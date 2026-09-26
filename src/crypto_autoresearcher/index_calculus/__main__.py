"""Command line: ``python -m crypto_autoresearcher.index_calculus``.

    solve    one instance end to end, JSON out
    sweep    index calculus vs Pollard rho over field sizes: one JSONL row per
             instance and method, fitted cost exponents in N with bootstrap CIs;
             --engine enumerate mitm runs both decomposition engines
    engines  per-target decomposition cost of msolve (Groebner) vs exhaustive
             enumeration on a ladder of factor-base sizes, with the check that
             both engines find exactly the same decompositions
    analyze  refit and tabulate from sweep / engines JSONL files

Costs are counts, reported in columns that are never summed: S_3 root solves
for index calculus, group additions of the walk for rho (its fixed setup is a
separate column).  Exponents are least-squares slopes of log2(cost) against
log2(N) (sweep) or log2(|F|) (engines); the interval is a stratified
percentile bootstrap over instances.
"""

from __future__ import annotations

import argparse
import gzip
import json
import math
import random
import statistics
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

from .curve import generate_prime_order_curve
from .decompose import DecompStats, decompose_all
from .factor_base import (FACTOR_BASES, FactorBase, build_factor_base,
                          default_fb_size, subgroup_prime_filter)
from .rho import pollard_rho
from .solver import ENGINES, solve_index_calculus
from .stats import bootstrap_slope, fit_exponent


# -- instances ------------------------------------------------------------------

def _instance(bits: int, curve_seed: int, target_seed: int = 0, p_filter=None):
    E, P = generate_prime_order_curve(bits, curve_seed, p_filter=p_filter)
    k = random.Random(f"target|{bits}|{curve_seed}|{target_seed}").randrange(1, E.order)
    Q = E.mul(k, P)
    E.ops.group_ops = 0
    return E, P, Q, k


def _curve_fields(E, bits: int, c: int, label: str) -> dict:
    return {"bits": bits, "curve": c, "p": E.p, "a": E.a, "b": E.b, "N": E.order,
            "log2N": math.log2(E.order), "p_filter": label}


# -- solve ------------------------------------------------------------------------

def cmd_solve(args: argparse.Namespace) -> int:
    pf = subgroup_prime_filter([args.m], args.tolerance) if args.subgroup_prime else None
    E, P, Q, k = _instance(args.bits, args.curve_seed, args.target_seed, pf)
    out = {"curve": {"p": E.p, "a": E.a, "b": E.b, "order": E.order}, "P": P, "Q": Q}
    ic = solve_index_calculus(E, P, Q, m=args.m, fb_kind=args.fb, fb_size=args.fb_size,
                              seed=args.seed, engine=args.engine,
                              accelerate=False if args.no_accel else None,
                              table_arity=args.table_arity)
    out["index_calculus"] = ic.to_dict() | {"correct": ic.k == k}
    if args.rho:
        rr = pollard_rho(E, P, Q, seed=args.seed)
        out["rho"] = {"k": rr.k, "verified": rr.verified, "walk_ops": rr.walk_ops,
                      "setup_ops": rr.setup_ops, "group_ops": rr.group_ops,
                      "walks": rr.walks, "seconds": rr.seconds}
    json.dump(out, sys.stdout, indent=2, default=list)
    print()
    return 0 if ic.verified else 1


# -- sweep ------------------------------------------------------------------------

