# J6 — cost, scope, and what a PASS licenses

**Task** TASK-20260907-ee1ca7 (Red Team, independent session, blind to
TASK-20260907-b2a8ad) · **Batch** BATCH-8f3e86 · **Goal** GOAL-ECDLP-bbc21f
· **Experiment** EXP-ECDLP-612fb1 under `amendments/v2_to_v3.yaml`
· **Snapshot read** `fe6cdf59f`

**Verdict on J6: HOLDS on the producer's package; BREAKS on the contract's own
premise for U1.** I found no overclaim in anything the Executor wrote. I did
find that the amendment's residual R3 asserts a property of STAGE 3B — a third
*independent* angle — that STAGE 3B cannot have, and the numbers now prove it
does not have. That is a defect in the frozen contract's premise, not in the
execution, and the Executor flagged the coincidence itself (U1) without drawing
the conclusion.

All citation provenance below is `internal` unless marked otherwise.

---

## 1. Sentence-level audit against amendment Section 9

Section 9 states four things a PASS does and does not license. I read the
Executor's `execution_report.yaml`, `artifact_inventory.json`,
`source_v3/IMPLEMENTATION.md`, the eleven run records and the analysis run's
thirteen artifacts against each.

### (1) The ceiling/mechanism slide — **not found**

`DEC-20260907-9b1b02` recorded this exact slide once already in the concurrent
lane, so I searched for it specifically rather than generically: a grep for
`attain|achiev|mechanism|feasib|online|half the table|advice ratio` across the
execution report, `IMPLEMENTATION.md` and the analysis `stdout.log` returns
seven hits, and every one of them is a *disclaimer*:

- `scope_statement.what_this_execution_does_not_state` — "does not state
  whether ceiling feasibility holds, does not state anything about clause (C1)
  of H-ECDLP-37dc01, does not resolve EV-ECDLP-2e9680 a = 1/8 disagreement,
  does not reopen or weaken EV-ECDLP-60e266 obstruction, and asserts nothing
  about any online re-selection procedure attaining the measured ceiling."
- `scope_statement.arms_not_run` — "no online arm of any kind."
- `interpretation_statement` — "OBSERVATIONS ONLY … The Coordinator interprets."
- `gate_ordering_note` — "No artifact this task produced contains an
  interpretive line at all."

I verified that last claim rather than accepting it: no analysis artifact
contains a sentence asserting feasibility. The G3 verdict table is literally
the first content block of the execution report, ahead of the disclaimer.

**No sentence in the producer's package reads a ceiling result as a mechanism
result.** The producer is clean here, and unusually so.

### (2) "Smaller `a` is not free" — **the frontier tuple is carried; the risk is downstream**

The review plan named this as the most likely break. It does not break in the
package — but it is live for any reader of it, and the numbers are stark enough
that I state them here so the Coordinator cannot slide.

`cost_table.json` carries, **per cell**, `top_share_T_sel_mean`,
`static_cov_mean`, `margin_mean`, `margin_null_mean`,
`S_bits_oracle_T_sel_table`, `S_bits_static_T_table`,
`S_peak_bits_pool_working_storage`, `P_group_ops_mean`, `P_over_sqrt_NT_mean`,
`generating_walks_mean` and `capped_walk_fraction_mean`, with `W`, `theta` and
`cap` in the adjacent `modeled` block. **No ratio appears anywhere in the
package without its frontier tuple, because no ratio appears anywhere in the
package at all.** The producer quotes no advice ratio.

Here is the full tuple at N = 2^24, r = 2, recomputed by this Red Team from
each measurement run's own `raw-result.json` (means over the five frozen
seeds):

| a | W | TopShare(T) | TopShare(T/2) **ceiling** | StaticCov(T,2) **achieved** | S, T/2 table | S, T table | S_peak | P (ops) | P/√(NT) |
|---|---|---|---|---|---|---|---|---|---|
| 1/16 | 64.000 | 0.183307 | **0.117445** | 0.096880 | 6144 b | 12288 b | 49152 b | 34509 | 0.5266 |
| 1/8 | 90.510 | 0.271302 | **0.179119** | 0.172186 | 6144 b | 12288 b | 49152 b | 51762 | 0.7898 |
| 3/16 | 110.851 | 0.339271 | 0.231029 | 0.241024 | 6144 b | 12288 b | 49152 b | 67424 | 1.0288 |
| 1/4 | 128.000 | 0.389872 | 0.271307 | 0.290613 | 6144 b | 12288 b | 49152 b | 81464 | 1.2430 |

