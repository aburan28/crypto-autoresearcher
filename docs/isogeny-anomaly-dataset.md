# Isogeny-aware curve anomaly dataset (v0)

## Scope and epistemic constraints
This initial implementation supplies a deterministic dataset assembler, input validation and tests. **It does not generate curves, run Gröbner/SAT experiments, train a model, or establish a cryptanalytic speedup.** Those are separate execution milestones.

## Dataset contract
Each JSONL row represents one curve with stable `curve_id`, `family` (binary, prime, extension), `field` (characteristic and degree as exact strings/integers), exact decimal-string `order`, `features` object, and `provenance` (revision, generator, parameters). The assembler rejects conflicting records for the same curve ID and emits a deterministic SHA-256 digest.

Example:
```json
{"curve_id":"demo:binary:83:1","family":"binary","field":{"characteristic":"2","degree":83},"order":"123","features":{"trace":"7","j_invariant":"0","endomorphism_discriminant":null,"conductor":null},"provenance":{"revision":"commit-sha","generator":"sage-generator","parameters":{"seed":17}}}
```

## Planned relational entities
- **curves**: canonical field polynomial/basis, Weierstrass coefficients, isomorphism class, subgroup order, trace, discriminants, endomorphism conductor, automorphism count, embedding degree, CM data, torsion, field representation.
- **isogeny_edges**: source/target IDs, degree, separability, rationality/extension degree, kernel certificate, dual edge, verified map and volcano level.
- **experiments**: immutable experiment ID, solver/version, factor base, summation polynomial system, monomial order, random seed, resource cap, hardware/CPU pinning, revision and raw artifact hash.
- **measurements**: attempts, misses, timeouts, duplicates, verified relations, independent rank increments, relation yield, degree of regularity, Macaulay matrix dimensions, SAT conflicts, memory, wall-clock and CPU/GPU time.
- **comparisons**: matched curve pair, shared subgroup/field constraints, preprocessing and transfer costs, confidence intervals and paired controls.

Store unknown invariants as null rather than zero. Exact integers must never be coerced to floating-point ML features without explicit transformation.

## Feature families
1. Intrinsic: characteristic, extension degree, trace, subgroup factorization, j-invariant, CM discriminant, endomorphism conductor, embedding degree, automorphism group, twist data.
2. Graph: local isogeny degrees, volcano depth, conductor index across edges, short cycles, distance to crater, extension-of-definition and verified transport cost.
3. Algebraic solver: polynomial count/degrees, variable count, monomial ordering, regularity degree, leading-monomial profile, Hilbert series summaries, elimination width.
4. Empirical: verified independent relations per end-to-end second, failure rate, memory peak, SAT conflicts, rank progression, preprocessing and transfer cost.

## Training and evaluation
- Generate families at m=31, 51, 53, 83 (binary) and matched prime and extension-field sizes; use m=83 as the main binary scaling testbed. Do not extrapolate to m=131 without measured scaling evidence.
- Split by **isogeny component and parameter family**, not individual curves, to avoid graph-neighbor leakage.
- Fit baseline regressors on structural features; predict log(cost per independent verified relation). Residuals and prediction intervals define outliers. Use isolation forests or robust covariance only as complementary unsupervised detectors.
- Avoid target leakage: solver metrics are labels or post-hoc diagnostics, not predictors of their own outcome. Report paired comparisons within matched components and cross-family holdouts.
- Normalize and log full end-to-end costs including failed targets, duplicate relations, construction, verification and linear-algebra rank updates. Report censored timeouts rather than dropping them.
- An isogeny preserves ECDLP via transport when the degree is coprime to the subgroup order, but transport cost and computability matter; graph structure alone is not a hardness proof.

## Execution milestones
1. Implement Sage-based generators and independent order/isogeny certificate verification.
2. Persist curve and edge tables with stable IDs and exact field representations.
3. Connect existing F4/F5/SAT and relation benchmarks to immutable run receipts.
4. Run matched controls with identical solver budgets and hardware normalization.
5. Train grouped cross-validated models, publish residual rankings and blinded follow-up experiments.

## Usage
```bash
python tools/isogeny_anomaly_dataset.py examples/curves.jsonl --output /tmp/curves.jsonl
python -m unittest tests.test_isogeny_anomaly_dataset
```
