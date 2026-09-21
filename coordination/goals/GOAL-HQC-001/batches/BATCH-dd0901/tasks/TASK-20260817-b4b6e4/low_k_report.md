# low_k_report.md -- TASK-20260817-b4b6e4

GOAL-HQC-001 / BATCH-dd0901 / EXP-HQC-982268 / H-HQC-18d1b4 (stays PROPOSED).
Authorized by DEC-20260817-2b638b. **Claim tier: TOY, hard ceiling.**

> **OBSERVATIONS ONLY.** This report applies NO branch of `batch.yaml`'s frozen
> reading rule, names no branch, states no collapse verdict, declares the
> coupled null BLIND in no verdict sense, and concludes nothing about the
> k-explanation, assumption A17, assumption A5, HQC's decoding-failure rate,
> HQC's IND-CCA security, any standardized parameter set, or what the campaign
> should do next. It changes no record's status. The frozen reading rule is the
> Coordinator's to apply at the ledger archive; the two independent reviews and
> that archive adjudicate.

## 0. What ran, and what did not

Two runs, both terminal, both successful:

| run | script | wall (s) | core (s) | decoder calls |
|---|---|---:|---:|---:|
| Part A | `low_k_recompute.py` | 0.7951 | 1.2875 | 0 |
| Part B | `coupled_null_control.py` | 11.8117 | 11.9427 | 0 |
| **total** | | **12.6068** | **13.2302** | **0** |

Against authorizations of 300 wall-clock seconds and 150 core-seconds: 4.20% and
8.82%. Every figure is MEASURED (`time.time()` and `resource.getrusage` deltas
recorded in-process), never estimated after the fact.

**Zero decoder calls, enforced fail-closed.** Part A imports no pinned decoder
module at all. Part B loads all three under sha256 pins, installs
call-counting wrappers on the LOADED `stage_a` module object's `_t_shard` and
`decode_blocks` (a call increments the counter and raises -- it never
delegates), and at exit asserts both counters are exactly 0 and re-measures all
three module sha256 values ON DISK. Measured at exit:
`{stage_a._t_shard: 0, stage_a.decode_blocks: 0}`, all three pins unchanged.
No file on disk was edited.

**Nothing planned was skipped.** The planted-departure leg is absent by
Coordinator direction and is a declared substitution, not an omission
(EV-HQC-e458ef O10, O11). What is NOT reported, and why, is section 2 below:
the low-k values of two historical cells, suppressed by the fail-closed
reconstruction gate.

## 1. Part A -- committed-value verifications, all seven groups

Run BEFORE any new number was reported. **No array selection, window pairing,
tolerance or fit method was adjusted to make any of these pass.**

| check | tol | outcome | largest measured residual |
|---|---|---|---:|
| V1 four fresh cells at k=17 | 1e-12 | **PASS (4/4)** | 0.0 (exact) |
| V2 three contrasts at k=17 | 1e-12 | **PASS (3/3)** | 0.0 (exact) |
| V3 four fresh cells at k=2 | 1e-4 | **PASS (4/4)** | 4.894e-07 |
| V4 both 4-point ladders at k=17 | 1e-3 | **PASS (2/2)** | 3.349e-05 (alpha), 1.148e-04 (resid RMS) |
| V5 same-T noise handle at k=17 | 1e-3 | **PASS (3/3)** | 1.829e-04 |
| V6 same-T noise handle at k=2 | 1e-3 | **PASS (2/2)** | 2.501e-04 |
| V7 historical reconstruction gate | 1e-12 | **2 PASS / 2 FAIL** | see section 2 |

Ladders at k=17 reproduce 0.4733665 (shard 5000, residual RMS 1.0081148, slope
standard error 1.4544022) and 0.0115161 (shard 8002, residual RMS 0.5139410,
slope standard error 0.7414601) against the committed 0.4734 / 1.008 and
0.0115 / 0.514.

## 2. The reconstruction gate -- the load-bearing step, and it did not pass clean

`batch.yaml`'s per-cell array mapping is the authoring Coordinator's
RECONSTRUCTION, recorded as such and not as fact. It was transcribed verbatim
into `design.md` section 2.5 before any datum existed. **No alternative pairing
was tried, computed, or considered**, and no cell's low-k values were reported
without its gate passing.

