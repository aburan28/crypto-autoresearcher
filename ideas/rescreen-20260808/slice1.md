# Adversarial re-screen — slice1 (19 records)

Reviewer: red team. Snapshot read: `/tmp/wt-ideas-100` (read-only, nothing edited or
committed). Web search unavailable — **all external-literature novelty below is
unadjudicated and marked as such**. Every verdict here is an internal-corpus or
internal-mathematics verdict.

## Verdict table

| ID | verdict | one-line reason |
|---|---|---|
| IDEA-20260808-06aae4 | NOVEL | Sound cost-model record; its unit-cost "baseline reproduction" check is circular against its own no-published-figures rule (fix, not kill). |
| IDEA-20260808-a33400 | **REFUTED** | Headline prediction `c(4) > 1` is the record's own falsification condition: at r=4 the admissible delta-set family inside one diagonal structure has exactly **one** member. Measured 0/16 balanced at r=4 for every proper sub-coset. |
| IDEA-20260808-0e9fa1 | **REFUTED** | Decisive branch (ii) is empty a priori: an upper bound valid for **every** target is ≥ max ≥ the exact KN-FIND-007 mean, which the record itself cites. |
| IDEA-20260808-c31f1c | PARTIAL-OVERLAP | Same-round `486ae2` already enumerates "intervals, arithmetic progressions, rank-r generalized APs" as the lattice-describable family; plus a mis-citation of KN-FIND-007's coverage ceiling (1.107 vs the recorded ~1.54). |
| IDEA-20260808-be161c | **REFUTED** (claim C3 / the frontier inequality; O1–O3 and C1–C2 survive) | The stated frontier fails the record's own corner-reproduction control: the lattice corner gives `m ≥ N`, not `m > N/l`, and with the detection line included it is **infeasible for every m at l = 1**. |
| IDEA-20260808-c64123 | **SCOPE-INFLATED** | `GOAL-ECTD-001.yaml` contains **zero** occurrences of "descent" or "torsion"; the record's whole justification is closing a named priority family the goal does not name. Its (A)/(B) hold for every finite abelian group. |
| IDEA-20260808-5158fa | NOVEL | Derivation checks out; but the load-bearing equality is true by definition and the primary prediction cannot fail — only the named negative control is informative. |
| IDEA-20260808-ea3b4f | PARTIAL-OVERLAP | Fourth closure-quality audit in the same round (`3fdef7`, `8e13ff`, `71fea9`); premises verified, needs an explicit discrimination note. |
| IDEA-20260808-5d8b39 | NOVEL | Parameters and the outer-factor arithmetic verified independently (n=17669, n₁n₂=17664, l=5, tail = 2^-132.8). |
| IDEA-20260808-e820d2 | **REFUTED** (closure (iv) and prediction 5; facts (i)–(iii) survive) | MAYO-2 is silently omitted from the G table; **G(MAYO-2) = −12 ≤ 0**, so by the record's own criterion the route is *not* closed there. Prediction 5 predicts locus dimensions **below** dim P(O) (one of them negative) at the record's own toy cells. |
| IDEA-20260808-baf8bc | NOVEL | Sound accounting exercise; partially pre-empted at the Classic McEliece point by same-round `a3bcf0`, which is disclosed from the other side. |
| IDEA-20260808-e5f947 | NOVEL | Sound conformance record with a mandatory planted-defect control; should cite the corpus-invisible `KN-FIND-720727`. |
| IDEA-20260808-aa551f | **REFUTED** | `binom(τN,τ)` is not the challenge space under any tree layout: τ-parallel MPCitH forces exactly one unopened leaf per repetition, so the count is `N^τ` and the claimed delta is 0 by protocol semantics, not by a spec read. |
| IDEA-20260808-c959c7 | NOVEL | Derivation checks; the plain-UOV "forced value" arm is vacuous as a calibration; self-label bookkeeping defect shared with `040db9`. |
| IDEA-20260808-afe4ce | **REFUTED** | Computed: at the record's own cell (p=1009, B=5, m=2) the Gröbner basis of I_R is **[1]** in 8/8 random targets and contains a **degree-1** element in 6/6 planted-decomposition targets. Predicted floor was exactly B. |
| IDEA-20260808-040db9 | PARTIAL-OVERLAP + prior-art flag | The "oil space is an F_q[S]-module ⇒ extra equations" mechanism is, to my recollection, the core of published improved SNOVA cryptanalysis; corpus record `IDEA-20260805-70aa6e` already establishes the module structure. Unverifiable offline. |
| IDEA-20260808-750ead | NOVEL | Sound, but the predicted answer (density 1) is derivable in one line for any surrogate whose response degree exceeds the graph diameter; the O(\|V\|²) enumeration buys little. |
| IDEA-20260808-2b4581 | **REFUTED** (headline claim (ii); the ledger is salvageable under its other convention) | Its own self-consistency control `D(plain UOV) = 0` fails at 3 of 4 published UOV sets under the convention it uses for the headline `16^304`; D reduces to `(N−2O)·log₂q` minus the claimed level. |
| IDEA-20260808-7c4e9d | **REFUTED** | Arm C is *not* the random-from-F_p null (verified in `full_grid.py` at the very lines the record cites, and contradicted by same-round `4f3ef4`); its primary statistic is 0/0 in **34/40** cells; its prediction 3 is **false** on the data it claims to have already read. |

