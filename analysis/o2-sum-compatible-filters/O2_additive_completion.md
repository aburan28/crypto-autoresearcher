# Additive-character completion — families A, B, I, J close

Carries out the step `O2_derivation_attempt.md` §7.6 item 2 sketches and
declines to perform, and which §10 ranks as *"the largest missing piece and it
is routine rather than deep"*: extending the closure from **character filters**
(F1 families C, D, E, F, G) to **interval, bit-window and congruence filters**
(F1 families **A, B, I, J**).

**Status: EXPLORATORY ANALYSIS.** No frozen specification, no `EXP-*`, `RUN-*`,
`EV-*`, or ledger record is created or modified. Claim tier *exploratory*.
`certificate.kind: none`.

---

## 0. Answer first

| Question | Answer |
|---|---|
| Does the fibred argument transfer from multiplicative to additive characters? | **Yes**, and the degeneracy is *easier*: bounded by a pole-order argument, with no analogue of Lemma 7.2 needed. §2 |
| What is the degeneracy set? | `R = O` with `α + β = 0` — **a single point**, versus `O(D)` in the multiplicative case. §2.3 |
| Cost of completion? | `O(log p)` per factor, `O((log p)³)` total, absorbed into `p^{o(1)}`. §2.4 |
| Net effect on `M`? | `Λ = O(p^{-1/2+o(1)})`, so `M <= p^{1/2-o(1)}` — **identical to families C–G**. `j = 2` closes for A, B, I, J too. §3 |
| Does the measurement agree? | **Yes**: `α ∈ [-0.466, -0.426]` for all seven filters, against a **perfectly flat** dlog-interval control at `-0.000`. §4 |

---

## 1. Which inequality is being fed

Restating Theorem A in the form the Weil route actually consumes. The exact
identity of `O2_fourier_obstruction.md` §2 is

```
   eps  =  (1/M) Σ_t e(-td/M) · T_t ,        T_t = E_{P,Q}[ g_t(P) g_t(Q) conj(g_t(P+Q)) ]
```

with `g_t(P) = e(t·h(P)/M)`. Since `T_0 = 1`,

```
   eps  <=  1/M  +  max_{t ≠ 0} |T_t| .                                    (A′)
```

**`T_t` is a sum over the curve, not over dlogs.** This matters: the quantity
`Λ` that document reports is `max_ξ |ĝ_t(ξ)|` over *dlog* characters, and by
Parseval `|T_t| <= Λ`. Dlog characters are **not** algebraic functions on `E`, so
Weil cannot bound `Λ` directly — but it does not need to. Weil bounds `T_t`,
which is what (A′) consumes, and `Λ` remains a valid *conservative* upper bound
used for measurement in §4.

---

## 2. The completion

### 2.1 The class

`h : E(F_p) → [M]` is an **interval / bit-window / congruence filter** if each
level set `h^{-1}(c)` is determined by `x(P)` lying in a union of `O(1)`
intervals of `[0,p)` (families A, B) or an arithmetic progression (families I,
J). This covers `floor(Mx/p)`, `x mod M`, low/high/middle bit windows, popcount
thresholds and `y`-sign, i.e. every family [D] §7.6 lists as uncovered.

### 2.2 Expansion

For such `h`, `g_t(P) = e(t·h(P)/M)` is a function of `x(P)` alone, supported on
`O(1)` intervals, so its additive expansion

```
   g_t(P)  =  Σ_{α ∈ F_p} c_α^{(t)} · e_p( α · x(P) )
```

satisfies the standard incomplete-sum bound `Σ_α |c_α^{(t)}| = O(log p)`.
Substituting into `T_t`:

```
   T_t  =  Σ_{α,β,γ} c_α c_β conj(c_γ) · S(α,β,γ),
   S(α,β,γ) = E_{P,Q}[ e_p( α x(P) + β x(Q) − γ x(P+Q) ) ].
```

### 2.3 The fibred bound, and why the degeneracy is easier here

Fibre over `R = P+Q`; the substitution `(P,Q) ↦ (P,R)` is a bijection of
`E(F_p)²`, so

