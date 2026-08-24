# Pressure test of the R-LWE / M-LWE mechanism portfolio — consolidated verdict

**Target document:** `/Volumes/SSD990/crypto-autoresearcher/ideas/rlwe-mlwe-20260806/PORTFOLIO.md`
(the path was supplied to every verifier as the literal string `undefined`; each one located the
document independently by grep, and all seven agree on the same file and line ranges).

**Companion drafts audited:** `GOAL-RLWE-001/002/003.draft.yaml`, `RQ-RLWE-be8f64/912fdb/fe4e1f.draft.yaml`,
`proposals.draft.yaml`, `README.md` — all in the same directory.

**Scope:** 7 claim clusters verified by exact computation (integer/symbolic arithmetic, Bareiss
determinants, exhaustive enumeration, fpylll BKZ, Monte Carlo with matched nulls), plus 3 prior-art
screening lanes. Nothing in this report is a ledger record.

**Bottom line: 0 of 7 claim clusters survived intact. All 7 came back PARTIALLY WRONG.**
The portfolio's core algebra is sound — every structural identity checks out, several are stronger
than the document argues — but **every headline number that a downstream Executor would act on is
wrong**, and two of them are wrong in a direction that inverts the conclusion.

---

## 1. VERDICT TABLE

| id | what it covers | verdict | corrected value (headline) | adversarial pass overturned first verdict? |
|---|---|---|---|---|
| **C1** | M1 foundation: `(−s,e,1) ∈ M`, `N = R·(−s,e,1) ⊆ M`, Z-rank `n`, "consisting entirely of short vectors" (PORTFOLIO.md 96–112) | **PARTIALLY WRONG** | (a),(b),Z-rank `n` exact. "Entirely of short vectors" is false — `‖r·v‖ ≥ ‖r‖`, unbounded. Correct invariant: `λ₁(N)=…=λ_n(N)=‖(s,e,1)‖`; `det(N)^{1/n}=6.2875` vs `det(M)^{1/32}=57.6975` (n=8,m=2,q=3329) | **No.** Refutation pass skipped (verdict already negative). One *internal* self-refutation did fire and was honoured: the first hand-built coordinate matrix failed its own reconstruction check `C·B_M = B_N` and was discarded in favour of an exact rational solve. |
| **C2** | M1 trade table: dim, covolume, normalized covolume, dimension penalty; implied `vol(N)` (PORTFOLIO.md 116–121) | **PARTIALLY WRONG** | `covol(M)=q^{mn}`, `dim=(m+2)n`, `q^{m/(m+2)}` all exact. Kannan normalized covolume is `q^{mn/((m+1)n+1)}`, **not** `q^{m/(m+1)}` (45.45 vs 57.70 at n=8,m=1,q=3329). Dimension penalty is **n−1**, not `n`. Implied `vol(N)^{1/n} ≈ σ√((m+1)n)` is a strict AM-GM over-estimate; true value `σ√n·exp(ψ(m+1)/2)` | **No.** Skipped, already negative. |
| **C3** | M2 descent: identity `y₀=α·s₀+E₀`, "honest R'-LWE sample", condition count (PORTFOLIO.md 229–244) | **PARTIALLY WRONG** | Identity exact **mod q** (0/144 failures; control fails 100%). Rank exactly `n/2 = (f−1)n/f`, 25/25 at every parameter set. `q^{1/(fm)}` exact. But noise per-coefficient sd is `‖c‖·σ` (**41.6** at ML-KEM params), not `‖c‖·σ√n = 670`; α is **not** uniform in `R'_q`; descended samples are **not independent** beyond ≈2m | **No.** Skipped, already negative. |
| **C4** | M2+M5 envelope: E1 (ML-KEM) and E2 (FHE) block sizes (PORTFOLIO.md 263–292) | **PARTIALLY WRONG** | `q^{1/4}=7.596`, `‖c‖=41.59`, `β_before=367.2`, ring expansion constant **exactly 1** — all confirmed. But E2 "**370 → 420**" is wrong in magnitude *and sign*: under the document's own exchange law it is **367 → 201** (descent WINS). Honest two-axis figure `max(β_c, β_resid)` = **560 vs 367** (E2), **233 vs 152** (E1). E1 "kills the instance outright" is false — 80× noise headroom, `β` 152.445 vs 152.444 (dead even) | **No.** Skipped, already negative. Four modelling variants were tried adversarially to reproduce 420 and none did (385/319/386/319/205/206; only "dimension does not halve" gives 562, which negates the construction). |
| **C5** | M4 envelope: prime-ideal density, dual contains `Z^n`, ML-KEM smoothing (PORTFOLIO.md 380–384) | **PARTIALLY WRONG** | Prime above 3329 has residue degree **2**, index `q²`, so `det^{1/n} = q^{1/128} = **1.06541**`, not `q^{1/256} = 1.032`. `λ₁(L*) = 1` exactly — but it is a useless diagnostic (true for *every* sublattice of `Z^n`; predicts smoothing FAILURE at `η=4.90`). Correct quantity: shortest nontrivial character in `L*/Z^n`, norm **3.0477** → `η = 1.61`. ML-KEM verdict **PASS confirmed and quantified**: max character bias `2^-381.15`, exact TV `2^-378.0` | **No.** Skipped, already negative. A controlled counter-experiment was run (short primal vector + generic dual → TV `4.9e-238`, indistinguishable from random control) confirming the author's smoothing reasoning. |
| **C6a+C6b** | M9 Arora–Ge starvation (182–220) and M8 collapse (447–464) | **PARTIALLY WRONG** | `C(773,5) = 2,270,319,562,049 = **2^41.05**`, not `2^44`. `η=2` is wrong for **ML-KEM-512** (η₁=3 for *both* s and e → degree 7, `C(519,7)=2^50.78`). Equations available are **1536**, not 768. "Deficit exactly `n`" is unsupported (measured Galois redundancy `n(n−1)`; deficit vs unstructured control **0**). **M8's closure reason is false**: shortness of `s` was dropped; search space `2^594`, exactly 1 short-short solution, verified exhaustively at n=8 | **No.** Skipped, already negative. The M9 *prediction* was adversarially attacked with four independent equation sources (Galois, rotations, pairwise products, short-multiplier `‖c‖₁=2`) and held at rank increase **exactly 0** everywhere. |
| **C7** | M1 payoff regime: NTRU fatigue point, ML-KEM margin, FHE band, RNS (PORTFOLIO.md 138–149) | **PARTIALLY WRONG** | Exponent 2.484 confirmed exactly (real root of `Q³−2Q²−Q−½`). But the concrete fatigue point is `q ≈ **0.004**·n^2.484`, so at n=256 it is **3838 = 2^11.906** and ML-KEM's `q=3329` is **0.205 bits below it, not 8 bits**. FHE band is `2^24.3–2^29.3`, not `2^32–2^37`. Exponent holds only for σ=Θ(1) (Q*(S) = 2.15/2.48/2.78/3.18/3.73 at S=0.4/0.5/0.6/0.75/1.0) | **No.** Skipped, already negative. |

**Summary: 7 clusters checked, 7 partially wrong, 0 fully confirmed, 0 fully refuted.**
No adversarial re-check overturned a first verdict; the refutation pass was skipped in every case
because the verdict was already negative. Note that this means **no claim in this portfolio has been
adversarially attacked from the "it might be right after all" direction** — the negatives are firm,
but the *surviving* sub-claims listed in §3 carry only the strength of the primary verification.

---

## 2. WHAT IS BROKEN

Ordered by how much of the portfolio depends on it. Blunt.

### B1 — The κ-curve exchange law is missing the only term that decides the family. GOAL-RLWE-003's pre-registered ceiling is VOID as written. (C4)

PORTFOLIO.md line 271 says *"Minimizing over the single parameter `κ` settles the entire family at
once."* It does not. The exchange law on line 266–268 sets `‖c‖ = L(κ) = q^{κ/(mn)}·√(mn/2πe)` — the
Gaussian heuristic — and then charges only `[solve residual] + [FFT over V]`. **`L(κ)` is a lower
bound on what lattice reduction can produce, not what it does produce.** BKZ-β_c returns
`‖c‖ = δ(β_c)^{mn}·q^{κ/(mn)}`. Feeding that in:

- Reaching `L(κ)` at E2 (n=2^15, mn=65536) requires **β_c = 65539 > d**, i.e. exact SVP, cost ≈ 2^19137.
- Reaching `L(κ)` at E1 (n=256, mn=512) requires **β_c = 516 > d = 512**, again exact SVP.

Consequence: **an Executor who implements GOAL-RLWE-003 exactly as specified will compute that
descent BEATS the direct attack.** With a 2016-uSVP estimator calibrated to reproduce ML-KEM-512
β=406 and ML-KEM-768 β=624, the document's own assumption gives:

| | document says | correct under the document's own assumption | honest two-axis cost |
|---|---|---|---|
| E2 (FHE) | β 370 → 420, "descent still loses" | β **367 → 201** (descent wins by 166) | `max(β_c,β_resid) = 560` vs 367 direct — descent loses by ~190 |
| E1 (ML-KEM) | noise 670 ≈ q, "kills the instance outright" | β **152.444 → 152.445** — exactly noise-neutral | `max = 233` vs 152 direct — descent loses by ~80 |

The document's *conclusion* ("descent still loses") survives, but **for a reason the document states
backwards**. Line 287–288 says descent loses *"because `‖c‖` is pinned to the Gaussian heuristic of a
dimension-`mn` lattice and cannot be beaten."* If `‖c‖` really sat at the Gaussian heuristic, descent
would **win**. Descent loses because `‖c‖` cannot **reach** the heuristic.

**Records made void:** `GOAL-RLWE-003.ceiling_known_in_advance` (lines 36–47) and
`RQ-RLWE-912fdb.constraints[3]` (lines 58–64) both record the 670 / 370→420 figures as the
pre-registered expected negative. Both are wrong. `IDEA-20260806-35d60b.predicted_effect`
("A QUANTIFIED NEGATIVE") is unearned as stated. A batch that "reproduces this is succeeding" —
RQ-RLWE-912fdb line 62–63 — cannot reproduce it, because it is not true.

