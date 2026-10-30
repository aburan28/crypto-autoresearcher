---
title: "Lead 4: small-root / algebraic decomposition oracles for S4 and S5 over prime fields"
date: 2026-10-28
---

# Lead 4: small-root and algebraic decomposition oracles for S₄/S₅ over F_p

**Status.** Ideation and paper analysis (§0–§7), followed by measured
probes with native code (§7a, §7b). No breakthrough is claimed. No idea below plausibly reaches the S₄ milestone
(δ ≥ 1/4) or the S₅ goal (δ ≈ 1/5). The four ranked records are ordered by
expected information per unit cost, not by any chance of success.

**Labels used throughout.** `[measured]`: a run in this repository, cited.
`[derived]`: computed in this note and checkable from the stated formula.
`[literature]`: reported in a cited source, with how much of it was read.
`[proposed]`: an idea or prediction, not a result. `[recalled]`: from memory,
not re-read this session.

![Figure 1. δ-vs-arity map (A) and the m = 4 oracle-cost plane (B). Source: delta_arity_map.svg in this directory.](delta_arity_map.svg)

## 0. Bottom line

1. `[derived]` **The "1/80" for S₅ is an asymptotic formula and was never
   measured.** Probes B and C measured m = 2 (S₃) only. At lattice
   dimensions that can actually be reduced (about 5·10³ or less), the
   determinant bound at m = 4 is δ ≈ 1/313 (symmetric lattice, level 2,
   dimension 4845). On a 40-bit curve that means B = 1. The shortfall to
   δ ≈ 1/5 at feasible dimension is about **63×**, not 16×. At m = 3 the best
   feasible bound is δ ≈ 1/35.5 (dimension 969), which is B ≈ 2 at 40 bits,
   against the milestone's B = 2¹⁰ (§3.2).
2. `[derived]` **Six structural facts (F1–F6, §3.3) bound every lattice
   oracle on a coordinate factor base on a prime-order curve.** They are a
   principal ideal, Newton-polytope rigidity, the degree-optimality of x,
   box-volume invariance, the cost of overdetermination, and the
   global-lifting wall. Together they explain why every lattice variant
   measured so far lands on the same threshold, and they kill the 16
   mechanisms in §5.
3. `[proposed]` **Rank 1 is a closure test (L4-B).** It turns F1–F4 into a
   checkable statement with three premises, P1–P3. Its first step is
   symbolic and takes minutes. If a premise fails, that failure is the only
   lattice lead this note leaves open.
4. `[proposed]` **The narrow remaining space** (§7) is: a non-lattice
   small-root algorithm for one structured congruence at box volume
   p^{0.7–0.8}; factor bases that are not coordinate boxes (implicit,
   high-degree, or target-dependent); and transfer (§4.3 of the program
   note). This note has no concrete candidate in any of them.
5. `[derived]` **A planned experiment looks inapplicable.** The
   "D₄-symmetrised S₅ lattice probe" in `RESEARCH_IC_LEADS_AND_CONNECTIONS_20261010.md`
   §8.2 and §9.5 needs a rational 2- or 4-torsion point (as in FHJRV). That
   point does not exist on a prime-order curve. On even-order test curves
   the gain is a constant (K3, §5).
6. `[measured]` **The follow-up probes, run with native code (§7b), find
   nothing past the bounds.**
   - L4-B step 1 (native port) agrees with GP: S₄ and S₅ are dense and
     irreducible over F_p.
   - L4-C: an exact census over all targets on six toy curves finds no extra
     additive structure in small-x factor bases (41/41 cells inside the null
     band).
   - L4-A: symmetric S₄ lattices at dims 35 and 165 recover no planted
     non-global root at B ≥ 2, matching §3.2. A v1 false positive came from
     global relations and was amended.
   - P3: the ePrint LP could not be retrieved. Our search over triangular
     shift lattices exceeds no JM asymptote.
   - P3, addendum (2026-10-29, §7c): the strategy-independent bound of
     `research/smallroot_optimal_reach_20261026` applies here. Any
     x-variable lattice built from `(p, S)^t` on a convex monomial set
     reaches at most δ = 1/21.8 for S₄ and 1/70.8 for S₅. Those are 5.5× and
     14.2× short of the milestone and the goal, whatever the shift strategy,
     the LP included. This is conditional on that study's written proof,
     which has no Lean formalization. Only the arithmetic step is
     Lean-checked (§7c, "Formalization status").

## 1. Question

Is there a concrete lattice, embedding or algebraic structure that gives a
decomposition oracle for Semaev's S₅ (m = 4 summands) at δ ≈ 1/5, or for S₄
(m = 3) at δ ≥ 1/4, on prime-field curves? Under §5 of
`RESEARCH_PRIME_FIELD_BREAKTHROUGH_PROGRAM.md`, only such a structure
changes the exponent. Constant-factor tuning does not count. Generic table
oracles, which converge to BSGS, are out of scope.

## 2. Scope, inputs, and what was not done

* **Read.** `RESEARCH_PRIME_FIELD_BREAKTHROUGH_PROGRAM.md` (all of it,
  including the Probe B/C tables). `RESEARCH_IC_LEADS_AND_CONNECTIONS_20261010.md`
  §8–§10 (from the worktree copy
  `worktrees/codex-n83-d18-k2048-20261027/`). The AGENTS.md pointers file.
  The idea-generator contract and the inventor protocol in
  `crypto-autoresearcher`. Its ECDLP frontier rows `KR-IC-5931ee` and
  `KR-IC-5a43e5`. `KN-LIT-d8e1b9`.
* **Not done: no shell was available in this session.** The available
  tools were file read/write, grep/glob and web search/fetch. So:
  * I could not run `git log` or `git show` on the other sessions'
    branches. `research/prime-fall-degree-20261027`,
    `research/ic_prime_residual_lp_20261026` and
    `lead/ic-residual-lp-20261028` are not in the local refs. Only
    `research/fall-degree-bounds-20261008` and
    `research/prime-ksum-table-20261028` are, and branch contents cannot be
    read without git. §6 therefore scopes by topic, not by reading their
    results.
  * `pandoc` and `rsvg-convert` could not be executed here. The parent
    session rendered `report.pdf` afterwards (§9).
  * No experiment was run and no canonical IDs were allocated.
* **Write location.** The brief asked for
  `/Volumes/SSD990/crypto/research/prime_s5_small_root_leads_20261028/`.
  This session's write hook refused that path because it is the base
  checkout, not this session's worktree. The files are at
  `/Volumes/SSD990-2/crypto/objective-ritchie-6bf995/research/prime_s5_small_root_leads_20261028/`.
  Copying the directory across is a plain `cp -R`.
* **The `research-visuals` skill file.** It was not on disk in either
  checkout (it is presumably on `origin/main`). I followed the brief's
  version of it: a report, an editable SVG, and a PDF.

## 3. The baseline, re-derived in usable units

### 3.1 The target in cost-exponent form

`[derived from program note §2.4]` Write B = p^δ and T_dec = p^τ. Then
cost(B) ≈ (m!/2^m)·p·T_dec/B^{m−1} + m·B² has exponents 1 − (m−1)δ + τ and
2δ. The cost beats √p if and only if

    δ < 1/4   and   τ < (m−1)·δ − 1/2.

| m | polynomial | feasible δ window at τ = 0 | largest admissible τ | generic oracle τ = (m−1)δ |
|---|---|---|---|---|
| 3 | S₄ | none; tie only at δ = 1/4, τ = 0 | 0 | always above |
| 4 | S₅ | [1/6, 1/4) | 1/4 | always above |
| 5 | S₆ | [1/8, 1/4) | 1/2 | always above |
| m | S_{m+1} | [1/(2(m−1)), 1/4) | (m−3)/4 | always above |

So an oracle need not run in polynomial time. At m = 4 it may cost up to
p^{1/4}. What it must do is put its cost curve τ(δ) inside the triangle
δ ∈ (1/6 + τ/3, 1/4), τ < 3δ − 1/2 (Figure 1B). Every known route is
listed below. Past δ = 1/24, none of them is below τ = 3δ.

* Enumerate three coordinates and root-find the fourth: τ = 3δ.
* Enumerate k coordinates and use a lattice for the rest:
  * k = 2, bivariate degree-8 lattice: valid only for δ ≤ 1/24, with τ = 2δ.
  * k = 1, trivariate: δ ≤ 1/48, with τ = δ.
  * pure lattice: δ ≤ 1/80, with τ = 0.

### 3.2 Finite-level lattice reach (determinant bounds)

`[derived]` In each case below, the reach at level ℓ is Σ_α k(α) divided by
Σ_α (log_B of the size of x^α), taken over the lattice monomials. HG
dimension factors and binomial constants are ignored, exactly as in the
program note's §2.2.

* **Box (Jochemsz–May, monomials [0, dℓ]^m, d = 2^{m−1}).**
  δ_ℓ = Σ_{i<ℓ} (d·i + 1)^m / (m·(dℓ+1)^m·dℓ/2), with dimension (dℓ+1)^m.
  This reproduces the note's 1/18, 1/10 and 0.119 at m = 2.
