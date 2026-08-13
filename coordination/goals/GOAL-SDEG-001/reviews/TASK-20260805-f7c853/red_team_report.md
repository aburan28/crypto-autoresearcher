# Red Team report — EXP-SDEG-f7faa8 (frozen contract, status `review_required`)

Snapshot reviewed: commit `07c43118` on `claude/ssi-ecdlp-experiments-4cwbrq`,
worktree clean at review time. This report is an objection set. It changes no
record and asserts no research status.

---

## 0. What I did

I re-derived the entire frozen closed form Φ from clauses (1)–(9) of
`H-SDEG-0dd021` independently, in Python, without reading the Coordinator's
arithmetic, and then evaluated all three frozen candidates at all four gate
cells and at the reported arm-R cell CELL-E.

**The baseline-reproduction audit is genuine.** Clauses (2)–(4) reproduce,
exactly: `sr_pred(9,3..6) = 180 / 1,674 / 9,504 / 28,068`; `HF(9) =
[1,18,144,645,1566,738,0]` with frozen quotient `3,112` and `phi_full(9)=6`;
`sr_pred(12,3..6) = 312 / 3,834 / 29,418 / 156,520`; `N(24,6)=190,051`;
`nrows(9,6)=45,324`; `nrows(12,6)=183,312`; `nrows(12,5)=31,512`;
`h_6(12)=7,494`; `phi_full(12)=7`; `N(28,6)=499,178`; `nrows(13,6)=361,933`.
I confirm every one. The skeleton is not fitted and the audit was not
overstated. **That is the strongest thing in this package and I do not dispute
it.** Everything below is about what the gate built on top of it can and
cannot establish.

**The gate, computed:**

| | CELL-A / G1 (arm R, n=12 D6, target 7,110 ±5%) | CELL-B / G2 (arm P, n=12 D6, target exactly 0) | CELL-C / G3 (n=9 D6, target exactly 31,179) | CELL-D / G5 (arm R, n=12 D5, target exactly 0) |
|---|---|---|---|---|
| **C1** HARD_FREEZE | rank 147,996, deficit **8,524**, +19.9% → **FAIL** | 156,520 → PASS | declared arm P: 28,068 → FAIL. arm R: 28,068 → FAIL | 29,418, deficit 0 → PASS |
| **C2** SIGNED_CARRY | rank 156,520, deficit **0**, −100% → **FAIL** | 156,520 → PASS | declared arm P: 28,068 → FAIL. arm R: 31,179 → PASS | 29,418, deficit 0 → PASS |
| **C3** VARIETY_COLLAPSE | rank 174,031, deficit **−17,511**, +346% → **FAIL** | 156,520 → PASS | declared arm P: 28,068 → FAIL. arm R: 31,179 → PASS | 29,418, deficit 0 → PASS |

Intermediate quantities, for independent recomputation:
`s = [1, 24, 264, 1724, 7104, 16920, −8524]`, `phi_F(12,6) = 6`,
`A = 174,033`, `Σ_{k<6} s_k = 26,037`, `Σ_{k≤6} s_k = 17,513`, `|V| = 2`.
At CELL-D: `s = [1, 24, 264, 1724, 7104, 8174]`, `phi_F = 6 > D = 5`,
`A = 46,709`.

**F1 fires. No candidate passes.** And it fires for a reason that was
computable before the contract was frozen.

---

## Objections

### OBJ-1 — The four-gate instrument is a one-number test. G2 and G5 are model tautologies, not measurements. **BLOCKING**

Two of the four gates cannot discriminate between candidates and cannot fail
for any member of the family:

- **G2 is candidate-independent by construction.** Arm P's rule (clause 7)
  contains no `Q`; C1/C2/C3 differ *only* in `Q`. All three therefore return
  the identical number at CELL-B. Worse, the arm-P rule reduces to `sr_pred`
  whenever the projection loss `max(0, sr_pred + u_D − N)` vanishes, and here
  it vanishes with a slack of **17,515** — larger than the entire quantity
  under test. So G2 asks only "does Φ reproduce `sr_pred(12,6) = 156,520`?",
  which is CTRL-6 anchor #4, already reproduced before the contract was
  written. G2 carries zero information beyond the anchor set.
- **G5 is the identity `u_D` cancels.** At CELL-D, `phi_F = 6 > D = 5`, so no
  candidate freezes and all three collapse to `Q = Σ_{k≤D} s_k`, giving
  `rank = A − Σ s_k = N − Σ h_k = sr_pred` by the contract's own COROLLARY —
  which is an algebraic triviality (`A = N − u_D`, `s_D = h_D − u_D`, so `u_D`
  cancels). G5 tests that Φ satisfies a theorem Φ already proves.

The contract's own precedent record diagnoses exactly this failure mode:
EV-IC-002 OBS-5 records a criterion "satisfied whenever no instance falls
inside a two-group-operation window against a T_desc of roughly 32,000" and
concludes the reported pass "is an arithmetic consequence of its own
conditioning, not a measurement." CTRL-4 cites EV-IC-002 for a *different*
failure mode (post-hoc revision) while reproducing this one.

Net: after G3 (see OBJ-2), the gate's discriminating content is **one number,
three draws**. The contract presents "four gate conditions … three of them
exact, not banded" as if exactness were strength. Exactness on a tautology is
not strength; it is the appearance of strength. IR12 correctly requires
reporting "1 of 3 pre-declared candidates" — it should equally require
reporting "1 of 1 discriminating gate."

### OBJ-2 — G3 is arm-ambiguous, and the contract contradicts itself on which rule applies. **BLOCKING**

CELL-C is declared `arm: P (full support, u_6 = 0)`. Under the declared
arm-P rule the prediction is `sr_pred(9,6) = 28,068`, and G3 requires exactly
`31,179`. **G3 therefore fails for all three candidates, by exactly 3,111** —
which is precisely the "sr_pred overshoot 3,111 = 3,112 − 1 = frozen predicted
quotient minus |V|" that EV-SIG-006 already committed. Under arm-P, G3 is not a
test of Φ; it re-states an already-committed diagnosis and guarantees failure.

But the G3 metric text says "predicted rank at CELL-C, **per candidate**."
Candidate dependence exists *only* under arm R. So the metric presupposes
arm-R evaluation of a cell the inputs classify as arm P. Under arm R, C2 and C3
return `A − |V| = 31,179` and pass; C1 returns 28,068 and fails.

Whether G3 is a guaranteed fail-for-all or a 2-of-3 split therefore depends on
a choice the contract makes twice, differently, and never resolves. This is a
live degree of freedom inside a record that states "NO OTHER DEGREE OF FREEDOM
EXISTS" (assumptions, after clause 9). CTRL-9/IR6 do not save it: N0 is a
full-support generic null with **no columns deleted from anything**, so it is
neither "a full-support SYSTEM whose Macaulay columns are deleted afterwards"
(P) nor "a system whose EQUATION supports are constrained" (R). The taxonomy
has no cell for it, and the Stage-1 evaluator must choose after seeing that one
choice fails and the other passes. That is the EV-IC-002 pattern the contract
was explicitly built to avoid.

### OBJ-3 — `coordinator_prior_disclosure` determines the entire gate verdict. The "pre-declared candidate" framing is retrodiction. **BLOCKING as framing; NON-BLOCKING as concealment (there is none)**

