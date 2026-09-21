# TASK-20260729-020 — independent re-implementation and recount

**Validator, BATCH-012, GOAL-ECDLP-001.** Fresh non-originating session. No shared
conversation lineage with `TASK-20260729-014`, `-016` or `-018`. **Model
independence is not available and is not claimed** (`INT-BATCH012-D`).

Everything below was computed in this session. Every number is either produced by
code written in this session from the contract text, or read from a Git blob at a
named commit. Nothing is copied from the package's own narrative.

Scratch root for all execution was **outside the repository**
(`/private/tmp/.../scratchpad/`). The repository working tree was clean before and
after (`git status --porcelain` empty at both points), and no commit was made.

---

## 0. What governs

`experiments/EXP-YIELD-002/specification.yaml` at `f291a624`, as amended by
`amendments/v1_to_v2.yaml` at `e3c9cb45` and `amendments/v2_to_v3.yaml` at
`0548d8cc`. **v3 governs, then v2, then v1.**

Verified by this session: each of the three files was **added in exactly one
commit and never modified since** — `git log -- experiments/EXP-YIELD-002/specification.yaml experiments/EXP-YIELD-002/amendments/` returns exactly those
three commits and nothing else. All three are ancestors of the snapshot.

The specification's `status: review_required` / `approved_by: null` is the `D-1`
prophylaxis. Approval lives in
`.../archives/TASK-20260729-030/snapshot_commit_receipt.json`
(`APPROVAL_DETERMINATION.determination: APPROVED`, commit `5174001c`), and this
session verified that **`5174001c` is an ancestor of `f49670fa`**, which is the
parent of the run snapshot — i.e. approval is strictly earlier in the commit graph
than execution. The null was not read as evidence of non-approval.

---

## 1. Snapshot receipt verification (done against Git, not against the receipt's prose)

| check | result |
|---|---|
| `c7189f80` exists and is reachable from `HEAD` (`256f417a`) | **yes** (`git merge-base --is-ancestor`) |
| first parent | `f49670fa165e63cb8970ab137a4311c3d8223fd0` — **matches the receipt** |
| changed-path set | **exactly 11**, all `A` (additions), set-equal to `committed_paths` |
| SHA-256 of every committed blob at that commit | **11 of 11 match `path_sha256`** |
| extras, deletions, `__pycache__`, AppleDouble sidecars in the commit | **none** |
| twelfth declared path (the receipt itself) deferred under `INT-BATCH007-T` | strict subset, **not a scope overrun** |

The two hash-bound inputs were verified by this session directly from the Git
blobs at `2fb2bb7a`:

- `IN-1` `experiments/EXP-YIELD-001/runs/RUN-YIELD-001-NULL-RANDOM-SUMSET/results.json`
  → `040207f85a3444a3377cdf5c86175fb70de6e47280f91c09a516f7a65d2125cd` = pinned value.
- `IN-2` `experiments/EXP-YIELD-001/results/summary.json`
  → `2287b277b6f6ce842230ca13bf1217a8ba34cc6da1d2d362123502810f7b2aeb` = pinned value.

The driver blob at `c7189f80` hashes to
`6202852687076585346ab100868f94e672757b24b3c6f871913308fa805e9bf6`, which equals
`environment.driver_sha256` recorded in all three manifests.

**Not verified by this session:** that the person or agent who wrote the driver did
not read `experiments/EXP-YIELD-001/driver/yield_census.py`. That is an
attestation about an authoring process, not a checkable property of an artifact.
What *is* checkable — and was checked — is that the committed driver neither
imports nor opens it.

---

## 2. Re-execution of the committed driver into a scratch root outside the repository

The driver derives `REPO_ROOT` from its own location
(`dirname(__file__)/../../..`). A scratch tree was built outside the repository
containing only the driver blob from `c7189f80` and the two input blobs from
`2fb2bb7a`, and the driver was run there. It wrote exactly ten files and nothing
else — no `__pycache__`, no `.partial` residue, no extra artifact.

