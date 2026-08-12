# Accounting review of v3

## Handoff: independent traffic recomputation

### Claim or task

Independently recompute the v3 rank traffic and check the access-model
assumptions.

### Status

`GO`.

### Assumptions

- Elimination multiplication and subtraction share one fused update pass.
- Scans are monotone, normalization is in place, and swaps are pointer-only.

### Evidence so far

```text
F_p:  P=6183256, E=152824740, N=159007996, T=495573756
F_p2: P=615868,  E=14109700,  N=14725568,  T=46024308
```

Extension conversion gives
`495573756+2*46024308=587622372` base-field-word equivalents, or
`1762867116` cumulative logical bytes at three bytes per base-field word.
This is correctly distinct from peak RSS.

### Failure modes

- Retaining scalars differently or making extra coefficient passes requires
  observed counters and may require a versioned ceiling.

### Next concrete action

Implement phase counters exactly as frozen.

### Artifact paths

- `rank-traffic-model-v3.md`
- `execution-matrix-v3.json`

