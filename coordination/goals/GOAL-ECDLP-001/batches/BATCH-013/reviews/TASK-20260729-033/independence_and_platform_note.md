# TASK-20260729-033 — independence, re-derived arithmetic, seeds, DEV-4, platform

Companion to `contract_review.yaml` in the same directory. Verdict: **PASS with
fifteen numbered pre-dispatch conditions and no blocking objection.**

Everything numeric below was computed **in this session** from the committed
input files, using Python's standard library only, with the scripts written
outside the repository. Nothing was adjudicated by preferring one prior session's
statement over another. Where a re-derivation contradicts a committed figure, the
contradiction is reported as the finding.

---

## 0. Independence basis, stated rather than asserted

- **Session independence: TRUE.** Fresh subagent thread, no conversation lineage
  with TASK-20260729-031 and none with any BATCH-012 session, no access to the
  drafting of the contract under review.
- **Non-originating: TRUE.** This session authored no part of the contract, the
  feasibility table, the BATCH-013 queue, the BATCH-012 reviews, EV-ECDLP-009 or
  DEC-20260729-002.
- **Model independence: NOT AVAILABLE AND NOT CLAIMED** (INT-BATCH013-D).
  `requested_policy: review-adversarial`; `resolved_model_id: claude-opus-5`,
  self-reported by the runtime; `model_verified: false`; `fallback_used: false`.
  The adapter was not run, so no adapter result is claimed.
- **No commit was made. Nothing was written outside the write scope. No file
  under review was edited.** The three immutable `EXP-YIELD-002` files were read
  only.
- **Zero curve compute.** No curve object, point operation, factor base, sum set
  or census was constructed. All arithmetic is integer and float64 on already
  committed parameters.

### Snapshot verification, performed here

| check | result |
|---|---|
| commit | `de6fbb752f9f0b9ce28fda91b15a88593861dfcc` |
| first parent | `e1c75c724e05b1721efa407a101fb04ec14a5bba` — matches receipt |
| reachable from `HEAD` (`92827e89`) | YES, `git merge-base --is-ancestor` |
| changed paths | exactly 2, both `A`: the spec and the feasibility table |
| sha256 of the table blob | `1b9d2ddb002f05c54e18ed8e14d1200bc7836955aa4bf1fc72ad9284274b1de6` — matches receipt |
| sha256 of the spec blob | `fa4fa836f64c95a16f54e4b0c47da47587f63b9bf1e1933da11a730daf1fe68b` — matches receipt |
| working tree vs commit | identical; `git diff` empty, `git hash-object` reproduces `bc18aa43` and `133afa04` |
| YAML | `yaml.safe_load` succeeds; single top-level key `experiment` |

The receipt declares 3 paths and commits 2. **Not a discrepancy** — the third is
the receipt itself, committed in the child commit `92827e89`, and the receipt
discloses the gap in its own count fields.

**Not verified:** commit signature/provenance; the state of any non-ancestor
branch; `tools/allocate_id.py --check` for `EXP-YIELD-003`, which this session
did not run either, so the contract's declared `id_check` residual risk is
**carried undischarged** into this review.

---

## A. The declared set, the schedule, and the counts — re-derived

Source: `experiments/EXP-YIELD-001/runs/RUN-YIELD-001-NULL-RANDOM-SUMSET/results.json`
(IN-1), 49 cells.

| claim in the contract | re-derived here | verdict |
|---|---|---|
| 49 cells de-duplicate on measured `B` within `(k, m)` to 48 | 48 | CONFIRMED |
| exactly one duplicate, `(k=12, beta=.325, m=3)` and `(k=12, beta=.350, m=3)` | exactly one, label `T-12-3-B22` | CONFIRMED |
| merged tuple uses the first-listed occurrence, `round(beta*1000) = 325` | first-listed is `beta = 0.325` | CONFIRMED |
| 29 at `m = 2`, 19 at `m = 3` | 29 / 19 | CONFIRMED |
| C-14 gives 37 at `n = 100` and 11 at `n = 30` | 37 / 11 / 0 | CONFIRMED |
| the eleven `n = 30` members named in table §2.3 | identical set, verified member by member | CONFIRMED |
| the 10-replicate tier is unreachable; largest `C_red` is 91922 at `T-18-3-B82` | max `C_red` = 91922 at `T-18-3-B82` | CONFIRMED |
| all declared `C_red` are even | true at all 48 | CONFIRMED |
| quoted `lambda_C_red_over_N` equals `C_red/N` | max abs difference **0.0** over 48 | CONFIRMED |

