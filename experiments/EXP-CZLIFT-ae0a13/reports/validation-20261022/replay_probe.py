"""Phase-2 instrumented replay for TASK-20261022-93fb1c (J1 coverage, J2 borderline
probes, J3 comparison, PTM-1).

The per-sample loop below copies experiments/EXP-CZLIFT-ae0a13/implementation/run.py
measure_curve() (lines 79-119 at 03479a00) call-for-call so that the RNG stream
is consumed identically; every replayed row is compared with the archived raw
row, so a divergence would show up as a row mismatch.  Additions (no RNG use):

  * drop census: d, d2 and the reason for every skipped sample;
  * J3: the producer's s_tor(P) vs the validator's SEALED blind function
    (blind/blind_rederive.py: F1 spec formula and F2 group projection, two
    starts each, validator arithmetic), on every curve;
  * PTM-1: s_leak(R) = s_tor(R) + [log_P R] T^, T^ a fixed formal-group point,
    pushed through the producer's own smart_ratio / success rule / summarize;
  * Hensel-start collision count (eps1 == eps2) for the canonicity control.
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "experiments/EXP-CZLIFT-ae0a13/implementation"))
sys.path.insert(0, str(HERE / "blind"))

import run as driver  # noqa: E402  (producer driver, read-only use)
from harness import czlift  # noqa: E402
from harness.czlift import ZpCurve, smart_ratio  # noqa: E402
from harness.toycurve import EllipticCurve  # noqa: E402

import blind_lib  # noqa: E402  (validator, sealed)
import blind_rederive  # noqa: E402  (validator, sealed)

RUNS = REPO / "experiments/EXP-CZLIFT-ae0a13/runs"
SEEDS = {"RUN-CZLIFT-dab752": 20261009, "RUN-CZLIFT-5b2581": 20261010}


def producer_affine(E: ZpCurve, P):
    X, Y, Z = P
    zi = pow(Z, -1, E.M)
    return (X * zi % E.M, Y * zi % E.M)


def leak_point(E: ZpCurve, v: int):
    """Fixed formal-group point T^ with z = p^v (nonzero formal log), built from
    the validator's formal-parameter construction, checked on the producer curve."""
    C = blind_lib.Curve(E.p, E.a, E.b, E.k)
    T = C.point_from_z(E.p ** v)
    assert E.on_curve(T) and E.z_param(T) == E.p ** v % E.M
    return T


