#!/usr/bin/env python3
"""Blind re-derivation of the n83 stacked primary ratio and the A/A / planted controls.

Written from protocol.json "statistics" and "controls_pass_rule" ALONE, without
reading the producer's verify_receipt.py, run_schedule.py, arm.py, README.md or
panel/result.json. Reads the raw per-run stdout (raw_b64 producer JSON) under
panel/runs/ and the run index panel/runs.jsonl. Writes nothing except stdout.

Definitions (protocol.json statistics):
  E2E(k, c) = mean over k's rank processes of timing_ms.rank_stage
            + mean over the cold points of cold_in_process_ms(c)
  R = E2E(kP, cP) / E2E(kS, cS)
  bootstrap: cold points resampled (paired across arms) and, independently for
  each rank process, its attempts resampled (non-attempt time kept); 10,000
  draws, seed 20261016.  RNG family and CI method are not specified in the
  protocol; this script uses Python random.Random(seed) and the 2.5/97.5
  percentile interval, so CI endpoints are expected to agree only approximately.
controls_pass_rule:
  aa: E2E(kS+cS)/E2E(kSaa+cSaa) and cold cS/cSaa point estimates in [0.97, 1.03]
  planted: cSX/cS ratio of mean cold totals, 95% bootstrap lower bound above 1
"""
import base64
import json
import random
import sys
from pathlib import Path

panel = Path(sys.argv[1])
rows = [json.loads(l) for l in (panel / "runs.jsonl").read_text().splitlines() if l.strip()]


def raw(row):
    txt = (panel / row["stdout_file"]).read_text()
    line = [l for l in txt.splitlines() if l.startswith("raw_b64=")]
    assert len(line) == 1, row["stdout_file"]
    return json.loads(base64.b64decode(line[0][len("raw_b64="):]))


def summary(o):
    s = [r for r in o["records"] if r.get("kind") == "compact_orbit_dlp_summary"]
    assert len(s) == 1
    return s[0]


cold = {}   # arm -> {point_id: cold_in_process_ms}
rank = {}   # arm -> list of (block/panel, rank_stage_ms, [attempt_ms])
statuses = {}
for row in rows:
    statuses[row["status"]] = statuses.get(row["status"], 0) + 1
    if row["segment"].startswith("O"):
        continue  # Q0 exactness segment, not a cold point
    o = raw(row)
    if row["arm"] == "rT":
        continue
    s = summary(o)
    if row["segment"].startswith("C"):
        cold.setdefault(row["arm"], {})[row["point_id"]] = float(s["cold_in_process_ms"])
    elif row["segment"].startswith("K"):
        att = [x / 1e6 for x in s["rank_attempt_ns"]]
        rank.setdefault(row["arm"], []).append((o["panel"], float(s["timing_ms"]["rank_stage"]), att))

points = sorted(cold["cS"].keys())
print("status counts", statuses)
print("cold points", len(points), "per arm", {a: len(v) for a, v in cold.items()})
print("rank processes per arm", {a: [(p, round(t, 3), len(at)) for p, t, at in v] for a, v in rank.items()})
for a in cold:
    assert sorted(cold[a].keys()) == points, a


def mean(xs):
    return sum(xs) / len(xs)


def e2e(k, c, pts=None, rank_override=None):
    pts = points if pts is None else pts
    rk = rank_override[k] if rank_override else [t for _, t, _ in rank[k]]
    return mean(rk) + mean([cold[c][p] for p in pts])


R = e2e("kP", "cP") / e2e("kS", "cS")
aa_e2e = e2e("kS", "cS") / e2e("kSaa", "cSaa")
aa_cold = mean([cold["cS"][p] for p in points]) / mean([cold["cSaa"][p] for p in points])
planted = mean([cold["cSX"][p] for p in points]) / mean([cold["cS"][p] for p in points])
print("E2E(kP,cP) ms", e2e("kP", "cP"), " E2E(kS,cS) ms", e2e("kS", "cS"))
print("mean rank_stage kP", mean([t for _, t, _ in rank["kP"]]), "kS", mean([t for _, t, _ in rank["kS"]]))
print("mean cold cP", mean([cold["cP"][p] for p in points]), "cS", mean([cold["cS"][p] for p in points]))
print("R point", R)
print("AA e2e point", aa_e2e, "in [0.97,1.03]:", 0.97 <= aa_e2e <= 1.03)
print("AA cold point", aa_cold, "in [0.97,1.03]:", 0.97 <= aa_cold <= 1.03)
print("planted point", planted)

rng = random.Random(20261016)
B = 10000
rs, aas, pls = [], [], []
for _ in range(B):
    pts = [points[rng.randrange(len(points))] for _ in points]
    ro = {}
    for k, procs in rank.items():
        vals = []
        for _, t, att in procs:
            non_att = t - sum(att)
            vals.append(non_att + sum(att[rng.randrange(len(att))] for _ in att))
        ro[k] = vals
    rs.append(e2e("kP", "cP", pts, ro) / e2e("kS", "cS", pts, ro))
    aas.append(e2e("kS", "cS", pts, ro) / e2e("kSaa", "cSaa", pts, ro))
    pls.append(mean([cold["cSX"][p] for p in pts]) / mean([cold["cS"][p] for p in pts]))


def ci(xs):
    xs = sorted(xs)
    return xs[int(0.025 * len(xs))], xs[int(0.975 * len(xs)) - 1]


print("R CI (percentile, python random)", ci(rs))
print("AA e2e CI", ci(aas))
print("planted CI", ci(pls), "lower>1:", ci(pls)[0] > 1)
lo, hi = ci(rs)
verdict = "improvement" if lo > 1 else ("regression" if hi < 1 else "not_separated")
print("decision (controls pass required):", verdict)
# non-attempt share of rank_stage, to show what the attempt bootstrap leaves fixed
for k, procs in rank.items():
    for p, t, att in procs:
        print("rank", k, p, "stage_ms", round(t, 1), "attempts", len(att), "sum_att_ms", round(sum(att), 1),
              "non_att_ms", round(t - sum(att), 1))
