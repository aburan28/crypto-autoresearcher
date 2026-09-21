# Typed-tape and recursive-history transition machine, version `ttm-v1`

## Scope and fixed inputs

This is a finite ideal-choice abstraction for the rows in
`schedule_panel.yaml`.  It specifies a transition explorer; it is not a
model of the concrete `HashDRBG`, a stopping-law proof, or an end-to-end
attack model.  The explorer must execute every enabled typed symbol once and
must record invalid symbols as unavailable rather than converting them into a
different transition.

For a row let `ss = [s_0, ..., s_d]` be its interval list, `n = s_d`,
`ell = L`, and `theta` its declared threshold.  A call at index `r < d`
has current modulus `s_r` and child index `r + 1`; index `d` is the base
call.  The root call is `(history = root, r = 0)` and has `alwaysKeep = true`.
Every other call has `alwaysKeep = false`, subject to the bounded audit
policy below.

## State, history, and labels

A machine state is

```text
(call_history, tape_position, phase, r, retry_count, child_store, attempt)
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
  sorted finite vector over `Z/s_r Z`.
- `attempt` is either empty or `(q, v)`, the selected bin label and
  deterministically produced output vector for the current collimation.

States inherit a fixed row identifier.  A return transition appends a
`return(v)` event to the parent's history record before restoring the parent
state, so the explorer retains the complete recursive call/return history.
There are no transitions for a mismatched return label or for a return to an
empty parent frame.

## Typed tape alphabet

The tape is a finite sequence of tagged symbols, consumed left to right:

- `BaseDraw(x)`, with `x in {0, ..., n-1}`, is permitted only at a base
  call.  A base call consumes exactly `round(log2 L)` such symbols and maps
  them through the source-compatible subset-sum construction, followed by
  sorting and reduction modulo `n`.
- `LeftIndex(i)` and `RightIndex(j)` are permitted only during `collimate`.
  Their enabled domains are respectively `0 <= i < |v1|` and
  `0 <= j < |v2|`.  They select the pair used to choose a bin.

The symbol tag is part of the alphabet.  A tag used in the wrong phase, or an
index outside its enabled domain, is an invalid tape symbol and has no
transition.  The abstraction makes no assertion that concrete random bytes
have this distribution.

## Transitions

1. **Enter.** At `enter`, if `r = d`, move to base-draw accumulation.  After
   the required base symbols have been consumed, emit `return(v)`.  If
   `r < d`, move to `spawn_left`.
2. **Recursive children.** `spawn_left` creates a child frame with history
   `call_history + [left]`, index `r + 1`, and phase `enter`.  On its labeled
   return store `v1` and move to `spawn_right`.  `spawn_right` analogously
   creates the `right` child; on return store `v2` and move to `collimate`.
3. **Collimation draw.** From `collimate`, consume one valid `LeftIndex(i)`
   then one valid `RightIndex(j)`.  Set
   `q = floor((v1[i] + v2[j]) / s_r)` and
   `v = sort({(v1[u] + v2[w]) mod s_r : q*s_r <= v1[u] + v2[w] < (q+1)*s_r})`.
   Store `(q, v)` and move to `decide`.
4. **Decision.** At `decide`, let `keep` be
   `alwaysKeep OR (|v| / L >= theta)`.  A keep transition emits `return(v)`.
   A non-keep transition is a discard event.
5. **Retry.** A discard at the row-designated site with `retry_count = 0`
   creates a fresh same-level frame at the same `r`, with history appended by
   `retry(1)`, empty child store and attempt, and `retry_count = 1`.  This is
   the sole enabled retry successor.  A discard at that site with
   `retry_count = 1` moves to `retry_horizon_exhausted` and has no further
   retry successor.  At every non-designated non-root call, the bounded audit
   records the first decision and requires its keep branch; a non-keep branch
   is recorded as an out-of-policy terminal, not silently retried.

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
|v| / L < theta.
```

Equivalently, these are precisely the threshold-rejected outcomes at the
designated internal `S=2` retry site, before the retry or horizon-exhaustion
transition is applied.  This definition fixes the classification target only;
it reports no occupancy, witness, projected pair set, probability, or
conclusion.

## Required audit outputs

For each panel row, a later audit must retain the full transition trace,
including consumed symbol tags and positions, invalid-symbol exclusions,
call/return labels, every discard, the retry successor when enabled, and the
terminal horizon event when reached.  Its comparison to a static pair
enumeration is deferred and is not part of this preregistration.
