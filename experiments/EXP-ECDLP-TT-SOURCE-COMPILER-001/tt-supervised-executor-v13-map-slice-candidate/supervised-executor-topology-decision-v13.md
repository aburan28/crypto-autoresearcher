# Supervised Executor Topology Decision V13

## Status

`HYPOTHESIS` | `MODEL-BOUND` | `ZERO-RUN`

Decision: preserve V12's closed reducer and externalize only the E0 private-map
open result.

## deriveState ordering

```text
E0:evaluate reservation and capability
-> P001 action receipt plus private_map_open_intent
-> WAIT(private_map_open)
-> typed observation bound to P001 receipt and intent
-> observation-gateway private_map_open_observation
-> map_opened: P004 opened receipt, then live supervisor
-> map_open_failed: P003 failure terminal, then repository validation
```

`private_map_open_observation` adds `request_action_receipt_sha256`. Its subject
is the exact durable intent. `map_opened` yields the deterministic private-map
descriptor token; `map_open_failed` yields null.

## Selector conservation

The selector file remains byte-identical to V12. P001 supplies the durable
request. P002 is no-domain and unreachable from canonical V13 derivation,
because the reducer waits after P001 rather than constructing the historical
`open_syscall_success` source. P003 consumes a typed failure and writes only the
terminal. P004 consumes a typed success and writes the opened receipt.

The map-failure route enters repository validation directly, so it lacks the
ref observation normally created by P006, AN008, or AE008. G000 therefore
creates `ref_observation_pre` only when absent. This keeps P003 terminal-only
and gives both successful and failed E0 publication an explicit observed ref.

## Validation result

`OBSERVATION` | `MODEL-BOUND` | `ZERO-RUN`

Five traces replay to final lock release. The 70 inherited V12 controls and 19
focused V13 controls pass with exact preregistered rejections or publication
decisions. P002 is absent from every positive action journal and is explicitly
rejected at the post-P001 wait, while P001, P003, and P004 are each positively
exercised on their applicable branches.

Publication topology is now a separate pinned boundary: 227 exact payload
paths, no `-work` component, no AppleDouble or `.DS_Store` name, no symlink or
special file, and no self-selected omission. The immutable manifest will pin
the bytes after this path policy has fixed the set.

## Deferred topology

Restart evidence, process reconciliation, live Git effects, and infrastructure
finalization remain separate future slices.

## Next concrete action

Freeze only after independent Theory and Red Team review, exact payload-copy
verification, and publication-manifest validation. Typed restart and process
reconciliation remain the next unimplemented external-event slice.
