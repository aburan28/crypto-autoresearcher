# Recount note — VAL-20260729-002 / TASK-20260729-037

Independent validation working notes for the EXP-YIELD-003 run package committed at
`6921e7160f2e21711361e3fe8d346d25328238be` (parent `572ce080a1dd9ea76b078e0ec6d96e9f8ff522c9`,
branch `claude/ecdlp-b011`), governed by `experiments/EXP-YIELD-003/specification.yaml` at
`de6fbb752f9f0b9ce28fda91b15a88593861dfcc`.

The verdict, the rulings and the thirteen required narrowings live in
`validation_report.yaml` beside this file. This note carries the arithmetic.

**Nothing in this note interprets the mathematics.** No resume condition is applied and no
disposition of the difference between the two measurements is taken.

---

## 0. Independence basis

Fresh non-originating session. This session did not author the contract (TASK-20260729-031),
did not review it (TASK-20260729-033), did not execute it (TASK-20260729-035), did not archive
it (TASK-20260729-036), and shares no conversation lineage with TASK-20260729-031, -033, -035
or -038. Every input was read from committed Git blobs or committed archive receipts. No
producer working tree was consulted. **Model independence is not available and is not claimed**
(INT-BATCH013-D); the requested policy was `review-adversarial`, the resolved model is
self-reported `claude-opus-5`, and `model_verified` is **false**.

---

## 1. Snapshot verification

| check | result |
|---|---|
| `6921e716` reachable from HEAD `2c6b11f3` | YES |
| first (and only) parent | `572ce080a1dd9ea76b078e0ec6d96e9f8ff522c9` — matches receipt |
| changed paths | exactly **11**, all status `A` |
| deletions / renames / extras | none |
| AppleDouble sidecars, `__pycache__` | none |
| declared 12 vs committed 11 | the deferred twelfth is the receipt itself (INT-BATCH007-T) — strict subset, not a scope overrun |

All eleven recorded SHA-256 values were **recomputed from the Git blobs at that commit** by
piping `git cat-file blob 6921e716:<path>` through SHA-256. **All eleven match.**

The eleven committed paths are set-identical to the contract's `required_artifacts` list and
to the `eleven_declared_artifact_paths` field carried in all three manifests.

Input bindings were verified against the **bound commits**, not the worktree:

| input | bound commit | SHA-256 as read from the blob | matches the pin |
|---|---|---|---|
| IN-1 | `2fb2bb7a` | `040207f8…25cd` | YES |
| IN-2 | `2fb2bb7a` | `2287b277…2aeb` | YES |
| IN-3 | `c7189f80` | `73bb3ae1…caf8` | YES |
| IV-2 extra 1 (ASRECORDED) | `c7189f80` | `c486194d…556c1` | YES |
| IV-2 extra 2 (KNOWNANSWER) | `c7189f80` | `d99b8833…3799` | YES |

Cross-bindings: the driver SHA-256 recorded in all three manifests and all three
`results.json` environment blocks equals the committed driver blob; `summary.json`'s
`source_results_files` digests equal the three committed `results.json` digests.

---

## 2. The primary observation, recomputed from the 48 raw rows

Method: for each row, `z_i = (mean_i − P_pred_i) / (sd_ddof_1_i / sqrt(n_rep_i))`, computed
in this session with code written in this session — **not** the driver's summary code — then
mean, sample sd at ddof 1, and sd/sqrt(48).

| quantity | recomputed | package | difference |
|---|---|---|---|
| n | 48 | 48 | — |
| mean | `0.33369767840297898` | `0.33369767840297898` | **0.0** |
| sample sd (ddof 1) | `0.89157053997649016` | `0.89157053997649016` | **0.0** |
| standard error | `0.12868712281424166` | `0.12868712281424166` | **0.0** |
| min | `-1.6051967280661212` | same | 0.0 |
| max | `2.2570411311500851` | same | 0.0 |
| n_neg | **16** | 16 | — |
| tails \|z\|>1, >2, >3 | **12 / 3 / 0** | 12 / 3 / 0 | — |
| max \|z_sem\| | `2.2570411311500851` → **2.257041** | 2.257041 | 0.0 |
| attained at | **T-18-2-B82** | T-18-2-B82 | — |

**Maximum absolute difference over the whole 48-entry z_sem vector: exactly 0.0.** The sorted
48-entry vector is element-wise identical to the recorded `sorted_z_sem_vector_verbatim`.

n_neg was computed three independent ways — `z_sem < 0`, the recorded sign field, and
`mean − P_pred < 0` — all giving 16 with the same sixteen named members:
T-12-2-B36, T-12-2-B54, T-14-2-B34, T-14-2-B44, T-14-2-B56, T-14-2-B118, T-16-2-B72,
T-18-2-B44, T-18-2-B110, T-18-2-B140, T-18-2-B192, T-12-3-B20, T-14-3-B26, T-14-3-B34,
T-16-3-B38, T-18-3-B34.

**Reported honestly:** an alternative summation route (`statistics.stdev`) returns
`0.89157053997649005`, one ulp below the recorded value. The naive route and the `math.fsum`
route both return the recorded double bit for bit. This is float summation order, not a defect.

