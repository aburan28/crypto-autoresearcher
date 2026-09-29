"""Write implementation_report.yaml: files + sha256, tests, smoke, open questions.

  python3 -m pytest -p no:cacheprovider -q -rs tests > test-results.txt
  python3 make_report.py
"""

from __future__ import annotations

import datetime as dt
import json
import re
from pathlib import Path

import yaml

import driver
import fixtures

HERE = Path(__file__).resolve().parent
REPORT = HERE / "implementation_report.yaml"

OPEN_QUESTIONS = [
    ("OQ-1", "C-2/C-4 log base L",
     "L = number of liftable FB x-classes below B is 2..14 on the frozen fixtures (b16-s12 has L=2), "
     "so log_L readings are coarse and differ strongly between fixtures of one size.",
     "Implemented exactly as written; delta null when L < 2 or cycle_rank = 0 (reason recorded)."),
    ("OQ-2", "C-5 'delta_proof lower 95% CI'",
     "The population over which the CI is taken is not stated.",
     "Per size x budget, Student-t over the three seed fixtures: mean - t_{0.975,2} sd/sqrt(3); "
     "any null delta_proof in the cell makes the CI undefined (clause fails)."),
    ("OQ-3", "C-5 'flat or rising trend'",
     "No test for 'flat' is given.",
     "Per budget, OLS slope of delta_proof on bits over the nine fixtures; flat-or-rising iff the upper "
     "end of its two-sided 95% t-interval is >= 0."),
    ("OQ-4", "C-5 'ER null with identical |V|, |E| does not also exceed 1/4'",
     "Aggregation unstated. Structural pre-data remark (from the definitions only): G(|V|,|E|) has the "
     "same |E|-|V| as the treatment graph, so its cycle rank differs only through its component count; "
     "whenever the treatment clears 1/4, ER typically does too unless the treatment graph has many more "
     "components. Under any aggregation the supercritical-enriched verdict is therefore reachable only "
     "if the observed graph is markedly more fragmented than ER.",
     "ER 'exceeds' in a size x budget cell iff the mean ER delta_proof over its 3 x 32 replicates "
     "(null replicates excluded) is > 1/4; supercritical-enriched requires that this happens in NO cell. "
     "Reported in full so any other aggregation can be recomputed."),
    ("OQ-5", "C-5 subcritical 'at all sizes'",
     "Per fixture or per size mean, and which budget(s), unstated.",
     "Both inequalities (giant fraction < 0.05; cycle_rank <= 2 x components-with-cycle) at every one of "
     "the nine fixtures at both budgets. If both rules fire: inconclusive ('both_rules_fired')."),
    ("OQ-6", "C-4 vertex set of the LP graph",
     "Whether V is all liftable LP classes in [B, B2) or only those on an edge.",
     "V = root + LP classes incident to at least one LP edge. Cycle rank is unaffected (an isolated "
     "vertex adds 1 to |V| and to c); |V|, |E|/|V|, giant fraction, ER and planted sizes are affected. "
     "The count of liftable LP classes is recorded in the header for recomputation."),
    ("OQ-7", "C-3 multiple decompositions and degenerate hits",
     "'Decide exactly whether R_j = e1 P1 + e2 P2' does not say which relation is kept when several exist, "
     "nor how R_j = P1 (T = O) or R_j = O are handled.",
     "Full scan always (all charged); the relation kept is the first distinct unordered pair in (x, y) "
     "scan order; extra decompositions are counted (extra_decompositions). R_j = P1 is a recorded "
     "single-point hit, not a two-point relation and not an edge; R_j = O is recorded as R_is_O "
     "(construction charged, no scan). Both count as failed attempts."),
    ("OQ-8", "C-3 scan set",
     "'All points with x < B2' read literally includes both signs.",
     "Both signs scanned (2x the minimal x-only scan); every point operation, trivial ones included, "
     "charged as one group op."),
    ("OQ-9", "Seed labels not fixed by the protocol",
     "C-3 gives one label per attempt for two draws; C-6 gives '.../rewire|<i>' without per-fixture or "
     "per-draw parts; ER, planted, scramble, rho and audit labels are unspecified.",
     "a_j, b_j from '<attempt label>|a' and '|b'; rewire draws '<ns>|rewire|<i>|<bits>|<seed>|<budget>|"
     "<draw>'; ER '<ns>|er|<i>|...'; planted, scramble, rho, rho_walk, audit as listed in labels.py. "
     "Rejection retries append '|rej<r>'."),
    ("OQ-10", "C-6 '10% of attempts (SHA256-selected)'",
     "Exact 10% vs a hash predicate.",
     "Attempt j selected iff SHA256('<ns>|audit|<bits>|<seed>|<j>') mod 10 == 0 (about 10%, "
     "consistent across the A1 prefix and A2). All relation certificates are checked regardless."),
    ("OQ-11", "C-6 configuration-model rewire",
     "Pure (loops/multi-edges kept) vs erased vs edge-switching.",
     "Pure configuration model on the observed stub list (root included); the treatment graph is itself "
     "a multigraph."),
    ("OQ-12", "C-6 Erdos-Renyi G(|V|,|E|)",
     "Simple vs multigraph.",
     "Uniform simple graph (no loops, no parallel edges); infeasible if |E| > C(|V|,2), recorded."),
    ("OQ-13", "C-6 planted-dense construction",
     "'cycle rank forced to |V|^{1.5}' does not fix rounding or edge law.",
     "Random spanning tree on the observed vertex count plus ceil(|V|^{1.5}) uniform non-loop edges "
     "(multi-edges allowed); cycle rank exactly ceil(|V|^{1.5}); gate delta_proof(L of the fixture) > 1/4."),
    ("OQ-14", "Known false 'not_exercised'",
     "With few relations, the scrambled system can be consistent with nothing beyond the anchor determined, "
     "so it can neither pass nor fail verification (seen in smoke at 256 attempts).",
     "Recorded per cell as not_exercised, not a defect and not a pass; only passes_verification is a "
     "procedure defect. Reviewer to decide how not_exercised cells count."),
    ("OQ-15", "C-4 Horton at 24-bit",
     "'at 16- and 20-bit only (24-bit ... if memory protection requires)'.",
     "No minimum basis at 24-bit by default (GF(2) cycle rank reported); celltask --horton-24 exists but "
     "the driver never passes it."),
    ("OQ-16", "v1 secondary 'blind_descent_success'",
     "Protocol v2 defines no descent step.",
     "Recorded as null with the reason; no descent implemented."),
    ("OQ-17", "C-4 'charged work / sqrt(q)' unit",
     "Unit unstated; v1 charging_rule also lists sparse LA.",
     "Charged work = group operations of setup + attempts; LA is charged separately in mod-q mults and "
     "inversions (la_ops_charged) and is not converted; field ops (W_field) also reported. Instance "
     "construction Q = kG is uncharged. Rho is reported as walk (+escape) ops / sqrt(q)."),
    ("OQ-18", "LP log recovery fraction",
     "Anchor and denominator unstated.",
     "Anchor l(x(G)) = 1; fraction = verified determined LP classes / LP classes in the relation set."),
    ("OQ-19", "C-6 rho 'if any cost comparison is made'",
     "charged work / sqrt(q) is a C-4 secondary, so a comparison is always made.",
     "Rho baseline (64 targets per fixture) always runs; walk multiplier labels are not in the protocol."),
    ("OQ-20", "C-7 on a non-macOS host / success_criterion 'null controls passing'",
     "C-7 names macOS volumes; 'null controls passing' is not defined in v1 or v2.",
     "Same thresholds with '/' as the system volume. Null results are reported in full; the verdict "
     "follows C-5 only."),
    ("OQ-21", "v4 F-3 when the subcritical rule also fires",
     "The F-3 ruling covers a verdict that would otherwise be supercritical-enriched; it does not say what "
     "happens when the ER clause is undetermined, every other supercritical clause holds, and the "
     "subcritical rule also fires.",
     "Fail closed: the supercritical rule is 'undetermined' and the verdict is inconclusive (never "
     "certified-subcritical), with the reason naming the undetermined cells and that the subcritical rule "
     "also fired. A cell with at least one feasible ER replicate is determined (mean over feasible ones)."),
    ("OQ-22", "v4 F-4 cell-level power confirmation",
     "F-4 is stated per cell; each size x budget cell holds three fixtures.",
     "A size x budget cell has known-positive power confirmation only if all three fixtures' known "
     "positive is 'pass'. Gate-reachable minimum |V| = smallest |V| >= 2 with "
     "log_L(ceil(|V|^1.5)) - 1 > 1/4 (L < 2: unreachable, not_exercised). The planted cycle-rank "
     "construction check stays a procedure defect even when the gate is not reachable."),
    ("OQ-23", "v4 FX-5 decision supersession",
     "'a superseded_by field' does not say whether superseded_by: null counts (3 committed decisions carry "
     "an explicit null).",
     "A non-null, non-empty superseded_by (in coordinator_decision, the document, or execution_admission) "
     "or status superseded/withdrawn refuses; a null superseded_by does not. The driver also refuses a "
     "decision that a later ledger decision lists under 'supersedes'."),
    ("OQ-24", "v4 FX-6 'budgets different from every frozen (A1, A2)'",
     "Exact inequality allows a smoke budget adjacent to a frozen one (e.g. 750 vs 751), which is nearly an "
     "exchangeable replicate.",
     "Refusal is on exact equality with any of the 18 frozen A1/A2 values, as written. The v4 smoke uses "
     "b16-s13 (smallest q) at 64/256 and 400/1500, far from its frozen 199/574."),
    ("OQ-25", "v4 FX-5 snapshot receipt coverage and the dirty-tree rule",
     "Which implementation files must be pinned, and whether smoke output written after the snapshot "
     "counts as a dirty tree.",
     "Every receipt entry under implementation/ must match the working tree (the receipt itself excluded); "
     "every implementation *.py, tests/*.py and trial-plan-v2.json must be pinned; git status of "
     "implementation/ (untracked included, ignored excluded) must be empty. Any file added under "
     "implementation/ after the snapshot (including smoke output) therefore blocks a scientific run until "
     "a new snapshot covers it."),
    ("OQ-26", "v4 run status vocabulary",
     "FX-1 names failed_infrastructure; the status for a stopped procedure defect is not named.",
     "completed_valid (all cells, no defect); invalid with failure_class procedure_defect (a failed "
     "identity or reachable control); failed_infrastructure with failure_class exception | signal | "
     "infrastructure_error | resource_exhaustion; running while in progress."),
]

