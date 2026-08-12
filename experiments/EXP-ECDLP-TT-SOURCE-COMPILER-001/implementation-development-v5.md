# TT Target Staged Development Preflight V5

## Status and claim boundary

Semantic status: `OBSERVATION`, `TOY-EVIDENCE`, `MODEL-BOUND`.

Full target-partition implementation status: `NEGATIVE RESULT`, `REVISE`.

This checkpoint stages and supervises the development-only 25-target
specialization path. It does **not** freeze source advice, authorize a campaign,
produce a locator, establish index calculus, improve Pollard rho, or establish
an ECDLP breakthrough. The experiment still has no `execution_plan`.

## V4 review and repairs

An independent static red team returned `REVISE`. It confirmed that direct
child wall time, rusage, and pipe bytes were parent-observed, but found that a
minimal child-authored receipt could pass, the same interpreter could alter its
own audit state, no parent post-run stage hash existed, and three linear
verifier costs were absent.

V5 repairs the concrete fail-open and accounting findings:

- the parent requires exact result and receipt schemas, claim boundaries,
  role, stage, static-audit, environment-event, backend-check, read-file, raw
  input, and output bindings;
- the parent independently hashes every stage file before and after execution;
- the static audit now binds the parent launcher, child bootstrap, backend
  attestor, and auditor in a separate harness closure;
- a macOS Seatbelt profile denies network access, process forks, and all file
  writes for the child;
- producer and verifier source closures prohibit threading, `ctypes`, `mmap`,
  multiprocessing, subprocesses, sockets, and direct exec/fork calls;
- any role-triggered `ctypes.dlopen` after backend attestation is rejected;
- the verifier meters expected-vector zero fill, exhaustive equality checks,
  target serialization copies, and numeric core comparisons without creating
  the prior unmetered tuple copy;
- both producer and verifier retain the decoded input field values alongside
  their parsed tensor copies;
- one explicit `target_input_retention` event is independently replayed.

## Staging boundary

The parent controls the pinned interpreter command, reduced environment,
Seatbelt profile, timeout, pipes, pre/post hashes, and child rusage. The child
cannot write files, fork, or access the network under the OS profile.

File reads are still enumerated by the in-process audit hook rather than denied
by an OS read allowlist. The parent checks every reported path against allowed
roots and rehashes every reported file, while exact source and harness hashes
prevent drift in the reviewed implementation. This is stronger development
evidence, but it is not an adversarial syscall-completeness theorem. The
remaining read-boundary limitation keeps the full implementation at `REVISE`.

## V13 evidence

All artifacts remain outside the repository and report
`artifact_freeze_authorized=false`.

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `target-generator-staged-development-v13.json` | 1,000,952 | `f38a27bd059ae46aa49176c44ef23017428153d69c279b4af6d8fd5a753748dc` |
| `target-verifier-staged-development-v13.json` | 8,359 | `cedecc8dd7e5c11a6d47523b6147ff2e42d68dc4e35ede4f4beae33b00b89d02` |
| `target-generator-staging-receipt-development-v13.json` | 321,811 | `9cd4d2ae29acd0040af5a8d05bf08d925dcea969c364a58ebbb8cbfe043c4d8e` |
| `target-verifier-staging-receipt-development-v13.json` | 321,268 | `7ba0d8e4a04bd934cee776078552ff776e209144d7b458976b024c84da91158e` |
| `target-mutations-development-v13.json` | 6,029 | `e8b2582a027a54a2e812e6a395e5404dd27bc1477177e91f10c120c060ff79c6` |
| `target-order-invariance-development-v13.json` | 2,412 | `4303834628518bbace38abaae4ce7531a90fa7f05ed450c5ceceafcea7ad5a82` |
| `target-static-closure-audit-development-v13.json` | 2,064 | `2585a39e506f099ff2a771152cc35284366c311c2d235b4cbd65bfafead577d3` |

All seven records report `valid=true`. Producer and verifier stages contain
eight and seven files. Their complete runtime receipts hash 1,379 and 1,378
read files. The harness closure digest is
`8e89757320e6d9c2e6db3c5613ab509f1c3ecb657547b858ba70a07401607a87`.

## Producer accounting

The 569-event producer ledger reports:

```text
adds                              11,847,613
subs                               2,906,073
muls                              15,044,649
squares                                   75
inversions                             1,919
reductions                          6,105,159
comparisons                         3,227,775
hash bytes                            343,925
copied words                        2,235,640
logical traffic words             55,225,872

decoded input retained                53,712 words
parsed source advice                  52,311 words
emitted target output                 34,139 words
peak live state                      239,647 words
largest temporary TT                 100,200 words
largest local matrix                  10,800 words
largest int64 dot length                 144
largest int64 accumulator      2,242,211,904
child self-sampled RSS             67,174,400 bytes
parent-observed RSS                70,303,744 bytes
parent-observed wall time        2,500,332,125 ns
```

Forward and reverse schedules emit identical target records, arithmetic,
traffic, and 343,925 certificate hash bytes. Their separately reported peaks
are 239,647 and 217,438 field words.

## Verifier accounting and controls

The verifier checks 35,379 target tuples, 100 exact unfolding ranks, all 200
numeric factorization replays, and all final core words. Its cumulative meter
reports:

```text
adds                              49,598,903
subs                               3,804,421
muls                              57,735,286
inversions                             2,772
reductions                          8,325,096
comparisons                           500,998
hash bytes                          2,002,132
copied words                        5,719,113
logical traffic words             89,097,141
retained field words                 228,220
peak live field words                356,126
parent-observed RSS                77,725,696 bytes
parent-observed wall time        9,210,117,750 ns
```

All 22 development mutations fail closed, including input-retention resource
and event forgeries. These controls do not substitute for the frozen
29-mutation campaign. The experiment suite passes 49 tests.

## Remaining gates

- Replace child-audited file-read enumeration with an OS-enforced or externally
  traced read allowlist, or formally narrow the claim to exact reviewed-source
  integrity rather than adversarial capability isolation.
- Obtain a fresh independent review of the repaired V13 state and preserve any
  further `REVISE` findings.
- Execute the frozen 29-mutation generator/verifier partitions.
- Create and approve an `execution_plan`, then freeze source and target
  artifacts before any immutable campaign run.

## Next concrete action

Build a parent-owned file-read trace/control for the pinned child and compare
its exact path/digest closure with the V13 receipt before requesting the next
independent review.
