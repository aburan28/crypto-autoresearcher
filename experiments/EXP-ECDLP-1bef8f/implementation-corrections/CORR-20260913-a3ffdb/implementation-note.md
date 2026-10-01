# RUN-ECDLP-7ff4d9 correction implementation

This new, self-contained Stage 0 implementation is governed by
`CORR-20260913-a3ffdb-stage0.yaml` and authorization
`DEC-20260913-3330b6`. It preserves the original exact-enumeration algorithms
for unaffected anchors so their outputs can be compared byte-for-value with
the immutable invalid run, while replacing its defective J3/J6 controls.

Implemented corrections:

- `validate_conditional_identity(payload)` independently checks
  `B=c_H*H^2` and `B^m=n`, derives the exponent as `m+m`, and refuses named
  false premises before forming a conclusion.
- The frozen cell records `H^4/p` and `B^2/n` separately and states that
  `B^2=n` is false there.
- KF-2 compares the supplied key set with the exact Cartesian nine-key set
  before indexing a coefficient and reports all missing and extra keys.
- KF-3 validates one structured payload, accepts only the complete synthetic
  `admissibility_test_only` fixture, and issues structured refusals for a
  Stage 0 prohibited-field payload and every missing or failed witness.
- Certificate-none and no-prohibited-value gates come from recursive scans of
  the assembled output and structured-artifact summaries. Their injected
  mutations must turn the corresponding gate false.
- J1, J2, J4, J5, J7, J8, INV-1/2/3, all numerical anchors, and all 60 seeded
  matched-null vectors are recomputed and compared with unaffected observations
  from `RUN-ECDLP-1bef8f-S0`. Its invalid identity interpretation and J6 verdicts
  are explicitly excluded.

Protocol deviations: none.

Scientific boundary: one toy-scale Stage 0 fixture/instrument correction only.
No later stage is entered; no small-root value is computed or estimated; no
lattice, reduction, scalar recovery, certificate, attack, or ECDLP
interpretation is produced. Certificate kind is `none`.