* **Symmetric (monomials in e₁..e_m, total degree ≤ Dℓ, D = 2^{m−1}).**
  The weights are w_i = i because e_i ≤ C(m,i)·B^i. The leading monomial is
  e_m^D.
  δ_ℓ = Σ_{i<ℓ} C(D·i + m, m) / ((m(m+1)/2)·C(Dℓ + m, m + 1)), with
  dimension C(Dℓ + m, m).
  This reproduces the note's 1/12 at m = 2, level 1.
* **The two forms have the same asymptote.** Both tend to
  2/(m(m+1)·2^{m−1}) = 1/(m(m+1)2^{m−2}).
  * This is consistent with Probe C, which found equal thresholds for Rect
    and Sym.
  * At m = 2 the asymptote is 1/6. The note's "1/9 for the symmetric
    lattice" (§4.6) appears to undercount. That does not affect any
    decision.
  * At equal dimension the symmetric lattice is better at every finite
    level. At m = 2, level 3 it reaches 0.131 at dimension 28, against 0.119
    at dimension 49 for the box. So it is the right vehicle for measuring
    m = 3 and m = 4.

| m | lattice | level ℓ | dim | δ_ℓ | B at 40 bits | B at 56 bits | shortfall vs needed δ |
|---|---|---:|---:|---:|---:|---:|---:|
| 2 | box (measured HG 0.10, heuristic 0.14–0.16) | 1–3 | 9–49 | 1/18–0.119 | 15–84 `[measured]` | 48–229 `[measured]` | 3–5× vs 1/2 |
| 3 | box | 2 | 729 | 1/69.4 | 1.5 | 1.7 | 17× vs 1/4 |
| 3 | sym | 1 | 35 | 1/210 | 1.1 | 1.2 | 52× |
| 3 | sym | 2 | 165 | 1/55.0 | 1.7 | 2.0 | 13.8× |
| 3 | sym | 3 | 455 | 1/40.7 | 2.0 | 2.6 | 10.2× |
| 3 | sym | 4 | 969 | 1/35.5 | 2.2 | 3.0 | 8.9× |
| 3 | asymptotic | ∞ | ∞ | 1/24 | 3.2 | 5.0 | 6× |
| 4 | sym | 1 | 495 | 1.26e−4 | 1.0 | 1.0 | ≈1600× vs 1/5 |
| 4 | sym | 2 | 4845 | 1/313 | 1.09 | 1.13 | ≈63× |
| 4 | sym | 3 | 20475 | 1/184 | 1.16 | 1.23 | ≈37× |
| 4 | asymptotic | ∞ | ∞ | 1/80 | 1.41 | 1.62 | 16× |

The symmetric rows assume premise P2 of L4-B: the symmetrised support is
the full simplex of degree 2^{m−1} with e_m^{2^{m−1}} present.

One `[measured]` observation matters for interpretation. At m = 2, level 1,
the heuristic success at 40 bits extends to δ = 0.14, which is 2.5 times the
level-1 bound of 1/18. At 56 bits it drops to 0.10–0.12. So the slack
shrinks with p, which is what a finite-size effect looks like (L4-D).

### 3.3 Six structural facts

* **F1. The ideal is principal. `[derived from known irreducibility]`**
  * For generic z = x_R, the zero set of S_{m+1}(·; z) in A^m is
    x^m(A_R), the image of the coset A_R = {(P_i) : ΣP_i = R} ≅ E^{m−1}.
  * A_R is irreducible. The images of all sign patterns coincide because
    x(−P) = x(P). So the ideal of the zero set is (S_{m+1}(·; z)), given
    that S is squarefree.
  * Hence every polynomial that vanishes on all decompositions is a
    multiple of S. That includes translated targets
    S_{m+2}(x, x_T, x_{R+T}), symmetrised forms, and resultant splittings.
    The curve structure contributes nothing beyond S itself.
  * Irreducibility of S_n is known: Semaev 2004 `[recalled]`, and the
    corpus re-derives it via the Galois group (Z/2)^{m−2} (KN-FIND-a8990a,
    cited from KR-IC-5a43e5 `[kb]`).
* **F2. Newton polytopes are rigid. `[derived; Ostrowski, recalled]`**
  * Over F_p, NP(g·S) = NP(g) + NP(S). So every nonzero element of the
    ideal mod p has a Newton polytope containing a translate of NP(S). No
    sparser or lower-degree representative exists, and the JM monomial
    sets are forced up to shifts.
  * Modulo p^ℓ, zero divisors weaken this into a heuristic. That is why
    P3 asks an LP.
* **F3. x is degree-optimal among coordinates. `[derived]`**
  * Every degree-2 function in F_p(E) has the form M∘x∘τ_S, where M is a
    Möbius map and S ∈ E(F_p). Its involution is P ↦ Q − P, and Q can be
    halved because the group order is odd.
  * A degree-D coordinate gives a relation of degree up to D^{m−1} in each
    variable. With R fixed, P₁ has D^{m−1} candidates.
  * Values are identified only when the fibres are Aut(E)-orbits, so
    D ∈ {2, 4, 6}. Then |F| ≈ D·B, and the per-|F| reach
    2/(m(m+1)D^{m−1}) is largest at D = 2.
* **F4. Box volume is invariant. `[derived, first order, heuristic]`**
  * Consider substitutions of degree 1 in new box-bounded unknowns of the
    same total volume. Examples are Farey (x = u/v), lattice cosets
    (x = u + λv), base-M digits on Solinas primes, and Möbius maps.
  * They keep the degree pattern. To first order, the JM reach measured in
    box volume is unchanged. The linear case is the template: aX + bY ≡ c
    is solvable up to XY ≈ p, exactly as x alone is up to p.
* **F5. Overdetermination costs B/p. `[derived]`**
  * In a decomposition search the expected number of solutions in a box of
    volume V is V/p. Each further independent congruence multiplies it by
    about B/p (or 1/p).
  * Many-sample Coppersmith gains depend on a planted consistent solution,
    so they do not transfer. Examples are EC-HNP with 1/(d+1) known bits
    (Xu–Sarkar–Wang–Hu 2022 `[literature, abstract]`) and MIHNP.
  * By F1, there are no free equations to add.
* **F6. The global-lifting wall. `[literature + derived]`**
  * Turning a congruence into an exact equation on small inputs means
    making |value| < p. That forces a relation over a number field.
  * With random targets this happens only below the Coppersmith regime, or
    as xedni-type relations. Xedni-type relations do not beat rho
    (Jacobson–Koblitz–Silverman–Stein–Teske 2000 `[recalled]`, program
    note §4.6).

**Conditional closure statement `[proposed]`.** On a prime-order curve,
every lattice oracle over a coordinate factor base is bounded by the
shift-set LP of S_{m+1}'s Newton polytope. That bound is the JM value if
P1–P3 hold. L4-B tests exactly this. The §4 closure standard of the
inventor protocol is met only after L4-B's premises have been measured.
Until then the closure is `unverified`.

## 4. Ranked idea records

No canonical IDs were allocated (no shell, and the brief forbade edits
outside this directory). The local labels are L4-A to L4-D. Each record
follows the `idea` schema of `agents/idea-generator.md`, abbreviated where a
field does not apply.

### Rank 1: L4-B, the ideal-rigidity ceiling (closure test)

