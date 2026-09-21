"""proves_too_much control for TASK-20260904-8c5f97.

Object 1: the same (2,2,3) digit system at p = 2 and p = 3 (p-independence KNOWN FALSE).
Object 2: multiplication by ell^2 from degree 1 to degree 3 on F_p[a_1..a_6]/(a_i^2),
          s = 6 > p = 3 (Wilson inclusion W_{1,3}; rank 5 < 6 at p = 3).
Object 3: the direct presentation with B = round(p^{1/2}) -- handled in
          r3_direct_firstfall.py; the argument's size-independence hypothesis is absent.

Both my own code (rt_digit) and the PRODUCER'S METER are run on objects 1 and 2, so
the control also answers 'is the sweep's own code path sensitive to p at fixed shape?'
"""
import hashlib, json, os, random, sys
from itertools import combinations

REPO = "/home/user/crypto-autoresearcher"
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rt_digit import N, stilde_values, poly_from_values, profile, d_ff, echelon_ranks
from harness.macaulay_fp import macaulay as MAC
from harness.macaulay_fp.presentations import digit_presentation, substitute

out = {}
METER_FILES = ["__init__.py", "poly.py", "linalg.py", "columns.py", "series.py", "koszul.py",
               "macaulay.py", "localization.py", "nulls.py", "presentations.py"]
out["meter_version_sha256"] = {
    f"harness/macaulay_fp/{f}": hashlib.sha256(
        open(os.path.join(REPO, "harness/macaulay_fp", f), "rb").read()).hexdigest()
    for f in METER_FILES}


def s3_dict_own(A, Bc, xr, p):
    d = {}
    def add(i, j, c): d[(i, j)] = (d.get((i, j), 0) + c) % p
    add(2, 0, xr * xr); add(1, 1, -2 * xr * xr); add(0, 2, xr * xr)
    add(2, 1, -2 * xr); add(1, 2, -2 * xr); add(1, 0, -2 * xr * A); add(0, 1, -2 * xr * A)
    add(0, 0, -4 * xr * Bc); add(2, 2, 1); add(1, 1, -2 * A); add(0, 0, A * A)
    add(1, 0, -4 * Bc); add(0, 1, -4 * Bc)
    return {k: v for k, v in d.items() if v}


def meter_profile(A, Bc, xr, p):
    pres = digit_presentation(p, 2, 2, 3, lambda ring, xs: [substitute(ring, s3_dict_own(A, Bc, xr, ring.p), xs)])
    lay = MAC.analyze_degrees(pres.ring, [pres.generators[0]], 3, 6, convention="per_layer")
    return {"full_rank": [l.full_rank for l in lay], "top_rank": [l.top_rank for l in lay],
            "fall_dim": [l.fall_dim for l in lay], "d_ff": MAC.first_nonzero_fall(lay)}


# ------------------------------------------------------- object 1: p = 2 and p = 3
REFERENCE = {"full_rank": [0, 1, 6, 15], "top_rank": [0, 1, 2, 1],
             "fall_dim": [0, 0, 4, 14], "d_ff": 5}
obj1 = {"reference_profile_at_2_64_and_P256": REFERENCE}
for p in (2, 3, 5, 7, 11, 4099):
    rng = random.Random(31337 + p)
    mine, meters, zeros = {}, {}, []
    for _ in range(24):
        A, Bc, xr = (rng.randrange(p) for _ in range(3))
        v = stilde_values(A, Bc, xr, p)
        zeros.append(sum(1 for t in v if t % p == 0))
        pr = profile(poly_from_values(v, p), p)
        key = str({"full_rank": [x[0] for x in pr], "top_rank": [x[1] for x in pr]})
        mine[key] = mine.get(key, 0) + 1
        mp = meter_profile(A, Bc, xr, p)
        mkey = str({"full_rank": mp["full_rank"], "top_rank": mp["top_rank"]})
        meters[mkey] = meters.get(mkey, 0) + 1
    ref_key = str({"full_rank": REFERENCE["full_rank"], "top_rank": REFERENCE["top_rank"]})
    obj1[str(p)] = {"samples": 24, "own_code_profiles": mine, "meter_profiles": meters,
                    "own_equal_to_reference": mine.get(ref_key, 0),
                    "meter_equal_to_reference": meters.get(ref_key, 0),
                    "mean_zeros_on_cube": sum(zeros) / len(zeros),
                    "min_zeros": min(zeros), "max_zeros": max(zeros)}
