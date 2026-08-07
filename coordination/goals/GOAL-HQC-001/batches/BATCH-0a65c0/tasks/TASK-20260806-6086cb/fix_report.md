# Fix report — v3 amendment to `EXP-HQC-982268`

**Task** `TASK-20260806-6086cb` (executor) · **Batch** `BATCH-0a65c0` (6 of 6, the
declared cap) · **Goal** `GOAL-HQC-001` · **Repairs** `VF-1`, `VF-3`, and the
`CTRL-POSHOM` detection list, per `DEC-20260806-980816`. **Produced** 2026-08-06.

---

## 0. Claim tier and boundary

**TOY, hard ceiling.** Nothing below is a statement about HQC, about assumption
A17 or A5, about any decoding-failure rate, or about any standardized HQC
parameter set. Every number is about an *instrument* and its decision rule. A
repaired instrument is not a result, and a twice-repaired instrument is not a
better one.

**Compliance with the task's hard limits.** Zero HQC objects constructed. Zero
measurement arms run. Zero `log2_A_k` computed on any space-(T) arm. Every draw
is from `S ~ Binomial(n_e, q̂)` under the declared null, or from an explicitly
declared alternative used only to measure size off the calibration point. The
only (T) inputs are first moments — `q̂` and the per-set block-failure totals —
already published as chartered Stage-A diagnostics in `RUN-HQC-982268-STAGEA-a`.
`experiments/EXP-HQC-982268/specification.yaml` was not touched; all writes are
inside this task directory.

**Read-scope excursion, disclosed.** While orienting I read ~60 lines of
`BATCH-6fddee/tasks/TASK-20260806-64b506/stage_a.py` (`log2_A_from_hist`,
`jackknife_log2_A`, `batch_hists`, `evaluable_k`), which is outside my declared
`read_scope`. **No number in any deliverable depends on it**: the estimator here
is written from the definition in the approved contract and cross-checked against
exact rational arithmetic, not against that file. `stage_a.py` was never executed.

---

## 1. Per-defect status

| defect | status | the number that settles it |
|---|---|---|
| **VF-1** transcription | **CLOSED** | 87 cells measured from the constants *as written in `amendment_v3.yaml`*; **all 87 inside `[0.002, 0.004]`**; range over the 80 REPORTED cells **0.2567 %–0.2808 %**. The three cells that failed in v2 (0.610 / 0.419 / 0.551 %) now read **0.2674 / 0.2681 / 0.2691 %**. |
| **VF-3** q-sensitivity | **CLOSED BY DROPPING PS-A** | Sensitivity run at **every** reported k at every configuration. PS-R1 / PS-R3 (both allocations) / PS-R5 hold the band across ±3 SE at every k, breakdown margins **7.9×–48.9×**. **PS-A does not** (k=2 margin 1.00×, k=3 margin 0.67×) and is **dropped from criterion (iv)**. |
| **CTRL-POSHOM list** | **CORRECTED; blind class ACCEPTED with a proof; new control SPECIFIED, NOT VERIFIED** | List rewritten to the injection evidence. The shift-equivariant class is recorded as a structurally accepted blind spot with an argument for why no same-invariance repair closes it. `CTRL-IDXMAP` added on a *functional* invariance; demonstrated on a toy ring only — see `OPEN-9`. |

**Budget:** 568.6 of 1200 authorized core-seconds. Full breakdown, including
three aborted runs, in `amendment_v3.yaml → budget_and_provenance`.

---

## 2. VF-1 — the transcription defect

### 2.1 What the defect actually was

Not a calibration error. The validator confirmed the v2 calibration replicated
under an independent re-implementation and independent seeds. The defect was that
**a human copied 30 constants into a YAML file at five decimal places.** At k=2
the interval half-widths are 2.2e−5 to 5.5e−5 bits, so five decimals could move a
bound by up to **23.1 % of its own half-width** (PS-R5 k=2, half-width 2.167e−5).
The rule the artifact *states* — which is the only rule that runs — realized
0.610 / 0.419 / 0.551 % size against its own `[0.002, 0.004]` gate.

### 2.2 Why I did not simply carry more decimals

