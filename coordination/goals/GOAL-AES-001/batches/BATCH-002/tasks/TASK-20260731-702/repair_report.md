# Harness repair report — mutation control v2 (H-1, H-3)

Task: TASK-20260731-702 (executor) · Goal: GOAL-AES-001 · Batch: BATCH-002
Handoff: `ledger/handoffs/TASK-20260731-702.yaml`
Artifacts: `mutation_control_v2.py`, `repair_receipt.json`, this file.

**Scope.** This is a report about an *instrument*. It makes no cryptanalytic
claim, proposes no mechanism, assigns no evidence strength, and changes no
official state. Nothing here is a statement about AES at any round count.
Observations are reported; interpretation is the Validator's and the
Coordinator's.

```yaml
inference:
  policy: executor-implementation
  requested_policy: executor-implementation
  resolved_model_id: claude-opus-5
  fallback_used: true
  fallback_reason: >-
    executor-implementation is a GPT-5.6-family policy alias in
    orchestration/model-policies.yaml and cannot be resolved by Claude Code,
    whose subagent frontmatter accepts only Claude models. All subagents in
    .claude/agents/ run `model: inherit`; the substitution is structural and
    expected under this harness.
  degraded_allowed: false
  degraded_requirements: []
  reasoning_effort: null
  independent_session_required: false
  model_verified: false
  model_verified_note: >-
    `python3 -m orchestration.adapter doctor --probe` was NOT run in this task,
    so the resolved model identifier is unverified configuration in the sense
    of AGENTS.md "Model policy".
  standing_basis: >-
    inference-amendment commit 0137a051eb5828789eb267fa83c8278086578d4c.
```

---

## 1. What supersedes what

| new artifact | supersedes | status of the superseded item |
|---|---|---|
| `mutation_control_v2.py` | `BATCH-001/tasks/TASK-20260731-602/run_record.md` :: the `check_detection_power` scoring core of the archived driver (driver sha256 `675ff4d5…4a6d`) | unchanged on disk; still committed; **the BATCH-001 archived green stands as recorded** |
| `repair_receipt.json` | `BATCH-001/tasks/TASK-20260731-602/vector_check_receipt.json` :: the `detection_power_mutation_control` section | unchanged on disk; every other section of that receipt is untouched and **not** superseded |
| — | `BATCH-001/tasks/TASK-20260731-602/aes_reduced.py` | **NOT superseded.** It is the module under mutation and is unchanged. |

**Immutability.** No BATCH-001 artifact was modified, overwritten, deleted, or
re-run into. `aes_reduced.py` was opened read-only from its committed path,
hashed (`2c76f3e5db83ec2500ce1010a392a135869d8b9dd1a534af817e06f15babb447`,
equal to the hash recorded in the BATCH-001 receipt and by the validator), and
mutated only into copies under a scratch `tempfile.mkdtemp()` directory. The
BATCH-001 driver itself was **not executed**; its in-process scoring core was
*replicated* inside `mutation_control_v2.py`
(`legacy_inprocess_replica`) solely to exhibit the escape routes against the
design that admits them. Replica outputs are labelled and contribute nothing to
the v2 verdict.

Working-tree state at run time: commit `98ae8539c9cbb8c3a261ceab83536069c9947253`,
dirty only by this task's own untracked directory
(`?? coordination/goals/GOAL-AES-001/batches/BATCH-002/tasks/`).

---

## 2. The H-1 repair actually implemented

The BATCH-001 scoring had an exception-based detection path:

```python
except AssertionError as exc:
    rows.append({"mutant": name, "status": "rejected_by_module_self_check",
                 "detection_mechanism": "internal assertion in aes_reduced.py",
                 "detail": f"AssertionError: {exc}", "detected": True})
```

That path is **removed entirely**, not narrowed again. `mutation_control_v2.py`
has exactly one route to `detected: true`, and it requires positive evidence
that a comparison ran:

```python
detected = (total_cmp > 0) and (total_div > 0)
```

where `total_cmp` counts (mutant ciphertext, reference ciphertext) pairs that
were both physically produced and compared. Two structural properties make this
unreachable by an exception:

1. **`comparisons_executed` is incremented only inside the comparison loop**,
   once per pair of concrete 16-byte hex strings. No `except` clause anywhere in
   `score()` can increment it; the failure branches hard-code
   `"comparisons_executed": 0, "detected": False, "detection_mechanism": None`
   and set `infrastructure_outcome: true`.
2. **The mutant runs in a separate `python3` subprocess** and returns only
   ciphertext hex. Reference ciphertexts are computed in the parent *before any
   mutant runs*. A mutant cannot reach the counters, the references, or the
   verdict.

