# Prime-field ECDLP via summation polynomials: Amadori–Pintore–Sala evaluated, and what can be built on it

**Date.** 2026-10-24. **Scope.** The paper "On the discrete logarithm problem for prime-field elliptic curves" (Amadori, Pintore, Sala; Finite Fields Appl. 51 (2018) 168–182; IACR ePrint 2017/609; accepted manuscript on the Trento IRIS repository), its follow-ups, the surrounding prime-field summation-polynomial literature, and a design study of what can be built on it. Everything measured or derived here is labelled; nothing in this report claims a sub-√p algorithm.

**Sources.** Four literature lanes (notes in `lanes/` beside this file: `aps2018_dissection.md`, `prime_field_barriers.md`, `transferable_and_recent.md`, `prior_art_new_ideas.md`, plus my `coordinator_math_notes.md`), the repos' own notes (`RESEARCH_PRIME_FIELD_BREAKTHROUGH_PROGRAM.md`, `RESEARCH_PRIME_FAST_ECDLP.md`, `RESEARCH_SEMAEV_ROOTFIND_VS_GROEBNER.md`, hypothesis `H-ICEX-6ca21f`, frontier map), and four small computations run today in Sage/PARI (Appendix A).

---

## 0. Verdict

1. **The suspicion does not survive the read.** APS 2018 contains exactly two ideas beyond the standard pipeline: (i) a factor base made of random points `R_j = u_jP + v_jQ` with *known* log coordinates, so that **one** vanishing signed sum of `m` base points already gives the logarithm, and (ii) a partition of that base into `m` disjoint parts to kill trivial solutions. Everything else they do (Gröbner in grevlex on `S_m = 0, f_i(X_i) = 0`; splitting `S_4`, `S_5` into chains of `S_3` with auxiliary `Y`) is standard and is already in the repos. The follow-up by the same community (Kudo–Yokota–Takahashi–Yasuda, CANS 2018) added the hybrid method, the `(t_1,t_2) = (x_1+x_2, x_1x_2)` symmetrisation and GCD-based solving; the last of these is literally the repo's direct-subtraction root-finding oracle. Yokoyama–Yasuda–Takahashi–Kogure (J. Math. Cryptol. 2020) then proved, under two statistical assumptions they checked to 25 bits, that this whole family costs at least `m·2^{m−1}·d^{m−1}` field operations per system (`d` = per-variable base size), i.e. the naive method "cannot be more efficient than even the brute force method". APS themselves write "We do not claim" to beat `p^{1/2}`.

