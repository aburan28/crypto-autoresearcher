# TASK-20260803-69f3cd — what survives of ANOM-3

**Role:** Executor · **Goal:** GOAL-MLKEM-003 · **Batch:** BATCH-012 (final authorised batch)
**Archived by:** TASK-20260803-3fac41 · **Repo commit at run time:** `fba777b495a242196ad021b13d3485f2edd03b69`
**Estimator pin:** `3e48ef421ec256afddb3e7d2249a77eab6e9ba12`

Everything below is a **cost-model estimate**, not a measurement. Nothing here is an
ML-KEM break, a demonstration that ML-KEM misses a NIST category, a security proof in
either direction, a validated heuristic, or a correction of `EV-MLKEM-015`.
**AGENTS.md rule 12 remains UNMET and UNWAIVED.** No status of
`EV-MLKEM-011/013/015/017/018/019/020/021` or any `KN-*` entry is changed or proposed
to change. I record observations; the judgement belongs to the Reviewer and Coordinator.

---

## Step 0 — known-answer control, committed shim, no patch

Command (run before anything else, on a clean tree — `git status --porcelain` empty):

```
PYTHONPATH=tools/sage_free_estimator/shim:/tmp/le python3 tools/sage_free_estimator/known_answer_control.py
```

Verbatim stdout:

```
set             log2(rop)          reference      delta  beta   eta      d
Kyber512   140.1994731076     140.1994731076   0.00e+00   389   422   1005
Kyber768   200.9587149141     200.9587149141   0.00e+00   606   640   1420
Kyber1024  270.7236234535     (no reference)         --   855   889   1867

Kyber512   143.7884782479     143.7884782479   3.13e-13     dual_hybrid(fft=True)
Kyber768   203.7878630676     203.7878630676   2.27e-13     dual_hybrid(fft=True)

PASS: every reference reproduced against lattice-estimator 3e48ef421ec2 -- primal_bdd exactly (delta 0.0), dual_hybrid(fft=True) within 1e-09.
Scope: primal_bdd and dual_hybrid(fft=True) under RC.MATZOV.
KNOWN UNAVAILABLE in this harness, all verified by running them: arora_gb (PowerSeriesRing is a stub that raises), dual (ZeroDivisionError), primal_hybrid (ZeroDivisionError). Any 'best attack' claim is scoped to the attacks actually served.
```

stderr was empty. **Exit code 0. PASS.** Wall clock 29.1 s.
Shim SHA-256: `all.py` `32d60a646f636aea7d12ca51eb48b2326b454f8dd4e4df7d6477b7e523722aab`,
`known_answer_control.py` `bb632d652b4db72839d3bcbc7b4f9a6fd2e66145223c72905e9aaa0b119de9d0`.
`tools/sage_free_estimator` was **not** modified at any point in this task.

### The control's own scope, restated because it matters for S1

The control's dual reference is `estimator.lwe_dual.dual_hybrid(fft=True)`. That is
**not** the ANOM-3 callable. Verified from source and recorded in `results.json`
(`S0_identity_and_anchor`):

- `estimator/lwe.py:13` — `from .lwe_dual import matzov as dual_hybrid`, so the public
  name `LWE.dual_hybrid` **is** `lwe_dual.matzov`
  (`public_LWE_dual_hybrid_is_lwe_dual_matzov: true`).
- `lwe_dual.matzov` is an instance of class `MATZOV` (`lwe_dual.py:496`, instantiated
  at line 689).
- The **module-level** `estimator.lwe_dual.dual_hybrid` is a different object — a plain
  function that dispatches to `DH = DualHybrid()` (`lwe_dual.py:493`).
  `module_level_lwe_dual_dual_hybrid_is_matzov: false`.

So before S1, the situation was: the control covers `primal_bdd` and `DualHybrid`, and
covers `MATZOV` nowhere.

---

## S1 — Sage reference: **the gap is closed, and the numbers verify**

### The coverage gap, re-established from the committed archive

