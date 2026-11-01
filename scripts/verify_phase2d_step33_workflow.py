#!/usr/bin/env python3
"""Validate the STEP 33 workflow without transferring source through a shell.

Usage: python scripts/verify_phase2d_step33_workflow.py WORKFLOW.yml
This checks the project's workflow contract, not the full GitHub Actions schema.
"""
from __future__ import annotations

import argparse
import importlib
from pathlib import Path
import sys

import yaml


NAME = "Phase 2D STEP 33 controlled causal attribution"
COHORTS = {
    "windows-reference", "linux-reference",
    "linux-numpy-sensitivity", "linux-scipy-sensitivity",
}


def validate_workflow(path: Path) -> list[str]:
    """Return actionable errors; an empty list means the contract passed."""
    try:
        source = path.read_text(encoding="utf-8-sig")
        # Reject duplicate keys rather than accepting safe_load's last value.
        node = yaml.compose(source, Loader=yaml.SafeLoader)
        def check_keys(node, ancestors=()):
            if node is None or id(node) in ancestors:
                return
            ancestors = (*ancestors, id(node))
            if isinstance(node, yaml.MappingNode):
                seen = set()
                for key, value in node.value:
                    if not isinstance(key, yaml.ScalarNode):
                        raise ValueError("mapping keys must be scalar")
                    identity = (key.tag, key.value)
                    if identity in seen:
                        raise ValueError(f"duplicate key {key.value!r} at line {key.start_mark.line + 1}")
                    seen.add(identity)
                    check_keys(value, ancestors)
            elif isinstance(node, yaml.SequenceNode):
                for value in node.value:
                    check_keys(value, ancestors)
        check_keys(node)
        data = yaml.safe_load(source)
    except (OSError, UnicodeError, yaml.YAMLError, ValueError, RecursionError) as exc:
        return [f"{path}: cannot read valid workflow YAML: {exc}"]
    errors = []
    def require(condition, message):
        if not condition:
            errors.append(message)
    if not isinstance(data, dict):
        return ["workflow: expected a YAML mapping"]
    require(data.get("name") == NAME, f"name: must be {NAME!r}")
    # PyYAML's YAML 1.1 SafeLoader resolves the unquoted key 'on' to True.
    require(not ("on" in data and True in data), "on: ambiguous quoted and YAML 1.1 trigger keys")
    events = data.get("on", data.get(True))
    if not isinstance(events, dict):
        errors.append("on: expected a trigger mapping")
        events = {}
    require("pull_request_target" not in events, "on.pull_request_target: forbidden")
    for event, branch in (
        ("push", "codex/phase2d-upstream-attribution"),
        ("pull_request", "codex/phase2d-cross-platform-reproducibility"),
    ):
        config = events.get(event)
        if not isinstance(config, dict):
            errors.append(f"on.{event}: required trigger mapping is missing or malformed")
            continue
        require(config.get("branches") == [branch], f"on.{event}.branches: must be [{branch!r}]")
        require("branches-ignore" not in config, f"on.{event}.branches-ignore: conflicts with required branches")
        if event == "pull_request":
            types = config.get("types")
            require(isinstance(types, list) and all(isinstance(t, str) for t in types)
                    and "synchronize" in types, "on.pull_request.types: must be a list including synchronize")
    require("workflow_dispatch" in events and (events["workflow_dispatch"] is None
            or isinstance(events["workflow_dispatch"], dict)), "on.workflow_dispatch: required; use null or a mapping")

    def permissions(value, location):
        require(isinstance(value, dict) and value.get("contents") == "read"
                and all(isinstance(k, str) and v in ("read", "none") for k, v in value.items()),
                f"{location}: require contents: read and only read/none grants")
    permissions(data.get("permissions"), "permissions")
    jobs = data.get("jobs")
    if not isinstance(jobs, dict):
        return errors + ["jobs: expected a mapping containing capture, replay, compare"]
    for job_name, job in jobs.items():
        if not isinstance(job, dict):
            errors.append(f"jobs.{job_name}: expected a mapping")
            continue
        if "permissions" in job:
            permissions(job["permissions"], f"jobs.{job_name}.permissions")
        require(isinstance(job.get("runs-on"), (str, list)) and bool(job["runs-on"]),
                f"jobs.{job_name}.runs-on: required nonempty runner")
        steps = job.get("steps")
        require(isinstance(steps, list) and bool(steps) and all(
            isinstance(step, dict) and ((isinstance(step.get("run"), str) and bool(step["run"]))
            or (isinstance(step.get("uses"), str) and bool(step["uses"]))) for step in steps),
            f"jobs.{job_name}.steps: required nonempty list of run/uses mappings")
    for name in ("capture", "replay", "compare"):
        require(isinstance(jobs.get(name), dict), f"jobs.{name}: required job mapping")
    for name in ("capture", "replay"):
        job = jobs.get(name)
        if not isinstance(job, dict):
            continue
        strategy = job.get("strategy")
        matrix = strategy.get("matrix") if isinstance(strategy, dict) else None
        rows = matrix.get("include") if isinstance(matrix, dict) else None
        valid_rows = isinstance(rows, list) and all(isinstance(row, dict) and
            all(isinstance(row.get(key), str) and bool(row[key]) for key in ("name", "os", "numpy", "scipy")) for row in rows)
        names = [row["name"] for row in rows] if valid_rows else []
        require(valid_rows and len(names) == 4 and set(names) == COHORTS,
                f"jobs.{name}.strategy.matrix.include: require exactly four numerical cohorts: {', '.join(sorted(COHORTS))}")
    compare = jobs.get("compare")
    if isinstance(compare, dict):
        needs = compare.get("needs")
        require(isinstance(needs, list) and len(needs) == 2 and all(isinstance(n, str) for n in needs)
                and set(needs) == {"capture", "replay"}, "jobs.compare.needs: must contain capture and replay exactly once")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workflow", type=Path)
    parser.add_argument("--host-preflight", action="store_true", help="also check Python 3.11 and host dependencies")
    args = parser.parse_args(argv)
    errors = validate_workflow(args.workflow)
    if args.host_preflight:
        if sys.version_info[:2] != (3, 11):
            errors.append("host: Python 3.11 is required")
        for name in ("numpy", "scipy", "matplotlib", "pytest", "threadpoolctl"):
            try:
                importlib.import_module(name)
            except ImportError as exc:
                errors.append(f"host: install required dependency {name}: {exc}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"PASS: STEP 33 workflow contract: {args.workflow}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
