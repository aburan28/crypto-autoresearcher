# RT-20260805-a98111 — what I re-derived

Independent red-team session, `TASK-20260805-a98111`, BATCH-4bc9bc (batch 6 of 6),
GOAL-MLKEM-004. Reviewing snapshot `0d34dfcb`, which archives `TASK-20260805-74a8e9`.

**Scope banner, binding on every sentence.** TOY SCALE. m=35, n=25, d=60, q=127,
secret centred-binomial eta=2, error rounded Gaussian sigma=2, ONE LWE instance
(seed 20260803206), ONE sieve database. No ML-KEM break claim, no security proof,
no security claim in either direction, no FIPS 203 parameter set affected or
cleared, no speedup, no cost claim, no exponent moved. AGENTS.md rule 12 is UNMET
and UNWAIVED, inherited: this report changes the status of no `EV-MLKEM-*` record
and proposes none. I did not run `git commit` and wrote nothing outside my
`write_scope`. Objections and observations only.

**Quotation discipline.** Every quoted string below is copied from a path in the
declared artifact set and the path is cited inline. No ratio is restated without
its denominator in the same sentence. A subagent response message is not an
archived source (`DEC-20260804-485fa6` CE-1) and none is used here.

**Independence hygiene.** The session scratchpad is shared and contains prior and
concurrent sessions' scratch files (`rt_dep.py`, `rt_dep2.py`, `rt_out.json`,
`val_t1.py`, `val_t1.log`, `val_t2sens.py`). These are not archived sources —
`RT-20260804-0ff29a` says so of its own, and the producer records the same at
`.../TASK-20260805-74a8e9/report.md` DEV-9 — so I neither read nor reused any of
them. `val_t1.py`, `val_t1.log` and `val_t2sens.py` belong to the concurrent
validator task `TASK-20260805-983040`; reading them would have destroyed my
independence and I did not. Everything below is implemented from the recipes in
the committed artifacts.

---

## 1. What I ran

Two runs, against a declared `maximum_runs: 2`. Both on stock numpy 2.4.6,
Python 3.11.15, against the archived integers. No g6k, no fpylll, no venv, no
scoring.

- **RUN 1** `nested.py` (~14 min): independent recomputation of the T1 real arm;
  reproduction of two of the producer's sixteen ABL draws from its recorded
  seeds; three NESTED null controls at n=8 each that the package does not run;
  structural diagnostics on the sieve pool and on Y.
- **RUN 2** `second.py` (~1 min): the second archived certified dual family
  `SIEVE_SUMS` through the identical closed form, candidate columns and
  statistic; and the pooled-rank calibration of the real value against every
  decoupled draw now available.

Both scripts live in the session scratchpad and are **not** durable evidence; I
do not offer them as such. Every number below is reproducible from the recipe
stated here plus the committed `dependence.py` and `vectors.json`.

**Limit on my own work, stated first.** My controls import the *same*
`closed_form_cov` from
`coordination/goals/GOAL-MLKEM-004/batches/BATCH-a2bb63/tasks/TASK-20260804-f58d34/dependence.py`
that the producer imports. A defect in that closed form would move my arms and
the producer's together. I did write my own ST-6 statistic rather than calling
the producer's `st6_ratio_from_cov`. For the closed form itself I rely on
`RT-20260804-0ff29a`, which derived it from scratch and reproduced it, and on
KAC-1 in this run (`results_t1.json` `/known_answer_controls`, relative max error
0.00243 against a 4e5-draw Monte Carlo).

---

## 2. What reproduced

**The T1 real arm, exactly.** My independent ST-6 implementation, fed the archived
`closed_form_cov` on the archived candidate columns, returns
0.8646 / 0.7283 / 0.9692 / 0.9194 / 0.4149 for
near_miss_8 / near_miss_25 / uniform_8 / uniform_25 / secret_distribution_25.
Identical to four decimals to `results_t1.json` `/T1/real` and to the producer's
table.