```yaml
idea:
  id: "unallocated (local label L4-B)"
  title: "Ideal-rigidity ceiling for lattice decomposition oracles on coordinate factor bases"
  class: mechanism
  claim: >
    [proposed] On a prime-order E/F_p, every Coppersmith-type lattice oracle for
    m-decompositions over any factor base {P : t(P) in a box}, t in F_p(E), has
    asymptotic reach delta <= 1/(m(m+1)2^(m-2)) (1/24 at m=3, 1/80 at m=4), provided
    P1 S_{m+1}(.;z) is absolutely irreducible for a 1-O(1/p) fraction of z;
    P2 NP(S_{m+1}(.;z)) = [0,2^(m-1)]^m, equivalently the symmetrised support is the
       full degree-2^(m-1) simplex with e_m^(2^(m-1)) present;
    P3 the automated-Coppersmith LP (Meers-Nowakowski 2023; Ding et al. 2026) over shift
       sets drawn from (S,p)^l returns the JM value for that support.
  mechanism: >
    F1 fixes the information (every polynomial vanishing on all decompositions is a
    multiple of S). F2 fixes the support (no multiple is sparser). F3-F4 fix the
    coordinates (alternatives are box-preserving substitutions or raise the degree).
    The only remaining freedom is the shift set, which P3 prices exactly.
  novelty_status: adaptation   # optimality-of-lattices results exist (Aono et al.); applying them
                               # to Semaev's family with F1-F4 is not found in the sources checked
  citations:
    - {ref: "ePrint 2012/108; ACISP 2012; AAECC 29(2) 2018 (Aono-Agrawal-Satoh-Watanabe)", provenance: retrieved,
       claim: "bounds the reach of lattice constructions; JM/Coppersmith-May constructions asymptotically optimal in their framework",
       verified_by: "search-result abstract, 2026-10-28"}
    - {ref: "ePrint 2023/1409 (Meers-Nowakowski, Asiacrypt 2023)", provenance: retrieved,
       claim: "combinatorial, automatable restatement of Coppersmith", verified_by: "search-result abstract"}
    - {ref: "ePrint 2026/1027 (Ding-Dai-Wu-Zhang-Zhang)", provenance: retrieved,
       claim: "asymptotic bounds of automated Coppersmith computed by linear programming", verified_by: "abstract page fetched"}
    - {ref: "Semaev, ePrint 2004/031", provenance: recalled, claim: "S_n symmetric, irreducible, degree 2^(n-2) per variable"}
    - {ref: "KR-IC-5a43e5 / KN-FIND-a8990a", provenance: kb, claim: "Galois group (Z/2)^(m-2); re-derived irreducibility"}
  proof_search_map:
    bottleneck: "reach of the shift set for a fixed polynomial support; everything else is fixed by F1-F4"
    baseline_embedding:
      parameter_slice: "m=2 reproduces Probe B/C: box levels 1/18, 1/10, 0.119; sym level 1 = 1/12; both asymptotes 1/6"
      reproduction_check: "closed forms in README section 3.2 (symbolic)"
    observation_collision:
      observable: "planted-root reach in the Probe B protocol"
      distinct_preimage_search: "random polynomial with S4's exact support and degree pattern; equal reach => Semaev structure not load-bearing"
    constructive_transforms:
      - {transform: representation_reduction, proposed_object: "support polytope + LP", predicted_gain: "none (predicts JM)"}
    quantifier_order: "for all prime-order E, all coordinate t, all shift sets in (S,p)^l: reach <= LP(NP(S)); P1-P2 checked for sampled z"
    method_ceiling:
      strongest_certifiable_claim: "ceiling for lattice oracles only, conditional on Coppersmith's heuristic and P1-P3"
      nearby_object_control: "even-order curve with rational 2-torsion: the closure must predict only a constant change (K3)"
    proof_obligations:
      - {claim: "P1 irreducibility of specialisations", responsibility: correctness}
      - {claim: "P2 support = full box/simplex", responsibility: size}
      - {claim: "P3 LP optimum = JM", responsibility: strictness}
      - {claim: "prime order (no rational torsion) is required", responsibility: scope}
  predictions:
    - {metric: "nonzero vertex coefficients of S4(.;z), 40-bit Probe-B curve, 20 z", direction: higher, minimum_effect: "8/8 vertices for >= 19/20 z"}
    - {metric: "LP optimum / JM value (m=3, m=4)", direction: different, minimum_effect: "within 1% of 1"}
    - {metric: "max B with >= 4/8 success: S4 vs null polynomial at equal dim", direction: different, minimum_effect: "equal within one B step"}
  minimal_test:
    design: >
      Step 1 (symbolic, minutes): build S4(x1,x2,x3,z) by resultant for the 40-bit Probe-B curve
      at 20 random z. Record the 8 vertex coefficients of [0,4]^3, the symmetrised support and the
      e3^4 coefficient. Test absolute irreducibility by restricting to 50 random lines and factoring
      over F_p and F_{p^2}. Repeat Step 1 for the symmetrised S5 support.
      Step 2 (LP, minutes): feed both supports to the Ding et al. LP and compare to 1/24 and 1/80.
      Step 3 (Probe B/C framework, hours): only if the LP shift set differs from JM, run it at m=3
      on the 40-bit curve with Probe B's planted-root protocol, B in {2,3,4,6,8}, 8 trials per cell,
      beside Sym{l} of equal dimension; then m=4 at level 1. Otherwise go straight to L4-A.
    controls: ["null polynomial with identical support", "Sym{l} of equal dimension"]
    required_metrics: ["vertex count", "irreducible-restriction fraction", "LP optimum", "max B with >= 4/8 success", "ms per LLL"]
  falsification_conditions:
    - "Closure falsified if a vertex coefficient vanishes identically in z (P2), S4(.;z) is reducible for > 1% of z (P1), the LP optimum exceeds JM by > 5% (P3), or an LP-optimal lattice reaches >= 2 B-steps beyond Sym at equal dimension in Step 3."
    - "Any such failure is the one lattice lead left open here. Its best case is a constant factor in delta unless the support shrinks by a factor that grows with m."
  confounders: ["LLL vs BKZ quality at dim > 500", "finite-size slack at 40 bits (B <= 3 makes the Probe test coarse)"]
  interpretation_limits: ["lattice oracles only", "prime-order curves only", "says nothing about Groebner/fall-degree or non-coordinate factor bases"]
  heuristic_assumptions:
    - id: H1
      statement: "Coppersmith heuristic: the first m reduced polynomials are algebraically independent at the root"
      rigorous_support: "Howgrave-Graham bound (rigorous for vanishing over Z); independence is the heuristic"
      validation_plan: "Probe B's '>= 2 vanishing rows' and resultant non-vanishing rate, 8-64 trials per cell; compare to the HG-holds fraction"
  target_complexity:
    time_exponent: "n/a (closure test)"
    memory_exponent: "n/a"
    best_known: "Pollard rho sqrt(pi n/4); preprocessing rho S*T^2 ~ n"
    hidden_overhead: "none claimed"
    tradeoff_note: "n/a"
  prior_art:
    rows_checked: [KR-IC-5931ee, KR-IC-5a43e5, "program note section 2.2 / 4.6"]
    nearest: "Aono et al. optimality (general); program note Probe C (empirical, m=2)"
    relation: adaptation
    delta: "applies the optimality question to S_{m+1} with F1-F4, so the ceiling covers every coordinate factor base, not one lattice"
  estimated_cost: {implementation: low, compute: low}
  recommended_priority: high
```

### Rank 2: L4-A, the finite-level S₄/S₅ baseline (control)

```yaml
idea:
  id: "unallocated (local label L4-A)"
  title: "Measured S4 and S5 small-root reach for the best available (symmetric) lattices, normalised by enumeration cost"
  class: control
  claim: >
    [proposed] At m=3 and m=4 the measured reach of symmetric JM lattices matches the section 3.2
    determinant bounds, within the m=2 heuristic slack (at most 2.5x at level 1, shrinking with p).
    In particular, at 40 bits no lattice of dimension <= 5e3 reaches B >= 4 at m=3 or B >= 3 at m=4
    with >= 4/8 success, and at every cell the lattice costs more per call than the B^(m-1)
    enumeration it would replace.
  mechanism: "JM determinant bound plus a finite-size slack that decays with p (section 3.2)"
  novelty_status: known   # a measurement of known lattices; the program has not run m >= 3
  citations:
    - {ref: "RESEARCH_PRIME_FIELD_BREAKTHROUGH_PROGRAM.md section 3.2-3.3", provenance: internal, claim: "m=2 measured reach; protocol"}
    - {ref: "Jochemsz-May, Asiacrypt 2006", provenance: recalled, claim: "basic and extended strategies"}
  predictions:
    - {metric: "max B with >= 4/8 success, m=3, Sym l=2..4", direction: lower, minimum_effect: "B in [2,3] at 40 bits; [2,5] at 56 bits"}
    - {metric: "max B with >= 4/8 success, m=4, Sym l=1..2", direction: lower, minimum_effect: "B <= 2 at 40 and 56 bits"}
    - {metric: "false-positive rate on unplanted targets", direction: lower, minimum_effect: "0/8 per cell"}
  minimal_test:
    design: >
      Extend examples/prime_ecdlp_breakthrough_probe.rs with S4 and S5 (by resultants) and their
      symmetrised forms. Curves at 32, 40, 48 and 56 bits. Planted roots with B in {1,2,3,4,6,8,12,16};
      8 planted and 8 unplanted targets per cell. Lattices Sym{1..4} at m=3 and Sym{1,2} at m=4
      (dim 495, 4845), plus box level 2 at m=3 (dim 729) as a cross-check. Record HG-holds,
      '>= 2 vanishing rows', ms per reduction, and enumeration cost B^(m-1) for the same cell.
    controls: ["unplanted targets (decision behaviour)", "null polynomial with S4's support (from L4-B)", "m=2 Probe B rows re-run as a regression"]
    required_metrics: ["delta reach per (m, l, bits)", "slack = heuristic reach / delta_l", "ms per LLL / B^(m-1)"]
  falsification_conditions:
    - "Heuristic success >= 4/8 at delta >= 1/24 at m=3 (B >= 4 at 40 bits, B >= 6 at 56 bits) on >= 2 sizes, with reach not decreasing in p: that is structure-specific slack beyond the asymptotic JM value, and it contradicts L4-B."
    - "Success at B >= 3 for m=4 at level <= 2: contradicts the section 3.2 table and reopens the S5 lattice question."
  confounders: ["LLL non-determinism across implementations", "dimension factors in HG at dim > 1000", "tiny B makes brute force trivially cheaper"]
  interpretation_limits: ["a 40-bit curve resolves delta only in steps of log2(B)/40; the milestone is B = 1024 at 40 bits, so any lead is unambiguous but small reaches are coarse"]
  heuristic_assumptions:
    - id: H1
      statement: "as in L4-B"
      rigorous_support: "Howgrave-Graham"
      validation_plan: "fraction of '>= 2 vanishing' cells where the resultant actually recovers the root"
  target_complexity:
    time_exponent: "n/a (control)"
    memory_exponent: "n/a"
    best_known: "enumeration tau=(m-1)delta; rho p^(1/2)"
    hidden_overhead: "lattice cost poly(dim) with dim up to 4845"
    tradeoff_note: "n/a"
  prior_art: {rows_checked: [KR-IC-5931ee], nearest: "Probe B/C (m=2)", relation: extension, delta: "first m=3/4 rows; corrects the quoted '1/80 measured'"}
  estimated_cost: {implementation: medium, compute: "low for m=3; medium-high for m=4 level 2 (dim 4845 reductions)"}
  recommended_priority: high
```