```
   N² S  =  Σ_R e_p(−γ x(R)) · Σ_P e_p( α x(P) + β x(R−P) ) .
```

The inner sum is a **one-variable additive character sum** of the rational
function `F_R(P) = α x(P) + β x(R−P)` on `E`, genus 1. Weil/Bombieri for additive
characters gives `|Σ_P e_p(F_R(P))| <= c √p` **unless `F_R` is Artin–Schreier
degenerate**, i.e. `F_R = g^p − g + const` for some `g ∈ \bar F_p(E)`.

**Lemma (degeneracy).** For `p > 2` and `(α,β) ≠ (0,0)`, `F_R` is
Artin–Schreier degenerate **only** when `R = O` and `α + β = 0`.

*Proof.* If `F_R = g^p − g + c` then every pole of `F_R` has order divisible by
`p` (a pole of `g` of order `m` gives one of order `pm`). Now `x(·)` has a double
pole at `O`, and `x(R−·)` has a double pole at `P = R`.

- If `α,β ≠ 0` and `R ≠ O`: these are **distinct** places, so `F_R` has pole
  order exactly 2 at each. Since `p > 2`, `2` is not divisible by `p`, so `F_R`
  is not of that form unless it has no poles at all — impossible, as it has
  order-2 poles.
- If exactly one of `α,β` is zero: `F_R` is a nonzero multiple of a function
  with a single double pole; same contradiction.
- If `R = O`: `x(O−P) = x(−P) = x(P)`, so `F_O = (α+β)x(P)`, which is pole-free
  (hence constant, hence degenerate) exactly when `α + β = 0`. ∎

**This is strictly cleaner than the multiplicative case.** [D]'s Lemma 7.1 needs
a divisor-multiplicity count giving `<= 2Δ` exceptional `R`, plus Lemma 7.2 to
handle the Case-B branch where both divisors are `≡ 0 (mod k)`. Here the
exceptional set is **a single point**, `R = O`, and there is no second branch:
pole orders do the whole job. [D] §7.5's uncarried hypothesis **(H3)** — the
explicit zero/pole count for `F_R` — has **no analogue** that needs carrying out.

### 2.4 Assembling

Each exceptional `R` contributes at most `N`, so `N²|S| <= N·c√p + N`, giving
`|S| = O(p^{-1/2})` using `N ≍ p`. Then

```
   |T_t|  <=  (Σ|c_α|)(Σ|c_β|)(Σ|c_γ|) · max|S|  =  O( (log p)³ · p^{-1/2} )
            =  p^{-1/2 + o(1)} .
```

---

## 3. What closes

Feeding §2.4 into (A′), a Wagner level's gain is `eps·M <= 1 + M·p^{-1/2+o(1)}`,
which is `p^{o(1)}` exactly when `M <= p^{1/2-o(1)}` — **the same threshold
families C–G obtain**, with the three logarithms absorbed into the `o(1)`.

| `j` | needed `M` | families C–G | **families A, B, I, J** |
|---|---|---|---|
| 2 | `p^{1/3}` | CLOSED | **CLOSED** |
| 3 | `p^{1/4}` | CLOSED | **CLOSED** |
| 4 | `p^{1/5}` | CLOSED | **CLOSED** |

Combined with `O2_composition_closure.md` and Theorem C, obstruction (O2) now
covers **every filter family F1 enumerated except H** (SHA-256), which is the
in-arm null and outside any algebraic class by construction.

---

## 4. Measurement

`interval_decay.py`. `Λ` measured by exhaustive whole-group enumeration on eight
prime-order curves, `p = 523 … 65539` (a **125× range**), at `M = 4` and `M = 16`.
`Λ >= |T_t|`, so these are conservative.

