# Structured generic-group and preprocessing bounds for elliptic-coordinate predicates

**Literature cutoff:** 2026-07-17
**Prepared:** 2026-07-17
**Scope:** fixed-curve preprocessing, structured generic groups, coordinate predicates of the form \(L(x)=0\), recursive elliptic-curve addition circuits, batch point decomposition, and additive expansion/energy of coordinate-defined factor bases.
**Primary-source policy:** only papers, author-hosted papers, proceedings, IACR ePrint, and arXiv are cited.
**Read-only comparison target:** `/Volumes/Volume/crypto-autoresearcher-worktrees/coordinate-energy/experiments/EXP-ECDLP-RECURSIVE-002/contract.md`. That worktree was inspected but not edited.

## Claim-status legend

- **THEOREM:** a result proved in the cited source in its stated standard mathematical or algorithmic model.
- **RESTRICTED THEOREM:** proved, but only in an explicit idealized, representation-randomized, cell-probe, special-parameter, or other restricted model.
- **HEURISTIC:** a complexity estimate or interpretation that depends on distributional, solver, or scaling assumptions.
- **OPEN:** not settled by the sources checked; this includes a missing model translation, not an impossibility claim.

“No theorem located” below means no such theorem was found in the primary sources gathered for this note. It is not a novelty claim and not an impossibility statement.

## Executive result

