---
id: KN-OPEN-2e7514
type: open_problem
title: >-
  Does the fall_dim row-collapse exception occur at a STRICT-early-fall cell of
  the d=2 digit presentation, or only at the boundary cells s = 2^(m-1)?
tags: [semaev, digit-presentation, first-fall-degree, fall-dimension, row-independence, counterexample, small-prime-sweep, side-condition, open, ecdlp]
confidence: established
status: open
source_refs: [EV-PFDR-1394a4, DEC-20260904-1e27a2, H-PFDR-4148b8, EXP-PFDR-5726af]
added: 2026-09-04
superseded_by: null
---

## Statement

The fall-dimension identity of `H-PFDR-4148b8` (D4),

`fall_dim(d_ff) = m * [ C(s, a_0) − C(s, a_0 + e) ]`,

is **false as universally quantified** over all `p`, all non-singular curves and
all affine targets. An archived counterexample certificate exhibits it failing:
`m = 2`, `d = 2`, `s = 2`, `p = 13`, `E: y^2 = x^3 + 12x + 3`
(`4a^3 + 27b^2 = 5 ≠ 0`, `a, b ≠ 0`), `x_R = 11` gives `(d_ff, fall_dim) =
(5, 3)` against the frozen `(5, 4)`; a second instance is `p = 19`, `a = 2`,
`b = 15`, `x_R = 9`. Both curves pass the experiment's own filter, and at
`p = 13` all four window `x` are on the curve with `N_sol = 8`.

The mechanism is exact:

`fall_dim(D) = dim ker(m_{S~_top}) − dim Rel_D`, with
`Rel_D = { h of degree D − delta vanishing on supp(S~) }`,

and (D4) states the identity **without the hypothesis `Rel_D = 0`**. At the
counterexample, `S~` vanishes on the 8 digit vectors with `a_{1,0} ≠ a_{2,0}`,
so the linear form `a_{1,0} − a_{2,0}` kills every row and `full_rank` drops
from 4 to 3.

The repaired statement — *"… whenever no nonzero squarefree form of degree `a_0`
vanishes on `supp(S~)`; a sufficient condition is `N_sol < 2^(ms − a_0)`"* — is
**true at every draw in the package**, and the sufficient condition is **sharp**:
the counterexample sits at `N_sol = 8 = 2^(4−1)` exactly.

**WHAT IS OPEN: whether the exception can occur at a cell where the fall is
STRICTLY early (`d_ff < D_null`), or only at the boundary cells `s = 2^(m-1)`,
where `delta = n = ms` and the fall is degree exhaustion rather than a degree
fall.** The answer decides whether the repaired (D4) needs its `N_sol` side
condition **everywhere** or only at `s = 2^(m-1)`, and therefore how any
downstream statement about the fall dimension must be worded.

## Evidence bearing on it, and why it is suggestive rather than decisive

- The exception was found **twice**, both at the boundary cell `(m, s) = (2, 2)`,
  in an exhaustive sweep over all non-singular curves and all affine targets at
  `p ∈ {5, …, 41}` — 195 094 instances, 2 deviations.
- It was found **never** at the strict cell `(m, s) = (2, 3)`, in an exhaustive
  sweep at `p ∈ {11, …, 23}` — 26 000 instances, 0 deviations.
- Post hoc on the package's own records the row-independence flag
  (`full_rank < rows`) fires at **35 of 240 NULL-2 layers** and at **none** of
  the 272 Semaev or 1490 NULL-1 layers — so the collapse channel is real and
  active in this data, but only on the homogeneous block-factored null.
- The exception needs `N_sol >= 2^(ms − a_0)` and is therefore **invisible at
  the primes the battery ran** (`p ∈ {4099, 65537}`), where observed `N_sol` is
  in `{1, 2, 6}` against thresholds 8, 32, 64, 256, 512, `2^11`, `2^14`. Only a
  small-prime sweep can see it at all.

## Resolution criterion

Run the exhaustive small-prime `fall_dim` sweep at `(m, s) = (2, 3)` and
`(3, 4)` — all non-singular curves, all affine targets, `p ∈ {11..43}` at
`s = 3` and `p ∈ {17..31}` at `s = 4` — **with the row-independence readout
`(rows, full_rank)` recorded per layer and a flag for `full_rank < rows`**.

- **POSITIVE (exception exists at a strict cell):** any instance with
  `full_rank < rows` at a cell with `d_ff < D_null`. The repaired (D4) then needs
  its side condition everywhere, and the fall dimension cannot be quoted as a
  closed form at any cell without it.
- **NEGATIVE (exception confined to the boundary):** no such instance across the
  swept ranges, at which point the side condition can be attached to
  `s = 2^(m-1)` alone and the strict cells carry the closed form unqualified —
  scoped, as always, to the swept `(m, s, p)`.
- Cost: minutes of single-core Python on 64- and 4096-column matrices. No new
  tooling; the reviewer's sweep script already takes `(p, s)` as parameters, and
  the readout is free and belongs in the meter permanently.

## Scope and related facts

- The counterexample refutes a clause of a hypothesis; it does **not** touch
  that hypothesis's principal claim, the first-fall closed form
  `d_ff = m*2^(m-1) + floor((s − 2^(m-1))/2) + 1`, which survived every attack in
  the same round including the exhaustive sweeps above.
- The two boundary cells `(2,2,2)` and `(3,2,4)` carry **zero dynamic range** on
  the mechanism question anyway: there `delta = n = ms`, so `A_delta` is
  one-dimensional, `A_{delta+1} = 0`, `top_rank = 0` and `d_ff = n + 1` for
  *every* generator of degree `delta`. Whatever the answer, those cells are
  instrument checks and not evidence about the mechanism.
- The row-independence assumption is currently an **unnumbered, unstated
  heuristic** doing real work. Under this program's own standard it should be
  numbered, with the bound `N_sol < 2^(ms − a_0)` attached and with the
  observation that the object it concerns has a STRUCTURED zero set (the
  decomposition set), which is precisely why a random model can fail for it.
- Nothing here bears on cost, solving degree, yield or the ECDLP. A fall
  dimension is not a solving degree.
