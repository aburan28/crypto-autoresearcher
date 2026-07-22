# Finding v2 (HARDENED) — boolean Semaev t=3/t=7 Weil-descent degree of regularity is **linear**, with an exact analytic density c\*, and the Gröbner/Macaulay route is super-exponentially worse than rho at every tested scale

Thread: SIG asymptotics + DREG audit. Feeds **H-DREG-001** (degree axis) and
**H-SIG-001**. Supersedes `FINDING.md` (v1); v1 is not overwritten. Hardened by four
verified extensions plus the incorporation of the independent RED-TEAM.md challenge.

Author: independent Claude session (2026-07-20), worked in isolation. No ledger
commit is made by this session; a live co-driver owns ledger archival. This document
is a research artifact, not an official ledger record.

> **Status of the v1 → v2 change in one line.** v1's Claims 1–4 (family, series,
> linear semi-regular d_reg, and the n=9/D6 "null break" = d_reg degeneracy)
> **survive** independent validation and adversarial re-derivation. v1's Claim 5
> **as originally evidenced is retracted** — the RED-TEAM was correct that a raw
> subset-column corank at a single degree cannot decide d_reg(sem) vs d_reg(null).
> The conclusion d_reg(sem) > d_reg(null) is **re-established at toy scale by a
> corrected, order-independent instrument** (graded pivot-degree Hilbert function),
> which independently reproduces the red-team's own warning that the naive measure
> inverts. v1's Claim 6 (cost verdict) is **re-supported** — but now via a direct
> first-fall completeness census, not by asserting "sem ≥ semi-regular."

---

## TL;DR (hardened)

1. **Linear d_reg, closed form (SURVIVES).** For the t=3 family (nb = 2n boolean
   vars, n quadratics + n cubics) the semi-regular degree of regularity is the first
   non-positive coefficient of `B(z)^n`, `B(z) = (1+z)^2 / [(1+z^2)(1+z^3)]`, and
   grows **Θ(n)** with density → **c\* ≈ 0.2375**.

2. **Analytic linearity, theorem-grade for the semi-regular model (NEW).** The density
   is the algebraic constant **c\* = 0.2374790709146819**, the interior maximum on
   (0,1) of the rational logarithmic-derivative ψ(z)=zB′/B. It is a coalescing-saddle
   (Airy) transition of the generating function B(z)^n; c\* is the unique root in (0,1)
   of an explicit self-reciprocal octic. d_reg(n) = c\*·n + Θ(n^{1/3}). This is a
   *rigorous statement about the semi-regular model*, not an extrapolation.

3. **Crypto-scale target t=7, n=161 (NEW).** At the real config (nb=966,
   161 deg-2 + 805 deg-3) the semi-regular d_reg = **150**, giving Gröbner cost
   **2^1194 (ω=2)** to **2^1415 (ω=2.37)**, versus rho **2^80.5** on E(GF(2^161)) —
   the Gröbner route loses by **>1100 bits**, and the gap **grows** monotonically
   with t. The binary Weil-descent Semaev route is not a threat at these parameters.

4. **n=9/D6 "null break" = d_reg degeneracy, not a bug (SURVIVES).** The null fails
   its C5 control at n=9/D6 for the *mathematical* reason d_reg(9)=6: at D=d_reg the
   random null reaches full rank and the pre-collapse `sr_pred` necessarily
   under-shoots. The instrument is sound. **Valid measurement rule: the semi-regular
   baseline is well-defined at probe degree D iff D < d_reg(n).** Since d_reg(12)=7,
   the coordinator's target D6-at-n=12 is a clean sub-d_reg point (predicted to pass
   C5). n=9 (d_reg=6) was the one degenerate size.

