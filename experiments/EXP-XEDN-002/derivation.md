# EXP-XEDN-002 — Derivation

Arm A (exact census) and arm D (scoped codimension lemma) for the frozen
EXP-XEDN-001 function-field family.

- Experiment contract: `experiments/EXP-XEDN-002/specification.yaml` (frozen, approved).
- Task: TASK-20260724-229. Executor role: observations and derivations only.
- Every numbered claim below is labelled **(E)** exact/proved here, **(V)** verified
  by enumeration in a recorded run, **(P)** parameter count / heuristic, or
  **(L)** literature input used without re-derivation.
- Runs cited: `runs/RUN-XEDN-002-A2` (arm A + arm D tables; supersedes the
  metadata-defective `RUN-XEDN-002-A`), `runs/RUN-XEDN-002-B` (exhaustive
  frozen-predicate enumeration), `runs/RUN-XEDN-002-C` (independent full-space
  section fibering), `runs/RUN-XEDN-002-CTRL` (controls).

Throughout, `p` is an odd prime, `F_p[t]` the polynomial ring, and

- surface family: `S_b : y^2 = x^3 + b(t)` with `a(t) = 0` and `deg b = 6` exactly
  (i.e. `b_6 != 0`);
- slot: a monic quadratic `x(t) = t^2 + x_1 t + x_0`;
- section of the given shape: `y in F_p[t]`, `deg y <= 3`, with `y^2 = x^3 + b`;
- predicate: `is_square_poly` of `experiments/EXP-XEDN-001/xedni_sections.py`
  (sha256 `76f0cfe2f32362ff1110fc7c7b42db40d293099ae7718927c46223a42450b34f`),
  loaded verbatim by file path, never edited.

---

## Part 0 — What the frozen predicate actually tests

The census must count what the predicate counts, not what the mathematics would
count. The two differ, and both are reported.

### Lemma 0.1 (E). Squarefree criterion via the derivative

For `g in F_p[t]` nonzero, `g` is squarefree **iff** `gcd(g, g') = 1`.

*Proof.* If `q^2 | g` for an irreducible `q`, write `g = q^2 h`; then
`g' = 2 q q' h + q^2 h'` is divisible by `q`, so `q | gcd(g, g')`.
Conversely let `q` be irreducible with `q | g` and `q | g'`. Write `g = q h`, so
`g' = q' h + q h'` and `q | q' h`. Now `deg q' < deg q`, so `q | q'` forces
`q' = 0`, i.e. `q in F_p[t^p]`; but `F_p` is perfect, so
`q(t) = sum c_i t^{pi} = (sum c_i^{1/p} t^i)^p` would be a `p`-th power,
contradicting irreducibility. Hence `q | h`, so `q^2 | g`. ∎

### Lemma 0.2 (E, V). Exact semantics of the frozen predicate

For odd `p` and `f in F_p[t]`: `is_square_poly(f, p)` returns a non-`None` value
**iff** `f = y^2` for some **nonzero squarefree** `y in F_p[t]`.

*Proof.* Write `lc` for leading coefficient. The code (i) rejects `f` of odd
degree, (ii) rejects unless `lc(f)^((p-1)/2) = 1`, (iii) sets
`h = gcd(f, f')` normalised monic, (iv) rejects unless `2 deg h = deg f`,
(v) sets `c = lc(f) * lc(h)^{-1} = lc(f)` and returns `h` iff `f = c h^2`.

(⇐) Let `f = y^2`, `y != 0` squarefree, `deg y = d`, so `deg f = 2d` is even and
`lc(f) = lc(y)^2` is a nonzero square, passing (i) and (ii). Put
`y~ = y / lc(y)` (monic squarefree). Then `f = lc(y)^2 y~^2` and
`f' = 2 lc(y)^2 y~ y~'`, so `gcd(f, f') = y~ * gcd(y~, 2 y~') = y~` by
Lemma 0.1 and `2` invertible. Hence `h = y~`, `deg h = d`, passing (iv), and
`c h^2 = lc(y)^2 y~^2 = f`, so the predicate returns `h`. (The degenerate case
`d = 0`: `f` is a nonzero square constant, `f' = 0`, `pgcd(f, 0)` returns the
monic normalisation `[1]`, `deg h = 0 = deg f / 2`, and `c*1 = f`; accepted.)

