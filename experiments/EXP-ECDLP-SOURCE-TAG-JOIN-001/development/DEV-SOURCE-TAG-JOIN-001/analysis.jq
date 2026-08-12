def stats:
  sort as $values
  | {
      min: $values[0],
      median: $values[(($values | length) / 2 | floor)],
      max: $values[-1]
    };

def worst_ratio($row; $key):
  [$row.ratios_to_matched_nulls[][$key]] | max;

def metric_summary($rows; $key; $threshold):
  [$rows[] | worst_ratio(.; $key)] as $values
  | {
      metric: $key,
      threshold: $threshold,
      pass_count: [$values[] | select(. <= $threshold)] | length,
      worst_null_ratio: ($values | stats)
    };

def candidate_digest:
  {
    bits: .curve_bits,
    curve_id: .curve_id,
    family,
    witness_policy,
    source_tag,
    tag_count,
    output_router,
    saturated: .advice.route_universe_saturated,
    route_triples: .advice.distinct_route_triples,
    min_null_movement:
      ([.ratios_to_matched_nulls[].null_moved_fraction] | min),
    worst_d4_group:
      ([.ratios_to_matched_nulls[].supported_d4_group_operations] | max),
    mean_d4_group:
      ([.ratios_to_matched_nulls[].supported_d4_group_operations]
       | add / length),
    worst_d5_group:
      ([.ratios_to_matched_nulls[].supported_d5_group_operations] | max),
    worst_random_d5_group:
      ([.ratios_to_matched_nulls[].random_d5_group_operations] | max),
    query_st2_ratio:
      .d2_complement_comparison.candidate_to_d2_query_st2_diagnostic_ratio,
    hybrid_d5_group_ratio:
      .partial_d4_comparison
      .candidate_to_hybrid_supported_d5_group_operation_ratio
  };

.[0] as $document
| .[1] as $certificate
| [
    $document.instances[] as $instance
    | $instance.families[] as $family
    | $family.rows[]
    | select(.variant_kind == "candidate")
    | . + {
        curve_bits: $instance.curve.bits,
        curve_id: $instance.curve.id,
        family: $family.family
      }
  ] as $candidates
| [
    $candidates[]
    | . as $row
    | (if .tag_count == 4 then 2
       elif .tag_count == 8 then 3
       else 4
       end) as $tag_bits
    | (.advice.payload_bit_lower_estimate
       - .advice.distinct_route_triples * 3 * $tag_bits) as $shared_bits
    | {
        tag_count,
        best_possible_worst_payload_ratio:
          ([
            .ratios_to_matched_nulls[]
            | $shared_bits
              / ($row.advice.payload_bit_lower_estimate / .payload_bits)
          ] | max)
      }
  ] as $payload_capabilities
| [
    $document.exploratory_slopes[]
    | select(.variant_kind == "candidate" and .route_slope_eligible)
  ] as $eligible_slopes
