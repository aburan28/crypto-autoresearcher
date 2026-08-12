# Object-dimension ledger: generalized-root circuit

## Status

`OPEN`, `REVIEW_REQUIRED`. This ledger is a zero-run accounting surface. Unknown
entries are proof obligations, not permission to omit their cost.

## Normalization

Let

```text
B       = number of public signed factor identifiers
B_b     = accepted sources in branch b, with sum B_b = Theta(B)
n       = prime subgroup order
p       = field modulus, with p and n of the same asymptotic size
B       = n^(1/5) at the five-term balance
w       = ceil(log2(p)) bits per field word
N_j     = distinct finite j-sum support, measured rather than assumed maximal
epsilon_rel = |D5|/n for uniform targets
R_req   = r_star-r_0 required independent rank increments
eta_r   = conditional rank-increment probability at current rank r
A_(1-alpha) = preregistered high-confidence attempt budget
```

The stationary expectation is `R_req/(epsilon_rel*eta)`, not an exact attempt
count. If `R_req=Theta(B^rho)`, `epsilon_rel=Theta(B^-delta_epsilon)`, and
`eta=Theta(B^-delta_eta)`, then the attempt exponent is
`rho+delta_epsilon+delta_eta`. All operation exponents below are in `B`; rho has
exponent `2.5`.

## Registered objects

| Object | Count or dimension | Bytes or operations to charge | Target dependent | Disposition |
|---|---:|---:|---|---|
| Curve and group constants | `Theta(1)` words | `Theta(w)` bits | no | allowed |
| Rational-map branch descriptions | constant number and degree | `Theta(1)` words unless a degree grows | no | allowed; growing degree is disclosed |
| Accepted source and decoration registry | `Theta(B)` or the exact duplicate-id count | all source, unique integer lift, point, orientation, `Reg`, and id bytes | no | required advice |
| Squarefree root polynomials `M_b` | total degree `Theta(B)` | `Theta(B)` field words | no | required advice; may be streamed but not omitted |
| Four-gate branch cover | at most `5^4` patterns | `Theta(1)` formulas | no | allowed |
| Leaf source variables | 5 field residues plus unique lifts `0<=t_i<T_i<=p` | `Theta(1)` live words; aliases charged separately | yes | allowed |
| Leaf affine coordinates | at most 10 field variables | `Theta(1)` live words | yes | allowed |
| Intermediate typed points | 3 point states | `Theta(1)` live words | yes | allowed |
| Gate slopes and inverse witnesses | at most 8 field variables | `Theta(1)` live words | yes | allowed |
| Target ports | one typed point | `Theta(1)` live words | yes | allowed |
| Dense D2 support or target mask | `N_2<=min(n-1,binom(B+1,2))` entries | `Theta(N_2*w)` bits | either | forbidden on the positive path; `Theta(B^2)` is collision-light only |
| Dense D3 support | `N_3<=min(n-1,binom(B+2,3))` entries | `Theta(N_3*w)` bits | no | forbidden on the positive path; `Theta(B^3)` is collision-light only |
| Eliminated `G_Q`, `H_Q`, or `f6` vector | at least `Theta(B^2)` live coefficients in the known routes | charged exactly | yes | forbidden on the positive path |
| Shift family | `R(B)` rows, `C(B)` monomials | construction and storage of every row/column | layout may be offline; coefficients may be online | `UNKNOWN`, derive before code |
| Target lattice or linearized system | `Z_lat(B)` nonzeros with coefficient bit lengths `h_lat(B)` | build, integer bit complexity, reduction, reads, writes, peak bytes | yes | `UNKNOWN`, cannot be projected away |
| Reduced vectors and candidate roots | `L(B)` algebraic candidates | all reduction, enumeration, registry rejection, and duplicate decoration work | yes | `UNKNOWN` |
| Exact completion system | `R_cmp(B)` by `C_cmp(B)`, `Z_cmp(B)` nonzeros | build, solve, rank, fill, and traffic | yes | `UNKNOWN` |
| Completeness certificate | `Cert(B)` words | generation and independent checking | yes | `UNKNOWN`, mandatory |
| Five-id witness | 5 public ids plus signs | `Theta(log B)` bits | yes | required output |
| Exact fallback | D2+D3 advice and query vectors | full comparator cost | yes | allowed only as a charged failure; cannot support signal |

