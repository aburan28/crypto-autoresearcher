# EXP-ARGON-2608c2 — Implementation Note

Task: TASK-20260812-300522. Contract: `experiments/EXP-ARGON-2608c2/specification.yaml`
(status: approved, approved_by: coordinator, approved_at: 2026-08-14).
Handoff: `ledger/handoffs/TASK-20260812-300522.yaml`.

Requested policy: `executor-implementation`, reasoning_effort `medium`
(per CLAUDE.md's model-policy table). Resolved model: `claude-sonnet-5`
(this Claude Code session; `model: inherit`). `fallback_used: true` per
CLAUDE.md's own note that policy aliases do not resolve to distinct models
under this harness — not a silent substitution, the same fallback every
task in this harness records.

## Headline result: the calibration gate did not pass

**No Argon2 graph (G_real or G_unif) was ever constructed by this task.**
The REQUIRED `bcf891_independent_known_family_calibration` exact-tier stage
did not certify `calibration_error_ratio ∈ [1.0, 1.5]` for
`family_A_doubling_graph` at `exact_tier_size = 64`, because the exact/ILP
computation did not reach a proven optimum within the available compute
(see "Exact-computation tractability finding" below). Per this task's own
binding instruction — "do not construct any G_real/G_unif graph before the
calibration_exact_tier stage completes and calibration_error_ratio falls in
[1.0, 1.5] for BOTH family_A_doubling_graph and family_B_pure_chain, at
every exact_tier_size" — and per specification.yaml's `stopping_rules`
first entry, this is a **procedural halt before any Argon2 construction**,
not a numeric calibration failure and not a falsification of
H-ARGON-ef2f0b. See `execution_report.md` for the full accounting.

## Code layout (all within declared write_scope)

- `runs/_lib/graphs.py` — calibration reference-family constructors
  (`family_A_doubling_graph`, `family_B_pure_chain`), the frozen greedy
  eps-depth-reducing-set heuristic (`greedy_reduce`), and the exact ILP
  solver (`exact_min_removal_ilp`, via `pulp`/CBC).
- `runs/_lib/argon2_lane.py` — the single-lane Argon2 reference-index DAG
  builder (`build_real_graph`, `build_unif_graph`) for all three variants,
  per RFC 9106 (KN-LIT-7f3c21) Secs. 3.2, 3.4.1-3.4.2. **Smoke-tested
  (structural invariants: node 0/1 have no reference edge, every later
  node has exactly one chain + one reference edge, all edges point
  strictly backward; KS statistic computed on a toy q=64/t=1 instance for
  all three variants, confirming the expected non-uniformity direction --
  D≈0.18-0.28, p≪0.05 for all three toy variants) as
  `implementation_snapshot`, but never invoked on this task's declared run
  set, and this smoke test is NOT a declared run** (no manifest/budget
  accounting was created for it; it used a fixed toy `q=64` purely to check
  the code executes and produces structurally sane, directionally-expected
  output before being retained for a future amended task)
  because the calibration gate blocked all downstream construction. Kept as
  the reproducible artifact a future task can dispatch once the exact-tier
  tractability issue below is resolved (e.g. with a commercial ILP solver,
  a structure-specific exact algorithm for `family_A_doubling_graph`, or a
  revised exact_tier_sizes list, all of which require a Coordinator-level
  protocol amendment, not an Executor decision).
- `runs/_lib/ks.py` — one-sample Kolmogorov–Smirnov test against
  Uniform[0,1) (Stephens 1970 asymptotic approximation), self-implemented
  because neither `scipy` nor `numpy` is installed in this environment (see
  "Environment" below). **Never invoked** for the same reason as above.
- `runs/_lib/calibration_exact_cell.py` — the reproduction CLI actually
  invoked for every calibration_exact_tier run (see each run's
  `command.txt`).
- `runs/RUN-ARGON-2608c2-*/` — six immutable run directories, one per
  (`family`, `exact_tier_size`) cell of the REQUIRED calibration exact
  tier (2 families × 3 sizes = 6 runs). No other runs were planned or
  executed on this task (calibration_greedy_tier and every Argon2-graph
  stage are downstream of the gate and were not reached).

`runs/amendments/` is unchanged (empty `.gitkeep`, per the frozen contract
— no protocol_amendment was filed by this task).

## Exact-computation tractability finding (the key protocol deviation)

`bcf891`'s `exact_tier_procedure` calls the exact/ILP computation
"exact-tractable" at `exact_tier_sizes = {16, 32, 64}`. This session found
that assumption does **not** hold uniformly for `family_A_doubling_graph`
(the depth-robust-leaning family, which is deliberately adversarial: many
overlapping long paths survive almost any single-node or few-node removal)
using the only ILP tooling available in this environment (`pulp` 3.3.2 with
its bundled open-source CBC 2.10.3 — no commercial solver such as Gurobi or
CPLEX is installed or reachable).

**Formulation used** (`graphs.exact_min_removal_ilp`): a single-shot MILP,
not the naive lazy path-hitting cutting-plane this session also tried and
rejected (see below) — binary `x_v` (removed), integer depth variable `d_v`
bounded `[0, v]` (tight: at most `v` predecessor slots exist before index
`v`), edge constraints `d_v >= d_u + 1 - M_uv(x_u+x_v)` with per-edge
`M_uv = v` (tight, not a blanket `n`), and `d_v <= target + M_v x_v` with
`M_v = max(v - target, 0)`. This formulation is exact in principle (proof
in the function's docstring); the practical limitation is CBC's ability to
close the branch-and-bound gap in bounded wall-clock, not the formulation's
correctness.

**Methods tried and rejected before settling on the above:**
1. A naive big-`M` formulation with `M = n+2` uniformly: LP relaxation is
   extremely weak (root bound ≈ 0.24–0.35 against integer optima of 5–21);
   CBC exhausted a 60s budget on `q=32` without closing the gap.
2. A lazy cutting-plane / Benders-style formulation (`x`-only variables,
   iteratively adding "at least one node on this violated path is removed"
   constraints found via the same DP): rejected after empirically
   observing (`q=16`, logged in this session) that with LP-degenerate ties
   among many equally-good single-node cuts, this method exhaustively
   re-discovers essentially every subset of a given cardinality before
   advancing to the next (still at 2-element subsets after 130+ rounds on a
   16-node graph) — an artifact of `family_A_doubling_graph`'s symmetry, not
   a bug; adding a lexicographic tie-breaking secondary objective did not
   fix it within a practical iteration budget.
3. Two from-scratch branch-and-bound implementations (path-length branching,
   then binary include/forbid-pivot branching with a vertex-disjoint-path
   packing lower bound): both correctly *improved* the best-found incumbent
   over the greedy heuristic's starting bound (e.g. `q=32`: greedy 11 →
   B&B found 10 within 90s) but did not *prove* optimality for `q≥32`
   within a 90s budget.

**Empirically confirmed and independently important**: `pulp`'s
`LpStatus[status] == "Optimal"` does **not** by itself mean CBC proved
optimality. `contextlib.redirect_stdout` does not capture CBC's log at all
(CBC runs as an external subprocess writing to OS file descriptor 1
directly), so an earlier version of `exact_min_removal_ilp` in this session
silently mis-classified a `q=64` run that CBC's own terminal log showed
ended with `Result - Stopped on time limit` (gap 13.08, best possible only
1.207 against an incumbent of 17) as `"proven_optimal"`. `graphs.py`'s
final version fixes this by redirecting the real OS-level fd 1 to a temp
file for the duration of the solve and parsing the captured text for
`"Stopped on time limit"`. This is recorded here because it is exactly the
kind of solver-status-trusted-without-verification error the invalidation
rule ("independently checked against RFC 9106's pseudocode... not asserted
by mere self-report") is written to prevent, generalized to the exact
solver's own optimality claim.

**Final calibration_exact_tier results** (all six required cells were
computed; see `runs/RUN-ARGON-2608c2-*/raw-result.json` for the
machine-readable record):

| family | q | native_depth | target | greedy \|S*\| | exact \|S*\| | exact status | ratio | certified? |
|---|---|---|---|---|---|---|---|---|
| family_A_doubling_graph | 16 | 15 | 7 | 6 | 5 | proven_optimal (5.3s) | 1.2000 | yes |
| family_A_doubling_graph | 32 | 31 | 15 | 11 | 8 | proven_optimal (39.3s) | 1.3750 | yes |
| family_A_doubling_graph | 64 | 63 | 31 | 21 | **≤17** (CBC dual lower bound 5, from `⌈4.433⌉`) | **time_limit_incumbent** (150s cap, extended-budget diagnostic run to 300s: still not closed, dual bound only reached 4.43) | **[1.235, 4.20]** (uncertified range, not a point value) | **no** |
| family_B_pure_chain | 16 | 15 | 7 | 1 | 1 | proven_optimal (0.01s) | 1.0000 | yes |
| family_B_pure_chain | 32 | 31 | 15 | 1 | 1 | proven_optimal (0.01s) | 1.0000 | yes |
| family_B_pure_chain | 64 | 63 | 31 | 1 | 1 | proven_optimal (0.02s) | 1.0000 | yes |

Because the true `family_A_doubling_graph` q=64 minimum lies somewhere in
`[5, 17]` (a certified dual bound and a certified feasible upper bound,
neither tight), the true `calibration_error_ratio` at this cell lies
somewhere in `[21/17, 21/5] = [1.235, 4.20]`. This range is **not**
contained in `[1.0, 1.5]`, so the gate cannot be confirmed to pass at this
cell — nor can it be confirmed to *fail* outside the guarantee (the true
value might still be ≤1.5; we do not know). This uncertainty, not a
measured out-of-range ratio, is what blocks the run set.

An extended-budget diagnostic re-run of the same `q=64` cell at a 300s cap
(recorded in this note, not as a separate immutable run directory, since it
used a non-declared ad hoc budget purely to characterize the tractability
question — the declared, budget-accounted run is the 150s-capped one in
`RUN-ARGON-2608c2-2ba6b8/`) showed the CBC dual bound climbing only from
1.207 to 4.433 over the additional 150s, i.e. convergence is not close;
further extending the time budget within this task's declared ceiling
would not plausibly have closed the gap.

## Family construction — disclosed interpretation choice

`family_A_doubling_graph`'s spec text ("reference edge to `j - 2^k` for
every `k` such that `1 <= 2^k < j`") is read here as `k >= 1` (back-
distances 2, 4, 8, ...), excluding `k=0` (back-distance 1, which duplicates
the chain edge to `j-1` with no effect on longest-path depth). Disclosed,
not silent — see `graphs.py` docstring.

## Frozen greedy algorithm — implementation notes

`greedy_reduce` implements exactly the declared algorithm (topological
longest-path DP; remove the node nearest the current longest path's
midpoint; repeat until target depth reached), with one performance
optimization that does not change its semantics: because every edge in
these graphs points from a strictly lower index to a strictly higher index
(index-monotone DAG), removing node `mid` can only change depths at
indices `>= mid`; the DP is therefore only re-run over `[mid, n)` on each
iteration rather than from scratch. Verified against a from-scratch full
recompute on all six calibration cells (`native_depth`/`greedy_final_depth`
values agree with independent re-verification via `graphs.verify_removal`).

## Exact solver — independence from the greedy heuristic

Per DEC-20260812-03fa10's calibration_design_ruling, the exact method must
be methodologically independent of the greedy heuristic it calibrates. The
final `exact_min_removal_ilp` uses CBC branch-and-cut over an integer
program with depth variables — a fundamentally different algorithm from
the greedy heuristic's local "remove the midpoint of the current longest
path" rule — satisfying that independence requirement even though both
ultimately call the same `_dp_range`/depth-computation primitive to
*verify* candidate solutions (verification is not part of either method's
own search procedure).

## Environment

- Python 3.11.15, Ubuntu 24.04.4 LTS, x86_64, 4 vCPU, 15 GiB RAM.
- `pulp` 3.3.2 was installed via `pip install pulp` at the start of this
  task (`pip install --quiet pulp`) because neither `pulp`, `scipy`,
  `numpy`, nor `networkx` was present in the base environment. This is a
  tooling installation, not a dataset; no password, credential, leaked
  corpus, or third-party dataset was introduced. `pulp` bundles the
  open-source CBC solver (2.10.3, Dec 15 2019 build) used for every exact
  computation in this task.
- No GPU, no network access used during any run (all seed material is
  synthetic and generated in-process; the Argon2 code path that would have
  used `hashlib.blake2b` synthetic seed material was never invoked, per the
  gate above).

## Protocol deviations (recorded per AGENTS.md rule 9 / executor.md #12)

1. **Exact-tier tractability**: `family_A_doubling_graph` at
   `exact_tier_size=64` could not be certified exact within the available
   ILP tooling and a bounded time budget (150s declared, 300s diagnostic).
   This is the controlling deviation for this task's outcome (see above).
2. **Single-lane Argon2 window model** (documented in `argon2_lane.py`,
   never exercised): a simplified single-lane candidate-window rule was
   implemented in place of RFC 9106's full per-segment safety-window
   carve-outs, identical for G_real and G_unif so the window-size-matching
   control is preserved. Disclosed for completeness even though this code
   path was never run.
3. **G is not bit-exact**: `argon2_lane.py`'s stand-in for the BLAKE2b-
   derived compression function `G` uses `hashlib.blake2b` as a keyed PRF
   over position/content metadata rather than reproducing RFC 9106's exact
   8×8-permutation compression function. Disclosed for completeness; never
   exercised.
4. **Tooling installation**: `pulp` was installed via `pip` mid-task (see
   Environment). No experiment-data package was installed; only a
   general-purpose ILP library.

## What was NOT produced, and why

Per the calibration gate procedurally blocking all downstream work, the
following `required_artifacts` from specification.yaml were **not**
produced, and are recorded here as missing-with-reason rather than
fabricated or silently omitted:

- Per-(variant, t, q) rho, KS statistic/p-value, precondition labels: not
  produced — no Argon2 graph was ever built (gate blocked).
- `calibration_greedy_tier_table` (greedy-only |S*| at 512/2048/8192 for
  both calibration families): not produced — this stage is downstream of
  the exact-tier gate in the declared stage order and was not started once
  the gate could not be confirmed to pass; running it would not have
  changed the gate's binding block on Argon2 construction, and spending
  further budget on it was not warranted given the terminal outcome.
- `argon2i_seed_consistency_report`: not produced — requires a built
  Argon2i G_real graph, never constructed.
- Optional `q=16384` stretch cells: not attempted (moot; required cells
  were never reached either).

What **was** produced in full: all six REQUIRED calibration_exact_tier
cells (both families, all three exact_tier_sizes), each independently
verified (`verify_removal`), each with a complete immutable run record;
the `implementation_snapshot` source for every component including the
never-invoked Argon2 builder and KS test (written and available for a
future amended task); and this implementation note plus
`execution_report.md`.
