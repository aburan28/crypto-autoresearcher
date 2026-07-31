# TASK-20260729-040 — EXP-STR-004 feasibility table

Mandatory under `DEFER-BATCH009-003` as carried by the BATCH-014 dispatch queue
(`execution_gate.pre_freeze_requirements_binding_TASK-20260729-040`, item
"A FEASIBILITY TABLE IS MANDATORY").

It does two things and no more:

1. For **every invalidation rule** of `experiments/EXP-STR-004/specification.yaml`
   section 10, it shows the arithmetic that evaluates the rule at the **exact
   declared cells** and marks it **CAN FIRE** or **CANNOT FIRE**. A rule marked
   CANNOT FIRE must be removed or replaced before the freeze, with the removal
   recorded.
2. For **every criterion F-1 to F-5**, it states at which **named cells** the
   criterion is evaluable and what makes it evaluable there.

> **EVERY FIGURE IN THIS DOCUMENT IS HAND-DERIVED BY A SESSION WITH NO SHELL.**
> Nothing here was executed, parsed, validated or machine-checked. No harness
> was run, no allocator was run, no git command was run. The arithmetic is
> integer arithmetic a reader can redo in their head; the *empirical* inputs it
> leans on are exactly two committed numbers, both cited to `EV-STR-003`. Every
> such figure is flagged **[HAND-DERIVED]** or **[COMMITTED]** at the point of
> use, and the whole document is routed to the independent reviewer
> `TASK-20260729-042` for checking. **Freezing this table does not validate it.**

---

## 0. The fourteen cells and their derived quantities — [HAND-DERIVED]

`q = B // 3`; `rho = B mod 3`; `tau(B) = {3q, ..., B-1}`;
`R_base(B) = ceil(B/3) + 1 = (B+2)//3 + 1`; `Q(B) = max(60, B+10)`;
`rows_final = 3 · R_base` absent a shortfall.

| cell | curve | B | m | rho | q | tau(B) | R_base | Q | rows_final | rows_final − B | predicted MIS(A-prime) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| L12   | CURVE-J12S1 | 12  | 2 | 0 | 4  | {}    | 5  | 60  | 15  | 3 | ∅ |
| L13   | CURVE-J12S1 | 13  | 2 | 1 | 4  | {12}  | 6  | 60  | 18  | 5 | T(cell) |
| L24   | CURVE-J12S1 | 24  | 2 | 0 | 8  | {}    | 9  | 60  | 27  | 3 | ∅ |
| L25   | CURVE-J12S1 | 25  | 2 | 1 | 8  | {24}  | 10 | 60  | 30  | 5 | T(cell) |
| L48   | CURVE-J12S1 | 48  | 2 | 0 | 16 | {}    | 17 | 60  | 51  | 3 | ∅ |
| L49   | CURVE-J12S1 | 49  | 2 | 1 | 16 | {48}  | 18 | 60  | 54  | 5 | T(cell) |
| L96   | CURVE-J12S1 | 96  | 2 | 0 | 32 | {}    | 33 | 106 | 99  | 3 | ∅ |
| L97   | CURVE-J12S1 | 97  | 2 | 1 | 32 | {96}  | 34 | 107 | 102 | 5 | T(cell) |
| L192  | CURVE-J12S1 | 192 | 2 | 0 | 64 | {}    | 65 | 202 | 195 | 3 | ∅ |
| L193  | CURVE-J12S1 | 193 | 2 | 1 | 64 | {192} | 66 | 203 | 198 | 5 | T(cell) |
| X96   | CURVE-J16S3 | 96  | 2 | 0 | 32 | {}    | 33 | 106 | 99  | 3 | ∅ |
| X97   | CURVE-J16S3 | 97  | 2 | 1 | 32 | {96}  | 34 | 107 | 102 | 5 | T(cell) |
| A12M3 | CURVE-J12S1 | 12  | 3 | 0 | 4  | {}    | 5  | 60  | 15  | 3 | ∅ |
| A13M3 | CURVE-J12S1 | 13  | 3 | 1 | 4  | {12}  | 6  | 60  | 18  | 5 | T(cell) |