### B2 — The noise figure driving M2's headline carries a spurious factor of √n. 670 should be 41.6. (C3, C4)

PORTFOLIO.md line 267 writes `noise ≈ L(κ)·σ·√n·c_ring` and line 281 evaluates `42·1·16 ≈ 670`
against `q = 3329`, concluding *"The noise saturates the modulus — one level of descent kills the
instance outright."*

Measured across n ∈ {8,16,64,256}, m ∈ {2,3}, σ ∈ {1,3.2}, 400 reps, **the per-coefficient standard
deviation of `E = Σ cᵢeᵢ` is `‖c‖₂·σ` to within 2% in all 16 configurations.** `670` is the *L2 norm*
of `E` across 256 coefficients. The quantity comparable to a scalar modulus `q` is **41.6**, giving
`q/σ_E = 80` — nowhere near saturation. Comparing a 128-dimensional Euclidean norm to a scalar
modulus is a category error, and even at face value 670 < 3329.

Two refinements, both verified: the ring expansion constant is **exactly 1** (symbolically proved for
ternary `e` at n=8; measured 1.000 at n=64,256 — the apparent 1.039 at σ=1 is entirely
`std(rint(N(0,1))) = 1.0409`, the Gaussian rounding), so the document's `√n` is correct *for the norm*.
And `‖E₀‖`, the noise actually attached to the dimension-(n−κ) residual, is `‖c‖σ√(n−κ)` — a factor
`√f` below the formula on line 267. At FHE scale the noise **growth factor** is `L = 2^205.95`, not
`2^215.13`; `2^215` is the norm.

The error runs **against** the document's own conclusion. Uncorrected it closes the ML-KEM branch on
arithmetic that does not support closure.

### B3 — ML-KEM is 0.2 bits from the NTRU fatigue point, not 8. M1's entire scoping decision is on the wrong side of it, and the mandatory control is miscalibrated by ~250×. (C7)

PORTFOLIO.md line 138–140: *"Ducas–van Woerden put the NTRU fatigue point near `q ≈ n^2.484`; for
`n = 256` that is `≈ 2^19.9`, and ML-KEM's `q = 3329 = 2^11.7` is well below it."* The arithmetic is
right; the conclusion is not. **DvW's own concrete fatigue point, in the same abstract and explicitly
stated valid for n > 100, is `q ≈ 0.004·n^2.484`.** The constant is `2^-7.966` and it consumes the
entire claimed margin:

| | n=256 concrete fatigue `q*` | ML-KEM `q=3329` margin |
|---|---|---|
| ring degree n=256 | 3838 = 2^11.906 | **+0.205 bits** |
| module dim 512 (ML-KEM-512) | — | +2.69 bits |
| module dim 768 (ML-KEM-768) | — | +4.14 bits |
| module dim 1024 (ML-KEM-1024) | — | +5.17 bits |

Cross-checked against DvW's two §5.2 regressions: `0.0038·n^2.484 → +0.131 bits`;
`0.0034·n^2.506 → +0.147 bits`. Sanity check on the same formula: deployed NTRU sits at +3.37 / +2.52 /
+4.08 bits (HPS2048509 / HRSS701 / HPS4096821), matching DvW's own "we do not contradict NTRU's
concrete security". **The paper anticipates this exact mistake verbatim** (§ after the asymptotic
derivation): *"In practice however we do observe fatigue points that are significantly lower than the
naive value of q = n^2.484, which motivates a concrete analysis."* The corpus records the constant in
three places (KN-LIT-114, KN-TECH-045 complexity field, KN-TECH-045 obligation 1).

Two independent consequences, in opposite directions, both bad:

1. **AGENTS.md rule 4 violation.** PORTFOLIO.md line 33–34 says *"nothing here is a statement about
   ML-KEM"*. Line 138–140 **is** a quantitative safety statement about ML-KEM, and it is wrong. If M1's
   own hypothesis (the exponent transfers to the module presentation) is even approximately right,
   ML-KEM's ring degree sits **at** the NTRU fatigue point, inside the regime the portfolio declared
   out of scope.
2. **The mandatory NTRU control would be run at moduli ~250× too large.** PORTFOLIO.md line 163–165
   makes the matched-(n,q) NTRU control the point of the design and requires *"NTRU must show DSD
   where the literature says it does."* On the naive curve the expected fatigue at n=64 is `q ≈ 2^14.9`;
   the concrete value is `q ≈ 2^7.0`. The control would fire everywhere and be read as validating a
   detector that is in fact saturated. GOAL-RLWE-001's first completion criterion — the control
   firing *before* any R-LWE reading is interpreted — would be discharged by a broken instrument.

Also broken in the same paragraph: the FHE band `n^2.484 is 2^32–2^37` should read **2^24.3–2^29.3**
on the concrete curve, and the exponent 2.484 is stated unqualified when it holds only for
`σ = Θ(1)` (ternary). Solving the same DSD/SKR crossover at other secret widths gives
`Q*(S) = 2.152 / 2.484 / 2.781 / 3.176 / 3.732` at `S = 0.4/0.5/0.6/0.75/1.0`. Separately, the
constant 0.004 is calibrated on **matrix** NTRU (DvW Fig. 7), while M1's object is **circulant** —
which DvW explicitly differentiate, noting matrix "slightly favours the attacker" and circulant shows
"a larger variance in the concrete hardness". M1 currently has **no legitimate NTRU reference value**
for the fitted exponent `c` in its success criterion.

Final item in the same claim: PORTFOLIO.md line 16 asserts *"No primary source was read"* and line
22–25 treats eprint unreachability as plausibly gating the prior-art step. **Both DvW and
Felderhoff–Pellet-Mary–Stehlé are already on disk with full text** (`/Volumes/SSD990/research/classified/other/130900104.txt`
and `/Volumes/SSD990/research/137910070.pdf`, indexed as KN-LIT-5246 and KN-LIT-5365). The M1
prior-art gate is not network-blocked and can be partially cleared today.

### B4 — M9's three numbers are wrong and its one quantitative claim is unsupported. The prediction itself is right, and stronger than claimed. (C6a)

1. **`≈ C(773,5) ≈ 2^44`** (line 193–194) is **2,270,319,562,049 = 2^41.05**. Off by 2.95 bits.
   Reaching 2^44 at degree 5 would need N ≥ 1159 variables. The closest ML-KEM set is 1024 at 2^43.11.
2. **`CBD η = 2 ⟹ support [−2,2]`** (line 190) is stated about ML-KEM generally. True for 768 and 1024.
   **False for ML-KEM-512**, where FIPS 203 uses `η₁ = 3` for *both* the secret and the KeyGen error
   (verified against the vendored pq-crystals script at
   `experiments/EXP-MLKEM-001/vendor/pq-crystals-security-estimates/Kyber.py`), giving support
   `[−3,3]`, **degree 7**, and `C(519,7) = 2^50.78` monomials — a ~10-bit error for anyone who
   instantiates the lane at 512.
3. **`m = 256·3 = 768` scalar samples** undercounts by exactly 2×. ML-KEM's *secret* is CBD-bounded
   too, contributing 768 more degree-5 equations `∏_{k=−2}^{2}(sᵢ−k)=0`. **1536, not 768.** This
   matters more than the bit count: in the small-n experiments the secret equations were the **only**
   source that ever raised the Macaulay rank (n=4, D=6: **134 → 209 of 210 monomials — essentially
   solving the system**), while every ring-derived construction raised it by exactly zero. The
   starvation argument is aimed at the wrong quantity. The verdict survives (1536 ≪ 2^41) but the
   lane would reopen the moment a referee notices.
4. **"the rank deficit is exactly `n` per ring sample, invariantly"** (line 205–206) is unsupported
   and ill-posed. Measured: the Galois orbit's redundancy is `n(n−1)` per ring sample (n² conjugate
   equations collapse to exactly n independent ones), and the rank **deficit versus an unstructured
   control with matched equation and variable counts is 0**, not n. This is the single sentence in M9
   a referee would attack, and no measurement supports it.

### B5 — M8 is closed for a false reason, and the reason, if true, would be a bigger claim than anything else in the portfolio. (C6b)

PORTFOLIO.md line 458–460: *"every `e` is realizable with `s = a^{-1}(b − e)`, and there is nothing to
search."* The premise is correct (5000/5000 random `e` realizable). **The inference is a non-sequitur:
it drops the shortness constraint on `s`.** R-LWE asks for the pair (s,e) with *both* short.
Exhaustive search at n=8, q=3329, B=1 found **exactly 1 short-short solution among 6561** — a unique,
well-defined needle. At ML-KEM scale the space is `(2η+1)^n = 5^256 ≈ 2^594` with expected solution
count `2^-1806.6`: unique and hard. m=1 R-LWE is precisely the NTRU-shaped 2n-dimensional BDD
instance. **If "there is nothing to search" were true, m=1 R-LWE would be trivially broken.**

Secondary, off by one: *"The method needs `m ≥ 2`, which lands on a rank-2 module"* — the m=1 lattice
`{(s,e) ∈ R²}` **already** has R-rank 2. So M8 is in M7's setting at m=1, and the collapse argument
does not even do the work of routing it there.

This is the failure mode the program's own rules forbid: `IDEA-20260806-0f4843` is marked
`status: closed`, and PORTFOLIO.md line 492 instructs future batches not to rediscover it. A wrong
one-line reason gets frozen into the ledger and the lane never gets re-examined — while the real
question (can log-embedding / ℓ∞ geometry help BDD on the rank-2 R-LWE module?) is genuinely open and
is exactly what M7 is gated on.

### B6 — M1's trade table charges the wrong dimension penalty and the wrong Kannan density; both biases run against M1. (C2)

1. **Dimension penalty is `n−1`, not `n`.** `(m+2)n − ((m+1)n+1) = n−1`. Verified as 1, 3, 7 at
   n = 2, 4, 8 (independent of m). PORTFOLIO.md line 123–124 and line 170 both say `n`. Line 170 is
   the **decisive success criterion** — *"after charging the `n` extra dimensions"* — so the module
   side is overcharged by one dimension in every β comparison M1 will ever run.
