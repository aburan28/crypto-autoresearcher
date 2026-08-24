# Arm D design note — right-table random-from-F_p null

This is a Coordinator design artifact only. It does not approve, implement, or
execute `EXP-XOR-4ded1d`, and it changes no existing hypothesis status.

Archive retry note: the first snapshot attempt was not admitted because its
commit message omitted required task identifiers; this package is being
re-snapshotted before any independent review.

The prior x-oracle experiment compared the true right-table key relation against
a random predictor on the left query side. That comparison cannot distinguish
oracle information from a table-distribution or MITM-strategy artifact. This
successor keeps the actual ordered right-half pairs and all table workload, but
replaces each right-pair key `x(P2+P3)` with

```text
u_i = SHA256(seed || cell_id || tuple_index) mod p
```

with replacement. Collisions are retained and reported. The left query remains
the true `x(P1)`. The diagnostic comparison is Arm B versus Arm D, with Arm A
as the exact relation-set baseline. A/B/D must use the same curve selection,
factor-base order, tuple order, query count, candidate-verification path, and
charged field-operation accounting.

The experiment is deliberately toy-only (`m=3`, `p` in `{101,103,107,211}`,
`b` in `{0.4,0.5}`, five seeds). Primary measurements are relation-set recall
of B against A and the independent-group mean of `yield_B - yield_D`.
Secondary measurements include field operations, hash operations, key
generation, candidates verified, false positives, right-pair cardinality, key
occupancy/collisions, memory, and wall time.

The declared interpretation is narrow: a controlled positive B-D contrast would
support the claim that the true left/right key association matters for this toy
MITM strategy. It would not establish an ECDLP attack, a sub-rho result, an
asymptotic improvement, or a crypto-scale advantage. A null result would weaken
only that strategy-specific interpretation. Infrastructure, provenance, or
control failures invalidate the cell and are not mathematical evidence.

The design remains pending independent review and Coordinator approval. The
harness preflight currently has no usable inference backend, so no Executor or
review task is dispatchable yet.
