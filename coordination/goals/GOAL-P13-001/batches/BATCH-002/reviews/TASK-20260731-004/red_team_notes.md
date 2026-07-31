# TASK-20260731-004 — Red Team working notes (RT-20260731-004)

Independent session. Reviewed snapshot `7c2bd6f7` (run), contract commit `35701d8f`.
No commit made. Nothing written outside this directory.
All roles under this harness resolve to `claude-opus-5`, `model_verified: false`.
Model-level independence from the producer is **unavailable**; the mitigation used
here is CTRL-RT039-A adversarial mutation selection (I chose my own perturbations),
and it is **not a substitute** for the missing independence.

---

## 0. What I set out to do, and what actually happened

The card told me to attack a null as hard as a claimed break, and warned that a
tired campaign banks nulls cheaply. I ran the four fit perturbations the card
names. **All four failed.** The fit is exactly as stable as the executor reports.

So I changed target. Under CTRL-RT039-A I am required to choose my own
perturbations rather than re-run the producer's — and the perturbation the
producer *could not* choose without amending its own frozen contract is the prime
range. That is where the batch breaks.

---

## 1. Reproduction of the primary fit (independent, from `summary.json`)

Independent OLS, my own code:

```
c        = 0.138802      (fit_report.json: 0.13880213854255802)
rse M-A  = 0.073423      (fit_report.json: 0.07342302697779185)
rse M-0  = 0.113977      (fit_report.json: 0.11397683257079888)
ratio    = 1.5523        (fit_report.json: 1.5523308866750112)
```

Matches to six digits. GOF-3 fires correctly. CTRL-CAL-GATE fires correctly.
`READING-NOT-IDENTIFIED` is **mechanically correct** and I do not contest it.

---

## 2. Was the design powered to detect `c ≈ 1.9`? — YES, BY ~10×

Design: 8 primes, `log2 p ∈ {20..40}`, regressor `sqrt(log2 p)`, `Sxx = 3.0411`,
observed noise `rse(M-A) = 0.073423` bits.

GOF-3 requires `rse(M-0)/rse(M-A) ≥ 2`. Holding noise at the observed level:

| true c | expected rse ratio | GOF-3 fires? | swing over sweep |
|---|---|---|---|
| 0.10 | 1.29 | yes | 0.19 bits |
| 0.1975 | 2.00 | **threshold** | 0.37 bits |
| 0.30 | 2.85 | no | 0.56 bits |
| 1.00 | 9.02 | no | 1.85 bits |
| **1.9224 (= c\*)** | **17.28** | no | **3.56 bits** |

**Minimum detectable c = 0.1975.** `c_star = 1.9224` is 9.7× above it.

Model-free cross-check, no functional form assumed: the observed total swing of
`log2(T_entry_ops)` across the sweep is **0.3012 bits** (min 10.6151, max 10.9163).
`c = c_star` would require **3.561 bits**. A factor ~12.

**Conclusion.** `READING-NOT-IDENTIFIED` is *not* a statement about the
experiment's power. The design saw what it was built to see; the effect is
genuinely small *in this window*. The batch must therefore **not** write "we could
not detect a p-dependence" without the second sentence "and a `c` of order
`c_star` would have been detected at 17× the gate threshold."

This is the opposite of the failure mode the card anticipated, and it matters:
the underlying numbers point at the **threatened** direction (`c_hi = 0.2418` vs
`c_star = 1.9224`), i.e. the uncomfortable one, and the null hides it.

---

## 3. Is CTRL-CAL a control or a tautology? — A CONTROL, BUT MIS-SPECIFIED

### 3.1 Can it fail to fire?

`t_mul` carried interval `[-0.01300, +0.15484]`. The gate fails to fire iff the
primary interval's lower endpoint exceeds `0.15484`. With the observed primary
half-width `0.1031`, that needs `c_fit > ≈ 0.258`. At `c = 1.9` the primary
interval would sit near `[1.82, 2.03]` and the gate would not fire, comfortably.

**So it is not the BATCH-016 / CTRL-4 tautology class.** It *can* fail to fire, and
it would have failed to fire at the value that matters.

But it is **guaranteed** to fire for any true `c < ≈ 0.26`, which is precisely the
regime the instrument is in. In that regime it cannot separate "host artifact"
from "small true effect", and the run's artifacts do not say so.

### 3.2 The real defect: it is applied to a series from which the control is already subtracted

Because `log2(T_entry_ops) = log2(T_entry_s) − log2(t_mul)` and OLS is linear,

