"""Tests for the read-only research dashboard (`ui/`).

Two things are worth testing here and they are different in kind.

The first is ordinary: the shallow scanner handles every record shape this
corpus actually contains, and the index derives the right boards from them.
Those tests use fixtures and are exact.

The second is a calibration, and it is the reason this file also reads the
real ledger: `ui/scan.py` is deliberately approximate in its first tier, and
an approximation is only safe while somebody measures the error. The
agreement test below parses a sample of real records both ways and asserts
the shallow reading matches the exact one. If a future record shape breaks
the scanner, that test says so instead of the dashboard quietly showing
blank rows.
"""

from __future__ import annotations

import random
import re
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from ui import build as ui_build                       # noqa: E402
from ui import payloads, scan                          # noqa: E402
from ui.index import ResearchIndex                     # noqa: E402


# ---------------------------------------------------------------------------
# Shallow parsing, one test per record shape found in this corpus.
# ---------------------------------------------------------------------------

def test_wrapped_record_with_block_scalar():
    root, fields = scan.shallow_fields(
        "hypothesis:\n"
        "  id: H-ECDLP-a1b2c3\n"
        "  status: proposed\n"
        "  statement: >-\n"
        "    A folded scalar that runs\n"
        "    across two lines.\n"
        "  assumptions:\n"
        "  - first\n"
        "  - second\n"
    )
    assert root == "hypothesis"
    assert fields["id"] == "H-ECDLP-a1b2c3"
    assert fields["status"] == "proposed"
    assert fields["statement"] == "A folded scalar that runs across two lines."
    assert fields["assumptions"] == scan.STRUCTURED


def test_quoted_scalar_continued_on_following_lines():
    root, fields = scan.shallow_fields(
        "research_goal:\n"
        "  id: GOAL-AES-002\n"
        "  title: 'Full-round AES: does any tracked object beat the\n"
        "    exhaustive-key-search reference?'\n"
        "  status: active\n"
    )
    assert root == "research_goal"
    assert fields["title"].startswith("Full-round AES:")
    assert fields["title"].endswith("reference?")
    assert fields["status"] == "active"


def test_flat_record_without_a_wrapping_root():
    root, fields = scan.shallow_fields(
        "decision_id: DEC-20260807-fc6df4\n"
        "goal_id: GOAL-ECDLP-001\n"
        "decision_type: expand\n"
        "status: recorded\n"
    )
    assert root is None
    assert fields["decision_id"] == "DEC-20260807-fc6df4"
    assert fields["decision_type"] == "expand"


def test_flow_style_record_falls_back_to_a_real_parse():
    root, fields = scan.shallow_fields(
        'coordinator_decision: {id: DEC-20260716-004, decision: reject_scoped,\n'
        '  target_ids: [H-FB-001], decided_at: "2026-07-16"}\n'
    )
    assert root == "coordinator_decision"
    assert fields["decision"] == "reject_scoped"
    assert fields["target_ids"] == scan.STRUCTURED


def test_json_record_is_read_exactly():
    root, fields = scan.shallow_fields(
        '{"coordinator_decision": {"id": "DEC-1", "decided_at": "2026-08-24",\n'
        '  "target_ids": ["GOAL-X-1"], "batch_id": null}}'
    )
    assert root == "coordinator_decision"
    assert fields["decided_at"] == "2026-08-24"
    assert fields["batch_id"] == ""                    # explicit null, not STRUCTURED
    assert fields["target_ids"] == scan.STRUCTURED


def test_second_root_key_ends_the_first_record():
    root, fields = scan.shallow_fields(
        "experiment:\n  id: EXP-DREG-001\n  status: running\n"
        "handoff:\n  id: TASK-1\n  status: closed\n"
    )
    assert root == "experiment"
    assert fields["status"] == "running"               # not the handoff's


def test_trailing_comment_is_dropped_and_bare_null_reads_as_empty():
    """`direction: contradicts # the hypothesis` is a direction of `contradicts`,
    and an unquoted `null` is YAML's null -- read as the word it became a date
    that sorted above every real one."""
    _, fields = scan.shallow_fields(
        "evidence:\n"
        "  id: EV-X-001\n"
        "  direction: contradicts # contradicts the hypothesis\n"
        "  decided_at: null\n"
        "  tilde: ~\n"
        "  note: 'kept # not a comment'\n"
        "  quoted_null: 'null'\n"
        "  url: https://example.org/a#frag\n"
    )
    assert fields["direction"] == "contradicts"
    assert fields["decided_at"] == ""
    assert fields["tilde"] == ""
    assert fields["note"] == "kept # not a comment"
    assert fields["quoted_null"] == "null"
    assert fields["url"] == "https://example.org/a#frag"


def test_front_matter_folds_block_scalars_and_marks_structure():
    """`title: >-` over two lines is a title, not the string ">-"."""
    fields = scan.front_matter(
        "---\n"
        "id: KN-FIND-x\n"
        "title: >-\n"
        "  Two lines\n"
        "  of title\n"
        "tags: [a, b]\n"
        "proof_refs:\n"
        "  - p/q.md\n"
        "superseded_by: null\n"
        "added: 2026-09-04\n"
        "---\n"
        "body\n"
    )
    assert fields["title"] == "Two lines of title"
    assert fields["tags"] == scan.STRUCTURED
    assert fields["proof_refs"] == scan.STRUCTURED
    assert fields["superseded_by"] == ""
    assert fields["added"] == "2026-09-04"


# ---------------------------------------------------------------------------
# Identifier grammar. Both forms must link: legacy records are immutable and
# are most of this program's history.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("identifier", [
    "GOAL-ECDLP-001", "GOAL-AUXIN-a93442", "RQ-AES-002", "H-BKKMV-001",
    "EXP-AEADC-22a7e9", "EV-MLKEM-4a9cfe", "DEC-20260904-e1888e",
    "IDEA-20260809-313546", "TASK-20260719-039", "KN-TECH-056", "CORR-20260724-002",
    "RUN-ALBIN-001-import", "BATCH-241d37",
])
def test_identifier_grammar_matches_both_id_forms(identifier):
    assert scan.RECORD_ID_RE.findall(identifier) == [identifier]


def test_area_is_syntactic_and_absent_for_date_keyed_kinds():
    assert scan.id_area("GOAL-ECDLP-001") == "ECDLP"
    assert scan.id_area("EXP-AEADC-22a7e9") == "AEADC"
    assert scan.id_area("DEC-20260904-e1888e") is None
    assert scan.id_area("IDEA-20260809-313546") is None
    assert scan.id_area("TASK-20260719-039") is None


# ---------------------------------------------------------------------------
# Index behaviour, on a fixture repository.
# ---------------------------------------------------------------------------

