# TASK-20261029-11526b: J3b scope and wording (EXP-PFDR-bb0d26, H-PFDR-727bfc)

Red Team, review round BATCH-924d2c. This file covers joint J3b only. It reads the inference against the
proves-too-much objects (`outputs/ptm-results.json`) and the recorded data. Every number comes from an output
file in this directory, and each claim names that file.

## 1. Narrowest conclusion sentence that survives every PTM object

> On generated prime-order ordinary toy curves E/F_p with p of 20, 24 and 28 bits (main seed block 8,100,000 + c,
> j != 0, 1728), for x-label sets of rank r <= 3 log-GAPs built as specified (independent uniformly random base
> points, one representative per +-c, lexicographic half-box fill, every valid set collected from an injective
> box), of size 256 <= n <= 4096, the pooled nontrivial pair-sum coincidence count matches that of uniform label
> sets of the same size on the same curves within the measured per-cell 95% interval at each of the 44 assessable
> cells (|kappa - 1| bounded by x_c <= 0.0743 at every cell, x_c <= 0.0052 at every cell with n >= 2048;
> b20-r3-n4096 not assessable). That is, H1 is not contradicted for this statistic at the tested toy scope. The
> reading says nothing about label-describability or membership predicates, other statistics of the label sets,
> other set shapes or labelings, larger n or p, or any standardized curve.

The per-cell bounds x_c (the max |ci95 - 1| of the recorded bootstrap interval) are in `outputs/power-table.json`
under `/cells[]/equivalence_bound_recorded_ci`. The absolute bound on excess coincidences per set (the quantity a
cryptographic transfer would need) is in `outputs/regime-table.json`. The obstruction block should carry both.

## 2. Sentences that fail, and the object that defeats each

| # | Sentence (source) | Defeated by | Narrowed sentence that survives |
|---|---|---|---|
| F1 | "the reading is a scoped closure of label-describable rank <= 3 log-GAP bases at the toy sizes tested" (specification.yaml decision_impact.on_positive; DEC-20261022-f1efde rationale) | PTM-4a and PTM-4c. Both are label-describable objects (4a: a subset of L, the set cut out by the label predicate chi(f(x)) = 1; 4c: membership decided by one modular inversion and one comparison, a polynomial-time label predicate at every p). The frozen instrument reads both null at every tested cell. The statistic cannot tell label-describable sets from non-describable ones. The closure standard (docs/inventor-protocol.md section 4) is also not met for "label-describable": the measured obstruction is only the h = 2 pair-sum count. | "a scoped closure of pair-sum (h = 2) label-additive excess or deficit beyond x_c in the x-label sets of rank <= 3 log-GAPs (as built) at the 44 tested toy cells" |
| F2 | "The implicit-membership route of KN-OPEN-020 for the unknown-sharing base of IDEA-20261017-bbc53e is then not opened by a label predicate at these sizes" (decision_impact.on_positive) | PTM-4a/4c: a label predicate exists for sets that read null, so a null cannot show that no label predicate exists. It is also an untested object: the bbc53e base is F' = {cP : P in F_0, 1 <= abs(c) <= c_0}, a union of abs(F_0) rank-1 progressions over many independent points. It is not a single rank <= 3 box, and neither its cross-component coincidences nor its size regime was measured. | "these rank <= 3 log-GAP label sets show no pair-sum coincidence excess beyond x_c, the excess a small-doubling (Freiman-type) label description would force at these sizes; the implicit-membership route of KN-OPEN-020 and the union-of-progressions base of IDEA-20261017-bbc53e are not tested by this experiment" |
| F3 | "No label predicate of low complexity can therefore describe a log-GAP base" (IDEA-20261017-078074 claim) | PTM-4c, a low-complexity label predicate whose sets read null | as F1 |
| F4 | "Every toy cell within 5 percent with the planted arm recovered closes label-describable log-GAPs at the tested toy sizes" (H-PFDR-727bfc falsification_conditions[0]) | PTM-4a/4c (as F1). Also "every toy cell" is not observed: 44 of 45 cells, b20-r3-n4096 invalid. | as F1, over 44 cells |
| F5 | "a true 10% excess (375) sits about 6 sd out and the flag rule abs(z) > 4 detects it with probability above 0.95 under Poisson variance" (specification.yaml sample_size_justification) | J3a and PTM-2 at f = 0.10. The flag rule is the conjunction abs(kappa - 1) >= 0.10 AND abs(z) > 4, so at a true 10% departure its power is 0.50 at every powered cell (power-table.json). Empirically the flag rate at kappa_true ~ 1.10 is below 0.95 at every tested cell, and 0 of 8 at the high-count cells, where kappa_true lands just below 1.10 (ptm-results.json). The sentence holds for the z conjunct alone. | "the z conjunct alone detects a 10% departure with probability >= 0.95 at every powered cell; the flag rule reaches 0.95 only at abs(kappa - 1) >= 0.110 to 0.130 (per cell); a 10% departure is read null with probability <= 0.0033 at every powered cell" |
| F6 | "H1 ... labels x(cP) ... behave as independent uniform elements of L" read as established by O-NULL (H1 statement) | PTM-3 at b24-r1-n4096 and b20-r2-n4096 (deficit sets the specified greedy reaches, kappa ~ 0.95 to 0.99, abs(z) in the hundreds; see section 3). The frozen null class reads a known, hugely significant departure below 5% as null. The null class is a 5% equivalence margin, not a test of "independent uniform". | "H1 as operationalised (abs(kappa - 1) < 0.05 with the interval inside [0.90, 1.10]) is not contradicted; the literal random-model statement is not established" |