Replicate split: **37 tuples at n_rep = 100, 11 at n_rep = 30**, reproducing the C-14 schedule
from `C_red` and matching IN-1's own `replicates` field at all 48 tuples. The 10-replicate
tier is unreachable (largest `C_red` = 91922).

### Comparator, recomputed from the committed EXP-YIELD-002 blob

From `RUN-YIELD-002-NULL-REPAIRED/results.json` at `c7189f80`, by the same independent route:

- mean **0.3610236850427646** (the driver's quoted constant `0.36102368504276455` is this
  double exactly), sd **0.9750016842**, standard error **0.1407293712** (the receipt quotes
  0.1407), n_neg 16, tails 15/4/0, max 2.6101537975436533.
- Difference of means **0.0273260066**; combined standard error **0.1906748** using the
  receipt's rounded 0.1407 and **0.1906964** using the exact value; the ratio is **0.14 SE**
  either way.

**Comparability:** identical 48 tuple labels in identical order, identical `n_rep` tuple by
tuple, identical `P_pred` tuple by tuple, and a **different derived seed at every one of the
48 tuples**.

### Full per-tuple recount

| # | tuple | n_rep | mean (raw) | sd_ddof_1 (raw) | P_pred (quoted) | z_sem recomputed | z_sem recorded | diff |
|---|---|---|---|---|---|---|---|---|
| 1 | T-12-2-B36 | 100 | 599.01 | 8.94708913784 | 599.09744201 | -0.09773235555153013 | -0.09773235555153013 | 0.0 |
| 2 | T-12-2-B42 | 100 | 792.7 | 12.13601369 | 792.352616947 | 0.286241480627682 | 0.286241480627682 | 0.0 |
| 3 | T-12-2-B46 | 100 | 930.65 | 12.6118230565 | 930.438421102 | 0.167762342270332 | 0.167762342270332 | 0.0 |
| 4 | T-12-2-B54 | 100 | 1220.99 | 18.1494886813 | 1222.57154655 | -0.8714000570157971 | -0.8714000570157971 | 0.0 |
| 5 | T-12-2-B62 | 100 | 1528.44 | 21.2841858115 | 1526.80656986 | 0.7674383953958387 | 0.7674383953958387 | 0.0 |
| 6 | T-14-2-B34 | 100 | 568.84 | 3.94077365116 | 569.030071499 | -0.482320263832912 | -0.482320263832912 | 0.0 |
| 7 | T-14-2-B44 | 100 | 941.14 | 7.21393152732 | 941.291541576 | -0.2100679427476833 | -0.2100679427476833 | 0.0 |
| 8 | T-14-2-B56 | 100 | 1496.93 | 11.8264000175 | 1497.21219703 | -0.2386161695577788 | -0.2386161695577788 | 0.0 |
| 9 | T-14-2-B72 | 100 | 2401.78 | 18.2953214751 | 2400.83485988 | 0.5166020846316202 | 0.5166020846316202 | 0.0 |
| 10 | T-14-2-B86 | 100 | 3318.66 | 23.8061277232 | 3316.25974325 | 1.008251647697118 | 1.008251647697118 | 0.0 |
| 11 | T-14-2-B118 | 100 | 5687.6 | 37.1505264587 | 5688.37656484 | -0.2090319879285488 | -0.2090319879285488 | 0.0 |
| 12 | T-16-2-B38 | 100 | 719.15 | 2.73168834462 | 719.032378077 | 0.4305832427792581 | 0.4305832427792581 | 0.0 |
| 13 | T-16-2-B48 | 100 | 1143.31 | 4.42603637353 | 1142.93145718 | 0.8552636873705156 | 0.8552636873705156 | 0.0 |
| 14 | T-16-2-B58 | 100 | 1661.65 | 7.61759658802 | 1661.60503362 | 0.05902961118231318 | 0.05902961118231318 | 0.0 |
| 15 | T-16-2-B72 | 100 | 2542.41 | 9.36584704707 | 2542.44638579 | -0.03884943337759667 | -0.03884943337759667 | 0.0 |
| 16 | T-16-2-B88 | 100 | 3761.05 | 14.203694924 | 3760.94221155 | 0.07588761157052992 | 0.07588761157052992 | 0.0 |
| 17 | T-16-2-B116 | 100 | 6396.26 | 24.0015235207 | 6395.54820631 | 0.2965618784635907 | 0.2965618784635907 | 0.0 |
| 18 | T-16-2-B144 | 30 | 9598.9 | 41.4548778379 | 9591.4114562 | 0.9894238207441227 | 0.9894238207441227 | 0.0 |
| 19 | T-16-2-B192 | 30 | 16077 | 53.7760361961 | 16070.7703077 | 0.6345099467196165 | 0.6345099467196165 | 0.0 |
| 20 | T-16-2-B246 | 30 | 24248.53333 | 80.1041276363 | 24242.7520436 | 0.3953033272345757 | 0.3953033272345757 | 0.0 |
| 21 | T-18-2-B34 | 100 | 578.52 | 0.989643339488 | 578.359984811 | 1.616897547597426 | 1.616897547597426 | 0.0 |
| 22 | T-18-2-B44 | 100 | 967.18 | 2.22192927362 | 967.208297437 | -0.1273552531226473 | -0.1273552531226473 | 0.0 |
| 23 | T-18-2-B58 | 100 | 1677.77 | 3.29325910848 | 1677.60001838 | 0.5161501535427916 | 0.5161501535427916 | 0.0 |
| 24 | T-18-2-B82 | 100 | 3342.72 | 5.4736835971 | 3341.4845671 | 2.257041131150085 | 2.257041131150085 | 0.0 |
| 25 | T-18-2-B110 | 100 | 5979.66 | 11.9774366999 | 5981.58261422 | -1.605196728066121 | -1.605196728066121 | 0.0 |
| 26 | T-18-2-B140 | 100 | 9618.33 | 18.0213425659 | 9619.74464442 | -0.7849828122125881 | -0.7849828122125881 | 0.0 |
| 27 | T-18-2-B192 | 30 | 17794.26667 | 32.0247031086 | 17798.8236494 | -0.7793865304812018 | -0.7793865304812018 | 0.0 |
| 28 | T-18-2-B264 | 30 | 32635.2 | 49.048463015 | 32628.3965896 | 0.7597345744482393 | 0.7597345744482393 | 0.0 |
| 29 | T-18-2-B390 | 30 | 66040.16667 | 121.617286468 | 65997.8584197 | 1.905418372729015 | 1.905418372729015 | 0.0 |
| 30 | T-12-3-B16 | 100 | 646.12 | 8.60147978812 | 645.568750542 | 0.640877466907839 | 0.640877466907839 | 0.0 |
| 31 | T-12-3-B20 | 100 | 1151.37 | 15.7958279877 | 1153.00062788 | -1.032315546956421 | -1.032315546956421 | 0.0 |
| 32 | T-12-3-B22 | 100 | 1452.64 | 20.1927679823 | 1452.15101558 | 0.2421581907985726 | 0.2421581907985726 | 0.0 |
| 33 | T-14-3-B20 | 100 | 1306.79 | 8.45701549668 | 1305.85133723 | 1.109922017173411 | 1.109922017173411 | 0.0 |
| 34 | T-14-3-B26 | 100 | 2714.21 | 19.724514307 | 2714.7393765 | -0.2683850639739132 | -0.2683850639739132 | 0.0 |
| 35 | T-14-3-B34 | 100 | 5439.58 | 34.9710356343 | 5444.33230614 | -1.358926338968321 | -1.358926338968321 | 0.0 |
| 36 | T-16-3-B16 | 100 | 700.77 | 2.42401703498 | 700.239731629 | 2.187560412908034 | 2.187560412908034 | 0.0 |
| 37 | T-16-3-B22 | 100 | 1779.74 | 6.36692844139 | 1779.4366581 | 0.4764336628194231 | 0.4764336628194231 | 0.0 |
| 38 | T-16-3-B30 | 100 | 4386.65 | 16.7804449683 | 4386.5435529 | 0.0634352079275492 | 0.0634352079275492 | 0.0 |
| 39 | T-16-3-B38 | 100 | 8578.68 | 32.5104116967 | 8580.8360052 | -0.6631737602382661 | -0.6631737602382661 | 0.0 |
| 40 | T-16-3-B48 | 30 | 16131.66667 | 55.6951885084 | 16118.3346657 | 1.31110745249711 | 1.31110745249711 | 0.0 |
| 41 | T-16-3-B58 | 30 | 25701.63333 | 69.2643528427 | 25690.6238983 | 0.870594423578086 | 0.870594423578086 | 0.0 |
| 42 | T-18-3-B16 | 100 | 703.3 | 1.0963668191 | 703.054445299 | 2.239712997424541 | 2.239712997424541 | 0.0 |
| 43 | T-18-3-B24 | 100 | 2326.11 | 4.2590248801 | 2325.60645848 | 1.18229298115739 | 1.18229298115739 | 0.0 |
| 44 | T-18-3-B28 | 100 | 3670.29 | 7.75156549845 | 3670.0252225 | 0.3415793918199305 | 0.3415793918199305 | 0.0 |
| 45 | T-18-3-B34 | 100 | 6512.36 | 13.466396637 | 6513.57410944 | -0.9015844941942143 | -0.9015844941942143 | 0.0 |
| 46 | T-18-3-B44 | 30 | 13877.43333 | 25.8919283566 | 13874.6743972 | 0.5836303569593878 | 0.5836303569593878 | 0.0 |
| 47 | T-18-3-B58 | 30 | 30648.33333 | 57.8477987143 | 30647.7824847 | 0.05215621370149613 | 0.05215621370149613 | 0.0 |
| 48 | T-18-3-B82 | 30 | 77586.9 | 99.7394363951 | 77571.4716772 | 0.8472516697410911 | 0.8472516697410911 | 0.0 |

