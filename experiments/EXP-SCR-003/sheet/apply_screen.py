#!/usr/bin/env python3
"""EXP-SCR-003 mechanical adjudicator.

Applies the frozen KN-OPEN-005 GGM-simulability screen (dedup against closed
representation classes plus the NS-TX-PRIME-001 transcript criterion N1-N5) to
the 8 frozen family items of experiments/EXP-SCR-003/specification.yaml.

The screen is deterministic and zero-compute beyond table construction:
  * every corpus artifact is read as git blob content at the pinned commit
    (never the working tree) and checked against the spec's hash manifest;
  * calibration fixtures are adjudicated BEFORE any corpus family verdict;
  * dedup classes are assigned only when the family name, the pinned BATCH-007
    eligibility token, the criterion_result token, and the named owner record
    tokens are all present in the hash-verified corpus; otherwise the family is
    recorded undecidable_with_reason (run inconclusive, never negative);
  * N1-N5 statuses follow the frozen routing table below; admission requires a
    family with no covering dedup owner and N1-N5 all passing;
  * separation (N1-N3) and usefulness (N4-N5) verdicts are recorded separately;
    an encoding_only_gap is never a source-bearing separation, and a
    simulable_closed verdict requires a pinned covering theorem.

Stages (one per planned run):
  freeze_and_calibrate            -> RUN-SCR-003-A
  dedup_classification            -> RUN-SCR-003-B
  ns_tx_application_and_aggregate -> RUN-SCR-003-C

Exit codes: 0 = stage complete (see result JSON validity), 2 = implementation
error, 3 = control failure (corpus integrity / calibration / incomplete table),
4 = inconclusive (undecidable_with_reason recorded).

stdlib + PyYAML only.
"""

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import yaml

PINNED_COMMIT = "b8af1551e45fbe4435745239d29f4d141eea3356"
EXP_DIR_REL = "experiments/EXP-SCR-003"
SPEC_REL = EXP_DIR_REL + "/specification.yaml"
CORPUS_MANIFEST_REL = EXP_DIR_REL + "/corpus_manifest.json"
CALIBRATION_RECEIPT_REL = EXP_DIR_REL + "/sheet/calibration_receipt.json"
FAMILY_TABLE_REL = EXP_DIR_REL + "/family_table.json"
ADMISSION_DECISION_REL = EXP_DIR_REL + "/admission_decision.json"

SCREEN_REPORT = ("coordination/goals/GOAL-CRYPTO-001/batches/BATCH-007/"
                 "tasks/TASK-20260723-701/ggm_screen_report.yaml")
SCREEN_NOTE = ("coordination/goals/GOAL-CRYPTO-001/batches/BATCH-007/"
               "tasks/TASK-20260723-701/ggm_simulability_note.md")
THM = "research/THM_JETBARRIER1.md"
P1547_GATE = "ideas/artifacts/ECDLP-IDEA-004/p1547_prime_to_p_jet_coordinate_gate.md"
IDEA268 = ("ideas/rejected/"
           "ECDLP-IDEA-268_multiplicity_code_hasse_jet_local_lift_hypothesis.md")
FINDING = "ledger/FINDING-PF-IC-001.md"
EV_EQJ = "ledger/EV-EQJ-001.yaml"
EV_TTN = "ledger/EV-TTN-001.yaml"
EV_JET = "ledger/EV-JET-001.yaml"
EV_JETB = "ledger/EV-JETB-001.yaml"

# ---------------------------------------------------------------------------
# Frozen routing table.
#
# Per family: the eligibility token and criterion_result token that the pinned
# BATCH-007 screen report must carry, the owner-record files and tokens that
# must be present in the hash-verified corpus, and the frozen N1-N5 status
# bundle. Consistency with the spec's expected_dedup label is checked through
# DEDUP_CONSISTENCY; anything else yields undecidable_with_reason.
# ---------------------------------------------------------------------------

NOT_SCORED_CLOSED = "not_scored_family_closed_by_dedup"

