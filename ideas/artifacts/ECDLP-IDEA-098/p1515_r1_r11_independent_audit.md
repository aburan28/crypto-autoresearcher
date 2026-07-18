# P1515 R1-R11 independent static audit

Handoff: `TASK-20260718-P1515-R11-AUDIT`

Status:
`INDEPENDENT_SCOPED_AUDIT_PASS__DEFERRED_NO_CANDIDATE_OPERATION`

Decision:
`deferred_no_candidate_operation`

This is an independent theorem and semantic audit of the P1515 R1-R11
producer chain. No contract, solver, parameter sweep, elliptic fixture,
relation campaign, or experiment was run. The producer receipts, queue,
ledger, indexes, contracts, and validators were not edited. One exact symbolic
reconstruction over `Q(c)` was used to check R10's polynomial certificate; it
was not a finite-field or scaling experiment.

The decision is scoped. It says that the bound inputs contain no explicit
generic-prime operation that survives all removal, source, yield, rank, and
cost gates. It is not a lower bound against all arithmetic circuits, data
structures, extension-field transfers, covers, or nonlinear source routers.
It does not establish a below-rho ECDLP algorithm or a Shoup-bound improvement.

## Frozen audit interface

Let

```text
G=<P>, |G|=N prime, B=N^(1/5), m=5.
```

The factor alphabet is target-independent and has `Theta(B)` signed points.
For a known scalar `r`, an accepted relation must report a complete coefficient
row `c_r` and verify

```text
sum_i c_r[i] F_i = [r]P.
```

For blind descent, the unchanged router must report a complete row for
`Q+[t]P`, after which the factor logs and public mask `t` recover a candidate
for `log_P(Q)`. Chord, tangent, vertical, infinity, repeated, sign-fixed, and
nonreduced strata are part of the source inverse. An x-coordinate, endpoint,
count, aggregate certificate, geometric preimage, or relation without its
signed source row is not accepted.

At this balance, a one-row-per-target API has the necessary rectangle

```text
setup <= B^(2.25+o(1)),
query <= B^(1.25+o(1)),
complete time and peak memory <= N^(0.45+o(1)).
```

These are necessary gates, not sufficient evidence of an algorithm.

## Input and receipt hash binding

The audit used the following current bytes. All eleven receipt hashes match
both the producer ledger entries and the artifact index.

| Binding | SHA-256 |
|---|---|
| `AGENTS.md` | `3f3f2797ee98eeb07754780dd3e8b30c2f221937a87504b99c4359f35d7cbc6c` |
| `focus/focus_queue_20260717.json` | `5a1d64832ece7395545226686958f3e82ee7af0c1d7829753f66efbacd6d9d95` |
| `ledger/FINDING-PF-IC-001.md` | `8991bb62a5f034cdd9575ae3fece4af4a4f1a9469d0c2353eeb27e3dbc601545` |
| R1 `squarefree_source_gate.md` | `51ad15480c7740cc9f340684bbb98d3701dc033593569949a9536b2e5e6caead` |
| R2 `compressed_navigator_gate_v1.md` | `dadcadf45bdea910f0a12e904bdfe32c4a517b0756ef08148de75fb39929e3e5` |
| R3 `recursive_s3_grammar_spec_v1.yaml` | `884854c2928ce5baecf56f415653cb6bf436d5062309cbbcff3e60bcd0d49bc7` |
| R4 `recursive_s3_local_separator_trichotomy_v1.md` | `dec667b097bcaefdf4c54091b2a9fa7757db5a65efe5b36e6ac15a6ff11a435a` |
| R5 `recursive_s3_field_router_candidate_v1.md` | `ee7c0ef479f33d3a82ab6827c286460604c6d26c9a76aa551305eccc2a337e24` |
| R6 `prime_order_composable_bucket_theorem.md` | `524a59c1728bcbea804ac4be42ace5a965b68a6332e85d941829b89e04fc4225` |
| R7 `kummer_trace_norm_correction_gate.md` | `81a025925063937f4a496e0f6b0618b32525b1c176627449bdbd8eb96dd2f947` |
| R8 `exact_spectral_rank_density_gate.md` | `e572713a3910ef6a3e31ac360123aa8b5135c75d4210cbfb579e6831e9746fca` |
| R9 `ecfft_auxiliary_isogeny_router_gate.md` | `f8abb802b5052f614a6500c722083d3ebbd45d6e54353686ff3283ffa27a88b7` |
| R10 `ecfft_list_restricted_branch_locus_gate.md` | `e4972a1c6f4fb796a9efa556c745c4d4d5e4b00e5637e9fca9f3828abb4db120` |
| R11 `ecfft_lattes_rational_kernel_cofactor_gate.md` | `342e872f1e86297d88bb8684155ed84cf7c3b37351402fba4c296ff986ab141e` |