```
slope(ops) = slope(sec) − slope(t_mul)     exactly
```

Verified on the run's own numbers:

```
slope(raw seconds) = 0.2097
slope(t_mul)       = 0.0709
slope(ops)         = 0.1388 = 0.2097 − 0.0709   ✓ to all reported digits
```

So CTRL-CAL-GATE asks: *does `slope(sec) − slope(t_mul)` overlap `slope(t_mul)`?*
— i.e. *is `slope(sec) ≈ 2 · slope(t_mul)`?* That is **not** a host-contamination
test on the normalised series. The normalised series is the host-corrected one;
the gate double-counts.

The correct null object for a normalised series is `t_noop`, which is flat
(5.4–5.9 ns across the sweep), and `CTRL-NULL`, which is **clean** (NULL-1 slope
`0.000202`, interval `[−0.00309, +0.00349]`; eight values spanning 0.0060 bits).

CTRL-NULL is a genuinely good control and I have no objection to it.

---

## 4. THE MAIN EVENT: the measured window is a dispatch floor

### 4.1 Hypothesis

The timed window charges (c1) `Phi_ell` specialisation + (c2) root finding in
`F_{p^2}`. c1 is interpreter/database dispatch and is p-independent by
construction. c2 needs `x^(p^2) mod f` and grows ~linearly in `log p` in
`F_{p^2}`-ops. At `p ≤ 2^40` c1 is a large share, so the pooled per-entry cost is
a two-component mixture whose flat component suppresses the slope.

Tell from the run's own data before I ran anything: `t_mul` at `2^20` is
`1.735e-7 s` — 173 ns for a 20-bit `F_{p^2}` multiplication, ~32× the measured
no-op loop iteration. That is dispatch, not arithmetic. `t_mul` grows only 15.6%
across a doubling of word count (`2^20 → 2^40`), so ≥84% of the "host-normalised
`F_{p^2}`-operation" unit is p-independent overhead. **The normalisation does not
achieve the paper's unit at this scale.**

### 4.2 Probe RT-A (ran it — `scratchpad/rt_probe.py`, sage 10.9)

Same timed-window shape as `expand_step_V1`
(`classical_modular_polynomial` specialise → `.roots()` → non-backtracking
filter), same `t_mul`/`t_noop` calibration, `log2 p ∈ {20,40,64,128,256,512}`,
`ℓ ∈ {2,3}`, 30 steps/cell, `E0: y² = x³ + x`, `p` = largest prime `< 2^k` with
`p ≡ 3 mod 4`, supersingularity verified `True` at every p.

`T_entry_ops` median, ℓ = 2:

| log2 p | 20 | 40 | 64 | 128 | 256 | 512 |
|---|---|---|---|---|---|---|
| ops/entry | 1805 | 1876 | 2100 | 5572 | **19025** | 120366 |
| log2 | 10.818 | 10.874 | 11.036 | 12.444 | **14.216** | 16.877 |

Local slope in the M-A parameterisation:

```
20→40   c_local = 0.0301     <-- the measured window
40→64   c_local = 0.0971
64→128  c_local = 0.4248
128→256 c_local = 0.3780
256→512 c_local = 0.4016
```

M-A refit on `{64,128,256,512}`: **c = 0.3969, max |residual| = 0.060 bits.**
M-A is a *good* functional form once out of the floor. The run fitted it in the
one window where it is not.

### 4.3 Probe RT-B (component split + repeat — `scratchpad/rt_probe2.py`)

Two independent repetitions, agreeing to within 3% at every prime.

| log2 p | c1 Φ-specialise (s) | c2 root-find (s) | c2 share |
|---|---|---|---|
| 20 | 8.81e-05 | 1.706e-04 | 0.655 |
| 40 | 8.97e-05 | 1.987e-04 | 0.685 |
| 64 | 8.90e-05 | 2.456e-04 | 0.729 |
| 128 | 1.103e-04 | 3.103e-03 | 0.967 |
| 256 | 1.400e-04 | 1.244e-02 | **0.988** |

c1 grows **1.6×** across a 12.8× growth in `log p` — it is dispatch.
c2 grows **72×**. Hypothesis confirmed.

### 4.4 Probe limits — stated so nobody quotes them as a measurement

