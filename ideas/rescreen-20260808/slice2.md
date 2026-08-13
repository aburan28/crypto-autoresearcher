# Adversarial re-screen — slice2 (19 records)

Reviewer: Red Team. Snapshot: `/tmp/wt-ideas-100` (read-only, `main`).
Web search **unavailable** (tool error on every attempt) — **all external novelty is
unadjudicated**. Every verdict below is an internal-corpus / internal-soundness verdict.

## Verdict table

| ID | verdict | one-line reason |
|---|---|---|
| IDEA-20260808-a3f7c1 | **REFUTED** | Its "factor-m yield advantage" is an ordered/unordered over-count: measured ratio exactly 3.000 in 12/12 cells, distinct relations ratio exactly 1.000, yield-per-candidate exactly 1.0000; and the "y-oracle" is a Tonelli–Shanks square root, not an oracle. |
| IDEA-20260808-d3eb2a | **REFUTED** | Its central quantity q(l,N) is 0, not ">0.5 at l≥3": the record's own clean bound 2·max\|A\|·n/2^{l+1} exceeds the modulus by 10^9–10^18; even an oracle-optimal threshold gives q ≈ 0.008–0.016 at every (N,l) tested. |
| IDEA-20260808-0b3072 | **REFUTED** (claim C only) | Fibre of code→determinantal form is NOT finite-independent-of-q: measured exactly #C(F_q)−1 = 5, 8, 11, 8 at q = 5, 7, 11, 13, i.e. Θ(q). Claims (A) and (B) are correct. |
| IDEA-20260808-d935d1 | **REFUTED** (second claim) | "Stratum size q^{k−(n−r_min)²} … exponentially large … Θ(n)" is false: the exponent is k−⌊√k⌋² = O(√k) and is **exactly 0** at every perfect-square k=n (4,9,16,25,36,49,64,81,100). |
| IDEA-20260808-9f9ed8 | **REFUTED** (L2) | 127 of 32131 weight-192 pairs meet in **0**, not 96; the pairwise term is 72% of the singleton sum, so the bracket is 1.83 bits not "<1 bit", ≈29 bits at the outer level; and its own Table-11 fixture misses (−11.14 vs −10.79). |
| IDEA-20260808-70243a | **REFUTED** (HB-6, hence the headline O(1)) | HB-6 claims polylog-smoothness of the index with probability p^{−o(1)}; from the record's own size statement the index is ≥ ~p^{1/2}, and CEP gives p^{−a/c+o(1)} = p^{−Θ(1)}. The "O(1) multiplicative overhead" headline does not survive its own heuristic. |
| IDEA-20260808-632866 | **REFUTED** (claim C, "the real deliverable") | Under KN-TECH-035's own definition (full cost = hardware × time) an independent-repetition reduction multiplies full cost by **exactly** 1/ρ, sequentially or in parallel. The claimed asymmetric charging does not exist. (A)+(B) are fine but overlap IDEA-20260805-cbd93d. |
| IDEA-20260808-95a21c | **SCOPE-INFLATED** | "multiple kilobytes ⇒ L in the hundreds to thousands ⇒ log2 L = 8–13 bits" is arithmetically false: a multi-KB transcript at SHAKE rate 136–168 B gives log2 L ≈ 4.6–5.9; 8 bits needs ≥34 KB, 13 bits needs ≥1.1 MB. |
| IDEA-20260808-cb0828 | **SCOPE-INFLATED** | Claim (A) is right (r(512)=0.96515, p_acc=0.506) but claim (B) is a **0.051-bit** shift in q-equivalent terms against a fatigue margin of ~437 (~7·10^3 in scale-free form); the "margin below 1.3" branch is off by 2.5 orders of magnitude and was computable before filing. |
| IDEA-20260808-778f82 | **PARTIAL-OVERLAP** (arithmetic defects) | Its own bound gives d ≤ 4 at uov-Ip, not "d ≤ 2"; the "factor 17 miss" is 8.5. And "the vOW interpolation is worse than guessing at every published set" is false at MAYO-1/3/5 by its own formulas (2^174 vs 2^200, 2^267 vs 2^316, 2^363 vs 2^436). |
| IDEA-20260808-d07cd4 | **PARTIAL-OVERLAP** | IDEA-20260805-bd8339 already defines d_max over **distinct** irreducible factors, already identifies A_i as local-with-radical for e_i>1, and already names "the radical-lifting step for repeated factors" as its undischarged obligation with a dedicated REPEATED-FACTOR ARM. d07cd4's `discriminated_from` ("treats factor DEGREES, not MULTIPLICITIES") is false against bd8339's text. |
| IDEA-20260808-348896 | **PARTIAL-OVERLAP** (internal contradiction) | Claim (iii)'s reduction factor ℓ/d is inverted: support ⊆ ⟨(d,d)⟩ ⇒ F_{q^d}-quadratic ⇒ variable count drops by **d**, not ℓ/d. At d=ℓ (the \|S\|=1 case) the record's formula gives factor 1 while its own `sota_delta` claims factor ℓ. Prediction 3 also contradicts `survival_depth`. |
| IDEA-20260808-4c309d | **PARTIAL-OVERLAP** (unit error) | The floor `rank(M) − rel` subtracts A2-1's 960/1216/1248, which are **GF(2)-bit** relation counts, from a **byte-valued** rank bounded by 32; and `time_exponent` then multiplies (rank−rel) by 8. One of the two readings must be wrong and the floor is negative under either. |
| IDEA-20260808-bfee7e | **PARTIAL-OVERLAP** (exposure mismatch) | Its second comparison population, the 27-arm reference (mean 15.48, range 6–25, EV-AES-d81acf), is at **2^30–2^31** trials; E_geom is to be derived at **2^32**. Scaled to matched exposure the reference mean is ≈62, i.e. AES's 59 sits at the mean. Also states 15.63× where 59/4.0 = 14.75 and the evidence says 14.75×. |
| IDEA-20260808-24c61b | **PARTIAL-OVERLAP** (HA-1 mis-stated) | HA-1's mean 3^m/B^m is <1 for B>3; the exact count is **3^{m−1}** with **zero variance** on the bulk (measured 9/9/27/27 in 4/4 cells), so HA-1 is not a heuristic at all and its stated value is off by B^m/3. Claim A itself is sound. |
| IDEA-20260808-0eb075 | **PARTIAL-OVERLAP** (no method ceiling) | ρ(δ) is correct, but the record has **no `method_ceiling` entry** and never bounds its own prize: required N ∝ ln(trial count), so replacing q^{k_fft} by N_eff ≥ N caps the gain at the ratio ln N_eff / (k_fft ln q). Also HA-1 is stated "uniformly for N ≪ q^{k_fft}", and whether the deployed MATZOV point satisfies that is not checked. |
| IDEA-20260808-ceca08 | **NOVEL** | All exact arithmetic verified on 125 toy curves: 0 violations of n_1²\|#E, n_1\|p−1, n_1\|gcd(A−1,f), n_1\|cofactor; 46/125 curves have n_1 < gcd(A−1,f) (f_E>1), which is the identity's content. Minor: "confined to ℓ=2" holds only for 2-power cofactors (n_1 = 5 observed). |
| IDEA-20260808-c4b462 | **NOVEL** | Every exponent and every row of the concrete-cost table re-derived and correct; the method ceiling γ=1/3 is right; twelve `discriminated_from` entries; honest 0.03 prior. Cleanest cost accounting in the slice. |
| IDEA-20260808-b5b9ca | **NOVEL** | STEP 1 and STEP 2 re-derived and correct (Trd=0 ⇒ α²=−Nrd(α); Σ_{d≤T} h(−4pd)/(p/12) ~ T^{3/2}/√p). Objection: branch (B)'s prior of 0.2 is generous — the gap p^{4/3} vs p^{2+ε} is p^{2/3}, so branch (B) requires a major new analytic-number-theory theorem. |