**14 is a count and its members are the fourteen cell names in column 1.**
`rho = 0` at seven cells — `L12, L24, L48, L96, L192, X96, A12M3`.
`rho = 1` at seven cells — `L13, L25, L49, L97, L193, X97, A13M3`.

**The load-bearing column is `rows_final − B`.** It is `≥ 0` at all fourteen
cells, which is exactly the condition for the committed
`_measure_displacement_rank` to take its **square** branch
(`endomorphism_la.py:220-223`, square iff `rows ≥ cols`). The square branch is
what the derivation note analyses and what every prediction is stated on. The
margin is 3 rows (one triple) at every residue-zero cell and 5 rows at every
residue-one cell, so:

- a shortfall of **one** base row still leaves `rows_final − B ∈ {0, 2}` — square
  branch preserved, cell still measurable, shortfall still recorded and the cell
  still excluded from the comparative criteria (`IV-6`);
- a shortfall of **two or more** base rows gives `rows_final < B` — rectangular
  branch, and the run is invalid under `IV-5`.

---

## 1. Invalidation rules — CAN FIRE / CANNOT FIRE

Three firing classes are distinguished, because conflating them is how a
vacuous rule survives:

- **E — environment/data.** Can fire without anyone making a mistake.
- **G — implementation guard.** Fires only if the driver deviates from the
  contract. Still **CAN FIRE**: nothing in this contract makes driver
  correctness logically necessary, and each guard is checkable from the
  produced artifacts alone.
- **V — vacuous.** Cannot fire under any execution. **No rule is in this class,
  so no rule was removed.**

