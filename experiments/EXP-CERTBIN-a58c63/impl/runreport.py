"""run-report.md writer (mechanical; observations and rule outputs only)."""
import os


def fmt(v, nd=4):
    if isinstance(v, float):
        return f"{v:.{nd}g}"
    return str(v)


def write(run, plan, spec, cs, checks, glob_ck, dr, validity, raw, manifest):
    e = spec["experiment"]
    manifest = manifest["run"]
    L = []
    a = L.append
    a(f"# Run report: {e['id']} / {plan['run_id']}")
    a("")
    a("Observations and mechanically applied decision rules only. No hypothesis status, "
      "evidence record or knowledge entry is written or implied here. Verdict strings are the rule "
      "outputs defined in the frozen specification (DB-1..DB-12); adjudication belongs to the review "
      "round and the Coordinator.")
    a("")
    a("## Claim tier and scope (verbatim from the specification)")
    a("")
    a(f"- claim_tier: {e['claim_tier_and_scope']['claim_tier']}")
    a(f"- statement: {e['claim_tier_and_scope']['statement']}")
    a(f"- sota_delta: {e['claim_tier_and_scope']['sota_delta']}")
    a(f"- dominated_by: {e['claim_tier_and_scope']['dominated_by']}")
    a(f"- affected_vs_safe: {e['claim_tier_and_scope']['affected_vs_safe']}")
    a("")
    a("A \"STABLE\" regime-B verdict at l = 6 (D = 66) is not a P-GPU result (DB-7; Lemma B-S (d)). "
      "No GPU was run. Python/numpy wall time is not GPU cost.")
    a("")
    a("## Validity")
    a("")
    a(f"- status: **{validity['status']}**")
    a(f"- run-voiding failures: {validity['void_reasons'] or 'none'}")
    a(f"- partial invalidations: {validity['partial_invalidations'] or 'none'}")
    a(f"- protocol version: {manifest['protocol_version']} (specification v1 + {manifest['amendment'].get('id')}, "
      f"sha256 {manifest['amendment'].get('sha256')}, commit {manifest['amendment'].get('commit')})")
    a(f"- schedule: {manifest['schedule']['chosen']}; basis: {manifest['schedule']['basis']} "
      f"(T_proj = {fmt(manifest['schedule']['T_proj_single_worker_seconds_not_binding'])} s single-worker, not binding)")
    a(f"- raw-result agrees with cell-summary on every recomputed primary count: {raw['all_agree']}")
    a("")
    a("## Protocol version 2 changes that bind a verdict (AMD-20260924-3a9f06 C-13)")
    a("")
    a("- C-1/C-2 (ruling 1): first-match classification R0-R6; E3 success = R3 COLUMN at the target's own first "
      "non-pivot column. Binds MB2, MB5, DB-5 and hence DB-7 at the l = 5 cells. The rejected PREFIX-first reading is "
      "reported as E3_prefix_first_sensitivity in cell-summary.json and feeds no rule.")
    a("- C-3 (C-CLASS / INV-10), C-4/C-5 (C-REPLAYB v2 / INV-5 v2): bind the validity of DB-3, DB-4, DB-5, DB-11.")
    a("- C-6/C-7: K_B by the T_strict-guided computation on one S_probe stream; K_B(cell) = sum over unsat references (DB-3, DB-4).")
    a("- C-8/C-9: F-SAT/F-PLANT exhaustion stops; the E3 arm is their union by x_R; DB-5 UNDERPOWERED below 100; DB-7 NOT EVALUABLE on a void or underpowered conjunct.")
    a("- C-11/C-12: per-family modal; C-DELTA/C-RANKB also on the regime-B nulls (DB-8, M3).")
    a("- C-14/C-16: 18 retired seeds replaced by old + 10000; the count schedule is C_std by C-PILOT's own consequence.")
    a("- C-25: DB-5 and DB-7 at the l = 5 cells become exploratory_only if the review round finds that ruling 1 chose "
      "between two readings that both test C3. The coordinator prior (a)-(g) below is scored as written; it was not "
      "updated, and dev outputs (not frozen outputs) were seen before protocol version 2 was fixed.")
    a("")
    a("## Decision rules per cell")
    a("")
    for lab, d in dr["per_cell"].items():
        a(f"### {lab}")
        a("")
        for k in ("DB-1", "DB-2", "DB-3", "DB-5", "DB-6", "DB-7", "DB-8", "DB-10", "DB-11"):
            v = d.get(k, {})
            verdict = v.get("verdict")
            if k == "DB-10":
                verdict = f"KR1/RR-2: {v.get('KR1_RR2')}; TS1R/RR-4: {v.get('TS1R_RR4')}; P-C3: {v.get('P-C3')}" if "KR1_RR2" in v else v.get("verdict")
            a(f"- **{k}** ({v.get('regime', '')} {('D = ' + str(v.get('D'))) if v.get('D') else ''} "
              f"{v.get('granularity', '')}): {verdict}")
        a(f"- **DB-9**: {d['DB-9']['per_regime']}")
        a(f"- DB-7 failing conjuncts: {d['DB-7']['failing_conjuncts']}")
        a("")
    a("### DB-4 (n-scaling at fixed l)")
    a("")
    for k, v in dr["DB-4"].items():
        a(f"- {k}: {v.get('verdict')}; interval {v.get('ratio_interval_95', {}).get('lo_str')}..{v.get('ratio_interval_95', {}).get('hi_str')}; "
          f"inputs {v.get('inputs')}; (K_B19/K_B17)/4 = {fmt(v.get('predicted_(K_B19/K_B17)/4'))}; consistent: {v.get('consistent_with_prediction')}")
    a("")
    a(f"DB-12 primary/secondary: {dr['DB-12']}")
    a("")
    a("## Pre-registered predictions: observed values against the frozen thresholds")
    a("")
    for lab, c in cs.items():
        B = c["regime_B"]
        a(f"### {lab}")
        a(f"- PB-1 regime-B T_strict retention_family (unsat): {fmt(B['MB1']['retention_family'])} (min {fmt(B['MB1']['min'])}); threshold >= 0.9")
        a(f"- PB-2 break counts vs Poisson 99.9%: " + "; ".join(
            f"{k}: X = {d['X']}, K_B = {d['K_B']}, interval {[d['poisson999']['lo'], d['poisson999']['hi']] if d['poisson999'] else None}, inside = {d['inside']}"
            for k, d in B["MB3"]["per_ref"].items()))
        a(f"- PB-4 E3 (pooled, per unsat ref): " + "; ".join(
            f"{k}: {d['pooled']['E3_count']}/{d['pooled']['n']}" for k, d in B["MB5"]["per_ref"].items())
          + f" (evaluable: {B['MB5']['evaluable']})")
        a(f"- PB-5 unsat arm 1 in R_66: {B['MB4']['F-S3']['unsat']['one_in_R66']}/{B['MB4']['F-S3']['unsat']['n']}; "
          f"rank distribution {B['MB4']['F-S3']['unsat']['rank_distribution']}")
        if c.get("regime_A"):
            A = c["regime_A"]["D4"]
            a(f"- PB-6 / PC-3 regime-A T_strict retention_family (D = 4): {fmt(A['MA1']['strict_unsat']['retention_family'])}")
            a(f"- PC-1 K_rank_hull vs dim W (D = 4): " + "; ".join(f"{k}: {v['K_rank_hull']}/{v['dimW']}" for k, v in A["MA1"]["hull"].items()))
            ts = A["MA2_TS1R"].get("F-S3")
            if ts:
                a(f"- PC-2 TS1R (F-S3, D = 4): m = {ts['m']}, o = {ts['o']}, P = {ts['P_float']}, RR-4: {ts['verdict_RR4']}")
        sz = B.get("sizing_maximizing_ref")
        if sz:
            a(f"- PB-7 regime-B pruned dense bytes (maximizing ref {sz['ref']}): {sz['pruned_dense_bytes']} "
              f"(full {sz['full_dense_bytes']}); saving_strict {fmt(sz['saving_strict'])}")
        a(f"- TS2G delta tail: {B['MB4']['tail_delta_extremes']}")
        a("")
    a("## Coordinator prior (a)-(g): observed items")
    a("")
    a("Reported as the observed quantity beside each prior item; whether an item is 'overturned' is "
      "stated only where the prior names a checkable outcome.")
    for lab, c in cs.items():
        B = c["regime_B"]
        d = dr["per_cell"][lab]
        a(f"- {lab}: (a) C-DELTA pass {checks[lab]['C-DELTA']['pass']}, C-RANKB pass {checks[lab]['C-RANKB']['pass']}; "
          f"(b) DB-2 {d['DB-2']['verdict']}; (c) DB-1 {d['DB-1']['verdict']}; (d) DB-3 {d['DB-3']['verdict']}; "
          f"(e) DB-5 {d['DB-5']['verdict']}; (f) DB-6 {d['DB-6']['verdict']}; (g) DB-7 {d['DB-7']['verdict']}")
    a("")
    a("## Instrument checks (M5)")
    a("")
    for k, v in glob_ck.items():
        a(f"- {k}: {v.get('pass', v.get('all_pass'))}")
    for lab, ck in checks.items():
        a(f"- {lab}: " + ", ".join(f"{k} {v.get('pass') if isinstance(v, dict) else v}" for k, v in ck.items()
                                   if isinstance(v, dict) and "pass" in v))
    a("")
    a("Every failure is listed verbatim in instrument-checks.json. Deviations and interpretations: "
      "implementation.md and trial-plan-v1.json (interpretations).")
    p = os.path.join(run.out, "run-report.md")
    with open(p, "x") as f:
        f.write("\n".join(L) + "\n")
