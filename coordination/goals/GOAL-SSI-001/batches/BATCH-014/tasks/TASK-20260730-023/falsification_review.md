# Falsification review: BATCH-014 schedule/history reachability

## Verdict

**REVISE.** Snapshot
`a3ac87c9b369b4d306fa8827946c894e62626de5` supports the narrow finite-model
exclusion and supports retaining
`FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED`. Two provenance/representation claims
need correction:

1. The snapshot cannot independently establish that the schedule was pinned
   before analysis, because the pin and results first became durable together.
2. The embedded reproduction code statically enumerates child-vector pairs; it
   does not implement the claimed typed-tape/history transition machine.

Neither defect overturns the narrow zero-class exclusion. Both block stronger
language about preregistration or implemented transition-level coverage.

## Snapshot integrity

The reviewed commit is reachable from `HEAD` on
`cursor/supersingular-isogeny-goal-a9d5`, has parent
`e7e39b36d67bdd1302ccbfebdbfa93f12eca5130`, and changes exactly the five
producer files plus the snapshot receipt. SHA-256 values recomputed from
`git show` for all five producer artifacts match the receipt.

The receipt remains the committed pre-post-commit payload:
`commit_sha: null`, `verification.status: pending_post_commit`. Independent Git
checks establish the durable snapshot despite that stale receipt status.

## Schedule construction and post-selection

The schedule arithmetic checks. For `logn=2`, `logl=2`, and `logs=0`,
\(n=L=4\) and \(S_0=1\). Iteration of

\[
t \longmapsto \left\lfloor\frac{2tL}{3}\right\rfloor
\]

while \(t<n\), followed by appending \(n\), gives

\[
1 \longmapsto 2 \longmapsto 5,\qquad [1,2] \mathbin{+\!\!+} [4]=[1,2,4].
\]

This agrees with the `Main.hs` construction already pinned and independently
corroborated in BATCH-012. The row is a plausible smallest nondegenerate
two-internal-level schedule.

What does not check independently is the historical ordering. The BATCH-014
handoff said to pin one actual small schedule but did not predeclare the row.
`schedule_pin.yaml` and the result files enter immutable history in the same
commit. The field `pinned_before_analysis: true` is therefore producer
self-attestation, not preregistration. There is no evidence that the producer
post-selected the row, but this snapshot cannot exclude that failure mode.

Durable wording should be:

> The producer records the [1,2,4] schedule as selected before enumeration;
> this ordering was not independently preregistered.

The cheapest repair is not retrospective argument. Precommit a selection rule
or a small adjacent schedule panel before inspecting outputs, then report every
row.

## Positive-keep and zero-class check

Independent execution of the embedded standard-library arithmetic reproduced:

| requested length | pair states | zero states | minimum keep probability |
|---:|---:|---:|---:|
| 1 | 16 | 0 | 1 |
| 2 | 32 | 0 | 3/4 |
| 3 | 64 | 0 | 3/4 |
| 4 | 64 | 0 | 3/4 |

Thus the 176-state total checks. One minimum-positive example at requested
length 2 is

\[
v_1=(0,0,1,3),\qquad v_2=(0,3).
\]

At internal \(S=2\), the four \(q\)-bin cardinalities are \(3,3,1,1\).
The required cardinality is
\(\lceil(3/4)\cdot2\rceil=2\), so exactly six of eight sampled index pairs
select an accepted bin and the keep probability is \(6/8=3/4\).

Because every possible pair in the producer's enumerated set is positive, the
zero-progress class is empty in that set. Any actual ideal-choice tape path
whose generated pair lies in this set therefore cannot reach a zero-progress
state. This supports `jointly_reachable: false` in the declared bounded
abstraction.

## What the embedded analyzer actually represents

The reproduction program enumerates base vectors, pre-collimation pairs, bin
sizes, and keep probabilities. It has no variables or transitions for
`call_history`, `tape_position`, remaining typed symbols, or retry successors.
The reported 352 history-augmented states are 176 static pairs duplicated over
two markers.

