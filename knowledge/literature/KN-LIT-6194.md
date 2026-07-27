---
id: KN-LIT-6194
type: literature
title: "Registered (Inner-Product) Functional Encryption Danilo Francati1[0000−0002−4639−0636] , Daniele Friolo2[0000−0003−0836−1735]"
authors:
  - "Monosij Maitra"
  - "Giulio Malavolta"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, hash, mpc, protocol, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Registered encryption (Garg et al., TCC’18) is an emerging paradigm that tackles the key-escrow problem associated with identitybased encryption by replacing the private-key generator with a much weaker entity known as the key curator. The key curator holds no secret information, and is responsible to: (i) update the master public key whenever a new user registers its own public key to the system; (ii) provide helper decryption keys to the users already registered in the system, in order to still enable them to decrypt after new users join the system.

## Key claims (as reported)
- For practical purposes, tasks (i) and (ii) need to be efficient, in the sense that the size of the public parameters, of the master public key, and of the helper decryption keys, as well as the running times for key generation and user registration, and the number of updates, must be small.
- In this paper, we generalize the notion of registered encryption to the setting of functional encryption (FE).
- As our main contribution, we show an efficient construction of registered FE for the special case of (attribute hiding) inner-product predicates, built over asymmetric bilinear groups of prime order.
- Our scheme supports a large attribute universe and is proven secure in the bilinear generic group model.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14438334 (1).pdf`
- `downloads/14438334.pdf`
