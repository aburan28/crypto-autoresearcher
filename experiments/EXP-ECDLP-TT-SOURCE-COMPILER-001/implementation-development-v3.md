# TT Target Specialization Development Preflight V3

## Status and claim boundary

Semantic status: `OBSERVATION`, `TOY-EVIDENCE`, `MODEL-BOUND`.

Full target-partition implementation status: `NEGATIVE RESULT`, `REVISE`.

This checkpoint implements and independently verifies the 25 target tensor
specializations frozen by protocol v5. It does **not** freeze source advice,
authorize an experiment run, produce a locator, establish an index-calculus
algorithm, improve Pollard rho, or establish an ECDLP breakthrough. The
experiment still has no `execution_plan`.

The source inputs are wrapped in
`tt-source-candidate-bundle-development-v1`. The wrapper reconstructs the two
objects checked by the strict source preflight and matches their candidate
digests, but retains `artifact_freeze_authorized=false` throughout.

## Implemented development slice

The target path consists of:

1. `build_tt_source_candidate_bundle.py`, a harness-only reconstruction of the
   strict-preflight candidate advice and controls;
2. `compile_tt_target_advice.py`, the target-only producer;
3. `tt_target_runtime.py`, an exact weighted-direct-sum and two-sweep finite-
   field TT runtime;
4. `verify_tt_target_advice.py`, an independent Python-integer verifier that
   imports neither the producer, producer runtime, nor coefficient helper;
5. `run_tt_target_development_mutations.py`, 13 synthetic fail-closed controls;
6. `check_tt_target_order_invariance.py`, forward/reverse schedule comparison;
7. `audit_tt_target_closure.py`, a names-only disjoint static closure audit.

The producer reads only the candidate source bundle, target manifest, and full
execution matrix. It does not read the 138 MB source raw result, source
verifier, mutation manifest, or prior target result. Its reported local closure
is exactly:

```text
compile_tt_target_advice.py
tt_target_coefficients.py
tt_target_runtime.py
```

The reported verifier closure is exactly `verify_tt_target_advice.py`, with no
local-file overlap. This audit resolves ordinary local imports and scans a
bounded syntax blacklist; it is not yet a transitive runtime path attestation.

## Independent review history

The first independent review returned `NEGATIVE RESULT` for implementation
compliance while confirming the toy weighted algebra and 1,080 random matrix
factorizations. It found persistent-source liveness undercounting, a producer
five-tuple iterator, missing canonical dense-kernel checks, incomplete event
accounting, and weak multi-source controls.

Those findings were repaired with persistent source accounting, preallocation
refusal, ownership transfer for raw TT cores, removal of producer tuple
enumeration, canonical int64 scans, disjoint runtime events, and B5 six-source
tests.

A follow-up review then found four additional implementation failures:

- event vectors could be reduced together with cumulative totals and still be
  accepted;
- a valid-format false factor digest was not recomputed;
- producer and verifier peak-live claims omitted retained objects;
- the evidence table mixed stale artifacts from different source bytes.

The current slice repairs those failures narrowly:

- the verifier derives each source import, direct sum, rank factorization,
  absorption, and target emit vector from bound tensors, shapes, pivots, and
  state transitions;
- factor certificate SHA-256 values are recomputed over canonical certificate
  bytes;
- all 200 factor/absorption pairs are replayed through the exact eight-step TT
  shape state machine;
- producer resource maxima are independently reconstructed and must match;
- verifier liveness retains all source tensors and cached dense source tables;
- normalization mutates the caller-owned raw-core list, so replaced raw cores
  are not retained through the sweep;
- valid-format digest, paired-underaccounting, zero-ledger, and zero-peak
  controls now fail closed.

This is an exact replay of the **TT runtime ledger**, not yet exact accounting
for the entire `target_generator` process. Target coefficient derivation,
target-list hashing, whole-result serialization, final RSS sampling, complete
path/runtime attestation, and disposal accounting remain outside that ledger.
The full-partition review therefore remains `REVISE`.

## Development evidence

