# SGCP-EMBED-001 experiment/proof contract, version 3a

Date: 2026-07-17

Status: OPEN / HYPOTHESIS / IMPLEMENTATION-PREFLIGHT / VERSION-3A

Evidence state: no SGCP experiment, canonical ECDLP run, relation collection, or performance run has been executed under this contract.

Version history: version 1 was rejected before execution by
`pre-run-red-team-v1.md`. Version 2 fixed the degree-two decision set, expanded
P2 to the complete balanced formal-multiset universe, and separated public from
private audit data, but `pre-run-theory-review-v2.md` found four remaining
ambiguities. Version 3 froze graph semantics, support/comparator definitions,
policy branches, and the control registry and received GO in
`pre-run-theory-review-v3.md`. Version 3a adds the reviewed monotonic exact-audit
compression in `pre-run-theory-review-v3a.md`.

Scope restriction: implementation belongs on branch `codex/sgcp-embed-001` in
`/Volumes/Volume/crypto-autoresearcher-worktrees/sgcp-embed-001`. The frozen
EXP-ECDLP-RECURSIVE-002 review worktree at commit `f4c8109` must not be edited,
used as an execution directory, or imported as a mutable dependency.

## Literature and model binding

Literature basis:

- `notes/structured_group_coordinate_predicates_literature_20260717.md`
- SHA-256: `169604e8e0c2bf13cfc2d14067868af2e8c41b8346395e160b2d9103f1e31a60`

Exact model definitions were checked against Corrigan-Gibbs, Henzinger, and Wu, The Structured Generic-Group Model, Definitions 2.2, 2.3, and 3.1 and Theorems 3.2 and B.1:

- https://www.cs.utexas.edu/~dwu4/papers/SGGM.pdf
- checked PDF SHA-256: 82b40c277230d0603e5b87a3f6f5d045a7b3b8672f15f7e8ae983878296af66f

An implementation must bind both hashes. It must not invoke the theorem if the pinned definitions differ.

Control registry:

- `experiments/EXP-SGCP-EMBED-001/control-registry-v2.json`
- SHA-256: `cf07a4dedcc7d7895df7959aa809bee9fc8aefeff04a1ef643e7bf211173e5ca`

The builder and independent verifier must bind this exact registry and compare
every predicate, count, objective row, and counterexample. A renamed control or
first-error-only check is not equivalent.

## Claim boundary

SGCP-EMBED-001 asks whether a canonical recursive elliptic-curve factor-base witness structure, initially organized as

\[
F\longrightarrow 2F\longrightarrow 4F,
\]

can be completed into a finite commutative partial monoid with unique factorization and an injective EC-compatible labeling, while leaving the target-dependent \(4F+4F\) join outside the free operation.

A positive result is a toy, model-bound embedding certificate. It supplies one compatible labeling and permits computing the structured-model constrained-label statistic. The cited lower bound still concerns an existential hard distribution over compatible labelings; it is not automatically a lower bound for the conventional coordinates of a named curve.

A failure is a scoped negative for the stated semantic-label and witness-closure class. It is not an ECDLP impossibility, an index-calculus impossibility, or a statement that no coordinate compiler can exist.

# Experiment Contract: SGCP-EMBED-001

## Hypothesis

For every mandatory generated prime-order toy instance, there is a deterministic
or exactly pruned family of balanced four-factor formal multisets whose generated
formal order ideal:

1. is a Corrigan-Gibbs-Henzinger-Wu structured label space;
2. admits an injective EC-compatible labeling of order \(q\);
3. uses one semantic label per EC point and one canonical source per factor-base point;
4. exposes no direct retained-\(4F\) by retained-\(4F\) star edge;
5. has exact constrained-label fraction \(\delta=|C_\star|/q\);
6. retains at least 90 percent of raw final split-support coverage on each of the 10-, 11-, and 12-bit toy instances;
7. reports absolute retained coverage
   `|A4_ret + A4_ret| / q` separately, without treating high relative retention
   as an ECDLP-relevant success.

Coverage is target support for the still-charged final join. It is not relation rank or DLP success.

## Null hypothesis

Under the fixed semantic-label, balanced-four-witness, downward-closed completion class, at least one of the following holds:

- balanced-only edges violate exact associativity;
- associative closure maps distinct formal prime multisets to one EC label;
- a nonempty selected multiset sums to the identity;
- source-tag multiplicity cannot be represented by one injective labeling;
- every valid pruning retains less than 50 percent of raw final split-support coverage;
- every family meeting the retention gate also forces a direct retained-\(4F\) by retained-\(4F\) star edge.

Coverage between 50 and 90 percent is OPEN / INCONCLUSIVE.

## Parameters

