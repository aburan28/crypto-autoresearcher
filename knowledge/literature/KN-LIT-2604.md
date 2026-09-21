---
id: KN-LIT-2604
type: literature
title: "Atomic Secure Multi-Party Multiplication with Low Communication"
authors:
  - "Ronald Cramer"
  - "Ivan Damgård"
  - "Robbert de Haan"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [finite-field, mpc, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We consider the standard secure multi-party multiplication protocol due to M. This protocol is based on Shamir’s secret sharing scheme and it can be viewed as a practical variation on one of the central techniques in the foundational results of Ben-Or, Goldwasser, and Wigderson and Chaum, Crépeau, and Damgaard on secure multi-party computation.

## Key claims (as reported)
- Rabin’s idea is a key ingredient to virtually all practical protocols in threshold cryptography.
- Given a passive t-adversary in the secure channels model with synchronous communication, for example, secure multiplication of two secretshared elements from a finite field K based on this idea uses one communication round and has the network exchange O(n2 ) field elements, if t = Θ(n) and t < n/2 and if n is the number of players.
- This is because each of O(n) players must perform Shamir secret sharing as part of the protocol.
- This paper demonstrates that under a few restrictions much more efficient protocols are possible; even at the level of a single multiplication.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/45150329 (1).pdf`
- `downloads/45150329 (2).pdf`
- `downloads/45150329 (3).pdf`
- `downloads/45150329.pdf`