Counts: 7 NOVEL, 3 PARTIAL-OVERLAP, 8 REFUTED, 1 SCOPE-INFLATED.
(NOVEL: 06aae4, 5158fa, 5d8b39, baf8bc, e5f947, c959c7, 750ead.
PARTIAL-OVERLAP: c31f1c, ea3b4f, 040db9. REFUTED: a33400, 0e9fa1, be161c, e820d2,
aa551f, afe4ce, 2b4581, 7c4e9d. SCOPE-INFLATED: c64123.)

---

## Kills, with the competing claim or computation

### IDEA-20260808-a33400 — REFUTED (AES integral incidence design)

The record's discriminating prediction is "**c(4) > 1 strictly** (the 4-round integral
admits genuine reuse) while c(5) = 1", where `c(r)` is the GF(2)-rank of the span of the
r-round check functionals indexed by the delta-sets contained in one 2^32 diagonal coset
S, and where the admissible delta-sets are "a coset of a 1-byte or 4-byte active subspace
**on which the r-round balancedness check is defined**".

Its own claim (i) says the 4-byte diagonal family has "exactly 1" member inside S. So
c(4) > 1 requires the 1-byte family to be admissible at r = 4. It is not. Direct
measurement (full AES round function, column-major, random round keys):

```
1-byte-active Lambda-set at byte  0: rounds=3  balanced bytes = 16/16
1-byte-active Lambda-set at byte  0: rounds=4  balanced bytes =  0/16
1-byte-active Lambda-set at byte  5: rounds=3  balanced bytes = 16/16
1-byte-active Lambda-set at byte  5: rounds=4  balanced bytes =  0/16
1-byte-active Lambda-set at byte 10: rounds=3  balanced bytes = 16/16
1-byte-active Lambda-set at byte 10: rounds=4  balanced bytes =  0/16
1-byte-active Lambda-set at byte 15: rounds=3  balanced bytes = 16/16
1-byte-active Lambda-set at byte 15: rounds=4  balanced bytes =  0/16

2-byte-active subsets of the same diagonal, r=4:
  active bytes (0, 5): 2^16 texts, rounds=4 -> balanced bytes = 0/16
  active bytes (0,10): 2^16 texts, rounds=4 -> balanced bytes = 0/16
  active bytes (5,15): 2^16 texts, rounds=4 -> balanced bytes = 0/16
```

No proper sub-coset of the diagonal structure supports a 4-round balancedness check, so
the r=4 admissible family inside S has exactly one member and **c(4) = 1** — which is
verbatim the record's first falsification condition ("c(4) = 1. The standard data charging
is exactly right"). Two further consequences the record states backwards:

* It predicts `c(5) = 1`. By its own definition and the campaign's committed 0/16 at r=5,
  the r=5 admissible family inside S is **empty**, so c(5) = 0, not 1.
* Claim (iii) says "the data complexity every integral attack charges is off by exactly a
  factor c". The 16 output-byte checks from one structure are already charged by everyone
  — the campaign's own committed measurement is "16/16 balanced" from a single 53 s sweep.
  The reuse the record proposes to discover is the reuse already in the standard accounting.

What survives: the closed-form count |I(S)| = 2^24 · 4 = 2^26 for the 1-byte family is
correct, and the same rank question at **r = 3** (where the 1-byte family *is* admissible)
is a real, unasked question. Narrowest valid restatement: "how many independent 3-round
checks does one 2^32 diagonal structure support?"

### IDEA-20260808-0e9fa1 — REFUTED (determinant method on the Semaev hypersurface)

The record's dichotomy is: "(i) the bound exceeds the heuristic, so no obstruction is
proved... or (ii) the bound is BELOW the heuristic, in which case windowed factor bases are
yield-deficient unconditionally and the whole family dies with a rigorous theorem". It
prices (ii) at ~0.15.

Branch (ii) is empty before any derivation. The record cites `KN-FIND-007`, whose statement
is `E_r[c_D(r)] = binomial(B+m−1,m)/N` **exactly, for every base of size B, independently of
how D is chosen** — so a box base attains the mean by a one-line double count, and the
record's framing ("KN-FIND-007 ... says nothing about whether a BOX attains it") is answered
by the finding it cites. A determinant-method bound `F(m,B,p)` valid for **all** targets
satisfies `F ≥ max_r c_D(r) ≥ E_r[c_D(r)]`. Hence F can never be below the mean.

The comparison is also numerically vacuous at the stated operating point, where the exact
mean is far below 1:

```
 p      m   eps    B=p^(eps/m)   exact mean C(B+m-1,m)/N
 2^64   3   0.50   2^10.67       3.88e-11  = 2^-34.58
 2^64   4   0.75   2^12.00       6.37e-07  = 2^-20.58
 2^256  3   0.50   2^42.67       4.90e-40  = 2^-130.58
 2^256  5   0.75   2^38.40       4.52e-22  = 2^-70.91
```

