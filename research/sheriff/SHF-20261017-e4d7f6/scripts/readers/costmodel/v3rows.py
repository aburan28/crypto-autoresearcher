#!/usr/bin/env python3
"""Recompute n=41/53/61 baseline-row S fields from crypto rule/v3 analysis.json.
Usage: python3 -I -B v3rows.py <analysis.json> <baselines.json>"""
import json, sys
a = json.load(open(sys.argv[1])); b = json.load(open(sys.argv[2]))
rows = {r["n"]: r for r in b["baselines"]}
for s in a["sizes"]:
    n = s["n"]
    on = s["s_ic_online_mean"]; st = s["s_setup"]
    diag = s.get("diagnostics", {})
    print(f"n={n} s_setup={st:.6f} s_ic_online_mean={on:.6f} setup+online={st+on:.6f} "
          f"s_curve_construction={diag.get('s_curve_construction')} cold_ratio={s['cold_ratio_ic_over_rho']['value']:.4f} "
          f"s_rho_setup={s['s_rho_setup']:.4f} s_rho_online={s['s_rho_online_mean']:.4f}")
    print("   diagnostics keys:", list(diag.keys()))
    if n in rows:
        r = rows[n]
        print(f"   ROW: cold={r['s_ic_cold']} online={r['s_ic_online']} setup={r['s_ic_setup']} gap_cold={r['gap_cold_ic_over_rho']['value']} s_rho_cold={r['reference_rho']['s_rho_cold']}")
        print(f"   check setup: |row - analysis| = {abs(r['s_ic_setup']-st):.2e}; online: {abs(r['s_ic_online']-on):.2e}; cold vs setup+online: {abs(r['s_ic_cold']-(st+on)):.2e}")
        rc = s['s_rho_setup'] + s['s_rho_online_mean']
        print(f"   rho cold recomputed {rc:.4f}; IC cold/rho cold {(st+on)/rc:.4f}")
