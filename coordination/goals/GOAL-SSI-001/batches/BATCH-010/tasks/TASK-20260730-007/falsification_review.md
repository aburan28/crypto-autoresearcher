# Falsification review — RT-20260730-007

## Verdict

**CONFIRM.**

The BATCH-010 producer's narrow result survives independent checks against
Coordinator-committed snapshot
`e512b1aa044c17305da4290e2680c1665cd429a9`. O5 is now independently
reproducible for the checked text and conservative symbolic-cap implication
against the archived author-hosted PDF, with the stated qualification that
canonical ePrint byte identity is unverified. The joint worksheet does not pass,
so `FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED` remains the supported disposition.

## Immutable-snapshot and PDF check

The reviewed snapshot is reachable from review HEAD
`e47a83ed0115c3c85676bd928d0cf344a45b1069`; its parent is
`1e43478867404f1721aa7574ffcc158b53dee78e`. Its commit diff adds exactly the
six TASK-20260730-005 producer artifacts and the TASK-20260730-006 receipt.
No working-tree producer artifact was treated as evidence.

The PDF blob was streamed directly from the reviewed commit:

```text
git show e512b1aa044c17305da4290e2680c1665cd429a9:<PDF-path> | shasum -a 256
d4785e2863eebe97eb3a2909e02d669d138b2080c6e96e42c70d8d4fd2e89675  -

git cat-file -s e512b1aa044c17305da4290e2680c1665cd429a9:<PDF-path>
358133
```

The digest matches `source_manifest.yaml`, `classification.yaml`, and
`snapshot-receipt.json`; the size matches the manifest. Hash check: **PASS**.

The receipt remains internally marked `commit_sha: null` and
`pending_post_commit`. Independent Git checks establish reachability and exact
scope for this review, but the receipt's pending marker should not be described
as a durable post-commit-verifier acceptance.

## Independent quotation spot-check

Fresh `pdftotext -layout` extraction was run on the committed PDF stream.

- Physical PDF page 20 gives Equation (4.1) as
  \(36\widetilde L(2/(1-\delta))^d\), with \(\widetilde L\) an upper bound on
  typical phase-vector length, \(\delta\) the discard probability, and \(d\)
  the sieve-tree depth. The subsequent derivation uses input and output
  lengths bounded by \(D\) and nine QRACM lookups into \(D\) cells.
- Physical PDF page 18 gives the Figure 1 caption with
  \(\alpha=1/2\), \(\widetilde L_{\max}=8L\), and Equation (3.5). The following
  bullet imposes \(8L\) as a maximum, says generated vectors are almost always
  within a factor of eight, and enforces the hard bound by partial measurement.

These material words and constants match the BATCH-009 quotations. No material
quote mutation was found. The source does **not** literally substitute \(8L\)
for \(\widetilde L\) in Equation (4.1); \(D=8L\) is a conservative FC0
derivation for charged collimations in the pinned Figure 1 row, not a
source-reported typical-value equality or a complete attack estimate.

## O5 integrity judgment

O5 is **independently source-verified for the archived text scope, with
provenance qualification**.

The committed bytes identify Peikert's paper by title, author, and February 23,
2020 date, and reproduce all checked final-revision locators. The immutable
author-hosted copy is sufficient to independently verify the narrow textual
claims. The canonical ePrint PDF endpoint returned HTTP 403, so byte-for-byte
identity with that endpoint is not established. The producer states this limit
and does not overclaim canonical byte equality.

The cheapest remaining O5 control is to compare the canonical object when it
becomes obtainable. A byte mismatch would require enumerating differences and
checking whether any affects Equations (3.5), (4.1), the 8L statement, or their
locators; it would not by itself negate the text observed in the archived
author copy.

## QUERY_MEMORY falsification

The worksheet supports retaining `QUERY_MEMORY` unreconciliation:

1. The source's Equation (3.3) model, empirical per-run factor, and
   \(\widetilde Q_{\rm total}\) label do not define one recovery stopping law or
   identify the aggregate as
   \(\mathbb E[\sum_{k\le\tau}Q_k]\).
2. Fresh-sieve retries, punctured regularization, recovery, postprocessing,
   verification, and terminal-tail entry are not jointly costed under one law.
3. Nonnegative random-sum notation permits extended expectations but does not
   prove finite query, repeated-sieve, postprocessing, or classical-tail cost.
4. Equation (3.5) and the 8L cap bound a reusable per-vector QRACM row, not
   concurrent vectors, coherent workspace, classical backing, oracle state,
   cleanup state, or tail memory on a global schedule.
5. Source assumptions and empirical statements are not mapped into one final
   operational failure event.

The cheapest memory counterexample keeps every vector at or below \(8L\) while
delaying cleanup so arbitrarily many retry objects overlap. O5 remains true but
global memory grows with overlap. The source does not reject this mutation.
A heavy-tail stopping mutation likewise can preserve cited per-run facts while
making one required expected random sum infinite.

This is a supported gate diagnosis, not proof that reconciliation is impossible
or that QUERY_MEMORY is the only obstruction.

## Baselines and scope

There is no complete attack point to compare numerically with Pollard rho,
BSGS, or a specialized frontier. The closest specialized baseline remains
Peikert's own final binary c-sieve Figure 1 row under explicit QRACM and
optimistic oracle assumptions. This batch verifies source text and diagnoses
missing joint semantics; it supplies no new query/time/memory vector and no
Pareto delta.

Relation collection and rank are not the mechanism of the cited hidden-shift
sieve. Representation, complete labeled-state oracle realization, source
recovery, residual descent, verification, and error composition are not
instantiated end to end here. No conclusion transfers to generic ECDLP,
SIDH/SIKE, SQIsign/CGL path finding, numeric CSIDH security, parameter sizing,
the closed IDEA-20260725 lanes, a breakthrough, or GOAL completion.

## Recommended next gate

Keep `FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED`. Next require one source- or
code-compatible joint stopping law and deterministic global liveness schedule
that:

- proves finite query, repeated-sieve, postprocessing, and tail expectations;
- bounds coherent, QRACM, classical-backing, and tail memory on one timeline;
- rejects the heavy-tail and overlap mutations; and
- maps all component errors to one final operational event.

Do not advance to a uniform-oracle, numeric-security, breakthrough, or
completion gate until that joint control passes.
