# BATCH-022 OPENING — RT048-CTRL-1: HEUR-DS-1 ON THE CORRECT OBJECT

- Goal: `GOAL-ECDLP-001` (active) — Sub-goal `SG-ECDLP-001`
- **New** experiment: `EXP-SMTH-001` — **new** hypothesis: `H-SMTH-001` (status `specified`)
- Run to be executed (gated): `RUN-SMTH-001-heur`
- Opened by: `DEC-20260801-006`, executing the single `next_action` recorded at the
  BATCH-021 close (`DEC-20260801-005`), which ranked `RT048-CTRL-1` first
- Queue: `coordination/goals/GOAL-ECDLP-001/batches/BATCH-022/dispatch_queue.json`
- Tasks: `TASK-20260801-010` … `TASK-20260801-018`, `max_concurrent` 3
- Declared close records: `EV-SMTH-001`, `DEC-20260801-007` (both subject to a
  mandatory freshness re-check at `TASK-20260801-018`)

## Why this batch is different from the previous twenty-one

Every real arm in the `EXP-DS-001` series ran with `smoothness_abort=false`. So
`is_B_smooth` has **never been called**, anywhere in the series, on any arm or any
object, and the smoothness claw the lane exists to study has never executed. The one
HEUR sampling ever performed (EV-DS-002 finding F3) sampled the **wrong quantity** —
an identity-encoded curve x-coordinate below 2^20 rather than a half-arity Semaev
intermediate bounded by D = 2^40, a factor of about 2^20 apart (RT047-H2, RT048-H1).

**This would be the first experiment in the program that tests the mechanism
H-DS-001 is actually about.**

## What BATCH-022 measures

At the frozen toy cells `bits ∈ {16, 20}`, `m = 4`, over a frozen deterministic
factor base of **512** x-coordinates of E(F_p):

