#!/usr/bin/env python3
"""EXP-GFPN-05ff43 protocols 2-r5 / 2-a1-r5 -- the RL-1 LAUNCH RECORDER (readbackfull RL-1, RL-5; readbackclose RK-1;
failclosed RF-1; childend RG-1, RG-4 (a); gapattr RH-4; value classes RL-5, RK-5, RF-7, RG-8, RH-7). New file.

Each r5 entry, after importing the frozen modules and installing SE-3 (and, in the a1 entry, HR-3), and before
dispatching any command, calls install(): the module attribute v2_solver.run_child is replaced by `launch_recorder`, a
RECORDING PASS-THROUGH (RL-1). This module holds the ONLY load of the frozen run_child in the r5 tree (install() and its
read-back, DEC-20260924-daf670 LKA-7 (b)); the captured reference is stored only in _ST, where launch_recorder reads it,
and it is called only inside launch_recorder.

launch_recorder:
  (a) calls the ORIGINAL frozen function object, captured at install (module v2_solver, qualname run_child, code file
      implementation-v2/v2_solver.py, first line 149), with identical positional and keyword arguments;
  (b) returns the object that call returned, unchanged and uncopied; if the call raises, it re-raises the same exception
      (bare `raise`) after recording;
  (c) before returning or re-raising, appends ONE LAUNCH RECORD to the run-root solver-events.json under
      launch_records, in call order, made durable by the layer's single event writer (r5_resolve.append_launch_record),
      copied from the returned record (or, on a raise, from the frozen `rec` found on the traceback) and the call's
      arguments and from nothing else;
  (d) RECORDS ONLY: no value it records selects a result, triggers a re-solve, changes a class, delays or reorders a
      launch, or alters argv, env, cwd, cap, timeout, lock or count_instructions. No sleep, no guard, no function
      replacement. A recording failure is an SE-2 (4) consistency violation.
ON RETURN (RK-1 (a)): child_created is the KEY-PRESENCE test of child_rlimit_report in the returned record;
  pair_read_by_parent is the key-presence test of rlimit_as_child_getrlimit (RK-1 (c)); readback_from "returned_record".
ON RAISE (RK-1 (b) with RF-1 (a)): the raised exception and every exception reachable through __context__ / __cause__
  (each at most once, at most 16; a longer chain or a cycle -> `undetermined`) are inspected READ-ONLY for frames whose
  code object IS the captured frozen run_child (first line 149) or _run_child_locked (first line 177). From the
  outermost frozen run_child frame the local `rec` is read and rlimit_as_child_getrlimit, child_rlimit_report, outcome,
  refusal_reason and returncode are copied where present. child_created is three-valued (RF-1 (a)). raised,
  raise_site, the child pid where a frame holds it, readback_from "raise_frame_record". No frame local is assigned, no
  value found there is called or mutated, and no reference to the traceback or a frame is kept after the record is
  written. frame_inspection "not_found" -> child_created `undetermined` and an SE-2 (4) consistency violation.
PROCESS IDENTITY (RF-1 (b)): a recorder call that ends in a process other than the installing one writes NO launch
  record; it writes recorder-foreign-<pid>.json in the run root and returns or re-raises unchanged, nothing else.
CHILD END (RG-1 with RH-4): at install ONE after-fork-in-parent callback is registered (os.register_at_fork with
  after_in_parent only). It acts only while a recorder call is in progress in the installing process; on its FIRST
  invocation within a call it reads /proc/self/task/<tid>/children, takes the pids not present before the call, and
  if there is exactly one opens ONE software counter on it (PERF_TYPE_SOFTWARE, PERF_COUNT_SW_TASK_CLOCK; disabled;
  enable_on_exec; inherit NOT set; exclude_kernel and exclude_hv set; read_format total time enabled and running;
  close-on-exec). It catches every exception its own code raises (a signal-raised one included), records the type and
  marks the call; it writes nothing to any file, stream or pipe and does nothing in the child. After the frozen call
  returns or raises the recorder reads and closes the counter; every launch record carries child_end_observer and
  child_end ("no_child" | "exec" | "frozen_pre_exec_exit" | "undetermined", RG-1 (c)) and the call's stdout_path and
  stderr_path (RG-4 (a)).
Primitives (os, _libc) are module globals resolved at call time; only a development stand-in in a scratch process
ever replaces them (childend RG-7 (f); never in any package).
"""
import ctypes
import datetime
import errno
import inspect
import json
import os
import struct
import sys
import threading

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import r5_common as R                                    # noqa: E402  (imports no v2 / v2-a1 module)
import r5_resolve as RS                                  # noqa: E402  (the single event writer)

