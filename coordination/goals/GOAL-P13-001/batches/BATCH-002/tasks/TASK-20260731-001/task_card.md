# TASK-20260731-001 — Executor — NC-2 per-entry cost calibration (EXP-SSI-002)

**Goal** GOAL-P13-001 · **Batch** BATCH-002 · **Role** executor · **Priority** 100
**Depends on** (nothing) · **Archived by** TASK-20260731-002
**Budget** 5400 s wall clock · 4 GB · maximum_runs 1

> **The queue governs.** This card is a readable mirror of the `handoff` block in
> `coordination/goals/GOAL-P13-001/batches/BATCH-002/dispatch_queue.json` and of
> the frozen contract `experiments/EXP-SSI-002/specification.yaml`. Where this
> card and either of those differ in substance, **the queue and the contract
> govern** and the difference is a defect to report.

---

## Why this card exists

`DEC-20260724-016` records that the **NIST-I concrete margin (2.3 bits) is
smaller than the cost model's own irreproducibility band (3.51 bits)**, so
neither "threatened" nor "safe" is an honest official position. It names the
deciding measurement: **the per-entry table construction cost of Algorithm 1**.
That is control NC-2, priority `highest`. This card is NC-2.

No record in this program currently contains a measured per-entry cost for this
algorithm at any `p`.

## The methodological point that decides whether this card is worth anything

**An exponent cannot be identified from a single `p`.** NC-2's own wording says
"at p ~ 2^40". A single prime yields one cost number, not an exponent. The
approved contract therefore **widens NC-2 to a sweep**, and a single-`p`
measurement is not an acceptable substitute for any reason, including budget.

## What to do

1. Capture `sage --version` **verbatim** before the first computation, into
   `runs/RUN-SSI-002/sage_version.txt`. Sage 10.9 is at `/usr/local/bin/sage`
   and **must be invoked through the `sage` binary, never as a Python import** —
   `import sage` from system `python3` **fails on this host**.
2. **Compute** eight primes at `log2 p ∈ {20, 23, 26, 29, 32, 35, 38, 40}` by
   the contract's rule (largest prime below `2^k` with `p ≡ 3 mod 4`). Record
   rejection counts. **Verify** `E0.is_supersingular()` at each.
3. Run the **34 mandatory cells**: 8 primes × 3 `B` settings (B-ASY, B-FIX-8,
   B-FIX-32) × V-1 × SEED-A = 24; plus 8 primes × B-FIX-8 × V-2 × SEED-A = 8;
   plus 2 SEED-B cells at `k = 20` and `k = 40`.
4. **Charge everything** in the timed window: Φ_ℓ evaluation, **root finding**,
   the non-backtracking filter, and the table insertion — and report each of the
   four separately. Memory beside time for every cell. Sage startup **excluded**
   and reported as `sage_startup_seconds`. Precomputation (Φ_ℓ retrieval)
   reported **both amortised and fully charged**, with **both fits**.
5. Run the five controls and report every gate verdict: **CTRL-CAL** (F_{p^2}
   mul/inv and an empty loop, at every prime, **interleaved not blocked**, with
   its own fit), **CTRL-NULL** (fixed-buffer SHA-256, fixed-key dict ops, with
   their own fits), **CTRL-DRIFT** (start/end re-measurement at the extremes,
   round-robin cell ordering, wall and CPU time recorded separately),
   **CTRL-COUNT** (realised `#L` against the Lemma 3.2 upper and Section 4.1
   lower bounds, plus 50 ℓ-isogeny spot checks per cell), **CTRL-DET**
   (determinism re-execution against entry counts, table sizes, and j-invariant
   **sets**). Plus the **MIX-1** per-ℓ breakdown as a named table.
6. **Fit** M-A, M-B and the null M-0, with **both** the t-interval and the
   2000-resample bootstrap interval, and **carry the wider one**. Report the
   **full signed residual per prime**, the residual sign-pattern string, the
   regressor collinearity, and the GOF-1 / GOF-2 / GOF-3 verdicts.
7. Run the mandatory **FIT-ELL** isolated-ℓ fits (ℓ = 2 alone, ℓ = 3 alone) and
   compare against the pooled fit.
8. Evaluate the stability gates **ST-B**, **ST-V**, **ST-SEED**, **ST-NORM**.
9. Compute the extrapolation **by substitution into the committed, unmodified**
   `experiments/EXP-P13VOW-001/cost_model.py`, and solve `c_star` with that same
   model. **No margin arithmetic by hand anywhere.**
