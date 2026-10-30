#!/usr/bin/env python3
"""Per-cell runner for EXP-MONO-1a1be2 (TASK-20261029-a97206, IM-8).

Two entry points:

  launcher.py cell --cell-id ID --plan PLAN.json --run-id RUN-ID [--workers K]
      A contract cell. REFUSED unless the specification status is `approved` with a non-null `approved_by`
      and an approval lock exists (experiments/EXP-MONO-1a1be2/approval.lock, JSON with approved_by,
      specification_sha256, code_sha256, trial_plan_sha256 that must match the files on disk and the plan
      passed). After the gate the start-up known-answer suite (pytest code/tests/test_kat.py) must pass in
      full. Writes experiments/EXP-MONO-1a1be2/runs/<RUN-ID>/ (manifest.yaml, command.txt, environment.json,
      stdout.log, stderr.log, raw-result.json, summary.json, and results/<cell_id>.cdf.json for arm C).

  launcher.py --kat kat --arm {A,B,C} --q Q --n N [--m M] --curve-seed STR [...]
      A known-answer cell, explicit flag, written under a temporary directory and never under runs/. Refused
      for any (q, n) that is an arm-A/arm-B contract cell (KAT cells are disjoint from the contract).
      Derived statistics (ratios, coverage, frequencies) are withheld in KAT mode; only raw counts are written.

Nothing here is a run until a cell is executed through `cell`. Library functions (run_cell) are used by the
tests on KAT cells only.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
import platform
import resource
import shutil
import subprocess
import sys
import tempfile
import time
import traceback
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402

import counters  # noqa: E402
import curves  # noqa: E402
import fqn  # noqa: E402
import make_trial_plan as mtp  # noqa: E402
import semaev  # noqa: E402

EXP_DIR = os.path.abspath(os.path.join(HERE, ".."))
EXP_ID = "EXP-MONO-1a1be2"
SPEC_PATH = os.path.join(EXP_DIR, "specification.yaml")
LOCK_PATH = os.path.join(EXP_DIR, "approval.lock")
RUNS_DIR = os.path.join(EXP_DIR, "runs")
CODE_FILES = ["fqn.py", "curves.py", "semaev.py", "counters.py", "kernel.c", "launcher.py", "make_trial_plan.py"]
TEST_FILE = os.path.join(HERE, "tests", "test_kat.py")
EXIT_REFUSED = 3
EXIT_SELFTEST = 4


# ----------------------------------------------------------------------------- hashes and gate
def sha256_file(path: str) -> str:
    return counters.file_sha256(path)


def code_sha256() -> str:
    """One digest over the code files (name and sha256 of each, in the fixed order of CODE_FILES)."""
    h = hashlib.sha256()
    for name in CODE_FILES:
        h.update(f"{name}:{sha256_file(os.path.join(HERE, name))}\n".encode())
    return h.hexdigest()


def code_file_hashes() -> dict:
    return {name: sha256_file(os.path.join(HERE, name)) for name in CODE_FILES}


def check_approval(spec_path: str = SPEC_PATH, lock_path: str = LOCK_PATH, plan_path: str | None = None):
    """(ok, reasons). The specification must be approved with approved_by set and the lock must exist and
    bind the current specification, code and trial plan."""
    import yaml
    reasons = []
    try:
        with open(spec_path) as fh:
            spec = yaml.safe_load(fh)
        exp = spec.get("experiment", {})
    except Exception as e:  # noqa: BLE001
        return False, [f"cannot read specification: {e}"]
    if exp.get("status") != "approved":
        reasons.append(f"specification status is {exp.get('status')!r}, not 'approved'")
    if not exp.get("approved_by"):
        reasons.append("specification approved_by is null")
    if not os.path.exists(lock_path):
        reasons.append("approval lock missing: " + os.path.relpath(lock_path, EXP_DIR))
    else:
        try:
            with open(lock_path) as fh:
                lock = json.load(fh)
        except Exception as e:  # noqa: BLE001
            lock = {}
            reasons.append(f"approval lock unreadable: {e}")
        # Every field is checked unconditionally: an empty or non-object lock binds nothing and must refuse.
        if not isinstance(lock, dict) or not lock:
            reasons.append("approval lock is empty or not a JSON object")
            lock = {}
        if not lock.get("approved_by"):
            reasons.append("approval lock has no approved_by")
        if lock.get("specification_sha256") != sha256_file(spec_path):
            reasons.append("approval lock specification_sha256 differs from the specification on disk")
        if lock.get("code_sha256") != code_sha256():
            reasons.append("approval lock code_sha256 differs from the code on disk (invalid build)")
        if plan_path is not None and lock.get("trial_plan_sha256") != sha256_file(plan_path):
            reasons.append("approval lock trial_plan_sha256 differs from the trial plan passed")
    return (not reasons), reasons


def run_startup_selftest(receipt_path: str | None = None) -> tuple[bool, str]:
    """The start-up known-answer suite: the full pytest file, in a subprocess, no bytecode, no cache.
    With receipt_path, a JSON receipt binding code_sha256 and the test file's sha256 may stand in for a
    re-run of the same suite on the same code (written after a full pass); without it the suite always runs."""
    key = {"code_sha256": code_sha256(), "test_file_sha256": sha256_file(TEST_FILE)}
    if receipt_path and os.path.exists(receipt_path):
        try:
            with open(receipt_path) as fh:
                rec = json.load(fh)
            if all(rec.get(k) == v for k, v in key.items()) and rec.get("result") == "passed":
                return True, "receipt " + receipt_path
        except Exception:  # noqa: BLE001
            pass
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", TEST_FILE],
                       capture_output=True, text=True, env=env, cwd=HERE)
    ok = r.returncode == 0
    if ok and receipt_path:
        with open(receipt_path, "w") as fh:
            json.dump(dict(key, result="passed", pytest_tail=(r.stdout or "")[-300:]), fh, indent=1)
    return ok, (r.stdout + r.stderr)[-4000:]


# ----------------------------------------------------------------------------- environment record
def git_state() -> dict:
    root = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
    def g(*args):
        r = subprocess.run(["git", "-C", root] + list(args), capture_output=True, text=True)
        return r.returncode, r.stdout.strip()
    rc, head = g("rev-parse", "HEAD")
    if rc != 0:
        return {"commit": None, "dirty": None, "note": "git state unavailable at " + root}
    rc2, st = g("status", "--porcelain")
    return {"commit": head, "dirty": bool(st) if rc2 == 0 else None,
            "dirty_paths_count": len(st.splitlines()) if rc2 == 0 else None}


def environment_record() -> dict:
    import numpy
    try:
        import yaml
        yv = yaml.__version__
    except Exception:  # noqa: BLE001
        yv = None
    try:
        import pytest
        pv = pytest.__version__
    except Exception:  # noqa: BLE001
        pv = None
    u = platform.uname()
    return {
        "interpreter": {"executable": sys.executable, "version": sys.version, "implementation": platform.python_implementation()},
        "libraries": {"numpy": numpy.__version__, "pyyaml": yv, "pytest": pv},
        "compiler": counters.compiler_record(),
        "host": {"system": u.system, "release": u.release, "machine": u.machine, "node": u.node,
                 "cpu_count": os.cpu_count()},
        "git": git_state(),
        "code_sha256": code_sha256(), "code_file_sha256": code_file_hashes(),
        "random_sources": ["numpy PCG64 seeded per the specification seed rules (curves, bases, tuples, targets)",
                           "random.Random(20261029) choosing points in baby-step giant-step (does not affect N)",
                           "random.Random(20261029) in Cantor-Zassenhaus root splitting (does not affect the root set)"],
    }


# ----------------------------------------------------------------------------- cell execution
def _hist_str(h):
    return {str(k): v for k, v in sorted(h.items())}


def build_instance(q: int, n: int, curve_seed_string: str, expect: dict | None = None):
    F = fqn.FQ(q, n)
    E, info = curves.generate_curve(F, curve_seed_string)
    if expect is not None:
        for key, val in (("g", list(F.g)), ("a", list(E.a)), ("b", list(E.b))):
            if expect.get(key) != val:
                raise RuntimeError(f"identity mismatch for {key}: plan {expect.get(key)} vs regenerated {val}")
    return F, E, info


def _cell_summary_arm_a(res: dict, derived: bool):
    out = {}
    for role, r in res.items():
        d = {"B": r["B"], "t2": r["t2"], "N": r["N"], "size_X": r["size_X"], "S_size": r["S_size"],
             "generic_targets": r["generic_targets"], "special_targets": r["special_targets_O_and_E2"],
             "recount": r["recount"]}
        if "identities" in r:
            d["identities"] = r["identities"]
        if derived:
            conv = {}
            for c in ("A", "M", "S", "X"):
                st = r["conventions"][c]["stats"]
                conv[c] = {"mean_all": str(Fraction(st["all"]["sum"], st["all"]["targets"])),
                           "mean_generic": (str(Fraction(st["generic"]["sum"], st["generic"]["targets"]))
                                            if st["generic"]["targets"] else None),
                           "coverage_generic": ([st["generic"]["targets"] - st["generic"]["zeros"], st["generic"]["targets"]])}
            d["derived"] = conv
        out[role] = d
    return out


def run_arm_a(spec: dict, kernel, derived: bool, log):
    q, n, m = spec["q"], spec["n"], spec["m"]
    F, E, info = build_instance(q, n, spec["curve_seed"], spec.get("identity"))
    N, mask = kernel.valid_mask(E)
    if spec.get("identity") and spec["identity"].get("N") not in (None, N):
        raise RuntimeError(f"N mismatch: plan {spec['identity']['N']} vs counted {N}")
    D, X, t2 = E.factor_base()
    B = len(D)
    log(f"arm A cell {spec['cell_id']}: q={q} n={n} m={m} N={N} B={B} t2={t2} |X|={len(X)}")
    bases = {"line": D}
    seeds = spec.get("base_seeds", {})
    if "matched_random" in seeds:
        bases["matched_random"] = counters.matched_random_base(E, B, t2, curves.make_rng(seeds["matched_random"]))
    if "half_twin" in seeds:
        bases["half_twin"] = counters.twin_base(E, B, t2, curves.make_rng(seeds["half_twin"]))
    if "matched_random_reseeded_aa" in seeds:
        bases["matched_random_reseeded_aa"] = counters.matched_random_base(
            E, B, t2, curves.make_rng(seeds["matched_random_reseeded_aa"]))
    results = {}
    for role, pts in bases.items():
        Xl = counters.x_lifts(F, pts)
        t0 = time.perf_counter()
        results[role] = counters.exhaustive_cell(kernel, E, pts, Xl, m, N, mask, recount=True)
        results[role]["wall_seconds"] = time.perf_counter() - t0
        if not derived:                      # KAT mode: no cross-convention comparison is written
            results[role].pop("identities", None)
        log(f"  base {role}: B={len(pts)} done in {results[role]['wall_seconds']:.2f}s")
    raw = {"arm": "A", "cell_id": spec["cell_id"], "N": N, "curve_generation": info, "bases": results,
           "conventions_definition": "see counters.py module docstring"}
    return raw, _cell_summary_arm_a(results, derived), None


def arm_c_entry(r: dict, base_size: int, derived: bool, wall: float) -> dict:
    """Per-base record of an arm-C cell from the counter's output dict (pure function of `r`)."""
    counts = np.asarray(r["sampled_counts"])
    hist = {int(c): int(v) for c, v in zip(*np.unique(counts.astype(np.int64), return_counts=True))}
    entry = {"B": base_size, "t2": r["t2"], "S_size": r["S_size"], "draws": r["draws"],
             "multisets": r["multisets"], "cancellation_free_multisets": r["cancellation_free"],
             "N_cf_formula": str(r["N_cf_formula"]), "m_S": r["m_S"],
             "lambda_exact": [r["lambda"].numerator, r["lambda"].denominator], "lambda": float(r["lambda"]),
             "hist": _hist_str(hist), "exceptional_targets": [int(c) for c in r["S_counts"]],
             "wall_seconds": wall}
    if derived:
        entry["poisson"] = counters.poisson_summary(counts, float(r["lambda"]))
    return entry


