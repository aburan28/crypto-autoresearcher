# TT Target Development Preflight V4

## Status and claim boundary

Semantic status: `OBSERVATION`, `TOY-EVIDENCE`, `MODEL-BOUND`.

Full target-partition implementation status: `NEGATIVE RESULT`, `REVISE`.

This checkpoint strengthens the development-only 25-target specialization
path. It does **not** freeze source advice, authorize an experiment run,
produce a locator, establish index calculus, improve Pollard rho, or establish
an ECDLP breakthrough. The experiment still has no `execution_plan`.

## Repairs since V3

The independent V3 follow-up review accepted four concrete attacks or found
four material gaps:

1. all 188 nonzero-elimination counts could be zeroed while rebinding factor
   certificates and cumulative ledgers;
2. all 516 then-existing runtime events could be reordered;
3. verifier exact-rank liveness omitted the retained expected-value table;
4. producer traffic omitted NumPy remainder passes.

The current implementation repairs those findings by:

- reconstructing every raw direct-sum core with Python integers;
- independently running all 200 exact lexicographic RREF factorizations;
- checking pivots, scans, nonzero eliminations, both sweeps, and every final
  core word against numeric replay;
- enforcing the complete canonical 568-event state machine;
- including both observed and expected dense tables during rank checks;
- charging row normalization, elimination, absorption, and direct-core
  remainder traffic;
- metering all 25 target-coefficient derivations;
- metering target-list digesting, two size scans, and two full-result
  serialization passes;
- retaining all emitted target records until artifact serialization and
  recording 25 explicit target-array disposal transitions;
- performing an exact non-materializing JSON byte preflight before allocating
  the full payload and sampling RSS after that allocation.

Forward and reverse schedules produce identical target records, field
arithmetic, copied-word totals, and logical traffic. Their certificate hashes
process 343,747 and 343,762 bytes because schedule-dependent live-word values
have different decimal widths. Their peak live states are separately reported
as 185,935 and 163,726 field words; neither difference is hidden as invariant.

## Development evidence

All artifacts remain outside the repository and report
`artifact_freeze_authorized=false`.

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `source-candidate-bundle-development.json` | 214,471 | `152a2d866dc2d1751408ee7a80b42576e284025861b37f03f2855e1e9eac977a` |
| `target-generator-development.json` | 997,670 | `b2e6caf525d4c29245ddc1280ee7ae635cbf1b09d1ccfb06128bb94e2f61ff2e` |
| `target-verifier-development.json` | 8,008 | `058c7c091a88b8d5e4a30cf589f92cb03c9a17347f6b831fc8443f9e12cc8ab6` |
| `target-mutations-development.json` | 5,518 | `11b54927be62fb3302ddd0595c9a9ecbb78498f2405d4a583c862ae0f0586615` |
| `target-order-invariance-development.json` | 2,412 | `72da7ac10ae5a48e1527b908219bb3374bf917533720bfd64514abdab77ceeff` |
| `target-static-closure-audit-development.json` | 1,452 | `23a40caf2866077336fd2d4037cc6fe0acfdac2ae7cc0af15abe72fa23e77dea` |

All six records report `valid=true`. The target generator emits 568 events,
including 41 source imports, 25 coefficient formations, 25 direct sums, 200
rank factors, 200 absorptions, 25 combination summaries, 25 target emissions,
25 disposals, and two artifact events.

## Replayed producer measurements

```text
adds                              11,847,613
subs                               2,906,073
muls                              15,044,649
squares                                   75
inversions                             1,919
reductions                          6,105,159
comparisons                         3,227,775
hash bytes                            343,747
copied words                        2,128,216
logical traffic words             55,118,448

persistent source advice              52,311 words
persistent target output              34,139 words
peak live state                      185,935 words
largest temporary TT                 100,200 words
largest local matrix                  10,800 words
largest int64 dot length                 144
largest int64 accumulator      2,242,211,904
sampled producer RSS              46,776,320 bytes
serialized target raw                997,670 bytes
```

The int64 accumulator bound remains the closest hard gate. No target is a
canonical zero.

## Independent semantics and controls

The verifier checks 35,379 target tuples and 100 exact unfolding ranks with no
semantic, rank, or numeric replay mismatch. Its semantic/rank meter reports a
118,430-word peak and the process RSS sample is 49,725,440 bytes.

All 20 development mutations fail closed. New controls cover coefficient
accounting, output serialization passes, plausible event reordering, rebound
elimination certificates, retained-target-output accounting, and disposal
state. These controls do not substitute for the frozen 29-mutation campaign.

The experiment suite passes 41 tests. The repository suite passes 144 tests.
The static producer and verifier closures remain disjoint.

## Remaining REVISE boundary

The producer ledger is now independently replayed, but a complete target
partition is not yet established. The child still self-reports timing and RSS;
the final stdout write and runtime filesystem/environment closure do not have
an external parent receipt. The verifier's reported operation and live-word
meter covers exhaustive semantics and ranks, but not the preceding numeric
producer-ledger replay, parsed target retention, or all input/output handling.
Those omissions must not be described as full verifier-partition accounting.

Two fresh red-team workers were asked to review this repaired state, but both
remained running after explicit stop requests and were shut down without a
decision. Therefore no fresh `GO` is recorded. The prior `REVISE` decision is
preserved.

## Next concrete action

Implement an isolated target producer/verifier staging launcher that emits
parent-observed wall-time, child-rusage, stdout/stderr, environment, file-read,
Python, NumPy, and loader receipts; then meter the verifier's numeric ledger
replay and retained parsed targets before requesting another independent
review.
