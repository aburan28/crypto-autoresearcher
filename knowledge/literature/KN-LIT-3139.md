---
id: KN-LIT-3139
type: literature
title: "Constructing Rate-1 MACs from Related-Key"
authors: []
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mov-fr, pairing, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Almost all current block-cipher-based MACs reduce their security to the pseudorandomness of their underlying block ciphers, except for a few of them to the unpredictability, a strictly weaker security notion than pseudorandomness. However, the latter MACs offer relatively low efficiency.

## Key claims (as reported)
- In this paper, we investigate the feasibility of constructing rate-1 MACs from related-key unpredictable block ciphers.
- First, we show all the existing rate-1 MACs are insecure when instantiated with a special kind of related-key unpredictable block cipher.
- The attacks on them inspire us to propose an assumption that all the chaining values are available to adversaries for theoretically analyzing such MACs.
- Under this assumption, we study the security of 64 rate-1 MACs in keyed PGV model, and find that 1) 15 MACs are meaningless; 2) 25 MACs are vulnerable to three kinds of attacks respectively and 3) 24 MACs are provably secure when their underlying block ciphers are related-key unpredictable.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/61470255 (1).pdf`
- `downloads/61470255 (2).pdf`
- `downloads/61470255 (3).pdf`
- `downloads/61470255.pdf`
