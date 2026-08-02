# GATE-601-B run record — TASK-20260731-703

**Goal** GOAL-AES-001 · **Batch** BATCH-002 · **Role** executor · **Gate** GATE-601-B ·
**Candidate** CAND-601-B · **Date** 2026-08-01 (UTC)

Machine-readable companion: `gate_601b_results.json`.
Implementation: `gate_601b_impl.c`.

---

## 0. Scope, and what this record does not contain

These measurements concern a **small-scale, AES-shaped cipher** with n-bit cells
(n = 3, 4, 5) and a 4×4 cell state, defined in full in `gate_601b_impl.c`. **It is not
AES.** Nothing measured or written here is a statement about AES at any round count,
about full-round AES, or about the security of any system that uses AES.

Per `DEC-20260731-011`, disposition `CAND_601_B`, CAND-601-B's `sota_delta` and **every**
comparison against a recalled baseline are **struck**. Accordingly this record contains no
literature comparison, no recalled baseline, no bit-margin, no `sota_delta`, no
extrapolation to any cell width other than the three actually run, and no crossover
prediction — not as a result, an aside, a footnote, a motivation, or a "for context"
remark. The original GATE-601-B PASS/FAIL escalation criterion is **withdrawn** by the
dispatching handoff, because its escalation leg depended on a struck extrapolation; it is
not applied and not restated.

**The only baseline is the one implemented in this task.** Yield 3 compares two
implementations both written here and both actually run on the same inputs. That is the
whole comparison.

This record reports observations. It assigns no evidence strength, advances no hypothesis,
declares no heuristic validated or refuted, and changes no official state.

---

## 1. Inference block

| field | value |
|---|---|
| `policy` | `executor-implementation` |
| `requested_policy` | `executor-implementation` |
| `resolved_model_id` | `claude-opus-5` |
| `resolved_model_name` | Opus 5 |
| `fallback_used` | **true** |
| `fallback_reason` | Structural and expected under this harness: `.claude/agents/` frontmatter supports only Claude models and all subagents run `model: inherit`, so the `executor-implementation` alias cannot be resolved by `orchestration/model-bindings.yaml` here. The model actually serving this session is recorded rather than the policy's nominal backend. |
| `reasoning_effort` | null (policy default) |
| `degraded_allowed` | false |
| `degraded_requirements` | none |
| `independent_session_required` | false |
| `model_verified` | **false** — `python3 -m orchestration.adapter doctor --probe` was **not** run in this task, so the resolved identifier is unverified configuration in the sense of AGENTS.md. |
| `standing_basis` | inference-amendment commit `0137a051eb5828789eb267fa83c8278086578d4c` |

---

## 2. Environment, revision, and dirty-tree state

```
git commit   98ae8539c9cbb8c3a261ceab83536069c9947253
git branch   claude/aes-campaign-harness-0o9p7y
git dirty    YES — exactly one untracked path:
             ?? coordination/goals/GOAL-AES-001/batches/BATCH-002/tasks/
             (this task's own declared write scope; no tracked file was modified)

gcc          gcc (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0
python3      Python 3.11.15
pycryptodome 3.23.0        (version queried only; not used by this gate)
openssl      OpenSSL 3.0.13 30 Jan 2024   (version queried only; not used by this gate)
kernel       Linux 6.18.5 x86_64 GNU/Linux
cpu          Intel(R) Xeon(R) Processor @ 2.10GHz, 4 cores
memory       16461176 kiB total
sage         not available (not required)
GPU          not available (not required)
```

The gate is a single self-contained C program. It links nothing beyond libc, reads no
file, consumes no external entropy, and is single-threaded.

`gate_601b_impl.c` SHA-256:

```
dc2bc3fe02a08881a048eccfe48c64ebe2c5a35a6a9884b1fc33f0cf4b4789f3
```

(Recomputed and recorded again inside `gate_601b_results.json` →
`artifacts.implementation_sha256`. Verify with
`sha256sum coordination/goals/GOAL-AES-001/batches/BATCH-002/tasks/TASK-20260731-703/gate_601b_impl.c`.)

---

## 3. Exact commands and real output

`$SCRATCH` =
`/tmp/claude-0/-home-user-crypto-autoresearcher/42d1537b-7158-5124-bdad-0c8e3df17d46/scratchpad`
`$TASKDIR` =
`/home/user/crypto-autoresearcher/coordination/goals/GOAL-AES-001/batches/BATCH-002/tasks/TASK-20260731-703`

