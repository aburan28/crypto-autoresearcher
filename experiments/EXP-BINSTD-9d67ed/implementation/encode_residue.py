#!/usr/bin/env python3
"""Dual-route residual nonlinear clause density after Karabina symmetrisation.

Null encode: Weil-descend S_3(x1, x2, xR) with x1, x2 independently in span(V).
Treated encode: Karabina symmetric-function form (P + xR S)^2 + xR P + B with
S, P independently in the same span(V) (KR-IC-8b9daa / KR-IC-955fd6 pin).

C_nl = number of Weil-bit equations that still contain a degree≥2 monomial
after deleting monomials whose variable support is contained in the pure-linear
pivot set (no Magma SAT detector).

N_var = |nonlinear_support \\ pivots| (same remaining-variable definition as
EXP-BINSTD-16ee30 encode_s3).

Twin A: packed-mask XOR elimination + mask clause count.
Twin B: dense row-echelon + frozenset-monomial clause count.
"""
from __future__ import annotations


def _pmul(F, P, Q):
    out = {}
    for m1, c1 in P.items():
        for m2, c2 in Q.items():
            m = tuple(sorted(set(m1) | set(m2)))
            out[m] = out.get(m, 0) ^ F.mul(c1, c2)
    return out


def _padd(*Ps):
    out = {}
    for P in Ps:
        for m, c in P.items():
            out[m] = out.get(m, 0) ^ c
    return out


def _pscal(F, P, c):
    return {m: F.mul(v, c) for m, v in P.items()}


def _psq(F, P):
    out = {}
    for m, c in P.items():
        out[m] = out.get(m, 0) ^ F.mul(c, c)
    return out


def mono_mask(m):
    s = 0
    for i in m:
        s |= 1 << i
    return s


def descend_unsym(F, B: int, basis: list[int], xR: int):
    """Null: S_3 in (x1, x2) each in span(basis). nv = 2*ell."""
    L = len(basis)
    X1 = {(j,): basis[j] for j in range(L) if basis[j]}
    X2 = {(L + j,): basis[j] for j in range(L) if basis[j]}
    s12 = _pmul(F, X1, X2)
    e1 = _padd(s12, _pscal(F, X1, xR), _pscal(F, X2, xR))
    S = _padd(_psq(F, e1), _pscal(F, s12, xR), {(): B})
    return _weil_bit_eqs(F, S, 2 * L)


def descend_karabina(F, B: int, basis: list[int], xR: int):
    """Treated: Karabina auxiliaries S=x1+x2, P=x1 x2 plus symmetric S3.

    Variable blocks (nv = 4*ell): x1 | x2 | S | P, each in span(basis).
    Equations (concatenated Weil-bit lists):
      (K1) (P + xR S)^2 + xR P + B   — F2-linear in (S,P) bits after squaring;
      (K2) S + x1 + x2                 — linear;
      (K3) P + x1 x2                   — bilinear residue (the density source).
    This is the in-Python residual-density meter, not a SAT detector.
    """
    L = len(basis)
    nv = 4 * L
    X1 = {(j,): basis[j] for j in range(L) if basis[j]}
    X2 = {(L + j,): basis[j] for j in range(L) if basis[j]}
    Svar = {(2 * L + j,): basis[j] for j in range(L) if basis[j]}
    Pvar = {(3 * L + j,): basis[j] for j in range(L) if basis[j]}
    e = _padd(Pvar, _pscal(F, Svar, xR))
    k1 = _padd(_psq(F, e), _pscal(F, Pvar, xR), {(): B})
    k2 = _padd(Svar, X1, X2)
    k3 = _padd(Pvar, _pmul(F, X1, X2))
    eqs1, _ = _weil_bit_eqs(F, k1, nv)
    eqs2, _ = _weil_bit_eqs(F, k2, nv)
    eqs3, _ = _weil_bit_eqs(F, k3, nv)
    eqs = eqs1 + eqs2 + eqs3
    meta = {"nv": nv, "neq": 3 * F.n, "L": L, "blocks": "x1|x2|S|P"}
    return eqs, meta


def _weil_bit_eqs(F, poly, nv: int):
    n = F.n
    eqs = [[] for _ in range(n)]
    for m, c in poly.items():
        if c == 0:
            continue
        mask = mono_mask(m)
        for k in range(n):
            if (c >> k) & 1:
                eqs[k].append(mask)
    meta = {"nv": nv, "neq": n, "n_terms": len(poly)}
    return eqs, meta


def _combine_masks(masks: list[int]) -> dict[int, int]:
    seen: dict[int, int] = {}
    for mask in masks:
        seen[mask] = seen.get(mask, 0) ^ 1
    return {m: b for m, b in seen.items() if b}


def _split_linear_nonlinear(eqs: list[list[int]], nv: int):
    linear_rows: list[list[int]] = []
    nonlinear_vars: set[int] = set()
    combined: list[dict[int, int]] = []
    for masks in eqs:
        seen = _combine_masks(masks)
        combined.append(seen)
        const = 0
        lin = [0] * nv
        higher = False
        for mask in seen:
            if mask == 0:
                const ^= 1
                continue
            pc = mask.bit_count() if hasattr(int, "bit_count") else bin(mask).count("1")
            if pc == 1:
                v = (mask & -mask).bit_length() - 1
                if 0 <= v < nv:
                    lin[v] ^= 1
            else:
                higher = True
                m = mask
                while m:
                    lsb = m & -m
                    v = lsb.bit_length() - 1
                    if v < nv:
                        nonlinear_vars.add(v)
                    m ^= lsb
        if (any(lin) or const) and not higher:
            linear_rows.append(lin)
    return linear_rows, nonlinear_vars, combined