def _sweep_job(job: dict) -> list[dict]:
    bits, c = job["bits"], job["curve"]
    pf = subgroup_prime_filter(job["ms"], job["tolerance"]) if job["subgroup"] else None
    label = pf.label if pf else "none"
    E, P, Q, k = _instance(bits, c, 0, pf)
    base = _curve_fields(E, bits, c, label)
    rows = []
    if job["rho"]:
        rr = pollard_rho(E, P, Q, seed=c)
        rows.append(base | {"method": "rho", "fb": "-", "ok": rr.verified and rr.k == k,
                            "walk_ops": rr.walk_ops, "setup_ops": rr.setup_ops,
                            "group_ops": rr.group_ops, "walks": rr.walks,
                            "dp_bits": rr.dp_bits, "seconds": rr.seconds})
    for m in job["ic_ms"]:
        fbs = {}
        size = default_fb_size(E.order, m)
        if "subgroup" in job["fbs"]:
            fbs["subgroup"] = FactorBase.subgroup(E, size, c)
            size = len(fbs["subgroup"])  # every base in the cell gets this size
        size = max(4, size)
        for kind in job["fbs"]:
            fb = fbs[kind] if kind in fbs else build_factor_base(E, kind, size, c)
            for engine in job.get("engines", ["enumerate"]):
                if bits > job.get("engine_caps", {}).get(f"{engine}:{m}", 10**9):
                    continue
                E.ops.group_ops = 0
                ic = solve_index_calculus(E, P, Q, m=m, fb_kind=kind, seed=c,
                                          factor_base=fb, accelerate=job["accelerate"],
                                          engine=engine)
                rows.append(base | {
                    "method": f"ic_m{m}", "fb": kind, "engine": engine, "fb_size": len(fb),
                    "fb_params": {kk: v for kk, v in fb.params.items() if kk != "seed"},
                    "ok": ic.verified and ic.k == k, "s3_solves": ic.s3_solves,
                    "table_arity": ic.table_arity, "table_s3_solves": ic.table_s3_solves,
                    "table_entries": ic.table_entries,
                    "membership_tests": ic.membership_tests, "group_ops": ic.group_ops,
                    "target_ops": ic.target_ops, "decomp_ops": ic.group_ops - ic.target_ops,
                    "la_ops": ic.la_ops, "relations": ic.relations, "attempts": ic.attempts,
                    "rank": ic.rank, "accelerated": ic.accelerated,
                    "seconds": ic.seconds_total})
    return rows


def _parse_caps(items: list[str]) -> tuple[dict[int, int], dict[str, int]]:
    """``M=BITS`` caps an arity for every engine, ``ENGINE:M=BITS`` for one engine."""
    caps, engine_caps = {}, {}
    for it in items:
        m, _, b = it.partition("=")
        if ":" in m:
            engine, _, mm = m.partition(":")
            engine_caps[f"{engine}:{int(mm)}"] = int(b)
        else:
            caps[int(m)] = int(b)
    return caps, engine_caps


def cmd_sweep(args: argparse.Namespace) -> int:
    caps, engine_caps = _parse_caps(args.m_max_bits)
    subgroup = "subgroup" in args.fb
    jobs = []
    for bits in args.bits:
        for c in range(max(args.curves, args.rho_curves)):
            ic_ms = [m for m in args.m if c < args.curves and bits <= caps.get(m, 10**9)]
            jobs.append({"bits": bits, "curve": c, "ms": args.m, "ic_ms": ic_ms,
                         "fbs": args.fb, "rho": c < args.rho_curves, "subgroup": subgroup,
                         "tolerance": args.tolerance, "engines": args.engine,
                         "engine_caps": engine_caps,
                         "accelerate": False if args.no_accel else None})
    jobs.sort(key=lambda j: (-j["bits"] * (1 + len(j["ic_ms"])), j["curve"]))
    rows = _run_jobs(_sweep_job, jobs, args.workers, args.out, args.quiet)
    rows.sort(key=lambda r: (r["bits"], r["curve"], r["method"], r["fb"],
                             r.get("engine", "")))
    report = sweep_report(rows, args.reps)
    if args.json:
        json.dump({"rows": rows, **report}, sys.stdout, indent=2)
        print()
    else:
        print(format_sweep_report(report))
    return 0 if all(r["ok"] for r in rows) else 1


def _run_jobs(fn, jobs: list[dict], workers: int, out: str | None, quiet: bool) -> list[dict]:
    rows: list[dict] = []
    sink = open(out, "a") if out else None
    t0 = time.perf_counter()

    def emit(new: list[dict]) -> None:
        rows.extend(new)
        for r in new:
            if sink:
                sink.write(json.dumps(r) + "\n")
                sink.flush()
            if not quiet:
                print(_progress_line(r, time.perf_counter() - t0), file=sys.stderr)

    try:
        if workers <= 1:
            for job in jobs:
                emit(fn(job))
        else:
            with ProcessPoolExecutor(max_workers=workers) as pool:
                futures = [pool.submit(fn, job) for job in jobs]
                for fut in as_completed(futures):
                    emit(fut.result())
    finally:
        if sink:
            sink.close()
    return rows


