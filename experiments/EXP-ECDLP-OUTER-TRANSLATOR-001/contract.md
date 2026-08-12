# Experiment Contract: outer-aware complete comparator and coordinate translator census

## Status and boundary

`HYPOTHESIS`, `TOY-EVIDENCE`, `HEURISTIC`, and `MODEL-BOUND`.

This experiment runs only on generated ordinary prime-order curves over prime
fields. It has two phases:

1. establish exact `D2 + D3` as an honest outer-aware complete comparator,
   including partial advice and batched affine inversion;
2. test an exact source-domain Semaev `f4` elimination kernel before any
   optimized resultant, lattice, Groebner, or small-root solver is built.

Exact `D2 + D3` is generic meet in the middle with heuristic advice
`q^(3/5)` and online work `q^(2/5)`. It is not an exponent improvement, and its
completeness proof does not make this point a preprocessing lower bound. A
development pass by the coordinate kernel is permission to design a successor,
not an ECDLP result. Relation collection, rank, sparse linear algebra, and final
individual logarithms remain absent from this experiment.

## Hypothesis

For at least one public coordinate factor base, eliminating accepted source
roots and one exact `D2` x-orbit through the curve's actual `f4` relation yields
a target-conditioned compatibility polynomial whose target-independent advice,
target-specific workspace, and online field work are simultaneously smaller
than full `D3` advice and exact `D2 + D3` query work.

## Null hypothesis

After source-polynomial construction, denominator clearing, every polynomial
coefficient operation, modular reduction, gcd/root extraction, identity route,
memory traffic, and exact signed witness recovery are charged, the translator
either densifies toward full `D3`, costs at least exact `D2 + D3`, or shows
the same behavior on matched `random_x` factor bases.

## Parameters

- curves: seeded short-Weierstrass curves over prime fields;
- field-family restriction: the inherited development constructor uses only
  `p mod 4 = 3`; results may not be generalized to other prime congruence
  classes without a fresh-field successor;
- groups: prime order and cofactor one;
- exclusions: singular curves, trace in `{0,1}`, `j` in `{0,1728}`, repeated
  field moduli, and MOV embedding degree at most `20`; every curve and
  embedding degree is materialized before factor-base compilation;
- factor-base size: the exact sign-complete five-term occupancy rule inherited
  from `EXP-ECDLP-FIXED-COMPILER-001`;
- floor families: `x_interval`, `square_map`, `rational_union`, `random_x`,
  `random_scalar`, and `scalar_progression`;
- translator families: `x_interval`, `square_map`, `rational_union`, and
  `random_x`;
- partial-D3 fractions: `1/8`, `1/4`, and `1/2`, selected by public SHA-256
  rank independent of targets;
- target batches: `K in {1, B, 16B}`;
- target kinds: independently generated supported five-term points for
  correctness/recovery, plus one family-independent uniform nonidentity point
  schedule per curve for coordinate-versus-`random_x` comparisons;
- polynomial field: the same `F_p` as the curve;
- source branches: identity (`x=t`), square (`x=t^2+c`), and Mobius
  (`x=(t+d)/(t+e)`) with exact denominator clearing.

The configured `rational_union` is an explicit accepted-root parameterization,
not Petit-Kosters-Messeng's compositional `L=L_r o ... o L_1` factor-base
mechanism. This experiment may measure the former; it may not claim to test or
reject the latter. A genuine compositional-L construction is a separately gated
successor and control.

Constructor scalars for `random_scalar` and `scalar_progression` never enter an
eligible query, polynomial, advice record, or target schedule. The latter is a
comparator-only diagnostic and cannot establish coordinate structure.

## Phase A: exact outer-aware complete comparator

Let `F` be the sign-complete factor base and let `D2` contain every distinct
point `f_i + f_j`, with one exact two-leaf witness. Build

`D3 = {a + f : a in D2, f in F}`

with one exact three-leaf witness per distinct point. Query `Q` by scanning
`a in D2`, testing whether `Q-a` is a `D3` key, and verifying the recovered
five-leaf witness.

The full compiler stores exact D2 and D3 point keys and witnesses. Each partial
compiler stores a target-independent SHA-ranked D3 subset. A miss falls back to
the complete `F + D2 + D2` exact-D2 scan; no partial cache may silently reduce
success probability.

