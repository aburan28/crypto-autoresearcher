# TASK-20261002-a8bbd8 — executor report

Successor (b) of the F7/D3 follow-up (DEC-20261001-494663 NA-3 (b); designed and
approved by DEC-20261002-0df88e with the POWER RULE and the OUTCOME RULE fixed
before any (b) data existed). **Observations only.** No status, hypothesis,
evidence or ledger record was written or modified; every write is under this
task directory; no RUN id; nothing under `experiments/`. No engine or solver
code was imported or executed (nothing under `src/crypto_autoresearcher` —
attested in `receipt.yaml`): the generator is this task's own adapted copy of
the red team's self-contained replica `attacks/ptm5_engine.py` (RF-4: imports
only heapq/json/math/os/sys/time/numpy), and the analysis is pure computation
on the rows.

**THE HEADLINE STOP:** the pre-registered primary discriminator (the 26..32
segment slope) could NOT be completed. Rungs 30 and 32 were stopped by the
card's pre-registered machine-protection RSS stop (2.5e9 bytes per process):
the archived construction's encoding store (~2.3–4.0 KB per recorded encoding,
~B² encodings per instance) needs more than 2.5 GB per process at B = 151
(m4 b30) and B = 67 (m5 b30) and above, as constructed. The stop is BLOCKED,
never a finding: n was not changed, no rung was relaunched, rung 32 was never
attempted (ascending order — the stop at 30 ends the phase). The segment
actually fit is **26..28 (2 rungs, n = 400)**, and the pre-registered outcome
branches are evaluated on the TRUNCATED 26..28 calibrated interval; whether a
2-rung segment supports a branch reading is the Coordinator's call (NA-2),
not this executor's.

## 1. Generation (the power rule, executed as fixed)

Construction: `code/01_generator.py`, a byte-verbatim copy of
`attacks/ptm5_engine.py` with exactly three adaptations (diff-verified):
the docstring header, a `MODES = ("on",)` constant, and the mode loop using
it. Same N rule (`rung_prime(bits)`, rng `[575, bits, 0x5EED]`), same B rule
(`default_fb_size`), same labelling (`[575, bits, 0xABC]`), same instance and
target streams (`[575, bits, m, inst, 7]` / `[..., 11]`), same attempt cap
(`min(50N, 200000)`), same encodings, pair counting, row fields, stop and mode
semantics.

**Construction-fidelity check (before any new rung):** `out/fidelity_check.json`
— the adapted generator reproduces the ARCHIVED rows exactly (every field
except `seconds`) on m4 b12 (6 instances), m5 b12 (6) and m4 b24 (3):
`all_exact_match: true`. The probe rows live only under `out/fidelity/` and
never enter `out/replica_rows.jsonl` or the analysis. A 10-instance host-speed
probe at b24 (inst 200..209, not archived instances) calibrated this host at
~2.3× the archived box's speed (median 0.089 s vs 0.205 s per instance).

| rung | wall s | peak RSS | outcome |
|---|---|---|---|
| m4 b26 (B=72) | 44.8 | 407.7 MB | 200/200 rows |
| m4 b28 (B=117) | 177.8 | 2306.7 MB | 200/200 rows |
| m4 b30 (B=151) | 0.6 | **2737.1 MB** | **RSS STOP** (guard killed it; no row written) |
| m5 b26 (B=37) | 24.0 | 390.5 MB | 200/200 rows |
| m5 b28 (B=55) | 97.3 | 1354.2 MB | 200/200 rows |
| m5 b30 (B=67) | 0.6 | **2737.6 MB** | **RSS STOP** (guard killed it; no row written) |

