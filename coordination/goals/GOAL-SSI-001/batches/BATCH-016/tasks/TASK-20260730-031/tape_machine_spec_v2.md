# Typed-tape and recursive-history transition machine, version `ttm-v2`

## Scope and fixed inputs

This is a finite ideal-choice abstraction for the rows in
`schedule_panel.yaml`.  It specifies a transition explorer; it is not a
model of the concrete `HashDRBG`, a stopping-law proof, or an end-to-end
attack model.  The explorer must execute every enabled typed symbol once and
must record invalid symbols as unavailable rather than converting them into a
different transition.

Version `ttm-v2` is the successor to `ttm-v1` (BATCH-015 /
`TASK-20260730-025`).  It closes the preregistered gaps named
`TTM-RETURN-MODULUS` and `TTM-REQUESTED-LENGTH` in RT-20260730-029 /
DEC-20260730-007 by stating explicit return-modulus coercion and
requested-length / BaseDraw-count propagation **before** any later audit
inspects results.  Machine structure (phases, collimation, decide, one-retry
horizon at `internal_S2`, zero-progress class for `[1, 2, 4]`, typed tape
alphabet) remains compatible with `ttm-v1` except where this document
overrides it.

For a row let `ss = [s_0, ..., s_d]` be its interval list, `n = s_d`,
`ell = L`, and `theta` its declared threshold.  A call at index `r < d`
has current modulus `s_r` and child index `r + 1`; index `d` is the base
call.  The root call is `(history = root, r = 0)` and has `alwaysKeep = true`.
Every other call has `alwaysKeep = false`, subject to the bounded audit
policy below.

## State, history, and labels

A machine state is

```text
(call_history, tape_position, phase, r, retry_count, child_store, attempt,
 requested_length)
```

where:

- `call_history` is a finite word of call labels.  The initial history is
  `[root]`; a child appends `left` or `right`; a same-level retry appends
  `retry(k)` to the current call history, with `k` its retry number.
- `tape_position` is a nonnegative integer: the number of typed symbols
  already consumed.  It begins at zero and advances by one on every draw
  transition.
- `phase` is one of `enter`, `spawn_left`, `await_left`, `spawn_right`,
  `await_right`, `collimate`, `decide`, `return`, or
  `retry_horizon_exhausted`.
- `r` is the schedule index of the active call.
- `retry_count` is in `{0, 1}` at the designated retry site and is zero at
  every other call.
- `child_store` is either empty, `(v1)`, or `(v1, v2)`, where each `v` is a
  sorted finite vector over `Z/s_r Z` (the active parent modulus).
- `attempt` is either empty or `(q, v)`, the selected bin label and
  deterministically produced output vector for the current collimation.
- `requested_length` is a positive integer carried by every frame.  The root
  frame initializes `requested_length = L` for the panel row.  Child frames
  receive a length request by the propagation rule below; same-level retries
  keep the parent's `requested_length` unchanged.

States inherit a fixed row identifier.  A return transition appends a
`return(v)` event to the parent's history record before restoring the parent
state, so the explorer retains the complete recursive call/return history.

### Return labels versus return value types

Two distinct failure modes are named so they are not conflated:

1. **Mismatched return label.**  There is no transition for a return whose
   call label does not match the awaiting parent expectation (`left` while
   awaiting right, `right` while awaiting left, retry-label mismatch), and
   there is no transition for a return to an empty parent frame.  These are
   the same explicit no-transition rules as in `ttm-v1`.
2. **Ill-typed modulus return (closed in `ttm-v2`).**  Under `ttm-v1`, a
   child could emit a vector whose production modulus differed from the
   parent's `child_store` type `Z/s_r Z` with no coercion rule, so the return
   was undefined / ill-typed rather than an enumerated invalid-label branch.
   Under `ttm-v2`, every successful labeled return first applies the
   return-modulus rule below; after that coercion the stored vector lies in
   the declared parent state space.  There is therefore no separate
   ill-typed-modulus refusal branch once the coercion is applied.

## Return-modulus semantics (preregistered rule)

**Chosen rule: `reduce-mod-parent`.**

