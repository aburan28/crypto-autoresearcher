# Exact joint-moment oracle and i.i.d. null generator — method, checks, and limits

**Task**: `TASK-20260803-6f50df` (executor) · **Batch**: `BATCH-003` ·
**Goal**: `GOAL-HQC-001` · **Question**: `RQ-HQC-001`
**Produced**: 2026-08-03 · **Repo commit at start**: `6dc0040e24a5180d69ac5bef48b60f4d7c012bcc`
(tree clean at start; dirty only in this task's own directory at run time)
**Branch**: `claude/goal-target-hqc-launch-vndegi`
**Predecessor**: `TASK-20260802-ecba30`, terminated by an API session limit — an
**infrastructure failure**, never evidence about the mathematics (`AGENTS.md`
rule 5). Nothing was carried forward from it: `oracle.py` here was written from
the A17 characterization and re-derived and re-verified from scratch. Its
unreviewed interim note about a "ring ensemble exchangeability" observation is
**not cited**; the corresponding property is established independently in §7
below, and what is established is *weaker* than full exchangeability.

**Deliverables** (all under this task directory):

| file | sha256 | lines |
|---|---|---|
| `oracle.py` | `96c54ed52af92043cd9c5569d6005235fc8886cf6f247d1a1d5f13605510cd79` | 1933 |
| `test_oracle.py` | `b3c52cc0320f34084a85da193393001a038823613bd9229fbf6d66366c6befbc` | 760 |
| `oracle_values.json` | `a3d655823945f4fe99cec11944f49206f16a2779abbfe6a15c013629d52a28e5` | — (239 178 B) |
| `oracle_report.md` | *this file* | — |

---

## 0. What this is, and what it is not — stated first, in my own words

This is a **measuring instrument for a later measurement**, not a measurement.

`oracle.py` computes the joint moment `μ_m` **exactly**, by enumeration, for
**toy configurations small enough to enumerate completely**. Its entire value
is that it is not an estimate: a Monte-Carlo estimator of `μ_m` can be pointed
at one of these configurations and its output compared against a number that
is *known*, not *sampled*.

**It says nothing whatsoever about HQC.** Not about HQC-1, HQC-3, or HQC-5;
not about the decoding failure rate; not about whether assumption A17 holds,
fails, or fails in either direction; not about HQC's security in any respect.
Every ensemble here is a toy of at most 20 coordinates. HQC-1 has
`n = 17 669` coordinates, `n_e = 46` blocks of `n₂ = 384` bits, `ω = 66`,
`ω_r = ω_e = 75`, and `m = δ_e + 1 = 16`. Three configurations below borrow
HQC-1's *dimensions* to demonstrate computational reach; they use a
**different error distribution** and a **different block decoder**, they are
labelled `not_an_hqc_quantity: true` in `oracle_values.json`, and their
numbers are not comparable to any published DFR.

Claim tier: **toy**. `certificate.kind: none` — no solve and no relation is
claimed, so there is nothing to certify. `proof_status` of the two derivations
in this document (§7 Lemma R, §6 the arithmetic-regime bound): `derivation`
— checkable arguments, never machine-checked proofs.

**No confirmatory measurement was run.** `runs_authorized` is 0 for the HQC
decoding measurement the sibling task is designing, and none was executed. The
samplers in §5 and §7 draw from *this module's own toy ensembles* and exist
solely to check the oracle against itself.

---

## 1. The object, and the indexing convention — the part most worth attacking

The red team's stated concern is exactly right: an oracle that certifies a
*different* object than the protocol estimates is worse than no oracle,
because it manufactures confidence. So the convention is stated in full and
defended against the A17 definition it must match.

### 1.1 Definitions, taken verbatim from the A17 characterization

From `…/BATCH-002/tasks/TASK-20260802-15971b/a17_characterization.md` §1:

- `ẽ ∈ F₂^{N}` with `N = n_e · n₂`, partitioned into `n_e` **disjoint
  consecutive** blocks `B_j = {j·n₂, …, (j+1)·n₂ − 1}`, `j = 0 … n_e − 1`.
- `ẽ^{(j)} = ẽ|_{B_j}`.
- `F_j = 1{D_i(ẽ^{(j)}) ≠ 0}` — inner block `j` decodes to a nonzero codeword,
  i.e. to the wrong `F₂₅₆` symbol. `F_j` is a function of `ẽ^{(j)}` alone
  (plus tie-breaking; see C4).
- `S = Σ_j F_j`; `m = δ_e + 1`.

### 1.2 The four conventions

**C1 — DISTINCT indices.** For `J ⊆ {0,…,n_e−1}` with `|J| = k`,

```
μ_k(J) := E[ ∏_{j∈J} F_j ] = P[ F_j = 1 for every j ∈ J ].
```

The indices in `J` are **distinct**, and repetition is **forbidden**. `oracle.py`
raises on a repeated index rather than silently returning a number
(`FailureLaw.mu`, asserted; pinned by
`test_oracle.TestConventions.test_repeated_indices_are_refused`).

*Why this is the load-bearing convention.* `F_j² = F_j`. A "moment" formed
over a multiset with repeats therefore collapses onto a **lower-order**
moment, which is **larger**. That is not a small numerical slip: it is an
inflation whose direction is always upward, and an inflated `μ_m` against an
unchanged `q^m` reads as **positive dependence** — the exact finding this
campaign is looking for. Mutant M1 in §5 reproduces this bug deliberately and
measures its size.

**C2 — canonical scalar = subset average = normalised binomial moment.**

```
μ_k := (1 / C(n_e,k)) · Σ_{|J|=k} μ_k(J)  =  E[C(S,k)] / C(n_e,k).
```

**C3 — unconditional.** No conditioning on the global weight of `ẽ`, on `S`,
or on anything else.

**C4 — tie-breaking.** Where the inner ML decoder ties, `F_j` is Bernoulli
with an **exact rational** parameter `φ` given the block content, with
tie-breaking independent across blocks (rider **R-tie**,
`a17_characterization.md` §3.6). A deterministic "ties count as failure"
policy is also implemented and is verified to be pointwise conservative.

### 1.3 Defence of C2 against the A17 definition

Three independent reasons, and one safeguard.

1. **A17's own form is per-subset, and the oracle reports per-subset.** A17
   primary form (§2.2) asserts *"for every `J ⊆ {0,…,n_e−1}`,
   `P[⋀_{j∈J} F_j = 1] = p_i^{|J|}`"*, and reading R3 (§3.3) asserts
   `μ_k ≤ q^k` *"for all index sets of size `k`"*. The per-subset quantity is
   therefore primary. `oracle.py` computes and reports the **full per-subset
   table** `μ_k(J)` for every one of the `C(n_e,k)` subsets whenever it is
   enumerable, together with its min, max and average. The average is a
   summary that sits **beside** the table, never in place of it. Nothing is
   averaged away silently: §7 shows the oracle detecting a case where the
   subsets genuinely differ.
2. **C2 is the quantity the tail actually depends on.** `E[C(S,m)] =
   Σ_{|J|=m} μ_m(J) = C(n_e,m)·μ_m`, and `P[S ≥ m] ≤ E[C(S,m)]` is the
   leading Bonferroni term — the same object BATCH-002's sensitivity analysis
   identified as carrying ≥ 99.9 % of Theorem 6.1's tail at published
   parameters. Under A17 it is `C(n_e,m)·p_i^m`.
3. **C2 is what an unbiased estimator estimates.** The natural
   estimator `mean_t C(S_t, m)/C(n_e, m)` is unbiased for C2 with **no**
   exchangeability assumption. C1-with-a-fixed-subset (mutant M4) is unbiased
   only if the indicators are subset-exchangeable, which is a property that
   must be checked, not assumed.
4. **Safeguard.** Under exchangeability — which A17 *asserts*, and which
   `a17_characterization.md` Lemma L1 establishes only for `k = 1` — every
   `μ_k(J)` is equal and C1 ≡ C2. The oracle **tests** subset exchangeability
   per configuration and per `k`, and reports the flag; it never assumes it.

The identity `Σ_{|J|=k} μ_k(J) = E[C(S,k)]` is verified numerically, from two
different code paths, for every configuration
(`identity_binomial_moment_vs_law_of_S` in `oracle_values.json`: **all
agree**), and is pinned by
`test_oracle.TestConventions.test_mu_bar_equals_normalised_binomial_moment`.

---

## 2. Arithmetic regime — exactly where floating point enters (DUTY 1)

**Every** moment, marginal, tail, variance and reference value is computed in
`int` or `fractions.Fraction`. There is no floating point anywhere in the
computation path, and no test, comparison or reported verdict depends on a
float. Concretely:

- Ensembles are stored as **non-negative integer weights** `w(v)` over `F₂^N`
  plus an integer denominator `D = Σ_v w(v)`. `D == sum(weights)` is asserted
  at construction for every ensemble.
- Per-block failure probabilities are integer pairs `(fail_num, scale)` with
  `φ = fail_num/scale`, so tie-splitting stays exact
  (`RM(1,2)` has `scale = 4`).
- `μ_k(J)` is `Fraction(integer numerator, D · scale^k)`.
- The ring ensemble's XOR-convolution uses an **integer** Walsh–Hadamard
  transform; the inverse transform asserts that the division by `2^N` is
  exact and that every resulting count is non-negative.
- Route B is a pure-integer convolution of binomial coefficients.

Floating point appears in exactly two reporting-only places:

1. `safe_float(fr)` — a decimal rendering. It returns `None` on
   overflow/underflow rather than the silent `0.0` that `float()` gives for,
   e.g., `2^-2000` (pinned by
   `test_oracle.TestExactHelpers.test_safe_float_underflow_is_none_not_zero`).
2. `log2_fraction(fr)` — a base-2 logarithm for readability, and the
   `standard_error` / `z_score` of the Monte-Carlo self-tests in §5 and §7.

**Error bound for `log2_fraction`, derived.** For a positive integer `x` with
bit length `B > 64`, write `x = 2^{B−64}·t + s`, `t = x >> (B−64) ∈ [2^63,
2^64)`, `0 ≤ s < 2^{B−64}`. Then

```
log2(x) = (B−64) + log2(t) + log2(1 + s/(t·2^{B−64})),
```

and the third term is at most `log2(1 + 1/t) ≤ 1/(t ln 2) < 2^{−63}/ln 2 <
1.6·10^{−19}`. The float conversion of `t < 2^64` has relative error
`≤ 2^{−53}`, contributing `≤ 2^{−53}/ln 2 < 1.6·10^{−16}` to the logarithm;
`math.log2` itself contributes at most one ulp of a result of magnitude
`≤ 64`, i.e. `< 7.2·10^{−15}`. The additions and the final subtraction round
at `ulp(M)/2` for a result of magnitude `M`. For `|log₂| < 10^4` — the whole
range in `oracle_values.json`, whose largest integer is under `10^4` bits —
the total absolute error is **below `10^{−9}`**, and in practice below
`10^{−11}`. Pinned by
`test_oracle.TestExactHelpers.test_log2_is_reporting_only_and_accurate`
(exact powers of two return exactly, agreement with `math.log2` to 8 places).

---

## 3. Method — design for tractability, chosen before the configurations

The predecessor's last recorded act was to conclude its enumeration core was
too slow and begin a rewrite. This implementation picks the representation
first. Three layers plus a second route:

**Layer 1 — `AtomLaw`.** An exact law on `F₂^N` as integer weights plus a
denominator. Every ensemble used here — i.i.d. Bernoulli`(a/b)`, uniform fixed
weight, finite mixtures, explicit block products, and the HQC-shaped ring
product — is representable this way with **integers only**, so there is one
generic enumeration path rather than one per ensemble.

**Layer 2 — `BlockModel`.** `content ↦ (fail_num, scale)`. Implemented:
a bounded-distance weight threshold; `RM(1,mm)` with a **maximum-likelihood**
(exhaustive minimum-distance) decoder and either tie policy; and a
hand-specified truth table for tests.

**Layer 3 — `FailureLaw`, the collapse that makes this cheap.** A block's
failure value depends only on that block's content, and a block model takes
at most `V` distinct values. Pushing the atom law forward therefore collapses
`2^N` atoms onto at most `V^{n_e}` **signatures** — 32 signatures for the
`N = 20` configurations here. After one pass over the atoms, *all* `μ_k(J)`
for *all* subsets, the full law of `S`, every tail, and the exact estimator
variance are read off that small table. The signature array itself is built
digit-wise by list comprehension over blocks rather than by a per-atom Python
loop.

**Route B — the closed integer form that escapes `2^N` entirely.** For an
ensemble that is *uniform fixed weight globally* and, conditional on the block
weight profile, *uniform within blocks and independent across them*:

```
μ_k = [ Σ_t G_k(t) · C((n_e − k)·n₂, w − t) ] / ( C(N, w) · scale^k ),
```

where `G_k` is the `k`-fold convolution of the integer sequence
`A_j = Σ_{patterns of weight j} fail_num`, truncated at `w`. Pure integers,
cost `O(k · w · n₂)`, **independent of `2^N`**.

**Route B's precondition is stated because it is the one structural fact the
oracle uses rather than enumerating.** It holds exactly for the uniform
fixed-weight ensemble and for i.i.d. Bernoulli coordinates. It does **not**
hold for the ring ensemble, and Route B is never applied there. Where both
routes run, they are cross-checked and agree exactly
(config `A3`, `all_agree: true`; `test_oracle.TestRoutesAgree`, four
parameter sets plus a rational-`φ` case). A guard test also asserts Route B
does **not** return `q^k` on a fixed-weight ensemble, so a Route B that had
silently degenerated to the i.i.d. formula would fail.

---

## 4. The i.i.d. null generator, and the analytic-null agreement (DUTY 3)

### 4.1 What "independent by construction" means here

Three structurally different constructions of an independent null are
implemented, so that a bug shared between the null and the thing it controls
would have to be present in all three:

1. **Coordinate-level** (`atomlaw_iid_bernoulli`) — every one of the `N`
   coordinates is an independent Bernoulli`(p)`; blocks are disjoint, so block
   outcomes are independent as a *consequence of the construction*. This law
   is then pushed through the **same generic enumeration** as every dependent
   ensemble, so the null's `μ_k` is *computed*, not asserted.
2. **Explicit block product** (`atomlaw_product_blocks`) — the law is built as
   a literal product of per-block laws.
3. **Indicator-level** (`fl_iid_indicator`, and the `IIDNullGenerator`
   sampler) — `n_e` independent Bernoulli`(p_i)` indicators with matched
   `n_e`, block structure and marginal.

### 4.2 The check the duty asks for: does the enumerated null equal `p_i^m`?

**Yes, exactly, for every configuration and every `k`, per subset and on
average.** Equality is exact rational equality (`==` on `Fraction`), not
agreement to some tolerance.

| null configuration | `n_e` | `n₂` | `N` | block model | `p_i` (exact) | `μ_k = p_i^k` for all `k` | every subset equals `p_i^k` |
|---|---|---|---|---|---|---|---|
| `A1-null-iid-bernoulli-threshold` | 5 | 4 | 20 | threshold `t=1`, `p=1/4` | `67/256` | **yes**, `k=1…5` | **yes** |
| `A2-null-iid-bernoulli-rm12-tiesplit` | 5 | 4 | 20 | `RM(1,2)` ML, tie-split, `p=1/3` | `19/27` | **yes**, `k=1…5` | **yes** |
| `B3-iid-indicator-null` | 8 | — | — | indicator level, `p=1/10` | `1/10` | **yes**, `k=1…4` | **yes** |
| product-of-blocks (test suite) | 4 | 3 | 12 | threshold `t=1`, `p=1/4` | `5/32` | **yes**, `k=1…4` | **yes** |

Worked instance (`A1`), all values exact:

```
p_i        = 67/256
μ_1        = 67/256                       = p_i^1   ✓
μ_2        = 4489/65536                   = p_i^2   ✓
μ_3        = 300763/16777216              = p_i^3   ✓
μ_4        = 20151121/4294967296          = p_i^4   ✓
μ_5        = 1350125107/1099511627776     = p_i^5   ✓
```

The marginal `p_i` itself is cross-checked against an independent closed form
`p_i = Σ_j A_j·p^j·(1−p)^{n₂−j}/scale` that touches none of the enumeration
machinery (`marginal_agrees: true`).

**This is the test that would have caught the oracle.** Had the enumeration,
the signature collapse, the rational-`φ` handling, or the denominator
bookkeeping been wrong, the null would have missed `p_i^k` — and it does not,
for `k` up to 5, on two different block models, one of which has `φ ∉ {0,1}`.

---

## 5. Known-answer tests at all three signs, and the mutants (DUTY 4)

`python3 test_oracle.py` — **43 tests, all pass**, in 4.2 s. It prints a
known-answer table: **49 comparisons that must agree, 49 agree exactly; 9
mutant comparisons that must differ, 9 detected.**

### 5.1 Known-answer values (all exact; "expected" from an *independent* source)

The `expected` column comes from a closed form derived on paper and
implemented without touching `AtomLaw`, `FailureLaw`, or Route B, or from a
Fraction-only brute-force implementation of the definition (`bf_mu`).

| sign | mechanism | `k` | expected | observed | verdict |
|---|---|---|---|---|---|
| independent | i.i.d. Bernoulli + threshold, `p=1/4` | 3 | `125/32768` | `125/32768` | agree |
| independent | i.i.d. Bernoulli + threshold, `p=2/5` | 4 | `3748096/244140625` | `3748096/244140625` | agree |
| independent | i.i.d. Bernoulli + `RM(1,2)` tie-split | 3 | `6859/19683` | `6859/19683` | agree |
| independent | i.i.d. indicators, `p=3/13` | 6 | `729/4826809` | `729/4826809` | agree |
| independent | explicit product of independent blocks | 4 | `625/1048576` | `625/1048576` | agree |
| **negative** | occupancy, `N=12`, `w=5` (inclusion–exclusion) | 2 | `91/132` | `91/132` | agree |
| **negative** | occupancy, `N=12`, `w=5` | 4 | `9/22` | `9/22` | agree |
| **negative** | exactly-`c`, `n_e=7`, `c=3` (`C(n_e−k,c−k)/C(n_e,c)`) | 3 | `1/35` | `1/35` | agree |
| **negative** | fixed weight + threshold (Route B reference) | 3 | `9/308` | `9/308` | agree |
| **positive** | latent mixture `p∈{1/8,1/2}`, `λ=1/3` | 3 | `1398545/16777216` | `1398545/16777216` | agree |
| **positive** | latent mixture, same | 4 | `178961851/4294967296` | `178961851/4294967296` | agree |
| **positive** | comonotone, `p=1/7` (`μ_k = p` ∀k) | 6 | `1/7` | `1/7` | agree |
| **positive** | mixture of two *negatively* dependent fixed-weight laws | 3 | `17/55` | `17/55` | agree |

The full 49-row table is printed by `test_oracle.py`; every row is exact
equality.

Sign checks are asserted, not merely observed: sampling without replacement
must satisfy `μ_k < q^k` strictly for `k ≥ 2`, and a latent mixture must
satisfy `μ_k > q^k` strictly by Jensen. Both are `assert`ed in the suite.

### 5.2 A dependent object exhibiting *both* mechanisms

Configuration `A6` and `test_mixture_of_negative_components_is_positive`
construct a mixture of two uniform fixed-weight ensembles. Each component is
**negatively** dependent (`μ_k ≤ q_i^k`, verified) and the mixture over the
latent global weight is **positively** dependent (`μ_2 = 4961/16796 >
q̄² = 178084/938961`, verified). This is the shape `EV-HQC-6fd5b1` O-6
describes — two mechanisms of opposite sign in one object. **It is a property
of this toy construction and is not evidence about HQC or about which
mechanism dominates there.** Its role here is to prove the instrument
resolves both signs in a single ensemble rather than only in separate ones.

### 5.3 Mutants — the failure mode that looks like signal

Four plausible wrong ways to form the `m`-th joint moment. Their expectations
are computed **exactly** from the exact law of `S`, so the mutant analysis is
itself not sampled.

`m = 3` throughout; "reads as" is what a naive reader comparing the mutant to
`q^m` would conclude.

| ensemble (true sign) | truth `μ_3` | M1 with replacement | M1 / truth | M1 reads as | misleads? |
|---|---|---|---|---|---|
| `A1` null (**independent**) | `300763/16777216` | `5447569/104857600` | **×2.898** | **positive** | **YES** |
| `A3` fixed weight (**negative**) | `9/1615` | `6454/121125` | **×9.561** | **positive** | **YES** |
| `A5` mixture (**positive**) | `22364172763/137438953472` | `7159300153/34359738368` | ×1.280 | positive | no (sign right, size wrong by 28 %) |
| `R1` ring (**negative**) | `26464611/125772800` | `150479463/473497600` | ×1.510 | **positive** | **YES** |

**This is the concrete statement of the danger.** On a *perfectly
independent* ensemble the with-replacement mutant returns a value **2.9×**
`p_i^m`; on a *negatively dependent* one it returns **9.6×** the truth and
inverts the sign. Without an oracle, either would be reported as "positive
inter-block correlation found". All four are detected: the mutant value
differs from the exact truth in every case.

The remaining mutants, all detected, all biased **downward** by a constant
combinatorial factor:

| mutant | error | on `A1` |
|---|---|---|
| M2 — ordered distinct tuples, denominator `n_e^m` instead of `n_e^{(m)}` | ×`n_e^{(m)}/n_e^m` | ×0.48 |
| M3 — correct `C(S,m)` count, denominator `n_e^m` instead of `C(n_e,m)` | ×`1/m!` | ×0.08 |
| M4 — one fixed subset `{0,…,m−1}` instead of the average | exact iff subset-exchangeable | ×1.000 on `A1`; **×1.0000187 on the ring `R1`** |

M4 is the reason §7 matters: it is invisible on every exchangeable ensemble
and only appears once a non-exchangeable one is in the suite.

### 5.4 Sampler-versus-oracle self-tests

Deterministic given the recorded seeds. `z` uses the **exact** per-sample
variance computed from the exact law of `S`.

| what | samples | exact value | estimate | `z` | verdict |
|---|---|---|---|---|---|
| i.i.d. null, indicator level, `n_e=8`, `p=1/4`, `m=3`, seed 20260803 | 200 000 | `1/64` | `87071/5600000` | **−0.844** | within 4σ |
| the same mutant M1 estimator | 200 000 | (truth `1/64`) | `1769307/51200000` | **+208.6** | detected |
| i.i.d. null, coordinate level, `n_e=5`, `n₂=4`, `p=1/4`, `m=3`, seed 20260804 | 200 000 | `300763/16777216` | `35733/2000000` | **−0.396** | within 4σ |
| **ring ensemble `R1`** (dependent), `m=3`, seed 20260814 | 200 000 | `26464611/125772800` | `33707/160000` | **+0.358** | within 4σ |

The last row is the answer to the red team's question in its sharpest
available form: a **direct sampler of the ring ensemble** — one that draws
`x, y, r₁, r₂, e` as fixed-weight vectors, forms `x·r₂ + r₁·y + e` in
`F₂[X]/(X^n−1)`, truncates, and decodes each block — converges to the
**same** number the oracle computes exactly by enumeration, on a *dependent*
ensemble, not merely on the null. The oracle and a sampling estimator are
targeting the same object.

---

## 6. Determinism and reproduction (DUTY 5)

```sh
cd coordination/goals/GOAL-HQC-001/batches/BATCH-003/tasks/TASK-20260803-6f50df
python3 oracle.py --out oracle_values.json --seed 20260803     # ~21 s
python3 test_oracle.py                                          # ~4 s, 43 tests
```

- **Python** 3.11.15 (CPython), `Linux-6.18.5-x86_64-with-glibc2.39`.
- **Third-party dependencies: none.** Standard library only: `fractions`,
  `itertools`, `math`, `random`, `json`, `hashlib`, `platform`,
  `subprocess`, `argparse`, `time`, `os`, `sys`.
- **Randomness**: one source, `random.Random(seed)` (Mersenne Twister),
  seed `20260803`, consumed in a fixed order. Derived seeds: `+1` for the
  coordinate-level null sampler, `+11` for the ring sampler. Randomness is
  used **only** by the samplers in §5.4; every `μ_k`, tail, variance and
  reference value is deterministic exact arithmetic and does not consult the
  RNG at all.
- **Reproducibility verified**: two independent runs of the same `oracle.py`
  with the same command and seed produce **byte-identical** JSON once the
  wall-clock timing fields are removed. Checked explicitly; the *only* keys
  that differ between runs are `results.timings` and the per-row `seconds`
  entries in `reach_demonstrations` and `measured_scaling`. Every computed
  value, every verdict flag, and `provenance.command` are identical.
- Git commit and dirty-tree state are recorded inside `oracle_values.json`
  (`provenance`), along with the sha256 of `oracle.py` at run time. No
  state-mutating git command was run.

**Inference block** (per the harness model-policy note):

```yaml
inference:
  requested_policy: executor-implementation
  resolved_model_id: claude-opus-5
  fallback_used: true
  model_verified: false
  independent_session: true
```

`fallback_used: true` because no policy alias in
`orchestration/model-policies.yaml` resolves under this harness; the resolved
model is the session model. This is recorded, not silently substituted.

---

## 7. What the oracle found about its own ring configurations — flagged *and resolved*

`BATCH-003-OPENING.md` §5 adds a **flag-without-resolution gate**: a flagged
discrepancy must be resolved, or recorded as open with a named successor. One
discrepancy arose. It is resolved here.

**Observation.** In every HQC-shaped ring configuration, `μ_2(J)` is **not the
same for all pairs `J`**. Example, `R2` (`n = 16 = n_e·n₂`, `n_e = 4`,
`n₂ = 4`, threshold `t = 1`), exact:

```
μ_2({0,1}) = μ_2({1,2}) = μ_2({2,3}) = μ_2({0,3}) = 1482597/3920000     (adjacent)
μ_2({0,2}) = μ_2({1,3})                           = 100175981/264600000 (opposite)
```

So `subset_exchangeable` is `false` at `k = 2`. This *would* be alarming: it
is the property C2's safeguard depends on, and it is what A17 asserts.

**Resolution — Lemma R, derived and then verified.**

> *Lemma R.* Let `x, y, r₁, r₂, e` be independent and uniform on their
> fixed-weight sets in `R = F₂[X]/(X^n − 1)`, and `e′ = x·r₂ + r₁·y + e`.
> The fixed-weight sets are invariant under cyclic shift and ring
> multiplication commutes with shift, so the law of `e′` is invariant under
> the cyclic group of order `n`. `B_{j+1}` is the translate of `B_j` by `n₂`.
> Hence `μ_k(J) = μ_k(J+1)` whenever every shifted index still lies in
> `{0,…,n_e−1}`; and when `n = n_e·n₂` exactly, shifting by `n₂` is a genuine
> **cyclic permutation of the blocks**, so `μ_k` is constant on **cyclic
> orbits** of `k`-subsets. ∎

The acting group is therefore the cyclic group `C_{n_e}`, **not** the full
symmetric group. Non-exchangeability at `k = 2` is exactly what Lemma R
predicts: the six pairs of a 4-block ring fall into **two** cyclic orbits
(adjacent, opposite), so at most two distinct values are permitted, and at
`k = 1, 3, 4` there is one orbit and one value.

**Verification, in `oracle_values.json`:**

| configuration | shift equivariance | cyclic-rotation invariance | `k` | orbits | distinct `μ_k` values |
|---|---|---|---|---|---|
| `R2` (aligned, `n = 16`) | holds, 7/7 | holds | 1 | 1 | 1 |
| | | | 2 | **2** | **2** |
| | | | 3 | 1 | 1 |
| | | | 4 | 1 | 1 |
| `R1`, `R3` (truncated, `n = 17`) | holds, 7/7 | n/a (truncated) | 2 | — | 3 |
| `R4` (truncated, `n = 19`) | holds, 3/3 | n/a | 2 | — | 2 |

The orbit count and the distinct-value count match exactly in the aligned
case. `test_oracle.TestSubsetExchangeability` pins both the shift equivariance
and the oracle's ability to *detect* the non-exchangeability rather than
average it away.

**Consequences, stated plainly.**

1. The predecessor's unwritten "ring ensemble exchangeability" note, whatever
   it said, is **not** supported as full exchangeability by anything computed
   here; what holds is the strictly weaker **cyclic** equivariance of Lemma R.
   It is not cited anywhere in this package.
2. C2 remains well defined and remains what an unbiased estimator targets —
   this is precisely why C2 was chosen over "pick a subset".
3. A protocol that estimates `μ_m` from **one fixed block subset** would be
   biased on a non-exchangeable ensemble. Measured here: mutant M4 on `R1` is
   off by a factor `1.0000187`. Small at these toy parameters; the point is
   that it is **not zero**, and the oracle sees it.
4. **This says nothing about HQC.** Whether HQC's actual `ẽ` at `n = 17 669`
   with `n_e = 46` is or is not subset-exchangeable is not addressed, not
   measured, and not asserted here. Lemma R is about the toy ring
   configurations in this file. *Nothing open is left dangling: the discrepancy
   is resolved, and its scope limit is stated.*

---

## 8. Limits, honestly (DUTY 6) — the part the sibling feasibility task needs

### 8.1 Largest configuration actually reached, per route

| route | ensemble class | largest reached here | wall clock | binding cost |
|---|---|---|---|---|
| **A** full atom enumeration | any | `N = 20` (`n_e = 5`, `n₂ = 4`), `2^20 = 1 048 576` atoms, `k` to 5 | 0.35 s | `Θ(2^N)` time **and** memory |
| **A** ring ensemble | HQC-shaped ring on space (T) | `n = 19`, `N = 18` (`n_e = 3`, `n₂ = 6`), `m ≤ 3`; and `n = 17`, `N = 16`, `n_e = 4`, `m ≤ 4` | 4.6 s / 0.66 s | `C(n,ω)·C(n,ω_r)` ring products **+** `Θ(N·2^N)` WHT |
| **B** integer convolution | uniform fixed weight, block-exchangeable | `n_e = 100`, `n₂ = 1024`, `N = 102 400`, `w = 200`, `m = 30` | 0.13 s | `O(m·w·n₂)`, independent of `2^N` |

Measured Route A scaling (i.i.d. Bernoulli + threshold): `N = 8` → 0.000 s,
`N = 12` → 0.001 s, `N = 16` → 0.021 s, `N = 20` → 0.350 s. Each `+1` in `N`
roughly doubles both time and memory. **Extrapolated, not measured:** at that
doubling rate `N = 24` would be of order 6 s and a few hundred MB, and
`N = 30` is out of reach on memory alone. Those two figures are estimates and
are labelled as such; the four timings above are measurements. The hard cap in
code is `ENUM_MAX_N = 22`, which refuses rather than thrashes.

Measured ring-law scaling: `n = 13, N = 12` → 0.056 s (22 308 ring products);
`n = 17, N = 16` → 0.657 s (92 480); `n = 19, N = 18` → 4.6 s (938 961).
Truncating *before* convolving (legitimate because coordinate restriction is a
group homomorphism, so the pushforward of an XOR-convolution is the
convolution of the pushforwards) is what decouples `n` from `N` and makes
`n > N` affordable; without it the WHT would be `2^n`.

### 8.2 The gap, stated without softening

**The oracle reaches configurations far smaller than any useful measurement of
HQC, and the gap is large in three separate directions at once.**

| quantity | HQC-1 | oracle's faithful (ring) reach | gap |
|---|---|---|---|
| coordinates `N` | 17 664 (`n = 17 669`) | 18 | ~10³ |
| blocks `n_e` | 46 | 4 | ~10 |
| block length `n₂` | 384 | 6 | ~60 |
| moment order `m = δ_e+1` | 16 | 3–4 | ~4–5 |
| error weights `ω, ω_r, ω_e` | 66, 75, 75 | 3, 3, 3 | ~20 |
| inner code | duplicated `RM(1,7)` `[384,8,192]` | `RM(1,2)` `[4,3,2]` or a weight threshold | not the same code |

**Concealing this would corrupt the sibling's feasibility decision, so it is
stated first and plainly: the exact oracle cannot validate an estimator at
anything approaching HQC-relevant parameters on the faithful ensemble.**

What it *can* do, and what it is therefore for:

- validate an estimator's **combinatorics and code path** — the distinct-index
  convention, the subset normalisation, the tail/leading-term bookkeeping, the
  handling of tie-breaking randomness, and the null construction — all of
  which are parameter-independent and transfer verbatim to any size;
- supply an **exact ground truth at all three dependence signs**, so a
  candidate estimator can be shown to be unbiased on independent, positively
  dependent and negatively dependent ensembles before it is trusted on an
  unknown one;
- supply an **i.i.d.-by-construction null object** with matched `n_e`, block
  structure and marginal, in three constructions, with its exact `μ_m` known
  to be `p_i^m`;
- supply **exact estimator variances**, hence exact sample-size requirements
  (§8.4).

It cannot certify that an estimator behaves correctly at `n_e = 46`,
`n₂ = 384`, `m = 16` on HQC's actual `ẽ`. Nothing here does that, and no
extrapolation from these sizes to those is licensed (`AGENTS.md` rule 7).

### 8.3 Where the reach is *not* the bottleneck — a useful narrowing

Route B computes `μ_m` **exactly at HQC-1's dimensions in milliseconds** for a
uniform-fixed-weight ensemble with a threshold block decoder:
`n_e = 46`, `n₂ = 384`, `N = 17 664`, `w = 75`, `m = 16` in **≈ 3 ms**
(0.0029–0.0032 s across runs), where Route A would need `2^17664` atoms. Two such rows (`t = 3` and `t = 5`) are in
`oracle_values.json`.

**These are `not_an_hqc_quantity: true` and must not be read as HQC numbers.**
The ensemble is uniform fixed weight over `N` coordinates, which is *not* the
law of HQC's `ẽ = x·r₂ + r₁·y + e`; the block decoder is a bounded-distance
weight threshold at an arbitrarily chosen `t`, which is *not* HQC's duplicated
Reed–Muller ML decoder. Only the dimensions coincide. (At `t = 5` the exact
value is `0` — sixteen blocks each needing ≥ 6 errors cannot be supplied by a
global weight of 75 — which is a combinatorial fact about that toy model and
nothing else.)

The useful, transferable conclusion is a **narrowing of where the difficulty
lies**: the `m`-way moment *combinatorics* are cheap even at HQC's dimensions.
What is expensive is the joint law of `ẽ` on the true space (T) — the ring
product of fixed-weight vectors — and the inner ML decoder's exact per-pattern
failure profile. Any future exact work should attack those two, not the
moment bookkeeping.

### 8.4 Exact sample-size requirements for the canonical estimator

Exact per-sample variance of `C(S,m)/C(n_e,m)` under an i.i.d. null
(`S ~ Binomial(n_e, p)`), and the exact `T` for a 10 % relative standard
error. `n_e` and `m` are free parameters and `p` is swept over hypothetical
values. **No HQC marginal is asserted or used**; this is a property of the
estimator, offered as input to the feasibility analysis.

| `n_e` | `m` | `p` | `μ_m = p^m` | `T` for 10 % rel. s.e. | `log₂ T` |
|---|---|---|---|---|---|
| 8 | 3 | 1/4 | 1.56e−2 | 675 | 9.4 |
| 8 | 3 | 1/100 | 1e−6 | 2 058 847 | 21.0 |
| 16 | 6 | 1/10 | 1e−6 | 205 699 | 17.7 |
| 16 | 6 | 1/100 | 1e−12 | 2.09e10 | 34.3 |
| **46** | **16** | 1/2 | 1.53e−5 | 8 442 | 13.0 |
| **46** | **16** | 1/4 | 2.33e−10 | 2 380 032 | 21.2 |
| **46** | **16** | 1/10 | 1e−16 | 2.23e10 | **34.4** |
| **46** | **16** | 1/100 | 1e−32 | 1.40e23 | **76.9** |
| **46** | **16** | 1/1000 | 1e−48 | 1.55e38 | **126.9** |

Read plainly: a direct Monte-Carlo estimate of a 16-way joint moment at
`n_e = 46` is cheap only while the per-block marginal is large. The sample
requirement grows like `p^{−m}` once `μ_m` is small, and by `p = 10^{−2}` it
is already `2^77`. **This is a statement about the estimator's variance under
an i.i.d. null, not a claim about HQC's marginal, which is not measured
here.** Whatever reduced parameters the sibling protocol selects, this table
is the arithmetic that governs whether direct estimation is affordable there.

### 8.5 Other limits and deviations, recorded rather than omitted

1. **`R2` uses `n = 16`, which is not prime.** HQC requires `n` to be the
   smallest primitive prime above `n₁n₂`. `R2` sets `n = n_e·n₂` deliberately
   so that block rotation is exact and Lemma R's cyclic case can be tested;
   the price is that `X^16 − 1 = (X+1)^16` over `F₂`, a degenerate ring. `R1`,
   `R3` (`n = 17`) and `R4` (`n = 19`) use primes with truncation, which is the
   faithful shape (assumption A23).
2. **No duplicated Reed–Muller code.** HQC's inner code is `RM(1,7)`
   duplicated to `[384,8,192]`. Only plain `RM(1,mm)` is implemented, at
   `mm = 2, 3`. Duplication changes the weight profile and is *not* modelled.
3. **The inner decoder is exhaustive minimum-distance search**, not SPEC
   §3.4.3's Hadamard-transform decoder. These compute the same function (ML
   decoding), and the exhaustive version was chosen because for a correctness
   instrument, clarity beats cleverness. It is verified against coding theory:
   `RM(1,3) = [8,4,4]` gives `φ = 0` at weight ≤ 1, `φ = 3/4` at weight 2 (a
   4-way tie including the zero codeword), `φ = 1` at weight ≥ 3 — pinned as a
   test.
