# R1 — derivation note: minor degrees, the specialization step, the planted
# subvariety, and the EXACT rank-drop locus at (m, d, s) = (2, 2, 3)

Label: **derivation** (a checkable argument), never *proved theorem*. Red team,
TASK-20260904-8c5f97, EXP-PFDR-fd901a. Every integer below is produced by a
script under `scripts/` in this directory, with output under `out/`; nothing is
an experiment run.

## 1. Entries of M_D (claim (A) step 1) — CONFIRMED, independently

`scripts/r1_symbolic_entries.py` expands S_3(ell_1, ell_2, x_R) over
Z[A, B, x_R] with sympy from **my own** expression for S_3 (not
`harness/semaev.py`) and reduces a_i^2 -> a_i:

| quantity | my value | Stage 0 claim |
|---|---|---|
| nonzero entries of the D = 4 row | 49 | 49 |
| max total degree of an entry in (A, B, x_R) | 2 | 2 |
| integer content (gcd) of the whole row | 1 | 1 |
| content of the degree-3 entries | 4 | 4 (smallest) |
| content of the degree-4 entries | 16 | 16 |
| degree-4 part parameter-free | True | True |
| degree-4 part = 16 Q_1 Q_2, Q_k = a_{k0}a_{k1} + 2a_{k0}a_{k2} + 4a_{k1}a_{k2} | True | equivalent form stated |

Rows of M_5, M_6 are mu·S~ with multiplication merging monomials by bitwise OR,
so every entry stays a Z-linear combination of the 49 entries and keeps degree
<= 2. **Step 1 of claim (A) holds as written.**

My own S_3 was itself checked against real group arithmetic (40/40 random
(A,B,P,Q) at p = 10007: S_3(x(P), x(Q), x(P+Q)) = 0; `out/r1_derivation.json`
`s3_selftest`), so the audit does not inherit the producer's S_3.

## 2. The minor-degree bound — CORRECT IN STAGE 0, VACUOUS IN THE LEDGER RECORD

Stage 0 fixes ONE nonzero maximal minor P_D^*, deg(P_D^*) <= 2 r_D, and uses
Prob[drop] <= 2 r_D / p (2, 12, 30 at D = 4, 5, 6). That is valid: a rank drop
forces **every** maximal minor to vanish, so the vanishing of one fixed nonzero
minor is a necessary condition.

`H-PFDR-09e1b0.statement` and `IDEA-20260903-26aa81` claim (A) instead define
P_D as **the product of the nonzero maximal minors** and quote
Prob[drop] <= deg(P_D)/p. That is also valid but, at D = 6, the 15 x 64 matrix
has C(64, 15) = 159 518 999 862 720 maximal minors, so
deg(product) <= 30 · C(64,15) = 4.79e15 and the bound reads

  Prob <= 4.79e15 / p,

which is **vacuous at p = 4099 and at p = 16411** — i.e. at exactly the prime
where criterion (4) claims to measure the artifact rate — and only becomes
non-trivial above ~4.8e15. The usable constant is Stage 0's, and Stage 0 is not
the committed hypothesis record. **Objection RT-O1.**

## 3. Specialization inequality — holds, with a characteristic caveat

rank_{F_p}(M_D(pt)) <= rank_{F_p(A,B,x_R)}(M_D) <= r_D (the char-0 generic
rank). The *middle* term, not r_D, is what a specialization can reach: the
char-p generic rank can be strictly smaller when p divides all maximal minors.
The record covers this with "p not dividing the content of P_D", but Stage 0
§4 operationalizes "content prime" as the **gcd of the entries** of the D = 4
row (= 1, "so no prime divides the whole row") and then asserts "no odd prime
divides any entry's content". Entry content is not minor content; the
proves-too-much object 2 (Wilson W_{1,3}, s = 6, p = 3) is a matrix whose entry
content is 2 and whose rank nevertheless drops at p = 3. **Objection RT-O2.**

The gap is closable by computation, and I closed it: the integer top blocks at
D = 4, 5, 6 have invariant factors (16), (16, 16), (16) respectively
(`out/proves_too_much.json`, `top_block_invariant_factors_over_Z`), so the top
rank profile [1, 2, 1] holds **over every field of characteristic != 2** and
p = 2 is the only content prime of the top block. That is the conclusion Stage 0
asserted; it is now supported.

## 4. The planted subvariety — TESTED, no difference

Plan's worry: the planted x_R = x(P_1 + P_2) might lie inside the zero locus of
every maximal minor. Test (`out/r1_derivation.json`, `planted_vs_uniform`), my
own elimination, per prime 40 planted draws (the recorded (A, B, x_R)) plus 20
uniform (A, B, x_R):

