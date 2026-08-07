# R-LWE / M-LWE mechanism portfolio — 2026-08-06

Nine candidate mechanisms for attacking Ring-LWE and Module-LWE as *problems*
(not as schemes), ranked, each with the object it tracks, the exchange rate it
proposes to exploit, its ceiling stated in advance, and the cheapest experiment
that could kill it.

**Status: STAGING. Nothing here is a ledger record.** IDs are pre-allocated and
verified free (`tools/allocate_id.py --check`) but are not minted until a
Coordinator commits them.

---

## Provenance and limits (read first)

**REVISION 2, 2026-08-06.** This document was pressure-tested by 11 independent
agents after revision 1: 7 claim clusters checked by exact computation, 3
prior-art lanes screened. **All 7 came back partially wrong.** The structural
algebra held exactly — several parts are *stronger* than revision 1 argued — but
**every headline number a downstream Executor would have acted on was wrong**,
and two were wrong in the direction that inverts the conclusion. All corrections
are inline below and marked. Full verdict: `rlwe-pressure-test-report.md` in this
directory. **Read that before trusting anything here.**

- **Primary sources: partially read now, and the earlier blocker claim was
  wrong.** Revision 1 said no primary source had been read and treated
  RQ-FHE-001's "eprint unreachable (proxy CONNECT 403)" as a plausible gate.
  Corrected status: **eprint HTML abstract pages and `/search` return HTTP 200**;
  **PDFs return 403** behind a Cloudflare interstitial; and the **WebSearch /
  WebFetch tools are hard-broken** in this harness with a model-availability
  error — *not* a network block. **Earlier "unreachable" verdicts across this
  program may be misattributed tool failures and are worth re-testing.** Ducas–van
  Woerden (2021/999) and Felderhoff–Pellet-Mary–Stehlé (2022/1203 — *not* the
  number revision 1's recall would have produced) were both read in **full text**
  from local disk. No free-text web search was available for any lane.
- **Every number below has now been independently recomputed**, and most were
  replaced. Where a corrected value appears it comes from exact integer/symbolic
  arithmetic with matched null controls, not from this author's envelope.
- **Novelty is screened but INCOMPLETE in all three lanes; none is clean.** In
  every lane the single highest-collision document could not be read past its
  abstract. Prior-art risk grades below were revised — one up, one down.
- AGENTS.md rule 4 applies throughout: nothing here is a statement about
  ML-KEM, ML-DSA, or any deployed FHE parameter set. **Revision 1 violated this**
  by asserting an 8-bit NTRU-fatigue safety margin for ML-KEM. Withdrawn; the
  correct figure is 0.205 bits in the *other* direction, and no claim replaces it.

---

## The organizing claim

Three problems this program already tracks separately are **three presentations
of one object**:

Given two R-LWE samples `b_i = a_i·s + e_i (i = 1,2)`, eliminating `s` gives

```
a_2·b_1 − a_1·b_2 = a_2·e_1 − a_1·e_2 =: E        (E is public)
```

so `(e_1, e_2)` is a short vector in a **coset** of the rank-2 R-module

```
M_h = { (x, y) ∈ R² : y ≡ h·x  (mod q) },     h = a_1^{-1}·a_2
```

which is *literally the NTRU module*, and is the object HAWK's module-LIP
instances live on. So:

| presentation | object | homogeneous? | module structure on the target? |
|---|---|---|---|
| NTRU | `M_h`, rank 2 | yes | yes — `R·(f,g) ⊆ M_h` |
| 2-sample R-LWE, `s` eliminated | coset of `M_h`, rank 2 | no (BDD) | **no** — `R·(e_1,e_2) ⊄` coset |
| 2-sample R-LWE, `s` retained | `M`, rank 4 (below) | yes | yes — `R·(−s,e_1,e_2,1) ⊆ M` |

The third row is the one nobody reduces, and **that is mechanism M1's entire
thesis**. The second row is why the standard pipeline sees no structure: Kannan
embedding appends a *scalar* coordinate and destroys the R-module structure by
construction.

This unification means GOAL-HAWK-001 (rank-2 module-LIP), the NTRU fatigue
literature (KN-LIT-114, KN-LIT-112), and R-LWE cryptanalysis are pulling on the
same rope. Budget should be allocated accordingly.

---

## Ranking

Verdicts are **post-pressure-test**. Revision 1's grades are struck through where
they changed.

| # | mechanism | upside | prior-art risk | cost to kill | verdict |
|---|---|---|---|---|---|
| **M9** | Arora–Ge starvation | closes a lane **with a proof, now obtained** | low | **very low** (rank computation) | **GO — run first**, after 3 number fixes |
| **M1** | Dense-submodule (DSD) transfer: is there an overstretched R-LWE? | **high** (FHE parameter tables) | ~~med–high~~ → **MEDIUM**, but re-pointed: FPS is *supporting*, Karenin–Kirshanova 2024/844 is the real risk | low (n ≤ 64 sweep + NTRU control) | **GO after 2 blocking fixes**, then resolve K–K rank-generality before any code |
| **M2+M5** | The κ-surface unifying primal / dual / slot / subring-descent | closes a family | ~~low~~ → **HIGH** (Stange 2019/183; Ogilvie 2026/279) | low (closed-form + small sweep) | **NO-GO as first written** — was a false-positive generator; GO now the law is two-dimensional |
| M3 | R-LWE has no self-reduction over `a` → measure the weak-`a` tail | med | low–med, **concentrated entirely in Ikematsu et al. 2021** | med | conditional GO, build second |
| M4 | Smoothing failure mod sublattices → decidable weak-parameter test | med (tool) | ~~med~~ → **framing is published** (Peikert 2016 §3.2.1); non-ideal gap survives | med | GO **re-scoped to the non-ideal case** |
| M6 | Module-native reduction: does the *profile shape* change, not just constants? | low–med | high, **and risen** (Ducas–Engelberts–de Perthuis 2025/1904) | med–high | HOLD, gate on M1 |
| M7 | Quantum: does S-unit / Stickelberger machinery reach rank ≥ 2? | **very high** | high | very high | HOLD — moonshot, gate on M1+M9, **now absorbs M8** |
| M8 | ℓ∞ / log-embedding BDD | unknown | unknown | low | ~~closes into M7~~ → **REOPENED: the closure reason was false** |

---

## M1 — Dense-submodule transfer: is there an overstretched R-LWE / M-LWE?

`IDEA-20260806-d810ed` → GOAL-RLWE-001

### Object

The **homogeneous** module lattice, with the Kannan coordinate kept as a *ring*
coordinate rather than a scalar:

```
M = { (x, y_1,…,y_m, z) ∈ R^(m+2) : y_i ≡ a_i·x + b_i·z  (mod q) }
N = R·(−s, e_1, …, e_m, 1)
```

Both facts are one line each:

- `(−s, e, 1) ∈ M`, since `a_i·(−s) + b_i·1 = b_i − a_i·s = e_i`.
- `N ⊆ M`, since `r·(−s,e,1) = (−rs, re_1,…,re_m, r)` and
  `a_i·(−rs) + b_i·r = r(b_i − a_i·s) = r·e_i`.

So `N` is a rank-1 R-submodule — **Z-rank `n`** — of a lattice of Z-rank
`(m+2)n`, **spanned by `n` vectors of equal norm `‖(s,e,1)‖`**. (Not "consisting
entirely of short vectors" — `N` contains `r·v` for every `r ∈ R`, and since the
`z`-coordinate of `r·v` is `r` itself, `‖r·v‖ ≥ ‖r‖` is unbounded. The property
DSD needs is `λ₁(N) = … = λ_n(N) = ‖(s,e,1)‖`, equivalently
`det(N)^{1/n} ≪ det(M)^{1/((m+2)n)}` — measured `6.29` vs `57.70` at
`n=8, m=2, q=3329`.) That is exactly the configuration that makes NTRU
overstretched.

Two facts **verified but not claimed above, and both favour M1**: `N` is a
**primitive (saturated)** sublattice of `M` (Smith normal form elementary
divisors all 1, two independent routes, five parameter sets), and `N` is **not
contained in `qR^{m+2}` in any coordinate block** (the `z`-block is literally
`I`). Those are precisely the two conditions that would have made the dense
submodule invisible to BKZ. There is no lattice-theoretic obstruction.

And the contrast is **reproducible at toy scale**: BKZ-20, `n=8, m=2, q=3329` —
on `M` (dim 32) the eight shortest vectors all have norm² 41, the next is 31410,
and the eight span `N` with Z-rank 8. **The DSD event fires.** On the matched
Kannan lattice (dim 25, same determinant `3329^16`, target present) the shortest
is 41, the next is 72516, and the set of vectors with norm² ≤ 41 has Z-rank 1.

### The trade this proposes, stated honestly

| | standard (Kannan) | module-homogeneous |
|---|---|---|
| Z-dimension | `(m+1)n + 1` | `(m+2)n` |
| covolume | `q^{mn}` | `q^{mn}` |
| normalized covolume | `q^{mn/((m+1)n+1)}` (**not** the `n→∞` limit `q^{m/(m+1)}`) | `q^{m/(m+2)}` |
| dense rank-`n` submodule | **no** | **yes** |

Dimension penalty is `(m+2)n − ((m+1)n+1) = **n − 1**`, not `n`. And the exact
Kannan normalized covolume matters at the sizes actually swept: the limit form is
12–21% high there (`45.45` vs `57.70` at `n=8, m=1, q=3329`), so writing the
module side exactly and the Kannan side asymptotically computes the two halves of
this table to different standards and shifts any fitted `q*(n)`.

The airtight form of the comparison, which replaces the hand-wave: **the Kannan
lattice with τ=1 is literally the section `M ∩ (R^{m+1} × Z·1)`**, of identical
determinant `q^{mn}` (verified at `n=8, m=1, q=97`). So `M` *is* the Kannan
lattice plus `n − 1` dimensions of **unit density**.

The module formulation is **strictly worse for the uSVP event** — you pay `n − 1`
extra dimensions and a lower normalized density. The entire question is whether
the DSD event repays that. NTRU pays no such penalty (its natural lattice is
already the module lattice), so R-LWE's prior of success is *lower* than
NTRU's — which is precisely why the measurement is informative either way.

### Why it may be genuinely unexplored

Every deployed estimator (lattice-estimator, MATZOV, core-SVP) models uSVP and
dual on the Kannan lattice. There is **no DSD model in any of them**, and the
lattice they model has no dense submodule to find. A DSD event in the module
formulation is structurally invisible to the entire estimation pipeline.

### Payoff regime

Ducas–van Woerden's **concrete** fatigue point is `q ≈ 0.004·n^2.484` (their
abstract, stated valid for `n > 100`), not the bare asymptotic `n^{2.484+o(1)}`.
The constant is `2^{−7.966}` and it consumes the entire apparent margin: at
`n = 256` the fatigue point is `3838 = 2^11.906`, and ML-KEM's
`q = 3329 = 2^11.701` sits **0.205 bits BELOW it** — not 8 bits above. Charged
against module dimension `kn` rather than ring degree, the margin is
`+2.69 / +4.14 / +5.17` bits for ML-KEM-512/768/1024. DvW anticipate exactly this
error in the same paper: *"we do observe fatigue points that are significantly
lower than the naive value."*