### Rank 3: L4-D, the probabilistic regime (success-probability decay past the rigorous bound)

```yaml
idea:
  id: "unallocated (local label L4-D)"
  title: "Can the section 2.4 allowance T_dec <= p^((m-3)/4) be spent on lattice luck? Measure q(delta,p) past the bound"
  class: measurement
  claim: >
    [proposed] Past the rigorous bound, lattice success on decomposable targets decays as
    q = p^(-gamma(delta)), with gamma growing at least linearly in (delta - delta_l) times the
    dimension. Then the probabilistic oracle exponent tau = gamma(delta) exceeds enumeration's
    (m-1)delta for every delta above the asymptotic JM value, and the allowance cannot be spent on
    luck. Competing explanations: (i) finite-size slack, where q at fixed delta tends to 0 as p
    grows (predicted); (ii) structural slack, where gamma saturates below (m-1)delta (this would
    open a probabilistic-oracle lane).
  mechanism: "beyond the Minkowski/HG regime the target vector is no shorter than typical lattice vectors; success needs a short-vector coincidence whose probability falls with dim*(delta-delta_l)*log p"
  novelty_status: unverified
  citations:
    - {ref: "program note section 3.2 Probe B table", provenance: internal,
       claim: "m=2 level 1, delta=0.12: 7/7 (40-bit) vs 3/8 (56-bit); level 3, delta=0.14: 7/8 vs 3/8; delta=0.16: 5/8 vs 0/8 [measured]"}
  predictions:
    - {metric: "fitted gamma(delta) at delta = 1.2*delta_inf (m=2,3)", direction: higher, minimum_effect: "gamma > (m-1)*delta"}
    - {metric: "q at fixed delta vs bits (32..64)", direction: lower, minimum_effect: "monotone decrease, slope significant at 2 sigma"}
  minimal_test:
    design: >
      Probe B/C framework. m=2 at levels 1-3 and m=3 Sym{1,2}; curves at 32, 40, 48, 56 and 64 bits;
      delta grid from delta_rig to 2*delta_inf; 64 planted trials per cell. For each fixed delta,
      fit log2 q against log2 p to get gamma(delta). For m=3, compare with (m-1)delta = 2 delta.
      Re-randomise per trial by a fresh target, not by re-running LLL on the same basis
      (LLL is deterministic).
    controls: ["unplanted targets (false-success rate)", "null polynomial with the same support"]
    required_metrics: ["q(delta, bits) with Wilson intervals", "gamma(delta) with standard error", "ms per call"]
  falsification_conditions:
    - "Prediction falsified if some delta > delta_inf has a fitted gamma(delta) < (m-1)delta on >= 3 sizes with non-overlapping intervals. That would be the first evidence of a probabilistic lattice oracle below enumeration in exponent."
  confounders: ["discrete B steps at small bit sizes", "basis-reduction quality (LLL vs BKZ-20) changes q but should not change gamma's sign"]
  interpretation_limits: ["m=2 and m=3 only; extrapolating to m=4 assumes the same slope law"]
  heuristic_assumptions:
    - id: H2
      statement: "q(delta,p) = p^(-gamma(delta)) * poly(log p) for delta in (delta_l, 2 delta_inf)"
      rigorous_support: "Gaussian-heuristic short-vector counts in random lattices of fixed determinant (imitated, not proved for these lattices)"
      validation_plan: "five bit sizes, 64 trials per cell; check log-linearity (residuals) and that the 64-bit point lies within the 32-56-bit fit's prediction interval"
  target_complexity:
    time_exponent: "measured tau(delta) = gamma(delta); success region requires tau < 3 delta - 1/2 at m=4"
    memory_exponent: "poly"
    best_known: "enumeration tau = (m-1)delta"
    hidden_overhead: "poly(dim) per call"
    tradeoff_note: "none"
  prior_art: {rows_checked: [KR-IC-5931ee], nearest: "Probe B", relation: extension, delta: "turns the threshold into a cost exponent, which is what section 2.4 actually requires"}
  estimated_cost: {implementation: low, compute: low}
  recommended_priority: medium
```

### Rank 4: L4-C, structure in the gap (Poisson and clustering test of small roots)

```yaml
idea:
  id: "unallocated (local label L4-C)"
  title: "Are small S4 decompositions between delta = 1/24 and 1/4 distinguishable from a null model?"
  class: measurement
  claim: >
    [proposed] For delta in (1/24, 1/4), the small 3-decompositions of random targets on prime-order
    curves cannot be told apart from null models: counts are Poisson with mean lambda ~ c*B^3/p,
    targets R and R+T share summands no more often than chance, and decompositions do not
    concentrate on low-height integer subvarieties. Alternative: over-dispersion or excess
    coincidences, meaning algebraic structure in the gap that a non-lattice (determinant-method-type)
    oracle could target.
  mechanism: "between the rigidity regime (where small points lie on few Z-curves; Chang et al.) and equidistribution, nothing known forces structure; F1 says the only algebraic input is S itself"
  novelty_status: unverified
  citations:
    - {ref: "arXiv:1111.1543 (Chang, Cilleruelo, Garaev, Hernandez, Shparlinski, Zumalacarregui)", provenance: retrieved,
       claim: "upper bounds for points of modular curves in small boxes; rigidity at small box sizes", verified_by: "search-result abstract"}
    - {ref: "KN-LIT-d8e1b9 (Yokoyama-Yasuda-Takahashi-Kogure, JMC 14, 2020)", provenance: kb,
       claim: "naive Semaev IC over F_p no better than generic, under statistical assumptions on summation polynomials"}
  predictions:
    - {metric: "dispersion index Var/mean of decompositions per target", direction: different, minimum_effect: "within [0.95, 1.05] (null)"}
    - {metric: "R vs R+T shared-summand rate over null 1", direction: different, minimum_effect: "within 3 sigma"}
  minimal_test:
    design: >
      Toy prime-order curves at p ~ 2^26, 2^28, 2^30: one with a = -3 and random b, one with a = 0 and
      small b (the secp256k1 shape). B = floor(p^delta), delta in {1/24, 1/12, 1/8, 1/6, 1/5, 1/4};
      1e5 random targets per cell. Exact enumeration over pairs (P1, P2) in F^2, checking
      x(R - P1 - P2) <= B: B^2 point operations per target, at most 3.3e4 at p = 2^30, delta = 1/4,
      so minutes per cell on the native u64 engine. This is the Probe B/C protocol run exhaustively at
      toy size instead of by lattice. It gives the denominator any m=3 oracle at 40 bits must beat:
      the expected number of decompositions per target.
    controls: ["null 1: same group, factor base replaced by a uniformly random subset of E(F_p) of the same size",
               "null 2: random polynomial with S4's support in place of S4 (keeps shape, removes the group)"]
    required_metrics: ["dispersion index with 95% CI", "pair-coincidence rate vs nulls", "rank of degree-<=2 monomial matrix on multi-decomposition targets vs nulls"]
  falsification_conditions:
    - "Null claim falsified if the dispersion index CI excludes 1 at >= 2 sizes for the same delta, or the coincidence excess over null 1 exceeds 3 sigma. That is a positive lead, to be reported with the delta and curve shape."
  confounders: ["the a=0 curve's order-6 automorphism produces orbit-correlated decompositions (expected; count orbits, not points)", "twist x-values (x of points on the quadratic twist) must be excluded from F"]
  interpretation_limits: ["toy p only; transfer to 40-256 bits assumes stationarity in delta, which the three sizes check"]
  heuristic_assumptions:
    - id: H3
      statement: "N_R (number of small 3-decompositions of a random R) ~ Poisson(lambda(B,p))"
      rigorous_support: "Weil/Deligne equidistribution of points on the relation variety in large boxes (imitated below p^(1/2))"
      validation_plan: "1e5 targets x 6 deltas x 3 sizes; empirical vs Poisson pmf, chi-square, and tail check P(N >= 3)"
  target_complexity:
    time_exponent: "n/a (measurement)"
    memory_exponent: "n/a"
    best_known: "n/a"
    hidden_overhead: "none"
    tradeoff_note: "n/a"
  prior_art: {rows_checked: [KR-IC-5931ee], nearest: "Yokoyama et al. statistical assumptions (unverified at these deltas)", relation: extension,
              delta: "measures the assumption in the exact regime between lattice reach and the milestone; also validates the Poisson yield used by section 2.4"}
  estimated_cost: {implementation: low, compute: low}
  recommended_priority: medium
```

