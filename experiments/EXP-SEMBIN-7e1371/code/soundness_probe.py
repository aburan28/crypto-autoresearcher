#!/usr/bin/env python3
"""soundness_probe.py -- find the iteration at which the degree-capped closure
first produces a row that is NOT in the ideal.

Direct, not inferential. Every element of the ideal vanishes at every common
zero of the generators, so: run the closure for exactly `max_iter` iterations,
pull each basis row out with closure_row_masks, and evaluate it at a KNOWN
solution. A row that does not vanish there cannot be in the ideal, and the
iteration it first appears in localises the defect.

Usage: soundness_probe.py n k iters...      (m = t = 2 cells only)
"""
from __future__ import annotations

import ctypes
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import boolsys          # noqa: E402
import closure_cert     # noqa: E402
import solcount         # noqa: E402

_lib = closure_cert._lib
_lib.closure_row_masks.restype = ctypes.c_long
_lib.closure_rank.restype = ctypes.c_long
_lib.closure_ncols.restype = ctypes.c_long


def solution_assignment(inst):
    """One genuine common zero of the generators, as a Boolean bitmask over the
    N variables (x1 coordinates then x2 coordinates), via count_m2's lister."""
    lib = solcount._lib
    lib.list_m2.restype = ctypes.c_longlong
    lib.list_m2.argtypes = [ctypes.c_int, ctypes.c_uint64, ctypes.c_int,
                            ctypes.POINTER(ctypes.c_uint64), ctypes.c_uint64, ctypes.c_uint64,
                            ctypes.POINTER(ctypes.c_uint64), ctypes.c_long]
    basis = solcount._basis_array(inst["subspace_basis"])
    out = (ctypes.c_uint64 * 4096)()
    nf = lib.list_m2(inst["n"], inst["modulus"], inst["k"], basis,
                     inst["z"], inst["B"], out, 4096)
    if nf <= 0:
        return None, nf
    x1, x2 = out[0], out[1]
    bas = inst["subspace_basis"]

    def coords(x):
        red, tags = [], []
        for j, b in enumerate(bas):
            v, t = b, 1 << j
            for bv, bt in zip(red, tags):
                if v ^ bv < v:
                    v ^= bv
                    t ^= bt
            if v:
                red.append(v)
                tags.append(t)
        v, t = x, 0
        for bv, bt in zip(red, tags):
            if v ^ bv < v:
                v ^= bv
                t ^= bt
        return t if v == 0 else None

    c1, c2 = coords(x1), coords(x2)
    if c1 is None or c2 is None:
        return None, -2
    return c1 | (c2 << inst["k"]), nf


def evaluate(masks, assign):
    """Value at `assign` of the polynomial whose monomials are `masks`."""
    v = 0
    for m in masks:
        if (m & assign) == m:
            v ^= 1
    return v


def main():
    n, k = int(sys.argv[1]), int(sys.argv[2])
    iters = [int(x) for x in sys.argv[3:]] or [1, 2, 3]
    inst = boolsys.generate(n, 2, 2, k, "B_random", "low_degree_polynomial", 20260913101, 0)
    N, eqs = inst["N"], inst["equations"]
    s = solcount.count_chained(inst)["solutions"]
    assign, nf = solution_assignment(inst)
    print(f"cell ({n},2,2,{k})  N={N}  |V(I)|={s}  solutions listed={nf}")
    if assign is None:
        print("no solution available -- probe needs a solution-bearing instance")
        return
    bad = sum(1 for e in eqs if evaluate(e, assign))
    print(f"sanity: generators violated at the chosen zero = {bad} (must be 0)")
    if bad:
        return
    _lib.closure_eval_rows.restype = ctypes.c_long
    _lib.closure_eval_rows.argtypes = [ctypes.c_uint64, ctypes.POINTER(ctypes.c_long),
                                       ctypes.POINTER(ctypes.c_long)]
    for it in iters:
        res = closure_cert._run(N, 4, eqs, max_iter=it, mem_cap_gb=3.0)
        rank = _lib.closure_rank()
        fb, fc = ctypes.c_long(0), ctypes.c_long(0)
        offenders = _lib.closure_eval_rows(assign, ctypes.byref(fb), ctypes.byref(fc))
        first = (fb.value, fc.value, None) if offenders > 0 else None
        _lib.closure_free()
        tag = "SOUND" if offenders == 0 else f"*** {offenders} ROW(S) NOT IN THE IDEAL ***"
        print(f"  max_iter={it:>2}  status={res['status']:<20} rank={rank:>7} "
              f"drops={res.get('dropped_terms_above_D')}  {tag}", flush=True)
        if first:
            i, cnt, degs = first
            print(f"      first offending row: index {i} of {rank}, {cnt} monomials")
            break


if __name__ == "__main__":
    main()
