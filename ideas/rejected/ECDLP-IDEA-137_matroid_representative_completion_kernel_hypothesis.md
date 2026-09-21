# ECDLP-IDEA-137 — Matroid-representative completion kernel

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- Top lane: `-`
- State: `merged_rejected_hidden_completion_matroid`
- Cohort: `20260717-h`
- Evidence scale: semantic/theorem audit only; no experiment ran
- Contract posture: no contract; execution is not authorized
- Scale labels: prospective tests are `toy`; costs are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a small representative family or valid source tuple is not an ECDLP break.

## Falsifiable hypothesis

Partial factor-base sums can be embedded as independent sets of a public low-rank linear matroid so that a `q`-representative subfamily preserves every completion to every elliptic target. Iterative representative-family reduction then retains exact source provenance while shrinking the three-source frontier below the five-source rho gate.

## Mechanism-new operation

The proposed operation is **completion-preserving matroid kernelization of partial elliptic sums**. Each source-labelled partial tuple maps to a matroid set; representative-set reduction discards a tuple only when another extends through every permitted remaining source set and target condition.

After audit this is merged/rejected because the required public matroid is the missing source/completion oracle. Encoding partial sums by their scalars uses the DLP; encoding only public point coordinates has no proved matroid independence law matching elliptic completion; and a universal completion relation can distinguish essentially every provenance state. Applying representative-set algorithms after an extension matroid or all partial tuples are supplied is a backend overlapping IDEA-073, IDEA-082, IDEA-120, and P1477.

## Assumptions

1. Public `E,<P>,N,Q,F` and `B=N^beta` are fixed, with arity five and complete sign/exception semantics.
2. A public linear matroid of rank `r=N^kappa` represents exact extendibility without scalar labels or enumerated target fibers.
3. Representative-family construction begins before the `B^3` frontier and preserves ordered source labels and multiplicity.
4. The same frozen reduction works for known-log relations and fresh masked targets.
5. Matroid construction, field representation, all discarded states, output, rank, factor logs, descent, and memory are charged.

## Semantic fingerprint

`partial_elliptic_source_sets | public_linear_completion_matroid | q_representative_family | universal_target_extendibility | exact_provenance_kernel | blind_descent`

A genuine public completion matroid would be new. Representative-set reduction on a supplied completion oracle or hidden scalar embedding is the rejected duplicate.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `P1434`, the unresolved public source-fiber generator that the proposed matroid representation silently requires.
2. `ledger/FINDING-PF-IC-001.md` — imported `P1476`, the complete five-source exponent boundary the representative frontier must beat.
3. `ledger/FINDING-PF-IC-001.md` — imported `P1477`, whose source-distinct partial states grow past the gate.
4. `ledger/FINDING-PF-IC-001.md` — imported `P1479`, showing true factor logs are outside tested public low-dimensional linear feature spaces.
5. `ledger/FINDING-PF-IC-001.md` — imported `TRANSFER-NR-043`, where Abel–Jacobi completion labels match random/relabelled controls and do not supply non-generic source concentration.

## Closest primary literature

- Fomin, Lokshtanov, Panolan, and Saurabh, [Efficient Computation of Representative Sets with Applications in Parameterized and Exact Algorithms](https://arxiv.org/abs/1304.4626), give algorithms after a linear matroid and candidate family are supplied.
- Lokshtanov, Misra, Panolan, and Saurabh, [Deterministic truncation of linear matroids](https://doi.org/10.1145/3170444), preserve matroid structure but do not construct elliptic completion matroids.
- Wahlström, [Representative set statements for delta-matroids and the Mader delta-matroid](https://arxiv.org/abs/2306.03605), broadens the representation framework, not the missing group/source embedding.

No checked source gives the required public completion representation. Novelty remains unverified, but the present hypothesis assumes its key oracle.

## Complete factor-base-to-target-descent path

1. Freeze public inputs, source encoding, matroid representation, reduction order, and verifier.
2. Generate one- and two-source independent sets directly from `F`; reduce them while preserving all three-source/target extensions.
3. Extend and reduce to a source-complete five-relation kernel for each known-log target; decode and verify every tuple.
4. Collect rank-`B` rows, solve and verify factor logs.
5. Apply the unchanged kernelization to fresh masked targets, enumerate all scalar candidates, and accept only `[x]P=Q`.
6. Charge matroid construction, candidate generation, reductions, output, rank, linear algebra, descent, and memory.

## Full rho/BSGS cost model

Rho and BSGS both have `N^(1/2+o(1))` time; BSGS also has that memory. Let matroid setup/memory be `N^a,N^a_m`, rank `N^kappa`, frontier construction/query time and working memory `N^q,N^q_m`, inverse densities `N^delta,N^delta_t`, source output `o`, ambiguity `u`, and linear algebra `N^ell,N^ell_m`. Then

`lambda=max(a,beta+delta+q+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,kappa,q_m,beta+o,ell_m,u)`.

Thus `lambda` is the complete time exponent and `mu` is the complete peak-memory exponent.
Candidate families consumed by the representative algorithm are part of `q`; they cannot be omitted. Toy kernel sizes are model-bound.

## Likely fatal obstruction

Representative sets preserve extension only relative to a supplied matroid. Elliptic target completion is an affine group equation, not public linear independence. The natural `F_N` scalar representation is exactly the hidden discrete logarithm; public coordinate representations do not make addition completion matroidal. A universal matroid rich enough to distinguish every target and source word may have full state rank or require enumerating the frontier first.

## Proof track

Construct the public matroid and prove a biconditional between matroid extension and exact elliptic completion, source recovery, and full `lambda,mu<=0.45` without scalar coordinates or a prebuilt frontier.

## Disproof track

Show the representation uses hidden scalars, assumes an extension oracle, consumes all `B^3` candidates, loses provenance, or requires `lambda>=1/2` or `mu>=1/2`. The current specification is already rejected by the missing-matroid reduction.

## Positive and negative controls

- **Positive control:** graphic/linear matroid path problems with supplied representations and independently known representative families.
- **Positive control:** exhaustive tiny scalar-labelled cyclic groups, explicitly marked as hidden-coordinate controls.
- **Negative control:** public point-coordinate embeddings, random group tables, arithmetic-matroid rank, and P1477 state frontiers.
- **Negative control:** shuffled source labels and matched completion multiplicities.
- **End-to-end control:** rho/BSGS and blind targets with matroid setup charged.

## Quantitative promotion and falsification gates

This record is rejected at the supplied/hidden completion-matroid scope. A new ID requires an explicit public matroid biconditional and independently proved `lambda,mu<=0.45`. Falsify any successor on one lost completion, scalar-labelled column, pre-enumerated `B^3` family, post-hoc source recovery, or complete exponent at least `0.5`.

## Artifact plan

- Missing-matroid reduction: `ideas/artifacts/ECDLP-IDEA-137/completion_matroid_reduction.md`
- Prospective representation theorem: `ideas/artifacts/ECDLP-IDEA-137/public_completion_matroid.md`
- Frozen controls: `ideas/artifacts/ECDLP-IDEA-137/fixtures.json`
- Complete cost receipt: `ideas/artifacts/ECDLP-IDEA-137/cost_analysis.md`

These are prospective paths only.

## Interpretation boundary

This is rejected, novelty-unverified evidence. Any future finite data are toy; extrapolations are heuristic and model-bound. Matroid kernelization correctness does not establish a source oracle, below-rho algorithm, or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-137/completion_matroid_reduction.md` formalizing where the proposed linear matroid representation assumes hidden scalars, a supplied extension oracle, or the full partial-tuple family.
