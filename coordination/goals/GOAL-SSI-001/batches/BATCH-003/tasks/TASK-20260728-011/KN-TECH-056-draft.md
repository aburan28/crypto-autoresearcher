---
id: KN-TECH-056
type: technique
title: Supersingular isogeny-problem baselines, corrected against archived primary text (supersedes KN-TECH-029's classical F_p^2 figure)
tags: [isogeny-problem, path-finding, endomorphism-ring, meet-in-the-middle, claw-finding, cost-model, corpus-currency, supersession, isogeny, adjacent]
complexity: "F_p^2 unconditional: p^{1/2}*(log p)^{O(1)} time at polynomial memory. F_p^2 conditional on Heuristic 1 of the archived source: p^{1/3+o(1)} time AND memory, above a superpolynomial o(1) disclosed by the source. F_p: Otilde(p^{1/4}), carried at confidence relayed_from_abstract."
applicability: choosing the baseline a proposed supersingular-isogeny or endomorphism-ring attack must beat
source_refs: [KN-TECH-055, KN-LIT-078, KN-TECH-029]
supersedes: KN-TECH-029
confidence: reported
added: 2026-07-28
superseded_by: null
---

## Why this entry exists

`KN-TECH-029` records the classical baseline for the supersingular isogeny
problem over `F_{p^2}` as *"expected Otilde(p^{1/2}) time and space"* in its
`complexity` field and in its "Complexity landscape" section. That figure is
**stale against this repository's own archived primary text**. It is not wrong
as a statement about meet-in-the-middle; it is wrong as a statement about the
best known complexity of the problem.

`KN-TECH-029` is **superseded, not edited.** It remains in the corpus exactly as
written, per the immutability rule of `AGENTS.md`. This entry is the current one.

This is a **corpus-currency supersession sourced to archived primary text**. It
is not a `KN-FIND` promotion of an internal finding, and it asserts no result of
this program's own.

## The archived primary text

All quotations below are from
`inputs/P13-WESOLOWSKI-2026/paper_fulltext.md`, a frozen verbatim source record
in this repository, and were read directly with the line locators shown.

**Line 1 (title):**

> THE SUPERSINGULAR ISOGENY PROBLEM IN TIME AND MEMORY p^{1/3+o(1)}

**Line 11 (abstract):**

> We prove that under a plausible heuristic assumption (on the smoothness of
> certain random integers), the supersingular isogeny problem can be solved in
> time and memory p^{1/3+o(1)}. This improves upon the previous best complexity
> of p^{1/2} · (log p)^{O(1)}.

**Line 19 (Theorem 1.1):**

> Assuming Heuristic 1, there is a Las Vegas algorithm which, given a
> supersingular elliptic curve E/F_{p^2}, finds a non-scalar endomorphism
> α ∈ End(E) \ Z in expected time and memory p^{1/3+o(1)}.

**Line 23 (Corollary 1.2):**

> Assuming Heuristic 1, there is a Las Vegas algorithm of expected complexity
> p^{1/3+o(1)} for the supersingular endomorphism ring problem ... and for the
> supersingular isogeny problem ...

**Line 25 (what the previous baseline was):**

> The previous best algorithms to solve them had complexity p^{1/2} · (log p)^{O(1)},
> starting with [21]. This complexity had stayed remarkably stable, with
> subsequent improvements only impacting the logarithmic cofactor [15, 24, 26, 40].

## The corrected baseline

**Two tiers, and they must not be collapsed into one.**

1. **Unconditional tier — `p^{1/2} · (log p)^{O(1)}` time at polynomial memory.**
   Unchanged. The source itself places *"the classic p^{1/2+o(1)} algorithms with
   polynomial memory like [21]"* at this point (line 39). A proposed attack that
   reaches `p^{1/2+o(1)}` matches a baseline established in 1997 and improves
   nothing.

2. **Heuristic-conditional tier — `p^{1/3+o(1)}` time AND memory, conditional on
   Heuristic 1 of the archived source.** This is the current best known
   complexity of the supersingular isogeny problem, the supersingular
   endomorphism ring problem, and the `OneEnd` problem (Theorem 1.1 plus
   Corollary 1.2 via the cited reductions `[35, Theorem 1]` and
   `[35, Proposition 8.5]`). **It is conditional and must never be quoted
   unconditionally.**

**Three qualifications the source discloses about its own result, carried inline
because dropping any of them misrepresents it. All from line 39 and line 13.**

- *"the overhead hiding in the o(1) term is superpolynomial, much larger than the
  previous (log p)^{O(1)} cofactor"* (line 39). **No concrete-parameter
  conclusion follows from the exponent alone**, and no figure computed above
  that `o(1)` is a threshold anyone can evaluate at a realisable `p`.
- *"its memory cost is essentially as high as the complexity p^{1/3+o(1)}, a
  serious obstacle for any deployment of the algorithm on instances of
  cryptographic size"* (line 39). Memory is **not** polynomial in this tier.
- *"The impact on concrete parameter sets remains to be clarified"* (line 13).
  The source does not claim a break.

**The time–memory interpolation, quoted rather than paraphrased (line 39):**

> The time-memory tradeoff of van Oorschot–Wiener [43] solves a claw-finding
> problem of this size in time essentially √(N^3/w) = p^{1/2+o(1)}/w^{1/2} with
> memory w. This allows one to interpolate between the p^{1/3+o(1)} high-memory
> algorithm presented here and the classic p^{1/2+o(1)} algorithms with
> polynomial memory like [21].

So the two tiers are endpoints of one curve, not rival algorithms. A candidate
claiming an advantage must say **where on that curve** it sits.

**Parallelism (line 39, line 41):** *"The algorithm parallelizes perfectly"*, and
the van Oorschot–Wiener variant gives *"an attack in time p^{1/2+o(1)}/(w^{1/2} n)
with memory w and n parallel processors."*

## What is NOT corrected here

- **The `F_p` figures.** `KN-TECH-029`'s Delfs–Galbraith line — descend to the
  `F_p`-rational subgraph for `Otilde(p^{1/4})` — is **not superseded by this
  entry**, because the archived source does not address it. It remains at
  `KN-LIT-078`'s own stated confidence, `reported` / relayed from the abstract.
  `GOAL-SSI-001` `TASK-20260728-011` attempted the primary-source fetch and
  obtained the descent structure (one long random walk from each of `E_0`, `E_1`
  *"until we hit a supersingular curve defined over F_p"*) but **not** the
  quantitative memory profile of the inner search, and observed that two
  retrievals returned two different abstracts for the same identifiers. **Do not
  upgrade the `F_p` confidence label without the paper in hand.**
- **The quantum figures.** `KN-TECH-029`'s quantum `Otilde(p^{1/4})` line and its
  CSIDH-side subexponential line are untouched here.
- **The scheme scope.** Per line 31 the source names the affected set — CGL,
  the SQIsign family, GPS signatures, PRISM, ⊗-MIKE — and per lines 33–37 names
  as out of range *"all group-action-based constructions like CSIDH ... as well
  as torsion-based key exchanges like M(D)-SIDH, FESTA and POKE"*, on the stated
  ground that *"other cryptanalytic algorithms dominate the security analysis of
  these schemes"*. That scope is the source's, not this program's, and must not
  be widened when this entry is cited.

## How to use this entry

When benchmarking a proposed mechanism against the supersingular isogeny or
endomorphism ring problem:

- Benchmark **time exponents**: `p^{1/2+o(1)}` unconditional, `p^{1/3+o(1)}`
  conditional on Heuristic 1, over `F_{p^2}`.
- State which tier you are beating, and if you beat only the unconditional tier
  say so, since the conditional tier already sits below it.
- Do **not** benchmark against a full-cost figure computed above the disclosed
  superpolynomial `o(1)`; it is a threshold nobody can evaluate at any realisable
  `p`.
- Charge memory beside time. The conditional tier's memory is `p^{1/3+o(1)}`,
  not polynomial.

## Applicability limits

- The `p^{1/3+o(1)}` tier is **conditional on Heuristic 1** of the archived
  source. This program has neither validated nor challenged that heuristic, and
  holds no evidence bearing on it.
- Every figure here is asymptotic. Nothing in this entry establishes concrete bit
  security for any parameter set, and the source explicitly declines to
  (line 13, line 43: the concrete estimates of Section 4.1 *"make optimistic
  assumptions on the actual cost of certain steps, hence should not be
  interpreted as accurate predictions"*).
- This entry is a **corpus-currency correction**. It reports what an archived
  primary source says. It contains no result of this program's own, no empirical
  claim at any scale, and no cryptanalytic result.
- Provenance of the correction: `GOAL-SSI-001` correction C-β, raised in
  `TASK-20260728-005`, carried through `TASK-20260728-007` and
  `TASK-20260728-009`, and drafted with independently verified line locators in
  `TASK-20260728-011`. Zero curve computation was performed in any of them.
