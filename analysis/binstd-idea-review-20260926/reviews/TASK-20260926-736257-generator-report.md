# TASK-20260926-736257 (round 2, seam S4): generator report

Lane: solver structure specific to a curve defined over F_2, for index
calculus on ECC2K-130. Agent: idea-generator (policy research-deep, served by
the session model; no shell, no web). Written 2026-09-26; the lane was
interrupted by a rate limit after the first record was on disk and resumed on
2026-09-28 with no change to that record. No run was launched, no record was
edited, no status changed. Proposals only.

## 1. Records filed

| id | class | question | claim (25 words) | target m | novelty | cost |
| --- | --- | --- | --- | --- | --- | --- |
| IDEA-20260926-9c5694 | control | RQ-CERTBIN-836ce2 | On Koblitz curves (b in F_2) the n conjugates of a target over a non-stable V are n attempts of one target over n conjugate bases (Proposition T); their correlation is bounded below by the base-overlap count; the sound per-instance symmetry group is S_m; exhaustive orbit census at n = 17, 19. | constant (attempt generator; at most about one group op of the m = 4 budget) | unverified | impl low, compute low (minutes; optional closure arm about 2 CPU-h) |
| IDEA-20260926-9cc043 | measurement | RQ-CERTBIN-836ce2 | The direct S_4 descent at m = 3 has Boolean degree at most 6 in 18 variables (exponent weights, x^{2^k} linear); its exact degree, first fall, semi-regular reference D_reg = 10 and W_D refutation cost are measured against the chained system on identical attempts, Koblitz sibling as constant-vector arm. | m = 3 building block; constant (row closed by the product law) | unverified | impl medium, compute medium (10^0 to 10^2 CPU-h) |
| IDEA-20260926-b11cb1 | measurement | RQ-SATIC-1ae57a | Ideal-XG (linearise the restricted system at every node) is a solver-free ceiling for Gaussian elimination in SAT: leaf count 2^{(m-1)l + u*(n)} on the direct model with sum_{i<=m-1} C(u*, i) <= n, exactly enumeration at m = 2 and on chains. | constant (never below the enumeration oracle; closed at every m on ECC2K-130) | unverified | impl medium, compute low (minutes to one CPU-h; engine arm missing: WDSat) |

Unused ids, returned by name: IDEA-20260926-b88409, IDEA-20260926-bb6dd5.
Reason: the two remaining seam items collapsed into propositions already
stated in the corpus (section 4) and were folded into the records above
rather than filed as repackagings.

## 2. Which to test first, and why

IDEA-20260926-9c5694's census. It is the cheapest valid discriminator in the
lane: an exhaustive m = 2 sumset census over the whole subgroup (about 2^17
pair sums per base) on installed pure-Python instruments, with a pre-data
prediction (the overlap term from d_j = dim(V cap sigma^j V), d_1 = 5 at the
n = 17 cell) and a positive control whose answer is forced by proposition
(concordance exactly 1.000 on a stable V). Either outcome is useful: E-OVERLAP
closes two seam items with a number (what the orbit shares on a non-stable V,
and what symmetry breaking is sound), E-EXTRA would be the first
Koblitz-specific coupling between attempts and would go to adversarial review
before any cost reading. Second: IDEA-20260926-b11cb1's l = 6 walk (minutes),
because its E-BELOW outcome is the only thing in this lane that could move a
SAT exponent, and its L1/L2 regressions are exact.

Ranking rationale (information gain against cost): 9c5694 first (exact,
minutes, closes two items or opens one); b11cb1 second (minutes at l = 6,
bounds a lever three records argue about, one outcome exponent-relevant for
the SAT oracle only); 9cc043 third (hours to tens of hours, but it is the
only record that produces a number the m >= 4 pricing seam needs, namely
which m = 3 presentation to price).

## 3. Honest accounting (docs/inventor-protocol.md section 5)

**Objects considered.**
1. The orbit-indexed label vector (chi_V(sigma^j R))_j under Sigma = <sigma>
   (partial action; lossy; filed as 9c5694).
2. The degree-D mutant closure of the direct S_4 ideal, with the presentation
   choice direct/chained as a change of ideal (filed as 9cc043).
3. The linearisation state of the restricted descended system at a DPLL node
   (coordinate-dependent, branching under re-targeting; filed as b11cb1).
