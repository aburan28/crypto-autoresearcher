#!/usr/bin/env python3
"""Replicate the committed F_l certifier (exact_certify.certify) on the n=8
d=(1..1) control objects, with the DEFAULT 60-prime window and with ENLARGED
prime windows. This directly answers J3 A.2: are the [6,6,7,7,7,7,7,6]
shortfalls forced by the prime bound (enlarged window reaches 7 ->
instrument-boundary) or do they survive any enlargement (stays 6 -> genuine
dependence, control-failure revives)?

The committed certifier is imported byte-identical (sha256-pinned) via
ecrank_engine.load_exact_certify and called READ-ONLY with different
max_prime / max_good_primes. Nothing about the certificate changes except the
prime-search window.
"""
import os, sys, json
from fractions import Fraction as Fr

ROOT = "/Volumes/SSD990/llm/tmp/opencode/review-e3cf55-20260909"
SRC = os.path.join(ROOT, "experiments", "EXP-ECRANK-73275e", "source")
sys.path.insert(0, SRC)
os.environ.setdefault("ECRANK_REPO_ROOT", ROOT)
import ecrank_engine as E

ec, digest = E.load_exact_certify(ROOT)
print("committed exact_certify sha256:", digest)
print("pinned match:", digest == E.EXACT_CERTIFY_SHA)

HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, "b_tuples.json")) as f:
    BT = json.load(f)
N8 = [[Fr(x) for x in row] for row in BT["n8"]]

def build(bi):
    b = N8[bi]
    p_, g, s = E.mestre_polys(list(b))
    r = [E.peval(g, x) for x in b]
    ainv, Wpts = E.cubic_to_weierstrass(s, [(b[i], r[i]) for i in range(8)])
    ainv = [int(z) for z in ainv]
    pts = [[str(x), str(y)] for (x, y) in Wpts]
    return ainv, pts

def run_certify(ainv, pts, **kw):
    res = ec.certify(ainv, pts, **kw)
    return res

def summarize(res):
    return {
        "certified_rank_lower_bound": res["certified_rank_lower_bound"],
        "n_points_non_torsion": res.get("n_points_non_torsion"),
        "torsion_bound": res.get("torsion_bound"),
        "torsion_bound_primes": res.get("torsion_bound_primes"),
        "independence_attempts": res.get("independence_attempts"),
        "n_primes_used_best": (len(res["independence"]["primes_used"])
                               if res.get("independence") else None),
        "best_l": (res["independence"]["l"] if res.get("independence") else None),
        "errors": res.get("errors"),
    }

WINDOWS = [
    ("default (max_prime=1500, max_good_primes=60)",
     dict(max_prime=1500, max_good_primes=60)),
    ("ladder-10000 (max_prime=10000, max_good_primes=60)",
     dict(max_prime=10000, max_good_primes=60)),
    ("ladder-100000 (max_prime=100000, max_good_primes=60)",
     dict(max_prime=100000, max_good_primes=60)),
    ("enlarged (max_prime=100000, max_good_primes=200)",
     dict(max_prime=100000, max_good_primes=200)),
    ("enlarged (max_prime=100000, max_good_primes=400)",
     dict(max_prime=100000, max_good_primes=400)),
]

report = {}
for bi in (0, 1, 7, 2):
    ainv, pts = build(bi)
    rec = {"ainv": ainv}
    for name, kw in WINDOWS:
        res = run_certify(ainv, pts, **kw)
        rec[name] = summarize(res)
    report[str(bi)] = rec
    print("=== b_index %d ===" % bi)
    for name, _ in WINDOWS:
        s = rec[name]
        print("  %-45s certified=%s  (best l=%s, primes_used=%s)"
              % (name, s["certified_rank_lower_bound"],
                 s["best_l"], s["n_primes_used_best"]))
    print()

with open(os.path.join(HERE, "certify_windows.json"), "w") as f:
    json.dump(report, f, indent=1)
print("wrote certify_windows.json")
