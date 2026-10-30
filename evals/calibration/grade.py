"""Grader for the director calibration suites (the `command` grader of Delphi's registry).

Reads {suite, item, prompt, expect, answer} as JSON on stdin and prints {"passed", "reason"}.
It exits non-zero, printing no verdict, only when the suite itself is broken (a fixture that
no longer gives the facts it was built with), so Delphi stops instead of scoring a model on
a broken item.

    python3 grade.py card-compile | assess
"""
from __future__ import annotations

import json
import sys
import uuid
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "tools"))
import task_card as tc  # noqa: E402


def _scope(paths) -> set[str]:
    return {str(p).rstrip("/") for p in paths or []}


def compile_grade(answer: str, expect: dict) -> tuple[bool, str]:
    out = f".tmp/calibration-grade/{uuid.uuid4().hex}.yaml"
    try:
        findings = tc.ingest(answer, out, "card", None, REPO)
        if expect["kind"] == "error":
            if not findings:
                return False, "the reply wrote a card although the design leaves a value out"
            errors = [f for f in findings if f.startswith("specification_error:")]
            if not errors:
                return False, "refused, but not as a specification error: " + "; ".join(findings)
            if not any(m in f.lower() for m in expect["mentions"] for f in errors):
                return False, f"the specification errors do not name the missing {expect['mentions'][0]}: " + "; ".join(errors)
            return True, "named the missing value as a specification error"
        if findings:
            return False, "; ".join(findings)
        card = yaml.safe_load((REPO / out).read_text(encoding="utf-8"))
    finally:
        (REPO / out).unlink(missing_ok=True)
    problems = []
    if card.get("receipt") != expect["receipt"]:
        problems.append(f"receipt {card.get('receipt')} is not {expect['receipt']}")
    if _scope(card.get("write_scope")) != _scope(expect["write_scope"]):
        problems.append(f"write_scope {card.get('write_scope')} is not {expect['write_scope']}")
    if sorted(b.get("path") for b in card.get("binds") or []) != sorted(expect["binds"]):
        problems.append(f"binds {[b.get('path') for b in card.get('binds') or []]} are not {expect['binds']}")
    if card.get("commit") != expect["commit"]:
        problems.append(f"commit {card.get('commit')} is not {expect['commit']}")
    if _scope(card.get("must_not_exist")) != _scope(expect["must_not_exist"]):
        problems.append(f"must_not_exist {card.get('must_not_exist')} is not {expect['must_not_exist']}")
    got = card.get("commands") or []
    if len(got) != len(expect["commands"]):
        problems.append(f"{len(got)} commands, the design has {len(expect['commands'])}")
    for index, (g, e) in enumerate(zip(got, expect["commands"]), 1):
        for key, want in e.items():
            have = g.get(key)
            if key == "success_exit_codes":
                have, want = sorted(have or []), sorted(want)
            if key == "retry" and isinstance(have, dict):
                have = {"exit_codes": sorted(have.get("exit_codes") or []), "max_attempts": have.get("max_attempts")}
                want = {"exit_codes": sorted(want["exit_codes"]), "max_attempts": want["max_attempts"]}
            if have != want:
                problems.append(f"command {index} {key}: {have!r} is not {want!r}")
        for key in ("stdout", "env", "retry", "outputs"):
            if key not in e and g.get(key):
                problems.append(f"command {index} adds {key}, which the design does not give")
    if problems:
        return False, "; ".join(problems)
    return True, "lints clean and matches the design"


def assess_grade(answer: str, expect: dict) -> tuple[bool, str]:
    _, _, card = tc.load_card(expect["card"], REPO)
    facts = tc.assessment_facts(card, None, REPO)
    if facts["outcome"] != expect["outcome"]:
        raise SystemExit(f"fixture drift: {expect['card']} now gives {facts['outcome']}, built as {expect['outcome']}")
    out = f".tmp/calibration-grade/{uuid.uuid4().hex}.yaml"
    try:
        findings = tc.ingest(answer, out, "assessment", card, REPO)
    finally:
        (REPO / out).unlink(missing_ok=True)
    if findings:
        return False, "; ".join(findings)
    return True, "ingest accepted the assessment"


def main(argv: list[str]) -> int:
    family = argv[0] if argv else ""
    if family not in ("card-compile", "assess"):
        print("usage: grade.py card-compile | assess", file=sys.stderr)
        return 2
    item = json.load(sys.stdin)
    expect = json.loads(item["expect"])
    grade = compile_grade if family == "card-compile" else assess_grade
    try:
        passed, reason = grade(item["answer"], expect)
    except tc.CardError as exc:
        passed, reason = False, f"CARD ERROR {exc}"
    print(json.dumps({"passed": passed, "reason": reason[:2000]}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