- Curves: ordinary short-Weierstrass \(E/\mathbb F_p\), \(p>3\).
- Order: \(\#E(\mathbb F_p)=q\) prime, cofactor one.
- Exclusions: singular, trace 0, trace 1, \(j=0\), and \(j=1728\).
- Generator: lexicographically first affine point; every nonidentity point generates a prime-order group.
- Label-space size: exactly \(q\).
- Factor-base sizes: \(B\in\{4,6,8\}\), with \(B<q\).
- Predicate: \(L_B(X)\) has as roots the \(B/2\) least affine x-coordinates occurring on the curve; both signs are included, so \(|F_B|=B\).
- Relation prefix: balanced four-factor witnesses plus every regrouping forced by associativity.
- Final relation: excluded from star and deferred to a charged \(4+4\) join.
- Builder visibility: coordinates, curve arithmetic, \(L_B\), source tags, and selected witnesses. No discrete-log/scalar table.
- Verifier visibility: exhaustive scalar table as independent toy ground truth.
- Random-control seed:

\[
\operatorname{SHA256}(\text{SGCP-EMBED-001|control|qbits|B|rep}).
\]

Use repetitions 0 through 15 at 5–9 bits and 0 through 7 at 10–12 bits in the
later full-sweep random controls. The implementation preflight is deterministic,
uses only the registered five-bit fixture, and has no random-control replicate.

## Metrics

Record for every curve, \(B\), and policy:

- \(p,q,a_E,b_E,G\), trace, \(j\), and exact group-order certificate;
- \(|F|\), raw \(|2F|\), raw \(|4F|\), and raw \(|4F+4F|\);
- degree-two and degree-four witness counts and multiplicity histograms;
- retained formal multisets by degree 1, 2, 3, and 4;
- semantic collisions, classified by degree pair;
- nonidentity unordered star edges and ordered API-domain entries;
- exact constrained-label set, count, and \(\delta\);
- edges per constrained label;
- normalized edge density;
- raw witnesses per constrained label;
- selected balanced formal witnesses, parent-pair multiplicity, and candidates discarded by injectivity pruning;
- star-table description bits and source-witness bytes;
- source-tag multiplicity and tags discarded by semantic quotienting;
- final split-support ratio

\[
R_{\rm support}=
\frac{|A_4^{\rm ret}+A_4^{\rm ret}|}
{|A_4^{\rm raw}+A_4^{\rm raw}|};
\]

- raw and retained absolute group-coverage ratios

\[
\frac{|A_4^{\rm raw}+A_4^{\rm raw}|}{q},\qquad
\frac{|A_4^{\rm ret}+A_4^{\rm ret}|}{q};
\]

- target-wise final-witness histogram, stored only in the private audit artifact;
- identity, commutativity, associativity, compatibility, unique-factorization, acyclicity, source-faithfulness, and final-boundary results;
- minimized counterexample digest;
- builder/verifier operations, memory, and wall time as implementation diagnostics only.

Final-support witness histograms count unordered input pairs with replacement;
support sets are unchanged by this convention.

## Positive controls

1. PC-FREE-MONOID: a downward-closed free commutative monoid through degree four. It must pass identity, commutativity, associativity, and unique prime-multiset factorization.
2. PC-CYCLIC-NO-WRAP: a prime cyclic group whose retained degree-at-most-four source sums are distinct before reduction. It must pass all embedding checks.
3. PC-EC-FOREST: use the fixed registered `B=8` alternate `(1,6,6,6)` and require its injective EC closure to match the registry exactly.
4. PC-REPEATED-PRIME: the one-prime order ideal through exponents zero to four. It must have one prime multiset per label and the registered parent-pair counts.

A failed positive control invalidates the run.

## Negative controls

1. NC-BALANCED-ONLY: retain only \(1+1\to2\) and \(2+2\to4\) for a genuine four-leaf witness. Exact associativity must fail.
2. NC-ALL-WITNESSES: retain every degree-at-most-four EC formal multiset. The semantic injectivity gate must fail before star construction once a collision exists.
3. NC-DUPLICATE-TAG: demand two source-tag labels for one EC point. The one-label-per-element gate must reject it.
4. NC-COMPAT-MUTATION: keep an abstract monoid table fixed and mutate only one EC decoding. Compatibility must fail while the abstract model axioms still pass.
5. NC-FINAL-EDGE: use a synthetic one-prime degree-eight order ideal. All model axioms must pass, the direct \(A_4\times A_4\) boundary gate must fail, and delta must be recomputed.
6. NC-B6-D2-COLLISION: reconstruct the fixed `(0,3)+(3,17)=(4,10)` formal-product-versus-singleton collision.
7. NC-B8-CANONICAL-LOSS: canonical `(0,0,0,4)` for output `(6,3)` must fail injectivity while alternate `(1,6,6,6)` for the same output passes.
8. NC-OPTIMIZER-FIXTURE: a tiny frozen conflict graph must reproduce its unique lexicographic optimum under exhaustive enumeration.

Controls are isolated and report every predicate, not only the first failure.

Frozen control expectations:

- `PC-FREE-MONOID` uses three formal primes through total degree four: 35
  labels, 75 unordered nonidentity edges, and all 35 labels constrained.
- `PC-CYCLIC-NO-WRAP` uses `q=509` and weights `(1,5,25,125)` through total
  degree four: maximum unreduced sum 500, 70 represented and constrained
  labels, 185 unordered nonidentity edges, and delta `70/509`.
- `PC-REPEATED-PRIME` uses one prime through exponent four: five labels, four
  unordered nonidentity edges, immediate parent-pair counts `0,0,1,1,2` by
  degree zero through four, and one prime multiset for every label.
- `NC-BALANCED-ONLY` uses exactly `a*b=u`, `c*d=v`, and `u*v=w`; triple
  `(a,b,v)` has a defined left chain and no right chain.
- `NC-B6-D2-COLLISION` uses factor indices `(0,3)` and singleton index `5` on
  the registered `B=6` factor base; both evaluate to `(4,10)`.
- `NC-B8-CANONICAL-LOSS` uses the exact multisets and output registered above;
  both must occur in `U4_BAL`.
- `NC-OPTIMIZER-FIXTURE` uses four ordered candidates with synthetic outputs
  `(1,2,4,8)` in `Z_17` and conflicts `(0,1)` and `(2,3)`. Four maximum-size
  feasible pairs tie on three final sums, so the unique full-objective optimum
  after the lexicographic rule is candidate list `(0,2)`.
- `NC-FINAL-EDGE` uses the one-prime formal order ideal through degree eight.
  All nine labels are constrained, all model axioms pass, and the `4+4=8`
  edge alone triggers the direct final-edge predicate.

A missed negative control invalidates the run.

## Success criterion

Report a positive TOY-EVIDENCE / MODEL-EMBEDDING result only if:

1. every control behaves as preregistered;
2. every mandatory curve and \(B\) row has an independent certificate;
3. one fixed coordinate-only policy passes every model axiom on every mandatory row;
4. no direct retained-degree-four by retained-degree-four edge occurs in star;
5. \(R_{\rm support}\ge0.90\) on the 10-, 11-, and 12-bit rows for every \(B\);
6. absolute raw and retained group coverage, delta, edge density, source loss, public-table size, and private-audit size are reported exactly;
7. the existential-hard-distribution limitation is explicit.

This does not establish a faster-than-rho ECDLP algorithm, rank, target descent, or deployment relevance.

## Falsification criterion

- Fixed-policy negative: the deterministic P1 canonical policy or frozen P2 balanced-universe policy fails an axiom or retention gate. This rules out only that policy and candidate universe.
- Embedding-class negative: exhaustive search or independently certified branch-and-bound proves that every admissible pruning on the smallest failing instance has \(R_{\rm support}<0.50\), or every nonempty four-witness closure violates semantic injectivity.

Any negative report must preserve the minimized counterexample and a model-escape route.

## 1. Exact mathematical objects

### Prime-order EC group

Let

\[
E:y^2=x^3+a_Ex+b_E
\]

over \(\mathbb F_p\), with \(G=E(\mathbb F_p)=\langle G_0\rangle\) and \(|G|=q\) prime. Write the identity as \(O\). Use canonical injective serialization \(\operatorname{enc}(O)\) and \(\operatorname{enc}(x,y)\), sorting affine labels by integer pair \((x,y)\).

The verifier enumerates every \([k]G_0\), \(k\in\mathbb Z_q\), and checks that every point occurs once. The builder receives the point table with scalar indices removed.

### Coordinate factor base

Let \(x_1<\cdots<x_{B/2}\) be the least point-bearing x-coordinates. Define

\[
L_B(X)=\prod_{i=1}^{B/2}(X-x_i),\qquad
F=\{P\ne O:L_B(x(P))=0\}.
\]

Since \(q\) is odd and prime, there is no nonidentity rational 2-torsion; every selected x-coordinate contributes \(P\) and \(-P\), and \(|F|=B\).

Each point has one out-of-band source record

~~~text
(root_index, x, sign_bit, y)
~~~

where sign_bit is determined by the smaller of \(y\) and \(p-y\). Multiple records for one point are quotiented to the lexicographically first.

### Formal prime multisets

Treat factor-base labels as formal primes. For a multiset \(M\) of factor-base points, allowing repetition, define

\[
\operatorname{ev}(M)=\sum_{P\in M}P.
\]

The paper uses set language for unique primes but permits repeated primes through exponent vectors. The verifier therefore checks unique prime multisets and separately reports binary-tree multiplicity. Multiple bracketings of one prime multiset are not automatically a failure.

### Raw balanced forest

Enumerate all unordered degree-two multisets. For each nonidentity semantic output, retain the lexicographically least multiset and record alternatives. Pair canonical degree-two nodes, flatten each pair to a degree-four prime multiset, and retain the least witness per nonidentity output.

This BAL object is a witness forest, not yet a structured label space.

Version-2 P2 does not discard noncanonical degree-four formal multisets after
that audit canonicalization. Its frozen candidate universe is

\[
U_4^{\rm BAL}=\{\operatorname{sort}(A\uplus B):
 A,B\text{ are canonical nonidentity degree-two nodes}\}.
\]

Deduplicate this universe by the flattened formal multiset, retain every
balanced parent pair as private audit multiplicity, and independently evaluate
each formal multiset. Distinct candidates with one semantic EC output are
mutually infeasible because injectivity forbids selecting both. This universe
includes alternate formal witnesses for a semantic output; it is not one
canonical representative per output and is not the universe of every possible
unbalanced four-term expression.

## 2. Associativity obstruction

### Restricted theorem: balanced-only failure

Suppose

\[
a\star b=u,\quad c\star d=v,\quad u\star v=w
\]

are defined for nonidentity labels. Definition 2.2 associativity applied to \(a,b,v\) requires

\[
(a\star b)\star v=a\star(b\star v).
\]

Therefore \(b\star v\) and then \(a\star(b\star v)\) must be defined. A domain containing only \(1+1\to2\) and \(2+2\to4\), with no \(1+2\to3\), cannot contain a genuine recursive four-prime product.

This rules out only the literal balanced-only operation. It does not rule out associative closure, hiding the two-sum factorization, a weakened model, or a witness-aware model.

## 3. Generated formal order ideal

For P2, let `D4` contain selected degree-four prime multisets and define the
degree-two decision set, without ambiguity, by

\[
D_2(D_4)=\{A: |A|=2,\ A\text{ is a submultiset of some }M\in D_4\}.
\]

There are no independently retained canonical degree-two maxima in P2. Let
\(\mathcal M_{\max}=D_4\); `D2(D4)` is present only because it is forced by
downward closure. Define

\[
\mathcal M=
\{\varnothing\}\cup\{\{P\}:P\in F\}
\cup\{A:A\text{ is a submultiset of some }M\in\mathcal M_{\max}\}.
\]

This generated formal order ideal includes every degree-three and degree-two
regrouping forced by a retained four-witness. It is not claimed to be minimum
over all possible structured label spaces.

The candidate is admissible only if

\[
\operatorname{ev}:\mathcal M\to G
\]

is injective. This rejects:

- a nonempty multiset summing to \(O\);
- a composite summing to a factor-base prime;
- two distinct selected prime multisets with one EC sum;
- collisions introduced only by degree-three closure.

Canonical choice at degree two and four is not enough; injectivity is checked after full closure.

## 4. Label space, sigma, identity, and star

Use exactly one semantic label per group element:

\[
\mathcal L=\{\ell_P:P\in G\},\qquad |\mathcal L|=q.
\]

Define

\[
\sigma:\mathbb Z_q\to\mathcal L,\qquad
\sigma(k)=\ell_{[k]G_0}.
\]

This is bijective and therefore injective. Its identity is

\[
\mathbf 1_\star=\ell_O=\sigma(0).
\]

If ev is injective on \(\mathcal M\), let \(\mu\) be its inverse on \(\operatorname{ev}(\mathcal M)\). Define:

1. \(\ell_O\star\ell_P=\ell_P\star\ell_O=\ell_P\) for every \(P\).
2. For nonidentity labels represented by \(A,B\in\mathcal M\),

\[
\ell_{\operatorname{ev}(A)}\star\ell_{\operatorname{ev}(B)}
=\ell_{\operatorname{ev}(A\uplus B)}
\]

if and only if \(A\uplus B\in\mathcal M\).
3. Every other nonidentity pair is undefined.

No operation is exposed merely because EC addition is computable.

### Candidate embedding lemma

Status: RESTRICTED THEOREM CANDIDATE pending independent formal review.

If \(\mathcal M\) is finite and downward closed, contains empty and singleton multisets, and ev is injective, the operation above is:

- commutative by multiset union;
- unital by construction;
- associative with definedness because \(A\uplus B\uplus C\in\mathcal M\) implies every submultiset needed by the opposite parenthesization lies in \(\mathcal M\);
- uniquely factorable because ev assigns each represented label one prime multiset, while nonidentity labels outside ev(\(\mathcal M\)) are prime;
- compatible because every defined output is the label of the EC sum.

Missing review lemma: confirm the repeated-prime multiset interpretation against the pinned paper version and cover every identity case.

## 5. Exact axiom checks

### Identity

Check both ordered calls with identity for every label. Reject any nonidentity product outputting identity.

### Commutativity

Check symmetric definedness and equal output for every ordered pair.

### Associativity

For every ordered triple:

~~~text
if star(a,b) and star(star(a,b),c) are defined:
    star(b,c) must be defined
    star(a,star(b,c)) must be defined
    both outer results must be equal
~~~

Check literal cubic enumeration at 5–9 bits and compare it with an exact sparse composable-chain enumeration. Use the exact sparse enumeration at 10–12 bits; no sampling.

### Unique factorization

Use the paper-prime predicate:

~~~text
prime(l) :=
    l is not identity and
    there do not exist a,b different from l with star(a,b)=l
~~~

Enumerate all reachable prime multisets for each label. Identity has the empty multiset. Require exactly one prime multiset; separately record immediate parent pairs and binary trees.

### EC compatibility

For every defined pair, verify both:

\[
\operatorname{decode}(\ell_1\star\ell_2)
=\operatorname{decode}(\ell_1)+_E\operatorname{decode}(\ell_2)
\]

and, using verifier-only scalar ground truth,

\[
\sigma^{-1}(\ell_1\star\ell_2)
=\sigma^{-1}(\ell_1)+\sigma^{-1}(\ell_2)\pmod q.
\]

## 6. Constrained-label delta and edge density

Definition 3.1 gives

\[
C_\star=
\{\ell:\exists\ell'\ne\ell_O,\ \ell\star\ell'\text{ defined}\}
\cup
\{\ell:\exists\ell_1,\ell_2\ne\ell,\ \ell_1\star\ell_2=\ell\}.
\]

Compute \(C_\star\) directly and set

\[
\delta=|C_\star|/q.
\]

The identity is constrained because it can multiply a nonidentity label. Identity products do not constrain every other label because the companion required in the first clause must be nonidentity.

Do not substitute \(|F\cup2F\cup4F|/q\). Exact closure can add degree-three labels, identity contributes \(1/q\), and pruning changes endpoints.

Report role counts by degree, semantic overlaps, nonidentity edge count, edges per constrained label, normalized edge density, witness multiplicity, and star-description bits. The cited theorem uses delta, not these additional quantities; the additional metrics reveal what delta omits.

## 7. Source-tag boundary

The primary label is the EC point, not point-plus-witness.

If two source tags describe one point, sigma can select only one image label for that group element. Keeping both as labels of one semantic group value requires a new many-label or semantic-value model.

Therefore:

- quotient source records by point;
- retain one canonical source per factor-base point;
- retain one prime multiset per semantic composite;
- count discarded tags and alternate prime multisets;
- reconstruct each retained four-factor witness from its prime multiset and canonical sources;
- never credit discarded witnesses as exposed structure.

A tagged-label variant is MODEL-ESCAPE / NOT-CGHW-ELIGIBLE unless accompanied by a new formal model and theorem.

## 8. Boundary before the final join

Define

\[
A_4^{\rm ret}=
\{\operatorname{ev}(M):M\in\mathcal M,\ |M|=4,\ M\text{ retained}\}.
\]

The public partial-monoid certificate forbids:

- degree-eight multisets;
- nonidentity star edges with both inputs in \(A_4^{\rm ret}\);
- target-dependent pruning after seeing \(Q\).

The direct boundary predicate proves only that no nonidentity star edge has two
retained degree-four inputs. It does not prove absence of an equivalent lookup,
membership, predecessor, or witness-advice structure. Final pair-sum supports
and histograms used to score the optimizer belong to a separately hashed private
audit artifact; report their construction operations and bytes and do not count
them as free public structure.

The next problem is charged:

\[
\text{given }Q,\quad
\text{find }a,b\in A_4^{\rm ret}\text{ with }a+b=Q.
\]

If star exposes every \(A_4\times A_4\) pair, every output in \(A_4+A_4\) is constrained, so

\[
\delta\ge |A_4+A_4|/q.
\]

If \(A_4+A_4=G\), then \(\delta=1\). This concerns direct star exposure, not a
separately charged audit or data structure.

## 9. Smallest generated prime-order toy instances

For each bit size, search increasing prime \(p\equiv3\bmod4\), then increasing nonzero \(a_E,b_E\), requiring nonsingularity, exact prime order of the requested bit length, trace outside \(\{0,1\}\), and nonspecial \(j\). Choose the first affine point.

| q bits | p | a_E | b_E | q | trace | G |
|---:|---:|---:|---:|---:|---:|---:|
| 5 | 19 | 2 | 9 | 23 | -3 | (0, 3) |
| 6 | 43 | 1 | 3 | 47 | -3 | (2, 20) |
| 7 | 67 | 1 | 8 | 79 | -11 | (1, 12) |
| 8 | 131 | 1 | 9 | 137 | -5 | (0, 3) |
| 9 | 263 | 1 | 25 | 269 | -5 | (0, 5) |
| 10 | 523 | 1 | 42 | 557 | -33 | (0, 105) |
| 11 | 1031 | 1 | 17 | 1061 | -29 | (2, 462) |
| 12 | 2063 | 1 | 5 | 2129 | -65 | (1, 198) |

These are generator fixtures, not hypothesis evidence. The verifier must recount them. The 5–9-bit rows are the exhaustive counterexample lane; 10–12 bits are the retention lane. No scalar-recovery challenge is generated.

## 10. Policies and exact search

### P0 balanced-only

Use canonical \(1+1\to2\) and \(2+2\to4\) edges without closure. This must reproduce the associativity negative.

### P1 canonical closure

Take every canonical degree-two and degree-four witness, form full downward closure, and test ev injectivity. Preserve the first collision; do not silently prune.

### P2 exact balanced-universe optimum

Search over subsets of every distinct formal multiset in `U4_BAL`. Feasibility
requires semantic injectivity of the union of their downward closures, the
fixed singleton factors, and the empty multiset. `D2` consists exactly of the
degree-two submultisets forced by selected `D4`; no canonical degree-two node is
independently retained.

Optimize lexicographically:

1. absolute retained final split-support count;
2. retained degree-four formal multisets, which equals retained semantic outputs under injectivity;
3. smaller constrained set;
4. fewer nonidentity edges;
5. lexicographically smaller formal-multiset list.

Balanced parent-pair multiplicity is private audit data and is not an optimizer
credit or exposed structured operation.

Use exhaustive subsets or a complete branch-and-bound certificate at 5–7 bits; exact conflict-graph or MaxSAT certificates where feasible at 8–9 bits. Heuristics at 10–12 bits provide lower bounds only and cannot prove a class negative.

At five bits the proof object must bind the complete sorted `U4_BAL` universe,
its SHA-256, every individually invalid candidate, every pair conflict, explored
and pruned node counts, the full objective vector, and the lexicographic optimum.
The independent verifier reconstructs all of these fields and reruns exhaustive
search rather than trusting a claimed optimum.

Define the fixed base order ideal and each candidate order ideal by

\[
I_0=\{\varnothing\}\cup\{\{P\}:P\in F\},\qquad
I(M)=I_0\cup\operatorname{Sub}(M),
\]

where `Sub(M)` is the set of every submultiset of `M`, including empty and `M`
itself. A candidate `M` is individually invalid exactly when `ev` is
noninjective on `I(M)`. For two distinct individually valid candidates `M,N`,
the unordered pair `{M,N}` is a conflict edge exactly when `ev` is noninjective
on `I(M) union I(N)`.

### Conflict-graph completeness lemma

For `D4 subseteq U4_BAL`, its generated family is feasible if and only if `D4`
contains no individually invalid candidate and is an independent set of the
conflict graph above.

Proof: every formal element of the generated family belongs to `I0` or to
`Sub(M)` for some selected `M`. A collision lies either within one `I(M)`, which
makes that candidate individually invalid, or between elements contributed by
two selected candidate ideals, which creates their conflict edge. The converse
is immediate from the definitions.

At five bits the independent verifier must preserve and replay one direct
collision for every individually invalid vertex. By monotonicity, every subset
containing such a vertex is infeasible. It must then enumerate every subset of
the individually valid vertices and exact-compare graph independence with direct
injectivity on the full generated family. This is an exact proof for every
subset of `U4_BAL` without materializing the exponentially redundant supersets
of already invalid vertices. Testing only the optimizer winner is insufficient.
Record invalid-vertex count, valid-vertex count, exactly `2^valid_count` direct
subset comparisons, mismatch count, and a digest over the lexicographically
ordered `(subset, graph_feasible, direct_feasible)` rows.

Define the raw and selected semantic four-term sets and final supports exactly:

\[
A_4^{\rm raw}=\{\operatorname{ev}(M):M\in U_4^{\rm BAL}\},\qquad
A_4(D_4)=\{\operatorname{ev}(M):M\in D_4\},
\]

\[
S_{\rm raw}=\{x+_E y:x,y\in A_4^{\rm raw}\},\qquad
S(D_4)=\{x+_E y:x,y\in A_4(D_4)\}.
\]

Relative support is `|S(D4)|/|S_raw|`; raw absolute coverage is
`|S_raw|/q`; retained absolute coverage is `|S(D4)|/q`. The optimizer compares
feasible selections by: maximize `|S(D4)|`; maximize `|D4|`; minimize
`|C_star|`; minimize the number of unordered nonidentity star-domain pairs;
then minimize the sorted `D4` list lexicographically under the factor-index
order induced by `enc(P)`. No other tie-break is permitted.

## 11. Brute-force certificate schema

Emit canonical JSON with sorted keys and exact integer numerator/denominator ratios:

~~~json
{
  "schema": "sgcp-embed-001-certificate-v1",
  "experiment_id": "SGCP-EMBED-001",
  "claim_status": "HYPOTHESIS",
  "bindings": {},
  "implementation": {},
  "curve": {},
  "rows": [
    {
      "factor_base": {},
      "raw_witnesses": {},
      "public_model": {
        "labeling": {},
        "selected_formal_family": {},
        "star": {},
        "axioms": {},
        "constrained": {}
      },
      "private_audit": {
        "balanced_candidate_universe": [],
        "candidate_universe_sha256": "...",
        "optimizer_proof": {},
        "relative_final_support": {"numerator": 0, "denominator": 1},
        "raw_absolute_group_coverage": {"numerator": 0, "denominator": 1},
        "retained_absolute_group_coverage": {"numerator": 0, "denominator": 1},
        "target_witness_histograms": {},
        "charged_operations": {},
        "charged_bytes": 0
      },
      "controls": []
    }
  ],
  "resource_metrics": {},
  "artifact_digests": {
    "public_model_sha256": "...",
    "private_audit_sha256": "...",
    "deterministic_payload_sha256": "..."
  }
}
~~~

The builder artifact contains no scalar indices. Scalar compatibility and the
scalar-table digest appear only in the independent verification report. The
human report is derived from the public model and the explicitly charged private
audit; audit fields are never counted as free star advice.

## 12. Counterexample minimization

Every failure records its axiom, curve, \(B\), policy, labels, points, verifier scalars, formal prime multisets, star edges, and both evaluations.

Minimize in this order:

1. group-order bit length;
2. \(q,p,a_E,b_E\);
3. \(B\);
4. nonidentity edges, using deterministic delta debugging;
5. formal factor-base primes;
6. counterexample tuple length;
7. lexicographic label order.

Required witnesses:

- associativity: triple, existing left chain, and missing or unequal right chain;
- injectivity: \(M\ne N\) with ev(\(M\)) = ev(\(N\));
- unique factorization: one label and two prime multisets;
- compatibility: inputs, stored output, independent EC sum;
- source tag: two tags with one point/scalar;
- final boundary: one forbidden \(A_4\times A_4\) edge.

A policy failure is not a class negative without a complete, independently verified pruning search.

## 13. Proof track

1. Complete the downward-closed embedding lemma against the exact paper definitions, repeated primes, labels outside ev(\(\mathcal M\)), and identity cases.
2. Prove the generated formal order ideal contains every reassociation product forced by each retained four-prime product.
3. Derive exact constrained-label counts by degree; include degree three and identity.
4. Characterize ev injectivity as a restricted \(B_4\) or Freiman-isomorphism condition and identify the weakest condition needed for a selected witness family.
5. Preserve the theorem boundary: one compatible sigma implies a hard compatible-label distribution, not hardness of the conventional EC encoding.

## 14. Disproof and red-team track

1. Find the smallest closure-induced degree-three collision.
2. Classify collisions as identity/nonempty, singleton/composite, same-degree, cross-degree, within one closure, or between closures.
3. Measure witness loss caused by semantic quotienting and injectivity pruning.
4. Compare the canonical policy with the exact best feasible pruning over the frozen balanced formal-multiset universe.
5. Charge star-table description and construction separately as a concrete-algorithm diagnostic even though the model makes star free.
6. Preserve parameter reversals and do not fit a cryptographic exponent from these toys.

Model-escape routes after failure:

- semantic-value/syntactic-witness separation;
- a model allowing nonunique factorization;
- a unary coordinate-predicate oracle;
- a charged coordinate-circuit model;
- an unbalanced or alternative-coordinate witness representation.

## 15. Final join versus 3SUM-Indexing

For fixed \(A_1,A_2\subseteq G\), the next experiment preprocesses the arrays and answers:

~~~text
query(Q): return (i,j) such that A1[i] +_E A2[j] = Q, or NONE
~~~

With \(A_1=A_2=A_4^{\rm ret}\), this is the abelian-group form of 3SUM-Indexing plus source-witness output.

Direct EC baselines:

- linear complement scan with a hash dictionary: \(O(n)\) EC subtractions/lookups online and \(O(n)\) labels stored;
- complete pair-sum table: \(O(n^2)\) preprocessing/storage and expected constant lookup, charging collision lists and source indices;
- any Fiat–Naor or subfunction compiler implemented over an explicit EC function, charging advice, probes, EC/field operations, false candidates, and witness recovery.

An injective point serialization does not preserve addition. Every homomorphism from finite \(G\cong\mathbb Z_q\) to torsion-free \((\mathbb Z,+)\) is zero, so no injective global additive integer encoding exists. This only blocks the naive homomorphic transfer; it does not rule out partitioned reductions, modular carry handling, coordinate hashes, or EC-native subfunctions.

The Dinur–Golovnev integer tradeoff is an external structured upper-bound reference, not an EC theorem. A transfer claim requires:

1. a correctness-preserving reduction with carry/wrap handling and witness recovery;
2. an EC-native subfunction decomposition with a proved locality property; or
3. a randomized hash analysis bounding false candidates and charging EC verification.

Random hashing may support equality dictionaries. It must not be assumed to preserve pair sums or integer subfunction locality.

The next experiment should:

1. reproduce the integer algorithm in its own model;
2. use visible-exponent cyclic groups only to isolate modular wrap, clearly labeling exponent access as unavailable for EC;
3. test EC labels using only coordinates and group operations;
4. report advice bits, preprocessing, probes, RAM operations, EC/field operations, false candidates, verification, and witness bytes.

## 16. What remains outside this model

Even after a pass, SGCP-EMBED-001 does not model or prove:

- unary \(L(x)=0\) membership as an operation;
- four-term witnesses outside the frozen balanced universe and discarded parent-pair multiplicity;
- many syntactic labels per semantic point;
- coordinate arithmetic or star construction cost;
- summation-polynomial or Gröbner solving;
- target-independent algebraic specialization;
- the charged final join;
- random-walk relation yield;
- relation-matrix independence and rank;
- sparse linear algebra;
- factor-base logarithms;
- individual target descent;
- batch correlation or amortization;
- hardness of the standard coordinate labeling;
- cryptographic-size or deployment behavior.

These are later proof obligations, not closed frontiers.

## 17. Reproduction-oriented pseudocode

~~~text
bind contract, literature, and paper hashes
assert cwd is the SGCP branch and every output path is outside the frozen
    coordinate-energy review worktree

for qbits in 5..12:
    curve = deterministic_curve_search(qbits)
    verify curve and enumerate verifier-only scalar table
    public_points = point table without scalars

    for B in [4,6,8]:
        F, source_map = coordinate_factor_base(public_points, B)
        raw2 = all unordered degree-2 prime multisets
        canonical2 = least witness per nonidentity EC output
        raw4 = balanced pairs of canonical2 nodes
        U4_BAL = every distinct flattened raw4 formal multiset

        P0 = canonical 1+1 and 2+2 balanced edges without closure
        P1 = full closure of independently retained canonical D2 and canonical D4
        P2 = exact subset of U4_BAL; D2 is only the closure forced by selected D4

        for policy in [P0, P1, P2]:
            construct the policy-specific edge set or formal family above
            collisions = group the policy formal family by independent EC evaluation

            if collision-free:
                star = identity plus multiset-union operation
            else:
                reject embedding and retain minimized collisions

            verify every model axiom
            compute Definition 3.1 constrained set
            compute exact final support in the charged private audit without adding final star edges
            minimize failures
            emit canonical certificate row

run all controls
independently reconstruct certificate
emit hashes and exact-ratio report
~~~

Planned commands, not authorized to run until implementation review:

~~~bash
python3 -B experiments/EXP-SGCP-EMBED-001/src/sgcp_embed.py \
  --contract notes/sgcp_embed_001_contract_20260717.md \
  --literature notes/structured_group_coordinate_predicates_literature_20260717.md \
  --toy-bits 5 \
  --factor-base-sizes 4 6 8

python3 -B experiments/EXP-SGCP-EMBED-001/src/verify_sgcp_embed.py \
  --contract notes/sgcp_embed_001_contract_20260717.md \
  --literature notes/structured_group_coordinate_predicates_literature_20260717.md \
  --input experiments/EXP-SGCP-EMBED-001/preflight/sgcp-embed-001-5bit.json
~~~

## 18. Stop rules

Invalidate and stop if:

- a bound source hash differs;
- any output resolves under the frozen coordinate-energy review worktree;
- a curve fixture or group-order proof fails;
- builder-visible data contains scalar indices;
- a control misbehaves;
- the certificate cannot be independently reconstructed;
- any direct retained-\(4F\) by retained-\(4F\) star edge appears.

No ECDLP promotion is allowed until separate experiments charge final join, relation yield, rank, linear algebra, target descent, and an automorphism-aware rho baseline.

## Handoff: SGCP-EMBED-001 structured-label embedding

### Claim or task

Determine whether the balanced EC four-factor witness universe contains an injective, associative, uniquely factorable structured-label embedding after the regrouping closure forced by the Corrigan-Gibbs-Henzinger-Wu definition, while leaving the target-dependent \(4F+4F\) join charged and external.

### Status

HYPOTHESIS

### Assumptions

- Generated ordinary prime-order toy curves only; no deployed keys or canonical ECDLP run.
- Exactly one semantic label per EC point and one canonical source per factor-base point.
- For P2, only `D4 subseteq U4_BAL` is selected; `D2(D4)` is forced downward closure, with no independently selected degree-two maxima.
- Pinned 2026 structured-model definitions and hashes.
- Final-join advice/work, rank, linear algebra, and descent remain charged obligations.

### Evidence so far

- The literature basis establishes that \(L(x)=0\) alone is not a structured-model instantiation.
- Exact associativity forces \(3F\) regrouping products for any genuine balanced four-leaf witness.
- A downward-closed formal multiset family with injective EC evaluation is a concrete sufficient-condition candidate.
- Exposing all final \(4F+4F\) outputs constrains at least \(|4F+4F|\) labels.
- Integer 3SUM hashing does not transfer through ordinary point serialization without a new reduction or EC-native proof.

### Failure modes

- Associative closure creates collisions between distinct prime multisets.
- Identity or factor-base labels acquire alternate factorizations.
- Semantic quotienting discards useful witness multiplicity.
- Valid pruning loses most final split-support coverage.
- A table-defined free star hides prohibitive concrete construction/advice.
- The hard-distribution theorem is overread as a conventional-coordinate lower bound.

### Next concrete action

Implement the builder and independent verifier under
`experiments/EXP-SGCP-EMBED-001`, bind their hashes in the experiment record,
and run only the generated 5-bit control preflight before requesting approval
for a full toy sweep.

### Artifact paths

- `notes/sgcp_embed_001_contract_20260717.md`
- `notes/structured_group_coordinate_predicates_literature_20260717.md`
- Planned: `experiments/EXP-SGCP-EMBED-001/src/sgcp_embed.py`
- Planned: `experiments/EXP-SGCP-EMBED-001/src/verify_sgcp_embed.py`
- Planned: `experiments/EXP-SGCP-EMBED-001/preflight/`
