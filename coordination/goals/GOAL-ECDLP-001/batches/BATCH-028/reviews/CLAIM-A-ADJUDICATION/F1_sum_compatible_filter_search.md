# F1 — broad search for a sum-compatible filter on `E(F_p)`

Executor, BATCH-028. Executes falsifier **F1** of
`claim_a_adjudication.md` §7, obstruction conjunct **(O2)**.

**Status: EXPLORATORY SEARCH.** No frozen specification governs this work; no
`EXP-*` contract, no `RUN-*` record, no evidence record, and no ledger entry is
created or modified by it. Claim tier is *exploratory* under
`docs/claims-and-verification.md`. Nothing here promotes, rejects, or closes any
hypothesis, and nothing here declares a heuristic validated or refuted — those
judgements belong to the Reviewer and Coordinator. This document records
observations and the one specification problem the search uncovered.

**Certificate discipline.** This is a pure measurement run;
`certificate.kind: none`. There is no claimed discrete-log solve and no claimed
factor-base relation, so no solution certificate is owed. The two algebraic
identities on which the only positive findings rest were nonetheless verified
exactly and independently (§6.1, §7), and all curve arithmetic was verified
against SageMath 10.9, which did not participate in producing the measurements.

---

## 0. Answer first

| Question | Answer |
|---|---|
| Did anything on a **prime-order** `E(F_p)` beat chance? | **No.** Max predictability over 3450 `(h, M)` rows / 13 528 `(h, f, M)` combinations on 11 prime-order arms was **1.10× chance**, against the required **4×**. The matched decoupled null reached **1.10×** as well. |
| Did the `Z/N` control recover ≈0.50? | **Yes.** 0.5007 / 0.5002 / 0.5013 at 32/64/256 bits, flat in `M` from 4 to 256, exactly the two-candidate behaviour the adjudication predicted. SHA-256 returned exactly chance. |
| Did anything clear the `4/M` bar on `E(F_p)`? | **Yes — 18 rows, all of two bounded kinds**, plus one that shows F1 is under-specified. None of them is usable against a prime-order subgroup, and none supplies a growing `M`. See §6 and §5. |
| Is F1 falsified? | **F1 as literally written is falsified — twice, in bounded ways that do not touch the attack.** The mechanism F1 exists to detect is **unfalsified and better supported** than before. F1's wording needs a Coordinator amendment (§5, §9). |

---

## 1. What F1 asks

> **F1.** A map `h: E(F_p) -> [M]`, `M >= 4`, computable in `o(1)` group
> operations, with `Pr[h(P+Q) = f(h(P),h(Q))] >= 4/M` for some `f` over uniform
> `P, Q`.

Chance is `1/M`; the bar is a 4× lift. The task framing states the bar as the
inequality alone. The cost clause `o(1)` group operations is in the original
§7 text and turns out to carry the entire content of the falsifier (§5).

**Why it would matter.** Per the adjudication's Attack 4, a Wagner `k = 2^j`
tree over `m` summands would put the enumerate-and-join class at exponent
`(2^j + m)/(m(j+1))` — `0.4167` at `(j=2, m=16)`, `0.375` at `(j=3, m=16)` —
below `1/2`, defeating (LB-1). That is why this is the one exponent-moving
falsifier in the campaign.

**A quantitative point that constrains what counts as a hit, recorded here
because it bears on every positive in §6.** Wagner's tree needs each of the `j`
levels to pin `ell ≈ log2(N)/(j+1)` bits, i.e. `M ≈ N^{1/(j+1)}`. At
`(j=3, m=16)` and `N ≈ 2^256` that is `M ≈ 2^64`. A filter with a *constant*
`M` — 4, or 396, or any fixed number — supplies a constant number of bits and
buys a constant factor, not an exponent. So a genuine falsification of (O2)
needs an `h` whose `M` **grows with `N`**, not merely one that clears `4/M` at
some fixed small `M`. F1 as written does not say this. It should.

---

## 2. Curve panel

Ten curves, three field sizes (32, 64, 256 bits), chosen so that torsion is
visible and so that both the presence and the absence of small torsion are
represented. **`#E` and its factorization were computed by SageMath 10.9**
(`EllipticCurve(GF(p),[a,b]).cardinality()`, `abelian_group().invariants()`),
not by the measurement code.