The compiled binary and the intermediate stdout/stderr live in `$SCRATCH` because the
declared write scope of this task is `$TASKDIR` and the three declared artifacts are the
only files written there.

### RUN-703-BUILD-001 — build

```
gcc -O2 -std=c11 -Wall -Wextra -o $SCRATCH/gate_601b $TASKDIR/gate_601b_impl.c
```

Exit status `0`. stderr: **0 bytes** — compiles clean under `-Wall -Wextra`.
Binary SHA-256 `867c1d4b11b7f7e86ea6751e91120c13e6c39d39280c9c9dea994443b134213e`
(gcc output is not guaranteed byte-reproducible across environments; the *source* hash
above is the reproducibility anchor).

### RUN-703-GATE-001 — the declared measurement run

Wrapped only to capture rusage; the wrapper writes stdout/stderr to files and prints a
one-line JSON receipt.

```
python3 $SCRATCH/runwrap.py $SCRATCH/measurements.json $SCRATCH/gate.stderr.log \
        $SCRATCH/gate_601b 20260731 5 8 8 2
```

Inner command: `$SCRATCH/gate_601b 20260731 5 8 8 2`
argv meaning: `seed_base=20260731  structures_per_run=5  keys_at_3bit=8  keys_at_4bit=8  keys_at_5bit=2`

Real receipt, verbatim:

```json
{"command": ["/tmp/claude-0/-home-user-crypto-autoresearcher/42d1537b-7158-5124-bdad-0c8e3df17d46/scratchpad/gate_601b", "20260731", "5", "8", "8", "2"], "exit_status": 0, "wall_clock_seconds": 272.969, "peak_rss_kib": 67412, "user_cpu_seconds": 272.362, "sys_cpu_seconds": 0.537}
```

stderr: **0 bytes**. 54 measurement runs emitted. The program's own stdout is preserved
verbatim inside `gate_601b_results.json` → `raw_measurements`.

`runwrap.py` is four lines of `subprocess.run` + `resource.getrusage`; it is reproduced
here so no artifact depends on an unarchived scratch file:

```python
import resource, subprocess, sys, time, json
cmd = sys.argv[3:]
t0 = time.time()
with open(sys.argv[1], "wb") as out, open(sys.argv[2], "wb") as err:
    p = subprocess.run(cmd, stdout=out, stderr=err)
wall = time.time() - t0
ru = resource.getrusage(resource.RUSAGE_CHILDREN)
print(json.dumps({"command": cmd, "exit_status": p.returncode,
                  "wall_clock_seconds": round(wall, 3), "peak_rss_kib": ru.ru_maxrss,
                  "user_cpu_seconds": round(ru.ru_utime, 3),
                  "sys_cpu_seconds": round(ru.ru_stime, 3)}))
```

### Budget

| limit | value | used | within |
|---|---|---|---|
| wall clock | 2700 s | 272.969 s (measurement run) | yes |
| memory | 4 GB | peak RSS 67412 kiB ≈ 65.8 MiB ≈ 0.064 GB | yes |
| maximum runs | 8 | 2 declared runs | yes |

No timeout, crash, or resource-exhaustion condition occurred.

---

## 4. What was built

### 4.1 The cipher (a definitional construction, not AES)

n-bit cells over GF(2^n), 4×4 cell state, 5 rounds:

```
X = P + K0
rounds 1..3 : SubCells, ShiftRows, MixColumns, AddRoundKey   -> X3 is balanced
round  4    : SubCells, ShiftRows, MixColumns   (NO AddRoundKey)
round  5    : SubCells, ShiftRows, AddRoundKey  (NO MixColumns)
```

Declared definitional choices, each a property of this toy construction:

1. **Round 4 carries no AddRoundKey.** Deliberate, so the key-guess space is *exactly* the
   four cells this gate specifies (q⁴ = 2^16 at n = 4) rather than five. This is not an
   AES round structure.
