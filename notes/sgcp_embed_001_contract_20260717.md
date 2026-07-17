# SGCP-EMBED-001 experiment/proof contract

Date: 2026-07-17

Status: OPEN / HYPOTHESIS / CONTRACT-ONLY

Evidence state: no SGCP experiment, canonical ECDLP run, relation collection, or performance run has been executed under this contract.

Scope restriction: this artifact belongs only under /Volumes/Volume/autolab/research/prototypes. The audited worktree /Volumes/Volume/crypto-autoresearcher-worktrees/coordinate-energy must not be edited, used as an execution directory, or imported as a mutable dependency.

## Literature and model binding

Literature basis:

- research/prototypes/structured_group_coordinate_predicates_literature_20260717.md
- SHA-256: 8a580cf810d1e02a0e2600cae52b34d02800c02bf390de935385ac8d4dca354a

Exact model definitions were checked against Corrigan-Gibbs, Henzinger, and Wu, The Structured Generic-Group Model, Definitions 2.2, 2.3, and 3.1 and Theorems 3.2 and B.1:

- https://www.cs.utexas.edu/~dwu4/papers/SGGM.pdf
- checked PDF SHA-256: 82b40c277230d0603e5b87a3f6f5d045a7b3b8672f15f7e8ae983878296af66f

An implementation must bind both hashes. It must not invoke the theorem if the pinned definitions differ.

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

For every mandatory generated prime-order toy instance, there is a deterministic canonical or exactly pruned family of four-factor witnesses whose minimum associative completion:

1. is a Corrigan-Gibbs-Henzinger-Wu structured label space;
2. admits an injective EC-compatible labeling of order \(q\);
3. uses one semantic label per EC point and one canonical source per factor-base point;
4. exposes no \(4F+4F\) operation;
5. has exact constrained-label fraction \(\delta=|C_\star|/q\);
6. retains at least 90 percent of raw final split-support coverage on each of the 10-, 11-, and 12-bit toy instances.

Coverage is target support for the still-charged final join. It is not relation rank or DLP success.

## Null hypothesis

Under the fixed semantic-label, balanced-four-witness, downward-closed completion class, at least one of the following holds:

- balanced-only edges violate exact associativity;
- associative closure maps distinct formal prime multisets to one EC label;
- a nonempty selected multiset sums to the identity;
- source-tag multiplicity cannot be represented by one injective labeling;
- every valid pruning retains less than 50 percent of raw final split-support coverage;
- meeting retention requires exposing the forbidden final layer.

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

Use repetitions 0 through 15 at 5–9 bits and 0 through 7 at 10–12 bits.

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
- canonical witnesses retained and alternate witnesses discarded;
- star-table description bits and source-witness bytes;
- source-tag multiplicity and tags discarded by semantic quotienting;
- final split-support ratio

\[
R_{\rm support}=
\frac{|A_4^{\rm ret}+A_4^{\rm ret}|}
{|A_4^{\rm raw}+A_4^{\rm raw}|};
\]

- target-wise final-witness histogram;
- identity, commutativity, associativity, compatibility, unique-factorization, acyclicity, source-faithfulness, and final-boundary results;
- minimized counterexample digest;
- builder/verifier operations, memory, and wall time as implementation diagnostics only.

## Positive controls

1. PC-FREE-MONOID: a downward-closed free commutative monoid through degree four. It must pass identity, commutativity, associativity, and unique prime-multiset factorization.
2. PC-CYCLIC-NO-WRAP: a prime cyclic group whose retained degree-at-most-four source sums are distinct before reduction. It must pass all embedding checks.
3. PC-EC-FOREST: greedily retain one four-witness closure with injective EC evaluation. If one exists, it must pass even if coverage is small.

A failed positive control invalidates the run.

## Negative controls

1. NC-BALANCED-ONLY: retain only \(1+1\to2\) and \(2+2\to4\) for a genuine four-leaf witness. Exact associativity must fail.
2. NC-ALL-WITNESSES: retain all EC witness edges. Once a collision exists, unique factorization must fail.
3. NC-DUPLICATE-TAG: demand two source-tag labels for one EC point. The one-label-per-element gate must reject it.
4. NC-COMPAT-MUTATION: mutate one edge output. Compatibility must fail at that edge.
5. NC-FINAL-EDGE: add one \(A_4\times A_4\) edge. The boundary gate must fail and delta must be recomputed.

A missed negative control invalidates the run.

## Success criterion

Report a positive TOY-EVIDENCE / MODEL-EMBEDDING result only if:

