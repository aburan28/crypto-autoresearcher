# Check (c) — GATE-601-B run package and null control (TASK-20260731-703)

**Independent validation, TASK-20260731-705. Verdict for check (c) only.**
This file carries ONE verdict. It does not validate the derivation note
(check (a)) or the harness repair (check (b)), and a defect there does not
invalidate what is measured here.

| field | value |
|---|---|
| Reviewed revision | `ebac9ba8` (snapshot, TASK-20260731-704) |
| Artifacts | `gate_601b_impl.c` (`dc2bc3fe…`), `gate_601b_results.json`, `run_record.md` |
| **Verdict (c)** | **passed** |
| Struck-claim scope violations found | **NONE** |
| Official state changed | none. No evidence strength assigned. |

---

## 1. What I re-ran, and what I did not

**Re-ran, from committed source, end to end:**

```
gcc -O2 -std=c11 -Wall -Wextra -o gate_val gate_601b_impl.c   # exit 0, stderr 0 bytes
./gate_val 20260731 5 8 8 2                                    # exit 0
```

The source was extracted with `git show ebac9ba8:…/gate_601b_impl.c`; its
SHA-256 is `dc2bc3fe02a08881a048eccfe48c64ebe2c5a35a6a9884b1fc33f0cf4b4789f3`,
matching both the snapshot manifest and `artifacts.implementation_sha256`
recorded inside the results JSON. It compiles clean under `-Wall -Wextra`, as
the run record states. Runtime on my run was in the same ~273 s range as the
recorded 272.969 s (the wall clock is the only field I exclude from comparison).

**All 54 measurement runs reproduce bit-for-bit.** I compared my binary's
`runs` array against `raw_measurements.runs` in the committed JSON field by
field, excluding only `wall_clock_seconds`:

> **runs differing: 0 / 54**, over all of `cell_bits`, `guess_space`,
> `sbox_variant`, `sbox_seed`, `key_index`, `key_seed`, `structure_seed_base`,
> `affine_taps`, `affine_const`, `mixcolumns_row`, `mixcolumns_inv_row0`,
> `balance_selfcheck`, `survivors_direct`, `survivors_reorg`, `digest_direct`,
> `digest_reorg`, `sets_identical`, `true_guess`, `true_guess_survives_*`,
> the four op-class counters on each side, `ops_shared_build_G`, the
> precompute/per-structure decompositions, and `ratio_reorg_over_direct`.

**Not re-run, stated plainly:**

- I did not write an independent reimplementation of either aggregation. Budget
  did not allow it, and I say so rather than implying deeper coverage. My
  correctness check is therefore *reproduction* of their comparison, plus source
  reading of both aggregations, not an independent third implementation.
- I did not re-derive the small-scale cipher's specification from anything
  outside `gate_601b_impl.c`.
- I did not run the exploratory development sweep referenced in §9.1 of the run
  record; those numbers are outside my reproduction.

---

## 2. Yield 1 — correctness equivalence

**Verdict: CONFIRMED, and the comparison is exact rather than digest-only.**

Reading `main()` and lines 481–560 of the implementation: the surviving-key
bitmaps are compared with `memcmp` over the **whole** guess space, and the
FNV-1a-64 digest is recorded *in addition* to that comparison, not in place of
it. `sets_identical` is the memcmp result. So the task card's concern — a
digest of a partial set standing in for an exact comparison — does not apply:
the exact comparison is the primary check and covers every guess.

From my own run:

| cell width | runs | `sets_identical` all runs | true key survives both, all runs | `balance_selfcheck` |
|---|---|---|---|---|
| n=3 (2^12) | 24 | **true** | **true** | passed |
| n=4 (2^16) | 24 | **true** | **true** | passed |
| n=5 (2^20) | 6 | **true** | **true** | passed |

54/54 runs, byte-identical bitmaps, identical digests, correct key surviving on
both sides. The 24 runs at the fully enumerable 2^16 instance cover 8 distinct
keys under each of three S-box variants, as claimed.

