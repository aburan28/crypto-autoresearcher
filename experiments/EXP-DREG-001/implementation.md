# EXP-DREG-001 implementation

## Scope

`src/h012c_block_m4ri.py` computes the exact rank over `GF(2)` of a
degree-bounded Boolean Macaulay matrix without materializing one monolithic
rank-by-column basis.  It is an experimental measurement instrument.  It is
not an ECDLP solver and a low-degree rank deficit alone is not evidence of a
faster-than-Pollard-rho algorithm.

The instrument uses the existing chained-Semaev system builder and the T11
support-matched Boolean null.  For every polynomial, the null preserves the
number of monomials at each Boolean degree while replacing those monomials by
deterministic pseudorandom monomials under the recorded seed.  The null and
Semaev arms therefore share the equation-degree profile and Macaulay protocol.

## Exact-rank invariant

Let `S` be the column space already processed.  Each persisted carrier is a
pair `(P, H)` in which the columns of `H` are independent, `H[P, :]` is the
identity, and the carrier is zero on every earlier carrier's pivot coordinates.
For a new column block `B`, the update

```text
B <- B + H * B[P, :]
```

zeros the block on that carrier's pivots without changing its coset modulo
`S`.  Applying all carriers therefore maps the new columns to the quotient by
`S`.  Echelonizing the residual block gives exactly the dimension added by
that block.  Its pivot-normalized residual columns form the next carrier.
Induction over the column partition proves that the sum of block increments is
the rank of the full matrix, independent of partition boundaries.

The required partition-replication control is still necessary: it detects
implementation, serialization, and resume defects even though the underlying
quotient argument is exact.

`partition_control.py` is an independent deterministic positive control for
this invariant.  Version 2 compares monolithic M4RI rank against three block
widths in both split- and unsplit-carrier modes on random full-row-rank,
explicitly row-deficient, and zero matrices.  All 24 comparisons pass; the
versioned outputs, failed-attempt record, and checksums are preserved beside
this document.

## Checkpoint and identity discipline

- The ordered Boolean generator system has a canonical SHA-256 digest.
- Adjacency caches are keyed by arm, `n`, `t`, target, degree, seed, and system
  digest.
- Resume checks the recorded parameter identity and matrix dimensions.
- Every carrier file is written via atomic rename and has a digest in
  `state.json`; all digests are checked before reuse.
- `state.json` is atomically replaced only after a completed block and records
  the next column, accumulated rank, per-block timings, and carrier inventory.
- A completed raw result is emitted only after all full-matrix columns have
  been processed.  Subset-column ranks are not accepted for the Semaev arm.

Carrier matrices are split near 1.9 billion bits per file so checkpoint writes
do not require a second full carrier copy in memory.  The live process retains
the carriers needed for M4RI reductions; peak RSS and wall/CPU time are captured
by `/usr/bin/time -l` in each canonical run.

The macOS data volume reached ENOSPC during an unrelated short Sage control.
Subsequent invocations set `DOT_SAGE` to the ignored
`experiments/EXP-DREG-001/runtime/sage` directory on the external research
volume.  This changes only Sage's cache location; the exact value is retained in
the command/environment artifacts.  ENOSPC during Sage import is classified as
infrastructure failure and cannot be interpreted as mathematical evidence.

## Source provenance

The base implementation and dependencies were mechanically copied from the
read-only research checkout `/Volumes/Volume/research/ecdlp-autolab/src/` on
2026-07-18.  The block implementation was renamed from
`h012c_blockm4ri.py` to `h012c_block_m4ri.py`, then hardened in this repository
with identity-bound caches, matched-null arm selection, checkpoint hashing,
streamed carriers, deterministic resume checks, explicit results directories,
and machine-readable terminal status.

The code hashes frozen by the first canonical validation runs are:

```text
h012c_block_m4ri.py  0eb38126998c73601687e248439a05f39038e762d5a5b99009598b67e59a0bbb
h012_peel_rank.py    c46c871bf22ef3fd007802eae2bb3e0be5357f521126f1ec3eb8a42afbb529b8
macaulay_export.py   c00b8aad9ad47f8a3f09c39f6b65062a37562703bfd1c4f6159b1e54b1dbad97
ic_first_fall_fast.py f1c98bd8642df226760f43038d6687e73794d04b9c7a9073f244b8a0433fad61
semaev_tree.py       e9f1681b4e422f7a67176fffd3e5f91ab7a95c9fddc1eb925c2bb0a93a9becef
```

These hashes, the Git commit and dirty-tree digest, the exact command,
environment, seed, stdout/stderr, raw result, resource measurements, and
checkpoint digests are repeated in each run package.

## Validation and interpretation gate

Past-wall measurements cannot be interpreted until the instrument reproduces
the frozen Semaev anchors and the support-matched null anchors in
`specification.yaml`.  A mismatch returns the experiment to instrument
validation.  Timeout, OOM, cache corruption, or a failed resume is
infrastructure evidence only.  A valid toy-scale deficit is interpreted only
against the frozen growth, `d_reg`, and `d_ff` criteria and cannot establish a
cryptographic-scale or generic-group breakthrough.
