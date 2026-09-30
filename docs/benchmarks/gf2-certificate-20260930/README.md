# GF(2) certificate verification: implementation and evidence

Date: 2026-09-30. Related tracking: [issue #1505](https://github.com/aburan28/crypto-autoresearcher/issues/1505).

This is an engineering change to exact certificate checking. It introduces no
new elimination method, key-recovery workflow, TNFS implementation, or research
hypothesis transition.

## Research and current code

| Technique | Suitable workload | Finding for this change |
| --- | --- | --- |
| Packed GF(2), Four Russians tables, cache blocking | Dense binary matrices | The existing GF(2) engine already implements table-based blocked updates, super-blocks, OpenMP, and vectorized native kernels. No duplicate backend was added. |
| FFLAS-FFPACK | Dense exact arithmetic over suitable finite fields, especially word-size prime fields | A separate backend choice; it is not a replacement for an instrument that promises identical pivot and operation logs. |
| LinBox black-box methods | Large sparse or structured exact systems | Avoid elimination fill-in; applicability and certificate contracts must be evaluated independently. |
| CRYPTO 2026 Galois symmetry | TNFS constructions with the paper's prerequisites | Remains the separately tracked published result in KN-LIT-7643 / KN-OPEN-025. The 36x/144x factors are not applied here. |
| Prefix restriction and batched XOR | Checking packed binary row-combination certificates | Implemented in the existing verify_certificate function and exercised on synthetic matrices. |

Sources below are retrieved primary documentation or paper abstracts, not
unverified recalled references. This note makes no claim to have reproduced
M4RI, FFLAS-FFPACK, LinBox, or the TNFS paper.

## Implementation

The previous verifier reconstructed every packed word using a NumPy operation
for each contributing row. To establish that a reconstructed row has leading
column c, only words through floor(c/64) are needed. XOR is coordinatewise:
discarding the suffix cannot change the tested prefix.

Long combinations now gather rows in batches and reduce their checked prefixes
with NumPy bitwise XOR. Each gather holds at most 256 rows and 1 MiB of row data.
The accumulator, reduction workspace, and row indices are additional memory;
the 1 MiB limit describes the gather, not total process memory. Short
combinations retain the scalar loop. Prefixes exceeding the gather budget also
use the scalar path. Duplicate indices are retained, so even multiplicities
cancel exactly. Inputs are not modified.

A negative pivot column is now rejected explicitly. As before, the verifier
checks the independence witnesses that were supplied. It does not independently
prove that those rows span the whole input matrix; this is now stated in its
docstring.

## Correctness

Six unittest cases passed, covering 64 randomized combination fixtures against
both a scalar compatibility control and a Python-integer XOR oracle,
pivot boundaries, suffix changes, forced small batches, repeated indices,
invalid indices/columns, empty placeholders, input immutability, and
certificates generated from small synthetic rank-profile problems.

Run from the repository root:

```sh
python3 -m unittest discover -s tests -p test_gf2_certificate_batch.py -v
python3 tools/gf2_bench_certificate.py --out /tmp/gf2-certificate.json --repetitions 9 --iterations 1000
```

The new tests use unittest because pytest was unavailable in this session.
The existing pytest suite was not run locally. No native elimination, GPU, or
complete cryptographic workload was benchmarked.

## Synthetic timing results

The accepted implementation is recorded in final.json. Its source SHA-256
hashes match the submitted verifier and benchmark script. The baseline verifier
is the pre-change implementation from blob
94f1a925316b183c54cc3fa6488d6ec254cc8f10.

| Fixture | Baseline median, us | Candidate median, us | Ratio |
| --- | ---: | ---: | ---: |
| tiny_single | 3.177 | 2.486 | 1.28x |
| short_combination | 3.551 | 3.716 | 0.96x |
| medium_combination | 21.083 | 15.490 | 1.36x |
| long_early_pivot | 378.225 | 74.311 | 5.09x |
| long_late_pivot | 399.815 | 162.486 | 2.46x |
| wide_late_pivot | 384.395 | 345.207 | 1.11x |

These are phase-specific synthetic observations on a shared host. They do not
establish an elimination speedup or an end-to-end solver gain. Each fixture is
a single known-valid certificate, not a natural distribution of application
certificates. Small timings were noisy; no universal crossover or
hardware-independent ratio is claimed. The three-row fixture was about 4.6% slower in the final sample; gains are not uniform.

Environment: Intel Xeon Platinum 8370C, Linux x86_64, Python 3.12.14,
NumPy 2.3.5, affinity pinned to CPU 0 (NUMA node 0). NUMA memory binding was
not enforced and the memory type was unavailable. Raw wall and process-CPU
samples are retained. Input construction and hashing are excluded from both
arms; reconstruction and verification are included. Arm order alternates.
Peak RSS was not measured; the temporary-gather bound is from the code.

first.json, second.json, and third.json preserve development timing attempts. The first revealed
short-combination overhead; the scalar path was restored. The second showed
substantial timing noise, prompting longer sampling of short fixtures and
process-CPU timing. The third used a semantically equivalent scalar control;
the final runner restores the exact original verifier body (apart from its
function name/type annotation) and increases sampling. Earlier attempts are
not measurements of the submitted final source.

No formal EXP/RUN identifiers or independent-review attestations are asserted.
These files are ordinary engineering validation records.

## Primary references

- Albrecht and Pernet, *Efficient Decomposition of Dense Matrices over GF(2)*:
  https://arxiv.org/abs/1006.1744 — paper abstract inspected.
- FFLAS-FFPACK project documentation:
  https://linbox-team.github.io/fflas-ffpack/ — API and design inspected.
- LinBox project overview:
  https://linalg.org/overview.html — exact sparse/dense method descriptions inspected.
- Al Aswad, Pierrot and Thome, *High-Order Galois Automorphisms for TNFS Linear Algebra*:
  https://eprint.iacr.org/2026/560 and
  https://doi.org/10.1007/978-3-032-35398-6_3 — abstracts inspected.

