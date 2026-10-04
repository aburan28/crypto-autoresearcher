# Semaev 2015 at the named binary curves

Read this with the condition attached, because the condition is the whole
result's load-bearing part: **every row below is conditional on Assumption 1
(`d_F4 ≤ 4`), which this program has checked only at `n ≤ 21`.** The smallest
row in this table is `n = 97`. Nothing in the table is a statement about the
security of any curve, in either direction.

Derivation only, from the frozen and already-accepted instrument of
`EXP-SEMBIN-81dc96`, run at `RUN-SEMBIN-a7a2f3`. The instrument was loaded, not
re-implemented, and five cells of the producing run's own curve were reproduced
through the same call path before any new number was computed.

## Where the degrees come from

Read from frozen sources, not from recall, and the check earned its keep. A
recalled list had 359 as a binary Certicom degree. The frozen level-2 table
shows the 359-bit entry is `ECCp-359`, a **prime-field** curve, so there is no
binary Certicom challenge at 359 and it is absent here.

Certicom degrees come from the level-1 and level-2 challenge tables in
`inputs/BAILEY-2009-541-ECC2K130/talk-35minutes_text.md`, whose "Bits" column is
the field extension degree — checkable, because `ECC2K-130` appears at 131,
matching the independently known `GF(2^131)`. FIPS degrees come from the
`Curve K-163` … `Curve K-571` headings in the frozen SP 800-186 text, with the
B- family sharing each degree.

## The table

Section 4.5.2's own convention: stage 1 only, `t = m`, cofactor charged,
`block_n4w` solving cost. Margin is index calculus minus rho, so **positive
means rho wins**.

| n | curves | m\* | log₂ cost | log₂ rho | margin (bits) |
|--:|---|--:|--:|--:|--:|
| 97 | ECC2K-95, ECC2-97 | 6 | 104.86 | 48.5 | +56.36 |
| 109 | ECC2K-108, ECC2-109 | 6 | 108.88 | 54.5 | +54.38 |
| 131 | ECC2K-130, ECC2-131 | 7 | 115.42 | 65.5 | +49.92 |
| 163 | ECC2K-163, ECC2-163; K-163, B-163 | 7 | 123.77 | 81.5 | +42.27 |
| 191 | ECC2-191 | 8 | 130.10 | 95.5 | +34.60 |
| 233 | K-233, B-233 | 9 | 138.73 | 116.5 | +22.23 |
| 239 | ECC2K-238, ECC2-238 | 9 | 139.84 | 119.5 | +20.34 |
| 283 | K-283, B-283 | 9 | 147.65 | 141.5 | +6.15 |
| 409 | K-409, B-409 | 11 | 166.54 | 204.5 | −37.96 |
| 571 | K-571, B-571 | 12 | 186.31 | 285.5 | −99.19 |

## What it says

**No Certicom binary challenge curve is a target for this method.** All six
binary degrees lose to rho, by between 20.3 and 56.4 bits. `ECC2K-130`, the
curve the rest of this session's work was about, loses by 49.9 bits. That is a
second, independent route to the same conclusion the decomposition-oracle panel
reached on that curve by measurement.

**Among the FIPS binary curves, only 409 and 571 fall below rho at all**, and
409 does so only against the naive `2^{n/2}` baseline. `H-SEMBIN-97ea23`
(status: supported) puts the coherent-baseline crossover at 460 sparse and 520
dense, both above 409. So under a baseline this program already considers
better, **K-571 and B-571 are the only listed curves where Semaev's own model
puts index calculus below rho at all.**

`K-283` and `B-283` are the closest losing degrees, at +6.1 bits. That is the
one row where a modest improvement in the cost model would change the sign,
which makes it the row most worth attacking and the row most vulnerable to
exactly the assumption nobody has checked.

The vOW total-work column shifts every margin by a constant 0.175 bits and
changes no sign. It is not the coherent-baseline correction, which is a
fixed-memory-budget metric belonging to a different experiment and is cited
rather than recomputed here.

**The joint `(m, t)` optimum equals the `t = m` optimum at all ten degrees.**
The producing run found that on `n = 250..600`; it now extends down to `n = 97`.

## A defect found in the producing run

The search-floor probe this contract carries, and the producing contract did
not, found that `crossover_cofactor_absorbed = 250` in `RUN-SEMBIN-aa5161` is
that sweep's own lower search bound, not a crossover. The absorbed model sets
the solve cost to **zero** rather than absorbing a polynomial factor, so its
cost is below `2^{n/2}` throughout and the routine returns whatever floor it is
given: 20, 100 and 250 for the three floors tried. The derived
"charging the cofactor shifts the crossover up by 52" is therefore a difference
against a quantity that does not exist, and is withdrawn in
`CORR-20260917-02cfe6`.

The charged crossover of **302 stands** and is floor-independent, returning 302
from both `n_lo = 20` and `n_lo = 250`. Every margin in the table above rests on
the charged reading and is unaffected.

## Status

`EXP-SEMBIN-992e73` is **specified, not approved**, and `RUN-SEMBIN-a7a2f3` is
an unapproved derivation archived for auditability. No evidence record rests on
it, no hypothesis moves, and no completion criterion of any goal is advanced
until a Coordinator approves the contract and an independent reviewer reads the
run.
