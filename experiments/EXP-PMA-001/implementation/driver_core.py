"""
Shared per-instance driver used by RUN-PMA4-001-b and RUN-PMA4-001-c: runs
Module A (predicate) and Module B (decider), reconstructs Module B's
witness as real RationalFunction objects when EXISTS, and reverifies via
witness_verifier.py. This file is NOT one of the frozen required_artifacts
implementation files (parity_predicate.py / existence_decider.py /
witness_verifier.py); it only orchestrates calls into them identically for
every grid instance so the two runs do not duplicate (and risk diverging)
harness code. It contains no independent decision logic of its own.
"""
from __future__ import annotations

from common import build_p_table, q_ij, c_ijk, delta_ijk, ANCHOR_TRIPLES, NONEMPTY_SUBSETS
from existence_decider import constructive_sqrt, four_by_four_det, RationalFunction as RF
import parity_predicate as A
import witness_verifier as V


def run_instance(d_values, domain, field_label, kind):
    a_res = A.evaluate_instance(d_values, domain, field_label)
    p_table = build_p_table(d_values, domain)

    q_vals = {(i, j): q_ij(p_table, i, j, domain) for (i, j) in [(1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)]}
    degenerate = any(
        q_vals[tuple(sorted(pair))].is_zero()
        for tri in ANCHOR_TRIPLES
        for pair in [(tri[0], tri[1]), (tri[1], tri[2]), (tri[2], tri[0])]
    )

    record = {
        "kind": kind,
        "d_values": {str(k): v for k, v in d_values.items()},
        "predicate_verdict": a_res["verdict"],
        # Module A's own per-anchor-triple certificates (divisor factors,
        # valuations, residual constant class) are carried through here so
        # the aggregation stage (RUN-PMA4-001-d) can report obstruction
        # witnesses without re-deciding anything -- this is Module A's own
        # already-computed output, not a new computation.
        "predicate_triple_certificates": a_res.get("triple_certificates"),
    }

    if degenerate or a_res["verdict"] == "DEGENERATE":
        record["decider_verdict"] = "DEGENERATE"
        record["classification"] = "excluded_degenerate"
        record["degenerate_reasons"] = a_res.get("degenerate_reasons", [])
        return record

    sqrt_results = {}
    c_vals = {}
    for tri in ANCHOR_TRIPLES:
        D = delta_ijk(p_table, tri[0], tri[1], tri[2], domain)
        h, reason = constructive_sqrt(D, domain)
        sqrt_results[tri] = h
        c_vals[tri] = c_ijk(p_table, tri[0], tri[1], tri[2], domain)

    if any(h is None for h in sqrt_results.values()):
        record["decider_verdict"] = "NOT_EXISTS"
        record["decider_reason"] = "no constructive square root for at least one anchor discriminant"
        record["witness_reverified_16_16"] = None
        obstructed = a_res["verdict"] == "OBSTRUCTED"
        record["classification"] = "agreement_obstructed_confirmed" if obstructed else "false_compatibility"
        return record

    two_rf = RF.constant(2, domain)
    witness = None
    branch_summaries = []
    for s1 in (1, -1):
        for s2 in (1, -1):
            for s3 in (1, -1):
                signs = {ANCHOR_TRIPLES[0]: s1, ANCHOR_TRIPLES[1]: s2, ANCHOR_TRIPLES[2]: s3}
                entries = {}
                for idx in (1, 2, 3, 4):
                    entries[(idx, idx)] = p_table[(idx,)]
                one_rf = RF.constant(1, domain)
                entries[(1, 2)] = one_rf
                entries[(1, 3)] = one_rf
                entries[(1, 4)] = one_rf
                entries[(2, 1)] = q_vals[(1, 2)]
                entries[(3, 1)] = q_vals[(1, 3)]
                entries[(4, 1)] = q_vals[(1, 4)]
                for tri in ANCHOR_TRIPLES:
                    h = sqrt_results[tri]
                    sh = h if signs[tri] == 1 else (RF.constant(0, domain) - h)
                    c = c_vals[tri]
                    x = (c + sh) / two_rf
                    y = (c - sh) / two_rf
                    if tri == (1, 2, 3):
                        entries[(2, 3)] = x / q_vals[(1, 3)]
                        entries[(3, 2)] = y / q_vals[(1, 2)]
                    elif tri == (1, 2, 4):
                        entries[(2, 4)] = x / q_vals[(1, 4)]
                        entries[(4, 2)] = y / q_vals[(1, 2)]
                    elif tri == (1, 3, 4):
                        entries[(3, 4)] = x / q_vals[(1, 4)]
                        entries[(4, 3)] = y / q_vals[(1, 3)]
                mismatches = []
                for S in NONEMPTY_SUBSETS:
                    computed = four_by_four_det(entries, S, domain)
                    if computed != p_table[S]:
                        mismatches.append(str(S))
                branch_summaries.append({"signs": [s1, s2, s3], "n_mismatch": len(mismatches)})
                if not mismatches and witness is None:
                    witness = entries

    record["branch_log"] = branch_summaries
    if witness is not None:
        reverify = V.reverify_witness(witness, p_table, domain)
        record["decider_verdict"] = "EXISTS"
        record["witness_reverified_16_16"] = reverify["all_16_verified"]
        record["witness_matrix"] = {f"{k[0]},{k[1]}": str(v) for k, v in witness.items()}
        if not reverify["all_16_verified"]:
            record["classification"] = "invalid_measurement_witness_reverification_failed"
            return record
    else:
        record["decider_verdict"] = "NOT_EXISTS"
        record["witness_reverified_16_16"] = None

    obstructed = a_res["verdict"] == "OBSTRUCTED"
    exists = record["decider_verdict"] == "EXISTS"
    if obstructed and exists:
        record["classification"] = "false_obstruction"
    elif (not obstructed) and (not exists):
        record["classification"] = "false_compatibility"
    elif obstructed and (not exists):
        record["classification"] = "agreement_obstructed_confirmed"
    else:
        record["classification"] = "agreement_compatible_confirmed"
    return record