---

## 3. Re-execution of the committed driver

**Scope, stated first: this establishes determinism of the recorded pipeline and not
portability**, exactly as NARROW-5 required of BATCH-012. Same host, same OS, same architecture.

The committed driver blob and the five committed input blobs were extracted from Git into a
scratch root **outside the repository**; all three arms plus the summary step were re-executed
there in ST-2 order. Nothing was written inside the repository and the scratch root was deleted
afterwards. **These probes are UNARCHIVED AND ARE NOT EVIDENCE.**

Interpreter this validator ran under:

| field | value |
|---|---|
| `sys.version` | `3.14.3 (main, Feb  3 2026, 15:32:20) [Clang 17.0.0 (clang-1700.6.3.2)]` |
| `sys.executable` | `/opt/homebrew/opt/python@3.14/bin/python3.14` |
| `numpy.__version__` | `2.4.4` |
| `platform.platform()` | `macOS-26.6-arm64-arm-64bit-Mach-O` |
| `platform.machine()` | `arm64` |

— identical to the environment the three arms recorded.

Every leaf of `summary.json` and of all six run documents was compared at **exact float
equality**: **9022 leaves compared, 143 differ, 0 unclassified.**

| class | count | what |
|---|---|---|
| TIMING | 113 | `elapsed_seconds` at every level, `ru_utime`, `ru_stime`, `ru_maxrss`, `peak_memory_gb`, `started_utc`, `ended_utc` |
| GIT_STATE | 24 | 15 value diffs + 9 key-set diffs. The scratch root is not a Git repo, so `git_state()` records its documented `UNAVAILABLE` sentinel instead of commit `572ce080` / branch `claude/ecdlp-b011`. The helper degrades gracefully rather than aborting. |
| PATH_CWD | 12 | `invocation_cwd`, `git.worktree`, and the PP-1 leg `command` strings, which embed the absolute driver path |
| SELF_ARTIFACT_SHA | 3 | `summary.json`'s `source_results_files` digests, which cover files containing the timing fields above |