**Two of the sixteen ABL draws, from the producer's own seeds.** Seeds
20260805740000 and 20260805740007 give
0.8845 / 0.7653 / 0.9782 / 0.9092 / 0.4629 and
0.9226 / 0.8079 / 0.9691 / 0.9142 / 0.5038, identical to four decimals to
`results_t1.json` `/T1/ablated_per_draw[0]` and `[7]`. The ensemble is
reproducible from the record.

**The intervals, means, sds and z-scores.** Recomputing from
`results_t1.json` `/T1/ablated_draws`:

| group | ABL min | ABL max | mean | sd | real | z |
|---|---|---|---|---|---|---|
| near_miss_8 | 0.883502 | 0.934610 | 0.913967 | 0.018447 | 0.864574 | −2.6776 |
| near_miss_25 | 0.748464 | 0.807912 | 0.771172 | 0.016176 | 0.728326 | −2.6487 |
| uniform_8 | 0.969058 | 0.988680 | 0.980598 | 0.005988 | 0.969192 | −1.9048 |
| uniform_25 | 0.904381 | 0.931992 | 0.920327 | 0.007809 | 0.919429 | −0.1151 |
| secret_distribution_25 | 0.430920 | 0.507352 | 0.473771 | 0.024286 | 0.414935 | −2.4226 |

Every branch label follows. `uniform_8`'s INSIDE margin is
0.969192 − 0.969058 = 0.000134, i.e. DEV-8 is real.

**All six T2 cells.** Recomputing z from `results_t2.json`
`/T2/per_p/*/cells/*/m_z_perm` (8 realisations, ddof=1) reproduces every
published z to 1e-6: −3.18, −0.01, +6.72, +2.27, −3.01, −5.21, and hence every
branch.

**The extraction.** `report.md` is byte-identical to `results.json`
`/report_markdown` encoded UTF-8: 28,547 bytes, sha256
`7432f56da05e98e3ae9ffbbbe46e4a24ef1dd704db1be064af989163acfff97c`, and that
hash is declared in `receipt.json`. The Coordinator's DEV-3 claim in commit
`0d34dfcb` verifies.

**Every cross-citation the producer makes to a declared path.** Line-for-line:
`ledger/evidence/EV-MLKEM-d777f0.yaml` line 133 reads
`At n = 2 the residual is UNRESOLVED, and that is the check batch 6 runs.`;
`.../TASK-20260804-0ff29a/report.yaml` line 786 reads
`8 draws x 20 s = under 3 minutes, no lattice compute.`;
`.../TASK-20260804-264ab9/report.yaml` line 469 reads
`A residual of 4-9% survives every structural control I ran, consistently`.
All three are verbatim at the cited lines.

**T3.** `git diff 0d34dfcb^ 0d34dfcb -- knowledge/techniques/KN-TECH-6c0e15.md
knowledge/techniques/KN-TECH-9d21c4.md` is empty. `KN-TECH-1a5b7e.md` is a
660-line creation. `confidence: single_run_experiment` is retained.

**No security claim anywhere.** I searched `report.md`, `KN-TECH-1a5b7e.md`,
`results*.json` and the commit message for break / insecure / vulnerable /
bits-of-security / FIPS 203 / Kyber / speedup / affected shapes. The only hits
are explicit *disclaimers* and one reference to a broken `fpylll` constant. The
closest thing to an operational sentence, `report.md` line 315, is
`**An operational sign now exists as a measurement, and it is not consistent.**`,
and line 330 forecloses the reading: `so \`OP-HARDER\` here must not be read as
"the dependence makes the attack harder"`. This is not an overclaim.

---

## 3. The attack that FAILED — and I report it because it failed

I attacked the ablation on the axis the card names: does ABL differ from the
real arm in some **second** way, so that OUTSIDE_LOW is a confound rather than a
coupling effect?

`resolve.py` lines 686–692 build ABL as isotropic Gaussian row directions
rescaled to the sieve's exact row norms, with `Y_ab = rint(N(0, 2.272274))` iid.
That destroys **three** things at once relative to the real family, and I
predicted the deficit would be explained by one of the two uninteresting ones:

1. the sieve pool's Gram geometry (a sieve database is pairwise-reduced, so its
   inner-product tails should be lighter than isotropic, and `closed_form_cov`
   applies `exp(2c<x_i,x_j>)`, a convex function, to exactly those entries);
