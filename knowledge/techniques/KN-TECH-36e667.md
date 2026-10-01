---
id: KN-TECH-36e667
type: technique
title: "Genus-3 covers of binary elliptic curves over F_{q^3}: the non-hyperelliptic route is unsupported in characteristic 2, and no cover helps the original ECC2K-130 subgroup"
tags: [ghs, weil-descent, generalized-ghs, hess, genus-3, non-hyperelliptic, hyperelliptic, binary-field, characteristic-two, ecc2k-130, koblitz, index-calculus, diem, gaudry-thome, smith, scoped-negative, derivation, audit]
confidence: derivation
complexity: >-
  For E/F_{q^3}, q = 2^131, a subgroup of order about q^3: rho about q^{3/2} = 2^196.5;
  a hyperelliptic genus-3 cover with double-large-prime index calculus about
  q^{4/3} = 2^174.7; a non-hyperelliptic genus-3 cover with Diem's algorithm about
  q = 2^131. These are exponents of O~ bounds with constants, memory and transfer
  cost omitted. They are not benchmarks. The q^1 row has no known characteristic-2
  construction.
applicability: >-
  Elliptic curves over binary fields F_{2^{3l}} attacked by (generalized) GHS
  descent to F_{2^l}. The ECC2K-130 base curve lifted to F_{2^393} is covered only
  as a scoped negative.
source_refs: [KN-LIT-3305, KN-LIT-6987, KN-LIT-4552, KN-LIT-39d9ed, KN-LIT-197, KN-LIT-164, KN-LIT-a4d0f1, KN-TECH-3b593f, KN-TECH-4409e1]
added: 2026-09-30
superseded_by: null
---

## What this record is

This record audits a user-supplied argument (2026-09-30). The argument had four parts:

1. Specializing Hess' generalized GHS attack identifies binary elliptic curves
   over `F_{q^3}` that have a **non-hyperelliptic** genus-3 cover over `F_q`. A
   characteristic-2 `Õ(q)` route "already exists in theory".
2. It gave formal exponents for a new subgroup of order about `q^3`, with `q = 2^131`:
   rho `2^196.5`, hyperelliptic genus-3 index calculus `2^174.7`, and
   non-hyperelliptic genus-3 index calculus `2^131`.
3. Moving the original ECC2K-130 subgroup into a larger field preserves its
   order, and no cover advantage has been shown for it.
4. Hess identifies an obstruction to enlarging the field before descent in the
   original prime-degree setting.

The record checks each part against sources that were read, and states which
parts hold.

## Verdicts

| Claim | Verdict | Basis |
| --- | --- | --- |
| (2) exponent arithmetic | **Correct** as formal substitutions | `3·131/2 = 196.5`; `131·4/3 = 174.67`; `131·1 = 131`. The cost models are `Õ(q^{2-2/g})` hyperelliptic (KN-LIT-164, KN-LIT-a4d0f1) and `Õ(q^{2-2/(g-1)}) = Õ(q)` for non-hyperelliptic `g = 3` (KN-LIT-197; Diem–Thomé, J. Cryptology 21 (2008) 593–611). |
| (1) characteristic-2 non-hyperelliptic genus-3 cover from generalized GHS | **Not supported. The one primary source that treats the case says the opposite.** | See "The n = 3 binary case" below. |
| (3) no cover advantage for the ECC2K-130 subgroup | **Correct**, and stronger than stated | See "The original ECC2K-130 subgroup" below. |
| (4) Hess' field-enlargement obstruction | **Consistent but not checked beyond the abstract** | KN-LIT-6987 reports only that Hess "discuss[es] other possible extensions or variations of the GHS attack and conclude[s] that they are not likely to yield further improvements". The specific prime-degree obstruction has not been read in the corpus. |

## The n = 3 binary case

Menezes–Teske (KN-LIT-3305, CACR CORR 2004-25, §7 "The case n = 3") treat
exactly this setting: `N = 3l`, `K = F_{2^{3l}}`, `k = F_{2^l}`. Read from the
text:

- `X^3 + 1 = (X + 1)(X^2 + X + 1)`. The genus-3 family `W` consists of the
  curves `E_{a,b}` with `b = (γ1γ2)^2`, `Ord γ1 = X + 1`, `Ord γ2 = X^2 + X + 1`.
  These give `s1 = 1`, `s2 = 2`, `t = 3`, and a curve `C` of genus 3 over `F_q`.
