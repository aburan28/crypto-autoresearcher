---
id: KN-OPEN-5e3dd0
type: open_problem
title: >-
  A Frobenius-stable orbit-union factor base on a binary Koblitz curve DOES
  have an explicit bounded-degree algebraic membership description -- the
  weight-bounded set in a normal basis, via Hamming ideals -- and at n <= 19,
  m = 2, w = 2 its Groebner oracle resolves only at depth n - 1 and costs
  |F_w|^1.9-2.5 calls against the exhaustive oracle's |F_w|. OPEN: does any
  membership presentation of a Frobenius-stable non-subspace base yield a
  decomposition system that a Groebner engine resolves before enumeration
  does, at m >= 3, at w >= 3, with a stronger engine, or at n = 83?
tags: [ecdlp, frobenius, koblitz, subfield-curve, index-calculus, factor-base, orbit-union, normal-basis, hamming-weight, hamming-ideal, point-decomposition, semaev, weil-descent, groebner, prange, isd, negative-result, toy-tier, external-provenance, open]
confidence: unverified
confidence_note: >-
  `unverified` because the measurement it rests on, EV-ICPERF-988da7, is an
  external-provenance record of strength `preliminary` that no reviewer in
  this program has read (the ceiling DEC-20260918-4b7e21 set for records of
  that class). The structural statement in the title -- that the
  weight-bounded set in a normal basis is Frobenius-stable with a popcount
  membership test -- is a two-line argument and would be `established` on
  its own; it is held at the record's grade because the entry is about the
  measurement.
status: open
source_refs: [KN-LIT-316c94]
internal_refs: [EV-ICPERF-988da7, EXP-ICPERF-3fa3c7]
related_refs: [KN-OPEN-095df5, KN-FIND-47da4e, KN-FIND-b9a41d, EV-FROB-b6e1e9, RQ-FROB-7d8dd4, GOAL-FROB-6333a9, GOAL-ICPERF-e6b6a4, RQ-ICPERF-94c86e, KR-IC-b0fcda, KN-LIT-796]
proof_status: empirical_only
proof_refs: []
added: '2026-09-30'
superseded_by: null
---

## Statement

`RQ-FROB-7d8dd4` asks whether Frobenius structure can be pushed into the
expensive stage of subfield-curve index calculus. At prime `n` the linear
route is empty (`KN-FIND-b9a41d`; at `n = 131` the stable subspaces have
dimensions `0, 1, 130, 131`), orbit unions are available at any size, and
`KN-FIND-47da4e` measures the `(representative, shift)` parameterisation of
a general orbit union and finds it cost-neutral. `KN-OPEN-095df5` then says
what an orbit union lacks is "a cheap algebraic description the
decomposition solver can use", and looks for one in the Couveignes–Lercier
construction.

**One such description exists without any construction.** In a normal basis
`{α^{2^i}}` of `F_{2^n}` the Frobenius is a cyclic shift of coordinates, so

```text
    F_w = { P ∈ E(F_{2^n}) : wt_NB(x(P)) ≤ w },   |{x : wt(x) ≤ w}| = Σ_{j≤w} C(n, j),
```

is a Frobenius-stable orbit union at every `n`, needs no storage
(membership is a popcount), and by La Scala–Marchesin–Tiwari
(`KN-LIT-316c94`) has a membership ideal with `O(n)` auxiliary variables
and generators of degree at most `⌊log₂ n⌋ + 1` (FC-Hamming), or quadratic
generators with `O(n log n)` variables (C, QFC). The unlifted description is
the monomial ideal "every degree-`(w+1)` monomial vanishes", `C(n, w+1)`
generators of degree `w + 1`. So *explicit* and *bounded-degree* are not
the scarce properties.

**What is scarce is a description whose descended system resolves.**
`EV-ICPERF-988da7` (external, pre-registered, every target verified against
an exhaustive oracle, zero timeouts) runs the paper's own MultiSolve/OracleT
search on Semaev's `S₃` Weil-descended in normal-basis coordinates plus two
copies of the Hamming ideal, at `n ∈ {7, 11, 13, 17, 19}`, `m = 2`, `w = 2`:

