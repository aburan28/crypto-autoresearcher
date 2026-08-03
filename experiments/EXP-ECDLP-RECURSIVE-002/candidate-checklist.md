# ECDLP Candidate Checklist

## Candidate name

Replicated-null recursive coverage calibration, arithmetic v2 / execution v3.

## Target curve family

- prime field: seeded `p mod 4 = 3`
- curve: prime order, trace not in `{0,1}`, `j not in {0,1728}`
- replication: nine curves over nine distinct field primes
- special cases: supersingular, anomalous, special-j, composite-order,
  repeated-field, and nonmonotone schedules invalidate a run

## Structure exploited

Coordinate predicates may yield unusually efficient expansion from four-term
support advice to eight-term target coverage.

## Factor base and relations

- candidates: x interval, square map, rational union
- controls: 31 random-scalar and 31 construction-matched random-x samples per
  curve, plus mandatory scalar progression
- size: frozen unordered-occupancy sizing rule, used only to match scale
- relation: eight factor-base points sum to a target through a `4+4` lookup
- online model: exact uniform-permutation first-hit expectation per target

## Linear algebra and target descent

Not measured. Any finite-null pass remains a preflight additive-geometry
observation.

## Baselines

- paired independently seeded null samples are primary
- exact uniform-order lookup expectation removes support-order luck
- charged coordinate field costs and group operations are reported separately
- rho is measured only as arithmetic scale
- BSGS remains a generic time-memory reference

## Things that kill the idea

- candidate statistics lie inside either null sample
- shuffled scans disagree with exact expected first-hit work
- any mandatory positive, curve, field, seed, rho, resource, command, or
  verifier-linkage control fails
- charged coordinate arithmetic exceeds the preregistered cost gate
- rank, factor-base logs, linear algebra, or descent later erases the signal

## First experiment

Obtain a third independent pre-run `GO` on the v3 lock/receipt harness and
complete protocol hash set. Then make the approval-only commit, mint and audit
the external lock, and only then execute the 12-16 bit finite-null screen.
