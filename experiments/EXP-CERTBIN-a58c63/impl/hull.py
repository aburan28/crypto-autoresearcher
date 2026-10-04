"""Regime-A hull accounting (new; H-CERTBIN-7c3a18, EXP-CERTBIN-3f06d1-style
checks): the affine hull H = h_0 + W of a family's non-degenerate targets'
r-vectors, K_rank over F_2^n and K_rank_hull = rank(a_k restricted to W),
Sigma and Sigma_H computed exactly, C-FORMS (second evaluation path), C-SURV,
C-HZERO, the pivot-hazard table and HEUR-CERTBIN-TS1R's evaluation set with
exact 99.9% bands (statsx)."""
from fractions import Fraction

import numpy as np

from statsx import binom_band_half, binom_tail_exact, frac_log10


def echelon(vals):
    """Reduced basis dict {top bit: vector} of the F_2-span of ints."""
    basis = {}
    for v in vals:
        v = int(v)
        while v:
            h = v.bit_length() - 1
            if h in basis:
                v ^= basis[h]
            else:
                basis[h] = v
                break
    return basis


def reduce(v, basis):
    v = int(v)
    while v:
        h = v.bit_length() - 1
        if h in basis:
            v ^= basis[h]
        else:
            break
    return v


def in_span(v, basis):
    v = int(v)
    for h in sorted(basis, reverse=True):
        if (v >> h) & 1:
            v ^= basis[h]
    return v == 0


def parity(x):
    return bin(x).count("1") & 1


class Hull:
    def __init__(self, rs):
        rs = [int(r) for r in rs]
        self.h0 = rs[0] if rs else 0
        b = echelon([r ^ self.h0 for r in rs])
        self.Wbasis = [b[h] for h in sorted(b, reverse=True)]
        self.dimW = len(self.Wbasis)
        self._b = b
        self.zero_in_H = in_span(self.h0, b)

    def restrict(self, a):
        """a restricted to W, as the dimW-bit vector (<a, w_i>)_i."""
        v = 0
        for i, w in enumerate(self.Wbasis):
            if parity(int(a) & w):
                v |= 1 << i
        return v

    def contains(self, r):
        return in_span(int(r) ^ self.h0, self._b)


def solve_affine(rows, rhs, nvars):
    """Solve {<rows_k, z> = rhs_k} over F_2 (rows as ints of nvars bits).
    Returns (consistent, rank, particular solution, reduced system list)."""
    piv = {}  # pivot bit -> (row, rhs)
    for a, b in zip(rows, rhs):
        a, b = int(a), int(b)
        while a:
            h = a.bit_length() - 1
            if h in piv:
                pa, pb = piv[h]
                a ^= pa
                b ^= pb
            else:
                piv[h] = (a, b)
                break
        if a == 0 and b == 1:
            return False, None, None, None
    # back substitution: set free variables to 0
    z = 0
    for h in sorted(piv):
        a, b = piv[h]
        val = b ^ parity(a & z & ~(1 << h))
        if val:
            z |= 1 << h
    return True, len(piv), z, piv


def check_reduced(piv, z):
    return all(parity(a & z) == b for a, b in piv.values())