The 11 members, re-derived independently: `T-16-2-B144`, `T-16-2-B192`,
`T-16-2-B246`, `T-18-2-B192`, `T-18-2-B264`, `T-18-2-B390`, `T-16-3-B48`,
`T-16-3-B58`, `T-18-3-B44`, `T-18-3-B58`, `T-18-3-B82`. `37 + 11 = 48`.

### A.1 The single-replicate sd, the SEM at the fixed replicate count

At the **four INV-4-failing tuples**, and at a sample of **five passing tuples
chosen by this session** — one per field size plus the two extreme-lambda block
members — from IN-1's committed antipodal arm:

| tuple | status | `n` | `s_001` (committed) | `s_001/sqrt(n)` re-derived | table `sem_001` | abs diff |
|---|---|---|---|---|---|---|
| T-18-3-B16 | INV-4 FAIL | 100 | 1.279362214842879 | 0.1279362215 | 0.127936 | < 5e-7 |
| T-16-3-B16 | INV-4 FAIL | 100 | 2.6408599762466416 | 0.2640859976 | 0.264086 | < 5e-7 |
| T-18-3-B24 | INV-4 FAIL | 100 | 4.132587909323022 | 0.4132587909 | 0.413259 | < 5e-7 |
| T-18-3-B28 | INV-4 FAIL | 100 | 7.245730195129133 | 0.7245730195 | 0.724573 | < 5e-7 |
| T-12-2-B62 | passing (largest lambda) | 100 | 18.76940073738115 | 1.8769400737 | 1.876940 | < 5e-7 |
| T-18-2-B34 | passing (smallest lambda) | 100 | 1.1090081108355294 | 0.1109008111 | 0.110901 | < 5e-7 |
| T-14-2-B118 | passing | 100 | 35.98097701662237 | 3.5980977017 | 3.598098 | < 5e-7 |
| T-16-2-B246 | passing | 30 | 88.51851549934 | **16.1611958986** | 16.161252 | **5.61e-5** |
| T-18-3-B82 | passing | 30 | 173.7918857145807 | **31.7299120391** | 31.725983 | **3.93e-3** |

**The `n = 100` rows are exact** (the column is `s_001/10`). **Every `n = 30` row
is wrong**, and the pattern is consistent with hand division by
`sqrt(30) = 5.477225575051661`.

### A.2 OI-4 ruling — all eleven 30-replicate rows re-derived

| tuple | table `sem_001` | authoritative `s_001/sqrt(30)` | abs diff |
|---|---|---|---|
| T-16-2-B144 | 6.300000 | 6.2998540395 | 1.460e-04 |
| T-16-2-B192 | 9.218262 | 9.2182165977 | 4.540e-05 |
| T-16-2-B246 | 16.161252 | 16.1611958986 | 5.610e-05 |
| T-18-2-B192 | 6.726234 | 6.7262737545 | 3.975e-05 |
| T-18-2-B264 | 9.264178 | 9.2641442031 | 3.380e-05 |
| T-18-2-B390 | 19.117723 | 19.1176444548 | 7.855e-05 |
| T-16-3-B48 | 13.135487 | 13.1355736464 | 8.665e-05 |
| T-16-3-B58 | 14.184641 | 14.1846066260 | 3.437e-05 |
| T-18-3-B44 | 4.108967 | 4.1089986288 | 3.163e-05 |
| T-18-3-B58 | 10.340921 | 10.3408963795 | 2.462e-05 |
| **T-18-3-B82** | **31.725983** | **31.7299120391** | **3.929e-03** |

**Ruling.** The authoring session's **materiality** reading is **RIGHT** —
nothing in EXP-YIELD-003 consumes the column, the committed machine record is
correct (`sem_001_DETERMINED` equals `s_001/sqrt(n_rep)` to **0.0** absolute at
all 48 rows of the committed `RUN-YIELD-002-NULL-REPAIRED`), and the artifact is
superseded rather than edited. Its **characterisation** is **WRONG**: six-decimal
rounding cannot move a value by more than 5e-7, so these are hand-arithmetic
errors, not "presentation-level rounding". And the **largest** error, 3.929e-3 at
`T-18-3-B82`, is 45× the largest of the three rows that were hand-checked, and
`T-18-3-B82` was not one of them. See objection OBJ-5 and condition PDC-5.

---

## B. The aggregate SEM and the branch probabilities — re-derived

### B.1 OI-2 — the standard error of the 48-tuple `z_sem` mean

`z_sem` is self-normalising, so under a centred null it is Student-t on
`n_rep - 1` df and its variance depends on `n_rep` alone:
`Var = (n-1)/(n-3)`, i.e. `99/97` at `n = 100` and `29/27` at `n = 30`.

