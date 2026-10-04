---
id: KN-OPEN-095df5
type: open_problem
title: "Is there a commutative algebraic group over F_2 with a rational point of order 131 that admits an explicit Galois-invariant factor-base description, and what degree does the descended system reach? Both Couveignes-Lercier constructions GGMP writes down are excluded at n = 131 over F_2 by their own stated conditions, and no abelian variety of dimension <= 4 has 131 dividing its point count -- so the only surviving route is the one those authors leave as a conjecture"
tags: [ecdlp, ecc2k-130, koblitz, subfield-curve, index-calculus, factor-base, frobenius, galois-invariant, couveignes-lercier, algebraic-torus, abelian-variety, weil-polynomial, honda-tate, characteristic-two, n-131, open]
confidence: unverified
status: open
source_refs: [KN-LIT-796]
source_refs_note: >-
  KN-LIT-796 is this corpus's Galbraith-Granger-Merz-Petit entry and was seeded
  at ABSTRACT level, with its own note asking for an upgrade after a careful
  read. Its full text WAS read in the session that raised this entry -- section
  4.2, lemma 4.1, lemma 4.2, example 5.1, table 3 and the conclusion are quoted
  or cited below by number -- but that entry is not amended here, because a
  literature record is corrected by superseding it and that is a separate task.
  Couveignes-Lercier itself was NOT read: it is known here only through GGMP's
  reproduction of it, which is why every statement about their framework below
  is attributed to GGMP section 4.2 rather than to them.
internal_refs: [EV-FROB-b6e1e9, KN-FIND-47da4e, RQ-FROB-7d8dd4]
related_refs: [IDEA-20260918-9abf42, IDEA-20260918-6c07e1, RQ-QSP-f9bbdb, KN-LIT-4fe9d2, KN-LIT-096]
proof_status: derivation
proof_refs:
  - analysis/couveignes-lercier-131/weil_census.py
  - analysis/couveignes-lercier-131/exact_targets.py
proof_status_note: >-
  `derivation`, and the two halves differ in strength. The exclusion of the two
  WRITTEN constructions is arithmetic on integers taken from conditions quoted
  from GGMP section 4.2 and needs no computation at all. The abelian-variety
  exclusion is a checkable enumeration with an exact real-rootedness test, whose
  scripts are cited above; it is `derivation` rather than `certificate` because
  nothing machine-verifies the enumeration's completeness argument, and it is
  bounded at dimension 4 by cost.
added: '2026-09-21'
superseded_by: null
---

## Statement

`GOAL-FROB-6333a9` and `RQ-FROB-7d8dd4` ask whether Frobenius structure can be
pushed into the expensive stage of subfield-curve index calculus. At the
ECC2K-130 degree the linear route is empty: `ord_131(2) = 130`, so the only
Frobenius-stable `F_2`-subspaces of `F_{2^131}` are the four of dimension
`0, 1, 130, 131` (`IDEA-20260918-9abf42`). Orbit unions remain available at any
size because 131 is prime, and `KN-FIND-47da4e` measures the natural
parameterisation of those and finds it cost-neutral.

That leaves one family in the literature that could supply a Frobenius-invariant
factor base with a genuine low-degree algebraic description: the
Couveignes–Lercier construction, which builds Galois-invariant subsets of
`F_{q^n}` from a commutative algebraic group `G/F_q` carrying a rational subgroup
`T` of order exactly `n`, via the quotient isogeny `G → G/T`. GGMP section 4.2
reproduces it and turns it into factor bases.

**The open question is whether any such group exists over `F_2` at `n = 131`,
with explicit enough translation formulae to write the membership condition, and
what degree the descended summation-polynomial system then reaches.**

## Why `q = 2` is forced, so the question is this narrow

The Frobenius that is an endomorphism of a binary Koblitz curve is the 2-power
one, so the Galois group acting on the factor base is `Gal(F_{2^131}/F_2)`, of
prime order 131. An invariant set must be invariant under all of it. There is no
intermediate base field to retreat to, because 131 is prime.

## What is already excluded, and it is the whole of the written literature

Both instantiations GGMP section 4.2 writes down need a **one-dimensional** group
with a one-coordinate addition law, and both fail at `n = 131` over `F_2` on
integers alone:

| construction | stated condition | at `q = 2` | admits 131 |
|---|---|---|---|
| dimension-1 torus | `n` divides `q + 1` | `q + 1 = 3` | no |
| elliptic curve `H/F_q` | `n` has a squarefree multiple `N` with `N ≢ 1 mod p` and `q + 1 - 2√q < N < q + 1 + 2√q` | interval `(0.17, 5.83)`, so `N ≤ 5` | no |

No computation is involved: no multiple of 131 is at most 5, and 131 does not
divide 3.

The conjectural extension is the surviving route. GGMP section 4.2 closes by
relaying Couveignes and Lercier's own suggestion that *other* commutative
algebraic groups may each bring their own contribution. Probing that, over `F_2`
the group must have a rational point of order 131, and:

- **No abelian variety over `F_2` of dimension 1 to 4 has 131 dividing its point
  count.** At dimensions 1 and 2 no multiple of 131 is even inside the Weil range
  (`#A(F_q) ≤ (1+√q)^{2g}`, i.e. 5.83 and 33.97). At dimension 3 the only
  candidate count is 131 itself and 104 integer candidates are excluded exactly;
  at dimension 4 the candidates are the eight multiples up to 1048 and 234220
  integer candidates are excluded exactly. Real-rootedness is decided by Sturm
  sequence over the rationals, with the boundary `±2√2` split off as the factor
  `x² − 8` and approached from both sides so a root in the gap would be reported
  rather than silently classified. None was.
