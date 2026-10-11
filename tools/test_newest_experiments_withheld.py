"""Pins T-2 (DEC-20261005-98a823, TASK-20261005-27ff15).

newest_runnable() drops ids named in committed `withheld_contracts.ids` blocks
from unqualified and --goal selection, guarded by non-empty rule_9_fields,
reversible by a later `released_contracts.ids`, overridden by an explicit
--experiment, and always reported on stderr. --json stdout keeps its row shape.
"""
from __future__ import annotations

import inspect
import json
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import ecc_priority as EP  # noqa: E402
import newest_experiments as NE  # noqa: E402

RULE_9 = {f: f"{f} text" for f in EP.RULE_9_FIELDS}
HELD = "EXP-ECDLP-aaaaaa"
FREE = "EXP-ECDLP-bbbbbb"
GOAL_HELD = "EXP-ECDLP-cccccc"


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", "-c", "user.name=fixture", "-c", "user.email=fixture@example.invalid",
                    "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null",
                    *args], cwd=root, check=True, capture_output=True)


def _commit(root: Path) -> None:
    if not (root / ".git").exists():
        _git(root, "init", "-q")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "--allow-empty", "-m", "fixture")


def _write(path: Path, doc: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(doc, sort_keys=False))


def _exp(root: Path, exp_id: str, designed_at: str, goal_id: str | None = None) -> None:
    _write(root / "experiments" / exp_id / "specification.yaml",
           {"experiment": {"id": exp_id, "status": "approved", "approved_by": "coordinator",
                           "frozen": True, "execution_authorized": True,
                           "designed_at": designed_at, "goal_id": goal_id}})


def _fixture(root: Path) -> None:
    _write(root / "orchestration/research-priority.yaml", {"ecc_areas": ["ECDLP"]})
    _exp(root, HELD, "2026-10-03")
    _exp(root, FREE, "2026-10-02")
    _exp(root, GOAL_HELD, "2026-10-01", goal_id="GOAL-ECDLP-aa1111")
    (root / "ledger/decisions").mkdir(parents=True, exist_ok=True)


def _hold(root: Path, did: str, ids: list[str], *, decided_at="2026-10-05", rule_9=None,
          released: list[str] | None = None) -> None:
    cd: dict = {"id": did, "decided_at": decided_at}
    if ids:
        block = {"ids": ids}
        if rule_9 is not False:
            block["rule_9_fields"] = RULE_9 if rule_9 is None else rule_9
        cd["withheld_contracts"] = block
    if released:
        cd["released_contracts"] = {"ids": released}
    _write(root / f"ledger/decisions/{did}.yaml", {"coordinator_decision": cd})


def _ids(root: Path, **kw) -> list[str]:
    return [r["id"] for r in NE.newest_runnable(root, **kw)]


_SELECT = NE.newest_runnable


def _cli(monkeypatch, capsys, root: Path, *args: str):
    monkeypatch.setattr(NE, "newest_runnable", lambda **kwargs: _SELECT(root, **kwargs))
    assert NE.main(list(args)) == 0
    return capsys.readouterr()


def test_hold_is_honoured_and_reported(tmp_path):
    _fixture(tmp_path)
    _commit(tmp_path)
    assert _ids(tmp_path) == [HELD, FREE, GOAL_HELD]
    _hold(tmp_path, "DEC-20261005-000001", [HELD, GOAL_HELD, "EXP-ECDLP-notexp"])
    _commit(tmp_path)
    report: dict = {}
    assert _ids(tmp_path, hold_report=report) == [FREE]
    assert report["decisions"] == [{"decision_id": "DEC-20261005-000001", "held": 3, "dropped": 2}]
    assert report["dropped"] == [{"id": HELD, "decision_id": "DEC-20261005-000001"},
                                 {"id": GOAL_HELD, "decision_id": "DEC-20261005-000001"}]
    assert _ids(tmp_path, honour_holds=False) == [HELD, FREE, GOAL_HELD]
    # --goal selection applies the hold.
    assert _ids(tmp_path, goal="GOAL-ECDLP-aa1111") == []