```
37 * 99/97           = 37.7628865979
11 * 29/27           = 11.8148148148
sum                  = 49.5777014128
mean variance /48    =  1.0328687794
sqrt(...)            =  1.0163015194
/ sqrt(48)           =  0.1466904890      <-- SEM of the 48-tuple mean
```

- Contract/table state **0.146691**; the true value of their own chain is
  **0.1466905**. Last-digit slip; the working form "about 0.1467" is correct.
- Naive `1/sqrt(48) = 0.1443375673` — **CONFIRMED**; the t correction raises it
  by **1.630 %**, matching "about 1.6 per cent".
- Realised committed figure `0.9750016841736118/sqrt(48) = 0.1407293712` —
  **CONFIRMED**, matching the `0.140729` at EV-ECDLP-009 O-6.
- Committed first realisation re-derived from the 48 committed `z_sem` values:
  mean **0.36102368504276455**, sample sd **0.9750016841736118**, SEM
  **0.1407293712**, **t = 2.5653755**. All **CONFIRMED exactly**.
- `n_rep` distribution in the committed repaired arm: 37 at 100, 11 at 30 —
  **CONFIRMED**.

**Standardised resume edges:** `0.14/0.1466905 = 0.9543904` and
`0.25/0.1466905 = 1.7042686`. Contract states 0.954389 and 1.704194 (diff ≤ 8e-5)
and "about 0.95 / about 1.70" — correct where it matters.

### B.2 OI-3 — the pre-data branch probabilities

Model as stated: `M ~ Normal(mu, 0.1466905)`.

**Centred replication, `mu = 0`:**

| region | branch | table | re-derived |
|---|---|---|---|
| `-0.14 ≤ M ≤ +0.14` | chance and closed | 0.660 | **0.6601** |
| `+0.14 < M ≤ +0.25` | UNASSIGNED | 0.126 | **0.1258** |
| `M > +0.25` | driver / build / platform | 0.044 | **0.0442** |
| `M < -0.14` | UNASSIGNED | 0.170 | **0.1699** |
| **unassigned total** | | **about 0.296** | **0.2957** |

**Exactly reproducing shift, `mu = 0.361024`:**

| region | branch | table | re-derived |
|---|---|---|---|
| `-0.14 ≤ M ≤ +0.14` | chance and closed | 0.066 | **0.0656** |
| `+0.14 < M ≤ +0.25` | UNASSIGNED | 0.159 | **0.1586** |
| `M > +0.25` | driver / build / platform | 0.775 | **0.7754** |
| `M < -0.14` | UNASSIGNED | 0.000 | **0.00033** |
| **unassigned total** | | **about 0.159** | **0.1589** |

**Every figure in section 4 of the feasibility table is CONFIRMED.** The two
headline disclosures — **0.296** unassigned under a centred replication and
**0.159** under an exactly reproducing shift — are **correct to the precision
stated**. The contract's main honesty claim survives independent re-derivation.
Only the `M < -0.14` entry printed as "about 0.000" is a rounding of 3.3e-4.

**Caveat this session adds.** The model is Normal, but the aggregate is a mean of
48 Student-t variates; the normal approximation to the mean of 48 t-variates is
excellent, so this is a real approximation and an immaterial one. The declared
non-centrality from the second-order bias is ignored in the model, as the table
says; re-derived below, its aggregate contribution is +0.0264, so a
bias-centred model would shift every probability slightly. **The table's own
labelling of section 4 as an approximation covers this.**

### B.3 Other self-referential figures — all re-derived

| figure | claimed | re-derived | verdict |
|---|---|---|---|
| `2*Phi(-4)` | 6.33425e-5 | 6.334248e-5 | CONFIRMED |
| KA-4 chance alarm, `11 x` | 6.968e-4 | 6.9677e-4 | CONFIRMED (union bound; the 11 bins are dependent, so this is an upper bound) |
| IV-3 total | 8.235e-4 | 8.2345e-4 | CONFIRMED |
| KA-4 half-band `4*sqrt((3/11)(8/11)/1e6)` | 0.00178145 | 0.0017814471 | CONFIRMED |
| KA-6 half-band `4*sqrt((1/11)(10/11)/1e6)` | 0.00114993 | 0.0011499191 | CONFIRMED |
| KA-3 exact target `11-(8/11)[10(9/11)^4+(10/11)^4]` | (closed form) | 7.2441711011 | CONFIRMED, and the closed form agrees with `E = N-(1-s/N)[(N-1)A+C]` |
| seed pairs `73*72/2`, `73*105`, total | 2628, 7665, 10293 | identical | CONFIRMED |
| chance collision `10293/2^64` | about 5.6e-16 | 5.5798e-16 | CONFIRMED |
| max declared bias in bins | at most 0.131 | **0.130512** at `T-16-3-B58` | CONFIRMED |
| bias / sem interval and mean | [0.00468, 0.07542], mean 0.02638 | **[0.00468 (T-18-2-B390), 0.07542 (T-12-3-B16)], mean 0.02638** | CONFIRMED EXACTLY (using the measured `sem_rep`) |
| primary arm byte-clears | about 4.0e8 | 4.025e8 | CONFIRMED |
| block, four `m = 3` tuples | committed 1.70e10 | 1.702e10 | CONFIRMED |
| block, six `m = 2` tuples | about 1.74e10 | 1.743e10 | CONFIRMED |
| block total | about 3.44e10 | 3.444e10 | CONFIRMED |
| total random draws | below 5.2e8 | 5.092e8 | CONFIRMED |
| DEFER-BATCH013-001 cost multiple | "twenty-four times" | **12× on tuple-legs, 6.29× on byte-clears** | **CONTRADICTED — see OBJ-4** |