`experiments/EXP-MLKEM-015/implementation/reproduce_estimates.py:16` reads
`from estimator.lwe_dual import dual_hybrid` and line 43 calls
`dual_hybrid(params, red_cost_model=cm, fft=fft)`. The string `matzov(` does not appear
in that file. The archived field `dual_fft_MATZOV_log2` in
`runs/RUN-MLKEM-015-001/raw-result.json` is `143.78847824788485 / 203.78786306762115 /
273.81726768503654` — i.e. the `DualHybrid` numbers, not ANOM-3's.

**No archived Sage run has ever exercised the `matzov` path.** That was a fact about the
archive, not about this host, and it was true at all three parameter sets, not only at
768/1024.

### The acquisition attempt

Full transcript with every command and its exact output: `sage_attempt_transcript.txt`
(33 commands, in the write scope). Summary of the decisive ones:

| route | command | outcome |
|---|---|---|
| already present | `command -v sage`, `import sage` | `NOT-FOUND`; `ModuleNotFoundError: No module named 'sage'` |
| apt | `apt-cache policy sagemath` (before and after `apt-get update`) | `Candidate: (none)` — the Coordinator's finding **re-checked and confirmed** |
| apt | `apt-get install -y --no-install-recommends sagemath` | exit 100, `Package 'sagemath' has no installation candidate` |
| conda | `which conda mamba micromamba` | not found; `conda --version` exit 127 |
| pip wheel | `pip download sagemath-standard --only-binary :all:` | exit 1, no wheel |
| pip source | `pip install sagemath-standard` | exit 1 — `error: cannot find an installation of PARI/GP: make sure that the 'gp' program is in your $PATH` (fails building `cypari2`). The Coordinator's finding **re-checked and confirmed**, with the missing dependency now named. |
| **pip, passagemath** | `python3 -m venv /tmp/sagevenv && /tmp/sagevenv/bin/pip install passagemath-standard` | **exit 0** — 10.8.7, binary wheels, no compilation |

`passagemath-standard` is the SageMath source tree redistributed on PyPI as binary
wheels. It installed `sage.all`, and the estimator's whole Sage surface works:

```
$ /tmp/sagevenv/bin/python -c 'import sage.all; print("sage.all OK", sage.all.__file__)'
sage.all OK /tmp/sagevenv/lib/python3.11/site-packages/sage/all.py

$ /tmp/sagevenv/bin/python -c 'from sage.all import RR, log, binomial, find_root, RealDistribution; print("surface OK", RR(2).log(2))'
surface OK 1.00000000000000
```

### The verification

The estimator was then run under that interpreter with **the shim deliberately NOT on
`PYTHONPATH`** (`PYTHONPATH=/tmp/le` only), so `sage.all` resolves to the real Sage
implementation — real `RealField`/MPFR, real `find_root`, real `RealDistribution` — and
not to `shim/sage/all.py`.

| set | attack | shim (mpmath) | real Sage (passagemath 10.8.7) | delta (bits) |
|---|---|---|---|---|
| Kyber-512 | `primal_bdd` | 140.1994731076207 | 140.1994731076207 | **0.000e+00** |
| Kyber-512 | `matzov` | 139.6560414808584 | 139.6560414808584 | **0.000e+00** |
| Kyber-768 | `primal_bdd` | 200.9587149140538 | 200.9587149140538 | **0.000e+00** |
| Kyber-768 | **`matzov`** | **196.3662433539967** | **196.3662433500587** | **3.938e-09** |
| Kyber-1024 | `primal_bdd` | 270.7236234535225 | 270.7236234535225 | **0.000e+00** |
| Kyber-1024 | **`matzov`** | **262.3356800074737** | **262.3356800074737** | **0.000e+00** |

**`196.3662433540` and `262.3356800075` are VERIFIED, not unverified.** Kyber-1024
reproduces to floating-point equality; Kyber-768 agrees to 3.938e-09 bits, ~8 orders
below the 0.001-bit scale at which anything in this campaign is stated and ~9 below the
1-bit scale that decides a NIST category.

### What this does and does not establish — read before citing

- It establishes that **the shim is not the source of the 768/1024 figures**. Two
  independent arithmetic backends (mpmath at 200 bits vs. Sage/MPFR) driving the same
  pinned estimator source land on the same numbers.