**Every scientific leaf reproduced bit for bit**: all 48 per-tuple means, sds, sems, minima,
maxima, z_sem, z_sd, delta_z, `mean_minus_P_pred`, seed strings, derived seeds, throw counts
and variate counts; all eight known-answer targets, half-bands, admissible intervals and pass
flags; all ten high-precision leg means, differences and standard errors; all tail counts;
n_neg; OM-5, OM-6, OM-7; and both PP-1 leg vectors.

---

## 4. PP-1, tested independently rather than relayed

The claim: the 48-tuple z_sem vector reproduces **bit-identically** under python 3.13.1 with
numpy 2.4.0 — the exact committed EXP-YIELD-002 reference environment — and under 3.13.3 with
numpy 2.4.4.

**This validator could reach 3.13.1, and did.** Rather than reading the driver's own PP-1
sub-block, this session located the interpreters itself and re-executed the **full primary arm**
under each, in its own separate scratch root outside the repository.

| environment | source | all 48 means | all 48 sds | all 48 z_sem | OM-5 mean / sd / SE |
|---|---|---|---|---|---|
| 3.14.3 / numpy 2.4.4 | `/opt/homebrew/opt/python@3.14/bin/python3.14` | bit-identical | bit-identical | bit-identical | identical doubles |
| **3.13.1 / numpy 2.4.0** | `/Library/Frameworks/Python.framework/Versions/3.13/bin/python3` | bit-identical | bit-identical | **bit-identical** | identical doubles |
| 3.13.3 / numpy 2.4.4 | `/opt/homebrew/opt/python@3.13/bin/python3.13` | bit-identical | bit-identical | bit-identical | identical doubles |

**PP-1 CONFIRMED, at wider scope than PP-1 itself claims** (the whole arm, not only the z_sem
vector).

Corroborated **below the driver** as well: seeding `numpy.random.default_rng` with the
recorded derived seed `356104778378094363` and taking three raw 64-bit words returns
`[17567666082275304732, 3790038648535906794, 4113252643005023423]` under **both** numpy 2.4.4
and numpy 2.4.0 — reproducing the DEV-7 / RC-33-M probe exactly and showing the PCG64 stream
itself is unchanged between the two numpy versions on this host.

Consequence, recorded without interpretation: **the interpreter build and the numpy version are
excluded as sources of the difference between the two measurements, on this host.** PP-1 remains
no portability result, no cross-version determinism result and no separation of the driver from
the build (PDC-8).

Not obtainable and stated plainly: 3.11.14, 3.12.13 and 3.9.6 carry no numpy; **no different
operating system and no different machine architecture exist on this host.**

---

## 5. Seed machinery, derived independently

The derivation was reimplemented in this session directly from the contract's
`seed_derivation_binding` and `knownanswer_seed_derivation` clauses — low 64 bits of the
SHA-256 digest of the pipe-joined ASCII string, read as an **unsigned little-endian** integer —
with parameters taken from **IN-1's cells at `2fb2bb7a`** under the RC-C first-listed-occurrence
rule, not from the run's own rows.

| | |
|---|---|
| seeds derived independently | **73** (48 primary + 5 seeded known-answer + 20 high-precision legs) |
| mismatches against the recorded seed strings | **0** |
| mismatches against the recorded derived seeds | **0** |
| pairwise distinct | **YES** (73 distinct strings, 73 distinct seeds) |
| identical to the package's own `all_derived_seeds_of_EXP_YIELD_003` | YES |

RC-C detail: IN-1 carries **49** cells; de-duplication on `(k, m, B)` yields **48**; the single
merge is **T-12-3-B22**, whose two cells differ only in beta (0.325 and 0.35). The
**first-listed** occurrence binds, so `round(beta × 1000) = 325`, and the recorded seed string
is `130301|REPLICATE-REPAIRED|12|325|3|22|1782` — which is what the rule requires.

### Comparison pools, measured by enumeration (PDC-11)