Any import-time or run-time failure of the mutant is scored
`status: "mutant_import_error:<ExcClass>"` (or `mutant_encrypt_error:<ExcClass>`,
or `mutant_subprocess_error`), `detected: false`, and drives the overall verdict
to `FAIL` — an infrastructure outcome under AGENTS.md rule 5, never a detection.

---

## 3. Exact commands and real output

All commands run from repo root `/home/user/crypto-autoresearcher`.
`<SCR>` = `/tmp/claude-0/-home-user-crypto-autoresearcher/42d1537b-7158-5124-bdad-0c8e3df17d46/scratchpad`.

**Run 1 — first and only scored execution (no discarded attempts):**

```
$ python3 coordination/goals/GOAL-AES-001/batches/BATCH-002/tasks/TASK-20260731-702/mutation_control_v2.py \
      --out <SCR>/run1.json
EXIT=0        real 0m2.098s   user 0m1.775s   sys 0m0.290s
VERDICT pass
{
 "target_ref_anchored_to_target_ext_at_full_rounds": true,
 "all_fault_mutants_detected_by_comparison": true,
 "noop_mutant_not_detected": true,
 "every_reduced_round_mutant_detected_at_r_lt_Nr": true,
 "all_injected_failure_probes_behaved_as_required": true,
 "unscored_items": []
}
digest1=9bee94dedb259f8642adcf01d36bec6fa4488aec69a1e4e2cf7507129f3947d7
```

**Run 2 — determinism re-run:**

```
$ python3 .../mutation_control_v2.py --out <SCR>/run2.json \
      --prior-digest 9bee94dedb259f8642adcf01d36bec6fa4488aec69a1e4e2cf7507129f3947d7
EXIT=0
digest2 9bee94dedb259f8642adcf01d36bec6fa4488aec69a1e4e2cf7507129f3947d7
match True
verdict pass
```

**Run 3 — canonical receipt-producing execution:**

```
$ python3 coordination/goals/GOAL-AES-001/batches/BATCH-002/tasks/TASK-20260731-702/mutation_control_v2.py \
      --out coordination/goals/GOAL-AES-001/batches/BATCH-002/tasks/TASK-20260731-702/repair_receipt.json \
      --prior-digest 9bee94dedb259f8642adcf01d36bec6fa4488aec69a1e4e2cf7507129f3947d7 \
      --meta <SCR>/meta.json
EXIT=0
verdict pass  digest 9bee94de…47d7  match True
control_source_sha256 d2b2a5dd7720e36b7ff821737d3b7c299254a58f01dd7382bcb67c7a855a00d7
```

Three runs used of a declared maximum of six; wall clock ~2 s per run against a
declared 1500 s budget. **No run was discarded, hidden, or repeated until
favourable.** Between run 2 and run 3 the only source change was the addition of
the `--meta` option (which embeds the author-supplied inference block and run
ledger verbatim under `executor_meta`); it touches no scored quantity, and the
unchanged `results_digest` across runs 1–3 is the check on that statement.
`control_source_sha256` accordingly differs from runs 1–2 while `results_digest`
does not.

Determinism: all randomness is `random.Random` seeded from the four recorded
seeds (`full_round_tasks: 7020260731`, `reduced_round_tasks: 7020260732`,
`legacy_replica_pairs: 7020260733`, and `full_round_tasks ^ 0xA5A5` for the
anchor cases). Re-run is byte-identical on the scored content.

Tool versions, as reported by the tools themselves at run time: Python 3.11.15,
pycryptodome 3.23.0, `openssl version` → OpenSSL 3.0.13 30 Jan 2024,
`gcc -dumpfullversion` → 13.3.0, platform Linux-6.18.5.

---

## 4. H-1 proof obligation — both injected failure shapes

Each probe takes a base source and prepends an import-time injection
immediately before `__all__ = [` at module top level. Full scored output is in
`repair_receipt.json → injected_failure_shape_probes`.

### Probe A — import-time `AssertionError` unrelated to the injected fault (the exact H-1 shape)

Base: the `sbox_transpose_0x53_0x54` mutant (a genuinely faulty module).
Injected source:

```python
# --- probe A injection: import-time AssertionError unrelated to the fault ---
assert False, 'unrelated import-time assertion injected by probeA'
```

Exception actually raised: `AssertionError: unrelated import-time assertion
injected by probeA`.

| scorer | status | detected | comparisons executed | verdict |
|---|---|---|---|---|
| **v2 (this repair)** | `mutant_import_error:AssertionError` | **false** | **0** | **FAIL** |
| BATCH-001 in-process replica | `rejected_by_module_self_check` | true | 0 | pass |

The replica row reproduces defect H-1 exactly as the validator reported it.

### Probe B — import-time non-`AssertionError` (the original false-green shape)

Base: the same faulty mutant. Injected source:

```python
# --- probe B injection: import-time AttributeError ---
_probe_b_trigger = None.__dict__
```

Exception actually raised: `AttributeError: 'NoneType' object has no attribute
'__dict__'` — the exact shape named in the handoff.

| scorer | status | detected | comparisons executed | verdict |
|---|---|---|---|---|
| **v2** | `mutant_import_error:AttributeError` | **false** | **0** | **FAIL** |
| BATCH-001 replica | `driver_import_error` | false | 0 | FAIL |

Both shapes yield `detected: false` with a non-passing verdict under v2, with
zero comparisons executed and `detection_mechanism: null`. **H-1's proof
obligation is met.**

---

## 5. Third (and fourth) escape route — found by this task

I looked for further routes to a green that no comparison earned. Two exist in
the BATCH-001 design and are neither reachable by an `AssertionError` nor closed
by narrowing exception classes; a third is residual and stays open.

### ER-3 — import-time tamper with the scoring process's reference oracle

Because BATCH-001 imports the mutant *into the scoring process*, the mutated
source can rewrite the driver's own reference implementation at import time.
Probe C is a **semantics-preserving** module (unmutated `aes_reduced.py`, cipher
byte-identical) plus:

```python
try:
    from Crypto.Cipher import AES as _tamper_mod
    def _tamper_new(*a, **k):
        class _Fake:
            def encrypt(self, d): return bytes(len(d))
            def decrypt(self, d): return bytes(len(d))
        return _Fake()
    _tamper_mod.new = _tamper_new
except Exception:
    pass
```

| scorer | status | detected | evidence |
|---|---|---|---|
| BATCH-001 replica | `applied` | **true** | 30/30 random pairs "flagged" — a **manufactured detection on a module whose cipher was never changed** |
| **v2** | `compared_no_divergence` | **false** | 164 comparisons executed, 0 divergences (correct: the cipher is unchanged) |

This is a false-green route of a different kind from H-1: not "an exception was
credited", but "the comparison ran and lied". Narrowing exception classes cannot
touch it. v2 closes it by subprocess isolation plus computing all reference
ciphertexts in the parent before any mutant runs.

### ER-4 — `SystemExit` at import escapes `except Exception`

`SystemExit` derives from `BaseException`, so the BATCH-001 loop's
`except Exception` does not catch it. Probe D injects `raise SystemExit(3)` into
a faulty mutant:

| scorer | status | detected | note |
|---|---|---|---|
| BATCH-001 replica | `escaped_scoring_loop` | *null* | `SystemExit: 3` propagates out of the scoring loop; the mutant is never scored at all |
| **v2** | `mutant_import_error:SystemExit` | **false** | isolated runner catches `BaseException`; recorded as an infrastructure outcome, verdict FAIL |

### ER-5 — residual, **open**, not repaired

A mutant retains the power to *hide* its fault, e.g. by tampering with its own
output path inside its subprocess so that correct ciphertexts are emitted. That
direction produces a **false negative** — an undetected mutant, reported as
undetected and driving the verdict to FAIL — never a false green. It is recorded
in the receipt as `ER-5` and is **not** repaired here. A validator probing for a
route that turns a non-comparison into a *detection* should note that under the
isolated design the mutant has no channel to the parent's counters or
references; the remaining attack surface is the runner protocol itself.

---

## 6. H-3 — reduced-round round-structure mutants

Five new mutants perturb reduced-round round-structure logic, plus a
semantics-preserving no-op control. Every mutant is scored **separately** at
`r < Nr` and at `r = Nr`, so a fault caught only at full rounds is visible as
such.

Task sets (identical for every mutant): 36 full-round tasks (12 each at
128/192/256, compared against TARGET-EXT) and 128 reduced-round tasks (128-bit
at r ∈ {1,2,3,4,5} with `final_mix_columns` ∈ {False, True}, 192/256-bit at
r ∈ {1,2,3}, 8 draws per case, compared against TARGET-REF). 164 comparisons per
mutant.

| mutant | perturbed logic | r < Nr: divergences / comparisons | r = Nr: divergences / comparisons | detected | invisible at full rounds |
|---|---|---|---|---|---|
| `RR1_final_round_mixcolumns_retained` | `_is_final_round` → `False`; MixColumns retained in the final round | **88 / 128** (r = 1…5) | 36 / 36 | **true** | no |
| `RR2_is_final_round_off_by_one` | `_is_final_round`: `i == rounds-1` instead of `i == rounds` | **88 / 128** | 36 / 36 | **true** | no |
| `RR3_encrypt_partial_upper_bound_off_by_one` | `encrypt_partial` level range `range(start+1, end)` | **128 / 128** | 36 / 36 | **true** | no |
| `RR4_final_roundkey_from_untruncated_schedule` | round-key indexing at r < Nr: final round uses RK[Nr] of the untruncated schedule instead of RK[r] (a C3 violation) | **128 / 128** | **0 / 36** | **true** | **yes** |
| `RR5_initial_addroundkey_miscounted` | `whiten` applies RK[1] instead of RK[0] (a C2 violation) | **128 / 128** | 36 / 36 | **true** | no |
| `NOOP_is_final_round_rewritten` | `_is_final_round` rewritten to three lines, same boolean function | 0 / 128 | 0 / 36 | **false** | — |

