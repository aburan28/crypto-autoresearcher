---
id: KN-OPEN-ac409f
type: open_problem
title: Is there a LOWER bound on the eliminant-solving exponent kappa for the quasi-subfield chain systems? Every located constraint is an upper bound, and the closure argument needs a floor
tags: [qsp, quasi-subfield, ecdlp, index-calculus, eliminant, groebner, resultant, bkk, mixed-volume, cost-model, solver-exponent, kappa, heuristic-validation, ecc2k-130, characteristic-two, open]
confidence: unverified
status: open
source_refs: [KN-LIT-0a321c, KN-LIT-4fe9d2, KN-LIT-096, KN-TECH-080]
internal_refs: [EV-QSP-a6aa4b, DEC-20260917-793ae2, EXP-QSP-33b442, H-QSP-5540d7, RQ-QSP-f9bbdb, IDEA-20260916-b84e2d, TASK-20260917-52b4e6]
added: "2026-09-17"
superseded_by: null
---

## Statement

For the chain system `S` of [[KN-LIT-0a321c]] Section 3.1 at parameters
`(n, n', d, m)`, let `kappa` be the exponent governing the cost of solving the
system, in the sense of Proposition 8 of [[KN-LIT-4fe9d2]]:

```
    alpha_beta = 1 / (2 kappa beta)
```

A quasi-subfield factor base beats generic algorithms iff `alpha_beta > 1`, i.e.
iff **`kappa < 1/(2 beta)`** — iff the solver is *cheap*.

**Is there any published or derivable LOWER bound on `kappa` for these
systems?**

Every constraint on `kappa` this program has located is an **upper** bound, and
an upper bound cannot exclude a cheap solver. That is the gap, and it is a gap
in the literature rather than in this program's bookkeeping.

## Why it is precisely statable now, and what the threshold actually is

The quality floor is settled. `H-QSP-5540d7` (B), reviewed at
`review-breakthrough` and independently recomputed on all 65 archived complete
splitters from `(n, n', d)` alone with exact rationals
(`TASK-20260917-34b637`), gives for every completely splitting
`L = X^{p^{n'}} - lambda(X)` with `r >= 1` and `n' < n`:

```
    beta  >=  n / (n + n' - r)  >  1/2
```

So the threshold `kappa_crit = 1/(2 beta_min)` is computable exactly. At
`n = 131` the smallest admissible `beta` over `n' = 2..130` is `131/260` at
`n' = 130` (`q = 1, r = 1`), giving

```
    kappa_crit = 260/262 = 130/131 = 0.9923664
```

The general worst case is `n' = n - 1`, where `beta >= n/(2n-2)` and the
threshold is exactly `(n-1)/n`:

| n | kappa_crit = (n-1)/n |
|---|---|
| 7 | 0.857 |
| 31 | 0.968 |
| 131 | 0.9923664 |
| 257 | 0.9961 |
| → ∞ | → 1 |

**The question is therefore sharp: is `kappa >= 1` (asymptotically), or is it
not?** Nothing softer will do, and nothing harder is needed.

## Why the literature does not answer it, with the direction stated

Three located statements, all read directly against the frozen source texts by
`TASK-20260917-52b4e6`:

1. **Euler–Petit, Proposition 7**, verbatim: *"where `kappa` is a constant
   involved in the cost of the resolution of the system S **currently majored by
   4.876**"* (`inputs/EULER-PETIT-2019-QSP/paper_fulltext.md:2597`). "Majored
   by" is *bounded above*. `kappa <= 4.876` says nothing about whether
   `kappa >= 1`.
2. **Huang, Lemma 3.1**: the eliminant and its parametrisations *"can be found
   in `Õ(m^5.188 (3d)^{4.876 m^2})` arithmetic steps"* — a big-O, i.e. again an
   upper bound on cost.
3. **Huang, Appendix A.1**
   (`inputs/HUANG-2020-JMC-QSP/paper_fulltext.md:1116-1118`): the univariate
   polynomials are of degree ***bounded by*** `M(E) = 2^{m(m-1)} d^{m(m-1)/2}`,
   and root-finding *"can be **neglected** in the overall complexity
   estimation"*.

Statement 3 is the one that matters most, because it is what heuristic H1 of
`H-QSP-5540d7` leans on. H1's declared *rigorous ingredient* asserts the
eliminant "has degree `M(E)`" and that root-finding "costs **at least**
`M(E)`". Its own cited appendix says *bounded by* and *can be neglected* — the
opposite direction, twice. The step that would convert the upper bound into the
equality H1 needs is the **BKK / mixed-volume generic-attainment** statement,
which H1 itself marks `provenance: recalled` and describes as supporting
"nothing by itself"; AGENTS.md rule 9 bars a recalled reference from
discharging a heuristic's `supporting_results`.

After honouring that label, **H1 has no retrieved support in the direction the
closure argument uses it.**

## Why it will not be answered by BKK alone, even if someone retrieves it

The generic-attainment statement is about *generic* supports. The instances here
are not generic: they are chain systems `S^{(k)}` built from summation
polynomials composed `k` times with a fixed `lambda`, whose supports are highly
structured. Whether the mixed volume is attained on that family is exactly the
untested question, and a citation to the generic theorem does not settle the
structured case. This is the substantive half of the problem; the citation
direction above is only what makes it visible.

