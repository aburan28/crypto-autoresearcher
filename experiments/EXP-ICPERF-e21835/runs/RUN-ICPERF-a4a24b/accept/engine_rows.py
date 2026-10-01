#!/usr/bin/env python3
"""Epoch-2 acceptance driver for the ENGINE rows of RUN-ICPERF-a4a24b (A1/A2/A3/A7,
C-M2AGREE, C-SATREG).  NOT part of the instrument.

Every engine is launched THROUGH the repaired tree's own entry points
(bench.phase_C, bench.run_wdsat, bench.phase_D) with bench.Runner unchanged, so the
wall/CPU/RSS-watchdog/parse path measured here is the instrument's own.  This driver adds
exactly three things, none of which touch measurement logic:

  1. the row sink is `results_engine.jsonl` (epoch 1's committed `results.jsonl` is
     immutable and must not be appended to);
  2. a C-LOAD host snapshot (loadavg triple, MemAvailable, timestamp) is attached to each
     row as `host_at_launch`, taken immediately before Runner.run hands off to Popen;
  3. for --m2 only, the driver sets its OWN oom_score_adj to 1000 before launching, which
     the child inherits: on a guest with ~6.6 GiB MemAvailable and no swap, that makes the
     engine -- never an unrelated host process -- the kernel OOM killer's victim.  It changes
     nothing about what bench.py does; it is machine protection for a launch known to be
     close to the guest's resident ceiling (logs/mem_headroom_probe.json).

Usage: engine_rows.py --wdsat | --purecnf | --m2
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import CODE, RUN_DIR, host_state  # noqa: E402

sys.path.insert(0, str(CODE))
import bench  # noqa: E402  (the repaired tree)

REGRESSION = ("n15l5-1-S", "n15l5-11-U")
M2_INSTANCE = "n15l5-1-S"


class EpochTwoRunner(bench.Runner):
    """bench.Runner with a different row sink and a C-LOAD snapshot per launch."""

    def __init__(self, run_dir: Path):
        super().__init__(run_dir, dry=False)
        self.results = run_dir / "results_engine.jsonl"   # (1) never the committed file
        self.done = set()                                   # nothing in the new sink is done yet
        if self.results.exists():
            for ln in self.results.read_text().splitlines():
                try:
                    r = json.loads(ln)
                    self.done.add((r["instance"], r["engine"], r["config"]))
                except Exception:
                    pass
        self._last_host = None

    def run(self, argv, tag, timeout, stdin_path=None):
        self._last_host = host_state()                      # (2) C-LOAD
        rec = super().run(argv, tag, timeout, stdin_path)
        rec["host_at_launch"] = self._last_host
        rec["epoch"] = 2
        return rec


def inst_by_stem(stem: str) -> dict:
    for i in bench.instances():
        if i["stem"] == stem:
            return i
    raise SystemExit(f"no instance {stem}")


def do_wdsat(R: EpochTwoRunner):
    """C-SATREG: WDSat default on the two regression instances, exactly as phase_A's
    `default` config runs it (no flags), including the certificate check on a SAT answer."""
    for stem in REGRESSION:
        inst = inst_by_stem(stem)
        if R.already(stem, "wdsat", "default"):
            print(f"skip {stem}: already in {R.results.name}")
            continue
        info = bench.InfoFile.parse(inst["info"])
        sizing = bench.anf_sizing(inst["anf"])
        rec = bench.run_wdsat(R, inst["anf"], sizing, [], f"wdsat_default_{stem}")
        rec.update({"phase": "A", "instance": stem, "cell": inst["cell"], "label": inst["label"],
                    "engine": "wdsat", "config": "default", "acceptance_control": "C-SATREG"})
        if rec.get("status") == "SAT":
            rec["verification"] = bench.verify_assignment_bits(info, rec["assignment"])
        R.record(rec)
        print(json.dumps({k: rec.get(k) for k in ("instance", "status", "conflicts", "wall_s", "returncode",
                                                    "peak_rss_kb", "rss_limit_breached", "host_at_launch")}))


def do_purecnf(R: EpochTwoRunner):
    """A7: the three pure-CNF engines on n15l5-1-S through bench.phase_D (one instance)."""
    inst = inst_by_stem(M2_INSTANCE)
    bench.phase_D(R, [inst])


def do_m2(R: EpochTwoRunner):
    """A1/A2/A3/C-M2AGREE: Macaulay2 F4 on n15l5-1-S through bench.phase_C (one instance)."""
    open("/proc/self/oom_score_adj", "w").write("1000\n")   # (3) inherited by the child
    inst = inst_by_stem(M2_INSTANCE)
    hs = host_state()
    print(json.dumps({"pre_launch_host": hs, "oom_score_adj_self": 1000,
                      "rss_limit_gb": bench.RSS_LIMIT_GB, "rss_poll_interval_s": bench.RSS_POLL_INTERVAL_S,
                      "timeout_s_from_bench": bench.TIMEOUTS["m2_f4_l5"], "contract_ceiling_s": 900}), flush=True)
    bench.phase_C(R, [inst])


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--wdsat", action="store_true")
    g.add_argument("--purecnf", action="store_true")
    g.add_argument("--m2", action="store_true")
    a = ap.parse_args()
    R = EpochTwoRunner(RUN_DIR)
    t0 = time.time()
    if a.wdsat:
        do_wdsat(R)
    elif a.purecnf:
        do_purecnf(R)
    elif a.m2:
        do_m2(R)
    print(f"driver wall {time.time() - t0:.2f}s; rows now in {R.results}")
    for ln in R.results.read_text().splitlines():
        r = json.loads(ln)
        print(json.dumps({k: r.get(k) for k in ("recorded_at", "instance", "engine", "config", "status",
                                                 "conflicts", "gb_size", "engine_cpu_s", "maxdeg_gb",
                                                 "unit_ideal", "wall_s", "cpu_s", "returncode",
                                                 "peak_rss_kb", "rss_limit_breached", "stats",
                                                 "stats_unavailable_reason")}))


if __name__ == "__main__":
    main()
