"""R3: the direct presentation's first fall is B + 2, the frozen 65/129 is d_reg = B + 1.

Independent dense implementation (2 free variables x1, x2; generators
S_3(x1, x2, x_R) of degree 4 and f_V(x_k) = prod_{v<B}(x_k - v) of degree B).
Columns ordered by total degree with the top block LAST, pivot = highest column,
so full_rank / top_rank / fall_dim carry the meter's documented semantics.
"""
import json, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rt_digit import echelon_ranks

out = {}


def s3_bivariate(A, Bc, xr, p):
    """{(i, j): c} for S_3(x1, x2, x_R)"""
    d = {}
    def add(i, j, c):
        d[(i, j)] = (d.get((i, j), 0) + c) % p
    add(2, 0, xr * xr); add(1, 1, -2 * xr * xr); add(0, 2, xr * xr)
    add(2, 1, -2 * xr); add(1, 2, -2 * xr); add(1, 0, -2 * xr * A); add(0, 1, -2 * xr * A)
    add(0, 0, -4 * xr * Bc)
    add(2, 2, 1); add(1, 1, -2 * A); add(0, 0, A * A)
    add(1, 0, -4 * Bc); add(0, 1, -4 * Bc)
    return {k: v for k, v in d.items() if v}


def fV(var, B, p):
    """prod_{v<B}(x_var - v) as {(i, j): c}"""
    poly = {(0, 0): 1}
    for v in range(B):
        nxt = {}
        for (i, j), c in poly.items():
            k = (i + 1, j) if var == 0 else (i, j + 1)
            nxt[k] = (nxt.get(k, 0) + c) % p
            nxt[(i, j)] = (nxt.get((i, j), 0) - c * v) % p
        poly = {k: c for k, c in nxt.items() if c}
    return poly


def columns(D):
    cols = [(i, D0 - i) for D0 in range(D + 1) for i in range(D0 + 1)]
    return {m: k for k, m in enumerate(cols)}, len(cols) - (D + 1), len(cols)


def layers(gens, p, dmin, dmax):
    res = {}
    for D in range(dmin, dmax + 1):
        idx, top_start, ncols = columns(D)
        rows = []
        for g in gens:
            dg = max(i + j for i, j in g)
            md = D - dg
            if md < 0: continue
            for i in range(md + 1):
                mu = (i, md - i)
                row = {}
                for (a, b), c in g.items():
                    col = idx[(a + mu[0], b + mu[1])]
                    row[col] = (row.get(col, 0) + c) % p
                rows.append({k: v for k, v in row.items() if v})
        full, top = echelon_ranks(rows, p, top_start)
        res[D] = {"rows": len(rows), "ncols_top": D + 1, "full_rank": full,
                  "top_rank": top, "fall_dim": full - top}
    return res


def scan(B, p, seed=5):
    rng = random.Random(seed)
    A, Bc = rng.randrange(p), rng.randrange(p)
    xr = rng.randrange(p)
    gens = [s3_bivariate(A, Bc, xr, p), fV(0, B, p), fV(1, B, p)]
    res = layers(gens, p, 4, B + 3)
    first_fall = next((D for D in sorted(res) if res[D]["fall_dim"] > 0), None)
    d_top_full = next((D for D in sorted(res) if res[D]["top_rank"] == res[D]["ncols_top"]), None)
    return {"B": B, "p": p, "A": A, "Bc": Bc, "x_R": xr, "first_fall_d_ff": first_fall,
            "B_plus_2": B + 2, "d_top_full": d_top_full, "B_plus_1": B + 1,
            "fall_dim_at_first_fall": res[first_fall]["fall_dim"] if first_fall else None,
            "any_fall_below_B_plus_2": [D for D in sorted(res) if res[D]["fall_dim"] > 0 and D < B + 2]}


small = []
for B in (4, 5, 6, 8, 10, 12):
    for p in (4099, 16411, 1000003):
        small.append(scan(B, p))
out["small_B_scan"] = small

# the two contract cells, reproduced independently
out["contract_cells"] = [scan(64, 4099), scan(128, 16411)]
# p-independence of the first fall at FIXED B (the axis the control does NOT test)
out["fixed_B_across_p"] = [scan(8, p) for p in (4099, 16411, (1 << 64) - 59)]

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out",
                       "r3_direct_firstfall.json"), "w") as fh:
    json.dump(out, fh, indent=1, sort_keys=True)
print(json.dumps(out, indent=1, sort_keys=True))
