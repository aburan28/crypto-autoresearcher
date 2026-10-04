**Exact factor-base optimization and the two-torsion quotient coordinate**

This continuation replaces the earlier degree-19 sample ranking with exact finite coverage and finds a better base. It also gives the selected base an explicit algebraic membership predicate. The objects studied are finite point sets, rational fibers, sumsets, and Boolean polynomial predicates. No unknown point scalars are recovered.

**The selected base.** Work on

\[
K_1:y^2+xy=x^3+x^2+1,
\quad
\mathbb F_{2^{19}}=\mathbb F_2[z]/(z^{19}+z^5+z^2+z+1).
\]

The group order is 525086=2*262543. Let C consist of the signed Frobenius orbits of the following four points. Integers are polynomial-basis masks in the stated field.

| u-coordinate | y-coordinate |
|---:|---:|
| 6685 | 369649 |
| 8461 | 38471 |
| 25103 | 66503 |
| 32881 | 481942 |

Equivalently, choose these four u-values, close them under u -> u^2, and take both rational points over each resulting coordinate. C has exactly 76 abscissae, 152 nonzero points, and four signed Frobenius orbits. All its points lie in the odd-order subgroup G.

The exact support of sums of at most three points of C contains 237766 of the 262542 nonzero points of G:

\[
\boxed{p=6257/6909=90.5630337241\%.}
\]

The denominator 6909 counts target orbits, each of size 38. Exactly-three-point sums cover 6224 of those orbits, so 33 further target orbits require the two-point branch. Because C is negation-closed and repetitions are permitted, C is contained in C+C+C; the one-point branch adds no further support. Thus the support measured here is 2C union 3C.

The corresponding affine two-torsion-closed lift has 305 points and the same four projected signed orbit columns. Its exactly-three-point support has the same cardinality, by the quotient argument below. This equality concerns support; it does not equate the time needed to find a representation in the two descriptions.

**What was optimized, and what was proved computationally.** The fixed candidate pool consists of 37 distinct signed Frobenius orbits: the earlier five-orbit parent together with the orbits arising from eight prescribed, distinct affine seed domains. Every four-orbit subset of this pool has 152 quotient points. All

\[
\binom{37}{4}=66045
\]

subsets were evaluated exactly. The selected subset is the unique maximizer in this fixed pool. Its zero-based pool indices are [6,9,22,28], in the canonical representative ordering recorded in `orbit-global-n19.jsonl`. This is not a claim of optimality among all factor bases in the field.

| Construction | Quotient points | Signed orbit columns | Exact covered target orbits | Exact coverage |
|---|---:|---:|---:|---:|
| Earlier best four-orbit subset after correcting its sample ranking | 152 | 4 | 6165 / 6909 | 89.2314373% |
| Best of the five exactly checked one-orbit exchange finalists | 152 | 4 | 6184 / 6909 | 89.5064409% |
| Unique optimum among all 66045 subsets of this pool | 152 | 4 | 6257 / 6909 | 90.5630337% |
| Earlier five-orbit parent, expressed in quotient coordinates | 190 | 5 | 6811 / 6909 | 98.5815603% |

The final four-orbit base covers 3496 more nonzero targets than the earlier four-orbit base at unchanged cardinality and orbit count. Across the full four-orbit pool, coverage ranged from 4328/6909 (62.6429%) to 6257/6909. Base size alone therefore does not explain yield.

The earlier 4096-target experiment selected omitted parent orbit 3. Exact enumeration instead gives 6165/6909 for omitted orbit 0 and 6162/6909 for omitted orbit 3. The difference is small but real; the earlier sampled ranking remains an historical observation, not the final choice.

**Why exact coverage is affordable here.** Let pi be Frobenius. A base closed under pi and negation has the same number of unordered representations for R, pi(R), and -R: these maps give bijections of the representing multisets. On the prime-order subgroup, pi acts through a known root lambda of its characteristic polynomial. The action of H=<lambda,-1> on nonzero public subgroup labels is free. At degree 19, |H|=38, and all 262542 nonzero targets are partitioned by 6909 representatives.

