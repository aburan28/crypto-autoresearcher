#!/usr/bin/env python3
"""EXP-DREG-002 control: verify the n=17 null full-rank cell, partition A
(review correction C1: sr_pred_D = 126,922 must be MEASURED, not assumed).

Reads (READ-ONLY) EXP-DREG-001/runs/RUN-DREG-001-MEASURE-N17-NULL-A
(chunk_force 24000, 17 units), copies its result/state JSONs into this run's
work dir, sha256-pins them, verifies every checkpoint carry hash, checks the
unit arithmetic, and compares the measured rank against sr_pred_D = 126,922.

The null-arm two-partition gate (AMD-20260718-002) additionally requires the
chunk-20000 partition B; that replication status is recorded, not assumed.

Writes raw.json into the run dir. Exit 0 iff every performed check passes.
Never writes outside the run dir. Never writes into EXP-DREG-001.
"""
import hashlib, json, re, shutil, sys
from pathlib import Path

WS = Path(__file__).resolve().resolve().parent.parent.parent.parent
E1 = WS / "experiments" / "EXP-DREG-001" / "runs"
RUN_DIR = Path(sys.argv[1]).resolve()
WORK = RUN_DIR / "work"
WORK.mkdir(parents=True, exist_ok=True)

SR_PRED = 126922


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


failures = []
rd = E1 / "RUN-DREG-001-MEASURE-N17-NULL-A"
res_src = rd / "work" / "h012c_measure_n17_null_a_null_result_n17_t0.json"
st_src = rd / "work" / "h012c_measure_n17_null_a_null_n17_t0" / "state.json"
report = {"control": "null_n17_partition_A_verification_C1",
          "c1_prediction": SR_PRED, "failures": failures}

res_dst = WORK / res_src.name
st_dst = WORK / "state_partition_A.json"
shutil.copy2(res_src, res_dst)
shutil.copy2(st_src, st_dst)
res = json.loads(res_dst.read_text())
st = json.loads(st_dst.read_text())

carry_dir = st_src.parent
bad = [c["file"] for c in st["carries"]
       if sha256_file(carry_dir / c["file"]) != c["sha256"]]
if bad:
    failures.append(f"carry hash mismatch {bad}")

contig = all(u["j0"] == (st["units"][i - 1]["j1"] if i else 0)
             for i, u in enumerate(st["units"]))
sumk = sum(u["k"] for u in st["units"])
if not contig:
    failures.append("units not contiguous")
if sumk != st["rank_acc"] or st["rank_acc"] != res["rank"]:
    failures.append(f"rank arithmetic mismatch sum_k={sumk} "
                    f"state={st['rank_acc']} result={res['rank']}")
if not (st["done"] and st["next_col"] == st["ncols"]):
    failures.append("not terminal")
if res["pred"] != SR_PRED:
    failures.append(f"pred {res['pred']} != {SR_PRED}")

txt = (rd / "manifest.yaml").read_text()
def grab(key):
    m = re.search(rf"^\s*{key}: (.+)$", txt, re.M)
    return m.group(1).strip() if m else None

report.update({
    "source_run": "RUN-DREG-001-MEASURE-N17-NULL-A",
    "chunk_force": 24000,
    "copied_sha256": {res_dst.name: sha256_file(res_dst),
                      st_dst.name: sha256_file(st_dst)},
    "carries_checked": len(st["carries"]),
    "carries_hash_ok": not bad,
    "units": len(st["units"]), "units_contiguous": contig,
    "sum_k": sumk, "rank_state": st["rank_acc"],
    "done": st["done"], "next_col_eq_ncols": st["next_col"] == st["ncols"],
    "system_hash": res["system_hash"],
    "nrows": res["nrows"], "ncols": res["ncols"], "nb": res["nb"],
    "pred": res["pred"], "rank": res["rank"], "deficit": res["deficit"],
    "work_seconds": res["secs_total"],
    "completed_at_utc": res["completed_at_utc"],
    "manifest": {"status": grab("status"), "wall_seconds": grab("wall_seconds"),
                 "peak_rss_bytes": grab("peak_rss_bytes"),
                 "cpu_seconds": grab("cpu_seconds"), "commit": grab("commit"),
                 "instrument_sha256": grab("instrument_sha256")},
    "c1_check": {
        "sr_pred_D": SR_PRED,
        "measured_rank_partition_A": res["rank"],
        "rank_equals_sr_pred": res["rank"] == SR_PRED,
        "deficit": res["deficit"],
        "null_semi_regular_at_n17_partition_A": res["rank"] == SR_PRED,
    },
    "null_arm_partition_gate": {
        "partition_A_chunk_24000": "measured + verified here",
        "partition_B_chunk_20000": "pending (EXP-DREG-002 RUN-DREG-002-MEASURE-N17-NULL-B in progress at session cutoff; see its manifest)",
        "arm_gate_pass": False,
        "note": "AMD-20260718-002: no n=17 null value enters a fit/verdict until both partitions pass",
    },
})
report["verdict"] = "PASS" if not failures else "FAIL"
(RUN_DIR / "raw.json").write_text(json.dumps(report, indent=1) + "\n")
print(json.dumps({"verdict": report["verdict"], "failures": failures,
                  "rank": res["rank"], "sr_pred": SR_PRED,
                  "rank_equals_sr_pred": res["rank"] == SR_PRED}))
sys.exit(0 if not failures else 1)