Sentences that survive as written (with the 44-cell scope added): "may move to analyzed and, after independent
review ..., to supported at the tested toy scope only"; "the evidence record carries an obstruction block
(quantity kappa per cell with its 95% interval, the runs it is read from, the scope above) with its
resource_check"; "the growth-in-n question stays with the EXP-PFDR-0b3699 lineage and the idea's real-curve
prediction stays untested".

## 3. Proves-too-much table (frozen classification against the failure signature)

Filled from `outputs/ptm-results.json` (PTM-1 from `outputs/ptm1-results.json`). The cells were chosen as the
lowest-power r at n = 256 and n = 4096 per bits, plus the lowest-power cell overall and the widest-interval cell.

| Object | Construction (reviewer code unless noted) | Why known false | Cells | Frozen classification received | Failure signature | Result |
|---|---|---|---|---|---|---|
| PTM-1 | recorded plant arm routed as the gap arm (gap_C := plant_C), all main records | true label AP inside every set | all 44 powered; 45 half-cells | R0, all curves, empty replication file: 44/44 flagged (+), min kappa 1.289, min z 21.9; reading O-PENDING-REPLICATION, headline INCONCLUSIVE. R1, even curves as discovery and odd curves as pseudo-replication: 35 flagged (9 cells underpowered on a half), 35 of 35 survive; O-STRUCT, FALSIFY_SCOPED. The reviewer classifier and the producer's run.analyze_records agree class for class. | flagged with sign at every powered cell; O-STRUCT via the pseudo-replication | PASS |
| PTM-2 at 1.15 | label AP + uniform fill; AP-internal count = 0.15 x null mean by per-curve error diffusion (realized 0.150) | kappa_true ~ 1.15 (1.144 at the dense b20 n = 4096 cell) | 8 cells x 2 | 16/16 flagged (+), kappa 1.114 to 1.163 | flagged with sign at every tested cell | PASS |
| PTM-2 at 1.10 | same construction, f = 0.10 (realized internal fraction 0.100 in all 64 runs) | kappa_true ~ 1.10 (1.096 at b20-r2-n4096, 1.0998 at b24-r1-n4096, 1.0999 at b28-r3-n4096) | 8 cells x 8 | 25/64 flagged (0.39), 39 intermediate, 0 null. Per cell: 0/8 at b20-r2-n4096 and b24-r1-n4096, 3/8 at b28-r3-n4096 (kappa 1.0995 to 1.1003), 2/8 at b24-r1-n256, 5/8 at b20-r3-n256, b28-r1-n256, b28-r1-n512, b28-r2-n256 | flag rate >= 0.95, or the shortfall localizes the cells | FAIL against the design's 0.95; the shortfall is general and structural (the effect-size conjunct equals the alternative boundary), so it localizes no cell; no realization was read null |
| PTM-3 | uniform (n + k)-subset of L, exact greedy removal of the label in the most coincidences, k set by error diffusion (mu < 100) or a pilot | kappa ~ 0.85 | built as specified at 6 cells (b20-r3-n256, b24-r1-n256, b28-r1-n256, b28-r1-n512, b28-r2-n256, b28-r3-n4096) | 6/6 flagged (-), kappa 0.822 to 0.850 | flagged with sign at every tested cell | PASS where the object exists |
| PTM-3, not built as specified | b20-r2-n4096: no set of 4096 residues has pooled kappa < 0.912 (counting floor); b24-r1-n4096: the greedy saturates (0.973, 0.961, 0.951 at k = 1500, 3800, 8718). Substitutes were built at k = n. | known deficit | 2 cells | substitutes read null: kappa 0.990 (z -466) and 0.954 (z -534) | n/a (the specified object does not exist) | not built; the substitutes show the 5% margin, not a sensitivity defect |
| PTM-4a | uniform n-subset of L (fresh reviewer stream) | label-describable (inside L, the set where chi(f(x)) = 1) | 8 | 8/8 null | instrument expected null; the inference must refuse label-predicate conclusions | instrument as expected; the INFERENCE FAILS (F1, F2) |
| PTM-4b | geometric progression x0 g^k, g primitive, first n terms in L | label-describable through a discrete log in F_p^*; multiplicatively structured | 8 | 4 null (z -15.1, -27.2, +14.6 at the n = 4096 cells; -1.6 at b20-r3-n256), 4 intermediate (over-dispersed counts, interval beyond [0.90, 1.10], at the low-count cells) | expected null | null where counts are dense; the frozen interval rule catches the clumped counts elsewhere |
| PTM-4c | inverse interval: x = k^-1, k = t, t+1, ..., first n in L | label-describable by a polynomial-time label predicate at every p | 8 | 8/8 null (z +18.8 at b24-r1-n4096) | expected null; the inference must refuse | instrument as expected; the INFERENCE FAILS (F1 to F3) |
| PTM-5 short | uniform n-subset of L in an interval of length 4n | interval sets are additively structured | 8 | 8/8 flagged (+), kappa 31 to 1.3e5 | flagged with sign at every tested cell | PASS |
| PTM-5 half (reviewer addition) | uniform n-subset of L in an interval of length floor(p/2) | kappa_true = 4/3 | 8 | 8/8 flagged (+), kappa 1.331 to 1.369 | flagged with sign | PASS |