def measure_curve_instrumented(arm, p, A, B, N, n, *, seed, samples, label):
    rng = random.Random(seed * 7_919 + p * 31 + (A % p))
    Efp = EllipticCurve(p, A % p, B % p)
    assert Efp.order() == N and N % n == 0 and n != p and N % 2 == 1
    h = N // n
    k = driver.PRECISION
    E = ZpCurve(p, k, A, B)
    rows, drops, j3, leak_rows, eps_collisions = [], [], [], [], 0
    T1, T2 = leak_point(E, 1), leak_point(E, 2)
    for i in range(samples):
        P = czlift.point_of_order(Efp, n, h, rng)
        d = rng.randrange(2, n - 1)
        d2 = rng.randrange(1, n)
        Q = Efp.mul(d, P)
        R2 = Efp.mul(d2, P)
        S = Efp.add(P, R2)
        if Q is None or R2 is None or S is None or Q[1] == 0 or R2[1] == 0 or S[1] == 0:
            reason = [nm for nm, pt in (("Q", Q), ("R2", R2), ("S", S)) if pt is None or pt[1] == 0]
            drops.append({"sample": i, "d": d, "d2": d2, "n": n, "reason": reason,
                          "d2_is_n_minus_1": d2 == n - 1})
            continue
        e1, e2 = rng.randrange(p), rng.randrange(p)
        eps_collisions += e1 == e2
        hP1 = E.hensel_lift(P[0], P[1], eps=e1)
        hP2 = E.hensel_lift(P[0], P[1], eps=e2)
        tP, costP = E.torsion_section(hP1, n)
        tP_alt, _ = E.torsion_section(hP2, n)
        tQ, _ = E.torsion_section(E.hensel_lift(Q[0], Q[1], eps=rng.randrange(p)), n)
        tR2, _ = E.torsion_section(E.hensel_lift(R2[0], R2[1], eps=rng.randrange(p)), n)
        tS, _ = E.torsion_section(E.hensel_lift(S[0], S[1], eps=rng.randrange(p)), n)
        row = {
            "canonical": E.eq(tP, tP_alt),
            "hom_tor": E.eq(tS, E.add(tP, tR2)),
            "degenerate_tor": E.is_zero(E.mul(n, tP)),
            "tor_reduces": E.reduce(tP) == P,
            "tor_cost_additions": costP,
            "scalar_mult_tor": E.eq(tQ, E.mul(d, tP)),
            "sections": {},
        }
        for sec in driver.SECTIONS:
            sP = driver.lift_point(E, P, sec, rng)
            sQ = driver.lift_point(E, Q, sec, rng)
            sR2 = driver.lift_point(E, R2, sec, rng)
            sS = driver.lift_point(E, S, sec, rng)
            ratio, vP, vQ = smart_ratio(E, sP, sQ, n)
            tratio, tvP, tvQ = driver.tau_ratio(E, sP, sQ, tP, tQ)
            row["sections"][sec] = {
                "vP": vP, "vQ": vQ,
                "ratio_defined": ratio is not None,
                "success": ratio is not None and ratio == d % p,
                "identity_holds": (ratio == tratio and vP == tvP and vQ == tvQ),
                "hom_prec2": E.eq(sS, E.add(sP, sR2), prec=2),
            }
        rows.append(row)
        # ---- J3: producer s_tor vs sealed blind function (no RNG use)
        prod = producer_affine(E, tP)
        blind = {}
        for meth in ("F1", "F2"):
            for r in (0, 7 % p ** (k - 1) or 1):
                nb = blind_rederive.s_tor_point(p, A, B, N, n, P[0], P[1], r=r, method=meth)
                blind[f"{meth}_r{r}"] = nb
        agree = all(b[0] == "aff" and (b[1], b[2]) == prod for b in blind.values())
        # validator cost convention on the same scalars: (bits-1)+(popcount-1) per scalar, +1
        m = pow(n, -1, p ** k)
        my_cost = (n.bit_length() - 1 + bin(n).count("1") - 1) + (m.bit_length() - 1 + bin(m).count("1") - 1) + 1
        j3.append({"P": list(P), "producer_s_tor": list(prod), "blind_agrees_all4": agree,
                   "producer_cost": costP, "validator_cost_convention": my_cost,
                   "d": d, "d2": d2, "teich_hom2": row["sections"]["teichmuller"]["hom_prec2"]})
        # ---- PTM-1: leaky sections through the producer's measurement
        lr = {}
        for name, T in (("leak_v1", T1), ("leak_v2", T2)):
            sP = E.add(tP, T)               # log_P(P) = 1
            sQ = E.add(tQ, E.mul(d, T))     # log_P(Q) = d
            ratio, vP, vQ = smart_ratio(E, sP, sQ, n)
            lr[name] = {"vP": vP, "vQ": vQ, "ratio_defined": ratio is not None,
                        "success": ratio is not None and ratio == d % p,
                        "identity_holds": True, "hom_prec2": True}
        # control inside PTM: torsion section itself (formal log vanishes -> undefined)
        ratio, vP, vQ = smart_ratio(E, tP, tQ, n)
        lr["torsion_itself"] = {"vP": vP, "vQ": vQ, "ratio_defined": ratio is not None,
                                "success": ratio is not None and ratio == d % p,
                                "identity_holds": True, "hom_prec2": True}
        j3[-1]["torsion_vP"], j3[-1]["torsion_vQ"] = vP, vQ
        leak_rows.append({**{kk: row[kk] for kk in ("canonical", "hom_tor", "degenerate_tor", "tor_reduces",
                                                    "tor_cost_additions", "scalar_mult_tor")},
                          "sections": lr})
    rec = {"arm": arm, "label": label, "p": p, "A": A, "B": B, "N": N, "n": n,
           "precision": k, "rows": rows}
    return rec, drops, j3, leak_rows, eps_collisions


def rebuild_curve_list(seed, pmax=600, max_cm=24):
    rng = random.Random(seed)
    cm = czlift.cm_curves_with_prime_subgroup(50, pmax, 11)
    pool = len(cm)
    rng.shuffle(cm)
    cm = sorted(cm[:max_cm])
    rand = czlift.random_curves_with_prime_subgroup(
        [q for q in driver.PRIMES_RANDOM_ARM if q <= pmax], 11, random.Random(seed + 1))
    return cm, rand, pool


