# TASK-20260904-4c0d7d — Validator recomputation tables (V1–V4)

Every number below was produced by the scripts in this directory from the
committed snapshot of `experiments/EXP-PFDR-fd901a/` (run package first added
in commit `1b49d491`, an ancestor of the PR #713 merge `dfab9e6e` and of HEAD
`6468b25e`; `git status` clean for that path). No producer record was edited.

## V1 — run-set validity, manifest schema, seed and prime integrity

Source: `v1_check.py` → `v1_check_output.json`.

| run | files | checksums.sha256 | status | commit | dirty | command==command.txt | stderr bytes |
|---|---|---|---|---|---|---|---|
| RUN-PFDR-fd901a-fixture-p4099 | 6/6 + sidecar | 6/6 match | completed_valid | 3a9c1b02 | false | yes | 0 |
| RUN-PFDR-fd901a-posctrl-p4099 | 6/6 + sidecar | 6/6 match | completed_valid | 3a9c1b02 | false | yes | 0 |
| RUN-PFDR-fd901a-posctrl-p16411 | 6/6 + sidecar | 6/6 match | completed_valid | 3a9c1b02 | false | yes | 0 |
| RUN-PFDR-fd901a-sweep-p4099 | 6/6 + sidecar | 6/6 match | completed_valid | 3a9c1b02 | false | yes | 0 |
| RUN-PFDR-fd901a-sweep-p64 | 6/6 + sidecar | 6/6 match | completed_valid | 3a9c1b02 | false | yes | 0 |
| RUN-PFDR-fd901a-sweep-p256 | 6/6 + sidecar | 6/6 match | completed_valid | 3a9c1b02 | false | yes | 0 |

Cross-run identity (all six manifests):

| item | value | identical across the six |
|---|---|---|
| `code.commit` | 3a9c1b0257923bf7772b811963beaf57d67aa713 (real commit, 2026-09-03 20:13:47Z) | yes |
| `run_experiment.py` sha256 | cf3051de7079f091ab3c0306b6fac8050d36c2f2f3663b11b6058e7839a4d20e | yes |
| meter per-file sha256 (11 paths) | equal to `harness/macaulay_fp/VALIDATION.md` §1 and to the working tree today | yes |
| `meter.snapshot_commit` | 2d2083e5 (real commit) | yes |
| `selftest_in_this_lineage` | returncode 0, "52 passed" | yes (only the wall-clock seconds differ) |
| `environment.json` | sha256 11f48467…, Python 3.11.15, sympy 1.14.0, pyyaml 6.0.1, sage null | yes |
| `result.certificate` | kind none, verifier `no-claim` | yes |

Independent re-execution of the self-test by the validator:
`python3 -m pytest tests/test_macaulay_fp.py -q -p no:cacheprovider` → **52 passed**.

Seeds against the frozen contract (`specification.yaml:replication.seeds`) and
`TASK-20260903-5a62de` lines 116–119:

| seed set | contract | manifests |
|---|---|---|
| sweep curve seeds | 1101..1108 | [1101,1102,1103,1104,1105,1106,1107,1108] in all three sweeps |
| target seeds | 1..5 | [1,2,3,4,5] |
| null seeds | 7, 11, 13, 17, 19 | [7,11,13,17,19] |
| positive-control curves / targets | 2101..2103 / 1..2 | [2101,2102,2103] / [1,2] |
| secondary direct arm | (contract names none; D4) | 2101..2103 / 1..2, B = 8 |
| frozen fixture | curve seed 1101, target seed 1, p = 4099 | curve seed 1101, target seed 1, p = 4099 |
| degrees / window | 3..6 / 8 | `degrees: [3, 6]` (min,max), `window: 8` |

Primality, re-confirmed by the validator's own 12-base Miller–Rabin
(bases 2,3,5,7,11,13,17,19,23,29,31,37) and cross-checked with `sympy.isprime`:

| p | prime | note |
|---|---|---|
| 4099 | yes | |
| 16411 | yes | |
| 18446744073709551557 = 2^64 − 59 | yes | no prime in (2^64 − 59, 2^64): exhaustive scan of the 58 intervening integers returned [] ; `sympy.prevprime(2^64)` = 2^64 − 59 |
| 2^256 − 2^224 + 2^192 + 2^96 − 1 | yes | equals the manifest integer exactly |

