---
id: KN-LIT-6881
type: literature
title: "Succinct Diophantine-Satisfiability Arguments"
authors:
  - "Patrick Towa"
  - "Damien Vergnaud"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, finite-field, pairing, rsa, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A Diophantine equation is a multi-variate polynomial equation with integer coefficients, and it is satisfiable if it has a solution with all unknowns taking integer values. Davis, Putnam, Robinson and Matiyasevich showed that the general Diophantine satisfiability problem is undecidable (giving a negative answer to Hilbert’s tenth problem) but it is nevertheless possible to argue in zero-knowledge the knowledge of a solution, if a solution is known to a prover.

## Key claims (as reported)
- We provide the first succinct honest-verifier zero-knowledge argument for the satisfiability of Diophantine equations with a communication complexity and a round complexity that grows logarithmically in the size of the polynomial equation.
- The security of our argument relies on standard assumptions on hidden-order groups.
- As the argument requires to commit to integers, we introduce a new integer-commitment scheme that has much smaller parameters than Damgård and Fujisaki’s scheme.
- We finally show how to succinctly argue knowledge of solutions to several NP-complete problems and cryptographic problems by encoding them as Diophantine equations.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12491387 (1).pdf`
- `downloads/12491387.pdf`
