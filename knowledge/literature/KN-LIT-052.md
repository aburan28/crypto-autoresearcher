---
id: KN-LIT-052
type: literature
title: NTRU - A Ring-Based Public Key Cryptosystem
authors: [Hoffstein Jeffrey, Pipher Jill, Silverman Joseph H.]
year: 1998
venue: ANTS-III 1998, LNCS 1423, pp. 267-288
identifiers:
  eprint: null
  doi: 10.1007/BFb0054868
  url: https://link.springer.com/chapter/10.1007/BFb0054868
tags: [ntru, ring-lattice, public-key, encryption, short-vectors, post-quantum, adjacent]
confidence: established
citation_verified: web
added: 2026-07-23
superseded_by: null
---

## Contribution
Introduces NTRU, a ring-based public-key encryption scheme in the truncated
polynomial ring Z[x]/(x^N - 1). Fast, with short easily-generated keys and low
memory; security rests on the difficulty of finding very short vectors in the
associated NTRU lattices.

## Key claims (as reported)
- Polynomial-algebra encryption with a probabilistic decryption-failure
  parameterization; efficient relative to number-theoretic public-key schemes.
- Security tied to short-vector problems in a structured lattice family (later the
  basis of the Falcon signature, KN-LIT-057).

## Relevance to this program
POST-QUANTUM scheme, ADJACENT to (not part of) the ECDLP mission. Recorded as
context: the NTRU lattice family is an intended replacement for ECDLP-based
public-key crypto and underlies a NIST signature standard. Its security is a
lattice short-vector question (KN-TECH-020, KN-TECH-022), unrelated to discrete
logs.

## Not verified here
Full paper not read; NTRU is textbook-level in lattice cryptography (hence
confidence: established). Fields confirmed against the Springer LNCS 1423 record
via search, not by fetching the primary page.