def test_guard_failure_keeps_rows_selectable_and_names_the_decision(tmp_path, capsys):
    _fixture(tmp_path)
    _hold(tmp_path, "DEC-20261005-000001", [HELD], rule_9={**RULE_9, "budget": ""})
    _hold(tmp_path, "DEC-20261005-000002", [FREE], rule_9=False)
    _commit(tmp_path)
    report: dict = {}
    assert _ids(tmp_path, hold_report=report) == [HELD, FREE, GOAL_HELD]
    assert report["decisions"] == []
    err = capsys.readouterr().err
    assert "DEC-20261005-000001: withheld_contracts not honoured" in err and "budget" in err
    assert "DEC-20261005-000002: withheld_contracts not honoured" in err


def test_later_release_restores_and_same_decision_release_wins(tmp_path):
    _fixture(tmp_path)
    _hold(tmp_path, "DEC-20261005-000005", [HELD, FREE])
    # Same decided_at, lower id: applied first, so its release is overridden.
    _hold(tmp_path, "DEC-20261005-000001", [], released=[FREE])
    _commit(tmp_path)
    assert _ids(tmp_path) == [GOAL_HELD]
    _hold(tmp_path, "DEC-20261006-000001", [], decided_at="2026-10-06", released=[HELD])
    _commit(tmp_path)
    assert _ids(tmp_path) == [HELD, GOAL_HELD]
    _hold(tmp_path, "DEC-20261007-000001", [GOAL_HELD], decided_at="2026-10-07",
          released=[GOAL_HELD])
    _commit(tmp_path)
    assert _ids(tmp_path) == [HELD, GOAL_HELD]


def test_explicit_experiment_returns_a_withheld_row_with_its_shape(tmp_path, monkeypatch, capsys):
    _fixture(tmp_path)
    _commit(tmp_path)
    baseline = json.loads(_cli(monkeypatch, capsys, tmp_path, "--limit", "0", "--json").out)
    _hold(tmp_path, "DEC-20261005-000001", [HELD])
    _commit(tmp_path)

    out = _cli(monkeypatch, capsys, tmp_path, "--experiment", HELD, "--json")
    rows = json.loads(out.out)
    assert [r["id"] for r in rows] == [HELD]
    assert rows[0] == next(r for r in baseline if r["id"] == HELD)
    assert f"{HELD} is withheld from dispatch by DEC-20261005-000001" in out.err
    assert "explicit --experiment overrides 1" in out.err


def test_json_row_keys_match_a_no_hold_baseline_and_count_line_is_present(
        tmp_path, monkeypatch, capsys):
    _fixture(tmp_path)
    _commit(tmp_path)
    out = _cli(monkeypatch, capsys, tmp_path, "--limit", "0", "--json")
    baseline = json.loads(out.out)
    assert "newest_experiments: holds: no honouring decision; 0 row(s) dropped" in out.err

    _hold(tmp_path, "DEC-20261005-000001", [HELD])
    _commit(tmp_path)
    out = _cli(monkeypatch, capsys, tmp_path, "--limit", "0", "--json")
    held = json.loads(out.out)
    assert isinstance(held, list) and [r["id"] for r in held] == [FREE, GOAL_HELD]
    base_rows = {r["id"]: r for r in baseline}
    for row in held:
        assert list(row) == list(base_rows[row["id"]])
        assert row == base_rows[row["id"]]
    assert ("newest_experiments: holds: DEC-20261005-000001 dropped 1 row(s) of 1 held id(s); "
            "explicit --experiment overrides 0") in out.err
    assert "# withheld by decision" not in out.out + out.err

    out = _cli(monkeypatch, capsys, tmp_path, "--limit", "0", "--json", "--show-withheld")
    assert json.loads(out.out) == held
    assert f"# withheld by decision: 1\n{HELD}\tDEC-20261005-000001" in out.err

    out = _cli(monkeypatch, capsys, tmp_path, "--limit", "0", "--show-withheld")
    assert out.out.index(FREE) < out.out.index("# withheld by decision: 1")
    assert f"{HELD}\tDEC-20261005-000001" in out.out
    assert "DEC-20261005-000001 dropped 1 row(s)" in out.err

    out = _cli(monkeypatch, capsys, tmp_path, "--goal", "GOAL-ECDLP-aa1111", "--limit", "0", "--json")
    assert [r["id"] for r in json.loads(out.out)] == [GOAL_HELD]
    assert "DEC-20261005-000001 dropped 0 row(s) of 1 held id(s)" in out.err


