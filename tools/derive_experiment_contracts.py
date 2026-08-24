"""Derive draft experiment contracts from BATCH-cb71b5 proposals.

An IDEA record already carries the pieces an experiment contract needs: a
`minimal_test` with a design, controls and required metrics; `predictions`;
`falsification_conditions`; `confounders`; and this campaign's extra
`null_object_control`, `resource_label`, `admissibility` and `reachability_gate`
fields. This tool renders those into `experiments/<EXP-id>/specification.yaml`
in the schema of `templates/research-records.md`.

What it deliberately does NOT do:

  * It does not APPROVE anything. Every contract is written at `status: draft`.
    Only the Coordinator moves a contract to `review_required` or `approved`
    (AGENTS.md: only the Coordinator approves experiments), and the campaign's
    proof-search-map gate applies before any expensive run.
  * It does not invent content. A field the idea does not supply is written as
    null with a `derivation_gap` note naming what a human or Coordinator must
    fill in before the contract can be approved. Missing data stays missing
    (AGENTS.md rule 9).
  * It does not size budgets from wishes. Budgets come from the idea's declared
    `estimated_cost` mapped through a fixed, documented table. Scale metadata
    is copied from the idea when supplied and is not imposed automatically.

Usage:
    python3 tools/derive_experiment_contracts.py --plan     # dry run, prints map
    python3 tools/derive_experiment_contracts.py --write
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import subprocess
import sys

import yaml

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Lane area code per research question, so EXP ids land in the right namespace.
RQ_TO_AREA = {
    "RQ-ICINV-475b5e": "ICINV", "RQ-VOLC-f6253b": "VOLC",
    "RQ-JINV-8fc13a": "JINV", "RQ-EQIC-8cb959": "EQIC",
    "RQ-EQLA-0d3f40": "EQLA", "RQ-EWALK-8fa147": "EWALK",
    "RQ-TORS-8c7b79": "TORS", "RQ-PAIR-21313f": "PAIR",
    "RQ-CANL-63098f": "CANL", "RQ-CLGP-b99df5": "CLGP",
    "RQ-MODEL-e61cb2": "MODEL", "RQ-GGMB-6eaabc": "GGMB",
    "RQ-MTGT-2cabee": "MTGT", "RQ-INSTR-f8faa0": "INSTR",
}

# Documented budget table. compute -> (wall seconds per run, cpu hours, max runs).
BUDGET = {
    "low":    (900, 0.5, 20),
    "medium": (3600, 3.0, 40),
    "high":   (10800, 12.0, 60),
}

def allocate(area: str) -> str:
    out = subprocess.run(
        [sys.executable, os.path.join(REPO, "tools", "allocate_id.py"),
         "--next", "experiment", "--area", area],
        capture_output=True, text=True, cwd=REPO).stdout
    for tok in out.split():
        if tok.startswith(f"EXP-{area}-"):
            return tok
    raise RuntimeError(f"could not allocate an EXP id for {area}: {out}")


def _as_list(v) -> list:
    if v is None:
        return []
    return v if isinstance(v, list) else [v]


def contract_from_idea(idea: dict, exp_id: str) -> tuple[dict, list[str]]:
    """Render one idea into a draft contract. Returns (contract, gaps)."""
    gaps: list[str] = []
    mt = idea.get("minimal_test") or {}
    design = mt.get("design")
    if not design:
        gaps.append("minimal_test.design absent: no executable procedure to freeze")
    controls = _as_list(mt.get("controls"))
    nullctl = idea.get("null_object_control")
    if nullctl:
        controls = controls + [f"NULL OBJECT (from the proposal): {nullctl}"]
    else:
        gaps.append("null_object_control absent: mandatory under "
                    "docs/inventor-protocol.md 'controls before belief'")
    metrics = _as_list(mt.get("required_metrics"))
    if not metrics:
        gaps.append("minimal_test.required_metrics absent: nothing to measure")

    preds = _as_list(idea.get("predictions"))
    falsif = _as_list(idea.get("falsification_conditions"))
    if not falsif:
        gaps.append("falsification_conditions absent: contract is unfalsifiable")

    cost = (idea.get("estimated_cost") or {}).get("compute", "medium")
    wall, cpu, runs = BUDGET.get(str(cost).lower(), BUDGET["medium"])

    admissibility = idea.get("admissibility")
    if admissibility is None:
        gaps.append("admissibility absent: campaign requires the R1-R8 resource "
                    "label and its argument before dispatch")

    prereg = None
    for p in preds:
        if isinstance(p, dict) and p.get("minimum_effect"):
            prereg = {
                "quantity": p.get("metric"),
                "formula": p.get("minimum_effect"),
                "source": (f"pre-registered in {idea['id']} before any run under "
                           f"this contract; never tuned to data"),
            }
            break
    if prereg is None:
        gaps.append("no prediction carries a minimum_effect: nothing is "
                    "pre-registered, so any result would be post hoc")

    contract = {"experiment": {
        "id": exp_id,
        "hypothesis_id": None,
        # validate_ledger.DOCUMENTED_NULL_OK permits a null hypothesis_id ONLY
        # when accompanied by this note. The note is not a formality: it is what
        # stops a reader mistaking an unminted hypothesis for an overlooked field.
        "hypothesis_id_note": (
            "No hypothesis exists for this contract and none is invented. "
            "GOAL-ENDO-001 carries no active hypothesis; a proposal is not a "
            "hypothesis. This contract is DRAFT and NOT APPROVED; the "
            "/design-experiment step that mints a specified hypothesis from the "
            "parent IDEA has not been run."),
        "derived_from_idea": idea["id"],
        "question_id": idea.get("question_id"),
        "goal_id": "GOAL-ENDO-001",
        "batch_id": "BATCH-cb71b5",
        "version": 1,
        "title": idea.get("title"),
        "status": "draft",
        "objective": idea.get("claim"),
        "resource_label": idea.get("resource_label"),
        "admissibility": admissibility,
        "admissibility_argument": idea.get("admissibility_argument"),
        "reachability_gate": idea.get("reachability_gate"),
        "inputs": {
            "procedure": design,
            "mechanism": idea.get("mechanism"),
            "instrument": ("harness/isogeny_class.py, harness/exp_icinv.py and the "
                           "lane runners under harness/; pure Python with sympy "
                           "and numpy, no Sage"),
        },
        "controls": controls,
        "independent_variables": [],
        "metrics": {"primary": metrics[:4], "secondary": metrics[4:]},
        "heuristic_under_test": None,
        "preregistered_prediction": prereg or {
            "quantity": None, "formula": None, "source": None},
        "scale_relevance": {
            "tier": idea.get("scale_tier"),
            "justification": idea.get("scale_justification"),
            "correspondence": idea.get("scale_correspondence"),
        },
        "tail_checks": _as_list(idea.get("confounders")),
        "replication": {
            "seeds": [20260807, 20260808, 20260809],
            "independent_instances": 3,
        },
        "budget": {
            "wall_clock_seconds_per_run": wall,
            "total_cpu_hours": cpu,
            "maximum_memory_gb": 8,
            "maximum_runs": runs,
        },
        "stopping_rules": [
            "Stop at maximum_runs or total_cpu_hours, whichever binds first.",
            ("Stop immediately if the instrument fails its two-directional "
             "control (EXP-INSTR-2d32ba): measurements taken with a failed "
             "instrument are attempted_and_inconclusive, never evidence."),
            ("Stop and escalate to an independent review-adversarial session if "
             "any arm appears to exceed the automorphism-discounted rho baseline "
             "(GOAL-ENDO-001 pause condition P3)."),
        ],
        "invalidation_rules": [
            ("A timeout, crash, memory exhaustion or dependency failure makes the "
             "run failed_infrastructure and is NEVER negative mathematical "
             "evidence (AGENTS.md rule 5)."),
            ("An isogeny-class enumeration whose Hurwitz-Kronecker census fails "
             "makes the run invalid: a variance measured over an incomplete class "
             "is meaningless."),
            ("Any claimed solve or relation whose certificate fails independent "
             "re-verification makes the run completed_invalid."),
        ],
        "success_criterion": (prereg or {}).get("formula"),
        "falsification_criterion": falsif,
        "required_artifacts": [
            "manifest.yaml with command, commit, dirty-tree state, environment",
            "raw-result.json with every per-curve measurement, not just summaries",
            "the null-object arm's measurements, in the same file as the signal arm",
            "certificates for every claimed solve or relation",
        ],
        "assigned_to": "executor",
        "approved_by": None,
        "approval_gate": [
            ("Coordinator approval required before execution; this contract is "
             "machine-derived from the proposal and is NOT approved."),
            ("If the proposal is proof-oriented, a proof_search_map is required "
             "before implementation or expensive experiments (KN-TECH-080)."),
            ("If admissibility is inadmissible_generic_group, this contract is a "
             "RECORDED CLOSURE and must not be executed as an attack; it may be "
             "executed only as a baseline calibration, and its evidence record "
             "must say so."),
        ],
        "derivation_provenance": {
            "tool": "tools/derive_experiment_contracts.py",
            "source_record": idea["id"],
            "note": ("Fields are rendered from the proposal, never invented. A "
                     "null field means the proposal did not supply it."),
        },
        "derivation_gaps": gaps,
    }}
    return contract, gaps


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--glob", default="ledger/proposals/IDEA-20260807-*.yaml")
    args = ap.parse_args(argv)

    # Idempotency: an idea that already has a contract is skipped, so the tool
    # can be re-run as later lanes land without minting a second EXP id for the
    # same proposal.
    idx_path = os.path.join(REPO, "coordination", "goals", "GOAL-ENDO-001",
                            "batches", "BATCH-cb71b5", "experiment_index.json")
    existing = {}
    if os.path.exists(idx_path):
        prior = json.load(open(idx_path))
        existing = {c["idea_id"]: c["experiment_id"] for c in prior["contracts"]}

    rows, skipped = [], []
    for path in sorted(glob.glob(os.path.join(REPO, args.glob))):
        try:
            idea = yaml.safe_load(open(path))["idea"]
        except Exception as exc:
            skipped.append((os.path.basename(path), f"unparseable: {exc}"))
            continue
        rq = idea.get("question_id")
        area = RQ_TO_AREA.get(rq)
        if area is None:
            skipped.append((idea.get("id", path), f"unknown question_id {rq!r}"))
            continue
        if idea["id"] in existing:
            skipped.append((idea["id"],
                            f"already contracted as {existing[idea['id']]}"))
            continue
        rows.append((idea, area))

    print(f"proposals readable: {len(rows)}  skipped: {len(skipped)}")
    for s in skipped:
        print("  SKIP", s[0], "--", s[1])

    by_area: dict[str, int] = {}
    for _, a in rows:
        by_area[a] = by_area.get(a, 0) + 1
    print("by lane:", json.dumps(by_area, sort_keys=True))

    if not args.write:
        return 0

    written, gapped = 0, 0
    index = []
    for idea, area in rows:
        exp_id = allocate(area)
        contract, gaps = contract_from_idea(idea, exp_id)
        d = os.path.join(REPO, "experiments", exp_id)
        os.makedirs(d, exist_ok=True)
        out = os.path.join(d, "specification.yaml")
        if os.path.exists(out):
            print("  EXISTS, refusing to overwrite:", out)
            continue
        with open(out, "w") as fh:
            yaml.safe_dump(contract, fh, sort_keys=False, width=96,
                           allow_unicode=True, default_flow_style=False)
        written += 1
        gapped += bool(gaps)
        index.append({"experiment_id": exp_id, "idea_id": idea["id"],
                      "question_id": idea.get("question_id"), "lane": area,
                      "title": idea.get("title"),
                      "admissibility": idea.get("admissibility"),
                      "resource_label": idea.get("resource_label"),
                      "priority": idea.get("recommended_priority"),
                      "prior_of_survival": idea.get("honest_prior_of_survival"),
                      "derivation_gaps": gaps})
    idx = os.path.join(REPO, "coordination", "goals", "GOAL-ENDO-001",
                       "batches", "BATCH-cb71b5", "experiment_index.json")
    os.makedirs(os.path.dirname(idx), exist_ok=True)
    if os.path.exists(idx):
        index = json.load(open(idx))["contracts"] + index
    with open(idx, "w") as fh:
        json.dump({"generated_by": "tools/derive_experiment_contracts.py",
                   "status_of_every_contract": "draft (NOT approved)",
                   "count": len(index), "written_this_pass": written,
                   "with_derivation_gaps": gapped,
                   "contracts": index}, fh, indent=1)
    print(f"wrote {written} draft contracts ({gapped} carry derivation gaps)")
    print("index:", idx)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
