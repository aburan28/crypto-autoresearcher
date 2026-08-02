# Pre-implementation benchmark review v1

## Handoff: generalized-root accounting audit

### Claim or task

Audit the relation-attempt, advice, comparator, and one-instance exponent gates.

### Status

`OPEN`: `REVISE`; `NO-GO` for implementation.

The constant-yield boundary `B^2.5=n^0.5` is correct. Lattice, candidate-list,
completion, certificate, and target-system dimensions remain unknown, and the
original attempt and comparator formulas were incomplete.

### Assumptions

- `n=B^5` and `B` counts signed public factor identifiers.
- `N_j=Theta(B^j)` requires measured collision-light support.
- `epsilon_rel=|D5|/n` uses uniform targets.
- Rank yield may depend on current rank.

### Evidence so far

With `R_req=Theta(B^rho)`, support exponent loss `delta_epsilon`, rank-yield
loss `delta_eta`, and independent attempt cost `B^tau`, relation collection can
fit below rho only if

```text
tau+rho+delta_epsilon+delta_eta < 2.5.
```

A batch law `B^u*A^v` instead needs

```text
u+v*(rho+delta_epsilon+delta_eta) < 2.5.
```

The stationary expectation `R_req/(epsilon_rel*eta)` is not a deterministic
attempt count; execution needs a preregistered confidence budget.

Equal-byte fixed-base BSGS with `m` complete records costs `Theta(m)` offline and
at most `ceil(n/m)-1` giant steps online. Constructive generic preprocessing has
scale `T_G=soft-Theta(sqrt(epsilon_DLP*n/m))` and
`P_G=soft-Theta(sqrt(epsilon_DLP*n*m))`. Both solve a stronger problem.

### Failure modes

- Supported targets replace uniform relation probability.
- Separate support and rank losses are merged into one exponent.
- A finite `0.8x` ratio is called asymptotic compression.
- Candidate bytes and comparator entries are not normalized to complete records.
- Field work or traffic is inserted into the generic `S*T^2` theorem.
- One-target work is divided by a projected batch that was never constructed.

### Next concrete action

Fill every currently unknown solver dimension and re-run this accounting review.
Do not authorize source while an object remains `UNKNOWN`.

### Artifact paths

- `contract.md`
- `object-dimension-ledger.md`
- `notes/ecdlp_relation_preprocessing_accounting_20260718.md`

## Coordinator response

The contract now uses `R_req`, uniform `epsilon_rel`, rank-dependent `eta_r`,
`A_(1-alpha)`, separate exponent losses, exact advice tiers, equal-byte BSGS,
constructive generic preprocessing, actual-batch crossover, and the generic
theorem boundary. The `REVISE` and implementation `NO-GO` remain because solver
and completion dimensions are undefined.
