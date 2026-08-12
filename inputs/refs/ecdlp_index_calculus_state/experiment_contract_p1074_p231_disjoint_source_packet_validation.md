# Experiment Contract: P1074 P231 Disjoint-Source Packet Validation

## Hypothesis
The P1073 frozen two-stage packet for target `22050.cf1@11731` is not only a single winning row artifact: either fresh-target selected-source artifacts exist for the same public policy, or the frozen `high_salt_max` top-k7 stage-2 ordering still removes column `15` below one rho after excluding the P1073 winning source case/window.

## Null hypothesis
Fresh-target artifacts are absent from the selected-source corpus, and the frozen P1073 `high_salt_max` ordering only wins because its known winning row/window is included. Once that row/window is removed, the first column-`15` removal is above rho or absent.

## Parameters
- field/curve family: toy prime-field ECDLP audit, target `22050.cf1@11731`, group order `11779`
- sizes: P1072 validation family `mode_low_term_support_total5/top7` after stage-1 window `20640_20647`
- seeds: selected-source row keys embedded in existing selected-source artifacts
- factor base: target-eliminated factor certificates from P1055/P1067/P1069/P1071/P1072/P1073 lineage
- relation shape: direct-source selected row-key certificates, public selector `mode_low_term_support_total5`, `top_k=7`
- baseline: P1073 all-validation `high_salt_max` first column-`15` prefix at `0.7810219` rho; generic rho is one normalized rho budget

## Metrics
- group operations: normalized direct source charge over rho
- field operations: inherited from selected-source certificate generation; no fresh field-op backend in this probe
- memory: number of selected artifacts, factor artifacts, validation refs, and windows
- relation probability: number of disjoint windows/cases with marginal rank or column removal
- rank: marginal rank gain over the stage-1 packet
- solver degree: not tested in this packet-level audit
- wall-clock: not the primary metric; artifact hashes and operation counters are primary

## Positive control
The all-validation P1073 `high_salt_max` ordering must reproduce column `15` removal at prefix length `1` and below one rho.

## Negative control
The fresh-target scan must report no target other than `22050.cf1@11731` if the selected-source corpus is single-target. Excluding the P1073 winning row/window is the strict disjoint control.

## Success criterion
P1074 is strictly positive only if at least one of these holds:
- selected-source artifacts contain a fresh target suitable for the same frozen policy and the policy removes an analogous target-descent column below rho; or
- excluding the P1073 winning case still removes column `15` below one rho; or
- excluding the P1073 winning window still removes column `15` below one rho.

## Falsification criterion
P1074 is a strict negative if the corpus has no fresh target artifacts and both case-excluded and window-excluded frozen-policy scans first remove column `15` only at `>= 1.0` rho or never.

## Reproduction command
```bash
python3 tasks/ecdlp_index_calculus/low_term_total2_p1074_p231_disjoint_source_packet_validation.py \
  --contract ecdlp_index_calculus_state/experiment_contract_p1074_p231_disjoint_source_packet_validation.md \
  --out ecdlp_index_calculus_state/low_term_total2_p1074_p231_disjoint_source_packet_validation_probe.json
```

## Claim status taxonomy
- `HYPOTHESIS`: disjoint-source validation of the P1073 packet.
- `MODEL-BOUND`: toy p231/order-`11779` target-eliminated rank model.
- `TOY-EVIDENCE`: no cryptographic-scale claim.
- `POLLARD-RHO-BOUNDARY`: success is defined against one normalized rho budget.
- `TARGET-DESCENT-OPEN`: columns `[6,7]` remain open even if column `15` validates.

## Results
- claim: `OBSERVATION_P1074_DISJOINT_COLUMN15_SINGLE_EXISTS_BUT_POLICY_FAILS_STRICT_SPLIT`
- strict success: `false`
- weak success: `true`
- fresh targets in selected-source corpus after promotion: `0`; target inventory has `1530` post-promotion selected cases, all `22050.cf1@11731`
- positive control: all-validation `high_salt_max` removes column `15` at prefix length `1`, charge `0.7810219` rho
- strict disjoint controls: excluding the P1073 winner case or winner window first removes column `15` at prefix length `16`, charge `12.21167887` rho
- future-after-winner control: first column-`15` removal at prefix length `11`, charge `8.43065696` rho
- weak positive: disjoint window-local carrier `20696_20703:20701`, row keys `[22050.cf1@11731:uniform:256:salt165, 22050.cf1@11731:uniform:256:salt170]`, charge `0.75182482` rho, marginal rank `1`, removed `[15]`, remaining `[6,7]`

## Interpretation
P1074 does not validate the P1073 frozen global policy on a disjoint source split. It does show that the column-`15` direction is not unique to the P1073 winner window: a separate window has a below-rho single-row carrier. The missing layer is public routing to that carrier without rank/removal labels.

## Handoff: P1075 public window-router audit

### Claim or task
Test whether simple public case/window metadata can route to `20696_20703:20701` below rho after excluding the P1073 winner window.

### Status
HYPOTHESIS

### Assumptions
- Toy p231/order-`11779` target-eliminated rank model.
- Same-target selected-source corpus only; no fresh target artifacts are available in this branch.
- Router keys may use public salts, offsets, direct source charge, support size, priority-hit counts, and window aggregates, but not rank/removal labels.

### Evidence so far
- P1074 window-local carrier charge is `0.75182482` rho.
- Frozen global `high_salt_max` reaches it only at `12.21167887` rho after excluding the P1073 winner.

### Failure modes
- A router catalog may overfit the discovered carrier.
- Direct source charge may be public but still insufficient as a global ordering.
- Even a successful column-`15` router leaves columns `[6,7]` open.

### Next concrete action
```bash
python3 tasks/ecdlp_index_calculus/low_term_total2_p1075_p231_public_window_router.py --contract ecdlp_index_calculus_state/experiment_contract_p1075_p231_public_window_router.md --out ecdlp_index_calculus_state/low_term_total2_p1075_p231_public_window_router_probe.json
```

### Artifact paths
- `ecdlp_index_calculus_state/low_term_total2_p1074_p231_disjoint_source_packet_validation_probe.json`
