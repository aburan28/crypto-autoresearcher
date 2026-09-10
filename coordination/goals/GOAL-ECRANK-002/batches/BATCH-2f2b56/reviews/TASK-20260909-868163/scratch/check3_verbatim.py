#!/usr/bin/env python3
"""J2 check 3: verify the n2r verbatim_predicates recorded in the R12 raw
result match the ACTUAL lines of the frozen source (source/construct.py for
rat_height + convention A filter/count lines; source-v2/n2r.py for the
convention B h_B_from_instance lines). Re-runs the documented extraction
logic independently and compares line-by-line.
"""
import json

ROOT = "/Volumes/SSD990/llm/tmp/opencode/review-e3cf55-20260909"
RAW = f"{ROOT}/experiments/EXP-ECRANK-73275e/runs/RUN-ECRANK-73275e-R12-construct-n6-replication/raw-result.json"
CONSTRUCT = f"{ROOT}/experiments/EXP-ECRANK-73275e/source/construct.py"
N2R = f"{ROOT}/experiments/EXP-ECRANK-73275e/source-v2/n2r.py"

d = json.load(open(RAW))
vp = d["n2r"]["verbatim_predicates"]

def lines(p):
    with open(p) as f:
        return f.read().splitlines()

cl = lines(CONSTRUCT)
nl = lines(N2R)

# 1. rat_height definition: line starting 'def rat_height(' + next line
rat = None
for i, ln in enumerate(cl):
    if ln.startswith("def rat_height("):
        rat = [cl[i], cl[i + 1]]
        rat_idx = i
        break
print("== rat_height_definition (source/construct.py) ==")
print("actual  :", rat, f"(line {rat_idx+1})")
print("recorded:", vp["rat_height_definition"]["lines"])
print("MATCH" if rat == vp["rat_height_definition"]["lines"] else "MISMATCH")

# 2. convention A filter: line containing the h = max(...) + next 3
filt = None
for i, ln in enumerate(cl):
    if "h = max(rat_height(ri) for ri in r)" in ln:
        filt = [cl[i], cl[i + 1], cl[i + 2], cl[i + 3]]
        filt_idx = i
        break
print("\n== convention_A filter_lines (source/construct.py solve_n6) ==")
print("actual  :", filt, f"(line {filt_idx+1})")
print("recorded:", vp["convention_A_recorded_r_height"]["filter_lines"])
print("MATCH" if filt == vp["convention_A_recorded_r_height"]["filter_lines"] else "MISMATCH")

# 3. convention A count: line containing 'counts[int(H)] += 1', 2 before + it
cnt = None
for i, ln in enumerate(cl):
    if "counts[int(H)] += 1" in ln:
        cnt = [cl[i - 2], cl[i - 1], cl[i]]
        cnt_idx = i
        break
print("\n== convention_A count_lines (source/construct.py construct_arm) ==")
print("actual  :", cnt, f"(line {cnt_idx+1})")
print("recorded:", vp["convention_A_recorded_r_height"]["count_lines"])
print("MATCH" if cnt == vp["convention_A_recorded_r_height"]["count_lines"] else "MISMATCH")

# 4. convention B: 'def h_B_from_instance(' + next 9 (10 total) in n2r.py
convb = None
for i, ln in enumerate(nl):
    if ln.lstrip().startswith("def h_B_from_instance("):
        convb = nl[i:i + 10]
        convb_idx = i
        break
print("\n== convention_B lines (source-v2/n2r.py h_B_from_instance) ==")
print("actual  :", convb, f"(line {convb_idx+1})")
print("recorded:", vp["convention_B_solved_free_coordinate_height"]["lines"])
print("MATCH" if convb == vp["convention_B_solved_free_coordinate_height"]["lines"] else "MISMATCH")

# 5. uniqueness: exactly one occurrence of each anchor (no ambiguity)
print("\n== anchor uniqueness in source/construct.py ==")
print("rat_height def count:", sum(1 for ln in cl if ln.startswith("def rat_height(")))
print("conv A filter anchor count:", sum(1 for ln in cl if "h = max(rat_height(ri) for ri in r)" in ln))
print("conv A count anchor count:", sum(1 for ln in cl if "counts[int(H)] += 1" in ln))
print("h_B_from_instance def count in n2r.py:",
      sum(1 for ln in nl if ln.lstrip().startswith("def h_B_from_instance(")))
