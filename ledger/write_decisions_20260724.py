#!/usr/bin/env python3
"""Coordinator decisions for the 2026-07-24 frontier wave."""
import json, sys
from pathlib import Path

LEDGER = Path("/Volumes/Volume/crypto-autoresearcher/ledger")

def q(s): return json.dumps(s, ensure_ascii=False)

def dec_yaml(d):
    L = ["coordinator_decision:", f"  id: {d['id']}", f"  context: {q(d['context'])}",
         f"  decision: {d['decision']}", "  target_ids: [" + ", ".join(d["targets"]) + "]",
         "  rationale:"]
    L += [f"    - {q(r)}" for r in d["rationale"]]
    L.append("  evidence_refs: [" + ", ".join(d["ev"]) + "]")
    L.append("  limitations:")
    L += [f"    - {q(x)}" for x in d["limitations"]]
    L.append("  next_actions:")
    L += [f"    - {q(x)}" for x in d["next"]]
    L += ["  decided_by: coordinator", '  decided_at: "2026-07-24"']
    return "\n".join(L) + "\n"

DECS = [
 dict(id="DEC-20260724-001",
  context="THM_INCBARRIER2 theory note: cross-character cancellation at alpha <= 1/2",
  decision="supported", targets=["H-INCB-001"],
  ev=["research/THM_INCBARRIER2.md", "research/verification/thm_incbarrier2_check_output.json"],
  rationale=[
   "Method-barrier theorem PROVED: the entire norm/moment certification family provably caps at alpha = 1/2 — at B = floor(p^{1/2}) the target o(sqrt(p)) sits below every norm scale; signed cross-x cancellation of the profile delta on its own generating set is NECESSARY (not an artifact of weak methods).",
   "New unconditional tool PROVED: the energy certificate |T3 - mu| <= (1/6)*sqrt(B*N2), no black box, never worse than the Weil bound, measured 8-70x sharper on all 21 toy factor bases (with a discovered 2-torsion correction term, verified).",
   "Conditional ladder PROVED and supersedes THM1's heuristic cap: under profile-moment hypothesis H(k), certification holds for alpha > (k+1)/(2k+1) — k=1: 2/3, k=2: 3/5, k -> infinity: 1/2; the x-side Holder route strictly dominates the character-side at every k.",
   "Exact closing inputs named: EN(k) profile-moment proofs, BIL(theta) bilinear bounds (alpha = 1/2 needs theta = 1/4; harvesting alpha in [1/5, 2/5] needs theta in [2/5, 7/10]), STRUCT self-coupling. The problem is now a single precise statement CC(alpha), alpha <= 1/2.",
   "Verification: 148 checks, 0 failures; every formula verified exactly on the three ledger curves + 21 toy factor bases."],
  limitations=["G1 not closed: fixed/adversarial-F certification at alpha <= 1/2 remains open, now as the named signed-cancellation statement; the 1/2 ceiling applies to the norm/moment METHOD family, not to all possible mathematics."],
  next=["No further experiment work on incidences. The theory frontier is exactly CC(alpha) or a BIL(theta) input; H-INCB-001 remains supported (uniform-x theorem) with the method ceiling on record."]),
 dict(id="DEC-20260724-002",
  context="THM_BKKMV2 theory note: Lemma-G decomposition + erratum against THM_BKKMV1 section 4",
  decision="supported", targets=["H-BKKMV-001"],
  ev=["research/THM_BKKMV2.md", "research/verification/thm_bkkmv2_verify.sage", "CORR-20260724-002"],
  rationale=[
   "Substantial progress on the all-m MV law: the two-root expansion (T1), weight grading (T2), exact b-degree per term (T3), and the b-extremal non-cancellation Theorem B (conditional on (T_m)) are PROVED, with (T_m) verified unconditionally at m = 4, 5 — the b-extremal channel of the saturation theorem is theorem-backed in the verified range.",
   "Lemma-G is now decomposed into three falsifiable gaps with verified computed ranges: G1 = (T_m) + (NZ_j) (Krawtchouk zeros mapped), G2 = covering (mechanized at m = 4, 0 uncovered), G3 = grade migration. Predictions on record: deg_b S_{6,7,8} = 23, 57, 135.",
   "Bottom-fiber law PROVED at m <= 6 symbolic + m = 7 numeric (torsion law c_m = +-prod[psi](0)^{N(m,k)}; no reshuffle); even-m t = 0 non-saturation confirmed at m = 6 (X^10 | u_6).",
   "ERRATUM issued and recorded (CORR-20260724-002, rule 4): THM_BKKMV1's m=5 u_5 verification hardcoded a^2 instead of a^3 — the affected claims (the V1 u_5 artifact, its c_5, the 'psi_5-refutation', 'u_3^3 | u_5 exactly', the 'multiplicity 4->3 reshuffle') are INVALIDATED; V1's main Theorem 2 statements stand (independently re-verified); the torsion law actually holds (convention flip). Original receipts untouched per immutability policy.",
   "Verification: 27/29 checks pass; both FAILs are stale hand-estimates encoded as expectations, analyzed in-note."],
  limitations=["The all-m MV law remains OPEN (G1/G2/G3); symbolic S_5 over QQ(a,b) still censored (mitigated, no conclusion depends on it); minor run-budget deviation recorded by the executor (reruns after a serialization crash)."],
  next=["H-BKKMV-001 remains supported (theorem at m <= 5 + m = 6 certificate). The MV theory program continues only through the named gaps G1-G3; the deg_b predictions at m = 6, 7, 8 are cheap falsifiable checks for a future certificate run."]),
 dict(id="DEC-20260724-003",
  context="EXP-SIG-006 D6 null baseline re-derivation: freeze-degree diagnosis",
  decision="supported_scoped", targets=["H-SIG-001"],
  ev=["EV-SIG-006", "RUN-EXP-SIG-006-a", "RUN-EXP-SIG-006-b", "RUN-EXP-SIG-006-d", "RUN-EXP-SIG-006-f"],
  rationale=[
   "The D6 null failure is DIAGNOSED as a clean scientific finding, not an instrument bug: it is the semi-regular model's FREEZE-DEGREE break — the Hilbert-series prediction freezes (first HF = 0) at D = n/3 + 3 (n=9 -> D6, 12 -> D7, 15 -> D8, 18 -> D9), while real quotients collapse to |V| (variety enumeration: |V_sem| = 6, |V_null| = 1; null rank = ncols - |V| exactly).",
   "Column-matched nulls (equal ncols by construction) STILL fail at D6 — equal support does not fix the freeze collapse; no histogram-only sr_pred recalibration exists at n = 9 D6. The residual_6 = 2,615 value remains inadmissible, as EV-SIG-005 held.",
   "Admissible window identified: the baseline is predicted VALID at D6 for n >= 12 (freeze at D7; sr_pred(12,6) = 156,520) — the degree axis is not closed, it was merely measured at an n where the model itself breaks.",
   "New confound recorded (rule 8): column-matching itself induces sem-like syzygies (N1 D5 extra = 369 on two independent constructions) — part of the sem D5 deficit (909 at n = 9) may be support-induced rather than cascade content; on-lattice n >= 12 nulls validate exactly, so the supported cascade at D <= 5 is unaffected.",
   "Controls: determinism/cross-session reproduction PASS (residual_6 = 2,615 and A-chain values reproduced exactly); N1 D5 anchor FAIL recorded as data; n = 12 D6 validation censored (needs chunked echelon)."],
  limitations=["Diagnosis proved at n = 9 (full 2^18 variety enumeration); the n >= 12 validity prediction is untested (censored); the support-induced-syzygy confound is quantified only at n = 9 D5 (369 of 909)."],
  next=["Dispatch EXP-SIG-008: validate the D6 baseline at n = 12 (null rank == sr_pred = 156,520 at D6, chunked echelon, hours-scale, checkpointed); if valid, re-measure sem residual_6 at n = 12 — the first admissible birth-law point. Also quantify the support-induced share of the D5 deficit at n = 12 (disentangles cascade content from support artifact)."]),
 dict(id="DEC-20260724-004",
  context="EXP-SIG-007 n=21 residual_5 (partial; checkpointed)",
  decision="inconclusive", targets=["H-SIG-001"],
  ev=["EV-SIG-007", "RUN-EXP-SIG-007-a", "RUN-EXP-SIG-007-b", "RUN-EXP-SIG-007-c"],
  rationale=[
   "Delivered within budget: residual_4 = 15 canonical at n = 21 (2n/3+1 law — SEVENTH consecutive point of the linear series, zero seed variance); D4 deficit 56 = 8n/3; closure series still growing at n = 21 (A3_5 = 800, A4_5 = 1,407 — increments increasing: +261/+321/+381).",
   "The decisive D5 quantities (deficit_5, residual_5) remain unmeasured: rank(M5) at n = 21 is hours-scale; seed 1 checkpointed at 48,000/778,394 cols (6.17%) with staged completion formulas and a memory-safe driver; null D5 censored (same cost) — all D5-stage numbers are PRELIMINARY per protocol.",
   "Controls pass (gate C1/C2/C3/C4a; C9a anchors bit-exact; union method promoted to primary and validated; staircase engine cross-validated at n = 12).",
   "Rule-8: support thinning continues (79.84% at n = 21); rankK5 near-saturated (10,373/10,374); no saturation shoulder through 6% of columns."],
  limitations=["residual_5/deficit_5 at n = 21 not measured (infrastructure censoring, not evidence); null D5 arm censored; completion estimated at 3-5 h/seed under capped invocations."],
  next=["Continue the checkpointed rank(M5) cells (seed 1 first) in later coordinator turns alongside the DREG n = 21 cell; the closure-increment acceleration (+261/+321/+381) is a second quantitative thread to watch when residual_5 lands."]),
 dict(id="DEC-20260724-005",
  context="EXP-DREG-004 n=21 sem D5 deficit cell (in progress, checkpointed)",
  decision="inconclusive", targets=["H-DREG-001"],
  ev=["EV-DREG-004", "RUN-DREG-004-MEASURE-N21-SEM-A"],
  rationale=[
   "Cell launched and certified through two continuation turns: 142,000/778,394 columns (18.24%), rank_acc 140,858 (lower bound only — no rank/deficit claimed); sr_pred(n=21, D=5) = 268,674 independently reproduced (control PASS); 16/16 checkpoint lineage verifications pass; zero infrastructure failures.",
   "Rule-8: sem column support 79.83% continues the 84.2/82.2/81.9/80.8 decline; dependent-column profile is NON-MONOTONE along the column order (full-pivot through 68k, dip at 68k-112k, exactly full-pivot again 112k-142k) — the deficit forms late in the column order, not uniformly.",
   "Cost model updated: ~8-9 h under the 300 s invocation cap, ~3.5-4.5 h in a long-budget session at chunk 24,000; RSS projected 15-20 GB at completion (within 48 GB)."],
  limitations=["Cell 81.76% unmeasured (budget censoring, not evidence); two-partition control not yet exercisable; null arm not started."],
  next=["Continue EXP-DREG-004 via continuation turns (resume command on record in EV-DREG-004); on completion, run the two-partition consistency control BEFORE any rank claim, then decide H-DREG-001 on the 5-point deficit series."]),
]