2. the column dependence and shape of the real Y;
3. the row-wise x–y coupling — the thing the campaign is about.

I built the three nested nulls that separate them, n=8 each:

- **ROWPERM** — X real, phases real, phase rows permuted. Preserves X's Gram
  *exactly* and Y's column dependence *exactly*; destroys only the pairing.
- **XABL** — X ablated, Y real.
- **YABL** — X real, Y ablated.

Group means, against the producer's 16-draw ABL mean and sd:

| group | ABL mean (n=16) | ROWPERM (n=8) | XABL (n=8) | YABL (n=8) | real |
|---|---|---|---|---|---|
| near_miss_8 | 0.9140 | 0.9167 | 0.9078 | 0.9225 | 0.8646 |
| near_miss_25 | 0.7712 | 0.7793 | 0.7602 | 0.7733 | 0.7283 |
| uniform_8 | 0.9806 | 0.9776 | 0.9810 | 0.9786 | 0.9692 |
| uniform_25 | 0.9203 | 0.9230 | 0.9232 | 0.9204 | 0.9194 |
| secret_distribution_25 | 0.4738 | 0.4594 | 0.4578 | 0.4697 | 0.4149 |

Every one of the fifteen control means sits within 0.68 ABL ensemble sd of the
ABL mean. Across the three constructions, **7 of 120 control-draw/group cells**
(denominator: 3 constructions × 8 draws × 5 groups = 120) fall below the
producer's ABL ensemble minimum — 5.83%, against the 1/17 = 5.88% rate expected
if my controls were exchangeable with the ABL draws.

**So the producer's ablation is calibrated, and my structural attack fails.**
Preserving the real X, or the real Y, or both, while destroying only the row
pairing, does not recover the real value.

The structural diagnostics say the same thing directly, and refute my
conjecture 1 by measurement:

- pairwise cosine off-diagonals on a common 3000-row subsample: real sd 0.16924,
  kurtosis 2.8460, fraction with |cos| > 0.5 = 2.008e-3 (denominator: the
  4,498,500 distinct pairs among the 3000 sampled rows); ABL sd 0.16890,
  kurtosis 2.8406, fraction 1.890e-3. **Indistinguishable.** The sieve pool is
  not detectably pairwise-reduced relative to the isotropic model at this
  database, and my "lighter Gram tails" mechanism does not exist here;
- 0 of 17,919 rows of X have their negation also in the database;
- `X^T X / N` eigenvalue max/min: real 1.2865, ABL 1.1673 (both with mean
  eigenvalue 5.1856). A small anisotropy ABL does not preserve, but XABL shows
  it does not carry the deficit;
- Y column correlations: |off-diagonal| mean 0.00870 against the
  1/sqrt(17919) = 0.00747 noise floor, max +0.03259. Nearly uncorrelated,
  consistent with YABL ≈ ABL.

Because `closed_form_cov` depends on X **only** through `X X^T` and the row
norms, and on Y only through the phase matrix, ROWPERM is a complete
decomposition: the whole of the deficit lives in the **alignment** between the
sieve pool's Gram matrix and the candidate phase matrix. That is a stronger and
cleaner statement than the package makes, and it is in the producer's favour.
I record it as such.

---

## 4. The attacks that LANDED

### 4.1 The rejected null was known false before the measurement

ABL asserts three things jointly: X directions isotropic, Y iid rounded
Gaussian, X independent of Y. For the certified dual family **all three are
false by construction, before any measurement**. The package's own certificate
proves the third: `results_t1.json` `/certificate` records
`checked_entries: 447975`, `violating_entries: 0` for the membership identity —
that identity *is* the statement that y is a deterministic function of x. So
`OUTSIDE_LOW` licenses "the real family is not the ablated object", which nobody
disputed.

The interesting claim — that the *dual* structure or the *sieve* is what
produces the deficit, rather than any deterministic x–y coupling — is untested,
and this campaign has already been burned on exactly that distinction. The goal
record's own `batch_log` for BATCH-d3a45a records
`a family NOT in the lattice, with y a deterministic function of x, separates at
12.1507` (`ledger/goals/GOAL-MLKEM-004.yaml`). The analogue here was not built.