The validator offered two routes and I took a third that subsumes both, because
each of the first two leaves the same hole open:

- *"Carry ≥ 7 decimals"* is a rule about human care, and it fails the next time
  care lapses. The required precision is also **cell-dependent** (≥ 6 decimals at
  PS-R1 k=2, ≥ 7 at PS-R5 k=2, recomputed whenever an allocation changes), so it
  is a rule no reviewer can check by inspection.
- *"Bind the procedure and seed only, demote the table to a reference"* makes the
  artifact unauditable without executing the producer's program. A reviewer asked
  to verify a rule should not have to trust that program to learn what the rule
  **is**.

**What I did instead: no human types a constant.** `recalibrate.py` computes the
constants, **writes them into `amendment_v3.yaml` itself**, **re-reads that file
with `yaml.safe_load`**, asserts every parsed value is a `float` bit-identical to
the value generated, and only then measures the size **of the values it read back
out of the file**. Both authorities — the transcribed table and the generating
procedure — are carried, and their agreement is asserted mechanically. The
transcribed table binds at run time; the procedure is its provenance, and the run
is required to re-derive and assert **bit-identity** (not a tolerance — a
tolerance is a number somebody has to choose, which is how VF-1 happened).

### 2.3 Two encoding defects the guard caught, both in the VF-1 class

The round-trip assertion is load-bearing, not decorative. It found two real
defects before either could reach a reviewer:

1. **PyYAML resolves `1e-05` as a *string*, not a float.** Its float regex
   requires a decimal point in the mantissa; Python's own `repr(1e-05)` is exactly
   `1e-05`. The k=2 constants are precisely of that magnitude, so the obvious
   emission route would have silently written the binding constants **as text**.
   `yf()` forces a decimal point and asserts the parsed type, and the selftest
   asserts PyYAML still exhibits the trap so the guard cannot go stale unnoticed.
2. **The first `calibrate` run aborted in the post-injection check**, having
   emitted the constants at the wrong YAML indentation so they parsed as siblings
   of `frozen_intervals` rather than as its contents. Caught on first execution,
   at a cost of 96.5 core-seconds, and reported rather than quietly retried.

### 2.4 The measurement (`transcribed_size.json`)

Constants read back out of `amendment_v3.yaml`, type-asserted, scored on 1,000,000
validation draws per configuration under seeds independent of the calibration
seeds.

| set @ T | table rows | measured | REPORTED | size range over REPORTED | outside gate |
|---|---|---|---|---|---|
| PS-A @ 1e8 | 4 | 3 | 2 | 0.00273 – 0.00276 | 0 |
| PS-R1 @ 1e8 | 16 | 16 | 14 | 0.00260 – 0.00271 | 0 |
| **PS-R3 @ 1e7** | **17** | **17** | **17** | **0.00257 – 0.00278** | **0** |
| PS-R3 @ 2e7 | 21 | 21 | 19 | 0.00261 – 0.00279 | 0 |
| PS-R5 @ 2e7 | 30 | 30 | 28 | 0.00264 – 0.00281 | 0 |

`PS-A k=16` is the 88th row and has no interval at all (the estimator is undefined
on every null replicate); it is carried as NOT REACHED.

**`PS-R3 @ T = 1e7` is new in v3 and is the allocation this campaign funds.** v2
froze PS-R3 only at T = 2e7 and gave T = 1e7 a single k=17 row inside a cost
table — so the measurement the campaign is about to run **had no frozen rule at
any order but one**. v3 freezes k = 2..k_max at every configuration.

### 2.5 What this number is and is not worth

**VF-2 applies and is not evaded.** The validator showed this style of measurement
returns 0.2476 %–0.2894 % for *any* continuous law — including a standard normal
with no estimator and no instrument in sight — so a headline "measured size 0.26 %"
is close to a tautology about Monte-Carlo quantile error. That is not what this
table is for. Its job is the **differential** check that the *encoded* constants
realize the size of the constants they were meant to encode, and it does that job:
against a tautology it would have returned 0.26 % for v2's table too, and it
returns 0.610 / 0.419 / 0.551 %. What actually establishes the rule is the
contrast against v1 (0.30 %–23.55 %), and the amendment now leads with that.

