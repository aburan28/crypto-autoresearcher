# P1549 non-Cartesian finite-state closure theorem gate

## Status and claim boundary

- Record type: independent theorem-only gate
- Root hypothesis: `ECDLP-IDEA-195`
- Candidate: `P1549`
- Claim: `CLM-P1549-NONCARTESIAN-SEVEN-CHANNEL-CLOSURE`
- Evidence scale: exact square-zero algebra, layered-grammar counting,
  target-yield, and asymptotic cost statements; named representation controls;
  no experiment
- Contract state: the IDEA-195 contract remains retired, `review_required`,
  unapproved, and zero-run
- Claim labels: `heuristic`, `model-bound`, `novelty-unverified`
- Breakthrough claim: none
- Disposition:
  `INDEPENDENTLY_VERIFIED_SCOPED_NO_CANDIDATE__SEVEN_CHANNEL_VALUE_ALGEBRA_EXACT__SHARED_LAYER_PATH_MASS_AT_MOST_BD4__EXPLICIT_D4_PATH_EXPANSION_CONSERVES_B5_WORK__GLOBAL_EDGE_SCAN_MISSES_THE_RECTANGLE__AN_O_D_TARGET_LOCATOR_REQUIRES_GAMMA_AT_LEAST_11_OVER_12__DEGREE_B_IS_NOT_ALONE_FATAL__SIMULTANEOUS_TRACE_NORM_CLOSURE_AND_EXACT_PATH_INVERSE_UNSUPPLIED__INCONCLUSIVE`

The seven-channel value algebra is already exact. It preserves the constant
coefficient, the derivative with respect to the constant marker, and the five
source-coordinate derivatives under arbitrary regrouping. On a unique simple
zero, the five derivative ratios recover the five leaf x-coordinates.

That algebra is not a domain compressor. This audit freezes the most favorable
shared-state non-Cartesian path grammar that could make it one: five `O(B)`
state layers, four source-labelled correspondences of outdegree
`D=B^gamma`, and only `O(BD)` explicit edge state. Such a grammar supports at
most `O(BD^4)` exact five-source paths. This creates a sharp density/navigation
tradeoff.

If a target query explicitly expands the four correspondence levels, even
granting the first root for free, its `D^4` work cancels the support-density
gain and relation collection costs `B^5=N`. Scanning all `BD` stored edges per
target also misses the frozen rectangle. A genuinely new target-conditioned
locator with query cost `O(D)` would be different: it can meet the complete
relation gate only in the narrow range

```text
11/12 <= gamma <= 1.
```

At the lower endpoint, setup/state is `B^(23/12)`, one attempted query is
`B^(11/12)`, relation collection is `B^(9/4)=N^0.45`, and blind descent is
`B^(5/4)=N^0.25`, before lower-order and sparse-linear-algebra charges. At
`gamma=1`, the corresponding optimistic exponents are `B^2`, `B`, `B^2`, and
`B`.

This is a necessary conditional window, not a construction. No audited
artifact supplies the required `O(D)` target-to-path locator, simultaneous
trace/norm closure on its support, generic-prime construction, or exact signed
all-strata inverse. P1549 is therefore terminal inconclusive within its exact
grammar and control scope. There is no sub-rho ECDLP algorithm, Shoup-bound
improvement, or breakthrough.

## Hash-bound inputs

- `ideas/deferred/ECDLP-IDEA-195_noncartesian_s3_intertwiner_source_router_hypothesis.md`:
  `b52403859590a549f621fce1d2d71ab2e4da2d90faacbf9c0d3d48fcdb2bc513`
- `ideas/artifacts/ECDLP-IDEA-195/p1537_jet_preserving_compositional_intertwiner_audit.md`:
  `5b0112a1efc6043150d998fb1c38217c602a00186f7982443aaab7a443acf249`
- `ideas/artifacts/ECDLP-IDEA-102/p1538_bounded_state_local_norm_closure_audit.md`:
  `2a25ed9ed8eef5518229752a5c439c515255eb810bc01f99e7f0987531b52174`
- `ideas/reviews/REDTEAM-20260718T044328-0700.md`:
  `8c92774c682e69c969a31970a1bcbb6a1e6d971cacbad4bb98d1cad91ec373d4`
