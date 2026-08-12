def mean: add / length;

.[0] as $raw
| .[1] as $receipt
| .[2] as $manifest
| [
    $raw.instances[] as $instance
    | $instance.rows[]
    | select(.translator != null)
    | {
        bits: $instance.bits,
        seed: $instance.seed,
        factor_base_size: $instance.factor_base_size,
        family: .family,
        translator: .translator
      }
  ] as $translator_rows
| [
    $translator_rows[] as $row
    | ($row.translator.targets + $row.translator.matched_uniform_targets)[]
    | {
        family: $row.family,
        advice_ratio: $row.translator.preprocessing.advice_ratio_to_symmetry_d3,
        workspace_ratio: .gates.workspace_logical_ratio_to_symmetry_d3,
        online50_ratio: .gates.online_weighted_ratios_to_exact_d2_d3["50"],
        advice_gate: .gates.advice_gate,
        workspace_gate: .gates.workspace_gate,
        online_gate: .gates.online_gate,
        amortization_gate: .gates.amortization_within_b_gate
      }
  ] as $target_rows
| [
    $raw.instances[].rows[].floor.batches[]
    | select(.batch_scale == "B" or .batch_scale == "16B")
    | {
        scale: .batch_scale,
        clamped: .count_was_clamped,
        operation_gate: .comparison.deterministic_operation_signal_gate,
        inversion_ratio: .comparison.inversion_ratio,
        read_ratio: .comparison.d2_point_read_ratio,
        multiplication_ratio: .comparison.field_multiplication_ratio
      }
  ] as $batch_rows
| {
    protocol: $raw.protocol,
    claim_status: $raw.claim_status,
    configuration: $raw.configuration,
    evidence: {
      run_status: $manifest.status,
      run_commit: $manifest.git.commit,
      clean_prelog: $manifest.git.clean,
      source_hashes_stable: $manifest.source_hashes_stable,
      raw_sha256: $manifest.artifact_hashes["raw-result.json"],
      receipt_sha256: $manifest.artifact_hashes["verification-receipt.json"],
      manifest_wall_seconds: $manifest.overall_wall_seconds,
      process_child_max_rss_bytes: $manifest.overall_resource_usage.child_max_rss_after_bytes,
      timing_status: $receipt.timing_status
    },
    verification: {
      status: $receipt.status,
      instances: $receipt.verified_instances,
      families: $receipt.verified_families,
      factor_points: $receipt.verified_factor_points,
      d2_points: $receipt.verified_d2_points,
      d3_points: $receipt.verified_d3_points,
      translator_witnesses: $receipt.verified_translator_witnesses
    },
    decision: {
      translator_rows: ($translator_rows | length),
      functional_translator_rows: ($translator_rows | map(select(.translator.functional_gate)) | length),
      coordinate_continuation_rows: ($raw.aggregate.coordinate_continuation_rows | length),
      conjunctive_continuation_families: $raw.aggregate.conjunctive_continuation_families,
      promotion_rows: $raw.promotion_rows,
      batch_operation_signal_groups: ($raw.aggregate.conjunctive_batch_operation_signals | length),
      batch_practical_signal_groups: ($raw.aggregate.conjunctive_batch_practical_signals | length)
    },
    family_summaries: (
      $target_rows
      | group_by(.family)
      | map({
          family: .[0].family,
          target_rows: length,
          advice_ratio_min: (map(.advice_ratio) | min),
          advice_ratio_max: (map(.advice_ratio) | max),
          workspace_ratio_min: (map(.workspace_ratio) | min),
          workspace_ratio_max: (map(.workspace_ratio) | max),
          online50_null_ratios: (map(select(.online50_ratio == null)) | length),
          online50_numeric_min: (map(.online50_ratio) | map(select(. != null)) | min),
          online50_numeric_mean: (map(.online50_ratio) | map(select(. != null)) | mean),
          online50_numeric_max: (map(.online50_ratio) | map(select(. != null)) | max),
          advice_gate_passes: (map(select(.advice_gate)) | length),
          workspace_gate_passes: (map(select(.workspace_gate)) | length),
          online_gate_passes: (map(select(.online_gate)) | length),
          amortization_gate_passes: (map(select(.amortization_gate)) | length)
        })
    ),
    x_interval_same_map_null: [
      $translator_rows[]
      | select(.family == "x_interval")
      | {
          bits,
          seed,
          work50_ratio: .translator.matched_random_x.weighted_work_ratios["50"],
          density_ratio: .translator.matched_random_x.combined_g_density_ratio,
          support_not_worse: .translator.matched_random_x.support_not_worse,
          matched_gate: .translator.matched_random_x.matched_coordinate_gate
        }
    ],
    exploratory_slopes: $raw.aggregate.exploratory_slopes,
    trend_gates: $raw.aggregate.trend_gates,
    exact_batch_summary: (
      $batch_rows
      | map(select(.clamped | not))
      | group_by(.scale)
      | map({
          scale: .[0].scale,
          exact_rows: length,
          operation_gate_passes: (map(select(.operation_gate)) | length),
          mean_inversion_ratio: (map(.inversion_ratio) | mean),
          mean_d2_read_ratio: (map(.read_ratio) | mean),
          mean_multiplication_ratio: (map(.multiplication_ratio) | mean)
        })
    ),
    clamped_16b_rows: (
      $batch_rows
      | map(select(.scale == "16B" and .clamped))
      | length
    ),
    boundary: $raw.boundary
  }
