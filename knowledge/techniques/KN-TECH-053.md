---
id: KN-TECH-053
type: technique
title: MQ and Boolean polynomial-system solving - XL, BooleanSolve, and the crossbred hybrid
tags: [mq, multivariate-quadratic, xl, crossbred, booleansolve, boolean-solving, polynomial-system, exhaustive-search, hybrid, sparse-linear-algebra, groebner, crossover, solving, calibration, index-calculus]
confidence: reported
complexity: over F_2 with m=n, BooleanSolve is reported at O(2^{0.841 n}) deterministic and O(2^{0.792 n}) Las Vegas against an exhaustive-search baseline of 4 log_2(n) 2^n; the crossbred algorithm is reported to outperform prior methods over a wide parameter range but its exponent is parameter-dependent
applicability: any index-calculus cost model whose per-decomposition solve is done by an MQ/Boolean solver rather than a Groebner basis; required reading before quoting EXP-ICI-001's crossbred exponent
source_refs: [KN-LIT-138, KN-LIT-139, KN-LIT-140, KN-LIT-141, KN-TECH-003, KN-TECH-004, KN-TECH-011, KN-TECH-008]
added: 2026-07-25
superseded_by: null
---

## Method
Point-decomposition index calculus (`KN-TECH-003`) turns relation-finding into
repeated solving of a polynomial system derived from a summation polynomial. The
corpus has documented the **Groebner** route to that solve in depth
(`KN-TECH-004`, `KN-TECH-011`). This entry documents the other route — the
MQ/Boolean solver family — because that is what the program's own ICI thread
actually measures.

The family, in order of appearance:

- **XL and relinearization** (`KN-LIT-138`). Multiply the original equations by
  monomials to enlarge the system, then linearise. Targets the **overdefined**
  regime where `m` exceeds `n`; the square case `m = n` is the hard one.
- **BooleanSolve** (`KN-LIT-140`). Reduces the problem to a combination of
  exhaustive search over a subset of variables and sparse linear algebra on the
  remainder, with **proved** bounds `O(2^{0.841 n})` deterministic and
  `O(2^{0.792 n})` Las Vegas at `m = n`, against an exhaustive-search baseline of
  `4 log_2(n) 2^n`.
- **Crossbred** (`KN-LIT-139`). The same hybrid shape, tuned: a partial
  Macaulay-style linear-algebra phase followed by exhaustive search over the
  remaining variables, with the split a tunable parameter. Reported to outperform
  prior methods across a wide parameter range, and demonstrated by solving the
  Fukuoka Type I MQ challenges (`KN-LIT-141`) — 148 quadratic equations in 74
  variables in under a day.

The unifying idea is a **trade between linear algebra and search**, with the
achieved exponent a function of where the split is placed. This is the same
structural trade as enumeration versus sieving in lattices (`KN-TECH-042`) and
meet-in-the-middle versus low-memory collision search in isogenies
(`KN-TECH-050`), and it fails in the same way when the split parameter is not
reported alongside the exponent.

## The conflation to avoid
An MQ solver's complexity is stated in the **number of Boolean variables `n`** of
the system being solved. An index-calculus total exponent is stated in the
**group order**. `EXP-ICI-001` reports a crossbred *total IC* exponent of about
0.863 and a MITM one of about 0.667, with the decision gate on whether a
bootstrap CI lower bound falls below rho's 0.5. Those numbers are outputs of a
relation-collection cost model that *uses* a solver; they are not the solver's
own exponent, and quoting either as the other is a category error.

The check this entry enables: a measured per-solve cost implying behaviour better
than the proved bounds of `KN-LIT-140` in a comparable regime is a reason to
audit the measurement before celebrating it.

## Applicability limits
The proved bounds are for **quadratic** systems over **F_2** at `m = n`, under
whatever genericity assumptions the source states. Summation-polynomial systems
are neither generic nor necessarily in that regime — they are structured, often
overdetermined, and over prime fields in the program's main line rather than over
F_2. So this family bounds what a solver can be expected to do; it does not
predict what it will do on the program's systems, which is why the program
measures rather than assumes.

Nothing here bears on `KN-OPEN-001` (does index calculus beat rho over prime
fields). A faster MQ solver lowers the per-decomposition cost and leaves the
relation-count side of the cost model untouched; `FINDING-PF-IC-001`'s structural
argument is that the total is dominated by the `|F|`-size linear algebra, not by
the solve.

## Verified vs reported
All four source entries are `citation_verified: web`, written under an egress
policy that blocked every direct fetch; bibliographic details are corroborated
across primary-index listings, full texts were not read. **The 0.841 and 0.792
exponents and the `4 log_2(n) 2^n` baseline are quoted from a search-returned
abstract of `KN-LIT-140` and have not been confirmed against the paper.** The
crossbred algorithm's construction and parameterisation were not obtained at all;
`KN-LIT-139` records what it claims, not how it works.

The mapping onto `EXP-ICI-001` is read from that experiment's frozen
specification in this repository, and the category-error warning is this
program's own reasoning rather than a claim from any source.
