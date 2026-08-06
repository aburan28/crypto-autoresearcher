# Red-team report — Stage A of `EXP-HQC-982268`

**Task** `TASK-20260806-dd901b` (red-team) · **Batch** `BATCH-6fddee` ·
**Goal** `GOAL-HQC-001` · **Question** `RQ-HQC-001`
**Target** `TASK-20260806-64b506` (executor) · **Contract**
`experiments/EXP-HQC-982268/specification.yaml` · **Oracle**
`…/BATCH-003/tasks/TASK-20260803-6f50df/`
**Produced** 2026-08-06 · **Repo commit** `ff816e03` (branch
`claude/harness-goals-experiments-g5pt2o`)

I write objections. I change no status, edit no raw artifact, and write only
inside
`coordination/goals/GOAL-HQC-001/batches/BATCH-6fddee/reviews/TASK-20260806-dd901b/`.
I did not read the sibling review at `…/reviews/TASK-20260806-43a44f/`; it is
outside my read scope and reading it would compromise independence.

**Claim tier is TOY and I do not move it.** Nothing below is a statement about
HQC, about A17 or A5, about any decoding-failure rate, or about any
standardized HQC parameter set. Every number here is about an *instrument*.

---

## 0. Disclosure — compute I ran, and why it is not a run of `EXP-HQC-982268`

My dispatch entry carries `budget.runs_authorized: 0` and
`handoff.budget.maximum_runs: 1`. These conflict. I resolved the conflict
conservatively: **I constructed no HQC object.** I ran four probes, all in
scratch, none of which touches a ring, a fixed-weight sampler, a truncation, a
Reed–Muller decoder, or any HQC parameter beyond the integers `(n_e, q, T, k)`:

| probe | what it is | cost |
|---|---|---|
| P1 `ctrl_oracle_check.py` | pushes the oracle's **exact** enumerated `law_of_S` through `stage_a.py`'s own `log2_A_from_hist`. Zero sampling, zero randomness. | 3 s |
| P2 `ctrl_bs_blindness.py` | synthetic i.i.d. Bernoulli indicator matrices; genuine null vs `stage_a.py`'s CTRL-BS re-index | 6 s |
| P3 `nullm_surrogate.py` | `S ~ Binomial(n_e, q)` draws at each null arm's own achieved `T`; reads the sampling distribution of `stage_a.py`'s estimator | 42 s |
| P4 jackknife calibration | same, plus `stage_a.py`'s own `jackknife_log2_A`, measuring the realized false-positive rate of the `INV-NULL` rule | ~7 min |

These are **binomial arithmetic on synthetic data**. They produce no run
record, no evidence record, and no measurement of `mubar_k` on space (T) or
(M). They exist to answer the one question this review was dispatched to ask —
*can the controls fail* — and that question cannot be answered by reading. If
the Coordinator judges even this to exceed `runs_authorized: 0`, the finding
below stands on the package's **own committed `stage_a_results.json`** in
`OBJ-1`, which required no compute at all.

---

## 1. Verdict

**The package is unusually honest and technically strong in its parts, and its
headline is wrong.** The Executor found and reported three real contract
defects against itself (`D3`'s advertised discriminating power, `CTRL-BS`'s
"exactly 1" expectation, the tie-rule deviation), which is the behaviour this
program wants. But:

- **`OBJ-1` (blocking).** Stage A's single chartered deliverable — *"fix
  `k_max` by the pre-registered rule"* (contract `stage_A_calibration.purpose`)
  — was **computed and not reported**. The number is sitting in the package's
  own `stage_a_results.json` under `k_max_sizing`, and it says that at the
  **measured** `q̂`, `k = m` is **out of reach at the contracted trial
  allocation at two of the three order-matched sets**. `ST-4`, the
  pre-registered underpower contingency written for exactly this event, is
  never mentioned in the report or the manifest.
- **`OBJ-2` (blocking for interpretation).** The `INV-NULL` decision rule
  `|log2 Â_k| > 3·SE_jack` is **not a 0.27 % rule**. Measured under the exact
  null at the achieved `T`: **7.7 %** at PS-R1 `k = 16`, **8.7 %** at PS-R3
  `k = 22`, **12.7 %** at PS-R5 `k = 30 = m`, **21.0 %** at PS-R3 `k = 25`.
  The "28 firings prove the arms can fail" argument therefore proves something
  else, and the one T_stab-admissible firing the report escalates dissolves
  when the |z| is computed against the estimator's actual sampling
  distribution.
- **`OBJ-3`.** The contract's modelled null SE at the load-bearing cell
  (PS-R1, `k = 16`, `T = 1e8`) is **0.0321 bits**. Measured on the exact null
  law: **0.0744 bits**, a factor **2.3** — so the contract's advertised
  resolution "±0.096 bits at PS-R1 (k=16)" is really about **±0.22 bits**.
