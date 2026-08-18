# Arm-A successor repair design

This package is a new immutable successor to `EXP-ECDLP-5ec1c5`. The prior
package and its fresh `TASK-20260809-221bc9` NO-GO report remain unchanged.
This task creates no implementation, run, or empirical evidence.

## Closure map for the fresh review

| Finding | Concrete repair |
|---|---|
| `REV-221bc9-01` map-level automorphism closure and scalar ambiguity | v4 manifests require a typed `map-entry-v1` for every closure element: stable contiguous `map_index`, exact `generator_word`, formula and field witness, composition row, `map_on_P`, per-map `certified_scalar_lambda`, scalar certificate, and replay witness. `declared_generators`, a total duplicate-free composition table, and a complete closure witness bind the generated group. Canonicalization and stabilizer receipts reference exact map indices and their own scalars. |
| `REV-221bc9-02` unbounded calibration and absent terminal disposition | Every registered anomalous and low-embedding calibration row carries `max_attempts=256`, explicit `calibration_unavailable_and_package_invalid` and `calibration_detector_mismatch_and_package_invalid` outcomes, required terminal receipt fields, and no-replacement semantics. |
| `REV-221bc9-03` hypothesis/test mismatch | The hypothesis and experiment success rule both require the complete eight-group FULL/NEG and FULL/BASE comparisons, each with an exact two-sided `p <= .025` gate under Bonferroni family-wise alpha `.05`, with all rows valid. |
| `REV-221bc9-04` implicit baseline selector | The frozen proof fixture now has fixture mode, selector schedule `[0,1,2]`, encoded selector inputs, exact preimage bytes, and an execution rule. The production PART-v3 hash contract remains separately frozen and is not inferred from the fixture. |
| duplicated immutable batch task state | A new batch record is used; no prior snapshot is edited. Its task state starts consistently with the new queue and is advanced only by subsequent immutable coordination commits. |

The successor remains finite toy-scale and carries no exponent or
cryptographic-scale claim. The next gate is the exact snapshot followed by a
fresh independent `review-adversarial` session.
