## Observation

RUN-LHW-e98579 is the Stage 0 execution. Its receipt status is `output_validated`, returncode 0. `stdout.log` and `raw-result.json` both record outcome `O-STAGE0-OK` and stage 0. `raw-result.json` also records `twin_ok` true, `row_count` 6, `claims.break` false, and `claims.exponent_move` false. The archived frontier table has six rows and `twin_ok` true.

RUN-LHW-9ccf77 is the Stage 1 execution. Its receipt status is `claim_expired`, returncode null, and `scientific_conclusion` null. `stdout.log` and `stderr.log` are empty. `raw-result.json` is absent. `experiments/EXP-LHW-b49bc6/stage1/` is absent. `RESULTS.md` is absent. `manifest_v2.yaml` records status `failed_infrastructure`, `failure_class` `infrastructure_error`, `result.outcome` null, `result.valid` false, and `certificate.kind` none. The manifest states that `claim_expired` is not a scientific O-* label. The receipt spans 10730.21272 seconds, from `2026-10-03T17:39:58.803532+00:00` to `2026-10-03T20:38:49.016252+00:00`, and `expires_at` is `2026-10-03T20:38:49+00:00`. The manifest labels that span as the claim TTL stop and sets `measured_not_scientific` true.

A replay of `python3 implementation/run.py --stage 0` in `/tmp/review-lhw-b49bc6` returned outcome `O-STAGE0-OK`, `twin_ok` true, and `row_count` 6. That replay wrote under `/tmp` only.

## Comparison

The binomial coefficients and the two primes were computed before `implementation/`, `stage0/`, and `runs/` were opened.

| cell (m, w) | C(m, w) |
| --- | --- |
| (20, 2) | 190 |
| (20, 3) | 1140 |
| (20, 5) | 15504 |
| (24, 3) | 2024 |
| (24, 4) | 10626 |
| (24, 6) | 134596 |

The least prime strictly greater than `2^{22}` is 4194319. The least prime strictly greater than `2^{26}` is 67108879.

The archived `stage0/frontier-table.json` matches those eight integers. On every row, `binom_a`, `binom_b`, and `binom_freeze` equal C(m, w), and `l_a`, `l_b`, and `l_freeze` equal 4194319 when m is 20 and 67108879 when m is 24. `routes_agree` is 1 on all six rows. The replay table under `/tmp/review-lhw-b49bc6/stage0/` carries the same integers. `H-LHW-e54b1b` names the same eight integers; that file was opened only after the computation.

Stage 0 stdout and `raw-result.json` agree on `O-STAGE0-OK`. Stage 1 has no raw result and no O-* label in stdout. This package does not re-run EXP-LHW-44a6ec.

## Inference

Stage 0 holds as an integer freeze. The dual-route binomials and the wrap-exclusion primes agree with an independent computation, and the temp-directory replay returns `O-STAGE0-OK` with `twin_ok`.

Stage 1 is an infrastructure stop. `claim_expired` is not negative evidence and is not an E1 or E2 observation. `H-LHW-e54b1b` names that stop `O-IMPEDIMENT`. No sumset cardinality was persisted, so the E1/E2 discriminator was not measured. The evidence direction is neutral and the strength is inconclusive. The hypothesis stays `approved`. The experiment status `failed_infrastructure` records the Stage 1 claim TTL stop.

An empty Stage 1 stdout is not a sumset bound. Claim TTL expiry is not evidence against E2. The Stage 0 binomial freeze is not an E1 result.

## Limitation

The tested field degrees are the toy values m in {20, 24}. Nothing here transfers to cryptographic m. Stage 1 is unmeasured. This is not a rerun of EXP-LHW-44a6ec. The 10730-second receipt span is the claim TTL, not a counted walk. One coordinator task owned joints J1, J2, and J3 under addendum PD-1. No separate validator session and no red-team session ran. No sumset count from this package is reported as a measurement.
