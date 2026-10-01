# Validation report — TASK-20260913-31d530

- **Round:** REVIEW-SEMBIN-20260913-run2 (`coordination/review/sembin-20260913-run2/review-plan.yaml`)
- **Role:** validator, independent session, `requested_policy: review-adversarial`
- **Object:** `experiments/EXP-SEMBIN-354a75/runs/RUN-SEMBIN-1b9afe/`, archived in commit
  `40e1cf727` (`snapshot TASK-20260913-a10004: EXP-SEMBIN-354a75 RUN-SEMBIN-1b9afe before
  review`), against the frozen contract `experiments/EXP-SEMBIN-354a75/specification.yaml`
  (version 1, `approved`, `DEC-20260913-ebd639`) and the primary source
  `inputs/SEMAEV-2015-310/`
- **Joints owned:** J1, J2, J3. Plus the round's assigned **proves-too-much** control.
- **Joints NOT owned and not read:** J4, J5 (TASK-20260913-7ca970) and J6-BLIND
  (TASK-20260913-3395e3). Neither task directory existed at the time of this review;
  `coordination/review/sembin-20260913-run2/` contained only `review-plan.yaml`.

## Verdict summary

| joint | verdict | the artifact that decided it |
| --- | --- | --- |
| J1 — which ratio is the headline | **breaks** | the three columns each reproduce exactly and are mutually consistent as identities, but sections A/G average 20 configurations while C/D/F are one configuration, and the headline's own population is bimodal: `raw-result.json` `cells[6].configurations[*].sides.E.counts_summary.usable`, recomputed from `per-R-counts.json` |
| J2 — the artifact-free label | **breaks** | the headline deficit is not in any of the four factors; it is `f_dispersion`, and `f_dispersion` is 0.79–0.82 for `low_degree_polynomial` subspaces and 0.99–1.01 for `random_k_dimensional` ones at the same cells with no dependence on B (`per-R-counts.json`, `usable_point_multiset`, E side) |
| J3 — the decay claim | **breaks** (as stated; the underlying reasoning survives) | independent derivation `f_base = (1 + Z·\|V\|^{-1/2})^t` against all nine cells' `rational_factor_base_points_L`, plus `ratio-above-1-diagnosis.txt` section E's own table being ordered by \|V\| while t varies |

**No instrumental defect was found.** The enumeration is exhaustive where it claims to be,
every per-configuration count reconciles, and every digest matches. The defects are in how
the numbers were summarised — which is the Coordinator's stated whole-round prior, and on
that point the prior is confirmed.

**The Coordinator's prior was overturned on J2** (its diagnosis of where the deficit sits is
wrong, and the run's own report already made the distinction the prior thought was missing),
**partly overturned on J1** (the three columns are not definitionally vague; each is exact),
and **confirmed on J3**.

---

## 0. Artifact and receipt integrity (validator baseline, prior to the joints)

Checked before touching any joint, because a joint verdict on an unbound receipt is worthless.

| check | result |
| --- | --- |
| package committed before any reviewer read it | yes — `40e1cf727`, 23 files, adds the run package and `code/`; `git diff 40e1cf727 HEAD -- experiments/EXP-SEMBIN-354a75/` shows exactly one addition, `manifest_v2.yaml` (the additive schema completion, CORR-20260913-a99454) |
| working tree clean for the object | yes — `git status --porcelain experiments/EXP-SEMBIN-354a75/` empty |
| governing manifest read | `manifest.yaml` (archived). `manifest_v2.yaml` was not used for any substantive claim in this report |
| artifact SHA-256 + byte counts | 6/6 match (`command.txt`, `environment.json`, `per-R-counts.json`, `raw-result.json`, `stdout.log`, `stderr.log`) |
| code SHA-256 | 11/11 match in `artifact-digests.json`; `manifest.yaml` additionally records `yield_diagnose.py` with a note that it was written after `yield_run.py` finished, in response to the stopping rule — verified `0bce7238…` matches the file on disk |
| exact command | recorded, `command.txt` and `manifest.yaml` agree |
| revision + dirty tree | `71509d763983588b89ce04ba355e161426baf547`, `git_dirty: true` with all 12 dirty paths enumerated; every one is an untracked path (`??`), none is a modification to a tracked file |
| seeds | 5 declared seeds, per-configuration `seed` and `derived_seed` recorded; generator `numpy.random.default_rng` (PCG64); consumers enumerated |
| environment | `environment.json` present, `groebner_engine: None` recorded |
| resources | wall 827.3 s of a 3600 s budget, CPU 827.5 s, `peak_rss_gb_upper_bound: 1.043` against a 4 GB budget and a self-imposed 3 GB ceiling. The 1.043 GB figure is `getrusage(RUSAGE_CHILDREN)` and is declared as an upper bound; `MSG-20260913-477ddd`'s "0.50GB in-process peak" is the in-process high-water mark in `raw-result.json`. Two different measures, both recorded, not a contradiction |
| coverage | `unreached_cells: []`, 180/180 configurations, `reached_exhaustively: true` at all nine cells |
| validity | `completed_valid`; `certificate.kind: none` with a stated reason (a pure counting run claims no solve and no relation) |
| inference record | `requested_policy: executor-implementation`, `resolved_model_id: claude-opus-5`, `model_verified: false` with the reason (`doctor --probe` not run from that session). Disclosed, not concealed |
| authority boundaries | `evidence_record_written: false`, `hypothesis_status_changed: false`, `conclusion_about_any_curve_stated: false`, `specification_modified: false`, `committed_by_executor: false` |
| declared deviation | one, self-recorded: the bus write to `coordination/bus/messages/MSG-20260913-477ddd.yaml`, outside the declared `write_scope`, after the artifacts were sealed. Disclosed by the producer; affects no measurement |

Controls declared by the contract, re-read and checked:

- **baseline** — eq. (11) recomputed against all 33 `P_theoretical` entries of the frozen
  transcription; 33/33 match to four decimals under the paper's truncation convention,
  `max_abs_error` 9.87e-05. The control correctly refuses to be read as support for
  eq. (11) (`not_evidence_for_eq11`).
