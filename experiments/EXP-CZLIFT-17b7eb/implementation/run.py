"""EXP-CZLIFT-17b7eb driver: Smart's attack against the canonical curve lift.

On every class-number-one CM anomalous curve E/F_p (#E = p) with p <= pmax,
lift the CURVE to Z/p^k in five ways -- the explicit CM (canonical) model, an
isomorphic re-model of it, and perturbations at p-adic distance p and p^2 from
it -- lift POINTS by three sections (Hensel with a random x-digit, the naive
integer lift, the Teichmuller x), and read v_p(z([p]P^)) together with Smart's
ratio z([p]Q^)/z([p]P^) at the first nonzero digit. The pre-registered rule
under test is

    v_p(z([p]P^)) >= 2   <=>   v_p(j(E^) - j_CM) >= 2e,

e the ramification index of the j-map at j_CM (3 at j=0, 1 otherwise). The
driver records observations only; it decides nothing.
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

EXP_ID = "EXP-CZLIFT-17b7eb"
PRECISION = 8
POINT_SECTIONS = ("hensel_random", "naive", "teichmuller")


def lift_classes(p: int, A: int, B: int, j_cm: int, rng: random.Random, per_class: int):
    """(class name, A', B') curve lifts of the reduction of y^2 = x^3 + A x + B."""
    out = [("canonical", A, B)]
    for _ in range(per_class):
        t = rng.randrange(1, p)
        s = 1 + p * t
        out.append(("isomorphic", A * s * s, B * s * s * s))
    for _ in range(per_class):
        if j_cm == 0:
            out.append(("pert_p", p * rng.randrange(1, p), B + p * rng.randrange(0, p)))
            out.append(("pert_p2", p * p * rng.randrange(1, p), B + p * rng.randrange(0, p)))
        else:
            out.append(("pert_p", A + p * rng.randrange(1, p), B + p * rng.randrange(1, p)))
            out.append(("pert_p2", A + p * p * rng.randrange(1, p), B + p * p * rng.randrange(1, p)))
    return out


def lift_point(E: ZpCurve, R, section: str, rng: random.Random):
    if section == "hensel_random":
        return E.hensel_lift(R[0], R[1], eps=rng.randrange(E.p))
    if section == "naive":
        return E.hensel_lift(R[0], R[1], eps=0)
    if section == "teichmuller":
        return E.teichmuller_lift(R[0], R[1])
    raise ValueError(section)


def measure_curve(D: int, p: int, A: int, B: int, j_cm: int, *, seed: int,
                  samples: int, per_class: int) -> dict:
    rng = random.Random(seed * 1_000_003 + p)
    Efp = EllipticCurve(p, A % p, B % p)
    assert Efp.order() == p, "curve is not anomalous"
    e = czlift.ramification_index(j_cm)
    k = PRECISION
    rows = []
    for cls, A2, B2 in lift_classes(p, A, B, j_cm, rng, per_class):
        E = ZpCurve(p, k, A2, B2)
        dj = (E.j_invariant() - j_cm) % E.M
        v_dj = val_p(dj, p, k)
        predicted_degenerate = v_dj >= 2 * e
        for section in POINT_SECTIONS:
            for _ in range(samples):
                P = czlift.random_point(Efp, rng)
                # d = +-1 is excluded: every negation-equivariant section
                # (naive, Teichmuller) recovers it trivially, a symmetry and
                # not an attack (pilot observation, recorded in the contract).
                d = rng.randrange(2, p - 1)
                Q = Efp.mul(d, P)
                if Q is None or Q[1] == 0:
                    continue
                Ph = lift_point(E, P, section, rng)
                Qh = lift_point(E, Q, section, rng)
                ratio, vP, vQ = smart_ratio(E, Ph, Qh, p)
                rows.append({
                    "class": cls, "section": section, "v_dj": v_dj,
                    "predicted_degenerate": predicted_degenerate,
                    "vP": vP, "vQ": vQ, "degenerate": vP >= 2,
                    "ratio_defined": ratio is not None,
                    "success": (ratio is not None and ratio == d),
                })
    return {"D": D, "p": p, "A": A, "B": B, "j_cm": j_cm, "e": e,
            "precision": k, "rows": rows}


def summarize(curves: list[dict]) -> dict:
    by_class: dict[str, dict] = {}
    by_section: dict[str, dict] = {}
    agree = total = 0
    nondeg_success = nondeg_total = 0
    deg_success = deg_total = 0
    deg_inv_p_sum = 0.0
    for c in curves:
        p = c["p"]
        for r in c["rows"]:
            total += 1
            agree += int(r["degenerate"] == r["predicted_degenerate"])
            s = by_class.setdefault(r["class"], {"n": 0, "degenerate": 0, "success": 0,
                                                 "ratio_defined": 0, "predicted_degenerate": 0})
            s["n"] += 1
            s["degenerate"] += int(r["degenerate"])
            s["success"] += int(r["success"])
            s["ratio_defined"] += int(r["ratio_defined"])
            s["predicted_degenerate"] += int(r["predicted_degenerate"])
            if r["vP"] == 1:
                nondeg_total += 1
                nondeg_success += int(r["success"])
            elif r["ratio_defined"]:
                deg_total += 1
                deg_success += int(r["success"])
                deg_inv_p_sum += 1.0 / p
                t = by_section.setdefault(r["section"], {"n": 0, "success": 0, "inv_p_sum": 0.0})
                t["n"] += 1
                t["success"] += int(r["success"])
                t["inv_p_sum"] += 1.0 / p
    for s in by_class.values():
        s["frac_degenerate"] = s["degenerate"] / s["n"] if s["n"] else None
        s["frac_predicted_degenerate"] = s["predicted_degenerate"] / s["n"] if s["n"] else None
        s["success_rate"] = s["success"] / s["n"] if s["n"] else None
    for t in by_section.values():
        t["degenerate_success_rate"] = t["success"] / t["n"]
        t["reference_inv_p"] = t["inv_p_sum"] / t["n"]
    deg_ref = deg_inv_p_sum / deg_total if deg_total else None
    deg_rate = deg_success / deg_total if deg_total else None
    sigma = ((deg_ref * (1 - deg_ref) / deg_total) ** 0.5) if deg_total and deg_ref else None
    return {
        "samples_total": total,
        "rule_agreement": agree / total if total else None,
        "rule_disagreements": total - agree,
        "nondegenerate_samples": nondeg_total,
        "nondegenerate_success_rate": nondeg_success / nondeg_total if nondeg_total else None,
        "degenerate_ratio_defined_samples": deg_total,
        "degenerate_success_rate": deg_rate,
        "degenerate_reference_inv_p": deg_ref,
        "degenerate_z_score": ((deg_rate - deg_ref) / sigma) if sigma else None,
        "by_class": by_class,
        "degenerate_by_section": by_section,
        "curves": len(curves),
    }


def build(seed: int, pmax: int, samples: int, per_class: int) -> tuple[dict, dict]:
    curves_in = czlift.anomalous_cm_curves(pmax)
    curves = [measure_curve(D, p, A, B, j, seed=seed, samples=samples, per_class=per_class)
              for D, p, A, B, j in curves_in]
    metrics = summarize(curves)
    metrics["pmax"] = pmax
    metrics["seed"] = seed
    metrics["precision"] = PRECISION
    metrics["curve_list"] = [(c["D"], c["p"]) for c in curves]
    return metrics, {"curves": curves}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--pmax", type=int, default=1500)
    ap.add_argument("--samples", type=int, default=12)
    ap.add_argument("--per-class", type=int, default=2)
    args = ap.parse_args(argv)
    t0 = time.time()
    metrics, raw = build(args.seed, args.pmax, args.samples, args.per_class)
    t1 = time.time()
    sources = [os.path.abspath(__file__),
               os.path.join(REPO, "harness", "czlift.py"),
               os.path.join(REPO, "harness", "czlift_run.py"),
               os.path.join(REPO, "harness", "toycurve.py")]
    write_run_record(args.run_dir, run_id=args.run_id, exp_id=EXP_ID,
                     status="completed_valid", command=[sys.executable] + sys.argv,
                     sources=sources, seed=args.seed,
                     parameters={"pmax": args.pmax, "samples": args.samples,
                                 "per_class": args.per_class, "precision": PRECISION,
                                 "tier": "toy"},
                     metrics=metrics, raw=raw, started=t0, finished=t1,
                     stdout=json.dumps({k: v for k, v in metrics.items() if k not in ("by_class", "degenerate_by_section")},
                                       indent=1) + "\n")
    print(json.dumps({k: v for k, v in metrics.items() if k not in ("by_class", "curve_list", "degenerate_by_section")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