### Ranking rationale and what to test first

* **L4-B goes first.** Its Step 1 is a symbolic computation on one 40-bit
  curve and takes minutes. Step 2 is an LP of seconds to minutes. The
  outcome decides whether *any* future "new lattice" proposal can move
  δ's exponent:
  * if P1–P3 hold, every lattice variant is closed for coordinate factor
    bases on prime-order curves (§3.3);
  * if one fails, the failure names the only lattice lead left.

  It is also the cheapest valid discriminator in this note, because it
  needs no lattice reduction. L4-A and L4-D need the support facts P2 that
  L4-B produces before their symmetric-lattice dimensions mean anything.
* **L4-A fills in the measured rows the brief assumed already exist.**
  Information is moderate, since the predictions are fairly confident.
  Cost is medium for m = 4.
* **L4-D asks the right §2.4 question: cost exponent, not threshold.** It is
  cheap. A positive result would matter, but its prior is low.
* **L4-C is the only test aimed at non-lattice structure.** It is very
  cheap. A null result strengthens the closure. A positive result would be
  the only new lead.

## 5. Killed on paper

Every entry is `[derived]` unless marked otherwise. "Reach" means the JM
asymptotic δ in factor-base-size units.

| # | idea examined | mechanism hoped for | why it fails | effect on δ |
|---|---|---|---|---|
| K1 | Möbius-transformed or translated x-intervals; any other degree-2 coordinate | a better-conditioned box | F3: every degree-2 F_p-function is M∘x∘τ_S. Homogenising keeps degree d per variable and the same box | none (≡ JM) |
| K2 | Farey (x = u/v), GLV/lattice-coset (x = u + λv), SNFS base-M digit bases on Solinas primes (x = Σ a_j M^j) | "approximate subfield"; Weil restriction over Z | F4: degree-1 substitution, same box volume, same first-order reach. Exact splitting into several equations over Z needs \|S(...)\| < M, i.e. small x_R and small b: that is F6 (xedni) | none |
| K3 | Torsion symmetrisation (FHJRV), including the "D₄-symmetrised S₅ probe" | lower-degree invariants | needs E(F_p)[2] or [4] ≠ 0, which prime-order curves lack. On even-order curves, quotienting by ⟨T⟩ maps the problem onto E/⟨T⟩ with \|F\| × \|T\| at fixed box: a constant | constant |
| K4 | Interval membership polynomial = falling factorial; Bostan–Gaudry–Schost √B products `[recalled]` | evaluate "∃ root in the box" faster than enumeration | the m-dimensional box product costs B^{m²/(m+1)} (balance s^{m+1} = B/d), which is above enumeration's B^{m−1} by B^{1/(m+1)} | τ = 3.2δ > 3δ at m = 4 |
| K5 | Import many-sample Coppersmith (EC-HNP 1/(d+1), Xu–Sarkar–Wang–Hu 2022 `[literature]`; MIHNP) | shared unknowns raise the reach | F5: those systems have a planted solution. In IC each added independent congruence multiplies the solution count by about B/p, and F1 rules out free equations | n/a |
| K6 | Degree-2-divisor (trace of F_{p²}-points) factor base, small Mumford coefficients (u₁, u₀ ≤ √B) | factor base elements with a 2-parameter description | the relation becomes symmetrised S_{2k+1} in 2k unknowns. Per-element degree is ≥ 2^{2k−2} against 2^{k−1} at equal box volume (sketch; uses the symmetric-degree bound in §3.2) | ≈1/12 vs 1/6 at m = 2 |
| K7 | Points on small lines y = λx + μ (λ, μ ≤ √B) | free relations (each split line gives A + B + C = 0) | the norm over 3 intersection points gives degree 2·6^{m−1} per (λ, μ) pair, effective 6^{m−1} vs 2^{m−1}. The free relations are disjoint triples with no connectivity | ≈1/18 vs 1/6 at m = 2 |
| K8 | j = 0 orbit coordinate u = x³ (secp256k1); Z[ζ₃]-module lattices; grading of S by \|α\| mod 3 when a = 0 | 6-fold smaller factor base | the relation degree in u is 6^{m−1} while \|F\| grows only 6×. Z[ζ]-structure halves the lattice rank and grading splits it into 3 blocks: constants | ≈1/216 at m = 3 (worse) |
| K9 | y-coordinate factor base | different fibre structure | degree-3 function, so relation degree 3^{m−1} > 2^{m−1} (F3) | worse |
| K10 | Small-coefficient models (b = 7); each small x gives a global point on the twist E^{(x³+7)} over Q | integrality / global relations | reach mod p does not depend on coefficient size. Exact vanishing happens only below the rigidity threshold or for global relations (F6). Points on different twists share no Mordell–Weil group | none |
| K11 | Torsion (Teichmüller) lift τ: E(F_p) → Ẽ(Z_p)[n] | a homomorphic lift, so relations hold exactly p-adically and give a second equation mod p² | the first p-adic digit of x(τP) is a Newton step on ψ_n, a rational function of degree about n² in x(P). Smart / Satoh–Araki / Semaev work only when n = p | none |
| K12 | Bit decomposition x_i = Σ 2^k b_ik with b² = b (Boolean variables over F_p) | low-degree "field equations", as over F_{2^n} | after b² = b the polynomial is multilinear with ≥ B^m monomials: a knapsack of density ≫ 1, worse than enumeration. Gröbner on this system belongs to the fall-degree sessions | worse |
| K13 | Targets in a reducible fibre of S_{m+1}(·; z) | lower-degree factors for special targets | for m ≥ 2 the reducible z form a finite set independent of p (generic irreducibility plus constructibility), apart from z = ∞. z = ∞ gives factor-base-only relations via S_m, which need lattice box volume > p^{1/2+δ} against JM's p^{2/((m+1)2^{m−2})} | none |
| K14 | Half-small two-coordinate bases (x(P) ≤ X and x(P+T) ≤ X, X² = pB) | two coordinates of joint size | the unknowns exceed √p, and a bivariate quadratic has Coppersmith reach about p^{1/4} | none |
| K15 | Union factor bases across an isogeny class | larger \|F\| for the same box | within-curve relations leave the cost unchanged (relations needed and found scale together). Mixed relations multiply the degree by ℓ per foreign summand | none / worse |
| K16 | Genus-2 cover Jacobians where decompositions are "free" | Riemann–Roch gives g-term splittings | the decomposition is free but factor-base membership is not. IC on Jac(C) costs Õ(p^{2−2/g}) ≥ p (program note §4.3; Gaudry–Thériault–Thomé–Diem `[recalled]`) | n/a |

Also checked and already closed in the program note, not re-proposed: the
symmetric (e₁, e₂) rewrite of S₃ (§3.2 above shows its asymptote is 1/6,
not 1/9, which changes nothing); multiplicative-subgroup bases; global
lifting / xedni; embedding into an extension; lattice-assisted MITM;
low-degree-map factor bases.

## 6. Relation to the other active sessions

* **Prime-field fall degree / Gröbner** (`research/prime-fall-degree-20261027`,
  `research/fall-degree-bounds-20261008`, `codex/fall-degree-*`).
  * Nothing here proposes a Gröbner run.
  * K12 hands the Boolean-variable encoding to them.
  * If their solving degrees for S₄/S₅ with interval constraints come out
    sub-enumerative, that lies outside F1–F4, which are lattice-specific,
    and would supersede this note's closure for that solver class.
  * I could not read their branches (§2).
* **Residual large-prime IC** (`research/ic_prime_residual_lp_20261026`,
  `lead/ic-residual-lp-20261028`). Large-prime variants change constants in
  the relation phase. They do not change the §3.1 exponent condition,
  because the oracle's τ(δ) is unaffected. Not duplicated.
* **k-sum table** (`research/prime-ksum-table-20261028`). Generic, out of
  scope by the brief. Figure 1B's black line is its exponent.

## 7. Honest accounting (inventor protocol §5)