2. **Kannan normalized covolume `≈ q^{m/(m+1)}` is an n→∞ limit presented as if it applied at the
   tested sizes.** Exact value: `q^{mn/((m+1)n+1)}`. At the document's own sweep points this is 12–21%
   low: n=8,m=1,q=3329 gives **45.45**, not 57.70; n=8,m=2 gives **179.59**, not 222.95. The module
   side (`q^{m/(m+2)}`) is written exactly, so the two sides of the comparison table are not computed
   to the same standard. Any fatigue exponent `q*(n) ≈ n^c` fitted from the small-n sweep — M1's
   promised deliverable — will be systematically shifted.

Both biases flatter Kannan, so the **qualitative** conclusion of the table survives — and it survives
by a stronger route than the document offers: **the Kannan lattice with τ=1 is literally the section
`M ∩ (R^{m+1} × Z·1)`**, of identical determinant `q^{mn}` (verified: n=8,m=1,q=97, section dimension
17, det 97^8, identical to the Kannan basis). So `M` is the Kannan lattice plus `n−1` dimensions of
**unit density**. That is the airtight form of "strictly worse for the uSVP event" and should replace
the current prose.

3. **The implied `vol(N)` heuristic is always an over-estimate, by a factor that does not vanish.**
   The document does not write `vol(N)^{1/n} ≈ σ√((m+1)n)`, but it is the formula an Executor will
   reach for, and it is `√(arithmetic mean of A_k)` where the truth is the `geometric mean of √A_k`.
   By AM-GM it is a **strict** over-estimate, always. Closed form:
   `vol(N)^{1/n} → σ√n·exp(ψ(m+1)/2)` = `0.8736·σ√(2n)` (m=1), `0.9158·σ√(3n)` (m=2). Measured at
   n=8 (400 instances, σ=3.2): 1.128× (m=1), 1.062× (m=2); converged to the closed form out to n=2048.
   **Direction matters: this makes the dense submodule look less dense than it is**, i.e. the metric
   is biased toward M1's own most-likely-outcome null ("the n-dimension penalty swamps any DSD gain").
   A false negative here would close M1's lane for the wrong reason. Fix is cheap: compute `vol(N)`
   per instance as the exact integer `isqrt(det Gram)` (always a perfect square).
4. **The rotation basis is not near-orthogonal.** Orthogonality defect `δ^{1/n} → exp((ln(m+1)−ψ(m+1))/2)`
   = 1.1447 (m=1), 1.0919 (m=2); total `δ` = 2.4 at n=8, 1.3e7 at n=128, 4.7e117 at n=2048. Any DSD
   detector that infers "Z-rank n and x-stable" from vector lengths alone is miscalibrated by `1.14^n`
   and will misclassify at the n=32–64 end of the planned sweep.
5. Per-instance spread at n=8 is wide (heuristic/true from 0.88 to 1.51 over 12 exact instances), so
   **the planned n=8 sweep cannot read a fatigue point off single instances.**

### B7 — M4's prime-ideal density is off by a factor of 2 in the exponent, and its stated dual diagnostic fires on everything. (C5)

1. PORTFOLIO.md line 382: *"`det^{1/n} = 3329^{1/256} ≈ 1.032`"*. **3329 ≡ 1 mod 256 but not mod 512**,
   so every prime above q has **residue degree 2** and norm `q²`. Row reduction of the 256×256
   multiplication matrix gives rank 254 and index `q² = 11082241`. Correct normalized determinant:
   `(q²)^{1/256} = q^{1/128} = **1.06541**`. The document's 1.032 is a correct evaluation of `q^{1/256}`
   — the value for a **degree-1** prime — which **directly contradicts M5's own claim on line 248–250**
   that the slots are degree 2. The portfolio is internally inconsistent. Downstream: the Gaussian
   heuristic for `λ₁` is 4.125, not 3.996, and any ranking of rings by normalized ideal density that
   uses `q^{1/n}` will misrank ML-KEM against fully-split-NTT schemes where `q^{1/n}` genuinely *is*
   correct.
2. *"its dual contains `Z^n`"* is true, and exhaustive minimization over all 11,082,240 nonzero dual
   codewords confirms `λ₁(L*) = 1` **exactly**. But as a smoothing diagnostic it is worthless: the
   norm-1 dual vectors are integer vectors, i.e. the **trivial** characters for an error supported on
   `Z^n`. Feeding `λ₁(L*)=1` into `η_ε(L) ≤ √(ln(2n(1+1/ε))/π)/λ₁(L*)` gives `η = 4.90` at ε=2^-100,
   far above the CBD width of 1 — **falsely predicting smoothing FAILURE**. Since this is true for
   *every* sublattice of `Z^n`, an automated instrument built on it flags every integer-error scheme.
   M4 is meant to be a null control; a test that fires on everything has no discriminating power.
   The correct quantity is the shortest **nontrivial** character in `L*/Z^n`: norm **3.0477**, giving
   `η = 1.61`.

### B8 — "an honest R'-LWE sample" is not honest: α is measurably non-uniform and the descended samples are not independent. (C3)

1. **α is not uniform in `R'_q` over short c.** Against a Monte-Carlo null matched to the population's
   *exact* symmetry (the law is provably invariant under `c ↦ x²c`, acting as `α ↦ y·α`, an order-8
   group — a structure the document does not mention, and one that inflates naive df-based χ² nulls by
   ~√2), specific Fourier modes carry **3.8–6.1× the maximum bias uniform sampling ever produces**
   (max|F̂| = 0.024–0.038 vs 0.0063; z = +37 to +66 across three instances), while the distribution is
   simultaneously strongly under-dispersed (8/160/80 collisions vs null 780–806; z = −8 to −11).
   **The deviation strengthens as c gets shorter.** The portfolio flags this as an unproven heuristic
   (`IDEA-20260806-35d60b.risks[0]`), which is honest — but the heuristic is **false**, not merely
   unproven. Because the excess bias is concentrated in specific Fourier modes, it lands precisely on
   the FFT-over-V step that M5 and the unified κ-curve depend on.
2. **The descended samples are not independent, and this is flagged nowhere.** The noise tuple
   `(E₀^{(1)},…,E₀^{(N)})` is the image of the *fixed* mn-dimensional error vector under a linear map
   determined by the `c_j`. Measured rank **12 = mn − n/2** for N=10 samples living in `Z^40`. Beyond
   roughly `N = 2m` samples the "R'-LWE instance" has strictly less noise entropy than an honest
   oracle would supply. `E₀` is also a deterministic function of `c` and hence correlated with `α`.
   This **directly undercuts "Dimension halves per level" as a recursion** (PORTFOLIO.md line 237–238)
   and must be stated before any multi-level descent is costed.

### B9 — M1's "consisting entirely of short vectors" is false of every lattice. (C1)

PORTFOLIO.md line 110–112. `N = R·(−s,e,1)` contains `r·v` for **every** `r ∈ R`, and because the
z-coordinate of `r·v` is `r` itself, `‖r·v‖ ≥ ‖r‖` is unbounded — measured median `1.03e10` at
`|r|_∞ ≤ 1e9` against `‖v‖ = 6.4031`. Only the 2n vectors `±x^k·v` attain `‖v‖`. This conflates
"N is spanned by n short vectors" (true, and the property DSD needs) with "every vector of N is short"
(false, and false for every lattice). Prose defect only — the mechanism is unaffected, and the
document's own detector spec on line 161 already asks the right question.

---

## 3. WHAT SURVIVED

These took a real computational pass and held. Several are **stronger** than the document claims.

**M1 foundation (C1, C2) — the load-bearing algebra is exact.**
- `(−s,e,1) ∈ M`: 0 failures in 24 instances (n∈{4,8} × q∈{97,3329} × m∈{1,2} × 6 seeds).
- `N ⊆ M`: 0 failures in **3744** membership tests with `|r|_∞` up to `1e12`, plus structured `r`.
  Noted: this is *automatic* — `M` is the kernel of an R-module homomorphism `R^{m+2} → (R/qR)^m`,
  hence an R-submodule, so (b) follows from (a) with no extra content.
- `dim_Z(M) = (m+2)n` and `covol(M) = q^{mn}` **exactly**, verified by Bareiss determinant at five
  parameter sets (e.g. n=8,q=3329,m=2 → det = 3329^16 exactly), and robust to composite q (64, 100),
  `a₁ = 0`, and non-invertible `a`.
- Normalized covolume `q^{m/(m+2)}` exact: 0.000% relative error in all 12 instantiations.
- Z-rank of N is n inside dim (m+2)n.

**Two facts the document does not claim, which favour M1** (C1): `N` is a **primitive (saturated)**
sublattice of `M` — Smith normal form elementary divisors all 1 in M-coordinates at all five parameter
sets, by two independent routes — and `N` is **not contained in `qR^{m+2}` in any coordinate block**
(per-block gcds all 1; the z-block is literally `I`). These are the two conditions that would have made
the dense submodule invisible to BKZ. There is no lattice-theoretic obstruction.

**M1's central structural contrast is real and reproducible at toy scale** (C1, bonus probe). BKZ
block 20, n=8, m=2, q=3329: on `M` (dim 32) the eight shortest vectors all have norm² = 41, the next is
31410, and the eight span `N` with Z-rank 8 — **the DSD event fires**. On the matched Kannan lattice
(dim 25, same determinant `3329^16`, target norm² = 41 present) the shortest is 41, the next is 72516,
and the set of vectors with norm² ≤ 41 has **Z-rank 1**. The document's table row "dense rank-n
submodule: Kannan no / module yes" is confirmed by measurement.

**M2's reduction identity and condition count (C3) — exact, and operationally real.**
- `y₀ = α·s₀ + E₀` holds **exactly in `R'_q`** for every constructed instance (n∈{8,16}, q∈{97,3329},
  m∈{2,3}), 48/48 or 32/32 per configuration. A control with `α ∉ R'_q` fails **100%** of the time,
  so the test has power. Holds mod q only, not over Z (the integer lift of α carries odd coefficients
  that are nonzero multiples of q) — worth stating explicitly.
- The stated reason is correct: multiplication by α in R' preserves R' and xR'.
- Condition count is exactly right: `rank_{F_q}` of `c ↦ odd(Σcᵢaᵢ)` is `n/2 = (f−1)n/f` in **25/25**
  trials at every parameter set, versus n for the classical α=0 map. `q^{1/(fm)}` reproduces exactly.