The byte-clear ratio implies a total of order twice EXP-YIELD-002's measured
15.0 s, i.e. **of order 30 s against a 600 s per-run cap**, and the worst single
run (HIGHPREC, 3.44e10) is of order 29 s. **The budget is feasible with two
orders of margin.** Peak memory is one boolean array of length ≤ 261707 plus the
parsed inputs — far below the 4 GB cap.

---

## C. OI-1 and the seeds — derived independently

### C.1 The derivation convention, verified against the committed record

The contract's rule — low 64 bits, unsigned **little-endian**, of the SHA-256 of
the ASCII string joined by `|` in the order master seed, arm label, `k`,
`round(beta*1000)`, `m`, `B`, `C_red` — was **validated against committed data**
before being used, by re-deriving four committed EXP-YIELD-002 high-precision
seeds:

| seed string (committed) | committed seed | little-endian | big-endian |
|---|---|---|---|
| `120501\|HIGHPREC\|18\|200\|3\|16\|688` | 7698028898728741792 | **MATCH** | no |
| `120501\|HIGHPREC\|16\|225\|3\|16\|688` | 2489506930073106857 | **MATCH** | no |
| `120501\|HIGHPREC\|18\|225\|3\|24\|2312` | 8052555953165255232 | **MATCH** | no |
| `120501\|HIGHPREC\|18\|250\|3\|28\|3668` | 3048116416646993061 | **MATCH** | no |

The rule as written in EXP-YIELD-003 reproduces the committed convention exactly.

### C.2 The 73 seeds of EXP-YIELD-003, derived here

- 48 tuples under `130301|REPLICATE-REPAIRED|…`
- 10 block tuples × 2 labels under `130501|HIGHPREC-REPAIRED|…` and
  `130501|HIGHPREC-ASRECORDED|…` = 20
- 5 seeded known-answer cases under `130401|KNOWNANSWER|<case>|N|s|C_red`
  (KA-1, KA-2, KA-3, KA-4, KA-6; KA-5 and KA-7 reuse streams, KA-8 is DETERMINED)

`48 + 20 + 5 = 73`. **CONFIRMED.**

| check | result |
|---|---|
| distinct seed **strings** among the 73 | 73 — no repeat |
| distinct 64-bit **integers** among the 73 | 73 — **IV-2a would not fire** |
| KA-1 vs KA-4, which share `(N, s, C_red) = (11, 3, 0)` | distinct, keyed on the case label, exactly as the contract says |
| merged tuple `T-12-3-B22` seed field `round(beta*1000)` | 325, the first-listed occurrence |

### C.3 Disjointness, checked rather than assumed

| pool | size | collisions with the 73 |
|---|---|---|
| committed EXP-YIELD-002 derived seeds (3 run `results.json`) | **105 distinct** (109 seed fields; see below) | **0** — IV-2b would not fire |
| derived seeds recorded in IN-1 | **98 distinct** (49 antipodal + 49 independent-throw contrast) | **0** — IV-2c would not fire |

**Master seed blocks, verified from the run records themselves, not quoted:**

- EXP-YIELD-002 master seeds actually used: `120201` (repaired arm), `120301`
  (as-recorded), `120401` (known-answer), `120501` (high-precision block) —
  **four**, exactly as declared.
- BATCH-011 master seeds actually used, read from the six
  `experiments/EXP-YIELD-001/runs/*/results.json`: `110201`, `110301`, `110401`,
  `110501`, `110601`, `110701` — **six**, all inside the declared block
  `110200`–`110799`.
- EXP-YIELD-003: `130301`, `130401`, `130501` — pairwise distinct, disjoint from
  both blocks. **CONFIRMED.**
- DEC-20260729-002 NA-1 required disjointness from `120201`, `120501` and the
  `110xxx` block; the contract declares disjointness from **all four** EY-002
  master seeds. That is a **superset** of what NA-1 required.

