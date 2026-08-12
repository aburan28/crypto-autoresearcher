# CHECK (b) — the ER-6 close-out, the regression suite, the coverage boundary, and D-705-2

TASK-20260801-804 — GOAL-AES-001 BATCH-003 — validator, independent session,
review-adversarial policy.

**VERDICT FOR CHECK (b): `passed`, with TWO MAJOR defects (V-804-4, V-804-5) and
one unresolved conjecture.**
This verdict is for check (b) only. It is physically separate from the check-(a)
verdict in `od1_and_gate_review.md` and must never be merged, averaged or carried
across. The BATCH-002 precedent is applied: a defect in the instrument does not
touch the mathematics of check (a), and check (a)'s soundness does not validate
this repair.

**Independence limitation, stated by me.** SESSION independence only, NOT MODEL
independence, under standing basis `0137a051`. No closure attestation from this
session. **Literature:** none used; any recollection is `unverified-from-memory`.

Everything below is toy-scale instrument testing. It is not evidence about AES.

---

## 1. ER-6: I re-created the fault from my own text and re-injected it

I did not use the producer's `MODULE_FAULTS["er6"]`. I wrote my own
regime-confined fault, **different in both its regime and its wrong value** from
the producer's, into a scratch copy of the committed
`BATCH-001/.../aes_reduced.py` (the committed file was never written):

```python
    def _is_final_round(self, i: int) -> bool:
        if self.final_mix_columns and len(self.key) == 24:
            return i == 1   # VALIDATOR-804 FAULT A (regime-confined to k24 + fmc)
        return i == self.rounds and not self.final_mix_columns
```

**Independent confirmation that the fault is real, by direct ciphertext
comparison** (my own script, ordinary import name, pristine vs faulted, 4 random
vectors per cell over the full 3 key lengths × 2 fmc × {r=4, r=Nr} grid, seed
`80420260801`):

| cell | vectors differing |
|---|---|
| `k24_fmc1_r4` | **4/4** |
| `k24_fmc1_rfull` | **4/4** |
| all other 10 cells | 0/4 |

Fault A is **REAL and confined to (klen=24 ∧ fmc=True)**.

**Methodological trap I hit and record**, because it bears on how anyone confirms
a fault here: my first confirmation used `key = bytes(range(24))`,
`pt = bytes(range(16,32))`. That whitens to the all-`0x10` state, and MixColumns
fixes constant columns (`02⊕03⊕01⊕01 = 01`), so skipping MixColumns at round 1
changed **nothing** and the fault looked non-existent. A single structured test
vector can hide a real fault completely. I switched to multiple random vectors.
This is not a producer defect — it is a caution about single-vector confirmation
that I recommend be carried forward.

**Scored run of the committed control against my fault:**

```
python3 .../BATCH-003/tasks/TASK-20260801-802/mutation_control_v3.py \
    --module <scratch>/aes_faultA.py --repo-root <repo> --out rcpt_A.json
```

- **`verdict: FAIL`** (exit 1).
- `verdict_components.noop_mutant_not_detected: false` — i.e. the failure came
  through the no-op control diverging.
- The detecting row: `NOOP_is_final_round_rewritten`, `status: "compared"`,
  **`comparisons_executed: 212`, `divergences: 24`**, `detected: true`,
  `detection_mechanism: "differential ciphertext comparison …"`.

**Detection occurred through an EXECUTED COMPARISON THAT DIVERGED — 212 executed,
24 divergent — and through no exception path.** `infrastructure_outcome: false`;
`status` is `compared`, not any `*_error`. I re-read `score()` and confirmed the
only route to `detected: true` is `comparisons_executed > 0 AND divergences > 0`;
every error path returns `detected: false` with `infrastructure_outcome: true`.

**Before/after, on my own fault:** the same fault under `--fmc-coverage legacy`
returns **`verdict: pass`** — the exact ER-6 false green. Under the default full
coverage it FAILs. **ER-6 is closed on its axis, confirmed independently.**

---

## 2. Regression and vacuity — the control has not become a detect-everything

Re-run by me on the **pristine committed module**, `verdict: pass`:

- `NOOP_is_final_round_rewritten`: `detected: false`, **`comparisons_executed: 212`,
  `divergences: 0`**, `status: compared_no_divergence`. **Not detected after a
  nonzero number of executed comparisons** — required and confirmed.
