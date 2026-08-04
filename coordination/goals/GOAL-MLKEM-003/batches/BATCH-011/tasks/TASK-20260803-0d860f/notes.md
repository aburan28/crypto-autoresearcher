# Validation notes — TASK-20260803-0d860f

**Validator, GOAL-MLKEM-003 / BATCH-011. Supersedes TASK-20260803-e09290.**
Reviewed snapshot `12e97be8e04ebf685b5ba326b01241c06eb7c8e0`, package
`tasks/TASK-20260803-fb52f4/`. Verdict: **ADMISSIBLE_WITH_DEFECTS**, twelve
numbered defects, none of which changes a reported number except DEF-8
(0.01–0.35 bits, and it makes the residual *larger*).

Everything below is a **cost-model estimate**. Nothing was measured. No ML-KEM
break is claimed or implied, and nothing here is a security proof in either
direction. AGENTS.md rule 12 is UNMET and UNWAIVED; ANOM-3 stays gated and no
record changes.

---

## 0. Supersession disclosure

TASK-20260803-e09290 died on a provider session limit before writing anything.
The harness's shared scratchpad contains a directory named `val_e09290` and two
files named `rt_e29029_probe.*`. I saw those names in a directory listing while
creating my own working directory, and did not open, read, execute or copy any
of them. Every number in this report came out of a script I wrote in this
session.

One thing I *did* inherit and must disclose: the lattice-estimator clone in the
scratchpad already existed when I started. I did not take it on trust — I
verified `git rev-parse HEAD` = `3e48ef421ec256afddb3e7d2249a77eab6e9ba12` and
`git status --porcelain` empty (no modifications, no untracked files) before
using it.

---

## 1. The control, first, on the current shim

The task card asked whether the control still passes after the shim gained
`.n()` and Real-returning helpers this batch. It does, exit 0, with output
byte-identical to the transcript archived in the package:

```
Kyber512   140.1994731076     140.1994731076   0.00e+00   389   422   1005
Kyber768   200.9587149141     200.9587149141   0.00e+00   606   640   1420
Kyber1024  270.7236234535     (no reference)         --   855   889   1867
Kyber512   143.7884782479     143.7884782479   3.13e-13     dual_hybrid(fft=True)
Kyber768   203.7878630676     203.7878630676   2.27e-13     dual_hybrid(fft=True)
```

There is a detail here worth more than it first looks. The producer ran against
the **pre-`0100fdbc` shim plus an in-process patch** whose `.n(prec)` *rounds to
`prec` bits*, faithfully to Sage. I ran against the **committed post-`0100fdbc`
shim**, whose `_Real.n()` *ignores* `prec` and returns the full 200-bit value,
and I applied no patch at all. So my run is not a re-execution of the producer's
under the same conditions — it is the same computation under the other rounding
convention. Agreement therefore *re-establishes* the producer's CTRL-4 null
instead of inheriting it. The deltas I see (0.0 / 1.41e-11 / 0.0 on S1) are
exactly the producer's own CTRL-4 figures.

---

## 2. D1 — the attack-function identity

**Reproduced, exactly, and it is the finding.**

The source facts, read at the pin:

- `estimator/lwe.py:13` → `from .lwe_dual import matzov as dual_hybrid`
- `estimator/lwe_dual.py:496` → `class MATZOV:`
- `estimator/lwe_dual.py:689` → `matzov = MATZOV()`
- `estimator/lwe_dual.py:742` → `def dual_hybrid(` (a *different*, module-level function)

Executed, not just read:

```
estimator.lwe.dual_hybrid is estimator.lwe_dual.matzov        -> True
estimator.lwe.dual_hybrid is estimator.lwe_dual.dual_hybrid   -> False
type(estimator.lwe.dual_hybrid).__name__                      -> 'MATZOV'
type(estimator.lwe_dual.dual_hybrid).__name__                 -> 'function'
```

My numbers, RC.MATZOV, pin `3e48ef4`:

| | Kyber512 | Kyber768 | Kyber1024 |
|---|---|---|---|
| S0 `lwe_dual.dual_hybrid(fft=True)` | 143.78847824788517 | 203.78786306762137 | 273.8172676850367 |
| S1 `lwe_dual.matzov` (= `LWE.dual_hybrid`) | 139.65604148085845 | 196.36624335399668 | 262.3356800074737 |
| **D1** | **+4.132436767026718** | **+7.421619713624693** | **+11.481587677563027** |
| D1 / (S0 − Carrier) | 96.36 % | 85.43 % | 81.33 % |

Producer: +4.132437 / +7.421620 / +11.481588 and 96.4 % / 85.4 % / 81.3 %. Delta
0.0 / 1.41e-11 / 0.0.

**The growth claim.** gap/β at β from S0 (402/616/865): 0.010668 / 0.014104 /
0.016321 — monotone, and it reproduces the Coordinator's scouting ratios.
residual/β after D1 only, at β from S1: 0.000403 / 0.002150 / 0.003203.
residual/β after D1–D4, at β from S4: −0.001264 / −0.001043 / +0.000373. The
β-scaling component does live in D1 (and D3), and what remains brackets zero.
The claim is sound. The *table* is not reproducible from a stated convention
(DEF-4): the printed −0.00125 / −0.00103 correspond to β = 386 and β = 589,
not to S4's own β, the row has no β column, and the table is absent from
`results.json` entirely. Fifth decimal; the conclusion survives every choice I
tried.

D1 is the one part of this package I would defend without qualification. It is
a source fact plus a deterministic evaluation. There is no statistics in it, so
there is nothing for a null object to be a null of, and no amount of cost-model
scepticism touches it — if you call a different function you get a different
number, and one of the two functions is not the one the record thought it was.

---

## 3. ANOM-3

**Reproduced.** primal_bdd 140.1994731076207 / 200.9587149140538 /
270.7236234535225 (β 389/606/855, η 422/640/889, d 1005/1420/1867 — identical to
the control and to RUN-MLKEM-015-001). matzov 139.65604148085845 /
196.36624335399668 / 262.3356800074737. Difference **+0.5434316267622421 /
+4.592471560057106 / +8.387943446048837**.

Against 143/207/272: matzov(S1) sits 3.343959 / 10.633757 / 9.664320 below;
matzov(S4) 3.984118 / 12.508231 / 11.995256 below; primal_bdd 2.800527 /
6.041285 / 1.276377 below.

### The strongest corroboration nobody in the batch used

The pinned upstream repository's **own committed doctest**, at
`estimator/lwe.py:124`, prints for Kyber-512:

```
bdd                  :: rop: ≈2^140.2, red: ≈2^139.1, svp: ≈2^139.3, β: 389, η: 422, d: 1005, tag: bdd
dual_hybrid          :: rop: ≈2^139.7, red: ≈2^139.5, guess: ≈2^135.9, β: 387, p: 5, ζ: 0, t: 50, β': 391...
```

My unpatched run gives rop 139.65604 (2^139.7), red 139.54662 (2^139.5), guess
135.88093 (2^135.9), β 387, p 5, ζ 0, t 50, β′ 391 — every integer exact, every
log2 to printed precision. So **the Kyber-512 instance of ANOM-3 is readable
directly from the upstream repository's own committed output**, with no shim, no
patch and no instrument of this program involved: 2^139.7 < 2^140.2. That is as
close to instrument-independent as this campaign can get, and it should be the
sentence any downstream record leads with.

### Three limits that must travel with the triple

1. **The coverage is inverted relative to the effect.** The only Sage-anchored
   reference for `matzov` is that Kyber-512 doctest, where the undercut is
   **0.543432 bits**. The headline 4.59 and 8.39-bit undercuts sit on paths with
   no reference at all (DEF-9). The producer says this in §8.1; the §7 table
   prints the triple unmarked, and so do the snapshot commit message and the
   Coordinator note.
