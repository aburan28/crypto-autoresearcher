# Prime-field divisor fit and a target-blind high-arity base candidate

**Status:** exact input-preparation and correctness observations, 2026-10-17 UTC. This is a substantive factor-base search round, not an ECDLP run, degree-of-regularity measurement, or speed claim. The [editable chart source](2026-10-17-icperf-divisor-fit-chart.py), [SVG](2026-10-17-icperf-divisor-fit.svg), and [PDF](2026-10-17-icperf-divisor-fit.pdf) show exact divisor eligibility. The [machine-readable table](../../research/icperf_explicit_divisor_20261017/divisor_fit.json) and [base record](../../research/icperf_explicit_divisor_20261017/n63_m8_subgroup_seed20261017.json) are the primary artifacts.

## Exact field constraint

For the [three certified public prime curves](2026-10-17-icperf-prime-fixture.md), Sage factored `p−1` and proof-checked each prime factor. The table uses the prime implementation's `default_fb_size(N,m)` and chooses the exact divisor `d | p−1` nearest `2B`, with ties toward smaller `d`. The plotted gap is `|d−2B|/(2B)`. It is a **field eligibility** diagnostic: a close divisor does not ensure exactly `B` lifted curve points, a sparse descended system, or a useful relation. The source program is [icperf_divisor_fit.py](../../tools/icperf_divisor_fit.py), SHA-256 recorded in the JSON; all arithmetic rows have explicit numerator and denominator.

| Field | Factorization of `p−1` | Cells with nearest `d` within 15% of `2B` | Important misses |
| --- | --- | --- | --- |
| 50 bits | `2^7 · 179 · 2377 · 20673193` | `m=3,4,5` | `m=2,6,7,8` |
| 53 bits | `2 · 3 · 1501199800786417` | none of `m=2…8` | Nearest small divisor is `6` for every row; the fixed 53-bit curve cannot host this matched-size coset base. |
| 63 bits | `2^7 · 5 · 7 · 31 · 197 · 337119436319` | `m=3,4,5,6,7,8` | `m=2` |

The 63-bit `m=8` cell has default `B=406`, nearest `d=788`, and exact relative divisor gap `24/812 = 2.96%`. On the same field, `m=7` has `B=784`, `d=1576`, gap `8/1568 = 0.51%`. These numbers describe divisors and formulas, not realized base size. The 53-bit failure is scoped to this *fixed field* and the coset equation `x^d = g^d`; it does not obstruct small-x/random bases, other sparse equations, or selection of a different 53-bit field. Choosing a field for a favorable divisor incurs construction and rejected-candidate cost.

## Exact explicit-divisor construction

The [factor-base implementation](../../src/crypto_autoresearcher/index_calculus/factor_base.py) now accepts an explicit divisor for subgroup and Dickson bases. It checks `d | p−1`, factors only `d`, samples `ζ = h^((p−1)/d)`, and rejects `h` unless `ζ^(d/q) != 1` for every prime `q | d`. Thus `ζ` has exact order `d`; `g, gζ, …, gζ^(d−1)` enumerates the full coset without trial-factoring the wide `p−1` or finding a primitive root of the entire field. Legacy calls without an explicit divisor retain their existing path. Tests checked exact order, complete coset membership, Dickson's `D_d(x,c)=λ` identity, malformed divisors, a guard that fails if the old full-field path is invoked, and the public 63-bit fixture. Eight selected legacy subgroup/Dickson tests also passed.

One fixed, target-blind candidate was prepared with `kind=subgroup`, `d=788`, requested `B=406`, seed `20261017` on the certified 63-bit curve. It realized **380** distinct on-curve x-coordinates, so future controls must use **380**, the realized count. Its coset seed, exact-order `ζ`, one root draw, every affine point, fixture/source digests and point SHA-256 `8ab6c8f1f9da8eda141349b128fbeac379e1c40dd1ef42b6d0695ff3bc545a39` are in the base record. The independent record checker regenerated all 788 coset x-values, lifted them, compared the ordered 380-point list, and rejected a deliberately altered point. Its membership equation has exactly the two nonzero terms `x^788 − g^788` over this field. **Two input terms do not establish a low degree of regularity or faster solving.**

The base record's `preparation.wall_seconds` (about 0.053 s) times only the constructor call in that process. It excludes interpreter startup, fixture generation, exact `p−1` factorization and later search for alternative seeds; its peak RSS is process-level. The host load average was about 56 at the end. These diagnostics are not a controlled cold-start timing or a full setup ledger. A scientific trial must charge every one-time stage or declare and verify actual reuse across targets.

## Stage table and next discriminating comparison

| Stage | Current evidence | Remaining requirement |
| --- | --- | --- |
| Curve and field selection | Three exact prime-order fixtures; exact `p−1` factorizations and rejected curve prefixes. | A predeclared field-selection population and charged search, especially for a 53-bit sparse-coset arm. |
| Factor-base construction | One fully replayed 63-bit `m=8` coset candidate of realized size 380; membership polynomial has two terms. | Equal-realized-size random/small-x controls and a target-blind training/holdout split; full cold and amortized setup accounting. |
| Decomposition and algebra | No `m=8` trial on this base. | Planted correctness, direct `S_8` capacity as the seven-summand case, eight-summand `S_9` or chained `S_3`, actual input support and observed solving degree. |
| Relations, rank, target and rho | No measurement on this candidate. | Unplanted relation yield, duplicate/useful-rank accounting, linear algebra, unseen same-point target recovery, independent replay and matched rho. |

The cheapest falsifier for this candidate is exact planted and unplanted decomposition on the archived 380-point base and size-matched controls, stopping before a complete-cost panel if its solver representation or rank yield fails the frozen gate. The [full-width obstruction](../../problems/full-width-ic-arity-grid-unmeasured.md) remains open. The configured Coordinator backend is still unverified, so this preparation does not approve or launch that scientific protocol.

**Graph custody:** the [canonical ECDLP frontier index](../../knowledge/frontiers/ecdlp/README.md) was checked. No reviewed complete-cost finding changes, so its graph source and rendering remain unchanged. The chart here reports exact field-divisor fit only.