### 4.2 Widening the decoupled reference class deflates the headline

The min/max branch is a function of 16 draws. Pooling every decoupled draw now
available — the producer's 16 ABL plus my 8 ROWPERM, 8 XABL and 8 YABL, n=40 —
and ranking the real value in it:

| group | pool mean | pool sd | pool min | real | rank in pool | exact p |
|---|---|---|---|---|---|---|
| near_miss_8 | 0.9150 | 0.0215 | 0.8477 | 0.8646 | 1 of 40 below it | 0.0488 |
| near_miss_25 | 0.7710 | 0.0188 | 0.7150 | 0.7283 | 1 of 40 below it | 0.0488 |
| uniform_8 | 0.9797 | 0.0054 | 0.9674 | 0.9692 | 2 of 40 below it | 0.0732 |
| uniform_25 | 0.9214 | 0.0071 | 0.9044 | 0.9194 | 13 of 40 below it | 0.3415 |
| secret_distribution_25 | 0.4669 | 0.0210 | 0.4289 | 0.4149 | 0 of 40 below it | 0.0244 |

Exact p is (number of pooled decoupled draws at or below the real value + 1)
divided by 41 (denominator: 40 pooled decoupled draws plus the real value).

Two consequences. First, **on two of the three OUTSIDE_LOW groups the real value
is not extremal**: ROWPERM draw 05 gives near_miss_8 = 0.8477 against real
0.8646, and XABL draw 00 gives near_miss_25 = 0.7150 against real 0.7283. The
`OUTSIDE_LOW` label on those groups is an artefact of which 16 decoupled draws
happened to define the interval. Second, the best exact per-group p in the whole
T1 measurement is **0.0244, on one group, with five positively-correlated groups
examined**. That is a lead. It is not "z ≈ −2.5 therefore something is there",
and it is a long way from a result.

Note also that ROWPERM — the most *faithful* decoupled null, since it keeps the
real X and the real Y — has sd 0.0333 over 8 draws on near_miss_8 against ABL's
0.0184 over 16. The producer's comparator may be narrower than the decoupled
class it stands for on that group.

### 4.3 The second certified dual family goes the other way

`vectors.json` archives three families. `SIEVE_SUMS` is a second certified dual
family for the **same instance**, same A, same secret, and I ran it through the
identical closed form, candidate columns and statistic:

| group | SIEVE | SIEVE_SUMS | producer ABL interval | SIEVE_SUMS branch |
|---|---|---|---|---|
| near_miss_8 | 0.8646 | 0.9645 | [0.8835, 0.9346] | OUTSIDE_HIGH |
| near_miss_25 | 0.7283 | 0.8746 | [0.7485, 0.8079] | OUTSIDE_HIGH |
| uniform_8 | 0.9692 | 0.9977 | [0.9691, 0.9887] | OUTSIDE_HIGH |
| uniform_25 | 0.9194 | 0.9872 | [0.9044, 0.9320] | OUTSIDE_HIGH |
| secret_distribution_25 | 0.4149 | 0.4891 | [0.4309, 0.5074] | INSIDE |

**Caveat I state before drawing anything from it:** SIEVE_SUMS has different
marginals — X row-norm² mean 363.3934 against SIEVE's 181.4943, Y entrywise sd
3.214222 against 2.272274 — and the ABL ensemble was built to match SIEVE. The
`OUTSIDE_HIGH` labels are therefore **not** like-for-like verdicts and I do not
offer them as such.

What is marginal-independent, and what matters: **the two certified dual families
of the same instance differ from each other by 0.0285 to 0.1463 in ST-6 ratio**
(0.0999, 0.1463, 0.0285, 0.0678, 0.0742 across the five groups), against a
SIEVE-vs-ABL-mean deficit of 0.0009 to 0.0589 (0.0494, 0.0429, 0.0114, 0.0009,
0.0589). The between-real-object spread is of the same order as, and on four of
five groups larger than, the quantity being read as a finding — and the package
has **one** real object. This is LIM-1, now with a number.

