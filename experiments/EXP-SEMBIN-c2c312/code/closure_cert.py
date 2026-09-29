#!/usr/bin/env python3
"""closure_cert.py -- degree-capped Boolean closure certificate and the
GOAL-DREG-001-style single-level Macaulay rank, via libclosure.so (M4RI).

For a cap D >= max generator degree, W_D is the smallest subspace of the
Boolean ring truncated at degree D that contains the generators and is closed
under multiplication by monomials mu with deg(mu) + deg(f) <= D.  Its reduced
echelon basis G_D has the same leading-monomial ideal as the basis an F4 with
pair selection by degree holds after processing every pair of degree <= D
(truncated Buchberger criterion), so:

    G_D is a Groebner basis of the ideal  <=>  F4 completes with step degree <= D.

Verdict per D:
  * contains_one          -> SUFFICIENT (the ideal is the unit ideal, GB = {1}).
  * else count c of standard monomials of <LM(G_D)> (squarefree monomials not
    divisible by a leading monomial), capped.  In the Boolean ring every ideal
    is the vanishing ideal of its variety, so with s = |V(I)|:
        c == s  <=> G_D is a Groebner basis  -> SUFFICIENT
        c >  s                                -> INSUFFICIENT
    s comes from the F4 run's quotient dimension when that run completed, else
    from brute force over the free variables of G_D's linear rows when there are
    at most `brute_max_free` of them; otherwise the verdict is UNDETERMINED
    (recorded, never guessed).
  * closure_D = the smallest D with verdict SUFFICIENT.

The DREG statistic is the single-level Macaulay matrix at degree D: rows are
mu * g for the ORIGINAL generators only (deg mu <= D - deg g), no
re-multiplication; reported with the archived semi-regular prediction of
experiments/EXP-DREG-001/.../h012_peel_rank.py::semireg_rank_pred, copied
verbatim below.
"""
from __future__ import annotations

import ctypes
import hashlib
import itertools
import time
from array import array
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent
_lib = ctypes.CDLL(str(HERE / "libclosure.so"))
_lib.closure_run.restype = ctypes.c_int
_lib.closure_run.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_long, ctypes.c_void_p, ctypes.c_void_p,
                             ctypes.c_int, ctypes.c_double,
                             ctypes.POINTER(ctypes.c_long), ctypes.POINTER(ctypes.c_long),
                             ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p,
                             ctypes.POINTER(ctypes.c_long), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_long)]
_lib.closure_rank.restype = ctypes.c_long
_lib.closure_ncols.restype = ctypes.c_long
_lib.closure_lm_dump.argtypes = [ctypes.c_void_p]
_lib.closure_count_deg.restype = ctypes.c_long
_lib.closure_count_deg.argtypes = [ctypes.c_int]
_lib.closure_row_masks.restype = ctypes.c_long
_lib.closure_row_masks.argtypes = [ctypes.c_long, ctypes.c_void_p]
_lib.closure_standard_count.restype = ctypes.c_long
_lib.closure_standard_count.argtypes = [ctypes.c_long]
_lib.closure_free.restype = None


def semireg_rank_pred(eq_degs, nb, Dmax):
    """Verbatim from the archived GOAL-DREG-001 instrument (h012_peel_rank.py)."""
    a = [comb(nb, j) if j <= nb else 0 for j in range(Dmax + 2)]
    for d in eq_degs:
        for j in range(d, Dmax + 2):
            a[j] -= a[j - d]
    HF, ok = [], True
    for d in range(Dmax + 2):
        if not ok or a[d] <= 0:
            HF.append(0)
            if a[d] <= 0:
                ok = False
        else:
            HF.append(a[d])
    pred, tot = {}, 0
    for D in range(0, Dmax + 1):
        tot += comb(nb, D) - HF[D]
        pred[D] = tot
    return pred, HF


def _csr(equations):
    ptr = array("q", [0])
    masks = array("Q")
    for e in equations:
        masks.extend(e)
        ptr.append(len(masks))
    return ptr, masks