- `ideas/artifacts/ECDLP-IDEA-010/p1548_torsor_deck_orbit_router_gate.md`:
  `ea22392aeebf6f436a3ed19f9126f4c618c3327437c06f25a263439208e38742`
- `ideas/artifacts/ECDLP-IDEA-098/p1515_r1_r11_independent_audit.md`:
  `7e7609716f87b1b4df5ffc77406a912ad0303cc309ec1b84be42ebcc0d09539e`
- `ideas/artifacts/ECDLP-IDEA-098/recursive_s3_field_router_candidate_v1.md`:
  `ee7c0ef479f33d3a82ab6827c286460604c6d26c9a76aa551305eccc2a337e24`
- `ideas/artifacts/ECDLP-IDEA-098/compressed_navigator_gate_v1.md`:
  `dadcadf45bdea910f0a12e904bdfe32c4a517b0756ef08148de75fb39929e3e5`
- `ideas/artifacts/ECDLP-IDEA-098/recursive_s3_grammar_spec_v1.yaml`:
  `884854c2928ce5baecf56f415653cb6bf436d5062309cbbcff3e60bcd0d49bc7`

P1515 and its recursive-S3 controls are consumed only in their frozen scopes.
The sparse factor-map identity is a valid compact one-transition membership
control; it is not a composed source router.

## Frozen seven-channel interface

Let `k=F_p`, let the five public coloured factor decks have size
`Theta(B)`, and put

```text
N=|<P>| prime,
B=N^(1/5),
A_i=k[T_i]/(f_i),
A=tensor_(i=1)^5 A_i.
```

For a public target chart `R`, set

```text
g_R=S_6(T_1,T_2,T_3,T_4,T_5,x_R).
```

Use the square-zero marker algebra

```text
D_7=k[e_0,e_1,...,e_5]/(e_a*e_b : 0<=a,b<=5)
```

and the marked norm

```text
J_R=Norm_(A/k)(g_R+e_0+sum_(i=1)^5 e_i*T_i)
   =c_R+e_0*j_(R,0)+sum_(i=1)^5 e_i*j_(R,i).
```

P1537 gives the exact simple-support branches:

```text
no source:          c_R != 0;
one source a*:      c_R=0, j_(R,0)!=0,
                    a_i*=j_(R,i)/j_(R,0);
two or more sources:c_R=j_(R,0)=...=j_(R,5)=0.
```

For child values `q_a=g_R(a)`, one local block has

```text
h_empty=product_a q_a,
h_0    =sum_a product_(b!=a) q_b,
h_i    =sum_a a_i*product_(b!=a) q_b.
```

Later seven-channel messages multiply by

```text
C   =product_a c_a,
D_j =sum_a d_(a,j)*product_(b!=a)c_b,  j=0,...,5.
```

These formulas prove value-space closure and exact singleton conditioning.
They do not construct the `B^5` leaf values or a compact function family for
them. A P1549 representation must aggregate many source paths before their
individual `q_a` values are formed.

## Frozen shared-layer path grammar

The smallest favorable non-Cartesian grammar audited here consists of:

```text
V_0,V_1,V_2,V_3,V_4,       |V_j|=O(B),
E_j subset V_(j-1) x A_(j+1) x V_j,  j=1,...,4,
maximum outdegree(E_j)<=D,
D=B^gamma,                 0<=gamma<=1.
```

Each `v_0` carries the first exact signed source. Each edge carries the next
exact signed source and a complete projective `S3` transition certificate.
A complete path therefore carries five sources and has a publicly verifiable
endpoint

```text
sigma(path)=a_1+...+a_5 in <P>.
```

The source replay is biconditional: every accepted path returns its complete
edge sequence, signs, repetitions, tangent or vertical branches, infinity
charts, and multiplicities. Merging state vertices is allowed only if a target
query can unrank the exact path; an aggregate endpoint without its path is not
a source row.

This grammar grants several optimistic assumptions.

1. Every layer has only `O(B)` shared states rather than `BD^j` provenance
   states.