Shared immutable advice is counted once. Page cache, memory maps, compressed
coefficients, preconditioners, reduced target-independent bases, and GPU or
accelerator resident data remain advice or workspace and must appear in the
table. A pointer per D2 orbit is a `Theta(B^2)` object even if its payload is
elsewhere.

## Required symbolic inequalities

Write `Ops_pre(B)`, `Ops_try(B)`, and `Ops_batch(B,A)` for actual field-normalized
work, including failed targets and certificate generation. Before a development
implementation, provide a derivation satisfying all of:

```text
Advice(B), Workspace_pre(B), and AdviceWrites(B)
                                = o(B^2.5) words or exact bit analogue
Ops_pre(B)                     = o(B^2.5)
TargetLive(B)                  = o(B^2) field words
Ops_try(B)=B^tau with          tau+rho+delta_epsilon+delta_eta < 2.5
Ops_batch(B,A)=B^u*A^v with   u+v*(rho+delta_epsilon+delta_eta) < 2.5
Ops_linear_algebra(B)          = o(B^2.5)
Ops_descent(B)                 = o(B^2.5)
```

For the constant-yield case `rho=1`, the independent-attempt gate reduces to
`tau<1.5`. Reporting `Ops_batch/A` without constructing the full batch is not
evidence of sharing. See `notes/ecdlp_relation_preprocessing_accounting_20260718.md`
for the confidence budget and comparator formulas.

## Bounded-root feasibility entry

For each proposed shift family, append a row containing:

```text
source bounds X_1,...,X_5
full-field variable bounds
scaled polynomial list
monomial support
R(B), C(B), Z_lat(B)
coefficient height h_lat(B) and bit-operation bound
determinant or norm bound
recovery theorem or explicitly labeled heuristic
slack exponent after B=p^(1/5)
complete algebraic candidate-list bound L(B), including nonregistry roots
```

Frozen first-power tensor-box entry:

```text
X_1*...*X_5 approximately B^5 approximately p
R(B), C(B): Theta(B^5)
Z_lat(B), dense M_b: Theta(B^6)
average scaled source degree: Theta(B)
determinant-volume heuristic slack: -Theta(B)
decision: REJECTED_SCOPED, NO EXECUTION
```

The unconditional negative is the `Theta(B^5)` explicit materialization cost.
The determinant entry is a heuristic screen that supplies no positive recovery
slack; it is not a lower bound on the shortest vector. The derivation is frozen
in `first-power-box-lattice-negative-v1.md`. Constant circuit width does not
change the box-volume equality. A different positive mechanism must exploit a
registered algebraic dependency, source composition, implicit representation,
or exact sparse-solver structure and receive its own ledger entry.

## Completion feasibility entry

For each proposed completion method, append:

```text
input candidate guarantee
complete ideal or solution-set semantics
R_cmp(B), C_cmp(B), Z_cmp(B)
degree and fill bounds
rank or Krylov work
certificate format and verifier cost
failure and retry law
```

Current entry is `UNDEFINED`. A generic Groebner, resultant, or Macaulay solve
is a cold baseline unless its actual dimensions satisfy the inequalities above.

## Immediate kill conditions

- Any target-specific object indexed by all D2 states.
- Any advice object indexed by all D3 states.
- A source-bound argument that uses only `X_1*...*X_5 approximately p` and
  asserts slack without a theorem or preregistered heuristic inequality.
- A modular source alias, rejected registry root, or duplicate identifier whose
  enumeration and completeness cost is omitted.
- A completion path that returns some roots but cannot certify completeness.
- A supported-target filter, oracle target schedule, or uncharged fallback.
- A one-target speedup whose actual `A`-target relation batch reaches
  `Omega(B^2.5)` before sparse linear algebra or descent.

## Next concrete action

Dimension either a composition-tower frontier or the bounded-separation scalar
root operator; do not tune or implement the rejected shift family.
