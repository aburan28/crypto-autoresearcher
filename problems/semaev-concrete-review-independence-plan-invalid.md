# Concrete Semaev review plan fails the independence checker

- **Status:** resolved by prospective BATCH-016711; the original frozen batch remains invalid
- **Kind:** review-protocol and machine-check gap
- **Affected work:** [frozen batch plan](../coordination/formal-reviews/BATCH-semaev-concrete-20261031/review-plan.yaml), [J1 source review](../coordination/formal-reviews/BATCH-semaev-concrete-20261031/reviews/T-1060-j1/REVIEW.md), [J2 Lean review](../coordination/formal-reviews/BATCH-semaev-concrete-20261031/reviews/T-1061-j2/REVIEW.md), and [J3 blind derivation](../coordination/formal-reviews/BATCH-semaev-concrete-20261031/reviews/J3/report.md)
- **Next action owner:** Coordinator for any separately scoped follow-on claim
- **Last updated:** 2026-10-31

## Problem

The three technical joints have been reviewed at their stated scopes, but `tools/check_review_independence.py` cannot certify the round's declared independence. The plan was committed before reviewer dispatch and used Conductor `T-*` labels where the checker requires native `TASK-*` identifiers. It omitted the required failure signature for the proves-too-much control and the blind re-derivation's quantity, protected-source list, and assignee. Rewriting the frozen plan after the reviews would falsely make late declarations appear prospective.

## Evidence and uncertainty in the original round

- **Observed:** The [verbatim checker output](../coordination/formal-reviews/BATCH-semaev-concrete-20261031/reviews/T-1061-j2/independence-check.txt) from `python3 tools/check_review_independence.py --batch coordination/formal-reviews/BATCH-semaev-concrete-20261031` reports 11 findings and exits 1 on the archived J2 tree. It sees one recognized attestation; it cannot match the J1 and J3 reports to the plan's declared `T-*` owners. The missing fields are reported explicitly.
- **Observed:** J1 independently regenerated the four Boolean equations from the one archived draw, the 28/80 ordered row sets, and the source-to-Lean witness binding; its mutation and XOR-parity controls failed as expected. J3 independently reconstructed the 11/53 ranks and a distinct valid separator after a blind input freeze. J2 checked the finite Lean statement and a separator mutation; the hosted [PR #2805](https://github.com/isogeny-labs/crypto-autoresearcher/pull/2805) named receipt reports a full workspace build, `machine_verified`, and a passing transitive axiom audit for `concreteNewFall` on exact source bytes.
- **Observed:** J2 inspected the checker addendum contract. It can reassign owners and widen an existing protected-source list, but it cannot insert an absent original blind quantity or assignee or add the missing failure signature through its normal addendum path. The committed plan and reports remain intact.
- **Derived:** The technical checks support their scoped findings, but the batch cannot claim a passing machine independence gate or a complete `validated_scoped` review outcome from this round. This is a protocol failure, not evidence that the finite theorem is false.
- **Missing capability at the original round:** a valid prospective plan with native review task IDs, explicit negative-control failure signature, blind quantity and `blind_from` protection, an assigned blind reviewer, exact report paths, and three independently frozen attestations.

## What would unblock it

- [x] Create and commit a *new* review-round plan before dispatch. Name the exact frozen theorem/source inputs, native `TASK-*` owners, protected blind sources, re-derived quantity, and falsifying control behavior. Preserve this round as history; do not edit its original plan or attestations.
- [x] Have independently assigned reviewers attest their actual reads and judgments under the new plan. Reuse the earlier calculations as cited prior evidence only, with their original provenance; do not pretend they were produced under the new plan.
- [x] Run `tools/check_review_independence.py` against the new round, retain the exact output, and compose the source, Lean, blind, and execution boundaries into a reviewed report with its graph/diagram and PDF.

## Completed discriminating step

The following step was completed in [BATCH-016711](../coordination/formal-reviews/BATCH-016711/review-plan.yaml). The original instruction was: freeze a new plan that passes the checker structurally *before* any new reviewer starts, then have an independent blind reviewer test whether the finite witness and separator can be recovered without reading the producer's implementation or earlier reviewers' verdicts. A failing structural preflight stops dispatch; a failed blind result or source hash mismatch is retained as a scoped finding. No local Lean build or scientific run is required merely to repair the review protocol.

## Resolution and history

Open at the original round: J1 and J3 merged in PRs #2806 and #2807; J2 merged in PR #2809. Their scoped technical evidence remains available. Those merges did not repair the frozen batch plan.

Resolved prospectively on 2026-10-31: [PR #2813](https://github.com/isogeny-labs/crypto-autoresearcher/pull/2813) froze BATCH-016711 and a clean blind bundle before reviewer dispatch; [PR #2814](https://github.com/isogeny-labs/crypto-autoresearcher/pull/2814) published the J1/J2/J3 and archival handoffs. Three new independent reports, raw checks, read attestations and their hashes were archived in [PR #2815](https://github.com/isogeny-labs/crypto-autoresearcher/pull/2815). The composed checker [passes with zero findings](../coordination/formal-reviews/BATCH-016711/synthesis/checker-output.txt), and the [review PDF](../coordination/formal-reviews/BATCH-016711/synthesis/report.pdf) records a `validated_scoped` outcome for the one finite Boolean witness. The original invalid plan and its 11-finding output remain unchanged as historical evidence. A new draw or broader theorem would require its own binding and review.
