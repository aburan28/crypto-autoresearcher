# VAL-BATCH-012 — Independent Validation of RUN-SSIQ-a85692-i

```yaml
validation_report:
  id: VAL-20260806-b8fdf8
  task_id: TASK-20260806-b8fdf8
  run_ids:
    - RUN-SSIQ-a85692-i
  snapshot_verified:
    commit_sha: 1aa1c37f6bee07b32fe8bd9553ef438418222638
    parent_sha_expected: d729af05328f7e40fe466f4e4d473298e246db8f
    parent_sha_actual: d729af05328f7e40fe466f4e4d473298e246db8f
    commit_reachable_from_HEAD: true
    HEAD_at_time_of_review: 1aa1c37f6bee07b32fe8bd9553ef438418222638
    note: >-
      Read only the committed snapshot at 1aa1c37f (git log/merge-base
      independently checked, not taken from the receipt's own prose). This
      is a Coordinator-committed snapshot, not a working-tree-only receipt.

  artifact_checks:
    - check: declared_paths_exist_and_parse
      result: PASS
      detail: >-
        All 10 declared artifacts present under RUN-SSIQ-a85692-i and the
        one new implementation file; raw-result.json and
        truncation_probe_comparison.json parse as valid JSON.
    - check: path_sha256_independent_recomputation
      result: PASS
      detail: >-
        Independently recomputed SHA-256 of all 10 declared paths from the
        current working tree (which `git diff 1aa1c37f -- <path>` confirms
        is byte-identical to the committed blob at 1aa1c37f for every
        artifact path) and compared against every value in the receipt's
        path_sha256 map: 10/10 exact matches, byte for byte. No mismatch.
    - check: commit_chain
      result: PASS
      detail: >-
        `git log --oneline` confirms 1aa1c37f's parent is exactly d729af05
        (the commit that froze specification_v9.yaml), matching both the
        receipt's parent_sha and manifest.yaml's code.commit /
        execution_report.yaml's implementation_commit. 1aa1c37f is an
        ancestor of the current repository HEAD (merge-base --is-ancestor
        confirms). commit_sha_note's "null by construction" explanation
        (the receipt is committed inside the commit it describes) is
        consistent with the file being one of the 11 files changed in
        1aa1c37f's own diff --stat against its parent, which I verified
        directly.
    - check: prior_amendments_untouched
      result: PASS
      detail: >-
        `git diff --stat d729af05 -- specification.yaml specification_v2..v8.yaml
        runs/RUN-SSIQ-a85692-{a..h}` reproduced empty by this Validator
        independently (not merely trusted from the receipt).
    - check: write_scope_respected
      result: PASS
      detail: >-
        Exactly one new implementation file and one new run directory were
        added in 1aa1c37f (`git diff --stat` shows 11 changed files total:
        the receipt itself, the new .py, and 9 run artifacts under
        RUN-SSIQ-a85692-i/); nothing else changed.

  frozen_contract_conformance_checks:
    - check: base_seed_and_seed_formula_genuinely_imported
      result: PASS
      detail: >-
        delta_e_truncation_probe_v9.py imports
        delta_e_independent_rng_probe_v8 as v8probe (unedited file, `git
        diff --stat HEAD` confirms zero changes to that file across this
        and all prior amendments) and calls
        v8probe.derive_per_vertex_seed(base_seed, v) directly -- no local
        redefinition of that function exists anywhere in the new file
        (grepped). BASE_SEED = 20260811 is a literal constant in the new
        file, identical to v8probe's own BASE_SEED = 20260811 (grepped in
        delta_e_independent_rng_probe_v8.py line 119). Confirms the
        amendment's own stated design (isolate budget-truncation as the
        sole manipulated variable) is genuinely implemented, not merely
        claimed.
    - check: per_vertex_budget_fixed_constant
      result: PASS
      detail: >-
        PER_VERTEX_BUDGET_SECONDS = 0.5 is a literal module-level constant,
        passed unchanged into every two_sided_search call inside the
        per-vertex loop; never a function of elapsed/remaining time
        (confirmed by direct read of run_truncation_probe_v9's loop body).
    - check: fp_rational_wiring_before_search_loop
      result: PASS
      detail: >-
        run_truncation_probe_v9 (lines 162-166) constructs new_delta_map[v]
        = 1 for all F_p-rational vertices in a loop that completes strictly
        before the non-F_p-rational search loop (lines 168-196) begins.
        Matches v8's own PF-9 construction exactly.
    - check: comparison_1_source_and_function
      result: PASS
      detail: >-
        compare_against_archived is called with archived_delta_map loaded
        via `tdv5.load_archived_prime_data(args.raw_result_b, PRIME)`
        (GENUINELY IMPORTED, UNCHANGED), args.raw_result_b defaulting to
        RUN-SSIQ-a85692-b/raw-result.json exactly as the frozen contract
        requires.
    - check: comparison_2_source_and_parsing_helper
      result: PASS
      detail: >-
        parse_v8_new_delta_map(path) reads
        RUN-SSIQ-a85692-h/probe_delta_e_comparison.json (NOT raw-result.json
        -- confirmed the default --run-h-comparison argument points to the
        correct file), reads its top-level new_delta_map field directly
        (not nested under phase_minus1_real_search, matching the PF-1 fix),
        applies tuple(json.loads(key_str)) per key, and performs the exact
        collision/injectivity check (len(parsed) != len(raw) -> raise)
        the frozen contract specifies. Independently confirmed by direct
        Python execution against the real RUN-SSIQ-a85692-h file: 203 raw
        string keys -> 203 distinct parsed tuples, zero collisions.
    - check: pf5_write_order_and_failure_isolation_genuinely_implemented
      result: PASS
      detail: >-
        Static check: part_a_result and comparison_1 are computed in a
        code block (lines 479-511) that completes before Comparison 2's
        try/except block (lines 519-538) begins, and both are placed into
        comparison_payload/raw_result_payload independent of Comparison 2's
        outcome. DYNAMIC check (this Validator does not accept static
        tracing alone for a claimed failure-isolation property): I invoked
        the frozen, unmodified delta_e_truncation_probe_v9.py directly with
        `--run-h-comparison /nonexistent/path/does-not-exist.json` (a
        scratch-directory rerun, no frozen artifact touched) to force a
        genuine FileNotFoundError inside Comparison 2. Result: exit code 0,
        part_a_summary and comparison_1_against_archived_summary were both
        written intact with real, non-null values (n_resolved=8,
        n_timed_out=194, n_value_differs_vs_archived=0), comparison_2_against_v8_summary
        was null, and comparison_2_error captured the exact exception
        string ("FileNotFoundError: [Errno 2] No such file or directory:
        ..."). PF-5's failure-isolation discipline is genuinely functional,
        not merely dormant/structurally-present code.
    - check: no_part_b_no_permutation_null_control_this_amendment
      result: PASS
      detail: >-
        Grepped for depth0_fraction, summary_stats,
        run_probe_permutation_null_control_v8,
        run_probe_delta_e_search_v8, run_phase_minus1_on_confirmatory_set:
        none appear in executable code, only in docstring/comments
        disclaiming their use. Matches the frozen contract's explicit
        amendment_scope (PART A only).

  reexecution_c_repro:
    performed: true
    method: >-
      Ran the exact recorded command
      (`ulimit -v 2097152; timeout 600 python3
      experiments/EXP-SSIQ-a85692/implementation/delta_e_truncation_probe_v9.py
      --run-dir <clean scratch dir>`) from a clean scratch output directory
      at the current repository HEAD (1aa1c37f, one commit ahead of the
      run's own recorded code.commit d729af05 -- the intervening commit
      only added this run's own already-frozen artifacts, so it does not
      affect the executed code), against the same unmodified implementation
      file and the same read-only RUN-b/RUN-h source artifacts. Real
      wall-clock: 102.1s.
    result:
      graph_identity_verification: "PASS (n_built=203, degseq_pass=True) -- identical to archived run"
      n_timed_out: "194/194 -- identical to archived run"
      n_resolved: "10 (archived run: 8) -- DIFFERS, as PF-3 discloses is expected"
      coverage_fraction: "0.05155 (archived run: 0.04124) -- DIFFERS, consistent with PF-3"
      n_value_differs_vs_archived: "0 (over 19 resolved vertices this rerun) -- matches structural finding"
      n_value_differs_vs_v8: "0 (over the same 19 vertices) -- matches structural finding"
      comparison_2_error: "null -- matches"
    assessment: >-
      This is EXPECTED non-reproducibility, not a red flag, exactly as the
      frozen contract's own PF-3 finding discloses: PER_VERTEX_BUDGET_SECONDS
      is a real-time wall-clock cutoff, and which vertices resolve vs. time
      out depends on real machine speed/load even with byte-identical RNG
      draws. The PARSING/COMPARISON LOGIC (the part that is not
      timing-dependent) reproduces correctly: 194/194 timeouts,
      comparison_2_error null, and — most importantly for this amendment's
      own diagnostic purpose — n_value_differs stayed at exactly 0 in BOTH
      the archived run (8 resolved) and my independent rerun (10 resolved),
      strengthening rather than merely repeating the reported finding.
      Reported accurately per instruction, not fabricated.

  metric_recomputations:
    - metric: n_resolved / n_timed_out / coverage_fraction
      method: >-
        Loaded truncation_probe_comparison.json's own per_vertex_records
        (194 entries) directly, independently counted resolved==true
        (8) and timed_out==true (194), recomputed coverage_fraction =
        8/194.
      result: "n_resolved=8, n_timed_out=194, coverage_fraction=0.041237113402061855 -- EXACT MATCH to reported values"
      additional_finding: >-
        All 8 resolved vertices ALSO have timed_out=true (both search
        halves hit the 0.5s soft cap even on the 8 that found a collision
        from a partial table before the cutoff) -- confirms the manifest's
        own explanation and that "resolved" and "timed_out" are not
        mutually exclusive fields in this design.
    - metric: n_value_differs_vs_archived (Comparison 1)
      method: >-
        Independently loaded RUN-SSIQ-a85692-b's own delta_map directly
        from its raw-result.json (phase_minus1_real_search["2437"]["delta_map"],
        203 entries), independently parsed this run's own 17-entry
        new_delta_map from truncation_probe_comparison.json via
        tuple(json.loads(key)), and diffed key-by-key with a
        from-scratch script (not reusing the Executor's or Coordinator's
        comparison code).
      result: "17/17 keys present in archived map, 0/17 value differences -- CONFIRMS reported n_value_differs_vs_archived=0"
    - metric: n_value_differs_vs_v8 (Comparison 2)
      method: >-
        Independently loaded RUN-SSIQ-a85692-h's own new_delta_map directly
        from its probe_delta_e_comparison.json (203 entries, same
        tuple(json.loads(key)) parsing convention), diffed key-by-key
        against this run's own 17-entry new_delta_map.
      result: "17/17 keys present in v8's map, 0/17 value differences -- CONFIRMS reported n_value_differs_vs_v8=0"
      value_breakdown: >-
        9 vertices at value=1 (F_p-rational, unconditionally wired) + 8
        vertices at value=2 (all 8 resolved non-F_p-rational vertices
        resolved at the smallest possible non-trivial delta_e value,
        consistent with two_sided_search's best-first design finding
        small-degree collisions fastest).
    - metric: comparison_2_error null and reachability of its code path
      method: >-
        Confirmed field present and null by direct inspection of both
        raw-result.json and truncation_probe_comparison.json (not merely
        trusting the field's presence). Confirmed the guarding try/except
        is reachable and functions correctly by the dynamic PF-5 test above
        (forced FileNotFoundError, observed correct capture).
      result: "CONFIRMED genuinely null (path not exercised on a failure this run) AND confirmed functional when exercised."
    - metric: graph_identity_reverification
      method: >-
        Read graph_identity_verification block directly from both
        raw-result.json and truncation_probe_comparison.json.
      result: "n_built_vertices=203, degree_sequence_check.pass=true (n_degree_ne_3=0), vertex_count_match=true against archived n_vertices=203 -- MATCHES"

  control_checks:
    - control: negative/null-object control (permutation-null, PART B)
      result: NOT_APPLICABLE_THIS_RUN_BY_DESIGN
      detail: >-
        This amendment's frozen amendment_scope explicitly and deliberately
        excludes PART B (the permutation-null control) from this run's own
        scope, for a stated, previously-reviewed reason (a partial-coverage
        delta_map has no principled domain for depth0_fraction, which has
        no existence guard and would either require an ad-hoc restriction
        or reproduce v8's own PF-1/PF-9 crash). This is not a missing
        control silently omitted -- it is a scoped-out control with a
        named, reviewed reason, and the run does not claim a correlation,
        bias, or excess that would require a null-object baseline of its
        own. The relevant null-object comparison for THIS diagnostic's
        actual claim shape (does truncation reopen a value-difference
        channel) is the two REQUIRED COMPARISONS themselves (archived
        shared-RNG baseline; v8's own non-truncated probe), both of which
        this Validator independently recomputed above. No violation of the
        "controls before belief" rule is found for this specific,
        narrowly-scoped run; whether the broader multi-run picture (this
        run + v8's PART B) still needs a null object under severe
        truncation is a Coordinator-level interpretive question, not
        something this run's own artifacts are silent about.
    - control: positive control (graph-identity re-verification against
        archived ground truth)
      result: PASS
      detail: "See graph_identity_reverification recomputation above."

  statistical_power_assessment:
    finding: >-
      The frozen contract's own text anticipated "some or most" of 194
      vertices resolving; the actual result was 8/194 (4.12%), and my own
      independent rerun got 10/194 (5.15%) -- both far below "some or
      most." This materially changes what "0 value differences" can
      support. Using the exact Clopper-Pearson one-sided 95% upper
      confidence bound for a Bernoulli differencing-rate parameter with
      zero observed successes in n trials (1 - 0.025^(1/n)):
        - n=8 (archived run): upper bound = 36.9%
        - n=10 (my independent rerun): upper bound = 30.8%
      That is: an underlying per-vertex probability of a truncation-induced
      value difference as high as roughly one-in-three is still fully
      consistent with the observed "0/8" (or "0/10") result at 95%
      confidence. This is NOT the same statistical situation as v8's own
      full-coverage "0/203" comparison (which RT-BATCH-011 showed was
      near-certain for a structural reason, not a sample-size reason): here
      the small sample size ITSELF, not only the completed-search
      determinism argument, limits what "zero differences" can rule out.
      The run's own execution_report.yaml (ANOM-2) discloses this
      qualitatively ("this comparison's own statistical power is
      correspondingly small") -- this Validator's independent
      quantification (Clopper-Pearson bound ~31-37%) confirms that
      disclosure is not an understatement and should be read as a material
      caveat, not a footnote, whenever this run's "0 value differences" is
      cited.
    scope: >-
      This is a validity/power assessment of what the evidence can support,
      not an execution-fidelity finding -- the run's own numbers are
      confirmed correct (see metric_recomputations above); their
      informativeness for the truncation-boundary question is what is
      limited.

  heuristic_validation_checks: []
  cost_model_checks: []
  proof_architecture_checks: []

  scope_boundary_check:
    result: PASS
    detail: >-
      raw-result.json's objective_boundary and scale_qualifier fields, and
      execution_report.yaml's disclosed_interpretations/observations/
      anomalies, all correctly avoid asserting a PERSISTS/WEAKENS label or
      any claim about H-SSIQ-36e970, PF-6, or lever L4, consistent with the
      frozen contract's explicit OBJECTIVE_BOUNDARY. certificate.kind:
      none is correctly declared and justified per
      docs/claims-and-verification.md (no discrete-log solve or
      factor-base relation is claimed). This Validator likewise draws no
      conclusion about PF-6/H-SSIQ-36e970/lever L4 in this report, per its
      own task scope.

  minor_observations_non_blocking:
    - observation: >-
        specification_v9.yaml's own top-of-file comment still reads "DRAFT
        PROTOCOL AMENDMENT, NOT YET FROZEN" even though the YAML body below
        it states status: approved and frozen_at: '2026-08-06'. This
        appears to be a standing convention in this experiment lineage
        (specification_v8.yaml's top comment makes the identical "NOT YET
        FROZEN" claim about itself relative to v7, and was left unedited
        after v8's own freeze too) rather than a v9-specific defect, but it
        is worth the Coordinator flagging for correction in a future
        amendment since a header claiming "not yet frozen" on a frozen,
        approved, executed-against contract is confusing on a cold read.
        Does not affect this report's verdict: the frozen_at/status/
        pre_freeze_review fields (which govern) are internally consistent
        and match the commit history and executed code.

  verdict: passed
  verdict_rationale: >-
    Every artifact-presence, hash-integrity, commit-chain, write-scope, and
    frozen-contract-conformance check independently re-verified PASS. All
    headline numeric claims (n_resolved=8, n_timed_out=194,
    coverage_fraction=8/194, n_value_differs_vs_archived=0,
    n_value_differs_vs_v8=0, comparison_2_error=null, graph_identity
    pass=true/n=203) were recomputed from raw JSON by this Validator using
    fresh, from-scratch parsing code and matched exactly. PF-5's
    failure-isolation discipline was confirmed not just structurally
    present but dynamically functional via a deliberately induced failure
    against the unmodified frozen implementation. Independent
    re-execution reproduced the timing-sensitive vertex-level outcome
    differently (10 vs 8 resolved) exactly as PF-3 discloses is expected,
    while reproducing every non-timing-dependent structural result
    (194/194 timeouts, 0/0 value differences on both comparisons,
    comparison_2_error null) -- this is treated as confirming, not
    undermining, reproducibility of the governing logic. The receipt is
    admissible evidence of a genuinely executed, contract-conformant run.
    This verdict says nothing about what the measured relationship means
    for PF-6, H-SSIQ-36e970, or lever L4 (Coordinator's and Red Team's
    job), and the report separately flags -- as a required, non-blocking
    limitation, not a defect -- that the small resolved-sample size (n=8,
    or n=10 on independent rerun) gives "0 value differences" a wide
    statistical margin (Clopper-Pearson 95% upper bound on the true
    differencing rate: ~31-37%), which materially bounds how strongly this
    specific run's finding can be cited on its own.

  limitations:
    - >-
      Toy scale only: single prime p=2437 (N=203 vertices, log2(p)=11.25).
      No result transfers to cryptographic scale; the frozen contract's own
      scale_qualifier states this and this Validator did not need to add
      anything beyond confirming that disclosure is present and accurate.
    - >-
      Small resolved-sample statistical power: n=8 non-F_p-rational
      vertices resolved under forced truncation (n=10 in this Validator's
      own independent rerun); "0 value differences" over this sample size
      is consistent with an underlying differencing rate up to
      approximately 31-37% at 95% confidence (exact Clopper-Pearson upper
      bound), a materially wide margin. See statistical_power_assessment.
    - >-
      PF-3's disclosed hardware/timing non-determinism means the exact
      n_resolved/n_timed_out split is not bit-for-bit reproducible across
      machines even with identical RNG seeds; this Validator's own rerun
      (10/194 resolved) differs from the archived run's (8/194) for this
      reason, confirmed to be the expected cause rather than a defect.
    - >-
      This run carries no null-object (permutation) control of its own by
      explicit, previously-reviewed design (NO PART B); see control_checks
      above for why this is a scoped design choice, not an omission, for
      this run's specific claim shape.
    - >-
      This report validates execution integrity and numeric correctness
      only. It does not evaluate, and explicitly declines to evaluate, what
      this run's result means for PF-6's RNG-sharing hypothesis,
      H-SSIQ-36e970, or lever L4 -- that synthesis is reserved for the
      Coordinator's decision record, informed by this report and the
      parallel Red Team review.

  artifact_paths:
    - experiments/EXP-SSIQ-a85692/specification_v9.yaml
    - experiments/EXP-SSIQ-a85692/implementation/delta_e_truncation_probe_v9.py
    - experiments/EXP-SSIQ-a85692/implementation/delta_e_independent_rng_probe_v8.py
    - experiments/EXP-SSIQ-a85692/runs/RUN-SSIQ-a85692-i/manifest.yaml
    - experiments/EXP-SSIQ-a85692/runs/RUN-SSIQ-a85692-i/raw-result.json
    - experiments/EXP-SSIQ-a85692/runs/RUN-SSIQ-a85692-i/execution_report.yaml
    - experiments/EXP-SSIQ-a85692/runs/RUN-SSIQ-a85692-i/source_access_log.yaml
    - experiments/EXP-SSIQ-a85692/runs/RUN-SSIQ-a85692-i/command.txt
    - experiments/EXP-SSIQ-a85692/runs/RUN-SSIQ-a85692-i/environment.json
    - experiments/EXP-SSIQ-a85692/runs/RUN-SSIQ-a85692-i/stdout.log
    - experiments/EXP-SSIQ-a85692/runs/RUN-SSIQ-a85692-i/stderr.log
    - experiments/EXP-SSIQ-a85692/runs/RUN-SSIQ-a85692-i/truncation_probe_comparison.json
    - experiments/EXP-SSIQ-a85692/runs/RUN-SSIQ-a85692-b/raw-result.json
    - experiments/EXP-SSIQ-a85692/runs/RUN-SSIQ-a85692-h/probe_delta_e_comparison.json
    - coordination/goals/GOAL-SSIQ-001/batches/BATCH-012/archives/TASK-20260806-164c92-receipt.yaml
```
