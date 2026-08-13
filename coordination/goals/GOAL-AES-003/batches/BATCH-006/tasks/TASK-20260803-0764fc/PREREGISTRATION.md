# PRE-REGISTRATION — TASK-20260803-0764fc (BATCH-006, GOAL-AES-003)

**Frozen at 2026-08-03T16:02Z, before any measuring run of this task.**
The FIPS-197 pin (`runs/pin_aes.json`) and the geometry dump (`runs/geom.json`)
were executed before this file was written; they are instrument verification,
not measurements, and their outputs are recorded below as they came out.

This file is not edited after the first measuring arm starts. Any change
appears as `PREREG-AMENDMENT-*.md` with its own UTC stamp.

Role: Executor. `claim_tier: toy`. `certificate.kind: none` — set explicitly;
both items are pure counting measurements, no solve, no relation, no key
recovery is claimed or attempted. No comparison to published cryptanalysis is
made in either direction (RQ-AES-003 R3). Nothing here speaks to full-round or
deployed AES.

## Inference block

| field | value |
|---|---|
| `policy` | `executor-implementation` |
| `requested_policy` | `executor-implementation` |
| `resolved_model` | `claude-opus-5` |
| `fallback_used` | `false` |
| `model_verified` | `false` — no `orchestration.adapter doctor --probe` was run; this harness has no adapter probe |
| `standing_basis` | `0137a051eb5828789eb267fa83c8278086578d4c` |

## Budget

Declared 6000 s wall clock, 8 GB, max 40 runs. Start `2026-08-03T15:53:30Z`
(epoch 1785772410). Binding stop `2026-08-03T17:33:30Z` (epoch 1785778410),
computed as start + 6000. Stamps in `budget_stamps.jsonl`. If the stop is
reached, RANK 1 (Section A) is the priority and any dropped Section B work is
named.

---

## 0. Instrument: reused, not rewritten

| artifact | sha256 | provenance |
|---|---|---|
| `yoyo_sbox_v2` (binary, executed) | `d30e4d720317706043b263742062273d22fbe054f56a58a8b351f3bbb3fd9ff0` | byte-identical copy of `BATCH-004/tasks/TASK-20260803-367b1b/yoyo_sbox_v2` |
| `yoyo_sbox_v2.c.readonly_copy` (read, NOT rebuilt) | `6bda2ab7f3c8e6dee358d3fcba52803e4e43f794f963bafabc51cc0de379bc9c` | same source directory |

Both hashes match the values recorded in
`BATCH-005/tasks/TASK-20260803-48a239/PREREGISTRATION.md` lines 28–29. The
binary is **not** rebuilt: a rebuild would introduce an uncontrolled factor
into measurements whose purpose is to vary exactly one thing.

**FIPS-197 C.1 pin, executed before any measurement** (`runs/pin_aes.json`,
exit 0):

- `fips197_c1_kat_encrypt_match: true`
- `fips197_c1_kat_decrypt_match: true`
- `fips197_c1_kat_ciphertext_computed: 69c4e0d86a7b0430d8cdb78070b4c55a`
  (the FIPS-197 C.1 expected value)
- `roundtrip_checks: 5120`, `roundtrip_failures: 0`, `pin_seed: 60600001`
- `pin_pass: true`

Geometry (`runs/geom.json`) reproduces the campaign convention exactly:
`PW = [[0,5,10,15],[4,9,14,3],[8,13,2,7],[12,1,6,11]]`,
`CW = [[0,13,10,7],[4,1,14,11],[8,5,2,15],[12,9,6,3]]`.

**If any arm's `sbox_bijective` is false the binary refuses to measure (exit 4)
and that arm is recorded as refused, not as a reading.**

---

## 1. THE ABSENCE CLAIM I WAS HANDED, CHECKED — AND IT IS TOO STRONG

My task card and the BATCH-006 dispatch queue both state that the instrument
"has only ever run at r ∈ {2, 5, 6, 10}" and that therefore "every yoyo claim
across five batches assumes a monotone round-profile measured on ONE SIDE of
its peak". `CORR-20260803-c92db5` requires me to search before repeating an
absence claim. I searched. **The narrow form is true and the broad form is
false.**

Search performed (exact commands in `RESULTS.json.repository_search`):

1. `grep -rl "W_ge1" coordination ledger knowledge docs experiments` — 68 files.
2. For every one of those files, every `"rounds": <n>` occurrence extracted by
   regex and tabulated.
3. `grep -rn '"rounds": *[34]\b' --include=*.json --include=*.yaml --include=*.md .`
   over the whole repository.

Result: **r = 3 and r = 4 yoyo arms already exist in this repository**, in two
W_ge1-bearing files that the BATCH-005 red team's enumeration did not surface:

- `coordination/goals/GOAL-AES-003/batches/BATCH-001/tasks/yoyo5/analysis.json`
- `coordination/goals/GOAL-AES-003/batches/BATCH-001/tasks/yoyo5/analysis_seed1.json`
  (the second is a plan skeleton with null counts)

`BATCH-001/tasks/yoyo5/analysis.json` records, at `amask=1, smask=1`, on the
AES-NI instrument `yoyo2.c` under the same reduced-round convention and pinned
to FIPS-197 by four independent implementations (`pin_receipt.json`,
1554 equality checks, `PASS: true`):

| r | trials | seed | W>=1 | PRP null | excess factor |
|---|---|---|---|---|---|
| 3 | 2^32 | 20260802 | 4294967296 | 4.0 | 1073741824.0 (saturated) |
| 4 | 2^32 | 20260802 | 4294967296 | 4.0 | 1073741824.0 (saturated) |
| 5 | 2^32 | 20260802 | 67 | 4.0 | 16.75 |
| 6 | 2^32 | 20260802 | 3 | 4.0 | 0.75 |
| 10 | 2^32 | 20260802 | 3 | 4.0 | 0.75 |
| 4 | 2^33 | 88881111 | 8589934592 | 8.0 | 1073741824.0 (saturated) |
| 5 | 2^33 | 88881111 | 126 | 8.0 | 15.75 |
| 6 | 2^33 | 88881111 | 10 | 8.0 | 1.25 |
| 10 | 2^33 | 88881111 | 13 | 8.0 | 1.63 |

So the low side of the round profile **was** measured, twice, under two seeds,
on 2026-08-02, and it read **fully saturated at r = 4 and r = 3**.

What survives of the claim, stated precisely:

- TRUE: the **`yoyo_sbox_v2` instrument** (the software T-table AES with a
  parameterized S-box, BATCH-004 onward) has only ever run at r ∈ {5, 6}, and
  its BATCH-002 AES-NI predecessor `probe.c` only at r ∈ {2, 5, 6, 10}.
  Neither has ever run at r = 3 or r = 4.
- TRUE: no r=4 arm has ever been **paired** to an r=5 arm on key and stream,
  and none has ever been run under a **non-AES S-box**.
- FALSE, as worded in the queue: that no r=4 measurement exists, and that the
  low side of the profile has never been measured. It has.
- The BATCH-001 probe was an explicitly **exploratory scratchpad** run with no
  ledger record (its own `PREREGISTRATION.md` §0 says so), which is a plausible
  reason it was not surfaced; that makes it weaker evidence, not absent
  evidence.

**This changes my prediction from blind to informed, and I say so here rather
than letting a confirmed prediction look like a lucky call.** The arm is still
worth running: it has never been run on this instrument, never paired, and
never under a drawn S-box, and a disagreement between the two instruments at
r=4 would itself be a finding.

---

## 2. RANK 1 — the r = 4 arm

### Arms (frozen)

`./yoyo_sbox_v2 arm <name> <sboxspec> <rounds> <amask> <smask> <log2N> <seed> <armid> <threads>`

| id | command tail | role |
|---|---|---|
| A0-REPRO-R5-K1 | `aes 5 1 1 30 531001 1 2` | reproduction control: must return **exactly** BATCH-005 `D-AES-K1`'s 14 hits and key `bdf3823182ad657dab3d556b3886ba72` |
| **A1-R4-MAIN** | `aes 4 1 1 31 431001 1 2` | **the falsifier.** Paired to BATCH-004 `Y-AES-main` (r=5) and `Y-AES-main-r6` (r=6): identical `sboxspec, amask, smask, log2N, seed, armid, threads`; **`rounds` is the only argument that differs.** |
| **A2-R4-K1** | `aes 4 1 1 30 531001 1 2` | second pairing, to BATCH-005 `D-AES-K1` (r=5, 2^30). This is the red team's RC-9 geometry. |
| A3-R3-MAIN | `aes 3 1 1 24 431001 1 2` | exploratory profile fill, small N because saturation is expected |
| A4-R2-MAIN | `aes 2 1 1 20 431001 1 2` | exploratory; r=2 saturation was seen in BATCH-002 `arm_PC` on a different instrument |
| A5-R4-R1-K1 | `rand:20260803001 4 1 1 30 531001 1 2` | exploratory: is r=4 behaviour S-box-specific? Never asked before. |

A1 and A2 are the preregistered rank-1 arms. A0 is a control. A3–A5 are
labelled exploratory in advance and no falsification rides on them.

### Why the pairing holds by construction, and how it will be verified

