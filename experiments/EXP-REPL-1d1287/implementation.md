# EXP-REPL-1d1287 -- Implementation Notes

## Status at time of writing

Execution is a **budget-scoped pilot**, not the full frozen design. The
frozen specification's own combinatorics (3 capacities x 2 architectures x
2 curve sizes x 2 split modes x 3 real presentations x 5 seeds, plus a
matched scrambled-arm run per non-presentation combo per seed) requires
**480 training runs** at minimum for the primary measurement alone, before
any of controls C2/C3. This **exceeds** the spec's own declared
`maximum_runs: 400` (and the handoff's identical figure). This tension is
recorded as an observation for the Coordinator, not resolved unilaterally.

Independently, the session's actual compute environment (single CPU-only
machine, 14 cores, no GPU -- `torch.cuda.is_available() == False`) cannot
execute the spec's declared `total_gpu_hours: 60` design at all; the spec's
budget block assumes GPU-hours that do not exist in this execution
environment. This is reported explicitly rather than silently worked
around.

## Deviations from the frozen specification (all recorded, none silent)

1. **Curve sizes reduced.** The spec requires prime-order subgroups of
   2^20 and 2^28. This pilot uses 2^12 (4096) and 2^16 (65536) instead.
   Reason: constructing a curve with an EXACT power-of-two subgroup order,
   deterministically, in this harness, requires full O(p) point-counting
   (a vectorised Legendre-symbol scan) to locate a curve/prime pair with
   the right group order and to certify a generator of exactly that order.
   This is tractable at p ~ 10^4-10^5 but not at p ~ 2^20-2^28 without a
   Schoof-class point-counting algorithm, which was not implemented in the
   time available. **This changes the realized 5-sigma detectable-advantage
   thresholds** from the spec's stated 0.004 / 0.007 to values computed
   from the actually-used held-out sizes (reported per cell in
   `curves.json`-derived splits and in the per-run manifests; see
   `execution-report.md` for the realized SE / 5-sigma-threshold table).
   Dataset generation itself (sampling k -> kP) does NOT scale with N in
   this design (scalar multiplication is O(log N) regardless of table
   size), so the curve-size reduction was purely to make GROUP CONSTRUCTION
   tractable, not dataset generation.

2. **Grid coverage trimmed to fit `maximum_runs: 400`.** Priority order,
   fixed before any run:
   - curve_1 (2^12): FULL grid -- both architectures, both split modes, all
     3 capacities, all 3 real presentations, 5 seeds each, plus matched
     scrambled arm.
   - curve_2 (2^16): architecture = MLP only. Both split modes, all 3
     capacities, all 3 real presentations, 5 seeds, plus matched scrambled
     arm. **Transformer at curve_2 was NOT run.** This is named explicitly,
     per the stopping rule "stop at the run/GPU-hour cap, reporting
     completed cells and naming incomplete ones."
   - C2 (shuffled labels) and C3 (planted leaky): run at curve_1,
     random_by_logarithm split only, both architectures, all 3 capacities,
     1 seed each (reduced from the ad-hoc 2 seeds originally planned) --
     sufficient to check the blocking pass/fail criteria (chance-within-3SE
     for C2; >=0.10 advantage for C3) without spending run budget the
     primary matched-cell measurement needs more.
   This yields ~372 total training runs, under the 400 cap.

3. **Held-out / early-stop / train fractions.** The spec's absolute
   held-out sizes (>=4e5 at 2^20, >=1e6 at 2^28) do not transfer to the
   reduced curve sizes (they would exceed the group size). This pilot uses
   fixed fractions of each reduced curve's full group: train 60%,
   early-stop 10%, held-out 30%. Realized held-out sizes: curve_1 = 1229,
   curve_2 = 19661 examples (curve_2's training set is additionally capped
   at 6000 examples per run for wall-clock reasons -- `max_train=6000` --
   recorded per-run in `raw-result.json` as `n_train_used` vs
   `n_train_full`; this is itself a deviation, since the full 39321-example
   training split is not used for curve_2, and is disclosed rather than
   silently applied).

4. **Presentation encodings.** Coordinates are represented as fixed-width
   hex (4-bit) limb sequences (ceil(bits_p/4) limbs per coordinate).
   `affine_xy_limbs` = x-limbs ++ y-limbs. `x_only_limbs` = x-limbs only.
   `projective_jacobian_limbs` = X,Y,Z limbs of a FIXED (per-k, deterministic,
   not per-training-seed) random Jacobian representative -- fixed so the
   dataset is identical across training seeds, matching the "identical...
   preprocessing" requirement for pairing. `scrambled_labels` (the null) is
   HMAC-SHA256-derived pseudorandom limbs of the SAME length as
   `affine_xy_limbs`, keyed by a fixed PRF key recorded in `code/ec.py`
   (`PRF_KEY`) and mixed with the curve name and k -- a deterministic
   function of k only, carrying no algebraic/group-law structure.

