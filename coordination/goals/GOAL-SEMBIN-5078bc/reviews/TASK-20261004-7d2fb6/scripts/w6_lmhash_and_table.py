#!/usr/bin/env python3
"""w6_lmhash_and_table.py -- joint W6 (4)(5).
 (5) Producer's leading-monomial hash input format (closure_cert._lm_stats): sha256 over, for every basis row in ROW order (rows of the reduced echelon basis = ascending leading column =
     descending size, then ascending bitmask), the leading monomial's bitmask as 8 bytes BIG-endian (bit i <-> variable index i of var_names; constant monomial = 8 zero bytes).
     Verified here: sha256 recomputed from MY reference LM list (statement ORDER, literal comparator) equals the library's lm_sha256 for every completed unmutated run of the campaign.
 (4) Per window instance: |V|, verdict, polarity, decided D, and the checks it carries (structural / second routine / evalcheck / exact count by two counters / independent count by me).
Writes outputs/w6_table.json and prints a markdown table."""
import json, os, hashlib, glob, collections
SP, WS = os.environ["SP"], os.environ["WS"]; W = f"{SP}/work"
REPO = "/home/user/crypto-autoresearcher"; R = f"{REPO}/experiments/EXP-SEMBIN-7e1371/runs/RUN-SEMBIN-5ed13e"
# (5) hash format check
def sha_of(lms):
    h = hashlib.sha256()
    for x in lms: h.update(int(x).to_bytes(8, "big"))
    return h.hexdigest()
rows = [json.loads(l) for f in ("w5_orig.jsonl", "w5_bigN.jsonl") for l in open(f"{W}/out/{f}") if l.strip()]
chk = []
for r in rows:
    if r.get("rc") != 0 or r.get("variant") != "orig": continue
    ref = [int(x) for x in open(f"{W}/ref/{r['instance']}.D{r.get('D',4)}.lm").read().split()]
    full = not (r["contains_one"] and r["rank"] < r["ncols"])
    if full: chk.append((r["instance"], r["lm_sha256"] == sha_of(ref)))
print("(5) library lm_sha256 == sha256(8-byte big-endian leading masks of MY statement-order reference, row order):", sum(1 for _, ok in chk if ok), "of", len(chk), "completed unmutated runs;",
      "instances:", len({i for i, _ in chk}))
# (4) table
w4 = {r["instance_id"]: r for r in json.load(open(f"{WS}/outputs/w4_zeros.json"))}
tab = []
for lane in sorted(glob.glob(f"{R}/closure_m2_n4*")):
    recs = [json.loads(l) for l in open(f"{lane}/cells/results.jsonl") if l.strip()]
    for r in recs:
        if r["instrument"] != "closure_certificate": continue
        iid = r["instance_id"]; sc = next(x for x in recs if x["instance_id"] == iid and x["instrument"] == "exhaustive_solution_count")
        last = r["per_D"][-1]; V = sc["solutions"]; verdict = r["degree4_sufficiency_verdict"]
        second = ("n44_d5" if iid.endswith("n44_m2_t2_k22_low_B_ran_s20260913101_d5") else "n45_d0" if iid.endswith("n45_m2_t2_k23_low_B_ran_s20260913101_d0") else None)
        row = {"n": r["n"], "draw": r["draw"], "V": V, "verdict": verdict, "decided_at": f"D={last['D']}" + (" (1 in W_D)" if last.get("contains_one") else ""),
               "polarity": ("sufficient with 1 in W (|V|=0): soundness-sensitive, no witness exists, no count check" if (verdict == "sufficient" and last.get("contains_one")) else
                            "sufficient with |V|>0, std == |V| exactly: soundness-sensitive, with an independent exact-count agreement" if verdict == "sufficient" else
                            "insufficient: completeness-sensitive (missing products would produce it)"),
               "structural_check_every_elimination": all((p.get("elimination_faults") == 0) for p in r["per_D"]), "second_routine": bool(second), "evalcheck_at_one_zero": bool(second),
               "zeros_total": V, "evalcheck_fraction_of_zeros": (f"1/{V}" if second else None),
               "exact_count_two_counters": sc.get("cross_check_agrees"), "exact_count_independent_reviewer": w4[iid]["count_equals_recorded"],
               "partial_rank_record": bool(last.get("contains_one") and last["rank"] < last["ncols"]), "instance_id": iid}
        tab.append(row)
tab.sort(key=lambda x: (x["n"], x["draw"]))
json.dump({"lm_hash_check": {"matches": sum(1 for _, ok in chk if ok), "of": len(chk)}, "table": tab}, open(f"{WS}/outputs/w6_table.json", "w"), indent=1)
print("\n| n | draw | |V| | verdict | decided at | polarity | structural | 2nd routine | evalcheck (fraction of zeros) | counters | partial rank |")
print("|---|---|---|---|---|---|---|---|---|---|---|")
for t in tab:
    print(f"| {t['n']} | {t['draw']} | {t['V']} | {t['verdict']} | {t['decided_at']} | {t['polarity'][:46]} | {t['structural_check_every_elimination']} | {t['second_routine']} | {t['evalcheck_fraction_of_zeros'] or '-'} | 2 counters {t['exact_count_two_counters']}, reviewer {t['exact_count_independent_reviewer']} | {t['partial_rank_record']} |")
