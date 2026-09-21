---
id: KN-LIT-e77232
type: literature
title: >-
  ellipticnews 2015-04-13, "Elliptic curve discrete logarithm problem in
  characteristic two": Galbraith's assessment of the Semaev/Karabina
  S_3-chaining proposals, with the Semaev, Kosters and Gaudry comment thread
authors:
  - "Steven D. Galbraith"
comment_thread:
  - "Igor Semaev (2015-04-20)"
  - "Michiel Kosters (2015-05-02)"
  - "Pierrick Gaudry (2015-05-05)"
year: 2015
venue: "ellipticnews - The Elliptic Curve Cryptography blog (WordPress). Blog post with comment thread; not peer-reviewed."
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: "https://ellipticnews.wordpress.com/2015/04/13/elliptic-curve-discrete-logarithm-problem-in-characteristic-two/"
tags: [galbraith, semaev, karabina, kosters-yeo, summation-polynomial, chained-system, s3-chaining, weil-descent, first-fall-degree, degree-of-regularity, solving-degree, step-degree, binary-field, characteristic-2, prime-extension-degree, index-calculus, point-decomposition, ecdlp, cost-model, memory, xl, block-wiedemann, null-control, blog, prior-art]
confidence: reported
citation_verified: read
citation_verified_note: >-
  Full post and all three comments read in-session on 2026-09-05 from text
  supplied by the user; the live URL was fetched the same day by this session
  (HTTP 200, 136,551 bytes, sha256 05bba549...5122) and every figure recorded
  below was located in the retrieved page (the formulas render as LaTeX image
  alt text). Receipt: inputs/ELLIPTICNEWS-CHAR2-2015/provenance.json. The
  page bytes were deliberately not vendored.
citation_provenance: retrieved
added: "2026-09-05"
superseded_by: null
---

## Why this entry exists

The post is the contemporaneous expert assessment of the 2015 "unrolled
resultant" formulation of point decomposition over `F_{2^n}` — write the
decomposition as a chain of `S_3` equations through free intermediate points
so that no summation polynomial above `S_3` ever appears. That is the same
chained-`S_3` object this program measures (`EXP-DREG-001`, `KN-FIND-006`)
and asks about (`KN-OPEN-d6ad3f`). Its comment thread also carries three
numerical Gröbner step-degree observations at `n = 40..45` that appear in no
paper this corpus records — they exist only as blog comments. Filed so those
data points, and the memory-cost dispute, can be cited by a stable identifier
instead of being relayed from memory.

The corpus already holds the three preprints the post discusses:
`KN-LIT-009` (Semaev, ePrint 2015/310), `KN-LIT-7604` (Kosters–Yeo,
arXiv:1503.08001) and, for the wider first-fall-degree thread, `KN-LIT-005`
(Petit–Quisquater), `KN-LIT-023` (FPPR), `KN-LIT-024`, `KN-LIT-477`,
`KN-LIT-7607`. Karabina's ePrint 2015/319 has **no** entry (see "Not verified
here"). None of those sources was opened for this entry; everything attributed
to them below is *as relayed by the post*.

## Setting, as the post summarises it

- Semaev's 2004 summation polynomials `S_m(x_1..x_m)` vanish exactly when
  points with those x-coordinates sum to zero on `E(K-bar)`. Gaudry and Diem
  turned this into Weil-descent index calculus over `F_{2^n}`; Diem proved
  subexponential ECDLP along a sequence of *non-prime* `n`.
- Standard parameterisation: factor-base x-coordinates in a `d`-dimensional
  `F_2`-subspace with `m*d ~ n`, and a random point `R` is decomposed by solving
  `S_{m+1}(a_1, .., a_m, x(R)) = 0` — after descent, about `n` Boolean
  equations in about `n` variables. The obstacle is degree: `S_m` has degree
  `2^(m-2)` in each variable, so the descended system has very high degree.
- Prime `n` is the hard case, because the subspace cannot be a subfield.
  Degree reduction via group-action invariants for prime `n`: FGHR
  (`KN-LIT-004`), Huang–Petit–Shinohara–Takagi IWSEC 2013 (no entry in this
  corpus), Galbraith–Gebregiyorgis INDOCRYPT 2014 (`KN-LIT-439`).

## The 2015 proposals, as the post describes them

