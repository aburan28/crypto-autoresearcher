---
id: KN-LIT-4db619
type: literature
title: "New Public-Key Schemes Based on Elliptic Curves over the Ring Z_n"
authors:
  - "Kenji Koyama"
  - "Ueli M. Maurer"
  - "Tatsuaki Okamoto"
  - "Scott A. Vanstone"
year: 1992
venue: "Advances in Cryptology -- CRYPTO '91, LNCS 576, pp. 252-266 (Springer, 1992)"
identifiers:
  eprint: null
  doi: "10.1007/3-540-46766-1_20"
  arxiv: null
  url: "https://link.springer.com/chapter/10.1007/3-540-46766-1_20"
tags: [kmov, ring-curve, composite-modulus, factoring, trapdoor-one-way-function, rsa-analogue, rabin-analogue, ecdlp]
confidence: reported
citation_verified: web
added: "2026-10-01"
superseded_by: null
---

## Contribution

Abstract (verbatim from the publisher page): "Three new trapdoor one-way
functions are proposed that are based on elliptic curves over the ring Zn.
The first class of functions is a naive construction, which can be used only
in a digital signature scheme, and not in a public-key cryptosystem. The
second, preferred class of function, does not suffer from this problem and
can be used for the same applications as the RSA trapdoor one-way function,
including zero-knowledge identification protocols. The third class of
functions has similar properties to the Rabin trapdoor one-way functions.
Although the security of these proposed schemes is based on the difficulty
of factoring n, like the RSA and Rabin schemes, these schemes seem to be
more secure than those schemes from the viewpoint of attacks without
factoring such as low multiplier attacks. The new schemes are somewhat less
efficient than the RSA and Rabin schemes."

The scheme usually called **KMOV** is the second class: curves
`y^2 = x^3 + b` over `Z/nZ` with `p, q = 2 (mod 3)`, so that
`#E(F_p) = p + 1` and `#E(F_q) = q + 1` independently of `b`, and the
trapdoor exponent is `d = e^{-1} mod lcm(p + 1, q + 1)`.

## Key claims (as reported)

- Security is explicitly the difficulty of factoring `n`; no elliptic-curve
  hardness assumption is made.
- The claimed advantage over RSA is resistance to "attacks without
  factoring" (low-exponent / low-multiplier attacks), not a stronger
  assumption. Later work (not read here) showed the KMOV variants are
  subject to analogues of several RSA attacks; treat the "more secure"
  claim as the authors' 1991 view.

## Relevance to this program

Primary source for the ring-curve entry `KN-TECH-906e14` and for the
"factorization of N" row of the hiding-criterion table in
`KN-TECH-6ead00`. It is the earliest *fielded* trapdoor system whose object
is literally an elliptic-curve group, which is why the taxonomy keeps it
although its hardness is factoring; it is **not** a candidate for the
prime-field question in `GOAL-ECTD-001`.
