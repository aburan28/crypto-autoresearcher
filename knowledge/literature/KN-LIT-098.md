---
id: KN-LIT-098
type: literature
title: Polynomial-Time Algorithms for Prime Factorization and Discrete Logarithms on a Quantum Computer
authors: [Shor Peter W.]
year: 1997
venue: SIAM Journal on Computing, 26(5):1484-1509
identifiers:
  eprint: null
  doi: 10.1137/S0097539795293172
  url: https://arxiv.org/abs/quant-ph/9508027
tags: [shor, quantum, period-finding, quantum-fourier-transform, discrete-logarithm, factoring, polynomial-time, post-quantum, ecdlp, baseline]
confidence: established
citation_verified: read
added: 2026-07-24
superseded_by: null
---

## Contribution
The source of the quantum threat to all discrete-log and factoring based
cryptography. Shor gives randomized algorithms, polynomial in the input size,
for integer factorization (Section 5) and for extracting discrete logarithms
(Section 6) on a quantum computer, built from two subroutines: reversible
modular exponentiation and the quantum Fourier transform. The discrete-log
algorithm is a two-dimensional period-finding argument and applies to any
group in which the group law can be computed reversibly -- including elliptic
curves.

## Key claims (as reported)
- Polynomial-time quantum algorithms for factoring and for discrete logarithms
  (proven, modulo the model of a fault-free quantum computer).
- The number of steps is polynomial in the number of digits of the input.
- The paper is an expanded version of the 1994 FOCS paper, with the discrete
  log algorithm presented for the multiplicative group of a prime field; the
  generic-group formulation that covers ECDLP is the standard reading.

## Relevance to this program
Fixes the boundary of what this program is and is not studying. GOAL-CRYPTO-001
targets classical algorithmic advantage over Pollard rho; Shor already gives a
polynomial-time quantum algorithm, so "beats rho" is only interesting in the
classical model, and any proposal must state its model explicitly. The entry
also anchors the corpus's post-quantum material (KN-LIT-049 onwards), which
previously mentioned "ECDLP falls to Shor" in passing without a source entry:
the reason the corpus carries lattice and isogeny literature at all is this
result. Concrete resource requirements -- which are what determine whether the
threat is near-term -- are in KN-LIT-099, not here.

## Not verified here
The SIAM PDF was fetched and the abstract and the paper's structural summary
(sections 3-6) were read directly. The correctness arguments for the
period-finding and continued-fraction steps were not re-derived, and the
elliptic-curve specialization does not appear in this paper -- it is
downstream work (see KN-LIT-099). Author, title, venue (SIAM J. Comput.
26(5):1484-1509, October 1997) and DOI confirmed against the publisher record;
arXiv quant-ph/9508027 is the open version.