CDF_POISSON_KEYS = ("cdf_empirical", "cdf_poisson", "ks_stat", "chi2_stat", "chi2_df", "zero_fraction", "coverage",
                    "dispersion_index", "max_count", "p_max_pred")


def arm_c_flat(entry: dict, derived: bool) -> dict:
    """Flatten a per-base record into the IDEA machine_readable_output key layout (pure)."""
    flat = {k: v for k, v in entry.items() if k != "poisson"}
    if derived:
        flat.update({k: entry["poisson"][k] for k in CDF_POISSON_KEYS})
    return flat


def run_arm_c(spec: dict, kernel, derived: bool, log):
    q, n, m, s = spec["q"], spec["n"], spec["m"], spec["s"]
    F, E, info = build_instance(q, n, spec["curve_seed"], spec.get("identity"))
    if F.Q < 2 ** 27:
        N, method = kernel.count_points(E), "exhaustive_kernel"
    else:
        N, _ = E.count_points_bsgs()
        method = "bsgs"
    if spec.get("identity") and spec["identity"].get("N") not in (None, N):
        raise RuntimeError(f"N mismatch: plan {spec['identity']['N']} vs counted {N}")
    D, X, t2 = E.factor_base()
    B = len(D)
    log(f"arm C cell {spec['cell_id']}: q={q} n={n} m={m} s={s} N={N} B={B} t2={t2}")
    bases = {"line": D}
    if "matched_random" in spec.get("base_seeds", {}):
        bases["matched_random"] = counters.matched_random_base(
            E, B, t2, curves.make_rng(spec["base_seeds"]["matched_random"]))
    cdf = {"cell_id": spec["cell_id"], "n": n, "q": q, "curve_id": spec["curve_index"],
           "seed": spec["curve_seed"], "B": B, "t2": t2, "N": N, "s": s}
    raw_bases = {}
    for role, pts in bases.items():
        t0 = time.perf_counter()
        tr = curves.make_rng(spec["target_seed"])
        r = counters.arm_c_cell(kernel, E, pts, m, s, tr, N)
        entry = arm_c_entry(r, len(pts), derived, time.perf_counter() - t0)
        raw_bases[role] = entry
        flat = arm_c_flat(entry, derived)
        if role == "line":
            cdf.update(flat)                     # IDEA machine_readable_output keys, line base at top level
        else:
            cdf[role] = flat
        log(f"  base {role}: multisets={r['multisets']} done in {entry['wall_seconds']:.2f}s")
    raw = {"arm": "C", "cell_id": spec["cell_id"], "N": N, "N_method": method, "curve_generation": info,
           "bases": raw_bases}
    summary = {"cell_id": spec["cell_id"], "s": s, "B": B, "t2": t2, "N": N,
               "bases": {k: {"lambda_exact": v["lambda_exact"], "multisets": v["multisets"],
                             "cancellation_free_multisets": v["cancellation_free_multisets"], "m_S": v["m_S"],
                             "max_count": max(int(c) for c in v["hist"]),
                             **({"poisson": {k2: v["poisson"][k2] for k2 in
                                             ("coverage", "zero_fraction", "dispersion_index", "ks_stat",
                                              "chi2_stat", "chi2_df", "max_count", "p_max_pred")}}
                                if derived else {})} for k, v in raw_bases.items()}}
    return raw, summary, cdf