10. Evaluate the pre-registered reading **mechanically**, naming every
    contributing gate. `READING-NOT-IDENTIFIED` takes precedence.

## GAP-1 — handled explicitly, not by you silently

Algorithm 1 **never seeds the list**. Line 1 sets `L ← ∅`; line 4 iterates over
`ψ ∈ L`; the body is unreachable and the algorithm as published returns the
empty list for every input. **It cannot be run.**

Two strategies are **pre-registered in the contract**:

- **SEED-A** (`L ← {(E, id_E)}`) — **PRIMARY** for every fit.
- **SEED-B** (identity plus the first ℓ_min layer, built outside the timed
  window) — **VARIANT** at `k = 20` and `k = 40`, B-FIX-8, V-1 only.

Name the strategy in **every** cell record. Charge and report `seed_seconds`.
Report the SEED-A/SEED-B per-entry ratio and the SEED-GATE verdict.
**No SEED-B slope is reported as a fitted exponent** — two points cannot support
a slope with an interval. **Do not invent a third strategy.** **Do not describe
the seeding as a repair of GAP-1** — GAP-1 stays open.

## Hard prohibitions

- **No bare `c` anywhere.** Every reported `c` carries its interval, its full
  signed residuals and its goodness-of-fit verdict *in the same structure*.
- **`p ~ 2^40` is not cryptographic size.** No artifact may state or imply that
  the NIST-I margin has been measured. Every NIST-I/III/V figure is labelled
  **EXTRAPOLATION** with EA-1..EA-6 attached, and **EA-3** (the measured `B`
  regime never reaches the operating `B`) must appear *beside* every such figure,
  not only in a limitations list.
- **Heuristic 1 is not under test.** Nothing here validates, supports, weakens
  or refutes it.
- **GAP-2 and the Section 4.1 unverifiability are carried, not repaired.**
- Do **not** modify `specification.yaml` or `derivation_note.md`. They are the
  pre-registration and they are committed before you run.
- Do **not** read, edit or stage anything under `experiments/EXP-ISO-001/` — it
  belongs to an unrelated line of work.
- Write nothing outside `experiments/EXP-SSI-002/`. **Make no commit.**
- Write **no** interpretation, disposition, recommendation or hypothesis-status
  opinion. Those belong to the reviews and the Coordinator.
- **Never fabricate** a command, output, timing, statistic, prime or run.
  Missing data stays missing and is reported as missing.

## Budget and infrastructure

Caps: **120 s per cell**, **600 s per prime**, 300 s CTRL-CAL, 180 s CTRL-NULL,
360 s drift+determinism, 300 s fit, **5400 s total**, **4 GB**, 8 MiB per file /
32 MiB per run directory. **Mandatory pre-flight disk check before the first
write** — below 5 GiB free, stop and report and write nothing.

**Every budget breach and every Sage failure is INFRASTRUCTURE SIGNAL**, recorded
with a terminal status and an `invalid_reason`. It is never a measurement, never
a negative mathematical result, and is never fed to any pre-registered reading.

## Deliverables (13 paths — write all of them even for a partial card)

```
experiments/EXP-SSI-002/calibration_probe.py
experiments/EXP-SSI-002/fit_analysis.py
experiments/EXP-SSI-002/runs/RUN-SSI-002/manifest.yaml
experiments/EXP-SSI-002/runs/RUN-SSI-002/raw-timings.json
experiments/EXP-SSI-002/runs/RUN-SSI-002/summary.json
experiments/EXP-SSI-002/runs/RUN-SSI-002/fit_report.json
experiments/EXP-SSI-002/runs/RUN-SSI-002/controls.json
experiments/EXP-SSI-002/runs/RUN-SSI-002/execution_report.yaml
experiments/EXP-SSI-002/runs/RUN-SSI-002/sage_version.txt
experiments/EXP-SSI-002/runs/RUN-SSI-002/command.txt
experiments/EXP-SSI-002/runs/RUN-SSI-002/environment.json
experiments/EXP-SSI-002/runs/RUN-SSI-002/stdout.txt
experiments/EXP-SSI-002/runs/RUN-SSI-002/stderr.txt
```

`fit_analysis.py` **must recompute every fitted quantity from
`raw-timings.json` alone**, so an independent session can rerun it without
re-executing any Sage computation.

## Completion gate

G1–G14 as stated in the queue's `handoff.completion_gate` for this task.