- **`OBJ-4`.** The **ORACLE AGREEMENT** gate is a determinism-plus-self-test
  check of a *different program*. It contains **zero bits** about the Stage A
  instrument. The check that would have contained those bits (`CTRL-ORACLE`)
  was declared "NOT RUN — optional and non-blocking"; **it costs three
  seconds. I ran it. It passes** (§5).
- **`OBJ-5`.** One of the three null arms — the one the contract designates
  **PRIMARY** — is structurally incapable of failing for anything upstream of
  the indicator matrix, and I verify a hard structural reason the report does
  not state.

`valid_partial_measurement` is the right validity class. The
gate table that accompanies it is not.

---

## 2. `OBJ-1` — Stage A's chartered deliverable was computed and withheld: at the measured `q̂`, `k = m` does not fit the contracted allocation at PS-R1 or PS-R5

**Severity: blocking. Requires no new compute. Source: the package's own file.**

The contract charters Stage A to *"measure `q̂`, `p̂`, `γ̂`, `Corr(W_i,W_j)`,
`Var(W_1)`, tie rate at all four sets; check `INV-Q`; **fix `k_max` by the
pre-registered rule**"*. The pre-registered rule is
`T_req = max(T_prec, T_stab)`, and the contract states plainly that
**`T_stab` IS THE BINDING CRITERION AT EVERY CELL EXAMINED**.

`stage_a.py` computed `T_stab` at the **measured** `q̂` for every `(set, k)`
and wrote it to `stage_a_results.json` → `k_max_sizing`. Comparing those
values against the contract's own per-stage `trials` allocation — one line of
arithmetic that the package does not perform — gives:

| set | allocated `T` (contract) | `m` | `T_stab(m)` at measured `q̂` | verdict | `k_max` at allocation |
|---|---|---|---|---|---|
| PS-A | 1e8 (`stage_B1`) | 16 | 1.25e45 | out of reach by ~37 orders (already declared) | **3** |
| **PS-R1** | **1e8** (`stage_B2`) | **16** | **1.452e8** | **NOT REACHABLE — 1.45× the allocation** | **15** |
| PS-R3 | 2e7 (`stage_B3`) | 17 | 1.000e6 | reachable, 20× margin | 20 |
| **PS-R5** | **2e7** (`stage_B4`) | **30** | **2.554e7** | **NOT REACHABLE — 1.28× the allocation** | **29** |

The contract's own frozen `sample_size_derivation` claimed
`T_req(PS-R1, k=16) = 2.91e7` "against `T = 1e8`, margin 3.4x". That figure was
computed at the **modelled** `q_for_sizing = 0.2306`. The measured
`q̂ = 0.197427` is 14 % lower, and `T_stab` is violently non-linear in `q`: the
margin does not shrink from 3.4× to 2.9×, it **inverts to 0.69×**. The same
happens at PS-R5 (contract `T_req(30) = 2.72e6`; measured-`q̂`
`T_stab(30) = 2.554e7`, a 9.4× increase, against a 2e7 allocation). At PS-A the
`k = 3` requirement also rises 3.3× (1.61e7 → 5.34e7) and survives only because
PS-A's allocation is 1e8.

Three consequences the Coordinator needs before ranking any Stage B work:

1. **`ST-4` is triggered at PS-R1.** Its text: *"if the Stage-A `q̂` at PS-R1
   places `k = m = 16` outside the reachable range at the allocated `T`, the
   run PROCEEDS with the reachable `k_max` and REPORTS `k = 16` as NOT
   REACHED. It does NOT raise `p*`."* Stage A's numbers trigger this clause.
   The report never names `ST-4`.
2. **Contract `success_criterion` (iv) becomes unsatisfiable as written.** It
   requires `log2 Â_m` reported with a jackknife 3σ interval at **PS-R1,
   PS-R3 and PS-R5**. Two of three cannot deliver it at their allocations.
3. **The Coordinator's declared successor is right, and for a reason Stage A
   discovered without saying so.** `DEC-20260806-5289fb` ranks **B3 (PS-R3)**
   next, at 2940 core-seconds. PS-R3 is precisely the one order-matched set
   that retains margin at `k = m` under the measured `q̂`. That is now a
   *measured* justification rather than a cost-ordering coincidence, and it
   should be recorded as such.

The report's §8 "Not run, not evaluated, not evaluable" table lists twelve
items. `k_max` determination — the thing Stage A exists to produce — is not
one of them, because it was produced. It is the comparison against the
allocation that is missing, and it is the comparison that carries the result.

The `k_max_sizing` block is labelled *"forward-looking sizing numbers for a
stage that is NOT authorized, not measurements of anything."* That label is
half right and it is how the finding got buried: the `T_stab` values are
forward-looking, but the `q̂` they are computed from **is** a Stage A
measurement, and the contract asked for exactly this derived quantity.

