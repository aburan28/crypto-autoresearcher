# Composition: REVIEW-ICPERF-20260926-bcf1b2 (validator pass on KN-FIND-aa2efc / EV-ICPERF-10c5fc)

Composed by the dispatching top-level session (TASK-20260926-b84965) on
2026-09-26 after both reports were on disk and
`tools/check_review_independence.py --plan review-plan.yaml --reports reviews`
returned `PASS: 2 report(s), every joint owned and attested, blindness
respected, controls declared`. This composition changes no status. It reads
each joint's verdict against the prior recorded in `review-plan.yaml`
before either reviewer ran, and names the additive records a later
Coordinator act would write. Reports: `reviews/TASK-20260926-44629c/
validation-report.yaml` (validator, J1-J4 and the proves-too-much control,
checks under `checks/`) and `reviews/TASK-20260926-9fef40/rederivation-
report.yaml` (blind re-derivation, Q1-Q5, script `rederive.py`).

## 1. Verdicts by joint

| joint | verdict | load-bearing result |
| --- | --- | --- |
| J1 product identity and ambient size | holds | The identity 2^l · N/C(2^l, m) · C(2^l, m−1) = m·N is exact to relative error ≤ 1e-4 at every floor-optimal l. Under the subgroup-restricted model (N = r, base restricted to the order-r subgroup, |F| = 2^l/4) every floor row drops by exactly 4/(m+1) bits (1.33, 1.00, 0.80, 0.67, 0.57, 0.44 at m = 2, 3, 4, 5, 6, 8). The m = 3 floor becomes 2^67.585, still 6.78 bits above rho. No m ≤ 3 row crosses rho under either model. |
| J2 floor table and the oracle-budget definition | holds on arithmetic; definition defect downstream | All six floors reproduce to ≤ 0.05 bit; the oracle-budget column (−27.86, −6.78, +5.71, +13.94, +19.77, +27.35) and the required-speed-up 2^−(70.19 + log2 m) reproduce exactly. Three distinct quantities exist at m = 4: the floor-to-rho gap 2^−4.41 (rho/floor), the producer's per-target oracle budget 2^+5.71 (rho/targets at the floor-optimal l), and the re-optimised per-attempt budget 2^+11.01 (one attempt per relation, B re-optimised; this is IDEA-20260926-4b65e3's "capped" column, which the validator reproduces as its D3). |
| J3 rho reference | holds | sqrt(π r/(4·131)) = 2^60.80904, within 3.7e-5 bit of the finding; #E(F_2^131) = 4r from the Frobenius recurrence; r prime; convention matches CORR-20260922-81aeab (sqrt(π r/(4k)), k = 131). |
| J4 artifacts and strength label | breaks on the label | All seven sha256 values match at f9c77524 and every measured number in the finding reproduces from its artifact. But EV-ICPERF-10c5fc's `strength: replicated` overstates single-run cost claims (each round's own limits say "single sequential run, no repeated-trial statistics"; no in-program reviewer), and two quoted numbers are unbound: the amortisation shares 0.12% / 0.07% (solver_11 is not in the hashed list) and the degree-2 vanishing-ideal base case (6967 / 140400 / 8647 appear in no hashed artifact). The monotonicity argument's direction is sound and its refusal to transfer from m = 4 to m = 3 is correct. |
| proves-too-much control | pass, qualified | In the one comparable unit (the external boundary ledger's round-3 group-addition equivalents), the shape-matched free-oracle floor with N = r sits below all 216 measured toy Koblitz index-calculus totals (minimum total/floor = 2^+2.58); the failure signature does not appear. Under the producer's N = 4r ambient, three high-cofactor toy rows (e.g. n = 39, cofactor 8012) fall up to 2^−1.76 below the floor, which independently corroborates J1: the correct ambient is the target subgroup, not the full curve group. The round-0021/0022 tournament cells (0.831, 1.396, 2.207) are inconclusive, never a pass: their unit is callgrind instructions with no recorded group-operation conversion. |
| blind re-derivation Q1-Q5 | agrees | From the statement alone: floors 89.2516, 68.5850, 56.4049, 48.4352, 42.8501, 35.6086 bits (N = 4r) and 87.9183, 67.5850, 55.6049, 47.7685, 42.2786, 35.1642 (N = r, s = 2); oracle budgets rho/T of −27.86, −6.78, +5.73, +13.96, +19.77, +27.37 bits (N = 4r); rho 60.8090 bits; #E = 4r; r a strong probable prime (65 bases). The producer's, the validator's and the blind values agree to within 0.02 bit everywhere; the blind re-deriver attests it read none of the blind_from paths, and the independence checker confirms no declared source intersects them. |

## 2. Prior versus outcome

| prior | outcome |
| --- | --- |
| P1 exact reproduction of the floor table | held (validator and blind) |
| P2 ambient size moves rows by up to 2 bits toward the attacker, no verdict changes | held in direction, smaller in size: exactly 4/(m+1) bits (1.33 at m = 2 down to 0.44 at m = 8), no verdict changes; and the proves-too-much control produced evidence FOR the correction that the prior did not anticipate (three toy rows below the N = 4r floor) |
| P3 rho reference holds | held |
| P4 gap versus budget are different quantities and downstream records conflate them | held, and sharper: three quantities, not two (gap 2^−4.41, producer's budget 2^+5.71, re-optimised budget 2^+11.01 at m = 4); the validator lists every record in this program that quotes the gap as a per-attempt budget |
| P5 measured numbers match the artifacts | held for every hashed number; two quoted numbers turned out to be UNBOUND (solver_11 amortisation shares; vanishing-ideal base case), which the prior did not anticipate |
| P6 "replicated" is overstated | held (J4 breaks) |
| P7 the floor sits below every measured toy cost | held in the comparable unit; the tournament cells are inconclusive on units, not a pass |
| P8 vanishing-ideal monotonicity sound, no transfer to m = 3 | held |

Nothing the prior expected to hold was overturned. Two things the prior did not expect appeared, both from the controls: the unbound numbers (J4) and the sub-floor toy rows under the wrong ambient (proves-too-much). This is the reason the plan records a prior.

## 3. What the finding's downstream users should read

- The verdict every ECC2K-130 arity claim rests on stands: on ECC2K-130,
  arity m ≤ 3 cannot beat matched rho (2^60.81) even with a free
  decomposition oracle, under either ambient model. The finding's numbers
  are reproducible from their statement by a blind re-deriver.
- The floors are 0.44 to 1.33 bits pessimistic for a subgroup-restricted
  factor base (the cofactor's two bits, spread as 4/(m+1)); IDEA-20260926-
  136bd3's "exact filters carry exactly 2 bits" is the same fact read as a
  filter capacity.
- "Oracle budget per attempt" must be quoted as one of three named
  quantities. The following program records quote the floor-to-rho gap
  (2^4.4 / 2^4.41) where they mean a per-attempt budget: `analysis/binstd-
  idea-review-20260926/BRIEF.md` and `README.md`; `ledger/proposals/IDEA-
  20260926-89886c.yaml` and `-b6cc43.yaml`; the round-1 review YAMLs of
  IDEA-20260922-845a77, 77bf31, 2a3771, 6237e5, 493606, faa8d2, c2bbe6,
  153a90, 1b16d7, 793fd8, 7ab503, 29b1c5 and the three lane summaries;
  IDEA-20260926-4b65e3 mislabels the 2^4.4 column as rho/T while its
  corrected capped budgets (2^11, 33, 37, 42) are right. No verdict in any
  of them changes; the conflation is definitional. `BRIEF-ROUND2.md` states
  the distinction and the round-2 lanes were told to price against the
  budget (the first-summand row), not the gap.
- The finding and the evidence record themselves do not quote 2^4.4 and
  need no correction on that point.

## 4. What a later Coordinator act would write (none written here)

1. An additive scoping correction on KN-FIND-aa2efc / EV-ICPERF-10c5fc:
   the product law's ambient is the full curve group (N = 4r); for a
   subgroup-restricted base the floors drop by 4/(m+1) bits; verdicts
   unchanged on ECC2K-130.
2. A definition pin, in the same correction or as a note on
   RQ-ICPERF-94c86e's boundary table, separating gap, producer's per-target
   budget, and re-optimised per-attempt budget, with the m = 4 values
   2^−4.41, 2^+5.71, 2^+11.01.
3. A strength relabel of EV-ICPERF-10c5fc from `replicated` toward
   `preliminary` for its cost claims (the derivation tier of the product
   law is not affected), and a re-examination of the KN-FIND promotion bar
   the finding's own `promotion_gate` text already disclaims.
4. Binding or marking unbound the two unbound numbers: the solver_11
   amortisation shares and the vanishing-ideal base case.
5. Optionally, a unit-conversion note for the external tournament cells
   (callgrind instructions to group operations) so the proves-too-much
   control can be completed on them; until then they are inconclusive.

## 5. Procedure deviations

None. The plan was written and committed (d378d9840) before either reviewer
ran; the blind re-deriver's report was committed (1a83ab93e) before the
validator's returned and neither read the other. The validator's terminal
receipt verdict is `incomplete` by its own contract's vocabulary because
one joint breaks; that is the honest label for a round with a broken joint,
not a statement that the review is unfinished.
