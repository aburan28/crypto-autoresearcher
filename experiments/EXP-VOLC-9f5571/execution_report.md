execution_report:
  experiment_id: EXP-VOLC-9f5571
  task_id: TASK-20260810-a431bd
  goal_id: GOAL-ENDO-001
  batch_id: BATCH-d7e255
  implementation_commit: b56fe67db1a39ebe3860ee65294829d90fff4013
  snapshot_commit_at_dispatch: a9028dcd1
  protocol_deviations:
    - >-
      f=3 conductor-arm class chosen by a disclosed selection rule (smallest
      total class size among the family's 7 candidates at f=3, for
      tractability) since the contract names the arm as "f=3" without pinning
      a specific trace among the several classes at conductor 3 in this
      family; rule applied before any measurement, on structural size only.
    - >-
      SR4 matched-null split sizes for the f=107/T5 arm (1/35) are one short
      of the real class's floor count (36): no f=1 class in this family has
      exactly 37 curves. Closest available (h=36) used; disclosed, not
      reconciled.
    - >-
      SR4's f=3-sweep and f=107-sweep density grids use 3 factor-base sizes
      ([6,10,17]) rather than the 7-size main grid, to bound runtime; the main
      SR3 measurement uses the full 7-size grid.
    - >-
      Two implementation defects were found and repaired before this run was
      reported: (1) an initial SR4 verdict statistic pooled both declared
      halves, a no-op with respect to the split under test; (2)
      `harness.exp_icinv_fullgroup.measure_curve_all_arms` reads module-level
      SEEDS/TARGET_COUNTS constants rather than the values passed to
      `build_curve_package`, so only 1 of 8 declared seeds was scored until
      the constants were explicitly overridden. Both defects are recorded in
      full in `implementation.md` sec 2, with the two superseded run ids they
      produced kept immutable and marked via `SUPERSEDED.md` in each run
      directory.
  runs:
    completed:
      - RUN-VOLC-sr1-sr5-plus-t5-gate-v3
    invalid: []
    superseded:
      - id: RUN-VOLC-sr1-sr5-plus-t5-gate
        reason: >-
          SR4 verdict statistic ignored the declared-half split (pooled hits
          regardless of half). See its SUPERSEDED.md.
      - id: RUN-VOLC-sr1-sr5-plus-t5-gate-v2
        reason: >-
          measure_curve_all_arms scored only 1 of 8 declared seeds
          (module-global SEEDS/TARGET_COUNTS not overridden). See its
          SUPERSEDED.md.
    failed: []
  stopping_rules_fired_in_order:
    - rule: SR1_VELU_GATE
      outcome: PASS
      detail: >-
        p=4001, t=30, ell=2 Velu-rebuilt volcano reproduces {0:3,1:9,2:18,
        3:36,4:72} exactly; 270 directed edges, 0 unmatched; census agrees on
        all 138 curves.
    - rule: SR2_FAMILY_GATE
      outcome: PASS
      detail: >-
        N=19507 family re-derived: 59 candidates, 51 at f=1, 7 at f=3, 1 at
        f=107 (t=211,p=19717) -- matches
        analysis/endomorphism-isogeny-decomposition/MATCHED-ORDER-DESIGN.md
        sec 3 exactly. #E(F_p)=19507 verified per curve and Hurwitz-Kronecker
        census agrees on both chosen conductor-arm classes (f=3: t=-173,
        p=19333, 42 curves; f=107: t=211, p=19717, 37 curves).
    - rule: SR3_SUPPORT_GATE
      outcome: PASS
      detail: >-
        targets_B support certified equal to the enumerated E(F_p) on all 79
        measured curves (42 + 37), zero failures.
    - rule: SR4_NULL_FIRST
      outcome: >-
        COMPUTED AND WRITTEN FIRST (before any real level contrast is read;
        note no real level contrast was reachable in this run at all, see
        SR6/data-unreachability below). Both null instances show
        NULL_FIRES_OVERDISPERSION_DETECTED under an "any cell, any declared
        half over-dispersed vs its own binomial null" rule: f=3-sized null
        (14/28 split, class t=35/p=19541) 3/96 half-tests over-dispersed
        (~3.1%); f=107-sized null (1/35 split, class t=-133/p=19373) 4/48
        half-tests over-dispersed (~8.3%, all in the n=35 half). Both rates
        are consistent with, and the second somewhat above, the ~5%
        false-positive rate expected from an uncorrected 95% band applied
        across many cells; a plain pooled (non-split-aware) statistic never
        fires on either null class. Reported as observed; not adjudicated as
        real effect vs multiple-testing noise -- that judgment is not the
        executor's to make.
    - rule: SR5_FLOOR_BEFORE_EFFECT
      outcome: UNREACHED
      detail: >-
        No per-level vertex counts exist to compute a floor from (see kernel
        rationality gap below); not fabricated from the matched-null's
        per-half floors, a different object.
    - rule: raw_per_level_count_data_collection
      outcome: UNREACHED
      detail: >-
        gcd(N, 3) = gcd(N, 107) = 1 (N=19507 prime; verified: N mod 3 = 1,
        N mod 107 = 33). By Lagrange's theorem E(F_p) has zero points of
        order 3 or 107 on every curve of both conductor-arm classes --
        verified empirically by exhaustive liftable-x scan (zero rational
        order-ell subgroups found on all 42 + 37 curves), not merely cited.
        Velu's formulas (as implemented here, and as available anywhere in
        this harness) need an explicit rational kernel point; none exists.
        Building the graph via a Galois-stable-but-not-pointwise-rational
        kernel needs field-extension arithmetic (harness.toycurve is F_p
        only) or a modular-polynomial root count (Phi_3, Phi_107, neither
        available); neither was attempted within this dispatch's budget
        rather than risk a silently wrong isogeny graph. Blocks: per-level
        vertex counts, the detection floor tied to them, T5 branch (i) and
        (ii), and the T1 transport certificate, for BOTH conductor-arm
        classes. All recorded UNREACHED, not imputed.
    - rule: SR6_INSTRUMENT_GATE
      outcome: >-
        NEVER APPROACHED (moot in this run). SR6 gates reading a LEVEL
        VERDICT computed from real per-level data; that data is itself
        UNREACHED for the prior, independent reason above, so SR6's own gate
        condition was never reached -- not satisfied, not bypassed.
        EXP-INSTR-36c8cf status as of dispatch (Phase A stopped at its own
        falsification criterion, no interval accepted; Phase B not run) is
        recorded verbatim and not read as discharging the gate.
    - rule: SR9_NO_OUTCOME_SHOPPING
      outcome: >-
        Honoured. The T5 verdict is recorded as UNREACHED, explicitly NOT as
        `neither` (which would misrepresent an unreached cell as a measured
        negative per falsification criterion F6). The level verdict is
        recorded WITHHELD with both independent reasons stated, not
        collapsed into a convenient single reason.
    - rule: SR10_BASELINE_PAUSE
      outcome: NOT_TRIGGERED
      detail: >-
        No level or crater/floor ratio was measured at all in this run
        (UNREACHED), so no ratio could appear to exceed the
        automorphism-discounted rho baseline; P3 was never approached.
  t5:
    reached: false
    gated_by_sr6: false
    reason: >-
      Blocked by the same graph-construction gap as the level arm (see
      raw_per_level_count_data_collection above), a reason independent of
      and unrelated to SR6. T5 heuristic HEUR-VOLC-1 is explicitly NOT gated
      by SR6 per the contract's heuristic_under_test_note (it is validated
      inside this experiment by C-LOCAL-EXHAUSTIVE, not by
      EXP-INSTR-36c8cf); it was computed to the extent reachable, which is
      not at all in this run.
    verdict: UNREACHED
  observations:
    - >-
      Frozen prediction reference: preregistered_prediction in
      experiments/EXP-VOLC-9f5571/specification.yaml, which predicts no
      direction/effect size for the level arm and states the identifiability
      ceiling exactly (level axis depth 1, f=107 crater has 1 vertex). No
      comparison against this prediction is reported: the per-level data it
      would be compared to is UNREACHED.
    - >-
      SR1 comparison statistic: observed level distribution
      {0:3,1:9,2:18,3:36,4:72} vs target {0:3,1:9,2:18,3:36,4:72} -- exact
      match, 0 unmatched Velu images out of 270 directed edges.
    - >-
      SR4 matched-null comparison statistics: per-cell own-null
      over-dispersion ratios and verdicts for both null instances, in
      matched-null-verdict.json; both plain pooled and per-half statistics
      reported side by side (see protocol_deviations / implementation.md
      sec 4 for the full breakdown), no tail check applicable (SR4 has no
      density-tail requirement of its own beyond the sweep already run).
    - >-
      Tail checks (contract tail_checks): WALK-LENGTH TAIL -- not applicable,
      no walk was reachable. CRATER TAIL -- not applicable, no per-vertex
      level assignment was reachable. LOCAL-TEST TAIL -- not applicable, no
      local-test values were computed. DENSITY TAIL -- reported: lowest
      (fb=4) and highest (fb=22) density rows are both present in
      per-vertex-measurements.json's cells alongside every intermediate row,
      for both conductor-arm classes. SUPPORT-CERTIFICATE TAIL -- reported:
      zero vertices with a non-exact support certificate, listed as an empty
      set (support-certificates.json, every record's support_equals_predicted
      is true).
  anomalies:
    - >-
      Two implementation defects found and repaired before reporting (SR4
      pooled-not-split-aware statistic; module-global SEEDS/TARGET_COUNTS not
      overridden, scoring 1 of 8 declared seeds). Full detail and the
      superseded run ids in implementation.md sec 2 and this run's
      SUPERSEDED.md files.
    - >-
      MID-RUN STRUCTURAL DISCOVERY (the dominant finding of this run): the
      matched-order family's defining choice of a PRIME group order N=19507
      makes gcd(N, ell) = 1 for every ell != N, so NO conductor-arm class in
      this family can ever have a pointwise-F_p-rational kernel point for its
      own conductor prime. This is not particular to ell=3 or ell=107 or to
      the classes chosen here -- it follows from N being prime, which the
      design document chose deliberately (MATCHED-ORDER-DESIGN.md sec 3).
      The level_construction method this contract specifies (Velu isogenies
      from rational ell-torsion) is therefore, as literally written, not
      executable on ANY conductor arm of this family without extending the
      toolkit to field-extension or modular-polynomial isogeny construction.
      Recommended next action: a protocol amendment choosing one of (a)
      extend to F_{p^2} (or higher) Velu arithmetic with an independently
      re-verifiable field-extension point-order test, (b) implement/obtain
      the classical modular polynomials Phi_3 and Phi_107 for edge-existence
      counting (does not by itself supply a T1-transportable kernel point),
      or (c) choose a matched-order family with composite N divisible by the
      intended conductor-arm primes.
    - >-
      SR4's f=107-sized null shows a modestly elevated (not dramatic)
      over-dispersed-half rate (~8.3% of 48 half-tests) vs the f=3-sized
      null's ~3.1% of 96; both are consistent with, though not conclusively
      distinguished from, uncorrected multiple-testing noise at a 95% band.
      Reported, not adjudicated.
  artifact_paths:
    - experiments/EXP-VOLC-9f5571/implementation.md
    - experiments/EXP-VOLC-9f5571/execution_report.md
    - experiments/EXP-VOLC-9f5571/runs/_source/volc_graph.py
    - experiments/EXP-VOLC-9f5571/runs/_source/volc_driver.py
    - experiments/EXP-VOLC-9f5571/runs/RUN-VOLC-sr1-sr5-plus-t5-gate-v3/manifest.yaml
    - experiments/EXP-VOLC-9f5571/runs/RUN-VOLC-sr1-sr5-plus-t5-gate-v3/command.txt
    - experiments/EXP-VOLC-9f5571/runs/RUN-VOLC-sr1-sr5-plus-t5-gate-v3/environment.json
    - experiments/EXP-VOLC-9f5571/runs/RUN-VOLC-sr1-sr5-plus-t5-gate-v3/stdout.log
    - experiments/EXP-VOLC-9f5571/runs/RUN-VOLC-sr1-sr5-plus-t5-gate-v3/stderr.log
    - experiments/EXP-VOLC-9f5571/runs/RUN-VOLC-sr1-sr5-plus-t5-gate-v3/raw-result.json
    - experiments/EXP-VOLC-9f5571/runs/RUN-VOLC-sr1-sr5-plus-t5-gate-v3/velu-gate-p4001.json
    - experiments/EXP-VOLC-9f5571/runs/RUN-VOLC-sr1-sr5-plus-t5-gate-v3/family-construction.json
    - experiments/EXP-VOLC-9f5571/runs/RUN-VOLC-sr1-sr5-plus-t5-gate-v3/class-census.json
    - experiments/EXP-VOLC-9f5571/runs/RUN-VOLC-sr1-sr5-plus-t5-gate-v3/volcano-graph.json
    - experiments/EXP-VOLC-9f5571/runs/RUN-VOLC-sr1-sr5-plus-t5-gate-v3/per-level-counts.json
    - experiments/EXP-VOLC-9f5571/runs/RUN-VOLC-sr1-sr5-plus-t5-gate-v3/detection-floors.json
    - experiments/EXP-VOLC-9f5571/runs/RUN-VOLC-sr1-sr5-plus-t5-gate-v3/matched-null-verdict.json
    - experiments/EXP-VOLC-9f5571/runs/RUN-VOLC-sr1-sr5-plus-t5-gate-v3/support-certificates.json
    - experiments/EXP-VOLC-9f5571/runs/RUN-VOLC-sr1-sr5-plus-t5-gate-v3/per-vertex-measurements.json
    - experiments/EXP-VOLC-9f5571/runs/RUN-VOLC-sr1-sr5-plus-t5-gate-v3/r-by-level-contingency.json
    - experiments/EXP-VOLC-9f5571/runs/RUN-VOLC-sr1-sr5-plus-t5-gate-v3/t5-walk-per-seed.json
    - experiments/EXP-VOLC-9f5571/runs/RUN-VOLC-sr1-sr5-plus-t5-gate-v3/t5-local-test.json
    - experiments/EXP-VOLC-9f5571/runs/RUN-VOLC-sr1-sr5-plus-t5-gate-v3/t5-verdict.json
    - experiments/EXP-VOLC-9f5571/runs/RUN-VOLC-sr1-sr5-plus-t5-gate-v3/transport-certificates.json
    - experiments/EXP-VOLC-9f5571/runs/RUN-VOLC-sr1-sr5-plus-t5-gate-v3/verdict.json
    - experiments/EXP-VOLC-9f5571/runs/RUN-VOLC-sr1-sr5-plus-t5-gate/SUPERSEDED.md
    - experiments/EXP-VOLC-9f5571/runs/RUN-VOLC-sr1-sr5-plus-t5-gate-v2/SUPERSEDED.md
  executor_assessment:
    protocol_complete: false
    protocol_complete_note: >-
      SR1-SR4 are complete with real measured numbers. SR5, raw per-level
      count collection, T5 (both branches and verdict) and the T1 transport
      certificate are UNREACHED, for a reason (gcd(N,ell)=1 across the whole
      family) that is structural to this family's design and not resolvable
      by rerunning this contract as written. The level verdict is separately
      WITHHELD by SR6. success_criterion items (2), (5), (6), (7)-partial
      (level verdict half) are therefore not met in this run; (1) partially
      (SR1-4 pass, SR5 unreached), (3) met, (4) met (with the one-row r
      caveat), (7)-partial (T5 verdict half: recorded as UNREACHED, a valid
      value distinct from the four the contract defines, per SR9).
    data_quality: limited
    data_quality_note: >-
      SR1-SR4 data is good (exact reproduction, full seed/density coverage,
      certified support). Overall marked limited because the contract's own
      primary deliverables (per-level counts, T5, transport) are UNREACHED.
    requires_rerun: false
    requires_rerun_note: >-
      Not by re-running this contract as written -- the blocking condition
      (gcd(N,ell)=1) is structural to the chosen family, not a transient
      failure. Requires a protocol amendment (see anomalies) before the
      graph-dependent portion can be attempted.