Where the argument survives a known-false object, that location is the finding:

- The instrument has no sensitivity defect at any tested cell (PTM-1, PTM-2 at 1.15, PTM-3 where it exists, PTM-5).
- The argument "O-NULL, hence no label predicate" goes through unchanged on PTM-4a and PTM-4c, where its
  conclusion is false. It fails at the step from "pair-sum count matches uniform" to "not label-describable /
  not opened by a label predicate". The observable (kappa) has no separator for label-describability
  (observation-fiber attack). Label-describable sets (4a, 4c) and the log-GAP sets lie in the same fiber.
- The argument "O-NULL, hence labels behave as independent uniform elements" goes through on the PTM-3
  substitutes and on PTM-4b/4c at the dense cells (|z| 15 to 534 with |kappa - 1| < 0.05). The null class is a
  5% equivalence margin. At the high-count cells the instrument resolves 0.1%-scale label structure in z, and the
  frozen class discards it by design. Against that resolution, the log-GAP arm's |z| <= 3.13 at those cells is
  the informative statement: the observed |kappa - 1| is at most 0.0025 at every cell with n >= 2048 (3 sigma_kappa
  <= 0.0042) and at most 0.0005 at every cell with n = 4096 (3 sigma_kappa <= 0.0011).

## 4. Regime table (J3b item 1)

