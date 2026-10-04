#!/usr/bin/env python3
"""EXP-GFPN-05ff43 protocol v2-a1 -- msolve CHARACTERISTIC CHECK on synthetic systems of known degree.

Used by stage-1b development check A1-7 (b), by the AA-3 attribution run at p' = 16777291, and by
controls_a1 check (d) (A1-2 (d)). It never solves a ladder curve, cell or fixture system.

usage: python3 -B a1_health.py --p P --out DIR [--seed SEED] [--reinvoke-on-fail]

Systems. Two SYNTHETIC dense systems in 3 variables x1, x2, x3 over F_P, drawn IN THIS ORDER from
random.Random(SEED) (default '2026092001:v2a1:health:1073741831'; AA-3 (a) runs the SAME seed strings
at 16777291): degrees (2,2,2) then (4,4,4). "Dense" = every monomial of total degree <= d_i present,
each coefficient drawn as rng.randrange(1, P). By Bezout a generic such system is zero-dimensional
of degree 8 and 64.

Solver. /usr/bin/msolve with EXACTLY the v2 cell flags (v2_solver.msolve_argv: -v 2 -t 1 -f IN -o OUT
-P 1), under v2_solver.run_child: RLIMIT_AS = cap set IN THE CHILD and read back with getrlimit (a child
that cannot set it refuses to start), one memory-heavy child at a time, no other solver process.

PASS for one system iff: exit status 0; the output parses as a zero-dimensional parametrisation
(header 0); msolve's "Dimension of quotient" equals the expected D; the eliminating polynomial has
degree D and is square-free; every F_P-rational solution substitutes to 0 (v2 substitution check); and
the PARAMETRISATION ITSELF substitutes: with t the separating element, each equation reduces to 0
modulo the eliminating polynomial, i.e. EVERY one of the D solutions over the algebraic closure is
substituted, not only the rational ones.

On a mismatch the system of the same degree pattern is re-drawn once from SEED + ':2' (A1-7 (b)), to
separate a non-generic draw from a solver fault. With --reinvoke-on-fail a failing command is also
re-invoked once, byte-identical (AA-3 (b) reproduction clause).

Solver-side signals (A1-9, AA-3 (b)) are classified per run: crash_or_signal, refused_characteristic,
unparseable_output, degree_mismatch. Everything is written to OUT/health-<P>.json; msolve inputs,
outputs, logs and stderr are kept in OUT. Nothing here is a result about any ladder object.
"""
import argparse
import json
import os
import random
import sys
import time

sys.dont_write_bytecode = True
import a1_common as AC                                   # noqa: E402  (sets sys.path to implementation-v2/)

import flint                                             # noqa: E402
flint.ctx.threads = 1

import v2_arms as A                                      # noqa: E402
import v2_solver as V                                    # noqa: E402

NAMES = ["x1", "x2", "x3"]
PATTERNS = [(2, 2, 2), (4, 4, 4)]
EXPECTED = {(2, 2, 2): 8, (4, 4, 4): 64}
DEV_TIMEOUT_S = 1800   # synthetic n-variable check; uses the m = 3 per-target value of trial-plan-v2.json


def dense_system(rng, p, degs, nvars=3):
    eqs = []
    for d in degs:
        eqs.append({a: rng.randrange(1, p) for a in A.monomials_total(nvars, d)})
    return eqs


def draw(seed, p):
    rng = random.Random(seed)
    return {degs: dense_system(rng, p, degs) for degs in PATTERNS}


def _poly(coeffs, p):
    return flint.nmod_poly([int(c) % p for c in coeffs], p)


