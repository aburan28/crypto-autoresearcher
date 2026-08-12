---
id: KN-LIT-059
type: literature
title: Fiat-Shamir with Aborts - Applications to Lattice and Factoring-Based Signatures
authors: [Lyubashevsky Vadim]
year: 2009
venue: ASIACRYPT 2009, LNCS 5912, pp. 598-616
identifiers:
  eprint: null
  doi: 10.1007/978-3-642-10366-7_35
  url: https://link.springer.com/chapter/10.1007/978-3-642-10366-7_35
tags: [fiat-shamir-with-aborts, rejection-sampling, lattice-signature, dilithium, post-quantum, adjacent]
confidence: reported
citation_verified: web
added: 2026-07-23
superseded_by: null
---

## Contribution
Introduces the Fiat-Shamir-with-aborts / rejection-sampling paradigm for building
compact lattice-based (and factoring-based) signatures WITHOUT trapdoors.
Rejection sampling forces the signature distribution to be independent of the
secret, so transcripts leak nothing about the key.

## Key claims (as reported)
- Trapdoor-free lattice signatures via rejection sampling; the paradigm underlying
  Dilithium (KN-LIT-056).
- Secret-independent output distribution is the security-critical property.

## Relevance to this program
POST-QUANTUM construction, ADJACENT to the ECDLP mission. Recorded as context: the
second dominant lattice-signature paradigm (vs GPV hash-and-sign, KN-LIT-058).
NOTE a meaningful contrast with the ECDLP world: the secret-independent transcript
is exactly what defeats the nonce-leakage lattice attacks that break ECDSA
(KN-TECH-019) -- a design lesson from the discrete-log side carried into the
lattice side.

## Not verified here
Full paper not read; the rejection-sampling paradigm relayed from the abstract
(hence confidence: reported). No IACR ePrint located. Fields confirmed against the
Springer LNCS 5912 / DBLP records via search, not by fetching the primary page.