for d in DECS:
    p = LEDGER / f"{d['id']}.yaml"
    body = dec_yaml(d)
    if p.exists() and p.read_text() != body:
        print("REFUSE overwrite", p.name); sys.exit(1)
    p.write_text(body)
    print("wrote", p.name)

# Correction record for the THM_BKKMV1 erratum (rule 4: corrections create new records)
corr = """correction:
  id: CORR-20260724-002
  date: "2026-07-24"
  corrects: research/THM_BKKMV1.md section 4 (m=5 u_5 verification artifacts)
  reported_by: executor (THM_BKKMV2 verification suite, 27/29 checks)
  record_type: correction_of_artifacts (original receipts untouched per immutability policy)
  defect: >-
    research/verification/thm_bkkmv1_verify_m5.sage (stage u5) hardcoded the X^3-coefficient
    of u_4 with a^2 instead of a^3; the resulting u_5 is not even weight-homogeneous
    (THM_BKKMV2 T2 exposes this).
  invalidated_claims:
    - "V1's symbolic u_5 artifact and its c_5 factorization (research/verification/thm_bkkmv1_verify_results_u5.json)"
    - "the 'psi_5(0) | c_5 refutation' sub-conjecture verdict"
    - "the 'u_3^3 | u_5 exactly' observation"
    - "the 'multiplicity 4 -> 3 reshuffle' statement"
  unaffected_claims: >-
    THM_BKKMV1's main Theorem 2 statements (degree tower, leading-form recursion, universal
    diagonal corner, saturation theorem at m <= 5, MV law reduction) — independently re-verified
    in THM_BKKMV2's suite.
  corrected_statements: >-
    The torsion law c_m = +-prod[psi_{k-1} psi_{k+1}](0; -a, -b)^{N(m,k)} HOLDS (verified
    symbolically at m = 3, 5 and by exact integer division at m = 7); multiplicities equal the
    naive sign counts N(m,k) at every m <= 7 (no reshuffle). See research/THM_BKKMV2.md section 8.
  impact_on_decisions: >-
    DEC-20260722-003 (H-BKKMV-001 supported) is UNAFFECTED: it rests on the saturation theorem
    and the m = 3..6 MV certificates, none of which touch the invalidated u_5 artifact claims.
  evidence_refs: [research/THM_BKKMV2.md, research/verification/thm_bkkmv2_verify.sage, DEC-20260724-002]
"""
p = LEDGER / "CORR-20260724-002.yaml"
if p.exists() and p.read_text() != corr:
    print("REFUSE overwrite", p.name); sys.exit(1)
p.write_text(corr)
print("wrote", p.name)