5. **d_reg(sem) > d_reg(null) — retracted method, re-established by a corrected
   instrument (CHANGED).** The RED-TEAM refuted the v1 evidence (raw q_sem vs q_null
   across different column supports at a single degree). Replacing it with the
   **graded pivot-degree Hilbert function** read from a single Macaulay matrix, the
   separation holds at both n=6 and n=9: at d=d_reg(null) the null's genuine graded
   piece vanishes while the sem's is 32 (n=6) / 2034 (n=9). This is a Macaulay-max-
   degree statement (the structured system's Gröbner computation runs to *higher*
   degree — the wrong direction for an attacker), distinct from the first-fall
   question handled in item 6.

6. **First-fall completeness — no sub-d_reg opening (NEW; addresses the red-team's
   sharpest objection).** The attack-relevant quantity is the *first-fall* degree, not
   the semi-regular d_reg. First-fall IS low (D4 at n=6, D3 at n=9; linear ideal
   elements even earlier) — exactly the red-team / Petit–Quisquater signature. But the
   **relation supply there is only O(1)–O(n)** (far fewer than nb variables), the
   quotient stays exponentially large until ~d_reg, and a usable count of linear
   relations only materializes at Macaulay degree ≈ d_reg. A hybrid/last-fall solver
   still pays ≈ d_reg → Gröbner 2^{Θ(n)} ≫ rho 2^{n/2}. Verified at n=6, 9.

**Net:** on the degree axis, the t=3/t=7 binary Weil-descent Semaev route is a clean
negative control — no sub-rho signal at any tested scale — and this now rests on a
validated model, an analytic density, a corrected per-degree instrument, and a direct
first-fall census, rather than on the one inference the red-team overturned.

7. **Independent q→s adjudication of item 5 (NEW; `ADJUDICATION_solcount.txt`).** The
   F₂ solution count was pinned by direct enumeration: **s = 1** for the sem AND the
   null at both n=6 and n=9. So each arm's quotient q = ncols−rank collapses to 1
   exactly at its own solving degree. The null reaches q=1 at D=d_reg(null) (n=6 D5,
   n=9 D6); the sem quotient there is **95 (n=6) / 2040 (n=9) ≫ 1** and still
   descending (n=6: 95,51,24,9 at D5..D8). This is the *legitimate* d_reg(sem)
   observable the red-team asked for (q→s with s known), independent of the graded-HF
   route, and it confirms **d_reg(sem) > d_reg(null)** — the sem has not solved where
   the null has. The red-team's objection to the v1 subset-corank method is upheld;
   its tentative opposite reading (from the confounded stacked deficit) is resolved.

---

## Part A — v1 core (retained; two doc nits fixed)

**Family (verified from run receipts n=9..24).** nb = 2n boolean variables; n degree-2
equations + n degree-3 equations. eq_hist {2:n, 3:n}. Reproduced at n=6 live
(nb=12, {2:6,3:6}).

**Semi-regular series / d_reg law.** A(z) = (1+z)^{2n}/[(1+z^2)^n(1+z^3)^n] = B(z)^n.
The instrument's ascending in-place recurrence `a[j] -= a[j-d]` is exactly division by
(1+z^d); d_reg(n) = first D with [A]_D ≤ 0.

| n | 6 | 9 | 12 | 15 | 18 | 24 | 48 | 96 | 161 | 1000 | 8000 |
|---|---|---|----|----|----|----|----|----|-----|------|------|
| d_reg | 5 | 6 | 7 | 8 | 9 | 10 | 17 | 30 | 46 | 252 | 1929 |

d_reg/n → c\* ≈ 0.238 (marginal slope over [4000,8000] = 0.239).

> **DOC FIX 1 (validator nit).** The growth is Θ(n), not O(√n): **d_reg/√n grows
> without bound** — 3.6 at n=161, 8.0 at n=1000, 21.6 at n=8000. (v1 wrote "d_reg/√n
> strictly increasing 2.0 → 4.4"; the "4.4" endpoint is not reproducible from the
> table and is replaced by these exact values.)