A bound below these would prove `c_D(r) = 0` for **every** target, contradicting a positive
exact mean. Narrowest valid residue, and the version worth filing: the determinant method
could bound the **maximum / upper tail** of `c_D(r)`, which KN-FIND-007 explicitly does not
constrain ("Only the distribution is free"). That is a concentration question, not a
mean question, and the record must be rewritten in those terms or withdrawn.

### IDEA-20260808-be161c — REFUTED in claim C3 (the frontier inequality)

The record's own control: "**CORNER REPRODUCTION**: at h = m, C = 1, t = 0 the frontier
inequality must reduce to the textbook m > N/l information bound... A frontier that does not
contain the two known corners is misimplemented."

Its feasibility line is `log2 binom(m,h) + h·log2(2C) + t − N ≥ log2 M`. **The parameter l
does not appear in it at all.** At h = m, C = 1, t = 0 this is `m − N ≥ log2 M`, i.e.
`m ≥ N` — off by a factor l from the textbook bound, and exact only by coincidence at l = 1.
Including the detection line `log2 M ≥ 2h·log2(1/|sinc(C·2^{−l})|)` makes it worse:

```
  N=160 l=1: sinc(2^-1)=0.636620  textbook N/l = 160.00   record's corner: m >= inf (infeasible)
  N=160 l=2: sinc(2^-2)=0.900316  textbook N/l =  80.00   record's corner: m >= 229.55  (x2.87)
  N=256 l=1: sinc(2^-1)=0.636620  textbook N/l = 256.00   record's corner: m >= inf (infeasible)
  N=256 l=3: sinc(2^-3)=0.974495  textbook N/l =  85.33   record's corner: m >= 276.62  (x3.24)
```

At l = 1 — the record's own headline cell (256,1), and the leakage regime of both published
rows it quotes — the frontier declares the lattice corner infeasible for every m. Since C3's
INTERIOR/FACE predicate is an optimisation of exactly this functional, C3 is computing on an
object that does not contain the incumbent method.

Corroboration from inside the same round: the record's declared successor X1-02
(`IDEA-20260808-e40da2`) uses a *different* and correct reduction line (`t = N − k·s`) and
explicitly places "the lattice-with-predicate family... deliberately OUTSIDE the class". The
two records therefore contradict each other on whether the two families are corners of one
polytope — which is exactly claim C1.

What survives, and it is real: (O1)–(O3) are correct (I verified sinc(1) = 0 for the null
control and monotone decay of sinc(2^{−l}) as l falls, both as the record predicts), and C2
(the (w, r, μ) reporting signature) is untouched. Also note `novelty_screen` says "all 5 rows
matching RQ-ECDSA-87625f" and then lists 4 IDs, while `EXISTING_PROPOSALS.txt` has 3 such
rows — a small accuracy defect in a field the brief says to test rather than trust.

### IDEA-20260808-c64123 — SCOPE-INFLATED (Lang's theorem / descent)

Two independent problems.

**(1) The goal citation is false.** The record says "GOAL-ECTD-001's title names
'torsion/descent' as a priority family" and claims to convert "one of GOAL-ECTD-001's four
named priority families" to closed, satisfying completion criterion 1. `grep -c -i` over
`ledger/goals/GOAL-ECTD-001.yaml` returns **0 for "descent" and 0 for "torsion"**. The goal's
four prioritised families are: (1) secret isogeny-aligned factor bases and Semaev/Gröbner
heavy tails, (2) large-conductor vertical barriers, (3) hidden correspondences, (4) trapdoor
DDH. Completion criterion 1's barrier branch asks for an obstruction "for each prioritized
endpoint family" — closing a family the goal never prioritised advances it by zero.

**(2) The mathematics is an elementary identity in cohomological dress.** (A) is
`#(E(F_p)/lE(F_p)) = #E(F_p)[l]`, which is true for **any** finite abelian group A
(`|A/lA| = |A[l]|`) and needs neither Lang's theorem nor the Kummer sequence. (B) is
`G/lG = 0` for G of prime order N and l ≠ N, i.e. l is invertible mod N. Consequently the
proposed 200-curve toy test is a measurement whose null object returns the identical answer:
run it on a random finite abelian group and you get the same 100%. Per the artifact-tell
rule, a quantity that cannot move is not evidence. The only informative arm is the listed
PLANTED POSITIVE (non-cyclic l-part), which tests the instrument, not the claim.

Narrowest valid conclusion: the record is a correct one-paragraph note, not a closure, and
it must be re-anchored to a family the goal actually prioritises before it is scheduled.

### IDEA-20260808-e820d2 — REFUTED in closure (iv) and prediction 5 (MAYO excess defect)

Recomputing the record's own quantities from its own parameter table
(`e = o − (n−m)`, `G = (n−o) − e·o`, isolation iff `G ≤ 0`):

