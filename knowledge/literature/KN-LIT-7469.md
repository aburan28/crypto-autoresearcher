---
id: KN-LIT-7469
type: literature
title: "Verified Proofs of Higher-Order Masking Gilles Barthe1 , Sonia Belaı̈d2 , François Dupressoir1 , Pierre-Alain Fouque3"
authors:
  - "Benjamin Grégoire"
  - "Pierre-Yves Strub"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, mov-fr, mpc, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we study the problem of automatically verifying higher-order masking countermeasures. This problem is important in practice, since weaknesses have been discovered in schemes that were thought secure, but is inherently exponential: for t-order masking, it involves proving that every subset of t intermediate variables is distributed independently of the secrets.

## Key claims (as reported)
- Some tools have been proposed to help cryptographers check their proofs, but are often limited in scope.
- We propose a new method, based on program verification techniques, to check the independence of sets of intermediate variables from some secrets.
- Our new language-based characterization of the problem also allows us to design and implement several algorithms that greatly reduce the number of sets of variables that need to be considered to prove this independence property on all valid adversary observations.
- The result of these algorithms is either a proof of security or a set of observations on which the independence property cannot be proved.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/90560262 (1).pdf`
- `downloads/90560262.pdf`
