# V1 Retraction: Secret-Derived Double-Orientation Fixture

Date: 2026-07-20

Status: `NEGATIVE RESULT / PRESERVED PREDECESSOR / CUSTODY FAILURE`

## Retracted experimental interpretation

The files with prefix `iso_double_orientation_schur_selector` correctly
exercise the simultaneous-intertwiner algebra, but they do not establish the
claimed public-input geometric recovery interface.

The degree-3 fixture constructs target torsion actions as

```text
[3]^(-1) phi alpha hat(phi)
```

using the withheld isogeny and its dual.  For the selected kernel, the first
source automorphism does not preserve the kernel, so this is a rational
quasi-endomorphism action on torsion rather than an independently available
integral target endomorphism.  The matrix selector does not read the secret,
but the acquisition oracle that produced its target matrices does.

The standalone verifier independently recomputes matrix and interpolation
self-consistency.  It does not independently reconstruct geometric transport
or compare the recovered map with a sealed secret isogeny.  A red-team
mutation can falsify the hidden-recovery booleans and truth hashes, recompute
the self-authenticating payload digest, and still pass the verifier.

## What remains valid

- The finite matrix counts `4 -> 2` modulo `5` and `8 -> 2` modulo `7` are
  correct for the supplied endpoint action matrices.
- The exhaustive module counts modulo `9` and `15` are correct.
- The centralizer theorem is independent of this fixture and remains valid.
- The v1 producer and verifier are retained as a negative example of why
  public-action custody and secret-aware verification must be separated.

## What is withdrawn

- “genuine transported endomorphisms” for the degree-3 fixture;
- “independent geometric verification” of transport and withheld-map
  equality;
- any protocol or deployment inference from the v1 target-action oracle.

## Replacement gate

The replacement experiment must use three processes: a secret instance
generator, a selector that reads only explicit public endpoint maps, and a
secret-aware verifier that reconstructs transport, the hidden sign orbit, and
the normalized map.  Submission evidence must come from that replacement,
not from v1.