@pytest.fixture()
def tiny_repo(tmp_path: Path) -> Path:
    goals = tmp_path / "ledger" / "goals"
    goals.mkdir(parents=True)
    (goals / "GOAL-ECDLP-001.yaml").write_text(
        "research_goal:\n"
        "  id: GOAL-ECDLP-001\n"
        "  title: A goal\n"
        "  status: active\n"
        "  question_ids: [RQ-ECDLP-001]\n"
        "  next_action: run EXP-ECDLP-001 next\n"
        "  campaign_budget:\n"
        "    maximum_batches: null\n"
        "    total_wall_clock_seconds: null\n")
    (goals / "GOAL-PAUSED-001.yaml").write_text(
        "research_goal:\n  id: GOAL-PAUSED-001\n  title: Parked\n  status: paused\n")
    sharded = goals / "GOAL-SHARD-001"
    (sharded / "checkpoints").mkdir(parents=True)
    (sharded / "goal.yaml").write_text(
        "research_goal:\n  id: GOAL-SHARD-001\n  title: Sharded\n  status: active\n")
    (sharded / "checkpoints" / "BATCH-aaa111.yaml").write_text(
        "checkpoint:\n  batch_id: BATCH-aaa111\n  recorded_at: '2026-09-01'\n"
        "  summary: did a thing\n")

    questions = tmp_path / "ledger" / "questions"
    questions.mkdir(parents=True)
    (questions / "RQ-ECDLP-001.yaml").write_text(
        "research_question:\n  id: RQ-ECDLP-001\n  title: A question\n  status: open\n")

    evidence = tmp_path / "ledger" / "evidence"
    evidence.mkdir(parents=True)
    (evidence / "EV-ECDLP-001.yaml").write_text(
        "evidence:\n  id: EV-ECDLP-001\n  goal_id: GOAL-ECDLP-001\n  strength: replicated\n"
        "  direction: contradicts # the hypothesis\n  claim_tier: toy\n  proof_status: derivation\n"
        "  scope_statement: toy scale only\n  hypothesis_id: H-GONE-999\n  recorded_at: '2026-09-01'\n"
        "  obstruction:\n"
        "    statement: The first fall degree grows with the summation index.\n"
        "    quantity: first fall degree\n"
        "    value: '5, 5, 6 at m = 2, s = 2..4'\n"
        "    scope: toy instances only\n"
        "    measured_by: [EXP-ECDLP-001]\n"
        "    resource_check:\n      examined: true\n      reading: none found\n      spawned_ids: []\n")
    (evidence / "broken.yaml").write_text("evidence:\n  id: [unclosed\n")

    hypotheses = tmp_path / "ledger" / "hypotheses"
    hypotheses.mkdir(parents=True)
    (hypotheses / "H-ECDLP-001.yaml").write_text(
        "hypothesis:\n  id: H-ECDLP-001\n  question_id: RQ-ECDLP-001\n  goal_id: GOAL-ECDLP-001\n"
        "  statement: Summation polynomials descend in toy fields.\n"
        "  status: weakened\n  added: '2026-08-30'\n")

    decisions = tmp_path / "ledger" / "decisions"
    decisions.mkdir(parents=True)
    (decisions / "DEC-20260902-000001.yaml").write_text(
        "coordinator_decision:\n  id: DEC-20260902-000001\n  decision: support\n"
        "  goal_id: GOAL-ECDLP-001\n  target_ids: [H-ECDLP-001, EV-ECDLP-001]\n"
        "  context: Promotes the toy-scale finding.\n"
        "  knowledge_promotion:\n    promoted: [KN-FIND-001]\n    not_warranted: null\n"
        "  decided_at: null\n  recorded_at: '2026-09-02'\n")

    findings = tmp_path / "knowledge" / "findings"
    findings.mkdir(parents=True)
    (findings / "KN-FIND-001.md").write_text(
        "---\n"
        "id: KN-FIND-001\n"
        "type: internal_finding\n"
        "title: Toy-scale descent measured, not assumed\n"
        "tags: [toy, descent]\n"
        "confidence: reported\n"
        "internal_refs: [EV-ECDLP-001, DEC-20260902-000001, H-ECDLP-001]\n"
        "proof_status: derivation\n"
        "proof_refs:\n  - experiments/EXP-ECDLP-001/analysis/note.md\n"
        "claim_tier: toy\n"
        "added: 2026-09-02\n"
        "superseded_by: null\n"
        "---\n\n"
        "## Provenance\n\nPromoted by DEC-20260902-000001 from EV-ECDLP-001.\n\n"
        "## Finding\n\nTwo halves, of equal weight.\n\n"
        "The first fall degree of the toy system grows with the summation index, so\n"
        "no bounded-degree Macaulay matrix can see the descent.\n\n"
        "- measured at m = 2 and m = 3\n- exact integers, no fit\n\n"
        "## Not claimed\n\nNothing about cryptographic sizes.\n")
    (findings / "KN-FIND-bare01.md").write_text(
        "# A bare finding\n\nThis entry predates the front matter convention.\n")

    problems = tmp_path / "knowledge" / "open-problems"
    problems.mkdir(parents=True)
    (problems / "KN-OPEN-001.md").write_text(
        "---\nid: KN-OPEN-001\ntype: open_problem\ntitle: Does the toy descent scale?\n"
        "tags: [toy, scaling]\nstatus: open\nadded: 2026-08-20\ninternal_refs: [H-ECDLP-001]\n---\n\n"
        "## Statement\nWhether the measured descent survives past 32-bit fields.\n\n"
        "## Current state (as reported)\nNo. Only toy instances have been run.\n\n"
        "## What would resolve it\nA medium-tier replication.\n")

    spec = tmp_path / "experiments" / "EXP-ECDLP-001"
    (spec / "runs" / "RUN-ECDLP-001-a").mkdir(parents=True)
    (spec / "specification.yaml").write_text(
        "experiment:\n  id: EXP-ECDLP-001\n  status: approved\n  frozen: true\n"
        "  title: An experiment\n  hypothesis_id: H-GONE-999\n")
    (spec / "runs" / "RUN-ECDLP-001-a" / "manifest.yaml").write_text(
        "run:\n  id: RUN-ECDLP-001-a\n  status: completed_valid\n")

    policy = tmp_path / "orchestration"
    policy.mkdir()
    (policy / "research-priority.yaml").write_text("ecc_areas: [ECDLP]\n")
    tools = tmp_path / "tools"
    tools.mkdir()
    (tools / "ecc_priority.py").write_text(
        "import yaml\n"
        "def load_policy(path=None):\n"
        "    return yaml.safe_load(open(path).read())\n"
        "def ecc_areas(policy=None):\n"
        "    return set((policy or {}).get('ecc_areas', []))\n")
    return tmp_path