| pool | fields | distinct |
|---|---|---|
| three committed EXP-YIELD-002 run `results.json` files | **109** | **105** |
| IN-1 | **98** | **98** |

The four repeats in the EXP-YIELD-002 pool were located and named: seeds
`8735327159238186120`, `16248446860608800986`, `14480249529526124894` and
`5582516736328533752`, each appearing once in `repaired_arm.rows` and once in
`repaired_arm.INV_4_failing_tuples_reported_separately.rows` inside
**RUN-YIELD-002-NULL-REPAIRED** — exactly the four INV-4-failing tuples printed twice, exactly
as PDC-11 states. IN-1's 98 split **49 antipodal + 49 independent-throw contrast**, also as
PDC-11 requires.

### Disjointness

| test | collisions |
|---|---|
| my 73 ∩ the 105 EXP-YIELD-002 seeds | **0** |
| my 73 ∩ the 98 IN-1 seeds | **0** |
| my 73 ∩ (union of both) | **0** |
| any of my 73 inside the BATCH-011 master block 110200–110799 | **0** |
| master seeds 130301/130401/130501 ∩ {120201, 120301, 120401, 120501} | **0** |
| master seeds inside 110200–110799 | **0** |

**NO COLLISION. NOT BLOCKING.**

Residual, disclosed by the contract and confirmed real here: IV-2b and IV-2c cover only seeds
recorded in files this contract hash-binds. BATCH-011 run records outside those files are
covered by nothing but the master-seed block declaration, which is a design fact and not a proof
about SHA-256 outputs. That residual remains open.

### The DEV-4 repair

**Verified at all ten block tuples**, independently derived: the two legs differ only in the
arm-label field, so they produce different seed strings and different derived seeds everywhere.
The check is logged before the first draw in all three runs.

| # | tuple | REPAIRED seed string | seed | ASRECORDED seed string | seed | differ |
|---|---|---|---|---|---|---|
| 1 | T-18-3-B16 | `130501\|HIGHPREC-REPAIRED\|18\|200\|3\|16\|688` | 16672017974494891650 | `130501\|HIGHPREC-ASRECORDED\|18\|200\|3\|16\|688` | 15026484646879814662 | YES |
| 2 | T-16-3-B16 | `130501\|HIGHPREC-REPAIRED\|16\|225\|3\|16\|688` | 6356169809231926865 | `130501\|HIGHPREC-ASRECORDED\|16\|225\|3\|16\|688` | 5991715046859099274 | YES |
| 3 | T-18-3-B24 | `130501\|HIGHPREC-REPAIRED\|18\|225\|3\|24\|2312` | 121912427948858533 | `130501\|HIGHPREC-ASRECORDED\|18\|225\|3\|24\|2312` | 13960447756825278665 | YES |
| 4 | T-18-3-B28 | `130501\|HIGHPREC-REPAIRED\|18\|250\|3\|28\|3668` | 14829997857889012902 | `130501\|HIGHPREC-ASRECORDED\|18\|250\|3\|28\|3668` | 13393213991645824056 | YES |
| 5 | T-18-2-B34 | `130501\|HIGHPREC-REPAIRED\|18\|275\|2\|34\|578` | 12398305793511588173 | `130501\|HIGHPREC-ASRECORDED\|18\|275\|2\|34\|578` | 8061075119661171871 | YES |
| 6 | T-18-2-B44 | `130501\|HIGHPREC-REPAIRED\|18\|300\|2\|44\|968` | 2156437820764859131 | `130501\|HIGHPREC-ASRECORDED\|18\|300\|2\|44\|968` | 16589995872952076831 | YES |
| 7 | T-18-2-B58 | `130501\|HIGHPREC-REPAIRED\|18\|325\|2\|58\|1682` | 3227265022682286369 | `130501\|HIGHPREC-ASRECORDED\|18\|325\|2\|58\|1682` | 8153778479269885790 | YES |
| 8 | T-14-2-B118 | `130501\|HIGHPREC-REPAIRED\|14\|475\|2\|118\|6962` | 12429249545767948919 | `130501\|HIGHPREC-ASRECORDED\|14\|475\|2\|118\|6962` | 6180683322136222779 | YES |
| 9 | T-16-2-B246 | `130501\|HIGHPREC-REPAIRED\|16\|500\|2\|246\|30258` | 6261072199896633972 | `130501\|HIGHPREC-ASRECORDED\|16\|500\|2\|246\|30258` | 6737606402297603529 | YES |
| 10 | T-12-2-B62 | `130501\|HIGHPREC-REPAIRED\|12\|500\|2\|62\|1922` | 12216608495795058934 | `130501\|HIGHPREC-ASRECORDED\|12\|500\|2\|62\|1922` | 6986308684030574264 | YES |

**Error-bar status:** the difference column **now has a quantifiable error bar**, which the
committed EXP-YIELD-002 column does not and never will. Because the legs are independently
seeded the variances add, so `sqrt(sem_repaired² + sem_asrecorded²)` is a valid standard
error; it is recorded at all ten block tuples, and this session recomputed all ten — together
with all ten differences — to **0.0 absolute**.

---

## 6. Invalidation rules IV-1 … IV-7

**No IV rule fired in any of the three runs.** Each was checked independently rather than read
off the record.

