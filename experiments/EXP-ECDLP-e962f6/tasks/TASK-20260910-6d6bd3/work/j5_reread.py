#!/usr/bin/env python3
"""Validator J5: Stage 2 re-read (RUN-008) independent verification.

1. Re-verify the sha256 of every committed file RUN-008 read, against
   `git show HEAD:<path>` (the committed state) AND against the working tree.
   (16 committed files + 1 new artifact from this experiment, whose
   sha256_committed is null by record.)
2. Re-read the committed summary.json fields myself and recompute:
   - corrected residual R(N) = (top_T_share + cycle_mass_frac +
     capped_mass_8W_frac - C_max(a)) / C_max(a)  per (N, seed)
   - per-N median |R|
   - D1 (|R(2^26)| <= 0.15), D2 (per-N median |R| non-increasing up to 2pp),
     D3 (log-log slope of per-N median |R| over |R|>0.01 points in [-0.7,-0.1])
   - D3 slope BOTH ways: endpoint (2^20->2^24) and least-squares over the
     |R|>0.01 points
   - substitution clause (fewer than 3 points above the 0.01 floor?)
"""
import hashlib
import json
import math
import re
import statistics
import subprocess

ROOT = "/Volumes/SSD990/llm/tmp/opencode/review-e962f6-20260910"
R8 = f"{ROOT}/experiments/EXP-ECDLP-e962f6/runs/RUN-ECDLP-e962f6-008/raw-result.json"
d = json.load(open(R8))

print("=== 1. sha256 re-verification of the files RUN-008 read ===")
files = d["files_read"]
print(f"files_read: {len(files)} (16 committed + 1 new artifact)")
all_ok = True
for path, rec in sorted(files.items()):
    g = subprocess.run(["git", "show", f"HEAD:{path}"], capture_output=True, cwd=ROOT)
    if g.returncode != 0:
        print(f"  NOT IN HEAD: {path}")
        all_ok = False
        continue
    git_hash = hashlib.sha256(g.stdout).hexdigest()
    wt_hash = hashlib.sha256(open(f"{ROOT}/{path}", "rb").read()).hexdigest()
    committed = rec.get("sha256_committed")
    at_read = rec["sha256_at_read"]
    if committed is None:
        # new artifact of this experiment: verify at_read == HEAD == worktree
        ok = (git_hash == at_read == wt_hash)
        tag = "NEW-ARTIFACT"
    else:
        ok = (git_hash == committed == at_read == wt_hash)
        tag = "committed"
    all_ok &= ok
    if not ok:
        print(f"  MISMATCH [{tag}] {path}\n    at_read   {at_read}\n"
              f"    committed {committed}\n    git HEAD  {git_hash}\n    worktree  {wt_hash}")
print(f"all files: git-HEAD == recorded == working-tree: {all_ok}")
print(f"recorded read_only_guarantee: {json.dumps(d.get('read_only_guarantee'))}")

print()
print("=== 2. recompute corrected residuals from the committed fields ===")
cells = []
for path, rec in sorted(files.items()):
    if "EXP-ECDLP-869870" not in path:
        continue
    s = json.load(open(f"{ROOT}/{path}"))
    m = re.search(r"-N(\d+)-s(\d+)", path)
    N, seed = 2 ** int(m.group(1)), int(m.group(2))
    cell = s["cells"]["a=0.25"]
    top = cell["global_oracle"]["top_T_share_8W"]
    cmax = cell["global_oracle"]["model"]["c_max_numeric"]
    cyc = cell["cycle_mass_frac"]
    cap = cell["capped_mass_8W_frac"]
    R = (top + cyc + cap - cmax) / cmax
    cells.append((N, seed, top, cmax, cyc, cap, R))

# the 2^26 anchor from RUN-002 (committed)
r2 = json.load(open(f"{ROOT}/experiments/EXP-ECDLP-e962f6/runs/RUN-ECDLP-e962f6-002/raw-result.json"))
top26 = r2["top_T_share_8W"]
cyc26 = r2["cycle_mass_frac"]
cap26 = r2["capped_mass_8W_frac"]
cmax26 = 0.3889120129663709  # C_max(1/4) anchor (spec anchor_values; independently verified in J1)
R26 = (top26 + cyc26 + cap26 - cmax26) / cmax26
cells.append((2**26, 1, top26, cmax26, cyc26, cap26, R26))