(⇒) Suppose the predicate returns `h`. Then `f = c h^2` with `c = lc(f)` a
nonzero quadratic residue, so `f = (sqrt(c) h)^2` is a nonzero perfect square;
set `y = sqrt(c) h`, `deg y = deg h = deg f / 2`. Factor `y = u * prod q_i^{m_i}`
with `q_i` distinct irreducible, so `f = u^2 prod q_i^{2 m_i}`. For each `i`,
`q_i^{2 m_i - 1}` divides both `f` and `f'`, hence
`deg h = deg gcd(f, f') >= sum (2 m_i - 1) deg q_i = 2 deg y - sum deg q_i`.
With `deg h = deg y` this gives `sum (m_i - 1) deg q_i <= 0`, so every
`m_i = 1`: `y` is squarefree. ∎

Two consequences, both quantified in Part 1:

- **(E) No false positives.** The re-squaring test makes a non-square
  impossible to accept. (Already stated in `EXP-XEDN-001/contract.md`.)
- **(E) False negatives exist.** A perfect square whose square root is *not*
  squarefree is rejected. The smallest example is `f = 4 t^6 = (2 t^3)^2` at
  `p = 5`, which `RUN-XEDN-002-B` records as an observed missed square.
  `EXP-XEDN-001/contract.md` already logs this class as a harness limitation.
- **(E) `y = 0` is excluded.** For `f = 0` the leading coefficient is `0`, so
  the residue test rejects it. The `y = 0` two-torsion section is therefore
  never counted.

**(V)** Lemma 0.2 was checked against two algorithmically independent
implementations — top-down square-root extraction plus a discriminant
squarefree test, and `sympy` factorisation over `GF(p)` — on the **complete**
reachable set of `f` values at `p = 5` (62,500 values) and `p = 7` (705,894
values), and on 200,000 random sextics at `p = 101`: zero disagreements
(`RUN-XEDN-002-CTRL`, control 1).

---

## Part 1 — Arm A: the exact census

### 1.1 (E) The slot space

`b` has 7 coefficients with `b_6 != 0`, and `x` has 2 free coefficients, so

```
N_slots(p) = (p-1) * p^6 * p^2 = (p-1) * p^8 .
```

### 1.2 (E, V) Step 1 — reindexing the slot by the sextic

**Lemma 1.1.** Fix a monic quadratic `x`. Then `b |-> f := x^3 + b` is a
bijection from `{b : deg b = 6}` onto `F := {f : deg f <= 6, [t^6] f != 1}`.

*Proof.* `x^3` is monic of degree 6. In coefficient coordinates the map is the
translation `b |-> b + x^3` on `F_p^7`, hence bijective, and
`[t^6] f = 1 + b_6`, so `b_6 != 0` corresponds exactly to `[t^6] f != 1`. ∎

Because `F` does not depend on `x`, the number of hit slots is the same for
every `x`:

```
N_hit(p) = p^2 * Q(p),      Q(p) := #{ f in F : f = y^2, y != 0 squarefree } .
```

**(V)** The set equality of Lemma 1.1 was verified by direct enumeration for two
different `x` at `p = 5, 7` (`RUN-XEDN-002-A2`, `step1_bijection_holds`), and the
`x`-independence of the hit count was verified for every one of the 25 + 49
values of `x` at `p = 5, 7` and for 12 (resp. 6) values at `p = 11` (resp. 13)
(`RUN-XEDN-002-B`, `x_invariance_holds`).

### 1.3 (E, V) Step 2 — the squarefree census

**Lemma 1.2.** The number of **monic** squarefree polynomials of degree exactly
`n` over `F_p` is `1` for `n = 0`, `p` for `n = 1`, and `p^n - p^{n-1}` for
`n >= 2`.

*Proof.* Every monic `g` factors uniquely as `g = a^2 v` with `a` monic and `v`
monic squarefree. With `Z(u) = sum_n p^n u^n = 1/(1-pu)` counting all monic
polynomials by degree and `S(u)` counting monic squarefree ones, unique
factorisation gives `Z(u) = Z(u^2) S(u)`, so

```
S(u) = (1 - p u^2) / (1 - p u) = 1 + p u + sum_{n>=2} (p^n - p^{n-1}) u^n . ∎
```

Squarefreeness is invariant under multiplication by a nonzero scalar, so the
number of **all** squarefree polynomials of degree exactly `n` is
`(p-1)` times the monic count.