- `s₀` recovered **12/12** from the descended instance at n=8→4, q=97, m=2. The reduction works.

**C4's confirmed envelope numbers.** `q^{1/4} = 7.5959` (doc 7.6); `‖c‖ = L = 41.5888` (doc ~42);
`L·σ·√n = 665.4` (doc ~670 — internally consistent, just the wrong quantity); `‖E‖ = 2^215.13`
(doc 2^215); `β_before = 367.2` (doc ~370). And the **ring expansion constant is exactly 1**, proved
symbolically (`E[‖c·e‖²] = n·σ²·‖c‖²` by exact rational expansion at n=8) and measured at n=64,256 —
so the `√n` in the norm is right and the envelopes do not move for that reason.

**M9's core prediction (C6a) — confirmed, and upgraded from measurement to proof.** Galois conjugates,
rotations, pairwise products, **and** short-multiplier equations (`c = x^i ± x^j`, `‖c‖₁ = 2`, which the
portfolio did not consider) give rank increase **exactly 0**, at every n, q, B, m, D tested. Of all
Galois-conjugate equations generated (4, 8, 16, 32, 48, 64 of them), the count not equal to ±(a plain
equation) was **0/N in every configuration**; `|galois_set \ rotation_set| = 0`. And it is now a
theorem, not a table: for all `t ∈ (Z/2n)*`, `P_t` is a signed permutation and
`P_t·Neg(a) = Neg(σ_t(a))·P_t` (verified n∈{2,4,8,16}, 20 random `a` each), so the conjugated affine
forms are `±A_{π(j)}`; since the support `[−B,B]` is symmetric, `∏_k(−A−k) = (−1)^{2B+1}∏_k(A−k)`.
**Galois returns the same polynomials up to sign.** This is what M9 should bank.

**M4's ML-KEM verdict (C5) — PASS, confirmed and quantified far beyond the document's argument.**
Max character bias `2^-381.15` (at half-support characters, because ω² lies in the prime field);
**exact** TV from uniform `2^-378.0` via exact big-integer convolution over `Z_q` (128-step, total
`16^128`, verified); ~`2^756` samples to distinguish. Monte Carlo at 2e6 samples sits cleanly at the
noise floor (χ² z = 1.78 on the `F_q` marginal, z = −0.50 on 64×64 joint buckets). The bias formula
was validated to 8 digits against exhaustive enumeration in a small analogue (n=8, q=41). **ML-KEM
passes with ~373 bits of margin.** The factorization claim also holds exactly: `x^256+1` factors into
128 irreducible quadratics (product verified coefficient-by-coefficient), slots are `F_{q²}` of size
11082241 = 2^23.4017, and no element of `F_3329` has order 512.

**M4's smoothing reasoning (C5) — confirmed by controlled experiment.** Short vectors in the *primal*
lattice do not hurt smoothing; only short *dual* vectors do. Exact TV for three lattices: all-ones
dual vector 0.00481 → TV `9.68e-01` (no smoothing at all); short primal `√3` vector with generic dual
→ TV `4.93e-238`, **indistinguishable from a random control at `4.93e-234`**. ML-KEM's prime ideal
lattice is exactly the benign case.

**M1's RNS observation (C7e) — correct in both derivation and direction.** Instantiated exactly at
n=16 with `q = 7681·12289·40961`: for each `qᵢ`, `b = a·s + e (mod qᵢ)` holds identically, the
recovered centred error is **the original small `e`** (not a rescaled one), and `s` lifts exactly.
The converse provably fails (CRT-recombining three independent small errors gives `‖E‖_∞ = 1.49e12`
against `q/2 = 1.93e12` — not short). "Large q is the attacker's friend" independently confirmed with
a standard primal estimate: β = 594, 328, 207, 97, ≤45 at log₂q = 20, 30, 40, 60, 80 (n=1024, σ=3.2),
strictly monotone decreasing.

**M1's FHE gap (C7d) — confirmed and understated.** Recomputed for n ∈ {2^13,2^14,2^15} × log₂q ∈
{200,400,600,900}: 162.7–867.7 bits above the bare curve, **170.7–875.7 bits** above the concrete
`0.004·n^2.484` curve (51–264 decimal orders of magnitude). The FHE motivation for M1 is undamaged.

**The DvW exponent itself (C7a).** 2.484 re-derived from scratch as the real root of
`Q³ − 2Q² − Q − ½ = 0` → **Q* = 2.4836825706980122**, with relative block size at fatigue
`B* = 0.55798` agreeing on both branches.

**Adjacent, verified, not in the document but worth recording (C5).** Sparse ternary vectors in the
prime ideal above 3329: **weight 2 is provably impossible** (exhaustive over all 32,640 supports × 2
signs; `ord(ω) = 512` and index gaps ≤ 255), **weight 3 exists — exactly 1536 of them** (e.g.
`1 − x^6 − x^240`, `1 + x^42 + x^92`, re-verified by independent polynomial division mod `x²−17` over
GF(3329)), so `λ₁(L) = √3 = 1.732` against a Gaussian heuristic of 4.125. The mechanism is the
**parity split** (ω² = c lies in the prime field, so a vector supported entirely on even or entirely on
odd indices needs only *one* `F_q` collision), not "the field is too small" — actual density
1536/22108160 = 1/14393, about **770× denser** than a generic `q^-2` heuristic would predict. None of
this is an attack; the vectors are primal and ML-KEM still passes.

---

## 4. REQUIRED EDITS

Numbered, actionable without re-reading the verification. Quoted text is verbatim from the current
files. **E1–E9 are blocking** (a record is void or an experiment would produce a wrong answer);
E10–E23 are corrections; E24–E27 are process.

### PORTFOLIO.md

**E1 (BLOCKING) — line 266–271, the κ-curve exchange law. Make it two-dimensional.**
Replace:
```
‖c‖ ≈ L(κ) = q^{κ/(mn)} · sqrt(mn / 2πe)        (Gaussian heuristic)
residual instance:  dimension  n − κ,  modulus q,  noise ≈ L(κ)·σ·√n·c_ring
total cost = [reach ‖c‖ = L(κ) in dim mn] + [solve residual] + [FFT over V]
```
```
**Minimizing over the single parameter `κ` settles the entire family at once.**
```
with:
```
‖c(β_c)‖ = δ(β_c)^{mn} · q^{κ/(mn)}      (what BKZ-β_c actually returns)
L(κ)     = q^{κ/(mn)} · sqrt(mn / 2πe)   (Gaussian heuristic: a LOWER BOUND, not attainable)
residual instance:  dimension n − κ,  modulus q,
                    per-coefficient noise sd = ‖c‖·σ   (c_ring = 1, measured exactly)
                    ‖E_0‖ = ‖c‖·σ·√(n−κ)
total cost = max( β_c , β_resid(‖c(β_c)‖) ) + [FFT over V]
```
```
**The curve is TWO-dimensional: (κ, β_c). Minimizing over κ alone with ‖c‖ = L(κ)
plugs in an unattainable vector length and reports that descent WINS
(β 367 → 201 at FHE scale). Reaching L(κ) requires β_c = 65539 > d at
n = 2^15 and β_c = 516 > d = 512 at n = 256 — exact SVP in both cases.**
```

**E2 (BLOCKING) — line 279–288, both envelope evaluations.**
Replace:
```
At **ML-KEM-ish** parameters (`n = 256`, `q = 3329`, `σ ≈ 1`, `m = 2`, `f = 2`):
`covol^{1/512} = q^{1/4} ≈ 7.6`, `‖c‖ ≈ 7.6·√(512/2πe) ≈ 42`, so the descended
noise is `≈ 42·1·16 ≈ 670` against `q = 3329`. The noise saturates the modulus —
**one level of descent kills the instance outright.**

At **FHE-ish** parameters (`n = 2^15`, `log q = 800`, `σ = 3.2`, `m = 2`), one
descent level costs `≈ 2^215` of noise growth while halving the dimension, and
the crude uSVP estimate moves `β` from `≈ 370` to `≈ 420` — **descent still
loses**, because `‖c‖` is pinned to the Gaussian heuristic of a
dimension-`mn` lattice and cannot be beaten.
```
with:
```
At **ML-KEM-ish** parameters (`n = 256`, `q = 3329`, `σ ≈ 1`, `m = 2`, `f = 2`):
`covol^{1/512} = q^{1/4} = 7.596`, `‖c‖ = L = 41.59`, so the descended
per-coefficient noise sd is `41.59` against `q = 3329` — **80× headroom, not
saturation.** (`665` is the L2 norm of E across 256 coefficients and is not the
quantity comparable to a scalar modulus; `‖E_0‖ = 470.5`.) The residual is a
well-posed uSVP instance: against the model's own baseline (one ring secret,
dim 256, m = 2) the residual block size is `152.445` versus `152.444` direct —
**descent at ML-KEM parameters is noise-NEUTRAL, not fatal.** It loses only once
the cost of producing `c` is charged: `max(β_c, β_resid) = 233` versus 152 direct.

At **FHE-ish** parameters (`n = 2^15`, `log q = 800`, `σ = 3.2`, `m = 2`), one
descent level costs a noise GROWTH FACTOR of `L = 2^205.95` (`‖E‖ = 2^215.13` is
a norm, not a factor) while halving the dimension. Under the Gaussian-heuristic
`‖c‖` the uSVP estimate moves `β` from `367` to `201` — **descent WINS**, and
that is the artifact, not the answer. Charging the cost of producing `c`,
`max(β_c, β_resid) = max(560, 548) = 560` versus `367` direct — **descent loses
by ~190, because `‖c‖` cannot REACH the Gaussian heuristic**, not because it is
pinned to it.
```

