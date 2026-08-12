# V11 Spawn-Observation Checkpoint

Status: `HYPOTHESIS` | `MODEL-BOUND` | `ZERO-RUN` |
`NOVELTY-UNVERIFIED`

Decision: `GO_FOR_NEXT_TYPED_EVENT` within the finite model.

This checkpoint closes only the P0 typed-spawn/failure-commit vertical slice.
It is not a runtime executor, campaign authorization, cryptanalytic result, or
ECDLP claim.

## Positive evidence

- Two clean traces and one P0 spawn-failure trace replay to final lock release.
- The traces contain 260 journal transitions and 589 final records in total.
- P0 spawn failure is authored by the observation gateway, committed through a
  canonical failure envelope, followed by committed E0 close.
- The independent verifier reports 226 checks over all three traces.
- Nineteen focused controls, 30 inherited semantic controls, and five
  comparator/publication controls pass their preregistered first rejection.

## Repaired negative evidence

The static red team found that the reviewed builder accepted an empty
observation context while the verifier rejected it. The finding is preserved in
`supervised-executor-v11-static-red-team-review.md`.

The repaired reducers now compare context exactly, require every non-fixed
selector field explicitly, and reject a direct phase-spawn producer forgery.
Fresh receipts are required for these repaired bytes.

## Open boundaries

- C004 has a positive witness only for P0 spawn failure. Later-phase,
  runtime-failure, quarantine, and failed-E0-close shapes are untested.
- Mutation receipts establish exact first rejection, not causally regenerated
  predicate necessity.
- Map, reap, restart, recovery reconciliation, and infrastructure observations
  remain outside the slice.
- Rule totality, predicate classification, runtime implementation, campaign
  execution, and ECDLP relevance remain false.
- OS truthfulness, process identity, crash atomicity, filesystem durability, and
  live Git ref behavior remain outside the finite model.

## Byte anchors

- builder: `d5e05b497f8337a9407736cb9c76f1d7f675ea05d1159658ef3af35f94aa5e45`
- verifier: `278243881e8f10b2f1d70ac6eb0d61d0a16c9df7748b45239b964d37713a3006`
- selector: `2952bc3c3792eb3d43a4563ab4c6b7afa20922c0846a2a44f8b854bf873d2383`
- mandatory manifest: `18825a50259698eafab3df7c913f7d65a5ce0c3439ddef3c976168f97314219a`
- closed kernel: `5b35c76d4eb00b13fc18690fe09e8a162f03f513bbfbed844a7df562dcbd3959`
- independent verification: `92f16d2c35625527b8e35dde38d714e23a618c591ccfeffba805c2ae6cb23db6`
- focused controls: `e818bfd633e27947630354090fe57aa6ab9282d4dfeca881c87071b01ffe9def`
- semantic controls: `9f3cfa812c2574d760100b00b720c926ce32c8428e972dd985f682b7efb87cd0`
- meta/publication controls: `984f7823bbdd3e59f8b364d9dcc43113579bdffc297c010c5e7392e9687ab866`

## Next concrete action

Freeze this directory with exact manifest equality and an external SHA-256
root, then version a typed P0 reap observation and nonzero-exit failure trace.