4. The descended system's dependence on the curve coefficients (the
   "Koblitz versus ordinary first-fall degree" item): S_{m+1} depends on the
   curve only through b, so at fixed (field, V, x_R) Koblitz and ordinary
   systems differ only in the descended constant vector. Already stated in
   IDEA-20260922-1a081a HB1-1 (rigorous part) and IDEA-20260913-449d2b; folded
   into 9cc043's constant-vector arm, not filed.
5. The per-instance symmetry group of one descended instance (the "symmetry
   breaking respecting equivariance" item): S_m alone at prime n on subspace
   bases, by a77711 Lemmas A1/A2 plus the 29b1c5 review's iota-stability
   arithmetic; folded into 9c5694 as Proposition Sigma, not filed.
6. Normal-basis sparsity of the descent as a per-row / per-conflict constant:
   already the HOLD-I basis design (IDEA-20260922-f37254, 9d12bd, 99294c,
   cdca3a) and proved immaterial for closures by 917981 Proposition B; not
   filed.

**Depth of verified structure.** Propositions T, Sigma (9c5694), the
exponent-weight degree bound and the resultant form of S_4 (9cc043), and
Propositions C, L1, L2 (b11cb1) are this session's derivations at the
"three-line argument" tier; none is machine-checked and each record names its
Stage-0 check. The u*(n) table, the semi-regular D_reg values (8, 9, 10 for
degrees 4, 5, 6 in 18 variables), the Macaulay sizes at N = 18, and d_1 = 5
(n = 17) / d_1 = 17 (n = 131) are hand integer arithmetic labelled derived.
Nothing here is a measurement.

**dominated_by.** Checked row by row against the rendered frontier map (48
rows read) and the product-law table. All three records: n/a (no result
claimed). Per record: 9c5694 is dominated at the cells by oracle A and rho and
at ECC2K-130 by rho's own Frobenius classes (KR-RHO-037e22) and the product
law; 9cc043 by the enumeration oracle (about 2^13 root-findings) at the cell
and by the m = 3 free-oracle floor 2^68.58 on ECC2K-130; b11cb1 by the
(m-1)-fold enumeration of IDEA-20260904-96c4f3 at every m (the ceiling equals
it on chains and exceeds it by 2^{u*(n)} on the direct model) and by rho.

**sota_delta.** Zero on time, memory and data/queries on every ECDLP axis,
for all three records. Against the program's prior state: two propositions
and a pre-priced census (9c5694); the first closure measurement on the direct
S_4 presentation and a presentation comparison on identical attempts
(9cc043); a solver-free ceiling and the (m-1)l + u*(n) law for
Gaussian-elimination-in-SAT reconciling KN-FIND-47da4e, the frozen Trimoska
text and IDEA-20260904-e12b5a (b11cb1).

**Enumerated closures (section 4 standard: obstruction, argument,
redirection).**
- *Per-instance Frobenius symmetry breaking on a subspace base.* Obstruction:
  sigma R != R for R of prime order (a77711 A2), so the shift is an
  equivariance between instances; iota-stable subspaces at prime n are
  b^{1/4} F_{2^d} for d | n (29b1c5 review), so no 2-torsion translation
  preserves an index-calculus subspace. Argument: the stabiliser of one
  instance is S_m (Proposition Sigma in 9c5694). Redirection: orbit-union
  bases carry the orbit symmetry and are priced cost-neutral at m = 2
  (KN-FIND-47da4e, unverified); the m = 3 cell of that comparison is the open
  successor named there.
- *Exact work sharing across the 131 conjugate attempts on a non-stable V.*
  Obstruction: an automorphism of B carrying system(R) to system(sigma R)
  exists iff sigma V = V (917981 Propositions B, F), and no useful stable V
  exists at n = 131 (ord_131(2) = 130, IDEA-20260918-9abf42). Argument:
  Proposition T transports each conjugate attempt to a different base, so the
  conjugates are targets of the affine family E(r) and share only what 5d0b8e's
  retention bounds. Redirection: the conjugates' independence (the overlap
  term, 2^{-64} at (m, l) = (4, 33)) is the usable residue, as a free attempt
  generator inside the per-attempt budget; measured by 9c5694.
