# Round 018 Results — T4 backdoor-density bound (PO-011) + E-CG class-group probe

Date: 2026-06-01. Track ISO. Reproduction: `round018_backdoor_density.gp` (+ `.log`),
`round018_classgroup_genus.gp` (+ `.log`). Builds on NR-033 and `p256_trapdoor_theory_map.md`.

## T4 / PO-011 — density of "backdoor-eligible" curves (the chosen-seed bound)

**Claim (PO-011).** **RESTRICTED THEOREM / HEURISTIC.** For every *named* ECDLP weakness, the fraction
δ of order-n prime-field curves carrying it satisfies δ ≪ 2^{−80}, so planting it by seed search
(BADA55 model, budget 2^B, B≈32–80) is infeasible — independently of P-256 verifiably not having it.

**Mechanism / derivation.** #curves over F_p with trace t = H(4p−t²) (Hurwitz class number; Deuring).
Curves with small CM disc |D|≤L are those with t near ±2√p; summing H over them:
  #{|D|≤L} ≈ Σ_{t: 0<4p−t²≤L} H(4p−t²) ≈ c·L^{3/2}/√p,  total ≈ 2p,  so **δ(|D|≤L) ≈ c·(L/p)^{3/2}.**
(The L^{3/2} comes from Σ_{d≤L} H(d) ~ L^{3/2}; the trace window has width ~L/√p.)

**Empirical validation (round018_backdoor_density.log).** Exact Hurwitz-class-number counts at
p ∈ {2^14, 2^16, 2^18}: the ratio δ / (L/p)^{3/2} is **constant ≈ 0.055** across L/p ∈ [0.03, 0.5]
(a 16× range) and all three primes — confirming the exponent 3/2. (Below L/p≈0.02 the counts are
single-curve and the ratio gets noisy: finite-size discreteness, not a scaling break.) Anomalous and
supersingular densities measured at δ ≈ c/√p (c≈0.2), as predicted.

**P-256 extrapolation (p≈2^256), seeds needed = 1/δ:**

