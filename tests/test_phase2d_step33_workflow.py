"""Workflow contract and real argv/process regressions; no shell source transfer."""
import ast
import copy
import importlib.util
from pathlib import Path
import subprocess
import sys
import tomllib

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/verify_phase2d_step33_workflow.py"
WORKFLOW = ROOT / ".github/workflows/phase2d-step33-causal.yml"
SPEC = importlib.util.spec_from_file_location("workflow_validator", SCRIPT)
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


def test_workflow_parser_declared_in_ci_dev_dependencies():
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8-sig"))
    assert "PyYAML>=6,<7" in project["project"]["optional-dependencies"]["dev"]
    ci = yaml.load((ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8"),
                   Loader=yaml.BaseLoader)
    assert ci["on"] == ["push", "pull_request"]
    commands = [step["run"] for step in ci["jobs"]["validate"]["steps"] if "run" in step]
    assert commands.index("python -m pip install -e '.[dev]'") < commands.index("python -m pytest -q")


def baseline():
    data = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8-sig"))
    if True in data:
        data["on"] = data.pop(True)
    return data


def write(tmp_path, data):
    path = tmp_path / "workflow.yml"
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    return path


def invoke(path):
    return subprocess.run([sys.executable, str(SCRIPT), str(path)],
                          capture_output=True, text=True, shell=False)


@pytest.mark.parametrize("location,value,message", [
    (("name",), "wrong", "name:"),
    (("on", "push"), None, "on.push:"),
    (("on", "push", "branches"), ["main"], "on.push.branches"),
    (("on", "pull_request"), None, "on.pull_request:"),
    (("on", "pull_request", "branches"), ["main"], "on.pull_request.branches"),
    (("on", "pull_request", "types"), ["opened"], "synchronize"),
    (("on", "pull_request", "types"), "synchronize", "synchronize"),
    (("on", "pull_request_target"), None, "forbidden"),
    (("on", "workflow_dispatch"), False, "workflow_dispatch"),
    (("jobs", "compare", "needs"), ["capture"], "jobs.compare.needs"),
    (("jobs", "compare", "needs"), "capture replay", "jobs.compare.needs"),
    (("jobs", "compare", "needs"), [{}, "replay"], "jobs.compare.needs"),
    (("permissions",), "write-all", "permissions:"),
    (("permissions",), {"contents": "write"}, "permissions:"),
    (("permissions",), {"contents": "read", "actions": "write"}, "permissions:"),
    (("jobs", "capture", "permissions"), {"contents": "write"}, "permissions:"),
    (("jobs", "compare", "steps"), [None], "steps:"),
    (("jobs", "compare", "runs-on"), None, "runs-on:"),
    (("jobs", "replay", "strategy"), [], "numerical cohorts"),
    (("jobs",), [], "jobs:"),
    (("on",), [], "on:"),
])
def test_invalid_fields(tmp_path, location, value, message):
    data = baseline()
    target = data
    for key in location[:-1]:
        target = target[key]
    target[location[-1]] = copy.deepcopy(value)
    result = invoke(write(tmp_path, data))
    assert result.returncode != 0
    assert message in result.stderr
    assert "Traceback" not in result.stderr


@pytest.mark.parametrize("location", [
    ("name",), ("on",), ("permissions",), ("jobs",),
    ("on", "push"), ("on", "pull_request"), ("on", "workflow_dispatch"),
    ("on", "pull_request", "types"),
    ("jobs", "capture"), ("jobs", "replay"), ("jobs", "compare"),
    ("jobs", "compare", "needs"),
])
def test_missing_fields(tmp_path, location):
    data = baseline()
    target = data
    for key in location[:-1]:
        target = target[key]
    del target[location[-1]]
    result = invoke(write(tmp_path, data))
    assert result.returncode != 0
    assert "ERROR:" in result.stderr


@pytest.mark.parametrize("job", ["capture", "replay"])
@pytest.mark.parametrize("index", range(4))
def test_missing_numerical_cohort(tmp_path, job, index):
    data = baseline()
    del data["jobs"][job]["strategy"]["matrix"]["include"][index]
    result = invoke(write(tmp_path, data))
    assert result.returncode != 0
    assert f"jobs.{job}.strategy.matrix.include" in result.stderr


@pytest.mark.parametrize("source", ["name: [", "", "[]", "null", "name: a\nname: b\n"])
def test_invalid_yaml_or_document(tmp_path, source):
    path = tmp_path / "bad.yml"
    path.write_text(source, encoding="utf-8")
    result = invoke(path)
    assert result.returncode != 0
    assert "ERROR:" in result.stderr


def test_missing_workflow(tmp_path):
    result = invoke(tmp_path / "missing.yml")
    assert result.returncode != 0
    assert "cannot read valid workflow YAML" in result.stderr


def test_existing_workflow():
    assert VALIDATOR.validate_workflow(WORKFLOW) == []
    result = invoke(WORKFLOW)
    assert result.returncode == 0, result.stderr
    assert "PASS:" in result.stdout


@pytest.mark.parametrize("bom", [False, True])
def test_normal_argv_with_spaces_and_bom(tmp_path, bom):
    directory = tmp_path / "workflow directory with spaces"
    directory.mkdir()
    path = directory / "STEP 33 workflow.yml"
    path.write_text(WORKFLOW.read_text(encoding="utf-8-sig"),
                    encoding="utf-8-sig" if bom else "utf-8")
    result = invoke(path)
    assert result.returncode == 0, result.stderr


def test_quoted_on_key(tmp_path):
    assert VALIDATOR.validate_workflow(write(tmp_path, baseline())) == []


def test_python311_syntax():
    ast.parse(SCRIPT.read_text(encoding="utf-8"), feature_version=(3, 11))


def test_missing_argument():
    result = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True)
    assert result.returncode != 0
    assert "workflow" in result.stderr


def test_launcher_uses_file_arguments():
    source = (ROOT / "scripts/phase2d_step33_host.ps1").read_text(encoding="utf-8-sig")
    assert "Run-Python 'workflow-validation' @('scripts/verify_phase2d_step33_workflow.py','.github/workflows/phase2d-step33-causal.yml','--host-preflight')" in source
    assert "@('-c'" not in source
    assert source.index("Run-Python 'workflow-validation'") < source.index("Run-Python 'tests'")
