"""V3/V5: does the Coordinator-written manifest_v2.yaml / task-report.md narrative
match results.jsonl? Recomputes status counts per (phase, engine, config), per-phase
row counts and wall/cpu sums, host wall, gap count, hashcheck flags, MAX_ID presence,
and the per-cell median table of task-report.md section 7. Pure arithmetic."""
import json, os, statistics as st
from collections import Counter, defaultdict
from datetime import datetime, timezone

ROOT = "/workspace"
RUN = f"{ROOT}/experiments/EXP-ICPERF-66fd51/runs/RUN-ICPERF-305ca3"
HERE = os.path.dirname(os.path.abspath(__file__))
rows = [json.loads(l) for l in open(f"{RUN}/results.jsonl") if l.strip()]

def ts(s): return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).timestamp()
def finished(r): return r.get("status") in ("SAT", "UNSAT", "finished")
def med(v):
    v = [x for x in v if x is not None]
    return (st.median(v), len(v)) if v else (None, 0)

out = {"n_rows": len(rows)}

# status counts per phase/engine/config (manifest_v2 result.status_counts)
sc = defaultdict(Counter)
for r in rows:
    key = f"{r.get('phase')}_{r.get('engine')}_{r.get('config')}"
    if r.get("engine") == "certificate":
        key = f"{r.get('phase')}_certificate_shipped"
        sc[key][f"verified_{str(r.get('verified')).lower()}"] += 1
    else:
        sc[key][r.get("status")] += 1
out["status_counts"] = {k: dict(v) for k, v in sorted(sc.items())}

manifest_claims = {
    "A_certificate_shipped": {"verified_true": 30},
    "A_wdsat_default": {"SAT": 31, "UNSAT": 29},
    "A_wdsat_core_order": {"SAT": 31, "UNSAT": 29},
    "A_wdsat_symmetry": {"SAT": 31, "UNSAT": 29},
    "A_wdsat_gauss_elim": {"SAT": 31, "UNSAT": 29},
    "A_wdsat_noncore_first": {"SAT": 6, "UNSAT": 2, "budget_stop_timeout": 22},
    "A_wdsat_default_on_null_object": {"SAT": 7, "UNSAT": 2, "budget_stop_timeout": 9},
    "B_cryptominisat5_cnf_xor": {"SAT": 31, "UNSAT": 27, "budget_stop_timeout": 2},
    "C_macaulay2_F4_ZZ2_fieldeqs_grevlex": {"infrastructure_exit_-6": 32},
    "D_cadical_pure_cnf": {"SAT": 15, "UNSAT": 15},
    "D_cryptominisat5_pure_cnf": {"SAT": 15, "UNSAT": 15},
    "D_minisat_pure_cnf": {"SAT": 14, "UNSAT": 14, "budget_stop_timeout": 2},
    "E_singular_std_GF2_fieldeqs_dp": {"budget_stop_timeout": 4},
}
cmp = {}
for k, claim in manifest_claims.items():
    got = {kk: vv for kk, vv in out["status_counts"].get(k, {}).items() if vv}
    cmp[k] = {"manifest": claim, "results_jsonl": got, "equal": got == claim}
out["status_counts_vs_manifest_v2"] = cmp
out["all_status_counts_equal"] = all(v["equal"] for v in cmp.values())

# certificate rows
cert = [r for r in rows if r.get("engine") == "certificate"]
out["certificate_rows"] = {"n": len(cert), "verified_true": sum(1 for r in cert if r.get("verified") is True),
                           "why_values": dict(Counter(r.get("why") for r in cert))}

# per-phase rows, wall and cpu sums
ph = defaultdict(lambda: {"rows": 0, "wall": 0.0, "cpu": 0.0, "cpu_rows": 0})
for r in rows:
    p = r.get("phase"); ph[p]["rows"] += 1
    if r.get("wall_s") is not None: ph[p]["wall"] += r["wall_s"]
    if r.get("cpu_s") is not None: ph[p]["cpu"] += r["cpu_s"]; ph[p]["cpu_rows"] += 1
out["per_phase"] = {p: {"rows": v["rows"], "wall_sum": round(v["wall"], 1), "cpu_sum": round(v["cpu"], 1), "cpu_rows": v["cpu_rows"]} for p, v in sorted(ph.items())}
out["per_phase_manifest_v2"] = {"rows": {"A": 318, "B": 60, "C": 32, "D": 90, "E": 4},
                                "wall": {"A": 5508, "B": 3158, "C": 299, "D": 4657, "E": 3600}}