FAMILY_ROUTING = {
    "F1": {
        "eligibility": "prior_audited_not_remaining",
        "criterion_result": "fails_NS_TX_transcript_gap",
        "owner_files": [(THM, ["T2", "T4", "Hasse", "simulat"])],
        "covering_theorem": "THM-JETBARRIER1",
        "n1": "pass_oracle_answers_factor_through_public_data",
        "n2": "pass_relabelling_unaffected_by_public_answers",
        "n3": "simulable_closed",
        "n4": NOT_SCORED_CLOSED,
        "n5": NOT_SCORED_CLOSED,
        "separation": "simulable_closed",
        "usefulness": NOT_SCORED_CLOSED,
        "notes": ("All-order public Hasse-Schmidt simulation (T2/T4); zero "
                  "added group-oracle queries."),
    },
    "F2": {
        "eligibility": "prior_audited_not_remaining",
        "criterion_result": "fails_NS_TX_transcript_gap",
        "owner_files": [(THM, ["T1.3", "T4", "Hasse"])],
        "covering_theorem": "THM-JETBARRIER1",
        "n1": "pass_oracle_answers_factor_through_public_data",
        "n2": "pass_relabelling_unaffected_by_public_answers",
        "n3": "simulable_closed",
        "n4": NOT_SCORED_CLOSED,
        "n5": NOT_SCORED_CLOSED,
        "separation": "simulable_closed",
        "usefulness": NOT_SCORED_CLOSED,
        "notes": ("Public affine/algebraic constraints are public jet-scheme "
                  "equations (T1.3/T4)."),
    },
    "F3": {
        "eligibility": "prior_audited_not_remaining",
        "criterion_result": "no_nonzero_order_N_relation_channel",
        "owner_files": [(P1547_GATE, ["additive", "prime-to-p"])],
        "covering_theorem": "P1547",
        "n1": "pass_additive_channel_no_order_N_relation",
        "n2": "pass_relabelling_unaffected_by_public_answers",
        "n3": "simulable_closed",
        "n4": NOT_SCORED_CLOSED,
        "n5": NOT_SCORED_CLOSED,
        "separation": "simulable_closed",
        "usefulness": NOT_SCORED_CLOSED,
        "notes": ("Additive-channel boundary: closure is scoped to the "
                  "homomorphic additive channel only; it is not extended to "
                  "nonlinear cocycles, multi-point predicates, torsors, or "
                  "branch-selection distributions (F4 remains a distinct "
                  "uninstantiated residual)."),
    },
    "F4": {
        "eligibility": "uninstantiated_residual",
        "criterion_result": "cannot_apply_without_oracle",
        "owner_files": [(P1547_GATE, ["nonadditive", "unclassified"])],
        "covering_theorem": None,
        "n1": "cannot_apply_without_oracle",
        "n2": "not_reached",
        "n3": "not_reached",
        "n4": "not_reached",
        "n5": "not_reached",
        "separation": "separation_not_certified",
        "usefulness": "not_scored_no_oracle",
        "notes": ("P1547 names a nonadditive invariant only as an unclassified "
                  "possibility; no typed oracle exists to test. Recorded, not "
                  "discarded."),
    },
    "F5": {
        "eligibility": "model_seam_not_new_family",
        "criterion_result": "encoding_only_gap",
        "owner_files": [(THM, ["T6", "encoding"])],
        "covering_theorem": None,
        "n1": "seam_oracle_restores_concrete_encoding",
        "n2": "not_scored_model_seam",
        "n3": "encoding_only_gap",
        "n4": "fail_raw_coordinate_no_occurrence_relation",
        "n5": "not_scored_model_seam",
        "separation": "encoding_only_gap",
        "usefulness": "fail_n4_raw_coordinate",
        "notes": ("T6: non-generic by definition (restores the concrete curve "
                  "encoding); no k-dependent advantage; never recorded as a "
                  "source-bearing separation."),
    },
    "F6": {
        "eligibility": "outside_prime_field_scope",
        "criterion_result": "out_of_scope",
        "owner_files": [(SCREEN_NOTE, ["Weil-restriction", "G2"])],
        "covering_theorem": None,
        "n1": "not_scored_outside_prime_field_scope",
        "n2": "not_scored_outside_prime_field_scope",
        "n3": "not_scored_outside_prime_field_scope",
        "n4": "not_scored_outside_prime_field_scope",
        "n5": "not_scored_outside_prime_field_scope",
        "separation": "out_of_scope_not_scored",
        "usefulness": "out_of_scope_not_scored",
        "notes": ("G2 extension-field descent seam; a prime field has no proper "
                  "subfield, so it is outside the frozen prime-field scope."),
    },
    "F7": {
        "eligibility": "prior_rejected_not_remaining",
        "criterion_result": "hidden_source_oracle",
        "owner_files": [(IDEA268, ["multiplicity", "Hasse", "codeword"])],
        "covering_theorem": None,
        "n1": "fail_hidden_source_bearing_advice",
        "n2": "not_scored_prior_rejection",
        "n3": "not_scored_prior_rejection",
        "n4": "not_scored_prior_rejection",
        "n5": "not_scored_prior_rejection",
        "separation": "closed_by_prior_rejection",
        "usefulness": "not_scored_prior_rejection",
        "notes": ("ECDLP-IDEA-268 requires a hidden source-sensitive codeword "
                  "oracle and exact source lift; rejected, not remaining."),
    },
    "F8": {
        "eligibility": "prior_audited_not_reopened",
        "criterion_result": "no_new_transcript_criterion",
        "owner_files": [(FINDING, ["S-unit", "pairing", "trace-zero", "torsor"]),
                        (EV_EQJ, ["EV-EQJ-001"]),
                        (EV_TTN, ["EV-TTN-001"])],
        "covering_theorem": "FINDING-PF-IC-001",
        "n1": "pass_covered_screens_no_new_oracle",
        "n2": NOT_SCORED_CLOSED,
        "n3": "simulable_closed",
        "n4": NOT_SCORED_CLOSED,
        "n5": NOT_SCORED_CLOSED,
        "separation": "simulable_closed",
        "usefulness": NOT_SCORED_CLOSED,
        "notes": ("FINDING-PF-IC-001 screens (nets, S-units, pairings, "
                  "ramification, trace-zero, split-Jacobian, torsor, "
                  "endpoint-aggregation) plus EV-EQJ-001 and EV-TTN-001 "
                  "exclusions; no new source-bearing transcript criterion."),
    },
}