---

## 3. VF-3 — q-sensitivity at every reported k

### 3.1 Design

For each cell: 15 relative shifts of `q̂` — 0, ±1/±2/±3 SE, and an amplified probe
grid at ±0.25 / 0.5 / 1 / 2 / 4 % — at 400,000 validation draws each, scored
against the constants read back from the amendment. Each cell reports its
**breakdown shift** (the smallest |Δq/q| at which its size leaves the band) beside
its own 3 SE. That ratio is the single number that decides the question, and it
is more informative than the ±3 SE rows alone: at PS-R1/R3/R5 a ±3 SE shift moves
the size by less than Monte-Carlo resolution, so the ±3 SE rows on their own
cannot distinguish "robust" from "unmeasured".

`SE(q̂)/q̂ = sqrt((1−q)/block_failures)`, reproducing the validator's 3 SE figures
exactly: 3.328 % (PS-A), 0.1179 % (PS-R1), 0.0817 % (PS-R3), 0.0632 % (PS-R5).
**Stated correctly this time:** this is the ρ = 0 *value*, and since ρ > 0 is the
alternative the experiment exists to detect it is a **lower** bound, not an upper
one — v2 called it "the bound". The validator's measured inflation factors
(1.00 / 1.34 / 1.69 / 2.35) still leave ≥ 6× of margin at the reduced sets.

### 3.2 Result

| set @ T | 3 SE | robust over ±3 SE at every reported k? | breakdown margin over 3 SE |
|---|---|---|---|
| PS-A @ 1e8 | 3.328 % | **NO** | k=2: **1.00×** · k=3: **0.67×** |
| PS-R1 @ 1e8 | 0.1179 % | yes | 8.5× – 33.9× |
| PS-R3 @ 1e7 | 0.0817 % | yes | **12.2× – 48.9×** |
| PS-R3 @ 2e7 | 0.0817 % | yes | 12.2× – 48.9× |
| PS-R5 @ 2e7 | 0.0632 % | yes | 7.9× – 31.6× |

PS-A in detail, on my own constants, seeds and draws:

| k | −3 SE | q̂ | +2 SE | +3 SE | breakdown |
|---|---|---|---|---|---|
| 2 | 0.00368 | 0.00260 | 0.00229 | **0.00191** ✗ | 3.33 % = **3.0 SE** |
| 3 | **0.00409** ✗ | 0.00277 | **0.00194** ✗ | 0.00153 ✗ | 2.22 % = **2.0 SE** |

**VF-3 reproduces independently.** The validator measured PS-A k=3 at −3 SE as
0.00404 with the producer's unrounded constants; I measure 0.00409. PS-A k=3
leaves the band on *both* sides — anti-conservative at −3 SE and conservative
already at +2 SE.

### 3.3 Decision: PS-A is dropped from criterion (iv)

I did not make PS-A robust. Every route to doing so changes the rule in a way no
reviewer has seen, and the campaign is at its declared batch cap. Dropping is the
honest option and I took it plainly rather than by widening a band until the cell
fit inside it.

**What that costs, stated where it will be read.** PS-A is the **anchor set** —
true HQC-1 parameters, verbatim, the only configuration in the contract that is
not a reduced surrogate. After this change **no cell at true HQC parameters is
certified under criterion (iv)**, and (iv) rests entirely on order-matched reduced
sets. That sits on top of v2's already-recorded narrowing (anchoring (iv) on PS-R3
anchors it on HQC-3's shape, not HQC-1's). Both narrowings must travel into every
downstream record. What is *not* lost: PS-A's k = m = 16 cell was already
infeasible by 37 orders of magnitude (`T_stab` 1.246e45) under v1 and v2 alike, so
PS-A was never going to deliver an order-matched cell — what is dropped is two
low-order cells at the anchor. PS-A, if funded, is still run and still reported,
marked **NOT CERTIFIED UNDER (iv)** with its sensitivity rows attached.