@pytest.fixture()
def tiny_index(tiny_repo: Path) -> ResearchIndex:
    index = ResearchIndex(tiny_repo).build()
    index._deep_scan()                                 # run the sweep synchronously
    return index


def test_index_reads_both_goal_layouts(tiny_index):
    ids = {g.record_id for g in tiny_index.goals}
    assert {"GOAL-ECDLP-001", "GOAL-SHARD-001", "GOAL-PAUSED-001"} <= ids
    sharded = next(g for g in tiny_index.goals if g.record_id == "GOAL-SHARD-001")
    assert sharded.sharded is True
    assert [c["batch_id"] for c in sharded.checkpoints] == ["BATCH-aaa111"]


def test_checkpoint_shards_are_namespaced_by_their_goal(tiny_index):
    """`BATCH-001.yaml` exists under many goals and those do not collide.

    Naming a shard by its batch alone hid every one but the first and filled
    the duplicate-identifier report with ninety false positives, burying the
    real collisions it exists to surface.
    """
    assert "GOAL-SHARD-001~BATCH-aaa111" in tiny_index.records
    shard = tiny_index.records["GOAL-SHARD-001~BATCH-aaa111"]
    assert shard.kind == "BATCH"
    assert shard.area == "SHARD"
    assert not any(d["id"].endswith("BATCH-aaa111")
                   for d in tiny_index.integrity["duplicate_ids"])


def test_ecc_goals_sort_first(tiny_index):
    assert tiny_index.goals[0].record_id == "GOAL-ECDLP-001"
    assert tiny_index.goals[0].ecc is True


def test_ecc_membership_comes_from_the_declared_policy_not_the_prefix(tiny_index):
    """CLAUDE.md rule 11: the area set is declared, never inferred."""
    assert tiny_index.ecc_areas == {"ECDLP"}
    shard = next(g for g in tiny_index.goals if g.record_id == "GOAL-SHARD-001")
    assert shard.ecc is False


def test_forbidden_goal_status_is_flagged(tiny_index):
    """CLAUDE.md rule 10: `paused` and `blocked` are not permitted statuses."""
    paused = next(g for g in tiny_index.goals if g.record_id == "GOAL-PAUSED-001")
    assert any("forbidden" in flag for flag in paused.flags)
    assert any(f["id"] == "GOAL-PAUSED-001" for f in tiny_index.integrity["goal_flags"])


def test_bounded_budget_on_an_ecc_goal_is_flagged(tiny_repo):
    goal = tiny_repo / "ledger" / "goals" / "GOAL-ECDLP-001.yaml"
    goal.write_text(goal.read_text().replace("maximum_batches: null", "maximum_batches: 4"))
    index = ResearchIndex(tiny_repo).build()
    flagged = next(g for g in index.goals if g.record_id == "GOAL-ECDLP-001")
    assert any("maximum_batches" in flag for flag in flagged.flags)


def test_backlinks_are_derived_from_every_mention(tiny_index):
    assert "GOAL-ECDLP-001" in tiny_index.backlinks["RQ-ECDLP-001"]
    assert "GOAL-ECDLP-001" in tiny_index.backlinks["EXP-ECDLP-001"]


def test_dangling_reference_is_reported_not_repaired(tiny_index):
    dangling = {d["id"] for d in tiny_index.integrity["dangling_refs"]}
    assert "H-GONE-999" in dangling
    assert (tiny_index.repo / "ledger" / "evidence" / "EV-ECDLP-001.yaml").read_text()


def test_unparseable_record_is_reported_by_the_deep_scan(tiny_index):
    paths = {u["path"] for u in tiny_index.integrity["unparseable"]}
    assert "ledger/evidence/broken.yaml" in paths
    assert tiny_index.integrity["unparseable_state"] == "complete"


def test_evidence_status_column_uses_strength(tiny_index):
    record = tiny_index.records["EV-ECDLP-001"]
    assert record.status == "replicated"
    assert record.title == "toy scale only"


def test_experiment_runs_are_counted_from_manifests(tiny_index):
    experiment = next(e for e in tiny_index.experiments if e.record_id == "EXP-ECDLP-001")
    assert [(r["id"], r["status"]) for r in experiment.runs] == [
        ("RUN-ECDLP-001-a", "completed_valid")]


def test_an_experiment_is_found_by_its_runs_when_its_contract_is_not_yaml(tiny_repo):
    """Nineteen directories on the real corpus carry `specification.json` or
    only prose, and between them 218 runs. Scanning for `specification.yaml`
    alone reported a run total that was wrong, not merely incomplete."""
    other = tiny_repo / "experiments" / "EXP-JSON-001"
    (other / "runs" / "RUN-JSON-001-a").mkdir(parents=True)
    (other / "specification.json").write_text(
        '{"experiment": {"id": "EXP-JSON-001", "status": "approved", "title": "JSON contract"}}')
    (other / "runs" / "RUN-JSON-001-a" / "manifest.yaml").write_text(
        "run:\n  id: RUN-JSON-001-a\n  status: completed_valid\n")
    prose = tiny_repo / "experiments" / "EXP-PROSE-001"
    (prose / "runs" / "RUN-PROSE-001-a").mkdir(parents=True)
    (prose / "contract.md").write_text("# A contract that is only prose\n")
    (prose / "runs" / "RUN-PROSE-001-a" / "manifest.yaml").write_text(
        "run:\n  id: RUN-PROSE-001-a\n  status: completed_valid\n")

    index = ResearchIndex(tiny_repo).build()
    by_id = {e.record_id: e for e in index.experiments}
    assert set(by_id) == {"EXP-ECDLP-001", "EXP-JSON-001", "EXP-PROSE-001"}
    assert by_id["EXP-JSON-001"].contract == "specification.json"
    assert by_id["EXP-JSON-001"].title == "JSON contract"
    # A directory with runs and no machine-readable contract is still an
    # experiment that ran, and says so rather than vanishing.
    assert by_id["EXP-PROSE-001"].contract == ""
    assert [r["id"] for r in by_id["EXP-PROSE-001"].runs] == ["RUN-PROSE-001-a"]
    assert sum(len(e.runs) for e in index.experiments) == 3


def test_an_empty_directory_under_experiments_is_not_an_experiment(tiny_repo):
    (tiny_repo / "experiments" / "scratch").mkdir()
    (tiny_repo / "experiments" / "EXP-EMPTY-001" / "runs").mkdir(parents=True)
    (tiny_repo / "experiments" / "EXP-EMPTY-001" / "runs" / ".gitkeep").write_text("")
    index = ResearchIndex(tiny_repo).build()
    assert [e.record_id for e in index.experiments] == ["EXP-ECDLP-001"]