# Spec expected_dedup label vs pinned-report eligibility token.
DEDUP_CONSISTENCY = {
    ("prior_audited", "prior_audited_not_remaining"),
    ("prior_audited_not_reopened", "prior_audited_not_reopened"),
    ("uninstantiated_residual", "uninstantiated_residual"),
    ("model_seam_not_new_family", "model_seam_not_new_family"),
    ("outside_prime_field_scope", "outside_prime_field_scope"),
    ("prior_rejected_not_remaining", "prior_rejected_not_remaining"),
}

# ---------------------------------------------------------------------------
# Calibration fixture declarations. These instantiate the frozen fixture
# descriptions in specification.yaml; calibration proves the sheet maps them
# to the pre-declared verdicts before any corpus family is adjudicated.
# CAL-FAIL-SCR-003 is non-synthetic: its declaration is anchored to the
# hash-verified corpus records EV-JET-001 / EV-JETB-001 with covering theorem
# THM-JETBARRIER1.
# ---------------------------------------------------------------------------

FIXTURE_DECLS = {
    "CAL-PASS-SCR-003": {
        "covered_by_dedup": False,
        "corpus_anchors": [],
        "oracle": {"typed_io": True, "selection_law_declared": True,
                   "hidden_source_or_target_fitted_advice": False},
        "relabelling": {"proved_for_frozen_query_sequence": True,
                        "side_inputs_named": ["base_simulator_side_information"]},
        "gap": {"factors_through_public": False, "covering_theorem": None,
                "encoding_only": False, "epsilon": 1.0,
                "epsilon_at_least_inverse_polylog": True,
                "exceeds_collision_term": True,
                "deterministic_distinct_verified_outputs": True},
        "relation": {"exact_signed_occurrence_transcript": True,
                     "certified_miss": False,
                     "fixed_public_factor_deck": True,
                     "endpoint": "known_log"},
        "ledger": {"tau": 0.25, "lambda": 0.44, "mu": 0.44,
                   "all_terms_assigned": True},
    },
    "CAL-FAIL-SCR-003": {
        "covered_by_dedup": False,
        "corpus_anchors": [EV_JET, EV_JETB],
        "oracle": {"typed_io": True, "selection_law_declared": True,
                   "hidden_source_or_target_fitted_advice": False},
        "relabelling": {"proved_for_frozen_query_sequence": True,
                        "side_inputs_named": ["public_curve_equation",
                                              "formal_expressions",
                                              "equality_pattern"]},
        "gap": {"factors_through_public": True,
                "covering_theorem": "THM-JETBARRIER1",
                "encoding_only": False, "epsilon": 0.0,
                "epsilon_at_least_inverse_polylog": False,
                "exceeds_collision_term": False,
                "deterministic_distinct_verified_outputs": False},
        "relation": {"exact_signed_occurrence_transcript": False,
                     "certified_miss": False,
                     "fixed_public_factor_deck": False,
                     "endpoint": None},
        "ledger": {"tau": None, "lambda": None, "mu": None,
                   "all_terms_assigned": False},
    },
    "CAL-SPLIT-SCR-003": {
        "covered_by_dedup": False,
        "corpus_anchors": [],
        "oracle": {"typed_io": True, "selection_law_declared": True,
                   "hidden_source_or_target_fitted_advice": False},
        "relabelling": {"proved_for_frozen_query_sequence": True,
                        "side_inputs_named": ["base_simulator_side_information"]},
        "gap": {"factors_through_public": False, "covering_theorem": None,
                "encoding_only": False, "epsilon": 1.0,
                "epsilon_at_least_inverse_polylog": True,
                "exceeds_collision_term": True,
                "deterministic_distinct_verified_outputs": True},
        "relation": {"exact_signed_occurrence_transcript": False,
                     "certified_miss": False,
                     "fixed_public_factor_deck": False,
                     "endpoint": None},
        "ledger": {"tau": None, "lambda": None, "mu": None,
                   "all_terms_assigned": False},
    },
}

# Machine-checkable form of each fixture's pre-declared expected verdict.
FIXTURE_EXPECTED_CHECKS = {
    "CAL-PASS-SCR-003": lambda r: r["verdict"] == "ADMIT",
    "CAL-FAIL-SCR-003": lambda r: (r["verdict"] == "simulable_closed"
                                   and r["n3"] == "simulable_closed"),
    "CAL-SPLIT-SCR-003": lambda r: (r["separation_verdict"] == "separation_certified"
                                    and r["n3_epsilon"] == 1.0
                                    and r["n4"] == "fail"),
}