One recorded-not-interpreted observation I confirm from the raw data: survivor
counts at n=3 sit around 30–37 out of 4096, i.e. the small-scale construction
does not isolate a unique key at that width. The record carries this in
`additional_observations_recorded_not_interpreted` and does not build on it.
Correct handling.

---

## 3. Yield 2 — S-box independence under the null control

**Verdict: CONFIRMED. Both ratios reported below are computed by me from my own
run's raw data.**

The null object is the cipher's algebraic S-box replaced by a **freshly drawn
random bijection** (Fisher–Yates over seeded splitmix64), two independent draws
A and B, with everything else — cipher structure, MixColumns, key seeds,
structure seeds, both implementations, the counting convention — unchanged.
That is a null object of the same shape, which is what
`docs/inventor-protocol.md` §3 requires.

My recomputation, means over runs at each width:

| cell width | ratio, **algebraic S-box** | ratio, **random-bijection null** | relative difference | key-to-key spread within one fixed S-box |
|---|---|---|---|---|
| n=3 | 0.106512727063125 | 0.106511151212875 | **1.48e-05** | 1.24e-04 |
| n=4 | 0.044370095938125 | 0.044370099352125 | **7.69e-08** | 6.00e-06 |
| n=5 | 0.0165851714965 | 0.0165851719985 | **3.03e-08** | 2.84e-07 |

All three are far inside the declared 1% tolerance, and every figure agrees
with the committed record. I independently confirm the two structural facts the
record leans on:

- `ops_reorg_per_structure_total` is **exactly constant** across all keys and
  all S-box variants at each width (I checked: one distinct value per width).
  The reorganized side is data-oblivious, so all residual movement is on the
  direct side's single data-dependent counted site — the final
  `if (T4[z] & 1) g ^= sinv[z]` at line 393.
- At n=4 and n=5 the between-S-box difference is **smaller than the key-to-key
  spread under a fixed S-box**, which is the right way to state the comparison:
  changing the S-box moves the ratio less than changing the key does. At n=3 it
  is an order of magnitude smaller, and the record says "comparable … and
  remains an order of magnitude smaller" rather than overstating it.

