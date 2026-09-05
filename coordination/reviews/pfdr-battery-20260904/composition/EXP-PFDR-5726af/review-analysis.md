# Review analysis — EXP-PFDR-5726af (H-PFDR-4148b8)

Composed under TASK-20260904-e6b4dd from the two committed blinded reports of
review plan TASK-20260904-642cf5:

- validator (blind re-derivation) `coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-642cf5/validation-report.yaml`
- red team `coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-ed0e8f/red-team-report.yaml`

Package under review: ten runs of `experiments/EXP-PFDR-5726af/`, all
`completed_valid`, p ∈ {4099, 65537}, (m, s) cells (2,2)…(2,6), (3,4), (3,5),
plus the H-TOP symbolic run, the H-WIL 112-cell table and a mixed-block nearby
arm.

---

## Observation

**Joint-by-joint verdicts.**

| joint | owner | verdict | deciding fact |
| --- | --- | --- | --- |
| V1 blind re-derivation of (d_ff, fall_dim) and the per-layer profile at the deciding cell | 642cf5 | holds | phase-A implementation from the task card's statement alone (boundary 02:15:12Z, `rederivation.yaml` sha256 `2e96f2dc…`): Semaev arm **12/12 at (5, 4)** with (full, top) = (1,1), (6,2), (15,1) at D = 4,5,6; block-factored nulls 4/4 at (5,4); support-matched nulls 24/24 at d_ff = 6 with fall_dim 14; a supplementary sweep of 40 random curves per prime gives 80/80 at (5,4) |
| V2 run-set validity, schema, pinning, seeds, frozen-prediction binding | 642cf5 | holds | 10/10 `completed_valid`; 60/60 sidecar digests; one run-script hash across ten manifests; 15/15 pinned files identical; `stage0-predictions.yaml` sha256 identical in all ten; both apparent anomalies resolve exactly (m2-s6's differing commit touches only EXP-PFDR-fd901a paths; m3-s5's `dirty_tree.tracked_diff_sha256` reproduces byte for byte as `git diff 3a9c1b02 1b49d491`) |
| V3 instance and certificate checks | 642cf5 | holds | 12/12 non-singular with a,b ≠ 0; 12/12 x_R are window-pair sums with exhibited witnesses; N_sol recomputes 12/12 |
| V4 independent recomputation of the H-WIL table and the S_4 top form | 642cf5 | holds | 112/112 cells at rank min(C(s,j), C(s,j+2)), nothing below maximum, matching sympy on 112/112; S_4 total degree 12, per-variable [4,4,4], 125 monomials, top form the single monomial x_1^4x_2^4x_3^4 with coefficient exactly **1**; plus a negative leg the run did not record (S_4 nonzero 8/8 at random x_R) |
| R0 raw/summary agreement and residual regeneration | ed0e8f | holds | zero recorded-vs-derived mismatches over 272 Semaev layers, 1490 NULL-1 layers, 240 NULL-2 layers, 36 mixed-block objects and 24 non-monomial readings; every table entry of sections B-K reproduces |
| R1 the fall_dim identity and the boundary-cell anomaly | ed0e8f | **BREAKS** | **COUNTEREXAMPLE CERTIFICATE**: m = 2, d = 2, s = 2, p = 13, E: y² = x³ + 12x + 3 (4a³+27b² = 5 ≠ 0), x_R = 11 gives (d_ff, fall_dim) = **(5, 3)** against the frozen (5, 4), with N_sol = 8 and the vanishing linear form a_{1,0} − a_{2,0}; second instance p = 19, a = 2, b = 15, x_R = 9. Both curves pass the experiment's own filter |
| R2 exactness, the Wilson dependence, the scope of the 84cdb7 H1 refutation | ed0e8f | **BREAKS** | (D4)'s stated reason "for p > s every binom(k−i, t−i) is a positive integer below p" is FALSE — witness s = 10, j = 4, e = 2, p = 11 has a diagonal entry 15 ≥ p — while the rank is nevertheless full (210). The conclusion is right for a different reason (Kummer/Lucas); the source proposal IDEA-20260903-e1e38b (D4) had the correct bound (binom(s, ⌊s/2⌋) < 2^s ≤ p) and **the ledger record lost it** |
| R3 H-TOP provenance, the ALPF-011 citation, the CAS substitution | ed0e8f | **BREAKS** | the archived EXP-ALPF-011 column [4,4,4,12] is a **generator-degree list, not a per-variable profile** — decisive because the entry becomes [5,5,5,12] when \|FB\| = 5, and a per-variable profile of S_4 cannot track the factor base. HEUR-001's `random_model_justification` is factually wrong as written. No objection to the sympy substitution for the absent Sage |
| R4 nearby objects, confounds and conventions | ed0e8f | **BREAKS** | a non-tensor top form `ell_1²ell_2² + ell_1³ell_2` with dense sub-top terms has a rank-2 top form, so (D4) does not apply, and still gives d_ff = 5 (fall_dim 2, not 4). **d_ff alone does not identify block structure**; F5's converse reading is too strong |

