# Red-Team Review: Coordinate Energy Certificate V2.1

## Handoff: V2.1 predictor protocol pre-freeze audit

### Claim or task

Determine whether V2.1 is sound enough to freeze and consume a registered
development lockbox.

### Status

`OPEN`, `MODEL-BOUND`, `RED-TEAM REVISED`.

The audited pre-revision contract was
`e9fa9e44ae9aa9b1cacd1f222d96529b6a07be113cd0a860b48f9c786bc24bbe`.
It was not approved for launch. The findings below have been incorporated
into the successor now awaiting a clean freeze.

### Assumptions

- V2 remains control-invalid and supplies no candidate evidence.
- permutation ranks use `(1+extreme)/(1+draws)`;
- target-wide candidate multiplicities are heavy-tailed and family-specific;
- deterministic replay and semantic independence are distinct properties;
- seed freshness requires non-observation, not only numeric disjointness.

### Evidence so far

- 31 permutations made the positive-control Bonferroni gate mathematically
  unreachable;
- the absolute negative recall cap measured bucket width, not association;
- V2's binary planted negative did not match candidate multiplicities;
- arbitrary development configurations could be accepted with
  `--development`;
- the inherited mutation harness only compared projection digests;
- the 1% rule excluded V2's six-row bucket but had no boundary fixtures;
- confirmatory seeds had been written before a clean freeze.

### Failure modes

#### P0

1. A development control cannot pass if the finite permutation rank cannot
   cross its registered threshold.
2. A verifier that accepts arbitrary development inputs cannot certify an
   exact calibration profile.
3. A mutation is not semantically rejected merely because its serialized
   projection digest changes.

#### P1

1. Binary planted controls can miss instability in heavy-tailed candidate
   multiplicities.
2. Eight deterministic sentinels cannot establish a low false-positive rate.
3. A 1% support floor is not a stability theorem.
4. Prepublished seed-disjoint values are not proved fresh.
5. Mirrored implementations provide deterministic replay, not complete
   structural independence.

#### P2

Inherited predictor gate decisions still use rounded floating summaries in
some paths. Counts and multiplicity sums should eventually replace display
floats at every threshold boundary.

### Incorporated repairs

- development and confirmation both use 127 permutations;
- one exact registered development profile is distinct from exploratory
  development;
- negatives permute each candidate family's complete label pair;
- eight sentinels are required per family and explicitly do not claim
  false-positive calibration;
- exact 0.9%, 1%, 2%, 5%, pooled-only, balanced-null, and 1.1% planted
  controls are registered;
- confirmatory seeds are derived only after a clean source freeze;
- five semantic mutants run through the complete verifier with affected
  eligibility digests refreshed.

### Strongest valid conclusion

> The revised protocol closes the observed V2 rare-bucket failure and the
> pre-freeze P0 defects. It does not prove that 1% coverage is generally
> stable, establish a structured-group barrier, or provide an ECDLP
> improvement.

### Next concrete action

Commit the revised no-seed-lock implementation, run the untouched registered
development lockbox once, and independently inspect all 24 candidate-matched
sentinels plus semantic mutation receipts before deriving confirmatory seeds.

### Artifact paths

- `development/COORD-ENERGY-CERT-V2.1/contract.md`
- `development/COORD-ENERGY-CERT-V2.1/calibration-analysis.md`
- `src/coord_energy_certificate_v21.py`
- `src/verify_coord_energy_certificate_v21.py`
- `tests/test_coord_energy_certificate_v21.py`
- `tests/test_verify_coord_energy_certificate_v21.py`
