#!/usr/bin/env python3
"""EXP-GFPN-05ff43 protocol v2 -- child-process runner, msolve I/O, outcome classes.

MACHINE PROTECTION (AC-1 of DEC-20260923-e788a1; amendment DC-7; card EC-4):
  * every memory-heavy child (msolve, a builder, the Sage comparator, callgrind) is started by
    run_child(): fork; in the CHILD setrlimit(RLIMIT_AS, cap) then getrlimit; the read-back pair
    is sent to the parent over a pipe BEFORE exec. A child that cannot set the cap, or reads back a
    different value, exits without exec -- it REFUSES TO START (DC-6 R-1). The parent also reads
    "Max address space" from /proc/<pid>/limits after exec. Both values are returned; the
    manifest records the child's own read-back, never a wrapper default.
  * before each launch the driver checks its own VmRSS; above 1 GiB it refuses the launch.
  * one memory-heavy child at a time: an exclusive flock on a host-wide lock file, plus a scan of
    /proc for any other solver-like process (EC-10). Either condition refuses the launch.
  * peak memory per child from /proc/<pid>/status VmHWM / VmPeak, polled; also wait4 rusage.
  * msolve always runs with -t 1 (A-3); the thread count is read from the argv actually executed.

INSTRUCTION COUNTS (DC-4 C-1): perf_event_open(PERF_TYPE_HARDWARE, instructions, user only) is
attempted on the child before exec; where the host has no counter (ENOENT, as on the stage-1 host)
the row records the reason, and callgrind_instructions() provides valgrind --tool=callgrind counts
on fixture and m <= 4 shapes only. Labelled "measured work proxy (instructions)"; never converted
to F_p operations; never compared to 2^36.

OUTCOME CLASSES (DC-6 R-1, R-5): ok, timeout, memory_exhausted, crashed, positive_dimensional,
degenerate_parametrisation, refused_to_start (cap not settable / driver RSS / lock / other solver),
not_attempted is written by the driver. None of timeout, memory_exhausted, crashed,
positive_dimensional or degenerate_parametrisation is a measured non-decomposition.
"""
import ast
import ctypes
import errno
import fcntl
import os
import re
import resource
import signal
import struct
import tempfile
import time

import flint

MSOLVE = "/usr/bin/msolve"
VALGRIND = "/usr/bin/valgrind"
CAP_BYTES_DEFAULT = 10737418240            # AC-1: 10 GiB
DRIVER_RSS_LIMIT = 1 << 30                 # AC-1: 1 GiB
LOCK_PATH = os.environ.get("GFPN_V2_SOLVER_LOCK", os.path.join(tempfile.gettempdir(), "gfpn-v2-solver.lock"))
SOLVER_NAMES = ("msolve", "Singular", "magma", "M2", "maple", "sage", "valgrind", "callgrind")


# ----------------------------------------------------------------------------- host checks
def self_rss_bytes():
    with open("/proc/self/status") as fh:
        for line in fh:
            if line.startswith("VmRSS:"):
                return int(line.split()[1]) * 1024
    return None


def host_memory():
    info = {}
    with open("/proc/meminfo") as fh:
        for line in fh:
            k, v = line.split(":", 1)
            if k in ("MemTotal", "SwapTotal", "MemAvailable"):
                info[k + "_kB"] = int(v.split()[0])
    return info


def other_solver_processes(own_pids=()):
    """Solver-like processes on the host that are not ours (EC-10)."""
    found = []
    me = os.getpid()
    for d in os.listdir("/proc"):
        if not d.isdigit():
            continue
        pid = int(d)
        if pid == me or pid in own_pids:
            continue
        try:
            with open(f"/proc/{pid}/cmdline", "rb") as fh:
                argv = [a.decode(errors="replace") for a in fh.read().split(b"\0") if a]
        except OSError:
            continue
        if not argv:
            continue
        exe = os.path.basename(argv[0])
        joined = " ".join(argv)
        if exe in SOLVER_NAMES or (exe.startswith("python") and ("sage" in joined and "/opt/conda-sage" in joined)):
            found.append({"pid": pid, "argv0": argv[0], "cmdline": joined[:300]})
    return found


