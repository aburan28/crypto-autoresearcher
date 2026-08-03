# Literature Map: Recursive Expansion and Coordinate-Defined ECDLP Decomposition

Date: 2026-07-17
Target context (read-only): `/Volumes/Volume/crypto-autoresearcher-worktrees/coordinate-energy/notes/coordinate_decomposition_theories_20260717.md`
Scope: coordinate-defined elliptic-curve factor bases, summation-polynomial point decomposition, rational-map factor bases, additive energy and sumset expansion, fixed-curve preprocessing, and structured generic-group lower bounds.

## Executive assessment

The nearest established line is not a single paper but the intersection of five mature subjects:

1. Semaev-style factor bases and summation-polynomial point decomposition;
2. Gaudry/Diem/Joux--Vitse index calculus over extension fields and Weil restrictions;
3. Petit--Kosters--Messeng low-description-complexity factor bases defined by composed rational or algebraic maps over prime fields;
4. additive-combinatorial energy, doubling, and generalized-birthday methods for controlling intermediate sumsets; and
5. generic and structured-generic lower bounds, including preprocessing/advice tradeoffs.

The following status boundaries are the main conclusions.

- `ESTABLISHED`: coordinate-defined factor bases are standard. Examples include small-coordinate sets, subfield/vector-subspace coordinate sets, roots of quasi-subfield polynomials, and zero sets of high-degree polynomials represented as compositions of low-degree maps.
- `ESTABLISHED`: Semaev summation polynomials exactly encode whether chosen $x$-coordinates can be completed to curve points whose signed sum is zero, subject to base-field and sign checks.
- `ESTABLISHED`: relation-count heuristics in this literature normally quotient permutation symmetry, producing an $m!$ denominator. Symmetric polynomial systems, torsion quotients, and other orbit reductions are also standard.
- `HEURISTIC/PARAMETER-LIMITED`: the cost of solving the resulting polynomial systems, their degree of regularity, and their cryptographic-scale behavior are not generally proved. Prime-field rational-map experiments remain small-parameter results.
- `INFERENCE`: replacing $B^m/m!$ by the exact number $\binom{B+m-1}{m}$ of unordered multisets with repetition is a routine finite-$B$ correction, not a supported novelty claim. It is exact only as a domain count; it does not determine the number of distinct elliptic-curve sums.
- `INFERENCE`: Poisson occupancy $1-\exp(-M/N)$, with $M=\binom{B+m-1}{m}$, is a random-map model for distinct-target coverage, not an elliptic-curve theorem. Dependencies, repeated points, signs, and sum collisions must be measured or bounded.
- `OPEN`: no primary source located in this search states and optimizes the exact joint objective “retain near-random final $mF$ expansion while admitting a materially compressed exact representation of intermediate elliptic-curve sumsets.” Its components are standard; the combination should be described as an open synthesis or literature gap, not as novel.
- `MODEL-BOUND`: Shoup-type, preprocessing, and 2026 structured-generic lower bounds constrain algorithms only after the relevant representation has been embedded in their model. They do not establish impossibility for coordinate or rational-map algorithms.

No source found establishes a better-than-rho algorithm for general prime-order elliptic curves over large prime fields from these ingredients.

## 1. Counting model and terminology

Let $G=\langle P\rangle$ be a prime-order subgroup of $E(\mathbb F_p)$ of order $N$, let $F\subseteq G$ contain $B$ actual group elements, and let

\[
mF=\{P_1+\cdots+P_m:P_i\in F\}.
\]

The counting object must be fixed before applying any occupancy formula.

- Ordered tuples with repetition: $B^m$.
- Unordered multisets with repetition: $M_{\mathrm{multi}}=\binom{B+m-1}{m}$.
- Unordered subsets without repetition: $M_{\mathrm{distinct}}=\binom{B}{m}$.
- As $B\to\infty$ with fixed $m$, $M_{\mathrm{multi}}=B^m/m!+O(B^{m-1})$.

The image size obeys only

\[
|mF|\le \min(N,M),
\]

where $M$ is the chosen domain count. Equality need not hold because different multisets can have the same group sum. Under an explicit independent-uniform random-map model from $M$ domain elements to $G$, the expected occupied fraction is

\[
1-\left(1-\frac1N\right)^M\approx 1-e^{-M/N}.
\]

`INFERENCE`: this random-occupancy formula is a useful null model. It is not implied by Semaev's polynomial identity, by a factor-base cardinality estimate, or by low additive energy alone.

### Sign and coordinate warning

For a short Weierstrass curve, one $x$-coordinate usually corresponds to $P$ and $-P$. A set of $B$ coordinates is therefore not automatically a set of $B$ group elements. Semaev's equations existentially quantify compatible signs. Consequently:

- a sign-complete point factor base and a sign-canonical coordinate quotient have different atomic objects;
- permutation and sign orbits must not be counted twice;
- the binomial count applies only after the actual atoms, repetition policy, and orbit convention are fixed; and
- every decomposed target still requires an exact point-level witness check.

