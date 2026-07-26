---
id: KN-LIT-7281
type: literature
title: "Tweaks and Keys for Block Ciphers: the TWEAKEY Framework"
authors:
  - "Jérémy Jean"
  - "Ivica Nikolić"
  - "Thomas Peyrin"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, finite-field, hash, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We propose the TWEAKEY framework with goal to unify the design of tweakable block ciphers and of block ciphers resistant to relatedkey attacks. Our framework is simple, extends the key-alternating construction, and allows to build a primitive with arbitrary tweak and key sizes, given the public round permutation (for instance, the AES round).

## Key claims (as reported)
- Increasing the sizes renders the security analysis very difficult and thus we identify a subclass of TWEAKEY, that we name STK, which solves the size issue by the use of finite field multiplications on low hamming weight constants.
- Overall, this construction allows a significant increase of security of well-known authenticated encryptions mode like ΘCB3 from birthday-bound security to full security, where a regular block cipher was used as a black box to build a tweakable block cipher.
- Our work can also be seen as advances on the topic of secure key schedule design.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/88730185 (1).pdf`
- `downloads/88730185 (2).pdf`
- `downloads/88730185 (3).pdf`
- `downloads/88730185.pdf`
