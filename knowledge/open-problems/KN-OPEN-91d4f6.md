---
id: KN-OPEN-91d4f6
type: open_problem
title: >-
  Characteristic-2 approximate x-filters on binary curves: does the single-bucket
  gain G(M) = M * max_{c,d} pi_c(d) of an F_2-linear x-functional filter grow
  without bound on the prime-order subgroup?
tags: [binary-curves, characteristic-two, wagner-k-tree, generalized-birthday,
  sum-compatible-filter, bucket-gain, artin-schreier, trace, halving, open, ecdlp,
  exponent-stake]
confidence: unverified
status: open
source_refs: [KN-FIND-ffe1df, H-SEMBIN-c7e1d4, H-SEMBIN-83a856, KN-LIT-f6de4b,
  KR-IC-f5c584, DEC-20261003-4e91b7, DEC-20261002-7a3f19, TASK-20261001-9b3e70,
  TASK-20261002-9e27f4, TASK-20260928-62ad14]
added: 2026-10-03
superseded_by: null
---

## Provenance of this entry

Filed by `DEC-20261003-4e91b7` (R5). The text is the corrected wording of
candidate OPEN-A from `coordination/tasks/TASK-20261001-9b3e70/DERIVATION.md`
section 5, as corrected by validator report `VAL-20261003-17b1e4`
(`coordination/goals/GOAL-SEMBIN-5078bc/reviews/TASK-20261002-9e27f4/validation_report.yaml`,
joint JR-4, defects A-1 to A-3). The candidate as worded was **not** filable: it
used the bucket-averaged agreement that this program's own red team had already
retired as an observable, and it mixed `E(F_2^n)` with `<P>`.

`confidence: unverified` because every "Known" item below that is not a cited
finding is **toy scratch** from one validator session (block S3, n <= 13), not a
measurement under a contract.

## Statement

Let `E/F_{2^n}` be ordinary, `n` prime, with `E(F_{2^n}) = Z/h x <P>`, where
`l = |<P>|` is prime and `h in {2, 4}`. For maps `h_j : <P> -> [M]`, `M = 2^j`,
`j >= 2`, computable in `poly(n)` from `x(Q)` (in particular F_2-linear
x-functionals `(Tr(alpha_1 x), ..., Tr(alpha_j x))`), and a combining rule `f`,
define the **single-bucket gain**

    G(M) = M * max_{c,d} pi_c(d),   Q, R uniform in <P>,

where `pi_c(d)` is the per-bucket merge rate for bucket `c` and offset `d`
exactly as `KN-FIND-ffe1df` defines it (this entry does not redefine it). It is
the rate a Wagner level pays, because the level fixes one bucket and one offset
**after seeing `h`** (`KN-FIND-ffe1df`, red
team RT-20260803-be45a8, as measured by that line's RT-EXP-1). It is **not** the
bucket-averaged `eps = Pr[h(Q+R) = f(h(Q), h(R))]`, which is a weighted mean
over buckets and therefore bounds no Wagner attacker (`max >= mean`).

**Question.** Does `G(M)` grow without bound along `M ~ l^theta` for some
`theta > 0`?

## Known

- **On `<P>` no exact filter exists for any `M >= 2`** (Theorem C of
  `KN-FIND-ffe1df`, internal, transferred to the prime-order subgroup).
- **On `<P>` the halving trace is constant**: `Tr(x(Q)) = Tr(a)` for every
  `Q in <P>`, because every point of odd order lies in `2E`. Toy scratch: 200 of
  200 points on each of four toy curves (`VAL-20261003-17b1e4` S3). So the
  trace gives gain 1 on `<P>`.
- **On `E(F_{2^n})` the exact gain is exactly `h`**: 2 via `E -> E/2E` (the
  trace), and 4 via one point halving when `h = 4`. Toy scratch: 400 of 400
  points for the 2E criterion; 154 of 154 and 165 of 165 for the 4E filter.
  This is consistent with Theorem C's `h` bound, attained at `h = 4`. The j = 1
  exact trace filter on `E(F_{2^n})` is already a supported program hypothesis
  (`H-SEMBIN-83a856`, `DEC-20260913-92aa48`).
- `KN-FIND-ffe1df`'s additive-completion degeneracy lemma assumes `p > 2`.
  Characteristic 2, with F_2-linear x-functionals and the Artin-Schreier
  degenerate cases, is the uncovered complement. The additive Bombieri-Weil tool
  such a bound would need is recorded as largely untraced (`KN-LIT-f6de4b`).

## Resolution criterion

Either of:

1. **Positive:** an exhibited family `(alpha, f)` with `G(M)` unbounded along
   `M ~ l^theta`, measured against a SHA-based null with matched `M`, on `<P>`.
2. **Negative:** a bound `max_c pi_c <= (1 + o(1))/M` (on the single-bucket
   rate, **not** on the averaged `eps`) for all non-degenerate `(alpha, f)`,
   with the characteristic-2 Artin-Schreier degenerate cases classified.

**Measurable quantity.** `G(M)` against `j` on toy binary curves (the J3 RC5
ladder of `TASK-20260928-62ad14`, transferred), with a SHA null. **Sampling
domain is load-bearing:** the positive controls (trace at `h = 2`, one halving at
`h = 4`) work **only** when `Q, R` are sampled from `E(F_{2^n})`; sampled from
`<P>` they are silently dead. A design must run both domains and say which one
the question is asked on (`<P>`).

A level-1 bound does **not** close tree levels `>= 2` (`KN-FIND-ffe1df`,
"Level-1, not closed").

## Exponent stake

Possible. An unbounded `G(M)` on `<P>` along `M ~ l^theta` is the ingredient a
Wagner/HGJ-type tree on an approximate quotient would need; this is one of the
two places in the `GOAL-SEMBIN-5078bc` lane where an exponent can move
(`DEC-20261002-7a3f19` R10). No candidate filter is known.

## What must NOT be said in the meantime

- **Not** "approximate filters are excluded on binary curves". Theorem C excludes
  the exact case only, and only on `<P>`.
- **Not** "the trace gives a gain of 2" without the domain: on `<P>` it gives 1.
- **Not** a bound on the averaged `eps` presented as a Wagner barrier.
- Nothing here is a statement about the security of any curve.

## Related open surface

- `EXP-SEMBIN-3d9a71` (draft, not approved) measures `F_V`, the 0-fibre of the
  F_2-linear filter `x -> x mod V`. An excess of two-sum coincidences there would
  be weak first evidence of approximate sum-compatibility of that filter. It is a
  one-fibre probe and does not settle this question.
- `KN-OPEN-2f5e66` (Wagner-style generalized birthday closed for `z_R` by
  prime-order simplicity, exact case) is adjacent: a different object.
- `KN-OPEN-3c8f51` uses the `x(2E)` coset as a covariate in a degree-4
  refutation rate; adjacent.