**Proves-too-much control (ed0e8f).** Absent on the three planned objects and
on the added out-of-regime cell; **present as a partial survival** on one object
the reviewer added deliberately as the inconvenient variant: the non-tensor top
form above reproduces d_ff = 5 while (D4) declines at the tensor step. The
survival localises exactly at "AI_p(S~) = min_k a_0(A_k, ell_k^e)": what
produces d_ff = δ + 1 is the mere existence of SOME degree-1 annihilator of the
top form; being a block tensor is sufficient, not necessary. fall_dim still
separates (2 versus 4), so the mechanism claim survives **if it is carried by
the pair, not by d_ff alone**.

**New positive result produced by the review, not by the run.** H-TOP at m = 4,
declared not attempted in `stage0-htop.md` 2.2, is now checked: deg_{(x1..x4)}
S_5 = 32 and the coefficient of x_1^8x_2^8x_3^8x_4^8 is **1**, in six random
(a, b, x_R), with x_R symbolic, and with a, b symbolic (no free symbols in the
leading coefficient). m ≥ 5 remains an open symbolic obligation.

**Coordinator verification independent of the reports** (round-closure.md
item 2). The orchestrating Coordinator session RAN the reviewer's
`counterexample_certificate.py` and both instances reproduce
(p = 13, a = 12, b = 3, x_R = 11 and p = 19, a = 2, b = 15, x_R = 9; N_sol = 8;
actual (5,3) against predicted (5,4)). **This is reproduction of the reviewer's
implementation, NOT an independent re-derivation**, and it is cited that way
wherever it appears in EV-PFDR-1394a4 and DEC-20260904-1e27a2. The reviewer
itself re-checked the instance by three implementations sharing no code.

