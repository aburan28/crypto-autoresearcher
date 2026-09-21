# Experiment Contract: P1079 P231 Remaining Column Residual-Row Pivot

## Hypothesis
HYPOTHESIS: after the strict P1072/P1073 `[14,15]` packet, at least one target-eliminated factor relation row inside the post-promotion direct-source certificates has a residual pivot that removes remaining free column `6` or `7` with full parent-certificate direct charge below one Pollard-rho unit.

## Null hypothesis
All target-eliminated relation rows from the post-promotion direct-source certificates are dependent modulo the strict `[14,15]` packet rowspace, pivot outside columns `[6,7]`, or require full parent-certificate direct charge at or above one Pollard-rho unit.

## Parameters
- field/curve family: toy prime-field ECDLP artifact family for order `11779`, target `22050.cf1@11731`.
- sizes: one target; post-promotion direct-source certificate artifacts after P1069.
- seeds: deterministic existing artifact set; no new random seed.
- factor base: existing P231 low-term total-2 factor/certificate artifacts.
- relation shape: target-eliminated factor rows derived from public direct-source certificates.
- baseline: P1059 anchor plus P1067 train carrier plus P1069 promotion carrier plus P1072 stage-1 carrier plus P1073 strict column-15 carrier.

## Metrics
- group operations: full parent-certificate `direct_ops_over_rho`; allocated row charge is diagnostic only.
- field operations: not separately measured.
- memory: direct certificate artifact count, certificate count, relation-row count.
- relation probability: not measured; certificates are pre-materialized.
- rank: marginal source rank gain and removed free columns over the strict `[14,15]` packet.
- solver degree: not applicable.
- wall-clock: script runtime only.

## Positive control
Against the stage-1 packet, P1073 and P1074 column-15 carriers must still register as column-15 replay controls; this keeps the rowspace comparison aligned with P1078.

## Negative control
Rows whose residual only explains already-removed columns `14` or `15`, or whose parent certificate is one of the strict packet certificates, must not count as success for remaining columns `[6,7]`.

## Success criterion
Strict success requires a single target-eliminated relation row or parent certificate to remove column `6` or `7` relative to the strict packet, with full parent-certificate marginal charge `< 1.0` Pollard-rho unit.

## Falsification criterion
If all exact target-eliminated rows and all parent direct certificates fail to remove columns `[6,7]` relative to the strict packet, then this is a negative result for row-level residual reuse inside the existing direct-source certificate representation.

## Reproduction command
```bash
python3 tasks/ecdlp_index_calculus/low_term_total2_p1079_p231_remaining_column_residual_row_pivot.py
```

## Assumption and Evidence Labels
- `TOY-EVIDENCE`: target order is toy scale and cannot be projected to deployed curves directly.
- `MODEL-BOUND`: row-level scoring is bounded to existing direct-source certificates and target-eliminated factor rows.
- `HEURISTIC`: a below-rho row pivot is a source-construction signal, not a full index-calculus algorithm.
- `UNTESTED`: public routing to generate these rows before certificate construction is not solved here.

## Results
Latest run artifact: `ecdlp_index_calculus_state/low_term_total2_p1079_p231_remaining_column_residual_row_pivot_probe.json`.

- Claim status: `NEGATIVE_RESULT_P1079_RESIDUAL_67_SUPPORT_DEPENDENT_AFTER_1415_PACKET`.
- Strict baseline alignment with P1078: same free columns `[6,7]`, same strict rank gain `5`.
- Baseline strict certificates: `5`.
- Candidate post-promotion direct-source certificates after excluding strict-packet certificates: `35`.
- Candidate target-eliminated relation rows: `82`.
- Residual rows touching remaining columns `[6,7]`: `6`.
- Residual rows touching exactly one remaining column: `6`.
- Residual rows touching `[6,7]` while avoiding column `15`: `6`.
- Row-level remaining-column hits after strict packet: `0`.
- Parent-certificate remaining-column hits after strict packet: `0`.
- The six support-bearing residual rows all touch column `6`; no post-promotion target-eliminated residual row in this pool supplies a column-7 support direction.

## Interpretation
NEGATIVE RESULT: the current exact direct-source certificate representation has apparent column-6 support, but that support is rowspace-dependent after the strict `[14,15]` packet. This is not an impossibility result for prime-field ECDLP or index calculus. It rules out a narrower hope: simply splitting already materialized direct certificates into target-eliminated rows does not expose the missing `[6,7]` descent direction.

## Next Concrete Action
P1080 should target new residual supply, not ranking. The useful next experiment is a source-generator or representation-change scout that explicitly requests one of:

- target-eliminated rows with column `7` in factor support;
- column-6 rows whose residual is independent modulo the strict `[14,15]` packet;
- a representation where the `[5,6]`, `[2,4,5,6]`, or `[1,2,5,6]` dependent motifs split into independent directions.
