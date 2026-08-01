---
id: KN-LIT-4775
type: literature
title: "Log-S-unit Lattices Using Explicit Stickelberger"
authors:
  - "Generators to Solve Approx Ideal-SVP"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, lattice, mov-fr, number-theory, pqc, provable-security, quantum, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In 2020, Bernard and Roux-Langlois introduced the TwistedPHS algorithm to solve Approx-Svp for ideal lattices on any number field, based on the PHS algorithm by Pellet-Mary, Hanrot and Stehlé. They performed experiments for prime conductors cyclotomic fields of degrees at most 70, one of the main bottlenecks being the computation of a log-S-unit lattice which requires subexponential time.

## Key claims (as reported)
- Our main contribution is to extend these experiments to cyclotomic fields of degree up to 210 for most conductors m.
- Building upon new results from Bernard and Kučera on the Stickelberger ideal, we use explicit generators to construct full-rank log-S-unit sublattices fulfilling the role of approximating the full Twisted-PHS lattice.
- In our best approximate regime, our results show that the Twisted-PHS algorithm outperforms, over our experimental range, the CDW algorithm by Cramer, Ducas and Wesolowski, and sometimes beats its asymptotic volumetric lower bound.
- Additionally, we use these explicit Stickelberger generators to remove almost all quantum steps in the CDW algorithm, under the mild restriction √ that the plus part of the class number verifies h+ m ≤ O( m).

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/137910058 (1).pdf`
- `downloads/137910058.pdf`
