"""The explicit frozen-test successor runs; hash errors never omit a test."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from tools.ci_test_supersession import verified_bytes

pytest_plugins = ["pytester"]


def prepare(pytester, *, corrupt="", successor_fails=False):
    frozen = pytester.path / "test_frozen.py"
    frozen.write_text("def test_gate():\n    raise AssertionError('historical path fixture')\n\ndef test_unchanged():\n    assert True\n")
    successor = pytester.path / "successor.py"
    successor.write_text("def replacement(tmp_path):\n    assert tmp_path.is_dir()\n    assert " + ("False" if successor_fails else "True") + "\n")
    helper = pytester.path / "helper.py"
    helper.write_text("VALUE = 1\n")
    def bind(path):
        return {"path": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    record = {"schema": "ci-test-supersession-v1", "original_nodeid": "test_frozen.py::test_gate", "original_sha256": bind(frozen)["sha256"], "replacement": dict(bind(successor), callable="replacement"), "helpers": [bind(helper)]}
    (pytester.path / "supersession.json").write_text(json.dumps(record))
    if corrupt:
        target = {"original": frozen, "replacement": successor, "helper": helper}[corrupt]
        target.write_text(target.read_text() + "# changed bytes\n")
    root = Path(__file__).resolve().parents[1]
    pytester.makeconftest(f"import sys\nfrom pathlib import Path\nsys.path.insert(0, {str(root)!r})\nfrom tools.ci_test_supersession import apply_supersession\ndef pytest_collection_modifyitems(items):\n    apply_supersession(items, Path(__file__).parent, 'supersession.json')\n")
    return record


def test_successor_executes_with_fixture_and_preserves_other_node(pytester):
    record = prepare(pytester)
    result = pytester.runpytest_subprocess("-q", "test_frozen.py", "--junitxml=result.xml")
    result.assert_outcomes(passed=2)
    import xml.etree.ElementTree as ET
    cases = ET.parse(pytester.path / "result.xml").findall(".//testcase")
    assert {case.attrib["name"] for case in cases} == {"test_gate", "test_unchanged"}
    gate = next(case for case in cases if case.attrib["name"] == "test_gate")
    properties = {p.attrib["name"]: p.attrib["value"] for p in gate.findall("properties/property")}
    assert properties["test_successor_path"] == "successor.py"
    assert properties["test_successor_sha256"] == record["replacement"]["sha256"]
    assert properties["superseded_test_sha256"] == record["original_sha256"]


def test_failing_successor_is_a_real_test_failure(pytester):
    prepare(pytester, successor_fails=True)
    result = pytester.runpytest_subprocess("-q", "test_frozen.py")
    result.assert_outcomes(failed=1, passed=1)


@pytest.mark.parametrize("corrupt", ["original", "replacement", "helper"])
def test_hash_mismatch_refuses_collection(pytester, corrupt):
    prepare(pytester, corrupt=corrupt)
    result = pytester.runpytest_subprocess("-q", "test_frozen.py")
    assert result.ret != 0
    assert "source hash mismatch" in result.stdout.str() + result.stderr.str()
    assert "2 passed" not in result.stdout.str()


def test_other_explicit_selection_remains_unchanged(pytester):
    prepare(pytester, corrupt="replacement")
    result = pytester.runpytest_subprocess("-q", "test_frozen.py::test_unchanged")
    result.assert_outcomes(passed=1)


@pytest.mark.parametrize("relative", ["../outside.py", "/tmp/outside.py"])
def test_source_binding_refuses_escape(tmp_path, relative):
    with pytest.raises(ValueError, match="path/hash binding"):
        verified_bytes(tmp_path, {"path": relative, "sha256": "0" * 64})


def test_source_binding_refuses_symlink(tmp_path):
    actual = tmp_path / "actual.py"
    actual.write_text("pass\n")
    linked = tmp_path / "linked.py"
    linked.symlink_to(actual)
    with pytest.raises(ValueError, match="symlink"):
        verified_bytes(tmp_path, {"path": "linked.py", "sha256": hashlib.sha256(actual.read_bytes()).hexdigest()})
