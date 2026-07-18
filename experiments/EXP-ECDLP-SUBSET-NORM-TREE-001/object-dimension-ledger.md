# Object-dimension ledger: subset-norm tree

## Status

`OPEN`, `REVIEW_REQUIRED`. Unknown dimensions are explicit proof obligations.
This file does not authorize implementation or execution.

## Normalization

Let

```text
B        = number of signed public factor identifiers
n        = prime group order, with B=n^(1/5) at five-term balance
N2       = distinct finite D2 points <= min(n-1,binom(B+1,2))
N3       = distinct finite D3 points <= min(n-1,binom(B+2,3))
w        = ceil(log2(p)) bits per base-field word
epsilon_rel = |D5|/n for uniform targets
R_req    = r_star-r_0 required independent rank increments
eta_r    = conditional rank-increment probability at rank r
A_(1-alpha) = preregistered high-confidence attempt budget
```

`N2=Theta(B^2)` and `N3=Theta(B^3)` require measured collision-light support.
The stationary expected attempts are `R_req/(epsilon_rel*eta)`; this is not an
exact deterministic count.

One quadratic-extension word is two base-field words plus registered canonical
metadata. Record the irreducible quadratic and expand every extension operation
into its exact base-field arithmetic and traffic vector. D2 leaves are distinct
oriented affine points; identity is a separate sentinel. All multiplicities and
witness payloads are counted separately from distinct support.

## Offline and advice objects

| Object | Dimension | Charge | Tier A | Tier B |
|---|---:|---:|---|---|
| Curve, irreducible quadratic, extension basis, encoding rules | `Theta(1)` words | construction, canonical bytes, and base-field operation formulas | allowed | allowed |
| Factor registry | `Theta(B)` records | source, point, sign, and id bytes | required | required |
| D2 distinct leaves and pair witnesses | `Theta(N2)` records | all build operations and bytes | required | required unless exactly regenerated and charged |
| Balanced tree topology | `Theta(N2)` nodes | indices and child links | required | required |
| Dense node product polynomials at all levels | `Theta(N2 log N2)` extension coefficients | product-tree build, storage, and traffic | allowed and charged | allowed only within total advice gate |
| Root product `M_root` alone | `Theta(N2)` coefficients | build and bytes | allowed | allowed |
| Explicit D3 dictionary and triple witnesses | `Theta(N3)` records | enumeration, deduplication, bytes, and bandwidth | allowed and charged | forbidden |
| Conceptual translated `C_Q` | degree `Theta(N3)` | output-size construction | forbidden online | forbidden online |
| Node operator advice `A_I` | `s_I(B)` words and `r_I(B)` generator rank | all derivation, build, and bytes | `UNKNOWN` | `UNKNOWN` |
| Total node operator advice | `S_op=sum_I s_I` | full persistent and accelerator-resident bytes | charged | must be `o(B^3)` with all other advice |
| Terminal D3 witness lift | explicit D3 or scan `B` factors against charged D2 | membership, exact triple recovery, traffic, and replay | explicit dictionary permitted | exact `Theta(B)` online baseline uses no new D3 advice; any faster method is separately dimensioned |
| D2/D3 identity sentinels and witnesses | `Theta(1)` records | deterministic priority and membership path | required | required |
| Supported-target or answer table | one or more records per target | every key, bit, pointer, and payload | forbidden | forbidden |

Storing only generators is useful only after the displacement equation and
generator rank are proved. A seed that regenerates `Theta(B^3)` support per
query moves cost from advice to online work; it does not remove it.

## Per-target objects

| Object | Dimension | Required accounting | Disposition |
|---|---:|---|---|
| Target `Q` | `Theta(1)` words | canonical bytes and specialization work | allowed |
| Materialized translated D3 roots or polynomial | `Theta(N3)` words | construction and traffic | forbidden |
| All D2 membership, norm, or remainder values | `Theta(N2)` words | construction and output traffic | forbidden on positive path |
| Dense remainder `C_Q mod M_root` | `Theta(N2)` coefficients | exact build and live bytes | forbidden on positive path |
| Node specialization state at level `j` | `t_j(B)` words | build, parent-to-child restriction, reads, writes, and lifetime | `UNKNOWN` |
| Exact node predicate | one bit plus positive or negative certificate | `q_j(B)` base-field-normalized operations | required |
| Root-to-leaf transcript | `Theta(log N2)` decisions | certificate and independent replay | required |
| Terminal D3 witness | three public ids | lift operations and advice reads | required |
| Final five-id witness | five public ids | independent affine replay | required |
| Fallback scan | `Theta(N2)` probes | full exact comparator vector | charged failure only; cannot support signal |

The full online cost is

```text
T_online(B,Q) = sum over queried levels j of q_j(B)
                + target specialization
                + terminal witness lift
                + certificate generation.
```

The number of calls is `Theta(log N2)`, but no factor is treated as unit cost
until its operator dimensions are filled in.

## Tier gates

### Tier A: online-only fixed curve