| rule | what it invalidates | class | verdict | arithmetic / mechanism at the declared cells |
|---|---|---|---|---|
| **IV-1** dirty tree | that run | E | **CAN FIRE** | `harness/runner.py:44` records `dirty` **repository-wide** over tracked files, not just `harness/`. `SR-9` halts before any write if the tree is dirty at pre-flight, so `IV-1` catches the residual case: a co-driver or reviewer touching any tracked file **during** the 7200 s run window. The BATCH-014 queue records that this branch has co-drivers and that `main` moved five commits during the batch opening, so the residual case is live, not hypothetical. |
| **IV-2** missing one of the six files | that run | E | **CAN FIRE** | `write_run` writes the six files sequentially (`runner.py:185-194`). A `SIGKILL`, a disk-full condition, or an `SR-5` tree-cap stop between two `_write` calls leaves a short directory. Free space is ~124 GiB at freeze time [reported by the dispatching session, not verified here], so disk-full is unlikely but the mechanism exists. |
| **IV-3** code-hash disagreement across runs | the SET | E | **CAN FIRE** | The driver hashes four harness sources per run and there are 28 runs, so 28 hash blocks are compared. Any edit to `harness/` between run 1 and run 28 — the same co-driver mechanism as `IV-1` — produces two distinct blocks. |
| **IV-4** `len(F) != B`, or arm A-prime's orbit-structure assertion fails | that cell, both arms | E | **CAN FIRE** | `_build_phi_invariant_factor_base` returns `xs[:B] if len(xs) >= B else xs` (line 114) and its search loop is bounded by `j < 50·B + 1000`. At the largest cell `B = 193` that is **10650** candidate x-values for **65** whole orbits [HAND-DERIVED: `50·193 + 1000 = 9650 + 1000 = 10650`; `ceil(193/3) = 65`]. On `CURVE-J12S1` the prime is 12-bit, so at most about `p/2` x-coordinates lift and at most about `p/6` whole orbits exist [HAND-DERIVED, order-of-magnitude only]. The rule therefore fires only on a surprise — **but the derivation note's exactness rests on this hypothesis (D-3), so it is checked per cell rather than assumed, and a short list at any cell is a genuine possible outcome, not an impossible one.** |
| **IV-5** rectangular branch | that run | E | **CAN FIRE** | Fires exactly when `rows_final < B`, i.e. when the arm falls **two or more** base rows short of `R_base`. From the table in section 0 the slack is one base row at every cell. See section 2 for the shortfall arithmetic that makes this reachable at the smallest rungs. |
| **IV-6** base-row shortfall | that cell, excluded from comparative criteria | E | **CAN FIRE** | See section 2. This is the single most likely rule to fire in this experiment and the arithmetic is given in full there. |
| **IV-7** determinism check failed | that run | E (scoped) | **CAN FIRE, at four cells** | The check runs at `L12, L13, A12M3, A13M3` only, so it can fire only there. The scope is a declared cost trade — a second `O(B^3)` elimination at `L192`/`L193` would cost roughly `(192/12)^3 = 4096` times the smallest cell's [HAND-DERIVED, from the cubic cost model]. Within scope it fires on any nondeterminism in `_measure_displacement_rank` or in the driver's row handling. |
| **IV-8** nonzero suppression count | that run | G | **CAN FIRE** | The closure is unconditional **only because the driver deletes the line-303/304 conditions**. A driver that reuses `synthetic_phi_closure` from `experiments/EXP-STR-003/driver/ablation_driver.py:291-313`, which keeps both conditions, would report a nonzero count immediately. That is a real and specific failure mode, not a formality: the predecessor driver in this very lineage implements the suppressing version. |
| **IV-9** a certificate fails verification | that run, `completed_invalid` | E + G | **CAN FIRE** | Two mechanisms. (i) The `m = 3` certificate is **reconstructed by the driver** from the committed loop at `endomorphism_la.py:305-339`; the sign choices `sA ∈ {A, -A}`, `sB ∈ {B_pt, -B_pt}` and the remainder point must be recorded with the correct signs or the point sum will not equal the target. Both `A12M3` and `A13M3` exercise this path. (ii) The added `k·P == target` limb can fail if the driver reproduces the target sequence at line 272 incorrectly. |
| **IV-10** certificate rows ≠ committed collection rows | that cell | G | **CAN FIRE** | The same `m = 3` reconstruction risk as `IV-9`, plus the `m = 2` risk that the driver's certificate pass and `_collect_relations` walk the target sequence differently. This is the precise analogue of the append-replay assertion that `EXP-STR-003`'s driver used at `ablation_driver.py:809-811`, which is how that experiment established its replay was faithful. |
| **IV-11** run count ≠ 28, or an undeclared run id | the SET | E | **CAN FIRE** | `SR-0` (disk below 5 GiB), `SR-7` (evidence-integrity halt), `SR-8` (Sage absent or version mismatch) and `SR-9` (dirty tree) all halt **before any run record is written**, giving a count of 0. `write_run` also refuses to overwrite an existing run directory (`runner.py:109-112`), which converts a re-run into a hard failure rather than a silent clobber. |
| **IV-12** raw-result vs summary disagreement | the SUMMARY only | G | **CAN FIRE** | The summary is assembled separately from 28 raw records, over 14 cells × 2 arms × ~10 reported fields. Any assembly slip fires it. The rule deliberately invalidates the summary and **not** the runs, so a summary defect never destroys a measurement. |
| **IV-13** a metric produced by `main()` | that cell | G | **CAN FIRE** | `main()` is importable from the same module the driver already imports. It is forbidden and would raise `IndexError` at `endomorphism_la.py:451` at the **seven residue-one cells** — `L13, L25, L49, L97, L193, X97, A13M3` — as `EXP-STR-003` criterion S4 measured at 4 of 4 [COMMITTED: `EV-STR-003` observation O-3]. The rule is checkable from `command.txt` and the captured stderr of each run. |
| **IV-14** Sage output not exact integers | the verification, as infrastructure signal | E | **CAN FIRE** | This exact failure has already occurred in this repository. `EV-STR-001.deviations` records: *"4 sage invocations, attempts 1-3 infrastructure failures (preparser Integer leaks, JSON coercer truncation) fixed; attempt 4 is the run of record"* [COMMITTED]. Three of four `EXP-STR-001` Sage invocations died this way. The rule is the least hypothetical in this table. |

