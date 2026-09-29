#!/usr/bin/env python3
"""Diff my frozen V2 recomputation (v2_recomputation.json, hashed before
cost_table.py was opened) against the archived STATIC-001 outputs."""
import json
import os
import sys

import yaml

PKG = "/home/user/crypto-autoresearcher/experiments/EXP-PFDR-c04716/runs/STATIC-001"
HERE = os.path.dirname(os.path.abspath(__file__))

mine = json.load(open(os.path.join(HERE, "v2_recomputation.json")))
ct = yaml.safe_load(open(os.path.join(PKG, "cost-table.yaml")))
fx = yaml.safe_load(open(os.path.join(PKG, "fixtures.yaml")))
th = yaml.safe_load(open(os.path.join(PKG, "thresholds.yaml")))

mine_by_key = {(int(c["log2_N"]), c["m"], c["D_0"], round(c["omega"], 3)): c
               for c in mine["table_54"]}

print("=" * 100)
print("A. 54 TABLE CELLS: my log2_T / log2_memory vs archived cost-table.yaml")
print("=" * 100)
worst_T = (0.0, None)
worst_M = (0.0, None)
n_cmp = 0
rows = []
for c in ct["cells"]:
    key = (int(c["log2N"]), c["m"], c["D0"], round(float(c["omega"]), 3))
    m_ = mine_by_key[key]
    dT = m_["log2_T"] - float(c["log2_T"])
    dM = m_["log2_memory"] - float(c["log2_memory"])
    dn = m_["n"] - int(c["n_rounded"])
    drho = m_["log2_rho"] - float(c["prior_rho_log2_T"])
    n_cmp += 1
    if abs(dT) > worst_T[0]:
        worst_T = (abs(dT), key)
    if abs(dM) > worst_M[0]:
        worst_M = (abs(dM), key)
    rows.append((key, m_["log2_T"], float(c["log2_T"]), dT, dM, dn, drho,
                 m_["beats_rho"], bool(c["beats_rho_on_time_conditionally"])))
for r in rows:
    key, mt, at, dT, dM, dn, drho, mb, ab = r
    flag = "" if (abs(dT) < 1e-3 and mb == ab) else "   <<<"
    print(f"  N{key[0]:>3} m{key[1]} D0{key[2]} w{key[3]:<5} mine {mt:>9.4f} arch {at:>9.4f} "
          f"dT {dT:>+9.6f} dMem {dM:>+9.6f} dn {dn:>+2d} drho {drho:>+8.6f} "
          f"beats mine={mb} arch={ab}{flag}")
print(f"\n  cells compared: {n_cmp}")
print(f"  MAX |log2_T  difference|: {worst_T[0]:.8f} at {worst_T[1]}")
print(f"  MAX |log2_mem difference|: {worst_M[0]:.8f} at {worst_M[1]}")
print(f"  beats_rho agreement: {sum(1 for r in rows if r[7] == r[8])}/{n_cmp}")
print(f"  archived beats_rho count: {sum(1 for r in rows if r[8])}; mine: {sum(1 for r in rows if r[7])}")

print()
print("=" * 100)
print("B. HAND-VALUE DISCREPANCIES as archived, and as I recompute them")
print("=" * 100)
for c in ct["cells"]:
    if c.get("hand_T_log2") is not None:
        key = (int(c["log2N"]), c["m"], c["D0"], round(float(c["omega"]), 3))
        m_ = mine_by_key[key]
        my_disc = m_["log2_T"] - float(c["hand_T_log2"])
        print(f"  N{key[0]:>3} m{key[1]} D0{key[2]} w{key[3]:<5} hand {c['hand_T_log2']:>7} "
              f"src={c['hand_source']!r:<46} arch_disc {c['discrepancy_T_script_minus_hand']:>+8} "
              f"my_disc {my_disc:>+9.4f}  within1_arch={c['within_1_log2_of_hand']}")

print()
print("=" * 100)
print("C. FIXTURES: archived vs mine")
print("=" * 100)
print("  F1 null slice (archived pass=%s)" % fx["F1_null_slice_reproduces_da1428"]["pass"])
mine_f1 = {(f["m"], f["s"], round(f["omega"], 3)): f for f in mine["a_null_slice_fixtures"]}
for c in fx["F1_null_slice_reproduces_da1428"]["cells"]:
    k = (c["m"], c["s"], round(float(c["omega"]), 3))
    f = mine_f1[k]
    print(f"    m{k[0]} s{k[1]} w{k[2]:<5} arch dec={c['strictly_decreasing']} argmin_formula={c['argmin_k_formula_leaf']} "
          f"argmin_rf={c['argmin_k_rootfinding_leaf']} maxratio={c['max_log2_ratio_C(k+1)/C(k)']} logC_k0={c['log2C_k0']}"
          f"\n         mine dec={f['strictly_decreasing']} argmin={f['argmin_k']} leaf={f['k_max']} "
          f"maxstep={f['max_step']:.4f} logC_k0={f['logC_at_0']:.4f}  dC0={f['logC_at_0'] - float(c['log2C_k0']):+.6f}")

print()
for key in fx:
    if key.startswith("F2"):
        f2 = fx[key]
        print(f"  {key} (archived pass={f2.get('pass')})")
        print("    archived keys:", list(f2.keys()))
        for c in f2.get("cells", []):
            print("   ", {k: v for k, v in c.items() if k != "scan"})
    if key.startswith("F3"):
        f3 = fx[key]
        print(f"  {key} (archived pass={f3.get('pass')})")
        for c in f3.get("cells", []):
            print("   ", {k: v for k, v in c.items() if k != "scan"})
    if key.startswith("SMALL") or key.startswith("small"):
        sm = fx[key]
        print(f"  {key} (archived pass={sm.get('pass')})")

print()
print("=" * 100)
print("D. THRESHOLDS at 256 bits: archived vs mine")
print("=" * 100)
mine_th = {(t["m"], round(t["omega"], 3)): t for t in mine["e_thresholds_256"]}
for row in th["thresholds"]:
    if int(row["log2N"]) != 256:
        continue
    k = (row["m"], round(float(row["omega"]), 3))
    mt = mine_th.get(k)
    print(f"  m{k[0]} w{k[1]:<5} arch bracket=({row['largest_even_D0_with_T_below_rho']}, "
          f"{row['smallest_even_D0_with_T_at_or_above_rho']}) predicted={row.get('predicted_bracket_256')!r} "
          f"matches={row.get('matches_prediction')}")
    if mt:
        print(f"          mine bracket=({mt['largest_D0_below_rho']}, {mt['smallest_D0_at_or_above_rho']})")
    arch_scan = {r["D0"]: float(r["log2_T"]) for r in row["scan"]}
    if mt:
        for r in mt["rows"]:
            if r["D_0"] in arch_scan:
                print(f"            D0 {r['D_0']:>2}: mine {r['log2_T']:>9.4f} arch {arch_scan[r['D_0']]:>9.4f} "
                      f"d {r['log2_T'] - arch_scan[r['D_0']]:+.6f}")
