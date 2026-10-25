# Experiment spec (awaiting approval): prime-field decomposition-oracle order census

- **approved_by:** null
- **RQ:** RQ-ECDLP-361f3a
- **Idea:** IDEA-20261024-a2b05d (advances LEAD-ICE-generic-oracle-arity-cost-floor; sharpens LEAD-ICE-charged-toy-ic-exponent-vs-rho and LEAD-ICP-generic-table-decomposition `revisit_when`)
- **Claim class:** comparative / statistical (an exponent fit per arm), with one exact-computation control (the instrumented `B^1` oracle)
- **Repository that runs it:** `aburan28/crypto` (Rust, ecbench); records land in `crypto-autoresearcher` through the usual evidence path
- **Tier:** toy (fields <= 32 bits); nothing here is cited at cryptographic size
- **Status of this document:** a spec for the experiment-director; not compiled, relayed or run in the authoring session (hard rule 3)

## 1. Question and decision rule

For every decomposition oracle implemented for prime-field `ic.pipeline`, measure the
enumeration order `k` (fitted slope of log GAE-per-attempt against log B at fixed
arity m) and its return semantics (all decompositions of the target vs the first
one), and place it against the threshold line of the Lean theorem
`CryptoResearch.IC.ArityOracleThreshold`:

| semantics | sub-generic in the model iff |
|---|---|
| all-decompositions | `k < (m-1)/2` (and `m > k+3` when `k <= 2`) |
| one-decomposition | `k < m/2 - 1` |

**Primary metric.** `k_hat(arm, m)` with its 95% interval (ci_method `linearised_t`,
workloads as clusters; bootstrap secondary).

