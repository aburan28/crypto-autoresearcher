#!/usr/bin/env python3
"""Coordinator decision writer for the 2026-07-18 experiment batch.

Writes DEC-20260718-001..016 and updates the status field of each target
hypothesis record. Idempotent: refuses to overwrite an existing DEC with
different content.
"""
import json, re, sys
from pathlib import Path

ROOT = Path("/Volumes/Volume/crypto-autoresearcher")
LEDGER = ROOT / "ledger"
DATE = "2026-07-18"

def q(s):  # YAML-safe double-quoted scalar
    return json.dumps(s, ensure_ascii=False)

def dec_yaml(d):
    lines = ["coordinator_decision:"]
    lines.append(f"  id: {d['id']}")
    lines.append(f"  context: {q(d['context'])}")
    lines.append(f"  decision: {d['decision']}")
    lines.append("  target_ids: [" + ", ".join(d["target_ids"]) + "]")
    lines.append("  rationale:")
    for r in d["rationale"]:
        lines.append(f"    - {q(r)}")
    lines.append("  evidence_refs: [" + ", ".join(d["evidence_refs"]) + "]")
    lines.append("  limitations:")
    for l in d["limitations"]:
        lines.append(f"    - {q(l)}")
    lines.append("  next_actions:")
    for n in d["next_actions"]:
        lines.append(f"    - {q(n)}")
    lines.append("  decided_by: coordinator")
    lines.append(f'  decided_at: "{DATE}"')
    return "\n".join(lines) + "\n"

