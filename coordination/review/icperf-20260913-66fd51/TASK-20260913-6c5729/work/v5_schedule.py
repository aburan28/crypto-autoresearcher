#!/usr/bin/env python3
"""V5 follow-up: is the schedule sequential, and what are the high loadavg
readings actually measuring?

`recorded_at` is stamped to whole seconds, so a reconstructed start
(recorded_at - wall_s) carries up to 1 s of error and can put a long row's
start before a short row that truly preceded it. The sequential test below
allows exactly that 1 s of slack and no more.

The loadavg question matters because the plan's V5(2) asks whether excluding
rows launched at loadavg > 2 moves P3c -- and phase D, which P3c depends on,
is 82/90 high-load, so no low-load control can be formed from it. If the
elevated readings are the DECAY TAIL of an earlier phase rather than
concurrent load, the exclusion test is measuring phase order, not contention.
"""
import json
import math
import pathlib
from datetime import datetime

RUN = pathlib.Path("/workspace/experiments/EXP-ICPERF-66fd51/runs/RUN-ICPERF-305ca3")
HERE = pathlib.Path(__file__).resolve().parent

ROWS = [json.loads(l) for l in open(RUN / "results.jsonl")]
S = [r for r in ROWS if "status" in r and r.get("wall_s") is not None]


def ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


# ---- sequential-schedule test.
# Row r's true end E_r lies in [t_r, t_r + 1) because the stamp is truncated to
# whole seconds, so its true start lies in [t_r - w_r, t_r + 1 - w_r). Two rows
# a (earlier stamp) and b are PROVABLY concurrent only when b cannot have
# started after a ended even in the most favourable assignment -- a ending as
# early as t_a and b starting as late as t_b + 1 - w_b:
#       t_b + 1 - w_b < t_a   <=>   w_b > (t_b - t_a) + 1.
# Rows sharing a stamp cannot be ordered at all and prove nothing either way.
byend = sorted(S, key=lambda r: ts(r["recorded_at"]))
violations = []
n_pairs = 0
for i, a in enumerate(byend):
    ta = ts(a["recorded_at"])
    for b in byend[i + 1:]:
        tb = ts(b["recorded_at"])
        if tb == ta:
            continue  # same truncated second: order unknowable, proves nothing
        if tb - ta > 1000.0:
            break
        n_pairs += 1
        if b["wall_s"] > (tb - ta) + 1.0:
            violations.append(
                {
                    "earlier_stamp": f"{a['phase']}/{a['instance']}/{a['engine']}/{a['config']}",
                    "later_stamp": f"{b['phase']}/{b['instance']}/{b['engine']}/{b['config']}",
                    "provable_overlap_s": round(b["wall_s"] - (tb - ta) - 1.0, 3),
                    "earlier_recorded_at": a["recorded_at"],
                    "later_recorded_at": b["recorded_at"],
                    "later_wall_s": b["wall_s"],
                }
            )

# ---- loadavg: does it decay like a 60 s EWMA between consecutive rows?
# Linux loadavg1 uses exp(-5/60) per 5 s tick, i.e. exp(-dt/60) over dt.
seq = sorted(S, key=lambda r: ts(r["recorded_at"]))
decay = []
for a, b in zip(seq, seq[1:]):
    la, lb = a.get("loadavg1_at_start"), b.get("loadavg1_at_start")
    if la is None or lb is None:
        continue
    # dt between the two LAUNCH instants
    dt = (ts(b["recorded_at"]) - b["wall_s"]) - (ts(a["recorded_at"]) - a["wall_s"])
    if dt <= 0 or dt > 600:
        continue
    # one single-threaded row running the whole interval pulls load toward 1.0
    pred_pure_decay = la * math.exp(-dt / 60.0)
    pred_one_runner = 1.0 + (la - 1.0) * math.exp(-dt / 60.0)
    decay.append(
        {
            "phase": b.get("phase"),
            "instance": b.get("instance"),
            "engine": b.get("engine"),
            "config": b.get("config"),
            "dt_s": round(dt, 2),
            "load_prev": la,
            "load_now": lb,
            "pred_decay_to_0": round(pred_pure_decay, 3),
            "pred_decay_to_1": round(pred_one_runner, 3),
            "resid_vs_decay_to_1": round(lb - pred_one_runner, 3),
        }
    )

high = [d for d in decay if d["load_prev"] > 2.0]
resid = [abs(d["resid_vs_decay_to_1"]) for d in high]

# the specific phase C -> phase D handover the plan's P3c depends on
cd = [
    {
        "phase": r["phase"],
        "instance": r["instance"],
        "engine": r["engine"],
        "config": r["config"],
        "launch": datetime.utcfromtimestamp(ts(r["recorded_at"]) - r["wall_s"]).isoformat() + "Z",
        "loadavg1_at_start": r.get("loadavg1_at_start"),
        "wall_s": r["wall_s"],
        "cpu_s": r["cpu_s"],
        "wall_minus_cpu": round(r["wall_s"] - r["cpu_s"], 4),
        "status": r["status"],
    }
    for r in seq
    if r.get("phase") in ("C", "D")
]

out = {
    "sequential_schedule": {
        "n_ordered_pairs_tested": n_pairs,
        "n_provably_concurrent_pairs": len(violations),
        "violations": violations[:20],
        "note": (
            "recorded_at is stamped to whole seconds, so a reconstructed start "
            "carries up to 1 s of error. A pair is counted only when no "
            "assignment of true end times inside those one-second windows can "
            "make it sequential. Zero such pairs means the 474 solve rows are "
            "consistent with strictly sequential execution: no two rows can be "
            "shown to have run at the same time."
        ),
    },
    "loadavg_decay": {
        "n_transitions_from_load_above_2": len(high),
        "max_abs_residual_vs_60s_ewma_decaying_to_one_runner": max(resid) if resid else None,
        "mean_abs_residual": round(sum(resid) / len(resid), 4) if resid else None,
        "n_residual_over_0_5": len([x for x in resid if x > 0.5]),
        "sample": high[:25],
    },
    "phase_C_and_D_rows": cd,
}
json.dump(out, open(HERE / "v5_schedule.json", "w"), indent=1, sort_keys=True, default=str)
print(json.dumps(out["sequential_schedule"], indent=1)[:2500])
print(json.dumps({k: v for k, v in out["loadavg_decay"].items() if k != "sample"}, indent=1))