**What this control does and does not establish.** It is a control against an
*implementation artifact*: a ratio that moved under S-box randomization would
have shown the counted difference to be an artifact of the algebraic S-box
rather than a property of the reorganization, and would have voided the run.
It did not move. The control does **not** establish that the reorganization is
useful, that the ratio means a speedup, or anything about AES. The record's
`artifact_check` field says precisely this ("This is a statement about these two
implementations at these cell widths and nothing more"). Honest.

The reported quantity does behave as it should under the parameter meant to
destroy it: the reorganization is algebraically S-box-agnostic, so the
*prediction* is invariance, and invariance is what is measured — a
correspondence between prediction and measurement, not a signal that fails to
decay.

---

## 4. Yield 3 — the measured ratio at the 2^16 instance

**Verdict: CONFIRMED.**

From my own run, n=4 key 0 algebraic:

```
direct : table_lookups 778568312  xors 768082488  adds        0  muls      64  total 1546650864
reorg  : table_lookups  35524949  xors     69888  adds 31719424  muls 1310784  total   68625045
68625045 / 1546650864 = 0.04437009450375867
```

Both raw totals match the claim exactly (1546650864 and 68625045), and the
quotient matches the recorded per-run ratio `0.044370094504`. Across all 24 runs
at n=4 I compute mean **0.044370098214125**, min 0.044369957261, max
0.044370223485, relative spread 6.0e-06 — identical to the record's
`primary_instance` block, and consistent with the headline 0.0443701.

For completeness, my recomputed means at the other widths: n=3
**0.106511676496**, n=5 **0.016585171831**. Both match the record.

This is a **measured ratio against a baseline that was run on the same inputs**,
not a projection — the form `docs/inventor-protocol.md` §6 step 2 asks for. The
baseline is the direct partial-sums aggregation implemented in the same task and
run on the same `N0` tables, same keys, same structures, same S-box.

---

## 5. Counting symmetry — is the same work charged to both sides?

**Verdict: SUBSTANTIALLY SYMMETRIC, with two named asymmetries, neither of
which reverses the direction of the measurement.**

What I verified by reading the source rather than by trusting the
`symmetry_demonstration` field:

- All counted sites on both sides go through the same four macros `C_TL`,
  `C_XR`, `C_AD`, `C_ML` (lines 77–80), incrementing through one global pointer
  `CUR` retargeted per implementation. Each aggregation zeroes its own counter
  struct on entry (lines 340, 420) and clears `CUR` on exit. Neither side's
  counters can leak into the other's.
- `build_G()` is **literally the same function** called by both `agg_direct`
  (line 342) and `agg_reorg` (line 422), and it counts `C_TL(1)` + `C_ML(1)` per
  entry inside itself, so the identical cost lands in both totals. I confirmed
  numerically: `ops_shared_build_G = {tl 64, ml 64, total 128}` at n=4 and
  `ops_direct_precompute_total = 128` exactly — the direct side has no other
  precomputation, as claimed.
- Both sides consume the same `N0` parity tables and both sweep the full guess
  space for every structure; neither prunes using another structure's survivors.
  Confirmed in the loop structure.
- The shared preprocessing that is outside *both* counters — key setup, S-box
  construction, encryption, `N0` construction, the balance self-check — is
  outside both, not charged to one.

**Asymmetry 1 — an uncounted integer division on the reorganized side.**
Line 469, `int64_t cu = P[k] / (int64_t)n4;`, counts only the `C_TL(1)` array
read. The division itself falls into none of the four declared classes and is
therefore free. It executes `n4 × NB × R = 65536 × 4 × 5 = 1,310,720` times at
n=4. Charging it at weight 1 would raise the reorganized total by ~1.9%, moving
the ratio from 0.04437 to ~0.04522. Small, but it is a data operation on one
side only that the convention does not name. Recorded as **D-705-9 (low)**.

**Asymmetry 2 — excluding array writes is nominally symmetric and materially
favours the reorganized side.** "Array writes" are excluded on both sides, which
sounds even-handed. But the two sides have very different write-to-counted-op
ratios. From my run at n=4: the reorganized side's Walsh–Hadamard butterflies
perform `2` writes per butterfly, and the butterfly count implied by its own
`adds` counter (31,719,424 total minus 1,310,720 final-loop adds = 30,408,704
butterfly adds, i.e. 15,204,352 butterflies) gives **30,408,704 uncounted
writes against a counted total of 68,625,045 — about 44%.** The direct side's
uncounted `memset`s total roughly 21 M byte-writes against a counted total of
1.55e9, i.e. under 1.4%; its `T[nidx] ^= v` writes are already accompanied by
counted read+XOR pairs. Counting the reorganized side's butterfly writes alone
moves the ratio from 0.04437 to **0.06403**. Recorded as **D-705-10 (low)**.

Neither asymmetry, alone or together, changes the direction or the order of
magnitude of the measurement. I found no site where the direct side is charged
for work the reorganized side performs and is not charged for.

**The shared `build_G()` does not favour either side**: it is identical code,
counted identically, and at 128 counted ops out of 1.55e9 / 6.9e7 it is
numerically irrelevant to both.

---

## 6. Is "convention, not cost model" an honest framing?

**Verdict: YES, honest — and I can put a number on the sensitivity.**

The record declares the unweighted four-class sum a **convention**, states the
caveat in `counting_convention.unweighted_caveat` in terms ("the direct side is
lookups and XORs with zero adds, the reorganized side is lookups and adds plus
one multiply per transformed entry — so a different per-class weighting would
give a different ratio"), and archives the full per-class breakdown so any
weighting can be recomputed. That is the correct disclosure: it names the
profile asymmetry the task card asks about rather than hiding behind the single
number.

**Could a different weighting reverse the ratio?** I computed it rather than
speculating, using the n=4 key-0 breakdown:

| weighting | ratio (reorg / direct) |
|---|---|
| unweighted (as reported) | **0.0444** |
| + reorganized-side butterfly writes counted | 0.0640 |
| byte-traffic weighting (reorg works on `int64_t`, 8 B; direct on `uint8_t`, 1 B — so weight reorg's `tl`, `ad`, `ml` ×8) | **0.3546** |
| adds weighted 10× a table lookup | 0.2289 |
| adds weighted 20× | 0.4340 |
| adds weighted **48×** | **1.0083 — the reversal point** |
| adds weighted 100× | 2.0747 |

So: the ratio is **convention-sensitive by roughly an order of magnitude** — a
memory-traffic weighting moves it from 0.044 to 0.355 — but reversal requires
charging an `int64` addition about **48 times** a byte table lookup, which is
not a defensible weighting on any real machine (if anything the lookup is the
more expensive of the two). The honest statement is: the *direction* of the
measurement is robust to plausible reweighting; the *magnitude* is not, and the
reported 0.0444 is the most favourable end of that range. The record does not
claim otherwise, but it also does not quantify the range. Recorded as
**D-705-11 (informational)** — a suggestion, not a defect in what was reported.

**Memory is not reported per side.** The record gives whole-process peak RSS
(67,412 KiB ≈ 0.064 GB, inside the 4 GB budget), but not the memory each
aggregation uses. From the source at n=4 the direct side allocates
`n4+n3+n2+n1 = 69,904` bytes; the reorganized side allocates `Z` (65,536 B)
plus `WN`, `P` and `NB=4` mask arrays of `int64_t[65536]` = 3,145,728 B, total
**3,211,264 bytes — about 46× the direct side**. Under the target-result
profile's cost-honesty requirement (memory beside time), a counted-operation
ratio of 0.044 reported without the accompanying 46× memory ratio is an
incomplete cost picture. Recorded as **D-705-12 (low)**. Both figures are
derivable from the committed source, so nothing is hidden — it is simply not
tabulated.

---

## 7. Scope-violation sweep against DEC-20260731-011

`DEC-20260731-011` struck CAND-601-B's `sota_delta` and every recalled-baseline
comparison. I grepped all three TASK-20260731-703 artifacts — the C source, the
146 KB results JSON and the 553-line run record — case-insensitively for:
`sota_delta`, `bit margin` / `bit-margin`, `crossover`, `extrapolat*`,
`literature`, `recalled`, `baseline`, `speedup`, `faster than`, `beats`,
`outperform*`, `state of the art`, `8-bit`, `full AES`.

**Every hit is a disclaimer stating the prohibition or a scoping statement.**
Specifically:

- `run_record.md` §0 lines 18–24: cites `DEC-20260731-011` disposition
  `CAND_601_B` and declares the record contains no literature comparison, no
  recalled baseline, no bit-margin, no `sota_delta`, no extrapolation to any
  other cell width, and no crossover prediction; and records that the original
  GATE-601-B PASS/FAIL escalation criterion is **withdrawn** because its
  escalation leg depended on a struck extrapolation.
- `run_record.md` line 401 and line 548: the same exclusion restated and carried
  into the completion-gate table.
- `gate_601b_results.json` `scope_statement`: "It is NOT AES. Nothing recorded
  here is a statement about AES at any round count, about full-round AES, or
  about the security of any deployed system."
- `yield_3.baseline_statement`: "THE ONLY BASELINE IS THE DIRECT PARTIAL-SUMS
  AGGREGATION IMPLEMENTED IN THIS TASK AND RUN ON THE SAME INPUTS. No external,
  recalled or published figure enters this comparison in any form."
- `yield_3.verdict_statement`: "These are measurements at the widths run. No
  scaling law is fitted to them, no crossover is predicted, and nothing is
  extrapolated to any other cell width." The `cost_decomposition` blocks repeat
  "no scaling law is fitted and nothing is extrapolated" at each width.
- The three per-width numbers (0.10651 at n=3, 0.044370 at n=4, 0.016585 at n=5)
  are reported side by side with **no trend fitted and no fourth width
  predicted**, which is the temptation this prohibition exists to block. I
  checked for an implicit extrapolation — a fitted exponent, a "per-bit" factor,
  an asymptotic remark — and found none.
- `gate_601b_impl.c` contains no such text at all.

**No scope violation of DEC-20260731-011 appears anywhere in the
TASK-20260731-703 artifacts.** This confirms the dispatcher's own sweep
independently.

Scoping is also correct in the affirmative direction: the run record and the
results JSON both state that the object measured is a **small-scale AES-shaped
SPN with 3/4/5-bit cells**, that it **is not AES**, and that nothing here is a
statement about AES at any round count. The `experiment_definition` block names
the field polynomials (0x0B, 0x13, 0x25), the aggregation object and the
definitional choices. The record also declares its protocol deviations, its
runs-that-did-not-run (including an n=6 configuration that would need a 2^32
accumulator exceeding the 4 GB budget), and that no declared run was repeated to
obtain a more favourable number.

---

## 8. Defects from check (c)

| id | severity | statement |
|---|---|---|
| D-705-9 | low | The integer division at `gate_601b_impl.c:469` (`P[k] / n4`, executed 1,310,720× per run at n=4) is a data operation on the reorganized side that falls outside all four declared counting classes and is therefore uncounted. Charging it at weight 1 moves the ratio 0.04437 → ~0.04522. |
| D-705-10 | low | Excluding array writes is nominally symmetric but materially favours the reorganized side: its uncounted Walsh–Hadamard writes are ~44% of its counted total, versus under 1.4% for the direct side's `memset`s. Counting them moves the ratio 0.04437 → 0.06403. |
| D-705-11 | informational | The convention caveat names the profile asymmetry but does not quantify it. Measured range: 0.0444 unweighted → 0.3546 under a byte-traffic weighting; reversal requires weighting an `int64` add ≈48× a byte table lookup. |
| D-705-12 | low | Memory is reported only as whole-process peak RSS, not per side. From the committed source the reorganized side allocates ~3.21 MB against the direct side's ~69.9 KB at n=4 — a 46× memory ratio not tabulated beside the 0.044 operation ratio. |

None of these is an evidence-integrity failure, none affects reproducibility,
and none changes the direction of any reported measurement.

---

## 9. Verdict for check (c)

**passed.**

- The implementation compiles clean and **all 54 measurement runs reproduce
  bit-for-bit** from committed source at the recorded seed, on every field
  except wall clock.
- **Yield 1 (correctness equivalence): CONFIRMED**, by exact `memcmp` over the
  full guess space in every one of 54 runs, with the digest as a supplement
  rather than a substitute; the true key survives on both sides everywhere.
- **Yield 2 (S-box independence under a seeded random-bijection null):
  CONFIRMED**, with both ratios recomputed by me — 1.48e-05 (n=3), 7.69e-08
  (n=4), 3.03e-08 (n=5) relative difference, all far inside the 1% tolerance,
  and below the within-S-box key-to-key spread at n=4 and n=5.
- **Yield 3 (measured ratio): CONFIRMED** — 68625045 / 1546650864 =
  0.0443700945 at the 2^16 instance, mean 0.0443700982 over 24 runs.
- **The counting convention is substantially symmetric**, with two named
  asymmetries (D-705-9, D-705-10) that shift the magnitude by tens of percent
  and reverse nothing.
- **The "convention, not cost model" framing is honest**; I quantified its
  sensitivity (0.044 → 0.355 under a byte-traffic weighting; reversal needs an
  implausible 48× add weight).
- **No struck literature comparison, recalled baseline, `sota_delta`,
  bit-margin, cross-width extrapolation or crossover prediction appears
  anywhere** in the TASK-20260731-703 artifacts. Only the disclaimers stating
  the prohibition.

This is a measurement on a small-scale AES-shaped SPN at 3-, 4- and 5-bit cells.
It is not AES, it demonstrates no speedup on AES, and it supports no
cryptanalytic claim. I change no official state and assign no evidence strength.