2. **No key schedule**: six independent seeded random 16-cell round keys.
3. **MixColumns** is the AES-shaped circulant (2,3,1,1) over GF(2^n) *iff* it passes three
   acceptance conditions — all entries nonzero (needed for one active cell to spread to a
   full column, which the 3-round balance property uses); invertible; and row 0 of the
   inverse has four nonzero **pairwise distinct** entries (a zero would make one guessed
   cell irrelevant, a repeat would make two guessed cells interchangeable). It passes at
   n = 4 and n = 5. It **fails at n = 3**, where its inverse row over GF(2^3) is
   (5,0,6,2) — a zero coefficient. At n = 3 the program therefore deterministically takes
   the first circulant row in packed order that does pass: **(5,2,1,1)**, inverse row
   (7,4,2,5). Recorded per run.
4. **The "algebraic" S-box** is GF(2^n) inversion followed by an invertible GF(2)-affine
   map (smallest invertible circulant tap mask, plus constant `0x63 & (2^n − 1)`). At
   n = 3 every invertible circulant has weight 1, so the affine layer there is the
   identity rotation; recorded as `affine_taps` per run.

Field polynomials: n=3 `0x0B`, n=4 `0x13`, n=5 `0x25`.

**Data.** Per structure: q⁴ chosen plaintexts varying the four state-diagonal cells over
all values with the other twelve constant — a disjoint union of q³ Λ-sets, so the 3-round
balance property makes the aggregate zero for the correct guess. 5 structures per run,
reduced to a parity table `N0` over the four ciphertext cells the guess acts on, at
positions (row i, col (4−i) mod 4).

**A separate, explicit self-check** verifies the balance property directly on the round-3
state for every run (`balance_selfcheck`). It passed in **54/54** runs.

### 4.2 The aggregation object, and the two implementations

```
g(k) = XOR over the structure of  Sinv( XOR_i G_i[ c_i XOR k_i ] ),
       G_i[y] = Minv[0][i] * Sinv(y)
```

A guess survives a structure iff `g(k) = 0`, and survives the run iff it survives all five.

* **DIRECT** — partial-sums aggregation. Peels one ciphertext cell at a time, carrying a
  parity table that shrinks by a factor q per peeled cell (q⁴ → q⁴ → q³ → q² → q),
  evaluated over the whole guess space.
* **REORGANIZED** — the same `g` as a 4-dimensional Walsh–Hadamard convolution over the
  group (GF(2)^n)^4. For each of the n basis output-bit masks u,
  `C_u = WHT⁻¹( WHT(N0) · WHT(F_u) )` with `F_u(x) = (−1)^<u, Sinv(XOR_i G_i[x_i])>`, and
  the survival bit is recovered as `((T − C_u(k))/2) mod 2` with `T = Σ_c N0[c] = WHT(N0)[0]`.

Both were written in this task. Both consume the same `N0` tables. Both sweep the full
guess space for every structure; neither prunes using another structure's survivors.

### 4.3 Counting convention — counted, not timed

Four classes, incremented at the site where the arithmetic happens, through four macros
(`C_TL`, `C_XR`, `C_AD`, `C_ML`) defined once at the top of the file and routed through a
single global counter pointer that is retargeted per implementation:

| class | definition |
|---|---|
| `table_lookups` | one indexed read of **any** array — lookup table or working table alike |
| `xors` | one XOR of a data value or of an index value |
| `adds` | one integer addition or subtraction on a data value |
| `muls` | one integer multiplication on a data value |

`total = table_lookups + xors + adds + muls`, **unweighted**.

**Not counted, on either side:** array writes; `memset`/table clearing; loop bookkeeping;
shifts and masks used for bit-field packing; comparisons and branches.

**Outside both counters** (identical shared preprocessing): key setup, S-box construction,
encryption of the data, construction of `N0`, and the balance self-check.

**Unweighted-total caveat, stated plainly.** The two implementations have genuinely
different op-class profiles — the direct side records *zero* adds; the reorganized side
records 1 082 368 XORs against 760 217 600 adds at n = 5. Summing the classes with weight
1 each is a stated convention, not a cost model. A different per-class weighting would give
a different ratio. The full per-class breakdown is in the JSON so any weighting can be
recomputed from these numbers.

### 4.4 Demonstration that the counting is symmetric across the two implementations