2. All four edge layers can be represented in `O(BD)` words.
3. Edge certificates are constant-size and no dense polynomial coefficients,
   pair tables, roots, or source dictionaries are hidden in a state.
4. Every accepted path produces an independently useful row unless the mass
   bound itself says otherwise.

A construction that cannot meet these assumptions is more expensive than the
gate below.

## Path-mass and target-yield theorem

Let `M` be the number of complete source-labelled paths, counting separate
source records before endpoint collisions. The outdegree bound gives

```text
M <= |V_0|*D^4 = O(BD^4).                       (1)
```

Let `S` be the number of distinct subgroup endpoints represented by those
paths. Since every path has one endpoint,

```text
S <= M.                                         (2)
```

A uniformly sampled known scalar gives a uniform endpoint in `<P>`. Even if
every represented endpoint returns one fresh independent row for free, its
success probability is at most `M/N`. Collecting `B` rows therefore needs

```text
A_rel >= B*N/M >= N/D^4 = B^5/D^4.             (3)
```

The same argument counts all output rows rather than only endpoints: over `T`
uniform targets, expected total source-path output is `T*M/N`, so rank `B`
still requires (3) before dependencies and duplicate rows are charged.

One blind masked descent needs at least

```text
A_desc >= N/M >= B^4/D^4.                       (4)
```

Equations (1)-(4) are counting statements for this grammar. They are not a
lower bound against a grammar with a different arity, multirow algebraic
generator, or nonuniform target distribution with publicly known source logs.
Such a successor must state its replacement mass and rank theorem.

## Explicit navigation controls

### Four-level branch expansion

Grant a query its correct initial state for free. A depth-first navigator that
tests every allowed continuation still touches `Theta(D^4)` complete paths.
Multiplying this favorable query cost by (3) gives

```text
W_rel,explicit >= (B^5/D^4)*D^4 = B^5=N.       (5)
```

Blind descent analogously costs at least `B^4`. If root localization also
scans `B` roots, the result is worse. Thus explicit branch expansion exactly
conserves the path-mass gain; high branching alone is not compression.

### Whole-edge scan

A query that scans all stored edges pays `BD`. With `D=B^gamma`, equations
(3) and (4) give

```text
W_rel,scan  >= B^(5-4*gamma)*B^(1+gamma)
            = B^(6-3*gamma) >= B^3,

W_desc,scan >= B^(4-4*gamma)*B^(1+gamma)
            = B^(5-3*gamma) >= B^2.
```

The relation term misses `B^2.25` for every `0<=gamma<=1`. A shared adjacency
table is admissible setup, but traversing it per target is not the missing
navigator.

### Conditional compact locator

Let a genuinely target-conditioned locator cost

```text
Q=B^eta
```

per attempted target, including exact path unranking and source verification.
Under the optimistic `O(BD)` setup, the favorable exponents are

```text
setup/state:  1+gamma,
query:        eta,
relations:    5-4*gamma+eta,
blind descent:4-4*gamma+eta.                    (6)
```

The router and complete relation gates require

```text
1+gamma <= 9/4,
eta <= 5/4,
5-4*gamma+eta <= 9/4.                           (7)
```

The blind-descent bound is one `B` power weaker than the relation bound and is
automatic when the latter holds. Equation (7) is a conditional feasibility
region, not proof that any point in it is attainable.

For the strongest simple claim `Q=O(D)`, put `eta=gamma`. Then

```text
W_rel >= B^(5-3*gamma),
W_desc>= B^(4-3*gamma),
```

and (7) becomes

```text
11/12 <= gamma <= 1.                            (8)
```

Below `gamma=11/12`, relation density alone defeats an `O(D)` locator. Inside
(8), the exponents fit only because the locator is assumed to avoid the
`D^4` path tree and the `BD` global edge scan. Deriving that locator is the
remaining operation.

## Correction to the IDEA-195 degree boundary

IDEA-195 lists "map degree/table size grows at least B" as a possible fatal
disproof track. P1549 narrows that wording.

A degree `D=B` correspondence with `O(B)` states per layer has `O(B^2)` edge
state. If it also had a source-complete `O(B)` target locator, equations (6)
and (8) would give `B^2` setup, `B` query, `B^2` relation work, and `B` blind
descent. Those exponents fit the intermediate and complete `0.45` gates.

