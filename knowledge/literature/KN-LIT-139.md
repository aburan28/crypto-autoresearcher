---
id: KN-LIT-139
type: literature
title: A crossbred algorithm for solving Boolean polynomial systems
authors: [Joux Antoine, Vitse Vanessa]
year: 2017
venue: 'NuTMiC 2017, Warsaw (ePrint 2017/372); proceedings version Springer'
identifiers:
  eprint: iacr:2017/372
  doi: 10.1007/978-3-319-76620-1_1
  url: https://eprint.iacr.org/2017/372
tags: [mq, multivariate-quadratic, crossbred, boolean-solving, polynomial-system, exhaustive-search, hybrid, macaulay, solving, records, calibration, index-calculus]
confidence: reported
citation_verified: web
added: 2026-07-25
superseded_by: null
---

## Contribution
Introduces the **crossbred** algorithm for solving systems of Boolean polynomial
equations: given `m` polynomials of degree at most `d` in `n` variables, find
solutions over F_2. The algorithm is a hybrid — it performs a partial
Macaulay-style linear-algebra phase before falling back to exhaustive search over
a subset of variables — and is reported to outperform previously known methods
across a wide range of relevant parameters.

## Key claims (as reported)
- Solving Boolean polynomial systems is NP-hard for `d > 1`, which motivates the
  search for algorithms faster than exhaustive search.
- The new algorithm outperforms previously known methods over a wide range of
  relevant parameters.
- **Demonstrated in practice, not only asymptotically**: Joux solved all the
  Fukuoka Type I MQ challenges, including a system of **148 quadratic equations
  in 74 variables in under a day**.

## Relevance to this program
This is the solver behind the ICI thread's headline number. `EXP-ICI-001`'s
frozen specification compares a **crossbred** total index-calculus exponent of
about 0.863 against a **MITM** exponent of about 0.667, with bootstrap 90%
confidence intervals, and its decision gate is whether the best exponent's CI
lower bound sits below rho's 0.5. Until this entry the corpus contained no
description of the crossbred algorithm at all, so the program's most quoted
exponent rested on a solver with no recorded prior art — the "self-citation gap"
of `docs/knowledge-review-20260725.md` §6.3.

Two cautions that follow from having the entry:

- **The exponents are not the same object.** Crossbred's own complexity is
  expressed in the number of Boolean variables `n`; the ICI thread's 0.863 is a
  *total index-calculus* exponent in the group order, obtained by using crossbred
  as the per-decomposition solver inside a relation-collection cost model. The two
  must not be conflated when either is cited.
- **The Fukuoka result is a calibration anchor** in the sense of `KN-TECH-036`
  and `KN-TECH-049`: a publicly checkable instance somebody actually solved,
  against which a claimed solver cost can be sanity-checked.

## Not verified here
Verification was by web search surfacing primary-index listings (IACR ePrint
2017/372, DBLP `journals/iacr/JouxV17`, HAL deposit `hal-01981516`, a Springer
chapter DOI 10.1007/978-3-319-76620-1_1, and Semantic Scholar); direct fetches
returned HTTP 403 under this session's egress policy. The ePrint is dated 2017
and the Springer proceedings version appears later; **2017 is recorded and the
proceedings year was not confirmed.**

NOT verified here: the algorithm's actual construction, its parameter selection
(including the `k`-fraction the program's own solver path sweeps), its complexity
analysis, and the conditions under which it beats plain exhaustive search or
Groebner methods. The program's `crossbred_real_cost.py` cost model must be
checked against the paper, not against this entry.
