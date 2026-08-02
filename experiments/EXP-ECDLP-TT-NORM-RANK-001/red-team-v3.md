# Red-team review of v3

## Handoff: narrow traffic audit

### Claim or task

Verify that v3 closes the final rank-traffic accounting blocker.

### Status

`GO`. No concrete pre-implementation blocker remains for the frozen
`SANITY_ONLY` experiment.

### Assumptions

- Approval applies only to the declared incremental row basis and transposed
  column basis. A different access pattern requires a new version.

### Evidence so far

- Independent derivation confirmed `P=c*r`, `E=c*r*(r-1)/2`, `N=E+P`, and
  `T=3E+6P`.
- All 288 rank jobs aggregate to `495573756` `F_p` words and `46024308`
  `F_p2` words, or `587622372` base-field-word equivalents.
- The model covers materialization, monotone scans, fused updates,
  normalization, and certificate reads.
- It separately enforces pointer-only swaps, metadata accounting, observed
  phase counters, and invalidation on a ceiling overrun.

### Failure modes

- Nonmonotone scans, coefficient-row copies, missing phase counters, or a
  different rank implementation invalidate this approval.

### Next concrete action

Record coordinator approval of the exact v3 bundle for implementation.

### Artifact paths

- `rank-traffic-model-v3.md`
- `execution-matrix-v3.json`
- `contract-v3.md`
- `specification-v3.json`