---

## Detail for every non-NOVEL verdict

### IDEA-20260808-a3f7c1 — REFUTED

The record's mechanism STEP 2 derives, and its `predictions` re-state, `Y_guided /
Y_exhaust = m = 3.0 ± 0.5`, with "a ratio of 1.0 ± 0.2 falsifies the mechanism".
Claim (D) asserts "The search space is V (size B), not V^m … The algorithm's cost is
O(B * C_decomp) … not O(B^m * C_verify) as in MITM."

I ran the record's own experiment (p ∈ {101,103,107,211}, B ∈ {10,20,50}, m=3, 100
random targets per cell, matched solution sets, factor base = one point per x):

```
   p   B | exhaust distinct rel  cand |  guided rel(mult)  distinct     cand | ratio_mult ratio_distinct ratio_cand yield/cand
 101  10 |                  124 12000 |               372       124    36000 |      3.000          1.000      3.000     1.0000
 101  20 |                 1174 114000 |              3522      1174   342000 |      3.000          1.000      3.000     1.0000
 101  48 |                18087 1729600|             54261     18087  5188800 |      3.000          1.000      3.000     1.0000
 103  43 |                14096 1234100|             42288     14096  3702300 |      3.000          1.000      3.000     1.0000
 107  50 |                15864 1960000|             47592     15864  5880000 |      3.000          1.000      3.000     1.0000
 211  50 |                 9501 1960000|             28503      9501  5880000 |      3.000          1.000      3.000     1.0000
```
(12/12 cells identical; abridged.)

The predicted 3.0 appears **exactly**, and it is an artifact. The guided loop reports each
3-subset relation once per choice of which member plays P_0, i.e. m times: distinct
relations found are **identical** (ratio 1.000 in 12/12). It also examines exactly m times
as many candidates: B·C(B−1,2) = m·C(B,m)·(B/(B−2)). Yield per candidate examined is
**1.0000 in 12/12**. So claim (D) is backwards — the algorithm is *strictly worse* than
exhaustive search by exactly the factor m in candidates, and identical in relations found.
This is the standard "fix one element, solve the (m−1)-sum" restructuring of exhaustive
search, not a new algorithm.

Second, independent defect: **O_y is not an oracle.** Given x_0, y_0 is a modular square
root of x_0³+ax_0+b, computable by Tonelli–Shanks in O(log³ p). The record's
`hidden_overhead` says "If the oracle is simulated by exhaustive search (trying all y for
each x), the cost is O(B * p^{1/2}) per target" — that is a fabricated cost for a textbook
polynomial-time operation, and it means the "information content of the oracle" the
proposal exists to measure is zero bits.

Third: NULL OBJECT 1 is not implementable. "a RANDOM oracle O_rand … returns a uniformly
random y_0" produces (x_0,y_0) that is **not on E**, so `R − P_0` is undefined; and its
stated ⊥-rate (1 − B/p) does not match the true oracle's (≈1/2), so the signatures are not
matched either.

Cheapest discriminating control the record should have carried: deduplicate relations and
divide by candidates examined. That single change turns the headline 3.0 into 1.0.

Adjacency note: `KN-FIND-a8990a` (Semaev summation cover, monodromy (Z/2)^{m−2}) is the
right barrier record for arity-m decomposition and is not cited; it was invisible in the
dedup corpus.

### IDEA-20260808-d3eb2a — REFUTED

Claim: "a pair containing an erroneous sample fails that norm test with probability bounded
below by a computable quantity q(l,N)", prediction "above 0.5 at l ≥ 3 and below 0.15 at
l = 1", and HA-13's rigorous ingredient "The clean bound |A_j u_i − A_i u_j| ≤ 2 max|A|
n/2^{l+1} is an exact triangle inequality".

The bound is exact and **vacuous**. A_i is essentially uniform mod n, so max|A| ≈ n and the
bound is ≈ n²/2^l, which exceeds the modulus n for every l < log2 n. Measured directly
(planted corruptions, ground truth, 4000 pairs per cell):

```
 Nbits   l  clean bound/n   q_measured   clean pairs passing
    32   3      5.369e+08       0.0000                1.0000
    48   3      3.518e+13       0.0000                1.0000
    64   3      2.306e+18       0.0000                1.0000
    64  16      2.815e+14       0.0000                1.0000
```
(18/18 cells: q = 0.0000.)

Even with an **oracle-optimal** threshold calibrated to accept 99% of clean pairs, the best
achievable rejection rate on corrupted pairs is q ≈ 0.008–0.016 — indistinguishable from the
1% false-positive floor — because both residual distributions are uniform (mean |res|/n ≈
0.2500 for clean and 0.2500 for corrupted at every l ∈ {1,3,8,16}, N ∈ {32,48,64}).

The elementary reason, available at zero cost before filing: eliminating d from two samples
leaves one congruence in two unknowns of size n/2^l, so the expected number of consistent
(u_i,u_j) is (n/2^l)²/n = n/4^l ≫ 1 whenever 2l < log2 n. A corrupted pair is therefore
consistent too. The record's own weak-point paragraph silently drops the |A| factor
("At l = 1 the clean bound is n/4"), which is where the wrong l-dependence comes from: the
mechanism text and HA-13 use 2|A|n/2^{l+1}, the weak-point text uses 2n/2^{l+1}.

Narrowest surviving statement: the (1−e)^m law of H-ECDSA-7ccd4b stands against *this*
predicate at every l, not only at l = 1 — a stronger negative than the record anticipated,
and the record's stated "deliverable is the LOCATION of the transition in l" has no
transition to locate.

### IDEA-20260808-0b3072 — REFUTED (claim C)

Claims (A) (trace-form hull not GL_m×GL_n-invariant) and (B) (Δ_{ACB} = det A det B · Δ_C)
are both correct — I re-derived both.

Claim (C): "the fibre of the map 'code to determinantal form' is finite modulo the group for
generic codes, **by the classical theory of determinantal representations**, so the reduction
loses only a finite ambiguity", with prediction "Finite and small (bounded by a function of
m and k alone, **not growing with q**). Growth with q falsifies (C)."

At the record's own smallest minimal-test cell m=n=k=3 I counted GL_3×GL_3-classes of
determinantal representations of a fixed smooth plane cubic (Fermat X³+Y³+Z³), by
normalising M_1 = I and M_2 to a fixed regular-semisimple companion matrix and dividing by
the residual centraliser:

```
  q  #reps(M1=I,M2=C)  |Z(C)|  #GLxGL-classes  #C(F_q)  #C(F_q)-1
  5               120      96           5.000        6          5
  7               288     216           8.000        9          8
 11              1320    1200          11.000       12         11
 13              1152    1728           8.000        9          8