# ---------------------------------------------------------------------------
# Corpus access: git blob content at the pinned commit, never the working tree.
# ---------------------------------------------------------------------------

def git_blob_sha1(repo_root, path):
    proc = subprocess.run(["git", "rev-parse", "%s:%s" % (PINNED_COMMIT, path)],
                          cwd=repo_root, capture_output=True, text=True)
    if proc.returncode != 0:
        return None
    return proc.stdout.strip()


def git_blob_bytes(repo_root, sha1):
    proc = subprocess.run(["git", "cat-file", "blob", sha1],
                          cwd=repo_root, capture_output=True)
    if proc.returncode != 0:
        return None
    return proc.stdout


def verify_corpus(repo_root, spec):
    """Check every hash-manifest path: blob sha1 match + sha256 of content."""
    entries = []
    missing = []
    mismatches = []
    for item in spec["experiment"]["inputs"]["corpus_snapshot"]["hash_manifest"]:
        path = item["path"]
        expected = item["git_blob_sha1"]
        actual = git_blob_sha1(repo_root, path)
        entry = {"path": path, "expected_git_blob_sha1": expected,
                 "actual_git_blob_sha1": actual, "sha1_match": actual == expected,
                 "sha256_of_blob_content": None, "content_bytes": None}
        if actual is None:
            missing.append(path)
            entries.append(entry)
            continue
        content = git_blob_bytes(repo_root, actual)
        if content is None:
            missing.append(path)
            entries.append(entry)
            continue
        entry["sha256_of_blob_content"] = hashlib.sha256(content).hexdigest()
        entry["content_bytes"] = len(content)
        if actual != expected:
            mismatches.append(path)
        entries.append(entry)
    return {"pinned_commit": PINNED_COMMIT, "entries": entries,
            "missing": missing, "mismatches": mismatches,
            "entry_count": len(entries),
            "pass": (not missing) and (not mismatches)}


def corpus_text(repo_root, corpus, path):
    """Decoded blob content for a verified corpus path (None if unverified)."""
    for entry in corpus["entries"]:
        if entry["path"] == path and entry["sha1_match"]:
            blob = git_blob_bytes(repo_root, entry["actual_git_blob_sha1"])
            if blob is not None:
                return blob.decode("utf-8", errors="replace")
    return None


def crosscheck_manifest(repo_root, corpus):
    """Re-bind stage B/C to RUN-A's corpus_manifest.json (sha256 equality)."""
    mpath = Path(repo_root) / CORPUS_MANIFEST_REL
    if not mpath.is_file():
        return {"present": False, "consistent": False,
                "reason": "corpus_manifest.json missing (RUN-SCR-003-A required first)"}
    recorded = json.loads(mpath.read_text(encoding="utf-8"))
    if not recorded.get("pass"):
        return {"present": True, "consistent": False,
                "reason": "recorded corpus manifest is not pass"}
    rec = {e["path"]: e["sha256_of_blob_content"] for e in recorded["entries"]}
    fresh = {e["path"]: e["sha256_of_blob_content"] for e in corpus["entries"]}
    consistent = rec == fresh and recorded.get("pinned_commit") == PINNED_COMMIT
    return {"present": True, "consistent": consistent,
            "reason": None if consistent else "sha256 drift vs RUN-SCR-003-A manifest"}


# ---------------------------------------------------------------------------
# NS-TX-PRIME-001 screen machine (fixtures and any future declared family).
# ---------------------------------------------------------------------------