def _progress_line(r: dict, elapsed: float) -> str:
    if "method" in r:
        cost = r.get("walk_ops") if r["method"] == "rho" else r.get("s3_solves")
        return (f"[{elapsed:7.0f}s] {r['bits']:>3}b c{r['curve']:<2} {r['method']:<6} "
                f"{r['fb']:<8} {r.get('engine', '-'):<9} "
                f"|F|={r.get('fb_size', '-')!s:<6} ok={r['ok']!s:<5} "
                f"cost={cost:<11} t={r['seconds']:.2f}s")
    return (f"[{elapsed:7.0f}s] m={r['m']} {r['fb']:<8} |F|={r['fb_size']:<4} "
            f"target {r['target']:<3} agree={r['agree']!s:<5} "
            f"enum={r['enum_s3']:<8} msolve={r['msolve_status']}:{r['msolve_seconds']:.3f}s")


def _series(r: dict) -> tuple[str, str, str]:
    """(method, base, engine) of a row; rows from before engines were recorded
    are exhaustive enumeration."""
    return r["method"], r["fb"], r.get("engine", "enumerate" if r["method"] != "rho" else "-")


def _series_name(method: str, fb: str, engine: str) -> str:
    if method == "rho":
        return method
    return f"{method}:{fb}" if engine == "enumerate" else f"{method}:{fb}:{engine}"


def sweep_report(rows: list[dict], reps: int = 2000) -> dict:
    fits, table = {}, {}
    keys = sorted({_series(r) for r in rows})
    for method, fb, engine in keys:
        sel = [r for r in rows if _series(r) == (method, fb, engine) and r["ok"]]
        name = _series_name(method, fb, engine)
        if method == "rho":
            fits[name] = {"walk_ops": fit_exponent(sel, "walk_ops", reps=reps),
                          "group_ops": fit_exponent(sel, "group_ops", reps=reps)}
        else:
            fits[name] = {"s3_solves": fit_exponent(sel, "s3_solves", reps=reps),
                          "la_ops": fit_exponent(sel, "la_ops", reps=reps),
                          "seconds": fit_exponent(sel, "seconds", reps=reps)}
        for bits in sorted({r["bits"] for r in sel}):
            cell = [r for r in sel if r["bits"] == bits]
            primary = "walk_ops" if method == "rho" else "s3_solves"
            table.setdefault(bits, {})[name] = {
                "n": len(cell), "median": statistics.median(r[primary] for r in cell),
                "median_seconds": statistics.median(r["seconds"] for r in cell),
                "fb_size": statistics.median(r.get("fb_size", 0) for r in cell)}
    failed = [r for r in rows if not r["ok"]]
    return {"fits": fits, "table": {str(b): v for b, v in sorted(table.items())},
            "failed": len(failed), "instances": len(rows)}


def _fmt_fit(f: dict) -> str:
    if f["slope"] is None:
        return "n/a"
    ci = f" [{f['lo']:.3f}, {f['hi']:.3f}]" if f["lo"] is not None else ""
    return f"{f['slope']:.3f}{ci} (n={f['n']})"


def format_sweep_report(rep: dict) -> str:
    lines = ["fitted exponents: slope of log2(cost) vs log2(N), 95% bootstrap CI"]
    for name, f in rep["fits"].items():
        for metric, fit in f.items():
            lines.append(f"  {name:<20} {metric:<10} {_fmt_fit(fit)}")
    names = sorted({n for cells in rep["table"].values() for n in cells})
    lines.append("")
    lines.append("median cost per instance (rho: walk group ops; ic: S_3 solves)")
    lines.append("  bits " + " ".join(f"{n:>20}" for n in names))
    for bits, cells in rep["table"].items():
        vals = [f"{cells[n]['median']:>20.0f}" if n in cells else " " * 20 for n in names]
        lines.append(f"  {bits:>4} " + " ".join(vals))
    lines.append(f"instances: {rep['instances']}, failed: {rep['failed']}")
    return "\n".join(lines)


