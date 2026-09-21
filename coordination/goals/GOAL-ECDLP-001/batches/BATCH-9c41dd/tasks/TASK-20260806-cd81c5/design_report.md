# TASK-20260806-cd81c5 — design report

**Deliverables frozen.** `ledger/hypotheses/H-ICEX-9e54c2.yaml`,
`experiments/EXP-ICEX-146ff5/specification.yaml`, this file.
**Nothing was run, no goal status moved, nothing was promoted to `knowledge/`, no commit
was made.** The contract is approved as a contract; execution is not authorized (three
open preconditions, §6).

---

## 1. What was found before designing anything

`IDEA-20260803-fa9839` has already been audited once. `BATCH-156658/SCOPE-DECISION.md`
(owed to the ledger as `DEC-20260805-bb162b`) **declined** to bind it to
`GOAL-ECDLP-001`, routed it to `GOAL-ICEX-001`, independently re-derived and **confirmed
its core algebra**, and attached **four defects** any successor must repair. That file is
the single most important input to this task and was not named in the handoff. All four
repairs are carried (§4). The routing objection is *not* resolved here and is recorded as
an open precondition rather than assumed away (§6).

## 2. The dependency situation, verified rather than assumed

Verified from committed repository state, not asserted:

- `numpy 2.4.0` is recorded in the committed manifests of `RUN-YIELD-001-*`.
- `sympy` is imported at module scope by `harness/runner.py`, which produced those
  manifests, so it is present in the harness environment.
- The **only** committed manifest recording a SageMath runtime is
  `experiments/EXP-OIFP-0ca0c9/runs/RUN-OIFP-001/manifest.json` — `"SageMath 10.9"` on
  `"darwin arm64 (macOS 26.6)"`, i.e. a **different machine** from the linux worktree
  this contract targets.

That last point drove the design decision: the contract requires the **Python standard
library only** (`fractions.Fraction`, `decimal.Decimal` at 50 digits, `math`, `json`).
numpy is permitted but load-bearing nowhere, and `INV-DEP` invalidates a run whose driver
cannot complete with numpy uninstalled. Exact rational arithmetic is not a fallback here,
it is the *right* tool: every gate tolerance is zero, and a floating-point implementation
could not support a zero tolerance.

## 3. The calibration gate — how the conflict was resolved

The handoff requires a mandatory calibration gate reproducing "the KNOWN extension-field
index-calculus exponent," with a numeric tolerance, tight enough that a wrong model fails.
The proposal makes that gate depend on **transcribing a primary source**, and primary
sources are unreachable here. `SCOPE-DECISION §5.4` concluded the honest prior is that the
gate is **UNRUN** and therefore *nothing* is emitted — which would make the contract
unrunnable, i.e. the wrong experiment.

**Resolution: two gates, with the executable one blocking the deliverable.**

**GATE-A — calibration, hard blocker on everything, executable here, tolerance zero.**
Five arms, each reproducing a quantity the model did not choose:

- **A1** — the Gaudry–Diem `1/n!` extension-field decomposition probability. `KN-FIND-007`
  records that this probability *is* the conservation mean, so the check needs no
  retrieval. Required exactly: `n!·C(q+n−1,n)/q^n == ∏(1+j/q)`.
  **This is the arm that can fail.** It discriminates the three realistic counting-convention
  errors: the distinct-subset count `C(B,m)` gives first-order correction `−n(n−1)/2q`
  (wrong sign), the naive `B^m/m!` gives `0`, ordered tuples `B^m` give a leading constant
  `n!` too large. All three fail at tolerance zero.
- **A2** — relation-charge scaling: `C_rel(B)·B^(m−1) == m!·N·D` exactly at every `B`, and
  at the unrebalanced full-subfield-line instantiation (`B=q`, `D=q^0`, `N=q^n`, `m=n`)
  the charged total exponent in `q` must be **exactly 2**. That is an extension-field
  index-calculus exponent any reader recovers by hand; a mis-powered relation term misses it.
- **A3** — optimizer identities. Stationarity residual below `1e-25` in 50-digit decimal;
  ratio identity exact. The proposal's `1e-12` was **deliberately tightened** — a tolerance
  a wrong model can survive is not a gate.