```
python3 experiments/EXP-YIELD-002/driver/repaired_null.py --run RUN-YIELD-002-KNOWNANSWER
python3 experiments/EXP-YIELD-002/driver/repaired_null.py --run RUN-YIELD-002-NULL-ASRECORDED
python3 experiments/EXP-YIELD-002/driver/repaired_null.py --run RUN-YIELD-002-NULL-REPAIRED
python3 experiments/EXP-YIELD-002/driver/repaired_null.py --summary
```

**Environment of the re-execution.** `numpy` **`2.4.0`** — the exact string pinned
by `C-19b` and recorded in all three manifests before the first draw. Python
`3.13.1`, `macOS-26.6-arm64`. Wall clock 13.031 + 0.091 + 1.406 s = **14.53 s**
against the package's 13.368 + 0.093 + 1.497 = 14.96 s.

**Result: bit-identical on every scientific field.** A recursive structural diff of
the four re-generated JSON documents against the committed blobs, comparing floats
for exact equality, returns:

| file | total differing leaves | what they are |
|---|---|---|
| `RUN-YIELD-002-KNOWNANSWER/results.json` | 3 | `elapsed_seconds`, two `timestamps` |
| `RUN-YIELD-002-NULL-ASRECORDED/results.json` | 51 | 48 per-row `elapsed_seconds`, run `elapsed_seconds`, two `timestamps` |
| `RUN-YIELD-002-NULL-REPAIRED/results.json` | 55 | 52 per-row `elapsed_seconds`, run `elapsed_seconds`, two `timestamps` |
| `results/summary.json` | 7 | 4 per-row `elapsed_seconds`, 3 `source_results_files.*.sha256` (which differ only because the three source files differ in their timing fields) |

**Zero non-timing differences.** Every mean, standard deviation, seed, derived
seed, standardized residual, criterion evaluation, known-answer statistic and
`C-16` table entry reproduced exactly.

**Reported as a material finding rather than a footnote:** the numpy version I ran
under **is** `2.4.0`. It is not a different version, and the `C-3e` / `C-19b`
boundary — bit-exactness claimed only *within* the recorded version — was not
tested and is not claimed here. `C-19c`'s `shuffle=True` was therefore not
exercised as a load-bearing clause in this reproduction; it remains load-bearing
for any reader on a different numpy.

---

## 3. Independent re-implementation, from the contract text alone

A ~110-line simulator was written in this session directly from
`process_specification`, `replication.seed_derivation_binding` and amendment
clauses `C-3a`–`C-3e`, `C-19a`, `C-19c`. The Executor's driver was **not** used as
a source for it; the driver was read afterwards only to locate its I/O paths for
§2 and to grep its imports for §7.

```python
def per_tuple_seed(master, arm, c):                       # replication.seed_derivation_binding
    s = "|".join([str(master), arm, str(c["k"]), str(round(c["beta"] * 1000)),
                  str(c["m"]), str(c["B"]), str(c["C_red"])])
    return int.from_bytes(hashlib.sha256(s.encode("ascii")).digest()[:8], "little")

def replicate(rng, N, s, throws, premark):                # P-REPAIRED / P-ASRECORDED
    marked = np.zeros(N, dtype=bool)
    if premark and s > 0:                                 # STEP 1, omitted when s == 0
        marked[rng.choice(N, size=s, replace=False, shuffle=True)] = True   # C-3b + C-19c
    g = rng.integers(0, N, size=throws, dtype=np.int64)   # STEP 2, C-3d, one call
    marked[g] = True                                      # mark g and (N - g) mod N
    marked[(N - g) % N] = True
    return int(marked.sum())                              # STEP 3
```

