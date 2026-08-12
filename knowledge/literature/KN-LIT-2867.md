---
id: KN-LIT-2867
type: literature
title: "Chainable Functional"
authors:
  - "Dario Fiore"
  - "Russell W. F. Lai"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, mpc, pairing, provable-security, quantum, signature, survey, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A functional commitment (FC) scheme allows one to commit to a vector x and later produce a short opening proof of (f, f (x)) for any admissible function f . Since their inception, FC schemes supporting ever more expressive classes of functions have been proposed.

## Key claims (as reported)
- In this work, we introduce a novel primitive that we call chainable functional commitment (CFC), which extends the functionality of FCs by allowing one to 1) open to functions of multiple inputs f (x1 , . . . , xm ) that are committed independently, 2) while preserving the output also in committed form.
- We show that CFCs for quadratic polynomial maps generically imply FCs for circuits.
- Then, we efficiently realize CFCs for quadratic polynomials over pairing groups and lattices, resulting in the first FC schemes for circuits of unbounded depth based on either pairingbased or lattice-based falsifiable assumptions.
- Our FCs require fixing a-priori only the maximal width of the circuit to be evaluated, and have opening proof size depending only on the circuit depth.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14369060 (1).pdf`
- `downloads/14369060.pdf`