```
set             n    m   o    e   e*o  n-o     G  isolates?  dim locus pred  dim P(O)
MAYO-1         66   64   8    6    48   58    10      False              17         7
MAYO-2         78   64  18    4    72   60   -12      TRUE                5        17
MAYO-3         99   96  10    7    70   89    19      False              28         9
MAYO-5        133  128  12    7    84  121    37      False              48        11
```

The record reports "At RECALLED MAYO parameters G = 10, 19 and 37 -- it does not isolate".
**MAYO-2 is missing, and it is the one set where G ≤ 0**, i.e. where by the record's own
criterion the differential rank-drop locus *does* isolate the oil space. The claimed
closure ("the two conditions are equivalent, so the rank condition can never be strictly
stronger") is therefore unestablished at one of the four published parameter sets, and the
omission is silent.

Prediction 5 is worse: it predicts `dim(rank-drop locus) = n − 1 − e·o` exactly. But the
locus **always contains P(O)** (for x ∈ O, rank DP(x) ≤ n−o), so its dimension is always
≥ o−1. At the record's own toy cells:

```
  (q,n,m,o)=(16, 8,7,3)  e=+2  predicted dim = 1   but dim P(O) = 2   -> impossible
  (q,n,m,o)=(16,10,9,4)  e=+3  predicted dim = -3  but dim P(O) = 3   -> impossible (negative)
  (q,n,m,o)=(16,10,5,4)  e=-1  predicted dim = 13  but ambient dim = 9 -> impossible
```

The correct statement is `dim = max(o−1, n−1−e·o)` generically, and the isolation criterion
is exactly the case where the first term wins. Facts (i)–(iii) (the e sign table) are correct
as arithmetic and are the salvageable part.

### IDEA-20260808-aa551f — REFUTED (MQOM one-tree challenge count)

The arithmetic in prediction 2 is right: `log2 binom(τN,τ) − τ·log2 N ≈ τ·log2(e) − O(log τ)`
(e.g. 19.71 bits at N=256, τ=16). The interpretation is not.

In τ-parallel MPCitH/TCitH the τ unopened leaves cannot be an arbitrary τ-subset of the τN
leaves. Exactly one leaf per repetition must remain unopened: a repetition with **zero**
unopened leaves has all its shares revealed (the witness for that repetition is exposed), and
a repetition with **two** unopened leaves cannot be verified. So the admissible challenge set
has size `N^τ` whether the seeds come from τ independent trees or from one tree of τN leaves.
The one-tree optimisation reduces the number of revealed internal seed nodes (path overlap
near the root); it does not enlarge the challenge space. `binom(τN,τ) = 2^147.7` versus
`N^τ = 2^128` at (256,16) counts 19.7 bits of *inadmissible* openings.

The record names this as its first confounder ("at most one opened leaf per block, in which
case the count is N^tau after all") and then builds its title, claim (iii) and prediction 4
(a strictly smaller τ and smaller signatures) on the binomial anyway, with
`honest_prior_of_survival` 0.6/0.35 on the wrong side. The sign is also opposite to the
concern the corpus already carries: `IDEA-20260805-cec9b6` raises *correlated* GGM trees, a
defender's-disfavour effect, which is the direction single-tree constructions are actually
questioned in.

Narrowest valid residue: reading MQOM's layout and its stated soundness denominator is still
worth doing as a one-paragraph spec check, but the pre-registered delta is 0 and the record
should say so rather than predict tens of bits of unclaimed margin.

### IDEA-20260808-afe4ce — REFUTED (prime-field last-fall-degree floor)

The claim: with `I_R = <S_{m+1}(x_1..x_m, x_R)> + Σ_i <f_V(x_i)>`, "every element of I_R of
degree < B ... is a multiple of the Semaev generator alone", and prediction 1 is "**Exactly
B** at every cell (p in {1009, 4099}, B in {5,6,8,10}, m in {2,3})".

`<f_V(x_1), f_V(x_2)>` is radical, so `F_p[x_1,x_2]/<f_V(x_1),f_V(x_2)> ≅ F_p^{V×V}` and the
ideal generated by S in a product of fields is the set of functions vanishing on the zero
locus. Hence `I_R = I(Z)` with `Z = {(v_1,v_2) ∈ V² : S_3(v_1,v_2,x_R) = 0}` — the set of
decompositions of the target. At the record's cells `|Z|` is 0 or 1 (mean ≈ B^m/p ≤ 0.1), and
the vanishing ideal of a tiny finite set has tiny-degree elements. Computed directly (real
Semaev S_3 on a real curve, exact GF(p) Gröbner bases):

```
p=1009, y^2=x^3+331x+970, B=5, m=2, random targets:
  trial 0..7: |Z| = 0 in 8/8;  Groebner basis of I_R = [1]        <- degree 0, not a multiple of S_3

p=1009, y^2=x^3+463x+886, PLANTED targets R = P1+P2 with P1,P2 in the factor base:
  B=5  trials 0-2: |Z|=2, GB total degrees = [1, 2]   -> min degree of a non-multiple of S_3 = 1 (predicted 5)
  B=10 trials 0-2: |Z|=2, GB total degrees = [1, 2]   -> min degree of a non-multiple of S_3 = 1 (predicted 10)
```

Both regimes refute the floor: 0 when the target has no decomposition (the overwhelmingly
typical case at these parameters), 1 when it has one. The floor argument's error is that it
treats `I_R` as if it were graded — "J contributes nothing below degree B" ignores that
`h·S + Σ a_i f_V(x_i)` can cancel its own high-degree part, which is precisely what a
Gröbner computation does. Note the record's own HA-1 ("the decomposition locus is a proper
subvariety of {S=0}") is exactly the condition that makes I_R the ideal of a *very small*
set, i.e. it argues against the floor rather than for it.

Narrowest valid residue: with `x_R` left as a **free variable** the counting is genuinely
different (a rough parameter count gives a threshold near B for m = 2 and near 1.3B for
m = 3), and that is a defensible version of the claim. But the record's own point count
("S_{m+1} = 0 has p^{m−1} solutions") fixes x_R as a constant, so the version as filed is
refuted at its own cells.

### IDEA-20260808-2b4581 — REFUTED in headline claim (ii) (structure-discount ledger)

Its self-consistency control: "for plain UOV the ledger must return D = 0 **exactly**, since
the scheme IS its own matched baseline. A nonzero D there means the convention is
inconsistent." Its headline number uses `C_nom = q^{N−2O}` (that is where `16^304` comes
from). Evaluating that convention on the published plain-UOV sets:

```
  ov-Is : q=16  n=160 o=64  N-2O=32  log2 C_nom=128.0  claimed 128 ->  D =   0.0
  ov-Ip : q=256 n=112 o=44  N-2O=24  log2 C_nom=192.0  claimed 128 ->  D =  64.0
  ov-III: q=256 n=184 o=72  N-2O=40  log2 C_nom=320.0  claimed 192 ->  D = 128.0
  ov-V  : q=256 n=244 o=96  N-2O=52  log2 C_nom=416.0  claimed 256 ->  D = 160.0
```

The control fails at 3 of 4 sets; it holds at ov-Is by coincidence. The reason is structural,
not a transcription slip: under this convention `D = (N−2O)·log₂q − (claimed level)`, so D is
a relabelling of how far the *flattened* parameters sit from the UOV design regime, not an
exchange rate for the algebraic structure. The predicted ordering
`D(SNOVA) > D(QR-UOV) > D(MAYO) > D(UOV) = 0` is then forced by `N − 2O` alone and carries no
information about whether any structure is exploitable; `D(SNOVA) = 1088` bits says only that
n/o = 5.8 is not a UOV parameter choice.

What survives: the ledger under the *other* declared `C_nom` variant (a solving-degree model,
with `C_best` the best attack actually read) is coherent, and the UNAVAILABLE-cell discipline
is good practice. But then the `16^304` headline, and claim (ii)'s "largest object in the
slice by orders of magnitude", must be withdrawn.

### IDEA-20260808-7c4e9d — REFUTED (x-oracle true-null re-analysis)

Four independent defects, all checkable inside the snapshot.

**(1) The central premise is false, and the record names the file that refutes it.** It
claims "the true-null control ... ('Arm D: Random-from-F_p MITM') has already been performed:
Arm C in EXP-SEMAEV-f48dd1 uses random x-coordinates from F_p in the MITM framework", and
offers `full_grid.py` lines 195–278 as verification. Reading exactly that function
(`arm_c_random_predictor`, which begins at line 195): the **right-half table is identical to
Arm B**, built from the true sums `x(P2+P3)`; only the **left query value** is replaced by a
PRNG output, and with explicit collision avoidance (a random *injection*, not i.i.d. uniform).
Arm C then verifies the *actual* `P1`, whose x-coordinate is not the queried value. It is Arm
B with the query key deliberately decorrelated from the object verified — null by
construction, not by measurement. The same-round record `IDEA-20260808-4f3ef4` states the
identical reading in its own novelty screen ("The prior three-arm experiment used a random
predictor on the left query side (Arm C); it did not randomize the right-table key... the
proposed Arm D is a new control object") and proposes the control 7c4e9d says already exists.
Two records filed the same day against the same question and the same experiment, in direct
contradiction, neither citing the other.

**(2) The primary statistic is undefined on the data.** From
`runs/RUN-SEMAEV-f48dd1-grid/raw-results.json` (40 cells):

```
cells with relations_found_A == relations_found_B : 40/40   (the record's Y_A = Y_B: confirmed)
cells with relations_found_C == 0                 : 34/40
cells where cost_per_relation_C is 0/0 undefined  : 34/40
```

The record's Step 1/2 deliverable is `cost_per_relation = field_operations / relations_found`
for all three arms, its prediction 2 is
`mean(cost_per_relation_C / cost_per_relation_A) > 2.0`, and its falsification condition 2 is
the same ratio `< 1.5`. Both are division by zero in 85% of the cells, and the proposed
"mean, std, min, max" is not computable.

**(3) A pre-registered prediction is already false on the data the record says it read.**
Prediction 3: `mean(candidates_verified_C / |F|^2) < 0.1`. Actual: **0.132**, max 0.27.

**(4) Arithmetic.** `target_complexity.memory_exponent` reads "O(|F|^2) = O(p^{2bm}) ... For
m=3, b=0.5, this is O(p^3)". With `|F| = p^b`, `|F|² = p^{2b} = p^1`, not `p^3`; the exponent
conflates `|F|` with `|F|^m`. The same `p^3` figure is then used in `dominated_by` as the
memory axis of the Pareto comparison.

Taken together the record asserts results in `claim` ("The existing data shows...") that it
simultaneously lists as unmeasured predictions, and recommends a **closure** on that basis.
Per `docs/inventor-protocol.md` §4 a closure needs a named obstruction and an argument; here
the argument is "Y_C ≪ Y_A therefore the MITM framework provides no yield advantage", which
is a non-sequitur because Arm C's yield is zero by construction. The right closure input is
`4f3ef4`'s Arm D, which does not exist yet.

---

## Partial overlaps, with the exact text to add

### IDEA-20260808-c31f1c — PARTIAL-OVERLAP

Same-round `IDEA-20260808-486ae2` (the record c31f1c refers to only by the generator-internal
label "E1-01", never by ID) already states in its claim (A): "Subsets of F_p that are
describable at cost o(B) therefore fall into exactly one further family: LATTICE-DESCRIBABLE
sets (**intervals, arithmetic progressions, rank-r generalized APs**)". c31f1c's title claims
that enumeration as its own content.

Suggested `discriminated_from` addition:

> IDEA-20260808-486ae2 already enumerates the lattice-describable family as intervals,
> arithmetic progressions and rank-r generalized APs and fixes the threshold
> eps > m/(2(m-1)); this record contributes only (A) the invariance lemma that all rank-1
> GAPs are equivalent to the interval under an affine substitution, and (B) the measurement
> of eps_r versus eps_1 for r >= 2. It makes no classification claim.

Separately, a required correction: prediction 3 sets the artifact threshold at "the
Sidon-ceiling factor 1.107". `KN-FIND-007` records 1.1071 as a *measured* coverage ratio for
a Bose–Chowla base at one tested battery and states the ceiling separately: "**The headroom
ceiling is about +54%**". Using 1.107 as the threshold would cause a real coverage effect of
up to ~1.54 to be discarded as an artifact.

### IDEA-20260808-ea3b4f — PARTIAL-OVERLAP

Premises verified: `KN-FIND-002`, `KN-FIND-b7e091` and `KN-FIND-982fdf` are indeed oracle
simulability statements (titles confirmed in `knowledge/findings/`), and `KN-OPEN-001` is
indeed open. No mathematical objection. But this is the fourth closure-quality audit filed in
the same round (`3fdef7` on invisible barriers, `8e13ff` on a closure promotion gate, `71fea9`
on closure independence), and its `discriminated_from` names none of them.

Suggested addition:

> IDEA-20260808-8e13ff proposes a promotion GATE for new closures and IDEA-20260808-71fea9
> tests whether a round's closures are independent; both judge the closures themselves. This
> record takes the three findings as correct and audits only whether existing CITATIONS of
> them stay inside the generic-group model's input assumption. IDEA-20260808-3fdef7 concerns
> corpus visibility, not citation scope.

### IDEA-20260808-040db9 — PARTIAL-OVERLAP + prior-art flag

`IDEA-20260805-70aa6e` already establishes that SNOVA's oil space is an A-module (the record
discloses this and discriminates on "equations, not objects" — that discrimination is fair).
The stronger concern is external and I cannot settle it offline: **to my recollection, the
mechanism "the oil space is an F_q[S]-module, therefore the attacker obtains additional
equations for a single oil vector" is the core of published improved cryptanalysis of SNOVA
(the Beullens-line work of 2024–2025, plus Ikematsu et al.)**, not a session derivation. The
record labels it "DERIVED THIS SESSION", prices `honest_prior_of_survival` at 0.75 for a rank
gain, and states in `dominated_by` that it is "dominated by the reported SNOVA attacks (which
this program has not read)". That last sentence is the honest one and should be promoted to
the claim: the required first step is the literature read, not the toy instrument. Marked
**unadjudicated** — web search unavailable.

