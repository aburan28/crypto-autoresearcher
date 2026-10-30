"""Build the director calibration suites for Delphi's capability registry.

Two task families, both graded by this repository's own tools (`grade.py`, which calls
tools/task_card.py), so a pass means the answer would have been accepted in production:

  card-compile  the experiment-director compile step: a decided design in, a frozen-command
                card out. Positive items must lint and carry exactly the design's argv,
                timeouts, exit codes, receipt, scope and binds; negative items leave a value
                out of the design and pass only when the reply names it as a specification
                error instead of inventing a default.
  assess        the director assess step: a run's computed facts in, an execution_assessment
                out, checked by `task_card.py ingest` against the receipt on disk.

Every prompt is exactly what `task_card.py request` prints, so the suites measure the
production prompts. They depend on the checkout (HEAD, the director contract, the template),
so rebuilding changes their sha256, and Delphi then treats them as new measurements.

    python3 evals/calibration/build.py [--force]

writes card-compile.json, assess.json, fixtures/ (designs, executed cards and receipts)
and gold/ (one reference answer per item: the grader's positive control). It refuses to
overwrite an existing build without --force, because receipts are write-once.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "tools"))
import task_card as tc  # noqa: E402

REL = HERE.relative_to(REPO).as_posix()          # evals/calibration
EMIT = f"{REL}/fixtures/emit.py"
SUITE_SCHEMA = "conductor.capability.suite.v1"
GRADER = {"kind": "command", "timeout_seconds": 120}

# --------------------------------------------------------------------------- card-compile

# Shared design boilerplate: every value lint requires besides the commands themselves.
IDS = """- Experiment id: CAL-{id}. Card id: CARD-CAL-{id}-01. Bus address: executor-mechanical-cal.
- Not in the background.
- Stop condition: the run command exits with status 2."""

POSITIVE = [
    dict(id="print", commands=[dict(argv=["python3", EMIT, "print", "alpha"], timeout=60, codes=[0])],
         extra="Bind {emit}."),
    dict(id="pin", commands=[dict(argv=["python3", EMIT, "print", "pinned"], timeout=30, codes=[0])],
         extra="Pin the commit. Bind {emit}.", commit=True),
    dict(id="two", commands=[dict(argv=["python3", EMIT, "print", "one"], timeout=60, codes=[0]),
                             dict(argv=["python3", EMIT, "print", "two"], timeout=90, codes=[0],
                                  stdout="{out}/two.txt")],
         extra="Bind {emit}."),
    dict(id="codes", commands=[dict(argv=["python3", EMIT, "exit", "1"], timeout=45, codes=[0, 1])],
         extra="Bind {emit}."),
    dict(id="retry", commands=[dict(argv=["python3", EMIT, "exit", "0"], timeout=60, codes=[0],
                                    retry={"exit_codes": [75], "max_attempts": 2})],
         extra="Bind {emit}."),
    dict(id="env", commands=[dict(argv=["python3", EMIT, "print", "seeded"], timeout=60, codes=[0],
                                  env={"PYTHONHASHSEED": "0"})],
         extra="Bind {emit}."),
    dict(id="output", commands=[dict(argv=["python3", EMIT, "write", "{out}/result.txt", "done"], timeout=60,
                                     codes=[0], outputs=["{out}/result.txt"])],
         extra="Bind {emit}."),
    dict(id="fresh", commands=[dict(argv=["python3", EMIT, "write", "{out}/session/log.txt", "start"],
                                    timeout=120, codes=[0])],
         extra="Bind {emit}. The directory `{out}/session/` must not exist before the run.",
         must_not_exist=["{out}/session/"]),
]

# Each negative design leaves one value out; the reply must say so rather than choose a
# default. mentions: phrasings any of which its specification error must contain.
NEGATIVE = [
    dict(id="no-timeout", mentions=["timeout", "time limit"],
         text="- Command 1 (id run): `python3 {emit} print alpha`, success exit code 0.\n"
              "- Bind {emit}. Receipt at `{out}/receipt.json`. Write scope: `{out}/` only."),
    dict(id="no-receipt", mentions=["receipt"],
         text="- Command 1 (id run): `python3 {emit} print alpha`, timeout 60 seconds, success exit code 0.\n"
              "- Bind {emit}. Write scope: `{out}/` only."),
    dict(id="no-scope", mentions=["scope"],
         text="- Command 1 (id run): `python3 {emit} print alpha`, timeout 60 seconds, success exit code 0.\n"
              "- Bind {emit}. Receipt at `{out}/receipt.json`."),
    dict(id="no-codes", mentions=["exit code", "exit status", "success_exit_codes", "success code"],
         text="- Command 1 (id run): `python3 {emit} print alpha`, timeout 60 seconds.\n"
              "- Bind {emit}. Receipt at `{out}/receipt.json`. Write scope: `{out}/` only."),
]


def _out(item_id: str) -> str:
    return f".tmp/calibration-run/{item_id}"


def _fill(value, item_id: str):
    if isinstance(value, str):
        return value.format(emit=EMIT, out=_out(item_id))
    if isinstance(value, list):
        return [_fill(v, item_id) for v in value]
    if isinstance(value, dict):
        return {k: _fill(v, item_id) for k, v in value.items()}
    return value


def _design_text(item: dict) -> str:
    lines = [f"# Decided design: calibration item {item['id']}", "", IDS.format(id=item["id"])]
    for index, c in enumerate(item.get("commands", []), 1):
        c = _fill(c, item["id"])
        words = [f"- Command {index} (id step-{index}): `{' '.join(c['argv'])}`",
                 f"timeout {c['timeout']} seconds",
                 "success exit codes " + " and ".join(map(str, c["codes"])) if len(c["codes"]) > 1
                 else f"success exit code {c['codes'][0]}"]
        if c.get("stdout"):
            words.append(f"stdout to `{c['stdout']}`")
        if c.get("env"):
            words.append("environment " + ", ".join(f"{k}={v}" for k, v in c["env"].items()))
        if c.get("retry"):
            words.append(f"retry only on exit code {c['retry']['exit_codes'][0]}, at most "
                         f"{c['retry']['max_attempts']} attempts")
        if c.get("outputs"):
            words.append("declared output " + ", ".join(f"`{o}`" for o in c["outputs"]))
        lines.append(", ".join(words) + ".")
    if "text" in item:
        lines.append(_fill(item["text"], item["id"]))
    else:
        lines.append(f"- Receipt at `{_out(item['id'])}/receipt.json`. Write scope: `{_out(item['id'])}/` only.")
        lines.append("- " + _fill(item["extra"], item["id"]))
    return "\n".join(lines) + "\n"


def _expected_card(item: dict, head: str) -> dict:
    out = _out(item["id"])
    expect = {"kind": "card", "receipt": f"{out}/receipt.json", "write_scope": [f"{out}/"],
              "binds": [EMIT], "commit": head if item.get("commit") else None,
              "must_not_exist": _fill(item.get("must_not_exist", []), item["id"]), "commands": []}
    for c in _fill(item["commands"], item["id"]):
        expect["commands"].append({k: v for k, v in {
            "argv": c["argv"], "timeout_seconds": c["timeout"], "success_exit_codes": c["codes"],
            "stdout": c.get("stdout"), "env": c.get("env"), "retry": c.get("retry"),
            "outputs": c.get("outputs")}.items() if v is not None})
    return expect


def _gold_card(item: dict, expect: dict) -> dict:
    card = {"schema": tc.SCHEMA, "card_id": f"CARD-CAL-{item['id']}-01", "experiment_id": f"CAL-{item['id']}",
            "author_role": "experiment-director", "executor_role": "executor-mechanical",
            "kind": "frozen_command", "receipt": expect["receipt"],
            "binds": [{"path": EMIT, "sha256": tc.sha256_file(REPO / EMIT)}],
            "commands": [dict(id=f"step-{i}", **c) for i, c in enumerate(expect["commands"], 1)],
            "bus_address": "executor-mechanical-cal", "background": False,
            "write_scope": expect["write_scope"], "stop_when": ["The run command exits with status 2."]}
    if expect["commit"]:
        card["commit"] = expect["commit"]
    if expect["must_not_exist"]:
        card["must_not_exist"] = expect["must_not_exist"]
    return card


def _fence(doc: dict) -> str:
    return "```yaml\n" + yaml.safe_dump(doc, sort_keys=False) + "```\n"


def build_compile(head: str) -> list[dict]:
    items = []
    for item in POSITIVE + NEGATIVE:
        design = HERE / "fixtures" / "compile" / f"{item['id']}.md"
        design.parent.mkdir(parents=True, exist_ok=True)
        design.write_text(_design_text(item), encoding="utf-8")
        prompt = tc.compile_request([design.relative_to(REPO).as_posix()], [EMIT], f"{_out(item['id'])}/card.yaml")
        if "mentions" in item:
            expect = {"kind": "error", "mentions": item["mentions"]}
            # The gold reply still holds a card (ingest wants one) but lists the gap.
            gold_card = _gold_card({"id": item["id"]}, {"receipt": f"{_out(item['id'])}/receipt.json",
                                                        "write_scope": [f"{_out(item['id'])}/"], "commit": None,
                                                        "must_not_exist": [], "commands": []})
            gold = _fence(gold_card) + "\n" + _fence({"specification_errors": [
                f"the design gives no {item['mentions'][0]} value; it is not defaulted"]})
        else:
            expect = _expected_card(item, head)
            gold = _fence(_gold_card(item, expect)) + "\n" + _fence({"specification_errors": []})
        items.append({"id": item["id"], "prompt": prompt, "expect": json.dumps(expect, sort_keys=True)})
        (HERE / "gold" / "card-compile").mkdir(parents=True, exist_ok=True)
        (HERE / "gold" / "card-compile" / f"{item['id']}.md").write_text(gold, encoding="utf-8")
    return items

# --------------------------------------------------------------------------- assess

# Each case is a real card, really run (or deliberately not run), so the facts the prompt
# carries are the facts `ingest` recomputes from the receipt on disk.
ASSESS = [
    dict(id="ok-print", commands=[["print", "hello"]], outcome="executed_as_specified"),
    dict(id="ok-output", commands=[["write", "{dir}/out/result.txt", "done"]], outputs=True,
         outcome="executed_as_specified"),
    dict(id="ok-two", commands=[["print", "one"], ["print", "two"]], outcome="executed_as_specified"),
    dict(id="stop-exit", commands=[["exit", "3"]], outcome="stopped"),
    dict(id="stop-second", commands=[["print", "one"], ["exit", "4"]], outcome="stopped"),
    dict(id="stop-timeout", commands=[["sleep", "5"]], timeout=1, outcome="stopped"),
    dict(id="changed-output", commands=[["write", "{dir}/out/result.txt", "done"]], outputs=True,
         tamper=True, outcome="executor_deviated"),
    dict(id="outside-scope", commands=[["write", "{dir}/stray.txt", "x"]], outcome="executor_deviated"),
    dict(id="never-ran", commands=[["print", "hello"]], run=False, outcome="impeded"),
    dict(id="never-ran-two", commands=[["print", "one"], ["print", "two"]], run=False, outcome="impeded"),
]


def build_assess() -> list[dict]:
    items = []
    for case in ASSESS:
        d = f"{REL}/fixtures/assess/{case['id']}"
        commands = []
        for i, words in enumerate(case["commands"], 1):
            argv = ["python3", EMIT] + [w.format(dir=d) for w in words]
            c = {"id": f"step-{i}", "argv": argv, "timeout_seconds": case.get("timeout", 60), "success_exit_codes": [0]}
            if case.get("outputs"):
                c["outputs"] = [f"{d}/out/result.txt"]
            commands.append(c)
        card = {"schema": tc.SCHEMA, "card_id": f"CARD-CAL-{case['id']}-01", "experiment_id": f"CAL-{case['id']}",
                "author_role": "experiment-director", "executor_role": "executor-mechanical",
                "kind": "frozen_command", "receipt": f"{d}/out/receipt.json",
                "binds": [{"path": EMIT, "sha256": tc.sha256_file(REPO / EMIT)}], "commands": commands,
                "bus_address": "executor-mechanical-cal", "background": False,
                "write_scope": [f"{d}/out/"], "stop_when": ["The run command exits with status 2."]}
        card_path = REPO / d / "card.yaml"
        card_path.parent.mkdir(parents=True, exist_ok=True)
        card_path.write_text(yaml.safe_dump(card, sort_keys=False), encoding="utf-8")
        rel, sha, loaded = tc.load_card(card_path.relative_to(REPO).as_posix())
        if case.get("run", True):
            tc.run_card(rel, sha, loaded)
        if case.get("tamper"):
            (REPO / d / "out" / "result.txt").write_text("changed after the run\n", encoding="utf-8")
        facts = tc.assessment_facts(loaded)
        if facts["outcome"] != case["outcome"]:
            raise SystemExit(f"{case['id']}: facts give {facts['outcome']}, the case expects {case['outcome']}")
        prompt = tc.assess_request(rel, sha, loaded)
        gold = _fence({"execution_assessment": {
            "card_id": loaded["card_id"], "card_sha256": sha, "outcome": case["outcome"],
            "recommendation": tc.ALLOWED[case["outcome"]][0],
            "reasons": [f"Computed facts: outcome {case['outcome']}."], "interpretation": "not_assessed"}})
        items.append({"id": case["id"], "prompt": prompt,
                      "expect": json.dumps({"card": rel, "outcome": case["outcome"]}, sort_keys=True)})
        (HERE / "gold" / "assess").mkdir(parents=True, exist_ok=True)
        (HERE / "gold" / "assess" / f"{case['id']}.md").write_text(gold, encoding="utf-8")
    return items

# --------------------------------------------------------------------------- main


def suite(family: str, items: list[dict], max_tokens: int) -> dict:
    return {"schema": SUITE_SCHEMA, "id": f"{family}-v1", "family": family, "max_tokens": max_tokens,
            "grader": dict(GRADER, argv=["python3", "grade.py", family]), "items": items}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--force", action="store_true", help="delete the previous build first")
    args = parser.parse_args(argv)
    built = [HERE / "fixtures" / "compile", HERE / "fixtures" / "assess", HERE / "gold",
             HERE / "card-compile.json", HERE / "assess.json"]
    if any(p.exists() for p in built):
        if not args.force:
            print("a build exists; --force deletes it (its receipts are write-once) and rebuilds", file=sys.stderr)
            return 2
        for p in built:
            shutil.rmtree(p) if p.is_dir() else p.unlink(missing_ok=True)
    head = tc.git(REPO, "rev-parse", "HEAD")[1]
    for family, items, tokens in (("card-compile", build_compile(head), 8000), ("assess", build_assess(), 2000)):
        path = HERE / f"{family}.json"
        path.write_text(json.dumps(suite(family, items, tokens), indent=2) + "\n", encoding="utf-8")
        print(f"{path.relative_to(REPO)}: {len(items)} items")
    return 0


if __name__ == "__main__":
    sys.exit(main())