TALLY_KEYS = ("tuples", "zero_poly", "degree_deficient", "not_squarefree", "any_chi_zero", "eligible",
              "eligible_split", "eligible_all_chi_equal", "disagree", "gl_checked", "gl_checked_generic",
              "gl_mismatch_generic", "gl_mismatch_nongeneric", "gl_inf_sums")


def _analyse_block(args):
    """Worker: analyse a block of x-tuples (list of lists of code tuples). Returns tallies."""
    (q, n, g, a, b, xs_block, do_group_law_mask) = args
    F = fqn.FQ(q, n, tuple(g))
    E = curves.Curve(F, tuple(a), tuple(b))
    F2 = fqn.FQ2(F)
    patterns: dict = {}
    t = dict.fromkeys(TALLY_KEYS, 0)
    for tup, do_gl in zip(xs_block, do_group_law_mask):
        xs = [tuple(x) for x in tup]
        res = semaev.analyse_fibre(F, E, xs, detail=bool(do_gl))
        t["tuples"] += 1
        generic = False
        if res["zero_poly"]:
            t["zero_poly"] += 1
        else:
            if not res["full_degree"]:
                t["degree_deficient"] += 1
            if not res["squarefree"]:
                t["not_squarefree"] += 1
            generic = res["full_degree"] and res["squarefree"]
        status = "na"
        if 0 in res["chis"]:
            t["any_chi_zero"] += 1
        elif generic:
            t["eligible"] += 1
            split = bool(res["split_completely"])
            if do_gl and split != bool(res["split_check_xq"]):
                raise RuntimeError("ddf and x^Q-x split tests disagree (implementation error)")
            alleq = len(set(res["chis"])) == 1
            t["eligible_split"] += split
            t["eligible_all_chi_equal"] += alleq
            t["disagree"] += (split != alleq)
            status = "split" if split else "nonsplit"
        pat = "".join("+" if c == 1 else "-" if c == -1 else "0" for c in res["chis"]) + "|" + status
        patterns[pat] = patterns.get(pat, 0) + 1
        if do_gl:
            roots, ninf = semaev.roots_via_group_law(F, E, xs, F2)
            t["gl_checked"] += 1
            t["gl_inf_sums"] += ninf
            if generic:
                t["gl_checked_generic"] += 1
                t["gl_mismatch_generic"] += (roots != res["roots_Fq"])
            else:
                t["gl_mismatch_nongeneric"] += (roots != res["roots_Fq"])
    t["chi_patterns"] = patterns
    return t


