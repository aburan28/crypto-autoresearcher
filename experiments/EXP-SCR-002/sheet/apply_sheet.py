#!/usr/bin/env python3
"""EXP-SCR-002 mechanical repaired admission-sheet adjudicator and run harness.

Applies the frozen repaired SOURCE-LOCATOR-OPEN admission sheet (requirements
R1-R7) from experiments/EXP-SCR-002/specification.yaml to the 7 frozen corpus
audit items (I1-I7), reading all corpus content as git blobs at the pinned
commit (git cat-file), never the working tree.

Subcommands:
  run-a     Freeze corpus manifest + calibration fixtures + threshold
            recomputation control (RUN-SCR-002-A).
  run-b     Adjudicate R1-R4 over all 7 items with rejection bases and the
            dedup control (RUN-SCR-002-B).
  run-c     Adjudicate R5-R7 over all 7 items, determinism replay, emit the
            requirement matrix and admission decision (RUN-SCR-002-C).
  harness   Execute one payload run with timeout, resource measurement, and
            immutable run-record artifacts.
  validate  Lifecycle step-7 checks over the three run records.

stdlib + PyYAML only. No randomness: seeds = [] (deterministic audit).
"""

import argparse
import hashlib
import json
import os
import platform
import resource
import subprocess
import sys
import time
from datetime import datetime, timezone
from fractions import Fraction

import yaml

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
for _ in range(3):  # sheet/ -> EXP-SCR-002/ -> experiments/ -> repo root
    REPO_ROOT = os.path.dirname(REPO_ROOT)
EXP_DIR = os.path.join(REPO_ROOT, "experiments", "EXP-SCR-002")
SPEC_PATH = os.path.join(EXP_DIR, "specification.yaml")
TASK_ID = "TASK-20260727-007"

TERMINAL_STATUSES = (
    "completed_valid",
    "completed_invalid",
    "failed_infrastructure",
    "failed_implementation",
    "resource_exhaustion",
    "cancelled_by_budget",
)

ALL_ITEMS = ["I1", "I2", "I3", "I4", "I5", "I6", "I7"]

REQUIREMENT_ORDER = ["R1", "R2", "R3", "R4", "R5", "R6", "R7"]
REQUIREMENT_IDS = {
    "R1": "requirement_1_explicit_semantically_distinct_operation",
    "R2": "requirement_2_O1_GGM_simulator_exclusion",
    "R3": "requirement_3_subset_stable_occurrence_replay",
    "R4": "requirement_4_rank_yield_and_rejected_batch_charge",
    "R5": "requirement_5_restricted_replay_calls_and_live_state",
    "R6": "requirement_6_fresh_scalar_blind_query",
    "R7": "requirement_7_complete_threshold_and_baseline",
}

# Full charged-cost-model term set (frozen sheet R7 / charged_cost_model.symbols).
COST_TERMS = [
    "a", "a_m", "q_rel", "q_rel_replay", "q_rel_m", "o_rel", "r", "delta_rel",
    "eta_rank", "ell", "ell_m", "q_t", "q_t_replay", "o_t", "delta_t", "u_t",
    "m_replay", "m_output", "b_w", "b_m",
]

BATCH6_REPORT = (
    "coordination/goals/GOAL-CRYPTO-001/batches/BATCH-006/tasks/"
    "TASK-20260723-601/admission_report.yaml"
)
BATCH6_ADMISSION_MD = (
    "coordination/goals/GOAL-CRYPTO-001/batches/BATCH-006/tasks/"
    "TASK-20260723-601/source_locator_admission.md"
)
BATCH6_REVIEW_MD = (
    "coordination/goals/GOAL-CRYPTO-001/batches/BATCH-006/tasks/"
    "TASK-20260723-603/admission_review.md"
)
BATCH5_CANDIDATE = (
    "coordination/goals/GOAL-CRYPTO-001/batches/BATCH-005/tasks/"
    "TASK-20260723-501/candidate_report.yaml"
)
BATCH2_REPORT = (
    "coordination/goals/GOAL-CRYPTO-001/batches/BATCH-002/tasks/"
    "TASK-20260723-201/admission_report.yaml"
)
EV_CRYPTO_002 = "ledger/evidence/EV-CRYPTO-002.yaml"
P1553_GATE = "ideas/artifacts/ECDLP-IDEA-012/p1553_six_list_incidence_model_gate.md"

# Frozen named rejection bases and the pinned BATCH-006 dispositions they must
# match (CTRL-DEDUP-PRIOR-NEGATIVES). I7 is the named explicit control and is
# not on the excluded_nonconstructors list.
EXPECTED_DISPOSITION = {
    "I1": "rejected_as_hidden_input",
    "I2": "rejected_as_failed_or_renamed_IDEA_20260723_001_interface",
    "I3": "rejected_as_free_oracle",
    "I4": "rejected_as_target_dependent_leakage",
    "I5": "exact_predicate_for_supplied_sources_not_a_locator",
    "I6": "explicit_generic_baseline_not_semantically_distinct_and_costs_B3",
    "I7": None,
}

EXCLUDED_NAME = {
    "I1": "supplied_residue_source_scalar_or_B3_provenance",
    "I2": "compact_z_R_resultant_common_factor_or_source_dictionary",
    "I3": "unnamed_zero_minor_or_hyperplane_signature_locator",
    "I4": "target_fitted_coefficients_or_hidden_advice",
    "I5": "determinant_pair_wedge_or_Abel_endpoint_zero_test",
    "I6": "direct_source_labelled_3_plus_3_separator",
}

ITEM_OWNERS = {
    "I1": [
        BATCH6_REPORT + " (excluded_nonconstructors: rejected_as_hidden_input)",
        "EV-CRYPTO-006",
    ],
    "I2": [
        "EV-CRYPTO-002 (z_R closure: NO_ADMISSIBLE_CONSTRUCTION)",
        BATCH2_REPORT + " (verdict NO_ADMISSIBLE_CONSTRUCTION)",
        "OBL-ZR-COMPACT-CONSTRUCTOR-001 (BATCH-005 candidate_report exact_exclusions)",
    ],
    "I3": [
        "IDEA-20260723-002 (BATCH-005 candidate_report exact_exclusions)",
        BATCH6_REPORT + " (excluded_nonconstructors: rejected_as_free_oracle)",
    ],
    "I4": [
        BATCH6_REPORT + " (excluded_nonconstructors: rejected_as_target_dependent_leakage)",
        BATCH6_ADMISSION_MD,
    ],
    "I5": [
        "ideas/reviews/P1552_MECHANISM_FRONTIER_20260718.md",
        P1553_GATE,
        BATCH6_REPORT + " (excluded_nonconstructors: exact_predicate_for_supplied_sources_not_a_locator)",
    ],
    "I6": [
        BATCH6_REPORT + " (excluded_nonconstructors + baseline_comparison.closest_specialized_control)",
    ],
    "I7": [
        BATCH6_REPORT + " (charged_cost_model.current_explicit_control; named explicit control)",
        "RT-20260723-603 (threshold_recomputation control)",
        BATCH6_REVIEW_MD,
    ],
}

# Per-item grounded cell reasons (static text justified by the grounding
# checks; each check proves the cited pinned content exists).
R1_FAIL_REASON = {
    "I1": "A supplied residue, source, scalar, source dictionary, or B^3 provenance "
          "is a hidden input assuming the missing inverse, not a new public typed "
          "operation (BATCH-006 excluded_nonconstructors: rejected_as_hidden_input).",
    "I2": "The compact z_R/resultant/common-factor/source-dictionary route is the "
          "renamed, failed IDEA-20260723-001 interface (EV-CRYPTO-002 "
          "NO_ADMISSIBLE_CONSTRUCTION; OBL-ZR-COMPACT-CONSTRUCTOR-001), not a new "
          "semantically distinct operation.",
    "I3": "An unnamed zero-minor or hyperplane-signature locator is a free oracle "
          "(renamed IDEA-20260723-002 excluded route), not an explicit typed "
          "operation.",
    "I4": "Target-fitted coefficients or hidden advice leak the target into "
          "coefficient provenance; not a public target-independent operation.",
    "I5": "The determinant/pair-wedge/Abel-endpoint zero test is an exact predicate "
          "over supplied tuples/endpoints, not a source locator operation.",
    "I6": "Direct source-labelled 3+3 matching is the known generic control; it is "
          "not semantically distinct and costs B^3.",
    "I7": "The named explicit control is explicit and source-faithful but not "
          "semantically new (pinned assessment); it is the known generic baseline "
          "operation.",
}

R2_FAIL_REASON = {
    "default": "No exact target-dependent transcript certified non-reproducible by "
               "an O(1)-overhead generic-group simulator is supplied.",
    "I5": "The supplied-tuple determinant/wedge zero bit is equivalent to a "
          "group-sum equality and is reproduced with O(1) generic group operations "
          "(pinned R2 reason); merely reading coordinates proves no separation.",
    "I6": "The direct source-labelled match is itself generic (pinned R2 reason).",
    "I7": "The direct source-labelled match is itself generic (pinned R2 reason).",
}

R3_FAIL_REASON = {
    "default": "No exact yes/no restricted-existence call over occurrence-labelled "
               "rectangular subsets is instantiated; the 1+2*s*D_k depth-first "
               "schedule remains a conditional accounting obligation.",
    "I1": "Supplying a residue, source, scalar, source dictionary, or B^3 "
          "provenance assumes the missing inverse and is rejected (pinned R3 reason).",
}

R4_FAIL_REASON = "No deterministic rank-Theta(B) guarantee and no proved rank-yield " \
                 "tail over the frozen deck and target distribution: r=0, eta_rank " \
                 "unknown (not zero); expected Theta(B) rows are not a rank theorem."

