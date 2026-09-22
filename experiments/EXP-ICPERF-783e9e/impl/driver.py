#!/usr/bin/env python3
"""EXP-ICPERF-783e9e: the forced-arity constraint and the decomposition budget.

Runs under `sage -python`.  Four phases, each checkpointed to
<run-dir>/checkpoint/<phase>.json so an interrupted run resumes.  Output is
bounded: aggregate counters and one row per cell, never a per-instance stream.

  1 self_test     fixed fixtures with hand-checkable answers
  2 budget_table  the charged cost model over the real binary degrees
  3 degree_law    the Weil-descended Boolean degree, MEASURED, against m(m-1)
  4 solver_ladder measured Groebner solve time vs descended variable count,
                  at each arity, SAT and random targets separately

Phase 4 cells that exceed their declared timeout are recorded as
`timed_out: true` and are NEVER counted as evidence about difficulty -- an
unfinished solve is execution status (AGENTS.md rule 3), and the exponent fit
is computed only over cells that completed.
"""
import argparse, itertools, json, hashlib, os, platform, signal, sys, time, traceback
from datetime import datetime, timezone
from math import log2, sqrt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

EXPERIMENT = "EXP-ICPERF-783e9e"
SOURCES = ("costmodel.py", "arity.py", "pdp.py", "driver.py")


def stamp():
    return datetime.now(timezone.utc).isoformat()


def jsonable(o):
    """Sage returns its own Integer/Rational/RealNumber types; JSON does not know
    them. Convert on the way out rather than casting at every call site, so a new
    measurement cannot silently reintroduce the problem."""
    try:
        if o == int(o):
            return int(o)
    except (TypeError, ValueError, OverflowError):
        pass
    try:
        return float(o)
    except (TypeError, ValueError):
        return str(o)


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


class Timeout(Exception):
    pass


def _alarm(sig, frm):
    raise Timeout()


signal.signal(signal.SIGALRM, _alarm)

# Sage installs cysignals, which intercepts SIGALRM and raises its OWN
# AlarmInterrupt instead of letting the handler above run. Catching only
# `Timeout` therefore lets a per-cell timeout escape and kill the whole phase,
# which is exactly what happened on this run's first ladder attempt. Catch both.
try:
    from cysignals.signals import AlarmInterrupt as _AlarmInterrupt
    TIMEOUTS = (Timeout, _AlarmInterrupt)
except ImportError:                                  # pragma: no cover
    TIMEOUTS = (Timeout,)


# ---------------------------------------------------------------- phase 1 ----
def phase_self_test():
    from costmodel import rho_log2, log2_factorial, index_calculus
    from arity import boolean_degree
    checks = []

    def ck(name, got, want, tol=0.0):
        ok = abs(got - want) <= tol if isinstance(got, float) else got == want
        checks.append(dict(name=name, got=got, want=want, pass_=bool(ok)))

    ck("log2(4!)", round(log2_factorial(4), 6), round(log2(24), 6), 1e-6)
    ck("log2(6!)", round(log2_factorial(6), 6), round(log2(720), 6), 1e-6)
    # rho on a 2^131 group with the sqrt(2n) subfield speedup
    ck("rho(2,131) subfield", round(rho_log2(2, 131, True), 3),
       round(65.5 + log2(sqrt(3.141592653589793 / 4)) - 0.5 * log2(262), 3), 1e-3)
    # generic rho keeps only the sqrt(2) from negation
    ck("rho(2,131) generic", round(rho_log2(2, 131, False), 3),
       round(65.5 + log2(sqrt(3.141592653589793 / 4)) - 0.5, 3), 1e-3)
    # decomposition probability caps at 1
    ck("p caps at 1", index_calculus(2, 10, 5, 8)["log2_decomposition_probability"], 0.0)
    # the degree law, asserted here and MEASURED in phase 3
    for m, d in ((2, 2), (3, 6), (4, 12), (5, 20)):
        ck(f"boolean_degree({m}, l large)", boolean_degree(m, 99), d)
    # the low-dimension cap that the measurement forced into the law
    ck("boolean_degree(4, l=2) caps at m*l", boolean_degree(4, 2), 8)
    return dict(checks=checks, all_pass=all(c["pass_"] for c in checks))


# ---------------------------------------------------------------- phase 2 ----
def phase_budget_table(q, targets, m_values):
    from arity import curve_table
    rows = curve_table(q, [tuple(t) for t in targets], m_values, use_frobenius=True)
    rows_nf = curve_table(q, [tuple(t) for t in targets], m_values, use_frobenius=False)
    dead = {}
    for m in m_values:
        dead[m] = [r["n"] for r in rows
                   if any(c["m"] == m and (not c.get("viable", True)
                                           or c.get("free_oracle_loses"))
                          for c in r["cells"])]
    return dict(with_frobenius=rows, without_frobenius=rows_nf,
                degrees_where_arity_is_dead=dead,
                minimum_viable_arity={r["n"]: r["minimum_viable_arity"] for r in rows},
                minimum_viable_arity_no_frobenius={
                    r["n"]: r["minimum_viable_arity_no_frobenius"] for r in rows})


