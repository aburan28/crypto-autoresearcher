"""R4: two mutations that separate the two halves of the reported profile.

M1  zero-set- and support-preserving: random coefficients on the SAME 49
    monomials, constrained to vanish at exactly the same planted cube points.
    Prediction if full_rank is a function of the point set alone: full_rank
    unchanged, top_rank@5 moves 2 -> 6, i.e. the mutant reproduces the NULL
    arm's profile exactly.
M2  top-form-preserving, structure-destroying: keep the degree-4 part
    16 Q_1 Q_2 and randomise every sub-top coefficient (no curve, no target,
    no decomposition).  Prediction: the Semaev arm's profile exactly.
"""
import json, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rt_digit import N, stilde_values, poly_from_values, profile

REPO = "/home/user/crypto-autoresearcher"
P4099, P64 = 4099, (1 << 64) - 59
P256 = 2**256 - 2**224 + 2**192 + 2**96 - 1
out = {}


def evaluate(poly, v, p):
    return sum(c for m, c in poly.items() if (m & v) == m) % p


def q_block(lo):
    a0, a1, a2 = 1 << lo, 1 << (lo + 1), 1 << (lo + 2)
    return {a0 | a1: 1, a0 | a2: 2, a1 | a2: 4}


TOP4 = {}
for m1, c1 in q_block(0).items():
    for m2, c2 in q_block(3).items():
        TOP4[m1 | m2] = 16 * c1 * c2


def mutate_same_zeroset(poly, zeros, p, rng):
    """random coefficients on the same monomials, vanishing on `zeros`"""
    mons = sorted(poly)
    for _ in range(200):
        c = {m: rng.randrange(1, p) for m in mons}
        # solve for two coefficients so that the two zero conditions hold
        z1, z2 = zeros
        cand = [m for m in mons if (m & z1) == m or (m & z2) == m]
        for i in range(len(cand)):
            for j in range(i + 1, len(cand)):
                m1, m2 = cand[i], cand[j]
                a11 = 1 if (m1 & z1) == m1 else 0
                a12 = 1 if (m2 & z1) == m2 else 0
                a21 = 1 if (m1 & z2) == m1 else 0
                a22 = 1 if (m2 & z2) == m2 else 0
                det = (a11 * a22 - a12 * a21) % p
                if det == 0:
                    continue
                rest = {m: c[m] for m in mons if m not in (m1, m2)}
                b1 = -sum(v for m, v in rest.items() if (m & z1) == m) % p
                b2 = -sum(v for m, v in rest.items() if (m & z2) == m) % p
                inv = pow(det, -1, p)
                x1 = (a22 * b1 - a12 * b2) * inv % p
                x2 = (-a21 * b1 + a11 * b2) * inv % p
                if x1 == 0 or x2 == 0:
                    continue
                out_ = dict(rest); out_[m1] = x1; out_[m2] = x2
                vals = [evaluate(out_, v, p) for v in range(1 << N)]
                if [v for v in range(1 << N) if vals[v] == 0] == sorted(zeros) and \
                        max(bin(m).count("1") for m in out_ if out_[m]) == 4:
                    return out_
    return None


for run, p in (("RUN-PFDR-fd901a-sweep-p4099", P4099), ("RUN-PFDR-fd901a-sweep-p64", P64),
               ("RUN-PFDR-fd901a-sweep-p256", P256)):
    with open(os.path.join(REPO, "experiments/EXP-PFDR-fd901a/runs", run, "raw-result.json")) as fh:
        raw = json.load(fh)["raw"]
    curves = {c["seed"]: c for c in raw["curves"]}
    cubics = {c["seed"]: c for c in raw["singular_cubics"]}
    rng = random.Random(2026)
    m1_prof, m2_prof, n1, n2 = {}, {}, 0, 0
    for d in raw["draws"]:
        if d["arm"] != "semaev":
            continue
        c = curves[d["curve_seed"]]
        vals = stilde_values(c["a"], c["b"], d["x_R"], p)
        poly = poly_from_values(vals, p)
        zeros = [v for v in range(1 << N) if vals[v] % p == 0]
        mut = mutate_same_zeroset(poly, zeros, p, rng)
        if mut is not None:
            pr = profile(mut, p)
            k = str([list(x[:2]) for x in pr]); m1_prof[k] = m1_prof.get(k, 0) + 1; n1 += 1
        sub = {m: rng.randrange(0, p) for m in poly if bin(m).count("1") < 4}
        mut2 = {m: v % p for m, v in list(TOP4.items()) + list(sub.items()) if v % p}
        pr2 = profile(mut2, p)
        k2 = str([list(x[:2]) for x in pr2]); m2_prof[k2] = m2_prof.get(k2, 0) + 1; n2 += 1
    zc = {}
    for d in raw["draws"]:
        if d["arm"] != "noncurve_cubic":
            continue
        c = cubics[d["curve_seed"]]
        v = stilde_values(c["a"], c["b"], d["x_R"], p)
        z = sum(1 for t in v if t % p == 0)
        zc[str(z)] = zc.get(str(z), 0) + 1
    out[str(p)] = {"M1_same_zeroset_same_support": {"draws": n1, "profiles": m1_prof},
                   "M2_same_top_form_random_subtop": {"draws": n2, "profiles": m2_prof},
                   "semaev_recorded_profile": "[[0, 0], [1, 1], [6, 2], [15, 1]]",
                   "null_recorded_profile": "[[0, 0], [1, 1], [6, 6], [15, 1]]",
                   "noncurve_zero_counts": zc}

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out",
                       "r4_pointset_mutation.json"), "w") as fh:
    json.dump(out, fh, indent=1, sort_keys=True)
print(json.dumps(out, indent=1, sort_keys=True))
