# R4 — derivation note: the reported invariants are functions of the
# decomposition POINT SET and of a fixed integer top form, and nothing else

Label: **derivation**. Red team, TASK-20260904-8c5f97, EXP-PFDR-fd901a.

## 1. The two halves

From the R1 note §5 and the R2 note §1, at (m, d, s) = (2, 2, 3):

* **full_rank(D)** = rank of the 0/1 evaluation matrix of the squarefree
  monomials of degree D - 4 at the points of supp(S~) ⊂ {0,1}^6. It depends on
  S~ **only through its zero set** Z(S~) = {v : S~(v) = 0}, because multiplying
  the columns by the nonzero values S~(v) does not change a rank.
* **top_rank(D)** = rank of multiplication by the parameter-free integer form
  T = 16 Q_1 Q_2, i.e. **1, 2, 1** at D = 4, 5, 6 over every field of
  characteristic ≠ 2.

Every other reported invariant is a function of these two:
fall_dim = full − top, syzygy_dim = rows − full, deficit_series = pred − full,
d_ff = first D with fall_dim > 0, and the cumulative variants likewise.

## 2. Consequence for CTRL-CONFOUNDERS-NAMED (i), the cb8e46 CRT artifact

IDEA-20260830-cb8e46 (A) states that under the split membership encoding the
decomposition ideal **is** the vanishing ideal of the point set
Z = {grid points where the summation polynomial vanishes}, so every ideal-level
observable is determined by Z. The digit presentation at d = 2 is the same
object with the grid V^m replaced by {0,1}^{ms}: the membership quotient is
F_p[a]/(a_i^2 − a_i) ≅ F_p^{64} by CRT once per digit, and the ideal generated
by S~ in it is exactly {f : f vanishes on Z(S~)} = I(Z(S~)).

The contract and `analysis.md` exclude this confound by category —
"only generator-level observables (rank profiles) are read here". §1 shows the
category argument does not hold for this presentation: **four of the five
reported invariants are functions of the CRT point set Z(S~)**, and the fifth is
a constant of the digit map. The confound is therefore *not* excluded by
construction; it is excluded, if at all, only by the separate fact that the
planted design pins |Z(S~)| = 2 far below every threshold that could move a rank
(16, 32, 64). Objection RT-O6.

Nothing here contradicts a recorded integer. What it changes is the *label*:
the (2,2,3) profile is a two-number summary (|Z(S~)| coarsened at 16/32/64, plus
the fixed top form), not a measurement carrying curve, target or prime content.

## 3. The discriminating mutations (`scripts/r4_pointset_mutation.py`)

Run on the recorded (A, B, x_R) of all 40 Semaev draws at each of the three
primes, with my own code:

| mutation | construction | predicted | observed (40/40 at each of p = 4099, 2^64−59, P-256) |
|---|---|---|---|
| **M1** zero-set- and support-preserving | random coefficients on the same 49 monomials, constrained to vanish at exactly the same cube points, degree still 4 | full_rank unchanged; top_rank@5 → 6 | profile **[(0,0),(1,1),(6,6),(15,1)]** = the recorded NULL arm's profile, exactly |
| **M2** top-form-preserving, structure-destroying | keep the degree-4 part 16 Q_1 Q_2, randomise every sub-top coefficient — **no curve, no target, no decomposition, no Semaev polynomial** | the Semaev profile | profile **[(0,0),(1,1),(6,2),(15,1)]** = the recorded SEMAEV arm's profile, exactly |

**M2 is the null-object control (`docs/inventor-protocol.md` §3) this contract
does not contain, and the null object matches the finding.** The entire recorded
Semaev-minus-null offset (top_rank@5 −4, fall_dim@5 +4, d_ff −1) is carried by
the fixed integer monomial top form of the digit map at (m, s) = (2, 3), and by
nothing else. It is p-independent because that form is p-independent away from
2 — which is a statement about the digit encoding, not about the curve, the
target, the Semaev polynomial beyond its top monomial x_1^2 x_2^2, or the prime.

## 4. Nodal cubic and named curve, derived

* **Non-curve cubic.** (A, B) enter S~ only below the top degree (R1 note §1),
  so the singular-cubic arm has the identical top half by construction; and its
  planted root gives exactly 2 zeros on the cube at all three primes (verified,
  `out/r4_pointset_mutation.json`, `noncurve_zero_counts` = {2: 40} per prime),
  so its full half is identical too. **Agreement at every prime is forced**, and
  no sub-top term can move the profile unless it produces ≥ 16 zeros — which the
  exhaustive x_R search of the R1 note rules out for every curve tested at
  p = 4099. The contract's reading ("the p-axis carries nothing about the curve
  at this shape") is correct and derivable, not measured.
* **Named NIST P-256 curve.** Same two determinants: identical top form, and
  |Z| = 2 from the planted target. It adds nothing at fixed shape beyond a
  public-parameter instance, exactly as the plan expected.

## 5. Null-seed mixing (D3) — the executor's justification is correct

The Semaev generator has the same 49-monomial support in **all 40 draws at every
prime** (`out/r2_forced_profile.json`, `bookkeeping.semaev_term_counts` = {"[49]": 40}
per prime), and `support_matched_system` draws coefficients from the seed and the
support only. With the contract's verbatim seeds {7,11,13,17,19} the 200 null
draws per prime would have collapsed to **5 distinct polynomials**. The mixed
seed `hint(EXP_ID, "null", p, curve_seed, target_seed, ns)` gives 200 distinct
values per prime with 0 collisions (verified per prime). The deviation is
justified and strictly increases the null arm's information.

## 6. Output-degree proxy (IDEA-20260807-899c5e) — excluded, confirmed

`run_experiment.py` and `analyze.py` contain no Groebner basis, no quotient
dimension, no solution count and no solving degree; the metric set is exactly
{full_rank, top_rank, fall_dim, syzygy_dim, deficit_series} plus d_ff derived
from fall_dim, and the binomial-interval helper. Timings are recorded and never
compared. This confound is genuinely excluded by construction.