The cheapest control that would settle it is 8 ABL draws matched to SIEVE_SUMS's
row norms and Y sd — under three minutes, no lattice compute. **I did not run
it**, because it would have been a third measurement run against a declared
`maximum_runs: 2`. It is named as the successor's first check and it costs
nothing to reproduce from this recipe.

### 4.4 The "derived-before-the-run false-positive value" is forced

Commit `0d34dfcb` records `the derived-before-the-run false-positive value of
exactly 1 LOW / 14 INSIDE / 1 HIGH per group was met on all five groups`. The
producer says plainly why this is not calibration evidence, at `report.md` line
109: the value holds `whenever the draws are pairwise distinct, by the definition
of a min/max interval`. The check verifies distinctness and that the code
implements the frozen rule. It carries **zero** information about whether the
instrument discriminates. Placed in a paragraph headed "Discipline", beside the
genuine null-first timing evidence, it reads as more than it is. This is the
sixth quantity in this campaign that is forced by construction, and the first
that is forced in the *verification* rather than in the measurement.

Separately, the derivation is of the wrong quantity by a small margin in the
conservative direction: leave-one-out against the other 15 draws gives exactly
1/16 = 6.25%, but the rate relevant to the real arm — an independent 17th draw
against the minimum of 16 — is 1/17 = 5.88%.

### 4.5 SENS-T1 is off-scale and one-sided

`results_t1.json` `/T1_sensitivity` records ensemble min 0.9043808564728013,
RANK5 0.5091, `gap` 0.3952453396487522 against `threshold` 0.05. The effects
being read are 0.0009 to 0.0589 in the same units. A control that fires at 0.3952
establishes the statistic is alive; it does not establish that the instrument
resolves at one tenth of that. There is no negative control at effect scale — no
perturbation known to be irrelevant that must come back INSIDE. Given that I
measured a real-vs-ABL second-moment anisotropy (`X^T X/N` max/min 1.2865 vs
1.1673) that ABL does not preserve, a graded rank ladder (34, 33, 30, 25) would
say directly whether a ~0.05 drop is producible by second-moment structure alone.

### 4.6 T2's z is a t on 7 degrees of freedom, and two labels are unstable

The frozen rule fires on |z| > 3 where the denominator is an sd from 8 CAL-PERM
realisations. The correct reference is Student's t with 7 df: two-sided
P(|t_7| > 3) = 0.0199, which is 7.4x the Gaussian 0.0027. Separately, the exact
rank-based permutation p floor with 8 realisations is 1/9 = 0.111 (denominator:
8 comparator realisations plus the real statistic), so **no exact permutation p
below 0.111 is attainable in this design**, while the report cites |z| up to
5.21. Two of the three adjacent-family labels sit at z = −3.18 (p=2) and
z = −3.01 (p=5); the relative standard error of an sd estimated from 8 draws is
about 26.7%, so both labels flip to OP-NULL under a plausible re-estimation of
the comparator spread. The characterisation `sign-inconsistent across p`
(`report.md` line 319) is therefore itself label-unstable: if both OP-HARDERs
flipped, the adjacent family would read OP-NULL / OP-EASIER / OP-NULL.

---

## 5. DEV-5 — confirmed, and understated

`results_t2.json` `/T2_sensitivity/rows` gives, at t = 0, 0.10, 0.25, 0.50, 0.75:
branches OP-NULL, OP-HARDER, OP-HARDER, OP-HARDER, OP-EASIER; mean correlations
−0.0005489, +0.3059179, +0.4939149, +0.6956075, +0.8673897; and m_z
−0.894743, −1.098871, −1.148235, −1.129606, −0.849830. The correlation rises
monotonically and the label does not. **DEV-5 holds exactly as stated.**

It is understated in three ways the package does not say:

1. **The dominant response to increasing genuine dependence is OP-HARDER.**
   Three of the five grid points return it, at z = −34.83, −49.92, −36.01. The
   declared OP-EASIER gate at t = 0.75 returns z = +6.40. OP-EASIER appears at
   exactly one grid point, and it is the point the gate was placed at.