| {
    protocol: $document.protocol,
    development_only: $document.development_only,
    verification: {
      status: $certificate.status,
      input_file_sha256: $certificate.input_file_sha256,
      canonical_document_sha256: $certificate.canonical_document_sha256,
      verified_instances: $certificate.verified_instances,
      verified_families: $certificate.verified_families,
      verified_rows: $certificate.verified_rows,
      verified_matched_nulls: $certificate.verified_matched_nulls,
      verified_factor_witnesses: $certificate.verified_factor_witnesses
    },
    promotion: {
      configured_seed_count: $document.routing_summary.configured_seed_count,
      required_passing_seeds_per_size:
        $document.routing_summary.required_passing_seeds_per_size,
      routing_rows: ($document.routing_rows | length),
      compiler_rows: ($document.compiler_rows | length)
    },
    candidate_gate_counts: {
      total: ($candidates | length),
      source_signal:
        ([$candidates[] | select(.source_signal_gate_passed)] | length),
      compiler: ([$candidates[] | select(.compiler_gate_passed)] | length),
      routing: ([$candidates[] | select(.routing_gate_passed)] | length),
      instance_signal:
        ([$candidates[] | select(.instance_signal_gate_passed)] | length)
    },
    candidate_prerequisites: {
      null_invariants:
        ([$candidates[] | select(.null_invariants_passed)] | length),
      scalar_calibration:
        ([$candidates[] | select(.scalar_calibration_passed)] | length),
      all_nulls_moved_at_least_half:
        ([
          $candidates[]
          | select(all(.ratios_to_matched_nulls[];
                       .null_moved_fraction >= 0.5))
        ] | length),
      nonsaturated:
        ([
          $candidates[]
          | select(.advice.route_universe_saturated | not)
        ] | length),
      descent_solved_and_verified:
        ([
          $candidates[]
          | select(.descent.all_challenges_solved and .descent.all_verified)
        ] | length)
    },
    matched_null_metrics: [
      metric_summary($candidates; "payload_bits"; 0.8),
      metric_summary($candidates; "route_triples"; 0.8),
      metric_summary($candidates; "supported_d4_point_reads"; 0.8),
      metric_summary($candidates; "supported_d4_group_operations"; 0.8),
      metric_summary($candidates; "supported_d5_point_reads"; 0.8),
      metric_summary($candidates; "supported_d5_group_operations"; 0.8),
      metric_summary($candidates; "random_d5_point_reads"; 0.8),
      metric_summary($candidates; "random_d5_group_operations"; 0.8),
      metric_summary($candidates; "canonical_serialized_bytes"; 1.25),
      metric_summary($candidates; "python_deep_bytes"; 1.25)
    ],
    payload_gate_diagnostic: {
      model:
        "remove every candidate route bit while retaining shared factor/D2 payload",
      capable_of_0_8_even_with_zero_routes:
        ([
          $payload_capabilities[]
          | select(.best_possible_worst_payload_ratio <= 0.8)
        ] | length),
      by_tag_count:
        ($payload_capabilities
         | group_by(.tag_count)
         | map(
             . as $rows
             | {
                 tag_count: $rows[0].tag_count,
                 rows: ($rows | length),
                 capable:
                   ([
                     $rows[]
                     | select(.best_possible_worst_payload_ratio <= 0.8)
                   ] | length),
                 lower_bound:
                   ([$rows[].best_possible_worst_payload_ratio] | stats)
               }
           )),
      interpretation:
        "tag_count=4 cannot pass the total-payload threshold even with zero routes; tag_count=8/16 can in principle, but observed route payload did not separate from matched nulls"
    },
    compiler_components: {
      query_st2_at_most_0_8:
        ([
          $candidates[]
          | select(.d2_complement_comparison
                   .candidate_to_d2_query_st2_diagnostic_ratio <= 0.8)
        ] | length),
      descent_st2_at_most_0_8:
        ([
          $candidates[]
          | select(.d2_complement_comparison
                   .candidate_to_d2_descent_st2_diagnostic_ratio <= 0.8)
        ] | length),
      partial_query_better:
        ([
          $candidates[]
          | select(.partial_d4_comparison
                   .candidate_query_beats_hybrid_using_no_more_advice)
        ] | length),
      partial_descent_better:
        ([
          $candidates[]
          | select(.partial_d4_comparison
                   .candidate_descent_beats_hybrid_using_no_more_advice)
        ] | length),
      decomposition_envelope_better:
        ([
          $candidates[]
          | select(.decomposition_envelope.candidate_to_envelope_ratio < 1)
        ] | length),
      dlp_envelope_better:
        ([
          $candidates[]
          | select(.dlp_envelope.candidate_to_envelope_ratio < 1)
        ] | length)
    },
    by_bits:
      ($candidates
       | group_by(.curve_bits)
       | map(
           . as $rows
           | {
               bits: $rows[0].curve_bits,
               rows: ($rows | length),
               saturation_count:
                 ([$rows[] | select(.advice.route_universe_saturated)] | length),
               movement_and_saturation_eligible:
                 ([
                   $rows[]
                   | select(
                       (.advice.route_universe_saturated | not)
                       and all(.ratios_to_matched_nulls[];
                               .null_moved_fraction >= 0.5)
                     )
                 ] | length),
               best_worst_d4_group:
                 ([$rows[] | worst_ratio(.; "supported_d4_group_operations")]
                  | min),
               median_worst_d4_group:
                 ([$rows[] | worst_ratio(.; "supported_d4_group_operations")]
                  | stats | .median),
               best_worst_d5_group:
                 ([$rows[] | worst_ratio(.; "supported_d5_group_operations")]
                  | min),
               median_worst_d5_group:
                 ([$rows[] | worst_ratio(.; "supported_d5_group_operations")]
                  | stats | .median),
               best_worst_random_d5_group:
                 ([$rows[] | worst_ratio(.; "random_d5_group_operations")]
                  | min),
               median_worst_random_d5_group:
                 ([$rows[] | worst_ratio(.; "random_d5_group_operations")]
                  | stats | .median),
               minimum_query_st2_ratio:
                 ([$rows[].d2_complement_comparison
                    .candidate_to_d2_query_st2_diagnostic_ratio] | min),
               median_query_st2_ratio:
                 ([$rows[].d2_complement_comparison
                    .candidate_to_d2_query_st2_diagnostic_ratio]
                  | stats | .median),
               minimum_hybrid_d5_group_ratio:
                 ([$rows[].partial_d4_comparison
                    .candidate_to_hybrid_supported_d5_group_operation_ratio]
                  | min),
               median_hybrid_d5_group_ratio:
                 ([$rows[].partial_d4_comparison
                    .candidate_to_hybrid_supported_d5_group_operation_ratio]
                  | stats | .median)
               ,
               minimum_materialized_d5_group_ratio:
                 ([$rows[].materialized_comparison
                    .candidate_to_materialized_supported_d5_group_operation_ratio]
                  | min),
               median_materialized_d5_group_ratio:
                 ([$rows[].materialized_comparison
                    .candidate_to_materialized_supported_d5_group_operation_ratio]
                  | stats | .median),
               zero_average_bsgs_rows:
                 ([
                   $rows[]
                   | select(.matched_bsgs.average_online_group_operations == 0)
                 ] | length)
             }
         )),
    diagnostic_slopes: {
      eligible_candidate_rows: ($eligible_slopes | length),
      supported_d5_group_operations:
        ([$eligible_slopes[].supported_d5_group_operations] | stats),
      supported_d5_below_0_5:
        ([
          $eligible_slopes[]
          | select(.supported_d5_group_operations < 0.5)
        ] | length),
      subhalf_rows:
        ([
          $eligible_slopes[]
          | select(.supported_d5_group_operations < 0.5)
          | {
              family,
              witness_policy,
              source_tag,
              tag_count,
              supported_d5_group_operations
            }
        ]),
      payload_bits: ([$eligible_slopes[].payload_bits] | stats),
      route_triples: ([$eligible_slopes[].route_triples] | stats)
    },
    rho_comparison_by_bits:
      ($candidates
       | group_by(.curve_bits)
       | map(
           . as $rows
           | {
               bits: $rows[0].curve_bits,
               candidate_to_rho_average_group_operations:
                 ([$rows[].rho_comparison
                    .candidate_descent_to_rho_average_group_operation_ratio]
                  | stats),
               candidate_to_bsgs_worst_case_group_operations:
                 ([$rows[].matched_bsgs
                    .candidate_to_bsgs_worst_case_group_operation_ratio]
                  | stats)
             }
         )),
    fixed_identity_d4:
      ([$candidates[] | candidate_digest]
       | group_by([.family, .witness_policy, .source_tag, .tag_count,
                   .output_router])
       | map(
           select(length == 3 and all(.[]; .saturated | not))
           | sort_by(.bits)
           | {
               identity: {
                 family: .[0].family,
                 witness_policy: .[0].witness_policy,
                 source_tag: .[0].source_tag,
                 tag_count: .[0].tag_count,
                 output_router: .[0].output_router
               },
               by_bits:
                 [.[] | {bits, worst_d4_group, worst_d5_group}],
               maximum_worst_d4: ([.[].worst_d4_group] | max)
             }
         )
       | sort_by(.maximum_worst_d4)
       | .[0:5]),
    best_rows: {
      supported_d4:
        ([$candidates[] | candidate_digest]
         | sort_by(.worst_d4_group) | .[0:5]),
      supported_d5:
        ([$candidates[] | candidate_digest]
         | sort_by(.worst_d5_group) | .[0:5]),
      random_d5:
        ([$candidates[] | candidate_digest]
         | sort_by(.worst_random_d5_group) | .[0:5]),
      query_st2:
        ([$candidates[] | candidate_digest]
         | sort_by(.query_st2_ratio) | .[0:5])
    }
  }