**n=9/D6 mechanism.** At D=d_reg the null reaches full rank; `sr_pred` (pre-collapse
formula) under-shoots there by construction. The robust invariant, at two independent
sizes: the null's collapse degree (quotient ncols−rank → 1) equals the predicted d_reg
exactly — n=6 collapses at D5, n=9 at D6. Below d_reg the null's rank tracks `sr_pred`
(exactly at n=9 D2..D5 incl. 9504; within a 4-dim finite-size wobble at n=6/D4). The
"convolution-direction bug" hypothesis was falsified empirically. **No D6-null repair
is required to unblock the degree axis;** the fix is D < d_reg(n) (n≥12 for D6).

Receipts reproduced bit-for-bit: n=9 sem D6 (ncols 29332, rank 27292, sr_pred 28068);
null D6 (ncols 31180, rank 31179, sr_pred 28068) — from `RUN-EXP-SIG-005-h/-k`.

---

## Part B — Analytic proof of linearity (NEW; theorem-grade for the semi-regular model)

**Mechanism.** d_reg(n) is the first sign change of [z^{cn}]B^n. By Cauchy,
[z^{cn}]B^n = (1/2πi)∮ exp(n·g(z)) dz/z with g = log B − c log z. Saddles solve g′=0 ⇔
ψ(z):=zB′/B = c. ψ is **rational**:

    ψ(z) = z(2 − 4z + z² − 2z³ − 3z⁴) / [(1+z²)(1+z³)].

On (0,1) ψ rises from 0 to a strict interior maximum, then falls to ψ(1) = −3/2. Below
the max there are two positive real saddles (coefficient positive); they **coalesce**
at c=c\* (double saddle g′=g″=0 ⇔ ψ′(z\*)=0) and split into a complex-conjugate pair
above it (coefficient oscillates → sign changes). Hence the sign-change density equals
**c\* = max_{(0,1)} ψ**, an Airy-type coalescing-saddle transition (standard
Bardet–Faugère–Salvy analysis).

**Transcendental equation.** ψ′=0 reduces to the self-reciprocal octic

    2z⁸ − 8z⁷ + z⁶ − 12z⁵ − 10z⁴ − 12z³ + z² − 8z + 2 = 0,

equivalently the quartic 2w⁴ − 8w³ − 7w² + 12w − 8 = 0 in w = z+1/z. Its unique root in
(0,1) is **z\* = 0.2330651016198973**, and

    c\* = ψ(z\*) = 0.2374790709146819    (verified to 25 digits; g″(z\*)=0 confirmed).

**Why Θ(n), not O(√n).** c\* is a strictly positive interior maximum bounded away from
0, depending only on the n-independent B (i.e. on the degree pattern {2,3} and the
boolean ambient), so d_reg = c\*·n + Θ(n^{1/3}). Sub-linear growth requires the
transition density to vanish (c\*=0), which happens only in degenerate regimes (ψ≤0 on
(0,1), or super-linear equation excess). Our system is critically determined (m=nb=2n),
the maximal-density regime; a genuinely under-determined system is positive-dimensional
with even larger d_reg. Either way O(√n) is excluded.

**Empirical cross-check (exact integer d_reg to n=20000).** d_reg = c\*·n + a·n^{1/3} +
O(1), a≈1.45; the ratio (d_reg − c\*n)/n^{1/3} is essentially constant (1.43–1.46). A
3-parameter fit recovers slope 0.237463 vs analytic 0.237479 (diff −1.6e-5), max
residual 0.58 (< 1, integer-quantized). This resolves the apparent slow drift of
d_reg/n (0.286 at n=161 → 0.239 at n=20000) as the n^{1/3} finite-size term, not a
moving limit.

**Scope of "theorem-grade."** Given semi-regularity (Hilbert series = truncated B(z)^n),
linearity and the exact c\* follow from rigorous analytic combinatorics (Flajolet–
Sedgewick VIII, large-powers + Airy coalescing saddle). One step (global dominance of
the coalescing real saddle over the boundary poles on |z|=z\*) is verified numerically,
not by a written lemma; it is standard and the numerics are decisive. Semi-regularity of
the *actual* Semaev system is not proven here — it is validated by the instrument (null
matches sr_pred exactly for D<d_reg) and the true sem d_reg is ≥ this, so **c\* is a
rigorous lower density** for the real system.