def evaluate_declaration(decl, covering_theorems_verified):
    """Apply N1-N5 to a structured oracle declaration. Mechanical only."""
    out = {"n1": None, "n2": None, "n3": None, "n3_epsilon": None,
           "n4": None, "n5": None, "usefulness_failed_clauses": [],
           "separation_verdict": None, "usefulness_verdict": None,
           "verdict": None}

    oracle = decl["oracle"]
    if not oracle["typed_io"]:
        out["n1"] = "cannot_apply_without_oracle"
    elif oracle["hidden_source_or_target_fitted_advice"]:
        out["n1"] = "fail_hidden_source_bearing_advice"
    elif not oracle["selection_law_declared"]:
        out["n1"] = "cannot_apply_without_oracle"
    else:
        out["n1"] = "pass"
    if out["n1"] != "pass":
        for k in ("n2", "n3", "n4", "n5"):
            out[k] = "not_reached"
        out["separation_verdict"] = out["n1"]
        out["usefulness_verdict"] = "not_evaluated"
        out["verdict"] = "not_admitted_" + out["n1"]
        return out

    rel = decl["relabelling"]
    out["n2"] = ("pass" if rel["proved_for_frozen_query_sequence"]
                 and rel["side_inputs_named"] else "fail")
    if out["n2"] != "pass":
        for k in ("n3", "n4", "n5"):
            out[k] = "not_reached"
        out["separation_verdict"] = "relabelling_not_proved"
        out["usefulness_verdict"] = "not_evaluated"
        out["verdict"] = "not_admitted_relabelling_not_proved"
        return out

    gap = decl["gap"]
    if gap["factors_through_public"]:
        theorem = gap["covering_theorem"]
        if theorem and theorem in covering_theorems_verified:
            out["n3"] = "simulable_closed"
        else:
            # Never a proved simulation unless a pinned covering theorem
            # supplies it.
            out["n3"] = "separation_not_certified"
    elif gap["encoding_only"]:
        out["n3"] = "encoding_only_gap"
    elif (gap["epsilon_at_least_inverse_polylog"] and gap["exceeds_collision_term"]
          and gap["epsilon"] and gap["epsilon"] > 0):
        out["n3"] = "separation_certified"
        out["n3_epsilon"] = gap["epsilon"]
    else:
        out["n3"] = "separation_not_certified"
    out["separation_verdict"] = out["n3"]

    relation = decl["relation"]
    rel_ok = ((relation["exact_signed_occurrence_transcript"]
               or relation["certified_miss"])
              and relation["fixed_public_factor_deck"]
              and relation["endpoint"] in ("known_log",
                                           "fresh_scalar_blind_masked_target"))
    out["n4"] = "pass" if rel_ok else "fail"

    ledger = decl["ledger"]
    n5_ok = (ledger["all_terms_assigned"]
             and ledger["tau"] is not None and ledger["tau"] <= 0.25
             and ledger["lambda"] is not None and ledger["lambda"] <= 0.45
             and ledger["mu"] is not None and ledger["mu"] <= 0.45)
    out["n5"] = "pass" if n5_ok else "fail"

    failed = [k for k in ("n4", "n5") if out[k] != "pass"]
    out["usefulness_failed_clauses"] = failed
    out["usefulness_verdict"] = "pass" if not failed else "fail"

    all_pass = all(out[k] == "pass" for k in ("n1", "n2", "n3", "n4", "n5"))
    # n3 "pass" is not among the n3 vocabulary; admission requires a certified
    # source-bearing gap, i.e. n3 == separation_certified.
    admitted = (not decl["covered_by_dedup"]) and out["n3"] == "separation_certified" \
        and out["n4"] == "pass" and out["n5"] == "pass"
    if admitted:
        out["verdict"] = "ADMIT"
    elif out["n3"] == "simulable_closed":
        out["verdict"] = "simulable_closed"
    elif out["n3"] == "encoding_only_gap":
        out["verdict"] = "encoding_only_gap"
    elif out["n3"] == "separation_certified" and failed:
        out["verdict"] = "separation_certified_usefulness_rejected"
    else:
        out["verdict"] = "not_admitted_" + out["n3"]
    return out


def run_calibration(repo_root, spec, corpus):
    """Adjudicate the 3 frozen fixtures BEFORE any corpus family verdict."""
    covering = set()
    for path, theorem in ((THM, "THM-JETBARRIER1"), (FINDING, "FINDING-PF-IC-001")):
        if corpus_text(repo_root, corpus, path) is not None:
            covering.add(theorem)
    fixtures = []
    matches = 0
    for fspec in spec["experiment"]["inputs"]["calibration_fixtures"]:
        fid = fspec["id"]
        decl = FIXTURE_DECLS[fid]
        anchors_ok = all(corpus_text(repo_root, corpus, p) is not None
                         for p in decl["corpus_anchors"])
        if not anchors_ok:
            result = {"verdict": "instrument_failure_corpus_anchor_unverified"}
            match = False
        else:
            result = evaluate_declaration(decl, covering)
            match = bool(FIXTURE_EXPECTED_CHECKS[fid](result))
        matches += 1 if match else 0
        fixtures.append({"id": fid, "kind": fspec["kind"],
                         "synthetic_fixture": fspec["synthetic_fixture"],
                         "expected_verdict": fspec["expected_verdict"],
                         "observed": result, "anchors_verified": anchors_ok,
                         "match": match})
    accuracy = matches / len(fixtures) if fixtures else 0.0
    return {"fixtures": fixtures, "expected_count": len(fixtures),
            "matched_count": matches, "accuracy": accuracy,
            "all_pass": matches == len(fixtures) and len(fixtures) == 3,
            "ran_before_any_corpus_family_verdict": True}


# ---------------------------------------------------------------------------
# Dedup adjudication over the frozen family index.
# ---------------------------------------------------------------------------