out["per_phase_rows_equal"] = all(out["per_phase"][p]["rows"] == out["per_phase_manifest_v2"]["rows"][p] for p in "ABCDE")
out["per_phase_wall_within_1s"] = {p: abs(out["per_phase"][p]["wall_sum"] - out["per_phase_manifest_v2"]["wall"][p]) <= 1.0 for p in "ABCDE"}
out["measured_solver_wall_seconds_sum"] = {"validator": round(sum(r.get("wall_s") or 0 for r in rows), 1), "manifest_v2": 17223}
out["measured_solver_cpu_seconds_sum"] = {"validator": round(sum(r.get("cpu_s") or 0 for r in rows), 1), "manifest_v2": 17705}

# host wall from launch_time.txt to last recorded_at
launch = open(f"{RUN}/launch_time.txt").read().strip()
last = max(r["recorded_at"] for r in rows)
try:
    out["host_wall_s"] = {"launch_time.txt": launch, "last_recorded_at": last,
                          "validator": ts(last) - ts(launch[:19] + "Z" if not launch.endswith("Z") else launch), "manifest_v2": 120205}
except Exception as e:
    out["host_wall_s"] = {"launch_time.txt": launch, "last_recorded_at": last, "error": str(e)}

# per-phase host wall from phase_log.txt (as recorded there) -- just carry the file
out["phase_log.txt"] = open(f"{RUN}/phase_log.txt").read().strip().splitlines()

# gaps > 900 s in recorded_at order (manifest: exactly two)
srt = sorted(rows, key=lambda r: r["recorded_at"])
gaps = []
for a, b in zip(srt, srt[1:]):
    g = ts(b["recorded_at"]) - ts(a["recorded_at"])
    if g > 900: gaps.append((g, a["instance"], a["engine"], a["config"], b["instance"], b["engine"], b["config"]))
out["gaps_over_900s"] = gaps
out["gaps_over_900s_count_vs_manifest_2"] = len(gaps) == 2

# "no row has wall_s > 2*cpu_s + 2" (task-report s.5) and manifest wording
bad = [(r["instance"], r["engine"], r["config"], r["wall_s"], r.get("cpu_s")) for r in rows if r.get("cpu_s") is not None and r["wall_s"] > 2 * r["cpu_s"] + 2]
out["rows_wall_over_2cpu_plus_2"] = bad

# loadavg > 2 by phase (task-report s.4: A 2, B 7, C 31, D 82, E 3; total 125; max 4.55)
la = [r for r in rows if r.get("loadavg1_at_start") is not None and r["loadavg1_at_start"] > 2]
out["loadavg_over_2"] = {"total": len(la), "by_phase": dict(Counter(r["phase"] for r in la)),
                         "max": max((r["loadavg1_at_start"] for r in rows if r.get("loadavg1_at_start") is not None), default=None),
                         "A_rows": [(r["instance"], r["config"], r["loadavg1_at_start"]) for r in la if r["phase"] == "A"],
                         "B_rows": sorted((r["instance"], r["loadavg1_at_start"]) for r in la if r["phase"] == "B")}
out["loadavg_rows_missing_field"] = sum(1 for r in rows if r.get("loadavg1_at_start") is None)

# hashcheck on phase D
D = [r for r in rows if r.get("phase") == "D"]
out["phase_D_hashcheck"] = {"rows": len(D), "match_true": sum(1 for r in D if (r.get("pure_cnf_hashcheck") or {}).get("match") is True)}
hc_files = sorted(f for f in os.listdir(f"{RUN}/pure_cnf") if f.endswith(".hashcheck.json"))
out["pure_cnf_hashcheck_files"] = {"n": len(hc_files), "match_true": sum(1 for f in hc_files if json.load(open(f"{RUN}/pure_cnf/{f}")).get("match") is True)}

# MAX_ID presence on WDSat rows (invalidation rule 2 -- value equality checked in v4_null_shapes.py)
W = [r for r in rows if r.get("engine") == "wdsat"]
out["wdsat_rows_with_wdsat_constants_MAX_ID"] = {"wdsat_rows": len(W), "with_MAX_ID": sum(1 for r in W if (r.get("wdsat_constants") or {}).get("MAX_ID") is not None)}

