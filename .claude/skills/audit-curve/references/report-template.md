# Curve audit report template

Use this as a reporting contract, not as a substitute for raw certificates.
Unknown values are `null`; do not guess or silently omit them.

```yaml
audit_version: curve-audit-v1
recorded_at: null
auditor: null
verdict: INDETERMINATE

scope:
  security_game: null
  attacker: null
  target_security_bits: null
  success_probability: null
  operation_unit: null
  time_budget: null
  memory_budget: null
  data_or_query_budget: null
  parallelism: null
  reusable_precomputation: null
  isogeny_path_availability: null
  isogeny_field: null
  graph_boundary: null
  implementation_in_scope: null
  adversarial_input_capability: null
  scalar_reuse: null
  result_oracle: null

instance:
  curve_alias: null
  curve_uid: null
  field: null
  model: null
  coefficients: null
  generator: null
  subgroup_order_r: null
  subgroup_order_factorization: null
  subgroup_order_primality: null
  total_order_N: null
  total_order_factorization: null
  cofactor: null
  source_provenance: null

exact_checks:
  field_validity: {status: NOT_RUN, evidence: []}
  nonsingularity: {status: NOT_RUN, evidence: []}
  generator_on_curve: {status: NOT_RUN, evidence: []}
  generator_nonidentity: {status: NOT_RUN, evidence: []}
  generator_exact_order: {status: NOT_RUN, evidence: []}
  point_count: {status: NOT_RUN, evidence: []}
  group_structure: {status: NOT_RUN, evidence: []}
  trace_and_frobenius: {status: NOT_RUN, evidence: []}
  ordinary_or_supersingular: {status: NOT_RUN, evidence: []}
  curve_order_factorization: {status: NOT_RUN, evidence: []}
  twist_order_and_structure: {status: NOT_RUN, evidence: []}
  embedding_degrees: {status: NOT_RUN, evidence: []}
  endomorphism_data: {status: NOT_RUN, evidence: []}

instrument_controls:
  - name: null
    expected: null
    actual: null
    status: NOT_RUN
    evidence: []

class_invariants:
  q: null
  t: null
  frobenius_polynomial: null
  delta_pi: null
  fundamental_discriminant_D_K: null
  frobenius_order_conductor_f_pi: null
  frobenius_order_conductor_factorization: null
  extension_orders_checked: []
  anomalous: null
  supersingular: null
  embedding_degrees: []
  quadratic_twist_order: null

representative_structure:
  endomorphism_order_discriminant_D_E: null
  endomorphism_order_conductor_f_E: null
  endomorphism_order_conductor_factorization: null
  conductor_gap_index_g_pi_E: null
  conductor_gap_factorization: null
  endomorphism_order_basis_or_certificate: null
  endomorphism_order_status: INDETERMINATE
  volcano_levels: []
  inseparable_endomorphisms: []
  explicit_endomorphism_actions: []

attack_ledger:
  - attack: null
    preconditions: null
    status: NOT_RUN
    total_work: null
    offline_work: null
    online_work: null
    amortization_basis: null
    parallelism: null
    memory: null
    data_or_queries: null
    success_probability: null
    evidence: []

isogeny_paths: []
implementation_checks:
  formula_dependency:
    decoder_coefficients: []
    addition_coefficients: []
    doubling_coefficients: []
    ladder_coefficients: []
    output_validation: null
  formula_compatible_companions: []
  singular_smooth_locus_checks: []
  observable_and_sign_ambiguity: null
  subgroup_query_cost: null
  crt_modulus: null
  interval_completion_cost: null

statistics:
  purpose: null
  population: null
  sampling_distribution: null
  unique_samples: null
  determinate_samples: null
  indeterminate_samples: null
  excluded_samples: null
  weak_hits: null
  false_negative_assessment: null
  dependence_or_mixing: null
  interval_method: null
  confidence_level: null
  prevalence_interval: null
  stopping_rule: null

artifacts:
  commands: []
  software_versions: []
  certificates: []
  raw_outputs: []
  failures_and_timeouts: []

conclusion:
  supported_claim: null
  weakness_scope: null
  best_total_attack_cost: null
  coverage_limit: null
  unresolved_checks: []
  assumptions: []
```

For each isogeny path include source and destination curve UIDs, ordered edge
degrees, map or kernel artifact hashes, field of definition, path-discovery
cost, construction cost, evaluation cost, and proof that the target subgroup
survives. For each certificate include its format, producer, independent
verification command, hash, and verification result.

For each volcano-level record include `ell`, `v_ell(f_pi)`,
`v_ell(f_E)`, the evidence for both valuations, and whether the level is
certified or unresolved. For each isogeny edge include separability, field of
definition, source and destination `f_E`, and direction
`horizontal | ascending | descending | unresolved`. For certified path
endpoints also include `N_vertical`; do not substitute it for total path
degree or measured cost.