DECISIONS = [
 dict(n=1, ctx="EXP-JET-001 tangent-split (first-jet/dual-number) relation screening vs serial-S3 harvester",
  decision="reject_scoped", targets=["H-JET-001"], ev=["EV-JET-001", "RUN-JET-001-b"],
  rationale=[
   "Survival sigma = 1.0000 exactly at all four sizes (p=101..1009, 9984 pairs): the epsilon-system is implied by the zeroth-order solution set (Cramer determinant nonzero on 100% of pairs) — the candidate's named fatal obstruction #1, measured, not argued.",
   "Tangent-split is pure additive overhead: per-relation cost ratio 0.7733/0.7931/0.8151/0.8402 vs the >=4x promotion requirement; C_lin+C_nonlin > C_nonlin always.",
   "Charged exponents: classical 1.0616 [0.9984,1.1249], tangent 1.0240 [0.9615,1.0865] — 0.49 lies far below both CIs; neither promotion prong crossed.",
   "Controls PASS (POS-1 0/3133 mismatches; NEG-1 no leakage on 1200 non-relations)."],
  limitations=["Toy p <= 2^10, m=3, fixed-B grids; toy exponents constant-dominated; closes only the dual-number tangent-screen scope (rule 6)."],
  next=["H-JET-001 = rejected_scoped. D1 (JETB) barrier consistency result makes a revival of jet channels unlikely; no follow-up experiment unless the D1 theory note is overturned."]),
 dict(n=2, ctx="EXP-INC-001 output-sensitive finite-field incidence reporting for chord harvesting (m=3)",
  decision="reject_scoped", targets=["H-INC-001"], ev=["EV-INC-001", "RUN-INC-001-c"],
  rationale=[
   "Zero output sensitivity measured: candidate-test exponent 2.078 for enumerator and both reporters (exactly Theta(B^2), zero pairs avoided); marginal cost 341.2 ops/incidence is candidate-proportional, not output-proportional.",
   "Positive control PASS (reporter == enumerator multisets, 36/36); negative control PASS (random non-EC lines not cheaper).",
   "Complete-cost trends 0.551–0.736 per row, none below 0.49; total/(0.886*sqrt(n)) grows 4.71 -> 8.12 along the n^2/5 row.",
   "EC chord richness equals the random-line prediction (I_EC=13 vs I_rand=12) — consistent with the INCB ceiling measurement."],
  limitations=["Toy p <= 2^12, m=3 only, B <= 28; the candidate itself stated it lives in the m=4/5 regime or dies — m=4/5 supply arithmetic remains adverse per RT-1476 and no reporting primitive was found even at m=3; closes the tested scope (rule 6)."],
  next=["H-INC-001 = rejected_scoped. The RT-1472 'implicit deck with o(L) setup' loophole is narrowed: grid-bucketing + algebraic partition variants both failed to achieve output sensitivity; a fundamentally different primitive would be required."]),
 dict(n=3, ctx="EXP-STR-001 displacement-rank relation matrices from arithmetic-progression supports",
  decision="reject_scoped", targets=["H-STR-001"], ev=["EV-STR-001", "RUN-STR-001-a"],
  rationale=[
   "Both disproof-track criteria measured: (i) displacement rank alpha grows linearly in B (alpha/B 0.56–0.77, classic alpha at the generic maximum in 32/35 instances, identical to random baseline — no Toeplitz/Hankel structure); (ii) AP relation-stage penalty 17.5x–4128.6x vs the 1.5x gate, worsening with size (supply-side collapse: AP tuples cover only 3.3–13.2% of the group).",
   "Structured solve at the measured alpha costs 4.9–39x MORE ops than generic Wiedemann.",
   "Controls PASS (D={0} baseline reproduced 36/36; random x-sets show AP frequency at the exact combinatorial value, 6/6).",
   "Cause identified in-run: ~50% non-residue gaps in the x-interval factor base break translation invariance — the candidate's own obstruction #2."],
  limitations=["Toy p <= 2^12, m in {3,4}, D <= 64; structured-solve numbers model-only per frozen scope; closes the AP-support design scope (rule 6)."],
  next=["H-STR-001 = rejected_scoped. Designed-support structure for operator compression is closed for AP geometries; other support geometries would need a new candidate with a translation-invariance mechanism."]),
 dict(n=4, ctx="EXP-NET-001 elliptic-net (EDS) Somos-identity relation supply",
  decision="reject_scoped", targets=["H-NET-001"], ev=["EV-NET-001", "RUN-NET-001-a"],
  rationale=[
   "Collision statistics equal the random-oracle birthday model: total enrichment 1.05–1.20, fully accounted for by the measured index-1 universal-tautology class (581 collisions, k-independent) — the candidate's named strongest kill argument (Somos restricted to a k-fiber yields tautologies) is the measured regime.",
   "Charged k-recovery exponents 1.97–2.80 (optimistic/full-scan) vs BSGS 1.17–1.32 at identical accounting; ops ratio grows 24 -> 135 with size; rank-per-op gate missed by ~40x.",
   "Controls PASS (net-recomputed Tate pairing == Sage tate_pairing 3/3; EDS translation identity 18/18; random-oracle control 0.98–1.06).",
   "Consistency sets are large (|S| mean 11–68): collisions are k-unspecific — relations encode the group law, not k."],
  limitations=["Toy n <= 1607, B = ceil(sqrt(n)); Weil->Tate pairing substitution in the positive control (same Stange theorem family); closes the net-domain relation-supply scope (rule 6)."],
  next=["H-NET-001 = rejected_scoped. Record the unresolved k-dependence of product-value distributions (permuted nets 0.52–0.70x Q-involving collisions) as an observation, not a channel."]),
 dict(n=5, ctx="EXP-BKK-001 tropical/Newton-polytope (BKK) decomposition of the target-sectioned Semaev family",
  decision="reject_scoped", targets=["H-BKK-001"], ev=["EV-BKK-001", "RUN-BKK-001-a", "RUN-BKK-001-b", "RUN-BKK-001-c", "RUN-BKK-001-d"],
  rationale=[
   "Newton saturation measured exactly: sectioned S_m support fills the full box at m=3,4,5; MV = Bezuout_box exactly (rho_m = 1 at every m) — the candidate's named fatal obstruction, triggering its disproof track (>= 0.95 at m=5; measured 1.0).",
   "log MV/log Bezout = 1.0 at m=5 caps any BKK-based algorithm at the dense driver; MX-1478's 1.979 unchanged.",
   "NEG-1/NEG-2 PASS: random same-support systems give identical MV and identical op counts — no EC-specific sparse structure exists at the polytope level.",
   "POS-1 PASS: sparse and dense solution sets identical (54/54)."],
  limitations=["Toy p <= 2^10, m <= 5; unsectioned S_m IS materially sparser (439/625 at m=4) — the saturation is a property of target-sectioning; closes the support-aware-solving scope for sectioned systems (rule 6)."],
  next=["H-BKK-001 = rejected_scoped. Cross-confirmed by the independent D2 certificate (EV-BKKMV-001)."]),
 dict(n=6, ctx="EXP-EQJ-001 isotypic (S3 x (Z/2)^3) decomposition of the m=4 relation space",
  decision="reject_scoped", targets=["H-EQJ-001"], ev=["EV-EQJ-001", "RUN-EQJ-001-a", "RUN-EQJ-001-b", "RUN-EQJ-001-c"],
  rationale=[
   "Exactly 4 of 10 isotypic blocks carry anything (6 blocks exactly zero at all 9 cells, representation-theoretically forced by S3-invariance of the fiber indicator); rank never splits — every surviving block has r_lambda = r_full.",
   "LA factor: 1.0 (single-sufficient-block) or 0.25 exactly (all-blocks accounting — a 4x LOSS); the >=4x storage gain is the pre-existing FHJRV symmetrization factor, not new.",
   "The candidate's disguised-repetition kill line is the measured regime: B3 reduces to symmetrization with bookkeeping.",
   "Controls PASS (Parseval exact; negative control shows the EC block profile is NOT generic — |z| up to 152 — so the kill is 'no asymptotic gain', not 'not EC-specific').",
   "Reusable structural observations recorded: distinct-row collapse (64–67/12/11–15 distinct rows), near-full orbit bundles, small-integer kernel vectors."],
  limitations=["Toy p <= 2^12, m=4, 3 seeds; charged-exponent proxy non-monotone at toy scale (no exponent claim); closes the equivariant-decomposition scope (rule 6)."],
  next=["H-EQJ-001 = rejected_scoped. The distinct-row collapse observation is logged for the idea pool (relation-module compressibility), detached from the isotypic mechanism."]),
 dict(n=7, ctx="EXP-TRA-001 transfer-operator (Koopman) spectral channel on the translation walk",
  decision="reject_scoped", targets=["H-TRA-001"], ev=["EV-TRA-001", "RUN-TRA-001-a"],
  rationale=[
   "Localization L = O(1): fitted growth exponent delta = 0.0195 (super-constant required); L_eff median = 1.0 at all sizes; hits statistically at chance (negative-control floor).",
   "Positive control PASS (full-resolution C=n recovers k exactly — the channel exists in principle and is circular at C ~ n, as predicted).",
   "Sharper than the predicted barrier (rule 8 observation): all 54 exact coarse operators are exactly reversible (detailed-balance residual 2.5e-17) with entirely real spectra — for negation-symmetric x-interval partitions there are NO eigenvalue phases at any budget; the phase channel is destroyed structurally by the +/- fold.",
   "Charged cost 11358–51135 x sqrt(n); no sub-sqrt(n) regime approached."],
  limitations=["Toy p <= 2^12; x-interval partitions only; the reversibility observation suggests a provable symmetry theorem but is not yet one."],
  next=["H-TRA-001 = rejected_scoped; archive as a barrier measurement with the fitted L(S,C) law. Add 'coarse-grained translation operators on cyclic groups are character-mixing; negation-symmetric partitions are reversible with real spectra' to the theory-note candidate list (no experiment needed)."]),
 dict(n=8, ctx="EXP-TTN-001 tensor-network contraction of the recursive Semaev tensor with rank truncation",
  decision="reject_scoped", targets=["H-TTN-001"], ev=["EV-TTN-001", "RUN-TTN-001-b"],
  rationale=[
   "Promotion gate (bond-rank growth exponent < 1 at recall >= 0.99) NOT crossed: alpha = 1.161 (3-point) / 1.322 (root-only), identical at p = 101/431/1009.",
   "Genuine structural finding against the named obstruction: recursion bond ranks are exactly and stably LOW (3, 6, 15 at d = 2, 4, 8 vs full 3, 25, 81), field-size independent (beta = 0.000000), matching the Sylvester multiset count C(2^{m-3}+2, 2) exactly.",
   "But recall >= 0.99 needs the FULL bond rank over F_p: recall at chi_full - 1 is 0.0000–0.016; truncation has no negligible directions to discard.",
   "The exact combinatorial fit predicts exponent -> 2 (disproof region) for m >= 6 — recorded as a falsifiable extrapolation, not evidence.",
   "Controls all pass (contraction == direct definition 27/27 cells; random tensors full rank 27/27; CUR exact at full rank)."],
  limitations=["Toy p <= 2^10, m <= 5, one truncation rule (deterministic prefix-CUR over F_p); counting only, not enumeration; window slopes from 2–3 points; m >= 6 untested (rule 6)."],
  next=["H-TTN-001 = rejected_scoped. Two follow-ups are theory-flavored, not new attack experiments: (i) test the chi(m) = C(2^{m-3}+2, 2) law at m = 6 (predicts chi = 45) as a certificate; (ii) investigate alternative truncation rules only if a norm-bearing or border-rank relaxation is proposed with a mechanism."]),
 dict(n=9, ctx="EXP-NCP-001 noncommutative path-algebra syzygy search on the correspondence quiver",
  decision="reject_scoped", targets=["H-NCP-001"], ev=["EV-NCP-001", "RUN-NCP-001-a"],
  rationale=[
   "The candidate's named bookkeeping condition holds over the tested scope: the commutative quotient reproduces ALL found NC relations (0 violations on full histograms; 94,472 shadow replays) — commutator collapse is the measured regime.",
   "Every measured charged exponent >= 0.80 > 0.49 (NC OLS 1.155, comm_eq 0.990); per-relation cost grows ~linearly in n; hit rates track uniform-draw expectation ops/n.",
   "Controls PASS (2,400 engine checks + 12/12 k-recoveries; negative control as designed).",
   "Strict inclusion observed at (431, B=4, n=439): NC words reach only 350/439 values vs 437/439 commutative with 7.6x fewer ops — word-order constraints prune, never extend."],
  limitations=["Toy p in {101,431}, B in {4,8}, degree <= 6 truncated NC-GB; the commutator-generation theorem itself remains unproven (theory note). Closes the tested scope (rule 6)."],
  next=["H-NCP-001 = rejected_scoped. Theory-note candidate: prove the evaluation kernel KQ -> Z/n is generated by commutators (would close the whole noncommutative-correspondence direction for prime fields by theorem, no further experiments)."]),
 dict(n=10, ctx="EXP-JETB-001 generic-model barrier for jet-augmented relation channels (D1, theory-track toy certification)",
  decision="supported_scoped", targets=["H-JETB-001"], ev=["EV-JETB-001", "RUN-JETB-001-a"],
  rationale=[
   "Toy certification lands exactly on the barrier side at all three sizes: sigma_true = 1.0, leakage = 0, sigma_pass/p_m = 1.0, formal-group linearity 0/1745 failures — measured sigma matches the simulable-model prediction exactly (m=2 and m=3 varieties; exhaustive check at p=101: 0/10,201 mismatches).",
   "Independently replicates EXP-JET-001's sigma = 1 (self-contained implementation) — the jet channel carries no information beyond zeroth order.",
   "Controls PASS (S-evaluation == point arithmetic on 49,362 tuples; negative leakage 0 incl. 3,600 uniform pairs).",
   "Per the D1 decision rule this is barrier EVIDENCE (consistency), explicitly not a simulation theorem."],
  limitations=["Toy p in {101,211,431}; consistency evidence, not a proof; the singular-relation branch never exercised (0 in ~59.5k tuples); model formalization lives in analysis.md (research/THM_JETBARRIER1.md outside executor write boundary)."],
  next=["H-JETB-001 = supported_scoped (toy barrier evidence). Write research/THM_JETBARRIER1.md as a theory note formalizing the augmented model + attempting the simulation theorem; the P7 amendment (degree drop on the x1 = x_R fiber is zeroth-order-observable) should be incorporated. Jet-augmented channels (A1-class) are closed pending that theorem."]),
 dict(n=11, ctx="EXP-BKKMV-001 mixed-volume growth-law certificate for the Semaev family (D2, theory-track)",
  decision="supported_scoped", targets=["H-BKKMV-001"], ev=["EV-BKKMV-001", "RUN-BKKMV-001-a", "RUN-BKKMV-001-b", "RUN-BKKMV-001-c", "RUN-BKKMV-001-d", "RUN-BKKMV-001-e", "RUN-BKKMV-001-f"],
  rationale=[
   "Deliverable achieved: exact 3-point-certified growth law MV_m = (m-1)! * 2^((m-1)(m-2)) (m = 3,4,5; zero residual, exact integers, QQ-checked at m <= 4, two-prime support stability).",
   "Barrier side for B2-class methods: MV/Bezout_box = 1.000 exactly at all m (box-saturated after sectioning) — independently confirming EXP-BKK-001.",
   "Versus total-degree Bezout the ratio decays with exact Stirling form (1/2, 2/9, 3/32); log MV/log Bezout = 0.750/0.798/0.829 — a genuine but convention-dependent saving that does NOT change the per-variable driver; recorded with both conventions.",
   "Controls pass incl. BKK cross-check (0 violations in 21 Semaev + 19 same-support cells) and detector-teeth witnesses (N2 fires on positive-dimensional systems).",
   "Saturation dichotomy recorded (rule 8): unsectioned S_m is NOT box-saturated; every single-variable section IS the full box — specialization fills the Newton polytope."],
  limitations=["3-point law (m <= 5); extrapolation risk only; torus-count cross-check has low statistical power (counts <= 4); m = 6/7 not attempted."],
  next=["H-BKKMV-001 = supported_scoped (certificate delivered). Theory-note candidate: prove the sectioned box-saturation theorem and the MV law for all m (publishable complexity-geometry result); no further toy computation needed except m = 6 confirmation if cheap."]),
 dict(n=12, ctx="EXP-INCB-001 incidence-richness ceiling for EC chord arrangements (D3, theory-track)",
  decision="supported_scoped", targets=["H-INCB-001"], ev=["EV-INCB-001", "RUN-INCB-001-b"],
  rationale=[
   "Measured outcome lands on the generic-ceiling (barrier) side: EC richness exponent statistically indistinguishable from random line sets at all fittable cells (z = 0.611/0.441/0.954; one z = 4.079 cell identified in-run as a fit-conditioning artifact — identical EC/random c3 counts of 1.0 vs 1.0).",
   "Promotion gate for the 'excess' opening (z > 3 at all three sizes) is FALSE — the A2-class relation-supply opening is closed at toy scope.",
   "Controls PASS (random null within 0.06–0.69 SE of the exact prediction at all cells; grid positive control separated by 11.3–46 with c3 4.0–80.0 vs 0.0–6.83 — the instrument has sensitivity).",
   "Systematic small deficit recorded (rule 8): EC c3 runs 15–35% below the uniform-x first-moment prediction at all fittable cells (~2 SE, unexplained)."],
  limitations=["Toy p <= 2^12, B <= 28; richness profiles, not worst-case bounds; a proved character-sum ceiling theorem remains open; closes the toy-certification scope."],
  next=["H-INCB-001 = supported_scoped (toy ceiling evidence; the excess-opening reading is rejected_scoped). Theory-note candidate: EC-chord richness ceiling via character sums; investigate the systematic 15–35% c3 deficit only as theory, not as a harvesting channel."]),
 dict(n=13, ctx="EXP-ICI-001 total index-calculus exponent (crossbred/MITM) with uncertainty quantification",
  decision="reject_scoped", targets=["H-ICI-001"], ev=["EV-ICI-001", "RUN-EXP-ICI-001-a", "RUN-EXP-ICI-001-c", "RUN-EXP-ICI-001-d", "RUN-EXP-ICI-001-e", "RUN-EXP-ICI-001-f"],
  rationale=[
   "Falsification condition met numerically: crossbred total 0.891 [0.869, 0.914] (27/27 cells, 216/216 targets, n up to 26) — CI entirely above 0.5; MITM best family total 0.583 (t=12), all families above 0.5.",
   "Exponent drifts UPWARD with ladder extension (0.864 legacy -> 0.891 full), opposite the bend-down hope; extension-arm-only 0.925.",
   "Controls PASS: rho baseline slope 0.498 [0.471, 0.522]; matched-null contrast >= 2^13.2x (instrument is structure-sensitive); same-seed rerun 216/216 identical hashes.",
   "Stacked constants now CI-backed: MITM t=6 gap 2^42.7 at n=256; crossbred loses by 2^100 (CI90 [94.5, 105.7])."],
  limitations=["Toy n <= 26 system sizes; MITM n=28 arm censored (infrastructure, not evidence); wall-clock fit 0.573 reflects superlinear memory effects at toy scale."],
  next=["H-ICI-001 = rejected_scoped. The corpus point estimates (0.863/~0.667) are now CI-backed and extended; no sub-rho IC exponent survives uncertainty quantification."]),
 dict(n=14, ctx="EXP-DREG-001 boolean chained Semaev solving-degree deficit vs the semi-regular null",
  decision="inconclusive", targets=["H-DREG-001"], ev=["EV-DREG-001", "RUN-DREG-001-VALIDATE-N18-A", "RUN-DREG-001-VALIDATE-N15-NULL", "RUN-DREG-001-VALIDATE-N12-NULL"],
  rationale=[
   "Instrument validation COMPLETE and valuable: all five anchors pass bit-identical (deficit series 1,322 / 1,862 / 1,999 at n = 12/15/18; null == sr_pred exactly at n <= 15), determinism + checkpoint-partition + engine cross-validation controls pass; the checkpointable block-m4ri instrument is certified for the past-wall ladder.",
   "The hypothesis itself is UNTOUCHED: no past-wall cell was measured within budget (n=17 sem/null, n=21, n=24 censored per stopping rules — infrastructure, not evidence, rule 5); neither the success nor the falsification clause is evaluable.",
   "Deficit increments decelerate inside the wall (+540, +137) but cannot be extrapolated through a possible phase transition.",
   "Rule-8 observation recorded: sem Macaulay column support covers 84.2/82.2/80.8% of C(nb,<=5) at n=12/15/18, decreasing, while the null covers 100% — a structural signature distinct from the rank deficit."],
  limitations=["Measured cells n <= 18 at/below the old wall; n=17 null cell (review correction C1, sr_pred 126,922) unmeasured; d_ff distribution has only 2 resolved targets at n=12."],
  next=["H-DREG-001 = inconclusive; remains the single highest-value open object. Dispatch EXP-DREG-002: n=17 sem + null full-rank cells (costed ~1,300–2,000 s each, resumable from preserved checkpoints), then n=21 if the deficit law is still ambiguous."]),
 dict(n=15, ctx="EXP-SIG-001 low-degree syzygy family classification + Yokoyama #G* panel",
  decision="inconclusive", targets=["H-SIG-001"], ev=["EV-SIG-001", "RUN-EXP-SIG-001-a", "RUN-EXP-SIG-001-b", "RUN-EXP-SIG-001-c", "RUN-EXP-SIG-001-d"],
  rationale=[
   "Clause (a) 'all extra syzygies rewritable/Koszul' fails numerically: a genuine non-Koszul degree-3 linear syzygy exists at n = 9/15/18 (rankK(D3) = 0), and residual non-rewritable D4 syzygies remain at every size after removing the K-family and all D3 multiples (23, 82, 10, 13).",
   "But the exploitability question — does the non-rewritable component GROW with n — is unresolved: on the two T2-anchored sizes the residual is non-decreasing (10 -> 13) with 1 seed / 2 points; no CI possible.",
   "Clause (b) approximately holds: #G* = 9/15/49 family-independent (ratio 1.02–1.25), no CM/isogeny dependence, no collapse; Betti L1 = 0 vs nulls.",
   "Rule-8 observations: the 8n/3 D4 law fails at n = 9 (deficit 41 != 24; T2 only measured n >= 12); n = 12 seed 1 is a degenerate instance (R_x = 0, 2-torsion target) needing a re-run with a different seed.",
   "Controls PASS (null extra = 0; injected syzygy detected; T2 anchors 8n/3 reproduced exactly at n = 15/18; determinism checks identical)."],
  limitations=["Seed 1 only; D <= 4 only; no t=2 arm; n=12 degeneracy; growth claim rests on 2 points."],
  next=["H-SIG-001 = inconclusive. Dispatch EXP-SIG-002: (i) n = 12 re-run with a non-degenerate seed; (ii) residual non-rewritable D4 count at n in {9,12,15,18,21} with >= 3 seeds per size to resolve the growth question; (iii) extend to D = 5 at n <= 15 if budget allows."]),
 dict(n=16, ctx="EXP-R6-001 explicit-membership PDP on an arbitrary explicit birthday factor base",
  decision="reject_scoped", targets=["H-R6-001"], ev=["EV-R6-001", "RUN-EXP-R6-001-a", "RUN-EXP-R6-001-b", "RUN-EXP-R6-001-c", "RUN-EXP-R6-001-d"],
  rationale=[
   "Falsification condition (i) met: total-cost exponent alpha = 2.074, bootstrap CI90 (1.565, 2.621) — entirely above 0.5 and above the same-instance rho control 0.4988 (0.4813, 0.5161); cost above rho by 2.0e4–1.5e5x at every measured scale.",
   "No-win signature recurs (condition ii): d_reg median flat at 2.0 while cost scales ~l^2.1; nulls cost MORE than real systems (1.3–1.5x) — real systems track the support-matched null.",
   "No bookkeeping leak (condition iii): even solve-only, GB-only/rho = 5.1e3–2.7e4x.",
   "All four mandatory controls present and passing (rho 152/152 exact; curve spread 1.04–1.25; isogenous same-order identical; support-matched null harder).",
   "Sharp solve wall observed between F=18 (28 s) and F=20 (>460 s) — the approach hits its own complexity wall far below the spec ladder."],
  limitations=["valid_reduced_scope: m=3 only (m=4 arm fully censored — even F=6 > 300 s), F <= 16 vs spec's l = 2^20..2^30 ladder; censored cells are infrastructure (rule 5), but the measured exponent CI is entirely above 0.5 with the no-win signature, so the scoped closure stands (rule 6)."],
  next=["H-R6-001 = rejected_scoped. Closes the explicit-membership arbitrary-base direction (AUTOLAB_TASKS T1) at all reachable scales; combined with ICI's CI-backed totals, no explicit-base membership-solve route to sub-rho remains open in the tested regime."]),
]