---

## Part C — Crypto-scale target t=7, n=161 (NEW)

**t-family construction, verified from `experiments/EXP-SIG-005/src/semaev_tree.py`.**
Of the (t−1) chained S₃ equations, the last carries the constant R_X (degree 2) and the
other (t−2) are genuine 3-variable (degree 3); each Weil-descends to n boolean eqs,
giving **n deg-2 + n(t−2) deg-3**, with nb = n(t−2) + t·⌈n/t⌉. This reproduces both
anchors exactly (t=3: nb=2n, n+n; t=7 n=161: nb=966 = 161·5 + 7·23, 161+805).

**Result at t=7, n=161** (from the validated (1+z^d)-division recurrence on
A(z)=(1+z)^966/[(1+z²)^161 (1+z³)^805]):

- d_reg = **150** (clean sign flip: a[149]>0, a[150]<0 — no off-by-one).
- log2(#monomials of degree ≤150 in 966 boolean vars) = 597.19.
- Gröbner LA cost (#mon≤d_reg)^ω: **2^1194.4 (ω=2)**, **2^1415.3 (ω=2.37)**.
- rho = 2^(161/2) = **2^80.5**. Bit loss: **1113.9 (ω=2)**, **1334.8 (ω=2.37)**.

**Robustness across t at common n=161** (degree distribution read from `semaev_tree.py`,
not a fitted t-law):

| t | nb | #deg2 | #deg3 | d_reg | log2#mon | G(ω=2) | G(ω=2.37) | gap-vs-rho(ω=2) |
|---|-----|-------|-------|-------|----------|--------|-----------|-----------------|
| 3 | 323 | 161 | 161 | 47 | 189.6 | 2^379 | 2^449 | +299 |
| 4 | 486 | 161 | 322 | 73 | 292.6 | 2^585 | 2^693 | +505 |
| 5 | 648 | 161 | 483 | 99 | 395.4 | 2^791 | 2^937 | +710 |
| 6 | 806 | 161 | 644 | 125 | 497.3 | 2^995 | 2^1179 | +914 |
| 7 | 966 | 161 | 805 | 150 | 597.2 | 2^1194 | 2^1415 | +1114 |

Density d_reg/nb is flat and slightly worse for the attacker at larger t: 46/322=0.143
(t=3) vs 150/966=0.155 (t=7). Larger t buys the attacker nothing.

**Anchor validation (all exact):** t=3 d_reg = 5,6,7,8,9,10 @ n=6,9,12,15,18,24;
46 @ n=161; 252 @ n=1000; 1929 @ n=8000; t=7 n=161 = 150. Verified independently in
exact big-integer arithmetic (~30 quantities, zero discrepancies).

**Operative caveat (see also Parts D/E).** This is the **semi-regular** cost. It assumes
no exploitable first-fall collapse below d_reg — the same scoping assumption as the whole
finding. It is not an empirical semi-regularity check at n=161 (computationally
infeasible); it is validated only at toy scale (n≈9..24) and extrapolated under the
analytic density of Part B. ω=2 is reported as the attacker-favorable (block-Wiedemann /
sparse) bound; even there it is 2^1194.

---

## Part D — d_reg(sem) vs d_reg(null): red-team correction + corrected per-degree instrument (CHANGED)

### D.1 What the RED-TEAM overturned (accepted)

v1 Claim 5 argued d_reg(sem) > d_reg(null) from "at D=d_reg(null) the null quotient is 1
while the sem quotient is still 95 (n=6) / 2040 (n=9)." The RED-TEAM refuted this on four
grounds, **all of which are accepted here**:

1. q_sem and q_null are taken across **different column supports** (n=9 D6: sem ncols
   29332 < null 31180) — a subset-column-rank comparison H-DREG-001 pre-labels an
   artifact, "never evidence."
2. The Coordinator's Validator (DEC-20260720-002 check 4) already ruled this **one-arm-
   collapsed configuration non-evaluable**: at n=9/D6 the null has collapsed but the sem
   has not, and reaching d_reg on one arm says nothing about the other's collapse degree.
3. **sr_pred is degenerate at D=d_reg for BOTH arms** — by v1's own Claim-4 argument — so
   the sem deficit cited at that single cell is in the degenerate regime.
4. The sem quotient is **descending monotonically** (n=6: q_sem = 171→95→51→24→9 at
   D=4..8), heading toward the sem system's own solution count s (it is a *solving*
   instance with a decomposable target R). "Still 95" is a point on a descent, not a
   higher collapse degree. Moreover the sem **deficit is +76 at D4** — a rank deficit
   *below* d_reg=5, the extra-syzygy/degree-fall signature that trends the *opposite* way.

**Conclusion: v1's raw-corank evidence for Claim 5 does not survive and is retracted.**

### D.2 The corrected, order-independent instrument (per-degree Hilbert function)

The valid per-degree measure is the **graded Hilbert function** read from pivot-column
(leading-term) degrees in a single Macaulay echelon:

    HF_graded(d) = (# degree-d monomials appearing) − (# pivots whose leading monomial has degree d).

This is a genuine non-negative graded-piece dimension under the instrument's degree-
refining column order, and its cumulative sum equals the **order-independent** stacked
quotient q(D) = ncols − rank. Read from the single matrix M_D at D = d_reg.

**Secondary finding, in agreement with the red-team.** The literally-prescribed
stacked-rank-*difference* measure (HF = appear(d) − [rank(D=d) − rank(D=d−1)]) is
**confounded by affine degree-falls and INVERTS the claim**: at n=6 it goes negative for
sem first (sem d=4 = −16 while null d=4 = +32). The structured sem has a **low first-fall
degree**, so its stacked rank overshoots earlier; the stacked difference conflates
first-fall degree with solving degree. This is exactly the red-team's D4-deficit signal,
reproduced — and it is precisely why that measure must not be used.

### D.3 Result with the corrected instrument (n=6 and n=9)

At D = d_reg(null), the **null's genuine graded pieces vanish** while the **sem's are
large**:

    === n=6 (d_reg(null)=5), single matrix M_5 ===
      HF_null:  d=0..5 = 0 0 0 0 0 1   (single affine residual at top deg; genuine degrees all 0)
      HF_sem :  d=0..5 = 1 4 1 0 57 32  ->  HF_sem(d_reg=5) = 32  (not collapsed; stacked q=95)

    === n=9 (d_reg(null)=6), single matrix M_6 ===
      HF_null:  d=0..6 = 1 0 0 0 0 0 0   ->  HF_null(d_reg=6) = 0 EXACTLY (stacked q=1)
      HF_sem :  d=0..6 = 1 4 1 0 0 0 2034 -> HF_sem(d_reg=6) = 2034 >> 0 (stacked q=2040)

Money row (HF at d = d_reg(null)): n=6 → null 1 (residual), sem 32; n=9 → null 0, sem
2034. Cross-validated bit-for-bit against the receipts (n=9 M_6: sem 29332/27292/q2040,
null 31180/31179/q1) and reproduced by a distinct linear-algebra engine (Sage m4ri) at
n=6 and n=9/D5, so the separation is not a hand-rolled-echelon or pivot-order artifact.

**Interpretation and honest scope.** In the **Macaulay-max-degree / semi-regular sense**,
d_reg(sem) > d_reg(null): the structured system's Gröbner computation still has a large
graded piece where the null has fully collapsed — the extra cascade syzygies **raise** the
solving degree, the wrong direction for an attacker. This is consistent with the parent
finding. It is established per-degree at both toy sizes. It does **not**, by itself,
answer the attack-relevant *first-fall* question (the red-team's Claim-6 objection); that
is Part E. The n=6 "residual 1" vs n=9 "0" is a benign affine off-by-one (inhomogeneous
instrument vs homogeneous model), not a failure of the inequality.

---

## Part E — First-fall completeness check (NEW; answers the red-team's cost objection)

The RED-TEAM's strongest point (its "Claim 6 unsound as applied") is that Gröbner index
calculus on Semaev/Weil-descent systems is premised on the structured system solving **far
below** the semi-regular degree (first-fall; Petit–Quisquater, Faugère–Gaudry–Huot–
Renault). Using semi-regular d_reg as the true solving degree begs that question. We
therefore measured first-fall directly (n=6, 9).

**First-fall is low (concern confirmed, not assumed away):**

| n | nb | d_reg | d_ff (extra>0) | gap | d_ff (first linear ideal elt) | gap |
|---|----|-------|----------------|-----|-------------------------------|-----|
| 6 | 12 | 5 | D4 | 1 | D3 | 2 |
| 9 | 18 | 6 | D3 | 3 | D2 | 4 |

**But the relation supply at first-fall is far too small to solve:**

- Non-model syzygies (`extra`): n=6 = 0,0,76,597 (D2..5); n=9 = 0,1,41,910,8897 (D2..6).
- Directly-usable linear ideal elements (`le1`): n=6 = 0,6,6,8 (D2..5); n=9 = 1,1,6,6,14
  (D2..6). **le1_max = 8 (n=6) and 14 (n=9), both < nb = 12/18** — the linear part alone
  never determines the system.
- Quotient q_sem = ncols−rank stays exponentially large below d_reg: n=6 = 77,171,95
  (D3,4,5); n=9 = 365,1423,2437,2040 (D3..6). To collapse a quotient of this size you need
  ~2^{Θ(n)} independent new relations; only O(n) degree-fall relations appear at the low
  first-fall degrees, and they only shift degree d→d−1, not down to a solving set.
- **Variable-elimination escape fails:** a usable count of linear relations only appears at
  Macaulay degree ≈ d_reg (n=9 le1 jumps 6→14 only at D=6; n=6 reaches 8 only at D=5), so
  extracting them already costs the full d_reg linear algebra. Below d_reg you can eliminate
  at most ~6 of 12/18 variables, leaving a Θ(n)-variable residual whose d_reg is still
  Θ(n). Elimination shaves a constant factor off density, not the exponential rate.

**Verdict (no opening):** a hybrid/last-fall solver still pays ≈ d_reg, keeping Gröbner
2^{Θ(n)} ≫ rho 2^{n/2}. The first-fall axis leaves nothing the d_reg cost model misses at
these sizes.

**Honest scope of this check.** Two sizes only (n=6, 9). The "relation supply stays O(n)
while the quotient stays exponential" separation is anchored on these two points plus the
validated closed-form d_reg law; the two-size trend (extra-gap 1→3, le1_max 8→14 growing
~linearly, q growing exponentially) supports it but is **not an asymptotic proof**, and it
is **not a constructive impossibility proof** — no sub-d_reg solve was run to termination.
This is a relation-counting completeness census, the right scope for ruling out an obvious
opening, and it converts DEC-20260720-002's "true degree axis unmeasured past D=5" into
"first-fall measured at n=6,9; no exploitable sub-d_reg route found at toy scale." The
crypto-scale (Part C) inherits the same assumption: no first-fall collapse is *proven* at
n=161.

---

## Part F — Scope / honesty (AGENTS rules 4–7)

- **Toy scale.** All direct measurements are n∈{6,9} (per-degree HF, first-fall) or
  n≤24..20000 (integer d_reg law). n=161/1000/8000 and t=7 are recurrence/analytic
  extrapolations under the validated semi-regular model, not empirical solves.
- **Negative control.** t=3 and t=7 boolean Weil-descent over a binary field is a known
  **negative control** for the generic **prime-field** ECDLP target. **No prime-field
  claim, no crypto-scale positive claim, and no ECDLP break** is made or implied.
- **Semi-regular proxy.** d_reg is the semi-regular prediction, validated to match the
  random support-matched null exactly for D < d_reg (n=6,9) and by the exact closed form.
  The true sem solving degree is ≥ this (extra syzygies), so the negative (no-sub-rho)
  conclusion is robust in the safe direction. The load-bearing unproven step remains
  semi-regularity of the true Semaev system at scale.
- **Coordinator boundary.** This finding does not change any hypothesis status and does
  not discharge the DEC-20260720-002 prerequisite — those are Coordinator-only actions. It
  supplies a validated model, an analytic density, a corrected per-degree instrument, and a
  first-fall census that together convert "inconclusive/unmeasured" into "predicted
  no-signal with a concrete confirmable test (D6-at-n=12)."

---

## Part G — Reproduce

- **Pure-Python d_reg law + asymptotics:** `dreg_growth_law.py` (no Sage).
- **Sage validation** (null matches sr_pred for D<d_reg; collapse at D=d_reg; per-degree
  graded HF): `validate_dreg.sage` (runs n=6 and n=9) against the SIG-005 instrument
  `experiments/EXP-SIG-005/src/h013_f5_signatures.sage`. *(DOC FIX 2: v1 cited a
  non-existent `validate_fast.sage`; the present, equivalent script is
  `validate_dreg.sage`.)*
- **Analytic c\*** (octic, double-saddle check) and **exact-integer d_reg ladder to
  n=20000**: scratchpad scripts `saddle.py`, `empirical.py`.
- **Crypto-scale cost model** (t-family construction from `semaev_tree.py`, t=3..7 table):
  scratchpad `dreg_crypto_cost_model.py`.
- **Per-degree graded HF** (single-matrix, n=6 and n=9): scratchpad `hf_single.sage`,
  `hf_n9.sage`; confounded stacked-difference reference `hf_perdeg.sage`.
- **First-fall census** (extra/le1/q at each D, n=6 and n=9): scratchpad
  `firstfall_combined.sage`.
- **Receipts cross-check:** n=9 sem D6 (29332/27292/28068) and null D6 (31180/31179/28068)
  reproduced bit-for-bit from `RUN-EXP-SIG-005-h`, `-k`.

Run Sage with the mandatory scratch redirect (root disk is ~full):
`TMPDIR=/Volumes/Volume/sage-scratch-diag SAGE_TMP=/Volumes/Volume/sage-scratch-diag sage <script>`.

---

## Part H — What changed from v1 (and the red-team incorporation)

| Item | v1 | v2 (hardened) |
|------|----|----|
| Linear d_reg law, family, series | Claimed, empirical | **Survives** + exact analytic density c\*=0.2374790709 (Part B) |
| n=9/D6 "null break" | d_reg degeneracy | **Survives** unchanged |
| Baseline validity rule | D<d_reg(n); D6-at-n=12 clean | **Survives** unchanged |
| Crypto scale | not present | **Added**: t=7 n=161 d_reg=150, 2^1194 vs 2^80.5 (Part C) |
| d_reg(sem)>d_reg(null) | raw q_sem vs q_null at one degree | **Method retracted** (red-team); **re-established** via graded pivot-degree HF (Part D) |
| Cost verdict (Claim 6) | asserted sem ≥ semi-regular | **Re-supported** via direct first-fall census (Part E), not by assertion |
| d_reg/√n phrasing | "2.0 → 4.4" (unreproducible) | **Fixed**: grows without bound, 3.6/8.0/21.6 @ n=161/1000/8000 |
| Reproduce script name | `validate_fast.sage` (missing) | **Fixed**: `validate_dreg.sage` |

**Claim that did NOT survive verification:** v1 Claim 5's *evidentiary method* — deciding
d_reg(sem) > d_reg(null) from a raw subset-column corank (q_sem vs q_null) at the single
degree D=d_reg(null). The RED-TEAM was correct on all four grounds; that measurement is
retracted. The *conclusion* is re-established at toy scale by the order-independent graded
Hilbert function, with the attack-relevant first-fall question routed to a dedicated census
rather than assumed. Everything else in v1 survives independent validation and adversarial
re-derivation.
