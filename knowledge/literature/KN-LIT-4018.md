---
id: KN-LIT-4018
type: literature
title: "Functional Encryption against Probabilistic Queries: Definition, Construction and Applications"
authors:
  - "Geng Wang"
  - "Shi-Feng Sun"
  - "Zhedong Wang"
  - "Dawu Gu"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Functional encryption (FE for short) can be used to calculate a function output of a message, without revealing other information about the message. There are mainly two types of security definitions for FE, exactly simulation-based security (SIM-security) and indistinguishability-based security (IND-security).

## Key claims (as reported)
- Both of them have some limitations: FE with SIM-security supporting all circuits cannot be constructed for unbounded number of ciphertext and/or key queries, while IND-security is sometimes not enough: there are examples where an FE scheme is IND-secure but not intuitively secure.
- In this paper, we present a new security definition which can avoid the drawbacks of both SIM-security and IND-security, called indistinguishability-based security against probabilistic queries (pIND-security for short), and we give an FE construction for all circuits which is secure for unbounded key/ciphertext queries under this new security definition.
- We prove that this new security definition is strictly between SIM-security and IND-security, and provide new applications for FE which were not known to be constructed from IND-secure or SIM-secure FE.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/13940038 (1).pdf`
- `downloads/13940038.pdf`
