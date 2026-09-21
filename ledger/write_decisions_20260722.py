#!/usr/bin/env python3
"""Coordinator decisions for the 2026-07-22 next-batch evidence."""
import json, re, sys
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
    L += ["  decided_by: coordinator", '  decided_at: "2026-07-22"']
    return "\n".join(L) + "\n"

DECS = [
 dict(id="DEC-20260722-001",
  context="EXP-SIG-005 cascade-law falsifiable checks: n=24 residual prediction + D=6 birth-law attempt",
  decision="supported_scoped", targets=["H-SIG-001"],
  ev=["EV-SIG-005", "RUN-EXP-SIG-005-b", "RUN-EXP-SIG-005-c", "RUN-EXP-SIG-005-d", "RUN-EXP-SIG-005-e",
      "RUN-EXP-SIG-005-h", "RUN-EXP-SIG-005-j", "RUN-EXP-SIG-005-k", "RUN-EXP-SIG-005-m"],
  rationale=[
   "Falsifiable prediction CONFIRMED: D4 residual = 17 at n = 24 (both instruments, delta 0, 3 seeds, nulls all-zero, determinism) — the canonical series is exactly 2n/3+1 across SIX on-lattice sizes (9/11/13/15/17 at n = 12..24); linear growth in n.",
   "Boundary of the cascade now measured: the D5-born component residual_5 is NON-MONOTONE in n (344/878/1158/974 at n = 9/12/15/18; the n = 18 drop replicated on two seeds with zero variance) — the cascade's n-growth is weak (linear at D4, non-monotone at D5).",
   "Cross-instrument validation: SIG D5 Macaulay deficit == EXP-DREG block-m4ri deficit exactly at every shared n (1321/1322, 1862, 1999); on-lattice D5 deficit series 909/1322/1862/1999 is monotone but sharply decelerating (+413/+540/+137).",
   "D=6 axis INVALIDATED BY ITS OWN CONTROL (the harness working): the support-matched null breaks at D6 (ncols mismatch 31,180 vs 29,332; null overshoots sr_pred by 3,111; null extra/residual != 0) — sr_pred is miscalibrated at D6, so no D6 non-rewritability/deficit/birth-law quantity is admissible. This is the 'miscalibrated D6 null' pre-excluded in H-DREG-001, now directly demonstrated.",
   "Net: the cascade is real and confirmed through D = 5 with a linear D4 law, but its n-growth is weaker than the initial monotone picture suggested and its degree-axis continuation is currently unmeasurable — exploitability hopes are correspondingly tempered."],
  limitations=["Toy scale, m = 3, t = 3; residual_5 measured only to n = 18 (n = 21 ENOSPC-censored, not evidence); D6 baseline invalid pending re-derivation; d_reg(sem) < d_reg(null) remains unevaluable (fixed-degree proxies only)."],
  next=["H-SIG-001 remains supported_scoped with the sharpened, bounded picture above. Before ANY D6 claim: re-derive the D6 null baseline (equal-ncols support matching + sr_pred recalibration). Measure n = 21 residual_5 when disk pressure allows (tests whether 974 is decline onset or lattice fluctuation). Theory note: why the null breaks exactly at D6."]),
 dict(id="DEC-20260722-002",
  context="EXP-TTN-002 m = 6 bond-rank certificate for the TTN rank law",
  decision="supported_scoped", targets=["H-TTN-001"],
  ev=["EV-TTN-002", "RUN-TTN-002-c"],
  rationale=[
   "Certificate delivered: root/mechanism bond rank chi(6) = 45 = C(2^{6-3}+2, 2) EXACTLY on all 9 cells (p x 3 seeds), proved <= 45 by the Sylvester-multiset construction and certified = 45 by full-rank factors + rank-45 minor — the rank law is now a 4-point exact law (3, 6, 15, 45 at d = 2, 4, 8, 16).",
   "Grandchild split 4|2 also 45 (full Semaev symmetry); single-var bond full (17).",
   "New structural phenomenon recorded (rule 8): a universal degree-4 syzygy among S_4's five X-coefficient polynomials (identical witness vector across independent samples and both recursion sides, all 9 cells) drives the child bond 70 -> 69 -> 68 — invisible at m <= 5, mechanism open.",
   "Growth slope update: 4-point 1.3043, m5->m6 1.5850 — the trend toward asymptotic exponent 2 (the disproof direction for the attack) continues; H-TTN-001's rejection is hardened, not altered.",
   "Controls 9/9 pass incl. comb == balanced (recursion-associativity identity, 0/9x2048 mismatches) and comb == formal nested resultants; defect chain (int64 overflow, degree-drop padding) resolved across runs -a/-b/-c with identical measurements."],
  limitations=["Toy p <= 2^10, one curve family per cell; slopes from 4 points; child-bond law (68 vs 70 vs 45) not yet a theorem; dense symbolic S_6 probe censored (infrastructure)."],
  next=["H-TTN-001 remains rejected_scoped; the rank-law certificate is archived as negative-theory (full-rank-exponent trajectory toward 2). Theory-note candidate: the universal S_4 X-coefficient syzygy (explains 68; would complete the bond-rank law for all splits). No further attack-side work."]),
 dict(id="DEC-20260722-003",
  context="EXP-BKKMV-002 m = 6 MV certificate + THM_BKKMV1 theory note (box-saturation theorem)",
  decision="supported", targets=["H-BKKMV-001", "H-BKK-001"],
  ev=["EV-BKKMV-002", "RUN-BKKMV-002-a", "RUN-BKKMV-002-b", "RUN-BKKMV-002-c", "RUN-BKKMV-002-d",
      "research/THM_BKKMV1.md", "research/verification/thm_bkkmv1_verify_results_34.json",
      "research/verification/thm_bkkmv1_verify_m5.sage"],
  rationale=[
   "MV law now PROVED at m <= 5 and CERTIFIED at m = 6: THM_BKKMV1 proves the sectioned box-saturation theorem at m = 3 (13 cells), m = 4 (symbolic over QQ(a,b), 439 cells), m = 5 (explicit QQ instances + specialization monotonicity), and proves the reduction saturation ==> MV_m = (m-1)!*2^((m-1)(m-2)) = box Bezout for ALL m; EXP-BKKMV-002 then confirms MV_6 = 125,829,120 exactly on 6/6 instances (4-point certificate; MV/Bezout_box = 1.0).",
   "The diagonal corner x_1^D...x_{m-1}^D having coefficient exactly 1 in every section is PROVED for any curve, any char != 2 — explaining EXP-BKK-001's 54/54 diagonal presence as a theorem.",
   "Consequence for the attack side: the B2-class sparse-elimination barrier is now theorem-backed at m <= 5 (MV = box Bezout exactly), upgrading H-BKK-001's scoped rejection; the all-m law is reduced to one explicit OPEN GAP (the interior-fiber non-cancellation lemma, with a documented (a,b)-grading route).",
   "New proved micro-structure with falsifiable content: t = 0 sections at even m are NEVER saturated (u_m has X | u_m for even m; self-verified at m = 4: 37/125 cells lost) — exceptional sections are materially non-saturated.",
   "Two-prime hull stability + QQ checks pass; BKK cross-check on real systems passes; fiberwise instrument certified 12/12 vs symbolic ground truth before use."],
  limitations=["Saturation is a hull statement at finite p (2/30 m = 6 sections lost 30-60 hull-INTERIOR monomials, corners intact, MV unchanged; literal support saturation is char-0/generic-t); m = 5 generic support SIZE 54,777 is instance-confirmed, not symbolic; the all-m MV law remains CONJECTURE C1 pending the one named lemma."],
  next=["H-BKKMV-001 = supported (theorem at m <= 5 + m = 6 certificate). H-BKK-001's rejected_scoped now rests on a proved barrier at m <= 5. Remaining theory work (single targeted lemma): the interior-fiber non-cancellation lemma via the (a,b)-grading separation route; the u_m factorization law (u_3^3 | u_5 exactly) is a second open micro-conjecture. No new experiments."]),
 dict(id="DEC-20260722-004",
  context="THM_JETBARRIER1 theory note: simulation theorem for the jet-augmented generic group",
  decision="supported", targets=["H-JETB-001", "H-JET-001"],
  ev=["research/THM_JETBARRIER1.md", "research/verification/thm_jetbarrier1_check.out.json", "EV-JETB-001", "EV-JET-001"],
  rationale=[
   "The D1 barrier is now THEOREM, not toy evidence: T4 (simulation theorem) PROVED — every order-r jet/dual-number query on a public-equation variety is simulable from public zeroth-order data with ZERO group-oracle overhead and exactly preserved success probabilities; Shoup's Omega(sqrt(l)) lower bound and the exponent-1/2 barrier lift verbatim to the jet-augmented model.",
   "Consequence: all A1-class (tangent-screen / dual-number) channels are closed IN-MODEL BY PROOF — upgrading both the H-JET-001 scoped rejection and the H-JETB-001 toy barrier evidence to model-level closure.",
   "P7 amendment upgraded to exact algebra (L5): the x1 = x_R fiber degree drop is the doubling fiber, zeroth-order-observable; the measured 2/p and rate-1 regimes are exact zeroth-order arithmetic.",
   "The theorem's seam is sharp (T6 PROVED): extending the model with coordinate data of composite (non-public) elements collapses genericity; no intermediate well-defined-but-non-simulable jet model exists in the encoding-independent class.",
   "Verification: 9/9 checks PASS; the EV-JETB-001 'singular branch' confound resolved (C1: tested varieties generically smooth, PROVED for m = 2, 3)."],
  limitations=["In-model closure: the barrier holds for the formalized model J(E, FB, r); maximality of the simulable class (C2) and Weil-restriction/descent scope (G2) remain open conjectures/gaps, stated precisely in the note."],
  next=["H-JETB-001 = supported (theorem delivered); H-JET-001 remains rejected_scoped, now proof-backed. The jet/dual-number direction needs no further experiments; any revival must name an operation OUTSIDE the simulable class (the note's seam) with a mechanism."]),
 dict(id="DEC-20260722-005",
  context="THM_COMMUTATOR_KERNEL1 theory note: kernel theorem for prime-field translation quivers",
  decision="supported", targets=["H-NCP-001"],
  ev=["research/THM_COMMUTATOR_KERNEL1.md", "research/verification/commutator_kernel1_check_results.json", "EV-NCP-001"],
  rationale=[
   "The C3 disproof track is delivered as a THEOREM (T1-T2 PROVED): for the single-vertex translation/negation quiver of a prime-field cyclic group, the evaluation kernel is the normal closure of commutators, the forced dihedral torsion (nu^2 = 1, (nu t_i)^2 = 1), and the commutative subset-sum relation lattice L — every word-level relation descends to a signed-subset-sum relation of no larger l1 weight, at any word degree, B, factor base, or n.",
   "Precision bonus: the UNQUALIFIED claim 'kernel = commutator ideal' is PROVED FALSE (nu^2 - 1 is an explicit counterexample); the clean unqualified form holds for the translations-only subquiver — the note pins the exact truth.",
   "Corollary 2 (PROVED + numerically verified) exactly reproduces EXP-NCP-001's measured strict inclusion (p = 431, B = 4, n = 439: 350/439 vs 437/439) as boundary-shell pruning of a truncated ball — measurement and theorem agree quantitatively.",
   "Structural reason identified: no non-affine arrows exist within endomorphisms of a cyclic group — which is WHY prime-field quivers collapse. The noncommutative-correspondence direction for prime fields is closed BY PROOF."],
  limitations=["Single-vertex prime-field quivers only; Frobenius-augmented quivers over extension fields are CONJECTURE (skew-group-ring route, two named missing steps); the search-COST layer (complexity-level simulation) is an open gap; multi-vertex isogeny-graph groupoids open."],
  next=["H-NCP-001's rejected_scoped is now proof-backed; the direction is closed for prime fields by theorem. No further work unless the Frobenius-augmented conjecture is deliberately pursued (extension-field scope, explicitly out of the generic prime-field program)."]),
 dict(id="DEC-20260722-006",
  context="THM_INCBARRIER1 theory note: EC-chord richness ceiling proved in the uniform-x model",
  decision="supported", targets=["H-INCB-001", "H-INC-001"],
  ev=["research/THM_INCBARRIER1.md", "research/verification/thm_incbarrier1_check_output.json", "EV-INCB-001"],
  rationale=[
   "The D3 ceiling is now THEOREM in the uniform-x model (= the experiment's exact sampling model): no chord line is ever >= 4-rich (Bezout); exact full-group triple count T3^full = (n^2 - 6n + 5 + 3z + 2t)/6 proved by inclusion-exclusion; E[T3] with exact closed variance gives the phase diagram — B = p^alpha with alpha < 1/3 implies T3 = 0 w.h.p., alpha in (1/3, 1/2) implies I_EC = I_generic + o-term (the generic ceiling).",
   "The recorded 15-35% c3 'deficit' is EXPLAINED and de-mystified: the pair-density heuristic provably overstates the exact mean by 1 + 3/B (measured 1.10-1.43); it is not a character-sum signal, and provable error scales exceed any such signal by 10^2-10^4 at these sizes.",
   "Two-sided sharpness PROVED: group-AP factor bases do hit excess richness (T3 = 2 floor((B-1)^2/4) exactly, 3/4 of the proved worst-case bound) — but the excess trivializes via rank defect, so no harvesting channel results.",
   "Verification: 231 checks, 0 failures; the note also corrects an imprecision in EV-INCB-001's phrasing ('below at ALL fittable cells' — the (4099,16) cell sits at 1.023x) per rule 9/10 record discipline.",
   "Consequence: A2-class relation-supply closure is now theorem-backed in the uniform-x model, upgrading the H-INC-001/H-INCB-001 toy measurements."],
  limitations=["Uniform-x sampling model; fixed/adversarial-F certification at B = p^alpha, alpha <= 1/2 is blocked exactly at cross-character cancellation (direct Weil certifies only B = Omega(p); published bilinear ranges still miss harvesting by ~p^{1/10}); Poisson limit at alpha = 1/3 and interval-type F remain conjectures."],
  next=["H-INCB-001 = supported (theorem in the uniform-x model); H-INC-001's rejection now proof-backed in that model. The remaining frontier is a named barrier problem (cross-character cancellation at alpha <= 1/2), not an experiment; no further incidence work unless that barrier is attacked theoretically."]),
]

STATUS = {"H-JETB-001": "supported", "H-BKKMV-001": "supported", "H-INCB-001": "supported"}

for d in DECS:
    p = LEDGER / f"{d['id']}.yaml"
    body = dec_yaml(d)
    if p.exists() and p.read_text() != body:
        print("REFUSE overwrite", p.name); sys.exit(1)
    p.write_text(body)
    print("wrote", p.name)

for hid, st in STATUS.items():
    p = LEDGER / f"{hid}.yaml"
    txt = p.read_text()
    new, cnt = re.subn(r"(?m)^(\s*status:\s*)[a-z_]+", rf"\g<1>{st}", txt, count=1)
    assert cnt == 1, f"no status line in {p.name}"
    p.write_text(new)
    print(f"{p.name}: status -> {st}")