```yaml
honest_accounting:
  objects:
    - "tracked object: the decomposition tuple (x_1..x_m) as a small point on V(S_{m+1}(.;z)); operation set: none beyond the ideal (S)"
    - "representations examined: K1-K16 (coordinate changes, divisor/line/orbit/bit bases, lifts, covers)"
  lossy_projection_test: >
    No new tracked object is proposed. Of the representations examined, K1, K2 and K11 are lossless
    changes of coordinates (they fail the test). K6-K9 are lossy but raise the degree. Index calculus
    stays Class I partial-action (IDEA-20260806-c5d183). None of K1-K16 escapes KN-OPEN-020: all are
    explicit low-degree descriptions.
  depth_of_verified_structure: "paper-level (derived) only; nothing measured this session"
  dominated_by: "n/a (no result claimed). Rows checked: Pollard rho sqrt(pi n/4); preprocessing rho (S*T^2 ~ n, Probe A); generic IC (m-1)-enumeration; JM asymptotic lattice; McGuire-Mueller O(p log^2 p) (ePrint 2017/1262); naive Semaev IC (KR-IC-5931ee)"
  sota_delta: >
    No attack. Corrected baseline: at feasible dimension (<= 5e3) the S5 reach is about 1/313
    against 1/5 needed (about 63x), and the S4 reach is 1/35.5 against 1/4 (8.9x). Asymptotic
    gaps are 16x and 6x.
  closures:
    - "lattice oracles on coordinate factor bases, prime order: F1+F2+F3+F4 -> shift-set LP; status unverified until L4-B measures P1-P3"
    - "many-sample / overdetermined lattice imports: F5 (no planted solution, no free equations)"
    - "exact-vanishing tricks (small coefficients, digit bases, quadratic orders): F6 (global lifting, xedni)"
    - "K1-K16 individually, each with its mechanism in section 5"
  open_directions:
    - "a non-lattice small-root algorithm for one structured congruence at box volume p^0.7-0.8, which would need a named external ingredient; none found (searches below)"
    - "factor bases whose membership is implicit, high-degree or target-dependent (the KN-OPEN-020 escape), with a polynomial-time membership test and no coordinate-box description"
    - "transfer (program note section 4.3) and Groebner/fall degree (other sessions)"
    - "if L4-C shows over-dispersion: a determinant-method oracle aimed at the observed structure"
```

## 7a. L4-B step 1, run afterwards (measured, 2026-10-28)

The parent session ran L4-B's first step with PARI/GP
([`l4b_step1.gp`](l4b_step1.gp), output [`l4b_step1.out`](l4b_step1.out)).
Setup: the frontier campaign's 40-bit `a = −3` curve
`icv1-fp40-tm924137-0ecaaeb9` (`p = 2⁴⁰ − 213`, `b = 56`); 20 seeded random
`z`; `S₄ = Res_X(S₃(x₁,x₂,X), S₃(x₃,z,X))`. It takes under a second.

- **[measured] P2 holds on every sample.** For all 20 values of `z`, all 8
  vertex coefficients of the box `[0,4]³` are nonzero, so the Newton
  polytope of `S₄(·; z)` is the full box. No sparser support exists for a
  lattice to exploit at `m = 3`.
- **[measured] Irreducible over `F_p` on every sample.** For all 20 values
  of `z`, a restriction to a random line has full degree 12 and is
  irreducible over `F_p`.
- **[not tested] Absolute irreducibility.** Line restrictions cannot decide
  it. A degree-12 restriction that is irreducible over `F_p` splits over
  `F_{p^k}` into `gcd(k, 12)` factors whatever `S₄` does. A first version of
  the script that "tested" `F_{p²}` was wrong for this reason and was
  corrected. Absolute irreducibility of summation polynomials is
  [recalled] a known result (Diem); it was not re-read here.
- **P3 not run.** The automated-Coppersmith linear program of Ding et al.
  (ePrint 2026/1027) has no implementation in this repository. §7c bounds it
  anyway for x-variable lattices.

- **[measured] `m = 4` (`S₅`), the arity where beating rho is possible.**
  [`l4b_step1_s5.gp`](l4b_step1_s5.gp) ([`l4b_step1_s5.out`](l4b_step1_s5.out)):
  `S₅ = Res_X(S₃(x₁,x₂,X), S₄(X,x₃,x₄))` on the same curve, 20 seeded `z`.
  - All 16 vertex coefficients of `[0,8]⁴` are nonzero for all 20 values,
    so P2 holds.
  - A restriction to a random line has full degree 32 and is irreducible
    over `F_p` for all 20 values.

**Reading.** The failure of P2 was the only lattice lead L4-B could open at
`m = 3` or `m = 4`, and P2 holds at both. P1 holds over `F_p`. Only P3, the
linear program, is left open. Under L4-B's claim, every lattice oracle on a
coordinate factor base is then capped at `1/(m(m+1)2^{m−2})`: `1/24` at
`m = 3` and `1/80` at `m = 4`, against the `1/4` milestone and the `1/5`
goal. **Lead 4 is closed for lattice methods on coordinate factor bases**,
unless P3 returns a better shift set than Jochemsz–May. What remains is the
non-lattice space of §7, where this note has no concrete candidate.

## 7b. Lead-4 code and the follow-up probes (measured, 2026-10-28)

Five pieces of native Rust, all on main's crate and with no off-main
dependency:

- [`src/cryptanalysis/semaev_prime_poly.rs`](../../src/cryptanalysis/semaev_prime_poly.rs):
  dense `S₃…S₆` over `F_p` by the GP recursion, plus the structure checks;
- [`examples/semaev_prime_structure.rs`](../../examples/semaev_prime_structure.rs):
  L4-B step 1, natively;
- [`examples/semaev_gap_census.rs`](../../examples/semaev_gap_census.rs): L4-C;
- [`examples/semaev_lattice_reach.rs`](../../examples/semaev_lattice_reach.rs): L4-A;
- [`examples/semaev_shift_search.rs`](../../examples/semaev_shift_search.rs):
  the P3 fallback.

Each probe has a hashed `PROTOCOL.md`, registered before its measured run
(`REGISTRATION.sha256`), and the hashes of the binary and source it ran
(`BINARY.sha256`). Raw outputs are under `*/data/`. Derived tables and
figures come from `*/derive.mjs`, which reads only those outputs.

After the runs, CI's clippy (`-D warnings`) required five lint-only edits
to `semaev_prime_poly.rs` and two to `examples/semaev_gap_census.rs`:
`is_multiple_of`, `div_ceil`, `repeat_n`, and `2·d < len` for
`2·d ≤ len − 1`. Each edit computes the same values, and the 6 unit tests
still pass. The source hashes in the probes' `BINARY.sha256` refer to the
sources as run, at commit f91405e.

### 7b.1 The GP checks, ported (L4-B step 1, native)

`semaev_prime_poly` builds `S_{m+1}(x₁…x_m; z)` as
`Res_X(S₃(x₁,x₂,X), S_m(X,x₃,…; z))`, with formal-degree Sylvester
resultants and tensor interpolation.

- **[measured] The values match PARI/GP exactly.** The unit test
  `values_match_pari` checks S₃, S₄ and S₅ at three points each on the
  40-bit curve, against `polresultant` output.
- **[measured] `S₄` and `S₅` vanish on real sums.** Tested at
  `x(P₁+P₂+P₃)` and `x(P₁+…+P₄)`.
- **Irreducibility over `F_p`.** It is decided by intersecting factor-degree
  patterns of line restrictions (distinct-degree factorisation). A factor of
  total degree `a` forces `a` to be a subset sum on every full-degree line.
  This replaces the GP script's "one irreducible line" test. That test
  needs about `n` lines for a degree-`n` restriction, and in a first native
  run it missed for `S₅` (degree 32) within 60 lines.
- **[measured, `l4b/native_step1.jsonl`]** On the same curve and the same
  count (20 seeded `z` per arity): `S₄` and `S₅` have the full box (8/8 and
  16/16 vertices nonzero on 20/20 samples). They are irreducible over `F_p`
  on 20/20, settled within at most 8 lines for `S₄` and 6 for `S₅`.
  - New: the polynomials are **completely dense**. All 125 coefficients of
    `S₄(·; z)` on `[0,4]³` and all 6561 of `S₅(·; z)` on `[0,8]⁴` are
    nonzero on every sample.
  - It takes 0.1 s (`S₄`) and 14 s (`S₅`) for all 20 values of `z`.
- **[derived] Simplex vertices.** For the symmetrised form `g(e)`, the
  vertex coefficient of `e_i^D` equals the box coefficient of
  `Π_{j≤i} x_j^d`. That is the only `x`-monomial of that multidegree among
  `e^β` with `|β| ≤ D`. So box vertices nonzero implies simplex vertices
  nonzero, which is the premise §7b.4 needs.

### 7b.2 L4-C: is there structure in the gap? (census, [`l4c/`](l4c/))

The protocol changed the README record in three ways before any data:

- an exact census over all `r − 1` targets replaces 10⁵ samples;
- the counting unit is fixed: signed multisets summing to `R`;
- null 2 is dropped, because its expected root count is below 10⁻² per
  cell.

A 20-bit smoke run, before registration, showed that a per-target Poisson
null is wrong for a finite factor base. Its triple sums collide only
through short additive relations, which come in clumps. So the registered
comparison is against null 1 (five random factor bases of the same size),
with the primary statistic `triple_unshared`: 6-term relations among the
factor base.

- **Panel.** Six prime-order curves (`a = −3` and `a = 0` at 26, 28 and 30
  bits), with δ ∈ {1/24, 1/12, 1/8, 1/6, 1/5, 1/4, 0.3}. That is 41 cells
  (one skipped for memory, as registered), 246 censuses.