That representation gap does not defeat the empty-class argument: duplicating
or transitioning among a set that contains no zero-progress pair cannot create
one. It does mean the stronger implementation claim should be revised. The
snapshot supports:

> Static exhaustive enumeration of the possible internal S=2 pair set, with a
> conceptual initial/retry marker.

It does not by itself support:

> An implemented typed finite-choice-tape transition analyzer exhaustively
> executed recursive history and successor states.

An explicit transition machine remains useful as a control. It should encode
typed symbol consumption, enabled-index checks, child-generation phase, retry
count, and successor projection, then demonstrate that its projected pair set
equals the static set.

## Reachability and recurrence scope

The bounded judgments are:

- `jointly_reachable: false`: supported only for the zero-progress class in
  this finite ideal-choice abstraction;
- `recurrent: false`: supported only as “the empty class cannot be revisited at
  either of the two declared history markers.”

Standard recurrence is an unbounded-time property. One retry cannot prove that
the implementation, another schedule, or deeper histories are globally
nonrecurrent. Here the bounded statement is particularly simple because the
class is absent, not because a recurrence analysis established a global
transience law.

The producer keeps `non_extrapolation: true`, does not model the concrete
HashDRBG, and does not infer a global stopping tail. No illicit global C2
rejection appears in the snapshot. Future synthesis must preserve the bounded
qualifier whenever `recurrent: false` is quoted.

## QUERY_MEMORY, C2, C3, and error map

`FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED` remains supported.

**QM-STOPPING / C2.** This row removes one candidate obstruction in one finite
model: it excludes a zero-progress internal S=2 pair through the declared retry
horizon. It does not establish a schedule-, parameter-, and history-uniform
progress constant, concrete-DRBG behavior, the complete recovery stopping
distribution, or finite joint \(Q/S/P/C\) expectations. C2 remains live and
must not be globally rejected.

**QM-MEMORY-MAP / C3.** Recovery and object-lifetime tracing were out of scope.
No \(W/R/B/M_{\rm tail}\) widths, births, last uses, cleanup events,
concurrency, or global peak were supplied. C3 remains rejected only for the
previously established lexical simulator-`PhaseVector` subcase; broad C3 and
the FC0 memory map remain unresolved.

**QM-ERROR.** No recovery procedure, independent key verification, or
component-to-final-event implication was implemented. The operational event
\(F=\{\text{final key recovery fails}\}\) remains unmapped. QM-ERROR remains
blocking.

Clearing QUERY_MEMORY on the strength of the local positive keep result would
therefore be premature even if that result generalized: the memory and error
gates are independent and wholly absent.

## Baselines and claim creep

There is no generic ECDLP instance, solve path, or complete resource vector, so
no quantitative Pollard-rho or BSGS comparison is admissible. Peikert's pinned
CollimationSieve remains the closest specialized baseline. Analyzing one local
schedule abstraction changes neither its concrete nor asymptotic attack cost.

Representation, relation path, rank, scalar orientation, source recovery,
target descent, terminal verification, and residual-tail handling are not
implemented. There is no numeric-security, parameter, breakthrough, or
goal-completion claim.

Claim creep is limited but real in two descriptions: independently
unsubstantiated “pinned before analysis,” and “extended analyzer with recursive
history + typed finite choice-tape” when the emitted code is static
pair-set enumeration. The actual reachability result is scoped correctly and
must not be expanded into global nonrecurrence, global C2 rejection, or
QUERY_MEMORY clearance.

## Narrow conclusion and next action

The [1,2,4] construction, 176 pair-state count, and positive keep minima check.
Within the declared bounded ideal-choice abstraction, the zero-progress class
is empty and therefore neither jointly reachable nor revisitable through one
retry. This is not a global stopping or recurrence result and says nothing
about concrete HashDRBG evolution.

Revise the pin-order and analyzer-implementation wording. Then commit a
pre-analysis small-schedule panel and an explicit typed-tape transition-machine
specification, run every panel row through at least one same-level retry, and
compare each projected pair set with the current static enumeration. Recovery,
object lifetimes, and the common final-error event remain separate mandatory
gates.
