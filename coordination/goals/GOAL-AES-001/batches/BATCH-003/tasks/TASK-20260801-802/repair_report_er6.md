# ER-6 closure, coverage boundary, and the C0 loader fix

**Task:** TASK-20260801-802 (executor) — GOAL-AES-001, BATCH-003
**Machine-readable receipt:** `repair_receipt_v3.json` (this report is prose; the
receipt is the record)
**Scope:** INSTRUMENT ONLY.

```yaml
inference:
  policy: executor-implementation
  requested_policy: executor-implementation
  resolved_model_id: claude-opus-5
  fallback_used: true
  fallback_reason: >-
    Structural. Under this Claude Code harness the orchestration/model-policies.yaml
    policy aliases cannot be resolved by subagent frontmatter (CLAUDE.md, "Model
    policy note"); all subagents run `model: inherit`.
  model_verified: false      # `python3 -m orchestration.adapter doctor --probe` NOT run
  reasoning_effort: unrecorded
  independent_session: false
  degraded_allowed: false
  degraded_requirements: []
  standing_basis: inference-amendment commit 0137a051eb5828789eb267fa83c8278086578d4c
  provenance_basis: protocol-amendment-GOAL-AES-001-002 (in force from BATCH-003)
```

---

## 0. What this report is not

Nothing here is a claim about AES. A mutation control is an instrument; widening
its coverage is a reproducibility fact about that instrument and about nothing
else. This report asserts no evidence strength, proposes no state change, and
closes no hypothesis. It reports what was executed and what came out.

**H-2, H-4 and ER-5 remain OPEN and UNREPAIRED**, and are not mitigated,
narrowed or superseded by anything in this package. H-4 in particular — the
reduced-round path has no external reference and none can be obtained in this
environment — is irreducible. Widening the `final_mix_columns` axis widens
coverage *against the same internal comparison target*; it creates no external
reference, and anyone reading a wider green as a stronger statement about the
reduced-round convention would be reading it wrong.

---

## 1. What supersedes what, and what stands

| New file (BATCH-003) | Supersedes (BATCH-002, committed, READ-ONLY) |
|---|---|
| `mutation_control_v3.py` | `.../TASK-20260731-702/mutation_control_v2.py` (sha256 `d2b2a5dd…00d7`) |
| `verify_derivation_v2.py` | `.../TASK-20260731-701/verify_derivation.py` (sha256 `9618f55f…4951`) |
| `repair_receipt_v3.json` | `.../TASK-20260731-702/repair_receipt.json` (this task only) |
| `repair_report_er6.md` | `.../TASK-20260731-702/repair_report.md` (this task only) |

**No committed artifact was modified in place.** `mutation_control_v2.py`,
`verify_derivation.py` and `aes_reduced.py` were opened read-only; every mutated
or faulted copy was written into a per-run `tempfile.mkdtemp()` directory. Both
digests above were recomputed in this task from the committed blobs and match
the values recorded in BATCH-002. `git status --porcelain` at the end of the task
shows exactly one untracked path — this task's own directory — and no modified
tracked file.

**The BATCH-002 archived green STANDS AS RECORDED.** ER-6 is a *coverage*
escape. It bounds what a green from `mutation_control_v2` certifies about the
module under test; it falsifies none of that receipt's claims. Every one of its
five verdict components is a statement about *mutant detection*, and every one
of them was and remains true. This package must not be read as invalidating
BATCH-002, and it does not.

---

## 2. ER-6 / D-705-7 — closed on its axis, and proved

### The defect

`build_tasks()` in v2 generated

```python
for fmc in (False, True) if klen == 16 else (False,)
```

so `final_mix_columns=True` was only ever exercised with 16-byte keys. The
(key length × fmc) product was not covered, and the TASK-20260731-705 validator
showed that a fault confined to the uncovered part earns a full green.

### The fix

One line, in `fmc_variants()` in `mutation_control_v3.py`: `full` coverage (the
default) returns `(False, True)` for every key length. The v2 width is retained
*only* behind `--fmc-coverage legacy`, so that the before and the after can be
shown from one artifact without re-running the immutable v2 file.

### The proof, in three steps that were actually executed

**Step 1 — the fault, re-created verbatim from REPRO-705-6.** Injected into a
scratch copy of the committed `aes_reduced.py`, replacing the body of
`AES._is_final_round`:

```python
        if self.final_mix_columns and len(self.key) != 16:
            return i == max(self.rounds - 1, 1)   # VALIDATOR-INJECTED FAULT (ER-6 probe)
        return i == self.rounds and not self.final_mix_columns
```

**Step 2 — independently confirmed real and regime-confined, by direct
ciphertext comparison** (12-cell grid, seed `8020260801`, pristine module vs
faulted module, both executed in isolated subprocesses that import the module
under its *ordinary* name):

| key bytes | rounds | `fmc` | ciphertext differs? |
|---|---|---|---|
| 24 | 4 | **True** | **YES** |
| 24 | full | **True** | **YES** |
| 32 | 4 | **True** | **YES** |
| 32 | full | **True** | **YES** |
| 16 | 4 / full | True | no |
| 16 / 24 / 32 | 4 / full | False | no |

4 of 12 cells differ, and they are exactly the cells with `fmc=True` and key
length ≠ 16. The fault is real and it is confined to the regime v2 never
generated. (Full table with every ciphertext hex pair is in the receipt.)

**Step 3 — the before/after.**

| run | task width | verdict | no-op control mutant |
|---|---|---|---|
| RUN-802-4 | `legacy` (the v2 width) | **`pass`**, all five components true | `detected: false`, 164 comparisons, **0** divergences |
| RUN-802-5 | `full` (the repair) | **`FAIL`** (exit status 1) | `detected: true`, 212 comparisons, **48** divergences |

### By what mechanism the detection was credited

Two independent components flipped, both through **executed ciphertext
comparisons**, neither through any exception path.

1. **The semantics-preserving no-op control mutant.**
   `NOOP_is_final_round_rewritten` rewrites `_is_final_round` into the same
   boolean function, so it is semantics-preserving *with respect to the module
   it is derived from*. Any divergence it shows is therefore a divergence of the
   **module** from TARGET-REF, not of a mutation. Under the widened set it
   executed **212 comparisons** and diverged on **48**, and the per-cell
   breakdown places every one of those 48 in
   `k24_fmc1_r{1,2,3}` and `k32_fmc1_r{1,2,3}` — that is, *only* in cells the
   one-line widening added. Component `noop_mutant_not_detected` went false.
   Its row reads `status: compared`, `infrastructure_outcome: false`,
   `error_type: null`.

2. **Probe C.** Probe C's base is the *unmutated* module under test (its
   injection tampers only with an oracle, leaving the cipher byte-identical), so
   under the widened set it too diverges in the faulty cells: `detected: true`,
   standalone verdict `pass` against an expected `no_detection_credited`, so
   `matches_expectation` went false and component
   `all_injected_failure_probes_behaved_as_required` went false.

Under v3's detection rule — unchanged from v2 —
`detected := (comparisons_executed > 0) and (divergences > 0)`, an exception
could not have contributed to either flip even in principle. The H-1 property is
intact.

**ER-6 is closed on the (key length × final_mix_columns) axis.** It is not
closed as a class; see §4.

---

## 3. Regression — the widened set is not vacuous

A widened task set that fired on everything would make the ER-6 detection
meaningless. RUN-802-2 checks that against the **pristine** committed module,
212 tasks per mutant (36 full-round + 176 reduced-round):

| mutant | expected | detected | comparisons | divergences | at `r<Nr` | at `r=Nr` |
|---|---|---|---|---|---|---|
| `sbox_transpose_0x53_0x54` | true | true | 212 | 85 | yes | yes |
| `shiftrows_offsets_swapped` | true | true | 212 | 212 | yes | yes |
| `rcon_off_by_one` | true | true | 212 | 196 | yes | yes |
| `RR1_final_round_mixcolumns_retained` | true | true | 212 | 124 | **yes** | yes |
| `RR2_is_final_round_off_by_one` | true | true | 212 | 124 | **yes** | yes |
| `RR3_encrypt_partial_upper_bound_off_by_one` | true | true | 212 | 212 | **yes** | yes |
| `RR4_final_roundkey_from_untruncated_schedule` | true | true | 212 | 176 | **yes** | **NO** |
| `RR5_initial_addroundkey_miscounted` | true | true | 212 | 212 | **yes** | yes |
| `NOOP_is_final_round_rewritten` | **false** | **false** | **212** | **0** | no | no |