## 2. Coordinate-defined factor bases and summation-polynomial decomposition

### 2.1 Semaev summation polynomials

**Primary source.** Igor Semaev, “Summation polynomials and the discrete logarithm problem on elliptic curves,” IACR ePrint 2004/031: <https://eprint.iacr.org/2004/031>.

**Exact established claim.** For a Weierstrass elliptic curve, Semaev defines symmetric polynomials $S_m(x_1,\ldots,x_m)$ such that $S_m=0$ precisely when, over an algebraic closure, there exist curve points with those $x$-coordinates whose sum is the identity. For $m\ge3$, the degree in each variable is $2^{m-2}$. The recursive resultant construction is exact.

**Assumptions and boundary.** The polynomial criterion is over the algebraic closure. A cryptanalytic decomposition over $\mathbb F_p$ must additionally ensure that all required points and signs are $\mathbb F_p$-rational. Semaev's small-$x$ prime-field factor base supplies a coordinate predicate, but the paper's speedup depends on efficiently solving the bounded modular polynomial equations; it is not an unconditional general-prime-field ECDLP improvement.

**Relevance.** This is the direct algebraic compiler for the target note's point-decomposition predicate. Its symmetry explains why unordered tuples, rather than all $B^m$ orderings, are the natural relation objects.

### 2.2 Gaudry and Diem: subfield/vector-space coordinate bases

**Primary sources.**

- Pierrick Gaudry, “Index calculus for abelian varieties of small dimension and the elliptic curve discrete logarithm problem,” *Journal of Symbolic Computation* 44(12), 2009, 1690--1702. DOI: <https://doi.org/10.1016/j.jsc.2008.08.005>.
- Claus Diem, “On the discrete logarithm problem in elliptic curves,” *Compositio Mathematica* 147(1), 2011, 75--104. DOI: <https://doi.org/10.1112/S0010437X10005075>.

**Established/heuristic claims.** Gaudry uses a factor base whose $x$-coordinates lie in a proper subfield and applies Weil restriction to transform summation-polynomial decomposition into a multivariate system over the subfield. For fixed extension degree $n$, the resulting heuristic attack is commonly stated at $\widetilde O(q^{2-2/n})$ field-scale work, with constants that grow rapidly in $n$. Diem proves expected $(q_i^{n_i})^{o(1)}$ time for sequences with $n_i\to\infty$ and $n_i/\log q_i\to0$, and constructs a sequence with expected $\exp(O((\log q_i)^{2/3}))$ time. These are extension-field sequence results, not a theorem for arbitrary prime fields.

**Assumptions and boundary.** The useful coordinate structure comes from extension-field subfields or vector spaces. It is absent when $\mathbb F_p$ has no proper subfield. Weil restriction also changes the number and degree of equations, so small extension degree and solver behavior are essential parameters.

**Relevance.** These papers establish that a coordinate set can be both low-description and decomposition-useful when a genuine subfield geometry exists. They do not provide the target note's desired compressed intermediate EC sumsets over a prime field.

### 2.3 Joux--Vitse and algebraic-system refinements

**Primary sources.**

- Antoine Joux and Vanessa Vitse, “Elliptic Curve Discrete Logarithm Problem over Small Degree Extension Fields,” *Journal of Cryptology* 26, 2013, 119--143. IACR ePrint 2010/157: <https://eprint.iacr.org/2010/157>; DOI: <https://doi.org/10.1007/s00145-011-9116-z>.
- Antoine Joux and Vanessa Vitse, “Cover and Decomposition Index Calculus on Elliptic Curves Made Practical,” IACR ePrint 2011/020: <https://eprint.iacr.org/2011/020>.
- Jean-Charles Faugère, Ludovic Perret, Christophe Petit, and Guénaël Renault, “Improving the Complexity of Index Calculus Algorithms in Elliptic Curves over Binary Fields,” EUROCRYPT 2012. DOI: <https://doi.org/10.1007/978-3-642-29011-4_4>.
- Jean-Charles Faugère, Sylvain Huot, Antoine Joux, Guénaël Renault, and Vanessa Vitse, “Symmetrized Summation Polynomials: Using Small Order Torsion Points to Speed Up Elliptic Curve Index Calculus,” EUROCRYPT 2014. DOI: <https://doi.org/10.1007/978-3-642-55220-5_3>.

**Established/empirical claims.** Joux--Vitse reduce an (n)-point decomposition to (n-1) points over small-degree extension fields, trading relation probability for substantially smaller systems. Their cover/decomposition implementation solved a 149-bit subgroup instance over a degree-six extension after large but finite computational effort. Faugère--Perret--Petit--Renault exploit multihomogeneous polynomial structure, but their asymptotic solver estimate is explicitly heuristic. Faugère et al. quotient by translations by small torsion, reducing factor-base and polynomial-system symmetry; their concrete computations remain parameter-limited.

