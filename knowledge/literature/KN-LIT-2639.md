---
id: KN-LIT-2639
type: literature
title: "Automated Meet-in-the-Middle Attack Goes to Feistel"
authors:
  - "Qingliang Hou"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, hash, pairing, signature, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Feistel network and its generalizations (GFN) are another important building blocks for constructing hash functions, e.g., Simpira v2, Areion, and the ISO standard Lesamnta-LW. The Meet-in-the-Middle (MitM) is a general paradigm to build preimage and collision attacks on hash functions, which has been automated in several papers.

## Key claims (as reported)
- However, those automatic tools mostly focus on the hash function with Substitution–Permutation network (SPN) as building blocks, and only one for Feistel network by Schrottenloher and Stevens (at CRYPTO 2022).
- In this paper, we introduce a new automatic model for MitM attacks on Feistel networks by generalizing the traditional direct or indirect partial matching strategies and also Sasaki’s multi-round matching strategy.
- Besides, we find the equivalent transformations of Feistel and GFN can significantly simplify the MILP model.
- Based on our automatic model, we improve the preimage attacks on Feistel-SP-MMO, Simpira-2/-4-DM, Areion-256/-512-DM by 1-2 rounds or significantly reduce the complexities.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14438211 (1).pdf`
- `downloads/14438211.pdf`