`RC-C` de-duplication was performed independently: distinct measured `B` within
each `(k, m)` column, first-listed occurrence binding. **49 cells → 48 tuples**,
29 at `m = 2` and 19 at `m = 3`, 37 tuples at 100 replicates and 11 at 30, largest
`C_red` 91922. `P_pred`, `lambda`, `exp(-lambda)` and `T` were recomputed from
`N`, `C_red` and `|S_(m-2)|` rather than quoted.

### 3.1 Agreement with the package

Across all 48 tuples, comparing my values to the committed `results.json` field by
field, **the maximum absolute difference is `0.0` in every one of the following**:

`mean`, `sd_ddof_1`, `sem`, `z_sem`, `z_sd`, `z_shift`, `T`, `P_pred`,
`mu_001_QUOTED`, `s_001_QUOTED`, `sem_001_DETERMINED`, and the as-recorded arm's
`mean` and `sd_ddof_1`. All 96 derived seeds of the two 48-tuple arms match
**exactly as integers**, and all 96 seed strings match **exactly as strings** —
derived by me from the contract text, not read from the package.

`max |P_pred_mine − P_pred_quoted| = 0.0`, `max |lambda_mine − lambda_quoted| = 0.0`,
`max |T_mine − T_quoted| = 0.0` across the 48 tuples — an independent confirmation
of the `IV-4` re-derivation the package reports at max difference `0.0`.

### 3.2 The four criteria, recounted from my own raw means and standard deviations

| criterion | my firing set | my count | package |
|---|---|---|---|
| `CR-1`, `abs(z_sem) >= 3.000` | **empty** | 0 of 48 | empty |
| `CR-2`, `abs(z_sd) >= 3.000` | **empty** | 0 of 48 | empty |
| `CR-3`, `abs(z_shift) >= 3.000` | **empty** | 0 of 48 | empty |
| `CR-4`, `n_neg` | **`n_neg = 16`**, window `[14, 34]` | does not fire | 16 |

- `max abs(z_sem) = 2.6101537975436533` at **`T-18-3-B44`** — confirms the
  dispatching session's `2.6102`.
- `max abs(z_sd) = 0.4765467044908104`.
- `max abs(z_shift) = 2.981990543674932` at **`T-18-2-B140`**.
- `IV-1a`: `abs(z_comp) >= 3.000` at **0** of 48 → does not fire (needs > 2).
- `IV-1b`: `abs(ln_r_sd) >= 3.000/sqrt(n_rep − 1)` at **0** of 48 → does not fire.

**Both denominator readings were recomputed by me at every one of the 48 tuples**,
and both are reported at every one of the 48 rows of the committed
`results.json` (`denominator_reading_primary` = `sem_rep`,
`denominator_reading_secondary` = `s_rep`, each carrying its own denominator value
and `n_rep`). **No cell reports only one.**

### 3.3 The four `INV-4`-failing tuples, end to end

All values in this table were produced by my simulator in this session, and every
one of them equals the committed `results.json` value at absolute difference `0.0`.

| tuple | `N` | `C_red` | `s` | `n` | my `mu_rep` | my `s_rep` | `P_pred` (re-derived) | `z_sem` | `z_sd` | `z_shift` |
|---|---|---|---|---|---|---|---|---|---|---|
| `T-18-3-B16` | 261707 | 688 | 16 | 100 | 703.22 | 1.2758835322547226 | 703.054445298532 | +1.2975690749 | +0.1297569075 | +0.6752535948 |
| `T-16-3-B16` | 65633 | 688 | 16 | 100 | 700.72 | 2.91315372860147 | 700.239731629407 | +1.6486200707 | +0.1648620071 | +0.5769192113 |
| `T-18-3-B24` | 261707 | 2312 | 24 | 100 | 2325.93 | 3.985466019669393 | 2325.6064584777687 | +0.8118034896 | +0.0811803490 | +0.5070122126 |
| `T-18-3-B28` | 261707 | 3668 | 28 | 100 | 3670.16 | 6.892713177660516 | 3670.0252224971387 | +0.1955362125 | +0.0195536213 | +0.9296545773 |

