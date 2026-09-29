# Review analysis — EXP-PFDR-c04716 (H-PFDR-06fd60)

Composed under TASK-20260904-e6b4dd from the two committed blinded reports of
review plan TASK-20260904-2bb29d:

- validator `coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-2bb29d/validation-report.yaml`
- red team `coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-6681da/red-team-report.yaml`

Package under review: `experiments/EXP-PFDR-c04716/runs/STATIC-001/`, a
**zero-run** static derivation package (frozen `maximum_runs: 0`), seven files,
no manifest, no seed, no certificate (`certificate kind: none`).

---

## Observation

**Joint-by-joint verdicts, as the two reviewers reported them.**

| joint | owner | verdict | deciding fact |
| --- | --- | --- | --- |
| V1 package integrity, determinism, zero-run compliance | 2bb29d | holds | 6/6 archived sha256 recompute; exactly 7 files, no forbidden artifact; standard-library-only script; two invocations byte-identical to each other and to the archive |
| V2 independent recomputation of fixtures, cells, thresholds | 2bb29d | holds | 54/54 cells agree, max \|Δ log2 T\| = 0.00004974; all 15 signed hand-value discrepancies reproduced including sign; thresholds and 18 bounded 64-bit cells agree |
| V3 literal accounting of criteria (1)-(5) and P1-P5 | 2bb29d | holds, with one recorded reporting defect | F-A2-MISCOUNT: the execution report says P5's binomial is zero at "7 of the 9" (m, D_0) pairs; the emitted artifact and the reviewer's recomputation both say **6 of 9** |
| R1 generator degree at m ≥ 3 and the Macaulay degree floor | 6681da | **BREAKS** | deg S_{m+1} in the m unknowns is **m·2^{m-1}** (4/12/32/80 at m = 2/3/4/5), not 2m; hence δ = m·2^{m-1} and rows(D_0) = Ncols(n, D_0 − δ) = **0** at all 54 cells and at every D_0 = 2 threshold row |
| R2 bounded last fall vs bounded solve | 6681da | **BREAKS** | the plain-matrix deficiency does not fall to O(1) until D ≥ n + δ − 1 (348 at n = 269, δ = 80); the closure loophole cannot act below the generator degree, so d_lf ≥ d_ff ≥ δ + 1 = 13/33/81 at m = 3/4/5 |
| R3 marginal-cost sign flip, null slice, interior band, k* anomalies | 6681da | holds | exact log2 ratios bracket 0 within 1-3 residual variables of the predicted crossing D_0/(1 − 2^{−1/ω}); the null slice stays strictly decreasing with argmin at the leaf **even with the corrected δ**; P5's binomial is a formula slip and the corrected band cost 2^{n − (2 − 2ω)(D_0 − m)} is still exponential in n |
| R4 concrete-cost honesty, unit bookkeeping, scope | 6681da | **BREAKS** | (a) `cost_unit` is F_p field operations while the prior 127.8254 is 0.886·√N GROUP operations, subtracted directly: any conversion ≥ 2 flips three cells and moves the frozen 256-bit threshold row for (m 4, ω 2); (b) the generator's top-degree part alone has binom(s, 2^{m-1})^m = 2^221.3 nonzero terms at (256, m 5, D_0 4, ω 2), exceeding that cell's entire claimed total 2^108.76; (c) tabulated memory is the factor base only, understated by up to 2^39.9 at three of the four affected cells |

**Proves-too-much control (assigned to 6681da).** The failure signature
appeared on **3 of 4** objects.

- *direct presentation under the same bounded-slice arithmetic* — fired. Emits
  12 sub-ρ cells of 18 at 256 bits, best 2^94.95 against ρ 2^127.83, for an
  object with a **proven** floor d_lf ≥ B = 2^47 (IDEA-20260808-afe4ce). The
  survival is nowhere localised: no step of the argument ever compares D_0 with
  any generator degree.
- *m ∈ {3,4,5} with D_0 below m·2^{m-1}* — fired. Finite cost emitted at all 54
  cells with rows = 0. Survival is at the cost primitive itself: C(k) =
  2^k·Ncols(n−k, D(k))^ω is a **column** count, so an empty matrix and a
  solving matrix of the same width are charged identically.