**ML-KEM is therefore NOT demonstrably outside the regime, and this document
makes no claim that it is.** (The earlier draft asserted an 8-bit safety margin
for ML-KEM while also asserting it made no statement about ML-KEM. That was a
rule-4 violation and the number was wrong; both are withdrawn.)

Three qualifications the exponent carries and the earlier draft dropped: 2.484
holds only for ternary secrets (`σ = Θ(1)`) — `Q*(S)` rises to 2.78 at `S = 0.6`
and 3.73 at `S = 1.0`; the constant `0.004` is calibrated on **matrix** NTRU
while this object is **circulant**, which DvW explicitly differentiate; and so
**M1 currently has no legitimate NTRU reference value** for the fitted exponent
in its success criterion.

The payoff regime remains **large `q/σ`**: BGV/BFV/CKKS at
`n ∈ {2^13 … 2^15}` with `log q ∈ [200, 900]`, where the concrete fatigue point
is `2^24.3`–`2^29.3` and the shipped modulus is 170–876 bits above it
(recomputed; the FHE motivation is undamaged and was understated). If the exponent
transfers even approximately, the FHE parameter tables — all computed with a
uSVP/dual estimator — are systematically optimistic.

Note the RNS reduction does **not** rescue large `q`: from `b = a·s + e` over
`R_q` with `q = ∏ q_i`, reducing gives `b ≡ a·s + e (mod q_i)` with the *same*
small `e`, so hardness at modulus `q` is bounded *above* by the small-modulus
instances, never below. Large `q` is the attacker's friend here.