All four reproduce end to end from an independent simulator, and all four sit
inside `3.000` under **both** denominator readings, at tuples where the committed
BATCH-011 antipodal arm records single-sd residuals of `−12.439358544355992`,
`−5.899491744939043`, `−5.74856699942783` and `−3.9202705223876375` respectively
(those four figures are QUOTED from `declared_cell_set`, not measured here).

---

## 4. Known-answer arm `KA-1`–`KA-8`, re-implemented independently

Seeds derived by me from `C-3a` (`master | KNOWNANSWER | case | N | s | C_red`),
stream reuse by `C-19a`.

| case | my seed / stream | my result | contract tolerance | verdict |
|---|---|---|---|---|
| `KA-1` | `8656463976068770938` | all 1000 replicates `distinct = 3` | ZERO | **pass** |
| `KA-2` | `7585293975300151542` | all 1000 replicates `distinct = 11` | ZERO | **pass** |
| `KA-3` | `10737799175533793552` | mean `7.244196`, target `7.2441711010797825`, diff `2.4899e-05` | `<= 4 sd/sqrt(n)` = `4.8344e-03` | **pass** |
| `KA-4` | `7540738932008993469` | 11 frequencies in `[0.271761, 0.274043]` | band `[0.27094583, 0.27450872]` | **pass** |
| `KA-5` | reuses `KA-4` | all 10^6 pre-markings had exactly 3 distinct bins | ZERO | **pass** |
| `KA-6` | `14070980297015205872`, `s = 0` so step 1 omitted | `freq(distinct=1) = 0.090968`, 0 implication violations | band `[0.08975917, 0.09205901]` | **pass** |
| `KA-7` | reuses `KA-6` | marked set `== {g, (11−g) mod 11}` in all 10^6 | ZERO | **pass** |
| `KA-8` | no randomness | `max abs diff = 0.0` at all four tuples | `1e-9` | **pass** |

My independently-derived seeds for `KA-1`, `KA-2`, `KA-3`, `KA-4`, `KA-6` and my
empirical values `7.244196` and `0.090968` **match the committed record exactly**.
`KA-5`, `KA-7` and `KA-8` correctly carry no seed. Generators are seeded for
exactly `KA-1, KA-2, KA-3, KA-4, KA-6` — five, as `C-19a` requires.

**`IV-2` does not fire.** All eight cases pass on an implementation the Executor
did not write.

---

## 5. Bin accounting (`V6`)

Checked at all 48 rows of the committed `results.json`, and independently in my own
simulator:

- **`(N−1)/2` antipodal-pair bins plus the identity bin.** Every row records
  `realised_bin_count = N` and `realised_orbit_count = (N−1)//2 + 1`. **48 of 48
  correct.** The measured quantity is distinct **bins**, not orbits, in both
  implementations.
- **Identity bin eligible for pre-marking.** My `rng.choice(N, ...)` draws from all
  `N` bins including bin 0, per `identity_bin_may_be_pre_marked: YES`. Means agree
  at `0.0`, so the package does the same.
- **Identity bin may be hit.** `g = 0` marks bin 0 only. Verified to zero tolerance
  by my `KA-6`/`KA-7` re-implementation (0 implication violations in 10^6 draws).
- **Pre-marked bins counted once, uniform without replacement.** Verified by my
  `KA-4` (marginals) and `KA-5` (exactly 3 distinct in every one of 10^6
  pre-markings).
- **Odd-`C_red` rule.** All 48 declared `C_red` are even; `throws_per_replicate ==
  C_red // 2` at 48 of 48; no rounding rule is exercised. `IV-4`'s odd-`C_red` arm
  is untriggered and therefore untested — stated, not glossed.
