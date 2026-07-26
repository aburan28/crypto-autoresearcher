---
id: KN-LIT-6516
type: literature
title: "Security of Full-State Keyed Sponge and Duplex: Applications to Authenticated Encryption"
authors:
  - "Bart Mennink"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, rsa, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We provide a security analysis for full-state keyed Sponge and full-state Duplex constructions. Our results can be used for making a large class of Sponge-based authenticated encryption schemes more efficient by concurrent absorption of associated data and message blocks.

## Key claims (as reported)
- In particular, we introduce and analyze a new variant of SpongeWrap with almost free authentication of associated data.
- The idea of using full-state message absorption for higher efficiency was first made explicit in the Donkey Sponge MAC construction, but without any formal security proof.
- Recently, Gaži, Pietrzak and Tessaro (CRYPTO 2015) have provided a proof for the fixed-output-length variant of Donkey Sponge.
- Yasuda and Sasaki (CT-RSA 2015) have considered partially full-state Sponge-based authenticated encryption schemes for efficient incorporation of associated data.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/94520227 (1).pdf`
- `downloads/94520227.pdf`