**E3 (BLOCKING) — line 138–141, the payoff regime.**
Replace:
```
Not ML-KEM. Ducas–van Woerden put the NTRU fatigue point near `q ≈ n^2.484`;
for `n = 256` that is `≈ 2^19.9`, and ML-KEM's `q = 3329 = 2^11.7` is well
below it. The payoff regime is **large `q/σ`**: BGV/BFV/CKKS at
`n ∈ {2^13 … 2^15}` with `log q ∈ [200, 900]`, where `n^2.484` is `2^32`–`2^37`
```
with:
```
Ducas–van Woerden's CONCRETE fatigue point is `q ≈ 0.004·n^2.484` (their
abstract; stated valid for n > 100), not the bare asymptotic `n^{2.484+o(1)}`.
The constant is `2^-7.966` and it consumes the whole apparent margin: at
`n = 256` the fatigue point is `3838 = 2^11.906` and ML-KEM's
`q = 3329 = 2^11.701` sits **0.205 bits BELOW it**, not 8 bits. Charged against
module dimension `kn` rather than ring degree the margin is +2.69 / +4.14 / +5.17
bits for ML-KEM-512/768/1024. **ML-KEM is therefore NOT demonstrably outside the
regime, and this document makes no claim that it is.** The exponent 2.484 also
holds only for ternary secrets (σ = Θ(1)); `Q*(S)` rises to 2.78 at S = 0.6 and
3.73 at S = 1.0, and the constant 0.004 is calibrated on MATRIX NTRU while this
object is circulant. The payoff regime remains **large `q/σ`**: BGV/BFV/CKKS at
`n ∈ {2^13 … 2^15}` with `log q ∈ [200, 900]`, where the concrete fatigue point
is `2^24.3`–`2^29.3`
```

**E4 (BLOCKING) — line 458–460, M8's closure reason.**
Replace:
```
**It collapses immediately, and the collapse is the finding.** With `m = 1` and
`a` invertible mod `q`, `aR + qR = R`, so the coset is *everything*: every `e` is
realizable with `s = a^{-1}(b − e)`, and there is nothing to search. The method
needs `m ≥ 2`, which lands on a rank-2 module — i.e. M8 *is* M7's setting.
```
```
Record it as closed with that one-line reason rather than leaving it as an
attractive-looking lane for a future batch to rediscover and spend a week on.
```
with:
```
**The stated collapse does not hold.** It is true that with `m = 1` and `a`
invertible mod `q`, `aR + qR = R`, so every `e` is realizable with
`s = a^{-1}(b − e)` — verified 5000/5000. But that drops the shortness
constraint on `s`. R-LWE asks for the pair `(s,e)` with BOTH short, and that
needle is unique: exhaustive search at `n = 8, q = 3329, B = 1` finds exactly
**1** short-short solution among 6561; at ML-KEM scale the space is `2^594` with
expected solution count `2^-1806.6`. `m = 1` R-LWE is the NTRU-shaped
2n-dimensional BDD instance, not a triviality — and the `m = 1` lattice
`{(s,e) ∈ R²}` ALREADY has R-rank 2, so M8 is in M7's setting at `m = 1`.

**M8 is REOPENED as a gated lane, not closed.** The real question — can
log-embedding / ℓ∞ geometry help BDD on the rank-2 R-LWE module? — is open and
is exactly what M7 is gated on.
```
Also update the ranking table, line 86:
`| M8 | ℓ∞ / log-embedding BDD | — | — | — | **collapses into M7** (see below) |`
→ `| M8 | ℓ∞ / log-embedding BDD | unknown | unknown | low | **reopened — prior closure reason was wrong; merge into M7's gate** |`

**E5 (BLOCKING) — line 193–194, the monomial count.**
Replace `` `m = 256·3 = 768` scalar samples against `≈ C(773,5) ≈ 2^44` degree-≤5 monomials. ``
with:
```
`m = 256·3 = 768` sample equations, PLUS 768 more from the secret coordinates
(ML-KEM's secret is CBD-bounded too: `∏_{k=−2}^{2}(s_i − k) = 0`), so **1536**
degree-5 equations against `C(773,5) = 2,270,319,562,049 = 2^41.05` degree-≤5
monomials. (The secret equations are the only source that raised the Macaulay
rank in small-n experiments — n=4, D=6: 134 → 209 of 210 — so they must be
counted, not omitted.)
```

**E6 (BLOCKING) — line 190, the η claim.**
Replace `` ML-KEM's error is *bounded* (CBD `η = 2` ⟹ support `[−2,2]`), so Arora–Ge ``
with:
```
ML-KEM's error is *bounded*, so Arora–Ge applies in principle — but the degree
is parameter-set-dependent. **ML-KEM-768 and -1024: `η₁ = 2` for both `s` and
`e`, support `[−2,2]`, degree 5.** **ML-KEM-512: FIPS 203 uses `η₁ = 3` for
BOTH `s` and `e`, support `[−3,3]`, degree 7, `C(519,7) = 2^50.78` monomials.**
So Arora–Ge
```

**E7 (BLOCKING) — line 205–206, the deficit claim.**
Replace:
```
Predicted: **no** — the Galois conjugates are the rotations already counted, and
the rank deficit is exactly `n` per ring sample, invariantly.
```
with:
```
Predicted, and now measured: **no.** The Galois conjugates ARE the rotations
already counted, and the reason is a theorem rather than a rank tally: for every
`t ∈ (Z/2n)*` the Galois action `σ_t: x ↦ x^t` acts on the affine forms as a
SIGNED PERMUTATION, `P_t · Neg(a) = Neg(σ_t(a)) · P_t`, and since the error
support `[−B,B]` is symmetric, `∏_k(−A−k) = (−1)^{2B+1}∏_k(A−k)`. Galois returns
the same polynomials up to sign. Measured rank increase from Galois conjugates,
rotations, pairwise products, and short-multiplier (`‖c‖₁ = 2`) equations is
**exactly 0** at every `(n,q,B,m,D)` tested; the Galois orbit's redundancy is
`n(n−1)` per ring sample, and the rank deficit versus an unstructured control
with matched equation and variable counts is **0, not n**.
```

**E8 (BLOCKING) — line 170, the charged dimension penalty.**
Replace `` *after* charging the `n` extra dimensions. `` with
`` *after* charging the `n − 1` extra dimensions (`(m+2)n − ((m+1)n+1) = n − 1`). ``
Same fix at line 123–124: `` you pay `n` extra dimensions `` → `` you pay `n − 1` extra dimensions ``.

**E9 (BLOCKING) — line 382, the prime-ideal density.**
Replace `` with `det^{1/n} = 3329^{1/256} ≈ 1.032`, its dual contains `Z^n`, and `e(ω) mod q` ``
with:
```
with `det^{1/n} = (q²)^{1/256} = 3329^{1/128} ≈ 1.0654` — **residue degree 2, so
the norm is `q²`, not `q`** (index verified as `q²` by row reduction, rank 254;
`q^{1/256} = 1.032` is the degree-1 value and contradicts M5's own degree-2 slot
claim). Its dual contains `Z^n`, so `λ₁(L*) = 1` exactly — but that is the
TRIVIAL character for an integer-supported error and must not be fed to a
smoothing bound (it would give `η = 4.90` and falsely predict failure for every
sublattice of `Z^n`). The diagnostic quantity is the shortest NONTRIVIAL
character in `L*/Z^n`, norm **3.0477**, giving `η = 1.61`. And `e(ω) mod q`
```
Then replace `` uniform for any\npractical purpose. **Expect ML-KEM to pass with room.** `` with:
```
uniform, and now measured rather than asserted: max character bias `2^-381.15`,
exact total variation from uniform `2^-378.0`, ~`2^756` samples to distinguish.
**ML-KEM passes with ~373 bits of margin.**
```

**E10** — line 110–112. Replace:
```
So `N` is a rank-1 R-submodule — **Z-rank `n`** — of a lattice of Z-rank
`(m+2)n`, consisting entirely of short vectors.
```
with:
```
So `N` is a rank-1 R-submodule — **Z-rank `n`** — of a lattice of Z-rank
`(m+2)n`, spanned by `n` equally short vectors: `λ₁(N) = … = λ_n(N) =
‖(s,e,1)‖` (multiplication by `x` is a signed permutation, exactly
norm-preserving). *N does not consist entirely of short vectors* — it contains
`r·v` for every `r ∈ R` and `‖r·v‖ ≥ ‖r‖` is unbounded. The DSD-relevant
invariant is the density: `det(N)^{1/n} ≈ ‖(s,e,1)‖ ≪ det(M)^{1/((m+2)n)} =
q^{m/(m+2)}` (measured at n=8,m=2,q=3329: **6.2875 vs 57.6975**).
```
Add after: `` Two facts that strengthen this and were verified: `N` is a PRIMITIVE (saturated) sublattice of `M` (Smith normal form elementary divisors all 1 in M-coordinates), and `N ⊄ qR^{m+2}` in any coordinate block. Those are the two conditions that would have made the dense submodule invisible to BKZ. ``

**E11** — line 120, the trade table row. Replace
`` | normalized covolume | `≈ q^{m/(m+1)}` | `q^{m/(m+2)}` | ``
with `` | normalized covolume | `q^{mn/((m+1)n+1)}` (exact; → `q^{m/(m+1)}` only as n→∞) | `q^{m/(m+2)}` (exact) | ``
Add a footnote: *"At the sweep sizes this document proposes the asymptotic form is 12–21% high: at
n=8, m=1, q=3329 the exact value is 45.45, not 57.70; at m=2, 179.59 not 222.95. Both sides of this
table must be computed to the same standard or the fitted exponent q*(n) is biased."*

**E12** — line 118, dimension row. Add to the table caption or a footnote:
*"Dimension penalty is `n − 1`, not `n`. Moreover the Kannan lattice at τ=1 is literally the section
`M ∩ (R^{m+1} × Z·1)`, of identical determinant `q^{mn}` — so `M` is the Kannan lattice plus `n − 1`
dimensions of UNIT density. That is the airtight form of 'strictly worse for the uSVP event'."*