**IV-1.** Five hash-bound files verified against the bound commits (§1). IN-1 carries exactly 49
cells; IN-2 reports `n_evaluable_on_measured_B = 49` and `n_eval_denominator = 49`; RC-C
de-duplication yields exactly 48; no declared tuple has an odd `C_red`. The **192 tolerance
tests** (four quantities × 48 tuples) were re-run here: recomputing λ, exp(−λ), T and P_pred from
IN-1's integer constants gives a maximum absolute difference against the quoted values of
**exactly 0.0** on all four — far inside the 1e-9 tolerance. The C-14 replicate schedule
reproduces IN-1's counts at all 48 tuples.

**IV-2.** §5. Zero collisions in every pool; IV-2d verified at all ten block tuples.

**IV-3 — KA-1 … KA-8, every case re-verified:**

| case | what was re-verified here | result |
|---|---|---|
| KA-1 | distinct = 3 in all 1000 replicates, zero tolerance | 0 off-target |
| KA-2 | distinct = 11 in all 1000 replicates, zero tolerance | 0 off-target |
| KA-3 | closed-form target recomputed to the identical double `7.2441711010797825`; half-band 4.000·sd/√1e6 = `0.00483243453461788` recomputed exactly | \|diff\| = 0.0022248989 — inside |
| KA-4 | half-band 4.000·√((3/11)(8/11)/1e6) = `0.001781447085660493` recomputed exactly; worst of the 11 bin deviations recomputed | 0.0007987273 — inside |
| KA-5 | exactly 3 distinct marked bins in all 1e6 pre-markings, on the KA-4 stream | 0 violations |
| KA-6 | implication distinct = 1 iff g = 0, zero tolerance; half-band 4.000·√((1/11)(10/11)/1e6) = `0.001149919149152138` recomputed exactly | 0 violations; deviation 0.0004080909 — inside |
| KA-7 | exact antipodal set equality {g, (11−g) mod 11} in all 1e6 replicates | 0 violations |
| KA-8 | P_pred recomputed from quoted N, C_red, \|S_(m−2)\| at the four INV-4-failing tuples | **0.0 absolute** at all four, against 1e-9 |

**IV-4.** No timeout, crash, resource exhaustion, budget cancellation or implementation failure
in any run; none is recorded as a result.

**IV-5.** 48/48 primary tuples, 10/10 block tuples in both legs, 8/8 known-answer cases;
`tuples_not_reached` empty everywhere.

**IV-6.** Verified by inspection of the committed blob: imports are `argparse, datetime,
hashlib, json, math, os, platform, resource, struct, subprocess, sys, time` and `numpy`, and
nothing else; nothing under `harness/`, `tools/` or `orchestration/` is imported or
executed; no curve operation of any kind is implemented; no efficiency E and no yield ratio R is
computed or reported anywhere; and the commit changed exactly the eleven declared paths, so no
twelfth file was written. See §7 for the PDC-1 and AMB-2 readings this depends on, and finding
F-3 in the report for two imprecise verdict sentences.

**IV-7.** All six required environment strings present in all three manifests, all three
`results.json` files and both PP-1 leg blocks, each flagged recorded before the first draw. One
numpy version (2.4.4) across the three arms; PP-1's legs record their own six strings and are
expressly outside the single-version scope.

---

## 7. PDC compliance, PDC-1's load-bearing role, and AMB-2

All **fifteen** condition texts are carried in `summary.json` **byte-identical** to the
TASK-20260729-034 receipt's `PRE_DISPATCH_CONDITIONS_VERBATIM` block (checked by string
comparison — zero mismatches), and each of the three `results.json` files carries a
fifteen-key `pre_dispatch_condition_compliance` record.

Conditions re-derived rather than accepted:

| condition | independent check | result |
|---|---|---|
| PDC-3 | re-applied the RC-21B rule to IN-1 | rank 4 = **T-16-2-B38** at λ 0.011000564; **T-18-2-B82** at 0.012846427 is rank 5 — PDC-3's correction is right; the six selected block tuples are confirmed set-identical to the contract's named six |
| PDC-10 | Student-t mixture, 37 df=99 + 11 df=29 | **15.4121 / 2.3892 / 0.1869** vs quoted 15.412 / 2.389 / 0.187; standard-normal **15.2309 / 2.1840 / 0.1296** vs quoted 15.231 / 2.184 / 0.130, and correctly labelled as not the stated null |
| PDC-11 | pools enumerated | 109 fields / 105 distinct; 98 / 98 — confirmed with the four repeats located |
| PDC-12 | √(37·(99/97) + 11·(29/27))/48 | **0.1466904890**; edges **0.9543904** and **1.7042686** — matches to every quoted digit |
| PDC-15 | exact expectation vs T, 60-digit decimal | **max 3.230158440695e-05 at T-12-2-B62** — see below |

**PDC-1 was load-bearing, and the record's claim is right.** IV-6 read literally invalidates a
run that "applies any threshold to any quantity of this contract", while IV-1 mandates 192
tolerance tests at 1e-9 and IV-3 mandates 4.000-σ tolerances at KA-3/KA-4/KA-6 and 1e-9 at KA-8.
Without PDC-1's scoping, a literal Executor stops under ST-3 **before the first draw**. The
driver honoured PDC-1's scoping rather than ignoring IV-6: it records the collision explicitly as
AMB-1, cites PDC-1 as the resolution, states in each run record that the tolerances applied are
required execution of IV-1 and IV-3, and applies **exactly** the five tolerances PDC-1 names
(IV-1's 1e-9, KA-8's 1e-9, and the 4.000-σ bands of KA-3, KA-4 and KA-6) — every one of which
this session recomputed. It did not silently disregard IV-6 and it did not invent a wider
carve-out.