- **It is an implementation-agreement check, not a validation of the MATZOV cost model.**
  `lwe_dual.py:551` still reads `# p.29, we're ignoring O()`. Verifying that two
  interpreters compute the same truncated asymptotic says nothing about the asymptotic.
- **passagemath 10.8.7 is a redistribution/fork of SageMath, not upstream sagemath 10.9**
  (what `RUN-MLKEM-015-001` ran on, per its `raw-result.json`). For the 27-name surface
  the estimator uses these are the upstream Sage implementations, which is what the check
  needed — but it is not literally the same Sage build, and I do not claim it is.
- The known-answer control itself was **not** extended to cover `matzov`. Doing so is a
  shim change and I was instructed not to make one. **Recorded as needed, not made:** a
  `MATZOV_REFERENCE` block in `known_answer_control.py` carrying
  `139.6560414808584 / 196.3662433500587 / 262.3356800074737` with a stated tolerance
  (1e-8 would cover the observed 3.94e-09) would close the harness's largest remaining
  scope hole. That is a Coordinator decision, not mine.

---

## S2 — box widening: **nothing cheaper found, but the scan is PARTIAL**

### Why the optimiser's box is small

`MATZOV.__call__` (`lwe_dual.py:628-687`) searches `p` by `early_abort_range(2, q)`,
`k_enum` by `early_abort_range(0, n, 10)`, `k_fft` by `early_abort_range(0, n-k_enum, 10)`
— **step 10, with early abort** — and `beta` by `local_minimum(40, max_beta, precision=1)`,
which is a local, not exhaustive, search. Any of those could hide a cheaper point.

### On the prior informal scan

The Coordinator reports a 1701-point scan (β ± 40 step 4, `k_enum`/`k_fft` 0–40 step 5)
finding `+0.000000` bits. **That grid cannot have contained either incumbent.** The
reported optimum has `k_fft = 60` at Kyber-768 and `k_fft = 120` at Kyber-1024; both lie
outside `0–40`. A grid that excludes the incumbent trivially fails to beat it, so that
scan is not evidence of optimality in the direction it was read.

### What was actually scanned