def test_a_duplicated_identifier_resolves_to_the_canonical_file(tiny_repo):
    """A superseding copy under `ledger/corrections/` must not displace the
    live record: 31 records on the real corpus showed a v2 body, and linked
    "source" at the correction, purely because that path sorts first."""
    supersession = tiny_repo / "ledger" / "corrections" / "schema-supersessions" / "20260808"
    supersession.mkdir(parents=True)
    (supersession / "ledger__evidence__EV-ECDLP-001.v2.yaml").write_text(
        "evidence:\n  id: EV-ECDLP-001\n  strength: strong\n"
        "  scope_statement: the superseding copy\n")
    index = ResearchIndex(tiny_repo).build()

    record = index.records["EV-ECDLP-001"]
    assert record.path == "ledger/evidence/EV-ECDLP-001.yaml"
    assert record.title == "toy scale only"              # the canonical body
    assert record.status == "replicated"
    # Exactly one entry in the kind bucket, not two.
    assert [r.record_id for r in index.by_kind["EV"]].count("EV-ECDLP-001") == 1
    # And the collision is still reported rather than silently resolved.
    assert any(d["id"] == "EV-ECDLP-001" for d in index.integrity["duplicate_ids"])


def test_a_correction_only_record_is_still_reachable(tiny_repo):
    """Resolution prefers the canonical file; it does not drop a record that
    exists ONLY as a correction copy."""
    supersession = tiny_repo / "ledger" / "corrections" / "schema-supersessions" / "20260808"
    supersession.mkdir(parents=True)
    (supersession / "ledger__evidence__EV-ONLY-001.v2.yaml").write_text(
        "evidence:\n  id: EV-ONLY-001\n  strength: moderate\n")
    index = ResearchIndex(tiny_repo).build()
    assert index.records["EV-ONLY-001"].path.startswith("ledger/corrections/")


def test_a_gitkeep_placeholder_is_not_a_run(tiny_repo):
    """`runs/.gitkeep` is how "no runs yet" is committed, not a run."""
    (tiny_repo / "experiments" / "EXP-ECDLP-001" / "runs" / ".gitkeep").write_text("")
    index = ResearchIndex(tiny_repo).build()
    experiment = next(e for e in index.experiments if e.record_id == "EXP-ECDLP-001")
    assert [r["id"] for r in experiment.runs] == ["RUN-ECDLP-001-a"]


def test_run_timing_is_read_from_the_manifest_and_measured_when_it_can_be(tiny_repo):
    """A run that declares a start and a finish has a duration whether or not
    it reports one; a run that declares nothing reports nothing."""
    runs = tiny_repo / "experiments" / "EXP-ECDLP-001" / "runs"
    (runs / "RUN-ECDLP-001-timed").mkdir()
    (runs / "RUN-ECDLP-001-timed" / "manifest.yaml").write_text(
        "run:\n  id: RUN-ECDLP-001-timed\n  status: completed_valid\n"
        "  started_at: '2026-09-04T04:45:19Z'\n"
        "  finished_at: '2026-09-04T04:50:19Z'\n")
    (runs / "RUN-ECDLP-001-declared").mkdir()
    (runs / "RUN-ECDLP-001-declared" / "manifest.yaml").write_text(
        "run:\n  id: RUN-ECDLP-001-declared\n  status: completed_valid\n"
        "  started_at: '2026-09-04T04:45:19+00:00'\n  wall_seconds: 42.5\n")
    index = ResearchIndex(tiny_repo).build()
    by_id = {r["id"]: r for e in index.experiments for r in e.runs}

    measured = by_id["RUN-ECDLP-001-timed"]
    assert measured["started"] == "2026-09-04T04:45:19Z"
    assert measured["duration_seconds"] == 300.0          # measured, not declared
    declared = by_id["RUN-ECDLP-001-declared"]
    assert declared["duration_seconds"] == 42.5           # the manifest's own number wins
    assert declared["finished"] == ""
    silent = by_id["RUN-ECDLP-001-a"]
    assert silent["started"] == "" and silent["duration_seconds"] is None


def test_a_prose_date_is_not_read_as_a_timestamp():
    """`approved_at: after review` is not a date, and rendering it as one
    would put a fiction in a date column."""
    from ui.index import _epoch, _pick_date
    assert _pick_date({"approved_at": "after the review"}, ("approved_at",)) == ("", "")
    assert _pick_date({"approved_at": "null"}, ("approved_at",)) == ("", "")
    assert _pick_date({"approved_at": "2026-08-04"}, ("approved_at",)) == ("approved_at", "2026-08-04")
    # The field NAME travels with the value: approved and merely recorded are
    # different facts about a contract.
    assert _pick_date({"recorded_at": "2026-08-04"},
                      ("approved_at", "recorded_at")) == ("recorded_at", "2026-08-04")
    assert _epoch("2026-08-04T00:00:00Z") == _epoch("2026-08-04")     # naive reads as UTC
    assert _epoch("not a date") is None


def test_a_json_manifest_is_read_like_a_yaml_one(tiny_repo):
    runs = tiny_repo / "experiments" / "EXP-ECDLP-001" / "runs"
    (runs / "RUN-ECDLP-001-b").mkdir()
    (runs / "RUN-ECDLP-001-b" / "manifest.json").write_text(
        '{"run": {"id": "RUN-ECDLP-001-b", "status": "failed_infrastructure"}}')
    (runs / "_lib").mkdir()                            # shared code, not a run
    index = ResearchIndex(tiny_repo).build()
    experiment = next(e for e in index.experiments if e.record_id == "EXP-ECDLP-001")
    assert {r["id"]: r["status"] for r in experiment.runs} == {
        "RUN-ECDLP-001-a": "completed_valid",
        "RUN-ECDLP-001-b": "failed_infrastructure",
    }


def test_full_record_is_an_exact_parse(tiny_index):
    parsed, error = tiny_index.full_record("EV-ECDLP-001")
    assert error is None
    assert parsed["evidence"]["strength"] == "replicated"


def test_undated_records_sort_last_not_first():
    """An absent date is the oldest possible, not the newest.

    Getting this backwards floated every undated record to the top of every
    list, which is what the browser actually showed before it was fixed.
    """
    from ui.index import _neg_date
    assert _neg_date("2026-09-04") < _neg_date("2026-08-31") < _neg_date("")


def test_search_ranks_identifier_matches_first(tiny_index):
    hits, total = tiny_index.search("EV-ECDLP-001")
    assert total >= 1
    assert hits[0].record_id == "EV-ECDLP-001"