**(V)** Brute-force counts with the independent discriminant test at `p = 5`
give `{1, 5, 20, 100}` and at `p = 7` give `{1, 7, 42, 294}` for `n = 0..3`,
matching Lemma 1.2 (`RUN-XEDN-002-A2`, `step2_monic_squarefree`).

### 1.4 (E) Assembling `Q(p)`

Let `f = y^2` with `y != 0` squarefree. Then `deg f = 2 deg y <= 6`, so
`deg y in {0,1,2,3}`. The map `y |-> y^2` is exactly 2-to-1 on nonzero `y`
(`y` and `-y`, distinct because `p` is odd), and `F_p[t]` is a domain so a
nonzero square has exactly these two square roots. The membership condition
`[t^6] f != 1` reads:

- `deg y <= 2`: `[t^6] f = 0 != 1`, no condition;
- `deg y = 3`: `[t^6] f = lc(y)^2 != 1`, i.e. `lc(y) not in {1, -1}`
  (`p - 3` admissible leading coefficients).

Hence, with `M_n := p^n - p^{n-1}` for `n >= 2`,

```
2 Q(p) = (p-1)*1  +  (p-1)*p  +  (p-1)*M_2  +  (p-3)*M_3
       = (p^2 - 1) + (p^3 - 2p^2 + p) + (p^4 - 4p^3 + 3p^2)
       = p^4 - 3p^3 + 2p^2 + p - 1 ,
```

which is even for odd `p`, so

```
Q(p) = (p^4 - 3p^3 + 2p^2 + p - 1) / 2 .
```

### 1.5 (E) The closed form

```
N_slots(p) = (p-1) p^8
N_hit(p)   = p^2 (p^4 - 3p^3 + 2p^2 + p - 1) / 2
P_lift(p)  = (p^4 - 3p^3 + 2p^2 + p - 1) / (2 p^6 (p-1))
```

and the exact algebraic identity (verify by multiplying out
`(1 - 2u + u^3)(1 - u) = 1 - 3u + 2u^2 + u^3 - u^4` with `u = 1/p`)

```
2 p^3 * P_lift(p) = 1 - 2/p + 1/p^3          (exact, not an expansion)
```

so `P_lift(p) = (1 - 2/p + p^{-3}) / (2 p^3) < 1/(2 p^3)` for every `p >= 3`.

Therefore:

- `P_lift(p) = Theta(p^{-3})` with constant exactly `1/2`;
- the limiting exponent is `alpha = 3` **exactly**;
- the finite-size exponent between two sizes is
  `alpha_eff(p1,p2) = 3 - [log(1 - 2/p2 + p2^{-3}) - log(1 - 2/p1 + p1^{-3})] / log(p2/p1)`,
  which is strictly less than `3` and increases to `3`.

**(V)** `RUN-XEDN-002-B` reproduced `N_hit` exactly by exhaustive
frozen-predicate enumeration of the **full** slot space at `p = 5` (1,562,500
slots) and `p = 7` (34,588,806 slots), and reproduced `Q(p)` exactly on every
enumerated complete `b`-marginal at `p = 11, 13`. `RUN-XEDN-002-C` reproduced
`N_hit` exactly at `p = 5, 7, 11, 13` by the independent full-space section
fibering.

### 1.6 (E) Variants that isolate predicate semantics from mathematics

Same derivation with the squarefree requirement dropped (all nonzero squares):

```
2 Q_sq(p) = (p-1)(1 + p + p^2) + (p-3) p^3 = p^4 - 2p^3 - 1
Q_sq(p) - Q(p) = (p^3 - 2p^2 - p)/2 = p(p^2 - 2p - 1)/2
```

so the frozen predicate misses exactly `p^2 * p(p^2-2p-1)/2` slots
(875 at `p = 5`, verified in `RUN-XEDN-002-B`), a relative shortfall of
`O(1/p)` in the constant and **no change to the exponent**.

Including the excluded `y = 0` section adds exactly the slots with
`f = x^3 + b = 0`, i.e. `b = -x^3` — one `b` per `x`, and `deg(-x^3) = 6` with
leading coefficient `-1 != 0`, so all `p^2` of them lie inside the family:

```
N_hit^{+0}(p) = p^2 (Q(p) + 1),    relative effect 1/Q(p) = O(p^{-4}) .
```