**AMB-2 — ruled: the Executor's reading is correct.** The contract mandates the tail counts of
\|z_sem\| above 1, 2 and 3, and OM-6 mandates the negative-sign count; each is literally a
threshold on a quantity derived from OM-3 or OM-1, which PDC-1 does not name. The competing
reading is self-defeating — refusing to compute them breaches `tail_checks` and OM-6, computing
them fires IV-6, so no executor behaviour is compliant, and a construction on which the contract
cannot be executed at all is not a construction of it. IV-6 is a *scope-breach* rule whose
enumerated targets are all **outside** the contract's declared scope; the tail counts are inside
it, named and mandated by the contract, which expressly disclaims any test, firing or p-value on
them. PDC-1 supplies the governing principle even without the enumeration. And the procedural
handling was right: the Executor recorded the reading as its own and **flagged** it rather than
applying it silently.

**Blast radius, verified.** OM-5 is a mean, a sample standard deviation and a standard error over
the 48-entry z_sem vector; this validator recomputed all three from the raw rows **using no
comparison operator at all** and obtained the recorded doubles bit for bit. The tail counts and
n_neg are terminal leaves — no other quantity in any of the seven artifacts reads them. **The
data-dependence claim is confirmed.** One correction: the Executor's sentence understates the
*procedural* consequence — IV-6's own consequence clause is that **the run is invalid**, not that
the affected counts are struck. That branch does not arise given the ruling above, but no later
record should adopt the softer sentence.

**PDC-15 — ruled: quoted-figure imprecision, not a PDC violation.** Recomputing
(\|S_(m−2)\|/N)[(N−1)(1−2/N)^(C_red/2) + (1−1/N)^(C_red/2)] against T in 60-digit decimal
arithmetic at all ten block tuples gives a maximum of **3.230158440695e-05 at T-12-2-B62**
(the package reports 3.230158440703512e-05; the two agree to thirteen significant figures) —
marginally above the quoted "better than 3.2e-5". It is not a violation because \|E − T\| is
**DETERMINED** arithmetic on committed integer constants that no seed, draw, replicate count or
executor action can move; PDC-15's operative obligations on the run are the symmetric prohibition
and the requirement to state the formula, both discharged; and the figure is of exactly the same
species as PDC-3, PDC-4, PDC-5 and PDC-12, which this program corrects by supersession. Narrowing
N-3 states the correction.

---

## 8. Platform audit

| | three arms | committed EXP-YIELD-002 |
|---|---|---|
| python | **3.14.3** | 3.13.1 |
| numpy | **2.4.4** | 2.4.0 |
| OS | macOS-26.6-arm64-arm-64bit-Mach-O | *same* |
| machine | arm64 | *same* |
| processor | arm | *same* |

**Changed:** the interpreter build and the numpy version. **Unchanged:** the operating system,
the machine architecture and the host.

**Is the package's own language honest about what did *not* change? Yes, conspicuously.** All
three `results.json` files carry, as a positive sentence rather than an inferable silence,
"NO RECORD PRODUCED BY THIS BATCH MAY DESCRIBE THIS EXPERIMENT AS A FRESH-PLATFORM REPLICATION";
`summary.json` repeats it; the boundaries block states it; `what_this_package_does_not_do`
lists it; and the archive receipt ends its PP-1 block with "THIS IS NOT A FRESH-PLATFORM
REPLICATION". **The card's BLOCKING test — self-description as a fresh-platform replication
without a changed platform — is not triggered. The package asserts the opposite, everywhere.**

---

## 9. Artifact policy and resources

Every AGENTS.md artifact-policy item is present in all three manifests: exact command; git
commit `572ce080` with `dirty: true` and its two untracked entries enumerated; environment
and dependency versions; input parameters and seeds; requested policy
`executor-implementation`; backend; resolved runtime model id; model provenance;
`model_verified: false`; reasoning effort; `fallback_used: false`; empty
`degraded_requirements`; stdout and stderr locations; raw results location; validity status and
reason; timestamps; and resource measurements. A `certificate` block is present and correctly
declares `kind: none` for a pure measurement run.

| run | elapsed (s) | peak RSS (bytes) | terminal status |
|---|---|---|---|
| KNOWNANSWER | 17.859 | 65 814 528 | completed_valid |
| REPLICATE-REPAIRED | 3.545 | 50 741 248 | completed_valid |
| HIGHPREC | 4.885 | 49 594 368 | completed_valid |
| **total / max** | **26.289** | **65 814 528 (62.8 MiB)** | — |

Against ST-1's 600 s per run and 4 GB caps. Memory is reported beside time in every manifest.
ST-2 order confirmed from the recorded timestamps: KNOWNANSWER 15:17:13Z → REPLICATE-REPAIRED
15:17:40Z → HIGHPREC 15:18:04Z. All three `stdout.log` files are present and non-empty
(4458 / 9854 / 5294 bytes), with stderr tee'd in-process per DEV-1.