RULINGS = {
    "OQ-4": "Accepted in v3 (AMD-20260929-988139); v4 F-3 adds: no feasible ER replicate in a cell -> "
            "'undetermined', cannot support supercritical-enriched (inconclusive). Implemented in analysis.py.",
    "OQ-13": "v4 F-4: below the gate-reachable |V| for the fixture's L the known positive is not_exercised "
             "(not a defect, run continues; reported as lacking power confirmation). Implemented in celltask.py "
             "and analysis.py.",
    "OQ-14": "v4 FX-4: recovery fraction reported as 'undetermined' where known_false = not_exercised "
             "(analysis.py table).",
}


def test_summary() -> dict:
    p = HERE / "test-results.txt"
    if not p.exists():
        return {"status": "not run"}
    txt = p.read_text()
    m = re.search(r"(\d+) passed", txt)
    f = re.search(r"(\d+) failed", txt)
    s = re.search(r"(\d+) skipped", txt)
    return {"command": "python3 -m pytest -p no:cacheprovider -q -rs tests", "log": "test-results.txt",
            "passed": int(m.group(1)) if m else 0, "failed": int(f.group(1)) if f else 0,
            "skipped": int(s.group(1)) if s else 0, "last_line": txt.strip().splitlines()[-1]}


def main():
    files = sorted(p for p in HERE.rglob("*") if p.is_file() and "__pycache__" not in p.parts
                   and p != REPORT and p.name != "repair_report_v4.yaml")
    smoke = json.loads((HERE / "smoke" / "v4" / "smoke_summary.json").read_text())
    rep = {"implementation_report": {
        "task_id": "TASK-20260929-b72e82", "prior_task_ids": ["TASK-20260929-7e6ea7"],
        "experiment_id": "EXP-RELN-c5a377", "protocol_version": driver.PROTOCOL_VERSION,
        "protocol_files": {k: v for k, v in driver.protocol_binding(driver.REPO_ROOT_DEFAULT)["records"].items()},
        "repair_report": "repair_report_v4.yaml",
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "scientific_runs": 0, "run_directories_created": [],
        "execution_admitted": False,
        "admission_note": "DEC-20260929-ee5b8a approves implementation only and DEC-20260929-7a62cc keeps "
                          "currently_admitted false; the driver refuses both (tested). A scientific run also "
                          "needs --snapshot-receipt of a new snapshot (FX-5).",
        "trial_plan": {"path": "trial-plan-v2.json",
                       "sha256": fixtures.sha256_file(HERE / "trial-plan-v2.json"),
                       "cells": 18, "fixtures": 9, "budgets": ["A1", "A2"]},
        "fixture_regeneration": {"byte_identical": True, "reln_entries_identical": True,
                                 "reproduced_sha256": fixtures.FROZEN_JSON_SHA256,
                                 "test": "tests/test_fixtures.py::test_fixture_regeneration_byte_identical"},
        "tests": test_summary(),
        "smoke_v2_historical": {
            "summary_path": "smoke/smoke_summary.json",
            "summary_sha256": fixtures.sha256_file(HERE / "smoke" / "smoke_summary.json"),
            "note": "immutable protocol-v2 smoke; per AMD-20260929-cc7226 F-2 the smoke/dry/DRYRUN-controls "
                    "delta, ER-null and subcritical-rule readings are excluded from every analysis and were not "
                    "opened in this repair"},
        "smoke": {"summary_path": "smoke/v4/smoke_summary.json",
                  "summary_sha256": fixtures.sha256_file(HERE / "smoke" / "v4" / "smoke_summary.json"),
                  "fixture": smoke["fixture"], "namespace": "smoke|EXP-RELN-c5a377/v2",
                  "frozen_budgets_avoided": True,
                  "runs": {rid: {"driver_exit_code": r["driver_exit_code"],
                                 "manifest_status": r["manifest_status"],
                                 "run_record": {k: r["run_record"][k] for k in
                                                ("top_level_run_block", "required_keys_present",
                                                 "protocol_version", "files_present",
                                                 "environment_sage_version", "environment_dependencies")},
                                 "C7_admitted_by_precondition": r["C7_readings"]["admitted_by_precondition"],
                                 "C7_reasons": r["C7_readings"]["reasons"],
                                 "cells": [{"fixture_id": c["fixture_id"],
                                            "procedure_defects": c["procedure_defects"],
                                            "peak_rss_bytes_wait4": c["peak_rss_bytes_wait4"],
                                            "rho": c["rho"],
                                            "budgets": [{"budget": b["budget"], "attempts": b["attempts"],
                                                         "identities": b["identities"],
                                                         "controls": b["controls"]}
                                                        for b in c["budgets"]]}
                                           for c in r["cells"]]}
                           for rid, r in smoke["runs"].items()},
                  "verdict_reported": False},
        "files": [{"path": str(p.relative_to(HERE)), "sha256": fixtures.sha256_file(p),
                   "bytes": p.stat().st_size} for p in files],
        "open_questions": [{"id": i, "topic": t, "ambiguity": a, "literal_reading_implemented": r,
                            **({"protocol_ruling": RULINGS[i]} if i in RULINGS else {})}
                           for i, t, a, r in OPEN_QUESTIONS],
        "inference": {"requested_policy": "executor-implementation", "fallback_used": True,
                      "fallback_reason": "Cursor runtime: subagent runs on the inherited session model",
                      "resolved_model_id": "unverified"}}}
    REPORT.write_text(yaml.safe_dump(rep, sort_keys=False, width=100))
    print(REPORT, fixtures.sha256_file(REPORT))


if __name__ == "__main__":
    main()