| cell | recomputed alpha(17) | committed | abs residual | gate (1e-12) | status |
|---|---:|---:|---:|---|---|
| shard 5000, regime P | 2.8360981651225576 | 2.836 | 9.8165e-05 | **FAIL** | `DATA_AVAILABILITY_OUTCOME` |
| shard 6000, regime P | 1.4019206406015738 | 1.402 | 7.9359e-05 | **FAIL** | `DATA_AVAILABILITY_OUTCOME` |
| shard 8001, regime N | -0.26824951570854555 | -0.2682495157085447 | 8.327e-16 | **PASS** | reconstruction verified |
| shard 8002, regime N | -0.8662355237627501 | -0.8662355237627483 | 1.887e-15 | **PASS** | reconstruction verified |

The two failing cells' low-k values are **NOT reported** and appear as `null` in
`low_k_recompute_results.json`. The mapping was not adjusted and the cells were
not dropped: their selected arrays, lengths, k ranges, `n_batches`, recomputed
values, comparators and residuals are all in
`historical_cell_reconstruction.json`.

**A comparator-precision fact, declared in `design.md` BEFORE the gate ran.**
The comparators `+2.836` and `+1.402` exist in the committed record only at four
significant figures (EV-HQC-469c08 O6, whose own source table prints its SE
inputs to six decimals). A 1e-12 absolute gate against a four-significant-figure
decimal can pass only if the underlying full-precision value is exactly that
decimal. The gate was applied exactly as specified and **its 1e-12 verdict
stands as the verdict.** Purely so the Coordinator can see the character of the
failure, each cell also carries a clearly subordinate diagnostic --
`residual_vs_printed_precision_halfulp` -- which is NOT a second gate, cannot
turn a FAIL into a PASS, and did not change `gate_pass` or `cell_status`. Both
failing residuals (9.82e-05, 7.94e-05) are below half an ulp of four-significant-
figure printing (5e-04). That is an observation about comparator precision. It
is not a claim that the mapping is correct, and this report draws no such
conclusion.

## 3. Part A -- the measured numbers

### 3.1 The eight cells at k=5 and k=10 (and k=2, k=17 for context)

| cell | k=2 | k=5 | k=10 | k=17 |
|---|---:|---:|---:|---:|
| FRESH 5000, P | 0.580733 | **0.697364** | 1.051457 | 2.048813 |
| FRESH 5000, N | 0.506553 | **0.455398** | 1.136112 | 2.960737 |
| FRESH 8002, P | 0.628397 | **0.606080** | 0.575713 | 0.323623 |
| FRESH 8002, N | 0.511866 | **0.492779** | 0.812011 | 1.594336 |
| HIST 5000, P | -- | -- | -- | (gate FAIL) |
| HIST 6000, P | -- | -- | -- | (gate FAIL) |
| HIST 8001, N | 0.374003 | **0.224446** | 0.071112 | -0.268250 |
| HIST 8002, N | 0.515715 | **0.410684** | 0.120915 | -0.866236 |

Two of the four historical cells are unavailable at every k by the gate, so the
four-cell historical set the frozen route contemplates is **not complete at any
k in this run**. That is a data-availability fact, recorded as one.

### 3.2 The three contrasts

| contrast | k=2 | k=5 | k=10 | k=17 |
|---|---:|---:|---:|---:|
| regime main effect | 0.095355 | **0.177633** | -0.160477 | -1.091319 |
| shard main effect | -0.026488 | **0.026951** | 0.399922 | 1.545795 |
| interaction | -0.042350 | **0.128666** | 0.151642 | 0.358789 |

### 3.3 The two 4-point ladders (P1, P2, N1, N2; alpha = -OLS slope in log-log)

| shard | k | alpha | residual RMS | OLS slope standard error |
|---|---:|---:|---:|---:|
| 5000 | 5 | 0.518424 | 0.050646 | 0.073067 |
| 5000 | 10 | 0.538768 | 0.272425 | 0.393026 |
| 5000 | 17 | 0.473367 | 1.008115 | 1.454402 |
| 8002 | 5 | 0.482827 | 0.038093 | 0.054957 |
| 8002 | 10 | 0.385803 | 0.156443 | 0.225699 |
| 8002 | 17 | 0.011516 | 0.513941 | 0.741460 |

