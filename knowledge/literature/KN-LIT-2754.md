---
id: KN-LIT-2754
type: literature
title: "Blockcipher-based Authenticated Encryption: How Small Can We Go?"
authors:
  - "Avik Chakraborti"
  - "Tetsu Iwata"
  - "Kazuhiko Minematsu"
  - "Mridul Nandi"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [implementation, pairing, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper presents a design of authenticated encryption (AE) focusing on minimizing the implementation size, i.e., hardware gates or working memory on software. The scheme is called COFB, for COmbined FeedBack.

## Key claims (as reported)
- COFB uses an n-bit blockcipher as the underlying primitive, and relies on the use of a nonce for security.
- In addition to the state required for executing the underlying blockcipher, COFB needs only n/2 bits state as a mask.
- Till date, for all existing constructions in which masks have been applied, at least n bit masks have been used.
- Thus, we have shown the possibility of reducing the size of a mask without degrading the security level much.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10529228 (1).pdf`
- `downloads/10529228.pdf`