**Relevance.** Symmetry-aware compilation, reduced decomposition arity, and recursive polynomial structure are established. These works compress the *algebraic system*, not an exact set of intermediate EC sums. They are therefore close controls for Theory 1 but not prior instances of the full expansion--compression objective.

## 3. Rational-map and low-description factor bases over prime fields

### 3.1 Petit--Kosters--Messeng

**Primary source.** Christophe Petit, Michiel Kosters, and Ange Messeng, “Algebraic Approaches for the Elliptic Curve Discrete Logarithm Problem over Prime Fields,” PKC 2016, pp. 3--18. DOI: <https://doi.org/10.1007/978-3-662-49387-8_1>; author PDF: <https://www.iacr.org/archive/pkc2016/96140156/96140156.pdf>.

**Exact construction.** The paper considers factor bases of the form

\[
F_L=\{(x,y)\in E$\mathbb F_p$:L$x$=0\},
\]

where a large-degree polynomial or rational relation (L) has a short description as a composition of low-degree maps. Instead of expanding (L), the point-decomposition system introduces a chain of auxiliary variables for the map composition and combines it with a Semaev equation.

The paper gives two important source families:

1. roots forming a coset of a smooth-order subgroup of $\mathbb F_p^\times$, requiring suitable smooth structure in $p-1$; and
2. $x$-coordinates of a coset of a smooth subgroup on an auxiliary elliptic curve, represented through a chain of low-degree isogenies.

The auxiliary curve is not a transfer of the target ECDLP; it is a device for defining the target curve's factor-base coordinates.

**Heuristic relation model.** The expected number of decompositions is modeled as approximately

\[
\frac{$\deg L$^m}{m!p}.
\]

Their rough total-cost model is

\[
P(p,m)+\frac{m!p}{(\deg L)^{m-1}}\,T(E,m,L)+(\deg L)^\omega,
\]

where $P$ is factor-base preprocessing, $T$ is one point-decomposition solve cost, and the final term models linear algebra. In the balanced regime $(\deg L)^m\approx m!p$, a generic improvement would require the decomposition system to be solved below the corresponding square-root-scale threshold. The authors label this a rough model; their algorithms are practical only for small parameters and asymptotic conclusions are limited by incomplete Gröbner-basis complexity knowledge.

**Fixed-curve preprocessing.** Searching for an auxiliary map/curve is charged as preprocessing. For one proposed auxiliary-curve family, the random search estimate is parameter-dependent and is argued to be dominated by later linear algebra in the intended regime. This is a heuristic attack accounting, not a free-advice theorem.

**Relevance.** This is the closest direct prior art to “a union of shallow rational-map images with compact source circuits.” It establishes compact source descriptions and chain-constrained decomposition systems. It does not show that cross-component intermediate EC sums have compressed exact representations or that final sums retain random-like support.

### 3.2 Quasi-subfield polynomial factor bases

**Primary source.** Ming-Deh Huang, Michiel Kosters, Christophe Petit, Sze Ling Yeo, and Yang Yun, “Quasi-subfield Polynomials and the Elliptic Curve Discrete Logarithm Problem,” *Journal of Mathematical Cryptology* 14(1), 2020, 25--38. DOI: <https://doi.org/10.1515/jmc-2015-0049>.

