# TASK-20261003-3c8ea2: zero-run design of the single-bucket-gain ladder for KN-OPEN-91d4f6

Producer: idea-generator (independent session; not TASK-20261001-9b3e70, and not
either reviewer of REVIEW-SEMBIN-20261002-c7e1d4). **Zero scientific runs. No
G(M), pi_c(d) or bucket statistic was computed for any curve at any scale. Every
number below marked "scratch" is hand arithmetic from formulas and has not been
measured. Nothing is approved, nothing is committed, and no status moves. This
document says nothing about the security of any curve, in either direction.**

Drafts: `proposed-records/IDEA-20261003-5a2c9e.yaml`,
`proposed-records/H-SEMBIN-9c41f7.yaml`,
`proposed-records/EXP-SEMBIN-e2b864/specification.yaml` (status
`review_required`, no `approved_by` key).

---

## 0. One-page summary

**Question (KN-OPEN-91d4f6, asked on `<P>`).** Does any poly(n)-computable
F_2-linear x-functional filter `h_j : <P> -> F_2^j` (M = 2^j) on a toy ordinary
binary curve show a level-1 single-bucket gain `G(M) = M * max_{c,d} pi_c(d)`
that grows with M? Alternatively, does every tested family stay with the nulls,
as the prime-field ladder did (KN-FIND-ffe1df, RT-EXP-1)?

**Observable and bias correction.** The observable is `G = M_eff * max_{c,d}
pi_c(d)`, with `pi_c(d)` exactly KN-FIND-ffe1df's per-bucket merge rate, never
the averaged eps. The max over M^2 cells of empirical frequencies is biased
upward, so the design removes the bias with a **split-sample, cross-fitted
estimator**. The best cell `(c*, d*)` is selected on half A of the pairs, and
`pi` is estimated at that cell on the disjoint half B; the halves are then
swapped and the two estimates averaged. The held-out estimate is unbiased for
the true rate at the selected cell. Every family, null, and control goes
through the identical code path, with identical blocks, halves, eligibility
rule (at least 100 pairs per conditioning row) and M_eff convention.
Uncertainty comes from 8 independent blocks per curve (24 per n), which also
absorbs the correlation between nested rungs. The uncorrected in-sample G is
reported for continuity with RT-EXP-1 but never decides anything.

**Nulls (both required; a family "trips" only if it separates from both).**
- **N-SHA**: the first j bits of SHA-256(key || x(Q)), with the same M,
  negation-invariant like the x-filters.
- **N-MM**: the matched-marginal shuffle `h o sigma`. Here `sigma([k]P) =
  [phi(k)]P`, and phi is a keyed pseudorandom permutation of Z/l that commutes
  with negation. So `h o sigma` has exactly the level-set sizes of `h` on `<P>`
  and no additive structure. This is RT-EXP-1's shuffle on the sampled stream,
  and it is the null that exposed popcount and digit-sum as false positives.

**Controls.**
- **Baseline fixture on E(F_p), first.** RT-EXP-1's RNG-free cells at
  p = 65539 (M = 40), "x mod M" = 1.0859 and "sha [null]" = 1.0742, are
  reproduced by the committed script and by the new exact code. The new sampled
  estimator must then agree with the exact pi at its selected cell.
- **Positive controls on E(F_{2^n}), flagged as domain E.**
  - `Tr(x)`: exact G = 2 at M = 2.
  - The Z/4 class by one point halving on h = 4 curves: exact G = 4 at M = 4.
  - `Tr(sqrt(B)/x)` (an Artin-Schreier identity of the curve): exact G = 2.
  - Tr bit plus j-1 SHA bits: G = 2 at every j.
- **The same controls on `<P>`** must read exactly 1. Any other reading is an
  instrument defect.
- **Planted sensitivity on `<P>`, at both rules.**
  - RT-EXP-1's dlog mixture (`theta = M^{-1/3}`, predicted G about 1.5, flat).
  - An XOR-native mixture built from half-interval dlog bits (per-bit match
    probability 3/4, from a derivation), at a flat level and at the growth
    edge `G = M^{0.2}`.

**Ladder (n, j) and sample size.**
- n is in {19, 23, 31, 41}, with 3 ordinary non-Koblitz curves per n (cofactors
  2, 4, 4).
- `j_max(n) = min(10, floor(0.4 log2 l_min))`, giving j <= 6, 8, 10, 10
  (design figures). That puts 4 n per j for j <= 6, 3 n for j = 7..8, and 2 n
  for j = 9..10.
- S = 2^30 i.i.d. pairs per curve on `<P>`.
- The decision slope is fitted over the top 4 rungs of each n. Its planning
  standard error is `0.354 * 2^{j_top} / sqrt(S)` (scratch; section 6).
- A Bonferroni half-width of at most 0.05 per curve needs `S >= 2^{8.69 + 2
  j_top}`. That allows j_top = 10 at S = 2^30 (2^28.7 needed) and excludes 11
  (2^30.7 needed).
- The 0.4 rule keeps the finite-population null floor below about 0.07, so
  null slopes stay well under the threshold.

**Decision rule.** beta is the top-segment slope of log2 G_sc per doubling of M.
- **REFUTED (growth).** For some declared (family, rule), at 2 or more n
  (including n = 31 or n = 41): `beta_F >= 0.10`, and the Bonferroni CI of
  `beta_F - beta_null` excludes 0 against both nulls. Both nulls' slopes must
  have upper CI below 0.10. **Routes to the Coordinator before any
  interpretation, as possible rule-12 material.**
