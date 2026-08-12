---
id: KN-LIT-390
type: literature
title: "Easy scalar decompositions for efficient scalar multiplication on elliptic curves and genus 2 Jacobians"
authors:
  - "Benjamin Smith"
year: 2013
venue: "arXiv preprint"
identifiers:
  eprint: null
  doi: null
  arxiv: "1310.5250"
  url: "https://arxiv.org/abs/1310.5250"
tags: [curve-arithmetic, elliptic-curve, endomorphism, finite-field, glv-gls, jacobian, lattice, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The first step in elliptic curve scalar multiplication algorithms based on scalar decompositions using efficient endomorphisms— including Gallant–Lambert–Vanstone (GLV) and Galbraith–Lin–Scott (GLS) multiplication, as well as higher-dimensional and higher-genus constructions—is to produce a short basis of a certain integer lattice involving the eigenvalues of the endomorphisms. The shorter the basis vectors, the shorter the decomposed scalar coefficients, and the faster the resulting scalar multiplication.

## Key claims (as reported)
- Typically, knowledge of the eigenvalues allows us to write down a long basis, which we then reduce using the Euclidean algorithm, Gauss reduction, LLL, or even a more specialized algorithm.
- In this work, we use elementary facts about quadratic rings to immediately write down a short basis of the lattice for the GLV, GLS, GLV+GLS, and Q-curve constructions on elliptic curves, and for genus 2 real multiplication constructions.
- We do not pretend that this represents a significant optimization in scalar multiplication, since the lattice reduction step is always an offline precomputation—but it does give a better insight into the structure of scalar decompositions.
- In any case, it is always more convenient to use a ready-made short basis than it is to compute a new one.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/1310.5250v1.pdf`
