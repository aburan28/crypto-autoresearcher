# Analysis: EXP-ENDO-33a1ee / RUN-ENDO-bc1b14

Coordinator review under DEC-20261016-f379af. Evidence record EV-ENDO-118b3a; correction CORR-20261016-37897c. Hypothesis H-ENDO-c9f324; idea IDEA-20261016-15a6fc; question RQ-ENDO-476761; goal GOAL-ENDO-001. Snapshot TASK-20261016-8a9451 at `6033c3f08`. Independent validation TASK-20261016-35d324 (`experiments/EXP-ENDO-7494e7/validation/TASK-20261016-35d324.md`, run B, verdict passed). Ledger archive TASK-20261016-5c0f78.

Measured wall-clock of known-scalar variable-base k·P in one implementation on one shared host. Wall time is never a measured bound. No ECDLP, rho or exponent statement.

## Validity (checked before interpretation)

| check | result | source |
|:--|:--|:--|
| expected run count | 1 expected, 1 present (RUN-ENDO-bc1b14), two curves | spec `maximum_runs: 1`; manifest |
| manifest | `validity: valid`; points 64, reps 41, bootstrap 4000, seed 20261016, `--cflags=-O2 -march=native`; `repository_dirty: false` | manifest.yaml; validator B1 |
| series | 4 arms x 41 entries per curve; check.py exit 0 | validator B1 |
| raw / summary agreement | raw-result.json equals the two summaries; 17 receipt and 9 manifest digests match | validator B1 |
| recomputation | exact replay of the recorded bootstrap (seed 20261017, 4000 resamples) reproduces all 6 medians and CIs to 1e-12; an independent bootstrap (seed 0x35D324, 20000 resamples) agrees to 4 decimals | validator B2 |
| correctness | `correct: true`, `mismatches: []` on both curves; validator's own affine reference matches all 4 x 64 outputs per curve (512/512); fresh-point recompile 5/5 per arm per curve at both flag sets | validator B2, B3 |
| inputs | p and n match the source rows; k' = k·c mod n on all 64 points; all inputs on E with order n | validator B1 |
| code audit | equal work across arms; the a-multiplication is present in dbl-2007-bl; volatile sinks; A2 priced conservatively (about +0.3 % against it) | validator B3 |
| record defects (non-invalidating) | `provenance.cc` omits -march=native (CORR-20261016-37897c); spec text "p < 2^255" is stale (header says p < 2^256); no peak-memory record | validator B1 |

The run set is valid and complete.

## Observation

