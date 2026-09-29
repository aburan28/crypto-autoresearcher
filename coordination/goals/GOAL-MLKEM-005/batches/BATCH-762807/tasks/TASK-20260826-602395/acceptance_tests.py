#!/usr/bin/env python3
"""Acceptance suite for rt_ctrl_1_matched_pair_v2.py -- TASK-20260826-602395.

SIX TESTS, ONE PER DEFECT D1..D6. Each test OBSERVES the repaired behaviour in
an artifact on disk that the v2 instrument itself wrote. No test reads the v2
source and concludes a fix is present; no test re-implements the stub, the
handler or the flush.

ZERO LATTICE COMPUTE AT RESEARCH SCALE. Every lattice touched here is d=64,
beta=20. NO d=512 EXECUTION AND NO mpfr_bits=100 EXECUTION ON A d=512 BASIS
OCCURS ANYWHERE IN THIS FILE. The tiny cells are SURROGATES and are labelled as
such; what they cannot show is stated in implementation_report.md and repeated
in the board.

A FAIL is a legitimate outcome and is written to the board as a FAIL. Nothing
here retunes a threshold after seeing a result.
"""

from __future__ import annotations

import json
import math
import os
import shutil
import signal
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
EVID = os.path.join(HERE, "evidence")
ARTS = os.path.join(HERE, "artifacts")
BOARD = os.path.join(HERE, "acceptance_results.json")
PY = sys.executable
V2_PATH = os.path.join(HERE, "rt_ctrl_1_matched_pair_v2.py")

os.makedirs(EVID, exist_ok=True)
os.makedirs(ARTS, exist_ok=True)

sys.path.insert(0, HERE)
import rt_ctrl_1_matched_pair_v2 as v2  # noqa: E402  the instrument under test

TOY_D = 64
TOY_BETA = 20
TOY_MPFR = 53

SUITE_COMMAND = (
    f"{PY} {os.path.join(HERE, 'acceptance_tests.py')} "
    f"> acceptance_stdout.log 2> acceptance_stderr.log"
)

SURROGATE_LIMITS = (
    "SURROGATE. d=64, beta=20, mpfr_bits=53, tours of milliseconds. It CANNOT "
    "show that a fix survives at d=512 with mpfr_bits=100: it cannot exercise "
    "per-tour flush cost against a tour that takes hours, cannot bound the "
    "flush overhead on a real reduction, and cannot show behaviour over hours "
    "of RSS growth or file-handle lifetime."
)


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


class Checks:
    def __init__(self):
        self.items = []

    def check(self, label, ok, observed):
        self.items.append({"assertion": label, "passed": bool(ok),
                           "observed": observed})
        log(("  PASS " if ok else "  FAIL ") + label + f" | observed={observed}")
        return bool(ok)

    def status(self):
        if not self.items:
            return "NOT_REACHED"
        return "PASS" if all(i["passed"] for i in self.items) else "FAIL"


def read_jsonl(path):
    """Parse a journal. Unparseable lines are RETAINED, never dropped."""
    recs, bad = [], []
    with open(path, "r", errors="replace") as fh:
        for n, line in enumerate(fh, 1):
            if not line.strip():
                continue
            try:
                recs.append(json.loads(line))
            except Exception as exc:
                bad.append({"lineno": n, "raw": line.rstrip("\n"),
                            "error": f"{type(exc).__name__}: {exc}"})
    return recs, bad