**m = 5 decision (the power rule's ≥ 50% condition, recorded with numbers):**
the m = 4 phase ended at 224.4 s of the generation clock (terminated by the
recorded b30 stop); the continuation launched at 481.6 s; remaining wall clock
21118.4 s ≥ 10800 s → **m = 5 RAN** (`out/generation.log`, `m5_decision`
record). Its rungs 26 and 28 completed; its rung 30 hit the same RSS stop.

Final dataset: `out/replica_rows.jsonl`, **800 rows** — m4 b26, m4 b28, m5 b26,
m5 b28, 200 per cell, all on-mode, all with PRIMARY and full stops present, no
attempt-cap hits (`out/field_check.json`: `all_ok: true`, N and B constant per
rung). Machine checks before every launch: disk 4.11–4.49 GB free (floor 1 GB),
memory-available estimate 15.4–18.7 GB (floor 6 GB; macOS adaptation — no
`/proc/meminfo` on this host — (free+speculative+inactive) × 16384 B from
`vm_stat`, raw counts recorded at every check in `out/generation.log`).

## 2. Per-rung aggregate T (AMD-20261002-2bc8cf C-1..C-4), combined 12..28

T = (Σ w S²)/(Σ w r N/4), w = 1/(N B), per (m, rung), on-mode, PRIMARY stop,
both r conventions. **Premise audit (C-1):** the replica is exactly generic BY
CONSTRUCTION (verified by the fidelity check above); no arms, no per-arm audit
applies. **C-3:** both conventions reported. **C-4:** no per-instance predicate
adopted. 99% interval: the round's curve bootstrap at the five-per-rung design
(five instances per rung per replicate, 20000 replicates, `np.default_rng(0)`
per cell, `np.quantile` 0.005/0.995). Archived rungs (12..24): point T and ci99
recomputed as an exact-arithmetic reconciliation — **absdiff 0.0 vs F7(a)** on
every cell and convention; their coverage is RESTATED (read) from
TASK-20261002-758e51. New rungs: coverage computed fresh (NULL-B budget-Poisson
— F7(a)'s labelled adaptation — and NULL-G, the round's shape, per-cell
kappa_hat; 1000 designs, inner 20000 reps, seeds declared in §6/receipt).

| m | conv | T: 12..24 (archived) then 26, 28 (new) | 99% ci at the new rungs |
|---|---|---|---|
| 4 | frozen | 2.2315, 1.9421, 1.7715, 1.5024, 1.4077, 1.3935, 1.2953, **1.2400, 1.1712** | b26 [0.9720, 1.4901]; b28 [0.9440, 1.3479] |
| 4 | rank | 8.8642 → 6.0992, **5.9096, 5.5557** | b26 [4.8992, 6.9417]; b28 [4.8987, 6.2770] |
| 5 | frozen | 3.1718 → 1.9914, **1.9029, 1.8401** | b26 [1.1524, 2.5252]; b28 [1.1697, 2.2868] |
| 5 | rank | 12.4608 → 8.1513, **7.9111, 7.6056** | b26 [6.4890, 9.5145]; b28 [6.5574, 8.7285] |

**T-POINT TRIPWIRE: no rung's calibrated 99% interval excludes 1 from below**
on any new cell (m4 frozen b26/b28 STRADDLE 1 — lo99 0.9720/0.9440, hi99
1.4901/1.3479 — exactly the b20–b24 archived pattern; all other intervals sit
above 1). Archived flags were [] (F7(a)) and stay []. **No CROSS.** Nothing is
TW-BREAK-shaped and nothing routes to the Coordinator on that channel.
Coverage on the new cells: NULL-B 1.000 with false-flag rate (hi99 < 1) 0.000;
NULL-G 1.000 — the five-per-rung interval is conservative (over-covers) at
this design, the same observation F7(a) recorded.

## 3. The segment slope and the pre-registered outcome reading

NAMING (recorded, not silently resolved): the card's "log2 T_frozen" is, to
every digit of the archived reference value (-0.038062, calibrated
[-0.041782, -0.034385]), TASK-20261002-758e51's per-instance **log2
ratio_frozen** series (ratio = S/(0.5·sqrt(r_frozen·N)), the per-instance form
of the floor bound); "weighted OLS" is that fit's per-instance OLS (the
balanced 200-per-rung design weights rungs equally). No other reading
reproduces the archived reference. Fit conventions: the frozen `stats.py`
`bootstrap_slope` reimplemented verbatim (stratified by rung, one draw per
member with replacement, percentile endpoints by the `stats.py` index
arithmetic), reps 20000, level 0.95, seed 0; MC-5 calibration per
`calibration/f7.py` + `f7_supp.py` (10 configurations, 1000 series each,
inner reps 2000 seed 0; kappa_95 worst = 1.0641); calibrated interval =
[slope − κ(slope − lo), slope + κ(hi − slope)].

**The TRUNCATED 26..28 segment (m = 4 on-mode, PRIMARY stop, n = 400):**

| quantity | slope | nominal 95% (20000, seed 0) | calibrated | kappa worst |
|---|---|---|---|---|
| **ratio_frozen (the discriminator)** | **-0.015255** | [-0.023234, -0.007282] | **[-0.023746, -0.006771]** | 1.0641 |
| ratio_rank (context) | -0.014500 | [-0.021096, -0.007768] | [-0.021530, -0.007325] | 1.0658 |

