# EXP-JPR-402649 / STATIC-001 — derivation package (zero runs)

Hypothesis H-JPR-5e33d6, question RQ-ECDLP-160d89, task TASK-20260902-19eacf,
batch BATCH-67be49. Claim tier: **derivation** (docs/claims-and-verification.md,
refutation-artifact item 2). Nothing here is "proved"; every statement is a
checkable written argument. Zero runs, no code, no curve, no sampled point.
The N = 23 fixture in section 0.4 is a hand enumeration.

## Conventions

- G = <P>, |G| = N an odd prime; log_P : G -> Z/N the discrete logarithm,
  a group isomorphism. Characters chi_xi(R) = e(xi * log_P(R) / N),
  e(z) = exp(2 pi i z). For h : G -> C, hhat(xi) = E_R h(R) conj(chi_xi(R)).
- An order key is nu : G -> Z/N. It is a *cyclic order* when injective, hence
  a bijection (|G| = N). f = nu/N in R/Z, g = e(f).
- I_s = {s, s+1, ..., s+w-1} in Z/N is the cyclic interval of width w with
  start s. A nu-interval of width w is nu^{-1}(I_s). For 1 <= w <= N-1 the
  N intervals I_s are pairwise distinct: s is the unique u in I_s with
  u-1 not in I_s.
- D = nu^{-1}(J), J = I_j of width w; emission window J' = I_{j'} of width w'.
  Row window of R: W_R = {S : nu(R) + nu(S) in J'} = nu^{-1}(I_{j' - nu(R)}).
- Population soundness: eta_R = |W_R \ (D - R)| / |W_R|, and the join is
  (1-eta)-sound when sum_R eta_R |W_R| <= eta * sum_R |W_R|. For bijective nu
  every |W_R| = w', so this reads (1/N) sum_R eta_R <= eta.
- Intersection formula (used repeatedly). For 1 <= w <= (N-1)/2 and starts
  a, b with cyclic distance d = min(|a-b|, N-|a-b|):
  |I_a cap I_b| = max(0, w - d). Proof: I_{a+d} cap I_a = {a+d, ..., a+w-1}
  when d <= w-1 (w - d elements); a wrap-around contribution would need
  d + m >= N for some m <= w-1, impossible as d + m <= 2w - 2 <= N - 3; when
  d >= w the direct part is empty and the wrap-around part has w - (N-d)
  elements if N - d <= w - 1, else none; both parts cannot be nonempty
  since that needs N <= 2w - 2. Hence |I_a Delta I_b| = 2 min(d, w).

---

# Stage 0 — T1 (order rigidity) and the three blocking controls

## 0.1 Theorem T1 (derivation tier)

