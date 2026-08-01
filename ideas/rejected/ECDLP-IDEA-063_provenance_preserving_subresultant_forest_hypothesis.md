# ECDLP-IDEA-063 — Provenance-preserving subresultant forest

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- State: `rejected_merged`
- Evidence scale: `toy` exact-identity preflight only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Deduplication verdict: exact collision with ledger `ECFG-H669`, `ECFG-NR-1428-SHARED-ROW-NORM-NO-PROMOTION`, and `ECFG-P1428-EXACT-SHARED-UNION-CONTROL`
- Breakthrough claim: **none**; recovering row/root provenance or valid relations is not an ECDLP break.

## Falsifiable hypothesis

For the ledger's exact normalized row-norm family and factor-complement polynomial
`M_F`, a balanced product tree followed by multiplicity-aware subresultant propagation
can recover every `(row, factor-root, source-endpoint)` incidence in
`M(B) polylog(B) + O(I polylog(B))` field operations, where `B=deg(M_F)`, `M(B)` is
polynomial-multiplication cost, and `I` is the emitted incidence count. It never scans
all row/root pairs, preserves repeated-root provenance, emits enough independent rows
for factor-log calibration and masked target descent, and yields complete time and
memory exponents below `1/2` on at least one frozen arm.

## Mechanism-new operation

The proposed operation was a **source-labelled subresultant forest**. At the root, the known
P1428 union polynomial is intersected with `M_F`. The live gcd is then propagated to
both children against their product residues; squarefree, repeated, and shared factors
are separated by subresultant/cofactor certificates. A root-to-leaf path identifies the
row that produced a factor root, and the retained row map lifts it to the original
endpoint source.

A product tree that returns only a union, an independent gcd for every row, a changed
polynomial solver, an explicit row/root table, a dense resultant, or a relation-only
certificate does not implement this operation.

The complete ledger audit shows that the claimed distinction is false: P1428 already
used the balanced modular product/GCD route and recovered all 2,505 row-root incidences
together with source row, sign, factor, and tuple disambiguation. This is therefore a
preserved backend duplicate, not an active mechanism.

## Assumptions

1. `E(F_p)` contains a known prime-order subgroup `<P>` of order `N=p^(1+o(1))`, with challenge `Q=[x]P`.
2. The frozen factor complement `M_F`, normalized row norms, and row-to-endpoint maps reproduce the exact P1428 controls.
3. Product residues can be reduced modulo `M_F` without destroying factor multiplicity or source labels.
4. Shared factors, inseparable factors, zero rows, and exceptional charts have exact certificates and cannot be silently discarded.
5. Tree construction, polynomial arithmetic, all failed queries, output, sparse linear algebra, target descent, verification, and memory are charged.
6. No scalar-indexed table, target-selected tree, post-hoc filter, or explicit pair surface is available.
7. All extrapolations are toy, heuristic, model-bound, and novelty-unverified.

## Semantic fingerprint

`verified_row_norm_family | balanced_modular_product_tree | live_gcd_subresultant_propagation | repeated_factor_provenance | exact_row_root_endpoint_lift | output_sensitive_no_pair_table`