class SolverLock:
    """Host-wide exclusive lock: one memory-heavy child at a time (AC-1)."""

    def __init__(self, path=LOCK_PATH):
        self.path = path
        self.fh = None

    def acquire(self, wait_s=0):
        self.fh = open(self.path, "a+")
        t0 = time.time()
        while True:
            try:
                fcntl.flock(self.fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
                return True
            except OSError:
                if time.time() - t0 >= wait_s:
                    self.fh.close()
                    self.fh = None
                    return False
                time.sleep(1)

    def release(self):
        if self.fh:
            fcntl.flock(self.fh, fcntl.LOCK_UN)
            self.fh.close()
            self.fh = None


# ----------------------------------------------------------------------------- perf counter
_libc = ctypes.CDLL(None, use_errno=True)
_NR_PERF_EVENT_OPEN = 298     # x86_64


def _perf_open_instructions(pid):
    """Open a user-space instruction counter on pid (disabled, enable_on_exec, inherit).
    Returns (fd, None) or (None, reason)."""
    flags = (1 << 0) | (1 << 1) | (1 << 5) | (1 << 6) | (1 << 12)
    b = struct.pack("IIQQQQQ", 0, 128, 1, 0, 0, 3, flags)
    buf = ctypes.create_string_buffer(b + b"\0" * (128 - len(b)), 128)
    fd = _libc.syscall(_NR_PERF_EVENT_OPEN, buf, pid, -1, -1, 0)
    if fd < 0:
        e = ctypes.get_errno()
        return None, "perf_event_open(PERF_TYPE_HARDWARE, INSTRUCTIONS) failed: %s (%s)" % (errno.errorcode.get(e, e), os.strerror(e))
    return fd, None


def _perf_read(fd):
    try:
        v, enabled, running = struct.unpack("QQQ", os.read(fd, 24))
    finally:
        os.close(fd)
    return {"instructions_user": v, "time_enabled_ns": enabled, "time_running_ns": running,
            "multiplexed": running < enabled}


# ----------------------------------------------------------------------------- the child runner
def run_child(argv, stdout_path, stderr_path, cap_bytes=CAP_BYTES_DEFAULT, timeout_s=None,
              count_instructions=True, cwd=None, env=None, lock=True):
    """Run argv as a capped child. Returns a record dict (never raises for child failures)."""
    rec = {"argv": list(argv), "cap_bytes_requested": cap_bytes, "timeout_s": timeout_s}
    if not isinstance(cap_bytes, int) or cap_bytes <= 0:
        rec.update(outcome="refused_to_start", refusal_reason="invalid cap %r" % (cap_bytes,))
        return rec
    rss = self_rss_bytes()
    rec["driver_rss_bytes_before_launch"] = rss
    if rss is not None and rss > DRIVER_RSS_LIMIT:
        rec.update(outcome="refused_to_start", refusal_reason="driver RSS %d B exceeds 1 GiB (AC-1)" % rss)
        return rec
    others = other_solver_processes()
    if others:
        rec.update(outcome="refused_to_start", refusal_reason="another solver-like process is running (EC-10)",
                   other_processes=others)
        return rec
    lk = SolverLock() if lock else None
    if lk is not None and not lk.acquire(wait_s=0):
        rec.update(outcome="refused_to_start", refusal_reason="host solver lock %s is held (one memory-heavy child at a time)" % LOCK_PATH)
        return rec
    try:
        return _run_child_locked(argv, stdout_path, stderr_path, cap_bytes, timeout_s, count_instructions, cwd, env, rec)
    finally:
        if lk is not None:
            lk.release()


def _run_child_locked(argv, stdout_path, stderr_path, cap_bytes, timeout_s, count_instructions, cwd, env, rec):
    rep_r, rep_w = os.pipe()
    go_r, go_w = os.pipe()
    t0 = time.time()
    pid = os.fork()
    if pid == 0:                                    # ---- child
        try:
            os.close(rep_r)
            os.close(go_w)
            if cwd:
                os.chdir(cwd)
            fo = os.open(stdout_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
            fe = os.open(stderr_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
            os.dup2(fo, 1)
            os.dup2(fe, 2)
            try:
                resource.setrlimit(resource.RLIMIT_AS, (cap_bytes, cap_bytes))
            except Exception as e:                  # noqa: BLE001
                os.write(rep_w, ("ERR setrlimit %r" % (e,)).encode())
                os._exit(97)
            soft, hard = resource.getrlimit(resource.RLIMIT_AS)
            os.write(rep_w, ("OK %d %d" % (soft, hard)).encode())
            os.close(rep_w)
            if soft != cap_bytes or hard != cap_bytes:
                os._exit(98)
            os.read(go_r, 1)
            if env is not None:
                os.execve(argv[0], argv, env)
            os.execv(argv[0], argv)
        except BaseException:                       # noqa: BLE001
            pass
        os._exit(99)
    # ---- parent
    os.close(rep_w)
    os.close(go_r)
    report = b""
    while True:
        chunk = os.read(rep_r, 256)
        if not chunk:
            break
        report += chunk
    os.close(rep_r)
    report = report.decode(errors="replace")
    rec["child_rlimit_report"] = report
    if not report.startswith("OK"):
        os.close(go_w)
        _, st, _ru = os.wait4(pid, 0)
        rec.update(outcome="refused_to_start", refusal_reason="child could not set RLIMIT_AS: %s" % report, returncode=_decode_status(st))
        return rec
    _, soft, hard = report.split()
    rec["rlimit_as_child_getrlimit"] = {"soft": int(soft), "hard": int(hard)}
    if int(soft) != cap_bytes:
        os.close(go_w)
        _, st, _ru = os.wait4(pid, 0)
        rec.update(outcome="refused_to_start", refusal_reason="child read back RLIMIT_AS %s != requested %d" % (soft, cap_bytes), returncode=_decode_status(st))
        return rec
    perf_fd, perf_reason = (None, "not requested")
    if count_instructions:
        perf_fd, perf_reason = _perf_open_instructions(pid)
    os.write(go_w, b"g")
    os.close(go_w)
    peak = {"vmhwm_bytes": 0, "vmpeak_bytes": 0}
    proc_limit = None
    timed_out = False
    status = None
    ru = None
    while True:
        wpid, st, r = os.wait4(pid, os.WNOHANG)
        if wpid == pid:
            status, ru = st, r
            break
        try:
            with open(f"/proc/{pid}/status") as fh:
                for line in fh:
                    if line.startswith("VmHWM:"):
                        peak["vmhwm_bytes"] = max(peak["vmhwm_bytes"], int(line.split()[1]) * 1024)
                    elif line.startswith("VmPeak:"):
                        peak["vmpeak_bytes"] = max(peak["vmpeak_bytes"], int(line.split()[1]) * 1024)
            if proc_limit is None:
                # RLIMIT_AS is inherited across exec, so this read is valid before or after exec
                with open(f"/proc/{pid}/limits") as fh:
                    for line in fh:
                        if line.startswith("Max address space"):
                            proc_limit = line.split()[3]
        except (OSError, ValueError, IndexError):
            pass
        if timeout_s is not None and time.time() - t0 > timeout_s:
            timed_out = True
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            _, status, ru = os.wait4(pid, 0)
            break
        time.sleep(0.2)
    wall = time.time() - t0
    rec["rlimit_as_proc_limits_after_exec"] = proc_limit
    rec["wall_seconds"] = round(wall, 3)
    rec["returncode"] = _decode_status(status)
    rec["timed_out"] = timed_out
    rec["peak_rss_bytes"] = peak["vmhwm_bytes"]
    rec["peak_vm_bytes"] = peak["vmpeak_bytes"]
    rec["rusage"] = {"maxrss_bytes": ru.ru_maxrss * 1024, "utime_s": round(ru.ru_utime, 3), "stime_s": round(ru.ru_stime, 3)} if ru else None
    if perf_fd is not None:
        rec["instructions"] = {"method": "perf_event_open instructions:u (inherit, enable_on_exec)", **_perf_read(perf_fd),
                               "label": "measured work proxy (instructions)"}
    else:
        rec["instructions"] = {"method": None, "instructions_user": None, "reason": perf_reason,
                               "label": "measured work proxy (instructions)"}
    if timed_out:
        rec["outcome"] = "timeout"
    elif rec["returncode"] == 0:
        rec["outcome"] = "ok"
    else:
        # msolve 0.6.5 does not check every allocation: a request refused by RLIMIT_AS surfaces as a fatal
        # signal. Memory exhaustion is recorded only with EVIDENCE of near-cap use (sampled VmPeak / VmHWM, or
        # this child's own wait4 ru_maxrss); a death without that evidence stays `crashed` (conservative).
        ru_max = (ru.ru_maxrss * 1024) if ru else 0
        near_cap = (peak["vmpeak_bytes"] >= 0.80 * cap_bytes or peak["vmhwm_bytes"] >= 0.60 * cap_bytes
                    or ru_max >= 0.60 * cap_bytes)
        err = ""
        try:
            with open(stderr_path, errors="replace") as fh:
                err = fh.read()[-4000:]
        except OSError:
            pass
        alloc_msg = bool(re.search(r"(?i)cannot allocate|out of memory|bad_alloc|memoryerror|mmap|malloc", err))
        rec["outcome"] = "memory_exhausted" if (near_cap or alloc_msg) else "crashed"
        rec["memory_exhausted_basis"] = {"peak_near_cap": near_cap, "allocation_failure_message": alloc_msg,
                                         "rusage_maxrss_bytes": ru_max,
                                         "rule": "memory_exhausted iff a failed child shows near-cap use or an allocation-failure message; else crashed"}
    return rec


def _decode_status(st):
    if st is None:
        return None
    if os.WIFEXITED(st):
        return os.WEXITSTATUS(st)
    if os.WIFSIGNALED(st):
        return -os.WTERMSIG(st)
    return st


def envelope_tuple(rec, host, arm, construction, p, m, n, threads, msolve_version, last_round):
    """DC-7 A-6: the tuple every not_measured row carries."""
    return {"host_mem_total_kB": host.get("MemTotal_kB"), "host_swap_total_kB": host.get("SwapTotal_kB"),
            "cap_bytes_from_child": (rec.get("rlimit_as_child_getrlimit") or {}).get("soft"),
            "cap_proc_limits_after_exec": rec.get("rlimit_as_proc_limits_after_exec"),
            "threads": threads, "msolve_version": msolve_version, "arm": arm, "construction": construction,
            "p": p, "m": m, "n": n, "last_f4_round": last_round}


# ----------------------------------------------------------------------------- msolve
def msolve_argv(inpath, outpath, threads=1, gb_only=False):
    argv = [MSOLVE, "-v", "2", "-t", str(threads), "-f", inpath, "-o", outpath]
    argv += ["-g", "1"] if gb_only else ["-P", "1"]
    return argv


def threads_from_argv(argv):
    for i, a in enumerate(argv):
        if a == "-t" and i + 1 < len(argv):
            return int(argv[i + 1])
    return None


F4_ROW = re.compile(r"^\s*(\d+)\s+(\d+)\s+(\d+)\s+(\d+) x (\d+)\s+([\d.]+)%\s+(\d+) new\s+(\d+) zero\s+([\d.]+) \| ([\d.]+)")


def parse_msolve_log(text):
    """Per-round F4 table, summary, FGLM data (v1 parser, extended with the exact trace tuple used by
    jv_anchor_system_trace_identity and the DC-4 C-2 proxy bracket)."""
    st = {"dimension_of_quotient": None, "f4_rounds": [], "fglm": {}, "no_solution": False,
          "positive_dimension_reported": False, "timings": {}, "f4_summary": {}}
    mm = re.search(r"Dimension of quotient:\s*(\d+)", text)
    if mm:
        st["dimension_of_quotient"] = int(mm.group(1))
    if "Grobner basis has a single element" in text or "No solution" in text:
        st["no_solution"] = True
    if re.search(r"(?i)positive dimension|dimension is positive|not zero-dimensional|positive-dimensional", text):
        st["positive_dimension_reported"] = True
    nnz_total = red_total = 0.0
    for line in text.splitlines():
        r = F4_ROW.match(line)
        if not r:
            continue
        deg, sel, pairs, rows, cols, dens, new, zero, treal, tcpu = r.groups()
        rows, cols, dens = int(rows), int(cols), float(dens)
        k = int(new) + int(zero)
        nnz = rows * cols * dens / 100.0
        red = k * max(rows - k, 1) * cols * dens / 100.0
        nnz_total += nnz
        red_total += red
        st["f4_rounds"].append({"deg": int(deg), "sel": int(sel), "pairs": int(pairs), "rows": rows, "cols": cols,
                                "density_pct": dens, "new": int(new), "zero": int(zero),
                                "sec_real": float(treal), "sec_cpu": float(tcpu)})
    st["f4_summary"]["proxy_bracket"] = {
        "nnz": nnz_total, "reduction": red_total,
        "label": "proxy bracket [nnz, reduction]: NOT A BOUND IN EITHER DIRECTION (red team K6(d)(2)-(3)); never enters a band",
        "definitions": "nnz = sum rows*cols*density; reduction = sum (new+zero)*(rows-new-zero)*cols*density (v1 implementation.md lines 99-103)"}
    st["f4_summary"]["max_degree"] = max([r["deg"] for r in st["f4_rounds"]], default=None)
    st["f4_summary"]["n_rounds"] = len(st["f4_rounds"])
    for key, pat in {"max_matrix": r"max\. matrix data\s+(\d+) x (\d+) \(([\d.]+)%\)",
                     "rows_reduced": r"#rows reduced\s+(\d+)", "pairs_reduced": r"#pairs reduced\s+(\d+)",
                     "zero_reductions": r"#zero reductions\s+(\d+)", "size_of_basis": r"size of basis\s+(\d+)",
                     "terms_in_basis": r"#terms in basis\s+(\d+)"}.items():
        mm = re.search(pat, text)
        if mm:
            g = mm.groups()
            st["f4_summary"][key] = [float(x) if "." in x else int(x) for x in g] if len(g) > 1 else int(g[0])
    for key, pat in {"overall_cpu": r"overall\(cpu\)\s+([\d.]+) sec", "overall_elapsed": r"overall\(elapsed\)\s+([\d.]+) sec",
                     "linear_algebra_sec": r"linear algebra\s+([\d.]+) sec"}.items():
        mm = re.search(pat, text)
        if mm:
            st["timings"][key] = float(mm.group(1))
    mm = re.search(r"\[(\d+), (\d+)\], Non trivial / Trivial = ([\d.]+)%", text)
    if mm:
        st["fglm"] = {"dim": int(mm.group(1)), "nontrivial_cols": int(mm.group(2)), "nontrivial_pct": float(mm.group(3))}
    mm = re.search(r"Degree of the square-free part:\s*(\d+)", text)
    if mm:
        st["fglm"]["squarefree_degree"] = int(mm.group(1))
    mm = re.search(r"(?i)(?:elimination|eliminating|minimal) polynomial[^\n]*?degree[:\s]*(\d+)", text)
    if mm:
        st["fglm"]["minpoly_degree_reported"] = int(mm.group(1))
    return st


def trace_tuple(st):
    """The per-round trace compared by jv_anchor_system_trace_identity (rulings.DC-5 (2)):
    (degree, pairs, rows, columns, new, zero)."""
    return [(r["deg"], r["pairs"], r["rows"], r["cols"], r["new"], r["zero"]) for r in st["f4_rounds"]]


def parse_msolve_param(path):
    """Parse msolve -P 1 output. Returns ('none', None) for [-1] (no solution over the algebraic
    closure / unit ideal), ('param', dict), ('positive_dimensional', reason) or ('unparseable', reason)."""
    try:
        txt = open(path).read().strip()
    except OSError as e:
        return "unparseable", "output file unreadable: %s" % e
    if txt.endswith(":"):
        txt = txt[:-1]
    txt = txt.replace("\n", "")
    try:
        data = ast.literal_eval(txt)
    except Exception as e:                            # noqa: BLE001
        return "unparseable", "output does not parse: %r" % (e,)
    if data == [-1] or data == -1:
        return "none", None
    if not isinstance(data, list) or not data:
        return "unparseable", "unexpected output structure"
    if data[0] != 0:
        return "positive_dimensional", "msolve output header %r (not a zero-dimensional parametrisation)" % (data[0],)
    try:
        body = data[1]
        char, nvars, deg, names, linform, param = body[0], body[1], body[2], body[3], body[4], body[5]
        elim, den, plist = param[1][0], param[1][1], param[1][2]
    except Exception as e:                            # noqa: BLE001
        return "unparseable", "zero-dimensional header but body does not parse: %r" % (e,)
    return "param", {"char": char, "nvars": nvars, "degree": deg, "varnames": names, "linform": linform,
                     "elim": elim, "den": den, "params": plist}


def rational_solutions(par, p, nvars):
    """F_p-rational solutions from msolve's rational parametrisation (v1 convention, verified in v1:
    x_i = -v_i(r) / (c_i * den(r)); the last variable is r when no linear form was added)."""
    w = flint.nmod_poly(par["elim"][1], p)
    den = flint.nmod_poly(par["den"][1], p)
    info = {"elim_degree": w.degree(), "elim_squarefree": None}
    try:
        g = w.gcd(w.derivative())
        info["elim_squarefree"] = g.degree() == 0
    except Exception:                                 # noqa: BLE001
        pass
    sols = []
    for r, _mult in w.roots():
        r = int(r)
        dn = int(den(r))
        if dn == 0:
            continue
        vals = []
        for entry in par["params"]:
            polyc = entry[0]
            cst = int(entry[1]) if len(entry) > 1 else 1
            v = flint.nmod_poly(polyc[1], p)
            vals.append((-int(v(r)) * pow(cst * dn, -1, p)) % p)
        if len(vals) == nvars - 1:
            vals.append(r % p)
        if len(vals) != nvars:
            info["arity_mismatch"] = (len(vals), nvars)
            continue
        sols.append(vals)
    return sols, info


def substitute(eqs, sol, p):
    """True iff every equation vanishes at the F_p point sol (R-5 substitution check)."""
    for eq in eqs:
        s = 0
        for a, c in eq.items():
            t = c
            for x, e in zip(sol, a):
                if e:
                    t = t * pow(x, e, p) % p
            s = (s + t) % p
        if s:
            return False
    return True


def classify_solve(rec, st, parse_kind, parse_payload, sol_info, n_sub_fail):
    """R-5 outcome for a solver child that exited. Returns (outcome, reason)."""
    if rec.get("outcome") != "ok":
        return rec.get("outcome"), None
    if st["positive_dimension_reported"] or parse_kind == "positive_dimensional":
        return "positive_dimensional", parse_payload or "msolve reported positive dimension"
    if parse_kind == "unparseable":
        return "positive_dimensional", "output does not parse as a zero-dimensional parametrisation: %s" % parse_payload
    if parse_kind == "param":
        if sol_info and sol_info.get("elim_squarefree") is False:
            return "degenerate_parametrisation", "eliminating polynomial is not square-free"
        D = st["dimension_of_quotient"]
        if sol_info and D is not None and sol_info.get("elim_degree") is not None and sol_info["elim_degree"] != D:
            return "degenerate_parametrisation", ("eliminating polynomial degree %s != quotient dimension %s "
                                                  "(the minimal polynomial is not square-free: non-radical ideal)" % (sol_info["elim_degree"], D))
        sq = st["fglm"].get("squarefree_degree")
        if sq is not None and st["dimension_of_quotient"] is not None and sq != st["dimension_of_quotient"] and parse_payload.get("degree") not in (None, sq):
            return "degenerate_parametrisation", "msolve reports square-free part degree %s != quotient dimension %s" % (sq, st["dimension_of_quotient"])
        if n_sub_fail:
            return "degenerate_parametrisation", "%d parsed solution(s) fail substitution into the descended system" % n_sub_fail
    return "ok", None


# ----------------------------------------------------------------------------- callgrind (fallback for C-1)
def callgrind_instructions(argv, workdir, tag, cap_bytes, timeout_s):
    """Run argv under valgrind --tool=callgrind (capped child); return total Ir and the largest
    inclusive Ir among functions whose name contains 'f4' (the F4 core), or a reason."""
    out = os.path.join(workdir, "%s.callgrind.out" % tag)
    vargv = [VALGRIND, "--tool=callgrind", "--callgrind-out-file=%s" % out] + list(argv)
    rec = run_child(vargv, os.path.join(workdir, "%s.callgrind.stdout" % tag), os.path.join(workdir, "%s.callgrind.stderr" % tag),
                    cap_bytes=cap_bytes, timeout_s=timeout_s, count_instructions=False)
    res = {"method": "valgrind callgrind (Ir)", "child": {k: rec.get(k) for k in ("outcome", "wall_seconds", "returncode", "rlimit_as_child_getrlimit", "peak_vm_bytes")},
           "label": "measured work proxy (instructions)"}
    if rec.get("outcome") != "ok" or not os.path.exists(out):
        res["instructions_user"] = None
        res["reason"] = "callgrind child outcome %s" % rec.get("outcome")
        return res
    total = None
    with open(out, errors="replace") as fh:
        for line in fh:
            if line.startswith("summary:") or line.startswith("totals:"):
                total = int(line.split()[1])
    res["instructions_user"] = total
    try:
        import subprocess
        ann = subprocess.run(["callgrind_annotate", "--inclusive=yes", out], capture_output=True, text=True, timeout=600).stdout
        best = None
        for line in ann.splitlines():
            m = re.match(r"^\s*([\d,]+)\s+\(\s*[\d.]+%\)\s+(.*)$", line) or re.match(r"^\s*([\d,]+)\s+(\S.*)$", line)
            if m and re.search(r"(?i)f4", m.group(2)):
                v = int(m.group(1).replace(",", ""))
                if best is None or v > best[0]:
                    best = (v, m.group(2).strip()[:200])
        res["f4_core_inclusive_Ir"] = best[0] if best else None
        res["f4_core_function"] = best[1] if best else None
        if best is None:
            res["f4_core_note"] = "no function whose name contains 'f4' in callgrind_annotate output"
    except Exception as e:                            # noqa: BLE001
        res["f4_core_inclusive_Ir"] = None
        res["f4_core_note"] = "callgrind_annotate failed: %r" % (e,)
    try:
        os.remove(out)
    except OSError:
        pass
    return res