2. **The grid never reaches the regime the real measurement occupies.** The
   smallest nonzero grid point has mean correlation +0.3059; every real T2 cell
   has |mean correlation| ≤ 0.03305 (`results_t2.json`
   `/T2/expectations_scored/E2_abs_mean_corr_below_0p15/max_abs`). That is a
   factor of about 9. Since correlation ≈ sqrt(t) in this construction, the real
   cells sit near t ≈ 0.001, a hundredfold below the grid's finest nonzero point.
   The labels are read off an **uncharacterised** part of a **proven
   non-monotone** response curve.
3. Therefore the correct statement is stronger than "cannot sign one": at the
   dependence levels actually measured, nobody has shown the instrument responds
   to dependence *at all* in a way distinguishable from the two competing
   mechanisms the producer names (shrinking margin noise vs rising maximum over
   ten competitors).

Extending the grid to t in {0.001, 0.005, 0.01, 0.02} is synthetic-only and costs
seconds. Until it is run, `OP-HARDER` and `OP-EASIER` are labels, not directions.

**Consequence for the campaign, confirmed.** After six batches there is **no
operational direction, in either sense.** In the T2 sense the sign cannot be read
from the rule (DEV-5, and §5.2 above). In the T1 sense the direction is reported
as downward but the producer declines to attribute it (`report.md` line 217:
`**I do not conclude that the residual is object-specific, real, or a property of
the dual family.**`), no Nf was recomputed (`report.md` line 15: `No Nf
recomputed or corrected. No heuristic declared validated or refuted.`), and the
second certified dual family of the same instance sits on the other side of the
same interval on four of five groups (§4.3). Confirmed, not refuted.

---

## 6. Coordinator conduct in commit `0d34dfcb`

The rule the Coordinator set itself was quote-only-from-declared-paths-and-cite.
It largely kept it, and the one prior defect class — fabricated attribution — does
**not** recur. Every string the message places inside quotation marks,
`"dependence makes the attack harder"`, appears in `report.md` (line 330,
as `the dependence makes the attack harder`). Every figure in the message traces
to `results.json`, `results_t1.json` or `results_t2.json`; I checked each one.

Two defects, both minor, both recorded because this program tracks them:

- **CE-A.** `SENS-T1 cleared its pre-declared 0.05 threshold by 0.3952`.
  `results_t1.json` `/T1_sensitivity` has `gap` = 0.3952453396487522 and
  `threshold` = 0.05. The gap is 0.3952; the margin over the threshold is
  0.3452. The producer's own wording is correct (`report.md` line 125: `gap
  **0.3952** against a threshold of 0.0500`) and the message garbled it.
- **CE-B.** `DEV-5, which the producer calls the most important thing T2
  produced`. The producer's string is `most important caveat in T2`
  (`report.md` line 259). A caveat is not a thing produced. This is a
  Coordinator paraphrase carried by an attribution verb. It is materially
  faithful and it is emphatically **not** the `DEC-20260804-485fa6` CE-1 class,
  where strings were quoted as verbatim that appeared in no producer artifact.

One further framing point, not a quotation defect. The message says
`The two INSIDE groups are the uniform ones RT-20260804-0ff29a OBJ-3 had already
shown are pinned across objects`, which invites reading the two INSIDE groups as
controls that showed nothing. Only one of them did: uniform_25 sits at z = −0.12,
but uniform_8 sits at z = −1.90 and is INSIDE by 0.000134. All five groups have
z ≤ 0 and four of five have z ≤ −1.90. The message does report DEV-8, so the fact
is disclosed; the framing around it is not.

---

## 7. Six batches, at their real weight

Neither inflated nor dismissed.

**What is real and durable.**

- A working instrument, rebuilt from `KN-TECH-14efa5` in an ephemeral container
  six times running, with the drift recorded each time.
- A certified dual-vector database that a stranger can check without g6k: 17,919
  vectors, 0 violating of 447,975 entries, re-verified in this batch by code
  written in `resolve.py` that does not call the archived `certify()`
  (`results_t1.json` `/certificate`), and independently by reviewers in earlier
  batches. That artifact outlives the campaign.
- **Five observables refuted by construction rather than by a p-value.** In every
  case the refutation was an *object* exhibited without the structure the
  observable was supposed to detect, which reproduced the number. That is the
  strongest form of negative result available and this program produced five of
  them in six batches. It is unusual and it should be said out loud.
- Three superseding technique entries (`KN-TECH-9d21c4` → `KN-TECH-6c0e15` →
  `KN-TECH-1a5b7e`) codifying a forced-quantity taxonomy, now at five modes with
  a `forced_value_regime` field and a monotonicity refinement. This is the
  campaign's transferable output; it is method, not measurement, and it is not
  specific to LWE.
- One quantity that survived comparator replication to n=16, survived three
  nested nulls I built to kill it, and is entirely localised to the alignment
  between the sieve pool's Gram matrix and the candidate phase matrix.

**What is not there.**

- No statement about `MATZOV.Nf`. The final package disclaims one explicitly.
- No statement about the independence heuristic at any dimension.
- No operational direction, in either sense.
- No evidence at cryptographic scale, and none claimed.
- The surviving quantity is one instance, one database, one statistic, best exact
  per-group p 0.0244 of five correlated groups, and it points the other way on
  the second archived family.

**The honest summary sentence.** Six batches converted a plausible measurement
programme into a well-characterised method for killing plausible measurements,
plus one lead that is smaller than the between-object variation nobody has
measured. Under `docs/inventor-protocol.md` §2 and the Möbius precedent, that is
a real deliverable and it is not the deliverable the goal was chartered to
produce.

---

## 8. The terminal disposition

### The criteria, read from `ledger/goals/GOAL-MLKEM-004.yaml`

- **C1** — a measured score distribution of sieve-produced dual vectors at a
  stated set of reduced dimensions, with algorithm / dimension / modulus /
  distributions / count / seed recorded and reproducible from the archived
  script. **MET.** Cited: `EV-MLKEM-da9e3b` (BATCH-d2a728), re-verified in this
  snapshot at `results_t1.json` `/certificate` (17,919 vectors, 447,975 entries
  checked, 0 violating, 60 exact-bigint rows, 0 duplicate rows) and
  `/instance_regenerates_from_seed` (A and s identical from seed 20260803206).
  **Scope note the Coordinator must carry:** the "set of reduced dimensions" has
  exactly one element. RC-5, the dimension sweep, has gone unrun for three
  batches and the producer names it first among what remains open
  (`report.md` line 447). If "a stated set" is read as requiring more than one
  dimension, C1 is not met either.
- **C2** — an explicit comparison of that distribution against the independence
  structure underlying `MATZOV.Nf`'s closed-form advantage computation,
  reporting the direction and size of any departure or reporting agreement,
  with a null of the right shape run before any departure is believed.
  **NOT MET.** The final package disclaims it in its own scope banner
  (`report.md` line 15: `No Nf recomputed or corrected. No heuristic declared
  validated or refuted.`) and its T1 measurement involves no scoring at all
  (`results_t1.json` `/T1/what_is_measured`: `ST-6 ratio K_eff_trail/(K-1) from
  the ARCHIVED closed_form_cov, no scoring, on identical candidate columns`).
  The one batch that did report a departure against that structure,
  `EV-MLKEM-d777f0`, carries `direction: mixed` and the headline
  `The across-candidate departure is MOSTLY FORCED` with the reported factor of
  2 becoming 1.10 under both reviews. No direction stands.
- **C3** — independent Validator and Red Team sessions admit the run package.
  **MET for BATCH-d2a728** (`VAL-20260803-535d15` ADMISSIBLE_WITH_DEFECTS and
  `RT-20260803-4064e1` pass_with_constraints, per the goal record's `batch_log`).
  **NOT met for BATCH-f75059, BATCH-c45baf, BATCH-d3a45a or BATCH-a2bb63**, each
  of which drew `blocking_objections`. For BATCH-4bc9bc I return
  `pass_with_constraints`; C3 is met for this package if `TASK-20260805-983040`
  concurs.
- **C4** — Coordinator evidence, decision and warranted knowledge entries
  committed through verified ledger archives, scoped to what was measured.
  **MET.** Five batches carry `decision_id`, `evidence_id`, `snapshot_commit`
  and two reviews in the goal record's `batch_log`.

### The ruling

**`GOAL-MLKEM-004` should be retired at `closed_at_budget`, not `completed`.**

C1, C3 and C4 are met and I say so plainly, because understating a met criterion
is a contract violation in its own right. But all three are **procedural**: they
say the parameters were recorded, the archives were verified, and one of six
packages was admitted. **C2 is the only criterion that asserts a scientific
result, and it is not met.** Closing `completed` on C1/C3/C4 would be closing on
process and asserting a success the campaign did not achieve. The goal's own
`next_action` sets the bar at `completed` only if `a declared completion
criterion is actually met and cited` — singular; I flag that reading explicitly,
because it is precisely the seam where a criterion gets manufactured, and I rule
that a procedural criterion cannot carry a `completed` on a measurement goal.

**This is a budget exhaustion, not a closure of the lane.** Under
`docs/inventor-protocol.md` §4 a closure needs a named obstruction, an argument
and forward guidance. **There is no named obstruction here.** The campaign did
not hit one; it ran out of batches with a live, unresolved, cheap-to-test lead.
The decision record must say so in those terms, and must not read as "the
question is dead". A count of six batches and five refuted observables is a
fatigue report about the search, not a statement about the problem.

### The campaign should have a successor, and it is not this campaign renamed

Every one of the six batches varied the **object** at fixed (m, n, N, K, one
instance, one database), and every refutation came from exhibiting another
object. The successor must vary what six batches never varied:

1. **RC-5 — the dimension sweep at fixed (N, K).** m is the only named parameter
   supposed to destroy this class of quantity and it has never been moved. The
   prediction is already falsifiable and written down at `report.md` lines
   450–452: `the uniform-group floor should track \`1 - O(K/m)\`, so raising m at
   fixed (N, K) must raise it toward 1.` This is `docs/inventor-protocol.md` §3
   applied properly: ask what the quantity should do as the parameter meant to
   destroy it increases. If the floor tracks 1 − O(K/m), the whole ST-6 family is
   finite-m Gram geometry and **this program gets its first real closure with a
   named obstruction** — a better outcome than a seventh refuted observable.