Residual RMS is `sqrt(mean(resid^2))` over the four points (n, not n-2); the
slope standard error is the ordinary OLS one on 2 residual degrees of freedom.
All k in 2..26 are in `low_k_recompute_results.json`
(`four_point_ladders_by_k.<shard>.<k>`).

### 3.4 The same-T noise handle, the band-free yardstick

`D_shard(k) = |log2( se_paired(P2,k) / se_paired(N1,k) )|`; P2 and N1 are both
T=10,000, same shard, same jackknife batch size 50, same procedure, same call,
disjoint indices.

| k | D(5000) | D(8002) | D_RMS |
|---:|---:|---:|---:|
| 2 | 0.060834 | 0.104750 | 0.085654 |
| 5 | **0.115914** | **0.133205** | **0.124859** |
| 10 | 1.110033 | 0.616119 | 0.897713 |
| 17 | 4.062817 | 1.894927 | 3.169955 |

It is reported at every k in 2..26 in the results JSON. **Its stated limit is
not softened: it is a SCALE FROM n = 2 CONTRASTS, not a distribution. No
confidence interval is computable from it and none is claimed**
(EV-HQC-e458ef boundaries).

### 3.5 The eight real cells' `se_unpaired/se_paired` range (input to SHAPE)

| k | min | max |
|---:|---:|---:|
| 5 | 8.545049 | 11.126178 |
| 10 | 4.937997 | 11.905557 |
| 17 | 2.338019 | 28.691278 |

The k=17 range reproduces the committed [2.338, 28.691] exactly.

## 4. Part B -- the coupled-arm null band

**One structural change and nothing else.** `base ~ Binomial(55, p)` shared by
both arms; `arm_i = base + Bernoulli_i(p)` with an independent Bernoulli per
arm. `p` FROZEN at 0.31923392857142857, **not re-calibrated**. Ladder T in
{5000, 10000, 20000, 40000}, R = 200, five independent cell streams, same pinned
`arm_hists` / `evaluable_k` / `comb_matrix` / `matched_pair_stats` /
2-point-OLS chain, imported read-only. Both fail-closed selftests PASS.
`evaluable_k` was identical (2..26) across all 4,000 draws.

**Realized marginal check (this is what makes the comparison controlled).**
Over 150,000,000 arm draws: realized mean 17.877370 against Binomial(56, p)'s
17.877100 (Monte Carlo SE of the mean 2.85e-04, so 0.95 MC-SE out); realized
variance 12.173360 against 12.170123 (approx MC SE 1.41e-03, so 2.30 MC SE out).
Both arms separately are within 3 MC SE on mean and variance. The coupling
itself is confirmed directly: `arm_0 == arm_1` on 0.5653434 of trials against
the analytic `p^2 + (1-p)^2 = 0.5653527`.

**No reduction fired.** The pre-registered probe -- the first 20 replicates of
the T=40000 rung, 5 streams, 4,000,000 trial units -- MEASURED 0.500001
core-seconds (0.501450 wall), giving 1.250e-07 core-seconds per trial unit and a
projected total Part B cost of 9.375 core-seconds against the 90.0 core-second
trigger (60% of the 150 core-second authorization). So
`no_reduction_fired: true`, achieved R = 200, achieved rungs all four.
Part B is **not** underpowered by the pre-registered protocol, and its bands are
not being presented as anything other than what they measure.

### 4.1 The five separately simulated banded contrasts

Every one is formed DIRECTLY from four independent null cells per replicate (a
fifth for the replication delta). **No single alpha was banded and
algebraically rescaled** -- the defect DEC-20260817-2b638b rationale item (j)
named.

