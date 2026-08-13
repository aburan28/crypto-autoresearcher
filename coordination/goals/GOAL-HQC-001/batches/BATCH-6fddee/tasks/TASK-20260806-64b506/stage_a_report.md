# Stage A of `EXP-HQC-982268` — instrument validation: OBSERVATIONS

**Task** `TASK-20260806-64b506` (executor) · **Batch** `BATCH-6fddee` ·
**Goal** `GOAL-HQC-001` · **Question** `RQ-HQC-001`
**Contract** `experiments/EXP-HQC-982268/specification.yaml` ·
**Hypothesis** `H-HQC-18d1b4` · **Authorizing decision** `DEC-20260806-5289fb`
**Produced** 2026-08-06 · **Repo commit at run** `cab9633ec1dbf488a57012129d6970a6ad17f7b2`
(branch `claude/harness-goals-experiments-g5pt2o`; tree dirty only in this
task's own untracked directory)

Machine-readable companion: `stage_a_results.json`. Every number below is
produced by `stage_a.py` and is present in that file. Nothing is transcribed
by hand except where a two-term sum is stated and its two terms are named.

---

## 0. Scope, stated before any number

This document records **observations only**. It draws no conclusion, assigns
no evidence strength, and changes no status — those are Reviewer and
Coordinator acts.

- Execution was authorized for **Stage A only**, 1692 core-seconds, 4 cores,
  2 GB, one run (`DEC-20260806-5289fb`). Stages B1–B4 and C were **not run**.
- **`log2_A_k` and `log2_A_m` are NOT computed or reported on any space-(T)
  arm.** That is the measurement of `EXP-HQC-982268` and it is not
  authorized. Joint-moment numbers appear below **only on the three
  i.i.d.-by-construction null arms**, because the contract's `INV-NULL` gate
  is *defined* as a statement about `log2 Ahat_k` on those arms and is
  otherwise not evaluable at all. This reading is declared here rather than
  assumed silently.
- Stage A validates an **instrument**. It says nothing about HQC, about
  assumption A17 or A5, about any decoding-failure rate, or about any
  standardized HQC parameter set. **Claim tier: TOY**, hard ceiling
  (`RQ-HQC-001.claim_tier_ceiling`, `AGENTS.md` rule 7).
- No timeout, crash, or resource exhaustion occurred. Where something was not
  run or not evaluable, it is named as such in §8 and is an
  infrastructure/budget outcome, never a mathematical result
  (`AGENTS.md` rule 5).

---

## 1. What ran, and what it cost

One invocation of `stage_a.py`, plus one deterministic post-processing pass
that samples nothing (§9, and `run_manifest.yaml` `protocol_deviations`).

| phase | core-seconds | wall-seconds |
|---|---|---|
| oracle gate (re-run + test suite) | 20.64 | 20.60 |
| contract structural checks | 0.011 | — |
| smoke self-tests | 0.269 | — |
| throughput calibration | 1.023 | — |
| **(T) arms, 4 sets × 4 shards** | **1024.54** | 263.17 |
| **NULL-M arms, 4 sets × 4 shards** | **332.64** | 85.81 |
| analysis (NULL-P, CTRL-BS, INV-NULL, sizing) | 31.99 | — |
| **total accounted** | **1411.12 / 1692** | **403.02** |

`getrusage` total (self + children) 1413.59 core-seconds — consistent with the
accounted figure. Peak RSS 356 MB parent, 270 MB largest child, against the
2 GB cap. No shard was wall-clock truncated at any set or any arm.

Trials completed: **1 965 576** on (T), **1 785 528** on NULL-M,
**40 000 000** on NULL-P, and 20 block-shuffle replicates per set on CTRL-BS.

**Measured throughput against the contract's modeled figure.** The contract
models Stage A as 8 000 000 trials in 1692 core-seconds, i.e. **4728
trials/core-second**, and states that every entry in that table is modeled,
not measured, with a declared 2× implementation contingency.

| set | measured trials/core-second | modeled | ratio |
|---|---|---|---|
| PS-A | 1667 | 4728 | 0.35× |
| PS-R1 | 2555 | 4728 | 0.54× |
| PS-R3 | 2061 | 4728 | 0.44× |
| PS-R5 | 1502 | 4728 | 0.32× |

The composed pipeline is **1.9× to 3.1× slower than modeled**, i.e. the
declared 2× contingency is at or beyond its limit at three of the four sets.
Recorded as a measurement of this implementation on this host; no claim is
made that a different implementation could not be faster.

---

## 2. GATE — oracle agreement · **EVALUATED, AGREES**

The committed instrument at
`…/BATCH-003/tasks/TASK-20260803-6f50df/` was re-used, not reimplemented.

**(a) Committed file integrity.** sha256 of `oracle.py`, `test_oracle.py` and
`oracle_values.json` each **match** the values published in
`oracle_report.md`'s deliverables table (`96c54ed5…`, `b3c52cc0…`,
`a3d65582…`).