Notes on the numbers, so they are not read as more than they are:

- RR1 and RR2 diverge on 88 of 128 reduced tasks. The 40 non-diverging tasks are
  exactly the `final_mix_columns=True` cases, where the original also keeps
  MixColumns in the last round, so the mutation is a no-op there. That is the
  expected pattern, not a partial miss.
- **RR4 is the mutant that H-3 exists for.** It is invisible at `r = Nr`
  (0/36 divergences, by construction: at r = Nr, RK[Nr] *is* the correct key)
  and diverges on every one of the 128 reduced-round comparisons. A control
  without reduced-round coverage cannot see it at all.
- The no-op mutant executed all 164 comparisons and flagged none: the control
  discriminates rather than firing on any source change.

### What each reduced-round mutant is compared against

Two named targets, used on disjoint task sets:

- **TARGET-EXT** — pycryptodome 3.23.0, used for `r = Nr` tasks only. External
  to this program.
- **TARGET-REF** — `RefAES`, defined inside `mutation_control_v2.py`: a second
  implementation of the documented C1/C2/C3 convention, deliberately structured
  differently from `aes_reduced.py` (S-box from log/antilog tables rather than
  by `GF.inv` exponentiation; MixColumns via `xtime` per row rather than a matrix
  product; Rcon as a literal table rather than a computed power; state as a list
  rather than `bytes`). It is anchored to TARGET-EXT at `r = Nr` before use:
  8/8 agreeing cases at each of 128, 192 and 256 bits.

The unmutated `aes_reduced.py` is **never** used as a comparison target.

**What TARGET-REF establishes:** that a perturbed round structure produces
ciphertexts differing from those of a second, structurally different
implementation of the *same written convention* — i.e. the **sensitivity** of
this control, and prose-to-code agreement between two implementations.

**What it does not establish:** that C1/C2/C3 is correct, standard, or the
convention used anywhere else. `RefAES` was authored in this task, from the same
prose, by the same agent, in the same session. It is not an external reference
and cannot become one. **H-4 — the reduced-round path has no external reference
and cannot obtain one in this environment — stands unchanged and is not claimed
removed.** A green reduced-round row here means "the control fires when the
round structure is perturbed", not "the round structure is correct".

---

## 7. H-2 — RECORDED, NOT REPAIRED

`aes_reduced.py`'s import-time consistency check is an `assert`:

```python
assert mat_mul(AES_MIX, AES_INV_MIX) == IDENTITY_MIX, "AES MixColumns matrices inconsistent"
```

`python3 -O` strips `assert` statements, so **a module with provably
inconsistent MixColumns / inverse-MixColumns matrices imports cleanly under
`-O`**, and the module's only self-check silently vanishes. Consequence: any
process that imports `aes_reduced.py` under `-O` runs with no self-check at all,
and a check whose behaviour depends on an interpreter flag is not a check.

**This task does not repair that, and does not work around it.** It is out of
scope by the handoff and is recorded in `repair_receipt.json → checks_not_run`
as such.

Interaction with the H-1 repair: because the self-check *detection path* is
removed, H-2 can no longer produce a false green **in this control** — a mutant
whose MixColumns matrices are inconsistent must now be caught by an actual
ciphertext comparison, with or without `-O`. That narrows H-2's practical impact
in this one place. **H-2 IS NOT CLOSED.**

Similarly, **H-4 is not repaired and not claimed removed** (§6), and **ER-5**
(§5) remains open by design.

---

## 8. Verdict of this run, and what it is not

`repair_receipt.json → verdict: "pass"`, from five components all true:
TARGET-REF anchored to TARGET-EXT at full rounds; all eight fault mutants
detected by comparison; the no-op mutant not detected; every reduced-round
mutant detected at `r < Nr`; all four injected-failure probes behaved as
required; and `unscored_items: []` (no mutant or probe failed to be scored).

That verdict is a statement about an instrument's detection power against the
mutants and probes actually run, under the seeds and comparison targets
actually recorded, and nothing else. It certifies no cryptanalytic measurement,
supports no claim about AES at any round count, and assigns no evidence
strength. Whether it closes H-1 and H-3 is the Validator's judgement, not mine;
TASK-20260731-705 is directed to re-inject both H-1 shapes independently and to
hunt for a further escape.
