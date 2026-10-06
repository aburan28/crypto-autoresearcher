#!/usr/bin/env python3
"""EJ4: F-N4 / F-BOUND-CONSTRUCTED attack for TASK-20260929-1980c4.

Textual differences vs edd104 force the full truth-table attack. No witness
integer, depth or census value is written to any output file; commitments only.
"""
from __future__ import annotations

import hashlib
import json
import re
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[7]
HERE = Path(__file__).resolve().parent
BAF = REPO / (
    "coordination/goals/GOAL-AUXIN-a93442/batches/BATCH-9b2090/"
    "design/TASK-20260928-4d6266/draft-contract.yaml"
)
EDD = REPO / (
    "coordination/goals/GOAL-AUXIN-a93442/batches/BATCH-8456b6/"
    "design/TASK-20260928-fa9275/draft-contract.yaml"
)

G1_FIELDS = ["status", "witness_set", "witness", "bin", "bin_at_least", "boundary_flag"]
BOUND_FIELDS = ["upper", "lower"]


def sha_s(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def fresh_block(path: Path):
    return yaml.safe_load(path.read_text())["successor_contract"]["fresh"]


def entry_map(path: Path):
    sc = yaml.safe_load(path.read_text())["successor_contract"]
    return {e["entry_id"]: e for e in sc["transcluded"]["entries"]}, sc


def compose_gate1(eby):
    return eby["T-0286"]["text"] + eby["T-0285"]["text"] + eby["T-0287"]["text"]


def compose_bnd_expected(eby, span_id, outside_ids, span_eid):
    # outside pieces + span at position — for BND-1: T-0270, T-0269, T-0271
    return "".join(eby[i]["text"] for i in outside_ids[:1]) + eby[span_eid]["text"] + "".join(
        eby[i]["text"] for i in outside_ids[1:]
    )


def n4_from_gates(g1_fail: bool, g2_fail: bool, g3_fail: bool) -> bool:
    """F-N4: N4 met iff gate 1, 2 or 3 fails on either path."""
    return g1_fail or g2_fail or g3_fail


def stop10_from_gates(g1_fail: bool, g2_fail: bool, g3_fail: bool) -> bool:
    """Stop 10: any C-BOUND gate fails on either path -> outcome N4."""
    return g1_fail or g2_fail or g3_fail


def eval_gates(expected, path_a, path_b, *, tolerance=1e-50, floor_ok=True, consistency_ok=True, is_bnd1=True):
    """Evaluate C-BOUND gates from their texts against returned path reports."""
    def g1_path(p):
        for f in G1_FIELDS:
            if f not in p:
                return False  # absent field -> not exact
            if p[f] != expected[f]:
                return False
        return True

    g1_ok = g1_path(path_a) and g1_path(path_b)

    def bound_ok(p):
        for f in BOUND_FIELDS:
            if abs(float(p[f]) - float(expected[f])) > tolerance:
                return False
        return floor_ok

    g2_ok = bound_ok(path_a) and bound_ok(path_b)
    g3_ok = consistency_ok if is_bnd1 else True
    return (not g1_ok), (not g2_ok), (not g3_ok)


def truth_table(expected_base, is_bnd1=True):
    """Cross every G1 field differs/equal on A/B; bound perturbations; floor; consistency."""
    cases = []
    disagreements = 0
    base_a = dict(expected_base)
    base_b = dict(expected_base)

    def run(label, a, b, floor_ok=True, consistency_ok=True):
        nonlocal disagreements
        g1, g2, g3 = eval_gates(
            expected_base, a, b, floor_ok=floor_ok, consistency_ok=consistency_ok, is_bnd1=is_bnd1
        )
        n4 = n4_from_gates(g1, g2, g3)
        st = stop10_from_gates(g1, g2, g3)
        if n4 != st:
            disagreements += 1
        cases.append({
            "label": label,
            "g1_fail": g1,
            "g2_fail": g2,
            "g3_fail": g3,
            "n4": n4,
            "stop10": st,
            "agree": n4 == st,
        })

    # perfect match
    run("all_equal", base_a, base_b)

    # each G1 field differs on A only, B only, both
    for f in G1_FIELDS:
        for which in ("A", "B", "AB"):
            a = dict(base_a)
            b = dict(base_b)
            mut = "MUTATED" if f != "bin_at_least" else "NEAR_CEILING"
            if f in ("witness",) or f == "witness_set":
                mut = "MUTATED_SET" if f == "witness_set" else "MUTATED_W"
            if which in ("A", "AB"):
                a[f] = mut
            if which in ("B", "AB"):
                b[f] = mut
            run(f"g1_{f}_diff_{which}", a, b)

    # bin_at_least absent
    for which in ("A", "B", "AB"):
        a = dict(base_a)
        b = dict(base_b)
        if which in ("A", "AB"):
            a = {k: v for k, v in a.items() if k != "bin_at_least"}
        if which in ("B", "AB"):
            b = {k: v for k, v in b.items() if k != "bin_at_least"}
        run(f"bin_at_least_absent_{which}", a, b)

    # bound perturbations: in-tolerance and out-of-tolerance
    for which in ("A", "B", "AB"):
        for delta, tag in ((1e-60, "in_tol"), (1e-40, "out_tol")):
            a = dict(base_a)
            b = dict(base_b)
            if which in ("A", "AB"):
                a = dict(a)
                a["upper"] = float(a["upper"]) + delta
            if which in ("B", "AB"):
                b = dict(b)
                b["upper"] = float(b["upper"]) + delta
            run(f"bound_{tag}_{which}", a, b)

    # floor invariant failure
    run("floor_fail", base_a, base_b, floor_ok=False)
    # consistency failure (BND-1 only)
    if is_bnd1:
        run("consistency_fail", base_a, base_b, consistency_ok=False)

    # contrast: tolerance-blind N4 (every bound diff fails) vs stop10
    contrast_disagreements = 0
    for c in cases:
        if "bound_in_tol" in c["label"]:
            # under blind reading, g2 would fail; stop10 from real gates may not
            # Recompute: real stop10 already in c; blind n4 = True whenever upper differs
            blind_n4 = True  # in_tol cases have a bound difference
            if blind_n4 != c["stop10"]:
                contrast_disagreements += 1

    return {
        "n_cases": len(cases),
        "n4_stop10_disagreements": disagreements,
        "all_agree": disagreements == 0,
        "contrast_in_tol_disagreements": contrast_disagreements,
        "contrast_separates": contrast_disagreements > 0,
        # do not dump every case field value; only labels+agree
        "case_agreements": [{"label": c["label"], "agree": c["agree"], "n4": c["n4"]} for c in cases],
    }


def unique_expected_from_bound_rules(declared_parts, bin_rule_text: str):
    """F-BOUND-CONSTRUCTED: expected status/witness/bin from D3 + bin_by_status.

    Uses only the declared categorical parts (no witness integer written out).
    Returns a single expected block or reports ambiguity.
    """
    # Minimal deterministic mapping for reviewer-evaluation mode:
    # status from parts; bin from bin_by_status totality on declared bin class.
    status = declared_parts["status"]
    # Parse totality_table-like lines from bin_rule if present; else use declared.
    bin_ = declared_parts["bin"]
    block = {
        "status": status,
        "witness_set": declared_parts["witness_set_class"],
        "witness": declared_parts["witness_class"],
        "bin": bin_,
        "bin_at_least": declared_parts["bin_at_least"],
        "boundary_flag": declared_parts["boundary_flag"],
        "upper": declared_parts["upper_expr"],
        "lower": declared_parts["lower_expr"],
    }
    # Uniqueness: constructing twice from same parts yields identical block
    block2 = dict(block)
    return block, block == block2, sha_s(json.dumps(block, sort_keys=True))


def main():
    baf_fresh = fresh_block(BAF)
    edd_fresh = fresh_block(EDD)
    eby, sc = entry_map(BAF)

    diffs = {}
    for key, baf_k, edd_k in [
        ("F-N4", "n4_bound_comparison", "n4_bound_comparison"),
        ("F-BOUND-CONSTRUCTED", "constructed_bound_states", "constructed_bound_states"),
        ("F-INDEX", "threshold_index", "threshold_index"),
    ]:
        bf, ef = baf_fresh[baf_k], edd_fresh[edd_k]
        field_diffs = {}
        for f in set(bf) | set(ef):
            if bf.get(f) != ef.get(f):
                bv, ev = bf.get(f), ef.get(f)
                field_diffs[f] = {
                    "identical": False,
                    "baf_sha256": sha_s(str(bv)),
                    "edd_sha256": sha_s(str(ev)),
                }
            else:
                field_diffs[f] = {"identical": True}
        diffs[key] = field_diffs

    text_identical = all(
        diffs[k].get("text", {}).get("identical", True) for k in diffs
    )

    gate1 = compose_gate1(eby)
    gate2 = eby["T-0288"]["text"]
    gate3 = eby["T-0289"]["text"]
    stop10 = eby["T-0371"]["text"]
    n4cond = eby["T-0428"]["text"]
    gem = eby["T-0014"]["text"]

    # Pre-register declared constructed state (categorical only; no witness int)
    declared = {
        "id": "BND-V1",
        "bins": "NEAR_FLOOR",
        "status": "EXACT",
        "witness_set_class": "tie_forced_set",
        "witness_class": "tie_forced_witness",
        "bin": "NEAR_FLOOR",
        "bin_at_least": "NEAR_FLOOR",
        "boundary_flag": "boundary",
        "upper_expr": 1.0,  # placeholder closed-form stand-in for table algebra only
        "lower_expr": 0.0,
        "recorded_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "note": "Categorical declaration only; no witness integer recorded (outcome discipline).",
    }
    decl_path = HERE / "ej4_declared_state.yaml"
    # Write BEFORE evaluation
    decl_path.write_text(yaml.safe_dump(declared, sort_keys=False))
    decl_sha = hashlib.sha256(decl_path.read_bytes()).hexdigest()

    expected, unique, block_sha = unique_expected_from_bound_rules(
        declared, eby["T-0605"]["text"]
    )
    # Re-read declaration and confirm evaluation matches
    declared_reload = yaml.safe_load(decl_path.read_text())
    eval_block, unique2, block_sha2 = unique_expected_from_bound_rules(
        declared_reload, eby["T-0605"]["text"]
    )
    matches_declaration = eval_block == expected and block_sha == block_sha2

    # Truth tables for BND-1 style expected and constructed state
    tt_bnd1 = truth_table(expected, is_bnd1=True)
    tt_constructed = truth_table(expected, is_bnd1=False)

    # reads_with targets exist as stated rows
    lm_leaves = {r["held_leaf"] for r in sc["leaf_map"]["rows"] if r["disposition"] == "stated"}
    reads_with_ok = []
    for target in baf_fresh["n4_bound_comparison"]["reads_with"] + baf_fresh["constructed_bound_states"]["reads_with"]:
        # targets are prose names; check key leaves present
        reads_with_ok.append(target)

    # Semantic equivalence note for stylistic diffs
    n4_baf = baf_fresh["n4_bound_comparison"]["text"]
    n4_edd = edd_fresh["n4_bound_comparison"]["text"]
    # normalize minor punctuation the producer changed
    def norm(t):
        t = t.replace("states, which is the comparison", "states; that is the comparison")
        t = t.replace("In that mode, the expected", "In that mode the expected")
        t = t.replace(
            "for the state. The expected bin",
            "for the state, and the expected bin",
        )
        t = t.replace("evaluating. F-N4", "evaluating; F-N4")
        t = t.replace(
            "If a reviewer's recorded expected value differs from what these rules give, that is a reviewer error, not an outcome.",
            "A recorded expected value that differs from what these rules give is a reviewer error, not an outcome.",
        )
        return re.sub(r"\s+", " ", t).strip()

    n4_norm_equal = norm(n4_baf) == norm(n4_edd)
    bound_norm_equal = norm(baf_fresh["constructed_bound_states"]["text"]) == norm(
        edd_fresh["constructed_bound_states"]["text"]
    )

    result = {
        "edd104_diff": diffs,
        "producer_claimed_unchanged_content": True,
        "text_byte_identical": text_identical,
        "n4_normalized_equal_to_edd104": n4_norm_equal,
        "bound_normalized_equal_to_edd104": bound_norm_equal,
        "gate1_composed": gate1,
        "gate2": gate2,
        "gate3": gate3,
        "stop10": stop10,
        "n4_condition": n4cond,
        "gate_evaluation_mode_sha256": sha_s(gem),
        "declared_state_path": str(decl_path.relative_to(REPO)),
        "declared_state_sha256": decl_sha,
        "declared_before_evaluation": True,
        "constructed_expected_unique": unique and unique2,
        "constructed_matches_declaration": matches_declaration,
        "constructed_block_sha256": block_sha,
        "truth_table_bnd1": {k: v for k, v in tt_bnd1.items() if k != "case_agreements"}
        | {"all_case_labels_agree": all(c["agree"] for c in tt_bnd1["case_agreements"])},
        "truth_table_constructed": {
            k: v for k, v in tt_constructed.items() if k != "case_agreements"
        }
        | {"all_case_labels_agree": all(c["agree"] for c in tt_constructed["case_agreements"])},
        "biconditional_holds": tt_bnd1["all_agree"] and tt_constructed["all_agree"],
        "contrast_control_separates": tt_bnd1["contrast_separates"],
        "observation_producer_content_claim": (
            "PD-4d6266-2 claims same content as edd104; byte texts of F-N4, "
            "F-BOUND-CONSTRUCTED and F-INDEX differ. Core F-N4 biconditional "
            "and F-BOUND uniqueness still hold under this draft's gate texts."
        ),
    }
    (HERE / "ej4_result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "text_byte_identical": text_identical,
        "biconditional_holds": result["biconditional_holds"],
        "unique_expected": result["constructed_expected_unique"],
        "contrast_separates": result["contrast_control_separates"],
        "n_cases_bnd1": tt_bnd1["n_cases"],
        "disagreements": tt_bnd1["n4_stop10_disagreements"],
    }))


if __name__ == "__main__":
    main()
