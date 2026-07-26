---
id: KN-LIT-093
type: literature
title: Curve25519 - new Diffie-Hellman speed records
authors: [Bernstein Daniel J.]
year: 2006
venue: Public Key Cryptography - PKC 2006, LNCS 3958, pp. 207-228
identifiers:
  eprint: null
  doi: 10.1007/11745853_14
  url: https://cr.yp.to/ecdh/curve25519-20060209.pdf
tags: [curve25519, twist-security, cofactor, montgomery-curve, point-validation, parameter-selection, prime-field, safe-curves, ecdlp, hygiene]
confidence: established
citation_verified: read
added: 2026-07-24
superseded_by: null
---

## Contribution
Introduces Curve25519, the Montgomery curve y^2 = x^3 + 486662x^2 + x over
F_p with p = 2^255 - 19, and with it the design principle of *twist security*.
Rather than spending time rejecting inputs that lie on the quadratic twist,
the curve is chosen so that the twist is also cryptographically strong; every
32-byte string is then a valid public key and validation is free. The paper's
headline is speed (832457 Pentium III cycles), but the parameter-selection
argument is what matters for cryptanalysis.

## Key claims (as reported)
- Design rule stated explicitly: "Use a secure curve that also has a secure
  twist, rather than taking extra time to prohibit keys on the twist."
- The curve group has order 8 * p_1 and the twist group has order 4 * p_2 with
  both p_1 and p_2 prime (p_1 near 2^252); so the largest small-order
  confinement available to an attacker is cofactor 8 on the curve and 4 on the
  twist.
- Every known attack is claimed to cost more than a brute-force search on a
  128-bit symmetric key (conjectured, not proven -- the paper says
  "conjectured security level").

## Relevance to this program
Records the modern parameter-hygiene baseline against which "weak curve"
findings must be judged. Three consequences here. (1) Cofactor: the program's
baseline arithmetic is over the prime-order subgroup, and the cofactor 8 is
exactly the gap between #E and that subgroup order -- an off-by-cofactor error
in a rho count is an 8x mis-charge. (2) Twist: any mechanism that harvests
relations from x-coordinates alone is implicitly working on the union of curve
and twist, so its success probability must be charged over both groups. (3)
Scope: on a twist-secure curve, the invalid-curve and small-subgroup routes
(KN-LIT-091, KN-LIT-092) are closed by construction, which is why they are
adjacent-model results rather than ECDLP results. See KN-TECH-034.

## Not verified here
The full author PDF (cr.yp.to, 2006-02-09 version) was fetched and the
abstract, design-decision list, and the twist-group order discussion were read
directly; the cycle counts and the field-arithmetic sections were not checked.
Title, venue (PKC 2006, LNCS 3958, pp. 207-228), and DOI confirmed against the
IACR archive copy and an independent bibliographic record. The security level
is the author's conjecture, not a proven bound, and is recorded as such.
