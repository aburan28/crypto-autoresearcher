---
id: KN-LIT-2889
type: literature
title: "Chosen-Ciphertext Security from Identity-Based Encryption"
authors:
  - "Ran Canetti"
  - "Shai Halevi"
  - "Jonathan Katz"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [provable-security, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We propose a simple and efficient construction of a CCAsecure public-key encryption scheme from any CPA-secure identity-based encryption (IBE) scheme. Our construction requires the underlying IBE scheme to satisfy only a relatively “weak” notion of security which is known to be achievable without random oracles; thus, our results provide a new approach for constructing CCA-secure encryption schemes in the standard model.

## Key claims (as reported)
- Our approach is quite different from existing ones; in particular, it avoids non-interactive proofs of “well-formedness” which were shown to underlie most previous constructions.
- Furthermore, applying our conversion to some recently-proposed IBE schemes results in CCA-secure schemes whose efficiency makes them quite practical.
- Our technique extends to give a simple and reasonably efficient method for securing any binary tree encryption (BTE) scheme against adaptive chosen-ciphertext attacks.
- This, in turn, yields more efficient CCA-secure hierarchical identity-based and forward-secure encryption schemes in the standard model.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/eucrypt-camera (1).pdf`
- `downloads/eucrypt-camera (2).pdf`
- `downloads/eucrypt-camera.pdf`