STATUS = {
 "H-JET-001": "rejected_scoped", "H-INC-001": "rejected_scoped", "H-STR-001": "rejected_scoped",
 "H-NET-001": "rejected_scoped", "H-BKK-001": "rejected_scoped", "H-EQJ-001": "rejected_scoped",
 "H-TRA-001": "rejected_scoped", "H-TTN-001": "rejected_scoped", "H-NCP-001": "rejected_scoped",
 "H-JETB-001": "supported_scoped", "H-BKKMV-001": "supported_scoped", "H-INCB-001": "supported_scoped",
 "H-ICI-001": "rejected_scoped", "H-DREG-001": "inconclusive", "H-SIG-001": "inconclusive",
 "H-R6-001": "rejected_scoped",
}

errors = []
for d in DECISIONS:
    path = LEDGER / f"DEC-20260718-{d['n']:03d}.yaml"
    body = dec_yaml(dict(d, context=d["ctx"], target_ids=d["targets"],
                         evidence_refs=d["ev"], next_actions=d["next"],
                         id=f"DEC-20260718-{d['n']:03d}"))
    if path.exists() and path.read_text() != body:
        errors.append(f"REFUSE overwrite {path.name}")
        continue
    path.write_text(body)

for hid, st in STATUS.items():
    p = LEDGER / f"{hid}.yaml"
    if not p.exists():
        errors.append(f"MISSING {p.name}"); continue
    txt = p.read_text()
    new, cnt = re.subn(r"(?m)^(\s*status:\s*)[a-z_]+", rf"\g<1>{st}", txt, count=1)
    if cnt != 1:
        errors.append(f"NO STATUS LINE {p.name}"); continue
    p.write_text(new)
    print(f"{p.name}: status -> {st}")

if errors:
    print("ERRORS:"); [print(" ", e) for e in errors]; sys.exit(1)
print(f"Wrote {len(DECISIONS)} DEC records.")
