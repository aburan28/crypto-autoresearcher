# Execution report -- EXP-JINV-bd141d

```yaml
execution_report:
  experiment_id: EXP-JINV-bd141d
  handoff_id: TASK-20260810-799ffa
  implementation_commit: a9028dcd1dd755419223854e060e2f8d3043bc30
  requested_policy: executor-implementation
  requested_policy_note: >-
    Requested by the handoff with fallback_allowed=false, degraded_allowed=false.
    This run is a deterministic Python computation (no model in the reasoning
    loop of the harness process itself); the executor SESSION that authored,
    reviewed and dispatched this code and report ran under the resolved
    Claude Code session policy for the `executor` role. No downgrade occurred:
    the session was not asked to and did not fall back to a different policy.
  protocol_deviations:
    - "D1: raw density-swept rate measurement (both arms) and SR4 could not
       be executed: the approved contract's inputs.density_grid never
       instantiates factor_base_sizes or a target count T (contrast the
       sibling contract EXP-ICINV-4d33aa, which lists both explicitly), and
       no experiments/EXP-JINV-bd141d/amendments/ exists to supply them.
       Reported as specification_error, not fabricated."
    - "D2: r-stratification collapses to a single populated stratum (r=0)
       for the entire matched-order family, a structural consequence of
       N=19507 being odd -- verified per curve on all 2,212 curves, not
       assumed."
    - "D3: C-TRANSPORT-CERT (T1 transport certificate, crater<->floor) is
       UNREACHED: gcd(107, 19507)=1 means no curve of trace t=211 carries an
       F_p-rational point of order 107, so the only ell-isogeny machinery in
       this codebase (isogeny_class.velu_odd / find_kernel_generator) cannot
       be invoked. No certificate fabricated."
    - "D4: harness/runner.py (pre-existing, out of write_scope) defines
       _inference_block() twice; the second definition shadows the first, so
       every run this wrapper writes records a hardcoded
       inference.requested_policy: executor-terra rather than resolving via
       the adapter. Recorded, not fixed (out of scope), and does not affect
       the correctness of any measured content (no model was in the run's
       execution loop either way)."
  runs:
    completed:
      - experiments/EXP-JINV-bd141d/runs/RUN-JINV-matched-n19507-e0451f
    invalid: []
    failed: []
  stopping_rules_fired_in_order:
    - rule: SR1
      outcome: PASS
      detail: >-
        Re-derived N=19507 family: 59 classes, 51 at f=1, 46 distinct |D_0|,
        5 hit twice (30067, 42307, 72403, 75427, 76003), |D_0| in
        [1299, 78027], conductor arm [1,3,107] -- EXACT match to the design
        document's expected_inventory. Aut-arm class (t=211, p=19717,
        D=-34347=-3*107^2) present and matches exactly.
    - rule: SR1-completeness-certificate
      outcome: PASS
      detail: >-
        Hurwitz-Kronecker weighted census agrees for all 59 classes
        (isogeny_class.class_census against the full per-p enumeration).
    - rule: SR2
      outcome: PASS
      detail: >-
        All 2,212 curves across all 59 classes: #E(F_p)=19507 verified by an
        independent point enumeration (square-root table method, no shared
        code with toycurve.lift_x) against the character-sum trace; targets_B
        support certified equal to E(F_p) per curve by explicit
        construction (N=19507 prime forces the cyclic table from any one
        point to equal the whole group, verified by set comparison against
        the independent enumeration on EVERY curve).
    - rule: C-TRANSPORT-CERT
      outcome: UNREACHED
      detail: >-
        gcd(107, 19507)=1: no curve of trace 211 has an F_p-rational point of
        order 107; find_kernel_generator's own precondition fails on every
        curve by construction. A genuine construction requires an
        extension-field kernel-polynomial isogeny not implemented in this
        codebase.
    - rule: SR4/data-collection
      outcome: BLOCKED
      detail: >-
        specification_error -- inputs.density_grid.factor_base_sizes and
        target_counts/n_targets are not instantiated anywhere in the approved
        contract; inventing them would be the SR5 violation the rule exists
        to prevent.
    - rule: SR3
      outcome: BLOCKING
      detail: >-
        EXP-INSTR-36c8cf has not delivered a two-directional detection floor
        / false-positive rate at this design's actual geometry (Phase A
        stopped at its own falsification criterion with no interval
        accepted; Phase B has not run). Reached second, after SR4/data-
        collection already blocked; independently sufficient to block either
        arm's verdict on its own.
  sr3_reached: true
  sr3_handling: >-
    Not read or reported: no TREND-DETECTED / NO-TREND / NOT-RESOLVABLE
    verdict was computed for either arm. verdict.json in the run directory
    records "BLOCKED_SR3_AND_SPEC_GAP" for both d0_arm and aut_arm, per SR7
    (the verdict is computed by the frozen rule inside the run, not selected
    afterward -- here the rule's output is "no verdict", stated as such, not
    withheld after being computed).
  sr8_pause_condition: >-
    NOT TRIGGERED and NOT APPLICABLE this run: no crater/floor rate ratio was
    computed (blocked by D1/SR4 above), so there is no ratio to compare
    against sqrt(6). Recorded for completeness, not because it fired.
  observations:
    - "Family re-derivation reproduces the design document's quoted
       inventory exactly on every one of 7 compared figures (classes_total,
       classes_at_f1, distinct_D0_at_f1, D0_hit_twice_count, abs_D0_min,
       abs_D0_max, conductor_arm) plus the aut-arm class's declared (p, D)."
    - "Every one of 2,212 curves in the re-derived family (all 59 classes,
       not only the 51 f=1 classes Arm 1 measures) independently verifies
       #E(F_p)=19507 and targets_B full-group support."
    - "r=0 identically across all 2,212 curves (structural: N odd forces
       trivial rational 2-torsion), verified not assumed."
    - "|Aut| arm: 37 vertices enumerated at t=211 (1 crater at j=0/aut=6,
       36 floor at aut=2), matching 1 + h(-3*107^2) = 1 + 36 = 37 exactly.
       This is the raw enumerated count, reported as data; SR3 blocks any
       rank or permutation-probability VERDICT built from it."
    - "The five |D_0| trace-pair members (structural t/p/D listing only,
       no rate data) are recorded in tracepair-replication.json."
  anomalies:
    - "specification_error: EXP-JINV-bd141d's approved, frozen contract does
       not instantiate a density grid (factor-base sizes) or target count,
       unlike its sibling contract EXP-ICINV-4d33aa. This blocks the raw
       measurement collection the handoff asked this run to attempt, ahead
       of and independent of SR3."
    - "implementation_gap: harness/isogeny_class.py's only ell-isogeny
       construction (velu_odd/find_kernel_generator) is structurally
       inapplicable to the crater/floor 107-isogeny this contract's
       C-TRANSPORT-CERT requires, because gcd(107, 19507)=1."
    - "pre-existing defect in harness/runner.py (out of write_scope, not
       fixed): duplicate module-level _inference_block() definition, second
       one shadowing the first, hardcodes inference.requested_policy in
       every run manifest this wrapper writes rather than resolving via the
       adapter."
  artifact_paths:
    - experiments/EXP-JINV-bd141d/runs/RUN-JINV-matched-n19507-e0451f/manifest.yaml
    - experiments/EXP-JINV-bd141d/runs/RUN-JINV-matched-n19507-e0451f/command.txt
    - experiments/EXP-JINV-bd141d/runs/RUN-JINV-matched-n19507-e0451f/environment.json
    - experiments/EXP-JINV-bd141d/runs/RUN-JINV-matched-n19507-e0451f/stdout.log
    - experiments/EXP-JINV-bd141d/runs/RUN-JINV-matched-n19507-e0451f/stderr.log
    - experiments/EXP-JINV-bd141d/runs/RUN-JINV-matched-n19507-e0451f/raw-result.json
    - experiments/EXP-JINV-bd141d/runs/RUN-JINV-matched-n19507-e0451f/family-construction.json
    - experiments/EXP-JINV-bd141d/runs/RUN-JINV-matched-n19507-e0451f/class-census.json
    - experiments/EXP-JINV-bd141d/runs/RUN-JINV-matched-n19507-e0451f/order-verification.json
    - experiments/EXP-JINV-bd141d/runs/RUN-JINV-matched-n19507-e0451f/support-certificates.json
    - experiments/EXP-JINV-bd141d/runs/RUN-JINV-matched-n19507-e0451f/per-curve-measurements.json
    - experiments/EXP-JINV-bd141d/runs/RUN-JINV-matched-n19507-e0451f/per-class-aggregates.json
    - experiments/EXP-JINV-bd141d/runs/RUN-JINV-matched-n19507-e0451f/d0-arm-analysis.json
    - experiments/EXP-JINV-bd141d/runs/RUN-JINV-matched-n19507-e0451f/tracepair-replication.json
    - experiments/EXP-JINV-bd141d/runs/RUN-JINV-matched-n19507-e0451f/residual-p-check.json
    - experiments/EXP-JINV-bd141d/runs/RUN-JINV-matched-n19507-e0451f/aut-arm-ranks.json
    - experiments/EXP-JINV-bd141d/runs/RUN-JINV-matched-n19507-e0451f/transport-certificates.json
    - experiments/EXP-JINV-bd141d/runs/RUN-JINV-matched-n19507-e0451f/baseline-provenance.json
    - experiments/EXP-JINV-bd141d/runs/RUN-JINV-matched-n19507-e0451f/verdict.json
    - experiments/EXP-JINV-bd141d/runs/RUN-JINV-matched-n19507-e0451f/r-stratification-finding.json
    - harness/exp_jinv_matched.py
    - harness/run_jinv_matched.py
    - experiments/EXP-JINV-bd141d/implementation.md
  executor_assessment:
    protocol_complete: false
    protocol_complete_note: >-
      SR1, the SR1 completeness certificate, and SR2 are fully discharged
      over the whole re-derived family. SR4 and the raw density-swept
      measurement collection for both arms are BLOCKED by a specification
      gap in the approved contract (missing density grid / target count),
      not executed and not fabricated. SR3 independently blocks any verdict
      even had that data existed. C-TRANSPORT-CERT is UNREACHED (a genuine
      implementation gap: no ell=107-rational point exists on this class).
      The contract's own success_criterion (both arms measured, both arms'
      controls discharged, one of three frozen verdicts per arm) is
      therefore NOT met -- this is reported as a bounded, honest terminal
      state per the handoff's framing, not as protocol completion.
    data_quality: limited
    data_quality_note: >-
      Everything reported (family re-derivation, Hurwitz-Kronecker census,
      per-curve order/support certificates, |Aut|-arm structural
      enumeration, r-structural finding) is exact, deterministic, and
      independently cross-checked. Nothing beyond that was collected.
    requires_rerun: true
    requires_rerun_note: >-
      A rerun of the density-swept measurement stage (Arm 1 and Arm 2 rate
      measurement, SR4, the rank/permutation statistics) requires a
      Coordinator-filed protocol_amendment instantiating
      inputs.density_grid.factor_base_sizes and a target count, filed BEFORE
      that data is generated (SR5). It also requires EXP-INSTR-36c8cf Phase B
      to deliver its two-directional detection floor before SR3 permits
      reading any resulting verdict. C-TRANSPORT-CERT requires a new
      ell-isogeny construction (kernel-polynomial / extension-field) not
      present in this codebase.
```
