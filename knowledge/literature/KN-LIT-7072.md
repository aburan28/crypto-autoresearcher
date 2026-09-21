---
id: KN-LIT-7072
type: literature
title: "The Semi-Generic Group Model and Applications to Pairing-Based Cryptography?"
authors:
  - "Tibor Jager"
  - "Andy Rupp"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, dlp, elliptic-curve, factoring, finite-field, index-calculus, pairing, pollard-rho, provable-security, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In pairing-based cryptography the Generic Group Model (GGM) is used frequently to provide evidence towards newly introduced hardness assumptions. Unfortunately, the GGM does not reflect many known properties of bilinear group settings and thus hardness results in this model are of limited significance.

## Key claims (as reported)
- This paper proposes a novel computational model for pairing-based cryptography, called the Semi-Generic Group Model (SGGM), that is closer to the standard model and allows to make more meaningful security guarantees.
- In fact, the best algorithms currently known for solving pairing-based problems are semi-generic in nature.
- We demonstrate the usefulness of our new model by applying it to study several important assumptions (BDDH, Co-DH).
- Furthermore, we develop master theorems facilitating an easy analysis of other (future) assumptions.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines. Bears on the generic baseline (Pollard rho / generic-group lower bounds) against which every candidate algorithm in this program is benchmarked.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/6477543 (1).pdf`
- `downloads/6477543 (2).pdf`
- `downloads/6477543 (3).pdf`
- `downloads/6477543.pdf`
