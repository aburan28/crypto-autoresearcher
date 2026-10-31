"""The director calibration suites (evals/calibration) and their grader.

Every item carries a gold answer: the grader's positive control (it must pass) and, corrupted,
its negative control (it must fail). A grader that cannot tell them apart would make every
calibration in Delphi's registry meaningless, so these controls run on every change.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CAL = ROOT / "evals" / "calibration"
FAMILIES = ("card-compile", "assess")


def _suite(family: str) -> dict:
    return json.loads((CAL / f"{family}.json").read_text(encoding="utf-8"))


def _grade(family: str, item: dict, answer: str) -> dict:
    """Run the grader exactly as Delphi's command grader does: in the suite's directory,
    the item and answer as JSON on stdin."""
    proc = subprocess.run([sys.executable, "grade.py", family], cwd=CAL, capture_output=True, text=True,
                          input=json.dumps({"suite": family, "item": item["id"], "prompt": item["prompt"],
                                            "expect": item["expect"], "answer": answer}), timeout=120)
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout)


def _gold(family: str, item_id: str) -> str:
    return (CAL / "gold" / family / f"{item_id}.md").read_text(encoding="utf-8")


def _cases():
    for family in FAMILIES:
        for item in _suite(family)["items"]:
            yield pytest.param(family, item, id=f"{family}/{item['id']}")


@pytest.mark.parametrize("family", FAMILIES)
def test_suite_is_a_valid_delphi_suite(family):
    suite = _suite(family)
    assert suite["schema"] == "conductor.capability.suite.v1" and suite["family"] == family
    assert suite["grader"] == {"kind": "command", "argv": ["python3", "grade.py", family], "timeout_seconds": 120}
    ids = [item["id"] for item in suite["items"]]
    assert len(ids) == len(set(ids)) >= 10
    for item in suite["items"]:
        assert re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,63}", item["id"])
        assert item["prompt"].startswith("You are experiment-director")
        json.loads(item["expect"])
        assert (CAL / "gold" / family / f"{item['id']}.md").is_file()


def _corrupt(family: str, gold: str, expect: dict) -> str:
    if family == "assess":
        other = "stopped" if expect["outcome"] == "executed_as_specified" else "executed_as_specified"
        return gold.replace(f"outcome: {expect['outcome']}", f"outcome: {other}")
    if expect["kind"] == "error":
        return re.sub(r"specification_errors:\n- .*", "specification_errors: []", gold)
    return re.sub(r"timeout_seconds: (\d+)", lambda m: f"timeout_seconds: {int(m.group(1)) + 7}", gold, count=1)


@pytest.mark.parametrize("family,item", list(_cases()))
def test_gold_passes_and_corrupted_gold_fails(family, item):
    gold = _gold(family, item["id"])
    verdict = _grade(family, item, gold)
    assert verdict["passed"], verdict["reason"]
    corrupted = _grade(family, item, _corrupt(family, gold, json.loads(item["expect"])))
    assert not corrupted["passed"], "the grader passed a corrupted gold answer"


def _item(family: str, item_id: str) -> dict:
    return next(i for i in _suite(family)["items"] if i["id"] == item_id)


def test_inventing_a_missing_value_fails():
    # The design gives no timeout; a reply that picks one and claims no errors must fail.
    item = _item("card-compile", "no-timeout")
    invented = _gold("card-compile", "print").replace("CAL-print", "CAL-no-timeout").replace(
        "calibration-run/print", "calibration-run/no-timeout")
    verdict = _grade("card-compile", item, invented)
    assert not verdict["passed"]


def test_naming_the_wrong_missing_value_fails():
    item = _item("card-compile", "no-receipt")
    wrong = re.sub(r"specification_errors:\n- .*", "specification_errors:\n- the design gives no timeout",
                   _gold("card-compile", "no-receipt"))
    verdict = _grade("card-compile", item, wrong)
    assert not verdict["passed"] and "receipt" in verdict["reason"]


def test_a_recommendation_the_outcome_does_not_allow_fails():
    item = _item("assess", "changed-output")
    wrong = _gold("assess", "changed-output").replace("recommendation: escalate", "recommendation: proceed_to_analysis")
    verdict = _grade("assess", item, wrong)
    assert not verdict["passed"] and "recommendation" in verdict["reason"]