**T1.** Let N be an odd prime, nu : G -> Z/N injective, and D subset G with
2 <= |D| = w <= (N-1)/2 such that every translate D - T (T in G) is a
nu-interval. Then there exist a in (Z/N)^* and c in Z/N with
nu = a * log_P + c, and D = nu^{-1}(I_j) is a log-interval: log_P(D) is an
arithmetic progression in Z/N with common difference a^{-1}, equivalently a
genuine interval in the coordinate log_{P'} with P' = [a^{-1}]P. The witness
(a, c) depends on (nu, D) only. (The "plus-or-minus" of the hypothesis
statement is absorbed: a ranges over all of (Z/N)^*.)

**Step 1 (pairwise-distinct translates).** If D - T = D - T' with T != T',
then D + U = D for U = T - T' != 0. N prime implies <U> = G, so D is a union
of <U>-orbits, i.e. D in {emptyset, G}, contradicting 2 <= |D| <= (N-1)/2.
Hence the N translates are pairwise distinct. *Hypothesis used: N prime.*

**Step 2 (the translates exhaust the interval system).** Each D - T is a
nu-interval of width w. There are exactly N width-w nu-intervals (nu is a
bijection, and the N intervals I_s are distinct). N distinct translates
inside a set of N intervals: the translates ARE the width-w nu-intervals.
Define the start map s : G -> Z/N by D - T = nu^{-1}(I_{s(T)}); s is a
bijection. Write E_u := nu^{-1}(I_u). *Hypothesis used: nu injective.*

**Step 3 (adjacency).** By the intersection formula (needs 2 <= w <=
(N-1)/2), |E_a cap E_b| = |I_a cap I_b| = w - 1 iff b = a +/- 1. Translation
preserves intersection sizes: |(A - U) cap (B - U)| = |A cap B|.

**Step 4 (dihedral embedding, in full).** Let C_N be the graph on Z/N with
a ~ b iff |E_a cap E_b| = w - 1, i.e. b = a +/- 1: the N-cycle. For U in G
define phi_U : Z/N -> Z/N by phi_U(u) = the start of E_u - U, i.e.
phi_U(s(T)) = s(T + U). Well defined since every E_u is some D - T (Step 2)
and E_u - U = D - (T + U) is again a nu-interval. phi_U is a bijection
(inverse phi_{-U}) and preserves adjacency both ways: a ~ b iff
|E_a cap E_b| = w-1 iff |(E_a - U) cap (E_b - U)| = w-1 iff phi_U(a) ~
phi_U(b). So phi_U in Aut(C_N) = D_N (dihedral, order 2N; N >= 3).
Homomorphism: phi_{U+U'}(start E) = start(E - U - U') = phi_{U'}(start(E - U))
= phi_{U'}(phi_U(start E)). Injective: phi_U = id means D - T - U = D - T for
all T, i.e. D - U = D, so U = 0 by Step 1. Hence G embeds in D_N as a
subgroup of order N.

**Step 5 (rotations only).** D_N = {u -> u + k} cup {u -> -u + k}; every
reflection has order 2. A subgroup of odd order N contains no element of
order 2 (Lagrange), so the image of G lies in the rotation subgroup, which
has order N; therefore the image IS the rotation subgroup and
phi_U(u) = u + rho(U) with rho : G -> Z/N an injective homomorphism (a
bijection). Then s(T + U) = s(T) + rho(U), so s(T) = s(0) + rho(T), and
rho(T) = rho(P) * log_P(T) with a_0 := rho(P) != 0. *Hypothesis used: N odd.*

**Step 6 (recovering nu from the start map).** Let U_1 := rho^{-1}(1), so
E_{u+1} = E_u - U_1. For any u, nu^{-1}(u) is the unique element of
E_u \ E_{u+1} (since I_u \ I_{u+1} = {u}, w <= N-1). Apply to u = s(T):
nu^{-1}(s(T)) is the unique element of (D - T) \ (D - T - U_1)
= (D \ (D - U_1)) - T = {d_0} - T, where d_0 is the unique element of
D \ (D - U_1). Hence nu(d_0 - T) = s(T) = s(0) + a_0 log_P(T) for all T.
Put R = d_0 - T: log_P(T) = log_P(d_0) - log_P(R), so
nu(R) = s(0) + a_0 log_P(d_0) - a_0 log_P(R). Thus nu = a log_P + c with
a = -a_0 in (Z/N)^* and c = s(0) + a_0 log_P(d_0). D = nu^{-1}(I_j) then has
log_P(D) = a^{-1}(I_j - c), an arithmetic progression of difference a^{-1}.
No hypothesis on how nu is computed was used anywhere. QED (derivation).

**Boundary widths.** w = 1: every singleton is a nu-interval for every
injective nu, so the conclusion fails; excluded by 2 <= |D|. w > (N-1)/2:
G \ nu^{-1}(I_s) = nu^{-1}(I_{s+w}) is a nu-interval of width N - w and
complementation commutes with translation, so for 2 <= |D| <= N-2 apply T1
to whichever of D, G \ D has size <= (N-1)/2 (N odd, no tie at N/2). The
conclusion nu = a log_P + c is unchanged and the complement of a
log-interval is a log-interval. The extension flagged "to be confirmed" in
H-JPR-5e33d6 is therefore confirmed at derivation tier. For N = 3 the range
2 <= |D| <= 1 is empty and T1 is vacuous.

## 0.2 CTRL-COMPOSITE-COSET (blocking; forced: FAIL at a named step)

Object: Z/(de) with d, e >= 2, H = the order-e subgroup dZ/(de), D = a + H,
nu = "sort by coset, then arbitrarily within the coset": nu(x) =
e*(x mod d) + pi_{x mod d}(x) with each pi_r a bijection of the coset onto
{0, ..., e-1}. Every translate D - T = (a - T) + H is a coset, and
nu(coset) is an interval of width e, so the hypothesis "every translate is
a nu-interval" HOLDS.

Applying T1 step by step:
- Hypothesis "N odd prime": FAILS (N = de composite).
- Step 1 (pairwise-distinct translates): FAILS. D - T = D - T' iff
  T - T' in H, and |H| = e > 1. The proof of Step 1 invoked "<U> = G", which
  is false for U in H \ {0}: the stabilizer of D is H, not {0}. Only d of the
  N translates are distinct. **This is the named failing step.**
- Step 2 consequently FAILS: the d distinct translates are only the d
  "aligned" width-e intervals I_{e r}, not all N of them; s is not a
  bijection.
- Step 4 consequently FAILS: U -> phi_U has kernel H; the dihedral map is
  not injective; G does not embed in D_N.
- Conclusion: not reached. Indeed nu is arbitrary inside each coset, so nu is
  not affine in any generator, and Z/(de) has no log_P in the sense of T1.

Hand illustration (not a run): d = 3, e = 2, Z/6, H = {0, 3}, D = {0, 3},
nu(0)=0, nu(3)=1, nu(1)=2, nu(4)=3, nu(2)=4, nu(5)=5. Translates:
D - 0 = D - 3 = {0,3} = nu^{-1}{0,1}; D - 1 = D - 4 = {2,5} = nu^{-1}{4,5};
D - 2 = D - 5 = {1,4} = nu^{-1}{2,3}. Three distinct translates among six
width-2 intervals. Disposition: **as forced** (F1 not triggered).
Range note: for d = 2 the range hypothesis 2 <= e <= (N-1)/2 also fails
(e > (2e-1)/2); for d >= 3 it holds and Step 1 is the sole first failure.

## 0.3 CTRL-XOR-LEX (blocking; forced: SILENT; join-core rows only)

Object: G = F_2^{3m} under XOR, nu = lexicographic (bit string read as an
integer in Z/2^{3m}), injective. D = prefix subspace {v : top k bits 0},
1 <= k < 3m; D + T = {v : top k bits equal those of T}, a dyadic interval of
width 2^{3m-k} in nu. Hypothesis "every translate is a nu-interval": HOLDS.

Join-core rows scored (JPR-REV-2):
- Row "prime order": FAILS (N = 2^{3m}; also N is even, so Step 5's odd-order
  argument is unavailable: every non-identity element has order 2).
- Row "distinct translates" (Step 1): FAILS. D + T = D + T' iff T + T' in D;
  the stabilizer of D is D itself (a subgroup of size 2^{3m-k} > 1). Only
  2^k distinct translates exist; Step 2's exhaustion and Step 4's injectivity
  fail with it. **Named failing step: Step 1 (stabilizer of D is D).**
- Row "additivity" (T2): FALSE. XOR is not addition of ranks: for R = S != 0,
  nu(R xor S) = nu(0) = 0 while nu(R) + nu(S) = 2 nu(R) != 0 mod 2^{3m}
  unless nu(R) = 2^{3m-1}. The two-pointer join as defined (rank sums in J')
  is not the sound join on this object; the sound and complete join there is
  an equality join on the k-bit prefix, a different primitive.
No ECDLP-only row (source replay, scalar recovery) is scored. T1 is SILENT:
no step reaches a log order, and none exists. Disposition: **as forced**.

## 0.4 CTRL-ZN-IDENTITY (blocking; forced: rho = -id) and the N = 23 fixture

Object: G = Z/N, P = 1, log_P = id, nu = id, D = I_j with 2 <= w <= (N-1)/2.
D - T = I_{j-T}, so s(T) = j - T. Steps 1-4 hold. Step 5: phi_U(u) = u - U,
rho(U) = -U, a_0 = rho(1) = -1, an injective homomorphism: **rho = -id**.
Step 6: U_1 = rho^{-1}(1) = -1, D - U_1 = I_{j+1}, d_0 = j, c = s(0) + a_0 j
= j - j = 0, a = -a_0 = 1: nu = log_P = id. As forced.
T2 on this object: with J' = J (w' = w), nu(R) + nu(S) in J iff R + S in D:
eta = eta' = 0, defect 0 on every pair. T3: g = chi_1, ghat(1) = 1, gamma = 0,
xi_0 = 1 unique; the cascade returns x = (xi_0 x)/xi_0 = x, which was known:
vacuous, as forced.

**Hand fixture N = 23, w = 5** (paper enumeration; not a run). Note
2w = 10 <= 22 = N - 1. The 23 width-5 cyclic intervals I_s:

```
I_0 ={0,1,2,3,4}     I_1 ={1,2,3,4,5}     I_2 ={2,3,4,5,6}     I_3 ={3,4,5,6,7}
I_4 ={4,5,6,7,8}     I_5 ={5,6,7,8,9}     I_6 ={6,7,8,9,10}    I_7 ={7,8,9,10,11}
I_8 ={8,9,10,11,12}  I_9 ={9,10,11,12,13} I_10={10,11,12,13,14} I_11={11,12,13,14,15}
I_12={12,13,14,15,16} I_13={13,14,15,16,17} I_14={14,15,16,17,18} I_15={15,16,17,18,19}
I_16={16,17,18,19,20} I_17={17,18,19,20,21} I_18={18,19,20,21,22} I_19={19,20,21,22,0}
I_20={20,21,22,0,1}  I_21={21,22,0,1,2}   I_22={22,0,1,2,3}
```

Translates of D = I_0 = {0,1,2,3,4} by -T, T = 0..22, each reduced mod 23:

```
T=0 : {0,1,2,3,4}      = I_0     T=12: {11,12,13,14,15} = I_11
T=1 : {22,0,1,2,3}     = I_22    T=13: {10,11,12,13,14} = I_10
T=2 : {21,22,0,1,2}    = I_21    T=14: {9,10,11,12,13}  = I_9
T=3 : {20,21,22,0,1}   = I_20    T=15: {8,9,10,11,12}   = I_8
T=4 : {19,20,21,22,0}  = I_19    T=16: {7,8,9,10,11}    = I_7
T=5 : {18,19,20,21,22} = I_18    T=17: {6,7,8,9,10}     = I_6
T=6 : {17,18,19,20,21} = I_17    T=18: {5,6,7,8,9}      = I_5
T=7 : {16,17,18,19,20} = I_16    T=19: {4,5,6,7,8}      = I_4
T=8 : {15,16,17,18,19} = I_15    T=20: {3,4,5,6,7}      = I_3
T=9 : {14,15,16,17,18} = I_14    T=21: {2,3,4,5,6}      = I_2
T=10: {13,14,15,16,17} = I_13    T=22: {1,2,3,4,5}      = I_1
T=11: {12,13,14,15,16} = I_12
```

Coincidence as sets: the 23 translates are {I_0, I_22, I_21, ..., I_1}, i.e.
every one of the 23 intervals exactly once. Start map: s(T) = -T mod 23
(s(0)=0, s(1)=22, s(5)=18, s(12)=11, s(22)=1). Rotation: translating any
interval I_u by -T gives I_{u-T}, so phi_T(u) = u - T is rotation by exactly
-T, rho(T) = -T. Adjacency check from the table: |I_0 cap I_1| = 4,
|I_0 cap I_2| = 3, |I_0 cap I_4| = 1, |I_0 cap I_5| = 0, |I_0 cap I_18| = 0,
|I_0 cap I_19| = 1, |I_0 cap I_22| = 4: consistent with w - min(d, N-d).

## 0.5 NULL-1 (random cyclic order) and NULL-2 (x-coordinate order)

**NULL-1.** nu a uniformly random bijection G -> Z/N. For an emitted pair,
R + S is a fixed element and D = nu^{-1}(J) is a random w-set, so
P[R + S in D] = w/N up to the three ranks already conditioned on: soundness
rate w/N = 1/L at w = N^{2/3}. Fourier statistic: for xi != 0,
E_nu |ghat(xi)|^2 = (1/N^2)[N + sum_{R != R'} E e((nu(R) - nu(R'))/N)
chi_xi(R' - R)] and E e((u - u')/N) over distinct random ranks equals
-1/(N-1), giving E_nu |ghat(xi)|^2 = 1/(N-1); ghat(0) = 0 exactly. So the
statistic is O(N^{-1/2}) at every frequency in root-mean-square (predicted;
symbolic). COST STATEMENT, verbatim from JPR-REV-4: a join sound only at
rate 1/L is the literal independent pair coin, whose corrected cost is
**EXPECTED TIME N** (N^{2/3} pair enumeration per fresh attempt times
N^{1/3} retries), NOT the optimistic figure. T2 additivity holds with
probability w/N per pair; T3 predicts no heavy coefficient.

**NULL-2.** The x-coordinate integer order of K-EC-XINTERVAL-1
(IDEA-20260823-cab6c6) as a two-pointer key. T1 is NOT applied: x(-R) = x(R)
makes nu non-injective (invalidation rule 1). T2 and T3 apply and predict,
as for NULL-1, soundness rate 1/L, no heavy coefficient (the M4 computation
is FUTURE and excluded), and **EXPECTED TIME N** by the same JPR-REV-4
pair-coin accounting. This is the record's statement that K-EC-XINTERVAL-1
cannot be two-pointer joined.

## 0.6 Pareto rows (controls only; JPR-REV-3)

PARETO-RHO: (time, memory) exponents (1/2, 0). PARETO-BSGS: (1/2, 1/2).
Stated as CONTROL ROWS ONLY. No attack is mounted by this package, so its
realized position is dominated trivially by both; the conditional exponent 0
of T3 is a conditional collapse, not a Pareto position. No domination is
asserted in either direction on any axis.

**Stage 0 gate: all three blocking controls took their forced disposition.
No stopping rule fired. Proceed to Stage 1.**

---

# Stage 1 — T2 with explicit constants, the threshold tau_0, HEUR-001

Throughout Stage 1 nu is a bijection (cyclic order) unless stated; the
tie-tolerant variant is in 1.6. Hypotheses: population (1-eta)-soundness,
i.e. avg_R eta_R <= eta; size matching w' >= (1 - eta') w; 2 <= w, w'
<= (N-1)/2 where needed for the intersection formula.

