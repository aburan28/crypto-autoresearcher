---
id: KN-LIT-3371
type: literature
title: "Defeating Countermeasures Based on Randomized BSD Representations"
authors:
  - "Pierre-Alain Fouque"
  - "Frédéric Muller"
  - "Guillaume Poupard"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [curve-arithmetic, dlp, elliptic-curve, pairing, rsa, side-channel, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The recent development of side channel attacks has lead implementers to use increasingly sophisticated countermeasures in critical operations such as modular exponentiation, or scalar multiplication on elliptic curves. A new class of countermeasures is based on inserting random decisions when choosing one representation of the secret scalar out of a large set of representations of the same value.

## Key claims (as reported)
- For instance, this is the case of countermeasures proposed by Oswald and Aigner, or Ha and Moon, both based on randomized Binary Signed Digit (BSD) representations.
- Their advantage is to offer excellent speed performances.
- However, the first countermeasure and a simplified version of the second one were already broken using Markov chain analysis.
- In this paper, we take a different approach to break the full version of HaMoon’s countermeasure using a novel technique based on detecting local collisions in the intermediate states of computation.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/31560313 (1).pdf`
- `downloads/31560313 (2).pdf`
- `downloads/31560313.pdf`
