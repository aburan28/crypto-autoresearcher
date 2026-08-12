# P1512 Source-Labelled Linear-Chow Atomizer Contract

Status: `preregistered_theorem_gate`. No matrix construction or scaling run is
approved until Phase 0 supplies the exact source-biconditional complex and its
complete size proof.

## Objective

Test the representation-changing exception left by P1511: construct one
target-uniform linear complex before P1510's per-target pair-resultant leaves
are emitted, specialize it on public targets, and recover exact five-factor
source atoms in total work and state below Pollard rho.

On the frozen `q=Theta(r^5)` family, every construction, matrix coefficient,
specialization, kernel/cokernel operation, source inverse, unsuccessful target,
relation row, rank operation, and verification must fit a proved exponent
strictly below `5/2` in `r`.

This is a theorem gate, not relation collection, blind descent, an ECDLP
algorithm, or a Shoup-bound break.

## Frozen Inputs

- IDEA-115 source-labelled Ulrich-Chow hypothesis, SHA-256
  `708eef11d2f4ed4acbd5cb6f831ed21f419b26304a4e7de7e8a3610ebce55ab6`;
- P1510 multiplicative compiler derivation, producer, result, and independent
  audit;
- P1511 FD-width and factorized-semijoin derivations, results, and independent
  audits;
- P1493 pair-support product/CRT boundary and independent audit;
- immutable P1512-active focus queue, generated plan, and readable report,
  which must be hash-frozen before execution.

Every producer must record exact hashes. Any changed input requires a
versioned successor contract.

## Exact Incidence

Let `D={P_1,...,P_(2r)}` be the oriented public factor deck and let `R` be a
public target. The complete labelled fiber is

```text
X_R = {(i1,...,i5): R=P_i1+P_i2+P_i3+P_i4+P_i5}.
```

The universal incidence includes target coordinates, all five source labels,
signs, repeated factors, vertical pairs, infinity, nonreduced fibers, and every
complete addition chart. The candidate must give a public projective or graded
presentation of this incidence without enumerating `D^5`, A2, A3, P1510 leaves,
or known source tuples.

## Candidate Object

Freeze a target-independent sheaf, module, resolution, Chow/Tate complex,
subresultant complex, or exterior-syzygy object `C`. For a public target `R`,
specialization `C(R)` must satisfy an exact biconditional:

```text
normalized kernel/cokernel atom of C(R)
    iff
one complete signed source tuple in X_R.
```

There must be a public inverse from every atom to the five factor indices and
no atom may aggregate two source tuples without an independently bounded and
charged split. Determinants, ranks, membership bits, or unlabeled common
factors are insufficient.

## Phase 0: Linear-Complex Theorem

Before any implementation, the derivation must provide:

1. the exact ambient variety or scheme, embedding, grading, and target map;
2. the proposed Ulrich sheaf/module or other linearizing object and proof that
   every required cohomology or exactness condition holds;
3. every matrix dimension, block multiplicity, entry degree, coefficient
   payload, and construction recurrence as a function of `r`;
4. the kernel/source biconditional, normalization, multiplicity policy, and
   exceptional-chart inverse;
5. a proof that construction, specialization, atom extraction, source output,
   relation collection, sparse linear algebra, and peak state are all below
   `r^(5/2)` up to polylogarithmic factors;
6. a trust manifest showing no source table, P1510 leaf family, endpoint roots,
   or target-selected resolution enters construction.

A named sheaf, generic free-resolution command, determinant, or solver call is
not a derivation.

## Degree And Payload Gate

P1511 supplies the primary negative control. Its favorable batch products have
degree `N=r^3`, gcd degree `r`, and exact source output `r`, while the natural
P1510 product circuits contain `r^3` leaves per side.

For any `m x m` matrix whose entries are linear in the endpoint or target
parameter, `degree(det M)<=m`. Therefore a linear determinantal representation
of a degree-`N` batch polynomial requires `m>=N`. Standard Sylvester, Bezout,
subresultant, companion, and exterior-compound constructions must record this
dimension and cannot pass by calling it a linear complex.

Higher-degree or circuit-valued entries remain admissible only if their full
coefficient/circuit construction, evaluation, and source inverse are charged.
Moving the `r^3` payload into entries, annotations, kernel vectors, or a
resolution does not reduce the exponent.

This degree argument is a control, not a universal no-go for every Chow form or
nonlinear target-uniform complex.

## Exact Controls

- P1511's planted product systems at `r in {4,6,8,12,16,24,32}`;
- standard Sylvester and Bezout matrices for the batch gcd;
- principal subresultant and compound/exterior-power matrices;
- a published small Ulrich/Chow determinantal example with known kernel atoms;
- a label-dropped determinant matched for degree and coefficient payload;
- two-source and three-source elliptic toy fibers with exhaustive labels;
- mixed-source and nonreduced planted schemes that force atom separation;
- dense resultant, quotient-module, and post-hoc source annotation controls.

## Decision Rule

Record a scoped positive theorem only if one explicit target-uniform complex is
constructed before P1510 leaf emission, has a proved source-atom biconditional,
and has complete time and state exponents below `5/2` in `r`.

Record a scoped negative for the tested complex family if matrix dimension,
entry payload, kernel output, or source splitting is `Omega(r^(5/2))`. Record
`REVISE` or `inconclusive` if the sheaf/module is only named, exactness is
unproved, exceptional fibers are omitted, or complexity is inferred from toy
wall time.

Even a positive P1512 theorem would authorize only a separately frozen toy
complex implementation and then separately frozen relation, rank, and blind-
descent experiments. The generic sub-rho/Shoup claim remains `not_attempted`.

## Independent Audit

The audit must not import candidate helpers. It must reconstruct the incidence
and matrix dimensions, verify all exact sequences or rank identities on frozen
controls, replay every atom-to-source inverse, recompute coefficient and state
costs, and reject mutations to one matrix entry, source label, multiplicity,
exceptional chart, dimension formula, trust input, and claimed exponent.

## Budget

Phase 0 is limited to 7,200 wall-clock seconds, 8 aggregate CPU-hours, 8 GiB
peak memory, and 12 runs. No larger matrix or curve campaign is approved by
this contract.
