# Query2P1 independent red team

Task: `TASK-20260718-P1553-Q2P1-RT-R1`  
Role: independent Red Team  
Date: 2026-07-18  
Evidence: theorem and primary-literature review only; zero runs

No experiment, solver, fixture, timing run, relation campaign, shared-state
edit, P1554 allocation, unrestricted lower bound, Shoup improvement, or
breakthrough claim is made.

## Terminal scoped verdict

`REVISE_PRODUCER__INDEXING_AND_NARROW_QUOTIENT_CONTROLS_RECONSTRUCT__PCZT_E_IS_QUERY2P1_RENAMED_WITH_AN_UNTYPED_TRANSLATED_DIVISOR_MACRO__STANDARD_REALIZATIONS_RESTORE_B3_OR_B4__TARGET_LABEL_ZERO_DIVISOR_COMMON_FACTOR_OPERATION_UNCONSTRUCTED__REPRESENTATION_SENSITIVE_EXCEPTION_PRESERVED__NO_RUN__NO_BREAKTHROUGH`

The producer's indexing arithmetic, narrow prime-order quotient lemma,
known-scalar carry control, and conditional MPZ substitution reconstruct. The
claimed conditional reduction to PCZT-E does not. PCZT-E receives the same
preprocessing, target, restrictions, decision contract, witness contract, and
budget as Query2P1. Its displayed product is an exact restatement of the same
existential predicate, while its O(B) gate count treats a translation of an
entire degree-B^2 divisor as one untyped macro.

The narrow surviving exception is not PCZT-E. It is an explicit
target-label zero-divisor/common-factor operation producing a polynomial or
factor of degree at most B. Standard constructions of that object still expose
B^3 traffic. A representation-sensitive construction remains untested.

## 1. Frozen accounting

Set

```text
N = B^5,
setup time and retained advice <= B^(9/4+o(1)) = N^(0.45+o(1)),
online time and workspace       <= B^(5/4+o(1)) = N^(0.25+o(1)),
Pollard rho                       B^(5/2+o(1)) = N^(0.5+o(1)).
```

These resources are distinct:

| Resource | What is charged |
|---|---|
| Preprocessing construction | Every pair addition, sort, product-tree node, source backpointer, random trial, and detected rebuild before R is known |
| Retained advice | Every field element, point, occurrence label, dyadic membership, pointer, random seed needed online, and its word/bit width |
| Online query | All B values R-a, every target-dependent translation, false-positive cleanup, zero test, negative branch, and retry |
| Online workspace | Peak live target-dependent coefficients, quotient coordinates, branch state, and witness data |

For one canonical dyadic node in each source tree, materializing every leaf
pair in all ancestor-node pairs costs

```text
O(B^2 log^2 B) = B^(2+o(1))
```

construction and occurrence advice. That fits setup. If a restriction means a
union of canonical nodes, all node-pair combinations must also be selected and
aggregated. If only leaf pairs are retained once, online filtering is not free.
The producer needs to freeze which meaning is intended.

Source replay makes O(log B) calls, not one call. Polylogarithms do not change
the exponent, but every positive and negative child call belongs to the online
charge.

## 2. Small quotients and the carry counterexample

The narrow group statement is correct:

> A homomorphism from a cyclic prime-order group is constant or injective.

It excludes a proper nontrivial homomorphic image. It does not exclude all
small-range functions, nonhomomorphic hashes, coordinate algorithms, or
known-scalar arithmetic.

For known canonical representatives `x_i,r in [0,N)`, the exact relation is

```text
sum_i x_i = r (mod N)
iff
sum_i x_i = r + cN
```

for constantly many wraps c. Integer modular hashing can enumerate those wraps
and the ordinary base-m carries. This is a valid exact control.

The circular point step is obtaining `log_P(R) mod m`. With `m=B^3`, a supplied
residue leaves

```text
N/m = B^2
```

possible quotients. Since m is invertible modulo prime N,

```text
R-[r0]P = [t]([m]P),  0 <= t < Theta(B^2),
```

and BSGS completes t in B group work and B memory. Thus the scalar residue is
already powerful partial-DLP advice; integer hashing itself is not invalid.

This counterexample prevents the homomorphic lemma from being promoted into a
blanket small-quotient claim.