4. **The leading Bonferroni term is not tight at toy parameters.** On `R1`,
   `P[S ≥ 3] / (C(4,3)·μ_3) = 0.565`, because the toy marginal `q ≈ 0.60` is
   enormous. At HQC's published parameters BATCH-002 computed the leading term
   carrying ≥ 99.9 %. So the toy configurations do **not** reproduce the
   regime in which `μ_m` alone determines the tail, and no inference from
   these tails to that regime is licensed. (On `A3` the ratio is exactly 1
   because `μ_4 = μ_5 = 0` terminates the inclusion–exclusion.)
5. **`ENUM_MAX_N = 22` and `ENUM_MAX_BLOCK = 18`** are hard refusals, not
   warnings; oversized configurations raise `ValueError` (tested).
6. **Route B's structural precondition** (§3) is a genuine assumption about
   the ensemble class, not raw enumeration. It is stated at the function, it
   is exactly true for the ensembles it is applied to, and it is cross-checked
   against Route A wherever both run. It is never applied to the ring.
7. **The RNG is Python's Mersenne Twister**, which is not cryptographically
   strong. It is used only for the oracle's own self-tests, never for an
   exact value. A protocol needing high-quality sampling should say so
   separately.

---

## 9. Scope statement

- **No security claim about HQC in either direction**, and no statement about
  whether A17 holds, fails, or fails in a particular direction. That question
  is untouched by this file.
- **No confirmatory measurement was run.** `runs_authorized: 0` was respected.
  The samplers here draw from this module's own toy ensembles.
- **Claim tier: toy.** `certificate.kind: none`.
- **Not admissible toward the `AGENTS.md` rule 13 closure quorum**: this is an
  independent *session* on the same backend as every other task in this goal.
- **No toy-to-crypto extrapolation.** §8.2 states the gap in the terms it
  actually has.
- **Writes**: only the four files in this task directory. No ledger record, no
  knowledge entry, no experiment directory, no queue, no sibling or
  predecessor artifact was created or modified. No `__pycache__` is left
  behind. No state-mutating git command was run.
- **Every number in `oracle_values.json` is produced by code in `oracle.py`**
  that a reviewer can re-run with the command in §6; none is transcribed,
  estimated, or asserted by hand.