- **The one place 131 does appear is far out of reach of the framework.** The
  norm-one torus of dimension `φ(130) = 48` has order `Φ_130(2) =
  409368176241571`, which is divisible by 131, so an order-131 rational subgroup
  exists there. That is dimension 48 with no one-coordinate addition law, and the
  invariant set would be described by ratios in 48 variables. No degree bound on
  the descended system follows, which is exactly what this entry asks for.

## Why the degree half of the question is not a detail

Even granted a group, the construction has to beat what it replaces, and the one
measurement in the literature is discouraging. GGMP example 5.1 computes that at
`m = 3` the fraction-shaped factor base gives a Weil-descended system of degree
at most 9 against 6 for a vector space of matched size. Their table 3 times both
at `p = q = 2` and `log_q |F| = 7`, including a row at `n = 131`:

| shape | set-up | Gröbner |
|---|---|---|
| vector spaces | 5.46 s | 0.84 s |
| fractions | 96.53 s | 237.70 s |

Roughly 280 times the solve cost. Two cautions on reading that row: those runs
are explicitly **not** Galois invariant, the paper says they merely price the
shape, and the paper's own verdict is that the increased cost "does not seem to
be justified by needing 1/n fewer relations". So a positive answer to the
existence half would still owe a degree bound before it was worth anything.

## The cheapest discriminating test

Two, and the first is nearly free.

1. **Push the abelian-variety exclusion to dimension 5 and 6.** The targeted
   exact search scales with the number of integer candidates whose point count is
   a multiple of 131, which is far smaller than the class count; dimension 4 cost
   234220 exact tests. A hit would be a concrete group to examine, and its Weil
   polynomial would come with the search.
2. **Read Couveignes–Lercier directly rather than through GGMP.** Their framework
   is stated for a general commutative algebraic group, and whether the
   translation formulae it needs exist for anything beyond dimension 1 is a
   question about their paper, not about this program's arithmetic. That source is
   not vendored under `inputs/` and has not been read here.

## What would close this

Either of:

1. **A written construction**: a commutative algebraic group over `F_2` with a
   rational point of order 131, explicit translations, an irreducible preimage,
   and a degree bound on the descended system at the `m` an index calculus needs.
   That would reopen the invariant-factor-base route at the ECC2K-130 degree.
2. **A proof of non-existence** for the groups the framework can actually use,
   rather than an enumeration bounded at dimension 4. The natural form is a
   statement about which orders of rational torsion are achievable over `F_2` by
   a group with a one-coordinate addition law.

## What this entry does NOT claim

- **Not that no such group exists.** The enumeration stops at dimension 4, and
  the dimension-48 torus shows order-131 subgroups do exist once dimension is
  free. What is established is that the written constructions are unavailable and
  that the small-dimension abelian varieties are empty.
- **Not that the abelian-variety census is complete as a class enumeration.**
  `weil_census.py` reproduces the known isogeny-class counts at dimension 1 (5)
  and 2 (35) but finds 211 where the LMFDB isogeny-class search reports 215 at
  dimension 3, a disclosed gap of four classes attributed to numerical
  root-finding at the boundary. The exclusion above does **not** rest on that
  script: `exact_targets.py` enumerates only the candidates whose point count is a
  multiple of 131 and decides them exactly, so its zero is independent of the
  gap. The 215 figure is relayed from that database, not recomputed here.
- **Nothing about any deployed or challenge parameter.** No curve, group or point
  is constructed anywhere in the cited scripts. rho on ECC2K-130 stands at
  `2^60.9` (`KN-LIT-096`) and nothing here touches it.
- **Not a closure of anything.** `RQ-FROB-7d8dd4` stays open, and this entry
  narrows one family within it rather than answering its decision target.
- **No claim about Couveignes–Lercier's own text.** Every condition quoted is
  GGMP's reproduction of it.

## Adjacent readings from the same source read, recorded so they are not lost

Neither is part of this entry's statement and each would need its own record.

- **The `ord_n(2)` size-control obstruction is in GGMP section 4.1, but 131 is
  not named there.** The paper says that restricting to Galois-invariant vector
  spaces means losing fine control over the factor-base size, and that the
  construction is easy only when the order of 2 modulo `n` is small. It does not
  instantiate that at 131. `DEC-20260916-3c0cf5` ranked `IDEA-20260915-8fe0ef`
  behind other work partly because whether item (1) of its `what_is_new` — the
  trace-parity confinement forcing even `m` — was already in this paper was
  unchecked. It is not: the full text contains nothing on trace parity, cofactor
  classes or the parity of `m`.
- **Lemma 3.3's hypothesis looks narrower than its statement.** The lemma
  concludes that Frobenius applied to one relation over a `Frobenius`-invariant
  base of dimension `n'` yields at most `n'` independent relations, for any
  divisor `ℓ` of `X^n − 1`. Its proof needs `ℓ(π)` to annihilate factor-base
  points. On the recorded `n = 17` cell of `IDEA-20260915-8fe0ef` (`r = 65587`,
  `λ = 17184`) both degree-8 divisors of `Φ_17` evaluate to nonzero at `λ` while
  `Φ_17` itself evaluates to zero, which is consistent with the conclusion
  holding only for `ℓ = Φ_n`. Not adjudicated; a reader with the paper open
  should check it before any record leans on that lemma.

## Provenance

Raised in one interactive session while testing what would change the assessment
that no usable Frobenius-invariant factor base exists at the ECC2K-130 degree.
The scripts under `analysis/couveignes-lercier-131/` are committed with this
entry and are content-bound in the frontmatter's `proof_refs`; they are not
harness runs and no `RUN-*` record exists for them. No validator or red team in
this program has read either the scripts or this entry, which is why `confidence`
is `unverified`.
