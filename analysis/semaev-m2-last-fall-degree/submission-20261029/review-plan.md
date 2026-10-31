# Proof review plan, written before dispatch

Status: scoped technical review, not a ledger promotion. Archive owner T-778.
Prior: the trace normalization and Boolean closure certificate construction
appear plausible; the universal first-fall summary is more general than its
listed hypotheses and needs careful convention reconciliation.

One independent reviewer owns these joints:

* Re-derive the trace identity from the S3 formula, then inspect whether a
  nonzero trace residual is guaranteed and whether it is already a generator.
* Compare raw-list homogeneous-top syzygies, the KW span definition, the
  nonzero Petit--Quisquater cancellation definition, and closure-filtration
  new falls. Use the checked n=4 counterexample as a proves-too-much control.
* Check Propositions 1.1--1.5 and the need for unsatisfiability or a separate
  solution count. Test whether a certificate with an oversized kernel could
  be accepted while dimension equality is false.
* Check Theorem 2.5 and Proposition 3.7 bounds, particularly the branching
  degree accounting and target nonzero assumptions.

Inputs: theorem-dossier.md, results/verification-correction-20261019.md,
verify/cert_check.py, problems/semaev-degree-two-fall-nonzero-bridge.md,
and the primary KW paper. Blind re-derivation is from the formula and
definitions before reading the corresponding proof; any unavoidable exposure
is disclosed. The reviewer is independent of this session's new code and
manuscript; source-visible review is not fully blind.

Deliverable: a read-only findings report with exact hypotheses, any concrete
counterexamples, and safe theorem wording. Do not change original artifacts,
run large computations, or assert external human review. Parent archives the
returned report additively under this study directory. No official scientific
status changes are authorized by this review.
