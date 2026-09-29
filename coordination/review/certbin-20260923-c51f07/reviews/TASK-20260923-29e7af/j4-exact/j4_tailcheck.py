#!/usr/bin/env python3
"""J4 step 4 (TASK-20260923-29e7af): recompute the M2 'tail_extremes'
P_null_min_le_observed with (a) the archived impl/stats.py functions exactly as
analysis.summarize_p2 calls them and (b) exact rational arithmetic. Inputs: the
P2 S_k list from comparison-D4.json (== archived)."""
import json, math, os, sys
from fractions import Fraction
from math import comb
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, "/home/user/crypto-autoresearcher/experiments/EXP-CERTBIN-4e92d7/impl")
from stats import binom_sf  # archived, unmodified
rows = json.load(open(os.path.join(HERE, "comparison-D4.json")))["P2"]["table"]
S = [r["S_k"] for r in rows]
mn = 0.0
p_float = 1.0
for s in S:
    p_float *= binom_sf(int(math.floor(mn * s)) + 1, s, 0.5)
exact = Fraction(1)
for s in S:
    exact *= 1 - Fraction(1, 2 ** s)          # P(h > 0) = 1 - 2^{-S}
tail_exact = 1 - exact
per = [binom_sf(1, s, 0.5) for s in S]
out = {"S_k": S,
       "impl_float_P_null_min_le_observed": 1 - p_float,
       "impl_binom_sf(1,S,0.5) - 1 per pair (roundoff)": [x - 1.0 for x in per],
       "exact_P_null_min_le_observed": float(tail_exact),
       "exact_log10": math.log10(tail_exact.numerator) - math.log10(tail_exact.denominator)}
print(json.dumps(out, indent=1))
json.dump(out, open(os.path.join(HERE, "tailcheck.json"), "w"), indent=1)