**The contract's own honesty about this is correct and worth endorsing.**
Master-seed disjointness is a **design fact and not a proof** about derived
seeds, because the derivation is a SHA-256 digest whose outputs are not
predictable from the master seed. The real work is done by IV-2, and IV-2 does
what it claims: this session re-ran IV-2a, IV-2b and IV-2c against the same pools
the driver will use, and all three are clean.

**The disclosed scope limit is real and is correctly disclosed.** IV-2b and IV-2c
cover only files this contract hash-binds; they do **not** cover the BATCH-011
run records other than IN-1. This session did not enumerate those either, so the
residual **stands undischarged** and is not closed by this review. It is small —
a 64-bit collision has probability of order 1e-15 across the whole pool — and it
is disclosed rather than claimed away, which is the right treatment.

**Two count corrections (OBJ-11, OBJ-12):**

- The three EXP-YIELD-002 files record **109 seed fields**, of which **105 are
  distinct**. The four repeats are the four INV-4-failing tuples printed twice
  inside `RUN-YIELD-002-NULL-REPAIRED` — once under `rows` and once under
  `INV_4_failing_tuples_reported_separately`. They are **not** the four DEV-4
  shared high-precision seeds, which a reader might assume.
- IN-1 records **98** derived seeds, not just the antipodal arm's 49. IV-2c's own
  rule text (`any derived seed recorded in IN-1`) is correct and broader than the
  scope sentence that describes it.

---

## D. The DEV-4 repair, checked mechanically

### D.1 Does the repair actually give the two legs different streams?

Derived here at **all ten** block tuples, both labels:

| block tuple | `HIGHPREC-REPAIRED` string | `HIGHPREC-ASRECORDED` string | same seed? |
|---|---|---|---|
| T-18-3-B16 | `130501\|HIGHPREC-REPAIRED\|18\|200\|3\|16\|688` | `130501\|HIGHPREC-ASRECORDED\|18\|200\|3\|16\|688` | **NO** |
| T-16-3-B16 | … `\|16\|225\|3\|16\|688` | … `\|16\|225\|3\|16\|688` | **NO** |
| T-18-3-B24 | … `\|18\|225\|3\|24\|2312` | … `\|18\|225\|3\|24\|2312` | **NO** |
| T-18-3-B28 | … `\|18\|250\|3\|28\|3668` | … `\|18\|250\|3\|28\|3668` | **NO** |
| T-18-2-B34, T-18-2-B44, T-18-2-B58, T-14-2-B118, T-16-2-B246, T-12-2-B62 | (six m = 2 members) | (six m = 2 members) | **NO** at all six |

**Zero of the ten tuples produce a shared seed string or a shared 64-bit seed.
The repair is REAL, not nominal.** The label set is closed at exactly four
strings and the closure is what makes the coverage checkable rather than trusted
— which is the correct structural reading of what DEV-4 was.

### D.2 Would IV-2d have fired with certainty at all four EXP-YIELD-002 block tuples?

**YES. VERIFIED FROM THE COMMITTED ARTIFACT, NOT ASSERTED.**
`experiments/EXP-YIELD-002/runs/RUN-YIELD-002-NULL-REPAIRED/results.json`,
`repaired_arm.high_precision_diagnostic_block.rows`, records **one**
`seed_string` per tuple, shared by both legs:

```
T-18-3-B16   "120501|HIGHPREC|18|200|3|16|688"   derived 7698028898728741792
T-16-3-B16   "120501|HIGHPREC|16|225|3|16|688"   derived 2489506930073106857
T-18-3-B24   "120501|HIGHPREC|18|225|3|24|2312"  derived 8052555953165255232
T-18-3-B28   "120501|HIGHPREC|18|250|3|28|3668"  derived 3048116416646993061
```

Each row even carries its own `seed_note` declaring the defect. IV-2d fires when
"the two high-precision legs at any block tuple produce the same seed string";
here they produce the *same single* seed string at all four. **"Can fire" is a
demonstration and not an assertion — confirmed.**

The prohibition on the committed difference column is correspondingly right and
should stay: its two legs share a per-tuple seed, so its measured differences are
common-random-number estimates with offset rather than independent streams, and
its error bar is quantified nowhere.

---

## E. OI-1 — the RC-21B selection, re-applied

The rule as frozen: order the 29 declared `m = 2` tuples by
`lambda = C_red/N` **ascending**; take the **three smallest** and the **three
largest**; ties by first appearance in IN-1's `cells` array.

Re-applied to IN-1 in this session (`lambda` re-derived as `C_red/N` and
cross-checked against the quoted `lambda_C_red_over_N`, max abs difference
**0.0**):