_libc = ctypes.CDLL(None, use_errno=True)
_NR_PERF_EVENT_OPEN = 298                                # x86_64
PERF_TYPE_SOFTWARE = 1
PERF_COUNT_SW_TASK_CLOCK = 1
PERF_FLAG_FD_CLOEXEC = 1 << 3
# perf_event_attr flag bits: disabled (0), inherit (1) NOT set, exclude_kernel (5), exclude_hv (6), enable_on_exec (12)
ATTR_FLAGS = (1 << 0) | (1 << 5) | (1 << 6) | (1 << 12)
READ_FORMAT = 1 | 2                                      # PERF_FORMAT_TOTAL_TIME_ENABLED | PERF_FORMAT_TOTAL_TIME_RUNNING
CHAIN_LIMIT = 16                                         # RF-1 (a)
FROZEN_FILE = os.path.join(R.V2_DIR, "v2_solver.py")
RUN_CHILD_FIRSTLINE = 149
LOCKED_FIRSTLINE = 177
FORK_LINE = 181                                          # the frozen function forks and binds `pid` only at line 181
FOREIGN_PREFIX = "recorder-foreign-"
UNDET = "undetermined"
# RG-1 (c): the frozen child's own os._exit pairs (report prefix, returncode)
FROZEN_EXIT = (("ERR setrlimit", 97), ("ERR setrlimit", 99), ("", 99), ("OK", 98), ("OK", 99))

_ST = {"installed": False, "original": None, "signature": None, "code_run_child": None, "code_locked": None,
       "installing_pid": None, "run_dir": None, "v2_solver": None, "callback_registered": False,
       "in_call": False, "call": None, "ordinal": 0}


def _utc():
    return datetime.datetime.now(datetime.timezone.utc)


