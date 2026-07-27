---
id: KN-LIT-6631
type: literature
title: "SIGMA: the ‘SIGn-and-MAc’ Approach to Authenticated Diffie-Hellman and its Use in the IKE Protocols"
authors:
  - "Hugo Krawczyk"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, pollard-rho, protocol, quantum, signature, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present the SIGMA family of key-exchange protocols and the “SIGn-and-MAc” approach to authenticated Diffie-Hellman underlying its design. The SIGMA protocols provide perfect forward secrecy via a Diffie-Hellman exchange authenticated with digital signatures, and are specifically designed to ensure sound cryptographic key exchange while providing a variety of features and trade-offs required in practical scenarios (such as optional identity protection and reduced number of protocol rounds).

## Key claims (as reported)
- As a consequence, the SIGMA protocols are very well suited for use in actual applications and for standardized key exchange.
- In particular, SIGMA serves as the cryptographic basis for the signaturebased modes of the standardized Internet Key Exchange (IKE) protocol (versions 1 and 2).
- This paper describes the design rationale behind the SIGMA approach and protocols, and points out to many subtleties surrounding the design of secure key-exchange protocols in general, and identity-protecting protocols in particular.
- We motivate the design of SIGMA by comparing it to other protocols, most notable the STS protocol and its variants.

## Relevance to this program
Bears on the generic baseline (Pollard rho / generic-group lower bounds) against which every candidate algorithm in this program is benchmarked.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/27290399 (1).pdf`
- `downloads/27290399 (2).pdf`
- `downloads/27290399.pdf`