kappa_floor is the least kappa possible for ANY set of n distinct residues, from pair sums spread evenly; it is
computed in `scripts/ptm_sets.py`. The table is per (bits, n), since r changes neither p nor n. The absolute
excess bound is the 95% bootstrap bound on (S - M)/curves, maximized over r.

| bits | n | mean p | n^2/p | E[C] per set | n/sqrt(p) | max_r x_c (abs(kappa-1), 95%) | max_r abs(excess) per set (95%) |
|---|---|---|---|---|---|---|---|
| 20 | 256 | 7.95e5 | 0.0825 | 687 | 0.287 | 0.0258 | 18.1 |
| 20 | 512 | 7.95e5 | 0.33 | 1.11e4 | 0.574 | 0.0044 | 49.7 |
| 20 | 1024 | 7.95e5 | 1.32 | 1.79e5 | 1.15 | 0.0009 | 164 |
| 20 | 2048 | 7.95e5 | 5.28 | 2.87e6 | 2.30 | 0.0003 | 706 |
| 20 | 4096 | 7.95e5 | 21.1 | 4.61e7 | 4.59 | 0.0001 (kappa_floor 0.912) | 4.26e3 |
| 24 | 256 | 1.25e7 | 0.0053 | 43.7 | 0.0725 | 0.0582 | 2.60 |
| 24 | 512 | 1.26e7 | 0.0208 | 701 | 0.144 | 0.0186 | 13.1 |
| 24 | 1024 | 1.26e7 | 0.0834 | 1.13e4 | 0.289 | 0.0041 | 47.8 |
| 24 | 2048 | 1.26e7 | 0.334 | 1.81e5 | 0.578 | 0.0016 | 298 |
| 24 | 4096 | 1.26e7 | 1.33 | 2.90e6 | 1.16 | 0.0002 | 695 |
| 28 | 256 | 2.02e8 | 3.3e-4 | 2.70 | 0.018 | 0.0743 | 0.194 |
| 28 | 512 | 1.99e8 | 1.3e-3 | 44.1 | 0.036 | 0.0632 | 2.79 |
| 28 | 1024 | 2.08e8 | 5.0e-3 | 681 | 0.071 | 0.0203 | 13.6 |
| 28 | 2048 | 2.08e8 | 0.0202 | 1.09e4 | 0.142 | 0.0052 | 56.5 |
| 28 | 4096 | 2.08e8 | 0.0806 | 1.75e5 | 0.284 | 0.0012 | 208 |
| reference | 4096 | 2^256 | 1.4e-70 | 3.0e-64 = 2^-211 | 1.2e-35 | not tested | not tested |

Regime read:

- The reading covers the coincidence-rich regime, E[C] per set from 2.7 to 4.6e7. The cryptographic regime,
  where E[C] is far below 1 (2^-211 at p = 2^256, n = 4096), is not covered. There the question is whether a
  log-GAP has any nontrivial coincidence at all, so a p-independent structural coincidence rate is what matters.
- The instrument's sensitivity to a p-independent structural rate is set by the absolute per-set bound, not by
  kappa. The tightest bounds are 0.09 to 0.19 coincidences per set at b28 n = 256. They are about 2.6 per set at
  b24 n = 256 and b28 n = 512, and grow with n everywhere else. A mechanism producing 0.1 structural coincidences
  per n = 256 set would be essentially invisible here, yet it would exceed the random expectation at p = 2^256 by
  about 2^208.
- The question posed was how the reading should behave as p grows at fixed n if structure exists: a structural
  count c gives kappa - 1 = c/mu, rising with bits. The only cell with a 95% interval excluding 1 at the most
  sensitive size is b28-r1-n256 (kappa 1.041, excess 0.11 [0.025, 0.19] per set). That is consistent with c ~ 0.1
  and with chance (z = 2.52, one of 44 cells; tail-and-correlation.json). It is not resolved here; see the
  report's next action.