1. **RESTRICTED THEOREM — the familiar advice bound is real, but narrower than its slogan.** Corrigan-Gibbs and Kogan prove, for a prime-order generic group under a uniformly random injective labeling, a fixed generator, a uniformly random target, an \(S\)-bit group-specific advice string, and at most \(T\) online group-oracle queries, that

   \[
   S T^2 = \widetilde{\Omega}(\epsilon N).
   \]

   Here \(N\) is the group order, \(\epsilon\) is average success probability, and the tilde hides polylogarithmic factors in \(N\). This is not a lower bound for arbitrary algorithms on the standardized affine/projective encoding of one named elliptic curve. [Corrigan-Gibbs–Kogan, Theorem 2](https://eprint.iacr.org/2017/1113.pdf)

2. **RESTRICTED THEOREM — the fixed-generator tradeoff is tight in that model.** Generic random-walk preprocessing attacks achieve success \(\widetilde{\Omega}(S T^2/N)\), and the same paper proves the preprocessing-query tradeoff \(P T+T^2=\Omega(\epsilon N)\). Rotem and Segev give a fully constructive unit-cost-RAM realization of the matching advice tradeoff when \(S-T=\Omega(S)\). Thus the fixed-generator generic frontier is essentially settled, but only for its exact generic model. [Corrigan-Gibbs–Kogan](https://eprint.iacr.org/2017/1113.pdf), [Rotem–Segev, ITC 2022](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ITC.2022.12)

3. **RESTRICTED THEOREM — random generators have a different low-success frontier.** Bartusek, Ma, and Zhandry prove the tight generic success expression

   \[
   \epsilon=\widetilde{\Theta}\!\left(\frac{T^2}{N}+\frac{S^2T^4}{N^2}\right)
   \]

   for random-generator discrete logarithms with preprocessing. When the preprocessing term dominates, this is \(S T^2=\widetilde{\Theta}(\sqrt{\epsilon}\,N)\), not \(\widetilde{\Theta}(\epsilon N)\). The distinction matters for subconstant success; it disappears at exponent level for constant success. [Bartusek–Ma–Zhandry](https://eprint.iacr.org/2019/202.pdf)

4. **RESTRICTED THEOREM — the 2026 structured model exposes a quantified loophole.** Corrigan-Gibbs, Henzinger, and Wu add a free partial operation \(\star\) on labels. If a \(\delta\) fraction of labels are “constrained” by \(\star\), their prime-order preprocessing theorem gives a hard distribution of compatible labelings under which

   \[
   \operatorname{Adv}_{\mathrm{DL}}
   \leq \widetilde{O}\!\left(\frac{S T^2}{q}+\delta T\right).
   \]

   This is tight over the class of all structured label spaces because the authors construct an engineered \(\star_\delta\) attaining the two terms. It is not shown tight for elliptic-coordinate predicates or addition circuits. [The Structured Generic-Group Model, Theorem B.1 and Theorem B.5](https://eprint.iacr.org/2026/384.pdf)

5. **OPEN — \(L(x)=0\) does not instantiate \(\delta\) by itself.** The set

   \[
   \mathcal F_L=\{P\in E(\mathbb F_p):L(x(P))=0\}
   \]

   is a unary membership predicate. The structured model’s \(\star\) is a partial binary operation that must agree exactly with group addition wherever defined. Therefore \(\delta\neq |\mathcal F_L|/q\) without an additional, formally valid construction. A coordinate-specific relation compiler can remain outside both the ordinary generic model and the present structured model.

6. **THEOREM plus OPEN translation — split point decomposition is a preprocessing data-structure problem.** If \(A=4\mathcal F\) is materialized with source witnesses, then a query asking for \(Q=a+b\) with \(a,b\in A\) is a 3SUM-Indexing query in an abelian group. Existing upper bounds and weak cell-probe lower bounds therefore matter. Most timely, Dinur and Golovnev give a 2026 application-specific integer 3SUM-Indexing compiler with \(S=\widetilde O(n^{2.5-\alpha})\), \(T=\widetilde O(n^\alpha)\). Porting its subfunction decomposition, hashing, and witness recovery to \(E(\mathbb F_p)\) is **OPEN**. [Dinur–Golovnev, arXiv v2, 2026-04-23](https://arxiv.org/abs/2512.04258)

7. **OPEN — sparse coordinate-defined expansion is not covered by the available additive-combinatorial theorems.** Energy identities and inverse theorems characterize small doubling after it is observed. Elliptic sum-product papers prove expansion for different coordinate constructions and relatively dense parameter ranges. They do not establish random-like \(|2^j\mathcal F_L|\) growth for \(|\mathcal F_L|\asymp q^{1/8}\), nor do they provide decomposition witnesses or an online relation compiler.

The actionable conclusion is not that coordinate compilers are ruled out. It is that any claimed lower-bound instantiation must first supply a valid representation/operation embedding, while any positive compiler must charge advice bits, preprocessing work, online field/group operations, witness traffic, relation yield, rank, and target descent separately.

## 1. Exact verification of the fixed-curve advice tradeoff

### 1.1 Corrigan-Gibbs–Kogan theorem

**Status: RESTRICTED THEOREM.**

The exact setting of Theorem 2 in [The Discrete-Logarithm Problem with Preprocessing](https://eprint.iacr.org/2017/1113.pdf) is:

- \(N\) is prime.
- A labeling \(\sigma:\mathbb Z_N\rightarrow\mathcal L\) is chosen uniformly from injective maps. Labels have no public coordinate semantics.
- The generic group oracle returns \(\sigma(i+j)\) on labels \(\sigma(i),\sigma(j)\).
- The offline algorithm \(A_0\) receives \(\sigma(1)\), may make an unbounded number of generic-group queries in this theorem, and emits an \(S\)-bit state. It can be taken deterministic because its time is unbounded.
- The online algorithm \(A_1\) receives that state and \(\sigma(x)\), where \(x\) is uniform in \(\mathbb Z_N\), makes at most \(T\) group-oracle queries, and tries to output \(x\).
- The generator \(\sigma(1)\) is fixed. Success \(\epsilon\) is averaged over \(\sigma\), \(x\), and the online coins.
- Time \(T\) counts group-oracle queries, not RAM instructions, field operations, coordinate inversions, memory probes, communication, or parallel depth.
- Advice \(S\) is measured in bits. A table containing \(s\) group elements generally costs \(\Theta(s\log N)\) bits; suppressing this distinction is one source of the tilde factors.

The theorem concludes

\[
S T^2=\widetilde\Omega(\epsilon N).
\]

The proof actually passes through \((S+O(\log N))T^2=\widetilde\Omega(\epsilon N)\); the simplified form assumes the trivial logarithmic floor is absorbed. For composite group order, the analogous statement uses the largest prime factor, as the paper notes.

### 1.2 What “fixed curve” does and does not mean

**Status: RESTRICTED THEOREM.** A standardized curve and generator motivate group-specific advice, but the theorem still averages over a random encoding \(\sigma\). It proves a lower bound against preprocessing algorithms invariant under relabeling of group elements.

**Status: OPEN.** A real curve exposes \((x,y)\), field arithmetic, rational functions, curve equations, addition-law branches, endomorphisms, and serialization. These are precisely the kinds of representation-specific operations erased by random relabeling. The theorem therefore does not establish

\[
S T^2=\widetilde\Omega(\epsilon q)
\]

for all algorithms on a fixed affine or projective representation of \(E(\mathbb F_p)\).

“Beating the bound requires a non-generic algorithm” is correct. “The bound rules out a coordinate-specific algorithm” is not.

### 1.3 Tightness and the role of preprocessing time

**Status: RESTRICTED THEOREM.** Section 7.1 of Corrigan-Gibbs–Kogan describes the matching attack. The offline phase stores endpoints and known logarithms of \(S\) random-walk paths of length about \(T\); the online walk from the target succeeds when it hits one of the stored paths. Up to logarithmic factors, success is \(\Omega(S T^2/N)\).

The attack’s preprocessing work is about \(P\asymp S T\). Theorem 10 separately proves

\[
\epsilon=O\!\left(\frac{P T+T^2}{N}\right),
\qquad
P T+T^2=\Omega(\epsilon N).
\]

That theorem does not restrict advice size. It counts preprocessing and online generic-group queries.

**Status: RESTRICTED THEOREM.** [Rotem–Segev](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ITC.2022.12) remove the truly-random-hash idealization in the upper bound. In a unit-cost RAM model they obtain an explicit algorithm with success \(\widetilde\Omega(S T^2/N)\) when

\[
S-T=\Omega(S),
\]

equivalently \(T\leq(1-\alpha)S\) for a constant \(\alpha>0\). This includes the balanced \(S=T=\Theta(N^{1/3})\) exponent regime with a suitable constant gap and the family \(S=\Theta(N^{1-2\beta})\), \(T=\Theta(N^\beta)\) for \(\beta\geq1/3\). The paper leaves removal of the parameter condition as an explicit technical question.

**Status: RESTRICTED THEOREM.** [Maurer–Portmann–Zhu](https://eprint.iacr.org/2020/996.pdf) reconcile previously mismatched generic models. In their dense-representation preprocessing model, \(\ell\)-bit advice and \(k\) online operations give success at most \(3\ell(k+1)^2/N\); they also show matching generic algorithms up to logarithmic factors, including with a shared random oracle.

**Status: RESTRICTED THEOREM.** [Coretti–Dodis–Guo](https://eprint.iacr.org/2018/226.pdf) formulate auxiliary-input generic-group models and recover the preprocessing bounds through presampling/bit-fixing techniques. This strengthens confidence in the nonuniform generic result; it does not add fixed elliptic coordinates.

### 1.4 Fixed versus random generator

**Status: RESTRICTED THEOREM.** [Bartusek–Ma–Zhandry](https://eprint.iacr.org/2019/202.pdf) show that, for random-generator DLP with preprocessing, the optimal generic success is

\[
\widetilde\Theta\!\left(\frac{T^2}{N}+\frac{S^2T^4}{N^2}\right).
\]

The first term ignores advice and attacks the random-generator instance directly; the second solves two fixed-generator logarithms using the advice. Consequently:

- for constant success, fixed and random generators have the same exponent frontier;
- for subconstant success, the advice contribution scales as \(S T^2\asymp\sqrt\epsilon N\), not \(\epsilon N\);
- quoting only \(S T^2=\widetilde\Omega(\sqrt\epsilon N)\) omits the separate \(T^2/N\) route and is therefore incomplete outside the preprocessing-dominated regime.

For a standardized elliptic-curve generator, the fixed-generator theorem is the relevant generic comparison. For a protocol that randomizes the base, the full random-generator expression is the right comparison.

### 1.5 Batch caveat

**Status: OPEN.** The single-query theorem can be applied separately to independently sampled online targets, but it does not automatically lower-bound a batch algorithm that shares online state, reuses intermediate computations, receives correlated targets, or asks only for decompositions rather than logarithms.

**Status: RESTRICTED THEOREM.** Corrigan-Gibbs–Kogan prove a separate multiple-DLP theorem, and [Yun](https://eprint.iacr.org/2014/637.pdf) proves a tight generic lower bound of order \(\sqrt{MN}\) for solving \(M=o(N)\) independent DLP instances at constant success. These solve all logarithms. They are not the same problem as answering many set-membership/decomposition queries against a fixed factor base.

## 2. The 2026 structured generic-group model

### 2.1 Exact model

**Status: RESTRICTED THEOREM.** [Corrigan-Gibbs–Henzinger–Wu](https://eprint.iacr.org/2026/384.pdf) define a structured label space \((\mathcal L,\star)\), where \(\star:\mathcal L^2\rightharpoonup\mathcal L\) is a free partial binary operation. A compatible injective labeling \(\sigma:\mathbb Z_n\rightarrow\mathcal L\) must satisfy

\[
\ell_1\star\ell_2=O_\sigma(\ell_1,\ell_2)
\]

whenever \(\star\) is defined on image labels. The main formulation requires \((\mathcal L,\star)\) to be a commutative monoid with unique factorization. The paper notes that more permissive variants could be studied, but its theorems use the stated formulation.

An element is “constrained by \(\star\)” if it participates as a nonidentity input to a defined \(\star\) operation or is the output of a nontrivial defined operation. Let \(\delta\) be the fraction of labels constrained this way.

Only generic group-oracle calls cost time. Evaluation of \(\star\), arbitrary computation, and label inspection are free. This makes a lower bound stronger once an embedding is valid.

### 2.2 Online-only theorem

**Status: RESTRICTED THEOREM.** Theorem 3.2 states that, if at least one compatible labeling of order \(n\) exists and \(q\) is the largest prime factor of \(n\), there exists a hard distribution \(\mathcal D\) over compatible labelings such that every \(T\)-query DLP algorithm has advantage at most

\[
\frac{\delta n(3T+2)}q+\frac{(3T+1)^2}q+\frac1n.
\]

For prime order \(n=q\), this is \(O(\delta T+T^2/q)\). Constant success therefore requires

\[
T=\Omega\!\left(\min\{\sqrt q,1/\delta\}\right)
\]

up to constants and low-order terms.

This is an existential hard distribution over compatible encodings. It is not a theorem about every compatible encoding, and in particular not automatically about the conventional coordinate encoding of a named curve.

### 2.3 Preprocessing theorem and exact escape term

**Status: RESTRICTED THEOREM.** Theorem B.1 gives, for prime order \(q\), a hard distribution such that an \(S\)-bit-advice, \(T\)-query online algorithm has

\[
\operatorname{Adv}_{\mathrm{DL}}
\leq\widetilde O\!\left(\frac{S T^2}{q}+\delta T\right).
\]

Thus, if \(\delta T\leq\epsilon/2\), one may rearrange the theorem as

\[
S T^2=\widetilde\Omega(\epsilon q).
\]

If \(\delta T\) is already comparable to \(\epsilon\), the theorem gives no such advice lower bound. This \(\delta T\) term is the formal structured loophole.

**Status: RESTRICTED THEOREM.** Theorem B.5 shows class-wide tightness: for each \(\delta\), the authors construct a partial operation whose exposed labels include a known consecutive chain of powers and achieve advantage \(\widetilde\Omega(S T^2/q+\delta T)\). This proves that no better theorem is possible for all \(\star\) under only the constrained-label statistic.

**Status: OPEN.** It does not prove that a concrete elliptic-coordinate \(\star\) attains the \(\delta T\) term, nor that \(\delta\) alone characterizes its algorithmic power.

### 2.4 What the paper does not yet instantiate

The paper gives detailed structured applications for smooth integers and smooth polynomials. Its Section 5.3 says that many non-generic algorithms—including special-case elliptic-curve DLP algorithms—have not yet been modeled. In the full text checked for this note, there is no theorem instantiating:

- a predicate \(L(x(P))=0\);
- a Semaev summation-polynomial decomposition oracle;
- a recursive affine/projective addition-law circuit;
- an \(m\)-term point-decomposition data structure;
- additive energy or expansion of a coordinate-defined factor base.

**Status: OPEN.** Building one of these embeddings is exactly the missing comparison. The abstract’s broad reference to elliptic-curve points should not be read as a completed lower bound for prime-field coordinate factor bases.

## 3. Why \(L(x)=0\) is not yet a structured-model instantiation

Let \(G=\langle P\rangle\subseteq E(\mathbb F_p)\) have prime order \(q\), and let

\[
\mathcal F_L=\{R\in G:L(x(R))=0\}.
\]

### 3.1 Unary predicate versus partial group law

**Status: OPEN.** Membership in \(\mathcal F_L\) reveals a property of one label. The structured model reveals exact additions for selected pairs of labels. No source checked proves that a size-\(B\) efficiently testable predicate can be represented by a compatible \(\star\) constraining only \(O(B)\) labels.

The tempting substitution

\[
\delta\stackrel{?}=\frac{|\mathcal F_L|}{q}

\]

is therefore unjustified. A valid proof must specify the label space, the partial operation, compatibility with EC addition, associativity, identity, commutativity, unique factorization, and at least one injective compatible labeling.

### 3.2 Full coordinate addition makes the bound vacuous

**Status: RESTRICTED THEOREM, conditional on the proposed embedding.** If ordinary elliptic addition on conventional point labels is placed in \(\star\) everywhere, essentially every label is constrained, so \(\delta\approx1\). The bound \(O(\delta T+T^2/q)\) is then vacuous. This is expected: a fully concrete group representation is the far end of the structured-model interpolation.

The useful question is whether a relation compiler can be represented by a much sparser partial operation than full EC addition.

### 3.3 A canonical witness forest is plausible but lossy

One possible embedding is to expose only canonical recursive decompositions:

\[
\mathcal F\times\mathcal F\longrightarrow2\mathcal F,
\qquad
2\mathcal F\times2\mathcal F\longrightarrow4\mathcal F.
\]

Choose one parent pair for each output and treat the resulting structure as a witness forest.

**Status: OPEN.** This may restore unique factorization, but it discards alternate decompositions. The retained structure could be much weaker than the actual compiler. Conversely, keeping all decompositions creates multiple factorizations of one EC point and directly conflicts with the main model’s unique-factorization requirement.

Adding source tags does not trivially solve the problem: two distinct tagged witnesses for the same EC point cannot both be labels of one injective \(\sigma:\mathbb Z_q\rightarrow\mathcal L\) unless the model is extended to separate semantic group value from syntactic witness.

### 3.4 What \(\delta\) would count in a valid forest

**Status: HEURISTIC exponent sanity check.** Suppose \(|\mathcal F|=B\asymp q^{1/8}\) and the sumsets expand like random subsets until saturation. Then

\[
|2\mathcal F|\asymp q^{1/4},
\qquad
|4\mathcal F|\asymp q^{1/2},
\qquad
|8\mathcal F|\asymp q.
\]

If \(\star\) exposes only the layers through \(4\mathcal F\), the constrained-label union is dominated by \(|4\mathcal F|\), giving \(\delta\asymp q^{-1/2}\). The preprocessing theorem would then read

\[
\operatorname{Adv}_{\mathrm{DL}}
\leq\widetilde O\!\left(\frac{S T^2}{q}+\frac{T}{q^{1/2}}\right).
\]

If the final \(4\mathcal F+4\mathcal F\) layer is exposed for all outputs, nearly all group labels become constrained and \(\delta\asymp1\). This identifies a precise split:

- preprocess the two half-sum supports and leave the final target-dependent join online; or
- expose the final join as free structure and lose the lower bound.

The estimate is not a theorem about coordinate-defined factor bases. It is a target for an explicit embedding/counting experiment.

### 3.5 Endpoint counting misses edge density

**Status: OPEN.** The structured theorem counts constrained labels, not the number of defined \(\star\)-edges, the number of decomposition witnesses, circuit gates, or algebraic degree. Once a set of endpoints is constrained, a dense table of free additions among them may expose much more local structure without increasing \(\delta\) proportionally.

This can work in either direction:

- it may make the theorem conservative for a dense coordinate compiler;
- it may mean that high witness multiplicity is exactly the structure not summarized by \(\delta\);
- if multiplicity destroys unique factorization, the theorem may simply not apply.

The pair \((\delta,\text{edge/witness density})\), not \(\delta\) alone, is therefore the natural empirical audit statistic.

## 4. Recursive addition-law circuits

### 4.1 What addition-law papers prove

**Status: THEOREM.** Elliptic-curve addition is an algebraic morphism that can be represented by systems of polynomial/rational addition laws in projective coordinates. [Kohel](https://arxiv.org/abs/1005.3623) develops the vector-space structure of these laws.

**Status: THEOREM.** Arène, Kohel, and Ritzenthaler prove that a geometrically complete system of addition laws for a \(g\)-dimensional abelian variety in any projective embedding has at least \(g+1\) laws. They also prove that over fields with infinite absolute Galois group one can choose an embedding with a single law complete on rational-point pairs; they give low-dimensional refinements. [Complete addition laws on abelian varieties](https://arxiv.org/abs/1102.2349)

**Status: THEOREM, special representation.** Renes, Costello, and Batina give efficient formulas complete on prime-order short-Weierstrass curves in characteristic other than 2 or 3. [Complete addition formulas for prime order elliptic curves](https://eprint.iacr.org/2015/1060.pdf)

These results establish formula availability, branch coverage, and operation counts. They do not prove lower bounds on recursive circuit size, common-subexpression compression, inversion of the addition map, or batch decomposition.

### 4.2 Relation to recursive decomposition

An eight-term relation can be represented by a balanced tree of seven additions. In coordinates, each node uses a complete addition formula or one branch from a complete system. A target-independent compiler might try to reuse:

- denominator tests and exceptional strata;
- repeated low-degree subexpressions;
- projective normalization data;
- common elimination templates across targets;
- symmetries under input permutation and point negation;
- repeated intermediate points caused by high additive energy.

**Status: HEURISTIC.** Naive substitution through a balanced tree causes degree and expression growth, while retaining intermediate variables keeps local degree low at the cost of more variables and equations. Which representation wins is a solver- and parameter-dependent question.

**Status: OPEN.** No gathered source proves that every coordinate addition circuit with useful decomposition success must expose \(\Omega(q^\alpha)\) constrained labels, use \(\Omega(q^\alpha)\) advice, or take \(\Omega(q^\beta)\) online field operations. Conversely, no source supplies a sub-rho coordinate compiler for ordinary prime-field curves.

### 4.3 Summation-polynomial comparison

**Status: THEOREM.** Semaev’s summation polynomials characterize when points with prescribed \(x\)-coordinates can sum to the identity. [Semaev](https://eprint.iacr.org/2004/031.pdf)

The recursive addition circuit and the summation-polynomial system are two elimination organizations for related geometry:

- direct recursion retains \(x,y\) or projective intermediates and low-degree local addition constraints;
- summation polynomials eliminate \(y\)-coordinates and intermediates, producing fewer variables but rapidly increasing degree;
- chain-variable systems interpolate between these extremes.

**Status: OPEN.** A preprocessing lower bound for one organization does not automatically transfer to the other. A reusable target-independent elimination template is exactly a coordinate-specific loophole absent from the random-label generic model.

## 5. Petit-style rational-map factor bases and neighboring index calculus

### 5.1 Direct prior art for \(L(x)=0\)

**Status: HEURISTIC/parameter-limited algorithm.** Petit, Kosters, and Messeng define prime-field factor bases

\[
\mathcal F=\{(x,y)\in E(\mathbb F_p):L(x)=0\},

\]

where a high-degree rational map \(L\) is composed from low-degree maps. They combine the chain equations for that composition with a Semaev summation polynomial. Their two concrete sources of \(L\) are a smooth-order coset in \(\mathbb F_p^*\) and a smooth subgroup on an auxiliary elliptic curve mapped through an isogeny chain. [Petit–Kosters–Messeng, PKC 2016](https://www.iacr.org/archive/pkc2016/96140156/96140156.pdf)

Their partial cost model is

\[
P(p,m)
+\frac{m!\,p}{(\deg L)^{m-1}}T(E,m,L)
+(\deg L)^\omega,

\]

with expected decomposition multiplicity heuristically about

\[
\frac{(\deg L)^m}{m!\,p}.

\]

At the balanced choice \((\deg L)^m\approx m!p\), beating \(p^{1/2}\) requires the point-decomposition solver to run below approximately

\[
p^{1/2-1/m}.

\]

The paper explicitly reports only small-parameter practicality and leaves the relevant Gröbner complexity unresolved. This is the closest direct algorithmic comparison to a coordinate-specific relation compiler.

### 5.2 Semaev, Gaudry, Diem, Weil descent, and algebraic solvers

- **THEOREM:** Semaev supplies the summation-polynomial relation criterion. [Primary paper](https://eprint.iacr.org/2004/031.pdf)
- **HEURISTIC/parameter-limited:** Gaudry’s index-calculus framework and Diem’s developments obtain improvements for extension-field regimes through subfield factor bases and Weil restriction/descent. They do not give a general prime-field coordinate compiler. [Gaudry](https://doi.org/10.1016/j.jsc.2008.08.005), [Diem](https://doi.org/10.1112/S0010437X10005075)
- **HEURISTIC/parameter-limited:** Joux–Vitse exploit small extension degree and symmetries in a specific extension-field/static-DH regime. [Joux–Vitse](https://eprint.iacr.org/2010/157.pdf)
- **HEURISTIC:** Faugère–Perret–Petit–Renault analyze binary-field systems and obtain attack estimates under algebraic-solver assumptions. Their structure and solver diagnostics are relevant controls, but their field regime is not ordinary prime-field ECDLP. [Author-hosted paper](https://people.maths.ox.ac.uk/petit/files/Eurocrypt2012.pdf)
- **OPEN:** first-fall degree, degree of regularity, last-fall degree, crossbred/hybrid behavior, and target-to-target template reuse remain system-family dependent. Toy Gröbner timings alone do not establish an asymptotic attack.

The coordinate lead should therefore be framed as a test of whether recursive/cached algebra lowers \(T(E,m,L)\), not as a rediscovery of rational-map factor bases.

## 6. Batch point decomposition as 3SUM/kSUM indexing

### 6.1 Exact reduction for a split relation search

Let \(A=4\mathcal F\), with each stored \(a\in A\) carrying at least one four-factor witness. For a target \(Q\), finding an eight-term decomposition via a \(4+4\) split is

\[
\text{find }a,b\in A\text{ such that }a+b=Q.

\]

This is 3SUM-Indexing over the abelian group \(G\), followed by two source-witness lookups. If the two halves use different subsets, use \(A_1,A_2\).

The reduction is exact at the query level, but the attack cost must also include construction of \(A\), storage of source witnesses, collision/multiplicity handling, relation verification, relation-matrix rank, linear algebra, and individual-log descent.

### 6.2 Upper bounds

**Status: THEOREM.** Golovnev, Guo, Horel, Park, and Vaikuntanathan apply Fiat–Naor inversion to 3SUM-Indexing and obtain

\[
S^3T=\widetilde O(n^6)

\]

for an input of length \(n\). Their paper also supplies nonadaptive lower bounds and explicitly connects data structures with cryptographic preprocessing. [STOC 2020 / arXiv](https://arxiv.org/abs/1907.08355)

**Status: THEOREM, integer model.** Dinur and Golovnev improve the upper bound by decomposing the integer pair-sum function into about \(n\) subfunctions and applying improved inversion to each. For every \(0\leq\alpha\leq1\), they prove

\[
S=\widetilde O(n^{2.5-\alpha}),
\qquad
T=\widetilde O(n^\alpha),

\]

with standard-RAM online time matching the query count up to polylogarithmic factors and preprocessing time \(\widetilde O(n^2)\). It improves the prior frontier in the range \(n^{3/2}\ll S\ll n^{7/4}\). The paper also gives the analogous \(k\)SUM-Indexing space \(\widetilde O(n^{k-0.5-\alpha})\). [Dinur–Golovnev](https://arxiv.org/abs/2512.04258)

**Status: OPEN translation.** Their main formulation uses positive integers and modular hashing by random primes. An implementation over EC points needs a group-compatible substitute, explicit coordinate hashing, or a reduction to integer representatives that preserves pair-sum queries. That port is not supplied by the paper.

### 6.3 Lower bounds are much weaker than the conjectured frontier

**Status: RESTRICTED THEOREM.** Chung and Larsen prove, for adaptive cell-probe data structures over cyclic groups of size \(O(n^2)\) and XOR groups of comparable size, with \(S\) words of \(w=\Omega(\log n)\) bits,

\[
T=\Omega\!\left(\frac{\log n}{\log(Sw/n)}\right).

\]

They also prove stronger nonadaptive/small-probe statements. [Chung–Larsen, SODA 2023](https://arxiv.org/abs/2203.09334)

These are logarithmic query lower bounds, not a theorem such as \(ST=\widetilde\Omega(n^2)\) for fully adaptive algorithms. The stronger time-space statements in this literature are conjectures or upper bounds.

**Status: OPEN.** No gathered unconditional lower bound closes the EC split-decomposition data-structure frontier, especially for structured, dependent sets \(A=4\mathcal F_L\), witness output, large group universe \(|G|\gg n^2\), and coordinate computation outside the cell-probe cost.

### 6.4 Why this matters for the current lead

The 2026 3SUM-Indexing result is direct evidence that an application-specific relation compiler can beat a generic function-inversion application in a nontrivial parameter window. It does not break ECDLP, but it warns against using a generic preprocessing lower bound as a proxy for all structured pair-sum compilers.

For \(m=8\) and random-like expansion, \(n=|4\mathcal F|\asymp q^{1/2}\). The Dinur–Golovnev frontier translates heuristically to

\[
S\asymp q^{1.25-\alpha/2},
\qquad
T\asymp q^{\alpha/2},

\]

before witness and construction costs. These spaces exceed \(q\) over much of the useful range and therefore do not immediately beat rho; the value is as a compiler template and baseline, not as a claimed attack.

## 7. Additive energy and coordinate-defined expansion

### 7.1 General abelian-group facts

For \(A\subseteq G\), define additive energy

\[
E(A)=|\{(a_1,a_2,a_3,a_4)\in A^4:a_1+a_2=a_3+a_4\}|.

\]

**Status: THEOREM.** Cauchy–Schwarz gives

\[
E(A)\geq\frac{|A|^4}{|A+A|},
\qquad
|A+A|\geq\frac{|A|^4}{E(A)}.

\]

Thus unusually high energy is equivalent to many pair-sum collisions and forces smaller support.

**Status: THEOREM.** Freiman-type inverse results say that a finite subset of an abelian group with small doubling lies inside a bounded-complexity coset progression, with quantitative dependence on the doubling constant. [Green–Ruzsa](https://arxiv.org/abs/math/0505198)

These are conditional structural theorems: they explain what follows if small doubling is established. They do not prove that \(L(x)=0\) has small or large doubling.

### 7.2 Elliptic sum-product results do not match the needed set operation

**Status: RESTRICTED THEOREM.** Ahmadi and Shparlinski prove that, for an ordinary curve, a point \(P\) of order \(r\), and sufficiently large subsets of \(\mathbb Z_r^*\), at least one of

\[
\{x(aP)+x(bP)\}
\quad\text{and}\quad
\{x(abP)\}

\]

is large, with an explicit quantitative bound. [Ahmadi–Shparlinski](https://arxiv.org/abs/0806.0640)

Related bilinear-character-sum work obtains further coordinate expansion bounds. [Ahmadi–Shparlinski, Proceedings of the Edinburgh Mathematical Society](https://doi.org/10.1017/S0013091508000771)

These operations are not \(\mathcal F_L+\mathcal F_L\) under elliptic addition. The hypotheses are also much denser than \(|\mathcal F_L|\asymp q^{1/8}\) in the intended eight-term regime.

**Status: OPEN.** The gathered literature does not prove, uniformly for useful coordinate maps \(L\), either

\[
|2^j\mathcal F_L|\asymp\min(q,|\mathcal F_L|^{2^j})

\]

or a nontrivial opposite bound at sparse factor-base sizes. It also does not convert expansion into an efficient decomposition algorithm.

### 7.3 Expansion is not monotonically good for the structured lower bound

There is a three-way tradeoff:

- larger sumsets improve target coverage;
- larger intermediate supports increase the constrained-label fraction \(\delta\) in a witness-forest embedding;
- higher energy reduces support but increases witness multiplicity, which may aid a compiler while violating unique factorization.

**Status: OPEN.** A complete model needs both support growth and witness multiplicity. Exact support alone, while valuable, cannot decide whether the resulting structure is lower-bound compatible or algorithmically exploitable.

## 8. Baseline and neighboring-work comparison

| Cluster | Proven/observed content | Relevance to this lead | Missing comparison |
|---|---|---|---|
| Pollard rho and generic lower bounds | **RESTRICTED THEOREM:** generic DLP needs birthday-scale queries without preprocessing; rho supplies the practical baseline. [Shoup](https://doi.org/10.1007/3-540-69053-0_18), [Pollard](https://doi.org/10.1090/S0025-5718-1978-0491431-9) | Any claimed single-target attack must beat automorphism-aware rho in normalized group/field operations. | Coordinate compiler costs, memory bandwidth, parallelism, and precomputation amortization. |
| Fixed-curve generic preprocessing | **RESTRICTED THEOREM:** \(ST^2=\widetilde\Omega(\epsilon N)\), tight up to logs in the fixed-generator random-label model. | Correct null frontier for relabeling-invariant advice. | Named coordinate encoding and non-generic field operations. |
| Structured generic groups | **RESTRICTED THEOREM:** success \(\widetilde O(ST^2/q+\delta T)\) for a hard compatible-label distribution. | Candidate framework for a partial relation compiler. | Valid \(L(x)=0\)/recursive-circuit embedding; multiplicity beyond \(\delta\). |
| Semaev / summation polynomials | **THEOREM:** exact relation criterion. | Algebraic representation of point decomposition. | Solver complexity and reusable target-specialization templates. |
| Gaudry / Diem / Weil descent | **HEURISTIC or parameter-limited:** improvements in extension-field/subfield regimes. | Shows that representation-specific decomposition can beat generic behavior in neighboring families. | Transfer to ordinary prime fields without importing the extension-field structure. |
| Faugère–Perret–Petit–Renault / Joux–Vitse | **HEURISTIC or parameter-limited:** algebraic solvers, symmetry, and small-extension regimes. | Supplies solver metrics and controls. | Prime-field degree/regularity and honest asymptotics. |
| Petit–Kosters–Messeng rational maps | **HEURISTIC, toy/parameter-limited:** direct \(L(x)=0\) prime-field framework. | Closest positive prior art; must not be duplicated without attribution. | Batch symbolic reuse, dedicated solver, and proof/model link to SGGM. |
| 3SUM/kSUM indexing | **THEOREM in stated data-structure models:** structured upper bounds and weak cell-probe lower bounds. | Exact abstraction for the final split join. | EC-compatible subfunction decomposition and source-witness accounting. |
| Additive combinatorics | **THEOREM:** energy/support identities and inverse structure after small doubling. | Explains collision/support tradeoffs. | Sparse coordinate-defined expansion theorem and coordinate-computable certificate. |
| GLV/GLS/Frobenius/negation | **THEOREM/algorithms on special curves:** efficient endomorphisms decompose scalar multiplication and speed rho by orbit/constant factors. [GLV](https://www.iacr.org/archive/crypto2001/21390189.pdf), [Galbraith–Lin–Scott](https://eprint.iacr.org/2008/194.pdf) | Required stronger baseline and possible orbit batching. | Evidence that an orbit changes relation rank/probability asymptotically rather than constants. |

GLV/Frobenius structure should be tested as an accelerator or orbit-amortization control, not confused with an exponent-reducing decomposition theorem for ordinary prime curves.

## 9. Precise loopholes left for coordinate-specific relation compilers

1. **Coordinate semantics survive preprocessing.** Random-label lower bounds deliberately destroy access to \(x\), \(y\), field characters, denominators, and rational-map chains.
2. **A unary predicate is outside the current \(\star\) interface.** Efficient membership or root enumeration may reveal useful structure without exposing many exact free additions.
3. **Witness multiplicity is not summarized by \(\delta\).** Many decomposition edges can share a small endpoint set, while unique factorization excludes the most collision-rich case.
4. **Target-independent symbolic elimination may be advice.** Macaulay matrices, elimination orders, resultants, Gröbner traces, and branch schedules can be compiled once and specialized per target.
5. **Batch decomposition is not single-target DLP.** Shared work across many target points can follow 3SUM/kSUM-indexing frontiers before relation rank and descent are charged.
6. **Correlated targets may invalidate independent-query accounting.** Relation collection generates targets by a controlled walk or linear combination, not necessarily independent uniform queries.
7. **Alternative representations may coalesce circuits.** Projective, Edwards, Montgomery, Kummer-like, isogeny-derived, or tagged-witness representations may change circuit size and exceptional sets even when the abstract group is unchanged.
8. **Endomorphism/Frobenius orbits may improve batching.** Known results mainly give constant/orbit factors; a rank or relation-quality effect remains testable.
9. **Data-structure lower bounds are weak.** Present adaptive 3SUM-Indexing lower bounds are logarithmic in the relevant cell-probe regimes, leaving broad space for structured upper algorithms.
10. **A model extension could change the answer.** A structured model allowing unary predicates, semantic-value/syntactic-witness separation, nonunique factorization, and charged coordinate circuits may produce a tighter theorem—or expose a real loophole.

None of these items implies that a better ECDLP algorithm exists. They identify what has not been ruled out.

## 10. Relationship to `EXP-ECDLP-RECURSIVE-002`

The existing contract studies clean toy prime-order curves at 12, 14, and 16 bits, an eight-term \(4+4\) split, several frozen coordinate-defined factor-base families, exact \(|4A|\) and \(|8A|\), coverage efficiency, witness-map bytes, and order-robust lookup effort against random-scalar and random-\(x\) replicated nulls. It explicitly does not measure relation rank, solver degree, linear algebra, or target descent, and its current status is review-required before a canonical run.

The leads below do not repeat that support/lookup extremeness test. They consume its audited sets or reproduce its frozen generators only as inputs, then test missing model or compiler mechanisms.

| Proposed lead | New object measured | Why it does not duplicate `RECURSIVE-002` |
|---|---|---|
| SGCP-EMBED-001 | valid \(\star\), unique-factorization certificate, \(\delta\), retained witness coverage | Converts support data into a theorem-applicability audit. |
| EC-3SUM-COMPILER-001 | advice/query/preprocessing tradeoff for the final join | Benchmarks a real batch data structure rather than lookup-order robustness. |
| EC-ADDLAW-DAG-001 | rational-circuit DAG reuse, branches, denominators, specialization cost | Tests coordinate computation before support materialization. |
| PKM-BATCH-SPECIALIZE-001 | reusable algebraic template and per-target solver work | Tests the closest prior-art coordinate compiler and its amortization. |
| COORD-ENERGY-CERT-001 | Fourier/inverse-additive certificate and coordinate-computable predictor | Seeks a mechanism for any support anomaly, not another coverage score. |

## 11. Five testable leads

### Lead 1 — SGCP-EMBED-001: certify or refute an SGGM embedding

**Status: OPEN.**

**Hypothesis.** A large fraction of useful recursive witnesses can be represented by a commutative, associative, injectively labeled, unique-factorization partial operation whose constrained-label fraction is close to

\[
\frac{|\mathcal F\cup2\mathcal F\cup4\mathcal F|}{q},

\]

without exposing the final saturated \(8\mathcal F\) layer.

**Minimal test.** On each audited `RECURSIVE-002` instance:

1. enumerate source-tagged \(2\mathcal F\) and \(4\mathcal F\) witness DAGs;
2. choose one canonical parent pair per semantic EC point by a frozen ordering;
3. construct the induced partial \(\star\);
4. mechanically test commutativity, associativity wherever both sides are defined, identity, unique factorization, and compatibility with EC addition;
5. count constrained semantic labels, defined edges, alternative witnesses discarded, and surviving target coverage when the last \(4+4\) join remains online.

**Positive control.** A formal free commutative monoid of source symbols, where unique factorization holds by construction.

**Negative control.** The unpruned EC quotient retaining every witness, expected to exhibit multiple factorizations.

**Primary metrics.** \(\delta\), edges/constrained-label, witness multiplicity, retained \(|8\mathcal F|\) coverage ratio, and the smallest explicit axiom counterexample.

**Positive signal.** A fully checked embedding retaining at least 90% of the original target coverage with \(\delta\leq2|\mathcal F\cup2\mathcal F\cup4\mathcal F|/q\) on all three sizes.

**Falsification/narrowing.** Unique factorization or injectivity fails necessarily, or every valid pruning retains less than 50% of target coverage. Preserve the minimal collision diagram as a scoped negative result and formulate the needed model extension.

**Literature basis.** [Structured GGM, Definitions 2.2–3.1 and Theorems 3.2/B.1](https://eprint.iacr.org/2026/384.pdf).

### Lead 2 — EC-3SUM-COMPILER-001: port the 2026 subfunction compiler to the \(4+4\) join

**Status: OPEN.**

**Hypothesis.** The Dinur–Golovnev subfunction decomposition, or an EC-compatible analogue, lowers online query work for \(Q=a+b\), \(a,b\in4\mathcal F\), below both linear scan and the generic Fiat–Naor frontier in its stated nontrivial space window, without losing source witnesses.

**Minimal test.** Implement four frozen backends on the same materialized \(A=4\mathcal F\):

1. sorted linear/two-list scan;
2. full pair-sum table;
3. Fiat–Naor-style inversion baseline;
4. Dinur–Golovnev-style subfunctions using an explicitly documented point hash or modular projection.

Run first on the paper’s integer model as a positive control, then on a toy cyclic group with visible exponents, then on EC point encodings. Return exact factor-base witnesses, not only membership bits.

**Negative control.** Randomly permute point encodings while preserving only oracle addition; a coordinate-dependent compiler should lose its advantage.

**Primary metrics.** Advice bits, preprocessing RAM operations, online probes, online RAM operations, group/field operations, false candidates, verification work, witness bytes, and success over 128 fixed targets.

**Positive signal.** In the window \(n^{3/2}<S<n^{7/4}\), the EC backend beats both \(\widetilde O(n)\) query work and the measured Fiat–Naor backend, with fitted \(TS\) exponent at most 2.6 over at least three larger toy sizes and 100% witness verification.

**Falsification/narrowing.** The integer control reproduces the expected trend but every EC-compatible hash loses subfunction locality, or witness traffic/verification erases the online gain.

**Literature basis.** [Dinur–Golovnev](https://arxiv.org/abs/2512.04258), [Golovnev et al.](https://arxiv.org/abs/1907.08355), [Chung–Larsen](https://arxiv.org/abs/2203.09334).

### Lead 3 — EC-ADDLAW-DAG-001: measure reusable recursive addition-law structure

**Status: OPEN.**

**Hypothesis.** A complete addition-law representation yields substantial target-independent DAG reuse or a small family of denominator/branch strata when recursively composing four- and eight-term sums, beyond what a random low-degree map with the same local gate counts exhibits.

**Minimal test.** For short-Weierstrass complete formulas and one alternative coordinate model:

1. build balanced 2-, 4-, and 8-input symbolic addition DAGs with intermediate variables retained;
2. hash-cons common subexpressions and canonicalize input permutations/negations;
3. separately compose/eliminate to target-coordinate equations;
4. enumerate exceptional denominator strata and branch schedules on toy fields;
5. compare with random quadratic rational maps matched for variables, local degree, and gate count.

**Positive control.** Repeated doubling trees, which should display obvious subexpression reuse.

**Negative control.** Independently sampled random rational maps at each node.

**Primary metrics.** Unique DAG nodes, multiplication/inversion gates, numerator/denominator degrees, branch count, exceptional-set density, specialization operations, and semantic-output collision multiplicity.

**Positive signal.** At least a fourfold reduction in unique arithmetic nodes or specialization work versus independently evaluating all witnesses, replicated across three field sizes and absent from the matched random-map null.

**Falsification/narrowing.** Degree/branch growth tracks the random-map null and hash-consing saves only constants already explained by ordinary formula reuse.

**Literature basis.** [Kohel](https://arxiv.org/abs/1005.3623), [Arène–Kohel–Ritzenthaler](https://arxiv.org/abs/1102.2349), [Renes–Costello–Batina](https://eprint.iacr.org/2015/1060.pdf), [Semaev](https://eprint.iacr.org/2004/031.pdf).

### Lead 4 — PKM-BATCH-SPECIALIZE-001: target-independent algebraic advice for \(L(x)=0\)

**Status: OPEN.**

**Hypothesis.** For a Petit–Kosters–Messeng composed rational map, most elimination work can be compiled into a target-independent symbolic template whose per-target specialization is materially cheaper than a cold Gröbner/resultant solve and whose advice cost is honestly chargeable.

**Minimal test.** For \(m=4,6,8\) where feasible and at least three toy field sizes:

1. construct the Semaev-plus-\(L\)-chain system once with symbolic target \(X\);
2. cache monomial orders, Macaulay sparsity, elimination matrices, pivot schedules, Gröbner traces, or resultants that do not depend on \(X\);
3. specialize the same artifact to 128 frozen targets;
4. compare against cold solves, generic systems of the same multidegree, and the existing materialized-support lookup;
5. verify every returned decomposition on the curve.

**Positive control.** A univariate or extension-field chain family with known stable specialization behavior.

**Negative control.** Random systems with the same equation count and multidegrees.

**Primary metrics.** Advice bits, precomputation field operations, per-target field operations, memory reads, degree of regularity/last-fall diagnostics, specialization failures, solution count, and verified relation probability.

**Positive signal.** A replicated per-target exponent reduction of at least 0.05 versus cold solving, with advice and preprocessing charged, plus online cost trending below the PKM gate \(p^{1/2-1/m}\). A constant-factor gain alone remains a useful engineering result but is not an ECDLP promotion.

**Falsification/narrowing.** Pivot/leading-term structure changes with almost every target, cached artifacts approach the full solve size, or advice amortization requires more targets than the relation phase can use.

**Literature basis.** [Petit–Kosters–Messeng](https://www.iacr.org/archive/pkc2016/96140156/96140156.pdf), [Semaev](https://eprint.iacr.org/2004/031.pdf), [Faugère–Perret–Petit–Renault](https://people.maths.ox.ac.uk/petit/files/Eurocrypt2012.pdf).

### Lead 5 — COORD-ENERGY-CERT-001: explain any coordinate-set anomaly

**Status: OPEN.**

**Hypothesis.** If a frozen coordinate factor base is extreme relative to both random-scalar and random-\(x\) nulls, the anomaly is accompanied by a compact additive certificate—Fourier concentration, low Freiman dimension, a small family of popular differences, or a coordinate-computable partition—that predicts high-multiplicity half sums.

**Minimal test.** Reuse audited factor-base sets but add:

1. exact energy and representation-count histograms at \(2\mathcal F\) and \(4\mathcal F\);
2. the nontrivial Fourier spectrum in the toy scalar group, used only as diagnostic ground truth;
3. popular-difference graphs and approximate Freiman-dimension/GAP fits;
4. a held-out predictor built only from coordinates, \(L\)-chain values, characters, or denominator strata;
5. out-of-sample tests across curves and sizes.

**Positive control.** Arithmetic progressions or low-rank generalized progressions in the scalar group.

**Negative controls.** The existing random-scalar and random-\(x\) replicated nulls.

**Primary metrics.** Normalized energy, maximum nontrivial Fourier coefficient, spectral \(\ell_4\) mass, popular-difference concentration, compression length of the structural certificate, and held-out precision/recall for high-multiplicity sums.

**Positive signal.** The coordinate family exceeds the 99th percentile of both nulls at all sizes and a coordinate-only predictor retains at least 80% of the multiplicity enrichment on held-out curves.

**Falsification/narrowing.** Scalar-space structure is visible only after using discrete logs, or no coordinate-only predictor transfers. Such a result would show that the anomaly is diagnostic rather than an attack primitive.

**Literature basis.** [Green–Ruzsa](https://arxiv.org/abs/math/0505198), [Ahmadi–Shparlinski](https://arxiv.org/abs/0806.0640).

## 12. Recommended order

1. Run **SGCP-EMBED-001** first. It determines whether invoking the current structured lower bound is formally legitimate.
2. In parallel, prototype the integer positive control for **EC-3SUM-COMPILER-001**; do not begin with EC hashing before reproducing the paper’s regime.
3. Run **COORD-ENERGY-CERT-001** only after `RECURSIVE-002` passes its audit, because it consumes the same frozen sets but asks a different mechanistic question.
4. Use **EC-ADDLAW-DAG-001** to choose the coordinate/system representation for **PKM-BATCH-SPECIALIZE-001**.
5. Promote no result until relation yield, matrix rank, linear algebra, target descent, and automorphism-aware rho are charged.

## 13. Source verification and caveats

### Full theorem/model text checked from primary sources

- Henry Corrigan-Gibbs and Dmitry Kogan, *The Discrete-Logarithm Problem with Preprocessing*, EUROCRYPT 2018, revised 2021: [ePrint page](https://eprint.iacr.org/2017/1113), [PDF](https://eprint.iacr.org/2017/1113.pdf).
- James Bartusek, Fermi Ma, and Mark Zhandry, *The Distinction Between Fixed and Random Generators in Group-Based Assumptions*, CRYPTO 2019: [ePrint page](https://eprint.iacr.org/2019/202), [PDF](https://eprint.iacr.org/2019/202.pdf).
- Lior Rotem and Gil Segev, *A Fully-Constructive Discrete-Logarithm Preprocessing Algorithm with an Optimal Time-Space Tradeoff*, ITC 2022: [proceedings page and PDF](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ITC.2022.12).
- Ueli Maurer, Christopher Portmann, and Jiamin Zhu, *Unifying Generic Group Models*: [ePrint](https://eprint.iacr.org/2020/996), [PDF](https://eprint.iacr.org/2020/996.pdf).
- Sandro Coretti, Yevgeniy Dodis, and Siyao Guo, *Non-Uniform Bounds in the Random-Permutation, Ideal-Cipher, and Generic-Group Models*: [ePrint](https://eprint.iacr.org/2018/226), [PDF](https://eprint.iacr.org/2018/226.pdf).
- Henry Corrigan-Gibbs, Alexandra Henzinger, and David J. Wu, *The Structured Generic-Group Model*, EUROCRYPT 2026: [author page](https://people.eecs.berkeley.edu/~henrycg/pubs/structured-generic-groups/), [ePrint](https://eprint.iacr.org/2026/384), [PDF](https://eprint.iacr.org/2026/384.pdf).
- Christophe Petit, Michiel Kosters, and Ange Messeng, *Algebraic Approaches for the Elliptic Curve Discrete Logarithm Problem over Prime Fields*, PKC 2016: [IACR proceedings PDF](https://www.iacr.org/archive/pkc2016/96140156/96140156.pdf).
- Alexander Golovnev, Siyao Guo, Thibaut Horel, Sunoo Park, and Vinod Vaikuntanathan, *Data Structures Meet Cryptography: 3SUM with Preprocessing*: [arXiv](https://arxiv.org/abs/1907.08355).
- Eldon Chung and Kasper Green Larsen, *Stronger 3SUM-Indexing Lower Bounds*: [arXiv](https://arxiv.org/abs/2203.09334).
- Itai Dinur and Alexander Golovnev, *Improved Time-Space Tradeoffs for 3SUM-Indexing*, v2 dated 2026-04-23: [arXiv](https://arxiv.org/abs/2512.04258).
- Omran Ahmadi and Igor Shparlinski, *On the Sum-Product Problem on Elliptic Curves*: [arXiv](https://arxiv.org/abs/0806.0640).

### Primary source reached, but exact theorem text not fully rechecked before the requested cutoff

- Wieb Bosma and Hendrik Lenstra Jr., *Complete Systems of Two Addition Laws for Elliptic Curves*: [author-hosted PDF](https://www.math.ru.nl/~bosma/pubs/JNT1995.pdf). The citation was reached, but its exact minimality/bidegree theorem text was not re-extracted during this pass; this note does not rely on that exact detail.
- Pierrick Gaudry, *Index calculus for abelian varieties of small dimension and the elliptic curve discrete logarithm problem*: [journal DOI](https://doi.org/10.1016/j.jsc.2008.08.005). Only the high-level extension-field comparison is used here.
- Claus Diem, relevant extension-field index-calculus work: [journal DOI](https://doi.org/10.1112/S0010437X10005075). Only the high-level parameter-regime comparison is used here.
- Igor Shparlinski, *On the elliptic curve analogue of the sum-product problem*: [journal DOI](https://doi.org/10.1016/j.ffa.2007.12.002). Its exact quantitative inequality is deliberately not restated.

No conclusion in this note depends on an unverified exact constant or exponent from these four entries.

## 14. Bottom line

**Strongest valid statement.** Current preprocessing lower bounds rule out a better fixed-generator *generic* advice/time tradeoff under random encodings, and the 2026 structured model extends this to partial free operations with an explicit \(\delta T\) loophole. They do not yet rule out coordinate-specific relation compilers for \(L(x)=0\), recursive addition-law circuits, or batch decomposition on the conventional encoding of a prime-field elliptic curve.

**What has actually been ruled out.** Any candidate that is relabeling-invariant, or that admits a valid low-\(\delta\) structured-label embedding satisfying the paper’s axioms and hard-distribution interpretation, must respect the corresponding advice/query frontier.

**What has not been ruled out.** Unary coordinate predicates, nonunique witness DAGs, dense free edge sets on small supports, target-independent algebraic specialization, EC-specific 3SUM indexing, and sparse coordinate expansion outside present exponential-sum ranges.

**Next positive move.** Build the SGGM embedding certificate and the EC 3SUM compiler baseline before interpreting support expansion as either a lower bound or an attack signal.

**Next negative/proof move.** Prove that any useful coordinate relation compiler induces either (a) many constrained semantic labels, (b) a large advice string, or (c) a violation of injectivity/unique factorization in the current structured model. If (c) is unavoidable, formulate the smallest model extension and seek a new lower bound there.

## Handoff: coordinate-predicate lower-bound instantiation

### Claim or task

Determine whether a concrete \(L(x)=0\) recursive relation compiler can be embedded in the 2026 structured generic-group model with a nonvacuous constrained-label fraction, while separately benchmarking its final split join as a 3SUM-Indexing data structure.

### Status

OPEN

### Assumptions

- Prime-order subgroup \(G\subseteq E(\mathbb F_p)\).
- Frozen factor-base families and clean-curve controls from `EXP-ECDLP-RECURSIVE-002` after its audit gate.
- Advice, preprocessing work, online group/field work, memory, and witness bytes are charged separately.
- Toy results remain toy evidence; rho comparison includes available automorphism/endomorphism speedups.

### Evidence so far

- The fixed-generator generic advice bound is \(ST^2=\widetilde\Omega(\epsilon q)\) and is tight in its random-label model.
- The structured preprocessing bound is \(\widetilde O(ST^2/q+\delta T)\), but \(L(x)=0\) is not itself a valid \(\star\)-instantiation.
- Recursive witness multiplicity conflicts with the current model’s injectivity/unique-factorization requirements.
- The final \(4+4\) join is a 3SUM-Indexing query; 2026 work gives a new structure-specific upper bound in the integer model.
- Existing elliptic sum-product theorems do not settle sparse group-sum expansion for coordinate factor bases.

### Failure modes

- Treating factor-base density as \(\delta\) without constructing \(\star\).
- Counting support but not decomposition multiplicity or source-witness traffic.
- Importing an integer 3SUM compiler without a group-compatible hashing proof.
- Reporting cached Gröbner speedups without charging advice and precomputation.
- Treating a toy coverage or lookup win as an ECDLP exponent improvement.
- Omitting relation rank, linear algebra, target descent, or automorphism-aware rho.

### Next concrete action

Write and run the `SGCP-EMBED-001` experiment contract against the audited frozen outputs of `EXP-ECDLP-RECURSIVE-002`, producing either a machine-checkable \(\star\)/\(\delta\) certificate or the smallest injectivity/unique-factorization counterexample.

### Artifact paths

- `/Volumes/Volume/autolab/research/prototypes/structured_group_coordinate_predicates_literature_20260717.md`
- `/Volumes/Volume/crypto-autoresearcher-worktrees/coordinate-energy/experiments/EXP-ECDLP-RECURSIVE-002/contract.md` (read-only comparison target)