1. Every counted site on both sides goes through the **same four macros**, defined once.
2. The `G_i` table construction is **literally the same function** `build_G()`, called by
   both `agg_direct()` and `agg_reorg()`. Its standalone cost is measured with a fresh
   counter and emitted per run as `ops_shared_build_G` — 4q lookups + 4q multiplies
   (**64 + 64 at n = 4**) — and appears with exactly that value inside both totals.
   `ops_direct_precompute_total` equals it *exactly* (128 at n = 4), the direct side having
   no other precomputation.
3. Both sides consume the same `N0` for the same key, structures and S-box, and both sweep
   the full guess space per structure.
4. Each aggregation is run with its own zeroed counter struct; neither can contaminate the
   other.

**Residual data dependence, disclosed.** The reorganized side is fully data-oblivious: its
counted total is *bit-for-bit the same integer* for every key and every S-box at a given
width (68 625 045 at n = 4; 1 622 214 949 at n = 5). The direct side has exactly one
data-dependent counted site — the final step XORs `Sinv(z)` only for odd-parity entries of
the last table — so its total moves slightly with the data. That movement is present
between keys *under a fixed S-box* too, and that is the correct reference against which the
null control is read.

---

## 5. Yield 1 — correctness equivalence

**Protocol.** For every (cell width, S-box variant, key) both aggregations run on the same
`N0` tables; the surviving-key bitmaps are compared byte-for-byte over the whole guess
space with `memcmp`, and an FNV-1a-64 digest of each bitmap is recorded.

| | |
|---|---|
| measurement runs total | **54** |
| runs at the 2^16 guess space (4-bit cells) | **24** |
| distinct keys at 2^16 | **8**, under each of the three S-box variants |
| sets identical (byte-for-byte) | **54 / 54** |
| digests match | **54 / 54** |
| correct key survives under **both** | **54 / 54** |
| balance self-check passed | **54 / 54** |
| runs where the sets differ | **none** |

### Verdict — **IDENTICAL**

In all 54 runs — 24 of them at the fully enumerable 2^16 guess space, covering 8 distinct
keys under each of the three S-box variants — the two aggregations returned byte-identical
surviving-key bitmaps and identical digests, and the correct key survived under both.
The VOID-by-disagreement condition did **not** fire.

Per-run digests, survivor counts, key seeds and true-guess indices for every one of the 54
runs are in `gate_601b_results.json` → `yield_1_correctness_equivalence.per_run_digests`.

---

## 6. Yield 2 — S-box independence under the null control

**Null object.** The cipher's algebraic S-box replaced by a **freshly drawn random
bijection** on the cell alphabet (Fisher–Yates over seeded splitmix64). **Two** independent
draws, A and B. Everything else — cipher structure, MixColumns, key seeds, structure seeds,
both implementations, and the counting convention — unchanged.

Seeds: A = `seed_base ^ 0xA5A5A5A5 ^ cell_bits`, B = `seed_base ^ 0x5A5A5A5A ^ cell_bits`,
`seed_base = 20260731`. Recorded per run in the JSON.

Ratios side by side (mean of `ops_reorg_total / ops_direct_total` over the keys run):

| cell bits | algebraic S-box | random-bijection null (A and B pooled) | absolute difference | relative difference | largest key-to-key relative spread *within* a single fixed S-box |
|---|---|---|---|---|---|
| 3 | 0.106512727063 | 0.106511151213 | 1.576e-06 | **1.479e-05** | 1.242e-04 |
| 4 | 0.044370095938 | 0.044370099352 | 3.414e-09 | **7.694e-08** | 6.000e-06 |
| 5 | 0.016585171497 | 0.016585171999 | 5.020e-10 | **3.027e-08** | 2.841e-07 |

Stated tolerance: **1 % relative**.

### Verdict — **S-BOX-INDEPENDENT WITHIN THE STATED TOLERANCE**

At every cell width the counted ratio under the two random-bijection null S-boxes differs
from the ratio under the algebraic S-box by a relative amount far inside 1 %: 1.48e-05
(n=3), 7.69e-08 (n=4), 3.03e-08 (n=5). The reorganized side's counted total is *exactly*
invariant — the same integer for every key and every S-box at a given width. All residual
movement is on the direct side's single data-dependent counted site.

Control-of-the-control: at n = 4 and n = 5 the between-S-box difference is **smaller than
the key-to-key spread observed within a single fixed S-box** (7.69e-08 vs 6.00e-06 at n=4;
3.03e-08 vs 2.84e-07 at n=5) — changing the S-box moves the ratio *less* than changing the
key does under a fixed S-box. At n = 3 the between-S-box difference (1.48e-05) stays an
order of magnitude below the within-S-box key-to-key spread (1.24e-04).