- All eight fault mutants detected by comparison, each with 212 comparisons:
  `sbox_transpose_0x53_0x54` (85 div), `shiftrows_offsets_swapped` (212),
  `rcon_off_by_one` (196), `RR1_final_round_mixcolumns_retained` (124),
  `RR2_is_final_round_off_by_one` (124),
  `RR3_encrypt_partial_upper_bound_off_by_one` (212),
  `RR4_final_roundkey_from_untruncated_schedule` (176),
  `RR5_initial_addroundkey_miscounted` (212).
- `every_reduced_round_mutant_detected_at_r_lt_Nr: true`;
  `all_injected_failure_probes_behaved_as_required: true` — the H-1 injection
  shapes still fail closed.
- `runner_integrity`: write-time and post-run SHA-256 of the runner identical.

The widened task set has **not** made the control fire on everything.

---

## 3. Coverage-boundary fidelity (F-8)

I recomputed the boundary by running `mutation_control_v3.py` myself and comparing
its `coverage_boundary` to the `coverage_boundary_D_705_8.boundary` block in the
committed `repair_receipt_v3.json`.

- **Byte-for-byte identical** on `key_length_x_final_mix_columns_task_counts`
  (k16: 52/40, k24: 36/24, k32: 36/24 — six non-empty (klen × fmc) cells,
  `fully_covered: true`), on `cells_generated`, and on
  `n_cells_generated: 25`.
- The boundary statement therefore **matches the task set the code actually
  generates**. D-705-8 does not recur here.
- **Correction to the Coordinator's flag F-8, not to the artifact:** F-8 says "the
  21 enumerated cells". The receipt says **25**, my run produces **25**, and the
  two agree. The 21 is an error in the flag text.
- The "4 of 12 differing cells" claim I corroborated independently by a different
  route: my confirmation table for the producer's ER-6 fault shape
  (`len(key) != 16`) differs in **exactly** `k24_fmc1_r4`, `k24_fmc1_rfull`,
  `k32_fmc1_r4`, `k32_fmc1_rfull` — 4 of 12. ✔
- **`cells_generated` contains no `k*_fmc1_rfull` cell at all.** This is
  load-bearing for §5.

---

## 4. D-705-2 and C0 — my own diff and my own re-run

**Diff** of the committed `verify_derivation_v2.py` against the committed
BATCH-002 `verify_derivation.py` (sha256
`9618f55f82408098ffc54ec5a67cc536562289f1cddae29ef3b80f1e84034951`, which I
recomputed and which matches the value the v2 header cites):

- One added comment block (the superseding header + inference stanza), 44 lines.
- **One added code line**, inside `claim_C0_harness_crosscheck()`:
  `sys.modules[spec.name] = mod  # D-705-2 fix …`
- **Nothing else.** No claim, threshold, seed or PASS condition altered. The
  producer's description is exact.

**My own re-run** of `verify_derivation_v2.py`:

```
SUMMARY 17 PASS, 0 FAIL, 0 SKIP of 17 claims
CLAIM C0    PASS  MixColumns matrix, derived S-box (256/256) and GF(2^8) inverse
                  (256/256) all agree with TASK-20260731-602 aes_reduced.py
                  (module sha256 2c76f3e5…babb447)
```

**C0 now EXECUTES and PASSES.** The claimed 17 PASS / 0 FAIL / 0 SKIP is confirmed
from my own execution. C11 also re-passes (1020 forward-, 1020 reverse-reachable,
strongly connected), consistent with my independent graph work in check (a).

---

## 5. **V-804-4 (MAJOR) — I ran the producer's conjecture (ii) and it IS a false green**

F-6(ii). The producer named but correctly declined to run a fault confined to
`fmc=True ∧ r = Nr`. I am not bound by its `maximum_runs: 8`, so I ran it.

My fault, my own text, into a scratch copy of the committed module:

```python
    def _is_final_round(self, i: int) -> bool:
        if self.final_mix_columns and self.rounds == self.full_rounds:
            return i == max(self.rounds - 1, 1)   # VALIDATOR-804 FAULT B
        return i == self.rounds and not self.final_mix_columns
```

**Confirmed real by direct ciphertext comparison:** differs in `k16_fmc1_rfull`
(4/4), `k24_fmc1_rfull` (4/4), `k32_fmc1_rfull` (4/4); identical in the other nine
cells.

