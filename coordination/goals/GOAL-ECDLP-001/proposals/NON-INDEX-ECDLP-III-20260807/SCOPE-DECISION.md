# Scope decision — isogeny-class decomposition (with j-invariant/endomorphism focus)

## Decision

Admit a dedicated non-index tranche focused on isogeny-class micro-structure for
ordinary prime-field ECDLP. The proposal is narrowly scoped to public model
switching among explicit isogenous curves and to any resulting measurable search
advantage or definitive scope closure.

## Scope in

- explicit generation of isogenous representatives with frozen scripts and seeds,
- invariance maps across isogenous models,
- j-invariant and model-parameter effect on public observables,
- endomorphism probes whose derivation and use remain public and invertible,
- full accounting of transfer/preprocessing/failed-path costs,
- matched null models and injected-leakage controls.

## Scope out

- any claim that assumes access to hidden group secret or scalar label,
- any lane claiming asymptotic complexity without a finite artifact and
  explicit success-to-cost decomposition,
- full isogeny-graph search to cryptographic size,
- supersingular-only claims without explicit branch and explicit cost separation,
- topology/spectrum diagnostics without algorithmic use.

## Stage protocol

### Stage 0 — executable scope freeze

1. Fix curve families, prime sizes, subgroup basis, seeds, and transfer budget.
2. Freeze what is measured as “special structure” before running positive controls.
3. Register failure conditions for each lane in advance.

### Stage 1 — invariant ledger construction

1. Generate isogenous triples `(E, E', φ)` under explicit degree caps and
   transfer budgets.
2. Publish a ledger of invariants/non-invariants for `L1` and `L2`.
3. Pre-register a null model for coordinate-isomorphic, random-cycle, and random-group
   baselines.

### Stage 2 — bounded hypothesis tests

1. For each lane `L3` and `L4`, run replicated instances across seeds, primes,
   and held-out generators.
2. Correct for multiple comparisons on feature families.
3. Gate promotion on overhead-inclusive normalized advantage versus randomized control.

### Stage 3 — adversarial audit

1. Independent leakage and finite-size controls,
2. hidden preprocessing and memory-cost challenge,
3. transfer-invertibility check and disguised reduction check.

### Stage 4 — transition decision

- `SUPPORTED` only if the lane yields an end-to-end search advantage or strong
  negative with explicit scope closure.
- `DOES_NOT_SURVIVE` if null baselines match or if transfer cost dominates.
- `BLOCKED` only on infrastructure limits after all controls and attempts are
  immutably recorded.
- `INCONCLUSIVE` if controls are valid but evidence cannot discriminate outcomes.