In `yoyo_sbox_v2.c` the key is `kst = seed ^ 0xA5A5A5A5A5A5A5A5` then two
`splitmix64` draws (lines 382–384), and thread seed `t` is
`seed ^ armid*0x1234567891 ^ (t+1)*0x9E3779B97F4A7C15` (line 393). **Neither
depends on `rounds`.** The plaintext pair stream in `worker()` is drawn from
the thread state before any encryption call, so it too is round-independent.

I will **not** assert this. I will print `key_hex` and `thread_seeds` from the
new r=4 arms and compare them field by field against the recorded r=5 and r=6
JSON, and report the comparison including any mismatch.

### PREDICTION, FROZEN BEFORE MEASURING

**P1 (primary, A1 and A2).** r=4 reads **saturated or near-saturated**:
`W_ge1_nontrivial / nontrivial_trials >= 0.5`, i.e. excess factor
`>= 5.4e8` against the analytic null of `nontrivial_trials * 2^-30`.
Point prediction: **exactly 1.0**, every trial a hit, matching BATCH-001's two
r=4 arms.

**P2.** r=3 (A3) also saturated, rate 1.0.

**P3.** A0-REPRO returns exactly `W_ge1_nontrivial = 14`,
`key_hex = bdf3823182ad657dab3d556b3886ba72`,
`thread_seeds = [11400714758317678269, 4354685486758533762]`.

### What reading falsifies what — decided before the number exists

The campaign's artifacts describe the profile as a **monotone decay in r with
a death round at r=6** (BATCH-004 PREREGISTRATION "r=6 decay arms"; BATCH-002
r=2 saturated, r=5 ~15x, r=6 and r=10 at null). The queue's phrase "peak at
r=5" is a different and **already-false** description: r=2 was saturated in
BATCH-002 and r=3/r=4 saturated in BATCH-001, so r=5 was never the peak of
anything. I therefore register both readings separately.

| outcome | excess factor at r=4 | verdict registered in advance |
|---|---|---|
| **F1 — NULL** | DEAD by the frozen rule: `X/v <= 2.5` | **MONOTONE PROFILE FALSIFIED.** The statistic would not be decaying with round count; the r=5 signal would be a probe-geometry artifact at one round count rather than a decay phenomenon, and the "death round at r=6" framing would be wrong. It would also contradict BATCH-001's two saturated r=4 arms, forcing an instrument disagreement to be reported. |
| **F2 — BELOW r=5** | ALIVE but strictly below the r=5 arm's exact 95% Poisson lower bound | **MONOTONE PROFILE FALSIFIED** (non-monotone in r). |
| **F3 — INDISTINGUISHABLE** | inside the r=5 arm's exact 95% Poisson interval | **PARTIAL FALSIFICATION.** A flat r=4/r=5 profile is inconsistent with decay from saturation at r=3, and would be reported as such, not softened. |
| **C1 — CONSISTENT** | above the r=5 95% upper bound but below saturation | consistent with monotone decay. Also refutes the "peak at r=5" wording. |
| **C2 — SATURATED** (P1) | `>= 5.4e8` | consistent with monotone decay and with BATCH-001. Refutes "peak at r=5" outright: the statistic is not peaked at r=5, it is monotone decreasing and r=5 is merely the last round count with a sub-saturated, above-null reading. |

**If F1, F2 or F3 occurs I will state it in the first line of `RESULTS.json`'s
headline field and in my report to the Coordinator, without softening, and
will name the yoyo claims across BATCH-001 through BATCH-005 that it
undercuts.** Under C1/C2 I will say plainly that the rank-1 falsifier did not
fire and that the "peak at r=5" wording — not the decay claim — is what dies.

**What no outcome here establishes:** anything about round counts other than
2,3,4,5,6,10; about S-boxes not drawn; about (a,s) masks other than those run;
or about full-round or deployed AES.

---

## 3. RANK 2 — RC-8, the 27 draws

### Arms (frozen)

| id | command tail |
|---|---|
| B0-AES-REF | `aes 5 1 1 30 631001 1 2` |
| B01 … B27 | `rand:20260803701` … `rand:20260803727`, then ` 5 1 1 30 631001 1 2` |

**Seed freshness.** The arm seed is **631001**, used nowhere in this campaign.
`grep -rn "631001"` over `coordination/`, `ledger/`, `knowledge/` returns
nothing outside this task (recorded in `RESULTS.json`). This matters because
`thread_seed` depends only on `(seed, armid, thread index)`: reusing 431001 or
531001 at 2^30 would replay an exact prefix of an existing trial stream, which
is the trap `BATCH-005/.../RESULTS.json` line 1605 records hitting. The S-box
seeds `20260803701–727` are likewise fresh; the only prior S-box seeds on this
instrument are `20260803001` and `20260803002`.