2. **The complementary ensemble — R independent real sieve databases at fixed
   candidates.** This is LIM-1 and it has been open since batch 5. My §4.3
   measurement makes it urgent rather than tidy: the two archived certified dual
   families of the same instance differ by 0.0285 to 0.1463 in ST-6 ratio while
   the deficit being read is 0.0009 to 0.0589. Until the real arm has n > 1, the
   T1 comparison is one-sided by construction.
3. **A family with an arbitrary deterministic x–y coupling unrelated to A**, with
   marginals matched. §4.1. Batch 4's analogue of this control killed batch 4's
   observable; the analogue here has not been built.

These are different measurements on different axes with a pre-committed,
falsifiable stopping rule. That is what makes the successor a successor rather
than a rename. All three are cheap: (1) and (3) need no g6k at all, (2) needs one
sieve per replicate.

---

## 9. What I could not check

- **The scoring path.** T1 is closed-form only. I did not run a Monte-Carlo
  scoring cross-check of ST-6, and neither did this batch.
- **The T2 Stage B reconstruction below the archived cross-check.** I verified
  that `results_t2.json` records `abs_delta: 0.0` against the archive on all six
  known-answer cells and I reproduced every published z from the recorded
  `m_z_perm` arrays, but I did not rebuild the Stage B score matrices from
  scratch.
- **The rebuild transcript.** I did not re-run the passagemath / fpylll / g6k
  install. DEV-1, DEV-2 and DEV-7 are the producer's own disclosures and I take
  them as recorded, not as verified by me.
- **A marginal-matched ABL for SIEVE_SUMS**, which is the control that would turn
  §4.3 from a spread statement into a sign statement. Not run: it would be a
  third measurement run against a declared `maximum_runs: 2`. Named, costed and
  handed forward instead.
- **Anything at cryptographic scale.** Nothing here is crypto-scale evidence, and
  no extrapolation to FIPS 203 dimensions is made or implied.
