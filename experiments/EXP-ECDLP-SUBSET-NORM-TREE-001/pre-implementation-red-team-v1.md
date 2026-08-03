# Pre-implementation red-team review v1

## Handoff: subset-norm launch attack

### Claim or task

Try to hide D2/D3 state, oracle decisions, terminal witness work, or an invalid
fixed-curve versus one-instance comparison.

### Status

`OPEN`: `NO-GO` for implementation. Paper-only root-operator derivation may
continue.

### Assumptions

- Explicit D2 leaves and topology are allowed and charged.
- Tier A is fixed-curve online evidence only.
- Tier B and any pipeline claim include terminal witness recovery.
- No universal lower bound against full-rank structured operators is asserted.

### Evidence so far

1. The root operator, displacement equation, rank, storage, and query work are
   undefined.
2. Coordinate translation must cover `Q=O`, `S=O`, `S=Q`, `S=-Q`, and ordinary
   routes.
3. A node bit and D2 leaf do not supply the required D3 witness.
4. Synthetic random D3 support may not have source witnesses.
5. Easy planted leaves and unfair scan order can distort target cost.
6. An exhaustive oracle could secretly choose the path.
7. Extension arithmetic and Tier A/B pipeline costs can be mixed.

An exact Tier B terminal baseline exists: after `S=Q-R`, scan signed factors and
probe `S-P` in the charged D2 dictionary. This costs `Theta(B)` operations and
returns a three-factor witness without D3 advice.

### Failure modes

- Low displacement rank hides a dense embedding or all-level advice.
- Root structure does not restrict compactly to child subsets.
- Streaming all leaves reduces live memory but remains a D2 scan.
- Synthetic support tests operator rank but not relation rank or witness output.
- Tier A online improvement is promoted as a generic or one-instance break.

### Next concrete action

Minimal falsifier: derive only the root-node operator with every translation
branch and count specialization, generators, traffic, and live state. Reject
the family before child construction if it touches `Omega(N2)` target-conditioned
coefficients or drops a branch.

### Artifact paths

- `contract.md`
- `theory.md`
- `object-dimension-ledger.md`

## Coordinator response

The contract now includes the complete translation cover, exact `Theta(B)`
terminal lift, synthetic-null restriction, genuine same-map witness controls,
independent and blinded targets, candidate-generated positive and negative
certificates, base-field extension costs, separate Tier A/B gates, and actual
confidence-sized batches. Implementation remains `NO-GO` because the root
operator and displacement equation are still undefined.
