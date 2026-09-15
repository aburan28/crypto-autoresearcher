#!/usr/bin/env python3
"""Collect every child process this task launched into one machine-readable index."""
from __future__ import annotations

import json
from pathlib import Path

ART = Path(__file__).resolve().parent.parent / "artifacts"
FILES = ["v2a_wdsat_reruns.json", "v2b_m2_C1_C2.json", "v2b_m2_C3_C5.json",
         "v2b_m2_C6_C7.json", "v2c_singular_probe.json", "v2c_singular_fairness.json",
         "ptm2_wdsat_runs.json", "ptm2_null_and_identity.json"]

rows = []
for f in FILES:
    for r in json.loads((ART / f).read_text()):
        pk = r.get("proc_peaks_kb", {})
        rows.append({
            "tag": r["tag"], "source_file": f, "started_utc": r["started_utc"],
            "loadavg1_at_start": r["loadavg1_at_start"],
            "wall_s": r["wall_s"], "cpu_s": r.get("cpu_s"),
            "cpu_per_wall": r.get("cpu_per_wall"),
            "returncode": r["returncode"], "timed_out": r["timed_out"],
            "rlimit_as_gb": r["rlimit_as_gb"],
            "rss_watchdog_killed": r.get("rss_watchdog_killed"),
            "peak_rss_kb_this_child": r.get("peak_rss_kb_this_child"),
            "VmPeak_kb": pk.get("VmPeak"), "VmHWM_kb": pk.get("VmHWM"),
            "max_threads_observed": r.get("max_threads_observed"),
            "status": r.get("status"), "conflicts": r.get("conflicts"),
            "argv": r["argv"],
            "stdout_first_line": (r.get("stdout_head") or "").splitlines()[:1],
            "stderr_first_line": (r.get("stderr_head") or "").splitlines()[:1],
        })
rows.sort(key=lambda r: r["started_utc"])
(ART / "v2_rows_index.json").write_text(json.dumps(rows, indent=1))
print(f"{len(rows)} rows -> {ART/'v2_rows_index.json'}")
print(f"loadavg1 at start: min {min(r['loadavg1_at_start'] for r in rows)}  "
      f"max {max(r['loadavg1_at_start'] for r in rows)}")
print(f"total child wall {sum(r['wall_s'] for r in rows):.1f} s, "
      f"total child cpu {sum(r['cpu_s'] or 0 for r in rows):.1f} s")