- **The `(N−1)`-versus-`N` bin-count term.** The contract's exact mean is
  `E = N − (1 − s/N)[(N−1)A + C]` over `N` bins. I evaluated it independently at
  all 48 tuples: **largest `E − P_pred` is `0.13051` bins** against the contract's
  declared `at most 0.131 bins`, and **largest `(E − P_pred)/sem_rep` is `0.07542`
  SEM** against the declared `0.0752` tightest per-tuple maximum and the `0.0895`
  SEM envelope. **No silent divergence from the frozen contract was found in any
  of the five bin-accounting items.**

---

## 6. Comparability arm and `IV-1` (`V7`)

`z_comp = (mu_asrec − mu_001)/sqrt(sem_asrec^2 + sem_001^2)` and
`ln_r_sd = ln(s_asrec/s_001)`, recomputed by me from my own as-recorded arm and
from `IN-1` at `2fb2bb7a`:

- `abs(z_comp) >= 3.000` at **0** of 48 tuples. `IV-1a` fires only above 2. **Does
  not fire.**
- `abs(ln_r_sd) >= 3.000/sqrt(n_rep − 1)` (i.e. `0.30151` at the 37 hundred-replicate
  tuples, `0.55709` at the 11 thirty-replicate tuples) at **0** of 48. `IV-1b`
  **does not fire.**
- Mean `z_comp` over the 48 tuples `+0.0868`, sd `1.0585` — centred, as an
  independent re-implementation of the same process should be.

**Independent invalidation verdict: `IV-1` does not fire. The repaired arm's
comparison to the recorded BATCH-011 package is anchored and is not void.** The
`C-9` blind spot stands exactly as the amendment declares it: `IV-1` could not see
the package's largest anomaly even if it were real, and this pass is therefore not
evidence that it is absent.

The merged tuple `T-12-3-B22` uses its **binding committed reference** — the
`beta = 0.325` entry, `mu_001 = 1438.82`, `s_001 = 20.207699302768514`, seed field
`325` — exactly as `merged_tuple_reference_rule` and `merged_tuple_seed_note`
require, and it is drawn once.

---

## 7. Zero curve compute (`V2` scope clause)

From the committed driver blob at `c7189f80`:

- **Imports, complete list:** `argparse, datetime, hashlib, json, math, os,
  platform, resource, subprocess, sys, time, numpy` (plus `traceback` inside an
  exception handler). **Nothing from `harness/`. Nothing from `tools/`. No
  computer-algebra system. No BATCH-011 driver.**
- **Files opened under `experiments/EXP-YIELD-001`:** exactly two, `IN-1` and
  `IN-2`, each SHA-256-verified against the pinned value before parsing. The
  committed `input_integrity_IV_4` block records `sha256_as_read == sha256_pinned`
  for both; I re-verified both against the blobs myself.
- **No elliptic-curve arithmetic of any kind appears**: no point addition,
  doubling, scalar multiplication, curve order, factor-base construction or sum-set
  construction. The only occurrences of the string `curve` are in the
  `preregistered_power_curve` (a table of `phi` versus `E[n_neg]`) and in prose
  disclaimers.
- **Subprocess use** is confined to read-only `git` invocations and two
  `orchestration.adapter` calls that capture inference provenance. Neither produces
  a reported measurement.
- **Every input is quoted.** `N`, `B`, `C_red`, `m`, `beta`, `k`, `p`, `L`,
  `replicates`, `|S_(m-2)|`, `P_pred`, `lambda`, `exp(-lambda)`, `T`, `mu_001` and
  `s_001` all come from `IN-1`. I re-read every one of them from the blob at
  `2fb2bb7a` and compared: **max absolute difference `0.0` across all 48 tuples for
  all of them.**

---

## 8. `C-16` committed-table re-derivation (`DEV-3` tolerances)