### Ceiling, stated in advance

**DSD is not polynomial time and never will be.** Inside the overstretched
regime the attack stays exponential; the only claim available is a reduction in
the required BKZ block size `β`, i.e. bits. No batch may report this as a break.

### Cheapest decisive test

`n ∈ {8, 16, 32, 64}`, `m ∈ {1, 2, 4}`, sweep `log q`. Build the module basis
of `M`, run BKZ with a DSD detector (does the span of recovered short vectors
have Z-rank `n` and is it `x`-stable?), and plot the empirical fatigue curve.

**The control is mandatory and is the point of the design:** run the *same*
detector on matched-`(n, q)` NTRU instances, calibrated against the **concrete**
curve `q ≈ 0.004·n^2.484` — at `n = 64` that is `q ≈ 2^7.0`, **not** the naive
`2^14.9`. Calibrating on the naive curve puts the control ~250× too high in `q`,
where it fires everywhere and would be misread as validating a detector that is
in fact saturated. A control that cannot *fail* discharges nothing.

Two further detector requirements the first draft missed:

- **Do not infer "Z-rank `n` and `x`-stable" from vector lengths alone.** The
  rotation basis is *not* near-orthogonal: the orthogonality defect per dimension
  tends to `1.145` (m=1) / `1.092` (m=2), so total defect is `2.4` at `n=8` but
  `1.3e7` at `n=128`. A length-thresholded detector is miscalibrated by `1.14^n`
  and will misclassify at the `n = 32–64` end of the sweep.
- **Compute `vol(N)` per instance as the exact integer `isqrt(det Gram)`**, never
  from `σ√((m+1)n)`. That heuristic is a strict AM-GM over-estimate (true value
  `σ√n·exp(ψ(m+1)/2)`), and it errs in the direction that makes the dense
  submodule look *less* dense than it is — biasing the experiment toward M1's own
  null. Per-instance spread at `n=8` runs 0.88–1.51, so **the sweep cannot read a
  fatigue point off single instances.**