Therefore degree or an adjacency table of size `B` per state is not alone a
fatal obstruction. The fatal audited objects are:

1. expansion of the `D^4` composed paths;
2. a per-target scan of the `BD` edge table;
3. a `B^3` provenance or transition state;
4. a dense composed resultant or coefficient object;
5. a path oracle, source dictionary, or target-selected advice hidden in the
   representation; or
6. missing generic-prime, source-inverse, rank, or descent costs.

This correction does not promote IDEA-195. An `O(B)` inversion of the full
five-source output map would be the sought field-specific non-generic
operation; no such operation is supplied.

## Simultaneous trace/norm and source-inverse gate

For fixed endpoint variables `U,V`, write the Kummer branch polynomial

```text
S_3(U,V,Z)=alpha_2*Z^2+alpha_1*Z+alpha_0.
```

On charts where `alpha_2` is a unit, its unordered branch trace and norm are

```text
Tr_Z=-alpha_1/alpha_2,
Nm_Z= alpha_0/alpha_2.
```

A qualifying edge family must descend both coefficients through the same
target-independent, nonfixed support. Trace-only descent, a norm-zero test, a
deck-fixed component, or a bounded exceptional residue cannot transport the
complete branch. The descended representation must also remain closed under
the seven-channel update, not merely under scalar multiplication of values.

After a target is specialized, the locator must return an exact path and then
all five rational signed point sources. Multiple zeros kill the complete first
jet. Such strata must therefore be fully enumerated by a separate exact rule
or rejected by a preregistered test whose density, failures, and rank loss are
charged. A singleton ratio on a planted simple fiber does not establish this
all-strata inverse.

No audited artifact supplies:

1. a generic-prime positive-dimensional nonfixed support for both `Tr_Z` and
   `Nm_Z`;
2. an `O(BD)` or smaller representation family closed under all seven channel
   functions before leaf expansion;
3. an `O(D)` target locator for the four-level path output map;
4. exact multiplicity-aware signed source replay on every admitted stratum;
5. independent rank `B`, verified factor logs, and identical masked descent;
   or
6. complete bit time and memory at `lambda,mu<=0.45`.

## Named route audit

### Sparse multiplicative factor map

The valid one-step control

```text
Res_X(X^d-c,S_3(U,V,X))
```

can be evaluated at numeric `(U,V)` by powering `X^d` in a rank-two algebra.
It compresses one transition membership test. It does not invert the four
composed correspondences. Iterated elimination grows the composed degree;
explicit path lifting returns to (5). The simple subgroup version also needs a
large suitable divisor of `p-1` and does not give exact rational signed point
membership. It is not the P1549 locator.

### Recursive-S3 serial grammar

The frozen serial grammar stores `Theta(B^3)` exact `PREFIX3` derivations.
Hashing their endpoint states loses source replay unless a new output-sensitive
unranking operation is supplied. This is the existing P1515 provenance
control, not the shared `O(B)`-state grammar assumed above.

### Norms, resultants, and balanced cuts

Composing compact one-step incidences by a shared resultant is the P1513
product/norm object. Expanding its coefficients is the P1514 dense-elimination
control. A balanced two-versus-three realization stores or traverses `B^3`
states. None implements an `O(D)` path inverse.

### Lattes, ECFFT, power maps, and extension fields

P1537 and its predecessors already separate these routes. Lattes maps are
permutations on the rational prime subgroup or have many geometric lifts;
auxiliary ECFFT leaves do not inherit the target addition law; filtering them
breaks the deck; power maps need nongeneric rational roots or a charged
extension; and returning from extension-field branches lacks an exact rational
source inverse. P1549 does not reopen those families without a new support and
locator theorem.

### Linear transfer and supplied tensor identities

P1538 proves the endpoint-versus-source flattening rank for explicit linear
cut states and shows that adjoining the derivative channels does not reduce
the constant-channel rank. Matchgate, Pfaffian, MPS, Yang-Baxter, and
star-triangle names do not construct the restricted factor-base tensor. This
does not lower-bound an implicit nonlinear locator, which is exactly why the
conditional class (8) remains open.