`delta_i = (bias_i − r_i)/sem_001,i` with `bias_i` the exact process bias and
`r_i = mu_001,i − (P_pred,i − T_i)`; `p_i(c) = Q(c sqrt(2) − delta_i) + Q(c sqrt(2)
+ delta_i)`. Re-derived by me from `IN-1` and from the closed-form exact mean,
independently of the driver, and compared against the committed
`RT-20260729-029` table at `5174001c` (whose blob I hashed: `05f6e7cc...`, equal to
the `source.sha256` the driver records):

| quantity | Executor reports | **this session** | `DEV-3` tolerance | verdict |
|---|---|---|---|---|
| `max abs(delta_i − QUOTED)` | `4.939e-06` | **`4.939094e-06`** | `1e-5` | **within** |
| `max abs(p_i(3.000) − QUOTED)` | `4.987e-07` | **`4.987526e-07`** | `1e-6` | **within** |
| `max abs(r_i − IN-1 residual_after_adding_back)` | `0.0` | **`0.0`** | `1e-9` | **exact** |

Against the driver's own re-derived column my values agree to `9.76e-09`
(`delta_i`), `9.62e-10` (`p_i`) and `1.12e-07` (`bias_i`) — differences of
floating-point association only.

The two `C-16` pre-registered offenders reproduce: `T-18-2-B264` `delta = 2.93363`,
`p_i(3.000) = 0.095265`; `T-14-2-B118` `delta = −2.63998`, `p_i(3.000) = 0.054505`.
**Neither fired.** Their realised `abs(z_shift)` are `1.9806` and `1.5698`.

`DEV-3`'s reading is sound: the committed table is printed to 5 and 6 decimals, so
exact equality is unattainable in principle and a tolerance at print precision is
the only available reading. The realised maxima are within it by a factor of ~2.

---

## 9. `DEV-4` — does the shared `HIGHPREC` seed feed anything?

**The contract defect is real, and the Executor's reading was the right one.**

`replication.seed_derivation_binding` fixes the seed string fields as
`master | arm | k | round(beta*1000) | m | B | C_red` and enumerates the arm labels
as **exactly** `REPAIRED`, `ASRECORDED`, `KNOWNANSWER`, `HIGHPREC`.
`CTRL-002-DIAGNOSTIC-HIGHPRECISION` runs **both** processes at the same four
tuples under master seed `120501`. No field in the seed string distinguishes the
process. **The contract as written therefore mandates a shared per-tuple seed for
the two legs it exists to compare.** The alternative — inventing a label such as
`HIGHPREC-REPAIRED` — would be an Executor-side change to a frozen enumerated set.
Taking the contract literally and declaring the defect is the conservative choice
and is the correct one.

**Confirmed that it feeds nothing.** Traced in this session:

- The four `HIGHPREC` seeds appear only in `highprec_block()` and in the manifest's
  `high_precision_block_per_tuple`. They do not enter `repaired_arm.rows`.
- The criteria block (`CR-1`–`CR-4`) is computed from `repaired_arm.rows` only; my
  independent recount, which never touched the block, reproduces all four criteria
  exactly. That is the strongest possible demonstration that the block feeds no
  criterion.
- `IV-1` reads the as-recorded arm; `IV-2` reads the known-answer arm. Neither
  reads the block.
- The `DEV-5` phi-equivalent is computed from per-tuple
  `shortfall = P_pred − mu_rep` on the **criterion** arm and from `realised_n_neg`,
  not from the block.
- The block reports only `mean`, `sd_ddof_1`, `sem`, a measured mean difference and
  `T_DETERMINED`. **It attaches no standard error to the difference and computes no
  `z`** — which matters, because a shared stream would have made any such error bar
  wrong.
- Seed audit: 48 `REPAIRED` + 48 `ASRECORDED` + 4 `HIGHPREC` + 5 `KNOWNANSWER` =
  **105 seeds, 105 distinct**, with **no overlap between any two arms**. The only
  sharing anywhere in the package is the intended `KA-5`/`KA-4` and `KA-7`/`KA-6`
  stream reuse, and the `DEV-4` sharing between the block's two legs.

