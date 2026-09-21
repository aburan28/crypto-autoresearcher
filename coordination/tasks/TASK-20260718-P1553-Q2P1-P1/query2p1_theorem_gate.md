# Query2P1 theorem gate

Task: `TASK-20260718-P1553-Q2P1-P1`  
Role: Idea Generator  
Date: 2026-07-18  
Verdict: **conditional reduction plus scoped named-route failure; no constructed Query2P1**

No experiment, solver, fixture, timing run, shared-state edit, contract, P1554
allocation, or cryptanalytic result is asserted here.

## 1. Frozen question

Let `G=<P>` have prime order `N=p^(1+o(1))`, and set `B=N^(1/5)`.
There are five labelled signed decks `F1,...,F5`, each of size `Theta(B)`,
and a fresh online target `R`. The frozen preprocessing builds source-labelled
dyadic pair indexes

```text
D12 = {(a1,a2,u=a1+a2)}       |D12|=Theta(B^2),
D34 = {(a3,a4,v=a3+a4)}       |D34|=Theta(B^2).
```

For online dyadic restrictions `I1,...,I5`, Query2P1 must decide exactly

```text
C_R = sum_{u+v+a=R} m12(u) m34(v) m5(a) != 0
```

and recover one fully labelled source tuple with `O(log B)` replay and final
group verification. The complete budget is setup/advice/state
`B^(9/4+o(1))` and online time/workspace `B^(5/4+o(1)`. In `N` exponents,
the rectangle is `lambda=0.45`, online `mu=0.25`. Target-dependent advice,
scalar residues of `R`, dropped signs, and omitted exceptional charts are not
allowed.

## 2. Narrow quotient theorem and carry mutation

**Lemma 1 (prime-order homomorphic quotient).** If `q:G->H` is a group
homomorphism, then `q` is constant or injective. In particular, a nonconstant
homomorphic image has order `N`.

**Proof.** The kernel is a subgroup of the prime-order group `G`, hence has
order `1` or `N`. These give the injective and constant cases. QED.

This is deliberately narrow. It rules out a small **homomorphic** quotient and
an all-input zero-sum predicate that factors only through such a quotient. It
does not rule out coordinate algorithms, target-local structures, special
decks, known-scalar integer hashing, or representation-sensitive circuits.

**Known-scalar carry control.** If canonical representatives
`x_i,r in [0,N)` are known, then

```text
sum_i x_i = r (mod N)  iff  sum_i x_i = r + cN
```

for one of constantly many wrap values `c`. Integer modular hashing may then
enumerate the ordinary base-`m` carries and wraps. The load-bearing hypothesis
is knowledge of the scalar representatives. For a point challenge,
`kP -> k mod m` is not a homomorphism `C_N -> Z_m` unless `m` divides `N`, and
computing the canonical residue is partial DLP.

For the natural `m=B^3`, an oracle giving
`r0=log_P(R) mod m` leaves `Theta(N/m)=Theta(B^2)` candidates
`r=r0+t*m`. Since `m` is invertible modulo prime `N`,

```text
R-[r0]P = [t]([m]P),       0 <= t < Theta(B^2).
```

BSGS completes this interval in `~O(B)` group work and `O(B)` memory. Thus the
known-scalar carry mutation is a valid integer control, but the required point
residue is already enough partial DLP information to complete the fresh-target
DLP at the online exponent. It is not a free Query2P1 map.

## 3. Current indexing controls

The formulas below were checked against the current primary versions:

* Dinur-Golovnev v2: symmetric 3SUM-Ind has
  `S=~O(n^(2.5-delta))`, `T=~O(n^delta)`, preprocessing `~O(n^2)`;
  asymmetric 3SUM-Ind has `S=~O(n^(1.5-delta)m)`,
  `T=~O(n^delta)`; kSUM-Ind has
  `S=~O(n^(k-.5-delta))`, `T=~O(n^delta)`, preprocessing
  `~O(n^(k-1))` [primary v2](https://arxiv.org/abs/2512.04258v2).
* Kasliwal-Polak-Sharma v3 gives quadratic preprocessing and
  `~O(n^1.5)` subset-query time; unknown `C` uses quadratic space
  [primary v3](https://arxiv.org/abs/2410.16784v3).
* Kirkpatrick-Kuszmaul-Mathialagan-Vassilevska Williams v1 gives
  `P=~O(n^2)`, `S=~O(n^(2-2epsilon/3))`, and
  `Q=~O(n^(1.5+epsilon))` for `0<=epsilon<=1/2`, with high probability
  against an oblivious adversary
  [primary v1](https://arxiv.org/abs/2602.11363v1).

### DG target-only encodings

Take the two pair lists as the two length-`n=B^2` indexed lists. For one target
`R-a`, DG gives

```text
P = B^4,       S = B^(5-2delta),       T = B^(2delta).
```

The single-target cap `T<=B^1.25` forces `delta<=5/8`, so even before the fifth
list `S>=B^3.75`. Querying all `B` fifth-deck shifts costs
`B^(1+2delta)`; the full cap then forces `delta<=1/8` and
`S>=B^4.75`. DG is target-only: it does not accept the dyadic pair subsets.
Rebuilding advice for restrictions does not repair the `B^4` preprocessing.

The asymmetric collapse uses `n=B^2` for `D12` and `m=B^3` for
`D34+I5`. It gives

```text
S = B^(6-2delta),       T = B^(2delta).
```

Under the query cap, `S>=B^4.75`. The construction charges `~O(nm)=B^5`
preprocessing, and materializing the second list alone costs `B^3`.

DG `k=5`, `delta=1` is an important four-summand control:

```text
P=B^4,       S=B^3.5,       T=B.
```

It already fails before the fifth list. A full five-summand instance is `k=6`,
whose best `delta=1` control has `P=B^5`, `S=B^4.5`, `T=B`. Neither form
natively enforces one occurrence from each labelled source.

All DG transplants also need an exact additive integer representation of the
point relation. Coordinate serialization is not such a representation, and the
known-scalar mutation above is circular on fresh `R`.

### Dyadic preprocessed universes

For `A=D12`, `B=D34`, and `C'_R={R-a:a in I5}`, the universe size is
`n=B^2`. This is the natural subset-query encoding, but it charges:

| Control | Preprocessing | Retained space | Query |
|---|---:|---:|---:|
| KPS unknown `C` | `B^4` | `B^4` | `~B^3` |
| KPS known `C` | `B^4` | `~B^3` | `~B^3` |
| KKMVW | `B^4` | `B^(4-4epsilon/3)` | `B^(3+2epsilon)` |

Known `C` is unavailable because `R` is fresh. KKMVW's minimum space exponent
is `10/3` and its minimum query exponent is `3`. Padding a collapsed
pair-plus-fifth universe to `n=B^3` worsens preprocessing to `B^6`.

These structures are for integer addition. Their modular false-positive
correction is exact because integer reduction has an explicit carry relation;
it does not repair a nonadditive point-coordinate hash. Duplicate pair
endpoints also need an occurrence-aware source-label wrapper before arbitrary
dyadic restrictions can be replayed.

## 4. Algebraic route gates

The following table gives the required type information. All `B` exponents
suppress polylogarithmic factors.

| Route | Coefficient ring and represented dimension | Target polynomial and exact zero test | Dyadic update and source | `P/S/Q/W` | Gate |
|---|---|---|---|---|---|
| Shifted pair-divisor resultants | `F_p[U]` on the additive-line control; on `E`, complete affine/projective section rings with saturated denominators. Pair degrees are `B^2`. | For each `a`, test `Res_U(H12(U),H34(R-a-U))=0`. Packed `J_R(A)=Res_U(H12(U),H34(R-A-U))` can expose `B^4` coefficients. | Select canonical pair-node products; bisect the same test and verify labels. | `B^2/B^2/B^3/(B^2..B^3)`; dense packed form `B^4`. | Outside query. |
| Pair-plus-fifth norm | `A345=Map(D34 x I5,F_p)`, dimension `B^3`. | `d_R(v,a)=h12(R-v-a)` and `Norm(d_R)=0`, with complete equality sections on `E`. | Restrict product components; split a zero component, replay `D12`, verify. | `B^2/B^2/B^3/B^3`. | Outside query. |
| Target-polynomial quotient norm | `A5=F_p[T]/g_I5(T)=Map(I5,F_p)`, dimension `B`; degree-`B^2` pair polynomials over it have `B^3` coordinates. | `g_I5(T)=product_a(T-t_a)` for distinct public occurrence labels. Interpolate the complete point `Q_R(T)=R-a(T)`. Compute pair resultant `r_R(T)` and test `Norm_A5(r_R)=0`. | Fifth subproduct factors and pair-node products are selected; split a zero factor, then pair-bisect and verify. | `B^2/B^2/B^3/(<=B^3)`. | Packing changes syntax, not traffic. |
| Dynamic splitting | `A5` or `A345`; total component degree remains `B` or `B^3`. | Recurse on `gcd(r_R,g_I5)` or another zero divisor. | Restrictions select factors; a terminal factor identifies `a`, then pair replay. | `B^2/B^2/B^3/(B..B^3)` in the standard worst case. | Early split is only an input-dependent exception. |
| Product-circuit zero test | Complete section rings on `E` tensored with `A5`. The compact circuit references pair product trees and `B` translated gates; coefficient expansion is `B^3`. | Test whether `H12` has a common zero with the unexpanded product of translated `H34(R-a-U)` gates, across all saturated charts. | Accept canonical nodes directly; return a zero child or support exact `O(log B)` bisection and verification. | Required `<=B^2.25/B^2.25/B^1.25/B^1.25`; known dense/KU/resultant realizations are `B^3`. | Conditional primitive remains open. |

Using `g_R(Z)=product_a(Z-ell(R-a))` instead of the label polynomial is exact
only if `ell` separates every selected signed target point. Coordinate or sign
collisions must be split back into the occurrence-label algebra, restoring
dimension `B`. This is why a target polynomial does not provide a scalar small
quotient for free.

## 5. Other required route tests

**Nonhomomorphic coordinate hashes.** `x`, `y`, compressed encodings, and bytes
modulo `m` do not satisfy `h(A+B)=h(A)+h(B)`. The immediate collision
`x(Q)=x(-Q)` also loses the supplied sign. Hash-and-verify removes false
positives only after candidate enumeration; a worst-case bucket can restore the
`B^3` target-shift traffic. Perfect hashing of stored endpoints does not make
translation hash-compatible.

**Exact characters/Fourier.** Abstractly,

```text
C_R = (1/N) sum_t chi_t(-R) product_i(sum_{A in I_i} chi_t(A)).
```

Every nontrivial character of prime-order `G` has image order `N`. Exact full
inversion therefore has `N=B^5` modes, and evaluating `chi_t(Q)` on an
unoriented point requires its scalar or another unavailable computable
character. A strict subset of character evaluations has a linear kernel and
cannot determine an arbitrary group-algebra coefficient without a promise.
Low-Fourier-support special decks remain outside this failure statement.

**FFE masks.** Fermat equality masks over `F_p`, combined with both coordinates
and explicit infinity/chart flags, give an exact constant-size equality leaf.
They do not contract the `B^3` pair-pair-fifth evaluations. Their compact leaf
generator is included in the surviving product-circuit question.

**Semaev/field-equation encodings.** Semaev's `f_m` is an x-coordinate
existence equation: it accepts some compatible y/sign choices, not necessarily
the supplied signed labels
[primary definition](https://eprint.iacr.org/2004/031). Adding y/sign equations,
field equations, saturation, and all projective charts restores an exact leaf
but not a sub-`B^3` contraction. No bounded-degree solver, source reporter,
rank proof, or charged Weil-descent realization was constructed.

## 6. Surviving conditional construction

Define **PCZT-E**, the exact source-reporting elliptic product-circuit zero test.
Preprocessing receives the five signed labelled decks and their dyadic product
trees, but not `R`. Online it receives `R` and the five restrictions. In
complete coordinate-section rings, it must test whether `H12` shares a zero
with the compact translated product

```text
K_R(U) = product_{a in I5} H34(R-a-U),
```

where the notation denotes complete elliptic translation with all denominators,
infinity cases, and occurrence-label components retained. It must not expand
the `B^3` split coordinates.

**Conditional reduction.** If PCZT-E has setup/state `B^(9/4+o(1))`, total
online time/workspace `B^(5/4+o(1))`, exact correctness, and either returns a
zero child or supports `O(log B)` charged bisection, then it implements
Query2P1: a common zero is exactly a selected `u,v,a` with `u+v+a=R`; replay
recovers the five source labels; direct group addition verifies the output.

This is an operation-level reduction, not an algorithm. The audited dense,
standard resultant/gcd, KU, triangular, power-projection, and explicit split
norm realizations all materialize `B^3` traffic. The open kernel is a
random-access exact zero/witness operation on the compact translated circuit.

## 7. Conditional generic-DLP control

Maurer-Portmann-Zhu Section 5 proves, in its preprocessing generic-group
extraction model, success at most approximately
`advice_bits*(k_main+1)^2/N`, and supplies a matching `N^(1/3)` advice and
`N^(1/3)` online upper control up to logarithmic factors
[primary ePrint](https://eprint.iacr.org/2020/996).

At the frozen rectangle,

```text
k_main^2 * advice_bits
  = B^(2*(5/4)+9/4)
  = B^(19/4)
  = B^4.75
  < N=B^5.
```

Therefore a **complete generic DLP extraction reduction** with constant success
at these resources would violate that model's lower bound. This is conditional
on having such a complete reduction. Query2P1 alone is not DLP extraction, and
coordinates are non-generic information, so MPZ is not a Query2P1 or coordinate
lower bound. It sharpens the positive escape condition: a complete path must be
representation-sensitive or leave the MPZ hypotheses.

## 8. Terminal gate

| Completion item | Result |
|---|---|
| Constructed exact Query2P1 in the rectangle | **No** |
| Sharp conditional operation reduction | **Yes: PCZT-E** |
| Named concrete routes exhausted as requested | **Yes, scoped as above** |
| All-strata proof | **No** |
| Relation density/rank | **Not established** |
| Factor logs and identical scalar-blind descent | **Not produced** |
| Complete `lambda,mu<=0.45` path | **No** |
| Experiment or shared-state action | **None** |

Exactly one next action: seek or rule out PCZT-E in the compact-circuit access
model, and require an independently reviewed theorem specifying exact gates,
all charts, source replay, and frozen accounting before any experiment.

## 9. Local input bindings

SHA-256 was computed over the bytes read locally. The exact task object was
also canonicalized with `jq -S -c` and hashes to
`2d3aa21aae23dda6684ba14511ae1acea2c1fe341b2103c87c6bed5ae8001578`.

| Local input | SHA-256 |
|---|---|
| `AGENTS.md` | `4b9810aaa2c96a9e8d7db097d6abfc8cbeb24038df3a09e98f0beb4c23a6d362` |
| `coordination/dispatch_queue.json` | `3b13680e03d831e644a820aaafff19a75d69f326e184bea74f8b97eadd461110` |
| `ideas/artifacts/ECDLP-IDEA-012/p1553_finite_deck_weighted_endpoint_gate_r2.md` | `55acc1457e7fd5a740da57c2c1db957374c7c18561c67b1748176dc8c61fcda5` |
| `coordination/tasks/TASK-20260718-P1553-FD-REPORTER-P1/finite_deck_reporter_spec.md` | `fd12ff17055a108ef31e58b2fb813feb1b8dc8eb2950db127a7a623e69a4d77f` |
| `coordination/tasks/TASK-20260718-P1553-TENSOR-RT-R1/red_team_report.yaml` | `0a48143e4b5a25fad52200abf7d43f7094ef18af6df0348ea9aa987ecd15002d` |
| `coordination/tasks/TASK-20260718-P1553-TENSOR-RT-R1/tensor_rank_notes.md` | `c3df381e726745ee3b8b09ceb9273201b22b62ed2d0776c556d63908b30bfbdc` |
| `ideas/artifacts/ECDLP-IDEA-121/translated_product_common_norm_v3_audit_v2.md` | `407e3c7da6345f156f7c6bcaa75749e16b6184735d32be4b6e4aca69427763d5` |
| `ideas/artifacts/ECDLP-IDEA-121/ku_circuit_reduction_v2.md` | `6fcca1d12e911f6eb2142ac96b6d0a83b6ac20db11efd06bc24c0abb7c99dc48` |
| `ideas/artifacts/ECDLP-IDEA-165/pair_sum_quotient_theorem.md` | `18cebc9c209c6ba0d705e43da7f921885e60d3436b201375e306e14f4ae0bdb2` |
| `ideas/rejected/ECDLP-IDEA-138_sumcheck_source_self_reduction_hypothesis.md` | `e99daa8a7993266ae86dd9574d122d0b00e9cd897c5673937c6bb8534192af13` |
| `ideas/rejected/ECDLP-IDEA-156_combinatorial_nullstellensatz_source_self_reduction_hypothesis.md` | `228c2d55df137225c92f2a14afca188d09bc8917ced63b6c4d4ac2027accda39` |
| `ideas/rejected/ECDLP-IDEA-199_ranked_subset_convolution_source_unranking_hypothesis.md` | `ab36b80667d444a6be41439b89e8c133f2ef3e8fdeef0babb8408cccea84399e` |
| `ideas/rejected/ECDLP-IDEA-266_equiprojectable_dynamic_evaluation_source_tree_hypothesis.md` | `a9529076339b09b881d4504de45c132219352d4e0edc282cc0d2d955577ea1b1` |
| `ledger/FINDING-PF-IC-001.md` | `3776db92945bcb673a41aca3603b0fa3a516f9f3dd8a71b3efbc11d795a1d633` |
| `focus/current_plan.json` | `21dd1a00bc71f2e5987dd4709bf57f1e054c7c51913fb8027a9628da120f4f25` |