All files below are outside the repository and are not frozen run artifacts.

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `source-candidate-bundle-development.json` | 214,471 | `152a2d866dc2d1751408ee7a80b42576e284025861b37f03f2855e1e9eac977a` |
| `target-generator-development.json` | 905,153 | `75654fdd71da58fe652c46eb3652feda9b163dd0261d44299fabd5404b76e8c3` |
| `target-verifier-development.json` | 7,841 | `97554ffda7a2358e9bb399c974667dd30162f9f2a9d555a68a7e251e559a0a06` |
| `target-mutations-development.json` | 3,774 | `0d9eef989f04696b7fba0017401912a284725f46b211dfa39e19108324a24af3` |
| `target-order-invariance-development.json` | 2,167 | `5628675f75d13ffc18a5fc26ea27d28204dc2ce4040133a4e5f7236321a8c704` |
| `target-static-closure-audit-development.json` | 1,452 | `575c92abb16e7a87295fc4550d9752407c284320d39cf609dd78729e9e914612` |

All six records report `valid=true` and
`artifact_freeze_authorized=false`.

The candidate bundle reproduces the strict source candidate bindings:

```text
retained advice:  adfacac64f7a143e9dec8c7f849b7bb9517ff07c7099b80279c7ca9a891c529e
source controls:  b4ab406a8fd48b697584e03bb681d23be9562ea51a5e4684ac2ca206d6cbb06e
source receipt:   9e113a17f1bfbd8cbb718c85c7d655547ef96e5e781582383896e822bfd2e0bb
```

## TT runtime measurements

The producer completed 19 trace-zero targets and six general-trace controls:

```text
imported source tensors:       41
target linear combinations:   25
normalization calls:           25
two-sweep factorizations:     200
canonical-zero targets:         0
```

The independently replayed TT-runtime operation vector was:

```text
adds          11,847,570
subs           2,906,023
muls          15,044,444
squares                0
inversions         1,919
reductions      6,104,947
comparisons     3,227,350
hash_bytes        202,933
copied_words    2,025,799
```

Logical TT-runtime traffic was 42,741,703 field words. Resource maxima were:

```text
persistent source advice       52,311 words
peak live state               154,936 words       cap 500,000
largest temporary TT          100,200 words       cap 1,000,000
largest local matrix           10,800 words       cap 1,000,000
largest int64 dot length          144             cap 150
largest int64 accumulator   2,242,211,904         cap 2,335,637,400
sampled producer RSS        46,661,632 bytes      cap 2 GiB
serialized target raw          905,153 bytes      cap 256 MiB
```

The int64 accumulator gate has the least relative headroom and remains a hard
stop. The RSS value is sampled before final CLI serialization and is therefore
development evidence, not a closed full-partition maximum.

## Independent verifier and controls

The verifier independently rederived all coefficient formulas, evaluated every
target TT and source linear combination, and computed every exact unfolding
rank:

```text
exhaustive target tuple checks: 35,379
exact unfolding-rank checks:       100
semantic mismatches:                 0
rank mismatches:                     0
peak verifier live state:      115,305 words
sampled verifier RSS:        40,992,768 bytes
```

The persistent verifier lower bound is explicit: 52,311 source-tensor words
plus 53,919 cached dense values, or 106,230 words before target-local work.

All 13 development mutations failed closed:

- coefficient change;
- target core change with rebound target and emit digests;
- rank change;
- source-receipt change;
- factor-schedule change;
- valid-format false factor certificate digest;
- cumulative-operation undercount;
- paired event and cumulative undercount;
- fully zeroed event and cumulative ledgers;
- zeroed producer peak-live claim;
- target-order swap;
- target deletion;
- unauthorized breakthrough claim.

These are development controls, not execution of the frozen 29-mutation
manifest. Forward and reverse schedules produced 25 identical target records,
source candidate digests, TT-runtime operations, traffic, and field-resource
maxima. The complete experiment test suite passes 39 tests.

## Remaining gates

- Meter target coefficient derivation, target-list hashing, whole-result
  serialization, disposal, post-serialization RSS, and preallocation byte
  bounds as part of the complete `target_generator` partition.
- Replace the names-only closure report with isolated staging and runtime
  filesystem, environment, Python, NumPy, and OS-loader receipts.
- Run the frozen 29-mutation generator/verifier partitions rather than only the
  13 development controls.
- Obtain a fresh independent accounting/red-team decision over the completed
  partition and preserve any further `REVISE` findings.
- Create an approved `execution_plan`, then formally freeze source and target
  artifacts before any immutable campaign run.

## Next concrete action

Add independently replayable `target_coefficient_formation` and
`target_artifact_serialization` events to the target generator, including a
preallocation serialized-byte bound and an RSS sample after full-payload
materialization, then rerun the paired-ledger controls.