Box declared: β ∈ [incumbent ± 176] step 8 and [incumbent ± 24] step 1; `k_enum` 0–156
step 6 and ± 15 step 1; `k_fft` 0–252 step 6 and ± 15 step 1; `p` ∈ {2,3,4,5,6,7,8}.
That is materially wider than the optimiser on `k_enum`/`k_fft` (which it caps by early
abort) and materially **finer** (step 1 and 6 vs. the optimiser's step 10).

| set | points evaluated | `cost()` exceptions | best found | improvement over incumbent |
|---|---|---|---|---|
| Kyber-768 | 187,775 | 0 | 196.3662433539967 | **+0.000000 bits** |
| Kyber-1024 | 187,873 | 0 | 262.3356800074737 | **+0.000000 bits** |

**Both stages were truncated by the time budget**, and this materially limits the
conclusion. Exact β coverage, recovered arithmetically from the run's own
`points_evaluated` counts (the deadline is tested only at the top of the β loop, so every
count is an exact multiple of the per-β plane; all four remainder checks are 0):

| set | stage A declared β | stage A β **scanned** | stage B declared β | stage B β **scanned** | incumbent β |
|---|---|---|---|---|---|
| Kyber-768 | 413–765 step 8 (45 values) | **413–517 (14 values)** | 565–613 step 1 | **565–575 (11 values)** | **589 — not scanned** |
| Kyber-1024 | 647–999 step 8 (45 values) | **647–759 (15 values)** | 799–847 step 1 | **799–817 (19 values)** | **823 — not scanned** |

So the honest statement is: **across ~188k points per set, spanning `k_fft` up to 252,
`k_enum` up to 156 and `p` up to 8 — all far outside the prior informal box — nothing beat
the incumbent, at the β values actually reached.** The incumbent's own β and the region
above it were not reached. **S2 does not establish global optimality**, and the
Carrier-agreement question ("is the optimum a property of the box?") is not settled by it.
What S2 does do is remove the specific failure mode of the prior scan: the wide
`k_fft`/`k_enum`/`p` region that scan never entered contains nothing cheaper in the β band
examined.

---

## S3 — null object: one null ran, one did not

### NULL-1 (Kyber-specificity removed) — **implementation_error, no data**

Design: run the identical comparison (`primal_bdd` vs `matzov`, `RC.MATZOV`, `log2 rop`)
over 24 Kyber-*shaped* but non-Kyber LWE parameter sets (n ∈ [256,1280], q ∈ {769 … 40961},
centred-binomial η ∈ [1,5], m = n), seeded `random.Random(20260803)`. If the margin is
positive across the ensemble, "matzov < primal_bdd" is a generic property of the two cost
functions and says nothing about Kyber. This is the null DEF-7 asked for.

**It produced zero data points.** All 24 raised
`AttributeError: type object 'NoiseDistribution' has no attribute 'CenteredBinomial'`.

Root cause, verified by reading the pinned source: in `3e48ef4`, `CenteredBinomial` is a
**module-level class** in `estimator/nd.py:296`, not a method of `NoiseDistribution`
(`nd.py:69`); `estimator/schemes.py:22` uses it that way. The repair is one line:
`from estimator.nd import CenteredBinomial` and `Xs=CenteredBinomial(eta_s)`.

**Not repaired, not rerun.** `budget.maximum_runs = 1` and that run is spent. Re-running
would exceed a hard budget limit; a repair needs a new run allocation from the
Coordinator. The failure class is `implementation_error` — under `agents/executor.md` it
is **not** empirical evidence in either direction, and nothing is inferred from it. Since
BATCH-012 is the final authorised batch, **DEF-7's null of the right shape goes unrun for
a second consecutive batch unless the Coordinator allocates a successor run.** I flag that
as the single largest gap this task leaves open, and the cheapest to close.

### NULL-2 (MATZOV reduction frame removed) — **completed**

Design: the same comparison at the same three Kyber sets under reduction cost models
**other** than `RC.MATZOV`. ANOM-3 is stated inside the `RC.MATZOV` frame; removing that
frame removes the signal ANOM-3 is attributed to.

margin = log2 `primal_bdd` − log2 `matzov`, in bits:

| cost model | Kyber-512 | Kyber-768 | Kyber-1024 |
|---|---|---|---|
| ADPS16 | +3.9035 | +8.7450 | +14.3137 |
| BDGL16 | +0.4094 | +4.6595 | +10.2999 |
| LaaMosPol14 | **−1.6229** | +3.0086 | +6.8957 |
| CheNgu12 | +76.4172 | +165.8718 | +279.5573 |
| ABLR21 | +68.9771 | +159.6892 | +277.6238 |
| ChaLoy21 | +2.0676 | +5.5032 | +10.1225 |

**matzov undercuts primal_bdd in 17 of 18 cells (0.9444).** The single exception is
`LaaMosPol14` at Kyber-512.

Observation, recorded without conclusion: the ordering is very nearly invariant to the
reduction cost model, including under `CheNgu12` and `ABLR21` — enumeration-style models
where a +76 to +280 bit dual-over-primal gap is not credible as an attack comparison. The
comparison therefore returns the same ordering in frames where its output is not
believable. Whether that makes the ordering robust or makes it uninformative is a
judgement I do not make. It does mean the ordering is **not** specific to the `RC.MATZOV`
frame ANOM-3 is stated in.

---

## S4 — decay test, extended to 2^24 and 2^32: **completed**

Recipe (the BATCH-011 red team's, extended): subclass `MATZOV`, multiply `Nf`'s return by
2^δ, change nothing else, re-run the **full** optimiser so β, `p`, `k_enum`, `k_fft` are
re-chosen under the inflated N. `primal_bdd` is unchanged — the inflation is a statement
about the dual attack's sample requirement only. The subclass reproduces the pinned
optimum at δ = 0 to 4.16e-11 / 3.33e-12 / 2.63e-11 bits before any inflated row is
reported.

margin = log2 `primal_bdd` − log2 `matzov(N·2^δ)`, in bits:

| set | δ=0 | 1 | 2 | 4 | 8 | 16 | **24** | **32** | δ_flip |
|---|---|---|---|---|---|---|---|---|---|
| Kyber-512 | +0.543432 | +0.276399 | +0.076049 | −0.331512 | −1.133565 | −3.246362 | −6.197442 | −13.892838 | **2.7773** |
| Kyber-768 | +4.592472 | +4.592470 | +4.305263 | +3.884454 | +3.024729 | +0.728911 | **−1.515536** | −3.559786 | **19.6716** |
| Kyber-1024 | +8.387943 | +8.187715 | +8.163606 | +7.688228 | +6.923698 | +5.233394 | **+3.637196** | **+1.974121** | **> 32** |

Flip points by bisection with full re-optimisation at each fractional δ (14 iterations,
bracket width < 1.3e-4):

- **Kyber-512: δ_flip = 2.77728** bits — N understated by a factor of **6.856**.
- **Kyber-768: δ_flip = 19.67163** bits — N understated by a factor of **8.351 × 10^5**.
- **Kyber-1024: no flip within δ ≤ 32.** Margin is still **+1.974121** bits at N × 2^32.

Two things to record precisely:

1. **Kyber-768 and Kyber-1024 now flip, or approach flipping, where they did not before.**
   The red team's table stopped at 2^16 and reported "> 16" for both. Extending to 2^24
   shows Kyber-768 flipping at δ ≈ 19.67, and Kyber-1024 decaying monotonically from
   +8.388 to +1.974 across δ = 0 → 32. So **the quantity does decay under the parameter
   meant to destroy it on all three sets**; the inventor-protocol artifact tell (a
   quantity that never decays) is **not** triggered here. Kyber-1024 simply needs more
   than 32 bits of N-understatement.
2. **My Kyber-512 flip point (2.7773) differs from the red team's ≈ 2.3732.** The
   discrepancy is explained and is not a disagreement about the estimator: 2.3732 is what
   linear interpolation between the δ=2 and δ=4 rows gives
   (2 + 2·0.076049/(0.076049+0.331512) = 2.3732). 2.7773 is what re-optimising the attack
   at fractional δ actually gives. **Interpolation understates the flip point** because
   the optimiser recovers some of the loss. The δ=0/1/2/4/8/16 rows themselves agree with
   the red team's to the digits both reported, so the tables are consistent.

The direction of the sensitivity is unchanged and I state it in the direction it falls: at
Kyber-512 a factor-6.9 understatement of N erases the undercut — well inside the
uncertainty the Ducas–Pulles objection opens — while at Kyber-768/1024 it takes 2^19.7 and
more than 2^32. I do not know Ducas–Pulles's repaired constant and did not invent one.
This is a sensitivity, not a correction.

---

## S5 — c\* per attack. **No value is transferred between attacks.**

Definition (`EV-MLKEM-020`'s, not invented here): **c\* = (NIST classical cutoff bits −
log2 rop) / log2 M**, the memory-charge exponent at which charging `rop · M^c` reaches the
cutoff. Both memory recipes are stated; neither is preferred.

- **Model A** (EV-MLKEM-020's own, sieve only): `log2 M = 0.2075·b + log2 b`, with `b` =
  the attack's own sieve dimension. For `matzov`, `b` is its reported `beta_`
  (= 391 / 583 / 804).
- **Model P** (BATCH-011 red team's, peak including the FFT table):
  `log2 M = log2(2^(0.2075·b + log2 b) + p^k_fft)`. The `p^k_fft` term is an **inference**
  from `T_fftf`'s `p**(k+1)` at `lwe_dual.py:513` — labelled as an inference, not a
  quotation from MATZOV-2022.

### These values belong to `estimator.lwe_dual.matzov` (class `MATZOV`) under `RC.MATZOV`. Only.

| set | log2 rop (matzov) | cutoff | margin (bits) | β_sieve | k_fft, p | Model A log2 M | **c\*_matzov (A)** | Model P log2 M | **c\*_matzov (P)** |
|---|---|---|---|---|---|---|---|---|---|
| Kyber-512 | 139.656041 | 143 | +3.343959 | 391 | 50, 5 | 89.743545 | **0.037261** | 116.096320 | **0.028803** |
| Kyber-768 | 196.366243 | 207 | +10.633757 | 583 | 60, 4 | 130.159933 | **0.081698** | 130.161135 | **0.081697** |
| Kyber-1024 | 262.335680 | 272 | +9.664320 | 804 | 120, 4 | 176.481061 | **0.054761** | 240.000000 | **0.040268** |

Both prior computations are reproduced: Model A gives `0.0373 / 0.0817 / 0.0548`, matching
`DEC-20260803-85adf8` CE-1's `corrected_values`; Model P gives `0.028803 / 0.080877 /
0.040268` — my 512 and 1024 match the BATCH-011 red team's OBJ-4 exactly, and my 768 Model
P (0.081697) sits essentially on Model A because at Kyber-768 the FFT table `4^60 = 2^120`
is *below* the sieve's `2^130.16`, so peak memory is sieve-dominated there.

### The prohibited transfer, stated explicitly

`EV-MLKEM-020`'s **c\* ≈ 0.0316 / 0.0459 / 0.0071 belongs to
`estimator.lwe_primal.primal_bdd`.** It is quoted here only with that owner label and is
**not** applied to `matzov` — that substitution is exactly the error
`DEC-20260803-85adf8` records as CE-1. In particular the figure **0.007 is primal_bdd's at
Kyber-1024 and must not travel with ANOM-3**; matzov's own Kyber-1024 value is 0.0548 (A)
or 0.0403 (P), 5.7× to 7.8× larger. I did not recompute `primal_bdd`'s memory at all:
`primal_bdd` never calls `short_vectors` and so reports no `beta_sieve`, and inventing one
would be the same class of error in the other direction.

Recorded without conclusion: every value in the table is still one to two orders of
magnitude below 1/3, so nothing here disturbs `EV-MLKEM-020`'s qualitative finding that
memory charging dissolves the *security* reading. And the blunt fact from OBJ-4 stands
unchanged: at Kyber-1024 Model P's FFT table is **2^240 cells** against a claimed total
cost of 2^262.34.

---

## What survives, what does not, what remains uncheckable

**Survives.**
- The two load-bearing numbers are now checkable and check out. `196.3662433540` and
  `262.3356800075` reproduce under real Sage (passagemath 10.8.7) with the shim off the
  path, to 3.94e-09 and 0.0 bits. The "no Sage reference covers this path" concern is
  answered for the instrument, though not for the model. (S1)
- The margins are exactly as reported: **+0.543432 / +4.592472 / +8.387943** bits, with
  `primal_bdd` reproducing to delta 0.0 and `matzov` to ≤ 4.2e-11. (S0)
- The undercut is not an artifact of a narrow `k_enum`/`k_fft`/`p` box in the region
  examined: ~188k points per set at 768/1024, spanning far outside the optimiser's step-10
  early-aborting search, produced `+0.000000` bits of improvement. (S2, partial)
- The quantity **does** decay under N-inflation on all three sets, so the canonical
  inventor-protocol artifact tell is not triggered. (S4)

**Does not survive, or is weakened.**
- The prior informal 1701-point scan's `+0.000000` result should not be cited as evidence
  of optimality: its `k_fft` range `0–40` excluded both incumbents (60 and 120). (S2)
- My own S2 is **partial**: both stages truncated, and neither incumbent's own β was
  scanned. It does not establish global optimality and should not be cited as if it did.
- The red team's Kyber-512 flip point ≈ 2.3732 is an interpolation; re-optimisation gives
  **2.7773**. The qualitative reading is unchanged. (S4)
- The ordering is nearly invariant to the reduction cost model — 17 of 18 cells, including
  under enumeration models where a +280-bit gap is not believable. Whatever the internal
  comparison is measuring, it is not specific to the `RC.MATZOV` frame ANOM-3 is stated
  in. (S3 NULL-2)
- ANOM-3's *security* reading remains dissolved twice over, untouched by anything here.

**Remains uncheckable in this environment.**
- **DEF-7's null of the right shape (NULL-1) did not run** — `implementation_error`,
  one-line repair recorded, `maximum_runs = 1` spent. This is the largest gap I leave.
- Upstream **sagemath 10.9** specifically (what `RUN-MLKEM-015-001` used) remains
  unobtainable here: no apt candidate, no wheel, source build blocked on PARI/GP.
  passagemath 10.8.7 is a redistribution, and I do not claim it is the same build.
- The **MATZOV cost model itself**. `lwe_dual.py:551` still reads
  `# p.29, we're ignoring O()`. Two backends agreeing on a truncated asymptotic is
  agreement about arithmetic, not about the asymptotic. The Kyber-512 margin of 0.543432
  bits remains smaller than a single dropped factor of 2.
- `arora_gb`, `dual` and `primal_hybrid` remain unavailable in this harness (verified by
  running them, per the control's own output), so no "best attack overall" claim is
  possible.

**My read, offered as an executor observation and not as a verdict.** The instrument
objection against ANOM-3's internal comparison is now the weaker of the two live
objections: the numbers are real, reproduce across independent arithmetic backends, and
survive a much wider parameter box than anyone had checked. What has *not* moved is the
model objection — the two sides of the comparison are not costed in one frame, one of them
drops an admitted O(), neither exposes a success probability, and the ordering reappears
in frames where it cannot be believed. Deciding whether that makes the internal comparison
a finding or an artifact is the Reviewer's and Coordinator's call, not mine.

---

## Protocol deviations, defects, and anomalies — all recorded, none discarded

| id | class | description |
|---|---|---|
| DEF-A | `implementation_error` | S3 NULL-1 used `NoiseDistribution.CenteredBinomial`; in `3e48ef4` `CenteredBinomial` is a module-level class in `estimator/nd.py:296`. 24/24 points errored, 0 evaluated. Not repaired: `maximum_runs = 1` spent. |
| DEF-B | `implementation_error` | S1's archived-coverage sub-check computed the repo root 6 levels above `TASK_DIR` instead of 7; both file reads returned `FileNotFoundError`. The coverage fact is established instead by direct inspection and is reported above. No reported number depends on it. |
| DEV-1 | `resource_exhaustion` (bounded, by design) | S2 stages A and B were both truncated by their time budget on both sets. Exact β coverage recovered and recorded in `results.json` → `S2_beta_coverage_post_run_annotation`. |
| ANOM-A | unexpected observation | The known-answer control's dual reference does not cover the ANOM-3 callable at **any** parameter set, not only 768/1024 — `dual_hybrid` (module-level, `DualHybrid`) and `matzov` (`MATZOV`) are different objects. Recorded; the needed control extension is described but **not made**. |
| ANOM-B | unexpected observation | S1 succeeded where prior attempts failed, via a route not previously tried (`passagemath` binary wheels). The Coordinator's apt and pip-source findings were both re-checked and both confirmed. |
| ANOM-C | unexpected observation | NULL-2 returns the same ordering under `CheNgu12`/`ABLR21` with +76 to +280 bit margins, which are not credible as attack comparisons. |
| ANOM-D | unexpected observation | Kyber-768 flips at δ ≈ 19.67, which the red team's table (stopping at 2^16) recorded as "> 16". Kyber-1024 still has +1.974 bits of margin at 2^32. |
| — | inference substitution | Requested policy `executor-implementation` resolves to `anthropic:claude-sonnet-5`; the session is actually served by `claude-opus-5`. `fallback_allowed: true` in the handoff. Recorded as `fallback_used: true` in `receipt.json`, not silently accepted. |

**Nothing outside the write scope was modified.** `git status --porcelain` at run time
listed exactly one path: `coordination/goals/GOAL-MLKEM-003/batches/BATCH-012/tasks/`.
`tools/sage_free_estimator` is byte-identical to the committed tree. No `git commit` was
run. Package installs went into a throwaway venv at `/tmp/sagevenv`, not into the
interpreter that ran the control or the checks.

## Artifacts

- `reserve_checks.py` — the exact script run
- `results.json` — S0–S5 machine-readable, with `check_status` and `S2_beta_coverage_post_run_annotation`
- `sage_attempt_transcript.txt` — every S1 command and its exact output
- `run_stdout_raw.log`, `run_stdout.log`, `run_stderr.log` — run output
- `report.md` — this file
- `receipt.json` — state, commands, environment, timestamps, inference block
