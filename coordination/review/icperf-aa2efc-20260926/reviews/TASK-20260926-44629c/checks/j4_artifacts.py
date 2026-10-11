#!/usr/bin/env python3
"""J4: hashes and numbers read from the seven bound artifacts (validator TASK-20260926-44629c).
Repository: /home/user/crypto at HEAD f9c77524 (shallow clone; recorded commit 50ea716 not reachable, hashes are binding).
"""
import hashlib, json, os, subprocess
ROOT = "/home/user/crypto"
head = subprocess.run(["git", "-C", ROOT, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
dirty = subprocess.run(["git", "-C", ROOT, "status", "--porcelain"], capture_output=True, text=True).stdout.strip()
print(f"external repo HEAD = {head}; working tree clean = {dirty == ''}")
BOUND = {
 "research/nagao_relations/solver_10/summary.json": "fc28f1ebd770f69da840c2ffc0cb68cab9372d6953227c035641fe44e9ac3ada",
 "research/nagao_relations/solver_12/summary.json": "7ebd8b2531cbc2bee976f063ef4019428f2a8bcf67d5ad4a3453a95703dd2a2f",
 "research/nagao_relations/solver_12/CORRECTION.md": "7c6319a60843d924c3832f13c189b873c9d6639a544f143c2de6a59032721c30",
 "research/nagao_relations/solver_13/summary.json": "48af9b0a98d3f0cc394416a0fd554d2a5e1da5a391491d8d9313d6284c244fbb",
 "research/nagao_relations/solver_15/summary.json": "61aa98dbad9fbf1aeb048dcb47a2cda21fcc8e160502c327125f765ab9db42d0",
 "research/nagao_relations/solver_13/contract.json": "289b9253ee7b4c4b079cec0d051e3fd4209e474a1df32a1affb77492a9b48a83",
 "research/nagao_relations/solver_15/contract.json": "9f8e543b6a2f9226829be97bf06f135fb40b7249f744542f272549e0763bccee",
}
UNBOUND = ["research/nagao_relations/solver_11/summary.json", "research/nagao_relations/solver_11/contract.json",
           "research/nagao_relations/solver_10/raw.jsonl", "research/nagao_relations/solver_10/contract.json"]
def sha(p):
    return hashlib.sha256(open(os.path.join(ROOT, p), "rb").read()).hexdigest()
print("\n== (0) sha256 recomputation ==")
allok = True
for p, h in BOUND.items():
    got = sha(p); ok = got == h; allok &= ok
    print(f"  {'MATCH' if ok else 'MISMATCH'}  {p}  {got}")
print(f"  all seven match: {allok}")
for p in UNBOUND:
    print(f"  UNBOUND (not in EV-ICPERF-10c5fc list; my hash for the record)  {p}  {sha(p)}")

J = lambda p: json.load(open(os.path.join(ROOT, p)))
s10 = J("research/nagao_relations/solver_10/summary.json")
s12 = J("research/nagao_relations/solver_12/summary.json")
s13 = J("research/nagao_relations/solver_13/summary.json")
s15 = J("research/nagao_relations/solver_15/summary.json")
s11 = J("research/nagao_relations/solver_11/summary.json")
c10 = J("research/nagao_relations/solver_10/contract.json")

print("\n== (a) solver_10: 32/32 vs 0/32 at d = 6; 128 trials; 0 errors; 28 verified relations ==")
g = s10["groups"]
trials = sum(x["attempted"] for x in g); rels = sum(x["verified_relations"] for x in g)
print(f"  groups={len(g)} attempted total={trials} errors={len(s10['errors'])} verified_relations total={rels}")
RR = ("quadratic-optimized", "quadratic-image"); SAT = ("s4-symmetric", "chained-s3")
for d in (6, 7):
    for fam, name in ((RR, "RR (quadratic-optimized+quadratic-image)"), (SAT, "Semaev-via-SAT (s4-symmetric+chained-s3)")):
        rows = [x for x in g if x["d"] == d and x["variant"] in fam]
        att = sum(x["attempted"] for x in rows); res = sum(x["resolved"] for x in rows); rwb = sum(x["resolved_within_budget"] for x in rows)
        secs = [round(x["all_phase_seconds"]) for x in rows]
        print(f"  d={d} {name}: attempted {att}, resolved {res}, resolved_within_budget {rwb}; all_phase_seconds per 4-target group {secs}")
print(f"  contract seconds_per_instance = {c10['seconds_per_instance']} -> 4 targets x 120 s = 480 s; SAT groups at d=6 sit at ~480-1018 s, i.e. budget exhaustion")
# status field of raw.jsonl trials at d=6 for the SAT variants
raw = [json.loads(l) for l in open(os.path.join(ROOT, "research/nagao_relations/solver_10/raw.jsonl")) if l.strip()]
tr = [x for x in raw if x.get("kind") == "trial"]
from collections import Counter
for d in (6, 7):
    for v in ("quadratic-optimized", "quadratic-image", "s4-symmetric", "chained-s3"):
        c = Counter(x.get("status") for x in tr if x.get("d") == d and x.get("variant") == v)
        print(f"  raw.jsonl status counts d={d} {v}: {dict(c)}")

print("\n== (b) solver_12: null-object ratio 0.494x at d = 6; d = 7 withdrawn ==")
for x in s12["groups"]:
    print(f"  d={x['d']} {x['stratum']}: pair_over_image={x['pair_over_image']} invalid={x.get('pair_over_image_invalid')} pairs={x['pairs_enumerated']} pair_ops={x['pair_oracle_ops']} image_ops={x['quadratic_image_ops']}")
print(f"  cross_oracle_disagreements={s12['cross_oracle_disagreements']}; corrections={s12['corrections']}")
d6 = [x for x in s12["groups"] if x["d"] == 6]
tot = sum(x["pair_oracle_ops"] for x in d6) / sum(x["quadratic_image_ops"] for x in d6)
print(f"  pooled d=6 ratio over 8 instances = {tot:.4f}; inverse = {1/tot:.3f}x (finding title says RR costs 2.02x the null)")

print("\n== (c) solver_13: candidates/(|F|^2/2) = 3.00, 3.12, 2.33, 1.92, 1.99; op ratio 2.83 -> 1.55 ==")
for p in s13["points"]:
    print(f"  d={p['d']} |F|={p['factor_base_points']} cand/(F^2/2)={p['ratio_rr_candidates_over_half_f_squared']:.4f} rr_ops/pair_ops={p['ratio_rr_ops_over_pair_ops']:.4f}  (recomputed: {p['mean_rr_candidates']/(p['factor_base_points']**2/2):.4f}, {p['mean_rr_ops']/p['mean_pair_ops']:.4f})")
print(f"  verdict block: {s13['verdict']}; all_sets_equal={s13['all_sets_equal']}")

print("\n== (d) solver_15: span dimensions 71, 97, 123 at d = 4, 5, 6; 131 from d = 7; d = 45 ==")
for row in s15["span"]:
    dims = sorted(set(u["dimension"] for u in row["uniform"]))
    print(f"  d={row['d']} samples={row['samples']} uniform span dims={dims} saturated={row['saturated']} certificate_on_all_uniform={row['certificate_on_all_uniform']} planted dims={[p['dimension'] for p in row['planted']]} planted cert={[p['certificate'] for p in row['planted']]}")
print(f"  verdict: alive at {s15['verdict']['certificate_alive_at_d']}, largest d with certificate {s15['verdict']['largest_d_with_certificate']}, existence threshold d {s15['verdict']['existence_threshold_d']}, soundness gate {s15['verdict']['soundness_gate_passed']}")

print("\n== (e) solver_11 (UNBOUND): amortisation shares 0.12% at d = 6, 0.07% at d = 7 ==")
for x in s11["splits"]:
    print(f"  d={x['d']} target_independent_ops={x['target_independent_ops']} per_target_ops={x['per_target_ops']} share={x['amortisable_share']:.6f} = {100*x['amortisable_share']:.2f}%  (recomputed {100*x['target_independent_ops']/x['total_ops']:.4f}%)")

print("\n== (g) vanishing-ideal base-case numbers (6967, 140400, 8647) in any artifact? ==")
hits = []
for dp, dn, fn in os.walk(os.path.join(ROOT, "research/nagao_relations")):
    for f in fn:
        if f.endswith((".md", ".json", ".py")) and f != "raw.jsonl":
            t = open(os.path.join(dp, f), errors="ignore").read()
            for tok in ("6967", "140400", "8647"):
                if tok in t:
                    hits.append((os.path.relpath(os.path.join(dp, f), ROOT), tok))
for dp, dn, fn in os.walk(os.path.join(ROOT, "research/notes")):
    for f in fn:
        t = open(os.path.join(dp, f), errors="ignore").read()
        for tok in ("6967", "140400", "8647"):
            if tok in t:
                hits.append((os.path.relpath(os.path.join(dp, f), ROOT), tok))
print(f"  hits in notes / non-raw nagao_relations files: {hits if hits else 'NONE'}")
from math import comb
print(f"  1 + 131 + C(131,2) = {1 + 131 + comb(131, 2)}  (number of Boolean monomials of degree <= 2 in 131 variables: the full rank 8647 means I_2 = 0)")
print(f"  8647 - 1680 = {8647 - 1680}  (matches the quoted d = 5 kernel dimension 6967 if the d = 5 value set has 1680 distinct points of full rank)")