def run_dedup(repo_root, spec, corpus):
    report_text = corpus_text(repo_root, corpus, SCREEN_REPORT)
    assignments = []
    undecidable = []
    items = spec["experiment"]["inputs"]["audit_item_index"]["items"]
    for item in items:
        fid = item["id"]
        routing = FAMILY_ROUTING[fid]
        reasons = []
        checks = []

        if report_text is None:
            reasons.append("pinned screen report unverified in corpus")
        else:
            for token in (item["name"], routing["eligibility"],
                          routing["criterion_result"]):
                present = token in report_text
                checks.append({"path": SCREEN_REPORT, "token": token,
                               "present": present})
                if not present:
                    reasons.append("token %r absent from pinned screen report"
                                   % token)

        if (item["expected_dedup"], routing["eligibility"]) not in DEDUP_CONSISTENCY:
            reasons.append("spec expected_dedup %r inconsistent with pinned "
                           "eligibility %r" % (item["expected_dedup"],
                                               routing["eligibility"]))

        for path, tokens in routing["owner_files"]:
            text = corpus_text(repo_root, corpus, path)
            for token in tokens:
                present = (text is not None) and (token in text)
                checks.append({"path": path, "token": token, "present": present})
                if not present:
                    reasons.append("owner token %r absent from %s" % (token, path))

        if reasons:
            entry = {"id": fid, "name": item["name"],
                     "dedup_class": "undecidable_with_reason",
                     "dedup_owner": item["expected_owner"],
                     "owner_verified": False, "evidence_checks": checks,
                     "undecidable_reasons": reasons,
                     "admitted": False}
            undecidable.append({"id": fid, "reasons": reasons})
        else:
            entry = {"id": fid, "name": item["name"],
                     "dedup_class": item["expected_dedup"],
                     "dedup_owner": item["expected_owner"],
                     "screen_report_eligibility": routing["eligibility"],
                     "criterion_result": routing["criterion_result"],
                     "owner_verified": True, "evidence_checks": checks,
                     "admitted": False}
        assignments.append(entry)

    complete = (len([a for a in assignments
                     if a["dedup_class"] != "undecidable_with_reason"])
                == len(items) == 8)
    return {"assignments": assignments, "undecidable": undecidable,
            "assigned_count": len(assignments) - len(undecidable),
            "item_count": len(items), "complete": complete}


def build_family_entries(repo_root, spec, corpus):
    """Full family table content (dedup + N1-N5 statuses). Deterministic."""
    dedup = run_dedup(repo_root, spec, corpus)
    families = []
    for a in dedup["assignments"]:
        fid = a["id"]
        entry = dict(a)
        if a["dedup_class"] == "undecidable_with_reason":
            entry.update({"n1": "undecidable_with_reason",
                          "n2": "undecidable_with_reason",
                          "n3": "undecidable_with_reason",
                          "n4": "undecidable_with_reason",
                          "n5": "undecidable_with_reason",
                          "separation_verdict": "undecidable_with_reason",
                          "usefulness_verdict": "undecidable_with_reason",
                          "source_bearing_separation": False,
                          "covering_theorem": None})
        else:
            routing = FAMILY_ROUTING[fid]
            entry.update({
                "n1": routing["n1"], "n2": routing["n2"], "n3": routing["n3"],
                "n4": routing["n4"], "n5": routing["n5"],
                "separation_verdict": routing["separation"],
                "usefulness_verdict": routing["usefulness"],
                "source_bearing_separation": False,
                "covering_theorem": routing["covering_theorem"],
                "notes": routing["notes"],
            })
            # Admission gate: only a family with no covering dedup owner
            # proceeds to N1-N5 admission scoring. Every frozen family here
            # carries a verified named owner, so none is admitted.
            entry["admitted"] = False
        families.append(entry)
    residuals = [
        {"id": p["id"], "status": p["status"], "scored_for_admission": False}
        for p in spec["experiment"]["inputs"]["residual_placeholders"]["placeholders"]
    ]
    return {"families": families, "residuals": residuals,
            "undecidable": dedup["undecidable"]}


def canonical_bytes(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def tail_checks(families, replay_identical):
    simulable_ok = all(
        (f["separation_verdict"] != "simulable_closed")
        or (f["n3"] == "simulable_closed" and f["covering_theorem"])
        for f in families)
    encoding_ok = all(
        (f["n3"] != "encoding_only_gap")
        or (not f["source_bearing_separation"] and not f["admitted"])
        for f in families)
    no_admitted_simulable = all(
        not (f["admitted"] and f["separation_verdict"] == "simulable_closed")
        for f in families)
    return {
        "split_gate_no_simulable_from_usefulness_failure": simulable_ok,
        "split_gate_encoding_only_never_source_bearing": encoding_ok,
        "no_admitted_family_recorded_simulable": no_admitted_simulable,
        "dual_pass_byte_identical": replay_identical,
        "pass": simulable_ok and encoding_ok and no_admitted_simulable
                and replay_identical,
    }


def family_metrics(content):
    families = content["families"]
    return {
        "admitted_family_count": sum(1 for f in families if f["admitted"]),
        "dedup_class_assignment_complete":
            sum(1 for f in families if f["owner_verified"]) / len(families),
        "encoding_only_gap_flags":
            [f["id"] for f in families if f["n3"] == "encoding_only_gap"],
        "separation_not_certified":
            [{"id": f["id"], "n1": f["n1"]} for f in families
             if f["separation_verdict"] == "separation_not_certified"],
        "undecidable_items": content["undecidable"],
        "residuals_carried": len(content["residuals"]),
    }


# ---------------------------------------------------------------------------
# Stage drivers.
# ---------------------------------------------------------------------------

def load_spec(repo_root):
    with open(Path(repo_root) / SPEC_REL, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def write_json(repo_root, rel, obj):
    path = Path(repo_root) / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=False) + "\n",
                    encoding="utf-8")
    return path