| rank | tuple | lambda | | rank | tuple | lambda |
|---|---|---|---|---|---|---|
| 1 | **T-18-2-B34** | 0.00220858 | | 29 | **T-12-2-B62** | 0.48037991 |
| 2 | **T-18-2-B44** | 0.00369879 | | 28 | **T-16-2-B246** | 0.46101809 |
| 3 | **T-18-2-B58** | 0.00642703 | | 27 | **T-14-2-B118** | 0.41891811 |
| 4 | T-16-2-B38 | 0.01100056 | | 26 | T-12-2-B54 | 0.36440890 |
| 5 | T-18-2-B82 | 0.01284643 | | 25 | T-18-2-B390 | 0.29059215 |

**All six named tuples are CONFIRMED.** The 29 lambda values are pairwise
distinct as quoted to eight decimals, so no tie arises, exactly as stated. The
block is 10 tuples in 2 legs = 20 seeded streams — confirmed.

**One contradiction found (OBJ-3, PDC-3).** Table §6 states, "The nearest
non-selected neighbours, recorded so the boundary is checkable: `T-18-2-B82` at
`0.01284643` from below." **`T-18-2-B82` is rank 5.** The nearest non-selected
neighbour from below is **`T-16-2-B38` at `0.01100056`**, rank 4. The neighbour
from above, `T-12-2-B54` at `0.36440890`, is rank 26 and is **correct**.

This is the **fourth cardinality-not-identity instance** the contract's OI-7 asks
the reviewer to hunt for: an ordinal position read for a member identity, in the
one sentence written so that a boundary could be checked. It changes **nothing** —
the rule governs, the six names are right, and the rank-3-to-rank-4 gap
(0.00642703 → 0.01100056) is wide, so the boundary is robust either way.

---

## F. The platform clause, read adversarially

### F.1 Can it be satisfied by silence? **NO.**

Three independent mechanisms force positive disclosure:

1. **BND-3** states the prohibition as a positive sentence inside the contract's
   own `boundaries` block, not in a note: "NO RECORD MAY DESCRIBE THIS AS A
   FRESH-PLATFORM REPLICATION, BECAUSE THE PLATFORM DOES NOT CHANGE."
2. **ST-4** independently forbids the run package from describing the replication
   as a fresh-platform replication.
3. **IV-7 fires on a MISSING environment string**, so an omitted disclosure is an
   invalidation and not a silence; and
   `the_platform_cannot_vary_and_this_is_stated_plainly` requires the Executor to
   state the unavailability *in every manifest and in results.json* "rather than
   leaving it to be inferred from an absent field."

A clause whose omission fires an invalidation rule is not satisfiable by silence.
**The narrowing is honest and sufficient.**

### F.2 Is the SUP-E narrowing honest?

**YES.** It names the superseded text in *both* DEC-20260729-002 NA-1 and
RT-20260729-021 RC-21A, quotes it, states the corrected statement, and states the
cost plainly: "the narrowed experiment separates chance from a seed-independent
deterministic property of the driver-build-platform combination and separates
none of those three from each other, **which is strictly less than NA-1 asked
for**." It then refers the worth-running judgement to the Coordinator's G-5 scope
ruling rather than making it for itself. No superseded artifact is edited. That
is the program's correction mechanism used correctly — **the word is narrowed by
supersession, not quietly dropped.**

### F.3 Is PP-1's three-case pre-statement sound?

**Case one is right in its core claim.** If the second build carries the same
numpy version, the Generator stream is fixed by the numpy version and the seed
and **not** by the CPython build, so PP-1 produces the same numbers and **cannot
separate a driver property from a build property**. That is correct and is the
subtle part the contract gets right.

**Two qualifications:**

1. **"By construction" is one shade too strong.** It holds exactly for the random
   stream. For the float64 reductions that turn the stream into a mean and an sd
   it holds because the same numpy *version* built for a different CPython — a
   *different binary* — behaves identically on one CPU with runtime SIMD
   dispatch. That is an empirical property of two wheels, not a construction. The
   distinction is the difference between a tautology and a test.
2. **The taxonomy is not exhaustive (OBJ-8, PDC-8).** It splits on numpy *version
   equality*. The missing case is **different version, identical stream**:
   numpy's `Generator` stream is not guaranteed stable across feature releases
   but is in practice stable across patch releases, so a 2.4.0 → 2.4.4 move will
   very likely produce an identical PCG64 stream and therefore identical numbers.
   A reader applying the stated taxonomy would then classify a genuinely null
   result as case two, "confounds build with stream", when in fact nothing
   varied — or, worse, would read bit-identity across two numpy versions as a
   cross-version portability result, which BND-4 forbids.

