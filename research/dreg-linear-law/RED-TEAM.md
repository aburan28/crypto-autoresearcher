# Red-Team challenge — "boolean Semaev t=3 d_reg is linear; n=9 D6 is a d_reg degeneracy"

Reviewer: independent Red Team session (2026-07-20). Reviewed the working-tree
artifacts on branch `claude/dreg-linear-law`
(`research/dreg-linear-law/FINDING.md`, `dreg_results.json`, `dreg_growth_law.py`,
`validate_dreg.sage`, `diag_per_degree.sage`) against the committed instrument
`experiments/EXP-SIG-005/src/h013_f5_signatures.sage`, the run receipts
`RUN-EXP-SIG-005-h/-k`, and the ledger records `H-DREG-001.yaml` and
`DEC-20260720-002.yaml`. Note: these finding artifacts are NOT a
Coordinator-committed snapshot; per the Red Team contract this review is advisory
and is not a durable research artifact until archived by the Coordinator.

## What reproduced (sound as scoped)

- **Claim 1 (family):** independently confirmed at n=6: nb=2n boolean vars,
  n deg-2 + n deg-3 eqs (n=6 -> nb=12, 6 quadratics + 6 cubics). Receipts show
  nrows 45324 at n=9 D6. OK.
- **Claim 2 (series):** the ascending in-place recurrence realizes
  A(z)=(1+z)^{2n}/[(1+z^2)^n(1+z^3)^n]. sr_pred=28068 at n=9 D6 present in BOTH
  receipts; sr_pred at n=6 (D3=84, D5=1323) reproduced in my Sage run. OK.
- **Claim 3 (linear d_reg, c*~0.238):** re-ran `dreg_growth_law.py`. Values match
  `dreg_results.json` bit-for-bit (n=6->5 ... 8000->1929); marginal slope over
  [4000,8000] = 0.239; d_reg/n decreasing 0.83 -> 0.241 (still above the limit).
  This is a correct statement about the **semi-regular** model: for a semi-regular
  sequence with a fixed equation/variable ratio (here m/nb = 1), d_reg = Theta(n)
  is textbook (Bardet-Faugere-Salvy). No regime change; the closed form is exact.
  SOUND — **as a statement about the generic/null system only.**
- **Claim 4 (mechanism):** the n=9 D6 null C5 failure IS explained by
  d_reg(9)=6: at D=d_reg the null reaches full rank and the pre-collapse sr_pred
  formula is meaningless, so it under-shoots. My n=6 run corroborates the
  mechanism (null collapses to q=1 exactly at D=5=d_reg(6); sr_pred=1323
  under-shoots the actual full rank 1584). The reinterpretation of the calibration
  failure is plausible and well-supported.

Receipt attribution checks out: 29332/28068/27292 live in RUN-h (sem);
31180/28068/31179 live in RUN-k (null). "Bit-for-bit" is honest.

## The weakest claim — Claim 5 — FAILS

**Claim 5:** "d_reg(sem) > d_reg(null), Semaev structure RAISES the solving degree,
contradicting H-DREG-001's support clause," evidenced by "at D=d_reg(null) the
null quotient is 1 while the sem quotient is still 95 (n=6) / 2040 (n=9)."

This inference is invalid on four independent grounds, and it is the claim the
finding advertises as novel and as a **contradiction of established evidence**
(H-DREG-001), so it is exactly the claim that must survive scrutiny.

1. **It is the quantity the hypothesis already ruled out.** H-DREG-001 line 60-61
   states verbatim: *"Subset-column ranks are instrumentation artifacts for sem
   (finding iv) and are never evidence."* The finding's q_sem vs q_null comparison
   is taken across DIFFERENT column supports (n=9 D6: sem ncols 29332 < null ncols
   31180; n=6 D5: 1457 < 1585) — precisely a subset-column-rank comparison. The
   finding inverts a pre-declared artifact into a conclusion.

2. **The Coordinator's Validator already rejected this exact move.**
   DEC-20260720-002 check 4: "the deficit is at a FIXED degree ... both arms are
   below full row rank, so d_reg is NOT reached and d_reg(sem) < d_reg(null) is
   NOT evaluable from any current cell." At n=9 D6 the NULL has collapsed but the
   SEM has not; reaching d_reg on one arm tells you nothing about the other arm's
   collapse degree. The finding reads a d_reg inequality off a single degree where
   only one arm has collapsed — the non-evaluable configuration.

3. **sr_pred is meaningless at D=d_reg — by the finding's OWN argument.** The
   finding's Claim 4 correctly argues sr_pred is invalid at D >= d_reg. But n=9
   D6 IS d_reg(9)=6, so the deficit/quotient the finding cites for the sem arm at
   that cell is in the degenerate regime for BOTH arms. H-DREG-001's actual metric
   is deficit at D <= 6 with D < d_reg; a d_reg-comparison claim cannot be built
   on the one cell where the baseline collapses.

4. **The sem quotient is COLLAPSING, not stuck.** I drove the sem arm at n=6 past
   the null's collapse degree (my run, `/Volumes/Volume/sage-scratch-diag/rt_n6_deep.sage`):

   | D | sem q=ncols-rank | sem deficit | null q |
   |---|---|---|---|
   | 4 | 171 | **+76** | 243 |
   | 5 | 95 | -39 | 1 |
   | 6 | 51 | -150 | 0 |
   | 7 | 24 | -222 | 0 |
   | 8 | **9** | -252 | 0 |

   q_sem descends monotonically 171 -> 95 -> 51 -> 24 -> 9, heading to a small
   solution count over the sem system's own (smaller) support. "q_sem=95 at
   D=d_reg(null)" is a point on a descent, not evidence of a higher collapse
   degree. Note also the sem **deficit is +76 at D4** — a rank deficit BELOW
   d_reg=5, i.e., the extra-syzygy / degree-fall signature. That is H-DREG-001's
   OWN predicted mechanism (the O(n) low-degree syzygy family, "8n/3 at D4"),
   pointing toward d_reg(sem) < d_reg(null) — the OPPOSITE of Claim 5.