- *D_0 = 2* — fired, at the load-bearing threshold rows.
- *m = 2 (δ = 4 = 2m)* — did **not** fire; all 18 m = 2 cells sit above ρ by
  +40.48 to +137.44. The arithmetic is right where the object is right.

**Coordinator verification independent of the reports** (round-closure.md
item 3, re-checked here): `KN-TECH-002` states deg S_n per variable is
2^{n−2}, giving m·2^{m-1} total in m unknowns, and
`experiments/EXP-PFDR-5726af/stage0-htop.md` measured total degree 12 with
per-variable [4,4,4] at m = 3. The record's `2m` coincides with the truth only
at m = 2, which is not in the c04716 grid. **The degree fact is confirmed
against this program's own committed corpus and against a second experiment's
symbolic run, independently of the red team's instrument.**

**Provenance of the error (OBJ-9).** IDEA-20260830-84cdb7 claim (A) states
"one generator of total degree 2m (degree 2 in each x_k)", contradicting
KN-TECH-002. It propagates into 84cdb7's null d_reg, into H-PFDR-06fd60 (A)-(B),
into the contract's CTRL-CONFOUNDERS-NAMED (iv), and into every cell here.
IDEA-20260903-e1e38b (D3-D4) corrected it on 2026-09-03; the correction had not
reached this contract.

**Literal criterion failures, recorded as failures.** Criterion item (3) is met
under the contract's own listed hand values (max 0.1516) and under
H-PFDR-06fd60 (D) (max 0.1884), and **not** met under IDEA-20260903-dcf857 (D)
as a whole, where (256, m 4, D_0 6, ω 2.807) is +1.5966 against "about 2^150".
Prediction P3 (k* = 0) holds at 54/54 under the C(k) frozen in
`specification.inputs.cost_model` and **fails at 4/54** under the same model
plus the enumeration-leaf charge frozen in `H-PFDR-06fd60.assumptions`; the
package reported the failing reading as anomaly A1 rather than selecting the
flattering one. Criterion (2) is met by 0.1189 in log2 at its binding cell,
the same order as the package's own n ± 1 rounding sensitivity (0.119).

---

## Comparison

**Against the coordinator prior recorded in TASK-20260904-2bb29d (l.191-236),
frozen before any reviewer ran.**

The prior is **CONFIRMED, in unusual detail, on its central expectation and on
four of its subsidiary ones.**

| prior expectation | outcome |
| --- | --- |
| validator holds on V1 and V3; V2 within 0.2 in log2 at every cell; no zero-run breach | confirmed (max deviation 0.00005; 7 files; determinism) |
| the +1.60 discrepancy is outside the contract's listed hand values and so not a failure of item (3) as written | confirmed verbatim (V3 finding F-ITEM3-READING) |
| red team BREAKS the m ≥ 3 cells on a generator-degree error inherited from 84cdb7, corrected by e1e38b, confirmed symbolically by RUN-PFDR-5726af-htop; degree m·2^{m-1} (12/32/80), not 2m | confirmed exactly, including the numbers and the provenance chain |
| every bounded-slice cell at m ∈ {3,4,5} with D_0 ∈ {4,6,8} charges a matrix with **no rows**; only m = 2 is a possible object and m = 2 never beats ρ | confirmed exactly |
| the headline "beats ρ at m = 5 for D_0 ≤ 6" is void by derivation, independently of HEUR-001 | confirmed |
| a second, independent obstruction to HEUR-001's bounded-solve half from the row count Ncols(n, D − δ) vs Ncols(n, D) | confirmed (R2), with the sharper bound D ≥ n + δ − 1 |
| P5's interior-band formula is a derivation slip, harmless to the qualitative claim | confirmed (R3, OBJ-7), with the corrected residual column count 2^{2(D_0−m)} |
| the honest content of the package is the null-slice reproduction of da1428 and the flip mechanism at m = 2 | confirmed, and the reviewers add three more surviving items (see Inference) |

The prior is **REFINED, not overturned, in three places the prior did not
anticipate**, all of them adverse and none of them softening:

1. **OBJ-4, unconditional on everything.** The generator cannot be written
   down at the cells carrying the claim: binom(s, 2^{m-1})^m = 2^221.3 nonzero
   terms in its top-degree part alone at (256, m 5, D_0 4, ω 2), exceeding that
   cell's entire claimed total by 2^112.5, at every m = 5 cell. This is
   independent of HEUR-001, of D_0 and of ω. The prior did not contain it.
