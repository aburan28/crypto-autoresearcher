# Experiment Contract: P1076 P231 Blocker Prefilter Audit

## Hypothesis
The best P1075 route fails only because one public false-positive blocker, `20688_20695:20690`, precedes the true disjoint carrier, `20696_20703:20701`. A cheap public prefilter or honest two-candidate amortization may reject or absorb that blocker and restore the carrier below one rho.

## Null hypothesis
The blocker is indistinguishable from the carrier until full direct-source certificate generation or verifier labels are available. In that case, the best P1075 prefix remains above rho and the blocker cannot be treated as a free prefilter win.

## Parameters
- field/curve family: toy prime-field ECDLP audit, target `22050.cf1@11731`, group order `11779`
- surface: P1072 top-k7 validation refs after excluding the P1073 winner window `20664_20671`
- best P1075 route: `window_max_direct_ops_asc__chronological`
- blocker: `20688_20695:20690:mode_low_term_support_total5:7`
- carrier: `20696_20703:20701:mode_low_term_support_total5:7`
- baseline: P1075 best prefix `1.47445256` rho; carrier-only oracle `0.75182482` rho

## Metrics
- group operations: normalized source charge over rho
- field operations: inherited from existing certificate artifacts
- memory: direct certificate artifacts, base/candidate path overlap, matched certificate counts
- relation probability: whether the blocker has a matching direct-source certificate
- rank: marginal rank gain/removal over the stage-1 packet
- solver degree: not tested
- wall-clock: secondary; artifact hashes and operation counters are primary

## Positive control
The carrier-only window-local check must remove column `15` at `0.75182482` rho.

## Negative control
The blocker-plus-carrier P1075 prefix must cost `1.47445256` rho and remove column `15` only when the carrier is included.

## Strict success criterion
P1076 is strictly positive only if it finds a predeclared public, non-label prefilter or sharing rule that can be justified before full direct-source certificate generation and brings the blocker-plus-carrier route below one rho.

## Diagnostic success criterion
P1076 may record a diagnostic positive if post-hoc public filters over salts, offsets, or direct-source charge skip the blocker and route to the carrier below rho. Diagnostic positives require P1077 holdout validation before promotion.

## Falsification criterion
P1076 is negative if:
- the only clean blocker rejection is the post-generation certificate-selector label; and
- no direct-source path/certificate work is shared between blocker and carrier; and
- no diagnostic public filter reaches the carrier below rho.

## Reproduction command
```bash
python3 tasks/ecdlp_index_calculus/low_term_total2_p1076_p231_blocker_prefilter_audit.py \
  --contract ecdlp_index_calculus_state/experiment_contract_p1076_p231_blocker_prefilter_audit.md \
  --out ecdlp_index_calculus_state/low_term_total2_p1076_p231_blocker_prefilter_audit_probe.json
```

## Claim status taxonomy
- `HYPOTHESIS`: blocker prefilter or amortization.
- `MODEL-BOUND`: toy p231/order-`11779` target-eliminated rank model.
- `TOY-EVIDENCE`: no cryptographic-scale claim.
- `POSTHOC-DIAGNOSTIC`: filters derived from the blocker/carrier contrast are not validated.
- `POLLARD-RHO-BOUNDARY`: success requires below one normalized rho.

## Results
- claim: `OBSERVATION_P1076_POSTHOC_PUBLIC_BLOCKER_FILTERS_RESTORE_BELOW_RHO_NEED_HOLDOUT`
- strict success: `false`
- diagnostic success: `true`
- blocker matched direct-source certificates: `0`
- carrier matched direct-source certificates: `1`
- direct-source path overlap: `0`
- shared base paths: `2`
- combined blocker-plus-carrier prefix: `1.47445256` rho
- carrier-only charge: `0.75182482` rho
- remaining prefilter budget before one rho: `0.24817518` rho
- required savings from the two-candidate prefix: `0.47445256` rho
- public feature comparison: selected term support and priority hits are identical; row keys and salts have no overlap.
- diagnostic filters that skip the blocker and put the carrier first below rho: `salt_max_le_170`, `salt_min_le_165`, `salt_sum_le_335`, `salt_span_le_5`, `offset_ge_5`, `direct_ops_ge_0_75`, `has_salt165`, `has_salt170`, `no_salt174`.

## Interpretation
The clean certificate-level rejection is not a free public prefilter: the blocker is rejected only because it has no matching direct-source certificate for the selected `top_k=7` case, while the carrier has one. That is a post-generation label. However, the blocker/carrier contrast exposes several public salt/offset filters that restore the carrier below rho on this surface. These are post-hoc diagnostics and require holdout validation before promotion.

## Handoff: P1077 diagnostic filter holdout

### Claim or task
Validate whether the P1076 diagnostic filters transfer beyond the blocker/carrier contrast without using rank/removal labels.

### Status
HYPOTHESIS

### Assumptions
- Toy p231/order-`11779` target-eliminated rank model.
- Same-target selected-source corpus; no fresh target artifacts are available in this branch.
- Filters are public but post-hoc; P1077 must treat them as frozen.

### Evidence so far
- P1076 filters route `20696_20703:20701` below rho once the P1075 blocker is filtered.
- P1075 simple routers alone had zero below-rho wins after excluding the P1073 winner window.

### Failure modes
- Filters may only encode the known carrier's salts/offset and fail on later windows.
- Filters may recover P1073/P1074 known positives but no new independent direction.
- Even a filter holdout success leaves columns `[6,7]` open.

### Next concrete action
Freeze the P1076 diagnostic filters and test them on held-out validation windows excluding both `20664_20671` and `20696_20703`; report whether any new column-`15`, `6`, or `7` direction appears below rho.

### Artifact paths
- `ecdlp_index_calculus_state/low_term_total2_p1076_p231_blocker_prefilter_audit_probe.json`
