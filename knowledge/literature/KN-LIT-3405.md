---
id: KN-LIT-3405
type: literature
title: "Deterring Certificate Subversion: Efficient Double-Authentication-Preventing Signatures"
authors:
  - "Mihir Bellare"
  - "Bertram Poettering"
  - "Douglas Stebila"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, protocol, provable-security, rsa, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present highly efficient double authentication preventing signatures (DAPS). In a DAPS, signing two messages with the same first part and differing second parts reveals the signing key.

## Key claims (as reported)
- In the context of PKIs we suggest that CAs who use DAPS to create certificates have a court-convincing argument to deny big-brother requests to create rogue certificates, thus deterring certificate subversion.
- We give two general methods for obtaining DAPS.
- Both start from trapdoor identification schemes.
- We instantiate our transforms to obtain numerous specific DAPS that, in addition to being efficient, are proven with tight security reductions to standard assumptions.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/101750114 (1).pdf`
- `downloads/101750114 (2).pdf`
- `downloads/101750114 (3).pdf`
- `downloads/101750114 (4).pdf`
- `downloads/101750114.pdf`