- n relative to sqrt(p): 10 of 45 cells have n > sqrt(p) (all bits 20 cells with n >= 1024, and bits 24 with
  n = 4096). The recalled "Ahmadi-Shparlinski threshold ~p^(1/2)" does not match the source (section 6), and no
  tested cell has a proven kappa = 1 anchor.

## 5. Objects the wording could be read to cover that were not tested (J3b item 2)

Already listed in the contract's interpretation limits: translated boxes x(Q + cP); other box orders and fills;
sets with both lifts; y-labels and other labelings; other curve models (Montgomery, Edwards, Hessian x); non-GAP
bases; h >= 3 coincidences; n > 4096; p > 2^28; standardized and deployed curves; any cost or security
statement.

Not in the contract's limits, but covered by the wording "rank <= 3 log-GAP bases" or "the unknown-sharing base":

1. Folded boxes: log-GAPs whose base points carry a short relation. No valid set had a single duplicate skip
   (near-degenerate.json: duplicate_skips = 0 in every ok job of every r >= 2 cell). The 4 relation-degenerate
   tuples were excluded by the frozen rule. The reading therefore covers injective boxes only.
2. Structured base points: P_i that are small multiples of one point, or base points chosen with known
   relations. Only independent uniform P_i were tested.
3. The union-of-progressions base of IDEA-20261017-bbc53e (abs(F_0) >> 3 rank-1 progressions, c_0 = N^gamma),
   and ranks r > 3.
4. j = 0 and j = 1728 curves, where automorphisms put multiplicative structure (x -> beta x) on label sets.
   The toy generator rejects them. secp256k1 is a j = 0 curve.
5. Other statistics of the same sets: higher moments of C, the sumset growth law, multiplicative energy,
   energy against L, and any membership predicate. The reviewer's distribution-level checks found the per-curve
   distribution consistent with the null (dispersion-pit.json), so this item is a scope note, not a finding.

## 6. Recalled citation, retrieved (red-team responsibility 9)

The hypothesis and idea cite "Ahmadi-Shparlinski 2010 (recalled): forbids small label sumset and small group
sumset together above about p^(1/2)". Retrieved: O. Ahmadi and I. E. Shparlinski, "Bilinear character sums and
sum-product problems on elliptic curves", Proc. Edinburgh Math. Soc. 53 (2010) 1-12 (arXiv:0806.0640; read: the
abstract and the theorem statements in the ar5iv rendering).

- That paper pairs x(aP) + x(bP) with x(abP), i.e. label sums against a multiplicative structure in the scalar,
  not against a group sumset.
- Its nontrivial ranges for a prime-order curve (T ~ q) begin near #A >= q^(9/10) (Corollary 3) and q^(15/16)
  (Corollary 4), not at p^(1/2).
- The group-sum variant, x(R) + x(S) against x(R ⊕ S), is Shparlinski, Finite Fields Appl. (2008). Its bound
  #U #V >> min{q #R, #R^2 #S q^(-1/2)} is read only from the restatement in arXiv:1302.4210, not from the
  original. That bound is nontrivial for n >> q^(1/2). It is a lower bound on a sumset size, so even there it
  gives no upper bound on coincidences and no kappa = 1 anchor.
- The citation's role is "scope, not support", so the null reading does not rest on it. The p^(1/2) wording
  should be corrected and attributed to the 2008 paper, and the record should keep "no proven anchor at any
  tested cell".

## 7. J3b item 3: near-degenerate jobs and the degenerate jobs

- No near-degenerate stratum exists. Every ok job in every r >= 2 cell has duplicate_skips = 0, so the plan's
  top-decile comparison is empty (`near-degenerate.json`, the strata_plan entries). No near-degenerate departure
  can hide in the pooled kappa because there are no near-degenerate jobs.