1. every control behaves as preregistered;
2. every mandatory curve and \(B\) row has an independent certificate;
3. one fixed coordinate-only policy passes every model axiom on every mandatory row;
4. the final join is absent from star;
5. \(R_{\rm support}\ge0.90\) on the 10-, 11-, and 12-bit rows for every \(B\);
6. delta, edge density, source loss, and table size are reported exactly;
7. the existential-hard-distribution limitation is explicit.

This does not establish a faster-than-rho ECDLP algorithm, rank, target descent, or deployment relevance.

## Falsification criterion

- Fixed-policy negative: the deterministic canonical policy fails an axiom or retention gate. This rules out only that policy.
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

## 3. Minimum associative completion

Let \(\mathcal M_{\max}\) contain selected degree-two and degree-four prime multisets. Define

\[
\mathcal M=
\{\varnothing\}\cup\{\{P\}:P\in F\}
\cup\{A:A\text{ is a submultiset of some }M\in\mathcal M_{\max}\}.
\]

This downward closure includes every degree-three and degree-two regrouping forced by a retained four-witness.

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

This experiment forbids:

- degree-eight multisets;
- nonidentity star edges with both inputs in \(A_4^{\rm ret}\);
- free membership, predecessor, or witness access for \(A_4^{\rm ret}+A_4^{\rm ret}\);
- target-dependent pruning after seeing \(Q\).

The next problem is charged:

\[
\text{given }Q,\quad
\text{find }a,b\in A_4^{\rm ret}\text{ with }a+b=Q.
\]

If star exposes every \(A_4\times A_4\) pair, every output in \(A_4+A_4\) is constrained, so

\[
\delta\ge |A_4+A_4|/q.
\]

If \(A_4+A_4=G\), then \(\delta=1\). This concerns free exposure, not a separately charged data structure.

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

### P2 max-retention valid closure

Search over subsets of canonical degree-four prime multisets. Feasibility requires semantic injectivity of the union of their downward closures, singleton factors, empty multiset, and retained degree-two witnesses.

Optimize lexicographically:

1. final split-support coverage;
2. retained degree-four outputs;
3. retained source witnesses;
4. smaller constrained set;
5. fewer nonidentity edges;
6. lexicographically smaller witness list.

Use exhaustive subsets or a complete branch-and-bound certificate at 5–7 bits; exact conflict-graph or MaxSAT certificates where feasible at 8–9 bits. Heuristics at 10–12 bits provide lower bounds only and cannot prove a class negative.

## 11. Brute-force certificate schema

Emit canonical JSON with sorted keys and exact integer numerator/denominator ratios:

~~~json
{
  "schema": "sgcp-embed-001-certificate-v1",
  "experiment_id": "SGCP-EMBED-001",
  "claim_status": "TOY-EVIDENCE|NEGATIVE-RESULT|OPEN",
  "contract_sha256": "...",
  "literature_sha256": "8a580cf810d1e02a0e2600cae52b34d02800c02bf390de935385ac8d4dca354a",
  "sggm_pdf_sha256": "82b40c277230d0603e5b87a3f6f5d045a7b3b8672f15f7e8ae983878296af66f",
  "implementation": {
    "git_commit": "...",
    "builder_sha256": "...",
    "verifier_sha256": "...",
    "command_argv": [],
    "timestamp_utc": "..."
  },
  "curve": {
    "p": 0, "a": 0, "b": 0, "q": 0, "trace": 0,
    "generator": [0, 0],
    "point_table_sha256": "...",
    "group_order_proof": {}
  },
  "factor_base": {
    "B": 0,
    "L_roots": [],
    "labels": [],
    "canonical_sources": [],
    "discarded_source_tags": []
  },
  "raw_witnesses": {
    "degree2_count": 0,
    "degree4_count": 0,
    "multiplicity_histograms": {},
    "support_sizes": {}
  },
  "formal_family": {
    "maximal_multisets": [],
    "downward_closure_by_degree": {},
    "evaluation_map": [],
    "evaluation_injective": false,
    "evaluation_collisions": []
  },
  "labeling": {
    "label_order": [],
    "sigma_scalar_to_label": [],
    "injective": false,
    "identity_label": "..."
  },
  "star": {
    "identity_rule_total": false,
    "unordered_nonidentity_edges": [],
    "ordered_domain_sha256": "...",
    "description_bits": 0
  },
  "axioms": {
    "identity": {},
    "commutativity": {},
    "associativity": {},
    "compatibility_coordinates": {},
    "compatibility_scalars": {},
    "unique_prime_multiset_factorization": {},
    "binary_tree_multiplicity": {},
    "acyclic": {},
    "final_layer_excluded": {}
  },
  "constrained": {
    "labels": [],
    "count": 0,
    "delta": {"numerator": 0, "denominator": 1},
    "role_counts": {},
    "edge_density": {}
  },
  "retention": {
    "raw_final_support": 0,
    "retained_final_support": 0,
    "support_ratio": {"numerator": 0, "denominator": 1},
    "target_witness_histograms": {}
  },
  "controls": [],
  "counterexamples": [],
  "resource_metrics": {},
  "artifact_digests": {}
}
~~~