def param_substitution(par, eqs, p, nvars):
    """Substitute msolve's rational parametrisation into every equation modulo the eliminating polynomial.
    Returns (ok, detail). Covers all D solutions over the algebraic closure."""
    elim = _poly(par["elim"][1], p)
    den = _poly(par["den"][1], p)
    if elim.degree() < 1:
        return False, "eliminating polynomial of degree < 1"

    def inv_mod(a):
        g, s, _t = a.xgcd(elim)
        if g.degree() != 0:
            return None
        return (s * pow(int(g[0]), -1, p)) % elim

    xs = []
    for entry in par["params"]:
        v = _poly(entry[0][1], p)
        cst = int(entry[1]) if len(entry) > 1 else 1
        inv = inv_mod((den * cst) % elim)
        if inv is None:
            return False, "c_i * den(t) not invertible modulo the eliminating polynomial"
        xs.append((-v * inv) % elim)
    t = flint.nmod_poly([0, 1], p)
    lin = [int(c) % p for c in (par.get("linform") or [])]
    if len(xs) == nvars - 1:
        if len(lin) != nvars or lin[-1] == 0:
            return False, "cannot recover the last variable from linear form %r" % (lin,)
        rest = t
        for c, x in zip(lin[:-1], xs):
            rest = rest - x * c
        xs.append((rest * pow(lin[-1], -1, p)) % elim)
    elif len(xs) != nvars:
        return False, "parametrisation has %d entries for %d variables" % (len(xs), nvars)
    for j, eq in enumerate(eqs):
        acc = flint.nmod_poly([0], p)
        for a, c in eq.items():
            term = flint.nmod_poly([c % p], p)
            for x, e in zip(xs, a):
                if e:
                    term = (term * _powmod(x, e, elim)) % elim
            acc = (acc + term) % elim
        if acc != 0:
            return False, "equation %d does not vanish modulo the eliminating polynomial" % j
    return True, "all %d equations vanish modulo the eliminating polynomial (degree %d)" % (len(eqs), elim.degree())


def _powmod(x, e, m):
    r = flint.nmod_poly([1], m.modulus())
    b = x % m
    while e:
        if e & 1:
            r = (r * b) % m
        b = (b * b) % m
        e >>= 1
    return r


def _tail(path, n=50):
    try:
        with open(path, errors="replace") as fh:
            return fh.read().splitlines()[-n:]
    except OSError as e:
        return ["<unreadable: %s>" % e]


REFUSAL_PATTERNS = ("characteristic", "prime", "too large", "not supported", "unsupported", "field")


