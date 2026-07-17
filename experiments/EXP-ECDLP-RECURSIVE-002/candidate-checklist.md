# ECDLP Candidate Checklist

## Candidate name

Replicated-null recursive coverage calibration.

## Target curve family

- prime field: seeded `p mod 4 = 3`
- curve: prime order, trace not in `{0,1}`, `j not in {0,1728}`
- special cases: supersingular, anomalous, special-j, composite-order, and nonmonotone schedules invalidate a run

## Structure exploited

Coordinate predicates may yield unusually efficient expansion from four-term support advice to eight-term target coverage.

## Factor base and relations

- candidates: x interval, square map, rational union
- controls: 31 random-scalar and 31 random-x bases per curve, plus scalar progression
- size: frozen unordered-occupancy sizing rule, used only to match scale
- relation: eight factor-base points sum to a target through a `4+4` lookup

## Linear algebra and target descent

Not measured. Any percentile pass remains a preflight additive-geometry observation.

## Baselines

- paired empirical null distributions are primary
- rho is measured only as arithmetic scale
- BSGS remains a generic time-memory reference

## Things that kill the idea

- candidate statistics lie inside either null distribution
- support-order permutations change online work by more than 25 percent
- four-term support is not compressed, if a compression claim is attempted
- special curves, hidden bytes/bandwidth, rank, or descent erase the signal

## First experiment

The independently verifiable implementation is frozen. Obtain a pre-run `GO`,
then execute the registered 12-16 bit null calibration through the harness.