The VOID-by-S-box-dependence condition did **not** fire. Had the ratio moved beyond
tolerance, that would have shown the measured difference to be an implementation artifact
rather than an algebraic property, and it would have been reported as VOID. This is a
statement about these two implementations at these cell widths and nothing more.

---

## 7. Yield 3 — the measured counted ratio

**The only baseline is the direct partial-sums aggregation implemented in this task and run
on the same inputs.** No external, recalled, or published figure enters this comparison.

Measured counted-operation ratio, reorganized total ÷ direct total, unweighted, over the
full 5-structure key-recovery task:

| cell bits | guess space | runs | ratio (mean over all keys and all three S-box variants) | min | max | relative spread |
|---|---|---|---|---|---|---|
| 3 | 2^12 = 4096 | 24 | **0.1065116** | 0.106505529 | 0.106522200 | 1.57e-04 |
| **4** | **2^16 = 65536** | **24** | **0.0443701** | 0.044369957 | 0.044370223 | 6.00e-06 |
| 5 | 2^20 = 1048576 | 6 | **0.0165852** | 0.016585170 | 0.016585175 | 2.84e-07 |

The 2^16 instance (4-bit cells) is the enumerable instance this gate specifies; the 3-bit
and 5-bit numbers are measurements at those widths.

**Raw counter totals** (example run: key index 0, algebraic S-box, 5 structures):

| cell bits | side | table_lookups | xors | adds | muls | **total** |
|---|---|---|---|---|---|---|
| 3 | direct | 12 533 152 | 12 205 440 | 0 | 32 | **24 738 624** |
| 3 | reorganized | 1 376 877 | 4 672 | 1 191 936 | 61 472 | **2 634 957** |
| 4 | direct | 778 568 312 | 768 082 488 | 0 | 64 | **1 546 650 864** |
| 4 | reorganized | 35 524 949 | 69 888 | 31 719 424 | 1 310 784 | **68 625 045** |
| 5 | direct | 49 073 355 100 | 48 737 810 652 | 0 | 128 | **97 811 165 880** |
| 5 | reorganized | 834 700 453 | 1 082 368 | 760 217 600 | 26 214 528 | **1 622 214 949** |

(All three rows are the algebraic-S-box run at key index 0, matching
`ops_class_breakdown_example_run` in the JSON. The corresponding direct totals under the
two null S-boxes differ only in the last few digits — e.g. 97 811 172 536 and
97 811 165 608 at n = 5 — and every value is in `raw_measurements`.)

**Composition of the measured totals** (same example runs, 5 structures per run) — a
decomposition of numbers actually measured, with no model fitted to them:

| cell bits | direct precompute | direct per structure | reorganized precompute | reorganized per structure |
|---|---|---|---|---|
| 3 | 64 | 4 947 712 | 341 192 | 458 753 |
| 4 | 128 | 309 330 147 | 9 314 960 | 11 862 017 |
| 5 | 256 | 19 562 233 124 | 227 608 864 | 278 921 217 |

The direct side's precomputation is only the shared `G` tables. The reorganized side's
precomputation — the `G` tables, the combined table `Z`, and the transformed mask functions
— is independent of the key and of the data structures, so it is paid once per cipher and
reused across the five structures. Both parts of the split are reported as measured
numbers.

### Verdict — measured ratios as above

0.10651 at 3-bit cells, **0.044370 at 4-bit cells (the 2^16 instance)**, 0.016585 at 5-bit
cells. These are measurements at the widths actually run. **No scaling law is fitted to
them, no crossover is predicted, and nothing is extrapolated to any other cell width.**

---

## 8. Wall clock — reported separately, not substituted for the counted ratio

Timings are single-run observations on a shared 4-core VM, single-threaded, and are **not**
the gate's measurement. Example runs (algebraic S-box, key index 0), seconds:

| cell bits | data generation | direct | reorganized |
|---|---|---|---|
| 3 | 0.031 | 0.008 | 0.002 |
| 4 | 0.565 | 0.461 | 0.039 |
| 5 | 11.0 | 27.6 | 0.95 |

Whole measurement run: 272.969 s wall, 272.362 s user CPU, peak RSS 67 412 kiB.

