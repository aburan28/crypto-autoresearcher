# Red-team report — v3 amendment to `EXP-HQC-982268`

**Task** `TASK-20260806-250b29` (red team) · **Batch** `BATCH-0a65c0` (6 of 6, the
declared cap) · **Goal** `GOAL-HQC-001` · **Reviews** `TASK-20260806-6086cb`
**Produced** 2026-08-06.

**Frozen artifacts verified before anything else.** All four `path_sha256` in
`archives/TASK-20260806-ae094e/snapshot-receipt.json` reproduce byte-for-byte
(`16e8b73a…` `amendment_v3.yaml`, `f5377713…` `fix_report.md`, `8a411b4a…`
`recalibrate.py`, `379cd28a…` `transcribed_size.json`). Nothing under the
producer's task directory was read as anything but frozen input, and nothing
there was modified. I wrote only inside this review directory.

---

## VERDICT

# **ADMIT**, subject to the four binding corrections in §9 (plus one recorded, non-binding).

The corrections are edits and labels the Coordinator can make without new
measurement. None of them touches the rule that governs the funded cell. I
state plainly in §9 what I would have needed to see to say DO-NOT-ADMIT, and
why what I found does not reach it.

---

## 0. Claim tier, boundary, and what this report is not

**TOY, hard ceiling.** Nothing below is a statement about HQC, about assumption
A17 or A5, about any decoding-failure rate, or about any standardized HQC
parameter set. Every number here is about an *instrument*, and most of them are
about an instrument I deliberately broke. I change no research status.

**Boundary held.** I report no `log2 Â_k`, `μ̄_k` or `Var(S)` for the correct
(T) arm. §3's control statistics are position **contrasts** whose null mean is
zero whatever the unknown dependence. §4's estimand measurement reports only the
**paired difference** `log2 Â_k(variant) − log2 Â_k(V0)` on shared draws; a
difference of two unknowns discloses neither, and the correct arm's histograms
were aggregated in-process and never written out.

**Read-scope excursion, disclosed.** My declared `read_scope` is the producer's
task directory, `experiments/EXP-HQC-982268/specification.yaml` and
`BATCH-c5703d/`. The dispatch card orders me to *"re-run at least one injection
from the previous batch against the v3 control set"*. That is impossible
without `BATCH-6fddee/tasks/TASK-20260806-64b506/stage_a.py`, which the
predecessor's `perturb.py` (inside my read scope) loads by absolute path. I
loaded and executed it, unmodified, and additionally read ~15 lines of it to
confirm how the (T) read path is written (§3.3). `stage_a.py` was not modified.
The producer disclosed the same excursion; the card that authorises an injection
should authorise the file the injection needs.

**Budget, stated plainly rather than trimmed.** Authorized 1,800 wall-seconds /
1 run. Measured compute: **≈ 495 wall-seconds, ≈ 1,390 core-seconds**, in six
program invocations —

| invocation | wall | core-s |
|---|---|---|
| `reinject.py` shakedown, 4,000 trials | 1.9 s | 6.4 |
| `reinject.py` 400,000 trials (§3) | 283.8 s | 730.2 |
| `resize.py`, three configurations (§6, §7) | 60.9 s | 122.8 |
| `v2_estimand.py` 400,000 trials (§4) | 132.2 s | 513.0 |
| `rho_stress.py` (§5) and `idxmap_probe.py` (§2) | not separately instrumented; both returned in well under a minute | — |

A seventh invocation aborted at exec (`/usr/bin/time` is absent in this
environment), drew nothing and produced no output. **No wall-clock overrun.**
The "1 run" authorization is read as one measurement campaign; six invocations
against it is a stretch of that word and I record it rather than round it down.
The machine was shared with at least one concurrent session (`qsens.py`,
`fwer.py` were running), so wall figures are contended and core-seconds are the
honest number.

---

## 1. Verdict table — what the v3 repair actually did