All 28 arms share the arm seed so that **the S-box is the only thing that
varies** across the draws. The cost of that choice, stated: the 27 draws are
evaluated under one key and one plaintext stream, so the bound below is a
statement about S-boxes at that key block, not marginalised over keys.

**Every drawn S-box is pinned before it is measured**
(`./yoyo_sbox_v2 pin rand:<seed> 60600002`): bijectivity, 512 random
key/plaintext vectors × 10 round counts of encrypt/decrypt round-trip. A draw
that fails its pin is recorded as `pin_failed` and excluded from the
denominator with that reason stated; it is not silently dropped. The full
256-entry table of every draw is dumped to `sboxes/`.

### ALIVE criterion — the campaign's existing rule, and its ambiguity

The campaign states this rule in two non-equivalent places, so I register both
and will report both counts rather than pick the flattering one:

- **T5-SIMPLE** (BATCH-005 PREREGISTRATION line 132): "excess factor >= 5x is
  ALIVE. At 2^30 the null is 1.0, so ALIVE means >= 5 hits."
- **T5-FULL** (BATCH-004 PREREGISTRATION, frozen decision rule): ALIVE iff
  `X/v >= 5` **and** `P(K >= X | lambda = v) < 1e-6`. At `v = 1.0` the Poisson
  condition alone requires `X >= 10` (`P(K>=9|1)=1.1e-6`,
  `P(K>=10|1)=1.1e-7`), so T5-FULL is `X >= 10` at 2^30.
  DEAD iff `X/v <= 2.5` and `P(K <= X | lambda = 15.63v) < 1e-3`; otherwise
  INDETERMINATE.

The headline ALIVE count is reported under **T5-FULL**, the stricter and
chronologically first of the two, with the T5-SIMPLE count beside it.

### Bound to be computed

One-sided 95% lower confidence bound on `p`, the fraction of bijective S-boxes
that preserve the signal at this round count, key block and exposure, by
Clopper–Pearson: with `k` alive of `n`, `p_lo` solves
`P(K >= k | n, p_lo) = 0.05`; for `k = n` this is `0.05^(1/n)`.

Registered in advance:

- 27/27 alive → `0.05^(1/27) = 0.8950` (n = 27, this task alone)
- pooled with the 2 prior draws on this instrument (`rand:20260803001`,
  `rand:20260803002`, ALIVE in BATCH-004 and BATCH-005) → n = 29,
  `0.05^(1/29) = 0.9014` — the ">= 0.90" figure the campaign named as the
  target.
- current figure being replaced: **0.224** = `0.05^(1/2)` from two draws
  (`CORR-20260803-791ca7`, `EV-AES-c66a80` OBS-B4-3).

Both figures will be stated side by side. **If any draw is not ALIVE that is
the more interesting outcome**: its S-box table, seed, raw counts and Poisson
tail are reported in full, the bound is recomputed by Clopper–Pearson for
`k < n`, and no independence reading is asserted.

### Prediction, frozen

**P4.** All 27 draws ALIVE under T5-SIMPLE; at least 24 of 27 ALIVE under
T5-FULL. Reasoning stated in advance: the five prior r=5 arms under drawn
S-boxes at 2^30 read 22, 15, and (BATCH-005 K2/K3 blocks) similar values, and
BATCH-004's 2^31 arms read 11.0x–20.5x. Under a common rate of ~15 per 2^30
the Poisson probability of a single arm falling below 10 is ~0.07, so ~2 of 27
below the T5-FULL threshold is the expected shortfall.

**P5.** B0-AES-REF ALIVE under both rules.

**What no outcome here establishes:** anything about S-boxes at other key
blocks, other round counts, other exposures, or about full-round or deployed
AES. 27 draws from 256! bijections bound a fraction, not a structure.

---

## 4. Stopping rules

- Hard halt at `2026-08-03T17:33:30Z` (epoch 1785778410). Any arm not started
  by then is dropped and named; any arm running at then is allowed to finish
  only if its own recorded start plus 400 s is inside the stop, otherwise it is
  killed and recorded as `killed_on_budget`, never as a reading.
- Section A runs first and alone (no concurrency) so its timings are clean.
- Section B runs at most 2 arms concurrently (2 threads each, `nproc = 4`).
  Concurrency does not affect any count: every arm is a deterministic function
  of its arguments.
- A timeout or kill is **resource exhaustion**, never negative evidence.
- Max 40 runs declared; planned run count is 6 (A) + 28 (B) + 28 pins + 2
  instrument checks. **Pins and instrument checks are verification, not
  measurement arms**; the "runs" counter is applied to the 34 measuring arms,
  and that reading of the limit is stated here in advance.