- Falsified if: NTRU control fires reliably and R-LWE never fires at any `q`.
- Supported if: R-LWE fires, with a fitted exponent `q*(n) ≈ n^c`, and the
  module-formulation `β` at `q > q*` is below the Kannan-formulation `β`
  *after* charging the `n − 1` extra dimensions.

### Prior-art risk: MEDIUM — but revision 1 pointed it at the wrong paper

**Felderhoff–Pellet-Mary–Stehlé, 2022/1203** (revision 1's "most likely
collision") was read in **full text** and is **supporting evidence, not a
collision**: worst-case reduction, no experiments, strictly rank-2, and it
*explicitly disclaims* the overstretched regime — *"The regime of the
overstretch-NTRU attacks … is also distinct from ours, but in the opposite
direction"* — leaving the regime intersection an open problem.

**The real risk is Karenin & Kirshanova, *Finding Dense Submodules with Algebraic
Lattice Reduction*, AfricaCrypt 2024 / eprint 2024/844 — abstract only** (PDF 403,
OpenAlex closed, author homepage dead; **absent from all 7,819 KN-LIT corpus
entries**). It already coins the **"Dense Submodule Discovery (DSD) event"**, an
**algebraic Pataki–Tural lemma** over any number field, an algebraic GSA, and a
module-level algebraic LLL, applied to **NTRU as a rank-2 module with a rank-1
dense submodule**. **M1 cannot claim to introduce any of that.**

**The pivot of the entire screen is one unresolved question: is their machinery
arbitrary-rank, or rank-2 only?** If arbitrary-rank, M1 reduces to "apply an
existing published tool to a new object" and collision rises to **HIGH**. Resolve
before any code.

Also unresolved: **Ducas–Loyer, *Lattice Reduction via Dense Sublattices: A
Cryptanalytic No-Go*, 2025/1694** is a no-go for a *different* object (DSP_k-BKZ
on random lattices, no planted submodule). **M1 must distinguish itself from it
explicitly or be mistaken for something already ruled out.** Kirchner–Fouque 2017
remains **unread as primary** by this program (no eprint version, Springer
paywalled) and has only ever been cited at second and third hand.

**Honest repositioning:** *extend Karenin–Kirshanova's rank-2 NTRU DSD framework
to the rank-`(m+2)` R-LWE/M-LWE module* — pending their rank-generality.

---

## M9 — Arora–Ge starvation: is the deficit exactly `n`?

`IDEA-20260806-e4c374` → GOAL-RLWE-003

### Object

The rank of the Macaulay matrix of the Arora–Ge system, as a module over `R`.

ML-KEM's error is *bounded*, so Arora–Ge applies in principle — but the degree is
**parameter-set-dependent**, which the first draft got wrong. ML-KEM-768 and
-1024: `η₁ = 2` for both `s` and `e`, support `[−2,2]`, **degree 5**.
**ML-KEM-512: FIPS 203 uses `η₁ = 3` for BOTH the secret and the KeyGen error**
(checked against the vendored pq-crystals script in `experiments/EXP-MLKEM-001/`),
support `[−3,3]`, **degree 7**, `C(519,7) = 2^50.78` monomials.

It fails for one reason only: sample starvation. ML-KEM-768 publishes
`m = 256·3 = 768` sample equations, **plus 768 more from the secret coordinates**
— ML-KEM's secret is CBD-bounded too, so `∏_{k=−2}^{2}(s_i − k) = 0` — giving
**1536**, not 768, against `C(773,5) = 2,270,319,562,049 = **2^41.05**` (not
`2^44`; reaching `2^44` at degree 5 needs `N ≥ 1159` variables).

The correction matters beyond the bit count: in small-`n` experiments the
**secret equations were the only source that ever raised the Macaulay rank**
(`n=4, D=6`: 134 → 209 of 210 monomials — essentially solving the system), while
every ring-derived construction raised it by exactly zero. The starvation
argument in the first draft was aimed at the wrong quantity. The verdict survives
(`1536 ≪ 2^41`), but the lane would reopen the moment a referee noticed.

### The question

**Can the ring structure manufacture algebraically independent equations that
plain LWE cannot?** Three candidate sources: products of samples, Galois
conjugates of the equations, and the `R`-module structure of the Macaulay
matrix.

### Predicted answer, and why that is the useful outcome

Predicted: **no** — and this is the one prediction in the portfolio that the
pressure test **confirmed and upgraded from measurement to proof.** Galois
conjugates, rotations, pairwise products, **and** short-multiplier equations
(`c = x^i ± x^j`, which the first draft did not consider) give rank increase
**exactly 0** at every `n, q, B, m, D` tested.

The proof: for all `t ∈ (Z/2n)*`, the conjugation permutation `P_t` satisfies
`P_t·Neg(a) = Neg(σ_t(a))·P_t` — it is a *signed* permutation — so the conjugated
affine forms are `±A_{π(j)}`; and since the support `[−B,B]` is symmetric,
`∏_k(−A−k) = (−1)^{2B+1}∏_k(A−k)`. **Galois returns the same polynomials up to
sign.** That is what this lane should bank.

**Deleted from the first draft:** the claim that "the rank deficit is exactly `n`
per ring sample, invariantly." It is unsupported and ill-posed. Measured, the
Galois orbit's redundancy is `n(n−1)` per ring sample (`n²` conjugate equations
collapsing to exactly `n` independent ones), and the rank **deficit versus an
unstructured control with matched equation and variable counts is 0, not `n`**.
It was the single sentence in this lane a referee would have gone for.

