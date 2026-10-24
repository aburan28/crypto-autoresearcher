"""R2: per-section successes at p > 500 (both seeds) against the null and two leak models."""
import json, math
rows = []
for path in ("../../runs/RUN-CZLIFT-041d05/raw-result.json", "../../runs/RUN-CZLIFT-6709c9/raw-result.json"):
    raw = json.load(open(path))
    rows += [dict(r, p=c["p"]) for c in raw["raw"]["curves"] for r in c["rows"] if r["vP"] >= 2]
out = {}
for sec in ("hensel_random", "naive", "teichmuller"):
    rr = [r for r in rows if r["section"] == sec and r["p"] > 500]
    out[sec] = {"rows_both_seeds_p>500": len(rr), "successes": sum(r["success"] for r in rr),
                "expected_null": round(sum(1 / (r["p"] + 1) for r in rr), 2),
                "expected_if_1/sqrt(p)": round(sum(1 / math.sqrt(r["p"]) for r in rr), 1),
                "expected_if_10/p": round(sum(10 / r["p"] for r in rr), 1)}
print(json.dumps(out, indent=1))
json.dump(out, open("rt_r2_section_largep_output.json", "w"), indent=1)