**Literal failures, recorded as failures.** Prediction P3 ("the block-factored
null reproduces d_ff AND fall_dim exactly, forced 0 difference at every cell")
is not merely unobserved at the boundary cells (2,2,2) and (3,2,4) — it is
**unsatisfiable** there: a homogeneous block-factored null at s = e is a scalar
times the product of all ms variables, supported at one point of {0,1}^{ms}, so
its fall_dim is 1 for any m, s, p. The gate run records
`P3_null2_minus_semaev_all_zero` FALSE with 60 entries at fall_dim_diff −3, and
`F4_null1_falls_at_semaev_value_any_seed` TRUE, both set honestly by the
producer. The deciding cell s = 3 records P3 true and F4 false.

---

## Comparison

**Against the coordinator prior recorded in TASK-20260904-642cf5 (l.209-251).**

**CONFIRMED on its central expectations, and REFINED — not overturned — on the
one it got structurally right but bounded wrongly.**

| prior expectation | outcome |
| --- | --- |
| blind re-derivation returns (5,4) on all twelve instances with profile (1,1), (6,2), (15,1); every validation joint holds | confirmed exactly, on 12/12 and on an unrequested 80-draw supplementary sweep |
| the red team BREAKS (D4)/(D6)'s "block-factored null reproduces fall_dim exactly at EVERY cell", the discrepancy being the boundary cells s = e where the homogeneous null's fall_dim is 1 | confirmed exactly, including the mechanism (the null collapses to a single monomial supported at one cube point) |
| the red team shows, by adding random sub-top terms, that the discrepancy is **homogeneity, not curve information**, so curve-independence survives for d_ff everywhere and for fall_dim off the boundary | confirmed: the inhomogeneous block-factored null with no curve, no target and no x_R returns (5,4) and (13,12) exactly |
| the ALPF-011 citation mislabel is confirmed, so H-TOP at m = 3 rests on the symbolic check alone | confirmed, with the decisive extra fact that the archived entry TRACKS \|FB\| |
| the sympy resultant is accepted as an exact substitute for the absent Sage | confirmed; "no objection to D-HTOP-CAS" |
| "refuted by derivation" is conditional on Wilson's rank formula for the LOWER bound and tested only at s ≤ 8 | confirmed; the red team adds that no finite s-range can refute a boundedness statement at all |
| the non-monomial nearby object is untested at s = 3 and the red team constructs one that works | confirmed, and the constructed object produced the partial proves-too-much survival |

**REFINED, in the direction the prior did not go far enough.** The prior
expected the fall_dim clause to fail only at the **boundary** cells and only for
the NULL arm. The red team found the identity failing **in the Semaev arm
itself**, at an explicitly exhibited curve and target inside the hypothesis's
own quantifier range, and localised the mechanism exactly: fall_dim(D) =
dim ker(m_{S~_top}) − dim Rel_D with Rel_D = {h of degree D−δ vanishing on
supp(S~)}, and (D4) states the identity **without the hypothesis Rel_D = 0**.
The reviewer also supplied the repair and its rigorous sufficient condition
(N_sol < 2^{ms − a_0}) and verified post hoc that it holds with orders of
magnitude to spare at every tested cell (observed N_sol ∈ {1,2,6} against
thresholds 8, 32, 64, 256, 512, 2^11, 2^14) — and that the bound is **sharp**:
the counterexample sits at N_sol = 8 = 2^{4−1} exactly.

**The prior's expected DECISION is therefore only partly reached.** It expected
"support for H-PFDR-4148b8's closed form and curve-independence of d_ff at the
tested cells, with the fall_dim statement scoped to strict-early-fall cells".
The closed form and curve-independence of d_ff are confirmed and survived every
attack. But the fall_dim statement cannot be scoped merely to strict-early-fall
cells: it is FALSE as universally quantified, on an archived counterexample
certificate, and the repair needs a stated side condition. The decision is
therefore `weaken` and not `support`.

**Reviewer-versus-reviewer.** No disagreement on any shared fact. The two
independently converge on the round's most consequential scope point from
different directions: the validator's curve-free block-factored null reproduces
(5,4) at the deciding cell, and the red team's **inhomogeneous curve-free,
target-free, x_R-free** null reproduces (5,4) and (13,12), as does a dense
random polynomial with no block structure. Both locate the anomaly in
homogeneity rather than curve structure. Neither read the other.

---

## Inference

**What survives, scoped to d = 2, (m, s) ∈ {(2,2),(2,3),(2,4),(2,5),(2,6),
(3,4),(3,5)}, p ∈ {4099, 65537}, 3 curves × 2 targets (2 targets at m = 3), the
per-layer meter convention:**

1. **The closed form for the first fall degree is confirmed and survived every
   attack this round could mount, including an exhaustive small-prime sweep.**
   d_ff = m·2^{m-1} + ⌊(s − 2^{m-1})/2⌋ + 1 = 5, 5, 6, 6, 7, 13, 13 across the
   seven cells, identical across every curve, target and prime, strictly below
   the measured support-matched null at the five cells where a strict early fall
   is possible, and reproduced exactly by a curve-free block-factored null. The
   deciding cell was re-derived **blind** at (5,4) on 12/12 instances by an
   implementation that had read nothing of the producer's.
2. **H-TOP is now checked at m = 4**, by the review rather than by the run:
   deg S_5 = 32 in the four unknowns with leading coefficient exactly 1,
   constant in x_R and in (a, b). Together with m = 2 (by hand), m = 3 (the
   package's symbolic run plus the reviewer's independent reproduction), H-TOP
   holds at m = 2, 3, 4. **m ≥ 5 is open** and is recorded as KN-OPEN-02200b.
3. **The H-WIL exactness statement is verified unconditionally at e = 2 for
   s ≤ 8 by the package and s ≤ 10 by the review, and at e = 4 for s ≤ 10 by
   the review**, at the tested primes with p > s, and is conditional on Wilson's
   rank theorem beyond. The p-sweep the review added shows the control has real
   dynamic range: 79 rank drops at e = 2 and 32 at e = 4, **all at p ≤ s, none
   at p > s**.
4. **The identity d_lf-side mechanism is real but must be carried by the PAIR.**
   d_ff = 5 is reachable by a non-tensor top form; fall_dim still separates
   (2 versus 4). Any mechanism claim must be carried by (d_ff, fall_dim) or by
   the kernel dimension, never by d_ff alone.

**What falls, stated at full strength.**

5. **The fall_dim clause of (D4), as universally quantified, is FALSE, and the
   refutation is a counterexample certificate — the strongest artifact tier in
   `docs/claims-and-verification.md`.** p = 13, y² = x³ + 12x + 3, x_R = 11,
   s = 2 gives (5,3) against the frozen (5,4). The cause is exact: S~ vanishes
   on the 8 digit vectors with a_{1,0} ≠ a_{2,0}, so the linear form
   a_{1,0} − a_{2,0} kills every row and full_rank drops from 4 to 3. Re-checked
   by three implementations sharing no code, packaged as a self-contained
   60-line verifier that prints PASS, and reproduced by the orchestrating
   Coordinator session. The repaired statement — "fall_dim(d_ff) = m[C(s,a_0) −
   C(s,a_0+e)] whenever no nonzero squarefree form of degree a_0 vanishes on
   supp(S~); a sufficient condition is N_sol < 2^{ms − a_0}" — is true at every
   draw in the package.