- **matched null** — 45 realisations, 5 per cell. `min_matched_ratio` 0.99059,
  `max_matched_ratio` 1.01229. I recomputed the null's own dispersion factor at the three
  t = 2 cells from `exact_hit_fraction_all_q_targets` and `exact_mean_count`: **0.999823,
  1.000348, 1.000170**, with Poisson goodness-of-fit p = 0.424, 0.656, 0.216. The pipeline
  does not manufacture a dispersion deficit. This control is load-bearing for J2 below.
- **known-false class count** — modelled λ shifts by exactly t! in every cell; the ordered
  realisation inflates the mean by t! against the symmetric one.
- **invalid input** — R at infinity rejected, non-subspace V rejected, wrong dimension
  rejected.
- **exhaustiveness** — order-independence verified with three permutation seeds per audited
  cell, plus agreement with an independent per-R path; `multisets_enumerated` equals
  `expected_multisets` in every audited cell.
- **conservation identity** — I recomputed it independently at all nine cells. In each,
  `incidences + multisets_summing_to_infinity + multisets_whose_sum_has_x_in_V` equals
  `C(L+t-1, t)` **exactly**, with no remainder, and `enumerated_multisets == C(L+t-1, t)`
  exactly. E.g. n20: 476396 + 489 + 868 = 477753 = C(978, 2).