```text
Advice_A,total = O(B^3) in actual canonical bytes
T_online(B,Q) = o(B^2)
TargetLive(B)  = o(B^2) field words
```

`Theta(B^3)` D3 advice is allowed but must be reported with offline operations,
bytes, bandwidth, and amortization over the exact number of supported targets.

### Tier B: compressed advice

```text
Advice_total(B)    = o(B^3) field-word equivalent
PeakWorkspace_pre  = o(B^3)
T_online(B,Q)      = o(B^2)
TargetLive(B)      = o(B^2)
S_lift(B)          is included in Advice_total(B)
```

A finite `0.8x` ratio is only a development screen. An empirical Tier B claim
requires upper-confidence B-slopes below 3 for advice and peak preprocessing
workspace.

### Eventual single-instance index-calculus path

If `R_req=Theta(B^rho)`, support decays as `B^-delta_epsilon`, and rank yield as
`B^-delta_eta`, then the attempt exponent is
`rho+delta_epsilon+delta_eta`. A credible sub-rho path needs

```text
Advice_total, AdviceWrites, PeakWorkspace_pre = o(B^2.5)
Ops_pre(B)          = o(B^2.5)
Ops_batch(B,A_(1-alpha)) = o(B^2.5)
Ops_linear_algebra  = o(B^2.5)
Ops_descent         = o(B^2.5).
```

For an independent attempt of cost `B^tau`, require
`tau+rho+delta_epsilon+delta_eta<2.5`. For batch law `B^u*A^v`, require
`u+v*(rho+delta_epsilon+delta_eta)<2.5`.

Tier A explicit D3 advice has exponent 3 and fails this gate even if online
queries become spectacularly small. It may still be a fixed-curve online result.

## Generic preprocessing report

For any eventual arbitrary-target DLP pipeline, report separately:

```text
P_G         = preprocessing generic-group queries
S_bits      = immutable target-independent advice bits
S_group     = advice converted to complete generic-group records
T_G         = online generic-group oracle queries only
T_field     = concrete coordinate field-operation vector
Traffic     = probes, reads, writes, and bytes
epsilon_DLP = probability of returning a uniform target's discrete log
N_targets   = exact amortization count
```

Only theorem-aligned generic DLP algorithms report the bit-advice theorem ratio
`(S_bits+O(log n))*T_G^2/(epsilon_DLP*n)`. After a complete record encoding,
`S_group*T_G^2/(epsilon_DLP*n)` is only an exponent-normalized diagnostic. Also
report the preprocessing-query diagnostic
`(P_G*T_G+T_G^2)/(epsilon_DLP*n)`, using generic-group query counts. Field
operations, traffic, relation probability, coordinate structure, and batch
sharing remain separate and cannot be inserted into either ratio. The generic
lower bound is not directly a theorem about a five-term relation oracle. See
`notes/ecdlp_relation_preprocessing_accounting_20260718.md`.

For candidate `I` and output-equivalent comparator `C`, report

```text
K_star=inf {K>=1 : P_I+U_I(K) <= P_C+U_C(K)}
```

using actual batch work, and require `K_star<=A_(1-alpha)` for relation
collection.

## Root-node preflight entry

The first required derivation must fill:

```text
operator input/output modules: A_root=K[Z]/(M_root), End_K(A_root)
target-independent map:        J=multiplication by Z mod M_root
target specialization:         T_Q=(c_Q mod M_root)(J)
displacement operator:         Delta_J(T)=J*T-T*J
generator rank r_root(B):       0
displacement-kernel dimension: N2, since Cent(J)=K[J]
dense companion boundary:      N2 K-coefficients, REJECTED_SCOPED
direct explicit-factor input:  N3-epsilon_+(Q) translations, REJECTED_SCOPED
stored fixed coefficients:     Theta(N2) for M_root and D2 registry
query work q_root(B):           Theta(N2) dense-interface traffic or
                                Theta(N3) direct-factor specialization
translation branch cover:       exact, including Q=O, S=Q, S=-Q, ordinary
terminal-lift baseline:         Theta(B) factor scan with D2 probes
child restriction law:          not constructed for rejected interfaces
zero/nonzero certificates:      resultant/gcd exact; compact certificate open
identity and degree-drop path:   exact in root-operator-preflight-v1.md
decision:                       REJECTED_SCOPED for these two interfaces
```

The `Theta(N2)` statement is the dense power-basis boundary of the frozen
companion interface, not an information-theoretic lower bound on `r_Q`. The
`Theta(N3)` statement is for direct translated-factor processing, not a lower
bound on source-implicit specialization.

Second frozen family:

```text
ordered source algebra A_123:      Theta(B^3) coordinates if explicit
first dense sequential norm A_12: Theta(B^2) target slots
direct tuple stream:              Theta(B^3) translations
standard black-box vectors:       Theta(B^3) scalar coordinates
explicit selectors/global units: Theta(B^3) stored or regenerated coordinates
finite-child semantic law:        R_I=R_L*R_R, exact
root D2-identity membership:      Theta(B) charged factor scan
signed terminal provenance:       Theta(B) charged factor scan
decision:                         REJECTED_SCOPED for these explicit interfaces
```

