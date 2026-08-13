# L1 method-ceiling audit — lower bounds on the minimal degree of E → E^{(p)}

**Task:** TASK-20260805-87e568 · **Goal:** GOAL-SSIQ-001 · **Batch:** BATCH-001
**Role:** executor · **Protocol:** `docs/inventor-protocol.md` §8 / `KN-TECH-080`, audit 4
(method ceiling + nearby-object control), with audits 1 and 3 also discharged below.
**Repository revision at execution:** `d8701af525b7f39a90509c715ccadf96083ad150`,
branch `claude/0.25-algorithm-breakthrough-y7jbiy`, clean working tree.
**Compute performed:** none. Reading of files and fetching of sources only; every
retrieval is logged in `source_access_log.yaml`.

---

## VERDICT

> **CLOSED** — scoped to the target `E^{(p)}` and to targets obtained from it by an
> isogeny of known small degree.
>
> **One-sentence reason:** Aubry–Oyono–Vincent Remark 4.3 proves *unconditionally* that
> the exponent `1/3` in `δ_E ≤ (p/2)^{1/3}` is asymptotically optimal — for every
> `η < 1/3` and every `C' > 0` there exist a prime `p` and a supersingular `E/F̄_p` with
> `δ_E ≥ C'p^η` — which kills L1's "holding for all supersingular E" disjunct outright;
> and a class-number counting bound derived in this task (**D1**, §6) bounds the fraction
> of curves with `δ_E ≤ p^{1/4}` by `p^{-1/8+o(1)}`, which is not `p^{-o(1)}` and so kills
> L1's second disjunct as well.

**Evidential status differs sharply between the two pillars and must not be flattened:**

| pillar | closes | basis | status |
|---|---|---|---|
| P1 | disjunct 1 ("for all supersingular E") | AOV Remark 4.3, quoted verbatim §5 | **cited primary text, unconditional** |
| P2 | disjunct 2 ("for a `p^{-o(1)}` fraction") | derivation **D1**, §6, performed in this task | **`proof_status: derivation`** — checkable argument, not a cited theorem, not machine-checked |

**Reversion condition, stated before review:** if an independent Validator finds D1
unsound, the verdict for disjunct 2 reverts to **UNRESOLVED**. Disjunct 1 stays CLOSED
regardless, because P1 does not depend on D1.

**This is an audit verdict on a lever, not a ledger state transition.** No hypothesis is
minted, no record status is changed, and nothing here asserts that `p^{1/4}` is or is not
reachable by any other route. `0.25` remains the search target, not a claim.

---

## 1. What L1 says, restated exactly

From `ledger/goals/GOAL-SSIQ-001/goal.yaml`, `exponent_budget.levers`, id `L1`,
`claim_that_would_have_to_be_true`:

> a degree bound on the minimal isogeny E → E^{(p)} (or to another
> cheaply-recognisable auxiliary target) with exponent 1/4 rather than
> 1/3, holding for all supersingular E or for a p^{-o(1)} fraction.

Three things to notice before arguing:

1. It is a **disjunction** over strength — "for all E" **or** "for a `p^{-o(1)}` fraction".
   Closing L1 requires closing both. The second is the weaker and is the one the
   algorithm actually needs (F4 shows re-randomisation buys a `p^{-o(1)}` factor for free),
   so it is the **load-bearing** disjunct.
2. It carries its own nearby-object clause — "*or to another cheaply-recognisable
   auxiliary target*". The nearby-object control (§7) is therefore not decoration; it is
   part of the lever's own statement.
3. `named_obstruction_to_audit_first` names "Minkowski-type lower bounds on the minimum
   of the rank-4 quaternion lattice underlying `Hom(E, E^{(p)})` with the form `Nrd/p`".
   §3 records that this obstruction, **as named**, is a category error, and §4 records
   what the correct object turns out to be. The named obstruction was nevertheless a good
   pointer: it named the right lattice family, one rank off.

---

## 2. The lattice, stated before anything is argued about it

Per the task's named duty: rank, determinant/discriminant, quadratic form, and provenance
first, quoted from the source where the source states it, never a remembered lattice.

### 2.1 The rank-4 object, as the frozen source states it

`inputs/P13-WESOLOWSKI-2026/paper_fulltext.md`, **line 244** (Section 4.2), verbatim:

> To perform experiments with large p, we exploit the Deuring correspondence: instead of a
> random elliptic curve E, we generate a random maximal order O in the quaternion algebra
> B_{p,∞} ramified at p and ∞. Through the Deuring correspondence, E corresponds to a
> maximal order O. Then, the lattice of isogenies Hom(E, E^{(p)}) (with the quadratic form
> deg) is isometric to the unique two-sided ideal P of reduced norm p in O (with the
> quadratic form Nrd/p).

So the object the goal record names is:

| | value | provenance |
|---|---|---|
| lattice | `P`, the unique two-sided ideal of reduced norm `p` in a maximal order `O ⊂ B_{p,∞}` | frozen text line 244 |
| rank | 4 | `End(E)` is "a lattice of rank 4" (frozen text line 103); `P` has finite index in `O` |
| quadratic form | `Nrd/p` | frozen text line 244 |
| isometric to | `Hom(E, E^{(p)})` with the form `deg` | frozen text line 244 |

The frozen source does **not** state the determinant of this lattice. It is supplied by
the source of Theorem 1.5, next.

