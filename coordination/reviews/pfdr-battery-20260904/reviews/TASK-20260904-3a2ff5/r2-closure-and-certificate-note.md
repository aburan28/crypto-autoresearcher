# R2 — is the frozen closure Huang-Kosters-Yeo's V_{F,D}, and is the completeness certificate sound?

Red Team, TASK-20260904-3a2ff5. Read: `stage1-closure-convention.md` sections 1-3,
`closure.py` (sha256 63475db53f5d34859d638327a7082834da0b81209059d0b871bab5b4e32cfb98,
the version pinned by runs 3-23), `harness/macaulay_fp/linalg.py`. Computations:
`r2_certificate.py` -> `r2_certificate.json`; `ptm_objects.py` -> `ptm_objects.json`.

## 1. The section-2 equivalence, checked line by line

Claim under check: the frozen reduced-ring convention computes the image under
pi : R_{<=D} -> B_{<=D} of the polynomial-ring closure V^R_{F,D} with
F = {lifted reduced generators} u {a_i^2 - a_i}.

(a) ker(pi) cap R_{<=D} = span{ m (a_i^2 - a_i) : nominal deg <= D }. HOLDS: the field
equations have pairwise coprime leading terms a_i^2, so by Buchberger's first criterion
they are a Groebner basis and division gives a degree-bounded standard representation.
All these elements lie in V^R_{F,D}. (The note asserts this without the GB reason; the
reason is elementary and the assertion is correct.)

(b) "An element of pi(V^R) of reduced degree <= D-1 has a representative of nominal
degree <= D-1 in V^R, so it may be multiplied by any variable." HOLDS: representative
and element differ by a kernel element of nominal degree <= D, which is in V^R by (a).

(c) pi(F cap R_{<=D}) equals the cumulative Macaulay rows of the frozen convention.
HOLDS: a multiplier h with square factors reduces to a squarefree monomial m' with
deg m' <= deg h, and pi(h f) = m' pi(f), which is in W_0(D) since
deg m' <= D - deg f; conversely every W_0 row is such an image.

(d) "Multiply by all monomials keeping degree <= D" equals the iterated single-variable
closure. HOLDS in R: for g of degree delta and a monomial h of degree D - delta, every
intermediate a_{i1}...a_{ij} g has degree delta + j <= D - 1 for j < D - delta, so every
intermediate is multipliable. Pushed through pi, this is the frozen recursion.

(e) Falls correspond one to one because ker(pi) cap R_{<=D-1} is inside V^R_{F,D-1}.
HOLDS by (a) at degree D-1.

(f) The two sub-choices (NOMINAL multiplier degree; multiply only FALLEN elements) are
the ones that make the closure's d_ff equal the graded-rank d_ff at s = 1; the note
states this and CTRL-S1-BASELINE pins it. Checked and reproduced: the alternative
readings give d_ff = 2 at s = 1 against a graded d_ff of 3.

I found no gap in the equivalence argument.

CITATION CAVEAT (Red Team responsibility 9). The attribution of this object to
Huang-Kosters-Yeo is `recalled` in H-PFDR-c88f14 ("corpus note read, paper not opened").
I fetched https://eprint.iacr.org/2015/573: title, authors (Ming-Deh A. Huang, Michiel
Kosters, Sze Ling Yeo), year 2015, order-independence of the last fall degree, and the
doubt about the first fall degree assumption for Weil-descent summation systems all
CONFIRM KN-LIT-7607. The abstract page does NOT contain the definition of V_{F,i}, so the
definition the whole experiment measures remains unverified against the source in this
round. This does not affect internal validity -- the convention is frozen, explicit and
pinned by controls -- but "Huang-Kosters-Yeo's V_{F,D}" is a recalled attribution, and
any outward-facing statement should say so or open the paper.

## 2. The completeness certificate

Route (S), structural: at D = n+1 every element of B has degree <= n = D-1, so the whole
of V is fallen, V_{F,n+1} is an ideal containing F, hence equals I; no fall above n+1.
D_max >= n+1 therefore certifies. HOLDS. Applies at m = 2 for s <= 3 (n <= 6, D_max = 7).

