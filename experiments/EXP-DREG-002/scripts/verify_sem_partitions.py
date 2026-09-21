#!/usr/bin/env python3
"""EXP-DREG-002 control: certify the n=17 sem full-rank cell by the
checkpoint-partition consistency gate (AMD-20260718-002).

Reads (READ-ONLY) the two EXP-DREG-001 partition runs:
  RUN-DREG-001-MEASURE-N17-SEM-A  (chunk_force 24000, 14 units)
  RUN-DREG-001-MEASURE-N17-SEM-B  (chunk_force 20000, 16 units)
Copies their result/state JSONs into this run's work dir, sha256-pins them,
verifies every checkpoint carry hash in both partitions, checks the unit
arithmetic, and requires identical system_hash / pred / rank / deficit.

Writes raw.json into the run dir. Exit 0 iff every check passes.
Never writes outside the run dir. Never writes into EXP-DREG-001.
"""
import hashlib, json, re, shutil, sys
from pathlib import Path

WS = Path(__file__).resolve().parent.parent.parent.parent  # workspace root
E1 = WS / "experiments" / "EXP-DREG-001" / "runs"
RUN_DIR = Path(sys.argv[1]).resolve()
WORK = RUN_DIR / "work"
WORK.mkdir(parents=True, exist_ok=True)

PRED_EXPECTED = 126922


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def manifest_fields(path):
    txt = path.read_text()
    def grab(key):
        m = re.search(rf"^\s*{key}: (.+)$", txt, re.M)
        return m.group(1).strip() if m else None
    return {
        "status": grab("status"),
        "wall_seconds": grab("wall_seconds"),
        "peak_rss_bytes": grab("peak_rss_bytes"),
        "cpu_seconds": grab("cpu_seconds"),
        "commit": grab("commit"),
        "instrument_sha256": grab("instrument_sha256"),
    }


failures = []
report = {"control": "checkpoint_partition_consistency_n17_sem",
          "gate": "EXP-DREG-001/amendments/AMD-20260718-002-n17-partitions.yaml",
          "partitions": {}}

parts = {
    "A": {"run": "RUN-DREG-001-MEASURE-N17-SEM-A", "chunk": 24000,
          "tag": "measure_n17_sem_a"},
    "B": {"run": "RUN-DREG-001-MEASURE-N17-SEM-B", "chunk": 20000,
          "tag": "measure_n17_sem_b"},
}

for label, meta in parts.items():
    rd = E1 / meta["run"]
    res_src = rd / "work" / f"h012c_{meta['tag']}_sem_result_n17_t0.json"
    st_src = rd / "work" / f"h012c_{meta['tag']}_sem_n17_t0" / "state.json"
    entry = {"source_run": meta["run"], "chunk_force": meta["chunk"]}

    if not res_src.exists() or not st_src.exists():
        failures.append(f"partition {label}: missing source artifacts")
        continue

    res_dst = WORK / res_src.name
    st_dst = WORK / f"state_partition_{label}.json"
    shutil.copy2(res_src, res_dst)
    shutil.copy2(st_src, st_dst)
    res = json.loads(res_dst.read_text())
    st = json.loads(st_dst.read_text())
    entry["copied_sha256"] = {res_dst.name: sha256_file(res_dst),
                              st_dst.name: sha256_file(st_dst)}

    # 1. checkpoint carry-chain integrity (read-only hash of EXP-DREG-001 files)
    carry_dir = st_src.parent
    bad = [c["file"] for c in st["carries"]
           if sha256_file(carry_dir / c["file"]) != c["sha256"]]
    entry["carries_checked"] = len(st["carries"])
    entry["carries_hash_ok"] = not bad
    if bad:
        failures.append(f"partition {label}: carry hash mismatch {bad}")

    # 2. unit arithmetic: contiguous coverage, sum(k) == rank, terminal state
    contig = all(u["j0"] == (st["units"][i - 1]["j1"] if i else 0)
                 for i, u in enumerate(st["units"]))
    sumk = sum(u["k"] for u in st["units"])
    entry["units"] = len(st["units"])
    entry["units_contiguous"] = contig
    entry["sum_k"] = sumk
    entry["rank_state"] = st["rank_acc"]
    entry["done"] = st["done"]
    entry["next_col_eq_ncols"] = st["next_col"] == st["ncols"]
    if not contig:
        failures.append(f"partition {label}: units not contiguous")
    if sumk != st["rank_acc"] or st["rank_acc"] != res["rank"]:
        failures.append(f"partition {label}: rank arithmetic mismatch "
                        f"sum_k={sumk} state={st['rank_acc']} result={res['rank']}")
    if not (st["done"] and st["next_col"] == st["ncols"]):
        failures.append(f"partition {label}: not terminal")

    # 3. cell numbers
    entry.update({
        "system_hash": res["system_hash"],
        "nrows": res["nrows"], "ncols": res["ncols"], "nb": res["nb"],
        "pred": res["pred"], "rank": res["rank"], "deficit": res["deficit"],
        "work_seconds": res["secs_total"],
        "completed_at_utc": res["completed_at_utc"],
    })
    if res["pred"] != PRED_EXPECTED:
        failures.append(f"partition {label}: pred {res['pred']} != {PRED_EXPECTED}")
    if res["deficit"] != res["pred"] - res["rank"]:
        failures.append(f"partition {label}: deficit arithmetic wrong")

    # 4. resources from the EXP-DREG-001 manifest (coordinator receipts)
    mf = manifest_fields(rd / "manifest.yaml")
    entry["manifest"] = mf

    report["partitions"][label] = entry

# cross-partition identity (the AMD acceptance gate)
if len(report["partitions"]) == 2:
    a, b = report["partitions"]["A"], report["partitions"]["B"]
    same = (a["system_hash"] == b["system_hash"] and a["pred"] == b["pred"]
            and a["rank"] == b["rank"] and a["deficit"] == b["deficit"]
            and a["nrows"] == b["nrows"] and a["ncols"] == b["ncols"])
    report["cross_partition"] = {
        "system_hash_identical": a["system_hash"] == b["system_hash"],
        "pred_identical": a["pred"] == b["pred"],
        "rank_identical": a["rank"] == b["rank"],
        "deficit_identical": a["deficit"] == b["deficit"],
        "partitions_differ": a["chunk_force"] != b["chunk_force"],
        "units_differ": a["units"] != b["units"],
        "gate_pass": same and a["chunk_force"] != b["chunk_force"],
    }
    if not report["cross_partition"]["gate_pass"]:
        failures.append("cross-partition gate FAILED")

report["verdict"] = "PASS" if not failures else "FAIL"
report["failures"] = failures
(RUN_DIR / "raw.json").write_text(json.dumps(report, indent=1) + "\n")
print(json.dumps({"verdict": report["verdict"], "failures": failures,
                  "rank_A": report["partitions"].get("A", {}).get("rank"),
                  "rank_B": report["partitions"].get("B", {}).get("rank")}))
sys.exit(0 if not failures else 1)