def analyze_ref(hull, a0, a, n, fz_scored, ids_scored, rs_scored):
    """One reference: K_rank, K_rank_hull, Sigma, Sigma_H, C-SURV, C-HZERO and
    the per-pivot hazard rows. fz_scored: first replay-zero index per scored
    target (K = survived all)."""
    K = len(a)
    a = [int(x) for x in a]
    a0 = [int(x) for x in a0]
    nz = [x for x in a if x]
    K_rank = len(echelon(nz))
    restr = [hull.restrict(x) for x in a]
    K_rank_hull = len(echelon([x for x in restr if x]))
    # Sigma over F_2^n
    ok, rk, zpart, piv = solve_affine(a, [1 ^ b for b in a0], n)
    sigma = {"consistent": ok, "rank": rk, "dim": (n - rk) if ok else None}
    # Sigma_H: r = h0 + sum z_i w_i
    rhs_h = [1 ^ b ^ parity(x & hull.h0) for b, x in zip(a0, a)]
    okh, rkh, zh, pivh = solve_affine(restr, rhs_h, hull.dimW)
    sigma_h = {"consistent": okh, "rank_restricted": rkh, "dim": (hull.dimW - rkh) if okh else None}
    # C-SURV
    fz = np.asarray(fz_scored, dtype=np.int64)
    surv = int((fz == K).sum())
    in_sigma = 0
    in_sigma_h = 0
    for r in rs_scored:
        r = int(r)
        if ok and check_reduced(piv, r):
            in_sigma += 1
            if hull.contains(r):
                in_sigma_h += 1
    csurv = {"survivors_full_replay": surv, "targets_in_Sigma": in_sigma, "targets_in_Sigma_H": in_sigma_h,
             "pass": surv == in_sigma == in_sigma_h}
    # hazards
    counts = np.bincount(fz, minlength=K + 1)
    geq = np.cumsum(counts[::-1])[::-1]
    Sk = geq[:K]
    zk = counts[:K]
    span = {}
    incr = []
    for k in range(K):
        v = restr[k]
        vr = reduce(v, span)
        if vr:
            span[vr.bit_length() - 1] = vr
            incr.append(1)
        else:
            incr.append(0)
    hz_viol = [k for k in range(K) if not incr[k] and Sk[k] > 0 and zk[k] != 0]
    return {"K": K, "K_exact": len(nz), "K_rank": K_rank, "K_rank_hull": K_rank_hull, "dimW": hull.dimW,
            "zero_in_H": hull.zero_in_H, "Sigma": sigma, "Sigma_H": sigma_h, "C-SURV": csurv,
            "C-HZERO": {"violations": hz_viol, "pass": not hz_viol,
                        "n_dependent_with_survivors": int(sum(1 for k in range(K) if not incr[k] and Sk[k] > 0))},
            "_Sk": Sk, "_zk": zk, "_incr": incr, "_restr": restr, "_fz": fz}


def forms_first_zero_matmul(a0, a, rs, n):
    """C-FORMS second path: e = a0 + R A^T (mod 2) by integer matrix product,
    first zero per target (K if none)."""
    K = len(a)
    if len(rs) == 0:
        return np.zeros(0, dtype=np.int64)
    bits = np.arange(n)
    Rm = ((np.asarray([int(r) for r in rs], dtype=np.int64)[:, None] >> bits[None, :]) & 1).astype(np.int64)
    Am = ((np.asarray([int(x) for x in a], dtype=np.int64)[:, None] >> bits[None, :]) & 1).astype(np.int64)
    e = (Rm @ Am.T + np.asarray(a0, dtype=np.int64)[None, :]) % 2
    z = e == 0
    return np.where(z.any(axis=1), z.argmax(axis=1), K).astype(np.int64)