30 steps/cell (contract floor is 300 entries), same host as RUN-SSI-002, no
random-walk starting curves, no interleaved calibration schedule, no null control,
no determinism re-execution, no bootstrap, no interval, V-1 only, `ℓ ∈ {2,3}` only.
**These are red-team probes, not measurements of record. No `c` from them is a
fitted exponent.** They are sufficient for the qualitative claim (the flatness
breaks, and where) and nothing else.

---

## 5. The measured regime vs the operating regime — quantified

Committed model at `log2 p = 256` (imported unmodified, sha256 `a82b9d5b1f…`):

```
log2 B_opt = 14.200   (B ≈ 18,800)
log2 X     = 49.6
u          = 5.986
log2 M     = 93.278
log2 T     = 108.731
```

Run measured `B ≤ 32`; the **primary** B-ASY series measured `B ∈ {3,4,5}`.
Gap ≈ **9.2 bits in log2 B**, against a `B^{O(1)}` factor in Lemma 3.3.

**My probes fix the p axis and do nothing for the B axis.** EA-3 remains the
binding limitation and is unrepaired by this batch *and* by this review.

Honest scope: *the p axis is now known to be measurable and was not measured; the
B axis remains an extrapolation.*

---

## 6. My own perturbations — ALL FOUR FAILED, reported as failed

### Leave-one-prime-out (primary series)

```
drop k=20 -> c=0.1250 (−0.0138)     drop k=32 -> c=0.1376 (−0.0012)
drop k=23 -> c=0.1390 (+0.0002)     drop k=35 -> c=0.1255 (−0.0133)
drop k=26 -> c=0.1501 (+0.0113)     drop k=38 -> c=0.1251 (−0.0137)
drop k=29 -> c=0.1351 (−0.0037)     drop k=40 -> c=0.1747 (+0.0359)

LOO span = 0.0498   reported interval width = 0.2060   span/width = 0.24
```

**The interval is NOT too narrow.** Attack failed.

### Shortest 5-prime sub-range refits

```
{20..32} c=0.1304    {23..35} c=0.1688    {26..38} c=0.1812    {29..40} c=0.1879
```

Monotone upward drift with window centre — *directionally* consistent with §4's
curvature, but CI-T half-widths are 0.26–0.38, so not significant standalone.
Reported as a failed standalone attack; it is corroboration for §4, not evidence.

### Median vs mean

`0.1388 → 0.1653` (ops), `0.2097 → 0.2363` (raw s). Inside the interval. Failed.

### Drop the normalisation

`0.1388 → 0.2097`, intervals overlap; difference is exactly `slope(t_mul)` by §3.2.
Failed as a falsification — but it surfaced §3.2 and §7 below.

---

## 7. The reading is contingent on the *primary quantity*, and the mandated secondary series says something else

| series | c | rse0/rse | GOF-3 | identified |
|---|---|---|---|---|
| B-ASY ops (PRIMARY) | +0.1388 | 1.552 | **fires** | no |
| B-ASY raw seconds | +0.2097 | 4.244 | no | **yes** |
| B-FIX-8 ops | +0.1073 | 1.246 | fires | no |
| B-FIX-8 raw seconds | +0.1783 | 3.938 | no | **yes** |
| B-FIX-32 ops | +0.0667 | 1.113 | fires | no |
| B-FIX-32 raw seconds | +0.1376 | 4.625 | no | **yes** |
| B-FIX-8 V-2 ops | +0.2520 | 1.028 | fires (+GOF-1) | no |

**Every V-1 raw-seconds series passes all three GOF gates and identifies an
exponent** — and every one of them fires `READING-SMALL-C` (`c_hi ≪ c_star`), the
*threatened* direction.

This is a legitimate consequence of pre-registration, not misconduct: the contract
named `T_entry_ops` primary before any number existed. But `DEC-20260731-001` must
record **both** true sentences, because the normalisation is exactly what
subtracts a real slope and collapses the SNR.

---

## 8. `w = 2^30` — split verdict

Executor's basis: at `w = 2^30` the committed model returns
`margin(c=0) = 34.269` and `margin(c=2) = 2.269`, reproducing NC-2's "~34 / ~2"
and DEC-20260724-016's recorded 2.3 bits.

I verified this independently against the committed model and it is **exact and
unique on the model's memory grid `{30,40,50,60,70,80}`**. So the identification
is a correct *reconstruction* of the budget DEC-20260724-016 was implicitly using
— genuine service, not curve-fitting in the pejorative sense, and the executor
said so in those terms.

But `c_star` is not a constant of the problem:

```
w=2^20 -> c_star 1.6099      w=2^60 -> 2.8599
w=2^30 -> 1.9224             w=2^70 -> 3.1724
w=2^40 -> 2.2349             w=2^80 -> 3.4849
w=2^50 -> 2.5474             w=2^92 -> 3.8599    (model's own log2 M = 93.278)
```

Range **2.25 in c** = 11× the run's carried interval width (0.2060).
`margin(c_fit)` at 256 moves 32.05 bits (`w=2^30`) → 57.05 bits (`w=2^80`).

**Does it flip the reading?** No — `c_star > 1.61` at every feasible `w`, and the
largest `c_hi` anywhere in the run is 0.7745. Attack partly failed; recorded as
FAIL-9.

**Does it flip the margin figures?** Yes, badly. And that matters because:

### 8.1 A false statement of record

```
fit_report.json:3640   "all_memory_budgets_also_reported": true
fit_report.json:3683   "all_memory_budgets_also_reported": true
execution_report.yaml D-6: "Margins at w in {2^30..2^80} are reported alongside."
```

I grepped every artifact of RUN-SSI-002 for `w=2^40|2^50|2^60|2^70|2^80` and for
`memory_budget`. **There are no margin figures at any `w` other than `2^30`.**

The run record is immutable (AGENTS rule 2), so this is a **superseding
correction** in EV-SSI-006 / DEC-20260731-001, never an edit.

The deeper defect belongs upstream: DEC-20260724-016 quoted a 2.3-bit margin
without naming the memory budget that produced it.

---

## 9. The ℓ-mixture confound is untested **on the primary series**

`B-ASY` realised parameters from `summary.json`:

```
k=20,23      B=3   ell ∈ {2,3}
k=26,29,32   B=4   ell ∈ {2,3}
k=35,38,40   B=5   ell ∈ {2,3,5}     <-- the ell-set CHANGES inside the sweep
```

R-10 mandates FIT-ELL precisely for this — but FIT-ELL is specified at **B-FIX-8**,
not B-ASY. And `FIT-ELL|ell=2` is unusable (3 of 8 primes cleared the 300-entry
floor; carried interval `[−1.815, +1.097]`, width 2.91). `FIT-ELL|ell=3` overlaps
the B-FIX-8 pooled interval — a comparison against the wrong series.

I did **not** attempt the B-ASY per-ell refit; it needs a re-analysis pass over
`raw-timings.json` that I judged outside my card. Named as RC-2 and as an
attack-not-run.

---

## 10. The 178-second run

```
session_wall_seconds = 178.666        total cap 5400 s      (~30× headroom)
per-prime spend      = 10.5 – 31.1 s  sub-cap 600 s
cells_not_reached    = []             under_sampled_cells = []
skipped              = "B-FIX-32 under V-2 at every prime (OPTIONAL-IF-BUDGET)"
```

The skip is *named*, which is correct practice — but the stated reason
(budget) does not hold with 5221 s unspent. The run stopped because the script
ended.

**Would a wider sweep have changed the reading?** Yes, decisively — §4. My RT-A
probe reached `log2 p = 512` in ≈7 minutes on the same host, i.e. ~8% of the
unspent budget. The contract's declared *single largest* extrapolation (EA-1) was
avoidable.

More entries per cell would **not** have helped: cells already carry 1500–6000
entries and the limiting quantity is between-prime scatter (`rse ≈ 0.073 bits`),
not within-cell noise. **Wider, not deeper.**

---

## 11. Seeding (GAP-1) — attack failed

```
k=20: SEED-A/SEED-B = 0.9721   seed_seconds 7.5e-05 (A) / 3.8e-03 (B), outside window
k=40: SEED-A/SEED-B = 0.9785   seed_seconds 1.6e-05 (A) / 9.5e-04 (B), outside window
SEED-GATE band [0.90, 1.10] -> not fired
```

SEED-A's stated basis holds: it is the minimal completion that makes the loop
execute and it charges the maximum work to the measurement (conservative for a
cost floor). The constant is **not** seeding-dependent at the 2–3% level. I
looked for a third strategy that would move it further and do not believe one
exists at ≥1500 entries/cell: any seeding affects at most the first `ℓ+1` entries,
weight `O(1/1500)`.

**GAP-1 remains an open defect of the frozen text. Nothing here repairs it.**

---

## 12. Claim-ceiling audit — no breach found

