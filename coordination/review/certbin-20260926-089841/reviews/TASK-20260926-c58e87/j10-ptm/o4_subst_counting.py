"""O4 pre-engine substituted counting (TASK-20260926-c58e87). Own code only; NO ENGINE CALL.
For each system with a 1-dimensional left kernel c of the quadratic-column submatrix:
ell = sum c_k f_k; j* = least index of ell's linear support; pi: v_{j*} -> ell + v_{j*};
f'_k = pi(f_k) multilinearized, variables relabelled 0..16. P_sub = rank of the degree-4
projection of M'_4 (rows mu' f'_k, |mu'| = 2, 136 x 17; columns C(17,4) = 2380).
Also, for the unsubstituted system, the number e of 'ell-syzygies' sum_k c_k (ell+1) v_i f_k
= 0 (i = 0..17) independent of the 153 trivial syzygies (Koszul + field), by explicit vectors
over the 2924 Macaulay row indices (each vector also checked to be a syzygy).
Validation first: polynomial-basis S_3 at U62 idx 27 must give P_sub = 2213 - 834 = 1379
(RC-1 red-team R'_4 profile [1, 18, 154, 834, 2213]).
Usage: python3 o4_subst_counting.py <worktree> <j10-ptm dir>
"""
import itertools
import json
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import rtlib as R  # noqa: E402

wt, d = sys.argv[1], sys.argv[2]


def polys_of(E):
    return [set(R.COLMASK[c] for c in R.np.flatnonzero(E[k])) for k in range(17)]


def pmul(p, q):
    out = set()
    for a in p:
        for b in q:
            out ^= {a | b}
    return out


def ell_of(E):
    kd, c = R.left_kernel_dim_quadratic(E)
    if kd != 1:
        return kd, None, None
    polys = polys_of(E)
    ell = set()
    for k in range(17):
        if (c >> k) & 1:
            ell ^= polys[k]
    return kd, c, ell


def substitute(E, ell):
    lin = sorted(i for i in range(18) if (1 << i) in ell)
    if not lin:
        return None, None
    js = lin[0]
    a = set(ell) ^ {1 << js}  # affine form in the other variables
    out = []
    for p in polys_of(E):
        q = set()
        for m in p:
            if m & (1 << js):
                rest = m & ~(1 << js)
                q ^= pmul({rest}, a)
            else:
                q ^= {m}
        # relabel: drop bit js
        r = set()
        for m in q:
            low = m & ((1 << js) - 1)
            high = (m >> (js + 1)) << js
            r ^= {low | high}
        out.append(r)
    return js, out


def P_rank_masks(eqs, nv):
    deg4 = {m: i for i, m in enumerate(sum(1 << x for x in t) for t in itertools.combinations(range(nv), 4))}
    ech = R.Echelon()
    for t in itertools.combinations(range(nv), 2):
        mu = (1 << t[0]) | (1 << t[1])
        for f in eqs:
            x = 0
            for m in f:
                if R.popc(m) == 2 and (mu & m) == 0:
                    x ^= 1 << deg4[mu | m]
            if x:
                ech.add(x)
    return ech.dim()


def ell_syzygy_excess(E, c, ell):
    """rank(Triv + EllSyz) - rank(Triv) over row-index vectors (row index = mu_index*17 + k,
    mu over R.MUS2 order); each vector checked to be a syzygy."""
    polys = polys_of(E)
    muidx = {m: i for i, m in enumerate(R.MUS2)}

    def vec(k, g):  # coefficient vector of g * f_k (g of degree <= 2)
        x = 0
        for m in g:
            x ^= 1 << (muidx[m] * 17 + k)
        return x

    def is_syz(v):
        acc = set()
        r = v
        while r:
            lb = r & -r
            p = lb.bit_length() - 1
            r ^= lb
            mi, k = divmod(p, 17)
            acc ^= pmul({R.MUS2[mi]}, polys[k])
        return not acc

    triv = R.Echelon()
    for i in range(17):
        for j in range(i + 1, 17):
            triv.add(vec(i, polys[j]) ^ vec(j, polys[i]))
        triv.add(vec(i, polys[i] ^ {0}))
    base = triv.dim()
    ok = True
    extra = 0
    for i in range(18):
        g = pmul({1 << i}, ell ^ {0})
        v = 0
        for k in range(17):
            if (c >> k) & 1:
                v ^= vec(k, g)
        if v == 0:
            continue
        ok &= is_syz(v)
        if triv.add(v):
            extra += 1
    return base, extra, ok


res = {"validation": {}, "systems": []}
# validation on polynomial-basis S_3, U62 idx 27 (x_R 4418)
E0 = R.descent(4418, R.poly_basis())
kd, c, ell = ell_of(E0)
js, sub = substitute(E0, ell)
res["validation"] = {"x_R": 4418, "kernel_dim": kd, "j_star": js,
                     "ell_linear_support": sorted(i for i in range(18) if (1 << i) in ell),
                     "P_sub": P_rank_masks(sub, 17), "expected_P_sub_from_RC1": 2213 - 834,
                     "P_unsub": R.P_rank(E0)}
b, e, ok = ell_syzygy_excess(E0, c, ell)
res["validation"].update(trivial_rank=b, ell_syzygy_excess=e, ell_syzygies_are_syzygies=ok)
print("validation", res["validation"])

S = json.load(open(f"{d}/o4-systems.json"))
items = [(k["key"], k["s"], k["E_hex"]) for k in S["kept"] if "EXHAUSTED" not in k]
items += [(f"S3-VR:{dd['slot']}", dd["s"], dd["E_hex"]) for dd in S["descents"]]
for key, s, eh in items:
    E = R.hex_to_E(eh)
    kd, c, ell = ell_of(E)
    rec = {"key": key, "s": s, "kernel_dim": kd}
    if ell is not None:
        lin = sorted(i for i in range(18) if (1 << i) in ell)
        rec["ell_linear_support_size"] = len(lin)
        rec["ell_const"] = int(0 in ell)
        if lin:
            js, sub = substitute(E, ell)
            rec["j_star"] = js
            P = P_rank_masks(sub, 17)
            rec["P_sub"] = P
            rec["Z_sub"] = 2618 - P
            rec["Z_sub_minus_290"] = 2618 - P - 290
        b, e, ok = ell_syzygy_excess(E, c, ell)
        rec.update(trivial_rank=b, ell_syzygy_excess=e, ell_syzygies_are_syzygies=ok)
    res["systems"].append(rec)
    print(json.dumps(rec))
json.dump(res, open(f"{d}/o4-subst-counting.json", "w"), indent=1)
