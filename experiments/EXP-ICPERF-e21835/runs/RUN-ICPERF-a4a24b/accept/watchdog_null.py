#!/usr/bin/env python3
"""D2 / A4 / C-WATCHDOG-NULL: controls before belief, applied to the watchdog itself.

Two synthetic null objects of the same shape as a real engine child, both launched through
the REPAIRED Runner.run so the watchdog under test is the one the acceptance uses:

  (i)  watchdog_control/null_resident.py makes memory RESIDENT in increments and MUST be
       killed, with rss_limit_breached true and an observed peak within the polling
       tolerance of the limit.
  (ii) watchdog_control/null_addressspace.py RESERVES >= 64 GiB of address space
       (PROT_NONE, MAP_NORESERVE, never touched) while touching < 512 MiB, and MUST NOT be
       killed: it must exit 0 with rss_limit_breached false. RLIMIT_AS kills this object;
       a resident-set watchdog must not, which is what distinguishes the new limit from
       the old one. Killing it would reproduce the defect D2 removes.

Direction (ii) runs at the DECLARED 8 GiB limit. Direction (i) runs at a limit chosen from
the host's ACTUAL free memory at launch, because a 12 GiB resident allocation cannot be
reached on a host with ~7 GB available and no swap: the OOM killer would fire first, which
would measure the OOM killer rather than the watchdog. The limit used, the target, and the
reason are recorded on the row.
"""
from __future__ import annotations

import json
import sys

from common import LOGS, RUN_DIR, WD, emit, host_state, mem_available_kb  # noqa: F401

import bench  # noqa: E402


def one(tag, argv, limit_gb, timeout, extra):
    """Run one null object through the repaired Runner with the watchdog set to limit_gb."""
    saved = bench.RSS_LIMIT_GB
    bench.RSS_LIMIT_GB = limit_gb
    try:
        R = bench.Runner(RUN_DIR, False)
        host = host_state()
        m = R.run(argv, tag, timeout)
    finally:
        bench.RSS_LIMIT_GB = saved
    m.update(extra)
    m.update({"phase": "watchdog_control", "instance": tag, "cell": "n/a", "label": "n/a",
              "engine": "watchdog_null_object", "config": tag,
              "host_at_launch": host,
              "peak_rss_gib_observed": round(m["peak_rss_kb"] / (1 << 20), 3),
              "stdout_text_tail": (RUN_DIR / m["stdout"]).read_text(errors="replace")[-1500:]})
    R.record(m)
    return m


def main():
    avail_gib = mem_available_kb() / (1 << 20)
    # Direction (i): scaled to fit the host. Limit 2 GiB, target 4 GiB (2x the limit), which
    # needs at most ~2.5 GiB resident before the watchdog fires.
    resident_limit_gb = 2
    resident_target_mib = 4096
    res = one("watchdog_null_resident",
              [sys.executable, str(WD / "null_resident.py"),
               "--target-mib", str(resident_target_mib), "--step-mib", "128", "--hold-s", "0.05"],
              limit_gb=resident_limit_gb, timeout=300,
              extra={"direction": "(i) resident growth, must be KILLED",
                     "declared_limit_gb": 8, "declared_target_gib": 12,
                     "limit_used_gb": resident_limit_gb,
                     "target_mib_used": resident_target_mib,
                     "scaling_reason": (f"MemAvailable {avail_gib:.2f} GiB with SwapTotal 0: a 12 GiB"
                                        " resident allocation under an 8 GiB watchdog cannot be"
                                        " reached without invoking the kernel OOM killer, which"
                                        " would measure the OOM killer and not the watchdog"),
                     "allocation_schedule": "128 MiB per step, one byte written per 4096-byte page,"
                                            " 0.05 s hold per step; no randomness, no seed",
                     "expected": "killed with rss_limit_breached true"})

    # Direction (ii): the DECLARED 8 GiB limit; touches 256 MiB, reserves 64 GiB.
    asr = one("watchdog_null_addressspace",
              [sys.executable, str(WD / "null_addressspace.py"),
               "--reserve-gib", "64", "--touch-mib", "256", "--hold-s", "5"],
              limit_gb=8, timeout=300,
              extra={"direction": "(ii) address-space reservation, must NOT be killed",
                     "declared_limit_gb": 8, "limit_used_gb": 8,
                     "reserve_gib": 64, "touch_mib": 256,
                     "allocation_schedule": "one mmap of 64 GiB PROT_NONE|MAP_NORESERVE, never"
                                            " touched; then 256 MiB touched one byte per page;"
                                            " then held 5 s so many polls occur; no seed",
                     "expected": "exit 0 with rss_limit_breached false"})

    out = {"direction_i": {k: res.get(k) for k in
                           ("wall_s", "returncode", "timed_out", "rss_limit_breached",
                            "peak_rss_kb", "peak_rss_gib_observed", "rss_limit_gb",
                            "rss_poll_interval_s", "rss_polls", "limit_used_gb",
                            "target_mib_used", "scaling_reason", "stdout_text_tail")},
           "direction_ii": {k: asr.get(k) for k in
                            ("wall_s", "returncode", "timed_out", "rss_limit_breached",
                             "peak_rss_kb", "peak_rss_gib_observed", "rss_limit_gb",
                             "rss_poll_interval_s", "rss_polls", "reserve_gib", "touch_mib",
                             "stdout_text_tail")},
           "host_at_end": host_state()}
    out["measured"] = {
        "i_killed_by_watchdog": bool(res.get("rss_limit_breached")),
        "i_observed_peak_gib": res.get("peak_rss_gib_observed"),
        "i_limit_gib": res.get("limit_used_gb"),
        "i_peak_within_polling_tolerance": (
            res.get("peak_rss_kb", 0) >= res.get("limit_used_gb", 0) * (1 << 20)
            and res.get("peak_rss_kb", 0) <= (res.get("limit_used_gb", 0) + 0.5) * (1 << 20)),
        "ii_survived": asr.get("returncode") == 0 and not asr.get("rss_limit_breached"),
        "ii_observed_peak_gib": asr.get("peak_rss_gib_observed"),
    }
    (LOGS / "watchdog_null.json").write_text(json.dumps(out, indent=1, default=str))
    (WD / "outcomes.json").write_text(json.dumps({"direction_i": res, "direction_ii": asr},
                                                 indent=1, default=str))
    emit("watchdog_null", out)


if __name__ == "__main__":
    main()