def _pivots_a(rows: list[list[int]], nv: int) -> set[int]:
    packed = []
    for row in rows:
        w = 0
        for j, b in enumerate(row):
            if b:
                w |= 1 << j
        packed.append(w)
    pivots: set[int] = set()
    for col in range(nv):
        piv = None
        for i, w in enumerate(packed):
            if (w >> col) & 1:
                piv = i
                break
        if piv is None:
            continue
        pivots.add(col)
        pw = packed[piv]
        for i, w in enumerate(packed):
            if i != piv and ((w >> col) & 1):
                packed[i] ^= pw
        packed[piv] = 0
    return pivots


def _pivots_b(rows: list[list[int]], nv: int) -> set[int]:
    mat = [row[:] for row in rows]
    pivots: set[int] = set()
    row_i = 0
    for col in range(nv):
        piv = None
        for r in range(row_i, len(mat)):
            if mat[r][col]:
                piv = r
                break
        if piv is None:
            continue
        mat[row_i], mat[piv] = mat[piv], mat[row_i]
        pivots.add(col)
        for r in range(len(mat)):
            if r != row_i and mat[r][col]:
                mat[r] = [a ^ b for a, b in zip(mat[r], mat[row_i])]
        row_i += 1
        if row_i >= len(mat):
            break
    return pivots


def _mask_vars(mask: int, nv: int) -> set[int]:
    out = set()
    m = mask
    while m:
        lsb = m & -m
        v = lsb.bit_length() - 1
        if v < nv:
            out.add(v)
        m ^= lsb
    return out


def _cnl_nvar_from_combined(combined, nv: int, pivots: set[int], nonlinear_vars: set[int]):
    """Residual clause count after deleting monomials supported only on pivots."""
    c_nl = 0
    residual_nl_vars: set[int] = set()
    for seen in combined:
        has_nl = False
        for mask in seen:
            if mask == 0:
                continue
            pc = mask.bit_count() if hasattr(int, "bit_count") else bin(mask).count("1")
            if pc < 2:
                continue
            vs = _mask_vars(mask, nv)
            if vs and vs.issubset(pivots):
                continue
            has_nl = True
            residual_nl_vars |= vs - pivots
        if has_nl:
            c_nl += 1
    if residual_nl_vars:
        n_var = len(residual_nl_vars)
    elif nonlinear_vars:
        n_var = len(nonlinear_vars - pivots)
    else:
        n_var = nv - len(pivots)
    return c_nl, n_var


def _cnl_nvar_b_monomials(combined, nv: int, pivots: set[int], nonlinear_vars: set[int]):
    """Twin B: reconstruct frozenset monomials independently, then count."""
    c_nl = 0
    residual_nl_vars: set[int] = set()
    for seen in combined:
        monos = []
        for mask in seen:
            vs = frozenset(_mask_vars(mask, nv)) if mask else frozenset()
            deg = len(vs)
            monos.append((deg, vs))
        has_nl = False
        for deg, vs in monos:
            if deg < 2:
                continue
            if vs and vs <= pivots:
                continue
            has_nl = True
            residual_nl_vars |= set(vs) - pivots
        if has_nl:
            c_nl += 1
    if residual_nl_vars:
        n_var = len(residual_nl_vars)
    elif nonlinear_vars:
        n_var = len(nonlinear_vars - pivots)
    else:
        n_var = nv - len(pivots)
    return c_nl, n_var


def density(c_nl: int, n_var: int):
    if n_var > 0:
        return c_nl / n_var, False
    if c_nl == 0:
        return 0.0, False
    return None, True  # N_var=0 with leftover nonlinear clauses: artifact


def meter(eqs, nv: int) -> dict:
    lin_rows, nonlinear_vars, combined = _split_linear_nonlinear(eqs, nv)
    pa = _pivots_a(lin_rows, nv) if lin_rows else set()
    pb = _pivots_b(lin_rows, nv) if lin_rows else set()
    c_a, n_a = _cnl_nvar_from_combined(combined, nv, pa, nonlinear_vars)
    c_b, n_b = _cnl_nvar_b_monomials(combined, nv, pb, nonlinear_vars)
    d_a, art_a = density(c_a, n_a)
    d_b, art_b = density(c_b, n_b)
    ok = (c_a == c_b) and (n_a == n_b) and (art_a == art_b) and (pa == pb)
    if ok and not art_a:
        ok = d_a == d_b
    return {
        "ok": ok,
        "artifact": art_a or art_b,
        "C_nl_a": c_a,
        "C_nl_b": c_b,
        "N_var_a": n_a,
        "N_var_b": n_b,
        "density_a": d_a,
        "density_b": d_b,
        "pivots_a": sorted(pa),
        "pivots_b": sorted(pb),
        "nv": nv,
    }


def encode_pair(F, B: int, basis: list[int], xR: int) -> dict:
    eqs_u, meta_u = descend_unsym(F, B, basis, xR)
    eqs_k, meta_k = descend_karabina(F, B, basis, xR)
    null = meter(eqs_u, meta_u["nv"])
    treated = meter(eqs_k, meta_k["nv"])
    return {
        "null": null,
        "treated": treated,
        "twin_ok": bool(null["ok"] and treated["ok"] and not null["artifact"] and not treated["artifact"]),
        "meta_null": meta_u,
        "meta_treated": meta_k,
    }


def poly_basis(ell: int) -> list[int]:
    """Frozen encoder pin: span{1, t, t^2, ..., t^{ell-1}}."""
    return [1 << j for j in range(ell)]