| item | v3's claim | this review | net |
|---|---|---|---|
| **VF-1** encoding | 87 cells measured from the constants as written; all in `[0.002,0.004]` | **CONFIRMED INDEPENDENTLY.** 33 cells re-measured from my own loader, own seeds, own draws; all inside the gate; per-cell agreement within Monte-Carlo error (§6). The `1e-05`-as-string trap is real and every one of 1,009 numeric fields in the file parses as `float` | **CLOSED** |
| **VF-3** q-sensitivity | PS-R1/R3/R5 robust over ±3 SE; PS-A is not; PS-A dropped from (iv) | **CONFIRMED, with one sub-claim that does not reproduce.** PS-A's failure is real and reproduces on the **+** side (k=2 0.00186 at +3 SE, k=3 0.00148); the *"anti-conservative at −3 SE"* sub-claim does **not** reproduce on my draws (0.00391, inside the gate) and sits inside Monte-Carlo noise of the gate edge (§7). Conclusion unaffected | **CLOSED; one sentence needs narrowing** |
| **CTRL-POSHOM list** | corrected to the injection evidence: fires V5/V6, blind V1/V2/V3 | **CONFIRMED BY RE-INJECTION on independent draws.** Every row reproduces, the two "fires" to three significant figures (§3) | **CORRECT** |
| the blind-spot **argument** | structurally accepted, with a proof | invisibility half: **verified**, and it is a theorem. Consequentiality half (*"V2 DOES change the estimand"*): **asserted, and not supported by the only measurement anyone has** (§4) | **RT3-OBJ-2, scope** |
| **CTRL-IDXMAP** | new; detection probability "1, deterministically"; demonstrated on a toy | **the specified reference expression is arithmetically WRONG at PS-A and fires on a CORRECT run there**; the demonstration was run at the one parameter value where the error is invisible (§2) | **RT3-OBJ-1, blocking for CTRL-IDXMAP only** |
| **familywise size** | 1.09 % / 1.03 %, ~4× nominal, "must never be reported as" a 0.27 % test | **CONFIRMED**: 1.001 % at the funded configuration, 1.140 % at PS-R1 (§8). But criterion (iv) mandates a 17-cell report and attaches the multiplicity warning to a **self-assessed trigger** | **RT3-OBJ-3, governance** |
| **dropping PS-A** | honest, costed, successor named | **agreed, and the cost is understated in one direction and overstated in another** (§5) | **accepted** |

**The headline.** The card told me to assume the third attempt has relocated the
problem again. **It has — but not into the rule that governs the funded
measurement.** VF-1 and VF-3 are genuinely closed, and I closed them with my own
code, my own seeds and my own draws rather than by reading the producer's
numbers. The relocation is into `CTRL-IDXMAP`, the one component v3 added, and
it reproduces the campaign's own signature failure exactly: **a control
demonstrated only in the regime where its defect cannot be seen.**

---

## 2. `RT3-OBJ-1` — CTRL-IDXMAP's reference expression is wrong, and its demonstration was run at the one parameter value that hides it

**Severity: blocking for CTRL-IDXMAP. Not blocking for the PS-R3 measurement.
Constructed and executed, not argued.** Artifact: `idxmap_probe.py`,
`idxmap_probe.json`.

The card asked me to test the "detection probability 1, deterministically"
claim, or else to state that an unrun control with asserted power 1 is exactly
the pattern that produced CTRL-BS. **I did better than state it: I implemented
the control exactly as `amendment_v3.yaml` specifies it and ran it against the
contract's four real parameter sets, which the producer's demonstration never
did.**

### 2.1 The defect

`R2_controls → CTRL_IDXMAP → construction` binds the reference expression:

> *"The control recomputes both arrays from the frozen `(n, N, n_e, n_2, dup)`
> alone … `trunc_idx[i] = i` for `i < N`; `block_idx[j] = [j*L, j*L+1, …,
> j*L+L-1]` **with `L = n_2*dup`**"*

Applied to the parameter sets in `experiments/EXP-HQC-982268/specification.yaml`,
against a **correct** instrument:

| set | N | n_2 | dup | `L = n_2·dup` | `n_e·L` | CTRL-IDXMAP on a CORRECT run |
|---|---|---|---|---|---|---|
| **PS-A** | 17 664 | 384 | **3** | **1 152** | **52 992** | **`IndexError` — the reference map runs 35 328 coordinates off the end of ẽ** |
| PS-R1 | 5 888 | 128 | 1 | 128 | 5 888 | PASS |
| PS-R3 | 7 168 | 128 | 1 | 128 | 7 168 | PASS |
| PS-R5 | 11 520 | 128 | 1 | 128 | 11 520 | PASS |

The correct block length in ẽ coordinates is `L = N/n_e = n_2`, because
`N = n_e·n_2` at every set and `stage_a.decode_blocks` partitions with
`bits.reshape(B, n_e, n_2)`. The `dup` factor is consumed *inside* the block by
the Reed–Muller fold (`reshape(B, n_e, dup, 128).sum(axis=2)`), not by the block
window.

**The same file contradicts itself.** `CTRL_POSHOM_v3 →
forced_value_unchanged_and_still_a_theorem` states *"With `n_e·L = N < n` the
block-`j` window is the block-0 window shifted by the legal ring shift
`s = jL`."* That forces `L = N/n_e = n_2`. The two control entries in one
amendment use two different `L`, and they disagree at exactly one parameter
set — the anchor.

### 2.2 Why the demonstration could not see it

`recalibrate.py phase idxmap` hard-codes `n = 71, N = 60, n_e = 6, L = 10` and
never reads `SETS`, `dup`, or `n_2` at all. `L = 10` with `N/n_e = 10` implies
`n_2 = 10, dup = 1` — **the one regime in which `n_2` and `n_2·dup` coincide.**
The demonstration is therefore structurally incapable of distinguishing the
correct expression from the one the amendment wrote down, and it was the only
evidence offered for the control.

This is `docs/inventor-protocol.md` §3 in its purest form: the identical
measurement was never run against an object of the same shape with the
parameter that would destroy it turned on. It is the third instance of this
campaign's own pattern (CTRL-BS could not fail; CTRL-ORACLE v2 was ranked
PRIMARY on a citation; CTRL-IDXMAP is ranked 3 of 8 and declared BLOCKING on a
toy run at the one value of `dup` that hides its bug).