2. **These are free-memory gate counts** and c* is per-attack (see §5 below).
3. **Both sides share the disputed law.** `matzov` implements the very `Nf`
   independence law Ducas–Pulles target, and prices no false positives at all.

---

## 4. Is EV-MLKEM-015 wrong, or correct-and-incomplete?

**Neither cleanly. It is correct in its measurements, over-general in one
clause, and materially wrong in its inference.** This is where I part company
with the Coordinator note, which frames the surviving half as "correct about the
function it named".

| locus | verdict |
|---|---|
| `observations[0]` sentence 1 — "dual_hybrid+fft … 143.79/203.79/273.82 … primal_bdd … 140.20/200.96/270.72" | **Correct and correctly scoped.** Reproduced exactly. It *names the function*. |
| `observations[0]` sentence 2 — "Dual does not beat primal (gaps +3.59/+2.83/+3.09 bits)" | **Arithmetic right (+3.589005/+2.829148/+3.093644), sentence over-general.** "Dual" is the family; one member was measured. Inside the same instrument, pin and cost model, `matzov` beats primal_bdd by 0.54/4.59/8.39. As written this is a claim about the family and it is false of the family. |
| `inference` — "…must justify ingredients beyond **the public MATZOV dual in lattice-estimator**" | **Materially wrong, and load-bearing.** It calls `dual_hybrid+fft` "the public MATZOV dual". It is not: `lwe.py:13` binds the public name to `matzov`, which already sits 4.13/7.42/11.48 bits below the bar the inference sets, with *no* ingredient beyond the public estimator. |
| `boundaries[1]` — "lattice-estimator matzov dual ≠ Carrier polar-code repair" | Intent still true; wording propagates the same conflation. |

So "merely incomplete" understates it, and "wrong" overstates it. The right
disposition is a **superseding record** (rule 4), not a retraction: keep the
numbers, restate sentence 2 as a statement about
`estimator.lwe_dual.dual_hybrid(..., fft=True)`, replace the inference with one
naming `estimator.lwe_dual.matzov` and its 0.54/4.59/8.39-bit undercut of
primal_bdd, and attach the two boundaries this batch establishes (Kyber-512-only
Sage cover; both models share the contested law). That is a Coordinator act,
gated on rule 12, which is unmet. I am not performing it and this report does
not authorize it.

### What a record should say when a public API name and its function diverge

1. **Name the callable, never the alias.** Scope statements carry the
   fully-qualified object invoked — `estimator.lwe_dual.dual_hybrid`
   (module-level function, EspJouKha/GJ21 hybrid) — not "the estimator's dual".
2. **Record both sides of every alias, with the line.** If the package rebinds a
   name, the record quotes the rebinding and says which side it ran.
3. **Make identity machine-checkable, not prose.** Emit `__module__`,
   `type(...).__name__` and the estimator's own `f_name` for every costed
   callable into `results.json`, so a later reader diffs a *field*. The argument
   is this campaign's own history: a one-line alias survived EV-MLKEM-015, four
   batches and a Coordinator scouting exercise because identity lived in a
   sentence.
4. **State non-coverage positively.** Name the siblings in the same module you
   did *not* run, and why. "Dual does not beat primal" is unwritable under that
   discipline.
5. **Scope the verb to the object.** Generalising from one callable to a family
   is a separate claim with its own evidence, inheriting the weakest control
   covering any member.

---

## 5. The Coordinator note: both facts confirmed, split accepted with one
amendment and one correction

**Fact 1 — CONFIRMED.** `class MATZOV` at 496, `def Nf(` at 526, `mu = 0.5` at
539. `N` is a closed form in the parameters:
`exp(4(σ_s π/q)²)·exp(k_fft/3·(σ π/p)²)·(k_enum·H + k_fft·log p + log(1/μ))`,
annotated "`# p.29, we're ignoring O()`". No covariance, no correlation
coefficient, no dependence structure between score contributions, nothing
data-dependent. `mu` enters only as `log(1/mu)` and is never an argument. The
note's quoted excerpt is faithful.