def run_system(p, eqs, degs, tag, out_dir, cap):
    inp = os.path.join(out_dir, tag + ".ms")
    out = os.path.join(out_dir, tag + ".ms.out")
    wi = A.write_msolve_input(inp, NAMES, p, eqs)
    argv = V.msolve_argv(inp, out, threads=1)
    logp, errp = os.path.join(out_dir, tag + ".ms.log"), os.path.join(out_dir, tag + ".ms.err")
    t0 = time.time()
    rec = V.run_child(argv, logp, errp, cap_bytes=cap, timeout_s=DEV_TIMEOUT_S, count_instructions=False)
    res = {"tag": tag, "p": p, "degrees": list(degs), "expected_D": EXPECTED[degs], "input": {"path": inp, "sha256": AC.sha256_file(inp), **wi},
           "command": " ".join(argv), "threads_executed": V.threads_from_argv(argv),
           "child": {k: rec.get(k) for k in ("outcome", "returncode", "timed_out", "wall_seconds", "rlimit_as_child_getrlimit",
                                              "rlimit_as_proc_limits_after_exec", "peak_rss_bytes", "peak_vm_bytes", "refusal_reason",
                                              "child_rlimit_report", "memory_exhausted_basis")}}
    rc = rec.get("returncode")
    res["exit_status"] = rc if (rc is not None and rc >= 0) else None
    res["signal"] = (-rc) if (rc is not None and rc < 0) else None
    res["stderr_tail_50"] = _tail(errp)
    text = ""
    for f in (logp, errp):
        try:
            text += open(f, errors="replace").read() + "\n"
        except OSError:
            pass
    st = V.parse_msolve_log(text)
    res["dimension_of_quotient_printed"] = st["dimension_of_quotient"]
    kind = payload = sinfo = None
    nfail = None
    if rec.get("outcome") == "ok":
        kind, payload = V.parse_msolve_param(out)
        res["parse_kind"] = kind
        if kind == "param":
            sols, sinfo = V.rational_solutions(payload, p, len(NAMES))
            nfail = sum(1 for s in sols if not V.substitute(eqs, s, p))
            res["n_rational_solutions"] = len(sols)
            res["rational_substitution_failures"] = nfail
            res["solution_info"] = sinfo
            res["msolve_param_header"] = {"char": payload["char"], "nvars": payload["nvars"], "degree": payload["degree"],
                                          "linform": payload["linform"]}
            ok_p, why_p = param_substitution(payload, eqs, p, len(NAMES))
            res["parametrisation_substitution"] = {"pass": ok_p, "detail": why_p}
        else:
            res["parse_detail"] = payload
        outcome, reason = V.classify_solve(rec, st, kind, payload, sinfo, nfail or 0)
    else:
        outcome, reason = rec.get("outcome"), rec.get("refusal_reason")
    res["v2_outcome_class"] = outcome
    res["v2_outcome_reason"] = reason
    D = st["dimension_of_quotient"]
    checks = {
        "exit_0": rc == 0,
        "zero_dimensional_parametrisation": kind == "param",
        "quotient_dimension_equals_expected": D == EXPECTED[degs],
        "elim_degree_equals_expected": bool(sinfo) and sinfo.get("elim_degree") == EXPECTED[degs],
        "elim_squarefree": bool(sinfo) and sinfo.get("elim_squarefree") is True,
        "rational_solutions_substitute": nfail == 0,
        "parametrisation_substitutes": bool(res.get("parametrisation_substitution", {}).get("pass")),
        "threads_executed_1": res["threads_executed"] == 1,
    }
    res["checks"] = checks
    res["pass"] = all(checks.values())
    # A1-9 / AA-3 solver-side signal classification (only meaningful on a failure)
    sig = None
    if not res["pass"]:
        errtxt = "\n".join(res["stderr_tail_50"]).lower()
        if rec.get("outcome") == "refused_to_start":
            sig = "harness_refused_to_start"          # our runner refused: NOT a solver-side signal
        elif rc is not None and rc < 0:
            sig = "crash_or_signal"
        elif rc not in (0, None) and any(w in errtxt for w in REFUSAL_PATTERNS):
            sig = "refused_characteristic"
        elif rc not in (0, None):
            sig = "crash_or_signal"
        elif kind in ("unparseable", "positive_dimensional") or kind is None:
            sig = "unparseable_output"
        elif D != EXPECTED[degs] or (sinfo and sinfo.get("elim_degree") != EXPECTED[degs]):
            sig = "degree_mismatch"
        else:
            sig = "substitution_failure"
    res["solver_side_signal"] = sig
    res["wall_seconds"] = round(time.time() - t0, 3)
    return res