**Control run against it: `verdict: pass`.** Every component green, including
`noop_mutant_not_detected: true`, with 212 comparisons executed per mutant and
zero divergences on the no-op. **A demonstrated FALSE GREEN on the repaired
control, on a module I have independently proved wrong.**

Mechanism, named: `build_tasks()` hard-codes `final_mix_columns: False` on **every**
full-round task, and every reduced-round task has `r < Nr`. So no task in the
generated set ever lands in `(fmc=True ∧ r=Nr)`. The cell is not merely thinly
covered — it is **empty by construction**, which §3 confirms from the code.

This is **the ER-6 shape recurring inside the ER-6 repair, on the adjacent axis of
the same two-factor table.** ER-6 was `fmc × key length`; this is `fmc × regime`.
Severity **major**: it is live in the currently committed instrument.

Mitigating and stated fairly: the producer **predicted this cell in its own 12-cell
confirmation table and named it as an open gap**; the receipt's
`axes_NOT_exercised` and `class_of_escapes_status` explicitly refuse to claim the
class closed. The producer's conduct is correct; the instrument's coverage is not.

---

## 6. **V-804-5 (MAJOR) — ER-7 as a CLASS: I enumerated the signals and exploited a second one**

F-5. The producer found `__name__`. I enumerated what the control leaves
observable to a mutant executing inside the runner subprocess, by reading
`RUNNER_SRC` and `run_isolated()`:

| signal | visible to mutant? | exploitable as an under-test tell? | evidence |
|---|---|---|---|
| `__name__` | yes — runner sets `spec_from_file_location("mutant_under_test", …)` and `sys.modules["mutant_under_test"]` | **YES** | producer's ER-7 |
| `sys.argv[0]` | yes — always the runner path, basename `mutant_runner.py` | **YES — I exploited it** | §6.1 below |
| `sys.argv[1..3]` | yes — module path, `tasks_<tag>.json`, `out_<tag>.json`, all under a `mutation_control_v3_*` temp dir | **YES** (path pattern is a perfect tell) | read from `run_isolated` |
| own file path (`__file__`) | yes — a scratch temp dir, not the repo path | **YES** | read from `run_isolated` |
| cwd | inherited from the parent; `subprocess.run` sets no `cwd` | **weak/environment-dependent**; not probed by me | not run |
| environment variables | fully inherited; `subprocess.run` sets no `env` | **YES in principle** — a mutant can read anything the parent exports; I did not identify a specific control-set variable, so this is a channel, not a demonstrated exploit | not run |
| parent process identity | `os.getppid()`, and `/proc/<ppid>/cmdline` on Linux, which contains the control's own path | **YES in principle**; not probed by me | not run |
| presence/contents of the runner file | yes — `sys.argv[0]` is readable **and writable** | **YES** (this is ER-8's channel) | producer's ER-8 |
| presence of the tasks JSON | yes — a mutant can read `sys.argv[2]` and see the entire task set, including which cells will be compared | **YES, and it is the strongest of all**: a fault can be made to fire only on inputs *not* in the task file | not run |
| `sys.modules` contents / module search path | yes | **YES** | not run |

**The class is wide open. `__name__` is one of at least four immediately
exploitable signals and the runner makes no attempt to close any of them.** The
producer found one instance; the finding for review is that the control's
isolation model gives the mutant an ordinary child process with full visibility of
the harness, so "hide when observed" is available through many independent
channels. Closing them one at a time cannot succeed — see §8.

### 6.1 Demonstrated, not asserted

I built a cloak keyed on **`sys.argv[0]`, not `__name__`**:

```python
_V804_UNDER_TEST = os.path.basename(sys.argv[0]) == 'mutant_runner.py'
```
with the ER-6-class fault (`fmc=True ∧ len(key) != 16`) disabled exactly when that
is true.

- **Confirmed wrong** under ordinary import (my confirmation runner, argv[0] =
  `confirm2.py`): differs in `k24_fmc1_r4`, `k24_fmc1_rfull`, `k32_fmc1_r4`,
  `k32_fmc1_rfull`, 4/4 vectors each.
- **Control verdict: `pass`.** All components green; no-op not detected; 212
  comparisons per mutant. **A second, independent false green of the same class,
  on a module I have proved wrong.**

---

## 7. F-6(i) — the ER-8-restore conjecture: ATTEMPTED, **NOT RESOLVED**. I report this as a null.

I built the variant the producer named: the ER-6-class fault plus an import-time
rewrite of the shared runner (`sys.argv[0]`), with an `atexit` hook that **restores
the runner's original bytes** when the tampering process exits, so any post-run
digest matches.

- Fault confirmed real by ciphertext comparison (4 cells, 4/4 vectors).
- Control verdict: **`FAIL`**.
- `runner_integrity.runner_unmodified_during_run: true`, write-time and post-run
  digests identical.

**I cannot conclude that the restore trick defeats the integrity digest, and I do
not claim it.** My probe was confounded: the base fault I attached the tamper to
is the plain `len(key) != 16` ER-6 shape, which the widened coverage now catches
**regardless** of any runner tampering — the no-op mutant diverged (48 of 212) and
the run FAILed on the first mutant, before the tamper could matter. I also found
no `*.d8.py` artifacts, so I could not confirm the rewrite ever landed. The correct
statement is:

> **The ER-8-restore conjecture is UNRESOLVED. The digest matching after the run is
> consistent both with "the tamper never landed" and with "the tamper landed and was
> perfectly reverted", and my run cannot distinguish them.** A conclusive probe
> needs the tamper attached to a fault the coverage does not otherwise catch — e.g.
> the §5 `(fmc=True ∧ r=Nr)` fault — and needs an in-flight (not post-hoc) digest
> read. I did not have budget to build that. It remains the next thing to run.

This is an absence of evidence, not evidence of absence (AGENTS.md rule 5).

---

## 8. The structural question, ruled on explicitly

The Coordinator's reading is that ER-6 was the H-3 shape recurring inside the H-3
repair, and ER-7/ER-8 are the ER-6 shape recurring inside the ER-6 repair. **My
own results make it a fourth and fifth iteration, not a third:** V-804-4 is the
ER-6 shape recurring inside the ER-6 repair on the adjacent axis of the same
table, and V-804-5 is the ER-7 shape recurring immediately after ER-7 was named,
through a different signal.

**Ruling: yes, this is a strong prior against treating false-green escapes as
closable by enumeration — and it is stronger than an induction over three data
points.** There is a structural reason:

1. Each repair closes a **specific cell** of a coverage table or a **specific
   channel** of an isolation boundary. Both objects are *products of axes*, and
   the repair enumerates one axis while the escape moves to another. The table
   `(key length × fmc × round regime × direction × r>Nr × …)` and the channel set
   (`__name__`, `argv[0]`, `argv[2]`, env, `/proc`, cwd, file system) are each
   **open-ended**. Enumeration against an open-ended set does not converge.
2. The adversary model is **strictly stronger than the instrument**. The mutant is
   an ordinary child process with the harness's own inputs on its command line. Any
   test that runs the object under a distinguishable condition can be evaded by an
   object that reads the condition. This is the standard trusting-trust /
   observer-dependence shape; it is not repairable by adding cells or by adding
   digests, because the added check is itself observable.
3. The measured pattern is therefore what the structure predicts: three repairs,
   five escapes, and **two of my five found within one session and with no
   privileged knowledge**. A defect class whose next instance is cheap to find
   after each repair is not being exhausted.

**Does this raise whether `DEC-20260731-011`'s certification condition — H-1 and
H-3 closed before any reduced-round measurement is certified — is meetable at all
by an instrument of this design? YES, and my answer is: not as an enumeration, and
not by this instrument as designed.** Reasoned view:

- **H-1 (the scoring core) is meetable and looks met.** It is a *closed* property
  of one function: the only path to `detected: true` is `comparisons_executed > 0
  ∧ divergences > 0`, with every error path returning `detected: false` and
  `infrastructure_outcome: true`. I read it and I exercised it; it is verifiable by
  inspection over a finite code path. Nothing in my probes moved it.
- **H-3 (coverage/false-green) is NOT meetable by enumeration.** Closing it
  requires a statement of the form "no fault escapes", quantified over an open
  fault space and an open observation channel set. Every repair so far has
  converted "no fault escapes" into "no fault escapes *on the axes we enumerated*",
  which is a strictly weaker statement that the next probe falsifies.
- **What would change the answer** (offered as analysis, not as an authorised
  design change): replace enumeration with a *closed* argument — e.g. certify the
  module only over a task set the control **derives from the module's own declared
  parameter domain** rather than a hard-coded grid, so that "cell not generated" is
  impossible by construction; and remove the observability channel by making the
  comparison run under conditions **indistinguishable** from ordinary use
  (ordinary module name, ordinary argv, ordinary cwd, no harness-shaped paths),
  so "hide when observed" has nothing to key on. Both are closed properties. Until
  something of that kind exists, a certified reduced-round measurement under
  `DEC-20260731-011` should, in my view, be regarded as **not currently
  attainable**, and the honest statement is that the instrument bounds false
  greens on named axes only.

I emphasise the scope of this view: it is a judgement about instrument design
supported by five escapes across three repairs, two of them measured by me in this
session. It is not a proof of impossibility, and it is not a decision — the
transition is the Coordinator's in TASK-20260801-805.

---

## 9. F-7 — is the ER-8 isolation falsification correctly scoped?

**Partially audited; I state the limit.** I read the nine BATCH-003 `MUTANTS`
specs actually exercised in my runs and none contains a shared-runner tamper or a
name cloak — every one is a pure arithmetic/round-structure perturbation, all
detected by comparison with 212 comparisons each. I did **not** complete a
line-by-line audit of every committed BATCH-002 mutant source within budget.
So: **no evidence that any BATCH-002 scored result could have been affected, and I
found nothing suggestive — but I did not exhaustively confirm it, and I record this
as an incomplete sub-check rather than a pass.**

---

## 10. Manufactured false green of my own devising (asked for explicitly)

Delivered: **V-804-5** (§6.1) is a false green of my own devising, on a channel
none of ER-3..ER-8 covers — `sys.argv[0]` rather than `__name__`. **V-804-4** (§5)
is a second, on a coverage cell none of ER-3..ER-8 covers. Both were confirmed
wrong by independent ciphertext comparison first and then returned `verdict: pass`
from the committed control.

The strongest one I identified but did **not** run, and therefore do not claim: a
mutant that reads `sys.argv[2]` — the tasks JSON the runner is handed — and
disables its fault on exactly the (key, plaintext, rounds, fmc) tuples listed
there. That defeats **any** finite task set, including a corrected one, and it is
immune to widening coverage. Not run; named as the sharpest next probe.

---

## 11. Defects raised in check (b)

| id | severity | statement |
|---|---|---|
| **V-804-4** | **major** | Demonstrated false green: a fault confined to `(fmc=True ∧ r=Nr)` returns `verdict: pass` on the repaired control, on a module I independently proved wrong in 3 cells. `build_tasks()` sets `final_mix_columns=False` on every full-round task, so the cell is empty by construction. ER-6's shape, adjacent axis, live in the committed instrument. Predicted and disclosed by the producer; not repaired. |
| **V-804-5** | **major** | Demonstrated false green: an under-test cloak keyed on `sys.argv[0]` (basename `mutant_runner.py`) rather than `__name__` returns `verdict: pass`. ER-7 is a class, not an instance; I enumerated ≥ 4 immediately exploitable signals and the tasks-JSON channel is stronger still. |
| **V-804-6** | minor | The ER-8-restore conjecture is **unresolved**, not refuted. `runner_unmodified_during_run: true` after my restore-variant run is consistent with both "tamper never landed" and "tamper perfectly reverted"; my probe was confounded because the base fault was caught on the widened axis first. |
| **V-804-7** | informational | F-7's scoping audit is **incomplete** in my session: no line-by-line audit of every BATCH-002 mutant source was completed. No contrary evidence found. |
| **V-804-8** | informational | Single-vector fault confirmation is unsafe here: a structured key/plaintext can whiten to a constant state, on which MixColumns is the identity, hiding a real fault entirely. Recommend multi-vector confirmation as standing practice. |

**What check (b) confirms:** ER-6 is closed on its axis, verified by my own fault
through an executed comparison that diverged (212 executed, 24 divergent, no
exception path); the regression holds (no-op not detected after 212 comparisons;
all eight fault mutants and all H-1 shapes detected); the coverage boundary matches
the code exactly (25 cells, six non-empty (klen × fmc) cells); the D-705-2 change
is exactly one `sys.modules` line plus additive text; and C0 executes and passes,
17 PASS / 0 FAIL / 0 SKIP, from my own run.

**What check (b) does not confirm, and no one should read it as confirming:** that
the class of false-green escapes is closed. It is demonstrably not — I produced two
new ones in this session.