**Cheapest falsification of `OBJ-1`:** recompute
`T_stab(k=16 | n_e=46, q=0.197427)` from the contract's own formula
`s_90 = min{s : Σ_{s'≤s} P[S=s']·C(s',k) ≥ 0.90·E[C(S,k)]}`,
`T_stab = 30/P[S ≥ s_90]`. If it lands below 1e8, I am wrong. It is one call
to `stage_a.t_stab_required` and it is already in the committed JSON as
`1.452e8` with `s_90 = 25`.

---

## 3. `OBJ-2` — the `INV-NULL` decision rule cannot discriminate at the orders that matter, and the "one admissible firing" is an artifact of that

**Severity: blocking for interpretation. Established by probes P3/P4.**

`INV-NULL` fires when `|log2 Â_k| > 3·SE_jack`, with `SE_jack` the delete-one
jackknife over 200 contiguous trial batches. The report treats `3·SE` as a
significance threshold and reasons from firing counts ("324 cells, 28 fired…
of 151 `T_stab`-admissible cells, exactly 1 fired").

Nobody measured what that rule actually does under the null. I did. Drawing
`S ~ Binomial(n_e, q̂)` — which is *exactly* the law all three null arms
instantiate, and literally `NULL-P`'s construction — at each arm's own achieved
`T`, and applying `stage_a.py`'s own `jackknife_log2_A`:

| set / arm | `k` | `P[|log2 Â_k| > 3·SE_jack]` under the exact null | nominal |
|---|---|---|---|
| PS-R1 NULL-M | 2 | 0.3 % (1/300) | 0.27 % |
| PS-R1 NULL-M | 6 | 0.0 % (0/300) | 0.27 % |
| PS-R1 NULL-M | 9 | 0.7 % (2/300) | 0.27 % |
| PS-R1 NULL-M | **11** | **1.3 % (4/300)** | 0.27 % |
| PS-R1 NULL-M | 14 | 5.3 % (16/300) | 0.27 % |
| **PS-R1 NULL-M** | **16 = m** | **7.7 % (23/300)** | 0.27 % |
| PS-R3 NULL-M | 17 = m | 1.7 % (5/300) | 0.27 % |
| PS-R3 NULL-M | 22 | 8.7 % (26/300) | 0.27 % |
| PS-R3 NULL-M | 25 | 21.0 % (63/300) | 0.27 % |
| **PS-R5 NULL-M** | **30 = m** | **12.7 % (38/300)** | 0.27 % |

The mechanism is not exotic and is not "undersampling of a right-skewed
`C(S,k)`" alone. The jackknife SE is well calibrated *in expectation* (mean
`SE_jack` vs true sampling SD: 0.0049/0.0047 at `k=6`, 0.0502/0.0548 at
`k=11`, 0.419/0.512 at `k=16` — within 3–20 %). What breaks the rule is that
at high `k` **the point estimate and its own jackknife SE are driven by the
same handful of large-`S` trials and are therefore strongly positively
coupled**, so the Wald ratio `|point|/SE` has fat tails even though both
factors are individually fine. That is a decision-rule pathology, and it is
mode 4 of `KN-TECH-1a5b7e` — *"the fourth way a decision rule passes without
being able to discriminate."*

### 3.1 The escalated firing dissolves

The report's §6.1 escalates PS-R1 / NULL-M / `k = 11`
(`log2 Â_11 = −0.111265`, `SE_jack = 0.035350`, `|z| = 3.15`) and hands the
Reviewer a hypothesis: *"whether … evidence that the contract's `T_stab`
threshold of 30 … is too loose near its boundary."*

That hypothesis is not needed and is probably wrong. Under the exact null at
that arm's own `(n_e = 46, q = 0.197845, T = 497 632)`:

- true sampling SD of `log2 Â_11` = **0.0534**; mean `SE_jack` = **0.0502**;
- **the run's own realized `SE_jack` = 0.0354**, i.e. this particular sample
  drew an SE ~30 % below typical — the coupling above, exactly;
- surrogate mean = `−0.00178`, so the correctly-scaled statistic is
  `(−0.11126 + 0.00178)/0.0534 = **−2.05**`, **not 3.15**;
- at 2.05 the cell does not fire, and 1.3 % of null draws fire at this cell
  anyway.

`T_stab = 30` is not implicated. The threshold is not "too loose near its
boundary"; the |z| is mis-scaled. **This matters because the two diagnoses
have opposite consequences**: "T_stab too loose" says raise the sizing
constant and spend more compute; "the Wald statistic is mis-calibrated" says
the sizing is fine and the *decision rule* needs a null-calibrated critical
value. The report offers only the first.

### 3.2 "The nulls did fail somewhere, which is informative in itself"