2. **Why there is nothing to transfer.** The two APS ingredients are mutually exclusive with the one thing a decomposition oracle needs: algebraic structure on the base. Known logs ⇒ random `x`-coordinates ⇒ the constraint ring is `F_p^{B^m}` by the Chinese remainder theorem ⇒ every algebraic solver is a change of basis from grid evaluation (this is the CRT argument already recorded in `H-ICEX-6ca21f`, and it is Yokoyama et al.'s Lemma 8 in substance). Conversely, a structured base has unknown logs, so one relation is useless and `B` relations are needed. Worse, "find one signed `m`-sum of random group elements that vanishes" is the `k`-sum problem in `E(F_p)`, and Wagner's Theorem 2 (W. Dai) shows a `k`-sum solver in a cyclic group yields a DL solver in the same time, so any generic `k`-sum algorithm costs `Ω(√p)`. The one-relation trick is a constant-factor reorganisation inside the generic class.

3. **The prime-field barrier is sharper than the repos currently state, in three places** (§3): (a) a Lang–Weil/Bézout lemma closes the "images of low-degree maps" loophole: any subset of `F_p` of size `B ≪ p/D` that is the projection of the `F_p`-points of a variety cut out by degree-`≤ D` polynomials has Bézout cost `≥ B`, and its constraint algebra is `F_p^{B^m}` whether it is presented as one split polynomial or as a chain of low-degree maps (PKM's chains buy nothing — PKM themselves observed Semaev's split system was easier than theirs); (b) the Jochemsz–May lattice reach for a modular polynomial with Newton polytope `N` is `δ_max = 1/((m+1)·c_N)` with `c_N` the coordinate sum of the centroid of `N`, and I verified in Sage that `S_{m+1}` with one variable fixed has the *full box* as support (9/9, 125/125, 6561/6561 monomials), so the repo's shortfall table (3×, 6×, 13×, 30× for `m = 2..5`) is exact for the basic strategy and cannot be improved by polytope-aware constructions; (c) the "product/norm" paradigm (decide the PDP as a norm `N_V(z) = ∏_{u∈V^m} S_{m+1}(u,z)` from a split algebra), which is cheap in one dimension (Bostan–Gaudry–Schost `Õ(√B)` for intervals, `Õ(log B)` for subgroups), is blocked in two or more dimensions at `Õ(B^{3/2})`–`Õ(B^{4/3})`, i.e. above the enumeration cost `B`, with no known multidimensional analogue; I also checked numerically that the double product is dense (no hidden sparsity) for both base types.

4. **What is genuinely available** (§4): a short list of precisely stated open problems whose solution *would* change the exponent (I put each at a few percent); a constant-factor program for special prime-field curves (`j = 0` orbits, rational 2-/4-torsion symmetrisation) that is correct, implementable, and fits the repo's stated success criterion, but is bounded by `|Aut| ≤ 6` on columns and `2^{m−1}` on signs; several new closures worth recording in the ledger so nobody re-derives them; and the observation that the only summation-polynomial ideas from this literature with *measured* upside live in the binary-field program (FHJRV/Galbraith–Gebregiyorgis invariants, never built there), not over `F_p`.

---

## 1. What Amadori–Pintore–Sala actually do

Notation follows the accepted manuscript (AM). `|E(F_q)| = r` prime, `Q = wP`. APS's `m` counts **all** points in a relation (they solve `S_m`), so APS "`m = 3`" is the degree analogue of the standard two-point decomposition `R = P_1 + P_2` (`S_3(X_1,X_2,x(R))`); keep this shift in mind when comparing with PKM or the repos, which use `S_{m+1}` for `m` base points plus a target.

**Relation collection (AM §3).** Fix `m` and `s` with `s^m ≈ q`. The factor base starts empty; random `R = uP + vQ` are appended until `|F| = s`. "R does not need to be written as a sum of multiples of points in F, since R itself is a point of F."

**Relation solving (AM §3, §3.1).** Partition `F = F_1 ⊔ … ⊔ F_m` into equal parts, `V_i = x(F_i)`, `f_i(X_i) = ∏_{v∈V_i}(X_i − v)` of degree `≈ s/m`. Solve system (11)

```
S_m(X_1,…,X_m) = 0,   f_1(X_1) = 0, …, f_m(X_m) = 0
```

by a Magma Gröbner basis in grevlex (no algorithm, version or extraction method stated). A solution identifies `±P_i ∈ F_i` with `P_1 + ⋯ + P_m = ∞` (eq. 8), hence `λP + µQ = ∞` with `λ = Σ ε_i u_{j_i}`, `µ = Σ ε_i v_{j_i}`, and `w = −λ/µ mod r`. If the system has no solution, the whole base is redrawn. For `m = 4, 5` they replace `S_4`, `S_5` by `{S_3(X_1,X_2,Y), S_3(X_3,X_4,Y)}` and `{S_3(X_1,X_2,Y), S_4(X_3,X_4,X_5,Y)}` with an auxiliary `Y`, citing Huang et al., Karabina and Semaev 2015. The partition "breaks the symmetry and avoids trivial solutions when `m` is even" (AM p. 7) and is credited to Galbraith–Gebregiyorgis.

**Cost model (AM §3.2, all heuristic).** Expected number of `m`-sums `≈ (s/m)^m`; success probability per system `s^m/(q·m^m)` (eq. 12); total cost `(q·m^m/s^m)·T(E,m,V)` where `T` is the cost of one system. With `s^m ≈ q` this is `≈ m^m` Gröbner computations per DLP (27, 256, 3125 for `m = 3, 4, 5`), independent of `q`. "In order to reach an improvement with respect to algorithms for generic cyclic groups, this complexity should be smaller than `r^{1/2}`. We do not claim this result. Indeed our complexity analysis is partial, since we are unable to estimate the complexity of solving our polynomial equation systems." No degree of regularity, Macaulay bound or exponent appears anywhere in the paper.

**The PKM comparison (AM §3.3, Table 1).** They transcribe PKM's cost as `(p·m!/s^{m−1})·T' + s^ω`, assume `T ≈ T'` (eq. 13, explicitly unproven), and conclude APS beats PKM once `s·m! > m^m`, i.e. `p^{1/m} > m^m/m!` (7, 14, 24, 37, 52, 70 bits for `m = 3..8`; these reproduce). Assumption (13) equates structurally different systems (APS: `m` unknowns with one degree-`q^{1/m}/m` generator each; PKM: many unknowns, all of low degree). The "Petit et al." column of their Table 2 is PKM's *per-system* time for a two-point decomposition at `|V| ≈ p^{1/2}`, compared against APS's *per-DLP* time at `|F| ≈ p^{1/3}`; the even/odd-bit attribution of PKM's rows is also reversed relative to PKM's Tables 4/5. The "heuristic corroboration" of (13) rests on this apples-to-oranges comparison.

**Experiments (AM §3.4, Table 2).** `p` of 11–22 bits, `m ∈ {3,4,5}`, 100 curves × 10 instances, Magma, Xeon 5460; at 22 bits: 267.7 s (`m=3`, `s=146`), 339.9 s (`m=4`, `s=43`), 388.0 s (`m=5`, `s=21`). From 20 to 22 bits the `m=3` time grows ≈ 3.2× per bit, i.e. roughly `∝ p^{1.6–1.8}` over that range. No success rates, memory, degrees of regularity or system counts are reported.

**What they leave open (AM §4).** The complexity of system (11); whether non-Gröbner solvers are better; the composite-field case. They also write that for prime fields the obstacles are "the difficulty to endow F with an algebraic structure, and the impossibility to exploit the Weil descent".

**The three papers that settle the family.**

- *McGuire–Mueller, ePrint 2017/1262 (rev. 2018).* Same random base. Heuristic Result 6.5/6.6: the Gröbner cost of APS's system is `O(p^{ω−ω/m})` by the Macaulay bound (`O(p^2)` for `m = 3, ω = 3`, "roughly agrees with our experiments": 96 384 s at `p = 30 056 657`); Remark 6.4: the base must be regenerated `m^m/2^{m−1}` times, "so … several Gröbner basis computations and not only one as is claimed". Their Algorithm 3.1 (evaluate `S_m` on all multisets of `V`) costs `O(p log² p)`, and Algorithm 4.1 (**sum `m−1` base points, check whether the result is in `F`**) costs `O(p)` and is "the best index calculus algorithm for prime order fields at the present time"; their fast evaluation of `S_m` is a Sylvester-determinant recursion, `O(log² p)` per point for fixed `m`, independent of any structure of `V`. Verdict: "all these algorithms are worse than the well known square-root algorithms such as Pollard-Rho."
- *Kudo–Yokota–Takahashi–Yasuda, CANS 2018* (full text behind a paywall; content via its abstract and Dzierzkowski–Wroński 2024 §3.2.4): hybrid method (Bettale–Faugère–Perret: fix some variables, Gröbner on the rest), symmetrisation `t_1 = x_1 + x_2, t_2 = x_1x_2` (total degree 4 → 2 for `S_3`), and "solving via GCD computation, where efficient computation of `GCD(f_3(x_1, x_Q, x_R), f(x_1)) ∈ F_p[x_1]` is used"; the authors "discuss a limitation"; Dzierzkowski–Wroński state the accelerated variant's complexity "is at least `p^{2/3}`". Yokoyama et al. summarise: this study "showed that both methods of [APS, PKM] do not outperform generic algorithms".
- *Yokoyama–Yasuda–Takahashi–Kogure, J. Math. Cryptol. 14 (2020) 460–485.* For `S_{m+1}(x_1..x_m, x(aP+bQ)) = 0, F(x_i) = 0` with `F | x^q − x` of degree `d > δ = 2^{m−1}`: Lemma 6 (unnecessary signatures), Lemma 8 (any S-polynomial algorithm must compute `≥ (d^m − (d−δ)^m)^{1−ε}` S-polynomials, `≥ m·d^{m−1}` for `d > δ ≥ 4`), Proposition 9 (`≥ (m·d^{m−1})^{1−ε}` field operations), under Assumption 7 (semi-normality) and Remark 8 (signature-based algorithms are the most efficient), both checked experimentally to 25 bits. Consequence (§4.1.3): total cost `≳ m!·m·q`, more precisely `> q^{m(1−ε)/(m−1)}`: "cannot be more efficient than Pollard's rho method … cannot be more efficient than even the brute force method". Their mechanism — the cofactor `T` in `1 = T·S + Σ A_i F(x_i)` is the Lagrange interpolant over the `d^m` points of `V(⟨F(x_1),…,F(x_m)⟩)` with leading monomial `x_1^{d−1}⋯x_m^{d−1}` — is the CRT/`F_q^{d^m}` argument of `H-ICEX-6ca21f` in substance. They test random-rooted `F`, `F = x^k − 1` (`k | p−1`, i.e. the subgroup base) and `x^{k−1}+⋯+1`; all behave alike (`#G* ≈ 2.1·m·d^{m−1}`).

Applied to APS's own parameters (`d = s/m ≈ q^{1/m}/m`, `δ = 2^{m−2}`, `m^m` systems): total `≳ m^m · m·δ·(q^{1/m}/m)^{m−1} ≈ m²·2^{m−2}·q^{(m−1)/m}`, i.e. `≈ 18·q^{2/3}` at `m = 3`, consistent with the "at least `p^{2/3}`" quoted for the Kudo variant, and `→ q` as `m` grows. There is no exponent below 1/2 anywhere in this family.

---

## 2. Technique-by-technique transfer audit

The question was whether APS's techniques are "applicable to what we can do and improve greatly". Here is every technique in APS and its two accelerations, with its status.

| # | Technique (source) | What it is | Status for the repos | Why |
|---|---|---|---|---|
| 1 | On-the-run base of known-log points `u_jP + v_jQ` (APS §3) | base elements carry `(u_j, v_j)` | **Generic-bound; closed** (`H-ICEX-6ca21f` CRT argument; now also Wagner Thm 2) | random `x`-coordinates ⇒ constraint ring `F_p^{s^m}`; relation search = `k`-sum in a generic group ⇒ `Ω(√p)` |
| 2 | One relation suffices (APS §1) | no linear algebra, no `B` relations | **Generic-bound; closed** | only works with #1; saves a factor `m!·q^{1/m}/m^m` in the *count* of solves, each solve `≥ m·δ·d^{m−1}` (YYTK) |
| 3 | Disjoint partition `F = ⊔F_i` (APS §3.1; Matsuo / Galbraith–Gebregiyorgis idea) | kills `P + (−P)` solutions for even `m`, breaks `S_m` symmetry | **Constant factor; known** (GGMP §2.3: `(m−1)!` saving, `m²` linear-algebra penalty) | over `F_p` the base has unknown logs, so the `m²` penalty is paid; in the binary program the equivalent is coset-partitioning of the subspace (see §4.4) |
| 4 | `Y`-splitting of `S_4`, `S_5` into `S_3`-chains (APS §3.4, after Karabina/HPST/Semaev 2015) | lower degree, more variables | **Already in the repos** (chained systems, `build_decomposition_system`) | — |
| 5 | Gröbner in grevlex on split univariate constraints (APS §3) | the naive PDP solver | **Dominated; closed** (repo note of 2026-10-12: 35 000× slower than root finding at `|F| = 6`; YYTK lower bound) | CRT: the ideal is grid evaluation |
| 6 | Hybrid: fix `k` variables, Gröbner on the rest (Kudo 2018, after Bettale–Faugère–Perret) | enumeration × algebra | **Dominated** | fixing `m−2` variables and solving the last two costs `≥ B` each by CRT ⇒ `B^{m−1} > B^{⌈m/2⌉}` (MITM); the repo's `mitm` oracle is strictly better |
| 7 | `(t_1, t_2)` symmetrisation of `S_3` (Kudo 2018; FGHR) | degree 4 → 2 | **Already in the repos** (`symmetrized_semaev.rs`; Probe C measured the symmetric lattice) | constant factor; Probe C: same lattice reach, 3–10× cheaper per reduction |
| 8 | GCD-based solving `gcd(S_3(x_1, x_Q, x_R), f(x_1))` (Kudo 2018) | resultant/gcd with the split base polynomial | **Already in the repos, in a faster form** (`prime_fast::collect_relations`: the `S_3` root in `X` is `x(R ∓ F_i)`) | the gcd computes exactly what direct subtraction plus a lookup computes, at `Õ(B)` versus `O(B)` |
| 9 | Fast evaluation of `S_m` by Sylvester recursion (MM Lemma 5.1) | `O(log² p)` per point, `m ≤ 10` | **Not needed** | the repos never evaluate `S_m` pointwise in the prime pipeline; MM's own Algorithm 4.1 (sum `m−1` points, check membership) is the repo's oracle |
| 10 | Algorithm 4.1 (MM) | enumeration oracle | **Is the repo's `subtract`/`mitm` oracle** | worth a citation in the repo: PR #1560's oracle is MM Alg. 4.1 with `u64` Montgomery constants and the pair table (MITM) that MM did not use |

Net: of ten techniques, four are already in the repos (two in a faster form), four are closed by the generic bound or the CRT lower bound, and two are constant-factor reorganisations whose linear-algebra penalty is paid over `F_p`. Nothing changes the exponent, and the repos' prime-field enumeration oracle already sits where this literature ends (MM Alg. 4.1 + MITM, measured on the `S·T² ≈ p` line in `RESEARCH_PRIME_FIELD_BREAKTHROUGH_PROGRAM.md` §1).

---

## 3. The barrier, sharpened

The repo's §2 of `RESEARCH_PRIME_FIELD_BREAKTHROUGH_PROGRAM.md` already has the right map. The following strengthens it at four points; each is new relative to the repos and, as far as the four lanes could find, to the published record.

### 3.1 Known logs and structure are mutually exclusive, and the known-log side is provably generic

A base element can carry a known log only if it was *constructed* as `uP + vQ`; its `x`-coordinate is then a uniform field element. A base can carry algebraic structure only if its `x`-coordinates are *selected* (interval, subgroup, isogeny coset); their logs are then unknown. The only bridge is `Aut(E)` and known endomorphisms, which give orbits of size `|Aut| ∈ {2, 4, 6}` (the GLV-invariant fold the repos measured in E1–E18).

On the known-log side the relation search is: given `s` random elements of `E(F_p)`, find `m` of them with a vanishing signed sum. This is the `k`-sum problem. Wagner's long version states precisely when the `k`-tree algorithm applies (a chain of `lg k` normal subgroups with efficiently computable quotient maps, or interval joins in `(Z/mZ,+)`), and proves **Theorem 2 (W. Dai)**: a `k`-sum solver in a cyclic group `⟨g⟩` in time `t` gives discrete logs in `O(t)`; **Corollary 1**: every generic `k`-sum algorithm needs `Ω(√p)`. `E(F_p)` of prime order has no subgroup chain and no coordinate compatible with its group law. So APS's single relation cannot be found faster than `√p` by any algorithm that does not read the field representation — and the only field-representation algorithm anyone has (Gröbner on split polynomials) is bounded below by `m·δ·d^{m−1}` (YYTK). Citable chain: Wagner (long version, §3, Thm 2 and Cor. 1) → Shoup 1997 / Nechaev 1994.

### 3.2 No algebraic small set over `F_p` (a Lang–Weil/Bézout lemma)

The repos state "no subset of `F_p` has membership degree below its size" and list images of low-degree maps as "just small roots with higher degree". The clean statement, which also covers PKM's compositional bases and any "V is the projection of a variety" construction:

> **Lemma.** Let `V ⊂ F_p` with `|V| = B`, and suppose `V = π(W(F_p))` where `W ⊂ A^{1+r}` is cut out by polynomials of degree `≤ D` and `π` is the `x`-projection. Then either `B ≥ (p − c·D²·√p)/D^r` (some positive-dimensional, absolutely irreducible, non-vertical component of `W` contributes), or every point of `V` comes from a 0-dimensional piece of `W(\bar F_p)` or a vertical component `{x = c}`, so `B` is bounded by the Bézout number of `W` (polynomial in `D`, exponential in `r`).
>
> *Sketch.* Lang–Weil gives `#Z(F_p) ≥ p^{dim Z} − c·D²·p^{dim Z − 1/2}` for an absolutely irreducible `Z/F_p`; fibres of `π|_Z` are 0-dimensional of size `≤ D^r` by Bézout; non-absolutely-irreducible components have their `F_p`-points inside the intersection of Galois conjugates, of smaller dimension, and recurse.

Consequence: a base of size `p^{1/m} ≪ p/D^r` is forced to come from a 0-dimensional `W`, hence its constraint algebra `F_p[x_1..x_m]/I_W^m ≅ F_p^{B^m}` by CRT, **regardless of how the generators are written**. PKM's chains `x_{i,j+1} = L_j(x_{i,j})` present the same algebra with low-degree generators; the quotient does not change, and neither does the evaluation floor. This is why PKM found, "intriguingly", that Semaev's split system was easier than their chained one, and why YYTK's experiments on binomial, non-binomial and random `F` all behave alike. The contrast with `F_{q^n}` is now one sentence: there, `V = F_q` is the set of `F_q`-points of the affine line *over the subfield* `F_q`, and Weil restriction turns `S = 0` into `n` equations over `F_q` whose `\bar F_q`-variety is 0-dimensional with Bézout number `≈ 2^{(m−1)n}`, independent of `q`; `F_p` has no proper subfield, so the only varieties whose `F_p`-points could form the base are varieties over `F_p` itself, whose point counts are `≈ p^{dim}` — never `p^{1/m}` unless 0-dimensional.

Two corollaries worth recording as closures: (i) **bit-descent** (write `x_i = Σ_j x_{ij}2^j`, impose `x_{ij}² = x_{ij}` over `F_p`) lands in the split algebra `F_p[x_{ij}]/(x_{ij}² − x_{ij}) ≅ F_p^{2^N}`, same floor; more generally any polynomial map `F_p → S` has degree `≥ p/|S|` (each value has `≤ deg` preimages), so there is no low-degree projection of `F_p` to a small set, unlike the `F_q`-linear trace forms on `F_{q^n}`; (ii) **multiplied bases** `∪_{k≤N}[k](F)` or `∪_{α}α(F)` for CM endomorphisms enlarge the effective base to `N·B` with `B` unknowns but the oracle enumerates `(NB)^{m/2}`, and the whole algorithm stays on the `S·T² ≥ p` line (constant-factor reorganisation; the repo's GLV folds are the `|Aut|` special case).

### 3.3 Lattice reach for the exact Newton polytope: the box bound is tight

For a modular polynomial `f` in `m` variables with Newton polytope `N`, equal bounds `X_i = p^δ`, Jochemsz–May's basic strategy at shift level `t` has `|M_0| ≈ Vol(N)·t^m`, `|M_k| = #((t−k)N + k·l) ≈ Vol(N)(t−k)^m` for any `l ∈ N` (translation does not change lattice-point counts, and `(t−k)N + kl ⊂ tN` by convexity), hence `s_N = t|M_0| − Σ_{k≥1}|M_k| ≈ Vol·t^{m+1}·m/(m+1)` and `Σ_j s_j ≈ Vol·t^{m+1}·c_N` where `c_N = Σ_j centroid_j(N)`. The determinant condition `Σ_j δ s_j < t|M_0| − s_N` gives

```
δ_max = 1 / ((m+1) · c_N)          (unequal bounds: Σ_j δ_j · centroid_j < 1/(m+1)).
```

For the box `[0,d]^m`, `c_N = md/2` and this is the repo's `2/(m(m+1)d)`. The question was whether the *actual* support of `S_{m+1}(x_1..x_m, z)` is smaller than the box. Sage (p = 2^28+3, random `a, b`; Appendix A.1):

| polynomial | terms | deg/var | total deg | support with last var fixed | box | `c_N` | `δ_max` |
|---|---:|---:|---:|---:|---:|---:|---:|
| `S_3` | 17 | 2 | 4 | 9 | 9 | 2 | 1/6 |
| `S_4` | 439 | 4 | 12 | 125 | 125 | 6 | 1/24 |
| `S_5` | 54 777 | 8 | 32 | 6561 | 6561 | 16 | 1/80 |

The reason is structural: `S_n` has total degree `(n−1)·2^{n−2}` (McGuire–Mueller Thm 2.2), which equals `(number of free variables) × (degree per variable)` once one variable is fixed, so the total-degree cut does not reach into the box, and every box monomial is present. Hence the repo's measured `δ ≈ 1/6` at `S_3` and its predicted `1/24, 1/80, 1/240` are the *exact* basic-strategy limits; Probe C already showed extended shifts and the symmetric form do not move them. Jochemsz–May's own Appendix A ("generalized rectangle": `∏X_i^{λ_i} < N^{2/((n+1)D)}`) is the same number; Galbraith's textbook (§15.8.1) says "Coppersmith's method … seems not to be useful for this task"; Diem 2011 §1: "no efficient algorithm for this task is known (except for very special equations)". No paper in 2004–2026 applies lattices to summation polynomials, positively or negatively, beyond those two sentences; the repo's Probes B/C are the only measurements in existence.

### 3.4 The product/norm paradigm is blocked in the same place

A different way to phrase the PDP avoids Gröbner bases and lattices entirely: for a split base `V` and target `z`, the PDP is "is `N_V(z) := ∏_{u∈V^m} S_{m+1}(u, z)` zero?", the norm of `S_{m+1}` from the algebra `A_V = F_p[x]/(g_V(x_i))`. One-dimensional norms are sub-linear in `|V|`:

- `V = μ_B` (subgroup, `B | p−1`): `∏_{u∈μ_B} g(u) = Res(g, X^B − 1)`, computed from `X^B mod g` in `Õ(deg g · log B)`.
- `V = [0, B)`: `∏_{u<B} g(u)` by Bostan–Gaudry–Schost baby-step/giant-step in `Õ(√B · deg g)`.

So the last variable of a decomposition costs `polylog` or `√B` instead of `B`. But the next level is a product over a polynomial of degree `2^{m−1}·B` (the resultant in the last variable has that degree in the next one), so the second level costs `Õ(B)` for subgroups and `Õ(B^{3/2})` for intervals; a direct two-dimensional baby/giant split with `s²` baby steps produces a bivariate baby polynomial with `≈ 4s⁴` coefficients and lands at `B^{4/3}`. All of these are `≥ B` (enumeration) and `≥ B^{⌈m/2⌉}` is what MITM already achieves. I checked for hidden structure that a smarter algorithm could use (Appendix A.2): for `p = 65537`, `B = 64`, the degree-8064 polynomial `Ψ_2(z) = ∏_{u≠v∈V} S_3(u,v,z)` has 8034–8065 nonzero coefficients for both the subgroup `μ_64` and the interval `[0,64)`, on a `j = 0` curve and on a random curve — dense, as a random-model polynomial would be. The only collapse I could find is for a *linear* `f`: `Res(X^B − 1, (X+a)^B − 1) = a^B ∏_{u∈μ_e}(a^B − u)^{r_u}` with `e = (p−1)/B` and `r_u` the cyclotomic numbers of order `e` (verified in PARI for `p = 10009, B = 72`, six random `a`; Appendix A.4), and even that costs `≥ e = p/B` per evaluation plus `Õ(√p)` per cyclotomic number, i.e. `√p` at `B = √p`. `S_3` is not homogeneous (for `a = 0` it is quasi-homogeneous only for the diagonal `μ_3` action), so no such collapse exists.

The analytic literature agrees on the counting side: a degree-`d` curve has `≪ d^{4/3}|H|^{2/3}` points in `H × H` (Corvaja–Zannier) and `≤ 4|H|^{2/3}` for a line (Garcia–Voloch), and a cubic has `M^{1/3+o(1)}` points in an `M×M` box for `M < p^{1/8}` (Chang–Cilleruelo–Garaev–Hernández–Shparlinski–Zumalacárregui), with the range `p^{1/3} < M < p^{1/2}` — exactly the `m = 2` PDP regime — explicitly open. None of these papers gives a finding algorithm. The only sub-linear algorithms in a subgroup setting are Bourgain–Garaev–Konyagin–Shparlinski's identity tests for the hidden shifted power problem (`e^{1/4+o(1)}`, `e^{2/3+o(1)}`), which rely on additive-combinatorial product-set estimates for a rigid `(x+s)^e` structure and do not transfer to `S_{m+1} = 0`.

### 3.5 The arithmetic that decides which arities could ever matter

Three independent statements of the same accounting now exist: PKM §3.2 ("outperform generic algorithms … when one can solve `T(E,m,L)` more efficiently than `p^{1/2−1/m}`"), Semaev 2004 §3 (`t_{p,n}p^{1/n+δ} + p^{2/n+2δ}`, "when `n ≥ 5`, even for some exponential `t_{p,n}`, this amount may be less than `O(p^{1/2})`"), and the repo's `cost(B) ≈ (m!/2^m)·p·T_dec/B^{m−1} + m·B²`, optimum `B = (p·T_dec)^{1/(m+1)}`, total `≈ (p·T_dec)^{2/(m+1)}`: `m = 2` never, `m = 3` ties only with `T_dec = O(1)`, `m = 4` beats rho iff `T_dec ≪ p^{1/4}`, `m = 5` iff `T_dec ≪ p^{1/2}`. With MITM enumeration `T_dec = B^{⌈m/2⌉}` the total is `p^{1/2+1/m}` (the folklore bound, nowhere stated verbatim but implied by Semaev's and PKM's formulas with `t = p^{1/2}`). Every Gröbner route is `≥ m·δ·d^{m−1}` per system (YYTK), which exceeds MITM's `d^{⌈m/2⌉}` by `d^{⌊m/2⌋−1}·mδ`; so "APS versus PKM versus Semaev" is a contest among methods all dominated by the pair-table oracle the repos already run.

### 3.6 What is rigorous and what is not

Nothing above the generic bound is proven for general `E(F_p)`. The lower bounds (YYTK) are heuristic (two statistical assumptions, checked to 25 bits). The lattice bounds are heuristic (Jochemsz–May Assumption 1). Even the *existence* of Semaev's interval base at its expected size is heuristic for `m ≥ 3`: Kim–Tibouchi's `N(I) = |I|(1 + O(q^{−1/2})) + O(q^{1/2} log p)` (via Kohel–Shparlinski character sums) is vacuous below `|I| ≈ √p`; Galbraith–Gaudry state "#F ≈ #V" as an assumption. My free-relation count (Appendix A.3: `p = 2^20+7`, `B = 400`; 22 and 27 distinct interval elements involved in `S_3`-relations against ≈ 30 expected; 9 and 38 for `μ_358` against ≈ 22) is consistent with the random model and shows no excess structure in either base type.

---

## 4. What can be built on this

### 4.1 Open problems that would change the exponent (precise statements, low probability)

These are the only things I found that are *not* excluded by §3. I would not build on them; I would hand them to a number theorist as questions.

**P1. Multidimensional structured norms.** Compute `∏_{u ∈ [0,B)^4} S_5(u_1,u_2,u_3,u_4, z) mod p` (equivalently the norm of `S_5` from `F_p[x]/(∏_{i<B}(x_j − i))`) in time `B^{1−ε}·polylog`, or the same over `μ_B^4`. By §3.5 this is exactly an `m = 4` oracle with `T_dec ≪ p^{1/4}`; current tools give `B³` (three enumerated variables, last one by the 1-D norm) and MITM gives `B²`. The one-dimensional case is `Õ(√B)` (BGS) or `Õ(log B)` (subgroup); already the two-dimensional case `∏_{(u,v)∈[0,B)²} S_3(u,v,z)` in `o(B)` is open and, by the reduction to a degree-`2B` univariate product (§3.4), is not reachable by any holonomic/P-recursive trick I can see. Evidence against: the dense `Ψ_2` (Appendix A.2); the absence of any sub-linear "2-D factorial" algorithm in the literature; Corvaja–Zannier-type counting says the answer is almost always "no zero", which is information-theoretically cheap to *guess* but not to *certify*. Probability I assign: ≈ 2%.

**P2. Small roots of `S_5` at `δ ≈ 1/5`.** Stated in the repo as falsifier (1). §3.3 adds that polytope-aware lattices cannot help (full box), so any solution must come from the *curve* structure of the small-root instances (the roots are `x`-coordinates of points whose sum is fixed), not from the polynomial's shape. No paper has tried; Galbraith and Diem dismiss it in one sentence each. Probability: ≈ 2%.

**P3. A base that is the `F_p`-points of something that is not an `F_p`-variety.** By §3.2 the base must come from a 0-dimensional variety (CRT floor) or be non-algebraic (size ⇒ lattices, §3.3). The gap between these two is the only unexplored territory: sets defined by *inequalities in a different embedding* (e.g. `x = u/v` with `u, v` small — Semaev's rational variant, never analysed; it is a 2-D lattice per variable and loses to §3.3 by the same exponent calculation), or sets defined through the group structure of `E(F_p)` itself (points whose log lies in an interval — but that is BSGS). I found no candidate that survives both §3.2 and §3.3.

### 4.2 A constant-factor program for special prime-field curves (solid, modest)

This is the only prime-field work that is both correct and new to the repos, and it matches the repo's success criterion ("every verified, measured improvement over the current index-calculus baseline is a success … report each row's gap to the matched rho as the distance remaining"). It never changes the exponent and must be labelled engineering.

- **`j = 0` curves (secp256k1-type), `p ≡ 1 mod 3`.** `Aut(E)` has order 6, generated by `(x,y) ↦ (βx, −y)`, `β³ = 1`. Since this is a group automorphism, `S_m(βX) = c·S_m(X)`: for `a = 0` every monomial of `S_3` has total degree `≡ 1 mod 3`, i.e. `S_m` is quasi-homogeneous for the diagonal `μ_3`-grading (checked on the explicit `S_3`; the lane found no paper that states it). What this buys: a `β`-stable base (`V = βV`) has `B/3` orbits (`B/6` with negation) and a solve for target `z` also serves `βz, β²z`, so relations and columns both fall by 3 (6), linear algebra by 9 (36). What it does not buy: the action is scalar, not a reflection group, so the invariant ring is not polynomial and no FGHR-type change of variables lowers the degree (the only automorphism-symmetrisation experiment in print, Gebregiyorgis 2016 §4.3 with an order-3 endomorphism in characteristic 3, found the system *harder*). A `β`-stable base has no small-height description, so this is for the enumeration oracle only — and there it is the existing `glv-orbit` fold (E1–E18 measured `÷3`/`÷12` on columns, nothing on the exponent). Verdict: already measured; nothing to add beyond relabelling.
- **Curves with rational 2-torsion (cofactor 4/8: Curve25519/Ed25519-type).** FHJRV Prop. 8(i)/Prop. 10 hold over any field: with a 4-torsion point of rational `x` (`y² = x³ + ax² + bx`, `b` a square) the summation polynomials in the invariant generators `s_1..s_{n−1}, e_n` have 5/13/182/4125 monomials for `n = 3..6` instead of 5/36/940/–, and with full 2-torsion and two square `Δ_i` the `Q_{φ,n}` form has 3/6/32/396; base divided by 2 (4 with negation, 8 with full 2-torsion), sign ambiguity divided by `2^{n−1}`, decomposition probability multiplied by `2^{−(n−1)}`. Over `F_p` the carrier of the `2^{ω(n−1)}` saving (a Weil-restricted zero-dimensional system) does not exist, so the gain is on the enumeration oracle's sign bookkeeping and on lattice constants (the per-variable degree halves, so the basic-strategy reach doubles: `1/3, 1/12, 1/40, 1/120` — still 1.5–15× short). Verdict: implementable on the existing `fghr_line.rs` (built for `F_{p³}`), expected `≤ 8×` on columns, `≤ 2^{m−1}` on signs; label engineering. Prime-order curves (secp256k1, P-256) have no rational 2-torsion on any curve isogenous to them, so this does not touch them.
- **Preprocessing / multi-target accounting.** The one regime where sub-`√p` per target is real (Bernstein–Lange `p^{1/3}` after `p^{2/3}`; Probe A). Already in the repo; the only addition is to charge every "online" prime-field row against it, as `RESEARCH_IC_LEADS_AND_CONNECTIONS_20261010.md` §8.3 recommends.

### 4.3 New closures to record (so the next person does not re-derive them)

- APS one-relation + random base ⇒ `k`-sum in `E(F_p)`; Wagner Thm 2 / Cor. 1 ⇒ `Ω(√p)` for every generic algorithm; YYTK Lemma 8 / Prop. 9 for the algebraic one (`≥ m·δ·d^{m−1}` per system, `> q^{m(1−ε)/(m−1)}` total). This upgrades the `H-ICEX-6ca21f` CRT heuristic to two citable bounds.
- PKM's compositional chains and the subgroup/isogeny-coset bases are the same algebra as the split polynomial (§3.2); PKM §5 and YYTK §4.3 confirm experimentally. Multiplicative-subgroup bases are PKM §3.3 (2016), not new.
- Kudo's GCD solving = MM Algorithm 4.1 = the repo's direct-subtraction oracle; MM's "best index calculus for prime fields" is the repo's baseline with worse constants.
- Bit-descent over `F_p` (§3.2 corollary i), multiplied/endomorphism bases (ii), the Kummer-line "use both twists" idea (a mixed tuple splits into a shorter relation on `E` and a free relation on the twist; no gain), free relations among base points (`O(1)` of them exist at `B^m ≈ p`; APS's redraw works only because their base has known logs).
- Lattice reach: the box bound is exact for `S_{m+1}` (§3.3); no polytope-aware construction can move it.
- Product/norm paradigm: `Õ(B)`/`Õ(B^{3/2})` at two dimensions (§3.4); dense `Ψ_2`; linear-`f` cyclotomic collapse costs `p/B`.
- Representation-technique ECDLP (Delaplace–May `p^{1.314}`; Delaplace–Fouque–Kirchner–May `Õ(p)` and `p^{4/5}` online after `p^{6/5}` precomputation) needs `F_{p^ℓ}`, `ℓ ≥ 2`, because its filter is "`x ∈ F_p`", a proper-subfield condition; void over `F_p`.
- 2019–2026: no lattice/Coppersmith, double-large-prime, ML or SAT work specific to prime-field summation polynomials; the only prime-field items are QUBO/annealing toys (Wroński 2021 at `p = 251`; Dzierzkowski–Wroński 2024 at `p = 1021`) and an unrefereed ePrint (Hu 2024/1923) that contains an incorrect claim about `S_3`.

### 4.4 Where the summation-polynomial ideas from this literature do have measured upside: the binary program

The one thing APS and their accelerators get right is where symmetry pays: inside a Weil-restricted zero-dimensional system. The 2026-10-24 factor-base review already identified the unbuilt items with literature-measured gains, and this read confirms them from the other side:

- FHJRV / Galbraith–Gebregiyorgis Experiment 2 (binary Edwards `t = x + y`, `(Z/4)^{m−1} ⋊ S_m` invariants `e_1, s_2..s_m`, `m = 4, ℓ = 4` in 9–52 s at `n ≤ 53`): never built in the repos; the encyclopedia's C8 tested only the `m = 3` special subspace. This is the exact analogue, over `F_{2^n}`, of what §4.2 cannot deliver over `F_p`.
- GGMP's Frobenius-partitioned bases (`F_i = π^{i−1}(F)`, `m!` saving with no `m²` penalty) are the principled version of APS's partition trick for subfield curves.
- Kudo's hybrid is Bettale–Faugère–Perret / crossbred; the repo's Δ-sweep question (degree rise at `Δ ≈ 0`) is the right place to test whether fixing a few Boolean variables moves the solving degree there.

---

## 5. Recommendations, in order

1. **Record, do not build.** Add to the ledger/encyclopedia: the Wagner Thm 2 reduction and the YYTK bound for the known-log/random-base family (closing `H-ICEX-6ca21f`'s whole class, not just the tested backend); the identity "MM Alg. 4.1 = repo oracle"; the §3.2 lemma and its two corollaries; the §3.3 full-box fact with the Sage script; the §3.4 two-dimensional norm cost and the dense-`Ψ_2` check. Half a day; prevents the next "APS looks promising" cycle.
2. **If any prime-field engineering is wanted,** do the 2-torsion symmetrised oracle on a cofactor-8 curve family (`fghr_line.rs` already has the `D_3` resultant machinery) and charge it against matched rho at 0/0.1/1 GAE per AGENTS.md §5a; expect `≤ 8×` on columns and nothing on the exponent; label engineering. Do not spend effort on `j = 0` beyond what E1–E18 measured.
3. **Hand P1/P2 (§4.1) to a number theorist as stated problems**, with the `Ψ_2` density and the full-box support as the two negative data points; do not allocate compute.
4. **Put the exponent-seeking effort where the structure is:** the unbuilt GG14 Experiment 2 and the `Δ`-sweep in the binary program, per the 2026-10-24 review.

---

## Appendix A. Computations run today (all reproducible; scripts in `scripts/` beside this file; raw console outputs in `outputs.md`; run Sage through the repo's inner binary `/Volumes/SSD990/cryptanalysis/third_party/sage-binary/sage` with `TMPDIR`, `DOT_SAGE`, `MPLCONFIGDIR` pointed at a writable directory, since the launcher's `.sage-build-tmp` symlink targets a sandbox-denied `/private/tmp` folder)

**A.1 Newton polytope of `S_{m+1}` with one variable fixed** (`newton.sage`, Sage via the repo's inner binary with `DOT_SAGE`/`TMPDIR` redirected; `p = next_prime(2^28)`, random `a, b`; Singular's resultant limit forbids `p > 2^29`). Output:

```
S4: nterms 439 degs [4,4,4,4] total 12
S5: nterms 54777 degs [8,8,8,8,8] total 32
S3 with x3 fixed: free vars 2, deg/var 2, support 9 of box 9;  hull centroid sum 2;  delta_max 1/6
S4 with x4 fixed: free vars 3, deg/var 4, support 125 of box 125; hull centroid sum 6;  delta_max 1/24
S5 with x5 fixed: free vars 4, deg/var 8, support 6561 of box 6561; hull centroid sum 16; delta_max 1/80
```

**A.2 Density of the double product** (`psi2.sage`; `p = 65537`, `B = 64`; `Ψ_2(z) = ∏_{u≠v∈V} S_3(u,v,z)`, degree 8064):

| curve | base | nonzero coefficients / 8065 | roots in `F_p` | roots in `V` |
|---|---|---:|---:|---:|
| `y² = x³ + 7` | `μ_64` | 8034 | 1987 | 12 |
| `y² = x³ + 7` | `[0,64)` | 8065 | 1966 | 0 |
| random `a,b` | `μ_64` | 8064 | 1998 | 3 |
| random `a,b` | `[0,64)` | 8065 | 1995 | 0 |

**A.3 Free `S_3`-relations among base points versus the random model** (`free2.sage`; `p = 2^20+7`, `B = 400` interval, `μ_358` subgroup; the count is the number of distinct `z ∈ V` that are roots of `Ψ_2`, i.e. elements of `V` involved in some relation `±P_u ± P_v ± P_z = O`; random-model expectation `≈ B²(B−1)/(2p)` after correcting for the three-fold detection of each relation):

| curve | base | observed | expected |
|---|---|---:|---:|
| `y² = x³ + 7` | `[0,400)` | 22 | 30.5 |
| `y² = x³ + 7` | `μ_358` | 9 | 21.9 |
| random `a,b` | `[0,400)` | 27 | 30.5 |
| random `a,b` | `μ_358` | 38 | 21.9 |

**A.4 Cyclotomic collapse of the linear double product** (`cyc.gp`; `p = 10009`, `B = 72`, `e = 139`): `Res(X^B − 1, (X+a)^B − 1) = a^B ∏_{u} (a^B − u)^{r_u}` with `r_u = #{(z,h) ∈ μ_B² : (h−z)^B = u}/B` verified for six random `a` (all equal); multiplicities integral, `Σ r_u = B − 1 = 71`, 33 of 139 cosets hit.

## Appendix B. Key sources (full citation detail and page/equation references are in the four lane files)

- Amadori, Pintore, Sala, FFA 51 (2018) 168–182; ePrint 2017/609; accepted manuscript: https://iris.unitn.it/handle/11572/202653
- Kudo, Yokota, Takahashi, Yasuda, CANS 2018, LNCS 11124, 377–393, doi:10.1007/978-3-030-00434-7_19
- Yokoyama, Yasuda, Takahashi, Kogure, J. Math. Cryptol. 14 (2020) 460–485, doi:10.1515/jmc-2019-0029
- McGuire, Mueller, ePrint 2017/1262
- Petit, Kosters, Messeng, PKC 2016, LNCS 9614, 3–18: https://christophe.petit.web.ulb.be/files/16PKC_primeECDLP.pdf
- Semaev, ePrint 2004/031; Semaev, arXiv:1504.01175 (2015)
- Galbraith, Mathematics of Public Key Cryptography, §15.8.1, ch. 19; Galbraith–Gaudry, ePrint 2015/1022 (DCC 2016)
- Diem, Compositio 147 (2011); Kosters–Yeo, arXiv:1503.08001
- Jochemsz–May, ASIACRYPT 2006 (basic/extended strategy, Appendix A); May, LLL survey; Feng–Nitaj–Pan, ePrint 2024/1330 (JM bound = Newton-polytope volume)
- Wagner, "A generalized birthday problem", long version (§2 "Operations other than xor", §3 Thm 2, Cor. 1): https://people.eecs.berkeley.edu/~daw/papers/genbday-long.ps
- Bostan–Gaudry–Schost, SIAM J. Comput. 2007; Costa–Gerbicz–Harvey, arXiv:1209.3436
- Bourgain–Garaev–Konyagin–Shparlinski, SIAM J. Comput. 41 (2012), arXiv:1110.0812; Shkredov–Vyugin, arXiv:1102.1172; Mérai–Shparlinski, arXiv:1803.02165 (Corvaja–Zannier bound); Chang et al., arXiv:1111.1543
- Kim–Tibouchi, J. Math. Cryptol. 14 (2020) 339–345; Kohel–Shparlinski, ANTS-IV
- Faugère–Gaudry–Huot–Renault, J. Cryptology 27 (2014); Faugère–Huot–Joux–Renault–Vitse, EUROCRYPT 2014; Galbraith–Gebregiyorgis, INDOCRYPT 2014 and Gebregiyorgis thesis (Auckland 2016); Joux–Vitse, J. Cryptology 26 (2013); Galbraith–Granger–Merz–Petit, SAC 2020; Tsakou–Ionica, Math. Cryptology 1 (2021)
- Delaplace–May, ePrint 2019/800; Delaplace–Fouque–Kirchner–May, HAL hal-02427655 (2020)
- Dzierzkowski–Wroński, Tatra Mt. Math. Publ. 87 (2024); Wroński 2021 (QUBO); Hu, ePrint 2024/1923 (unreliable)