## Complete ECDLP accounting boundary

The conditional relation and blind-descent exponents above grant:

1. one independent row for every accepted path;
2. no colour, sign, lift, multiplicity, pole, or verification loss;
3. target-independent setup reusable for known scalars and masked targets;
4. sparse factor-log linear algebra in `B^(2+o(1))=N^(0.4+o(1))` time and
   admissible state;
5. constant-size source output per accepted simple target; and
6. base-field operations with no extension or bit-complexity penalty.

A passing successor must replace these grants with proofs and keep

```text
lambda=max(
  setup,
  relation attempts times query and output,
  factor-log solve,
  masked-target attempts times query and output,
  verification
) <= 0.45,

mu=max(
  resident grammar,
  query state,
  factor-log state,
  source output,
  ambiguity
) <= 0.45.
```

The window (8) is therefore necessary within the frozen `O(B)`-layer,
`O(BD)`-edge, one-row model. It is not sufficient for an ECDLP algorithm.

## Disposition

P1549 independently verifies the exact seven-channel value algebra and
sharpens the remaining operation to a target-conditioned path locator. The
following scopes are terminal negative or control results:

1. value-space closure presented as domain compression;
2. explicit four-level path expansion;
3. per-target scans of all shared edges;
4. serial `B^3` provenance and balanced transition decks;
5. dense composed norms, resultants, and coefficient objects;
6. trace-only, norm-zero, deck-fixed, whole-fiber, and source-incomplete
   supports; and
7. the named Lattes, ECFFT, power-map, extension-return, and explicit linear
   transfer routes without a new nonmerge theorem.

The following class remains open and unsupplied:

```text
a generic-prime shared-layer S3 support with D=B^gamma,
11/12<=gamma<=1, simultaneous trace/norm seven-channel closure,
and an exact target-to-signed-source path locator in O(D) work
without D^4 expansion, a BD scan, B^3 provenance, or source advice.
```

P1549 is terminal inconclusive because the class is quantitatively admissible
but no member is constructed. No contract, solver, fixture, relation campaign,
factor-log solve, blind descent, scalar recovery, Shoup-bound improvement, or
breakthrough exists.

## Exactly one next action

Write
`ideas/artifacts/ECDLP-IDEA-195/p1550_high_branching_s3_path_locator_gate.md`.
Freeze one shared-layer generic-prime `S3` correspondence with
`D=B^gamma`, `11/12<=gamma<=1`, and derive its target-conditioned path
recurrence. The receipt must either provide exact `O(D)` query and signed
all-strata replay formulas with simultaneous seven-channel trace/norm closure,
or show that the frozen family expands `D^4`, scans `BD`, materializes `B^3`,
uses a dense resultant, loses generic-prime applicability, or lacks source
inversion. Do not execute the retired contract, build a solver, or generate a
toy fixture.

## Primary references

- Semaev, *Summation polynomials and the discrete logarithm problem on
  elliptic curves*: <https://eprint.iacr.org/2004/031>.
- Petit, Kosters, and Messeng, *Algebraic Approaches for the Elliptic Curve
  Discrete Logarithm Problem over Prime Fields*:
  <https://christophe.petit.web.ulb.be/files/16PKC_primeECDLP.pdf>.
- Ben-Sasson, Carmon, Kopparty, and Levit, *Elliptic Curve Fast Fourier
  Transform (ECFFT) Part I*: <https://arxiv.org/abs/2107.08473>.
- Golovnev, Guo, Horel, Park, and Vaikuntanathan, *Data Structures Meet
  Cryptography: 3SUM with Preprocessing*:
  <https://arxiv.org/abs/1907.08355>.
- Shoup, *Lower bounds for discrete logarithms and related problems*:
  <https://www.shoup.net/papers/dlbounds1.pdf>.

These references supply the summation-polynomial representation, neighboring
factor-map and polynomial-evaluation controls, generic preprocessing controls,
and the generic-group comparison boundary. None supplies the P1549 compact
path locator or a below-rho generic-prime ECDLP algorithm.
