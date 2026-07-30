# P1510 Global Truncated Marked-Resultant Compiler Contract

Status: `approved_for_exact_preflight`. Scaling and claim promotion remain
evidence-gated.

## Objective

Test the only open algorithmic step in P1509's positive Hasse-jet source
section: construct the complete degree-at-most-two source-marked resultant as
global endpoint-polynomial coefficients without factoring the endpoint
resultant or opening one gcd per endpoint.

This is a compiler-only gate. A positive result is not relation collection,
factor-log recovery, blind target descent, a Pollard-rho improvement, or a
Shoup-bound break.

## Frozen Inputs

- IDEA-068 constructive section, SHA-256
  `6a8183033643ea9dab126a7add08c69508814eaee0a0667151e9ff569432f7b5`;
- P1509 contract, SHA-256
  `7b35fdd15681ad35c2cf07d3549d594208401f59412e82e4e69e61244419ed60`;
- P1509 result and independent audit, SHA-256
  `23ae26d712cd6ee521705985f9b25623a8713c46bd6e085b3586b503e79efc66`
  and `efa467d959138862d6e86570bb50f0ad962c4c925a8fe51041ffd7a6ea451227`;
- P1509 producer and audit runner, SHA-256
  `cec4db1835bc11c303864f9ee6a358d2e1db7430e77fbc58470adbc103475aec`
  and `ad8e4b32f6328926ba1363ea32e93429106e8f21d1393a7f506634c0ee617569`;
- P1510 multiplicative compiler derivation,
  `/Volumes/Volume/crypto-autoresearcher/ideas/artifacts/ECDLP-IDEA-068/p1510_multiplicative_compiler_derivation.md`,
  SHA-256
  `f1f5a5ce8ec38a89b7474c79490634c148cd5443395d66391582a54b8dfa9fad`;
- immutable P1510-active focus queue v2 and generated focus plan v2,
  `/Volumes/Volume/crypto-autoresearcher/focus/archive/focus_queue_p1510_active.json`
  and `/Volumes/Volume/crypto-autoresearcher/focus/archive/focus_plan_p1510_active.json`,
  SHA-256
  `8f455130a4b9f462117e95c4be5bdfb408029a3642b246b3daea0e4d50f7c1ac`
  and `e5ad59fc6216a8ad35583d91f245956c43fc79052a9a3c7e77513b7b9e0acd0d`;
- immutable P1510-active readable focus report,
  `/Volumes/Volume/crypto-autoresearcher/focus/archive/focus_report_p1510_active.md`,
  SHA-256
  `63eccb999d05184de0fa0c0b81e53aec903af0f3af3aad2812a583735ca3f263`.

The P1509 audit must remain terminal with all `12/12` checks passing. Any
changed input requires a versioned successor contract.

## Exact Algebra

For each frozen public start coordinate `u`, selector factors `f_i`, and public
codes `alpha_i=i+1`, rebuild

```text
A(V)   = product_i f_i(u,V)
A_0(V) = sum_i product_(ell != i) f_ell(u,V)
A_1(V) = sum_i alpha_i product_(ell != i) f_ell(u,V)

B(V,W)   = product_i f_i(V,W)
B_0(V,W) = sum_i product_(ell != i) f_ell(V,W)
B_1(V,W) = sum_i alpha_i product_(ell != i) f_ell(V,W).
```

Use the fixed 15-element marker basis

```text
1,
E0,E1,H0,H1,
E0^2,E0*E1,E0*H0,E0*H1,E1^2,E1*H0,E1*H1,H0^2,H0*H1,H1^2
```

for

```text
R = F_p[W][E0,E1,H0,H1] / (marker monomials of total degree >= 3).
```

The compiler must emit every coefficient polynomial `C_mu(W)` in

```text
Res_V(A + E0*A_0 + E1*A_1,
      B + H0*B_0 + H1*B_1) mod marker_degree^3
  = sum_mu C_mu(W) * mu.
```

No sparse omission is allowed. Zero coefficients are explicit. Record the
degree, dense coefficient count, canonical serialization hash, and construction
operation count for all 15 components.

## Source-Blind Construction Boundary

The compiler may read the curve, public start, selector polynomial, ordered
public selector-factor catalog, and frozen public code assigned to each factor.
It may not read or derive algorithmic advice from:

- roots or factorization of the endpoint resultant in `W`;
- an endpoint-wise `gcd(A(V),B(V,w))`;
- P1505 source partitions or any endpoint-to-source table;
- endpoint-specific vanishing-factor indices or common intermediate roots;
- hidden discrete logarithms, target-selected codes, or known-source labels.