### 2.2 The rank-3 object, as the source of Theorem 1.5 states it

Theorem 1.5 of the frozen text (line 81) is attributed to `[4]` = Aubry, Oyono, Vincent,
*Minimal degree of an isogeny between a supersingular elliptic curve and its conjugate*,
arXiv:2607.14624v1 (16 Jul 2026). **Retrieved this session** (`source_access_log.yaml`
entries `aov_abs`, `aov_html`, `aov_pdf`; HTML body SHA-256
`eec18aefad605f879e92b1174d16f161a9d1ea6ea9fa8ce42406cac62bb4e98d`). All quotations
below are from that retrieval; LaTeX markup is as rendered by arXiv's HTML.

**Definition (AOV §1, §2.2).** `δ_E := min_{φ: E→E^{(p)}} deg(φ)`, and
`δ(p) := max_{E ss/F̄_p} δ_E`.

**The Gross lattice (AOV §2.2), verbatim:**

> Let `τ: B_{p,∞} → B_{p,∞}` be given by `τ(x) = 2x − trd(x)`. Then for `O` an order in
> `B_{p,∞}`, we write `O^T` for the image of `O` under `τ` and call `O^T` the Gross lattice
> of `O`. […] If `O` is an order in `B_{p,∞}`, `O^T` is a lattice of rank 3 contained in the
> lattice of elements of `O` of trace 0.

and, for the Hermite bound it will use:

> If `L` is any lattice of rank 3 and `D_1 ≤ D_2 ≤ D_3` are its successive minima, we have
> `det(L) ≤ D_1D_2D_3 ≤ 2det(L)`, we call the second inequality the Hermite bound
> [Mar03, Theorem 2.6.8].

**AOV Proposition 3.1**, verbatim:

> If `E` is a supersingular elliptic curve defined over `F̄_p` then:
> `δ_E = min_{Λ ⊂ O^T} det(Λ)/(4p)`
> where the minimum runs over every rank-2 sublattice of the Gross lattice `O^T`, where `O`
> is a maximal order of `B_{p,∞}` isomorphic to `End(E)`.

**AOV Proposition 4.1**, verbatim:

> For the matrix `G` as in equation (3) and the ternary quadratic form given in (5), we
> have: `Discr(Q) = det(G)^2 = 16p^4`.
> *Proof.* A tedious calculation shows that `Discr(Q) = det(G)^2`, and by [CG14, Lemma 3.1]
> we have `det(G) = 4p^2`.

**And — the cleanest statement of the object, AOV §5.1, verbatim:**

> Let `E` be a supersingular elliptic curve defined over `F̄_p` and `R` be the sublattice of
> isogenies `φ: E → E^{(p)}` such that if `φ̂: E^{(p)} → E` is the dual isogeny of `φ` and
> `F: E → E^{(p)}` is the degree-`p` Frobenius isogeny, then `φ̂ ∘ F ∈ End(E)` is of trace 0.
> Since by [AV], the sublattice of `End(E)` of inseparable elements of trace 0 has rank 3,
> and `φ ↦ φ̂ ∘ F` is a bijection between isogenies from `E` to `E^{(p)}` and inseparable
> endomorphisms of `E`, then `R` is also a lattice of rank 3. Furthermore, again by [AV],
> for `Q` as in equation (5), the degree form on `R` is equal to `Q' = Q/(4p)` and is of
> discriminant `p/4`. […] `N_1` is the least degree of an isogeny `E → E^{(p)}` […]
> Furthermore, using the Hermite bound we have `p/4 ≤ N_1N_2N_3 ≤ p/2`.

**Therefore the lattice that actually governs `δ_E` is:**

| | value | provenance |
|---|---|---|
| lattice | `R ⊂ Hom(E, E^{(p)})`, the trace-zero sublattice (`φ` such that `φ̂∘F` has `trd = 0`) | AOV §5.1 |
| rank | **3** | AOV §5.1, via `[AV]` |
| quadratic form | `Q' = Q/(4p)`, which **is** the degree form on `R` | AOV §5.1 |
| discriminant | **`p/4`** | AOV §5.1 |
| first minimum | `N_1 = δ_E` | AOV §5.1 |
| two-sided constraint | **`p/4 ≤ N_1N_2N_3 ≤ p/2`** (Hermite, both directions) | AOV §5.1 |

This is the whole audit in one line: **the object is rank 3, of discriminant `≍ p`, and
`1/3` is `1/rank`.**

### 2.3 Independent cross-check of the discriminant (derived in this task)

Recorded because the audit must not rest on a single reading of a single retrieval, and
because it ties the frozen text's rank-4 statement (§2.1) to AOV's rank-3 statement (§2.2).

Starting from the frozen text's `(P, Nrd/p)`:

- `det(O, Nrd) = D²/16 = p²/16` for `O` maximal of reduced discriminant `D = p`
  (checked by hand on the Hurwitz order, `p = 2`: that lattice is `D_4*`, `det = 1/4 = 4/16` ✓;
  and on `M_2(Z)`, `D = 1`, `Nrd = ad − bc`, `det = 1/16` ✓).
- `[O : P] = Nrd(P)² = p²`, so `det(P, Nrd) = p⁴ · p²/16 = p⁶/16`; scaling the rank-4 form
  by `1/p` divides the determinant by `p⁴`, giving `det(P, Nrd/p) = p²/16`.
