"""EXP-PFDR-0b3699 P0 step (1): the design curves (TASK-20261002-8a6b8a).

    <PY> experiments/EXP-PFDR-0b3699/design_a.py --bits 30 32 --c0 2010 --n-per-rung 6800 \
        --workers 4 --out experiments/EXP-PFDR-0b3699/runs/RUN-PFDR-0b3699-p0-design/curves.jsonl.gz

For every candidate design curve (bits, c) it records, from design quantities only and
before any census run of this experiment:

* the curve (p, a, b, N, P) of generate_prime_order_curve(bits, c,
  p_filter=subgroup_prime_filter([3, 4, 5], 0.15)) (EXP-PFDR-011cd0 cells.design_curves);
* size0 = default_fb_size(N, 4), |F_sub| of FactorBase.subgroup(E, size0, c) and
  s_sub = max(4, |F_sub|);
* mu_model(j) = T (T - 1) / (3 N) with T = s_sub^2 (L1 first moment, generic multiplicity 3
  of L2; implementation-notes PDI-1);
* x0 of the small_x_offset base, recomputed independently with the standard random module
  and the builder's label "fb-smallx-offset|{p}|{a}|{b}|{size}|{seed}", seed c + 9000, and
  the offset walk (first s_sub x >= x0 with x^3 + a x + b a nonzero square, by Euler's
  criterion -- not by factor_base.py);
* the height screen: every x of the offset base with x * v mod p in [-2^12, 2^12] for some
  v in 1..16 (controls_design_notes.offset_range_and_height_screen);
* whether planted_sub plants (FactorBase.planted(E, s_sub, seed = c + 8000); a ValueError is
  a design stop) and its n_tt.

Imports curve.py and factor_base.py only (inputs.experiment_scripts_new).  Writes
curves.jsonl.gz (gzip -n style: mtime 0, no name), sorted by (bits, c).  Nothing is
interpreted.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import importlib.util
import io
import json
import os
import random
import sys
import types
from concurrent.futures import ProcessPoolExecutor

REPO = "/home/user/crypto-autoresearcher"
ENGINE_DIR = os.path.join(REPO, "src/crypto_autoresearcher/index_calculus")
_PKG = "_exp0b3699_ic"  # stub package: only curve.py and factor_base.py are executed


def _load_engine_modules():
    """Load curve.py and factor_base.py by path under a stub package, so that the package
    __init__.py (which imports the solver, tails, rho and decompose modules) never runs."""
    pkg = types.ModuleType(_PKG)
    pkg.__path__ = [ENGINE_DIR]
    sys.modules[_PKG] = pkg
    mods = {}
    for name in ("curve", "factor_base"):
        spec = importlib.util.spec_from_file_location(f"{_PKG}.{name}",
                                                      os.path.join(ENGINE_DIR, f"{name}.py"))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[f"{_PKG}.{name}"] = mod
        spec.loader.exec_module(mod)
        mods[name] = mod
    return mods


_M = _load_engine_modules()
generate_prime_order_curve = _M["curve"].generate_prime_order_curve
FactorBase = _M["factor_base"].FactorBase
default_fb_size = _M["factor_base"].default_fb_size
subgroup_prime_filter = _M["factor_base"].subgroup_prime_filter

HEIGHT_BOUND = 1 << 12
HEIGHT_MULTIPLIERS = range(1, 17)


def _square_nonzero(rhs: int, p: int) -> bool:
    return rhs != 0 and pow(rhs, (p - 1) // 2, p) == 1


def offset_walk(p: int, a: int, b: int, size: int, seed: int) -> tuple[int, list[int]]:
    """x0 and the first `size` x >= x0 with x^3 + a x + b a nonzero square mod p."""
    x0 = p // 4 + random.Random(f"fb-smallx-offset|{p}|{a}|{b}|{size}|{seed}").randrange(p // 2)
    xs, x = [], x0
    while len(xs) < size:
        if x >= p:
            raise ValueError(f"offset walk reached p (x0 = {x0})")
        if _square_nonzero((x * x * x + a * x + b) % p, p):
            xs.append(x)
        x += 1
    return x0, xs


def height_hits(xs: list[int], p: int) -> list[list[int]]:
    hits = []
    for x in xs:
        for v in HEIGHT_MULTIPLIERS:
            r = x * v % p
            if r <= HEIGHT_BOUND or r >= p - HEIGHT_BOUND:
                hits.append([x, v])
    return hits


def design_curve(task: tuple[int, int]) -> dict:
    bits, c = task
    pf = subgroup_prime_filter([3, 4, 5], 0.15)
    E, P = generate_prime_order_curve(bits, c, p_filter=pf)
    p, a, b, N = E.p, E.a, E.b, E.order
    size0 = default_fb_size(N, 4)
    F_sub = FactorBase.subgroup(E, size0, c)
    s_sub = max(4, len(F_sub))
    T = s_sub * s_sub
    mu = T * (T - 1) / (3 * N)
    x0, xs = offset_walk(p, a, b, s_sub, c + 9000)
    rec = {"bits": bits, "curve": c, "p": p, "a": a, "b": b, "N": N,
           "P": [int(P[0]), int(P[1])], "p_filter": pf.label,
           "size0": size0, "F_sub": len(F_sub), "s_sub": s_sub, "subgroup_d": F_sub.params["d"],
           "mu_model": mu, "mu_model_rule": "T (T - 1) / (3 N), T = s_sub^2",
           "x0": x0, "offset_bound": xs[-1] + 1, "offset_span": xs[-1] + 1 - x0,
           "height_screen_hits": height_hits(xs, p)}
    try:
        pl = FactorBase.planted(E, s_sub, seed=c + 8000)
        tts = [r for r in pl.params["planted_relations"] if r["class"] == "TT"]
        rec["planted"] = {"ok": True, "n_tt": pl.params["n_tt"], "n_tt_planted": len(tts),
                          "size": len(pl), "error": None}
    except ValueError as exc:
        rec["planted"] = {"ok": False, "n_tt": None, "n_tt_planted": 0, "size": None,
                          "error": f"ValueError: {exc}"}
    return rec


def write_gz_jsonl(path: str, recs) -> str:
    buf = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=buf, mtime=0) as gz:
        for r in recs:
            gz.write((json.dumps(r, sort_keys=True) + "\n").encode())
    data = buf.getvalue()
    if os.path.exists(path):
        raise SystemExit(f"refusing: {path} exists (records are immutable)")
    with open(path, "wb") as fh:
        fh.write(data)
    return hashlib.sha256(data).hexdigest()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bits", type=int, nargs="+", required=True)
    ap.add_argument("--c0", type=int, required=True)
    ap.add_argument("--n-per-rung", type=int, required=True)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    tasks = [(b, c) for b in a.bits for c in range(a.c0, a.c0 + a.n_per_rung)]
    if a.workers <= 1:
        recs = [design_curve(t) for t in tasks]
    else:
        with ProcessPoolExecutor(max_workers=a.workers) as pool:
            recs = list(pool.map(design_curve, tasks, chunksize=16))
    recs.sort(key=lambda r: (r["bits"], r["curve"]))
    digest = write_gz_jsonl(a.out, recs)
    loaded = sorted(m for m in sys.modules if m.startswith("crypto_autoresearcher") or
                    m.startswith(_PKG))
    summary = {"what": "design_a.py curves", "curves": len(recs), "bits": a.bits, "c0": a.c0,
               "n_per_rung": a.n_per_rung, "out": a.out, "sha256": digest,
               "engine_modules_loaded": loaded,
               "planted_errors": sum(1 for r in recs if not r["planted"]["ok"]),
               "height_screen_curves": sum(1 for r in recs if r["height_screen_hits"])}
    print(json.dumps(summary))
    return 0


if __name__ == "__main__":
    sys.exit(main())