R5_FAIL_REASON = "No subset-stable operation supplies the restricted calls to " \
                 "enumerate and charge; rebuilds, misses, traversal frontiers, and " \
                 "live state cannot be costed for a missing operation."

R6_FAIL_REASON = {
    "default": "No admitted operation supplies the fresh masked-target source "
               "inverse inside B^(5/4+o(1)) = N^(0.25+o(1)).",
    "I7": "The named control's direct fresh-target descent costs "
          "B^(3+o(1)) = N^(0.60+o(1)) > N^0.25 (recomputed).",
}

R7_FAIL_REASON = {
    "default": "No complete cost ledger is supplied; unknown terms are admission "
               "failures, not zeros.",
    "I7": "Certifiable work exponent >= 0.60 and materialized memory exponent 0.60 "
          "exceed the lambda,mu <= 0.45 gates (recomputed); the remaining "
          "unassigned terms are admission failures, not zeros.",
}

PLANNED_RUNS = {
    "RUN-SCR-002-A": "run-a",
    "RUN-SCR-002-B": "run-b",
    "RUN-SCR-002-C": "run-c",
}

STAGE_BUDGET_SECONDS = {
    "RUN-SCR-002-A": 900,
    "RUN-SCR-002-B": 1500,
    "RUN-SCR-002-C": 1500,
}

WALL_TIMEOUT_SECONDS = 1800  # frozen per-run budget (budget.wall_clock_seconds_per_run)
MEM_LIMIT_BYTES = 4 * 1024**3  # frozen 4 GB cap

BETA = Fraction(1, 5)  # frozen factor scale B = N^(1/5)


# --------------------------------------------------------------------------
# spec / corpus access
# --------------------------------------------------------------------------

def load_spec():
    with open(SPEC_PATH, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)["experiment"]


def pinned_commit(spec):
    return spec["inputs"]["corpus_snapshot"]["pinned_commit"]


def git_blob_bytes(commit, path):
    out = subprocess.run(
        ["git", "cat-file", "blob", "%s:%s" % (commit, path)],
        capture_output=True,
        cwd=REPO_ROOT,
    )
    if out.returncode != 0:
        return None
    return out.stdout


def git_blob_sha1_of(content):
    header = b"blob %d\x00" % len(content)
    return hashlib.sha1(header + content).hexdigest()


def sha256_hex(content):
    return hashlib.sha256(content).hexdigest()


def canonical_json(obj):
    return json.dumps(obj, indent=2, sort_keys=True) + "\n"


def write_json_if_absent_or_identical(path, obj):
    data = canonical_json(obj)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as fh:
            existing = fh.read()
        if existing != data:
            raise RuntimeError("immutable artifact content conflict: %s" % path)
        return False
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(data)
    return True


def verify_corpus(spec):
    """CTRL-CORPUS-INTEGRITY: read every pinned blob, compare git blob SHA-1."""
    commit = pinned_commit(spec)
    entries = []
    missing, mismatches = [], []
    for entry in spec["inputs"]["corpus_snapshot"]["hash_manifest"]:
        path = entry["path"]
        want = entry["git_blob_sha1"]
        content = git_blob_bytes(commit, path)
        if content is None:
            missing.append(path)
            entries.append(
                {
                    "path": path,
                    "expected_git_blob_sha1": want,
                    "status": "missing",
                }
            )
            continue
        got = git_blob_sha1_of(content)
        rec = {
            "path": path,
            "expected_git_blob_sha1": want,
            "actual_git_blob_sha1": got,
            "sha256": sha256_hex(content),
            "bytes": len(content),
            "status": "pass" if got == want else "mismatch",
        }
        if got != want:
            mismatches.append(path)
        entries.append(rec)
    return {
        "control": "CTRL-CORPUS-INTEGRITY",
        "pinned_commit": commit,
        "verification_rule": spec["inputs"]["corpus_snapshot"]["verification_rule"],
        "entry_count": len(entries),
        "verified": sum(1 for e in entries if e["status"] == "pass"),
        "missing": missing,
        "mismatches": mismatches,
        "pass": not missing and not mismatches,
        "entries": entries,
    }


class Corpus:
    """Cached pinned-commit corpus content (git blobs only)."""

    def __init__(self, spec):
        self.commit = pinned_commit(spec)
        self._text = {}

    def text(self, path):
        if path not in self._text:
            content = git_blob_bytes(self.commit, path)
            if content is None:
                raise KeyError("missing corpus path: %s" % path)
            self._text[path] = content.decode("utf-8")
        return self._text[path]

    def yaml(self, path):
        return yaml.safe_load(self.text(path))


def excerpt(text, needle, width=200):
    idx = text.find(needle)
    if idx < 0:
        return None
    start = max(0, idx - 20)
    snippet = text[start : idx + len(needle) + (width - len(needle) - 20)]
    return " ".join(snippet.split())


def _check(check_id, description, ok, evidence=None):
    return {
        "check_id": check_id,
        "description": description,
        "result": "pass" if ok else "fail",
        "evidence": evidence or {},
    }


# --------------------------------------------------------------------------
# frozen repaired admission sheet (R1-R7)
# --------------------------------------------------------------------------

def verdict_from_cells(cells):
    """cells: {Rk: {status}}. Returns (verdict, first_failed_key)."""
    first_failed = None
    for key in REQUIREMENT_ORDER:
        if cells[key]["status"] != "pass":
            first_failed = key
            break
    return ("REJECT", first_failed) if first_failed else ("ADMIT", None)


def apply_sheet(facts):
    """Pure function of the fact vector {Rk: bool}. Returns per-requirement
    cells with fail-at-first-failure / fail_independently statuses."""
    cells = {}
    first_failed = None
    for key in REQUIREMENT_ORDER:
        if facts.get(key):
            cells[key] = {"requirement_id": REQUIREMENT_IDS[key], "status": "pass"}
        else:
            status = "fail" if first_failed is None else "fail_independently"
            if first_failed is None:
                first_failed = key
            cells[key] = {"requirement_id": REQUIREMENT_IDS[key], "status": status}
    verdict, _ = verdict_from_cells(cells)
    return verdict, first_failed, cells


def evaluate_r7(terms, deterministic_rank_guarantee):
    """Frozen R7 derived-term arithmetic over Fraction-valued terms.

    terms: dict over COST_TERMS with Fraction or None values.
    Returns (pass, detail). Unknown terms are failures, never zeros.
    """
    unassigned = [k for k in COST_TERMS if terms.get(k) is None]
    detail = {"unassigned_terms": unassigned}
    if unassigned:
        detail["failure"] = "unknown terms are admission failures, not zeros"
        return False, detail
    t = terms
    c_rel = max(t["q_rel"], t["q_rel_replay"] + t["o_rel"], t["o_rel"])
    l_rel = max(Fraction(0), BETA - t["r"]) + t["delta_rel"] + t["eta_rank"] + c_rel
    tau = t["delta_t"] + t["u_t"] + max(t["q_t"], t["q_t_replay"] + t["o_t"], t["o_t"])
    lam = max(t["a"], l_rel, t["ell"], tau, BETA, t["b_w"])
    mu = max(t["a_m"], t["q_rel_m"], BETA, t["ell_m"], t["m_replay"], t["m_output"], t["b_m"])
    derived = {
        "c_rel": str(c_rel), "L_rel": str(l_rel), "tau": str(tau),
        "lambda": str(lam), "mu": str(mu),
        "c_rel_float": float(c_rel), "L_rel_float": float(l_rel),
        "tau_float": float(tau), "lambda_float": float(lam), "mu_float": float(mu),
    }
    failures = []
    if not (Fraction(0) <= t["r"] <= t["o_rel"]):
        failures.append("constraint 0 <= r <= o_rel violated")
    if t["eta_rank"] == 0 and not deterministic_rank_guarantee:
        failures.append("eta_rank = 0 without a deterministic rank guarantee")
    if tau > Fraction(1, 4):
        failures.append("tau > 0.25 fresh-query violation")
    gate = Fraction(9, 20)  # 0.45
    interval_upper = Fraction(1, 2)  # 0.50 rho baseline; no admissible interval
    interval_flags = []
    for name, val in (("lambda", lam), ("mu", mu)):
        if val > gate:
            failures.append("%s > 0.45" % name)
            if val <= interval_upper:
                interval_flags.append(
                    "%s = %s in (0.45, 0.50]: fails R7 explicitly (no "
                    "intermediate admissible interval)" % (name, val)
                )
    detail.update(
        {
            "derived": derived,
            "failures": failures,
            "interval_(0.45,0.50]_flags": interval_flags,
        }
    )
    return not failures, detail