| k | contrast | mean | SD | 95% interval | width | measured/analytic SD ratio | >10%? |
|---:|---|---:|---:|---|---:|---|---|
| 5 | single cell alpha | 0.48746 | 0.11579 | [0.2626, 0.6994] | 0.4368 | 1.000 / 1.000 | no |
| 5 | regime main effect | -0.01303 | 0.11376 | [-0.2288, 0.1831] | 0.4119 | 0.9825 / 1.000 | no |
| 5 | shard main effect | -0.00272 | 0.11304 | [-0.2107, 0.2108] | 0.4214 | 0.9762 / 1.000 | no |
| 5 | interaction | -0.00810 | 0.21376 | [-0.4000, 0.4102] | 0.8102 | 1.8460 / 2.000 | no (7.70%) |
| 5 | replication delta | -0.00128 | 0.16715 | [-0.3034, 0.3751] | 0.6784 | 1.4436 / 1.414 | no |
| 10 | single cell alpha | 0.49527 | 0.30719 | [-0.1486, 1.1077] | 1.2563 | 1.000 / 1.000 | no |
| 10 | regime main effect | -0.02404 | 0.25863 | [-0.5314, 0.4572] | 0.9886 | 0.8419 / 1.000 | **YES (15.81%)** |
| 10 | shard main effect | 0.01571 | 0.26559 | [-0.4941, 0.5328] | 1.0268 | 0.8646 / 1.000 | **YES (13.54%)** |
| 10 | interaction | 0.01026 | 0.63219 | [-1.1934, 1.3760] | 2.5694 | 2.0580 / 2.000 | no |
| 10 | replication delta | 0.02681 | 0.48283 | [-0.8506, 1.0014] | 1.8520 | 1.5717 / 1.414 | **YES (11.16%)** |
| 17 | single cell alpha | 0.38098 | 1.01741 | [-1.7188, 2.2071] | 3.9260 | 1.000 / 1.000 | no |
| 17 | regime main effect | -0.07233 | 0.90882 | [-1.7473, 1.6800] | 3.4273 | 0.8933 / 1.000 | **YES (10.67%)** |
| 17 | shard main effect | 0.03537 | 0.93614 | [-1.7735, 1.8344] | 3.6079 | 0.9201 / 1.000 | no (7.99%) |
| 17 | interaction | 0.11318 | 2.09311 | [-3.8790, 4.4850] | 8.3640 | 2.0573 / 2.000 | no |
| 17 | replication delta | 0.07678 | 1.58222 | [-2.9362, 3.1766] | 6.1128 | 1.5551 / 1.414 | no (9.98%) |

**FOUR SD-RATIO DISCREPANCIES ABOVE 10% ARE REPORTED AS FINDINGS AND NOT
SMOOTHED**: regime main effect at k=10 (15.81%) and k=17 (10.67%), shard main
effect at k=10 (13.54%), replication delta at k=10 (11.16%). Three of the four
are contrasts of MEANS whose measured SD ratio is BELOW the analytic 1.000, and
one (replication delta at k=10) is ABOVE 1.414. The analytic factors assume the
cells are independent draws from one law, which they are by construction here;
the executor records the discrepancy and offers no explanation for it.

### 4.2 k=17 band widths beside the committed comparators

Coupled, this batch: single cell alpha 3.9260; regime main effect 3.4273; shard
main effect 3.6079; interaction 8.3640; replication delta 6.1128.
Committed uncoupled (BATCH-91929e): 2.788 and 3.188.
Reviewer-built coupled: 3.398, 3.508, 4.326.
Reported side by side as measured; no conclusion is drawn about what the
comparison implies.

### 4.3 The two blindness tests -- PASS/FAIL, no interpretation

**SHAPE** -- is the coupled null's median `se_unpaired/se_paired` at order k
inside the closed range spanned by the eight real cells at the same k?

| k | coupled null median (pooled) | real cells' range | verdict | per-rung verdicts |
|---:|---:|---|---|---|
| 5 | 5.143413 | [8.545049, 11.126178] | **FAIL** | FAIL at all four rungs |
| 10 | 4.301179 | [4.937997, 11.905557] | **FAIL** | FAIL at all four rungs |
| 17 | 2.826520 | [2.338019, 28.691278] | **PASS** | PASS at all four rungs |

`design.md` section 3.5 did not disambiguate pooling across rungs, so both the
pooled median and every per-rung median are reported with their own verdicts.
They agree at every k. For reference, BATCH-91929e's uncoupled null returned
0.9965 / 0.9984 on the same statistic.

**POWER** -- does each banded contrast's minimum detectable effect
`max(|p2.5|, |p97.5|)` stay at or below 3.702 alpha units?

| k | single cell | regime ME | shard ME | interaction | replication delta |
|---:|---|---|---|---|---|
| 5 | PASS 0.6994 | PASS 0.2288 | PASS 0.2108 | PASS 0.4102 | PASS 0.3751 |
| 10 | PASS 1.1077 | PASS 0.5314 | PASS 0.5328 | PASS 1.3760 | PASS 1.0014 |
| 17 | PASS 2.2071 | PASS 1.7473 | PASS 1.8344 | **FAIL 4.4850** | PASS 3.1766 |