def test_the_index_writes_nothing(tiny_repo):
    """The dashboard is an observer. It holds no authority in the program."""
    before = {p: p.stat().st_mtime_ns for p in tiny_repo.rglob("*") if p.is_file()}
    index = ResearchIndex(tiny_repo).build()
    index._deep_scan()
    index.full_record("EV-ECDLP-001")
    index.search("anything")
    after = {p: p.stat().st_mtime_ns for p in tiny_repo.rglob("*") if p.is_file()}
    assert before == after


# ---------------------------------------------------------------------------
# Calibration against the real corpus.
# ---------------------------------------------------------------------------

REAL_LEDGER = REPO / "ledger"


@pytest.mark.skipif(not REAL_LEDGER.is_dir(), reason="no ledger/ in this checkout")
def test_shallow_reading_agrees_with_the_exact_parse():
    """Measure the first tier's error rather than assuming it away.

    A floor, not an exact number: the corpus grows with every batch and is a
    different size in every worktree. What must not drift is the agreement
    RATE -- a new record shape the scanner cannot read would push it down.
    """
    paths = sorted(REAL_LEDGER.rglob("*.yaml"))
    if len(paths) < 50:
        pytest.skip("ledger too small to calibrate against")
    random.Random(20260904).shuffle(paths)

    agree = disagree = 0
    for path in paths[:400]:
        record = scan.scan_file(path, REPO)
        try:
            doc = yaml.safe_load(path.read_text(encoding="utf-8", errors="replace"))
        except Exception:                              # noqa: BLE001 - integrity's problem
            continue
        if not isinstance(doc, dict):
            continue
        body = doc
        if len(doc) == 1 and isinstance(next(iter(doc.values())), dict):
            body = next(iter(doc.values()))
        for key, want in body.items():
            if isinstance(want, bool) or not isinstance(want, (str, int, float)):
                continue
            expected = re.sub(r"\s+", " ", str(want)).strip()
            got = record.fields.get(key)
            if got == expected:
                agree += 1
            elif got is not None and expected.startswith(got[:40]):
                agree += 1                             # quoting artefact, same field
            else:
                disagree += 1

    total = agree + disagree
    assert total > 500, f"only {total} scalar fields sampled"
    rate = agree / total
    assert rate >= 0.98, f"shallow/exact agreement fell to {rate:.3%} ({disagree} of {total})"


@pytest.mark.skipif(not REAL_LEDGER.is_dir(), reason="no ledger/ in this checkout")
def test_every_real_record_yields_an_identifier():
    """No row in the browser may be nameless."""
    nameless = [
        str(record.path) for record in scan.scan_ledger(REPO) if not record.record_id
    ]
    assert not nameless


# ---------------------------------------------------------------------------
# The static build. The published site and the local server must serve the
# SAME data contract -- two products that disagree about their own data are
# one product and one bug.
# ---------------------------------------------------------------------------

@pytest.fixture()
def built_site(tiny_repo: Path, tmp_path: Path) -> Path:
    out = tmp_path / "site"
    ui_build.build(tiny_repo, out, verbose=False)
    return out


def _json(path: Path):
    import json
    return json.loads(path.read_text(encoding="utf-8"))


def test_build_emits_every_file_the_client_boots_from(built_site):
    for required in ("index.html", "app.js", "app.css", ".nojekyll",
                     "data/meta.json", "data/index.json", "data/overview.json",
                     "data/goals.json", "data/experiments.json", "data/findings.json",
                     "data/integrity.json"):
        assert (built_site / required).is_file(), required


def test_build_emits_one_page_per_record_and_per_goal(tiny_repo, built_site):
    index = ResearchIndex(tiny_repo).build()
    for record_id in index.records:
        assert (built_site / "data" / "records" / f"{record_id}.json").is_file(), record_id
    for goal in index.goals:
        assert (built_site / "data" / "goals" / f"{goal.record_id}.json").is_file()


def test_index_rows_match_the_declared_columns(built_site):
    meta = _json(built_site / "data" / "meta.json")
    rows = _json(built_site / "data" / "index.json")
    assert meta["columns"] == payloads.INDEX_COLUMNS
    assert rows and all(len(row) == len(meta["columns"]) for row in rows)


def test_meta_says_which_commit_the_snapshot_is_of(built_site):
    """A static page must not imply freshness it does not have."""
    meta = _json(built_site / "data" / "meta.json")
    assert meta["mode"] == "static"
    assert meta["built_at"]
    assert "commit" in meta and "repo_url" in meta


def test_the_snapshot_does_not_bundle_source_text(built_site):
    """116 MB of YAML that is one click away on GitHub is not worth shipping."""
    payload = _json(built_site / "data" / "records" / "EV-ECDLP-001.json")
    assert "raw" not in payload
    assert payload["body"]["strength"] == "replicated"


def test_links_are_identifiers_not_embedded_summaries(built_site):
    """The browser already holds every summary; embedding them again tripled
    the detail files for nothing."""
    payload = _json(built_site / "data" / "records" / "GOAL-ECDLP-001.json")
    assert all(isinstance(x, str) for x in payload["links"]["out"])
    assert "RQ-ECDLP-001" in payload["links"]["out"]


def test_search_shards_cover_every_indexed_kind(tiny_repo, built_site):
    index = ResearchIndex(tiny_repo).build()
    for kind, records in index.by_kind.items():
        shard = _json(built_site / "data" / "search" / f"{kind}.json")
        assert shard["ids"] == [r.record_id for r in records]
        assert len(shard["text"]) == len(shard["ids"])


def test_a_second_build_replaces_rather_than_accumulates(tiny_repo, built_site):
    stale = built_site / "data" / "records" / "GONE-999.json"
    stale.write_text("{}")
    ui_build.build(tiny_repo, built_site, verbose=False)
    assert not stale.exists()


def test_the_build_touches_nothing_but_its_output_directory(tiny_repo, tmp_path):
    """The read-only property survives the static build.

    The one thing the builder writes is the directory it was told to write.
    That directory defaults to `site/` INSIDE the repository, which is why
    `/site/` is gitignored -- so this builds to a sibling and asserts the
    corpus itself is untouched.
    """
    out = tmp_path.parent / "outside-site"
    before = {p: p.stat().st_mtime_ns for p in tiny_repo.rglob("*") if p.is_file()}
    ui_build.build(tiny_repo, out, verbose=False)
    after = {p: p.stat().st_mtime_ns for p in tiny_repo.rglob("*") if p.is_file()}
    assert before == after
    assert (out / "data" / "meta.json").is_file()


def test_build_report_carries_what_ci_gates_on(tiny_repo, tmp_path):
    report = ui_build.build(tiny_repo, tmp_path.parent / "report-site", verbose=False)
    assert report["records"] == len(ResearchIndex(tiny_repo).build().records)
    assert report["files"] > 0 and report["bytes"] > 0