---

## 9. Additional observations — recorded, not interpreted

1. **3-bit survivor saturation.** At 3-bit cells the surviving-key set does not shrink to
   the correct key alone: it saturates around **30 of 4096** guesses (observed range 29–37
   across the 24 declared runs at that width) and stops shrinking as structures are added.
   Exact numbers from the exploratory development sweep (one value per S-box variant, key
   index 0):
   * *Before* the MixColumns acceptance rule of §4.1 existed — first row (2,3,1,1), whose
     inverse row over GF(2^3) is (5,0,6,2), a zero coefficient making one guessed cell
     irrelevant — survivors at 1, 2, 3, 4, 5, 6 structures were
     (640,736,672), (272,328,312), (232,216,224), (192,184,192), (176,176,176),
     (176,176,176).
   * *After* the rule — first row (5,2,1,1), inverse row (7,4,2,5) — (608,576,552) at 1
     structure, (45,42,51) at 3, (30,32,32) at 5, (30,29,31) at 6.

   The correct key is always among the survivors, and both implementations always agree on
   the whole set. Recorded as an unexplained property of the 8-element cell alphabet in
   this toy construction. Not investigated further: it lies outside the three yields, and
   it does not affect them — the equivalence check compares whatever sets arise, and the
   counted ratio is not a function of the survivor count on either side.
2. At 4-bit and 5-bit cells the surviving set is the correct key alone in **44 of the 48**
   runs at those widths; 3 runs returned 2 survivors and 1 run returned 3.
3. The two op-class profiles are genuinely different (direct: zero adds; reorganized: adds
   dominate), which is why the unweighted-total caveat in §4.3 is stated explicitly rather
   than left implicit.
4. The **full-scale form of this attack was not attempted**. BATCH-001 declares it needs a
   2^32-entry (4 GB) accumulator, exceeding this task's 4 GB memory budget. It was not run,
   not partially run, and not estimated around.

---

## 10. VOID conditions

| condition | fired | detail |
|---|---|---|
| surviving-key sets differ (correctness bug) | **no** | 54/54 runs byte-identical |
| counted ratio depends on the S-box (implementation artifact) | **no** | relative difference 1.48e-05 / 7.69e-08 / 3.03e-08 at n = 3/4/5, all far inside the 1 % tolerance |

Neither VOID condition occurred, so the counted ratio of §7 is reported as a measurement
rather than suppressed. Neither of these outcomes is a result about AES; both are results
about this implementation pair on this toy construction.

---

## 11. Terminal status of every attempt, including what did not run

### Declared runs

| run id | kind | terminal status | exit | note |
|---|---|---|---|---|
| RUN-703-BUILD-001 | build | `completed_valid` | 0 | clean under `-Wall -Wextra`, 0 bytes stderr |
| RUN-703-GATE-001 | measurement | `completed_valid` | 0 | 272.969 s, 67 412 kiB peak RSS, 0 bytes stderr, 54 measurement runs emitted, executed **exactly once** |
| RUN-703-REPRO-001 | reproduction check | `completed_valid` | 0 | recompile of the archived source + re-run at the same seed; see §12 |

Certificate discipline (`docs/claims-and-verification.md`): **`certificate.kind: none`**,
stated explicitly. This is a pure measurement task — no discrete-log solve and no
factor-base relation is claimed, so there is nothing to certify. The two internal
correctness self-checks that *are* performed (the 3-round balance property, and that the
true key survives under both aggregations) are recorded per run in the JSON.

### Not run, with reasons

| item | reason |
|---|---|
| **GATE-601-A** | **NOT DISPATCHED.** CAND-601-A is premise-undermined and repair-before-run under DEC-20260731-011. It was not run, not partially run, and its statistic was not computed. |
| full-scale form of the reorganization | Declared out of envelope in BATCH-001 (2^32-entry, 4 GB accumulator against a 4 GB task budget). Not attempted and not estimated around, per the handoff. |
| `python3 -m orchestration.adapter doctor --probe` | Not run in this task; `model_verified` is therefore recorded **false** rather than asserted true. |

### Protocol deviations, recorded not discarded