**(b) Re-run against the committed values.** Command
`python3 oracle.py --out <scratch>/oracle_values_rerun.json --seed 20260803`,
exit code 0, 20.6 s. Structural deep-diff of the re-run against the committed
`oracle_values.json`:

| difference class | count | verdict |
|---|---|---|
| **computed values** | **0** | full agreement |
| timings | 27 | expected; enumerated in the JSON |
| provenance | 5 | expected; enumerated below |

The 27 timing differences are exactly the keys `oracle_report.md` §6 names as
the only run-to-run variation: `results/timings/*` and the per-row `seconds`
entries under `reach_demonstrations` and `measured_scaling`. The 5 provenance
differences are `/provenance/command` (this run's `--out` path),
`/provenance/git_branch`, `/provenance/git_commit`,
`/provenance/git_dirty_paths/[0]` and `/provenance/platform` — all of which
differ because this is a different branch, commit and container, and none of
which is a computed value.

**Every one of the oracle's computed values, verdict flags and reference
numbers reproduced identically.**

**(c) Committed test suite.** `python3 test_oracle.py` — exit code 0,
**43 tests, all pass**, 2.97 s. This includes the suite's own known-answer
table, its mutant detection, its Route A / Route B cross-checks and its
subset-exchangeability checks.

No disagreement was found, so nothing had to be papered over. `PYTHONDONTWRITEBYTECODE=1`
was set for both subprocesses; the sibling task directory is byte-identical
after the run and no `__pycache__` was left in it.

---

## 3. Contract structural checks · **EVALUATED, ALL MATCH**

Recomputed from the contract's own rules, not read off the table.

| set | ring rule `n` computed | tabulated | match | \|τ_computed − τ_tabulated\| |
|---|---|---|---|---|
| PS-A | 17669 | 17669 | yes | 3.0e−6 |
| PS-R1 | 5923 | 5923 | yes | 8.3e−7 |
| PS-R3 | 7187 | 7187 | yes | 6.3e−6 |
| PS-R5 | 11549 | 11549 | yes | 1.0e−6 |

`n` was recomputed as the smallest prime above `N` with 2 primitive modulo it
(SPEC §4.1's own rule), by an independent Miller–Rabin plus multiplicative-order
test. `N = n_e·n_2`, `n_2 = 128·dup` and `d_i = 64·dup` hold at all four sets.
A mismatch would have been `failed_implementation` (`INV-INVARIANT`); none
occurred.

**`INV-Q` — partially evaluable.** The rigorous lower end
`P[Bin(d_i,p*) > d_i/2] + ½P[Bin(d_i,p*) = d_i/2]` was computed in exact
rational arithmetic at every set. The upper end `p_i` (Prop. 6.1.4) is
available **only at PS-A**, from the contract's own frozen fixture
(`log2 p_i = −10.7950`).

| set | bracket low (log2) | bracket high (log2) | measured `log2 qhat` | inside? |
|---|---|---|---|---|
| PS-A | −18.541 | −10.795 | **−11.546** | **yes** |
| PS-R1 | −7.262 | not evaluable | −2.341 | not evaluable |
| PS-R3 | −6.145 | not evaluable | −1.644 | not evaluable |
| PS-R5 | −5.474 | not evaluable | −1.272 | not evaluable |

*Why the upper end is not evaluable at the reduced sets:* Proposition 6.1.4's
closed form for `p_i` is not transcribed anywhere in this task's read scope
(it lives in `BATCH-001`'s `dfr_model_transcription.md`), and the frozen
fixture supplies `p_i` only at HQC-1/3/5, i.e. at `dup` 3 and 5, never at
`dup = 1`. Reconstructing the formula from memory would be fabrication, so
the upper end is reported as **NOT EVALUABLE** rather than guessed. At the
reduced sets `qhat` is above the rigorous lower end, which is the half of the
bracket that could be checked.

---

## 4. (T) sampler diagnostics

| set | T | `qhat` | `phat` | `p*` (contract) | `phat − p*` | `gammahat` | `Corr(W_i,W_j)` | `Var(W_1)` (binomial ref.) | tie rate |
|---|---|---|---|---|---|---|---|---|---|
| PS-A | 527 928 | 3.3445e−4 | 0.3397888 | 0.339788 | **+6.1e−7** | **0.7364** | −0.005759 | 85.63 (86.14) | 3.135e−4 |
| PS-R1 | 572 588 | 0.197427 | 0.3479150 | 0.347921 | **−6.0e−6** | **0.7532** | −0.005400 | 28.89 (29.04) | 0.15095 |
| PS-R3 | 511 228 | 0.319946 | 0.3649440 | 0.364929 | **+1.5e−5** | **0.7903** | −0.003757 | 29.55 (29.67) | 0.21111 |
| PS-R5 | 353 832 | 0.414120 | 0.3761890 | 0.376188 | **+5.2e−7** | **0.8127** | −0.002086 | 29.98 (30.04) | 0.24900 |

Two observations recorded without interpretation:

- `phat` reproduces the contract's tabulated analytic `p*` to between
  **5.2e−7 and 1.5e−5** at all four sets. `p*` was not used as an input to
  the (T) sampler at any point; it enters `stage_a.py` only as a tabulated
  constant to compare against and as the NULL-M/calibration marginal.
- `gammahat` at PS-A is **0.7364**, against the published-derived values
  `0.7350 / 0.7355 / 0.7325 / 0.7249` that the contract records for HQC-1's
  four tail depths.

### 4.1 Upper-tail quantiles of `w(etilde)` at PS-A vs SPEC Table 10 (`D4`/`TC-1`)

| tail | observed | SPEC Table 10 | deviation | trials needed | achieved |
|---|---|---|---|---|---|
| 1e−3 | 6169.0 | 6169 | **0.0** | ≥ 1e3 | 527 928 |
| 1e−4 | 6201.0 | 6203 | **−2.0** | ≥ 1e4 | 527 928 |
| 1e−5 | 6233.4 | 6232 | **+1.4** | ≥ 1e5 | 527 928 |
| 1e−6 | — | 6257 | **NOT REACHED** | ≥ 1e6 | 527 928 |

Three of the four tails are reachable at the authorized budget and all three
deviate by **less than 3 weight units**. The 1e−6 tail requires at least
10^6 trials against 527 928 achieved: it is **NOT REACHED**, a budget
outcome, not a deviation. `D4`'s stated trigger (deviation > 3 units at ≥ 2
of 4 tails) did not fire on the tails that could be evaluated.

### 4.2 `TC-2` — `qhat` at PS-A vs SPEC Table 11 · **NOT EVALUABLE AS SPECIFIED**

`qhat` (this decoder, lowest-index tie rule) `= 3.3445e−4 = 2^−11.546`.
SPEC Table 11's observed inner DFR is `2^−10.96 = 5.020e−4`. The gap is
**−0.586 bits**, against `TC-2`'s stated tolerance of 0.30 bits.

That comparison **cannot be closed at this run**, for a reason measured here
and recorded in §7.1: the contract requires *both* deterministic tie
conventions to be reported and only one was implemented. Because a tie can
only ever move a block from success to failure when the zero-codeword index
is inside the tied argmax set, the second convention's `qhat` lies rigorously
in `[qhat, qhat + tie_rate]`, i.e.
`[3.3445e−4, 6.4794e−4] = [2^−11.546, 2^−10.592]` —
**and `2^−10.96` lies inside that interval.** `TC-2` is therefore reported as
NOT EVALUABLE pending the second convention, not as passed and not as failed.

---

## 5. GATE — drift and invariant detectors

| detector | status | observation |
|---|---|---|
| **D1** `gammahat` | **EVALUATED, no alarm** | 0.7364 / 0.7532 / 0.7903 / 0.8127 at PS-A/R1/R3/R5; none in the drift band [0.95, 1.05]. PS-A's extra requirement `gammahat ∈ [0.55, 0.85]` is **met** (0.7364). Approximate SE `√(2/(T−1))` = 1.9e−3 … 2.4e−3. |
| **D1 on NULL-M** (`TC-5`) | **EVALUATED, passes** | `gammahat` = 1.00034 / 1.00446 / 0.99868 / 1.00081, i.e. `z` = +0.20 / **+2.22** / −0.58 / +0.28 against the theoretical 1. All four within 3 SE. The +2.22 at PS-R1 is the largest and is recorded rather than smoothed. |
| **D2** exact weights | **EVALUATED, 0 deviations** | Checked on **every one of 1 965 576** (T) trials, twice per vector: as index-set cardinality after Floyd sampling and as the popcount of the constructed ring element. `(ω, ω, ω_r, ω_r, ω_e)` held on all 9 827 880 vectors. |
| **D3** support cap | **EVALUATED, 0 violations — but see §7.2** | `w(etilde) ≤ 2ωω_r + ω_e` and the same on `w(e'')`, every trial. Max observed vs cap: 6254/9975, 2202/3476, 2782/4641, 4549/7973. |
| **D5** CTRL-REPLAY | **EVALUATED, 0 mismatches** | 400 trials per set (1600 total), `etilde` re-derived bit-for-bit from the recorded seed through an independent dense-GF(2) path (single big-integer multiply in base 256) sharing no shift, XOR or mask with the production sparse shift-XOR path. Bit-identity held on all 1600. |
| **D4** Table 10 tails | **PARTIALLY EVALUATED** | §4.1: 3 of 4 tails evaluated and within tolerance; the 1e−6 tail NOT REACHED at the authorized T. |

`D5` was run at **400 trials per set against the contract's 1e4**, because
CTRL-REPLAY is nominally a stage-C control and stage C is not authorized;
400/set is what Stage A's share of the budget affords. Recorded as a reduced
sample count, not as CTRL-REPLAY discharged.

---

## 6. GATE — `INV-NULL` on the three null arms

`INV-NULL` fires at a cell when `|log2 Ahat_k| > 3·SE_null`. **324 cells** were
evaluated across 4 sets × 3 arms; **28 fired**.

Cells were admitted for reporting when at least 30 trials had `S ≥ k`. That
floor is **weaker than the contract's own `T_stab = 30/P[S ≥ s_90]`**, so
every cell is additionally cross-referenced against `T_stab` recomputed at
that arm's own `qhat` (`INV_NULL_vs_T_stab` in the JSON). The result:

| set | arm | T | largest `k` with `T ≥ T_stab` | `k` where INV-NULL fired | fired **while** `T ≥ T_stab` |
|---|---|---|---|---|---|
| PS-A | NULL-P | 1e7 | 2 | — | — |
| PS-A | NULL-M | 662 268 | 2 | — | — |
| PS-A | CTRL-BS | 527 928 | 2 | — | — |
| PS-R1 | NULL-P | 1e7 | 14 | — | — |
| PS-R1 | NULL-M | 497 632 | 11 | 11 … 20 | **k = 11** |
| PS-R1 | CTRL-BS | 572 588 | 11 | — | — |
| PS-R3 | NULL-P | 1e7 | 18 | — | — |
| PS-R3 | NULL-M | 385 732 | 15 | 25 … 32 | — |
| PS-R3 | CTRL-BS | 511 228 | 15 | — | — |
| PS-R5 | NULL-P | 1e7 | 29 | 49 … 58 | — |
| PS-R5 | NULL-M | 239 896 | 22 | — | — |
| PS-R5 | CTRL-BS | 353 832 | 22 | — | — |

**Of 151 cells that the contract's own `T_stab` rule would admit, exactly one
fired.** Of the 173 cells beyond `T_stab`, 27 fired.

### 6.1 The one admissible firing, stated in full

PS-R1, NULL-M, `k = 11`: `log2 Ahat_11 = −0.111265`, jackknife SE `0.035350`
over 200 contiguous batches, `|z| = 3.15` against the threshold 3.
`T_stab(11) = 465 873` against `T = 497 632` — the cell clears `T_stab` by
6.8 %, and `k = 12` does not clear it at all (`T_stab(12) = 1 711 338`).

It is not an isolated cell. On this arm `|z|` rises monotonically with `k`:

`k` = 2 … 14 → `|z|` = 1.14, 1.44, 1.75, 2.05, 2.30, 2.49, 2.63, 2.77, 2.93,
**3.15**, 3.45, 3.84, 4.31,

with `log2 Ahat_k` monotonically negative throughout and the jackknife bias
estimate negative at every `k`. The firing at `k = 11` is where a smooth,
one-signed drift crosses the threshold, not a jump.

NULL-M is the arm on which `A_k = 1` is a *theorem* (blocks are functions of
disjoint independent coordinates). The direction of every firing on every arm
is **negative**, which is the direction a right-skewed `C(S,k)` produces when
the large-`S` region carrying the estimand's mass is undersampled. Whether
`k = 11` here is a chance excursion among 151 admissible cells or evidence
that the contract's `T_stab` threshold of 30 (which the contract itself calls
"a judgement, not a theorem") is too loose near its boundary is a **Reviewer
question and is not adjudicated here**.

### 6.2 The nulls did fail somewhere, which is informative in itself

`INV-NULL` firing at 28 cells demonstrates that these arms are **capable of
failing** with the estimator and SEs as implemented. The set of firing cells
is, with the single exception above, exactly the set of cells the contract's
own sizing rule would have excluded — so on this run the null arms behaved as
undersampling detectors.

---

## 7. Defects and limitations found — reported because they were found

### 7.1 The tie rule: one of two required conventions was implemented

`EXP-HQC-982268.inputs.decoder` requires the deployed deterministic rule
broken by lowest index **and** states "the two deterministic conventions
bracket it and **both are reported**". Only the lowest-index convention was
implemented and run. **This is a protocol deviation.**

It is material, not cosmetic, and the measured tie rates say by how much:

| set | tie rate | `qhat` (lowest index) | rigorous upper end `qhat + tie_rate` |
|---|---|---|---|
| PS-A | 3.135e−4 | 3.3445e−4 | 6.4794e−4 |
| PS-R1 | 0.15095 | 0.197427 | 0.348381 |
| PS-R3 | 0.21111 | 0.319946 | 0.531055 |
| PS-R5 | 0.24900 | 0.414120 | 0.663122 |

The tie rate is **93.7 % of `qhat` at PS-A** and **60 % to 77 % of `qhat`** at
the three `dup = 1` sets — a first-order effect, not a rider. The bracket is
rigorous:
the two conventions differ on a block only when the tied argmax set contains
the zero-codeword index, so `q_highest = q_lowest + P[tie ∧ 0 ∈ argmax ∧ WHT_0 > 0]`,
which lies in `[q_lowest, q_lowest + P(tie)]`. The second convention is
**unrun**, and until it is run, `qhat` at every set is bracketed rather than
determined, and `TC-2` is not evaluable (§4.2).

### 7.2 `D3` cannot fail on the object it is advertised to detect

The contract states that `w(etilde) ≤ 2ωω_r + ω_e` is "a hard support cap on
(T), **violated with probability ~1 on (M)**", and lists `D3` among the "hard
invariants that cannot be satisfied by an (M) sampler". **At these four
parameter sets that is not so.**

| set | cap `2ωω_r + ω_e` | `N·p*` = mean `w` on (M) | cap / mean | distance in (M) standard deviations |
|---|---|---|---|---|
| PS-A | 9975 | 6002 | 1.66× | ≈ 63 σ |
| PS-R1 | 3476 | 2049 | 1.70× | ≈ 39 σ |
| PS-R3 | 4641 | 2616 | 1.77× | ≈ 50 σ |
| PS-R5 | 7973 | 4334 | 1.84× | ≈ 70 σ |

On space (M), `w(etilde) ~ Binomial(N, p*)`, whose mean is 1.66–1.84× **below**
the cap and whose standard deviation puts the cap 39–70 σ into the upper tail.
An (M)-drifted sampler would violate `D3` with probability indistinguishable
from zero, not ~1. `D3` remains a valid hard invariant against a grossly
malformed sampler — and it was evaluated on every trial with 0 violations —
but it is **not a (T)-versus-(M) discriminator at these parameters**, contrary
to the rationale the contract gives for it. The detectors that did bear on
that question here are `D1` (§5), the `phat` agreement and the Table 10 tail
comparison (§4).

### 7.3 `CTRL-BS`'s expectation is not exactly 1

The contract asserts that on CTRL-BS "`E[Ahat_k] = 1` **EXACTLY**, for every
`k`, by construction". Under the shuffle, block `j` of a pseudo-trial comes
from a distinct true trial, so the numerator estimates
`e_k(q_0,…,q_{n_e−1})/C(n_e,k)` — the elementary symmetric mean of the
**per-block** marginals — while the denominator is `qbar^k`. Maclaurin's
inequality gives `e_k/C(n_e,k) ≤ qbar^k` with equality **iff every `q_j` is
equal**. So `E[log2 Ahat_k^BS] ≤ 0` with a computable floor, not 0 exactly.

Computed from the recorded per-block marginals, the floor is numerically
negligible here: at PS-R1 it is `−2.3e−7` bits at `k = 2` and `−2.8e−5` bits
at `k = 16`, i.e. **8.2e−4 and 9.6e−5 times the SE actually used**, and the
same order at every set (per-cell values in
`ctrl_BS_expectation_analysis`). The contract's claim as written is
inexact; the inexactness does not compromise `INV-NULL` at the achieved `T`.

### 7.4 What the three null arms structurally cannot detect

Recorded so the coverage is not overstated:

- **NULL-P** draws `S ~ Binomial(n_e, qhat)` directly. It touches no ring, no
  sampler, no truncation and no decoder. It can only detect an error in the
  `C(S,k)/C(n_e,k)` arithmetic, the ratio and the jackknife.
- **NULL-M** exercises the decoder and the estimator on i.i.d. coordinates. It
  does not touch the fixed-weight sampler, the ring product or the truncation.
- **CTRL-BS** re-indexes the **(T) arm's own indicator matrix**. It therefore
  cannot detect any decoder or sampler defect at all — a wrong `F_j` enters
  the null and the thing it controls identically. It detects estimator and
  pipeline artifacts only.

Consequently **no null arm in Stage A tests whether the (T) joint law is
correct.** The checks that bear on the (T) object are `D2`, `D5`, the `phat`
agreement (§4), `D1` (§5) and the Table 10 tail comparison (§4.1) — and, per
§7.2, not `D3`.

### 7.5 `INV-NULL` at PS-A is evaluable only at `k = 2`

At `qhat = 3.34e−4`, `T_stab(2) = 261 685` and `T_stab(3)` is far beyond the
authorized budget; `T_stab(16) = 1.25e45`. All three arms reached `k = 2`
only:

| arm | `k = 2` value | SE | `|z|` | trials with `S ≥ 2` |
|---|---|---|---|---|
| NULL-P | −0.020908 | 0.041476 | 0.50 | 1123 |
| NULL-M | +0.104177 | 0.151859 | 0.69 | 83 |
| CTRL-BS | −0.037446 | 0.208110 | 0.18 | 51 |

`k ≥ 3` is **NOT REACHED** at PS-A on every arm. This is a property of the
authorized budget, not a null result.

---

## 8. Not run, not evaluated, not evaluable

| item | status | reason |
|---|---|---|
| Stages B1–B4, C | **NOT RUN** | not authorized (`DEC-20260806-5289fb`) |
| Stage D (PS-D2, PS-D4 dilution) | **NOT RUN** | optional stage, not authorized |
| `log2 A_k` / `log2 A_m` on any (T) arm | **NOT COMPUTED** | not authorized; §0 |
| `CTRL-WBP` (within-block permutation) | **NOT RUN** | stage C |
| `CTRL-DEC` at 1e5 trials/set | **NOT RUN** | stage C; a 7200-block cross-check was run instead (§9) |
| `CTRL-ORACLE` | **NOT RUN** | optional and non-blocking by contract |
| second deterministic tie convention | **NOT RUN** | §7.1 — protocol deviation |
| `INV-Q` upper end at PS-R1/R3/R5 | **NOT EVALUABLE** | Prop. 6.1.4's `p_i` formula is outside this task's read scope; §3 |
| `TC-2` | **NOT EVALUABLE** | depends on §7.1 |
| `D4` at the 1e−6 tail | **NOT REACHED** | needs ≥ 1e6 trials; 527 928 achieved |
| `INV-NULL` at PS-A, `k ≥ 3` | **NOT REACHED** | §7.5 |
| `INV-SHARD` (3-shard consistency) | **NOT EVALUATED** | a stage-B rule on `log2 Ahat_k`, which Stage A does not compute |
| `INV-REPRO` fixture file | **NOT EVALUATED AS A FILE** | `experiments/EXP-HQC-982268/fixtures/published_values.json` does not exist in the tree and is outside this task's write scope. The fixture *values* that Stage A can touch were used and checked: `p* ` (§4), `log2 p_i(6.1.4)` at PS-A (§3), and SPEC Table 10's error-vector column (§4.1). |
| `sympy`, `SageMath`, `scipy` | **ABSENT** | confirmed absent at run time and recorded in the manifest; nothing here depended on them. Third-party dependency used: `numpy` 2.4.6 only. |

---

## 9. Supplementary instrument checks (not contract gates)

**Smoke self-tests, all pass** (run before the budget was spent): the size-128
fast Walsh–Hadamard transform matches an independently constructed dense
Hadamard matrix exactly; the sparse shift-XOR ring product matches the dense
big-integer path; Floyd sampling gives exact weight and distinct indices in
50/50 cases; the counter-mode PRNG is replayable and domain-separated; the
binomial-moment estimator returns `q^k` on an exact binomial law to relative
1.9e−8.

**Extended decoder cross-check** (post-processing pass; i.i.d. Bernoulli
blocks only — no ring element and no fixed-weight vector constructed). The
folded-WHT argmax was compared against exhaustive minimum-distance search over
all 256 duplicated RM(1,7) codewords, 600 blocks per cell, at
`p ∈ {0.30, 0.34, 0.38, 0.42, 0.46, 0.50}` and `dup ∈ {1, 3}`:
**7200/7200 blocks agree.** The sweep exists because the smoke-phase check ran
at `p ≈ p*`, where `dup = 3` produced **zero** failures and therefore did not
exercise the failure branch; at `p ≥ 0.38` the `dup = 3` failure branch is
exercised (21, 210, 509, 598 failures at `p` = 0.38, 0.42, 0.46, 0.50) and
still agrees exactly. This is CTRL-DEC in spirit at Stage-A scale; it is not
CTRL-DEC discharged.

---

## 10. Reproduction

```sh
cd coordination/goals/GOAL-HQC-001/batches/BATCH-6fddee/tasks/TASK-20260806-64b506
PYTHONDONTWRITEBYTECODE=1 python3 stage_a.py \
    --out-dir . --scratch <scratch> --core-seconds 1692 --cores 4 --wall-cap 1400
PYTHONDONTWRITEBYTECODE=1 python3 stage_a.py --out-dir . --scratch <scratch> --postprocess
```

Master seed 20260804; per-shard key = first 128 bits of
`SHA-256("EXP-HQC-982268/v1" | set_id | arm | shard | 20260804)`; per-trial
domain `b"v<i>" || trial_index_le64`, five disjoint counter subspaces per
trial. The (T) arms consult **no** other source of randomness, so every trial
is a deterministic function of `(key, trial index)` and is replayable in
isolation — which is what `D5` used.

**Two figures in this run are throughput-dependent and will differ on other
hardware**: the trial counts per set are sized from a measured calibration, so
a faster or slower host produces different `T`, and hence different SEs and a
different `k`-reachability boundary. Every gate verdict above is stated with
its `T`.

---

*Executor's record. No status changed, no evidence record written, no ledger
or experiment file touched. Files written: exactly the four declared
artifacts in this task directory.*