Searched all thirteen run artifacts. No artifact asserts the NIST-I margin as
measured; none claims Heuristic 1 validated/weakened; none claims GAP-1/GAP-2
repaired; none validates Section 4.1; none recommends a parameter; none makes an
asymptotic claim; none mentions CSIDH or PEGASIS. Every margin figure carries the
`"EXTRAPOLATION"` label, EA-3 restated beside it, and the note that it is
"arithmetic on a fit that was declared not adequate, NOT a margin claim."
`execution_report.yaml` lines 546–555 restate every carried limitation.

The only false statement of record is §8.1, which is an overstatement of
*completeness*, not a claim-ceiling breach.

**Attack failed and I report it as failed. The executor's honesty discipline on
this run is good.**

---

## 13. A latent trap in the frozen contract

The committed model's `margin := log2speedup_vs_DG` is **decreasing in c**. So
`c_hi < c_star` ⟹ margin **>** 3.51 bits. `READING-SMALL-C`'s *condition* and its
*label* (THREATENED) are both right; its **text** — "THE EXTRAPOLATED NIST-I
MARGIN IS SMALLER THAN THE 3.51-BIT IRREPRODUCIBILITY BAND" — has the inequality
backwards.

No effect on this run (evaluated mechanically on the condition; NOT-IDENTIFIED
took precedence). But `DEC-20260731-001` will quote these readings in prose, and a
reader following the text rather than the condition will conclude the opposite of
what the model says. Fix by superseding text; never edit the frozen contract.

---

## 14. `fallback_used: true` against `fallback_allowed: false`

`manifest.yaml` records it explicitly, with a disclosure block. My assessment
(the Coordinator adjudicates, not me):

This is a **harness-level impossibility, not an executor choice**. Claude Code
cannot resolve GPT-5.6-family aliases at all, so `fallback_allowed: false` was
*unsatisfiable at dispatch time*. The defect belongs to the dispatch step.

The mathematics does not depend on which model wrote the script: the arithmetic is
independently reproducible from `raw-timings.json`, the validator reproduced it,
and I reproduced the primary fit to six digits. **I see no ground to rule the
measurement inadmissible on this basis.** Record the deviation against dispatch
and fix the queue template so an unsatisfiable inference constraint is not emitted
again.

### What the shared model cost *here specifically*

BATCH-016's R-9 finding recurs, exactly. R-9 ("everything is charged") is a
**mechanical** constraint on the **execution** layer, and it worked: the timed
window genuinely charges Φ evaluation, root finding, filter and insertion, and
CTRL-COUNT's 50/50 spot checks pass in every cell.

What the shared model did **not** protect is the **selection** layer — the choice
`exponents_log2p = {20..40}`. Coordinator, executor and validator all inherit the
same prior that "toy scale means small primes", and all three accepted a p range
that makes the headline quantity unmeasurable. I only broke it because
CTRL-RT039-A forced me to pick my own perturbation, and the one I picked was a
perturbation of the **design**, not of the **fit**.

That is the mitigation working. It is not model independence and this report
claims none.

---

## 15. Attacks I did NOT run (named, per RT10)

- FIT-ELL on the primary **B-ASY** series (§9) → RC-2.
- **Any B sweep at all.** CC-2 entirely unrepaired by me; I measured `ℓ ∈ {2,3}`.
- Any audit of the committed cost model's Dickman machinery, optimiser grid, or
  the 0.05–3.51 bit EA-5 band. I imported it unmodified and checked its sha256.
- Any check on a **second host**. Same host as the run, so a host-specific
  dispatch profile is not separated from a general one.
- V-2 (Vélu) past `2^40`. RT-A/RT-B are V-1 only.
- CTRL-DRIFT re-derivation from raw timings; I accepted the executor's ratios.
- NC-1 and NC-3 — not opened by this batch (N-9), not assessed.

---

## 16. Bottom line

The run is valid, the controls are clean, the arithmetic reproduces, the claim
ceiling is respected, and `READING-NOT-IDENTIFIED` fired correctly.

**The defect is in the frozen contract's prime range, not in the execution.**

The null is real *as a statement about `p ≤ 2^40`* and **not** as a statement
about Algorithm 1. It should be banked with that scope attached and with the
power analysis (§2) attached, and the lane should **not** be closed — there is no
named obstruction, only an unspent budget and a parameter frozen in the wrong
place.

Next action: open **NC-2-EXT** as `EXP-SSI-003`, everything carried over from
EXP-SSI-002 unchanged except `exponents_log2p = {20, 40, 64, 96, 128, 192, 256,
320}`, with gates and readings frozen **before** execution and **without**
reference to any number in this report.
