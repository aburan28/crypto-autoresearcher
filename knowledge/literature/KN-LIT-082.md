---
id: KN-LIT-082
type: literature
title: An improved algorithm for computing logarithms over GF(p) and its cryptographic significance
authors: [Pohlig Stephen C., Hellman Martin E.]
year: 1978
venue: IEEE Transactions on Information Theory, 24(1):106-110
identifiers:
  eprint: null
  doi: 10.1109/TIT.1978.1055817
  url: https://ee.stanford.edu/~hellman/publications/28.pdf
tags: [pohlig-hellman, group-order, smooth-order, subgroup, crt, generic, discrete-logarithm, baseline, ecdlp, hygiene]
confidence: established
citation_verified: read
added: 2026-07-24
superseded_by: null
---

## Contribution
Shows that the discrete logarithm in a cyclic group of order n is only as hard
as the discrete logarithm in its largest prime-order subgroup. If
n = prod p_i^{e_i}, one solves the DLP modulo each p_i^{e_i} separately (by
e_i nested solves in a group of order p_i) and reassembles k by the Chinese
Remainder Theorem. The paper states the consequence for cryptography directly:
primes p for which p-1 is smooth must be avoided, because then computing logs
over GF(p) is easy.

## Key claims (as reported)
- For p-1 with only small prime factors the algorithm runs in O(log^2 p)
  time and space, versus O(p^{1/2}) for previously published methods (proven,
  and the paper gives explicit operation counts).
- General form: cost is dominated by the largest prime factor of the group
  order; each prime-order subsolve is still a square-root problem in p_i.
- The paper gives worked examples at both extremes, including a 137-digit
  prime for which the method is easy and a 60-digit prime for which no known
  algorithm was feasible.

## Relevance to this program
This is the reduction that defines what "the ECDLP instance" even is. Every
cost statement the program makes -- baseline or claimed advantage -- must be
made against the largest prime-order subgroup, not the full group order
#E(F_p). It also fixes a scoping rule for negative results: an advantage
demonstrated on a curve with smooth group order is an artifact of
Pohlig-Hellman, not a mechanism. Group-order factorization is therefore a
mandatory precondition check on any instance the program constructs, and any
toy curve used for measurement must have its prime-order subgroup stated
explicitly. See KN-TECH-030.

## Not verified here
Full text of the Stanford-hosted reprint was fetched and the abstract, the
O(log^2 p) claim, and the operation-count statements were read directly. The
detailed operation counts in Section III were not re-derived. The CRT
reassembly step and the per-subgroup square-root cost are standard/textbook
(hence confidence: established).
