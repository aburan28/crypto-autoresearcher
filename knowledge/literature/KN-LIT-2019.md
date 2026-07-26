---
id: KN-LIT-2019
type: literature
title: "A Counterexample to the Chain Rule for Conditional HILL Entropy? And what Deniable Encryption has to do with it"
authors:
  - "Stephan Krenn"
  - "Krzysztof Pietrzak"
  - "Akshay Wadia"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A chain rule for an entropy notion H(·) states that the entropy H(X) of a variable X decreases by at most ` if conditioned on an `-bit string A, i.e., H(X|A) ≥ H(X) − `. More generally, it satisfies a chain rule for conditional entropy if H(X|Y, A) ≥ H(X|Y ) − `.

## Key claims (as reported)
- All natural information theoretic entropy notions we are aware of (like Shannon or min-entropy) satisfy some kind of chain rule for conditional entropy.
- Moreover, many computational entropy notions (like Yao entropy, unpredictability entropy and several variants of HILL entropy) satisfy the chain rule for conditional entropy, though here not only the quantity decreases by `, but also the quality of the entropy decreases exponentially in `.
- However, for the standard notion of conditional HILL entropy (the computational equivalent of min-entropy) the existence of such a rule was unknown so far.
- In this paper, we prove that for conditional HILL entropy no meaningful chain rule exists, assuming the existence of one-way permutations: there exist distributions X, Y, A, where A is a distribution over a single bit, but H HILL (X|Y ) H HILL (X|Y, A), even if we simultaneously allow for a massive degradation in the quality of the entropy.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/77850023 (1).pdf`
- `downloads/77850023 (2).pdf`
- `downloads/77850023 (3).pdf`
- `downloads/77850023.pdf`