**Outcome under DEC-20261002-0df88e's rule, evaluated on the truncated
interval:** the 26..28 calibrated interval [-0.023746, -0.006771] **EXCLUDES
the archived 12..24 slope** -0.038062 (it lies entirely ABOVE it, and is
disjoint from the archived calibrated interval [-0.041782, -0.034385] —
"bending beyond both intervals" in the strong sense) **and ALSO excludes 0**
(both endpoints negative). By the rule's letter, **FLAT** fires (direction:
above — shallower than the 12..24 slope, flattening-shaped); the additional
fact the rule's branches do not name is that the decline has NOT stopped: the
truncated segment's interval excludes 0 too, i.e. the decline continues at a
measurably shallower rate on 26..28.

**NARROWEST SUPPORTED SENTENCE (the rule's own branch, on the truncated
segment):** on the 26..28 segment — rungs 30 and 32 stopped by the
pre-registered RSS machine-protection stop, so the pre-registered 26..32
discriminator was not completed — the m = 4 on-mode segment slope of log2
T_frozen vs log2 N is **-0.015255** (MC-5-calibrated 99% [-0.023746,
-0.006771]), an interval that excludes the 12..24 slope -0.038062 (FLAT by the
rule's letter, bending beyond both calibrated intervals) while also excluding
0 (the decline continues, shallower); no rung's 99% T interval excludes 1 from
below (no CROSS). Whether a 2-rung segment supports the FLAT reading is the
Coordinator's call under NA-2.

Supporting context (arithmetic, labelled, not the discriminator): measured
m4 frozen T sits ABOVE the naive 12..24-slope projection at both new rungs —
T(26) = 1.2400 vs projected 1.2322 (×1.0063), T(28) = 1.1712 vs projected
1.1446 (×1.0232) — consistent with a bend toward flattening; the same
projection puts T(30) ≈ 1.102 and T(32) ≈ 1.033, rungs that were stopped and
carry no measurement. Per-instance levels on the new segment: ratio_frozen
[0.791, 1.379], ratio_rank [1.945, 2.896] — recorded as observations only (no
per-instance predicate is adopted, AMD C-4).

## 4. Machinery cross-checks (all exact)

- **12..24 reproduction cross-check** (same rows, F7(a)'s exact seeds —
  `random.Random(0)` bootstrap and the `F7a-replica-*` MC-5 masters):
  reproduces F7(a)'s archived fits **exactly** — ratio_frozen slope
  -0.038061906588711954, nominal and calibrated intervals to absdiff 0.0;
  ratio_rank likewise. The archived values remain the reference; this
  validates the machinery used for the 26..28 fit.
- **Archived per-rung reconciliation:** recomputed point T and ci99 match
  F7(a)'s `per_rung_T.json` to absdiff **0.0** on all 14 cells × 2
  conventions.
- **Vectorized cross-check** of the 26..28 fit (numpy PCG64, seed 11058136):
  interval endpoints agree with the verbatim fit to ≤ 5.3e-05 (F7(a)'s
  analogue was ≤ 4.2e-05); the linear-form self-check holds (absdiff 3.5e-18).
- **MC-2** (200 seeds × 2000 reps): 0/200 flips of "excludes 0"; endpoint
  MC s.d. ≤ 2.5e-04. **MC-5 coverage** on the new segment: 0.943–0.958 at
  nominal 95% over the 10 configurations (kappa worst 1.0641).

## 5. Analysis attempts (both recorded)

One implementation failure, one success; no analysis quantity changed between
them (all seeds fixed; the deterministic per-rung T and segment fits are
identical across attempts — the failure was in an ADDED context block, after
`per_rung_T.json` was written):

1. `python3 code/guard.py analysis_02 -- python3 code/02_analysis.py` — exit 1
   after 107.9 s: `IndexError` in the naive-continuation context block (rungs
   30/32 have no rows; the log2N lookup indexed an empty list).
   **implementation_error in this executor's context block, not a finding.**
   stdout/stderr retained as `out/02_analysis_attempt1.{stdout,stderr}`.
2. Fix (stopped rungs' N recovered from the deterministic `rung_prime(bits)`,
   the same N the driver's rung_launch records show); rerun:
   `python3 code/guard.py analysis_02_attempt2 -- python3 code/02_analysis.py`
   — exit 0 after 146.9 s, peak RSS 177.7 MB. Outputs as reported above.

## 6. Defects, deviations, unrecoverable conventions (recorded, not dropped)

1. **The RSS machine-protection stop truncated the primary discriminator
   (26..32 → 26..28).** The card's RSS stop (2.5e9 bytes per process) binds
   the archived construction at rung 30 for both m (peaks 2737.1/2737.6 MB
   within 0.6 s; the store needs ~2.3–4.0 KB per recorded encoding and
   ~B² encodings per instance — at m4 b28 the completed rung already peaked
   at 2306.7 MB). The stop stands: no n change, no relaunch, no
   memory-layout re-engineering of the archived construction (that would be a
   protocol change mid-run, the Coordinator's to commission, not this
   executor's to make silently). The driver's pre-rung projection modelled
   WALL CLOCK (B³ scaling) but not RSS; the guard's enforcement is what
   stopped the rungs — which is its job. The outcome branches are evaluated
   on the truncated interval with the truncation disclosed in every output.
2. **On-mode rows only (no census rows).** The power rule names on-mode cells
   only ("m = 4 on-mode primary; m = 5 on-mode ONLY if…") and every analysis
   the card orders reads on-mode rows; the archived replica's census rows are
   unused by all of them. Recorded as the reading of the power rule; the
   construction, row fields and mode semantics are otherwise byte-identical
   (diff-verified).
3. **"log2 T_frozen" / "weighted OLS" naming.** Resolved by the archived
   reference values (see §3): the discriminator is the F7(a) per-instance log2
   ratio_frozen fit. Recorded, not silently resolved.
4. **Analysis attempt 1 failed** (implementation_error in the added
   naive-continuation context block; §5). Both attempts retained.
5. **macOS adaptations** (no `/proc`): the guard polls `ps -o rss=` (the
   archived guard summed `/proc/*/status` VmRSS over the process tree; this
   task's children fork nothing, recorded); MemAvailable estimated as
   (free+speculative+inactive) × 16384 B from `vm_stat`, raw counts recorded
   at every check; the archived guard's 1.5e9 limit replaced by THIS card's
   2.5e9.
6. **Fidelity probes under `out/fidelity/`** (a handful of archived instances
   regenerated ONLY to verify the adapted generator reproduces the archive
   exactly, plus a 10-instance host-speed probe at inst 200..209 of b24 —
   instances the archive does not contain): never enter
   `out/replica_rows.jsonl`, never analyzed, disclosed here.
7. **Archived rungs' coverage restated, not recomputed** (their NULL-B/NULL-G
   masters were F7(a)-task-tagged `[758510, …]`; restating keeps the archived
   segment read-only). New rungs use this task's declared masters
   `[11058136, …]` (= 0xA8BBD8). The archived rungs' point T and ci99 were
   recomputed only as an exact reconciliation (absdiff 0.0).
8. **Dispatch-note HEAD vs execution HEAD.** The dispatch note said HEAD
   c24c15034c; at execution HEAD is a5e412576e (one later `bus: publish
   records` commit; the card/decision commit c24c15034c is present beneath
   it; every declared input exists at HEAD — verified by reading each before
   the attempt). Working tree clean apart from this task directory.
9. **Driver exits.** Both generation drivers exited 1 — by design: each
   phase's recorded RSS stop ends it with a nonzero exit so the stop is
   visible. The completed rungs' rows are intact (200/200 per cell).

Scope discipline (TW-SCOPE): toy scale — the replica stops at 28 bits (the
pre-registered rungs 30/32 stopped); synthetic Z_N replica; no
deployed-curve claim, no universal impossibility, no exponent below rho.

## 7. Deliverables

- `code/` — `01_generator.py` (adapted verbatim, diff-verified), `guard.py`,
  `00_fidelity_check.py`, `run_generation.py`, `run_generation_m5.py`,
  `02_analysis.py` (deterministic; all seeds declared in the docstrings and
  the receipt)
- `out/replica_rows.jsonl` — exactly the new-run rows (800: m4/m5 × b26/b28,
  on-mode, 200 per cell); nothing archived duplicated or regenerated
- `out/per_rung_T.json` — both r conventions per rung (12..28 combined),
  99% intervals at 20000 replicates, coverage (fresh for new rungs, restated
  for archived), T-point flags = []
- `out/segment_slopes.json` — the truncated 26..28 segment slope with
  calibrated interval, read against the archived 12..24 slope and 0, the
  outcome classification, the reproduction cross-checks, the naive-continuation
  context, the truncation record
- `out/fidelity_check.json`, `out/field_check.json`, `out/generation.log`,
  `out/commands.log`, `out/fidelity/` (probes), `out/02_analysis.stdout`,
  `out/02_analysis.stderr`, `out/02_analysis_attempt1.{stdout,stderr}`,
  `out/run_generation{,_m5}.{stdout,stderr}`
- `report.md` (this file), `receipt.yaml`
