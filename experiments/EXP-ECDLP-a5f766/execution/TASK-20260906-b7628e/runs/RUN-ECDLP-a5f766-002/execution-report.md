# Execution report — RUN-ECDLP-a5f766-002 (EXP-ECDLP-a5f766 v2)

Terminal status: **valid** (single run completed within all ceilings).

Observations only. No interpretation of the hypothesis, no status change,
no claim that any heuristic is supported or refuted; that judgment belongs
to /review-evidence under Coordinator authority.

## Frozen prediction reference (read-only)

`approved-contract-v2.yaml` `preregistered_prediction`: J = 2*x0*x1/A0 - x0^2*A1/A0^2;
active u gives J' = J; pullback eps->c*eps gives J_pullback = c*J; J_C = J_G = 0;
J_V = -6 before pullback. Etaleness gives uniqueness, not a blanket zero derivative.

## Recorded outcomes (no interpretation)

- rows planned/executed: 96 / 96
- certificate group statuses: {'1_expansion': 'PASS', '2_active_model_action': 'PASS', '3_pullback_law': 'PASS', '4_constant_pure_gauge_null': 'PASS', '5_flex_identities': 'PASS', '6_scoped_etale_section_lemma': 'UNRESOLVED'}
- symbolic nonzero residual count: 0
- row failure counts: {'expansion_fail': 0, 'gauge_fail': 0, 'covariance_fail': 0, 'orderzero_fail': 0, 'indeparith_fail': 0}
- nonzero constant/pure-gauge jets among 64 C/G rows: 0
- flex mismatches against -6*c among 32 V rows: 0
- eligibility: [{'p': 7, 'n_points': 6, 't_mod_p': 2, 'eligible_p_not_divides_t': True, 'hasse_coefficient_mod_p': 2, 'hasse_nonzero': True, 'methods_agree': True}, {'p': 11, 'n_points': 12, 't_mod_p': 0, 'eligible_p_not_divides_t': False, 'hasse_coefficient_mod_p': 0, 'hasse_nonzero': False, 'methods_agree': True}, {'p': 13, 'n_points': 12, 't_mod_p': 2, 'eligible_p_not_divides_t': True, 'hasse_coefficient_mod_p': 2, 'hasse_nonzero': True, 'methods_agree': True}, {'p': 17, 'n_points': 21, 't_mod_p': 14, 'eligible_p_not_divides_t': True, 'hasse_coefficient_mod_p': 14, 'hasse_nonzero': True, 'methods_agree': True}]
- rejection tests: [('char_3', True), ('A0_zero', True), ('n_equals_p', True), ('singular_curve', True)]
- collisions: {'C_G_pairs': {'equal_jet': 32, 'distinct_raw': 32, 'total': 32}, 'P_minus_P': {'same_F': 96, 'total': 96}}
- stage wall seconds: {'preconditions_and_eligibility': 0.0939873750321567, 'symbolic_certificates_and_scoped_lemma': 0.2329621659591794, 'finite_controls': 0.0055342919658869505, 'immutable_artifact_production': 2.346792457974516}

## Known-false control outcome (expected positive control)

The blanket zero-derivative rule is the deliberately known-false object. The V
family exhibits J = -6 (and -6*c after pullback) on all 32 rows while the section
remains a smooth nonidentity order-3 section: recorded as the control behaving as
designed. This is not negative evidence against the research direction or IDEA-109.

## Anomalies and unexpected observations

- none recorded

## Observations

- contract sha256 verified: a81b1476954d80d8042d697299f2522a6658431b17380f3ef423cb5403c6c79d
- special-fiber certificates hold on all panel primes: 3375 unit; P on curve; tangent slope 3; 2P=-P so 3P=O; P nonidentity (y0=5 nonzero)
- eligibility: [{'p': 7, 'n_points': 6, 't_mod_p': 2, 'eligible_p_not_divides_t': True, 'hasse_coefficient_mod_p': 2, 'hasse_nonzero': True, 'methods_agree': True}, {'p': 11, 'n_points': 12, 't_mod_p': 0, 'eligible_p_not_divides_t': False, 'hasse_coefficient_mod_p': 0, 'hasse_nonzero': False, 'methods_agree': True}, {'p': 13, 'n_points': 12, 't_mod_p': 2, 'eligible_p_not_divides_t': True, 'hasse_coefficient_mod_p': 2, 'hasse_nonzero': True, 'methods_agree': True}, {'p': 17, 'n_points': 21, 't_mod_p': 14, 'eligible_p_not_divides_t': True, 'hasse_coefficient_mod_p': 14, 'hasse_nonzero': True, 'methods_agree': True}]
- ordinary-eligible primes: [7, 13, 17]; ineligible (auxiliary only): [11]
- rejection fixtures: all four rejected before jet interpretation: ['char_3', 'A0_zero', 'n_equals_p', 'singular_curve']
- symbolic certificate statuses: {'1_expansion': 'PASS', '2_active_model_action': 'PASS', '3_pullback_law': 'PASS', '4_constant_pure_gauge_null': 'PASS', '5_flex_identities': 'PASS', '6_scoped_etale_section_lemma': 'UNRESOLVED'}; nonzero residuals: 0
- 96-row grid executed: {'rows': 96, 'expansion_fail': 0, 'gauge_fail': 0, 'covariance_fail': 0, 'orderzero_fail': 0, 'indeparith_fail': 0, 'null_nonzero': 0, 'flex_mismatch': 0}
- C/G collision pairs: {'equal_jet': 32, 'distinct_raw': 32, 'total': 32} (same invariant jet; raw coordinate motion differs where v=1 or via G's x1=6 seed)
- P/-P sign collisions retained: {'same_F': 96, 'total': 96} (same x-jet, same F0/J; no injective-encoding claim)
- G raw x1 = 6 before further actions verified at every panel prime

## Protocol deviations

- PD-1 (infrastructure): Executor subagent dispatched twice via the session Task
  runtime; both returned empty with zero artifacts. The frozen contract was then
  executed in-process by the dispatching session under the executor role contract
  (observations only, identical write scope and budget). Downstream validator and
  red-team sessions remain independent and did not originate this implementation.

## Certificate group 6 note

Group 6 (scoped etale-section lemma) is recorded UNRESOLVED: part 1 carries a
complete elementary proof in lemma-proof.md (subject to independent audit), the
part 2 witness is machine-checked, and the IDEA-109 reconciliation is deferred by
design.md to the later proof audit. A deferred proof obligation is unresolved work,
not a refutation.