def _iso(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


# ----------------------------------------------------------------------------- RG-1: the child-end observer (gamma; clause RG-1)
def _thread_children():
    """/proc/self/task/<tid>/children of the calling thread (RG-1 (a) (1))."""
    fd = os.open("/proc/self/task/%d/children" % threading.get_native_id(), os.O_RDONLY)
    try:
        data = b""
        while True:
            chunk = os.read(fd, 65536)
            if not chunk:
                break
            data += chunk
    finally:
        os.close(fd)
    return [int(x) for x in data.split()]


def _perf_open_task_clock(pid):
    """RG-1 (a) (2): one software task-clock counter on pid, disabled, enable_on_exec, inherit not set, exclude_kernel
    and exclude_hv set, read_format total time enabled and running, close-on-exec. Returns (fd, None) or (None, reason)."""
    b = struct.pack("IIQQQQQ", PERF_TYPE_SOFTWARE, 128, PERF_COUNT_SW_TASK_CLOCK, 0, 0, READ_FORMAT, ATTR_FLAGS)
    buf = ctypes.create_string_buffer(b + b"\0" * (128 - len(b)), 128)
    fd = _libc.syscall(_NR_PERF_EVENT_OPEN, buf, pid, -1, -1, PERF_FLAG_FD_CLOEXEC)
    if fd < 0:
        e = ctypes.get_errno()
        return None, "perf_event_open(PERF_TYPE_SOFTWARE, PERF_COUNT_SW_TASK_CLOCK) failed: %s (%s)" % (errno.errorcode.get(e, e), os.strerror(e) if e else "")
    return fd, None


def _read_counter(fd):
    """RG-1 (b): value, time_enabled, time_running; the counter is closed."""
    try:
        v, enabled, running = struct.unpack("QQQ", os.read(fd, 24))
    finally:
        os.close(fd)
    return v, enabled, running


def _after_fork_in_parent():
    """RG-1 (a) with RH-4: registered with os.register_at_fork(after_in_parent=...) only; nothing for the child."""
    call = _ST["call"]
    if call is None or not _ST["in_call"] or os.getpid() != _ST["installing_pid"]:
        return
    try:
        call["callback_invocations"] += 1
        if call["callback_invocations"] > 1:
            call["marks"].append("second callback invocation within the call")
            return
        obs = call["observer"]
        before = call["children_before"]
        if before is None:
            obs["reason"] = "the pre-call children listing was absent or unreadable"
            return
        try:
            after = _thread_children()
        except OSError as e:
            obs["reason"] = "the children listing was absent or unreadable: %s" % type(e).__name__
            return
        new = [p for p in after if p not in before]
        obs["new_pids"] = new
        if len(new) != 1:
            obs["reason"] = "no new child pid" if not new else "several new child pids"
            return
        obs["pid"] = new[0]
        fd, why = _perf_open_task_clock(new[0])
        if fd is None:
            obs["reason"] = why
            return
        call["counter_fd"] = fd
        obs["opened"] = True
    except BaseException as e:                           # noqa: BLE001  (RG-1 (a): every exception; RH-4 incl. signal-raised)
        call["callback_exception"] = type(e).__name__
        call["marks"].append("the callback caught %s" % type(e).__name__)


# ----------------------------------------------------------------------------- child_end (RG-1 (c)); epsilon value, gamma writer
def child_end_value(child_created, raised, call):
    """RG-1 (c) with RH-4: exactly one of no_child | exec | frozen_pre_exec_exit | undetermined. `call` carries the
    observer, the marks, whether the callback fired, and the returned record's report and returncode."""
    obs = call["observer"]
    fired = call["callback_invocations"] > 0
    if call["marks"]:
        return UNDET
    if child_created is False and raised is None and not fired:
        return "no_child"
    if child_created is False and raised is not None and not fired:
        return "no_child"
    if child_created is not True or raised is not None:
        return UNDET
    if not (obs.get("opened") and obs.get("read") and obs.get("pid") is not None):
        return UNDET
    if isinstance(obs.get("time_enabled_ns"), int) and obs["time_enabled_ns"] > 0:
        return "exec"
    if obs.get("time_enabled_ns") == 0 and obs.get("value") == 0 and call.get("report_carried"):
        rep, rc = call.get("report"), call.get("returncode")
        for prefix, code in FROZEN_EXIT:
            if rc == code and isinstance(rep, str) and ((prefix == "" and rep == "") or (prefix and rep.startswith(prefix))):
                return "frozen_pre_exec_exit"
    return UNDET


# ----------------------------------------------------------------------------- RK-1 (b) with RF-1 (a): the raise-path inspection
def _chain(exc):
    """RF-1 (a): the raised exception and every exception reachable through __context__ / __cause__, each at most once,
    at most CHAIN_LIMIT; returns (list, limit_or_cycle_flag)."""
    out, seen, flag = [], set(), None
    stack = [(exc, ())]
    while stack:
        e, path = stack.pop(0)
        if id(e) in path:
            flag = "cycle"
            continue
        if id(e) in seen:
            continue
        seen.add(id(e))
        out.append(e)
        if len(out) > CHAIN_LIMIT:
            flag = "chain limit %d exceeded" % CHAIN_LIMIT
            break
        for nxt in (e.__cause__, e.__context__):
            if nxt is not None:
                stack.append((nxt, path + (id(e),)))
    return out, flag


def _inspect_raise(exc):
    """Read-only inspection of the raise path (RK-1 (b); RF-1 (a)). Keeps no reference to a traceback or frame."""
    crc, clk = _ST["code_run_child"], _ST["code_locked"]
    chain, flag = _chain(exc)
    info = {"chain_length": len(chain), "chain_flag": flag, "frame_inspection": "not_found", "rec_state": None,
            "copied": {}, "locked_frames": [], "pid": None, "raise_site": None}
    rec_frame_found = False
    rec_has_report = False
    try:
        for ci, e in enumerate(chain):
            tb = e.__traceback__
            first_run_child = None
            innermost_frozen = None
            while tb is not None:
                fr = tb.tb_frame
                code = fr.f_code
                if code is crc and first_run_child is None:
                    first_run_child = fr
                if code is clk:
                    loc = fr.f_locals
                    pid = loc.get("pid")
                    info["locked_frames"].append({"chain_index": ci, "tb_lineno": tb.tb_lineno,
                                                  "pid_bound": "pid" in loc, "pid": pid if isinstance(pid, int) else None})
                    if isinstance(pid, int) and pid > 0 and info["pid"] is None:
                        info["pid"] = pid
                    del loc
                if ci == 0 and os.path.abspath(code.co_filename) == os.path.abspath(FROZEN_FILE):
                    innermost_frozen = (code.co_name, tb.tb_lineno)
                del fr
                tb = tb.tb_next
            if ci == 0:
                info["raise_site"] = {"function": innermost_frozen[0], "line": innermost_frozen[1]} if innermost_frozen else None
            if first_run_child is not None and not rec_frame_found:
                rec_frame_found = True
                info["frame_inspection"] = "found"
                loc = first_run_child.f_locals
                if "rec" in loc and isinstance(loc["rec"], dict):
                    rec = loc["rec"]
                    info["rec_state"] = "bound"
                    for key in ("rlimit_as_child_getrlimit", "child_rlimit_report", "outcome", "refusal_reason", "returncode"):
                        if key in rec:
                            info["copied"][key] = json.loads(json.dumps(rec[key], default=str))
                    rec_has_report = "child_rlimit_report" in rec
                    del rec
                else:
                    info["rec_state"] = "unbound"
                del loc
            first_run_child = None
    finally:
        tb = None
        chain = None
    # RF-1 (a): child_created, three-valued
    if info["frame_inspection"] == "not_found" or flag is not None:
        created = UNDET
    elif rec_has_report or info["pid"] is not None:
        created = True
    elif all(f["tb_lineno"] < FORK_LINE and not f["pid_bound"] for f in info["locked_frames"]):
        created = False
    else:
        created = UNDET
    info["child_created"] = created
    return info


# ----------------------------------------------------------------------------- RF-1 (b): process identity
def _foreign(exc):
    """RF-1 (b): in a process other than the installing one: write recorder-foreign-<pid>.json in the run root and do
    nothing else (no launch record; no exit, signal or wait). A write failure is not handled beyond this."""
    body = json.dumps({"installing_pid": _ST["installing_pid"], "pid": os.getpid(),
                       "raised": type(exc).__name__ if exc is not None else None}).encode()
    try:
        fd = os.open(os.path.join(_ST["run_dir"], "%s%d.json" % (FOREIGN_PREFIX, os.getpid())), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
        try:
            os.write(fd, body)
        finally:
            os.close(fd)
    except Exception:                                    # noqa: BLE001
        pass


# ----------------------------------------------------------------------------- the launch record (gamma; clause RL-1 / RK-1 / RF-1 / RG-1 / RG-4 (a))
def _bind(args, kwargs):
    try:
        b = _ST["signature"].bind(*args, **kwargs)
        b.apply_defaults()
        return dict(b.arguments), None
    except TypeError as e:
        return {}, "arguments did not bind to the frozen signature: %s" % type(e).__name__


def _base_record(ordinal, a, bind_err, caller, start, end, call):
    so, se = a.get("stdout_path"), a.get("stderr_path")
    return {"ordinal": ordinal, "tag": os.path.basename(so) if isinstance(so, str) else None,
            "stdout_path": so, "stderr_path": se,
            "arguments_bound": bind_err is None, "arguments_bind_error": bind_err,
            "caller": caller, "start_utc": _iso(start), "end_utc": _iso(end),
            "child_end_observer": {k: call["observer"].get(k) for k in ("pid", "opened", "read", "value", "time_enabled_ns",
                                                                         "time_running_ns", "reason")},
            "callback_fired": call["callback_invocations"] > 0, "callback_marks": list(call["marks"]),
            "callback_exception": call["callback_exception"]}


def _record_return(res, ordinal, a, bind_err, caller, start, end, call):
    """RL-1 (c) with RK-1 (a), (c): copied from the returned record and the call's arguments."""
    rec = _base_record(ordinal, a, bind_err, caller, start, end, call)
    rec["argv"] = list(res["argv"]) if "argv" in res else "absent"
    rec["cap_bytes_requested"] = res["cap_bytes_requested"] if "cap_bytes_requested" in res else "absent"
    rec["rlimit_as_child_getrlimit"] = res["rlimit_as_child_getrlimit"] if "rlimit_as_child_getrlimit" in res else "absent"
    rec["child_rlimit_report_carried"] = "child_rlimit_report" in res
    if "child_rlimit_report" in res:
        rec["child_rlimit_report"] = res["child_rlimit_report"]
    if "refusal_reason" in res:
        rec["refusal_reason"] = res["refusal_reason"]
    rec["outcome"] = res.get("outcome")
    if "returncode" in res:
        rec["returncode"] = res["returncode"]
    rec["child_created"] = "child_rlimit_report" in res                                  # RK-1 (a): key presence
    rec["pair_read_by_parent"] = "rlimit_as_child_getrlimit" in res                      # RK-1 (c)
    rec["raised"] = None
    rec["readback_from"] = "returned_record"
    call["report_carried"] = rec["child_rlimit_report_carried"]
    call["report"] = res.get("child_rlimit_report")
    call["returncode"] = res.get("returncode")
    rec["child_end"] = child_end_value(rec["child_created"], None, call)
    return rec


def _record_raise(exc, ordinal, a, bind_err, caller, start, end, call):
    """RK-1 (b) with RF-1 (a): copied from the frozen `rec` on the traceback and the call's arguments."""
    info = _inspect_raise(exc)
    rec = _base_record(ordinal, a, bind_err, caller, start, end, call)
    cp = info["copied"]
    rec["argv"] = "absent (raise path: RK-1 (b) copies no argv)"
    rec["cap_bytes_requested"] = a["cap_bytes"] if "cap_bytes" in a else "absent"
    rec["rlimit_as_child_getrlimit"] = cp["rlimit_as_child_getrlimit"] if "rlimit_as_child_getrlimit" in cp else "absent"
    rec["child_rlimit_report_carried"] = "child_rlimit_report" in cp
    for key in ("child_rlimit_report", "outcome", "refusal_reason", "returncode"):
        if key in cp:
            rec[key] = cp[key]
    rec["child_created"] = info["child_created"]
    rec["pair_read_by_parent"] = "rlimit_as_child_getrlimit" in cp
    rec["raised"] = type(exc).__name__
    rec["raise_site"] = info["raise_site"]
    rec["pid"] = info["pid"]
    rec["readback_from"] = "raise_frame_record"
    rec["frame_inspection"] = info["frame_inspection"]
    rec["rec"] = info["rec_state"] if info["rec_state"] else "not found"
    rec["chain"] = {"length": info["chain_length"], "flag": info["chain_flag"], "locked_frames": info["locked_frames"]}
    call["report_carried"] = rec["child_rlimit_report_carried"]
    call["report"] = cp.get("child_rlimit_report")
    call["returncode"] = cp.get("returncode")
    rec["child_end"] = child_end_value(rec["child_created"], rec["raised"], call)
    return rec, info["frame_inspection"] == "not_found"


def _finish(call, a, bind_err, caller, ordinal, start, end, res, exc):
    _ST["call"] = None
    fd = call.pop("counter_fd", None)
    if os.getpid() != _ST["installing_pid"]:             # RF-1 (b)
        _foreign(exc)
        return
    obs = call["observer"]
    if fd is not None:
        try:
            v, en, run = _read_counter(fd)
            obs.update(read=True, value=v, time_enabled_ns=en, time_running_ns=run)
        except Exception as e:                           # noqa: BLE001
            obs["reason"] = "counter read failed: %s" % type(e).__name__
    not_found = False
    try:
        if exc is None:
            rec = _record_return(res, ordinal, a, bind_err, caller, start, end, call)
        else:
            rec, not_found = _record_raise(exc, ordinal, a, bind_err, caller, start, end, call)
        RS.append_launch_record(rec)
    except RS.SolverEventConsistencyError:
        raise
    except Exception as e:                               # noqa: BLE001  (RL-1 (d): a recording failure)
        RS._recording_failure("launch record", e)
    if not_found:                                        # RK-1 (b): frame_inspection not_found is an SE-2 (4) violation
        doc = RS._STATE["doc"]
        doc["consistency_violation"] = True
        doc["recording_failures"].append({"where": "launch record %d: frame_inspection not_found" % ordinal, "at": R.now()})
        RS._write()


def launch_recorder(*args, **kwargs):
    """RL-1 with RK-1, RF-1, RG-1, RG-4 (a): the recording pass-through installed at v2_solver.run_child."""
    original = _ST["original"]
    a, bind_err = _bind(args, kwargs)
    call = {"children_before": None, "callback_invocations": 0, "marks": [], "callback_exception": None,
            "observer": {"pid": None, "opened": False, "read": False, "value": None, "time_enabled_ns": None,
                         "time_running_ns": None, "reason": None, "new_pids": None},
            "counter_fd": None}
    try:
        call["children_before"] = _thread_children()
    except OSError:
        call["children_before"] = None
    fr = sys._getframe(1)
    caller = {"file": os.path.relpath(fr.f_code.co_filename, R.REPO), "function": fr.f_code.co_name, "line": fr.f_lineno}
    del fr
    _ST["ordinal"] += 1
    ordinal = _ST["ordinal"]
    start = _utc()
    _ST["call"] = call
    _ST["in_call"] = True
    try:
        res = original(*args, **kwargs)
    except BaseException as exc:                         # noqa: BLE001
        _ST["in_call"] = False
        end = _utc()
        _finish(call, a, bind_err, caller, ordinal, start, end, None, exc)
        raise
    _ST["in_call"] = False
    end = _utc()
    _finish(call, a, bind_err, caller, ordinal, start, end, res, None)
    return res


launch_recorder.__r5_launch_recorder__ = True


# ----------------------------------------------------------------------------- install and read-back (RL-5; the RL-1 installation)
def install(v2_solver_module, run_dir):
    """RL-1 / RL-5: capture the ORIGINAL frozen run_child (the one load of the frozen function object in the r5 tree)
    and the code objects of run_child and _run_child_locked (RK-1 (b): READ, not replaced), store the installing pid
    (RF-1 (b)), register the RG-1 after-fork-in-parent callback once, and replace v2_solver.run_child by the recorder.
    Writes nothing."""
    if _ST["installed"]:
        raise RuntimeError("r5_recorder.install called twice")
    RS._ensure_doc(run_dir)
    orig = v2_solver_module.run_child
    locked_code = v2_solver_module._run_child_locked.__code__
    _ST.update(installed=True, original=orig, signature=inspect.signature(orig), code_run_child=orig.__code__,
               code_locked=locked_code, installing_pid=os.getpid(), run_dir=run_dir, v2_solver=v2_solver_module)
    if not _ST["callback_registered"]:
        os.register_at_fork(after_in_parent=_after_fork_in_parent)
        _ST["callback_registered"] = True
    v2_solver_module.run_child = launch_recorder
    return _identity(orig)


def _identity(fn):
    code = getattr(fn, "__code__", None)
    return {"module": getattr(fn, "__module__", None), "qualname": getattr(fn, "__qualname__", None),
            "code_file": os.path.relpath(code.co_filename, R.REPO) if code is not None else None,
            "code_firstlineno": code.co_firstlineno if code is not None else None}


def readback(v2_solver_module, users=()):
    """RL-5 INSTALL READ-BACK: v2_solver.run_child is the RL-1 recorder; the recorder's captured original is the frozen
    function (module v2_solver, qualname run_child, code file implementation-v2/v2_solver.py, first line 149); the
    captured code objects are the frozen run_child's and _run_child_locked's (first line 177); the RG-1 callback is
    registered in this (the installing) process; every loaded module that uses v2_solver (users: v2_driver.V,
    a1_health.V, a1_pari.V where loaded) holds THIS module object, and it is sys.modules['v2_solver']."""
    reasons = []
    attr = getattr(v2_solver_module, "run_child", None)
    is_rec = attr is launch_recorder and getattr(attr, "__r5_launch_recorder__", False) is True
    orig = _ST["original"]
    code = getattr(orig, "__code__", None)
    orig_ok = (orig is not None and orig is not launch_recorder and getattr(orig, "__module__", None) == "v2_solver"
               and getattr(orig, "__qualname__", None) == "run_child" and code is not None
               and os.path.abspath(code.co_filename) == os.path.abspath(FROZEN_FILE) and code.co_firstlineno == RUN_CHILD_FIRSTLINE
               and _ST["code_run_child"] is code)
    lk = _ST["code_locked"]
    locked_ok = (lk is not None and lk.co_name == "_run_child_locked" and lk.co_firstlineno == LOCKED_FIRSTLINE
                 and os.path.abspath(lk.co_filename) == os.path.abspath(FROZEN_FILE))
    cb_ok = _ST["callback_registered"] is True and _ST["installing_pid"] == os.getpid()
    mod_ok = sys.modules.get("v2_solver") is v2_solver_module and all(getattr(u, "V", None) is v2_solver_module for u in users)
    if not is_rec:
        reasons.append("RL-5 install read-back: v2_solver.run_child is not the RL-1 launch recorder")
    if not orig_ok:
        reasons.append("RL-5 install read-back: the recorder's captured original is not the frozen v2_solver.run_child")
    if not locked_ok:
        reasons.append("RL-5 install read-back: the captured _run_child_locked code object is not the frozen one")
    if not cb_ok:
        reasons.append("RL-5 install read-back: the RG-1 after-fork callback is not registered in the installing process")
    if not mod_ok:
        reasons.append("RL-5 install read-back: a module using v2_solver does not hold the one v2_solver module object")
    rec = {"v2_solver.run_child_is_r5_launch_recorder": is_rec, "recorder_original_is_frozen_v2_solver_run_child": orig_ok,
           "captured_run_child_locked_code_is_frozen": locked_ok, "rg1_callback_registered_in_installing_process": cb_ok,
           "one_v2_solver_module_object": mod_ok, "users_checked": [getattr(u, "__name__", "?") for u in users],
           "original_identity": _identity(orig) if orig is not None else None,
           "installing_pid": _ST["installing_pid"], "frozen_file_sha256": R.sha256_file(FROZEN_FILE)}
    return rec, reasons
