# Independent review of the BINSTD encoded Lean certificate

**Date:** 2026-10-26 UTC
**Producer snapshot:** `6409590d9bf26201956095e87f36f25d346cba68`
**Precommitted plan:** `cab536aaa7ddc70016acfaff741b5478b3261dc1`
**Review tasks:** `TASK-20261026-538444` (source and Lean), `TASK-20261026-7ab9cb` (blind arithmetic); archival task `TASK-20261026-034c33`.

This is a technical review of a narrow formal artifact. It changes no official hypothesis, experiment, evidence, or knowledge status. [claim-verdicts.json](archive/claim-verdicts.json) is the machine-readable, claim-by-claim result; [diagram.svg](diagram.svg) shows its boundary, and [report.pdf](archive/report.pdf) is the inspected reading copy.

## Observation

The producer theorem states eight conjuncts about the source-defined finite bitmask predicate: three positive masks (`131081`, `313`, `471`), exact candidate counts (`510`, `30`, `30`), and two false controls (`131073`, `257`). Reviewer J1 checked all eight frozen source hashes against the producer Git tree, then independently ran direct Lean 4.35.0-rc1 compilation, exact type prints and seven axiom queries. The four check processes exited `0,0,0,1` in order; the final `1` was the expected rejection of a deliberately false control. Six theorem audits reported only `propext`; the count theorem reported no axioms. J1 retained the failed initial run caused by a 2 GiB virtual-address cap, then retried with a single worker thread under the task's observed resident-memory budget.

Reviewer J2 read only the mathematical statement, its own handoff and its own artifacts. Its independent implementation retained each of 1,110 monic divisor candidate rows. All five truth values and candidate counts match J1's source-guided replay. Both known-reducible controls have zero remainder modulo bitmask `3`; they need 17 and 8 XOR reductions respectively, and one fewer step leaves an unfinished remainder. [reconciliation.json](reconciliation.json) checks both reports' counts, values, first zero divisors and direct Lean exit codes. Its source is [reconcile.py](reconcile.py).

The first independence-check call could not parse the reviewers' sealed top-level YAML attestations. Each reviewer added a new checker-compatible attestation without editing the sealed one. The same precommitted plan then passed `tools/check_review_independence.py` with both joints owned, blindness respected and controls declared. Both outcomes and the exact commands are retained in [independence-check.json](independence-check.json). The checker validates declared reads and ownership; it cannot prove a session made no undisclosed read.

## Comparison and scoped verdicts

| Claim | Machine status | Semantic fidelity | Review outcome |
| --- | --- | --- | --- |
| Five exact finite encoded predicate values and candidate counts | Passed by two independent finite implementations | Faithful within the specified bitmask algorithm | **Validated within that finite scope** |
| Exact combined Lean declaration and seven direct axiom outputs | Passed by fresh pinned direct Lean | Faithful to the narrow source-defined theorem | **Inconclusive as a complete repository certificate** pending full Lake target gate |
| Archived direct-check receipt | Passed against frozen hashes and fresh direct replay | Faithful to a direct source check | **Validated within direct-check scope** |
| Full Mathlib/Lake workspace and formal target verifier | Not verified | Not reviewed dynamically | **Inconclusive** |
| Irreducibility in `(ZMod 2)[X]` or Frobenius/normal-basis identification | Not verified by this declaration | Partial correspondence of displayed exponents only | **Inconclusive** |

The current GitHub Actions formal job had zero executed steps and an account payment/spending-limit annotation; this is an infrastructure failure, not a theorem failure. Another owner held the host's formal workload lane during review, so this review did not start a full Mathlib build. The source contains no checked map from natural-number masks to `(ZMod 2)[X]`, no proof that its `remFuel` computes polynomial remainder, and no irreducibility or Frobenius bridge. Those are separate proof obligations, not consequences of the eight encoded Boolean conjuncts.

## Next checks

1. Run the frozen exact-pin Mathlib/Lake workspace and named-target verifier gate when the host has exclusive, budgeted build ownership and at least 16 GiB reserve. Preserve the producer revision and complete input hashes.
2. Add a checked mask-to-polynomial map, prove the encoded remainder agrees with polynomial division for nonzero divisors, and derive irreducibility in `(ZMod 2)[X]` from the bounded divisor criterion.
3. Prove or explicitly delimit any normal-basis/Frobenius interpretation before using this certificate to support that larger claim.
4. Repair the GitHub Actions billing or spending-limit gate, obtain current-head required checks, and only then use the user's approved merge/Pages publication path.

No scientific run, EKS job, Diem generator, source freeze followup, rho cutover, instance, quota change, or Pages deployment was made as part of this review.
