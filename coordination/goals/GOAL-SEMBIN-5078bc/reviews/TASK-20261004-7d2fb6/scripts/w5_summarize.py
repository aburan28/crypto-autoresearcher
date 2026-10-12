#!/usr/bin/env python3
"""w5_summarize.py -- summarise w5_campaign.py output (JSON lines) by variant: how many (instance, cap) runs completed, and in how many
the rank / standard count / leading-monomial set / verdict / saturation check left the reference. Usage: w5_summarize.py file.jsonl ..."""
import sys, json, collections
rows = [json.loads(l) for f in sys.argv[1:] for l in open(f) if l.strip()]
for r in rows:
    if r.get("rc") == 0: r["early_stop_partial_rank"] = bool(r["contains_one"] and r["rank"] < r["ncols"])
by = collections.defaultdict(list)
for r in rows: by[r["variant"] if "variant" in r else "?"].append(r)
print(f"{'variant':9s} {'runs':>5s} {'done':>5s} {'rank!=':>7s} {'std!=':>6s} {'LM!=':>5s} {'verdict!=':>10s} {'satviol>0':>10s} {'sat_checked':>11s} {'early-stop':>10s}")
for v, rs in by.items():
    done = [r for r in rs if r.get("rc") == 0]
    nr = sum(1 for r in done if not r["rank_equal"] and not r.get("early_stop_partial_rank"))
    ns = sum(1 for r in done if not r["std_equal"]); nl = sum(1 for r in done if not r["lm_equal_as_set"] and not r.get("early_stop_partial_rank"))
    nv = sum(1 for r in done if not r["verdict_equal"])
    sat = [r for r in done if "saturation_violations" in r and not r.get("early_stop_partial_rank")]
    nsv = sum(1 for r in sat if r["saturation_violations"] > 0)
    es = sum(1 for r in done if r.get("early_stop_partial_rank"))
    print(f"{v:9s} {len(rs):5d} {len(done):5d} {nr:7d} {ns:6d} {nl:5d} {nv:10d} {nsv:10d} {len(sat):11d} {es:10d}")
# unmutated: any disagreement at all?
bad = [r for r in by.get("orig", []) if r.get("rc") == 0 and not (r["std_equal"] and r["verdict_equal"] and (r["rank_equal"] or r.get("early_stop_partial_rank")) and (r["lm_equal_as_set"] or r.get("early_stop_partial_rank")) and not (r.get("saturation_violations") and not r.get("early_stop_partial_rank")) and not r.get("gens_not_in_span"))]
print("unmutated runs disagreeing with the reference (excluding the early-stop partial-rank runs, whose partial basis is not saturated by construction):", len(bad))
es = [r for r in by.get("orig", []) if r.get("early_stop_partial_rank")]
print("unmutated early-stop (1 entered W) runs:", [(r["instance"], r["cap_gib"], r["rank"], r["ncols"]) for r in es])