def stage_freeze_and_calibrate(repo_root, spec):
    corpus = verify_corpus(repo_root, spec)
    manifest = dict(corpus)
    manifest["control"] = "CTRL-CORPUS-INTEGRITY"
    manifest["pass_condition"] = "zero missing paths and zero hash mismatches"
    write_json(repo_root, CORPUS_MANIFEST_REL, manifest)
    if not corpus["pass"]:
        return ({"stage": "freeze_and_calibrate", "corpus": corpus_summary(corpus),
                  "calibration": None, "valid": False,
                  "invalid_reason": "corpus_integrity_failed"}, 3)

    calibration = run_calibration(repo_root, spec, corpus)
    receipt = dict(calibration)
    receipt["control"] = "CTRL-SHEET-CALIBRATION"
    receipt["pass_condition"] = ("CAL-PASS ADMIT, CAL-FAIL simulable_closed, "
                                 "CAL-SPLIT N3-certified plus N4-rejected")
    write_json(repo_root, CALIBRATION_RECEIPT_REL, receipt)
    if not calibration["all_pass"]:
        return ({"stage": "freeze_and_calibrate", "corpus": corpus_summary(corpus),
                  "calibration": calibration, "valid": False,
                  "invalid_reason": "calibration_failed_instrument_unsound"}, 3)
    return ({"stage": "freeze_and_calibrate", "corpus": corpus_summary(corpus),
              "calibration": calibration, "valid": True,
              "invalid_reason": None}, 0)


def corpus_summary(corpus):
    return {"pinned_commit": corpus["pinned_commit"],
            "entry_count": corpus["entry_count"],
            "missing": corpus["missing"], "mismatches": corpus["mismatches"],
            "pass": corpus["pass"]}


def stage_dedup_classification(repo_root, spec):
    corpus = verify_corpus(repo_root, spec)
    rebind = crosscheck_manifest(repo_root, corpus)
    if not corpus["pass"] or not rebind["consistent"]:
        return ({"stage": "dedup_classification", "corpus": corpus_summary(corpus),
                  "manifest_rebind": rebind, "dedup": None, "valid": False,
                  "invalid_reason": "corpus_integrity_failed"}, 3)
    dedup = run_dedup(repo_root, spec, corpus)
    if dedup["undecidable"]:
        # Stage stop rule: inconclusive (not negative); undecidable_with_reason
        # is recorded per family.
        return ({"stage": "dedup_classification", "corpus": corpus_summary(corpus),
                  "manifest_rebind": rebind, "dedup": dedup, "valid": True,
                  "inconclusive": True,
                  "invalid_reason": None}, 4)
    return ({"stage": "dedup_classification", "corpus": corpus_summary(corpus),
              "manifest_rebind": rebind, "dedup": dedup, "valid": True,
              "inconclusive": False, "invalid_reason": None}, 0)