The first exact oracle processes one target representative at a time, using pair sums to count every unordered triple with repetitions. Orbit-weighted representation totals must agree with a separate Burnside count of cofactor-admissible multisets. A Python read-back reconstructs the target partition independently from the public characteristic polynomial and checks every total.

For the exhaustive pool optimization, support was cached for each single orbit, each pair of orbits with repetition, and all 9139 triples of orbit types with repetition. In a tuple, choose a summand in its least-indexed orbit and use a signed Frobenius transformation to move that summand to the orbit's fixed representative. The remaining summands stay in their own orbits. Enumerating them therefore gives every target orbit that this orbit-type combination can produce. Conversely every generated sum is an actual tuple, so the support cache is exact.

The support of a chosen four-orbit base is the union of its four single-orbit supports, ten pair-type supports, and twenty triple-type supports. This reduces the final search to bitset unions over the 6909 target orbits. The cache matched all five earlier exact exchange finalists. The selected global maximum was then checked by the separate target-by-target oracle: its support agrees bit for bit, and its complete representation count satisfies the independent symmetric-cube total.

**The quotient coordinate gives a more useful domain description.** For a general ordinary binary curve

\[
E:y^2+xy=x^3+a x^2+b,\qquad c=\sqrt b,
\]

the rational two-torsion point is T=(0,c). For x(P) nonzero, define

\[
u=x+c/x.
\]