- For `x ∈ P` one has `p | trd(x)`; writing `trd(x) = ps`, the form value is
  `Nrd(x)/p = p·s²/4 + Nrd(x_0)/p` with `x_0` the trace-zero part. Hence **every vector of
  form value `< p/4` has `s = 0`**, i.e. lies in the trace-zero sublattice. So the minimum
  is carried by a rank-3 sublattice whenever `δ_E < p/4`.
- Splitting off the rank-1 part `P ∩ Q·1 = pZ` (form value `p` at the generator — this is
  the Frobenius itself) leaves a rank-3 lattice of determinant `p/16` or `p/4` according to
  a projection index of 1 or 2. Taking `p/4`, Hermite in rank 3 with `γ_3 = 2^{1/3}` gives
  `min ≤ γ_3 · (p/4)^{1/3} = (2p/4)^{1/3} = (p/2)^{1/3}`.

**That reproduces Theorem 1.5's constant exactly**, and reproduces AOV §5.1's stated
discriminant `p/4` exactly, from an entirely different starting point (the frozen text's
rank-4 statement) than AOV's (the Gross lattice). Labelled as an in-task derivation, not a
citation. Its only role here is corroboration; nothing downstream depends on it.

---

## 3. The named obstruction, as named, is a category error — recorded, not silently fixed

The goal record's `named_obstruction_to_audit_first` asks whether "a Minkowski-type lower
bound on the minimum of the rank-4 quaternion lattice … forces a minimum matching exponent
1/3". Two independent defects:

1. **Direction.** Minkowski's convex-body theorem, Hermite's constant, and Cassels'
   Theorem III are all *upper* bounds on the minimum of a lattice of given determinant.
   No such theorem can force a *floor*: for any fixed determinant there are lattices with
   arbitrarily small minimum. A lattice determinant alone never lower-bounds `λ_1`. So the
   named obstruction cannot close L1 in the form in which it is named.
2. **Rank.** Applied to the rank-4 object of §2.1 (`det = p²/16`), Hermite gives
   `λ_1 ≤ γ_4 · det^{1/4} = √2 · (p²/16)^{1/4} = p^{1/2}/√2` — exponent **1/2**, strictly
   *weaker* than Theorem 1.5. The exponent `1/3` is unreachable from the rank-4 object; it
   comes from the rank-3 object of §2.2, where the arithmetic constraint `p | trd` has
   already been spent (§2.3).

**Both defects are informative rather than fatal to the audit.** Defect 2 identifies the
load-bearing structure precisely — the drop from exponent `1/2` to `1/3` is bought by the
trace-zero reduction, i.e. by the fact that the target is the *Frobenius conjugate* and not
an arbitrary curve — and that identification is what makes the nearby-object control in §7
decidable rather than a guess. Defect 1 forces the audit to look for a genuinely different
kind of statement, which §5 and §6 supply.

---

## 4. The three quantities, kept apart

Per the task's named duty. Each row states what it is, what it is not, and where it comes
from.

### (i) The proven UPPER bound, for all E — **exists**

**AOV Theorem 4.2** (= AOV Theorem 1.1 = frozen text Theorem 1.5), verbatim:

> Let `p` be a prime number and `E` be a supersingular elliptic curve defined over `F̄_p`,
> then `δ_E ≤ ∛(p/2)`.

Its proof, verbatim:

> Cassels proved in Theorem III page 33 of [Cas97] that if `f(x) = Σ f_{ij}x_ix_j` with
> `f_{ij} = f_{ji}` is a positive definite ternary quadratic form, then there is an integral
> vector `u ≠ 0` such that `f(u) ≤ ∛(2 Discr(f))` where `Discr(f) = det(f_{ij})` […]
> Cassels's result implies, together with Proposition 4.1, that the quadratic form `Q`
> represents an integer `n` such that `n ≤ ∛(32p^4) = 4p∛(p/2)`. Thus `O^T` contains a
> rank-2 sublattice of determinant `≤ 4p∛(p/2)`, and therefore by Proposition 3.1, we
> conclude that `δ_E ≤ ∛(p/2)`.

Unconditional, universal in `E` and `p`. **This is (i). It is not a floor.**

### (ii) The TYPICAL minimal degree — **exists, and is not (iii)**

- The frozen text's **Heuristic 1** (line 69) sets `u = log(p/2)/(3 log B)`, i.e. it models
  `deg(φ)` as a random integer of size `(p/2)^{1/3}`. Its own justification (line 83) is
  explicitly "*Combining these two results, Heuristic 1 only asks that the degree of the
  smallest isogeny E → E^{(p)} has the smoothness probability that one would expect for a
  random integer of its size*". A **size model**, not a bound.
- AOV's data: `δ(p)` tracks `⌊∛(p/2)⌋` closely — "*for primes `p ≤ 22,000` we have
  `⌊∛(p/2)⌋ − δ(p) ≤ 4`, and for primes `93,312 ≤ p ≤ 101,306`, we have
  `⌊∛(p/2)⌋ − δ(p) ≤ 5`*" (AOV §6.2), leading to **Conjecture 6.8**. `δ(p)` is a **maximum
  over `E`**, so even this is not a statement about the typical curve.
- AOV explicitly records that **small values occur in abundance**: "*fixing the prime
  `p = 234,959` for which `δ(p) = 48 = ⌊∛(p/2)⌋`, we find that for each `1 ≤ n ≤ 48` there is
  `E` defined over `F̄_{234959}` with `δ_E = n`*" (§6.2), and **Conjecture 6.3** asserts `δ`
  is surjective onto `Z_{>0}`.