## 3. Indexing theorem reconstruction

The primary theorem substitutions agree with the producer.

### Dinur-Golovnev v2

For two lists of length `n=B^2`, the symmetric 3SUM-indexing tradeoff gives

```text
P = B^4,
S = B^(5-2 delta),
T = B^(2 delta).
```

For one target, `T<=B^(5/4)` forces `delta<=5/8`, hence
`S>=B^(15/4)`. Sweeping all B fifth points costs `B^(1+2 delta)`;
the cap then forces `delta<=1/8`, hence `S>=B^(19/4)`. Preprocessing remains
B^4, and the theorem indexes fixed lists rather than dyadic source subsets.

For the asymmetric `n=B^2`, `m=B^3` encoding,

```text
P = B^5,
S = B^(6-2 delta),
T = B^(2 delta).
```

The target cap again gives `S>=B^(19/4)`. The B^3 second list is already
outside the online rectangle.

The kSUM controls also reconstruct:

```text
four summands: k=5, delta=1 -> P=B^4, S=B^(7/2), T=B;
five summands: k=6, delta=1 -> P=B^5, S=B^(9/2), T=B.
```

Neither supplies separate-source dyadic semantics or an additive map from
fresh elliptic points to integers.

### Preprocessed universes

With pair universes of size `n=B^2`, Kasliwal-Polak-Sharma gives B^4
preprocessing and B^3 query time. Known-C retained state is B^3, but the set
`{R-a}` is unavailable before fresh R; unknown-C retained state is B^4. Its
modular false-positive removal is valid for integer addition because the
congruence and carry relation are explicit. It does not repair a nonadditive
coordinate serialization.

Kirkpatrick-Kuszmaul-Mathialagan-Vassilevska Williams gives

```text
P = B^4,
S = B^(4-4 epsilon/3),
Q = B^(3+2 epsilon),  0 <= epsilon <= 1/2.
```

The minimum state exponent is `10/3`; the minimum query exponent is 3, at a
different endpoint. The guarantee is randomized with high probability against
an oblivious adversary. It is not an exact worst-case Query2P1 interface
without an additional detected-failure construction.

All these theorems are positive upper-bound controls. Their failure to enter
the rectangle is not a data-structure lower bound.

## 4. PCZT-E is not a reduction

Write the selected pair endpoint divisors as D12 and D34. On a valid complete
elliptic model, the intended expression is

```text
K_R(U) = product_(a in I5) H34(R-a-U).
```

The claimed common-zero statement is

```text
exists U:
  H12(U)=0 and K_R(U)=0
iff
exists u in D12, v in D34, a in I5:
  u+v+a=R.
```

That is Query2P1 after distributing an existential quantifier through a
product. PCZT-E contributes no intermediate object, transform, access model,
or implementable algebraic grant.

The compact-gate count has two representations, and both expose the omission:

1. If H34 is a dense degree-B^2 section, translating it by each of B different
   points costs B^2 represented coefficients per translation, hence B^3.
2. If H34 remains a B^2-leaf product, instantiating its equality leaves for
   each of B target points gives B^3 `(v,a)` leaves.

Sharing the generic translation formula in a DAG does not share its B distinct
parameter values or outputs. A symbolic parameter T moves the computation to
the B-dimensional fifth-label algebra; a degree-B^2 pair section over that
algebra again has B^3 base-field coordinates. Calling each translated whole
divisor one gate assumes the missing higher-order operation.

The identity mutation is decisive: replace the name PCZT-E by its contract.
The producer then says, "given the Query2P1 inputs, answer Query2P1 exactly and
return its witness." The product notation does not change the operation.

## 5. Exact roots, cancellation, and charts

Three semantics must remain separate.

**Common roots.** Over a field and on a valid chart,

```text
H12 and product_a F_a have a common root
iff
H12 and some F_a have a common root.
```

A product cannot cancel a zero. Likewise, in a squarefree split label algebra,
the norm of an element is zero exactly when one component is zero.

**Coefficient reporters.** A trace, moment, selected coefficient, or weighted
checksum can cancel between components. Such a reporter is not an existence
bit unless an extra theorem establishes the biconditional. Common-root
existence must not be inferred from a cancellation-prone aggregate.