- **independent cross-check of the exhaustive pass** (mine, not the run's): the exhaustive
  pass runs on one configuration per cell (B = 1, low-degree V). Five of the twenty
  configurations at each m = t = 2 cell are that same configuration under five different
  draw seeds, i.e. 10 000 independent target draws from the object the exhaustive pass
  enumerates in full. Agreement:

  | cell | exhaustive hit fraction (all targets) | 10 000 sampled draws, same configuration | z |
  | --- | --- | --- | --- |
  | n20 m2 t2 k10 | 0.29836 (1 046 398 targets) | 0.29840 ± 0.00458 | +0.01 |
  | n22 m2 t2 k11 | 0.31605 (4 191 860 targets) | 0.31360 ± 0.00464 | −0.53 |
  | n24 m2 t2 k12 | 0.31140 (16 779 152 targets) | 0.31320 ± 0.00464 | +0.39 |

  The exhaustive pass and the sampler agree on the same object. There is no enumeration
  defect and no per-R count that fails to reconcile.

---

## J1 — which ratio is the headline

### The three columns, each recomputed from its own stated definition

All three reproduce. Cell n20 m2 t2 k10 throughout; `P_eq11 = 1 − exp(−0.5) = 0.3934693`.

**Section A, `sem P` = 0.9024.** Definition (`yield_stats.py` docstring, which names it
"the HEADLINE ratio"): `ratio_zero` = measured fraction of R with at least one decomposition,
divided by eq. (11)'s P. Recomputed **from `per-R-counts.json` rather than from the run's
aggregates**: pooling the E-side `usable_point_multiset` column over the 20 configurations
carrying the `n20-m2-t2-k10` prefix gives 40 000 entries, mean 0.49525, non-zero fraction
0.355075, so the ratio is 0.355075 / 0.3934693 = **0.902421**, against the reported
0.902421. Reproduced exactly.

**Section D, observed P ratio = 0.7583.** Definition (`yield_diagnose.probability_decomposition`):
`exact_hit_fraction / P_eq11`, where `exact_hit_fraction` comes from
`cells[i].exact_usable_all_R_B1_low_degree` — the sampling-free pass over the whole target
population of **one** configuration. 0.298359 / 0.3934693 = **0.758277**, reported 0.758277.
Reproduced exactly. It also satisfies its own stated factorisation:
`f_dispersion × f_mean_level = 0.815801 × 0.929487 = 0.758277`.

**Section G, `f_dispersion` = 0.9091.** Definition: `P_measured / (1 − exp(−mean_measured))`
on the same pooled population as section A. From `per-R-counts.json`:
0.355075 / (1 − exp(−0.49525)) = **0.909093**, reported 0.909093. Reproduced exactly.
And the two pooled columns are related by an exact identity:
`G × f_mean_level(pooled) = 0.909093 × 0.992660 = 0.902421 = A`.

### What each column actually is

| | A (`sem P`) | D (`observed` P ratio) | G (`f_dispersion`) |
| --- | --- | --- | --- |
| is it a measured-over-eq.(11) ratio? | **yes** | **yes** | **no** — the denominator is the *realized* mean, not eq. (11)'s |
| target population | E | E | E |
| presentation | `usable`; at these cells `single`, `chained`, `usable` and `point_multiset_total` are **identical per R**, verified column-by-column from `per-R-counts.json` | `usable` | `usable` |
| class-count variant | `semaev_v_to_the_t_over_t_factorial` | same | none in the denominator |
| target sampling | 2 000 sampled draws per configuration | **exhaustive**, all 1 046 398 targets | 2 000 per configuration |
| configurations averaged | **20** (both subspace variants × both B modes × 5 seeds) | **1** (`B_eq_1`, `low_degree_polynomial`) | **20** |

So the plan's suspicion that the columns differ in population is right, but not on the axis
it named: the E/T axis is not the discriminator (all three are E; the T side is uniformly
0.0000 at every cell and is separately disclosed in `task-report.md` §112–136 and §773), and
the presentation axis is not the discriminator either (the three presentations coincide per R
at these cells). **The discriminating axis is which configurations are averaged, and the
diagnosis never names it in sections C, D, E or F.** The `raw-result.json` field key does
name it — `exact_usable_all_R_B1_low_degree` — which is to the producer's credit; the
rendered diagnosis does not, and a reader of the diagnosis sees "over the WHOLE target
population" in section C's header, which refers to targets and reads as though it also meant
configurations.

### Which one multiplies into stage-1 relation cost, and was that the one quoted

`task-report.md` §11 Step 1 states the cost relation and I agree with it: stage-1 cost
∝ 1/P, so the cost-bearing quantity is P itself, and the cost-bearing *ratio* is
P_measured / P_eq11. That rules G out immediately: G is a *factor* of the cost-bearing ratio,
not the ratio. A and D are both of the right kind, and they differ in population.

`MSG-20260913-477ddd` quotes "ratio 0.9024/0.9069/0.9073 with intervals excluding 1 BELOW"
and reads the sign off it. So the quoted column is A: a ratio of the cost-bearing kind.

**That is where J1 breaks.** A is an average over a population that is *bimodal*, and the
two modes straddle 1. Splitting A's own 40 000 draws by the contract's declared independent
variable `subspace variant` (§ J2 below has the full table):

| cell | `low_degree_polynomial` | `random_k_dimensional` | pooled (the quoted number) |
| --- | --- | --- | --- |
| n20 m2 t2 k10 | 0.7810 | 1.0238 | 0.9024 |
| n22 m2 t2 k11 | 0.8158 | 0.9979 | 0.9069 |
| n24 m2 t2 k12 | 0.7929 | 1.0217 | 0.9073 |

Stage-1 relation cost is incurred by a *particular* factor base on a *particular* curve. The
cost-bearing ratio therefore has an instance-level value, and in this cell set it takes one
of two well-separated values. 0.9024 is the cost-bearing ratio for no instance the run
measured: it is the midpoint of a 22% overstatement and a 2% understatement. A reader of the
bus message could not have recovered either.

A second, independent defect on the same column. A's interval is a Wilson score interval on
40 000 draws (`yield_stats.wilson`), i.e. it treats the 40 000 draws as exchangeable
Bernoulli trials. They are not: they come from 20 configurations whose per-configuration
ratios have a between-configuration standard deviation of 0.13. Re-running the interval at
the configuration level (20 clusters, t-interval on the cluster means):

| cell | reported Wilson interval | cluster-level interval | width ratio |
| --- | --- | --- | --- |
| n20 | [0.8905, 0.9144] | [0.8415, 0.9634] | 5.1× |
| n22 | [0.8950, 0.9188] | [0.8581, 0.9556] | 4.1× |
| n24 | [0.8954, 0.9193] | [0.8511, 0.9635] | 4.7× |

The qualitative claim "the interval excludes 1 below" survives at all three cells even at
cluster level. The stated precision does not, and it is understated by a factor of four to
five in exactly the direction that made the effect look sharper than the design supports.

### What the Coordinator's prior got right and wrong on J1

Right: J1 breaks, and "a reader of the bus message could not have known which one they were
being given" is correct — and understated, because the quoted one is an average over a
population no single reader could have guessed was bimodal.

Wrong: "three numbers between 0.75 and 0.91 for one cell … is the shape of a quantity whose
definition has not been pinned down." Each of the three *is* pinned down, each reproduces to
six decimals from the raw per-R data or the exhaustive aggregates, and the two pooled ones
are related by an exact identity (A = G × f_mean_level). The disagreement between A and D is
neither arithmetic nor definitional vagueness: it is a change of averaging population
between sections of one file, compounded by bimodality inside one of those populations. The
distinction matters for the remedy. Nothing needs redefining; the sections need their
population stated, and the headline needs splitting.

---

## J2 — the artifact-free label

### The criterion, stated before the values were computed

Required disclosure first: the review plan pre-discloses `f_legal = 0.9972` and
`f_base = 0.9103` at n20 in its prior, and I read the plan in full before this joint, as the
handoff directs. So "before looking at the values" is, for me, necessarily "before computing
anything and without using the disclosed values to choose the criterion." The ordering
protection the joint is built on is therefore partly spent by the plan's own deliberate
disclosure. I compensate by making the criterion **decidable from the factor definitions
alone**, so a reader can check that no value could have influenced it, and by adding a second
criterion that is decided by an object the run already measured rather than by my judgement.

**Criterion 1 (definitional, two axes).**

- *Axis 1 — cardinality or incidence?* A factor is **cardinality-only** if its value is a
  ratio of two counts each determined by |V|, t, q, L and #E alone, carrying no information
  about *which* multisets sum to *which* targets. A factor is **incidence-structural** if its
  value depends on the realized incidence between multisets and targets. A cardinality-only
  factor can be removed from eq. (11) by substituting the right count, with no measurement of
  a curve beyond a point count; an incidence-structural one cannot.
- *Axis 2 — biased or mean-one?* Over the ensemble of instances the design samples, does the
  factor have a deterministic sign, or is it a fluctuation with mean 1?

Only a factor that is incidence-structural, or cardinality-only-and-biased, can carry a
reported bias sign. A cardinality-only mean-one factor cannot: its realized value at one
instance is a draw, not a bias.

**Criterion 2 (operational, decided by the run's own matched null).** The matched null is a
symmetric random map on the exact class count pushed through the identical pipeline — eq.
(11)'s object with **no curve in it**. A factor the null exhibits is a property of eq. (11)'s
bookkeeping. A factor the null does not exhibit is a property of the object being measured.

Assignments, from the definitions in `yield_diagnose.py` and `yield_null.py`:

| factor | definition | axis 1 | axis 2 | can it carry a bias sign? | null exhibits it? |
| --- | --- | --- | --- | --- | --- |
| `f_multiset` | `C(L+t−1,t) / (L^t/t!)` = ∏(1+i/L) | cardinality | biased ≥ 1 | yes | **yes** (the null's Semaev-variant ratio is 1.00058/1.00072/1.00036, the class-count inflation) |
| `f_base` | `(L/\|V\|)^t` | cardinality | **mean-one** | **no** | **no** (the null has no L) |
| `f_pop` | `q / \|targets\|` | cardinality | ≈1 | negligibly | n/a (null runs over all q) |
| `f_legal` | `incidences / C(L+t−1,t)` | **incidence** | biased ≤ 1 | yes | **no** |
| `f_dispersion` | `P_meas / (1−exp(−mean))` | **incidence** (distributional) | not fixed a priori | yes | **no** — null gives 0.99982, 1.00035, 1.00017 |

The two criteria agree everywhere they both speak. Both put `f_base` on the side that
**cannot** carry a bias sign.

### The four-factor decomposition, reproduced

Recomputed from `raw-result.json`'s raw integer fields (`rational_factor_base_points_L`,
`enumerated_multisets`, `incidences`, `target_population_affine_x_outside_V`) with no use of
the run's own factor values:

| cell | L | f_legal | f_multiset | f_base | f_pop | product | observed | residual |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| n20 m2 t2 k10 | 977 | 0.997160 | 1.001024 | 0.910310 | 1.002081 | 0.910545 | 0.910545 | 1.000000000000 |
| n22 m2 t2 k11 | 2051 | 0.998474 | 1.000488 | 1.002932 | 1.000583 | 1.002473 | 1.002473 | 1.000000000000 |
| n24 m2 t2 k12 | 4047 | 0.999257 | 1.000247 | 0.976217 | 0.999885 | 0.975621 | 0.975621 | 1.000000000000 |

The residual closes to 1 to twelve decimals, better than the claimed 1e-9, at these three
cells and at all five other non-degenerate cells. `C(L+t−1,t)` equals `enumerated_multisets`
exactly in every cell. **Section C is arithmetically sound and I found nothing wrong with
it.**

### Where the deficit actually sits — the prior's diagnosis is overturned

The prior holds that "the entire ~9% deficit in the cells labelled artifact-free is f_base."
It is not, and the confusion is the J1 population conflation:

- `f_base = 0.9103` is the value for **one** configuration, whose L = 977 against E[L] = 1024
  — a −1.44σ draw on a quantity with σ ≈ √|V| = 32. Over the 20 configurations of that cell
  `f_base` averages **0.9888**, and over the three cells 0.9888 / 0.9998 / 1.0032, with a
  spread that matches the derivation in J3. `task-report.md` §11 Step 2 states this already,
  correctly, and the prior did not credit it.
- Meanwhile the **headline** ratio, which   is the pooled one, factors as
  `A = f_dispersion(pooled) × f_mean_level(pooled) = 0.9091 × 0.9927`. The pooled *mean*
  ratio is 0.9905, 1.0070 and 1.0068 at the three cells, every interval containing 1 — i.e.
  **eq. (11) gets the mean right to within 1%** there. The 9–10% deficit is essentially all
  in `f_dispersion`, which is not one of the four factors at all.

So the prior's dichotomy — "either those cells are not artifact-free, or f_base is not an
artifact" — is a false dichotomy at the headline. At the headline `f_base ≈ 1`,
`f_multiset ≈ 1`, `f_pop ≈ 1`, and the label's arithmetic premise holds. The label's
*inference* is what breaks, and for a reason absent from the prior.

### Why the label breaks: the deficit is a function of the subspace construction

`f_dispersion` is incidence-structural, so under my criterion it *can* carry a bias sign —
and it is not a formula artifact, which the null confirms. But it is not a statement about
"the curve's realized yield" either. Splitting the E-side `usable_point_multiset` column of
`per-R-counts.json` by the contract's two declared independent variables — subspace variant
and B mode — at the three cells the run calls artifact-free (10 000 draws per box):

| cell | subspace | B mode | mean | hit fraction | P ratio | f_dispersion |
| --- | --- | --- | --- | --- | --- | --- |
| n20 m2 t2 k10 | low_degree | B = 1 | 0.45090 | 0.29840 | 0.7584 | 0.8222 |
| n20 m2 t2 k10 | low_degree | random B | 0.50030 | 0.31620 | 0.8036 | 0.8032 |
| n20 m2 t2 k10 | random V | B = 1 | 0.51350 | 0.40450 | 1.0280 | 1.0072 |
| n20 m2 t2 k10 | random V | random B | 0.51630 | 0.40120 | 1.0196 | 0.9949 |
| n22 m2 t2 k11 | low_degree | B = 1 | 0.50550 | 0.31360 | 0.7970 | 0.7903 |
| n22 m2 t2 k11 | low_degree | random B | 0.51630 | 0.32840 | 0.8346 | 0.8143 |
| n22 m2 t2 k11 | random V | B = 1 | 0.49280 | 0.39100 | 0.9937 | 1.0049 |
| n22 m2 t2 k11 | random V | random B | 0.49940 | 0.39430 | 1.0021 | 1.0030 |
| n24 m2 t2 k12 | low_degree | B = 1 | 0.48870 | 0.31320 | 0.7960 | 0.8102 |
| n24 m2 t2 k12 | low_degree | random B | 0.49540 | 0.31080 | 0.7899 | 0.7956 |
| n24 m2 t2 k12 | random V | B = 1 | 0.51630 | 0.40370 | 1.0260 | 1.0011 |
| n24 m2 t2 k12 | random V | random B | 0.51320 | 0.40030 | 1.0174 | 0.9972 |

Read the `mean` column first: it is 0.45–0.52 in every box, against eq. (11)'s λ = 0.5. The
mean is fine everywhere. The **dispersion** is not: variance/mean is 1.46–1.52 in the
low-degree boxes and 0.99–1.00 in the random-subspace boxes, so the low-degree counts are
over-dispersed — the same mean spread over fewer targets, hence more zeros, hence P below the
Poisson value at the realized mean. The effect tracks the **subspace basis** and is
indifferent to B.

Cluster-level statistics over configurations (10 per family, t-intervals on cluster means):

| cell | low_degree P ratio | random V P ratio | Welch t |
| --- | --- | --- | --- |
| n20 | 0.7810, [0.7553, 0.8067] | 1.0238, [0.9940, 1.0536] | 13.97 |
| n22 | 0.8158, [0.7899, 0.8418] | 0.9979, [0.9576, 1.0382] | 8.60 |
| n24 | 0.7929, [0.7755, 0.8104] | 1.0217, [1.0021, 1.0413] | 19.70 |

This is a **"controls before belief" chain in its strongest form**, and it comes out the way
a real signal comes out rather than the way an artifact does:

1. eq. (11)'s own object, with no curve — matched null, `f_dispersion` = 0.99982/1.00035/1.00017,
   Poisson fit passes. The pipeline manufactures nothing.
2. Curve + **random** k-dimensional subspace — `f_dispersion` = 0.99–1.01, indistinguishable
   from the null.
3. Curve + **low-degree polynomial** subspace — `f_dispersion` = 0.79–0.82, stable across a
   4× range of |V| and across both B modes.

The parameter that would destroy the structure is randomising the subspace basis, and when it
is randomised **the signal decays to exactly nothing**, matching the curve-free null. That is
the opposite of the canonical artifact tell in `docs/inventor-protocol.md` §3.

### Verdict on J2, and what the shortfall's mechanism actually is

The label "the m = t = 2, |V| ≥ 1024 cells are artifact-free" is defensible in the narrow
sense the report means it: the class-count artifacts are numerically negligible there and
`f_base` averages to ≈1. **What breaks is the inference the label is used for** — that the
negative bias sign read off those cells is about the curve's realized yield. It is not:

- The *mean* is not in deficit at all (pooled mean ratio 0.9905; the incidence-structural,
  curve-reflecting `f_legal` is only 0.28%, 0.15% and 0.07% below 1 at the three cells).
- The 9–10% deficit is `f_dispersion`: **over-dispersion / clustering of the per-target
  decomposition counts**, present only when V is the subspace of polynomials of degree < k
  and absent when V is a random k-dimensional subspace, with no dependence on the curve
  coefficient B.
- So the shortfall's mechanism is a property of the **x-coordinate window**, not of eq.
  (11)'s class-count bookkeeping (which is ≈1 here) and not of the curve family (which is
  common to both boxes).

This matters for the direction of the correction, because of what the primary source says.
`inputs/SEMAEV-2015-310/paper_fulltext.md` lines 539–545: "Let V be a set of all polynomials
in α of degree < k = ⌈n/m⌉ … one can define V as any subspace of F_2n of dimension k.
However it seems that using the subspace of low degree polynomials significantly reduces the
time and space complexity in comparison with a randomly generated subspace and is therefore
preferable." The paper's own V is the low-degree-polynomial subspace. So for the construction
the paper specifies, eq. (11) overstates P by **18–22%**, not by 9–10%: the headline is
*conservative* for the paper's own choice, because it is diluted with a family the paper
explicitly declines to use. The executor's **sign** is not overturned — it is reinforced.
Its **magnitude and its attribution** are.

Two boundaries I hold explicitly. First, the paper's stated reason for preferring the
low-degree window is a Gröbner-basis/degree matter. I cite that sentence as a quotation of
the source and I **measure, estimate and assert no degree anywhere** (IMP-SEMBIN-ENGINE); I
therefore do **not** evaluate the trade-off between the yield penalty measured here and the
advantage the paper claims for that choice, and nothing in this report bears on it. Second,
nothing here says anything about any curve's security at any parameter, in either direction.

---

## J3 — the decay claim

### Derivation from the definitions alone

`f_base = (L/|V|)^t`, with L the number of F_q-rational points of E: y² + xy = x³ + B whose
x-coordinate lies in V, and V an F_2-subspace of dimension k, so 0 ∈ V and |V| = 2^k.

For x ≠ 0 the curve equation is a quadratic in y whose solvability over F_q is a trace
condition on (x³+B)/x² = x + B/x²; it has either 2 or 0 solutions. For x = 0 it reads y² = B,
and squaring is a bijection in characteristic 2, so x = 0 contributes **exactly one** point.
Hence with r = #{x ∈ V carrying a rational point},

    L = 2(r − 1) + 1 = 2r − 1,

which is the run's own stated convention. Writing r − 1 = #{x ∈ V \ {0} : trace condition
holds} and modelling each nonzero x as satisfying it with probability 1/2 (the global
frequency is (q − 1 − t_a)/2 of q − 1, i.e. 1/2 + O(q^{-1/2}) by Hasse),

    r − 1 ~ Binomial(|V| − 1, 1/2),  E[L] = |V|,  sd(L) = √(|V| − 1).