| probe | detected | standalone verdict | comparisons | matches expectation |
|---|---|---|---|---|
| A — import-time `AssertionError` | false | `FAIL` | 0 | yes |
| B — import-time `AttributeError` | false | `FAIL` | 0 | yes |
| C — import-time oracle tamper | false | `no_detection_credited` | 212 | yes |
| D — import-time `SystemExit` | false | `FAIL` | 0 | yes |

Verdict `pass`, all five components true, no unscored items. So:

- **H-1 still fails closed.** Every injection shape still scores
  `detected: false`; A, B and D with **zero** comparisons executed and an
  infrastructure outcome, never a detection.
- **H-3 still holds.** All five reduced-round mutants are still detected at
  `r < Nr`, and RR4 is still detected at `r < Nr` (176) and **not** at `r = Nr`
  (`invisible_at_full_rounds: true`) — the exact bug class H-3 named.
- **The no-op control still discriminates**, scoring `detected: false` *after*
  212 executed comparisons. The comparison ran and found nothing; it was not a
  silent skip.
- **Determinism:** RUN-802-2 and RUN-802-3 produced identical
  `results_digest` `7cb09212b03c335cc81f3aa58dcdd88085541d25e2bf1219a4d8348bc7c4a207`
  with `determinism_rerun_digest_matches: true`. Seeds are unchanged from v2
  apart from one added seed (`fault_confirmation: 8020260801`).

---

## 4. D-705-8 — the coverage boundary, stated rather than implied

The lesson of ER-6 is that **an uncovered axis is invisible until someone probes
it**, so the covered set is now written into the receipt
(`coverage_boundary`, computed by the control from the task set it actually
generated) rather than left to be inferred from the loop that generates it.

### What a green now covers

(key length × `final_mix_columns`) task counts, **all six cells non-empty**:

| | `fmc=False` | `fmc=True` |
|---|---|---|
| 16-byte key | 52 | 40 |
| 24-byte key | 36 | 24 |
| 32-byte key | 36 | 24 |

Round counts compared: `r ∈ {1,2,3,4,5}` for 16-byte keys, `r ∈ {1,2,3}` for 24-
and 32-byte keys, plus `r = Nr`. 21 distinct
(key length × fmc × round count) cells are generated; they are enumerated with
their task counts in `coverage_boundary.cells_generated`.

A green states only that *these mutants* were detected, and the no-op control
not detected, **by comparisons performed in those cells**. It says nothing about
any other cell, and it is not a certification of `aes_reduced.py` in any cell.

### What a green does NOT cover

Closing one axis does not close the class of coverage escapes. Named gaps, none
of which is claimed safe:

1. **`final_mix_columns=True` at `r = Nr`.** The widening applies to the
   *reduced-round* task set only; every full-round task still has `fmc=False`,
   so no cell `k{16,24,32}_fmc1_rfull` is generated. This gap is **not
   hypothetical**: the ER-6 confirmation table above shows the faulted module
   differing from the pristine one at `k24_fmc1_rfull` and `k32_fmc1_rfull`,
   cells where the module is demonstrably wrong and which the control never
   enters. In the ER-6 run the fault was caught anyway, but only because it
   *also* reached the reduced-round cells. A fault confined to
   (`fmc=True` AND `r = Nr`) would still escape. I did not demonstrate this with
   a confined fault, because adding one would have changed
   `mutation_control_v3.py` after the runs above and forced every run to be
   repeated, exceeding the handoff's `maximum_runs: 8`. It is recorded as an
   identified gap, not as a demonstrated escape.
2. **Decryption.** Only `AES.encrypt_block` is ever called. `decrypt_block`,
   `decrypt_partial`, `unwhiten`, `round_backward`, `inv_shift_rows` and
   `AES_INV_MIX` are never compared against anything. A fault confined to the
   decrypt path is an exact ER-6-shaped escape on this axis.
3. **`r > Nr`.** `aes_reduced.py` explicitly supports round counts above the
   FIPS-197 value; no task generates one, so the extended key schedule and the
   extrapolated round sequence are never compared.
4. **`r = 0` and other degenerate round counts**; **non-default `Components`**
   (`with_random_sbox`, `with_identity_mixcolumns`, …), which no task
   instantiates; **multi-block / ECB** (`encrypt_ecb` is never called); and
   **key/plaintext value space** — faults conditional on a specific key or
   plaintext are untouched by widening `fmc`.

