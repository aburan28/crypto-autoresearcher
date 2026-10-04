# DIFFS.md -- repaired tree vs frozen tree (C-BYTE part 2)

Generated 2026-09-16T06:13:39Z by TASK-20260915-4f4027 epoch 2. Unified diffs of
`experiments/EXP-ICPERF-e21835/code/<file>` against `experiments/EXP-ICPERF-66fd51/code/<file>`,
produced with `diff -u` and reproduced VERBATIM; every `@@` hunk is preceded by a
`DEFECT:` line naming the declared defect id(s) it implements. A hunk labelled MIXED
contains lines from two or three declared defects that share a file region (imports,
constants, a docstring, one status-then-stats block); its per-line split is given.
No hunk is attributable to no declared defect. Whether a MIXED hunk satisfies the
contract's 'exactly one of D1-D5' wording is a reviewer's call and is reported, not
resolved, here. `binec.py` is byte-identical and has no diff.

## binec.py

- frozen  sha256: `b6edbcf60b1f3e902d0119f5c1291fdbbe331b15d4e3cdcc42c594d877f98a52`
- repaired sha256: `b6edbcf60b1f3e902d0119f5c1291fdbbe331b15d4e3cdcc42c594d877f98a52`
- diff hunks: 0

Byte-identical; no diff.

## convert.py

- frozen  sha256: `16affe2c5ba07cb5a05b5ba8c0301027ca0adb9901e2f7e73b2e5647edfb495d`
- repaired sha256: `7166582b1154fcecaa4a238749f230efee0b26543308410e121ccbb56d8bff35`
- diff hunks: 1

```diff
--- experiments/EXP-ICPERF-66fd51/code/convert.py	2026-09-13 21:51:52.993515130 +0000
+++ experiments/EXP-ICPERF-e21835/code/convert.py	2026-09-15 22:30:16.903076249 +0000
DEFECT: D1 -- hunk 1/1: magma_to_m2 `gens_` -> `gensG` at all three occurrences plus a comment; the RESULT byte format is unchanged (regex in bench.py phase_C still matches).
@@ -48,10 +48,14 @@
         "t0 = cpuTime();",
         ('G = groebnerBasis(J, Strategy => "F4");' if strategy == "F4" else "G = gens gb J;"),
         "t1 = cpuTime();",
-        'gens_ = flatten entries G;',
-        '<< "RESULT gb_size=" << #gens_ << " cpu_s=" << (t1 - t0)'
-        ' << " maxdeg_gb=" << max apply(gens_, f -> first degree f)'
-        ' << " is_unit=" << (any(gens_, f -> f == 1_R)) << endl;',
+        # D1: Macaulay2 parses a trailing underscore as its subscript operator, so
+        # `gens_` is a parse error at this line, raised only after F4 completes.
+        # The identifier changes; the RESULT line's byte format does not, because
+        # bench.py parses it with a fixed regex.
+        'gensG = flatten entries G;',
+        '<< "RESULT gb_size=" << #gensG << " cpu_s=" << (t1 - t0)'
+        ' << " maxdeg_gb=" << max apply(gensG, f -> first degree f)'
+        ' << " is_unit=" << (any(gensG, f -> f == 1_R)) << endl;',
         "exit 0;",
     ]
     return "\n".join(lines) + "\n"
```

## bench.py

- frozen  sha256: `e8aad273646c4eb12efbcd0bfb75ca42a8278d2046549ffeb3f53d49388c88d8`
- repaired sha256: `d835b1ead969989d58857bfd46d107f2bd42ec2faa8be80fa3bd203e9016cc05`
- diff hunks: 13