Bookkeeping defect shared with `c959c7`: 040db9's `discriminated_from` says "M1-08 (this
file)" while c959c7's says "M1-06 (this file)", and both refer to the other by an internal
label with no IDEA ID. A future reader cannot resolve either pointer.

---

## Notes on the seven NOVEL records (what I checked, and what to fix)

(`ea3b4f` is listed last for convenience; its verdict is PARTIAL-OVERLAP, above.)

* **06aae4** (AES DS-MITM memory accounting). Internally consistent; the three-convention
  discipline and the machine-specificity caveat are correct. One fix: its `proof_search_map`
  makes "baseline reproduction is the unit-cost convention, which must reproduce the standard
  accounting exactly" the load-bearing control, while `assumptions` forbids relying on "a
  specific published table of complexities". The control cannot be run under the record's own
  rule. Either the reproduction target must be stated as a re-derived formula with its
  derivation committed, or the rule must be relaxed for the reproduction arm only.
* **5158fa** (CM ray class field). The derivation checks: `n = (N, π−1)` gives `π ≡ 1 (mod n)`
  by construction; `(π)` is a principal prime of O coprime to n; the Artin symbol of a
  principal prime is the class of its generator in `(O/n)*/im(O*)`; hence trivial, hence
  complete splitting. `[K_n:K] = h(O)(N−1)/w ≈ p^{3/2}` is right (h(O) ~ √p, N ~ p). Caveat
  worth recording in the record itself: the "single computable equality" is true by
  *definition* of n, so prediction 1 (f = e = 1 in 100% of samples) cannot fail and is not a
  test. The NEGATIVE CONTROL with an unrelated modulus m is the only arm that can come out
  either way, and it should be promoted to the primary prediction.
