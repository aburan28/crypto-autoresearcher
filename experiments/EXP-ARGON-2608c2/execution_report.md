# Execution Report — EXP-ARGON-2608c2

Task: TASK-20260812-300522 | Handoff: `ledger/handoffs/TASK-20260812-300522.yaml`
Contract: `experiments/EXP-ARGON-2608c2/specification.yaml` (approved,
approved_by: coordinator, 2026-08-14, version 1)
Implementation note: `experiments/EXP-ARGON-2608c2/implementation.md`

```yaml
execution_report:
  experiment_id: EXP-ARGON-2608c2
  implementation_commit: fb8fde81f9911bb34e212f26e196ebe5e6f2fd82
  implementation_commit_note: >-
    Git HEAD of this shared worktree at the time these runs executed
    (branch claude/experiment-loop-m0xg9s). Working tree carried untracked
    paths from this task's own writes plus a concurrent, unrelated task's
    writes under experiments/EXP-ISOU-2ac81f/** (not touched by this task).
    No tracked file was modified. Recorded per-run in each
    runs/RUN-ARGON-2608c2-*/manifest.yaml `code.commit`/`code.dirty`.
  requested_policy: executor-implementation
  requested_reasoning_effort: medium
  resolved_model_id: claude-sonnet-5
  fallback_used: true
  fallback_note: >-
    Policy aliases resolve to the single session model under this Claude
    Code harness (CLAUDE.md "Model policy note"); not a silent substitution.
  protocol_deviations:
    - >-
      Exact-tier tractability: family_A_doubling_graph at exact_tier_size=64
      could not be certified exact by the available open-source ILP tooling
      (pulp 3.3.2 / CBC 2.10.3, no commercial solver available) within a
      150s declared time budget (nor within a 300s diagnostic extension).
      This is the controlling deviation; see implementation.md.
    - >-
      pulp was installed via `pip install pulp` mid-task (tooling only, no
      experiment data); scipy/numpy/networkx were absent and NOT installed
      -- the KS test was self-implemented instead (never exercised, since
      the gate blocked all Argon2-stage work that would have needed it).
    - >-
      family_A_doubling_graph's spec text is read as excluding the k=0
      back-distance (already the chain edge); disclosed interpretation, no
      effect on any reported number's correctness.
    - >-
      Single-lane Argon2 window-model simplification and G-as-blake2b-PRF
      stand-in are documented in argon2_lane.py/implementation.md but were
      NEVER EXERCISED -- no Argon2 graph was built on this task.

  runs:
    completed:
      - RUN-ARGON-2608c2-294e74   # family_A_doubling_graph, q=16, proven_optimal
      - RUN-ARGON-2608c2-868a32   # family_A_doubling_graph, q=32, proven_optimal
      - RUN-ARGON-2608c2-4da88e   # family_B_pure_chain,     q=16, proven_optimal
      - RUN-ARGON-2608c2-1a1711   # family_B_pure_chain,     q=32, proven_optimal
      - RUN-ARGON-2608c2-e0b77a   # family_B_pure_chain,     q=64, proven_optimal
    invalid: []
    failed:
      - run_id: RUN-ARGON-2608c2-2ba6b8   # family_A_doubling_graph, q=64
        status: resource_exhaustion
        reason: >-
          CBC did not close the optimality gap within the declared 150s
          time budget (log: "Stopped on time limit"; incumbent |S*|<=17,
          dual lower bound only 5 after rounding 4.433; a 300s diagnostic
          extension only raised the dual bound to 4.433, not close to
          closing). Result is a genuine, correctly-computed, but
          UNCERTIFIED upper bound, not a negative or invalid measurement of
          any Argon2 quantity -- no Argon2 graph was ever built. Classified
          resource_exhaustion per agents/executor.md's failure taxonomy,
          per AGENTS.md rule 3 (never negative mathematical evidence).

    not_run:
      - stage: calibration_greedy_tier
        reason: >-
          Downstream of the exact-tier gate in the declared stage order;
          not started once the gate could not be confirmed to pass for
          family_A_doubling_graph q=64 (informational stage only -- running
          it would not have unblocked Argon2 construction).
      - stage: argon2i_construction_and_ks
        reason: BLOCKED by calibration gate (see below). Never started.
      - stage: argon2d_id_construction_and_ks
        reason: BLOCKED by calibration gate. Never started.
      - stage: g_unif_null_construction
        reason: BLOCKED by calibration gate. Never started.
      - stage: greedy_rho_compute
        reason: BLOCKED by calibration gate. Never started.
      - cells: "q=16384 optional stretch (all variants, both t)"
        reason: >-
          Moot -- required cells were never reached either (gate blocked
          all Argon2 construction).

  observations:
    calibration_gate_outcome: NOT CONFIRMED (procedural halt, resource_exhaustion)
    calibration_gate_binding_text: >-
      "do not construct any G_real/G_unif graph before the
      calibration_exact_tier stage completes and calibration_error_ratio
      falls in [1.0, 1.5] for BOTH family_A_doubling_graph and
      family_B_pure_chain, at every exact_tier_size" (this handoff,
      constraints; mirrors specification.yaml stopping_rules first entry).
    calibration_exact_tier_table:
      - {family: family_A_doubling_graph, q: 16, native_depth: 15, target_depth: 7, greedy_size: 6, exact_size: 5,  exact_status: proven_optimal,        ratio: 1.2000,            certified: true}
      - {family: family_A_doubling_graph, q: 32, native_depth: 31, target_depth: 15, greedy_size: 11, exact_size: 8,  exact_status: proven_optimal,        ratio: 1.3750,            certified: true}
      - {family: family_A_doubling_graph, q: 64, native_depth: 63, target_depth: 31, greedy_size: 21, exact_size: "<=17 (upper bound); >=5 (dual lower bound)", exact_status: time_limit_incumbent, ratio: "[1.235, 4.20] (uncertified range)", certified: false}
      - {family: family_B_pure_chain,     q: 16, native_depth: 15, target_depth: 7, greedy_size: 1, exact_size: 1,  exact_status: proven_optimal,        ratio: 1.0000,            certified: true}
      - {family: family_B_pure_chain,     q: 32, native_depth: 31, target_depth: 15, greedy_size: 1, exact_size: 1,  exact_status: proven_optimal,        ratio: 1.0000,            certified: true}
      - {family: family_B_pure_chain,     q: 64, native_depth: 63, target_depth: 31, greedy_size: 1, exact_size: 1,  exact_status: proven_optimal,        ratio: 1.0000,            certified: true}
    determination: >-
      5 of 6 required exact-tier cells certify ratio in [1.0, 1.5]
      (family_A q=16, q=32; family_B q=16, q=32, q=64). The sixth cell
      (family_A q=64) cannot be certified to lie in [1.0, 1.5] -- the
      certified bracket [1.235, 4.20] straddles the boundary and its upper
      end is far outside it. Per the gate's binding "at every exact_tier_
      size" wording, ALL SIX cells must certify pass before ANY Argon2
      construction; five passing does not satisfy this. No G_real, no
      G_unif, no rho value, no KS statistic exists anywhere in this run
      set for any (variant, t, q) cell.
    rho_table: "NOT PRODUCED -- gate blocked (see above). No entries."
    ks_table: "NOT PRODUCED -- gate blocked (see above). No entries."
    calibration_greedy_tier_table: "NOT PRODUCED -- downstream of exact-tier gate, not started."
    argon2i_seed_consistency_report: "NOT PRODUCED -- requires a built Argon2i G_real graph, never constructed."
    tail_checks: "NOT APPLICABLE -- no rho values exist to check for internal consistency."
    rho_vs_q_scaling_trend: "NOT APPLICABLE -- no rho values exist."
    frozen_prediction_reference: >-
      H-ARGON-ef2f0b `predictions` / specification.yaml
      `preregistered_prediction`: rho<=0.5 confirms, rho>=0.8 falsifies,
      [0.5,0.8) partial per variant; KS p<=0.05 precondition. FROZEN,
      UNCHANGED, and NOT COMPARED AGAINST ANY DATA in this run set, because
      no rho or KS data exists to compare it against. This is not a
      negative_observation against H-ARGON-ef2f0b -- the hypothesis's own
      subject matter (the Argon2 DAG) was never measured.

  anomalies:
    - >-
      pulp's LpStatus reported "Optimal" for a CBC solve that its own log
      showed had been stopped on the time limit with an open gap (observed
      on an exploratory q=64 run before the final exact_min_removal_ilp fix
      in graphs.py); this was caused by contextlib.redirect_stdout not
      capturing CBC's subprocess-level stdout writes. Fixed by redirecting
      OS file descriptor 1 directly and parsing the captured text. Recorded
      per AGENTS.md rule 8 (unexpected observations preserved, not
      discarded) even though the fixed code no longer exhibits it.
    - >-
      family_A_doubling_graph's minimum node-removal set grows much faster
      with q than family_B_pure_chain's (which stays at exactly 1 for every
      tested size) -- consistent with family_A's intended role as the
      depth-robust-leaning reference and family_B's role as the
      deliberately shallow reference (bcf891's own predicted qualitative
      pattern), though this is an aside about the calibration families
      themselves, not a measurement of H-ARGON-ef2f0b's Argon2 claim.
    - >-
      Naive lazy-cutting-plane and big-M ILP formulations (rejected, see
      implementation.md) both independently confirmed the qualitative
      difficulty of family_A_doubling_graph's exact computation growing
      sharply between q=16 and q=32/64 -- this is not a one-off fluke of
      the final formulation.

  artifact_paths:
    - experiments/EXP-ARGON-2608c2/implementation.md
    - experiments/EXP-ARGON-2608c2/execution_report.md
    - experiments/EXP-ARGON-2608c2/runs/_lib/graphs.py
    - experiments/EXP-ARGON-2608c2/runs/_lib/argon2_lane.py
    - experiments/EXP-ARGON-2608c2/runs/_lib/ks.py
    - experiments/EXP-ARGON-2608c2/runs/_lib/calibration_exact_cell.py
    - experiments/EXP-ARGON-2608c2/runs/RUN-ARGON-2608c2-294e74/
    - experiments/EXP-ARGON-2608c2/runs/RUN-ARGON-2608c2-868a32/
    - experiments/EXP-ARGON-2608c2/runs/RUN-ARGON-2608c2-2ba6b8/
    - experiments/EXP-ARGON-2608c2/runs/RUN-ARGON-2608c2-4da88e/
    - experiments/EXP-ARGON-2608c2/runs/RUN-ARGON-2608c2-1a1711/
    - experiments/EXP-ARGON-2608c2/runs/RUN-ARGON-2608c2-e0b77a/

  budget_accounting:
    wall_clock_seconds_budget: 7200
    wall_clock_seconds_used_declared_runs: >-
      ~195s across the six declared calibration_exact_tier runs (5.3+39.3+
      150.1+0.01+0.01+0.02, plus negligible greedy time), well under budget.
    wall_clock_seconds_used_exploratory: >-
      Additional exploratory/diagnostic wall-clock (formulation trials,
      the 300s q=64 extension) was spent investigating the exact-tier
      tractability question before settling on the final formulation and
      the terminal determination; this exploratory work is disclosed in
      implementation.md but is not itself a declared run (no fabricated
      run record was created for throwaway formulation attempts).
    maximum_runs_budget: 200
    maximum_runs_used: 6
    maximum_memory_gb_budget: 2
    maximum_memory_gb_used: "well under 2GB (n<=64 integer arrays, CBC MIPs with <=400 rows/columns)"
    budget_stop_triggered: false
    note: >-
      This task did NOT halt because of the wall-clock/run-count/memory
      budget ceiling -- it halted because the calibration gate itself could
      not be confirmed to pass, per that gate's own binding, procedural
      language, independent of remaining budget headroom.

  required_artifacts_accounting:
    - item: "Run manifests per graph-build-plus-compute run"
      status: PRESENT (6/6 calibration_exact_tier runs)
    - item: calibration_derivation.md content
      status: >-
        PRESENT, embedded in implementation.md ("Exact-computation
        tractability finding" + family construction sections) and in each
        run's raw-result.json, rather than as a separate top-level file --
        this task's write_scope is restricted to implementation.md,
        execution_report.md, and runs/, so required-artifact CONTENT is
        satisfied within those three paths rather than by a fourth
        top-level filename. Flagged explicitly, not silently substituted.
    - item: calibration_greedy_tier_table
      status: "MISSING -- not started (see runs.not_run above); reason recorded, not silently omitted."
    - item: "Per required (variant,t,q) cell rho/KS/precondition data"
      status: "MISSING -- gate blocked; reason recorded."
    - item: argon2i_seed_consistency_report
      status: "MISSING -- gate blocked; reason recorded."
    - item: implementation_snapshot
      status: >-
        PRESENT -- runs/_lib/{graphs.py, argon2_lane.py, ks.py,
        calibration_exact_cell.py}, including the never-exercised Argon2
        builder and KS test, retained for a future amended task.
    - item: certificate
      status: "PRESENT -- {kind: none} in every run manifest, per docs/claims-and-verification.md (pure measurement, no solve/relation claimed)."
    - item: "Final summary report"
      status: "PRESENT -- this file."

  executor_assessment:
    protocol_complete: false
    protocol_complete_note: >-
      The declared protocol's REQUIRED calibration precondition did not
      reach a pass determination; per the protocol's own binding language
      this is itself a complete, terminal, correctly-executed outcome for
      this run set (the protocol does not require Argon2 construction to
      "complete" the task when its own precondition gate is unmet) -- but
      it does mean the experiment's substantive objective (measuring rho)
      was not reached, hence protocol_complete: false in the sense of "the
      full planned sweep did not execute."
    data_quality: limited
    data_quality_note: >-
      The six calibration_exact_tier measurements themselves are good
      quality (5 of 6 independently certified exact via CBC branch-and-cut
      plus from-scratch verification; the 6th is an honestly-bounded
      range, not a fabricated point value). No Argon2 data of any kind
      exists to assess.
    requires_rerun: true
    requires_rerun_note: >-
      A future task cannot simply "rerun this one" -- it requires either
      (a) a Coordinator-level protocol_amendment revising exact_tier_sizes
      or the exact-computation method for family_A_doubling_graph
      specifically (e.g. a structure-specific exact algorithm, a longer
      declared time budget with a commercial ILP solver, or accepting a
      certified-bracket gate criterion in place of a point-value ratio),
      or (b) accepting the current 5/6 result as insufficient to proceed
      and redirecting this sub-line of GOAL-ARGON-001 work. This decision
      is the Coordinator's, not the Executor's, per this task's own
      prohibition on modifying the frozen protocol.
```