**(V)** Both variants verified in `RUN-XEDN-002-B` (counts) and
`RUN-XEDN-002-CTRL` (control 5: all `p^2` such slots exist, all are rejected by
the frozen predicate).

### 1.7 (E, V) The non-monic (free-`x`) variant

This is **outside** the frozen slot definition and does **not** change the gate
quantity; it is derived because arm D needs it. Let `x` range over all
polynomials of degree `<= 2` (`p^3` values) and keep `deg b = 6` exactly, i.e.
`[t^6](y^2 - x^3) = y_3^2 - x_2^3 != 0`. Write

```
SF(c) := #{ y != 0 squarefree, deg y <= 3, y_3 = c }
SF(0) = (p-1)(1 + p + M_2) = (p-1)(p^2 + 1),      SF(c) = M_3 = p^3 - p^2  (c != 0)
```

Summing over `x_2` and the admissible `y_3` (for `x_2 = 0` the condition is
`y_3 != 0`; for `x_2 != 0` a square `x_2^3` excludes exactly the two roots
`±sqrt(x_2^3)`, and `x_2^3` is a residue iff `x_2` is), the excluded and
recovered terms cancel and the total is `(p-1) * [SF(0) + (p-1) M_3]`. With the
`p^2` free choices of `x_1, x_0` and the 2-to-1 `±y` count:

```
N_hit^free(p)   = p^2 (p-1)^2 (p^3 + 1) / 2
N_slots^free(p) = (p-1) p^9
P_slot^free(p)  = (p-1)(p^3 + 1) / (2 p^7)      = (1 - 1/p)(1 + p^{-3}) / (2p^3)
mean sections per surface (free x) = (p-1)(p^3+1) / (2 p^4)  ->  1/2
```

**(V)** `RUN-XEDN-002-C` reproduced `N_hit^free` exactly at `p = 5, 7, 11, 13`
(25,200 / 303,408 / 8,058,600 / 26,745,264).

So the **per-slot** rate is `Theta(p^{-3})` in both conventions — the slot count
and the hit count both scale by `p` when `x` is unnormalised — while the
**per-surface** expected number of sections is `Theta(p^{-1})` for monic `x` and
`Theta(1)` for free `x`. This factor-of-`p` difference is the subject of arm D.

---

## Part 2 — Arm D: scoped codimension lemma

### 2.1 Setting and explicit hypotheses

**Hypotheses (H1)–(H6).**

- **H1** `p` is an odd prime, `p > 3` (needed for the Weierstrass form used, for
  the `±y` 2-to-1 count, and for the cubic/quadratic discriminants used as the
  independent squarefree test).
- **H2** The surface is given by the polynomial Weierstrass model
  `y^2 = x^3 + a(t) x + b(t)` over `F_p(t)` with `deg a <= A` (or `a = 0`
  identically, written `a` absent) and `deg b <= B`. Requiring `deg b = B`
  exactly changes constants, not exponents (Part 1 does the exact version).
- **H3** The section shape is `x` of degree `<= d` with `delta` free
  coefficients (`delta = d` for monic of degree exactly `d`, `delta = d + 1`
  for unrestricted) and `y` of degree `<= e` (`e + 1` coefficients).
  Sections are **integral**: `x, y` are polynomials, not rational functions.
- **H4** "Slot" means a pair (surface, `x`); `P_slot` is the probability that a
  uniformly random slot admits a section of the shape. "Per surface" means the
  probability that a uniformly random surface admits at least one such slot.
  These differ by up to a factor `p^delta`; the H-XEDN-001 gate is stated on
  `P_slot`.
- **H5** The counted objects are **distinct** sections of the fixed degree
  shape, not independent points of the Mordell–Weil group.
- **H6** All statements are about uniformly random members of the stated
  coefficient box. Nothing is claimed about structured subfamilies.

Let `M_0 := max(3d, A + d, B)` (drop `A + d` if `a` is absent) and
`M := max(3d, 2e, A + d, B)`.

### 2.2 Lemma D1 (E) — rigorous upper bound

Let `E := min(e, floor(M_0 / 2))`. Then for every `p` satisfying H1,

```
P_slot <= p^{E - B}        and        P_surf <= p^{delta + E - B} .
```