- **O1 Gates.** Correctness true on both curves. Target A/A A3/A0 0.9989 [0.9923, 1.0101]. Control A/A 1.0002 [0.9864, 1.0060]. Control A1/A0 upper bound 0.9316.
- **O2 Target** other/BADA55-VPR-224 (route 5·5, degree 25, dual sign +1). Medians, ns per scalar multiplication: A0 224,139.2; A1 212,508.3; A2 220,662.1; A3 226,697.7. Paired ratios (median, 95 % percentile-bootstrap CI): A1/A0 0.9324 [0.9220, 0.9423]; A2/A0 0.9693 [0.9647, 0.9767].
- **O3 Control** (3-isogenous neighbour of NIST P-256, route [3] back to P-256's a = -3 model): A0 272,232.4; A1 250,264.0; A2 250,267.4; A3 267,943.8 ns. A1/A0 0.9197 [0.9073, 0.9316]; A2/A0 0.9262 [0.9089, 0.9352].
- **O4 Derived savings** (1 - median ratio): target persistent 6.76 % [5.77, 7.80], one-shot 3.07 % [2.33, 3.53]; control persistent 8.03 %, one-shot 7.38 %. Modelled (RUN-ENDO-d7cb69): target 15.205 % and 11.441 %; control 15.276 % and 14.465 %.
- **O5 Contention** (validator B4: a repetition is flagged when any arm exceeds 1.10 x that arm's median). 17 of 41 target and 19 of 41 control repetitions are flagged, in bursts of 1.2-1.9x. The outliers by arm are 11/11/13/14 on the target and 11/11/12/10 on the control, with no drift; ratio slopes are at most 0.0011 per repetition.
  - Dropping the flagged repetitions gives, on the target: A1/A0 0.9334 [0.9239, 0.9423], A2/A0 0.9681 [0.9638, 0.9710], A3/A0 0.9987 [0.9944, 1.0062].
  - On the control: A1/A0 0.9183 [0.9051, 0.9223], A2/A0 0.9257 [0.9089, 0.9316], A3/A0 0.9983 [0.9845, 1.0035].
  - The run report records that another validator (TASK-20261016-1b5210) was doing CPU work in the same container around the run.

## Comparison (against the frozen contract)

- **Gate resolution**: correctness, both A/A gates (CI contains 1 and lies within [0.95, 1.05]) and the positive control (control A1/A0 upper bound < 1) pass. The target's A1/A0 and A2/A0 inferences are released.
- **Success criterion**: target ratio_A2_over_A0 95 % CI upper bound < 1. Met: 0.9767. Falsification (lower bound ≥ 1) and inconclusive (CI contains 1, or a gate fails) do not apply. Without the contention-flagged repetitions, every gate outcome and interval side is unchanged.
- **Preregistered prediction**: persistent saving in (0, 15.205 %), observed 6.76 %; one-shot in (0, 11.441 %), observed 3.07 %; one-shot < persistent, holds. The control shows the same ordering and dilution (8.03 % > 7.38 %, both below modelled). The prediction source is disclosed as not independent of the smoke run; the criteria are interval-sign criteria and do not use smoke values.
- **Measured against modelled**: the target keeps 44 % of its modelled persistent saving and 27 % of its modelled one-shot saving; the control keeps 53 % and 51 %. The one-shot dilution is larger on the target, whose route has two 5-isogeny steps each way against one 3-step for the control.
- **Against the index-calculus baseline and the matched rho**: not applicable; known-scalar k·P wall-clock in one implementation. The GAE pricing band (AGENTS.md section 5a) does not apply; this is not an ECDLP comparison.

## Inference

- **I1** On other/BADA55-VPR-224, on this host, with bench.c compiled by cc 13.3.0 at -O2 -march=native, one-shot variable-base k·P routed through the 5·5 neighbour's a = -3 model is measurably faster than k·P on E with E's generic-a doubling: 3.07 % (95 % CI 2.33 % to 3.53 %). The persistent form saves 6.76 % (5.77 % to 7.80 %).
- **I2** The measured saving is well below the modelled one, as predicted. The modelled M_eq omits the final inversion, field additions, control and memory overhead, all of which every arm pays.
- **I3** The frozen on_positive branch applies: supported at the measured tier for this curve, host, compiler and implementation only. Strength is preliminary: one curve, one host, one compiler, an untuned generic A0, unreplicated.

## Limitation

- **L1** One shared KVM host (Intel Xeon 2.80 GHz, 4 vCPU) without pinning, frequency control or isolation; contention is visible though symmetric (O5).
- **L2** Generic 4-limb CIOS with S = M and an untuned A0; a tuned E-side implementation could narrow or erase the gap. Variable-time code; one Fermat inversion in every arm.
- **L3** One curve. BADA55-VPR-224 is, as recalled context only, a published demonstration curve rather than a deployed standard; nothing relies on that.
- **L4** The prediction and the A/A margin were written with the smoke values in view (disclosed). Correctness was checked on repetition-0 outputs; later repetitions repeat the same deterministic computation.
- **L5** Nothing transfers to other hosts, compilers, libraries, dedicated squaring, constant-time or complete formulas, fixed-base k·P, or the GLV curves of EXP-ENDO-7494e7. Faster known-scalar multiplication does not establish faster unknown-scalar recovery.
- **L6** Heuristics H1-H3 of the idea are not validated; the route cost of H3 is embedded in A2 and not isolated. No peak-memory record.