- The 4 degenerate jobs (b20-r3-n4096, c = 6, 30, 42, 47) each carry one generic short relation among the base
  points: (5, 2, -14), (13, 9, -8), (1, -11, 5), and (4, -8, 3) together with its double. The reviewer rebuilt
  their half-box enumerations bit-exactly (`degenerate-relations.json`). The duplicate count equals the overlap
  of the relation, for example prod(21 - abs(v_i))/2 = 624 for (13, 9, -8). No relation of the form P_i = +-P_j
  occurs, so no trivial seeding defect is visible.
- Unexpected observation: 4 degenerate curves of 50, against 0.73 (Monte Carlo) to 0.89 (overlap count)
  expected under independent uniform base points (Poisson p ~ 0.007 to 0.013; near-degenerate.json,
  duplicate_model). This is recorded, not explained. It is not evidence about H1.
- Implication for the invalid cell: b20-r3-n4096 is not assessable. Its 46 ok curves are a survivor sample
  conditioned on "no relation with overlap > 534 in the 2T box". They are not a reading of the cell and must not
  be pooled into one. For the scope, the valid data cover injective boxes only (section 5, item 1). At
  cryptographic N a relation in a box of side 4T + 1 has probability about (4T+1)^r/N, effectively 0, so the
  exclusion does not bias transfer to random base points. It does leave folded or structured-base log-GAPs
  untested.

## 8. J3b item 4: promotion gates and the exemplar checklist

- H-PFDR-727bfc has asymptotic_claim null and claims no exponent. The four asymptotic promotion gates do not
  apply, including the concrete-cost table before promotion past analyzed (docs/target-result-profile.md Part D).
  The composition_rule.promotion_gates_note reading holds.
- Exemplar checklist (Part C): C1 and C2 are "no" (no exponent change), so the hypothesis is non-target-class and
  the checklist classifies rather than gates. "May not reach supported without C12-C16" binds target-class
  promotion, so it does not block here.
- Heuristic-validation obligations that do apply (docs/evidence-and-reproducibility.md "Heuristic-validation
  experiments"; docs/claims-and-verification.md "Heuristic records"):
  - (a) Pre-registered prediction: met (P1, P-detect, P2, frozen 2026-10-22).
  - (b) Exact prediction source, rigorous bound plus classical distribution theorem: NOT met. H1's
    rigorous_support is "recalled, not read; no bound at these sizes"; the random-set law is a model computation,
    not a proven bound on x(cP). The gap belongs in an obstructions entry, together with the misattributed
    threshold of section 6.
  - (c) Scale stated, no transfer claimed: met (R10). The tested scale is a design choice, not "the largest
    feasible", so the record should say so.
  - (d) Tail consistency checks: met descriptively. The largest abs(z) = 3.13 has familywise p 0.074 independent,
    0.073 with the estimated correlation, 0.10 with the calibration bias (tail-and-correlation.json).
  - (e) Every deviation recorded as an unexpected observation. Owed: the degenerate excess (section 7), the
    cell-level heterogeneity of gap z (omnibus-null-controls.json, split-half.json), the b24-r1-n2048 deficit
    (coherent across curves, about 0.1%), and the b28-r1-n256 interval excluding 1.
  - (f) "Agreement supports, never proves": the evidence record keeps the heuristic conditional.

## 9. J3b item 5: supported on this run set without a replication block

- Consistent with the frozen rules. The replication rule acts only on flagged cells, and with none flagged
  O-NULL follows. decision_impact.on_positive permits supported after independent review. Repository precedent
  allows analyzed -> supported without a replicated state (H-SEMBIN-97ea23, DEC-20260915-fad1c1).
- Three limits apply, each traceable to the rules:
  - (a) The design leaves one error mode unreplicated by construction: a false null is never confirmed on the
    replication block. The guard against it is the null class itself (P(read null | abs(delta) = 0.10) <= 0.0033
    per cell), not replication.
  - (b) The evidence rests on one main seed block. Its strength is the Coordinator's call; "replicated" in the
    evidence-hierarchy sense is not met. docs/task-lifecycle.md promotes a KN-FIND only for a support decision
    backed by replicated or strong evidence.
  - (c) The supported statement can only be the narrowed sentence of section 1, over 44 cells.
