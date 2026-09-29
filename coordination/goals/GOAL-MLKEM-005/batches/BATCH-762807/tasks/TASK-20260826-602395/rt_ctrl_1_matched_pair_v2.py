#!/usr/bin/env python3
"""RT-CTRL-1 MATCHED-PAIR INSTRUMENT, v2 -- successor of the pinned runner.

TASK-20260826-602395 / BATCH-762807 / GOAL-MLKEM-005.

WHAT THIS FILE IS
-----------------
A NEW file. It does not edit and does not import the pinned predecessor

  coordination/goals/GOAL-MLKEM-005/batches/BATCH-f9780d/tasks/
      TASK-20260824-b3e9da/rt_ctrl_1_matched_pair.py
  sha256 bc0524ee432a2327bc4a5cfff5d8f5d79b590d37b2f38ea428c78af5abb25035

which is IMMUTABLE (bound by the completed snapshot receipt of
TASK-20260824-c7248f) and was verified unchanged at that sha256 by this task
before this file was written.

The construction, seed formula, precision-before-GSO ordering, ROW_EXPO-free
mpfr GSO and content-bound strategies source are carried over from that
predecessor and from

  BATCH-0d5018/tasks/TASK-20260815-f14d3c/
      stage0_d512_beta5570_precision_bisection_and_reattempt.py
  sha256 58a1fdc21f45730789feeff69c6a6fd7c24bf4938be15d6e878afd246d0de485

(also verified at that sha256 by this task). DEC-20260815-3e8e9c carries the
construction shape forward "without re-litigation"; nothing here re-litigates
it.

WHAT IT REPAIRS (D1..D6 of the task card)
-----------------------------------------
D1  A per-cell STARTED stub is written and fsync'd to the results journal
    BEFORE any lattice work of that cell begins.
D2  SIGTERM/SIGINT (and, for a capped cell, SIGALRM) handlers flush a
    KILLED_PARTIAL / TIMED_OUT_PARTIAL record. See SIGNAL SAFETY below for
    the mechanism AND ITS LIMITS.
D3  Per-tour progress -- tour index, wall clock, cpu time, peak RSS, and the
    cheap basis-quality readouts available at that point -- appended and
    fsync'd to the results journal AND printed to stdout, EVERY TOUR. This
    requires driving the tour loop here rather than calling
    BKZReduction.__call__; the loop below is a line-for-line transcription of
    upstream's (see TOUR LOOP PROVENANCE) and the acceptance suite ships an
    equivalence control against upstream __call__ at d=64.
D4  A resource-sampler thread holds a psutil handle and records
    .cpu_times() and .memory_info().rss (peak by polling), cross-checked
    against resource.getrusage().ru_maxrss; os.getloadavg() goes into
    environment.json; a stdout tail ring buffer is carried in every flushed
    record, including the killed/timed-out ones.
D5  The tour count is the number of completed iterations of the transcribed
    upstream loop -- i.e. the number of self.tour(...) calls that returned,
    which is exactly the set of ("tour", i) contexts upstream opens. The
    predecessor's `getattr(bkz, "tours", None)` is never used; fpylll assigns
    no such attribute. See TOUR COUNT DEFINITION below for why `bkz.trace`
    alone is NOT sufficient.
D6  root_hermite_factor = (b0 / q**0.5) ** (1/d).  The predecessor's
    b0**(1/d) / (q**0.5)**(1/1) is retained ONLY under the explicitly
    labelled key `root_hermite_factor_legacy_defective_formula`, for
    comparison, and is never the reported quantity.

TOUR COUNT DEFINITION (D5), AND A FINDING AGAINST THE PRESCRIPTION
-----------------------------------------------------------------
DEC-20260824-5e222e prescribes taking `tours` from `bkz.trace`. Taken
literally that is NECESSARY BUT NOT SUFFICIENT, and taken naively it
reproduces the defect it repairs. In the installed fpylll 0.6.4,
`BKZReduction.__call__(self, params, min_row=0, max_row=-1, tracer=False)`
defaults `tracer` to False, and ends with

    tracer.exit()
    try:
        self.trace = tracer.trace
    except AttributeError:
        self.trace = None

so after a default `bkz(par)` the attribute EXISTS and is None -- an
always-None read, exactly like `getattr(bkz, "tours", None)`. Upstream's own
docstring states it: `bkz(BKZ.EasyParam(10), tracer=False); bkz.trace is None`
-> True. This instrument therefore does not read `bkz.trace` on the driving
path at all. It counts tours in the driving loop, and SAYS SO:

    tours = the number of completed iterations of the transcribed upstream
            while-loop, incremented after each self.tour(...) returns.

That count is available AFTER EVERY TOUR, which a trace-child count is not:
`bkz.trace` only exists once the whole call has returned, which is precisely
the case BATCH-f9780d did not get. The equivalence of the two counts is an
acceptance control, not an assumption.

TOUR LOOP PROVENANCE
--------------------
Transcribed from fpylll/algorithms/bkz.py `BKZReduction.__call__` in the
installed fpylll 0.6.4, preserving the pre-loop LLL and all four break tests
in order. Dropping the pre-loop LLL or the auto-abort test would make this a
DIFFERENT ALGORITHM rather than an instrumented one.

SIGNAL SAFETY (D2) -- MECHANISM AND LIMITS, CLAIMED NO HIGHER THAN IT IS
------------------------------------------------------------------------
Mechanism:
  * The results journal is a JSON-Lines file opened ONCE with
    os.open(..., O_WRONLY|O_CREAT|O_APPEND) and kept in a module-level int.
  * A complete KILLED_PARTIAL record is PRE-SERIALISED to a bytes object and
    rebound to a module-level name after every tour and every resource
    heartbeat. Rebinding a module-level name to a new bytes object is atomic
    in CPython, so a handler reads either the old or the new payload, never a
    torn one.
  * The handler performs exactly: one os.write(fd, payload), one
    os.write(1, short_payload), one os.fsync, then os._exit(). It allocates
    nothing, opens nothing, imports nothing, calls no json function and does
    not touch buffered Python I/O. os._exit is used deliberately so that no
    atexit hook and no buffered-stream flush runs from signal context (a
    flush could deadlock if the signal landed inside a buffered write).
  * O_APPEND plus a single write() syscall means the record is appended
    whole, after whatever bytes are already there; it cannot interleave with
    a partially written earlier line.

Limits, stated because they are real:
  1. THE PAYLOAD IS STALE BY UP TO ONE HEARTBEAT INTERVAL. Elapsed time,
     cpu time and peak RSS in the flushed record are as of the last refresh.
     Every flushed record carries `staleness_bound_seconds` so a reader can
     see the bound rather than infer it.
  2. CPython runs a Python-level signal handler only at an interpreter check
     in the main thread. IF SIGTERM ARRIVES WHILE THE PROCESS IS INSIDE A
     LONG fplll C CALL, THE HANDLER DOES NOT RUN UNTIL THAT CALL RETURNS TO
     THE INTERPRETER. If the killer follows with SIGKILL before then, or the
     C call never returns, the handler NEVER RUNS. What survives that case is
     what is already on disk: the STARTED stub, every completed tour, every
     heartbeat, and the tour-start record naming the tour that was in flight
     and when it began. THE RESIDUAL LOSS WINDOW IS THEREFORE THE PROGRESS
     MADE INSIDE THE CURRENTLY RUNNING TOUR, and at d=512 a single tour may
     be hours. This is named here rather than left for a reviewer to find.
  3. SIGKILL runs nothing. Same residual as (2), by construction.
  4. os.write to a regular file reaches the kernel page cache, so a killed
     PROCESS cannot lose it; a killed MACHINE could. fsync is issued after
     the stub, after every tour and in the handler, which narrows that to the
     handler's own write.
  5. The aggregate `<prefix>_results.json` view is NOT written from signal
     context (json.dump is not signal-safe). After a kill it holds the last
     safe-point state; `rebuild-results` regenerates it from the journal,
     which is the durable primary.

SCALE GUARD
-----------
This task is ZERO-LATTICE-COMPUTE. `run` REFUSES any d greater than
--max-toy-d (default 128) unless --scale-run-authorisation is given with a
non-empty reason, which is then recorded. No d=512 execution and no
mpfr_bits=100 execution on a d=512 basis was performed by this task.

CLAIM CEILING
-------------
instrument_repair. Nothing produced by this file or by its acceptance suite
is evidence about ML-KEM at any FIPS 203 parameter set, about lattice
hardness, or about the obstruction RT-CTRL-1 targets. Claim tier: toy.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import resource
import signal
import subprocess
import sys
import threading
import time
from collections import deque
from time import process_time

# --- construction constants, carried over verbatim from the pinned lineage ---
SEED_ROOT = 715923
Q = 3329
D_DEFAULT = 512
BETA_DEFAULT = 55

HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.abspath(
    os.path.join(HERE, "..", "..", "..", "..", "..", "..", "..")
)
DEFAULT_STRATEGIES = os.path.join(
    _REPO_ROOT,
    "coordination/goals/GOAL-MLKEM-005/batches/BATCH-f9780d/tasks/"
    "TASK-20260824-b3e9da/inputs/fplll_strategies_default.json",
)
PINNED_PREDECESSOR_SHA256 = (
    "bc0524ee432a2327bc4a5cfff5d8f5d79b590d37b2f38ea428c78af5abb25035"
)
INSTRUMENT_VERSION = "rt_ctrl_1_matched_pair_v2 / TASK-20260826-602395"

STDOUT_TAIL_LINES = 24

# ------------------------------------------------------------------ D2 state
# Module-level, so the signal handler touches only pre-existing bindings.
_H_FD = -1              # journal fd, opened once
# One pre-serialised partial record PER SIGNAL, so the flushed status is the
# true one (KILLED_PARTIAL vs TIMED_OUT_PARTIAL) without any work in the
# handler. The dict is REBUILT and REBOUND wholesale on each refresh; rebinding
# a module-level name is atomic in CPython, so the handler reads either the old
# dict or the new one, never a half-updated one.
_H_PAYLOAD: dict = {}
_H_STDOUT = b"[v2] signal received; pre-serialised partial record flushed\n"
_H_ARMED = False


def _signal_flush_and_die(signum, frame):  # noqa: ARG001 - signal API
    """Async-signal-context flush. Allocates nothing; see SIGNAL SAFETY."""
    try:
        os.write(_H_FD, _H_PAYLOAD[signum])
    except Exception:
        pass
    try:
        os.fsync(_H_FD)
    except Exception:
        pass
    try:
        os.write(1, _H_STDOUT)
    except Exception:
        pass
    os._exit(128 + signum)


# ------------------------------------------------------------------ helpers
def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def root_hermite_factor(b0: float, q: int, d: int) -> float:
    """D6, CORRECTED. delta_0 = (b0 / vol^(1/d))^(1/d), and for the q-ary
    construction with k = d//2 the lattice volume is q^(d/2), so
    vol^(1/d) = q^(1/2). The 1/d exponent applies to the RATIO."""
    return (float(b0) / (q ** 0.5)) ** (1.0 / d)


def root_hermite_factor_legacy_defective(b0: float, q: int, d: int) -> float:
    """The pinned predecessor's line 78, VERBATIM, for comparison ONLY.
    `b0**(1/d) / (q**0.5)**(1/1)`. The trailing **(1/1) is a no-op and the
    1/d exponent is applied to b0 alone. Never reported as the answer."""
    return float(b0) ** (1.0 / d) / (q ** 0.5) ** (1.0 / 1)


def root_hermite_distortion_closed_form(q: int, d: int) -> float:
    """corrected / defective, INDEPENDENT OF b0:
        (b0/q^(1/2))^(1/d)  /  ( b0^(1/d) / q^(1/2) )
      = q^(-1/(2d)) * q^(1/2)
      = q^(1/2 - 1/(2d))
    """
    return q ** (0.5 - 1.0 / (2.0 * d))


class Journal:
    """Append-only JSON-Lines results journal. The durable primary record."""

    def __init__(self, path: str):
        self.path = path
        self.fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)

    def write(self, record: dict, fsync: bool = True) -> bytes:
        data = (json.dumps(record, sort_keys=True) + "\n").encode("utf-8")
        os.write(self.fd, data)
        if fsync:
            try:
                os.fsync(self.fd)
            except OSError:
                pass
        return data


class StdoutTee:
    """stdout with a ring buffer, so a killed cell still carries a tail (D4)."""

    def __init__(self, log_path: str | None):
        self.ring: deque[str] = deque(maxlen=STDOUT_TAIL_LINES)
        self.fd = None
        if log_path:
            self.fd = os.open(log_path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)

    def emit(self, line: str) -> None:
        stamped = f"[{time.strftime('%H:%M:%S')}] {line}"
        self.ring.append(stamped)
        sys.stdout.write(stamped + "\n")
        sys.stdout.flush()
        if self.fd is not None:
            try:
                os.write(self.fd, (stamped + "\n").encode("utf-8"))
            except OSError:
                pass

    def tail(self) -> list[str]:
        return list(self.ring)


class ResourceSampler(threading.Thread):
    """D4. Holds the psutil handle; polls rss for a true peak and cpu_times().

    NOTE, stated rather than implied: the pinned predecessor has NO polling
    loop at all (119 lines, no psutil import). DEC-20260815-3e8e9c(i) speaks of
    "the psutil handle the polling loop already holds"; this loop is BUILT
    here, not extended.
    """

    def __init__(self, interval: float, on_sample):
        super().__init__(daemon=True)
        self.interval = interval
        self.on_sample = on_sample
        self.stop_event = threading.Event()
        self.peak_rss_bytes = 0
        self.last_cpu_times = None
        self.samples = 0
        self.psutil_available = False
        self.psutil_error = None
        self._proc = None
        try:
            import psutil  # noqa: PLC0415

            self._proc = psutil.Process(os.getpid())
            self.psutil_available = True
            self.psutil_version = psutil.__version__
        except Exception as exc:  # pragma: no cover - infrastructure branch
            self.psutil_error = f"{type(exc).__name__}: {exc}"
            self.psutil_version = None

    def sample(self) -> dict:
        snap = {"sampler_samples": self.samples}
        if self._proc is not None:
            try:
                rss = self._proc.memory_info().rss
                self.peak_rss_bytes = max(self.peak_rss_bytes, rss)
                ct = self._proc.cpu_times()
                self.last_cpu_times = {
                    "user": ct.user,
                    "system": ct.system,
                    "children_user": ct.children_user,
                    "children_system": ct.children_system,
                }
                snap["rss_bytes"] = rss
            except Exception as exc:  # pragma: no cover
                snap["psutil_sample_error"] = f"{type(exc).__name__}: {exc}"
        snap["peak_rss_bytes"] = self.peak_rss_bytes
        snap["peak_rss_mb"] = round(self.peak_rss_bytes / (1 << 20), 3)
        snap["cpu_times"] = self.last_cpu_times
        snap["cpu_times_source"] = (
            "psutil.Process(os.getpid()).cpu_times()"
            if self.psutil_available
            else "UNAVAILABLE: " + str(self.psutil_error)
        )
        ru = resource.getrusage(resource.RUSAGE_SELF)
        snap["ru_maxrss_kb"] = ru.ru_maxrss
        snap["ru_maxrss_mb"] = round(ru.ru_maxrss / 1024.0, 3)
        snap["rusage_cpu_seconds"] = {"user": ru.ru_utime, "system": ru.ru_stime}
        snap["process_time_seconds"] = process_time()
        return snap

    def run(self) -> None:
        while not self.stop_event.wait(self.interval):
            self.samples += 1
            try:
                self.on_sample(self.sample())
            except Exception:  # pragma: no cover
                pass


def environment_record(strategies_path: str | None) -> dict:
    """D4: load average goes here. Shape follows the committed precedent
    BATCH-0d5018/tasks/TASK-20260815-f14d3c/environment.json, plus loadavg,
    psutil and the interpreter path (recorded BY CONTENT, not only by path --
    the predecessor's whole failure mode was an environment difference
    recorded by path)."""
    env = {
        "instrument": INSTRUMENT_VERSION,
        "recorded_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "python_executable": sys.executable,
        "python_version": sys.version,
        "platform": platform.platform(),
        "nproc_os_cpu_count": os.cpu_count(),
        "load_average_1_5_15": list(os.getloadavg()),
        "load_average_source": "os.getloadavg()",
    }
    for mod in ("fpylll", "numpy", "psutil"):
        try:
            m = __import__(mod)
            env[f"{mod}_version"] = getattr(m, "__version__", "unknown")
            env[f"{mod}_file"] = getattr(m, "__file__", None)
        except Exception as exc:
            env[f"{mod}_version"] = None
            env[f"{mod}_import_error"] = f"{type(exc).__name__}: {exc}"
    try:
        with open("/proc/meminfo") as fh:
            for line in fh:
                if line.startswith("MemTotal"):
                    env["mem_total"] = line.strip()
                    break
    except OSError:
        env["mem_total"] = None
    if strategies_path:
        env["strategies_file"] = strategies_path
        try:
            env["strategies_sha256"] = sha256_file(strategies_path)
        except OSError as exc:
            env["strategies_sha256"] = None
            env["strategies_error"] = f"{type(exc).__name__}: {exc}"
    try:
        env["git_commit"] = subprocess.run(
            ["git", "-C", _REPO_ROOT, "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=20, check=False,
        ).stdout.strip() or None
    except Exception as exc:
        env["git_commit"] = None
        env["git_error"] = f"{type(exc).__name__}: {exc}"
    return env


# ------------------------------------------------------------------ the cell
def run_cell(
    d: int,
    beta: int,
    mpfr_bits: int,
    role: str,
    journal: Journal,
    tee: StdoutTee,
    strategies: str | None = None,
    seed_index: int = 0,
    heartbeat_seconds: float = 1.0,
    simulate_slow_tour_seconds: float = 0.0,
    cell_timeout_seconds: float = 0.0,
    arm_signals: bool = True,
) -> dict:
    """Run ONE matched-pair cell with D1..D6 repaired. Returns the final record.

    `simulate_slow_tour_seconds` > 0 makes this a DECLARED SURROGATE: it adds a
    time.sleep between tours and every record carries surrogate: true with the
    kind. It is never used for a measurement.
    """
    global _H_FD, _H_PAYLOAD, _H_ARMED

    import numpy as np  # noqa: PLC0415
    from fpylll import GSO, LLL, BKZ, FPLLL, IntegerMatrix  # noqa: PLC0415
    from fpylll.algorithms.bkz2 import BKZReduction  # noqa: PLC0415
    from fpylll.tools.bkz_stats import dummy_tracer  # noqa: PLC0415

    surrogate = simulate_slow_tour_seconds > 0.0
    identity = {
        "d": d,
        "beta": beta,
        "mpfr_bits": mpfr_bits,
        "role": role,
        "construction": "corrected_mpfr_no_row_expo",
        "instrument": INSTRUMENT_VERSION,
        "surrogate": surrogate,
        "surrogate_kind": (
            "tiny_lattice_with_declared_inter_tour_sleep" if surrogate else None
        ),
        "simulate_slow_tour_seconds": simulate_slow_tour_seconds,
    }

    sampler = ResourceSampler(heartbeat_seconds, lambda s: None)
    state = {
        "tours_completed": 0,
        "tour_in_flight": None,
        "tour_in_flight_started_wall": None,
        "tours_table": [],
    }
    t_start_wall = time.time()
    t_start_cpu = process_time()

    _SIGNAL_STATUS = {
        signal.SIGTERM: ("KILLED_PARTIAL", "SIGTERM"),
        signal.SIGINT: ("KILLED_PARTIAL", "SIGINT"),
        signal.SIGALRM: ("TIMED_OUT_PARTIAL", "SIGALRM (cell timeout)"),
    }

    def refresh_partial_payload() -> None:
        """Rebuild the pre-serialised signal payloads (D2). Atomic rebinding."""
        global _H_PAYLOAD
        snap = sampler.sample()
        rec = dict(identity)
        rec.update(
            {
                "record_kind": "cell_partial_flushed_from_signal_handler",
                "failed_infrastructure": True,
                "tours": state["tours_completed"],
                "tours_completed": state["tours_completed"],
                "tour_in_flight_index": state["tour_in_flight"],
                "tour_in_flight_started_wall_utc": state[
                    "tour_in_flight_started_wall"
                ],
                "tour_in_flight_elapsed_seconds_at_refresh": (
                    None
                    if state["tour_in_flight_started_wall"] is None
                    else round(time.time() - state["tour_in_flight_started_wall"], 6)
                ),
                "elapsed_seconds_at_refresh": round(time.time() - t_start_wall, 6),
                "cpu_seconds_at_refresh": round(process_time() - t_start_cpu, 6),
                "payload_refreshed_at_utc": time.strftime(
                    "%Y-%m-%dT%H:%M:%SZ", time.gmtime()
                ),
                "payload_refresh_points": [
                    "cell start", "each tour start (before entering fplll)",
                    "each tour end", "each heartbeat (SUBJECT TO THE GIL)",
                ],
                "staleness_bound_seconds_between_tours": heartbeat_seconds,
                "staleness_bound_seconds": None,
                "staleness_note": (
                    "MEASURED, NOT ASSUMED. Every figure in this record is as of "
                    "the last refresh. Between tours the bound is "
                    "staleness_bound_seconds_between_tours. INSIDE an fplll tour "
                    "it is NOT: fplll's C calls hold the GIL, so the sampler "
                    "thread cannot run and no heartbeat refresh occurs until the "
                    "tour returns. The true bound is therefore "
                    "heartbeat_seconds PLUS the duration of the tour that was in "
                    "flight, which at d=512 may be hours. `staleness_bound_"
                    "seconds` is left null rather than stated as a number this "
                    "mechanism does not support. What is NOT stale is "
                    "tour_in_flight_index and tour_in_flight_started_wall_utc, "
                    "which are refreshed before the tour is entered."
                ),
                "tours_table": state["tours_table"],
                "stdout_tail": tee.tail(),
                "resources": snap,
            }
        )
        built = {}
        for signum, (status, name) in _SIGNAL_STATUS.items():
            r = dict(rec)
            r["status"] = status
            r["signal"] = name
            r["signal_number"] = int(signum)
            built[signum] = (json.dumps(r, sort_keys=True) + "\n").encode("utf-8")
        _H_PAYLOAD = built

    # ---------------- D1: STARTED stub, written and fsync'd BEFORE any work
    started = dict(identity)
    started.update(
        {
            "record_kind": "cell_started_stub",
            "status": "STARTED",
            "start_wall_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "start_wall_epoch": t_start_wall,
            "pid": os.getpid(),
            "python_executable": sys.executable,
            "why_this_exists": (
                "D1: the predecessor wrote its results JSON only after the cell "
                "returned, so a SIGTERM'd cell contributed nothing at all. This "
                "stub is on disk and fsync'd before the cell begins."
            ),
        }
    )
    journal.write(started)
    tee.emit(
        f"STARTED cell d={d} beta={beta} mpfr_bits={mpfr_bits} role={role!r} "
        f"surrogate={surrogate}"
    )

    # ---------------- D2: arm the handlers against the already-open journal
    _H_FD = journal.fd
    sampler.start()
    refresh_partial_payload()
    if arm_signals:
        signal.signal(signal.SIGTERM, _signal_flush_and_die)
        signal.signal(signal.SIGINT, _signal_flush_and_die)
        _H_ARMED = True
        if cell_timeout_seconds > 0:
            signal.signal(signal.SIGALRM, _signal_flush_and_die)
            signal.setitimer(signal.ITIMER_REAL, cell_timeout_seconds)
            tee.emit(f"cell timeout armed at {cell_timeout_seconds}s (SIGALRM)")
        tee.emit("SIGTERM/SIGINT handlers armed against the open journal fd")

    # keep the payload fresh from the heartbeat too
    sampler.on_sample = lambda s: refresh_partial_payload()

    result = dict(identity)
    result["record_kind"] = "cell_final"
    result["start_wall_utc"] = started["start_wall_utc"]
    try:
        seed = int(
            np.random.default_rng([SEED_ROOT, 0, d, beta, seed_index, 0]).integers(
                0, 2 ** 31 - 1
            )
        )
        FPLLL.set_random_seed(seed)
        result["seed_used"] = seed
        result["seed_formula"] = (
            "np.random.default_rng([SEED_ROOT, 0, d, beta, seed_index, 0])"
            ".integers(0, 2**31-1); SEED_ROOT=715923 (verbatim from the lineage)"
        )
        if strategies:
            result["strategies_file_used"] = strategies
            result["strategies_sha256"] = sha256_file(strategies)

        A = IntegerMatrix.random(d, "qary", k=d // 2, q=Q)
        t0 = time.time()
        LLL.reduction(A)
        result["outer_lll_reduction_elapsed_seconds"] = time.time() - t0

        FPLLL.set_precision(mpfr_bits)        # BEFORE GSO.Mat construction
        M = GSO.Mat(A, float_type="mpfr")     # explicitly NO flags=GSO.ROW_EXPO
        M.update_gso()
        result["gso_float_type_used"] = M.float_type
        L = LLL.Reduction(M, flags=LLL.DEFAULT)

        if strategies:
            par = BKZ.Param(block_size=beta, strategies=strategies,
                            flags=BKZ.AUTO_ABORT)
        else:
            par = BKZ.Param(block_size=beta, flags=BKZ.AUTO_ABORT)
        bkz = BKZReduction(L)

        # ---------------------------------------------------------------
        # TRANSCRIBED upstream loop (fpylll/algorithms/bkz.py __call__),
        # with per-tour flush added and NOTHING removed.
        # ---------------------------------------------------------------
        tracer = dummy_tracer
        if par.flags & BKZ.AUTO_ABORT:
            auto_abort = BKZ.AutoAbort(bkz.M, bkz.M.d)
        cputime_start = process_time()

        t_lll = time.time()
        bkz.lll_obj()                      # <-- the pre-loop LLL. Not dropped.
        result["pre_loop_lll_elapsed_seconds"] = time.time() - t_lll

        i = 0
        break_reason = None
        t_bkz = time.time()
        while True:
            state["tour_in_flight"] = i
            state["tour_in_flight_started_wall"] = time.time()
            journal.write(
                {
                    **identity,
                    "record_kind": "tour_start",
                    "tour_index": i,
                    "wall_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "elapsed_seconds": round(time.time() - t_start_wall, 6),
                    "why_this_exists": (
                        "So that a cell killed INSIDE a tour still records which "
                        "tour was in flight and when it began -- the residual "
                        "loss window named in SIGNAL SAFETY limit (2)."
                    ),
                }
            )
            # Refresh BEFORE entering the C call: fplll holds the GIL, so this
            # is the last moment the payload can learn which tour is in flight.
            refresh_partial_payload()
            tour_t0 = time.time()
            clean = bkz.tour(par, 0, -1, tracer)
            tour_dt = time.time() - tour_t0
            i += 1

            # ---- D3: per-tour progress, flushed EVERY tour ----
            snap = sampler.sample()
            r00 = float(M.get_r(0, 0))
            b0_gso = r00 ** 0.5
            logdet = float(M.get_log_det(0, d))
            import math  # noqa: PLC0415

            # INCIDENTAL OBSERVATION, recorded rather than silently absorbed.
            # In the installed fpylll 0.6.4, M.get_log_det(0, d) returns the log
            # determinant of the GRAM matrix, i.e. 2*log(vol). Measured on this
            # construction at d=64: exp(get_log_det/(2d)) == q**0.5 to ~1e-12,
            # while exp(get_log_det/d) == q. The committed precedent
            # TASK-20260815-f14d3c (sha256 58a1fdc2...) writes
            #   det_l_pow_1_over_d = exp(log_det / d)
            # which is therefore vol**(2/d), not vol**(1/d). BOTH forms are
            # recorded below, each labelled; the corrected one is the reported
            # `delta_0_from_gso_logdet`. This is an observation about a
            # committed artifact, not a change to it.
            vol_root_from_gso = math.exp(logdet / (2.0 * d))
            delta0_gso = (b0_gso / vol_root_from_gso) ** (1.0 / d)
            delta0_gso_precedent_form = (
                b0_gso / math.exp(logdet / d)
            ) ** (1.0 / d)
            row = {
                "tour_index": i - 1,
                "tours_completed_after_this_tour": i,
                "wall_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "elapsed_seconds_since_cell_start": round(
                    time.time() - t_start_wall, 6
                ),
                "tour_elapsed_seconds": round(tour_dt, 6),
                "cpu_seconds_since_cell_start": round(
                    process_time() - t_start_cpu, 6
                ),
                "clean": bool(clean),
                "gso_r00": r00,
                "b0_norm_from_gso": b0_gso,
                "gso_log_det_0_d": logdet,
                "gso_log_det_semantics": (
                    "log det of the GRAM matrix (= 2*log vol), measured: "
                    "exp(get_log_det/(2d)) == q**0.5 on this construction"
                ),
                "vol_root_from_gso_exp_logdet_over_2d": vol_root_from_gso,
                "delta_0_from_gso_logdet": delta0_gso,
                "delta_0_from_gso_logdet_precedent_literal_form":
                    delta0_gso_precedent_form,
                "delta_0_precedent_form_note": (
                    "TASK-20260815-f14d3c's literal "
                    "(sqrt(get_r(0,0)) / exp(get_log_det(0,d)/d))**(1/d); "
                    "recorded for comparison ONLY, see gso_log_det_semantics"
                ),
                "root_hermite_factor": root_hermite_factor(b0_gso, Q, d),
                "root_hermite_factor_legacy_defective_formula":
                    root_hermite_factor_legacy_defective(b0_gso, Q, d),
                "peak_rss_bytes": snap["peak_rss_bytes"],
                "cpu_times": snap["cpu_times"],
            }
            state["tours_table"].append(row)
            state["tours_completed"] = i
            state["tour_in_flight"] = None
            state["tour_in_flight_started_wall"] = None
            journal.write({**identity, "record_kind": "tour_progress", **row})
            tee.emit(
                f"tour {i - 1} done ({i} tours so far) in {tour_dt:.3f}s "
                f"delta_0={delta0_gso:.6f} rss={snap['peak_rss_mb']}MB "
                f"clean={bool(clean)}"
            )
            refresh_partial_payload()

            if surrogate and simulate_slow_tour_seconds > 0:
                time.sleep(simulate_slow_tour_seconds)

            if clean or par.block_size >= bkz.M.d:
                break_reason = "clean_or_blocksize_ge_d"
                break
            if (par.flags & BKZ.AUTO_ABORT) and auto_abort.test_abort():
                break_reason = "auto_abort"
                break
            if (par.flags & BKZ.MAX_LOOPS) and i >= par.max_loops:
                break_reason = "max_loops"
                break
            if (par.flags & BKZ.MAX_TIME) and (
                process_time() - cputime_start >= par.max_time
            ):
                break_reason = "max_time"
                break

        result["bkz_elapsed_seconds"] = time.time() - t_bkz
        result["break_reason"] = break_reason

        # ---- D5 ----
        result["tours"] = i
        result["tours_mechanism"] = "driving_loop_counter"
        result["tours_definition"] = (
            "The number of completed iterations of the transcribed upstream "
            "BKZReduction.__call__ while-loop, i.e. the number of "
            "bkz.tour(par, 0, -1, tracer) calls that returned. That set is "
            "exactly the set of ('tour', i) tracer contexts upstream opens, so "
            "it is the number of BKZ tours."
        )
        result["tours_why_not_bkz_trace"] = (
            "bkz.trace is None after a default bkz(par) because "
            "BKZReduction.__call__ defaults tracer=False and then sets "
            "self.trace = None; and even with tracer=True the count exists only "
            "AFTER the whole call returns, which is the case a killed cell never "
            "reaches. getattr(bkz,'tours',None) is never used: fpylll assigns no "
            "such attribute."
        )
        result["tours_table"] = state["tours_table"]

        b0 = A[0].norm()
        result["b0_norm"] = float(b0)
        # ---- D6 ----
        result["root_hermite_factor"] = root_hermite_factor(b0, Q, d)
        result["root_hermite_factor_formula"] = "(b0 / q**0.5) ** (1/d)"
        result["root_hermite_factor_legacy_defective_formula"] = (
            root_hermite_factor_legacy_defective(b0, Q, d)
        )
        result["root_hermite_factor_legacy_formula_text"] = (
            "b0**(1/d) / (q**0.5)**(1/1)   <-- the pinned predecessor's line 78, "
            "recorded for comparison ONLY and never reported as the answer"
        )
        result["root_hermite_distortion_corrected_over_legacy"] = (
            result["root_hermite_factor"]
            / result["root_hermite_factor_legacy_defective_formula"]
        )
        result["root_hermite_distortion_closed_form_q_pow_half_minus_1_over_2d"] = (
            root_hermite_distortion_closed_form(Q, d)
        )
        result["status"] = "COMPLETED"
    except Exception as exc:  # noqa: BLE001 - recorded, not raised
        result["status"] = "ERROR"
        result["error"] = f"{type(exc).__name__}: {exc}"
        import traceback  # noqa: PLC0415

        result["traceback"] = traceback.format_exc()
    finally:
        try:
            signal.setitimer(signal.ITIMER_REAL, 0)
        except Exception:
            pass
        sampler.stop_event.set()
        try:
            from fpylll import FPLLL as _F  # noqa: PLC0415

            _F.set_precision(53)
        except Exception:
            pass

    snap = sampler.sample()
    result["elapsed_seconds"] = round(time.time() - t_start_wall, 6)
    result["cpu_seconds"] = round(process_time() - t_start_cpu, 6)
    result["resources"] = snap
    result["peak_rss_bytes"] = snap["peak_rss_bytes"]
    result["peak_rss_mb"] = snap["peak_rss_mb"]
    result["cpu_times"] = snap["cpu_times"]
    result["stdout_tail"] = tee.tail()
    result["heartbeat_seconds"] = heartbeat_seconds
    result["sampler_samples_observed"] = sampler.samples
    result["sampler_samples_expected_if_never_starved"] = (
        int(result["elapsed_seconds"] / heartbeat_seconds)
        if heartbeat_seconds > 0 else None
    )
    result["sampler_starvation_note"] = (
        "observed vs expected heartbeat samples. A large shortfall is the "
        "GIL held by fplll C calls; it is measured here rather than asserted."
    )
    result["psutil_available"] = sampler.psutil_available
    result["psutil_version"] = sampler.psutil_version
    result["psutil_error"] = sampler.psutil_error
    result["end_wall_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    journal.write(result)
    tee.emit(
        f"cell -> {result['status']} tours={result.get('tours')} in "
        f"{result['elapsed_seconds']:.3f}s"
    )
    return result


# ------------------------------------------------------------------ results
def rebuild_results(journal_path: str, out_path: str) -> dict:
    """Aggregate the append-only journal into a single results JSON.

    Not signal-safe and never called from signal context. Tolerates a
    truncated final line (a partial write cannot happen with a single
    os.write, but the reader must not assume it): unparseable lines are
    RETAINED VERBATIM under `unparseable_lines` rather than dropped.
    """
    records, bad = [], []
    with open(journal_path, "r", errors="replace") as fh:
        for lineno, line in enumerate(fh, 1):
            line = line.rstrip("\n")
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except Exception as exc:
                bad.append({"lineno": lineno, "raw": line,
                            "error": f"{type(exc).__name__}: {exc}"})
    agg = {
        "instrument": INSTRUMENT_VERSION,
        "journal_path": journal_path,
        "journal_sha256": sha256_file(journal_path),
        "rebuilt_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "record_count": len(records),
        "record_kinds": sorted({r.get("record_kind", "?") for r in records}),
        "statuses_present": sorted({r["status"] for r in records if "status" in r}),
        "records": records,
        "unparseable_lines": bad,
    }
    with open(out_path, "w") as fh:
        json.dump(agg, fh, indent=2)
    return agg


# ------------------------------------------------------------------ main
def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("run", help="run one or more matched-pair cells")
    r.add_argument("--out-dir", required=True)
    r.add_argument("--prefix", default="rt_ctrl_1_matched_pair_v2")
    r.add_argument("--d", type=int, default=D_DEFAULT)
    r.add_argument("--beta", type=int, default=BETA_DEFAULT)
    r.add_argument("--mpfr-bits", default="75,100",
                   help="comma-separated list of mpfr precisions, one cell each")
    r.add_argument("--roles", default="",
                   help="comma-separated role labels, one per cell")
    r.add_argument("--strategies", default=DEFAULT_STRATEGIES)
    r.add_argument("--no-strategies", action="store_true")
    r.add_argument("--heartbeat-seconds", type=float, default=1.0)
    r.add_argument("--simulate-slow-tour-seconds", type=float, default=0.0)
    r.add_argument("--cell-timeout-seconds", type=float, default=0.0)
    r.add_argument("--max-toy-d", type=int, default=128)
    r.add_argument("--scale-run-authorisation", default="")

    rb = sub.add_parser("rebuild-results", help="aggregate a journal into JSON")
    rb.add_argument("--journal", required=True)
    rb.add_argument("--out", required=True)

    sub.add_parser("self-check", help="print environment and formula self-test")

    a = p.parse_args(argv)

    if a.cmd == "rebuild-results":
        agg = rebuild_results(a.journal, a.out)
        print(json.dumps({k: v for k, v in agg.items() if k != "records"}, indent=2))
        return 0

    if a.cmd == "self-check":
        print(json.dumps(environment_record(None), indent=2))
        print(json.dumps({
            "distortion_q3329_d512": root_hermite_distortion_closed_form(3329, 512),
            "distortion_q3329_d80": root_hermite_distortion_closed_form(3329, 80),
        }, indent=2))
        return 0

    # ---- scale guard: this task is ZERO-LATTICE-COMPUTE ----
    if a.d > a.max_toy_d and not a.scale_run_authorisation.strip():
        sys.stderr.write(
            f"REFUSED: d={a.d} exceeds --max-toy-d={a.max_toy_d} and no "
            "--scale-run-authorisation was given. TASK-20260826-602395 is "
            "zero-lattice-compute; DEC-20260824-5e222e refuses the d=512 / "
            "mpfr_bits=100 re-run until this instrument exists and is reviewed.\n"
        )
        return 2

    os.makedirs(a.out_dir, exist_ok=True)
    strategies = None if a.no_strategies else a.strategies
    journal_path = os.path.join(a.out_dir, f"{a.prefix}_results.jsonl")
    results_path = os.path.join(a.out_dir, f"{a.prefix}_results.json")
    stdout_path = os.path.join(a.out_dir, f"{a.prefix}_stdout.log")
    env_path = os.path.join(a.out_dir, f"{a.prefix}_environment.json")

    env = environment_record(strategies)
    env["argv"] = sys.argv
    env["scale_guard"] = {
        "max_toy_d": a.max_toy_d,
        "d_requested": a.d,
        "scale_run_authorisation": a.scale_run_authorisation or None,
    }
    with open(env_path, "w") as fh:
        json.dump(env, fh, indent=2)

    journal = Journal(journal_path)
    tee = StdoutTee(stdout_path)
    journal.write({
        "record_kind": "run_header",
        "instrument": INSTRUMENT_VERSION,
        "task": "TASK-20260826-602395",
        "batch": "BATCH-762807",
        "goal": "GOAL-MLKEM-005",
        "d": a.d, "beta": a.beta,
        "environment_json": env_path,
        "pinned_predecessor_sha256": PINNED_PREDECESSOR_SHA256,
        "start_wall_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    })

    bits = [int(x) for x in a.mpfr_bits.split(",") if x.strip()]
    roles = [x for x in a.roles.split(",") if x.strip()]
    for idx, mb in enumerate(bits):
        role = roles[idx] if idx < len(roles) else f"cell_mpfr_{mb}"
        run_cell(
            d=a.d, beta=a.beta, mpfr_bits=mb, role=role,
            journal=journal, tee=tee, strategies=strategies,
            heartbeat_seconds=a.heartbeat_seconds,
            simulate_slow_tour_seconds=a.simulate_slow_tour_seconds,
            cell_timeout_seconds=a.cell_timeout_seconds,
        )
        rebuild_results(journal_path, results_path)

    rebuild_results(journal_path, results_path)
    tee.emit(f"wrote {journal_path} and {results_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