**The honest generalisation is not "the fmc axis is now safe" but "a coverage
boundary that is not written down will be assumed to be wider than it is".**
ER-6 was the H-3 failure shape recurring on a different axis *inside the repair
for H-3*. Items 1–4 are candidates for the same recurrence and none of them is
claimed safe.

---

## 5. D-705-2 — C0 now executes, and passes

The committed `verify_derivation.py` omitted `sys.modules[spec.name] = mod`
before `spec.loader.exec_module(mod)`, so `aes_reduced.py`'s
`from __future__ import annotations` + `@dataclass` combination could not
resolve its own annotations at class creation, the import raised, and claim C0
reported SKIP. This is the same import quirk that produced BATCH-001's original
false green.

`verify_derivation_v2.py` differs from the committed blob by exactly two hunks:
the additive superseding/provenance header required by
protocol-amendment-GOAL-AES-001-002, and this one line —

```diff
         mod = importlib.util.module_from_spec(spec)
+        sys.modules[spec.name] = mod  # D-705-2 fix (TASK-20260801-802): required for @dataclass annotation resolution
         spec.loader.exec_module(mod)  # type: ignore[union-attr]
```

Nothing else was changed: no claim, threshold, seed or PASS condition was
touched.

**Run (RUN-802-1), exit status 0. Verbatim:**

```
CLAIM C0    PASS MixColumns matrix, derived S-box (256/256) and GF(2^8) inverse (256/256) all agree with TASK-20260731-602 aes_reduced.py (module sha256 2c76f3e5db83ec2500ce1010a392a135869d8b9dd1a534af817e06f15babb447)
...
SUMMARY 17 PASS, 0 FAIL, 0 SKIP of 17 claims
```

C0 **executes rather than skipping, and passes**: 17 PASS / 0 FAIL / 0 SKIP,
up from 16 PASS / 0 FAIL / 1 SKIP. The full 17-line output is in the receipt.

**Scope of that pass.** It is agreement between two implementations authored
inside this program on elementary algebraic constants (the MixColumns matrix,
256 S-box entries, 256 GF(2⁸) inverses). It is not an external validation and it
says nothing about AES.

---

## 6. Going further: two NEW escape routes, both false greens

Four escape routes had been found across two batches, each only because somebody
went looking. I looked again, aiming specifically at a **false green** — a
`verdict: pass` on a module I had demonstrably broken — because that is the
dangerous direction. A false negative (ER-5: a mutant hiding its own fault) is
recorded and is less dangerous. I found two.

### ER-7 — the evaluator-name cloak (OPEN, NEW, not repaired)

The control imports every mutant under the fixed module name
`mutant_under_test`, and a module can read its own `__name__`. One line:

```python
_ER7_UNDER_TEST = (__name__ == "mutant_under_test")
```

with the ER-6-class fault gated on `not _ER7_UNDER_TEST`. Under an ordinary
import the module is wrong in the same 4 of 12 cells (independently confirmed by
the same direct ciphertext comparison, which imports under the module's ordinary
name). Under the control it is clean.

**Result (RUN-802-6): `verdict: pass`, all five components true, 212 comparisons
executed per mutant, on a module confirmed broken.** A FALSE GREEN — and
**widening the fmc axis does not prevent it**: the widened cells are generated
and compared, and the module simply presents a correct face inside them. ER-7 is
orthogonal to ER-6 and survives its repair.

This generalises past one string constant. Any mutation control that (a)
executes the module under test and (b) leaves that module *any* observable
signal of being under test — module name, `argv`, cwd, parent process, the
control's own markers in its source — can be shown a different object than a
consumer would see. Randomising `mutant_under_test` per run raises the cost; it
does not remove the class.

### ER-8 — shared-runner tamper across the process boundary (OPEN, NEW, detected but not prevented)

Each mutant subprocess is passed the **shared** runner script's own path as
`sys.argv[0]`, and the scratch directory is writable. The first mutant executed
rewrites that runner at import time; every later mutant subprocess is then run
by a runner that strips the fault out of the module source before
`exec_module`. The no-op control, which runs last, sees a clean module.

**Result (RUN-802-7): `verdict: pass`, all five components true, on a module
confirmed broken in 4 of 12 cells.** A second false green, by a different route.