For a batch, report both:

1. target-major affine queries;
2. D2-major queries that read each D2 point once and batch all nonexceptional
   affine denominators with one inversion per D2 row.

Batching may reduce inversions and memory reads. It does not reduce the number
of target/D2 complement tests asymptotically, and it is a practical constant or
bandwidth result unless a later mechanism changes that count.

## Phase B: exact coordinate-elimination census

For nonidentity D2 x-orbits, define

`M2(V) = product(V - x(A))`.

For each source branch `b`, define the accepted-source root polynomial

`Pb(T) = product(T - t_i)`

and its public rational map `x = phi_b(T)`. Construct the actual fourth Semaev
polynomial through

`f4(U,V,W,X) = Res_Z(f3(U,V,Z), f3(W,X,Z))`.

For target `Q`, substitute `U=phi_b(T)` into `f4(U,V,W,x(Q))`, clear exactly
`den(phi_b)^4`, and eliminate the accepted source roots by product evaluation.
The product must equal the direct product over accepted factor x-coordinates up
to a disclosed nonzero scalar.

The executable advice representation for this census is the explicit D2-root
list, `M2`, accepted source-root lists, and map parameters. The constructed
`Pb` coefficients, accepted x-values, and factor ordinals are segregated
diagnostics because the current online kernel consumes roots rather than a fast
resultant with `Pb`. Extraction and sorting are included in preprocessing time
and traffic.

Combine all branches into `G_Q(V,W)`. Eliminate the second D2 x-orbit by the
exact root product

`H_Q(V) = product_{w: M2(w)=0} G_Q(V,w) mod M2(V)`.

Compute `gcd(H_Q,M2)`, extract roots using the public D2 x-orbit dictionary, add
an explicit identity-D2 route, recover full signed factor/D2 witnesses, and
verify their five EC leaves sum exactly to `Q`.

This root-product kernel is a census implementation, not a claim that naive
root products are the best resultant algorithm. It records the exact
degree/density and operation target that any product-tree, subresultant,
modular-composition, or multipoint successor must beat.

The direct quadratic-quadratic `f4` evaluation vector is also reported. Its
scalar baseline caches each invariant left `(factor_x,D2_x)` and right
`(D2_x,target_x)` `f3` coefficient triple on first use, and charges cache
construction plus every quadratic resultant. A nested root product is not new
merely because it is written as a translator.
If reduced `H_Q` is explicitly emitted as a dense degree-`Theta(|D2_x|)`
polynomial, writing its coefficients alone costs `Omega(B^2)` field elements.
Any sub-D2 online proposal must keep it implicit or sparse, avoid constructing
it, exploit stronger root structure, or share enough work across targets.

## Positive control

Use the same polynomial engine to compute

`C_Q(V) = (V-x(Q)) product_{w: M2(w)=0} f3(V,w,x(Q)) mod M2(V)`.

The extra factor represents the missing finite-plus-identity route. The gcd
roots, plus an identity sentinel iff `Q in D2`, must equal the independently
enumerated x-orbits that participate in exact `D2 + D2 = Q` decompositions.
`Q=O` is a separate control where every finite D2 x-orbit is compatible.
Every recovered four-leaf witness must verify. Any false negative, unexplained
root, or source-substitution mismatch invalidates the polynomial engine.

## Negative and matched controls

- `random_x` uses the identical finite-field polynomial pipeline and the same
  factor-base size, target schedule, D2 construction, and cost accounting;
- only `x_interval` versus `random_x` is an eligible same-map null because both
  use the identity source map `x=t`; `square_map` and `rational_union` rows are
  map-confounded diagnostics and cannot pass continuation without randomized
  controls using their respective maps;
- target/source permutations are audit-only mutation controls;
- exact D2 outer scan, full and partial D3, full materialized D4 where feasible,
  equal-advice fixed-base BSGS, and Pollard rho are disclosed baselines;
- deleting a source root, changing a source denominator, changing a D2 root,
  mutating a target, or changing a returned witness must be rejected;
- SymPy may be used only as a test oracle for tiny polynomial identities. The
  experiment implementation and verifier remain dependency-free.

Literature-only comparator rows disclose generic `5`-SUM indexing and the
optimal generic fixed-group preprocessing frontier. These are model boundaries,
not automatically transferable lower bounds for coordinate algorithms.

