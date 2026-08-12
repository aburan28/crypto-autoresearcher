# Red-Team Review: TYPED-TT-SAMPLED-LOCATOR-V1

- The full-budget run is only a replay control; it does not establish a new
  algorithm.
- Support recall must be compared with the materialized D4 support, not only
  with sampled row-space identities.
- A hit count is insufficient: every candidate witness must be valid, false
  positives must be counted, and relation rank must be recomputed.
- The p4027 `source_prf_x` rank failure must remain visible rather than being
  averaged away.
- Any sub-full exact result is still a fixed toy-fixture observation; source
  cache savings, matrix work, descent, and rho must remain in the boundary.
- The p4027/random_x half-budget result is a candidate optimization signal,
  not a general selector: it must replicate on fresh curves and survive full
  end-to-end accounting.

## Handoff

### Claim or task

Audit whether sampled suffix prediction can preserve relation support.

### Status

NEGATIVE RESULT with one positive family-specific signal

### Assumptions

- The transcript's baseline hits and scalar labels are immutable evidence.

### Evidence so far

- Full-budget replay is exact across eight rows.
- p4027/random_x is exact at 32/64 columns; p947/x_interval is exact at
  16/25 columns; most other sub-full budgets miss projected support or rank.

### Failure modes

- Uniform sampling can miss sparse support and undercount relation rank.

### Next concrete action

Replicate the two sub-full signals on fresh ordinary curves and compare a
structured suffix selector against the hash-ranked selector.

### Artifact paths

- `RUN-001/raw-result.json`
- `RUN-001/verification.json`
