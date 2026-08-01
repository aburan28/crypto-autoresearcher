# ECDLP-IDEA-020 — Cartier differential-syndrome descent

## Status and claim labels

- Class: `algorithm`
- Risk band: `high-risk`
- State: `proposed_unapproved`
- Evidence scale: `toy` preflight only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a differential identity or decoded planted residue set is not a break.

## Falsifiable hypothesis

For a factor base `F` of size `B=N^beta`, a divisor `D=sum P_i-R-(m-1)O` can be encoded
by a third-kind differential whose Cartier iterates give a public syndrome. A frozen sparse
decoder recovers the factor-base support in sublinear work in `B`, and the complete
relation/base-log/target-descent exponent is below `1/2`.

## Mechanism-new operation

Convert the Abel–Jacobi condition to residues of a logarithmic differential and apply
**Cartier-iterate sparse syndrome decoding**. This is not idea 007's S-unit support search,
idea 012's aggregate divisor intersection, or another polynomial solver: the predicted new
information is a Frobenius-semilinear syndrome with recoverable residue locations.

## Assumptions

1. `E/F_p` contains `<P>` of prime order `N≈p`, and `Q=[x]P`.
2. The target syndrome is computable from `R` without knowing the support it must decode.
3. Differential residues, poles, exact-form ambiguity, and Cartier normalization are explicit.
4. The decoder returns all points/signs/multiplicities and every miss is charged.
5. Precomputation, semilinear algebra, verification, and memory are included.
6. Toy extrapolation is heuristic, model-bound, and novelty-unverified.

## Semantic fingerprint

`third_kind_differential | factor_base_residue_dictionary | Cartier_iterate_syndrome | sparse_Abel_Jacobi_support_decoder`

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — the support-search and membership-quotient obstruction.
2. `ledger/H-FB-001.yaml` — prevents the residue dictionary alone from counting as new.
3. `ledger/EV-FB-001.yaml` — supplies the matched relation-yield control.
4. `ledger/H-REP-001.yaml` — distinguishes a semilinear syndrome from a coordinate rewrite.
5. `ledger/SYNTHESIS-20260716.md` — requires full rho/BSGS comparison.

## Closest primary literature

- Cartier, [Sur l'acyclicité du complexe des formes différentielles](https://www.numdam.org/item/ASNSP_1962_3_16_1_45_0/), supplies the Cartier/de Rham operation.
- Tate, [Residues of differentials on curves](https://www.numdam.org/item/10.24033/asens.1162.pdf), supplies the residue formalism.
- Kedlaya, [Counting points using Monsky–Washnitzer cohomology](https://arxiv.org/abs/math/0105031), is the nearby computational Frobenius boundary.

The sources do not construct the proposed prime-to-`p` ECDLP support syndrome. Novelty
remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `F`, a differential basis, residue dictionary, Cartier depth, and exact-form quotient.
2. Precompute every factor-base signature and validate it under coordinate changes.
3. For `R=[a]P+[b]Q`, compute the public target syndrome and decode every candidate support.
4. Verify each supported divisor and group relation, then collect enough independent rows.
5. Solve factor-base logarithms and run the unchanged syndrome decoder on `Q+[t]P`.
6. Substitute base logs, recover `x`, and verify `[x]P=Q`.

## Full rho/BSGS cost model

Let build cost be `N^c`, one syndrome/decoder attempt `N^u`, reciprocal relation and target
densities `N^delta,N^delta_t`, verification `N^v`, sparse-LA exponent `omega_s*beta`, and
storage `N^s`. Rho is `N^1/2` time with negligible memory; BSGS is `N^1/2`
time/memory. The proposal has
`lambda=max(c,beta+u+delta,omega_s*beta,u+delta_t,beta+v)` and
`mu=max(s,beta)`. Differential construction from a guessed support is charged as circular,
not as a successful query.

## Likely fatal obstruction

Cartier/de Rham information is `p`-primary and finite-dimensional, while the cryptographic
subgroup has order `N!=p`; it may be blind to the relevant divisor class. Constructing the
third-kind differential can already require its pole/support locations. Any surviving
signature may therefore be a tautology or the original decomposition in disguise.

## Proof track

Define the syndrome functorially from `R`, prove its dependence on the unknown support is
sparse and invertible, and bound all costs to obtain `lambda,mu<1/2`.

## Disproof track

Prove the syndrome factors through a `p`-primary quotient and vanishes/collides on `<P>`,
show target construction requires support, or fit full cost at or above rho.

## Positive and negative controls

- Positive control: planted logarithmic differentials with known residues and poles.
- Positive instrumentation control: exhaustive divisor/differential agreement on tiny curves.
- Negative control: prime-to-`p` subgroup points with randomized support labels.
- Mechanism controls: Miller S-unit and aggregate-support queries on identical targets.
- Lift/coordinate control: all valid differential basis changes.

## Quantitative promotion and falsification gates

Use 10–24-bit prime-order groups, at least 50 curves per size, Cartier depths `1–6`,
`m in {3,4}`, and exhaustive truth through 17 bits. Promotion requires zero wrong
supports, 99.9% syndrome agreement, 1,000 relations and 100 descents at each of the two
largest sizes, upper 95% `u+delta<=0.20`, `u+delta_t<=0.45`, `lambda<=0.45`, and
`mu<=0.45`. Falsify if all prime-to-`p` syndromes collide/vanish, target syndrome requires
the support, one accepted support is wrong, or every full-cost lower bound reaches `0.50`.
Arithmetic implementation failures are not mathematical negatives.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-020/preflight_spec.yaml`
- `ideas/artifacts/ECDLP-IDEA-020/cartier_syndrome.sage`
- `ideas/artifacts/ECDLP-IDEA-020/runs/<run_id>/manifest.yaml`
- `ideas/artifacts/ECDLP-IDEA-020/runs/<run_id>/differentials.jsonl`
- `ideas/artifacts/ECDLP-IDEA-020/runs/<run_id>/supports.jsonl`
- `ideas/artifacts/ECDLP-IDEA-020/analysis.md`

## Interpretation boundary

All observations remain toy, heuristic, model-bound, and novelty-unverified. Differential
correctness or a residue certificate is not an ECDLP improvement.

## Exactly one next executable action

1. Implement the public-target versus oracle-support Cartier-syndrome ablation on exhaustive 10–17-bit curves.