**(ii) is a size model plus data on the extremal curve. It is not (iii), and this audit
does not use it as (iii) anywhere.**

### (iii) A LOWER bound forcing a floor — **exists in two distinct forms**

- **(iii-a) A proven floor on the extremal curve.** AOV **Remark 4.3**. Quoted and analysed
  in §5. This is the pillar P1.
- **(iii-b) The trivial floor and its exact failure set.** `δ_E ≥ 1` always, with equality
  **exactly** on the `F_p` locus: AOV §1, "*if `j(E) ∈ F_p`, there is an isogeny `E → E^{(p)}`
  of degree 1*", and §2.2, "*For all primes `p`, there exist supersingular elliptic curves
  with `j`-invariant in `F_p`; […] for those curves `δ_E = 1`.*" The `F_p` locus has size
  `≍ p^{1/2}` inside `≍ p/12` curves (frozen text is silent; Delfs–Galbraith §4 states the
  density directly — see `L4_baseline_acquisition.md` §4). **Consequence: there is no
  universal floor at any positive exponent.** Any closure of L1 must therefore be a
  statement about *how many* curves are low, not about *all* curves — which is exactly the
  shape of D1 in §6.
- **(iii-c) A proven bound on the fraction of low curves.** Derivation D1, §6. Pillar P2.

**Summary against the task's guardrail:** the literature does **not** give only (i) and
(ii). It gives (i), (ii), and (iii-a). That is why the verdict is not UNRESOLVED.

---

## 5. Pillar P1 — AOV Remark 4.3 kills L1's "for all E" disjunct

**Verbatim (AOV Remark 4.3), reproduced in full because the quantifier order is the whole
content:**

> The bound of Theorem 4.2 is best possible asymptotically: Indeed, Yang proved in
> [Yan08, Proposition 1.4] that, if there are positive constants `θ` and `C` such that every
> supersingular elliptic curve over `F̄_p` can be lifted to a CM elliptic curve over some
> number field with CM by the quadratic ring of discriminant `D` with `D ≤ Cp^θ`, then
> `θ ≥ 2/3`. But a supersingular elliptic curve `E` can be lifted to an elliptic curve
> defined over a number field with CM by the quadratic ring of discriminant `D` if and only
> if its Gross lattice represents `D` by [GL25, Proposition 3.7] and the remark immediately
> following conditions (i) and (ii) of [CCO14, 2.1.5].
>
> Hence, if `θ < 2/3`, then for any constant `C`, there exist a prime `p` and a supersingular
> elliptic curve `E` defined over `F̄_p` with `D_1 > Cp^θ`. Letting `D_i` be the `i`th
> successive minimum of the Gross lattice of `E` and `t_{12} = ½trd(β_1 β̄_2)` as before, by
> [HKTV, Lemma 2.6.1] we have that `|t_{12}| ≤ D_1/2`, and therefore
> `D_1D_2 − t_{12}² ≥ 3D_1²/4 > (3C²/4)p^{2θ}`. Since `D_1D_2 − t_{12}²` is the determinant of
> a sublattice of the Gross lattice of rank 2, by Proposition 3.1 for this elliptic curve `E`
> there is an isogeny `E → E^{(p)}` of degree strictly greater than `(3C²/16)p^{2θ−1}`.
> Letting `θ = (η+1)/2` and `C = √(4C'/3)`, we deduce thus from Yang's result that if
> `η < 1/3`, then for any constant `C' > 0` there exists a prime number `p` and a supersingular
> elliptic curve `E` defined over `F̄_p` with an isogeny `E ⟶ E^{(p)}` of degree at least
> `C'p^η`.

**Quantifier order, made explicit (KN-TECH-080 audit 3):**

```
∀ η < 1/3 . ∀ C' > 0 . ∃ p prime . ∃ E supersingular /F̄_p .  δ_E ≥ C'·p^η
```

Note carefully what it is **not**: it is *not* `∀p ∃E`. It is an infinitely-often statement
in `p`, and it is about the **extremal** curve at those `p`. The witness `p` may depend on
`η` and `C'`.

**Why it nonetheless kills disjunct 1 decisively.** Suppose a bound `δ_E ≤ c·p^{1/4}` held
for all supersingular `E` over `F̄_p` for all `p ≥ p_0`. Take `η = 0.3 < 1/3` and any `C' > 0`;
Remark 4.3 yields `(p, E)` with `δ_E ≥ C'p^{0.3}`, hence `C'p^{0.3} ≤ c·p^{1/4}`, hence
`p^{0.05} ≤ c/C'`. Because `δ_E ≤ (p/2)^{1/3}` always (Theorem 4.2), the witness satisfies
`C'p^{0.3} ≤ (p/2)^{1/3}`, i.e. `p^{1/30} ≥ C'·2^{1/3}` — so the witness `p` grows without
bound as `C' → ∞`, and `p^{0.05} ≤ c/C'` fails for `C'` large. Contradiction. More generally
**no bound `δ_E ≤ Cp^η` with `η < 1/3` can hold for all supersingular `E`.** The exponent
`1/3` in Theorem 4.2 is exactly optimal as a universal bound.