def _sum_tallies(ts):
    # Start from zero counters so an instance with no tuples still yields a complete tally.
    out: dict = dict.fromkeys(TALLY_KEYS, 0)
    for t in ts:
        for k, v in t.items():
            if isinstance(v, dict):
                d = out.setdefault(k, {})
                for kk, vv in v.items():
                    d[kk] = d.get(kk, 0) + int(vv)
            else:
                out[k] = out.get(k, 0) + int(v)
    out["chi_patterns"] = dict(sorted(out.get("chi_patterns", {}).items()))
    return out


def _block(tuples, i, j):
    if isinstance(tuples, np.ndarray):
        return [[list(map(int, row)) for row in t] for t in tuples[i:j]]
    return [[list(x) for x in t] for t in tuples[i:j]]


def _analyse_all(F, E, tuples, gl_mask, workers: int):
    """Analyse every x-tuple (a list of tuples of field elements, or an (T, n, n) integer array) in blocks of
    2000, in order; tallies are sums, so the result does not depend on the number of workers."""
    block = 2000
    total = len(tuples)
    jobs = ((F.q, F.n, list(F.g), list(E.a), list(E.b), _block(tuples, i, min(i + block, total)),
             gl_mask[i:i + block]) for i in range(0, total, block))
    if workers > 1:
        import multiprocessing as mp
        with mp.Pool(workers) as pool:
            return _sum_tallies(pool.imap(_analyse_block, jobs))
    return _sum_tallies(_analyse_block(j) for j in jobs)


