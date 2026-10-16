"""Combined route: GLV on a cheaper-model isogenous neighbour, against GLV on E.

``isomodel`` prices a model change along a rational isogeny; ``curvesweep``
prices the cheapest chain endomorphism (2-GLV) on a small-|D_K| curve with the
curve's own arithmetic.  On a curve that has both, the question is whether the
two compose: run the 2-GLV on a neighbour E' that admits an ``a = -3`` model
and still carries the cheap chain, i.e. ``End(E')`` contains the element the
chain realises (a horizontal edge keeps the order; a vertical one need not).

Per curve, three arms in one cost model (curvesweep's, M_eq = M + S):

* ``glv_on_E``      -- ``curvesweep.sweep_curve`` on E, re-run here;
* ``model_change``  -- the best neighbour model, no GLV (``isomodel``);
* ``combined``      -- ``sweep_curve`` on the neighbour, plus the conversion
  (forward chain, dual chain, scalar adjustment) and the input-format term
  for the one-shot column.

The input-format term (CORR-20261016-ac9fc8): ``sweep_curve`` prices the
chain's first step with an affine input, but in the route the GLV receives
the forward map's Jacobian image.  The cheaper of two evaluations is charged:
(a) the chain on the Jacobian input (its first step at the Jacobian rate), or
(b) the chain on E's affine P, then one more forward pass on that Jacobian
image -- valid because the edge is horizontal (the chain builds on both ends),
so the isogeny commutes with the CM action.

Candidates for ``combined`` are the neighbours within ``--ells``/``--depth``
whose short-Weierstrass class is cheaper than E's, tried in order of increasing
conversion cost; the first one on which the cheapest chain element builds and
verifies (curvesweep's GLV-2 check on points) is priced, and every attempt is
recorded.  The route E -> E' -> E is verified on points with
``isomodel.verify_route``.  Modelled operation counts only.

    python -m harness.endosweep.isoglv --rows RUN/raw-result.json --out-dir DIR
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import sys
import time

from . import curvesweep as CW
from . import isomodel as IM
from . import quadorder as QO
from .targets import Target, verify
from .toyverify import Curve


def _target(name: str, p: int, a: int, b: int, n: int, h: int) -> Target:
    T = Target(name, p, "weierstrass", {"a": a, "b": b}, n, h, family="isoglv")
    return verify(T)


def _glv(T: Target, D: int, build_limit: int, build_seconds: float) -> dict:
    t0 = time.time()
    try:
        r = CW.sweep_curve(T, D, source="isoglv", build=True, build_limit=build_limit,
                           build_seconds=build_seconds)
    except Exception as exc:  # recorded, never dropped
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}", "seconds": round(time.time() - t0, 1)}
    mo = r.model_ops or {}
    out = {"ok": bool(r.best_verified and mo), "kind": r.kind, "arithmetic": r.arithmetic,
           "best_element": r.best_element, "best_order": r.best_order, "chain_M_eq": r.best_chain_M_eq,
           "built": r.built, "verified": r.verified, "note": r.note, "seconds": round(time.time() - t0, 1)}
    if mo:
        out.update(glv_M_eq=mo["glv"][mo["best_glv"]], glv_schedule=mo["best_glv"],
                   baseline_M_eq=mo["baseline"][mo["best_baseline"]], ratio=mo["ratio"],
                   coeff_bits_babai=mo["coeff_bits_babai"])
        rows = [x for x in r.rows if x.get("found")]
        if rows:
            out["glv_check"] = rows[0].get("glv_check")
    return out


def input_format_cost(order, path) -> dict:
    """M_eq the GLV's chain endomorphism costs beyond its affine-input price when its input is Jacobian."""
    order, path = list(order or []), list(path or [])
    if not order:                                        # a unit endomorphism: no first-step shortcut
        return {"M_eq": 0, "route": "unit"}
    first = order[0]
    jac = sum(CW.step_ops(first, IM.VARIANT, False)) - sum(CW.step_ops(first, IM.VARIANT, True))
    via_e = sum(sum(CW.step_ops(ell, IM.VARIANT, False)) for ell in path) + sum(IM.CS.tail_ops(IM.VARIANT))
    if jac <= via_e:
        return {"M_eq": jac, "route": "chain on the Jacobian input", "alternative_M_eq": via_e}
    return {"M_eq": via_e, "route": "chain on E's affine P, then one more forward pass", "alternative_M_eq": jac}