# ---------------------------------------------------------------- phase 3 ----
def phase_degree_law(cells):
    """MEASURE the Boolean degree of the descended system; compare to m(m-1)."""
    from pdp import curve, semaev, subspace_basis, descend
    from arity import boolean_degree, anf_log2_monomials
    from math import log2 as _log2
    rows = []
    for (n, m, l) in cells:
        try:
            K, E, a6 = curve(n, seed=3)
            _, S = semaev(m, K, a6)
            basis = subspace_basis(K, n, l, seed=5)
            xR = E.random_point()[0]
            t0 = time.perf_counter()
            B, eqs = descend(S, basis, xR, m, n)
            build = time.perf_counter() - t0
            D = max(e.deg() for e in eqs)
            mons = set()
            for e in eqs:
                mons.update(e.monomials())
            dense = anf_log2_monomials(m * l, D)
            rows.append(dict(n=n, m=m, l=l, variables=m * l, equations=len(eqs),
                             measured_boolean_degree=D,
                             predicted_degree=boolean_degree(m, l),
                             distinct_anf_monomials=len(mons),
                             log2_distinct_anf_monomials=_log2(len(mons)) if mons else None,
                             log2_dense_bound=dense,
                             anf_density=(len(mons) / (2.0 ** dense)) if mons else None,
                             semaev_monomials=len(S.monomials()),
                             semaev_degree_per_variable=max(S.degrees()),
                             build_seconds=round(build, 3)))
        except Exception as exc:
            rows.append(dict(n=n, m=m, l=l, error=str(exc)[:200]))
    scored = [r for r in rows if "measured_boolean_degree" in r]
    return dict(cells=rows,
                law_holds=all(r["measured_boolean_degree"] == r["predicted_degree"]
                              for r in scored),
                cells_measured=len(scored),
                anf_density_range=([min(r["anf_density"] for r in scored),
                                    max(r["anf_density"] for r in scored)]
                                   if scored else None))


