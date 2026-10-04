---
id: KN-OPEN-8f3d27
type: open_problem
title: >-
  Does the proven linear-in-n solving-degree upper bound for the unrestricted Weil
  restriction transfer to the factor-base-restricted (x_i in V) descent of the
  binary summation polynomial, and is that restricted solving degree bounded by
  some f(m)?
tags: [binary-curves, summation-polynomials, weil-descent, solving-degree,
  last-fall-degree, factor-base-restriction, groebner, characteristic-two, open,
  ecdlp, sub-question, exponent-stake]
confidence: reported
status: open
source_refs: [KR-IC-889857, KN-LIT-f37b9a, KN-OPEN-d218ec, KN-LIT-024, KR-IC-f5c584,
  KR-IC-fbdb61, KN-LIT-4e8513, KN-OPEN-7f0511, KN-FIND-936151, H-SEMBIN-c7e1d4,
  DEC-20261003-4e91b7, TASK-20261001-9b3e70, TASK-20261002-9e27f4]
added: 2026-10-03
superseded_by: null
---

## Provenance and relation to existing entries (read this first)

Filed by `DEC-20261003-4e91b7` (R5) as a **narrowed sub-question, linked rather
than standalone**. Candidate OPEN-B of
`coordination/tasks/TASK-20261001-9b3e70/DERIVATION.md` section 5 was a
**duplicate as worded** (validator report `VAL-20261003-17b1e4`, joint JR-4,
defects B-1 to B-4):

- its solving-degree half **is** the open gap already carried by
  `KN-LIT-f37b9a` ("the gap between a proven linear upper bound and a
  conjectured constant") and by the frontier dispute row `KR-IC-889857`;
- its first-fall half is recorded as **bounded independently of `n`**
  (`KN-LIT-024`, `KR-IC-f5c584`; abstract-level);
- it conflated solving degree with first-fall degree, which the corpus records as
  distinct invariants (`KN-LIT-4e8513`, `KN-OPEN-7f0511`, `KN-FIND-936151`);
- `KN-OPEN-d218ec` is its Semaev-Assumption-1 special case.

This entry records **only** the residue those entries do not state: the
`x_i in V` restriction and the transfer of the proven linear upper bound to it.
Work on the general dispute belongs to `KR-IC-889857` / `KN-LIT-f37b9a`; work on
`d_F4 <= 4` belongs to `KN-OPEN-d218ec`.

`confidence: reported` because the classifications above rest on corpus entries
whose own provenance is mostly abstract-level; the validator's classification
records what the corpus says, not a verification of those papers.

## Statement

For the factor-base-restricted Weil descent over F_2 of the summation polynomial
`S_{m+1}` on a binary curve `E/F_{2^n}`, `n` prime, with `x_i in V`,
`dim V = ceil(n/m)`, and the field equations adjoined:

1. **(Transfer.)** The solving degree of the **unrestricted** Weil restriction is
   at most `n * reg(F^h) - n + 1`, linear in `n` (`KN-LIT-f37b9a` Cor. 4.12, as
   that entry records it). Does a bound of that form hold for the
   **V-restricted linear section**? This is not recorded anywhere in the corpus.
2. **(Boundedness.)** Is `sd_degrevlex` of the restricted system bounded by some
   `f(m)` independent of `n`? Equivalently, where `KR-IC-fbdb61`'s last-fall
   conditions hold, is `max.GB.deg` bounded (`sd = max{d_F, max.GB.deg}`,
   `KN-LIT-4e8513` Thm 3.1)?

**Known, and not the question:** first-fall degree is bounded independently of
`n` (`KN-LIT-024`, `KR-IC-f5c584`).

## Resolution criterion

- Part 1 is settled only by proof (or by a counterexample family to the linear
  form).
- Part 2 is settled only by proof. Measurements at `n` in about `[17, 41]` can
  **falsify a stated** `f(m)` (for example Semaev's 4 at `m = 2`, which is
  `KN-OPEN-d218ec`'s question) and can bound `f` from below. They cannot prove or
  refute "bounded by some `f(m)`".

## Exponent stake

Possible: a proof of part 2 would make the restricted index calculus
heuristically subexponential, which is the exponent-moving claim the FFDA
dispute is about. Part 1 alone gives a rigorous upper bound and moves no
exponent. This is one of the two places in the `GOAL-SEMBIN-5078bc` lane where
an exponent can move (`DEC-20261002-7a3f19` R10).

## What must NOT be said in the meantime

- **Not** "solving degree grows with `n`" or "is bounded" from finite-`n` data.
- **Not** "first fall is open": it is recorded as bounded.
- **Not** that this entry is the FFDA dispute; it is the restriction-transfer
  residue of it.
- Nothing here is a statement about the security of any curve.
