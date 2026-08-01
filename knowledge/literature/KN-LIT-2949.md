---
id: KN-LIT-2949
type: literature
title: "Collision-based Power Analysis of Modular"
authors:
  - "Exponentiation Using Chosen-message Pairs"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [curve-arithmetic, implementation, provable-security, rsa, side-channel]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper proposes new chosen-message power-analysis attacks against public-key cryptosystems based on modular exponentiation, which use specific input pairs to generate collisions between squaring operations at different locations in the two power traces. Unlike previous attacks of this kind, the new attacks can be applied to all the standard implementations of the exponentiation process: binary (left-toright and right-to-left), m-ary, and sliding window methods.

## Key claims (as reported)
- The SPA countermeasure of inserting dummy multiplications can also be defeated (in some cases) by using the proposed attacks.
- The effectiveness of the attacks is demonstrated by actual experiments with hardware and software implementations of RSA on an FPGA and the PowerPC processor, respectively.
- In addition to the new collision generation methods, a high-accuracy waveform matching technique is introduced to detect the collisions even when the recorded signals are noisy and the clock has some jitter.

## Relevance to this program
Elliptic-curve/abelian-variety mathematics background for the program; relevant to curve arithmetic, point counting, and structural results underlying ECDLP instances.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/51540017 (1).pdf`
- `downloads/51540017 (2).pdf`
- `downloads/51540017 (3).pdf`
- `downloads/51540017.pdf`
