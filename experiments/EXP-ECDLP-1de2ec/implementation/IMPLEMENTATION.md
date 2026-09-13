# EXP-ECDLP-1de2ec Stage 1 implementation

Generic keyed-random-function instrument for the approved Stage 1
pilot (`execution_authorized_stages: [0, 1]`). Curve arms (Stage 4)
are not implemented and are not authorized by TASK-20260908-470642.

## Operative parameters

Taken from `specification.yaml` `definitions` and `instrument.generic_walk`:

- `N = 2^24`, `T_BL = 256`, `a = 1/4`, `r = 2`, `k = 4`
- `W = sqrt(a N / T_BL) = 128` (the definition). The cost-model
  `standardized_parameter_sets` row lists `W = 362`; that contradicts
  the definition and is **not** used. Recorded as an observation.
- `cap = 8 W = 1024`
- `f(x) = mix64(x XOR K) mod N` with `mix64` = splitmix64 finaliser
- DP predicate `hash64(x) < floor(2^64 / W)` with an independent key
  (`hash64` is the same finaliser on `x XOR H`)
- selection weight `S_d + 4 W h_d`, seeded tie-break
- seed streams as `seed_policy` (walk key `s`, targets `100+s`,
  tie-break `200+s`, PHI `400+s`)

## Arms

One process per `(seed, arm)` covers that arm's `T_0 × U` (and `phi`)
grid. Arms share the pool and walk at a given seed because the pool is
regenerated from the same tagged streams.

## What this is not

Observations only. `analyze.py` reports frozen comparison statistics
(`T_0(U)` interpolation, F1 ingredients, brackets). It does not judge
support or refutation.