The two bolded ceilings are the cells that PASS. **They are the two lowest
absolute coverages in the grid.** The a = 1/16 *oracle* half-table covers
0.117445 of N per walk; the a = 1/4 *realistic full* table — already achieved,
already committed, and the cell where G3 fails — covers 0.290613, which is
2.47× more. A G3 PASS at small `a` does not mean anything got better; it means
the ceiling fell far enough that a roughly constant estimator loss dominates it.

Normalising away the walk-length difference does not rescue it. Derived by this
Red Team (my own composite, stated as such, with the raw tuple above so a reader
can form their own):

| a | ceiling coverage / W | achieved coverage / W |
|---|---|---|
| 1/16 | 0.0018351 | 0.0015137 |
| 1/8 | 0.0019790 | 0.0019024 |
| 3/16 | 0.0020841 | 0.0021743 |
| 1/4 | 0.0021196 | **0.0022704** |

Per unit of expected online walk length, the **unattainable** a = 1/16 ceiling
is **19.2 % below** the **attained** a = 1/4 static table, and the a = 1/8
ceiling is 12.8 % below it. Per unit of precomputation the picture is nearly
flat and still adverse: coverage ÷ (P/√(NT)) is 0.2230 at the a = 1/16 ceiling
against 0.2338 at the a = 1/4 achieved table, i.e. 4.6 % worse.

**The one axis on which the small-`a` cells win is the one the claim is about:
advice size, 6144 bits against 12288, exactly 2×.** That is a genuine trade, not
a free lunch, and it must be quoted as a trade.

### (3) Measured / modeled separation — **clean, with one classification note**

`cost_table.json` keeps two disjoint top-level blocks. `modeled` holds only
`N, T, T_sel, W, theta, cap` plus the generating formula. `measured` holds
counts, coverages, margins, bit counts and resource measurements. **No column
collision.**

One note, not a defect: `S_bits_oracle_T_sel_table`, `S_bits_static_T_table`
and `S_peak_bits_pool_working_storage` sit in the `measured` block but are pure
arithmetic in `(T_sel, T, r, n)` — nothing was measured to obtain them. The
amendment's own `required_artifacts_per_run.notes` classifies bit counts as
MEASURED, so the producer followed the contract exactly. The contract's
classification is what is loose, and a later reader could take "measured
storage" for an observation. Low severity; recorded so it is not rediscovered.

### (4) Scope — **stated correctly, with one ledger gap for the archive task**

- `claim_tier: toy` is stated in `scope_statement` and unchanged. ✅
- No claim reaches outside the run cells: `tested_parameters` names exactly
  `N ∈ {2^20, 2^24}`, `a ∈ {1/16, 1/8, 3/16, 1/4}`, `r ∈ {2, 4, 8}`, seeds
  {1..5}, `T_sel = floor(T/2)`, exact basins; `transfer_assumptions_made_by_this_report: none`. ✅
- `cells_not_run: []` with every cell of the stage plan executed, so nothing is
  reported as a negative in place of a missing measurement. ✅
- **EV-ECDLP-60e266's obstruction is neither reopened nor weakened.** a = 1/4
  returns 0/5 at both N with every per-seed margin negative, and my own
  diagnostic extends that to 0 of 20 seeds and 0 of 15504 five-seed draws at
  N = 2^24. The obstruction is corroborated at four times the seed count, not
  eroded. ✅
- **The `a`-widening.** Section 9 restates it and
  `H-ECDLP-37dc01.test_boundary.boundary_amendments` carries exactly one entry,
  dated 2026-09-07, widening `a` to include {1/16, 1/8, 3/16}. That entry names
  `experiment_id: EXP-ECDLP-6ac801`. **It does not name EXP-ECDLP-612fb1 or its
  v3 item.** The widening is therefore disclosed, but the hypothesis record does
  not yet record that *this* experiment is also being evaluated outside the
  original boundary. This is a ledger-archive housekeeping item for
  TASK-20260907-33a736, not a defect in the producer's package, and I flag it
  because a later reader auditing "which experiments were evaluated outside the
  stated boundary" would miss this one.

