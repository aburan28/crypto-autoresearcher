#!/usr/bin/env python3
"""Phase-2 J3 comparison for EXP-CZLIFT-7c8d73 (validator TASK-20261022-d7d57f).

Compares the SEALED blind formal-log coefficients (blind/blind_output.json, produced by
blind/blind_formal_log.py before any blind_from path was opened) with the producer's
harness/czlift_formal.formal_series at the specification's precision k = 6:
  (1) the plan's literal quantity: y^2 = x^3 + B, p = 7, B = 5 (reading a: z^0..z^6);
  (2) the specification's curve family: every one of the 29 curves (and A != 0 in general);
  (3) an additivity test of each log_F mod p^6 on a formal point pair, using the
      validator's own chord law in the (z, w) plane (exact rationals);
  (4) the pert_p accident: the linear form j_A r1 + j_B r2 mod p for the two mislabelled lifts,
      and the expected number of such accidents per seed.
Run with python3 -B.
"""
from __future__ import annotations

import importlib.util
import json
import os
import sys
from fractions import Fraction

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, REPO)
_spec = importlib.util.spec_from_file_location("blind_formal_log", os.path.join(HERE, "blind", "blind_formal_log.py"))
blind = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(blind)

from harness import czlift, czlift_formal  # noqa: E402
from harness.czlift import ZpCurve  # noqa: E402

K = 6
sealed = json.load(open(os.path.join(HERE, "blind", "blind_output.json")))


def blind_coeffs(ser, A, B, p, n_terms):
    return [blind.modpk(blind.peval(ser[n], A, B), p, K) if ser[n] else 0 for n in range(n_terms)]


def main():
    W = blind.formal_w()
    LG = blind.integrate(blind.invariant_differential(W))
    EX = blind.reversion(LG)
    out = {}

    # (1) the plan's literal quantity
    E = ZpCurve(7, K, 0, 5)
    w, lg, ex = czlift_formal.formal_series(E)
    out["literal_quantity_p7_B5"] = {
        "sealed_blind_reading_a": sealed["designated_prime"]["mod_p^6_reading_a"],
        "producer_log_F_coeffs_z0_to_z6": lg.c,
        "agree": lg.c == sealed["designated_prime"]["mod_p^6_reading_a"],
        "sealed_blind_reading_b_z1_to_z7": sealed["designated_prime"]["mod_p^6_reading_b"],
        "producer_has_no_z7_term": len(lg.c) == K + 1,
    }

    # (2) the specification's family
    fam = []
    dis_log = dis_exp = 0
    for D, p, A, B, j in czlift.anomalous_cm_curves(1500):
        E = ZpCurve(p, K, A, B)
        w, lg, ex = czlift_formal.formal_series(E)
        bl = blind_coeffs(LG, A, B, p, K + 1)
        be = blind_coeffs(EX, A, B, p, K + 1)
        bw = blind_coeffs(W, A, B, p, K + 1)
        dl = [i for i in range(K + 1) if bl[i] != lg.c[i]]
        de = [i for i in range(K + 1) if be[i] != ex.c[i]]
        dis_log += bool(dl)
        dis_exp += bool(de)
        fam.append({"D": D, "p": p, "A": A, "B": B,
                    "producer_log": lg.c, "blind_log": bl, "log_disagree_at": dl,
                    "producer_exp": ex.c, "blind_exp": be, "exp_disagree_at": de,
                    "w_agree_mod_z7": bw == w.c})
    out["family_comparison"] = {"curves": len(fam), "curves_log_disagree": dis_log,
                                "curves_exp_disagree": dis_exp, "rows": fam}

    # (3) additivity mod p^6 on a formal pair, own chord law
    add = []
    pick = {(-3, 7), (-3, 19), (-11, 223), (-11, 619), (-67, 17), (-163, 41)}
    for D, p, A, B, j in [c for c in czlift.anomalous_cm_curves(1500) if (c[0], c[1]) in pick]:
        E = ZpCurve(p, K, A, B)
        w, lg, ex = czlift_formal.formal_series(E)
        z1, z2 = p * 1, p * 2
        z3 = blind.chord_sum_z(A, B, W, z1, z2)
        z3m = blind.modpk(z3, p, K)
        prod_def = (lg.eval(z1) + lg.eval(z2) - lg.eval(z3m)) % p ** K
        true_def = blind.eval_series_num(LG, A, B, z1) + blind.eval_series_num(LG, A, B, z2) \
            - blind.eval_series_num(LG, A, B, z3)
        add.append({"D": D, "p": p, "A_mod_p": A % p,
                    "v_p(producer log defect mod p^6)": blind.vp(prod_def, p) if prod_def else ">=6",
                    "v_p(blind log defect)": blind.vp(true_def, p)})
    out["additivity_mod_p6"] = add

    # (4) pert_p accidents
    acc = []
    for (D, p, A, B, A2, B2) in [(-67, 17, -85963680, 306775458864, -85963476, 306775459068),
                                 (-11, 223, -85536, 9879408, -51863, 9926015)]:
        r1, r2 = (A2 - A) // p, (B2 - B) // p
        assert A + p * r1 == A2 and B + p * r2 == B2
        den = 4 * A ** 3 + 27 * B ** 2
        # j = 6912 A^3 / den ; dj/dA = 6912*(3A^2 den - A^3*12A^2)/den^2 ; dj/dB = -6912 A^3 * 54 B / den^2
        jA = Fraction(6912 * (3 * A ** 2 * den - A ** 3 * 12 * A ** 2), den ** 2)
        jB = Fraction(-6912 * A ** 3 * 54 * B, den ** 2)
        lin = jA * r1 + jB * r2
        acc.append({"D": D, "p": p, "r1": r1, "r2": r2, "v_p(j_A r1 + j_B r2)": blind.vp(lin, p),
                    "v_p(j(E^) - j_cm) exact": blind.vp(Fraction(6912 * A2 ** 3, 4 * A2 ** 3 + 27 * B2 ** 2)
                                                         - Fraction(6912 * A ** 3, den), p)})
    e1 = [p for D, p, A, B, j in czlift.anomalous_cm_curves(1500) if D != -3]
    out["pert_p_accidents"] = {"lifts": acc,
                               "expected_split_pert_p_lifts_per_seed_approx_sum_2_over_p_e1": sum(2 / p for p in e1),
                               "note": "e=1 pert_p lift (A+p r1, B+p r2) is split iff j_A r1 + j_B r2 = 0 mod p "
                                       "(probability about 1/p); e=3 pert_p has A = p r with r a unit, so v(j) = 3 "
                                       "exactly and it is never split."}
    json.dump(out, sys.stdout, indent=1, default=str)
    print()


if __name__ == "__main__":
    main()