def _run(N, D, equations, max_iter, mem_cap_gb):
    ptr, masks = _csr(equations)
    n_it = max_iter + 2
    iter_rows = array("q", [0] * n_it)
    iter_rank = array("q", [0] * n_it)
    iter_new = array("q", [0] * n_it)
    iter_wall = array("d", [0.0] * n_it)
    ncols = ctypes.c_long(0)
    iters = ctypes.c_long(0)
    rank = ctypes.c_long(0)
    one = ctypes.c_int(0)
    maxrows = ctypes.c_long(0)
    pbuf = (ctypes.c_long * len(ptr)).from_buffer(ptr)
    mbuf = (ctypes.c_uint64 * max(1, len(masks))).from_buffer(masks) if len(masks) else (ctypes.c_uint64 * 1)()
    t0 = time.time()
    rc = _lib.closure_run(N, D, len(equations), ctypes.addressof(pbuf), ctypes.addressof(mbuf),
                          max_iter, float(mem_cap_gb * (1 << 30)),
                          ctypes.byref(ncols), ctypes.byref(iters),
                          (ctypes.c_long * n_it).from_buffer(iter_rows), (ctypes.c_long * n_it).from_buffer(iter_rank),
                          (ctypes.c_long * n_it).from_buffer(iter_new), (ctypes.c_double * n_it).from_buffer(iter_wall),
                          ctypes.byref(rank), ctypes.byref(one), ctypes.byref(maxrows))
    wall = time.time() - t0
    k = iters.value
    profile = [{"iteration": i, "rows": iter_rows[i], "rank_after": iter_rank[i],
                "new_pivots": iter_new[i], "wall_s": iter_wall[i]} for i in range(k)]
    return {"rc": rc, "ncols": ncols.value, "rank": rank.value, "contains_one": bool(one.value),
            "iterations": profile, "max_rows_seen": maxrows.value, "wall_s": wall,
            "status": "completed" if rc == 0 else ("unreached_memory_cap" if rc == 1 else "error")}


def _lm_stats(D):
    rank = _lib.closure_rank()
    lms = array("Q", [0] * max(1, rank))
    _lib.closure_lm_dump(ctypes.addressof((ctypes.c_uint64 * len(lms)).from_buffer(lms)))
    by_deg = {d: _lib.closure_count_deg(d) for d in range(0, D + 1)}
    h = hashlib.sha256()
    for x in lms[:rank]:
        h.update(int(x).to_bytes(8, "big"))
    return list(lms[:rank]), by_deg, h.hexdigest()


def _linear_rows(N, D):
    """Rows of the basis whose leading monomial has degree 1, as (mask lists)."""
    rank = _lib.closure_rank()
    ncols = _lib.closure_ncols()
    buf = array("Q", [0] * (ncols + 1))
    cbuf = (ctypes.c_uint64 * len(buf)).from_buffer(buf)
    lms, _, _ = _lm_stats(D)
    rows = []
    for i, lm in enumerate(lms):
        if lm and bin(lm).count("1") == 1:
            cnt = _lib.closure_row_masks(i, ctypes.addressof(cbuf))
            rows.append(list(buf[:cnt]))
    return rows


def _brute_solutions(N, equations, linear_rows, max_free):
    """Enumerate V(I) given linear rows of the basis (each vanishing on V(I)).
    Returns (count, note) or (None, note)."""
    # linear row: leading var (degree-1 monomial) = sum of other linear terms + const.
    # rows are in RREF so leading variables are distinct and do not appear in other rows' tails? (full RREF: yes)
    lead = {}
    for r in linear_rows:
        lv = r[0]
        assert bin(lv).count("1") == 1
        lead[lv.bit_length() - 1] = r[1:]
    free = [j for j in range(N) if j not in lead]
    if len(free) > max_free:
        return None, f"{len(free)} free variables > {max_free}"
    count = 0
    for bits in itertools.product((0, 1), repeat=len(free)):
        val = {}
        for j, b in zip(free, bits):
            val[j] = b
        # RREF: tails of linear rows involve only free variables and the constant
        ok = True
        for lv, tail in lead.items():
            v = 0
            for mm in tail:
                if mm == 0:
                    v ^= 1
                else:
                    j = mm.bit_length() - 1
                    if j not in val:
                        ok = False
                        break
                    v ^= val[j]
            if not ok:
                break
            val[lv] = v
        if not ok:
            return None, "linear rows not in solved form"
        # check all original equations
        good = True
        for e in equations:
            s = 0
            for mm in e:
                prod = 1
                x = mm
                while x:
                    j = (x & -x).bit_length() - 1
                    if not val[j]:
                        prod = 0
                        break
                    x &= x - 1
                s ^= prod
            if s:
                good = False
                break
        if good:
            count += 1
    return count, f"brute force over {len(free)} free variables"