# ===================================================================== D6
def test_D6():
    """PURE ARITHMETIC. No lattice, no fpylll. Asserts the correction in CLOSED
    FORM and RECOMPUTES the committed distortion figures instead of quoting."""
    log("D6: closed-form root-Hermite correction")
    c = Checks()
    q = 3329
    out = {"test": "D6_root_hermite_closed_form", "surrogate": False,
           "lattice_used": False, "q": q}

    # (a) closed form, independent of b0, over many b0 and several d
    spread = {}
    for d in (64, 80, 128, 512):
        ratios = []
        for b0 in (1e2, 1e3, 5e3, 2.5e4, 1e6, 1.234e9):
            corrected = v2.root_hermite_factor(b0, q, d)
            defective = v2.root_hermite_factor_legacy_defective(b0, q, d)
            ratios.append(corrected / defective)
        closed = v2.root_hermite_distortion_closed_form(q, d)
        rel = max(abs(r / closed - 1.0) for r in ratios)
        spread[d] = {"closed_form_q_pow_half_minus_1_over_2d": closed,
                     "ratios_over_b0_values": ratios,
                     "max_relative_deviation": rel}
    out["closed_form_by_d"] = spread
    c.check(
        "corrected/defective == q**(1/2 - 1/(2d)) for every tested b0 and d, "
        "rel dev < 1e-12",
        all(v["max_relative_deviation"] < 1e-12 for v in spread.values()),
        {d: v["max_relative_deviation"] for d, v in spread.items()},
    )

    # (b) recompute the committed d=512 distortion (committed value: 57.242)
    d512 = v2.root_hermite_distortion_closed_form(q, 512)
    out["recomputed_distortion_q3329_d512"] = d512
    out["committed_distortion_q3329_d512_quoted"] = 57.242
    c.check("recomputed distortion at (q=3329, d=512) rounds to 57.242",
            round(d512, 3) == 57.242, d512)

    # (c) recompute the committed d=80 distortion (committed value: 54.8457)
    d80 = v2.root_hermite_distortion_closed_form(q, 80)
    out["recomputed_distortion_q3329_d80"] = d80
    out["committed_distortion_q3329_d80_quoted"] = 54.8457
    c.check("recomputed distortion at (q=3329, d=80) rounds to 54.8457",
            round(d80, 4) == 54.8457, d80)

    # (d) the committed d=80 TRIPLE must be internally consistent:
    #     standard_delta_0 / runner_formula == q**(1/2 - 1/160)
    committed_runner = 0.018481105
    committed_delta0 = 1.0136088
    ratio_from_committed = committed_delta0 / committed_runner
    out["committed_d80_triple"] = {
        "runner_defective_formula": committed_runner,
        "standard_delta_0": committed_delta0,
        "ratio_recomputed_from_the_two_committed_numbers": ratio_from_committed,
        "closed_form": d80,
        "relative_deviation": abs(ratio_from_committed / d80 - 1.0),
        "note": (
            "Recomputed here from the two committed numbers; the committed "
            "numbers themselves came from a d=80 basis this task did not run "
            "and cannot reproduce byte-for-byte. What is asserted is the "
            "CONSISTENCY of the committed triple with the closed form, to the "
            "precision at which the two numbers were committed (8 and 8 "
            "significant figures)."
        ),
    }
    c.check(
        "committed d=80 pair (0.018481105, 1.0136088) has ratio == "
        "3329**(1/2-1/160) to within 1e-6 relative",
        abs(ratio_from_committed / d80 - 1.0) < 1e-6, ratio_from_committed)

    # (e) v2's function IS the closed form, not merely close to it
    same = all(
        v2.root_hermite_factor(b0, q, d) == (b0 / q ** 0.5) ** (1.0 / d)
        for b0 in (137.0, 1e4, 3.3e7) for d in (64, 80, 512)
    )
    c.check("v2.root_hermite_factor(b0,q,d) is exactly (b0/q**0.5)**(1/d)",
            same, same)

    # (f) the defective form is exactly the pinned predecessor's line 78
    b0 = 140.93615575855614
    lit = float(b0) ** (1.0 / 512) / (q ** 0.5) ** (1.0 / 1)
    c.check("v2's legacy-defective helper reproduces the predecessor's line 78 "
            "expression exactly",
            v2.root_hermite_factor_legacy_defective(b0, q, 512) == lit, lit)

    out["checks"] = c.items
    out["status"] = c.status()
    out["what_this_cannot_show"] = (
        "It is arithmetic. It says nothing about any basis, any reduction, or "
        "any parameter set; it does not show the corrected formula is the right "
        "figure of merit for anything, only that the predecessor's expression "
        "differs from the standard one by exactly q**(1/2 - 1/(2d))."
    )
    return out, c


# ============================================== the tiny cell (D3, D4, D5)
def run_tiny_cell():
    """ONE tiny cell through v2's OWN run_cell path. Feeds D3, D4 and D5."""
    outdir = os.path.join(ARTS, "D3_D4_D5_tiny_cell")
    shutil.rmtree(outdir, ignore_errors=True)
    os.makedirs(outdir, exist_ok=True)
    journal_path = os.path.join(outdir, "tiny_results.jsonl")
    stdout_path = os.path.join(outdir, "tiny_stdout.log")
    env_path = os.path.join(outdir, "tiny_environment.json")

    env = v2.environment_record(v2.DEFAULT_STRATEGIES)
    env["produced_by"] = "acceptance_tests.py::run_tiny_cell via " \
                         "rt_ctrl_1_matched_pair_v2.environment_record()"
    with open(env_path, "w") as fh:
        json.dump(env, fh, indent=2)

    journal = v2.Journal(journal_path)
    tee = v2.StdoutTee(stdout_path)
    rec = v2.run_cell(
        d=TOY_D, beta=TOY_BETA, mpfr_bits=TOY_MPFR,
        role="ACCEPTANCE tiny cell (SURROGATE, not a measurement)",
        journal=journal, tee=tee, strategies=v2.DEFAULT_STRATEGIES,
        heartbeat_seconds=0.05,
        arm_signals=False,   # the suite keeps its own handlers; D1/D2 test the
                             # arming path in a separate REAL subprocess kill
    )
    results_path = os.path.join(outdir, "tiny_results.json")
    v2.rebuild_results(journal_path, results_path)
    return rec, journal_path, env_path, env, outdir