Therefore L/|V| = 1 + Z·√(|V|−1)/|V| ≈ 1 + Z·|V|^{-1/2} with Z standard, and

    f_base = (1 + Z·|V|^{-1/2})^t = 1 + t·Z·|V|^{-1/2} + O(t²/|V|).

Three consequences, all predictions:

1. **Rate.** sd(f_base) ≈ t·|V|^{-1/2}; mean-absolute deviation
   ≈ t·√(2/π)·|V|^{-1/2} ≈ 1.596·|V|^{-1/2} at t = 2. So |f_base − 1| = Θ(t·|V|^{-1/2}).
   Section E's "O(|V|^{-1/2})-type" **rate is correct**, with constant t.
2. **Mean.** E[f_base] = 1 + t(t−1)/(2|V|) + O(…) → 1. Convergence is in probability, and the
   *bias* is one order smaller than the fluctuation: O(|V|^{-1}) against O(|V|^{-1/2}).
3. **Sign.** sign(f_base − 1) = sign(Z), a fresh fair coin for every configuration. **The
   sign does not settle.** The derivation *predicts* non-monotonicity, so non-monotonicity is
   not a defect — per the plan's own instruction.

### Against all nine cells

Empirical check of the derivation's two moments, over the distinct configurations of each
cell (`rational_factor_base_points_L`):