6. **(D6)/P3's "forced 0 at every cell" is unsatisfiable at the two boundary
   cells**, and those two cells carry **zero dynamic range** on the mechanism
   question: at s = 2^{m-1}, δ = n = ms, so A_δ is one-dimensional and
   A_{δ+1} = 0, giving top_rank = 0 and d_ff = n + 1 for EVERY generator of
   degree δ. The measured agreement there is degree exhaustion, not a degree
   fall. Two of the seven cells in the residual table are instrument checks, not
   evidence.
7. **"Refuted by derivation" and "closed at d = 2" are over-stated as written.**
   Refuting IDEA-20260830-84cdb7's H1 (boundedness in s) needs the LOWER bound
   only, hence Wilson only, so the s ≤ 8 direct check contributes **no
   unconditional refutation** — no finite s-range can refute a boundedness
   statement. The unconditional content is exactly "d_ff takes the values
   5,5,6,6,7 at s = 2..6, m = 2, two primes".
8. **(D7)'s literal σ ≥ 1 is wrong for every m ≥ 3.** The recomputed bound
   σ ≥ ω·m·H(1/(2m))/(m−1) is 1.623 (m 2), 0.975 (m 3), 0.725 (m 4), 0.586
   (m 5), 0.497 (m 6), 0.433 (m 7), 0.318 (m 10) at ω = 1, falling below
   IDEA-20260808-812554's admission threshold 1 − 2/(m−1) from m = 6 upward. The
   CONCLUSION survives for a reason the record does not give: 2^s ≤ p caps s and
   s ≥ 2^{m-1} caps m (≤ 9 at s = 256, ≤ 7 at s = 64), and at those finite points
   the exact column count gives σ ≥ 1.015 (3,256), 0.901 (4,128), 0.818 (4,256),
   0.779 (5,256), 0.859 (6,256), 1.031 (7,256), 1.125 (9,256). **The closure
   does not reach m ≥ 10 at 256-bit p, where the presentation is in the
   hypothesis's own excluded regime — and 812554's table says large m is exactly
   where the admission threshold is loosest.** The closure is weakest where the
   stake is most attractive; that belongs in the forward guidance.
9. **Two citation defects are confirmed and are corrections owed, not opinions.**
   HEUR-001's `random_model_justification` rests on a misread archived column;
   (D4)'s exactness justification is false as written and needs the Kummer/Lucas
   argument or the proposal's own 2^s ≤ p bound restored.