The dense counts are allocated or worst-case interface widths, not lower bounds
on a compact scalar circuit. The two-source intermediate applies only to
sequential elimination that explicitly emits it.

Fresh successor entry:

```text
scalar-only transposed norm:        UNDEFINED, REVIEW_REQUIRED
compact branch selector:            UNDEFINED, REVIEW_REQUIRED
internal vector spaces and oracles: UNDEFINED
target-parametric boundary size:    UNDEFINED
construction work and traffic:      UNDEFINED
chosen-child scalar/update law:      UNDEFINED for first witness
both child scalars:                  required only for all-root enumeration
positive and negative certificates: UNDEFINED
signed terminal provenance:         Theta(B) baseline available
```

Known naive routes are already outside the candidate:

```text
materialize C_Q:                 Theta(B^3) target output
evaluate every D2 predicate:     Theta(B^2) target output
form dense C_Q mod M_root:       Theta(B^2) target state
```

Bounded-separation v3 entry:

```text
node degree n:                     N2=Theta(B^2)
distinct translated values t_Q:   N3-epsilon_+(Q)+o_3*1_(Q!=O)
linear homogeneous moment span:   min(n+1,t_Q)
node-oblivious linear width:       n+1 in collision-light full support
canonical formal slots:            sum_k binom(k+r_A-1,r_A-1)
                                    *binom(n-k+r_D-1,r_D-1)
canonical active slots:            proof obligation after finite reduction
global EC rank-one ratio:           excluded by addition-fiber divisors
explicit trace recurrence order:   t_Q=Theta(B^3), REJECTED_SCOPED
first-witness child law:            one chosen child at each known-zero parent
path work and traffic:              each summed, strict o(B^2) required
aggregate peak target state:        strict o(B^2) required
minimal CP/TT/circuit size:         OPEN
fixed-node nonlinear predicate:     OPEN
decision:                           decision-v3.json, weaken
```

Historical three-source TT zero-locator sketch (`SUPERSEDED PAPER DRAFT`):

```text
finite-branch tensor:               G_Q in K^(d_1*d_2*d_3)
zero indicator:                     Z_Q=1-G_Q^(|K|-1), exact componentwise
logical zero test:                  Z_Q is zero tensor iff no finite hit
witness locator:                    leading nonzero TT index, conditional
source-to-public provenance:        three registered source IDs
remaining leaves:                   one charged D2 pair-witness lookup
root D2-identity route:             charged Theta(B) Member_D3 scan
TT state at uniform rank r:         O(B*r^2), literature-derived inference
coarse exact normalization work:    O(B*r^3) per step, literature-derived
state threshold:                    r=o(B^(1/2)) before other state
per-normalization work threshold:   r=o(B^(1/3)) before logs/circuit length
G_Q circuit length and ranks:        UNDEFINED, FATAL OBLIGATION
indicator Hadamard chain:            O(log |K|) normalizations, UNDEFINED ranks
complete selector/branch cover:      UNDEFINED
total target work and traffic:       UNDEFINED, must be strict o(B^2)
total fixed advice/workspace:        UNDEFINED, must be strict o(B^3)
decision:                            PAPER PREFLIGHT REQUIRED, NO SOURCE
```

The `O(B*r^3)` normalization line and resulting `r=o(B^(1/3))` threshold above
undercharge the standard raw Hadamard route. They are retained only as
historical provenance. The current direct five-source ledger is
`experiments/EXP-ECDLP-TT-ZERO-LOCATOR-001/object-dimension-ledger-v4.md`; it
charges raw allocation `B*(2*r^2+3*r^4)`, exact reduction `O(B*P^3)` with
`P<=r^2`, every target construction/certificate/replay term, and cumulative
traffic separately.

## Immediate kill conditions

- Root specialization has `Omega(B^2)` live coefficients, values, or traffic.
- Total Tier B operator plus witness-lift advice has `Omega(B^3)` records.
- Exactness requires a hidden D2 mask or target answer table.
- Identity support or target-dependent degree drop requires an unreported D3
  membership oracle.
- A tree-based compact root operator cannot choose one child without rebuilding
  a D2-length target object. A direct root zero locator may instead return the
  source tuple and bypass the tree, but must fully charge that locator.
- A positive leaf cannot produce a registered D3 witness through the charged
  `Theta(B)` D2-lift baseline or a fully dimensioned improvement.
- The matched random operator has the same rank and cost within the
  preregistered gate.
- A one-target average is extrapolated to `A_(1-alpha)` targets without
  constructing and charging the batch.

## Next concrete action

Use the completed direct v4 paper preflight and derive or refute the first
RCB-plus-norm-indicator central-rank certificate. Do not create source code if
the central rank reaches `Omega(B)`, any cumulative Tier-B target resource
reaches `Omega(B^2)`, or fixed advice/workspace reaches `Omega(B^3)`.