def run_arm_b(spec: dict, kernel, derived: bool, log, workers: int = 1):
    out_inst = []
    # B1 cells that carry tuple_seed_aa also run the independent A/A sample (CTL-aa, C-aa-tupleseed).
    samples = [("primary", spec["tuple_seed"])]
    if spec["arm"] == "B1" and spec.get("tuple_seed_aa"):
        samples.append(("aa", spec["tuple_seed_aa"]))
    for inst in spec["instances"]:
        q, n = inst["q"], spec["n"]
        F, E, info = build_instance(q, n, inst["curve_seed"], inst.get("identity"))
        D, X, t2 = E.factor_base()
        for sample, seed in samples:
            rng = curves.make_rng(seed)
            if spec["arm"] == "B1":
                T = spec["tuples"]
                xs = rng.integers(0, q, size=(T, n, n))
                step = max(int(round(1 / spec["group_law_subsample_fraction"])), 1)
                gl = [(i % step == 0) for i in range(T)]          # subsample rule: every step-th tuple
                tuples = xs
            else:
                maxT = spec["max_tuples_per_instance"]
                nx = len(X)
                if nx < n:
                    tuples = []
                elif math.comb(nx, n) <= maxT:
                    tuples = [[X[i] for i in c] for c in itertools.combinations(range(nx), n)]
                else:
                    tuples = []
                    for _ in range(maxT):
                        idx = sorted(int(i) for i in rng.choice(nx, size=n, replace=False))
                        tuples.append([X[i] for i in idx])
                gl = [True] * len(tuples)
            t0 = time.perf_counter()
            tally = _analyse_all(F, E, tuples, gl, workers)
            el = time.perf_counter() - t0
            log(f"  {spec['cell_id']} q={q} [{sample}]: {tally['tuples']} tuples in {el:.1f}s")
            entry = {"q": q, "n": n, "sample": sample, "tuple_seed": seed, "B": len(D), "t2": t2,
                     "size_X": len(X), "tally": tally, "wall_seconds": el, "curve_generation": info}
            if derived:
                el_n = tally["eligible"]
                entry["derived"] = {"split_fraction_of_eligible": (tally["eligible_split"], el_n),
                                    "disagreements": tally["disagree"]}
            out_inst.append(entry)
    raw = {"arm": spec["arm"], "cell_id": spec["cell_id"], "instances": out_inst}
    return raw, {"cell_id": spec["cell_id"],
                 "instances": [{"q": i["q"], "sample": i["sample"], "tally": i["tally"]} for i in out_inst]}, None


