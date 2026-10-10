"""EXP-CZLIFT-7c8d73 driver: Serre-Tate level-1 splitting by explicit construction.

An independent instrument for the degeneracy read in EXP-CZLIFT-17b7eb. On
every class-number-one CM anomalous curve (p <= pmax) and the same four
curve-lift classes (canonical CM model, isomorphic re-model, perturbations
at p-adic distance p and p^2), with Hensel point lifts, compute the formal
logarithm lambda = log_F(z([p]P^)) from the formal-group series
(harness/czlift_formal.py) and, when p^2 | lambda, CONSTRUCT the p-torsion
lift P~ = P^ - exp_F(lambda / p) and verify [p]P~ = O by curve arithmetic.
E^[p] splits (v_p(q - 1) >= 2 in Serre-Tate coordinates) exactly when such a
lift exists. The pre-registered expectation is agreement with the
j-distance rule of H-CZLIFT-889c9d on every sample and a verified
construction on every split sample. Observations only.
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

from harness import czlift, czlift_formal  # noqa: E402
from harness.czlift import ZpCurve, val_p  # noqa: E402
from harness.czlift_run import write_run_record  # noqa: E402
from harness.toycurve import EllipticCurve  # noqa: E402

EXP_ID = "EXP-CZLIFT-7c8d73"
PRECISION = 6


def lift_classes(p, A, B, j_cm, rng, per_class):
    out = [("canonical", A, B)]
    for _ in range(per_class):
        s = 1 + p * rng.randrange(1, p)
        out.append(("isomorphic", A * s * s, B * s ** 3))
    for _ in range(per_class):
        if j_cm == 0:
            out.append(("pert_p", p * rng.randrange(1, p), B + p * rng.randrange(0, p)))
            out.append(("pert_p2", p * p * rng.randrange(1, p), B + p * rng.randrange(0, p)))
        else:
            out.append(("pert_p", A + p * rng.randrange(1, p), B + p * rng.randrange(1, p)))
            out.append(("pert_p2", A + p * p * rng.randrange(1, p), B + p * p * rng.randrange(1, p)))
    return out


def measure_curve(D, p, A, B, j_cm, *, seed, samples, per_class):
    rng = random.Random(seed * 999_983 + p)
    Efp = EllipticCurve(p, A % p, B % p)
    assert Efp.order() == p
    e = czlift.ramification_index(j_cm)
    k = PRECISION
    rows = []
    for cls, A2, B2 in lift_classes(p, A, B, j_cm, rng, per_class):
        E = ZpCurve(p, k, A2, B2)
        E8 = ZpCurve(p, 8, A2, B2)
        v_dj = val_p((E8.j_invariant() - j_cm) % E8.M, p, 8)
        predicted_split = v_dj >= 2 * e
        for _ in range(samples):
            P = czlift.random_point(Efp, rng)
            Ph = E.hensel_lift(P[0], P[1], eps=rng.randrange(p))
            v, Pt, verified = czlift_formal.p_torsion_lift(E, Ph)
            rows.append({"class": cls, "v_dj": v_dj, "predicted_split": predicted_split,
                         "v_log": v, "split": v >= 2, "constructed": Pt is not None, "verified": verified,
                         "reduces": (Pt is not None and E.reduce(Pt) == P)})
    return {"D": D, "p": p, "A": A, "B": B, "j_cm": j_cm, "e": e, "precision": k, "rows": rows}


def summarize(curves):
    n = agree = split = verified = reduces = nonsplit_constructed = 0
    by_class = {}
    for c in curves:
        for r in c["rows"]:
            n += 1
            agree += r["split"] == r["predicted_split"]
            if r["split"]:
                split += 1; verified += r["verified"]; reduces += r["reduces"]
            elif r["constructed"]:
                nonsplit_constructed += 1
            s = by_class.setdefault(r["class"], {"n": 0, "split": 0, "verified": 0})
            s["n"] += 1; s["split"] += r["split"]; s["verified"] += r["verified"]
    for s in by_class.values():
        s["frac_split"] = s["split"] / s["n"]
    return {"samples_total": n, "rule_agreement": agree / n if n else None, "rule_disagreements": n - agree,
            "split_samples": split, "construction_verified_rate": verified / split if split else None,
            "construction_reduces_rate": reduces / split if split else None,
            "nonsplit_with_construction": nonsplit_constructed, "by_class": by_class, "curves": len(curves)}


def build(seed, pmax, samples, per_class):
    curves = [measure_curve(D, p, A, B, j, seed=seed, samples=samples, per_class=per_class)
              for D, p, A, B, j in czlift.anomalous_cm_curves(pmax)]
    m = summarize(curves)
    m.update({"seed": seed, "pmax": pmax, "precision": PRECISION})
    return m, {"curves": curves}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True); ap.add_argument("--run-id", required=True)
    ap.add_argument("--seed", type=int, required=True); ap.add_argument("--pmax", type=int, default=1500)
    ap.add_argument("--samples", type=int, default=8); ap.add_argument("--per-class", type=int, default=2)
    a = ap.parse_args(argv)
    t0 = time.time(); m, raw = build(a.seed, a.pmax, a.samples, a.per_class); t1 = time.time()
    sources = [os.path.abspath(__file__), os.path.join(REPO, "harness", "czlift.py"), os.path.join(REPO, "harness", "czlift_formal.py"),
               os.path.join(REPO, "harness", "czlift_run.py"), os.path.join(REPO, "harness", "toycurve.py")]
    write_run_record(a.run_dir, run_id=a.run_id, exp_id=EXP_ID, status="completed_valid", command=[sys.executable] + sys.argv, sources=sources, seed=a.seed,
                     parameters={"pmax": a.pmax, "samples": a.samples, "per_class": a.per_class, "precision": PRECISION, "tier": "toy"},
                     metrics=m, raw=raw, started=t0, finished=t1, stdout=json.dumps({k: v for k, v in m.items() if k != "by_class"}, indent=1) + "\n")
    print(json.dumps({k: v for k, v in m.items() if k != "by_class"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