def test_ssh_remotes_normalise_to_a_browsable_url(monkeypatch, tmp_path):
    monkeypatch.delenv("GITHUB_REPOSITORY", raising=False)
    monkeypatch.setattr(ui_build, "_git",
                        lambda repo, *a: "git@github.com:owner/repo.git")
    assert ui_build.resolve_repo_url(tmp_path) == "https://github.com/owner/repo"


def test_actions_environment_wins_over_the_local_checkout(monkeypatch, tmp_path):
    """In Actions the checkout can be a detached merge commit whose HEAD is
    not a sha anyone can browse to."""
    monkeypatch.setenv("GITHUB_REPOSITORY", "owner/repo")
    monkeypatch.setenv("GITHUB_SERVER_URL", "https://github.com")
    monkeypatch.setenv("GITHUB_SHA", "0" * 40)
    assert ui_build.resolve_repo_url(tmp_path) == "https://github.com/owner/repo"
    assert ui_build.resolve_commit(tmp_path) == "0" * 40


def test_no_remote_means_no_source_links_rather_than_broken_ones(monkeypatch, tmp_path):
    monkeypatch.delenv("GITHUB_REPOSITORY", raising=False)
    monkeypatch.setattr(ui_build, "_git", lambda repo, *a: "")
    assert ui_build.resolve_repo_url(tmp_path) == ""


def test_the_integrity_report_published_is_a_measured_one(built_site):
    """The sweep is waited for at build time: publishing an empty
    `unparseable` list under state "running" would report a clean sweep that
    never happened."""
    integrity = _json(built_site / "data" / "integrity.json")
    assert integrity["unparseable_state"] == "complete"
    assert "ledger/evidence/broken.yaml" in {u["path"] for u in integrity["unparseable"]}


# ---------------------------------------------------------------------------
# Findings: the program's output, read exactly. A findings board that showed
# titles without claims, or claims without their basis, would be decoration.
# ---------------------------------------------------------------------------

from ui.index import statement_excerpt, split_front_matter  # noqa: E402


def test_statement_excerpt_prefers_the_statement_section_and_its_blockquote():
    body = (
        "## Provenance\n\nCame from somewhere.\n\n"
        "## What this says, and what it does NOT say\n\n"
        "**Not toy.** Some framing first.\n\n"
        "> The estimator is chaotic when m << n.\n\n"
        "More prose after the quote.\n"
    )
    assert statement_excerpt(body) == "The estimator is chaotic when m << n."


def test_statement_excerpt_joins_a_framing_sentence_with_the_claim_after_it():
    body = "## Finding\n\nTwo halves, of equal weight.\n\nThe degree grows.\n\n- measured\n- exact\n"
    assert statement_excerpt(body) == "Two halves, of equal weight. The degree grows. measured exact"


def test_statement_excerpt_falls_back_to_the_first_prose_and_clips_at_a_word():
    body = "Just a paragraph " + "word " * 300
    out = statement_excerpt(body, limit=80)
    assert out.startswith("Just a paragraph word") and out.endswith("…") and len(out) <= 81


def test_split_front_matter_is_exact_and_reports_absence():
    front, body, error = split_front_matter("---\nid: KN-X\ntags: [a, b]\nadded: 2026-01-02\n---\n\n# Body\n")
    assert error is None and front["tags"] == ["a", "b"] and body.strip() == "# Body"
    assert split_front_matter("# no front matter\n")[2] == "no front matter"
    assert split_front_matter("---\nid: [unclosed\n---\nbody\n")[2].startswith(("ScannerError", "ParserError"))


def test_findings_are_parsed_exactly_and_attributed_through_their_evidence(tiny_index):
    finding = next(f for f in tiny_index.findings if f.record_id == "KN-FIND-001")
    assert finding.title == "Toy-scale descent measured, not assumed"
    assert finding.proof_status == "derivation" and finding.claim_tier == "toy"
    assert finding.status == "current" and finding.error is None
    assert finding.proof_refs == 1 and finding.tags == ["toy", "descent"]
    assert finding.refs[:3] == ["EV-ECDLP-001", "DEC-20260902-000001", "H-ECDLP-001"]
    # The entry never names its goal; the evidence it rests on does.
    assert finding.goal_ids == ["GOAL-ECDLP-001"]
    assert finding.areas == ["ECDLP"]                    # not the cited KN entries' families
    assert finding.excerpt.startswith("Two halves, of equal weight. The first fall degree")
    assert "measured at m = 2 and m = 3" in finding.excerpt


def test_a_finding_without_front_matter_still_indexes_and_says_so(tiny_index):
    bare = next(f for f in tiny_index.findings if f.record_id == "KN-FIND-bare01")
    assert bare.error == "no front matter"
    assert bare.title == "A bare finding"                # from its heading
    assert bare.status == "current" and bare.excerpt.startswith("This entry predates")


def test_open_problems_carry_statement_state_and_resolution(tiny_index):
    problem = tiny_index.open_problems[0]
    assert problem.record_id == "KN-OPEN-001" and problem.status == "open"
    assert problem.statement == "Whether the measured descent survives past 32-bit fields."
    assert problem.current_state == "No. Only toy instances have been run."
    assert problem.resolution == "A medium-tier replication."


def test_obstruction_blocks_are_read_exactly_from_evidence(tiny_index):
    assert len(tiny_index.obstructions) == 1
    block = tiny_index.obstructions[0]
    assert block.evidence_id == "EV-ECDLP-001" and block.goal_id == "GOAL-ECDLP-001"
    assert block.statement == "The first fall degree grows with the summation index."
    assert block.quantity == "first fall degree" and block.value == "5, 5, 6 at m = 2, s = 2..4"
    assert block.measured_by == ["EXP-ECDLP-001"]
    assert block.resource_examined is True and block.resource_reading == "none found"


def test_knowledge_families_are_a_facet_of_their_own_not_areas(tiny_index):
    facets = tiny_index.facets()
    assert {f["key"] for f in facets["knowledge"]} == {"FIND", "OPEN"}
    assert "FIND" not in {a["key"] for a in facets["areas"]}
    assert "ECDLP" in {a["key"] for a in facets["areas"]}


def test_a_null_date_falls_through_to_the_next_date_field(tiny_index):
    decision = tiny_index.records["DEC-20260902-000001"]
    assert decision.date == "2026-09-02"                  # recorded_at, not the word "null"


def test_hypothesis_verdicts_fold_scoped_spellings_and_skip_design_stages():
    assert payloads.hypothesis_verdict("supported_scoped_two_adjacent_toy_instances") == "supported_scoped"
    assert payloads.hypothesis_verdict("supported") == "supported"
    assert payloads.hypothesis_verdict("weakened") == "weakened"
    assert payloads.hypothesis_verdict("proposed_instrument_underexplored_single_cell_inconclusive") is None
    assert payloads.hypothesis_verdict("approved") is None