---

## 2. U1 — was the third independent angle delivered?

**No. Not at N = 2^24, r = 2 — and not at N = 2^20 either.**

The amendment's residual **R3** describes running this predicate on the frozen
v2 instrument as a third angle: *"a different experiment identifier, a
different random-function family, a different basin-closure implementation from
either 6ac801 arm."* Exactly one of those three is true.

- **Different experiment identifier** — true, and it is the weakest of the
  three. An identifier is not an instrument.
- **Different random-function family** — false. The amendment's own Section 3
  `reading_P1_frozen_instrument` *requires* STAGE 3B to use v2's splitmix64 map
  and DP predicate verbatim, and `required_implementation_files` *requires*
  `run_stage3.py` to import `source_v2/instrument.py` unchanged. Meanwhile
  `EV-ECDLP-2e9680`'s `a_1_8_disagreement.root_cause` records that
  EXP-ECDLP-6ac801's production Stage B was "reusing
  experiments/EXP-ECDLP-612fb1/source_v2/instrument.py unchanged". Same module.
- **Different basin-closure implementation** — false, for the same reason:
  `g3_predicate.exact_basins` is a one-line delegation to `I.exact_basins`.

The measurement confirms it. STAGE 3B's r = 2 margins at N = 2^24 reproduce
6ac801's *production* margins to all six quoted decimals at every `a` the prior
record quotes (U1), and STAGE 3A reproduces the committed a-scan **bitwise**,
maximum absolute difference exactly 0.0 over 20 rows (U3). Two deterministic
programs sharing a module, a seed policy and a pool draw agreeing bitwise is
not corroboration; it is a determinism check. A valuable one — it proves the
new driver did not corrupt the frozen instrument — but it carries no
independence.

**Three consequences the Coordinator should not have to derive:**

1. **STAGE 3B does not resolve the a = 1/8 disagreement inside
   EV-ECDLP-2e9680.** That disagreement is blind (1/5) against production
   (5/5). STAGE 3B re-executes the production side. Re-running one side of a
   disagreement cannot settle it, however many decimals it reproduces. The
   Executor states this correctly and does not claim otherwise.
2. **R3 is still owed.** The residual the amendment opened remains open, and the
   amendment's own text is what asserted it had been discharged.
3. **Whether this batch delivers any independent angle at all rests entirely on
   the Validator's J2 blind re-derivation, which I am blind to by construction.**
   I therefore cannot judge it, and I record that limit rather than filling it.
   The frozen plan already discloses that J2's independence is itself partial —
   the re-deriver must read the amendment, whose Section 1 quotes the prior
   lane's per-seed margins.

The snapshot receipt for TASK-20260907-7bf406 states plainly that no joint in
the frozen plan names this question in these words and routes it to the nearest
owned joint. That gap was stated rather than hidden, and it is answered here.

---

## 3. What a PASS licenses, and what hides in the gap

**Licensed, if and only if J1/J2/J3 also hold** (owned by the Validator; I take
no position): at N = 2^24, on the splitmix64 keyed-random-function instrument,
T = 256, T_sel = 128, r = 2, exact basins, five declared seeds, the exact
coverage of the best possible 128-entry table reached or exceeded the exact
coverage of the w(d)-selected 256-entry table, at a = 1/16 (5/5) and a = 1/8
(5/5). That is a statement about the basin-size distribution and the
estimator's loss at those parameters. Under my own 15 extra seeds it is more
robust than five seeds could show: 20/20 and 19/20 per-seed margins positive,
and 15504/15504 five-seed draws PASS at both cells.

**Not licensed, and the gap is large:**

1. **No mechanism.** `TopShare(T_sel)` is an oracle: it is the top-128 basins by
   *true exact size*, which no selection rule can identify. Zero online arms ran.
   Nothing here says any re-selection procedure attains the ceiling at any batch
   size U. This is the distinction Section 9 bullet 2 exists to protect.
