# Result Summary

## Main result

For `A = 2^a` and every `c = 1 mod 4`, the POKE-4D ambiguity

```text
x1^2 + x2^2 = c (mod A)
```

contains exactly `2^(a+1) = 2A` ordered pairs.  The pairs can be streamed in
`O(A poly(a))` bit operations and polynomial working space.

After Moriya's generalized MOXZ normalization for strong masked-degree CIST,
the correct pair is `(alpha*q1, alpha*q2)`.  Each enumerated pair determines the
scaled Kani matrix and candidate subgroup.  Conditional on the charged
fixed-dimensional candidate-reconstruction interface, trying every pair solves
the search problem in

```text
2^(a+1) * C_HD(2^a,p) + O(2^a poly(a,log p)).
```

The paper keeps `C_HD` explicit; the arithmetic artifact does not implement or
benchmark the higher-dimensional recovery routine.

## Cryptographic implication

Snake Mackerel's two published level-I primes both use `a = 75`, so the exact
outer candidate list has size `2^76`.  In OW-KCA this is an exhaustive
candidate-recognition bound: after a candidate secret/key is reconstructed, the
oracle recognizes whether it matches the honest challenge key.  Under random
candidate order and distinct candidate-key classes, the expected number of
recognitions is about `2^75`.

This is not a logarithmic-query direction recovery, a passive attack, a measured
`2^76`-bit-operation implementation, or a general isogeny, SCALLOP, or ECDLP
improvement.

## Evidence

- Formal exact-count proof via the norm map on `(Z/2^a Z)[i]`.
- Output-sensitive binary lifting algorithm.
- 24 exact positive runs over `a = 4,6,...,18` and three seeds.
- 24 matched `c = 3 mod 4` negative controls.
- Independent verifier passes every count, sample, lift, mutation, and parameter
  translation check.
- Producer scientific SHA-256:
  `17259548d869b828c2892b153a166908dbca4c3db42c34cc849708ce3c592dc5`.
- Verifier scientific SHA-256:
  `261872d818566752c1543eed9c4f87d6124f06fd3366a352e21944840287f7eb`.