**Fact 2 — CONFIRMED, and stronger than stated.** `Pwrong|false_pos|fpfn|Phi_inv`
over lines 496–700 returns **0**; over the *whole* 796-line file it also returns
**0**. The range is the right one (`matzov = MATZOV()` is at 689). There is no
outer repetition and no amplification term on that path.

I add one corroboration the note does not use, which makes the asymmetry
concrete rather than inferential: **Carrier's archived Table C.2 carries both a
`log2(Pwrong)` column (−119.57 / −177.79 / −244.03) and a `log2(R)` repetition
column (9.39 / 9.49 / 15.15)**, under a caption reading "We recall that
P_good ≈ 0.5". Both sides target ≈0.5 success; only one of them prices the
consequences. The producer records this as H17 *unsized* and refuses to absorb
it into the residual, which is the correct handling — and it means the surviving
MATZOV-2022 residual (+1.52 / +0.99 / +2.20) is not bounded by anything in the
package.

**The split.** Accepted. The "estimator reproduces Carrier" agreement really is
weak corroboration when both sides make the disputed assumption, and ANOM-3's
internal content really does stand or fall on the function identity alone, which
I verified independently. Two changes:

- **Amendment**: EV-MLKEM-015 is not merely "correct about the function it
  named" — its *inference* misidentifies the function. See §4.