## Cost model and metrics

Report separately for every curve, family, phase, target kind, and batch size:

- `|F|`, `|D2|`, `|D2_x|`, `|D3|`, exact five-term success probability;
- D2/D3 preprocessing EC additions, field multiplications, inversions, wall
  diagnostics, canonical logical bytes, and Python deep bytes;
- scalar and batched query EC operations, field multiplications, inversions,
  dictionary probes, point/witness reads, logical bytes, and wall time;
- batch prefix/backward multiplications and the number of inversion batches;
- source-polynomial degree, nonzero coefficients, branch-map degree, cleared
  template degrees, terms, and denominator scalar;
- `f4` terms and degree in each variable;
- cached direct quadratic-resultant `f4` coefficient operations on identical
  tuples, including cache entries and hits;
- branch and combined `G_Q` degrees, terms, density, construction operations;
- unreduced `H_Q` degree bound, reduced degree/terms/density, modular reduction
  operations, gcd operations, root-extraction operations, and peak workspace;
- identity-route work, compatibility-root count, exact witness count, and all
  back-solving/audit probes;
- target-independent advice bytes and target-specific workspace bytes;
- operation-derived logical coefficient reads/writes, explicit source/D2 root
  reads, and witness-recovery bytes as a disclosed traffic lower bound; this is
  not reported as cache-line, RSS, or hardware-bandwidth measurement;
- whether `H_Q` is explicit, sparse, or implicit, including coefficient writes;
- target-symbolic degree and dense coefficient bounds for a batch template in
  `x(Q)`, even when that template is not materialized;
- weighted field work `M + wI` for `w in {10,50,100}`, while preserving the
  unweighted operation vector as authoritative;
- amortized total work for `K in {1,B,16B}` and the number of targets supported;
- translator many-target totals are reported as
  `preprocessing + K*(measured mean online work)` on the shared uniform sample;
  unless a real shared evaluator is implemented, these rows are labeled
  independent-target projections rather than batch speedups;
- exploratory log-log slopes over at least three sizes, never promoted from the
  development sweep.

Field additions and zero tests are reported separately. Polynomial operations
must count executed coefficient operations, not only output coefficients.
Audit-only exhaustive scalar indices and brute-force root sets are segregated.
Full-D3 advice is reported both as full signed point keys and as a
symmetry-compressed x-orbit codec with one orientation-bound witness and
factor-index involution. Translator gates use the smaller valid comparator.
The run wrapper reports process-level child `ru_maxrss`, but this experiment
does not claim phase-isolated peak RSS. Logical live-set bounds, not RSS, gate
continuation; retained Python sizes remain diagnostics.

## Development configuration

- bit sizes: `8, 10, 12`;
- curve seeds: `3317584535, 2246822507`;
- floor families: all six listed families;
- translator families: all four listed families;
- partial-D3 fractions: `1/8, 1/4, 1/2`;
- batch multipliers: `1, B, 16B`;
- supported and uniform batch replicates: two each;
- coordinate targets: two supported nonidentity targets per family and curve;
- matched targets: two identical uniform nonidentity points shared by every
  translator family on a curve;
- occupancy lambda: `0.5`;
- rho trials: two.

This configuration is explicitly noncanonical and requires
`--allow-development`. A canonical configuration uses bit sizes `10,12,14`,
three curve seeds, four target replicates, four coordinate targets, a frozen
source review, and `--authorize-canonical`. The canonical flag is invalid
without separately recorded user approval. No canonical command is authorized
by this contract.

## Functional success gate

1. Deterministic replay and independent curve/order/factor/D2/D3 checks pass.
2. Full and partial compilers preserve exact success through their disclosed
   fallback and every returned five-leaf witness verifies.
3. Scalar and batched comparator queries return the same solved-target set.
4. Batched affine outputs equal independent scalar affine subtraction.
5. The corrected S3 positive-control root set is exact for generic, identity
   half, and identity-target cases.
6. Source substitution and direct factor-root products agree up to the expected
   nonzero denominator scalar.
7. Every S4 compatibility root agrees with brute x-orbit enumeration and every
   recovered signed witness verifies.
8. Every mutation control is rejected.

Both supported and matched-uniform coordinate schedules report requested,
available, and realized cardinality. Any clamp fails the translator-wide
functional, pre-null, and instance gates even when all realized targets verify.

