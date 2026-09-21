# Implementation plan: outer translator

## Modules

- `src/exact_floor.py`: exact D3 construction, full/partial queries, deterministic
  target schedules, scalar and D2-major batched affine queries, and advice/read
  accounting;
- `src/polynomial_engine.py`: dependency-free exact sparse/univariate `F_p`
  arithmetic, Semaev `f3/f4`, source substitution, root products, modular
  reduction, gcd, and coefficient-operation counters;
- `src/outer_translator.py`: curve/factor orchestration, source-branch extraction,
  exact brute compatibility and witness audits, baselines, gates, source hashes,
  authorization boundary, and JSON output;
- `src/verify_outer_translator.py`: deterministic replay plus an independently
  structured affine/order/support/root/witness audit.
- `src/run_development.py`: exact noncanonical configuration lock, clean-commit
  prelog, child-process resource capture, independent-verifier launch, and
  hash manifest. It exposes no canonical authorization path.

## Trust boundaries

- Constructor scalars are never passed to exact-floor or translator queries.
- Uniform target scalars and supported construction witnesses are private audit
  inputs and are not eligible advice.
- Full D5 support, brute S3/S4 compatibility sets, and scalar indices are
  verifier/audit objects; their operations and storage are segregated.
- The S3 control includes `(V-x(Q))` for finite-plus-identity decompositions and
  treats `Q=O` with an emitted branch that recovers every finite orbit and the
  identity sentinel.
- A source branch contains only sanitized public source parameters already
  emitted by the factor-base constructor.
- Target-specific `G_Q`, `H_Q`, gcds, masks, and roots are online workspace.
- D3 keys are baseline advice and may not enter translator preprocessing.
- The hard D3 advice comparator uses one x-orbit key and one orientation-bound
  witness, deriving the negative witness by adjacent factor-index involution.
- D2 identity routes are explicit and charged because x-coordinate Semaev
  polynomials do not represent the point at infinity.

## Determinism

Curve, factor-base, target, cache-ranking, and batch seeds are pure functions of
the disclosed experiment seed, bit size, family ordinal, and schedule label.
All points, polynomials, witnesses, and source branches use canonical order.
JSON is emitted with sorted keys and finite numbers only.

Supported coordinate targets are family-specific correctness controls. A
second uniform schedule uses a family-independent seed per curve; only those
identical points enter coordinate-versus-`random_x` ratios. Translator
many-target rows are explicit independent-target projections, not a claimed
shared batch evaluator.

Both schedules emit requested/available/realized cardinality records and fail
closed on a clamp. Final continuation is assigned only after the aggregate
independently checkable three-size/two-seed trend gate is attached.

## Source binding

Each artifact binds SHA-256 hashes for the generator, verifier, exact-floor
module, polynomial module, run wrapper, transitive curve/factor modules, contract,
hypothesis, research question, theory note, implementation note, literature
refresh, and every versioned pre-run review. A canonical artifact additionally
requires a frozen-configuration equality check and the separate authorization
flag.

## Independent checks

The verifier must independently:

1. validate strict JSON types and reject duplicate keys/nonfinite values;
2. reconstruct every curve, count its order, and verify the prime/cofactor and
   exclusion predicates;
3. rebuild factor points, D2, and D3, while exact replay reconstructs the public
   target schedules;
4. verify every returned five-leaf witness by affine addition;
5. compare scalar and batched complement outputs;
6. independently recompute S3/S4 compatibility and identity routes from affine
   group addition, while exact replay covers the dependency-free `f3/f4`
   coefficient path;
7. recompute source maps and denominator nonvanishing;
8. recompute symmetry/source advice, batch workspace/timing derivations, and the
   corresponding gates; exact replay covers the remaining diagnostic gates;
9. reject source, target, point, root, operation-count, advice, or witness
   mutations in focused tests.

## Development boundary

The first run is the exact contract development configuration only. It requires
`--allow-development`; `--authorize-canonical` is rejected for nonfrozen input.
The wrapper requires a clean committed worktree and a new output directory.
No result is promoted from one phase merely because the other phase is functionally
correct.