| p | planted profiles | uniform profiles | planted zeros of S~ on the cube | uniform zeros |
|---|---|---|---|---|
| 4099 | [(0,0),(1,1),(6,2),(15,1)] × 40 | same × 20 | 2 (40/40) | 0 (20/20) |
| 2^64 - 59 | same × 40 | same × 20 | 2 (40/40) | 0 (20/20) |
| P-256 | same × 40 | same × 20 | 2 (40/40) | 0 (20/20) |

The planted generic profile equals the uniform one at all three primes. The
planted design differs from uniform only by forcing exactly 2 zeros of S~ on the
64-point cube (the two orderings of the planted pair) — 14 short of the
threshold in §5. **No planted-versus-uniform difference: the plan's breaking
artifact does not appear.**

## 5. The EXACT rank-drop locus (sharper than Schwartz-Zippel)

In the multilinear quotient B = F_p[a]/(a_i^2 - a_i) ≅ F_p^{64} (evaluation on
{0,1}^6), the row mu·S~ is the vector (mu(v) S~(v))_v. Scaling columns by the
nonzero values S~(v) does not change rank, so

  **full_rank(D) = rank of the 0/1 evaluation matrix of the squarefree
  monomials of degree D - 4 at the points of supp(S~) = {v : S~(v) != 0}.**

full_rank(D) therefore depends on S~ **only through its zero set**, and a drop
at D needs a nonzero multilinear polynomial of degree D - 4 vanishing on
supp(S~). Minimum-weight lemma (induction on n; standard): a nonzero multilinear
polynomial of degree <= k over any field is nonzero at >= 2^{n-k} points of
{0,1}^n. With n = 6:

| D | rows | drop requires |Z(S~)| >= | witness at the threshold |
|---|---|---|---|
| 4 | 1 (deg 0) | 64 (S~ ≡ 0) | — |
| 5 | 6 (deg 1) | 32 | Z = {a_i = 0} |
| 6 | 15 (deg 2) | 16 | Z = {a_0 = a_1 = 1}: rank 14 < 15 (verified, `out/r1_rankdrop_locus.json`) |

The top block cannot drop at all for odd p (§3, parameter-free with invariant
factors 16). **So the entire rank-drop locus at (2,2,3) is the set of
(A, B, x_R) at which S~ acquires >= 16 zeros on the cube in special position.**

Rigorous density bound, better than Schwartz-Zippel and uniform in the curve:
for fixed (A, B), each of the 64 cube points contributes a **quadratic in x_R**,
so at most 128 (point, root) incidences exist; an x_R with >= 16 zeros consumes
16 of them, so at most 8 values of x_R in all of F_p can have >= 16 zeros:

  density of the D = 6 drop locus in x_R  <=  8 / p   (= 0.00195 at p = 4099)
  density at D = 5 <= 4/p, at D = 4 <= 2/p; union <= 14/p versus Stage 0's 44/p.

## 6. The explicit rank-drop point the plan asked for: THERE IS NONE at p = 4099

The plan asks for an explicit (A, B, x_R) at p = 4099 dropping the D = 5 top
block. **No such point exists**: the D = 5 top block is the parameter-free
matrix of multiplication by 16 Q_1 Q_2, of rank 2 over every field with 2 != 0.

For the full ranks I searched the **whole x_R axis exhaustively** by the
root-finding route of §5 (`scripts/r1_rankdrop_locus.py`):

| object | curves | x_R searched per curve | max zeros of S~ found | drop threshold |
|---|---|---|---|---|
| the 8 contract curves + 8 singular cubics at p = 4099 | 16 | all 4099 | 6 | 16 |
| random curves at p = 4099 | 19 992 | all 4099 (81 947 208 pairs) | 6 | 16 |

Maximum-zero histogram over the 19 992 curves: 2 → 18 575, 3 → 285, 4 → 1123,
5 → 5, 6 → 4. The worst case found (A = 2622, B = 1125, x_R = 1628, 6 zeros)
still has the reference profile [(0,0),(1,1),(6,2),(15,1)].

**Conclusion for R1.** Every step of the derivation checks out and the planted
step is unproblematic, for a reason stronger than the plan's: the locus it
worries about is empty on the tested primes, not merely thin. Two defects are
recorded (RT-O1 vacuous constant in the committed record; RT-O2 entry-content
in place of minor content). The stated breaking artifacts (an explicit p = 4099
rank-drop point; a planted-vs-uniform difference) **did not appear**.