5. **C3 planted-leaky-encoding construction.** The spec requires "4 bits of
   k XORed into low bits of the label" reaching >=0.10 advantage. This
   pilot instead OVERWRITES (not XORs) the last x-limb of the affine
   encoding with the top 4 bits of k directly (which fully determine the
   MSB target). This is a stronger leak than a 4-bit XOR would produce and
   is intentional: it gives an unambiguous, easily-verified pass/fail for
   the blocking control within the epoch budget used. Deviation recorded;
   the control's function (a pipeline sanity check, not a scientific
   measurement) is unaffected by using overwrite instead of XOR.

6. **C5 table-attack reproduction is classical Shanks BSGS**
   (S = T = O(sqrt(N)), S*T = N), not a Hellman/distinguished-point table
   tuned to saturate the S*T^2 = Omega(N) Corrigan-Gibbs-Kogan bound. BSGS
   is a legitimate, exactly-verified precomputation/online tradeoff and
   gives a real measured (S,T) point for the frontier plot, but it does
   NOT saturate the tighter bound (S*T^2 = N^1.5 for BSGS, not N) -- so the
   reproduced attack sits strictly above/inside the bound rather than on
   it. The bound curve itself remains a MODELED line per the spec's
   `measured_vs_modeled` separation; only the reproduced attack's (S,T) is
   a measured point.

7. **Standard error for `structure_gap`.** Computed as
   `sqrt(SE_real^2 + SE_scrambled^2)` using per-arm binomial SE
   `sqrt(p_hat(1-p_hat)/n_heldout)`. This is an approximation: curve-arm and
   scrambled-arm models are evaluated on the SAME set of held-out logarithm
   indices (paired), so a paired-difference SE using per-example
   correct/incorrect indicators would be tighter and is not what is
   reported. This likely OVERSTATES the combined SE (conservative in the
   direction of under-claiming significance), and is disclosed rather than
   silently assumed exact.

8. **Git commit drift.** The commit hash recorded at session start
   (`40459ba9...`) differed from the commit hash observed moments later when
   git state was captured for run manifests (`1ba846482...`), despite this
   task never running `git commit`. This indicates concurrent write
   activity in the shared worktree/branch from another process during this
   task's execution window. Each run's manifest records the git commit and
   dirty-tree state AT THE TIME THAT RUN EXECUTED (not a single fixed
   value for the whole batch), which is the technically correct behavior,
   but the drift itself is recorded here as an infrastructure anomaly for
   the Coordinator's attention -- it means "the exact commit" is not a
   single well-defined value for this run batch if other writes were
   landing on the same branch concurrently.

## Architecture / capacity table

MLP: one-hot limb encoding (16-dim per limb) flattened, `hidden` sizes
`[4]`, `[32,16]`, `[512,128]` for capacity_id 0/1/2 respectively.
Transformer: limb-embedding (`d_model` in `{4,16,64}`) + 1 encoder layer +
mean-pool + linear head, `nhead` in `{1,2,4}`.
Parameter counts and both raw (32-bit) and gzip-compressed state-dict sizes
are recorded per run in `raw-result.json` (`n_params`, `S_bits_raw`,
`S_bits_compressed`).

## Files

- `code/find_curves.py`, `curves.json` -- curve construction (see deviation 1).
- `code/ec.py` -- group arithmetic and presentation encodings.
- `code/precompute.py`, `code/cache/*.npz` -- once-per-curve point table and
  all four presentation arrays, computed once and reused identically across
  every architecture/capacity/seed (required for matched-pair identity).
- `code/splits.py` -- both split modes, with disjointness assertions run at
  construction time (`verify_disjoint`), not merely asserted.
- `code/models.py` -- MLP / Transformer architectures and capacity table.
- `code/run_cell.py` -- single matched training run (importable and
  standalone-CLI-reproducible; verified to produce identical output either
  way).
- `code/orchestrate.py` -- run-grid orchestrator; writes the full
  AGENTS.md-required run-directory layout per run
  (`runs/<RUN-ID>/{manifest.yaml,command.txt,environment.json,stdout.log,
  stderr.log,raw-result.json}`); runs C6 (scrambled arm) FIRST, then C2 and
  C3 (blocking), then the main matched grid.
- `code/table_attack.py`, `c5-table-attack.json` -- C5 reproduction (see
  deviation 6).
