---
id: KN-LIT-2377
type: literature
title: "ALBATROSS: publicly AttestabLe BATched Randomness based On Secret Sharing"
authors:
  - "Ignacio Cascudo"
  - "Bernardo David∗"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper we present ALBATROSS, a family of multiparty randomness generation protocols with guaranteed output delivery and public verification that allows to trade off corruption tolerance for a much improved amortized computational complexity. Our basic stand alone protocol is based on publicly verifiable secret sharing (PVSS) and is secure under in the random oracle model under the decisional DiffieHellman (DDH) hardness assumption.

## Key claims (as reported)
- We also address the important issue of constructing Universally Composable randomness beacons, showing two UC versions of Albatross: one based on simple UC NIZKs and another one based on novel efficient “designated verifier” homomorphic commitments.
- Interestingly this latter version can be instantiated from a global random oracle under the weaker Computational Diffie-Hellman (CDH) assumption.
- An execution of ALBATROSS with n parties, out of which up to t = (1/2 − ) · n are corrupt for a constant  > 0, generates Θ(n2 ) uniformly random values, requiring in the worst case an amortized cost per party of Θ(log n) exponentiations per random value.
- We significantly improve on the SCRAPE protocol (Cascudo and David, ACNS 17), which required Θ(n2 ) exponentiations per party to generate one uniformly random value.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12491371 (1).pdf`
- `downloads/12491371.pdf`