### F.4 Host observation — **UNARCHIVED PROBE, NOT EVIDENCE**

Run **outside the repository**, on the executing host, purely to bound which
PP-1 case is reachable. **It is not archived, it is not evidence, and no
conclusion in this review rests on it.** It is recorded because a design decision
depends on which cases are live.

```
python3.11  ->  3.11.14   numpy ABSENT
python3.13  ->  3.13.1    numpy 2.4.0        (this IS the primary build)
python3.14  ->  3.14.3    numpy 2.4.4
default python3 -> 3.13.1 numpy 2.4.0
```

If that state holds at execution time:

- **PP-1 case one is unreachable** without installing numpy 2.4.0 into another
  interpreter. So the one case that could test "the interpreter build does not
  change the arithmetic" is the one PP-1 will not get.
- **3.11 is unusable** (no numpy) → would be recorded NOT OBTAINED for that build.
- **3.14.3 + numpy 2.4.4** is the only usable second build, and it lands in the
  *fourth*, unenumerated case if the PCG64 stream is stable across the patch bump.

This makes the missing case the **likely** case, not a corner case, which is why
PDC-8 requires classification on **stream equality** rather than on version
equality. IV-7's existing carve-out already anticipates a numpy difference
between the three arms and PP-1, so the contract remains **executable** either
way.

### F.5 What the replication can and cannot establish — endorsed without further narrowing

BND-1 and BND-2 are exactly right and this session does not narrow them further:
with a fresh master seed on the same driver, the same build and the same
platform, this replication **separates CHANCE from a SEED-INDEPENDENT
DETERMINISTIC PROPERTY of the driver-build-platform combination, separates NONE
of those three from each other, and never separates any of them from the
PROCESS.** A reproduction would be evidence about **this instrument** and never
about the balls-in-bins process, never about `P_pred`, and never about
decomposition yield.

---

## G. The smuggled-criterion hunt — result stated both ways

**No success or falsification criterion is smuggled onto the primary quantity.**
Four surfaces exist on which a realised value could nevertheless be reported as a
pass or a failure of something, and all four are fenced by condition rather than
by removal:

| id | surface | why it is a surface | closed by |
|---|---|---|---|
| SC-1 | the resume condition itself | it *is* a pre-registered three-way disposition rule on the primary observation; the contract's defence — it disposes of an instrument note, not a hypothesis — holds, but the contract must never be described as threshold-free | PDC-6, PDC-14 |
| SC-2 | `mean(delta_z)` of OM-7 | identically `mean(z_new) − 0.36102368504276455`, so the resume disposition can be taken through a differently named quantity | PDC-7 |
| SC-3 | tail-check counts above 1, 2, 3 beside expectations | counts-beside-expectations is a chi-square-shaped surface even with no test performed — **and the stated reference distribution is the wrong one** | PDC-10 |
| SC-4 | the high-precision difference column against `T` | re-derived: the exact expectation of the repaired-minus-as-recorded difference is `(s/N)[(N−1)(1−2/N)^(C_red/2) + (1−1/N)^(C_red/2)]`, which agrees with `T = |S_(m−2)|e^{−λ}` to better than **3.2e-5** at all ten block tuples — so the column is a clean unbiased estimator of `T` and agreement is *arithmetic, not evidence* | PDC-15 |

### G.1 The tail-check reference distribution, quantified (OBJ-10)

Feasibility table §3.1 states, correctly, that `z_sem` is Student-t on
`n_rep − 1` df. The tail check nonetheless compares realised counts against
**standard-normal** expectations for 48 draws:

| threshold | expected count, N(0,1) | expected count, the stated t-mixture (37 @ 99 df, 11 @ 29 df) | understatement |
|---|---|---|---|
| `|z| > 1` | 15.231 | 15.412 | 1.2 % |
| `|z| > 2` | 2.184 | 2.389 | 9.4 % |
| `|z| > 3` | 0.130 | 0.187 | **44 %** |

A reader comparing realised counts against the standard-normal figures will see
an apparent tail excess that is an artefact of the wrong reference.

---

## H. RT21-1 compliance, and the PRED-ID extension put to the test

**The C-20 power sentence is not reproduced, in whole or in paraphrase.** Checked
by search across both artifacts: the contract states instead that it "HAS NO
CRITERION, THEREFORE IT HAS NO POWER AGAINST ANY ALTERNATIVE", which is the
correct statement for a contract with no criterion, and the correction is cited
where the sentence is referenced.

**The structural diagnosis is right.** C-20's mechanism — widening a
self-critical sentence into an obligation binding every later record — is
correctly identified as the propagation channel: a mandated sentence *copies*,
and a copy cannot be corrected in the carrying, so a false one reaches immutable
artifacts uncorrected. A **rule** re-derives at each use. **Removing the
mechanism loses nothing the mechanism was for**, because the function C-20
served — limits travel with the claim — is preserved by PRED-ID EXTENDED without
the copy hazard.

