---
id: KN-TECH-906e14
type: technique
title: >-
  Ring-curve trapdoors over Z/NZ (KMOV, Demytko, elliptic-curve Paillier and Okamoto-Uchiyama) -- the factorization of N as the trapdoor for the group order and for the additive kernel of reduction modulo p^2
tags: [trapdoor, ring-curve, kmov, demytko, paillier, okamoto-uchiyama, factoring, composite-modulus, kernel-of-reduction, anomalous, ecdlp]
confidence: reported
complexity: >-
  holder with the factorization computes #E(Z/NZ) = #E(F_p) * #E(F_q) by point counting on each factor (polynomial), and for N = p^2 q solves the p-part of the DLP by one division in the additive group E_1(Z/p^2 Z) = ker(reduction) ~ (F_p, +); outsider must factor N (NFS, L_N(1/3, 1.923)) or solve the DLP without the order
applicability: >-
  RSA-like settings where the modulus is a public product of secret primes; the security is that of factoring, and the schemes are encryption or signature systems rather than ECDLP hardness assumptions in their own right
source_refs: [KN-LIT-088, KN-TECH-6ead00, KN-OPEN-b9907c, KN-OPEN-9b71bb]
added: 2026-09-30
superseded_by: null
---

## Constructions (citations not yet filed as KN-LIT entries; all reported)

- **KMOV** (Koyama, Maurer, Okamoto, Vanstone, CRYPTO 1991, "New public-key
  schemes based on elliptic curves over the ring Z_n"): `E: y^2 = x^3 + b`
  over `Z/NZ` with `p, q = 2 mod 3` so that `#E(F_p) = p + 1`, `#E(F_q) = q + 1`
  regardless of `b`. Encryption is scalar multiplication by `e`; decryption
  uses `d = e^{-1} mod lcm(p+1, q+1)`. The trapdoor is the group order,
  known only through the factorization.
- **Demytko** (EUROCRYPT 1993): the same idea for general `a, b` using
  x-only arithmetic and the four twists to avoid the curve-order dependence
  on the message.
- **Elliptic-curve Paillier** (Galbraith, J. Cryptology 15(2), 2002,
  "Elliptic curve Paillier schemes") and the elliptic-curve
  **Okamoto-Uchiyama** variant: `N = p^2 q` (or `p^2`), and the kernel of
  reduction `E_1(Z/p^2 Z) -> E(F_p)` is isomorphic to the additive group of
  `F_p` via the formal group logarithm. A DLP whose base and target lie in
  that kernel is a division in `F_p`. This is exactly the mechanism of the
  Smart / Satoh-Araki / Semaev attack on anomalous curves (KN-LIT-088),
  reused constructively with the prime hidden inside `N`.

## Why they count as ECDLP trapdoors

Each is a family `Gen -> ((N, E, P), tau = (p, q))` on which the holder's
DLP-type problem is polynomial and the outsider's reduces to factoring. They
are the only *fielded* trapdoor systems whose object is literally an elliptic
curve group, which is why the taxonomy (KN-TECH-6ead00) keeps them even though
the hardness is factoring rather than any elliptic-curve problem.

## Detectability

`N` is visibly composite (it is published as a modulus). Nothing is hidden
about the *structure*; the secret is the factorization, and the public
attack is factoring. Special-form moduli `p^2 q` have dedicated attacks
(lattice methods of Peralta-Okamoto and Boneh-Durfee-Howgrave-Graham for
`p^r q`) that shrink but do not close the factoring gap at proper sizes.

## Applicability limits

- The holder's advantage is capped by the factoring assumption; no
  sub-factoring shortcut is known or claimed.
- These do **not** give a trapdoor on a prime-field curve: reduce mod one
  prime and the trapdoor disappears. They are therefore not candidates for
  GOAL-ECTD-001.
- The partially anomalous variant (E anomalous mod `p` only) halves the
  problem rather than solving it; KN-OPEN-b9907c records whether that half
  can be composed into a full trapdoor. The composite-*order* (not
  composite-modulus) variant is KN-OPEN-9b71bb.