It is visible at all only because v3 added a runner-integrity check that v2 did
not have: the runner's SHA-256 changed from `d2376d86…68eda` to `819ea4ea…ab0e4`
during the run and `runner_unmodified_during_run` is `false`, where the baseline
run reports the two digests equal.

**What this falsifies, stated precisely.** It falsifies as a *general* statement
v2's isolation claim that a mutant's "residual power is to hide its own fault …,
never to manufacture a detection". Subprocess isolation does protect the
parent's reference ciphertexts, counters and verdict arithmetic — that part held
under every probe run here — but the scratch directory is shared mutable state,
so one mutant can change how a later mutant is executed. Stated fairly: this
**does not** retroactively invalidate any BATCH-002 scored result, all of which
used non-adversarial mutants authored inside the control itself. v3 **detects**
this after the fact and does **not** prevent it; a tamper that also restored the
runner's bytes before exiting would defeat the digest check, and that variant
was not implemented or run — it is an untested conjecture, not a demonstrated
escape.

### What I tried and could NOT break

Recorded because a failed attack is informative:

- **Manufacture `detected: true` from an exception path** (import-time
  `AssertionError`, `AttributeError`, `SystemExit`). Failed. Probes A, B and D
  still score `detected: false` with 0 comparisons and standalone verdict
  `FAIL`. The rule
  `detected := comparisons_executed > 0 and divergences > 0` has no exception
  branch to attack.
- **Manufacture a detection by tampering with the parent's reference oracle**
  (the ER-3 shape). Failed. References are computed in the parent before any
  mutant runs; probe C's tamper stays in its own subprocess.
- **Make the widened set vacuous** — i.e. check whether widening made the
  control fire on everything, which would make the ER-6 "detection" meaningless.
  Failed, which is the wanted outcome: on the pristine module the no-op control
  still scores `detected: false` after 212 comparisons, and probe C still scores
  `no_detection_credited`.
- **Break determinism.** Failed: two invocations, identical digest.
- **Use ER-8 to manufacture a spurious detection for a *later* mutant** (rather
  than hide one). The same vector can evidently write arbitrary content into the
  shared runner, so this looks reachable — but I did not implement or run it, so
  it is recorded as an untested conjecture and **not** as a demonstrated escape.

### Neither ER-7 nor ER-8 is repaired here

Repairing either is a design change to the control that has had no independent
review, and inventing one inside the same artifact that claims a repair is how
ER-6 came to exist in the first place — the repair for H-3 reproduced the H-3
failure shape. Both are recorded, reproducible from the recorded commands, and
left for the Coordinator to scope.

---

## 7. Status of every defect, restated

| defect | status after this task |
|---|---|
| H-1 | CLOSED per DEC-20260731-013 (Coordinator). Re-verified here as still holding under the widened set. No new status asserted. |
| **H-2** | **OPEN, NOT REPAIRED, NOT MITIGATED.** `assert`-based module self-check, stripped by `python3 -O`. Untouched. |
| H-3 | CLOSED per DEC-20260731-013 (Coordinator). Re-verified here as still holding. No new status asserted. |
| **H-4** | **OPEN, NOT REPAIRED, IRREDUCIBLE.** No external reduced-round reference exists or can be obtained here. TARGET-REF establishes SENSITIVITY only. Widening `fmc` does not mitigate it in any degree. |
| **ER-5** | **OPEN, NOT REPAIRED, NOT MITIGATED.** A mutant can still hide its own fault (false negative). |
| ER-6 | Closed **on the (key length × final_mix_columns) axis only**, demonstrated. The class of coverage escapes is NOT closed. |
| **ER-7** | **OPEN, NEW**, found by this task, not repaired. |
| **ER-8** | **OPEN, NEW**, found by this task, detected but not prevented. |

## 8. Budget and runs

7 of the 8 permitted runs were used; all seven are in the receipt with their
commands, exit statuses and timings. **No run was discarded, repeated to obtain a
favourable result, or omitted.** The summed measured wall clock of the executed
commands is well inside the 900 s limit; no budget limit was reached. Checks that
did not run are enumerated with their reasons in
`repair_receipt_v3.json → checks_not_run`, including the one demonstration
(gap 1 of §4) that the run budget did not permit.
