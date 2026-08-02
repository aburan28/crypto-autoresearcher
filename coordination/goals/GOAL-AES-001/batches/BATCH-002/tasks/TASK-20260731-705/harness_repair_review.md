# Check (b) — harness repair closing H-1 and H-3 (TASK-20260731-702)

**Independent validation, TASK-20260731-705. Verdict for check (b) only.**
This file carries ONE verdict. A sound derivation note (check (a)) does not
validate this repair, and a defect here does not touch the gate run (check (c)).

| field | value |
|---|---|
| Reviewed revision | `ebac9ba8` (snapshot, TASK-20260731-704) |
| Artifacts | `mutation_control_v2.py` (`d2b2a5dd…`), `repair_receipt.json`, `repair_report.md` |
| **Verdict (b)** | **passed, with a new open escape route recorded (ER-6)** |
| Official state changed | none. No evidence strength assigned. |

---

## 1. What I executed

I did not accept the repair on the strength of `repair_report.md`. From the
committed source:

1. Re-ran the whole control against the committed BATCH-001 harness:
   `python3 mutation_control_v2.py --module …/aes_reduced.py --repo-root
   /home/user/crypto-autoresearcher --out my_receipt.json`, exit 0, 2.0 s,
   stderr 0 bytes.
   **`results_digest = 9bee94dedb259f8642adcf01d36bec6fa4488aec69a1e4e2cf7507129f3947d7`
   — byte-identical to the producer's recorded digest.** The receipt's own
   `control_source_sha256` recomputes to `d2b2a5dd…`, matching the snapshot
   manifest.
2. Wrote my own probe driver (`val_probes.py`) that imports the control module,
   builds its task set, computes reference ciphertexts in the parent, and then
   drives `run_isolated` + `score` on modules **I** faulted, with **my own**
   injection text.
3. Built a deliberately faulty `aes_reduced.py` and ran the full control
   against it, to try to manufacture a false GREEN.

---

## 2. My own re-injection of the two H-1 failure shapes