### Cost: very low

It is a rank computation over `F_q` at `n ∈ {4, 8, 16}` with a symbolic
follow-up. Days, not weeks. This is the highest information-per-token item in
the portfolio and should run first regardless of what else is approved.

### Prior-art risk: LOW for the ring-specific rank statement.

---

## M2 + M5 — The κ-curve: one parameter unifying the whole structured-dual family

`IDEA-20260806-35d60b` (descent) and `IDEA-20260806-b37e8e` (slot-FFT) →
GOAL-RLWE-003

### The two endpoints, then the unification

**M2, subring descent.** Let `K' ⊂ K` with `[K:K'] = f`, `R = ⊕_j R'·ω_j` (free
for the power-of-2 cyclotomic tower: `Z[ζ_2n] = Z[ζ_n][ζ_2n]`, basis `{1, ζ_2n}`,
`f = 2`). Find short `c ∈ R_q^m` with `α := Σ c_i a_i ∈ R'_q`. Then multiplication
by `α` is `R'`-linear and preserves the `ω`-decomposition, so taking the
`ω_0`-component of `y := Σ c_i b_i = α·s + E`:

```
y_0 = α · s_0 + E_0        with   E = Σ c_i e_i
```

— **an honest R'-LWE sample in dimension `n/f` with secret `s_0`.** Dimension
halves per level.

The constraint `α ∈ R'` is only `(f−1)·n/f` `F_q`-conditions, versus the `n`
conditions the classical dual attack imposes (`α = 0`). So the `c`-lattice is
*less* constrained and its short vectors are shorter by `q^{1/(fm)}`.

**M5, slot-restricted dual.** Require instead that `α` vanish on all but one CRT
slot. For ML-KEM, `q = 3329 ≡ 1 (mod 256)` but not `(mod 512)`, so
`R_q ≅ ∏_{i=1}^{128} F_q[x]/(x²−γ_i)` — degree-2 slots. That is `n − 2`
conditions instead of `n`, and the residual guess is over a slot of size `q²`,
FFT-able. Strictly weaker constraint than the classical dual, so strictly
shorter vectors suffice.

**The unification.** Both are the same move with a different budget. Let
`V ⊆ R_q` be the allowed image of `Σ c_i a_i`, of `F_q`-codimension `κ ∈ [0, n]`:

```
κ = n              →  α = 0                →  classical dual attack
κ = n − 2          →  α in one slot        →  M5, slot-restricted dual
κ = n − n/f        →  α ∈ R'               →  M2, subring descent
κ = 0              →  no constraint        →  primal attack
```

and the exchange law is closed-form:

```
‖c(β_c)‖ = δ(β_c)^{mn} · q^{κ/(mn)}      (what BKZ-β_c actually returns)
L(κ)     = q^{κ/(mn)} · sqrt(mn / 2πe)   (Gaussian heuristic: a LOWER BOUND,
                                          NOT attainable)
residual instance:  dimension n − κ,  modulus q,
                    per-coefficient noise sd = ‖c‖·σ    (c_ring = 1, measured
                                                         exactly, not √n)
                    ‖E_0‖ = ‖c‖·σ·√(n − κ)
total cost = max( β_c , β_resid(‖c(β_c)‖) ) + [FFT over V]
```

**The curve is TWO-dimensional: `(κ, β_c)`.** Minimising over `κ` alone with
`‖c‖ = L(κ)` plugs in an unattainable vector length and reports that **descent
WINS** — `β 367 → 201` at FHE scale. Reaching `L(κ)` requires `β_c = 65539 > d`
at `n = 2^15` and `β_c = 516 > d = 512` at `n = 256`: exact SVP in both cases.

The earlier one-parameter form of this section was a **false-positive generator
pointed at deployed parameter sets**, and it is the most serious error the
pressure test found. It is corrected here rather than deleted, because the shape
of the mistake is the finding: the cost of *producing* `c` is the term that
decides the family, and omitting it makes every structured relaxation look free.