When a child frame emits a keep-return of a sorted vector `v*` whose
coordinates are integer representatives produced in that child's production
domain (base: residues in `{0, ..., n-1}` after reduction modulo `n`;
internal: residues produced by that child's collimation modulo its own
active modulus), and the awaiting parent has active modulus `s_r`, the return
transition stores

```text
v = sort( (x mod s_r) for x in v* )
```

into the parent's `child_store` as `v1` or `v2` as appropriate.  Each
coordinate of `v` is the unique residue in `{0, ..., s_r - 1}`.  The parent
frame's `child_store` type remains vectors over `Z/s_r Z`.

This rule is total on finite integer vectors: every successful labeled return
lands in the declared parent state space.  It is the preregistered coercion
that closes `TTM-RETURN-MODULUS`.  It is recorded here as an explicit
specification choice for the typed explorer (preferred when a uniquely
source-faithful store-time reading is uncertain relative to retaining
unreduced integer representatives through collimation).  Later audits must
apply this rule as written; they must not substitute a retain-representatives
or retain-child-modulus convention without a new preregistered successor.

Collimation and decide on the parent frame use only the post-coercion
vectors in `child_store`.

## Requested-length semantics (preregistered rule)

**Chosen rule: adaptive length propagation with length-indexed BaseDraw count.**

Every frame carries `requested_length`.  Base calls are **not** forced solely
by the row-level `L` when a recursive call has a different length request.

### Propagation

Let `ℓ` be the active frame's `requested_length`.

1. **Root.**  `requested_length = L` (panel row).
2. **Left child.**  On `spawn_left`, the child frame is created with
   ```text
   requested_length_left = ceil_sqrt(3 * ℓ)
   ```
   where `ceil_sqrt(a)` is the least nonnegative integer `x` with `x*x >= a`.
3. **Right child.**  On `spawn_right`, after `v1` has been stored in the
   parent, the right child is created with
   ```text
   requested_length_right = ceil( (3 * ℓ) / |v1| )
   ```
   using ordinary integer ceiling division.  Well-formed keep-returns have
   `|v1| >= 1`, so the denominator is nonzero.
4. **Retry.**  A same-level retry frame inherits the same `requested_length`
   as the discarded attempt.

This propagation matches the length-indexed family used by the BATCH-014
static analyzer (`TASK-20260730-021`) and is preregistered so that panel
audits can relate to that family without silent amendment.  It addresses
`TTM-REQUESTED-LENGTH`.

### BaseDraw count

A base frame (`r = d`) with `requested_length = ℓ` consumes exactly

```text
base_draw_count(ℓ) = round(log2 ℓ)
```

typed `BaseDraw` symbols, where `round` is the ordinary nearest-integer map
with the finite panel table

```text
ℓ | base_draw_count(ℓ)
1 | 0
2 | 1
3 | 2
4 | 2
```

(and the same `round(log2 ·)` rule for any larger positive `ℓ` that a
propagated request may produce).  After those symbols are consumed, the
source-compatible subset-sum construction (all subset sums of the drawn
values in `{0, ..., n-1}`), followed by sorting and reduction modulo `n`,
yields the base output vector `v*` before the return-modulus coercion into
the parent.

When `base_draw_count(ℓ) = 0`, the base frame consumes no tape symbols and
emits the length-1 vector `(0)` over `Z/nZ` (empty subset sum), then returns
through `reduce-mod-parent`.

### Decision threshold

At `decide`, let `ℓ` be the **frame's** `requested_length` (not merely the
row-level `L` when they differ).  Keep is

```text
alwaysKeep OR (|v| / ℓ >= theta)
```

equivalently `|v| >= ceil(theta * ℓ)` when comparing cardinalities.

## Typed tape alphabet

The tape is a finite sequence of tagged symbols, consumed left to right:

- `BaseDraw(x)`, with `x in {0, ..., n-1}`, is permitted only at a base
  call.  A base call consumes exactly `base_draw_count(requested_length)`
  such symbols and maps them as specified above.
- `LeftIndex(i)` and `RightIndex(j)` are permitted only during `collimate`.
  Their enabled domains are respectively `0 <= i < |v1|` and
  `0 <= j < |v2|`.  They select the pair used to choose a bin.