# -- engines ----------------------------------------------------------------------

def _targets(E, fb: FactorBase, m: int, count: int, planted: float, seed: int):
    """Targets off the factor base; a fraction built as sums of m base points."""
    rng = random.Random(f"engines-targets|{E.p}|{fb.kind}|{len(fb)}|{m}|{seed}")
    xs = {Q[0] for Q in fb.points}
    out = []
    while len(out) < count:
        plant = len(out) < round(planted * count)
        if plant:
            R = None
            for _ in range(m):
                F = rng.choice(fb.points)
                R = E.add(R, F if rng.random() < 0.5 else E.neg(F))
        else:
            R = E.random_point(rng)
        if R is not None and R[0] not in xs:
            out.append((R, plant))
    return out


_CACHE: dict = {}


def _engines_curve(bits: int, curve_seed: int, spec: dict | None):
    """The engines curve, built once per process (the filtered prime search is slow)."""
    key = ("curve", bits, curve_seed, json.dumps(spec, sort_keys=True))
    if key not in _CACHE:
        pf = subgroup_prime_filter([], **spec) if spec else None
        _CACHE[key] = (_instance(bits, curve_seed, 0, pf), pf.label if pf else "none")
    return _CACHE[key]


def _engines_task(task: dict) -> dict:
    from .msolve import decompose_msolve, startup_seconds

    (E, _, _, _), _ = _engines_curve(task["bits"], task["curve_seed"], task["pf_spec"])
    fb_key = ("fb", E.p, task["kind"], task["size"])
    if fb_key not in _CACHE:
        _CACHE[fb_key] = build_factor_base(E, task["kind"], task["size"], 0)
    fb = _CACHE[fb_key]
    R, m = tuple(task["R"]), task["m"]
    stats = DecompStats()
    t0 = time.perf_counter()
    enum = decompose_all(E, fb, R, m, stats)
    enum_seconds = time.perf_counter() - t0
    out = decompose_msolve(E, fb, R, m, seed=task["target"], timeout=task["timeout"])
    ok = out.status in ("ok", "no_solution")
    member = fb.membership_poly()
    return {"engine_cell": True, "bits": task["bits"], "p": E.p, "m": m,
            "fb": fb.kind, "fb_size": len(fb), "fb_params": {
                kk: v for kk, v in fb.params.items() if kk != "seed"},
            "member_degree": max(member), "member_terms": len(member),
            "target": task["target"], "planted": task["planted"],
            "enum_s3": stats.s3_solves, "enum_seconds": enum_seconds,
            "enum_decomps": len(enum),
            "msolve_status": out.status, "msolve_seconds": out.seconds,
            "msolve_net_seconds": max(out.seconds - startup_seconds(), 1e-4),
            "msolve_runs": out.runs, "msolve_degree": out.degree,
            "msolve_decomps": len(out.relations), "msolve_unlifted": out.unlifted,
            "agree": (enum == out.relations) if ok else None}


