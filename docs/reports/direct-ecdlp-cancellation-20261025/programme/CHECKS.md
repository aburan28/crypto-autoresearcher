# Development checks and limits

These are implementation self-tests on fixed tiny public synthetic inputs, not admitted scientific trials or a performance study. No solver advantage, novel identity, cryptographic-size result or independent-session verification is claimed.

## Tagged reference

Sources and receipts: [reference/README.md](reference/README.md), [C++20 source](reference/tagged_reference.cpp), [fixtures](reference/fixtures.tsv), [test launcher](reference/test.sh), [machine-readable receipt](reference/development-validation.json) and [retained output](reference/development-validation.txt).

| Field p | Curve (a,b) | P | Curve order | Prime subgroup order r | Cofactor |
| --- | --- | --- | --- | --- | --- |
| 5 | (0,1) | (0,1) | 6 | 3 | 2 |
| 17 | (2,2) | (5,1) | 19 | 19 | 1 |
| 23 | (1,1) | (17,3) | 28 | 7 | 4 |

The p=5 fixture is a special-j exception control. These fixtures do not represent the proposed ordinary-curve cohort. Complete point enumeration and trial division check their small orders and primes. Independently coded affine and Jacobian additions share the field reduction primitive and curve model; this is an arithmetic cross-check, with that dependency disclosed.

Each final suite reports the following measured assertion/case counts. Counts describe overlapping checks, not independent statistical samples.

| Check | Recorded count |
| --- | ---: |
| Assertions | 13,731 |
| Full-curve point-pair additions | 1,181 |
| Scalar bit inputs, including noncanonical-range inputs | 44 |
| Subgroup targets | 29 |
| Outside-subgroup on-curve targets | 24 |
| Point-transition witness candidates enumerated | 58,054 |
| One/two-step tagged boundary comparisons | 2,362 |
| Mutated traces rejected | 428 |
| Ring checks | 8,225 |
| Expected invalid-input rejections | 22 |

Strict warning-as-error compilation, normal execution, UBSan and combined ASan/UBSan passed. LeakSanitizer failed under environment tracing; the successful combined sanitizer invocation explicitly used `ASAN_OPTIONS=detect_leaks=0`. Leak detection did not pass and remains unavailable. The initial signed-conversion compilation failure, subsequent repair, strengthened suite and sanitizer failure are retained in the receipt. No measured elapsed-time comparison was collected.

Final source SHA-256: `6694c908abf275a2be41655cbbed6f5fcfb131a0dfb300b2027a323f9e3f2685`.

Reproduce with `./reference/test.sh normal`, `./reference/test.sh ubsan` and `ASAN_OPTIONS=detect_leaks=0 ./reference/test.sh asan-ubsan`. The launcher builds in a disposable temporary directory; its only target interface is `--self-test`. The fixture-discovery utility is provenance scaffolding for these tiny fixtures, not the scientific-cohort generator.

## Fixed-window control

[window-control.md](window-control.md) derives the exact binary rank r−1 and the tagged row/column margins of the full point-state window matrix. The written argument applies to odd r>1. It is a known scalar-window control and supplies no unknown target's scalar labels.

The [C++ regression](window-control.cpp) checks r in {3,5,7,11,13,17} and d in {1,2,3,4}: 24 cases, 24 ranks, 448 tagged margins, 24 deliberate mutations and 18 rank calibrations. Both normal and ASan/UBSan execution passed with leak checking explicitly disabled for the environment limitation. Its source SHA-256 is `d7948445e4c7cf75e6c90417107886e935110aee4d9c903a8581b59054221a94`.

The rank is over F₂, not the square-zero ring. High rank of this full matrix only bounds exact rank-one decompositions of that flattening. It does not bound arbitrary bit-level algorithms or target-conditioned evaluation time; full rank and cheap implicit computation can coexist.

## What is still missing

The reference has deterministic **point-level** states. It does not compile modular arithmetic into Boolean gates/carries, establish unique wire extensions for such a circuit, search a frozen rewrite grammar, or evaluate a new cancellation construction. Fixed-window agreement is a known positive control. No discovery/confirmation cohort, blinded labels, rho comparison, formal proof assistant build or admitted experiment has run.

The [methodology review](methodology-review.md) is same-session assistance with access to the plan. It is useful criticism but is not a formal independent review, blind re-derivation or novelty certificate. The source corpus, source hashes and earlier literature coverage limits remain those in [SOURCES.md](../SOURCES.md).

The lossy-panel correction in [LEADS.md](LEADS.md) is a derived finite-group reference, not a new measured result or correction to frozen evidence. It requires separate checking before an official source/status update.
