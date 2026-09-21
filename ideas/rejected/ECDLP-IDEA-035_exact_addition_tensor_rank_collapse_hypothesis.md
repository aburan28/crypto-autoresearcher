# ECDLP-IDEA-035 — Exact addition-law tensor-rank collapse

## Status and claim labels

- Class: `algorithm`
- Risk band: `high-risk`
- State: `proposed_unapproved`
- Evidence scale: `toy` exact-rank preflight only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; contracting a toy circuit or finding a low-rank approximation is not an ECDLP break.

## Falsifiable hypothesis

The complete double-and-add relation `Q=[x]P`, booleanized with exact elliptic addition
constraints and compiled in a frozen bit order, has elliptic-specific exact middle-cut
rank `chi=N^(beta+o(1))` with `beta<1/(2 omega_T)`.  A target-independent exact tensor
factorization can then contract the witness network, recover every bit of `x`, and verify
the original target in time and bit memory below exponent `1/2`.

## Mechanism-new operation

The only proposed new operation is an **exact structural rank-collapse theorem for the
elliptic addition tensor**, uniform over ordinary prime-order curves and absent from
matched random cyclic circuits. Generic tensor-network contraction, SAT, Groebner bases,
approximate truncation, a different variable order chosen after seeing `Q`, or another
solver substitution is only a control and is a duplicate under the ledger. This record
survives only if the elliptic law itself removes the recorded state-space obstruction.

## Assumptions

1. A complete addition-law system, bit encoding, auxiliary field, cut order, and exact arithmetic are frozen independently of `Q` and `x`.
2. All selector bits, denominators, exceptional cases, and field-equation constraints are included.
3. The factorization and contraction are exact; numerical or lossy low rank cannot support a scalar claim.
4. Factor discovery, coefficient bit lengths, target insertion, back substitution, and all candidate branches are charged.
5. The rank advantage must persist against matched generic cyclic and randomized-addition controls.
6. Scaling claims remain toy, heuristic, model-bound, and novelty-unverified.

## Semantic fingerprint

`complete_elliptic_addition_circuit | exact_boolean_tensor_network | uniform_middle_cut_rank_collapse | witness_scalar_contraction`

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — the relation baseline whose solver bottleneck cannot be hidden by recompilation.
2. `ledger/H-REP-001.yaml` — distinguishes a new exact tensor object from a coordinate-only rewrite.
3. `ledger/EV-REP-002.yaml` — requires orientation, normalization, and hidden-state branches to be retained.
4. `ledger/H-FB-001.yaml` — supplies the relation-base and linear-algebra accounting boundary.
5. `ledger/SYNTHESIS-20260716.md` — enforces complete descent and matched rho/BSGS promotion.

## Closest primary literature