The binary addition and doubling formulas give x(P+T)=c/x(P) and x(2P)=u^2. These follow directly from the standard affine formulas in the [Explicit-Formulas Database](https://www.hyperelliptic.org/EFD/g12o/auto-shortw.html).

A constructive rational-fiber description is

\[
x^2+ux+c=0,\qquad w^2+w=u+a,\qquad y=xw+c.
\]

Substituting y into the curve equation verifies the correspondence. For u nonzero, the fiber has four rational points precisely when

\[
\operatorname{Tr}(u+a)=0,
\qquad
\operatorname{Tr}(c/u^2)=0.
\]

Otherwise it has none. At u=0 the first quadratic has a single root; the fiber has two rational points if Tr(a)=0 and none otherwise. The rational two-torsion point lies over the projective u=infinity value and is handled separately.

For Koblitz curves b=1, this becomes Tr(u)=Tr(a) and Tr(1/u)=0. On K_1 with odd extension degree, the conditions are

\[
\boxed{\operatorname{Tr}(u)=1,\qquad\operatorname{Tr}(1/u)=0.}
\]

The finite-group endomorphism psi=pi^(-1) composed with [2] has x-coordinate u=x+1/x; it is the dual Frobenius on these curves. Its kernel is {O,T}. With cofactor two, its image is G and its restriction to G is invertible. The trace homomorphism with kernel 2E is classical; see Proposition 4.2 of [Kosters–Yeo](https://arxiv.org/pdf/1503.08001). For larger cofactors, being in 2E must not be confused with being in the selected prime-order subgroup.

If B# is closed under translation by T and contains the affine two-torsion point, put C=psi(B#) minus {O}. An exactly-three-point decomposition over B# maps to an at-most-three-point decomposition over C. Conversely, a nonzero target represented by at most three points of C can be lifted, filling missing summands with T and correcting the final torsion discrepancy by translating one non-torsion summand. This proves the support equivalence used in the comparisons. In particular the two-summand branch must be retained after passing to quotient coordinates.

Eight exhaustive fiber audits, covering both Koblitz parameters and four general binary curves at degrees seven and nine, verified the translation and doubling identities, the two trace conditions, and every exceptional fiber. They are finite checks of the formulas, not substitutes for the algebraic derivation.

**The selected membership polynomial.** Let M_i(U) be the minimal polynomial over F2 of each of the four selected u-representatives, and put

\[
g(U)=M_1(U)M_2(U)M_3(U)M_4(U).
\]

Each factor is irreducible of degree 19. The polynomial g is squarefree of degree 76 and has exactly the 76 selected abscissae as its roots. The factor base is therefore given exactly by

\[
C=\{(u,v)\in K_1(\mathbb F_{2^{19}}):g(u)=0\}.
\]

In the following binary polynomial masks, bit i is the coefficient of U^i.

| Orbit representative u | Minimal-polynomial mask | Boolean degree upper bound for its descended equation |
|---:|---|---:|
| 6685 | `0xcf9b9` | 4 |
| 8461 | `0xf7761` | 3 |
| 25103 | `0xdf101` | 4 |
| 32881 | `0xc4db5` | 3 |

The product mask is `0x162aacedcc818b84628d`. A separate Python implementation of binary polynomial and finite-field arithmetic verified the modulus, all four minimal polynomials, disjoint Frobenius orbits, squarefreeness, the complete root count, rationality, and both trace predicates. The resulting certificate is `global-selected-predicate-certificate.json`.

The descended product equation has Boolean degree at most six: U^e is a product of wt_2(e) Frobenius-linear maps, and the maximum binary weight among the nonzero exponents is six. This is a syntactic degree bound for the membership predicate, not a solving-degree estimate. A selector formulation can instead choose one of the four factors and guard its coordinate equations; its individual factor equations have the bounds shown above. Neither formulation has a measured coupled SAT solving cost in this mathematical phase.

**Comparisons that did not become the leading base.** Trace-aligned affine seeds A=v0+V, with Tr(v0)=1 and V contained in ker(Tr), give a compact way to satisfy the first quotient condition by construction. Their Frobenius unions are filtered by Tr(1/u)=0. Twenty-five deterministic construction attempts produced eight distinct domains with exactly four signed Frobenius orbits. All eight were evaluated exactly. Their best coverage was 6101/6909, below the earlier 6165/6909 base. Their representation means were nearly identical, while their variances and coverage differed. The final selected base combines individual orbits from this pool; it does not retain an entire affine seed domain.

The degree-17 comparison also completed exact target-orbit censuses. Here #K_1=131174=2*65587, and there are 1929 nonzero target orbits of size 34. For the seed masks [20545,121057,130292], two-torsion closure increased coverage from 1371/1929 to 1785/1929, preserving three projected signed orbit columns. The lifted base grew from 103 to 205 points. A four-column alternative reached 1918/1929, and two seven-column alternatives covered every nonzero target. Thus the usefulness of torsion closure transfers to another field degree, while the preferred orbit count changes.

**Evidence and remaining boundary.** The earlier source artifacts are preserved. `protocol.json`, the subsequent stage protocols, source snapshots, and the final manifest identify the successive implementations and input sets. `verification.txt` records the independent partition/count checks. The optimization result is exact for the specified curve, allowed decomposition lengths, and fixed pool of 37 orbits. Expanding that pool, changing the field degree, optimizing a different summand count, or including the cost of solving the coupled Semaev system is a different comparison.

Reproduction commands:

```sh
cp research/sat_factor_base_review_20260908/continuation-01/source_snapshots/Cargo.lock Cargo.lock
cargo run --release --example koblitz_factor_base_math -- research/sat_factor_base_review_20260908/yield-n19.jsonl 1 two-torsion 0 --exact-orbits
cargo run --release --example koblitz_affine_quotient_base -- 19 --exchange research/sat_factor_base_review_20260908/continuation-01 --global-pool
python3 research/sat_factor_base_review_20260908/continuation-01/global_predicate_certificate.py
python3 research/sat_factor_base_review_20260908/continuation-01/verify_continuation.py
```

The repository ignores its root `Cargo.lock`; the preserved snapshot pins the dependency resolution recorded by the final manifest. Use new output files for repetitions. The pool construction reads the preserved affine seed records; it does not regenerate a different pool during global optimization.