def threshold_recomputation(spec, corpus):
    """CTRL-THRESHOLD-RECOMPUTATION: symbolic exponent arithmetic for the
    frozen regime and the named explicit control (I7)."""
    identities = {
        "B^(9/4)": (Fraction(9, 4), Fraction(9, 20), "0.45"),
        "B^(5/2)": (Fraction(5, 2), Fraction(1, 2), "0.50"),
        "B^3": (Fraction(3, 1), Fraction(3, 5), "0.60"),
        "B^(5/4)": (Fraction(5, 4), Fraction(1, 4), "0.25"),
    }
    recomputed = {}
    identities_ok = True
    for name, (k, want, dec) in identities.items():
        got = k * BETA
        ok = got == want
        identities_ok &= ok
        recomputed[name] = {
            "exponent_in_N": str(got),
            "decimal": float(got),
            "frozen_sheet_value": dec,
            "match": ok,
        }

    report = corpus.yaml(BATCH6_REPORT)
    derivation_text = "\n".join(report["epistemic_separation"]["derivation"])
    pinned_identities_ok = all(
        s in derivation_text
        for s in ("B^(9/4)=N^0.45", "B^(5/2)=N^0.50", "B^3=N^0.60", "B^(5/4)=N^0.25")
    )

    ctrl = report["charged_cost_model"]["current_explicit_control"]
    pair = ctrl["target_independent_pair_state"]["N_exponents"]
    campaign = ctrl["complete_relation_campaign"]["N_exponents"]
    fresh = ctrl["complete_fresh_masked_target_control"]["N_exponents"]
    sparse = ctrl["optimistic_sparse_factor_log_solve"]["N_exponents"]
    aggregate = ctrl["aggregate"]
    extracted_ok = (
        [float(Fraction(2, 5))] * 2 == [float(x) for x in pair]
        and [float(Fraction(3, 5))] * 2 == [float(x) for x in campaign]
        and [float(Fraction(3, 5)), float(Fraction(2, 5))] == [float(x) for x in fresh]
        and [float(Fraction(2, 5)), float(Fraction(1, 5))] == [float(x) for x in sparse]
        and float(Fraction(3, 5)) == float(aggregate["certifiable_total_work_lower_exponent"])
        and float(Fraction(3, 5)) == float(aggregate["direct_materialized_memory_exponent"])
    )

    # I7 aggregates, symbolic (Fraction): lambda >= max(a, campaign, ell, tau, beta).
    a = Fraction(2, 5)       # target-independent pair state work B^2
    a_m = Fraction(2, 5)     # pair state memory B^2
    campaign_work = Fraction(3, 5)   # complete relation campaign B^3
    campaign_mem = Fraction(3, 5)    # materialized campaign memory B^3
    tau = Fraction(3, 5)     # complete fresh masked target B^3
    ell = Fraction(2, 5)     # optimistic sparse factor-log solve B^2 (conditioned)
    ell_m = Fraction(1, 5)   # sparse row state B^1
    lam = max(a, campaign_work, ell, tau, BETA)
    mu = max(a_m, campaign_mem, BETA, ell_m)
    gate = Fraction(9, 20)
    i7 = {
        "named_control": report["baseline_comparison"]["closest_specialized_control"]["name"],
        "assigned_stage_exponents": {
            "a": str(a), "a_m": str(a_m), "ell": str(ell), "ell_m": str(ell_m),
            "r": "0", "campaign_work": str(campaign_work),
            "campaign_memory": str(campaign_mem), "tau": str(tau),
        },
        "lambda_certifiable_at_least": str(lam),
        "lambda_float": float(lam),
        "mu_materialized": str(mu),
        "mu_float": float(mu),
        "tau": str(tau),
        "tau_float": float(tau),
        "fails_R6_fresh_query": tau > Fraction(1, 4),
        "fails_R7_lambda": lam > gate,
        "fails_R7_mu": mu > gate,
        "interval_(0.45,0.50]_membership": gate < lam <= Fraction(1, 2)
        or gate < mu <= Fraction(1, 2),
    }
    control_pass = (
        identities_ok
        and pinned_identities_ok
        and extracted_ok
        and i7["fails_R6_fresh_query"]
        and i7["fails_R7_lambda"]
        and i7["fails_R7_mu"]
    )
    return {
        "control": "CTRL-THRESHOLD-RECOMPUTATION",
        "beta_in_N": str(BETA),
        "recomputed_identities": recomputed,
        "identities_match_frozen_sheet": identities_ok,
        "pinned_derivation_carries_identities": pinned_identities_ok,
        "pinned_control_exponents_match_recomputation": extracted_ok,
        "named_control_I7": i7,
        "pass": control_pass,
    }


# --------------------------------------------------------------------------
# calibration fixtures
# --------------------------------------------------------------------------

# CAL-PASS-SCR-002: synthetic must-pass fixture (declared in the frozen spec;
# excluded from the corpus matrix and not evidence about H-SCR-002).
CAL_PASS_DESCRIPTOR = {
    "fixture_id": "CAL-PASS-SCR-002",
    "synthetic": True,
    "facts": {
        "R1": True,  # explicit typed operation with provenance/subset semantics/signed output
        "R2": True,  # frozen transcript certified non-O(1)-simulable by its own proof sketch
        "R3": True,  # fully enumerated subset-stable replay schedule
        "R4": True,  # deterministic rank guarantee (r = 0.20, eta_rank = 0)
        "R5": True,  # every call/rebuild/live-state charge enumerated
        "R6": True,  # tau = 0.25 <= 0.25 fresh query inside B^(5/4)
    },
    "deterministic_rank_guarantee": True,
    "terms": {
        "a": "0.44", "a_m": "0.44",
        "q_rel": "0.20", "q_rel_replay": "0.10", "q_rel_m": "0.20",
        "o_rel": "0.20", "r": "0.20", "delta_rel": "0.10", "eta_rank": "0",
        "ell": "0.40", "ell_m": "0.20",
        "q_t": "0.20", "q_t_replay": "0.10", "o_t": "0.10",
        "delta_t": "0.025", "u_t": "0.025",
        "m_replay": "0.40", "m_output": "0.20", "b_w": "0.40", "b_m": "0.40",
    },
    "declared": {"lambda": "0.44", "mu": "0.44", "tau": "0.25"},
}


def run_calibration(spec):
    """CTRL-SHEET-CALIBRATION: frozen sheet on the two pre-declared fixtures,
    executed BEFORE any corpus verdict is read."""
    fixtures = []

    # CAL-PASS-SCR-002 (synthetic must-pass).
    terms = {k: Fraction(v) for k, v in CAL_PASS_DESCRIPTOR["terms"].items()}
    r7_ok, r7_detail = evaluate_r7(terms, CAL_PASS_DESCRIPTOR["deterministic_rank_guarantee"])
    facts = dict(CAL_PASS_DESCRIPTOR["facts"])
    facts["R7"] = r7_ok
    verdict, first_failed, cells = apply_sheet(facts)
    declared = CAL_PASS_DESCRIPTOR["declared"]
    declared_match = (
        r7_ok
        and r7_detail["derived"]["lambda_float"] == float(Fraction(declared["lambda"]))
        and r7_detail["derived"]["mu_float"] == float(Fraction(declared["mu"]))
        and r7_detail["derived"]["tau_float"] == float(Fraction(declared["tau"]))
    )
    fixtures.append(
        {
            "id": "CAL-PASS-SCR-002",
            "kind": "must_pass",
            "synthetic_fixture": True,
            "expected_verdict": "ADMIT",
            "actual_verdict": verdict,
            "first_failed_requirement": (
                REQUIREMENT_IDS[first_failed] if first_failed else None
            ),
            "requirement_statuses": {k: c["status"] for k, c in cells.items()},
            "r7_derived": r7_detail.get("derived"),
            "declared_aggregates_match": declared_match,
            "pass": verdict == "ADMIT" and declared_match,
        }
    )

    # CAL-FAIL-SCR-002 (real must-fail): the I5 record through the sheet first.
    corpus = Corpus(spec)
    rec = adjudicate_item("I5", spec, corpus, REQUIREMENT_ORDER)
    r2_status = rec["requirements"]["R2"]["status"]
    expected = (
        rec["verdict"] == "REJECT"
        and rec["first_failed_requirement"] == REQUIREMENT_IDS["R1"]
        and r2_status == "fail_independently"
    )
    fixtures.append(
        {
            "id": "CAL-FAIL-SCR-002",
            "kind": "must_fail",
            "synthetic_fixture": False,
            "expected_verdict": "fail at R1 with independent fail at R2 "
            "(supplied-tuple predicate, O(1)-simulable)",
            "actual_verdict": rec["verdict"],
            "first_failed_requirement": rec["first_failed_requirement"],
            "requirement_statuses": {
                k: c["status"] for k, c in rec["requirements"].items()
            },
            "pass": expected,
        }
    )

    accuracy = sum(1 for f in fixtures if f["pass"]) / len(fixtures)
    return {
        "control": "CTRL-SHEET-CALIBRATION",
        "ordering": "calibration executed before any corpus verdict is read",
        "fixtures": fixtures,
        "accuracy": accuracy,
        "pass": accuracy == 1.0,
    }


# --------------------------------------------------------------------------
# per-item adjudication (checks grounded in pinned corpus bytes)
# --------------------------------------------------------------------------

def _undecidable(item_id, name, checks, reason):
    cells = {
        k: {"requirement_id": REQUIREMENT_IDS[k], "status": "undecidable_with_reason"}
        for k in REQUIREMENT_ORDER
    }
    return {
        "item_id": item_id,
        "item_name": name,
        "verdict": "undecidable_with_reason",
        "undecidable_reason": reason,
        "first_failed_requirement": None,
        "expected_rejection_basis": None,
        "named_rejection_basis": None,
        "rejection_basis_source": None,
        "owners": [],
        "requirements": cells,
        "cost_terms": {"assigned": {}, "unassigned": COST_TERMS, "unassigned_count": len(COST_TERMS)},
        "checks": checks,
    }


def _item_meta(spec, item_id):
    for entry in spec["inputs"]["audit_item_index"]["items"]:
        if entry["id"] == item_id:
            return entry
    raise KeyError("item not in frozen audit_item_index: %s" % item_id)


