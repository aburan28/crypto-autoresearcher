---
id: KN-OPEN-2c095b
type: open_problem
title: Is the multiplicative-order deficit of a curve-derived lambda a fact about CM arithmetic, or a fact about small integers?
tags: [ecdlp, ordinary-curves, cm, endomorphism, kernel-field, multiplicative-order, matched-null, null-design, heuristic-validation, toy-scale, open]
confidence: unverified
status: open
source_refs: [EV-ICINV-c68f13, DEC-20260807-4261e3, H-ICINV-82ee6a, EXP-ICINV-fcb497, RQ-ICINV-475b5e, GOAL-ENDO-001]
added: 2026-08-07
superseded_by: null
---

## Statement

`H-ICINV-82ee6a`'s heuristic **HEUR-ORD-1** says that for the Z[π]-minimal
non-scalar endomorphism `α = u + vπ` of a uniformly sampled ordinary `E/F_p`,
the scalar `λ = −u·v⁻¹ mod d` (`d = deg α`) "behaves with respect to
multiplicative order like a uniformly random element of `(Z/d)*`".
`EXP-ICINV-fcb497` tested exactly that, against a null drawn uniformly from
`(Z/d)*` on the same `d`. The measurement returned the predicted null at two of
three seeds — and a **deficit** of `log m / log d` against that null
(`m = ord_d(λ)` runs *smaller* than a random unit's order) at the three smallest
decades at all three seeds, `D ∈ [0.066, 0.121]`, reaching `D ∈ [0.104, 0.121]`
at `p = 16381` at 3/3 seeds, above the design's declared resolvable floor of
`0.10`.

The open question is what that deficit is a fact *about*, and the design cannot
say, because it never drew the comparison that would decide:

> **Does the multiplicative order of a curve-derived `λ` differ from that of a
> uniformly random *small integer* of matched magnitude modulo the same `d` —
> or is the entire deficit against the uniform-unit null explained by the fact
> that curve-derived `λ` are small integers and small integers are not uniform
> units?**

## Why the question exists — a derivation, not an observation

This is forced by the frozen contract's own identities, and is checkable without
running anything:

- **T3.** `min_{v ≠ 0} N(u + vπ) = |D|/4` up to rounding, attained at `v = ±1`,
  `u = round(−t/2)`.
- **λ-rule.** `λ = −u·v⁻¹ mod d`. With `v = −1` this is `λ = u`.
- Therefore **`λ = ±round(t/2) mod d`**, and by Hasse `|t| ≤ 2√p`, so
  **`|λ| ≤ (|t|+1)/2 ≤ √p + 1 ≈ √d`**.

Two consequences follow immediately, and both are visible in the run artifacts:

1. **The curve-derived `λ` lives in a window of size `O(√d)`, not in all of
   `(Z/d)*`.** Confirmed at `p = 16777213`: `u = 455, v = −1, λ = 455,
   d = 16570188`, and `d = 455² − 455·910 + p` gives `t = 910 = 2·455` — λ is
   exactly `t/2`. The matched null, by contrast, draws uniformly from `(Z/d)*`,
   i.e. from a set roughly `√d` times larger.
2. **`m` depends on the curve only through `t`.** Hence the observed `(d, m)`
   collisions (164–939 distinct pairs per 1000 instances, rising with `p`), and
   hence an effective number of distinct objects per decade of order `√p` rather
   than the nominal `n = 1000`.

So a deficit against a uniform-unit null is ambiguous between two entirely
different statements — one about elliptic curves, one with no elliptic curve in
it at all:

- **(CM reading)** the CM structure makes the kernel-generator field degree
  small more often than chance; or
- **(integer reading)** small integers simply have smaller multiplicative order
  than uniform units mod the same `d`, and any construction producing small `λ`
  would show the same deficit.

## What the 13 runs of EXP-ICINV-fcb497 can and cannot distinguish

**Can, partially.** The deficit is largest exactly where the curve-derived
sample is most atomic (distinct `(d, m)` pairs 167 → 275 → 435 → 596 → 762 →
852 → 923 across `p = 4093 … 16777213`) and drops below the critical value at
`p = 16777213` at all three seeds. That is consistent with a small-`d`
arithmetic artefact, which the contract pre-declared as an interpretation limit.

**Can, negatively.** Pure noise at the resolution floor is *excluded as a
complete explanation*: `p = 16381` reaches `D ∈ [0.104, 0.121]` at three
independent seeds, at or above the declared floor.

**Cannot, at all.** The CM reading versus the integer reading. No null over
small integers of matched magnitude was ever drawn, so nothing in the 21 000
measured instances bears on it. An effect that genuinely shrinks with `p` and an
artefact that shrinks with `p` are also indistinguishable from seven decades all
below `2^24`.

## Cheapest discriminating test

Cheap in the literal sense — the whole of `EXP-ICINV-fcb497` cost 25.1 seconds
of wall clock and 0.007 CPU-hours.

Re-run the frozen STAGE-3 measurement with **one addition and nothing else**: a
*second* null, drawn from integers `a` with `|a| ≤ (|t|+1)/2` and
`gcd(a, d) = 1`, on the **same** `d`, through the identical order code path,
written to disk before any KS statistic is read. Pre-register the discriminator
before drawing:

- curve-derived indistinguishable from the **small-integer** null, both sitting
  below the uniform-unit null → **integer reading**; the deficit is not about
  curves, and HEUR-ORD-1 must be *restated* against the correct null rather than
  reported as validated against the wrong one;
- curve-derived sitting significantly **below the small-integer null too** →
  **CM reading**; that is the interesting signal, it is a fact about ordinary CM
  arithmetic, and the family carrying it must be characterised by `(t, D, f, d)`.

Design elements to fix in advance, because they are what would spoil it:
stratify by trace so the `O(√p)` effective sample size is visible instead of
hidden behind `n = 1000`; keep the planted `m = 2` control and the `m = 1`
nearby-object fixture blocking; keep the three seeds; and state that a null
result here is a *restatement* of HEUR-ORD-1, not a refutation of it.

## Related, and deliberately not merged into this entry

- **The `|t| ≤ 2` family.** For `|t| ≤ 2` the derivation above forces
  `λ ∈ {1, d−1}` and `m ∈ {1, 2}`: the kernel of the minimal non-scalar
  endomorphism is fully rational. Observed in the small-order tail at
  `p = 4093` and `p = 16381`. This does **not** falsify HEUR-ORD-1 — the
  trace-density of `|t| ≤ 2` is `O(1/√p) → 0`, which is exactly the
  density-zero exceptional set H1 asserts exists — and it is not an attack,
  because `H-ENDO-001`'s scalar action on the prime-order subgroup bites
  regardless. It is a separate object with a separate fate.
- **The STAGE-0 question** — over which field the square-root Vélu `Õ(√d)`
  operation count is stated — is *not* filed as an open problem, and should not
  be. It is a retrieval task blocked by HTTP 403 Cloudflare interstitials on
  both eprint PDFs, not a mathematical unknown. It is tracked as next action N4
  of `DEC-20260807-4261e3`. Until it is answered, cost corollary CC of
  `H-ICINV-82ee6a` stays UNDETERMINED.

## What would close this

Either (i) the discriminating replication above, at three seeds and with both
nulls, showing which null the curve-derived sample matches; or (ii) a derivation
bounding the distribution of `ord_d(a)` for `a` uniform in `[1, √d]` against
that for `a` uniform in `(Z/d)*`, which would answer the integer half without
touching a curve. Neither exists in this campaign. Until one does, the deficit
observed by `EXP-ICINV-fcb497` is recorded as **unresolved**, and HEUR-ORD-1's
validation is `preliminary` and toy-scale with this confound outstanding
(`EV-ICINV-c68f13`).

## Scope

Ordinary short-Weierstrass curves over prime fields, `p < 2^24`, `α` restricted
to `Z[π]`, claim tier **toy**. Nothing here transfers to supersingular curves,
to the full endomorphism ring where the conductor exceeds 1, or to
cryptographically sized parameters, and nothing here is an attack or a speedup:
`sota_delta` against `0.886·√N` is `0.0`.