**Invalid charts.** An affine addition formula can acquire denominator or
base-locus zeros. Multiplying incomplete chart equations can therefore create
false roots. PCZT-E names "complete charts/saturation" but does not provide:

- a finite chart cover and applicability selectors;
- complete signed addition and negation laws;
- saturated ideals removing denominator components;
- tangent, vertical, infinity, repeated-support, and nonreduced rules;
- compatible line bundles/local trivializations and gluing; or
- a proof that every valid source appears once under the chosen occurrence
  semantics.

An effective endpoint divisor also merges equal endpoints. Existence survives
that merge, but labelled witness replay requires every factor to retain its
ordered source occurrence, signs, chart branch, and dyadic ancestors. A common
factor without those backpointers is not a source witness.

## 6. Dynamic evaluation in the no-relation case

Let the fifth labels be distinct `t_a`, and define

```text
g_I(T) = product_(a in I5)(T-t_a),
A5     = F_p[T]/g_I(T) = Map(I5,F_p).
```

For each component, let `r_R(t_a)` be the exact complete-chart intersection
resultant between D12 and the reflected translate of D34 by `R-a`.

In a no-relation query,

```text
r_R(t_a) != 0 for every a,
gcd(g_I,r_R) = 1,
r_R is a unit in A5.
```

There is no zero divisor on which dynamic evaluation can split. A brancher
whose progress event is an early zero or relation must inspect every component
or invoke a genuine aggregate unit/common-factor test. The standard
componentwise route performs B degree-B^2 pair-divisor tests, for B^3 total
work. A product tree redistributes these tests; it does not create the aggregate
certificate.

The same issue appears during source replay. Even with a positive parent,
the queried child can be negative. Exact complexity cannot be justified only
by favorable early relation discovery.

This no-relation unit mutation rejects branching-only speedups. It is not a
lower bound against a new batched, aggregate, or representation-sensitive
algorithm.

## 7. Smallest non-tautological residual

The useful residual can be stated without renaming Query2P1.

Preprocess source-labelled dyadic pair-divisor trees for D12 and D34 and a
squarefree occurrence-label tree for I5. For a fresh R and canonical dyadic
restrictions, interpolate the complete signed fifth point `A_I(T)` in A5 and
define

```text
r_R(T) = complete elliptic intersection resultant of
         D12 and (tau_(R-A_I(T)) o [-1])_* D34,
         reduced modulo g_I(T),

z_R(T) = gcd(g_I(T), r_R(T)).
```

The required output is `z_R(T)`, an equivalent nontrivial factor, or a unit
certificate. Its degree is at most B. A nonconstant factor identifies exactly
the fifth occurrence labels that extend to a selected pair-pair relation.

This is narrower than Query2P1 because it names a checkable algebraic output,
not merely the desired bit. Given a fifth label, source-labelled dyadic pair
replay and direct group verification are separate operations. It is also more
demanding than a cancellation-prone coefficient reporter.

The operation is not constructed. Standard dense section, resultant,
quotient-ring, split norm, triangular, power-projection, and componentwise
realizations expose B^3 traffic. A representation-sensitive algorithm that
constructs this degree-B output from compact pair trees without that traffic
remains outside the negative.

No intrinsic elliptic shortcut survived this review:

- complete coordinate or Semaev leaves give exact local predicates but no
  sub-B^3 contraction;
- x-only Semaev equations admit compatible signs rather than the supplied
  signed occurrences;
- a nontrivial character of the prime-order point group has order N, while an
  efficiently computable scalar orientation or all N modes is unavailable;
- extension-field or pairing characters require their field degree,
  construction, rational-point return, and injective orientation to be charged;
- ECFFT accelerates polynomial operations through an auxiliary smooth-order
  elliptic tree and does not diagonalize addition in this prime-order target
  group; and
- dynamic triangular/equiprojectable methods operate after a represented
  zero-dimensional algebra is supplied.

Special deck families, an untested target-local data structure, and a concrete
representation-sensitive implementation of `z_R` remain explicit exceptions.

## 8. Operation-level deduplication