NIST P-256 named-curve parameters in the raw record: `a == p − 3` (true) and
`b = 0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b`,
the standard curve constant.

D9 disclosure check: `harness/runner.py` does define `_inference_block` twice
(lines 183 and 701); the later definition is constant and hard-codes
`"requested_policy": "executor-terra"`. `executor-terra` is an **alias of
`executor-implementation`** in `orchestration/model-policies.yaml:196`, so the
recorded policy names the same policy the handoff requested. Every run's
`inference.resolved_model_id` is `none (deterministic harness execution)`; no
run claims a model in its loop.

## V2 — raw/summary agreement (recomputed from `runs/*/raw-result.json` only)

Source: `v2_recompute.py` → `v2_recompute_output.json`. `analysis.json` and
`analysis.md` were not read by the script.

Draw counts (recomputed vs `analysis.md` / manifest metrics — identical):

| prime | semaev | null_support | noncurve_cubic | secondary_direct_B8 | semaev_named | null_named | total |
|---|---|---|---|---|---|---|---|
| 4099 | 40 | 200 | 40 | 6 | – | – | 286 |
| 2^64−59 | 40 | 200 | 40 | 6 | – | – | 286 |
| P-256 | 40 | 200 | 40 | 6 | 5 | 25 | 316 |

No duplicate draw key `(arm, curve_seed, target_seed[, null_seed])` at any prime;
`valid: true` on every draw.

Flatness pairing, 64-bit vs P-256, keyed on `(arm, curve seed, target seed[, null seed])`:

| arm | paired | identical on every invariant | invariants compared |
|---|---|---|---|
| semaev | 40 | **40** | 29 |
| null_support | 200 | **200** | 29 |
| noncurve_cubic | 40 | **40** | 29 |
| secondary_direct_B8 | 6 | **6** | 16 |

Modal profiles `(full_rank, top_rank)` at D = 3..6, all three primes:
semaev and noncurve_cubic `[[0,0],[1,1],[6,2],[15,1]]`, unanimous;
null_support `[[0,0],[1,1],[6,6],[15,1]]`, unanimous. `d_ff` 5 / 5 / 6.
`d_ff` recomputed from `per_layer` (first D with `fall_dim > 0`) for **all 888
sweep draws**: 0 mismatches with the recorded `d_ff`.

Rank-drop at 4099 against the 64-bit modal profile, and exact Clopper–Pearson
two-sided 95 % upper limit for 0 of n, `1 − (0.025)^{1/n}`:

| arm | n | drop events | any-difference events | rate | CP upper |
|---|---|---|---|---|---|
| semaev | 40 | 0 | 0 | 0.0000 | 0.08809730287880235 |
| null_support | 200 | 0 | 0 | 0.0000 | 0.018275340355136227 |
| noncurve_cubic | 40 | 0 | 0 | 0.0000 | 0.08809730287880235 |

Semaev-minus-null (modal, per invariant), at each prime — identical tables:

| invariant | 4099 | 2^64−59 | P-256 |
|---|---|---|---|
| top_rank@5 | −4 | −4 | −4 |
| fall_dim@5 | +4 | +4 | +4 |
| d_ff | −1 | −1 | −1 |
| all other 26 invariants | 0 | 0 | 0 |

