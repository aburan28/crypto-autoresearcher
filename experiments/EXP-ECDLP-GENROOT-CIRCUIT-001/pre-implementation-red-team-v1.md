# Pre-implementation red-team review v1

## Handoff: generalized-root launch attack

### Claim or task

Try to make the bounded-source circuit pass without a real exact solver or
full-pipeline improvement.

### Status

`OPEN`: `NO-GO` for implementation. Paper-only derivation may continue.

### Assumptions

- Repeated signed factor identifiers are allowed.
- Targets are independent of advice and audit witnesses.
- This verdict does not rule out dedicated generalized-root algorithms.

### Evidence so far

1. Shift, completion, and certificate dimensions were undefined, with no source
   box slack.
2. Raw polynomial solutions were not initially bound to public identifiers.
3. `5^4` planted controls included unreachable right-identity routes.
4. The source-randomization null could alter integer bounds and create a trivial
   lattice advantage.
5. Postselected supported targets and fallback could pass while uniform targets
   failed.
6. Online ratios could pass before actual relation support and rank costs were
   charged.

The feasible left-associated typed language has finite leaves: gate 1 is
`ORD`, `DBL`, or `INV`; a later `LID` occurs exactly after `INV`; `RID` is
unreachable; other finite-input gates are `ORD`, `DBL`, or `INV`.

### Failure modes

- A constant-size addition graph still induces D2-sized or larger solver state.
- Post-hoc registry filtering hides missed or extraneous roots.
- Bound-confounded nulls manufacture a positive coordinate signal.
- Two easy planted targets hide no-hit and uniform-target failures.
- A correct toy solver remains short of relation rank, linear algebra, descent,
  and a sub-rho total.

### Next concrete action

Minimal falsifier: derive one complete lattice recovery inequality at
`T_1=...=T_5=B` and `B=p^(1/5)`, including full-field variables. Reject the
family before implementation if slack is nonpositive.

### Artifact paths

- `contract.md`
- `theory.md`
- `object-dimension-ledger.md`

## Coordinator response

The contract now uses decorated solutions, feasible branch routes, exact
infeasibility sentinels, bound-matched controls, independent uniform targets,
blinded plants, zero fallback on every target, confidence-sized batches, and
support/rank gates. The minimal falsifier was instantiated and failed in
`first-power-box-lattice-negative-v1.md`. Implementation remains `NO-GO`; the
broader generalized-root hypothesis remains open outside that shift family.
