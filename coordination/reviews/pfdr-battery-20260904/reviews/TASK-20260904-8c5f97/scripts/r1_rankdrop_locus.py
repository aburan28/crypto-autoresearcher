"""R1: the EXACT rank-drop locus of the (2,2,3) digit system, and an exhaustive
search over the whole x_R axis at p = 4099 for a rank-drop point.

Derivation being tested (see note-r1-minor-degree-and-rank-drop-locus.md):
  * top_rank(D) is parameter-free -> can never drop for p odd;
  * full_rank(D) = rank of the degree-(D-4) squarefree monomial evaluation
    matrix on supp(S~) subset {0,1}^6, so a drop at D needs
    |Z(S~)| >= 2^{6-(D-4)} zeros (multilinear minimum-weight bound):
    D = 4 -> 64, D = 5 -> 32, D = 6 -> 16.
For fixed (A, B) every cube point contributes a QUADRATIC in x_R, so the whole
x_R axis is searched exactly by root-finding: <= 2 roots per cube point.
"""
import json, os, random, sys
from itertools import combinations
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rt_digit import N, ell, stilde_values, poly_from_values, profile, echelon_ranks

P4099 = 4099
out = {}


def sqrt_mod_p3mod4(a, p):
    a %= p
    if a == 0: return 0
    r = pow(a, (p + 1) // 4, p)
    return r if r * r % p == a else None


def zero_multiplicity_over_all_xR(A, Bc, p):
    """Exhaustive over x_R in F_p: multiset of (x_R -> number of cube points where S~ = 0).
    Returns (max_count, argmax_xR, count_of_always_zero_points)."""
    counts = {}
    always = 0
    for v in range(1 << N):
        x1, x2 = ell(v, 0), ell(v, 3)
        c2 = (x1 - x2) ** 2 % p
        c1 = (-2 * ((x1 + x2) * (x1 * x2 + A) + 2 * Bc)) % p
        c0 = ((x1 * x2 - A) ** 2 - 4 * Bc * (x1 + x2)) % p
        if c2 == 0 and c1 == 0 and c0 == 0:
            always += 1
            continue
        roots = []
        if c2 == 0:
            if c1: roots = [(-c0) * pow(c1, -1, p) % p]
        else:
            disc = (c1 * c1 - 4 * c2 * c0) % p
            r = sqrt_mod_p3mod4(disc, p)
            if r is not None:
                inv = pow(2 * c2 % p, -1, p)
                roots = list({(-c1 + r) * inv % p, (-c1 - r) * inv % p})
        for x in roots:
            counts[x] = counts.get(x, 0) + 1
    if not counts:
        return always, None, always
    best = max(counts, key=counts.get)
    return counts[best] + always, best, always


# ---- 1. the eight contract curves at p = 4099, exhaustively over all x_R ----
with open("/home/user/crypto-autoresearcher/experiments/EXP-PFDR-fd901a/runs/"
          "RUN-PFDR-fd901a-sweep-p4099/raw-result.json") as fh:
    raw = json.load(fh)["raw"]
contract = []
for c in raw["curves"] + raw["singular_cubics"]:
    m, x, alw = zero_multiplicity_over_all_xR(c["a"], c["b"], P4099)
    contract.append({"seed": c["seed"], "kind": c.get("kind", "singular"), "a": c["a"], "b": c["b"],
                     "max_zeros_over_all_xR": m, "argmax_xR": x, "identically_zero_points": alw})
out["contract_curves_exhaustive_xR_p4099"] = contract

# ---- 2. 20000 random curves at p = 4099, each exhaustive over all x_R -------
rng = random.Random(20260904)
hist = {}
worst = None
for _ in range(20000):
    A = rng.randrange(P4099); Bc = rng.randrange(P4099)
    if (4 * A ** 3 + 27 * Bc ** 2) % P4099 == 0: continue
    m, x, alw = zero_multiplicity_over_all_xR(A, Bc, P4099)
    hist[str(m)] = hist.get(str(m), 0) + 1
    if worst is None or m > worst[0]: worst = (m, A, Bc, x)
out["random_curves_exhaustive_xR_p4099"] = {
    "curves": sum(hist.values()), "targets_per_curve": P4099,
    "curve_target_pairs_searched": sum(hist.values()) * P4099,
    "max_zero_count_histogram": hist,
    "worst_case": {"zeros": worst[0], "a": worst[1], "b": worst[2], "x_R": worst[3]}}

# profile at the worst case found
v = stilde_values(worst[1], worst[2], worst[3], P4099)
pr = profile(poly_from_values(v, P4099), P4099)
out["worst_case_profile_p4099"] = {"zeros": sum(1 for t in v if t == 0),
                                   "profile_full_top_fall": pr}

# ---- 3. minimum-weight threshold, checked empirically -----------------------
def rank_on_subset(keep, deg):
    rows = []
    for c in combinations(range(N), deg):
        mu = sum(1 << i for i in c)
        rows.append({j: 1 for j, w in enumerate(keep) if (w & mu) == mu})
    return echelon_ranks(rows, P4099, 10 ** 9)[0]


rng2 = random.Random(11)
mw = {}
for zeros in (15, 16, 20, 31, 32, 40):
    drops = 0
    for _ in range(300):
        Z = set(rng2.sample(range(64), zeros))
        keep = [v for v in range(64) if v not in Z]
        deg = 2 if zeros < 32 else 1
        want = 15 if deg == 2 else 6
        drops += (rank_on_subset(keep, deg) < want)
    mw[str(zeros)] = {"random_zero_sets": 300, "degree": deg, "rank_drops": drops}
out["minimum_weight_empirical"] = mw
# an explicit witness at the threshold: Z = {v : a_0 = a_1 = 1} has 16 points and
# kills the quadratic a_0 a_1
keep = [v for v in range(64) if not (v & 1 and v & 2)]
out["explicit_threshold_witness"] = {"zeros": 64 - len(keep),
                                     "rank_deg2_on_support": rank_on_subset(keep, 2),
                                     "expected_full": 15}

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out",
                       "r1_rankdrop_locus.json"), "w") as fh:
    json.dump(out, fh, indent=1, sort_keys=True)
print(json.dumps(out, indent=1, sort_keys=True)[:4000])
