# EXP-PFDR-cbdefb — Stage 1: the FROZEN closure convention, the censoring flag, the known-answer fixtures and the pre-declared analysis choices

Task TASK-20260903-6745ea (Executor). Written and frozen BEFORE the first
official run of this experiment (every run manifest records this file's
sha256 under `inputs.parameters.closure_convention_sha256`; the convention
identifier string `cbdefb-closure-v1` is recorded per system in
`raw-result.json`). Nothing below is adjusted after the first official run;
a change would be a versioned protocol amendment, never an edit. Observations
only; no status is touched.

The convention implements `specification.yaml inputs.closure_convention`
verbatim and resolves the two readings named as a confounder by
IDEA-20260903-d52480 ("multiply only fallen elements" versus "multiply
everything") the way sections 1-2 explain. Implementation:
`experiments/EXP-PFDR-cbdefb/closure.py` (its docstring restates this section).

## 1. The convention

Ring. The shared meter's `Ring(p, n_sq = m s, n_free = 0)`: the multilinear
quotient B = F_p[a]/(a(a - 1)) on n = m s digit variables (d = 2). B_{<=D} is
the span of the squarefree monomials of degree <= D; the degree of an element
is the meter's REDUCED total degree. (For d > 2 presentations and for the
s = 1 direct-presentation cross-check the ring is the ordinary polynomial
ring with the membership generators listed explicitly in F; there reduced =
nominal degree and everything below applies unchanged.)

Definition (for one generator list F and one degree D, D_min = min deg F):

- W_0(D) = V_{F,D-1} + span{ m f : f in F, m a ring monomial, deg m <= D - deg f }.
  The second summand is the meter's CUMULATIVE Macaulay row space at D
  (`layer_rows(..., "cumulative")`, reduced rows; the layers j < D are
  already inside V_{F,D-1}, so the code adds only the per-layer rows at D
  for D > D_min). V_{F,D_min - 1} = 0.
- Pass t: F_t = W_t cap B_{<=D-1}, the FALL SPACE of W_t = the echelon rows
  whose pivot lies below the degree-D block (the meter's identity
  `fall_dim = full_rank - top_rank`, linalg.py); W_{t+1} = W_t + sum_i a_i F_t
  over ALL ring variables a_i. (Only the part of F_t not multiplied in an
  earlier pass — or at degree D - 1 — is multiplied again; by linearity the
  space W_{t+1} is the same.)
- V_{F,D} = the fixed point (finite dimension guarantees termination).
- FALL AT D  <=>  dim(V_{F,D} cap B_{<=D-1}) > dim V_{F,D-1}
  (V_{F,D-1} is contained in the left side by construction);
  `new_fall(D)` is the difference.
- d_ff = least D <= D_max with a fall; d_lf = largest D <= D_max with a fall;
  the full fall history {D : fall at D} is recorded.
- iteration_count(D) = (number of passes that inserted at least one new
  pivot) + 1. So a degree without fallen elements, or whose fallen elements'
  variable multiples add nothing, has count 1; CTRL-ITERATION-COUNT reads
  "a fall at D with iteration_count(D) = 1" as the artifact tell.

Sub-choices fixed here and the reason for each:

1. W_0 uses NOMINAL multiplier degree (deg m <= D - deg f), i.e. exactly the
   union of the per-layer Macaulay layers the graded-rank d_ff of
   EXP-PFDR-5726af is read from. The alternative (all m with REDUCED
   deg(m f) <= D) would insert, already at D = deg f, the multiples a_i f for
   every variable dividing every top monomial of f; at s = 1 the top form is
   the single monomial a_1 a_2, so that alternative gives d_ff = 2 while the
   graded-rank d_ff is 3, violating CTRL-S1-BASELINE's forced disposition
   "the closure's d_ff equals the graded-rank d_ff". The nominal choice is
   therefore the one the contract's own controls pin.
2. Only FALLEN elements are multiplied ("multiply only fallen elements").
   "Multiply everything" (every g in W with deg(a_i g) <= D, which in the
   quotient includes degree-D elements whose top form is divisible by a_i)
   likewise gives d_ff = 2 at s = 1 (f itself has top form a_1 a_2) and fails
   the same control.
