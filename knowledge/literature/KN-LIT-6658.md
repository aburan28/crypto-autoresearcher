---
id: KN-LIT-6658
type: literature
title: "Simple Power Analysis of Unified Code for ECC Double and Add"
authors:
  - "Colin D. Walter"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [curve-arithmetic, elliptic-curve, implementation, prime-field, side-channel, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Classical formulae for point additions and point doublings on elliptic curves differ. This can make a side channel attack possible on a single ECC point multiplication by using simple power analysis (SPA) to observe the different times for the component point operations.

## Key claims (as reported)
- Under the usual binary exponentiation algorithm, the deduced presence or absence of a point addition indicates a 1 or 0 respectively in the secret key, thus revealing the key in its entirety.
- Several authors have produced unified code for these operations in order to avoid this weakness.
- Although timing differences are thereby eliminated from this code level, it is shown that SPA attacks may still be possible on selected single point multiplications if there is sufficient side channel leakage at lower levels.
- Here a conditional subtraction in Montgomery modular multiplication (MMM) is assumed to give such leakage, but other modular multipliers may be equally susceptible to attack.

## Relevance to this program
Elliptic-curve/abelian-variety mathematics background for the program; relevant to curve arithmetic, point counting, and structural results underlying ECDLP instances.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/31560191 (1).pdf`
- `downloads/31560191 (2).pdf`
- `downloads/31560191.pdf`
