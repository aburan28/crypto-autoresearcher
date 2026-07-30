---
id: KN-LIT-7252
type: literature
title: "Traitor-Tracing from LWE Made Simple and Attribute-Based"
authors:
  - "Yilei Chen"
  - "Vinod Vaikuntanathan"
  - "Brent Waters"
  - "Hoeteck Wee"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A traitor tracing scheme is a public key encryption scheme for which there are many secret decryption keys. Any of these keys can decrypt a ciphertext; moreover, even if a coalition of users collude, put together their decryption keys and attempt to create a new decryption key, there is an efficient algorithm to trace the new key to at least one the colluders.

## Key claims (as reported)
- Recently, Goyal, Koppula and Waters (GKW, STOC 18) provided the first traitor tracing scheme from LWE with ciphertext and secret key sizes that grow polynomially in log n, where n is the number of users.
- The main technical building block in their construction is a strengthening of (bounded collusion secure) secret-key functional encryption which they refer to as mixed functional encryption (FE).
- In this work, we improve upon and extend the GKW traitor tracing scheme: – We provide simpler constructions of mixed FE schemes based on the LWE assumption.
- Our constructions improve upon the GKW construction in terms of expressiveness, modularity, and security. – We provide a construction of attribute-based traitor tracing for all circuits based on the LWE assumption.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/11239214 (1).pdf`
- `downloads/11239214.pdf`