- **[measured] Null result.** In all 41 cells, the small-x values of
  `triple_unshared`, `pair_collisions` and `ge2` lie inside the registered
  band (null-1 range ± 3σ). No (shape, δ) is outside on the same side at
  two sizes. The falsifier did not fire.
- **[measured] δ ≤ 1/5 is uninformative.** Every count is zero, for the
  small-x and the null bases alike, as the protocol's limits anticipated.
  The informative cells are δ = 1/4 and 0.3 (Figure 2).
- **Reading.** Up to the toy sizes tested, small-abscissa factor bases have
  no more short additive relations than random factor bases of the same
  size. There is no gap structure for a non-lattice oracle to target. This
  supports the Poisson-yield assumption in §2.4 and does not reopen lead 4.

![Figure 2. L4-C: 6-term relations among the factor base, small-x vs five null-1 bases (exact census over all targets; band = registered null range ± 3σ). Source: l4c/analysis/l4c.svg.](l4c/analysis/l4c.svg)

### 7b.3 L4-A: measured S₄ lattice reach ([`l4a/`](l4a/))

Symmetric JM lattices for `S₄`:

- `g(e₁,e₂,e₃)` is found by a 35-unknown linear solve, checked on 6 extra
  points;
- the lattice is triangular in `(β₃, β)`, with `g` monic in `e₃⁴`;
- reduction uses main's `lattice::lll_reduce`.

A timing pilot fixed the scope before registration:

- dim 35 takes about 20 ms;
- dim 165 takes 116 s, about 200 s under load;
- no dim-455 reduction finished in 5 h 10 min ([`l4a/pilot/PILOT.md`](l4a/pilot/PILOT.md)).

So **ℓ ≥ 3 at m = 3, and all of m = 4, stay `[derived]` only.**

Measured cells:

- **ℓ = 1 (dim 35):** 32, 40 and 48 bits; B ∈ {1, 2, 3, 4, 6, 8, 12, 16}; 8 planted and 8 unplanted targets per cell.
- **ℓ = 2 (dim 165):** 32 and 40 bits; B ∈ {1, 2, 3, 4, 6}; 4 planted and 4 unplanted per cell.

**[measured] v1: the registered falsifier fired, on a planting defect.** At ℓ = 2 on 40 bits, B = 4 succeeded on 3 of 4 targets and B = 3 on 2 of 4, while the §3.2 bound is B ≈ 1.7.

- PARI/GP shows that **all 8 distinct successful planted targets** in v1, across every cell, satisfy `S₄(x; z) = 0` over ℤ ([`l4a/succ.gp`](l4a/succ.gp), [`l4a/succ.out`](l4a/succ.out)).
- They have `z ∈ {1, 2, 3, 25}`, and most are trivial `P − P + Q = Q` decompositions.
- Cause: small x's repeat, and the planting rule accepted any root. Any lattice that contains S₄ finds such roots automatically, which is F6 global lifting, not modular reach.
- The v1 data, protocol and fired falsifier are kept ([`l4a/data-v1/`](l4a/data-v1/), Figure 3b). [`AMENDMENT-1.md`](l4a/AMENDMENT-1.md), hashed before the rerun, redraws planted roots that vanish modulo the independent prime 2⁶¹ − 1 and changes nothing else.

**[measured] v2 (amendment 1): no planted success in any cell.**

| bits | ℓ | dim | planted success, all B | unplanted hg_holds | measured reach | §3.2 bound B_ℓ | median LLL time |
|--:|--:|--:|:--|:--|:--|--:|--:|
| 32 | 1 | 35 | 0/64 | 0/64 | B < 2 | 1.11 | 8–19 ms |
| 40 | 1 | 35 | 0/56 (B = 1: no non-global root) | 0/64 | B < 2 | 1.14 | 9–22 ms |
| 48 | 1 | 35 | 0/64 | 0/64 | B < 2 | 1.17 | 10–24 ms |
| 32 | 2 | 165 | 0/20 | 0/20 | B < 2 | 1.50 | 46–131 s |
| 40 | 2 | 165 | 0/16 (B = 1: no non-global root) | 0/20 | B < 2 | 1.66 | 66–178 s |

Every reduction costs far more than the `(B + 1)²` enumeration it would replace: 46–178 s against at most 49 candidates at ℓ = 2.

**Reading.** The measured m = 3 reach agrees with the §3.2 determinant bounds. They predict B < 2 at both levels and all three sizes, and v2 finds no success at B ≥ 2. There is no slack beyond the bound, unlike the up-to-2.5× slack Probe B saw at m = 2. No falsifier fired in v2. The m = 3 rows at ℓ = 1 and 2 are now `[measured]`; ℓ ≥ 3 and all of m = 4 remain `[derived]`. The v1 episode is a lesson for any future planted-root test: exclude global relations, or a lattice "succeeds" on them by construction.

![Figure 3a. L4-A v2: planted-root success of symmetric JM lattices for S₄ against the root bound B, with global relations excluded (zero in every cell). Source: l4a/analysis/l4a.svg.](l4a/analysis/l4a.svg)

![Figure 3b. L4-A v1 (superseded): the apparent successes, every one a global relation S₄(x; z) = 0 over ℤ. Source: l4a/analysis/l4a-v1.svg.](l4a/analysis/l4a-v1.svg)

### 7b.4 P3 fallback: our search over triangular shift lattices ([`p3/`](p3/))

**What this is not.** P3 names the LP of Ding et al. (ePrint 2026/1027).
Its PDF is behind a Cloudflare browser challenge this session does not
pass, so that LP is **not implemented here**.

**What was run instead.** An exact count over an explicit family of
triangular shift lattices:

- every leading vertex of the Newton polytope;
- monomial sets made of rectangles with extended caps, cut by `|β| ≤ s` or
  by one `{0,1,2}` half-space;
- `k(β)` maximal subject to the shifts staying in the set.

The score is the determinant bound `δ = Σk / Σ⟨w,β⟩`, without dimension
factors. The code reproduces every §3.2 JM value exactly (`jm_set_delta =
jm_formula` in all rows). That covers the m = 4 symmetric values: 1.26·10⁻⁴,
1/313 and 1/184.

| shape | m | best δ found (dim) | best δ / δ_JM at equal dimension | asymptote | exceeded |
|:--|--:|:--|:--|--:|:--|
| simplex (e) | 3 | 0.0326 (3642) | 1.078 at dim 56 | 1/24 = 0.0417 | no |
| box (x) | 3 | 0.0306 (15625) | 1.010 at dim 1331 | 0.0417 | no |
| simplex (e) | 4 | 0.0061 (64065) | 1.032 at dim 495 | 1/80 = 0.0125 | no |
| box (x) | 4 | 0.0048 (390625) | 1.002 at dim 83521 | 0.0125 | no |

- **[derived by computation] No lattice in the family exceeds the
  asymptote.** At equal dimension the best gain over the JM curve is
  **≤ 8 %**, at small dimension only. Above a few hundred it is ≤ 3 %.
  These are extended-strategy shifts, not a new exponent (Figure 4).
- **Reading.** This is consistent with F1–F4 and with L4-B's conditional
  closure. It is a finite family, not the LP, so P3 remains formally
  **open**. The ePrint's formula, read and run, is the only thing that
  could still change it.

![Figure 4. P3 fallback: δ against dimension for our shift-lattice family (lines) and the JM levels (squares), with the asymptotes. Source: p3/analysis/p3.svg.](p3/analysis/p3.svg)

### 7b.5 Where lead 4 stands

| premise / probe | status |
|:--|:--|
| P1, irreducible over F_p | measured: GP and native, 20/20 at m = 3 and 4 |
| P1, absolutely irreducible | not decidable by line restrictions; recalled (Diem) |
| P2, full box | measured: GP and native, dense, 20/20 |
| P3, automated-Coppersmith LP | open; our finite search finds nothing past the JM asymptote |
| L4-A, measured reach | measured at m = 3, ℓ ≤ 2: no success at B ≥ 2, matching §3.2 (v1 false positive: global relations, amended) |
| L4-C, gap structure | measured: null, 41/41 cells inside the band |
| L4-D | not run |

Lead 4 stays **closed for lattice oracles on coordinate factor bases**,
conditional only on P3. No measured cost changed, so this is not an
improvement under the success criterion, and no dashboard point is added
(AGENTS §7a).

## 7c. Addendum (2026-10-29): a bound on every shift strategy, the P3 LP included

`research/smallroot_optimal_reach_20261026` (merged 2026-10-26) proves this
for one polynomial `f` modulo `p` in `n` unknowns with equal bounds
`|x_i| < p^δ`. Every Coppersmith lattice whose rows lie in `(p, f)^t`, on
the lattice points of a convex monomial set, satisfies Howgrave-Graham only
if

`ε = n·δ ≤ (n! · vol Newt(f))^{−1/n}`.

Its §2 gives the argument: regular sequence, Ostrowski, Brunn–Minkowski. It
covers Jochemsz–May, Ryan's optimal shifts and any LP-chosen shift set,
because all of them are sublattices of `L(M)`. The proof drops dimension
factors, which favours the attack.