def adjudicate_item(item_id, spec, corpus, emit_requirements):
    """Ground the item's fact vector in pinned bytes, then apply the sheet.

    emit_requirements: which requirement cells to emit in the returned record
    (the full fact vector is always computed).
    """
    meta = _item_meta(spec, item_id)
    name = meta["name"]
    expected_basis = meta["expected_rejection_basis"]
    report = corpus.yaml(BATCH6_REPORT)
    repaired = {r["id"]: r for r in report["repaired_requirements"]}
    checks = []

    def require(check_id, desc, ok, evidence=None):
        checks.append(_check(check_id, desc, ok, evidence))
        return ok

    ok = True

    # Common check 1: frozen index entry with its expected rejection basis.
    ok &= require(
        "CK-%s-INDEX" % item_id,
        "frozen audit_item_index names the item with its expected rejection basis",
        meta["id"] == item_id and bool(expected_basis),
        {"item_name": name, "expected_rejection_basis": expected_basis},
    )

    # Common check 2: the pinned BATCH-006 repaired sheet records R1 as fail and
    # R2-R7 as fail_independently over the checked material.
    expected_statuses = {"R1": "fail"}
    for k in REQUIREMENT_ORDER[1:]:
        expected_statuses[k] = "fail_independently"
    statuses_ok = all(
        repaired[REQUIREMENT_IDS[k]]["status"] == expected_statuses[k]
        for k in REQUIREMENT_ORDER
    )
    ok &= require(
        "CK-%s-SHEET-STATUSES" % item_id,
        "pinned BATCH-006 repaired_requirements carry the frozen per-requirement "
        "dispositions (R1 fail; R2-R7 fail_independently)",
        statuses_ok,
        {k: repaired[REQUIREMENT_IDS[k]]["status"] for k in REQUIREMENT_ORDER},
    )

    # Item-specific grounding.
    threshold = None
    if item_id in EXCLUDED_NAME:
        excl = {e["name"]: e["disposition"] for e in report["excluded_nonconstructors"]}
        ok &= require(
            "CK-%s-EXCLUSION" % item_id,
            "pinned BATCH-006 excluded_nonconstructors carries the item with the "
            "matching disposition",
            excl.get(EXCLUDED_NAME[item_id]) == EXPECTED_DISPOSITION[item_id],
            {"disposition": excl.get(EXCLUDED_NAME[item_id])},
        )

    if item_id == "I1":
        r3_reason = repaired[REQUIREMENT_IDS["R3"]]["reason"]
        ok &= require(
            "CK-I1-HIDDEN-INPUT",
            "pinned R3 reason rejects supplied residue/source/scalar/dictionary/B^3 "
            "provenance as assuming the missing inverse",
            "assume the missing inverse" in r3_reason,
            {"excerpt": excerpt(r3_reason, "assume the missing inverse")},
        )
    elif item_id == "I2":
        ev002 = corpus.text(EV_CRYPTO_002)
        batch2 = corpus.text(BATCH2_REPORT)
        candidate = corpus.yaml(BATCH5_CANDIDATE)
        excl = {
            e["id"]: e["reason"]
            for e in candidate["corpus_deduplication"]["exact_exclusions"]
        }
        zr = excl.get("OBL-ZR-COMPACT-CONSTRUCTOR-001", "")
        ok &= require(
            "CK-I2-ZR-CLOSURE",
            "EV-CRYPTO-002 records the z_R closure NO_ADMISSIBLE_CONSTRUCTION and "
            "the pinned BATCH-002 sheet failed the same interface",
            "NO_ADMISSIBLE_CONSTRUCTION" in ev002
            and "verdict: NO_ADMISSIBLE_CONSTRUCTION" in batch2,
            {"ev_excerpt": excerpt(ev002, "NO_ADMISSIBLE_CONSTRUCTION")},
        )
        ok &= require(
            "CK-I2-RENAMED-INTERFACE",
            "pinned BATCH-005 exact_exclusions names the route a rename of the "
            "IDEA-20260723-001 interface",
            "IDEA-20260723-001" in zr,
            {"excerpt": excerpt(zr, "IDEA-20260723-001")},
        )
    elif item_id == "I3":
        candidate = corpus.yaml(BATCH5_CANDIDATE)
        excl = {
            e["id"]: e["reason"]
            for e in candidate["corpus_deduplication"]["exact_exclusions"]
        }
        hyp = excl.get("IDEA-20260723-002", "")
        r1_reason = repaired[REQUIREMENT_IDS["R1"]]["reason"]
        ok &= require(
            "CK-I3-RENAMED-ROUTE",
            "pinned BATCH-005 exact_exclusions carries the zero-minor/"
            "hyperplane-signature route as the excluded IDEA-20260723-002 interface",
            "zero-minor" in hyp and "hyperplane-signature" in hyp,
            {"excerpt": excerpt(hyp, "zero-minor")},
        )
        ok &= require(
            "CK-I3-UNNAMED-ORACLE",
            "pinned R1 reason classifies the product/common-factor or zero-minor "
            "route as an excluded interface or an unnamed oracle",
            "unnamed oracle" in r1_reason,
            {"excerpt": excerpt(r1_reason, "unnamed oracle")},
        )
    elif item_id == "I4":
        admission_md = corpus.text(BATCH6_ADMISSION_MD)
        ok &= require(
            "CK-I4-TARGET-LEAKAGE",
            "pinned BATCH-006 admission note lists target-fitted coefficients among "
            "the rejected supplied-payload classes",
            "target-fitted" in admission_md,
            {"excerpt": excerpt(admission_md, "target-fitted")},
        )
    elif item_id == "I5":
        r2_reason = repaired[REQUIREMENT_IDS["R2"]]["reason"]
        facts_text = "\n".join(report["epistemic_separation"]["established_facts"])
        p1553 = corpus.text(P1553_GATE)
        ok &= require(
            "CK-I5-SUPPLIED-TUPLE-PREDICATE",
            "pinned established facts record that the determinant, pair-wedge, and "
            "Abel-endpoint predicates test supplied tuples or endpoints",
            "predicates test supplied tuples or endpoints" in facts_text,
            {"excerpt": excerpt(facts_text, "predicates test supplied tuples or endpoints")},
        )
        ok &= require(
            "CK-I5-O1-SIMULABLE",
            "pinned R2 reason records the supplied-tuple determinant/wedge zero bit "
            "as reproduced with O(1) generic group operations",
            "reproduced with O(1) generic group operations" in r2_reason,
            {"excerpt": excerpt(r2_reason, "reproduced with O(1) generic group operations")},
        )
        ok &= require(
            "CK-I5-P1553-GATE",
            "pinned P1553 gate records no endpoint-only batch locator",
            "P1553 supplies no endpoint-only batch locator" in p1553,
            {"excerpt": excerpt(p1553, "P1553 supplies no endpoint-only batch locator")},
        )
    elif item_id == "I6":
        r1_reason = repaired[REQUIREMENT_IDS["R1"]]["reason"]
        ok &= require(
            "CK-I6-GENERIC-CONTROL",
            "pinned R1 reason classifies direct 3+3 matching as the known generic "
            "control",
            "Direct 3+3 matching is the known generic control" in r1_reason,
            {"excerpt": excerpt(r1_reason, "Direct 3+3 matching")},
        )
    elif item_id == "I7":
        closest = report["baseline_comparison"]["closest_specialized_control"]
        ok &= require(
            "CK-I7-NAMED-CONTROL",
            "pinned baseline_comparison names the explicit source-labelled six-list "
            "control and records it as not semantically new with N^0.60 campaign work",
            closest["name"] == "source_labelled_six_list_Abel_Jacobi_endpoint_control"
            and "not semantically new" in closest["assessment"]
            and "N^(0.60+o(1))" in closest["complete_campaign_work"],
            {"excerpt": excerpt(closest["assessment"], "not semantically new")},
        )
        threshold = threshold_recomputation(spec, corpus)
        ok &= require(
            "CK-I7-THRESHOLD-RECOMPUTATION",
            "symbolic recomputation of the frozen exponent identities and the named "
            "control's lambda/mu/tau matches the pinned record and fails R6/R7 with "
            "certifiable work exponent at least 0.60",
            threshold["pass"],
            {
                "lambda_certifiable_at_least": threshold["named_control_I7"]["lambda_certifiable_at_least"],
                "mu_materialized": threshold["named_control_I7"]["mu_materialized"],
                "tau": threshold["named_control_I7"]["tau"],
            },
        )

    # Dedup: named rejection basis must match the pinned disposition (I1-I6) or
    # the named explicit control (I7), with owners.
    if item_id == "I7":
        basis_source = "named explicit control: pinned charged_cost_model.current_explicit_control " \
                       "and baseline_comparison.closest_specialized_control"
        basis_ok = expected_basis == "work_and_memory_exponent_0.60_fresh_query_0.60"
    else:
        basis_source = "BATCH-006 excluded_nonconstructors disposition: %s" % EXPECTED_DISPOSITION[item_id]
        basis_ok = True  # disposition equality already checked in CK-...-EXCLUSION
    ok &= require(
        "CK-%s-DEDUP-BASIS" % item_id,
        "named rejection basis matches the frozen expected basis and the pinned "
        "exclusion record (CTRL-DEDUP-PRIOR-NEGATIVES)",
        basis_ok and bool(ITEM_OWNERS[item_id]),
        {"expected_rejection_basis": expected_basis, "source": basis_source},
    )

    if not ok:
        failed = [c["check_id"] for c in checks if c["result"] == "fail"]
        return _undecidable(
            item_id, name, checks,
            "grounding checks failed: %s" % ", ".join(failed),
        )

    # Fact vector: no grounded item supplies any of R1-R7 (all facts False).
    facts = {k: False for k in REQUIREMENT_ORDER}
    verdict, first_failed, cells = apply_sheet(facts)

    # Grounded per-cell reasons.
    for key in REQUIREMENT_ORDER:
        if cells[key]["status"] == "pass":
            continue
        if key == "R1":
            reason = R1_FAIL_REASON[item_id]
        elif key == "R2":
            reason = R2_FAIL_REASON.get(item_id, R2_FAIL_REASON["default"])
        elif key == "R3":
            reason = R3_FAIL_REASON.get(item_id, R3_FAIL_REASON["default"])
        elif key == "R4":
            reason = R4_FAIL_REASON
        elif key == "R5":
            reason = R5_FAIL_REASON
        elif key == "R6":
            reason = R6_FAIL_REASON.get(item_id, R6_FAIL_REASON["default"])
        else:
            reason = R7_FAIL_REASON.get(item_id, R7_FAIL_REASON["default"])
        cells[key]["reason"] = reason

    # Cost-term assignment (R7 secondary metric): unknown terms are failures.
    if item_id == "I7":
        assigned = {
            "a": "0.40", "a_m": "0.40", "ell": "0.40 (optimistic, conditioned on "
            "Theta(B) independent verified rows)", "ell_m": "0.20", "r": "0",
        }
        unassigned = [t for t in COST_TERMS if t not in ("a", "a_m", "ell", "ell_m", "r")]
    else:
        assigned = {}
        unassigned = list(COST_TERMS)

    record = {
        "item_id": item_id,
        "item_name": name,
        "verdict": verdict,
        "first_failed_requirement": REQUIREMENT_IDS[first_failed] if first_failed else None,
        "expected_rejection_basis": expected_basis,
        "named_rejection_basis": expected_basis,
        "rejection_basis_source": basis_source,
        "owners": ITEM_OWNERS[item_id],
        "requirements": {k: cells[k] for k in emit_requirements},
        "cost_terms": {
            "assigned": assigned,
            "unassigned": unassigned,
            "unassigned_count": len(unassigned),
        },
        "checks": checks,
    }
    if item_id == "I7" and threshold is not None and "R7" in emit_requirements:
        record["requirements"]["R7"]["recomputation"] = threshold["named_control_I7"]
    if item_id == "I7" and threshold is not None and "R6" in emit_requirements:
        record["requirements"]["R6"]["tau_recomputed"] = threshold["named_control_I7"]["tau"]
    return record