Report §6.2 argues that 28 firings *"demonstrates that these arms are capable
of failing with the estimator and SEs as implemented."* Given the table above,
what 28 firings across 324 cells demonstrates is mostly that the rule fires on
pure noise at 5–20 % in the high-`k` cells where most firings sit. A control
that rejects a true null one time in eight is not sensitive; it is
uninformative in the other direction. This sentence should not survive into an
evidence record as a sensitivity argument.

### 3.3 The forward consequence, which is the serious one

The contract's **`falsification_criterion`** is
`|log2 Â_m| ≥ 3 × jackknife SE` at `k = m`. That is the same statistic, at the
same orders, at PS-R1 (`m=16`), PS-R3 (`m=17`) and PS-R5 (`m=30`). At Stage
A's `T` its false-positive rate at `k = m` is 7.7 % / 1.7 % / 12.7 %. At
larger `T` the skew abates — at `T = 1e8`, `k = 16`, I measured 0/20 firings —
but *nobody has established that*, and Stage A was the stage chartered to
establish it. **A frozen falsification criterion whose realized size is
unmeasured is not a falsification criterion.**

**Cheapest fix, and cheapest falsification of this objection:** for each
`(set, k = m)` at the *Stage-B* `T`, draw ~2 000 `Binomial(n_e, q̂)` samples,
apply `stage_a.jackknife_log2_A`, and read the empirical two-sided 99.7 %
critical value off the resulting distribution. Cost: minutes; no HQC object;
no ring; no decoder. If the empirical critical value comes out at `3·SE_jack`,
`OBJ-2` is refuted at that cell.

---

## 4. `OBJ-3` — the contract's modelled null variance understates the truth by 2.3× at the load-bearing cell

The contract's `sample_size_derivation` gives
`SE(log2 Â_16) = 0.0321` bits at PS-R1's allocated `T = 1e8`, and
`interpretation_of_a_null_result` converts that into the advertised width
*"±0.096 bits at PS-R1 (k=16)"* — the number any downstream reader will quote
as the experiment's resolution.

Measured (probe P4, `n_e = 46`, `q = 0.197427`, `T = 1e8`, R = 20 independent
samples, exact null):

| quantity | value |
|---|---|
| true SD of `log2 Â_16` | **0.0744 bits** |
| mean `SE_jack` from `stage_a.py` | 0.0576 bits |
| contract `SE_at_allocated_T` | **0.0321 bits** |
| mean point estimate (truth = 0) | −0.0068 bits |

So `V(n_e, q, k)` as frozen in the contract understates the estimator's null
variance at this cell by `(0.0744/0.0321)² ≈ 5.4×`, the advertised ±0.096-bit
resolution is really **≈ ±0.22 bits**, and — since `T_prec ∝ V` — the
precision leg of `T_req` is understated by the same factor, compounding
`OBJ-1` rather than offsetting it.

Two riders, stated because they bound the claim: R = 20 gives the SD estimate
roughly ±16 % relative, and I measured PS-R1 `k = 16` only. I do **not** claim
the other advertised widths (±0.024 at PS-R3, ±0.078 at PS-R5, ±0.028 / ±0.32
at PS-A) are wrong; they are computed by the same formula and are now
untrusted until measured, which costs minutes.

Separately and minor: the point estimator's null mean is not 0 — I measure
−0.099 bits at `T = 2.91e6`, −0.025 at `T = 2.91e7`, −0.0068 at `T = 1e8`, a
one-signed bias decaying roughly as `1/T`. At `T = 1e8` that is 9 % of one true
SD, so it is not material there; it *is* material at Stage A's `T ≈ 5e5`, where
it is a large part of the "monotone negative drift" the report attributes to
undersampling. The fix is free: report the measured null-mean offset beside
every `log2 Â_k`, since the frozen prediction is a two-sided test against
exactly 0.

---

## 5. `OBJ-4` — the ORACLE AGREEMENT gate is a tautology as a check of *this* instrument; the real check costs three seconds and I ran it

The report's most confident sentence is its gate-table entry:

> **ORACLE AGREEMENT | EVALUATED, AGREES.** All three committed sha256 match
> `oracle_report.md`'s table. Re-run vs committed `oracle_values.json`: **0
> computed-value differences** … `test_oracle.py`: **43 tests, all pass**.

Every element of that is true. I verified the three sha256 independently
(`96c54ed5…`, `b3c52cc0…`, `a3d65582…` — they match the files and the report
table). And every element of it is a statement about `oracle.py`, not about
`stage_a.py`. `phase_oracle()` does exactly three things: hash three sibling
files; re-run `oracle.py` and deep-diff its output against the JSON
`oracle.py` itself produced; run `oracle.py`'s own committed test suite. **No
value produced by `stage_a.py` is compared against any value produced by the
oracle anywhere in the gate.** The gate can fail only if `oracle.py` is
non-deterministic or a sibling file was mutated. It is a chain-of-custody and
reproducibility check — worth having, honestly executed — carrying the name of
a cross-validation it does not perform.

Meanwhile §8 records:

> `CTRL-ORACLE` | **NOT RUN** | optional and non-blocking by contract

`CTRL-ORACLE` is the only item in the entire contract that would test the
Stage A estimator against ground truth that is *known* rather than *sampled*,
and it is the reason the sibling task built the oracle at all
(`oracle_report.md` §0: *"a Monte-Carlo estimator of `μ_m` can be pointed at
one of these configurations and its output compared against a number that is
known, not sampled"*). Skipping it left every check of the estimator in Stage
A confined to laws where the correct answer is `log2 A_k = 0` — that is,
**the instrument was calibrated only at the null point of a two-sided test
whose entire purpose is detecting departures from that point.**

So I ran it (probe P1). It is deterministic and requires no sampling: the
oracle publishes each configuration's **exact rational `law_of_S`**, which is
precisely the input `stage_a.log2_A_from_hist` consumes.

**Result: 40 cells across all 13 oracle configurations, max discrepancy
1.2 × 10⁻¹⁴ bits.** Including strongly off-null ground truth:

| configuration | `k` | exact `log2 A_k` | `stage_a.py` | diff |
|---|---|---|---|---|
| `B2-comonotone-extreme-positive` | 4 | +9.965784 | +9.965784 | 0.0e+00 |
| `A5-positive-latent-mixture` | 5 | +3.216740 | +3.216740 | −8.9e−16 |
| `A3-negative-global-fixed-weight-threshold` | 3 | −2.851453 | −2.851453 | +5.3e−15 |
| `B1-exactly-c-extreme-negative` | 3 | −1.562242 | −1.562242 | −8.9e−16 |
| `R1-ring-truncated-prime-n17` | 4 | −0.098977 | −0.098977 | −3.6e−15 |
| `R4-ring-3blocks-n19-n2-6` | 3 | −0.012468 | −0.012468 | +1.2e−14 |

**This is a genuine pass and it should be recorded as one.** The Stage A
estimator's `S`-histogram → `log2 A_k` arithmetic is correct off the null, at
both signs, over four orders of magnitude of effect size. The objection is not
that the instrument is broken; it is that **the package asserted an "oracle
agreement" it had not obtained, while declining a three-second check that
would have obtained it.** Under `AGENTS.md` rule 6 and
`docs/inventor-protocol.md` §6 step 4, "optional and non-blocking" is a
statement about contractual dependency, not a licence to leave the only
ground-truth comparison unrun and then name a different check after it.

**What P1 does *not* establish, stated so no one over-reads it:** it exercises
the estimator arithmetic only. It says nothing about the fixed-weight sampler,
the ring product, the truncation, the folded-WHT decoder, or the jackknife —
and `OBJ-2`/`OBJ-3` show the jackknife leg is where the real trouble is. The
end-to-end `CTRL-ORACLE` (run the *whole* Stage A pipeline on an oracle
configuration and compare to the exact number) remains unrun and is not
three seconds' work, because `stage_a.decode_blocks` is hard-wired to a
size-128 WHT while the oracle's toy block models are `threshold(n2=4,t=1)` and
RM(1,2). That gap is worth a line in a successor contract.

---

## 6. `OBJ-5` — explicit verdict: can each null arm actually fail?

Required deliverable. Verdicts, with the structural reason:

### `NULL-P` — **CAN FAIL. Narrowest scope. Demonstrated.**
Draws `S ~ Binomial(n_e, q̂)` and pushes it through the same estimator. It
touches no ring, sampler, truncation or decoder — the report states this
correctly in §7.4. It *did* fire (PS-R5, `k = 49…58`), so it is not inert. It
detects arithmetic and jackknife defects in `mubar_from_hist` /
`log2_A_from_hist` and nothing else. Note the shared-code hazard: `NULL-P` and
the (T) arm are scored by the *same functions*, so a defect that is a smooth
monotone distortion of the histogram appears identically on both and cancels
in the contrast. `P1` (§5) is the check that closes this gap, and it now
passes.

### `NULL-M` — **CAN FAIL. Strongest of the three. Fired.**
The only arm exercising the decoder. `A_k = 1` is a theorem on it, it produced
the run's only `T_stab`-admissible firing, and its deviations at high `k` are
large. Genuine sensitivity. Two limits: it does not touch the fixed-weight
sampler, the ring product or the truncation (report §7.4, correct); and per
`OBJ-2` most of its firings are decision-rule artifacts rather than arm
failures.

### `CTRL-BS` — **CANNOT FAIL for anything upstream of the indicator matrix, and it is the least sensitive arm at the load-bearing orders. The contract designating it PRIMARY is backwards.**

The report's §7.4 already concedes *"it cannot detect any decoder or sampler
defect at all — a wrong `F_j` enters the null and the thing it controls
identically."* That concession is correct and it is more damaging than the
report treats it, because the contract calls this arm
**"NULL OBJECT — PRIMARY"** on the strength of it matching *"the EXACT true
marginal block-failure law — not a modelled marginal."* Three additions:

1. **A hard structural fact the report does not state.** `stage_a.py` builds
   the pseudo-sample as `Fb[:,j] = np.roll(F[:,j], -off[j])`. A cyclic roll is
   a **permutation of a column**, so every per-block column sum is preserved
   *exactly*. Therefore `q̂^{BS} ≡ q̂^{T}` **identically**, not approximately.
   I verified `Σ_t S_t` on the committed histograms at all four sets: PS-A
   8 122 / 8 122; PS-R1 5 200 049 / 5 200 049; PS-R3 9 159 668 / 9 159 668;
   PS-R5 13 187 613 / 13 187 613. The control's denominator carries **zero
   independent information** — it is the (T) arm's own `q̂`.
2. **It fired at 0 of 108 cells**, and its `|z|` never exceeded **1.67**
   anywhere in the run, including at cells where its own point estimate was
   −2.13 bits. Compare `NULL-M`, which reached `|z| = 8.39`.
3. **Its per-run spread is larger, not smaller** (probe P2: at `k = 16`,
   `T = 572 588`, genuine i.i.d. null mean −0.079 / sd 0.297 over 6 samples;
   CTRL-BS re-index mean −0.037 / sd 0.719 over 18). With only 6 independent
   underlying matrices this is indicative rather than established, but it
   points the same way as (2): CTRL-BS is the noisiest arm and therefore the
   one least able to reject. **`INV-NULL` clause (d)** — "the CTRL-BS excess
   exceeds 25 % of the (T) excess" — is a ratio of two noisy quantities with a
   fixed 25 % threshold and no stated uncertainty, evaluated on an arm whose
   own realization spread at `k = m` is comparable to the excesses being
   compared. That clause needs an error bar before Stage B, or it will pass by
   construction.

**Recommendation (not a status change):** the Coordinator should consider
re-designating `NULL-M` as the primary null and `CTRL-BS` as a
pipeline/estimator control, via a versioned `protocol_amendment` creating a new
record. Do not silently re-rank them.

---

## 7. Claim leakage — scan and quotes

I looked for anything licensing a statement about HQC, A17, A5, decoding
failure rates or standardized parameter sets. **The report's own scoping (§0,
§8) is genuinely good**, and `stage_a.py`'s module docstring restates the
ceiling. Three items nonetheless need fencing before promotion:

**L1 — the `TC-2` bracket must not be promoted to "our decoder reproduces
HQC's published inner DFR."** Report §4.2 and the Executor's summary:

> the lowest-index `q̂ = 2^−11.546` is 0.586 bits from Table 11's `2^−10.96`,
> but `2^−10.96` lies inside the bracket `[2^−11.546, 2^−10.592]`

The bracket is **0.954 bits wide**. That the published value lies inside it is
close to uninformative — it is an interval that would contain almost any
plausible value. The honest statement, which the report *does* make and which
must be the one that survives: `TC-2` is **NOT EVALUABLE** pending the second
tie convention. Anything stronger is unsupported. Related and worth
foregrounding: at PS-A the **tie rate is 93.7 % of `q̂`**, so at HQC-1's own
parameters this instrument's measured block-failure rate is dominated by the
tie convention. That is a first-order instrument property, correctly logged as
`DEV-1`.

**L2 — the `p̂` agreement is a much weaker check than its billing.** Summary:

> `p̂` reproduces the tabulated analytic `p*` to 5.2e−7–1.5e−5 at all four
> sets (`p*` is never a (T) input)

The parenthetical does rhetorical work it cannot support. `p*` is a
deterministic function of `(n, ω, ω_r, ω_e, N)` via Prop. 6.1.2, which the
sampler realizes *by construction*; at `T ≈ 5×10⁵` agreement to 10⁻⁶ is close
to arithmetically forced. It is a real check of the ring product and
truncation — a necessary condition — and it says nothing whatsoever about the
**joint** law across blocks, which is the entire estimand. The genuinely
strong (T)-object check in this package is the **Table 10 upper-tail
comparison** (0.0 / −2.0 / +1.4 weight units at the 1e−3/1e−4/1e−5 tails),
because it compares against a published *measurement* of the same object; that
is the one to cite.

**L3 — "STAGE A COMPLETE" is not supportable as stated.** The Executor's
opening line to the Coordinator. Against `OBJ-1` (the chartered `k_max`
deliverable's implication unreported, `ST-4` untriggered), `OBJ-2` (the gate's
own decision rule uncalibrated) and `OBJ-4` (`CTRL-ORACLE` unrun), the
supportable statement is: *"Stage A executed inside budget and produced its
diagnostics; three gates require adjudication before Stage B is ranked."*

