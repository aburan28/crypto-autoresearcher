---
id: KN-LIT-3229
type: literature
title: "Cryptanalysis of FIDES"
authors:
  - "Itai Dinur"
  - "Jérémy Jean"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
FIDES is a lightweight authenticated cipher, presented at CHES 2013. The cipher has two version, providing either 80-bit or 96bit security.

## Key claims (as reported)
- In this paper, we describe internal state-recovery attacks on both versions of FIDES, and show that once we recover the internal state, we can use it to immediately forge any message.
- Our attacks are based on a guess-and-determine algorithm, exploiting the slow diffusion of the internal linear transformation of FIDES.
- The attacks have time complexities of 275 and 290 for FIDES-80 and FIDES-96, respectively, use a very small amount of memory, and their most distinctive feature is their very low data complexity: the attacks require at most 24 bytes of an arbitrary plaintext and its corresponding ciphertext, in order to break the cipher with probability 1.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/85400138 (1).pdf`
- `downloads/85400138 (2).pdf`
- `downloads/85400138 (3).pdf`
- `downloads/85400138.pdf`