def adjudicate_items(item_ids, spec, emit_requirements):
    corpus = Corpus(spec)
    return [adjudicate_item(i, spec, corpus, emit_requirements) for i in item_ids]


def merge_records(b_records, c_records):
    """Pass-1 matrix: R1-R4 cells from RUN-SCR-002-B + R5-R7 cells from
    RUN-SCR-002-C, verdict recomputed from the merged cells."""
    merged = []
    for b, c in zip(b_records, c_records):
        assert b["item_id"] == c["item_id"]
        reqs = dict(b["requirements"])
        reqs.update(c["requirements"])
        if b["verdict"] == "undecidable_with_reason" or c["verdict"] == "undecidable_with_reason":
            verdict = "undecidable_with_reason"
            first_failed = None
        else:
            verdict, fk = verdict_from_cells(reqs)
            first_failed = REQUIREMENT_IDS[fk] if fk else None
        rec = dict(c)
        rec["requirements"] = reqs
        rec["verdict"] = verdict
        rec["first_failed_requirement"] = first_failed
        rec["checks"] = b["checks"] + c["checks"]
        merged.append(rec)
    return merged


def _matrix_payload(records):
    return [
        {
            "item_id": r["item_id"],
            "verdict": r["verdict"],
            "first_failed_requirement": r["first_failed_requirement"],
            "named_rejection_basis": r["named_rejection_basis"],
            "requirements": {
                k: {"requirement_id": c["requirement_id"], "status": c["status"]}
                for k, c in r["requirements"].items()
            },
        }
        for r in records
    ]


def _verdict_flips(pass1, pass2):
    p2 = {r["item_id"]: r for r in pass2}
    flips = []
    for r in pass1:
        other = p2.get(r["item_id"])
        if other is None:
            flips.append({"item_id": r["item_id"], "pass2": "missing"})
            continue
        if other["verdict"] != r["verdict"]:
            flips.append(
                {"item_id": r["item_id"], "pass1": r["verdict"], "pass2": other["verdict"]}
            )
    return flips


def _per_requirement_tally(records):
    tally = {}
    for key in REQUIREMENT_ORDER:
        counts = {"pass": 0, "fail": 0, "fail_independently": 0, "undecidable_with_reason": 0}
        for r in records:
            status = r["requirements"].get(key, {}).get("status")
            if status in counts:
                counts[status] += 1
        tally[REQUIREMENT_IDS[key]] = counts
    return tally


def _now():
    return datetime.now(timezone.utc).isoformat()


def _write_out(out_path, raw):
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(canonical_json(raw))


def _pre_controls(spec):
    corpus_report = verify_corpus(spec)
    calibration = run_calibration(spec)
    return corpus_report, calibration


# --------------------------------------------------------------------------
# payload commands
# --------------------------------------------------------------------------

def cmd_run_a(out_path):
    spec = load_spec()
    print("RUN-SCR-002-A: freeze corpus manifest + calibration + threshold recomputation")
    corpus_report = verify_corpus(spec)
    manifest_path = os.path.join(EXP_DIR, "corpus_manifest.json")
    write_json_if_absent_or_identical(manifest_path, corpus_report)
    print(
        "corpus integrity: %d/%d verified, missing=%d, mismatches=%d"
        % (
            corpus_report["verified"],
            corpus_report["entry_count"],
            len(corpus_report["missing"]),
            len(corpus_report["mismatches"]),
        )
    )
    calibration = run_calibration(spec)
    receipt_path = os.path.join(EXP_DIR, "sheet", "calibration_receipt.json")
    write_json_if_absent_or_identical(receipt_path, calibration)
    print(
        "calibration: accuracy=%.3f pass=%s (%s)"
        % (
            calibration["accuracy"],
            calibration["pass"],
            ", ".join(
                "%s=%s" % (f["id"], f["actual_verdict"]) for f in calibration["fixtures"]
            ),
        )
    )
    threshold = threshold_recomputation(spec, Corpus(spec))
    print(
        "threshold recomputation: pass=%s (I7 lambda>=%s mu=%s tau=%s)"
        % (
            threshold["pass"],
            threshold["named_control_I7"]["lambda_certifiable_at_least"],
            threshold["named_control_I7"]["mu_materialized"],
            threshold["named_control_I7"]["tau"],
        )
    )
    valid = corpus_report["pass"] and calibration["pass"] and threshold["pass"]
    invalid_reason = None
    if not corpus_report["pass"]:
        invalid_reason = "corpus integrity control failed (missing or mismatched pinned blobs)"
    elif not calibration["pass"]:
        invalid_reason = "calibration accuracy below 2/2 (sheet unsound as instrumented)"
    elif not threshold["pass"]:
        invalid_reason = "threshold recomputation disagrees with the frozen sheet"
    raw = {
        "run_id": "RUN-SCR-002-A",
        "experiment_id": "EXP-SCR-002",
        "generated_at": _now(),
        "corpus_integrity": {k: v for k, v in corpus_report.items() if k != "entries"},
        "corpus_manifest_path": os.path.relpath(manifest_path, REPO_ROOT),
        "calibration": calibration,
        "calibration_receipt_path": os.path.relpath(receipt_path, REPO_ROOT),
        "threshold_recomputation": threshold,
        "controls": {
            "CTRL-CORPUS-INTEGRITY": "pass" if corpus_report["pass"] else "fail",
            "CTRL-SHEET-CALIBRATION": "pass" if calibration["pass"] else "fail",
            "CTRL-THRESHOLD-RECOMPUTATION": "pass" if threshold["pass"] else "fail",
        },
        "valid": valid,
        "invalid_reason": invalid_reason,
    }
    _write_out(out_path, raw)
    return 0 if valid else 2


def cmd_run_b(out_path):
    spec = load_spec()
    print("RUN-SCR-002-B: adjudicate R1-R4 over all 7 items")
    corpus_report, calibration = _pre_controls(spec)
    print(
        "pre-controls: corpus=%s calibration=%s"
        % (corpus_report["pass"], calibration["pass"])
    )
    if not (corpus_report["pass"] and calibration["pass"]):
        raw = {
            "run_id": "RUN-SCR-002-B",
            "experiment_id": "EXP-SCR-002",
            "generated_at": _now(),
            "corpus_integrity_pass": corpus_report["pass"],
            "calibration": calibration,
            "adjudications": [],
            "controls": {
                "CTRL-CORPUS-INTEGRITY": "pass" if corpus_report["pass"] else "fail",
                "CTRL-SHEET-CALIBRATION": "pass" if calibration["pass"] else "fail",
            },
            "valid": False,
            "invalid_reason": "pre-controls failed before adjudication",
        }
        _write_out(out_path, raw)
        return 2

    records = adjudicate_items(ALL_ITEMS, spec, ["R1", "R2", "R3", "R4"])
    for rec in records:
        print(
            "  %s %-62s -> %s (first: %s)"
            % (
                rec["item_id"],
                rec["item_name"][:62],
                rec["verdict"],
                rec["first_failed_requirement"],
            )
        )
    rejected = [r for r in records if r["verdict"] == "REJECT"]
    undecidable = [r for r in records if r["verdict"] == "undecidable_with_reason"]
    basis_coverage = (
        sum(1 for r in rejected if r["named_rejection_basis"] and r["owners"])
        / len(rejected)
        if rejected
        else 1.0
    )
    dedup_pass = basis_coverage == 1.0 and not undecidable
    valid = dedup_pass
    raw = {
        "run_id": "RUN-SCR-002-B",
        "experiment_id": "EXP-SCR-002",
        "generated_at": _now(),
        "corpus_integrity_pass": corpus_report["pass"],
        "calibration": calibration,
        "adjudications": records,
        "r1_r4_tally": _per_requirement_tally(records),
        "rejection_basis_coverage": basis_coverage,
        "undecidable_items": [
            {"item_id": r["item_id"], "reason": r.get("undecidable_reason")}
            for r in undecidable
        ],
        "inconclusive": bool(undecidable),
        "controls": {
            "CTRL-CORPUS-INTEGRITY": "pass",
            "CTRL-SHEET-CALIBRATION": "pass",
            "CTRL-DEDUP-PRIOR-NEGATIVES": "pass" if dedup_pass else "fail",
        },
        "valid": valid,
        "invalid_reason": None
        if valid
        else "dedup rejection-basis coverage below 1.0 or undecidable item present",
    }
    _write_out(out_path, raw)
    return 0 if valid else 2


