# Isogeny-j-invariant attack decomposition for non-index ECDLP

## Goal

Decompose the isogeny/endomorphism search space into bounded, falsifiable
subproblems that test whether moving between public isogenous models of a curve
changes accessible attack structure for prime-field ECDLP without changing the core
group.

The starting hypothesis is narrow:

- generic prime-order curve groups are fixed by group order;
- rational isogenies can change the curve model (`j`, conductor, model parameters)
  while preserving group size;
- only a small and explicit fraction of public invariants are potentially
  computationally exploitable;
- any claimed benefit must close into an end-to-end Pollard-style search gain and
  pay full preprocessing/transfer cost.

## Relationship to active proposals

This proposal builds directly on:

- `NON-INDEX-ECDLP-II-20260806`, which already established general non-index lanes,
- recent isogeny-transfer audits on Wesolowski-style transfer and class-group
  transfer boundaries,
- and open control failures around special-curve leakage, especially where model
  change is confused with curve change.

This proposal is the **third non-index tranche** and is focused on isogeny-class
structure, not general ML or generic control refinements.

## Hard exclusions

Reject or mark `DOES_NOT_SURVIVE` if any lane:

- relies on a transfer to a non-computable oracle,
- requires hidden scalar-dependent preprocessing not priced into preprocessing or
  end-to-end cost,
- reports a visual/topological/feature discrepancy without algorithmic consequence,
- assumes full isogeny graph traversal at cryptographic size,
- imports supersingular/imaginary methods when the objective statement is ordinary
  prime-field ECDLP unless the transfer model and control scope explicitly switch.

## Subproblem decomposition

### L1 — Isogeny-class control scaffold

Construct an executable corpus that contains triplets `(E, E', φ)` where:

- `E(F_p)` and `E'(F_p)` have the same prime-order subgroup size,
- `E'` is reached by explicit low/medium-degree isogenies (including identity),
- `j(E) != j(E')` and/or visible model parameters differ,
- seeds, coefficients, and transforms are frozen and reproducible.

No lane runs before `L1` succeeds.

### L2 — In-class invariant atlas

Quantify invariance/variability across isogenous representatives for:

- embedding degree, cofactor behavior in the prime subgroup context,
- known special predicates (anomalousness, MOV/GHS-style flags, known small
  torsion-related features),
- easy endomorphism availability probes (CM degree-2/4/8 patterns),
- cheap trajectory statistics under identical seeded point sequences.

Deliverable: a signed list of invariants and non-invariants with confidence bounds.

### L3 — j-invariant steering candidate search

Ask whether `j`-variation within an isogeny class correlates with public
structure changes that can be turned into a predicate. Explicitly test:

- any mapping from `j(E')` to a lower-cost walk policy,
- any predicate on public states whose score changes with isogenous choice and not
  with curve isomorphism in the same class.

Promotion requires overhead-inclusive proof that a concrete search decision changes.

### L4 — Endomorphism transfer stability test

For sampled isogenous representatives, measure:

- transfer cost of moving points/candidates between models,
- whether public endomorphism probes on `E'` translate to `E` without hidden
  scalar leak or inverse-map assumption,
- whether any speedup survives back-translation to the original curve.

This lane is explicitly scoped to “publicly computable and invertible transfer”;
transfer steps that already solve ECDLP are rejected.

### L5 — Adversarial control and null-hypothesis falsification

Construct matched controls so that:

- coordinate randomization alone reproduces observed effects if they are
  coordinate artifacts,
- random-cycle and random-group controls are the null baseline,
- injected-leakage positive controls are detected before any positive claim.

Any lane that is not beat by these controls is scored negative.

## Expected artifact contract

Each lane must output:

- preregistered prediction and null controls,
- deterministic seeds and exact script versions,
- raw per-instance records and summary tables,
- full preprocessing/transfer/memory accounting,
- `SUPPORTED / DOES_NOT_SURVIVE / INCONCLUSIVE / BLOCKED`,
- one-line next-concrete-action to avoid dead-end ambiguity.