| quantity | at `n = 19` (of 19 coordinates, `|F_w| = 229`) |
|---|---|
| mean tame depth, FC / C / QFC | 17.8 / 18.2 / 18.2 |
| mean GroebnerSafe calls per target, FC / C / QFC | 113 / 135 / 135 |
| exponent of calls per target in `|F_w|`, fitted over `n = 11..19` | 1.87 / 2.43 / 2.48 |
| subspace baseline through the same solver | depth 0.0, 1.00 call |
| registered success threshold for the exponent | 0.8 |

The oracle is the exhaustive oracle with a Gröbner computation attached to
each candidate: the paper's own Classic McEliece verdict, that the Prange
point wins, transferred intact. A 16× larger per-call budget at `n = 11`
lowers the tame depth by one to two levels of eleven and does not change
the picture.

**The open question** is the negation of that measurement outside its
tested scope. Is there a membership presentation of a Frobenius-stable
non-subspace factor base on a binary Koblitz curve -- the Hamming ideals at
`w ≥ 3`, the same ideals at `m ≥ 3` with the paper's GBDecode outer loop, a
different presentation altogether, or the same system under a
state-of-the-art engine (msolve, Magma F4, M4GB) -- whose descended
decomposition system a Gröbner computation resolves at a depth bounded away
from `n`, so that calls per target grow slower than `|F_w|^{m−1}`? And what
is the tame depth of the weight-bounded family at `n = 83`, the other
repository's own ECC2K-130 confidence gate, which nothing here reaches?

## Why it matters here

`RQ-FROB-7d8dd4`'s decision target (b) wants a Frobenius-invariant
decomposition system measurably cheaper than the plain system at the same
`(q, n, m)`. `EV-FROB-b6e1e9` closed the shift-parameterised family at
`m = 2` (cost-neutral) and this record closes the weight-bounded
Hamming-ideal family at `m = 2, w = 2, n ≤ 19` (worse than enumeration by
a growing factor). Together they say that for the two natural algebraic
descriptions of an orbit union the solver either pays the `n` systems it
was meant to save or pays the enumeration it was meant to replace.
`KN-OPEN-095df5`'s search for a Couveignes–Lercier group should read this
entry first: an explicit invariant description is not what that construction
would be buying; a *resolvable* one is, and GGMP's own table 3 (280× the
solve cost for fraction-shaped bases) points the same way.

## What is already excluded (tested scope of EV-ICPERF-988da7)

- `K_0 : y² + xy = x³ + 1` over `F_{2^n}`, `n ∈ {7, 11, 13, 17, 19}`.
- `m = 2`, `w = 2`, the paper's C, FC and QFC presentations with the
  XRev-BitFold order, the naive monomial ideal as a control.
- A degree-6-truncated Boolean F4 with a `2^28` XOR budget and a `2^26`-word
  matrix cap, swept to `2^30` at `n = 11`.
- Correctness is not in question: 480 of 480 oracle answers agree with the
  exhaustive labels and every decomposition is re-verified on the curve.

Nothing at `n = 83` or `131`, nothing at `m ≥ 3`, nothing at `w ≥ 3`, no
second engine. A conclusion at any of those needs its own record.

## The cheapest discriminating tests

1. **A second engine on the frozen systems.** Export the `n = 17` and
   `n = 19` FC systems at the root and at a few tree nodes and run msolve or
   Magma F4 with the same degree cap; report tame depth in the same unit.
   If the depth moves by a factor rather than a few levels, the exponent
   verdict must be redone. The producing record predicts it will not.
2. **`w = 3` at `n = 17, 19`**, as the protocol originally registered before
   the runtime deviation to `w = 2`; a full tree has 1,160 leaves at
   `n = 19`.
3. **`m = 3` with the GBDecode outer loop**, which is the configuration the
   paper's decoder is actually designed for and the one this transfer did
   not run.

## What would close this

Either a measured cell -- same curve family, verified against an exhaustive
oracle, budget and engine stated -- in which calls per target for some
presentation grow with exponent below `m − 1` in `|F_w|` across at least
four sizes, or an argument (a first-fall or solving-degree bound on the
descended system with the Hamming ideal adjoined) that no truncated
Gröbner computation can resolve above depth `n − c` for constant `c`, which
would close the family by derivation rather than by measurement.
