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
        "evidence:\n  id: EV-ECDLP-001\n  strength: replicated\n"
        "  scope_statement: toy scale only\n  hypothesis_id: H-GONE-999\n")
    (evidence / "broken.yaml").write_text("evidence:\n  id: [unclosed\n")

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
    assert experiment.runs == [{"id": "RUN-ECDLP-001-a", "status": "completed_valid"}]


def test_a_gitkeep_placeholder_is_not_a_run(tiny_repo):
    """`runs/.gitkeep` is how "no runs yet" is committed, not a run."""
    (tiny_repo / "experiments" / "EXP-ECDLP-001" / "runs" / ".gitkeep").write_text("")
    index = ResearchIndex(tiny_repo).build()
    experiment = next(e for e in index.experiments if e.record_id == "EXP-ECDLP-001")
    assert [r["id"] for r in experiment.runs] == ["RUN-ECDLP-001-a"]


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
                     "data/goals.json", "data/experiments.json", "data/integrity.json"):
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