def main():
    out = {}
    for run_id, seed in SEEDS.items():
        raw = json.loads((RUNS / run_id / "raw-result.json").read_text())
        cm, rand, pool = rebuild_curve_list(seed)
        listed = [("cm_canonical", p, A, B, N, n, f"D={D}") for D, p, A, B, N, n in cm] + \
                 [("random_naive", p, a, b, N, n, "random") for p, a, b, N, n in rand]
        rec_list = [(c["arm"], c["p"], c["A"], c["B"], c["N"], c["n"], c["label"]) for c in raw["raw"]["curves"]]
        res = {"seed": seed, "cm_pool_size": pool, "curve_list_matches_raw": listed == rec_list,
               "rows_match": 0, "rows_total": 0, "curves_row_mismatch": [], "drops": [],
               "eps_collisions": 0, "j3": [], "ptm_curves": []}
        leak_curves = []
        for (arm, p, A, B, N, n, label), rc in zip(listed, raw["raw"]["curves"]):
            fresh, drops, j3, leak_rows, coll = measure_curve_instrumented(
                arm, p, A, B, N, n, seed=seed, samples=16, label=label)
            res["rows_total"] += len(rc["rows"])
            if fresh["rows"] == rc["rows"]:
                res["rows_match"] += len(rc["rows"])
            else:
                res["curves_row_mismatch"].append([arm, p, n])
            for dr in drops:
                dr.update({"arm": arm, "p": p, "label": label})
            res["drops"] += drops
            res["eps_collisions"] += coll
            res["j3"].append({"arm": arm, "label": label, "p": p, "A": A, "B": B, "N": N, "n": n,
                              "rows": len(j3), "blind_agree": sum(x["blind_agrees_all4"] for x in j3),
                              "producer_cost_mean": sum(x["producer_cost"] for x in j3) / len(j3),
                              "validator_cost_mean": sum(x["validator_cost_convention"] for x in j3) / len(j3),
                              "cost_offset_set": sorted({x["producer_cost"] - x["validator_cost_convention"] for x in j3}),
                              "first_pair": j3[0], "pairs": j3})
            leak_curves.append({"arm": arm, "label": label, "p": p, "A": A, "B": B, "N": N, "n": n,
                                "precision": 4, "rows": leak_rows})
        summ = driver.summarize(leak_curves)
        res["ptm_summary_via_producer_summarize"] = summ["sections"]
        res["drop_reasons"] = sorted({tuple(d["reason"]) for d in res["drops"]})
        res["drops_all_d2_eq_n_minus_1"] = all(d["d2_is_n_minus_1"] for d in res["drops"])
        res["expected_drops_if_only_d2_eq_n_minus_1"] = None
        out[run_id] = res
    (HERE / "replay_probe_output.json").write_text(json.dumps(out, indent=1, sort_keys=True, default=list) + "\n")
    for run_id, res in out.items():
        print("==", run_id, "seed", res["seed"], "cm pool", res["cm_pool_size"],
              "curve list == raw:", res["curve_list_matches_raw"],
              f"rows reproduced {res['rows_match']}/{res['rows_total']}", "mismatched curves:", res["curves_row_mismatch"])
        print("  drops:", len(res["drops"]), "reasons:", res["drop_reasons"], "all d2==n-1:", res["drops_all_d2_eq_n_minus_1"])
        for d in res["drops"]:
            print("    ", d["arm"], d["label"], "p", d["p"], "n", d["n"], "d", d["d"], "d2", d["d2"], d["reason"])
        print("  eps collisions (canonicity starts identical):", res["eps_collisions"])
        tot = sum(x["rows"] for x in res["j3"]); agr = sum(x["blind_agree"] for x in res["j3"])
        j0 = [x for x in res["j3"] if x["label"] == "D=-3"]
        print(f"  J3 blind vs producer s_tor: all curves {agr}/{tot}; j=0 curves {sum(x['blind_agree'] for x in j0)}/{sum(x['rows'] for x in j0)} over p={[x['p'] for x in j0]}")
        print("  cost offsets producer-validator:", sorted({o for x in res["j3"] for o in x["cost_offset_set"]}))
        for sec, arms in res["ptm_summary_via_producer_summarize"].items():
            for a, m in arms.items():
                print(f"  PTM {sec:15s} {a:13s} n={m['n']} success_rate={m['success_rate']:.4f} z={m['z_score']:.2f} frac_v1={m['frac_valuation_1']:.4f}")


if __name__ == "__main__":
    main()