The deliverable is still a *surface* rather than an attack, with the literature's
attacks marked as points on it and the optimum located — the direct descendant of
KN-OPEN-019 ("what object does each attack family track, and is that enumeration
closed?") applied to structured lattices.

### What the envelope already says (re-derive before citing)

At **ML-KEM-ish** parameters (`n = 256`, `q = 3329`, `σ ≈ 1`, `m = 2`, `f = 2`):
`covol^{1/512} = q^{1/4} = 7.596`, `‖c‖ = L = 41.59`, so the descended
**per-coefficient** noise sd is `41.59` against `q = 3329` — **80× headroom, not
saturation.** (`665` is the *L2 norm* of `E` across 256 coefficients; comparing
it to a scalar modulus is a category error, and even at face value 665 < 3329.
`‖E_0‖ = 470.5`.) The residual is a well-posed uSVP instance: `β_resid = 152.445`
versus `152.444` direct — **descent at ML-KEM parameters is noise-NEUTRAL, not
fatal.** It loses only once the cost of producing `c` is charged:
`max(β_c, β_resid) = 233` versus `152` direct.

At **FHE-ish** parameters (`n = 2^15`, `log q = 800`, `σ = 3.2`, `m = 2`), one
descent level costs a noise **growth factor** of `L = 2^205.95` (`‖E‖ = 2^215.13`
is a norm, not a factor) while halving the dimension. Under the Gaussian-heuristic
`‖c‖` the uSVP estimate moves `β` from `367` to `201` — **descent WINS**, and that
is the artifact, not the answer. Charging the cost of producing `c`:
`max(β_c, β_resid) = max(560, 548) = 560` versus `367` direct — **descent loses by
~190, because `‖c‖` cannot REACH the Gaussian heuristic**, not because it is
pinned to it.

So the expected outcome for the `κ = n − n/f` endpoint is still a **quantified
negative** — but the reason in the first draft was stated backwards, and the two
headline numbers behind it were both wrong. The value is the surface, and a
surface whose optimum sits at an endpoint is a closed family.

### Ceiling, stated in advance

**This cannot move an exponent.** The relaxation from `κ = n` to `κ = n − k` is
worth a factor `q^{k/(mn)}` in required vector length — `O(1)` bits for any
`k = O(1)`, and self-defeating for `k = Θ(n)` because the noise term grows
faster than the dimension shrinks. The honest best case is a small constant
number of bits plus a closed family.

### Mandatory internal gate

**Do not build a ring-native dual attack on top of a dual-attack score model
this program has evidence to distrust.** GOAL-MLKEM-004 measured exactly that
model and KN-OPEN-016 is open. The `κ`-curve must be computed in whichever cost
model GOAL-MLKEM-004 lands on, or reported in both with the divergence shown.

There is a bonus here: slot-restricted dual vectors form an `R'`-module, so
their correlation structure is **exactly computable** rather than assumed. That
makes M5 a new *instrument* for testing the independence heuristic, independent
of its value as an attack.

---

## M3 — R-LWE has no self-reduction over `a`

`IDEA-20260806-a51421` → GOAL-RLWE-002

### Observation

R-LWE has a perfect random self-reduction over the **secret** (`s ↦ s + t` for
public `t`). It has **none over `a`**. The only maps preserving both the instance
shape and the smallness of the error are `a ↦ ±x^k·a`: multiplying by a unit `u`
requires `u·e` to stay small, and the only short units are roots of unity.

Consequence: **a set of weak `a` cannot be argued away by re-randomization.** It
can only be bounded through the LPR worst-case reduction, whose concrete
parameters are nowhere near deployment. The average-case hardness claim over `a`
is therefore a statement about a distribution **nobody has measured**.

### Program

At small `n`, sample many `a`, measure the `β` required for fixed success
probability, and characterize the **left tail**. Then two follow-ons:

1. **Tail exponent.** Is it heavy enough that a seed search matters? ML-KEM
   derives `A` from a public seed `ρ` via SHAKE-128 — irrelevant when `ρ` is
   honestly random, but directly relevant to any protocol that reuses, derives,
   or lets a party choose `ρ`, and to any scheme with a *fixed global* `a`.
2. **Constructive weak instances.** Build `a` whose module `M_a` contains a
   planted short vector, then ask whether such `a` are distinguishable from
   random. If they are not, that is a trapdoor-R-LWE observation with its own
   interest and its own warning label.

### Ceiling

Cannot break ML-KEM. Best case is a measured tail exponent plus, possibly, a
constructive weak family.

### Prior-art risk: LOW–MEDIUM

Chen–Lauter–Stange and Elias–Lauter–Ozman–Stange construct weak **rings and
moduli**. Weak `a` inside a fixed *good* ring is the novelty axis, and the
"no re-randomization over `a`" point — folklore — has not, to the author's
knowledge, been turned into a measurement program.

---

## M4 — Smoothing failure modulo sublattices: a decidable weak-parameter test

`IDEA-20260806-e2ed7a` → GOAL-RLWE-002

### Generalization

The known attacks (EHL, ELOS, CLS) require *a ring homomorphism `R_q → F_q`
under which the error stays small*. The right invariant is weaker and larger:

> the error distribution **fails to smooth** a sublattice `L`, where `L` ranges
> over kernels of `R_q`-module maps.

Bias is then `≈ Σ_{v ∈ L*, short} exp(−π σ² ‖v‖²)`, and the instance is
attackable when that exceeds the inverse sample count.

**This generalization is not new — it is Peikert, *How (Not) to Instantiate
Ring-LWE*, 2016/351, §3.2.1**, which re-expresses EHL/ELOS/CLS through duality
and trace pairings and says verbatim that the framework is *"strictly more
general"* than the ring-homomorphism one; his Lemma 3.1 is the smoothing-failure
criterion for an arbitrary lattice `L`, and Theorem 5.2 proves immunity via the
smoothing parameter by name. The first draft claimed this move. **Withdrawn.**

**Residual novelty, narrow but real, and it survives for a technical reason:**
Peikert's *positive* (immunity) result quantifies over **ideals only**, and its
proof leans on `λ₁(𝔮^{-1}) ≥ √n·N(𝔮^{-1})^{1/n}` — an algebraic-norm bound valid
for ideal lattices. **For a non-ideal sublattice of large index that bound
fails.** So "`L` ranging over kernels of `R_q`-module maps *including non-ideal
`R'`-submodules*" is a genuine gap in the published positive result, and that
gap — not the framing — is this lane's contribution.

### What the envelope already says

For ML-KEM (`n = 256`, `q = 3329`, CBD `η = 2`) — **the null control is no longer
an expectation, it is measured.** Max character bias `2^{−381.15}`; exact total
variation from uniform `2^{−378.0}` by big-integer convolution; ~`2^756` samples
to distinguish. **ML-KEM passes with ~373 bits of margin.**

Two corrections to the first draft's reasoning, both material to the instrument:

- `det^{1/n} = 3329^{1/256} ≈ 1.032` is **wrong**. `3329 ≡ 1 mod 256` but **not
  mod 512**, so every prime above `q` has **residue degree 2** and norm `q²`:
  `det^{1/n} = (q²)^{1/256} = q^{1/128} = **1.06541**`. The 1.032 figure is the
  degree-1 value, and it **contradicted this document's own M5 section**, which
  correctly says the slots are degree 2. Internal inconsistency, now resolved
  toward degree 2.
- "its dual contains `Z^n`, so `λ₁(L*) = 1`" is true (verified exhaustively) but
  is **worthless as a diagnostic and must not be built into the instrument.**
  `λ₁(L*) = 1` holds for *every* sublattice of `Z^n`, and feeding it into
  `η_ε(L) ≤ √(ln(2n(1+1/ε))/π)/λ₁(L*)` predicts smoothing **FAILURE** at
  `η = 4.90` — i.e. it fires on every integer-error scheme ever proposed. The
  norm-1 dual vectors are the *trivial* characters. **The correct quantity is the
  shortest nontrivial character in `L*/Z^n`**: norm `3.0477`, giving `η = 1.61`.

The underlying smoothing logic *was* right and is now confirmed by controlled
experiment: short vectors in the **primal** lattice do not hurt smoothing, only
short **dual** vectors do (short-primal case: TV `4.9e−238`, indistinguishable
from a random control). Adjacent verified curiosity, not an attack: the prime
ideal above 3329 contains **exactly 1536 weight-3 ternary vectors** (weight 2 is
provably impossible), e.g. `1 − x^6 − x^240`, so `λ₁ = √3` against a Gaussian
heuristic of 4.125 — ~770× denser than a generic `q^{−2}` count predicts, via a
**parity split** (`ω²` lies in the prime field). ML-KEM still passes.

### The deliverable is an instrument, not a break

A decidable test: given `(n, f(x), q, error distribution)`, compute the maximum
bias over a family of `L` and report. Then scan the zoo nobody has scanned —
FHE moduli, NTT-unfriendly `q`, non-power-of-2 cyclotomics, PLWE with arbitrary
`f`.

**Positive control is available and mandatory:** the instrument must reproduce a
known-weak EHL/ELOS instance. If it cannot, the instrument is wrong and no
negative result from it means anything. Null control: ML-KEM must come out flat.

---

## M6 — Module-native reduction: does the profile *shape* change?

`IDEA-20260806-e5e694` → gated on M1

Every known structured speedup is polynomial: rotations give `≤ 2n` in sieving,
symplectic/Hermitian gives a constant. The asymptotic question is answered (no).
The concrete one is not, and the sharp version is **not "is it faster" but "is
the basis profile a different shape":**

> BKZ's cost is driven entirely by the GSA slope. If tower-recursive reduction
> (Kirchner–Espitau–Fouque style) yields a *piecewise* profile with a flatter
> head — because the top of the subfield tower is reduced exactly — then the
> effective `β` for a fixed Hermite factor differs by more than a constant.

That is measurable at `n = 64…256` with today's tools, and it is a different
question from the throughput comparisons in the literature.

**Ceiling:** constant-factor or log-factor. State it up front so no batch reports
`2n` as an exponent. **Prior-art risk: HIGH** — gate behind M1.

---

## M7 — Quantum: does the S-unit / Stickelberger machinery reach rank ≥ 2?

`IDEA-20260806-53e680` → moonshot, gated on M1 + M9

Biasse–Song gives quantum polynomial-time class-group and S-unit computation for
`Z[ζ_2^k]`; CDPR/DPW convert it to `2^{Õ(√n)}`-approximate ideal-SVP. Every
deployed scheme sits at *polynomial* approximation factors. The gap is the whole
story, and the unexamined question is which half of it is essential:

> Is the `2^{√n}` barrier a limitation of the **technique** (Stickelberger,
> log-unit geometry) or of the **rank-1 setting**? The machinery is about
> principal ideals — rank 1. R-LWE with ≥ 2 samples and M-LWE are rank ≥ 2.

By the organizing claim above, a rank-2 S-unit method would hit R-LWE, NTRU, and
HAWK's module-LIP simultaneously. **This program already owns the most
informative datum in the area:** GOAL-HAWK-001 and KN-OPEN-028 record that the
rank-2 route via nrd-PIP is super-polynomial because Heuristic 4 *failed* while
1–3 verified. That localizes the obstruction. The question worth asking is not
"can rank-2 be done" but "**is the step where Heuristic 4 failed intrinsic to
rank 2, or an artifact of the nrd-PIP presentation?**"

**Honest framing:** a proven obstruction is as valuable as a positive result and
is far more likely. Do not open this lane before M1 and M9 report.

---

## M8 — ℓ∞ / log-embedding BDD — **REOPENED; the first draft closed it for a false reason**

`IDEA-20260806-0f4843` → status changed from `closed` to `proposed`

Every reduction algorithm optimizes `ℓ₂`. The R-LWE error is small in **every
embedding** — a polydisc in the canonical embedding, i.e. a box in the log
embedding, which is exactly the geometry the unit group acts on by translation
and exactly what CDPR machinery manipulates. Nobody has run that machinery on
the *error* instead of on an *ideal generator*. Tempting.

**The stated collapse does not hold.** It is true that with `m = 1` and `a`
invertible mod `q`, `aR + qR = R`, so every `e` is realizable with
`s = a^{-1}(b − e)` — verified 5000/5000. **But that drops the shortness
constraint on `s`.** R-LWE asks for the pair `(s,e)` with *both* short, and that
needle is unique: exhaustive search at `n = 8, q = 3329, B = 1` finds **exactly
one** short-short solution among 6561; at ML-KEM scale the space is `5^256 ≈
2^594` with expected solution count `2^{−1806.6}`. `m = 1` R-LWE is the
NTRU-shaped `2n`-dimensional BDD instance — **if "there is nothing to search"
were true, `m = 1` R-LWE would be trivially broken.**

Off by one in the same paragraph: the `m = 1` lattice `{(s,e) ∈ R²}` **already**
has R-rank 2, so M8 is in M7's setting at `m = 1`, and the collapse argument does
not even do the work of routing it there.

**This is the failure mode the program's rule 9 forbids** — a wrong one-line
reason frozen into the ledger, with an instruction to future batches not to
re-examine it. The real question (can log-embedding / ℓ∞ geometry help BDD on the
rank-2 R-LWE module?) is open, and it is exactly what M7 is gated on. M8 is
therefore **merged into M7's gate**, not closed.

---

## What is deliberately not here

- **Decryption-failure and side-channel amplification** — implementation flank,
  owned by GOAL-MLKEM-001/002, and not a statement about R-LWE the problem.
- **ML on LWE (SALSA/PICANTE/VERDE line)** — sparse-secret, small `n`, and the
  ring angle (rotations as data augmentation) is a poly-factor at best.
- **Sparse-secret hybrid attacks** — already owned by RQ-FHE-001 and KN-OPEN-026,
  and blocked on the same network policy. M1's payoff regime overlaps RQ-FHE-001's
  parameter sets; coordinate rather than duplicate.
- **Chen's 2024 quantum LWE algorithm** — withdrawn; reviving it is not a lane,
  it is a hope.

---

## Recommended first batch

Revised after the pressure test. Three items, all cheap, none dependent on the
others:

1. **M9** (Arora–Ge) — days. The prediction is already confirmed *and upgraded to
   a proof*; what remains is to fix three numbers (`2^41.05` not `2^44`; 1536
   equations not 768; ML-KEM-512 is `η₁ = 3`/degree 7) and delete the
   "deficit exactly `n`" sentence. Closest thing to a finished result here.
2. **M1 prior-art gate — now a single question, not a reading list.** FPS and DvW
   are read; the gate reduces to: **is Karenin–Kirshanova 2024/844 arbitrary-rank
   or rank-2 only?** The PDF is 403-blocked, so this needs an out-of-band copy,
   an interlibrary request, or the AfricaCrypt proceedings. Second question in
   the same gate: how does M1 differ from Ducas–Loyer's 2025/1694 no-go?
3. **M2+M5 κ-surface** — re-derive with the two-dimensional `(κ, β_c)` law and
   confirm the corrected endpoints. **Do not run the revision-1 form**: it
   reports descent beating the primal attack at FHE parameters.

M1's experiment opens only after item 2 resolves. M3/M4 open in the second batch,
M4 re-scoped to the non-ideal sublattice case. M6 and M7 gate on M1 + M9.
**M8 is reopened and merged into M7's gate** — its revision-1 closure reason was
false, and freezing it into the ledger would have been a rule-9 failure.