- **Correction, and this one matters for what travels downstream**: the note's
  "Unchanged and reinforcing" paragraph transfers EV-MLKEM-020's
  c\* ≈ 0.007 to the ANOM-3 undercut. **c\* is per-attack** — EV-MLKEM-020 says
  so in its own boundaries ("c\* is the critical exponent OF primal_bdd … the
  scheme-level exponent is a MAXIMUM over the attack frontier and is unknown").
  `matzov` has a *larger* margin and a *smaller* sieve, so its c\* is larger.
  Carrying EV-MLKEM-020's own Model A convention across
  (log₂M = 0.2075·β_sieve + log₂β_sieve at β_sieve = 391/583/804, margins
  +3.343959 / +10.633757 / +9.664320):

  | | Kyber512 | Kyber768 | Kyber1024 |
  |---|---|---|---|
  | c\* primal_bdd (EV-MLKEM-020) | 0.03164649 | 0.04588645 | 0.00705473 |
  | c\* matzov (my arithmetic) | **0.037261** | **0.081698** | **0.054761** |

  Up to **7.8×** larger at Kyber-1024. The note's *qualitative* point survives
  intact — 0.08 is still one to two orders below every named hardware convention
  and far below 1/3 — but "as small as 0.007" is the wrong number for the dual
  and must not travel with ANOM-3. My figures are indicative arithmetic under a
  memory model EV-MLKEM-020 itself downgraded to
  `construction_with_partial_support`; they are `unable_to_check` for provenance
  and are recorded here to stop a wrong figure entering a durable record, not to
  assert a right one.

Per the task card, having confirmed both facts I did not re-derive them further.

---

## 6. D2 / D3 / D4 and the residuals

I re-implemented the stage searches from the *description* of the boxes, sharing
no code with the producer. Stages 2 and 3 landed on the **identical argmin
points** on all three sets — `(p, k_enum, k_fft, β)` = (5,7,42,386) / (4,23,59,586)
/ (4,3,115,823), then m = 481 / 644 / 814 — which is a stronger version of the
producer's CTRL-7 than CTRL-7 itself: a refiner optimising a different objective
could not land there from a different code path.

| | Kyber512 | Kyber768 | Kyber1024 |
|---|---|---|---|
| D2 (mine) | +0.29948707477905 | +0.81205389811271 | +0.33545680658926 |
| D2 (producer) | +0.2994870747896 | +0.8120538989870 | +0.3354568067037 |
| D3 (mine) | +0.03474449121018 | +1.06242042179599 | +1.99547908544287 |
| D3 (producer) | +0.0347444912104 | +1.0624204227522 | +1.9954790857849 |

**D4 is the one place my search did worse than the producer's, and the cause is
mine.** Both sweeps step β_sieve by 2. My start point came from S1's β′ = 391,
making my grid **odd**; the producer's came from S3's β′ = 390, making theirs
**even**. I never evaluated 390 and found 139.05611 at β_sieve = 389
(D4 = +0.2657); the producer found 139.01588 at 390 (D4 = +0.305928). I then
evaluated the producer's point directly: **139.01588189973273** against the
claimed 139.0158818997194, delta 1.33e-11. The producer's D4 is correct and mine
is the weaker search. I record it (DEF-10) because it demonstrates that D4 is
grid-artifact-sensitive at the 0.04-bit level, which reinforces the producer's
own §8.4 statement that D2+D3+D4 *understates* estimator-side slack. A step-1
sweep costs ~2 s.

**Residuals.** All reproduced: after D1 only, vs Carrier +0.156041 / +1.266243 /
+2.635680; after D1–D4, **−0.484118 / −0.608231 / +0.304744**; vs MATZOV-2022
+2.156041 / +2.866243 / +4.535680 then +1.515882 / +0.991769 / +2.204744.
Attributed total +4.772596 / +9.296094 / +13.812524.

**Is the negative residual stated or hidden? Stated, in three places, and
correctly interpreted.** `run_stdout.log` lines 70/80/90 print
"UNATTRIBUTED RESIDUAL −0.4841 / −0.6082"; `results.json` carries the signed
value plus `fraction_attributed` above 1.0 (1.1129 / 1.0700); and `gap_report.md`
§4 says "This **over-attributes** … A negative residual is not a tighter
explanation; it means the true attribution lies **between** the two rows. Stated
rather than suppressed." I looked specifically for the failure mode where the
tighter-looking row is promoted to the headline, and it is not there — §2 and
§6(2) give both rows, and §4 labels the like-for-like row the honest comparison.
That is the right call and it deserves saying.

---

## 7. The four rejected explanations — sound, or convenient?

| axis | my numbers | verdict |
|---|---|---|
| sieve cost model (`RC.GJ21 − RC.MATZOV`) | 5.555101 / 6.546499 / 6.246213 at β_sieve 391/583/804 | **sound but under-powered** |
| dimensions-for-free | +7.998375 / +10.305508 / +12.991238; d4f(β\*) 35.677 / 47.858 / 61.099 | **sound but under-powered** |
| core-SVP vs gates | 24.146148 / 22.041836 / 20.580049 | **sound, and discriminating** |
| Carrier table arithmetic | 9/9 C.1 splits; C.2 sums 139.510031 / 194.810446 / 259.350009 | **sound, and I extended it** |

The isolation argument for the sieve axis is source-true: `class MATZOV(GJ21)`
at `reduction.py:963` overrides nothing but `__name__` and the `NN_AGPS` table,
and `class GJ21(Kyber)` at :860 inherits `d4f`, applied at :903. MATZOV's own
archived text says "the cost of sieving is reduced by ≈ 6 bits in rank 400"
(`matzov_v2_loci.txt:10-11`); 5.56 bits at sieve dimension 391 is a fair
reproduction. Both unit declarations are verbatim in the archive
(`matzov_v2_loci.txt:36`, `carrier_hal_front_matter.txt:56`), as is the
dimensions-for-free passage (`matzov_v2_loci.txt:12-19`).

**Not convenient — but rejected only at the resolution of the gap, not of the
residual, and the report does not say so (DEF-6).** §5(1) says the sieve
re-costing "cancels and explains none of the gap". The cancellation is exact
only if Carrier's nearest-neighbour fit is *coefficient-identical* to
`RC.MATZOV`'s `NN_AGPS`, and the only archived evidence for that is one abstract
phrase. A 15–35 % coefficient mismatch inside a term worth 5.56/6.55/6.25 bits
would by itself cover the *entire* surviving MATZOV-2022 residual
(+1.52/+0.99/+2.20). Same shape of argument for d4f, worth 8.00/10.31/12.99:
"applied by both sides" is sourced for *existence*, not for *magnitude*.

I do not think this is motivated reasoning. The rejections are not load-bearing
for the headline — D1 is a source fact — each axis is sized honestly, and the
core-SVP rejection is genuinely discriminating on both magnitude and *sign*
(the unit gap *shrinks* 24.15 → 20.58 while the observed gap *grows* 4.29 →
14.12). They are simply under-powered for the one thing §6(3) leans on them for.

**I extended CTRL-5.** As written it checks `n_enu + n_fft + n_lat = n` on the
*transcribed dict* — it would pass on a mistyped table. I checked the
transcription itself against
`inputs/MLKEM-DUAL-SOURCES-20260802/extracts/carrier-hal-05406481/page37_tables_C1_C2.txt`:
all nine C.1 rows and all three C.2 CC rows, every field. Correct.

---

## 8. Controls, and the null that is missing

The inventor protocol's controls-before-belief obligation is **partially met**,
and the gap is on the *second* headline rather than the first.

- **D1 needs no null.** Two distinct callables, deterministic evaluation, no
  statistical content.
- **The decay test is answered, and answered well, for the growth claim.** The
  parameter meant to destroy the signal is the decomposition itself; the report
  predicts residual/β should stop scaling; it does; and the over-shoot into
  negative territory is reported rather than trimmed. That is the protocol's
  canonical artifact tell being checked *and* failing to fire.
- **The missing null is for the reproduction claim** (DEF-7). "The pinned
  estimator reproduces Carrier's published headline to −0.48/−0.61/+0.30 bits"
  has **no measured false-positive rate**. CTRL-6 mis-pairs *parameter sets* and
  produces +67.24 / −120.04 — magnitudes at which no sign-locked bug could
  survive, so it cannot fail informatively. CTRL-7 is a real control on a
  different question. The null of the right shape is free and already archived:
  run the identical S1→S4 machinery against a target it should **not** reach —
  Carrier's own C0 row (Table C.2 `log2(Tsample)` 115.76 / 172.70 / 238.98) or CN
  row (143.30 / 189.78 / 254.44), or a target shifted ±3 bits — and show the
  residual does not collapse under a bit. The machinery moves the estimator by
  0.64 / 1.87 / 2.33 bits (S1→S4), i.e. the same order as the residual it is
  being used to explain. Until that is run, "lands on the same number" is
  uncontrolled.

Negative controls that *are* present and do work: CTRL-4 (rounding null,
discriminating, now replicated across sessions and conventions); and the
estimator's own loud failures — `arora_gb`, `dual`, `primal_hybrid` and
`matzov` under `RC.Kyber` all raise rather than returning a wrong cost, and the
producer verified that by running them rather than asserting it.

---

## 9. Anomalies and DEV-1

**ANOM-1** verified independently: `75f6c8e0` (03:29:53) → `428bb713` (03:41:23,
a merge of origin/main), 28 files changed,
`git diff --stat` over `tools/sage_free_estimator` and
`inputs/MLKEM-DUAL-SOURCES-20260802` **empty**. Recorded, impact checked, impact
none. Model handling.

**ANOM-2** verified at the source, and it is visible in my own numbers: at
Kyber-512 S1 the automatic path reports β = 387 with β′ = 391, so `Nf` is
evaluated at 387 while reduction is charged at 391. Stage 4 is therefore not a
pure relaxation — which the producer states in the stage-4 docstring and in the
report — and it means D4's sign is not guaranteed a priori, so the Kyber-768/1024
zeros are informative rather than trivial.

**ANOM-4** verified: C.2 CC sums 139.510031 / 194.810446 / 259.350009, i.e.
−0.010031 above and +0.289554 / +0.349991 below the abstract-derived headlines;
sampling term dominates to 3.1e-05 / 4.5e-04 / 9.2e-06 bits. Correctly recorded,
correctly unresolved (Table 5.1 is not archived), correctly not blamed on the
estimator. **Not** correctly propagated: measured against Carrier's own table
rather than the abstract, the like-for-like residual is +0.146010 / +1.555798 /
+2.985671, not +0.156 / +1.266 / +2.636 — Kyber-768 up 23 %, Kyber-1024 up 13 %
(DEF-8). The published target is itself ambiguous by 0.29–0.35 bits and the
headline sentence should carry that.

### DEV-1 — was following the objective the right call?

**Yes, and it was the only defensible call.** The handoff is internally
inconsistent: `objective` and `artifact_paths` specify the gap decomposition and
name `dual_gap_decomposition.py` / `gap_report.md`, while `deliverables` and
`completion_gate` are BATCH-010 text naming `memory_charged_derivation.py`,
`derivation_report.md` and c\*. Four reasons, in decreasing weight:

1. **The stale items are not satisfiable, not merely inconvenient.**
   c\* = margin / log₂M needs a memory figure and a gap decomposition produces
   none. Producing one would have meant inventing a memory model for an attack
   whose estimator module supplies no memory at all — which is *precisely* the
   defect EV-MLKEM-020 records against BATCH-010 (H4/H5: "the memory model is
   borrowed, not derived"). Obeying the stale gate would have manufactured the
   exact artifact the previous batch was criticised for.
2. **The handoff resolves itself.** `objective` and `artifact_paths` are the
   blocks the dispatcher binds and the archive verifies; `artifact_paths` names
   the gap-decomposition files; and the Coordinator then *amended*
   `artifact_paths` to add the log files, i.e. acted on the gap-decomposition
   reading. Three signals against one.
3. **The alternative is worse for the program.** Halting on a Coordinator
   specification error burns the batch and produces nothing reviewable, and rule
   9 treats abandoning a live lead as symmetric with overclaiming. KN-OPEN-016's
   headline question was the live lead — and the batch went on to overturn the
   Coordinator's own premise, which is the outcome a halt would have forfeited.
4. **The deviation was declared, classified and itemised.** DEV-1 names it a
   `specification_error, non-blocking`; the two stale gate items are *carried* in
   `completion_gate` marked `[STALE GATE ITEM]` / `not_applicable` with reasons
   rather than deleted; and the transferable parts (β and d per set, agreement
   with the control) were satisfied anyway.

One residual criticism. The stale gate also carried "the memory unit is stated
and the conversion shown", answered with "no memory figure is used anywhere in
this package". True of the package, but not of the reading a reviewer wants,
because ANOM-3's significance *does* turn on a memory charge. Sizing c\* for
`matzov` was out of scope and correctly skipped — but a one-line pointer to
EV-MLKEM-020 beside the ANOM-3 table would have pre-empted the Coordinator
note's mis-transfer of 0.007 (DEF-12), which is now sitting in the tree
unreviewed.

This is a Coordinator defect. The producer's handling of it is the model.

---

## 10. Two archive-integrity findings

**DEF-1.** `snapshot_receipt.json` has `commit_sha: null`, `parent_sha: null`,
`verification.status: "pending_post_commit"`. The dispatcher's post-commit
verifier cannot run against a null SHA. I did all four checks by hand and they
pass — `12e97be8e04e` is an ancestor of HEAD `6876940e3fdc`, changes exactly the
seven declared paths plus the receipt, all seven sha256 preserved, message names
the tasks and the goal — but the receipt does not carry the binding AGENTS.md
requires.

**DEF-2.** The reviewed snapshot's tree does not contain the instrument the
package was produced with. The producer honestly pins
`shim/sage/all.py` at `6f93583d…702` (the file at `0100fdbc^`); the tree at
`12e97be8e04e` carries `32d60a64…aab`, because commit `0100fdbc` landed **31
seconds** before the snapshot. Checking out the reviewed snapshot and re-running
the archived command exercises a *different* instrument. This is the third
recurrence of the class EV-MLKEM-020 records as EI-2, and the second involving
this shim.

Three mitigations, and one thing they do not buy. Mitigations: the change is at
least **committed** this time, with a message and a `Found-by:` attribution,
unlike BATCH-010's uncommitted edit; I ran the whole recomputation on the new
shim and every number reproduced to ≤ 1.9e-09 bits; and the control passes
byte-identically on it. What that does not buy: the bound came from a reviewer
*running* it, not from the archive. The general remedy is cheap — a snapshot
should either include the instrument among its declared paths or record the
instrument hash it certifies.

Relatedly, `tools/sage_free_estimator/README.md` still prints the old three-line
control transcript and says "The control covers `primal_bdd` under `RC.MATZOV`",
while the control now also covers `dual_hybrid(fft=True)` at Kyber-512/768
(DEF-3). On an instrument whose stated raison d'être is "the control is the
whole point", documentation drift about *control coverage* is the wrong kind of
drift.

---

## 11. What I could not check

- **Whether either cost model is correct.** I reproduced arithmetic, source
  citations and controls. I did not and could not establish that
  lattice-estimator's MATZOV cost function, Carrier's analysis, or MATZOV-2022's
  analysis is right.
- **The NIST cutoffs 143/207/272**, verified only against archived *secondary*
  bytes (MATZOV's Table 1 NIST column, Carrier's abstract). No primary NIST or
  FIPS 203 text is readable under this program's network policy. Every margin
  statement inherits that.
- **`matzov` at Kyber-768 and Kyber-1024 against real Sage.** No reference
  exists. Two Sage-free sessions agreeing is not a Sage reference, and this is
  exactly where ANOM-3's large numbers live.
- **Carrier's Table 5.1**, not archived, so ANOM-4 cannot be resolved.
- **Whether Carrier's nearest-neighbour fit is coefficient-identical to
  `NN_AGPS`** — the hinge of DEF-6, and nothing in the archive settles it.
- **H15 and H17.** Not implemented in this instrument. H17 is the larger and is
  plausibly the whole MATZOV-2022 residual; sizing it changes the frozen cost
  model and needs a Coordinator amendment.
- **Global optimality of any stage.** Both searches are local boxes; DEF-10 shows
  the grids have artifacts.
- **H10, the stage-order dependence.** Not run by the producer or by me. D1 and
  the total are order-independent; the *split* between D2/D3/D4 is not
  established.
- **KN-OPEN-016's actual question** — whether the MATZOV-family success
  probabilities survive the Ducas–Pulles objection — is untouched by the batch
  and by this validation.
- **Model provenance.** `orchestration.adapter doctor --probe` was not run;
  `model_verified: false`. This is a `review-adversarial` pass with
  `fallback_used: true`, not a rule-12 `review-breakthrough` pass at `max`.

---

## 12. Bottom line

The package is **admissible with twelve defects**. Its central finding is the
strongest kind this campaign produces: a checkable source fact
(`estimator/lwe.py:13`) plus a deterministic evaluation, reproduced here from
scratch under a different rounding convention with maximum deviation 1.9e-09
bits. It overturns the premise its own batch was opened on, and says so. It
surfaced the observation most inconvenient to its own conclusion (ANOM-3) and
refused to adjudicate it, and it reported the negative residual that makes its
own decomposition look worse rather than better.

What the defects bound is not the finding but how far §6(2) and §6(3) may be
pushed: DEF-6 (the rejections are under-powered at residual resolution), DEF-7
(the reproduction claim has no null of the right shape) and DEF-9 (ANOM-3 is
largest where the instrument is least covered) together mean that no residual
below about two bits should be read as meaningful, and that the 4.59/8.39-bit
ANOM-3 figures carry less weight than the 0.54-bit one that is anchored to
upstream's own committed output.

Nothing here is an ML-KEM break, a demonstration that ML-KEM misses a NIST
category, a security proof in either direction, a validated heuristic, a
correction of EV-MLKEM-015, or authorization to promote anything. Rule 12
remains UNMET and UNWAIVED.