**Concrete successor, costed.** Derive PS-A's interval at the **Stage-B** realized
`q̂` rather than the Stage-A one: at T = 1e8 the PS-A (T) arm accumulates ≈1.538e6
block failures against Stage A's 8,122, so 3 SE falls 3.33 % → 0.242 %, a factor
13.8, giving margins of 13.8× and 9.2× against the breakdown shifts above.
**The risk that buys, stated:** the interval becomes a function of the data it
scores, which reintroduces exactly the numerator/denominator coupling R1 removed
from the Wald rule. Its size would have to be measured for the whole plug-in
procedure, not at a fixed q. **I did not make that measurement and v3 does not
adopt the route.**

---

## 4. The CTRL-POSHOM detection list

### 4.1 Corrected to what was measured

Red team `TASK-20260806-42c153` §3: PS-R1, 400,000 trials, eight variants sharing
the same draws. **I did not re-run that injection** — no measurement authorization
— so every row is cited, not reproduced.

| | variant | defect | q̂ shift | Q/df | verdict |
|---|---|---|---|---|---|
| **FIRES** | V5 | block-0 tie rule | +1.12 % | 571.5 | real win |
| **FIRES** | V6 | one masked coordinate in the last block | **−0.19 %** | 17.31 | **the strongest result for this control** |
| fires, **no marginal value** | V4 | wrap error | −87.53 % | 35 141.7 | INV-Q / BASE-TABLE10 / D1 catch it first |
| **BLIND** | V1 | off-by-one truncation window | −0.01 % | 0.933 | v2 listed this on the **catch** side |
| **BLIND** | V2 | interleaved block partition | +0.03 % | 1.262 | **the serious one** |
| **BLIND as tested** | V3 | last block's window read one coordinate early | +0.00 % | 1.046 | not *structurally* blind — see §4.2 |
| no conclusion | V7 | sign-blind decoder acceptance | 0.00 % | 1.053 | **the injection was inert** — bit-identical to correct over 400,000 × 46 decodes |
| **UNTESTED** | — | dup-folding stride error | — | — | v2 listed on the **catch** side; **moved to UNTESTED, not to blind** |

Two things I deliberately did *not* do: I did not relist any blind defect as
caught, and I did not move the untested `dup`-stride case onto the blind side
either. Nobody has measured it; `dup = 1` at PS-R1 so it could not be tested
there. It is `OPEN-10` with a 15-core-minute resolution.

### 4.2 The blind spot is structural, and here is the argument

Let `G = ⟨X⟩ ≅ Z_n` act by ring shift. CTRL-POSHOM's null is forced by exactly one
fact: **the law of `e''` is G-invariant.** Both clauses compare block *j* against
block *j′* and are unchanged when the window family `{B_j}` is replaced by
`{g·B_j}`.

So suppose a defect replaces the correct windows by `B'_j = s_j + B'_0` — still a
**single G-orbit with the same increments**. Then by G-invariance every `B'_j` has
the same marginal law, and `(B'_j, B'_{j+d})` is a G-translate of `(B'_0, B'_d)`,
so its joint law depends only on `d`. **Both clauses hold exactly.** The control's
detection probability equals its size: it is not weak on this class, it is *blind*
to it, at every T.

Classifying the three measured variants against that:

- **V1** takes `B'_0 = B_0 + 1` with the same increments. The whole indicator
  matrix has the **identical joint law**, so V1 is invisible to every statistical
  test of the (T) arm whatsoever — it is harmless for the estimand and is a defect
  only against the specification.
- **V2** takes `B'_0 = {0, n_e, 2n_e, …}` with increments `s_j = j`: still one
  G-orbit, so both clauses hold exactly — **but a decimated window and a contiguous
  window do not have the same weight law, so V2 does change the estimand.** That
  combination is what makes V2 dangerous: consequential *and* exactly invisible.
- **V3 is not of this form.** Moving one window by −1 changes the gaps between it
  and the others, so clause (b) *is* violated at the pairs involving that block.
  It survived at T = 4e5 as a **power** failure at one pair class out of
  `C(n_e,2)`, and its detectability at Stage-B T is unmeasured. This distinction is
  mine and refines both the amendment and the red team report, which record V3
  simply as "pass".