2. **OBJ-5 moves a FROZEN threshold.** The unit mismatch between `cost_unit`
   (field operations) and the prior (group operations) flips three cells and
   moves the frozen 256-bit bracket for (m 4, ω 2) from "T ≥ ρ at D_0 = 4" to
   "T < ρ at D_0 = 4". The bias is conservative for the claim, but the near-tie
   verdicts are not robust to the artifact's own declared unit.
3. **V2's observation-collision finding.** The hypothesis's own
   `proof_search_map` names the interior band as the observable separating
   "HEUR-001 true everywhere" from "a partial bound at k = 0 only". The
   validator verified independently that k_c lies OUTSIDE the guessing range at
   54 of 54 cells and that P5's top binomial is zero at 6 of 9 (m, D_0) pairs,
   so **the separator does not separate at any cell in the table**. The package
   emits the facts that imply this and does not draw the consequence.

The one place the two reviewers touch the same fact — P5's binomial count —
they agree with each other and disagree with the execution report's prose (6 of
9, not 7). No reviewer-versus-reviewer disagreement requires localisation.

---

## Inference

**What the two reports jointly establish, scoped to the tested arithmetic**
(d = 2 digit presentation, m ∈ {2,3,4,5}, D_0 ∈ {2,4,6,8}, ω ∈ {2, 2.807},
log2 N ∈ {64,128,256}, exact integer binomials, **no curve at any scale**):

1. **The receipt is admissible at derivation tier.** The archived package is
   exactly what its script produces, the script is exactly what the frozen
   formulas produce, and the zero-run contract is honoured in the committed
   snapshot. This is a statement about the arithmetic, not about the object.
2. **The headline is void by derivation.** Every bounded-slice cell of
   `cost-table.yaml` at m ∈ {3,4,5}, and every D_0 = 2 row at every m, prices a
   Macaulay matrix with **zero rows**. The four cells reported as beating ρ are
   among them. This is a derivation from the generator's degree and is
   **independent of HEUR-001** — it does not wait on any measurement.
3. **HEUR-001 at the tabulated D_0 is not merely unmeasured at m ≥ 3, it is
   excluded by counting.** A degree fall needs a multiplier of degree ≥ 1, so
   d_lf ≥ d_ff ≥ δ + 1 = 13/33/81 at m = 3/4/5. Any D_0 that could satisfy
   HEUR-001 is at least m·2^{m-1}, and at that floor the same balance gives
   log2 T = 342.97 at (256, m 5, ω 2) against ρ's 127.83 — a method ceiling
   2^215 **above** the baseline.
4. **The affected scope is empty for a reason internal to the presentation**,
   not merely unmeasured, and at m = 5 it is refuted by OBJ-4 independently of
   HEUR-001. Any future citation of the four cells must carry that.

**What survives, recorded as carefully as what fell.** Constraint 4 of the
composition handoff requires this, and the red team names it explicitly in its
own `narrowest_supported_statement` item (5):

- **The null-slice reproduction of IDEA-20260808-da1428** — C(k) strictly
  decreasing, argmin at the enumerative leaf, assembly slope exactly N^1 —
  holds **with the corrected generator degree δ = m·2^{m-1}**, at all six
  fixture cells and both ω, and independently at all 54 balanced table cells.
  Fixture F1 survives the correction.
- **The marginal-cost sign derivation of claim (C)** is correct within the
  model: the exact crossing sits 1-3 residual variables below the asymptotic
  formula D_0/(1 − 2^{−1/ω}), whose constants 13.66/20.49/27.31 (ω 2) and
  18.28/27.42/36.56 (ω 2.807) both reviewers reproduce.
- **The corrected interior band** is 2^{n − (2 − 2ω)(D_0 − m)}, still
  exponential in n, so the qualitative claim of P5 stands after the formula is
  repaired.
- **The m = 2 arithmetic is right**, above ρ by 2^40 to 2^137, and m = 2 is the
  only region of the grid where the priced matrix has any rows at all.
- **The total-cost bookkeeping is right.** Both reviewers independently
  re-derived the balance from B relations, per-target success probability
  B^m/(m!·N) and 2^m·C per call, obtaining exactly B^{m+1} = m!·2^m·C·N and
  T = 2B^2 — the frozen formula. Success is never treated as certain; the
  inverse success probability is genuinely carried in every tabulated number.