1. **Key counts differ by width.** 8 keys per S-box variant at 3-bit and 4-bit cells, but
   **2** per variant at 5-bit cells, because a 5-bit key-variant costs ≈ 40 s and the full
   sweep had to fit the 2700 s budget. The completion gate requires at least 8 keys at the
   2^16 guess space; that is met with 8 distinct keys under each of the three S-box
   variants (24 runs). The 3-bit and 5-bit widths are measurements, not the gated instance.
2. **MixColumns at 3-bit cells is (5,2,1,1), not the AES-shaped (2,3,1,1)**, for the
   algebraic reason in §4.1. Recorded per run rather than hidden.
3. **Development iterations preceded the declared runs**, in the scratchpad: an exploratory
   survivor-count sweep (numbers reproduced in §9.1) and a first version whose 3-bit
   MixColumns inverse row carried a zero coefficient. They are described here rather than
   discarded. **No declared run was repeated to obtain a more favourable number**, and the
   declared measurement run was executed exactly once, with its output preserved verbatim
   in the JSON.

---

## 12. Reproduction

```bash
cd /home/user/crypto-autoresearcher
sha256sum coordination/goals/GOAL-AES-001/batches/BATCH-002/tasks/TASK-20260731-703/gate_601b_impl.c
# expect dc2bc3fe02a08881a048eccfe48c64ebe2c5a35a6a9884b1fc33f0cf4b4789f3

gcc -O2 -std=c11 -Wall -Wextra -o /tmp/gate_601b \
    coordination/goals/GOAL-AES-001/batches/BATCH-002/tasks/TASK-20260731-703/gate_601b_impl.c
/tmp/gate_601b 20260731 5 8 8 2 > /tmp/measurements.json
```

Every counted number, survivor count, digest, seed and verdict in this record is a function
of `argv` alone. The program takes no other input. Comparing `/tmp/measurements.json`
against `raw_measurements` in `gate_601b_results.json` should differ only in the
`wall_clock_seconds` fields, which are timing observations and are reported separately from
the counted operations.

**RUN-703-REPRO-001 — reproduction check actually performed.** The archived source was
recompiled into a fresh binary and re-run at the same seed:

```
gcc -O2 -std=c11 -Wall -Wextra -o $SCRATCH/verify_bin $TASKDIR/gate_601b_impl.c
$SCRATCH/verify_bin 20260731 5 8 8 0 > $SCRATCH/verify.json
```

(`keys_at_5bit = 0` keeps the check cheap; that argument affects only the 5-bit loop and
leaves the 3-bit and 4-bit output unchanged.) Exit status 0. **All 48 emitted run records
at 3-bit and 4-bit cells — every survivor count, digest, seed, verdict and counter total —
compared equal field-for-field against the corresponding records of RUN-703-GATE-001, with
only the `wall_clock_seconds` fields excluded.** Determinism confirmed.

---

## 13. Completion gate check

| gate item | status |
|---|---|
| inference block in both `gate_601b_results.json` and `run_record.md` | present, with policy, requested_policy, resolved model, `fallback_used: true`, `model_verified: false`, standing basis `0137a051` |
| Yield 1: ≥ 8 random keys at the 2^16 guess space, sets compared exactly, verdict + per-key digests | 8 distinct keys × 3 S-box variants = 24 runs at 2^16; verdict IDENTICAL; digests recorded per key and per seed |
| Yield 2: identical comparison re-run with a seeded random bijection, both ratios side by side, difference quantified, VOID reported if moved | two independent seeded draws; ratios tabulated in §6; differences 1.48e-05 / 7.69e-08 / 3.03e-08; VOID did not fire |
| Yield 3: measured ratio at 2^16 and at each width run, raw counter totals both sides, counting convention stated and shown symmetric | §7 tables; convention §4.3; symmetry demonstration §4.4 |
| no literature comparison, recalled baseline, `sota_delta`, bit-margin, other-width extrapolation, or crossover prediction anywhere | none present; §0 declares the exclusion and cites DEC-20260731-011 |
| small-scale scope stated; nothing asserted about AES | §0 and §4.1 |
| every attempted run's terminal status recorded, including what did not run and why | §11 |
| results JSON machine-readable with commands, exit statuses, tool versions, git commit and dirty state, seeds, timestamps, resource measurements | yes |
| raw data and summaries agree | summaries in the JSON are computed from `raw_measurements` in the same script and both are archived |
| result reproduces from the recorded command and revision | §12 |