**E13** — add a new bullet under "Cheapest decisive test" (after line 161):
```
- Compute `vol(N)` per instance as the exact integer `isqrt(det(B_N B_N^T))`
  (always a perfect square; equals `N_{K/Q}(s·conj(s) + Σ e_i·conj(e_i) + 1)`).
  Do NOT use `vol(N)^{1/n} ≈ σ√((m+1)n)` — by AM-GM that is a STRICT
  over-estimate by a factor `1/exp(ψ(m+1)/2)·√(m+1)`, i.e. 1.1447× at m=1 and
  1.0919× at m=2, and the factor does not vanish with n. It biases the detector
  toward the null this mechanism is trying to falsify.
- The rotation basis is NOT near-orthogonal: `δ^{1/n} → exp((ln(m+1)−ψ(m+1))/2)`,
  giving δ = 2.4 at n=8 and 1.3e7 at n=128. Any detector inferring "Z-rank n and
  x-stable" from vector lengths alone is miscalibrated by `1.14^n` at the n=32–64
  end of the sweep.
- Per-instance spread of `vol(N)^{1/n}` at n=8 runs 0.88–1.51× the heuristic, so
  no fatigue point may be read off single instances.
```

**E14** — line 163–166, the control. Replace *"NTRU must show DSD where the literature says it does."*
with:
```
NTRU must show DSD where the CONCRETE literature curve `q* ≈ 0.004·n^2.484` says
it does — NOT where the bare `n^2.484` says it does. At n = 64 those differ by
~250× in q (`2^7.0` vs `2^14.9`); running the control at the naive value would
fire it everywhere and validate a saturated detector. Note further that DvW's
fatigue point is the CROSSOVER at which DSD occurs before SKR, not "the q at
which DSD occurs" — so the detector must measure a crossover against a matched
SKR baseline, which the current test design does not specify.
```

**E15** — line 237–238. Replace `` — **an honest R'-LWE sample in dimension `n/f` with secret `s_0`.** Dimension\nhalves per level. `` with:
```
— an R'-LWE-SHAPED sample in dimension `n/f` with secret `s_0`. The identity is
exact in `R'_q` (verified 144/144, with an `α ∉ R'_q` control failing 100%), but
"honest" does not survive measurement, on two counts:
(i) **α is NOT uniform in `R'_q`.** Against a null matched to the population's
exact `c ↦ x²c` symmetry, specific Fourier modes carry 3.8–6.1× the maximum bias
uniform sampling produces (z = +37 to +66), with 5–100× fewer collisions than
uniform (z = −8 to −11). The deviation STRENGTHENS as `c` gets shorter, and it
is concentrated in exactly the Fourier modes the M5 FFT-over-V step uses.
(ii) **The descended samples are NOT independent.** The noise tuple is the image
of one fixed `mn`-dimensional error vector under a map fixed by the `c_j`
(measured rank 12 = mn − n/2 for N = 10 samples in `Z^40`), so beyond roughly
`N = 2m` samples the instance carries less noise entropy than an honest oracle
would supply. **"Dimension halves per level" is therefore not a valid recursion
as stated** and must be re-costed before any multi-level descent is claimed.
```

**E16** — line 81, ranking table row for M2+M5: change prior-art risk `low (as a *family* statement)`
→ `HIGH — see novelty status; Stange 2019/183 §5 is a direct collision on subring descent, and
Ogilvie 2026/279 may already contain the unified primal+dual ring framework`.

**E17** — line 79, ranking table row for M1: change prior-art risk `med–high` → `MEDIUM, but
UNRESOLVED — Karenin–Kirshanova 2024/844 already coins "Dense Submodule Discovery", the algebraic
Pataki–Tural lemma and the algebraic GSA, at rank 2. Whether their machinery is arbitrary-rank is the
pivot and is unread (full text unreachable).`

**E18** — line 16–25, the provenance block. Replace:
```
  RQ-FHE-001 records that `eprint.iacr.org` is unreachable from this harness
  (proxy CONNECT 403); the same blocker plausibly gates the prior-art step for
  most of this portfolio, and that must be stated in any handoff rather than
  worked around.
```
with:
```
  **That recorded blocker is now partly stale.** `eprint.iacr.org` HTML abstract
  pages and the search endpoint return HTTP 200 via `curl`; only the PDFs return
  403 (Cloudflare interstitial, not a proxy block). Separately, the WebSearch and
  WebFetch TOOLS fail with a model-availability error, which is NOT a network
  block and may have caused earlier "unreachable" verdicts to be misattributed.
  Two of this portfolio's three named prior-art targets are ALREADY ON DISK in
  full text: Ducas–van Woerden (`/Volumes/SSD990/research/classified/other/130900104.txt`,
  KN-LIT-5246) and Felderhoff–Pellet-Mary–Stehlé (`/Volumes/SSD990/research/137910070.pdf`,
  KN-LIT-5365, eprint **2022/1203** — not 2022/1332). The M1 prior-art gate is
  not network-blocked and can be partially cleared today.
```

**E19** — line 31–32. Replace *"**Novelty is unscreened.** Prior-art risk is graded per mechanism, but
no search was performed."* with:
```
**Novelty screening has now been run on three lanes and is INCOMPLETE on all
three.** See `rlwe-pressure-test-report.md` §5. Headline: the DSD concept, name,
algebraic Pataki–Tural lemma and algebraic GSA are already published
(Karenin–Kirshanova, AfricaCrypt 2024, eprint 2024/844) for rank-2 NTRU; the
smoothing generalization M4 proposes is the central contribution of Peikert
2016/351 §3.2.1, which explicitly claims to be "strictly more general" than the
ring-homomorphism framing; and M2's subring descent collides with Stange
2019/183 §5. Prior-art screening remains the first gate on every lane, and no
lane is clean.
```

**E20** — line 487–489, the recommended first batch, item 3. Replace:
```
3. **M1 prior-art gate** — read FPS / Kirchner–Fouque / DvW *before* any code.
   If the network policy blocks eprint, that blocker is the batch's reported
   outcome, not a reason to start experimenting blind.