**No leakage found in the other direction.** I found no sentence asserting
anything about A17, A5, a DFR, or a standardized parameter set. `log2_A_k` and
`log2_A_m` are genuinely absent from every (T) arm — I checked `stage_a.py`'s
(T) worker `_t_shard` and the diagnostics block, and the joint-moment estimator
is invoked only on `null_p_bh`, `null_m_bh` and `ctrl_bs_reps`. The
authorization boundary was respected.

---

## 8. Uncharged cost and hidden assumptions in how the gates were evaluated

**U1 — the cell-admission floor is not the contract's rule, and it is
presented as if adjacent to it.** `stage_a.evaluable_k` admits `k` when at
least **30 trials have `S ≥ k`**, with the docstring *"(The contract's own
`T_stab` reasoning…)"*, and reuses the constant `T_STAB_THRESHOLD = 30`. These
are different quantities: the contract's rule is `T ≥ 30/P[S ≥ s_90]` where
`s_90` is the 90 %-of-estimand-mass quantile, and at PS-R1 `k = 16` that is
`s_90 = 25`, not `k`. The report does cross-reference the real `T_stab`
afterwards (`INV_NULL_vs_T_stab`) — good — but the **denominator "151
admissible cells" is a post-hoc selection**, computed after the firings were
known, from an admission rule that is not the pre-registered one. Under
`INV-NULL`'s own `preregistration_note` ("the magnitude threshold and the
significance threshold are both fixed here and may not be adjusted after data
exist"), the *reporting partition* deserves the same discipline.

**U2 — "151 cells" invites a multiple-comparisons reading the data do not
support.** The 151 cells are functions of **12 histograms** (4 sets × 3 arms);
within an arm the `k`-ladder is almost perfectly dependent. "1 firing in 151"
suggests ~0.4 expected by chance; the effective number of independent tests is
closer to 12. The report's own §6.1 correctly notes the firing is "where a
smooth one-signed drift crosses the threshold, not a jump" — which is exactly
the statement that the 151 cells are not 151 tests. The two framings are in
tension and the summary keeps the reassuring one.

**U3 — the trial counts `T` are throughput-adaptive.** Report §10: *"the trial
counts per set are sized from a measured calibration, so a faster or slower
host produces different `T`."* The report flags this. The uncharged part: the
`k`-reachability boundary, every SE, and therefore **which cells were eligible
to fire**, are all functions of host speed. `ST-7` forbids adaptive stopping on
the primary metric and Stage A computes no primary metric, so no rule is
broken — but the `INV-NULL` gate outcome is not reproducible on different
hardware, and the gate table does not say so.

