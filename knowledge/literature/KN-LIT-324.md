---
id: KN-LIT-324
type: literature
title: "On the correct use of the negation map in the Pollard rho method"
authors:
  - "Daniel J. Bernstein"
  - "Tanja Lange"
  - "Peter Schwabe"
year: 2011
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2011/003"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2011/003"
tags: [curve-arithmetic, dlp, ecdlp, elliptic-curve, hyperelliptic, implementation, pairing, pollard-rho]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Bos, Kaihara, Kleinjung, Lenstra, and Montgomery recently showed that ECDLPs on the 112-bit secp112r1 curve can be solved in an expected time of 65 years on a PlayStation 3. This paper shows how to solve the same ECDLPs at almost twice the speed on the same hardware.

## Key claims (as reported)
- The improvement comes primarily from a new variant of Pollard’s rho method that fully exploits the negation map without branching, and secondarily from improved techniques for modular arithmetic.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines. Bears on the generic baseline (Pollard rho / generic-group lower bounds) against which every candidate algorithm in this program is benchmarked.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2011-003.pdf`
- `downloads/65710132 (1).pdf`
- `downloads/65710132 (2).pdf`
- `downloads/65710132 (3).pdf`
- `downloads/65710132.pdf`
- `downloads/negation-20110102.pdf`