The following authoritative overlap was also hash-checked:

| Overlap binding | SHA-256 |
|---|---|
| P1501 producer JSON | `97949bb077a932d777dd10e25f11050a2e326060e5112f45868f6080473978c3` |
| P1501 independent audit JSON | `b0b912521ff0b4568c3214fdd482ef22a1a19015f38f10302d1b66daca5cb61c` |
| `ECDLP-IDEA-009_nonequivariant_trace_zero_transfer_hypothesis.md` | `7fabf5c4fa94353908eb4e1dbf61dfab9b768ce28f8f391b25e69ff994f8e240` |
| `ECDLP-IDEA-010_torsor_deck_orbit_descent_hypothesis.md` | `315f2b6e62df24fa300cec72190fc2bc1c3e42f4aea074ef78eac7c461745c56` |

The P1501 audit reports all 12 checks passed and binds focus candidate P1501,
whose current state is `completed_negative` and `independently_verified=true`.
This audit consumes that result only in its frozen ordinary algebraic-transfer
scope.

## R1-R11 disposition

| Gate | Independent reconstruction | Scope-correct disposition |
|---|---|---|
| R1 universal facets | `|D_m|=Theta(B^m)`, `sum_R d_R=|D_m|`, and constant-success rank `B` needs `Omega(N/B^(m-1))` random known targets. Exposing the universal source deck costs `Omega(B^m+N/B^(m-1))`, minimized at `m/(2m-1)>1/2`. | `accept_scoped_negative`. This closes explicit universal facets, shellings, and equivalent source dictionaries. A target-local implicit navigator remains open because a fixed fiber has degree `d_R`, not `B^m`. |
| R2 compressed controls | At `m=5`, explicit `2+3` orientations cost `B^4` or `B^3` over `B` queries; offline six-list MITM has `B^3` states. Dinur-Golovnev v2 gives five-source `kSUM` setup at least `B^4.5` in its stated range and asymmetric setup at least `B^4.75` when `q<=1.25`. | `accept_control_only`. These are known upper-bound constructions, not a data-structure lower bound or an elliptic transfer. |
| R3 serial grammar | The declared exact-parent grammar has `Theta(B^3)` `PREFIX3` derivations. Hashing endpoints does not preserve a biconditional source inverse without parent lists or a new unranking operation. | `accept_scoped_negative`. This closes only the frozen serial provenance representation, not arbitrary shared grammars or nonlocal term orders. |
| R4 local operators | Explicit provenance reaches `B^3`; the declared endpoint scan costs `B^2` per target; checked indexes miss the rectangle; named norm/resultant and dense aggregates route to P1513/P1514/R1. | `accept_scoped_negative`. The four-operator list is not exhaustive for arbitrary arithmetic circuits. A new indexed or factored source-unranking primitive must be explicit before it is a candidate. |
| R5 sparse factor map | `Res_X(X^d-c,S3(U,V,X))` is a valid compact one-transition norm in a quadratic algebra. It requires a suitable divisor of `p-1`, is x-only, duplicates PKM16, and supplies no costed five-transition source router. | `reject_candidate_operation`. Compact membership is not composed target-to-source path finding; composition returns to explicit states, P1513 norms, or P1514 dense solving. |
| R6 composable labels | Equality under an exact globally composable label is a group congruence. Its fibers are cosets of a subgroup; prime order makes the label constant or injective. | `accept_scoped_negative`. This removes exact global quotient chains, not list-specific nonhomomorphic or support-changing corrections. |
| R7 Kummer trace/norm | The two roots of `S3(u,v,Z)` are the Kummer pseudo-sums. Their trace and norm are its monic coefficients, and deck aggregation is exactly a resultant/product over the source leaves. | `accept_semantic_removal`. Raw pairwise trace/norm is the existing S3 norm backend. It supplies neither support enrichment nor a source-complete composed router. |
| R8 linear spectral factor | Target-versus-source flattening has one standard basis column per endpoint, hence exact rank `|mF|`. Explicit retained components plus one-witness target attempts cost at least `max(S,B*N/S)>=sqrt(B*N)=N^0.6`. | `accept_scoped_negative`. This closes exact separated linear one-witness factors only. Nonlinear transposed batches and multirow reporters remain outside the theorem. |
| R9 auxiliary ECFFT | A low-degree isogeny is injective on `G`; an unrelated ECFFT tree has no supplied target-addition law. The canonical transformed-trace difference is nonzero. A certified set of size `O(sqrt(N))` has model-bound pair occupancy `O(N^(-1/10))`. | `accept_scoped_negative`. ECFFT is a polynomial-arithmetic backend, not a target router. Other maps and proved list-specific intertwiners remain open; the occupancy statement remains model-bound. |
| R10 restricted canonical support | Exact reconstruction over `Q(c)[X,Y]` gives `gcd(D_T,D_N)=(X-1)(X+1)`. At `c=0`, both residuals have bidegree `(6,7)`, coprime contents, and the stated nonzero degree-84 resultant. | `accept_scoped_negative`. The only common curve component is deck-fixed; the nonfixed residue is bounded on the frozen target/map. Other targets, maps, exceptional parameters, and non-Cartesian supports remain open. |
| R11 same-field kernel | The rational-kernel cofactor conclusion and rank conclusion are correct after the proof wording correction below. Same-field rational branching is `N^o(1)` and supplies no extra target-log columns. | `accept_scoped_negative_with_correction`. Extension-field, unrelated-auxiliary, cover-geometric, non-Cartesian, and nonlinear batch mechanisms remain outside scope. |