* **5d8b39** (HQC DFR factorisation). Independently verified: n = 17669, n₁n₂ = 46·384 =
  17664, truncation l = 5, inner code [384,8,192]; and with the quoted p_i = 2^-10.79 and RS
  [46,16] (δ=15), `Pr[Binom(46,p_i) > 15] = 1.05e-40 = 2^-132.8`, so the claim that the
  40-to-80 orders of magnitude sit in the outer binomial tail is arithmetically sound. Scope
  note: its own `dominated_by` concedes Table 11 already reports inner simulations at true
  block lengths, so "moves the measurable fraction from zero to two of three factors"
  overstates — the new objects are the p_i(w) **grid** and the profile law.
* **baf8bc** (memory-capped ISD frontier). Sound; controls (unconstrained reproduction,
  monotonicity, sublinear-weight null) are the right ones. Note that same-round `a3bcf0`
  argues structurally that the representation gain is a small constant at Classic McEliece's
  t = 64–128 even with free memory, which pre-empts the McEliece point of Claim A; `a3bcf0`
  discloses the relationship from its side.
* **e5f947** (ML-DSA accept fibre). Sound, with a mandatory baseline-invisible positive
  control. It should cite `KN-FIND-720727` (one of the five barriers invisible in
  `KNOWLEDGE_BARRIERS.txt`), which records that the ML-DSA formal proofs are scoped to
  cryptographic adversaries — adjacent support for the record's premise that the algebraic
  argument does not cover the encoding, not a duplicate and not a closure against it.
