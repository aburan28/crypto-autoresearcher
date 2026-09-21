# Analysis: TYPED-TT-SAMPLED-LOCATOR-V1

## Handoff: sampled predicted-zero locator

### Claim or task

Test whether sampled predicted suffix columns can replace the full suffix
scan in the typed-TT relation transcript.

### Status

OBSERVATION, TOY-EVIDENCE, MODEL-BOUND

### Assumptions

- The committed relation transcript is a public toy fixture, not a deployed
  key-recovery transcript.
- The materialized D4 support in that transcript is the comparison baseline.
- A sampled column budget is useful only if support and rank remain exact.

### Evidence so far

- The full `B^2` budget exactly replays projected `a`-support, valid witnesses,
  and held-out coverage on all eight rows; the verifier also preserves the
  p4027 `source_prf_x` 8/9 rank-deficient control.
- A 32/64 suffix budget on p4027 `random_x` preserves exact support, held-out
  coverage, valid witnesses, and 9/9 relation rank. It evaluates 186,368 of
  372,736 predicted entries and uses 22,632 source point additions versus
  29,568 for the full budget.
- A 16/25 budget on p947 `x_interval` preserves the same checks and evaluates
  28,000 of 43,750 predicted entries. The other p947 rows and p4027 families
  require the full tested budget for exact support; p4027 `source_prf_x` never
  reaches full rank.
- Candidate rows can contain multiple valid `R^4` witnesses for one `a`;
  exactness therefore uses the repository's projected `a`-support contract
  while counting extra valid witnesses separately.

### Failure modes

- Relation support may be sparse in suffix coordinates, making uniform samples
  miss it; this occurred for most tested family/budget pairs.
- A sampled row-space check can pass while the omitted columns contain
  additional zeros or needed independent relations.
- The observed p4027 win is one family on one curve and has no fitted
  asymptotic meaning.
- Full-budget replay may diverge if the transcript or source hashes are not
  bound correctly.

### Next concrete action

Repeat the half-budget result on fresh larger curves and replace uniform
hash-ranked suffix sampling with a target-independent structured selector;
then charge sparse linear algebra and target descent before treating the
signal as more than a locator optimization.

### Artifact paths

- `src/typed_tt_sampled_locator.py`
- `src/verify_typed_tt_sampled_locator.py`
- `tests/test_typed_tt_sampled_locator.py`
