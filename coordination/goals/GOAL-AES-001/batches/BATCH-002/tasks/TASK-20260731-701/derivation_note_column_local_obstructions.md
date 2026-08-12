# Two column-local obstructions in the algebra of the AES round function

**A standalone derivation note.**

| field | value |
|---|---|
| Task | TASK-20260731-701 (GOAL-AES-001, BATCH-002) |
| Role | idea-generator |
| Created | 2026-08-01 |
| `proof_status` | **derivation** — checkable arguments plus a recomputation script. Not `proven` (no machine-checked formal proof exists), not `empirical_only` (nothing here is a measurement of a cipher's behaviour). |
| Claim tier | not applicable: **no cryptanalytic claim is made** (see §0.2) |
| Verification script | `verify_derivation.py`, in this directory |
| Official state changed | none |

```yaml
inference:
  policy: research-deep
  requested_policy: research-deep
  resolved_model_id: claude-opus-5
  fallback_used: true
  fallback_reason: >-
    Structural. Under this Claude Code harness the orchestration/model-policies.yaml
    policy aliases cannot be resolved by subagent frontmatter (CLAUDE.md, "Model
    policy note"); all subagents run `model: inherit`, so a substitution is
    expected and is recorded rather than performed silently.
  model_verified: false        # `python3 -m orchestration.adapter doctor --probe` was NOT run in this session
  reasoning_effort: unrecorded
  independent_session: false
  standing_basis: >-
    inference-amendment commit 0137a051eb5828789eb267fa83c8278086578d4c
```

---

## 0. What this note says, and what it does not

### 0.1 Statement of purpose

Two elementary facts about the algebra of AES components are recorded here as
numbered propositions with derivations, consequences, scope statements, and a
script that recomputes every number in them from scratch. Both are **negative
structural facts**: they say that a particular *style of argument* is not
available, and they say why.

They are worth archiving for one reason: each of them is an error that an
ideation session actually made, and that a reader who has not made it yet would
plausibly make. Specifically:

- **Proposition 1** removes a transitivity argument. It is natural, and wrong,
  to reason "the linear layer of AES acts on a column by an invertible
  `4 x 4` matrix over `GF(2^8)`, and `GL(4, q)` together with the translations
  generates the 2-transitive group `AGL(4, q)`, so no nonconstant invariant of a
  column can exist." AES does not supply `GL(4, q)`. It supplies **one element**
  of it, of multiplicative order 4. Nonconstant invariants of a single column
  difference therefore exist in enormous abundance, and their non-existence may
  not be asserted by a transitivity argument.
- **Proposition 2** reassigns blame inside the S-box. It is natural, and wrong,
  to say that byte-wise inversion destroys `GF(2^8)`-collinearity. It preserves
  it exactly, including at zero coordinates under the AES convention
  `Inv(0) = 0`. The operative obstruction at SubBytes is the `GF(2)`-affine
  layer `L`.

### 0.2 Scope: what is NOT claimed

This note makes **no cryptanalytic claim about AES of any kind, at any round
count.** It contains no distinguisher, no key recovery, no complexity claim, no
measured structural excess, and **no barrier statement about AES security**.

In particular:

1. Nothing here asserts that any attack on AES is or is not possible.
2. Nothing here concerns full-round AES (10/12/14 rounds), AES-NI-deployed AES,
   or the security of any system that uses AES.
3. Proposition 1 is a *removal of an argument*, not a construction of one. It
   states that a certain closure argument is unavailable. It does **not** claim
   that the objects that argument tried to kill are useful; the honest position
   after Proposition 1 is that their status is *open*, which is strictly weaker
   than either "closed" or "promising".
4. Proposition 2 is a statement about two maps applied to a vector of bytes. It
   is **not** a statement about difference propagation through SubBytes; §3.5
   makes that limitation explicit, because it is exactly where an over-reading
   would occur.

### 0.3 Independence from other records

This note is self-contained: every definition it uses is given below, every
derivation is carried out here, and every number is recomputed by the script in
this directory. It cites `EV-AES-001` and `TASK-20260731-604` **only as
provenance** (§7) — for where these facts were first recomputed inside this
program — and depends on neither for any step of its argument. A reader with no
access to either can read, check, and reproduce everything below.

### 0.4 Literature status

**No primary source was read.** `eprint.iacr.org`, `csrc.nist.gov` and
`arxiv.org` are unreachable under this campaign's network policy. Nothing in
this note is presented as a citation, and no claim of novelty against the
external literature is made or implied: both propositions are elementary, and
the honest expectation is that both are well known to specialists. Their value
here is archival and local — they are recorded so that this program does not
repeat two specific errors — not as new mathematics. The AES specification is
not cited from a read document; the constants used below are stated explicitly
in §1 and are cross-checked by the script against the independently verified
harness `aes_reduced.py` (claim `C0`).

---

## 1. Setting and notation

Let `q = 2^8 = 256` and let `F = GF(2^8)` be the field with the AES reduction
polynomial

```
x^8 + x^4 + x^3 + x + 1      (0x11B)
```

A **state** is an element of `F^16` arranged as a `4 x 4` array of bytes in
column-major order. A **column** is an element of `F^4`.

The AES round function is `AddRoundKey . MixColumns . ShiftRows . SubBytes`
(with `MixColumns` omitted in the final round). This note concerns three of
those four operations, restricted to a single column:

- **AddRoundKey (ARK)** — translation `x |-> x + k` on `F^4` by the round-key
  column `k`.
- **MixColumns (MC)** — left multiplication by the fixed circulant matrix

```
        [ 02 03 01 01 ]
   M =  [ 01 02 03 01 ]        entries in hexadecimal, as elements of F
        [ 01 01 02 03 ]
        [ 03 01 01 02 ]
```

  `M` is invertible over `F`, so `M` is an element of `GL(4, F)`.
- **SubBytes (SB)** — the byte-wise map `S = L . Inv`, where
  - `Inv(x) = x^{-1}` for `x != 0` and `Inv(0) = 0` (the AES convention, and
    the reason `S` is defined on all of `F`), and
  - `L(b) = A b + 0x63` is `GF(2)`-affine on the 8 bits of `b`, with
    `A` the bit-circulant `b'_i = b_i + b_{i+4} + b_{i+5} + b_{i+6} + b_{i+7}`
    (indices mod 8, sums over `GF(2)`).

  `L` is `GF(2)`-affine and is **not** `GF(2^8)`-linear or `GF(2^8)`-semilinear;
  that is the content of Corollary 2.1.

ShiftRows is not used by either proposition and is mentioned only in §5.

**The difference convention.** Propositions and consequences that mention
"differences" refer to the XOR of two states under the *same* key. On
differences the translation `x |-> x + k` acts as the identity, since
`(x + k) + (y + k) = x + y`. This is the restriction that makes Proposition 1
sharp, and §2.4 states its effect on the group explicitly.

**Collinearity.** For nonzero `v, w` in `F^n`, write `v ~ w` ("`v` and `w` are
`GF(2^8)`-collinear") iff `w = lambda v` for some `lambda` in `F^*`. The
relation is defined on nonzero vectors only; the zero vector is excluded
throughout, and every statement below that mentions collinearity carries that
restriction. A map `f : F^n -> F^n` **preserves collinearity** iff `v ~ w`
implies `f(v) ~ f(w)` whenever `f(v)` and `f(w)` are both nonzero.

---

## 2. Proposition 1 — MixColumns supplies a cyclic group of order 4

> **Proposition 1.**
> **Hypothesis:** `M` is the AES MixColumns matrix over `F = GF(2^8)` displayed
> in §1, acting on a single column `F^4`.
> **Conclusion:** the multiplicative order of `M` in `GL(4, F)` is exactly `4`.
> The subgroup `<M>` it generates is therefore cyclic of order 4.

### 2.1 Derivation

`M` is the circulant matrix with first row `c = (02, 03, 01, 01)`, i.e.
`M[i][j] = c[(j - i) mod 4]`. The ring of `4 x 4` circulants over `F` is
isomorphic to

```
   R = F[y] / (y^4 - 1) = F[y] / (y^4 + 1)          (characteristic 2)
```

by sending a circulant with first row `c` to `c(y) = c_0 + c_1 y + c_2 y^2 +
c_3 y^3`. Multiplication of circulants corresponds to multiplication in `R`, so
the order of `M` equals the multiplicative order of `c(y)` in `R^*`.

In characteristic 2, `y^4 + 1 = (y + 1)^4`. Substitute `z = y + 1`, so that
`R = F[z] / (z^4)` and `z` is nilpotent of index 4. Expanding
`c(y) = 02 + 03 y + y^2 + y^3` at `y = z + 1`:

```
   02             = 02
   03 (z + 1)     = 03 z + 03
   (z + 1)^2      = z^2 + 1
   (z + 1)^3      = z^3 + z^2 + z + 1
```

Collecting coefficients over `F` (all additions are XOR):

```
   constant : 02 + 03 + 01 + 01 = 01
   z        : 03 + 01           = 02
   z^2      : 01 + 01           = 00
   z^3      : 01
```

so

```
   c = 1 + n,     n = 02 z + z^3,     n nilpotent (n^4 = 0 since z^4 = 0).
```

In characteristic 2, squaring is additive, hence

```
   c^2 = 1 + n^2 = 1 + (02 z + z^3)^2 = 1 + 04 z^2 + z^6 = 1 + 04 z^2
   c^4 = 1 + n^4 = 1 + (04 z^2)^2     = 1 + 10 z^4       = 1
```

Therefore `M^4 = I`. And `c^2 = 1 + 04 z^2 != 1` because `04 != 0` in `F`, so
`M^2 != I`; since the order divides 4 and is not 1 or 2, it is exactly 4. `[]`

*(Script claim `C1` recomputes `M^1, M^2, M^3, M^4` directly by matrix
multiplication over `F` and checks that the first power equal to `I` is the
fourth.)*

### 2.2 Consequence 1.1 — `<M>` is a vanishingly small subgroup of `GL(4, F)`

```
   |GL(4, GF(2^8))| = (q^4 - 1)(q^4 - q)(q^4 - q^2)(q^4 - q^3),   q = 256
                    = 4294967295 * 4294967040 * 4294901760 * 4278190080
                    ~ 3.39 * 10^38
   |<M>| / |GL(4, F)| = 4 / that  ~  1.18 * 10^-38
```

The exact integer and the ratio are recomputed by script claim `C2`. The point
is not the smallness itself — a cyclic subgroup of a large group is expected to
be small — but that **every step of a transitivity argument must be justified
from `<M>`, not from `GL(4, F)`**, and `<M>` is not a large subgroup in any
sense that would let the two be conflated.

### 2.3 Consequence 1.2 — the orbit of `e1` has size 4

Let `e1 = (01, 00, 00, 00)`. Its `<M>`-orbit is
`{ e1, M e1, M^2 e1, M^3 e1 }`, where `M e1` is the first column of `M`, namely
`(02, 01, 01, 03)`. These four vectors are pairwise distinct, so the orbit has
size exactly 4 — against `q^4 - 1 = 4294967295` nonzero vectors. Script claim
`C3` recomputes the orbit and its size.

For contrast: `GL(4, F)` is transitive on nonzero vectors, so under `GL(4, F)`
the orbit of `e1` would be all `4294967295` of them, and *that* is what a
"no nonconstant invariant exists" argument needs.

### 2.4 Consequence 1.3 — the number of orbits on nonzero vectors

Every `<M>`-orbit has size dividing `|<M>| = 4`, hence size at most 4. With
`q^4 - 1 = 4294967295` nonzero vectors, the number of orbits is at least

```
   ceil( 4294967295 / 4 ) = 1073741824
```

which in particular exceeds the figure `1073741823` recorded for this fact in
`EV-AES-001` observation B-3 (that figure is the floor rather than the ceiling
of the same quotient; both are valid lower bounds and the sharper one is stated
here). Script claim `C4` recomputes the bound.

The exact count follows from Burnside's lemma. Working in `R = F[z]/(z^4)` as
in §2.1: `M - I` corresponds to `n = 02 z + z^3 = z (02 + z^2)`, and
`02 + z^2` is a unit of `R` (nonzero constant term), so `n` is an associate of
`z`; the kernel of multiplication by `z` on `R` is the ideal `(z^3)`, of
dimension 1 over `F`. Likewise `M^2 - I` corresponds to `n^2 = 04 z^2`, an
associate of `z^2`, whose kernel is `(z^2)`, of dimension 2. And
`M^3 - I = M^{-1}(I - M)` has the same kernel as `M - I`. Hence

```
   dim ker(M   - I) = 1     nonzero fixed vectors of M   :   256   - 1 =   255
   dim ker(M^2 - I) = 2     nonzero fixed vectors of M^2 : 65536   - 1 = 65535
   dim ker(M^3 - I) = 1     nonzero fixed vectors of M^3 :   256   - 1 =   255
```

Burnside over the four group elements (the identity fixes all `q^4 - 1`):

```
   #orbits = ( 4294967295 + 255 + 65535 + 255 ) / 4 = 4295033340 / 4
           = 1073758335
```

Cross-check by orbit-size stratification, which must give the same number:
255 vectors lie in orbits of size 1; `65535 - 255 = 65280` lie in orbits of
size 2, giving `32640` such orbits; the remaining
`4294967295 - 65535 = 4294901760` lie in orbits of size 4, giving `1073725440`
such orbits; and `255 + 32640 + 1073725440 = 1073758335`. Script claim `C5`
recomputes the kernel dimensions by Gaussian elimination over `F` and both
counts.

**Reading.** A function on nonzero column differences is `<M>`-invariant
exactly when it is constant on these `1073758335` orbits. Nonconstant invariants
therefore exist in abundance — there are `1073758335` independent binary choices
available, not zero. *This does not make any of them useful.* It makes their
uselessness something that must be **argued or measured**, not deduced from
transitivity.

### 2.5 Consequence 1.4 — the group actually available, and what it is not

Two readings must be separated, and both fail the transitivity requirement.

**(a) On differences.** ARK acts as the identity on differences (§1), so it
contributes nothing. The group generated on a column *difference* by the
column-local linear operations of the AES round function is exactly `<M>`:
cyclic of order 4, with at least `1073741824` orbits on nonzero vectors
(exactly `1073758335`). It is **not transitive**. Every consequence that
requires transitivity — in particular "no nonconstant invariant of a single
column difference exists" — is unavailable.

**(b) On states.** If instead one works on states, ARK contributes the full
translation group `T ~ F^4` (as the round key varies), and the available group
is the semidirect product `T . <M>`, of order `q^4 * 4 = 17179869184`, sitting
inside `AGL(4, F)` of order `q^4 * |GL(4,F)| ~ 1.46 * 10^48`. `T . <M>` **is**
transitive on `F^4`, because `T` alone is. But a transitive group is
2-transitive iff a point stabiliser is transitive on the remaining points, and
the stabiliser of `0` in `T . <M>` is exactly `<M>`, which by Consequence 1.3
has `1073758335` orbits on the `4294967295` nonzero vectors. So `T . <M>` is
**not 2-transitive**, and the consequence "no nonconstant invariant of a pair of
column states exists" is likewise unavailable.

The general statement `<translations, GL(4,q)> = AGL(4,q)` is true, and is *not*
what is at issue. What is at issue is that AES supplies one element of
`GL(4, q)`, not the group.

### 2.6 Consequence 1.5 — what does survive

One thing survives, and it is elementary rather than group-theoretic: **any**
invertible linear map preserves collinearity. For `M` invertible and
`w = lambda v`,

```
   M w = M (lambda v) = lambda (M v)
```

because `M` is `F`-linear, so `M v ~ M w`. This holds for every element of
`GL(4, F)` and needs no transitivity. So the *collinearity relation* on column
differences propagates deterministically through MixColumns and (being
translation-invariant) through AddRoundKey. That, and not any statement about
invariants in general, is the correct residue of the argument Proposition 1
removes.

### 2.7 Scope of Proposition 1

- It concerns the matrix `M` acting on **one column**, and the group it
  generates. It says nothing about the group generated by the AES round
  function on the whole 128-bit state, which involves ShiftRows and SubBytes
  and is a different and much harder object.
- It is a statement about an *argument*, not about the cipher: it removes a
  deduction, and supplies no replacement conclusion in either direction.
- The count `1073758335` is a count of `<M>`-orbits. It is **not** a count of
  useful invariants, and no claim is made that any of them is measurable,
  key-dependent, or attack-relevant.

---

## 3. Proposition 2 — byte-wise inversion preserves collinearity

> **Proposition 2.**
> **Hypothesis:** `Inv : F -> F` is the AES inversion `Inv(x) = x^{-1}` for
> `x != 0` with the convention `Inv(0) = 0`, extended byte-wise to `F^n` by
> `Inv(v)_i = Inv(v_i)`. Let `lambda` be in `F^*`.
> **Conclusion:** `Inv(lambda v) = lambda^{-1} Inv(v)` for every `v` in `F^n`,
> including every `v` with one or more zero coordinates. Consequently `Inv`
> preserves `GF(2^8)`-collinearity: `v ~ w` implies `Inv(v) ~ Inv(w)`.

### 3.1 Derivation

Coordinate-wise, with `lambda != 0`.

*Case `v_i != 0`.* Then `lambda v_i != 0` (a field has no zero divisors), and

```
   Inv(lambda v_i) = (lambda v_i)^{-1} = lambda^{-1} v_i^{-1}
                   = lambda^{-1} Inv(v_i)
```

*Case `v_i = 0`.* Then `lambda v_i = 0`, so the left side is `Inv(0) = 0` by the
AES convention, and the right side is `lambda^{-1} Inv(0) = lambda^{-1} * 0 = 0`.
They agree. The convention is therefore not a nuisance to be waved past: it is
exactly what makes the identity hold on **all** of `F^n` rather than only on
the vectors with full support.

Combining the two cases coordinate-wise gives
`Inv(lambda v) = lambda^{-1} Inv(v)`. `[]`

For collinearity: let `v ~ w`, so `w = lambda v` with `lambda != 0`. Then
`Inv(w) = lambda^{-1} Inv(v)` with `lambda^{-1} != 0`. Since `Inv` is a
bijection on `F` (it is an involution), `Inv(v)` and `Inv(w)` are nonzero
whenever `v, w` are. Hence `Inv(v) ~ Inv(w)`. `[]`

Note the scalar is *inverted*, not preserved: `Inv` acts on the projective class
by a genuine map, not by the identity. The **relation** `~` is preserved; the
scalar is not.

*(Script claim `C6a` checks the scalar identity exhaustively over all
`255 * 256 = 65280` pairs `(lambda, x)`, so no sampling assumption enters.
Claims `C6b` and `C6c` check the vector-level statement on 4000 seeded random
collinear pairs with all coordinates nonzero and on 4000 with at least one zero
coordinate respectively.)*

### 3.2 Corollary 2.1 — the affine layer `L` is where collinearity dies

`L(b) = A b + 0x63` is `GF(2)`-affine, and `A` is not `GF(2^8)`-linear. `L` does
**not** preserve `GF(2^8)`-collinearity in general.

Deterministic counterexample, checkable by hand (script claim `C7c`):

```
   v      = ( 01, 00, 00, 00 )
   w      = 02 * v = ( 02, 00, 00, 00 )          so v ~ w
   L(00)  = 0x63,  L(01) = 0x7C,  L(02) = 0x5D
   L(v)   = ( 7C, 63, 63, 63 )
   L(w)   = ( 5D, 63, 63, 63 )
```

If `L(w) = mu L(v)` then comparing any of the last three coordinates gives
`63 = mu * 63`, hence `mu = 1`, hence `7C = 5D`, which is false. So
`L(v)` and `L(w)` are not collinear. `[]`

(The two S-box values used are `S(01) = L(Inv(01)) = L(01) = 0x7C` and
`S(0x8d) = L(Inv(0x8d)) = L(02) = 0x5D`, since `Inv(02) = 0x8d`; the script
recomputes `L` from its bit definition and does not take these on trust.)

Script claims `C7a` and `C7b` additionally measure the failure rate on 4000
seeded random non-constant collinear pairs, under `L` alone and under the full
S-box `S = L . Inv`. The predicted count of surviving collinear pairs is 0 in
both cases. Two random nonzero vectors of `F^4` are accidentally collinear with
probability `255 / (2^32 - 1) = 5.94e-08`, so the expected accidental count over
4000 draws is `2.4e-04`; the script's PASS condition is set at exactly 0 so that
any hit is surfaced rather than absorbed, and a count of 1 should be read as an
accidental collinear image rather than as a contradiction of this corollary.

### 3.3 Corollary 2.2 — the exception, stated rather than hidden

Corollary 2.1 says "not in general", and that qualifier is load-bearing. On the
degenerate family of **constant vectors** `v = (a, a, a, a)`, `L` *does* preserve
collinearity: `L(v) = (L(a), L(a), L(a), L(a))` is again a constant vector, and
any two nonzero constant vectors are collinear (scalar `L(b)/L(a)`). The only
exception inside the exception is that `L(a) = 0` for exactly one `a` in `F`, in
which case the image is the zero vector and collinearity is undefined by the
convention of §1.

Script claim `C8` checks this exhaustively over all `255 * 254 = 64770` pairs
`(a, lambda)` with `a != 0` and `lambda not in {0, 1}`, and asserts zero broken
cases. Because of this family, claims `C7a` and `C7b` sample **non-constant**
vectors, and this is recorded here rather than left as an unexplained sampling
choice.

### 3.4 Consequence — the correct reading of `S = L . Inv`

Within the factorisation `S = L . Inv`, the factor that fails to be
collinearity-covariant is `L`, not `Inv`. Any argument of the form "the object
dies at SubBytes because inversion destroys the `GF(2^8)`-structure" is wrong as
stated; the conclusion may survive, but the mechanism is the `GF(2)`-affine
layer.

This is the vector-valued form of a duality that is elementary at the level of a
single byte pair: `Inv` sends the ratio `(a : b)` to `(b : a)` and so acts on
`P^1(F)`, while `L(a)/L(b)` is not a function of `a/b`. The content added here is
that the same split holds for `n`-byte vectors and for the collinearity relation
in `F^n`, and that the AES zero convention makes it hold without exceptions.

### 3.5 Scope of Proposition 2 — the limitation that matters most

**Proposition 2 is a statement about `Inv` applied to a vector. It is not a
statement about difference propagation.**

SubBytes acts on *values*, not on differences: for the byte-wise S-box `S`, the
output difference `S(x + d) + S(x)` is not a function of `d` alone. Therefore
neither Proposition 2 nor Corollary 2.1 says, by itself, anything about whether
the collinearity of a *difference* vector is preserved across a SubBytes layer —
with `Inv`, with `L`, or with `S`. That question is not addressed here and is
not addressed by either proposition.

Symmetrically: on *values*, collinearity is destroyed by AddRoundKey, since
`y = lambda x` does not imply `y + k = lambda (x + k)` unless `k = lambda k`.

The precise scope of Proposition 2 is therefore:

- **What is established:** among the byte-wise maps composing SubBytes, `Inv` is
  collinearity-covariant on vectors and `L` is not.
- **What is not established:** anything about the propagation of collinearity of
  differences through a round, in either direction.

A reader who takes only one thing from §3 should take this paragraph, because it
is the boundary at which the correction of an over-strong claim would itself
become an over-strong claim.

---

## 4. What the two propositions do and do not license

**Licensed.**

1. Column-local invariants of a difference may not be excluded by a
   `GL`/`AGL` transitivity argument. On differences, only `<M> ~ Z/4` acts, with
   `1073758335` orbits on nonzero vectors; on states, `T . <M>` is transitive but
   not 2-transitive.
2. What genuinely propagates deterministically through ARK and MC on a column
   difference is the **collinearity relation**, for the elementary reason in
   §2.6, and only that.
3. Inside `S = L . Inv`, the collinearity-breaking factor is `L`.

**Not licensed.**

4. No claim that any column-local invariant is useful, measurable,
   key-dependent, or attack-relevant. Proposition 1 restores these objects to the
   status *open*, which is weaker than *promising*.
5. No claim about difference propagation through SubBytes (§3.5).
6. No claim about AES at any round count, and no barrier statement about AES
   security (§0.2).
7. No novelty claim against the external literature (§0.4).

---

## 5. A remark on ShiftRows, recorded to prevent a foreseeable misreading

ShiftRows is a permutation of the 16 byte positions. As a map on the whole
state viewed as `F^16` it is `F`-linear, so by the argument of §2.6 it preserves
whole-state collinearity. What it does **not** do is act column-wise: column `j`
of the output draws one byte from each of the four input columns. Any object
defined on a *column* — including the collinearity relation of §2.6 — is
therefore not carried by ShiftRows to a corresponding object on a column of the
next state.

This remark is not used by either proposition. It is recorded because
Proposition 1 removes one obstruction to column-local objects and a reader could
mistake that for a green light; ShiftRows is a separate and untouched
obstruction to *column-local* objects specifically, and it is the reason the
companion ideation record in this directory works at the ShiftRows-invariant
byte set (the 2-round super-box) instead.

---

## 6. Reproduction

### 6.1 Invocation

From this directory:

```
python3 verify_derivation.py
```

The script has no third-party dependencies (standard library only), seeds every
randomised check from constants recorded in its own source
(`SEED_C6B = 202608010001`, `SEED_C6C = 202608010002`,
`SEED_C7A = 202608010003`, `SEED_C7B = 202608010004`, `N_SAMPLES = 4000`),
prints exactly one line beginning `CLAIM ` per claim with a `PASS` / `FAIL` /
`SKIP` verdict, ends with a `SUMMARY` line, and exits non-zero iff any claim
FAILs.

### 6.2 EXECUTION STATUS — READ THIS BEFORE LOOKING FOR OUTPUT

**The script was NOT executed in the session that authored this note, and no
output of it is transcribed anywhere in this note or in any other artifact of
TASK-20260731-701.** The authoring agent had no command-execution tool
available in this session. Under `AGENTS.md` rule 9 an unobserved output is
never reported as observed, so the alternative — printing a plausible
transcript — is a fabrication and was not taken. This is a limitation of this
artifact and is stated as one rather than worked around.

What stands in its place:

- Every numerical value in this note is **derived analytically in the text
  above**, not read off a run. §2.1 derives the order; §2.2 gives the closed
  form for `|GL(4,F)|`; §2.3 exhibits the orbit; §2.4 derives the kernel
  dimensions from the ring structure and computes both the Burnside count and
  the stratified cross-check; §3.1 derives the inversion identity case by case;
  §3.2 gives a counterexample checkable by hand.
- The script's PASS conditions **encode exactly those derived values** (for
  example claim `C5` asserts the literal `1073758335` and the kernel dimensions
  `1, 2, 1`), so a run that passes confirms the derivations, and a run that
  fails identifies precisely which derived value is wrong.
- The script audits its own arithmetic before using it: claim `C-TAB` checks the
  log/antilog fast path against a reference shift-and-add multiplication on all
  65536 ordered pairs, and claim `C0` cross-checks the MixColumns matrix, the
  derived S-box and the field inverse against the independently verified
  `aes_reduced.py` harness (read-only; `SKIP` if that file is unavailable).

The validation task `TASK-20260731-705` re-executes this script from committed
source and recomputes both propositions by its own independent method. Until
that happens, the correct status of this note is: **derivations complete and
self-checking, machine recomputation pending.**

### 6.3 Claim index

| claim | what it recomputes | where derived |
|---|---|---|
| `C-TAB` | table arithmetic vs. reference multiplication, 65536 pairs | §6.2 |
| `C0` | constants vs. the `TASK-20260731-602` harness (read-only) | §1 |
| `C1` | order of `M` in `GL(4, GF(2^8))` is 4 | §2.1 |
| `C2` | `\|GL(4,GF(2^8))\|` and the ratio `4/\|GL\| ~ 1.18e-38` | §2.2 |
| `C3` | `<M>`-orbit of `e1` has size 4 | §2.3 |
| `C4` | `q^4-1 = 4294967295`; orbit count `>= 1073741824` | §2.4 |
| `C5` | kernel dims `1,2,1`; exact orbit count `1073758335`, two ways | §2.4 |
| `C6a` | `Inv(lambda x) = lambda^{-1} Inv(x)`, exhaustive incl. `x = 0` | §3.1 |
| `C6b` | collinearity under `Inv`, 4000 pairs, all coordinates nonzero | §3.1 |
| `C6c` | collinearity under `Inv`, 4000 pairs with a zero coordinate | §3.1 |
| `C7a` | collinearity broken by `L`, 4000 non-constant pairs | §3.2 |
| `C7b` | collinearity broken by `S = L . Inv`, 4000 non-constant pairs | §3.2 |
| `C7c` | the deterministic `L` counterexample `(01,00,00,00)`, `lambda=02` | §3.2 |
| `C8` | the constant-vector exception, exhaustive | §3.3 |
| `C9` | every entry of `M` is nonzero | App. A |
| `C10` | the entries of `M` generate `GF(2^8)^*` multiplicatively | App. A |
| `C11` | the `(lambda, k)` graph on 1020 nodes is strongly connected | App. A |

### 6.4 Steps not covered by the script

None. Every numerical assertion in §§2–3 and Appendix A appears in the table
above. The *derivations* themselves (the ring isomorphism in §2.1, the case
analysis in §3.1, Burnside's lemma in §2.4) are mathematical arguments and are
not the sort of thing a script checks; the script checks their numerical
conclusions, which is the strongest check available by recomputation.

---

## Appendix A — two auxiliary properties of `M`

These are recorded because a companion argument in
`candidate_report.yaml` (same directory, same task) uses exactly them. **No
claim of Proposition 1 or Proposition 2 depends on them**, and this note is
complete without this appendix.

- **A.1** Every one of the 16 entries of `M` is nonzero; the distinct entry
  values are `{01, 02, 03}`. Immediate from the display in §1. Script claim
  `C9`.
- **A.2** The multiplicative subgroup of `GF(2^8)^*` generated by the entries of
  `M` is all of `GF(2^8)^*`, of order 255 — indeed `0x03` alone is a generator
  under the AES reduction polynomial. Script claim `C10`, which also reports the
  orders of `0x02` and `0x03` individually.
- **A.3** The directed graph on the `255 * 4 = 1020` nodes `(lambda, k)`, with
  `lambda` in `GF(2^8)^*` and `k` in `{0,1,2,3}`, and an edge
  `(lambda, k) -> (lambda * M[j][k], j)` for each `j`, is strongly connected.
  Sketch: for each `k` the entries `M[j][k]` run over `{02, 03, 01, 01}`, so two
  of the four edges out of `(lambda, k)` preserve `lambda` and move the index,
  and from any index those index-moves reach all four indices; and one edge
  multiplies `lambda` by `0x03`, which by A.2 generates `GF(2^8)^*`. Script
  claim `C11` verifies strong connectivity by forward and reverse reachability
  rather than relying on this sketch.

---

## 7. Provenance, and the honest limitations of this note

**Provenance.** Both facts were first recomputed inside this program in the
independent validation session `TASK-20260731-604` (recorded as defects I-4 and
I-2 against the `TASK-20260731-601` ideation package) and are stated in
`EV-AES-001` observations B-3, B-4 and C-1, with a coordinator-side
corroboration of the order of `M` and of the inversion identity. This note is
written to stand **without** those records: they are named here so a reader can
trace the history, and nothing above is an appeal to them. The correction they
prompted is also recorded there: the `TASK-20260731-601` report contradicted
itself, blaming `Inv` in one place while its own enumerated closure correctly
blamed `L`. §3 resolves that contradiction in favour of `L`.

**Limitations.**

1. The script was not executed in the authoring session (§6.2). Machine
   confirmation is pending and this note does not assert it.
2. Cross-model independence is unavailable under this harness (standing basis
   `0137a051`): the sessions that recomputed these facts resolve to the same
   inherited model. Agreement between them is independence in *session*, not in
   *model*.
3. No primary source was read (§0.4). No novelty is claimed and none should be
   inferred; both propositions are elementary.
4. The AES specification is pinned operationally, not by citation: by the
   constants displayed in §1 and by claim `C0`'s cross-check against a harness
   whose full-round outputs were verified against two independent
   implementations. That is the strongest available grounding in this
   environment and it is weaker than a read specification.
5. This note asserts **no cryptanalytic claim about AES at any round count** and
   is **not a barrier statement about AES security** (§0.2). It removes one
   argument and reassigns the blame in another.