## 1.1 Step A — soundness on a row

For each R, |W_R| = w', |D - R| = w, |W_R \ (D - R)| = eta_R w', so
|W_R cap (D - R)| = (1 - eta_R) w' and |(D - R) \ W_R| = w - (1-eta_R) w'.
Symmetric difference:
  Delta_R := |(D - R) Delta W_R| = w - w' + 2 eta_R w'.                (A)
Averaging |W_R cap (D-R)| <= w over R: (1 - avg eta_R) w' <= w, hence
  w' <= w / (1 - eta).                                                  (A')

## 1.2 Step B — size matching

From w' >= (1 - eta') w: w - w' <= eta' w. With (A'):
  Delta_R <= (eta' + 2 eta_R / (1 - eta)) w =: a_R w,                   (B)
  abar := avg_R a_R <= eta' + 2 eta/(1 - eta) <= 2 (eta + eta') / (1 - eta).
(If w' > w the term w - w' is negative and (B) still holds.)

## 1.3 Markov and the union bound (the constant in delta)

For any K > 0, Markov on a_R >= 0 gives
  |{R : a_R > K abar}| / N <= 1/K =: delta.                              (M)
Call R *good* when a_R <= K abar. For (R, R') uniform in G x G, each of
R, R', R + R' is uniform, so the union bound gives
  P[some row among R, R', R + R' is bad] <= 3 delta.                    (U)
This is the 3*delta of the hypothesis statement. Note the structure of (M):
the row defect on good rows is K * abar * w, and delta = 1/K. The product
(row-defect constant) x delta equals abar w, fixed by the data; a first-moment
argument cannot make both C and c_1 absolute constants simultaneously (see
1.5, where this is what fixes tau_0).

## 1.4 Step C — the translate-comparison step: NOT AVAILABLE as sketched

What IS derived. Write E_u = nu^{-1}(I_u) (width w') and s(R) = j' - nu(R),
so W_R = E_{s(R)}. For good rows R and R + R':
  |(E_{s(R)} - R') Delta E_{s(R+R')}|
    <= |(D - R - R') Delta (E_{s(R)} - R')| + |(D - R - R') Delta E_{s(R+R')}|
    = Delta_R + Delta_{R+R'} <= 2 K abar w.                             (C1)
(translation preserves symmetric differences). (C1) holds on all but a
2*delta fraction of pairs (3*delta with the third row charged). It is an
*approximate translation-invariance of the row-interval system*: every
translate of D is within a_T w of a nu-interval whose start j' - nu(T) is an
exact affine function of nu(T). This is the approximate form of T1's
hypothesis.

What is NOT derived. The sketch continues: "two width-w' intervals whose
symmetric difference is O((eta+eta')w) have starts differing by
O((eta+eta')w), so nu(R+R') = nu(R) + nu(R') + O((eta+eta')w)". The
conversion symdiff -> start distance is valid for two nu-INTERVALS
(|E_a Delta E_b| = 2 min(dist(a,b), w') by the intersection formula, so
dist(a,b) <= symdiff/2 whenever symdiff < 2w'). But E_{s(R)} - R' is a
TRANSLATE of a nu-interval, and for a general nu a translate of a
nu-interval is not a nu-interval and has no start. Assigning it the start
s(R) - nu(R') + const asserts that translation by R' shifts every rank in
E_{s(R)} by about nu(R') - const, which is the approximate additivity being
proved. The step as written is circular. **Verdict: the translate-comparison
step cannot be written in full from soundness and size matching alone.**

Missing lemma, named for review (internal obligation, not external):
  (TC) Stability of T1: if every translate D - T is within a_T w of a
  nu-interval with start affine in nu(T), then nu is approximately affine in
  log_P on most of G with defect O(max a_T * w) in Z/N.
A naive route (compare the images under translation by U of two row windows
at rank distance k <= w' via the intersection formula; obtain
|nu(T2 + U) - nu(T + U)| = k +/- 4 K abar w up to SIGN; fix the sign by
consistency on triples; chain windows around the cycle) yields at best a
global drift O((N/w') K abar w) = O((eta + eta') N), i.e. precision
O(eta + eta') in R/Z rather than O(w/N), with the rotation/reflection
dichotomy not excluded at that precision. Not derived here; recorded as the
identified gap.

**The O(w) fallback (declared and derived, scope stated).** From window
membership alone: for an emitted sound pair (R, S), nu(S) in I_{j' - nu(R)}
and nu(R + S) in I_j, hence
  nu(R + S) - nu(R) - nu(S) - k_0 in [-(w'-1), w-1],  k_0 := j - j',     (FB)
so || f(R+S) - f(R) - f(S) - k_0/N ||_{R/Z} <= C_fb * w/N with
  C_fb = max(1, w'/w) <= 1/(1 - eta)  (<= 6/5 for eta <= 1/6).
SCOPE: (FB) holds on the emitted sound pairs only, a (1 - eta) w'/N fraction
of G x G, NOT on a 1 - 3 delta fraction. The extension to almost all pairs is
exactly the missing lemma (TC). This differs from the contract's expectation
that the fallback "still gives additive precision N^{-1/3+o(1)}" on most
pairs; that expectation is not borne out by the derivation and is recorded
as an observation, not repaired.

## 1.5 Unexpected observation — an unconditional weak Fourier consequence

Not requested by the contract; recorded under AGENTS.md rule 8. Let
A(R,S) = 1[nu(R) + nu(S) in J'], B(R,S) = 1[R + S in D]. Soundness:
E[AB] >= (1 - eta) w'/N. Expand A over Z/N ranks and B over G characters:
  A(R,S) = sum_m ahat(m) g_m(R) g_m(S),  g_m := e(m nu/N),
    ahat(m) = (1/N) sum_{u in J'} e(-mu/N), |ahat(m)| <= min(w'/N, 1/(2|m|)),
  B(R,S) = sum_xi bhat(xi) chi_xi(R) chi_xi(S),  sum_xi |bhat(xi)|^2 = w/N.
Then E[AB] = sum_{m, xi} ahat(m) bhat(xi) c(m,xi)^2 with
c(m,xi) := E_R g_m(R) chi_xi(R) = (g_m)hat(-xi), and sum_xi |c(m,xi)|^2 = 1
for each m (Parseval). Cauchy-Schwarz:
  |sum_xi bhat(xi) c(m,xi)^2| <= sqrt(w/N) (sum_xi |c|^4)^{1/2}
                               <= sqrt(w/N) max_xi |c(m,xi)|.
The m = 0 term equals w w'/N^2. With S_1 := sum_{m != 0} |ahat(m)|
<= 2 + ln w' (split at |m| = N/(2w'); sin(pi x) >= 2x on [0,1/2]):
  max_{m != 0, xi} |(g_m)hat(xi)| >= (w'/w) sqrt(w/N) (1 - eta - w/N)/(2 + ln w').
Since c(m, 0) = E_R e(m nu(R)/N) = 0 for m != 0 (nu bijective), the maximiser
has xi != 0. At w = N^{2/3}, w' >= (1 - eta') w:
  some dilate e(m nu/N), m != 0, has a coefficient >= (1-eta')(1-eta-o(1))
  N^{-1/6} / (2 + (2/3) ln N)                                          (U1)
UNCONDITIONALLY from soundness. Consequences, stated as observations only:
(a) it is a heavy coefficient of size N^{-1/6}/log N, not a constant; feeding
it to an SFT with cost poly(1/tau) would give cost N^{Theta(1)}, so (U1)
alone does not support the exponent-0 headline (relevant to M3, see report);
(b) it concerns e(m nu/N) for some m != 0, not necessarily m = 1, so it does
not by itself settle F3 as phrased; (c) NULL-1 is consistent with (U1): a
random order has all coefficients about N^{-1/2} and is not sound.

## 1.6 Ties

With ties, |W_R| varies, w' no longer equals |W_R|, and the width inequality
w' >= (1 - eta') w does not imply |W_R| >= (1 - eta')|D|. T2 in the stated
"ties allowed" form needs the size-matching hypothesis in set form,
|W_R| >= (1 - eta') |D| for all R; with that substitution (A)-(C1) and (FB)
go through with w' replaced by |W_R| row by row. Recorded as an observation
on the hypothesis statement; the injective case is unaffected.

## 1.7 The threshold tau_0 (M2): derivation chain

The frozen shape (specification.preregistered_prediction) is
  Re E[g(R+R') conj g(R) conj g(R')] >= (1 - 3 delta) cos(2 pi theta) - 3 delta,
with theta the additivity defect in R/Z on good pairs. Its premise is the
all-pairs form of T2, i.e. (TC). The chain below is therefore CONDITIONAL
on (TC) holding with the symdiff-to-start conversion of 1.4 (dist <=
symdiff/2); every constant is otherwise explicit.

1. Row and size steps: Delta_R <= a_R w, abar <= 2 t/(1 - eta), t := eta + eta'.
2. Markov: good rows a_R <= K abar off a delta = 1/K fraction; union: 3 delta.
3. (TC, conditional): start distance <= (Delta_R + Delta_{R+R'})/2 <= K abar w,
   valid only when K abar w < w' (non-vacuity of the conversion).
   Defect theta = K abar w / N.
4. Fourier (Stage 2, lemma (i)): on good pairs the summand has real part
   >= cos(2 pi theta), on bad pairs >= -1, giving the frozen shape and
   1 - gamma := (1 - 3 delta) cos(2 pi theta) - 3 delta.
5. Extraction and uniqueness (lemma (i)): need 1 - gamma > 1/sqrt 2.
6. Choice of K. delta = 1/K decreases and theta grows with K; theta <= w'/N
   is negligible at w' = Theta(N^{2/3}), so K is pushed to the non-vacuity
   limit K -> w'/(abar w), giving
     delta = abar w / w' <= abar/(1 - eta') <= 2 t / ((1-eta)(1-eta')) =: c_1 t,
     c_1 = 2/((1-eta)(1-eta')) >= 2;  theta -> w'/N <= w/((1-eta) N).
   Equivalently C = 2K/(1-eta) in the form defect = C t w/N, with
   C delta = 2/(1-eta): the two constants are tied, not both absolute.
7. Condition (asymptotic, cos -> 1): 6 delta < 1 - 1/sqrt 2 = 0.292893.
   With (1-eta)(1-eta') >= 1 - t: 12 t < 0.292893 (1 - t), so
     tau_0 = 0.292893 / 12.292893 = 0.023826 ~ 1/42.0.
   Finite N correction: replace 0.292893 by 0.292893 - (1 - 3 delta)
   (1 - cos(2 pi w'/N)) = 0.292893 - O((w'/N)^2), vanishing at rate N^{-2/3}.
8. Above tau_0 the record has NO conclusion (the bound is one-sided).

**Comparison with the frozen prediction.** Predicted: tau_0 strictly in
(0, 1/6), of order 1/20. Derived (conditional on (TC)): tau_0 ~ 0.0238
~ 1/42, strictly inside (0, 1/6); smaller than 1/20 by a factor of about 2,
traceable to c_1 = 2 (the factor 2 in (A)) where the prediction implicitly
took c_1 = 1. No term was dropped that raises the value; a tighter route
would lower c_1, not raise tau_0 above 1/6. The prediction is not adjusted.
F5 check: tau_0 ~ 1/42 does not exclude every eta compatible with Theta(L)
output (the identity order has eta = eta' = 0 with w' = w = N^{2/3});
F5 not triggered.

## 1.8 HEUR-001 — second-moment bound with shared-leaf dependence charged

Lists (R_i)_{i <= L}, (S_k)_{k <= L} i.i.d. uniform on G (A3), nu fixed.
X_{ik} = A_{ik} Y_{ik} with A_{ik} = 1[nu(R_i) + nu(S_k) in J'],
Y_{ik} = 1[R_i + S_k in D]; p := E A_{ik} = w'/N, q := E X_{ik} = (1 - eta_pop) p.
M = sum A_{ik} (emitted), Z = sum X_{ik} (sound emitted); empirical rate Z/M.
Var(Z) = sum over index pairs of Cov: L^2 diagonal terms each <= q <= p;
pairs sharing exactly one leaf, at most 2 L^2 (L-1) < 2L^3, each with
Cov <= E[X_{ik} X_{ik'}] <= E[A_{ik} A_{ik'}] = p^2 (given R_i the two
emissions are independent with probability w'/N each, nu bijective);
disjoint index pairs are independent. Hence
  Var(Z) <= L^2 p + 2 L^3 p^2,  and likewise Var(M) <= L^2 p + 2 L^3 p^2.
At w' = N/L (p = 1/L): E M = L, E Z = (1-eta_pop) L, Var(M), Var(Z) <= 3L.
The shared-leaf term (2L) is of the same order as the diagonal (L): it
changes the constant from 1 to 3, not the order. Chebyshev (Markov on the
square, elementary): |M - L| <= lambda sqrt(3L) and |Z - E Z| <= lambda
sqrt(3L) except with probability <= 2/lambda^2, whence
  | Z/M - (1 - eta_pop) | <= 2 lambda sqrt(3) / ((1 - o(1)) sqrt L)
                           = O(L^{-1/2}) with probability 1 - 2/lambda^2.
Symbolic validation of HEUR-001 as specified: variance is o(1) relative;
the falsification condition (variance not o(1)) is not met symbolically.
With ties, replace p^2 by E_R[|W_R|^2]/N^2 in the shared-leaf term (charged
explicitly). No conclusion about the heuristic is drawn here.

---

# Stage 2 — T3 as three lemmas

Standing hypothesis for Stage 2: the all-pairs form of T2, i.e. off a set of
pairs of density <= 3 delta, ||f(R+R') - f(R) - f(R') - k_0/N|| <= theta.
(The constant k_0/N is removed by replacing f with f - k_0/N, which changes
no Fourier magnitude; assume k_0 = 0.) This hypothesis is CONDITIONAL on
(TC) of 1.4.

## Lemma (i) — Fourier identity, extraction, exclusion of xi_0 = 0, uniqueness

Identity. Expanding g = sum_xi ghat(xi) chi_xi and using
E_{R,R'} chi_a(R+R') conj chi_b(R) conj chi_c(R') = [a = b][a = c]:
  E_{R,R'} g(R+R') conj g(R) conj g(R') = sum_xi ghat(xi) |ghat(xi)|^2.
Lower bound. The summand has modulus 1; on good pairs its argument is
2 pi (f(R+R') - f(R) - f(R')) with norm <= theta, so its real part is
>= cos(2 pi theta) (theta <= 1/2); on bad pairs the real part is >= -1. Thus
  Re sum_xi ghat(xi)|ghat(xi)|^2 >= (1 - 3 delta) cos(2 pi theta) - 3 delta = 1 - gamma.
Extraction. sum_xi |ghat(xi)|^2 = E|g|^2 = 1 (Parseval), so
Re sum ghat |ghat|^2 <= max_xi |ghat(xi)| * 1; hence some xi_0 has
|ghat(xi_0)| >= 1 - gamma, and the argument of ghat(xi_0) is not needed.
Exclusion of xi_0 = 0. For bijective nu, ghat(0) = E_R e(nu(R)/N)
= (1/N) sum_{u in Z/N} e(u/N) = 0 exactly, so xi_0 != 0 whenever 1 - gamma
> 0. For nu with ties this exact argument is unavailable. The contract's
suggested route, "|D| = Theta(N/L) forces f non-constant on a positive
fraction", was examined and does NOT close on its own: |ghat(0)| >= 1 - gamma
means e(f) is concentrated near one phase on most points, and additivity
then forces that phase near 0, but a thin accepted slice D of size Theta(w)
is compatible with that concentration as far as lemma (i) sees. In the
tie case xi_0 != 0 is therefore carried as the explicit hypothesis
|E_R e(nu(R)/N)| < 1 - gamma (observation recorded; not repaired).
Uniqueness. If |ghat(xi_0)| >= 1 - gamma then sum_{xi != xi_0} |ghat(xi)|^2
<= 1 - (1 - gamma)^2, so every other coefficient has modulus
<= sqrt(1 - (1-gamma)^2) < 1 - gamma iff (1 - gamma)^2 > 1/2. Under that
condition xi_0 is the unique coefficient above 1/sqrt 2 and the spectral
gap is Gap := (1 - gamma) - sqrt(1 - (1-gamma)^2) > 0.

## Lemma (ii) — transfer from G to Z/N

Define phi_P(t) := g([t]P) and phi_Q(t) := g([t]Q) on Z/N, Q = [x]P, x != 0.
Fourier on Z/N: phi_P hat(m) = E_t g([t]P) e(-mt/N) = E_R g(R) conj chi_m(R)
= ghat(m), identically in m. For Q: phi_Q hat(m) = E_t g([tx]P) e(-mt/N);
substituting u = tx (a bijection of Z/N as x != 0):
= E_u g([u]P) e(-m x^{-1} u/N) = ghat(m x^{-1}). Hence phi_Q hat(xi_0 x)
= ghat(xi_0): phi_P has its unique heavy coefficient at xi_0 and phi_Q at
xi_0 x, both of modulus >= 1 - gamma, all others <= sqrt(1 - (1-gamma)^2).
Query cost: one value phi_Q(t) costs one scalar multiplication
(<= 2 log_2 N group operations by double-and-add) plus one evaluation of nu.
Interface: this is exactly the query model demanded of the SFT in lemma (iii).

## Lemma (iii) — two SFT calls and one division (CONDITIONAL on AGS-1)

Dependence. This lemma rests on the recalled Akavia-Goldwasser-Safra
statement, provenance recalled, UNOPENED in this program. The exact form
required, extracted from the needs below, is written VERBATIM as obligation
AGS-1 in external-obligations.yaml. Nothing in this lemma is supported by
the recollection; the lemma is a conditional statement.

Needs, in order. (N1) Query access to phi : Z/N -> C with |phi| <= 1, the
algorithm choosing t (lemma (ii) supplies it). (N2) Threshold tau := 1/sqrt 2
+ Gap/2, so that exactly one coefficient of phi_P (and of phi_Q) exceeds tau.
(N3) Output: a list Lambda containing every m with |phi hat(m)| >= tau, of
size at most a poly(1/tau) bound, with failure probability <= eps. (N4) Cost:
poly(log N, 1/tau, log(1/eps)) queries and arithmetic.

Algorithm (given AGS-1). Call SFT on phi_P with (tau, eps): list Lambda_P.
Call SFT on phi_Q: list Lambda_Q. For every m in Lambda_P estimate
|phi_P hat(m)| by K_est uniform random queries; by Chebyshev (Markov on the
square), K_est = 36 |Lambda_P| / (eps Gap^2) queries give every estimate
within Gap/3 except with probability eps, which isolates xi_0 as the unique
element with estimate > 1/sqrt 2 + Gap/6; likewise xi_0 x from Lambda_Q.
Output x := (xi_0 x) * xi_0^{-1} mod N and verify [x]P = Q (one scalar
multiplication); on failure repeat. Cost per attempt: 2 SFT calls plus
2 K_est estimation queries plus the verification, each query at
O(log N) group operations + 1 evaluation of nu; success probability
>= (1 - eps)^4 (two SFT failures, two estimation failures); expected attempts
<= (1 - eps)^{-4} <= 2 at eps = 1/8. Total: (log N)^{O(1)} * poly(1/Gap)
evaluations of nu and group operations, poly(log N, 1/Gap) memory, with the
polynomial's degree fixed by AGS-1 once opened. The algorithm depends on nu
(through phi) but not on Q beyond queries, and not on the list randomness.
Chebyshev and Parseval are elementary and re-derived; no external source
supports any step; AGS-1 is the single external obligation.

Conditional-exponent statement (M3, as derived): IF (TC) holds and IF AGS-1
holds as written, the cascade costs (log N)^{O(1)} evaluations of nu, i.e.
exponent 0. No independent derivation inside this package finds N^c for the
cascade under those two hypotheses. Separately, the unconditional
consequence (U1) of 1.5 supplies only a N^{-1/6}/log N coefficient, under
which the same cascade would cost N^{Theta(1)}; that is a statement about
the hypotheses' availability, not about the cascade. Both facts are reported.

---

# Stage 3 — the one-percent obligation (HEUR-002), stated and not claimed

When coverage is a constant c in (0, 1) bounded away from 1 (the emission
window captures only a c fraction of the accepted incidences), Step B fails:
(A') no longer bounds w' by w/(1 - eta) and Delta_R is no longer small for
most rows; the row windows need not approximate D - R at all. What survives
of Stage 1 is only: additivity of nu, with defect O(w) in Z/N, on a set of
pairs of density >= c w'/N * (1 - eta) inside the emitted set, i.e.
"additivity on a dense set of pairs" after normalising by the emission
density. The route named in H-JPR-5e33d6 (Balog-Szemeredi-Gowers, then a
Freiman-type theorem in Z/N; both recalled, unopened, obligations only)
would give a subset of G of positive density on which nu agrees with an
affine function of log_P up to O(w) — a noisy coarse-log oracle whose
error positions are unknown. Turning that into a full logarithm is the
hidden-number-problem-with-errors setting; the exact statement it would
need is written as obligation HNP-ERR-1 in external-obligations.yaml.
NOTHING is claimed for this regime: neither that BSG + Freiman applies with
the needed parameters, nor that HNP-ERR-1 is available in the literature,
nor any bound on the resulting cost. HEUR-002 is stated, not validated.

---

# Stage 4 — placement on the IDEA-20260829-3f0f4b surface; uncovered primitives

The 3f0f4b surface: level-1 join cost L^gamma per side, survivor sums
supported on N^s elements; T = N^max(gamma (2-s)/4, s/2), M =
N^max((2-s)/4, s/2). The order-join branch of the RQ-ECDLP-160d89
certificate (H-JPR-3a00f0 rows JPR-C2/C3 realised by a sorted range scan) was
the point (gamma, s) = (1, 2/3), i.e. T = N^{1/3}, M = N^{1/3}.

Placement, as derived: the surface presupposes that the level-1 join is the
expensive step. Under T3 — conditional on (TC), on eta + eta' < tau_0, and on
AGS-1 — any key realising that join sound at that soundness yields log_P(Q)
directly in (log N)^{O(1)} evaluations of nu, so the four-list structure is
not used at all: the branch is a point at exponent 0 OFF the surface, not
the point (1, 2/3) on it. Unconditionally, nothing below N^{1/2} is claimed
and no point of the surface is realised; the realised position of this
package is "no attack". dominated_by and sota_delta are restated in
surface-placement.yaml exactly as in IDEA-20260901-a66d70, each labelled
conditional or realised.

Join primitives NOT covered by T1-T3 (reasons in uncovered-primitives.yaml):
hash joins (rectangle covers, 390ccc's class); polynomial-relation joins
(IDEA-20260901-730f23); data-dependent orders (nu chosen after seeing Q or
the lists); constant-coverage joins (Stage 3); non-prime orders and
non-injective keys under T1; joins with two-sided error or w' << w; joins
whose emission predicate is not a rank-sum window (e.g. rank difference or
product windows); multi-key or multi-round joins; and any join at
eta + eta' >= tau_0. Also not covered: keys with ties under the exact
width form of size matching (1.6) and the tie case of the xi_0 = 0
exclusion (lemma (i)).

---

# Summary of what this package derives and does not derive

Derived (derivation tier): T1 in full with the boundary widths and the
complementation extension; the three forced control dispositions; the
N = 23 fixture; T2 steps A, B, Markov, union bound with explicit constants;
the approximate translation-invariance (C1); the O(w) fallback (FB) on
emitted sound pairs; the unconditional weak-coefficient bound (U1); lemma
(i) except the tie-case xi_0 = 0 exclusion; lemma (ii); lemma (iii)
conditional on AGS-1; the HEUR-001 second-moment bound; the tau_0 chain.
Not derived: the translate-comparison step / stability lemma (TC), hence
the all-pairs form of T2, hence the premise of lemma (i)'s lower bound and
of tau_0; the tie-case exclusion of xi_0 = 0. No hypothesis, experiment,
question, or goal status is changed by any of this; no ECDLP result exists.
