---
id: KN-LIT-6213
type: literature
title: "Relaxing Chosen-Ciphertext Security"
authors:
  - "Ran Canetti"
  - "Hugo Krawczyk"
  - "Jesper B. Nielsen"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, protocol, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Security against adaptive chosen ciphertext attacks (or, CCA security) has been accepted as the standard requirement from encryption schemes that need to withstand active attacks. In particular, it is regarded as the appropriate security notion for encryption schemes used as components within general protocols and applications.

## Key claims (as reported)
- Indeed, CCA security was shown to suffice in a large variety of contexts.
- However, CCA security often appears to be somewhat too strong: there exist encryption schemes (some of which come up naturally in practice) that are not CCA secure, but seem sufficiently secure “for most practical purposes.” We propose a relaxed variant of CCA security, called Replayable CCA (RCCA) security.
- RCCA security accepts as secure the non-CCA (yet arguably secure) schemes mentioned above; furthermore, it suffices for most existing applications of CCA security.
- We provide three formulations of RCCA security.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/27290563 (1).pdf`
- `downloads/27290563 (2).pdf`
- `downloads/27290563.pdf`