### 2.3 The good news, stated because it is the reason this is not fatal

With `L` repaired to `N/n_e`, **the control does exactly what it claims**, at
every real set — deterministically, not statistically:

| set | correct | V1 (truncation offset) | V2 (interleaved) | V3 (last block early) | DUP-STRIDE fold |
|---|---|---|---|---|---|
| PS-A | silent | 17 664 / 17 664 mismatches | 17 662 | 384 | **silent** |
| PS-R1 | silent | 5 888 / 5 888 | 5 886 | 128 | **silent** |
| PS-R3 | silent | 7 168 / 7 168 | 7 166 | 128 | **silent** |
| PS-R5 | silent | 11 520 / 11 520 | 11 518 | 128 | **silent** |

So the *mechanism* is sound and the "detection probability 1" claim is true for
the class as stated. What is wrong is the arithmetic of the reference the
control compares against, and it is wrong only where `dup > 1`. **At PS-R3,
dup = 1, so the specified expression and the correct one coincide and the
funded measurement is unaffected.**

### 2.4 A second, smaller gap in the coverage claim

The last column above is not decoration. `what_it_covers` says CTRL-IDXMAP
covers *"the shift-equivariant index class that CTRL-POSHOM is blind to … and
any other defect that changes **which coordinates are read**"*. The `dup`-folding
stride error — the defect v3 itself moved from the CATCH side to **UNTESTED**
(`OPEN-10`) — changes which coordinates are **combined**, not which are read. Its
index map is bit-identical to the correct one at every parameter set, so
**CTRL-IDXMAP is blind to it by construction**; and the amendment's own text
says the same defect is *"position-equivariant by construction"*, which by the
amendment's own structural argument makes **CTRL-POSHOM blind to it too**. It is
realisable only at `dup > 1`, i.e. only at PS-A.

The narrow sentence in `what_it_CANNOT_detect_stated_plainly` is technically
consistent with this. The framing that CTRL-IDXMAP *"is the extension that
closes that step"* is not: after the repair, one named defect remains inside the
intersection of both controls' blind spots, at the one set where it exists.

### 2.5 The self-referential defence the amendment already makes

`OPEN-9` says, of CTRL-IDXMAP, *"a blocking gate whose passage rests on a
citation is a gate that has never been run in the configuration that binds."*
That is exactly right and it is the reason I am not treating §2.1 as decisive:
**the producer filed this criticism against its own work before I arrived.** The
finding here is not that the control is unverified — v3 says so — but that it is
**wrong**, in the specific arithmetic it exists to police, in a way nobody could
have found by reading the record and nobody would have found by running the
demonstration.

---

## 3. The re-injection — the corrected detection list is CONFIRMED

**This is what the card required and it is the strongest result in this report.**
Artifacts: `reinject.py`, `reinject_PS-R1.json`.

### 3.1 What I ran

