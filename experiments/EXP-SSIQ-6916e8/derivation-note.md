# Derivation note: the determinant of Hom(E, E') under deg is p^2/16

- Experiment: `EXP-SSIQ-6916e8` (frozen specification v1), hypothesis `H-SSIQ-a9df38`,
  approval `DEC-20260926-e05697`, task `TASK-20260926-7d20e4`, run `RUN-SSIQ-81bd08`.
- **Tier: DERIVATION** (`docs/claims-and-verification.md`, "Refutation artifacts",
  item 2). This is a written argument meant to be checked step by step by an
  independent reader. It is **not** machine-verified and is **not** labelled
  "proved". It is pending independent review (validator with a blind
  re-derivation; see the handoff's `review_note`).
- Author: executor session, 2026-09-26. This note records an argument, not
  an observation. The computation in `RUN-SSIQ-81bd08` tests the
  normalisation inputs (Sections 2 to 4) at 22 primes. It does not test the
  Deuring interface (Section 5).

## 0. Setting and conventions

- `p` is prime. `B = B_{p,inf}` is the quaternion algebra over Q ramified
  exactly at `{p, inf}`. `Nrd` is the reduced norm and `Trd` the reduced
  trace. `x -> xbar` is the standard involution, with `x xbar = Nrd(x)` and
  `x + xbar = Trd(x)`.
- Associated bilinear form: `<x, y> = (Nrd(x+y) - Nrd(x) - Nrd(y)) / 2 = Trd(x ybar) / 2`.
  This polarisation identity follows from
  `Nrd(x+y) = (x+y)(xbar+ybar) = Nrd x + Nrd y + (x ybar + y xbar)` and
  `y xbar = conj(x ybar)`, so `x ybar + y xbar = Trd(x ybar)`.
- **Gram convention** (frozen, spec `conventions.gram_matrix`): for a
  quadratic form `q` on a Z-basis `e_1..e_n`, `A_ii = q(e_i)` and
  `A_ij = (q(e_i+e_j) - q(e_i) - q(e_j))/2`, so `q(x) = x^T A x`. `det(L, q)`
  means `det A`, an exact rational. It does not depend on the choice of
  Z-basis, because a change of basis `U` in `GL_n(Z)` gives
  `U^T A U`, and `det U = ±1`.
- The trace-form matrix is `T_ij = Trd(e_i conj(e_j))`. By the polarisation
  identity `T_ij = 2 <e_i, e_j> = 2 A_ij` for `i != j`, and
  `T_ii = Trd(e_i ebar_i) = 2 Nrd(e_i) = 2 A_ii`. **So `T = 2A`, and in rank 4
  `det T = 2^4 det A = 16 det A`.** Control C-TRD tests exactly this.
- For a lattice `I` in `B`, `n(I)` is the positive generator of the Z-module
  spanned by `{Nrd(x) : x in I}`. On a Z-basis this is the gcd of the
  `A_ii` and `2A_ij`: `Nrd(sum x_i e_i) = sum x_i^2 A_ii + sum_{i<j} x_i x_j (2A_ij)`,
  and every `A_ii` and `2A_ij` is itself a difference of norm values. The
  run measures `n(I)` exactly this way (spec `conventions.ideal_norm`).
- For full-rank lattices `L ⊆ M`, `[M : L]` is the group index. It equals
  `|det H|` when `H` expresses a basis of `L` in a basis of `M`.
- `R(L, q) = det(L, q) · 16 / p^2`.

## 1. Lemma C (correctness of sublattice scaling)

**Claim.** If `L ⊆ M` are full-rank Z-lattices of rank `n` with a quadratic
form `q`, then `det(L, q) = [M : L]^2 · det(M, q)`.

**Proof.** Let the columns of a matrix `X` be a Z-basis of `M`, and let
`X H` (with `H` in `M_n(Z)`) be a Z-basis of `L`. The Gram matrix of `L` is
`H^T A_M H`, so `det A_L = (det H)^2 det A_M`. The index `[M : L]` is
`|det H|`, by the Smith normal form: `Z^n / H Z^n` has order `|det H|`.
∎

This is proof obligation **correctness**. It is exact and needs no
arithmetic input. Arm A6 tests it on 484 random sublattices, with the index
measured as `|det H|`.

## 2. Lemma B (baseline): det(O, Nrd) = p^2 / 16 for every maximal order O of B_{p,inf}

**Input (recalled, not re-proved here).** A maximal order `O` of `B_{p,inf}`
has discriminant `disc(O) = |det(Trd(e_i e_j))| = p^2`. Equivalently, its
reduced discriminant is `p`, the product of the finite ramified primes.
- Provenance: recalled standard fact (Voight, *Quaternion Algebras*;
  H-SSIQ-a9df38 `structural_ingredients` cites "Ch. 16
  norms/discriminants" as recalled, not opened in this program).
- It is corroborated, not proved, by arms A1 (PARI's independently computed
  maximal order), A2 (hand-written orders) and A5 (right orders) of the run.

**Step 1 (trace form with or without conjugation).** On `O`, the matrices
`(Trd(e_i e_j))` and `(Trd(e_i conj(e_j)))` differ by the Z-linear map
`y -> ybar`, which maps `O` to itself because `ybar = Trd(y) - y` and
`Trd(y)` is in Z for `y` in an order. This map is an involution, so its
determinant is ±1. So `|det T| = disc(O) = p^2`. The form `Nrd` is positive
definite on `B` because `B` is definite (ramified at inf). So `T = 2A` is
positive definite and `det T = +p^2`.

**Step 2.** From Section 0, `det T = 16 det(O, Nrd)`. So

    det(O, Nrd) = p^2 / 16,   i.e.   R(O, Nrd) = 1.            (B)

**Hand checks.**
- `p = 2`, Hurwitz order `Z<1, i, j, w = (1+i+j+k)/2>` in `(-1,-1)`:
  - `A = [[1,0,0,1/2],[0,1,0,1/2],[0,0,1,1/2],[1/2,1/2,1/2,1]]`.
  - `det A = 1 - 3/4 = 1/4 = 2^2/16`.
- `p = 3 mod 4`, `Z<1, i, (1+j)/2, (i+k)/2>` in `(-1,-p)`:
  - The Gram matrix splits into the two orthogonal blocks
    `{1, (1+j)/2}` and `{i, (i+k)/2}`, each equal to
    `[[1, 1/2], [1/2, (1+p)/4]]`.
  - Each block has determinant `p/4`, so `det A = (p/4)^2 = p^2/16`.

This is proof obligation **baseline**. Lever L1 records that the rank-4
object `(P, Nrd/p)` gives exponent 1/2. The index-1 case below reproduces
that value: `log_p(p^2/16)/4 -> 1/2`.

## 3. Lemma S (size): [O : I] = n(I)^2 and det(I, Nrd/n(I)) = p^2/16

Let `O` be maximal and `I ⊆ O` a full-rank left `O`-ideal (`O I ⊆ I`). Then
`O_L(I) ⊇ O`, so `O_L(I) = O` by maximality.

**Input (recalled).** A lattice whose left order is a maximal order of a
quaternion algebra over Q is locally principal: `I_l = O_l α_l` at every
prime `l`. Its right order `O_R(I)` is again maximal. Provenance: recalled
(Voight, as cited in H-SSIQ-a9df38; maximal orders are hereditary, and
lattices over them are invertible and locally principal).

**Step 1 (local index).** At a prime `l`:
- `[O_l : O_l α_l] = |det(ρ_α)|_l^{-1}`, where `ρ_α : y -> y α_l` is right
  multiplication on the 4-dimensional `Q_l`-algebra `B_l`.
- The (left or right) regular representation of a quaternion algebra
  satisfies `det(ρ_α) = Nrd(α)^2`. Over a splitting field,
  `B = M_2`, right multiplication by `α` acts on the two rows independently,
  so it is `α^T ⊕ α^T` and its determinant is `(det α)^2`.
- So `[O_l : I_l] = l^{2 v_l(Nrd α_l)}`.

**Step 2 (local norm).** `n(I_l) = Nrd(α_l) · n(O_l) = Nrd(α_l) Z_l`,
because `1` is in `O_l`, so `gcd Nrd(O_l) = 1`, and `Nrd` is multiplicative.

**Step 3 (global).** Index and norm are both products of their local
values. So

    [O : I] = prod_l l^{2 v_l(n(I))} = n(I)^2.                 (S1)

**Step 4 (determinant).** By Lemma C and (B):

    det(I, Nrd) = [O:I]^2 · det(O, Nrd) = n(I)^4 · p^2/16.

The form `Nrd/n(I)` scales the rank-4 Gram matrix by `1/n(I)` and hence its
determinant by `n(I)^{-4}`:

    det(I, Nrd/n(I)) = p^2/16,   i.e.   R = 1.                  (S2)

This holds for every such `I`, and so for every right order `O_R(I)` too.
By Lemma B, (B) applies to `O_R(I)` directly, since it is maximal.

**The two-sided ideal P.** Take `P = {x in O : p | Nrd(x)}`, the unique
two-sided ideal of reduced norm `p` (recalled: `P_p` is the maximal ideal of
the local maximal order, and `P_l = O_l` for `l != p`). Then `n(P) = p`,
`[O : P] = p^2`, and:

    det(P, Nrd/p) = p^2/16.                                     (S3)

**Controls that must fail (exact values implied by the above).**
- C-NOSCALE: `det(I, Nrd) / det(I, Nrd/n(I)) = n(I)^4`, so `R = n(I)^4`,
  which is not 1 whenever `n(I) > 1`.
- C-TRD: `det T / det A = 16` and `R(T) = 16`.
- C-NONMAX: `Z + 2O` has index 8 in `O`. It contains `2O`, which has index
  16, and `(Z + 2O)/2O` is the image of `Z·1`, of order 2. So
  `det(Z+2O, Nrd) = 64 det(O, Nrd)` and `R = 64`. Its trace-form
  determinant is `64 p^2`, not `p^2`, so it is flagged non-maximal.

This is proof obligation **size**. Arms A3 and A4 test `[O:I] = n(I)^2`,
with both sides measured independently (M-INDEX, 462 ideals), and test (S2)
and (S3) (M-R).

**Method note on the construction of P used in the run.** The executor
built `P` as `pO + (lift of the kernel of the matrix (Trd(e_i e_j)) mod p)`.

- Rationale (recalled): the inverse different of a maximal order of
  `B_{p,inf}` is `P^{-1}`, so `O^# = P^{-1} = p^{-1} P` and
  `P = p O^# = {x in O : Trd(x y) in pZ for all y in O}`.
- This rationale is not relied on. The run checks the result directly under
  C-ALG (e): `O P ⊆ P`, `P O ⊆ P`, and `p | Nrd` on a basis.
- It also records the diagnostic `[O : P] = p^2`. Together with
  `pO ⊆ P ⊆ {x : p | Nrd x}`, that identifies the lattice as `P`.

## 4. Theorem (rank-4 closure, dimension one), given the interface of Section 5

For every prime `p` and all supersingular `E, E'`, let `Hom(E, E')` be the
full homomorphism module over `\bar F_p`. It is a rank-4 Z-lattice with the
positive definite quadratic form `deg`. (All supersingular j-invariants lie
in `F_{p^2}`. Over a model on which all homomorphisms are defined, this is
the `F_{p^2}`-module of the hypothesis statement.) Under the interface (D)
of Section 5:

1. `det(Hom(E, E'), deg) = p^2/16`, by (D) and (S2).
2. For every full-rank sublattice `L ⊆ Hom(E, E')` of index `m`:
   `det(L, deg) = m^2 p^2/16 >= p^2/16`, by Lemma C.
3. Hence `log_p det(L) / 4 = 1/2 + log_p(m)/2 - log_p(16)/4 >= 1/2 - log_p(16)/4`.
   This is the **exponent floor**. The constant is stated: `log_p(16)/4 = log_p 2`.
4. **Certificates.** A Hermite/Minkowski-type certificate built from
   `(rank, det)` alone has the form `min q <= c_4 det(L)^{1/4}`. For the
   Hermite constant, `c_4 = γ_4 = 2^{1/2}` in the Gram convention above.
   By item 2 its bound is at least `c_4 (p^2/16)^{1/4} = (c_4/2) p^{1/2}`.
   So no such certificate built from any rank-4 full-rank sublattice of a
   single `Hom(E, E')` certifies an isogeny `E -> E'` of degree below
   `(c_4/2) p^{1/2}`.
5. **Admissibility window of GOAL-SSIQ-001** (`log_p(det)/rank <= 1/4`,
   i.e. `det <= p` at rank 4). This requires `m^2 p^2/16 <= p`, i.e.
   `p m^2 <= 16`.
   - Solutions: `p in {2, 3, 5, 7, 11, 13}` with `m = 1`, and `p in {2, 3}`
     with `m = 2`. There are no others.
   - So for every `p >= 17`, the "rank 4 with det <~ p" option is **empty**
     inside a single `Hom(E, E')` under `deg` in dimension one.
   - Asymptotically the exponent is `1/2 > 1/4`.

This says nothing about the actual minimum of any particular `Hom(E, E')`,
which can be far below `p^{1/2}`. Minkowski/Hermite bounds are upper bounds
on minima, never floors (H-SSIQ-a9df38 `assumptions`).

## 5. Interface obligation (Deuring), with provenance: CITED, NOT TESTED

**(D)** Let `O ≅ End(E)` and let `I` be a left `O`-ideal connecting `O` to
`O_R(I) ≅ End(E')`. Then `Hom(E, E')` with `deg` is isometric to
`(I, Nrd/n(I))`.

- **Internal citation, case `E' = E^{(p)}`, `I = P`.**
  `inputs/P13-WESOLOWSKI-2026/paper_fulltext.md` line 244 (frozen source,
  read by this executor on 2026-09-26) states that "the lattice of isogenies
  Hom(E, E^{(p)}) (with the quadratic form deg) is isometric to the unique
  two-sided ideal P of reduced norm p in O (with the quadratic form Nrd/p)."
  Provenance: internal.
- **General pair.** The general correspondence
  `Hom(E, E') ~ (I, Nrd/n(I))` is recalled (Kohel 1996 thesis; Voight,
  *Quaternion Algebras*, Deuring chapter, cited in H-SSIQ-a9df38 as Ch. 42).
  It was **not opened in this program**. Provenance: recalled.
  `verified_by: null`.
- **Convention independence.** References differ on whether `Hom(E, E')`
  corresponds to `I`, `Ibar` or `I^{-1}`, with the matching rescaling.
  Conjugation `x -> xbar` is an `Nrd`-isometry and `n(Ibar) = n(I)`. For
  `I^{-1} = Ibar / n(I)`, the form `Nrd · n(I)` on `I^{-1}` is isometric to
  `Nrd/n(I)` on `Ibar`. So the determinant `p^2/16` is the same under every
  convention.
- **What the run does not do.** `RUN-SSIQ-81bd08` constructs no curve and no
  isogeny (handoff C-4). It tests the quaternion-side normalisation only
  (Sections 1 to 3). The interface is the one input of the Theorem that the
  computation does not touch. This is proof obligation **interface**.

## 6. Nearby objects (control C-NEAR): the lemma must NOT apply at rank 3

Let `O^0 = {x in O : Trd x = 0}` and `P^0 = {x in P : Trd x = 0}`. Both are
rank 3.

**Fact 1: `Trd(O) = Z`.**
- `Trd(O)` is an ideal of Z containing `Trd(1) = 2`.
- If `Trd(O) ⊆ 2Z`, then `1/2` is in the dual `O^# = {x : Trd(xO) ⊆ Z}`,
  but not in `O` (`Nrd(1/2) = 1/4`).
- **p odd.** `[O^# : O] = disc(O) = p^2` is odd, so `O^#/O` has no element
  of order 2. This contradicts `1/2` being in `O^# \ O`, since
  `2 · (1/2) = 1` is in `O`.
- **p = 2.** Every maximal order is conjugate to the Hurwitz order (class
  number 1, recalled), and that order contains `w` with `Trd w = 1`. `Trd` is
  conjugation-invariant.
- So `Trd(O) = Z`.

**Fact 2: `Trd(P) = pZ`.**
- Image modules localise, so it suffices to compute `Trd(P_l)` for each `l`.
- For `l != p`: `P_l = O_l` and `Trd(O_l) = Z_l` by Fact 1.
- At `p` (recalled local structure): `O_p = S + S π`, where `S` is the
  unramified quadratic extension ring of `Z_p`, `π^2 = p` up to a unit,
  `π s = σ(s) π`, and `P_p = π O_p = π S + p S`.
- Elements of `S π` have reduced trace 0. `Trd(p s) = p Tr_{S/Z_p}(s)`, and
  `Tr_{S/Z_p}` is onto `Z_p` because `S` is unramified.
- So `Trd(P_p) = p Z_p`, and hence `Trd(P) = pZ`.

**Step 1: orthogonality.** For trace-zero `x`,
`<1, x> = Trd(xbar)/2 = Trd(x)/2 = 0`. So `Z·1 ⊕ O^0` and `pZ·1 ⊕ P^0` are
orthogonal sums.

**Step 2: index 2.**
- `Z + O^0 = {x in O : Trd x in 2Z}`. If `Trd x = 2t`, then `x - t` is in
  `O^0`. The converse is clear.
- This is the kernel of `O -> Z/2`, `x -> Trd x mod 2`, which is onto by
  Fact 1. So `[O : Z + O^0] = 2`.
- In the same way, `pZ + P^0 = {x in P : Trd x in 2pZ}` has index 2 in `P`,
  by Fact 2. If `Trd x = 2pt`, then `x - pt` is in `P^0`, because
  `pt` is in `pZ`, which is contained in `P`.

**Step 3: determinants.**
- `det(Z·1 ⊕ O^0, Nrd) = Nrd(1) · det(O^0, Nrd)`. By Lemma C this equals
  `4 · p^2/16`. So

      det(O^0, Nrd) = p^2 / 4.

- `det(pZ·1 ⊕ P^0, Nrd) = Nrd(p) · det(P^0, Nrd) = p^2 det(P^0, Nrd)`. By
  Lemma C this equals `4 · det(P, Nrd) = 4 · p^4 · p^2/16`. So
  `det(P^0, Nrd) = p^4/4`. Rescaling the rank-3 form by `1/p` divides by
  `p^3`:

      det(P^0, Nrd/p) = p / 4.

**Reading.**
- `log_p(p/4)/3 -> 1/3`. This reproduces lever L1's recorded rank-3
  discriminant `p/4` (exponent 1/3, frozen Theorem 1.5).
- `O^0` and `P^0` are **not full-rank** sublattices of a rank-4 Hom-module,
  so Lemma C, and with it the floor of Section 4, does not apply to them.
- The closure therefore does not "prove too much": the rank-3 route to
  `p^{1/3}` is untouched.
- If the run returned a multiple of `p^2/16` here, the note's nearby-object
  analysis would be wrong. The frozen outcome for that case is
  INCONCLUSIVE-NEAR, which is not a falsification of the rank-4 lemma.

## 7. Scope statement (exact)

**Covered (derivation tier, conditional on the cited interface (D)):** every
full-rank (rank-4) sublattice of a **single** module `Hom(E, E')`, with the
**degree form**, for supersingular elliptic curves (**dimension g = 1**),
every prime `p`, and every pair `(E, E')`.

**Not covered, and left OPEN:**
1. **Rank <= 3 certificates**, e.g. the rank-3 trace-zero route with
   `det p/4` and exponent 1/3, and its density limits under H-WESO-9dc201.
   Section 6 shows the argument does not reach them.
2. **Other quadratic forms** on these lattices: anything other than `deg`
   (equivalently `Nrd/n(I)`), including weighted or twisted forms.
3. **Dimension g >= 2** (abelian surfaces and higher): the genuine
   higher-dimensional branch of lever N5.
4. **Several Hom-modules at once.** For an orthogonal direct sum of `k`
   modules under the sum of the `deg` forms, Lemma C and (S2) give
   `det = (p^2/16)^k` at rank `4k`, again with exponent `-> 1/2`. Glued,
   non-orthogonal or non-full-rank constructions across several targets are
   not covered.

The finite computation does not widen this scope. The universal statement
rests on this note, not on the 22-prime sample. The note is a derivation
pending independent review. A theorem-level claim still routes to a proof
assistant or a human referee.

## 8. Proof-obligation ledger (H-SSIQ-a9df38 `proof_search_map.proof_obligations`)

| obligation | statement | where discharged | inputs recalled / cited | computational check (RUN-SSIQ-81bd08) |
| --- | --- | --- | --- | --- |
| baseline | det(O, Nrd) = p^2/16 | Section 2 (Lemma B) | disc(O) = p^2 (recalled) | A1, A2, A5 (R = 1), C-TRD |
| interface | Hom(E,E') ~ (I, Nrd/n(I)) | Section 5 | line 244 (internal) for E^{(p)}; general pair recalled | **not tested** |
| size | [O:I] = n(I)^2, det(I, Nrd/n(I)) = det(O, Nrd) | Section 3 (Lemma S) | local principality, det of regular rep (recalled / derived) | A3, A4 (M-INDEX, M-R), C-NOSCALE, C-NONMAX |
| correctness | det(L) = [M:L]^2 det(M) | Section 1 (Lemma C) | none | A6 (M-SUB) |
| scope | rank 4, single Hom, deg, g = 1 only | Sections 4, 6, 7 | none | C-NEAR (rank-3 values p^2/4, p/4) |

## 9. Baseline table (M-EXP)

M-EXP is filled in after `RUN-SSIQ-81bd08` from its `raw-result.json`
(`counts.M_EXP_report_only`). Exact determinants are copied verbatim from
the run. The float columns are renderings for this table only and never
entered a pass/fail decision.

*(See the table appended below the line after the run completes.)*

---

### M-EXP baseline table (RUN-SSIQ-81bd08, appended after the run)

Source: `runs/RUN-SSIQ-81bd08/raw-result.json`, `counts.M_EXP_report_only`, generated by script from that file. The exact values are the recorded `det_python`, which equals `det_pari` in every row. The expected values are p^2/16 for (P, Nrd/p) at rank 4 and p/4 for (P^0, Nrd/p) at rank 3. The float columns show log_p(det)/rank, for this table only.

| p | tier | class | det(P, Nrd/p), rank 4 (exact) | log_p(det)/4 | det(P^0, Nrd/p), rank 3 (exact) | log_p(det)/3 |
| --- | --- | --- | --- | --- | --- | --- |
| 2 | S | 2 | 1/4 | -0.500000 | 1/2 | -0.333333 |
| 3 | S | 3mod4 | 9/16 | -0.130930 | 3/4 | -0.087287 |
| 5 | S | 5mod8 | 25/16 | 0.069323 | 5/4 | 0.046216 |
| 7 | S | 3mod4 | 49/16 | 0.143793 | 7/4 | 0.095862 |
| 11 | S | 3mod4 | 121/16 | 0.210935 | 11/4 | 0.140623 |
| 13 | S | 5mod8 | 169/16 | 0.229762 | 13/4 | 0.153175 |
| 17 | S | 1mod8 | 289/16 | 0.255349 | 17/4 | 0.170233 |
| 19 | S | 3mod4 | 361/16 | 0.264591 | 19/4 | 0.176394 |
| 23 | S | 3mod4 | 529/16 | 0.278935 | 23/4 | 0.185957 |
| 101 | S | 5mod8 | 10201/16 | 0.349810 | 101/4 | 0.233206 |
| 103 | S | 3mod4 | 10609/16 | 0.350445 | 103/4 | 0.233630 |
| 109 | S | 5mod8 | 11881/16 | 0.352250 | 109/4 | 0.234833 |
| 113 | S | 1mod8 | 12769/16 | 0.353376 | 113/4 | 0.235584 |
| 9223372036854775907 | M | 3mod4 | 85070591730234617692071315155187672649/16 | 0.484127 | 9223372036854775907/4 | 0.322751 |
| 9223372036854775931 | M | 3mod4 | 85070591730234618134793172924216916761/16 | 0.484127 | 9223372036854775931/4 | 0.322751 |
| 9223372036854775837 | M | 5mod8 | NOT COMPUTED (PARI alginit error; see execution-report.yaml) | - | NOT COMPUTED | - |
| 9223372036854776077 | M | 5mod8 | 85070591730234620828017807685811509929/16 | 0.484127 | 9223372036854776077/4 | 0.322751 |
| 9223372036854776257 | M | 1mod8 | 85070591730234624148431740953530930049/16 | 0.484127 | 9223372036854776257/4 | 0.322751 |
| 9223372036854776393 | M | 1mod8 | 85070591730234626657188934978030090449/16 | 0.484127 | 9223372036854776393/4 | 0.322751 |
| 57896044618658097711785492504343953926634992332820282019728792003956564820063 | L | 3mod4 | 3351951982485649274893506249551461531869841455148098344430890360930441007529386992678013613106965100498333315792682161256674324286735112967360159567323969/16 | 0.496078 | 57896044618658097711785492504343953926634992332820282019728792003956564820063/4 | 0.330719 |
| 57896044618658097711785492504343953926634992332820282019728792003956564820109 | L | 5mod8 | 3351951982485649274893506249551461531869841455148098344430890360930441007534713428782930158096449365808732959553932580551293790232550161831724163530771881/16 | 0.496078 | 57896044618658097711785492504343953926634992332820282019728792003956564820109/4 | 0.330719 |
| 57896044618658097711785492504343953926634992332820282019728792003956564821041 | L | 1mod8 | 3351951982485649274893506249551461531869841455148098344430890360930441007642631655952108852231217523836830089673180206259670795917324630127099200356323681/16 | 0.496078 | 57896044618658097711785492504343953926634992332820282019728792003956564821041/4 | 0.330719 |

Reading, restricted to arithmetic: the rank-4 column is exactly 1/2 - log_p(16)/4 (index 1), which tends to 1/2. The rank-3 column is exactly 1/3 - log_p(4)/3, which tends to 1/3. This is what Sections 4 and 6 state. At p = 2, 3 the log_p constants dominate. These are finite-p renderings, not evidence for the universal statement.
