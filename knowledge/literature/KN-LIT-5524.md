---
id: KN-LIT-5524
type: literature
title: "On the Multiplicative Complexity of Boolean"
authors:
  - "Bitsliced Higher-Order Masking"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [finite-field, glv-gls, implementation, mpc, pairing, provable-security, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Higher-order masking is a widely used countermeasure to make software implementations of blockciphers achieve high security levels against side-channel attacks. Unfortunately, it often comes with a strong impact in terms of performances which may be prohibitive in some contexts.

## Key claims (as reported)
- This situation has motivated the research for efficient schemes that apply higher-order masking with minimal performance overheads.
- The most widely used approach is based on a polynomial representation of the cipher s-box(es) allowing the application of standard higher-order masking building blocks such as the ISW scheme (Ishai-Sahai-Wagner, Crypto 2003).
- Recently, an alternative approach has been considered which is based on a bitslicing of the s-boxes.
- This approach has been shown to enjoy important efficiency benefits, but it has only been applied to specific blockciphers such as AES, PRESENT, or custom designs.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/98130222 (1).pdf`
- `downloads/98130222.pdf`
