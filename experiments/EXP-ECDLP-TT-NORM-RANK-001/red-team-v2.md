# Red-team review of v2

## Handoff: complete rank-traffic audit

### Claim or task

Audit the corrected v2 schedule, mutations, independence, workload, rescaling,
and interpretation firewall before implementation.

### Status

`REVISE` with one accounting blocker. Every non-traffic v2 blocker passed.

### Assumptions

- Approval remains limited to a `SANITY_ONLY` semantic diagnostic.

### Evidence so far

- Mutation coverage, exact rescaling schedule, independent paths, static
  rank-field provenance, asymmetric control, workload counts, and
  interpretation firewall passed.
- V2 declared multiplication ceiling `N=c*r*(r+1)/2`, elimination subtraction
  ceiling `E=c*r*(r-1)/2`, and traffic `3N`.
- The aggregate `565377396` base-field-word equivalents was exactly `3N` after
  extension conversion and did not define or charge a complete elimination
  update stream.
- A correct implementation could exceed the false ceiling or omit real
  traffic, so execution remained blocked.

### Failure modes

- Arithmetic counts without an access schedule do not prove memory-traffic
  completeness.

### Next concrete action

Preserve v2 and freeze an implementation-specific access model that charges
materialization, pivot scans, elimination updates, normalization, certificates,
extension width, and metadata.

### Artifact paths

- `execution-matrix-v2.json`
- `execution-matrix-v3.json`
- `rank-traffic-model-v3.md`