def cmd_run_c(out_path):
    spec = load_spec()
    print("RUN-SCR-002-C: adjudicate R5-R7, replay, emit matrix and decision")
    corpus_report, calibration = _pre_controls(spec)
    print(
        "pre-controls: corpus=%s calibration=%s"
        % (corpus_report["pass"], calibration["pass"])
    )
    if not (corpus_report["pass"] and calibration["pass"]):
        raw = {
            "run_id": "RUN-SCR-002-C",
            "experiment_id": "EXP-SCR-002",
            "generated_at": _now(),
            "corpus_integrity_pass": corpus_report["pass"],
            "calibration": calibration,
            "adjudications": [],
            "controls": {
                "CTRL-CORPUS-INTEGRITY": "pass" if corpus_report["pass"] else "fail",
                "CTRL-SHEET-CALIBRATION": "pass" if calibration["pass"] else "fail",
            },
            "valid": False,
            "invalid_reason": "pre-controls failed before adjudication",
        }
        _write_out(out_path, raw)
        return 2

    run_b_raw_path = os.path.join(EXP_DIR, "runs", "RUN-SCR-002-B", "raw-result.json")
    if not os.path.exists(run_b_raw_path):
        raw = {
            "run_id": "RUN-SCR-002-C",
            "experiment_id": "EXP-SCR-002",
            "generated_at": _now(),
            "adjudications": [],
            "controls": {},
            "valid": False,
            "invalid_reason": "dependency RUN-SCR-002-B raw result missing",
        }
        _write_out(out_path, raw)
        return 2
    with open(run_b_raw_path, "r", encoding="utf-8") as fh:
        run_b_records = json.load(fh)["adjudications"]

    records_c = adjudicate_items(ALL_ITEMS, spec, ["R5", "R6", "R7"])
    for rec in records_c:
        print(
            "  %s %-62s R5-R7: %s"
            % (
                rec["item_id"],
                rec["item_name"][:62],
                {k: c["status"] for k, c in rec["requirements"].items()},
            )
        )

    # Pass 1: RUN-SCR-002-B R1-R4 cells + this run's R5-R7 cells.
    pass1_records = merge_records(run_b_records, records_c)
    # CTRL-REPLAY-DETERMINISM pass 2: fresh full-sheet application over all 7.
    pass2_records = adjudicate_items(ALL_ITEMS, spec, REQUIREMENT_ORDER)
    payload1 = _matrix_payload(pass1_records)
    payload2 = _matrix_payload(pass2_records)
    bytes1 = canonical_json(payload1).encode("utf-8")
    bytes2 = canonical_json(payload2).encode("utf-8")
    replay_identical = bytes1 == bytes2
    replay = {
        "control": "CTRL-REPLAY-DETERMINISM",
        "pass1_source": "RUN-SCR-002-B adjudications (R1-R4) + RUN-SCR-002-C adjudications (R5-R7)",
        "pass2_source": "fresh full-sheet application over all 7 items in RUN-SCR-002-C",
        "pass1_sha256": sha256_hex(bytes1),
        "pass2_sha256": sha256_hex(bytes2),
        "byte_identical": replay_identical,
        "verdict_flips": _verdict_flips(pass1_records, pass2_records),
        "pass": replay_identical,
    }
    print("replay determinism: byte_identical=%s" % replay_identical)

    threshold = threshold_recomputation(spec, Corpus(spec))

    rejected = [r for r in pass1_records if r["verdict"] == "REJECT"]
    undecidable = [r for r in pass1_records if r["verdict"] == "undecidable_with_reason"]
    admitted = [r for r in pass1_records if r["verdict"] == "ADMIT"]
    basis_coverage = (
        sum(1 for r in rejected if r["named_rejection_basis"] and r["owners"])
        / len(rejected)
        if rejected
        else 1.0
    )
    cell_count = sum(len(r["requirements"]) for r in pass1_records)
    matrix_complete = cell_count == 7 * 7
    interval_flags = []
    for r in pass1_records:
        r7 = r["requirements"].get("R7", {})
        recomp = r7.get("recomputation")
        if recomp and recomp["interval_(0.45,0.50]_membership"]:
            interval_flags.append(
                {"item_id": r["item_id"], "note": "lambda/mu in (0.45, 0.50] fails R7 explicitly"}
            )

    matrix = {
        "experiment_id": "EXP-SCR-002",
        "hypothesis_id": spec["hypothesis_id"],
        "pinned_commit": pinned_commit(spec),
        "sheet": "frozen repaired SOURCE-LOCATOR-OPEN admission sheet R1-R7 (specification.yaml)",
        "verdict_rule": spec["inputs"]["frozen_admission_sheet"]["verdict_rule"],
        "asymptotic_regime": spec["inputs"]["frozen_admission_sheet"]["asymptotic_regime"],
        "item_count": len(pass1_records),
        "requirement_count": 7,
        "cell_count": cell_count,
        "matrix_completeness": cell_count / 49.0,
        "admissible_operation_count": len(admitted),
        "rejection_basis_coverage": basis_coverage,
        "undecidable_items": [
            {"item_id": r["item_id"], "reason": r.get("undecidable_reason")}
            for r in undecidable
        ],
        "unknown_exponent_term_count": {
            r["item_id"]: r["cost_terms"]["unassigned_count"] for r in pass1_records
        },
        "per_requirement_failure_counts": _per_requirement_tally(pass1_records),
        "first_failed_requirement_per_item": {
            r["item_id"]: r["first_failed_requirement"] for r in pass1_records
        },
        "interval_check_(0.45,0.50]": {
            "flagged_items": interval_flags,
            "rule": "any item scoring lambda or mu in (0.45, 0.50] fails R7 explicitly",
        },
        "replay_determinism": replay,
        "threshold_recomputation": threshold,
        "items": pass1_records,
    }
    matrix_path = os.path.join(EXP_DIR, "requirement_matrix.json")
    write_json_if_absent_or_identical(matrix_path, matrix)

    decision = {
        "experiment_id": "EXP-SCR-002",
        "hypothesis_id": spec["hypothesis_id"],
        "decision_basis": "frozen repaired sheet R1-R7 applied mechanically to the 7 "
        "frozen audit items at the pinned corpus snapshot",
        "admissible_operation_count": len(admitted),
        "decision": "zero_admissible_operations" if not admitted else "falsification_class_observation",
        "falsification_observations": [
            {
                "note": "VERBATIM falsification-class observation (spec "
                "falsification_criterion): an item passed R1-R7; recorded as an "
                "unfiled theorem candidate. The Executor does not escalate further.",
                "item": r,
            }
            for r in admitted
        ],
        "per_item": [
            {
                "item_id": r["item_id"],
                "item_name": r["item_name"],
                "verdict": r["verdict"],
                "first_failed_requirement": r["first_failed_requirement"],
                "named_rejection_basis": r["named_rejection_basis"],
            }
            for r in pass1_records
        ],
        "observations_only": True,
        "note": "Observations only. No conclusion that H-SCR-002 is supported or "
        "refuted; evidence-strength assignment and any status transition belong to "
        "the Coordinator under independent review.",
    }
    decision_path = os.path.join(EXP_DIR, "admission_decision.json")
    write_json_if_absent_or_identical(decision_path, decision)

    dedup_pass = basis_coverage == 1.0 and not undecidable
    controls = {
        "CTRL-CORPUS-INTEGRITY": "pass",
        "CTRL-SHEET-CALIBRATION": "pass",
        "CTRL-THRESHOLD-RECOMPUTATION": "pass" if threshold["pass"] else "fail",
        "CTRL-DEDUP-PRIOR-NEGATIVES": "pass" if dedup_pass else "fail",
        "CTRL-REPLAY-DETERMINISM": "pass" if replay_identical else "fail",
    }
    valid = (
        replay_identical
        and dedup_pass
        and matrix_complete
        and threshold["pass"]
    )
    invalid_reason = None
    if not replay_identical:
        invalid_reason = "non-identical requirement matrices across determinism passes"
    elif not dedup_pass:
        invalid_reason = "dedup rejection-basis coverage below 1.0 or undecidable item present"
    elif not matrix_complete:
        invalid_reason = "incomplete requirement matrix (fewer than 7x7 cells without undecidable records)"
    elif not threshold["pass"]:
        invalid_reason = "threshold recomputation disagrees with the frozen sheet"
    raw = {
        "run_id": "RUN-SCR-002-C",
        "experiment_id": "EXP-SCR-002",
        "generated_at": _now(),
        "corpus_integrity_pass": corpus_report["pass"],
        "calibration": calibration,
        "adjudications": records_c,
        "replay_determinism": replay,
        "threshold_recomputation": threshold,
        "r5_r7_tally": _per_requirement_tally(records_c),
        "full_matrix_tally": _per_requirement_tally(pass1_records),
        "admissible_operation_count": len(admitted),
        "rejection_basis_coverage": basis_coverage,
        "cell_count": cell_count,
        "undecidable_items": matrix["undecidable_items"],
        "inconclusive": bool(undecidable),
        "requirement_matrix_path": os.path.relpath(matrix_path, REPO_ROOT),
        "admission_decision_path": os.path.relpath(decision_path, REPO_ROOT),
        "controls": controls,
        "valid": valid,
        "invalid_reason": invalid_reason,
    }
    _write_out(out_path, raw)
    return 0 if valid else 2