**Status of that argument:** it is an argument, not a measurement, written *after*
the measurements. Clauses (1)–(2) are elementary given G-invariance, which the
validator verified. Clause (3) predicts exactly what was observed, including that
one of the three variants is undetected for a *different* reason — corroboration,
not proof.

**This is the second instance of one pattern.** CTRL-BS was the first (its
`np.roll` preserves every column sum, so a wrong `F` cancels). The generalizable
statement — *an invariance strong enough to force a control's null value also
blinds that control to every defect respecting it, so the strength of a forced
null and the breadth of its coverage are in direct tension* — is a KN-TECH
candidate. **I do not promote it:** two instances on one instrument is not a
technique, and the Coordinator's stated bar (a second instrument) is right.

### 4.3 The new control, and what it is not

A control for this class **must not be a distributional test of the (T) sample**,
because two index maps in the same G-orbit family produce G-homogeneous samples
that no homogeneity test can separate. Two routes exist: compare against a law
known in advance (that is `OPEN-6`, unbuilt), or compare the instrument against
the specification **functionally**. v3 takes the second.

**`CTRL-IDXMAP`** — deterministic, blocking. Its invariance is *functional
agreement with the specification's index arithmetic*, deliberately **not**
ring-shift invariance. The sampler must express truncation and block extraction as
explicit index arrays and **gather through them**, so the array emitted is the
array read; the control recomputes both from the frozen `(n, N, n_e, n_2, dup)`
alone and requires elementwise equality. Detection probability **1,
deterministically**, for any defect that changes which coordinates are read — not
a power statement, not a function of T, and not defeatable by shift-equivariance.

Demonstrated on a **toy ring** (n=71, N=60, n_e=6, L=10): silent on the correct
map, fires on V1 (60 + 60 index mismatches), V2 (58), V3 (10).

**Three honest limits, stated up front rather than found later:**

1. **The demonstration is a toy.** It constructs no HQC object and shows the
   *mechanism* only. It demonstrates nothing about `stage_a.py`, which I did not
   execute or instrument.
2. **`CTRL-IDXMAP` is a specification, not a passing gate** (`OPEN-9`). The v2
   episode is the precedent and the warning: a blocking gate whose passage rests on
   a citation is a gate that has never been run in the configuration that binds.
   That criticism applies to this control and I have recorded it against my own
   work. Its ranking entry carries "SPECIFICATION ONLY".
3. **It has one real failure mode:** an implementation that emits a correct map and
   reads by other means passes it vacuously. The gather requirement is what
   forecloses that, and it is therefore a binding *implementation* obligation, not
   a reporting one.

`CTRL-POSHOM` is **kept** — V6 (one masked coordinate, 0.19 % q̂ shift, detected)
is a real capability nothing else in the contract has — but **demoted** from v2's
"PRIMARY, the only control sensitive upstream of the indicator matrix", and its
scope is restated as *position-dependent* defects.

---

## 5. What I could not close

Reported as unclosed rather than papered over.

1. **`RT2-OBJ-1` — the rule is sized at a point, and the null is composite.** OPEN.
   I **independently reproduced** the red team's objection from the constraints
   rather than their code: at PS-R1 k=16 a law at TV = 8.90e−5 with `log2 A_16` = 0
   to 8.8e−12 bits fires the cell **91.24 %** of the time (their 91.41 %). Two
   things I measured that they did not:
   - **At the cell this campaign actually funds** (PS-R3 k=17, T=1e7) the same
     construction is far weaker: it reaches only TV = 0.0495 at the non-negativity
     bound — **556× further from the binomial** — and even there fires only
     14.30 %. A structural reading, **offered as a hypothesis and not established**:
     the attack loads a tail `C(S,k)` never reaches, and its leverage grows with
     `k/E[S]` — 1.76 at PS-R1 k=16 versus **0.95** at PS-R3 k=17. **One family, one
     support choice, no search over supports.**
   - **The multi-k battery mitigates it and the mitigation is not free.** Against
     the PS-R1 law the reported battery rejects with probability 1.0000 where the
     single cell gives 91.24 %. **But its familywise size under the exact binomial
     null is 1.09 % (PS-R1) and 1.03 % (PS-R3)** — roughly 4× the 0.27 % per-cell
     nominal, as 14–17 correlated cells should give. A battery reading is therefore
     **not** a 0.27 % test and must never be reported as one. v3 requires every
     evaluable k to be reported and requires the familywise rate to be stated; it
     does **not** make the battery the falsification criterion, which would need its
     own calibration.

   What remains open: the size under the composite null is unknown, and the
   run-time size guard is drawn from the same binomial law and **cannot see this by
   construction**. The red team's framing — "the new run-time check is
   self-referential" — is correct and is not repaired here.

