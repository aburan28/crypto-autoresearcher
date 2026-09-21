---
id: KN-LIT-103
type: literature
title: Sieve algorithms for the shortest vector problem are practical
authors: [Nguyen Phong Q., Vidick Thomas]
year: 2008
venue: 'Journal of Mathematical Cryptology, 2(2):181-207'
identifiers:
  eprint: null
  doi: 10.1515/JMC.2008.009
  url: https://people.csail.mit.edu/vidick/JoMC08.pdf
tags: [sieving, aks, svp, exact-svp, heuristic, memory, implementation, lattice, baseline]
confidence: reported
citation_verified: read
added: 2026-07-24
superseded_by: null
---

## Contribution
The first implementation and practical analysis of the Ajtai-Kumar-Sivakumar
(AKS) sieve, the `2^O(n)`-time-and-space randomised algorithm for exact SVP.
Before this paper the AKS sieve was widely believed impractical -- Schnorr had
estimated the hidden constant in the exponent at 30 or more. The paper shows a
heuristic variant is implementable, which is the origin of the entire modern
sieving line that now dominates lattice cryptanalysis.

## Key claims (as reported)
- A heuristic variant of AKS runs in `(4/3 + eps)^n` polynomial-time operations
  using `(4/3 + eps)^(n/2)` polynomially-many bits of space. The variant is
  explicitly heuristic; the provable AKS bounds are not what is implemented.
- The implementation experimentally finds shortest vectors up to dimension 50.
- Honest negative result stated by the authors: in those dimensions the sieve is
  *slower* than classical alternatives (enumeration). Practicality here means
  "implementable and competitive in principle," not "faster today."

## Relevance to this program
Two lessons the program can use directly. First, this is a clean worked example
of an algorithm whose asymptotic superiority (`2^O(n)` versus enumeration's
`2^Theta(n log n)`) was real but took roughly a decade of engineering
(KN-LIT-104, KN-LIT-105, KN-LIT-106) before it won at any dimension anyone
cared about -- the exact pattern the program's own asymptotic-versus-concrete
gates are meant to detect. Second, the paper's memory statement is the origin of
the sieving memory problem: the space requirement is exponential and
non-negotiable, which is what makes lattice sieving the natural test case for
full-cost accounting (KN-TECH-035, KN-TECH-044).

## Not verified here
The complete published abstract and the introduction of the author-hosted PDF
were read. The `(4/3 + eps)^n` heuristic analysis was not re-derived, the
implementation was not run, and the dimension-50 result was not reproduced.