def test_D3(rec, journal_path):
    log("D3: per-tour progress table")
    c = Checks()
    recs, bad = read_jsonl(journal_path)
    tour_rows = [r for r in recs if r.get("record_kind") == "tour_progress"]
    starts = [r for r in recs if r.get("record_kind") == "tour_start"]
    out = {
        "test": "D3_per_tour_progress", "surrogate": True,
        "surrogate_kind": "tiny_lattice d=64 beta=20 mpfr_bits=53",
        "journal_path": os.path.relpath(journal_path, HERE),
        "tours_table_rows_in_journal": len(tour_rows),
        "tour_start_rows_in_journal": len(starts),
        "tours_table_rows_in_final_record": len(rec.get("tours_table") or []),
        "tours_table_sample_first": tour_rows[0] if tour_rows else None,
        "tours_table_sample_last": tour_rows[-1] if tour_rows else None,
        "unparseable_lines": bad,
        "stdout_lines_mentioning_tour": [
            l for l in (rec.get("stdout_tail") or []) if " tour " in l
        ],
    }
    c.check("the results journal carries MORE THAN ONE tour_progress row",
            len(tour_rows) > 1, len(tour_rows))
    c.check("the final record's tours_table has more than one row",
            len(rec.get("tours_table") or []) > 1,
            len(rec.get("tours_table") or []))
    c.check("every tour row carries index, wall clock and a basis-quality "
            "readout",
            all(("tour_index" in r and "wall_utc" in r
                 and "delta_0_from_gso_logdet" in r
                 and "root_hermite_factor" in r) for r in tour_rows),
            sorted(tour_rows[0].keys()) if tour_rows else None)
    c.check("tour indices are consecutive from 0",
            [r["tour_index"] for r in tour_rows] == list(range(len(tour_rows))),
            [r["tour_index"] for r in tour_rows])
    c.check("per-tour progress also reached stdout",
            len(out["stdout_lines_mentioning_tour"]) > 0,
            len(out["stdout_lines_mentioning_tour"]))
    c.check("no unparseable line in the journal", not bad, len(bad))
    out["checks"] = c.items
    out["status"] = c.status()
    out["what_this_cannot_show"] = SURROGATE_LIMITS
    return out, c


def test_D4(rec, env_path, env):
    log("D4: machine-readable resource record")
    c = Checks()
    ct = rec.get("cpu_times") or {}
    out = {
        "test": "D4_resource_record", "surrogate": True,
        "surrogate_kind": "tiny_lattice d=64 beta=20 mpfr_bits=53",
        "cpu_times": ct,
        "cpu_times_source": (rec.get("resources") or {}).get("cpu_times_source"),
        "peak_rss_bytes": rec.get("peak_rss_bytes"),
        "peak_rss_mb": rec.get("peak_rss_mb"),
        "ru_maxrss_mb_cross_check": (rec.get("resources") or {}).get(
            "ru_maxrss_mb"),
        "psutil_available": rec.get("psutil_available"),
        "psutil_version": rec.get("psutil_version"),
        "stdout_tail_lines": len(rec.get("stdout_tail") or []),
        "stdout_tail": rec.get("stdout_tail"),
        "environment_json_path": os.path.relpath(env_path, HERE),
        "load_average_1_5_15": env.get("load_average_1_5_15"),
        "sampler_samples_observed": rec.get("sampler_samples_observed"),
        "sampler_samples_expected_if_never_starved":
            rec.get("sampler_samples_expected_if_never_starved"),
        "python_executable": env.get("python_executable"),
    }
    c.check("psutil handle available and .cpu_times() non-zero user time",
            bool(rec.get("psutil_available")) and (ct.get("user") or 0) > 0,
            ct.get("user"))
    c.check("peak RSS recorded and non-zero",
            (rec.get("peak_rss_bytes") or 0) > 0, rec.get("peak_rss_mb"))
    c.check("resource.getrusage ru_maxrss cross-check present",
            (out["ru_maxrss_mb_cross_check"] or 0) > 0,
            out["ru_maxrss_mb_cross_check"])
    c.check("load average present in environment.json as a 3-tuple",
            isinstance(env.get("load_average_1_5_15"), list)
            and len(env["load_average_1_5_15"]) == 3,
            env.get("load_average_1_5_15"))
    c.check("stdout_tail non-empty in the machine-readable record",
            len(rec.get("stdout_tail") or []) > 0,
            len(rec.get("stdout_tail") or []))
    out["gil_starvation_observation"] = (
        "MEASURED, reported as an observation. The resource sampler is a Python "
        "thread; fplll's C calls hold the GIL, so heartbeat samples do not "
        "arrive while a tour is running. observed vs expected sample counts are "
        "recorded above. Consequence at scale: peak RSS and cpu_times in a "
        "signal-flushed record are as of the last inter-tour refresh, so at "
        "d=512 they can be a whole tour stale. Named here, not left to review."
    )
    out["checks"] = c.items
    out["status"] = c.status()
    out["what_this_cannot_show"] = SURROGATE_LIMITS
    return out, c


