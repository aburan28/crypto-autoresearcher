"""EXP-CZLIFT-ae0a13 driver: the canonical point section on non-anomalous curves.

For E/F_p with a prime-order subgroup <P> of order n != p, the reduction map
E(Q_p)[n] -> E(F_p)[n] is an isomorphism, so the TORSION SECTION
s_tor(R) = the unique n-torsion lift of R is a canonical section. The driver
computes it explicitly (harness.czlift.ZpCurve.torsion_section), on two arms:

  cm_canonical : class-number-one CM curves lifted by their integral CM model
                 (the Serre-Tate canonical lift of the curve);
  random_naive : random curves y^2 = x^3 + a x + b lifted by the integers a, b
                 (an arbitrary, non-canonical lift of the curve).

Per (P, Q = dP) pair it records: canonicity (two Hensel starts give the same
s_tor), the homomorphism identity s_tor(R1 + R2) = s_tor(R1) + s_tor(R2), the
degeneracy [n] s_tor(R) = O at full precision, the additions spent, and for the
non-torsion sections hensel_random / naive / teichmuller the Smart ratio
z([n]s(Q))/z([n]s(P)), its success against d, and the pre-registered identity

    z([n]s(Q))/z([n]s(P)) = z(tau_Q)/z(tau_P),  tau_R = s(R) - s_tor(R),

which says the ratio depends only on the non-canonical part of the section.
Observations only; the driver decides nothing.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from harness import czlift  # noqa: E402
from harness.czlift import ZpCurve, val_p, smart_ratio  # noqa: E402
from harness.czlift_run import write_run_record  # noqa: E402
from harness.toycurve import EllipticCurve  # noqa: E402

EXP_ID = "EXP-CZLIFT-ae0a13"
PRECISION = 4
SECTIONS = ("hensel_random", "naive", "teichmuller")
PRIMES_RANDOM_ARM = (53, 71, 101, 131, 173, 211, 263, 307, 367, 421, 487, 557)


def lift_point(E: ZpCurve, R, section: str, rng: random.Random):
    if section == "hensel_random":
        return E.hensel_lift(R[0], R[1], eps=rng.randrange(E.p))
    if section == "naive":
        return E.hensel_lift(R[0], R[1], eps=0)
    if section == "teichmuller":
        return E.teichmuller_lift(R[0], R[1])
    raise ValueError(section)


def tau_ratio(E: ZpCurve, sP, sQ, tP, tQ):
    """Leading digit of z(sQ - tQ) / z(sP - tP) when both valuations agree."""
    p, k = E.p, E.k
    zP = E.z_param(E.sub(sP, tP))
    zQ = E.z_param(E.sub(sQ, tQ))
    vP, vQ = val_p(zP, p, k), val_p(zQ, p, k)
    if vP >= k or vQ < vP:
        return None, vP, vQ
    if vQ > vP:
        return 0, vP, vQ
    return (zQ // p ** vQ) * pow((zP // p ** vP) % p, -1, p) % p, vP, vQ


def measure_curve(arm: str, p: int, A: int, B: int, N: int, n: int, *, seed: int,
                  samples: int, label: str) -> dict:
    rng = random.Random(seed * 7_919 + p * 31 + (A % p))
    Efp = EllipticCurve(p, A % p, B % p)
    assert Efp.order() == N and N % n == 0 and n != p and N % 2 == 1
    h = N // n
    k = PRECISION
    E = ZpCurve(p, k, A, B)
    rows = []
    for _ in range(samples):
        P = czlift.point_of_order(Efp, n, h, rng)
        d = rng.randrange(2, n - 1)  # +-1 excluded (negation-equivariant sections)
        d2 = rng.randrange(1, n)
        Q = Efp.mul(d, P)
        R2 = Efp.mul(d2, P)
        S = Efp.add(P, R2)
        if Q is None or R2 is None or S is None or Q[1] == 0 or R2[1] == 0 or S[1] == 0:
            continue
        hP1 = E.hensel_lift(P[0], P[1], eps=rng.randrange(p))
        hP2 = E.hensel_lift(P[0], P[1], eps=rng.randrange(p))
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
        for sec in SECTIONS:
            sP = lift_point(E, P, sec, rng)
            sQ = lift_point(E, Q, sec, rng)
            sR2 = lift_point(E, R2, sec, rng)
            sS = lift_point(E, S, sec, rng)
            ratio, vP, vQ = smart_ratio(E, sP, sQ, n)
            tratio, tvP, tvQ = tau_ratio(E, sP, sQ, tP, tQ)
            row["sections"][sec] = {
                "vP": vP, "vQ": vQ,
                "ratio_defined": ratio is not None,
                "success": ratio is not None and ratio == d % p,
                "identity_holds": (ratio == tratio and vP == tvP and vQ == tvQ),
                "hom_prec2": E.eq(sS, E.add(sP, sR2), prec=2),
            }
        rows.append(row)
    return {"arm": arm, "label": label, "p": p, "A": A, "B": B, "N": N, "n": n,
            "precision": k, "rows": rows}


def summarize(curves: list[dict]) -> dict:
    tot = {"n": 0, "canonical": 0, "hom_tor": 0, "degenerate_tor": 0,
           "tor_reduces": 0, "scalar_mult_tor": 0, "cost_sum": 0,
           "cost_bound_sum": 0}
    sec: dict[str, dict] = {}
    for c in curves:
        p, n, k = c["p"], c["n"], c["precision"]
        bound = 2 * (n.bit_length() + (p ** k).bit_length()) + 1
        for r in c["rows"]:
            tot["n"] += 1
            for key in ("canonical", "hom_tor", "degenerate_tor", "tor_reduces", "scalar_mult_tor"):
                tot[key] += int(r[key])
            tot["cost_sum"] += r["tor_cost_additions"]
            tot["cost_bound_sum"] += bound
            for name, s in r["sections"].items():
                for arm_key in ("all", c["arm"]):
                    t = sec.setdefault(name, {}).setdefault(arm_key, {
                        "n": 0, "ratio_defined": 0, "v1": 0, "success": 0,
                        "identity": 0, "hom_prec2": 0, "inv_p_sum": 0.0})
                    t["n"] += 1
                    t["ratio_defined"] += int(s["ratio_defined"])
                    t["v1"] += int(s["vP"] == 1)
                    t["success"] += int(s["success"])
                    t["identity"] += int(s["identity_holds"])
                    t["hom_prec2"] += int(s["hom_prec2"])
                    t["inv_p_sum"] += 1.0 / p
    out = {
        "pairs_total": tot["n"],
        "canonicity_rate": tot["canonical"] / tot["n"] if tot["n"] else None,
        "homomorphism_rate_torsion": tot["hom_tor"] / tot["n"] if tot["n"] else None,
        "degeneracy_rate_torsion": tot["degenerate_tor"] / tot["n"] if tot["n"] else None,
        "torsion_reduces_rate": tot["tor_reduces"] / tot["n"] if tot["n"] else None,
        "scalar_mult_equivariance_rate": tot["scalar_mult_tor"] / tot["n"] if tot["n"] else None,
        "torsion_cost_mean_additions": tot["cost_sum"] / tot["n"] if tot["n"] else None,
        "torsion_cost_within_bound": None,
        "sections": {},
    }
    out["torsion_cost_within_bound"] = (tot["cost_sum"] <= tot["cost_bound_sum"]) if tot["n"] else None
    for name, arms in sec.items():
        out["sections"][name] = {}
        for arm_key, t in arms.items():
            n_ = t["n"]
            ref = t["inv_p_sum"] / n_
            rate = t["success"] / n_
            sigma = (ref * (1 - ref) / n_) ** 0.5
            out["sections"][name][arm_key] = {
                "n": n_,
                "frac_valuation_1": t["v1"] / n_,
                "success_rate": rate,
                "reference_inv_p": ref,
                "z_score": (rate - ref) / sigma if sigma else None,
                "identity_rate": t["identity"] / n_,
                "homomorphism_rate_prec2": t["hom_prec2"] / n_,
            }
    # arm difference in success rate, pooled over sections
    diffs = {}
    for name, arms in out["sections"].items():
        if "cm_canonical" in arms and "random_naive" in arms:
            a, b = arms["cm_canonical"], arms["random_naive"]
            pooled = (a["success_rate"] * a["n"] + b["success_rate"] * b["n"]) / (a["n"] + b["n"])
            se = (pooled * (1 - pooled) * (1 / a["n"] + 1 / b["n"])) ** 0.5
            diffs[name] = {"difference": a["success_rate"] - b["success_rate"],
                           "z_score": ((a["success_rate"] - b["success_rate"]) / se) if se else None}
    out["arm_difference"] = diffs
    return out


def build(seed: int, pmax: int, samples: int, max_cm: int) -> tuple[dict, dict]:
    rng = random.Random(seed)
    cm = czlift.cm_curves_with_prime_subgroup(50, pmax, 11)
    rng.shuffle(cm)
    cm = sorted(cm[:max_cm])
    rand = czlift.random_curves_with_prime_subgroup([q for q in PRIMES_RANDOM_ARM if q <= pmax],
                                                    11, random.Random(seed + 1))
    curves = []
    for D, p, A, B, N, n in cm:
        curves.append(measure_curve("cm_canonical", p, A, B, N, n, seed=seed,
                                    samples=samples, label=f"D={D}"))
    for p, a, b, N, n in rand:
        curves.append(measure_curve("random_naive", p, a, b, N, n, seed=seed,
                                    samples=samples, label="random"))
    metrics = summarize(curves)
    metrics.update({"seed": seed, "pmax": pmax, "precision": PRECISION,
                    "curves_cm": len(cm), "curves_random": len(rand)})
    return metrics, {"curves": curves}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--pmax", type=int, default=600)
    ap.add_argument("--samples", type=int, default=16)
    ap.add_argument("--max-cm", type=int, default=24)
    args = ap.parse_args(argv)
    t0 = time.time()
    metrics, raw = build(args.seed, args.pmax, args.samples, args.max_cm)
    t1 = time.time()
    sources = [os.path.abspath(__file__),
               os.path.join(REPO, "harness", "czlift.py"),
               os.path.join(REPO, "harness", "czlift_run.py"),
               os.path.join(REPO, "harness", "toycurve.py")]
    write_run_record(args.run_dir, run_id=args.run_id, exp_id=EXP_ID,
                     status="completed_valid", command=[sys.executable] + sys.argv,
                     sources=sources, seed=args.seed,
                     parameters={"pmax": args.pmax, "samples": args.samples,
                                 "max_cm": args.max_cm, "precision": PRECISION,
                                 "tier": "toy"},
                     metrics=metrics, raw=raw, started=t0, finished=t1,
                     stdout=json.dumps(metrics, indent=1) + "\n")
    print(json.dumps({k: v for k, v in metrics.items() if k != "sections"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