out["object_1_digit_system_small_p"] = obj1

# --------------------------------- object 2: Wilson inclusion W_{1,3}, s = 6, p = 3
def wilson_rank(p, s=6, j=1, e=2):
    """rank of multiplication by ell^e = (sum a_i)^e from degree j to degree j+e in
    F_p[a_1..a_s]/(a_i^2)."""
    src = [sum(1 << i for i in c) for c in combinations(range(s), j)]
    tgt = {m: k for k, m in enumerate(sum(1 << i for i in c) for c in combinations(range(s), j + e))}
    # (sum a_i)^e in the squarefree-square algebra: e! * e_e(a) = e! * sum_{|S|=e} prod_S
    from math import factorial
    ellе = {sum(1 << i for i in c): factorial(e) % p for c in combinations(range(s), e)}
    rows = []
    for m in src:
        row = {}
        for mm, c in ellе.items():
            if mm & m: continue
            row[tgt[mm | m]] = (row.get(tgt[mm | m], 0) + c) % p
        rows.append({k: v for k, v in row.items() if v})
    return echelon_ranks(rows, p, 10 ** 9)[0]


out["object_2_wilson"] = {
    "map": "multiplication by ell^2, degree 1 -> 3, s = 6 variables, F_p[a]/(a^2)",
    "min_binom": min(len(list(combinations(range(6), 1))), len(list(combinations(range(6), 3)))),
    "rank_by_prime": {str(p): wilson_rank(p) for p in (2, 3, 5, 7, 11, 13, 4099)},
    "entry_content_gcd": 2, "note": "entries are 2! = 2 times a 0/1 inclusion matrix"}

# --------------------- exact content primes of the (2,2,3) TOP block (Smith divisors)
import sympy
def q_block(lo):
    a0, a1, a2 = 1 << lo, 1 << (lo + 1), 1 << (lo + 2)
    return {a0 | a1: 1, a0 | a2: 2, a1 | a2: 4}
top4 = {}
for m1, c1 in q_block(0).items():
    for m2, c2 in q_block(3).items():
        top4[m1 | m2] = 16 * c1 * c2

def topblock_matrix(D):
    tgt = {m: k for k, m in enumerate(sum(1 << i for i in c) for c in combinations(range(N), D))}
    rows = []
    for c in combinations(range(N), D - 4):
        mu = sum(1 << i for i in c)
        row = [0] * len(tgt)
        for m, v in top4.items():
            if m & mu: continue
            row[tgt[m | mu]] += v
        rows.append(row)
    return sympy.Matrix(rows)

sd = {}
for D in (4, 5, 6):
    Mx = topblock_matrix(D)
    from sympy.matrices.normalforms import invariant_factors
    inv = invariant_factors(Mx, domain=sympy.ZZ)
    sd[str(D)] = {"shape": [Mx.rows, Mx.cols], "invariant_factors": [int(x) for x in inv],
                  "primes_dividing_last_invariant_factor":
                      sorted(set(sympy.factorint(int(inv[-1])).keys())) if inv and int(inv[-1]) else []}
out["top_block_invariant_factors_over_Z"] = sd

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out",
                       "proves_too_much.json"), "w") as fh:
    json.dump(out, fh, indent=1, sort_keys=True)
print(json.dumps({k: v for k, v in out.items() if k != "meter_version_sha256"}, indent=1, sort_keys=True))
