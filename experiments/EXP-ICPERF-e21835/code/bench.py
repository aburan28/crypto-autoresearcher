#!/usr/bin/env python3
"""EXP-ICPERF-66fd51 harness: measure every declared engine on every shipped Trimoska
S_4 PDP instance, certify every SAT answer against the curve, and write results
incrementally so a watchdog stop leaves a partial artifact rather than nothing.

Usage:
  python3 bench.py --run-dir RUNDIR [--phases A,B,C,D,E] [--dry-run]

Phases (ordered so a stop leaves the most valuable data first):
  A  certificates for all 30 S instances; WDSat default / core-order / symmetry / GE on all
     60 instances; WDSat default on matched random null objects for 3 S + 3 U templates per cell
  B  CryptoMiniSat on the CNF-XOR form, all 60
  C  Macaulay2 F4 (ZZ/2 + field equations): all 20 n15l5; 3 S + 3 U per l=6 cell
  D  CryptoMiniSat / CaDiCaL / MiniSat on the pure-CNF form (regenerated with the vendored
     XORtoCNF.sh and hash-checked against the upstream manifest): 5 S + 5 U per cell
  E  Singular std (GF(2) + field equations): 2 S + 2 U of n15l5

Every engine invocation is a child process under a wall-clock timeout and a RESIDENT-SET
watchdog over the child's process group; wall, CPU (user+sys), peak RSS, exit status,
stdout/stderr paths and the 1-minute load average at launch are recorded per run in
results.jsonl.

Successor tree of EXP-ICPERF-66fd51/code/bench.py (EXP-ICPERF-e21835): repairs D2
(RLIMIT_AS replaced by an 8 GiB resident-set watchdog), D4 (the version probe returns
under inherited stdin) and D5 (per-engine solver statistics on the pure-CNF rows).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import resource
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
BENCH = REPO / "inputs/TRIMOSKA-ECICB-2024/upstream/benchmarks"
XOR2CNF = REPO / "inputs/TRIMOSKA-ECICB-2024/upstream/XORtoCNF.sh"
UPSTREAM_SUMS = REPO / "inputs/TRIMOSKA-ECICB-2024/UPSTREAM_SHA256SUMS.txt"
WDSAT_SRC = REPO / "inputs/TRIMOSKA-WDSAT-2024/upstream/src"

sys.path.insert(0, str(HERE))
from binec import InfoFile, bits_to_int  # noqa: E402
from convert import (_parse_anf_equation, anf_null_object, anf_shape, magma_to_m2,  # noqa: E402
                     magma_to_singular, parse_anf_header)

CELLS = [(15, 5), (17, 6), (19, 6)]
M = 3  # factor-base points per decomposition (generator's m-1)
# D2: the memory limit is a RESIDENT-SET limit enforced by a watchdog over the child's
# process group.  RLIMIT_AS is set nowhere: it caps virtual address space, which a
# garbage-collected algebra system reserves far in excess of what it makes resident
# (measured 145.4 GiB reserved against 6.8 GiB resident), so it aborted rows that were
# using well under half the memory they were allowed.  A row this watchdog kills is a
# budget stop with its limit recorded, never negative evidence.
RSS_LIMIT_GB = 8
RSS_POLL_INTERVAL_S = 0.25
RSS_KILL_GRACE_S = 5.0
PAGE_KB = os.sysconf("SC_PAGE_SIZE") // 1024
VERSION_PROBE_TIMEOUT_S = 10
TIMEOUTS = {"wdsat": 600, "wdsat_null": 180, "wdsat_noncore": 120, "cms_xor": 300, "m2_f4_l5": 600,
            "m2_f4_l6": 1800, "cnf_generic": 300, "singular_std": 900}
NONCORE_PER_LABEL = 5  # noncore_first runs on the first 5 S + 5 U of each cell
NULL_SEED_BASE = 20260913


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


# D2: resident-set watchdog primitives.  RSS is summed over the child's whole process
# group, because Macaulay2's F4 spawns its own threads and an engine may fork helpers.
def pgid_rss_kb(pgid: int) -> int:
    """Sum VmRSS over every live process in process group `pgid`, in KB."""
    total = 0
    for entry in os.listdir("/proc"):
        if not entry.isdigit():
            continue
        try:
            data = open(f"/proc/{entry}/stat", "rb").read()
            # comm may contain spaces and parentheses: fields resume after the last ')'
            rest = data[data.rindex(b")") + 2:].split()
            if int(rest[2]) != pgid:  # rest = state ppid pgrp ...
                continue
            total += int(open(f"/proc/{entry}/statm", "rb").read().split()[1]) * PAGE_KB
        except (OSError, ValueError, IndexError):
            continue
    return total


def kill_group(pgid: int, proc: "subprocess.Popen", grace: float = RSS_KILL_GRACE_S) -> None:
    """SIGTERM then SIGKILL the whole process group; never leave a survivor holding memory."""
    for sig in (signal.SIGTERM, signal.SIGKILL):
        try:
            os.killpg(pgid, sig)
        except (ProcessLookupError, PermissionError):
            pass
        try:
            proc.wait(timeout=grace)
            return
        except subprocess.TimeoutExpired:
            continue
    try:
        proc.wait(timeout=grace)
    except subprocess.TimeoutExpired:
        pass


def instances():
    for n, l in CELLS:
        for i in range(1, 21):
            label = "S" if i <= 10 else "U"
            yield {"n": n, "l": l, "id": i, "label": label, "cell": f"n{n}l{l}",
                   "stem": f"n{n}l{l}-{i}-{label}",
                   "info": BENCH / f"INFOn{n}l{l}-{i}-{label}.dimacs",
                   "anf": BENCH / f"Xn{n}l{l}-{i}-{label}.anf",
                   "xor": BENCH / f"Xn{n}l{l}-{i}-{label}.dimacs",
                   "magma": BENCH / f"n{n}l{l}-{i}-{label}.in"}


def subset(insts, per_label):
    out = []
    for cell in {i["cell"] for i in insts}:
        for lab in ("S", "U"):
            out += [i for i in insts if i["cell"] == cell and i["label"] == lab][:per_label]
    return sorted(out, key=lambda i: (i["n"], i["id"]))


class Runner:
    def __init__(self, run_dir: Path, dry: bool):
        self.run_dir = run_dir
        self.dry = dry
        self.logs = run_dir / "logs"
        self.logs.mkdir(parents=True, exist_ok=True)
        self.results = run_dir / "results.jsonl"
        self.done = set()
        if self.results.exists():
            for ln in self.results.read_text().splitlines():
                try:
                    r = json.loads(ln)
                    self.done.add((r["instance"], r["engine"], r["config"]))
                except Exception:
                    pass

    def record(self, rec: dict):
        rec["recorded_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        with open(self.results, "a") as f:
            f.write(json.dumps(rec, sort_keys=True) + "\n")
        self.done.add((rec["instance"], rec["engine"], rec["config"]))

    def already(self, inst, engine, config) -> bool:
        return (inst, engine, config) in self.done

    def run(self, argv, tag: str, timeout: int, stdin_path: Path | None = None) -> dict:
        """Run argv as a child under a wall-clock timeout and a RESIDENT-SET watchdog.

        D2: RLIMIT_AS is not set.  The child gets its own session (so its process group
        can be polled and killed as a unit); the watchdog polls the group's summed VmRSS
        every RSS_POLL_INTERVAL_S seconds and kills the group when the sum exceeds
        RSS_LIMIT_GB.  peak_rss_kb is the largest sum the watchdog OBSERVED, so it is
        accurate only to the polling interval; a breach is therefore recorded together
        with the limit and the interval and never presented as an exact peak.
        """
        out_p, err_p = self.logs / f"{tag}.out", self.logs / f"{tag}.err"
        if self.dry:
            return {"dry_run": True, "argv": argv}
        before = resource.getrusage(resource.RUSAGE_CHILDREN)
        load1 = os.getloadavg()[0]
        limit_kb = RSS_LIMIT_GB * (1 << 20)
        t0 = time.monotonic()
        timed_out = False
        breached = False
        peak_kb = 0
        polls = 0
        with open(out_p, "wb") as fo, open(err_p, "wb") as fe:
            stdin = open(stdin_path, "rb") if stdin_path else subprocess.DEVNULL
            try:
                p = subprocess.Popen(argv, stdout=fo, stderr=fe, stdin=stdin,
                                     start_new_session=True)
            finally:
                if stdin_path:
                    stdin.close()
            pgid = p.pid  # start_new_session makes the child its own group leader
            while True:
                rc = p.poll()
                rss = pgid_rss_kb(pgid)
                polls += 1
                peak_kb = max(peak_kb, rss)
                if rc is not None:
                    break
                if rss > limit_kb:
                    breached = True
                    kill_group(pgid, p)
                    rc = p.returncode
                    break
                if time.monotonic() - t0 > timeout:
                    timed_out = True
                    kill_group(pgid, p)
                    rc = None
                    break
                try:
                    rc = p.wait(timeout=min(RSS_POLL_INTERVAL_S,
                                            timeout - (time.monotonic() - t0)))
                except subprocess.TimeoutExpired:
                    continue
                break
        wall = time.monotonic() - t0
        after = resource.getrusage(resource.RUSAGE_CHILDREN)
        return {"argv": argv, "wall_s": round(wall, 4), "timed_out": timed_out, "returncode": rc,
                "cpu_s": round((after.ru_utime - before.ru_utime) + (after.ru_stime - before.ru_stime), 4),
                "max_rss_kb_children_highwater": after.ru_maxrss,
                "peak_rss_kb": peak_kb, "rss_limit_gb": RSS_LIMIT_GB,
                "rss_limit_breached": breached, "rss_poll_interval_s": RSS_POLL_INTERVAL_S,
                "rss_polls": polls, "rss_source": "sum of VmRSS over the child's process group",
                "loadavg1_at_start": round(load1, 2), "timeout_s": timeout,
                "stdout": str(out_p.relative_to(self.run_dir)), "stderr": str(err_p.relative_to(self.run_dir))}


# ----------------------------------------------------------------------------- WDSat

def anf_sizing(anf_path: Path) -> dict:
    src = anf_path.read_text()
    nv, ne = parse_anf_header(src)
    monos, maxdeg, maxterms = set(), 1, 0
    for ln in src.splitlines():
        t = ln.split()
        if t and t[0] == "x":
            terms, _ = _parse_anf_equation(t[1:-1])
            maxterms = max(maxterms, len(terms))
            for m in terms:
                if len(m) > 1:
                    monos.add(tuple(m))
                    maxdeg = max(maxdeg, len(m))
    max_id = nv + len(monos)
    return {"MAX_ANF_ID": nv + 1, "MAX_DEGREE": maxdeg + 1, "MAX_ID": max_id,
            "MAX_EQ": sum(len(m) + 1 for m in monos) + 64, "MAX_EQ_SIZE": maxdeg + 2,
            "MAX_XEQ": ne + 1, "MAX_XEQ_SIZE": max_id, "n_unary": nv, "n_eqs": ne,
            "n_nonunary_monomials": len(monos), "max_terms_per_eq": maxterms}


def build_wdsat(run_dir: Path, sizing: dict, buffer_size: int) -> Path:
    """Build WDSat from the vendored source with an exact static configuration."""
    consts = {k: sizing[k] for k in ("MAX_ANF_ID", "MAX_DEGREE", "MAX_ID", "MAX_EQ", "MAX_EQ_SIZE", "MAX_XEQ", "MAX_XEQ_SIZE")}
    consts["MAX_BUFFER_SIZE"] = buffer_size
    sig = "_".join(f"{k}{v}" for k, v in sorted(consts.items()))
    bdir = run_dir / "builds" / f"wdsat_{hashlib.sha1(sig.encode()).hexdigest()[:10]}"
    exe = bdir / "wdsat_solver"
    if exe.exists():
        return exe
    shutil.copytree(WDSAT_SRC, bdir / "src")
    cfg = bdir / "src" / "config.h"
    text = cfg.read_text()
    # Replace the single active (uncommented) block: every '#define __X__ value' line that is
    # not inside a /* ... */ comment.  We rewrite by removing all active defines of the sized
    # constants and appending our own block; the XG_ENHANCED switch is left as shipped.
    out = []
    in_comment = False
    for ln in text.splitlines():
        stripped = ln.strip()
        if in_comment:
            out.append(ln)
            if "*/" in stripped:
                in_comment = False
            continue
        if stripped.startswith("/*") and "*/" not in stripped:
            in_comment = True
            out.append(ln)
            continue
        m = re.match(r"#define __(\w+)__\s", stripped)
        if m and m.group(1) in consts:
            continue
        out.append(ln)
    out.append("/* EXP-ICPERF-66fd51 exact sizing (derived from the instance ANF) */")
    for k, v in consts.items():
        out.append(f"#define __{k}__ {v}")
    cfg.write_text("\n".join(out) + "\n")
    (bdir / "config_used.json").write_text(json.dumps(consts, indent=1))
    log = subprocess.run(["make"], cwd=bdir / "src", capture_output=True, text=True)
    (bdir / "make.log").write_text(log.stdout + "\n--- stderr ---\n" + log.stderr)
    if log.returncode != 0 or not exe.exists():
        raise RuntimeError(f"WDSat build failed in {bdir}")
    return exe


def parse_wdsat(out_text: str) -> dict:
    lines = [ln.strip() for ln in out_text.splitlines() if ln.strip()]
    res = {"status": "unknown", "conflicts": None, "assignment": None, "solver_notes": []}
    for ln in lines:
        if ln.startswith("!!!"):
            res["solver_notes"].append(ln)
    if any(ln.startswith("UNSAT") for ln in lines):
        res["status"] = "UNSAT"
        idx = max(i for i, ln in enumerate(lines) if ln.startswith("UNSAT"))
        if idx + 1 < len(lines) and lines[idx + 1].lstrip("-").isdigit():
            res["conflicts"] = int(lines[idx + 1])
        return res
    bitlines = [i for i, ln in enumerate(lines) if re.fullmatch(r"[01]{8,}", ln)]
    if bitlines:
        i = bitlines[-1]
        res["status"] = "SAT"
        res["assignment"] = lines[i]
        if i + 1 < len(lines) and lines[i + 1].lstrip("-").isdigit():
            res["conflicts"] = int(lines[i + 1])
    return res


def verify_assignment_bits(info: InfoFile, bits: str) -> dict:
    """Interpret the first m*l bits as x_1 | x_2 | x_3 (low-degree-first) and check on the curve."""
    ml = M * info.l
    if len(bits) < ml:
        return {"verified": False, "why": "assignment shorter than m*l"}
    xs = tuple(bits[k * info.l:(k + 1) * info.l] for k in range(M))
    ok, why = info.check_certificate(xs)
    return {"verified": ok, "why": why, "x_bits": list(xs),
            "matches_shipped_certificate_as_set": (info.cert_bits is not None and sorted(xs) == sorted(info.cert_bits))}


def parse_dimacs_model(out_text: str) -> dict:
    status = "unknown"
    vals = {}
    for ln in out_text.splitlines():
        if ln.startswith("s "):
            if "UNSAT" in ln:
                status = "UNSAT"
            elif "SAT" in ln:
                status = "SAT"
        elif ln.startswith("v "):
            for t in ln.split()[1:]:
                v = int(t)
                if v != 0:
                    vals[abs(v)] = 1 if v > 0 else 0
    return {"status": status, "vals": vals}


# D5: each engine prints its own solver-statistics block in its own format, so a single
# CryptoMiniSat-shaped pattern recorded counters for one engine of three.  CaDiCaL prints
# them only when not run with -q, and MiniSat only at verbosity >= 1; both flags are set
# in phase_D.  An engine that still emits no counter gets a recorded reason, never a
# silently absent field.
SOLVER_STAT_PATTERNS = {
    "cryptominisat5": r"^c\s+(conflicts|decisions|propagations)\s*:\s*(\d+)",
    "cadical": r"^c\s+(conflicts|decisions|propagations)\s*:\s*(\d+)",
    "minisat": r"^(conflicts|decisions|propagations)\s*:\s*(\d+)",
}


def parse_solver_stats(engine: str, err_text: str, out_text: str) -> dict:
    pattern = SOLVER_STAT_PATTERNS.get(engine)
    if pattern is None:
        return {}
    stats = {}
    for ln in (out_text + "\n" + err_text).splitlines():
        m = re.match(pattern, ln.strip() if engine == "minisat" else ln)
        if m:
            stats[m.group(1)] = int(m.group(2))
    return stats


def model_bits(vals: dict, ml: int) -> str:
    return "".join(str(vals.get(i, 0)) for i in range(1, ml + 1))


# ----------------------------------------------------------------------------- phases

def phase_A(R: Runner, insts):
    # A.1 certificates (independent arithmetic)
    for inst in insts:
        info = InfoFile.parse(inst["info"])
        if inst["label"] == "S" and not R.already(inst["stem"], "certificate", "shipped"):
            ok, why = info.check_certificate()
            R.record({"phase": "A", "instance": inst["stem"], "cell": inst["cell"], "label": inst["label"],
                      "engine": "certificate", "config": "shipped", "verified": ok, "why": why,
                      "certificate": list(info.cert_bits)})
    # A.2 WDSat four configurations on every instance
    # core_order is a prefix of WDSat's default order (1..N), so it must match
    # default exactly: it is the identity check on the -g wiring (P3a).
    # noncore_first is the real order control (P3b): a full permutation with the
    # N-ml e-variables ahead of the ml core variables, so the search stays
    # complete but propagation from the core is lost.
    configs = {
        "default": lambda inst, s: [],
        "core_order": lambda inst, s: ["-g", ",".join(str(i) for i in range(1, M * inst["l"] + 1))],
        "noncore_first": lambda inst, s: ["-g", ",".join(
            str(i) for i in list(range(M * inst["l"] + 1, s["n_unary"] + 1)) + list(range(1, M * inst["l"] + 1)))],
        "symmetry": lambda inst, s: ["-b", "-m", str(M), "-l", str(inst["l"])],
        "gauss_elim": lambda inst, s: ["-x"],
    }
    # noncore_first pilots (pre-run smoke) took 2 s / 109 s / >300 s where default took
    # 0.005 s / 0.2 s / 2.3 s, so it runs on a 5+5 subset per cell under its own
    # timeout; its timeouts are right-censored lower bounds, which summary.py uses.
    noncore_stems = {i["stem"] for i in subset(insts, NONCORE_PER_LABEL)}
    for inst in insts:
        info = InfoFile.parse(inst["info"])
        sizing = anf_sizing(inst["anf"])
        for cname, extra in configs.items():
            if R.already(inst["stem"], "wdsat", cname):
                continue
            if cname == "noncore_first" and inst["stem"] not in noncore_stems:
                continue
            to = TIMEOUTS["wdsat_noncore"] if cname == "noncore_first" else None
            rec = run_wdsat(R, inst["anf"], sizing, extra(inst, sizing), f"wdsat_{cname}_{inst['stem']}", timeout=to)
            rec.update({"phase": "A", "instance": inst["stem"], "cell": inst["cell"], "label": inst["label"],
                        "engine": "wdsat", "config": cname})
            if rec.get("status") == "SAT":
                rec["verification"] = verify_assignment_bits(info, rec["assignment"])
            R.record(rec)
    # A.3 matched random null objects, WDSat default: 3 S + 3 U templates per cell
    # (smoke runs showed 35-600+ s per null object against <3 s structured; the
    # timeout is a recorded budget stop and a LOWER BOUND, never a measurement)
    null_dir = R.run_dir / "null_objects"
    null_dir.mkdir(exist_ok=True)
    for inst in subset(insts, 3):
        if R.already(inst["stem"], "wdsat", "default_on_null_object"):
            continue
        seed = NULL_SEED_BASE * 1000 + inst["n"] * 100 + inst["id"]
        src = inst["anf"].read_text()
        null_src = anf_null_object(src, seed)
        null_p = null_dir / f"NULL-{inst['stem']}.anf"
        null_p.write_text(null_src)
        shape_ok = anf_shape(src) == anf_shape(null_src)
        sizing = anf_sizing(null_p)
        rec = run_wdsat(R, null_p, sizing, [], f"wdsat_null_{inst['stem']}", timeout=TIMEOUTS["wdsat_null"])
        rec.update({"phase": "A", "instance": inst["stem"], "cell": inst["cell"], "label": inst["label"],
                    "engine": "wdsat", "config": "default_on_null_object", "null_seed": seed,
                    "null_object": str(null_p.relative_to(R.run_dir)), "shape_matches_template": shape_ok,
                    "null_sizing": sizing})
        R.record(rec)


def run_wdsat(R: Runner, anf: Path, sizing: dict, extra: list, tag: str, timeout: int | None = None) -> dict:
    buffer_size = 60000
    timeout = timeout or TIMEOUTS["wdsat"]
    for attempt in range(4):
        exe = build_wdsat(R.run_dir, sizing, buffer_size)
        m = R.run([str(exe), "-i", str(anf)] + extra, tag, timeout)
        if R.dry:
            return m
        out = (R.run_dir / m["stdout"]).read_text(errors="replace")
        err = (R.run_dir / m["stderr"]).read_text(errors="replace")
        if "__MAX_BUFFER_SIZE__" in err and not m["timed_out"]:
            buffer_size *= 2
            continue
        parsed = parse_wdsat(out)
        m.update(parsed)
        m["wdsat_build"] = str(exe.parent.relative_to(R.run_dir))
        m["wdsat_constants"] = json.loads((exe.parent / "config_used.json").read_text())
        m["stderr_head"] = err[:300]
        if m["timed_out"]:
            m["status"] = "budget_stop_timeout"
        elif m.get("rss_limit_breached"):
            # D2: an honest resident-set limit is expected to kill rows; it is a budget
            # stop with its limit recorded, never negative evidence about the engine.
            m["status"] = "budget_stop_rss_limit"
        elif m["returncode"] not in (0, 1) and m["status"] == "unknown":
            m["status"] = f"infrastructure_exit_{m['returncode']}"
        return m
    m["status"] = "infrastructure_buffer_sizing_failed"
    return m


def phase_B(R: Runner, insts):
    for inst in insts:
        if R.already(inst["stem"], "cryptominisat5", "cnf_xor"):
            continue
        info = InfoFile.parse(inst["info"])
        m = R.run(["cryptominisat5", "--verb", "1", str(inst["xor"])], f"cms_xor_{inst['stem']}", TIMEOUTS["cms_xor"])
        m.update({"phase": "B", "instance": inst["stem"], "cell": inst["cell"], "label": inst["label"],
                  "engine": "cryptominisat5", "config": "cnf_xor"})
        finish_dimacs_record(R, m, info, inst)
        R.record(m)


def finish_dimacs_record(R: Runner, m: dict, info: InfoFile, inst: dict):
    if R.dry:
        return
    out = (R.run_dir / m["stdout"]).read_text(errors="replace")
    err = (R.run_dir / m["stderr"]).read_text(errors="replace")
    parsed = parse_dimacs_model(out)
    if m["timed_out"]:
        m["status"] = "budget_stop_timeout"
    elif m.get("rss_limit_breached"):  # D2
        m["status"] = "budget_stop_rss_limit"
    else:
        m["status"] = parsed["status"]
    m["stats"] = parse_solver_stats(m.get("engine", ""), err, out)  # D5
    if not m["stats"]:  # D5
        m["stats_unavailable_reason"] = (
            f"{m.get('engine')}: no conflict/decision/propagation counter matched its"
            f" statistics pattern in stdout or stderr"
            f" (status={m.get('status')}, returncode={m.get('returncode')},"
            f" timed_out={m.get('timed_out')}, argv={' '.join(m.get('argv', []))})")
    if parsed["status"] == "SAT":
        bits = model_bits(parsed["vals"], M * inst["l"])
        m["assignment_core_bits"] = bits
        m["verification"] = verify_assignment_bits(info, bits)


def pure_cnf(R: Runner, inst: dict) -> Path:
    """Regenerate the pure-CNF form with the vendored XORtoCNF.sh and hash-check it."""
    cdir = R.run_dir / "pure_cnf"
    cdir.mkdir(exist_ok=True)
    target = cdir / f"{inst['stem']}.dimacs"
    if target.exists():
        return target
    work = cdir / f"work_{inst['stem']}"
    work.mkdir(exist_ok=True)
    nvars = int(inst["xor"].read_text().splitlines()[0].split()[2])
    offset = subprocess.run(["bash", str(XOR2CNF), str(nvars), str(inst["xor"])], cwd=work,
                            capture_output=True, text=True, check=True).stdout.strip().splitlines()[-1]
    norm = (work / "F_3_norm.dimacs").read_text().splitlines()
    new_nvars = int(offset) - 1
    new_nlines = len(norm) - 1
    target.write_text(f"p cnf {new_nvars} {new_nlines}\n" + "\n".join(norm[1:]) + "\n")
    shutil.rmtree(work)
    expected = None
    for ln in UPSTREAM_SUMS.read_text().splitlines():
        h, p = ln.split(None, 1)
        if p.strip() == f"./benchmarks/{inst['stem']}.dimacs":
            expected = h
    (cdir / f"{inst['stem']}.hashcheck.json").write_text(json.dumps(
        {"regenerated_sha256": sha256(target), "upstream_sha256": expected, "match": sha256(target) == expected}))
    return target


def phase_D(R: Runner, insts):
    sub = subset(insts, 5)
    # D5: -q suppressed CaDiCaL's statistics block and -verb=0 suppressed MiniSat's, so
    # neither engine could report a conflict count.  Both now run at the verbosity that
    # prints their own counters; the CNF, the timeout and the watchdog are unchanged.
    engines = {"cryptominisat5": lambda p: ["cryptominisat5", "--verb", "1", str(p)],
               "cadical": lambda p: ["cadical", str(p)],
               "minisat": lambda p: ["minisat", "-verb=1", str(p), "MODEL_OUT"]}
    for inst in sub:
        info = InfoFile.parse(inst["info"])
        cnf = pure_cnf(R, inst)
        hc = json.loads((cnf.parent / f"{inst['stem']}.hashcheck.json").read_text())
        for ename, mk in engines.items():
            if R.already(inst["stem"], ename, "pure_cnf"):
                continue
            argv = mk(cnf)
            model_out = None
            if "MODEL_OUT" in argv:
                model_out = R.logs / f"{ename}_cnf_{inst['stem']}.model"
                argv = [model_out.__str__() if a == "MODEL_OUT" else a for a in argv]
            m = R.run(argv, f"{ename}_cnf_{inst['stem']}", TIMEOUTS["cnf_generic"])
            m.update({"phase": "D", "instance": inst["stem"], "cell": inst["cell"], "label": inst["label"],
                      "engine": ename, "config": "pure_cnf", "pure_cnf_hashcheck": hc})
            if model_out is not None and model_out.exists() and not R.dry:
                # minisat writes "SAT\n<lits> 0" or "UNSAT" to the model file
                txt = model_out.read_text()
                lines = txt.splitlines()
                fake = ("s SATISFIABLE\nv " + lines[1] + "\n") if lines and lines[0].startswith("SAT") else "s UNSATISFIABLE\n"
                (R.run_dir / m["stdout"]).write_text(fake + "\n--- original stdout ---\n" + (R.run_dir / m["stdout"]).read_text())
            finish_dimacs_record(R, m, info, inst)
            if ename == "cadical" and m.get("status") == "unknown" and not m["timed_out"] and not R.dry:
                # cadical -q prints s/v lines; if suppressed, fall back on exit code 10/20
                m["status"] = {10: "SAT", 20: "UNSAT"}.get(m["returncode"], "unknown")
            R.record(m)


def phase_C(R: Runner, insts):
    plan = [i for i in insts if i["cell"] == "n15l5"] + subset([i for i in insts if i["l"] == 6], 3)
    sdir = R.run_dir / "scripts"
    sdir.mkdir(exist_ok=True)
    for inst in plan:
        if R.already(inst["stem"], "macaulay2_F4_ZZ2_fieldeqs", "grevlex"):
            continue
        script = sdir / f"{inst['stem']}.m2"
        script.write_text(magma_to_m2(inst["magma"].read_text(), "F4"))
        to = TIMEOUTS["m2_f4_l5"] if inst["l"] == 5 else TIMEOUTS["m2_f4_l6"]
        m = R.run(["M2", "--script", str(script)], f"m2_{inst['stem']}", to)
        m.update({"phase": "C", "instance": inst["stem"], "cell": inst["cell"], "label": inst["label"],
                  "engine": "macaulay2_F4_ZZ2_fieldeqs", "config": "grevlex", "script": str(script.relative_to(R.run_dir))})
        if not R.dry:
            out = (R.run_dir / m["stdout"]).read_text(errors="replace") + (R.run_dir / m["stderr"]).read_text(errors="replace")
            g = re.search(r"RESULT gb_size=(\d+) cpu_s=([\d.]+) maxdeg_gb=(\d+) is_unit=(true|false)", out)
            if m["timed_out"]:
                m["status"] = "budget_stop_timeout"
            elif m.get("rss_limit_breached") and not g:  # D2
                m["status"] = "budget_stop_rss_limit"
            elif g:
                m.update({"gb_size": int(g.group(1)), "engine_cpu_s": float(g.group(2)), "maxdeg_gb": int(g.group(3)),
                          "unit_ideal": g.group(4) == "true"})
                m["status"] = "UNSAT_certified_unit_ideal" if m["unit_ideal"] else "consistent_proper_ideal"
            else:
                m["status"] = f"infrastructure_exit_{m['returncode']}"
        R.record(m)


def phase_E(R: Runner, insts):
    plan = subset([i for i in insts if i["cell"] == "n15l5"], 2)
    sdir = R.run_dir / "scripts"
    sdir.mkdir(exist_ok=True)
    for inst in plan:
        if R.already(inst["stem"], "singular_std_GF2_fieldeqs", "dp"):
            continue
        script = sdir / f"{inst['stem']}.sing"
        script.write_text(magma_to_singular(inst["magma"].read_text(), "std"))
        m = R.run(["Singular", "-q", str(script)], f"singular_{inst['stem']}", TIMEOUTS["singular_std"])
        m.update({"phase": "E", "instance": inst["stem"], "cell": inst["cell"], "label": inst["label"],
                  "engine": "singular_std_GF2_fieldeqs", "config": "dp", "script": str(script.relative_to(R.run_dir))})
        if not R.dry:
            out = (R.run_dir / m["stdout"]).read_text(errors="replace")
            g = re.search(r"RESULT gb_size=(\d+) cpu_ticks=(\d+) ticks_per_sec=(\d+) vdim=(-?\d+) maxdeg_gb=(\d+)", out)
            if m["timed_out"]:
                m["status"] = "budget_stop_timeout"
            elif m.get("rss_limit_breached") and not g:  # D2
                m["status"] = "budget_stop_rss_limit"
            elif g:
                m.update({"gb_size": int(g.group(1)), "engine_cpu_s": int(g.group(2)) / int(g.group(3)),
                          "vdim": int(g.group(4)), "maxdeg_gb": int(g.group(5))})
                m["status"] = "UNSAT_certified_unit_ideal" if m["vdim"] == 0 else f"consistent_vdim_{m['vdim']}"
            else:
                m["status"] = f"infrastructure_exit_{m['returncode']}"
        R.record(m)


def probe_version(argv, timeout: int = VERSION_PROBE_TIMEOUT_S) -> tuple:
    """D4: a version probe that RETURNS, bounded, however it is launched.

    Three separate failure modes are closed, because the frozen probe's 60 s timeout did
    not save RUN-ICPERF-c9590f and a named call is therefore not evidence of a fix:
      * stdin is /dev/null, so an engine that drops into an interactive read (Singular
        does exactly this on `--version`) sees EOF instead of inheriting the launcher's
        stdin and waiting for input that never arrives;
      * output goes to TEMPORARY FILES rather than pipes, so nothing can block draining a
        pipe whose write end a surviving descendant still holds -- which is what
        subprocess.run does after its own timeout fires;
      * the child gets its own session and is killed BY PROCESS GROUP, so a forked
        grandchild cannot outlive the timeout.
    Returns (first_output_line_or_reason, seconds).  A failure is reported as
    `unavailable: <reason>` and never propagated to the caller.
    """
    t0 = time.monotonic()

    def took():
        return round(time.monotonic() - t0, 3)

    try:
        with tempfile.TemporaryFile() as fo, tempfile.TemporaryFile() as fe:
            try:
                p = subprocess.Popen(argv, stdout=fo, stderr=fe, stdin=subprocess.DEVNULL,
                                     start_new_session=True)
            except OSError as e:
                return f"unavailable: {type(e).__name__}: {e}", took()
            try:
                rc = p.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                kill_group(p.pid, p)
                return (f"unavailable: no exit within {timeout}s; process group killed"
                        f" (argv {' '.join(argv)})"), took()
            fo.seek(0)
            fe.seek(0)
            text = fo.read().decode(errors="replace") or fe.read().decode(errors="replace")
    except Exception as e:  # noqa: BLE001
        return f"unavailable: {type(e).__name__}: {e}", took()
    lines = [ln for ln in text.strip().splitlines() if ln.strip()]
    if not lines:
        return f"unavailable: exit {rc} with no output", took()
    return lines[0], took()


def environment() -> dict:
    seconds = {}

    def ver(argv):
        line, took = probe_version(argv)
        seconds[argv[0]] = took
        return line
    env = {"python": sys.version.split()[0], "platform": platform.platform(), "cpu_count": os.cpu_count(),
            "gcc": ver(["gcc", "--version"]), "M2": ver(["M2", "--version"]), "Singular": ver(["Singular", "--version"]),
            "cryptominisat5": ver(["cryptominisat5", "--version"]), "cadical": ver(["cadical", "--version"]),
            "minisat": "2.2.1 (apt; prints no version)", "loadavg_at_start": os.getloadavg(),
            "rss_limit_gb_per_child": RSS_LIMIT_GB, "rss_poll_interval_s": RSS_POLL_INTERVAL_S,
            "rlimit_as_set": False, "version_probe_timeout_s": VERSION_PROBE_TIMEOUT_S,
            "timeouts_s": TIMEOUTS,
            "benchmark_manifest_sha256": sha256(UPSTREAM_SUMS),
            "wdsat_src_sha256": {p.name: sha256(p) for p in sorted(WDSAT_SRC.iterdir())}}
    env["version_probe_seconds"] = seconds  # D4: what each probe actually cost
    return env


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--phases", default="A,B,C,D,E")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=0, help="smoke testing only: first N instances per label per cell")
    a = ap.parse_args()
    run_dir = Path(a.run_dir).resolve()
    run_dir.mkdir(parents=True, exist_ok=True)
    R = Runner(run_dir, a.dry_run)
    insts = list(instances())
    if a.limit:
        insts = subset(insts, a.limit)
    for inst in insts:
        for k in ("info", "anf", "xor", "magma"):
            if not inst[k].exists():
                raise SystemExit(f"missing input {inst[k]}")
    (run_dir / "environment.json").write_text(json.dumps(environment(), indent=1, default=str))
    (run_dir / "plan.json").write_text(json.dumps({"phases": a.phases, "cells": CELLS, "instances": len(insts),
                                                   "timeouts_s": TIMEOUTS,  # D2
                                                   "rss_limit_gb_per_child": RSS_LIMIT_GB,
                                                   "rss_poll_interval_s": RSS_POLL_INTERVAL_S,
                                                   "rlimit_as_set": False}, indent=1))
    phases = {"A": phase_A, "B": phase_B, "C": phase_C, "D": phase_D, "E": phase_E}
    for ph in a.phases.split(","):
        t0 = time.time()
        phases[ph](R, insts)
        with open(run_dir / "phase_log.txt", "a") as f:
            f.write(f"{ph} finished at {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} after {time.time() - t0:.1f}s\n")


if __name__ == "__main__":
    main()