## Narrative summary

This task implemented the full REQUIRED `bcf891_independent_known_family_
calibration` exact-tier stage (`family_A_doubling_graph` and
`family_B_pure_chain`, at `exact_tier_sizes` 16, 32, 64) — the binding
precondition specification.yaml requires to pass, procedurally, before any
Argon2 graph may be built. Five of six required cells certified
`calibration_error_ratio ∈ [1.0, 1.5]` via an exact ILP solve independently
re-verified from scratch. The sixth (`family_A_doubling_graph`, `q=64`)
could not be certified exact within the available open-source ILP tooling
and a bounded time budget; the certified bracket for its true ratio,
`[1.235, 4.20]`, is not confirmed to lie within `[1.0, 1.5]`.

Per this task's explicit, procedurally-binding instruction, this is
sufficient to halt: **no Argon2 graph (G_real or G_unif) was constructed
for any variant, and no rho or KS value exists anywhere in this run set.**
This is reported as the terminal result for the whole run set, per
specification.yaml's stopping rules — an infrastructure/tractability
finding (`resource_exhaustion`), not a numeric calibration failure with a
ratio measured outside bounds, and emphatically not a falsification, partial
confirmation, or any other determination about H-ARGON-ef2f0b, whose
Argon2-DAG subject matter was never examined by this task. No conclusion
about H-ARGON-ef2f0b's support or refutation is stated here; that judgment
belongs to the Coordinator under `/review-evidence`, and in this case there
is no rho/KS data for it to judge — only a documented reason why none
exists yet, and the concrete redirect/amendment choices available in
`executor_assessment.requires_rerun_note` above.