def test_D5(rec, journal_path):
    """Tour count + the EQUIVALENCE CONTROL against upstream __call__."""
    log("D5: tour count, and the upstream-equivalence control")
    c = Checks()
    out = {
        "test": "D5_tour_count", "surrogate": True,
        "surrogate_kind": "tiny_lattice d=64 beta=20 mpfr_bits=53",
        "tours": rec.get("tours"),
        "tours_type": type(rec.get("tours")).__name__,
        "mechanism": rec.get("tours_mechanism"),
        "definition": rec.get("tours_definition"),
        "why_not_bkz_trace": rec.get("tours_why_not_bkz_trace"),
        "break_reason": rec.get("break_reason"),
        "b0_norm": rec.get("b0_norm"),
        "seed_used": rec.get("seed_used"),
    }
    c.check("tours is a non-None int >= 1",
            isinstance(rec.get("tours"), int) and rec["tours"] >= 1,
            rec.get("tours"))
    c.check("the mechanism is recorded in the machine-readable record",
            bool(rec.get("tours_mechanism")) and bool(rec.get(
                "tours_definition")), rec.get("tours_mechanism"))

    # ---- the defect itself, probed live on the same construction ----
    # ---- CONTROL: upstream BKZReduction.__call__ on the SAME seed ----
    try:
        import numpy as np
        from fpylll import GSO, LLL, BKZ, FPLLL, IntegerMatrix
        from fpylll.algorithms.bkz2 import BKZReduction

        seed = int(np.random.default_rng(
            [v2.SEED_ROOT, 0, TOY_D, TOY_BETA, 0, 0]).integers(0, 2 ** 31 - 1))
        FPLLL.set_random_seed(seed)
        A = IntegerMatrix.random(TOY_D, "qary", k=TOY_D // 2, q=v2.Q)
        LLL.reduction(A)
        FPLLL.set_precision(TOY_MPFR)
        M = GSO.Mat(A, float_type="mpfr")
        M.update_gso()
        L = LLL.Reduction(M, flags=LLL.DEFAULT)
        par = BKZ.Param(block_size=TOY_BETA, strategies=v2.DEFAULT_STRATEGIES,
                        flags=BKZ.AUTO_ABORT)
        bkz = BKZReduction(L)
        t0 = time.time()
        bkz(par, tracer=True)
        ctrl_elapsed = time.time() - t0
        labels = []
        for ch in bkz.trace.children:
            lab = ch.label[0] if isinstance(ch.label, tuple) else ch.label
            labels.append(lab)
        ctrl_tours = sum(1 for lab in labels if lab == "tour")
        ctrl_b0 = float(A[0].norm())
        FPLLL.set_precision(53)

        out["equivalence_control"] = {
            "what_it_controls": (
                "That driving the tour loop here did not change the algorithm. "
                "Upstream BKZReduction.__call__ is run on an IDENTICALLY "
                "constructed basis with the SAME seed, and its tour count "
                "(counted from bkz.trace children labelled 'tour', with "
                "tracer=True) and final b0 are compared with v2's."),
            "seed": seed,
            "upstream_tours_from_trace_children": ctrl_tours,
            "upstream_trace_child_labels": labels,
            "upstream_b0_norm": ctrl_b0,
            "upstream_elapsed_seconds": ctrl_elapsed,
            "v2_tours_from_driving_loop": rec.get("tours"),
            "v2_b0_norm": rec.get("b0_norm"),
            "tours_match": ctrl_tours == rec.get("tours"),
            "b0_identical": ctrl_b0 == rec.get("b0_norm"),
            "scale_caveat": (
                "Demonstrated at d=64 ONLY. It establishes that the loop is a "
                "faithful transcription at this dimension; it establishes "
                "NOTHING about d=512 behaviour."),
        }
        c.check("EQUIVALENCE CONTROL: v2's driving-loop tour count equals "
                "upstream __call__'s trace-child tour count on the same seed",
                ctrl_tours == rec.get("tours"),
                {"upstream": ctrl_tours, "v2": rec.get("tours")})
        c.check("EQUIVALENCE CONTROL: final b0 norm identical",
                ctrl_b0 == rec.get("b0_norm"),
                {"upstream": ctrl_b0, "v2": rec.get("b0_norm")})
    except Exception as exc:
        import traceback
        out["equivalence_control"] = {
            "status": "NOT_REACHED",
            "error": f"{type(exc).__name__}: {exc}",
            "traceback": traceback.format_exc(),
        }
        c.check("EQUIVALENCE CONTROL ran", False, out["equivalence_control"])

    # ---- the DEFECT itself, probed live, in its own isolated block ----
    try:
        from fpylll import GSO, LLL, BKZ, IntegerMatrix
        from fpylll.algorithms.bkz2 import BKZReduction

        Ap = IntegerMatrix.random(32, "qary", k=16, q=v2.Q)
        LLL.reduction(Ap)
        Mp = GSO.Mat(Ap, float_type="double")
        Mp.update_gso()
        bkz_default = BKZReduction(LLL.Reduction(Mp, flags=LLL.DEFAULT))
        bkz_default(BKZ.Param(block_size=10, strategies=v2.DEFAULT_STRATEGIES,
                              flags=BKZ.AUTO_ABORT))          # default tracer
        probe = {
            "calling_convention": "bkz(par)  -- the predecessor's line 73",
            "getattr(bkz,'tours',None)": getattr(bkz_default, "tours", None),
            "hasattr(bkz,'tours')": hasattr(bkz_default, "tours"),
            "hasattr(bkz,'trace')": hasattr(bkz_default, "trace"),
            "bkz.trace is None": getattr(bkz_default, "trace", "ABSENT") is None,
            "finding": (
                "BOTH reads are dead under the predecessor's calling "
                "convention. `tours` is never assigned, and `trace` IS "
                "assigned but set to None because "
                "BKZReduction.__call__ defaults tracer=False. Taking `tours` "
                "from bkz.trace naively -- as DEC-20260824-5e222e's wording "
                "prescribes -- would reproduce the always-None defect in a new "
                "costume. This instrument therefore counts in the driving loop "
                "and says so."),
        }
        out["defect_probed_live"] = probe
        c.check("the predecessor's getattr(bkz,'tours',None) is still None AND "
                "bkz.trace is also None after a default bkz(par)",
                probe["getattr(bkz,'tours',None)"] is None
                and probe["bkz.trace is None"] is True, probe)
    except Exception as exc:
        import traceback
        out["defect_probed_live"] = {
            "status": "NOT_REACHED", "error": f"{type(exc).__name__}: {exc}",
            "traceback": traceback.format_exc()}
        c.check("live defect probe ran", False, out["defect_probed_live"])

    # real-basis D6 cross-check, free from the same cell
    last = (rec.get("tours_table") or [{}])[-1]
    if "root_hermite_factor" in last:
        out["real_basis_d6_cross_check"] = {
            "d": TOY_D,
            "b0_norm_from_gso": last.get("b0_norm_from_gso"),
            "root_hermite_factor_corrected": last.get("root_hermite_factor"),
            "root_hermite_factor_legacy_defective":
                last.get("root_hermite_factor_legacy_defective_formula"),
            "measured_ratio": (
                last["root_hermite_factor"]
                / last["root_hermite_factor_legacy_defective_formula"]),
            "closed_form_q_pow_half_minus_1_over_2d":
                v2.root_hermite_distortion_closed_form(v2.Q, TOY_D),
            "delta_0_from_gso_logdet": last.get("delta_0_from_gso_logdet"),
            "note": (
                "A REAL reduced basis at d=64, so this is the R-3b-shaped "
                "cross-check on an actual basis rather than pure arithmetic. "
                "It is d=64, not the d=80 the committed review used, and it is "
                "this task's own seed."),
        }
    out["checks"] = c.items
    out["status"] = c.status()
    out["what_this_cannot_show"] = SURROGATE_LIMITS
    return out, c


# =============================================================== D1 and D2
def _launch_and_signal(tag, argv, kill_after, sig):
    """Launch the v2 instrument as a REAL subprocess and send it a REAL signal."""
    outdir = os.path.join(ARTS, tag)
    shutil.rmtree(outdir, ignore_errors=True)
    os.makedirs(outdir, exist_ok=True)
    stdout_path = os.path.join(outdir, "surrogate_stdout.log")
    full = [PY, V2_PATH, "run", "--out-dir", outdir] + argv
    t0 = time.time()
    with open(stdout_path, "wb") as fh:
        proc = subprocess.Popen(full, stdout=fh, stderr=subprocess.STDOUT)
        if sig is not None:
            time.sleep(kill_after)
            kill_at = time.time()
            os.kill(proc.pid, sig)
        else:
            kill_at = None
        rc = proc.wait(timeout=120)
    return {
        "tag": tag,
        "command": " ".join(full),
        "pid": proc.pid,
        "returncode": rc,
        "signal_sent": None if sig is None else int(sig),
        "signal_sent_name": None if sig is None else signal.Signals(sig).name,
        "sent_after_seconds": None if sig is None else kill_after,
        "sent_at_epoch": kill_at,
        "total_elapsed_seconds": time.time() - t0,
        "out_dir": os.path.relpath(outdir, HERE),
        "stdout_path": os.path.relpath(stdout_path, HERE),
        "journal_path": os.path.join(outdir, "surrogate_results.jsonl"),
        "failed_infrastructure": True,
        "label": "failed_infrastructure",
    }


def test_D1_D2():
    log("D1/D2: STARTED stub + real-SIGTERM flush, in a real subprocess")
    c1, c2 = Checks(), Checks()

    # S1 -- REAL SIGTERM, tiny lattice surrogate, NO sleep anywhere.
    s1 = _launch_and_signal(
        "D1_D2_surrogate_S1_sigterm_failed_infrastructure",
        ["--prefix", "surrogate", "--d", str(TOY_D), "--beta", str(TOY_BETA),
         "--mpfr-bits", "53,53,53,53,53,53", "--heartbeat-seconds", "0.25"],
        kill_after=2.0, sig=signal.SIGTERM)
    s1["surrogate"] = True
    s1["surrogate_kind"] = (
        "TINY LATTICE, no sleep stub anywhere: six d=64 beta=20 mpfr=53 cells "
        "run back to back and SIGTERM delivered 2.0 s in, so the signal lands "
        "in the middle of real fplll work rather than in a Python sleep.")
    s1["why_adequate"] = (
        "What D1/D2 assert is that a record exists after a REAL kill. A tiny "
        "lattice exercises the identical stub/handler/flush code path in "
        "rt_ctrl_1_matched_pair_v2.py -- the acceptance suite launches that "
        "file as a subprocess and re-implements none of it.")
    recs1, bad1 = read_jsonl(s1["journal_path"])
    s1["records"] = recs1
    s1["unparseable_lines"] = bad1
    started1 = [r for r in recs1 if r.get("status") == "STARTED"]
    final1 = [r for r in recs1 if r.get("record_kind") == "cell_final"]
    killed1 = [r for r in recs1 if r.get("status") == "KILLED_PARTIAL"]
    tstart1 = [r for r in recs1 if r.get("record_kind") == "tour_start"]
    tprog1 = [r for r in recs1 if r.get("record_kind") == "tour_progress"]
    s1["counts"] = {"started_stubs": len(started1), "cell_final": len(final1),
                    "killed_partial": len(killed1),
                    "tour_start": len(tstart1), "tour_progress": len(tprog1)}
    s1["kill_landed_inside_a_tour"] = len(tstart1) > len(tprog1)
    s1["cells_started_but_never_finished"] = len(started1) - len(final1)

    c1.check("the process exited on the signal (returncode 128+SIGTERM=143)",
             s1["returncode"] == 143, s1["returncode"])
    c1.check("D1: at least one STARTED stub is on disk", len(started1) >= 1,
             len(started1))
    c1.check("D1: a cell that STARTED and never finished still left a record "
             "(the exact loss BATCH-f9780d suffered)",
             (len(started1) - len(final1)) >= 1,
             s1["cells_started_but_never_finished"])
    c1.check("D1: the STARTED stub carries d, beta, mpfr_bits, role, start "
             "time and status",
             bool(started1) and all(k in started1[-1] for k in
                                    ("d", "beta", "mpfr_bits", "role",
                                     "start_wall_utc", "status")),
             sorted(started1[-1].keys()) if started1 else None)

    c2.check("D2: a KILLED_PARTIAL record is on disk after the real kill",
             len(killed1) == 1, len(killed1))
    kp = killed1[-1] if killed1 else {}
    c2.check("D2: it was flushed by the signal handler and names the signal",
             kp.get("record_kind") == "cell_partial_flushed_from_signal_handler"
             and kp.get("signal") == "SIGTERM", kp.get("signal"))
    c2.check("D2: it carries tours-so-far as an int",
             isinstance(kp.get("tours"), int), kp.get("tours"))
    c2.check("D2: it carries elapsed time",
             isinstance(kp.get("elapsed_seconds_at_refresh"), (int, float)),
             kp.get("elapsed_seconds_at_refresh"))
    c2.check("D2: it carries a non-empty stdout_tail",
             len(kp.get("stdout_tail") or []) > 0,
             len(kp.get("stdout_tail") or []))
    c2.check("D2: it carries the literal failed_infrastructure label",
             kp.get("failed_infrastructure") is True,
             kp.get("failed_infrastructure"))
    c2.check("D2: EVERY line of the journal parses -- no truncated record",
             not bad1, len(bad1))
    c2.check("D2: the kill landed INSIDE a tour (tour_start without a matching "
             "tour_progress), so the flush was not merely between tours",
             s1["kill_landed_inside_a_tour"],
             {"tour_start": len(tstart1), "tour_progress": len(tprog1)})

    # rebuild the aggregate view from the journal, through v2's own code path
    rebuilt_path = os.path.join(HERE, s1["out_dir"], "surrogate_rebuilt.json")
    agg = v2.rebuild_results(s1["journal_path"], rebuilt_path)
    s1["rebuilt_results_path"] = os.path.relpath(rebuilt_path, HERE)
    s1["rebuilt_statuses_present"] = agg["statuses_present"]
    c2.check("v2's own rebuild-results path turns the post-kill journal into a "
             "parseable aggregate carrying both STARTED and KILLED_PARTIAL",
             "STARTED" in agg["statuses_present"]
             and "KILLED_PARTIAL" in agg["statuses_present"],
             agg["statuses_present"])

    # S2 -- the instrument's OWN cell timeout (SIGALRM), for the
    # "stdout_tail retained FOR A TIMED-OUT CELL" clause of condition (i).
    s2 = _launch_and_signal(
        "D1_D2_surrogate_S2_timeout_failed_infrastructure",
        ["--prefix", "surrogate", "--d", str(TOY_D), "--beta", str(TOY_BETA),
         "--mpfr-bits", "53", "--heartbeat-seconds", "0.25",
         "--simulate-slow-tour-seconds", "0.4",
         "--cell-timeout-seconds", "1.5"],
        kill_after=0.0, sig=None)
    s2["surrogate"] = True
    s2["surrogate_kind"] = (
        "DECLARED SLEEP SURROGATE: a tiny d=64 lattice with an explicit 0.4 s "
        "inter-tour sleep so the instrument's own 1.5 s cell timeout trips "
        "deterministically. The sleep is a declared surrogate knob of the "
        "instrument and every record it produces carries surrogate: true.")
    s2["why_adequate"] = (
        "It exercises the TIMED-OUT cell path, which condition (i) names "
        "separately from the killed path ('stdout_tail retained for a "
        "TIMED-OUT cell'). It does NOT show timeout behaviour at d=512.")
    recs2, bad2 = read_jsonl(s2["journal_path"])
    s2["records"] = recs2
    s2["unparseable_lines"] = bad2
    timed2 = [r for r in recs2 if r.get("status") == "TIMED_OUT_PARTIAL"]
    s2["counts"] = {
        "started_stubs": len([r for r in recs2 if r.get("status") == "STARTED"]),
        "timed_out_partial": len(timed2),
        "tour_progress": len([r for r in recs2
                              if r.get("record_kind") == "tour_progress"]),
    }
    c2.check("D2/D4: the instrument's own cell timeout flushed a "
             "TIMED_OUT_PARTIAL record", len(timed2) == 1, len(timed2))
    c2.check("D2/D4: the TIMED-OUT record retains a non-empty stdout_tail",
             bool(timed2) and len(timed2[-1].get("stdout_tail") or []) > 0,
             len(timed2[-1].get("stdout_tail") or []) if timed2 else 0)
    c2.check("D2: the timed-out record's surrogate flag is set",
             bool(timed2) and timed2[-1].get("surrogate") is True,
             timed2[-1].get("surrogate") if timed2 else None)
    c2.check("D2: no unparseable line in the timed-out journal",
             not bad2, len(bad2))

    # combined stdout evidence log
    stdout_log = os.path.join(EVID, "D1_D2_sigterm_surrogate_stdout.log")
    with open(stdout_log, "w") as fh:
        for s in (s1, s2):
            fh.write(f"=== {s['tag']} ===\n")
            fh.write(f"command: {s['command']}\n")
            fh.write(f"returncode: {s['returncode']}  "
                     f"signal_sent: {s['signal_sent_name']}\n")
            fh.write("--- captured stdout (verbatim) ---\n")
            with open(os.path.join(HERE, s["stdout_path"]),
                      errors="replace") as src:
                fh.write(src.read())
            fh.write("\n")

    out = {
        "test": "D1_D2_started_stub_and_signal_flush",
        "condition_v_label": "failed_infrastructure",
        "condition_v_note": (
            "DEC-20260815-3e8e9c condition (v) VERBATIM: 'PRESERVE EVERY "
            "ARTIFACT OF EVERY EXECUTION, INCLUDING AN INFRASTRUCTURE-KILLED "
            "ONE, UNDER A failed_infrastructure LABEL.' Both surrogate "
            "executions below were deliberately terminated. Every artifact of "
            "both is preserved under artifacts/*_failed_infrastructure/ and "
            "nothing was deleted; the literal label is carried in the "
            "directory name AND in each flushed record's "
            "failed_infrastructure field."),
        "S1_real_sigterm": s1,
        "S2_instrument_cell_timeout": s2,
        "D1_checks": c1.items,
        "D2_checks": c2.items,
        "D1_status": c1.status(),
        "D2_status": c2.status(),
        "what_this_cannot_show": (
            SURROGATE_LIMITS + " Specifically for the handler: CPython runs a "
            "Python signal handler only at an interpreter check in the main "
            "thread. S1 shows the handler firing when SIGTERM arrives during "
            "fplll work at d=64, where a tour is milliseconds and the C call "
            "returns almost immediately. IT DOES NOT SHOW the handler firing "
            "promptly at d=512, where a single tour may be hours: there the "
            "flush is deferred until the C call returns, and a SIGKILL "
            "following the SIGTERM, or a hard container stop, would lose it. "
            "What survives that case is only what is already on disk -- the "
            "STARTED stub, every completed tour, and the tour_start record "
            "naming the in-flight tour."),
    }
    return out, c1, c2


# ==================================================================== main
def main():
    log(f"interpreter: {PY}")
    log(f"instrument : {V2_PATH}")
    board = {
        "task": "TASK-20260826-602395",
        "batch": "BATCH-762807",
        "goal": "GOAL-MLKEM-005",
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "interpreter": PY,
        "suite_command": SUITE_COMMAND,
        "instrument_under_test": "rt_ctrl_1_matched_pair_v2.py",
        "claim_ceiling": "instrument_repair",
        "claim_tier": "toy",
        "not_evidence_about": (
            "Nothing on this board is evidence about ML-KEM at any FIPS 203 "
            "parameter set, about lattice hardness, or about the obstruction "
            "RT-CTRL-1 targets. A PASSING ACCEPTANCE TEST SAYS ONLY THAT THE "
            "INSTRUMENT NOW RECORDS WHAT IT ALWAYS SHOULD HAVE RECORDED."),
        "no_d512_and_no_100bit_cell_executed": True,
        "scale_of_every_test": "d=64, beta=20, mpfr_bits=53 (toy surrogate)",
        "defects": {},
    }

    def entry(did, status, evidence_rel, command, asserted, extra=None):
        e = {"status": status, "evidence_path": evidence_rel,
             "command": command, "asserted": asserted}
        if extra:
            e.update(extra)
        board["defects"][did] = e

    # --- D6 (no fpylll) ---
    try:
        d6, c6 = test_D6()
    except Exception as exc:
        import traceback
        d6 = {"test": "D6_root_hermite_closed_form", "status": "NOT_REACHED",
              "reason": f"{type(exc).__name__}: {exc}",
              "traceback": traceback.format_exc()}
    with open(os.path.join(EVID, "D6_root_hermite.json"), "w") as fh:
        json.dump(d6, fh, indent=2)
    entry("D6", d6["status"], "evidence/D6_root_hermite.json", SUITE_COMMAND,
          "That (b0/q**0.5)**(1/d) divided by the predecessor's "
          "b0**(1/d)/(q**0.5)**(1/1) equals q**(1/2 - 1/(2d)) for every tested "
          "b0 and d, recomputing 57.242 at d=512 and 54.8457 at d=80 and "
          "checking the committed d=80 triple for internal consistency.")

    # --- tiny cell -> D3, D4, D5 ---
    tiny_err = None
    try:
        rec, journal_path, env_path, env, tiny_dir = run_tiny_cell()
        if rec.get("status") != "COMPLETED":
            tiny_err = f"tiny cell status={rec.get('status')} " \
                       f"error={rec.get('error')}"
    except Exception as exc:
        import traceback
        tiny_err = f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}"
        rec = journal_path = env_path = env = None

    if rec is not None and rec.get("status") == "COMPLETED":
        d3, _ = test_D3(rec, journal_path)
        d4, _ = test_D4(rec, env_path, env)
        d5, _ = test_D5(rec, journal_path)
        shutil.copyfile(env_path,
                        os.path.join(EVID, "D3_D4_environment.json"))
    else:
        nr = {"status": "NOT_REACHED",
              "reason": "the tiny acceptance cell did not complete",
              "what_was_tried": (
                  f"v2.run_cell(d={TOY_D}, beta={TOY_BETA}, "
                  f"mpfr_bits={TOY_MPFR}) through the instrument's own path"),
              "error": tiny_err,
              "infrastructure_note": (
                  "AGENTS.md rule 3: a failure here is infrastructure signal "
                  "and is never evidence that the fix is impossible.")}
        d3 = dict(nr, test="D3_per_tour_progress")
        d4 = dict(nr, test="D4_resource_record")
        d5 = dict(nr, test="D5_tour_count")
        with open(os.path.join(EVID, "D3_D4_environment.json"), "w") as fh:
            json.dump(dict(nr, test="D3_D4_environment"), fh, indent=2)

    tiny_payload = {"D3": d3, "D4": d4,
                    "tiny_cell_final_record": rec if rec else None,
                    "tiny_cell_journal": (
                        os.path.relpath(journal_path, HERE)
                        if journal_path else None)}
    with open(os.path.join(EVID, "D3_D4_tiny_cell.json"), "w") as fh:
        json.dump(tiny_payload, fh, indent=2)
    with open(os.path.join(EVID, "D5_tour_count.json"), "w") as fh:
        json.dump(d5, fh, indent=2)

    entry("D3", d3["status"], "evidence/D3_D4_tiny_cell.json", SUITE_COMMAND,
          "That the results journal the instrument wrote carries a tours table "
          "with MORE THAN ONE row, each row bearing tour index, wall clock and "
          "a basis-quality readout, and that per-tour progress also reached "
          "stdout.")
    entry("D4", d4["status"], "evidence/D3_D4_tiny_cell.json", SUITE_COMMAND,
          "That the machine-readable record carries a non-zero cpu_times() "
          "user time from a psutil handle, a non-zero peak RSS with a "
          "getrusage cross-check, a non-empty stdout_tail, and that "
          "environment.json carries os.getloadavg().",
          {"environment_evidence_path": "evidence/D3_D4_environment.json"})
    entry("D5", d5["status"], "evidence/D5_tour_count.json", SUITE_COMMAND,
          "That the recorded tour count is a non-None int >= 1 obtained by the "
          "declared driving-loop mechanism, AND that it equals upstream "
          "BKZReduction.__call__'s own trace-child tour count on an "
          "identically seeded d=64 basis with an identical final b0.")

    # --- D1/D2 ---
    try:
        d12, c1, c2 = test_D1_D2()
        s1_status, s2_status = d12["D1_status"], d12["D2_status"]
    except Exception as exc:
        import traceback
        d12 = {"test": "D1_D2_started_stub_and_signal_flush",
               "status": "NOT_REACHED",
               "reason": f"{type(exc).__name__}: {exc}",
               "traceback": traceback.format_exc(),
               "infrastructure_note": (
                   "AGENTS.md rule 3: infrastructure signal, never evidence "
                   "that the fix is impossible.")}
        s1_status = s2_status = "NOT_REACHED"
    with open(os.path.join(EVID, "D1_D2_sigterm_surrogate.json"), "w") as fh:
        json.dump(d12, fh, indent=2)
    log_path = os.path.join(EVID, "D1_D2_sigterm_surrogate_stdout.log")
    if not os.path.exists(log_path):
        with open(log_path, "w") as fh:
            fh.write("NOT_REACHED: the D1/D2 surrogate did not run to the "
                     "point of producing a stdout capture.\n"
                     f"reason: {d12.get('reason')}\n")
    entry("D1", s1_status, "evidence/D1_D2_sigterm_surrogate.json",
          SUITE_COMMAND,
          "That a per-cell STARTED stub written BEFORE the cell began is on "
          "disk after a REAL SIGTERM, for a cell that started and never "
          "finished -- the exact record BATCH-f9780d's 100-bit cell did not "
          "leave.",
          {"stdout_evidence_path":
           "evidence/D1_D2_sigterm_surrogate_stdout.log"})
    entry("D2", s2_status, "evidence/D1_D2_sigterm_surrogate.json",
          SUITE_COMMAND,
          "That a REAL SIGTERM to the instrument subprocess left exactly one "
          "signal-handler-flushed KILLED_PARTIAL record carrying tours-so-far, "
          "elapsed time, stdout_tail and the failed_infrastructure label, in a "
          "journal every line of which still parses; and that the "
          "instrument's own cell timeout leaves a TIMED_OUT_PARTIAL record "
          "with a retained stdout_tail.",
          {"stdout_evidence_path":
           "evidence/D1_D2_sigterm_surrogate_stdout.log"})

    board["summary"] = {d: board["defects"][d]["status"]
                        for d in ("D1", "D2", "D3", "D4", "D5", "D6")}
    board["a_fail_is_a_legitimate_outcome"] = (
        "Any FAIL or NOT_REACHED above is reported verbatim. No assertion in "
        "acceptance_tests.py was weakened and no threshold was moved after "
        "seeing a result.")
    with open(BOARD, "w") as fh:
        json.dump(board, fh, indent=2)
    log("BOARD: " + json.dumps(board["summary"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