Place the compiler behind a narrow input adapter. Hash-freeze its 15-component
output and operation transcript before the verifier receives any forbidden
object. Static imports, runtime access logging, and an independent source-input
mutation must check this boundary.

## Phase 0: Construction Recurrence

Before a scaling run, freeze one exact algorithm that computes the truncated
resultant without first computing the full marker polynomial. The derivation
must state:

1. the recurrence, subresultant, determinant-derivative, or product-tree
   identity used;
2. why every division is exact or why no division by a nonunit in `R` occurs;
3. how truncation is preserved after every addition and multiplication;
4. the number and degrees of all endpoint polynomials held simultaneously;
5. a recurrence in `r` for base-field additions, multiplications, inversions,
   and endpoint-polynomial coefficient operations;
6. a proved upper bound for total work and peak state.

A high-level call to a generic resultant or determinant routine is not a cost
proof. Full Sylvester determinants, full marker-polynomial resultants, and
per-endpoint openings may be retained only as charged controls.

If Phase 0 cannot produce a source-blind exact construction and symbolic bound,
record `REVISE` or a scoped negative. Do not infer asymptotics from wall time.

## Exactness Fixtures

Run the frozen compiler on all eight P1490 cells (`L=4,8,16,32`, both nonces;
`r=4,4,7,12`). After the output is frozen, the verifier must:

1. evaluate all 15 coefficients at every one of the 908 endpoint coordinates;
2. reproduce every P1509 degree-one and degree-two local leading form up to the
   same nonzero public resultant scale;
3. recover all 900 nonreturn source partitions and both start signs;
4. verify that the known return endpoint has zero marker components below its
   first nonzero order `2r` while retaining it as a control;
5. compare `C_1(W)` with the ordinary unmarked P1490 resultant;
6. compare all 15 coefficients with a full symbolic-resultant oracle at the
   smallest feasible sizes only.

## Scaling Fixtures and Cost Accounting

Use deterministic planted factor systems at
`r in {4,6,8,12,16,24,32}` with degree-one and degree-two common-root cases,
nonendpoint cases, and the growing-order return analogue. Freeze all factors
and codes before running the compiler.

The operation counter must descend to base-field coefficient operations. In
particular, one endpoint-polynomial multiplication, truncated-ring
multiplication, matrix operation, or resultant call cannot be charged as one
operation. Record wall time and peak RSS as secondary implementation evidence.

The primary passing condition is a reviewed symbolic
`O(r^2 polylog r)` work bound and `O(r^2)` peak coefficient-state bound. Fits of
`log(operations)` against `log(r)` and normalized work curves are diagnostics.
They cannot rescue a missing proof or overrule a proved cubic term.

The frozen preflight budget is at most 21,600 wall-clock seconds, 24 aggregate
CPU-hours, 16 GiB peak memory, and 30 total runs. Shards may separate frozen
sizes and controls only; all shard work is aggregated.

## Controls

- ordinary unmarked resultant and marker-off replay;
- full symbolic marked resultant on the smallest feasible fixtures;
- generic Sylvester determinant with complete charged arithmetic;
- P1509's endpoint-wise gcd verifier with its `Theta(r^3)` aggregate charge;
- explicit endpoint/source table replay, labelled oracle-only;
- planted degree-one, degree-two, nonendpoint, and growing-return systems;
- random public code permutations with inverse catalog lookup;
- matched random factor systems with the same degrees and output size.

## Independent Audit

The audit must reimplement canonical marker arithmetic, rebuild the public
factors from curve data, and verify the 15 coefficient polynomials without
importing compiler helpers. It must reject at least these mutations:

- one endpoint-polynomial coefficient;
- one marker-basis index or missing zero component;
- one public code assignment;
- one endpoint-specific source lookup introduced into compiler inputs;
- one operation-count component or omitted control charge;
- one local multiplicity, return-factor treatment, or sign branch;
- one claimed symbolic recurrence term.

## Decision Rule

Record a scoped positive compiler only if:

- Phase 0 proves a source-blind exact construction with
  `O(r^2 polylog r)` work and `O(r^2)` state;
- all 15 global coefficients match the exact controls;
- all P1509 local forms and source partitions replay after freezing;
- every forbidden-information and mutation audit passes; and
- the independent audit validates the symbolic and measured accounting.

Record a scoped negative if exact construction necessarily materializes cubic
state/work, uses per-endpoint opening or source advice, or violates exactness.
Record `inconclusive` or `REVISE` for an implementation failure, ambiguous
finite-size scaling, or an unproved complexity recurrence.

Even a positive P1510 result authorizes only a separately frozen complete
relation-collection experiment. The campaign's relation, blind-descent, and
end-to-end sub-rho/Shoup claims remain `not_attempted`.