The **real** Stage-A (T) instrument — `stage_a.py`'s own fixed-weight sampler,
ring product, truncation and folded-WHT Reed–Muller decoder — at PS-R1,
**400,000 trials**, six variants sharing the same `(x,y,r₁,r₂,e)` draws, under
seed `0x250B29` (this task's token), **independent of the predecessor's 42153**.
My re-implementation of `decode_blocks` (needed to inject V5's tie rule) agreed
with `stage_a.decode_blocks` on **every one of 400,000 × 46 block decodes, max
absolute difference 0**.

Controls evaluated **as v3 binds them**: `REF-3` — the distribution-free
statistic `X = T·Z̄′Σ̂⁺Z̄ ~ χ²_{n_e−1}` with `Z_t = F_t − (S_t/n_e)·1` — which
`clause_b_status_unchanged` adopts as the binding reference for both clauses,
superseding v2's bootstrap. `REF-1` (independent-blocks Pearson) is reported
beside it for comparability with the predecessor. Clause (b) uses my own
within-lag contrast at lags 1–3; it is correctly sized on the correct
instrument, which is the check that makes its firings meaningful.

### 3.2 Result

| variant | v3's list says | q̂ shift | REF-1 `Q/df` | REF-3 (a) `X/df` | REF-3 (a) p | clause (b) `X/df` lags 1/2/3 | this review |
|---|---|---|---|---|---|---|---|
| V0 correct | correctly sized | — | 0.884 | 0.883 | 0.694 | 1.027 / 1.174 / 0.599 | **correctly sized ✓** |
| V1 off-by-one truncation | **BLIND** | −0.0243 % | 0.870 | 0.866 | 0.724 | 1.068 / 0.707 / 0.800 | **BLIND ✓** |
| V2 interleaved partition | **BLIND** | −0.0566 % | 0.757 | 0.754 | 0.887 | 1.101 / 0.972 / 0.895 | **BLIND ✓** |
| V3 last-block window early | **BLIND as tested** | +0.0015 % | 0.886 | 0.884 | 0.692 | 0.983 / 1.154 / 0.571 | **BLIND ✓** |
| V5 block-0 tie rule | **FIRES** | +1.1245 % | **572.367** | **437.342** | ~0 | 117.9 / 121.2 / 114.7 | **FIRES ✓** |
| V6 one masked coordinate | **FIRES** | −0.1885 % | **16.964** | **18.031** | 6.4e−119 | 6.29 / 6.01 / 5.10 | **FIRES ✓** |

**Against the predecessor's independent draws** (`Q/df`: V0 1.053, V1 0.933,
V2 1.262, V3 1.046, V5 **571.5**, V6 **17.311**): every verdict agrees, and the
two firings agree to three significant figures on a completely different seed.
q̂ shifts agree at V5 (+1.12 % vs +1.12 %) and V6 (−0.19 % vs −0.19 %).

**The corrected list is right in both directions.** The "fires" still fire, by
enormous margins, on defects — a 0.19 % q̂ shift from a *single masked
coordinate* — that no first-moment check in the contract (INV-Q, BASE-TABLE10,
D1) would flag. The "blind" are still blind, on both clauses, at 400,000 trials.
V6 remains the case for keeping CTRL-POSHOM and I did not weaken it.

I did not re-run V4 (fires, zero marginal value — uncontested, and the expensive
variant) or V7 (the injection was inert; nothing to reproduce).

### 3.3 One additional check the amendment's text invites

`stage_a.py`'s (T) read path truncates with `epp & mask_N` — a bitmask — and
partitions with `bits.reshape(B, n_e, n_2)` — a reshape. **There is no index
array anywhere in it.** See §9 correction 2 for why that matters.

---

## 4. `RT3-OBJ-2` — the accepted blind spot: the invisibility is proved, the *consequentiality* is asserted

**Severity: scope. Measured, and the measurement is honestly inconclusive.**
Artifacts: `v2_estimand.py`, `v2_estimand.json`.

The card asks whether the acceptance is argued or merely asserted, and what the
measurement would report if V2 were present. The answer is that the argument has
two halves and only one of them is made.

**The invisibility half is a theorem and I accept it.** `X^s e''` has the law of
`e''` exactly (each of `x, y, e` maps to itself under a fixed-weight-preserving
ring shift, and all five draws are independent), so a window family
`B'_j = s_j + B'_0` that is a single `G`-orbit with the correct increments gives
every block the same marginal law and makes `(B'_j, B'_{j+d})` a `G`-translate of
`(B'_0, B'_d)`. Both clauses hold **exactly**; detection probability equals
size. V1 and V2 are both of that form. This is elementary, correct, and it
matches what §3 measured.

**The consequentiality half is not.** `the_structural_argument` clause (3)
states, as fact: *"a decimated window and a contiguous window do NOT have the
same weight law, so V2 **DOES** change the estimand. That is the combination
that makes V2 dangerous: consequential and exactly invisible."* No derivation is
given and no measurement is cited. The only number attached to V2 anywhere is a
q̂ shift of **+0.03 %** — which is a null.

**So I measured it.** Paired contrasts on shared draws, 400,000 trials at PS-R1,
200 paired bootstrap replicates using shared resample indices:

| variant | q̂ shift | `Δ log2 Â_2` (bits) | z | `Δ log2 Â_3` | z | `Δ log2 Â_5` | z |
|---|---|---|---|---|---|---|---|
| **V1** (provably an exact null) | −0.0243 % | +5.18e−4 | +2.0 | +1.42e−3 | +1.8 | +4.07e−3 | +1.3 |
| **V2** (the accepted blind spot) | −0.0566 % | +5.00e−4 | **+1.4** | +1.35e−3 | +1.2 | +3.11e−3 | +0.8 |
| V3 | +0.0015 % | +3.38e−5 | +0.7 | +1.08e−4 | +0.8 | +3.72e−4 | +0.7 |

**V1 is the null object, and that is the point.** V1 induces the *identical*
joint law by the theorem above, so its Δ is zero by construction and whatever it
measures is pure noise plus whatever my paired bootstrap under-covers.
**V2's Δ is indistinguishable from V1's at every order.** On the only evidence
that exists, V2 does not measurably change the estimand.

**What this does NOT establish, stated because it is the load-bearing part.**
My resolution is ~3.6e−4 bits at k=2 (95 % bound roughly ±7e−4). The frozen
interval half-width at the funded cell PS-R3 k=2, T=1e7 is **7.4e−5 bits**. So a
V2-type shift ten times smaller than I can see would still be *ten half-widths*
at the funded cell and would fire the rule with probability near one. **I cannot
exclude a consequential shift; I have shown only that the amendment's positive
assertion is unsupported.** Both directions are unproved, and the record states
one of them as fact.

This does not change the acceptance decision. It changes what may be written
about it: the honest form is *"V2 is exactly invisible (theorem) and its effect
on the estimand is unmeasured; the campaign's own resolution is an order of
magnitude too coarse to settle it."* The current wording licenses a downstream
reader to treat "silent wrong answer" as demonstrated when it is hypothesised —
and, symmetrically, licenses nobody to relax about it.

---

## 5. `RT3-OBJ-3` — dropping PS-A, and a stress test the amendment did not run

**The drop is right. I argue it, as the card asks, and then I strengthen the
half of the record that is weaker than the producer realised.**

### 5.1 Is criterion (iv) still worth satisfying without the anchor?

**Yes, narrowly, and only if the narrowing travels.** The argument:

1. **The anchor could never have delivered an order-matched cell.** PS-A's
   `k = m = 16` needs `T_stab = 1.246e45` — I re-derived this independently and
   reproduce it exactly (§7). What is dropped is `k = 2` and `k = 3` at the
   anchor: two low-order cells, never the thing (iv) was for.
2. **A cell you cannot size is worse than a cell you do not certify.** PS-A's
   3 SE(q̂)/q̂ is 3.33 % against 0.06–0.12 % elsewhere, because Stage A recorded
   **8,122** block failures there against 5.2e6–1.3e7 at the reduced sets. That
   is a counting-statistics fact about the anchor, not a defect in the rule.
   Certifying a cell whose realized size moves from 0.0037 to 0.0015 across its
   own plug-in uncertainty would be the VF-1 failure again, one level out.
3. **Nothing is suppressed.** PS-A is still run, still reported, marked
   `NOT CERTIFIED UNDER (iv)` with its sensitivity rows attached, and a costed
   successor (re-derive at the Stage-B q̂: 3 SE falls 3.33 % → 0.242 %, factor
   13.8) is named **with its own risk stated** — that the interval becomes a
   function of the data it scores, reintroducing the coupling R1 removed. That
   is exactly what `AGENTS.md` research-direction integrity requires of a
   deprioritization: evidence, budget, test boundary, residual uncertainty,
   concrete successor.
4. **The goal's own criterion 1 asks for reduced parameters.** (iv) after the
   drop is a statement about an instrument at an order-matched surrogate. That
   is a legitimate instrument result and it is all this campaign was ever going
   to have. It is *not* a statement about HQC-1, and the amendment says so in
   the loudest text in the file.

**What I hold against it:** the amendment says the narrowing "must appear in
every downstream record" but the enforcement is prose. See §9 correction 3.

### 5.2 The stress test nobody ran, which favours the amendment

`the_SE_reference_is_a_LOWER_bound_and_v2_called_it_a_bound` correctly records
that `SE(q̂)/q̂ = sqrt((1−q)/failures)` is the **ρ = 0** value, and defends the
reduced sets using the validator's *measured* inflation factors
(1.00 / 1.34 / 1.69 / 2.35). Nobody asked what happens at the **physical
maximum** of the nuisance the experiment exists to detect. I did.
Artifact: `rho_stress.py`, `rho_stress.txt`.

At ρ = 1, inflation is `sqrt(1+(n_e−1))`: ×7.483 at PS-R3, ×6.782 at PS-R1,
×9.487 at PS-R5. Measured, 400,000 draws per point, my own seeds, all reported
cells:

| set @ T | 3 SE(ρ=0) | 3 SE(ρ=1) | size range at −3 SE(ρ=1) | at +3 SE(ρ=1) | all cells in `[0.002,0.004]` |
|---|---|---|---|---|---|
| **PS-R3 @ 1e7 (funded)** | 0.000817 | 0.006117 | 0.00293 – 0.00331 | 0.00227 – 0.00261 | **YES** |
| PS-R1 @ 1e8 | 0.001179 | 0.007994 | 0.00300 – 0.00349 | **0.00200** – 0.00263 | yes, **on the gate edge** |
| PS-R5 @ 2e7 | 0.000632 | 0.005999 | 0.00279 – 0.00358 | 0.00205 – 0.00242 | yes, thin |

*(Artifact note: `rho_stress.txt`'s per-line text says "all 17" at every set
because the count is hard-coded in the print format. The check itself is over
**every reported cell** of each configuration — 17 at PS-R3, 14 at PS-R1, 28 at
PS-R5 — as `rho_stress.py` shows. Cosmetic; the verdict column is correct.)*

**The funded configuration holds the acceptance band across ±3 SE even if every
block were perfectly correlated** — the worst case the nuisance can physically
take. That is a stronger robustness statement than the amendment makes for
itself, and it is the single best reason to admit. PS-R1 and PS-R5 are *not*
comfortable at that extreme (PS-R1's `+3 SE(ρ=1)` minimum is 0.00200, exactly
the gate boundary), which is worth recording because v3's blanket
"PS-R1/R3/R5 are robust" is true at ρ = 0 and true-but-marginal at ρ = 1.

---

## 6. VF-1 independently re-measured — the gate the card told me not to take on trust

Artifacts: `resize.py`, `resize_results.json`. Own loader, own seeds
(SHA-256 of this task id, not the producer's namespace), own draws, 1,000,000
validation replicates per configuration.

- **1,009 numeric fields** in `amendment_v3.yaml` (609 in `frozen_intervals`,
  400 in `q_sensitivity`) **all parse as `float`**. The `1e-05` trap is real and
  reproduces: `yaml.safe_load("v: 1e-05")` returns a `str`, `"v: 1.0e-05"` a
  `float`. The guard is load-bearing and it works.
- **PS-R3 @ 1e7, the funded configuration, all 17 cells:**

| k | producer | this review [95 % CI] | k | producer | this review [95 % CI] |
|---|---|---|---|---|---|
| 2 | 0.00273 | 0.00267 [0.00257, 0.00278] | 11 | 0.00262 | 0.00268 [0.00258, 0.00278] |
| 3 | 0.00278 | 0.00267 [0.00257, 0.00277] | 12 | 0.00265 | 0.00273 [0.00263, 0.00283] |
| 4 | 0.00278 | 0.00270 [0.00260, 0.00281] | 13 | 0.00259 | 0.00271 [0.00261, 0.00282] |
| 5 | 0.00278 | 0.00279 [0.00269, 0.00289] | 14 | 0.00257 | 0.00267 [0.00257, 0.00278] |
| 6 | 0.00278 | 0.00274 [0.00264, 0.00284] | 15 | 0.00260 | 0.00258 [0.00248, 0.00268] |
| 7 | 0.00276 | 0.00268 [0.00258, 0.00278] | 16 | 0.00267 | 0.00263 [0.00253, 0.00273] |
| 8 | 0.00277 | 0.00273 [0.00263, 0.00284] | 17 | 0.00270 | 0.00260 [0.00250, 0.00270] |
| 9 | 0.00271 | 0.00272 [0.00262, 0.00283] | 18 | 0.00278 | 0.00259 [0.00249, 0.00269] |
| 10 | 0.00265 | 0.00274 [0.00264, 0.00284] | | | |

  **Zero cells outside `[0.002, 0.004]`**, range 0.00258–0.00279 against the
  producer's 0.00257–0.00278. PS-A (k=2 0.00274, k=3 0.00261) and PS-R1
  (14 cells, 0.00264–0.00280) likewise: **33 cells re-measured, zero outside
  the gate.**

  **Agreement, stated precisely rather than generously.** Across all 33 cells,
  **one** producer/reviewer difference exceeds 2σ of the two-sample
  Monte-Carlo error — PS-R3 k=18, 0.00278 vs 0.00259, **z = −2.62**. At 33
  comparisons ≈1.7 are expected past 2σ, so this is what agreement looks like,
  not a discrepancy; but it is not the case that every producer value falls
  inside my interval and I do not claim it. Nothing turns on it: k=18's size is
  0.00259 either way, comfortably inside the gate, and the gate is what binds.

**VF-1 is closed and I closed it myself.** The producer's own caveat stands and
I endorse it: VF-2 means 0.26 % is close to a tautology about Monte-Carlo
quantile error, and this table's job is only the differential check that the
*encoded* constants realize the size of the constants they were meant to encode.
Against v2's table the same measurement returned 0.610 / 0.419 / 0.551 %. It
does that job.

---

## 7. VF-3 independently re-measured — closed, with one sub-claim withdrawn

Same artifacts, 400,000 draws per shift point, my own seeds.

**PS-A @ 1e8:**

| shift | SE | k=2 | k=3 |
|---|---|---|---|
| −3 SE | −3.00 | 0.00369 in | **0.00391 in** ← does not reproduce |
| −2 SE | −2.00 | 0.00327 in | 0.00339 in |
| 0 | — | 0.00260 in | 0.00263 in |
| +1.80 SE (+2 %) | +1.80 | 0.00228 in | **0.00195 OUT** |
| +2 SE | +2.00 | 0.00218 in | 0.00200 (on the edge) |
| **+3 SE** | +3.00 | **0.00186 OUT** | **0.00148 OUT** |

**PS-A fails, and the drop is correct** — but the *reason* stated in the record
is half right. The **conservative failure on the + side is solid and
reproduces**: k=2 leaves the band at exactly 3 SE, k=3 by 1.8–2 SE, both far
outside. The **anti-conservative failure on the − side does not reproduce**: the
producer measured 0.00409 and the validator 0.00404 at −3 SE, both barely past
0.004; I measure **0.00391**, inside. At 400,000 draws the Monte-Carlo SE at
that level is ≈1.0e−4, so the three measurements are 0.00391 / 0.00404 / 0.00409
— a spread of 1.8 SE straddling the gate edge. `VF_3_resolution` states as fact
that k=3 *"leaves the band on BOTH sides — anti-conservative at −3 SE"*; on
three measurements that is a coin flip, not a finding. Correction in §9.

**PS-R3 @ 1e7, all 17 cells** — the range over cells at each shift:

| shift | SE | min | max | all in band |
|---|---|---|---|---|
| −3 SE (−0.000817) | −3.00 | 0.00265 | 0.00283 | **yes** |
| 0 | — | 0.00263 | 0.00280 | yes |
| +3 SE (+0.000817) | +3.00 | 0.00241 | 0.00288 | **yes** |
| ±1 % | ±36.7 | 0.00183 | 0.00397 | no |
| ±4 % | ±146.8 | 0.00055 | 0.00974 | no |

Minimum breakdown margin over 3 SE across the funded cells: **12.2×**,
reproducing the amendment exactly. I also checked that the reported
`breakdown_rel_shift` values are **genuine measured breakdowns and not the grid
ceiling** — cells recorded at 0.04 are inside the band at 0.02 and outside at
0.04 on my own grid, so the "48.9×" figures are measurements, not censored
values. That was my first suspicion and it is wrong.

**Reachability arithmetic re-derived from scratch** (`k_max`, `T_stab`, `s_90`
at the measured q̂): `k_max` = 3 / 15 / **18** / 20 / 29 and `T_stab(m)` =
1.246e45 / 1.452e8 / **1.000e6** / 1.000e6 / 2.554e7. **Every value reproduces
exactly**, including the funded cell's 10× margin at `k = m = 17`.

---

## 8. `RT3-OBJ-4` — the familywise size is right, and the amendment does not quite bind how it is read

**Severity: governance. Confirmed numerically.**

Measured under the **exact** binomial null, 1,000,000 replicates, my own seeds,
"any reported cell outside its interval":

| configuration | cells | familywise rate [95 % CI] | × the 0.27 % per-cell nominal | producer |
|---|---|---|---|---|
| **PS-R3 @ 1e7 (funded)** | 17 | **1.001 %** [0.981, 1.020] | **3.71×** | 1.03 % |
| PS-R1 @ 1e8 | 14 | 1.140 % [1.120, 1.161] | 4.22× | 1.09 % |
| PS-A @ 1e8 | 2 | 0.532 % [0.518, 0.546] | 1.97× | — |

**RT2-OBJ-1's mitigation cost is real and the producer reported it accurately.**
Nothing here contradicts the record. The objection is to the *governance*:

1. **Criterion (iv) v3 mandates a 17-cell report** ("for EVERY k in 2..k_max"),
   so a battery reading is not optional — it is what the criterion produces.
2. **The multiplicity warning is attached to a self-assessed trigger.** The
   binding requirement is *"the familywise flag rate of the multi-k battery,
   **whenever a battery reading is relied upon**"*. "Relied upon" is undefined
   and self-declared. An executor who reports 17 cells and observes one firing
   can consistently say it is not relying on a battery reading, omit the rate,
   and report a 0.27 % cell — which is the exact misreading `RT2-OBJ-1` says
   "must never" happen.
3. **The criterion (iv) text itself carries no multiplicity language at all.**
   The warning lives in `open_items`, two thousand lines away from the sentence
   a downstream record will quote.

**Why this is not a blocker.** `TASK-20260806-cde749`'s card forbids the
Executor from concluding anything; the interpretation happens at the
Coordinator's ledger archive, where §9 correction 4 is a one-line fix. But the
fix must be made *before* the measurement, not after, because the number will
travel from the measurement report.

---

## 9. Verdict, and the corrections it is subject to

## **ADMIT.**

**What I would have needed for DO-NOT-ADMIT, and why this is not that.** A
refusal here spends the campaign's last batch on nothing. It is warranted if the
rule that governs the funded measurement is wrong, unmeasured where it is
load-bearing, or advertised as something it is not. I tested all three against
the funded cell, with my own code, seeds and draws:

- the encoded rule realizes its intended size at **all 17** PS-R3 @ 1e7 cells
  (§6);
- it holds the band across ±3 SE at every one of them, and **also at ρ = 1**,
  the physical maximum of the nuisance (§5.2);
- its reachability arithmetic reproduces exactly (§7);
- its advertised control list is now **factually correct in both directions**,
  confirmed by re-injection on an independent seed (§3);
- I found **no security claim about HQC** anywhere in the four artifacts.

The defect I did find (§2) is in a control that (a) is labelled SPECIFICATION
ONLY by the producer itself, (b) has never run, (c) is arithmetically correct at
`dup = 1` and therefore at the funded set, and (d) is repaired by changing
`n_2*dup` to `n_2` in one line. Refusing the whole amendment over an unrun
control that cannot affect the funded number would be premature closure
(`docs/inventor-protocol.md` §4), and it would leave the campaign with the *v1*
INV-NULL — the rule measured at 0.30 %–23.55 % size — as the only thing in
force. That is strictly worse than admitting the repaired one.

### Binding corrections — all edits, none requiring new measurement

1. **Fix CTRL-IDXMAP's reference expression.** `L = n_2*dup` → `L = N/n_e`
   ( = `n_2`), and record that as written the control fires with certainty on a
   *correct* run at PS-A. Add the `dup`-stride defect to
   `what_it_CANNOT_detect_stated_plainly` explicitly, and strike or qualify
   *"the extension that closes that step"* — after the repair one named defect
   (`OPEN-10`) still sits inside the intersection of CTRL-POSHOM's and
   CTRL-IDXMAP's blind spots. Re-run the demonstration at `dup = 3`. **(§2)**
2. **Resolve the sampler contradiction before dispatching the measurement.**
   `what_v3_does_not_change` says the (T) sampler is UNCHANGED;
   `CTRL_IDXMAP.construction` binds the sampler to express truncation and block
   extraction as index arrays and *gather* through them. `stage_a.py` does
   neither — it uses `epp & mask_N` and `reshape` (§3.3). The measurement card
   orders the Executor to "run every control the admitted amendment declares".
   **The Coordinator must state, in the measurement card, that CTRL-IDXMAP is
   NOT RUN / SPECIFICATION ONLY and that the (T) sampler is not to be modified.**
   The failure mode this forecloses is an executor rewriting the frozen sampler
   to satisfy a blocking gate, in the last batch, with no review left.
3. **Narrow the VF-3 sub-claim.** `VF_3_resolution` asserts PS-A k=3 *"leaves
   the band on BOTH sides — anti-conservative at −3 SE"*. Three independent
   measurements give 0.00391 / 0.00404 / 0.00409 against a 0.004 gate and a
   ≈1.0e−4 Monte-Carlo SE. The + side reproduces solidly and is sufficient;
   the − side should read "at or just past the gate edge, within Monte-Carlo
   resolution". The drop decision is unaffected. **(§7)**
4. **Make the multiplicity binding unconditional.** Replace *"whenever a battery
   reading is relied upon"* with an unconditional requirement, and put one
   sentence **inside criterion (iv)'s own text**: *a set of per-k firings from
   the 17-cell report is a familywise-1.0 % observation, not a 0.27 % one, and
   no downstream record may describe it as the latter.* **(§8)**
5. *(Not binding, recorded.)* Restate `the_structural_argument` clause (3) to
   separate the **proved** invisibility of V2 from the **unmeasured** claim that
   it changes the estimand, citing this report's paired-contrast bound. **(§4)**

**Claim tier stays TOY.** Nothing in this batch, mine included, is a result
about HQC. I changed no status, no ledger record, no experiment contract, and
nothing under the producer's frozen task directory; all four frozen hashes
verify unchanged after my runs.

---

## 10. Cheapest falsification of each v3 claim

| claim | cheapest observation that falsifies it | cost |
|---|---|---|
| VF-1 "87 cells, all inside the gate" | load the constants with an independent loader and re-measure — **done** (§6), it holds; to falsify *me*, find a numeric field in the file that parses as `str` (I checked all 1,009) | 60 core-s |
| VF-3 "PS-R1/R3/R5 robust over ±3 SE" | **done** (§7); to falsify the *defence*, note the SE is the ρ=0 value — **done** (§5.2), it survives even ρ=1 at PS-R3 | 120 core-s |
| VF-3 "PS-A k=3 is anti-conservative at −3 SE" | **already falsified as stated** (§7): 0.00391 on 400k independent draws | free, done |
| CTRL-POSHOM's corrected list | re-inject on an independent seed — **done** (§3), it reproduces | 730 core-s |
| **CTRL-IDXMAP "detection probability 1"** | **already falsified as specified** (§2): run the amendment's own reference expression at PS-A and it raises `IndexError` on a correct instrument. To falsify *my* repair, exhibit a set with `N ≠ n_e·n_2` | free, done |
| CTRL-IDXMAP "closes the shift-equivariant class" | **already falsified** (§2.4): the `dup`-stride defect has a bit-identical index map | free, done |
| "V2 changes the estimand" | measure the paired contrast against V1, the exact null — **done** (§4): indistinguishable at 400k. To settle it properly, 4e6 trials would reach ~1e−4 bits, still above the funded half-width | ~7,000 core-s (not spent) |
| familywise 1.03 % | **done** (§8): 1.001 % [0.981, 1.020] on my own draws | free with §6 |
| `k_max = 18`, `T_stab(17) = 1e6` | re-derive from `s_90` — **done** (§7), exact | free |
| RT2-OBJ-1 "PS-R3 is 556× further from the binomial" | search over supports rather than one hand-picked triple; the producer says it ran none | ~30 core-min (not spent) |

---

## 11. Artifacts

All under
`coordination/goals/GOAL-HQC-001/batches/BATCH-0a65c0/reviews/TASK-20260806-250b29/`:

| file | what it is |
|---|---|
| `reinject.py` | six-variant (T) injection harness, seed `0x250B29`; self-tests against `stage_a.decode_blocks` on every decode |
| `reinject_PS-R1.json` | 400,000-trial REF-1 / REF-3 clause (a) and (b) per variant |
| `idxmap_probe.py`, `idxmap_probe.json` | CTRL-IDXMAP implemented **as specified** and applied to the four real parameter sets; the repaired version; the `dup`-stride blind spot |
| `resize.py`, `resize_results.json` | independent size of the encoded constants, q-sensitivity grid, familywise rate |
| `rho_stress.py`, `rho_stress.txt` | q-sensitivity at ρ = 1, the physical maximum of the nuisance |
| `v2_estimand.py`, `v2_estimand.json` | paired `Δ log2 Â_k` of V1/V2/V3 against V0 on shared draws, with V1 as the exact-null control |
| `reinject_stdout.txt`, `reinject_time.txt`, `v2_estimand_stdout.txt` | raw stdout and timings |

*Red-team record. I wrote only inside this directory. I hold no authority to
change status and changed none.*
