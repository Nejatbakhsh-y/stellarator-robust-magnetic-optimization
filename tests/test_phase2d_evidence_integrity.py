import hashlib
import importlib.util
from pathlib import Path

import pytest


MODULE = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "phase2d_evidence_integrity.py"
)

spec = importlib.util.spec_from_file_location(
    "phase2d_evidence_integrity",
    MODULE,
)

verifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verifier)


def make_fixture(tmp_path):

    root = tmp_path / "results" / "phase2d"
    root.mkdir(parents=True)

    original = root / "old.json"
    original.write_bytes(b"original")

    output = root / "step38-independent-verification-test"
    output.mkdir()

    baseline = output / "historical-before.sha256"

    digest = hashlib.sha256(b"original").hexdigest()

    baseline.write_text(
        f"{digest}  results/phase2d/old.json\n",
        encoding="utf-8",
    )

    return tmp_path, original, output, baseline


def test_unchanged_originals_pass(tmp_path):

    repo, _, _, baseline = make_fixture(tmp_path)

    result = verifier.audit(repo, baseline)

    assert result["status"] == "PASS"
    assert result["historical_originals_integrity"] == "PASS"


def test_new_step38_outputs_do_not_change_history(tmp_path):

    repo, _, output, baseline = make_fixture(tmp_path)

    (output / "new.json").write_bytes(b"manifest")

    diagnostic = (
        repo
        / "results"
        / "phase2d"
        / "step38-diagnostic-20261101"
    )

    diagnostic.mkdir()

    (diagnostic / "result.json").write_bytes(b"new")

    result = verifier.audit(repo, baseline)

    assert result["status"] == "PASS"
    assert len(result["new_step38_diagnostics"]) == 1


def test_modified_historical_file_rejected(tmp_path):

    repo, original, _, baseline = make_fixture(tmp_path)

    original.write_bytes(b"changed")

    result = verifier.audit(repo, baseline)

    assert result["status"] == "FAIL"
    assert result["changed_originals"]


def test_missing_historical_file_rejected(tmp_path):

    repo, original, _, baseline = make_fixture(tmp_path)

    original.unlink()

    result = verifier.audit(repo, baseline)

    assert result["status"] == "FAIL"
    assert result["missing_originals"]


def test_unexpected_new_file_rejected(tmp_path):

    repo, _, _, baseline = make_fixture(tmp_path)

    new_file = (
        repo
        / "results"
        / "phase2d"
        / "unexpected.json"
    )

    new_file.write_bytes(b"unexpected")

    result = verifier.audit(repo, baseline)

    assert result["status"] == "FAIL"
    assert result["unexpected_new_files"]


def test_duplicate_baseline_rejected(tmp_path):

    repo, _, _, baseline = make_fixture(tmp_path)

    content = baseline.read_text()

    baseline.write_text(content + content)

    with pytest.raises(ValueError, match="duplicate"):
        verifier.audit(repo, baseline)