## What is already known and does NOT close it

- **The margin over H1's own assumption is `1/n`.** H1 assumes `kappa >= 1`;
  the closure needs `kappa >= (n-1)/n`. At `n = 131` the entire robustness of
  the closure beyond its own assumption is **0.76 %**, and it is **zero in the
  limit**. The rhetoric "five times below Rojas' 4.876" describes a safety
  factor that does not exist in the parameter the closure depends on.
- **A linear-time eliminant solver sits at `kappa = 1`** — on the boundary,
  inside the closure at finite `n` by `1/n` and outside it asymptotically.
  `H-QSP-5540d7`'s own `assumptions` block already concedes: *"A solver model in
  which the cost does not grow with `d` is not excluded by (E)."*
- **The `m >> 1` idealisation does not hide the answer, and errs the safe way.**
  Proposition 7 instantiated in full at integer `m` (carrying `m!`,
  `m^{5.188}` and `3^{kappa m^2}`, which the asymptotic form drops), minimised
  over every `n'` not dividing `n` and `m` in 2..59 at `beta` equal to (B)'s
  bound and `kappa = 4.876`, gives a minimum of `2^166.43` at `(n' = 3, m = 2)`
  against the idealised `2^117.67` and rho's `2^60.9` ([[KN-LIT-096]]); dropping
  `3^{kappa m^2}` entirely still gives `2^126.24`. The idealisation is generous
  to the attacker by about 49 bits, which for a non-existence claim is the
  conservative direction. **All of that is conditional on `kappa = 4.876` and
  therefore on the very quantity in question.**

## Cheapest discriminating test

**Measure the eliminant degree at the smallest cell, and stop guessing.**

The scheduled validation route `IDEA-20260916-b84e2d` proposes sampling
`(n, m, d)` in `{17, 23, 29, 41} × {2, 3, 4} × {2, 3}` and comparing the measured
univariate degree and solution count against `2^{m(m-1)} d^{m(m-1)/2}`. It is a
**proposal at `status: proposed`, never designed into a frozen contract**, and
carries a recorded engine impediment: no Gröbner or resultant engine is
installed (`sage`, `magma`, `macaulay2`, `singular`, `msolve`, `ntl_or_flint`
all absent, re-confirmed by every `environment.json` of `EXP-QSP-33b442`).

**That impediment may be larger than the cheapest informative cell requires.**
At `m = 2` the system is two equations and a **resultant suffices** — no Gröbner
basis, no specialised engine. `M(E)` at `m = 2` is `2^2 d` — 8 at `d = 2`, 12 at
`d = 3` — so the discriminating measurement is: *does the eliminant actually
have degree `M(E)`, or does it collapse?* A collapse by a factor growing with
`d` is H1's own stated `falsification_condition`. A single afternoon at
`(m, d) = (2, 2)` and `(2, 3)` would convert the question from unanswerable to
measured, and it does not need the blocked engine.

Design against the obvious failure mode before running it: `m = 2` may be too
small for the asymptotic regime the exponent describes, so a non-collapse at
`m = 2` is weak evidence for `kappa >= 1` while a **collapse** at `m = 2` is
strong evidence against it. The test is therefore asymmetric, and that asymmetry
should be stated in the contract rather than discovered afterwards.

## What would close this

Either of:

1. **A retrieved or derived lower bound** on the eliminant degree, or on the
   solving cost, for the structured chain systems — not for generic supports.
   This would promote the closure reading (E) of `H-QSP-5540d7` from a bare
   heuristic to a conditional result with a supported condition.
2. **A measured collapse**: an executable cell whose univariate degree or
   solution count falls below `M(E)` by a factor growing with `d`, i.e. a solver
   with `kappa < (n-1)/n`. That would refute (E)'s *conclusion*, not merely its
   stated reason, and would be a far more valuable result than the closure — it
   would reopen the quasi-subfield line that (E) claims to close.

Until one exists, (E) is a bare heuristic plus the unconditional bound (B), with
`1/n` of margin, and it may not move toward `supported`
(`DEC-20260917-793ae2`).

## What this entry does NOT claim

- **Not that H1 is false.** H1 may well be true; its `formal_statement` and
  `falsification_condition` are correctly written as a heuristic and name
  exactly the right test. What is established is that the *record's support* for
  H1's load-bearing direction is absent once `recalled` citations are honoured.
- **Not that the quasi-subfield bound is in doubt.** (A) and (B) of
  `H-QSP-5540d7` are unconditional, need no cost model, and survived every
  attack in the review round of `TASK-20260917-43701b` — 0 violations across
  roughly 340 000 candidates from two implementations with no shared lineage.
  This open problem is entirely about the *closure reading* (E).
- **Nothing about any deployed curve.** No curve, group or point was constructed
  in any artifact cited here. rho on ECC2K-130 stands at `2^60.9`
  ([[KN-LIT-096]]) and nothing here touches it.

## Provenance

Raised by the review round of `TASK-20260917-43701b`, joint J6, owned by
`TASK-20260917-52b4e6` (`review-breakthrough`, `max` effort, independent
session), whose objection O1 produced the direction finding at **derivation**
tier — a checkable argument over verbatim quotations from two frozen source
texts plus exact rational arithmetic. Composed into `EV-QSP-a6aa4b` and promoted
by `DEC-20260917-793ae2` (decision: `weaken`).
