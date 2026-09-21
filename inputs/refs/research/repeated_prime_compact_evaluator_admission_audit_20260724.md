# Repeated-Prime Compact Evaluator Admission Audit

Date: 2026-07-24

## Handoff: no admitted compact evaluator

### Claim or task

Audit whether the current checkout contains a compact evaluator for the
repeated-prime divided orientation

```text
gamma_r = omega_0 / ell^r
```

that can recover the existing repeated-prime ascending fixtures without full
`E[ell^(r+1)]` acquisition.

### Status

`NEGATIVE RESULT / ADMISSION AUDIT / NO COMPACT RIGHT-DIVISION EVALUATOR / NOT-A-BREAK`

### Evidence

Artifacts:

- analyzer:
  `experiments/ecdlp_isogeny/iso_repeated_prime_compact_evaluator_admission_audit.py`
- result:
  `experiments/ecdlp_isogeny/iso_repeated_prime_compact_evaluator_admission_audit_result.json`
- verifier:
  `experiments/ecdlp_isogeny/iso_repeated_prime_compact_evaluator_admission_audit_verify.py`
- verifier result:
  `experiments/ecdlp_isogeny/iso_repeated_prime_compact_evaluator_admission_audit_verify.json`

The analyzer confirms:

- the accepted repeated-prime implementation still contains lift-order torsion
  acquisition patterns, including `torsion_basis(lift_order)` and
  `full_torsion_points_with_stats`;
- the existing fixed-`ell^2` local-power profile has failures on the
  conductor-27 fixtures `p in {577,619,757}`;
- the right-division degree proxy is present and has
  `explicit_map_right_division_is_compact=false`;
- no compact evaluator is admitted.

The verifier passes with zero failures.

### Interpretation

This does not close the repeated-prime idea.  It closes the current checkout as
evidence for the requested breakthrough.  The only route that can reopen the
branch is a new evaluator that passes a stronger sentinel:

```text
forbid torsion_basis(ell^(r+1));
forbid full lift-order torsion-field basis construction;
forbid secret-edge/path access before map freeze;
recover the nine exact repeated-prime composites;
reject wrong-level controls.
```

Until that exists, repeated-prime divided-orientation recovery remains a
correctness/selectivity theorem under a charged high-torsion information model,
not a general isogeny-complexity improvement, SCALLOP break, or ECDLP
consequence.

### Next concrete action

Write the runtime sentinel harness first, then develop candidate evaluators
inside it.  A candidate that trips the sentinel is automatically a scoped
negative, regardless of whether it recovers the toy maps.