# --------------------------------------------------------------------------
# harness: immutable run records with measured resources
# --------------------------------------------------------------------------

def cmd_harness(run_id):
    if run_id not in PLANNED_RUNS:
        raise SystemExit("unknown run id: %s" % run_id)
    run_dir = os.path.join(EXP_DIR, "runs", run_id)
    if os.path.exists(run_dir):
        raise SystemExit("run dir already exists (immutable): %s" % run_dir)
    os.makedirs(run_dir)
    raw_path = os.path.join(run_dir, "raw-result.json")
    payload = [
        sys.executable,
        os.path.relpath(os.path.abspath(__file__), REPO_ROOT),
        PLANNED_RUNS[run_id],
        "--out",
        os.path.relpath(raw_path, REPO_ROOT),
    ]
    command_str = " ".join(payload)
    with open(os.path.join(run_dir, "command.txt"), "w", encoding="utf-8") as fh:
        fh.write(command_str + "\n")

    env = _environment()
    with open(os.path.join(run_dir, "environment.json"), "w", encoding="utf-8") as fh:
        fh.write(canonical_json(env))

    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=REPO_ROOT
    ).stdout.strip()
    status_lines = subprocess.run(
        ["git", "status", "--porcelain"], capture_output=True, text=True, cwd=REPO_ROOT
    ).stdout.splitlines()
    tracked, untracked = [], []
    for line in status_lines:
        xy, path = line[:2], line[3:]
        if xy == "??":
            untracked.append(path)
        else:
            tracked.append(path)
    tracked_appledouble = [p for p in tracked if os.path.basename(p).startswith("._")]
    tracked_real = [p for p in tracked if not os.path.basename(p).startswith("._")]
    # Dirty basis (disclosed): tracked, non-._ paths only. ._ AppleDouble exFAT
    # artifacts and new untracked run artifacts under experiments/EXP-SCR-002/
    # do not set the flag.
    dirty = bool(tracked_real)

    started_at = _now()
    t0 = time.monotonic()
    usage_before = resource.getrusage(resource.RUSAGE_CHILDREN)
    timed_out = False
    infra_error = None
    stdout_path = os.path.join(run_dir, "stdout.log")
    stderr_path = os.path.join(run_dir, "stderr.log")
    with open(stdout_path, "w", encoding="utf-8") as out_fh, open(
        stderr_path, "w", encoding="utf-8"
    ) as err_fh:
        try:
            proc = subprocess.Popen(
                payload,
                cwd=REPO_ROOT,
                stdout=out_fh,
                stderr=err_fh,
            )
            try:
                rc = proc.wait(timeout=WALL_TIMEOUT_SECONDS)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
                timed_out = True
                rc = None
        except OSError as exc:  # infrastructure: spawn failure
            rc = None
            infra_error = "spawn failure: %s" % exc
    wall = time.monotonic() - t0
    finished_at = _now()
    usage_after = resource.getrusage(resource.RUSAGE_CHILDREN)
    cpu_seconds = (usage_after.ru_utime - usage_before.ru_utime) + (
        usage_after.ru_stime - usage_before.ru_stime
    )
    peak_rss = usage_after.ru_maxrss
    rss_unit = "bytes"
    if sys.platform != "darwin":
        peak_rss = peak_rss * 1024  # Linux reports KiB
        rss_unit = "bytes (converted from KiB)"

    raw = None
    if os.path.exists(raw_path):
        with open(raw_path, "r", encoding="utf-8") as fh:
            raw = json.load(fh)

    if timed_out:
        status_str = "resource_exhaustion"
        validity_reason = "exceeded per-run wall-clock budget of %ds (killed)" % WALL_TIMEOUT_SECONDS
        valid = False
    elif peak_rss > MEM_LIMIT_BYTES:
        status_str = "resource_exhaustion"
        validity_reason = "measured peak RSS %d bytes exceeded the 4 GB memory budget" % peak_rss
        valid = False
    elif infra_error:
        status_str = "failed_infrastructure"
        validity_reason = infra_error
        valid = False
    elif rc != 0 and raw is None:
        status_str = "failed_implementation"
        validity_reason = "payload exited rc=%s without writing raw result" % rc
        valid = False
    elif raw is None:
        status_str = "failed_infrastructure"
        validity_reason = "raw result artifact missing after rc=0"
        valid = False
    else:
        valid = bool(raw.get("valid"))
        status_str = "completed_valid" if valid else "completed_invalid"
        validity_reason = raw.get("invalid_reason") or (
            "all frozen controls passed" if valid else "frozen control(s) failed"
        )

    metrics = {}
    if raw:
        metrics = {
            "valid": raw.get("valid"),
            "controls": raw.get("controls", {}),
        }
        if "corpus_integrity" in raw:
            metrics["corpus_verified"] = raw["corpus_integrity"]["verified"]
            metrics["corpus_entries"] = raw["corpus_integrity"]["entry_count"]
        if "calibration" in raw:
            metrics["calibration_accuracy"] = raw["calibration"]["accuracy"]
        if "rejection_basis_coverage" in raw:
            metrics["rejection_basis_coverage"] = raw["rejection_basis_coverage"]
        if "undecidable_items" in raw:
            metrics["undecidable_item_count"] = len(raw["undecidable_items"])
        if "admissible_operation_count" in raw:
            metrics["admissible_operation_count"] = raw["admissible_operation_count"]
        if "cell_count" in raw:
            metrics["cell_count"] = raw["cell_count"]
        if "replay_determinism" in raw:
            metrics["replay_byte_identical"] = raw["replay_determinism"]["byte_identical"]

    anomalies = []
    if tracked_appledouble:
        anomalies.append(
            "worktree carries %d tracked ._ AppleDouble exFAT artifact "
            "modifications; excluded from the dirty flag per the disclosed basis; "
            "no tracked source content modified" % len(tracked_appledouble)
        )

    summary = {
        "run_id": run_id,
        "experiment_id": "EXP-SCR-002",
        "status": status_str,
        "valid": valid,
        "metrics": metrics,
        "timing": {"wall_seconds": round(wall, 6)},
        "resources": {"cpu_seconds": round(cpu_seconds, 6), "peak_rss_bytes": peak_rss},
    }
    with open(os.path.join(run_dir, "summary.json"), "w", encoding="utf-8") as fh:
        fh.write(canonical_json(summary))

    # Handoff-named aliases with byte-identical content (DEV-1 resolution:
    # frozen spec names raw-result.json/stdout.log/stderr.log; handoff names
    # raw.json/summary.json/stdout.txt/stderr.txt; both sets are emitted).
    for src, dst in (
        ("raw-result.json", "raw.json"),
        ("stdout.log", "stdout.txt"),
        ("stderr.log", "stderr.txt"),
    ):
        src_path = os.path.join(run_dir, src)
        if os.path.exists(src_path):
            with open(src_path, "rb") as fh:
                content = fh.read()
            with open(os.path.join(run_dir, dst), "wb") as fh:
                fh.write(content)

    artifacts = {}
    for fname in sorted(os.listdir(run_dir)):
        if fname == "manifest.yaml" or fname.startswith("._"):
            continue
        with open(os.path.join(run_dir, fname), "rb") as fh:
            artifacts[fname] = sha256_hex(fh.read())

    spec = load_spec()
    manifest = {
        "run": {
            "id": run_id,
            "experiment_id": "EXP-SCR-002",
            "task_id": TASK_ID,
            "status": status_str,
            "validity_reason": validity_reason,
            "code": {
                "commit": commit,
                "dirty": dirty,
                "dirty_basis": "tracked, non-._ paths only (git status --porcelain); "
                "._ AppleDouble exFAT artifacts and new untracked run artifacts "
                "under experiments/EXP-SCR-002/ do not set the flag",
                "dirty_detail": {
                    "tracked_modified_non_appledouble": len(tracked_real),
                    "tracked_modified_appledouble": len(tracked_appledouble),
                    "untracked_path_count": len(untracked),
                },
                "command": command_str,
                "harness_command": "%s %s harness --run-id %s"
                % (sys.executable, os.path.relpath(os.path.abspath(__file__), REPO_ROOT), run_id),
            },
            "inference": {
                "requested_policy": "executor-implementation",
                "resolved_model_id": None,
                "reasoning_effort": None,
                "fallback_used": False,
                "degraded_requirements": [],
                "adapter_version": None,
                "model_verified": "unverified (no adapter probe inside Executor runs)",
                "note": "deterministic stdlib+PyYAML audit; no model inference performed inside any run",
            },
            "environment": env,
            "inputs": {
                "seeds": [],
                "seed_policy": spec["replication"]["seed_policy"],
                "pinned_commit": pinned_commit(spec),
                "parameters": {
                    "run_purpose": _run_purpose(spec, run_id),
                },
            },
            "timing": {
                "started_at": started_at,
                "finished_at": finished_at,
                "wall_seconds": round(wall, 6),
            },
            "resources": {
                "peak_rss_bytes": peak_rss,
                "peak_rss_unit": rss_unit,
                "cpu_seconds": round(cpu_seconds, 6),
                "measurement_method": "resource.getrusage(RUSAGE_CHILDREN) delta around the payload "
                "child; wall via time.monotonic; memory budget enforced post-hoc against "
                "measured peak RSS (darwin rejects setrlimit RLIMIT_AS)",
                "limits": {
                    "wall_timeout_seconds": WALL_TIMEOUT_SECONDS,
                    "stage_budget_seconds": STAGE_BUDGET_SECONDS[run_id],
                    "memory_budget_bytes": MEM_LIMIT_BYTES,
                },
            },
            "controls": raw.get("controls", {}) if raw else {},
            "result": {
                "metrics": metrics,
                "valid": valid,
                "invalid_reason": None if valid else validity_reason,
                "certificate": {"kind": "none", "verified": None, "verifier": None},
            },
            "protocol_deviations": [],
            "anomalies": anomalies,
            "artifacts": artifacts,
        }
    }
    with open(os.path.join(run_dir, "manifest.yaml"), "w", encoding="utf-8") as fh:
        yaml.safe_dump(manifest, fh, sort_keys=False, default_flow_style=False)
    print(
        "%s: status=%s wall=%.3fs cpu=%.3fs peak_rss=%dB"
        % (run_id, status_str, wall, cpu_seconds, peak_rss)
    )
    return 0 if status_str == "completed_valid" else 1