def run(p, out_dir, seed=AC.HEALTH_SEED, cap=AC.CAP_BYTES, reinvoke_on_fail=False):
    os.makedirs(out_dir, exist_ok=True)
    others = V.other_solver_processes()
    report = {"check": "msolve characteristic check (A1-7 (b); AA-3; A1-2 (d))", "p": p, "seed": "random.Random('%s')" % seed,
              "retry_seed": "random.Random('%s:2')" % seed, "patterns": [list(x) for x in PATTERNS], "expected": {str(list(k)): v for k, v in EXPECTED.items()},
              "flags": "v2_solver.msolve_argv(threads=1): -v 2 -t 1 -f IN -o OUT -P 1 (the v2 cell flags)",
              "cap_bytes_requested": cap, "other_solver_processes_at_start": others, "msolve": "/usr/bin/msolve", "systems": []}
    systems = draw(seed, p)
    retry = None
    for degs in PATTERNS:
        tag = "health_p%d_d%s" % (p, "".join(map(str, degs)))
        r = run_system(p, systems[degs], degs, tag, out_dir, cap)
        entry = {"pattern": list(degs), "first": r}
        if not r["pass"] and reinvoke_on_fail:
            entry["reinvocation"] = run_system(p, systems[degs], degs, tag + "_reinvoke", out_dir, cap)
        if not r["pass"]:
            if retry is None:
                retry = draw(seed + ":2", p)
            r2 = run_system(p, retry[degs], degs, tag + "_seed2", out_dir, cap)
            entry["retry_seed2"] = r2
            if not r2["pass"] and reinvoke_on_fail:
                entry["retry_seed2_reinvocation"] = run_system(p, retry[degs], degs, tag + "_seed2_reinvoke", out_dir, cap)
        entry["pattern_pass"] = r["pass"] or bool(entry.get("retry_seed2", {}).get("pass"))
        report["systems"].append(entry)
    report["pass"] = all(e["pattern_pass"] for e in report["systems"])
    report["getrlimit_read_backs"] = sorted({json.dumps(x, sort_keys=True) for e in report["systems"] for k in ("first", "reinvocation", "retry_seed2", "retry_seed2_reinvocation")
                                             if k in e for x in [e[k]["child"].get("rlimit_as_child_getrlimit")] if x})
    report["getrlimit_read_backs"] = [json.loads(x) for x in report["getrlimit_read_backs"]]
    with open(os.path.join(out_dir, "health-%d.json" % p), "w") as fh:
        json.dump(report, fh, indent=1, default=str)
    return report


def fb1_trigger(report_31, report_fb1_char):
    """AA-3 (b): FB-1 may trigger ONLY IF the 16777291 run passes, BOTH seeded systems at 1073741831 fail with an
    A1-9 solver-side signal (a degree mismatch counts only if reproduced on ':2'), and every failure reproduces on
    one re-invocation of the failing command."""
    solver_signals = ("crash_or_signal", "refused_characteristic", "unparseable_output", "degree_mismatch")
    out = {"p16777291_pass": bool(report_fb1_char.get("pass")), "per_pattern": []}
    both_fail = True
    for e in report_31["systems"]:
        f = e["first"]
        sig = f.get("solver_side_signal")
        ok_signal = sig in solver_signals
        if sig == "degree_mismatch":
            ok_signal = e.get("retry_seed2", {}).get("solver_side_signal") == "degree_mismatch"
        reproduced = e.get("reinvocation", {}).get("solver_side_signal") == sig if not f["pass"] else False
        fails = (not f["pass"]) and not e.get("pattern_pass")
        out["per_pattern"].append({"pattern": e["pattern"], "fails": fails, "signal": sig, "signal_is_A1_9_solver_side": ok_signal,
                                   "reproduced_on_reinvocation": reproduced})
        both_fail = both_fail and fails and ok_signal and reproduced
    out["fb1_triggers"] = bool(out["p16777291_pass"] and both_fail)
    if not report_31.get("pass") and not report_fb1_char.get("pass"):
        out["attribution"] = "harness (both characteristics fail): fix in stage 1b or STOP; FB-1 does not trigger (AA-3 (b))"
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--p", type=int, required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", default=AC.HEALTH_SEED)
    ap.add_argument("--reinvoke-on-fail", action="store_true")
    a = ap.parse_args()
    rep = run(a.p, a.out, a.seed, reinvoke_on_fail=a.reinvoke_on_fail)
    for e in rep["systems"]:
        f = e["first"]
        print("p=%d pattern=%s pass=%s D=%s exit=%s signal=%s getrlimit=%s" % (a.p, e["pattern"], f["pass"], f["dimension_of_quotient_printed"],
              f["exit_status"], f["signal"], f["child"].get("rlimit_as_child_getrlimit")))
    print("OVERALL pass=%s" % rep["pass"])
    return 0 if rep["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