**No invalidation rule is marked CANNOT FIRE, and therefore no rule was removed
or replaced before the freeze.** This sentence is the record the queue requires.

**14 is a count and its members are the fourteen rule identifiers `IV-1`
through `IV-14` in column 1.**

---

## 2. The rule most likely to fire: `IV-6` base-row shortfall — arithmetic in full

This is the one place where the design has real risk, and it is stated in full
rather than asserted away.

### The mechanism

`_collect_relations(inst, fb, m, Q)` iterates `t_idx ∈ range(Q·5)`, breaks as
soon as `len(relations) >= Q`, deduplicates targets by x-coordinate
(`seen_targets`), and appends one row per successful decomposition. So it can
return **fewer than `Q`** rows, and the contract needs only the first
`R_base(B)` of them. A shortfall means `rows_base_collected < R_base(B)`.

### The one committed empirical anchor

`EV-STR-003` observation O-10(a) records, for arm A at instance I1 — **the same
curve `CURVE-J12S1` this ladder sits on** — `hits = 15`, `attempts = 27` at
`B = 27` [COMMITTED]. That is a measured decomposition rate of `15/27` on this
curve at `B = 27` with `m = 2`.

### The arithmetic — [HAND-DERIVED]

The number of distinct two-summand sums over a factor base of size `B` grows
like `B^2`, and `n = 733` for this curve is fixed, so the per-target
decomposition probability falls roughly like `B^2` until it saturates. Anchoring
on the committed `15/27` at `B = 27` and scaling by `(B/27)^2`:

| cell | B | scaled per-target rate | targets allowed = `5·Q` | expected rows | `R_base` | headroom |
|---|---|---|---|---|---|---|
| L12   | 12  | ~0.11 | 300  | ~33  | 5  | ~6.6x |
| L13   | 13  | ~0.13 | 300  | ~39  | 6  | ~6.5x |
| L24   | 24  | ~0.44 | 300  | ~131 | 9  | large |
| L25   | 25  | ~0.48 | 300  | ~143 | 10 | large |
| L48   | 48  | saturating | 300 | quota-bound at 60 | 17 | large |
| L96+  | ≥96 | saturating | ≥530 | quota-bound | ≤66 | large |

The scaled rates are **order-of-magnitude estimates from one committed data
point**, not predictions, and the distinct-target dedup makes the "targets
allowed" column an upper bound: the target sequence
`k = (t_idx+1)·c mod (n-1) + 1` at `endomorphism_la.py:272` is periodic, so the
number of **distinct** target x-coordinates is bounded by roughly half that
period and may be well below `5·Q`. That is precisely why `IV-6` **CAN FIRE**
and why it is retained.

### Why the quota floor `Q(B) = max(60, B+10)` exists

Under the committed quota `max(10, B+10)` the smallest cell would get
`5·22 = 110` candidate targets for `R_base = 5` rows at a scaled rate of ~0.11 —
about 12 expected rows, a margin of ~2.4x, with the distinct-target bound
biting hardest exactly there. The floor of 60 raises the allowance to 300 at the
six smallest rungs. **The floor is chosen before any cell is measured, for that
stated reason, and it cannot change which rows are measured**, because the
measured rows are the first `R_base` of a deterministic list and are therefore a
prefix invariant to `Q` above the shortfall threshold (contract section 1,
`truncation_is_declared_not_incidental`).

### The `m = 3` cells

`A12M3` and `A13M3` use the committed `m = 3` branch, a quadruple loop over the
factor base. At `B = 12` that is at most `12·2·12·2 = 576` inner steps per
target [HAND-DERIVED], each producing a remainder point whose x must lie in the
12-element factor base. The three-summand decomposition rate is far higher than
the two-summand rate at the same `B`, so `IV-6` is **less** likely at these two
cells than at `L12`/`L13`, and the binding constraint there is time, not supply.