```diff
--- experiments/EXP-ICPERF-66fd51/code/bench.py	2026-09-13 22:45:48.587497666 +0000
+++ experiments/EXP-ICPERF-e21835/code/bench.py	2026-09-15 22:34:12.091749958 +0000
DEFECT: MIXED D2+D4+D5 -- hunk 1/13: MODULE DOCSTRING ONLY, no behaviour. Replaced sentence ('address-space limit' -> 'RESIDENT-SET watchdog over the child's process group'): D2. Added 'Successor tree ...' paragraph naming the three bench.py repairs: a comment that names D2, D4 and D5.
@@ -15,9 +15,14 @@
      XORtoCNF.sh and hash-checked against the upstream manifest): 5 S + 5 U per cell
   E  Singular std (GF(2) + field equations): 2 S + 2 U of n15l5
 
-Every engine invocation is a child process under a wall-clock timeout and an address-
-space limit; wall, CPU (user+sys), peak RSS, exit status, stdout/stderr paths and the
-1-minute load average at launch are recorded per run in results.jsonl.
+Every engine invocation is a child process under a wall-clock timeout and a RESIDENT-SET
+watchdog over the child's process group; wall, CPU (user+sys), peak RSS, exit status,
+stdout/stderr paths and the 1-minute load average at launch are recorded per run in
+results.jsonl.
+
+Successor tree of EXP-ICPERF-66fd51/code/bench.py (EXP-ICPERF-e21835): repairs D2
+(RLIMIT_AS replaced by an 8 GiB resident-set watchdog), D4 (the version probe returns
+under inherited stdin) and D5 (per-engine solver statistics on the pure-CNF rows).
 """
 from __future__ import annotations
 
DEFECT: MIXED D2+D4 -- hunk 2/13: MIXED imports. `import signal`: used only by kill_group (D2). `import tempfile`: used only by probe_version (D4).
@@ -29,8 +34,10 @@
 import re
 import resource
 import shutil
+import signal
 import subprocess
 import sys
+import tempfile
 import time
 from pathlib import Path
 
DEFECT: MIXED D2+D4 -- hunk 3/13: MIXED constants. `-MEM_LIMIT_GB = 6` removed and `RSS_LIMIT_GB`, `RSS_POLL_INTERVAL_S`, `RSS_KILL_GRACE_S`, `PAGE_KB` plus the six-line comment added: D2. `VERSION_PROBE_TIMEOUT_S = 10`: D4.
@@ -48,7 +55,17 @@
 
 CELLS = [(15, 5), (17, 6), (19, 6)]
 M = 3  # factor-base points per decomposition (generator's m-1)
-MEM_LIMIT_GB = 6
+# D2: the memory limit is a RESIDENT-SET limit enforced by a watchdog over the child's
+# process group.  RLIMIT_AS is set nowhere: it caps virtual address space, which a
+# garbage-collected algebra system reserves far in excess of what it makes resident
+# (measured 145.4 GiB reserved against 6.8 GiB resident), so it aborted rows that were
+# using well under half the memory they were allowed.  A row this watchdog kills is a
+# budget stop with its limit recorded, never negative evidence.
+RSS_LIMIT_GB = 8
+RSS_POLL_INTERVAL_S = 0.25
+RSS_KILL_GRACE_S = 5.0
+PAGE_KB = os.sysconf("SC_PAGE_SIZE") // 1024
+VERSION_PROBE_TIMEOUT_S = 10
 TIMEOUTS = {"wdsat": 600, "wdsat_null": 180, "wdsat_noncore": 120, "cms_xor": 300, "m2_f4_l5": 600,
             "m2_f4_l6": 1800, "cnf_generic": 300, "singular_std": 900}
 NONCORE_PER_LABEL = 5  # noncore_first runs on the first 5 S + 5 U of each cell
DEFECT: D2 -- hunk 4/13: New `pgid_rss_kb` (sum VmRSS over a process group) and `kill_group` (SIGTERM then SIGKILL the group). kill_group is also CALLED by the D4 probe, but it is the watchdog's kill path and is declared under D2.
@@ -59,6 +76,44 @@
     return hashlib.sha256(p.read_bytes()).hexdigest()
 
 
+# D2: resident-set watchdog primitives.  RSS is summed over the child's whole process
+# group, because Macaulay2's F4 spawns its own threads and an engine may fork helpers.
+def pgid_rss_kb(pgid: int) -> int:
+    """Sum VmRSS over every live process in process group `pgid`, in KB."""
+    total = 0
+    for entry in os.listdir("/proc"):
+        if not entry.isdigit():
+            continue
+        try:
+            data = open(f"/proc/{entry}/stat", "rb").read()
+            # comm may contain spaces and parentheses: fields resume after the last ')'
+            rest = data[data.rindex(b")") + 2:].split()
+            if int(rest[2]) != pgid:  # rest = state ppid pgrp ...
+                continue
+            total += int(open(f"/proc/{entry}/statm", "rb").read().split()[1]) * PAGE_KB
+        except (OSError, ValueError, IndexError):
+            continue
+    return total
+
+
+def kill_group(pgid: int, proc: "subprocess.Popen", grace: float = RSS_KILL_GRACE_S) -> None:
+    """SIGTERM then SIGKILL the whole process group; never leave a survivor holding memory."""
+    for sig in (signal.SIGTERM, signal.SIGKILL):
+        try:
+            os.killpg(pgid, sig)
+        except (ProcessLookupError, PermissionError):
+            pass
+        try:
+            proc.wait(timeout=grace)
+            return
+        except subprocess.TimeoutExpired:
+            continue
+    try:
+        proc.wait(timeout=grace)
+    except subprocess.TimeoutExpired:
+        pass
+
+
 def instances():
     for n, l in CELLS:
         for i in range(1, 21):
DEFECT: D2 -- hunk 5/13: Runner.run rewritten: the `limits()` preexec closure setting RLIMIT_AS is removed; subprocess.run is replaced by Popen(start_new_session=True) polled every RSS_POLL_INTERVAL_S; the group is killed on RSS > limit or on wall timeout; the row gains peak_rss_kb, rss_limit_gb, rss_limit_breached, rss_poll_interval_s, rss_polls, rss_source.
@@ -105,35 +160,61 @@
         return (inst, engine, config) in self.done
 
     def run(self, argv, tag: str, timeout: int, stdin_path: Path | None = None) -> dict:
-        """Run argv as a child under timeout and RLIMIT_AS; return measurements."""
+        """Run argv as a child under a wall-clock timeout and a RESIDENT-SET watchdog.
+
+        D2: RLIMIT_AS is not set.  The child gets its own session (so its process group
+        can be polled and killed as a unit); the watchdog polls the group's summed VmRSS
+        every RSS_POLL_INTERVAL_S seconds and kills the group when the sum exceeds
+        RSS_LIMIT_GB.  peak_rss_kb is the largest sum the watchdog OBSERVED, so it is
+        accurate only to the polling interval; a breach is therefore recorded together
+        with the limit and the interval and never presented as an exact peak.
+        """
         out_p, err_p = self.logs / f"{tag}.out", self.logs / f"{tag}.err"
         if self.dry:
             return {"dry_run": True, "argv": argv}
         before = resource.getrusage(resource.RUSAGE_CHILDREN)
         load1 = os.getloadavg()[0]
-
-        def limits():
-            lim = MEM_LIMIT_GB * (1 << 30)
-            resource.setrlimit(resource.RLIMIT_AS, (lim, lim))
-
+        limit_kb = RSS_LIMIT_GB * (1 << 20)
         t0 = time.monotonic()
         timed_out = False
+        breached = False
+        peak_kb = 0
+        polls = 0
         with open(out_p, "wb") as fo, open(err_p, "wb") as fe:
             stdin = open(stdin_path, "rb") if stdin_path else subprocess.DEVNULL
             try:
-                p = subprocess.run(argv, stdout=fo, stderr=fe, stdin=stdin, timeout=timeout,
-                                   preexec_fn=limits, check=False)
-                rc = p.returncode
-            except subprocess.TimeoutExpired:
-                timed_out, rc = True, None
+                p = subprocess.Popen(argv, stdout=fo, stderr=fe, stdin=stdin,
+                                     start_new_session=True)
             finally:
                 if stdin_path:
                     stdin.close()
+            pgid = p.pid  # start_new_session makes the child its own group leader
+            while True:
+                rc = p.poll()
+                rss = pgid_rss_kb(pgid)
+                polls += 1
+                peak_kb = max(peak_kb, rss)
+                if rc is not None:
+                    break
+                if rss > limit_kb:
+                    breached = True
+                    kill_group(pgid, p)
+                    rc = p.returncode
+                    break
+                if time.monotonic() - t0 > timeout:
+                    timed_out = True
+                    kill_group(pgid, p)
+                    rc = None
+                    break
+                time.sleep(RSS_POLL_INTERVAL_S)
         wall = time.monotonic() - t0
         after = resource.getrusage(resource.RUSAGE_CHILDREN)
         return {"argv": argv, "wall_s": round(wall, 4), "timed_out": timed_out, "returncode": rc,
                 "cpu_s": round((after.ru_utime - before.ru_utime) + (after.ru_stime - before.ru_stime), 4),
                 "max_rss_kb_children_highwater": after.ru_maxrss,
+                "peak_rss_kb": peak_kb, "rss_limit_gb": RSS_LIMIT_GB,
+                "rss_limit_breached": breached, "rss_poll_interval_s": RSS_POLL_INTERVAL_S,
+                "rss_polls": polls, "rss_source": "sum of VmRSS over the child's process group",
                 "loadavg1_at_start": round(load1, 2), "timeout_s": timeout,
                 "stdout": str(out_p.relative_to(self.run_dir)), "stderr": str(err_p.relative_to(self.run_dir))}
 
DEFECT: D5 -- hunk 6/13: `parse_cms_stats` (one CryptoMiniSat-shaped regex) replaced by per-engine `SOLVER_STAT_PATTERNS` and `parse_solver_stats(engine, ...)`.
@@ -254,10 +335,25 @@
     return {"status": status, "vals": vals}
 
 
-def parse_cms_stats(err_text: str, out_text: str) -> dict:
+# D5: each engine prints its own solver-statistics block in its own format, so a single
+# CryptoMiniSat-shaped pattern recorded counters for one engine of three.  CaDiCaL prints
+# them only when not run with -q, and MiniSat only at verbosity >= 1; both flags are set
+# in phase_D.  An engine that still emits no counter gets a recorded reason, never a
+# silently absent field.
+SOLVER_STAT_PATTERNS = {
+    "cryptominisat5": r"^c\s+(conflicts|decisions|propagations)\s*:\s*(\d+)",
+    "cadical": r"^c\s+(conflicts|decisions|propagations)\s*:\s*(\d+)",
+    "minisat": r"^(conflicts|decisions|propagations)\s*:\s*(\d+)",
+}
+
+
+def parse_solver_stats(engine: str, err_text: str, out_text: str) -> dict:
+    pattern = SOLVER_STAT_PATTERNS.get(engine)
+    if pattern is None:
+        return {}
     stats = {}
     for ln in (out_text + "\n" + err_text).splitlines():
-        m = re.match(r"c\s+(conflicts|decisions|propagations)\s*:\s*(\d+)", ln)
+        m = re.match(pattern, ln.strip() if engine == "minisat" else ln)
         if m:
             stats[m.group(1)] = int(m.group(2))
     return stats
DEFECT: D2 -- hunk 7/13: run_wdsat: new `budget_stop_rss_limit` status when the watchdog killed the row.
@@ -354,6 +450,10 @@
         m["stderr_head"] = err[:300]
         if m["timed_out"]:
             m["status"] = "budget_stop_timeout"
+        elif m.get("rss_limit_breached"):
+            # D2: an honest resident-set limit is expected to kill rows; it is a budget
+            # stop with its limit recorded, never negative evidence about the engine.
+            m["status"] = "budget_stop_rss_limit"
         elif m["returncode"] not in (0, 1) and m["status"] == "unknown":
             m["status"] = f"infrastructure_exit_{m['returncode']}"
         return m
DEFECT: MIXED D2+D5 -- hunk 8/13: MIXED finish_dimacs_record. The status ladder gaining `budget_stop_rss_limit`: D2. `parse_solver_stats(engine, ...)` call and the `stats_unavailable_reason` field naming the engine when no counter matched: D5.
@@ -379,8 +479,19 @@
     out = (R.run_dir / m["stdout"]).read_text(errors="replace")
     err = (R.run_dir / m["stderr"]).read_text(errors="replace")
     parsed = parse_dimacs_model(out)
-    m["status"] = "budget_stop_timeout" if m["timed_out"] else parsed["status"]
-    m["stats"] = parse_cms_stats(err, out)
+    if m["timed_out"]:
+        m["status"] = "budget_stop_timeout"
+    elif m.get("rss_limit_breached"):  # D2
+        m["status"] = "budget_stop_rss_limit"
+    else:
+        m["status"] = parsed["status"]
+    m["stats"] = parse_solver_stats(m.get("engine", ""), err, out)  # D5
+    if not m["stats"]:  # D5
+        m["stats_unavailable_reason"] = (
+            f"{m.get('engine')}: no conflict/decision/propagation counter matched its"
+            f" statistics pattern in stdout or stderr"
+            f" (status={m.get('status')}, returncode={m.get('returncode')},"
+            f" timed_out={m.get('timed_out')}, argv={' '.join(m.get('argv', []))})")
     if parsed["status"] == "SAT":
         bits = model_bits(parsed["vals"], M * inst["l"])
         m["assignment_core_bits"] = bits
DEFECT: D5 -- hunk 9/13: phase_D engine flags: cadical loses `-q`, minisat `-verb=0` -> `-verb=1`, so each engine prints its own statistics block; CNF, timeout and watchdog unchanged.
@@ -416,9 +527,12 @@
 
 def phase_D(R: Runner, insts):
     sub = subset(insts, 5)
+    # D5: -q suppressed CaDiCaL's statistics block and -verb=0 suppressed MiniSat's, so
+    # neither engine could report a conflict count.  Both now run at the verbosity that
+    # prints their own counters; the CNF, the timeout and the watchdog are unchanged.
     engines = {"cryptominisat5": lambda p: ["cryptominisat5", "--verb", "1", str(p)],
-               "cadical": lambda p: ["cadical", "-q", str(p)],
-               "minisat": lambda p: ["minisat", "-verb=0", str(p), "MODEL_OUT"]}
+               "cadical": lambda p: ["cadical", str(p)],
+               "minisat": lambda p: ["minisat", "-verb=1", str(p), "MODEL_OUT"]}
     for inst in sub:
         info = InfoFile.parse(inst["info"])
         cnf = pure_cnf(R, inst)
DEFECT: D2 -- hunk 10/13: phase_C (Macaulay2): `budget_stop_rss_limit` status when the watchdog killed the row and no RESULT line was parsed.
@@ -465,6 +579,8 @@
             g = re.search(r"RESULT gb_size=(\d+) cpu_s=([\d.]+) maxdeg_gb=(\d+) is_unit=(true|false)", out)
             if m["timed_out"]:
                 m["status"] = "budget_stop_timeout"
+            elif m.get("rss_limit_breached") and not g:  # D2
+                m["status"] = "budget_stop_rss_limit"
             elif g:
                 m.update({"gb_size": int(g.group(1)), "engine_cpu_s": float(g.group(2)), "maxdeg_gb": int(g.group(3)),
                           "unit_ideal": g.group(4) == "true"})
DEFECT: D2 -- hunk 11/13: phase_E (Singular): same `budget_stop_rss_limit` status site.
@@ -491,6 +607,8 @@
             g = re.search(r"RESULT gb_size=(\d+) cpu_ticks=(\d+) ticks_per_sec=(\d+) vdim=(-?\d+) maxdeg_gb=(\d+)", out)
             if m["timed_out"]:
                 m["status"] = "budget_stop_timeout"
+            elif m.get("rss_limit_breached") and not g:  # D2
+                m["status"] = "budget_stop_rss_limit"
             elif g:
                 m.update({"gb_size": int(g.group(1)), "engine_cpu_s": int(g.group(2)) / int(g.group(3)),
                           "vdim": int(g.group(4)), "maxdeg_gb": int(g.group(5))})
DEFECT: MIXED D4+D2 -- hunk 12/13: MIXED. New `probe_version` (DEVNULL stdin, temp-file output, own session, process-group kill, 10 s bound, returns `unavailable: <reason>`) and `environment()` rewired through it with `version_probe_seconds` recorded: D4. Inside `environment()`, `mem_limit_gb_per_child` -> `rss_limit_gb_per_child`, `rss_poll_interval_s`, `rlimit_as_set: False`: D2 (the environment record must name the limit actually in force).
@@ -500,19 +618,69 @@
         R.record(m)
 
 
+def probe_version(argv, timeout: int = VERSION_PROBE_TIMEOUT_S) -> tuple:
+    """D4: a version probe that RETURNS, bounded, however it is launched.
+
+    Three separate failure modes are closed, because the frozen probe's 60 s timeout did
+    not save RUN-ICPERF-c9590f and a named call is therefore not evidence of a fix:
+      * stdin is /dev/null, so an engine that drops into an interactive read (Singular
+        does exactly this on `--version`) sees EOF instead of inheriting the launcher's
+        stdin and waiting for input that never arrives;
+      * output goes to TEMPORARY FILES rather than pipes, so nothing can block draining a
+        pipe whose write end a surviving descendant still holds -- which is what
+        subprocess.run does after its own timeout fires;
+      * the child gets its own session and is killed BY PROCESS GROUP, so a forked
+        grandchild cannot outlive the timeout.
+    Returns (first_output_line_or_reason, seconds).  A failure is reported as
+    `unavailable: <reason>` and never propagated to the caller.
+    """
+    t0 = time.monotonic()
+
+    def took():
+        return round(time.monotonic() - t0, 3)
+
+    try:
+        with tempfile.TemporaryFile() as fo, tempfile.TemporaryFile() as fe:
+            try:
+                p = subprocess.Popen(argv, stdout=fo, stderr=fe, stdin=subprocess.DEVNULL,
+                                     start_new_session=True)
+            except OSError as e:
+                return f"unavailable: {type(e).__name__}: {e}", took()
+            try:
+                rc = p.wait(timeout=timeout)
+            except subprocess.TimeoutExpired:
+                kill_group(p.pid, p)
+                return (f"unavailable: no exit within {timeout}s; process group killed"
+                        f" (argv {' '.join(argv)})"), took()
+            fo.seek(0)
+            fe.seek(0)
+            text = fo.read().decode(errors="replace") or fe.read().decode(errors="replace")
+    except Exception as e:  # noqa: BLE001
+        return f"unavailable: {type(e).__name__}: {e}", took()
+    lines = [ln for ln in text.strip().splitlines() if ln.strip()]
+    if not lines:
+        return f"unavailable: exit {rc} with no output", took()
+    return lines[0], took()
+
+
 def environment() -> dict:
+    seconds = {}
+
     def ver(argv):
-        try:
-            return subprocess.run(argv, capture_output=True, text=True, timeout=60).stdout.strip().splitlines()[0]
-        except Exception as e:  # noqa: BLE001
-            return f"unavailable: {e}"
-    return {"python": sys.version.split()[0], "platform": platform.platform(), "cpu_count": os.cpu_count(),
+        line, took = probe_version(argv)
+        seconds[argv[0]] = took
+        return line
+    env = {"python": sys.version.split()[0], "platform": platform.platform(), "cpu_count": os.cpu_count(),
             "gcc": ver(["gcc", "--version"]), "M2": ver(["M2", "--version"]), "Singular": ver(["Singular", "--version"]),
             "cryptominisat5": ver(["cryptominisat5", "--version"]), "cadical": ver(["cadical", "--version"]),
             "minisat": "2.2.1 (apt; prints no version)", "loadavg_at_start": os.getloadavg(),
-            "mem_limit_gb_per_child": MEM_LIMIT_GB, "timeouts_s": TIMEOUTS,
+            "rss_limit_gb_per_child": RSS_LIMIT_GB, "rss_poll_interval_s": RSS_POLL_INTERVAL_S,
+            "rlimit_as_set": False, "version_probe_timeout_s": VERSION_PROBE_TIMEOUT_S,
+            "timeouts_s": TIMEOUTS,
             "benchmark_manifest_sha256": sha256(UPSTREAM_SUMS),
             "wdsat_src_sha256": {p.name: sha256(p) for p in sorted(WDSAT_SRC.iterdir())}}
+    env["version_probe_seconds"] = seconds  # D4: what each probe actually cost
+    return env
 
 
 def main():
DEFECT: D2 -- hunk 13/13: plan.json: `mem_limit_gb` -> `rss_limit_gb_per_child`, `rss_poll_interval_s`, `rlimit_as_set: False`.
@@ -534,7 +702,10 @@
                 raise SystemExit(f"missing input {inst[k]}")
     (run_dir / "environment.json").write_text(json.dumps(environment(), indent=1, default=str))
     (run_dir / "plan.json").write_text(json.dumps({"phases": a.phases, "cells": CELLS, "instances": len(insts),
-                                                   "timeouts_s": TIMEOUTS, "mem_limit_gb": MEM_LIMIT_GB}, indent=1))
+                                                   "timeouts_s": TIMEOUTS,  # D2
+                                                   "rss_limit_gb_per_child": RSS_LIMIT_GB,
+                                                   "rss_poll_interval_s": RSS_POLL_INTERVAL_S,
+                                                   "rlimit_as_set": False}, indent=1))
     phases = {"A": phase_A, "B": phase_B, "C": phase_C, "D": phase_D, "E": phase_E}
     for ph in a.phases.split(","):
         t0 = time.time()
```

