"""Independent, fail-closed Phase 2D historical evidence verification."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ENTRY = re.compile(
    r"^([0-9a-fA-F]{64})  (results/phase2d/.+)$"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as stream:
        for block in iter(
            lambda: stream.read(1024 * 1024),
            b"",
        ):
            digest.update(block)

    return digest.hexdigest()


def audit(repo: Path, baseline: Path) -> dict:

    repo = repo.resolve(strict=True)
    root = repo / "results" / "phase2d"
    baseline = baseline.resolve(strict=True)

    if not root.is_dir() or not baseline.is_relative_to(root):
        raise ValueError("Invalid evidence root or baseline")

    if (
        baseline.name != "historical-before.sha256"
        or not baseline.parent.name.startswith(
            "step38-independent-verification-"
        )
    ):
        raise ValueError("Invalid frozen STEP 38 baseline")

    inventory = {}

    for number, line in enumerate(
        baseline.read_text(
            encoding="utf-8-sig"
        ).splitlines(),
        1,
    ):
        match = ENTRY.fullmatch(line)

        if not match:
            raise ValueError(
                f"Malformed baseline record: {number}"
            )

        expected, relative = match.groups()

        path = (repo / Path(relative)).resolve(
            strict=False
        )

        if (
            not path.is_relative_to(root)
            or baseline.parent in path.parents
            or relative in inventory
        ):
            raise ValueError(
                f"Unsafe or duplicate baseline record: {number}"
            )

        inventory[relative] = expected.lower()

    if not inventory:
        raise ValueError("Historical baseline is empty")

    changed = []
    missing = []

    for relative, expected in sorted(
        inventory.items()
    ):
        path = repo / relative

        if not path.is_file() or path.is_symlink():
            missing.append(relative)
            continue

        actual = sha256(path)

        if actual != expected:
            changed.append(relative)

    new_diagnostics = []
    unexpected_additions = []

    for path in root.rglob("*"):

        # The current verification output is excluded.
        # Its files were created after the baseline.
        if baseline.parent in path.parents:
            continue

        if not path.is_file() and not path.is_symlink():
            continue

        relative = path.relative_to(repo).as_posix()

        if relative in inventory:
            continue

        if path.is_symlink():
            unexpected_additions.append(relative)
            continue

        first_component = path.relative_to(
            root
        ).parts[0]

        if first_component.startswith("step38-"):
            new_diagnostics.append(relative)
        else:
            unexpected_additions.append(relative)

    original_integrity = (
        "PASS"
        if not changed and not missing
        else "FAIL"
    )

    inventory_integrity = (
        "PASS"
        if not unexpected_additions
        else "FAIL"
    )

    result = {
        "schema": "phase2d-evidence-baseline-v1",
        "baseline": baseline.relative_to(
            repo
        ).as_posix(),
        "baseline_sha256": sha256(baseline),
        "original_file_count": len(inventory),
        "changed_originals": changed,
        "missing_originals": missing,
        "new_step38_diagnostics": sorted(
            new_diagnostics
        ),
        "unexpected_new_files": sorted(
            unexpected_additions
        ),
        "historical_originals_integrity": original_integrity,
        "inventory_policy": inventory_integrity,
        "hosted_artifact_authentication": "NOT_ASSESSED",
        "scientific_acceptance": "NOT_ESTABLISHED",
    }

    result["status"] = (
        "PASS"
        if original_integrity == "PASS"
        and inventory_integrity == "PASS"
        else "FAIL"
    )

    return result


def main() -> int:

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--repo",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--baseline",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--output",
        type=Path,
        required=True,
    )

    args = parser.parse_args()

    result = audit(
        args.repo,
        args.baseline,
    )

    output = args.output.resolve(
        strict=False
    )

    if output.parent != args.baseline.resolve().parent:
        raise ValueError(
            "Report must remain in the baseline output directory"
        )

    output.write_text(
        json.dumps(
            result,
            indent=2,
            sort_keys=True,
        ) + "\n",
        encoding="utf-8",
    )

    print(
        "ORIGINAL EVIDENCE:",
        result["historical_originals_integrity"],
    )

    print(
        "BASELINE RECORDS:",
        result["original_file_count"],
    )

    print(
        "CHANGED ORIGINALS:",
        len(result["changed_originals"]),
    )

    print(
        "MISSING ORIGINALS:",
        len(result["missing_originals"]),
    )

    print(
        "NEW STEP38 DIAGNOSTICS:",
        len(result["new_step38_diagnostics"]),
    )

    print(
        "UNEXPECTED ADDITIONS:",
        len(result["unexpected_new_files"]),
    )

    print(
        "EVIDENCE INTEGRITY:",
        result["status"],
    )

    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())