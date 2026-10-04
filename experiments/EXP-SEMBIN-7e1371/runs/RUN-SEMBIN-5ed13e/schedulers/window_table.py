"""Results table for RUN-SEMBIN-5ed13e, read from the lane records
(closure_m2_n*/cells/results.jsonl). Prints Markdown; writes nothing."""
import json, pathlib
RUN = pathlib.Path(__file__).resolve().parent.parent
print("| n | N | draw | |V(I)| (exact) | verdict (D <= 4) | decided at | rank / columns at D | standard monomials | LM SHA-256 (prefix) | D=4 wall s | faults | resumes |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|")
for lane in sorted(RUN.glob("closure_m2_n*/cells/results.jsonl")):
    counts, recs = {}, []
    for line in lane.read_text().splitlines():
        r = json.loads(line)
        if r.get("instrument") == "exhaustive_solution_count":
            counts[r["instance_id"]] = r["solutions"]
        elif "per_D" in r and r.get("instrument") != "macaulay_single_level":
            recs.append(r)
    for r in recs:
        last = r["per_D"][-1]
        d4 = next((p for p in r["per_D"] if p["D"] == 4), None)
        at = f"D={last['D']}" + (" (1 in W_D)" if last.get("contains_one") else "")
        print(f"| {r['n']} | {r['N']} | {r['draw']} | {counts.get(r['instance_id'], '?')} | "
              f"{r['degree4_sufficiency_verdict']} | {at} | {last.get('rank')} / {last.get('ncols')} | "
              f"{last.get('standard_monomials')} | {str(last.get('basis_lm_sha256'))[:8]} | "
              f"{round(d4['wall_s']) if d4 and d4.get('wall_s') else '-'} | "
              f"{sum(p.get('elimination_faults', 0) or 0 for p in r['per_D'])} | "
              f"{sum(p.get('checkpoint_resumes', 0) or 0 for p in r['per_D'])} |")