- **BOUNDED-EXCESS.** No growth, but a top-rung excess of more than 0.10 over
  both nulls at 2 or more n. Routes to the Coordinator; this is a
  constant-factor reading.
- **PASS** (the null prediction holds). All gates pass, and neither of the
  above occurs.
- **INCONCLUSIVE.** Any of:
  - the fixture is not reproduced;
  - a positive control is missed;
  - a control is alive on `<P>`;
  - a planted control fails its gate;
  - the nulls are floor-dominated at too many n.
- **INVALID.** Custody or arithmetic gate failure; nothing is read.

**Draft ids** (hand-chosen tokens, no shell; collision greps clean; checks owed):
IDEA-20261003-5a2c9e, H-SEMBIN-9c41f7, EXP-SEMBIN-e2b864.

**Ceiling.** Level 1 only. A level-1 result does not close tree levels >= 2.
Theorem C already excludes exact filters on `<P>`, so only the approximate
question is measured. The families are declared, so the list is incomplete.
The tier is toy (n <= 41).

---

## 1. The observable, exactly, and the selection-bias correction

**Definition (KN-FIND-ffe1df; not redefined here).** For a label `h` with
values in `[M]` and a combining rule family `{f_d}`,

    pi_c(d) = Pr[ h(Q+R) = c | f_d(h(Q), h(R)) = c ],   Q, R uniform in <P>, Q+R != O
    G       = M_eff * max_{c,d} pi_c(d)

where `M_eff` is the number of labels actually observed on the sample. A filter
earns no credit for buckets it never fills, which is RT-EXP-1's (H6) convention.
**Convention change, disclosed:** when `M_eff = 1` (a constant label) this design
sets `G := 1`; RT-EXP-1 returned NaN. Labels are not remapped onto
`0..M_eff-1`. RT-EXP-1 remapped, which changes the Z/M arithmetic when buckets
are empty. Every declared family has `M_eff = M` unless the degeneracy audit
(section 3) flags it. The fixture cell has `M_eff = M = 40`, so it is
unaffected.

**Rules.** Both rules below are fixed before any run and both bear on the
decision, for every family:

- **RULE-A** (KN-FIND-ffe1df's rule verbatim): `f_d(a, b) = a + b + d mod 2^j`,
  where labels are integers with bit i equal to functional i+1.
- **RULE-X** (the group law of F_2^j): `f_d(a, b) = a XOR b XOR d`. This is the
  only rule under which an F_2-linear label can be a homomorphism. It is the
  rule the trace obeys on E.

The max over the offset d is part of the observable, because the attacker picks
d after seeing h. A third statistic, the unrestricted-rule envelope `G_U = M_eff
* max_{a,b,c} Pr[h(Q+R)=c | h(Q)=a, h(R)=b]`, is computed at j <= 5 only. It is
the statistic the BINSTD lineage uses, and it is secondary and never decides
anything.

**Computing it from one histogram.** For each pair, form the combined label
`e = h(Q) op h(R)` (op is + mod 2^j or XOR) and the sum label `c' = h(Q+R)`.
Accumulate `H[e, c']`. Then `pi_c(d)` is `H[e, c] / H[e, .]` at `e = c - d`
(or `c XOR d`), and the max over (c, d) is the max over (row e, column c) of
`H[e,c]/H[e,.]`. Labels are nested in j through the low bits, so the j-rung
histogram is a marginal of the j_max histogram, for both rules. One stream of
pairs serves every family, null, and rung.

**Split-sample, cross-fitted estimator (the correction).** The pairs of a
curve's stream are indexed t = 0..S-1.
- Block `b = t mod 8`. Half `A` if `floor(t/8)` is even, else half `B`.
- In each block, for each (label, rule, j):
  1. Rows e with at least 100 pairs in **both** halves are eligible; the count
     and mass of excluded rows are reported.
  2. **A -> B:** take `(e*, c*) = argmax` of `H_A[e,c]/H_A[e,.]` over eligible
     rows and all c, with ties broken by the least (e, c). Then
     `pi_hat_AB = H_B[e*,c*]/H_B[e*,.]`.
  3. **B -> A** symmetrically.
  4. `G_sc(b, j) = M_eff * (pi_hat_AB + pi_hat_BA)/2`, with `G_sc := 1` when
     `M_eff = 1`.

The curve-level `G_sc(j)` is the mean over the 8 blocks, with standard error
`sd/sqrt(8)`. Each held-out estimate is unbiased for the population rate
`pi_{c*}(d*)` of the cell selected on independent data, so the upward selection
bias of a max over M^2 noisy cells is removed. What remains is the true rate of
a selected cell, which is <= the true max. That is conservative for detecting a
signal, and it is applied identically to the nulls.

**What the correction does not remove, and why that is correct.** A fixed
random-like filter on a finite group has a genuine finite-population
max-bucket excess of about `sqrt(2 ln M * M / l)` (scratch). That is a real
property of that filter on that curve, which an attacker could also use. It
is not sampling noise, so it is not corrected away. It is present in N-SHA and
N-MM at the same scale, and the decision compares families with nulls by
paired, block-wise differences on the same pairs.

**Translation of the card's wording.** "G(M) decays with the nulls" referred to
RT-EXP-1's in-sample G, whose excess decays in p. Under the corrected estimator
the nulls read `G_sc` close to 1 at every rung, with slope near 0. The null
prediction becomes: **the family tracks both nulls in level and in ladder
slope.**

## 2. Mechanism: what the XOR-rule gain is, and the lossy-projection test

**Derivation (this design; elementary; unreviewed).** On `y^2 + xy = x^3 + A x^2
+ B`, a line `y = lambda x + c` meets the curve where `x^3 + (A + lambda^2 +
lambda) x^2 + c x + (B + c^2) = 0`. So for any Q, R with Q + R != O and chord
(or tangent) slope `lambda`,

    x(Q) + x(R) + x(Q+R) = lambda^2 + lambda + A.

Since `Tr(alpha lambda^2) = Tr(alpha^{1/2} lambda)`, for every `alpha`

    Tr(alpha x(Q)) + Tr(alpha x(R)) + Tr(alpha x(Q+R)) = Tr(gamma lambda) + Tr(alpha A),
    gamma = alpha + alpha^{1/2}.

Consequences:

1. **The exact case is exactly gamma = 0, that is alpha in {0, 1}.** With
   alpha = 1 the right side is the constant `Tr(A)`, so `Tr(x) + Tr(A)` is a
   homomorphism `E -> F_2`. That is H-SEMBIN-83a856's E/2E map, here in one
   line. Every other alpha gives a lambda-dependent error bit.
2. **For an F_2-linear label `h = L_alpha(x)`**, the RULE-X error vector is
   `w(Q,R) = h(Q) XOR h(R) XOR h(Q+R) = L_gamma(lambda_{QR}) XOR L_alpha(A)`.
   Hence

       G_X = M_eff * max_{s,d} Pr[ L_gamma(lambda_{QR}) = d | L_alpha(x_Q) XOR L_alpha(x_R) = s ].

   **The XOR-rule single-bucket gain of an x-linear filter is the
   predictability of a j-bit linear projection of the chord slope from the
   XOR of the two input labels.** A gain needs `(L_alpha(x_Q + x_R),
   L_gamma(lambda))` to be non-equidistributed on `<P> x <P>`. Those are
   additive-character sums of rational functions of (s, lambda) under the
   Artin-Schreier conditions that define the pair set and the `<P>`
   membership (Tr and depth-2 conditions). This is precisely the
   "characteristic-2 Artin-Schreier degenerate cases" surface of
   KN-OPEN-91d4f6, made concrete.
3. **The diagonal triple sums are free.** `T_u = E[(-1)^{u . w}]` is the Walsh
   transform of the histogram of w, which is the row-collapsed RULE-X
   histogram. It is reported as diagnostic SPEC-T: KN-FIND-ffe1df's T_t at
   characteristic 2.

**Lossy-projection test, against the named operation set.**
- **Object.** The label h (j of n bits of x, sign discarded).
- **Operation set Sigma.** Translation by an element of the partner list, which
  is the merge of one Wagner level.
- **Test.** The retained part propagates deterministically iff w is a function
  of `(h(Q), h(R))`. By the identity, that holds iff `gamma = 0` on the span,
  i.e. the span is inside {0, 1}. That case is the trace: lossy and
  Class I partial-action on E, and constant on `<P>`. For every non-degenerate
  span the test fails, as Theorem C (KN-FIND-ffe1df) requires on `<P>`.
- **Placement.** The object is **Class II, branching**. The experiment reads its
  (L, b) meter (IDEA-20260802-002) at one level: L = j bits retained,
  `b = M / G`.
- **The question.** Does b grow more slowly than M?

The test costs no compute and is recorded here, not in the experiment.

**Representation and operation pair (search bias 6).** The representation is
R1 (x in F_{2^n}; polynomial basis, normal basis, and 1/x), and Sigma is
pairwise translation at one merge level.

**Named off-limits primary lenses for this session** (heavily mined):
- prime-field interval and bit-window filters (KN-FIND-ffe1df families A, B);
- quadratic and higher residue characters (families C to G, D);
- popcount and digit sums (I, J);
- Koblitz Frobenius-invariant filters on the full group E (the BINSTD lineage,
  IDEA-20260926-136bd3 to EXP-BINSTD-811a2e).

None is the primary object here. KN-OPEN-019 (no written ECDLP object
enumeration) still stands, so the family-to-object mapping above is a sketch.

## 3. Filter families and combining rules (declared, closed, fixed before any run)

Each family defines ten functionals `ell_1..ell_10`. `h_j(Q)` has bit i equal to
`ell_{i+1}(x(Q))`, i < j, so the families are nested.

| id | functionals | structure |
|---|---|---|
| LR-A | `Tr(alpha_i x)`, alpha_i from DRBG label `...|alpha|LR-A|<curve>|i` | random |
| LR-B | same, independent draw (`...|LR-B|...`) | random (second draw, spread across alpha) |
| LP-LO | polynomial-basis coefficients of z^0..z^9 | structured, low coordinates |
| LP-HI | polynomial-basis coefficients of z^{n-1}..z^{n-10} | structured, high coordinates |
| LN | normal-basis coordinates c_0..c_9, for the least normal element theta | structured; normal basis (always exists) |
| LI | `Tr(beta_i / x)`, beta_i from DRBG | 1/x-linear, Artin-Schreier-adjacent |

**Degeneracy audit (Stage 0, linear algebra, no curve data):**
- **LR-A, LR-B.** Redraw until the ten alpha are F_2-independent and 1 is not in
  their span.
- **LI.** Redraw until sqrt(B) is not in the span.
- **LP-LO, LP-HI, LN.** Report whether 1 is in the span, and keep the family as
  declared. A flagged structured family reads a constant bit on `<P>` (M_eff
  halves), and that is reported, not "fixed".
- **Stage 1, empirical.** Every character `u` in F_2^j minus 0 of every family
  with `|E chi_u| > 0.5` on half A is flagged as degenerate.

**Rules per family.** RULE-A and RULE-X for every family, both decision-bearing,
with the offset maximised as part of G. The rule set does not depend on data.

**Not declared (out of scope, with revisit).**
- Koblitz curves and Frobenius-equivariant filters (the BINSTD lineage covers
  them on E).
- y-dependent, nonlinear, and target-dependent filters.
- Composites with exact components.
- Levels >= 2.
- Revisit: a family with REFUTED or BOUNDED-EXCESS here, or a Coordinator
  request for a Koblitz-on-`<P>` arm.

## 4. Nulls

- **N-SHA.** `h(Q)` = bits 0..9 of `SHA-256("EXP-SEMBIN-e2b864|sha|<curve>|" ||
  x(Q) as ceil(n/8) big-endian bytes)`. It is the same M, nested, and a function
  of x only, so it is negation-invariant like the families.
- **N-MM(F)**, one per family and per planted control: `h_F(sigma(Q))`, with
  `sigma([k]P) = [phi(k)]P`.
  - For k in [1, (l-1)/2], `phi(k) = s(k) * psi(k)`, where psi is a keyed
    cycle-walking Feistel PRP on [1, (l-1)/2] (4 rounds; SHA-256 or keyed
    BLAKE2b, declared in the manifest) and s(k) is a keyed sign. Then
    `phi(l - k) = l - phi(k)`.
  - sigma is therefore a bijection of `<P> \ {O}` that commutes with negation.
    `h o sigma` has **exactly** the level-set sizes of h over `<P>`, and sigma
    is not a homomorphism.
  - One sigma per curve serves every family. The cost is three extra
    scalar multiplications per pair: `phi(k1)`, `phi(k2)`, `phi(k1 + k2)`.
  - **Not an automorphism.** A multiplier map `k -> u k` would preserve G
    exactly. RT-EXP-1's x([2]P) row equals its x mod M row for exactly that
    reason, so such a map is a forbidden "shuffle".
- **Identical procedure.** Every null passes through the same stream, blocks,
  halves, eligibility, M_eff convention, rules, rungs, and slope fit as the
  families. Family-versus-null comparisons are paired block-wise.

## 5. Controls and baseline fixture

**Order of execution.** FX, then curve admission, then the arithmetic and
domain gates, then the E-domain controls, then the `<P>` controls and planted
controls, then the families. No family label is read on a curve before every
earlier gate on that curve and every run-level gate has passed.

**FX: the RT-EXP-1 regression fixture on E(F_p), before any binary cell.**
- **FX-1.** Run `analysis/o2-sum-compatible-filters/rt_exp_1.py` read-only from
  its directory. Its printed row "x mod M" must show 1.0859 at 65539, and its
  row "sha [null]" must show 1.0742 at 65539. Both cells are RNG-free.
- **FX-2.** The new exact whole-group statistic, written independently: all N^2
  pairs, the RULE-A of RT-EXP-1, O included with x = 0 as RT-EXP-1 does,
  M = round(N^{1/3}) = 40. It is computed on the three curves `curves_near(65539,
  3)` selects, and the means over the three must match 1.0859 and 1.0742 within
  5e-5.
- **FX-3 (estimator validation).** On each fixture curve and in each direction,
  the sampled split-sample estimator for "x mod M" at S_FX = 2^26 index-sampled
  pairs is checked. Its held-out estimate must lie inside its own 99.9% Wilson
  interval around the **exact** pi at the selected cell, taken from FX-2's
  table: 6 checks, 0 failures allowed. The naive in-sample sampled G is
  reported beside the exact G.
- **FX-4 (recorded, not gating).** The exact G of the planted constructions of
  this design, on Z/l at the n = 19 and n = 23 values of l (j <= 6, by FFT over
  Z/l; no curve). Each is compared with its formula below.
- A failure of FX-1, FX-2 or FX-3 makes the experiment **INCONCLUSIVE**, and
  nothing else is read.

**Positive controls on E(F_{2^n})** (stream S_E = 2^24 pairs per curve, uniform
on E via `[k]P + [t]T_h`; **flagged domain E**):

| id | label | rule, M | must read |
|---|---|---|---|
| CE-TR | `Tr(x) + Tr(A)` | X, 2 | G = 2 exactly; the selected cell has zero violations |
| CE-Z4 | Z/4 class (h = 4 curves): b0 = Tr(x)+Tr(A); b1 = Tr(y1 + (lam+1) x1) on P1 = P - b0 T4, lam^2 + lam = x1 + A; class = b0 + 2 b1 | A, 4 | G = 4 exactly |
| CE-AS | `Tr(sqrt(B)/x)` | X, 2 | G = 2 exactly |
| CE-NEST | Tr bit, then j-1 SHA bits | X, j = 2..6 | within 4 SE of 2 at each j |

- **Two identity gates.** On every E-stream point with x != 0, `Tr(sqrt(B)/x) =
  Tr(x) + Tr(A)`: 0 violations, by the Artin-Schreier identity `(y/x)^2 + y/x =
  x + A + B/x^2`. The halving presentation of CE-Z4 must equal the reference
  class `c` with `[l]Q = [l c] T4` on 10^4 points: 0 mismatches. The
  presentation is from IDEA-20261001-39014f D5 and EXP-BINSTD-c9c8a2 DF-6
  (internal).
- **Chord gate G-CHORD.** On 10^4 pairs of each stream, the RULE-X error vector
  w of LR-A equals `L_gamma(lambda) XOR L_alpha(A)`, computed from the chord
  slope: 0 mismatches. This checks the filters and the group law at once.

**The same controls on `<P>`** (the main stream) must read **exactly 1**:
- CP-TR, CP-Z4 and CP-AS are constant on `<P>`, so M_eff = 1 and G = 1.
- CP-NEST has a constant Tr bit plus j-1 SHA bits, so M_eff = 2^{j-1}. It must
  read like N-SHA: the paired difference CI contains 0 at every rung, and so
  does its slope difference.
- **Domain gates.** Every sampled point satisfies `Tr(x) = Tr(A)` (0
  violations; this holds because `<P>` is inside 2E). `[l]Q = O` on every
  2^16-th point (0 violations).
- **Breaking the domain gates is INVALID.** A CP-* reading other than 1, with
  the domain gates intact, is an estimator defect and makes the experiment
  **INCONCLUSIVE**.

**Planted sensitivity controls on `<P>`** (dlog-based instrument controls, not
cheap filters). Each point's coin is keyed by its dlog k, and each control is
also read under N-MM.

| id | label at rung j | rule | predicted G (formula; FX-4 records exact Z/l values) | gate |
|---|---|---|---|---|
| PL-A-FLAT | with prob theta_j = M^{-1/3}: k mod 2^j; else the SHA bits | A | about 1 + theta^3 (M/2 - 1) = 1.5 - 1/M (RT-EXP-1's construction) | level >= 0.25 above both nulls at every j >= 3; slope < 0.10 |
| PL-A-EDGE | the same, with theta_j^3 = (2^{0.2j} - 1)/(2^{j-1} - 1) | A | about M^{0.2} | trips the growth criterion at every n |
| PL-X-FLAT | with prob theta_j: bits `[frac(xi_i k / l) in [1/4, 3/4)]`, i < j, xi_i from DRBG; else SHA; theta_j^3 = 0.5/(1.5^j - 1) | X | about 1.5 | as PL-A-FLAT |
| PL-X-EDGE | the same, with theta_j^3 = (2^{0.2j} - 1)/(1.5^j - 1) | X | about M^{0.2} | as PL-A-EDGE |

- **Basis of the PL-X formulas (derivation; continuum limit).** For the square
  wave `g(u) = sign(cos 2 pi u)`, `E[g(u1) g(u2) g(u1+u2)] = sum_m ghat(m)^3 =
  (16/pi^3) sum_k (-1)^k/(2k+1)^3 = 1/2`. That uses `beta(3) = pi^3/32`, which
  is recalled and checked by FX-4. So each bit obeys XOR w.p. 3/4, and the full
  gain is about `(3/2)^j` if the bits are independent.
- The independence assumption and the finite-l corrections are why FX-4
  records exact values, and why the gates require separation and tripping, not
  equality.
- Every planted control's N-MM must collapse to the null: paired difference CI
  containing 0. This is RT-EXP-1's "P2 to P2 SHUF" check.

## 6. Ladder and sample-size derivation

**Curves.**
- Ordinary `y^2 + xy = x^3 + A x^2 + B` with B not in F_2 (so not Koblitz).
- Roles: O2 (A = 1, h = 2), O4a and O4b (A = 0, h = 4).
- B comes from a SHA-256 DRBG, label `EXP-SEMBIN-e2b864|curve|<n>|<role>|<attempt>`.
- Accept iff `#E = h l` with l proved prime by complete trial division
  (l < 2^40, so at most 2^20 divisions).
- #E is counted by two routes: BSGS with uniqueness in the Hasse interval
  (confirmed on 20 points), and an exhaustive x-count at n <= 23.
- The field polynomial is the least-k irreducible trinomial, else the least
  pentanomial (Ben-Or test).

**Design figures, not results.** l_min(n) is about 2^{n-2} (the cofactor-4
roles).

| n | log2 l_min (approx.) | j_max = min(10, floor(0.4 log2 l_min)) | top segment J_top | theta-diagonal rungs (1/4, 1/3) |
|---|---|---|---|---|
| 19 | 17 | 6 | 3..6 | 4, 6 |
| 23 | 21 | 8 | 5..8 | 5, 7 |
| 31 | 29 | 10 | 7..10 | 7, 10 |
| 41 | 39 | 10 | 7..10 | 10, (13 not reached) |

Each j in 2..6 has 4 n, j = 7..8 have 3 n, and j = 9..10 have 2 n. The card's
requirement is at least two n per j.

**Why the 0.4 rule.** The finite-population null floor is about `f(n,j) =
sqrt(2 ln(2^j) 2^j / l)` (scratch, design heuristic HA-4). At the chosen top
rungs it is 0.064 (n = 19, j = 6), 0.037 (n = 23, j = 8), 0.005 (n = 31,
j = 10), and smaller at n = 41. Its slope over J_top is at most 0.022 per
doubling (n = 19), well below the 0.10 threshold. Without the rule, n = 19 at
j = 10 would put the null slope near 0.08. The measured null slopes gate this
(section 7).

**Precision (planning; scratch).**
1. With cross-fitting at G near 1, `SE(G_sc(j)) ~ M / sqrt(S)` per curve,
   because each direction has `Y ~ S/(2M)` pairs in its row and the two
   directions are averaged.
2. Then `SE(log2 G) ~ 1.443 M / sqrt(S)`.
3. The decision slope is a WLS fit of log2 G_sc on j over the 4 rungs of
   J_top, with fixed weights `4^{-(j - j_top + 3)}`. Its standard error is
   `1.40 sigma_0`, where sigma_0 is the lowest rung's SE.
4. With a 1.4x allowance for unmodelled inter-rung correlation:

       SE(beta) ~ 0.354 * 2^{j_top} / sqrt(S)

5. Each decision is a family-wise 0.05 over 12 (family, rule) cells, so
   z = 2.87. The requirement `z SE <= 0.05` per curve gives

       S >= 413 * 4^{j_top} = 2^{8.69 + 2 j_top}

   That is 2^28.7 at j_top = 10, which S = 2^30 meets, and 2^30.7 at
   j_top = 11, which it does not. **j_max = 10.**
6. Per-n pooled values: `SE(beta) ~ 0.0064` at j_top = 10. The decision uses
   the 24-block spread with `t_23 ~ 3.2`, so the half-width is about 0.020.
7. The top-rung level SE is 0.031 per curve and 0.018 per n, so a 0.10 excess
   is resolved at more than 3 sigma.

**Stream sizes.** S = 2^30 per curve on `<P>`, S_E = 2^24 per curve on E, and
S_FX = 2^26 per fixture curve. There are 12 curves.

## 7. Decision rule and routing (pre-registered)

For each (family F, rule rho, n), on the paired block statistics over the 24
blocks of the 3 curves:

- `beta_F`: the J_top WLS slope of log2 G_sc, averaged over blocks.
- `Delta_beta_SHA = beta_F - beta_SHA` and `Delta_beta_MM = beta_F -
  beta_MM(F)`, both block-paired.
- `Delta_top = G_sc^F(j_top) - max(G_sc^SHA(j_top), G_sc^MM(F)(j_top))`, also
  block-paired.
- CIs use `t_23` at two-sided level `1 - 0.05/12`.

**Null-floor gate (per n, per F).** The upper CI of `beta_SHA` and of
`beta_MM(F)` must be below 0.10. If not, that (n, F) is NULL-FLOOR and is not
read.

**REFUTE-n(F, rho).** All of:
- `beta_F >= 0.10`;
- the lower CI of `Delta_beta_SHA` is above 0;
- the lower CI of `Delta_beta_MM` is above 0;
- every gate at n passed.

**Outcomes.**
1. **REFUTED (growth).** REFUTE-n for the same (F, rho) at 2 or more n,
   including n = 31 or n = 41.
   **Routing:** write no interpretation; route to the Coordinator as possible
   rule-12 material. Reviewer escalation and independent replication come
   before any reading. Such a family is the candidate ingredient
   KN-OPEN-91d4f6 describes. **It is not an attack.**
2. **BOUNDED-EXCESS.** Not REFUTED, but for some (F, rho) the lower CI of
   `Delta_top` is above 0.10 at 2 or more n. The null prediction is falsified
   in level only.
   **Routing:** to the Coordinator. It is a constant-factor reading with no
   exponent stake as measured.
3. **PASS** (the null prediction holds). Every gate passes; at least 3 of the
   4 n are readable, including both 31 and 41; neither outcome 1 nor 2
   occurs. The scoped statement is in section 9.
4. **INCONCLUSIVE** (nothing is read as PASS). Any of:
   - FX-1, FX-2 or FX-3 fails;
   - a positive control is missed (CE-TR, CE-Z4 or CE-AS not exact, or CE-NEST
     off);
   - a control is alive on `<P>` (CP-* not equal to 1 with the domain gates
     intact);
   - a planted gate fails (a FLAT that does not separate or does trip, an EDGE
     that does not trip, or a planted N-MM that does not collapse);
   - fewer than 3 readable n, or 31 or 41 not readable.
   A partial REFUTE-n is still reported and routed. It is not a refutation.
5. **INVALID** (nothing is read). Any of:
   - curve admission is not met;
   - a domain gate is violated;
   - the Artin-Schreier identity, halving-presentation, or G-CHORD gate is
     violated;
   - code hash or DRBG record custody is broken.

Timeouts, crashes and watchdog checkpoints are infrastructure (AGENTS.md rule
3) and never evidence. A watchdog checkpoint resumes from the deterministic
stream.

**Secondary readings (reported; never decisive).**
- The in-sample G and its RT-EXP-1-style slope.
- The theta-diagonal G_sc minus null against log2 l.
- G_U at j <= 5.
- SPEC-T: max over u of `|T_u|`, at sampling SE about 2^-15, which resolves
  the Weil scale 2^{-n/2} at n <= 23. The prediction is "above the null" by
  the prime-field analogy (KN-FIND-ffe1df: T_x 34x T_sha), with low confidence.
- Selection consistency: the fraction of blocks that choose the modal cell.
- The marginal-floor value `M_eff max_c q_c`.
- Per-curve slopes with a Cochran Q heterogeneity test. That test addresses
  RT-EXP-1 limitation 5, the per-curve spread not separated from the trend.

## 8. Cost estimate (advisory; scratch, not measured)

- **Per `<P>` pair:**
  - Two fixed-base comb scalar multiplications (window 8: about 2 to 4 group
    additions each).
  - One addition for Q+R.
  - Three PRP-indexed scalar multiplications for N-MM (about 12 additions).
  - Six batched inversions for LI (x^{-1} on 6 points).
  - About 9 SHA-256 or keyed-hash calls.
  - Filter parities, which are negligible.
  - Total: about 20 to 26 group-addition equivalents.
- **Per curve:** 2^30 pairs, about 2^34.6 additions. Over 12 curves, about
  3.2e11 additions.
- **Wall clock.**
  - Compiled batch-affine arithmetic with carry-less multiply, at an assumed
    50 ns per addition: about 4.5 CPU-hours.
  - Vectorised numpy at an assumed 1 us per addition: about 90 CPU-hours.
  - Pure per-element Python is infeasible (more than 2 CPU-months). The
    contract therefore requires a vectorised or compiled implementation.
  - Hashing adds about 1e4 to 1e5 CPU-seconds.
  - The E-streams (12 x 2^24) and the fixture are minutes.
- **Memory.** uint16 histograms of 2^20 cells at j = 10, times 2 halves, 8
  blocks, and about 35 (label, rule) pairs, is about 1.1 GB. Rungs below
  j_max are marginals. The bound is 4 GB. If it would be exceeded, the
  deterministic stream is regenerated per label group (cost multiplies, and
  is recorded). S is never reduced.
- **Implementation:** medium. Binary field arithmetic, fixed-base comb, a
  cycle-walking PRP, the estimator, and gates. Roughly 600 to 900 lines.
- **Staged runs.**
  - RUN-1: FX plus curve admission plus every gate and the E controls
    (minutes to an hour).
  - RUN-2: n = 19, 23.
  - RUN-3: n = 31, 41.
  - PASS or REFUTED needs RUN-3. An early REFUTE-n at 19 or 23 is still
    reported and routed.

## 9. Method ceiling

- **Strongest certifiable statement (PASS).** On the 12 tested toy ordinary
  binary curves (n in {19, 23, 31, 41}), for the 6 declared x-filter families
  under RULE-A and RULE-X, the level-1, selection-corrected single-bucket gain
  on `<P>`:
  - shows no growth of 0.10 or more in log2 G per doubling of M over J_top(n)
    beyond both nulls; and
  - shows no top-rung excess of 0.10 or more over both nulls,

  at the stated resolution (about ±0.02 per n on the slope).
- **What it cannot certify.**
  - Anything about undeclared filters. The class of cheap h is not enumerable,
    and KN-FIND-ffe1df Proposition 2 says no group-theoretic argument reaches
    it.
  - Growth slower than 0.10 per doubling (for example polylog), or growth that
    starts beyond j = 10 or beyond n = 41.
  - **Tree levels >= 2.** Inputs there are conditioned on level-1 survival, and
    a level-1 result does not close them (KN-FIND-ffe1df).
  - The universal (forall) negative route of KN-OPEN-91d4f6, which needs a
    proof.
  - Anything about Koblitz curves or about E.
- **Regime the ladder does not resolve.** The "Weil-scale, random-sign" regime
  `G - 1 ~ M l^{-1/2}` at n >= 31. It is visible only at n <= 23, and there only
  through SPEC-T. Discrimination is between square-root cancellation across
  the M^2 character pairs (G tracks the nulls) and coherent, barrier-saturating
  structure (`G - 1 ~ M^2 l^{-1/2}`, which would grow by about 2 in log2 per
  rung at n = 31 once above the floor). This is the same M^2 barrier as
  KN-FIND-ffe1df's `M <= p^{1/4}`.
- **What Theorem C contributes.** It excludes exact filters on `<P>`. The
  design measures only the approximate question, which Theorem C does not
  touch.
- **Nearby objects.** (i) E(F_{2^n}), where the exact gain h is attained and
  the controls must be alive. (ii) E(F_p) at the RT-EXP-1 fixture. The
  instrument must read differently on these than on `<P>`, or it has not
  identified anything.

## 10. Prior art (summary; the full block is in the IDEA)

- **RT-EXP-1 / KN-FIND-ffe1df (internal; adjacent).** The same observable on
  E(F_p) with exact whole-group counts and in-sample G. This design transfers
  it to characteristic 2 on `<P>` and adds the split-sample correction, the
  j-ladder, RULE-X, and exact positive controls on E.
- **BINSTD lineage (internal; adjacent; the nearest).** IDEA-20260926-136bd3,
  then EXP-BINSTD-de9678, 6f1e66, c9c8a2, and 811a2e (version 4,
  review_required, zero runs).
  - It measures bucket gain on binary Koblitz curves **sampled from the full
    group E**. Its arms are stratified by the exact E/4E quotient. Its
    estimator is the in-sample max over (a, b) conditioning cells against
    measured random-label quantiles. Its ladder runs over n at
    M = N^{1/3}, N^{1/4}, for n <= 23, plus M = 16 at n = 41.
  - It **explicitly declines sampling from the target subgroup 4E**
    (EXP-BINSTD-c9c8a2 scope "RR-1 route (b)"; audit sheet `rr1_route`).
  - The deltas here: the question is asked on `<P>` (KN-OPEN-91d4f6's
    load-bearing domain); the families are F_2-linear random, polynomial,
    normal and 1/x on ordinary non-Koblitz curves; the observable is
    KN-FIND-ffe1df's quasigroup-rule pi_c(d) at both rules; and the estimator
    is split-sample. The M_eff = 1 convention also avoids that lineage's SR-6
    trigger for labels constant on 4E.
- **H-SEMBIN-83a856 (internal; special case).** The j = 1 trace filter on E,
  which is supported and serves here as CE-TR.
- **J3 RC5** (TASK-20260928-62ad14 report, RT-20261001-3359c3; internal;
  same target). This design is RC5 written down, corrected for domain
  (VAL-20261003-17b1e4 A-2) and observable (A-1).
- **Farashahi, Pellikaan and Sidorenko 2008 (retrieved, abstract only;
  adjacent).** A level-0 statement: x-coordinate subfield coefficients are
  near-uniform on the main subgroup, for n = 2l. Our n are odd primes, and that
  paper has no sum or triple statement.
- **Ahmadi and Shparlinski 2014, Lemma 1** (retrieved via ar5iv; it recalls
  Kohel-Shparlinski; adjacent). A subgroup x-character-sum bound, **for p >= 5
  only**. The characteristic-2 analogue that HA-1 imitates is untraced
  (KN-LIT-f6de4b).
- **The chord-slope reformulation (section 2).** A derivation in this design.
  Its literature status is **unverified**: only the queries listed in the IDEA
  were run.

## 11. dominated_by and sota_delta (honest accounting, inventor protocol section 5)

- **Object.** An F_2-linear x-label on `<P>` under pairwise translation (Class
  II branching), read by its single-bucket gain. RULE-X is reformulated as the
  linear predictability of the chord slope.
- **Depth of verified structure.** Derivation only, at three points: the
  chord identity; the exact-case characterisation `gamma = 0`, i.e. alpha in
  {0,1}; and the PL-X 3/4 constant (continuum). Nothing was measured.
- **dominated_by.** "n/a (no result claimed)". Checked row by row against the
  ECDLP frontier map:
  - Generic floor and rho: KR-RHO-13bf67, 0528e7, 037e22, fb88e6, 6239aa,
    7d93f6, 46c2c6, ea34b8, 18cc42.
  - Binary-curve rho mechanics: KR-RHO-6654ba (halving step), fbd582
    (x(P-Q) alongside x(P+Q)).
  - Binary index calculus: KR-IC-f5c584 (trace morphism; the exact case of
    section 2), 1fcdbc, 889857, 73db3f, 955fd6 (2- and 4-torsion), b0fcda.
  - KR-RHO-6654ba, fbd582, KR-IC-f5c584 and 955fd6 were read in full; the
    other rows were checked by title and claim line only.

  Pollard rho with negation (`0.886 sqrt(l)`, O(1) memory) dominates every
  outcome on time, memory, and data. A level-1 gain is not an algorithm.
- **sota_delta.** Time 0, memory 0, data/queries 0. The contribution is a
  measurement and its instrument: a preregistered, selection-corrected
  characteristic-2 ladder on `<P>`, and the chord-slope identity.
- **Enumerated closures.**
  - Exact x-linear XOR filters on E are exactly span{1} (the trace), by the
    chord identity: a derivation with a named mechanism.
  - On `<P>` they are constant (Theorem C transferred).

  No approximate closure is claimed.
- **Open directions for the next session.**
  1. A characteristic-2 equidistribution bound for `(L_alpha(x_Q + x_R),
     L_gamma(lambda))` on `<P> x <P>`, which would be the KN-OPEN-91d4f6
     negative route for RULE-X. Classify its Artin-Schreier-degenerate
     (alpha, gamma).
  2. The same ladder for 1/x and quadratic labels, and for target-dependent
     labels.
  3. A level-2 conditioned ladder: inputs drawn from level-1 survivors.
  4. Koblitz curves on `<P>` with Frobenius-equivariant labels, which the
     BINSTD lineage declines.

## 12. Procedure deviations and disclosures

- **PD-1, dispatch preconditions not met (material).** The card is
  `written_not_dispatched`, blocked on TASK-20261003-6d2f84. Per the dispatch
  note, **the user requested this run now**, and TASK-20261003-6d2f84 is being
  run concurrently with no receipt yet. Its records (DEC-20261003-4e91b7,
  KN-OPEN-91d4f6, this card) were read from the working tree. Whether they are
  committed on main was taken from the dispatch message; it was not verified
  here (no shell, no git). DP-2 (a lane claim on GOAL-SEMBIN-5078bc) was **not**
  made by this session, because claiming with `--publish` writes outside the
  write scope. Disclosed, not waived.
- **PD-2, identifiers hand-chosen (material).** There was no shell, so
  `tools/allocate_id.py` was not run. Greps over ledger/, knowledge/,
  coordination/, and experiments/*.yaml, plus a repository filename glob, found
  no occurrence of 5a2c9e, 9c41f7, or e2b864. A first choice for the
  hypothesis token matched a substring of a hash in a GOAL-ECDLP-001 receipt
  and was replaced. **Owed before filing:** `allocate_id.py --check` for each
  id and `git grep` for each token.
- **PD-3, no parse check.** The YAML drafts were not machine-parsed. Scalars
  containing ": " or braces are quoted or in block scalars. A strict parse and
  `tools/validate_ledger.py` are owed by the archiving task
  (TASK-20261003-d05b93).
- **PD-4, kb index not queried.** The crypto-kb MCP tools were not available in
  this session's tool surface. Prior art used grep and the web, as listed in
  the IDEA. Absence of a hit is not evidence of absence.
- **PD-5, write scope.** Only `coordination/tasks/TASK-20261003-3c8ea2/` was
  written. A KN-LIT note for Farashahi, Pellikaan and Sidorenko 2008 (abstract
  retrieved) is **owed to a curation task**; it was not written here, because
  `knowledge/` is outside the write scope.
- **PD-6, scratch arithmetic.** Every precision, floor, cost and planted-gain
  figure is scratch hand arithmetic from stated formulas, labelled as such.
  FX-4 and the gates check them at run time. None is a measurement.
- **Not used:** the frozen Hhan source (inputs/HHAN-2024-2402.11269/). No
  Hhan-dependent statement appears here.