def _run_purpose(spec, run_id):
    for run in spec["replication"]["planned_runs"]:
        if run["id"] == run_id:
            return run["purpose"]
    return None


def _environment():
    git_version = subprocess.run(
        ["git", "--version"], capture_output=True, text=True, cwd=REPO_ROOT
    ).stdout.strip()
    return {
        "operating_system": platform.system() + " " + platform.release(),
        "architecture": platform.machine(),
        "hostname": platform.node(),
        "python_version": sys.version.split()[0],
        "python_implementation": platform.python_implementation(),
        "sage_version": None,
        "git_version": git_version,
        "dependencies": {"pyyaml": yaml.__version__},
        "cpu_count": os.cpu_count(),
        "volume_note": "exFAT volume; ._ AppleDouble files may appear and are ignored",
    }


# --------------------------------------------------------------------------
# lifecycle step-7 validation
# --------------------------------------------------------------------------

def cmd_validate():
    spec = load_spec()
    checks = []

    run_ids = list(PLANNED_RUNS)
    run_dirs = [
        d
        for d in os.listdir(os.path.join(EXP_DIR, "runs"))
        if d.startswith("RUN-") and not d.startswith("._")
    ]
    checks.append(
        _check(
            "expected_run_count",
            "exactly the 3 planned runs exist",
            sorted(run_dirs) == sorted(run_ids),
            {"planned": run_ids, "found": sorted(run_dirs)},
        )
    )

    required_files = [
        "manifest.yaml",
        "command.txt",
        "environment.json",
        "raw-result.json",
        "raw.json",
        "summary.json",
        "stdout.log",
        "stdout.txt",
        "stderr.log",
        "stderr.txt",
    ]
    manifests = {}
    schema_ok = True
    schema_detail = {}
    for rid in run_ids:
        rdir = os.path.join(EXP_DIR, "runs", rid)
        missing = [f for f in required_files if not os.path.exists(os.path.join(rdir, f))]
        schema_detail[rid] = {"missing_files": missing}
        if missing:
            schema_ok = False
            continue
        with open(os.path.join(rdir, "manifest.yaml"), "r", encoding="utf-8") as fh:
            m = yaml.safe_load(fh)["run"]
        manifests[rid] = m
        required_keys = [
            "id",
            "experiment_id",
            "status",
            "code",
            "inference",
            "environment",
            "inputs",
            "timing",
            "resources",
            "result",
            "artifacts",
        ]
        missing_keys = [k for k in required_keys if k not in m]
        schema_detail[rid]["missing_keys"] = missing_keys
        if missing_keys:
            schema_ok = False
        if m.get("status") not in TERMINAL_STATUSES:
            schema_ok = False
            schema_detail[rid]["bad_status"] = m.get("status")
        if m["inputs"].get("seeds") != [] or not m["inputs"].get("seed_policy"):
            schema_ok = False
            schema_detail[rid]["seed_issue"] = True
        if not isinstance(m["timing"].get("wall_seconds"), (int, float)) or m["timing"]["wall_seconds"] <= 0:
            schema_ok = False
        if not isinstance(m["resources"].get("peak_rss_bytes"), int):
            schema_ok = False
        if not isinstance(m["resources"].get("cpu_seconds"), (int, float)):
            schema_ok = False
    checks.append(
        _check(
            "schema_validity",
            "all run records carry the required files and manifest fields with terminal statuses",
            schema_ok,
            schema_detail,
        )
    )

    seed_ok = all(
        manifests.get(rid, {}).get("inputs", {}).get("seeds") == []
        and manifests.get(rid, {}).get("inputs", {}).get("seed_policy")
        == spec["replication"]["seed_policy"]
        for rid in run_ids
    )
    checks.append(
        _check(
            "seed_policy",
            "deterministic audit: seeds=[] and the frozen seed policy recorded in every "
            "manifest; no duplicated or missing seeds possible",
            seed_ok,
        )
    )

    raw_summary_ok = True
    rs_detail = {}
    for rid in run_ids:
        rdir = os.path.join(EXP_DIR, "runs", rid)
        with open(os.path.join(rdir, "raw-result.json"), "r", encoding="utf-8") as fh:
            raw = json.load(fh)
        with open(os.path.join(rdir, "summary.json"), "r", encoding="utf-8") as fh:
            summ = json.load(fh)
        agree = summ["metrics"].get("controls", {}) == raw.get("controls", {}) and summ[
            "valid"
        ] == raw.get("valid")
        if "admissible_operation_count" in raw:
            agree = agree and summ["metrics"].get("admissible_operation_count") == raw[
                "admissible_operation_count"
            ]
        rs_detail[rid] = {"agree": agree}
        raw_summary_ok &= agree
        for a, b in (
            ("raw-result.json", "raw.json"),
            ("stdout.log", "stdout.txt"),
            ("stderr.log", "stderr.txt"),
        ):
            with open(os.path.join(rdir, a), "rb") as fh:
                ca = fh.read()
            with open(os.path.join(rdir, b), "rb") as fh:
                cb = fh.read()
            raw_summary_ok &= ca == cb
        rs_detail[rid]["aliases_byte_identical"] = True
    checks.append(
        _check(
            "raw_summary_agreement",
            "summary.json metrics agree with raw-result.json in every run; naming "
            "aliases byte-identical",
            raw_summary_ok,
            rs_detail,
        )
    )

    ctrl_ok = True
    ctrl_detail = {}
    for rid in run_ids:
        rdir = os.path.join(EXP_DIR, "runs", rid)
        with open(os.path.join(rdir, "raw-result.json"), "r", encoding="utf-8") as fh:
            raw = json.load(fh)
        controls = raw.get("controls", {})
        ctrl_detail[rid] = controls
        ctrl_ok &= all(v == "pass" for v in controls.values())
    with open(os.path.join(EXP_DIR, "requirement_matrix.json"), "r", encoding="utf-8") as fh:
        matrix = json.load(fh)
    ctrl_ok &= matrix["replay_determinism"]["byte_identical"]
    ctrl_ok &= matrix["rejection_basis_coverage"] == 1.0
    ctrl_ok &= matrix["cell_count"] == 49
    ctrl_ok &= matrix["threshold_recomputation"]["pass"]
    ctrl_ok &= not matrix["undecidable_items"]
    checks.append(
        _check(
            "control_comparability",
            "all five frozen controls pass identically across runs; replay "
            "byte-identical; matrix 49/49; basis coverage 1.0; zero undecidable",
            ctrl_ok,
            {
                "runs": ctrl_detail,
                "replay_byte_identical": matrix["replay_determinism"]["byte_identical"],
                "rejection_basis_coverage": matrix["rejection_basis_coverage"],
                "cell_count": matrix["cell_count"],
                "threshold_recomputation_pass": matrix["threshold_recomputation"]["pass"],
                "undecidable_items": matrix["undecidable_items"],
            },
        )
    )

    artifact_list = [
        "experiments/EXP-SCR-002/specification.yaml",
        "experiments/EXP-SCR-002/sheet/apply_sheet.py",
        "experiments/EXP-SCR-002/sheet/calibration_receipt.json",
        "experiments/EXP-SCR-002/corpus_manifest.json",
        "experiments/EXP-SCR-002/requirement_matrix.json",
        "experiments/EXP-SCR-002/admission_decision.json",
        "experiments/EXP-SCR-002/implementation.md",
        "experiments/EXP-SCR-002/analysis.md",
        "experiments/EXP-SCR-002/execution-report.yaml",
        "ledger/hypotheses/H-SCR-002.yaml",
    ]
    art_missing = [p for p in artifact_list if not os.path.exists(os.path.join(REPO_ROOT, p))]
    checks.append(
        _check(
            "required_artifacts",
            "all required artifacts exist (run directories checked separately above); "
            "ledger/hypotheses/H-SCR-002.yaml is a pre-existing read-only input",
            not art_missing,
            {"missing": art_missing},
        )
    )

    result = {
        "generated_at": _now(),
        "checks": checks,
        "all_pass": all(c["result"] == "pass" for c in checks),
        "admissible_operation_count": matrix["admissible_operation_count"],
        "per_requirement_failure_counts": matrix["per_requirement_failure_counts"],
    }
    print(canonical_json(result))
    return 0 if result["all_pass"] else 1


# --------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    for name in ("run-a", "run-b", "run-c"):
        p = sub.add_parser(name)
        p.add_argument("--out", required=True)
    sub.add_parser("harness").add_argument("--run-id", required=True)
    sub.add_parser("validate")
    args = parser.parse_args()

    if args.cmd == "run-a":
        return cmd_run_a(args.out)
    if args.cmd == "run-b":
        return cmd_run_b(args.out)
    if args.cmd == "run-c":
        return cmd_run_c(args.out)
    if args.cmd == "harness":
        return cmd_harness(args.run_id)
    if args.cmd == "validate":
        return cmd_validate()
    return 1


if __name__ == "__main__":
    sys.exit(main())