def _install_limits(timeout_seconds, memory_gb):
    import signal
    if memory_gb:
        lim = int(memory_gb * 2 ** 30)
        resource.setrlimit(resource.RLIMIT_AS, (lim, lim))
    if timeout_seconds:
        def _alarm(signum, frame):
            raise TimeoutError(f"watchdog: cell exceeded {timeout_seconds} s")
        signal.signal(signal.SIGALRM, _alarm)
        signal.setitimer(signal.ITIMER_REAL, float(timeout_seconds))


def run_cell(spec: dict, outdir: str, kat: bool, workers: int = 1, kernel=None, command: str = "",
             run_id: str | None = None, timeout_seconds: float | None = None, memory_gb: float | None = None) -> dict:
    """Execute one cell spec and write the run package into outdir. Returns the manifest dict."""
    os.makedirs(outdir, exist_ok=True)
    msgs, errs = [], []
    log = lambda s: msgs.append(s)  # noqa: E731
    tmp = None
    t_start = time.time()
    status, reason = "completed", None
    raw = summary = cdf = None
    try:
        _install_limits(timeout_seconds, memory_gb)
        if kernel is None:
            tmp = tempfile.mkdtemp(prefix="mono1a1be2-kernel-")
            kernel = counters.Kernel(counters.build_kernel(tmp))
        derived = not kat
        arm = spec["arm"]
        if arm == "A":
            raw, summary, cdf = run_arm_a(spec, kernel, derived, log)
        elif arm == "C":
            raw, summary, cdf = run_arm_c(spec, kernel, derived, log)
        elif arm in ("B1", "B2"):
            raw, summary, cdf = run_arm_b(spec, kernel, derived, log, workers)
        else:
            raise ValueError(f"unknown arm {arm}")
    except (TimeoutError, MemoryError):
        status, reason = "failed", "resource_exhaustion"
        errs.append(traceback.format_exc())
    except Exception:  # noqa: BLE001
        status, reason = "failed", "infrastructure_or_implementation_error"
        errs.append(traceback.format_exc())
    finally:
        try:
            import signal
            signal.setitimer(signal.ITIMER_REAL, 0)
        except Exception:  # noqa: BLE001
            pass
        if tmp:
            shutil.rmtree(tmp, ignore_errors=True)
    env = environment_record()
    manifest = {
        "experiment_id": EXP_ID, "run_id": run_id, "cell_id": spec["cell_id"], "arm": spec["arm"],
        "kat": kat, "status": status, "failure_class": reason,
        "identity_fields": {k: spec.get(k) for k in ("q", "n", "m", "curve_seed", "identity", "instances",
                                                     "base_seeds", "tuple_seed", "target_seed", "s")},
        "seeds": {k: spec.get(k) for k in ("curve_seed", "base_seeds", "tuple_seed", "target_seed")},
        "code_sha256": env["code_sha256"], "code_file_sha256": env["code_file_sha256"],
        "git": env["git"], "environment_file": "environment.json", "command_file": "command.txt",
        "started_unix": t_start, "wall_seconds": time.time() - t_start,
        "peak_rss_kb_measured": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "certificate": {"kind": "none", "note": "measurement run; no discrete-log or relation claim"},
        "derived_statistics_withheld": kat,
    }
    def w(name, text):
        with open(os.path.join(outdir, name), "w") as fh:
            fh.write(text)
    import yaml
    w("manifest.yaml", yaml.safe_dump(json.loads(json.dumps(manifest, default=str)), sort_keys=True))
    w("command.txt", command + "\n")
    w("environment.json", json.dumps(env, indent=1, sort_keys=True) + "\n")
    w("stdout.log", "\n".join(msgs) + ("\n" if msgs else ""))
    w("stderr.log", "".join(errs))
    if raw is not None:
        w("raw-result.json", json.dumps(raw, indent=1, sort_keys=True, default=str) + "\n")
        w("summary.json", json.dumps(summary, indent=1, sort_keys=True, default=str) + "\n")
    if cdf is not None:
        os.makedirs(os.path.join(outdir, "results"), exist_ok=True)
        w(os.path.join("results", spec["cell_id"] + ".cdf.json"), json.dumps(cdf, indent=1, sort_keys=True, default=str) + "\n")
    return manifest