**Recorded imprecision in the source, not a defect in the conclusion.** The final sentence
as printed says "*there exists … `E` … with an isogeny `E ⟶ E^{(p)}` of degree at least
`C'p^η`*", which read literally is trivial (compose with anything). The derivation two
sentences earlier makes the intent unambiguous: it bounds `D_1D_2 − t_{12}²` from below,
that quantity is the *minimum* rank-2 sublattice determinant for a Minkowski-reduced
rank-3 lattice, and Proposition 3.1 turns the minimum into `δ_E`. The intended and derived
statement is `δ_E > (3C²/16)p^{2θ−1}`. The audit uses the derived statement and records the
printed wording so that a Validator checks the same object.

**Dependency disclosure.** P1 inherits `[Yan08, Proposition 1.4]`, `[GL25, Proposition 3.7]`,
`[CCO14, 2.1.5]` and `[HKTV, Lemma 2.6.1]`. **None of those four was fetched in this
session.** They are cited by AOV as unconditional results; this audit inherits them exactly
as AOV states them and does not verify them. This is the same class of inherited dependency
that `KN-TECH-058` records for the frozen text's `[35]` reductions.

---

## 6. Pillar P2 — derivation D1: the fraction of curves with `δ_E ≤ p^{1/4}` is `≤ p^{-1/8+o(1)}`

**This section is a derivation performed in this task.** It is `proof_status: derivation`
in the sense of `docs/claims-and-verification.md` §"Refutation artifacts": a self-contained
argument a reader can check step by step. It is **not** a cited theorem, **not** machine
checked, and **not** an empirical measurement.

### 6.1 Ingredients, each with its status

| # | statement | status |
|---|---|---|
| a | For `p > 11` and `n < p/4`: a least-degree isogeny `E → E^{(p)}` of degree `n` corresponds to `ψ ∈ End(E)` with `trd(ψ) = 0` and `nrd(ψ) = np`. | **AOV §3, primary text fetched this session.** AOV's argument: `nrd(α) ≥ ¼trd(α)²`; `p | trd(α)` for `α` inseparable, "*since `p` is either inert or ramified in any imaginary quadratic field that embeds into `B_{p,∞}`, an element of `B_{p,∞}` of norm divisible by `p` must also have trace divisible by `p`*"; so `nrd = np < p²/4` forces `trd = 0`. |
| b | Hence `ψ² = −np`, so `Z[ψ] ≅ Z[√(−np)]`, an order of discriminant `−4np`. | immediate from (a) |
| c | For an imaginary quadratic order of discriminant `D < 0` in which `p` is not split, the number of supersingular `j`-invariants over `F̄_p` admitting an embedding of it is `≤ H(4n p)` up to a bounded factor (Deuring/Eichler optimal-embedding count, summed over the finitely many orders containing `Z[√(−np)]`; the `1/|Aut|` weights are bounded). | **standard background, NOT fetched this session.** Flagged for Validator. AOV itself uses the same correspondence in the other direction in Remark 4.3, via `[GL25, Prop 3.7]`. |
| d | `h(D) ≪ |D|^{1/2} log|D|`, hence `H(4np) ≪ (np)^{1/2+o(1)}`. | **classical, NOT fetched this session.** Flagged for Validator. |
| e | `#{supersingular j-invariants over F̄_p} = p/12 + O(1)`. | **standard background, NOT fetched this session.** Flagged for Validator. |

### 6.2 The count

For `T ≤ (p/2)^{1/3}` (so that `n ≤ T < p/4` for `p` large, and (a) applies):

```
#{E : δ_E ≤ T}  ≤  Σ_{n ≤ T} #{E : δ_E = n}
               ≪  Σ_{n ≤ T} (np)^{1/2+o(1)}                    [(a),(b),(c),(d)]
               ≪  T^{3/2} · p^{1/2+o(1)}
```

and dividing by (e):

```
       fraction(T) := #{E : δ_E ≤ T} / (p/12)  ≪  T^{3/2} · p^{-1/2+o(1)}          (D1)
```

### 6.3 What D1 says

- **At `T = p^{1/4}`:** `fraction ≪ p^{3/8 − 1/2 + o(1)} = p^{-1/8+o(1)}`.
  `p^{-1/8}` is **not** `p^{-o(1)}`. **L1's second disjunct fails at exponent `1/4`.**
- **The threshold is exactly `1/3`:** `fraction(p^θ) ≥ p^{-o(1)}` requires
  `3θ/2 − 1/2 ≥ −o(1)`, i.e. `θ ≥ 1/3 − o(1)`. So `1/3` is precisely the smallest exponent
  at which a `p^{-o(1)}` fraction of curves can have `δ_E ≤ p^θ`. Not "1/4 is hard"; **"1/3
  is the boundary".**
- **The bound is saturated, not slack, at `1/3`:** at `T = (p/2)^{1/3}` D1 returns
  `fraction ≪ p^{o(1)}`, i.e. it becomes vacuous exactly where AOV Theorem 4.2 says the true
  fraction is `1`. A counting bound that goes vacuous precisely at the known truth is
  consistent and cannot be improved at that exponent.

### 6.4 Baseline reproduction (KN-TECH-080 audit 1)

Combining D1 with the goal record's opening cost reading (`exponent_budget`, factors
F1–F4: one attempt at degree threshold `p^θ` costs `X² ≈ p^θ`, attempts are re-randomised,
F4 contributes exponent 0):