| Named weakness | δ | seeds to plant |
|---|---|---|
| small CM disc \|D\|≤2^10 (GLV-usable) | ~2^{−369} | 2^369 |
| small CM disc \|D\|≤2^40 (generous) | ~2^{−324} | 2^324 |
| small CM disc \|D\|≤2^80 | ~2^{−264} | 2^264 |
| small embedding degree k≤2^20 (Balasubramanian–Koblitz) | ~2^{−208} | 2^208 |
| anomalous (#E=p, t=1) | ~2^{−128} | 2^128 |
| supersingular | ~2^{−128} | 2^128 |

All ≫ 2^80 (generous NSA seed/compute budget). **No named weakness is plantable via seed search.**

**Label.** The toy-validated scaling is OBSERVATION; the exponent 3/2 is THEOREM (class-number average);
the P-256 extrapolation is HEURISTIC (big extrapolation, but the exponent is proven, not fit). The
"not plantable" conclusion is RESTRICTED THEOREM in the BADA55 random-oracle-seed model.

**What this closes / leaves open.** Closes the chosen-seed trapdoor for every *named* weakness (doubly:
too rare to plant AND verifiably absent). The residual (T5) is sharpened to exactly: *an unknown ECDLP
weakness with δ ≥ 2^{−B}, recognizable from public (a,b)/j data, known to NSA ~1997* — i.e. it would
have to be **relatively common** (≥2^{−80} of curves) yet undiscovered by 30 years of public
cryptanalysis. Unfalsifiable, but maximally constrained, and identical for every deployed curve.

## E-CG — class-group structure of D = disc(P-256)

**Claim.** **THEOREM (genus theory).** Cl(O_K) for D=disc(P-256) has **2-rank exactly 4**: D is a
fundamental discriminant with ω(|D|)=5 distinct prime factors (3, 5, 456597257999, p₄, p₅), and for a
fundamental discriminant 2-rank(Cl) = (#prime divisors) − 1 = 4. Hence 16 | h(D) and the 2-Sylow has
rank 4.

**Interpretation.** 2-rank 4 is **exactly generic** for a 5-prime discriminant — no anomalous
structure. Class-group Pohlig–Hellman at the 2-part buys only a factor 16 toward vectorization —
negligible. No L1/L2 anomaly detected.

**Feasibility note (R4 / CSI-FiSh).** |D|≈2^258 ≈ 78 digits < CSI-FiSh's 155-digit class-group
computation, so the *full* Cl(O_K) (h(D) and all invariant factors) is classically computable at
≈ L_{|D|}[1/2] ≈ 2^{45}–2^{62}. Attempted via PARI `quadclassunit` (`round018_classno.log`): **timed
out at 40 min on a single core** (exit 124) — consistent with the subexponential estimate; the full
h(D) needs a CSI-FiSh-style dedicated computation, not a quick run. The 2-rank=4 result above is exact
(genus theory) and does **not** depend on it. Even a fully known Cl(O_K) gives only uniform sampling,
**not** vectorization (Couveignes), **not** an ECDLP break.

## Next

T2/PO-009 (gated-meter sweep over Cl(O_K) neighbors) — the one remaining test that could falsify the
"no weak B" headline at the open L3 level. In progress.

## T2 / PO-009 — gated-meter + true-GB sweep across isogeny neighbors (headline falsification test)

Reproduction: `round018_T2_isogeny_gatedmeter.sage` (+ `.log`, `_result.json`).

**Part A (leading-form level): RIGOROUS closure.** **OBSERVATION → THEOREM.** The leading form of the
Semaev polynomial is **independent of the curve coefficients (a,b)**: in S_3 = (x1−x2)²x3² −
2((x1+x2)(x1x2+a)+2b)x3 + ((x1x2−a)²−4b(x1+x2)), every (a,b)-dependent term has total degree ≤ 2 < 4,
so top_form(S_3) = x0²x1²−2x0²x1x2−2x0x1²x2+x0²x2²−2x0x1x2²+x1²x2² for **all** (a,b) (verified for 5
curves incl. (0,1),(9999,1234)). The same holds for S_m (coefficients enter only sub-leading terms).
**Consequence:** the audited leading-form gated meter (d_ff, D_reg, gate_passes, gate_meaningful) is
*literally identical* for every curve y²=x³+ax+b over F_p — confirmed: meter on (2,3) and (9999,1234)
both give d_ff=3, D_reg=6, gate_meaningful=False. **This closes T2 at the leading-form level for the
ENTIRE isogeny class** (indeed for every F_p curve), strengthening NR-022/PO-004 from "per-variable
degree invariant under one isogeny" to "the whole leading-form BFS analysis is (a,b)-blind."

**Part B (sub-leading / true Gröbner): weak negative evidence.** **OBSERVATION (TOY, low-resolution).**
Toy E0/F_8191, prime order N=8059. (Note: this toy has D=−15075=−3²·5²·67, conductor **f=15 — a TALL
volcano**, crater h(−67)=1; so the same-order neighbors collected via ℓ=3,5 isogenies span *different
volcano levels* = L2 variation, a bonus, but it is not a faithful flat-volcano analog.) For E0 + its
ℓ=3, ℓ=5 same-order neighbors, the true degrevlex GB of a real m=2 decomposition system (guaranteed
solution) gives **maxGBdeg=3, #sols=4, real-relation-found=True — identical across all** (no neighbor
solves lower). **Caveat (honest):** the different-order *negative control* gives the *same* numbers, so
this m=2 metric is **non-discriminating** — it confirms no gross degeneracy but is weak evidence, not a
strong falsification probe. m=2 in 2 variables is dominated by the |FB|-degree constraints and cannot
resolve coefficient-level effects.

**T2 net status.** Leading-form door **CLOSED** rigorously (Part A). Sub-leading door has only
weak negative evidence (Part B, coarse). **Sharp remaining probe (PO-009'):** measure the *true*
first-fall / solving degree of an m=3 (S_4) or m=4 (S_5) decomposition across horizontal Cl(O_K)
neighbors of a genuinely **flat-volcano** toy (f=1), where the variables are coupled and the
coefficients can in principle induce non-generic early falls (the NR-027/NR-032 machinery, applied
across the class rather than at one curve). Expected NEGATIVE by Part A's leading-form invariance,
but only an m≥3 true-first-fall measurement would settle the sub-leading level.

## Round-018 bottom line

- **T4/PO-011:** no NAMED weakness is plantable by seed search (all need ≫2^80 seeds; small-disc 2^324, MOV 2^208, anomalous/SS 2^128) — and all are verifiably absent. Density law δ~(L/p)^{3/2} empirically validated.
- **E-CG:** Cl(O_K) 2-rank = 4 (genus theory, exact) — generic, no anomaly; full h(D) feasible (<CSI-FiSh) but not the bottleneck.
- **T2/PO-009:** leading-form invariance of the Semaev meter across the class is now a (near-)theorem (Part A); the only surviving door is sub-leading m≥3 true-first-fall on a flat-volcano toy (PO-009').
