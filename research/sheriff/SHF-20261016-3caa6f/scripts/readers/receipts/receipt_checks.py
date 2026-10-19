"""Row-level receipt checks for the n83 stacked run (reads only; prints to stdout).
argv: panel_dir schedule.json binaries.sha256"""
import base64, hashlib, json, sys, statistics
from pathlib import Path
panel = Path(sys.argv[1]); sched = json.load(open(sys.argv[2]))
bins = {l.split()[1].rsplit('/', 1)[1]: l.split()[0] for l in open(sys.argv[3]) if l.strip()}
rows = [json.loads(l) for l in (panel / "runs.jsonl").read_text().splitlines() if l.strip()]
srun = {r["serial"]: (seg["id"], r) for seg in sched["segments"] for r in seg["runs"]}
print("scheduled", len(srun), "rows", len(rows), "serials equal:", sorted(srun) == sorted(r["serial"] for r in rows))
bad = []
gap = {}
wall = {}
for r in rows:
    seg, s = srun[r["serial"]]
    exp_bin = bins["rho_tuned_r770"] if r["arm"] == "rT" else bins["ic_online_stacked_r770"]
    if r["binary_sha256"] != exp_bin: bad.append(("binary", r["serial"]))
    if (r["arm"], r["point_id"], r["seed"], r["segment"]) != (s["arm"], s["point_id"], s["seed"], seg): bad.append(("sched", r["serial"]))
    cmd = r["command"]
    if cmd[cmd.index("--arm") + 1] != r["arm"]: bad.append(("cmd-arm", r["serial"]))
    if cmd[cmd.index("--seed") + 1] != str(r["seed"]): bad.append(("cmd-seed", r["serial"]))
    pt = cmd[cmd.index("--point") + 1].split(",")
    if pt != [str(v) for v in s["point"]]: bad.append(("cmd-point", r["serial"]))
    if r["returncode"] != 0 or r["timed_out"] or r["status"] != "valid": bad.append(("status", r["serial"]))
    for ev in ("oom", "oom_kill", "max"):
        if r["counters_after"]["memory_events"][ev] != r["counters_before"]["memory_events"][ev]: bad.append(("mem-" + ev, r["serial"]))
    txt = (panel / r["stdout_file"]).read_text()
    b64 = [l for l in txt.splitlines() if l.startswith("raw_b64=")][0][8:]
    rawbytes = base64.b64decode(b64)
    o = json.loads(rawbytes)
    cand = {hashlib.sha256(rawbytes).hexdigest(), hashlib.sha256(b64.encode()).hexdigest()}
    rh = r["fields"]["raw_result_sha256"]
    if rh not in cand: bad.append(("raw_sha_unmatched", r["serial"]))
    if r["arm"] != "rT":
        sm = [x for x in o["records"] if x.get("kind") == "compact_orbit_dlp_summary"][0]
        c = sm["cold_in_process_ms"]
        if c > r["process_wall_ms"]: bad.append(("interval>wall", r["serial"]))
        gap.setdefault(r["arm"], []).append(r["process_wall_ms"] - c)
        wall.setdefault(r["arm"], []).append(r["process_wall_ms"])
        if r["segment"].startswith("C") and abs(float(r["fields"]["setup_ms"]) + float(r["fields"]["online_ms"]) - c) > 5:
            pass
print("row problems:", bad[:20], "count", len(bad))
print("mean(process_wall - cold_in_process) ms per arm:", {a: round(statistics.mean(v), 1) for a, v in sorted(gap.items())})
m = {a: statistics.mean(v) for a, v in wall.items()}
print("rank-process wall ms:", {a: [round(x) for x in wall[a]] for a in ("kP", "kS", "kSaa")})
print("single-process wall ratio kP/kS:", m["kP"] / m["kS"], " cold wall ratio cP/cS (C only):",
      statistics.mean([r["process_wall_ms"] for r in rows if r["arm"] == "cP" and r["segment"].startswith("C")]) /
      statistics.mean([r["process_wall_ms"] for r in rows if r["arm"] == "cS" and r["segment"].startswith("C")]))
flags = [(r["serial"], r["arm"], r["segment"], r["contention_flags"], r["child_major_faults"]) for r in rows if r["contention_flags"] or r["child_major_faults"]]
print("contention/major-fault rows:", flags)
