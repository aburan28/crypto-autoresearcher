# Typed-tape and recursive-history transition machine, version `ttm-v2`

**Supersedes `ttm-v1`** (`BATCH-015/tasks/TASK-20260730-025/tape_machine_spec.md`),
which is left unedited. `ttm-v2` exists to close the two specification errors
`TASK-20260730-027` recorded and `RT-20260730-029` upheld:

| id | ttm-v1 defect, as recorded |
|---|---|
| `TTM-RETURN-MODULUS` | "Base returns are reduced modulo `n`, whereas the restored parent `child_store` requires vectors over `Z/s_r Z`; no return coercion is defined." |
| `TTM-REQUESTED-LENGTH` | "`ttm-v1` fixes `BaseDraw` count by row-level `L` and omits the requested-length semantics used by the BATCH-014 static analyzer." |

Everything not restated below is inherited from `ttm-v1` verbatim. **This is a
preregistration. It contains no analysis output, no occupancy, no pair set, no
witness, no probability, and no conclusion**, and it asserts no equivalence to
the concrete `Main.hs` or to `HashDRBG`.

## 1. `TTM-RETURN-MODULUS` — the typing of returns and of `child_store`

`ttm-v1` declared `child_store` to be "either empty, `(v1)`, or `(v1, v2)`,
where each `v` is a sorted finite vector over `Z/s_r Z`" — with `s_r` the
modulus of the call that **owns** the store. It separately declared that a base
call reduces "modulo `n`". Those two statements are inconsistent whenever
`s_r != n`, which is every non-base call, so the machine has no transition at
the first base return. That is the blocker as diagnosed, and it is a **typing
error in the specification**, not a defect discovered in the underlying scheme.

`ttm-v2` fixes the types by stating them per index rather than per store:

- **Return type.** A call at schedule index `r` returns a sorted finite vector
  over `Z/s_r Z`. This holds for every `r`, base and internal alike. The base
  call is the case `r = d`, where `s_d = n`, so "reduce modulo `n`" is the
  `r = d` instance of one uniform rule rather than a special case.
- **Store type.** A call at index `r` has children at index `r + 1`. Its
  `child_store` therefore holds vectors over `Z/s_{r+1} Z`, **not** over
  `Z/s_r Z`. This is the correction: `ttm-v1` named the owner's modulus where it
  meant the child's.
- **Coercion.** With the two types above, the value a child returns
  (`Z/s_{r+1} Z`) and the type its parent stores (`Z/s_{r+1} Z`) already agree,
  so **the required coercion is the identity** and the first base return is
  closed. `ttm-v2` defines it explicitly all the same, so no later reader has to
  re-derive it:

  ```text
  store_coerce_{r}(w) = w        for w a sorted vector over Z/s_{r+1} Z
  ```

  and `store_coerce` is **undefined** — no transition — on any vector whose
  modulus is not `s_{r+1}`. An out-of-type return is an invalid transition and
  is recorded as such, exactly as an invalid tape symbol is.
- **Reduction happens at collimation, not at return.** The step that changes
  modulus is collimation at index `r`, which consumes `Z/s_{r+1} Z` values and
  produces a `Z/s_r Z` value:

  ```text
  q = floor((v1[i] + v2[j]) / s_r)
  v = sort({ (v1[u] + v2[w]) mod s_r : q*s_r <= v1[u] + v2[w] < (q+1)*s_r })
  ```

  This is `ttm-v1`'s rule unchanged. `ttm-v2` only makes explicit that its
  inputs are child-modulus values and its output is owner-modulus, which is what
  makes the return chain well typed.

**An alternative reading is rejected explicitly.** One could instead have kept
`child_store` at `Z/s_r Z` and defined a non-trivial coercion `Z/s_{r+1} Z ->
Z/s_r Z` applied at return time. `ttm-v2` does **not** do this, because
collimation already performs a reduction to `Z/s_r Z`, and reducing at return as
well would apply it twice and silently change the binning. Recorded so that the
choice is auditable rather than implicit.

## 2. `TTM-REQUESTED-LENGTH` — what a call asks for and what a return delivers

`ttm-v1` fixed the base draw count from the row-level `L` and never said what
length any call *requests*, which is the quantity the decision rule divides by.
`ttm-v2` defines it:

- **Requested length.** Every call, at every index, is invoked with a requested
  length `ell = L`, the row-level constant (`L = 4` for both preregistered
  rows). It is an input to the call, uniform across the schedule, and it is
  **not** a function of `r`.
- **What the base call delivers.** A base call consumes exactly
  `round(log2 L)` `BaseDraw` symbols and maps them through the
  source-compatible subset-sum construction, then sorts and reduces modulo
  `s_d = n`. The construction yields `2^{round(log2 L)}` subset sums, so the
  delivered vector has length **at most** `L`; it is shorter exactly when
  distinct subsets collide modulo `n`. `ttm-v2` does not assume `|v| = L`.
- **What a collimating call delivers.** `|v|` is the number of sums falling in
  the selected bin `q`, which is bounded above by `|v1| * |v2|` and may be
  zero. It is **not** truncated, padded, or resampled to `L`.
- **The decision rule reads requested length, not delivered length.**
  `keep = alwaysKeep OR (|v| / L >= theta)` uses the requested `L` as the
  denominator and the delivered `|v|` as the numerator. `ttm-v2` states this
  because with `|v|` unbounded above by `L` at a collimating call, "length" was
  ambiguous in `ttm-v1` between the two, and the ratio's meaning depends on
  which is meant.
- **No length-driven transition exists.** Nothing in `ttm-v2` branches on `|v|`
  except the `decide` comparison above. In particular a short return is not an
  error, not a retry trigger, and not an invalid transition.

**Scope note.** `TTM-REQUESTED-LENGTH` observed that `ttm-v1` "omits the
requested-length semantics used by the BATCH-014 static analyzer." `ttm-v2`
supplies a definition for *this machine*. It does **not** claim that definition
reproduces the BATCH-014 analyzer's, and `EV-SSI-015` already records the two as
`not_comparable`. Establishing or refuting agreement is downstream work and is
not preregistered here.

## 3. Required trace output, strengthened

`RT-20260730-029` upheld `TTM-EXECUTION-TRACE-OVERSTATEMENT`: BATCH-015's audit
was a **static type-consistency diagnosis**, not literal recursive execution,
and was described as though it were the latter. `ttm-v2` therefore makes the
distinguishing artifact mandatory *before* any rerun may be called exhaustive:

- For each panel row, the audit must emit a **frame-by-frame trace on the
  all-zero tape** — every `BaseDraw(0)`, `LeftIndex(0)`, `RightIndex(0)` — from
  `(root, r=0, enter)` to a terminal state.
- Each frame must record: `call_history`, `tape_position`, `phase`, `r`,
  `retry_count`, `child_store` with its modulus, and `attempt`.
- The trace must show the **first base return crossing into its parent's
  `child_store`**. That single frame pair is what `ttm-v1` could not produce and
  is the minimum evidence that `ttm-v2` is closed where `ttm-v1` was not.
- An audit that cannot emit this trace reports `SCOPED_NO_GO` and **must not**
  describe its output as an execution, a rerun, or exhaustive.

The all-zero tape is chosen because it is canonical, requires no randomness, and
is reproducible by inspection. It is a **smoke trace**: it demonstrates the
machine is closed under its own transitions and asserts nothing about
occupancy, reachability, or any distribution.

## 4. Unchanged from `ttm-v1`

State tuple, history labels, typed alphabet and its invalid-symbol rule,
transition list 1–5, the designated retry site `internal_S2`, the one-retry
horizon, the bounded audit policy, and the syntactic zero-progress class are all
inherited unchanged. `ttm-v2` narrows no transition and adds no new one; it
types the existing ones and pins one previously undefined constant.

## 5. Claim boundary

This specification is a finite ideal-choice abstraction over the two
preregistered rows. It is **not** a model of `HashDRBG`, not a stopping-law
proof, not an end-to-end attack model, and not a claim about CSIDH or any
supersingular-isogeny parameter set. No curve, isogeny, simulator, or quantum
circuit is executed by anything in this file. **No numeric security claim, no
breakthrough claim, and no goal-completion claim is made or implied.** Recovery
implementation and object-lifetime tracing remain a separate later gate and are
out of scope, per `DEC-20260730-007`.