# ----------------------------------------------------------------------------- spec from a plan cell
def spec_from_plan_cell(cell: dict) -> list[dict]:
    """One launcher spec per plan cell (B2 carries both instances in one spec)."""
    arm = cell["arm"]
    if arm == "A":
        seeds = {k: v["seed_string"] for k, v in cell["base_roles"].items() if v}
        return [{"arm": "A", "cell_id": cell["cell_id"], "q": cell["q"], "n": cell["n"], "m": cell["tuple_size_m"],
                 "curve_index": cell["curve_index"], "curve_seed": cell["identity"]["curve_seed"]["seed_string"],
                 "identity": cell["identity"], "base_seeds": seeds}]
    if arm == "C":
        seeds = {k: v["seed_string"] for k, v in cell["base_roles"].items() if v}
        return [{"arm": "C", "cell_id": cell["cell_id"], "q": cell["q"], "n": cell["n"], "m": cell["tuple_size_m"],
                 "curve_index": cell["curve_index"], "curve_seed": cell["identity"]["curve_seed"]["seed_string"],
                 "identity": cell["identity"], "base_seeds": seeds, "s": cell["sample_size_s"],
                 "target_seed": cell["target_seed"]["seed_string"]}]
    if arm == "B1":
        aa = cell.get("tuple_seed_aa")
        return [{"arm": "B1", "cell_id": cell["cell_id"], "n": cell["n"], "m": cell["tuple_size_m"],
                 "tuples": cell["tuples"], "group_law_subsample_fraction": cell["group_law_subsample_fraction"],
                 "tuple_seed": cell["tuple_seed"]["seed_string"],
                 "tuple_seed_aa": aa["seed_string"] if aa else None,
                 "instances": [{"q": cell["q"], "curve_seed": cell["identity"]["curve_seed"]["seed_string"],
                                "identity": cell["identity"]}]}]
    if arm == "B2":
        return [{"arm": "B2", "cell_id": cell["cell_id"], "n": cell["n"], "m": cell["tuple_size_m"],
                 "max_tuples_per_instance": cell["max_tuples_per_instance"],
                 "tuple_seed": cell["tuple_seed"]["seed_string"],
                 "instances": [{"q": i["q"], "curve_seed": i["identity"]["curve_seed"]["seed_string"],
                                "identity": i["identity"]} for i in cell["instances"]]}]
    raise ValueError(arm)


# ----------------------------------------------------------------------------- CLI
def cmd_cell(args) -> int:
    ok, reasons = check_approval(plan_path=args.plan)
    if not ok:
        print("REFUSED: contract cell not startable:", file=sys.stderr)
        for r in reasons:
            print("  - " + r, file=sys.stderr)
        return EXIT_REFUSED
    passed, tail = run_startup_selftest(args.selftest_receipt)
    if not passed:
        print("REFUSED: start-up known-answer suite did not pass in full:\n" + tail, file=sys.stderr)
        return EXIT_SELFTEST
    with open(args.plan) as fh:
        plan = json.load(fh)
    cell = next((c for c in plan["cells"] if c["cell_id"] == args.cell_id), None)
    if cell is None:
        print(f"REFUSED: cell {args.cell_id} not in the plan", file=sys.stderr)
        return EXIT_REFUSED
    outdir = os.path.join(RUNS_DIR, args.run_id)
    if os.path.exists(outdir):
        print(f"REFUSED: run directory {outdir} exists (run records are immutable; use a new run id)", file=sys.stderr)
        return EXIT_REFUSED
    spec = spec_from_plan_cell(cell)[0]
    command = " ".join([sys.executable] + sys.argv)
    man = run_cell(spec, outdir, kat=False, workers=args.workers, command=command, run_id=args.run_id,
                   timeout_seconds=args.timeout_seconds, memory_gb=args.memory_gb)
    print(json.dumps({"run_dir": outdir, "status": man["status"]}))
    return 0 if man["status"] == "completed" else 1