def stage_ns_tx_application_and_aggregate(repo_root, spec):
    corpus = verify_corpus(repo_root, spec)
    rebind = crosscheck_manifest(repo_root, corpus)
    if not corpus["pass"] or not rebind["consistent"]:
        return ({"stage": "ns_tx_application_and_aggregate",
                  "corpus": corpus_summary(corpus), "manifest_rebind": rebind,
                  "valid": False, "invalid_reason": "corpus_integrity_failed"}, 3)

    # CTRL-REPLAY-DETERMINISM: apply the frozen screen twice over the full
    # family index; the family tables must be byte-identical.
    pass1 = build_family_entries(repo_root, spec, corpus)
    pass2 = build_family_entries(repo_root, spec, corpus)
    pass1_bytes = canonical_bytes(pass1)
    pass2_bytes = canonical_bytes(pass2)
    replay_identical = pass1_bytes == pass2_bytes

    families = pass1["families"]
    checks = tail_checks(families, replay_identical)
    metrics = family_metrics(pass1)

    replay = {"passes": 2,
              "pass1_sha256": hashlib.sha256(pass1_bytes).hexdigest(),
              "pass2_sha256": hashlib.sha256(pass2_bytes).hexdigest(),
              "identical": replay_identical,
              "verdict_flips_between_passes": 0 if replay_identical else None}

    table = {
        "experiment_id": "EXP-SCR-003",
        "hypothesis_id": "H-SCR-003",
        "screen": {"dedup_rule": "frozen specification v1 dedup classes",
                   "criterion": "NS-TX-PRIME-001"},
        "corpus": {"pinned_commit": PINNED_COMMIT,
                   "manifest": CORPUS_MANIFEST_REL,
                   "integrity": "pass"},
        "generated_by": EXP_DIR_REL + "/sheet/apply_screen.py",
        "families": families,
        "residuals": pass1["residuals"],
        "metrics": metrics,
        "replay": replay,
        "tail_checks": checks,
    }

    incomplete = len(families) < 8
    if incomplete and not pass1["undecidable"]:
        return ({"stage": "ns_tx_application_and_aggregate",
                  "corpus": corpus_summary(corpus), "valid": False,
                  "invalid_reason": "family_table_incomplete"}, 3)
    if not replay_identical or not checks["pass"]:
        write_json(repo_root, FAMILY_TABLE_REL, table)
        return ({"stage": "ns_tx_application_and_aggregate",
                  "corpus": corpus_summary(corpus), "metrics": metrics,
                  "replay": replay, "tail_checks": checks, "valid": False,
                  "invalid_reason": "determinism_or_split_gate_failure"}, 3)

    write_json(repo_root, FAMILY_TABLE_REL, table)

    admitted = [f for f in families if f["admitted"]]
    falsification_observations = []
    for f in admitted:
        # Falsification-class observation, recorded verbatim (spec
        # falsification_criterion). No escalation by the Executor.
        falsification_observations.append({
            "family_id": f["id"], "name": f["name"],
            "observation_class": "falsification_candidate_unfiled_theorem_candidate",
            "n1": f["n1"], "n2": f["n2"], "n3": f["n3"],
            "n4": f["n4"], "n5": f["n5"],
            "separation_verdict": f["separation_verdict"],
            "usefulness_verdict": f["usefulness_verdict"]})

    decision = {
        "experiment_id": "EXP-SCR-003",
        "hypothesis_id": "H-SCR-003",
        "observation_only": True,
        "admitted_family_count": len(admitted),
        "admitted_families": [f["id"] for f in admitted],
        "decision_observation": ("zero_admitted_families_over_checked_frozen_corpus"
                                 if not admitted else
                                 "families_admitted_see_falsification_observations"),
        "falsification_class_observations": falsification_observations,
        "residuals_carried": pass1["residuals"],
        "scope_note": ("Scoped to the checked frozen representation corpus at "
                       "the pinned commit; per spec claim_tier_basis this is "
                       "neither a universal simulability theorem nor GGM "
                       "completeness. Observation only: no hypothesis status "
                       "is asserted by this record."),
    }
    write_json(repo_root, ADMISSION_DECISION_REL, decision)

    return ({"stage": "ns_tx_application_and_aggregate",
              "corpus": corpus_summary(corpus), "manifest_rebind": rebind,
              "metrics": metrics, "replay": replay, "tail_checks": checks,
              "admitted_family_count": len(admitted),
              "falsification_class_observations": falsification_observations,
              "inconclusive": bool(pass1["undecidable"]),
              "valid": True, "invalid_reason": None}, 0)


STAGES = {
    "freeze_and_calibrate": stage_freeze_and_calibrate,
    "dedup_classification": stage_dedup_classification,
    "ns_tx_application_and_aggregate": stage_ns_tx_application_and_aggregate,
}


def main(argv=None):
    parser = argparse.ArgumentParser(description="EXP-SCR-003 frozen screen adjudicator")
    parser.add_argument("--repo-root", default=str(Path(__file__).resolve().parents[3]))
    parser.add_argument("--stage", required=True, choices=sorted(STAGES))
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--result-path", required=True,
                        help="repo-relative path for the machine-readable result")
    args = parser.parse_args(argv)

    repo_root = str(Path(args.repo_root).resolve())
    result_path = Path(repo_root) / args.result_path

    try:
        spec = load_spec(repo_root)
        result, code = STAGES[args.stage](repo_root, spec)
    except Exception as exc:  # implementation error: recorded, never a result
        result = {"stage": args.stage, "valid": False,
                  "invalid_reason": "implementation_error",
                  "error": "%s: %s" % (type(exc).__name__, exc)}
        code = 2

    result["run_id"] = args.run_id
    result["experiment_id"] = "EXP-SCR-003"
    result["pinned_commit"] = PINNED_COMMIT
    result_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.write_text(json.dumps(result, indent=2, sort_keys=False) + "\n",
                           encoding="utf-8")
    print(json.dumps({"run_id": args.run_id, "stage": args.stage,
                      "exit_code": code, "valid": result.get("valid"),
                      "invalid_reason": result.get("invalid_reason")},
                     sort_keys=True))
    return code


if __name__ == "__main__":
    sys.exit(main())
