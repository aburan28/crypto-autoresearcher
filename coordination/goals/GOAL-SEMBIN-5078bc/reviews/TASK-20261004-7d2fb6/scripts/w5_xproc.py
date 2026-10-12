#!/usr/bin/env python3
"""w5_xproc.py -- joint W5 (3)(4): the PRODUCER'S OWN cross-check procedure (record run = default routine at cap A; check run =
-DECH_EVALCHECK build, routine mzd_echelonize, cap B, evaluation check at a verified zero) applied to unmutated and mutated builds, next
to my independent reference and saturation verifier. A mutant is applied to BOTH builds, as a code defect would be.
Usage: w5_xproc.py OUT.jsonl STEM VARIANT CAP_A CAP_B     VARIANT in orig, STRESS32, MA, MB_s32, ...
Output line: record/check outcomes, whether the producer procedure flags, whether the reference / verifier flag. Scratch."""
import sys, os, json, subprocess
SP, WS = os.environ["SP"], os.environ["WS"]; W = f"{SP}/work"
sys.path.insert(0, f"{WS}/scripts")
from w5_singledrop import run_child
import gen_small, numpy as np
out, stem, variant, capA, capB = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4]), float(sys.argv[5])
s = json.load(open(f"{W}/inst/{stem}.json")); N, V = s["N"], s["V"]
if variant == "orig": plain, ev = f"{W}/build/libclosure_orig.so", f"{W}/build/libclosure_orig_evalcheck.so"
else: plain, ev = f"{W}/mut/libclosure_{variant}.so", f"{W}/mut/libclosure_{variant}_ev.so"
ok = gen_small.zeros_count(N, s["equations"])[1]; zeros = np.nonzero(ok)[0]
assert len(zeros), "needs a zero for the evaluation check"
witness = int(zeros[0])
st = dict(kv.split("=") for kv in open(f"{W}/ref/{stem}.D4.stats").read().split())
ref_rank, ref_std = int(st["rank"]), int(st["std"]); ref_lm = [int(x) for x in open(f"{W}/ref/{stem}.D4.lm").read().split()]
rows = f"{W}/rows_xp_{stem}_{variant}.bin" if N <= 22 else "-"
a = run_child("plain", plain, stem, -1, -1, capA, rows)
b = run_child("xcheck", ev, stem, -1, -1, capB, "-", 0, witness)
diffs = [k for k in ("rank", "std", "lm_sha256", "profile") if b.get(k) != a.get(k)]
rec = {"stem": stem, "variant": variant, "cap_record": capA, "cap_check": capB, "N": N, "V": V,
       "record": {k: a.get(k) for k in ("rc", "rank", "std", "contains_one", "lm_sha256", "profile")},
       "check": {k: b.get(k) for k in ("rc", "rank", "std", "lm_sha256", "profile", "evalcheck_bad_calls", "ech_calls")},
       "check_vs_record_disagreements": diffs, "producer_procedure_flags": bool(diffs) or b.get("evalcheck_bad_calls", 0) > 0 or a["rc"] != 0 or b["rc"] != 0}
lm = a.get("lm", [])
rec["record_outcome_equals_reference"] = (a["rc"] == 0 and a["rank"] == ref_rank and a["std"] == ref_std and lm == ref_lm)
if rows != "-" and os.path.exists(rows):
    q = subprocess.run([f"{W}/refclos", "saturate", f"{W}/inst/{stem}.sys", "4", rows], capture_output=True, text=True).stdout.strip()
    kv = dict(x.split("=") for x in q.split()); rec["verifier_violations"] = int(kv["saturation_violations"]); os.remove(rows)
rec["independent_checks_flag"] = (not rec["record_outcome_equals_reference"]) or rec.get("verifier_violations", 0) > 0
open(out, "a").write(json.dumps(rec) + "\n")
print(f"{stem:28s} {variant:9s} capA={capA:<8g} capB={capB:<8g} record rank/std={a.get('rank')}/{a.get('std')} (ref {ref_rank}/{ref_std}) check rank/std={b.get('rank')}/{b.get('std')} "
      f"evalcheck_bad={b.get('evalcheck_bad_calls')} | PRODUCER PROCEDURE FLAGS: {rec['producer_procedure_flags']} | reference/verifier flag: {rec['independent_checks_flag']} (sat={rec.get('verifier_violations')})", flush=True)
