# ECDLP-IDEA-198 — Barvinok carry-state source unranking

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- Top lane: `-`
- State: `merged_rejected_fixed_dimension_encoding_requires_scalar_or_growing_carries`
- Cohort: `20260718-d`
- Evidence scale: literature and representation audit only; no experiment ran
- Contract posture: none
- Scale labels: prospective tests are `toy`; projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a short generating function or unranked tuple is not an ECDLP break.

## Falsifiable hypothesis

Recursive elliptic addition and factor-base membership can be encoded as a fixed-dimensional modular carry polytope whose lattice-point set has a target-independent short rational generating function. Hadamard products, projection, and lexicographic unranking then return exact five-source fibers below rho and BSGS.

## Mechanism-new operation

The operation is **short rational generating-function projection and exact unranking of a modular carry encoding**. Unlike a generic SMT or Gröbner solver, it claims a fixed-dimensional representation theorem. The audit finds that elliptic field multiplication either remains nonlinear or needs `Omega(log N)` bit/carry variables; replacing coordinates by scalar indices is the DLP. Without that theorem the proposal is a solver substitution.

## Assumptions

1. Public `E/F_p`, prime order `N`, factor base `F` of size `B=N^beta`, and target are fixed.
2. A fixed-dimensional integer/carry system encodes field arithmetic and complete elliptic charts exactly.
3. Its short generating function has size at most `B^2.25` and supports target specialization without rebuilding.
4. Projection/unranking returns every exact signed source and multiplicity with no scalar-coordinate oracle.
5. Coefficient bit lengths, Hadamard products, failed targets, output, rank, descent, and memory are charged.

## Semantic fingerprint

`elliptic_coordinate_carry_polytope | fixed_dimension_short_rational_generating_function | target_Hadamard_projection | lexicographic_exact_source_unranking | blind_descent`

## Five closest ledger entries

1. `inputs/ledger_inventory.json` — imported `P1480`, the exact bit-vector SMT compilation control.
2. `inputs/ledger_inventory.json` — imported `P1477`, the dense serial-state control.
3. `inputs/ledger_inventory.json` — imported `P1434`, the missing public source generator.
4. `inputs/ledger_inventory.json` — imported `ECFG-H642`, a target support-router hypothesis.
5. `inputs/ledger_inventory.json` — imported `ECFG-H643`, the complete source/rank/descent accounting frontier.

## Closest primary literature

- Barvinok and Woods, [Short rational generating functions for lattice point problems](https://arxiv.org/abs/math/0211146), gives polynomial algorithms only under fixed-dimensional rational-polyhedral hypotheses.
- Barvinok, [A polynomial time algorithm for counting integral points in polyhedra when the dimension is fixed](https://doi.org/10.1109/SFCS.1993.366830), supplies the fixed-dimension counting primitive.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031), supplies nonlinear elliptic relation equations, not a fixed-dimensional integer lift.

No checked source supplies the required encoding; novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze coordinate charts, integer encoding, factor-base index map, generating-function grammar, masks, and verifier.
2. Construct one target-independent short function and prove exactness and size bounds.
3. Specialize known-log endpoints, unrank all exact signed sources, and verify them.
4. Preserve poles, carries, overflows, signs, repeats, infinity, multiplicity, failed queries, and output.
5. Collect full-rank rows and solve/verify factor logs.
6. Specialize the same object to fresh `Q+[r]P` masks.
7. Recover candidate scalars, subtract masks, and verify `[x]P=Q`.
8. Charge construction, bit complexity, projection, unranking, rank, descent, verification, and memory.

## Full rho/BSGS cost model

Rho costs `N^(1/2+o(1))` time; BSGS costs that time and memory. Let setup be `N^a,N^a_m`, reciprocal densities `N^delta,N^delta_t`, specialization/unranking `N^q,N^q_m`, ranked rows/query `N^r`, output/ambiguity `o,u`, and linear algebra `N^ell,N^ell_m`. The complete exponents are

`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

Both must be at most `0.45`; polynomial time in an uncharged dimension is invalid.

## Likely fatal obstruction

Barvinok complexity is exponential in dimension. Exact finite-field multiplication and inverses need a growing bit/carry circuit or nonlinear Diophantine constraints; lifting all field variables gives dimension `Omega(log N)` or coefficient/monomial expansion beyond the gate. Scalar-linear constraints would require discrete-log labels. Projection can also count without retaining signed point sources.

## Proof track

Give an explicit fixed-dimensional rational polytope family, prove its short-function size and all-strata source biconditional, exclude scalar labels, and derive `lambda,mu<=0.45` in bit operations.

## Disproof track

Prove dimension grows with `log N`, expose nonlinear/nonpolyhedral constraints, show projection merges source tuples, reduce the encoding to scalar coordinates, or derive complete exponent at least `0.50`.

## Positive and negative controls

- Positive control: fixed-dimensional modular linear systems with independently known lattice points.
- Negative control: P1480 bit-vector circuits, scalar-coordinate encodings, dense Presburger expansions, and source tables.
- Negative control: rho, BSGS, known-log targets, and blind masks.

## Quantitative promotion and falsification gates

This version is merged/rejected. A successor needs dimension bounded independently of `N`, short-function size at most `B^2.25`, 100% exact source/multiplicity recall, no scalar labels, and `lambda,mu<=0.45`. Growing dimension, a nonlinear oracle, one merged source, or exponent at least `0.50` falsifies it.

## Artifact plan

- Prospective encoding theorem: `ideas/artifacts/ECDLP-IDEA-198/fixed_dimension_encoding_theorem.md`
- Prospective source-unranking specification: `ideas/artifacts/ECDLP-IDEA-198/source_unranking_spec.md`
- Prospective cost receipt: `ideas/artifacts/ECDLP-IDEA-198/cost_analysis.md`

All paths are prospective; no artifact root exists.

## Interpretation boundary

This is merged/rejected, novelty-unverified algorithm analysis. Finite tests would be toy and scaling heuristic and model-bound. A short function, count, exact source, or toy scalar is not a breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-198/fixed_dimension_encoding_theorem.md` giving a scalar-free fixed-dimensional polyhedral encoding of complete elliptic addition or proving that exact multiplication forces dimension `Omega(log N)` or nonpolyhedral constraints.
