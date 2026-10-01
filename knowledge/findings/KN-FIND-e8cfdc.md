---
id: KN-FIND-e8cfdc
type: internal_finding
title: Repaired Teichmuller non-homomorphic contrast (H-ECDLP-6a9479 claim 3) reads as chance at toy scale, closing the EXP-ECDLP-a26bde carve-out
tags:
- ecdlp
- toy-scale
- non-homomorphic-section
- teichmuller-lift
- statistical-control
- null-result
- degeneracy-screen
- instrument-validation
confidence: established
internal_refs:
- H-ECDLP-09125b
- EXP-ECDLP-e36df2
- EV-ECDLP-5b61eb
- DEC-20260912-2a626b
- KN-TECH-73630e
- H-ECDLP-6a9479
- EV-ECDLP-95ec68
- DEC-20260911-74c9dc
- KN-FIND-85845f
proof_status: derivation
proof_refs:
- experiments/EXP-ECDLP-e36df2/design_note.md
- experiments/EXP-ECDLP-e36df2/analysis.md
added: '2026-09-12'
superseded_by: null
---

## Finding

`H-ECDLP-6a9479` claim (3) (the canonical Teichmuller-style non-homomorphic
contrast section's digit is linear in `m` "at a rate at most `3/p`, never
systematically") was left explicitly undecided by `EXP-ECDLP-a26bde`
(`EV-ECDLP-95ec68`, `DEC-20260911-74c9dc: refine`): that test design pooled
a mathematical tautology (`m=1`, the same computation invoked twice) with
genuine trials, and used a `3/p` falsification threshold below the tested
68-sample ladder's coarsest measurable nonzero rate — no outcome of it
could have discriminated "no systematic linearity" from "one coincidence."

`H-ECDLP-09125b` repairs the test design (`EXP-ECDLP-e36df2`) rather than
re-running the broken one: the `m=1` tautology is removed from the
statistic entirely; a pre-registered cross-prime screen excludes any tested
multiple whose x- or y-coordinate reduces to a global rational value of
exactly `+1` or `-1` at every one of a curve's primes simultaneously (the
only rationals that are `(p-1)`-th roots of unity for every odd prime,
hence the only possible source of a prime-independent "free" agreement
under a Teichmuller-style lift); the per-instance sample size is chosen
(`N_i = ceil(20*p_i)`, power >= 0.90 at alpha=0.01) so a 3x-chance
systematic effect is actually statistically resolvable, not merely "more
than one hit in 68 tries"; and two independently coded, differently
realized non-homomorphic contrast sections (`s_x`: Teichmuller-x/Hensel-y;
`s_y`: Teichmuller-y/Hensel-x) are tested in parallel so a degeneracy
affecting one is checkable against the other.

**Result, on 24 toy `(curve,prime)` instances (5 original curves + 1
engineered positive-control curve, primes in `[2^10,2^14)`), independently
re-derived from raw per-instance data before this decision was made
(`EV-ECDLP-5b61eb`):** both sections read as chance. Pooled
`rho_hat_x=1.016` (95% exact-Poisson CI `[0.928,1.110]`), `rho_hat_y=0.983`
(CI `[0.896,1.076]`) — both contain 1 and exclude any value `>=3`, agreeing
in verdict. A seeded pseudorandom null-object control (`s_rand`, zero
structure by construction) also reads as chance (`rho_hat=1.072`, CI
`[0.982,1.169]`), ruling out a method-level inflation independent of
anything about `s_x`/`s_y`. An engineered curve with a known, certain
`m=2` coincidence (doubling slope exactly 1, by construction) is caught by
the cross-prime screen on 4/4 of its primes, confirming the screen excludes
only the named degeneracy class and is not blind to it. A `mu0_target=40`
sensitivity re-run (curve idx 1, fully independent) reproduces the same
qualitative verdict.

Claim tier: **toy** throughout. No attack, no exponent claim: every tested
multiple is generated from a global point whose scalar is known to the
generator. This is toy-scale empirical evidence **consistent with, not a
new proof of,** `KN-TECH-73630e`'s uniqueness-of-homomorphic-section
theorem — the theorem is cited and assumed, not re-derived. This decision
concerns `H-ECDLP-09125b` alone; it does not reopen, modify, or supersede
`H-ECDLP-6a9479`, which remains `status: analyzed` with claim (3) `refine`,
an immutable record of what the earlier, unrepaired test showed.

## Methodological finding: a chi-square goodness-of-fit diagnostic can be badly misleading when the tested ladder is longer than the point's order

A secondary instrument-design lesson, reusable beyond this experiment: a
per-instance ladder of length `N_i` sampling `[m]S mod p` for `m` up to
`N_i` will, once `N_i` exceeds the point's order `n`, sample the
*same* underlying group elements repeatedly (period exactly `n`, since
`[m]S mod p` depends on `m` only through `m mod n`). Any digit computed as
a deterministic function of that point alone (not of a target quantity
that varies with a *different*, longer period) inherits the same period-`n`
periodicity. A naive chi-square goodness-of-fit test that assumes `N_i`
independent draws over `p` categories will then report a statistic
inflated by a factor tracking `N_i/n` — in this experiment, ratios from
`~19x` (when `n` is close to `p`, since `N_i=ceil(20p)` already implies
~20 cycles) up to `~726x` (when `n << p`, e.g. `n=415` against
`p=14821`) — despite there being no genuine non-uniformity finding at all.
Verified directly on three distinct `(curve,prime)` instances (two by the
experiment's own design note, a third independently by this review:
`p=7487,n=413`, observed ratio `359.92` vs. predicted `N_i/n=360.66`,
within `0.21%`). This does **not** affect a statistic whose *target*
quantity does not share the short period `n` (here, `m*d(s(S)) mod p`
cycles with the full period `p`, since `gcd(n,p)=1` and `d(s(S))` is a
nonzero residue) — confirmed here by the null-object control `s_rand`
landing in the same range as `s_x`/`s_y` despite having no reason to
inherit the periodicity argument at all. Anyone building a similar
long-ladder digit-agreement test should either bound `N_i` by a small
multiple of the point's order before running a marginal-uniformity
diagnostic, or read such a diagnostic against `dof x (N_i/n)`, not `dof`.

## What this closes and what it does not

- Closes `DEC-20260911-74c9dc`'s carve-out of `H-ECDLP-6a9479` claim (3):
  the question "is the repaired, resolution-matched test decidable, and
  what does it decide" now has a recorded, independently-verified answer
  (`EV-ECDLP-5b61eb`, `DEC-20260912-2a626b: support`, strength `strong`).
- Does **not** retroactively change `H-ECDLP-6a9479`'s own immutable
  `analyzed` status or its claim-(3)-`refine` disposition, which remains
  the correct record of what the *original*, unrepaired test showed.
- Does **not** prove `KN-TECH-73630e`'s uniqueness theorem or strengthen it;
  this is toy-scale empirical evidence consistent with it.
- No transfer beyond the tested toy scale (6 curves, 24 instances, primes
  10-14 bits) is claimed or implied.
