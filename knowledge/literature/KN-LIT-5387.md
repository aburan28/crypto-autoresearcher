---
id: KN-LIT-5387
type: literature
title: "On Randomizing Hash Functions to Strengthen the Security of Digital Signatures"
authors:
  - "Praveen Gauravaram⋆⋆"
  - "Lars R. Knudsen"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, rsa, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Halevi and Krawczyk proposed a message randomization algorithm called RMX as a front-end tool to the hash-then-sign digital signature schemes such as DSS and RSA in order to free their reliance on the collision resistance property of the hash functions. They have shown that to forge a RMX-hash-then-sign signature scheme, one has to solve a cryptanalytical task which is related to finding second preimages for the hash function.

## Key claims (as reported)
- In this article, we will show how to use Dean’s method of finding expandable messages for finding a second preimage in the MerkleDamgård hash function to existentially forge a signature scheme based on a t-bit RMX-hash function which uses the Davies-Meyer compression functions (e.g., MD4, MD5, SHA family) in 2t/2 chosen messages plus 2t/2+1 off-line operations of the compression function and similar amount of memory.
- This forgery attack also works on the signature schemes that use Davies-Meyer schemes and a variant of RMX published by NIST in its Draft Special Publication (SP) 800-106.
- We discuss some important applications of our attack.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/54790091 (1).pdf`
- `downloads/54790091 (2).pdf`
- `downloads/54790091 (3).pdf`
- `downloads/54790091.pdf`