Failure of any item invalidates the implementation rather than the hypothesis.

## Batch practical-signal gate

A batch mechanism is a practical signal only if the following hold on both
seeds at every size:

1. it uses identical advice and returns the identical solved-target set;
2. it reduces inversions and D2 logical reads by at least `20%`;
3. any extra field multiplications are bounded by the recorded Montgomery
   prefix/backward products, and peak extra logical workspace stays within the
   pre-registered bound `K*(8*field_bytes + 2*target_index_bytes)` for pending
   affine records, denominator/prefix/inverse arrays, and active indices;
4. timed kernels exclude witness/affine audits and alternate execution order,
   but wall time remains an unattested diagnostic and cannot satisfy a verified
   practical-signal gate in this experiment;
5. any deterministic operation/read pass is labeled constant-factor/bandwidth
   unless complement-test
   scaling itself decreases.

The aggregate deterministic operation-signal rows are conjunctive by
factor-base family, target kind, and batch scale. The verified practical-signal
list remains empty because no separately attested timing harness is present.
Any future wall-clock claim requires raw repeated samples and a distinct
benchmark receipt; it cannot be created by editing volatile artifact fields.

## Coordinate-translator continuation gate

The coordinate mechanism may advance to an optimized resultant or multipoint
successor only if, on both seeds at every tested size:

1. the functional gate passes;
2. target-independent translator advice is at most `0.8x` the
   symmetry-compressed full-D3 logical advice and the conservative
   target-specific live-coefficient workspace upper bound is at most `0.8x`
   that logical advice baseline; retained canonical/Python sizes are disclosed
   diagnostics and are not described as measured RSS peaks;
3. online work through exact witness recovery is at most `0.8x` scalar exact
   `D2 + D3` under each disclosed inversion weight;
4. on identical family-independent uniform targets, an eligible same-map
   coordinate family is at most `0.8x` matched `random_x` online work or
   intermediate density and has no smaller exact supported-target count; in
   this contract only `x_interval` has that eligible identity-map null;
5. no target-specific coefficient vector, compatibility mask, D3 key, or hidden
   scalar is moved into preprocessing advice;
6. the aggregate has complete three-size/two-seed coverage; fitted log slopes
   for weighted online work at inversion weights `10,50,100`, combined-`G`
   maximum variable degree and term count, and explicit `H` coefficient writes
   do not exceed the symmetry-D3 advice-bit materialization slope; and the
   combined-`G` density slope is nonpositive. Undefined slopes fail closed;
7. the nonnegative translator-minus-D3 preprocessing differential amortizes
   within at most `B` supported relation targets; projected `K`-target totals
   must separately disclose that no shared translator batch work was executed.

Passing is only a positive toy signal. Even `T=o(B^2)` for one decomposition is
not yet enough: collecting about `B` relations with `B=p^(1/5)` requires roughly
`T=o(B^(3/2))=o(p^(3/10))` before preprocessing, matrix, and descent costs to
beat `p^(1/2)`. Any future ECDLP-level continuation must demonstrate total
fitted exponent below `0.5` on fresh random curves with relation generation,
matrix rank, sparse linear algebra, and individual descent included.

The final per-instance continuation gate is the conjunction of exact target
cardinality, the identity control, functional checks on supported and matched
uniform targets, every target-level advice/workspace/online/amortization gate,
the eligible same-map null, and the family-level trend gate.

## Falsification criterion

If the functional gate passes but the coordinate continuation gate fails, record
a scoped negative for this exact root-product/resultant representation and its
tested source maps. Preserve any batch inversion Pareto improvement separately.
Do not generalize the result to optimized resultants, all coordinate predicates,
batch multipoint evaluation, point decomposition, index calculus, or ECDLP.

## Reproduction command

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B \
  experiments/EXP-ECDLP-OUTER-TRANSLATOR-001/src/run_development.py \
  --output-dir \
  experiments/EXP-ECDLP-OUTER-TRANSLATOR-001/development/DEV-OUTER-TRANSLATOR-001
```

The wrapper refuses a dirty worktree or an existing output directory, prelogs
the exact child commands and source hashes, captures process-level child
resource usage and raw logs, runs the independent verifier, rechecks source
stability, and writes `run-manifest.json`. It cannot authorize a canonical run.