*(Trivial, prose only: the commit message says "peak RSS 61 MB"; 61 is the GiB-scaled 0.0613
read as MB. The measured peak is 62.8 MiB = 65.8 MB. The manifests are correct.)*

---

## 10. The three items handed up, and the deviation count

**(a) PDC-15's marginal exceedance** — §7. Ruled quoted-figure imprecision, corrected by N-3.

**(b) DEV-5/6/7 placement.** Confirmed: the KNOWNANSWER and HIGHPREC manifests list only DEV-1
and DEV-8. But the three are not alike. **DEV-6 and DEV-7 are arm-specific** (PP-1 and the
RC-33-M stream probe both belong to the REPLICATE-REPAIRED arm), so their absence from the other
two manifests is **correct, not a defect**. **DEV-5 is arm-general** — its own text says "THE
THREE ARMS" — so its labelled entry is genuinely missing from two manifests. Its *substance*
survives: all three environment blocks carry the realised strings and the quoted committed
reference environment side by side, so no reader of any single manifest is misled. Minor,
non-blocking; the receipt's grouping of all three overstates it.

**(c) The null auxiliary tolerance field.** Confirmed, with one correction: for **KA-4 and
KA-6** the `tolerance` key is **absent** (not present-with-null) in *both* `results.json` and
`summary.json`, while `half_band` and `admissible_interval` are **present and non-null for
both cases in both files**. The contract's IV-3 text says the admissible interval and the numeric
half-band are recorded per case in both files, and that NARROW-1's cosmetic omission "is repaired
here by requiring the field in both files". Read as "the tolerance field", the cosmetic half of
NARROW-1 is **not** discharged for those two cases; read as "the interval and half-band just
named", it is. The **substantive** half is discharged either way. The Executor's decision not to
edit the driver after its SHA-256 was already recorded in three manifests is **correct** — the
same call the BATCH-012 Executor made — because editing it would break a binding four artifacts
depend on.

**Deviation count.** The committed package declares **five** distinct deviation identifiers —
DEV-1, DEV-5, DEV-6, DEV-7, DEV-8 — each with a `what`, an `effect_size` and a
`conservative_reading`. The snapshot receipt records `count: 8`. **DEV-2 and DEV-3 appear
nowhere** in the EXP-YIELD-003 contract, the pre-execution review, or any of the eleven committed
artifacts; they are EXP-YIELD-002 identifiers. **DEV-4** appears only as the *name* of the
seed-string repair carried from EXP-YIELD-002, which the frozen contract repairs rather than
deviates from. Eight is the highest identifier used, not an enumerated set — the
cardinality-rather-than-identity failure PRED-ID EXTENDED exists to prevent, occurring here in the
archive receipt rather than the run package. Corrected by N-6.

Related (finding F-1): EXP-YIELD-002 used DEV-1…DEV-7. EXP-YIELD-003 reuses DEV-1 with the *same*
content and says so, but reuses **DEV-5, DEV-6 and DEV-7 with entirely different content**. Any
cross-experiment DEV reference in this lineage must name the experiment as well as the number
(N-7).

**DEV-8** is assessed as the only available honest handling: the contract forbids the driver from
importing *or executing* anything under `orchestration/` and IV-6 fires on invoking a forbidden
module, so `doctor --probe` could not run without invalidating the run. The consequence is
recorded rather than papered over — `model_verified: false`, `fallback_used: false`, empty
`degraded_requirements`, and the INT-BATCH013-D policy-binding mismatch disclosed in every
manifest's inference block. **No adapter result is claimed and none is fabricated.** The same
limitation applies to this validation report's own resolved model.

---

## 11. Controls before belief

The package's positive controls (KA-1…KA-8) and integrity controls (IV-1, IV-2) all pass and
were all re-verified here. **The control that is missing is the null-object control on the
reported signal itself:** RT-20260729-033 raised **RC-33-K** — draw the 48-tuple arm under K
independent master seeds with K of order 10 and report the between-seed scatter directly — as the
cheapest discriminating control, and **expressly raised it without imposing it**, because
adopting it would consume the single permitted RC-13 amendment cycle. The run therefore measures
the statistic at **K = 1** fresh master seed.

That is faithful execution of the frozen contract and **not** a defect in the run. It is a bound
on what any reader may take from the pair of measurements (N-11). Stating it is this validator's
job; disposing of the shift is not.

---

## 12. What this validation did not do

- It applied **no** resume condition and took **no** disposition of the difference between the
  two measurements. That belongs to TASK-20260729-038 and DEC-20260729-003.
- It changed no status and created no evidence, decision or knowledge record.
- It made **no commit** and wrote nothing outside
  `coordination/goals/GOAL-ECDLP-001/batches/BATCH-013/reviews/TASK-20260729-037`.
- It repaired no producer artifact.
- It did **not** independently reimplement the simulated process. Re-execution of the same driver
  blob is a determinism check, not an instrument-independence check; RC-F remains undischarged and
  untouched.
- It did not audit DEC-20260729-002 or EV-ECDLP-009 beyond the quantities the package quotes, and
  did not attempt to reconcile the duplicated identifier VAL-20260729-001.
- Nothing was reached outside the 3600 s cap that is not named here. No different operating system
  and no different machine architecture exist on this host, so no cross-platform check was
  possible.