- Bosma and Lenstra, [Complete systems of two addition laws for elliptic curves](https://doi.org/10.1006/jnth.1995.1088), proves the complete algebraic addition-law boundary that the exact circuit must encode.
- Oseledets, [Tensor-Train Decomposition](https://doi.org/10.1137/090752286), develops tensor-train ranks and contractions; its algorithms do not give the required elliptic-specific exact rank theorem.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://doi.org/10.1007/3-540-69053-0_18), supplies the generic-group boundary that a representation-specific rank theorem would have to escape.

No checked source proves a uniform sub-square-root exact cut-rank bound for inversion of an
elliptic scalar-multiplication circuit. Novelty is unverified, not established.

## Complete factor-base-to-target-descent path

Here the replacement factor base is the frozen set of local tensors for field equations,
complete addition-law selectors, and scalar-bit transitions.

- Compile the target-independent scalar-multiplication circuit and certify equivalence to the complete elliptic addition relation.
- Factor every local constraint exactly and prove the declared cut-rank bounds without using target labels.
- Insert public `P,Q` boundary tensors only after the factorization and contraction order are frozen.
- Contract forward and backward messages exactly, retaining every nonzero witness branch.
- Back-substitute the scalar bits and enumerate the complete residual witness list.
- Accept only candidates satisfying `[x]P=Q` on the original curve.

## Full rho/BSGS cost model

Let compilation and exact factor discovery cost `N^c`, reciprocal applicability be
`N^zeta`, maximum exact bond dimension be `chi=N^beta`, auxiliary-field degree and
coefficient precision contribute `N^(phi+h)`, contraction exponent be `omega_T`,
residual witness multiplicity be `N^u`, back substitution be `N^b`, verification be
`N^v`, and other bit memory be `N^s`. Pollard rho costs `N^(1/2+o(1))` time with
negligible group storage; BSGS costs `N^(1/2+o(1))` time and memory. The proposed exact
network costs time exponent
`lambda=max(zeta+c,omega_T*beta+phi+h,u+b+v)` and bit-memory exponent
`mu=max(s,2*beta+phi+h,u)`. Construction of every exact factor, repeated contraction for
bit recovery, and output of all witnesses are included. Any uncharged `N^(1/2)` boundary
table or target-specific rank decomposition fails the model.

## Likely fatal obstruction

Across a middle cut, distinct partial scalars can induce distinguishable curve states, so
the exact communication/Hankel rank may be `Omega(sqrt(N))` or larger in every useful
ordering. Complete selectors can increase rank, and approximate tensor compression loses
the unique witness guarantee. In that case the method is simply an expensive exact solver
substitution and must be rejected as a duplicate/control.

## Proof track

Give a uniform target-independent decomposition of the complete elliptic addition tensor,
prove exact rank `N^beta` with `omega_T*beta<1/2` and `2 beta<1/2`, and prove exact witness
recovery with sub-square-root factor construction, field, ambiguity, and memory costs.

## Disproof track

Prove a fooling-set, communication-rank, or Hankel-rank lower bound of
`N^(1/2-o(1))` for every target-independent useful cut, or show the same rank profile on
matched generic cyclic circuits and therefore no elliptic-specific operation.

## Positive and negative controls

- Positive control: a planted low-rank reversible addition circuit with one known witness.
- Positive instrumentation control: exhaustive exact truth tensors for tiny elliptic curves.
- Negative control: random cyclic-group addition circuits with matched state and bit sizes.
- Structural control: randomized complete addition laws and preregistered variable orders.
- Approximation control: compare exact rank with numerical truncation, but forbid approximate results from scalar recovery claims.
- Leakage control: hash factors and cut orders before `Q` is inserted.

## Quantitative promotion and falsification gates

The toy gate measures exact ranks over two auxiliary prime fields on deterministic curves
through order 257. Promotion only to a scaling contract requires zero missing or false
witnesses, target-independent factors, a rank advantage of at least `4x` over both matched
controls on at least 90% of cells, and upper 95% `beta<=0.15`, `phi+h<=0.15`,
`lambda<=0.45`, and `mu<=0.45`. Falsify if any exact witness is lost, ranks depend on
the target-selected order, elliptic/control ranks agree within `20%`, or the lower 95%
bound for `beta`, `lambda`, or `mu` reaches `0.50`.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-035/preflight_spec.yaml`
- `ideas/artifacts/ECDLP-IDEA-035/exact_addition_tensor.sage`
- `ideas/artifacts/ECDLP-IDEA-035/runs/<run_id>/manifest.yaml`
- `ideas/artifacts/ECDLP-IDEA-035/runs/<run_id>/rank_profiles.tsv`
- `ideas/artifacts/ECDLP-IDEA-035/runs/<run_id>/witnesses.jsonl`
- `ideas/artifacts/ECDLP-IDEA-035/runs/<run_id>/costs.tsv`
- `ideas/artifacts/ECDLP-IDEA-035/analysis.md`

## Interpretation boundary

All evidence remains toy, heuristic, model-bound, and novelty-unverified. A correct circuit,
an exact toy contraction, or a low numerical rank is not a breakthrough. Without a uniform
elliptic-specific exact rank theorem and complete sub-rho target recovery, the approach is
classified as a solver substitution and rejected.

## Exactly one next executable action

1. For every prime `p<=257`, compile the lexicographically first ordinary prime-order curve's complete scalar-multiplication relation in the frozen MSB-first order and compute its exact middle-cut ranks over `F_2` and `F_3` against matched cyclic and randomized-addition controls.
