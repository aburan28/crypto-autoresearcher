# BATCH-016 ttm-v2 panel audit (TASK-20260730-033)

Task `TASK-20260730-033` executes the preregistered `ttm-v2` transition
explorer against the immutable panel and machine from commit
`1801e2a512158c803d424d480eb15f6417ac01a3` (TASK-20260730-031).  This is a
finite ideal-choice typed-tape / recursive-history audit.  It is not a curve,
isogeny, quantum circuit, HashDRBG, recovery, or object-lifetime computation.

## Method

1. **Machine.** Literal stack-based execution of
   `tape_machine_spec_v2.md`: phases
   `enter → spawn_left/await_left → spawn_right/await_right → collimate →
   decide → return` (base: `enter → base_draw → return`), with
   `reduce-mod-parent` on every labeled return and adaptive
   `requested_length` propagation
   (`ceil_sqrt(3·ℓ)` left; `ceil((3·ℓ)/|v1|)` right; base draws
   `round(log2 ℓ)`).
2. **All-zero tapes.** For each panel row, one oracle run supplies the zero
   element of every enabled `BaseDraw` / `LeftIndex` / `RightIndex` domain
   and retains the full frame-by-frame event list through root return
   (`zero_tape_traces.yaml`).  Events include
   `call_history`, `r`, `phase`, `requested_length`, `retry_count`,
   `tape_position`, consumed symbols, post-coercion `child_store`, and
   decide/discard/retry/horizon markers.
3. **Exhaustive audit.** Compositional enumeration of every enabled typed
   transition at each reachable `(r, requested_length, retry_count)`, through
   the designated `internal_S2` one-same-level-retry horizon and
   keep-on-first-attempt at other internal calls.  Toy panel sizes were fully
   enumerated (no bounded subset).

## BATCH-015 qualification

BATCH-015 / `TASK-20260730-027` is retained only as a **static
type-consistency diagnosis** of `ttm-v1` (endpoint-versus-parent-modulus
comparison without a retained recursive machine trace).  Per
`DEC-20260730-007` and `RT-20260730-029`, it must not be read as literal
recursive execution of `ttm-v1`.  The present task supplies the required
explorer and frame-by-frame traces under the successor specification
`ttm-v2`.

## Per-row results

### `[1, 2, 4]` — CSIDH-CS-6f9188e4-logn2-logl2-logs0-theta3over4

| Metric | Value |
|---|---|
| All-zero-tape terminal | `root_return` (53 events; real stack trace) |
| Projected S=2 pair set count | 8 |
| Pairs by requested_length | `{1: 4, 3: 4, 4: 4}` (ℓ=2 unreachable at S=2) |
| Zero-progress decide occupancy | 0 |
| `jointly_reachable` | false |
| `recurrent` within one-retry horizon | false |
| Min conditional keep by ℓ | all `1` |
| Retry-triggering index outcomes | 0 |

Under `reduce-mod-parent`, base returns collapse into `Z/2Z` before S=2
collimation.  No threshold-rejected S=2 decide state occurs in the exhaustive
ideal-choice enumeration.  This is **not** equated to BATCH-014's empty
all-q-bins class (see comparison below).

### `[1, 2, 5, 8]` — CSIDH-CS-6f9188e4-logn3-logl2-logs0-theta3over4

| Metric | Value |
|---|---|
| All-zero-tape terminal | `root_return` (114 events; real stack trace) |
| Recursive prefix | root S=1 → internal S=2 → internal S=5 → base S=8 |
| Projected S=2 pair set count | 2703 |
| Pairs by requested_length | `{1: 239, 2: 887, 3: 1636, 4: 2338}` |
| Zero-progress decide occupancy | 946 |
| `jointly_reachable` | true |
| `recurrent` within one-retry horizon | true |
| Min conditional keep by ℓ | `{1: 1, 2: 5/6, 3: 7/9, 4: 7/9}` |
| Non-designated out-of-policy discards (S=5) | 626 |

S=2 zero-progress decide states are occupied and recur under the one-retry
horizon in this finite ideal-choice model.  Witness samples are in
`panel_audit_results.yaml`.  These are **not** a global stopping-tail claim,
not HashDRBG evidence, and not QUERY_MEMORY clearance.

## Comparison to BATCH-014

Status: `definitions_differ_not_equated`.

BATCH-014 reported 176 static pre-collimation pairs for `[1,2,4]` and an
empty zero-progress class under an all-q-bins-below-threshold predicate with
Z/nZ representatives retained at S=2.  `ttm-v2` coerces returns with
`reduce-mod-parent` into `Z/s_r Z` before collimation and uses a
threshold-rejected decide definition.  Pair counts and emptiness statements
are therefore not equated.  BATCH-014 pin order remains self-attested; its
analyzer was static enumeration, not a tape/history machine.

## Mutations

No in-run discriminating mutation was required: `ttm-v2` already fixed
`reduce-mod-parent` and adaptive requested-length in the preregistration
snapshot.  `TTM-RETURN-MODULUS` and `TTM-REQUESTED-LENGTH` are closed as
specification blockers under that frozen text.  See `mutation_status.yaml`.

## Claim boundary

Disposition: `FC0_QUERY_MEMORY_SEMANTICS_UNRECONCILED`.

Supported only as finite ideal-choice observations under preregistered
`ttm-v2` on the two toy rows.  Explicitly excluded: HashDRBG equivalence,
global history-uniform stopping tail, end-to-end Q/S/P/C, FC0 memory bound,
final error map, numeric security, breakthrough, goal completion, and
QUERY_MEMORY clearance.  C2 remains live; C3 remains lexical-only; recovery
and object-lifetime remain a separate unperformed gate
(`QM-STOPPING`, `QM-MEMORY-MAP`, `QM-ERROR`).

## Reproduction

```sh
python3 coordination/goals/GOAL-SSI-001/batches/BATCH-016/tasks/TASK-20260730-033/ttm_v2_explorer.py
```

Preregistration inputs are read-only from TASK-20260730-031 /
`1801e2a512158c803d424d480eb15f6417ac01a3`.  Artifacts are written only under
this task directory.  No git commit is performed by the Executor.
Inference: requested `executor-terra`, resolved Cursor Grok,
`fallback_used: true`.
