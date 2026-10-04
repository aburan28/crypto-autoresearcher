# Cold-start single-target IC: ARM composition

RUN-KIC-a15078 completed 96 valid scientific processes on 24 fresh public-synthetic targets. The composed IC takes a paired median **3.2945816805 times** the strengthened rho's whole-process wall time. Its fixed 10,000-resample paired-bootstrap 95% interval is **[2.8025165543, 4.3689454583]**. The preregistered requirement—median below 0.95 and bootstrap upper endpoint below 1—was not met. This is a finite measured gap, not a closure of the IC direction.

The candidate combines the previously tested larger pair table and target-certificate stopping with guarded ARM PMULL field arithmetic and a compact dual-sign relation-query kernel. Rho receives the common field arithmetic and inversion improvements too. The factor base remains the point-defined signed Frobenius orbit base with 75 columns and density parameter 1/256.

All citations in this report have **internal** provenance: the linked protocol, immutable producer artifacts and independent review. No novelty, asymptotic, security or cryptanalytic conclusion is asserted.

## Matched four-arm comparison

| Comparison | Median of paired wall-time ratios | Interpretation |
| --- | ---: | --- |
| Composed IC / larger-table full-rank IC | 0.8201511124 | 17.98% less wall time on matched targets |
| Strengthened rho / previous rho | 0.6048672983 | 39.51% less wall time on matched targets |
| Composed IC / previous rho | 2.0480127644 | IC still slower |
| Composed IC / strengthened rho | 3.2945816805 | Primary comparison; IC still slower |

Marginal arm medians below describe typical times and memory separately. Dividing these medians does not reproduce the median of paired ratios above.

| Arm | Median cold wall, seconds | Median process CPU, seconds | Median peak RSS, bytes |
| --- | ---: | ---: | ---: |
| Larger-table full-rank IC | 4.1377702915 | 4.0197315 | 774,569,984 |
| Composed IC | 3.0809126245 | 3.0593625 | 773,734,400 |
| Previous rho | 1.5092528755 | 1.5009090 | 88,416,256 |
| Strengthened rho | 0.9604996665 | 0.9418145 | 88,391,680 |

Composed IC / strengthened rho has a paired median peak-RSS ratio of 8.7492585298. Peak RSS is the per-process `wait4` value; sampled physical footprint is recorded separately. The maximum sampled footprint across all 96 processes was 774,849,448 bytes.

The composed IC's median internal setup is 0.7615440415 seconds, query kernel 1.844755585 seconds, and relation collection 1.856930354 seconds. The query is nested within collection. Component medians are not additive and are not substituted for the external cold wall measurement. Reference/base validation, certificate verification, output and process overhead remain charged in that wall measurement.

## Evidence and controls

The field is GF(2^53), the curve uses a=0, the polynomial is x^53+x^6+x^2+x+1 and the subgroup order is 21,044,858,204,113. Each target is an explicitly known synthetic scalar multiple. The panel is disjoint from the 84 earlier targets and from control scalar 17. Each of the 24 permutations of the four arms appears once.

- All 96 scientific processes completed validly; no omitted cases, retries, watchdog expiries, resource-cap events or missing-telemetry cases.
- All 24 IC generation-prefix comparisons and target certificates passed; all 24 old/new rho walk-semantic comparisons passed.
- Seventeen IC and five rho native tests passed, including 2,809 basis products, 53 basis squares, deterministic inversion controls, exceptional point cases and 30 batch shapes.
- All eight untimed solver controls passed. Actual ARM query-branch use was recorded in every candidate n53 process.
- An independent validator derived the primary statistic and certificates from raw receipts before inspecting the producer's implementation and analysis. All seven assigned joints passed, including static replay of 1,781 candidate relation group identities and all 96 public target equations. Final acceptance is bound by [the Coordinator decision](../../ledger/decisions/DEC-20260921-6648da.md) and [the review report](review/report.json).

Cold means a fresh process, working directory, HOME and TMPDIR, with no reused factor-base table or logs. Each arm uses one worker. Wall time covers launch through `wait4` reap and complete result verification/output. Offline builds are preserved separately. No operating-system cache flush, thermal invariance, background-load invariance or fresh serving-model probe is claimed. Native review used the requested independent sol/xhigh session; static adapter model-verification metadata is older configuration and is disclosed in the admission receipt.

The generic independence helper could not parse this lane's bespoke top-level review-plan schema and exited 2 with `no review_plan block`. The validator checked all seven joints and blind-read ordering directly; no automated independence-helper pass is claimed. The producer analysis field `eligible_for_independent_review=false` denotes its failed positive-signal predicate, not an invalid finite receipt.

## Progress in this continuation

| Run | Bounded mechanism | Scientific processes | Measured result within its own panel |
| --- | --- | ---: | --- |
| RUN-KIC-e3dbed | Remove unused allocation; calibrate density; held-out IC/rho | 96 | Selected K=75; primary IC/rho 3.5110 |
| RUN-KIC-8b5038 | Double signed-expanded hash capacity | 72 | IC wall ratio 0.8708; RSS ratio 1.7623 |
| RUN-KIC-56c897 | Stop at a verified target-determining certificate | 72 | IC wall ratio 0.9358; all 24 certificate/prefix checks pass |
| RUN-KIC-a15078 | Compose improvements and strengthen common ARM arithmetic | 96 | IC wall ratio 0.8202; strengthened-rho primary 3.2946 |

These are 336 scientific processes in four distinct frozen panels. Ratios across rows are not a controlled speedup trajectory and must not be multiplied together. Earlier density selection was nearly tied at K=75 and K=94 and predates the composition; K=75 is the selected tested configuration, not a proved optimum for the new implementation.

The next action and alternative rankings belong to the Coordinator decision. No fifth experiment or profiler run is represented by these results.

## Reproducibility pointers

- [Frozen protocol](protocol.json), [approval](approval.md) and [preregistered review plan](review_plan.json).
- [Producer analysis](artifacts/RUN-KIC-a15078/analysis.md), [process receipts](artifacts/RUN-KIC-a15078/receipts/processes.jsonl) and [raw-output manifest](artifacts/RUN-KIC-a15078/receipts/raw_processes_manifest.json).
- [Lossless analysis archive index](artifacts/RUN-KIC-a15078/analysis.json.archive-index.json). The committed gzip reconstructs the original 139,940,845-byte analysis with SHA-256 `e9121f475497f1f16c9ad8688123592913488091da7fa20e36f902466ad1e027`; original result bytes are unchanged.
- [Source custody index](source_custody_index.json), [source patch](artifacts/RUN-KIC-a15078/candidate.patch), [snapshot receipt](snapshot_receipt.json) and [execution receipt](artifacts/RUN-KIC-a15078/execution_receipt.json).
- [Blind re-derivation](review/blind_rederivation.json), [review admission](review_admission.json), [final archive receipt](archive_receipt.json).

Work is isolated on local branch `codex/cold-single-ic-20260921`. No remote publication was performed.