### Disposition if it fires

Recorded naming the cell and the arm; the cell excluded from the comparative
criteria; the exclusion stated in the summary; the verdict `incomplete`; **the
arms are never re-balanced after the fact.** A shortfall is an
`incomplete`-class outcome, never a measurement and never a negative result.

---

## 3. Stopping rules — firing analysis

Included beyond the queue's minimum because a stopping rule that cannot fire is
as misleading as an invalidation rule that cannot.

| rule | verdict | arithmetic / mechanism |
|---|---|---|
| **SR-0** disk < 5 GiB | **CAN FIRE** | The volume is reported at ~124 GiB free and 94% used at freeze time [reported by the dispatching session; **not verified by this session**]. The BATCH-014 queue reports a different figure (~30 GiB free, 99% used) from an earlier session, and `git fsck` has already timed out on this volume. **The two reports disagree and this table does not reconcile them** — that is exactly why the check is mandatory and is made at run time rather than trusted from a report. |
| **SR-1** per-run > 900 s | **CAN FIRE** | The largest run is `AP-L193` or `EP-L193`, estimated 100–500 s [HAND-DERIVED, contract section 8]. The margin is under 2x and the dominant term — two dense object-dtype `193×193` matrix products plus one `O(B^3)` modular elimination, about `3 · 193^3 ≈ 21.6` million Python-level integer operations — is the one the contract names as most likely to be underestimated. |
| **SR-2** total > 7200 s | **CAN FIRE** | Pessimistic stage sum 6480 s against 7200 s [HAND-DERIVED, contract section 8]. Headroom is 720 s, about 10%. |
| **SR-3** RSS > 8 GB | **CAN FIRE** but unlikely | `EXP-STR-003` peaked at 0.0994 GB with `B = 397` [COMMITTED, `EV-STR-003` O-12]. This contract's largest `B` is 193. Retained because a `B×B` object array is allocated three times per measurement and an unexpected copy is the classic way this fails. |
| **SR-4** run dir > 2 MiB | **CAN FIRE** but unlikely | Largest projected directory is `EP-L193`: `198 × 193 = 38214` integers in the final row list plus 193 in the factor base plus 66 certificates. At `json.dumps(indent=2)`, which places each list element on its own line, that is roughly 230–400 KiB [HAND-DERIVED]. Well under 2 MiB. Retained as a guard, and its firing is a *deviation* (`DEV-SIZE-1`), not an invalidation. |
| **SR-5** tree > 64 MiB | **CAN FIRE** but unlikely | 28 directories at the largest projection is roughly 6–11 MiB [HAND-DERIVED]. |
| **SR-6** Sage cumulative > 900 s | **CAN FIRE** | One batched invocation. Startup dominates and is paid once. The verification workload is at most about 500 certificates, each a handful of point operations. Fires on a pathological startup or a verifier defect. |
| **SR-7** evidence-integrity halt | **CAN FIRE** | `--scratch` resolving inside the repository is a one-character mistake, and `experiments/EXP-STR-003/` sits in the same tree. |
| **SR-8** Sage absent / version mismatch | **CAN FIRE** | The pre-freeze host observation is **not** an archived result and carries no guarantee that the binary is present at execution time. The check is required precisely because the observation cannot be relied on. |
| **SR-9** dirty tree at pre-flight | **CAN FIRE** | Same co-driver mechanism as `IV-1`. This rule exists so a dirty tree costs zero run records instead of 28 invalid ones. |
| **SR-10** zero base rows | **CAN FIRE** | The degenerate limit of the section 2 arithmetic. |
| **SR-11** card cannot finish | **CAN FIRE** | Procedural; it binds the Executor's reporting behaviour. |

---

## 4. Criteria F-1 to F-5 — where each is evaluable, and what makes it evaluable

"Evaluable at a cell" means: every quantity the criterion reads is defined at
that cell from a valid run.

