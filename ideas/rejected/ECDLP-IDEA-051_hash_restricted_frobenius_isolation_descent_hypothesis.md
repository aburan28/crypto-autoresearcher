# ECDLP-IDEA-051 — Hash-restricted Frobenius-isolation descent

## Status and claim labels

- Class: `representation`
- Risk band: `high-risk`
- State: `rejected_merged`
- Evidence scale: `toy` reasoning and preflight only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Deduplication verdict: exact semantic merge with the ledger's already-successful
  trace/deck/Frobenius isolation lane; isolation is not its remaining obstruction.
- Breakthrough claim: **none**; an isolated Frobenius factor, correct projector, valid
  relation, or recovered toy scalar is not an ECDLP break.

## Falsifiable hypothesis

Let `X/F_p` be a frozen auxiliary cover or higher-genus carrier with an explicitly
identified `E`-isotypic factor, and let `Q=[x]P` lie in a prime-order subgroup of order
`N=p^(1+o(1))`. The rejected proposal asserted that restricting rigid-cohomology
Frobenius to public hash-selected divisor classes would isolate the target `E` factor
and simultaneously produce source-resolving factor-base decompositions with complete
relation collection, linear algebra, and target descent below `N^(1/2)` time and memory.

The ledger already separates and isolates hidden target-isotypic Prym blocks. Therefore
the statement is false as a mechanism-new claim unless the hash restriction constructs
an evaluable divisor correspondence or a new native factorization law; projector
isolation alone is already present and does not imply either operation.

## Mechanism-new operation

The proposed operation was to compute a rigid-cohomology Frobenius matrix, apply a
target-independent polynomial projector onto the `E`-isotypic generalized eigenspace,
and retain only divisor/place columns selected by a frozen public hash. Projected
columns would then be treated as a compressed factor base for relation and descent
queries.

After semantic audit, this is **not mechanism-new**: replacing an exact trace/deck
projector with a rigid-cohomology implementation changes the isolation backend but not
the mathematical carrier, relation source, rank law, or descent map. Hash restriction
is a selector and cannot receive credit unless a theorem proves it preserves complete
source recovery while reducing a recorded exponent.

## Assumptions

- `E/F_p`, `P`, `Q`, `N`, the cover `X`, its maps, and every hash seed are public and
  frozen before target outcomes are inspected.
- Rigid-cohomology precision, denominator growth, field extensions, Frobenius lifts,
  exceptional fibers, and projector reconstruction are exact or independently bounded.
- A projected cohomology vector is not treated as a divisor, point, relation, or scalar
  without an explicit evaluable correspondence and independent replay.
- Factor-base construction, rejected hash columns, relation misses, full rank, target
  descent, verification, and bit memory are charged.
- Any experiment is toy, heuristic, model-bound, and novelty-unverified.

## Semantic fingerprint

`auxiliary_cover | rigid_cohomology_Frobenius | hash_restricted_isotypic_projector | projected_divisor_columns | claimed_relation_and_target_descent`

Collision fingerprint:
`hidden_Prym_E_factor | trace_deck_Frobenius_isolation | no_evaluable_map_or_native_factorization | selector_does_not_remove_obstruction`

## Five closest ledger entries

1. `ledger/H-ISO-001.yaml` — prevents same-field or auxiliary-map structure from being treated as a weak DLP carrier without a new relation operation.
2. `ledger/EV-ISO-001.yaml` — records matched evidence that isogeny structure alone does not change decomposition behavior.
3. `ledger/H-REP-001.yaml` — distinguishes a changed computational representation from a changed solving exponent.
4. `ledger/FINDING-PF-IC-001.md` — requires a complete source-resolving relation and descent path below rho, not only an isolated factor.
5. `ledger/SYNTHESIS-20260716.md` — enforces the toy-versus-cryptographic and correctness-versus-performance boundaries.

## Closest primary literature

