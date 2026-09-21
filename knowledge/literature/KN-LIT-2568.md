---
id: KN-LIT-2568
type: literature
title: "Approx-SVP in Ideal Lattices with Pre-processing"
authors:
  - "Alice Pellet-Mary"
  - "Guillaume Hanrot"
  - "Damien Stehlé"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [class-group, lattice, number-theory, provable-security, quantum, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We describe an algorithm to solve the approximate Shortest Vector Problem for lattices corresponding to ideals of the ring of integers of an arbitrary number field K. This algorithm has a pre-processing phase, whose run-time is exponential in log |∆| with ∆ the discriminant of K.

## Key claims (as reported)
- Importantly, this pre-processing phase depends only on K.
- The pre-processing phase outputs an “advice”, whose bit-size is no more than the run-time of the query phase.
- Given this advice, the query phase of the algorithm takes as input any ideal I of the ring of integers, and e outputs an element of I which is at most exp(O((log |∆|)α+1 /n)) times longer than a shortest non-zero element of I (with respect to the Euclidean norm of its canonical embedding).
- This query phase runs in e time and space exp(O((log |∆|)max(2/3,1−2α) )) in the classical setting, and 1−2α e exp(O((log |∆|) )) in the quantum setting.

## Relevance to this program
Elliptic-curve/abelian-variety mathematics background for the program; relevant to curve arithmetic, point counting, and structural results underlying ECDLP instances.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/114760241 (1).pdf`
- `downloads/114760241.pdf`
