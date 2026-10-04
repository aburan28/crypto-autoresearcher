#!/usr/bin/env python3
"""TASK-20260923-b8f163 J1 negative controls for the J1 comparisons themselves.

A comparison that cannot fail proves nothing. For each misreading the review
plan names as a likely break, construct the object under the WRONG reading and
show that it differs from the archived / impl object. Instance: F-S3 reference
U1 only (already in the J1 instance set). Zero trials; no RUN-id.

  W1  degrevlex tie-break reversed ("a DOES contain v_i")
  W2  pivot rule read against the ORIGINAL matrix
  W3  mu * f_k not multilinearized (terms with a repeated variable dropped)
  W4  ascending (not descending) degrevlex, constant first
"""
import gzip
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import j1_spec_literal as J  # noqa: E402  (validator's own module)

RUN = J.RUN


def main():
    out = {}
    curve = json.load(open(os.path.join(RUN, "curve.json")))
    B = curve["B"]
    refs = json.load(open(os.path.join(RUN, "references.json")))["F-S3"]["references"]
    xR = refs["U1"]["x_R"]
    f = J.equations_from_coef(J.descent_mobius(B, xR))
    for D in (3, 4):
        cols, _ = J.column_order_literal(D)
        mus, _ = J.row_order_literal(D)
        arch_cols = [tuple(c["monomial"]) for c in json.load(open(os.path.join(RUN, f"column-order-D{D}.json")))["columns"]]
        # W1: reversed tie-break
        def wrong_greater(a, b):
            if len(a) != len(b):
                return len(a) > len(b)
            d = set(a) ^ set(b)
            if not d:
                return False
            return max(d) in set(a)
        from functools import cmp_to_key
        w1 = sorted(J.monomials_upto(D), key=cmp_to_key(lambda a, b: -1 if wrong_greater(a, b) else (1 if wrong_greater(b, a) else 0)))
        w1_diff = sum(1 for a, b in zip(w1, arch_cols) if a != b)
        # W4: ascending
        w4 = list(reversed(cols))
        w4_diff = sum(1 for a, b in zip(w4, arch_cols) if a != b)
        colidx = {m: i for i, m in enumerate(cols)}
        rows = J.macaulay_rows(f, mus, colidx)
        arch_T = refs["U1"][f"D{D}"]["T_strict"]
        # W1 effect on T_strict: build rows in the W1 column order and eliminate
        colidx_w1 = {m: i for i, m in enumerate(w1)}
        rows_w1 = J.macaulay_rows(f, mus, colidx_w1)
        T_w1 = [[p, c] for p, c, _ in J.literal_solver(rows_w1, len(w1))]
        # W2: pivot candidates read from the ORIGINAL matrix
        cur = list(rows)
        used = [False] * len(rows)
        T_w2 = []
        for c in range(len(cols)):
            bit = 1 << c
            cand = [i for i in range(len(rows)) if (not used[i]) and (rows[i] & bit)]
            if not cand:
                continue
            p = cand[0]
            for x in cand[1:]:
                cur[x] ^= cur[p]
            used[p] = True
            T_w2.append([p, c])
        # W3: no multilinear reduction (drop terms where mu and m share a variable)
        rows_w3 = []
        for mu in mus:
            for k in range(J.NEQ):
                acc = set()
                for m in f[k]:
                    if set(mu) & set(m):
                        continue
                    prod = tuple(sorted(set(mu) | set(m)))
                    acc ^= {prod}
                v = 0
                for prod in acc:
                    v |= 1 << colidx[prod]
                rows_w3.append(v)
        w3_rows_diff = sum(1 for a, b in zip(rows, rows_w3) if a != b)
        T_w3 = [[p, c] for p, c, _ in J.literal_solver(rows_w3, len(cols))]
        first_div = lambda A, Bl: next((i for i, (a, b) in enumerate(zip(A, Bl)) if a != b), min(len(A), len(Bl)))
        out[f"D{D}"] = {
            "W1_tiebreak_reversed": {"column_positions_differing_from_archived": w1_diff,
                                     "T_strict_equal_archived": T_w1 == arch_T},
            "W4_ascending_order": {"column_positions_differing_from_archived": w4_diff},
            "W2_pivot_rule_original_matrix": {"T_strict_equal_archived": T_w2 == arch_T,
                                              "first_divergence_step": first_div(T_w2, arch_T),
                                              "len_wrong": len(T_w2), "len_archived": len(arch_T)},
            "W3_no_multilinear_reduction": {"rows_differing": w3_rows_diff,
                                            "T_strict_equal_archived": T_w3 == arch_T},
            "correct_reading_T_strict_equal_archived": [[p, c] for p, c, _ in J.literal_solver(rows, len(cols))] == arch_T,
        }
        print(D, json.dumps(out[f"D{D}"]))
    json.dump(out, open(os.path.join(HERE, "j1_power_controls.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