**One residual reading risk, which is the reason this needs a narrowing rather than
a clean bill.** Because the two legs share a stream, the block's
`repaired − asrecorded` differences (`15.9447` vs `T = 15.9580`; `15.8261` vs
`15.8332`; `23.7687` vs `23.7889`; `27.5352` vs `27.6103`) are **common-random-number**
estimates. Their apparent tightness is not the tightness two independent 10^4-replicate
draws would show, and no record may read it as an independent confirmation of `T`.

---

## 10. The unexplained observation: `z_sem` mean `+0.3610`

### 10.1 Reproduced

From my own simulator, over the 48 tuples:

```
mean(z_sem)  = 0.361024        (package: 0.36102368504276455)
sd(z_sem)    = 0.975002        (package: 0.9750016841736118)
SE of mean   = 0.140729
t            = 2.5654
n_neg        = 16
```

**Reproduced exactly.** Counts of `abs(z_sem)` above 1 / 2 / 3 are 15 / 4 / 0
against standard-normal expectations 15.23 / 2.18 / 0.13 for 48 draws.

### 10.2 Search for an instrument cause

Four candidate causes were tested. **None explains it.**

**(a) The two declared second-order biases.** I evaluated the contract's own exact
mean `E = N − (1 − s/N)[(N−1)A + C]` at all 48 tuples and formed
`bias_i/sem_rep_i`:

```
min 0.00468   max 0.07542   mean 0.02638
```

The declared `0.0895` SEM envelope **holds**, and the declared per-tuple maximum
`0.0752` is confirmed at `T-12-2-B46`. But the mean bias is only `+0.0264`.
Re-standardizing against the **exact** process mean instead of `P_pred` leaves

```
mean(z_exact) = 0.334642   sd 0.974   SE 0.140641   t = 2.3794
```

so **the declared biases account for `0.026` of `0.361` and no more.**

**(b) Small-sample skewness of the standardized statistic.** Replicate-level
skewness across the 48 tuples has mean `−0.2172` (range `−1.810` to `+0.721`),
giving a predicted `t`-statistic bias of `+0.011`. Real, correctly signed, and an
order of magnitude too small.

**(c) An off-by-one in the pre-mark, a `ddof` inconsistency, or a wrong shuffle
keyword.** Excluded structurally: my simulator was written from the contract text,
marks exactly `s` bins, uses `ddof = 1` for `s_rep` and `sem = s_rep/sqrt(n_rep)`,
and reproduces every package number at `0.0`. Two independently-written
implementations agreeing bit-for-bit rules out a coding slip in either — and if the
*specification* itself induced a systematic upward shift, that shift would appear in
(d) below. It does not.

**(d) A seeding correlation or a pathology of the SHA-256 seed derivation.** Two
Monte Carlo experiments were run in this session, both with seeds disjoint from
every seed the contract uses:

- **`numpy.SeedSequence.spawn`, 100 repetitions of the entire 48-tuple design:**
  `mean(z_sem)` over 48 has MC mean `+0.0342`, MC sd `0.1320`. Observed `+0.3610`
  is `2.48` MC sd above; `1` of `100` repetitions reached it. `n_neg` MC mean
  `23.55` (the contract's declared Poisson-binomial `E[n_neg] = 23.504`), and
  `n_neg <= 16` in `1` of `100`.
- **The contract's own SHA-256 seed rule, 400 repetitions under master seeds
  `500000 + 13i`:** MC mean `+0.0439`, MC sd `0.1473` (the independence prediction
  is `sqrt(1.03/48) = 0.147` — the seed machinery behaves exactly as independent
  streams should). `P(mean z_sem >= 0.361024) = 0.0100 +/- 0.0050`.
  `P(n_neg <= 16) = 0.0200`. `n_neg` MC mean `23.25`, sd `3.42`.

The MC mean `+0.037`-to-`+0.044` is fully accounted for by (a) `+0.026` plus (b)
`+0.011`.

**(e) Structure across strata**, which a real instrument effect would show:

| stratum | n | mean `z_sem` |
|---|---|---|
| all | 48 | `+0.3610` |
| `m = 2` / `m = 3` | 29 / 19 | `+0.3698` / `+0.3477` |
| `n_rep = 100` / `30` | 37 / 11 | `+0.3207` / `+0.4966` |
| `k = 12` / `14` / `16` / `18` | 8 / 9 / 15 / 16 | `+0.7091` / `+0.0113` / `+0.0046` / `+0.7179` |

`corr(z_sem, lambda) = +0.031`; `corr(z_sem, log N) = +0.064`;
`corr(z_sem, s) = −0.063`; `corr(z_sem, z_comp) = −0.066` (independent streams,
expected 0). **There is no gradient in `lambda`, `N` or `s`** — the shift is not
tracking any parameter a mis-specified process would track, and the `k = 14` and
`k = 16` columns sit at zero.

### 10.3 Finding

**No instrument cause was found.** The shift is not a seeding correlation, not a
shared stream, not an off-by-one in the pre-mark, not a `ddof` inconsistency, and
not a skewness artifact. Under a correct implementation of the *specified* process
at other seeds it does not recur: it is an **upper-tail excursion of roughly
`0.010` (MC, `M = 400`, `+/- 0.005`)** of this particular pre-registered seed set,
with `n_neg = 16` sitting at `P = 0.020` of the same MC and being the same data
seen through a coarser statistic rather than independent corroboration.

**This validator does not interpret what that means.** Two readings remain open and
both belong to `TASK-20260729-021` and the Coordinator: (i) chance, at a rate the
contract's own `0.377` marginal budget was never computed to cover for an
*aggregate* statistic that no criterion tests; (ii) a small positive component in
the specified process that neither declared bias captures and that the design has
no power to resolve. The design's own `C-20` sentence already covers the second:
a shortfall — or excess — of 5 per cent of `T` or less would very likely go
undetected by anything in this contract.

---

## 11. Checks reached, and checks not reached inside the cap

**Reached:** snapshot receipt against Git; contract immutability and precedence;
approval precedence in the commit graph; re-execution and bit-level diff;
independent re-implementation of both null processes, of `P_pred`, of the seed
derivation and of all four criteria; all eight known-answer cases; `IV-1`; `IV-4`
input integrity; the `C-16` table; bin accounting in all five items; both
denominators at all 48 cells; raw-to-summary agreement over 48 tuples x 16
quantities plus five whole-block equalities; manifest schema against the AGENTS.md
artifact policy for all three runs; seed distinctness across all 105 seeds; all
seven declared deviations; a two-experiment Monte Carlo of the aggregate shift.

**Not reached, and named as required:**

1. **Cross-platform and cross-version reproduction.** My re-execution used the same
   interpreter, the same architecture and the same numpy `2.4.0` as the package.
   The `C-3e` boundary — bit-exactness only within the recorded version — is
   restated, not tested.
2. **`RC-F`.** My re-implementation is also derived from the same contract text. A
   process error transcribed faithfully into the contract would be invisible to me
   exactly as `C-12`/`C-21` say it is invisible to `IV-1`. The `P-REPAIRED` step-1
   asymmetry applies to my re-implementation too and is the only part of this that
   is genuinely independent of the BATCH-011 driver.
3. **The odd-`C_red` arm of `IV-4`** is untriggered by the declared set and
   therefore untested by anything, including me.
4. **The exact-`A1` column of the `C-16` table** is quoted, not re-derived, by the
   Executor (`DEV-3`, no scipy) and was not re-derived by me either. Only the `A2`
   column and `delta_i` were independently checked.
5. **Whether the driver's author read `yield_census.py`.** Unverifiable from
   artifacts; see §1.
6. **Model independence.** Unavailable (`INT-BATCH012-D`) and not claimed.