**U4 — the stated mechanism for the 27 non-admissible firings does not fit all
the data.** Report §6.1: *"the direction of every firing on every arm is
negative, which is the direction a right-skewed `C(S,k)` produces when the
large-`S` region … is undersampled."* The directional claim is true as stated
(I checked PS-R5 `NULL-P`'s ten firing cells: all negative). But the *drift* on
`NULL-P` is **positive** at PS-R1 (`+0.284` at `k = 20`) and PS-R3 (`+1.681` at
`k = 31`), reaching values larger in magnitude than several firing cells and
escaping only because the SE is huge. A single "undersampling ⇒ negative"
mechanism does not produce a positive drift on one arm and a negative drift on
another at the same set. The mechanism is offered as explanation and is at
best partial; per `docs/inventor-protocol.md` §3 it is an unverified structural
story, not a control.

**U5 — throughput.** Measured 1502–2555 trials/core-second vs the modelled
4728, i.e. **1.9×–3.1× slower, at or past the declared 2× contingency**. The
Executor reports this plainly (credit). The uncharged consequence: the
contract's `optimistic_assumptions` says *"If the true factor is 5× the total
becomes 1.4e5 core-seconds and `ST-1` truncates `T` rather than overrunning."*
At the measured 3.1× at PS-R5, `stage_B4`'s 4 940 modelled core-seconds become
~15 300. Combined with `OBJ-1`, PS-R5's `k = m = 30` needs **more** trials than
allocated at **~3× the cost per trial**. That compounding is not stated
anywhere and it is exactly the budget arithmetic the Coordinator needs.

---

## 9. Cheapest falsification for each claim the package makes

Per the handoff's fourth question. Each row is an observation that would refute
the claim, ordered by cost.

| claim the package makes | cheapest observation that refutes it | cost |
|---|---|---|
| "ORACLE AGREEMENT — AGREES" (as a check of *this* instrument) | Read `phase_oracle()`: no `stage_a` output enters the comparison. Already refuted. | 0 |
| `k = m` reachable at PS-R1/PS-R5 at contracted `T` | `T_stab(16 \| q̂=0.197427) = 1.452e8 > 1e8`; `T_stab(30 \| q̂=0.414120) = 2.554e7 > 2e7`. In the package's own JSON. Already refuted. | 0 |
| `INV-NULL` at `3·SE_jack` is a 0.27 % rule | 300 `Binomial(n_e,q̂)` draws + `jackknife_log2_A`; count firings. Measured 7.7 %/8.7 %/12.7 %/21.0 %. Already refuted. | ~7 min |
| Contract resolution "±0.096 bits at PS-R1 k=16" | 20 null draws at `T=1e8`; SD of the point estimate. Measured 0.0744 bits (3 SD ≈ 0.22). Already refuted. | ~4 min |
| The `k=11` firing indicates `T_stab=30` is too loose | Same 300 draws: realized `SE_jack` 0.0354 vs typical 0.0502; corrected `\|z\| = 2.05 < 3`. Already refuted. | included above |
| `CTRL-BS` "matches the exact true marginal law" as an independent null | `Σ_t S_t` identical on (T) and CTRL-BS at all four sets (verified). Not independent. Already refuted as *independent*. | 0 |
| **`stage_a.py`'s estimator is correct off the null** | Push the oracle's exact `law_of_S` through `log2_A_from_hist` for a configuration with `\|log2 A_k\| ≫ 0`. **I ran it: 40 cells, max diff 1.2e−14. NOT refuted — this one passes.** | 3 s |
| `D2` (exact weights) holds | One trial with a repeated index in the Floyd sample. Checked on 9 827 880 vectors, 0 deviations. Not refuted. | 0 |
| `p̂ = p*` to 1e−6 implies the (T) *joint* law is right | Construct any sampler with correct marginals and wrong block coupling — `p̂` is unchanged. Refutes the *implication*, not the measurement. | algebra |
| The remaining advertised widths (±0.024 PS-R3, ±0.078 PS-R5, ±0.028/±0.32 PS-A) | Same 20-draw null measurement at each cell. **Not yet run — I make no claim about these.** | ~10 min |

---

## 10. What the package got right, and should be credited for

Recording this because a red-team report that lists only faults mis-ranks the
work.

- **Three contract defects found and reported against itself**, none of them
  forced: `D3` is not the (T)-vs-(M) discriminator the contract claims (the
  cap sits 39–70 σ *inside* the (M) mean — a clean, correct, load-bearing
  refutation of the contract's own rationale); `CTRL-BS`'s `E[Â_k] = 1
  EXACTLY` is false by Maclaurin, with the floor computed and shown harmless
  at this `T`; and §7.4's statement that **no null arm tests the (T) joint
  law** is the single most valuable sentence in the report.
- **`DEV-1` (the unrun second tie convention) is disclosed as material with
  its size**, and `TC-2` is declared NOT EVALUABLE rather than passed. The
  rigorous bracket argument (`q_high = q_low + P[tie ∧ 0 ∈ argmax ∧ WHT₀>0]`)
  is correct.
- **The authorization boundary held.** No `log2_A_k`/`log2_A_m` on any (T)
  arm; no ledger, experiment or sibling-task file touched; the sibling
  instrument's three files verify byte-identical after the run; `PYTHONDONTWRITEBYTECODE=1`
  set so no `__pycache__` was left in a read-only sibling directory.
- **Budget honesty**: the 1.9–3.1× throughput shortfall is reported against
  the modelled figure rather than smoothed, and the 1e−6 tail and PS-A `k ≥ 3`
  are `NOT REACHED` (budget outcomes) rather than nulls — `AGENTS.md` rule 5
  correctly applied.
- **The smoke suite and the extended decoder cross-check are real controls**:
  the 7 200/7 200 exhaustive-minimum-distance agreement was deliberately
  extended to `p ≥ 0.38` *because* the failure branch was unexercised at
  `p ≈ p*` — that is a control being made able to fail, on the executor's own
  initiative, which is the exact discipline `KN-TECH-1a5b7e` asks for.

---

## 11. What I did not evaluate

Stated so coverage is not overstated.

- The **end-to-end** `CTRL-ORACLE` (whole Stage A pipeline vs an exact oracle
  configuration). Not run by anyone; not three seconds' work (decoder shape
  mismatch, §5).
- The (T) sampler, ring product and truncation. I ran none of them; I rely on
  the package's `D2`/`D5`/Table-10 evidence, which looks sound.
- `INV-Q`'s upper end at the reduced sets — outside my read scope too, for the
  same reason (Prop. 6.1.4's `p_i` lives in `BATCH-001`). The Executor's refusal
  to reconstruct it from memory is correct and should not be second-guessed.
- The advertised widths at PS-R3, PS-R5 and PS-A (§9, last row).
- The sibling validation report `…/reviews/TASK-20260806-43a44f/`, deliberately
  unread.
- Whether any of this bears on HQC. **It does not, and Stage A cannot make it
  do so.**

---

*Red-team record. No status changed, no hypothesis transitioned, no ledger or
experiment file touched, no raw artifact edited. Files written: this report
only. Probe scripts live in session scratch and are reproducible from the code
listed in §0; they construct no HQC object.*