* **c959c7** (QR-UOV A-bilinearity control). The derivation is right: A-bilinearity gives
  `P'(x, t^j x) = t^j P'(x,x) = 2 t^j P(x)`, vacuous in char 2 and a multiple of the original
  otherwise. One weakness: the plain-UOV arm's "forced value" is vacuous ("with no algebra
  there is no multiplier to adjoin beyond the identity"), so it calibrates only against coding
  errors, not against the effect; the SNOVA positive arm carries all the instrument's power.
* **750ead** (SQISIGN admissible-commitment locus). Sound and honestly scoped to a surrogate.
  But the predicted outcome (a) is derivable without the O(|V|²·|response space|) sweep: if
  the surrogate's response space contains isogenies of degree exceeding the graph's diameter,
  every vertex is reachable from the public key and |A| = |V| identically. Derive the forced
  value first and run the enumeration only as an instrument check against the rigged-verifier
  positive control. Its `dominated_by: n/a` is thin but defensible since no result is claimed;
  the p^{1/3+o(1)} baseline is consistent with sibling `19876e` and `KN-TECH-058`.
* **ea3b4f** — see partial-overlap section; no mathematical objection.

## Cross-cutting observations about the batch

1. **Internal generator labels leak into the ledger.** `E1-01`, `M1-06`, `M1-08`, `C1-05`,
   `X1-01`/`X1-02`/`X1-03`, `S1b-02`, `E2-07`/`E2-08` appear in `discriminated_from`,
   `dominated_by` and `target_complexity` fields of at least 9 records in this slice, with no
   IDEA IDs. Two of them (`M1-06`/`M1-08`) are used self-referentially by *both* members of a
   pair. These pointers are unresolvable for anyone who was not in the generating session, and
   they are exactly the fields the dedup process depends on.
2. **Two records of the same round contradict each other on a matter of fact** (`7c4e9d` vs
   `4f3ef4` on what Arm C is), and a third pair contradict each other on scope (`be161c` vs
   `e40da2` on whether the lattice family is inside the class). Nothing in the process caught
   this because generators screened against the *pre-existing* corpus only.
3. **Four records in this slice fail a control they themselves declared mandatory** (`a33400`
   c(4)=1; `be161c` corner reproduction; `e820d2` prediction 5 / the G table; `2b4581` D=0 for
   plain UOV). In every case the failing check is arithmetic and costs under a minute. A
   cheap pre-file gate — *evaluate your own declared controls on your own declared parameters
   before filing* — would have caught all four.

## What I actually checked

Corpus files read: `RESCREEN_BRIEF.md`, `slice1.txt`, all 19 assigned records in full,
plus (in whole or in relevant part) `IDEA-20260808-4f3ef4`, `-3f8a2b`, `-e40da2`, `-f332da`,
`-a3bcf0`, `-486ae2`, `-b188d0`, `-19876e`, and the titles of all 126 2026-08-08 proposals
(extracted programmatically for cross-round duplicate screening).