- *Gaussian elimination in SAT as an exponent lever.* Obstruction: Proposition
  C orders every linear-consequence refutation below ideal-XG, whose leaf
  count is never below the enumeration oracle 2^{(m-1)l}. Argument: L1, L2
  exact; L3 generic with the collapse located at u*(n). Redirection: the only
  route below the ceiling is nonlinear per-node derivation (IDEA-20260906-
  412391's pass), whose ceiling is the mutant closure's, i.e. the CERTBIN
  refutation-cost lane.
- *Koblitz versus ordinary first-fall degree at matched n.* Obstruction:
  S_{m+1} involves only b, so the descended systems differ only in the
  constant vector; the first fall (KR-IC-f5c584's trace equation) holds for
  every b. Argument: 1a081a HB1-1's rigorous part, 449d2b. Redirection: the
  constant vector is known to move plain M_4 and not W_4 at m = 2 (KN-FIND-
  7c1e94 N-CONVL); 9cc043's constant-vector arm measures it at m = 3; the
  target CLASS (which x are abscissae) is the curve-dependent part and lives
  in IDEA-20260926-a79052 and cafcf1.

**Open directions for the next session.**
1. The m = 3 cell of the orbit-union (representative, shift) comparison
   (KN-FIND-47da4e's own successor), the one place the orbit symmetry could
   still pay on ECC2K-130's stable SETS.
2. If 9cc043 returns E-DIRECT, the S_5 descent at m = 4 (degree at most 12 in
   4l variables by exponent weights) is the presentation to price against the
   m = 4 budget; if E-CHAIN, the chained W-filter of 89886c is.
3. If b11cb1 returns E-BELOW, localise the residual's linear structure (an
   ell-type functional on the last-block univariate); that is the only SAT
   outcome in this lane with exponent content, and it is bounded above by the
   enumeration exponent regardless.
4. A literature pass with retrieval on GGMP's full text (section 4, transport
   and symmetry breaking), on FPPR/PQ12 for the exponent-weight bound, and on
   the XOR-Gauss SAT literature for a linearisation ceiling, before any of the
   three records is labelled above unverified.

## 4. Why fewer than five

Two seam items dissolved into propositions the corpus already carries
(section 3, objects 4 and 5), and one (normal-basis sparsity) is HOLD-I's
filed design. Filing them as records would have been repackaging; folding them
into the three records keeps their content auditable without a duplicate id.
The returned ids are free again for `tools/allocate_id.py`.

## 5. Records read (in full unless noted)

BRIEF.md; BRIEF-ROUND2.md; frontier-map-rendered-20260926.md (all 48 rows);
README.md of this directory; novelty-screen-frontier-map.md (head);
agents/idea-generator.md; docs/object-frame-ideation.md; docs/inventor-
protocol.md sections 4-5; templates/research-records.md ("Prior art on ideas",
"Citation provenance"); IDEA-20260922-845a77; IDEA-20260926-917981, 89886c,
ae8f0a, a79052; titles and claims of every IDEA-20260926-*; IDEA-20260906-
a77711; IDEA-20260923-5d0b8e; the reviews of IDEA-20260922-7ab503, 2a3771,
493606, 77bf31; KN-FIND-5a8d3e, c3a917, 7c1e94, 47da4e; KN-TECH-b18366;
KN-OPEN-3c8f51, 095df5 (head); KN-LIT-7604, 7607, 0d9d28, 005, fa346d (head);
EXP-CERTBIN-e94b27 specification.yaml and impl/README.md, macaulay.py,
gf2n.py (head), closure.py (head), oracles_rc1.py (head); IDEA-20260920-
18dc28; RQ-SATIC-1ae57a; IDEA-20260904-3c7a91; IDEA-20260904-e12b5a (lines
1-130); IDEA-20260906-412391 (lines 1-60); IDEA-20260922-cdca3a; IDEA-
20260922-af7396 (lines 60-150); IDEA-20260915-0d8e90 (lines 1-80); IDEA-
20260922-1a081a (lines 470-514); IDEA-20260913-449d2b (lines 1-40, 612-631);
titles of IDEA-20260922-f37254, 9d12bd, 99294c, 6237e5, IDEA-20260920-b9f0c5,
IDEA-20260913-9ba7fc, 191ed2, IDEA-20260915-3f1964, eee7e4, 7ef636,
IDEA-20260904-96c4f3, 7fd218; inputs/SATIC-TRIMOSKA-2019/paper_fulltext.md at
the lines matching "Gauss" (with context). Corpus greps: "first fall",
"semi-regular", "linearis", "normal basis", "orbit system", "equivarian",
"XOR", "Gaussian elimination", "symmetry breaking", "degree fall",
"circulant", "S_4", "Res_X", "only through b", "Hamming weight of the
exponent". No web search.
