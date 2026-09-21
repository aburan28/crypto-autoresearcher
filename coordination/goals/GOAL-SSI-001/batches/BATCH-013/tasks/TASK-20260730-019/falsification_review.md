# Falsification review: TASK-20260730-017

## Verdict

**CONFIRM**, with a non-blocking row-scope wording guard.

The committed snapshot supports the narrow claim that its finite idealized
one-level state set contains exact zero-progress witnesses. It does not support
a global-tail conclusion, global C2 rejection, an implemented recovery
schedule, a broad C3 rejection, or any numeric-security, breakthrough, or goal
completion claim.

## Snapshot integrity

Snapshot `e726092f064c9c8961b4422fc175661161fcc512` is reachable from `HEAD` on
`cursor/supersingular-isogeny-goal-a9d5`, has the receipt-declared parent
`0ad406b5eaa9d9032c32d3b0de840ee166e7a683`, and changes exactly the receipt
plus the five producer artifacts. SHA-256 values recomputed from `git show`
match all five values in the committed receipt.

The receipt itself remains `pending_post_commit` with `commit_sha: null`.
That stale in-file status does not erase the independently verified Git facts,
but the Coordinator's archive verifier remains responsible for its normal
post-commit receipt handling.

## Independent witness check

One independent standard-library recomputation of the embedded analyzer
returned:

- 36 parameter rows;
- 1,014 parameterized ordered child-vector-pair checks;
- 16 zero-progress witnesses;
- minimum positive probability `1/4`.

For the representative
`(n,ell,s,theta,v1,v2)=(3,2,1,3/4,(0,1),(0,2))`, the required bin size is two.
The four pair sums are `0,2,1,3`, hence the bin cardinalities are all one and
`p=0`. The vectors arise in the stated base model from `z=1` and `z=2`.

The 16 witnesses occur in only four rows:

- `(3,2,1,3/4)`: 2;
- `(3,2,1,1)`: 2;
- `(4,2,1,3/4)`: 6;
- `(4,2,1,1)`: 6.

Accordingly, `analyzer_report.md`'s phrase “at all tested parameter rows” is
unsafe if read row-wise. The valid statement is that the minimum over the
**combined** enumerated state set is zero, with witnesses in four of 36 rows.
This wording issue does not overturn the producer's explicitly scoped claim.

## What the witness falsifies

The witness falsifies a strictly positive progress lower bound over every state
in the producer's combined finite idealized state set. It therefore blocks one
simple route from that model to a geometric retry tail.

It does not establish:

1. use of the witness parameters by the pinned simulator's interval schedule;
2. joint reachability under concrete `HashDRBG` evolution and recursive
   history;
3. recurrence of a zero-progress class after discard and regeneration;
4. a heavy-tail law, divergent expectation, or absence of another summable
   stopping argument;
5. any end-to-end `Q/S/P/C` resource value.

The cheapest next discriminator is a bounded history-aware run of the pinned
small schedule with an explicit finite random-source state. It should test both
joint reachability of the representative class and return to that class after
one retry. That separates an isolated local counterexample from a
process-level stopping obstruction.

## QUERY_MEMORY and mutations

`FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED` remains supported:

- **QM-STOPPING / C2:** remains live. The finite witness strengthens the
  underdetermination control inside the idealized model, but finite coverage
  cannot reject C2 globally.
- **QM-MEMORY-MAP / C3:** broad C3 remains unresolved. Only the prior lexical
  simulator-PhaseVector subcase is rejected. The new W/R/B/M_tail schedule has
  no implementation locations, widths, traces, cleanup proof, or global peak.
- **QM-ERROR / error map:** remains live. The specification declares `F` and
  desired constituent inclusions, but does not instantiate `Verify`, prove
  exhaustive terminal typing, supply component probabilities, or map
  simulator event `F_sim` to recovered-key failure `F`.

The recovery document correctly labels itself a specification. Treating it as
an implemented source-recovery or verification path would be claim creep; the
producer does not do so.

## Baselines and scope

There is no complete attack or resource vector to compare with Pollard-rho,
BSGS, or Peikert's specialized collimation-sieve baseline. Representation,
relation path, rank, scalar orientation, source recovery, target descent, and
verified key recovery remain absent. No Pareto, `sota_delta`, parameter,
numeric-security, ECDLP, breakthrough, or completion conclusion is admissible.

## Next concrete action

Pin one actual small interval-schedule instance and add only the state required
to follow recursive history and an explicit finite random source through one
retry. Determine whether a zero-progress class is jointly reachable and
recurrent. Keep the separate implementation of recovery, W/R/B/M_tail
lifetimes, and the common event `F` as an independent subsequent gate.
