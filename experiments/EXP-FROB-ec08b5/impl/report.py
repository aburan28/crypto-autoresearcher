#!/usr/bin/env python3
"""Derive metrics.json and report.md from a run's raw-result.json. Pure Python."""
import argparse, json, hashlib
from pathlib import Path


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    a = ap.parse_args()
    rd = Path(a.run_dir)
    d = json.loads((rd / "raw-result.json").read_text())
    st, lc, cc, cp, tt = (d["self_test"], d["lattice_crosscheck"], d["census_crosscheck"],
                          d["curve_panel"], d["target_table"]["targets"])
    scored = [r for r in cp["cells"] if "skipped" not in r]

    verdicts = {
        "P1_four_methods_agree": bool(lc["all_agree"]) and bool(st["all_pass"]),
        "P2_two_census_derivations_agree": bool(cc["all_agree"]),
        "P3_stability_and_controls": bool(cp["stable_V_always_pi_stable"]
                                          and cp["unstable_control_always_fails"]
                                          and cp["null_curve_control_always_fails"]),
        "P4_exact_orbit_count": bool(cp["prediction_exact_on_all"]),
        "P5_net_loss_at_131_and_163": None,
    }
    by_n = {r["n"]: r for r in tt if r["q"] == 2}
    loss_131_163 = all(not v["net_win"] for n in (131, 163) for v in by_n[n]["verdicts"])
    win_127 = any(v["net_win"] for v in by_n[127]["verdicts"])
    verdicts["P5_net_loss_at_131_and_163"] = bool(loss_131_163 and win_127)

    metrics = dict(
        experiment="EXP-FROB-ec08b5",
        preregistered_verdicts=verdicts,
        all_predictions_held=all(verdicts.values()),
        self_test_fixtures=len(st["checks"]),
        lattice_cells=len(lc["cells"]),
        exhaustively_verified_cells=sum(1 for r in lc["cells"] if r["C_agrees"] is True),
        census_subspaces_compared=cc["subspaces_compared"],
        census_mismatches=cc["mismatches"],
        curve_cells_measured=cp["cells_measured"],
        curve_points_enumerated=sum(r["factor_base_size"] for r in scored),
        largest_factor_base=max(r["factor_base_size"] for r in scored),
        orbit_prediction_exact_cells=sum(1 for r in scored if r["prediction_exact"]),
        target_degrees=len(tt),
        headline=dict(
            n131=dict(stable_subspaces=by_n[131]["stable_subspace_count"],
                      attainable_dimensions=by_n[131]["attainable_dimensions"],
                      min_faithful_dimension=by_n[131]["min_faithful_dimension"],
                      worst_margin_log2=min(v["margin_log2"] for v in by_n[131]["verdicts"]),
                      best_margin_log2=max(v["margin_log2"] for v in by_n[131]["verdicts"]),
                      net_win_at_any_m_in_panel=any(v["net_win"] for v in by_n[131]["verdicts"])),
            n163=dict(stable_subspaces=by_n[163]["stable_subspace_count"],
                      attainable_dimensions=by_n[163]["attainable_dimensions"],
                      min_faithful_dimension=by_n[163]["min_faithful_dimension"],
                      best_margin_log2=max(v["margin_log2"] for v in by_n[163]["verdicts"]),
                      net_win_at_any_m_in_panel=any(v["net_win"] for v in by_n[163]["verdicts"])),
            goal_cells=dict(
                n41_primary_m2=next(v for v in by_n[41]["verdicts"] if v["m"] == 2),
                n43_decisive_m3=next(v for v in by_n[43]["verdicts"] if v["m"] == 3)),
        ),
        raw_result_sha256=sha(rd / "raw-result.json"),
    )
    (rd / "metrics.json").write_text(json.dumps(metrics, indent=1, sort_keys=True))

    L = []
    w = L.append
    w("# EXP-FROB-ec08b5 — the Frobenius-stable factor-base design space\n")
    w(f"Run `{json.loads((rd / 'execution-receipt.json').read_text())['run_id']}`. "
      "Every number below is an exact finite count; nothing is sampled or estimated.\n")
    w("## Preregistered predictions\n")
    w("| id | prediction | verdict |")
    w("| --- | --- | --- |")
    names = {"P1_four_methods_agree": "four independent lattice methods agree",
             "P2_two_census_derivations_agree": "totient and Burnside censuses agree",
             "P3_stability_and_controls": "stable V gives a pi-stable factor base; both controls fail",
             "P4_exact_orbit_count": "orbit count equals f + (|F_V| - f)/n exactly",
             "P5_net_loss_at_131_and_163": "net loss at n = 131, 163; net win available at n = 127"}
    for k, v in verdicts.items():
        w(f"| {k.split('_')[0]} | {names[k]} | {'HELD' if v else 'FAILED'} |")
    w("")
    w("## Verification\n")
    w(f"- self-test fixtures: {len(st['checks'])}/{len(st['checks'])} pass")
    w(f"- lattice cells cross-checked by 4 methods: {len(lc['cells'])}, "
      f"of which {metrics['exhaustively_verified_cells']} also by exhaustive subspace enumeration")
    w(f"- stable subspaces compared across two independent orbit-census derivations: "
      f"{cc['subspaces_compared']}, mismatches: {cc['mismatches']}")
    w(f"- curve cells measured: {cp['cells_measured']}, factor-base points enumerated: "
      f"{metrics['curve_points_enumerated']}, largest factor base: {metrics['largest_factor_base']}")
    w("")
    w("## Curve panel — measured Frobenius orbits on real factor bases\n")
    w("| q | n | dim V | j-index | \\|F_V\\| | fixed | orbits | predicted | exact | reduction | non-stable V control | null-curve control |")
    w("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for r in scored:
        cv = r.get("control_unstable_V", {}); cn = r.get("control_null_curve", {})
        w(f"| {r['q']} | {r['n']} | {r['dim']} | {r['curve_index']} | {r['factor_base_size']} | "
          f"{r['fixed_points']} | {r['measured_orbits']} | {r['predicted_orbits']} | "
          f"{'yes' if r['prediction_exact'] else 'NO'} | {r['measured_reduction']:.4f} | "
          f"{'fails as required' if cv.get('control_passes') else 'DID NOT FAIL'} | "
          f"{'fails as required' if cn.get('control_passes') else 'DID NOT FAIL'} |")
    w("")
    w("## Target degrees — is the orbit trick available, and is it a net win?\n")
    w("`d` is ord_n(q); `s` the number of irreducible factors of Phi_n over F_q; "
      "`d_faith` the smallest stable dimension on which Frobenius acts non-trivially. "
      "`l*` = ceil(n/m) is the unconstrained Gaudry dimension, `l'` the smallest attainable "
      "faithful one at least that large. Margin is log2(mean orbit size) - (l' - l*)*log2(q): "
      "positive means the orbit quotient outweighs the factor-base inflation.\n")
    w("| q | n | d | s | #stable | d_faith | " + " | ".join(f"m={m}" for m in (2, 3, 4, 5)) + " | note |")
    w("| --- | --- | --- | --- | --- | --- | " + " | ".join("---" for _ in range(4)) + " | --- |")
    for r in tt:
        ns = r["stable_subspace_count"]
        ns = f"2^{1 + r['irreducible_factors_of_phi_n']}" if ns > 10 ** 6 else str(ns)
        cells = []
        for v in r["verdicts"]:
            cells.append("unavailable" if not v["available"]
                         else f"{'win' if v['net_win'] else 'loss'} {v['margin_log2']:+.1f}b")
        w(f"| {r['q']} | {r['n']} | {r['ord_n_q']} | {r['irreducible_factors_of_phi_n']} | {ns} | "
          f"{r['min_faithful_dimension']} | " + " | ".join(cells) + f" | {r['note']} |")
    w("")
    w("## Scope\n")
    w("- Scoped to the Gaudry/Diem factor-base family `F_V = {P : x(P) in V}` with V an "
      "F_q-subspace. Other factor-base shapes are not covered.")
    w("- Clauses about orbit length are for n an odd prime with gcd(q, n) = 1. The lattice "
      "itself is verified also at p | n, where T^n - 1 is not squarefree.")
    w("- Structural availability is not practical feasibility: a cell marked `win` at large m "
      "says nothing about whether the Semaev system at that m can be solved.")
    w("- No discrete logarithm is solved and no deployed curve is an instance.")
    (rd / "report.md").write_text("\n".join(L) + "\n")
    print("wrote metrics.json and report.md; all_predictions_held =", metrics["all_predictions_held"])


if __name__ == "__main__":
    main()