- **Both ω on every cell**, the o(1) disclosed per cell, eight optimistic
  assumptions each with a bias direction, `dominated_by` filled and correctly
  signed, `affected_scope` opening "NONE unconditionally", and the executor's
  own disclosure of anomalies A1 and A2 rather than the flattering reading.
  The package's honesty is not in question; its object is.

**What is NOT concluded, in either direction.** The red team states it and this
composition adopts it: it does **not** follow that a bounded last fall degree
is impossible for the digit presentation — a D_0 = m·2^{m-1} + O(1) constant in
s is excluded by nothing here; it does **not** follow that the digit
presentation is worse than the direct one, since its floor m·2^{m-1} does not
grow with the factor base, unlike afe4ce's B, which is a real structural gain;
and nothing here is a universal impossibility claim about index calculus over
prime fields.

**Promotion ceiling.** H-PFDR-06fd60 carries an asymptotic-complexity claim
(a conditional exponent). Under the four promotion gates it may not move toward
`supported` at all here — gate (1) fails (no lemma decomposition survives the
degree correction), gate (2) fails (HEUR-001 is excluded at the tabulated D_0),
gate (3) fails (the cost table prices an object with no rows and understates
memory), gate (4) is partly met by this round. The ceiling is `analyzed`, and
the decision reaches it from the adverse side.

---

## Limitation

1. **Nothing here was measured.** Zero runs, zero seeds, zero curves, zero
   sampled points, by frozen contract. Every number is an estimate conditional
   on HEUR-001 or an exact binomial identity. `scale_relevance.tier` is `toy`
   with the justification that no curve at any scale is examined; the 64/128/256
   rows are estimates, not measurements, and no cryptographic-scale label
   attaches anywhere.
2. **The validator did not audit `cost_table.py` line by line** (750 lines; it
   read the docstring, imports and targeted greps, ran it twice, and
   reimplemented every load-bearing quantity). Equality of the reimplementation
   with the archive is strong evidence about the ARITHMETIC, not a proof that
   no unused branch does something else. `ck-curves.yaml` (19305 lines) was
   re-derived at the level of invariants, not point by point.
3. **The F2 second pass is not blind.** The validator's first, pre-hashed pass
   gave slope ω − 1 and disagreed with the archive by 2.0 in the exponent; the
   agreement at 2ω − 1 was reached only after `cost_table.py` was opened and
   IDEA-20260808-da1428's mandated root-finding leaf charge was read. Both
   passes are preserved. The agreement is therefore weaker evidence than the
   disagreement was, and F2's headline exponent is not a property of the
   Macaulay column counting alone.
4. **The degree probe is the red team's own instrument.** It is validated
   against a known answer (S_3..S_6 vanish on 5/5 genuine zero-sum tuples and
   not at random tuples) and against EXP-PFDR-5726af's symbolic S_4, and this
   Coordinator confirmed the same fact from KN-TECH-002 and from 5726af's
   committed stage0 note. But no reviewer re-derived the degree law from a
   published source in this round; KN-LIT-001 is cited at key-claim level.
5. **The Huang-Kosters-Yeo relation** that would connect HEUR-001's two clauses
   is carried as `provenance: recalled, verified_by: null`. Neither reviewer
   opened the source. It stays a pointer in this composition too, and it backs
   nothing.
6. **Both reviewers report `model_verified: false`** with `AUTORESEARCH_POLICY`
   and `AUTORESEARCH_BACKEND` unset. Judgement across this round is correlated:
   producer and both reviewers report the same model family.
7. **This composition ran no code and no tool.** The Coordinator subagent has no
   shell; it verified the degree fact by reading committed records, not by
   executing the red team's script. The reproduction of
   `counterexample_certificate.py` recorded in round-closure.md item 2 belongs
   to EXP-PFDR-5726af, not to this experiment.
8. **Two corrections are owed and are NOT made here**, because records are
   immutable: the corrected cost table at generator degree m·2^{m-1} with a
   feasibility gate refusing to price a zero-row cell, and an annotation of
   IDEA-20260830-84cdb7 claim (A) / H-PFDR-06fd60 (A) recording the degree.
   Both are named in DEC-20260904-d47cd2's `next_actions` for the orchestrating
   session to allocate identifiers for.