**Decision rule, pre-registered.** For each arm:
- `k_hat` lower CI bound >= threshold line -> the arm is inside the obstruction's scope
  (the lead's closure covers it; record as `advances LEAD-ICE-generic-oracle-arity-cost-floor`, no disposition change).
- `k_hat` upper CI bound < threshold line **and** the arm's end-to-end S exponent
  (cold, every phase, failures charged) also has a 95% interval below rho's over the
  same ladder -> `open_next_step` for that arm with `best_measured` filled; this
  would also falsify the lead's closure within its scope and requires `review-breakthrough`.
- `k_hat` upper CI bound < threshold line but end-to-end S exponent not below rho
  -> H1-H3 are wrong as a model of that pipeline (the theorem's `needs_H*`
  controls say which); record as `inconclusive`, revisit the hypotheses, not the lead.
- Interval straddles the line -> `exhausted_at_scale` for the ladder reached;
  `revisit_when`: ladder extended by >= 6 bits.

**Multiplicity.** m arms x oracles; Bonferroni on the number of (arm, m) cells; the
power check `2/(N+1) < alpha/cells` is run with N = number of workloads (>= 8 per size,
>= 6 sizes) before any data.

## 2. Arms

All arms run inside `ecbench` (`src/cryptanalysis/ecbench/methods.rs`), counted in
`ecbench.gae`, on the same frozen workloads, interleaved.

| arm | role | ecbench method / params | expected k (prediction, not a result) |
|---|---|---|---|
| A1 | candidate | `ic.pipeline factor_base=prime-abscissa:size=B oracle=subtract linalg=incremental-gauss targets=walk`, m = 2 | 1 (one pass over the base; all-decompositions) |
| A2 | candidate | same, `oracle=mitm:negation_folded=1`, m = 2 | 1 (table lookup against a B-table; all-decompositions) |
| A3 | candidate | `oracle=rootfind-subtract` / `rootfind-mitm` / `rootfind-pairs`, m = 2 | 1 |
| A4 | candidate | `oracle=mitm-prime-batch`, `mitm-prime-blocked`, m in {3, 4, 5} | ceil(m/2) |
| A5 | candidate | `oracle=descent-algebraic solver=exhaustive`, m in {3, 4} | m - 1 |
| A6 | candidate (if present on prime curves) | any `descent-algebraic` Groebner / `sat-cdcl` oracle that accepts a prime-field base; otherwise mark `absent` (docs/ic/LEADERBOARD.md: "Prime curves have no algebraic oracle in ecbench") | fitted; the only arm that could sit below the line |
| C1 | positive control | an instrumented oracle added through `ecbench-extend` whose attempt loop touches each base element exactly once and returns on the first hit (one-decomposition, k = 1 by construction) | 1.000 within CI |
| C2 | positive control | the same loop without early exit (all-decompositions, k = 1) | 1.000; and `relations_per_attempt` must track B^m/(m! r) |
| C3 | negative control | `oracle=descent-algebraic solver=exhaustive` at m = 2 (k = 1 by construction, same code path as A5) | 1 |
| R | incumbent | Table B row for the same curve (m = 2 folded/walked pair table), frozen protocol `research/ic_tool_program/rule/*` | end-to-end S, not k |
| rho | matched reference | `rho.negation`, same single planted target, same resource envelope | alpha = 0.5 by declaration; measured 0.4545 [0.3876, 0.5927] in the sealed session |
| AA | A/A | a second copy of A2 on the same workloads | ratio 1.0 in operations (determinism check) |

New arms (C1, C2) go through `.agents/skills/ecbench-extend/SKILL.md`: implement on
`CountedGroup`, register in `methods::registry()`, document the charge in
`docs/ecbench/README.md` section 7; a parameter that changes the search gets no default.

## 3. Ladder and instances

- Six prime-order curves drawn by `prime_search` with a recorded seed, field sizes
  12, 14, 16, 18, 20, 22, 24 bits (>= 12 bits of log2 r spanned; the sealed prime
  toy domain `ECDOM1ha1f283af3a5d` curves fp18-tm337, fp20-t727, fp22-tm1385,
  fp24-t1059 are reused where the size matches so the result can be paired with
  `ECBND1h93b7a9d5c187` / `ECBND1h9879c0aa348f` / `ECBND1h9896c8176a62`).
- Within each curve a beta ladder of >= 6 factor-base sizes B = 2^{b}, b spanning
  >= 6 bits (the slope in log B at fixed r is `k`); sizes chosen before data.
- 8 planted targets per (curve, B), target_seed recorded; 3 rounds; warmup 1.
- Isomorphic and isogenous controls are not needed for `k` (the oracle cost is a
  function of B and the arm), but one isomorphic re-presentation of one curve is
  run as a representation check (LEAD-ICE-curve-presentation-invariance).

## 4. Counting

- Counted unit `ecbench.gae`; S = GAE / sqrt(r); floor sqrt(pi/4) (A = 2).
- Per phase: setup, relation collection (split into attempts, GAE per attempt,
  relations per attempt), linear algebra, descent. A missing phase makes the
  total unknown.
- Charge censored failures; state setup amortisation (none: one target, cold).
- Every unpriced counter on every arm, reference included, listed and priced
  at 0, 0.1 and 1 GAE per operation (`ecbench band`): lookups, legendre_symbols,
  sqrt_solves, row_ops, target_guard_probes, table inserts, canonicalisations.
  `k_hat` is reported at each weight; the arm is placed against the line only
  where the order holds across the band.

## 5. Statistics

- Primary: `k_hat` per (arm, m) from the regression of log GAE-per-attempt on
  log B pooled over sizes, workloads as clusters, ci_method `linearised_t`.
- Secondary: end-to-end S exponent alpha per arm against rho's, same ladder;
  relations-per-attempt against B^m/(m! r) (H1 check); linalg GAE against B^2 (H3 check).
- Decision rule and multiplicity as in section 1; effect size with CI before any p-value.
- Power check before data: with 8 workloads x 3 rounds per size and 6 sizes, the
  slope CI half-width must be below 0.25 in k for the A/A arm, else the ladder is
  widened before the candidate arms run.

## 6. Isolation and freeze

- Interleave arms; host-load gate; NUMA-local whole-core placement (isolation L2).
- Commit `PROTOCOL.md` (this spec, with the chosen seeds and sizes) before the
  first data point; deviations as labelled amendments.
- Independent replay on a second host for any rule-in (`ecbench-independent-runner`).

## 7. Evidence

Replay certificate, validator report, `VALIDATION.json` passing
`python3 scripts/validation_gate.py evidence <dir>` (crypto); a research-visuals
report (one figure: `k_hat` with CI per arm against the threshold line for
each m, negatives included) and PDF; a `benchmarks/<YYYYMMDD>-oracle-order-census/`
entry; a `claims/<name>.json` in crypto-autoresearcher only if an arm rules in.

## 8. Confounders, and how the design neutralises each

| confounder | design |
|---|---|
| curve model and presentation | one model (short Weierstrass), one isomorphic control curve |
| field representation | u64 Montgomery for all arms, same binary commit |
| Aut(E) and whether rho folds it | A = 2 everywhere; rho.negation folds negation, IC arms use negation_folded where offered |
| distinguished-point and collision parameters | rho.negation frozen at the sealed-session parameters |
| failure censoring | charged; censored runs bound the ratio |
| setup amortisation | none (one target, cold) |
| unpriced counters | band 0 / 0.1 / 1 GAE on every arm |
| host load and placement | L2 isolation, interleaving, A/A arm |
| compiler, toolchain and commit drift | one commit, recorded; replay certificate |
| best-of-k selection | sizes, seeds and arms fixed in PROTOCOL.md before data; every arm reported |

## 9. Outcomes and what each changes (decision_impact, prospective)

- on_positive (an arm below the line with end-to-end S below rho): the lead's
  closure is falsified within scope; `review-breakthrough` at max; the
  threshold theorem's H1-H4 are checked against the data before any claim leaves.
- on_negative (every arm on or above the line): the proof upgrade of
  LEAD-ICE-generic-oracle-arity-cost-floor is corroborated at toy scale for
  every implemented prime-field oracle; `revisit_when` becomes "an oracle with
  measured k below the line"; the prime-field Tier X question is restated as the
  construction problem for `k < (m-1)/2`.
- inconclusive (intervals straddle): `exhausted_at_scale` for this ladder; extend by >= 6 bits.