| Owner | Same operation and information flow |
|---|---|
| P1513 | Translated pair-divisor product and common-factor localization. PCZT-E is its compact syntax with the locator left as a macro. |
| P1551 | Endpoint existence/coefficient aggregation plus labelled source unranking. PCZT-E asks for the same missing oracle. |
| P1516 | B^2 target-independent pair states plus an absent target-local collision router. Query2P1 asks for that router on two pair decks and one fifth deck. |
| IDEA-138 | Witness self-reduction from a supplied nonzero conditional predicate; replay does not construct the predicate. |
| IDEA-156 | Exact conditional coefficient/existence queries over a finite source grid; compact syntax plus conditioning is the same flow. |
| IDEA-199 | Endpoint coefficient access and exact source unranking from a compact transform; changing the backend does not supply the coefficient deck. |
| IDEA-266 | Dynamic zero-divisor splitting after a source algebra is supplied; branching does not construct the algebra or improve the negative worst case. |

The target-label `z_R` output is a sharpening of the P1513/P1551/P1516 residual,
not a new hypothesis owner.

## 9. Conditional generic extraction control

Maurer-Portmann-Zhu Theorem 3 gives, in its preprocessing dense-representation
extraction model,

```text
success <= 3 * advice_bits * (k_main+1)^2 / N.
```

At the frozen caps, suppressing word-size logarithms,

```text
advice_bits * k_main^2
  = B^(9/4) * B^(2*5/4)
  = B^(19/4)
  = B^4.75
  < B^5
  = N.
```

Therefore a complete generic DLP extraction reduction with constant success at
these resources would conflict with that model. Query2P1 is not generic DLP
extraction, and coordinates are representation data. This benchmark is not a
Query2P1, coordinate, Semaev, or circuit lower bound.

## 10. Primary literature check

The following primary versions were checked:

1. Dinur and Golovnev, *Improved Time-Space Tradeoffs for 3SUM-Indexing*,
   [arXiv:2512.04258v2](https://arxiv.org/abs/2512.04258v2). The fixed-list
   3SUM/kSUM tradeoffs and preprocessing charges reconstruct; subset-universe
   semantics do not follow.
2. Kasliwal, Polak, and Sharma, *3SUM in Preprocessed Universes: Faster and
   Simpler*, [arXiv:2410.16784v3](https://arxiv.org/abs/2410.16784v3). The
   source-subset and modular false-positive semantics are integer-additive.
3. Kirkpatrick, Kuszmaul, Mathialagan, and Vassilevska Williams,
   *Preprocessed 3SUM for Unknown Universes with Subquadratic Space*,
   [arXiv:2602.11363v1](https://arxiv.org/abs/2602.11363v1). Theorem 1.1 gives
   the cited tradeoff and states the oblivious-adversary limitation.
4. Maurer, Portmann, and Zhu, *Unifying Generic Group Models*,
   [IACR ePrint 2020/996](https://eprint.iacr.org/2020/996). Theorem 3 and
   Corollary 3 give the conditional advice-times-main-query benchmark; Theorem
   2 and Corollary 2 give the N^(1/3) upper controls up to logarithms.
5. Semaev, *Summation polynomials and the discrete logarithm problem on
   elliptic curves*, [IACR ePrint 2004/031](https://eprint.iacr.org/2004/031).
   Its x-coordinate existence equation does not select the supplied signs.
6. Kedlaya and Umans, *Fast Polynomial Factorization and Modular
   Composition*, [primary PDF](https://users.cms.caltech.edu/~umans/papers/KU08-final.pdf).
   Its finite-ring input is represented; it does not grant a constant-cost
   parameterized whole-divisor translation gate.
7. Dahan, Moreno Maza, Schost, Wu, and Xie, *Lifting Techniques for
   Triangular Decompositions*,
   [primary PDF](https://users.math.msu.edu/users/wenyuanwu/papers/Lifting_DMSWX.pdf).
   Dynamic lifting consumes a supplied zero-dimensional system or triangular
   representation.

## 11. Exactly one next action

Under existing P1553/P1513/P1551/P1516 ownership, replace PCZT-E by one
theorem-only specification of the target-label zero-divisor/common-factor
operation `z_R(T)=gcd(g_I(T),r_R(T))`; either give a complete-chart,
source-labelled algorithm that constructs `z_R` from the dyadic pair trees
within `B^(9/4+o(1))` preprocessing/advice and `B^(5/4+o(1))` total online
time/workspace including replay, or preserve it as the sole explicit
representation-sensitive exception with the B^3 standard route charged.

## 12. Hash bindings and checks

The exact task object was canonicalized with

```text
jq -S -c '.. | objects | select(.id? ==
"TASK-20260718-P1553-Q2P1-RT-R1")' coordination/dispatch_queue.json
```

and hashes to
`76b57236129be2262bc05794f2cf41f8feb499b68b1da6c053beb64dcfee5077`.

| Local read-scope input | SHA-256 |
|---|---|
| `AGENTS.md` | `4b9810aaa2c96a9e8d7db097d6abfc8cbeb24038df3a09e98f0beb4c23a6d362` |
| `agents/red-team.md` | `7ae9372d518fba2b9868eccf1d99102cde1ac6dae2d7bb593971d264314893f5` |
| `ideas/artifacts/ECDLP-IDEA-012/p1553_finite_deck_weighted_endpoint_gate_r2.md` | `55acc1457e7fd5a740da57c2c1db957374c7c18561c67b1748176dc8c61fcda5` |
| `coordination/tasks/TASK-20260718-P1553-Q2P1-P1/query2p1_report.yaml` | `60488d10253b4161562704e048a5e57dda33e031051ed00cf43ad339ac9125bb` |
| `coordination/tasks/TASK-20260718-P1553-Q2P1-P1/query2p1_theorem_gate.md` | `0f6d5e1caabbe2edfd84f76404805e2d4df5316263d384ad0e10f0b685527f92` |
| `ideas/artifacts/ECDLP-IDEA-121/translated_product_common_norm_v3_audit_v2.md` | `407e3c7da6345f156f7c6bcaa75749e16b6184735d32be4b6e4aca69427763d5` |
| `ideas/artifacts/ECDLP-IDEA-121/ku_circuit_reduction_v2.md` | `6fcca1d12e911f6eb2142ac96b6d0a83b6ac20db11efd06bc24c0abb7c99dc48` |
| `ideas/artifacts/ECDLP-IDEA-165/pair_sum_quotient_theorem.md` | `18cebc9c209c6ba0d705e43da7f921885e60d3436b201375e306e14f4ae0bdb2` |
| `ledger/FINDING-PF-IC-001.md` | `3776db92945bcb673a41aca3603b0fa3a516f9f3dd8a71b3efbc11d795a1d633` |
| `focus/current_plan.json` | `21dd1a00bc71f2e5987dd4709bf57f1e054c7c51913fb8027a9628da120f4f25` |
| `coordination/dispatch_queue.json` | `f282d915a6a248e509cce6bd7844614d82a21f22dbe4f0cb7a97443b430aed32` |

Supplementary operation-dedup inputs were also byte-bound:

| Supplementary input | SHA-256 |
|---|---|
| `ideas/artifacts/ECDLP-IDEA-195/p1551_finite_domain_selector_circuit_gate.md` | `5f1bd9c12ca700074c9cd327f6539bc880ec60b27431dc5f34e23b0a12f6c68f` |
| `ideas/rejected/ECDLP-IDEA-138_sumcheck_source_self_reduction_hypothesis.md` | `e99daa8a7993266ae86dd9574d122d0b00e9cd897c5673937c6bb8534192af13` |
| `ideas/rejected/ECDLP-IDEA-156_combinatorial_nullstellensatz_source_self_reduction_hypothesis.md` | `228c2d55df137225c92f2a14afca188d09bc8917ced63b6c4d4ac2027accda39` |
| `ideas/rejected/ECDLP-IDEA-199_ranked_subset_convolution_source_unranking_hypothesis.md` | `ab36b80667d444a6be41439b89e8c133f2ef3e8fdeef0babb8408cccea84399e` |
| `ideas/rejected/ECDLP-IDEA-266_equiprojectable_dynamic_evaluation_source_tree_hypothesis.md` | `a9529076339b09b881d4504de45c132219352d4e0edc282cc0d2d955577ea1b1` |

Both producer receipts were present. The producer YAML was parsed as a mapping;
the local JSON inputs parsed; all scoped paths existed. The final reports are
ASCII-only and no file outside this task's two deliverables was written.