print(f"{'N':>10} {'seed':>4} {'top_T':>12} {'C_max':>12} {'cyc':>10} {'cap':>10} {'R':>12} {'|R|':>10}")
for N, seed, top, cmax, cyc, cap, R in cells:
    print(f"{N:>10} {seed:>4} {top:>12.8f} {cmax:>12.8f} {cyc:>10.6f} {cap:>10.6f} {R:>12.6f} {abs(R):>10.6f}")

byN = {}
for N, seed, top, cmax, cyc, cap, R in cells:
    byN.setdefault(N, []).append(abs(R))
medians = {N: statistics.median(v) for N, v in sorted(byN.items())}
print()
print("per-N median |R|:")
for N in sorted(medians):
    print(f"  N={N:>10} ({len(byN[N])} seeds): median |R| = {medians[N]!r}   per-seed: {[round(x,6) for x in sorted(byN[N])]}")

print()
print("=== 3. decay checks ===")
d1 = abs(R26) <= 0.15
print(f"D1: |R(2^26)| = {abs(R26)!r} <= 0.15: {d1}")
Ns = sorted(medians)
d2 = True
for prev, nxt in zip(Ns, Ns[1:]):
    ok = medians[nxt] <= medians[prev] + 0.02
    d2 &= ok
    print(f"D2 step {prev}->{nxt}: {medians[prev]!r} -> {medians[nxt]!r} (delta {medians[nxt]-medians[prev]:+.6f}, floor 0.02): {ok}")
print(f"D2: {d2}")
pts = [(N, medians[N]) for N in Ns if medians[N] > 0.01]
print(f"points with |R| > 0.01: {[(N, m) for N, m in pts]}")
print(f"n points above floor: {len(pts)} (substitution clause triggers if < 3: {len(pts) < 3})")
xs = [math.log2(N) for N, _ in pts]
ys = [math.log(m) for _, m in pts]
slope_end = (ys[-1] - ys[0]) / (xs[-1] - xs[0])
n = len(xs)
xbar, ybar = sum(xs) / n, sum(ys) / n
slope_ls = sum((x - xbar) * (y - ybar) for x, y in zip(xs, ys)) / sum((x - xbar) ** 2 for x in xs)
print(f"D3 endpoint slope (2^20 -> 2^24): {slope_end!r}")
print(f"D3 least-squares slope over {n} points: {slope_ls!r}")
in_band_end = -0.7 <= slope_end <= -0.1
in_band_ls = -0.7 <= slope_ls <= -0.1
print(f"endpoint in [-0.7,-0.1]: {in_band_end}; least-squares in [-0.7,-0.1]: {in_band_ls}")
print(f"D3 verdict (outside band => does not pass): endpoint {not in_band_end}, ls {not in_band_ls}")

print()
print("=== 4. RUN-008 committed values for comparison ===")
print("residual_table:")
for row in d.get("residual_table", []):
    print("  ", json.dumps(row))
print("per_N_median_abs_R:", json.dumps(d.get("per_N_median_abs_R")))
print("decay_checks:", json.dumps(d.get("decay_checks"), indent=1))
print("anchor_crosscheck_612fb1_002:", json.dumps(d.get("anchor_crosscheck_612fb1_002")))
print("largest_abs_R_cell:", json.dumps(d.get("largest_abs_R_cell")))

out = {
    "sha256_all_ok": all_ok,
    "cells": [{"N": N, "seed": s, "R": R, "absR": abs(R)} for N, s, t, c, cy, cp, R in cells],
    "medians": {str(N): m for N, m in medians.items()},
    "D1": d1, "D2": d2,
    "D3_endpoint": slope_end, "D3_ls": slope_ls,
    "D3_points": pts,
}
with open(f"{ROOT}/experiments/EXP-ECDLP-e962f6/tasks/TASK-20260910-6d6bd3/work/j5_reread_checks.json", "w") as fh:
    json.dump(out, fh, indent=1)
print("\nwritten: work/j5_reread_checks.json")
