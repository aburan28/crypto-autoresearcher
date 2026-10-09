"""Audit replay (not a new trial): reproduce EXP-CERTBIN-66e167 Stage-1 census_one exactly,
and classify each colliding pair as STRUCTURAL (per-generator Z[tau] identity: for every
generator j, c_j(lambda) == 0 mod r, so it holds for any choice of generators) or
GENUINE (a chance collision depending on the discrete logs of the generators)."""
import sys, json, random
from collections import defaultdict
import os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'experiments', 'EXP-CERTBIN-66e167', 'implementation'))
import run as R

cell = R.setup_cell(R.N19, R.MOD19, R.SEEDS["primary"], require_prime_r=True)
r = cell["r_work"]; curve = cell["curve"]
C19, E = R.smallest_C_eff(r)
table = R.build_dl_table(curve, cell["G"], r)
lam = R.lambda_of(curve, cell["G"], table, r)
out = {"r": r, "C_eff": C19, "birthday": E, "lambda": lam, "rows": []}
for seed_name in ("primary", "holdout"):
    seed = R.SEEDS[seed_name]
    for k in (2, 3):
        # --- verbatim replay of census_one's sampling ---
        rng = random.Random(seed + 17 * k)
        n = cell["n"]; gens = []; used = set()
        while len(gens) < k:
            x = rng.randrange(1, cell["F"].q)
            P = curve.lift_x(x)
            if P is None: continue
            Q = curve.mul(cell["order"] // r, P) if cell["order"] % r == 0 else curve.mul(4, P)
            if Q is None: continue
            if curve.mul(r, Q) is not None: continue
            key = R.point_key(Q)
            if key in used: continue
            used.add(key); gens.append(Q)
        pts = R.orbit_union(curve, gens, n)
        B = len(pts); Mtot = R.stars_and_bars(B, R.M)
        ranks = R.sample_multiset_ranks(rng, Mtot, C19)
        multisets = [R.unrank_multiset(rk, B, R.M) for rk in ranks]
        fibers = defaultdict(list)
        for ti, ms in enumerate(multisets):
            S = None
            for idx in ms: S = curve.add(S, pts[idx])
            fibers[R.point_key(S)].append(ti)
        pairs = [(m[a], m[b]) for m in fibers.values() for a in range(len(m)) for b in range(a+1, len(m))]
        # --- classification: each base point = s * tau^i * G_j ---
        rep = {}
        for j, G in enumerate(gens):
            P = G
            for i in range(n):
                for s, Qp in ((1, P), (-1, curve.neg(P))):
                    rep.setdefault(R.point_key(Qp), (j, s, i))
                P = R.frob_point(curve.F, P)
        lam_pow = [pow(lam, i, r) for i in range(n)]
        structural = genuine = 0; examples = []
        for a, b in pairs:
            c = [0] * k
            for idx in multisets[a]:
                j, s, i = rep[R.point_key(pts[idx])]; c[j] = (c[j] + s * lam_pow[i]) % r
            for idx in multisets[b]:
                j, s, i = rep[R.point_key(pts[idx])]; c[j] = (c[j] - s * lam_pow[i]) % r
            if all(v == 0 for v in c):
                structural += 1
                if len(examples) < 3:
                    examples.append([[rep[R.point_key(pts[i])] for i in multisets[a]], [rep[R.point_key(pts[i])] for i in multisets[b]]])
            else:
                genuine += 1
        out["rows"].append({"seed": seed_name, "k": k, "B": B, "raw_pairs": len(pairs),
            "structural_pairs": structural, "genuine_pairs": genuine,
            "genuine_over_birthday": genuine / E, "raw_over_birthday": len(pairs) / E,
            "structural_examples (j,sign,tau_exp)": examples})
print(json.dumps(out, indent=1))