# null rows shape flag
N = [r for r in rows if r.get("config") == "default_on_null_object"]
out["null_rows_shape_matches_template"] = {"rows": len(N), "true": sum(1 for r in N if r.get("shape_matches_template") is True)}

# task-report section 7 median table (wall_s medians over finished rows)
cols = [("wdsat", "default"), ("wdsat", "core_order"), ("wdsat", "symmetry"), ("wdsat", "gauss_elim"), ("wdsat", "noncore_first"),
        ("wdsat", "default_on_null_object"), ("cryptominisat5", "cnf_xor"), ("cryptominisat5", "pure_cnf"), ("cadical", "pure_cnf"),
        ("minisat", "pure_cnf"), ("macaulay2_F4_ZZ2_fieldeqs", "grevlex"), ("singular_std_GF2_fieldeqs", "dp")]
table = {}
for cell in ("n15l5", "n17l6", "n19l6"):
    for lab in ("S", "U"):
        row = {}
        for e, c in cols:
            m, k = med([r["wall_s"] for r in rows if r.get("engine") == e and r.get("config") == c and r.get("cell") == cell and r.get("label") == lab and finished(r)])
            row[f"{e}/{c}"] = (round(m, 4) if m is not None else None, k)
        table[f"{cell}/{lab}"] = row
out["task_report_s7_table_recomputed"] = table
report_table = {  # transcribed from task-report.md section 7 (wall medians; (n) where given)
    "n15l5/S": [0.0651, 0.0649, 0.0328, 0.2656, (14.2562, 5), (27.2847, 3), (0.4414, 10), 0.4668, 0.7172, (2.2725, 5), None, None],
    "n15l5/U": [0.2160, 0.2159, 0.0654, 1.1183, (114.5009, 2), (17.2610, 3), (9.8681, 10), 12.5040, 3.6272, (7.0860, 5), None, None],
    "n17l6/S": [0.2909, 0.2908, 0.1406, 1.8455, (80.2237, 1), (29.9413, 1), (13.8022, 10), 3.0242, 7.3359, (12.9997, 5), None, None],
    "n17l6/U": [2.3216, 2.3214, 0.4164, 16.7068, (None, 0), (49.9407, 2), (81.1419, 10), 80.0281, 51.7916, (105.3739, 5), None, None],
    "n19l6/S": [0.3162, 0.3162, 0.1407, 1.9952, (None, 0), (None, 0), (21.2779, 10), 21.3309, 9.6440, (65.2518, 4), None, None],
    "n19l6/U": [2.3471, 2.3716, 0.4166, 16.5063, (None, 0), (None, 0), (121.8064, 8), 195.9794, 56.8536, (123.5298, 4), None, None],
}
diffs = []
for key, vals in report_table.items():
    for (e, c), v in zip(cols, vals):
        got_m, got_n = table[key][f"{e}/{c}"]
        if isinstance(v, tuple):
            want_m, want_n = v
            if (want_m is None) != (got_m is None) or (want_m is not None and abs(want_m - got_m) > 0.00051) or want_n != got_n:
                diffs.append((key, f"{e}/{c}", v, (got_m, got_n)))
        else:
            if (v is None) != (got_m is None) or (v is not None and abs(v - got_m) > 0.00051):
                diffs.append((key, f"{e}/{c}", v, (got_m, got_n)))
out["task_report_s7_table_diffs"] = diffs

json.dump(out, open(f"{HERE}/v3v5_manifest_narrative.json", "w"), indent=1, default=str)
print(json.dumps({k: out[k] for k in ("n_rows", "all_status_counts_equal", "certificate_rows", "per_phase", "per_phase_rows_equal",
                                       "per_phase_wall_within_1s", "measured_solver_wall_seconds_sum", "measured_solver_cpu_seconds_sum",
                                       "host_wall_s", "gaps_over_900s_count_vs_manifest_2", "rows_wall_over_2cpu_plus_2", "loadavg_over_2",
                                       "loadavg_rows_missing_field", "phase_D_hashcheck", "pure_cnf_hashcheck_files",
                                       "wdsat_rows_with_wdsat_constants_MAX_ID", "null_rows_shape_matches_template",
                                       "task_report_s7_table_diffs")}, indent=1, default=str))
for k, v in out["status_counts_vs_manifest_v2"].items():
    if not v["equal"]: print("STATUS MISMATCH", k, v)
