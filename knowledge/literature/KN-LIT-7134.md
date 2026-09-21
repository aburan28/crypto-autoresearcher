---
id: KN-LIT-7134
type: literature
title: "Tight Security Bounds for Key-Alternating Ciphers"
authors:
  - "Shan Chen"
  - "John Steinberger⋆"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [provable-security, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A t-round key-alternating cipher (also called iterated Even-Mansour cipher ) can be viewed as an abstraction of AES. It defines a cipher E from t fixed public permutations P1 , . . . , Pt : {0, 1}n → {0, 1}n and a key k = k0 k · · · kkt ∈ {0, 1}n(t+1) by setting Ek (x) = kt ⊕ Pt (kt−1 ⊕ Pt−1 (· · · k1 ⊕ P1 (k0 ⊕ x) · · · )).

## Key claims (as reported)
- The indistinguishability of Ek from a truly random permutation by an adversary who also has oracle access to the (public) random permutations P1 , . . . , Pt was investigated in 1997 by Even and Mansour for t = 1 and for higher values of t in a series of recent papers.
- For t = 1, Even and Mansour proved indistinguishability security up to 2n/2 queries, which is tight.
- Much later Bogdanov et al.
- (2011) conjectured that security should t be 2 t+1 n queries for general t, which matches an easy distinguishing attack (so security cannot be more).

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/84410214 (1).pdf`
- `downloads/84410214 (2).pdf`
- `downloads/84410214 (3).pdf`
- `downloads/84410214.pdf`
