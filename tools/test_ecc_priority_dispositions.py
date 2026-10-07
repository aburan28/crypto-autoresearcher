"""Pins T-1 (DEC-20261005-138b51 tooling_change_T1, TASK-20261005-27ff15).

open_ecc_ideas() honours committed `coordinator_decision.idea_dispositions`
blocks by explicit ID only, guarded by non-empty rule_9_fields, reversible by a
later `reopened` disposition, and always reports what it removed.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import ecc_priority as EP  # noqa: E402

RULE_9 = {f: f"{f} text" for f in EP.RULE_9_FIELDS}
SSI_IDEAS = ("IDEA-20261004-e4c461", "IDEA-20261004-edbd24", "IDEA-20261004-a09dd4")


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


def _fixture(root: Path, ideas: dict[str, str]) -> None:
    _write(root / "orchestration/research-priority.yaml", {"ecc_areas": ["ECDLP"]})
    _write(root / "ledger/questions/RQ-ECDLP-aaaaaa.yaml",
           {"research_question": {"id": "RQ-ECDLP-aaaaaa"}})
    for iid, title in ideas.items():
        _write(root / f"ledger/proposals/{iid}.yaml",
               {"idea": {"id": iid, "status": "proposed", "question_id": "RQ-ECDLP-aaaaaa",
                         "added": "2026-10-01", "title": title}})
    (root / "ledger/decisions").mkdir(parents=True, exist_ok=True)


def _decision(root: Path, did: str, ids: list[str], *, disposition="declined_out_of_question",
              decided_at="2026-10-05", rule_9=None) -> None:
    block = {"disposition": disposition,
             "applies_to_exactly": [{"id": i, "title": "t"} for i in ids]}
    if rule_9 is not False:
        block["rule_9_fields"] = RULE_9 if rule_9 is None else rule_9
    _write(root / f"ledger/decisions/{did}.yaml",
           {"coordinator_decision": {"id": did, "decided_at": decided_at,
                                     "idea_dispositions": block}})


def _open(root: Path, disposed: list | None = None) -> list[str]:
    return [r["id"] for r in EP.open_ecc_ideas(repo=root, disposed_out=disposed)]


IDEAS = {"IDEA-20261001-aaaaaa": "The integer 1023 has bit length 10",
         "IDEA-20261001-bbbbbb": "The integer 1023 has bit length 10",
         "IDEA-20261001-cccccc": "a real idea"}


def test_disposition_is_honoured_by_explicit_id_only(tmp_path, capsys):
    _fixture(tmp_path, IDEAS)
    _decision(tmp_path, "DEC-20261005-000001", ["IDEA-20261001-aaaaaa"])
    _commit(tmp_path)
    disposed: list = []
    # bbbbbb shares aaaaaa's title and stays open: membership is never by title.
    assert _open(tmp_path, disposed) == ["IDEA-20261001-bbbbbb", "IDEA-20261001-cccccc"]
    assert [(r["id"], r["decision_id"], r["disposition"]) for r in disposed] == [
        ("IDEA-20261001-aaaaaa", "DEC-20261005-000001", "declined_out_of_question")]
    assert capsys.readouterr().err == ""
    assert "IDEA-20261001-aaaaaa" in _open_without_holds(tmp_path)


def _open_without_holds(root: Path) -> list[str]:
    return [r["id"] for r in EP.open_ecc_ideas(repo=root, honour_dispositions=False)]


def test_guard_failure_keeps_the_ideas_open_and_warns(tmp_path, capsys):
    _fixture(tmp_path, IDEAS)
    _decision(tmp_path, "DEC-20261005-000001", ["IDEA-20261001-aaaaaa"],
              rule_9={**RULE_9, "test_boundary": "  "})
    _decision(tmp_path, "DEC-20261005-000002", ["IDEA-20261001-bbbbbb"], rule_9=False)
    _commit(tmp_path)
    disposed: list = []
    assert _open(tmp_path, disposed) == list(IDEAS)
    assert disposed == []
    err = capsys.readouterr().err
    assert "DEC-20261005-000001" in err and "test_boundary" in err
    assert "DEC-20261005-000002" in err and "successor_or_revisit" in err


def test_later_reopened_restores_and_ordering_breaks_ties_by_decision_id(tmp_path):
    _fixture(tmp_path, IDEAS)
    _decision(tmp_path, "DEC-20261005-000005", ["IDEA-20261001-aaaaaa", "IDEA-20261001-bbbbbb"])
    # Later decided_at: reopens aaaaaa.
    _decision(tmp_path, "DEC-20261004-ffffff", ["IDEA-20261001-aaaaaa"],
              disposition="reopened", decided_at="2026-10-06", rule_9=False)
    # Same decided_at, lower id: applied BEFORE the disposal, so it changes nothing.
    _decision(tmp_path, "DEC-20261005-000001", ["IDEA-20261001-bbbbbb"],
              disposition="reopened", decided_at="2026-10-05", rule_9=False)
    _commit(tmp_path)
    assert _open(tmp_path) == ["IDEA-20261001-aaaaaa", "IDEA-20261001-cccccc"]
    # Same decided_at, higher id: applied after the disposal, so it restores.
    _decision(tmp_path, "DEC-20261005-000009", ["IDEA-20261001-bbbbbb"],
              disposition="reopened", decided_at="2026-10-05", rule_9=False)
    _commit(tmp_path)
    assert _open(tmp_path) == list(IDEAS)


def test_unparseable_and_uncommitted_decisions_withhold_nothing(tmp_path, capsys):
    _fixture(tmp_path, IDEAS)
    (tmp_path / "ledger/decisions/DEC-20261005-00000b.yaml").write_text(
        "coordinator_decision:\n  idea_dispositions: [unclosed\n")
    _commit(tmp_path)
    _decision(tmp_path, "DEC-20261005-000001", ["IDEA-20261001-aaaaaa"])  # not committed
    assert _open(tmp_path) == list(IDEAS)
    err = capsys.readouterr().err
    assert "DEC-20261005-00000b.yaml does not parse" in err
    assert "DEC-20261005-000001.yaml carries idea_dispositions but is uncommitted" in err


_OPEN = EP.open_ecc_ideas


def _cli(monkeypatch, capsys, root: Path, *args: str):
    monkeypatch.setattr(EP, "open_ecc_ideas",
                        lambda pol, area=None, **kw: _OPEN(None, area, repo=root, **kw))
    assert EP.main(["--open-ideas", *args]) == 0
    return capsys.readouterr()


def test_disposed_section_is_always_printed(tmp_path, monkeypatch, capsys):
    _fixture(tmp_path, IDEAS)
    _commit(tmp_path)
    out = _cli(monkeypatch, capsys, tmp_path)
    assert "# Disposed by decision: 0" in out.out

    _decision(tmp_path, "DEC-20261005-000001", ["IDEA-20261001-aaaaaa"])
    _commit(tmp_path)
    out = _cli(monkeypatch, capsys, tmp_path, "--limit", "1")
    section = out.out.split("# Disposed by decision: 1", 1)
    assert len(section) == 2
    assert "- IDEA-20261001-aaaaaa  [ECDLP]  DEC-20261005-000001  declined_out_of_question" in section[1]
    assert "IDEA-20261001-aaaaaa" not in section[0]

    # --json: stdout keeps its shape (a list of open rows); the section is on stderr.
    out = _cli(monkeypatch, capsys, tmp_path, "--json")
    rows = json.loads(out.out)
    assert [r["id"] for r in rows] == ["IDEA-20261001-bbbbbb", "IDEA-20261001-cccccc"]
    assert set(rows[0]) == {"id", "area", "question_id", "added", "title", "path",
                            "recommended_priority"}
    assert "# Disposed by decision: 1" in out.err
    assert "IDEA-20261001-aaaaaa" in out.err


def test_real_corpus_never_disposes_ssi_ideas_and_disposes_the_listed_sixteen():
    """DEC-20261005-2ee2e2 PD-1: an SSI idea is never disposed by 138b51; it is
    open unless a hypothesis or experiment references it, then neither."""
    doc = yaml.safe_load((ROOT / "ledger/decisions/DEC-20261005-138b51.yaml").read_text())
    sixteen = {e["id"] for e in doc["coordinator_decision"]["idea_dispositions"]["applies_to_exactly"]}
    assert len(sixteen) == 16
    taken = EP._taken_idea_ids()
    disposed: list = []
    open_ids = {r["id"] for r in EP.open_ecc_ideas(disposed_out=disposed)}
    by_decision = {r["id"]: r["decision_id"] for r in disposed}
    for iid in SSI_IDEAS:
        assert iid not in by_decision, iid
        if iid in taken:
            assert iid not in open_ids, iid
        else:
            assert iid in open_ids, iid
    assert not (sixteen & open_ids)
    for iid in sixteen - taken:
        assert by_decision.get(iid) == "DEC-20261005-138b51", iid
    attributed = [i for i, d in by_decision.items() if d == "DEC-20261005-138b51"]
    assert len(attributed) >= 16 - len(sixteen & taken)
