---
id: KN-LIT-4087
type: literature
title: "Generic Compilers for Authenticated Key Exchange?"
authors:
  - "Tibor Jager"
  - "Florian Kohlar"
  - "Sven Schäge"
  - "Jörg Schwenk"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [protocol, signature, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
So far, all solutions proposed for authenticated key agreement combine key agreement and authentication into a single cryptographic protocol. However, in many important application scenarios, key agreement and entity authentication are clearly separated protocols.

## Key claims (as reported)
- This fact enables efficient attacks on the naı̈ve combination of these protocols.
- In this paper, we propose new compilers for two-party key agreement and authentication, which are provably secure in the standard BellareRogaway model.
- The constructions are generic: key agreement is executed first and results (without intervention of the adversary) in a secret session key on both sides.
- This key (or a derived key) is handed over, together with a transcript of all key exchange messages, to the authentication protocol, where it is combined with the random challenge(s) exchanged during authentication.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/6477232 (1).pdf`
- `downloads/6477232 (2).pdf`
- `downloads/6477232 (3).pdf`
- `downloads/6477232.pdf`