The R10 resultant factorization was independently reconstructed exactly, not
inferred from a finite sample. The R2 tradeoff was checked against the current
primary preprint, and R9's use of ECFFT was checked against the ECFFT Part I
scope. These checks do not turn neighboring upper bounds into lower bounds.

## Explicit R11 proof-wording correction

R11's conclusion `K_rat|h` is accepted, but it should not rest on the bare
sentence that `H_rat intersect G={O}` implies `gcd(K_rat,N)=1`. The direct group
proof is:

```text
|H_rat+G|
  = |H_rat|*|G|/|H_rat intersect G|
  = K_rat*N.
```

Because `H_rat+G` is a subgroup of `E(F_p)` and
`#E(F_p)=h*N`, Lagrange gives

```text
K_rat*N divides h*N,
therefore K_rat divides h.
```

This proves the desired subpolynomial rational-kernel bound without an
unstated Sylow or coprimality step.

There is also a source-log wording correction. If `Y=Phi(g)` for `g in G`, the
rational fiber is `g+H_rat`. If `g+h` is also in `G`, then
`h in H_rat intersect G`, so `h=O`. Thus exactly one rational preimage of `Y`
lies in `G`. The other rational lifts lie outside the target subgroup and have
no logarithm to base `P`; nonrational geometric lifts live over extension
fields and likewise have no `F_p` target-subgroup log. After transport all
lifts still collapse to the one image factor column `Y`, so they provide no
independent column or row rank. They should be described as unverifiable lift
labels for the target-log system, not as multiple logged source factors.

This correction narrows wording only. It does not weaken R11's scoped negative
or close any extension-field or cover-geometric mechanism.

## Signed source, rational-yield, and rank gate

Any claimed survivor must define a public map from its internal outputs to a
matrix over `F_N`:

```text
internal branch
  -> exact five signed points in E(F_p)
  -> factor-point image columns
  -> coefficient row c in F_N^B
  -> verified known right-hand side r.
```

For an extension-field or cover output, let:

```text
Y_geom = number of geometric branches,
Y_rat  = number yielding exact E(F_p) signed-source rows,
C      = the relation matrix after factor-image column aggregation,
r_img  = rank_F_N(C).
```

Only `Y_rat` and `r_img` receive credit. Frobenius conjugates, nonrational
kernel points, deck labels, distinct lifts with one image, repeated source
rows, and auxiliary atoms without target-subgroup logs contribute zero rank.
The base-log phase needs at least `B` usable image columns and `r_img=B` after
all aggregation and duplicate removal. A transfer with an auxiliary log system
must also provide a public full-rank conversion to the target factor logs; an
oracle conversion or source DLP is forbidden.

Every failed rationality test, exceptional chart, ambiguous sign, fiber branch,
source split, coefficient conversion, relation verification, and emitted row is
charged. The identical public inverse is required for masked target descent.

## Full cost gate

For a target-at-a-time candidate, write setup time/state as `B^s_t,B^s_m`,
query time/state as `B^q_t,B^q_m`, conditional independent image-rank yield as
`B^y`, and success probability as `B^(-d)`. The expected independent rank gain
per query is at most `B^(y-d)`, so collecting rank `B` has the favorable query
work floor

```text
B^(1-y+d+q_t).
```

The one-witness case is `y=d=0`, recovering `q_t<=1.25`. A multirow claim may
raise `y`, but it must emit and verify the rows and prove their post-aggregation
rank; geometric or duplicate multiplicity cannot raise `y`.

Let `d_Q` be the reciprocal-success exponent for blind masked descent,
`q_Q` its attempt-cost exponent, and `o_Q` its candidate-output exponent, all
in base `B`. Let `lambda_map,mu_map` include extension construction, field
arithmetic, cover equations, branch handling, rational descent, and target-log
conversion in base-`N` exponents. Even under the favorable sparse factor-log
allowance, a complete candidate must prove

```text
lambda = max(
  s_t/5,
  (1-y+d+q_t)/5,
  2/5,
  (d_Q+q_Q)/5,
  o_Q/5,
  lambda_map,
  lambda_verify
) <= 0.45,

mu = max(
  s_m/5,
  q_m/5,
  mu_factor_log,
  mu_map,
  mu_output,
  1/5
) <= 0.45.
```

If the operation processes a succinct target batch rather than individual
queries, it must replace the query term by an explicit batch recurrence and
prove total relation-stage work at most `N^(0.45+o(1))`, total independent
post-aggregation rank at least `B`, and peak state at most
`N^(0.45+o(1))`. Materializing the targets, exact linear modes, source deck,
geometric fibers, or output rows is charged. Dense or less favorable linear
algebra replaces the optimistic `2/5` term by its actual exponent.

Target-independent setup must be frozen before both known-scalar targets and
`Q`. Separate masked descent, factor-log verification, final scalar
verification, coefficient traffic, and bit complexity over `F_(p^k)` are not
absorbed into field-operation notation.

## Surviving class A: extension-field or unrelated auxiliary intertwiner

No explicit operation in the bound inputs passes this class.

R9 writes an example of the kind of identity required,

```text
Res_Z(S3_E(X,Y,Z),T-psi(Z))
  = c(X,Y) H(psi(X),psi(Y),T),
```

but supplies no `psi,H` on an admitted generic-prime support, no bounded branch
recurrence, and no signed source inverse. R11 names extension-field kernels as
an exception but supplies no descent from geometric branches to rational
factor points, no rational-yield theorem, and no independent image-column rank.
ECFFT's fast polynomial operations do not fill any of those missing fields.

The authoritative P1501 overlap removes a tempting rename. Ordinary algebraic
or Frobenius-equivariant trace-zero transfers in P1501's frozen catalog are
already `completed_negative` and independently verified. The remaining
extension/cover descriptions route as follows:

| Proposed mechanism | Existing route |
|---|---|
| Ordinary algebraic/equivariant trace-zero transfer | P1501 scoped completed negative; do not reopen as P1515. |
| Explicit public nonalgebraic or Frobenius-nonequivariant scalar-compatible evaluator together with a decomposition-changing image locus | `ECDLP-IDEA-009`; neither indispensable operation is currently supplied. |
| Nontrivial cover/torsor geometry with target-compatible deck-orbit compression and projected rank beyond raw deck multiplicity | `ECDLP-IDEA-010`; raw branch count or kernel multiplicity is a control. |
| Same-field target isogeny or Lattes kernel multiplicity | R9/R11 scoped negative. |
| List-specific nonhomomorphic `S3` support-changing correction not using the transfer or cover mechanisms above | Existing `ECDLP-IDEA-057` residual, with no explicit operation in this audit. |

None of these routes supplies an operation here with source inversion, rational
yield, independent columns, setup/query recurrence, factor logs, and target
descent. The class is mathematically open only in the residual scopes already
owned by P1501/IDEA-009/IDEA-010/IDEA-057; it is not a P1515 survivor to rename.

## Surviving class B: nonlinear implicit batch or multirow router

No explicit operation in the bound inputs passes this class.

R8 correctly leaves nonlinear transposed target batches and multirow reporters
outside its linear one-witness rank theorem. That logical exception is not an
algorithm. No receipt supplies:

1. a succinct target-batch representation with a target-independent build;
2. a nonlinear recurrence mapping that batch to exact signed source rows;
3. a proof of rational output and all-strata source replay;
4. relation rank after duplicate source and image-column aggregation;
5. a separate masked-target invocation; or
6. complete time, output, and memory exponents in the gate above.

The squarefree accepted-facet navigator, nonlocal source unranking, implicit
common-root circuit, and multirow spectral consumer are all names for missing
operations. Using any of them as an oracle would assume the P1515 objective.
Explicit facets fail R1, checked indexes fail R2, serial provenance fails R3,
named local operators route under R4, sparse membership fails R5, exact labels
fail R6, trace/norm routes under R7, exact linear modes fail R8, and an ECFFT
backend without a new recurrence fails R9-R11.

The residual open class is therefore an explicit generic-prime,
target-independent, non-Cartesian support-changing arithmetic operation that
maps a succinct target batch to independently ranked exact source rows without
materializing the removed objects. No such recurrence is present in the audit
inputs.

## Exact decision

```text
R1-R11 receipt reconstruction: pass in stated scopes
R11 producer wording: corrected in this audit only
extension/unrelated-auxiliary class: no candidate operation
nonlinear implicit-batch/multirow class: no candidate operation
P1515 contract authorization: no
solver or fixture authorization: no
scoped decision: deferred_no_candidate_operation
official hypothesis state change: none; coordinator-owned
breakthrough: none
```

This decision preserves the open residual classes and their existing ownership.
It does not prove that such operations cannot exist. It records that no explicit
operation in the R1-R11 chain can presently be source-inverted, ranked, and
costed through the full generic-prime factor-base-to-target-descent path.

## Exactly one next action

1. Execute one coordinator disposition transaction that hash-binds this audit, records the P1515 recommendation `deferred_no_candidate_operation`, and reranks outside the squarefree-shelling/ECFFT-kernel grammar without authorizing a contract.

## Primary references checked

- Dinur and Golovnev, *Improved Time-Space Tradeoffs for 3SUM-Indexing*, v2:
  <https://arxiv.org/abs/2512.04258>.
- Ben-Sasson, Carmon, Kopparty, and Levit, *Elliptic Curve Fast Fourier
  Transform (ECFFT) Part I*:
  <https://arxiv.org/abs/2107.08473>.
- Semaev, *Summation polynomials and the discrete logarithm problem on
  elliptic curves*: <https://eprint.iacr.org/2004/031>.
- Shoup, *Lower bounds for discrete logarithms and related problems*:
  <https://www.shoup.net/papers/dlbounds1.pdf>.

These sources provide neighboring constructions and the generic comparison
boundary. None supplies the missing P1515 source router or an end-to-end
generic-prime below-rho ECDLP algorithm.