The claimed distinction from P1428 was exact provenance propagation, but the positive
P1428 control already contains source-resolved incidence recovery. The fingerprint is
retained only as a collision key.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H669`, whose hypothesis already names a balanced product/subresultant circuit for exact zero/source recovery.
2. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-P1428-EXACT-SHARED-UNION-CONTROL`, which recovered 2,505 row-root incidences with source-row/sign/factor/tuple disambiguation.
3. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1428-SHARED-ROW-NORM-NO-PROMOTION`, which records the exact non-promotion boundary for the same shared row-norm computation.
4. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H670`, the adjacent source-resolved factor-root incidence backend.
5. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H671`, the adjacent affine root-pencil/source-recovery branch.

## Closest primary literature

- Borodin and Moenck, [Fast modular transforms](https://doi.org/10.1016/S0022-0000(74)80029-2), supplies product/remainder-tree arithmetic, not row provenance for elliptic norms.
- Bernstein, [Scaled remainder trees](https://doi.org/10.1016/j.jalgor.2004.04.009), supplies fast batched remainder propagation, not multiplicity-aware endpoint lifting.
- Semaev, [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031.pdf), supplies the nearby decomposition equations and their source requirement.

No checked source composes these operations into the stated elliptic row/root/source
forest or proves a below-rho pipeline. The composition claim remains novelty-unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N`, a target-independent factor base `F`, its complement polynomial `M_F`, and the verified row-norm generator.
2. Reproduce every row norm, union root, and source map against exhaustive tiny-curve truth.
3. Build the balanced product tree modulo `M_F`, compute the root live gcd, and propagate certified subresultants to leaves.
4. Lift every leaf factor to its row and endpoint sources; independently verify multiplicities and curve additions.
5. Stream source-labelled relations until the factor-base matrix has `B+margin` independent rows, retaining duplicate and failed outputs.
6. Solve factor-base logarithms with the frozen sparse-linear-algebra baseline and verify each calibrated log.
7. Apply the identical forest to randomized targets `Q+[t]P` until a source-labelled descent is found.
8. Substitute factor logs, remove `t`, recover `x`, and independently verify `[x]P=Q`.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` group operations with constant state; BSGS costs
`N^(1/2+o(1))` time and memory. Let `B=N^beta`, target-independent setup cost
`N^a`, successful-query reciprocal density `N^delta`, target-query reciprocal density
`N^delta_t`, forest arithmetic per query `N^phi`, emitted provenance output per query
`N^omega`, sparse linear algebra `N^(2beta+o(1))`, and retained memory `N^mu`.

The fully charged exponents are
`T_rel=max(delta+phi,delta+omega)`,
`T_desc=max(delta_t+phi,delta_t+omega)`, and
`lambda=max(a,T_rel,2beta,T_desc)`. The memory exponent includes the complete tree,
subresultant certificates, row maps, output, and matrix. If factor overlap causes total
live degree or emitted provenance `Omega(B^2)`, then `phi>=2beta` or `omega>=2beta` is
charged rather than hidden. Promotion requires `lambda<1/2` and `mu<1/2`, not merely
quasilinear polynomial arithmetic in `B`.

In the P1428 family there are `R=Theta(B)` input row norms of degree `Theta(B)`, so the
total input degree is `D_in=Theta(B^2)`. Reading, constructing, or propagating the full
input family costs `Omega(D_in)` absent another representation theorem; the draft's
`M(B)` expression incorrectly charged only the complement degree.

## Likely fatal obstruction

The primary obstruction is already historical: P1428 performed the proposed balanced-
product/source-resolution computation and did not promote. More generally, the union
polynomial can be cheap precisely because it forgets which rows share a root.
At high overlap, both children retain the same live factor and recursive provenance
branches into `Theta(B^2)` incidences. Repeated roots may also require per-row local
factorization, while independent emitted relations can remain too sparse. In any of
those cases the forest reconstructs the explicit incidence table and the recorded
rho-or-worse boundary returns.

## Proof track

Prove a multiplicity-aware propagation identity for normalized row norms modulo `M_F`;
bound the sum of live degrees across each tree level; prove exact row/root/endpoint
lifting including shared factors; then bound setup, output, relation rank, target
descent, verification, and memory to obtain `lambda,mu<1/2`.

## Disproof track

Exhibit a false or missed provenance lift, prove `Omega(B^2)` total live degree/output
on the frozen ordinary-curve family, show per-leaf factorization is unavoidable, or
establish `lambda>=1/2` after rank and target descent on every complete-cost arm.

## Positive and negative controls

- Positive primitive control: reproduce P1428 union roots and all exhaustive row/root incidences.
- Positive provenance control: planted polynomials with unique, shared, and repeated factors and known leaf labels.
- Positive ECDLP control: tiny exhaustive source tuples, relation rank, factor logs, and masked target recovery.
- Negative overlap control: every row shares the same live factor, forcing explicit branching to be charged.
- Mechanism control: independent row gcds and a materialized row/root table.
- Leakage control: reject scalar labels, target-selected trees, post-hoc row deletion, and discarded failures.

## Quantitative promotion and falsification gates

No promotion gate remains because the semantic collision rejects this record. The
historical Phase 1 required zero union, multiplicity, row, root, or endpoint mismatches on all
exhaustive instances. Phase 2 uses at least 20 ordinary prime-field curves per size,
three seeds, and `B in {16,32,...,4096}` where feasible. Promotion requires at least
1,000 independently verified relations and 100 target descents at each of the two
largest completed sizes, at least `0.8B` independent rows per accepted collection,
upper 95% forest exponent in `B` at most `1.20+output`, and upper 95%
`lambda,mu<=0.45`, stable under leave-largest-size-out fits.

Falsify the scoped mechanism on any independently reproduced provenance error, lower
95% live-degree or output exponent at least `2` in `B`, fewer than `0.5B` independent
rows at both largest sizes, or lower 95% `lambda>=0.50` in every arm. Timeout, OOM, or
unsupported polynomial arithmetic is infrastructure evidence, not mathematical falsification.

## Artifact plan

- Retired draft contract: `ideas/rejected/contracts/ECDLP-EXP-CONTRACT-063_provenance_forest_preflight.yaml`
- Identity: `ideas/artifacts/ECDLP-IDEA-063/provenance_identity.md`
- Implementation: `ideas/artifacts/ECDLP-IDEA-063/provenance_forest.sage`
- Independent verifier: `ideas/artifacts/ECDLP-IDEA-063/verify_provenance.sage`
- Runs: `ideas/artifacts/ECDLP-IDEA-063/runs/<run-id>/`
- Analysis: `ideas/artifacts/ECDLP-IDEA-063/analysis.md`
- Retain every polynomial, tree node, gcd, subresultant, factor multiplicity, row/source lift, relation, rank, target attempt, command, seed, environment, resource trace, stdout, and stderr.

## Interpretation boundary

This rejected hypothesis remains toy, heuristic, model-bound, and novelty-unverified. Correct
batch gcds, recovered provenance, valid relations, or a toy scalar do not establish a
breakthrough. Only complete independently verified source recovery and all-stage
rho/BSGS accounting can support escalation.

## Exactly one next executable action

1. Preserve this record and `ideas/rejected/contracts/ECDLP-EXP-CONTRACT-063_provenance_forest_preflight.yaml` as the P1428 collision control; do not execute it unless a future proof identifies a source operation absent from the cited P1428 records.