*Proof.* Fix `a` and `x`. If a slot `(a, b, x)` is a hit with witness `y` of
degree `k`, then `b = y^2 - x^3 - a x` and
`deg(y^2) = 2k <= max(deg b, deg(x^3 + a x)) <= max(B, 3d, A + d) = M_0`,
so `k <= floor(M_0/2)`; with `k <= e` this gives `deg y <= E`. Hence
`y |-> b` maps the at most `p^{E+1}` admissible `y` onto all `b` that make the
slot a hit, so each `(a, x)` has at most `p^{E+1}` hit values of `b`. Summing
over the `p^{dim_a + delta}` pairs `(a, x)` and dividing by
`|Sl| = p^{dim_a + B + 1 + delta}` gives the first bound; the second follows
because a surface with a hit slot is the image of some hit. ∎

**Corollary D1a (E).** If `P_slot >= c p^{-alpha}` for all large `p` with
`alpha < 1/2`, then `E - B >= -alpha > -1/2`, and `E - B` is an integer, so
`E >= B`. Since `E <= e` and `E <= floor(M_0/2)`, this forces

```
e >= B      and      (for B >= 1)   max(3d, A + d) >= 2B .
```

*Interpretation.* `alpha < 1/2` requires the section's `y` to carry at least as
many free coefficients as `b`, **and** the `x`-degree to be large relative to
`B` (`d >= 2B/3` when `a` is absent). For the frozen configuration
(`a` absent, `B = 6`, `d = 2`, `e = 3`) Lemma D1 gives `P_slot <= p^{-3}`,
which Part 1 attains up to the exact factor `(1 - 2/p + p^{-3})/2`.

### 2.3 Lemma D2 (P) — the parameter count

**This is a parameter count, not a geometric theorem.** The incidence set is
`I = {(a, x, y) : deg(y^2 - x^3 - a x) <= B}`; the constraint is the vanishing
of the `K := max(0, M - B)` coefficients in degrees `B+1 .. M`. Counting each
vanishing coefficient as one codimension and each variety's `F_p`-points as
`p^{dimension}`, and using the exactly 2-to-1 `±y` map off `y = 0`:

```
P_slot  ~  (1/2) p^{-c_slot},   c_slot = B + K - e = max(B, 3d, 2e, A + d) - e
P_surf  ~  min(1, (1/2) p^{delta - c_slot}),   c_surf = c_slot - delta
```

The **marked** steps are: (i) the `K` leading-coefficient conditions are
independent; (ii) point counts equal `p^{dim}`; (iii) the double cover
contributes exactly `1/2`. Step (iii) is exact (Part 1). Steps (i)–(ii) are
verified exactly in three configurations:

| configuration | `c_slot` | `c_surf` | exact result | source |
|---|---|---|---|---|
| `a` absent, `B=6`, monic `d=2`, `e=3` | 3 | 1 | `P_slot = (1-2/p+p^{-3})/(2p^3)`; mean sections/surface `= (1-2/p+p^{-3})/(2p)` | Part 1, RUN-...-A2/B/C |
| `a` absent, `B=6`, free `d<=2`, `e=3` | 3 | 0 | `P_slot = (1-1/p)(1+p^{-3})/(2p^3)`; mean sections/surface `-> 1/2` | §1.7, RUN-...-C |
| `A=1`, `B=1`, free `d=0`, `e=0` | 1 | 0 | harness measured `0.4915` vs predicted `1/2` on 1296 surfaces | EXP-XEDN-001 part 1 |

### 2.4 (P) Which configurations have codimension zero

From `c_slot = max(B, 3d, 2e, A+d) - e`:

- **(P) `c_slot >= e`.** Because `max(...) >= 2e`. So any shape with a
  non-constant `y` (`e >= 1`) has `c_slot >= 1`, hence `alpha >= 1 > 1/2`.
  The minimum `c_slot = 1` is attained, e.g. `A <= 2, B <= 2, d = 0, e = 1`.
- **(P) `c_slot = 0` only for the all-constant configuration.** `c_slot = 0`
  needs `e = max(B, 3d, 2e, A+d) >= 2e`, so `e = 0`, and then
  `max(B, 3d, A) = 0`, i.e. `B = 0`, `d = 0`, `A <= 0`: constant `a, b, x, y`.
  This has no fibration content at all (no `t` appears), so it cannot host a
  specialisation relation.
- **(P) `c_surf = 0` with monic `x`:** the same all-constant configuration only
  (`max(...) = e + d` forces `2e <= e + d` and `3d <= e + d`, i.e.
  `2d <= e <= d`, so `d = e = 0`).
