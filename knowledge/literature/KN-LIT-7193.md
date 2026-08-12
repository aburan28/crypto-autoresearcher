---
id: KN-LIT-7193
type: literature
title: "Toward Hierarchical Identity-Based Encryption"
authors:
  - "Jeremy Horwitz"
  - "Ben Lynn"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We introduce the concept of hierarchical identity-based encryption (HIBE) schemes, give precise definitions of their security and mention some applications. A two-level HIBE (2-HIBE) scheme consists of a root private key generator (PKG), domain PKGs and users, all of which are associated with primitive IDs (PIDs) that are arbitrary strings.

## Key claims (as reported)
- A user’s public key consists of their PID and their domain’s PID (in whole called an address).
- In a regular IBE (which corresponds to a 1-HIBE) scheme, there is only one PKG that distributes private keys to each user (whose public keys are their PID).
- In a 2-HIBE, users retrieve their private key from their domain PKG.
- Domain PKGs can compute the private key of any user in their domain, provided they have previously requested their domain secret key from the root PKG (who possesses a master secret).

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/hibe (1).pdf`
- `downloads/hibe (2).pdf`
- `downloads/hibe.pdf`
