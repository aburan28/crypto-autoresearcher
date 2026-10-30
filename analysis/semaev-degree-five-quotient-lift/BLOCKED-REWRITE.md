# Block triangular rewrite candidate

This separate implementation changes the provisional-map construction in
`quotient_lift_batched.cpp`. The running high-memory campaign still uses its
frozen original binary. The new candidate has passed software equivalence
controls, but has no frontier execution or measured speed advantage yet.

For each nonstandard high monomial i, the original algorithm computes

    map[i] = sum_q seed[divisor[i], q] * map[target(missing[i], q)]

over F2. Triangularity requires every contributing target to have index greater
than i. Standard high monomials already have their unit images, and all lower
degree monomials already have their seed images.

The candidate processes a block [start,end) in descending index order. For
each missing-variable group, it first computes a matrix product using only
targets at or above end. Those images are final by induction over previously
processed blocks. It then visits the block's rows in reverse order, adding
exactly the contributions with targets below end. Every such target is still
strictly above the current row, so its image is final by induction inside the
block. The two disjoint contributions sum to the original recurrence. The
same triangularity rejection remains in place. This is a written equivalence
argument, not an independently reviewed or proof-assistant-checked theorem.

No closure relations, coordinate choices, early-exit conditions, certificate
format or final export operations change. The candidate remains an untrusted
producer: the original independent certificate checker is required for every
scientific inference. A quotient killing the constant remains inconclusive
about membership in the true closure.

The allocation estimate includes an additional conservative allowance for
the target-index table, a 4096-row panel, its product, and coordinate actions,
even when the relation chunk is smaller. Process memory limits remain
necessary. The software controls do not establish frontier admission.

## Retained controls

`test_blocked_rewrite.py` compares four generic systems at block sizes 31,
257, and 4096 against the frozen batched exporter. All 12 candidate outputs
are byte-identical, and each output satisfies the independent small-system
conditions. The cases cover internal and external dependencies, multiple
blocks, a partial final block, and non-word-aligned quotient coordinates.
The largest generic control has 16 Boolean variables; this is not a scale
claim for the frontier systems.

Three Semaev cascades also pass the original standalone checker at degrees
3,4,5. All nine certificate files match the prior batched cascade controls
byte for byte and match direct closure codimensions.

Receipts and raw artifact pointers are in `validation/blocked-rewrite-20261029/`.
Builds use g++ -O3 -march=native, the retained static M4RI library, and
REWRITE_BLOCK_ROWS=31,257,4096. Source and binary hashes are in summary.json.
The native build is not a portability assertion.

Before scientific use: freeze a separate instrument/protocol, retain an
actual run's complete artifacts, and obtain original-checker acceptance for
any candidate certificate. Do not replace the active campaign's binary or
interpret these controls as a speed measurement.

## Baseline x86-64 build qualification

The separate portable build uses `-O3 -march=x86-64 -mtune=generic` and the static M4RI build configured with SIMD flags disabled. It passes the same four generic cases at all three block sizes: 12 candidate comparisons are byte-identical to the portable batched reference, and all 16 reference/candidate outputs match the prior native build. The nine Semaev stage certificates pass the original checker, match direct codimensions, and match the previous native certificate bytes.

[Qualification records](validation/blocked-portable-20261029/qualification.json) bind compiler details, library/source/binary hashes, exact build commands, complete control outputs, and the artifact-store archive containing the binaries. This is local software qualification, not a universal CPU compatibility assertion. Per-node controls remain required. No frontier trial, performance comparison, or scientific admission was performed with this build; the active workers retain their frozen instruments.