def cmd_engines(args: argparse.Namespace) -> int:
    from .msolve import available

    if not available():
        print("msolve not found: install it (apt install msolve) or set CRYPTO_AR_MSOLVE",
              file=sys.stderr)
        return 2
    spec = ({"tolerance": args.tolerance, "sizes": list(args.sizes)}
            if "subgroup" in args.fb else None)
    (E, _, _, _), label = _engines_curve(args.bits, args.curve_seed, spec)
    print(f"curve: p={E.p} a={E.a} b={E.b} N={E.order}; p-1 filter: {label}",
          file=sys.stderr)
    rows: list[dict] = []
    for m in args.m:
        for kind in args.fb:
            done_bases = set()
            for size in args.sizes:
                if args.max_size and size > args.max_size:
                    break
                target_size = size
                if "subgroup" in args.fb and kind != "subgroup":
                    target_size = len(FactorBase.subgroup(E, size, 0))  # matched size
                fb = build_factor_base(E, kind, target_size, 0)
                key = (len(fb), max(fb.membership_poly()))
                if key in done_bases:  # two rungs gave the same base
                    continue
                done_bases.add(key)
                tasks = [{"bits": args.bits, "curve_seed": args.curve_seed, "pf_spec": spec,
                          "kind": kind, "size": target_size, "m": m, "R": R,
                          "planted": planted, "target": t, "timeout": args.timeout}
                         for t, (R, planted) in enumerate(
                             _targets(E, fb, m, args.targets, args.planted, args.seed))]
                cell = _run_jobs(_engines_one, tasks, args.workers, args.out, args.quiet)
                cell.sort(key=lambda r: r["target"])
                rows.extend(cell)
                done = [r for r in cell if r["msolve_status"] in ("ok", "no_solution")]
                slow = (not done or statistics.median(r["msolve_seconds"] for r in done)
                        > args.max_seconds or len(done) < len(cell) / 2)
                if slow:
                    print(f"m={m} {kind}: stopping the ladder after |F|={len(fb)} "
                          f"(median msolve time over {args.max_seconds}s or failures)",
                          file=sys.stderr)
                    break
    report = engines_report(rows, args.reps, args.min_seconds)
    if args.json:
        json.dump({"rows": rows, **report}, sys.stdout, indent=2)
        print()
    else:
        print(format_engines_report(report))
    disagreements = sum(1 for r in rows if r["agree"] is False)
    return 1 if disagreements else 0


def _engines_one(task: dict) -> list[dict]:
    return [_engines_task(task)]


def engines_report(rows: list[dict], reps: int = 2000, min_seconds: float = 0.05) -> dict:
    """Per-(m, base) exponent fits and per-cell medians.

    The msolve fit uses only cells whose median msolve time is at least
    ``min_seconds`` (below that the ~4 ms process start-up dominates and the
    net time is noise) and in which at least half the targets finished: a
    cell where most runs hit the timeout keeps only its fastest targets, so
    its median would be biased low.  Such a cell is still tabulated, as a
    lower bound.  Rungs of the size ladder that produced the same base (and
    hence the same targets) are counted once.
    """
    seen, uniq = set(), []
    for r in rows:
        key = (r["m"], r["fb"], r["fb_size"], r["member_degree"], r["target"])
        if key not in seen:
            seen.add(key)
            uniq.append(r)
    rows = uniq
    fits, cells = {}, []
    for m, kind in sorted({(r["m"], r["fb"]) for r in rows}):
        sel = [r for r in rows if (r["m"], r["fb"]) == (m, kind)]
        ok = [r for r in sel if r["msolve_status"] in ("ok", "no_solution")]

        def cell_of(r):
            return r["fb_size"], r["member_degree"]

        fit_cells = set()
        for key in {cell_of(r) for r in ok}:
            done = [r["msolve_seconds"] for r in ok if cell_of(r) == key]
            total = sum(1 for r in sel if cell_of(r) == key)
            if statistics.median(done) >= min_seconds and 2 * len(done) >= total:
                fit_cells.add(key)
        timed = [r for r in ok if cell_of(r) in fit_cells]
        name = f"m{m}:{kind}"
        fits[name] = {
            "enum_s3": _size_fit(sel, "enum_s3", reps),
            "enum_seconds": _size_fit(sel, "enum_seconds", reps),
            "msolve_seconds": _size_fit(timed, "msolve_net_seconds", reps),
            # the same msolve times against the degree of the membership
            # polynomial (|F| for the dense bases, d ~ 2|F| for subgroup)
            "msolve_vs_degree": _size_fit(timed, "msolve_net_seconds", reps,
                                          x_key="member_degree")}
        for size, degree in sorted({(r["fb_size"], r["member_degree"]) for r in sel}):
            c = [r for r in sel if (r["fb_size"], r["member_degree"]) == (size, degree)]
            cok = [r for r in c if r["msolve_status"] in ("ok", "no_solution")]
            cells.append({
                "name": name, "fb_size": size, "targets": len(c),
                "member_degree": c[0]["member_degree"], "member_terms": c[0]["member_terms"],
                "enum_s3": statistics.median(r["enum_s3"] for r in c),
                "enum_seconds": statistics.median(r["enum_seconds"] for r in c),
                "msolve_seconds": (statistics.median(r["msolve_seconds"] for r in cok)
                                   if cok else None),
                "msolve_ok": len(cok), "decomps": sum(r["enum_decomps"] for r in c),
                "agree": sum(1 for r in c if r["agree"]),
                "disagree": sum(1 for r in c if r["agree"] is False)})
    return {"fits": fits, "cells": cells,
            "disagreements": sum(1 for r in rows if r["agree"] is False),
            "targets": len(rows)}


