---
id: KN-TECH-036
type: technique
title: Public ECDLP record computations as baseline calibration
tags: [record-computation, calibration, certicom-challenge, secp112r1, sect113r2, ecc2k-130, prime-field, binary-field, pollard-rho, distinguished-points, baseline, cost-model, ecdlp]
confidence: reported
complexity: public completed records -- 112-bit prime field (2009, ~2^56 iterations, ~215 PS3s, ~6 months); 117.35-bit binary field (2016, ~2^60 iterations, up to 576 FPGAs, >6 months)
applicability: sanity-checking any claimed cost, advantage, or feasibility statement about ECDLP at or above 100 bits
source_refs: [KN-LIT-095, KN-LIT-096, KN-LIT-097, KN-LIT-012, KN-TECH-006]
added: 2026-07-24
superseded_by: null
---

## The record set
| Instance | Field | Bits | Work | Hardware / duration | Source |
| --- | --- | --- | --- | --- | --- |
| secp112r1 | prime | 112 | ~8.4e16 (~2^56.2) expected iterations | ~215 PlayStation 3s, Jan-Jul 2009 (~3.5 months if continuous) | KN-LIT-095 |
| sect113r2 | binary | 112 | 82.2M distinguished points vs 59.5M expected | up to 120 Spartan-6 FPGAs, ~48 days | KN-LIT-097 |
| target117 over F_2^127 | binary | 117.35 | ~2^60 iterations | up to 576 FPGAs, >6 months | KN-LIT-097 |
| ECC2K-130 (Certicom) | binary Koblitz | 131 | ~2^60.9 iterations *estimated* | multi-platform CPU/GPU/Cell/FPGA effort | KN-LIT-096 |

The 109-bit prime-field record dates to October 2002; the Certicom challenges
over 109-bit fields were all solved between April 2000 and April 2004
(KN-LIT-096). ECC2K-130 is listed as an estimate, not a completion: KN-LIT-096
is a design and status report, and this program has not established whether or
when that challenge was finally solved.

## How to use these numbers
**As a feasibility ceiling.** The largest publicly completed ECDLP is 117.35
bits. A 256-bit curve requires about 2^128 iterations against that record's
2^60 -- a gap of roughly 2^68. No mechanism can be validated end-to-end at
cryptographic size within any plausible budget, which is precisely why
GOAL-CRYPTO-001 requires a certificate-verified *advantage over a matched
baseline* under a charged cost model, and not a solve.

**As a variance reference.** The sect113r2 run needed 82.2M distinguished
points against an expectation of 59.5M -- about 1.38x its expected work, on a
correctly implemented attack. Single-instance timings fluctuate at that scale,
so an observed speedup of tens of percent on one instance is noise, not
evidence. This is the empirical grounding for demanding replicated runs with
distinct seeds.

**As a reminder that the baseline is already optimized.** Every record above
uses parallel collision search with distinguished points, and the binary-curve
records additionally claim negation and automorphism speedups
(KN-TECH-018) before the attack starts. The baseline to beat is the optimized
one; comparing against a naive serial rho is a mis-charge of the same kind as
using #E instead of the prime subgroup order.

**As available test instances.** secp112r1 has a published solution
(KN-LIT-095 gives the target point, the prime subgroup order, and the
recovered logarithm), which makes it an end-to-end test of a solver and its
certificate machinery against a known answer at a nontrivial size.

## Applicability limits
Three of the four records are over binary fields with exploitable curve
structure; only KN-LIT-095 is a prime-field ordinary-curve result, which is
the class this program targets. Hardware-hours are not portable across eras --
2009 PlayStation clusters and 2016 FPGA farms are not comparable to current
accelerators -- so these entries calibrate *iteration counts and variance*
reliably and *wall-clock feasibility* only loosely. The figures are as
reported by the authors and were not independently reproduced.

## Verified vs reported
All figures above were read from the primary PDFs (see KN-LIT-095, -096, -097)
but none was reproduced or independently checked, so confidence is `reported`
rather than `established`. The 2^68 gap calculation and the variance argument
are this program's own arithmetic over those reported numbers. Whether more
recent records exist beyond 2016 was not established by this survey and should
be re-checked before any claim of "current record" is made.
