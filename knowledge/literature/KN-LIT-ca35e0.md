---
id: KN-LIT-ca35e0
type: literature
title: "Climbing and descending tall isogeny volcanos (Galbraith) -- ECDLP transfer across the conductor gap; Sec. 10 'The Koblitz, Koblitz, Menezes speculation'"
authors:
  - "Steven D. Galbraith"
year: 2024
venue: "IACR ePrint 2024/924 (extended version); Research in Number Theory 11, no. 7 (2025); ANTS XVI talk"
identifiers:
  eprint: "iacr:2024/924"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2024/924"
tags: [ecdlp, isogeny, isogeny-class, volcano, crater, conductor, conductor-gap, kani, meet-in-the-middle, random-self-reduction, jmv, kkm, pairing-friendly, cm-method, ordinary-curves, galbraith]
confidence: reported
citation_verified: read
added: "2026-10-03"
superseded_by: null
supersedes: KN-LIT-1210
---

## Contribution

Revisits whether ECDLP is equally hard on two ordinary curves over F_q with the
same number of points, i.e. whether an efficient isogeny (group
homomorphism) can be built between them. The obstruction is the **conductor
gap**: write t^2 - 4q = f^2 D0; if a large prime N divides f and the two curves'
End-ring conductors differ in their power of N, every connecting isogeny has
degree divisible by N (Kohel). N <= 2 sqrt(q).

Uses the Kani construction (Robert's efficient representation of large-prime-
degree isogenies) plus a meet-in-the-middle search.

## Key claims (as stated in the paper; proofs not re-checked here)

- Worst-case isogeny between any two curves in a class: from O~(q^{3/2})
  [Galbraith 1999, KN-LIT-7630] to **heuristic O~(q^{2/5})** (Sec. 7).
- Given two curves across a large prime conductor gap N with
  q^{1/4} < N < sqrt(q), connected by an N-isogeny: a representation is found in
  O~(N^{1/2}) = O~(q^{1/4}).
- **Flat volcanoes** (random curves) and **tall volcanoes with constant/
  polynomial-size crater** (CM / pairing-friendly curves): rigorous **O~(q^{1/4})**
  isogeny between any two curves in the class.
- **Ascending is cheap**: from any floor curve one reaches the crater in at
  most O~(q^{1/4}).
- **Descending to an unknown floor curve is the open hard step (Problem B)**:
  given E0 on the crater and large N | f, *producing* a floor curve E1 costs
  either ~N^2 > q^{1/2} (construct the N-isogeny) or ~q^{1/2} guesses of a
  random E1 with the right point count. Sec. 11 lists a better Problem-B
  algorithm as the main open problem (modular-curve-biased guessing via
  Sutherland is suggested but not completed).
- **Theorem 5 (Sec. 9, revisiting JMV)**: if algorithm A solves ECDLP on a fixed
  positive proportion of curves with n points, then ECDLP on a *random* curve
  with n points is solvable with overwhelming probability in O~(q^{2/5}) plus
  poly(log q) queries to A. The proof partitions the class into S1 (conductor
  coprime to the large primes, i.e. near the crater) and S2 (divisible),
  #S2/#S1 >= q^{1/5}/2, and simply *ignores S1 as negligible*.

## Section 10: the KKM speculation (verbatim gist)

"Koblitz, Koblitz and Menezes [KKM11 = KN-LIT-0cb87e] introduced a bizarre
consequence of the difficulty to compute isogenies across the conductor gap.
They argued that this issue might imply that curves on the floor of the volcano
are less secure (i.e., have easier discrete logarithm problem) than curves on
the crater. There is no direct evidence for this conjecture ..." Galbraith then
shows his results do not refute it: crater -> floor transfer still costs
>= q^{1/2} (Problem B), so an easy floor does not leak to the crater; but
floor -> crater costs <= q^{1/4}, so (for small maximal-order class number) a
sub-sqrt attack on the crater would propagate to the *whole* class. "In
summary, our results are consistent with the argument by Koblitz, Koblitz and
Menezes."

## Limits

- Exponent-level statements in field operations; classical only (Kuperberg
  makes the problem subexponential quantumly, footnote 3).
- Isogeny transfer bounds hardness *equivalence*; it gives no ECDLP algorithm
  and no evidence that any level is weak.
- Theorem 5's guarantee covers random curves of the class (S2); the crater-side
  set S1 -- exactly the special CM / pairing-friendly curves -- is outside it.

## Relevance to this program

Sharpest current statement of the asymmetry around the conductor barrier,
directly feeding GOAL-ECTD-001 (KN-OPEN-cbbd97, KN-OPEN-cc1988),
RQ-VOLC-f6253b, and the new directional problem KN-OPEN-f2f6dc. Supersedes the
title-only bulk stub KN-LIT-1210.

## Local copies

- Fetched to session scratch from https://eprint.iacr.org/2024/924.pdf
  (sha256 `7e3af289faaa3b7c6b981e5f37ced7c975f4862a0ddcb46b4554c6ccfef202f6`);
  not vendored. Bulk-seed copies listed in KN-LIT-1210 (`downloads/2024-924*.pdf`).