```

The class count is **exactly #C(F_q) − 1** in 4/4 cells, i.e. Θ(q). That is precisely what
the classical theory the record cites says: determinantal representations of a smooth plane
curve of degree d correspond to line bundles of degree d(d−1)/2 with H⁰(L(−1)) = 0, i.e. to
Pic^{g−1} minus one point — a **g-dimensional family**, not a finite set. The record's own
mechanism text names this ("for plane curves these correspond to line bundles of the right
degree") and then draws the opposite conclusion. This is the same failure mode as
IDEA-20260808-2e14f7 citing Chebotarev for a claim Chebotarev contradicts.

Scaling: for k = 3 and m = n the form is a plane curve of degree n with genus (n−1)(n−2)/2,
so the fibre is ~q^{(n−1)(n−2)/2} — exponential in n². The record's falsification condition
#3 ("solution set grows with q, falsifying (C) and making the reduction lose exponentially
much information") fires.

Narrowest surviving statement: (A) is a correct and useful named obstruction (support
splitting does not transfer to MCE); (B) is a correct transformation law. The *reduction*
in (C) is not information-preserving and must not be filed as "loses only a finite
ambiguity".

### IDEA-20260808-d935d1 — REFUTED (second claim)

"SECOND CLAIM: at square parameters with k about m = n, the formula gives r_min about
n − sqrt(k) and a stratum of size about q^{k − (n − r_min)²}, **which is exponentially
large** — so the distinguished-set route is blocked for a COUNTING reason", and
`target_complexity.time_exponent`: "At square parameters with k about n that exponent is
**Θ(n), i.e. exponential**."

The r_min formula is right; the exponent is not. r_min is the least r with k ≥ (n−r)², so
n − r_min = ⌊√k⌋ and the exponent is k − ⌊√k⌋², which is **O(√k)** and is **exactly 0**
whenever k is a perfect square:

```
 n=k | r_min | n-r_min | exponent k-(n-r_min)^2
   9 |     6 |       3 |                      0
  14 |    11 |       3 |                      5
  16 |    12 |       4 |                      0
  22 |    18 |       4 |                      6
  24 |    20 |       4 |                      8
  25 |    20 |       5 |                      0
  36 |    30 |       6 |                      0
  64 |    56 |       8 |                      0
 100 |    90 |      10 |                      0