```
                filter      523     1033     2063     4111     8219    16417    32779    65539    alpha
        A: floor(Mx/p)  0.13548  0.09049  0.08376  0.06465  0.04987  0.02723  0.02151  0.01622   -0.443
            I: x mod M  0.13506  0.08156  0.06781  0.05376  0.04076  0.02886  0.02139  0.01549   -0.426
           B: low bits  0.13506  0.08156  0.06781  0.05376  0.04076  0.02886  0.02139  0.01549   -0.426
          B: high bits  0.16455  0.08921  0.08339  0.06324  0.04921  0.02756  0.02109  0.01616   -0.466
           B: mid bits  0.15344  0.09840  0.06719  0.05574  0.04063  0.03038  0.02040  0.01673   -0.449
      H: sha(x) [null]  0.14340  0.12268  0.07779  0.07275  0.04208  0.03409  0.02499  0.01619   -0.452
   P2: dlog-int [ctrl]  0.90032  0.90032  0.90032  0.90032  0.90032  0.90032  0.90032  0.90032   -0.000
```

**The control is the point.** `P2` is the dlog-interval filter of [D]'s
Proposition 2 — the *same shape* as row A, an interval pullback, but of the
discrete log instead of `x`. It is **flat to five decimals across the whole
range**, `α = -0.000`, while every `x`-based filter decays at `p^{-0.44}`.

This is the null-object discipline of `docs/inventor-protocol.md` §3 satisfied in
the strongest available form: the apparatus **provably can** detect a
non-decaying filter, because one is sitting in the table not decaying. It also
makes the **cost clause visible as a measurement** — `x(P)` is computable from
`P`, the dlog is not, and that is exactly the line the decay column draws.

**On the fitted value.** `α ≈ -0.44` rather than `-0.50` is the expected
signature of the `log p` completion loss: for `Λ ~ C·log p·p^{-1/2}` the local
slope is `-0.5 + 1/log p ≈ -0.39` mid-range, so the observed values sit between
the two predictions. **This is consistent with, not a confirmation of, the log
factor** — the SHA null sits at `-0.452` too, and a structureless filter has
`Λ ~ N^{-1/2}` for reasons having nothing to do with completion. The measurement
distinguishes *decaying* from *flat*; it does not resolve logarithms.

---

## 5. Hypotheses and limits

1. **(H1′) Weil/Bombieri for ADDITIVE character sums on a curve** — a *different*
   literature hypothesis from (H1)'s multiplicative statement. It is, however,
   **better attested**: the Encyclopedia of Mathematics *Bombieri–Weil bound*
   entry states precisely this case (`|S(f)| <= (2g − 1 + deg f)√q`, via
   Artin–Schreier coverings, Bombieri 1966), whereas the multiplicative curve
   statement needed `KN-LIT-7639` and remains partly untraced. A `KN-LIT` entry
   for (H1′) is owed on the same footing.
2. **The degeneracy lemma of §2.3 is mine and is new here** — it is not in [D],
   which only asserted that Artin–Schreier degeneracy "plays the role of" `k`-th
   power degeneracy. It is four lines and should be checked by hand. `p > 2` is
   used and is harmless.
3. **Explicit constants not carried out**, as throughout this program.
4. **`O(1)` intervals per level set** is a real restriction: a filter whose level
   sets are `p^{Ω(1)}` intervals is not covered, and its completion loss would
   not be logarithmic. Family J's popcount at large `M` should be checked
   against this.
5. **Toy scale.** `p <= 65539`. Under `AGENTS.md` rule 4 this is not crypto-scale
   validation and none is offered. The theorem is asymptotic; the computation
   checks its `p`-dependence over three orders of magnitude.

**`dominated_by` / `sota_delta`.** No algorithm proposed; no frontier row
occupied. `sota_delta = 0` on time, memory and data/queries; `dominated_by`
inapplicable rather than `null`.

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
    models. Recorded, never silently substituted (AGENTS.md rule 11). The
    degeneracy lemma in section 2.3 is short enough to check by hand, which is
    the intended mitigation.
  degraded_allowed: false
  degraded_requirements: []
  model_verified: false
  model_verified_reason: >-
    `python3 -m orchestration.adapter doctor --probe` was not run in this
    session. The identifier is unverified configuration.
```
