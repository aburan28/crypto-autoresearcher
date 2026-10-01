#!/usr/bin/env python3
"""Sample M2's VmRSS at 0.05 s over a full F4 run (mode=series) to compute the maximum RSS
growth over any 0.25 s window (ADD1-a worst-case inter-poll overshoot), or send SIGTERM at
T seconds (mode=sigterm T) to measure how long M2 takes to die and whether RSS grows during
the kill grace."""
import json, os, signal, subprocess, sys, time
mode = sys.argv[1]; script = sys.argv[2]
tsig = float(sys.argv[3]) if mode == "sigterm" else None
series = []
p = subprocess.Popen(["M2", "--script", script], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL, start_new_session=True)
t0 = time.monotonic(); sent = None; rc = None
while True:
    rc = p.poll()
    if rc is not None: break
    try:
        for ln in open(f"/proc/{p.pid}/status"):
            if ln.startswith("VmRSS"):
                series.append((round(time.monotonic() - t0, 3), int(ln.split()[1]))); break
    except OSError: pass
    if tsig is not None and sent is None and time.monotonic() - t0 >= tsig:
        os.killpg(p.pid, signal.SIGTERM); sent = time.monotonic() - t0
    if time.monotonic() - t0 > 300: p.kill(); break
    time.sleep(0.05)
tend = time.monotonic() - t0
out = {"mode": mode, "returncode": rc, "wall_s": round(tend, 3), "samples": len(series), "loadavg_start_end": None}
if series:
    peak = max(series, key=lambda s: s[1])
    out["peak_kb"] = peak[1]; out["peak_at_s"] = peak[0]; out["last_kb"] = series[-1][1]
    # max growth over any window of <= 0.25 s (and <= 0.30 s to cover sleep jitter)
    for W in (0.25, 0.30, 1.0, 5.25):
        best = (0, None, None)
        j = 0
        for i in range(len(series)):
            while j < len(series) and series[j][0] - series[i][0] <= W: j += 1
            for k in range(i + 1, j):
                d = series[k][1] - series[i][1]
                if d > best[0]: best = (d, series[i], series[k])
        out[f"max_growth_kb_in_{W}s"] = {"kb": best[0], "mib": round(best[0] / 1024, 1), "from": best[1], "to": best[2]}
    out["mean_rate_mib_per_s_to_peak"] = round(peak[1] / 1024 / peak[0], 1) if peak[0] else None
if sent is not None:
    out["sigterm_sent_at_s"] = round(sent, 3); out["died_after_sigterm_s"] = round(tend - sent, 3)
    after = [s for s in series if s[0] >= sent]
    out["rss_after_sigterm"] = {"first": after[0] if after else None, "max": max(after, key=lambda s: s[1]) if after else None, "n": len(after)}
print(json.dumps(out, indent=1))
json.dump({"summary": out, "series": series}, open(f"m2_{mode}.json", "w"))