def test_direction_polarity_folds_forty_spellings_into_four():
    fold = payloads.direction_polarity
    assert fold("supports_with_caveat") == "supports" and fold("confirms") == "supports"
    assert fold("weakening_scoped") == "weakens" and fold("refutes_own_prior_reading") == "weakens"
    assert fold("neutral") == "neutral" and fold("") == "neutral" and fold("n/a") == "neutral"
    assert fold("corrects_prior") == "mixed" and fold("revises") == "mixed"


def test_findings_payload_carries_every_board(tiny_index):
    payload = payloads.findings_payload(tiny_index)
    assert payload["counts"]["findings"] == 2 and payload["counts"]["current"] == 2
    assert payload["counts"]["by_proof_status"]["derivation"] == 1
    verdicts = payload["hypothesis_verdicts"]
    assert [v["id"] for v in verdicts] == ["H-ECDLP-001"]
    assert verdicts[0]["verdict"] == "weakened"
    assert verdicts[0]["decision_ids"] == ["DEC-20260902-000001"]
    evidence = next(e for e in payload["evidence"] if e["id"] == "EV-ECDLP-001")
    assert evidence["direction"] == "contradicts" and evidence["polarity"] == "weakens"
    assert evidence["neutral"] is False and evidence["goal_id"] == "GOAL-ECDLP-001"
    assert evidence["finding_ids"] == ["KN-FIND-001"]
    # `broken.yaml` is an evidence record too, with no direction: neutral.
    assert payload["evidence_counts"]["polarity"] == {"neutral": 1, "weakens": 1}
    assert [o["evidence_id"] for o in payload["obstructions"]] == ["EV-ECDLP-001"]
    assert payload["open_problems"][0]["id"] == "KN-OPEN-001"


def test_overview_leads_with_findings_and_the_pipeline(tiny_index):
    overview = payloads.overview_payload(tiny_index)
    assert overview["findings"]["current"] == 2
    assert overview["findings"]["latest"][0]["id"] == "KN-FIND-001"    # newest first
    assert [s["label"] for s in overview["pipeline"]] == [
        "questions", "proposals", "hypotheses", "experiments", "runs", "evidence",
        "decisions", "findings"]
    stages = {s["key"]: s for s in overview["pipeline"]}
    assert stages["H"]["note"] == "1 with a verdict"
    assert stages["EV"]["note"] == "1 with a direction"
    assert stages["FIND"]["count"] == 2 and stages["FIND"]["note"] is None
    assert overview["recent_decisions"] == ["DEC-20260902-000001"]
    assert overview["hypothesis_verdicts"] == {"weakened": 1}
    assert overview["evidence_polarity"] == {"neutral": 1, "weakens": 1}
    assert overview["open_problems"]["latest"][0]["id"] == "KN-OPEN-001"


def test_build_emits_the_findings_board(built_site):
    board = _json(built_site / "data" / "findings.json")
    assert {"findings", "counts", "hypothesis_verdicts", "evidence", "evidence_counts",
            "obstructions", "open_problems"} <= set(board)
    assert board["findings"][0]["id"] == "KN-FIND-001"


def test_findings_are_filed_under_one_area_and_carry_their_non_claim(tiny_index):
    finding = next(f for f in tiny_index.findings if f.record_id == "KN-FIND-001")
    assert finding.area == "ECDLP"                       # its goal's area
    assert finding.non_claim == "Nothing about cryptographic sizes."
    bare = next(f for f in tiny_index.findings if f.record_id == "KN-FIND-bare01")
    assert bare.area is None and bare.non_claim == ""


def test_open_problems_are_attributed_through_their_citations(tiny_index):
    problem = tiny_index.open_problems[0]
    assert problem.goal_ids == ["GOAL-ECDLP-001"]       # via H-ECDLP-001's goal_id
    assert problem.area == "ECDLP" and problem.areas == ["ECDLP"]


def test_directions_roll_the_program_up_by_area(tiny_index):
    payload = payloads.findings_payload(tiny_index)
    rows = {r["area"]: r for r in payload["directions"]}
    assert payload["directions"][0]["area"] == "ECDLP"   # ECC first
    ecdlp = rows["ECDLP"]
    assert ecdlp["ecc"] is True
    assert [g["id"] for g in ecdlp["goals"]] == ["GOAL-ECDLP-001"] and ecdlp["active_goals"] == 1
    assert ecdlp["findings"] == 1 and ecdlp["latest_finding"]["id"] == "KN-FIND-001"
    assert ecdlp["verdicts"] == {"weakened": 1}
    assert ecdlp["evidence"] == {"supports": 0, "weakens": 1, "mixed": 0, "neutral": 0}
    assert ecdlp["open_problems"] == 1 and ecdlp["hypotheses"] == 1 and ecdlp["experiments"] == 1
    assert rows["SHARD"]["findings"] == 0                # a goal with nothing established yet
    assert rows["SHARD"]["latest_finding"] is None
    overview = payloads.overview_payload(tiny_index)
    assert overview["directions"]["total"] == len(payload["directions"])
    assert overview["directions"]["top"][0]["area"] == "ECDLP"


def test_added_within_counts_current_findings_against_the_given_day(tiny_index):
    from datetime import date
    assert payloads.added_within(tiny_index, 7, today=date(2026, 9, 5)) == 1   # added 2026-09-02
    assert payloads.added_within(tiny_index, 1, today=date(2026, 9, 5)) == 0


def test_built_shell_versions_its_assets(built_site):
    """A browser that cached `app.js` must not run the old client against a
    new deploy's data."""
    html = (built_site / "index.html").read_text(encoding="utf-8")
    assert 'src="app.js?v=' in html and 'href="app.css?v=' in html
    assert ui_build.version_assets('<script src="app.js"></script>', "abc/def0123456789") \
        == '<script src="app.js?v=abcdef012345"></script>'


def test_a_knowledge_entry_page_carries_its_body_and_front_matter(built_site):
    """The body IS the entry. Without it a finding's page was a title and a
    link to GitHub, which is not a page."""
    payload = _json(built_site / "data" / "records" / "KN-FIND-001.json")
    assert payload["verified"] is True
    assert payload["body"]["proof_status"] == "derivation"
    assert "## Finding" in payload["markdown"]
    assert "raw" not in payload                            # source text still not bundled
    bare = _json(built_site / "data" / "records" / "KN-FIND-bare01.json")
    assert bare["verified"] is False and bare["parse_error"] == "no front matter"
    assert bare["markdown"].startswith("# A bare finding")


