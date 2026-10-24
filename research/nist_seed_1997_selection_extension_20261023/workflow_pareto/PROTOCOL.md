# Frozen cost-proxy Pareto check

**Frozen:** 2026-10-24 UTC, before computing the new pairwise joint comparison.

## Question

Under the user's conditional assumption that every named omitted candidate was reached, could a two-step 1997 workflow choose the published curves as the nondominated options in (a) point-counting difficulty and (b) ease of certifying the resulting prime order? This is an arithmetic **process proxy**, not a runtime model, historical attribution, or ECDLP weakness test.

## Fixed inputs and identities

- `../sea_signature/runs/scan-20261023T1840Z/raw.json`, SHA-256 `4a0df1de260e4533253ef591f7b084b73e86fac5e03558ec3609081c750f48fe`: 19 full UIDs and strict Elkies-only cutoff primes, independently Sage-verified in the source study.
- `../../nist_seed_order_certificate_20261023/analysis.json`, SHA-256 `a86f488c3481519269725c1acf76e614b27f53b25f6fe23fd3b1e4fb7196c69c`: 19 matching UIDs, each with separately recorded `n−1` and `n+1` factor data.
- `../../nist_seed_skipped_curves_20261016/assessed.json`, SHA-256 `370e79ce0bff8f26bb437fe37d1756f3f8261a5c00e9062ba41cf70f272e8841`, and `traits.json` in that directory, SHA-256 `a1102bd487379d223581863fab731d6eb6957bf0e264b450f1c7b298279b0b67`: one-based ordinals and exact field identities.
- The one-based ordinals are used only to restrict to omitted candidates *earlier* than a published candidate in the same reconstructed stream. Full `curve_uid` is the join key. P-224 opposite signs count as one isomorphism class.

## Predeclared metrics and controls

For point-counting cost proxy, a lower strict Elkies-only cutoff `ℓ` is better. For primality-certificate structure, test **separately**, without fitting weights: (1) smaller largest-prime bit length required when the `n−1` Pocklington size criterion first crosses `sqrt(n)`, and (2) fewer prime-power components required at that crossing. In each two-dimensional view, an earlier omission dominates a later published curve when it is no worse on both metrics and strictly better on at least one. Ties in both dimensions do not dominate. Count all eligible same-field ordered pairs and list exact counterexamples. As a negative control, repeat each comparison using `n+1` factor data, which is not a Pocklington certificate for `n`.

The strongest possible rule in this family, “publish only candidates nondominated by an earlier qualifying candidate on both cost proxies,” fails if any earlier omission dominates a later published curve in either predeclared `n−1` view. If none dominates in a view, the view remains arithmetically consistent but is not established historically; omitted candidates might themselves have been eligible or other costs may matter. No runtime, hidden weakness, or all-eleven selector is inferred from either outcome.

## Execution and artifacts

One Python pass over the 19 immutable rows: record all 25 same-field omitted–published comparisons, mark which omissions precede each published ordinal, and apply the historical-prefix test only to that earlier subset; no optimization, parameter fitting, additional features, or recursive factoring. Require exactly 19 UIDs in both inputs and 11 omitted/8 published same-field labels. Record input digests, all pair rows, counts and control outcomes in a new JSON file. Retain analyzer, dated report, editable diagram, SVG and inspected PDF. Stop after this pass; corrections are additive.