- **A4** — the optimizer exponent is `(1+d)/(m+ω−1)`, not `1/(m+ω−1)`. This arm exists
  because the **proposal itself pre-registered the wrong value**; the arm catches the one
  error already known to have been made here.
- **A5** — window-shape reproduction against exact rationals pre-registered at design time
  **without an interpreter**. Deliberately capable of convicting its own author.

**GATE-B — external tightness, pre-registered UNRUN, blocks four named readings only:**
any tightness claim; any "no-go"/"impossible"/"closed" phrasing of an empty window; any
comparison with the literature; any prime-field positive reading. It does *not* block the
window or the satellite table.

The in-repository statement of `2−2/n` I located
(`notes/ecdlp_recursive_expansion_literature_map_20260717.md` §2.2, "commonly stated at
Õ(q^{2−2/n})") is an **agent-written secondary note** with correct bibliographic citations
but no transcribed excerpt or hash. It is recorded in the contract as **not** discharging
GATE-B.

**This re-partition of `SCOPE-DECISION §5.4` is declared, not silent** — see
`deviations_from_prior_review.repartition_of_5_4` in the specification, which states what
5.4 required, what the contract does, why, and routes the disagreement explicitly to
`TASK-20260806-7e7ce3`. It is a pre-observation protocol decision taken before any number
exists, not a criterion changed after an outcome.

## 4. The four `SCOPE-DECISION §5` repairs

| Defect | Disposition |
|---|---|
| 5.1 per-fibre `2(1−1/W_eff)` correction at the `N=q^n` baseline | Adopted in the form 5.1 permitted: written as **HEUR-AT-4**, a *reviewable claim* — the conservation identity counts multisets of **group elements** and so already enumerates every sign assignment `x(±P₁±…±P_{m−1})` that `KN-FIND-c41ea9`'s complete splitting produces; applying both double-counts. **CTRL-PARAM** can refute it. |
| 5.2 `B* = N^{1/(m+1)}` false wherever `d>0` | Adopted verbatim; **GATE-A/A4** fails a run reporting otherwise. |
| 5.3 memory row quoted at `B*(m,0)` | Adopted verbatim; every row carries `B*(m,d)` in elements and bits. |
| 5.4 unrun gate collapses the deliverable | Adopted in part and **re-partitioned, declared** (§3). |

## 5. What charging the omitted terms actually changed

Charging the seven stages `GOAL-ECDLP-001`'s objective and `RQ-ICEX-001`'s constraints
require did not merely add rows — it **changed the shape of the answer**, and produced two
findings *against* the proposal. Both are pre-registered as point predictions that
GATE-A/A5 and CTRL-CONVENTION can fail, not asserted as results.

1. **The proposal's `HEUR-AT-1` validation clause is false above a computable boundary.**
   It asserts the threshold exponent is identical under harvest-all and
   one-relation-per-target, "only the constant moves, by at most 1.582". That holds only
   for `d ≤ (ω−1)/m`. Above it the harvest optimum passes the kink `B_k = (m!N)^{1/m}`,
   the 1PT optimum is pinned at the kink, and the exponents differ. At `ω=2` the
   divergence set is non-empty for every `m ≥ 5`.
2. **A physical trial-count floor bounds the window.** The expected trial count
   `m!N/B^{m−1}` at the optimum must be at least 1, forcing `d ≤ ω/(m−1)`.

Intersecting the three constraints, the pre-registered window supremum at `ω=2` is
EMPTY, EMPTY, `1/4`, `3/10`, `1/3`, `1/3`, `2/7`, `1/4`, `2/9`, `1/5`, `2/11` at
`m = 2…12`. The proposal's `d < (m−3)/4` agrees at `m=4` and then grows without bound;
**the charged window peaks at `1/3` for `m ∈ {6,7}` and decays like `2/(m−1)`.** That is a
materially different instruction to the deferred goals than "go to higher arity."

`CTRL-DEGENERATE` arm D2 is the mechanism that makes this visible and is designed to
expose a real model defect rather than to pass: at `D_trial = N` the raw two-term model
reports index calculus *winning* for `m ≥ 8`, which is absurd (the first trial already
costs `N`). The pre-registered flip arity is exactly 8; a different flip invalidates the
run.

## 6. Execution authorization — three open preconditions

1. **P1** — independent red-team pass `TASK-20260806-7e7ce3`. An adverse finding requires
   one versioned `protocol_amendment`, snapshot-committed and re-reviewed, before execution.
2. **P2** — the goal binding is unresolved. `GOAL-ICEX-001.next_action` reads "NO ICEX
   MEASUREMENT AUTHORIZED". This contract performs no measurement, but that reading is
   `GOAL-ICEX-001`'s Coordinator's to make on its own record. **This file does not make it.**
3. **P3** — revisit condition **R-D** of the decline. The contract now charges descent,
   verification, multi-target and BSGS; it does **not** model relation rank (declared, with
   its direction). Whether that satisfies R-D, and whether the extension needs its own
   `IDEA-*` record, is an unmade Coordinator decision.

## 7. WHAT THIS EXPERIMENT CANNOT CONCLUDE

This is the section the completion gate requires. Every item is binding on any record that
cites `EXP-ICEX-146ff5`.

1. **It cannot conclude anything about prime-field ECDLP hardness in either direction.**
   It fixes a window with `D_trial` **free**. `KN-OPEN-001` is not narrowed by one bit.
2. **A non-empty window is not an algorithm, a construction, or evidence that one exists.**
   No oracle achieving any `d` inside the window is constructed, exhibited, or argued to
   exist. "The window is non-empty at `m=6`" may never be written or paraphrased as
   "prime-field ECDLP is weakened", "a sub-rho algorithm exists", or "index calculus is
   feasible at `m=6`".
3. **An empty window is not a no-go.** While GATE-B is unrun, empty means "empty within
   this charge". The words no-go, impossible and closed are forbidden. The model is known
   *not* to be tight — the recalled `2−2/n` would beat it at `n=3`, and the observation
   collision localizes the missing ingredient to the relation-search term (large primes
   being the named, **unverified**, candidate).
4. **No-go readings are conservative only against omitted terms *inside* the modelled
   algorithm — never against better algorithms outside it.** Both caveats travel together.
5. **It cannot validate or invalidate any solving-degree measurement.** The satellite table
   converts a degree to a cost through `HEUR-AT-3`, the Macaulay charge, which is
   **unvalidated in this corpus**. The conditional qualifier may not be dropped anywhere.
6. **It cannot authorize, prioritize, deprioritize or close any satellite goal.** The table
   is an *input* to each goal's own Coordinator decision, not the decision.
7. **It is not crypto-tier evidence.** Evaluations at `N ∈ {2^160,…,2^384}` are **model
   arithmetic at those symbols**, stamped `model_evaluation: true`. The only enumerated
   instances are `Z/N` with `N ≤ 2^16` (CTRL-NULL). **No elliptic curve is used and no
   ECDLP instance is solved at any size.**
8. **It cannot discharge any heuristic.** `HEUR-AT-1…4` remain conditional regardless of
   outcome (`docs/claims-and-verification.md`).
9. **It cannot establish that relation rank, `D_trial` tail behaviour, or descent depth are
   negligible.** Rank is declared-omitted; the charge is a lower bound; `D_trial` is an
   expectation and a heavy-tailed oracle satisfies no row.
10. **Reproducibility is not correctness.** Exact arithmetic reproduces bit-for-bit by
    construction. Only GATE-A, the five controls, and independent re-derivation can convict
    this contract.
11. **It meets no completion criterion of any goal, moves no hypothesis status, and opens
    none of the four asymptotic-complexity promotion gates.** Nothing here bears on any
    deployed curve, protocol or scheme.
12. **A timeout, crash or implementation failure is infrastructure signal, never a negative
    mathematical result** (AGENTS.md rule 5).

## 8. Residual risks I could not close

- **No shell.** `tools/allocate_id.py --check` was not run; the ids were `--check`
  confirmed free by the dispatching session at batch open, and this worktree only verified
  by glob. Recorded as a partial check with its residual risk, not as a pass.
- **The pre-registered window rationals were derived without an interpreter.** GATE-A/A5
  exists precisely because a mismatch is as likely my algebra as the implementation's, and
  it invalidates the run either way.
- **`HEUR-AT-4` is a claim, not a proof.** If `CTRL-PARAM` refutes it,
  `KN-FIND-c41ea9`'s untested `2^{n−1}` compounding clause is live — and that refutation
  would be worth more than the window.
- **The §5.4 re-partition is a judgement call** and is routed to the red team as such.

---

## 9. Coordinator decision

Recorded here because `ledger/decisions/` is **not** in this task's `write_scope` — the
batch assigns `DEC-20260806-8f7e4f` to `TASK-20260806-636e61`, the post-red-team ledger
archive. No `DEC-*` id is minted here: this session has no shell, cannot run
`tools/allocate_id.py --check`, and will not fabricate an identifier (AGENTS.md rules 9
and 14). Until that archive, this is a durable coordination artifact and **not** an
official ledger transition.

```yaml
coordinator_decision:
  id: null                       # owed to DEC-20260806-8f7e4f at TASK-20260806-636e61
  recorded_at: '2026-08-06'
  decided_by: coordinator
  under_task: TASK-20260806-cd81c5
  context: >-
    IDEA-20260803-fa9839 (the arity threshold) was named the highest-value zero-compute
    item in the ECDLP portfolio and is the declared exit from the six-goal measurement
    deadlock. It had already been audited once - BATCH-156658/SCOPE-DECISION.md declined
    to bind it to GOAL-ECDLP-001, confirmed its core algebra, and attached four defects.
    This task converts it into a specified hypothesis and a frozen contract that runs on
    the Python standard library alone.
  decision: approve
  target_ids: [H-ICEX-9e54c2, EXP-ICEX-146ff5, IDEA-20260803-fa9839]
  rationale:
  - >-
    The contract is executable HERE. Standard library only; numpy permitted but
    load-bearing nowhere; INV-DEP invalidates a run that silently acquires a dependency.
    The one committed SageMath manifest in the corpus is from a different machine, which
    is why portability rather than availability drove the choice.
  - >-
    The calibration gate was made executable without weakening it. GATE-A has five arms
    at tolerance ZERO reproducing quantities the model did not choose - the Gaudry-Diem
    1/n! probability with its exact first-order correction, the unrebalanced
    extension-field exponent 2, the optimizer identities at 1e-25, the (1+d) optimizer
    exponent, and the pre-registered window shape. Three realistic counting-convention
    errors, one mis-powered relation term and one wrong pre-registered exponent each fail
    an arm; the last is ALREADY ON RECORD as having been made in the source proposal.
  - >-
    GATE-B (external transcription) is pre-registered UNRUN and blocks four named
    readings - tightness, no-go phrasing, literature comparison, and any prime-field
    positive reading. The re-partition of BATCH-156658 defect 5.4 is declared in the
    contract, is a pre-observation protocol decision, and is routed to the red team for
    adjudication rather than settled here.
  - >-
    All three mandatory controls are present and each can fail. CTRL-NULL enumerates
    actual multisets over actual groups for four base families including a structureless
    null and a rank-deficient degenerate, and recomputes the WINDOW from each - so it
    bites on the deliverable, not on an intermediate. CTRL-DEGENERATE D1 must report
    index calculus losing by at least 1.1287*sqrt(N); D2 is designed to EXPOSE a real
    model defect (the raw verdict flips absurdly at m = 8) rather than to pass.
  - >-
    All seven stages GOAL-ECDLP-001's objective names are charged against rho AND BSGS,
    with relation rank declared-omitted and its direction stated. Charging them changed
    the answer - the window is bounded, peaks at 1/3 for m in {6,7}, and decays like
    2/(m-1), against the proposal's unbounded d < (m-3)/4. Two findings against the
    proposal fall out and are pre-registered as falsifiable predictions, not asserted.
  - >-
    The satellite deliverable is defined exactly - D_reg_max(m, N, omega, omega_GB, n_v)
    as an integer per cell for GOAL-SDEG-001, GOAL-DREG-001 and GOAL-SIG-001, with
    NOT-THRESHOLD-CONVERTIBLE marked where no degree qualifies, conditional on HEUR-AT-3
    at every citation, and explicitly not a decision about any goal.
  evidence_refs:
  - ledger/proposals/IDEA-20260803-fa9839.yaml
  - coordination/goals/GOAL-ECDLP-001/batches/BATCH-156658/SCOPE-DECISION.md
  - knowledge/findings/KN-FIND-007.md
  - knowledge/findings/KN-FIND-c41ea9.md
  - ledger/evidence/EV-FBG-001.yaml
  - ledger/evidence/EV-ICEX-001.yaml
  - ledger/evidence/EV-IC-002.yaml
  - ledger/goals/GOAL-ICEX-001.yaml
  - knowledge/open-problems/KN-OPEN-001.md
  - knowledge/open-problems/KN-OPEN-020.md
  - analysis/SSI-ECDLP-SYNTHESIS-20260803.md
  - experiments/EXP-YIELD-001/runs/RUN-YIELD-001-BASELINE-RHO-BSGS/results.json
  limitations:
  - >-
    APPROVAL OF A CONTRACT IS NOT AUTHORIZATION OF A RUN. Three preconditions are open -
    the independent red-team pass, the unresolved GOAL-ICEX-001 binding, and whether the
    seven-stage extension satisfies revisit condition R-D of the prior decline.
  - >-
    NO HYPOTHESIS STATUS MOVES. H-ICEX-9e54c2 is created at `specified`. H-STR-002 and
    every other live hypothesis keep their current status. No asymptotic-complexity
    promotion gate is opened. No closure quorum is claimed.
  - >-
    Claim tier toy. Nothing here measures ECDLP, no curve is used, no oracle is
    constructed, KN-OPEN-001 is untouched, and nothing bears on any deployed system.
  - >-
    The pre-registered window rationals were derived WITHOUT AN INTERPRETER. GATE-A arm
    A5 exists to catch the authoring Coordinator's own algebra, and invalidates the run
    either way.
  knowledge_promotion:
    promoted: []
    not_warranted: >-
      No run happened and no evidence record was produced. A design-and-approval task is
      not `replicated` or `strong` evidence and promotes no KN-FIND. The two findings
      against IDEA-20260803-fa9839 (the false HEUR-AT-1 convention clause and the missing
      trial-count admissibility bound) are DESIGN-TIME DERIVATIONS pre-registered as
      falsifiable predictions, not adjudicated results; they become promotable only if a
      run confirms them and independent review accepts it.
  next_actions:
  - >-
    TASK-20260806-fb85f5 snapshot-archives H-ICEX-9e54c2, EXP-ICEX-146ff5 and this report
    before any reviewer reads them. Nothing here is durable until that commit is accepted
    by the post-commit verifier.
  - >-
    TASK-20260806-7e7ce3 red-teams the contract and is asked EXPLICITLY to adjudicate
    three things - whether the GATE-B re-partition of BATCH-156658 defect 5.4 is a
    relaxation; whether GATE-A's zero tolerances are genuinely capable of failing; and
    whether any of the seven charged stages is omitted or charged at zero.
  - >-
    The GOAL-ICEX-001 / GOAL-ECDLP-001 binding (execution_authorization P2 and P3) is a
    Coordinator decision on the owning goal's own record, preserving its own single next
    action. It is NOT made here and must not be treated as made.
  dominated_by: >-
    Not applicable as an attack - no algorithm is proposed and no Pareto point is claimed.
    Written explicitly rather than left null.
  sota_delta: >-
    Zero on every ECDLP cost axis. Pollard rho remains the baseline; no attack, no
    measurement, no exponent moved.
  inference:
    requested_policy: coordinator-orchestration-code
    resolved_model_id: claude-opus-5
    reasoning_effort: null
    fallback_used: true
    fallback_reason: >-
      This Claude Code harness cannot resolve the policy aliases in
      orchestration/model-policies.yaml; per-role policy selection under this runtime is
      process-level. Recorded, never silently substituted (AGENTS.md rule 11).
    degraded_allowed: false
    degraded_requirements: []
    model_verified: false
    model_verified_reason: >-
      No adapter probe receipt exists for this session.
```