# ---------------------------------------------------------------- phase 4 ----
def phase_solver_ladder(ladders, timeout_seconds):
    from pdp import curve, semaev, subspace_basis, descend
    from sage.all import Ideal, set_random_seed
    out = {}
    for m_str, ns in ladders.items():
        m = int(m_str)
        rows = []
        for n in ns:
            l = -(-n // m)
            try:
                K, E, a6 = curve(n, seed=3)
                _, S = semaev(m, K, a6)
                basis = subspace_basis(K, n, l, seed=5)
                Vset = [sum((K(c) * b for c, b in zip(co, basis)), K(0))
                        for co in itertools.product([0, 1], repeat=l)]
                FB = []
                for x in Vset:
                    try:
                        FB += E.lift_x(x, all=True)
                    except Exception:
                        pass
                if len(FB) < m + 2:
                    rows.append(dict(n=n, l=l, skipped="factor base too small",
                                     factor_base=len(FB)))
                    continue
                set_random_seed(11 + n)
                pts = [FB[(3 * i + 1) % len(FB)] for i in range(m)]
                Rsat = sum(pts[1:], pts[0])
                Rrand = E.random_point()
                while Rrand[0] in set(Vset) or Rrand == E(0):
                    Rrand = E.random_point()
                row = dict(n=n, l=l, m=m, variables=m * l, factor_base=len(FB))
                for tag, target in (("sat", Rsat), ("random", Rrand)):
                    if target == E(0):
                        row[tag] = dict(skipped="target is the identity")
                        continue
                    t0 = time.perf_counter()
                    B, eqs = descend(S, basis, target[0], m, n)
                    tb = time.perf_counter() - t0
                    entry = dict(equations=len(eqs),
                                 boolean_degree=max(e.deg() for e in eqs),
                                 build_seconds=round(tb, 3))
                    signal.alarm(int(timeout_seconds))
                    try:
                        t0 = time.perf_counter()
                        gb = list(Ideal(eqs).groebner_basis())
                        entry["groebner_seconds"] = round(time.perf_counter() - t0, 4)
                        signal.alarm(0)
                        entry["unsat"] = (len(gb) == 1 and gb[0] == B(1))
                        entry["timed_out"] = False
                    except TIMEOUTS:
                        signal.alarm(0)
                        entry.update(groebner_seconds=None, timed_out=True,
                                     timeout_seconds=timeout_seconds,
                                     note=("Execution status, not a mathematical "
                                           "result: the cell is uncharacterised, "
                                           "not proven hard."))
                    row[tag] = entry
                rows.append(row)
            except Exception as exc:
                rows.append(dict(n=n, l=l, error=str(exc)[:200]))
        out[m_str] = dict(cells=rows, fits=_fit_exponents(rows))
    return out


def _fit_exponents(rows, min_points=4):
    """Least-squares slope of log2(seconds) against descended variable count.

    Fitted ONLY over completed cells; timed-out cells are excluded and counted.
    A slope is reported with a 95% interval and the number of points, so a fit
    from three points cannot be mistaken for a law.
    """
    fits = {}
    for tag in ("sat", "random"):
        pts, censored = [], 0
        for r in rows:
            e = r.get(tag)
            if not isinstance(e, dict):
                continue
            if e.get("timed_out"):
                censored += 1
                continue
            s = e.get("groebner_seconds")
            if s and s > 0:
                pts.append((r["variables"], log2(s)))
        # drop the flat small-n regime: fit the largest half of the ladder
        pts = sorted(pts)
        tail = pts[len(pts) // 2:] if len(pts) >= 2 * min_points else pts
        fits[tag] = _ols(tail, censored, len(pts))
    return fits


def _ols(pts, censored, total_points):
    k = len(pts)
    if k < 3:
        return dict(slope=None, points=k, censored_cells=censored,
                    total_completed=total_points,
                    note="fewer than three completed cells; no slope reported")
    sx = sum(p[0] for p in pts); sy = sum(p[1] for p in pts)
    sxx = sum(p[0] ** 2 for p in pts); sxy = sum(p[0] * p[1] for p in pts)
    den = k * sxx - sx * sx
    if den == 0:
        return dict(slope=None, points=k, censored_cells=censored,
                    note="degenerate design: all cells share a variable count")
    b = (k * sxy - sx * sy) / den
    a = (sy - b * sx) / k
    resid = [p[1] - (a + b * p[0]) for p in pts]
    s2 = sum(r * r for r in resid) / (k - 2)
    se = sqrt(s2 / (sxx - sx * sx / k))
    return dict(slope=b, intercept=a, stderr=se,
                ci95=[b - 1.96 * se, b + 1.96 * se],
                points=k, censored_cells=censored, total_completed=total_points,
                variable_range=[min(p[0] for p in pts), max(p[0] for p in pts)])


# --------------------------------------------------------------------------- #
PHASES = ("self_test", "budget_table", "degree_law", "solver_ladder")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--plan", required=True)
    ap.add_argument("--resume", action="store_true")
    a = ap.parse_args()
    rd = Path(a.run_dir); rd.mkdir(parents=True, exist_ok=True)
    (rd / "checkpoint").mkdir(exist_ok=True)
    plan = json.loads(Path(a.plan).read_text()); panel = plan["panel"]
    here = Path(__file__).resolve().parent

    receipt = dict(experiment=EXPERIMENT, run_id=plan["run_id"], started_at=stamp(),
                   trial_plan_sha256=sha(a.plan),
                   source_sha256={s: sha(here / s) for s in SOURCES},
                   python=sys.version, platform=platform.platform(),
                   phases={}, status="running")
    results, failed = {}, None
    for name in PHASES:
        cp = rd / "checkpoint" / f"{name}.json"
        if a.resume and cp.exists():
            d = json.loads(cp.read_text())
            results[name] = d["result"]; receipt["phases"][name] = dict(d["meta"], resumed=True)
            continue
        t0 = time.perf_counter()
        try:
            if name == "self_test":
                r = phase_self_test()
            elif name == "budget_table":
                r = phase_budget_table(panel["q"], panel["targets"], panel["m_values"])
            elif name == "degree_law":
                r = phase_degree_law([tuple(c) for c in panel["degree_cells"]])
            elif name == "solver_ladder":
                r = phase_solver_ladder(panel["ladders"], panel["ladder_timeout_seconds"])
        except Exception:
            failed = dict(phase=name, traceback=traceback.format_exc()[-4000:])
            receipt["phases"][name] = dict(status="error",
                                           wall_seconds=round(time.perf_counter() - t0, 3))
            break
        meta = dict(status="ok", wall_seconds=round(time.perf_counter() - t0, 3),
                    completed_at=stamp(), resumed=False)
        tmp = cp.with_suffix(".tmp")
        tmp.write_text(json.dumps(dict(result=r, meta=meta), default=jsonable))
        tmp.replace(cp)
        results[name] = r; receipt["phases"][name] = meta
    receipt["finished_at"] = stamp()
    receipt["status"] = "error" if failed else "completed"
    if failed:
        receipt["failure"] = failed
        receipt["infrastructure_note"] = ("A phase failed. Per AGENTS.md rule 3 this is "
                                          "execution status, not negative mathematical "
                                          "evidence about any hypothesis.")
    (rd / "raw-result.json").write_text(
        json.dumps(results, indent=1, sort_keys=True, default=jsonable))
    receipt["raw_result_sha256"] = sha(rd / "raw-result.json")
    (rd / "execution-receipt.json").write_text(
        json.dumps(receipt, indent=1, sort_keys=True, default=jsonable))
    print("status:", receipt["status"])
    for k, v in receipt["phases"].items():
        print(f"  {k}: {v.get('status')} {v.get('wall_seconds')}s")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