2. **`OPEN-6` — no arm tests the (T) joint law against an answer known in advance.**
   Not narrowed by this record. `CTRL-IDXMAP` is not distributional at all, so it
   does not help here. Still the largest hole in the instrument.

3. **`CTRL-POSHOM` clause (b) remains unevaluated**, not passed: no committed run
   records `pair_counts_by_position.csv`. v3 adopts the red team's distribution-free
   `REF-3` as the binding reference for both clauses — together with their honest
   caveat that `Σ̂` contains `Σ_t S_t²`, so any valid calibration of clause (a)
   **does** form a (T) second moment and declining to form it does not avoid the
   `OPEN-8` disclosure.

4. **`OPEN-8` needs a Coordinator ruling, not an executor's edit.** All v3 does is
   what an Executor may: criterion (iv) authorizes k = 2 explicitly as a reported
   Stage-B cell at PS-R3 under the frozen interval, which is the substance of the
   validator's recommendation. I did not perform the inversion, and neither reviewer
   did.

5. **The `dup`-stride mechanism** (`OPEN-10`) is untested and its asserted mechanism
   has no derivation in v2, none from the red team, and none from me.

---

## 6. Reproduction

```
python3 recalibrate.py all      # selftest, calibrate, qsens, measure, battery, idxmap
```

regenerates the two machine-generated blocks of `amendment_v3.yaml` and all of
`transcribed_size.json` from nothing but the frozen procedure, its SHA-256-derived
seeds, and the Stage-A first moments in the script's `SETS` table. The `measure`
phase reads the constants **back out of `amendment_v3.yaml`**, so re-running it is
also the check that the file has not been edited since the constants were written.

Estimator cross-checked against exact rational arithmetic: **max |difference|
4.62e−14 bits over 131 comparisons**, nine orders below the narrowest half-width
in the record (2.167e−5 bits). Round-trip of the whole constant table: **max
absolute difference exactly 0.0**, every constant parsing as `float`.

Deliverables, and the only files this task wrote:
`amendment_v3.yaml`, `recalibrate.py`, `transcribed_size.json`, `fix_report.md`.
Cached phase results live outside the task directory (`RECAL_WORK`, default
`$TMPDIR/recalibrate-TASK-20260806-6086cb`) so the Coordinator's snapshot commit
stages exactly its declared `artifact_paths`.

---

## 7. What a reviewer should attack first

Ranked by where I think this work is weakest, not by where it is strongest.

1. **Load the constants from `amendment_v3.yaml` yourself and measure them.** That
   is the gate, and it is the one thing I would not want taken on trust. Watch for
   the `1e-05`-as-string trap if you write your own loader.
2. **`CTRL-IDXMAP` has never run on the real instrument.** It is a specification
   whose demonstration is a toy. If you inject V1/V2/V3 against v3's control set,
   this is the control to point at — and `OPEN-9` says so before you do.
3. **The structural argument in §4.2 was written after the measurements**, and it
   is an argument. Clause (3)'s claim that V3 is a *power* failure rather than a
   structural one is the part most likely to be wrong, and it is unmeasured at
   Stage-B T.
4. **The PS-R3 near-null in §5.1 is one family with one hand-chosen support.** A
   better support may well beat 14.30 %, and I ran no search.
5. **Dropping PS-A is a judgement**, not an arithmetic consequence. The numbers say
   PS-A cannot be certified at the Stage-A `q̂`; they do not say it must be dropped
   rather than re-derived at the Stage-B `q̂`. I argued for dropping on cap and
   review grounds and named the alternative with its cost and its risk. Disagreeing
   with that trade is legitimate.
