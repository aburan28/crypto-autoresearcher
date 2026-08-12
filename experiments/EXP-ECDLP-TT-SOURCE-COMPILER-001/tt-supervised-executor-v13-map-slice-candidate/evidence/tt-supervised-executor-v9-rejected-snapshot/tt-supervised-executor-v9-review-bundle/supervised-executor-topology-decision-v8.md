# Supervised Executor Topology Decision V8 For V9

## Status

`HYPOTHESIS` | `MODEL-BOUND` | `ZERO-RUN`

Decision: use one closed event-sourced reducer for V9. Do not implement runtime
schemas and do not run the campaign from this decision alone.

## Rejected Topology

V8 split authority between caller-supplied source fields and a partially checked
record array. Its traces carried records forward but called `sourceFor` again at
every step. The local builder and verifier therefore shared semantic omissions.

## Selected Topology

```text
typed root records
        |
        v
canonicalRecordUniverse
        |
        v
closed envelope, path, payload, producer, and linkage validation
        |
        v
replay digest-linked action and observation receipts
        |
        v
deriveState(canonical records, replayed context)
        |
        v
reconstruct exact selector schema and source
        |
        v
select one inherited rule
        |
        v
append exact domain delta plus transition receipt
```

`deriveState` receives no source object. Full source snapshots are forbidden.
The unchanged 153-rule selector matrix is data, not a source oracle.

## State Domains

The reducer indexes:

- campaign root and recovery approval;
- contiguous admission/start/end identities;
- active reservation and committed phase chain;
- executable, capability, private-map, launch, process, result, content, and
  terminal links;
- literal Git objects and pre/CAS/post ref observations;
- closure request, lifetimes, measurements, receipts, recalculation, and lock
  release;
- one journal cursor derived from predecessor-bound receipts.

The reconstructed result is one of:

- `READY`: exact source and selector context are derivable;
- `WAIT`: one typed external observation is required;
- `COMPLETE`: the exact final lock release is durable.

## Context Handoff

The selected rule determines the next context. An action receipt durably binds
that context even when the action has no domain record. An observation receipt
cannot change context. Replaying or deleting either receipt breaks the journal
chain.

## End-To-End Coverage

Two complete traces are required:

- A0 normal flow;
- A2 recovery flow with closed A0/A1 history.

Both traverse P0-P5, E0, literal Git publication, cumulative meter accounting,
campaign terminal, recalculation, and final lock release. This replaces V8's
short independently reseeded trace fragments.

## Independent Verification

The verifier does not import builder code. It hardcodes the closed vocabulary,
re-indexes every prefix, reconstructs each selector source, checks rule/action
and context transitions, validates domain-type deltas, and independently runs
all mutation operations. Builder verdict fields are treated as untrusted data.

## Strongest Valid Claim

If the generated traces and every regression pass independent verification, V9
supports a restricted finite-model claim: those canonical workflows replay into
the inherited selector rules without source reseeding, open record authority,
disconnected Git history, or unbound resource/capability evidence.

It does not establish runtime enforcement, campaign safety, an ECDLP algorithm,
or an exponent improvement.

## Next Concrete Action

Independently verify, deterministically rebuild, freeze exact hashes, and submit
the immutable V9 bundle to fresh Theory and Red Team review.