- `c6-seed-variance.json`, `c2-c3-controls.json`, `run-log-summary.json` --
  control-outcome summaries, each independently loadable and cross-checked
  against the per-run `raw-result.json` files in `execution-report.md`.

9. **`contiguous_block_by_logarithm` split is confounded with the target
   and its structure_gap numbers are `invalid_measurement`, discovered
   post-hoc.** The implemented contiguous split assigns the held-out slice
   to the topmost contiguous block of k in `[0,N)`. Since the target is
   `MSB(k) = [k < N/2]`, that block is (for this reduced-N pilot) 100%
   label=0 -- verified empirically: held-out label balance is exactly 0.0
   for both curves under this split (train-split balance is 0.833). A
   single-class held-out set makes "0.5 = chance" the wrong baseline (a
   trivial always-predict-0 rule scores `heldout_advantage = 0.5` on ANY
   dataset, real or scrambled, regardless of learned content), which is
   directly visible in the raw data as exact-zero or saturated,
   zero-variance gaps at the largest capacity under this split. C2
   (shuffled labels) was run only under `random_by_logarithm` and did not
   surface this, because C2 checks label/input decoupling, not
   split-induced class imbalance. **All 180 runs using
   `contiguous_block_by_logarithm` (135 MAIN-real + 45 C1-C6-scrambled) are
   reclassified `invalid_measurement` post hoc** in
   `invalidations.json`, without modifying the original (immutable) run
   directories. This is recorded as a genuine implementation defect in the
   split construction, not a finding about the hypothesis, and it means
   this pilot in practice reports a valid instrument for only ONE of the
   two required split modes (`random_by_logarithm`); the spec's requirement
   to run and report both modes was executed, but one mode's output is
   invalid rather than a valid data point. `random_by_logarithm` was
   independently verified to be balanced (48-52% per split) and is not
   affected by this defect.

10. **Git commit drift observed three times during this task's execution
    window** (`40459ba9...` at session start, `1ba846482a...` when writing
    early run manifests, `5a0d24c27b...` when finalizing analysis), with no
    `git commit` run by this task. This confirms concurrent write activity
    on the shared branch/worktree from another process throughout
    execution. Each run's manifest records the commit observed AT THAT
    RUN'S EXECUTION TIME, which is technically correct, but "the exact
    commit for this run batch" is not a single well-defined value -- flagged
    for the Coordinator.

11. **Manifest reshape (post-hoc, mechanical, requested by Coordinator).**
    All 372 `runs/*/manifest.yaml` files were originally written flat
    (`{"run_id": ..., ...}`), not matching the canonical
    `{"run": {"id": ..., ...}}` shape `tools/validate_ledger.py` and every
    other archived experiment in this batch (EXP-ECTD-9e4248, EXP-FIB-001,
    EXP-DTREE-001) use. `code/reshape_manifests.py` rewrote all 372
    manifest.yaml files in place to the canonical nested shape (`run_id` ->
    `run.id`; `git_commit`/`git_dirty`/`command` -> `run.code.{commit,dirty,
    command}`; `environment` -> `run.environment` + `run.inference`;
    `params`/`seed` -> `run.inputs.{parameters,seeds}`;
    `wall_clock_seconds` -> `run.timing.wall_seconds`; `certificate`/`reason`
    -> `run.result.{certificate,invalid_reason}`). Two fields the canonical
    schema expects that this harness never instrumented were added as
    explicit nulls rather than fabricated: `run.resources.peak_rss_bytes:
    null` (note: "not instrumented") and `run.timing.started_at` /
    `finished_at: null` (only a wall-clock delta, `wall_seconds`, was ever
    captured). This was verified lossless: all 372 manifests still parse,
    and for every one of the 372 (not just a sample) every original field's
    value round-trips to the same value at its new nested path, while
    `raw-result.json`, `command.txt`, `environment.json`, `stdout.log`, and
    `stderr.log` are confirmed byte-identical (sha256) to a pre-reshape
    backup for all 372 runs. Re-running `tools/validate_ledger.py`
    afterward produces zero errors referencing `EXP-REPL-1d1287` (down from
    381); the remaining validator failures are pre-existing, unrelated to
    this experiment, and out of this task's scope.

## Certificate discipline

No run in this experiment claims a discrete-log solve or factor-base
relation as a security result. The C5 table-attack DOES recover discrete
logs at toy scale as its own internal correctness check (it must, to be a
valid measurement of T), and that recovery is self-verified within
`table_attack.py` (`k_rec == k_true`) using code independent of the BSGS
solver's internal state (a direct scalar-multiplication check via
`curve.scalar_mul`). All training runs set `certificate.kind: none` in
their manifests, as this experiment measures held-out predictive advantage,
not solves.
