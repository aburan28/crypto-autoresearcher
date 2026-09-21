#!/usr/bin/env python3
"""f4_trace.py -- Semaev-commensurable F4 step-degree trace via msolve.

msolve (Berthomieu, Eder, Safey El Din) implements Faugere's F4 with pair
selection by degree: every round selects all critical pairs of the current
minimal degree, builds the Macaulay-type matrix, reduces it, and adds the new
basis elements.  With `-v 2` it prints one line per round:

    deg  sel  pairs  mat(rows x cols)  density  new  zero  time

`deg` is the degree of the pairs selected in that round -- the same quantity
MAGMA's F4 verbosity calls the "step degree" and Semaev reads d_F4 from
(KN-LIT-fa346d Section 4.5.1).  Two readings are recorded per run:

  d_F4_semaev : max of the input generators' degree and of `deg` over the rounds
                up to and including the LAST round that added at least one new
                basis element.  Rounds after it that add nothing are the "No
                pairs to reduce" tail Semaev excludes.  The input-degree floor is
                Semaev's own wording ("maximal total degree of the polynomials
                occurring before a Groebner basis is computed"): the generators
                occur, so a run whose every round adds nothing (a planted-point
                control) still reports the generators' degree, never nothing.
  d_F4_last_productive_round : the same without the floor (None if no round
                added anything).
  d_F4_naive  : max `deg` over every round, tail included.

Field equations are explicit generators (Section 4.5.1: "n(t-2)+kt field
equations are added"), so the convention is `explicit_generators`.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import resource
import signal
import subprocess
import threading
import time
from pathlib import Path

ROUND_RE = re.compile(r"^\s*(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+x\s+(\d+)\s+([\d.]+)%\s+(\d+)\s+new\s+(\d+)\s+zero\s+([\d.]+)\s*\|\s*([\d.]+)")
QUOT_RE = re.compile(r"Dimension of quotient:\s*(\d+)")
BASIS_RE = re.compile(r"#length of basis:\s*(\d+)")


def msolve_version() -> str:
    try:
        out = subprocess.run(["msolve", "-h"], capture_output=True, text=True, timeout=20)
        m = re.search(r"msolve\s+([\d.]+)", out.stdout + out.stderr)
        return m.group(1) if m else (out.stdout.splitlines() or ["?"])[0].strip()
    except Exception as exc:  # pragma: no cover
        return f"unknown ({exc})"


def _limits(mem_bytes: int):
    def fn():
        if mem_bytes:
            resource.setrlimit(resource.RLIMIT_AS, (mem_bytes, mem_bytes))
    return fn


def _drain(stream, sink):
    sink.append(stream.read())


def _communicate_wait4(proc, deadline: float):
    """Like Popen.communicate, but reaps the child with wait4 so the returned rusage is this
    child's own.  RUSAGE_CHILDREN.ru_maxrss is the high-water mark over EVERY child this
    process has ever waited for, so it would carry the heaviest earlier cell into every later
    record.  Returns (stdout, stderr, timed_out, rusage)."""
    outs, errs = [], []
    readers = [threading.Thread(target=_drain, args=(proc.stdout, outs)),
               threading.Thread(target=_drain, args=(proc.stderr, errs))]
    for th in readers:
        th.start()
    for th in readers:
        th.join(max(0.0, deadline - time.time()))
    timed_out = any(th.is_alive() for th in readers)
    if timed_out:
        # os.kill, not proc.kill(): the latter polls, and polling would reap the child
        # before wait4 can read its rusage.
        try:
            os.kill(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        for th in readers:
            th.join()
    proc.stdout.close()
    proc.stderr.close()
    _, status, ru = os.wait4(proc.pid, 0)
    proc.returncode = os.waitstatus_to_exitcode(status)
    return "".join(outs), "".join(errs), timed_out, ru


def read_d_f4(rounds: list, input_max_degree: int | None):
    """The three readings from a raw round table; used by run_msolve and by
    summarize.py to re-read records whose raw rounds were stored."""
    d_naive = max((r["deg"] for r in rounds), default=None)
    last_prod = max((i for i, r in enumerate(rounds) if r["new"] > 0), default=None)
    d_lpr = max((r["deg"] for r in rounds[: last_prod + 1]), default=None) if last_prod is not None else None
    floor = input_max_degree or 0
    d_sem = max(d_lpr or 0, floor) if (d_lpr is not None or input_max_degree is not None) else None
    tail = [r["deg"] for r in rounds[(last_prod + 1 if last_prod is not None else 0):]]
    return d_sem, d_lpr, d_naive, tail


def gb_quotient_dimension(gb_path: Path, var_names, cap: int = 200000):
    """|V(I)| from msolve's reduced Groebner basis file: the field equations are
    in the ideal, so the quotient's monomial basis is the set of squarefree
    monomials not divisible by any squarefree leading monomial of the basis
    (leading monomials with a square divide no squarefree monomial). msolve
    prints each polynomial with its leading term first (DRL). Returns
    (count, note); count is None if the basis cannot be read, cap+1 if the
    count exceeds cap, 0 for the unit ideal."""
    try:
        txt = Path(gb_path).read_text()
    except OSError as exc:
        return None, f"unreadable: {exc}"
    body = txt[txt.index("["):] if "[" in txt else ""
    body = body.strip().lstrip("[").rstrip(":").rstrip("]")
    polys = [p.strip() for p in body.split(",\n")] if body else []
    if not polys:
        return None, "no basis in file"
    idx = {v: i for i, v in enumerate(var_names)}
    lms = []
    for p in polys:
        p = p.strip()
        if p == "1":
            return 0, "unit ideal"
        lead = p.split("+")[0].strip()
        mask, square = 0, False
        for factor in lead.split("*"):
            factor = factor.strip()
            if factor.isdigit():
                continue
            name, _, exp = factor.partition("^")
            if name not in idx:
                return None, f"unknown variable {name}"
            if exp and int(exp) >= 2:
                square = True
            mask |= 1 << idx[name]
        if not square:
            lms.append(mask)
    if 0 in lms:
        return 0, "unit ideal"
    N = len(var_names)
    by_hb = {}
    for l in lms:
        by_hb.setdefault(l.bit_length() - 1, []).append(l)
    count = 1
    queue = [0]
    while queue:
        m = queue.pop()
        start = m.bit_length()
        for j in range(start, N):
            m2 = m | (1 << j)
            if any((l & ~m2) == 0 for l in by_hb.get(j, ())):
                continue
            count += 1
            if count > cap:
                return cap + 1, f"exceeds cap {cap}"
            queue.append(m2)
    return count, f"standard squarefree monomials of {len(lms)} squarefree leading terms"


def run_msolve(ms_path: Path, out_path: Path, wall_cap_s: float, mem_cap_gb: float,
               threads: int = 1, input_max_degree: int | None = None) -> dict:
    # -u 1: regenerate the basis hash table after every F4 step.  Without it
    # msolve keeps every monomial ever hashed (exponent vectors of length N),
    # and on the N = 40 cell (19,3,3,7) the table grew past 2^26 entries under a
    # 6 GB cap and msolve segfaulted ("Enlarging hash table failed").  The
    # regeneration is garbage collection only: the pair selection, the
    # per-round matrices and the step degrees are unchanged.
    cmd = ["msolve", "-v", "2", "-g", "2", "-t", str(threads), "-u", "1", "-f", str(ms_path), "-o", str(out_path)]
    t0 = time.time()
    status = "completed"
    stdout = ""
    stderr = ""
    rc = None
    peak_rss = None
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                preexec_fn=_limits(int(mem_cap_gb * (1 << 30))))
        stdout, stderr, timed_out, ru = _communicate_wait4(proc, t0 + wall_cap_s)
        rc = proc.returncode
        if timed_out:
            status = "unreached_wall_cap"
        peak_rss = ru.ru_maxrss * 1024
    except Exception as exc:
        status = "launch_error"
        stderr = repr(exc)
    wall = time.time() - t0
    if status == "completed" and rc not in (0,):
        blob = (stderr + stdout).lower()
        if ("alloc" in blob or "hash table failed" in blob or "enlarging" in blob or rc in (-9, -11, 134, 137)):
            status = "unreached_memory_cap"
        else:
            status = f"failed_rc_{rc}"
    rounds = []
    for line in stdout.splitlines():
        m = ROUND_RE.match(line)
        if m:
            rounds.append({
                "deg": int(m.group(1)), "sel": int(m.group(2)), "pairs": int(m.group(3)),
                "rows": int(m.group(4)), "cols": int(m.group(5)), "density_pct": float(m.group(6)),
                "new": int(m.group(7)), "zero": int(m.group(8)),
                "real_s": float(m.group(9)), "cpu_s": float(m.group(10)),
            })
    quot = QUOT_RE.search(stdout)
    quotient_dim = int(quot.group(1)) if quot else None
    basis_len = None
    basis_is_unit = None
    quotient_source = "msolve 'Dimension of quotient' line"
    if out_path.exists():
        txt = out_path.read_text()
        mb = BASIS_RE.search(txt)
        basis_len = int(mb.group(1)) if mb else None
        basis_is_unit = ("[1]:" in txt) and (basis_len == 1)
        if basis_is_unit:
            quotient_dim = 0
        elif quotient_dim is None and status == "completed" and basis_len:
            names = ms_path.read_text().splitlines()[0].split(",")
            qd, note = gb_quotient_dimension(out_path, names)
            if qd is not None and qd <= 200000:
                quotient_dim = qd
                quotient_source = f"reduced basis file: {note}"
    d_semaev, d_lpr, d_naive, tail = read_d_f4(rounds, input_max_degree)
    return {
        "engine": "msolve", "engine_version": msolve_version(), "command": " ".join(cmd),
        "field_equation_convention": "explicit_generators",
        "status": status, "exit_code": rc, "wall_s": wall, "peak_rss_bytes": peak_rss,
        "rounds": rounds, "f4_step_count": len(rounds),
        "d_F4_semaev": d_semaev if status == "completed" else None,
        "d_F4_last_productive_round": d_lpr if status == "completed" else None,
        "d_F4_naive": d_naive if status == "completed" else None,
        "input_max_degree": input_max_degree,
        "d_F4_partial_max_deg_seen": d_naive,
        "f4_empty_step_degrees": tail if status == "completed" else None,
        "quotient_dimension": quotient_dim if status == "completed" else None,
        "quotient_dimension_source": quotient_source if (status == "completed" and quotient_dim is not None) else None,
        "basis_length": basis_len, "ideal_is_unit": basis_is_unit,
        "stdout_sha256": hashlib.sha256(stdout.encode()).hexdigest(),
        "stdout": stdout, "stderr": stderr[-4000:],
    }
