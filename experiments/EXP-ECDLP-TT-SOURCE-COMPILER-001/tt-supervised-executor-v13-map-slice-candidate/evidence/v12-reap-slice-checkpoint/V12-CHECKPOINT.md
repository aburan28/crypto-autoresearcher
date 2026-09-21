# V12 Typed-Reap Observation Checkpoint

Status: `HYPOTHESIS` | `MODEL-BOUND` | `ZERO-RUN` |
`NOVELTY-UNVERIFIED`

Decision: `GO_FOR_PUBLICATION_STAGING` within the finite model.

This checkpoint closes only the typed spawn and typed reap observation
boundaries, including P0 spawn-failure and P0 runtime-failure commit paths. It
is not a runtime executor, campaign authorization, cryptanalytic result, or
ECDLP claim.

## Positive evidence

- Two clean traces, one P0 spawn-failure trace, and one P0 runtime-failure trace
  replay to final lock release.
- The traces contain 313 journal transitions and 688 final records.
- P0 runtime failure is observation-gateway authored, committed through the
  canonical failure envelope, and followed by committed E0 close.
- The independent verifier reports 482 checks over all four traces and all
  receipt-linked mutation inputs.
- Thirty semantic, 19 spawn, 16 reap, and five comparator/publication controls
  pass their registered first rejection or positive control.
- Stale same-rule reap requests and duplicate request/subject consumption are
  rejected by explicit bilateral invariants.

## Preserved negative evidence

The initial Red Team and Theory reviews both returned `NO_GO`. The Red Team
identified missing stale-request and duplicate-consumption controls; those
findings and repairs are preserved. The post-fix Red Team permits finite-model
publication staging. Theory found no remaining invariant defect and requires
the immutable publication root before final procedural approval.

## Open boundaries

- C004 is witnessed only for P0 spawn and runtime failure.
- Mutation receipts establish exact first rejection, not complete causal
  necessity.
- Map, restart, recovery reconciliation, process reconciliation, and live
  infrastructure finalization remain outside this slice.
- Rule totality, runtime implementation, campaign execution, and ECDLP
  relevance remain false.
- OS truthfulness, process identity, crash atomicity, filesystem durability,
  producer-key freshness, and live Git ref behavior remain outside the model.

## Byte anchors

- builder: `a2bd379ee14b9374584d7a15f372730b84d142d00c32ea7ca1b5ec16ac442be0`
- verifier: `63a0bf022e380870959d968b458bb09135a0be119e813a981c4aa984ef64a15c`
- selector: `2952bc3c3792eb3d43a4563ab4c6b7afa20922c0846a2a44f8b854bf873d2383`
- mandatory manifest: `3e963b2454fd3fff6bb533e1ec50df428ed5e2fed92cd9149af8970ac2dca4c8`
- closed kernel: `aab6fa3f555418eea5c2fd94305818d210a90f13a414f12d8e6d2f85806eb8b5`
- independent verification: `0d91ad662ebeeaf7c65617296ab870386ebc3bdf8f0d271effdf5107687a2ea8`
- semantic controls: `18bac9da043f7695bed73b7170891bdea4fde77fccf9ed329504a574170f37a8`
- spawn controls: `6ec602a79a4584b47b292319f729e8efb239f636bdb4b7ddc25a250191820b54`
- reap controls: `72d8780e6fac566095b19157b5463de3f02784d4cf2570aa14a406db934b6390`
- meta/publication controls: `c051390e2680fa3560284549182e6aa0464f2c224875d1e0a7671d9ac7dee98f`

## Next concrete action

Freeze this directory with exact manifest equality and an external SHA-256
root, then obtain the post-publication Theory decision before versioning a
typed E0 private-map observation.
