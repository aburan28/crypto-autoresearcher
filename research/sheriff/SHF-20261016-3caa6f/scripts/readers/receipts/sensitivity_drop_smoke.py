"""Sensitivity: primary R without the pre-freeze-exercised unit s000 (cold) and rank seed 101 (K1)."""
import base64, json, sys
from pathlib import Path
panel = Path(sys.argv[1])
rows = [json.loads(l) for l in (panel / "runs.jsonl").read_text().splitlines() if l.strip()]
def sm(r):
    t = (panel / r["stdout_file"]).read_text()
    o = json.loads(base64.b64decode([l for l in t.splitlines() if l.startswith("raw_b64=")][0][8:]))
    return [x for x in o["records"] if x.get("kind") == "compact_orbit_dlp_summary"][0]
cold, rank = {}, {}
for r in rows:
    if r["arm"] == "rT" or r["segment"].startswith("O"): continue
    s = sm(r)
    if r["segment"].startswith("C"): cold.setdefault(r["arm"], {})[r["point_id"]] = s["cold_in_process_ms"]
    else: rank.setdefault(r["arm"], {})[r["segment"]] = s["timing_ms"]["rank_stage"]
mean = lambda xs: sum(xs) / len(xs)
pts = [p for p in sorted(cold["cS"]) if p != "s000"]
for blocks in (["K1", "K2"], ["K2"], ["K1"]):
    e = lambda k, c: mean([rank[k][b] for b in blocks]) + mean([cold[c][p] for p in pts])
    print("19 points (no s000), blocks", blocks, "R =", e("kP", "cP") / e("kS", "cS"))