## summary.py

- frozen  sha256: `eaf54bd7d0bc1b9a0926cafe1ba7dd975da4aa952a8b530018c52a59ac994561`
- repaired sha256: `353fa48db0d4bd13348d1f35ecb5fa19cbef59c79b060c387c145e47078f3389`
- diff hunks: 5

```diff
--- experiments/EXP-ICPERF-66fd51/code/summary.py	2026-09-13 22:47:32.927937180 +0000
+++ experiments/EXP-ICPERF-e21835/code/summary.py	2026-09-15 22:36:52.148542174 +0000
DEFECT: D3 -- hunk 1/5: D3(b,c): new helpers `unevaluated`, `evaluated`, `compose` -- the ONE uniform reporting rule (evaluated flag, reason, `unevaluable` list, nonempty list forces top-level holds None). No numeric logic.
@@ -33,6 +33,40 @@
     return not (s.startswith("budget_stop") or s.startswith("infrastructure") or s == "unknown")
 
 
+def unevaluated(reason: str, **fields) -> dict:
+    """D3(b,c): a clause that could not be evaluated, reported instead of dropped."""
+    rec = dict(fields)
+    rec.update({"evaluated": False, "reason": reason, "holds": None})
+    return rec
+
+
+def evaluated(**fields) -> dict:
+    """D3(b,c): a clause that was evaluated in full."""
+    rec = dict(fields)
+    rec["evaluated"] = True
+    return rec
+
+
+def compose(clauses: dict, **extra) -> dict:
+    """D3(b,c): ONE uniform reporting rule for every prediction quantified over cells.
+
+    Every clause says whether it was evaluated; an unevaluated clause names what was
+    missing.  The prediction lists every such clause in `unevaluable`, and a NONEMPTY
+    `unevaluable` list forces top-level `holds: None` -- never true and never false,
+    because a prediction quantified over every cell is not settled by the cells that
+    happened to be measurable.  This changes no median, ratio, threshold, inclusion rule
+    or the definition of `finished`; it changes only what is reported.
+    """
+    unevaluable = sorted(k for k, v in clauses.items() if not v.get("evaluated", True))
+    resolved = [v["holds"] for k, v in clauses.items()
+                if v.get("evaluated", True) and v.get("holds") is not None]
+    holds = None if (unevaluable or not resolved) else all(resolved)
+    rec = {"cells": clauses, "unevaluable": unevaluable, "n_clauses": len(clauses),
+           "n_evaluated": len(clauses) - len(unevaluable), "holds": holds}
+    rec.update(extra)
+    return rec
+
+
 def main(run_dir: Path):
     rows = load(run_dir)
     by = defaultdict(list)
DEFECT: D3 -- hunk 2/5: D3(b): P1 gains `evaluated: True, unevaluable: []` so every prediction carries the same reporting fields. holds formula unchanged.
@@ -75,6 +109,7 @@
     out["predictions"]["P1"] = {"n_certificates": len(certs), "invalid_certificates": bad_certs,
                                 "n_sat_answers": len(sat_answers), "unverified_sat_answers": bad_answers,
                                 "sat_answers_on_U_labelled_instances": sat_on_U,
+                                "evaluated": True, "unevaluable": [],  # D3(b)
                                 "holds": (len(certs) == 30 and not bad_certs and not bad_answers)}
 
     # ---- P2: WDSat default vs every finishing Groebner engine, per cell, S and U separately
DEFECT: D3 -- hunk 3/5: D3(b): P2 -- a cell/label with a missing median is reported `unevaluated` with the missing keys named instead of vanishing; ratio formula and 0.1 threshold unchanged; composed by `compose`. (This is the site of epoch 1's 12 UNEXPLAINED leaf differences: a `ratio: null` key now exists where the frozen output had no key.)
@@ -83,11 +118,17 @@
         for label in ("S", "U"):
             L = out["cells"][cell][label]
             for gname, key in (("m2_f4", "m2_f4_wall_s"), ("singular", "singular_wall_s")):
+                name = f"{cell}/{label}/wdsat_default_over_{gname}"
                 if L.get(key) is not None and L.get("wdsat_default_wall_s") is not None:
                     ratio = L["wdsat_default_wall_s"] / L[key] if L[key] > 0 else None
-                    p2[f"{cell}/{label}/wdsat_default_over_{gname}"] = {"ratio": ratio, "holds": ratio is not None and ratio <= 0.1}
-    out["predictions"]["P2"] = {"cells": p2, "holds": all(v["holds"] for v in p2.values()) if p2 else None,
-                                "note": "None = no Groebner engine finished on that cell; nothing asserted"}
+                    p2[name] = evaluated(ratio=ratio, holds=ratio is not None and ratio <= 0.1)
+                else:  # D3(b): the missing side is named instead of the clause vanishing
+                    missing = [k for k in (key, "wdsat_default_wall_s") if L.get(k) is None]
+                    p2[name] = unevaluated(f"no median for {', '.join(missing)}: no row of that"
+                                           f" engine/config finished on {cell}/{label}", ratio=None)
+    out["predictions"]["P2"] = compose(
+        p2, note="an unevaluable clause means no Groebner engine finished on that cell/label;"
+                 " nothing is asserted about it")
 
     # ---- P3: (a) explicit core order == default per instance (identity check on -g);
     #          (b) non-core-first order >= 2x default in median conflicts per cell;
DEFECT: D3 -- hunk 4/5: D3(a): `L = out['cells'][cell][label]` bound INSIDE the P3 per-(cell,label) loop, and the l=6 pure-CNF clause computed per (cell,label) (the frozen `continue` on empty nc/de also skipped it). D3(b): P3 noncore/cms clauses, P4 missing-median case and all three P5 clauses (including the Groebner term guarded on m2_f4_cpu_s) reported `unevaluated` with reasons. D3(c): P4's under-floor cell reported unevaluated instead of dropped from top-level holds. All medians, ratios (`/`), thresholds (2, 10, 0.9, 0.05, [0.5,2]) and `finished` untouched; extra fields (S, U, the two wall medians) are new reporting fields.
@@ -101,73 +142,131 @@
                         if "default" in c and "core_order" in c and c["default"] != c["core_order"])
     compared = sum(1 for c in by_inst.values() if "default" in c and "core_order" in c)
     if compared:
-        p3["core_order_identity"] = {"instances_compared": compared, "mismatching_instances": mismatches,
-                                     "holds": not mismatches}
+        p3["core_order_identity"] = evaluated(instances_compared=compared,
+                                              mismatching_instances=mismatches,
+                                              holds=not mismatches)
+    else:  # D3(b)
+        p3["core_order_identity"] = unevaluated(
+            "no instance carries both a finished default row and a finished core_order row"
+            " with a conflict count", instances_compared=0, mismatching_instances=[])
     # P3b compares wall time on the SAME instances, right-censored: a timeout row
     # contributes its timeout_s, a lower bound on its true wall, so the resulting
     # median is itself a lower bound and the >= 2x test stays valid (never inflated
     # in the direction of the prediction by the censoring).
     for cell in cells:
         for label in ("S", "U"):
+            # D3(a): THE LOOP-VARIABLE LEAK.  The pure-CNF clause below read `L`, which
+            # this loop never bound, so it silently used the last aggregate bound by the
+            # earlier per-cell loop (n19l6/U) and every l = 6 cell received that one
+            # cell's ratio.  Binding the per-(cell, label) aggregate here, inside the loop
+            # that uses it, is the whole fix; the ratio's formula is untouched.
+            L = out["cells"][cell][label]
+            nc_name = f"{cell}/{label}/noncore_first_over_default_wall_censored"
             nc = [r for r in rows if r.get("engine") == "wdsat" and r.get("config") == "noncore_first"
                   and r.get("cell") == cell and r.get("label") == label
                   and (finished(r) or r.get("status") == "budget_stop_timeout")]
-            if not nc:
-                continue
             stems = {r["instance"] for r in nc}
             de = [r for r in rows if r.get("engine") == "wdsat" and r.get("config") == "default"
                   and r.get("instance") in stems and finished(r)]
-            if not de:
-                continue
-            nc_vals = [r["wall_s"] if finished(r) else float(r.get("timeout_s") or r["wall_s"]) for r in nc]
-            de_med = med([r["wall_s"] for r in de])
-            nc_med = med(nc_vals)
-            r = nc_med / de_med if de_med and de_med > 0 else float("inf")
-            p3[f"{cell}/{label}/noncore_first_over_default_wall_censored"] = {
-                "noncore_first_wall_s_lower_bound": nc_med, "default_wall_s": de_med, "ratio_lower_bound": r,
-                "n_noncore_rows": len(nc), "n_noncore_timeouts": sum(1 for x in nc if not finished(x)),
-                "noncore_first_conflicts_finished_median": med([x["conflicts"] for x in nc if finished(x) and x.get("conflicts") is not None]),
-                "holds": r >= 2}
-            if cell.endswith("l6") and L["cryptominisat5_pure_cnf_wall_s"] is not None and L["wdsat_default_wall_s"] is not None:
-                r = L["cryptominisat5_pure_cnf_wall_s"] / L["wdsat_default_wall_s"] if L["wdsat_default_wall_s"] > 0 else float("inf")
-                p3[f"{cell}/{label}/cms_pure_cnf_over_wdsat"] = {"ratio": r, "holds": r >= 10}
-    out["predictions"]["P3"] = {"cells": p3, "holds": all(v["holds"] for v in p3.values()) if p3 else None}
+            if not nc:  # D3(b)
+                p3[nc_name] = unevaluated(f"no noncore_first row on {cell}/{label} is either"
+                                          f" finished or a recorded timeout", n_noncore_rows=0)
+            elif not de:  # D3(b)
+                p3[nc_name] = unevaluated(f"no finished wdsat default row on the {len(stems)}"
+                                          f" instance(s) the noncore_first rows cover",
+                                          n_noncore_rows=len(nc))
+            else:
+                nc_vals = [r["wall_s"] if finished(r) else float(r.get("timeout_s") or r["wall_s"]) for r in nc]
+                de_med = med([r["wall_s"] for r in de])
+                nc_med = med(nc_vals)
+                r = nc_med / de_med if de_med and de_med > 0 else float("inf")
+                p3[nc_name] = evaluated(
+                    noncore_first_wall_s_lower_bound=nc_med, default_wall_s=de_med, ratio_lower_bound=r,
+                    n_noncore_rows=len(nc), n_noncore_timeouts=sum(1 for x in nc if not finished(x)),
+                    noncore_first_conflicts_finished_median=med([x["conflicts"] for x in nc if finished(x) and x.get("conflicts") is not None]),
+                    holds=r >= 2)
+            if cell.endswith("l6"):
+                cms_name = f"{cell}/{label}/cms_pure_cnf_over_wdsat"
+                if L["cryptominisat5_pure_cnf_wall_s"] is not None and L["wdsat_default_wall_s"] is not None:
+                    r = L["cryptominisat5_pure_cnf_wall_s"] / L["wdsat_default_wall_s"] if L["wdsat_default_wall_s"] > 0 else float("inf")
+                    p3[cms_name] = evaluated(ratio=r, holds=r >= 10,
+                                             cryptominisat5_pure_cnf_wall_s=L["cryptominisat5_pure_cnf_wall_s"],
+                                             wdsat_default_wall_s=L["wdsat_default_wall_s"])
+                else:  # D3(b)
+                    missing = [k for k in ("cryptominisat5_pure_cnf_wall_s", "wdsat_default_wall_s")
+                               if L[k] is None]
+                    p3[cms_name] = unevaluated(f"no median for {', '.join(missing)} on"
+                                               f" {cell}/{label}", ratio=None)
+    out["predictions"]["P3"] = compose(p3)
 
     # ---- P4: -x does not reduce median wall time
     p4 = {}
     for cell in cells:
         for label in ("S", "U"):
             L = out["cells"][cell][label]
+            name = f"{cell}/{label}"
             if L["wdsat_gauss_elim_wall_s"] is not None and L["wdsat_default_wall_s"] is not None:
                 d = L["wdsat_default_wall_s"]
                 if d <= 0.05:
-                    p4[f"{cell}/{label}"] = {"gauss_elim": L["wdsat_gauss_elim_wall_s"], "default": d,
-                                            "holds": None, "note": "default median under the 0.05 s floor; unresolvable by wall clock"}
+                    # D3(c): the frozen reduction reported this cell with holds None and
+                    # then dropped it from the top-level `holds`, so a prediction
+                    # quantified over every cell read as settled on a subset.  The
+                    # threshold and the 0.05 s floor are unchanged; only the reporting is.
+                    p4[name] = unevaluated("default median under the 0.05 s floor;"
+                                           " unresolvable by wall clock",
+                                           gauss_elim=L["wdsat_gauss_elim_wall_s"], default=d)
                 else:
-                    p4[f"{cell}/{label}"] = {"gauss_elim": L["wdsat_gauss_elim_wall_s"], "default": d,
-                                            "holds": L["wdsat_gauss_elim_wall_s"] >= 0.9 * d}
-    resolved = [v["holds"] for v in p4.values() if v["holds"] is not None]
-    out["predictions"]["P4"] = {"cells": p4, "holds": all(resolved) if resolved else None}
+                    p4[name] = evaluated(gauss_elim=L["wdsat_gauss_elim_wall_s"], default=d,
+                                         holds=L["wdsat_gauss_elim_wall_s"] >= 0.9 * d)
+            else:  # D3(b)
+                missing = [k for k in ("wdsat_gauss_elim_wall_s", "wdsat_default_wall_s") if L[k] is None]
+                p4[name] = unevaluated(f"no median for {', '.join(missing)} on {name}",
+                                       gauss_elim=L["wdsat_gauss_elim_wall_s"],
+                                       default=L["wdsat_default_wall_s"])
+    out["predictions"]["P4"] = compose(p4)
 
     # ---- P5: SAT solvers U/S conflicts >= 2; Groebner S/U cpu in [0.5, 2]
     p5 = {}
     for cell in cells:
         S, U = out["cells"][cell]["S"], out["cells"][cell]["U"]
+        name = f"{cell}/wdsat_U_over_S_conflicts"
         if S["wdsat_default_conflicts"] and U["wdsat_default_conflicts"] is not None:
             r = U["wdsat_default_conflicts"] / S["wdsat_default_conflicts"]
-            p5[f"{cell}/wdsat_U_over_S_conflicts"] = {"ratio": r, "holds": r >= 2}
+            p5[name] = evaluated(ratio=r, S=S["wdsat_default_conflicts"],
+                                 U=U["wdsat_default_conflicts"], holds=r >= 2)
+        else:  # D3(b)
+            p5[name] = unevaluated("no usable wdsat default median conflict count for both"
+                                   f" labels of {cell} (S={S['wdsat_default_conflicts']},"
+                                   f" U={U['wdsat_default_conflicts']})", ratio=None)
         cms = {}
         for label in ("S", "U"):
             cms[label] = med([(r.get("stats") or {}).get("conflicts") for r in rows
                               if r.get("engine") == "cryptominisat5" and r.get("config") == "cnf_xor"
                               and r.get("cell") == cell and r.get("label") == label and finished(r)])
+        name = f"{cell}/cms_xor_U_over_S_conflicts"
         if cms["S"] and cms["U"] is not None:
             r = cms["U"] / cms["S"]
-            p5[f"{cell}/cms_xor_U_over_S_conflicts"] = {"ratio": r, "S": cms["S"], "U": cms["U"], "holds": r >= 2}
+            p5[name] = evaluated(ratio=r, S=cms["S"], U=cms["U"], holds=r >= 2)
+        else:  # D3(b)
+            p5[name] = unevaluated("no usable cryptominisat5 cnf_xor median conflict count for"
+                                   f" both labels of {cell} (S={cms['S']}, U={cms['U']})",
+                                   ratio=None, S=cms["S"], U=cms["U"])
+        # D3(b): THE UNEVALUATED GROEBNER CLAUSE.  This term is guarded on m2_f4_cpu_s,
+        # which is the median of the rows' `engine_cpu_s` key.  When no Macaulay2 row
+        # carries that key the term simply vanished, and the top-level `holds` was then
+        # computed over the surviving terms as if P5 had been evaluated in full.  The
+        # guard and the [0.5, 2] band are unchanged; the skip is now recorded.
+        name = f"{cell}/m2_S_over_U_cpu"
         if S["m2_f4_cpu_s"] and U["m2_f4_cpu_s"]:
             r = S["m2_f4_cpu_s"] / U["m2_f4_cpu_s"]
-            p5[f"{cell}/m2_S_over_U_cpu"] = {"ratio": r, "holds": 0.5 <= r <= 2}
-    out["predictions"]["P5"] = {"cells": p5, "holds": all(v["holds"] for v in p5.values()) if p5 else None}
+            p5[name] = evaluated(ratio=r, S=S["m2_f4_cpu_s"], U=U["m2_f4_cpu_s"], holds=0.5 <= r <= 2)
+        else:
+            p5[name] = unevaluated(
+                "no median for m2_f4_cpu_s: no macaulay2_F4_ZZ2_fieldeqs/grevlex row of"
+                f" {cell} carries the engine_cpu_s key (S={S['m2_f4_cpu_s']},"
+                f" U={U['m2_f4_cpu_s']}), so the Groebner clause of P5 was not evaluated",
+                ratio=None)
+    out["predictions"]["P5"] = compose(p5)
 
     # ---- P6: null objects >= 10x harder in conflicts than structured U
     p6 = {}
DEFECT: D3 -- hunk 5/5: D3(c): P6 -- a cell without a finished null-object conflict count is named in `unevaluable` and forces top-level holds None instead of being filtered out; >= 10 threshold and exclusion rule unchanged.
@@ -177,13 +276,26 @@
         null_conf = med([U["wdsat_default_on_null_object_conflicts"], S["wdsat_default_on_null_object_conflicts"]])
         if null_conf is not None and U["wdsat_default_conflicts"]:
             r = null_conf / U["wdsat_default_conflicts"]
-            p6[cell] = {"null_median_conflicts": null_conf, "structured_U_median_conflicts": U["wdsat_default_conflicts"],
-                        "ratio": r, "holds": r >= 10}
+            p6[cell] = evaluated(null_median_conflicts=null_conf,
+                                 structured_U_median_conflicts=U["wdsat_default_conflicts"],
+                                 ratio=r, holds=r >= 10)
         else:
-            p6[cell] = {"null_median_conflicts": null_conf, "structured_U_median_conflicts": U["wdsat_default_conflicts"],
-                        "ratio": None, "holds": None}
-    out["predictions"]["P6"] = {"cells": p6, "holds": all(v["holds"] for v in p6.values() if v["holds"] is not None) if p6 else None,
-                                "note": "null objects with status budget_stop/infrastructure are excluded and counted in exclusions"}
+            # D3(c): THE SILENTLY DROPPED CELL.  The frozen reduction filtered cells whose
+            # own `holds` was None out of the top-level `holds`, so a prediction quantified
+            # over EVERY cell was reported true on the strength of the cells that happened
+            # to finish.  The exclusion rule for null rows and the >= 10x threshold are
+            # unchanged; the cell is now named in `unevaluable` and the prediction reports
+            # `holds: null`.
+            missing = ("no finished null-object row carries a conflict count"
+                       if null_conf is None else
+                       "no usable structured U median conflict count")
+            p6[cell] = unevaluated(f"{missing} for {cell}", null_median_conflicts=null_conf,
+                                   structured_U_median_conflicts=U["wdsat_default_conflicts"],
+                                   ratio=None)
+    out["predictions"]["P6"] = compose(
+        p6, note="null objects with status budget_stop/infrastructure are excluded and counted"
+                 " in exclusions; a cell with no finished null object is reported in"
+                 " `unevaluable` and forces holds: null")
 
     out["n_rows"] = len(rows)
     (run_dir / "summary.json").write_text(json.dumps(out, indent=1, default=str))
```