```
with:
```
3. **M1 prior-art gate** — DvW and FPS are on disk and have now been read in
   full text (see §5 of the pressure-test report): FPS22 is a worst-case
   reduction, strictly rank-2, and EXPLICITLY disclaims the overstretched regime
   ("The regime of the overstretch-NTRU attacks … is also distinct from ours,
   but in the opposite direction"), leaving the regime intersection as an OPEN
   PROBLEM — which supports rather than blocks M1. **The gate now turns on one
   unresolved fact: whether Karenin–Kirshanova (eprint 2024/844) state their
   algebraic Pataki–Tural lemma and DSD prediction for ARBITRARY-rank modules or
   only rank 2.** Their PDF is 403 and closed-access. Resolve via institutional
   Springer access to LNCS 14861 ch. 18, the AfricaCrypt 2024 talk materials, or
   the authors — before a line of code. Also distinguish M1 explicitly from
   Ducas–Loyer 2025/1694 (dense-sublattice no-go, generic lattices) and from
   Ducas–Engelberts–de Perthuis 2025/1904 + de Perthuis–Trenkic 2025/2195
   (module-BKZ and module primal attack for M-LWE, already concrete and
   experimental).
```

### GOAL-RLWE-001.draft.yaml

**E21 (BLOCKING) — lines 40–44, `ceiling_known_in_advance`.** Replace:
```
    Additionally: ML-KEM is almost
    certainly OUT of the payoff regime -- the published NTRU fatigue point near
    q = n^2.484 puts n = 256 at about 2^19.9 while ML-KEM's q = 3329 is 2^11.7 --
    so a null result at ML-KEM parameters is the expected outcome and is not
    evidence about the mechanism.
```
with:
```
    Additionally: the earlier statement that ML-KEM is OUT of the payoff regime
    was WRONG and is retracted. Ducas-van Woerden's CONCRETE fatigue point is
    q ~ 0.004*n^2.484, which at n = 256 is 3838 = 2^11.906; ML-KEM's q = 3329 is
    2^11.701, i.e. 0.205 bits BELOW it (2.69 / 4.14 / 5.17 bits when charged
    against module dimension for 512/768/1024). This goal therefore makes NO
    claim, in either direction, about whether ML-KEM is inside or outside the
    regime, and a reading at ML-KEM parameters is NOT a free null. AGENTS.md
    rule 4 is binding: no result here is a statement about ML-KEM.
```

**E22 (BLOCKING) — lines 15–17, `objective`.** Replace
`The mechanism is that N is\n    provably inside M and consists of short vectors -- the NTRU configuration --`
with
`The mechanism is that N is provably inside M, is PRIMITIVE (saturated) in M and\n    outside qR^(m+2) in every block, and is spanned by n vectors of equal minimal\n    norm ||(s,e,1)|| so that det(N)^(1/n) << det(M)^(1/((m+2)n)) -- the NTRU\n    configuration --`

**E23** — lines 18–19. Replace `lowers\n    normalized covolume from about q^(m/(m+1)) to q^(m/(m+2))` with
`lowers\n    normalized covolume from q^(mn/((m+1)n+1)) to q^(m/(m+2)); the dimension\n    penalty is n-1, not n`. Same correction at line 72
(`with the n extra dimensions charged` → `with the n-1 extra dimensions charged`).

**E24** — lines 54–58, `known_blocker`. Replace the eprint text with the E18 replacement, and add:
`Papers already on disk: DvW (KN-LIT-5246) and FPS22 (KN-LIT-5365, eprint 2022/1203). The live gate is
Karenin-Kirshanova eprint 2024/844 rank-generality, which is unread.`

**E25** — lines 83–86, `first_batch` item 2. Replace the four one-line facts with the five corrected
ones, and add: `covol(M) = q^(mn), dim (m+2)n, and q^(m/(m+2)) have now been verified EXACTLY at five
parameter sets and need not be re-derived; what does need re-deriving is the Kannan side
(q^(mn/((m+1)n+1)), NOT q^(m/(m+1))) and the dimension penalty (n-1, NOT n).`

### GOAL-RLWE-003.draft.yaml

**E26 (BLOCKING) — lines 43–47, `ceiling_known_in_advance`.** Replace:
```
    self-defeating because the noise term L(kappa)*sigma*sqrt(n) grows faster
    than the dimension shrinks -- the envelope in PORTFOLIO.md puts one descent
    level at ML-KEM-like parameters at noise about 670 against q = 3329
    (instance dead) and at FHE-like parameters at block size moving 370 -> 420
    (wrong direction).
```
with:
```
    self-defeating -- but NOT for the reason previously recorded, and the two
    envelope figures previously recorded here (670 vs q = 3329; beta 370 -> 420)
    are BOTH WRONG and are retracted. Corrected: the per-coefficient descended
    noise at ML-KEM-like parameters is 41.6 against q = 3329 (80x headroom, the
    instance is NOT dead; 670 was an L2 norm compared against a scalar modulus),
    and at FHE-like parameters the block size under the Gaussian-heuristic ||c||
    moves 367 -> 201, i.e. descent APPEARS TO WIN. The family closes only when
    the omitted cost axis is restored: ||c|| = delta(beta_c)^(mn)*q^(kappa/(mn)),
    total cost max(beta_c, beta_resid), giving 560 vs 367 at FHE scale and 233
    vs 152 at ML-KEM scale. Descent loses because ||c|| cannot REACH the Gaussian
    heuristic (beta_c = 65539 > d at n = 2^15; 516 > d = 512 at n = 256), not
    because it is pinned to it.
```

**E27 (BLOCKING) — lines 12–13, `objective`.** Replace
`the resulting residual instance of dimension n - kappa with noise about\n    L(kappa)*sigma*sqrt(n)` with
`the resulting residual instance of dimension n - kappa with per-coefficient\n    noise sd L(kappa)*sigma (c_ring = 1, measured exactly; the sqrt(n) belongs to\n    the L2 norm ||E||, not to the per-coefficient sd), and the block size\n    beta_c(kappa) needed to PRODUCE c, which is the axis that decides the family`.
Also lines 16–19: `yields an honest R'-LWE sample` → `yields an R'-LWE-SHAPED sample (the identity is
exact mod q, but alpha is measurably non-uniform in R'_q and the samples are not independent beyond
about 2m)`. Line 22: `predicted deficit exactly n per ring sample` → `predicted rank increase exactly
zero from every ring-derived equation source; the Galois orbit's redundancy is n(n-1) per ring sample
and the deficit versus an unstructured control is 0`.

**E28** — line 70 completion criterion. Add: `The curve is two-dimensional (kappa, beta_c). A
one-parameter minimization over kappa with ||c|| = L(kappa) reports that descent beats the primal
attack at both parameter sets and is a KNOWN ARTIFACT, not a discovery. A batch reporting it as a
finding has not discharged this criterion.`

### GOAL-RLWE-002.draft.yaml

**E29** — lines 38–43. Replace `the prime ideal above q has\n    normalized determinant 3329^(1/256) = 1.032, its dual contains Z^n, and\n    e(omega) mod q is a 256-term modular sum against a 2^11.7 modulus`
with `the prime ideal above q has residue degree 2, index q^2, and normalized\n    determinant 3329^(1/128) = 1.0654 (the previously recorded 1.032 is the\n    degree-1 value and is wrong). Its dual contains Z^n so lambda_1(L*) = 1\n    exactly, but that is the trivial character and must NOT be fed to a smoothing\n    bound; the diagnostic quantity is the shortest nontrivial character in\n    L*/Z^n, norm 3.0477, giving eta = 1.61. The ML-KEM null is now MEASURED\n    rather than argued: max character bias 2^-381.15, exact TV 2^-378.0, ~2^756\n    samples to distinguish`.

**E30** — `instrument_discipline`. Add: `The instrument must NOT use lambda_1(L*) of the full dual as
its smoothing statistic. That equals 1 for EVERY sublattice of Z^n and would flag every
integer-error scheme as failing smoothing -- a test with no discriminating power. Use the shortest
nontrivial character in L*/Z^n.`

### RQ drafts

**E31** — `RQ-RLWE-be8f64.draft.yaml` lines 30–32, 38, 61: apply E23's corrections
(`q^(mn/((m+1)n+1))` not `q^(m/(m+1))`; `n-1` not `n` extra dimensions) in all three places.
Also line 27–29: `consisting of short vectors` → `spanned by n vectors of equal minimal norm`.

**E32 (BLOCKING)** — `RQ-RLWE-912fdb.draft.yaml` lines 58–64: replace the entire third constraint
with E26's corrected text, and change `A batch that reproduces this is succeeding, not failing.` to
`Those figures were wrong and are retracted; a batch that reproduces them has reproduced an error.`
Line 36: `a rank deficit of exactly n per ring sample` → `rank increase exactly zero from every
ring-derived equation source`.

**E33** — `RQ-RLWE-fe4e1f.draft.yaml` lines 50–52: apply E29's correction to the referenced envelope.

### proposals.draft.yaml

**E34** — `IDEA-20260806-d810ed`: line 22–23 `a rank-1 R-submodule of Z-rank n made\n      entirely of short vectors` → `a rank-1 R-submodule of Z-rank n spanned by n vectors of equal
minimal norm, primitive in M and outside qR^(m+2) in every block`. Line 44 `(q^(m/(m+2)) versus
Kannan's q^(m/(m+1)))` → `(q^(m/(m+2)) versus Kannan's exact q^(mn/((m+1)n+1)))`. Line 54
`ML-KEM is out of the payoff regime by roughly 8 bits of q, so a null there says nothing` →
`RETRACTED: on DvW's concrete curve q* ~ 0.004*n^2.484 the margin at n = 256 is 0.205 bits, not 8.
ML-KEM is NOT demonstrably out of the payoff regime and this record makes no claim either way.`

**E35** — `IDEA-20260806-e4c374`: line 66–68 apply E5 and E6 (`1536` equations, `2^41.05`,
ML-KEM-512 η₁=3/degree 7). Line 71–72 apply E7.

**E36** — `IDEA-20260806-35d60b`: line 105–107 apply E15's "R'-LWE-SHAPED" qualification.
Lines 120–125 `predicted_effect`: replace the envelope with E26's corrected figures and mark the
former ones retracted. Line 135 risk (`The ring-multiplication expansion factor in ||E_0|| is assumed
to be ~sqrt(n); measure it.`) → `MEASURED: the ring expansion constant is exactly 1 and the sqrt(n)
belongs to the L2 norm, not the per-coefficient sd. Risk discharged; the surviving error was a units
mismatch, not the constant.` Line 134 risk → `MEASURED AND FALSE: alpha is non-uniform in R'_q by
3.8-6.1x in specific Fourier modes (z = +37 to +66). Additionally the descended samples are not
independent beyond about 2m.`

**E37** — `IDEA-20260806-b37e8e`: line 159 `noise ~ L(kappa)*sigma*sqrt(n)` → `per-coefficient noise
sd L(kappa)*sigma`; add the `beta_c` axis to the `mechanism` field per E1.

**E38 (BLOCKING)** — `IDEA-20260806-0f4843`: change `status: closed` → `status: proposed`,
`class: lane_closure` → `class: mechanism`, and replace the `claim` field's closing argument
(lines 349–353) with E4's replacement text. Add to `risks`: `The previous closure reason was wrong
(it dropped the shortness constraint on s) and would, if believed, imply m=1 R-LWE is trivially
broken.`

### README.md

**E39** — lines 45–48: replace the eprint-blocker paragraph with E18's corrected reachability status,
and note that the live M1 gate is Karenin–Kirshanova rank-generality, not eprint access.

---

## 5. NOVELTY STATUS

> ### ⚠ ALL THREE LANES ARE **INCOMPLETE**. NONE IS CLEAN.
>
> **eprint.iacr.org status (supersedes the recorded "proxy CONNECT 403"):** HTML abstract pages and
> the `/search` endpoint return **HTTP 200** via `curl`. **PDFs return 403** behind a Cloudflare
> interstitial (not attempted — solving the challenge is out of bounds). Separately, the **WebSearch
> and WebFetch tools are hard-broken** in this harness with a model-availability error — which is
> *not* a network block, and which means earlier "unreachable" verdicts in this program may have been
> misattributed tool failures. **Consequence: no free-text web search was available for any lane.**
> Surveys, lecture notes, theses, Google Scholar, and full-text (non-abstract) search were entirely
> unscreened. Semantic Scholar was rate-limited (429) throughout; DuckDuckGo served a CAPTCHA.
>
> **In every lane, the single highest-collision document could not be read past its abstract.**

### Lane 1 — M1: DSD / overstretched regime for the R-LWE/M-LWE module lattice
**Collision risk: MEDIUM. Screening INCOMPLETE.**

- **Karenin & Kirshanova, "Finding Dense Submodules with Algebraic Lattice Reduction", AfricaCrypt
  2024, eprint 2024/844** — **ABSTRACT ONLY** (fetched twice independently, eprint HTML + Springer;
  full text unreachable: PDF 403, OpenAlex `oa_status: closed`, author homepage dead). It already
  coins the **"Dense Submodule Discovery (DSD) event"**, establishes an **algebraic Pataki–Tural
  lemma** over any number field, an **algebraic GSA**, and a module-level algebraic LLL, with
  heuristic prediction and experimental verification — applied to **NTRU as a rank-2 module with a
  rank-1 dense submodule**. **M1 cannot claim to introduce any of these.** *The pivot of the whole
  screen is unresolved: whether their machinery is arbitrary-rank or rank-2 only.* If arbitrary-rank,
  M1 reduces to "apply an existing published tool to a new object" and **collision rises to HIGH.**
  Resolve before any code.
- **Felderhoff–Pellet-Mary–Stehlé, "On Module Unique-SVP and NTRU", eprint 2022/1203** (note: **not**
  2022/1332, which the portfolio's recall would have pointed at) — **FULL TEXT read** from local PDF.
  Worst-case reduction, no experiments, **strictly rank-2**, and it **explicitly disclaims the
  overstretched regime** ("The regime of the overstretch-NTRU attacks … is also distinct from ours,
  but in the opposite direction") and **leaves the regime intersection as an open problem**. This is
  *supporting evidence for M1*, not a collision. The portfolio's graded "most likely collision" was
  wrong.
- **Ducas–van Woerden, eprint 2021/999** — **FULL TEXT read** from local PDF. Uses Ring-LWE as the
  *baseline NTRU departs from* and never analyses it (2 hits for ring-lwe/module in the whole text,
  both framing sentences). Neither establishes nor rules out M1's object.
- **Kirchner–Fouque 2017** — **UNREACHABLE as primary** (no eprint version, Springer paywalled).
  Characterized only at second and third hand. **This program has never read it directly.**
- Closest live competition, **abstracts only**: Ducas–Engelberts–de Perthuis "Predicting Module-Lattice
  Reduction" (2025/1904, first open-source module-BKZ); de Perthuis–Trenkic "Refined Modelling of the
  Primal Attack … Against M-LWE" (2025/2195); **Ducas–Loyer "Lattice Reduction via Dense Sublattices:
  A Cryptanalytic No-Go" (2025/1694)** — a no-go for a *different* object (DSP_k-BKZ on random
  lattices, no planted submodule). M1 must distinguish itself from that paper explicitly or be
  mistaken for something already ruled out.
- Negative evidence: all 14 eprint hits for "overstretched" enumerated — **zero** are R-LWE/M-LWE
  overstretched papers. "dense sublattice" returns exactly 2 (2025/1694 and 2024/844). Suggestive,
  not conclusive (eprint search is strict-AND, title/abstract only).
- **Corpus gap:** grep for "karenin", "dense submodule", "DSD event" across all 7,819 KN-LIT entries
  returns **nothing**. The highest-collision paper is absent from the corpus.

**Position M1 as: extending Karenin–Kirshanova's rank-2 NTRU DSD framework to the rank-(m+2)
R-LWE/M-LWE module — pending resolution of their rank-generality.**

### Lane 2 — M2/M5: subring/subfield descent and codimension-parameterized dual
**Collision risk: HIGH. Screening INCOMPLETE. The portfolio grades this LOW; that grade is wrong.**

- **Stange, "Algebraic aspects of solving Ring-LWE … Blum–Kalai–Wasserman", eprint 2019/183** —
  **FULL TEXT read** (Intro, Props 4.4/4.5, all of §5 incl. Prop 5.1 / Thm 5.2 / Cor 5.3, §7, §8).
  Direct collision territory on subring descent.
- **Ogilvie, "On the Concrete Hardness Gap Between MLWE and LWE", eprint 2026/279** — **ABSTRACT
  ONLY**, full text Cloudflare-blocked with no mirror. Incorporates a ring-symmetry mechanism into
  **"both primal and dual hybrid frameworks"** — the closest published thing to M2+M5's unified
  primal+dual ring-aware framework. **Cannot tell from the abstract whether her parameterization
  subsumes the κ-curve. Highest-value gap in this lane.**
- **Guo–Johansson (Asiacrypt 2021)** and **MATZOV (2022)** — **UNREACHABLE** (not on eprint; Zenodo
  403). Both characterized *only* via Ducas–Pulles §3.3/§3.4. MATZOV in particular has a
  dimension-reduction parameter that may already be the κ-parameterization in other terms.
- **"Espitau et al. on subfield/ring descent" was never pinned down** — the search surfaced only
  Kirchner–Espitau–Fouque 2019/1436 ("Algebraic and Euclidean Lattices: Optimal Lattice Reduction and
  Beyond") and 2017/142, **neither read beyond title**. This named target is **effectively
  UNSCREENED**, and 2019/1436 is a plausible collision.
- Also unread: Karenin et al. 2025/1002 (a general BDD dimension-reduction framework from the
  Ducas/Pulles orbit — could contain the family), Wu–Xu 2022/1661 (self-described "first attempt" at
  a ring-structured dual attack), 2026/688.
- Cheapest next check: **Stange 2019/183's forward citation graph.** An extension of her Theorem 5.2
  to a short-vector regime by anyone else would be the exact collision.

### Lane 3 — M3/M4: weak `a` inside a good ring, and the smoothing generalization
**Collision risk: HIGH. Screening INCOMPLETE. M4's headline generalization is effectively PUBLISHED.**

- **Peikert, "How (Not) to Instantiate Ring-LWE", eprint 2016/351 / SCN 2016** — **FULL TEXT read**
  (§3.2.1, §3.2.2, §5.1, §5.2.1, §5.2.2, §5.3.1). **§3.2.1 does exactly M4's generalization**: it
  re-expresses EHL/ELOS/CLS/CLS via duality/trace pairings, and states verbatim that *"not every tuple
  of dual elements … corresponds to such a ring homomorphism, so the present framework is strictly
  more general."* **Lemma 3.1 is the smoothing-failure criterion for an ARBITRARY lattice L.**
  Theorem 5.2 proves immunity via the smoothing parameter by name. **M4 cannot claim the
  "ring-hom → smoothing of a sublattice" move.**
  **Residual novelty that DOES survive, for a good technical reason:** Peikert's positive (immunity)
  result quantifies over **ideals only**, and its proof uses `λ₁(𝔮^{-1}) ≥ √n·N(𝔮^{-1})^{1/n}`, an
  algebraic-norm bound valid for ideal lattices. For a **non-ideal** sublattice of large index that
  bound fails. **So "L ranging over kernels of R_q-module maps including non-ideal R'-submodules" is
  a real gap in the published positive result — and that, narrowly, is M4's contribution.**
- **Ikematsu–Nakamura–Yasuda, "A Trace Map Attack Against Special Ring-LWE Samples", IWSEC 2021** —
  **ABSTRACT ONLY** (Springer). This is the **direct threat to M3's novelty axis**: it gives a
  **necessary and sufficient condition on a PAIR OF SAMPLES** (hence `a`-dependent) inside a fixed
  **good cyclotomic ring**, compares BKZ block sizes, and *"discuss[es] the (in)feasibility of the
  trace map attack for RANDOM ring-LWE samples."* It also partially occupies M4's non-ideal territory
  (the trace map onto a subring is an R'-module map that is not an ideal quotient).
  **UNRESOLVED AND CRITICAL: whether they QUANTIFIED the density of "special" samples or only argued
  infeasibility qualitatively. If quantified, M3's "measured weak-`a` tail" is dead as stated.**
- Verified structural point *supporting* partial novelty: the mainline weak-instance literature is
  **`a`-independent** — Peikert's attack condition depends only on the error distribution and the
  chosen Z-basis, and works for *every* `a`. EHL/ELOS/CLS/CIV/Peikert all define weak instances as
  properties of `(R, q, error)`, never of `a`. The Ikematsu trace-map line is the exception, and it
  is where essentially all of M3's collision risk is concentrated.
- **M3's "no random self-reduction over `a`": no published statement found, but this is a
  LOW-CONFIDENCE negative.** Evidence is string-absence in three PDFs (Peikert 2016, Peikert–Pepin,
  LPR Toolkit — all zero hits for "self-reduc"/"rerandomiz") plus a corpus grep. **With no free-text
  web search available, folklore stated in other words would not have been caught.** Framing caveat
  M3 must address: LPR's worst-case theorem *produces* random `a`, so no RSR over `a` is needed for
  the standard hardness argument — plausibly why nobody states its absence as a limitation. Corollary:
  under ideal-SVP hardness the weak-`a` set is already forced to be asymptotically negligible, so any
  measured tail is a **concrete-parameter** phenomenon and must not be claimed as asymptotic.
- Named target **not adequately screened**: LPR 2012/230 and the LPR Toolkit's rationale for the
  error distribution (title/grep only), and **Castryck–Iliashenko–Vercauteren, "On error distributions
  in ring-based LWE" (ANTS 2016) — not read at all**, though directly on-topic.

---

## 6. GO / NO-GO

| mechanism | verdict | one-line reason |
|---|---|---|
| **M1** — DSD transfer | **GO, after two blocking fixes** | The algebra is exact and *stronger* than claimed (N is primitive in M, outside `qR^{m+2}`, and BKZ-20 recovers it at n=8 while matched Kannan gives rank 1) — but the payoff-regime scoping is wrong by 8 bits (E3) and the NTRU control would run at ~250× the right modulus (E14); fix both, then resolve Karenin–Kirshanova's rank-generality before any code. |
| **M2+M5** — the κ-curve | **NO-GO as specified; GO once the exchange law is two-dimensional** | As written it omits `β_c(κ)` and will report that descent BEATS the primal attack (367→201 at FHE, dead-even at ML-KEM) — a false-positive generator pointed at deployed parameter sets; both recorded envelope numbers are wrong, and the prior-art grade must go LOW→HIGH. |
| **M3** — weak-`a` tail | **CONDITIONAL GO, build second** | The "no self-reduction over `a`" observation is probably unstated but rests on a low-confidence negative with no web search available; the measurement axis may already be occupied by Ikematsu et al. 2021, whose full text must be read first. |
| **M4** — smoothing instrument | **GO as an instrument, with novelty re-scoped to the non-ideal case** | The ML-KEM null is now *measured* (TV `2^-378`, 373 bits of margin) rather than argued, so the null control is already discharged — but the headline generalization is Peikert 2016 §3.2.1, the ideal density is wrong by a factor of 2 in the exponent (E9), and the stated dual diagnostic fires on every sublattice of `Z^n`. |
| **M6** — profile shape | **HOLD, gate unchanged** | Still gated on M1, and prior-art risk went up: Ducas–Engelberts–de Perthuis 2025/1904 already delivers concrete module-BKZ prediction with the first open-source implementation, and its full text is unread. |
| **M7** — rank-2 S-unit | **HOLD as gated moonshot** | Unchanged by this pressure test — except that M8's collapse being false means M7's rank-2 setting is reachable at `m = 1`, so the gate should absorb M8 rather than sit downstream of a lane that was closed for a wrong reason. |
| **M9** — Arora–Ge starvation | **GO, run first, after three number fixes** | The prediction is confirmed and upgraded to a proof (Galois acts as a signed permutation; symmetric support kills the sign; rank increase exactly 0 from four independent sources) — but `2^44`→`2^41.05`, ML-KEM-512 is η₁=3/degree 7, the equation count is 1536 not 768, and "deficit exactly n" must be deleted before a referee sees it. |
| **M8** — ℓ∞ / log-embedding | **REOPEN (was "closed on arrival")** | The closure reason drops the shortness constraint on `s` and would, if true, imply `m=1` R-LWE is trivially broken; the real search space is `2^594` with a unique short-short solution, verified exhaustively at n=8. |

---

*Report generated from 7 independent claim verifications (all exact arithmetic, adversarially
re-checked) and 3 prior-art screening lanes. Scratchpad artifacts:
`/private/tmp/claude-501/-Volumes-SSD990-research/eafcc47d-b0be-4a13-95fd-58d699c93491/scratchpad/`.
Nothing in this report is a ledger record.*
