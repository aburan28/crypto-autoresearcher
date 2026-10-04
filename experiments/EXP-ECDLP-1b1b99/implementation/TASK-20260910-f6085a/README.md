# CM pure cost component

`costs.py` exports `strict_json_loads(data)`, `canonical_json(value)`,
`parse_cost_csv(data, required_columns)`, `validate_raw_rows(rows, *,
component_phases=None)`, `canonical_targets(prefixes, class_memberships)`,
`allocate_equal(row, *, strategy_view, scenario, targets, reason_code)`,
`validate_allocation_edges(rows, edges)`, and `actual_campaign_accounting(rows)`.
They use only standard-library integer arithmetic and are inert on import.

`reducers.py` exports exact `median7`, `median6`, `select_baselines(rows)`,
`reduce_primary(cells)`, `q_star(ladder)`, and `hard_validity(facts)`.  All
fractions are exact numerator/denominator values. Selection rows are one row per
`(interval, coordinate, candidate_arm, endpoint, block)` and include integer
`CPU_nanoseconds`, `repetitions`, and any `setup_CPU_nanoseconds`; they require
all 9 × 6 × 8 × 7 records. A primary cell names exactly two scalar and two
transport endpoint objects, each with fixed CPU and seven block objects.

The caller supplies candidate-prefix and endpoint/class tables. Their shape and
membership are checked, but this module never represents that as certificate
verification. Nor does it infer authorization, resource/custody validity,
runtime success, a launched run, a mathematical fact, or a performance result.
