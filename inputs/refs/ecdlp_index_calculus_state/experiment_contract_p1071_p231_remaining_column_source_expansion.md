# Experiment Contract: P1071 P231 Remaining-Column Source Expansion

## Hypothesis
Changing the source family beyond the exhausted `mode_low_term_support_total5/top16/direct_source` pool exposes a second target-eliminated rank direction over the P1069 promoted packet, removing at least one remaining free column in `[6,7,14,15]`.

## Null hypothesis
The available expanded selected-source artifacts are still rank-dependent after the P1069 promoted packet. No selector/top-k variant, no single later case, and no full expanded-source batch adds marginal rank or removes any remaining free column.

## Parameters
- field/curve family: toy prime-field ECDLP harness, target `22050.cf1@11731`
- sizes: p231 state artifacts, order `11779`
- factor base: current order-`11779` target-eliminated factor namespace
- promoted packet: P1059 anchor `18464_18471:18465`, P1067 training carrier `20464_20471:20465`, and P1068 validation carrier `20632_20639:20636`
- candidate source surface: all available `low_term_total2_selected_leaf_term_support_scout_22050_col15_selector_expanded_*` selector/top-k cases after promoted carrier `20632_20639`
- audited selectors: all public selector names found in the selected-source artifacts
- audited top-k values: all top-k values found in the selected-source artifacts
- target columns: promoted-packet free columns `[6,7,14,15]`

## Metrics
- selector/top-k inventory and case counts
- single-case marginal rank and free-column removals over the promoted packet
- per selector/top-k full-family marginal rank and free-column removals
- all-expanded-source full-pool marginal rank and free-column removals
- charge to first useful single-case or family hit, if any
- whether useful evidence is direct-public-key-verified or only rank-bearing

## Positive control
The promoted packet must reproduce P1069/P1070: marginal rank gain `1` over the original anchor and remaining free columns `[6,7,14,15]`.

## Negative control
The original P1070 family `mode_low_term_support_total5/top16/direct_source` must remain exhausted: no second-direction rank or free-column removal.

## Success criterion
P1071 is positive if any expanded selector/top-k single case, selector/top-k family, or the full expanded-source pool adds marginal rank or removes at least one of `[6,7,14,15]` over the promoted packet.

## Falsification criterion
P1071 is negative if even the full expanded-source pool has marginal rank gain `0` and removes no free columns over the promoted packet.

## Reproduction command
```bash
python3 tasks/ecdlp_index_calculus/low_term_total2_p1071_p231_remaining_column_source_expansion.py \
  --contract ecdlp_index_calculus_state/experiment_contract_p1071_p231_remaining_column_source_expansion.md \
  --out ecdlp_index_calculus_state/low_term_total2_p1071_p231_remaining_column_source_expansion_probe.json
```

## Assumption and claim discipline
- `TOY-EVIDENCE`: p231/order-`11779` only.
- `MODEL-BOUND`: rank is measured inside the current verifier target-eliminated factor namespace.
- `SOURCE-FAMILY-EXPANSION`: this changes selector/top-k materialization but remains within the same target-specific artifact family.
- `SINGLE-TARGET`: current selected-source artifacts contain only `22050.cf1@11731`; no fresh-target claim is made.
- `ORACLE-POOL-AUDIT`: full-pool success would show source supply exists; a later P1072 would still need a public selector.
- `POLLARD-RHO-BOUNDARY`: marginal rank evidence is not a complete faster-than-rho ECDLP algorithm.

## Next concrete action after run
If positive, freeze the lowest-cost public selector/top-k family and validate on a disjoint later split. If negative, the next experiment must create new source rows or a new representation, not rescore the existing selected-source artifacts.

## Results
- timestamp: `2026-06-30T08:45:23Z`
- claim: `OBSERVATION_P1071_EXPANDED_SOURCE_FAMILY_HAS_SECOND_DIRECTION`
- expanded source inventory: `1270` cases across `40` selector/top-k families and `16` later windows; all artifacts are for target `22050.cf1@11731`, so this is not a fresh-target validation.
- original P1070 family control: `mode_low_term_support_total5/top16` remains exhausted with marginal rank gain `0` and removed columns `[]`.
- single-case hits: `10`; best single hit is `20664_20671:20666`, selector `mode_low_term_support_total5`, top-k `7`, row keys `[salt164,salt166]`, direct charge `0.75182482` rho, direct-public-key verified, marginal rank gain `1`, removed free column `[14]`, remaining `[6,7,15]`.
- selector/top-k family hits: `2`; both are `mode_low_term_support_total5`, with top-k `7` and `12`.
- best family: `mode_low_term_support_total5/top7`, `27` cases over `14` windows, marginal charge `20.48905116` rho, marginal rank gain `2`, removed columns `[14,15]`, remaining `[6,7]`.
- second family: `mode_low_term_support_total5/top12`, `36` cases over `14` windows, marginal charge `26.510949` rho, marginal rank gain `2`, removed columns `[14,15]`, remaining `[6,7]`.
- full expanded pool: marginal charge `855.35036911` rho, marginal rank gain `2`, removed columns `[14,15]`, remaining `[6,7]`.
- interpretation: changing source family/top-k exposes source rows for remaining-column rank. This is a source-supply positive but not yet a public efficient selector: the full family charges well above rho, and the artifacts are still single-target.
- artifact: `ecdlp_index_calculus_state/low_term_total2_p1071_p231_remaining_column_source_expansion_probe.json`

## Handoff: P1072 frozen top-k7 split validation

### Claim or task
Freeze `mode_low_term_support_total5/top7`, promote the earliest below-rho column-`14` hit, and test whether later top-k7 rows add the next direction against the updated packet.

### Status
HYPOTHESIS

### Assumptions
- P1071 used an oracle expansion audit, so P1072 must use a chronological split.
- The first top-k7 hit can be treated as the training/first-stage carrier.
- Later validation must be scored against the packet that already includes the first-stage carrier.

### Evidence so far
- P1071 best single top-k7 hit removes column `14` at `0.75182482` rho.
- The full top-k7 family removes `[14,15]`, proving a second direction exists somewhere in the family.

### Failure modes
- Later top-k7 rows may remove column `15` only after above-rho charge.
- The column-`15` contribution may require batch effects rather than a single public case.
- The family may remain same-target only until fresh-target artifacts are generated.

### Next concrete action
```bash
python3 tasks/ecdlp_index_calculus/low_term_total2_p1072_p231_topk7_split_validation.py \
  --contract ecdlp_index_calculus_state/experiment_contract_p1072_p231_topk7_split_validation.md \
  --out ecdlp_index_calculus_state/low_term_total2_p1072_p231_topk7_split_validation_probe.json
```

### Artifact paths
- `ecdlp_index_calculus_state/experiment_contract_p1071_p231_remaining_column_source_expansion.md`
- `tasks/ecdlp_index_calculus/low_term_total2_p1071_p231_remaining_column_source_expansion.py`
- `ecdlp_index_calculus_state/low_term_total2_p1071_p231_remaining_column_source_expansion_probe.json`