2. **No exponent.** Every statement is a constant-factor statement under the
   Corrigan-Gibbs–Kogan `S·T² = Ω̃(εN)` preprocessing ceiling
   (KN-LIT-013, cited via the v1/v2 contracts; provenance internal — this Red
   Team did not open the corpus entry). No asymptotic promotion gate is engaged.
3. **No group.** The instrument is a keyed random function on Z_N with an
   independently keyed DP predicate. No curve arm, no cryptographic N, no named
   scheme. Nothing here is an ECDLP result.
4. **The scale gap, stated as orders of magnitude.** Tested N spans 2^20 → 2^24:
   a factor of 16, **1.2 orders of magnitude**. A cryptographically relevant
   group order is ≈ 2^256, another **≈ 70 orders of magnitude**, with
   T = N^{1/3} moving from 256 to ≈ 2^85 — about 25 orders of magnitude in T.
   The batch's entire N-dependence evidence is two points: the pooled a = 1/8
   margin is +0.004724 at N = 2^20 and +0.006933 at N = 2^24. It did not shrink.
   Two points do not carry a trend and I do not read one.
5. **What breaks first, named concretely.** From the decomposition in J5,
   `margin = estimator_loss − halving_loss`. The estimator loss saturates near
   **0.099** for every a ≥ 1/8 at *both* tested N (0.0955/0.1038/0.0990 at
   T = 64; 0.0991/0.0982/0.0993 at T = 256), while the halving loss tracks
   `TopShare(T)` and grows with `a`. G3 is feasible exactly where `TopShare(T)`
   is small enough that roughly a third of it sits under that ≈ 0.099 ceiling —
   the crossing lies between `TopShare(T) = 0.271` (a = 1/8, PASS) and `0.339`
   (a = 3/16, FAIL). **The load-bearing extrapolation is therefore that
   `estimator_loss(T, r = 2)` stays ≈ 0.099 as T grows by ≈ 2^77.** The batch
   measures it at T = 64 and T = 256 — two points, 2 bits of T out of ≈ 79 —
   where it is remarkably flat (0.099049 → 0.099258 at a = 1/4). That is the
   quantity that decides whether any of this transfers, and it is the quantity
   with the thinnest evidence. It is cheap to extend and nobody has.

---

## 4. Pareto honesty

**`dominated_by`** — I checked every frontier row available in this lane before
answering, and the answer is not a bare `null`.

Rows checked (all `provenance: internal`):

1. N = 2^24, a = 1/4, r = 2, STATIC(T) — coverage 0.290613, S = 12288 b,
   S_peak = 49152 b, P/√(NT) = 1.2430, W = 128
   (`RUN-ECDLP-612fb1-v3-g3x24-s1..s5`; consistent with EV-ECDLP-60e266's
   recorded "the r = 2 static selection already captures 0.29").
2. N = 2^24, a = 3/16, r = 2, STATIC(T) — 0.241024, P/√(NT) = 1.0288.
3. N = 2^24, a = 1/8, r = 2, STATIC(T) — 0.172186, P/√(NT) = 0.7898.
4. N = 2^24, a = 1/16, r = 2, STATIC(T) — 0.096880, P/√(NT) = 0.5266.
5–6. N = 2^24, a ∈ {1/16, 1/8}, ORACLE(T/2) — 0.117445 / 0.179119, S = 6144 b,
   **unattainable**.