Knowledge records read: `KN-FIND-007` (full), `KN-TECH-057` (full), `KN-FIND-720727`,
`KN-FIND-860118`, `KN-FIND-002`, `KN-FIND-b7e091`, `KN-FIND-982fdf`, `KN-OPEN-001` headers.
Existence-checked: `KN-LIT-7605/7607/475`, `KN-OPEN-002/020`, `KN-FIND-006`, `KN-TECH-058`.
Ledger records read: `GOAL-ECTD-001.yaml`, `RQ-ECTD-001.yaml`.
Dedup corpus greps: `EXISTING_PROPOSALS.txt` (RQ-ECDSA-87625f rows), `REJECTED_TITLES.txt` and
`DEFERRED_TITLES.txt` (AES entries; ECDLP-IDEA-326/379), `KNOWLEDGE_BARRIERS.txt`
(multivariate).
Experiment artifacts read: `experiments/EXP-SEMAEV-f48dd1/implementation/full_grid.py`
(lines 180–290, i.e. `arm_c_random_predictor`) and
`runs/RUN-SEMAEV-f48dd1-grid/raw-results.json` (all 40 cells).

Computations run (scripts in the session scratchpad; outputs quoted verbatim above):
1. AES round function implemented from scratch (S-box built by field inversion + affine map,
   verified against S(0x00)=0x63, S(0x01)=0x7c, S(0x53)=0xed); integral balancedness of
   1-byte-active Λ-sets at r=3 and r=4 for all four diagonal positions, and of 2-byte-active
   sub-cosets at r=4. **[a33400]**
2. Exact KN-FIND-007 means `C(B+m−1,m)/N` at B = p^{eps/m} for p ∈ {2^22, 2^64, 2^256},
   m ∈ {3,4,5}, eps ∈ {0.5,0.75,1.0}. **[0e9fa1]**
3. sinc evaluation and the corner-reproduction arithmetic of the HNP frontier at
   N ∈ {160,256}, l ∈ {1,2,3,4}; plus the record's own null (sinc(1)=0) and decay controls.
   **[be161c]**
4. `e` and `G` for all published MAYO/UOV/SNOVA-flattened sets and all six toy cells named in
   the record. **[e820d2]**
5. Exact GF(p) Gröbner bases of `I_R = <S_3(x1,x2,xR), f_V(x1), f_V(x2)>` on real curves at
   p=1009, B ∈ {5,10}, m=2, for 8 random targets and 6 planted-decomposition targets
   (sympy 1.14, lex and grevlex). **[afe4ce]**
6. HQC parameter arithmetic and the outer binomial tail `Pr[Binom(46, 2^-10.79) > 15]`.
   **[5d8b39]**
7. `D = (N−2O)·log₂q − claimed level` for the four published plain-UOV sets and the four MAYO
   sets. **[2b4581]**
8. `binom(τN,τ)` vs `N^τ` at four (N,τ). **[aa551f]**
9. Aggregate statistics over all 40 cells of RUN-SEMAEV-f48dd1-grid: A/B relation equality,
   zero-yield count for Arm C, `candidates_verified_C/|F|²`. **[7c4e9d]**

**Could not verify / left open:**
* All external-literature novelty. Web search and fetch unavailable. This bites hardest on
  `040db9` (SNOVA module-structure attack), `be161c` (eprint 2024/296), `baf8bc`
  (memory-constrained ISD literature) and `aa551f` (the one-tree line) — all four records say
  so themselves.
* `06aae4`'s and `a33400`'s citations of committed campaign measurements (the r=6 recovery at
  69.39 s vs ~25 s brute force; MEAS-GOAL-AES-002-002 at 53 s) were not traced to their batch
  artifacts; only the AES mathematics was checked.
* `5d8b39`'s Table 11 values (p_i = 2^-10.79 / -14.14 / -11.30) come from `KN-LIT-b9e1a8` and
  were used as given; I checked only that they are *consistent* with a 2^-128-class DFR at the
  real HQC-128 parameters, not that they are the spec's numbers.
* `c959c7` and `040db9` both depend on specification reads that have not happened
  (A-bilinearity of QR-UOV as actually constructed; SNOVA's A-stability). My checks are of the
  algebra as the records state it, not of the schemes as specified.
* Whether MAYO's own design rationale already contains the `e > 0` observation (`e820d2`'s own
  0.35 prior) — that is a spec read, not refutable from here. My refutation of `e820d2` is of
  its closure and prediction 5 only, and is independent of that question.

## Next concrete action

Before anything in this slice is scheduled: run each record's own declared controls on its
own declared parameters as a filing gate. That single step, at under a minute of arithmetic
per record, disposes of `a33400`, `be161c`, `e820d2` and `2b4581`. Then re-run the
adversarial pass over the remaining five slices with the same move as its primary instrument —
this slice's kill rate came almost entirely from evaluating the record's prediction at the
point where the record itself already fixed the answer.
