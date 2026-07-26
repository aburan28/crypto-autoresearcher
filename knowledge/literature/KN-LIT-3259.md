---
id: KN-LIT-3259
type: literature
title: "Cryptanalysis of Sosemanuk and SNOW 2.0 Using Linear Masks"
authors:
  - "Jung-Keun Lee"
  - "Dong Hoon Lee"
  - "Sangwoo Park"
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
In this paper, we present a correlation attack on Sosemanuk with complexity less than 2150 . Sosemanuk is a software oriented stream cipher proposed by Berbain et al. to the eSTREAM call for stream cipher and has been selected in the final portfolio.

## Key claims (as reported)
- Sosemanuk consists of a linear feedback shift register(LFSR) of ten 32-bit words and a finite state machine(FSM) of two 32-bit words.
- By combining linear approximation relations regarding the FSM update function, the FSM output function and the keystream output function, it is possible to derive linear approximation relations with correlation −2−21.41 involving only the keystream words and the LFSR initial state.
- Using such linear approximation relations, we mount a correlation attack with complexity 2147.88 and success probability 99% to recover the initial internal state of 384 bits.
- We also mount a correlation attack on SNOW 2.0 with complexity 2204.38 .

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/53500530 (1).pdf`
- `downloads/53500530 (2).pdf`
- `downloads/53500530 (3).pdf`
- `downloads/53500530.pdf`