def test_unparseable_decision_is_skipped_with_a_warning(tmp_path, capsys):
    _fixture(tmp_path)
    (tmp_path / "ledger/decisions/DEC-20261005-00000b.yaml").write_text(
        "coordinator_decision:\n  withheld_contracts: {ids: [EXP-ECDLP-aaaaaa\n")
    _commit(tmp_path)
    assert _ids(tmp_path) == [HELD, FREE, GOAL_HELD]
    assert "DEC-20261005-00000b.yaml does not parse" in capsys.readouterr().err


def test_signature_stays_call_compatible_for_autopilot():
    params = inspect.signature(NE.newest_runnable).parameters
    assert list(params)[:4] == ["repo", "include_blocked", "goal", "experiment_ids"]
    assert params["repo"].kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
    for name in ("honour_holds", "hold_report"):
        assert params[name].kind is inspect.Parameter.KEYWORD_ONLY
    assert params["honour_holds"].default is True
    assert params["hold_report"].default is None


def _decision(name: str) -> dict:
    return yaml.safe_load((ROOT / "ledger/decisions" / f"{name}.yaml").read_text())["coordinator_decision"]


def test_real_corpus_withholds_at_least_the_151_ids_and_none_excluded_by_98a823():
    first = _decision("DEC-20261005-138b51")["withheld_contracts"]["ids"]
    second = _decision("DEC-20261005-98a823")
    named = set(first) | set(second["withheld_contracts"]["ids"])
    assert len(named) == 151
    state = NE.withheld_state(ROOT)
    assert len(state) >= 151
    assert named <= set(state)
    excluded = {row["id"] for row in second["excluded_from_hold"]["rows"]}
    assert len(excluded) == 22
    assert not any(state.get(eid) == "DEC-20261005-98a823" for eid in excluded)


def test_ready_rows_sort_before_unimplemented_within_a_priority_group(tmp_path, monkeypatch):
    """P0.3: an older contract with a trial plan outranks a newer one without."""
    root = tmp_path
    _write(root / "orchestration/research-priority.yaml", {"ecc_areas": ["ECDLP"]})
    _exp(root, "EXP-ECDLP-aaaaaa", "2026-10-01")
    _exp(root, "EXP-ECDLP-bbbbbb", "2026-10-05")
    (root / "ledger/decisions").mkdir(parents=True)
    _commit(root)
    monkeypatch.setattr(NE, "execution_progress",
                        lambda exp_dir, repo: {"execution_state": "ready"}
                        if exp_dir.name == "EXP-ECDLP-aaaaaa"
                        else {"execution_state": "needs_implementation_or_plan"})
    assert _ids(root, off_main={}) == ["EXP-ECDLP-aaaaaa", "EXP-ECDLP-bbbbbb"]


def test_off_main_runs_parses_refs_and_experiment_ids(monkeypatch):
    log = ("@@origin/cursor/run-a, origin/other\n"
           "experiments/EXP-ECDLP-aaaaaa/runs/RUN-1/manifest.yaml\n"
           "\n@@origin/cursor/run-b\n"
           "experiments/EXP-ECDLP-aaaaaa/runs/RUN-2/manifest.yaml\n"
           "experiments/EXP-SSI-bbbbbb/runs/RUN-9/stdout.txt\n"
           "experiments/EXP-SSI-bbbbbb/specification.yaml\n")

    class Done:
        stdout = log

    monkeypatch.setattr(NE.subprocess, "run", lambda *a, **k: Done())
    assert NE.off_main_runs(Path("/nowhere")) == {
        "EXP-ECDLP-aaaaaa": ["origin/cursor/run-a", "origin/cursor/run-b", "origin/other"],
        "EXP-SSI-bbbbbb": ["origin/cursor/run-b"],
    }


def test_off_main_runs_is_empty_without_git(monkeypatch):
    def boom(*a, **k):
        raise OSError("no git")
    monkeypatch.setattr(NE.subprocess, "run", boom)
    assert NE.off_main_runs(Path("/nowhere")) == {}