- Kedlaya, [Counting points on hyperelliptic curves using Monsky--Washnitzer
  cohomology](https://arxiv.org/abs/math/0105031), supplies a primary algorithmic
  reference for explicit Frobenius action in `p`-adic cohomology; it does not turn an
  eigenspace projector into an ECDLP descent map.
- Harvey, [Kedlaya's algorithm in larger
  characteristic](https://arxiv.org/abs/math/0610973), gives a nearby explicit
  Frobenius-computation framework and its precision/cost obligations.
- Kani and Rosen, [Idempotent relations and factors of
  Jacobians](https://doi.org/10.1007/BF01231534), gives the primary decomposition
  framework closest to isolating isotypic Jacobian factors.

These sources support Frobenius computation and factor isolation, not the proposed
hash-restricted source-recovery theorem. Novelty remains unverified.

## Complete factor-base-to-target-descent path

- Freeze `X`, the map/correspondence data, cohomology basis, precision, projector
  polynomial, divisor representation, factor-base bound, and hash rule.
- Enumerate or construct the factor-base places and compute their exact divisor classes;
  cohomology labels alone are not accepted as factor-base columns.
- Apply the Frobenius projector and hash rule, retaining rejected columns and collision
  multiplicities for accounting.
- For known-scalar random shifts, use a specified native function/divisor operation to
  emit complete factor-base decompositions and independently verify every relation on
  the relevant Jacobian and on `E`.
- Collect enough independent rows to solve every retained factor-base logarithm; include
  projector setup, cover arithmetic, misses, and extension-field work.
- Apply the unchanged operation to `Q+[t]P`, recover explicit divisor/point atoms,
  substitute solved logs, remove `t`, and verify `[x]P=Q`.
- If the projected class cannot be converted to an evaluable correspondence or native
  factorization without solving the original problem, the path terminates before
  relation collection and the duplicate verdict stands.

## Full rho/BSGS cost model

Let the retained factor base have size `B=N^beta`; cohomology/Frobenius/projector setup
cost `N^(a+o(1))` time and `N^(s+o(1))` bits; one complete source-resolving relation
query cost `N^(q+o(1))`; reciprocal verified relation density be `N^(delta+o(1))`;
and one masked-target query have cost/density exponents `q_t,delta_t`. Hash survival is
`N^(-eta)` but cannot be credited unless relation rank and descent remain complete.

- Pollard rho uses `N^(1/2+o(1))` group operations and `N^o(1)` state.
- BSGS uses `N^(1/2+o(1))` time and `N^(1/2+o(1))` stored group elements.
- Projector and hashed factor-base setup cost `N^(a+o(1))` time and
  `N^(max(s,beta-eta)+o(1))` memory.
- Collecting `Theta(N^(beta-eta))` independent rows costs at least
  `N^(beta-eta+delta+q+o(1))`.
- Sparse linear algebra costs `N^(2*(beta-eta)+o(1))` time and
  `N^(beta-eta+o(1))` memory; dense fallback costs exponent `3*(beta-eta)`.
- Complete masked-target descent costs `N^(delta_t+q_t+o(1))`, plus candidate output
  and verification.

Thus the optimistic time exponent is
`lambda=max(a,beta-eta+delta+q,2*(beta-eta),delta_t+q_t)` and bit-memory exponent is
`mu=max(s,beta-eta)`. Promotion would require upper confidence bounds
`lambda<1/2` and `mu<1/2` against both rho and BSGS. If hash restriction reduces rank or
descent probability by its survival factor, `eta` cancels and supplies no asymptotic
gain.

## Likely fatal obstruction

Cohomology realizes the already-known isotypic projector but does not produce an
evaluable homomorphism on divisor representatives, a smoothness law, or atom sources.
Hash restriction discards columns without changing the native relation distribution;
successes and usable rank can fall in the same proportion. Precision and extension
degree may also dominate. The proposal therefore stops at the ledger's existing
isolation milestone and never reaches a new factor-base-to-target descent operation.

## Proof track

To overturn rejection, prove that the hash-restricted projector canonically constructs
an evaluable divisor correspondence or native factorization oracle, prove complete
source lifting, and establish relation rank and masked-target descent with the stated
`lambda,mu<1/2` bounds. The proof must identify a mathematical operation absent from the
existing trace/deck/Frobenius projector.

## Disproof track

Show that the new projector lies in the algebra generated by the existing Frobenius,
trace, and deck operators; that hash restriction scales successes and rank with retained
columns; that projected vectors do not lift canonically to divisors; or that any lift
requires the original decomposition/DLP. Any one confirms the merge/reject verdict.

## Positive and negative controls

- Positive cohomology control: a split Jacobian with a known projector and explicit
  factor maps, verifying matrices, eigenvalues, and precision.
- Positive source control: planted divisors whose factors and pushforward to `E` are
  known independently of the projector.
- Negative projector control: a random same-dimension invariant subspace with matched
  eigenvalue multiplicities.
- Negative hash control: deterministic random column subsets at identical density.
- Mechanism control: the existing trace/deck projector on the same carrier.
- Leakage control: forbid target-conditioned hashes, basis choices, precision, and
  post-hoc column restoration.

## Quantitative promotion and falsification gates

A counterfactual preflight would use at least 24 ordinary toy carriers per size at
10--18 bits, three independent covers/projectors per carrier, exhaustive divisor truth
through 14 bits, and at least 1,000 verified relations plus 100 masked descents at the
largest two sizes. Reconsideration requires zero projector/divisor/source mismatches,
at least 99% planted-source recall, full retained factor rank, at least 95% verified
masked-target recovery, and upper 95% bounds `lambda<=0.45` and `mu<=0.45` with all
precision and rejected columns charged. Falsify if the operator algebra matches the
existing projector, no source-resolving map exists, rank falls with hash survival, or
any lower 95% complete-cost bound reaches `0.50`.

## Artifact plan

- Deduplication proof: `ideas/artifacts/ECDLP-IDEA-051/projector_equivalence.md`
- Frozen matrices: `ideas/artifacts/ECDLP-IDEA-051/frobenius_projectors.jsonl`
- Divisor/source replay: `ideas/artifacts/ECDLP-IDEA-051/source_replay.jsonl`
- Cost worksheet: `ideas/artifacts/ECDLP-IDEA-051/cost_model.json`
- Planned audit runs: `ideas/artifacts/ECDLP-IDEA-051/runs/<run-id>/`
- Required retained data: bases, precision, projector polynomials, hashes, rejected
  columns, divisor lifts, relations, ranks, descents, commands, environment, resource
  metrics, stdout, stderr, and checksums.

## Interpretation boundary

This preserved record is rejected and merged. It is toy, heuristic, model-bound, and
novelty-unverified. Correct cohomology, a projector, an isolated factor, a relation, or a
toy scalar cannot support a breakthrough claim. Only a genuinely new evaluable
correspondence or factorization operation with a complete sub-rho path could justify a
new ID.

## Exactly one next executable action

1. Execute a symbolic projector-equivalence audit on exhaustive 8--12-bit split-cover controls, comparing the hash-restricted rigid-cohomology operator with the algebra generated by the existing trace, deck, and Frobenius projectors; do not run relation collection.