def cmd_kat(args) -> int:
    if (args.q, args.n) in mtp.contract_cells_qn():
        print(f"REFUSED: (q={args.q}, n={args.n}) is a contract cell; KAT cells must be disjoint", file=sys.stderr)
        return EXIT_REFUSED
    cid = f"KAT-{args.arm}-n{args.n}-q{args.q}"
    m = args.m or args.n
    spec = {"arm": args.arm, "cell_id": cid, "q": args.q, "n": args.n, "m": m, "curve_index": 0,
            "curve_seed": args.curve_seed}
    if args.arm == "A":
        spec["base_seeds"] = {"matched_random": f"kat|base|{cid}|random|0", "half_twin": f"kat|base|{cid}|twin|0"}
    elif args.arm == "C":
        spec.update(s=args.s, target_seed=f"kat|targets|{cid}", base_seeds={"matched_random": f"kat|base|{cid}|random|0"})
    else:
        spec.update(arm=args.arm, instances=[{"q": args.q, "curve_seed": args.curve_seed}], tuples=args.tuples,
                    group_law_subsample_fraction=0.1, max_tuples_per_instance=args.tuples,
                    tuple_seed=f"kat|tuples|{cid}|0")
    outdir = tempfile.mkdtemp(prefix="mono1a1be2-kat-")
    command = " ".join([sys.executable] + sys.argv)
    man = run_cell(spec, outdir, kat=True, workers=1, command=command, run_id=None)
    print(json.dumps({"kat_dir": outdir, "status": man["status"]}))
    return 0 if man["status"] == "completed" else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--kat", action="store_true", help="known-answer cell: temporary directory, never runs/")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("cell")
    c.add_argument("--cell-id", required=True)
    c.add_argument("--plan", required=True)
    c.add_argument("--run-id", required=True)
    c.add_argument("--workers", type=int, default=1)
    c.add_argument("--selftest-receipt", default=None,
                   help="optional JSON receipt standing in for a re-run of the full KAT suite on identical code")
    c.add_argument("--timeout-seconds", type=float, default=None, help="watchdog; a cell over it is failed (resource_exhaustion), void")
    c.add_argument("--memory-gb", type=float, default=16.0, help="address-space cap (specification budget.maximum_memory_gb: 16)")
    e = sub.add_parser("environment", help="write the environment record (interpreter, libraries, compiler and flags, host)")
    e.add_argument("--out", required=True)
    k = sub.add_parser("kat")
    k.add_argument("--arm", choices=["A", "B1", "B2", "C"], required=True)
    k.add_argument("--q", type=int, required=True)
    k.add_argument("--n", type=int, required=True)
    k.add_argument("--m", type=int)
    k.add_argument("--curve-seed", required=True)
    k.add_argument("--s", type=int, default=40)
    k.add_argument("--tuples", type=int, default=50)
    args = ap.parse_args(argv)
    if args.cmd == "environment":
        with open(args.out, "w") as fh:
            fh.write(json.dumps(environment_record(), indent=1, sort_keys=True) + "\n")
        print("wrote " + args.out)
        return 0
    if args.cmd == "cell":
        if args.kat:
            print("REFUSED: --kat applies to the kat subcommand only", file=sys.stderr)
            return EXIT_REFUSED
        return cmd_cell(args)
    if not args.kat:
        print("REFUSED: the kat subcommand requires the explicit --kat flag", file=sys.stderr)
        return EXIT_REFUSED
    return cmd_kat(args)


if __name__ == "__main__":
    sys.exit(main())