Injected at module top level immediately before `__all__ = [`, into the
committed harness source, using my own text (not the producer's probe strings):

| my probe | shape | scored status | `detected` | `detection_mechanism` | comparisons | divergences |
|---|---|---|---|---|---|---|
| `VAL_A_assertionerror` | `assert 1 == 2, 'validator-705 unrelated import assertion'` — **import-time AssertionError unrelated to any fault**, the exact H-1 shape | `mutant_import_error:AssertionError` | **False** | `null` | 0 | 0 |
| `VAL_B_zerodivision` | `_v705 = 1/0` — **import-time non-AssertionError**, my own choice of class | `mutant_import_error:ZeroDivisionError` | **False** | `null` | 0 | 0 |

Both H-1 shapes are scored `detected: false` with a null detection mechanism
and zero comparisons executed. **Neither is credited as a detection.** In the
full control run these are classified as infrastructure outcomes and the
standalone verdict is non-passing (`FAIL` / `no_detection_credited` per the
mutant's declared `expected_standalone_verdict`), consistent with AGENTS.md
rule 5 — a control that could not run is not a result.

I re-injected the producer's exact AttributeError shape as well, and two shapes
they did not test:

| my probe | shape | scored status | `detected` |
|---|---|---|---|
| `VAL_B2_attributeerror` | `None.__dict__` (their exact text, independently injected) | `mutant_import_error:AttributeError` | **False** |
| `VAL_E_keyboardinterrupt` | `raise KeyboardInterrupt` — a `BaseException` that is **not** `SystemExit` | `mutant_import_error:KeyboardInterrupt` | **False** |
| `VAL_F_osexit0` | `os._exit(0)` — process dies with exit code 0 and never writes the output file | `mutant_subprocess_error:SubprocessFailure` | **False** |
| `VAL_G_forged_output` | mutant forges the runner's JSON output file and `os._exit(0)`s before the cipher runs | `mutant_output_arity_mismatch` | **False** |

Every shape **fails closed**. I could not find a route by which a module that
never produced a ciphertext is credited with a detection. The repair's stated
mechanism holds under inspection as well as under test: `score()` computes
`detected = (total_cmp > 0) and (total_div > 0)` and there is no other
assignment of `detected: true` in the file; the self-check detection path was
removed rather than narrowed, which is why exception-class probes cannot reach
it at all.

`VAL_G` deserves a note: had the forged file carried the *correct* arity and
*correct* ciphertexts, the mutant would score `detected: false` — a false
negative, i.e. the ER-5 family the producer already recorded as open. It would
not manufacture a green.

---

## 3. Third escape route — my own attempt to manufacture a false GREEN

The producer found ER-3 (semantics-preserving oracle monkeypatch, 30/30 falsely
detected under the BATCH-001 control) and ER-4 (`SystemExit` escaping
`except Exception`), and left ER-5 open. Both ER-3 and ER-4 reproduce as
`detected: false` in my run. I looked for a different one.

Manufacturing a false green cannot be done from the mutant side: every mutant-
side trick I tried moves the verdict toward `FAIL`, because the control's green
requires *positive* comparison evidence for each fault mutant. So I attacked
the other end — **what the green certifies about the module it is run on**.

### ER-6 (found by this validator): a fault in a regime the task set never generates

`build_tasks()` generates reduced-round tasks over
`for klen in (16,24,32): for r in REDUCED_ROUND_COUNTS[klen]: for fmc in
(False, True) if klen == 16 else (False,)`. The `final_mix_columns=True`
variant is therefore **only ever exercised with 16-byte keys**. I injected into
`aes_reduced.py` a fault active exactly in the complementary regime:

```python
        if self.final_mix_columns and len(self.key) != 16:
            return i == max(self.rounds - 1, 1)   # VALIDATOR-INJECTED FAULT (ER-6 probe)
        return i == self.rounds and not self.final_mix_columns
```

Confirmed the fault is real and regime-confined by direct comparison against
the unmodified module:

| key length | rounds | `final_mix_columns` | ciphertext differs? |
|---|---|---|---|
| 24 | 4 | **True** | **YES — module is wrong here** |
| 24 | 4 | False | no |
| 24 | full | False | no |
| 16 | 4 | True | no |
| 16 | 4 | False | no |
| 16 | full | False | no |

Ran the full control against that faulted module:

```
VERDICT: pass
  target_ref_anchored_to_target_ext_at_full_rounds : true
  all_fault_mutants_detected_by_comparison         : true
  noop_mutant_not_detected                         : true
  every_reduced_round_mutant_detected_at_r_lt_Nr   : true
  all_injected_failure_probes_behaved_as_required  : true
```

**A demonstrably broken `aes_reduced.py` earns a full green.** This is a
coverage escape, not a scoring bug: the control's five components are all
statements about mutant detection, and every one of them is true. But it is the
*same failure shape as H-3* — a bug living in a regime the comparison never
enters — recurring on a different axis inside the repair that closes H-3.

Recorded as **ER-6, OPEN**, severity **medium**. I did not repair it. The
cheap fix, for whoever owns it, is one line in `build_tasks()`: generate
`fmc ∈ {False, True}` for all three key lengths.

Scope of the finding, stated fairly: the receipt's `scope_statement` is
"INSTRUMENT ONLY", and the control is a *mutation* control, not a certification
of `aes_reduced.py`. ER-6 does not falsify anything the receipt claims. It does
bound what a green means, and that bound is not currently written down.

Two further escapes I probed and could **not** open:
- Timeout/kill of the isolated runner: `run_isolated` treats a nonzero return
  code or a missing output file as `SubprocessFailure` → `detected: false`
  (verified by `VAL_F`). No detection is manufactured.
- Unapplied source edits: an edit whose anchor string does not match cannot
  silently pass, because the mutant then equals the original and yields zero
  divergences → `detected: false` against `expected_detected: true` → the
  verdict component fails. Fails safe.

---

## 4. H-3 — per-mutant confirmation that detection happened at `r < Nr`

From my own receipt, the eight fault mutants and the no-op control (164
comparisons each: 128 reduced-round tasks + 36 full-round tasks):

| # | class | `detected` | at `r < Nr` | at `r = Nr` | divergences / 164 |
|---|---|---|---|---|---|
| 1 | component (BATCH-001 continuity) | true | yes | yes | 79 |
| 2 | component | true | yes | yes | 164 |
| 3 | component | true | yes | yes | 156 |
| 4 | `RR1_final_round_mixcolumns_retained` | true | **yes** | yes | 124 |
| 5 | `RR2_is_final_round_off_by_one` | true | **yes** | yes | 124 |
| 6 | `RR3_encrypt_partial_upper_bound_off_by_one` | true | **yes** | yes | 164 |
| 7 | **`RR4_final_roundkey_from_untruncated_schedule`** | true | **yes** | **NO** | **128** |
| 8 | `RR5_initial_addroundkey_miscounted` | true | **yes** | yes | 164 |
| 9 | `NOOP_is_final_round_rewritten` | **false** | no | no | **0** |

**`every_reduced_round_mutant_detected_at_r_lt_Nr: true`** in my run, and the
per-regime split is recorded per mutant rather than aggregated, so the claim is
checkable rather than asserted.

**RR4 confirms the H-3 claim exactly.** It diverges on **128 of 128** tasks at
`r < Nr` and **0 of 36** at `r = Nr`, and the scorer flags
`invisible_at_full_rounds: true`. This is the whole point of the H-3 repair:
BATCH-001 compared only at full rounds and would have scored this mutant
undetected. Reading the edit confirms the construction is honest — the mutant
expands the schedule to `max(self.rounds, self.full_rounds) + 1` and uses
`round_keys[full_rounds]` for the last round, which coincides with the correct
key precisely when `rounds == full_rounds`. It is invisible at full rounds
**by construction**, not by luck.

**The no-op control genuinely scores undetected.** `NOOP_is_final_round_rewritten`
rewrites `_is_final_round` into three lines computing the same boolean, and
scores `status: compared_no_divergence`, `detected: false`, 164 comparisons
executed, 0 divergences. That is the right shape: the comparison *ran* (164
comparisons, so this is not a silent skip masquerading as a pass) and found
nothing. Without this control the green would be unfalsifiable — a scorer that
said "detected" for everything would also show
`all_fault_mutants_detected: true`. It does discriminate.

---

## 5. Is `RefAES` independent enough? — honest assessment

The reduced-round mutants are compared against **TARGET-REF = `RefAES`, a
second implementation written inside `mutation_control_v2.py` by the same
agent, in the same task, from the same prose convention**. Full-round tasks use
TARGET-EXT = pycryptodome, which is genuinely external.

**My assessment: it establishes SENSITIVITY, and nothing stronger.** It is
circular with respect to *convention correctness* and cannot be otherwise in
this environment. Concretely:

- What it does establish: the control's comparison machinery reacts to
  round-structure perturbation at `r < Nr`; and two structurally different
  implementations (log/antilog vs. table S-box, `xtime` vs. matrix MixColumns,
  list vs. bytes state) of the *same written convention* agree. That rules out a
  class of transcription slips in either implementation.
- What it does **not** establish: that conventions C1/C2/C3 are correct,
  standard, or the ones used anywhere else. A shared misreading of the prose by
  the one agent that wrote both implementations is invisible to this comparison.
- The anchoring to TARGET-EXT at `r = Nr` across all three key sizes bounds the
  circularity but does not remove it, because every convention question at issue
  is one that *vanishes* at `r = Nr`.

**The producer says exactly this, unprompted.** `comparison_targets.TARGET-REF`
carries a `does_not_establish` field reading "that the C1/C2/C3 convention is
correct, standard, or the one used anywhere else. RefAES was authored in this
task from the same prose by the same agent and is NOT an external reference",
and `repair_report.md` §6 repeats it. I checked for an overclaim and did not
find one. The circularity is real; it is disclosed at the point of use rather
than buried; and it is exactly what defect **H-4** names.

One structural mitigation worth recording in the repair's favour: because RR1,
RR2, RR3, RR4 and RR5 each perturb a *different* truncation-convention axis
(final-round MixColumns, round indexing, loop bound, final round key, whitening
key), a shared misreading on any of those five axes would show up as an
undetected mutant and fail the green. The circularity therefore bites only on
axes no RR mutant covers — which is exactly where ER-6 lives.

---

## 6. H-2 and H-4 — correctly recorded as open

Verified in the committed artifacts, in my own regenerated receipt, and in the
report:

- **H-2** — `H2_status` (verbatim): "RECORDED, NOT REPAIRED. `aes_reduced.py`'s
  import-time consistency check is an `assert` and is stripped by `python3 -O`.
  Removing the self-check DETECTION path means H-2 can no longer produce a false
  green in this control, but the module-level weakness is unchanged and **H-2 IS
  NOT CLOSED**." `checks_not_run` separately lists the H-2 repair as out of
  scope by handoff. **Not quietly closed.** The distinction drawn — the false-
  green *route* through H-2 is gone, the *weakness* is not — is precise and I
  agree with it.
- **H-4** — `comparison_targets.H4_status` (verbatim): "H-4 (no external
  reference exists for `r < Nr`) **STANDS AND IS NOT CLAIMED REMOVED**."
  `checks_not_run` records the missing external reduced-round reference and the
  unreachable NIST CAVP vectors, with reasons. **Not quietly closed.**
- **ER-5** is likewise carried as `open by design; recorded, not repaired`.

I searched all three artifacts for any sentence claiming H-2 or H-4 closed,
removed, mitigated or superseded, and found none.

---

## 7. No BATCH-001 artifact was modified in place

`git diff --name-status 98ae8539 ebac9ba8` shows ten paths, all `A` (added),
none under `batches/BATCH-001/`. The control's docstring states it "supersedes
— it does NOT modify" the BATCH-001 control, and the BATCH-001 scoring core is
*replicated* in `legacy_inprocess_replica()` rather than re-run, solely to
exhibit ER-3/ER-4. `checks_not_run` records that the BATCH-001 driver was not
re-executed and why. `--module` is read-only in every code path I traced.
My own runs used copies in scratch; I edited no repository artifact.
**Confirmed: no in-place modification.**

---

## 8. Defects from check (b)

| id | severity | statement |
|---|---|---|
| ER-6 / D-705-7 | medium | **New escape route, found by this validator.** The control returns `verdict: pass` with all five components true on an `aes_reduced.py` that is demonstrably wrong for `final_mix_columns=True` with 24- or 32-byte keys, because `build_tasks()` only generates `fmc=True` for 16-byte keys. Same failure shape as H-3, on an uncovered axis. Coverage hole, not a scoring bug; open, not repaired. |
| D-705-8 | low | Neither `repair_receipt.json` nor `repair_report.md` states the `(key length × final_mix_columns)` coverage boundary of the task set, so a reader cannot see from the artifacts which regimes a green does and does not cover. `checks_not_run` covers other boundaries carefully; this one is missing. |
| D-704-1 (referred) | low | `mutation_control_v2.py` carries no per-artifact inference block. Ruling in `validation_report.yaml`. |

---

## 9. Verdict for check (b)

**passed, with a new open escape route recorded (ER-6).**

- The receipt **reproduces bit-for-bit** from committed source
  (`results_digest 9bee94de…`).
- **H-1 is genuinely closed, not narrowed.** Both failure shapes, re-injected by
  me with my own text, score `detected: false` with a null mechanism and zero
  comparisons; four further shapes of my own devising (ZeroDivisionError,
  KeyboardInterrupt, `os._exit(0)`, forged output file) also fail closed. The
  repair removes the self-check detection path rather than enumerating exception
  classes, which is why exception-class probes cannot reach it.
- **H-3 is closed as claimed.** Every reduced-round mutant is detected by a
  comparison performed at `r < Nr`; RR4 diverges 128/128 at `r < Nr` and 0/36 at
  `r = Nr` and is flagged `invisible_at_full_rounds`; the semantics-preserving
  no-op scores `detected: false` after 164 executed comparisons, so the green
  discriminates.
- **TARGET-REF establishes SENSITIVITY only**, and the artifacts say so
  themselves; the circularity is real, disclosed, and is precisely defect H-4.
- **H-2 and H-4 are correctly recorded as open**, as is ER-5.
- **ER-6 is new and open**: a green does not certify the module in regimes the
  task set never generates.

I change no official state and assign no evidence strength.
