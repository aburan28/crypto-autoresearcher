# Experiment Contract: P1078 P231 Remaining Column Source-Family Pivot

## Hypothesis
HYPOTHESIS: after the P1072/P1073 packet removes columns 14 and 15 for `22050.cf1@11731`, the expanded P1071 selector/top-k source pool contains a public source family or single source row that removes remaining free column 6 or 7 with marginal direct charge below one Pollard-rho unit.

## Null hypothesis
The expanded P1071 source pool only replays column-15 removal, adds rank without removing columns 6 or 7, or requires marginal direct charge at or above one Pollard-rho unit for any column-6/7 movement.

## Parameters
- field/curve family: toy prime-field ECDLP artifact family already materialized for order `11779`, target `22050.cf1@11731`.
- sizes: one target, post-promotion selected-source windows after P1069; selector/top-k grid inherited from P1071.
- seeds: deterministic existing artifact set; no new random seed.
- factor base: existing P231 low-term total-2 factor/certificate artifacts.
- relation shape: direct-source selected cases scored by certificate rank over the existing factor matrix.
- baseline: P1059 anchor plus P1067 train carrier plus P1069 promotion carrier plus P1072 stage-1 top-k7 carrier plus P1073 strict column-15 carrier.

## Metrics
- group operations: direct selected-case charge normalized by Pollard-rho unit.
- field operations: not separately measured; direct charge is the existing proxy.
- memory: artifact/certificate count and selector/top-k pool size.
- relation probability: not measured here; source pool is pre-materialized.
- rank: marginal source rank gain over the `[14,15]` packet.
- solver degree: not applicable to this source-rank audit.
- wall-clock: script runtime only; not a cryptanalytic complexity claim.

## Positive control
Column-15 replay controls must still be detected when the P1073 strict carrier or the P1074 disjoint diagnostic carrier is evaluated against the stage-1 packet.

## Negative control
Against the strict `[14,15]` packet, a source row or family that removes only column 15 is classified as replay and must not count as success.

## Success criterion
Strict success requires at least one single source row, selector/top-k family, or full-pool public inventory evaluation with `removed_free_columns` intersecting `{6,7}` and `marginal_charge_over_rho < 1.0` relative to the strict `[14,15]` packet.

## Falsification criterion
If all expanded single rows, selector/top-k families, and the full pool fail to remove column 6 or 7 below one Pollard-rho unit, the hypothesis is narrowed to a negative result for this representation, target, source pool, and `[14,15]` baseline packet.

## Reproduction command
```bash
python3 tasks/ecdlp_index_calculus/low_term_total2_p1078_p231_remaining_column_source_family_pivot.py
```

## Assumption and Evidence Labels
- `TOY-EVIDENCE`: target order is toy scale and cannot be projected to deployed curves directly.
- `MODEL-BOUND`: scoring is bounded to the existing direct-source certificate model.
- `HEURISTIC`: below-rho direct charge is a frontier signal, not a full index-calculus algorithm.
- `UNTESTED`: fresh-target and cryptographic-scale transfer remain untested.

## Results
Latest run artifact: `ecdlp_index_calculus_state/low_term_total2_p1078_p231_remaining_column_source_family_pivot_probe.json`.

- Claim status: `NEGATIVE_RESULT_P1078_EXPANDED_FAMILIES_NO_67_DIRECTION_AFTER_1415_PACKET`.
- Strict packet free columns: `[6, 7]`.
- Expanded candidate cases after excluding strict-packet refs: `1268`.
- Expanded selector/top-k families after excluding strict-packet refs: `40`.
- Single remaining-column hits for columns `[6,7]`: `0`.
- Family remaining-column hits for columns `[6,7]`: `0`.
- Full pool marginal rank gain: `0`.
- Full pool removed free columns: `[]`.
- Full pool marginal charge over rho: `853.81022312`.
- Stage1 replay controls: `4` column-15-only replays; best replay `20696_20703:20701` at marginal charge `0.75182482`.
- Positive control: P1073 strict winner replays column 15 against stage1 at marginal charge `0.7810219`; P1074 diagnostic carrier replays column 15 against stage1 at marginal charge `0.75182482`.

## Interpretation
NEGATIVE RESULT: for this toy target, direct-source representation, current P1071 expanded source pool, and strict `[14,15]` packet, the remaining columns `[6,7]` have no observable single-row, selector/top-k-family, or full-pool direction. This does not rule out index calculus for prime-field ECDLP. It rules out continuing to sort the same post-P1073 top-k/source-family surface as a route to columns `[6,7]`.

## Next Concrete Action
P1079 should change representation or decomposition source rather than ranking this exhausted surface again. The next positive test is a source-construction pivot that searches for certificates whose support touches exactly one of columns `[6,7]` before adding them to the `[14,15]` packet, with column-15 replay used only as a calibration control.