| tag | `p` (bits) | curve `y^2 = x^3+ax+b` | `#E` factorization | group structure | rational 2-torsion pts |
|---|---|---|---|---|---|
| C1-p32-prime | 4294967291 (32) | a=1, b=13 | 4295040499 (prime) | Z/4295040499 | 0 |
| C2-p32-cof3 | 4294967291 (32) | a=3, b=42 | 3 · 1431660059 | Z/4294980177 | 0 |
| C3-p32-full2tors | 4294967291 (32) | a=−31, b=30 | 2^3 · 3 · 4139 · 43237 | Z/2 × Z/2147495316 | 3 |
| C4-p32-supersingular | 4294967291 (32) | a=1, b=0 | 2^2·3^2·7·11·31·151·331 | Z/4294967292 | 1 |
| C5-p32b-1mod12 | 4294967197 (32) | a=0, b=7 | 7 · 613578961 | Z/4295052727 | 0 |
| C6-p64-prime | 18446744073709551427 (64) | a=1, b=6 | 18446744066056893107 (prime) | Z/18446744066056893107 | 0 |
| C7-p64-cof5 | 18446744073709551427 (64) | a=2, b=8 | 5 · 3689348813634888413 | Z/18446744068174442065 | 0 |
| C8-secp256k1 | 2^256−2^32−977 (256) | a=0, b=7 | 1157920892373161954235709850086879078528375642790749043826051631415181614943 37 (prime) | cyclic, prime order | 0 |
| C9-p64-full2tors | 18446744073709551427 (64) | a=−31, b=30 | 2^3 · 283 · 24061 · 338633272037 | Z/2 × Z/9223372039401914924 | 3 |
| C10-psec-full2tors | 2^256−2^32−977 (256) | a=−31, b=30 | 2^3·5·11·19·1568366341·177182803437613·11618414862094160710691·4289993660935733972973542239 | Z/2 × Z/(#E/2) | 3 |

C3, C9, C10 are `y^2 = (x−1)(x−5)(x+6)` at three field sizes — deliberately
constructed with full rational 2-torsion, as positive controls. C4 is
supersingular (`p ≡ 3 mod 4`, `#E = p+1`) with completely smooth order, giving
large torsion subgroups. C5 is over a field with `p ≡ 1 mod 12`, so cubic,
quartic and octic residue characters exist there.

**Arms.** Each curve was measured on the *full* group and, where a cofactor
exists, on the *prime-order subgroup* reached by `[cofactor]P` (`[8]P` for the
2-torsion curves, i.e. the odd part). The prime-order arms are the ones that
matter: a cryptographic ECDLP instance lives in a prime-order subgroup.

---

## 3. Method

**Sampling.** `P` and `Q` are drawn independently and uniformly from the affine
points of `E(F_p)` with `y ≠ 0` (uniform `x`, reject non-residues, uniform sign
of `y`) — uniform on `E(F_p)` up to the `O(1/#E)` mass of `O` and the
2-torsion. Subgroup arms multiply by the cofactor, which maps the uniform
distribution on `E(F_p)` onto the uniform distribution on the prime-order
subgroup. `P` and `Q` are disjoint halves of one fresh point pool, so they are
independent, not resampled from a shared pool. Sample sizes: 400 000 pairs at
32 bits, 300 000 at 64 bits, 120 000 at 256 bits, split 50/50 into a fit half
and a disjoint score half.

**`f` strategies, all fit on the fit half and scored on the disjoint score
half.** Fitting and scoring on the same samples inflates the estimate; every
number below is out-of-sample.

- `f_const` — best constant predictor `argmax_c Pr[h(P+Q)=c]`. **This is the
  honest floor**, not `1/M`: a non-uniform or degenerate `h` beats `1/M` with
  no sum-compatibility whatsoever.
- `f_shift` — `c = a + b + d (mod M)`, best `d`. Only `M` parameters, so it is
  statistically powerful at large `M` where a full joint table is starved. This
  is the strategy that recovers the `Z/N` filter.
- `f_xor` — `c = a ⊕ b ⊕ d` for `M` a power of two. Included because the
  natural group law on character values is multiplicative, i.e. XOR on bits;
  omitting it would have hidden the 2-descent positive.
- `f_joint` — the **empirically optimal** `f(a,b) := argmax_c Pr[h(P+Q)=c |
  h(P)=a, h(Q)=b]` from the fit-half joint table, with empty cells falling back
  to the global mode. Restricted to `M ≤ 32`: at `M = 256` a joint table has
  65 536 cells and the fit is starved, which is precisely where out-of-sample
  scoring degenerates to noise. `f_joint` dominates every fixed algebraic `f`
  for a given `h`, so it is the fairest test of whether `h` carries any
  sum-compatible information at all.

**Degeneracy accounting.** `M_eff` = number of distinct `h` values actually
observed. A trap the raw F1 inequality walks straight into: an `h` that
duplicates a bit, or has an image smaller than `M`, clears `4/M` with no
structure at all. Example from this run: on C1 the pair
`(chi(x−1), chi(x−a))` with `a = 1` is the *same character twice*, so
`M_eff = 2` while `M = 4`, and it scores 0.5013 — a spurious "2× lift". Every
result below is reported against `M_eff` and against `f_const`, never against
`1/M` alone.

**Candidate `h` families searched — 507 distinct `(h, M)` definitions, 7917
scored rows on `E(F_p)`, 31 283 `(h, f, M)` combinations in total** (13 528 of
them on prime-order arms):

| family | distinct `(h,M)` | rows |
|---|---|---|
| A. coordinate bit-windows (low / high / middle windows of `x`, of `y`, joint `(x,y)` windows) and arithmetic combinations (`x±y`, `xy`, `x⊕y`, `x^2`, `x^3`, `x^{-1}`, all mod `M` for `M` ∈ {4,8,16,32,64,256}) | 79 | 1338 |
| B. `x mod k`, `y mod k` for `k` ∈ {5,7,9,15,17} | 10 | 196 |
| C. quadratic characters and their products: `chi` of `x`, `y`, `x±1`, `x+2`, `x±y`, `xy`, `x^2+1`, `3x^2+a`, `x^3+1`, plus a 12-point scan of `chi(x−e)` at arbitrary `e` (small, curve-derived, and random), combined into pairs (`M=4`), triples (`M=8`) and quadruples (`M=16`) | 302 | 5660 |
| D. higher-power residue characters where the field admits them: cubic (`p≡1 mod 3`), quartic (`p≡1 mod 4`), octic (`p≡1 mod 8`), alone and paired | 8 | 76 |
| E. rational functions of `(x,y)` — `x/y`, `y/x`, `x^2/y`, `y/x^2`, `(x+1)/(y+1)`, `xy/(x+1)` — i.e. coordinates of other curve models (Montgomery/Edwards-like), reached with one batch inversion | 18 | 144 |
| F. 2-descent characters `chi(x − e_i)` at the **rational 2-torsion** `x`-coordinates, alone and in combination | 75 | 339 |
| G. projection onto a small-order subgroup (a genuine group homomorphism) | 8 | 10 |
| H. structureless in-arm null: SHA-256 of `x` truncated to `M` | 2 | 44 |
| I. digit statistics: popcount of `x` mod 4, decimal digit sum mod 4 | 2 | 44 |
| J. `y`-sign (the one coordinate datum that flips under negation), alone and joint with `x`-windows | 3 | 66 |
| **total** | **507** | **7917** |

Additionally, a search over the **entire function space** of balanced `h` on
small groups was attempted by simulated annealing. It failed its own positive
controls and contributes no evidence; recorded in §8.

---

## 4. Apparatus validation — three independent checks

Under `docs/inventor-protocol.md` §"controls before belief", none of the
measurements below mean anything until the instrument is shown to detect a
positive when one exists. Three checks, all passed.

**4.1 Arithmetic verified against SageMath.** For all 10 curves: sampled points
lie on the curve; batch point addition agrees with Sage's elliptic-curve
addition on 20 random pairs per curve; batch scalar multiplication `[k]P` with
`k = 12345678901` agrees with Sage on 20 points per curve. **Total mismatches:
0.** A χ² uniformity smoke test on `x mod 8` (df = 7, 4000 points per curve)
returned 4.30–10.70 across the panel — no cell out of range.

**4.2 The `Z/N` arm — mandatory negative control — recovers ≈0.50.**
`N` matched to each curve's order; `h` = low bits, high bits, `mod k`, middle
window, popcount, SHA-256.

| arm | `x_low_4` | `x_low_16` | `x_low_256` | `x_high_256` | `sha256_x_16` (chance 0.0625) | `popcount_4` (chance 0.25) |
|---|---|---|---|---|---|---|
| `Z/N`, N ≈ 2^32 | **0.5007** | **0.5007** | **0.5007** | 0.5003 | 0.0634 | 0.2515 |
| `Z/N`, N ≈ 2^64 | **0.5002** | **0.5000** | **0.5000** | 0.5001 | 0.0626 | 0.2508 |
| `Z/N`, N ≈ 2^256 | **0.5013** | **0.5023** | **0.5003** | 0.4969 | 0.0636 | 0.2510 |

Binomial SE 0.0011 / 0.0013 / 0.0020. The apparatus reproduces the adjudication's
finding exactly: over `Z/N` the sum's low bits are pinned to two candidates
independently of `M`, so predictability is ≈1/2 flat in `M` — a lift of 128×
chance at `M = 256`. It also reproduces the null: SHA-256 and popcount sit on
chance to within 1.5 SE. **The instrument can see a 4× lift; it is not blind.**

**4.3 The decoupled null — an object-level null of the same shape.** For four
prime-order arms the entire 380-to-410-family sweep was re-run with `h(P+Q)`
replaced by `h(P'+Q')` from an **independent** sample. Every `h` keeps its exact
marginal distribution; all dependence on `(h(P), h(Q))` is destroyed. This
calibrates the noise ceiling of the sweep *including* the
multiple-comparison effect of taking a maximum over ~1500 statistics per arm.

| curve | REAL max lift | REAL max z | NULL max lift | NULL max z |
|---|---|---|---|---|
| C1-p32-prime | 1.057× | 4.51 | **1.101×** | **4.66** |
| C6-p64-prime | 1.070× | 4.08 | **1.104×** | **5.36** |
| C8-secp256k1 | 1.038× | 3.30 | **1.045×** | **3.43** |
| C7-p64-cof5, `[5]P` | 1.073× | 4.21 | 1.075× | 4.99 |

`z = (best_p − f_const)/SE`. Over all prime-order rows the `z` distribution is
median 0.85, 95th percentile 2.90, max 4.51; over the decoupled-null rows it is
median 0.79, 95th percentile 2.93, max 5.36. **The real data and the null are
statistically indistinguishable, and the null is if anything slightly higher.**
The residual 1.04–1.10× lifts are selection noise, not signal.

---

## 5. A specification problem in F1 that the search uncovered

**F1's inequality alone is satisfied on every prime-order `E(F_p)`, by an `h`
that is useless.** On a prime-order curve, pull the interval (or low-bit)
partition of `Z/N` back through the discrete logarithm:
`h(P) = ⌊M · dlog_G(P) / N⌋`. Since `dlog` is a group isomorphism, this is
exactly the `Z/N` filter and inherits its predictability. Measured exactly (not
sampled) on `E(F_487)` with `#E = 499` prime, by computing all 499 discrete
logarithms:

| `M` | chance `1/M` | F1 bar `4/M` | measured `Pr` | lift | clears `4/M`? |
|---|---|---|---|---|---|
| 4 | 0.2500 | 1.0000 | 0.5025 | 2.0× | no |
| 8 | 0.1250 | 0.5000 | 0.5043 | 4.0× | **yes** |
| 16 | 0.0625 | 0.2500 | 0.5111 | 8.2× | **yes** |
| 64 | 0.0156 | 0.0625 | 0.5442 | 34.8× | **yes** |
| 256 | 0.0039 | 0.0156 | 0.7375 | 188.8× | **yes** |

(The rise above 0.50 at large `M` is a finite-size artifact of `N = 499`; at
cryptographic `N` it would sit at ≈0.50, still clearing.)

This `h` costs a discrete logarithm to evaluate, so it violates the `o(1) group
operations` clause and is worthless as an attack — but it does satisfy F1's
stated inequality, at every `M ≥ 8`, on every prime-order curve including
secp256k1. **The whole content of F1 is therefore in its cost clause, not in its
inequality.** A later session reading only the inequality would record a
falsification that means nothing.

**Amendment request to the Coordinator** (I am not authorised to edit the
falsifier and have not): F1 should be restated with three additions —
(i) the cost clause made binding and quantified, e.g. *evaluable in
`O(polylog p)` field operations and zero group operations*; (ii) the requirement
that `M` **grow with `N`** (a Wagner `j`-level tree needs `M ≈ N^{1/(j+1)}`), so
a constant-`M` filter does not count; (iii) the domain restricted to the
**prime-order subgroup** in which the ECDLP instance lives, rather than to
`E(F_p)`. Without (iii) the falsifier is met by torsion artifacts (§6).
This is an amendment request producing a new record, not an edit; the frozen
text stands and every number in this report is scored against it as written.

---

## 6. Everything on `E(F_p)` that cleared the bar — 18 rows, two kinds

Reported against `M_eff`, i.e. after excluding the duplicate-bit degeneracies
described in §3.

### 6.1 The 2-descent characters — real, cheap, and dead where it counts

On a curve with a rational 2-torsion point at `x = e` (a root of `x^3+ax+b`),
the map

```
    h_e(P) = chi(x(P) − e)          (chi = Legendre symbol)
```

is a **group homomorphism** `E(F_p) → {±1}`: this is the classical 2-descent /
2-isogeny descent map. With full rational 2-torsion (three roots `e_0,e_1,e_2`)
any two of the three give an independent pair, so
`h(P) = (chi(x−e_i), chi(x−e_j))` maps onto `(Z/2)^2` and is sum-compatible
with `f = XOR`.

**Measured, out-of-sample, `f_xor` fit on a disjoint half:**

| curve | field | `h` | `M_eff` | `Pr[h(P+Q)=f(h(P),h(Q))]` | `f_const` | `4/M_eff` | clears |
|---|---|---|---|---|---|---|---|
| C3-p32-full2tors | 32-bit | `(chi(x−e_i), chi(x−e_j))`, all 3 pairs | 4 | **1.0000** | 0.2499 | 1.0000 | **yes** |
| C9-p64-full2tors | 64-bit | same, all 3 pairs | 4 | **1.0000** | 0.2499 | 1.0000 | **yes** |
| C10-psec-full2tors | 256-bit | same | 4 | **1.0000** | 0.2500 | 1.0000 | **yes** |
| C4-p32-supersingular | 32-bit | `chi(x−e_0)` alone (only one rational 2-torsion pt) | 2 | 1.0000 | 0.5005 | — (`M<4`) | n/a |

`f_const = 0.2499` confirms the image is uniform over 4 values, so `M_eff = 4`
genuinely — this is not the duplicate-bit degeneracy. Predictability is
**exactly** 1.0000, and it costs **two Legendre symbols and zero group
operations**, so unlike the dlog filter of §5 it satisfies F1's cost clause too.

**Hardening — every check I could apply:**

1. **Is it exact, or a statistical accident?** Exact. Direct verification of
   `chi(x(P+Q)−e) = chi(x(P)−e)·chi(x(Q)−e)` on 20 000 independent random pairs
   per `(curve, e)`: **0 violations** in 20 000/20 000 for every rational
   2-torsion root on C3 (e = 1, 5, −6), C9 (same three), C10 (same three), and
   C4 (e = 0). It is an identity, not a measurement.
2. **Does it survive a second curve and a second field size?** Yes — three
   curves at 32, 64 and 256 bits, all 1.0000.
3. **Does it survive out-of-sample `f`?** Yes; `f_xor` is fit on the fit half
   and scored on the disjoint score half, and `f_const` is reported separately
   at 0.25.
4. **Is it a torsion artifact bounded by a small factor? YES — and this is
   decisive.** For a finite abelian group `A`, `A/2A ≅ A[2]`, so the image of
   *any* 2-descent map has size at most 4 over `F_p`. `M` is capped at 4
   forever: **2 bits, a constant, not a growing filter.** Per §1, a Wagner tree
   at `(j=3, m=16)`, `N ≈ 2^256` needs `M ≈ 2^64`. Two bits buys a constant
   factor and moves no exponent.
5. **Does it survive on the subgroup where the ECDLP lives? NO — it vanishes
   identically.** Measured on the odd part `[8]E(F_p)`: the character takes the
   single value `+1` on every sampled point, on all three curves. The scorer
   reports `Pr = 1.0000` there via `f_const` with `M_eff = 1` — a constant
   function, which predicts itself perfectly and filters nothing. The whole-sweep
   maximum on the C3 and C9 odd-part arms falls back to 1.10× chance, i.e. noise
   (Table in §7). Structurally this is forced: a homomorphism from a group of
   prime order `N` into a group of order `M < N` is trivial, and a
   cryptographic curve has no rational 2-torsion at all — C1, C2, C5, C6, C7 and
   secp256k1 all have `x^3+ax+b` irreducible over `F_p`, so the character does
   not exist on them in the first place.

So this is a genuine sum-compatible filter on `E(F_p)`, it satisfies F1's
literal statement including the cost clause, and it is **exactly as useless as
the adjudication's own parenthetical anticipated**: bounded by the torsion
order, and identically trivial on the prime-order subgroup.

### 6.2 Small-subgroup projections — real, but they cost group operations

`h(P) = ` index of `[λ/M]P` in the order-`M` subgroup (`λ` = group exponent) is
a group homomorphism and is perfectly sum-compatible by construction.

| curve | `M` | `Pr` | `f_const` | `4/M` | clears |
|---|---|---|---|---|---|
| C4-p32-supersingular | 396 | 1.0000 | 0.0030 | 0.0101 | yes (396× chance) |
| C4-p32-supersingular | 151 | 1.0000 | 0.0059 | 0.0265 | yes |
| C4-p32-supersingular | 33 | 1.0000 | 0.0308 | 0.1212 | yes |
| C5-p32b-1mod12 | 7 | 1.0000 | 0.1451 | 0.5714 | yes |
| C3-p32-full2tors | 6 | 1.0000 | 0.1590 | 0.6667 | yes |
| C7-p64-cof5 | 5 | 1.0000 | 0.2090 | 0.8000 | yes |

These are the positive controls that prove the scorer detects a perfect filter
at large `M` (396 buckets, lift 396×). They are **not** F1 falsifications:
evaluating `[λ/M]P` costs `O(log p)` group operations, violating the `o(1)`
clause, and `M` is capped by the torsion order — which is 1 for C1, C6, C8 and
for every standardized cryptographic curve with cofactor 1, and at most 8 for
those with a small cofactor. C4's `M = 396` exists only because that curve is
supersingular with completely smooth order `p+1`; on the prime-order arms of the
same panel no such subgroup exists.

**No third kind was found.** Every one of the 18 clearing rows is a 2-descent
character or a subgroup projection.

---

## 7. The main negative: prime-order arms

Eleven prime-order arms — C1 (×2 independent runs), C6 (×2), C8 (×2), plus the
`[3]P`, `[5]P`, `[7]P` and `[8]P` subgroup arms of C2, C7, C5, C3 and C9 —
covering 3450 `(h, M)` rows and 13 528 `(h, f, M)` combinations, excluding
subgroup projections.

**Best observed predictability per effective alphabet size, over all
prime-order arms:**

| `M_eff` | rows | chance `1/M` | F1 bar `4/M` | max observed `Pr` | binomial SE | lift | best `h` |
|---|---|---|---|---|---|---|---|
| 4 | 2521 | 0.2500 | 1.0000 | 0.25497 | 0.00178 | 1.020× | `(chi(y), chi(x−y))` — secp256k1 |
| 5 | 22 | 0.2000 | 0.8000 | 0.20285 | 0.00164 | 1.014× | `y mod 5` — secp256k1 |
| 7 | 22 | 0.1429 | 0.5714 | 0.14485 | 0.00091 | 1.014× | `y mod 7` — C7 `[5]P` |
| 8 | 326 | 0.1250 | 0.5000 | 0.12977 | 0.00137 | 1.038× | `x_low_8` — secp256k1 |
| 9 | 32 | 0.1111 | 0.4444 | 0.11332 | 0.00129 | 1.020× | `(cubic(x), cubic(y))` — secp256k1 |
| 16 | 295 | 0.0625 | 0.2500 | 0.06505 | 0.00101 | 1.041× | **`sha256(x) mod 16`** — secp256k1 |
| 17 | 18 | 0.0588 | 0.2353 | 0.06014 | 0.00053 | 1.022× | `y mod 17` — C5 `[7]P` |
| 32 | 36 | 0.0312 | 0.1250 | 0.03235 | 0.00046 | 1.035× | `x_low_32` — C6 |
| 64 | 99 | 0.0156 | 0.0625 | 0.01639 | 0.00033 | 1.049× | `x^{-1} mod 64` — C6 |
| 256 | 54 | 0.0039 | 0.0156 | 0.00430 | 0.00015 | 1.101× | `x_high_256` — C3 odd part |

**The global maximum over every prime-order arm is a lift of 1.101×, which is
27.5% of the 4× bar.** Nothing came within a factor of 3.6 of clearing.

Two things make this reading tight rather than merely quiet:

- **The winner at `M = 16` is SHA-256 of the `x`-coordinate** — a function with
  no elliptic-curve content whatsoever, included precisely as an in-arm null.
  When the top of the ranking is occupied by a cryptographic hash, the ranking
  is noise.
- **The decoupled null reaches the same maximum** (§4.3), so the residual
  1.04–1.10× is exactly what taking a maximum over ~1500 statistics produces
  under the null.

Supplementary context, not part of F1: top-2 coverage (allowing `f` to output
two candidates) reached at most 0.1293 at `M = 16` on prime-order arms against a
chance value of 2/16 = 0.125. Even a 2-candidate relaxation finds nothing. For
comparison, `Z/N` reaches ≈0.50 with a *single* candidate.

**Also negative, individually worth recording because they were the most
motivated guesses:** rational-function coordinates (`x/y`, `y/x`, `x^2/y`,
`(x+1)/(y+1)`, …), which are the coordinates of Montgomery- and Edwards-style
models with different addition formulae — all at chance; higher-power residue
characters (cubic, quartic, octic) on the `p ≡ 1 mod 12` field — all at chance;
the `y`-sign, the one coordinate datum sensitive to negation — at chance;
`chi(x−e)` for 12 non-torsion values of `e`, including curve-derived and random
`e` — all at chance, on curves where no rational 2-torsion exists. The last one
is the sharpest: the descent character is at 1.0000 when `e` is a root of the
cubic and at chance when it is not, on the same curve, with the same code.

### 7.1 A near-miss worth recording

For **every** `e` and every curve, the following identity holds:

```
chi( x(P+Q) − e )  =  chi( (y_Q − y_P)^2 − (x_P + x_Q + e)(x_Q − x_P)^2 )
```

because `x(P+Q) − e = [ (y_Q−y_P)^2 − (x_P+x_Q+e)(x_Q−x_P)^2 ] / (x_Q−x_P)^2`
and `chi` of a square is 1. Verified exactly: 20 000/20 000 agreements, **0
violations**, on C1, C6 and secp256k1 at `e ∈ {0, 1, 12345}`.

So a quadratic-character bit of the *sum* is computable from the coordinates of
`P` and `Q` **with no modular inversion at all** — cheaper than forming `P+Q`.
It is nonetheless not an F1 filter and cannot drive a k-tree, for a specific
reason: it is a function `g(P,Q)` of the **full coordinates of both points**,
not of the form `f(h(P), h(Q))`. Wagner's join needs to *bucket each list
independently* and then match buckets; a primitive that must see both elements
still costs `Θ(W_1 · W_2)` work and adjudicates no more pairs than a plain join,
so it does not touch (O1) either. When `e` is a rational 2-torsion root the
right-hand side factors and collapses to `chi(x_P−e)·chi(x_Q−e)` — which is
exactly why the descent character, and only the descent character, becomes a
per-element filter. This looks to me like the structural reason the search comes
up empty, and it is offered as an observation, not as a proof.

---

## 8. What failed, recorded in full

**8.1 Full-function-space search by simulated annealing — INSTRUMENT FAILURE,
contributes no evidence.** To go beyond hand-picked families I attempted to
maximise the exact (not sampled) predictability over *all* `h` on small groups,
using the complete Cayley table:
`pred(h) = n^{-2} Σ_{a,b} max_c #{(i,j): h(i)=a, h(j)=b, h(i+j)=c}`.

- *First attempt (unconstrained moves).* Collapsed to a near-constant `h` in
  every arm — a degenerate optimum (one bucket holding 54% of the group,
  predicted always) that is useless as a filter. Superseded, not deleted.
- *Second attempt (balance-constrained swap moves).* Chance is then exactly
  `1/M`. **It failed its positive controls.** Reference optima computed directly:
  the 2-descent filter on the `#E = 536` curve scores 0.9944, `Z/536 mod 4`
  scores 1.0000, `Z/499` low-2-bits scores 0.5025. Balanced annealing from
  random starts (60 000 steps × 4 restarts) reached only **0.279**, **0.274**
  and **0.282** respectively — it did not find *any* of the three known optima.

Per `docs/inventor-protocol.md`, a measurement that cannot detect a positive
when one is present yields no negative. **The annealing arm's result on the
prime-order curve (0.2728 at `M=4`) is therefore discarded as evidence and is
recorded here only as a method that did not work.** The landscape is a needle in
a haystack for single-swap local search. All conclusions in §7 rest on the
family sweep and its decoupled null, not on this.

**8.2 One family raised an exception.** `proj_subgroup_M12` on C3 threw
`KeyError` during table lookup: the order-12 subgroup generator search returned
a point of order 12, but `E(F_p)[12]` on that curve is `Z/2 × Z/12`, so
`[λ/12]P` does not always land in the cyclic group generated by it.
Classification: `implementation_error`, confined to one positive-control family.
It affects no conclusion — other `M` values on the same curve (2, 3, 6) ran
correctly and the 2-descent result on C3 is independent of it. Recorded, not
suppressed.

**8.3 Protocol notes / limitations.**
- Point sampling excludes `O` and the points with `y = 0`; this is a relative
  deviation of `O(1/#E)` from exactly uniform on `E(F_p)` and cannot produce or
  hide a 4× effect.
- `f_joint` was restricted to `M ≤ 32`; at `M = 64` and 256 only `f_const`,
  `f_shift` and `f_xor` were fit. `f_shift` is the strategy that recovers the
  `Z/N` positive at `M = 256` (0.5003), so the large-`M` arm is not blind.
- The 256-bit arms used a reduced family set (105–126 families) and 60 000
  scoring samples, versus ~400 families and 200 000 samples at 32 bits. A 4×
  lift at `M = 16` would still be a 190-σ effect at 60 000 samples.
- The `Z/N` control was run before the top-2 statistic was added, so top-2
  numbers exist for the curve arms only.

---

## 9. Honest assessment of F1's status

I am recording an observation, not a verdict on the closure; the disposition of
(O2) and of the §7 KN-FIND candidate belongs to the Reviewer and Coordinator.

**F1 as literally written: FALSIFIED, twice, in ways that do not touch the
attack it was designed to detect.**

1. By the dlog pull-back (§5): satisfies the inequality at every `M ≥ 8` on
   every prime-order curve including secp256k1; violates the cost clause;
   worthless.
2. By the 2-descent characters (§6.1): satisfies the inequality *and* the cost
   clause, at `M = 4`, with predictability exactly 1.0000, verified as an exact
   identity on three curves at three field sizes. But `M` is capped at 4 by
   `A/2A ≅ A[2]`, and the map is identically trivial on the odd-order subgroup
   and does not exist at all on a curve of prime order.

Neither of these is the object (O2) is about. Both are inside the "if the curve
has small-order torsion, a reduction modulo that torsion IS sum-compatible"
carve-out the task itself anticipated, and both are bounded exactly as
predicted — by the torsion order, which is 1 on the groups where prime-field
ECDLP is actually posed.

**The mechanism F1 exists to detect — a cheap filter, on a prime-order
subgroup, with `M` able to grow with `N` — is UNFALSIFIED by this search, and
the search materially strengthens (O2).** The strengthening, stated at exactly
its own weight:

- 507 distinct `(h, M)` definitions across 10 candidate families, 31 283
  `(h, f, M)` combinations, 10 curves, 3 field sizes, 11 prime-order arms;
- the strongest available `f` for each `h` (the empirically optimal joint table)
  fit out-of-sample on a disjoint half;
- maximum lift on any prime-order arm **1.101×** against a required **4×**;
- an in-arm structureless null (SHA-256) that *tops* the ranking at `M = 16`;
- a matched decoupled null whose maximum lift and maximum z-score **equal or
  exceed** the real data's;
- a `Z/N` control that recovers ≈0.50 at every `M` and every field size, proving
  the instrument detects a real filter when one exists;
- a curve-side positive control (2-descent at 1.0000, subgroup projection at
  `M = 396`) proving it detects one on `E(F_p)` too.

**What this is not.** It is not a proof that no such `h` exists. The searched
space is "functions of the affine coordinates in the families listed", which is
a vanishing fraction of all maps `E(F_p) → [M]`; the attempted full-space search
failed (§8.1) and left that gap open. A single well-chosen algebraic invariant
outside families A–J would overturn this. Under
`docs/inventor-protocol.md` §4 the durable content here is the **named
obstruction with an argument** — §7.1's identity, plus the group-theoretic
observation that a sum-compatible `h` with `f` a group law *is* a homomorphism
and `Hom(Z/N, Z/M)` is trivial for `N` prime and `M < N` — and the count of 507
screened families is the fatigue report that accompanies it, not the result.

**`dominated_by` / `sota_delta` for this deliverable.** No algorithm is
proposed, so there is no frontier row to occupy: `sota_delta = 0` on time,
memory and data/queries. `dominated_by` is inapplicable rather than `null`.

---

## 10. Forward guidance — what remains open in this direction

1. **The gap left by §8.1.** A full-function-space search needs a method that
   actually works: spectral/Fourier optimisation over the group's character
   basis rather than local swaps, or an exact optimum for very small `N` by
   integer programming. Any such method must recover the three reference optima
   in §8.1 before its negatives count.
2. **Higher-degree descent and isogeny-induced maps.** `A/mA ≅ A[m]` bounds
   *every* descent-type character by the torsion, so this lane is bounded a
   priori; but the bound should be stated as a lemma rather than inferred from
   the `m = 2` measurement.
3. **Filters valued in something other than `Z/M` or `(Z/2)^k`** — e.g. a map to
   a set with a non-group `f`. `f_joint` searches all `f` for a given `h`, so
   this is covered for the `h` tested, but not for `h` outside families A–J.
4. **The §7.1 identity as an obstruction argument.** Making precise the step
   "the only per-element factorisations of `chi(x(P+Q)−e)` occur at the roots of
   the cubic" would convert (O2) from a measurement into an argument, which is
   what the closure standard actually asks for.
5. **F1's restatement** (§5) before any further session scores against it.

---

## 11. Reproduction

- Repository commit at execution: `67d0217bf5b6736fcfa0c7961d593b67abbecc5b`;
  worktree carried 1 untracked pre-existing path (BATCH-026 review directory),
  unrelated to this work. This document is the only file written.
- Environment: Python 3.13.1, numpy 2.4.0, macOS-26.6-arm64; SageMath 10.9
  (used only for curve orders, group invariants, 2-torsion roots, and the
  independent arithmetic check).
- Determinism: every arm is seeded (`random.Random(seed)` for sampling,
  `numpy.default_rng(seed)` for the shuffled control); seeds 11–13 (`Z/N`),
  101–108 (32-bit), 201–203 (64-bit), 301 (256-bit), 401–410 (round 2), 17
  (annealing). Re-running the same seed reproduces the tables exactly.
- Scripts were run under the session scratchpad
  (`F1/{f1lib,run_f1,round2,anneal,anneal2,verify_descent,dlog_filter}.py`,
  `F1/{pick_curves,pick2,pick3,fix2t,verify_arith}.sage`) and are **scratch, not
  archived artifacts** — the same status the adjudication gave its own
  computations. §3 states the method in enough detail to rebuild them. Any
  promotion of these numbers must re-run them inside an experiment directory
  with the standard receipt package (`manifest.yaml`, `command.txt`,
  `environment.json`, `stdout.log`, `stderr.log`, `raw-result.json`).

---

## Inference

```yaml
inference:
  requested_policy: executor-implementation
  resolved_model_id: claude-opus-5
  reasoning_effort: null
  fallback_used: true
  fallback_reason: >-
    This Claude Code harness cannot resolve the policy aliases in
    orchestration/model-policies.yaml; subagent frontmatter supports only Claude
    models. Recorded, never silently substituted (AGENTS.md rule 11). Note the
    consequence: this search and the adjudication it tests resolve to the same
    backend, so it is a procedurally separate session, not a model-independent
    check of that document's reasoning.
  degraded_allowed: false
  degraded_requirements: []
  model_verified: false
  model_verified_reason: >-
    `python3 -m orchestration.adapter doctor --probe` was not run in this
    session. The identifier is unverified configuration.
```
