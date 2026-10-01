# P9: pair-table reuse within a cold point-decomposition job

This guide explains the frozen [protocol](protocol.json), approved by
[DEC-20260922-10be27](../../ledger/decisions/DEC-20260922-10be27.md).
The JSON protocol is normative. This document contains no measured P9 result.

The question is whether the orbit-canonical pair table keeps its total-cost
advantage when a fresh process builds the table once and uses it for many
point-decomposition queries. The earlier P8 experiment measured a fresh build
for each query. A construction saving cannot be multiplied by the number of
queries when construction occurs only once.

## Fixed comparisons

| Regime | Binary field | Signed factor-base points | Seed orbits | Queries per job |
| --- | --- | ---: | ---: | --- |
| N19/K4 | GF(2^19), modulus x^19+x^5+x^2+x+1 | 152 | 4 | 1, 32, 512 |
| N23/K16 | GF(2^23), modulus x^23+x^5+1 | 736 | 16 | 1, 32, 512 |

Both regimes use the binary curve y^2+xy=x^3+x^2+1. Field degree and base size
change together. Differences between the regimes therefore cannot isolate
field scaling.

The expanded arm stores distinct full-point pair sums and inline witness
indices. The canonical arm stores normal-basis x-orbit representatives with
full witness information, then recovers the sign and inverse Frobenius shift
on a hit. Both use the accepted P8 batch arithmetic and query ordering.

The N19 seed points are fixed by the prior experiment. The N23 base uses the
first 16 distinct valid signed Frobenius orbits found by the protocol's
SHA-256 coordinate recipe. Every cold job reruns and validates that recipe;
it receives no retained base or pair table from the controls.

## Query panels and measured boundary

A deterministic, public control generator produces eight panels of 512 points
per regime. Scalars used to create those public points remain in control-only
metadata. Each measured worker receives the Q-only panel. Panels are not
selected by whether a decomposition exists. M=1 and M=32 use prefixes of the
same M=512 panel, so those samples are nested.

The schedule contains 384 fresh native processes:
2 regimes × 3 query counts × 8 panels × 4 technical repetitions × 2 arms.
Arm order alternates by repetition; paired blocks are sorted by the frozen
hash rule. No failed job is replaced or retried.

Primary wall time runs from native process launch through its sole reap.
It includes input reading, fresh base construction and validation, normal-basis
preparation where needed, one table build, all M queries, witness recovery and
verification, and output. Every query computes all Q-P candidates in a batch,
then probes the sorted base until the first hit or exhaustion. Negative queries
remain in the total cost. T_job/M is a derived average, not a separate timing.

Compiler cost, controls, independent replay, parent validation, hashing and
archival costs are retained separately. Logical table payload and process RSS
are distinct quantities; CPU scopes are not added together when they overlap.

## Correctness before timing

One native control process handles both regimes. It checks the declared
fields and group orders, complete normal-coordinate round trips, independent
field and group controls, exact bases, complete pair-sum support, every stored
canonical row, recovered witnesses, panels and exceptional points. It also
requires actual rejection of false transport, sign, key, sum, curve and base
certificates.

The independently written Python checker reconstructs the field arithmetic,
base recipes, public panels, full pair-sum sets, canonical orbit expansion and
query witnesses. It must pass before a separate benchmark admission is
committed. Source, binary and all admitted input bytes are hash-bound. A
control failure or missing artifact stops the dependent stage and asserts
nothing about the mathematical hypothesis.

## Predeclared interpretation

The only primary cell is N23/K16 with M=512. For each panel and arm, take the
median of its four technical repetitions; divide canonical by expanded to get
eight paired panel ratios, then take their median. The fixed bootstrap uses
10,000 resamples of those eight panels and type-7 percentile endpoints.

The prediction requires valid controls, valid independent replay, all 384 jobs
valid, a primary median ratio at most 0.90, and a 95% upper endpoint below 1.
All five other cells are descriptive. The bootstrap describes the eight fixed
public lists; it does not establish an IID population result or a scaling law.

After the raw snapshot, separate source and permanently blind review sessions
check implementation, witnesses, timing custody and the paired calculation.
Only a Coordinator decision can state the scoped disposition. This experiment
measures finite point decomposition. It does not supply a new full IC/rho
comparison, a logarithm-recovery result, or an asymptotic security claim.
