---
id: KN-LIT-2149
type: literature
title: "A New Keystream Generator MUGI Dai Watanabe1 , Soichi Furuya1 , Hirotaka Yoshida1"
authors:
  - "Kazuo Takaragi"
  - "Bart Preneel"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, implementation, pairing, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present a new keystream generator (KSG) MUGI, which is a variant of Panama proposed at FSE ’98. MUGI has a 128-bit secret key and a 128-bit initial vector as parameters and generates a 64-bit string per round.

## Key claims (as reported)
- The design is particularly suited for efficient hardware implementations, but the software performance of MUGI is excellent as well.
- A speed optimized implementation in hardware achieves about 3 Gbps with 26 Kgates, which is several times faster than AES.
- On the other hand the security was evaluated according to re-synchronization attack, related-key attack, and linear correlation of an output sequence.
- Our analysis confirms that MUGI is a secure KSG.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/23650181 (1).pdf`
- `downloads/23650181 (2).pdf`
- `downloads/23650181.pdf`