- **(P) `c_surf = 0` with free `x` of degree `<= d` (`delta = d+1`):**
  `max(B, 3d, 2e, A+d) = e + d + 1` forces `2d - 1 <= e <= d + 1`, hence
  `d <= 2`. The maximal-`B` solutions are

  | `d` | `e` | max `B` | max `A` |
  |---|---|---|---|
  | 0 | 0 | 1 | 1 |
  | 0 | 1 | 2 | 2 |
  | 1 | 1 | 3 | 2 |
  | 1 | 2 | 4 | 3 |
  | 2 | 3 | **6** | **4** |

  The last row is exactly the integral-section shape of a **rational elliptic
  surface** (`deg a <= 4`, `deg b <= 6`, `x` of degree `<= 2`, `y` of degree
  `<= 3`). So in the natural (unnormalised) shape a constant fraction of
  surfaces carries a section — §1.7 computes that constant exactly as `1/2` in
  the `a = 0` slice — while the frozen family's monic normalisation moves the
  same configuration to `c_surf = 1`.

The full grid of `1080` configurations (`A <= 4`, `B <= 8`, `d <= 3`, `e <= 4`,
with and without `a`) is in `runs/RUN-XEDN-002-A2/raw-result.json` under
`arm_d_parameter_grid`.

### 2.5 (P) Why prescribing the target specialisation removes the `c = 0` regime

The xedni step does not sample a random surface. It must produce a surface whose
fibre at some `t_0` **is** the target curve `E : Y^2 = X^3 + A_0 X + B_0` and
`m` sections that specialise to prescribed points `P_1..P_m in E(F_p)`. Count
the conditions:

- `a(t_0) = A_0`, `b(t_0) = B_0`: 2 conditions on the surface parameters;
- `x_i(t_0) = X_i`: 1 condition per section (then `y_i(t_0) = ±Y_i` is automatic
  because `y_i(t_0)^2 = X_i^3 + A_0 X_i + B_0 = Y_i^2`; the sign is a discrete
  choice, not a dimension);
- each section imposes its polynomial identity: `M_i + 1` equations.

Parameter count for the prescribed configuration space:

```
dim  <=  [dim_a + (B+1)] + sum_i (delta_i + e_i + 1) - sum_i (M_i + 1) - (2 + m)
      =  dim_a + B - 1 - m - sum_i c_surf,i .
```

With the best possible shape (`c_surf,i = 0` for all `i`) this is
`dim <= dim_a + B - 1 - m`. A relation among the specialised sections needs
`m >= r + 1` sections, and **(L)** the Shioda–Tate bound gives `r <= 8` for a
rational elliptic surface, so `m >= 9`. Then:

- frozen family (`a` absent, `dim_a = 0`, `B = 6`): `dim <= -4`. The abundance
  that `c_surf = 0` provided for a *random* surface is gone: the prescription
  consumes more parameters than the family has.
- full rational elliptic surface (`dim_a = 5`, `B = 6`): `dim <= 1`. The count
  is **not** negative, so this parameter count does **not** exclude the
  prescribed construction — it is consistent with the classical xedni
  construction existing. **(L)** The classical route fails for a different
  reason (a bound on the size of the coefficients of any relation the lifted
  points can satisfy, KN-LIT-021), which this counting says nothing about.

So the correct scoped statement is: *prescribing the specialisation destroys the
`c_surf = 0` abundance as soon as the number of required sections exceeds the
surface's free parameters (`m > dim_a + B - 1`), which happens at `m >= 6` for
the frozen `a = 0`, `B = 6` family and at `m >= 11` for the full rational
elliptic family.* At `m = 9` on the full family the count is at the boundary,
and nothing here decides it.

### 2.6 Cases the lemma does NOT cover

1. `p = 2, 3` (H1). The Weierstrass form, the `±y` count, and the discriminant
   squarefree test all change.
2. Non-integral sections: `x = u / w^2`, `y = v / w^3` with `w` non-constant —
   i.e. sections of positive `w`-degree in the Mordell–Weil lattice. Only
   polynomial (integral) sections are counted (H3).
3. Non-minimal or non-polynomial models, other fibrations of the same surface,
   and coefficient rings other than `F_p[t]`.
4. Sections defined over an extension (`F_{p^k}(t)`), after a base change
   `t -> t^k`, or over a base curve of positive genus.