**But the claim that no mandatory-sentence clause is created is FALSE (OBJ-2).**
`the_constrained_sentence_binding_every_record_this_contract_produces` mandates a
substantive sentence on the driver, the three run records, the results summary,
EV-ECDLP-010 and DEC-20260729-003. Its prohibition half is sound — this session
re-derived that the exact process mean exceeds `P_pred` at **all 48** tuples,
maximum excess 0.130512 bins at `T-16-3-B58`. Its **assertion** half carries an
empirical claim derived from EXP-YIELD-002's data ("by an amount larger than the
declared second-order biases account for … unexplained") and is bound onto
records that will describe **EXP-YIELD-003's** data, which may not support it.
**That is C-20 one iteration later**, and PDC-2 scopes it.

**Does the PRED-ID extension bind? Partially.** Its operative sentence binds
"EVERY STATEMENT THAT REPORTS A COUNT OF **TUPLES**", while its declared scope
one sentence earlier is "EVERY POWER, SENSITIVITY, **COUNT** AND MAGNITUDE
STATEMENT". Tested:

- **Every count of tuples complies and is correct**: 48, 29, 19, 37, 11, four,
  six, ten, 49 — all say they are counts, all name their members or the exact
  table section, and all were re-derived correct here.
- **Counts that are not of tuples escape it**: `105` derived seeds names no
  members anywhere and is ambiguous between 109 occurrences and 105 distinct
  values (OBJ-11).
- **And four further instances of the same genus were found anyway**: OBJ-3 (rank
  read for identity), OBJ-4 (tuple-legs counted as tuples), OBJ-10 (counts
  compared against the wrong population's expectation), OBJ-11.

The honest summary: **the rule is a real improvement over a sentence, and it did
not prevent recurrence in the contract's own companion table.** That is the
strongest available argument both for keeping the rule and for widening it
(PDC-11).

---

## I. The single most likely way this still goes wrong in execution

**An ST-3 stop before the first draw, on the IV-6 / IV-3 collision (OBJ-1,
PDC-1).** IV-6 invalidates the run if the driver "applies any threshold to any
quantity of this contract", while IV-1 mandates 192 tolerance tests at 1e-9 and
IV-3 mandates 4.000-sigma tolerance tests at KA-3, KA-4 and KA-6. Read literally,
a *correct* run fires IV-6. This lineage's Executor is demonstrably literal —
that is exactly how DEV-4 was found and declared rather than patched — and ST-3
obliges a stop when the contract "cannot be executed as written". Two rules that
invalidate each other is that case. Under RULE-BATCH013-SCOPE a stop costs the
batch. **Recording PDC-1 verbatim in the TASK-20260729-034 receipt, before
TASK-20260729-035 is dispatched, is what prevents it.**

Runner-up: **PP-1 landing in the unenumerated fourth case** (different numpy
version, identical stream) and being written up as either a confounded case-two
result or, worse, as cross-version portability — which BND-4 forbids. PDC-8
prevents it.

---

## J. Scope limits this review does not cross

- **This is not a cryptanalytic result.** Nothing here, and nothing
  EXP-YIELD-003 can produce, is an attack, an attack improvement, an exponent
  result, a closure or an impossibility claim. Claim tier is capped at **toy**.
- **No direction is declared impossible.** RC-B, RC-F, DEFER-BATCH009-001,
  DEFER-BATCH012-001 and DEFER-BATCH013-001 remain open, unretracted and
  undischarged; absence of evidence is not impossibility.
- **RC-7 matched baseline: DECLARED INAPPLICABLE — concurred.** EXP-YIELD-003
  solves no instance, recovers no discrete logarithm, computes no relation and
  touches no curve. There is no algorithmic task against which Pollard rho, BSGS
  or any specialized baseline could be matched, and quoting one would be
  decoration. The BATCH-011 cost position at EV-ECDLP-008 O-11 stands unretracted
  and is **not** restated as a result of BATCH-013.
- **The relevant "baseline" for this design is statistical, not algorithmic**, and
  it is named as required control **RC-33-K**: `K` independent master seeds
  instead of one, at ~1.2 % of the block's cost per extra draw. That control is
  **raised, not imposed** — adopting it consumes the single RC-13 amendment
  cycle, and any cycle-cap ruling on it must go to a session that did **not**
  author it, which is not this one.
- **`confirmatory_status: exploratory_only` is correct** on both stated grounds,
  and the contract's own separation of pre-registration *order* from confirmatory
  *standing* is correct and is not conflated anywhere.
