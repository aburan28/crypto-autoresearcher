---
id: KN-LIT-4039
type: literature
title: "Further Hidden Markov Model Cryptanalysis"
authors:
  - "P.J. Green"
  - "R. Noad"
  - "N.P. Smart"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, elliptic-curve, pairing, side-channel, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We extend the model of Karlof and Wagner for modelling side channel attacks via Input Driven Hidden Markov Models (IDHMM) to the case where not every state corresponds to a single observable symbol. This allows us to examine algorithms where errors in measurements can occur between sub-operations, e.g. there may be an error probability of distinguishing an add (A) versus a double (D) for an elliptic curve system.

## Key claims (as reported)
- The prior work of Karlof and Wagner would assume the error was between distinguishing an add-double (AD) versus a double (D).
- Our model also allows the modelling of unknown values, where one is unable to determine whether a given observable is add or double, and is the first model to allow one to analyse incomplete traces.
- Hence, our extension allows a more realistic modelling of real side channel attacks.
- In addition we look at additional heuristic approaches to combine multiple traces together so as to deduce further information.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/005 (1).pdf`
- `downloads/005 (2).pdf`
- `downloads/005 (3).pdf`
- `downloads/005.pdf`