- **The change of variables.** Unroll the resultant recursion that defines
  `S_m`: introduce free intermediate points `Q_1 = P_1 + P_2`,
  `Q_2 = Q_1 + P_3`, …, `R = Q_{m-2} + P_m`. Only `S_3` (total degree 4) is
  ever used. The system then has `m*d + (m-2)*n ~ (m-1)*n` variables and
  `(m-1)*n` equations, all of total degree 4. Galbraith's reading: an elegant
  choice of variables for a known algorithm, not a new algorithm — he says
  Semaev's title overstates the contribution.
- Both papers assume the Petit–Quisquater first-fall-degree conjecture
  (`KN-LIT-005`) for these systems.
- **Karabina (as relayed).** `m = 5`, targeting `O(q^(2/5))` against Pollard
  rho's `O(q^(1/2))`, `q = 2^n`. Experimental support only up to `n = 19` at
  `m = 5`, and that using `S_4` rather than the full `S_3` chain. Suggested
  crossover against rho only once `2^n > 2^700`.
- **Semaev (as relayed).** `m` grows with `n`; experiments up to `n = 21`,
  `m = 6`. For `n = 571` he proposes `m = 12` and running time
  `O((n(m-1))^(4*omega))`, `omega > 2.3`. The post's PS notes the ePrint
  revision rests on a weaker "Assumption 2" (its statement is not recorded
  here); Galbraith's view is unchanged — insufficient evidence for very large
  `n`.

## Galbraith's objections

1. **Evidence gap.** The conjecture is extrapolated from `n <= 26`, `m <= 6`
   (Karabina, Semaev) to `n = 571`, `m = 12` with *both* parameters growing.
   Kosters–Yeo (`KN-LIT-7604`) computed as far as `n = 40` and read their
   results as evidence *against* the conjecture. If it fails, there is no
   reason to expect these methods to beat rho on prime-degree binary curves.
2. **Memory.** A dense Macaulay-style matrix for a degree-4 system in
   `N = (m-1)*n` Boolean variables has `C(N+3, 4)^2` entries. At `n = 571`,
   `m = 12` that is at least `2^91` bits, needed for *every* relation, and
   (as far as is known) not distributable; the final linear algebra is the
   easier part. Scale comparisons offered: Avogadro's number is about `2^79`;
   the 2013 web was about 4 zettabytes.
   *Re-checked here:* `N = 6281`, `C(6284, 4) = 2^45.88`, squared
   `2^91.77` bits, about `5.3e14` TB; Avogadro `= 2^78.99`; 4 ZB
   `= 2^74.8` bits. The arithmetic is right; the formula is Galbraith's.
3. **Conclusion (2015).** More work is needed on the first-fall conjecture and
   on this algorithm class; at the time of writing there is no serious threat
   to the ECDLP over prime-degree binary fields.

## Comment thread — the data that lives only here

**Semaev, 2015-04-20** (five points):

1. *Sparsity.* Each Boolean equation has at most about `n^3 / m` monomials and
   the whole system about `(n*m)^4 / 4!`; the matrix at `n = 571`, `m = 12`
   then needs about `2^70` bits, not `2^91`; structure could cut it further at
   the cost of time. *Re-checked here:* `(nm)^4/24 = 2^46.38` columns and
   `n^3/m = 2^23.89` nonzeros per row; with row count of the order of the
   column count that is `2^70.3` nonzero positions, matching his figure under
   that reading. The sparsity formulas are his, not re-derived.
2. *Solver.* Use XL with Coppersmith's block Wiedemann instead of F4/F5; cites
   Cheng–Chou–Niederhagen–Yang's parallel XL as evidence the step distributes.
3. *Regularity degree.* The first-fall assumption says the regularity degree of
   these Boolean systems is at most 4. He argues Kosters–Yeo's `n = 40`,
   `m = 2` computation was incomplete and so is not strong evidence of a
   degree above 4, and reports the opposite: 100 random systems at `n = 40`,
   `m = 2` solved in Magma with maximal step degree 4 before the basis was
   found, with possibly "redundant" degree-5/6/7 steps at the very end.
   Karabina's own experiments (`n <= 19`, `m = 5`) are cited as consistent
   with degree at most 4.
4. *Robustness claim.* At `n = 571`, `m = 12` the method would still beat
   Pollard even with regularity degree up to 6, with linear-algebra exponent 3
   as in Magma's Gröbner engine.
