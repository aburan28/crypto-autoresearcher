#!/usr/bin/env python3
"""Cross-check the new op counters against fields the uncounted producer already emitted (and that the
archived run 38862448935 carries), for every IC and rho record of run 39882571652.

If a counter measures what its name says, it must equal (or stand in a fixed relation to) the
pre-existing field: s3_root_solves vs root_calls, root_index_probes vs probes, rank-stage solves and
probes vs rank_root_calls_total / rank_probes_total, setup inserts vs stored states, rho
partition_hashes vs walk_steps. Reads the run's stdout files as data only.
"""
import base64
import json
import sys
from pathlib import Path

panel = Path(sys.argv[1])
runs = [json.loads(l) for l in Path(sys.argv[2]).read_text().splitlines() if l.strip()]
out = Path(sys.argv[3])


def dec(p):
    lines = p.read_text().splitlines()
    return json.loads(base64.b64decode([l for l in lines if l.startswith("raw_b64=")][0][8:]))


checks = {}
def chk(name, ok):
    checks.setdefault(name, [0, 0])
    checks[name][0 if ok else 1] += 1

for row in runs:
    rec = dec(panel / row["stdout_file"])
    if row["arm"] == "rT":
        o = rec["records"][0]["outcome"]
        c = o["charges_setup_and_solve"]
        chk("rho partition_hashes == walk_steps", c["partition_hashes"] == o["walk_steps"])
        chk("rho group_additions == walk_steps + walks + 1", c["group_additions"] == o["walk_steps"] + o["walks"] + 1)
        chk("rho canonicalizations == group_additions - 1", c["canonicalizations"] == c["group_additions"] - 1)
        chk("rho table_inserts == table_entries", c["table_inserts"] == o["table_entries"])
        chk("rho failed_collisions == 0", c["failed_collisions"] == 0)
        continue
    t = [r for r in rec["records"] if r.get("kind") == "compact_orbit_dlp_target"][0]
    s = [r for r in rec["records"] if r.get("kind") == "compact_orbit_dlp_summary"][0]
    tc, ph = t["op_counts"], s["op_counts"]["phases"]
    chk("target s3_root_solves == root_calls", tc["s3_root_solves"] == t["root_calls"])
    chk("target root_index_probes == probes", tc["root_index_probes"] == t["probes"])
    chk("target canonicalizations == 2*root_solves + relation-side extras (>= 2*solves)", tc["canonicalizations"] >= 2 * tc["s3_root_solves"])
    chk("setup root_index_inserts == 2*stored_states", ph["setup"]["root_index_inserts"] == 2 * s["stored_states"])
    if row["arm"] in ("kS", "kP"):
        chk("rank s3_root_solves == rank_root_calls_total", ph["rank_stage"]["s3_root_solves"] == s["rank_root_calls_total"])
        chk("rank root_index_probes == rank_probes_total", ph["rank_stage"]["root_index_probes"] == s["rank_probes_total"])
        chk("rank ec_scalar_mul == rank_attempts", ph["rank_stage"]["ec_scalar_mul"] == s["rank_attempts"])
        chk("rank la_inversions == rank", ph["rank_stage"]["la_inversions"] == s["rank"])
    chk("ec_frobenius == 0 in every phase (base loaded, not constructed)",
        all(p.get("ec_frobenius", 0) == 0 for p in ph.values()) and tc.get("ec_frobenius", 0) == 0)

out.write_text(json.dumps(checks, indent=1) + "\n")
print(json.dumps(checks, indent=1))