```
total ≈ p^θ · fraction(p^θ)^{-1}  ≫  p^θ · p^{1/2 − 3θ/2}  =  p^{1/2 − θ/2}
```

- at `θ = 1/3`: `p^{1/3}` — **exactly the frozen source's exponent, reproduced from a
  completely independent direction** (a class-number count, versus the source's
  Hermite/Cassels bound plus smoothness heuristic);
- at `θ = 1/4`: `p^{3/8}` — **worse than the incumbent**;
- `p^{1/2 − θ/2}` is *decreasing* in `θ`, and `θ` is capped at `1/3` by Theorem 4.2 (beyond
  which the fraction saturates at 1 and the cost is just `p^θ`, increasing). **`θ = 1/3` is
  the interior optimum of the method.**

This is the method ceiling in the §8 sense: *the strongest result the proposed measure could
certify even under ideal tuning*. Lowering the degree threshold does not help; it strictly
hurts, and by an amount the bound quantifies.

**Conditionality flag:** this bookkeeping step (§6.4 only — not D1 itself) uses the goal
record's *opening, self-declared-unverified* reading of the exponent budget.
`TASK-20260805-85af9d` is re-deriving that reading from primary text. If F1↔total is
corrected, §6.4 must be recomputed. D1 and the verdict in §6.3 do not depend on it.

### 6.5 Where D1 could fail

Recorded so a reviewer knows where to push, rather than left for a reviewer to find:

1. Ingredient (c) — the optimal-embedding count and the treatment of non-maximal orders
   between `Z[√(−np)]` and the maximal order. A factor of `n^{o(1)}` here is harmless; a
   factor of `n^{1/2}` would not be.
2. Ingredient (e)'s weighting: curves versus `j`-invariants versus maximal orders differ by
   bounded factors (`E` and `E^{(p)}` share an order; `|Aut| ∈ {2,4,6}`). All bounded, all
   absorbed in `o(1)` — but a reviewer should confirm no factor of `p^{ε}` hides there.
3. The step from "least-degree isogeny" to "some isogeny": D1 counts curves possessing
   *some* trace-zero inseparable endomorphism of norm `≤ Tp`, which is a superset of
   `{δ_E ≤ T}`. That direction is the safe one for an upper bound. ✓
4. `Remark 1` of the frozen text (line 191) observes there are "*generally multiple small
   (non-cyclic) isogenies E → E^{(p)}*". D1 is a bound on the number of *curves*, not on the
   number of *isogenies*, so multiplicity does not weaken it. ✓

---

## 7. Nearby-object control (KN-TECH-080 audit 4, second half)

The lever explicitly permits substituting "another cheaply-recognisable auxiliary target",
so this control decides part of the verdict rather than merely annotating it.

The load-bearing structure identified in §2–§3 is: **(rank 3) + (discriminant `≍ p`) +
(the trace-zero reduction, which exists because the target is the Frobenius conjugate)**.
Each candidate neighbour is tested against exactly that.

| # | nearby target | does the ceiling argument still apply? | result |
|---|---|---|---|
| N1 | **other Galois conjugates** `E^{(p^k)}` | `E^{(p²)} = E` for `E/F_{p²}` (frozen text line 220 uses exactly this: "*the domain of `χ` is `E^{(p²)} = E`*"). The Galois orbit is `{E, E^{(p)}}`. | **degenerate — there is no other conjugate to substitute.** The control returns nothing to test. Recorded rather than scored. |
| N2 | **quadratic (and other) twists** | A twist has the same `j`-invariant, hence the same vertex of the isogeny graph and the same maximal order `O`; `Hom(E, (E^t)^{(p)})` is isometric to `Hom(E, E^{(p)})`. AOV §5.1 Remark 1 of Delfs–Galbraith's §3 both treat twists as bookkeeping on `j`. | **ceiling transfers exactly.** No gain, and none available. |
| N3 | **small-degree-modified targets** `E' = E^{(p)}/G`, `#G = m` | If `ψ: E → E'` has degree `d`, then composing with the dual of `E^{(p)} → E'` gives `E → E^{(p)}` of degree `dm ≥ δ_E`. So `{E : ∃G, #G = m, mindeg(E→E^{(p)}/G) ≤ T} ⊆ {E : δ_E ≤ mT}`, and D1 applies with `T ↦ mT`. | **ceiling transfers, with the invariant being the PRODUCT `mT`.** A `p^{-o(1)}` fraction still requires `mT ≥ p^{1/3−o(1)}`. Escaping by nudging the target requires nudging it by degree `≥ p^{1/3}/T` — at which point locating `G` is the original problem again. |
| N4 | **`E → E'` for `E'` a generic supersingular curve** (the null object: an unstructured target) | The trace-zero reduction is unavailable (no involution), so the governing lattice is the rank-4 `Hom(E,E')` of determinant `p²/16`; Hermite gives exponent **`1/2`**, and Delfs–Galbraith's own framing (a meet-in-the-middle over `≈ p` curves) puts the typical minimal degree at `≍ p^{1/2}`. | **the method behaves differently on the null object — exponent `1/2`, not `1/3`.** This is the control passing: the argument is *not* insensitive to the structure it claims to use. |
| N5 | **structurally different auxiliary targets** — oriented curves, curves with prescribed torsion images, higher-dimensional objects (superspecial abelian surfaces), targets over larger fields | Neither the trace-zero reduction, nor Proposition 3.1, nor D1's Deuring count applies. The argument is **silent**, not negative. | **NOT COVERED.** This is the residual open direction and is the one redirection component inside the CLOSED verdict. |