| cell | \|V\| | t | mean L | predicted E[L] | sd L | predicted √(\|V\|−1) | sd f_base | predicted t/√\|V\| |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| n12 m6 t6 k2 | 4 | 6 | 4.2 | 4 | 1.4 | 1.7 | 6.83 | 3.00 |
| n15 m5 t3 k3 | 8 | 3 | 8.1 | 8 | 3.1 | 2.6 | 1.26 | 1.06 |
| n13 m4 t4 k4 | 16 | 4 | 14.5 | 16 | 2.8 | 3.9 | 0.567 | 1.00 |
| n17 m3 t3 k6 | 64 | 3 | 67.5 | 64 | 6.5 | 7.9 | 0.342 | 0.375 |
| n19 m3 t3 k7 | 128 | 3 | 127.1 | 128 | 12.3 | 11.3 | 0.291 | 0.265 |
| n21 m3 t3 k7 | 128 | 3 | 135.5 | 128 | 11.3 | 11.3 | 0.321 | 0.265 |
| n20 m2 t2 k10 | 1024 | 2 | 1028.0 | 1024 | 25.6 | 32.0 | 0.0505 | 0.0625 |
| n22 m2 t2 k11 | 2048 | 2 | 2046.8 | 2048 | 36.4 | 45.2 | 0.0354 | 0.0442 |
| n24 m2 t2 k12 | 4096 | 2 | 4115.8 | 4096 | 66.2 | 64.0 | 0.0325 | 0.0312 |

