# Experiment Contract: P1061 P231 Salt Family Independent Rank

## Hypothesis
A public salt-pair family selected only from calibration can broaden the P1059 exact row-key packet into a reusable below-rho source schedule. The family should find a non-anchor forward rank packet and ideally add cumulative target-eliminated rank beyond the P1059 anchor.

## Null hypothesis
Broader salt-pair families can recover non-anchor local packets, but those packets remain rank-dependent with the P1059 anchor or cost too much once charged under the public source policy.

## Parameters
- field/curve family: toy prime-field ECDLP harness, target `22050.cf1@11731`
- sizes: p231 state artifacts, order `11779`
- factor base: current order-`11779` target-eliminated factor namespace
- relation shape: direct-source certificates for `mode_low_term_support_total5`, `top_k=16`, clause `direct_source`
- base window rule: P1054 `(transfer_span >= 6) AND (mean_ops >= 0.72992701)`, P1056 `case_count <= 2`
- case-level family features: public row-key salt features `salt_min`, `salt_max`, `salt_gap`, `salt_sum`, high-salt flags, and priority-hit flags
- rule selection: calibration-only; require calibration rank gain at least `2` and calibration strict source charge below one rho; prefer single-condition non-equality salt-family rules over exact equality and two-condition rules
- anchor forward window: `18464_18471`

## Metrics
- group operations: strict source charge from `direct_ops_over_rho` for selected source cases
- memory: loaded certificate artifacts, selected windows, selected transfers, unique target-eliminated rows
- relation probability: usable direct-source certificates per selected case
- rank: local split rank gain and cumulative rank gain over the selected split union
- disjoint support: forward selected windows excluding `18464_18471`
- independence: cumulative forward-family rank gain minus P1059 anchor rank gain

## Positive control
The exact P1059 row-key prefix must reproduce the anchor below-rho packet: charge `0.83211679` rho and rank gain `2`.

## Negative control
P1060 exact row-key disjoint support remains empty on the P1056 forward split.

## Success criterion
P1061 is a strong positive only if the calibration-selected family has a non-anchor below-rho rank packet and cumulative forward-family rank gain strictly exceeds the P1059 anchor rank gain. It is a weaker positive precursor if a non-anchor below-rho packet exists but cumulative rank does not increase.

## Falsification criterion
P1061 is negative if no calibration-selected salt-family rule exists, no non-anchor forward packet is selected below rho, or the selected family fails the P1059 anchor control.

## Reproduction command
```bash
python3 tasks/ecdlp_index_calculus/low_term_total2_p1061_p231_salt_family_independent_rank.py \
  --contract ecdlp_index_calculus_state/experiment_contract_p1061_p231_salt_family_independent_rank.md \
  --out ecdlp_index_calculus_state/low_term_total2_p1061_p231_salt_family_independent_rank_probe.json
```

## Assumption and claim discipline
- `TOY-EVIDENCE`: p231/order-`11779` only.
- `MODEL-BOUND`: rank is measured inside the current verifier target-eliminated factor namespace.
- `CALIBRATION-SELECTED`: family rule selection uses calibration rank/charge only.
- `POLLARD-RHO-BOUNDARY`: below-rho source charge for one rank packet is not a complete ECDLP algorithm.
- `TARGET-DESCENT-BOUNDARY`: cumulative rank gain is still not individual-log descent unless remaining factor dependencies are resolved.

## Next concrete action
Build P1062 as a multi-family rank-diversity selector over salt-family candidates and charge only families that add independent rank directions.

## Results
- Status: `POSITIVE_SIGNAL_P1061_SALT_FAMILY_DISJOINT_PACKET_RANK_DEPENDENT`.
- Calibration-selected public family rule: `salt_sum >= 348`.
- Calibration result: selected transfer `10343`, strict charge `0.83211679` rho, rank gain `2`, charge per rank gain `0.4160584`.
- Exact P1059 anchor control: selected transfer `18465`, strict charge `0.83211679` rho, rank gain `2`.
- Non-anchor family packet: selected window `18688_18695`, transfer `18695`, strict charge `0.71532847` rho, local rank gain `1`, charge per rank gain `0.71532847`.
- Family forward union: selected windows `18464_18471` and `18688_18695`, strict charge `1.54744526` rho, cumulative rank gain `2`.
- Cumulative extra gain over the P1059 anchor: `0`.

## Interpretation
P1061 broadens the exact P1059 row key into a public salt-family selector and finds a real non-anchor below-rho rank packet. The limitation is rank dependence: the non-anchor packet does not add cumulative rank beyond the anchor in the current target-eliminated factor namespace. This is a positive relation-supply signal, not a collector closure.

## Failure modes and boundaries
- `WEAK-POSITIVE`: disjoint local packet exists below rho, but strict independent-rank success is false.
- `MODEL-BOUND`: rank dependence is measured only in the current order-`11779` target-eliminated factor namespace.
- `TARGET-DESCENT-BOUNDARY`: no individual-log descent is implemented.
- `NEXT POSITIVE QUESTION`: can a selector choose families by expected new pivot/free-column impact rather than by calibration charge density alone?