1. Compute the **genuine half-arity Semaev partial-map intermediate** under the frozen
   map `INT-1` — specialize S_3(x_i, x_j, Z), take the elementary symmetric functions
   (e_1, e_2) of its root multiset (a *complete* invariant of the map's image), and
   encode them as an integer in [1, p²] by the bijection `ENC-B`.
2. Do this **exhaustively** over all C(513, 2) = **131 328** unordered half-tuples —
   above the frozen 10^5 minimum, with **no sampling seed and no sampling noise**.
3. Record the **largest prime factor** and the **B-smoothness indicator** of every
   sample, at every rung of a frozen smoothness ladder.
4. Compare the empirical CDF against **Dickman ρ(u)** under EXP-DS-001's
   **already-frozen** KS, rate-band and tail thresholds — reused verbatim, not
   redrafted.
5. Run the **identical** measurement on **uniform random integers on the matched
   range [1, p²]** — the mandatory null object.
6. Sweep **u over [2, 6]** so the required u^(−u(1+o(1))) decay is directly testable.

No search. No timing. No cost identity. No R. **This is a distributional measurement,
not a cost measurement.**

### Why a new EXP id was mandatory

The measurement needs summation-polynomial arithmetic, which
`CTRL-RT047-MATCHED-NULL.budget.new_dependencies` **forbids inside the EXP-DS-001
lane**. Filing this as a control there would breach a frozen clause. No EXP-DS-001
specification, control, amendment, driver, run package or result is read-modified,
edited or staged by this batch.

## Expressly forbidden anti-pattern (AP-1)

> **Do NOT set `smoothness_abort = true` on the existing EXP-DS-001 arms and call the
> mechanism exercised.**

At those parameters that calls `is_B_smooth` on an identity-encoded x-coordinate below
2^20 with B = 64 — a **stand-in**, not the Semaev intermediate bounded by D = 2^40 —
and would produce a false *"mechanism exercised"* tick on the ledger **while testing
nothing**. If it is ever run it is labelled a **plumbing check**, it produces no
evidence record, and it discharges nothing. Written into the contract, the hypothesis
and the Executor handoff.

## The BATCH-021 lesson, applied: **attainability**

BATCH-021's disposition map was verified **exhaustive** by an independent reviewer and
was applied honestly. It was never checked for **attainability**, and its favourable
branch **D-2 was arithmetically unreachable**: `split_search` caps per-target
enumeration at C(129, 2) = 8256, forcing U ≤ 0.4706 for any succeeding split arm, so
U ≥ 0.9 could never have fired **on any object**, including one with the strongest
imaginable Semaev structure. *The experiment could not have confirmed the hypothesis
even had it been true.*

Exhaustiveness is necessary and is **not sufficient**. So this batch freezes an
**attainability argument** (`ATTAIN-RR-SMTH-1`) alongside the reading rule, and makes
checking it an **explicit, named duty** of `TASK-20260801-012` — with its own
deliverable file, `attainability_check.md`, and its own line in the approval gate.

**It has already changed the design, before any review:**

- **The factor base had to move to Bfb = 512.** Distinct half-tuples number
  C(Bfb+1, 2) — that is 2080 at Bfb = 64, 8256 at 128, 32 896 at 256, **every one below
  the frozen 10^5 minimum**. At any EXP-DS-001 factor-base size the required sample
  count is reachable only by drawing with replacement from a support of ≤ 32 896
  values, whose discretization would dominate the KS statistic and force a failure for
  a reason having nothing to do with Semaev structure. This is arithmetically the
  **same shape of defect** as the C(129, 2) cap — caught this time *before* the freeze.
- **The u = 6 rung is underpowered** (2.58 expected smooth samples against the 30 the
  rate band needs), so it is **declared unattainable as a rate decision in advance**,
  excluded from RATE-DS-1, retained for the decay tell where its low-count noise is
  provably *conservative*, and it carries the sample size that would power it
  (n ≥ 1 526 718).

## The frozen reading rule `RR-SMTH-1`

Precedence: **M-0 → M-5 → M-1 → exactly one of {M-2, M-4, M-6}.**

| Branch | Condition | Disposition |
|---|---|---|
| **M-0** INTEGRITY GUARD | short sample set; sample outside [1, p²]; factorization mismatch; primality failure; undeclared degenerate rate > 1%; INT-1 irreproducible; timeout/crash/exhaustion | **Map SUSPENDED.** Infrastructure signal, never a mathematical result (AGENTS.md r5). |
| **M-5** APPARATUS FAILURE | (a) the **null itself** fails its Dickman checks; (b) the **ENC-A power certificate fails to reject**; (c) the apparatus-identity control **rejects** | **Map SUSPENDED.** Instrument failure; no disposition on the heuristic in either direction. |
| **M-1** STAND-IN TELL | `DECAY-1` fires on the real sample at either bit size | **`inconclusive`** + a *positive* instrument finding: the sampled quantity is not behaving like an integer of size D. Repair INT-1. **Not** a refutation. |
| **M-2** CONSISTENT | at **both** bit sizes: KS pass ∧ TAIL pass ∧ RATE pass at every powered u ∈ {2,3,4,5} ∧ two-sample KS does not reject | **`replicate`.** Explicitly **not** `support`, not validation above toy, not S1_met, no gate movement. |
| **M-4** DEVIATION | at **both** bit sizes the M-2 conjunction fails, with the null passing and the power certificate rejecting | **`weaken`**, scoped to INT-1/ENC-B/the two field sizes/Bfb=512/m=4/the frozen ladder. Refutation artifact archived **first**; `status_scope` block mandatory (RT048-B5). **Never `reject_scoped`.** |
| **M-6** SPLIT | exactly one bit size satisfies M-2 | **`inconclusive`.** No post-hoc label; the passing cell may not be reported alone. |

Exhaustive: given no M-0/M-5/M-1, each cell passes or fails → both / neither /
exactly one → M-2 / M-4 / M-6. No gap, no room for a post-hoc reading.

### Attainability, branch by branch (summary — full argument in the contract)

- **M-0**, **M-5** — reachable by concrete achievable implementations (a wall-clock
  stop; a log-base-2 ρ evaluation; an ENC-A that collapses to ENC-B; an off-by-one in
  the base-p concatenation).
- **M-1** — reachable, **by a measurement this program actually produced**: the
  BATCH-020 stand-in gives a ratio of 0.0527 against the 0.006404 threshold, a factor
  8.2 over. A genuine sample sits a factor **100 under** it.
- **M-2** — **its reachability is demonstrated inside the same run by the null arm**,
  which travels the identical code path and produces an M-2-pattern measurement. It is
  impossible for the M-2 pattern to be unreachable while the null is admissible. This
  is the precise repair of BATCH-021's D-2.
- **M-4** — reachable by an achievable configuration of the frozen design (a bias
  concentrating e_2 on a density-½ set displaces the CDF by up to 0.25, **39×** the
  two-sample threshold). No cap and no closed form bounds the statistic away from its
  rejection region.
- **M-6** — reachable for a stated physical reason: the factor base covers ≈0.78 % of
  F_p at bits 16 and ≈0.049 % at bits 20, a factor-16 density difference.

## Every decision variable was checked for **variation**

EV-DS-004 N-2 / RT048-B1 recorded that the previous lane's charged-unit proxy was a
**closed form in the protocol's own matched parameters** — a constant 40 units per
enumeration, so the ratio was exactly the enumeration-count ratio with the
**object-free** expectation 2/129. The object cancelled.

Here: **ENC-B is a bijection** [0,p) × [0,p) → [1, p²], and the null is drawn uniformly
on that same [1, p²]. So the real sample deviates **iff** the joint law of the two
elementary symmetric functions of the half-arity Semaev partial map departs from
uniform — *a property of the Semaev map alone, containing no free parameter of the
protocol.* Two variables **are** degenerate by construction; both are **declared** and
confined to roles the degeneracy does not spoil — the ENC-A power certificate (used
only to certify that the statistic *can* reject) and the apparatus-identity control
(whose agreement is expressly declared **not** to be corroboration).

## Two defects carried as declared open items

- **OPEN-BATCH022-A** — `tools/validate_ledger.py` indexes runs only from
  `manifest.yaml`, but **both** EXP-DS-001 control runs emit `manifest.json`, exactly
  as their frozen contracts specified. So `EV-DS-003` and `EV-DS-004` are both reported
  as *"evidence references unknown run"* — for runs that exist and were
  certificate-verified 1200/1200 by two independent sessions. Repo-wide the convention
  is `manifest.yaml` (≈1462 files vs ≈17 json) and the same experiment's three earlier
  runs follow it. **Ruling: EXP-SMTH-001 specifies `manifest.yaml`** so it does not
  inherit the defect — and consequently the exact companion filenames `check_run`
  demands: `command.txt`, `environment.json`, `stdout.log`, `stderr.log`,
  `raw-result.json` (note **`.log`**, not `.txt`). This **repairs nothing** in
  EXP-DS-001 and is not a repair of it; those artifacts are immutable. Both candidate
  repairs and all forbidden repairs are named in `DEC-20260801-006`.
- **OPEN-BATCH022-B** — the recurring **same-date DEC-id collision** with `origin/main`,
  now **four** occurrences. Mitigated (declared id + mandatory freshness re-check +
  renumber *our* record, never theirs), **not fixed**; two candidate repairs named.

## Forbidden in BATCH-022

- `S1_met`, `F1_met`, `F2_met`, `structure_gate_passed` — under **every** branch (this
  batch runs no search and cannot evaluate them)
- `support` for `H-SMTH-001`, for `H-DS-001`, or for HEUR-DS-1
- any movement of asymptotic promotion gates **G1–G4**, which remain **OPEN**
- any asymptotic, crypto-scale, medium-scale or affected-scheme claim
- `reject_scoped`, and in particular reject_scoped-as-impossibility
- `dominated_by: null` anywhere downstream
- altering `H-DS-001`, `H-IC-001` or `H-STR-002`; re-scoring `EV-DS-001`…`EV-DS-004`
- editing, read-modifying or staging **any** file under `experiments/EXP-DS-001/`
- touching FAEST or XEDN
- the AP-1 flag-flip anti-pattern

## Ranked backlog carried, not dropped

`RT048-CTRL-3` (the B-sweep at Bfb ∈ {32, 64, 128, 256} on both objects, whose generic
prediction is now exact at U = 1/(Bfb + 0.5)) and `RT048-CTRL-4` (replication at a
second seed) remain D-1's mandatory companions and are ranked **behind** this batch's
work. If BATCH-022 closes without reaching them they are re-ranked into BATCH-023 and
the carry-forward is recorded.

## Budget

`campaign_budget.maximum_batches` is **50**; BATCH-022 is the **twenty-second** batch.
**No pause condition fires.** Stated explicitly rather than left implicit. Goal status
is and remains `active`.