E[L] = |V| holds to within a fraction of one sd everywhere; the sd matches to within the
precision a 16-sample estimate of a standard deviation carries (≈18%). The three realized
`f_base` values the plan quotes sit at −1.44σ, +0.07σ and −0.76σ of the derived distribution:
all ordinary draws. Sign across the nine cells: +, −, +, +, +, +, −, +, − — unsettled, as
derived. (n19 and n21 share one V and B = 1, so their identical L = 139 is one draw, not two.)

### The threshold |V|, and whether any cell reaches it

| the effect f_base noise must fall below | \|V\| needed (mean-\|·\|) | \|V\| needed (2σ) | reached in this contract? |
| --- | --- | --- | --- |
| the headline pooled P deficit, 1 − 0.9024 = 0.0976 | 267 (k ≥ 9) | 1 680 (k ≥ 11) | **n22 and n24 yes; n20 NO** |
| the per-family (low-degree) deficit, ≈0.19 | 71 | 443 (k ≥ 9) | all three yes |
| `f_legal` at n20, 1 − 0.99716 = 0.00284 | 315 721 (k ≥ 19) | 1 983 733 (k ≥ 21) | **no cell** |
| `f_legal` at n24, 0.00074 | 4 650 254 (k ≥ 23) | 29 218 408 (k ≥ 25) | **no cell** |

Largest |V| in the contract is 4096. Two readings follow, and both are findings:

- Against the **headline** effect, n20 — the cell section C displays and the plan quotes — is
  the one cell of the three that does **not** reach the window where the claim is testable:
  its 2σ f_base band is ±0.125, wider than the 0.0976 effect. n22 and n24 do reach it.
- Against the quantity section F calls "the realized shortfall" (`f_legal`, 0.07–0.28%), **no
  cell in this contract comes within three orders of magnitude**, and pooling does not
  rescue it: 20 configurations reduce the f_base standard error by √20, giving 0.0070 at n24,
  still nine times the 0.00074 `f_legal` effect there. So within this cell set `f_legal`
  cannot be isolated from `f_base` noise at the single-configuration level at all, and only
  the exhaustive pass — which fixes L and so eliminates the f_base fluctuation by
  conditioning rather than averaging — gives it meaning. That is a real strength of the
  exhaustive design and it should be said; it is also the reason section C's numbers cannot
  be read as a decomposition of section A's.

### Verdict on J3

**Breaks as stated; survives as intended.** The Coordinator's prior is confirmed, and the
derivation it asked for is supplied above. Three specific ways section E's sentence is wrong,
beyond non-monotonicity:

1. **Order conflation.** The sentence calls `f_multiset` and `f_base` jointly
   "O(|V|^{-1/2})-type small-window effects." They are one order apart:
   `f_multiset = 1 + t(t−1)/(2L) + …` is O(|V|^{-1}) and deterministically ≥ 1;
   `f_base − 1` is O(t·|V|^{-1/2}) with an unsettled sign. At |V| = 4096, t = 2 the two are
   1.00025 and 0.976 — a factor of 100 apart in deviation. Lumping them is what makes the
   realized 0.9103 at n20 read as though it were negligible like 1.0010.
2. **The table is not at fixed t.** Section E's header says the effects "go to 1 as |V| grows
   at fixed t" and its table is sorted by |V| "so the trend is visible" — but t runs
   6, 3, 4, 3, 3, 3, 2, 2, 2 down the rows. Only the last three rows are at fixed t, and the
   derived constant is t, so most of the apparent trend is the t axis. The table cannot
   exhibit the claim it is offered as evidence for.
3. **"Go to 1" is the wrong mode of convergence for f_base.** `f_multiset` converges
   pointwise and monotonically. `f_base` converges in probability with an unsettled sign, so
   no finite sequence of cells can show it "going to 1", and reading three points as a decay
   measurement is a category error. The right statement is the one `task-report.md` §11
   Step 2 already makes — a mean-one fluctuation of relative size O(t·|V|^{-1/2}) that
   averages out across configurations — and section E should have said that instead.

---

## Proves-too-much control (assigned to this task)

**Object:** cell n15 m5 t3 k3, exhaustive configuration (B = 1, low-degree V), where L = 3,
`C(L+t−1,t) = C(5,3) = 10` multisets exist in total, `incidences = 0`, and the true yield is
exactly zero. The run's own four-factor attribution machinery was executed on it — I imported
`mean_decomposition` and `probability_decomposition` from `code/yield_diagnose.py` and called
them on that cell record, rather than reading the printed table.

**What the machinery does — the part that passes.** It does **not** return a finite,
meaningful-looking ratio. Verbatim:

```
observed_ratio_of_means      = 0.0
product_of_factors           = 0.0
residual_observed_over_product = None        # printed as "0/0 (both)"
f_dispersion                 = nan           # printed as nan
f_mean_level                 = 0.0
```

No value is fabricated at the singularity, and both the mean-level and probability-level
routines announce the undefinedness in the rendered output. That is the deliverable the plan
asked for and the machinery behaves correctly on it.

**What the control nevertheless exposes — the argument, not the object.** Three things go
through unchanged where their conclusion has no content:

1. `attribution_closes` returns **True** on the degenerate branch, because the branch tests
   `observed == 0.0` — which is `0 = 0` and says nothing about the four factors. Section C's
   footer AND-s that vacuous True into its assurance and prints "every cell's attribution
   closes to 1e-9: True". At one of the nine cells no residual was computed at all, so the
   sentence is literally false as written. The honest form is "closes to 1e-9 at the eight
   cells where the residual is defined; undefined at n15 m5 t3 k3."