Net: Claim 5 is unsupported, and the raw signature it overlooks (D4 fall +
monotone q descent) trends the other way. The honest status is the one the
Coordinator already recorded: **d_reg(sem) vs d_reg(null) is not evaluated in
either direction** by a fixed-degree corank. The finding does not resolve it; it
re-derives the non-evaluability and mislabels it as a resolution.

## Claim 6 — cost consequence — UNSOUND AS APPLIED

The arithmetic is fine (monomials <= 0.24n over 2n vars ~ 2^{1.06n}; LA cost
2^{(2.1..2.5)n}). The defect is the premise: it uses the **semi-regular** d_reg as
the **true** Semaev solving degree. The entire basis of Groebner index calculus on
Weil-descent / Semaev systems (first-fall-degree assumption; Petit-Quisquater
2012, Faugere-Gaudry-Huot-Renault, Semaev) is that the structured system solves
FAR BELOW the semi-regular degree. The finding measures a first-fall signal (sem
deficit +76 at D4, below d_reg) and then asserts the true degree is >= semi-regular
anyway. So "2^{Theta(n)} >> rho, no sub-rho signal on the degree axis" is a bound
on a **generic** system of this shape, not on the true Semaev system. The correct,
narrow conclusion is DEC-20260720-002's: **the true degree axis is unmeasured past
D=5**; this finding does not change that.

## Baseline comparison

- **Pollard-rho / BSGS:** 2^{n/2} on an n-bit binary-field curve. Correct as the
  bar. The finding beats it only under the (unproven) identity
  d_reg(sem) = d_reg(null,semi-regular). If the true (first-fall) sem degree is
  sub-linear, rho is NOT necessarily safe on the degree axis — which is the open
  question, not a settled negative.
- **Closest specialized baseline (the right one):** first-fall-degree Groebner
  index calculus for Semaev/Weil-descent, whose defining claim is
  d_solve << d_reg,semi-regular. The finding's cost model silently assumes this
  baseline is wrong (d_solve = d_reg,semi-regular) without measuring d_ff for the
  sem arm — H-DREG-001's second metric (gap(n)=d_reg-d_ff) is exactly this and is
  untouched here.

## Probes requested by the task

- **(a) Is q_sem>q_null read correctly?** No. Different column supports (H-DREG-001
  line 60 "artifact, never evidence"), one-arm-collapsed non-evaluability
  (Validator check 4), and a degenerate D=d_reg cell for the sem deficit. The
  sem system is a **solving instance** (`build_boolean_semaev` plugs in a
  decomposable target R[0]); its quotient tends to the solution count, not to 1,
  and it is observed descending (171->9). Reading "still 95" as "harder" is wrong.
- **(b) Is the linear extrapolation sound?** Yes for the **semi-regular** d_reg
  (reproduced; no regime change). Unsound as a proxy for the true sem solving
  degree — that is the load-bearing, unjustified step.
- **(c) Hidden assumption permitting sub-linear d_reg?** Yes: the first-fall
  degree. The finding's own D4 deficit is direct evidence of sub-d_reg degree
  falls; it assumes (without proof) sem >= semi-regular.
- **(d) Scope honesty?** Mostly honest (toy scale, t=3 binary Weil-descent as a
  negative control, no crypto/prime claim, no break). Two overreaches: (i) "no
  sub-rho signal on the degree axis" generalizes a null/semi-regular result to the
  true system; (ii) "no D6 repair needed / prerequisite discharged conceptually"
  edges into reversing DEC-20260720-002, a Coordinator-only action. Even granting
  Claim 4, the instrument still silently emits a meaningless sr_pred at D>=d_reg
  and fails its own C5 control with no guard — a D<d_reg guard is a (small) code
  change, so "no repair needed" is too strong.

## Cheapest decisive falsification of Claim 5 / 6

Drive the **sem arm** at n=6 (fast; nb=12, full space at D8 is 3797 cols) to
its own collapse and read where q_sem stabilizes = the F2 solution count s of the
decomposable-R instance. My partial run already shows q_sem = 9 at D8 and still
falling. Complete it (D8->D9) plus a direct variety solve to pin s; if q_sem
settles at a small s by D <= d_reg(null), then d_reg(sem) <= d_reg(null) and
Claim 5 is falsified. This is minutes of compute and needs no instrument repair.
The properly comparable d_reg test (both arms to collapse at a common small n,
plus gap(n)=d_reg-d_ff, H-DREG-001's own metric) is the only route to a real
d_reg(sem) datum; a single-degree corank is not.

## Narrowest supported statement

Claims 1-4 (family, series, semi-regular linearity, and the mechanism explaining
the n=9 D6 null calibration failure as a d_reg=6 degeneracy) reproduce and are
sound as scoped. Claim 5 (Semaev structure RAISES d_reg / contradicts H-DREG-001)
is NOT supported: it rests on a subset-column corank the hypothesis pre-labels an
artifact, at a single degree where only the null has collapsed and sr_pred is
degenerate, and the sem arm's own signature (D4 deficit +76; q descending 171->9)
trends toward the opposite conclusion. Claim 6's cost verdict is valid only for a
generic system of this shape; the true Semaev degree axis remains unmeasured past
D=5, exactly as DEC-20260720-002 records. No status change is warranted, and the
DEC-20260720-002 prerequisite is not discharged by this finding.