# ---------------------------------------------------------------------------
# Commit dates. Most of this corpus declares no date, so git supplies one --
# but only when history is really there to read.
# ---------------------------------------------------------------------------

from ui import gitdates                                  # noqa: E402


def _epoch_of(iso: str) -> int:
    from datetime import datetime
    return int(datetime.fromisoformat(iso.replace("Z", "+00:00")).timestamp())


def _git(repo: Path, *args: str, when: str | None = None) -> None:
    """Run git, optionally pinning the commit's time.

    Both dates are pinned: `ui/gitdates.py` reads the COMMITTER date (`%ct`),
    which is when a commit landed in this history -- stable here because
    `main` takes merge commits and never squashes (CLAUDE.md). Setting only
    `--date`, the author date, leaves the committer date at "now" and every
    fixture commit lands in the same second.
    """
    import os
    import subprocess
    env = dict(os.environ)
    if when:
        env["GIT_COMMITTER_DATE"] = when
        env["GIT_AUTHOR_DATE"] = when
    subprocess.run(["git", "-C", str(repo), *args], check=True,
                   capture_output=True, text=True, env=env)


@pytest.fixture()
def git_repo(tiny_repo: Path) -> Path:
    import subprocess
    if subprocess.run(["git", "--version"], capture_output=True).returncode != 0:
        pytest.skip("git is unavailable")
    _git(tiny_repo, "init", "-q", "-b", "main")
    _git(tiny_repo, "config", "user.email", "t@example.invalid")
    _git(tiny_repo, "config", "user.name", "Test")
    _git(tiny_repo, "add", "-A")
    _git(tiny_repo, "commit", "-q", "-m", "first", when="2026-08-01T10:00:00Z")
    (tiny_repo / "ledger" / "evidence" / "EV-ECDLP-002.yaml").write_text(
        "evidence:\n  id: EV-ECDLP-002\n  strength: strong\n")
    _git(tiny_repo, "add", "-A")
    _git(tiny_repo, "commit", "-q", "-m", "second", when="2026-08-05T10:00:00Z")
    return tiny_repo


def test_commit_dates_are_read_from_history(git_repo):
    dates = gitdates.load(git_repo)
    assert dates.available and dates.error is None
    first, last = dates.of("ledger/evidence/EV-ECDLP-001.yaml")
    added, _ = dates.of("ledger/evidence/EV-ECDLP-002.yaml")
    assert first and last and added
    # Exact instants, so a drifting clock cannot make this pass by accident.
    assert first == last == _epoch_of("2026-08-01T10:00:00Z")
    assert added == _epoch_of("2026-08-05T10:00:00Z")
    assert dates.of("ledger/evidence/does-not-exist.yaml") == (None, None)


def test_an_amended_record_shows_a_later_last_commit_than_its_first(git_repo):
    """Records are immutable, so first and last are usually equal. When they
    differ the file was changed in place, and the page says so."""
    goal = git_repo / "ledger" / "goals" / "GOAL-ECDLP-001.yaml"
    goal.write_text(goal.read_text() + "  updated_at: '2026-08-09'\n")
    _git(git_repo, "add", "-A")
    _git(git_repo, "commit", "-q", "-m", "third", when="2026-08-09T10:00:00Z")
    dates = gitdates.load(git_repo)
    first, last = dates.of("ledger/goals/GOAL-ECDLP-001.yaml")
    assert first == _epoch_of("2026-08-01T10:00:00Z")
    assert last == _epoch_of("2026-08-09T10:00:00Z")


def test_a_directory_span_covers_everything_under_it(git_repo):
    """A run is a directory of artifacts, so its arrival is the first commit
    touching any of them."""
    dates = gitdates.load(git_repo)
    first, last = dates.dir_span("experiments/EXP-ECDLP-001/runs/RUN-ECDLP-001-a")
    assert first and last
    assert first == dates.of("experiments/EXP-ECDLP-001/runs/RUN-ECDLP-001-a/manifest.yaml")[0]


def test_a_shallow_clone_yields_no_dates_rather_than_identical_ones(git_repo, tmp_path):
    """The failure this guards is not a missing value but a WRONG one: under
    a depth-1 checkout every record reports the same commit time, and that
    looks entirely plausible on a page."""
    shallow = tmp_path / "shallow"
    _git(git_repo, "clone", "-q", "--depth", "1", f"file://{git_repo}", str(shallow))
    dates = gitdates.load(shallow)
    assert dates.available is False
    assert "shallow" in (dates.error or "")
    assert dates.of("ledger/evidence/EV-ECDLP-001.yaml") == (None, None)


def test_a_contract_less_experiment_is_dated_by_its_directory(git_repo):
    """Its `path` is a directory, which has no commit of its own: the date
    has to come from the span of everything under it."""
    prose = git_repo / "experiments" / "EXP-PROSE-001"
    (prose / "runs" / "RUN-PROSE-001-a").mkdir(parents=True)
    (prose / "runs" / "RUN-PROSE-001-a" / "manifest.yaml").write_text(
        "run:\n  id: RUN-PROSE-001-a\n  status: completed_valid\n")
    _git(git_repo, "add", "-A")
    _git(git_repo, "commit", "-q", "-m", "prose experiment", when="2026-08-07T10:00:00Z")

    index = ResearchIndex(git_repo).build()
    experiment = next(e for e in index.experiments if e.record_id == "EXP-PROSE-001")
    assert experiment.contract == ""
    assert experiment.committed == _epoch_of("2026-08-07T10:00:00Z")


def test_a_directory_that_is_not_a_repository_reports_why(tiny_repo):
    dates = gitdates.load(tiny_repo)
    assert dates.available is False and dates.error
    assert dates.of("anything") == (None, None)


def test_experiments_payload_separates_declared_dates_from_observed_ones(tiny_index):
    payload = payloads.experiments_payload(tiny_index)
    row = payload["experiments"][0]
    assert row["id"] == "EXP-ECDLP-001"
    assert row["dated"] == "" and row["date_field"] == ""   # this contract declares none
    timing = payload["timing"]
    assert timing["runs"] == 1 and timing["experiments"] == 1
    assert timing["runs_with_declared_start"] == 0
    # The fixture is not a git repository, so the honest answer is "no dates".
    assert timing["git"]["available"] is False and timing["git"]["error"]


def test_the_build_reports_whether_commit_dates_were_available(built_site):
    meta = _json(built_site / "data" / "meta.json")
    assert "git" in meta and "available" in meta["git"]
    experiments = _json(built_site / "data" / "experiments.json")
    assert "timing" in experiments
    assert experiments["timing"]["git"]["available"] == meta["git"]["available"]
