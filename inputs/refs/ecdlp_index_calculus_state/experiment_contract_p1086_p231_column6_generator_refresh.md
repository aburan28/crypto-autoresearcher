# Experiment Contract: P1086 P231 Column-6 Generator Refresh

## Hypothesis
HYPOTHESIS: after P1085 integrates the verified column-7 relation, a changed public source route or representation can produce an order-`11779` column-6 row with marginal rank gain below Pollard rho.

## Null hypothesis
The currently available and newly refreshed public source routes only produce column-6 rows that are dependent, RHS-inconsistent, verifier-failing, or above rho after source/materialization accounting.

## Parameters
- field/curve family: toy prime-field ECDLP artifact family for order `11779`, target `22050.cf1@11731`.
- base packet: order-filtered strict packet plus P1083/P1085 column-7 row.
- remaining priority column: `6`.
- baseline: Pollard rho `137` generic steps.
- route classes: P1083/P1085 route classes plus any new public source route slices explicitly registered by the script.

## Metrics
- source/materialization charge over rho:
- verifier pass/fail:
- column-6 support rows:
- marginal rank gain:
- coefficient rank:
- augmented rank:
- RHS consistency:
- free columns before/after:
- route/selector/top-k:
- holdout/disjoint status:

## Positive control
Reproduce P1085: packet rank `15`, augmented rank `15`, free columns `[6,16]`, remaining priority `[6]`, and no strict next-direction candidate in the existing P1083 route set.

## Negative control
Reject all order-mismatched certificates and metadata-only support. Existing below-rho support `[3,5,6]` and `[2,4,5,6]` rows must remain rank-zero against the P1085 packet unless the generator materially changes the rowspace.

## Success criterion
Strict success requires a verified order-`11779` row touching column `6`, below rho, RHS-consistent, and adding marginal rank against the P1085 packet.

## Falsification criterion
If all searched/refreshed routes produce only dependent, inconsistent, unverified, or above-rho column-6 rows, record a scoped negative and identify the next representation or source-family change.

## Reproduction command
```bash
python3 tasks/ecdlp_index_calculus/low_term_total2_p1086_p231_column6_generator_refresh.py
```

## Assumption and Evidence Labels
- `TOY-EVIDENCE`: target order is toy scale and cannot be projected to deployed curves directly.
- `MODEL-BOUND`: route search is bounded to materialized artifacts unless new source slices are explicitly generated.
- `HEURISTIC`: packet rank progress is an index-calculus precursor, not a complete algorithm.
- `UNTESTED`: no deployed-curve relevance is claimed.

## Result: 2026-06-30

Status: `NEGATIVE_RESULT_P1086_REFRESHED_ROUTES_NO_VERIFIED_COLUMN6_RANK_GAIN`.

The P1086 script reproduced the P1085 packet state: rank `15`, augmented rank `15`, free columns `[6,16]`, remaining priority `[6]`, and target-descent consistency `true`. It then scanned `1749` refreshed route artifacts across `direct_col15_lowterm_support5`, `direct_earlycols_shape`, `direct_support10_scheduled`, `relation_priority_22050`, `direct_other_22050`, and `priority_conditioned_col6_col15_direct`.

Evidence:
- verified coefficient column-6 support rows: `385`;
- strict column-6 packet successes: `0`;
- best coefficient candidate marginal rank gain: `0`;
- best candidate charge: `0.72992701x` rho;
- priority scout artifacts checked: `215`;
- order-`11779` target scout cases checked: `1463`;
- actual order-`11779` target column-6 exported-form cases: `0`;
- carrier-quotient representation progress count: `255`, but identity projection collapse count is also `255`, so this is not accepted as a verified coefficient relation.

Interpretation: this is a scoped negative for the refreshed materialized route set and the current carrier-quotient representation. It does not rule out a column-6 route. The next positive question is whether a source-form generator can force actual order-`11779` column-6 exported forms before direct certificate export.

Artifacts:
- `tasks/ecdlp_index_calculus/low_term_total2_p1086_p231_column6_generator_refresh.py`
- `ecdlp_index_calculus_state/low_term_total2_p1086_p231_column6_generator_refresh_probe.json`
- `ecdlp_index_calculus_state/p1086_column6_generator_refresh_probe.json`
- `ecdlp_index_calculus_state/p1086_column6_generator_refresh.md`

## Handoff: P1087 order-11779 column-6 exported-form generator

### Claim or task
Generate public source cases whose exported relation forms actually contain order-`11779` column `6`, then export direct certificates and rescore against the P1085 packet.

### Status
HYPOTHESIS

### Assumptions
- `TOY-EVIDENCE`: target remains the p231/order-`11779` toy family.
- `MODEL-BOUND`: success is limited to the local public relation-equation verifier and packet-rank model.
- `HEURISTIC`: packet rank closure is an index-calculus precursor, not an end-to-end faster-than-rho algorithm.

### Evidence so far
- P1086 found `385` actual column-6 coefficient rows, but all were dependent against the P1085 packet.
- P1086 found `0` actual order-`11779` priority-scout column-6 exported-form cases among `1463` target cases.
- Order-`9887` column-6 route hits exist in nearby scouts but are explicitly excluded from the order-`11779` packet.

### Failure modes
- The generator may again produce metadata-only column-6 support rather than exported coefficient support.
- It may produce verified column-6 forms whose target-eliminated rows stay in the P1085 rowspace.
- It may improve only a representation quotient, not the verified coefficient rowspace.

### Next concrete action
Create `tasks/ecdlp_index_calculus/low_term_total2_p1087_p231_column6_exported_form_generator.py` with a guard that requires actual order-`11779` column-6 exported forms before certificate export.

### Artifact paths
- `ecdlp_index_calculus_state/experiment_contract_p1087_p231_column6_exported_form_generator.md`