**Exact/conditional claim.** The authors define nearly split polynomials of the form $X^{q^{n'}}-\lambda(X)$ with low-degree $\lambda$, use their roots as factor-base coordinates, and derive conditional complexity estimates for extension-field ECDLP. The paper explicitly leaves open whether sufficiently favorable polynomials exist to beat the best generic algorithms.

**Counting relevance.** The analysis uses the common heuristic that most unordered $m$-tuples produce distinct sums and therefore models relation probability with an $m!$ symmetry denominator. This is strong evidence that unordered/permutation-corrected counting is standard in the index-calculus literature.

**Boundary.** This is principally an extension/composite-field construction. It neither proves random occupancy nor yields the target prime-field expansion--compression property.

### 3.3 Deterministic encodings as a missing source-map comparator

**Primary sources.**

- Pierre-Alain Fouque, Antoine Joux, and Mehdi Tibouchi, “Injective Encodings to Elliptic Curves,” ACISP 2013. DOI: <https://doi.org/10.1007/978-3-642-39059-3_14>.
- Daniel J. Bernstein, Mike Hamburg, Anna Krasnova, and Tanja Lange, “Elligator: Elliptic-curve points indistinguishable from uniform random strings,” ACM CCS 2013. DOI: <https://doi.org/10.1145/2508859.2516734>.
- David Kumallagov, “Exact output statistics of Icart's encoding in exceptional $j=0$ case,” arXiv:2606.07390: <https://arxiv.org/abs/2606.07390>.

**Established claims.** The first two papers construct efficient, invertible or injective maps from field-like sources into large subsets of suitable elliptic curves. Kumallagov gives exact image, fibre, collision, entropy, and character-energy statistics for a current, exceptional $j=0$ Icart-encoding case.

**Relevance and boundary.** These papers show that “compact source circuit plus large EC image” is already standard. They do not claim that source tags compose cheaply under EC addition, that the image has random-like $m$-fold group-sum expansion, or that such an encoding speeds ECDLP. The $j=0$ statistics are special-family evidence, not a general-curve theorem.

## 4. One-relation and complete-attack comparisons

**Primary source.** Alessandro Amadori, Federico Pintore, and Massimiliano Sala, “On the discrete logarithm problem for prime-field elliptic curves,” *Finite Fields and Their Applications* 51, 2018, 168--182. IACR ePrint 2017/609: <https://eprint.iacr.org/2017/609>; DOI: <https://doi.org/10.1016/j.ffa.2018.01.009>.

**Claim.** The paper samples a target-dependent factor base from random known combinations of $P$ and (Q) and seeks a zero-sum relation, avoiding the conventional large relation matrix in its proposed setup. Its evidence is small-parameter and does not establish a large-prime-field break.

**Relevance.** It is an important control against optimizing the wrong objective. A factor base with favorable coverage can still lose once the number of relations, matrix rank, individual logarithm phase, or target descent is charged. Conversely, a one-relation design changes those requirements entirely. Any recursive-expansion proposal must specify which complete attack it serves.

## 5. Additive energy, doubling, and elliptic-coordinate expansion

### 5.1 What additive energy proves

For a finite subset (A) of an abelian group, define

\[
E(A)=|\{$a_1,a_2,a_3,a_4$\in A^4:a_1+a_2=a_3+a_4\}|.
\]

Cauchy--Schwarz gives the exact elementary inequality

\[
E(A)\ge \frac{|A|^4}{|A+A|}.
\]

Thus high pair energy forces compressed pair sums. The converse direction requires structural theorems or additional hypotheses; pair energy alone does not determine $|mA|$, target occupancy, or the cost of representing exact witnesses.

**Primary sources.**

- Ben Green and Imre Ruzsa, “Freiman's theorem in an arbitrary abelian group,” arXiv:math/0505198: <https://arxiv.org/abs/math/0505198>; DOI: <https://doi.org/10.1112/jlms/jdl021>.
- Christian Reiher and Tomasz Schoen, “Note on the theorem of Balog, Szemerédi, and Gowers,” *Combinatorica* 44, 2024. DOI: <https://doi.org/10.1007/s00493-024-00092-5>.

**Established claims.** Green--Ruzsa show that small-doubling subsets of arbitrary abelian groups lie inside quantitatively controlled coset progressions. Balog--Szemerédi--Gowers-type results, including the sharper Reiher--Schoen form, extract a large small-doubling subset from a set with large additive energy.

**Prime-order EC interpretation.** A prime-order EC subgroup has no proper nontrivial subgroups, removing one source of coset structure, but it still contains arithmetic-progression-like subsets under a chosen generator. These theorems characterize additive structure abstractly; they do not make that structure accessible from public curve coordinates without knowing discrete-log labels.

**Relevance.** Energy is a standard diagnostic for intermediate collision/compression. The target objective is deliberately antagonistic: it seeks enough intermediate structure to save work without allowing that structure to suppress final expansion. The literature implies that this balance should be measured at every depth $j$, not inferred from (E$F$) alone.

### 5.2 Coordinate-set expansion results on elliptic curves

**Primary sources.**

- Omran Ahmadi and Igor Shparlinski, “On the Sum-Product Problem on Elliptic Curves,” arXiv:0806.0640: <https://arxiv.org/abs/0806.0640>.
- Omran Ahmadi and Igor Shparlinski, “Exponential Sums over Points of Elliptic Curves,” arXiv:1302.4210: <https://arxiv.org/abs/1302.4210>.
- David Kohel and Igor Shparlinski, “On Exponential Sums and Group Generators for Elliptic Curves over Finite Fields,” ANTS-IV, LNCS 1838, 2000, pp. 395--404. Author PDF: <https://www.i2m.univ-amu.fr/perso/david.kohel/pub/character.pdf>.

**Established claims.** These papers bound character/exponential sums and prove expansion or equidistribution statements involving elliptic-curve coordinates. Ahmadi--Shparlinski show that certain pairs of coordinate-additive and scalar-multiplicative images cannot both be small, and later improve bilinear-sum bounds with applications to distributions of EC-derived sets. Kohel--Shparlinski use exponential-sum bounds to obtain deterministic $O(q^{1/2+\varepsilon})$ group-generator algorithms.

**Boundary.** These results concern field addition of coordinates, scalar products, coordinate images of EC addition, or sets above roughly square-root-scale thresholds under stated assumptions. They do not directly bound $|mF|$ for a small coordinate-defined factor base $B\asymp q^{1/m}$, and the $x$-map loses sign information.

**Relevance.** Character-sum measurements are justified as possible signature-routing diagnostics. The current theorems do not establish a nontrivial routing advantage in the target parameter regime; a shuffled-signature control remains necessary.

## 6. Generalized birthday algorithms and compressed joins

**Primary source.** David Wagner, “A Generalized Birthday Problem,” CRYPTO 2002. DOI: <https://doi.org/10.1007/3-540-45708-9_19>; paper: <https://www.iacr.org/archive/crypto2002/24420288/24420288.pdf>.

**Established claim.** Wagner gives tree algorithms for finding one element from each of several independent lists whose XOR is zero. Intermediate lists are kept small by imposing progressively stronger partial-sum constraints. For four lists this gives the familiar cube-root-scale regime; larger list counts give further generalized-birthday tradeoffs under the model's independent-list and bitwise-filter assumptions.

**Primary occupancy analysis.** Anna Lindo and Serik Sagitov, “Asymptotic results for the number of Wagner's solutions to a generalised birthday problem,” arXiv:1507.05490: <https://arxiv.org/abs/1507.05490>, studies Poisson approximation and the fraction of all random solutions recovered by Wagner filtering.

**Relevance and boundary.** Wagner is the closest standard algorithmic analogue of “compressed intermediate joins with a surviving final solution.” Its compression comes from discarding partial sums using a homomorphic bit constraint over XOR and from using separately sampled lists. EC addition does not supply the same coordinate-bit homomorphism. Reusing one unordered factor base also introduces dependencies. Any claimed recursive-join gain must therefore be compared with a colored-list Wagner control and must charge witness loss caused by filters.

## 7. Fixed-curve preprocessing and advice/online tradeoffs

### 7.1 Generic DLP with preprocessing

**Primary sources.**

- Henry Corrigan-Gibbs and Dmitry Kogan, “The Discrete-Logarithm Problem with Preprocessing,” EUROCRYPT 2018. IACR ePrint 2017/1113: <https://eprint.iacr.org/2017/1113>; DOI: <https://doi.org/10.1007/978-3-319-78375-8_14>.
- Lior Rotem and Gil Segev, “A Fully Constructive Discrete-Logarithm Algorithm with Preprocessing,” ITC 2022. DOI: <https://doi.org/10.4230/LIPIcs.ITC.2022.12>.
- Ueli Maurer, Christopher Portmann, and Jiamin Zhu, “Unifying Generic Group Models,” IACR ePrint 2020/996: <https://eprint.iacr.org/2020/996>.

**Restricted theorem.** In a prime-order generic group of size $N$, Corrigan-Gibbs--Kogan prove, up to logarithmic factors, an advice/online lower bound of the form

\[
S T^2=\widetilde\Omega$\varepsilon N$,
\]

where $S$ is advice size, $T$ is online group-operation cost, and $\varepsilon$ is success probability. They also give a preprocessing-time tradeoff of the form $PT+T^2=\Omega(\varepsilon N)$. Rotem--Segev give a fully constructive matching upper-bound family up to logarithmic factors. Maurer--Portmann--Zhu reconcile model variants and close gaps between upper- and lower-bound formulations.

**Relevance.** A fixed-curve coordinate compiler must report at least preprocessing work $P$, stored advice $S$, online work $T$, success probability, and target multiplicity/batch size. An apparent $N^{1/3}$ online result with $N^{1/3}$ advice is compatible with the generic frontier and is not by itself a non-generic break.

**Boundary.** Coordinate predicates, field arithmetic, rational maps, and polynomial solving are deliberately non-generic. The theorem is a baseline and accounting discipline, not a proof that those methods cannot improve.

### 7.2 Nonuniform fixed-curve framing

**Primary source.** Daniel J. Bernstein and Tanja Lange, “Non-uniform cracks in the concrete: the power of free precomputation,” ASIACRYPT 2013, IACR ePrint 2012/318: <https://eprint.iacr.org/2012/318>.

**Relevance.** This paper explains why standard, widely reused groups require explicit nonuniform/fixed-instance accounting. It motivates amortization studies but does not make precomputation free in a security claim.

## 8. Generic and structured-generic lower bounds

### 8.1 Shoup's generic-group lower bound

**Primary source.** Victor Shoup, “Lower Bounds for Discrete Logarithms and Related Problems,” EUROCRYPT 1997. DOI: <https://doi.org/10.1007/3-540-69053-0_18>.

**Restricted theorem.** In the generic-group model, an algorithm solving DLP in a group whose order has a large prime factor needs square-root-many oracle operations for constant success, up to the theorem's exact probability parameters.

**Boundary.** The encoding is random and the algorithm sees only group-oracle behavior. Coordinate equations, endomorphisms, rational maps, and field structure are outside the plain model. Therefore this theorem does not rule out the target hypothesis.

### 8.2 Structured generic-group model, including preprocessing

**Current primary source.** Henry Corrigan-Gibbs, Alexandra Henzinger, and David J. Wu, “The Structured Generic-Group Model,” EUROCRYPT 2026, IACR ePrint 2026/384. Project page: <https://people.eecs.berkeley.edu/~henrycg/pubs/structured-generic-groups/>; paper: <https://www.cs.utexas.edu/~dwu4/papers/SGGM.pdf>.

**Restricted theorem.** The model supplements generic group labels with a free partial operation that agrees with the true group operation on the structured portion of the representation. If at most a $\delta$ fraction of labels are constrained by this structure, their DLP lower bound has the form

\[
\Omega\left(\min(\sqrt q,1/\delta)\right)
\]

for a prime-order group of size $q$, under the paper's precise structured-generic model. The preprocessing appendix gives a hard-distribution advantage upper bound, up to logarithmic factors, of the form

\[
\widetilde O$ST^2/q+\delta T$.
\]

The paper also applies the framework to several concrete structure classes, including elliptic-curve points, under explicit partial-operation definitions.

**Relevance.** This is the closest lower-bound language for source-tagged partial composition. To invoke it for recursive expansion, one must:

1. define the free partial operation $\star$ represented by the source tags;
2. prove when $\star$ equals true EC addition;
3. bound the constrained fraction $\delta$, possibly separately at each join depth;
4. map stored circuits/tables to $S$ bits and all remaining group work to $T$; and
5. respect the theorem's hard-distribution and model assumptions.

**What it does not prove.** A coordinate predicate or short source description does not automatically provide a free partial group operation. Conversely, rapidly expanding intermediate sets may increase the structured domain while destroying compressibility. No direct corollary found in the paper settles the target joint objective for coordinate-defined EC factor bases.

## 9. Pollard rho, endomorphisms, and the correct baseline

**Primary sources.**

- John M. Pollard, “Monte Carlo Methods for Index Computation (mod (p)),” *Mathematics of Computation* 32(143), 1978, 918--924. DOI: <https://doi.org/10.1090/S0025-5718-1978-0491431-9>.
- Robert Gallant, Robert Lambert, and Scott Vanstone, “Faster Point Multiplication on Elliptic Curves with Efficient Endomorphisms,” CRYPTO 2001. DOI: <https://doi.org/10.1007/3-540-44647-8_11>.
- Joppe Bos, Thorsten Kleinjung, and Arjen Lenstra, “On the Use of the Negation Map in the Pollard Rho Method,” ANTS-IX, 2010. DOI: <https://doi.org/10.1007/978-3-642-14518-6_9>.

**Established baseline.** Pollard rho gives square-root expected group-operation complexity and negligible storage in the random-walk model. Parallel collision search changes wall time but not total generic work. Efficient automorphisms can quotient the walk by small orbits; negation and GLV/GLS/Frobenius structure normally give constant-factor or orbit-size square-root gains, with implementation caveats such as short cycles.

**Relevance.** A coordinate-energy candidate must compare against the automorphism-aware rho appropriate to the fixed curve, count field and group operations, report memory and parallelism, and separate a many-target amortized gain from a single-target break.

## 10. Is the unordered-multiset occupancy correction standard?

### Verdict

`ESTABLISHED`: quotienting order/permutation symmetry is standard. Semaev polynomials are symmetric; prime-field and extension-field index-calculus analyses routinely divide expected relation counts by $m!$; torsion symmetrization and related orbit reductions go further.

`ELEMENTARY REFINEMENT`: for exactly $B$ distinguishable factor-base points with repetition allowed, replacing $B^m/m!$ by

\[
\binom{B+m-1}{m}
\]

is the exact stars-and-bars count. The asymptotic $B^m/m!$ used in the literature is its leading term. This exact finite-size replacement should not be called novel.

`HEURISTIC`: converting that domain count into target coverage with

\[
1-\exp\left$-\binom{B+m-1}{m}/N\right$
\]

assumes near-independent uniform sums. The closest ECDLP papers use the corresponding low-density expected-solution heuristic; they do not prove the full saturation curve for a structured coordinate factor base.

`OPEN`: the correction may still be operationally important because a factor $m!$ materially changes toy and crossover parameters. The publishable question would not be the binomial identity, but a theorem or reproducible empirical law controlling collision multiplicities and occupancy for a specified family of coordinate-defined EC sets.

### Required checks before using the formula

1. Is $B$ counting coordinates, sign classes, or actual points?
2. Are repeated factor-base elements allowed by the decomposition algorithm?
3. Is the target relation ordered, unordered, or quotiented by a larger automorphism group?
4. How many different multisets map to each group sum?
5. Are exceptional tuples with $P=-P$, repeated coordinates, poles, or points at infinity handled?
6. Does the solver enumerate all witnesses or only one representative per algebraic component?

## 11. Is the expansion--compression objective standard?

### What is already standard

- Final relation probability or image size as an attack parameter: Semaev, Gaudry, Diem, Joux--Vitse, Petit--Kosters--Messeng.
- Compact coordinate-source maps and composed constraints: Petit--Kosters--Messeng, quasi-subfield polynomials, Icart-type maps, Elligator, injective encodings.
- Symmetry compression of polynomial systems: symmetric Semaev equations and torsion quotients.
- Intentionally pruned intermediate joins: Wagner generalized birthday algorithms.
- Energy, small doubling, and structured-subset consequences: additive combinatorics.
- Advice/online and preprocessing/online tradeoffs: generic DLP preprocessing literature.
- Partial-operation structure as a lower-bound parameter: the structured generic-group model.

### What was not found as a standard named objective

No primary source located here jointly optimizes all of the following for the same prime-field EC factor-base family:

1. near-random support or occupancy of the final (mF);
2. exact, witness-preserving compression of one or more intermediate (jF);
3. a source-tag composition rule cheaper than enumerating those sums;
4. charged fixed-curve preprocessing and stored advice;
5. a complete relation-generation/linear-algebra/target-descent attack; and
6. comparison against automorphism-aware rho and generic preprocessing frontiers.

`INFERENCE`: the target objective is best described as a synthesis of standard themes and an open comparison framework. This search does not support saying that the objective, its terminology, or any specific construction is novel. A novelty claim would require broader citation chaining and, more importantly, a concrete construction whose joint bounds differ from the ingredients above.

## 12. Relevance to the three theories in the target note

### Theory 1: symmetry-corrected split compiler

**Closest work.** Semaev symmetry, $m!$-corrected relation estimates, Joux--Vitse arity reduction, and torsion-symmetrized summation polynomials.

**Assessment.** The occupancy correction is sound as a null-model calibration, but the combinatorial identity is standard. The research content lies in measuring or proving the multiset-to-sum collision law and in showing that a split compiler reduces actual work after witness verification.

**Missing proof obligation.** Bound or measure the multiplicity distribution of the map $\operatorname{Sym}^m(F)\to G$, not merely its domain size.

### Theory 2: union of shallow rational-map images

**Closest work.** Petit--Kosters--Messeng, quasi-subfield polynomials, deterministic EC encodings, and Wagner's tree joins.

**Assessment.** Compact source circuits and unions/cosets of map images have strong precedent. The unsupported step is that cross-component EC sums remain random-like while intermediate joins admit exact compressed source-tag representations.

**Missing proof obligation.** Exhibit a partial composition law or data structure whose build/query cost and advice size are below flat meet-in-the-middle while preserving the claimed final coverage.

### Theory 3: coordinate-signature batch routing

**Closest work.** Character-sum/equidistribution results for EC coordinates, source encodings, and generalized-birthday filters.

**Assessment.** Routing by coordinate predicates is standard in spirit, but no source found proves useful correlation at $B\asymp q^{1/m}$ for a general prime-field curve. A route that only partitions uniformly random candidates gives no intrinsic gain after false positives and verification are charged.

**Missing proof obligation.** Demonstrate predictive mutual information between the signature and successful join buckets against a shuffled-label control, then account for all rejected and verified candidates.

## 13. Missing comparisons that should be added before any novelty or speed claim

1. **Wagner/colored-list control.** Split one factor base into independently colored lists and compare flat MITM with Wagner-style filtering at equal witness success.
2. **Petit--Kosters--Messeng systems.** Use their composed-map/Semaev chain as the direct rational-map baseline, not only ad hoc coordinate maps.
3. **Deterministic-encoding images.** Test Icart/Fouque--Joux--Tibouchi/Elligator-compatible images where the source map is already compact and well studied.
4. **One-relation method.** Compare with Amadori--Pintore--Sala to avoid assuming that full relation collection and linear algebra are mandatory.
5. **Complete attack costs.** Include relation count, rank, sparse linear algebra, and individual-log/target descent, not just target membership in (mF).
6. **Generic preprocessing frontier.** Report $P,S,T,\varepsilon$, batch size, memory bytes, and memory traffic against $ST^2\$ and $PT+T^2\$ bounds.
7. **Structured-generic embedding.** Define the partial operation and estimate its structured fraction $\delta$; do not cite the 2026 theorem without this mapping.
8. **Automorphism-aware rho.** Include negation and every efficiently computable endomorphism available on the tested curve.
9. **Field-family controls.** Separate prime fields, binary fields, extension fields, ordinary/supersingular curves, and exceptional-$j$ encodings.
10. **Sign/orbit accounting.** Compare sign-complete, sign-canonical, and torsion-orbit factor bases with exact witness verification.

## 14. Experiments suggested directly by the literature

### E1. Exact occupancy calibration

For at least three prime-field sizes and several seeds, report:

- $B,m,N$ and the exact multiset count $M=\binom{B+m-1}{m}$;
- realized $|jF|$ for every $1\le j\le m$;
- full multiplicity histograms for $\operatorname{Sym}^j(F)\to G$;
- distinct-input and repeated-input variants;
- sign-complete and sign-canonical variants;
- Poisson goodness-of-fit and total-variation distance from a matched random subset.

This tests the literature's expected-solution heuristic rather than assuming it.

### E2. Energy profile rather than one energy statistic

Measure $E_2(F)$, selected higher energies, doubling constants, and $|jF|$ at each depth. Add an arithmetic-progression control, a random-subset control, and a rational-map-image control. The Green--Ruzsa/BSG comparison predicts that extreme energy should expose a structured subset; the experiment asks whether moderate intermediate compression can coexist with late expansion.

### E3. Source-map family comparison

On the same target curve and at matched $|F|$, compare:

- a random point subset;
- a small-$x$ coordinate base;
- a Petit--Kosters--Messeng composed-map base;
- one deterministic encoding image where the curve family permits it; and
- a union of shallow map images.

Record source-circuit size, map fibres, join multiplicities, exact witness cost, and final support.

### E4. Wagner isolation control

Color the atoms into $m$ independent lists. Run a Wagner-style tree with explicit filters and a flat split MITM at equal success probability. Then repeat with one reused unordered factor base. The difference isolates savings due to standard generalized-birthday filtering from savings due to the proposed source representation.

### E5. Structured-generic diagnostic

For each source representation, define the exact domain on which a proposed tag-level $\star$ operation returns a correct EC sum without a generic addition. Estimate $\delta_j$ at every join depth and plot observed $S,T,\varepsilon$ against the structured-generic expression $\widetilde O(ST^2/N+\delta T)$. This is a model-alignment diagnostic, not a proof.

### E6. Complete fixed-curve accounting

Record preprocessing operations/time $P$, advice bits $S$, online group/field operations $T$, memory traffic, batch target count, and amortized crossover. Compare with ordinary and automorphism-aware rho, generic preprocessing upper bounds, and the PKM algebraic solver at matched target coverage.

## 15. Claims that remain open

- `OPEN`: whether any efficiently recognizable prime-field coordinate set of cryptographically relevant size has provably near-random $m$-fold EC sum occupancy.
- `OPEN`: whether such a set can simultaneously support exact source-level intermediate composition with asymptotically or concretely less work than flat joins.
- `OPEN`: whether coordinate signatures yield useful routing correlation below square-root-scale regimes after false-positive verification.
- `OPEN`: whether a concrete representation can be mapped to a structured-generic partial operation with a favorable $\delta$ without paying equivalent advice or preprocessing.
- `OPEN`: whether any resulting complete attack beats automorphism-aware rho for a general large-prime-field curve, either single-target or under an explicitly charged many-target model.

These are open questions, not impossibility statements.

## Handoff: Calibrate recursive coordinate decomposition against the nearest literature

### Claim or task
Determine whether a coordinate-defined factor base can combine near-random final multiset-sum occupancy with an exact compressed representation of intermediate EC joins after all preprocessing, advice, and witness costs are charged.

### Status
OPEN

### Assumptions
- The target subgroup has prime order $N$ and all experiments use authorized generated or public benchmark instances.
- The atomic factor-base set, sign convention, and repetition policy are fixed before counting.
- Poisson occupancy is a null hypothesis, not an established EC theorem.
- Source tags count as useful compression only when they preserve exact point-level witnesses.
- Fixed-curve preprocessing, advice, memory traffic, relation collection, linear algebra, target descent, and automorphism-aware rho are charged.

### Evidence so far
- Coordinate-defined and composed rational-map factor bases are established in the Semaev/Gaudry/Diem/Petit--Kosters--Messeng line.
- The $m!$ permutation correction is standard; $\binom{B+m-1}{m}$ is its exact finite-$B$, repetition-allowed refinement.
- Additive energy and generalized-birthday filtering supply standard intermediate-compression diagnostics and controls.
- No primary source found jointly proves or optimizes near-random final EC expansion and exact compressed intermediate source composition for general prime-field curves.
- Generic and structured-generic lower bounds constrain only explicitly mapped models and do not close this non-generic frontier.

### Failure modes
- Counting coordinates as points or mishandling sign and repetition orbits.
- Treating domain cardinality as distinct-sum support.
- Rediscovering Wagner filtering, rational-map bases, or deterministic encodings without the stronger joint property.
- Measuring relation membership while omitting rank, target descent, preprocessing, advice, or memory.
- Comparing with plain rho when the curve admits useful automorphisms.
- Presenting a toy occupancy fit as an asymptotic or deployment-relevant break.

### Next concrete action
Run the literature-guided query/experiment: for one random factor base, one Petit--Kosters--Messeng composed-map base, and one deterministic-encoding image at matched $B$ on each of three prime-field sizes, compute the exact maps $\operatorname{Sym}^j(F)\to G$ for $1\le j\le m$, their multiplicity/energy profiles, minimal exact source-tag representation sizes, and flat-MITM versus colored-list Wagner work at equal verified-target success.

### Artifact paths
- `/Volumes/Volume/autolab/research/ecdlp_recursive_expansion_literature_map_20260717.md`
- `/Volumes/Volume/crypto-autoresearcher-worktrees/coordinate-energy/notes/coordinate_decomposition_theories_20260717.md` (read-only source context)