### F-1 — SET IDENTITY

| arm | evaluable at | what makes it evaluable |
|---|---|---|
| A-prime | **all fourteen cells** | The predicted set is `∅` at the seven residue-zero cells (derivation D-6) and `T(cell)` at the seven residue-one cells, computed by the closed-form rule D-7 from the arm's own truncated base row list and `tau(B)` — both available **before** `alpha` is measured. The measured set needs only the square branch, guaranteed by `rows_final ≥ B` in section 0. |
| E-prime | **a cell only if the partner `AP` run at that cell is valid** | P-3's predicted set for arm E-prime **is** `MIS(A-prime, cell)`, a measured object. **DEPENDENCY DECLARED IN ADVANCE:** if the `AP` run at a cell is invalid under any of `IV-1..IV-11`, F-1 for `EP` at that cell is **not evaluable**, the cell is named as such, and the verdict is `incomplete`. |

### F-2 — STATIC BOUND `alpha ≤ |MIS|`

Evaluable at **all fourteen cells for both arms**, independently of the partner
arm: it reads only that arm's own `alpha` and its own measured set. It is the
only criterion with no cross-arm dependency, and it is therefore the last one to
become unevaluable.

### F-3 — LADDER

Evaluable over the **ten ladder cells only** — `L12, L13, L24, L25, L48, L49,
L96, L97, L192, L193` — and only if `alpha(A-prime)` is defined at **all ten**.
`X96`, `X97`, `A12M3` and `A13M3` are **excluded by construction**: `X96`/`X97`
sit on a different curve and `A12M3`/`A13M3` at a different arity, so including
them would confound the B-sweep with the very variables the ladder isolates. If
any ladder cell is excluded, F-3 is reported **not evaluable** with the missing
cells named; it is never evaluated on a subset silently.

`Z0` versus `L0 = {L12, L24, L48, L96, L192}` has a reachable middle: `Z0` can be
any subset of the ten, so `identity_holds`, `mixed` and `fails_wholly` are all
attainable. **`mixed` is reachable by construction, which repairs the
`EV-STR-003` observation O-5 defect.**

### F-4 — DIAGNOSTICITY

Evaluable at a cell iff **both** arms produced a defined `alpha` there. The
agreement set `AGREE` can be the full fourteen, any proper non-empty subset, or
empty, so all three outcomes are attainable and `mixed` is reachable.

**What makes each cell informative is not uniform, and this is stated in
advance:**

- At the **seven residue-zero cells** the two closures are the *same index map*
  (derivation D-4a), so the factor base is the only difference and a
  disagreement there is informative — and the derivation says it will not occur.
- At the **seven residue-one cells** the arms differ in *two* ways, factor base
  and tail behaviour of the closure (D-4b), so a disagreement there is
  attributable to the truncated tail of the committed builder and is **not**
  evidence of endomorphism content.

### F-5 — B-INDEPENDENCE OF THE BOUND

Evaluable **per arm** over the **ten ladder cells only**, on the same all-ten
condition as F-3, and for the same reason.

**Firing analysis, per arm — [HAND-DERIVED from the derivation note]:**

- **Arm A-prime.** At residue-zero cells `alpha = 0 ≤ 3`. At residue-one cells
  `alpha ≤ |T|` and
  `|T| = 2 · #{ j < q : r_j[3q] = 1 } + [sigma . r_q ≠ r_q]`. **Two** base rows
  touching the tail already give `|T| ≥ 4`, so `alpha > 3` is arithmetically
  available and **F-5 CAN FIRE for arm A-prime**. It is not a vacuous criterion.
- **Arm E-prime.** The derivation gives `|MIS| ≤ 1` at every residue-one cell and
  `MIS = ∅` at every residue-zero cell, so `alpha ≤ 1 ≤ 3` throughout and F-5 is
  **derived not to fire**. It remains **evaluable and logically able to fire** —
  the measurement could return `alpha > 3` — and if it does, that **falsifies the
  derivation**, which is informative in its own right. It is retained for that
  reason and the asymmetry is recorded here rather than discovered later.