def screen(row: dict, *, ells: list[int], depth: int, max_nodes: int, disc_bound: int,
           build_limit: int, build_seconds: float, max_candidates: int, verify_scalars: int, seed: int) -> dict:
    t0 = time.time()
    p, a, b, n, h = (int(row["p"], 16), int(row["a"], 16), int(row["b"], 16), int(row["n"], 16), row["cofactor"])
    T = _target(row["name"], p, a, b, n, h)
    E = Curve(p, a, b)
    trace = T.trace
    scan = QO.small_discriminant_scan(trace * trace - 4 * p, disc_bound)
    out = {"name": row["name"], "bits": p.bit_length(), "D_K": scan.found, "f_pi": scan.conductor,
           "model_change": row["best"], "E_model_baseline": row["baseline"]}
    if scan.found is None:
        out["note"] = f"|D_K| > {disc_bound}: no chain endomorphism to price; the model-change arm stands alone"
        out["seconds"] = round(time.time() - t0, 1)
        return out
    D = scan.found
    out["glv_on_E"] = _glv(T, D, build_limit, build_seconds)
    eclass = sum(CW.arithmetic(p, a).dbl)
    nodes = IM.bfs(E, trace, n, ells, depth, max_nodes)
    cands = []
    for nd in nodes[1:]:
        ar = CW.arithmetic(p, nd.a)
        if sum(ar.dbl) >= eclass:
            continue
        path = [e.ell for e in nd.path]
        cands.append((IM.conversion_cost(path, "weierstrass", ar.note), nd, ar.note))
    cands.sort(key=lambda c: (c[0], [e.ell for e in c[1].path]))
    out["candidates_cheaper_class"] = len(cands)
    attempts, combined = [], None
    for conv, nd, note in cands[:max_candidates]:
        TN = _target(f"{row['name']} via {'·'.join(str(e.ell) for e in nd.path)}", p, nd.a, nd.b, n, h)
        g = _glv(TN, D, build_limit, build_seconds)
        att = {"path": [e.ell for e in nd.path], "j": hex(nd.j), "a": hex(nd.a), "b": hex(nd.b),
               "arithmetic": note, "conversion_M_eq": round(conv, 1), "glv": g}
        attempts.append(att)
        if g.get("ok"):
            att["input_format"] = input_format_cost(g.get("best_order"), att["path"])
            model = IM.Model("weierstrass", CW.arithmetic(p, nd.a), note)
            att["route_verification"] = IM.verify_route(E, trace, n, h, nd, model, verify_scalars, seed)
            combined = att
            break
    out["attempts"] = attempts
    out["combined"] = combined
    ge = out["glv_on_E"]
    if ge.get("ok") and combined:
        gn = combined["glv"]["glv_M_eq"]
        out["combined_vs_glv_on_E"] = {
            "persistent_gain": round(1 - gn / ge["glv_M_eq"], 5),
            "oneshot_gain": round(1 - (gn + combined["conversion_M_eq"] + combined["input_format"]["M_eq"])
                                  / ge["glv_M_eq"], 5)}
    if combined:
        gn = combined["glv"]["glv_M_eq"]
        base = row["baseline"]["M_eq"]
        out["combined_vs_E_model_baseline"] = {
            "persistent_gain": round(1 - gn / base, 5),
            "oneshot_gain": round(1 - (gn + combined["conversion_M_eq"] + combined["input_format"]["M_eq"])
                                  / base, 5)}
    if ge.get("ok") and row.get("best"):
        mc = row["best"]
        out["model_change_vs_glv_on_E"] = {
            "persistent_gain": round(1 - mc["M_eq"] / ge["glv_M_eq"], 5),
            "oneshot_gain": round(1 - mc["oneshot_M_eq"] / ge["glv_M_eq"], 5)}
    out["seconds"] = round(time.time() - t0, 1)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--rows", required=True, help="RUN-ENDO-d7cb69 raw-result.json")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--ells", default="2,3,5,7,11,13")
    ap.add_argument("--depth", type=int, default=2)
    ap.add_argument("--max-nodes", type=int, default=64)
    ap.add_argument("--disc-bound", type=int, default=2_000_000)
    ap.add_argument("--build-limit", type=int, default=3)
    ap.add_argument("--build-seconds", type=float, default=900.0)
    ap.add_argument("--max-candidates", type=int, default=12)
    ap.add_argument("--verify-scalars", type=int, default=8)
    ap.add_argument("--seed", type=int, default=20261016)
    ap.add_argument("--only", default=None)
    ap.add_argument("--include", default="", help="comma-separated row names added to the selection (controls)")
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    src = json.load(open(args.rows))["rows"]
    inc = [x for x in args.include.split(",") if x]
    sel = [r for r in src if r.get("name") in inc] + [
        r for r in src if r.get("role") == "population" and r.get("best") and r["best"]["persistent_gain"] > 0
        and r.get("name") not in inc]
    if args.only:
        sel = [r for r in sel if r["name"] in inc or any(k in r["name"] for k in args.only.split(","))]

    def git(*c):
        try:
            return subprocess.check_output(["git", *c], text=True).strip()
        except Exception:
            return None
    prov = {"command": " ".join(sys.argv), "commit": git("rev-parse", "HEAD"),
            "dirty": bool(git("status", "--porcelain", "--", "harness")), "python": sys.version,
            "platform": platform.platform(), "flint": __import__("flint").__version__, "args": vars(args),
            "source_rows": args.rows, "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    ells = [int(x) for x in args.ells.split(",")]
    results = []
    with open(os.path.join(args.out_dir, "rows.jsonl"), "w") as jl:
        for r in sel:
            try:
                res = screen(r, ells=ells, depth=args.depth, max_nodes=args.max_nodes, disc_bound=args.disc_bound,
                             build_limit=args.build_limit, build_seconds=args.build_seconds,
                             max_candidates=args.max_candidates, verify_scalars=args.verify_scalars, seed=args.seed)
            except Exception as exc:
                res = {"name": r["name"], "error": f"{type(exc).__name__}: {exc}"}
            results.append(res)
            jl.write(json.dumps(res) + "\n")
            jl.flush()
            c = res.get("combined_vs_glv_on_E")
            print(f"{res['name']:<28} D_K={res.get('D_K')} E-GLV={res.get('glv_on_E', {}).get('glv_M_eq')} "
                  f"combined={None if not res.get('combined') else res['combined']['glv'].get('glv_M_eq')} "
                  f"vsGLV={c} {res.get('error', '')}", flush=True)
    prov["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    json.dump({"provenance": prov, "rows": results}, open(os.path.join(args.out_dir, "isoglv.json"), "w"), indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