2. Section F prints `1 − f_legal = 1.000000` at this cell under the heading "f_legal … is the
   realized shortfall", in the same column and the same units as the 0.002840 at n20. But the
   n20 figure is 476 396 incidences out of 477 753 multisets and the n15 figure is **0 out of
   10**. A 0-of-10 outcome is uninformative about any rate; section F carries no denominator
   column, so a reader cannot tell the two apart. The conclusion "f_legal is the realized
   shortfall" is asserted at a cell where it is a statement about ten objects.
3. The sharpest one, and it is the J1 defect in its most extreme form: at this same cell
   label, **section A reports `sem P` = 1.2400 with a 95% interval [1.0439, 1.4728] lying
   strictly above 1**, flagged `SEM>1` — while sections C, D and F report exactly zero yield.
   I checked where section A's 129 hits in 40 000 draws come from: the box that the exhaustive
   pass enumerates (low-degree V, B = 1) contributes **zero** of them over its 10 000 draws;
   they come from the other three boxes (random V/B = 1: 0.00550; low-degree/random B:
   0.00350; random V/random B: 0.00390). So one cell label carries a **+24% excess** and a
   **−100% shortfall** simultaneously, in one file, both called a measured-over-eq.(11)
   quantity.

**Conclusion of the control.** The numerical machinery is honest at the singularity; the
**argument** built on top of it is not. Per the plan's `what_a_failure_means`, the finding is
the argument: the diagnosis publishes a blanket "attribution closes everywhere", a
denominator-free 100% shortfall, and an excess and a total absence under one label. None of
these is a computational error, and all three are visible only because the degenerate cell
was used as the known-false object.

---

## Defects found, ranked

1. **The headline marginalises a declared independent variable that controls the sign of the
   reported effect, and the split is recorded nowhere.** `subspace variant` is listed in
   `specification.yaml` under `independent_variables`; the contract's required results table
   keyed by `(n, m, t, k, presentation, class_count, subspace, B, seed)` **is** delivered, so
   the data is retained and recoverable — which is why I could find this. But no narrative
   artifact reports it: grepping `task-report.md`, `summary-tables-E.txt`,
   `summary-tables-T.txt` and `ratio-above-1-diagnosis.txt` for `low_degree_polynomial`,
   `random_k_dimensional`, "variant", "per-variant" or "subspace family" returns nothing.
   This is also an **unrecorded unexpected observation** under core rule 8 — the run records
   four and this is a fifth — and it supplies a candidate mechanism for the third recorded
   one, `shape_deficit_not_monotone_in_t`, which says "no mechanism for the dip is offered":
   at the t = 3 cells **neither** family shows a dispersion deficit (`f_dispersion` runs
   0.967–1.008 across all twelve subspace × B boxes of the three t = 3 cells, with the two
   families indistinguishable), so the t = 2 entry is not a point on a t-trend at all — it is a
   low-degree-subspace effect, and there is no monotone-in-t quantity to be dipping. I measure
   the association only; I identify no cause for the clustering and offer none.
2. **Sections C, D, E and F silently change averaging population from sections A and G.**
   A and G pool 20 configurations; C, D, E and F are the single `B_eq_1`/`low_degree`
   exhaustive configuration. The `raw-result.json` key discloses it
   (`exact_usable_all_R_B1_low_degree`); the rendered diagnosis does not, and section C's
   header "over the WHOLE target population" reads as though it covered configurations too.
   The n15 row above is the worst case.
3. **The headline interval is computed under an independence assumption the run's own data
   violates.** Wilson on 40 000 pooled draws, against a between-configuration sd of 0.13;
   4–5× too narrow. The direction of the conclusion survives at cluster level; the stated
   precision does not.
4. *(minor)* Section C's "every cell's attribution closes to 1e-9: True" AND-s in a vacuous
   True from the degenerate branch.
5. *(minor)* Section F carries no denominator column, so 0-of-10 and 476 396-of-477 753 print
   in the same units.

None of these is an enumeration defect, a non-exhaustive cell, or a per-R count that fails to
reconcile. Everything I could recompute, reconciled.

## What the run got right and should be credited with

- The four-factor identity is exact (residual 1 to 12 decimals) and the conservation identity
  is exact with no remainder at all nine cells.
- The exhaustive pass agrees with 10 000 independent draws on the same configuration at
  |z| ≤ 0.53 at all three m = t = 2 cells.
- The matched null is the right control, is correctly constructed on the exact class count,
  and is what makes my J2 finding possible; the run also refuses to read the baseline control
  as support for eq. (11), which is the correct category discipline.
- `task-report.md` §11 Step 2 already states the `f_base` fluctuation argument correctly —
  the argument the Coordinator's prior on J2 assumed was missing.
- The stopping rule fired and was obeyed: no ratio above 1 is reported as a finding anywhere.
- The T-side zero yield, the refusal to add a `t < m` cell to manufacture a comparison, the
  specification-annotation mismatch, and the out-of-scope bus write are all disclosed by the
  producer rather than found by me.
- The sign of the executor's conclusion is not overturned. For the subspace the primary source
  actually specifies it is stronger than reported.

## What I could not evaluate, and why

- **The mechanism of the low-degree clustering.** I measured an association between the
  subspace construction and the dispersion deficit. I did not identify why the degree-<k
  window clusters, and I offer no mechanism.
- **Whether the effect exists at t ≥ 3.** The contract's t = 3 cells have |V| ∈ {64, 128}, so
  "no low-degree effect at t = 3" is confounded with small |V| and with f_multiset being
  large there. Not separable in this cell set; a scope limit, not evidence either way.
- **Whether the low-degree deficit decays with |V|.** It is 0.812 / 0.802 / 0.803 over a 4×
  range, which is too narrow to distinguish "no decay" from "slow decay".