def family_hull_analysis(unit, n, eval_min=100):
    """unit: regime-A result dict of one (family, D). Uses the family's
    non-degenerate targets for the hull; every reference with forms
    (own and cross) is analysed. Returns (summary, hazards-per-ref, cforms)."""
    recs = unit["records"]
    nd = [r for r in recs if not r["degenerate"] and r["x_R"] is not None]
    if not nd:
        return None, None, None
    hull = Hull([r["x_R"] for r in nd])
    out = {"dimW": hull.dimW, "zero_in_H": hull.zero_in_H, "h0": hull.h0, "W_basis": hull.Wbasis,
           "n_targets_hull": len(nd), "refs": {}}
    hazards = {}
    cforms = {"pairs_checked": 0, "mismatches": []}
    refs = unit.get("_ref_forms", {})
    band_cache = {}
    evalset = {}
    for key, fv in refs.items():
        a0, a = fv[0], fv[1]
        xref = fv[2] if len(fv) > 2 else None
        if key == "modal" or key.endswith(":modal"):
            scored = [r for r in nd if r["idx"] > 100] if key == "modal" else nd
        else:
            scored = nd
        scored = [r for r in scored if key in r["refs"]]
        fz = [r["refs"][key]["replay_first_zero"] for r in scored]
        rs = [r["x_R"] for r in scored]
        fz2 = forms_first_zero_matmul(a0, a, rs, n)
        cforms["pairs_checked"] += len(fz)
        bad = [(r["idx"], int(x), int(y)) for r, x, y in zip(scored, fz, fz2) if x != y]
        if bad:
            cforms["mismatches"].append({"ref": key, "n": len(bad), "first": bad[:10]})
        an = analyze_ref(hull, a0, a, n, fz, [r["idx"] for r in scored], rs)
        Sk, zk, incr, restr = an.pop("_Sk"), an.pop("_zk"), an.pop("_incr"), an.pop("_restr")
        fza = an.pop("_fz")
        ids = np.array([r["idx"] for r in scored], dtype=np.int64)
        rows = []
        for k in range(an["K"]):
            S = int(Sk[k])
            row = {"k": k, "a_k": int(a[k]), "a0_k": int(a0[k]), "a_k_restricted": int(restr[k]),
                   "hull_rank_increasing": bool(incr[k]), "S_k": S, "zeros": int(zk[k]),
                   "h_k": (str(Fraction(int(zk[k]), S)) if S else None)}
            if incr[k] and S >= eval_min:
                if S not in band_cache:
                    band_cache[S] = binom_band_half(S)
                lo, hi = band_cache[S]
                row["band_999"] = [lo, hi]
                row["in_band"] = lo <= int(zk[k]) <= hi
                surv_ids = ids[fza >= k]
                skey = (int(restr[k]), surv_ids.tobytes())
                if skey not in evalset:
                    evalset[skey] = {"ref": key, "k": k, "S_k": S, "zeros": int(zk[k]), "band": [lo, hi],
                                     "in_band": row["in_band"], "also_at": []}
                else:
                    evalset[skey]["also_at"].append([key, k])
            rows.append(row)
        hazards[key] = rows
        an["r_ref"] = xref
        an["r_ref_in_hull"] = (hull.contains(xref) if xref is not None else None)
        an["C-HZERO"]["premise_note"] = ("Lemma 3's hazard-0 identity presumes a point of the survivor coset in H with e_k = 1 "
                                         "(e.g. r_ref in H); r_ref_in_hull is recorded as a diagnostic")
        out["refs"][key] = an
    m = len(evalset)
    o = sum(1 for v in evalset.values() if not v["in_band"])
    if m:
        tail = binom_tail_exact(m, Fraction(1, 1000), o)
    else:
        tail = None
    ts1r = {"m": m, "o": o, "P_Bin_m_0.001_ge_o": (str(tail) if tail is not None else None),
            "log10_P": (frac_log10(tail) if tail not in (None, 0) else None),
            "P_float": (float(tail) if tail is not None else None),
            "verdict_RR4": ("NOT EVALUABLE (m < 5)" if m < 5 else
                            ("SUPPORTED" if tail >= Fraction(1, 1000) else "FALSIFIED")),
            "measurements": list(evalset.values()),
            "n_rep_dependent_with_S_ge_100": sum(1 for rows in hazards.values() for r in rows
                                                 if not r["hull_rank_increasing"] and r["S_k"] >= eval_min),
            "n_rep_dependent_with_S_ge_100_nonzero_h": sum(1 for rows in hazards.values() for r in rows
                                                          if not r["hull_rank_increasing"] and r["S_k"] >= eval_min
                                                          and r["zeros"] != 0)}
    out["TS1R"] = ts1r
    return out, hazards, cforms