7. All eight N = 2^20 counterparts (`RUN-ECDLP-612fb1-v3-rep20-s1..s5`).
8. EV-ECDLP-60e266's own recorded frontier quantities — `rho_ORACLE = T_sel/T`
   at which ORACLE(T_sel) matches STATIC(T), and `rho_T(U)` steady-state and
   cumulative — which already frame this lane as a ceiling calculation
   ("fixed-advice re-selection can buy at most `1 − rho_ORACLE ≈ 0.45` of the
   advice at a = 1/4").

**Answer.** On the achievable `(P, S, coverage)` tuple, **no measured point in
this grid dominates another**: moving `a` trades P against coverage
monotonically, so all four rows sit on a trade curve. `dominated_by: null`
would be technically defensible on that tuple alone and would also be
misleading, so I do not record it. The honest statement is:

> **This batch produces no point on the achievable frontier at all.** The only
> quantity that turns positive at a ∈ {1/16, 1/8} is `TopShare(T_sel)`, an
> oracle no selection rule attains, and zero online arms were run. There is
> therefore nothing to dominate and nothing to be dominated. Judged as a
> *ceiling*, the a = 1/16 result is beaten on two of three normalisations by a
> row this lane already holds: row 1 above (a = 1/4, r = 2, STATIC(T),
> N = 2^24) achieves 0.0022704 coverage per unit W against the a = 1/16
> ceiling's 0.0018351, and 0.2338 coverage per unit P/√(NT) against 0.2230.

**`sota_delta`** — **0.000 on every achievable axis** (time, memory, data,
advice, queries), because no achievable object was produced. The measured
*ceiling* delta, which is what the batch actually establishes, is:

- `+0.020565` (a = 1/16) and `+0.006933` (a = 1/8) in exact single-walk hit
  probability at N = 2^24, r = 2, of the best-possible 128-entry table over the
  w(d)-selected 256-entry table, i.e. **at half the advice** (6144 vs 12288
  bits) at `W = 64` / `W = 90.51` and `P/√(NT) = 0.527` / `0.790`;
- pooled BCa 95 % CI `[0.016375, 0.025305]` and `[0.004497, 0.009939]`
  respectively, 10000 resamples, resampling unit = seed (the producer's
  disclosed deviation D3), from a maximum of 5⁵ = 3125 distinct resamples;
- and **negative** at a = 3/16 (`−0.009995`) and a = 1/4 (`−0.019307`), which
  is where the previously claimed operating point sits.

Against the prior state of knowledge, the delta is narrower still: `a = 1/16`
was already CONFIRMED G3-feasible twice inside EV-ECDLP-2e9680 (blind 5/5 and
production 5/5), and STAGE 3B reproduces the production arm bitwise, so it adds
reproducibility rather than corroboration (§2). The genuinely new measurements
in this batch are the first null-object and decay controls ever applied to the
G3 margin (amendment residual R5) — and the first red-team pass on this lead
(R2), which is this document.

---

## 5. Forward guidance

Two cheap measurements that the basins already computed here would give for
nearly nothing, and which would answer more than another PASS/FAIL would:

1. **The whole curve, not the point.** The batch evaluates
   `TopShare(t) − StaticCov(T, 2)` at exactly one `t = T/2` and reduces it to a
   boolean. The zero-crossing `rho_ORACLE(a) = t*/T` is the quantity
   EV-ECDLP-60e266 already named, is a continuous and far more informative
   object than a binary verdict, and costs one extra sort per (a, seed) once the
   exact basins exist. Reporting `rho_ORACLE(a)` for `a ∈ {1/16 … 1/4}` would
   replace four bits of information with four numbers.
2. **`estimator_loss` against T.** Per §3.5 this is the load-bearing quantity
   for any transfer claim and it has two measured points. A T-sweep at fixed
   N = 2^24 (T ∈ {64, 128, 256, 512, 1024}, exact basins already affordable at
   0.46 GiB and 24 s per seed) would turn "we measured two points and they were
   flat" into a trend, or falsify it. Nothing else in this lane changes what a
   PASS at toy scale is worth as much as that would.

---

## 6. Terminal J6 statement

The producer's package overclaims nothing, quotes no ratio without its frontier
tuple, mixes no measured and modeled column, states the toy tier, reaches
outside no run cell, and neither reopens nor weakens EV-ECDLP-60e266. I looked
specifically for the four failure modes the review plan named and found none of
them in what the Executor wrote.

The overclaim that *is* present sits one level up, in the frozen amendment's
residual R3, and the batch's own numbers refute it: STAGE 3B is a bitwise
re-execution of EXP-ECDLP-6ac801's production arm, not a third independent
angle. The claim survives my attack on cost and scope. It does not yet have the
independent corroboration the contract said this batch would supply.