def _size_fit(rows: list[dict], key: str, reps: int, x_key: str = "fb_size") -> dict:
    sel = [r for r in rows if r.get(key) and r[key] > 0]
    xs = [math.log2(r[x_key]) for r in sel]
    ys = [math.log2(r[key]) for r in sel]
    return bootstrap_slope(xs, ys, [(r["fb_size"], r["member_degree"]) for r in sel],
                           reps=reps)


def format_engines_report(rep: dict) -> str:
    lines = ["per-target cost exponents in |F| (slope of log2 cost vs log2 |F|, 95% CI;"
             " msolve_vs_degree: vs log2 deg f)"]
    for name, f in rep["fits"].items():
        for metric, fit in f.items():
            lines.append(f"  {name:<14} {metric:<15} {_fmt_fit(fit)}")
    lines.append("")
    lines.append("  cell            |F|  deg(f) terms  enum S3  enum s     msolve s  "
                 "ok/T   decomps agree/disagree")
    for c in rep["cells"]:
        ms = f"{c['msolve_seconds']:.4f}" if c["msolve_seconds"] is not None else "-"
        lines.append(f"  {c['name']:<14} {c['fb_size']:>4} {c['member_degree']:>7} "
                     f"{c['member_terms']:>5} {c['enum_s3']:>8.0f} {c['enum_seconds']:>7.4f} "
                     f"{ms:>12} {c['msolve_ok']:>3}/{c['targets']:<3} {c['decomps']:>7} "
                     f"{c['agree']:>5}/{c['disagree']}")
    lines.append(f"targets: {rep['targets']}, engine disagreements: {rep['disagreements']}")
    return "\n".join(lines)


# -- analyze ----------------------------------------------------------------------

def cmd_analyze(args: argparse.Namespace) -> int:
    rows = []
    for path in args.files:
        opener = gzip.open if path.endswith(".gz") else open
        with opener(path, "rt") as fh:
            rows.extend(json.loads(line) for line in fh if line.strip())
    sweep_rows = [r for r in rows if "method" in r]
    engine_rows = [r for r in rows if r.get("engine_cell")]
    out = {}
    if sweep_rows:
        out["sweep"] = sweep_report(sweep_rows, args.reps)
    if engine_rows:
        out["engines"] = engines_report(engine_rows, args.reps, args.min_seconds)
    if args.json:
        json.dump(out, sys.stdout, indent=2)
        print()
    else:
        if "sweep" in out:
            print(format_sweep_report(out["sweep"]))
        if "engines" in out:
            print(format_engines_report(out["engines"]))
    return 0