```
Verified k − ⌊√k⌋² ≤ 2√k for all k ≤ 20000.

So the counting gate does **not** block the Leon-style route at square parameters; it says
the smallest nonempty stratum is q^{O(√k)}, and O(1) at perfect-square k = n. The record's
own falsification condition ("Some realistic parameter shape yields a polynomial-size
smallest stratum, which reopens the Leon-style route") fires at k = n ∈ {9,16,25,36,49,64,
81,100}. The record's `sota_delta` — "supplies the reason the answer is no at square
parameters" — is therefore not supported by its own formula.

Note the gate may still be practically binding at deployed shapes (k=n=24 gives exponent 8,
q^8 ≈ 2^96 at q≈2^12), but that is a **q-dependent concrete** statement, not "Θ(n),
i.e. exponential". The record must be restated with the correct exponent before it can serve
as a feasibility gate, and the "no Leon-style attack can exist" conclusion withdrawn.

### IDEA-20260808-9f9ed8 — REFUTED (L2, the claim the record says it rides on)

Three separable defects, all cheaply checkable.

**(a) The codeword geometry is wrong.** "two distinct weight-192 codewords of the
[384, 8, 192] code meet in exactly 96 coordinates and the pair probability is a
two-dimensional binomial-type sum over the induced 4-cell partition". I built the code
(RM(1,7) 3-fold duplicated) and enumerated all pairs:

```
length: 384  #codewords: 256  weight distribution: {0: 1, 384: 1, 192: 254}
pairwise |supp(c) cap supp(c')| histogram over all 32131 pairs: {0: 127, 96: 32004}
```
127 pairs (the complementary pairs c, c+1) meet in **0** coordinates. For those the induced
partition has two empty cells and the "4-cell" sum degenerates.

**(b) L2's own width formula is wrong, and the true width is ~1.8 bits, not <1.**
Computing exactly with the record's transcribed p* = 0.3398 and the true geometry:

```
singles sum (254*single + all-ones) = 2^-11.14
sum over pairs (true geometry)      = 2^-11.61        -> S2/S1 = 0.718
Bonferroni-2 lower bound            = 2^-12.96
inner bracket width log2(upper/lower) = 1.826 bits    (record predicts "Under 1 bit")
```
The record's stated width "log2(1 + sum_pairs / sum_singles)" evaluates to 0.78 bits and is
the wrong formula; the correct width is −log2(1 − S2/S1) = 1.83 bits. Compounded at the
outer stage the record's own rule gives (δ_e+1)·b = 16 × 1.83 ≈ **29 bits**, against the
predicted "about 3 bits, which is USEFUL" and toward the "about 128 bits, which is useless"
branch. The record's supporting argument — "the union bound is loose by only about 0.17
bits, which says the 255 events are nearly disjoint - exactly the regime where second-order
Bonferroni is tight" — is refuted: the pairwise term is 72% of the singleton term.

**(c) The record's own regression fixture fails.** "with p* = 0.3398 the single-codeword
probability Pr[Bin(192, p*) ≥ 97] should land near 2^-18.8, and 255 times that near 2^-10.8,
reproducing the specification's number - which is the sanity check that the transcribed
figures are being used correctly."

```
Pr[Bin(192,0.3398)>=97]  = 2^-19.125          (record: "near 2^-18.8")
254*single + all-ones    = 2^-11.136          (Table 11 predicted -10.79)
255*single               = 2^-11.130
```
Nor does any variant reading fix it: ties-as-failures gives −10.134, Prop 6.1.4 tie-credit
gives −10.550. The p* that would reproduce −10.79 under the strict reading is 0.34146, not
0.3398. So the transcription/event model is not yet pinned, and the record's `baseline_
embedding.reproduction_check` ("must reproduce Table 11's −10.79 … to within the rounding of
the printed p* values") does not pass at 0.35 bits.

Narrowest surviving statement: a two-sided bracket via second-order Bonferroni is
computable and correct as a *method*, but at HQC-1 it is ≈1.8 bits inner / ≈29 bits outer,
which the record itself classifies as crypto-irrelevant.

### IDEA-20260808-70243a — REFUTED (HB-6, and with it the headline)

Headline: "EndRing at p^{1/3+o(1)} with an **O(1) multiplicative overhead** and no
(log N)^{-12}", `sota_delta` "removes an overhead this corpus prices at 2^96–2^192 …
replacing it with a factor 3 plus a saturation".

HB-6: "the index [End(E) : O''] behaves like a uniformly random integer of its size with
respect to smoothness, so it is (log p)^{O(1)}-smooth **with probability p^{−o(1)}**", with
`rigorous_ingredient` "The index is exactly sqrt(disc(O')/p²) … Its SIZE is therefore
rigorous" and `distribution_imitated` "Canfield-Erdos-Pomerance / Dickman-de Bruijn".

The cited theorem contradicts the claim. The record's own SC-2 check states deg(α_i) =
p · deg(φ) · deg(ω)², so every reduced norm is ≥ p, hence disc(O'') ≳ 16·n₁n₂n₃ ≳ 16p³ and
the index ≳ 4p^{1/2}. CEP/Dickman for an integer of size p^a with B = (log p)^c gives
u = a log p/(c log log p) and u^{−u} = exp(−(a/c)·log p·(1−o(1))) = **p^{−a/c+o(1)}** — a
polynomial loss, not p^{−o(1)}. Concretely (CEP exponent −u log2 u, a = 1/2):

```
 log2 p   log2(index)>=   B=(log2 p)^c    u      u^{-u} as log2
    256             128   c=3, 2^24.0   5.33            -12.9
    512             256   c=3, 2^27.0   9.48            -30.8
   1024             512   c=3, 2^30.0  17.07            -69.9
```
The exponent grows linearly in log p. So HB-6 is false as stated, and with it the "O(1)
multiplicative overhead": the record's own model gives a p^{Θ(1)} inverse-success factor,
which is an exponent change, not a constant.

There is a second, opposite problem the record creates for itself: "the whole step is
polynomial iff the index is smooth or has a factorable shape" and "a large prime factor
makes saturation expensive". Saturating a quaternion order at a *known* prime q is
polynomial in log q; the only genuinely hard sub-step is **factoring** the index, which at
256-bit p is L_p[1/3] ≈ 2^{50}, far below the 2^{85.3} headline. So the record simultaneously
overstates the risk (it is factoring, not saturation) and understates the heuristic cost
(p^{−Θ(1)}, not p^{−o(1)}). Either the heuristic or the risk statement has to go; the record
cannot keep both and still claim O(1).

Cost-model challenge the record does not answer (my contract's hidden-overhead item):
it claims memory p^{1/3+o(1)} and time p^{1/3+o(1)} and asserts `dominated_by` "KN-TECH-057's
four full-cost rows" were checked, but never converts to full cost. Under KN-TECH-035/057,
S = p^{1/3} gives τ = S^{1/3} = p^{1/9} and full cost p^{1/3}·p^{1/9} = **p^{4/9}**, against
KN-TECH-057's VW matched baseline p^{1/2} (F_{p²}) at polynomial per-processor space. The
advantage survives (4/9 < 1/2) but is 0.056 in the exponent, not the picture the
`dominated_by` line paints. Require the p^{4/9} number in the record.

Note: 70243a is the only record in this slice touching KN-TECH-057 ground, and — unlike the
brief's expectation — it *does* cite KN-TECH-057 by ID. What it does not do is use it.

### IDEA-20260808-632866 — REFUTED (claim C)

(A) and (B) check out arithmetically. ρ = C(n/d,w/d)^d/C(n,w) and the record's Stirling form
Θ(d^{d/2}(2πw(1−w/n))^{−(d−1)/2}) agree to within 0.2–1.8% across (n,w,d) grids, and
log2(1/ρ) is 3.2–3.7 bits at d = 2 ("a handful of bits" ✓).

Claim (C) is described as "the real deliverable": "the 1/rho repetitions multiply TIME while
leaving MEMORY unchanged - so under the full-cost composition this program uses
(KN-TECH-035, KN-TECH-044) the reduction's overhead is charged asymmetrically and the bit
count in (A) is not the bit count that matters", with prediction "Strictly greater than
1/rho for memory-heavy solvers".

KN-TECH-035 defines full cost as **hardware × time**. For a reduction that repeats an
independent trial 1/ρ times:
- sequentially: hardware unchanged, time × 1/ρ → full cost × 1/ρ;
- in parallel: hardware × 1/ρ, time unchanged → full cost × 1/ρ;
- in KN-TECH-057's W×τ form: W → W/ρ, S unchanged so τ = S^{1/3} unchanged → full cost × 1/ρ.

The overhead is **exactly 1/ρ on the full-cost axis, independent of the solver's memory
exponent**. There is no asymmetry to charge. If anything the sign is the other way: a
reusable table amortised across repetitions makes the composed cost *sub*-1/ρ.

What remains: (A)+(B), which the record itself concedes may be dominated by
IDEA-20260805-cbd93d ("dominates the numeric value of log2(1/rho) if its admissibility ratio
is the same quantity - which, from its claim text, it appears to be") and which is standard
folklore for regular/split syndrome decoding. Required `discriminated_from` addition: "the
every-adversary quantifier of the reduction formulation, and nothing else; the full-cost gap
claimed in (C) is zero under KN-TECH-035."

### IDEA-20260808-95a21c — SCOPE-INFLATED

"Predicted magnitude for (B): FAEST signatures are multiple kilobytes, so L is in the
hundreds to thousands of hash blocks and log2(L) is between about 8 and 13 bits", and
`time_exponent`: "a 10-bit correction would put the charged forgery cost near 2^116, which
is a CATEGORY-RELEVANT number".

From the record's own premise:

```
transcript                         SHAKE128 (r=168 B)      SHAKE256 (r=136 B)
4 KB                                 L= 24.4, log2=4.61      L= 30.1, log2=4.91
8 KB                                 L= 48.8, log2=5.61      L= 60.2, log2=5.91
32 KB                                L=195.0, log2=7.61      L=240.9, log2=7.91

log2 L = 8  requires a transcript >= 43,008 B (SHAKE128) / 34,816 B (SHAKE256)
log2 L = 13 requires a transcript >= 1,376,256 B / 1,114,112 B
```
"Multiple kilobytes" gives log2 L ≈ 4.6–5.9, not 8–13. To reach the top of the stated band
you need a ~1.1 MB hashed string. The prediction is inflated by roughly 3–8 bits and the
2^116 "category-relevant" sentence has no support from the record's own premise. Even at a
generous 26 KB transcript the answer is ≈7.6 bits.

Second objection (units, partially self-flagged): the correction is to the attacker's cost
in **compression calls**, while the matched baseline 2^{126.1} is in AES operations. Any
statement of a margin must convert both to the same unit; a SHAKE permutation is not one AES
call. The record's confounder about "one oracle query regardless of length" flags the
bound-vs-table distinction but not the unit mismatch in the comparison itself.

### IDEA-20260808-cb0828 — SCOPE-INFLATED

Claim (A) is correct and I confirm it exactly. FALCON's σ_{f,g} = 1.17√(q/2n) makes
E[‖(f,g)‖²] = 1.17²q, so the acceptance bound 1.17√q sits at the mean and the truncation
point is T = 2n in χ²_{2n} units:

```
     n  dof=2n    p_acc   r=E[X|X<=T]/E[X]   log2(1/r) = bits of q-equivalent shift
   256     512   0.5083            0.95096                                   0.0725
   512    1024   0.5059            0.96515                                   0.0512
  1024    2048   0.5042            0.97527                                   0.0361
  2048    4096   0.5029            0.98247                                   0.0255
```
r(512) = 0.96515 lands in the record's own "material" band [0.9, 0.98]; the decay control
r(1024) > r(512) holds. Good so far.

Claim (B) is where the scope inflates. −10 log10(r) = **0.154 dB = 0.051 bits of q**. Against
the fatigue point (Ducas–van Woerden q* ≈ n^{2.484}, both the criterion and q = 12289
recalled, as the record flags):

```
  n=512: q* = 5.368e6, q = 12289, margin q*/q = 436.8 -> 421.6 with the conditional width
  n=1024: margin 2443.8 -> 2358.7                       (record's decision threshold: 1.3)
```
Sharper and criterion-independent: FALCON *fixes* σ² = 1.17²q/(2n), so the fatigue-relevant
ratio q/σ² = 2n/1.17² = **748 at n=512, independent of q**, against n^{2.484} ≈ 5.4·10⁶ — a
factor 7.2·10³. A 3.5% move in σ² cannot approach a 10³–10⁴ gap under any criterion in that
family.

So the record's `honest_prior_of_survival` "P(the margin recomputation lands below 1.3)
~ 0.12" is not defensible: it was decidable in one line from the record's own recalled
numbers before filing. The mechanism (deployed width is the conditional width) is real and
worth recording; the "first-order finding about FN-DSA-512" framing and the block-size-sign-
flip prediction are not. Narrowest supported statement: "keygen rejection reduces
E[‖(f,g)‖²] by 3.5% at n=512 and 2.5% at n=1024; this is 0.05 bits of q-equivalent movement
and does not change any regime verdict."

### IDEA-20260808-778f82 — PARTIAL-OVERLAP with two arithmetic defects

The central inequality is correct and I verified the parameter table:

```
set                               (n-o)(m+2)     4n   ratio   d_max=2n/(m+2)  d_need=(n-o)/2
uov-Ip (112,44,44)                      3128    448    6.98             4.87            34.0
MAYO-1 (66,64,8)                        3828    264   14.50             2.00            29.0
```
Both of the record's quoted instances reproduce. Also verified: the m=1 baseline embedding
(d ≤ 2n/3, and 3(n−o) ≤ 4n for all o ≥ 0); the crossover n > 3o; and the whipping invariance
(both sides scale by k).

Defect 1 — `sota_delta`: "at RECALLED uov-Ip the split MitM would need d >= 34 while the
existence count permits **d <= 2**; the miss is a factor 17 in d". The record's own bound is
d ≤ 2n/(m+2) = 224/46 = 4.87, i.e. **d ≤ 4**; the miss is 34/4 = **8.5**, not 17. The
headline deliverable number is wrong by 2×.

Defect 2 — `memory_exponent`/`time_memory_tradeoff`: "A van Oorschot-Wiener interpolation
gives time q^{3(n-o)/4}/sqrt(w) at memory w, which is the honest low-memory statement and
**is worse than guessing at every published set**" and "the interpolation makes the MitM
strictly worse, which strengthens the closure". False in MAYO's regime, by the record's own
two formulas at w = 1:

```
set                     log2 q^{3(n-o)/4}   log2 q^{n-2o} (guessing)   vOW worse?
uov-Ip (112,44,44)                  408.0                      192.0         True
MAYO-1 (66,64,8)                    174.0                      200.0        False
MAYO-3 (99,96,10)                   267.0                      316.0        False
MAYO-5 (133,128,12)                 363.0                      436.0        False
```
Since the record states "that crossover is stated because it is why the closure matters most
for MAYO", the sentence that the tradeoff strengthens the closure is exactly wrong in the
regime the closure is for. The closure still holds — the existence inequality fails at MAYO
by a factor 14.5 — but the "strictly worse under vOW" support must be withdrawn.

Required `discriminated_from` addition: none needed for corpus overlap (I confirmed no
multivariate corpus record addresses MitM), but the two numbers above must be corrected
before the record is used as a design threshold.

### IDEA-20260808-d07cd4 — PARTIAL-OVERLAP

`why_not_a_renamed_known_approach` says: "IDEA-20260805-bd8339 claims the exponent is
governed by d_max(f), the largest factor degree, via a CRT split and a rank spectrum. This
record AGREES on d_max for the squarefree case and **adds the case that record does not
treat: repeated factors**"; `discriminated_from` says bd8339 "treats factor DEGREES, not
MULTIPLICITIES, and proposes no lifting algorithm."

bd8339's own text (read at `/tmp/wt-ideas-100/ledger/proposals/IDEA-20260805-bd8339.yaml`):
- headline defines d_max as "the largest degree among the **DISTINCT** irreducible factors of f";
- line 33: W "EXISTS AND IS INVERTIBLE FOR EVERY monic f, **including non-squarefree f**";
- line 163: "For a repeated factor (e_i > 1), A_i is local with radical …";
- lines 82–83: the exponent claim holds "as far as **the radical-lifting step for repeated
  factors is cheap** -- the second of which is NOT derived here";
- line 494: "The repeated-factor lift is NOT derived";
- lines 412–414: a dedicated "REPEATED-FACTOR ARM … f = p^e with p irreducible … this arm
  tests the radical-lifting claim".

So the repeated-factor case, the local-ring/radical structure, and the exponent statement
deg f_i (not e_i·deg f_i) are all already in bd8339, which explicitly names the lifting as
its undischarged obligation and designs the experiment for it. d07cd4's genuine contribution
is the Newton/Hensel derivation and its ⌈log2 e⌉-linear-solve cost — i.e. it **discharges
bd8339's named open lemma**, which is valuable, but it is not a new weak-parameter family
and its `discriminated_from` text is false against bd8339.

Density claim: "a uniformly chosen degree-ell polynomial is non-squarefree with probability
exactly 1/q" is correct (monic squarefree count = q^n − q^{n−1} for n ≥ 2). But bd8339
already prices the *reducible* family at density 1 − I_q(ℓ)/q^ℓ ≈ 1 − 1/ℓ, and the
non-squarefree family is a measure-1/q **sub**-case of it. So "one in q parameter choices is
in this family" understates rather than adds exposure.

Required `discriminated_from` text (supply verbatim):
> "IDEA-20260805-bd8339 already states d_max over DISTINCT irreducible factors, already
> identifies A_i as local with nilpotent radical for e_i > 1, and explicitly names the
> radical-lifting step for repeated factors as NOT derived (lines 82–83, 494) with a
> dedicated REPEATED-FACTOR ARM (lines 412–414). This record does not open a new case; it
> supplies the missing lemma — the Newton linearisation modulo N^{2k} and its ⌈log2 e_i⌉
> linear solves — that bd8339's exponent claim already depends on. The 1/q non-squarefree
> density is a sub-case of bd8339's already-computed reducible density 1 − I_q(ℓ)/q^ℓ and is
> not a separate exposure."

Additional objection (not resolvable here): step (1) asserts "the public key … splits
correspondingly". QR-UOV's public forms are F_q-valued quadratic forms on F_q^{nℓ} with
block structure; the CRT/radical reduction requires the forms to factor through A. The
record must exhibit that structure rather than assume it — which is precisely the direction
audit IDEA-20260805-bb9f73 is filed against, and which d07cd4 cites but does not consume.

### IDEA-20260808-348896 — PARTIAL-OVERLAP (internal contradiction)

The core object is sound: I verified that the Frobenius-bidegree expansion is a bijection
onto F_q-quadratic maps (ℓ²N² coefficients in A, i.e. ℓ³N² over F_q, matching
ℓ·(Nℓ)(Nℓ+1)/2 after the (i,j)↔(j,i) symmetrisation), that A-linear changes of variables
preserve each slot, and that A-semilinear ones shift bidegrees by a constant.

Defect 1 — the reduction factor is inverted. Claim (iii): "if S(pk) is contained in the
subgroup generated by (d,d) for some d dividing ell, the map is F_{q^d}-quadratic and a
PARTIAL reduction to F_{q^d} applies, **cutting the attacker's variable count by a factor
ell/d**"; `target_complexity`: "variable count drops from n ell² to n ell²/(ell/d), i.e. the
exponent … drops by the factor d/ell."

If support ⊆ ⟨(d,d)⟩ then Y ↦ λY for λ ∈ F_{q^d} scales the map by λ², so the map is
F_{q^d}-quadratic and the variable count over F_{q^d} is nℓ²/**d**, not nℓ²·d/ℓ. Test at the
record's own extreme: |S| = 1 is the case d = ℓ (⟨(ℓ,ℓ)⟩ = {(0,0)}). The record's formula
gives factor ℓ/d = 1, i.e. **no reduction** — while its own `sota_delta` says "|S| = 1 would
mean SNOVA's effective variable count is n·ℓ rather than n·ℓ², a factor-ℓ reduction". The
two statements are mutually exclusive. (The numerical example ℓ=4, d=2 does not discriminate
because ℓ/d = d there.)

Defect 2 — prediction 3 contradicts `survival_depth`. Prediction 3: "stability of S(pk)
across 100 independently generated SNOVA keys … predicted: **Identical for all keys**,
because the support is determined by the Q-twist construction, not by the key."
`survival_depth`: the support "**DISSOLVES** under an F_q-linear change of variables that is
not A-semilinear, which is exactly the secret transformation SNOVA applies". Both cannot
hold. The deciding fact — whether SNOVA's secret T is A-linear or merely F_q-linear — is a
one-line spec read, not a 100-key experiment, and the record should say so rather than
schedule the experiment.

Defect 3 (minor) — HA-1's bound: a uniform F_q-quadratic map on A^N has a given bidegree slot
empty with probability q^{−ℓN²}, not q^{−N}; the stated bound is conservative but the
exponent is wrong.

### IDEA-20260808-4c309d — PARTIAL-OVERLAP (unit error in the floor)

The mechanism (a backward dependency invariant that lower-bounds guessed key bytes) is a
real gap-filler and I found no corpus record doing it. Two defects.

Defect 1 — units. The floor is "rank(M) minus the key-schedule relation count (the quantity
catalogue A2-1 reports as **960/1216/1248** for AES-128/192/256)", and `time_exponent` then
says the floor is "**8*(rank(M) - rel)** bits". The 960 figure is a count of **GF(2)-linear
bit relations** (AES-128: 30 words × 4 bytes × 8 bits = 960); rank(M) is a **byte-valued**
rank over GF(2^8) on a matrix "at most 32 x 16(R+1)", hence ≤ 32. Under the byte reading the
floor 8·(rank − 960) is hugely negative; under the bit reading the ×8 is double-counting.
The record's `minimal_test` does say "relations restricted to the spanned round keys", which
is the right object, but the claim text imports the global 960 directly. Fix the unit and the
restriction before the table is built.

Defect 2 — the fixture is not a fixture. Prediction 1: "rank(M) for the 4-round integral
shape … predicted: exactly 4 (one last-round-key column), deficit 0 - a hand-known fixture",
and `falsification_conditions`: "rank(M) is not 4 on the 4-round fixture - construction
wrong". Real AES omits MixColumns in the final round, in which case one byte of the last
round key suffices and the answer is **1**; with MixColumns present it is 4. The record does
not pin which the harness implements, so a fixture that can be satisfied by either reading
cannot falsify anything. Required control: pin the final-round MixColumns convention in the
pinned FIPS-197 harness and re-state the fixture value.

Third, a definitional objection: M is built "through the LINEAR PART ONLY (… SubBytes
replaced by an opaque per-byte bijection)". With opaque bijections there is no matrix over
GF(2^8) to take a rank of; what the lossy-projection paragraph actually describes is a
dependency-**set** closure ("MixColumns merges each four into their union"). Set cardinality
and GF(2^8) rank coincide only when the dependency map is full rank on its support. The
record must say which quantity it computes, since the closure sentence ("no attack in the
class can guess fewer than rank(M) − rel") is only valid for the set version.

### IDEA-20260808-bfee7e — PARTIAL-OVERLAP (exposure mismatch)

The record's design is otherwise good (pre-registration as a commit, a baseline-embedding
check that must return 4.0, a non-MDS sibling null, an r-sweep decay control — exactly the
artifact tell my contract asks for). Two defects, both in the numbers it imports.

Defect 1 — mismatched exposure in the second comparison population. HA-1's
`validation_route` says: "At real-AES scale, reuse the already-committed 27-arm random-S-box
reference distribution (mean 15.481481481481481, range 6-25 …) as a second comparison
population at zero new compute", and `tail_checks` says "Compare the closed form against the
EXTREMES 6 and 25 of that reference distribution". But E_geom is to be derived "at the
campaign's exact configuration (**N=2^32**, amask=1, smask=1)", while EV-AES-d81acf's scope
line reads "**2^30-2^31 trials per arm**" (and its own text scales an arm "at 2^31 trials …
to a 2^30-equivalent rate"). Comparing a 2^32 prediction against unscaled 2^30–2^31 counts
guarantees an apparent factor-2-to-4 mismatch that is pure exposure. Scaled to 2^32 the
reference mean is ≈62 — i.e. AES's 59 sits essentially **at** the random-S-box mean, which
is the same conclusion EV-AES-048545 reached (58/51 vs 59) and which the derivation would
otherwise appear to contradict. This is the same matched-exposure discipline EV-AES-e4c091
was already flagged for.

Defect 2 — transcription. The record's opening sentence: "an r=5 yoyo hit count of 59 for
AES against a null expectation of 4.0 (BATCH-002 A1, **15.63x**)". 59/4.0 = 14.75, and
EV-AES-048545 line 44 reads "R3-A1 AES W=59 excess **14.75x**". The record's own control
list demands "Pin the probe from the committed … sources - not from memory and not from the
goal record's prose"; the same discipline must be applied to the counts.

### IDEA-20260808-24c61b — PARTIAL-OVERLAP (HA-1 mis-stated)

Claim A (the closure) is sound and I could not break it: HGJ/BCJ's filter needs the target
residue k mod M; guessing it costs M and the filter saves M, so the family collapses to
BSGS; and Wagner-style multi-level constraints need a proper quotient of ⟨P⟩, which a prime
order does not have. The forward guidance (three named missing ingredients) satisfies
`docs/inventor-protocol.md` §4, so this is a legitimate closure and not a fatigue report.

HA-1 is wrong and, more importantly, is not a heuristic. It states R "is concentrated around
its mean **3^m/B^m** * (normalisation)". Exact enumeration:

```
B=4 m=3: distinct targets 232, bulk targets 63: min R 9, max R 9, mean R 9.000   (3^{m-1}=9)   record's 3^m/B^m = 0.422
B=4 m=4: bulk targets 255: min R 27, max R 27, mean 27.000                       (3^{m-1}=27)  record's = 0.316
B=8 m=3: bulk targets 511: min R 9, max R 9, mean 9.000                                        record's = 0.053
B=8 m=4: bulk targets 4095: min R 27, max R 27, mean 27.000                                    record's = 0.020
```
The true count on the bulk is **exactly 3^{m−1} with zero variance** in 4/4 cells; the
stated mean is < 1 for every B > 3 and is off by the factor B^m/3 (1365 at B=8, m=4). The
"(normalisation)" hedge is carrying the entire claim. And since the record's own
`rigorous_ingredient` correctly calls it "a finite combinatorial identity", HA-1 should be
deleted as a heuristic and replaced by the identity R = 3^{m−1} on the bulk, with the
boundary handled separately (that is where the record's `tail_checks` on min R actually
bites).

No corpus duplicate found: I confirmed the record's grep claim — no ECDLP-as-knapsack record
exists in EXISTING_PROPOSALS.txt, and the batch's only other representation-technique record
(IDEA-20260808-a3bcf0) is ISD at Classic McEliece, a different object.

### IDEA-20260808-0eb075 — PARTIAL-OVERLAP (no method ceiling)

The algebra is right: I re-derived that E_x[f(x)f(x+δ)] = ½Σ_i cos(2π⟨w_i,δ⟩/q) for distinct
±w_i, so the record's ρ(δ) = (1/N)Σ_i cos(2π⟨w_i,δ⟩/q) is exact, and the sign of the
correction (correlated field ⇒ lower max ⇒ lower noise floor ⇒ attacker-favourable) is right.

Objection 1 — the record has **no `method_ceiling`** entry, which my contract requires
before implementation. Its ceiling is computable in closed form now: the required number of
dual vectors satisfies N·bias ≈ √(N ln M), i.e. N ∝ ln M, so replacing M = q^{k_fft} by
N_eff bounds the achievable reduction in N by the ratio ln N_eff / (k_fft ln q). Since
N_eff ≥ N by construction (the Fourier support has N frequencies), the largest possible gain
is a factor 1 − ln(q^{k_fft}/N_eff)/(k_fft ln q), which the record can evaluate at the
MATZOV parameters before spending a producer slot. If that number is under a few percent,
Δβ is under 1 and the lane closes at zero compute.

Objection 2 — HA-1 is stated "uniformly for **N ≪ q^{k_fft}**", and the record never checks
whether the deployed MATZOV point satisfies it. If N ≳ q^{k_fft} at ML-KEM-768, the
Fourier support is essentially the whole group, ρ(δ) → δ_0, N_eff → q^{k_fft} and the
mechanism is void exactly where it is supposed to matter. The record's own `controls` list
the N-sweep decay but names the toy-scale smoothness bias as the leading extrapolation risk;
the regime condition is the prior gate.

Objection 3 — the `dominated_by` field reads "n/a (no attack-cost result claimed)" followed
by a list of records checked. Since the deliverable is a signed Δβ against the MATZOV cost,
the memory axis must appear: a reduction in required N is also a reduction in the dual store,
so the correct entry is a two-axis comparison against the KN-FIND-014/015/016 pinned cost,
not "n/a".

---

## NOVEL verdicts — what I checked

**IDEA-20260808-ceca08.** I re-derived n_1 = gcd(A−1, m), m = f/f_E, from the Smith normal
form of multiplication by π−1 = (A−1) + m·(f_E ω) on O = Z ⊕ Z f_E ω (the first invariant
factor is the gcd of the four matrix entries, and m divides the other two). I then verified
the exact half on 125 random toy curves over 21 primes:

```
curves tested: 125
violations of n1^2 | #E        : 0
violations of n1 | p-1         : 0
violations of n1 | gcd(A-1,f)  : 0
violations of n1 | cofactor    : 0
cases where n1 < gcd(A-1,f) (f_E>1, curve above the floor): 46
n1 distribution: {1: 105, 2: 18, 4: 1, 5: 1}
```
The 46 strict cases are the identity's content (gcd(A−1,f) over-estimates n_1 exactly when
f_E > 1). One caveat: the record says the leak is "confined to ell = 2"; an n_1 = 5 was
observed, so the correct statement is "confined to the primes dividing the cofactor", which
is ℓ=2 only for 2-power cofactors. Also note that "curves at the floor have cyclic group
structure" and the ℓ-Sylow/level relation are classical volcano-navigation facts; the record
flags this as "[recall-uncertain on attribution]" and external novelty is unadjudicated here.

**IDEA-20260808-c4b462.** I re-derived every exponent: selected pair lists L²/M = N^{1/3};
cross-pairs N^{2/3}; two independent selectors ⇒ a summing 4-tuple survives with probability
M^{−2} = N^{−2/3}, giving N^{1/3}·N^{−2/3} = N^{−1/3+γ} matches per root; total
N^{2/3−γ}; memory N^{1/3}; γ = 0 reproduces T·S = N BSGS exactly; γ > 1/6 is the correct
sub-rho gate; the ceiling γ = 1/3 follows from one M-valued condition carrying log M bits.
All nine numbers in each row of `concrete_cost_table` reproduce (128-bit: 64/64/42.7/85.3/
85.3/64/59.7/42.7). Scalar-list construction, bucket build, sorting and the affine
self-reduction are all charged in `hidden_overhead_disclosure`. `dominated_by` is a real
conditional audit with a frontier row list, not a formality. This is the only record in the
slice whose cost model I could not find a hole in.

**IDEA-20260808-b5b9ca.** I re-derived STEP 1 (Trd(α)=0 ⇒ α² = −Nrd(α); Nrd = p·deg φ ⇒
Z[α] has discriminant −4p·deg φ) and STEP 2 (h(−4pd) ~ √(pd), so Σ_{d≤T} h(−4pd)/(p/12) ~
8T^{3/2}/√p, and at T ~ p^{1/3} this is Θ(1), consistent with δ_E ≤ (p/2)^{1/3} being the
threshold). Objection: branch (B)'s prior of 0.2 is generous. The gap between |D| ~ p^{4/3}
and the recalled |D| ≥ p^{2+ε} is a factor p^{2/3}; closing it is not a bibliographic
correction but a major theorem in the level-aspect-coupled-to-discriminant-aspect regime.
The record's own `honest_prior_of_survival` line already identifies the ramification of p in
every Q(√(−pd)) as "the record's real risk … a mathematical one, not a bibliographic one";
the record's *headline* should say so too, since it currently sells the deciding step as
"one bibliographic fact". Also, prediction 2's Poisson null for the per-curve CM
multiplicity is a modelling choice, not forced — Eichler's formula with the ramified local
factor at p is the right null and should be used instead of Poisson.

---

## What I actually checked

**Records read in full:** all 19 YAMLs under `/tmp/wt-ideas-100/ledger/proposals/`.

**Corpus / knowledge files read:** `agents/red-team.md`;
`knowledge/techniques/KN-TECH-057.md` (in full), `KN-TECH-035.md`, `KN-TECH-044.md` (heads);
`knowledge/findings/KN-FIND-720727.md`, `KN-FIND-860118.md`, `KN-FIND-006.md`,
`KN-FIND-a8990a.md` (heads); `ledger/proposals/IDEA-20260805-bd8339.yaml` (grepped in full
for the repeated-factor treatment); `IDEA-20260808-c959c7.yaml` (head);
`ledger/evidence/EV-AES-048545.yaml`, `EV-AES-e4c091.yaml`, `EV-AES-dec938.yaml`,
`EV-AES-d81acf.yaml` (scoped greps for counts and exposures); `EXISTING_PROPOSALS.txt`,
`EXISTING_HYPOTHESES.txt`, `CATALOGUE_TITLES.txt`, `REJECTED_TITLES.txt`,
`KNOWLEDGE_BARRIERS.txt`; the full question-grouping of all 126 records in the 2026-08-08
batch (to find intra-batch collisions).

**Brief's three unchecked barrier records:**
- `KN-TECH-057` — relevant only to IDEA-20260808-70243a in this slice. That record *does*
  cite KN-TECH-057 by ID in `dominated_by`, but does not use it: I supply the missing
  full-cost number (p^{4/9} under KN-TECH-035's τ = S^{1/3}) above.
- `KN-FIND-720727` (ML-DSA fault injection outside the formal model) — no record in slice2
  touches ML-DSA; no overlap.
- `KN-FIND-860118` (uncorroborated quantum-break claim / determinant-ideal closure) — the
  only ML-KEM record here (0eb075) is a classical dual-attack cost correction; no overlap.
- `KN-FIND-a8990a` — adjacent to a3f7c1's arity-m decomposition and not cited; noted.

**Computations run** (scripts in
`/private/tmp/claude-501/-Volumes-SSD990-research/470d7176-1bcc-451c-9995-1ef445a7ca69/scratchpad/rs/`):
1. `chk_a3f7c1b.py` — guided vs exhaustive relation yield on real toy curves, 12 cells.
2. `chk_d935d1.py` — r_min and stratum exponent for k = n over a grid, plus the O(√k) bound to k ≤ 20000.
3. `chk_9f9ed8.py` — exhaustive construction of duplicated RM(1,7) and all 32131 pairwise support intersections.
4. `chk_9f9ed8b.py` / `chk_9f9ed8c.py` — exact-rational Bonferroni terms, bracket width, and Table-11 fixture under three event readings.
5. `chk_0b3072b.py` — determinantal representation classes of a fixed smooth plane cubic at q = 5,7,11,13 (linear-reduced enumeration + centraliser division), against #C(F_q).
6. `dick.py` — CEP/Dickman smoothness exponents for 70243a's index at log2 p ∈ {256,…,1024}.
7. `chk_95a21c.py` — block-count arithmetic for SHAKE128/SHAKE256/SHA-256 rates.
8. `chk_cb0828.py` — exact truncated-χ² acceptance rate and conditional second moment at n = 128…2048; fatigue margins.
9. `chk_778f82.py` — the (n−o)(m+2) vs 4n table at seven parameter sets and the vOW-vs-guessing comparison.
10. `chk_24c61b.py` — exact enumeration of enlarged-alphabet digit representations at (B,m) ∈ {4,8}×{3,4}.
11. `chk_ceca08.py` — group structure, t, D, f, D_0, A, gcd(A−1,f) on 125 toy curves.
12. `chk_632866.py` — exact ρ vs the Stirling form at four (n,w) and four d.
13. `chk_d3eb2a.py` / `chk_d3eb2a2.py` — pairwise-predicate rejection rate with planted ground truth, and the oracle-optimal-threshold version.

**What I could NOT verify, and what would settle it:**
- All external novelty. Web search failed on every attempt. In particular: whether the
  RM-Bonferroni bracket (9f9ed8), the plain-SD↔d-split permutation reduction (632866), the
  group-structure volcano-level leak (ceca08 — Miret et al.-style ℓ-Sylow/level results are
  what I would look for), the FALCON conditional-width observation (cb0828), and Beauville's
  determinantal-representation classification (0b3072, which my computation confirms
  empirically) are already published. Settled by one literature session.
- 4c309d's 4-round fixture value (1 vs 4) — settled by reading the final-round MixColumns
  convention in the pinned FIPS-197 harness.
- 348896's prediction 3 vs `survival_depth` — settled by one line of the SNOVA spec (is T
  A-linear or only F_q-linear?).
- 0eb075's HA-1 regime (N vs q^{k_fft} at deployed MATZOV parameters) — settled from
  KN-FIND-014/015/016's pinned cost model without any new run.
- 95a21c's exact FAEST v2.0 transcript length — my table is parameterised by transcript size,
  so the refutation holds from the record's own "multiple kilobytes" premise regardless; the
  exact L needs the spec.
- d07cd4's step (1): whether QR-UOV's public forms actually factor through A. Settled by the
  spec read that both d07cd4 and IDEA-20260805-bb9f73 already list as required.

**Duplication scan result:** no exact duplicate found inside slice2 or against the wider
2026-08-08 batch. RQ-MCEQ-fcb504's two records (0b3072, d935d1) are deliberately
complementary and cross-cite correctly. RQ-MCE-e65b3c's five records are Classic McEliece,
a different problem. The one real overlap is d07cd4 vs IDEA-20260805-bd8339, documented
above with the exact lines.