def closure_certificate(N, equations, D, mem_cap_gb, s_known=None, standard_cap=100000,
                        brute_max_free=20, want_linear_rows=False):
    max_gen_deg = max(max((bin(mm).count("1") for mm in e), default=0) for e in equations)
    if D < max_gen_deg:
        return {"D": D, "status": "not_applicable", "reason": f"D < max generator degree {max_gen_deg}"}
    res = _run(N, D, equations, max_iter=64, mem_cap_gb=mem_cap_gb)
    out = {"D": D, "instrument": "closure", "field_equation_convention": "engine_implicit_boolean_ring", **res}
    if res["status"] != "completed":
        _lib.closure_free()
        return out
    lms, by_deg, lm_hash = _lm_stats(D)
    out["basis_leading_degree_counts"] = {str(k): v for k, v in by_deg.items()}
    out["basis_lm_sha256"] = lm_hash
    c = _lib.closure_standard_count(standard_cap)
    out["standard_monomials"] = c if c <= standard_cap else None
    out["standard_monomials_exceeds_cap"] = c > standard_cap
    s = s_known
    s_source = "f4_quotient_dimension" if s_known is not None else None
    if res["contains_one"]:
        out["verdict"] = "sufficient"
        out["verdict_basis"] = "1 in W_D"
        s = 0
        s_source = s_source or "closure_contains_one"
    else:
        if s is None:
            lin = _linear_rows(N, D)
            cnt, note = _brute_solutions(N, equations, lin, brute_max_free)
            if cnt is not None:
                s, s_source = cnt, note
        if s is None:
            out["verdict"] = "undetermined"
            out["verdict_basis"] = "|V(I)| unknown: F4 run incomplete and too many free variables for brute force"
        elif c > standard_cap:
            out["verdict"] = "insufficient"
            out["verdict_basis"] = f"standard monomials > {standard_cap} >= |V(I)| = {s}" if s <= standard_cap else "undetermined"
            if s > standard_cap:
                out["verdict"] = "undetermined"
        elif c == s:
            out["verdict"] = "sufficient"
            out["verdict_basis"] = f"standard monomials = |V(I)| = {s}"
        elif c > s:
            out["verdict"] = "insufficient"
            out["verdict_basis"] = f"standard monomials {c} > |V(I)| = {s}"
        else:
            out["verdict"] = "error"
            out["verdict_basis"] = f"standard monomials {c} < |V(I)| = {s}: impossible, instrument defect"
    out["solutions"] = s
    out["solutions_source"] = s_source
    if want_linear_rows:
        out["linear_rows"] = _linear_rows(N, D)
    _lib.closure_free()
    return out


def macaulay_single_level(N, equations, D, mem_cap_gb):
    res = _run(N, D, equations, max_iter=1, mem_cap_gb=mem_cap_gb)
    _lib.closure_free()
    eq_degs = [max((bin(mm).count("1") for mm in e), default=0) for e in equations if e]
    pred, HF = semireg_rank_pred(eq_degs, N, D)
    rows = res["iterations"][1]["rows"] if len(res["iterations"]) > 1 else res["iterations"][0]["rows"]
    return {"D": D, "instrument": "macaulay_single_level_DREG", "status": res["status"],
            "rows": rows, "cols": res["ncols"], "rank": res["rank"] if res["status"] == "completed" else None,
            "sr_pred_rank": pred[D], "sr_HF": HF[: D + 1],
            "deficit_vs_semiregular": (pred[D] - res["rank"]) if res["status"] == "completed" else None,
            "wall_s": res["wall_s"], "contains_one": res["contains_one"]}
