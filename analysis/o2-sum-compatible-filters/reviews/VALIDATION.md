# Independent validation — the (O2) analysis line, `GOAL-ECDLP-001`

**Role:** Validator. **Verdict: `failed`.** Five confirmed errors, four numeric
mismatches, and one self-contradiction in the knowledge entry. The core
mathematics largely survives; the *write-ups* do not, and one knowledge-corpus
coverage claim must be withdrawn.

A `failed` verdict here means the artifact set is not admissible as committed.
It does **not** mean the barrier conclusion is wrong — three of the four load-
bearing theorems check out and every reproducible number reproduces. It means
specific stated claims are false as written and must be superseded (never
overwritten — `AGENTS.md` rule 4) before this line is cited.

Snapshot validated: `HEAD = 198c410a5cad30f948f36229f9fba0c36a543451`, branch
`research/o2-quasigroup-scaling`, working tree clean for `analysis/` and
`knowledge/`. All artifacts are committed; no working-tree-only receipt was
accepted.

Environment of this validation run: Python 3.13.1, numpy 2.4.0,
macOS-26.6-arm64-arm-64bit-Mach-O — an exact match to what
`O2_fourier_obstruction.md` §6 records ("Python 3.13, numpy 2.4.0,
macOS-26.6-arm64").

---

## Item 1 — Do the scripts reproduce the quoted tables? **PASS, with four mismatches**

Commands run, all from `analysis/o2-sum-compatible-filters`:

```
python3 fourier_obstruction.py
python3 charfilter_decay.py
python3 interval_decay.py
python3 quasigroup_gap.py
python3 quasigroup_scaling.py
python3 scaling.py
```

All six ran to completion, exit 0. **Digit-for-digit agreement** with the quoted
tables in:

| document / table | script | result |
|---|---|---|
| `O2_fourier_obstruction.md` §6 scaling table (9 rows, 4 columns) | `scaling.py` | exact, all digits |
| `O2_fourier_obstruction.md` §6 log-log slopes `-0.463 / -0.441 / -0.455 / -0.466` | `scaling.py` | exact (`-0.4634 / -0.4414 / -0.4546 / -0.4655`) |
| `O2_fourier_obstruction.md` §6 `(T1)(T2)(T3) 18/18` | `fourier_obstruction.py` | exact |
| `O2_composition_closure.md` §3.4 `Λ ~ p^(-0.4964 / -0.4569 / -0.4665)`, `Λ√p` endpoints | `charfilter_decay.py` | exact |
| `O2_quasigroup_gap.md` §3 table (6 rows × 7 columns) | `quasigroup_gap.py` | exact, all digits |
| `O2_quasigroup_scaling.md` §2 table (8 rows × 7 columns) | `quasigroup_scaling.py` | exact, all digits (seeded `default_rng(20260802)`) |
| `O2_additive_completion.md` §4 table (7 rows × 9 columns, both `M`) | `interval_decay.py` | exact, all digits |

Positive/negative controls all behave as the documents state: `Z/1024` with
`M | N` gives `eps = 1.00000, Delta = 1.00000`; `Z/1021` gives `eps = 0.50049`
(doc: `0.5005`) with `Delta = 0.90032…0.99960` (doc: `0.90–0.9996`); the
dlog pull-back gives `Delta = 0.90032 / 0.99359` (doc: `0.900 / 0.994`).

### Mismatch 1 — **substantive**. `O2_quasigroup_gap.md` §3, finding 1

Document states:

> 1. **`(eps_quasi − 1/M)/Λ <= 0.17` everywhere** — over all filters, primes and
>    `M`. It never approaches `M`. At `M=5`, where `(★)` permits `5`, the
>    observed value is `0.11`.

Command: `python3 quasigroup_gap.py`. The maximum of the `(q-1/M)/L` column over
**all** rows is **`0.322`**, not `0.17`:

```
  dlog mod M     523   5  0.20000   0.93549   0.50096   0.50096   0.50249      0.322      0.323
    dlog-int     523   5  0.20000   0.93549   0.50096   0.50096   0.50249      0.322      0.323
```

This is contradicted by the document's own §3 table two lines above the claim,
which prints `**0.278**` for `dlog mod M`, `p=4111`, `M=4`. The `<= 0.17` bound
is true only over the `x mod M` and `char` filters (max `0.167`, at `p=523`,
`M=5`). The correct all-filter statement is `<= 0.33`.

The qualitative conclusion — "it never approaches `M`" — is **unaffected**
(`0.322` against `M ∈ {3,4,5}`). Only the number is wrong.

Propagated verbatim into: `O2_quasigroup_scaling.md` §1 ("found the normalized
excess `(eps − 1/M)/Λ <= 0.17`") and the `quasigroup_scaling.py` module
docstring.

### Mismatch 2 — minor. `O2_fourier_obstruction.md` §6

> That column is flat at `1.03–1.20` across a **230x** range of `N`

Command: `python3 scaling.py`. The `D/sqrt(logMN/N)` column ranges
**`1.016`–`1.200`**; the minimum is `1.016` at `N=7699`, and `1.026`, `1.029`,
`1.030` also fall below the stated `1.03`. The `230x` figure is correct
(`120413/523 = 230.2`).

### Mismatch 3 — minor. `O2_fourier_obstruction.md` §5, item 3

> Theorem A then *predicts* `eps_+ <= 1/M + Delta`, and the measured `eps_+`
> lands at `1/M` to three decimals.

Command: `python3 fourier_obstruction.py`. `|eps_+ − 1/M|` for the x-coordinate
filter: `0.00129` (N=499, M=4), `0.00264` (N=499, M=16), `0.00129` (N=1103,
M=4), `0.00091` (N=1103, M=16), `0.00013` (N=1901, M=4), `0.00114` (N=1901,
M=16). The deviation sits **in** the third decimal in five of six cases. "To
three decimals" holds only at `N=1901, M=4`.

### Mismatch 4 — minor, conservative direction. `README.md` and `O2_quasigroup_scaling.md` §3

> the exact worst case over all `f` stays ~160x below the `(star)` ceiling at
> `M = 32`

Command: `python3 quasigroup_scaling.py`. At `M = 32`, `excess_arb = 0.144`, so
the true looseness at `M=32` is `32/0.144 = 222×`. The figure `160` is
`32/0.196`, where `0.196` is the maximum of `excess_arb` over **all** `M`
(attained at `M = 16`). The error understates the producers' own margin, so it
is not an overclaim, but the row and the ceiling do not belong to the same `M`.

### Two further recording inaccuracies (not table mismatches)

- `README.md` §Reproducing: "The one sampled quantity in the whole directory is
  the *search* over Latin squares in `quasigroup_scaling.py` at `M > 5`."
  `quasigroup_scaling.py` also draws `K = 600` Latin squares at `M = 4` (where
  only 576 exist), and `excess_randf` is a `K = 600` sample over arbitrary `f`
  at **every** `M` including 4.
- `README.md` §Reproducing quotes "verified to 1e-15"; the script prints its own
  threshold as `1e-9`. The observed per-configuration errors across the 18
  prime-order configurations are `≤ 7.88e-16`, so `1e-15` is defensible for
  those 18, but it is not the tolerance the script asserts.

---

## Item 2 — Theorem A. **Bound VALID. Exact identity CONFIRMED WRONG.**

### The bound `eps <= 1/M + Λ` is correct, and "no factor `M`" is justified

Re-derived independently. Lemma 1 is correct under the document's own
conventions (`phihat(xi) = E_x[phi(x) e(-xi x/N)]`, inversion and Parseval both
check out). The `t = 0` term contributes exactly `1`; for `t ≠ 0`,
`|g_t| = 1` gives `sum_xi |ghat_t(xi)|^2 = 1` by Parseval, so each of the `M-1`
nonzero-`t` terms is bounded by `max_xi |ghat_t(xi)| ≤ Λ`. Dividing by `M`:
`eps <= 1/M + ((M-1)/M)·Λ`.

**No factor `M` is hidden in the `t`-sum.** The `t`-sum has `M` terms, but the
prefactor is `1/M` and the bound is a *maximum over `t`*, so the `M` cancels
exactly. This is the genuine difference from Theorem B / `(★)`, whose factor `M`
comes from Cauchy–Schwarz over level sets or over `M³` triples — a different
step. Confirmed.

### The exact identity as printed is wrong

`O2_fourier_obstruction.md` §2 states:

```
   eps_+ := Pr_{x,y}[ h(x+y) = f(h(x), h(y)) ]
          = (1/M) * sum_{t=0}^{M-1} e(-t*d/M) * sum_xi g_t-hat(xi) |g_t-hat(xi)|^2
```

Lemma 1 with `A = g_t`, `B = C = conj(g_t)` gives
`sum_alpha Ahat(alpha) Bhat(-alpha) Chat(-alpha)`. The document's own next line,
`conj(g)-hat(-alpha) = conj(ghat(alpha))`, is **correct** — but substituting it
yields

```
   sum_alpha  ghat_t(alpha) · conj(ghat_t(alpha))^2  =  sum_alpha conj(ghat_t(alpha)) · |ghat_t(alpha)|^2
```

which is the **complex conjugate** of what the document prints. Equivalently,
the printed identity computes `eps` for `f(a,b) = a + b − d`, not `a + b + d`.

Verified numerically (script at
`/private/tmp/.../scratchpad/check_thmA.py`, curve `p=503`, `N=499`):

```
         h   M   d   eps_brute                   DOC form                   ALT form
   x mod M   4   1    0.253228     0.254433  +9.97e-18i      0.253228  -9.54e-18i
   x mod M   4   3    0.254433     0.253228  +1.17e-17i      0.254433  -7.81e-18i
   x mod M  16   3    0.064112     0.065293  +1.27e-18i      0.064112  -1.65e-18i
       sha   4   1    0.253601     0.247128  +1.27e-17i      0.253601  -9.00e-18i
```

`ALT form` (with the conjugate) matches brute force to machine precision for
every `d`. `DOC form` matches only at `d = 0` and at `d = M/2`, and elsewhere
returns the value for `−d`.

**Impact.** None on the bound `(A)` (the two forms have equal modulus), none on
the closure, and none on any computed number in the directory. **But it exposes
a control gap:** Theorem A is *stated* for all affine `f(a,b) = a+b+d`, while
`fourier_obstruction.py` exercises **only `d = 0`** (`eps_group_law` hardcodes
`(a+bb) % M`). At `d = 0` the two forms are numerically indistinguishable
because the total is real. The advertised "exact identity verified to `1e-15`
on 18/18 configurations" therefore does not test the identity in the generality
in which it is stated, and did not catch a real error in it.

`KN-FIND-ffe1df` states Theorem A only in bound form, using `|T_t|`, so it is
**not** affected.

---

## Item 3 — Theorem C. **VALID. Every implication checks.**

Each link verified independently:

1. **Exact sum-compatibility + surjectivity ⟹ `f` associative.** Correct. For
   `a,b,c ∈ [M]` surjectivity supplies `P,Q,R`, and
   `f(f(a,b),c) = h((P+Q)+R) = h(P+(Q+R)) = f(a,f(b,c))` uses associativity of
   `+` twice. Surjectivity is used exactly once, to realize an arbitrary triple,
   and that is precisely what the computation needs. **It is enough.**
2. **Associative quasigroup ⟹ group.** Applied correctly; this is standard. The
   parenthetical justification is also correct: with `e = a\a` (so `a·e = a`),
   any `b` is `y·a` by right division, whence `b·e = y·(a·e) = y·a = b`; the
   symmetric argument gives a left identity, the two coincide, and division
   supplies inverses.
3. **`h` a surjective homomorphism ⟹ `M | N`.** Correct: the image of `Z/N` has
   order dividing `N`; `N` prime and `M < N` forces `M = 1`, contradicting
   `M ≥ 2`. Corollary C.1 is right as stated.

**On the specific worry — does it secretly need surjectivity onto a subgroup?**
No, and I checked the non-surjective case rather than taking the `(H6)`
citation on trust. Let `S = im(h)`. Compatibility gives `f(S×S) ⊆ S`. For
`a ∈ S`, `f(a,·)` is injective on `[M]` (quasigroup), hence injective from the
finite set `S` into `S`, hence bijective on `S`; same for `f(·,a)`. So
`(S, f|_S)` **is** a quasigroup, the identical argument runs on `S`, and the
conclusion becomes `|S| = M_eff` divides `N`, i.e. `h` is constant. The theorem
is therefore robust to dropping surjectivity, with `M` replaced by `M_eff` —
which is exactly the `(H6)` discipline the document invokes. No hidden
requirement.

**Scope, correctly stated by the producers.** Theorem C covers the **exact**
case only. `O2_quasigroup_gap.md` §2 ("What this does not do"), §4, and
`O2_quasigroup_scaling.md` §5 all say so plainly. The approximate case is
measurement, and both documents label it as such.

One wording nit: "`h` is a surjective homomorphism **by hypothesis**" — only
surjectivity is by hypothesis; the homomorphism property is derived. Harmless.

---

## Item 4 — The degeneracy lemma. **Pole-order core VALID. Assembly and class membership NOT.**

### 4a. The pole-order argument is correct

- Degeneracy `F = g^p − g + c` forces every pole order divisible by `p`: a pole
  of `g` of order `m` gives `g^p` a pole of order `pm > m`, so no cancellation.
  Correct.
- `x(·)` has a double pole at `O`; `x(R−·)` has a double pole at `P = R`, since
  `P ↦ R−P` is an automorphism of `E` and `R−P = O ⟺ P = R`. Correct, and
  correct **for every** `R ≠ O`.
- `R ≠ O`, `α,β ≠ 0`: two distinct places, pole order exactly `2` at each,
  `p > 2` so `p ∤ 2`. Non-degenerate. Correct.
- Exactly one of `α, β` zero: single double pole. Correct.
- `R = O`: `x(−P) = x(P)` so `F_O = (α+β)x(P)`; degenerate iff `α+β = 0`
  (`F ≡ 0 = 0^p − 0 + 0`), otherwise a double pole at `O` with `p > 2`. Correct.

**On the specific worries raised:**

- **`α` or `β` zero** — handled, correctly, by the lemma's second bullet.
- **2-torsion `R`** — *not* a special case. The places `O` and `R` are distinct
  for any `R ≠ O` whatever its order, and `x(R−·)`'s pole order is `2`
  regardless. No omission.
- **`R` where the two poles collide** — collision happens iff `R = O`, which is
  exactly the case the lemma isolates. No omission.
- `p = 2` is excluded explicitly and the exclusion is used.

So the lemma is right, and `KN-LIT-f6de4b`'s judgement — "the §2.3 degeneracy
lemma is a *pole-order* argument that is self-contained given the criterion" —
is correct.

### 4b. §2.4's assembly is false as quantified — the `(α,β) = (0,0)` term

§2.4 concludes `|T_t| <= (Σ|c_α|)(Σ|c_β|)(Σ|c_γ|) · max|S|` with
`max|S| = O(p^{-1/2})`. But `S(α,β,γ) = E_{P,Q}[e_p(αx(P)+βx(Q)−γx(P+Q))]`
satisfies

```
   S(0,0,0) = 1     exactly.
```

For `(α,β) = (0,0)` the inner sum over `P` is `N` for **every** `R` — every `R`
is exceptional, `F_R ≡ 0` is degenerate — so the "one exceptional point"
accounting does not apply, and `max|S| = 1`, making the assembled bound
`O((log p)³)`: vacuous. The lemma explicitly excludes `(α,β) = (0,0)` and §2.4
never returns to it.

This is the only bad block: `α = 0, β ≠ 0` gives `F_R = βx(R−P)`, non-degenerate
for every `R` including `R = O`; and `(α,β) = (0,0)`, `γ ≠ 0` gives
`S = (1/N)Σ_R e_p(−γ x(R)) = O(p^{-1/2})` by Weil on `E`. So the residue is the
single term `(0,0,0)`, contributing `|c_0^{(t)}|² c_0^{(t)}`.

**The repair requires a hypothesis the document does not state**: `|c_0^{(t)}|`
small for `t ≠ 0`, i.e. balance / non-redundancy of `h`. `[D]` states this as
`(H6)`; `O2_additive_completion.md` states no analogue. Measured
`max_t |c_0^{(t)}|`:

```
=== A: floor(Mx/p)  /  I: x mod M ===   (identical values)
       p         M=4        M=16        M=64       M=256
    1021     0.00098     0.00279     0.00293     0.00294
   65521     0.00002     0.00002     0.00021     0.00023

=== J: popcount ===
    1021     0.02940     0.82644     0.98825     0.99926
   65521     0.00398     0.73346     0.98094     0.99880
```

So the repair is available for the filters actually measured, and **not**
available for popcount.

Also unmentioned: the Weil sum must exclude the poles of `F_R` (`P = O` and
`P = R`), a 2-point correction absorbed into constants. Minor.

### 4c. The `O(log p)` completion loss — true for the measured filters, not established by the stated argument

§2.2 asserts `Σ_α |c_α^{(t)}| = O(log p)`, justified by "`g_t` … supported on
`O(1)` intervals". But `g_t = Σ_c e(tc/M) 1_{A_c}` has `M` level sets, and the
triangle inequality over them yields only `O(M log p)`. Since `M ~ p^{1/3}` is
the regime being closed and the bound is used **cubed**, an `M`-dependence here
would be fatal. Measured `max_{t≠0} Σ_α |c_α^{(t)}|`:

```
       p        M=4      M=16      M=64     M=256
    1021       5.37      5.37      5.37      5.37
    4093       6.26      6.26      6.26      6.26
   16381       7.14      7.14      7.14      7.14
   65521       8.02      8.02      8.02      8.02          (log 65521 = 11.09)
```

Uniform in `M` and growing like `~0.63 log p`. **The claim is true for
`floor(Mx/p)` and `x mod M`; the argument given for it does not establish the
uniformity in `M` that the closure needs.**

For popcount the same quantity is `16.15 / 27.79 / 48.16 / 85.33` at
`p = 1021 / 4093 / 16381 / 65521` — growth `~p^{0.39}`, **not** `O(log p)`.

### 4d. The class does not contain several families the document says it closes

`O2_additive_completion.md` §2.1 defines the class as: each level set determined
by `x(P)` in a union of `O(1)` intervals of `[0,p)` (assigned to families A, B)
or an arithmetic progression (assigned to families I, J). Against F1's actual
taxonomy (`F1_sum_compatible_filter_search.md` §3):

| F1 family | what it actually contains | in the class? |
|---|---|---|
| A | bit-windows of `x`, **of `y`**, **joint `(x,y)` windows**, and `x±y`, `xy`, `x⊕y`, `x²`, `x³`, `x^{-1}` mod `M` | only the `x`-window members |
| B | `x mod k` **and `y mod k`**, `k ∈ {5,7,9,15,17}` | only the `x` members (and these are APs, not `O(1)` intervals — the label assignment is inverted) |
| I | popcount of `x` mod 4, **decimal digit sum** mod 4 | **no** — neither `O(1)` intervals nor an AP; measured `L¹ ~ p^{0.39}` |
| J | **`y`-sign**, alone and joint with `x`-windows | **no** — not a function of `x(P)` at all, so §2.2's expansion never starts |

The document's own §5.4 concedes "Family J's popcount at large `M` should be
checked against this" — which is both a hedge against §2.1's flat assertion and
a mislabelling (popcount is family **I**; family **J** is `y`-sign).
`interval_decay.py` measures only `x`-functions (`floor(Mx/p)`, `x mod M`, low /
high / mid bit windows of `x`, the SHA null, the dlog control) — so popcount,
digit sums, `y`-sign, joint windows, `x±y`, `xy`, `x⊕y`, `x²`, `x³`, `x^{-1}`
have **neither proof nor measurement** anywhere in this directory.

---

## Item 5 — The composition. **Arithmetic correct. The substitution is INVALID as written; the conclusion survives after a stated repair.**

### 5a. The exponent arithmetic is right

`(A) + (W)` gives `eps <= 1/M + c₁ D p^{-1/2} + c₂ D / N`; multiplying by `M`
(Lemma 5) gives `gain <= 1 + M(c₁ D p^{-1/2} + c₂ D/N)`. With `D = p^{o(1)}` and
`N ≍ p` (Hasse), the bracket is `p^{-1/2+o(1)}`, so the gain is `p^{o(1)}` for
`M <= p^{1/2-o(1)}`. Correct, and mildly conservative (the sharp threshold is
`M <= p^{1/2+o(1)}`); conservatism is the safe direction for a closure claim.
`j = 2` needs `M ~ p^{1/3}`, which is below `p^{1/2}` by a polynomial margin.

`[D]`'s own route substitutes into the `M`-lossy `(★)`, giving `M <= p^{1/4}`.
The single factor `M` is indeed the whole difference. Correct.

### 5b. "Wagner needs `M ≈ p^{1/(j+1)}`" — correct

Standard `k`-tree with `k = 2^j`: lists of size `N^{1/(j+1)}`, each of `j`
levels clearing `log N/(j+1)` bits, so the bucket alphabet is `M = N^{1/(j+1)}`,
and `N ≍ p`. `[D]` §7.4 re-derives it from the leaf-list side and gets the same
answer. The counterfactual exponent `(2^j+m)/(m(j+1))` is confirmed against
`F1_sum_compatible_filter_search.md` §1 and reproduces `0.4167 / 0.3750 / 0.4000`
at `m = 16, j = 2,3,4` — and is implemented identically in both
`charfilter_decay.py` and `scaling.py`.

### 5c. The substitution itself is invalid — this is the load-bearing error

`(A)` is stated with `Λ` (`[F]`'s `Delta`, a max over **dlog** characters);
`(W)` bounds `max_{ψ≠1}|T̂_ψ|` (`[D]`'s trilinear coefficient). Theorem A's own
identity gives only the **one-way** inequality `|T_t| <= Λ`. Substituting a bound
on the *smaller* quantity into an inequality stated in terms of the *larger* one
does not follow.

Measured (script `check_lambda_vs_T.py`, same curves as `charfilter_decay.py`):

```
      p       N           filter   M     Lambda   max|T_t|  ratio L/T
    523     523       char C r=2   4   0.091194   0.001627      56.05
   2063    2129       char C r=2   4   0.048754   0.001491      32.70
   8219    8117       char C r=2   4   0.028805   0.000556      51.79
  32779   32909       char C r=2   4   0.014179   0.000054     262.03
    523     523          x mod M   4   0.135065   0.023080       5.85
   32779   32909          x mod M   4   0.021650   0.002834       7.64
```

They are not the same object, they differ by up to 262×, and the gap **grows**
with `p`.

**Repair (available, and it costs nothing):** use `(A′) eps <= 1/M +
max_{t≠0}|T_t|`, which is the Theorem A identity *before* Parseval is applied.
Then `(W)` applies directly and `(C)` follows unchanged. So the closure
conclusion survives; the composition's stated derivation does not.

Direction matters for the empirical arm: since `Λ >= |T_t|`, measuring `Λ` decay
at `p^{-0.457…-0.496}` is **conservative** for the conclusion, and the measured
`|T_t|` decays faster still (`0.001627 → 0.000054` over a 63× range in `p`,
`~p^{-0.82}`, consistent with `[D]` §8.5's conjectured `O(Δ/p)`). The empirical
support is stronger than claimed, not weaker.

---

## Item 6 — Notation. **The table is correct on the collision it flags, and wrong on the row below it.**

Verified against sources:

- `[D]` §7.1 defines a character filter of complexity `(k, r, Δ)` with
  `Σ_j deg(g_j) <= Δ` — so `[D]`'s `Δ` **is** divisor/degree complexity. ✔
- `[F]` §1 defines `Delta(h) = max_{t≠0} max_ξ |ghat_t(ξ)|` — so `[F]`'s `Delta`
  **is** the max Fourier coefficient. ✔
- The collision is real, the rename to `D` and `Λ` is the right fix, and **no
  argument in the composition conflates `D` with `Λ`**: `(W)` uses `D` as degree
  complexity throughout, matching `[D]` Theorem 3 step 6 (`|T̂_ψ| ≤ c₁Δp^{-1/2} +
  2Δ/N`, i.e. `c₂ = 2`). ✔
- Row 1 (`δ(h,f)` vs `eps`) and row 5 (`delta` vs `λ`) also correctly separate
  `[D]`'s agreement `δ` from `[F]`'s level-set coefficient `delta`. ✔

**But the row the table gets wrong is the one it treats as settled.** §1.1
asserts:

> `Λ` and `max_{ψ≠1}|T̂_ψ|` are the same object reached two ways … This is the
> hinge of the composition.

They are not the same object (item 5c, measured 262× apart). So the document
resolves one symbol collision and introduces a second, more consequential one at
the point it identifies as load-bearing.

The conflation is inherited by:
- `charfilter_decay.py` docstring: "Composing them predicts … `Lambda(h) = O(p^{-1/2})`" and "If Weil governs Lambda, the fitted exponent is ~0.5." Weil does not govern `Λ`.
- `O2_composition_closure.md` §3.4, headed "Empirical check on `(W)`" — it measures `Λ`, not `T̂_ψ`.
- `KN-LIT-7639` §Relevance: "The closure's dependence is on the **shape** `Λ = O(D·p^{-1/2})`, which is verified here."

`O2_additive_completion.md` §1 states the correct position — "Dlog characters
are **not** algebraic functions on `E`, so Weil cannot bound `Λ` directly — but
it does not need to" — without noting that the composition had asserted the
identification. And `KN-FIND-ffe1df` states Theorem A in the repaired `|T_t|`
form and describes the composition as substituting `|T_t| = O(D·p^{-1/2})`, so
**the knowledge entry is correct here and the document it summarizes is not.**

---

## Item 7 — Does `KN-FIND-ffe1df` represent what the documents prove?

**Partly. Two claims must be weakened, one withdrawn, and one dropped limitation
restored.**

### 7a. WITHDRAW — coverage of F1 families I and J, and most of A

Coverage table row:

> | A, B, I, J — intervals, bit windows, congruences, popcount, `y`-sign | closed | Theorem A + Weil (additive completion) |

Not supported (item 4d). Popcount and decimal digit sums (family **I**) fail the
class's own `O(1)`-intervals / AP hypothesis and are measured to have
`L¹ ~ p^{0.39}`, not `O(log p)`. `y`-sign (family **J**) is not a function of
`x(P)`, so the §2.2 expansion the whole argument rests on never begins. Family A
contains `y`-windows, joint `(x,y)` windows, and `x±y`, `xy`, `x⊕y`, `x²`, `x³`,
`x^{-1}` mod `M`, none of which are in the class. Family B contains `y mod k`.

Defensible replacement: *closed for filters that are functions of `x(P)` alone
whose level sets are `O(1)` intervals or arithmetic progressions —
`floor(Mx/p)`, `x mod M`, `x`-bit-windows — conditional on (H1′), which is
untraced.*

### 7b. WITHDRAW — "(H1′) … better attested"

"What is NOT established" item 3 states:

> (H1′) the *additive* case is better attested but has **no `KN-LIT` entry
> yet** — one is owed.

Both halves are false as committed, and are refuted by a document the **same
file** cites in its Artifacts block: `KN-LIT-f6de4b` exists, and concludes
"**So (H1′) is materially LESS well attested than (H1)** — the reverse of what
that document claims," with the curve-level additive bound and the
Artin–Schreier criterion both in its NOT-verified rows. The Artifacts line
("largely untraced; see 'What is NOT established' item 3, which that entry
corrects downward") was added without updating item 3, leaving a live
self-contradiction inside one immutable record.

### 7c. WEAKEN — the coverage table carries no conditionality marker

Rows C–G are marked `closed` via "Theorem A + Weil (multiplicative)", but
`KN-LIT-7639` records that the curve-level statement for **general character
order `k > 2`** is untraced, and states explicitly: "**family D (cubic,
quartic, octic residue characters, `k = 3,4,8`) is not covered by this entry**."
Family D is nonetheless in the `closed` row. Rows A/B/I/J rest on (H1′), which
is untraced in full. `KN-FIND` item 3 mentions the `k > 2` gap in prose, but the
table — which is what a reader will cite — says `closed` unqualified.

### 7d. RESTORE — a limitation that was dropped in transit

`O2_fourier_obstruction.md` §7 limitation 4:

> **Uniform `P, Q` only.** Wagner's later levels operate on lists already
> filtered at earlier levels, so their inputs are conditioned. The theorem
> applies verbatim to level 1 and needs restating for levels `>= 2`.

This appears in neither `O2_composition_closure.md` §5 ("What remains open",
six items) nor `KN-FIND-ffe1df` ("What is NOT established", five items). The
headline "every Wagner configuration `j >= 2` is closed" therefore rests on an
inequality proved for the **first level only**. This is the single most
important omission in the knowledge entry, because it is a limitation the
producers themselves identified and then lost.

### 7e. What `KN-FIND-ffe1df` gets right, and should keep

Recorded accurately and, in several places, against interest:

- Theorem A stated in the correct `max_{t≠0}|T_t|` form (better than the
  document it summarizes).
- Theorem C stated correctly and scoped to the exact case.
- "Barrier result, not an attack"; `sota_delta = 0` on time/memory/data;
  `dominated_by` **inapplicable** rather than `null` — the inventor-protocol
  Pareto-honesty requirement is met, not gamed.
- Toy scale `N <= 65539` flagged under `AGENTS.md` rule 4. (Strictly,
  `scaling.py` reaches `N = 120413`; the bound understates, which is harmless.)
- Independence recorded as **procedural, not model-level** — both derivations
  resolved to `claude-opus-5`.
- The missing `EV-* → DEC-* → KN-FIND-*` chain named as "a real gap".
- The `KN-LIT-7639` sequential-ID provenance defect disclosed voluntarily.

---

## Controls — `docs/inventor-protocol.md` §3. **SATISFIED, and unusually well.**

The protocol's canonical artifact tell is "a quantity that does not decay when
the parameter meant to destroy it increases." This directory runs that test in
**both** directions and states what the quantity should do:

- `interval_decay.py` carries the dlog-interval filter of `[D]` Proposition 2 as
  a positive control of the *same shape* as the object under test (an interval
  pullback), and it does **not** decay: `α = -0.000`, flat to five decimals
  (`0.90032` at every `p` from 523 to 65539), beside `α ∈ [-0.466, -0.426]` for
  every `x`-based filter. An apparatus that provably can see a non-decaying
  filter is reporting decay on the others.
- Structureless SHA-256 null in every table; the curve filter is
  indistinguishable from it.
- `quasigroup_scaling.py` runs a matched-`K` random-`f` null beside the
  quasigroup arm, and **deliberately rejects** the cheap isotope-of-the-cyclic-
  table sampler in favour of Jacobson–Matthews precisely because the cheap one
  would rig the control. Verified in the code: the chain is a genuine JM
  incidence-cube walk, seeded `default_rng(20260802)`, `50M²` burn-in and `8M²`
  steps between draws, with `is_latin` asserted on each sample.
- Positive controls where a filter must exist: `Z/1024` with `M | N`
  (`eps = 1.0000`), `Z/1021` (`eps = 0.50049`), and `[D]` §4's composite-order
  arm.

No reported signal in this directory lacks a null object of the same shape.

---

## What I could NOT verify, and why

1. **(H1) and (H1′) themselves.** No primary source was retrieved in this
   session either. Bombieri 1966 and Perel'muter were not obtained. The
   Artin–Schreier pole-order *algebra* is elementary and I verified it; the
   **bound** it gates is untraced to a primary source, as `KN-LIT-f6de4b`
   already records. The whole additive-completion closure and the general-`k`
   part of the multiplicative one hang on this.
2. **(H3)**, `[D]`'s explicit zero/pole count for `F_R`, asserted as `O(D)` and
   not carried out. Affects `c₁` only.
3. **Every computation in `[D]` (`O2_derivation_attempt.md`).** Its §8 states
   the scripts are "under the session scratchpad (`O2/c{1,2,3,5,6,7,8}*.py`);
   **scratch, not archived artifacts**". They are not in this directory. So the
   numbers in `[D]` §3 (Proposition 2 verification), §4 (Theorem 1 exhaustive
   check + composite-order positive control), §6 (`C1`/`C2` chord identity), and
   §8.3/§8.5 (`GAP` decay table, `|T̂_ψ|` scaling) are **not reproducible from
   the committed tree**. `[D]` is the source of Proposition 2, Theorem 3, and
   the Weil machinery the entire composition consumes. This is the largest
   artifact gap in the line.
4. **`F1_sum_compatible_filter_search.md`'s 507-family sweep** — same status; not
   reproducible from this directory. I verified only that the `1.101×` figure
   `[F]` §4 quotes is consistent with F1 §7's own tables (global max real lift
   over prime-order arms, `x_high_256` at `M_eff = 256`).
5. **Anything at cryptographic scale.** Everything here is `p <= 65539` /
   `N <= 120413`. Under `AGENTS.md` rule 4 and rule 7 this is not crypto-scale
   validation, the documents say so consistently, and I confirm the limitation
   rather than the claim.
6. **`|T̂_ψ| = O(Δ/p)`** (`[D]` §10's conditional strengthening) — not attempted.
7. **Receipt package.** There is no `EXP-*`, `RUN-*`, `EV-*` or `DEC-*` record,
   no run manifest, no per-run command/seed/environment/resource record, and no
   `inference` probe verification (`model_verified: false` everywhere, honestly
   recorded). Only `quasigroup_scaling.py` carries a seed; the other scripts are
   deterministic and reproduce, which I confirmed. Claim tier is declared
   *exploratory* with `certificate.kind: none`, and `KN-FIND-ffe1df` names the
   missing promotion chain itself — so this is a disclosed gap, not a concealed
   one, but the artifact policy's package is absent and no promotion should
   proceed on it.

---

## Explicit answer: should any claim in `KN-FIND-ffe1df` be weakened or withdrawn?

**Yes — three.**

| # | claim | action |
|---|---|---|
| 1 | Coverage table: "A, B, I, J — intervals, bit windows, congruences, **popcount**, **`y`-sign** — closed" | **WITHDRAW** the popcount / digit-sum (family I), `y`-sign (family J), and `y`- / joint- / nonlinear members of families A and B. Replace with: functions of `x(P)` alone whose level sets are `O(1)` intervals or APs. |
| 2 | "What is NOT established" item 3: "(H1′) the additive case is **better attested** but has **no `KN-LIT` entry yet**" | **WITHDRAW** both halves. `KN-LIT-f6de4b` exists and concludes the opposite; the contradiction is internal to this file. |
| 3 | Coverage table rows marked `closed` with no conditionality | **WEAKEN** to *closed conditional on (H1)/(H1′)*, and remove F1 family D (`k = 3,4,8`) from the closed set until the `k > 2` curve statement is traced. |

**And one restoration:** add `[F]` §7 limitation 4 (uniform independent `P,Q`;
proved for Wagner level 1 only, levels `>= 2` operate on conditioned lists) to
"What is NOT established". It was present upstream and was dropped.

Everything else in `KN-FIND-ffe1df` is an accurate representation of what the
documents establish, including its own statement that no independent Validator
or Red Team pass existed at the time of writing.

**Not to be weakened:** Theorem C, the Theorem A *bound*, the `Λ`-decay and
excess measurements, the barrier-not-attack framing, and the toy-scale
disclosure. Those hold.

---

## Corrections owed in the analysis documents (supersede, do not overwrite)

1. `O2_fourier_obstruction.md` §2 — Theorem A's exact identity needs a conjugate
   (or `e(+td/M)`). Bound and conclusion unaffected. Add: the verification
   covers `d = 0` only.
2. `O2_composition_closure.md` §1.1 and §3.1–3.2 — `Λ ≠ max_{ψ≠1}|T̂_ψ|`; restate
   the composition through `(A′)`. `charfilter_decay.py`'s docstring and
   `KN-LIT-7639` §Relevance inherit the same statement.
3. `O2_quasigroup_gap.md` §3 finding 1 — `0.17` → `0.33` over all filters (or
   restrict the claim to the non-dlog filters). Propagated to
   `O2_quasigroup_scaling.md` §1 and `quasigroup_scaling.py`'s docstring.
4. `O2_additive_completion.md` §2.4 — handle the `(α,β) = (0,0)` block and state
   the balance / non-redundancy hypothesis it needs; §2.1 — correct the
   class-to-family mapping and remove popcount and `y`-sign from the covered
   list; §2.2 — the `O(log p)` L¹ bound needs a justification uniform in `M`.
5. `O2_additive_completion.md` §5.1 — "better attested" is superseded by
   `KN-LIT-f6de4b` (that entry already lists this correction as owed and
   deliberately unapplied pending review; it can now be applied).
6. Minor: `O2_fourier_obstruction.md` §6 `1.03` → `1.016`; §5 "to three
   decimals"; `README.md` sampling scope and the `1e-15` tolerance; the
   `~160×`-at-`M=32` figure.

---

```yaml
validation_report:
  id: VAL-20260803-3b7c1a
  task_id: null                       # dispatched conversationally; no TASK-* envelope supplied
  run_ids: []                         # no RUN-* records exist for this line
  artifact_checks:
    - path: analysis/o2-sum-compatible-filters/
      committed: true
      head: 198c410a5cad30f948f36229f9fba0c36a543451
      dirty_tree: false
      status: present
    - path: knowledge/findings/KN-FIND-ffe1df.md
      committed: true
      status: present
    - path: knowledge/literature/KN-LIT-7639.md
      committed: true
      status: present
    - path: knowledge/literature/KN-LIT-f6de4b.md
      committed: true
      status: present
    - path: "O2_derivation_attempt.md computations (O2/c{1,2,3,5,6,7,8}*.py)"
      committed: false
      status: MISSING — declared "scratch, not archived artifacts"; [D]'s numbers
              are not reproducible from the committed tree
    - path: "run manifests / EXP-* / RUN-* / EV-* / DEC-*"
      status: ABSENT — disclosed by the producers; claim tier exploratory
  metric_recomputations:
    - {script: fourier_obstruction.py, target: "O2_fourier_obstruction.md 6", result: exact_match}
    - {script: scaling.py,            target: "O2_fourier_obstruction.md 6 table + slopes", result: exact_match}
    - {script: charfilter_decay.py,   target: "O2_composition_closure.md 3.4", result: exact_match}
    - {script: quasigroup_gap.py,     target: "O2_quasigroup_gap.md 3 table", result: exact_match}
    - {script: quasigroup_gap.py,     target: "O2_quasigroup_gap.md 3 finding 1 (<=0.17)", result: MISMATCH — true max 0.322}
    - {script: quasigroup_scaling.py, target: "O2_quasigroup_scaling.md 2", result: exact_match}
    - {script: interval_decay.py,     target: "O2_additive_completion.md 4", result: exact_match}
    - {check: "Theorem A exact identity, affine d != 0", result: FAILED — conjugate missing; doc form returns eps for -d}
    - {check: "Lambda vs max|T_t|",    result: FAILED — not the same object; ratio up to 262x at p=32779}
    - {check: "L1 of additive expansion vs M", result: uniform in M for x-filters (~0.63 log p); ~p^0.39 for popcount}
    - {check: "S(0,0,0)",              result: = 1 exactly; sec 2.4's max|S| = O(p^-1/2) false as quantified}
  control_checks:
    - {control: "dlog-interval positive control, must NOT decay", result: PASS — alpha = -0.000, flat to 5 dp}
    - {control: "SHA-256 structureless null",                     result: PASS — curve filter indistinguishable}
    - {control: "Z/1024 with M|N, exact homomorphism",            result: PASS — eps = Delta = 1.00000}
    - {control: "Z/1021, M does not divide N",                    result: PASS — eps = 0.50049}
    - {control: "random-f null at matched K = 600",               result: PASS — excess_randf ~ excess_quasi}
    - {control: "Jacobson-Matthews vs isotope sampler",           result: PASS — cheap rigged sampler explicitly rejected; JM verified in code}
    - {control: "affine f with d != 0",                           result: ABSENT — Theorem A stated for all d, verified only at d = 0}
    - {control: "families I (popcount/digit sum), J (y-sign), y- and joint-coordinate members of A/B",
       result: ABSENT — claimed closed, neither proved nor measured}
  heuristic_validation_checks:
    - not_applicable: "No heuristic-validation experiment in the target-result-profile sense is claimed or owed; KN-FIND-ffe1df states this correctly."
  cost_model_checks:
    - not_applicable: "No concrete-cost table and no per-attempt x inverse-success bookkeeping is claimed. sota_delta = 0; dominated_by inapplicable, not null — Pareto honesty satisfied."
  proof_architecture_checks:
    - {check: "Theorem A bound and 'no factor M'",            result: VALID}
    - {check: "Theorem A exact identity",                     result: INVALID as stated (conjugation)}
    - {check: "Theorem C, all four implications + surjectivity necessity", result: VALID}
    - {check: "Degeneracy lemma pole-order core",             result: VALID}
    - {check: "Degeneracy lemma assembly (sec 2.4)",          result: INVALID as quantified; repair needs an unstated balance hypothesis}
    - {check: "Composition exponent arithmetic + Wagner M ~ p^{1/(j+1)}", result: VALID}
    - {check: "Composition substitution (W) into (A)",        result: INVALID as written; VALID after restating as (A')}
    - {check: "Notation reconciliation table sec 1.1",        result: correct on D vs Lambda; INCORRECT on Lambda vs T-hat}
    - {check: "Quantifier fidelity — level 1 vs levels >= 2", result: limitation stated upstream, DROPPED downstream}
  verdict: failed
  limitations:
    - "Verdict scopes the artifact set as committed, not the barrier conclusion. Theorem C, the Theorem A bound, and every reproducible measurement stand."
    - "(H1) and (H1') were not independently traced to a primary source in this session either."
    - "[D]'s and F1's computations are not in the committed tree and could not be re-run."
    - "Toy scale throughout: p <= 65539, N <= 120413. Not crypto-scale validation of anything."
    - "Both underlying derivations resolved to claude-opus-5; this validation is a fourth session on the same backend, so it is procedural independence only. Under AGENTS.md rule 12 a closure claim still needs review-breakthrough at max on a distinct resolved model."
    - "No EXP/RUN/EV/DEC records, no run manifests, no probe-verified model identifiers. Disclosed by the producers, but the artifact policy package is absent and blocks promotion."
  artifact_paths:
    - analysis/o2-sum-compatible-filters/reviews/VALIDATION.md
```

*No file outside `analysis/o2-sum-compatible-filters/reviews/` was created or
modified by this validation. Nothing was committed. No ledger record, hypothesis
status, or producer artifact was touched.*