The human report is derived from this JSON.

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
2. Prove the minimum reassociation closure forced by each retained four-prime product.
3. Derive exact constrained-label counts by degree; include degree three and identity.
4. Characterize ev injectivity as a restricted \(B_4\) or Freiman-isomorphism condition and identify the weakest condition needed for a selected witness family.
5. Preserve the theorem boundary: one compatible sigma implies a hard compatible-label distribution, not hardness of the conventional EC encoding.

## 14. Disproof and red-team track

1. Find the smallest closure-induced degree-three collision.
2. Classify collisions as identity/nonempty, singleton/composite, same-degree, cross-degree, within one closure, or between closures.
3. Measure witness loss caused by semantic quotienting and injectivity pruning.
4. Compare the canonical policy with the exact best feasible pruning.
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
- discarded noncanonical witnesses;
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
assert cwd and every output path are outside the audited worktree

for qbits in 5..12:
    curve = deterministic_curve_search(qbits)
    verify curve and enumerate verifier-only scalar table
    public_points = point table without scalars

    for B in [4,6,8]:
        F, source_map = coordinate_factor_base(public_points, B)
        raw2 = all unordered degree-2 prime multisets
        canonical2 = least witness per nonidentity EC output
        raw4 = balanced pairs of canonical2 nodes
        canonical4 = least flattened witness per nonidentity EC output

        for policy in [P0, P1, P2]:
            maxima = choose selected degree-2 and degree-4 multisets
            formal_M = full downward closure plus empty and F singletons
            collisions = group formal_M by independent EC evaluation

            if collision-free:
                star = identity plus multiset-union operation
            else:
                reject embedding and retain minimized collisions

            verify every model axiom
            compute Definition 3.1 constrained set
            compute exact final support without adding final star edges
            minimize failures
            emit canonical certificate row

run all controls
independently reconstruct certificate
emit hashes and exact-ratio report
~~~

Planned commands, not authorized to run until implementation review:

~~~bash
python3 research/prototypes/sgcp_embed_001.py build \
  --contract research/prototypes/sgcp_embed_001_contract_20260717.md \
  --toy-bits 5,6,7,8,9,10,11,12 \
  --factor-base-sizes 4,6,8 \
  --policies balanced-only,canonical-closure,max-retention-closure \
  --output research/prototypes/sgcp_embed_001_artifacts/certificate.json

python3 research/prototypes/verify_sgcp_embed_001.py \
  --contract research/prototypes/sgcp_embed_001_contract_20260717.md \
  --certificate research/prototypes/sgcp_embed_001_artifacts/certificate.json \
  --output research/prototypes/sgcp_embed_001_artifacts/verification.json
~~~

## 18. Stop rules

Invalidate and stop if:

- a bound source hash differs;
- any output resolves under the audited worktree;
- a curve fixture or group-order proof fails;
- builder-visible data contains scalar indices;
- a control misbehaves;
- the certificate cannot be independently reconstructed;
- any final \(4F+4F\) edge appears.

No ECDLP promotion is allowed until separate experiments charge final join, relation yield, rank, linear algebra, target descent, and an automorphism-aware rho baseline.

## Handoff: SGCP-EMBED-001 structured-label embedding

### Claim or task

Determine whether a canonical EC four-factor witness prefix admits an injective, associative, uniquely factorable structured-label embedding after the regrouping closure forced by the Corrigan-Gibbs-Henzinger-Wu definition, while leaving the target-dependent \(4F+4F\) join charged and external.

### Status

HYPOTHESIS

### Assumptions

- Generated ordinary prime-order toy curves only; no deployed keys or canonical ECDLP run.
- Exactly one semantic label per EC point and one canonical source per factor-base point.
- Downward closure of selected degree-two and degree-four prime multisets.
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

Implement the builder and independent verifier under /Volumes/Volume/autolab/research/prototypes, bind their hashes in a versioned amendment, and run only the generated 5-bit control preflight before requesting approval for a full toy sweep.

### Artifact paths

- /Volumes/Volume/autolab/research/prototypes/sgcp_embed_001_contract_20260717.md
- /Volumes/Volume/autolab/research/prototypes/structured_group_coordinate_predicates_literature_20260717.md
- Planned: /Volumes/Volume/autolab/research/prototypes/sgcp_embed_001.py
- Planned: /Volumes/Volume/autolab/research/prototypes/verify_sgcp_embed_001.py
- Planned: /Volumes/Volume/autolab/research/prototypes/sgcp_embed_001_artifacts/