- **[derived] Both premises hold here.**
  - The small-x factor base gives every `x_i` the same bound `B`.
  - L4-B measured the Newton polytopes. `Newt(S₄(·; z))` is the full box
    `[0,4]³` (volume 64), and `Newt(S₅(·; z))` is the full box `[0,8]⁴`
    (volume 4096), on 20/20 values of `z` (§7a, §7b.1).
- **[derived] The bound.** The formula reproduces the study's S₃ value of
  0.3293 (`vol = 14/3`, `n = 3`). For this note's targets it gives:

| polynomial | n | vol Newt | ε bound | per-variable δ bound | target δ | short by |
|:--|--:|--:|--:|--:|--:|--:|
| S₄ (m = 3) | 3 | 64 | 0.1376 | 0.0459 = 1/21.8 | 1/4 (milestone) | 5.5× |
| S₅ (m = 4) | 4 | 4096 | 0.0565 | 0.0141 = 1/70.8 | 1/5 (goal) | 14.2× |

  The bounds sit just above the Jochemsz–May asymptotes, 1/24 and 1/80, as
  an upper bound should. The P3 fallback's best values, 0.0306 at m = 3 and
  0.0048 at m = 4 (x-box), sit below them.

**What this closes, conditionally.** Assume the cited theorem holds. Then the
"real P3 LP" left open in §0 and §7a cannot reach either target with
x-variable lattices on convex monomial sets. That holds for every shift
strategy, not only the triangular families searched in §7b.4. The closure
rests on the cited study's written proof, which is not machine-checked
(next paragraph).

**Formalization status (AGENTS.md "Mathematical results should include Lean
proofs").** The only new mathematics in §7c is a corollary: the cited theorem
applied to measured volumes, followed by arithmetic. Proof map:

| step | statement | Lean declaration | status |
|:--|:--|:--|:--|
| T (cited) | `n·δ ≤ (n!·vol Newt f)^{−1/n}` for `(p, f)^t` lattices on convex monomial sets, equal bounds | none | **not formalized**. Missing: Newton polytopes, lattice determinants of `(p, f)^t`, Howgrave-Graham and Brunn–Minkowski, none of which is in core Lean (the `crypto-lean` library was not surveyed for them). The cited study ships no Lean either. |
| P (measured) | `Newt(S₄(·; z)) = [0,4]³` and `Newt(S₅(·; z)) = [0,8]⁴` on the 20/20 seeded `z` | none | computational evidence (L4-B), not a theorem for all `z` |
| R (bridge) | for positive reals, `(n!V)^{−1/n}/n ≤ 1/k ⟺ k^n ≤ n^n·n!V` | none | not formalized (real n-th roots need Mathlib); elementary |
| A (arithmetic) | `21³ ≤ 3³·3!·64`, `70⁴ ≤ 4⁴·4!·4096`, `(5·4)³ ≤ 3³·3!·64`, `(14·5)⁴ ≤ 4⁴·4!·4096`; not `22³ ≤ …`, not `71⁴ ≤ …` | `PrimeS5SmallRoot.s4_reach_le_1_21`, `s4_misses_quarter_by_5x`, `s5_reach_le_1_70`, `s5_misses_fifth_by_14x`, `s4_not_le_1_22`, `s5_not_le_1_71` in [`lean/ReachArithmetic.lean`](lean/ReachArithmetic.lean) | **checked**. Lean 4.34.1 core, `by decide`; `#print axioms` reports no axioms for all six |

This is partial formalization. T stays a written proof, and the closure is
reported as conditional on it.

**What it does not close.**

- **The symmetric e-form.** Its bounds `C(m,i)·B^i` are unequal, and for
  unequal bounds the theorem bounds only `∏ δ_i`. The cited study's
  numerical optimiser found nothing above 1/2 for S₃ there. §7b.4 found no
  e-form family above the JM asymptote. A proof for the e-form is still
  missing.
- **Non-convex monomial sets.**
- **Lattices that use more than the one ideal `(p, S_{m+1})^t`,** for
  example several targets' polynomials at once.

These are the remaining lattice items. They are listed in the cited study's
§5 for S₃ and carry over here.

## 8. Sources

Each entry is marked with how far it was read.

* `[internal]` `RESEARCH_PRIME_FIELD_BREAKTHROUGH_PROGRAM.md` (2026-10-08):
  §2.1–2.4 cost model and JM table; Probe B/C tables; §4.6 closures.
* `[internal]` `RESEARCH_IC_LEADS_AND_CONNECTIONS_20261010.md` §8–§10
  (worktree copy).
* `[kb]` `crypto-autoresearcher` frontier rows KR-IC-5931ee and KR-IC-5a43e5;
  KN-LIT-d8e1b9 (Yokoyama, Yasuda, Takahashi, Kogure, *J. Math. Cryptol.* 14
  (2020) 460–485, doi:10.1515/jmc-2019-0029).
* `[retrieved, 2-page abstract read]` G. McGuire, D. Mueller, "A few more
  index calculus algorithms for the ECDLP", ePrint 2017/1262 (Caen 2018
  abstract): O(p log² p), Gröbner-free. Its reference list confirms
  Amadori–Pintore–Sala ePrint 2017/609 and Faugère–Huot–Joux–Renault–Vitse,
  EUROCRYPT 2014, LNCS 8441, 40–57.
  https://nitaj.users.lmno.cnrs.fr/Caen2018/DanielaMuellerCaen2018.pdf
* `[retrieved, abstract]` J. Hu, "Implementation analysis of index calculus
  method on elliptic curves over prime finite fields", ePrint 2024/1923.
  https://eprint.iacr.org/2024/1923
* `[retrieved, abstract]` Y. Aono, M. Agrawal, T. Satoh, O. Watanabe, "On the
  optimality of lattices for the Coppersmith technique", ePrint 2012/108;
  ACISP 2012; AAECC 29(2) 2018. https://eprint.iacr.org/2012/108
* `[retrieved, abstract]` J. Xu, S. Sarkar, H. Wang, L. Hu, "Improving bounds
  on elliptic curve hidden number problem for ECDH key exchange",
  Asiacrypt 2022, ePrint 2022/1239. https://eprint.iacr.org/2022/1239
* `[retrieved, search abstract]` K. Meers, J. Nowakowski, automated
  Coppersmith, Asiacrypt 2023, ePrint 2023/1409.
  https://eprint.iacr.org/2023/1409
* `[retrieved, abstract]` Z. Ding, Z. Dai, B. Wu, Y. Zhang, K. Zhang,
  "Computing asymptotic bounds for the automated Coppersmith method via
  linear programming", ePrint 2026/1027. https://eprint.iacr.org/2026/1027
* `[retrieved, search abstract]` M.-C. Chang, J. Cilleruelo, M. Garaev,
  J. Hernández, I. Shparlinski, A. Zumalacárregui, "Points on curves in
  small boxes and applications", arXiv:1111.1543.
  https://arxiv.org/abs/1111.1543
* `[recalled]` I. Semaev, ePrint 2004/031. E. Jochemsz, A. May, Asiacrypt
  2006. D. Coppersmith, J. Cryptology 1997. Bostan–Gaudry–Schost, SIAM J.
  Comput. 2007. Ostrowski's theorem on Newton polytopes of products.
  Jacobson–Koblitz–Silverman–Stein–Teske, DCC 2000 (xedni).
  Petit–Kosters–Messeng, PKC 2016. Gaudry–Thériault–Thomé–Diem (genus-g
  double large prime).
* **Searches that found nothing beyond the above** (2026-10-28):
  * "summation polynomials prime field … Coppersmith small roots lattice
    index calculus";
  * "ePrint 2023 2024 2025 index calculus elliptic curves prime field
    summation polynomial";
  * "elliptic curve hidden number problem x-coordinate Coppersmith 2020–2023".

  None of them turned up a small-root method for summation polynomials past
  the JM reach, or any sub-√p prime-field algebraic ECDLP result. Hu 2024
  states that no subexponential method is known.

## 9. Files and rendering

* `README.md`: this report.
* `delta_arity_map.svg`: Figure 1, hand-written and editable. Every
  coordinate follows the formula in its header comment.
* `delta_arity_map.png`: the figure rendered with
  `rsvg-convert -w 2160 delta_arity_map.svg -o delta_arity_map.png`.
* `report.pdf`: rendered from this file with every figure link pointed at its
  PNG (`pandoc … --pdf-engine=typst`), after §7b was added.
* `l4b/`, `l4c/`, `l4a/`, `p3/`: one directory per §7b probe. Each holds
  `PROTOCOL.md` (with `AMENDMENT-1.md` for L4-A), `REGISTRATION.sha256`,
  `BINARY.sha256` (binary and source hashes), raw `data/`, `derive.mjs` (a
  thin Node derivation over the raw data; tooling, not research code) and
  `analysis/` (tables, editable SVG figures, PNG renders made with
  `rsvg-convert -w 2160`).
* The native code lives outside this directory:
  `src/cryptanalysis/semaev_prime_poly.rs` and the four `examples/semaev_*.rs`
  programs named in §7b.