3. "Multiply by all monomials keeping degree <= D" is realised as iterated
   multiplication by single variables: every intermediate product of a fallen
   element by a variable is again fallen (degree <= D - 1) or lands in degree
   exactly D, so the iterated variable closure contains every m g with
   nominal deg m <= D - deg g, and additionally the products through
   intermediates that collapsed (which the polynomial-ring reading also
   contains, section 2). The literal "reduced deg(m g) <= D for all monomials
   m" reading would insert a_i a_j g for degree-D intermediates a_i g, i.e.
   one degree EARLIER than the polynomial-ring object (section 2); it is not
   used.

## 2. Why this is Huang-Kosters-Yeo's V_{F,D}, exactly

Take HKY's definition in the polynomial ring R = F_p[a_1..a_n] with F = the
REDUCED (multilinear) generators lifted to R together with the field
equations a_i^2 - a_i (the theorem's own setting for the descended field
equations; the reduction of the generators themselves is part of the
presentation, IDEA-20260830-84cdb7's "substituted S_{m+1} reduced in B"):
V^R_{F,D} is the smallest subspace of R_{<=D}
containing F cap R_{<=D} and closed under g -> h g whenever deg(h g) <= D
(monomials h suffice). Let pi: R_{<=D} -> B_{<=D} be reduction. Its kernel
is spanned by the monomial multiples of a_i^2 - a_i of nominal degree <= D
(reduce one exponent at a time), all of which lie in V^R_{F,D}; hence
V^R_{F,D} = pi^{-1}(pi(V^R_{F,D})) cap R_{<=D}. An element of pi(V^R_{F,D})
of reduced degree <= D - 1 has its reduced representative (nominal degree
<= D - 1) in V^R_{F,D}, so it may be multiplied by any variable; conversely
a degree-D element of R cannot be multiplied by a nonconstant without
leaving R_{<=D}. Therefore pi(V^R_{F,D}) is the smallest subspace of B_{<=D}
containing pi(F cap R_{<=D}) = the cumulative Macaulay rows (multipliers of
nominal degree <= D - deg f; multipliers with square factors reduce to
lower squarefree multiples plus kernel elements), containing
pi(V^R_{F,D-1}), and closed under g -> a_i g for g of REDUCED degree
<= D - 1 — which is section 1 verbatim. Falls correspond one to one:
V^R_{F,D} cap R_{<=D-1} strictly contains V^R_{F,D-1} iff the reduced
statement holds, because ker(pi) cap R_{<=D-1} lies in V^R_{F,D-1}.
So the frozen convention computes the image of HKY's invariant for the
digit system with its field equations, degree for degree, and inherits the
monomial-order independence (KN-LIT-7607) by construction.

If instead F carries an UNREDUCED generator of nominal degree D_0 > its
reduced degree (84cdb7's literal direct list at s = 1: S_3(x_1, x_2, x_R) has
nominal degree 4, reduced degree 2), the polynomial-ring closure cannot see
the generator before D = D_0 and then registers its own reduction modulo the
field equations as a fall at D_0; the two objects differ by exactly that
initial reduction fall. Both are run on the s = 1 slice (section 5) so the
difference is on record; the digit closure is the object of this contract.
(Recorded before the first official run; the dry runs into the scratchpad
that preceded this note's final wording are disclosed in implementation.md.)

Hand check (section 4, fixture H): F = {a_1 a_2 + a_3}. V_{F,2} = span(f).
At D = 3: W_0 = span(f, a_1 f, a_2 f, a_3 f); a_1 f = a_1 a_2 + a_1 a_3 and
a_2 f have degree 2, so V_{F,3} cap B_{<=2} strictly contains V_{F,2}: a fall
at 3, and it is the SAME fall the polynomial ring shows as
x_1 f - x_2 (x_1^2 - x_1) = x_1 x_2 + x_1 x_3. Multiplying the fallen
elements gives a_3, a_1 a_2, a_1 a_3, a_2 a_3, a_1 a_2 a_3, so V_{F,3} is the
whole ideal (dimension 5 = 8 - |Z|, Z = {000, 100, 010}); no fall at D >= 4.
Expected history {3}, d_ff = d_lf = 3, iteration_count(3) = 2.

## 3. The censoring flag (frozen)

Two flags are recorded per system; d_lf enters a slope fit only when the
second is False.

- `no_fall_in_window` (the contract's literal string "no fall observed in
  (d, D_max]" with d the generator degree): no fall at any D in
  (D_min, D_max]; then d_ff and d_lf are undefined (null).
- `right_censored`: True unless the fall history is CERTIFIED complete at
  D_max by one of two routes, both exact:
  (S) structural: in B every ideal is radical and V_{F,n+1} is an ideal
      (at D = n + 1 every element of B is fallen), so V_{F,D} = ideal(F) for
      all D >= n + 1 and no fall occurs at D >= n + 2. Hence D_max >= n + 1
      certifies completeness. At m = 2 this covers s <= 3 (n <= 6).
  (C) ideal-side: with Z = the common zeros of F in {0,1}^n and
      I = ideal(F) = I(Z) (B is a product of copies of F_p), dim(I cap B_{<=D})
      = N_D - r_D with r_D the rank of evaluation at Z on B_{<=D}.
      C1: dim V_{F,D_max} = N_{D_max} - r_{D_max}.
      C2(D), D_max < D <= n: I cap B_{<=D} = (I cap B_{<=D-1}) + sum_i a_i (I cap B_{<=D-1}),
      decided by the dimension of the annihilator {lambda on B_{<=D} :
      lambda|B_{<=D-1} in span(ev_z), (lambda o a_i)|B_{<=D-1} in span(ev_z)
      for every i} (exact linear algebra over F_p); C2(n + 1) is trivial.
      C1 and every C2 give V_{F,D} = I cap B_{<=D} for all D >= D_max by
      induction (the fallen part of V_{F,D-1} is all of it), hence no fall
      above D_max.
  Ordinary rings (d > 2 equal-d^s arms; the s = 1 direct-presentation
  cross-check): never certified (no structural bound in the polynomial ring
  and no Groebner computation is allowed to stand in for one); the digit
  form of the s = 1 slice is certified structurally (n = 2).
  Rings with 2^n > 1024 monomials (the (2, 6) equal-d^s arm): certificate not
  attempted (column cap), right-censored by declaration.
- A `right_censored` draw with an observed fall reports its d_lf as an
  OBSERVED-SO-FAR value, labelled censored, never as a bound and never in a
  fit (contract invalidation rule 5). A cell is "fully censored" when every
  draw of the arm is right-censored.

## 4. Known-answer fixtures (CTRL-KNOWN-ANSWER-FIXTURE) and the substitution

The F_2 Weil-descent fixture of `inputs.known_answer_fixtures (ii)` is NOT
exhibited: its conformance to Theorem 2.6 of arXiv:2103.07282 requires the
hypothesis "reducible for k", which the proposing session retrieved only at
abstract / ar5iv level (proof bodies not read) and which this session, with
no web access, cannot re-read or verify; a fixture whose conformance cannot
be argued would pin nothing. Per the contract, the PLANTED-FALL fixture is
the known answer and this substitution is recorded here and in analysis.md.

- Fixture P (planted fall, seed 5, the construction of
  `tests/test_macaulay_fp.py::test_planted_fall_generator_reports_fall_with_content_h`
  re-implemented in the run script): p = 4099, 10 squarefree variables,
  f_1, f_2 random quadratics (density 0.7), u, v random homogeneous linear
  forms (density 0.8), h random of degree 2 (density 0.5), g = u f_1 + v f_2 + h
  with deg g = 3 and deg h = 2, `random.Random(5)`. Forced disposition: the
  extended system {f_1, f_2, g} has a fall at D = 3 = deg g with
  iteration_count(3) >= 2; h lies in V_{F,3} cap B_{<=2} of the extended
  system and NOT in its V_{F,2} and NOT in V_{F,3} of the base {f_1, f_2}; the
  base has no fall at D = 3. D_max = 5 for this fixture (638 columns); both
  engines are run and must agree. The same construction in the ordinary ring
  (3 free variables, seed 5) exercises the ordinary-ring path.
- Fixture H (hand-derived, section 2): {a_1 a_2 + a_3} in 3 squarefree
  variables, p = 4099, D_max = 7. Forced: history {3}, dim V_{F,3} = 5,
  iteration_count(3) = 2, certified (structural).
- The s = 1 slice (CTRL-S1-BASELINE) is section 5.

## 5. The s = 1 slice (CTRL-S1-BASELINE)

Object: m = 2, d = 2, s = 1, every prime in {4099, 16411, 65537}, curve seeds
3101..3108 (the ladder's curves), planted targets with window [0, 2) (the
only window whose digits are {0, 1}); a curve with no on-curve x in {0, 1}
has no plantable s = 1 target and is recorded as such (no unplanted target
is substituted). Three generator lists per draw:
(a) the direct presentation of IDEA-20260830-84cdb7 at B = 2
    (`direct_presentation`): [S_3(x_1, x_2, x_R), x_1(x_1 - 1), x_2(x_2 - 1)]
    in the ordinary ring, S_3 unreduced (nominal degree 4);
(b) the digit presentation at s = 1 (`digit_presentation`): [S_3(a_1, a_2, x_R)
    reduced] in the squarefree ring, whose quotient IS x_k(x_k - 1) = 0;
(c) the polynomial ring on the REDUCED generator: [lift of (b) to R,
    x_1(x_1 - 1), x_2(x_2 - 1)] — HKY's own setting for the object (b)
    computes (section 2).
Checks: (a)'s S_3 reduced modulo x_k^2 - x_k equals (b) term for term under
x_k -> a_k (the s = 1 identification); the closure on (b) satisfies
d_lf >= 2 (afe4ce's floor, B = 2) and closure d_ff = graded-rank d_ff (the
control's forced disposition, `s1_pass`); the closure on (c) must reproduce
(b)'s fall history exactly (the section-2 equivalence at the smallest
instance); the closure on (a) is reported beside them and is expected to
differ from (b) by the initial reduction fall at nominal degree 4 (section 2,
last paragraph).

## 6. CTRL-DFF-AGREEMENT (P1)

EXP-PFDR-5726af's Semaev instances at p = 4099 (curve seeds 1101..1103,
target seeds 1..2, its curve and target construction reproduced exactly:
a = 527, b = 72, x_R = 2374 for (1101, 1) etc.), s = 2..5. Forced exact:
closure d_ff = graded-rank d_ff (same meter, same code path here) = the
per-draw d_ff recorded in that package's raw-result.json (5, 5, 6, 6).

## 7. Engines, cross-checks and the memory contract

- Reference engine: the meter's `Echelon` (dict rows, exact). Accelerator:
  `DenseRREF` (float64 BLAS products, reduction mod p after every product;
  exact because every partial sum is < 1024 * 65537^2 < 2^53, asserted).
- Policy: a system whose column space at D_max has <= 256 columns is
  measured with the reference engine AND recomputed with the dense engine
  (histories must agree integer for integer); above 256 columns (s = 5 main
  cells, the fixtures P, the (2, 6) arm) the dense engine is the measurement
  and the reference engine recomputes the declared subsample: at every
  (s = 5, p) cell the draws (curve seed 3101, target seed 1) of the Semaev
  and non-curve arms, their NULL-1 seed 7, and the NULL-2 / NULL-3 seed-7
  objects; fixture P entirely. Any disagreement invalidates the run.
- The graded-rank layers (P1) are the meter's `analyze_layer(..., "per_layer")`.
- Memory: RLIMIT_AS = 8 GB; pre-flight (`columns.preflight`) at D_max per
  ring: abort above 50,000 columns or 4 GiB dense-equivalent
  (rows x columns x 8 bytes); the (2, 2, 6, 8) cell is excluded by name and
  is not on this ladder (D_max = 7).
- Wall clock: 7200 s per run (hard alarm -> failed_infrastructure, partial
  results preserved); a guard at 6600 s stops STARTING new systems and marks
  the rest not computed; a run with not-computed systems is
  failed_infrastructure (resource_exhaustion), never evidence.
- One worker: BLAS threads pinned to 1.

## 8. Pre-declared analysis choices (Stage 4; written before any run)

- Slope fits: ordinary least squares of the per-draw value against s,
  pooled over the three primes. PRIMARY range s in {2, 3, 4, 5} (the cells
  carrying a frozen d_ff prediction; s = 1 is the direct-presentation
  boundary with a degree-2 generator); SECONDARY range s in {1..5}, reported
  beside it. d_lf fits use only draws with `right_censored = False`; d_ff
  fits use draws with an observed fall. 95 percent interval: the t-interval
  from the residual variance (n - 2 degrees of freedom); when the residual
  variance is 0 the interval is the point estimate and is flagged
  DEGENERATE; a percentile bootstrap over draws within cells (2000
  resamples, `random.Random(0)`) is reported beside it. Resolution 0.25 as
  frozen.
- Outcome label (contract + H-PFDR-c88f14 P4/P5), evaluated mechanically on
  the primary fit: OUTCOME I iff the d_lf interval contains 1 and excludes
  0.5; OUTCOME II iff additionally the d_ff interval lies strictly below the
  d_lf point estimate and excludes 1; OUTCOME III iff the d_lf interval
  contains 0 and excludes 0.25 AND at least four consecutive s have every
  draw uncensored with one common d_lf value (flat) AND the ladder top is
  uncensored; otherwise UNRESOLVED. Both the d_lf-only label (I / III /
  unresolved) and the joint label are reported.
- HEUR-002 falsifier check (statistic only): whether the d_lf interval
  excludes 0 on a ladder with no censored or aborted cells at its top.
- Null band: per (s, p) cell and null arm, c = d_lf - (s + 2) on uncensored
  draws, membership in {0, 1, 2}; censored draws listed; tail check = the
  largest c and whether it grows with s.
- NULL-3: d_ff(NULL-3) - d_ff(Semaev) per cell (forced 0; NULL-3 has 5
  objects per cell, compared with the cell's Semaev value set); d_lf
  difference reported; tail check = the largest d_lf difference.
- Controlled-null flags (F5): whether NULL-1, NULL-2 or the non-curve arm
  has the same (d_ff, d_lf) pair as the Semaev arm at every cell.
- Equal-d^s spread: the set of (d_ff, d_lf, censored) over (2, 6), (4, 3),
  (8, 2) per (curve, target); the spread in d_ff and in d_lf; the factor-2
  rule stated next to it.
- Iteration counts: the minimum count at a claimed fall per cell and arm
  (forced >= 2); any count-1 fall named.
- Tail checks: the top two uncensored Semaev cells with pre-flight counts
  and iteration counts.

## 9. Seeds (as frozen)

Curve seeds 3101..3108 per prime; target seeds 1..5; null seeds 7, 11, 13,
17, 19 per null arm (NULL-1 per draw; NULL-2 and NULL-3 take no curve or
target input and are computed once per (p, s, seed) and reported per draw by
reference — deviation D-NULL-ONCE, the same disclosure as EXP-PFDR-5726af's
D-NULL2-ONCE); known-answer fixture seed 5; 5726af's seeds 1101..1103 / 1..2
for CTRL-DFF-AGREEMENT only. Curves: SHA-256 draws as in EXP-PFDR-5726af
(a = SHA256("cs:p:a{t}") mod p, b likewise, rejecting a = 0, b = 0,
singular curves and curves with fewer than two on-curve x in [0, 4)).
Non-curve cubic: per curve seed, t = SHA256("EXP-PFDR-cbdefb:singular:p:cs:t:attempt")
mod p, A = -3 t^2, B = 2 t^3 (nodal), window x with square right-hand side and
x != t; x_R a root of S_3(x_1, x_2, X) with the same S_3 formula, certificate
kind s3_root re-verified by `harness.semaev.s3_eval`.