The symbol tag is part of the alphabet.  A tag used in the wrong phase, or an
index outside its enabled domain, is an invalid tape symbol and has no
transition.  The abstraction makes no assertion that concrete random bytes
have this distribution.

## Transitions

1. **Enter.** At `enter`, if `r = d`, move to base-draw accumulation.  After
   the required base symbols have been consumed (possibly zero), emit
   `return(v*)` and apply `reduce-mod-parent` into the awaiting parent.  If
   `r < d`, move to `spawn_left`.
2. **Recursive children.** `spawn_left` creates a child frame with history
   `call_history + [left]`, index `r + 1`, phase `enter`, and
   `requested_length = ceil_sqrt(3 * ℓ)`.  On its labeled return, apply
   `reduce-mod-parent`, store `v1`, and move to `spawn_right`.
   `spawn_right` analogously creates the `right` child with
   `requested_length = ceil((3 * ℓ) / |v1|)`; on return apply
   `reduce-mod-parent`, store `v2`, and move to `collimate`.
3. **Collimation draw.** From `collimate`, consume one valid `LeftIndex(i)`
   then one valid `RightIndex(j)`.  Set
   `q = floor((v1[i] + v2[j]) / s_r)` and
   `v = sort({(v1[u] + v2[w]) mod s_r : q*s_r <= v1[u] + v2[w] < (q+1)*s_r})`.
   Store `(q, v)` and move to `decide`.
4. **Decision.** At `decide`, let `keep` be
   `alwaysKeep OR (|v| / requested_length >= theta)`.  A keep transition
   emits `return(v)` (then the parent's `reduce-mod-parent` if the receiver
   is a parent frame).  A non-keep transition is a discard event.
5. **Retry.** A discard at the row-designated site with `retry_count = 0`
   creates a fresh same-level frame at the same `r`, with history appended by
   `retry(1)`, empty child store and attempt, the same `requested_length`,
   and `retry_count = 1`.  This is the sole enabled retry successor.  A
   discard at that site with `retry_count = 1` moves to
   `retry_horizon_exhausted` and has no further retry successor.  At every
   non-designated non-root call, the bounded audit records the first decision
   and requires its keep branch; a non-keep branch is recorded as an
   out-of-policy terminal, not silently retried.

The designated site is `internal_S2` for both preregistered rows.  The root
is never a retry site because it has `alwaysKeep = true`.

## One-retry horizon and zero-progress class

The horizon contains the initial attempt and at most one fresh same-level
retry at the designated `internal_S2` call.  No transition may create
`retry(2)` or a retry at another level.

For the BATCH-014 row `[1, 2, 4]`, the zero-progress class is defined
syntactically as the set of reachable `decide` states satisfying all of:

```text
r identifies S = 2;
call_history is a non-root internal S=2 invocation or its retry(1);
alwaysKeep = false;
child_store = (v1, v2);
attempt = (q, v);
|v| / requested_length < theta.
```

Equivalently, these are precisely the threshold-rejected outcomes at the
designated internal `S=2` retry site, before the retry or horizon-exhaustion
transition is applied.  This definition fixes the classification target only;
it reports no occupancy, witness, projected pair set, probability, or
conclusion.

## Required audit outputs

For each panel row, a later audit must retain the **full transition trace**,
including frame-by-frame events: every frame's
`(call_history, r, phase, requested_length, retry_count)`, consumed symbol
tags and positions, invalid-symbol exclusions, labeled call/return events
with post-coercion `child_store` contents, every discard, the retry
successor when enabled, and the terminal horizon event when reached.

BATCH-016 additionally requires, before claiming an exhaustive panel rerun, a
real **all-zero-tape** frame-by-frame trace for each panel row (canonical tape
whose every drawn `BaseDraw` / index symbol is the zero element of its
enabled domain, with unavailable symbols recorded as such).  Comparison of
explorer outputs to a static pair enumeration is deferred and is not part of
this preregistration.

## Claim boundary

This document preregisters only the `ttm-v2` transition rules.  It contains
no analysis outputs, pair sets, reachability or recurrence results, keep
probabilities, witnesses, `QUERY_MEMORY` conclusions, numeric-security
claims, breakthrough claims, or goal-completion claims.