**Control outcome:** the ceiling separates the intended object (`E^{(p)}`, exponent `1/3`)
from the null object (a generic target, exponent `1/2`), so it has identified real
structure rather than being a generic lattice platitude (N4). It **extends** to the
neighbours a lever would naturally substitute (N1–N3) rather than merely deflecting to
them. **The control therefore did not change the verdict from CLOSED to REDIRECTED** — but
it did carve the verdict's scope, which is why the verdict line names its scope explicitly.

---

## 8. Quantifier-order audit (KN-TECH-080 audit 3)

Recorded because three superficially similar statements have different quantifier
structures and conflating any two of them would produce a false closure or a false opening.

```
(i)     ∀p . ∀E ss/F̄_p .                     δ_E ≤ (p/2)^{1/3}            AOV Thm 4.2  [PROVEN]
(iii-a) ∀η<1/3 . ∀C'>0 . ∃p . ∃E ss/F̄_p .    δ_E ≥ C'·p^η                 AOV Rmk 4.3  [PROVEN]
(iii-b) ∀p . ∃E ss/F̄_p .                     δ_E = 1                      AOV §2.2     [PROVEN]
(iii-c) ∀p . ∀T ≤ (p/2)^{1/3} .              #{E: δ_E ≤ T}/(p/12) ≪ T^{3/2}p^{-1/2+o(1)}
                                                                          D1, §6       [DERIVED HERE]
L1-d1   ∃C . ∀p . ∀E ss/F̄_p .                δ_E ≤ C·p^{1/4}              [REFUTED by (iii-a)]
L1-d2   ∀p . #{E: δ_E ≤ p^{1/4}}/(p/12) ≥ p^{-o(1)}                       [REFUTED by (iii-c)]
```

The trap this audit was most at risk of: `(iii-b)` and `(iii-a)` are both "lower-bound
shaped" and both `∃`-quantified over `E`, but they point in opposite directions —
`(iii-b)` says there is always a curve at the floor, `(iii-a)` says there is sometimes a
curve at the ceiling. **Neither is a per-curve floor, and neither alone closes L1.**
Only `(iii-c)`, which quantifies over the *population*, closes the disjunct the algorithm
actually needs.

---

## 9. Observation-collision test (KN-TECH-080 audit 2), briefly

The observable the closure relies on is `δ_E`, equivalently `N_1` of the rank-3 lattice
`(R, Q')`. Two ground-truth objects with the same observable but opposite status would be
two curves with equal `δ_E` where the conclusion holds for one and fails for the other.
Because the conclusion here is a *population count* rather than a per-curve predicate, a
collision at the level of `δ_E` is not a defect: D1 sums over the fibres of `δ_E`
deliberately. The audit is recorded as **not applicable in its usual form**, with the
substitute check being §6.5's list of places the fibre count itself could be wrong.

AOV supply a real observation collision of a different kind, worth recording: for
`p = 22,273` they exhibit a Gram matrix satisfying every constraint of their sieve for
which "*there is no supersingular elliptic curve realizing this quadratic module*" (§5.1).
The lattice-level observable is therefore **not** identifying for the curve-level object.
That does not affect D1 (which is an upper bound and so is unharmed by counting
non-realised lattices) but it would matter to any lever that tried to *construct* a curve
from a desired lattice.

---

## 10. What this audit does NOT establish

Stated plainly, because a closed lever is exactly where scope creep is cheapest.

1. **Nothing about whether `p^{1/4}` is reachable** for the supersingular isogeny problem
   over `F_{p²}`. L1 is one of five enumerated levers, the enumeration is explicitly
   non-exhaustive (`lever_completeness_disclaimer`), and L2, L3, L4, L5 are untouched here.
2. **Nothing about the frozen algorithm's correctness, its Heuristic 1, or its concrete
   cost.** Those belong to GOAL-P13-001 (`EV-PEC-2e67ff`, `EV-PEC-857664`) and are inputs,
   not re-derived here.
3. **No claim that `1/3` is a lower bound for the problem.** D1 is a ceiling on a *method*
   — degree-threshold + meet-in-the-middle + re-randomisation — not on the supersingular
   isogeny problem. A mechanism that does not route through a bound on `δ_E` is entirely
   outside its reach. Treating §6.4 as evidence that the problem is `p^{1/3}`-hard would be
   precisely the "saturated framework mistaken for a saturated problem" failure that
   `KN-TECH-080` card D warns against.
4. **No verification of the inherited dependencies:** `[Yan08]`, `[GL25]`, `[CCO14]`,
   `[HKTV]`, `[Cas97]`, `[CG14]`, `[AV]`, `[Mar03]` — all cited by AOV, none fetched.
   `[AV]` (Aubry–Vincent) is especially load-bearing: AOV Theorem 2.2, Proposition 3.1 and
   the `Q' = Q/(4p)`, `discriminant p/4` statement all rest on it.
5. **Single-session retrieval of AOV.** This session fetched AOV independently of the
   earlier `TASK-20260724-P13-REV-R1` retrieval and the two agree on Theorem 4.2's
   statement, but both readings originate under the same model (see §11). `RT-20260728-013`'s
   standing objection about single-reader keystone verification is *reduced*, not closed.

---

## 11. Evidence-strength cap, restated

