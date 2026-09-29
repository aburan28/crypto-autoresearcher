#!/usr/bin/env python3
"""J2 check 2: recompute R12 counts_per_H monotonicity (both conventions),
feasibility_fraction, cross-tabulation consistency, and decade ratios
from the raw result, using exact arithmetic (fractions.Fraction).
"""
import json
from fractions import Fraction

ROOT = "/Volumes/SSD990/llm/tmp/opencode/review-e3cf55-20260909"
P = f"{ROOT}/experiments/EXP-ECRANK-73275e/runs/RUN-ECRANK-73275e-R12-construct-n6-replication/raw-result.json"
d = json.load(open(P))

H_levels = d["H_levels"]
counts_per_H = d["counts_per_H"]
rec = d["n2r"]["reconciliation"]
N_A = rec["N_per_H_convention_A"]
N_B = rec["N_per_H_convention_B"]
xtab = rec["cross_tabulation"]
found = d["found"]

print("== basic counts ==")
print("len(found) =", len(found), "| len(xtab) =", len(xtab), "| n_instances =", rec["n_instances"])
print("n_b_declared =", d["n_b_declared"], "| n_b_done =", d["n_b_done"])
print("feasible_tuples =", d["feasible_tuples"], "| recorded feasibility_fraction =", d["feasibility_fraction"])
ff = Fraction(d["feasible_tuples"], d["n_b_declared"])
print("recomputed feasibility_fraction =", ff, "=", float(ff),
      "| MATCH" if float(ff) == d["feasibility_fraction"] else "| MISMATCH")

print("\n== b_index multiset found vs xtab ==")
fb = sorted(f["b_index"] for f in found)
xb = sorted(r["b_index"] for r in xtab)
print("equal multisets:", fb == xb)

print("\n== re-derive N_per_H from xtab rows ==")
def count_le(col):
    out = {}
    for H in H_levels:
        out[str(H)] = sum(1 for r in xtab if r[col] <= H)
    return out
cA = count_le("h_A")
cB = count_le("h_B")
print("convention A (h_A<=H):", cA, "| recorded N_A:", N_A, "| MATCH" if cA == N_A else "| MISMATCH")
print("convention B (h_B<=H):", cB, "| recorded N_B:", N_B, "| MATCH" if cB == N_B else "| MISMATCH")

print("\n== monotonicity (non-decreasing) under both conventions ==")
for name, N in (("A", N_A), ("B", N_B)):
    vals = [N[str(H)] for H in H_levels]
    mono = all(vals[i] <= vals[i+1] for i in range(len(vals)-1))
    print(f"convention {name}: {vals} monotonic_non_decreasing={mono}")
# top-level counts_per_H vs convention A
print("top-level counts_per_H:", counts_per_H, "== N_A:", counts_per_H == N_A)

print("\n== decade ratios (exact rationals) ==")
def ratios(N):
    a, b, c = N["100"], N["1000"], N["10000"]
    return [Fraction(b, a), Fraction(c, b), Fraction(c, a)]
rA = ratios(N_A)
rB = ratios(N_B)
print("A: 1000/100 =", rA[0], "=", float(rA[0]),
      "| 10000/1000 =", rA[1], "=", float(rA[1]),
      "| two-decade 10000/100 =", rA[2], "=", float(rA[2]))
print("B: 1000/100 =", rB[0], "=", float(rB[0]),
      "| 10000/1000 =", rB[1], "=", float(rB[1]),
      "| two-decade 10000/100 =", rB[2], "=", float(rB[2]))

recA = rec["decade_ratios"]["convention_A"]
recB = rec["decade_ratios"]["convention_B"]
print("\nrecorded A ratios:", [x["ratio"] for x in recA["decade_ratios"]],
      "two_decade:", recA["two_decade_total_ratio"])
print("recorded B ratios:", [x["ratio"] for x in recB["decade_ratios"]],
      "two_decade:", recB["two_decade_total_ratio"])
print("A match:", [x["ratio"] for x in recA["decade_ratios"]] == [float(rA[0]), float(rA[1])]
      and recA["two_decade_total_ratio"] == float(rA[2]))
print("B match:", [x["ratio"] for x in recB["decade_ratios"]] == [float(rB[0]), float(rB[1])]
      and recB["two_decade_total_ratio"] == float(rB[2]))

print("\n== out_of_box_B_observations ==")
print("recorded:", rec["out_of_box_B_observations"])
# out-of-box B: instances whose h_B exceeds the max H level (10000)
oob = sum(1 for r in xtab if r["h_B"] > max(H_levels))
print("recomputed (h_B > 10000):", oob)
