# TASK-20260723-503 falsification review

## Review boundary and verdict

This independent review is anchored to Coordinator-committed snapshot
`2197d98ed254abe38a2485e01c5231cdd00f5679`. The commit is reachable from
`HEAD`, changes exactly the two producer artifacts and their snapshot receipt,
and the two producer blob hashes match the receipt.

I **uphold `NO_ADMISSIBLE_NEXT_MECHANISM`**, narrowly. The snapshot contains no
new operation to admit, so it cannot support a proposal, experiment, or
sub-rho claim. This is a checked-snapshot disposition, not an exhaustive
literature result or an impossibility theorem. `breakthrough_claimed` remains
`false`.

There are two fatal objections to the producer's future admission gate as
written. Neither supplies a candidate or overturns the no-candidate verdict:

1. The gate has an unclassified interval between its campaign threshold
   \(0.45\) and its fail boundary \(0.50\).
2. Coordinate erasure plus naming a non-generic step does not rule out an
   \(O(1)\)-overhead generic simulator or a target-independent identity.

## Novelty and renamed-backend leakage

There is no positive novelty claim to confirm because no mechanism is
proposed. The producer correctly leaves `novelty_status: unverified` and
rejects backend-only substitutions: a solver, term order, sparse linear
algebra routine, compact-\(z_R\) payload, common-factor update, or unnamed
zero-minor locator is not new if its relation interface and source obligations
are unchanged.

The exclusion must remain interface-specific. EV-CRYPTO-002 weakens only the
named compact-constructor sheet. EV-CRYPTO-004 is inconclusive and therefore
does not close all hyperplane-signature or zero-minor variants. A future
explicit operation that changes the semantics, repairs manuscript alignment,
and carries a complete cost path remains logically open. This limitation does
not rescue anything in the present snapshot.

## Oracle-leakage challenge

The source-relabel and scalar-blind target controls point at the right failure
mode. An aggregate endpoint, determinant, zero minor, or existence bit is not
an ECDLP relation until exact signed source occurrences can be replayed.
Duplicate coordinates, deck membership, signs, and target masking matter;
target-fitted coefficients, a supplied source object, or an uncharged source
dictionary are oracle leakage.

The cheapest source mutation holds all public endpoints fixed while permuting
duplicate occurrence labels and deck membership. A valid method must still
return a verifiable signed tuple, or charge ambiguity and all restricted
queries used to recover it. Subset restriction is not free: rebuilding
coefficients or state for each dyadic replay call belongs in setup, query
work, and live memory.

The generic-encoding control needs one stronger obligation. Showing that a
coordinate expression ceases to typecheck on opaque labels proves coordinate
dependence, not useful non-generic information. The sheet must state the exact
target-dependent transcript or relation that an \(O(1)\)-overhead generic
simulator cannot reproduce. Universal identities and aggregate statistics
receive no advantage credit.

## End-to-end path and cost objections

The producer correctly refuses to equate a first \(N^{0.50+o(1)}\) collision
with a complete route. The route still needs \(\Theta(B)\) independent rows,
factor logs, exact source recovery, fresh scalar-blind descent, sign/scalar
orientation, and final public group-equality verification.

The current explicit six-list control remains worse than rho:

| Stage | Work exponent | Memory exponent |
|---|---:|---:|
| Complete explicit relation campaign | \(0.60\) | \(0.60\) materialized |
| Optimistic sparse factor-log solve | \(0.40\) | \(0.20\) |
| Fresh blind descent | \(0.60\) | \(0.40\) reusable pair state |

An unspecified streaming schedule may reduce represented state to \(0.40\),
but it does not reduce the \(0.60\) collection or descent work.

Two undercharges remain in the future symbolic ledger:

- Independently checking rank detects a deficient batch but does not pay for
  collecting replacement batches. Positive rank credit \(r\) requires a
  deterministic guarantee or a rank-yield tail bound plus charged retries.
- The formula does not separately expose every restricted source-unranking
  call or target-side output/replay state. Those costs must be assigned
  explicitly rather than absorbed into prose about ambiguity and failed
  branches.

The cheapest formal counterexample to gate adequacy is zero-compute. Set
\(\lambda=0.47\), \(\mu=0.40\), keep the fresh query within \(N^{0.25}\), and
satisfy every semantic and certificate condition. The candidate does not pass
because \(0.47>0.45\), but it does not fail under the stated cost condition
because \(0.47<0.50\). The same admission template must classify any
\(\lambda>0.45\), \(\mu>0.45\), or online-bound violation as an admission
failure. The rho boundary is a baseline, not the campaign threshold.

## Matched baselines

- **Pollard rho:** expected \(N^{1/2+o(1)}\) group work and \(N^{o(1)}\)
  serial memory. This is the decisive generic baseline.
- **BSGS:** \(N^{1/2+o(1)}\) work and \(N^{1/2+o(1)}\) memory. The producer
  omitted this explicit row, but BSGS does not rescue an \(N^{0.60}\) route
  and is less attractive than serial rho in memory.
- **Closest specialized control:** the source-labelled six-list
  Abel--Jacobi/kSUM-style route in the snapshot costs \(N^{0.60+o(1)}\)
  complete collection and fresh descent, with \(N^{0.60+o(1)}\) materialized
  memory or an unproved \(N^{0.40+o(1)}\) streaming state. Cited setup/query
  rectangles do not supply a source-recovering end-to-end algorithm and
  cannot be credited with free rank or descent.

The missing BSGS row is presentational. The closest specialized route still
loses rho on complete work.

## Cheapest-gate assessment

A theorem-only `explicit_operation_and_full_cost_admission_sheet` is the
right cheapest *form*: a toy fixture cannot manufacture a missing identity,
source inverse, or asymptotic proof. It is not decisive as presently written
because of the threshold gap, simulator gap, and rank/replay accounting
ambiguity. These are repairs to a future admission template, not grounds to
run a gate now. Because the present package has no candidate, this review
confirms `NO_ADMISSIBLE_NEXT_MECHANISM` and proposes no next gate.

## Narrowest remaining open problems

1. **SOURCE-LOCATOR-OPEN:** construct a subset-stable endpoint-derived exact
   six-list restricted-existence operation with signed occurrence-level
   source replay, without \(B^3\) provenance, target-fitted advice, a supplied
   source object, or a hidden dictionary.
2. **KN-OPEN-005:** exhibit a target-dependent coordinate output and prove it
   is not \(O(1)\)-overhead generic-group simulable.
3. **KN-OPEN-004:** prove all-arity Newton saturation or find an asymptotic
   support exception beyond the scoped \(m=3,4,5\) evidence that lowers the
   complete relation-and-descent cost.
4. **KN-OPEN-006:** find a non-arithmetic-progression support family whose
   structure survives relation-density, rank, factor-log, memory, and blind
   descent charges below the matched threshold.

These remain open mathematical questions, not surviving proposals.

## Scope limits

This was a zero-compute, non-operational academic review. It performed no key
recovery, standardized-curve execution, deployed-target analysis, or
cryptographic experiment. It changes no ledger, hypothesis, experiment, or
goal status and makes no conclusion beyond the committed BATCH-005 snapshot.

## Single next action

The Coordinator ledger archive task should archive exactly
`red_team_report.yaml` and `falsification_review.md` for TASK-20260723-503,
recording the upheld scoped disposition and gate-fatal objections without
filing a proposal, opening an experiment, or changing official research
status.