**The executor declares the control BLIND in no verdict sense.** These are the
mechanical outcomes of two pre-declared arithmetic tests. `batch.yaml`'s frozen
rule reads them.

## 5. The 2-point local exponent and what dominates it

Wherever this report characterises the 2-point local exponent, the standing
`dominated_by` value is recorded verbatim:

> **"4-rung OLS in log-log on identical data, SD 0.234334 against 0.700666, a
> 2.99x noise reduction at zero cost."**

That is the committed, UNCOUPLED figure. This batch's OWN measured SDs on ITS
COUPLED replicates (stream `cell_5000_P`, R=200, rungs {5000, 10000, 20000,
40000}), reported beside it and never in place of it:

| k | measured SD, 2-point | measured SD, 4-rung OLS | measured noise-reduction factor |
|---:|---:|---:|---:|
| 5 | 0.115794 | 0.031710 | 3.652x |
| 10 | 0.307191 | 0.082533 | 3.722x |
| 17 | 1.017414 | 0.295875 | 3.439x |

The 2-point estimator this campaign's cells are built on is dominated by a
4-rung OLS on identical data at every k measured here as well as in the
committed uncoupled record. `dominated_by` is not null and asserting otherwise
would be a fabrication under AGENTS.md rule 9 and a violation of
`docs/inventor-protocol.md`'s Pareto-honesty obligation.

## 6. Limitations, declared here rather than left for a reviewer

1. **The fresh-versus-historical procedural asymmetry.** In every HISTORICAL
   cell the two T-points come from DIFFERENT tasks in DIFFERENT processes -- and
   in this campaign's case also different machines, operating systems, Python
   versions and numpy versions (`a79e4f`: Linux x86_64, Python 3.11.15, numpy
   2.4.6, 4 cores; `8bbdd2` and `e61cca` likewise separate runs; the FRESH
   arrays: macOS arm64, Python 3.13.1, numpy 2.4.0, 14 cores). In all four
   FRESH cells both T-points are sliced from ONE call in ONE process
   (EV-HQC-e458ef O4, O18). **This is a standing limitation of any
   fresh-versus-historical comparison built from these eight cells.** Every
   array read reports its `n_batches` (200 for all eight historical arrays and
   all eight fresh windows) in `historical_cell_reconstruction.json` and
   `low_k_recompute_results.json.fresh_window_metadata`.
2. **Two of the four historical cells are unavailable at every k.** Any
   historical-set statement from this run rests on two cells, both regime N,
   both from the 8001/8002 shard family. The regime-P half of the historical set
   is absent.
3. **The same-T noise handle is a scale from n = 2 contrasts**, not a
   distribution. No interval is computable from it and none is claimed.
4. **The null object is shard-free and defect-free by construction.** Its
   "shard" and "regime" cell labels carry no distinct law; the analytic SD
   factors follow from cell independence alone. Nothing in Part B measures the
   real object.
5. **Pre-registration is content-corroborated, not independently anchored.**
   The executing session does not commit, so no pre-fill blob was committed by
   it. `design.md` was closed before either driver ran and both drivers measured
   its sha256 (`4fdf71da68c81fb9f649e9a058f86ffb9917f183c361e290565f58681d9c77b5`)
   at launch, before any statistic. No anchor line was hand-authored into
   `stdout.log`. This is the same weakness EV-HQC-e458ef O15(a) recorded against
   BATCH-91929e, restated rather than papered over.
6. **Scope.** PS-R3 only (n=7187, n_e=56, n_2=128, dup=1, N=7168, k in 2..26,
   m=17, N_JACK_BATCHES=200); shards 5000, 6000, 8001, 8002; the trial ranges
   and windows named in `design.md`; R=200 coupled null replicates on four
   rungs. Nothing here is a measurement of HQC.
7. **The persist-per-trial-S standing requirement does not bind on this task.**
   DEC-20260817-2b638b next_actions item (3) makes it effective from the NEXT
   SAMPLING TASK. This task makes zero decoder calls and samples nothing, so it
   is not a sampling task. **It is carried forward by name to the next sampling
   task in this family -- the next task that calls `stage_a._t_shard`.**