# -- entry point ------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m crypto_autoresearcher.index_calculus",
                                 description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("solve", help="solve one instance")
    s.add_argument("--bits", type=int, default=16)
    s.add_argument("--m", type=int, default=2)
    s.add_argument("--fb", choices=FACTOR_BASES, default="small_x")
    s.add_argument("--fb-size", type=int, default=None)
    s.add_argument("--engine", choices=ENGINES, default="enumerate")
    s.add_argument("--curve-seed", type=int, default=0)
    s.add_argument("--target-seed", type=int, default=0)
    s.add_argument("--seed", type=int, default=0)
    s.add_argument("--subgroup-prime", action="store_true",
                   help="choose p so that p-1 hosts a subgroup base of the default size")
    s.add_argument("--tolerance", type=float, default=0.15)
    s.add_argument("--table-arity", type=int, default=None,
                   help="mitm engine: points per precomputed tail (default (m+1)//2)")
    s.add_argument("--no-accel", action="store_true", help="disable the numpy scan")
    s.add_argument("--rho", action="store_true", help="also run Pollard rho")
    s.set_defaults(func=cmd_solve)

    w = sub.add_parser("sweep", help="IC vs rho across field sizes")
    w.add_argument("--bits", type=int, nargs="+", default=[12, 14, 16, 18])
    w.add_argument("--m", type=int, nargs="+", default=[2])
    w.add_argument("--fb", choices=FACTOR_BASES, nargs="+", default=["small_x"])
    w.add_argument("--curves", type=int, default=3, help="curves per size for IC")
    w.add_argument("--rho-curves", type=int, default=0,
                   help="curves per size for rho (default: same as --curves)")
    w.add_argument("--engine", choices=[e for e in ENGINES if e != "msolve"], nargs="+",
                   default=["enumerate"], help="decomposition engines to run on each base")
    w.add_argument("--m-max-bits", nargs="*", default=[], metavar="[ENGINE:]M=BITS",
                   help="skip IC at arity M above BITS, e.g. 3=28, or only for one "
                        "engine, e.g. enumerate:3=24")
    w.add_argument("--tolerance", type=float, default=0.15,
                   help="subgroup fairness: |d - 2|F|| <= tol * 2|F| for some d | p-1")
    w.add_argument("--workers", type=int, default=1)
    w.add_argument("--out", help="append one JSON row per instance to this file")
    w.add_argument("--reps", type=int, default=2000, help="bootstrap replicates")
    w.add_argument("--no-accel", action="store_true")
    w.add_argument("--json", action="store_true")
    w.add_argument("--quiet", action="store_true")
    w.set_defaults(func=cmd_sweep)

    g = sub.add_parser("engines", help="msolve vs enumeration per target")
    g.add_argument("--bits", type=int, default=16,
                   help="field size; msolve is used only below 2^16 (see msolve.py)")
    g.add_argument("--curve-seed", type=int, default=0)
    g.add_argument("--m", type=int, nargs="+", default=[2, 3])
    g.add_argument("--fb", choices=FACTOR_BASES, nargs="+", default=list(FACTOR_BASES))
    g.add_argument("--sizes", type=int, nargs="+",
                   default=[4, 6, 8, 12, 16, 24, 32, 48, 64, 96, 128, 192, 256])
    g.add_argument("--max-size", type=int, default=0,
                   help="skip ladder rungs above this size (the curve, which is chosen "
                        "from the full --sizes ladder, stays the same)")
    g.add_argument("--targets", type=int, default=12, help="targets per cell")
    g.add_argument("--planted", type=float, default=0.5,
                   help="fraction of targets built as sums of m base points")
    g.add_argument("--seed", type=int, default=0)
    g.add_argument("--timeout", type=float, default=300.0, help="per msolve run")
    g.add_argument("--max-seconds", type=float, default=60.0,
                   help="stop a ladder once the median msolve time exceeds this")
    g.add_argument("--tolerance", type=float, default=0.15)
    g.add_argument("--workers", type=int, default=1)
    g.add_argument("--out")
    g.add_argument("--reps", type=int, default=2000)
    g.add_argument("--min-seconds", type=float, default=0.05,
                   help="fit msolve only on cells whose median time is at least this")
    g.add_argument("--json", action="store_true")
    g.add_argument("--quiet", action="store_true")
    g.set_defaults(func=cmd_engines)

    z = sub.add_parser("analyze", help="refit from JSONL rows")
    z.add_argument("files", nargs="+", help="sweep / engines JSONL files (.gz is fine)")
    z.add_argument("--reps", type=int, default=2000)
    z.add_argument("--min-seconds", type=float, default=0.05,
                   help="engines: fit msolve only on cells at least this slow")
    z.add_argument("--json", action="store_true")
    z.set_defaults(func=cmd_analyze)

    args = ap.parse_args(argv)
    if getattr(args, "rho_curves", None) == 0:
        args.rho_curves = args.curves
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
