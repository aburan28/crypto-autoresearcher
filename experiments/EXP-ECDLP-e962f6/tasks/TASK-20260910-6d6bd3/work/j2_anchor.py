#!/usr/bin/env python3
"""Validator J2 + blind re-derivation, from RUN-002 raw-result.json ONLY
(for the re-derivation: only the basin_histogram_8W block is used, per the
frozen plan's blind_rederivation statement).

Checks:
  A. params/seeds/W/theta/cap as frozen (W = sqrt(a N / T) = 256, not 2048)
  B. partition identity recomputed from the histogram:
     sum(size*count) + capped_mass_8W + cycle_mass == N, digit-for-digit
  C. BLIND RE-DERIVATION of top_T_share: sum of the T=256 largest capped
     basin sizes / N, from the histogram block only.
  D. n_pairs consistency: N - cycle_mass (population = points reaching a DP)
"""
import json

P = "/Volumes/SSD990/llm/tmp/opencode/review-e962f6-20260910/experiments/EXP-ECDLP-e962f6/runs/RUN-ECDLP-e962f6-002/raw-result.json"
d = json.load(open(P))

print("=== A. params / keys ===")
p = d["params"]
k = d["keys"]
print(json.dumps(p, indent=1))
print(json.dumps(k, indent=1))
N, T, a, W = p["N"], p["T"], p["a"], p["W"]
import math
W_def = math.sqrt(a * N / T)
print(f"W from definition sqrt(a*N/T) = {W_def!r}; recorded W = {W!r}; match: {W_def == W}")
print(f"theta recorded = {p['theta']!r}; 1/W = {1.0/W!r}; match: {p['theta'] == 1.0/W}")
print(f"cap8 recorded = {p['cap8']!r}; 8W = {8*int(W)!r}; match: {p['cap8'] == 8*int(W)}")
print(f"seeds: walk_key={k['walk_key_seed']} (frozen 1), dp_key={k['dp_key_seed']} (frozen 101), tie_break={k['tie_break_seed']} (frozen 401)")
print(f"seeds match frozen: {k['walk_key_seed']==1 and k['dp_key_seed']==101 and k['tie_break_seed']==401}")

print()
print("=== B. partition identity from histogram ===")
h = d["basin_histogram_8W"]
sizes = h["sizes"]
counts = h["counts"]
print(f"histogram: {len(sizes)} size classes, sizes {sizes[0]}..{sizes[-1]}")
print(f"dense 1..max: {sizes == list(range(1, len(sizes) + 1))}")
print(f"max size class = {max(sizes)}; cap 8W = {p['cap8']}")
sum_capped = sum(s * c for s, c in zip(sizes, counts))
n_basins = sum(counts)
cycle = d["cycle_mass"]
capped = d["capped_mass_8W"]
total = sum_capped + capped + cycle
print(f"sum of capped basin sizes (from histogram) = {sum_capped}")
print(f"n basins (DPs with nonempty basin) = {n_basins}; nDP recorded = {d['nDP']}")
print(f"capped_mass_8W = {capped}; cycle_mass = {cycle}")
print(f"sum + capped + cycle = {total}; N = {N}; digit-for-digit: {total == N}")
print(f"committed partition_identity block: {d['partition_identity']}")

print()
print("=== C. BLIND RE-DERIVATION of top_T_share (histogram block only) ===")
# spec definition: top_T_share = sum of the T largest exact basin sizes
# divided by N (cap 8W).  T = 256, N = 2^26 per the spec's anchor_enumeration.
T_spec, N_spec = 256, 2**26
cnt = dict(zip(sizes, counts))
remaining = T_spec
top_sum = 0
for s in sorted(cnt, reverse=True):
    take = min(cnt[s], remaining)
    top_sum += take * s
    remaining -= take
    if remaining == 0:
        break
share = top_sum / N_spec
print(f"sum of {T_spec} largest capped basin sizes = {top_sum}")
print(f"re-derived top_T_share = {top_sum} / {N_spec} = {share!r}")
committed = d["top_T_share_8W"]
print(f"committed top_T_share_8W = {committed!r}")
print(f"match: {share == committed}; abs diff = {abs(share - committed):.3e}")

print()
print("=== D. Spearman population consistency ===")
sp = d["spearman_walk_length_vs_basin_size"]
print(json.dumps(sp, indent=1))
print(f"N - cycle_mass = {N - cycle}; n_pairs recorded = {sp['n_pairs']}; match: {N - cycle == sp['n_pairs']}")

out = {
    "A_params": p, "A_keys": k,
    "W_definition_match": W_def == W,
    "B_sum_capped": sum_capped, "B_total": total, "B_N": N,
    "B_digit_for_digit": total == N,
    "C_top_sum": top_sum, "C_share": share, "C_committed": committed,
    "C_match": share == committed,
    "D_n_pairs_match": N - cycle == sp["n_pairs"],
}
with open("/Volumes/SSD990/llm/tmp/opencode/review-e962f6-20260910/experiments/EXP-ECDLP-e962f6/tasks/TASK-20260910-6d6bd3/work/j2_anchor_checks.json", "w") as fh:
    json.dump(out, fh, indent=1)
print("\nwritten: work/j2_anchor_checks.json")
