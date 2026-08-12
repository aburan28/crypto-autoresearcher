---
id: KN-LIT-2162
type: literature
title: "A New Structural-Differential Property of 5-Round AES"
authors:
  - "Lorenzo Grassi"
  - "Christian Rechberger"
  - "Sondre Rønjom"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
AES is probably the most widely studied and used block cipher. Also versions with a reduced number of rounds are used as a building block in many cryptographic schemes, e.g. several candidates of the SHA-3 and CAESAR competition are based on it.

## Key claims (as reported)
- So far, non-random properties which are independent of the secret key are known for up to 4 rounds of AES.
- These include differential, impossible differential, and integral properties.
- In this paper we describe a new structural property for up to 5 rounds of AES, differential in nature and which is independent of the secret key, of the details of the MixColumns matrix (with the exception that the branch number must be maximal) and of the SubBytes operation.
- It is very simple: By appropriate choices of difference for a number of input pairs it is possible to make sure that the number of times that the difference of the resulting output pairs lie in a particular subspace is always a multiple of 8.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10210215 (1).pdf`
- `downloads/10210215.pdf`