Answer to the direct question: **YES**, and more strongly than asked. The
disclosure does not merely identify a winner — it settles that there is none.
From `s_6 = −8,524`, "phi_F pulled 7→6", and numbers already committed:

- **C1** `deficit = sr_pred − (A − Σ_{k<phi_F} s_k) = −s_6 = 8,524`. One line
  from the disclosure alone, via the contract's own COROLLARY. `|8,524 −
  7,110|/7,110 = 19.9% > 5%` → FAIL.
- **C2** `Σ_{k≤6} s_k = A − sr_pred = 174,033 − 156,520 = 17,513 > |V| = 2`, so
  `rank = sr_pred`, `deficit = 0` → FAIL. Needs no disclosure at all — two
  committed numbers.
- **C3** `D = 6 ≥ phi_F = 6` (which is exactly what the disclosure states) →
  `rank = A − |V| = 174,031`, `deficit = −17,511` → FAIL.

So the record that freezes the candidate list also contains the quantity that
evaluates every member of it. The disclosure is honest and I credit it — the
Coordinator wrote "makes each candidate's G1 prediction computable in one line
by any reader" and recorded a prior of failure. But having done so, the
epistemic property that "frozen before evaluation" is supposed to buy is gone.
Pre-registration protects against choosing a criterion after seeing an outcome;
it does not protect when the outcome is a deterministic function of information
in the pre-registration itself. Whether the author actually carried out the
arithmetic is unverifiable and *irrelevant*: the information content of the
freeze is what matters, not introspection.

The consequence for the deliverable is specific. Stage 1 is not an experiment;
it is a derivation the record already contains. Calling it a "gate",
"falsification", "decidable with a reachable negative", and budgeting three
runs and 1,800 s for it charges a documentation task as a test. The honest
framing: **"the frozen family is refuted by a one-line consequence of the
disclosed `s_6`; here is the named no-go."** That deliverable is worth having.
The gate ceremony around it is not.

### OBJ-4 — The gate is unpassable by *any* truncation convention, not just these three. F1 was structurally guaranteed. **BLOCKING as scope of the negative; STRENGTHENS the negative**

G1's band on the deficit maps to a band on `Q = A − rank` of
**[24,267.5, 24,978.5]** (width 711, i.e. ±1.44% of the required `Q = 24,623`).
The complete lattice of `Q` values reachable from partial sums of the model's
own series, plus `|V|` and 0, is:

`{0, 1, 2, 25, 289, 2013, 9117, 17513, 26037}`

**None lies in the band, and the nearest (26,037) misses the band edge by
1,058.5.** The measured `24,623` is not a partial sum of the model's series and
is not within one window-width of one. So the refutation is broader than "three
candidates failed": no single-valued, parameter-free collapse convention built
from partial sums of `S_{n,F}` can pass G1 at this cell. That is a real,
useful, and stronger negative than the contract claims — and the BRANCH
NEGATIVE deliverable (b) should state it in this form rather than as "three
canonical collapse conventions."

The other side of the same coin: the contract's `success_criterion` opens
"DECIDABLE, WITH A REACHABLE NEGATIVE … neither is a failure." The accurate
statement is **determined, with an unreachable positive.** BRANCH POSITIVE is
not reachable by any member of the frozen list. A contract that lists two
branches, one of which is arithmetically impossible, should say so.

### OBJ-5 — `u_5 = 8,746` is presented as `committed` and is not committed anywhere. Clause (6)'s per-cell precondition is undischargeable at CELL-D. **NON-BLOCKING, must-fix**

I searched the ledger, the SIG-008 artifacts, the SIG-006 artifacts and the
DREG batch tree. The string `8746` occurs in exactly one place in this
repository: `ledger/hypotheses/H-SDEG-0dd021.yaml:486` — the record under
review. It is a Coordinator derivation, `N(24,5) − 46,709 = 8,746`, resting on
the unverified assumption that the whole D5 deficiency sits at degree 5.

CELL-D's block labels it `committed:`. It is not. Compare CELL-A, where
`u_6 = 16,018` *is* recoverable from a committed histogram
(`1/24/276/2,024/10,626/42,504/118,578`, in EV-SIG-008 and in
`experiments/EXP-SIG-008/runs/RUN-EXP-SIG-008-a/raw.json`) — that one is fine.
The n=12 **D5** degree histogram exists in no committed record.

This matters beyond labelling. Clause (6) states `s_k = h_k for k<D` and
`s_D = h_D − u_D` hold "whenever `u_k = 0` for `k < D` (verified at every
committed cell; **VERIFIED PER CELL, never assumed**)". At CELL-D that
verification cannot be performed from committed data at zero compute. The
contract asserts an obligation it cannot discharge at one of its four gate
cells. (It does not change the verdict — all three candidates return `sr_pred`
at CELL-D under either reading — but a frozen contract that elsewhere insists
"THE COMMITTED NUMBERS ARE READ AS-IS" must not label a derivation as
committed. AGENTS rule 9.)

### OBJ-6 — CELL-A's provenance is misdescribed in *both* directions. **NON-BLOCKING, must-fix**

The contract says the 7,110 figures "survive via the live transcript and git
branch `exp-sig-008-artifacts` commit `d1d36dd`."

- `d1d36dd` is **not reachable from this repository** (`git rev-parse` fails;
  no such branch). The contract cites an unresolvable commit as the durable
  record of its most load-bearing number.
- Meanwhile a committed, in-tree, machine-readable artifact exists and the
  contract does not cite it:
  `experiments/EXP-SIG-008/runs/RUN-EXP-SIG-008-n/raw.json`, present in
  snapshot `07c43118`, recording `n:12, seed:2, nrows:183312, ncols:174033,
  sr_pred:156520, rank:149410, deficit:7110, extra:7110, rankK6:26792,
  rank_eq_sr_pred:false, done:true`, with
  `instrument_sha256.semaev_tree.py = e9f1681b4e…becef`,
  `instrument_sha256_matches_pinned: true`, `git_commit f6fa31b0…` (reachable),
  and `secs_total: 1182`.

So the honest statement is *narrower and stronger* than the contract's: the
7,110 anchor has a committed raw result and a pinned builder hash; what it
lacks is a `manifest.yaml`, which is why `check_run` rejects it — a
**registration defect, not an evidentiary void**, exactly as EV-SIG-008's own
`consequence` field says ("a schema-generation problem rather than missing
evidence"). Both the hypothesis's `PROVENANCE ASYMMETRY` clause and CELL-A's
`provenance_caveat` overstate the absence while citing an unreachable commit.

**Is that acceptable?** For Stage 1, yes with the correction above, for one
reason I verified rather than assumed: the provenance problem is **not
load-bearing for the verdict.** For C1 to pass G1 the true rank would have to
be wrong by ≥ 1,058.5 (0.7% of 149,410) in the favourable direction. The
committed receipt reports 11 chunk units whose per-unit pivot yields sum
exactly to 149,410 and `cols_fraction: 1`. Re-measurement will not rescue any
candidate. IR11 already forbids citing the destroyed receipts as a
reproduction, and that is the right rule.

For anything beyond Stage 1, no. And note the cost, which the contract has
mischarged: `secs_total: 1182` for the original CELL-A measurement — **less
than Stage 1's own declared 1,800 s wall-clock budget.** The contract defers
re-measurement of its weakest anchor to a Stage 2 that is not authorized, when
the receipt says the cell is a ~20-minute job (memory ~7 GB, so it needs
Stage-2's memory cap, not its time budget). Treating a 20-minute re-measurement
as out of reach while calling the same anchor "the WEAKEST PROVENANCE IN THE
GATE" is an uncharged cheapness.

### OBJ-7 — The best-provenanced arm-R cell is demoted to non-gating while the worst-provenanced one gates. **NON-BLOCKING, but it costs the contract its strongest available negative**

CELL-E (EV-SIG-006 N1, n=9, D6, arm R, `A=29,332`, `|V|=0`, measured rank
28,939) is:

- **the same arm as CELL-A** (its equation supports were constructed);
- from a run that *does* register — EV-SIG-006 states all six cited run IDs
  resolve to committed manifests, unlike every EV-SIG-008 run;
- **already discriminating**. I computed: `u_6 = 1,848`, `s_6 = −9,945`,
  `phi_F = 6`. C1 → 26,220 (miss −2,719, and predicts deficit **+1,848**
  against a measured **−871**: wrong sign); C2 → 29,332 (miss +393, deficit
  −1,264 vs −871, i.e. 45% off); C3 → 29,332 (identical).

So the entire family is *also* refuted at n=9, on the right arm, on a
registrable receipt, at zero compute — independently of the 7,110 provenance
question and independently of the G3 arm ambiguity.

The stated reason for demotion (D4/CORR-20260805-9d2e17: EV-SIG-006's blanket
*inference* is contradicted by its own N1 *observation*) is a good reason to
distrust the inference and no reason at all to distrust the measurement. The
net effect of the selection is that the gate's known-shape control is the cell
Φ's two surviving candidates can hit, and the same-n, same-D, same-arm,
better-provenanced cell they miss is non-gating. I am not alleging intent; I am
recording that the choice runs in the model's favour and that reversing it
strengthens the negative at zero cost.

### OBJ-8 — Stage 2 is a lane that will consume the budget and return an infrastructure/coverage outcome at n≥13. The budget block is internally inconsistent by 2.4×. **BLOCKING for any Stage-2 authorization; NON-BLOCKING for Stage 1**

Charged against the one measured precedent (TASK-20260731-016: n=12 D6,
`chunk_force 12000`, 15 units, `secs_total 1,623.8 s`, `peak_rss 7.16 GB`),
scaling elimination work as `rows × cols × min(rows,cols)`:

| n | D | ncols | nrows | est. instrument-s | carrier bits | projected peak RSS |
|---|---|---|---|---|---|---|
| 9 | 6 | 31,180 | 45,324 | 11 | — | — |
| 10 | 6 | 110,056 | 109,030 | 333 | — | — |
| 11 | 6 | 145,499 | 142,461 | 751 | — | — |
| 12 | 6 | 190,051 | 183,312 | **1,624 (measured)** | 3.34 GB | **7.16 GB (measured)** |
| 13 | 6 | 499,178 | 361,933 | **16,626 (≈4.6 h)** | 13.50 GB | **≈28.9 GB** |
| 14 | 6 | 621,616 | 447,034 | 31,585 (≈8.8 h) | ≥23.26 GB | ≥49.9 GB |

(Carrier = `nrows × rank_acc` bits, the dominant resident object in the chunked
block-m4ri instrument; calibrated at the measured 2.14× RSS-over-carrier factor
at n=12. Rank at n=13 taken as `sr_pred(13,6) = 320,359`, which I computed from
Φ; it is an upper estimate. The whole table is a **model**, marked UNVERIFIED —
no off-lattice cell of this lineage has ever been built, as the contract's own
`blocking_nulls` concedes.)

Consequences:

1. **n=13 D6 exceeds the declared 24 GB memory cap** (≈28.9 GB projected).
   Not "expensive" — out of budget on the memory axis, before the time axis is
   consulted. n=14 is ≈50 GB and should not be in the record at all.
2. **The declared ladder is 2.7× oversubscribed.** n∈{9..13} × D∈{5,6} × 2 arms
   × 2 seeds = 40 cells ≈ **77,833 s ≈ 21.6 h** against a 28,800 s ceiling. The
   n=13 rung alone (8 cells) is ≈66,857 s = **2.3× the entire ceiling.**
3. **The budget block contradicts itself.** `stage2: maximum_runs 117 ×
   wall_clock_seconds_per_run 600 = 70,200 s` vs `wall_clock_seconds_ceiling
   28,800 s` (2.4× over); top-level `maximum_runs 120 × 600 = 20 cpu-h` vs
   `total_cpu_hours 8.5` (2.4× over). One of the two numbers in each pair is
   decorative.
4. **SR3 forces ≥28 chunked invocations for the single n=13 D6 cell** at the
   measured rate. EV-DREG-004's precedent is a 33-invocation chunked lineage
   across five sessions destroyed at 24.93% of columns, with a measured
   carrier-codec bottleneck (198.6 s unpickle per 44 blocks vs 0.7 s projected
   raw). The contract inherits the chunking discipline and IR1/IR4 correctly,
   but inherits nothing that changes the arithmetic: the n=13 cell is *larger*
   than the destroyed n=21 D5 cell on the carrier axis.

**The core is survivable.** n∈{9,12} × D∈{5,6} × 2 arms × 2 seeds ≈ **6,597 s =
23% of the ceiling.** So the correct scoping is core-only. Declaring a ladder
that SR4 will amputate at its first two rungs inflates the apparent reach of
the contract; SR4 is written as a graceful-degradation rule but is in fact the
expected path, and the record should say so up front rather than in a stopping
rule.

### OBJ-9 — "one instrument lineage" is two rank engines. **NON-BLOCKING**

`H-SDEG-0dd021.statement` and `scale_relevance` both claim "one instrument
lineage." CELL-A and CELL-D come from `SIG8_run.sage` (Sage 10.9, Python
3.14.3, macOS arm64, `instrument_sha256` block); CELL-B comes from
`src/h012c_block_m4ri.py` (chunked block-m4ri). Two different exact-rank
engines. The *builder* may well be shared — `semaev_tree.py` hashes to
`e9f1681b…becef` identically in `src/`, `EXP-SIG-001/002/005/008` — but the
SIG-008 receipt pins the builder and the DREG receipt does not (see OBJ-10).
CTRL-5 exists precisely because two elimination orders can disagree; two
engines is a stronger version of the same risk and should be named as such.

### OBJ-10 — The Stage-1 builder-identity check is guaranteed inconclusive as scoped, and the 138,570/138,573 pair cannot test HEUR-BF-1 as formally stated. **NON-BLOCKING**

The contract requires Stage 1 to verify "FROM THE COMMITTED SYSTEM HASHES AND
BUILDER PATHS" that CELL-H and CELL-B were built by the same builder. From
committed artifacts:

- SIG side (`RUN-EXP-SIG-008-n/raw.json`): builder hash `semaev_tree.py =
  e9f1681b…`, `instrument_sha256_matches_pinned: true`. **No system hash.**
- DREG side (TASK-20260731-016): `system_hashes.null = f2f61073…`,
  `system_hashes.sem = c47d17c3…`, `instrument.path =
  src/h012c_block_m4ri.py`. **No builder hash.**

The two sides record disjoint identity evidence. Builder identity is therefore
**not establishable at zero compute in either direction**, and the required
artifact `builder_identity_check.json` will read "inconclusive." The contract
permits that outcome, which is correct, but then has no route to resolving it —
and the resolution is a ~1-minute rebuild (see the cheapest control below).

On attack 4's substance: **a 2-column ncols difference is fully consistent with
a seed difference and does not prove two builders.** The D6 column set is the
up-closure of the *equation supports*, and the equations are seed-drawn, so the
support size is seed-dependent by construction — EV-SIG-006 records exactly
this size-dependence within one builder. Both lineages agree on the structural
facts that a builder change would most likely break: deg≤5 complete
(`55,455`), all deficiency at degree 6, and `ncols + u_6 = 190,051 = N(24,6)`
on both sides (174,033+16,018 and 174,035+16,016). So the pair is *evidence
for* a common convention, not against it.

But the pair **cannot test HEUR-BF-1 as formally stated.** HEUR-BF-1
quantifies over seeds "at fixed support data"; these two cells have different
support data (174,033 vs 174,035). The antecedent fails, so the comparison is
not a controlled seed experiment at all. The hypothesis record concedes the
general point ("the 'fixed support' antecedent is not automatically satisfiable
across seeds") and the contract nonetheless calls the pair "a live,
unexploited datum bearing directly on HEUR-BF-1." It does not bear on it. A
3-in-138,570 rank difference across two different column sets, two rank
engines, and two experiments is uninterpretable in every direction, and the
correct Stage-1 disposition is to say so rather than to record it as a spread
*or* as inconclusive-pending-builder-check.

What else is incomparable across the two lineages, if builder identity is not
established: every cross-lineage statement in the contract — CTRL-3's
"difference between the arms" at n=12 (CELL-A from SIG, CELL-B from DREG), the
`rankK_D = nrows − sr_pred` identity in clause (9) (verified only on the SIG
side), and the entire F6 confound disposition, which is *about* this
incomparability and is therefore not a fallback but the leading hypothesis.

### OBJ-11 — Four sentences could be cited as though a boolean d_reg model transferred. **NON-BLOCKING, must-fix wording**

The scope discipline in both records is unusually good — `asymptotic_claim:
null`, `corollaries: DELIBERATELY EMPTY`, `sota_delta` zero on every attack
axis, `dominated_by` correctly marked not-applicable because no Pareto point is
claimed (that `null` is *not* a rule-5 fabrication here, and I checked), and an
explicit "KN-OPEN-002 IS NOT CLOSED, NARROWED, OR ADVANCED." I found no
overclaim in the conclusions. I did find four unqualified sentences that a
downstream citation could carry across the boolean/prime-field gap:

1. `proof_search_map.bottleneck`: "every d_reg-derived cost prediction at D ≥ 6
   is measured against it" — unqualified by "boolean".
2. `asymptotic_claim_note` and `interpretation_limits[0]`: "A validated Φ makes
   existing d_reg predictions usable" — unqualified, twice.
3. `objective`, `success_criterion` branch NEGATIVE (c), and `F7`: "which
   (n, D) ranges make **d_reg-derived cost predictions** unusable" — three
   occurrences, none saying "boolean chained-Semaev".
4. `proof_search_map.bottleneck`: "Repairing or **condemning** this one step is
   upstream of GOAL-SDEG-001, GOAL-SIG-001 and GOAL-DREG-001."

Item 4 is also substantively wrong (see OBJ-12). The transfer risk in items 1–3
is concrete because the negative is explicitly routed to
`IDEA-20260803-fa9839`, whose subject is prime-field point-decomposition index
calculus with `D_trial = N^d` and a threshold `d < (m−3)/4` — a
crypto-relevant comparison. The routing label "NOT-THRESHOLD-CONVERTIBLE" is
itself safe (it asserts non-transfer), but it creates the citation path, and
along that path a sentence reading "d_reg-derived cost predictions are unusable
at D ≥ 6" has no boolean qualifier attached. Add "boolean chained-Semaev
(t=3, n≤14, GF(2))" at all six occurrences. Also note the pinned instrument is
literally named `dreg_crypto_cost_model.py`, which shortens that path by one
step.

### OBJ-12 — "Unblocks SDEG/DREG/SIG" is rhetorical: neither branch changes any goal's `next_action`. **NON-BLOCKING**

I checked all three goal records at the snapshot.

- **GOAL-SDEG-001** `next_action`: "Defer activation/executor until ECDLP
  verifier-hash and precommit residuals clear under a separate ledger
  authorization; **no runs now**." A Stage-1 PASS makes Stage 2 "eligible for a
  separate Coordinator ledger authorization" (SR1) — i.e. eligible for the very
  authorization the goal is already waiting on for unrelated reasons. Unchanged
  either way.
- **GOAL-SIG-001** `next_action`: "Defer calibration executor until campaign
  capacity prioritizes D≥6 null recalibration." Its completion criterion does
  admit "**or a scoped instrument no-go**", so a sufficiently strong negative
  is a real route. But *this* negative is not that: the contract itself states
  "A Stage-1 FAIL … does NOT establish that no closed form exists." It refutes
  one three-member model family. GOAL-SIG-001 still lacks a valid D≥6 null
  baseline afterwards, exactly as before.
- **GOAL-DREG-001** `next_action` is about EXP-DREG-004 n=21 archival and
  BATCH-004 CTRL-B; its completion criterion requires the on-lattice ladder at
  n∈{12,15,18} with ≥3 seeds. Nothing in Stage 1 touches it. Note n=15 and n=18
  are outside this contract's declared boundary entirely, so even a completed
  Stage 2 would not feed DREG's criterion.

And item 4 of OBJ-11 is wrong on its own terms: a Stage-1 FAIL **condemns a
proposed repair of `sr_pred`, not `sr_pred` itself.** After F1 fires, `sr_pred`
is exactly as calibrated or as broken as it was before. "Condemning this one
step" is not among the reachable outcomes.

What Stage 1 *does* produce, honestly stated: a documented dead end for one
model family, plus (if OBJ-4 is adopted) a sharper statement that the whole
partial-sum-convention class is dead at this cell. That is a knowledge artifact
worth committing. It is not an unblock, and the justification should not be
written as one.

### OBJ-13 — No decay control. The contract never states what Φ's own mechanism predicts as n grows — which is the one cheap thing that would distinguish a mechanism from a coincidence at n=12. **NON-BLOCKING; this is the missing forward guidance**

Standing obligation (inventor protocol §3): name the parameter that is supposed
to destroy the signal and state what the measurement should do as it increases.
The contract does not, so I did.

Φ's mechanism is that the support restriction pulls `phi_F` below `phi_full`,
which requires `s_6 = h_6 − u_6 ≤ 0`. Computed:

| n | nb | h_6 | C(nb,6) | u_6 needed to freeze | as % of sextics | committed u_6 |
|---|---|---|---|---|---|---|
| 9 | 18 | −8,097 | 18,564 | 0 (already frozen) | 0.0% | 0 (N0) / 1,848 (N1) |
| 10 | 22 | 803 | 74,613 | 803 | 1.1% | not measured |
| 11 | 23 | 3,322 | 100,947 | 3,322 | 3.3% | not measured |
| 12 | 24 | 7,494 | 134,596 | 7,494 | 5.6% | **16,018 (11.9%)** |
| 13 | 28 | 106,743 | 376,740 | 106,743 | **28.3%** | not measured |
| 14 | 29 | 139,209 | 475,020 | 139,209 | 29.3% | not measured |

At the committed n=12 miss fraction of 11.9%, `s_6` at n=13 would be about
**+61,500 > 0**, so `phi_F = 7 > D = 6`, no freeze, and **all three candidates
predict deficit exactly 0 at n=13 D6 arm R.** The support miss fraction would
have to be 2.4× the n=12 value for any candidate to predict a defect there.

This is the decay control the contract is missing, and it is sharp in both
directions:
- If the n=13 D6 arm-R deficit is measured **nonzero**, the family dies again
  for a reason that has nothing to do with the collapse rule — the freeze
  mechanism itself is not what produces the defect.
- If it is **zero**, then the 7,110 below-freeze collapse is an n=12
  phenomenon, `phi_F` is not tracking it, and the correct object is whatever
  makes n=12 special — which the contract would then have to name.

It is also the cheapest way to see that the "below-freeze collapse" may be a
knife-edge: `h_6` jumps 7,494 → 106,743 between n=12 and n=13, a 14× step, so
the window in which `u_6` can exceed `h_6` at D=6 is essentially n∈{10,11,12}.
A quantity whose proposed mechanism is live at exactly one measured size is the
canonical artifact shape, and the contract should carry that as an explicit
alternative hypothesis rather than only as HEUR-BF-1 seed noise.

---

## Attack 1 — the computed prior

**The gate is effectively a one-number test with three draws, and the honest
answer is stronger than "1 in 3".**

Discriminating power by gate, computed above:

| gate | discriminates among C1/C2/C3? | can it fail for any candidate? |
|---|---|---|
| G2 | **no** — arm-P rule contains no `Q` | no — projection loss is 0 with slack 17,515 |
| G5 | **no** — `phi_F = 6 > D = 5`, all reduce to `Σ_{k≤D} s_k` | no — it is the identity `u_D` cancels |
| G3 | only under arm R (contract declares arm P) | under arm P: fails for all three, by 3,111 |
| G1 | **yes** | yes — and it does, for all three |

So: **one number, three draws, a ±5% window.**

Two ways to price "by chance", both crude and both labelled as models:

*(a) Continuous prior on the deficit scale.* The G1 window is 711 wide.
- uniform on the span of the family's own outputs `[−17,511, +8,524]` (width
  26,035): **2.73% per candidate, 7.97% for at least one of three** (3.65 bits
  of evidence had a pass occurred);
- uniform on `[0, |s_6|] = [0, 8,524]`, the below-freeze mass — the natural
  scale for a defect of this mechanism: **8.34% per candidate, 23.0% for three**
  (2.12 bits);
- uniform on `[0, A − sr_pred] = [0, 17,513]`, the largest in-model quotient:
  **4.06% per candidate, 11.7% for three** (3.10 bits).

So a pass, had one occurred, would have been between a **1-in-12 and a 1-in-4
coincidence: 2.1 to 3.7 bits.** Against that the contract offers "four gate
conditions, three exact" and "seven predictions frozen." Those descriptions and
that number are not compatible.

*(b) The correct discrete answer, which supersedes (a).* The candidates are not
random draws; their outputs live on a lattice. The reachable `Q` values are
`{0, 1, 2, 25, 289, 2,013, 9,117, 17,513, 26,037}` and the required band is
`[24,267.5, 24,978.5]`. **Zero of nine lattice points fall in the band; the
nearest misses by 1,058.5, which is 1.5× the entire window width.** So

> **P(a random one of the three passes G1) = 0, exactly, and P(any
> partial-sum convention passes) = 0 as well.**

**Blunt version, as requested:** yes — this is a one-number test with three
draws at a ~1.4%-of-`Q` window, and it is worse than a 1-in-3 shot: it is a
0-in-3 shot that was determined before the contract was frozen. As an
instrument for authorizing a 28,800 s ladder it is far weaker than the contract
presents. As a cheap refutation of a model family it is genuinely useful, and
that is what it should be called.

## Attack 2 — does the disclosure compromise the gate?

**YES.** `s_6 = −8,524` plus the committed `7,110`, `A = 174,033`,
`sr_pred = 156,520` and `|V| = 2` determine all three G1 predictions
(8,524 / 0 / −17,511) and hence the whole verdict, since a G1 failure for all
three is a gate FAIL regardless of G2/G3/G5. See OBJ-3 for the three one-line
derivations. The disclosure was made openly and the record says as much; the
objection is to the framing that survives it, not to concealment.

## Attack 3 — provenance of the one number that matters

Partly acceptable, and materially mis-stated. See OBJ-6: `d1d36dd` is
unreachable from this repository, while a committed `raw.json` carrying 7,110
and a pinned builder hash *is* in the snapshot and is not cited. The defect is
registration (no `manifest.yaml`), not absence. It is **not** load-bearing for
the Stage-1 verdict (C1 would need the rank to be wrong by ≥1,058.5, i.e. 0.7%,
against a receipt whose 11 per-unit pivot yields sum exactly to 149,410). It
**is** load-bearing for anything Stage 2 would claim, and IR11 handles that
correctly. Cheapest fix: below.

## Attack 4 — the unreconciled sem readings

A 2-column `ncols` difference **is** consistent with a seed difference (the
support is the up-closure of seed-drawn equation supports) and does **not**
prove two builders; both lineages agree on `ncols + u_6 = 190,051`, on deg≤5
completeness, and on all-deficiency-at-degree-6, which is what a builder change
would most likely break. But it cannot be *verified* from committed artifacts,
because the two sides record disjoint identity evidence (OBJ-10). And the pair
cannot test HEUR-BF-1 as formally stated, because the "fixed support data"
antecedent fails by construction.

## Attack 5 — uncharged cost

Charged in OBJ-8. Stage 2 as declared is not survivable: n=13 D6 is ≈28.9 GB
projected against a 24 GB cap and ≈4.6 h against a 28,800 s ceiling; the full
40-cell ladder is 2.7× oversubscribed; the n=13 rung alone is 2.3× the ceiling;
the budget block contradicts itself by 2.4×. The **core** (n∈{9,12}) is
survivable at 23% of the ceiling. n=14 (≈50 GB) should be struck, not marked
optional.

## Attack 6 — scope creep and transfer

Six sentences to qualify (OBJ-11); the "unblocks" justification is rhetorical
(OBJ-12). No conclusion in either record overclaims, and the Pareto/`sota_delta`
honesty is correct as written.

---

## The single cheapest control that would most improve the contract

**Rebuild the n=12, t=3, ti=0 systems at seeds 2 and 2026 from the hash-pinned
`src/semaev_tree.py` (sha256 `e9f1681b4e422f7a67176fffd3e5f91ab7a95c9fddc1eb925c2bb0a93a9becef`,
identical in `src/` and `EXP-SIG-{001,002,005,008}/src/`), and record: the
system hash, the D5 and D6 column counts, and the per-degree column histogram
at both D=5 and D=6. No rank computation.**

Cost: `build_system` plus adjacency. EV-DREG-004's restart guide measures
`build_system 0.45 s` and `adjacency 39.6 s` at n=21 / nb=42 / 778k columns;
n=12 / nb=24 / 190k columns is far smaller. Order of one minute, a few hundred
MB — inside Stage 1's declared 1,800 s / 2 GB envelope, and it converts four
separate unverifiable premises into verified facts at once:

1. **Builder identity (OBJ-10, attack 4).** If the rebuilt seed-2026 system
   hash equals `f2f61073…`/`c47d17c3…`, the two lineages share a builder and the
   138,570/138,573 pair is at least a same-builder comparison. If it does not,
   they are two builders and every cross-lineage statement in the contract —
   CTRL-3 at n=12 above all — is void, which is a *finding*, not a nuisance.
2. **The missing n=12 D5 histogram (OBJ-5).** Directly supplies `u_5` and
   whether `u_k = 0` for `k < 5`, discharging clause (6)'s per-cell obligation
   at CELL-D and replacing a derived number labelled `committed` with a measured
   one.
3. **The 7,110 anchor's structural half (OBJ-6, attack 3).** Independently
   re-derives `174,033 / 16,018 / 46,709 / 174,035 / 16,016` without relying on
   EV-SIG-008's unregistrable receipts, discharging IR3 at three of the four
   gate cells and removing the "transcript-preserved" caveat from everything
   except the rank itself.
4. **Stage-2 feasibility, free.** The same run at n=13 (build only) discharges
   the L0 off-lattice constructibility check that `blocking_nulls` currently
   carries as `unverified`, and yields the n=13 `u_6` — which, per OBJ-13,
   *by itself* decides whether Φ predicts any defect at all at n=13 D6.

Two zero-compute companions that should ship with it, in priority order:
**(i)** promote CELL-E to gating with the same ±5% band (OBJ-7) — it refutes
all three candidates on the right arm at n=9 with a registrable receipt;
**(ii)** resolve CELL-C's arm by fiat in the contract before evaluation, and
state which of the two G3 readings is being used (OBJ-2).

---

## Claim ceiling I would accept

For a Stage-1 report produced under this contract, with the corrections above:

> Over boolean chained Semaev (t=3, ti=0, GF(2)), at n ∈ {9, 12} and D ∈ {5, 6},
> on the committed cells of the EXP-SIG-006/008 and EXP-DREG-001 lineages, the
> parameter-free closed form Φ = untruncated boolean/Koszul Hilbert series with
> field equations carried, plus the EV-SIG-006 up-closure law, **fails to
> reproduce the committed arm-R rank at n=12 D6 under all three frozen collapse
> conventions, and under any collapse convention formed from partial sums of its
> own series** — the required quotient 24,623 misses the nearest reachable
> partial sum 26,037 by 1,058.5, against a tolerance of ±355.5. The same family
> also fails at n=9 D6 arm R (CELL-E). This refutes one model family for one
> measurement instrument. It establishes nothing about whether a valid D≥6 null
> baseline exists, does not repair or condemn `sr_pred`, moves no exponent,
> transfers to no prime-field statement, and leaves the mechanism of the 7,110
> defect fully open. Claim tier: **toy**. `sota_delta`: **zero on every attack
> axis**. Pollard rho remains the ECDLP baseline.

Not acceptable at any tier: "the D6 below-freeze collapse is explained/closed";
"no closed form exists"; "d_reg-derived cost predictions are unusable" without a
boolean qualifier; "GOAL-SIG-001's instrument no-go is satisfied"; any Stage-1
outcome described as unblocking a goal.

---

```yaml
red_team_report:
  id: RT-20260805-cde43a
  task_id: TASK-20260805-f7c853
  claim_under_review: >-
    EXP-SDEG-f7faa8 (status review_required, approved_by null) proposes a
    zero-compute four-number Stage-1 gate (G1/G2/G3/G5) that decides whether the
    frozen parameter-free closed form Phi of H-SDEG-0dd021 can reproduce the two
    committed n=12 D6 null numbers (7,110 arm R; 0 arm P) plus two exact
    controls, and thereby whether an n=9..13 x D=5,6 ladder is authorized.
  verdict: REVISE — do not approve as written. Stage 1 is a derivation, not a
    test; Stage 2 is not survivable at the declared budget.
  objections:
  - id: OBJ-1
    label: BLOCKING
    summary: >-
      G2 and G5 are model tautologies with zero discriminating power. G2 is
      candidate-independent (arm-P rule has no Q) and reduces to the CTRL-6
      anchor sr_pred(12,6)=156,520 with a projection-loss slack of 17,515. G5 is
      the identity u_D cancels (phi_F=6 > D=5, all candidates reduce to
      Q=sum_{k<=D}s_k). The four-gate instrument has one discriminating number.
      Precedent for exactly this failure mode: EV-IC-002 OBS-5.
  - id: OBJ-2
    label: BLOCKING
    summary: >-
      G3 is arm-ambiguous. CELL-C is declared arm P, under which Phi predicts
      28,068 and G3 fails for all three candidates by exactly 3,111 (the
      sr_pred overshoot EV-SIG-006 already committed). The G3 metric text says
      "per candidate", which only arm R can produce; under arm R, C2 and C3 pass
      at 31,179. N0 is neither P nor R under the contract's own taxonomy. A live
      degree of freedom in a record asserting none.
  - id: OBJ-3
    label: BLOCKING
    summary: >-
      coordinator_prior_disclosure (s_6 = -8,524, freeze pulled 7->6) plus
      committed numbers determines all three G1 predictions (8,524 / 0 /
      -17,511) and hence the whole verdict. Pre-registration cannot protect an
      outcome that is a deterministic function of the pre-registration. Stage 1
      is a derivation the record already contains, budgeted and framed as a test.
      Disclosed rather than concealed; the objection is to the surviving framing.
  - id: OBJ-4
    label: BLOCKING
    summary: >-
      F1 is structurally guaranteed and the refutation is broader than three
      candidates. Required Q = 24,623, band [24,267.5, 24,978.5]; the reachable
      lattice {0,1,2,25,289,2013,9117,17513,26037} contains no point in the band
      and the nearest misses by 1,058.5 = 1.5 window widths. No partial-sum
      collapse convention can pass. "Decidable with a reachable negative" is
      really "determined with an unreachable positive".
  - id: OBJ-5
    label: NON-BLOCKING
    summary: >-
      u_5 = 8,746 is labelled `committed` at CELL-D and occurs nowhere in the
      repository except H-SDEG-0dd021 itself. It is derived as N(24,5)-46,709
      under an unverified assumption. The n=12 D5 degree histogram is committed
      nowhere, so clause (6)'s "VERIFIED PER CELL, never assumed" precondition is
      undischargeable at a gate cell.
  - id: OBJ-6
    label: NON-BLOCKING
    summary: >-
      CELL-A provenance misdescribed both ways. Cited commit d1d36dd is
      unreachable from this repository; the committed, in-snapshot artifact
      experiments/EXP-SIG-008/runs/RUN-EXP-SIG-008-n/raw.json (rank 149410,
      deficit 7110, semaev_tree.py sha e9f1681b..., secs_total 1182) is not
      cited. Defect is registration (no manifest.yaml), not absence. Not
      load-bearing for the verdict (C1 needs a 1,058.5 = 0.7% rank error to
      pass). Also: re-measuring that cell costs 1,182 s, less than Stage 1's own
      1,800 s budget, yet is deferred to an unauthorized Stage 2.
  - id: OBJ-7
    label: NON-BLOCKING
    summary: >-
      CELL-E (n=9 D6, arm R, registrable EV-SIG-006 receipt) is demoted to
      non-gating while the worst-provenanced cell gates. It already refutes all
      three candidates: C1 26,220 (wrong sign: predicts +1,848 vs measured
      -871), C2/C3 29,332 (miss +393; deficit -1,264 vs -871, 45% off). The
      demotion reason attacks EV-SIG-006's inference, not its measurement, and
      runs in the model's favour.
  - id: OBJ-8
    label: BLOCKING for Stage 2; NON-BLOCKING for Stage 1
    summary: >-
      Stage 2 is not survivable. n=13 D6 projects to ~28.9 GB peak RSS against a
      24 GB cap and ~16,626 s against a 28,800 s ceiling; the 40-cell ladder is
      ~77,833 s = 2.7x oversubscribed; the n=13 rung alone is 2.3x the ceiling;
      n=14 is ~50 GB. The budget block contradicts itself 2.4x (117 runs x 600 s
      = 70,200 s vs 28,800 s ceiling; 120 x 600 = 20 cpu-h vs 8.5 declared). SR3
      forces >=28 invocations for one n=13 cell, against the EV-DREG-004
      precedent of a 33-invocation lineage destroyed at 24.93%. The core
      (n in {9,12}) IS survivable at 23% of the ceiling.
  - id: OBJ-9
    label: NON-BLOCKING
    summary: >-
      "One instrument lineage" is two exact-rank engines (SIG8_run.sage vs
      src/h012c_block_m4ri.py). CTRL-5 exists because elimination orders can
      disagree; two engines is the stronger version of that risk.
  - id: OBJ-10
    label: NON-BLOCKING
    summary: >-
      The Stage-1 builder-identity check is guaranteed inconclusive: the SIG side
      records a builder hash and no system hash, the DREG side a system hash and
      no builder hash. Separately, the 138,570/138,573 pair cannot test HEUR-BF-1
      as formally stated, because the "fixed support data" antecedent fails
      (174,033 vs 174,035). A 2-column difference IS consistent with a seed
      difference and does not prove two builders.
  - id: OBJ-11
    label: NON-BLOCKING
    summary: >-
      Six unqualified occurrences of "d_reg-derived cost predictions" /
      "d_reg predictions usable" / "condemning this one step is upstream of
      [three goals]" could be cited across the boolean-to-prime-field gap,
      especially since the negative is routed to IDEA-20260803-fa9839 (prime-field
      arity threshold) and the pinned instrument is named dreg_crypto_cost_model.py.
      Add the boolean qualifier at every occurrence.
  - id: OBJ-12
    label: NON-BLOCKING
    summary: >-
      "Unblocks SDEG/DREG/SIG" is rhetorical. Checked all three goals at the
      snapshot: neither branch changes any next_action. GOAL-SIG-001's
      "scoped instrument no-go" route is real but this negative does not reach it
      (the contract itself says a FAIL does not establish that no closed form
      exists). A FAIL condemns a proposed repair of sr_pred, not sr_pred.
  - id: OBJ-13
    label: NON-BLOCKING
    summary: >-
      No decay control. Phi's own mechanism requires s_6 = h_6 - u_6 <= 0; at
      n=13, h_6 = 106,743 so the support must miss 28.3% of sextics versus the
      committed 11.9% at n=12. At the committed miss fraction all three
      candidates predict deficit EXACTLY 0 at n=13 D6 arm R. h_6 jumps 7,494 ->
      106,743 between n=12 and n=13, so the proposed mechanism is live only at
      n in {10,11,12} — the canonical shape of a one-size artifact, which the
      contract should carry as an explicit alternative hypothesis.
  required_controls:
  - >-
    CHEAPEST, DO FIRST: rebuild the n=12 t=3 ti=0 systems at seeds 2 and 2026
    from the hash-pinned src/semaev_tree.py (e9f1681b...), recording system hash,
    D5 and D6 column counts, and per-degree histograms at both degrees. No rank
    computation; ~1 minute. Settles builder identity, supplies the missing n=12
    D5 histogram, re-derives 174,033/16,018/46,709/174,035/16,016 independently
    of unregistrable receipts, and (extended to n=13, build only) discharges L0
    and yields the n=13 u_6 that decides OBJ-13.
  - >-
    Promote CELL-E (n=9 D6 arm R, EV-SIG-006 registrable receipt) to a gating
    cell with the same +-5% band. Zero compute. It refutes all three candidates
    on the correct arm, at a second n, on better provenance than CELL-A.
  - >-
    Resolve CELL-C's arm in the contract text before any evaluation, and state
    which G3 reading is in force. Under arm P, G3 fails for all three by 3,111
    and must be declared a guaranteed-fail control rather than a gate.
  - >-
    Re-state the negative at its true scope (OBJ-4): no partial-sum collapse
    convention can pass G1 at CELL-A, not merely these three.
  - >-
    Pre-register the n-decay prediction of OBJ-13 (all three candidates predict
    deficit exactly 0 at n=13 D6 arm R unless the sextic miss fraction exceeds
    28.3%) BEFORE any Stage-2 cell is measured.
  - >-
    Restrict any Stage-2 authorization to the core (n in {9,12} x D in {5,6} x
    both arms x 2 seeds, ~6,597 s = 23% of ceiling). Strike n=14. Move n=13 to a
    separate contract with its own memory analysis.
  counterexample_or_mutation: >-
    CELL-E is the counterexample already sitting in the contract, demoted to
    non-gating: n=9, D=6, arm R, |V|=0, A=29,332, measured rank 28,939 on a
    registrable receipt. C2 and C3 — the only candidates that can pass G3 under
    the arm-R reading — predict 29,332 (deficit -1,264 against a measured -871,
    45% off). C1 predicts 26,220 with the wrong sign. The mutation that would
    have made the gate informative is therefore free: gate on CELL-E as well as
    CELL-A, so that the family must survive two independent n on the same arm.
  baseline_comparison: >-
    NOT APPLICABLE AS AN ATTACK, AND CORRECTLY DECLARED SO. Both records set
    asymptotic_claim null, corollaries empty, sota_delta zero on every axis
    (time, memory, data, queries, advice), and dominated_by not-applicable
    because no Pareto point is claimed. I checked and I do not dispute any of it:
    this is a model repair of a measurement instrument, no exponent moves,
    Pollard rho and BSGS remain the ECDLP baselines untouched, and KN-OPEN-002
    (prime-field solving-degree growth) is neither closed nor narrowed. The
    dominated_by null here is not a rule-5 fabrication. The one Pareto-shaped
    obligation that IS owed (KN-LIT-7593: an eliminated search dimension is not a
    speedup until the invariant's own cost is charged) is met for Stage 1's
    evaluation cost (zero) and NOT met for its validation cost: the ladder that
    would license any use of Phi costs 2.7x the declared Stage-2 budget (OBJ-8).
  heuristic_challenges:
  - >-
    HEUR-BF-1 (determinism of extra_D). Its own random_model_justification
    concedes there is none that survives scrutiny, which is honest. But the datum
    the contract offers to test it — the 138,570/138,573 pair — cannot test it,
    because the "fixed support data" antecedent fails by construction (174,033 vs
    174,035, two rank engines, two experiments). The pair should be recorded as
    uninterpretable rather than as pending-builder-check.
  - >-
    HEUR-BF-2 (the three-member family contains the truth). The record already
    names this as its weakest link. OBJ-4 sharpens the refutation from "these
    three" to "any partial-sum convention", which is the useful form.
  - >-
    HEUR-BF-3 (the arm rule). Its declared falsifier is G2, which cannot fail
    (OBJ-1). So HEUR-BF-3 is stated with a falsification condition that is
    unreachable. Its real test would be a cell where the arm-P projection loss is
    nonzero, i.e. where sr_pred + u_D > N(nb,D); no such committed cell exists,
    and none is in the ladder. That gap should be stated.
  - >-
    Scale honesty (AGENTS rule 7): correctly and repeatedly declared toy, with a
    boolean-to-prime-field gap stated as UNMET rather than deferred. No objection.
  cost_model_challenges:
  - >-
    n=13 D6 exceeds the declared 24 GB memory cap (carrier 13.50 GB, projected
    peak ~28.9 GB at the measured 2.14x factor). n=14 is ~50 GB. Memory, not
    time, is the binding constraint and the contract charges only time.
  - >-
    The full ladder is ~77,833 instrument-seconds = 21.6 h against a 28,800 s
    ceiling (2.7x). The n=13 rung alone is 2.3x the ceiling. SR4 is written as
    graceful degradation but is the expected path from the outset.
  - >-
    The budget block is internally inconsistent by 2.4x on both the stage and
    top-level rows.
  - >-
    Re-measuring the weakest-provenance anchor costs 1,182 s per its own committed
    receipt — less than Stage 1's declared wall clock — yet is charged to an
    unauthorized Stage 2.
  - >-
    All Stage-2 projections here are a rows x cols x min(rows,cols) model
    calibrated on ONE measured cell and are marked UNVERIFIED. No off-lattice
    cell of this lineage has ever been built.
  reduction_and_scope_challenges:
  - >-
    No reduction is claimed and corollaries is deliberately empty — correct.
  - >-
    Six sentences omit the boolean qualifier on "d_reg-derived cost predictions"
    (OBJ-11), and the negative is routed to a prime-field threshold proposal.
  - >-
    The affected-vs-safe analogue here is the goal-unblocking claim, and it is
    inflated: no goal's next_action changes on either branch (OBJ-12).
  proof_architecture_challenges:
  - >-
    Baseline reproduction (audit 1): PASSES. I re-derived all ten structural
    anchors independently and confirm every one. Not disputed.
  - >-
    Observation collision (audit 2): correctly identified and committed, and it
    IS the content of the hypothesis. But the proposed separator — the sign of
    s_D under the arm's own numerator — fails at CELL-A for all three
    candidates and at CELL-E for all three, so the separator does not separate.
  - >-
    Quantifier order (audit 3): stated correctly as EXISTS Phi FORALL cells, and
    the weaker order is explicitly disclaimed. But the witness was chosen after
    the quantity that evaluates it was in hand (OBJ-3), which is the quantifier
    defect in its epistemic rather than logical form.
  - >-
    Method ceiling (audit 4): honestly stated (toy, boolean-only, cannot close
    KN-OPEN-002). No objection.
  - >-
    Nearby-object control (audit 4b): two are named, and both are cells where all
    three candidates trivially succeed (CELL-B, CELL-D). The nearby object that
    actually discriminates — CELL-E, same arm, |V|=0 — is demoted to non-gating
    (OBJ-7). The nearby-object control as configured cannot fail.
  - >-
    Compositional invariant: the contract's one derived theorem ("sr_pred is
    support-independent") is the algebraic triviality that u_D cancels, and its
    identification with sr_pred requires D < phi_full. At n=9 D6 the untruncated
    full prediction is 36,165 against 31,180 columns — a rank exceeding the
    column count. The corollary therefore holds only outside the regime the
    hypothesis is about, and should be stated with that hypothesis attached.
  narrowest_supported_statement: >-
    On the committed cells of the EXP-SIG-006/008 and EXP-DREG-001 lineages
    (boolean chained Semaev, t=3, ti=0, GF(2), n in {9,12}, D in {5,6}), the
    frozen parameter-free closed form Phi does not reproduce the committed arm-R
    rank at n=12 D6 (149,410; required quotient 24,623) under C1 (26,037), C2
    (17,513) or C3 (2), nor under any collapse convention formed from partial
    sums of its own series, the nearest reachable value missing the +-5% band by
    1,058.5 against a tolerance of +-355.5; and it additionally fails at n=9 D6
    arm R (CELL-E, measured 28,939; predictions 26,220 / 29,332 / 29,332). This
    refutes one model family for one measurement instrument at toy scale. It does
    not establish that no closed form exists, does not repair or condemn sr_pred,
    does not resolve the mechanism of the 7,110 defect, moves no exponent,
    transfers to no prime-field statement, and changes no goal's next_action.
  next_concrete_action: >-
    Before approval: run the ~1-minute builder rebuild described in
    required_controls[0] (seeds 2 and 2026 at n=12, plus n=13 build-only), record
    the system hash and the D5/D6 per-degree histograms, and use the result to
    (a) settle builder identity, (b) replace the uncommitted u_5 = 8,746 with a
    measured value, and (c) fix the n=13 u_6 that decides whether Phi predicts any
    defect at n=13 at all. Then amend the contract to promote CELL-E to gating,
    fix CELL-C's arm, restate the negative at partial-sum-family scope, correct
    the CELL-A provenance citation to RUN-EXP-SIG-008-n/raw.json, and restrict any
    Stage-2 authorization to the n in {9,12} core.
  artifact_paths:
  - coordination/goals/GOAL-SDEG-001/reviews/TASK-20260805-f7c853/red_team_report.md
  - experiments/EXP-SDEG-f7faa8/specification.yaml
  - ledger/hypotheses/H-SDEG-0dd021.yaml
  - ledger/corrections/CORR-20260805-9d2e17.yaml
  - ledger/proposals/IDEA-20260803-202a15.yaml
  - ledger/proposals/IDEA-20260803-fa9839.yaml
  - ledger/evidence/EV-SIG-006.yaml
  - ledger/evidence/EV-SIG-008.yaml
  - ledger/evidence/EV-DREG-004.yaml
  - ledger/evidence/EV-DREG-008.yaml
  - ledger/evidence/EV-IC-002.yaml
  - ledger/goals/GOAL-SDEG-001.yaml
  - ledger/goals/GOAL-SIG-001.yaml
  - ledger/goals/GOAL-DREG-001.yaml
  - knowledge/open-problems/KN-OPEN-002.md
  - experiments/EXP-SIG-008/runs/RUN-EXP-SIG-008-n/raw.json
  - coordination/goals/GOAL-DREG-001/batches/BATCH-005/tasks/TASK-20260731-016/results.json
  - coordination/goals/GOAL-DREG-001/batches/BATCH-005/tasks/TASK-20260731-016/raw-result.json
  snapshot_reviewed: 07c431181fd36e058d016733c034cb88e42c7e8f
  branch: claude/ssi-ecdlp-experiments-4cwbrq
  computation_note: >-
    Every number attributed to Phi in this report was recomputed independently
    from clauses (1)-(9) by this session, not read from the records under review.
    All Stage-2 cost figures are a rows x cols x min(rows,cols) model calibrated
    on the single measured cell TASK-20260731-016 and are marked UNVERIFIED. No
    quantity in this report is presented as a measurement this session performed
    on a Macaulay matrix; no rank was computed here.
  inference:
    requested_policy: review-adversarial
    resolved_model_id: claude-opus-5
    reasoning_effort: null
    fallback_used: true
    fallback_reason: >-
      This Claude Code harness cannot resolve the policy aliases in
      orchestration/model-policies.yaml. Recorded, never silently substituted
      (AGENTS.md rule 11).
    degraded_allowed: false
    degraded_requirements: []
    independent_session: true
    model_verified: false
    model_verified_reason: >-
      No adapter probe receipt was obtained for this session.
```