5. Section shapes outside the tabulated grid: the closed formula for `c_slot`
   is stated for all `(A, B, d, e)`, but the `c = 0` classification uses the
   grid plus the inequalities of §2.4; nothing is claimed for `x` or `y` of
   unbounded degree.
6. **Structured (non-uniform) subfamilies (H6).** On a structured subfamily the
   lift probability can be `1` by construction (`b := y^2 - x^3`). The xedni
   construction *is* such a structured choice, so Lemma D1/D2 do not close it;
   only the marked count of §2.5 speaks to it.
7. Distinct vs independent sections (H5). No Mordell–Weil rank, height pairing,
   or torsion computation was performed. `r <= 8` is a literature input.
8. The cost of *finding* a section when one exists, and the cost of the
   specialisation/descent step: not modelled.
9. Classical xedni over `Q` or number fields (KN-LIT-020, KN-LIT-021): a
   different setting; nothing here transfers to it, and nothing here is
   evidence about it.
10. Any crypto-scale statement. The closed form is evaluated at `p <= 809`;
    exhaustive verification reaches `p <= 13`. Toy scale only.
11. The two marked counting heuristics of Lemma D2 remain unproved in general;
    they are verified exactly only in the three configurations of the table in
    §2.3.

---

## Part 3 — Structural observations the census forced (E, V)

These are exact facts about the frozen family, recorded because AGENTS.md rule 8
requires unexpected observations to be recorded. They are **not** evidence for
or against H-XEDN-001; they bound how representative the frozen family is.

1. **(E)** Every member of the family has `j`-invariant `0`: for
   `y^2 = x^3 + a x + b` the fibre `j` is `1728 * 4a^3 / (4a^3 + 27 b^2)`, and
   `a = 0` identically. So under the standard definition (constant `j`,
   equivalently mutually isomorphic smooth fibres over the algebraic closure)
   **every** surface in the frozen family is iso-trivial, and the family is a
   family of sextic twists of the single curve `Y^2 = X^3 + 1`.
2. **(E, V)** Exactly `(p-1) p` members are isomorphic over `F_p(t)` to a
   constant curve, namely `b = c (t + a_0)^6` (then `x = (t+a_0)^2 X`,
   `y = (t+a_0)^3 Y` gives `Y^2 = X^3 + c`); verified at `p = 5, 7, 11, 13`
   (20 / 42 / 110 / 156).
3. **(E, V)** For `p = 1 mod 3` the family has the automorphism `x -> zeta x`
   with `zeta^3 = 1`, which fixes `x^3` and hence maps sections to sections. In
   the **free-`x`** convention this triples the sections of a surface: at
   `p = 7, 13` the maximum sections per surface jumps to 36 and 63, and
   `P[>= 1 section]` drops (0.114 at `p = 7`, 0.121 at `p = 13`) versus
   `p = 5, 11` (0.353, 0.395) although the mean is monotone (0.403, 0.430,
   0.455, 0.462). Verified: 624 and 708 orbit checks with zero violations
   (`RUN-XEDN-002-CTRL`). The monic convention hides this, because `zeta x` is
   not monic.
4. **(E, V)** The scaling action `x(t) -> lambda^{-2} x(lambda t)`,
   `b(t) -> lambda^{-6} b(lambda t)` preserves monicity and fixes those `b`
   supported on monomial degrees `k = 6 mod |H|` for a subgroup
   `H <= F_p^*`; such surfaces carry monic section orbits of size dividing
   `|H|`. Verified: at `p = 7`, `b = t^6 + 2` has stabiliser all of `F_7^*` and
   its 6 monic hit slots form a single orbit; at `p = 13`,
   `b = 3t^6 + 10t^3 + 9` has stabiliser `{1, 3, 9}` and its 9 monic hit slots
   form three orbits of size 3. Not every section-rich surface is explained
   this way: at `p = 13`, `b = 3t^6+2t^5+2t^4+10t^3+10t^2+8t+9` also has 9 monic
   hit slots but a trivial stabiliser.

The original candidate description for this route
(`research_directions_20260718.md`, candidate B2, "Target family") excludes
"constant/iso-trivial surfaces" and "j=0/1728 (extra sections may confound
controls)". Observations 1–4 record that the frozen family is exactly the
excluded case. That is a statement about the formalisation, not about the
mathematics of lifting.
