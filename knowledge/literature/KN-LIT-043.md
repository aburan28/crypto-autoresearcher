---
id: KN-LIT-043
type: literature
title: Hardness of Computing the Most Significant Bits of Secret Keys in Diffie-Hellman and Related Schemes (Hidden Number Problem)
authors: [Boneh Dan, Venkatesan Ramarathnam]
year: 1996
venue: CRYPTO 1996, LNCS 1109, pp. 129-142
identifiers:
  eprint: null
  doi: 10.1007/3-540-68697-5_11
  url: https://link.springer.com/chapter/10.1007/3-540-68697-5_11
tags: [hidden-number-problem, hnp, lattice, cvp, diffie-hellman, bit-security, ecdlp-adjacent, cryptanalysis]
confidence: established
citation_verified: web
added: 2026-07-23
superseded_by: null
---

## Contribution
Introduces the Hidden Number Problem (HNP): recover a hidden s mod p given, for
known random multipliers t_i, the most significant bits of s*t_i mod p. Shows HNP
is solvable in polynomial time by reducing it to a lattice closest-vector (CVP)
problem plus lattice basis reduction, given enough MSBs.

## Key claims (as reported)
- Computing the ~sqrt(log p) most significant bits of a Diffie-Hellman shared
  secret is as hard as computing the whole secret (bit-security of DH MSBs).
- Extends to ElGamal, Shamir message passing, Okamoto conference keys; proposes a
  DH variant with a provably hard single MSB.

## Relevance to this program
The foundational lattice tool of the entire nonce-leakage attack family, and the
theoretical root of the lattice/ECDLP intersection. The HNP-to-CVP reduction is
exactly what later work (KN-LIT-044, KN-LIT-045) turns against elliptic-curve
discrete-log signatures (ECDSA) when nonce bits leak. NOTE: this attacks the
signature/leakage layer via lattices, NOT the plain ECDLP itself -- the
distinction the program should preserve (KN-OPEN-011). Uses lattice reduction
(KN-TECH-020) and is adjacent to Coppersmith small-roots (KN-LIT-037).

## Not verified here
Full paper not read; the HNP definition and CVP reduction are textbook-level in
lattice cryptanalysis (hence confidence: established). Predates the IACR ePrint
archive. Bibliographic fields confirmed against the Springer/DBLP records via
search, not by fetching the primary page.