Null-seed integrity (invalidation rule 5 and D3): 200 distinct `rng_seed_mixed`
per sweep prime, 0 collisions, 5 distinct mixed seeds in each of the 40
`(curve, target)` cells, null-seed labels exactly {7,11,13,17,19}; 0 overlap of
mixed seeds between primes. No flatness bucket mixes a planted arm with the
unplanted null arm (the bucket key's first component is the arm).

**Instance multiplicity (a validator finding, not a disagreement with
`analysis.md`):** the rank profile is a deterministic function of `(A, B, x_R)`,
and the 40 draws per cell do not contain 40 distinct triples, because a curve
whose window `[0,8)` holds only two or three on-curve x-values cannot supply
five distinct planted targets.

| cell | draws | distinct (A,B,x_R) | distinct (A,B) | CP upper on draws | CP upper on distinct triples |
|---|---|---|---|---|---|
| 4099 semaev | 40 | **31** | 8 | 0.0881 | **0.1122** |
| 4099 noncurve | 40 | 35 | 8 | 0.0881 | 0.1000 |
| 2^64−59 semaev | 40 | 30 | 8 | 0.0881 | 0.1157 |
| 2^64−59 noncurve | 40 | 28 | 8 | 0.0881 | 0.1234 |
| P-256 semaev | 40 | 29 | 8 | 0.0881 | 0.1194 |
| P-256 noncurve | 40 | 30 | 8 | 0.0881 | 0.1157 |
| P-256 named semaev | 5 | 4 | 1 | 0.5218 | 0.6024 |

**Cross-prime object sharing:** 0. The curve draw hashes `p` into `(A, B)`
(`sha256(EXP:curve:p:seed:A|B:attempt) mod p`), so no `(A, B, x_R)` triple is
shared between the 64-bit and the 256-bit cell; likewise the null RNG seed mixes
`p`, so the paired null draws are different random polynomials. The pairing is a
pairing of seed labels, not of objects.

## V3 — independent certificate re-verification and rank recomputation

Sources: `v3_independent.py` (+ `_output.json`), `v3_fixture_and_table.py`
(+ `_output.json`). These scripts import nothing from `harness/` and nothing
from the producer's `run_experiment.py` / `analyze.py`; the group law, the
`S_3` evaluation, the multilinear (`a^2 = a`) algebra and the Gaussian
elimination over `F_p` are the validator's own. `harness/semaev.py` was read
once, to confirm the same `S_3` convention; it was never called.

Certificates re-verified with the validator's own affine addition
(`P1, P2, R` on-curve; `x(P1+P2) = x_R`; `{x1, x2}` equal to the recorded pair)
and own `S_3` evaluation (`S_3(x1, x2, x_R) ≡ 0`, cubic confirmed singular
`4A^3 + 27B^2 ≡ 0`):

| run | decomposition certs | re-verified | S_3-root certs | re-verified | singular confirmed |
|---|---|---|---|---|---|
| sweep-p4099 | 46 | 46 | 40 | 40 | 40 |
| sweep-p64 | 46 | 46 | 40 | 40 | 40 |
| sweep-p256 | 51 | 51 | 40 | 40 | 40 |
| posctrl-p4099 | 6 | 6 | – | – | – |
| posctrl-p16411 | 6 | 6 | – | – | – |
| fixture-p4099 | 1 (in `raw.target`) | 1 | – | – | – |

**Total 156 decomposition certificates and 120 S_3-root certificates
re-verified; 0 failures.**

Rank profiles rebuilt from `S~ = S_3(ell_1, ell_2, x_R) mod (a_i^2 − a_i)`,
`ell_k = a_{k,0} + 2 a_{k,1} + 4 a_{k,2}`, per-layer rows
`{ mu · S~ : deg mu = D − 4 }`, exact elimination modulo p:

| prime | arm | draws recomputed | agreeing on (full_rank, top_rank, fall_dim, row/col shape, S~ term count, planted root, digit decoding) |
|---|---|---|---|
| 4099 | semaev | 40 | 40 |
| 4099 | noncurve_cubic | 40 | 40 |
| 2^64−59 | semaev | 40 | 40 |
| 2^64−59 | noncurve_cubic | 40 | 40 |
| P-256 | semaev | 40 | 40 |
| P-256 | semaev_named_p256 | 5 | 5 |
| P-256 | noncurve_cubic | 40 | 40 |
| **total** | | **245** | **245** |

Named draws (the ones cited in the report), recomputed value in each case
`full_rank = [0, 1, 6, 15]`, `top_rank = [0, 1, 2, 1]`, `fall_dim = [0, 0, 4, 14]`,
row counts `[0, 1, 6, 15]`, matching the raw record:

| prime | arm | curve seed | target seed |
|---|---|---|---|
| 2^64−59 | semaev | 1101 | 1 |
| 2^64−59 | semaev | 1104 | 3 |
| 2^64−59 | semaev | 1108 | 5 |
| 2^64−59 | noncurve_cubic | 1101 | 1 |
| P-256 | semaev | 1101 | 1 |
| P-256 | semaev | 1104 | 3 |
| P-256 | semaev | 1108 | 5 |
| P-256 | semaev_named_p256 | NIST-P-256 | 1 |
| P-256 | semaev_named_p256 | NIST-P-256 | 4 |
| P-256 | noncurve_cubic | 1101 | 1 |

Fixture instance (p = 4099, A = 941, B = 428, x_R = 3690), recomputed:
`P1 = (4, 3731)`, `P2 = (7, 2764)`, validator's `P1 + P2 = (3690, 1145) = R`;
`S_3(4, 7, 3690) ≡ 0`; `S~` has 49 nonzero terms and its **49 coefficients are
identical, term by term, to the producer's in-run sympy `independent_stilde`
(0 differences)**; profile `[0,1,6,15] / [0,1,2,1] / [0,0,4,14]`, equal to the
meter, to the producer's sympy `DomainMatrix` rank and to its naive elimination.

Bonus cross-instance check: the *other* contract's "frozen fixture" instance
(EXP-PFDR-5726af, p = 4099, A = 527, B = 72, x_R = 2374) recomputes to the same
profile `[0,1,6,15] / [0,1,2,1] / [0,0,4,14]`, 49 terms.

Not recomputed independently: the `null_support` arm (its coefficients come
from the producer's seeded RNG and are not stored in the raw records), the
`secondary_direct_B8` and positive-control ranks (different presentation;
outside the plan's V3 scope), and `syzygy_dim` / `deficit_series` (their null
series convention is not restated in the contract in a form I could rebuild
without the producer's `series.py`). These are recorded as limitations, not as
disagreements.

## V4 — controls and criterion accounting

Source: `v4_controls_and_criteria.py` → `v4_controls_and_criteria_output.json`.

| control | blocking | contract requires | realised |
|---|---|---|---|
| CTRL-FROZEN-FIXTURE | yes | agreement with EXP-PFDR-5726af on the shared instance, else an independent second implementation in-run | fallback route: 1 run, 1 instance, meter = sympy = naive at D = 3..6; validator re-verified |
| CTRL-POSITIVE-P-DEPENDENCE | yes | 3 curves × 2 targets at p ∈ {4099, 16411}, B = round(√p) | 6 draws each; B = 64 / 128; d_ff 66 / 130; d_top_full 65 / 129; series d_reg 65 / 129 |
| NULL-SUPPORT | yes | 5 seeds per (curve, target, p) | 200 per sweep prime (+25 on the named curve), 0 seed collisions |
| NEARBY-NON-CURVE-CUBIC | no | 8 curves × 5 targets | 40 per sweep prime, all cubics confirmed singular by the validator |
| CTRL-SECONDARY-DIRECT-FIXED-B | no | 3 curves × 2 targets, B = 8, three primes | 6 per prime; d_ff 10 = B + 2, top-full degree 9 = B + 1 |
| CTRL-NAMED-CURVE | no | NIST P-256 at the 256-bit prime | 5 semaev + 25 null draws; a = p − 3, b = standard |
| CTRL-CONFOUNDERS-NAMED | no | no ideal-level or Groebner quantity in a metric | no Groebner call, quotient dimension or solution count in any metric the validator recomputed; all 245 recomputed invariants are generator-level graded ranks |

Frozen-fixture timing (the plan's specific attack):

| event | time (UTC) |
|---|---|
| RUN-PFDR-fd901a-fixture-p4099 started | 2026-09-03T20:29:17.221596Z |
| RUN-PFDR-fd901a-fixture-p4099 finished | 2026-09-03T20:29:20.392103Z |
| earliest EXP-PFDR-5726af run started (RUN-PFDR-5726af-htop) | 2026-09-03T20:34:34.961003Z |
| RUN-PFDR-5726af-m2-s3 started | 2026-09-03T20:34:40.281141Z |
| EXP-PFDR-5726af run package first committed | 2026-09-03T21:08:06Z (89dc58e3) |

⇒ no EXP-PFDR-5726af run existed when the fixture executed; the contract's
fallback was legitimately available and was used.

Contract defect (invalidates nothing): the two contracts' "shared" (2,2,3),
p = 4099 fixture instance is not the same object —
fd901a: `A = 941, B = 428, x_R = 3690`; 5726af (`is_frozen_fixture: true`):
`A = 527, B = 72, x_R = 2374`, both at curve seed 1101 / target seed 1. The
primary agreement route is therefore not executable from these artifacts even
now that 5726af has run.

Criterion accounting, literal:

| # | frozen text | measured | literal reading |
|---|---|---|---|
| 1 | the frozen fixture agrees exactly | meter = sympy = naive at every D ≤ 6, reproduced by the validator | **met**, via the fallback route |
| 2 | the positive control shows d_ff = 65 and 129 (strictly increasing) | first fall (contract's own d_ff definition) **66 and 130** in 6/6 draws each | **NOT met as written** |
| 3 | every Semaev-arm invariant identical at the 64-bit and 256-bit primes in ≥ 38 of 40 draws | 40 of 40 on all 29 invariants | **met** |
| 4 | the rank-drop rate at 4099 is reported with its interval and is below 0.1 per draw | 0 events of 40, rate 0.0000, CP 95 % [0, 0.0881] | **met** (on the rate) |
| 5 | the Semaev-minus-null table at the large primes is reported and is the same at both | identical at all three primes; nonzero only top_rank@5 −4, fall_dim@5 +4, d_ff −1 | **met** |

Criterion (2), both readings, from the raw records:

| reading | p = 4099 (B = 64) | p = 16411 (B = 128) | equals frozen 65 / 129 |
|---|---|---|---|
| first fall (first D with per-layer `fall_dim > 0`) — the contract's own d_ff | 66 | 130 | no |
| first D with `top_rank = #monomials(D)` (`d_top_full`) | 65 | 129 | yes |
| semi-regular series `d_reg` (`series_d_reg`) | 65 | 129 | yes |

The control's forced disposition is met under every reading: strictly
increasing (66 → 130, 65 → 129), no early fall (`fall_dim = 0` at D = 64 and
D = 65, first nonzero `fall_dim = 2` at D = 66), instrument not blind to p.
The contract's O1 bar ("flatness here means the instrument is blind to p and no
O1 may be reported") therefore does not fire. Which integer the contract
*should* have frozen is joint R3's question, not this task's.

Prediction integrity: `git diff c5742969 HEAD -- experiments/EXP-PFDR-fd901a/specification.yaml`
is **empty** — the contract is byte-identical to its approving commit
(c5742969, 2026-09-03 19:42:47Z), which precedes the first run
(20:29:17Z) by 46 minutes. The only change between the design commit
(23593cc6) and the approval commit was `status: review_required → approved`
plus the approval note; `preregistered_prediction`, `success_criterion`,
`controls` and `invalidation_rules` were untouched. `experiments/EXP-PFDR-fd901a/amendments/`
does not exist and no amendment was recorded — consistent with an unaltered
prediction, though the directory named in the reproduction package of
`docs/evidence-and-reproducibility.md` is therefore absent.

## V1 addendum — manifest schema against `docs/evidence-and-reproducibility.md`

Checked field by field against the "Minimum run manifest" template. All six
manifests carry `run.{id, experiment_id, status}`, `code.{commit, dirty,
command}`, the full `environment`, `inputs`, `timing`, `resources`,
`result.{metrics, valid, invalid_reason, certificate.{kind, verified,
verifier}}` and `artifacts` blocks. The **same ten `inference` sub-fields are
absent from all six**, and only those:

`canonical_policy`, `backend`, `provider`, `model_provenance`,
`model_verified`, `requested_reasoning_effort`, `fallback_reason`,
`degraded_requirements`, `independent_session`, `config_digest`.

Root cause is the disclosed D9 defect (the constant `_inference_block` at
`harness/runner.py:701` shadowing the adapter-aware one at line 183). Most of
the information is present in a non-schema location,
`inputs.parameters.executor_session_inference` (requested policy, requested
effort, adapter resolution `anthropic:claude-sonnet-5`, runtime-reported
`claude-fable-5-1`, `model_verified: false`, `fallback_used: unknown`,
`degraded: false`, `independent_session: true`). `config_digest` and
`model_provenance` are absent everywhere. No measured quantity in this package
depends on any of these fields — the runs have no model in their loop.