- "In fact, in this case the generalized GHS reduction and the GHS reduction
  coincide". Among the representations, `γ1 = 1` is always available, so
  `E_{a,b} ∈ W` if and only if `Ord b = X^2 + X + 1`.
- "the resulting curve of genus 3 over F_q is **hyperelliptic**."
- The reach is roughly `q^2` curves directly. By an isogeny walk of expected
  `q/2` steps (their Assumption C), it extends to non-subfield curves with
  `#E(F_{q^3}) ≡ 0` or `2 (mod 8)`, according to their §7 and the `F_{2^210}`
  discussion in §8. The DLP then costs Gaudry–Thomé `O(q^{4/3+ε})`, and they
  classify `F_{2^{3l}}` as only **partially weak** on that basis.

The second possible route, an isogeny from a hyperelliptic genus-3 Jacobian to
a non-hyperelliptic one, is ruled out in characteristic 2 by Smith (KN-LIT-4552,
eprint 2007/428, §1): "it does not apply in characteristic 2 or 3. In the case
of characteristic 2, the subgroup S is the kernel of a verschiebung, so X is
necessarily hyperelliptic." The positive result is stated for characteristic
`p > 3`, covering about 18.57% of hyperelliptic genus-3 curves.

Momose–Chao style weak coverings over cubic extensions (KN-LIT-a4d0f1) are in
odd characteristic.

**Conclusion.** On the sources in hand, the best characteristic-2 genus-3 route
for curves over `F_{q^3}` is the **hyperelliptic** one, at `Õ(q^{4/3})`. The
`2^131` row has no characteristic-2 construction behind it. Claim (1) moves from
"exists in theory" to an **open construction question**.

## The original ECC2K-130 subgroup

The ECC2K-130 curve is a Koblitz curve defined over `F_2`, and its target
subgroup has prime order `r ≈ 2^129` in `E(F_{2^131})`. Consider `E(F_{2^393})` with
`q = 2^131`:

- The points of order `r` keep order `r`. Claim (3) is correct.
- `b ∈ F_2 ⊂ F_q` gives `Ord b = X + 1`, which is magic number `m = 1`. The GHS
  descent from `F_{q^3}` to `F_q` therefore returns a genus-1 curve, the curve
  itself, and no higher-genus cover arises.
- Even granting a genus-3 non-hyperelliptic cover, `Õ(q) = 2^131` exceeds rho on
  the original subgroup, which is about `2^{64.5}`. No genus-`g ≥ 1` cover over
  `F_{2^131}` whose index calculus costs at least `q^1` can beat rho on a
  `2^129` subgroup. This also exceeds rho on the new part of `E(F_{q^3})`,
  whose order is about `q^2`.
- The same point, stated about the phrase "a new subgroup of size about `q^3`":
  for a curve defined over `F_q`, `#E(F_{q^3}) = #E(F_q) · (≈ q^2)`. A subgroup of
  order about `q^3` needs a **different** curve over `F_{q^3}`, not ECC2K-130's.
  The comparison table in claim (2) is therefore about generic binary curves
  over `F_{2^393}`, not about the challenge.

## What would reopen claim (1)

Any one of the following:

- (a) An explicit binary elliptic curve over `F_{2^{3l}}` together with a
  computed genus-3 cover over `F_{2^l}` shown to be non-hyperelliptic. For
  example, its canonical image is a smooth plane quartic. The cover must be
  produced by a descent that Menezes–Teske §7 does not already enumerate, and
  the map's kernel must avoid the large prime subgroup.
- (b) A characteristic-2 isogeny from a hyperelliptic to a non-hyperelliptic
  genus-3 Jacobian whose kernel is not the Verschiebung kernel.
- (c) A source that the corpus has read and that states such a construction.

The cheapest test is (a) at toy scale, `l ∈ {5, 7}`: enumerate the Menezes–Teske
`W` family, compute each cover's genus and hyperellipticity, and look for any
non-hyperelliptic genus-3 cover. No experiment has been run for this record.

## Scope labels

`DERIVATION` / literature audit, binary fields, no experiment and no toy data.
The ECC2K-130 statement is a scoped negative for cover-based transfer to
`F_{2^393}` only. Claim (1) is recorded as **unsupported, not refuted**: the
user's report was not available to the corpus, and a construction outside
Menezes–Teske's §7 enumeration is not excluded here.