5. *Asymptotics.* The bound `2^(c * (n log n)^(1/2))`, `c = 1.69`, survives
   provided the regularity degree grows as `o((n / log n)^(1/2))`.

**Kosters, 2015-05-02:**

- With the Caramel team (Nancy), the `n = 45`, `m = t = 2` computation was
  completed: the Gröbner basis terminated, the system had two solutions, the
  computation **reached step degree 5**, and needed 126 GB of RAM.
- At `n = 25`, `m = t = 3`: when the system has **no** solutions the step
  degree seems to be 4; when it **has** solutions the step degree seems to be 5
  again (that run did not finish after 111 GB, whereas its degree-4 step used
  only 11 GB).

**Gaudry, 2015-05-05:** offers time on a 512 GB machine to anyone whose
experiments on these questions are memory-limited.

**Contradiction, kept visible** (retrieval policy, point 7): Semaev's hundred
random `n = 40`, `m = 2` systems top out at step degree 4; Kosters' solved
`n = 45`, `m = 2` system reached 5. Kosters' own solutions/no-solutions split
suggests a reconciliation — solvable instances climb to 5, unsolvable ones stop
at 4 — but that reading is this entry's inference, not either author's claim,
and neither comment says enough about instance generation to settle it.

## Relevance to this program

1. **Origin of the object.** The chained-`S_3` presentation is exactly the
   object of `EXP-DREG-001` / `KN-FIND-006` and of `KN-OPEN-d6ad3f`. This post
   is where its cost claims, and the objections to them, were first stated in
   public. A proposal on that object cites this entry alongside `KN-LIT-009`.
2. **A null-control caveat, in the quantity this program measures.** Kosters'
   split — step degree 4 without solutions, 5 with — is a reported instance of
   the null object being *easier* than the real one. A degree ceiling measured
   on solution-free systems, which is what a null arm under `KN-TECH-1cd4bb`
   typically is, may under-state the solving degree of solvable instances.
   When null and real arms are compared on solving or step degree, whether the
   instances have solutions is a confound to declare. The direction matters:
   it makes null-derived ceilings optimistic, not conservative.
3. **Memory beside time.** The `2^91` versus `2^70` dispute is a 21-bit
   cost-model disagreement that turns entirely on representation (dense versus
   sparse) and solver (F4 versus XL/Wiedemann). It is the memory column the
   target result profile requires; a cost table for `S_3`-chained descent at
   cryptographic `n` must say which side it takes and why, and neither side
   here was validated beyond `n = 45`.
4. **A conditional claim with its falsification condition attached.**
   Semaev's asymptotic holds if and only if the regularity degree is
   `o((n / log n)^(1/2))`. That is a numbered-heuristic-shaped statement, and
   the direct test is the growth of regularity or step degree in `n` at fixed
   small `m` — on which the thread already places two points, 4 at `n = 40`
   by one account and 5 at `n = 45` by another.
5. **Scale.** Every empirical figure here is at `n <= 45`, `m <= 3` (Kosters)
   or `n <= 26`, `m <= 6` (Semaev, Karabina). Nothing in this entry transfers
   to `n = 571` without the conjecture; the corpus's proved-form context for
   whether it can hold is `KN-LIT-7607` / `KN-LIT-7605`.

## Not verified here

- Semaev 2015/310 (either revision), Karabina 2015/319 and Kosters–Yeo
  1503.08001 were **not** read for this entry; every number attributed to
  them above is as the post relays it.
- The step-degree observations are comment-thread reports. Curve, factor-base
  construction, instance generation, Magma version and monomial order are all
  unstated; Kosters' hedge "seems" is retained deliberately.
- Only arithmetic marked *re-checked* was recomputed. The dense-matrix size
  formula and the sparsity estimates are the respective authors'.
- The reconciliation of the 4-versus-5 contradiction is this entry's
  inference.
- Karabina's paper has no `KN-LIT` entry. The seed bibliography
  (`inputs/bibliography.json`, `karabina_2015_point_decomposition_binary`)
  lists it as arXiv:1504.02347 while the post cites ePrint 2015/319; whether
  those are the same text was not checked.
- Not a peer-reviewed source. Confidence stays `reported` for the technical
  claims; the *existence* of the post and comments, and the figures they
  state, were verified against the live page on 2026-09-05.