Per `BATCH-001-OPENING.md` §5 and `ledger/goals/GOAL-SSIQ-001/goal.yaml`
`runtime.runtime_note`: per-role model policies do not resolve under this Claude Code
binding. The requested policy was `executor-implementation`; the adapter binds it to
`anthropic:claude-sonnet-5 (effort=medium)`; the session that produced this audit is
`claude-opus-5` under `model: inherit`. `fallback_used: true`. Producer/reviewer
independence available to this campaign is **session** independence, not **model**
independence. Any evidence record built on this audit inherits that cap.

---

## 12. Recommendations for the next batch (RECOMMENDATIONS, not decisions)

Ordered by cost. None of these mints a hypothesis, designs an experiment, or changes a
record status; all of that is the Coordinator's.

**R1 — Validate D1 before anything is built on it. Cheapest, highest leverage.**
An independent Validator re-derives §6.2 and checks ingredients (c), (d), (e) against
fetched primary sources (Deuring/Eichler optimal-embedding count; the class-number bound;
the supersingular mass formula). Zero compute, one session. **If D1 falls, disjunct 2 of L1
reopens immediately and BATCH-002 has a live lever again**; if it holds, L1 is closed with
a real ceiling argument and the campaign has its first committed §8 closure.

**R2 — Null-object control on D1 at finite `p`, using AOV's own published artefacts.**
AOV computed `δ_E` for *every* supersingular curve for every prime `p ≤ 22,000`, plus
sieved ranges to `p ≤ 265,207`, and released code at `[AOV26]` (GitHub, "WISDE"). Measuring
the empirical `fraction(T) = #{E : δ_E ≤ T}/#{E}` against D1's `T^{3/2}p^{-1/2}` shape is a
direct instrument check. **State the limit honestly up front:** at `p ≈ 2·10^5` and
`T = p^{1/4} ≈ 22`, D1's bound is numerically vacuous (it exceeds the total curve count), so
this measures the *shape and constant* of the model, not the exponent. One decade of `p` will
not resolve an exponent. It is still the only place a coding error in D1's exponent would
show up cheaply.

**R3 — Audit the residual redirection, N5, before treating L1 as fully retired.**
The only surviving direction inside L1's own wording is "another cheaply-recognisable
auxiliary target" of a *structurally different* kind (N5): oriented curves in the sense of
`[40]` (Corte-Real Santos–Herlédan Le Merdy–Macula–Meyer–Morrison–Orvis, ePrint 2026/1219,
cited by the frozen text at line 53 as having reused Frobenius conjugates), targets with
prescribed torsion images, or higher-dimensional targets. The audit question is sharp and
cheap: **does the substitute target have a rank-3 governing lattice of discriminant
`≪ p^{3/4}`, or a governing lattice of rank `< 3`?** Those are the only two ways to reach
exponent `1/4` from a lattice-minimum bound, and both are checkable from a discriminant
computation before any implementation.

**R4 — Record the general shape as a candidate technique note, not as a finding.**
The pattern "*exponent = (1/rank) × (log_p discriminant)*, and the count of curves below a
threshold is what a re-randomising algorithm actually consumes" generalised cleanly here
and produced both a ceiling and an independent reproduction of the incumbent exponent. It
is a method, not a result. If the Coordinator wants it in `knowledge/`, it belongs as a
`KN-TECH` after R1 passes — never as a `KN-FIND`, since this task established no result of
the program's own beyond D1.

**R5 — Do not spend BATCH-002 budget re-attacking F1.**
Per AGENTS.md rule 9 the deprioritisation is recorded with its parts: *evidence* — AOV
Theorem 4.2, Remark 4.3, and D1; *budget* — one zero-compute session; *test boundary* —
targets `E^{(p)}` and its small-degree-modified neighbours only, nothing about L2/L3/L4/L5
or about N5; *remaining uncertainty* — D1's ingredients (c)–(e) unverified, N5 unaudited,
eight cited AOV dependencies uninspected; *successor* — R3; *revisit condition* — **if R1
finds D1 unsound, or if R3 finds a substitute target whose governing lattice has rank `< 3`
or discriminant `≪ p^{3/4}`, L1 reopens.**

---

## Artefacts and locators

| what | where |
|---|---|
| frozen source (Theorem 1.5 line 81; Section 4.2 isometry line 244; Heuristic 1 line 69; Remark 1 line 191) | `inputs/P13-WESOLOWSKI-2026/paper_fulltext.md` |
| AOV arXiv:2607.14624v1, HTML body | fetched; SHA-256 `eec18aefad605f879e92b1174d16f161a9d1ea6ea9fa8ce42406cac62bb4e98d` (`source_access_log.yaml` → `aov_html`) |
| AOV PDF (retained hash only; no text extractor available in-environment) | SHA-256 `6f556abbe4b3c3b60ac7a55dd775b3e4feb8f02c77d831db4f9e74668cb9be31` (`aov_pdf`) |
| AOV abstract page | SHA-256 `09768304a2cb8d6edfae58be192d08e79e0066a007d62fbc9d6a489fdb047cf7` (`aov_abs`) |
| every retrieval attempt, successful or not | `source_access_log.yaml` |
| L4 companion | `L4_baseline_acquisition.md` |
| prior single-reader retrieval of AOV (GAP-7 closure) | `coordination/tasks/TASK-20260724-P13-REV-R1/review_tail_report.yaml`, item T5 |
