---
id: KN-LIT-5922
type: literature
title: "Privately Constraining and Programming PRFs, the LWE Way"
authors:
  - "Chris Peikert"
  - "Sina Shiehian"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [curve-arithmetic, lattice, mpc, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Constrained pseudorandom functions allow for delegating “constrained” secret keys that let one compute the function at certain authorized inputs—as specified by a constraining predicate—while keeping the function value at unauthorized inputs pseudorandom. In the constraint-hiding variant, the constrained key hides the predicate.

## Key claims (as reported)
- On top of this, programmable variants allow the delegator to explicitly set the output values yielded by the delegated key for a particular set of unauthorized inputs.
- Recent years have seen rapid progress on applications and constructions of these objects for progressively richer constraint classes, resulting most recently in constraint-hiding constrained PRFs for arbitrary polynomial-time constraints from Learning With Errors (LWE) [Brakerski, Tsabary, Vaikuntanathan, and Wee, TCC’17], and privately programmable PRFs from indistinguishability obfuscation (iO) [Boneh, Lewi, and Wu, PKC’17].
- In this work we give a unified approach for constructing both of the above kinds of PRFs from LWE with subexponential exp(nε ) approximation factors.
- Our constructions follow straightforwardly from a new notion we call a shift-hiding shiftable function, which allows for deriving a key for the sum of the original function and any desired hidden shift function.

## Relevance to this program
Elliptic-curve/abelian-variety mathematics background for the program; relevant to curve arithmetic, point counting, and structural results underlying ECDLP instances.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10770193 (1).pdf`
- `downloads/10770193 (2).pdf`
- `downloads/10770193 (3).pdf`
- `downloads/10770193 (4).pdf`
- `downloads/10770193.pdf`