### The pre-registered non-support clause

Bound to F-5 in the contract and repeated here because it is the sentence most
likely to be dropped: **if F-5 does not fire for arm A-prime, that is NOT support
for `H-STR-002` if F-4 also does not fire.** A bound of 3 that a construction
with zero endomorphism content satisfies identically is a property of the closure
convention, not of the endomorphism. The derivation note section D-9 states that
this is the **expected** outcome, not a remote contingency.

---

## 5. Identifier check — NOT PERFORMED AS SPECIFIED, and that is recorded as a defect

`INT-BATCH014-C` and the completion gate `G13` require
`tools/allocate_id.py --check` to be run for `EXP-STR-004`, `EV-STR-004`,
`DEC-20260729-004` and the 28 `RUN-STR-004-*` identifiers, with the **verbatim**
result recorded and a collision reported as a STOP.

**THE FREEZING SESSION HAD NO SHELL AND COULD NOT RUN THE ALLOCATOR. NO
ALLOCATOR RESULT EXISTS AND NONE IS CLAIMED. NO ALLOCATOR OUTPUT IS
REPRODUCED HERE, VERBATIM OR OTHERWISE, BECAUSE NONE WAS OBTAINED. G13 IS
THEREFORE PARTIALLY UNMET AND THIS SECTION IS THE RECORD OF THAT.**

What was done instead, and its exact limits:

- A repository-wide text search **of this worktree only** for `EXP-STR-004`,
  `EV-STR-004`, `DEC-20260729-004` and `RUN-STR-004`.
- Result: every occurrence is a **reservation**, not an allocation — they appear
  in the BATCH-014 dispatch queue, in the nine BATCH-014 task-card mirrors, in
  `ledger/goals/GOAL-ECDLP-001.yaml`, and in earlier BATCH-009/011/012/013
  records that name `EXP-STR-004` as the scheduled successor.
- A directory/file existence check: `experiments/EXP-STR-004/` did not exist
  before this task wrote into it; `ledger/evidence/EV-STR-004.yaml` does not
  exist; `ledger/decisions/DEC-20260729-004.yaml` does not exist; no
  `RUN-STR-004-*` run directory exists anywhere.

**Limits, stated plainly.** A repository-wide search in one worktree **cannot see
non-ancestor branches**, and this branch has had `origin/main` merged into it but
carries no guarantee of seeing unmerged co-driver work. **FOUR ID COLLISIONS ARE
ALREADY ON RECORD IN THIS CAMPAIGN**, and two duplicated immutable identifiers
(`TASK-20260728-002`, `VAL-20260729-001`) are carried unrepaired, so this is not
hypothetical.

**Routing.** The allocator check is an **OPEN PRE-DISPATCH CONDITION** carried to
`TASK-20260729-041`, which has a shell and stages these files, and to the
independent reviewer `TASK-20260729-042`. **On a collision: STOP AND REPORT.** A
rename changes declared `artifact_paths` and requires a recorded `QUEUE-AMEND`
before anything is staged (`INT-BATCH014-C`).

---

## 6. What this table does not establish

- It does not establish that any cell will produce a valid measurement.
- It does not establish that the harness is correct, that the driver will be
  correct, or that Sage will be present at execution time.
- It does not establish that the derivation note is correct. Its firing analysis
  for F-5 and its predicted-set column **assume** the derivation and would have
  to be redone if the derivation is wrong.
- It contains **no measurement**. Every number is either arithmetic on declared
  parameters, an order-of-magnitude estimate flagged **[HAND-DERIVED]**, or a
  figure quoted from a committed record and flagged **[COMMITTED]**.
- It approves nothing. `TASK-20260729-042` reviews the contract, the derivation
  note and this table; the Coordinator's approval determination lives in the
  `TASK-20260729-043` receipt and in `DEC-20260729-004`.
