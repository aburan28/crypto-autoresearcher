---
id: KN-LIT-7570
type: literature
title: On k-way split multiplication algorithms
authors: [Cihangir Mehmet Ozgun, Yayla Oguz]
year: 2026
venue: 'Cryptology ePrint Archive, Paper 2026/1494'
identifiers:
  eprint: iacr:2026/1494
  doi: null
  arxiv: null
  url: https://eprint.iacr.org/2026/1494
tags: [polynomial-multiplication, karatsuba, toeplitz, tmvp, subquadratic, interpolation-lower-bound, crossover, field-arithmetic, cost-model, ntt-unfriendly, implementation, adjacent]
confidence: reported
citation_verified: web
added: 2026-07-26
superseded_by: null
---

## Contribution
A mathematical framework for generalized **`k`-way split** polynomial multiplication
and Toeplitz Matrix-Vector Product (TMVP) algorithms over arbitrary fields, with exact
recurrences, a TMVP construction meeting the interpolation lower bound, and explicit
algebraic crossover thresholds telling you which algorithm sequence is optimal at a
given input size.

## Key claims (as reported)
- Generalized `k`-way Schoolbook and Karatsuba algorithms are constructed with **exact
  closed-form recurrence relations and arithmetic complexities for any integer `k`**.
- A new `k`-way TMVP algorithm using optimal evaluation points and matrix row-reversal
  is proved to **strictly achieve the theoretical interpolation lower bound**,
  requiring exactly `2k-1` subproblems and giving asymptotic complexity
  `O(n^{log_k(2k-1)})`.
- The optimal consecutive application sequence of `k`-way Karatsuba and Schoolbook is
  determined for any input size `n`, with peak efficiency "driven entirely by the
  **prime factorization of `n`**".
- Exact algebraic crossover thresholds are established, with the generalized TMVP
  formulas and optimal sequences claimed to outperform state-of-the-art unequal
  `k`-way splits and classical approaches.
- The motivating application is lattice PQC over NTT-unfriendly rings.

## Relevance to this program
`adjacent` and **low-level**: this is field/ring arithmetic, not an ECDLP technique.
It is recorded for cost-accounting hygiene rather than for any mechanism.

`KN-TECH-035` (full-cost accounting) and `KN-TECH-052` (fitting and extrapolating cost
exponents from bounded experiments) are the relevant corpus entries. Every ECDLP
exponent the program measures is quoted in some unit — field operations, gates, or
wall clock — and the conversion between those units is exactly what this paper
formalizes for multiplication. Two usable takeaways:

- The optimal multiplication schedule depends on the **prime factorization of the
  operand size**, not smoothly on the size. That is a concrete reason why a wall-clock
  measurement at one field size does not interpolate to another, and why the program's
  own extrapolations should be fit on the operation-count abstraction rather than on
  timings that silently switch algorithm at a crossover.
- Crossover thresholds between subquadratic and schoolbook methods are the reason a
  measured exponent can appear to bend at small scale for reasons that have nothing to
  do with the mathematics under test — a confound worth ruling out before any
  first-fall-degree or solving-degree curve is read as a mathematical signal.

Forecloses nothing and bears on no open problem in the corpus.

## Not verified here
Full paper not read; all claims relayed from the official ePrint abstract retrieved
from eprint.iacr.org on 2026-07-26 (hence `confidence: reported`); the abstract as
retrieved from the listing page was **truncated mid-sentence** in its final clause, so
the comparison against "state-of-the-art unequal `k`-way splits" is relayed
incompletely. ePrint history: received 2026-07-21, approved 2026-07-24. Not
peer-reviewed as of this entry; no DOI.

NOT verified here: the proofs, the claimed strictness of meeting the interpolation
lower bound, the crossover thresholds, any benchmark numbers (none appear in the
abstract), and whether the results hold uniformly over "arbitrary fields" including
the large prime fields this program works in — the stated motivation is
characteristic-friendly PQC rings, which is not the program's setting.