Route (C): C1 says dim V_{F,D_max} = dim(I cap B_{<=D_max}); with V contained in
I cap B_{<=D_max} always, C1 is EQUALITY of the two spaces. C2(D) says
I cap B_{<=D} = (I cap B_{<=D-1}) + sum_i a_i (I cap B_{<=D-1}). C1 + all C2 imply, by
the induction written out as Lemma 4 of `derivation-r3-single-fall.md`, that
V_{F,D} = I cap B_{<=D} for every D >= D_max, hence no fall above D_max. The
implementation of C2 by an annihilator dimension is correct: the unknowns parameterise
exactly the functionals on B_{<=D} that annihilate J = I cap B_{<=D-1} (that space has
dimension r_{D-1} + (N_D - N_{D-1}) = the code's `nunk`), the constraints impose
lambda(a_i v) = 0 for v in a kernel basis of J, and `codim = nunk - rank` is then
dim Ann(J + sum_i a_i J) = N_D - dim(J + sum a_i J), compared against r_D. Correct.

INDEPENDENT SECOND IMPLEMENTATION. I recomputed dim(J + sum_i a_i J) directly, by
building a kernel basis of the evaluation map, multiplying it out and echelonising --
no dual/annihilator argument. On the declared s = 4 instance the two implementations
agree at D = 4, 5, 6, 7, 8 (codim = r_D = |Z| = 2; `r2_certificate.json`).

FINDING (C2 IS VACUOUS HERE). Lemma 3 of `derivation-r3-single-fall.md` proves C2(D)
holds for every D >= e(Z) + 2, where e(Z) is the interpolation degree of the zero set.
Observed |Z| <= 4 on every draw, so e(Z) <= 3, and every C2 the certificate evaluates is
at D >= 8. So all 480 recorded C2 checks (`s4:D=8` x120, `s5:D=8,9,10` x120 each, every
one "holds": `r0_controls.json`) were a theorem, not a test. Confirmed empirically even
on a system with |Z| = 386 (C2 holds at D = 8, 9, 10). The censoring decision at s = 4, 5
therefore rests on C1 ALONE. That is not a defect -- C1 is the right test and it refuses
correctly (section 3) -- but "certified C1+C2" should not be read as two independent
checks.

STRUCTURAL CONSEQUENCE (design, not error). C1 says the closure has already computed the
entire ideal cap at D_max. So a system can only be certified uncensored if it has
already SOLVED by D_max. The certificate is therefore not neutral between arms: the
Semaev arm falls at 6 and saturates, so it certifies; NULL-1/NULL-2 at s = 5 have not
saturated at 7, so they cannot certify and are censored. Censoring in this design is a
deterministic consequence of a high last fall, not a random loss. Since censored draws
are excluded from the d_lf fit, any future cell with d_lf > D_max would be dropped, and
the fit would be biased toward Outcome III. At s <= 5 nothing was dropped on the Semaev
arm, so no bias was realised here; it is a live hazard for any extension of the ladder.

## 3. The planted late-fall object (the certificate must refuse)

Construction (mine, `ptm_objects.py`, seed 20260904, p = 4099, n = 10 squarefree
variables): f1, f2 random of degree 5; u, v random of degree 3; h random of degree 7;
g = u f1 + v f2 + h, of degree 8. F = {f1, f2, g}. By construction u f1 and v f2 are
degree-8 Macaulay rows, so h = g - u f1 - v f2 of degree 7 appears at D = 8: a fall
strictly ABOVE D_max = 7.

Result with the producer's UNCHANGED `certify_history` at D_max = 7:
  falls in (5, 7] = [] ; dim V at 7 = 112 against dim(I cap B_{<=7}) = 582 ;
  C1 = FALSE ; certified = FALSE ; route "not certified" ; right_censored = TRUE.
Run to D_max = 9, the true history is falls = [8], iteration count 2 at the fall,
dim V_8 = 627 = dim(I cap B_{<=8}).

The certificate REFUSED, as the failure signature requires. No false certificate.

## 4. The dense engine's exactness

`DenseRREF.__init__` asserts p^2 (ncols + 1) < 2^53. Every partial sum in the engine is
bounded by that quantity: `_reduce` computes R - F @ M with inner dimension <= rank
<= ncols and entries < p (so |sum| <= ncols p^2 + p); `_rref_small` computes
R - outer(f, row) (entries < p^2 + p); `add_batch` computes M - G @ NR with inner
dimension <= ncols; the scatter into `prods` receives at most two contributions per
target column (a monomial already containing a_i, and its preimage without a_i), so
entries are < 2p. Largest actual value at the largest cell (p = 65537, N = 968):
4.16e12 = 2^41.92, eleven binary orders below 2^53. The bound holds with margin, and
float64 represents every intermediate exactly. The scatter itself is correct: for a
fixed variable a_i, columns containing i map to themselves and columns not containing i
map injectively to columns containing i, so the two fancy-index accumulations realise
the multiplication map exactly.

I also checked the `processed`-row optimisation in both engines; it is sound (see the
implementation check in `derivation-r3-single-fall.md` section 5).

RECORDED LIMITATION (not a break): at every s = 5 cell only 1 of 40 Semaev draws per arm
was cross-checked against the reference sparse engine; 39 of 40 rest on the dense engine
alone. Where both ran (every s <= 4 system, every fixture, the declared s = 5 subsample)
the histories agree integer for integer.

RESULT FOR R2: HOLDS. The frozen convention computes the stated invariant; the
certificate is sound and refuses on a known-false object. Two findings attach: C2 is a
theorem at the tested zero-set sizes so the certificate is C1 alone, and the HKY
attribution of the invariant is a `recalled` citation whose definition was not verified
against the source in this round.