- **The random-subspace family has no exhaustive pass.** Only
  `exact_usable_all_R_B1_low_degree` exists, one configuration per cell, all in the low-degree
  family. The random-family result rests on 20 000 sampled draws and 10 configurations per
  cell — ample, but sampled. A scope limit, not negative evidence.
- **Any degree.** None measured, estimated or asserted (IMP-SEMBIN-ENGINE). The paper's own
  reason for preferring the low-degree window is a Gröbner matter and I quote it without
  evaluating it, so the trade-off between the yield penalty measured here and that claimed
  advantage is **not** assessed by this report.
- **Model verification.** `manifest.yaml` records `model_verified: false` for the producing
  session (no `doctor --probe`); my own session is in the same position. Disclosed on both
  sides, and it bears on provenance rather than on any number here.
- **J4, J5, J6-BLIND, and the claim as a whole.** Not mine. I read no sibling report and
  none existed. I offer no whole-claim verdict and no view on whether the
  eq. (11)-conditional closure in KN-FIND-9643e7 / DEC-20260913-74e208 survives; the
  `t < m` versus `t = m` comparison that question needs is, as the producer states, not
  available in this cell set, and I confirmed the cell list: eight of nine cells have t = m
  and the sole t < m cell is the degenerate one used above as the known-false object.

## Pointer recorded, not pursued

`task-report.md` §10 observes that EXP-RELN-164ad3's metric M3 residual is this run's
`f_base` under an encoding mismatch. That is outside my joints and I did not evaluate it. A
separate pointer for whoever holds RQ-SEMBIN-9e8f82: the subspace-variant dependence in J2
bears on any comparator that assumes eq. (11)'s Poisson link holds for a low-degree-window
factor base. Both are pointers, neither a finding.

---

```yaml
validation_report:
  id: VAL-20260913-31d530
  task_id: TASK-20260913-31d530
  review_round_id: REVIEW-SEMBIN-20260913-run2
  run_ids: [RUN-SEMBIN-1b9afe]
  experiment_ids: [EXP-SEMBIN-354a75]
  joints_owned: [J1, J2, J3]
  artifact_checks:
    - artifact_sha256_and_bytes: 6/6 match against artifact-digests.json
    - code_sha256: 11/11 match, plus yield_diagnose.py verified against manifest.yaml
    - snapshot_commit_binding: 40e1cf727 contains the package; only manifest_v2.yaml added since
    - working_tree_clean_for_object: true
    - command_revision_dirty_seeds_environment_resources: all present in manifest.yaml
    - coverage: unreached_cells empty, 180/180 configurations, reached_exhaustively true at 9/9
    - conservation_identity: recomputed exactly at 9/9 cells, no remainder
  metric_recomputations:
    - A_sem_P_n20: 0.902421 recomputed from per-R-counts.json, reported 0.902421
    - A_sem_P_n22_n24: 0.906869 / 0.907313 recomputed from per-R-counts.json, reported 0.906869 / 0.907313
    - D_observed_P_ratio_n20: 0.758277 recomputed, reported 0.758277
    - G_f_dispersion_n20_n22_n24: 0.909093 / 0.902011 / 0.902591 recomputed, reported 0.9091 / 0.9020 / 0.9026
    - identity_A_equals_G_times_f_mean_level: 0.909093 x 0.992660 = 0.902421, exact
    - four_factor_residual: 1.000000000000 at all 8 non-degenerate cells (claimed 1e-9)
    - exhaustive_vs_10000_same_configuration_draws: |z| <= 0.53 at all three m=t=2 cells
    - cluster_level_interval_n20: [0.8415, 0.9634] against reported Wilson [0.8905, 0.9144]
    - L_distribution: E[L] = |V| and sd(L) ~ sqrt(|V|) confirmed at 9/9 cells
  control_checks:
    - baseline: 33/33 to four decimals, truncation convention; correctly not read as support for eq. (11)
    - matched_null: f_dispersion 0.99982 / 1.00035 / 1.00017 at t=2, Poisson fit p 0.22-0.66; pipeline manufactures no deficit
    - known_false_class_count: t! shift reproduced in every cell
    - invalid_input: R at infinity, non-subspace V, wrong dimension all rejected
    - exhaustiveness: order-independent under 3 permutation seeds per audited cell
    - proves_too_much_assigned_to_this_task: machinery returns 0/0 and nan at L=3 and says so (PASSES); the argument built on it does not (attribution_closes vacuously True, denominator-free 100% shortfall, +24% and -100% under one cell label)
    - null_object_decay_check_mine: signal decays to exactly nothing when the subspace basis is randomised, matching the curve-free null
  verdicts_by_joint:
    J1: breaks
    J2: breaks
    J3: breaks
  verdict: incomplete
  verdict_rationale: >-
    The receipt is instrumentally sound and every recomputable quantity reconciles, so this is
    not `failed` and certainly not `invalid`: nothing is missing, stale or fabricated, the
    enumeration is exhaustive where claimed, and the exhaustive pass cross-validates against
    independent sampling. But the run's headline quantity marginalises a declared independent
    variable that determines the sign of the reported effect, its stated interval is computed
    under an independence assumption its own data violates, and its diagnosis changes
    averaging population between sections without saying so. A receipt whose headline cannot
    be read without those three corrections is not yet admissible as the evidence it is
    offered as, and the remedy is a re-summarisation of committed data rather than any new
    measurement. `incomplete` on the joints owned; the other joints are not mine and this is
    not a whole-claim verdict.
  limitations:
    - reports on J1, J2, J3 and the assigned proves-too-much control only
    - no mechanism identified for the low-degree clustering; association measured only
    - t >= 3 behaviour of that association confounded with small |V| in this cell set
    - only one exhaustive pass exists per cell, all in the low-degree family
    - no degree measured, estimated or asserted anywhere (IMP-SEMBIN-ENGINE)
    - no statement about any curve's security, in either direction
    - no hypothesis status moved, no evidence record, no decision, nothing promoted
  artifact_paths:
    - coordination/review/sembin-20260913-run2/TASK-20260913-31d530/report.md
    - coordination/review/sembin-20260913-run2/TASK-20260913-31d530/attestation.yaml
```
