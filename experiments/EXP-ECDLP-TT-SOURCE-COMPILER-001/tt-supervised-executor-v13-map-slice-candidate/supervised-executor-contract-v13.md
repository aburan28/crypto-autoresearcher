# Experiment Contract: V13 Typed Private-Map Observation

## Status

`HYPOTHESIS` | `MODEL-BOUND` | `ZERO-RUN` | `NOVELTY-UNVERIFIED`

V13 extends the immutable V12 checkpoint rooted at
`98dba44fb4e79fd4d156a04ec6a528d2fa98d528d8e7c8fa16f18f58fa4c60da`.
It does not modify or reinterpret those bytes.

## Hypothesis

The P001 action receipt and its `private_map_open_intent` domain record can be
the durable request for exactly one typed private-map observation. The gateway
can then produce either `map_opened` or `map_open_failed` without any selector
source asserting an unobserved syscall result.

## Null hypothesis

The split permits an action-authored result, stale or duplicate consumption,
cross-intent binding, map observation during E0 close mode, descriptor/value
disagreement, builder/verifier divergence, or an uncommittable E0 map failure.

## Parameters

- model: finite event-sourced closed reducer;
- predecessor: immutable V12 reap-slice checkpoint;
- run modes: normal A0 and recovery A2;
- affected context: E0 private-map evaluation only;
- request: P001 action receipt plus exact open-intent subject;
- new observation kind: `private_map_open`;
- observation values: `map_opened`, `map_open_failed`;
- positive traces: inherited four traces plus E0 map-open failure;
- baseline: V12 four-trace artifact and 70-control checkpoint.

## Metrics

- canonical trace count and journal transitions;
- exact final-universe digests;
- builder/verifier replay parity;
- inherited and focused mutation counts;
- P002 positive reachability after externalization;
- E0 map-failure commit and closure path;
- publication payload equality at freeze.

## Positive control

Clean A0 and A2 traces must preserve terminal behavior with `map_opened` typed
observations, and all V12 failure traces must remain replayable.

## Negative control

A private-map observation over E0 close mode or an already consumed P001
request must reject before selector progression.

## Success criterion

- P001 writes the intent and becomes the exact request receipt.
- Derivation waits after the intent until one typed observation is present.
- `private_map_open_observation` is authored only by `observation_gateway` and
  binds the P001 receipt plus exact intent.
- P002 produces no domain record and is unreachable from canonical V13 state.
- P003 writes only the map-failure terminal over typed failed observation.
- The E0 failure trace commits E0 failure and reaches final lock release.
- Both reducers agree on all positive traces and registered mutations.
- All 70 V12 controls replay under exact V13 bytes.
- Publication verification is bound to an exact pinned path set and payload
  count, with metadata and `-work` paths rejected independently of manifest
  equality.

## Falsification criterion

Any accepted wrong request, wrong intent, duplicate or missing consumer,
cross-ordinal result, E0-close observation, action-authored result,
value/domain mismatch, success receipt over failure, or reducer disagreement
narrows or rejects the hypothesis.

## Results

`OBSERVATION` | `MODEL-BOUND` | `ZERO-RUN`

- Five canonical traces complete in 422 journal transitions and 927 final
  records: clean A0, recovery A2, P0 spawn failure, P0 runtime failure, and E0
  private-map failure.
- The selector remains byte-identical to V12. No positive trace selects P002.
- Clean map opens and the E0 map failure are gateway-authored observations
  bound to the exact P001 action receipt and open intent.
- P003 emits exactly one domain record, the failure terminal over the typed
  failed observation.
- The exceptional P003 route reaches repository validation without the usual
  P006 ref observation. G000 now creates `ref_observation_pre` only when it is
  absent, before constructing the failure commit. Ordinary phase paths retain
  their existing P006/AN008/AE008 observation.
- All 70 inherited V12 controls and 19 focused V13 controls pass. The focused
  set contains 17 map/state mutations plus missing-required-payload and
  listed-AppleDouble publication controls.
- Publication policy `publication-payload-policy-v13.json` pins exactly 227
  required payload paths. Persistent mutation inputs live under four
  non-`work` trees; every path component ending in `-work`, every AppleDouble
  name, `.DS_Store`, symlink, special file, unlisted file, and missing required
  file is rejected.
- The initial Red Team staging `NO_GO` and the first failed policy-label run
  are preserved as required payloads. The mandatory manifest remains
  publication closed until immutable staging and post-freeze reviews complete.

## Interpretation

The hypothesis is supported inside the finite event-sourced model. This closes
one authority gap: selector actions no longer author the E0 private-map syscall
result. It does not establish operating-system truthfulness, crash atomicity,
runtime implementation correctness, campaign safety, or any ECDLP result.

## Excluded claims

- restart and process reconciliation;
- live meter and infrastructure observations;
- runtime descriptor truthfulness, filesystem durability, and live Git effects;
- implementation or campaign authorization;
- any cryptanalytic or ECDLP improvement.

## Reproduction command

```bash
node build_v13_closed_kernel.mjs
node verify_v13_closed_kernel.mjs
node run_semantic_regressions_v13.mjs
node run_spawn_failure_regressions_v13.mjs
node run_reap_failure_regressions_v13.mjs
node run_map_failure_regressions_v13.mjs
node run_meta_publication_regressions_v13.mjs
```

## Next concrete action

Obtain a post-repair Red Team staging decision, then create and verify the
exact 227-payload immutable V13 map-slice checkpoint before beginning typed
restart and process reconciliation.