**SCOPE, stated plainly because a reader can get it wrong.** The block-factored
null — a curve-free, target-free, x_R-free object — reproduces the Semaev arm's
(d_ff, fall_dim) exactly at the deciding cell and at (3,2,5), and a dense random
polynomial with no block structure reproduces the boundary-cell values.
**Nothing measured here is a statement about summation polynomials, elliptic
curves or the ECDLP.** The observable is a property of the block-tensor
structure of the digit presentation. Any downstream sentence of the form "the
Semaev system at (2,2,3) behaves thus" must read "any generator with this
block-tensor top form behaves thus".

---

## Limitation

1. **A first fall degree is not a solving degree, not a cost, and not an
   exponent.** Nothing on any attack axis moves. Pollard rho is unchallenged
   and unapproached by anything in this package.
2. **Toy scale throughout.** p ∈ {4099, 65537}, ≤ 64 columns at the deciding
   cell, s ≤ 8 (s ≤ 10 in the review) for H-WIL, m ∈ {2,3}. No transfer to
   cryptographic s is claimed and none is available.
3. **The declared 12 instances are 11 distinct instances.** At p = 65537, curve
   seed 1103, target seeds 1 and 2 both give x_R = 47685; two further draws
   (p = 65537, curve 1102) certify only through a doubling P + P and have
   N_sol = 1. The deciding cell replicates over **11 distinct instances on 6
   curves**, not 12.
4. **The validator could not check the seed → (a, b, x_R) derivation**:
   `run_pfdr_5726af.py` is `blind_from`. Every checkable consequence is
   consistent (genuine non-singular curves, genuine window-pair sums, N_sol
   matching draw for draw, the s = 2 generator matching the printed one term by
   term), but the derivation itself was not re-executed.
5. **The per-layer profile at the deciding cell has no recorded counterpart.**
   The manifests expose only d_ff and fall_dim there; the validator's
   (1,1), (6,2), (15,1) stands as an independent value confirmed against R0's
   regeneration from the raw records, which is a different reviewer's joint.
6. **`stage0-predictions.yaml` was first committed WITH the run package**, so
   its own `written_before_any_official_rank: true` is self-attested. The
   binding evidence is the contract commit c5742969 (2026-09-03T19:42:47Z),
   byte-identical at HEAD, 52 minutes before the first run. The file also
   discloses a pre-registration scratch benchmark that printed rank profiles at
   m = 2, s ∈ {3,4,5,6}, p = 4099 on an ad-hoc curve before it was written —
   disclosed by the producer and neutralised by the earlier contract commit.
7. **The Wilson source was not opened.** Two WebSearch queries and two WebFetch
   attempts failed (HTTP 403 / PDF extraction unavailable). Exactness beyond
   s ≤ 10 rests on a classical theorem cited at snippet level.
8. **The exception's existence at a strict-early-fall cell is undetermined.**
   The row-collapse counterexample was found twice at (2,2,2) and never in
   26,000 exhaustive instances at (2,2,3). Whether the repaired (D4) needs its
   N_sol side condition only at s = 2^{m-1} or everywhere is **open** and is
   recorded as KN-OPEN-2e7514.
9. **A contract wording inconsistency, harmless at m = 2**: D_null is written
   ⌊(ms + me)/2⌋ + 1 in the frozen prediction file and ⌊(ms + 2m)/2⌋ + 1 in
   CTRL-CONFOUNDERS-NAMED. They agree at m = 2 and disagree at m = 3 (13 vs 10).
   Every recorded D_null follows the first form, so no scored comparison moves.
   Separately, the printed `D_null_84cdb7` column at (3,2,4) and (3,2,5) (9 and
   11) is the null of a system that does not exist and must be dropped or
   annotated; it was never scored.
10. **This composition ran no code.** The Coordinator subagent has no shell. The
    counterexample reproduction cited above was performed by the orchestrating
    session and is reproduction of the reviewer's implementation, not an
    independent re-derivation.
11. **Two corrections are owed and are NOT made here** (records are immutable):
    an annotation of H-PFDR-4148b8 (D4) carrying the row-independence side
    condition and the Kummer/Lucas exactness argument, and an annotation of
    HEUR-001's `supporting_results` recording that the EXP-ALPF-011 archive
    supports only "total degree 12" and that m = 3 rests on the symbolic run.
    Both are named in DEC-20260904-1e27a2's `next_actions`.
