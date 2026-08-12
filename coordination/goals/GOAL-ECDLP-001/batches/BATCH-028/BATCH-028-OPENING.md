# BATCH-028 OPENING — MEASURE THE YARDSTICK

**Goal:** GOAL-ECDLP-001 · **Sub-goal:** SG-ECDLP-001 · **Question:** RQ-ECDLP-002
**Opened by:** DEC-20260801-015 (2026-08-01)
**Queue:** `coordination/goals/GOAL-ECDLP-001/batches/BATCH-028/dispatch_queue.json`
**Tasks:** TASK-20260802-001 … TASK-20260802-011 (eleven cards) · **max_concurrent:** 3
**Goal status:** `active`. BATCH-028 is the **twenty-eighth** batch against
`campaign_budget.maximum_batches = 50`, so **no pause condition fires** — stated
explicitly rather than left implicit.

---

## 1. The single next action, and why it cuts both ways

BATCH-027 measured `HEUR-DS-1` for the first time in twenty-seven batches and
branch **L-4** fired: one of ten certifying comparisons outside its archived
band, at **one** cell, direction `BELOW_BAND`, disposition **`inconclusive`**
(DEC-20260801-014, EV-LPF-001).

That outcome can be neither strengthened nor dismissed, and the reason is
`OBJ-RT082-1`: **the frozen band is calibrated to a noise source the real arm
does not have.**

| | `OBJ-NULL-UNIF` | `OBJ-REAL` |
|---|---|---|
| what it is | 130,816 **iid draws** | **not a sample** — the frozen specification says so |
| noise scale | 200-replicate sd matches `√(p(1−p)/n)` to ~8% at every rung | determined by 512 x-coordinates, each in 511 pairs, `n = C(512,2) = 130816` exactly |
| fluctuation actually measured | yes | **no — one instance per cell** |

**It cuts both ways and that is precisely why it is decisive.** If the
between-instance sd **exceeds** the iid sd, the one reject is noise **and the
nine non-rejections are nearly vacuous**, because a band too narrow is one a
genuinely deviant real arm would also have passed at `u = 4` and `u = 5`. If it
is **below**, both are stronger than they look. The detection-floor table
published in EV-LPF-001 — `u=2 ±1.7%`, `u=3 ±4.5%`, `u=4 ±13%`, `u=5 ±39%` —
**could be right by a factor of 1 or wrong by a factor of ~16**, and nothing in
the campaign distinguishes those. **It is not repairable by argument.**

It is also the only action that simultaneously decides whether the bits-16
`u = 2` shortfall **reproduces or evaporates**, and discharges the artifact side
of **RT049-CTRL-5**, without which `H-LPF-001` can never reach `replicated`.

---

## 2. The ruling: a control under EXP-LPF-001, not a new EXP id

`RULE-BATCH028-CTRL`. **Run id `RUN-LPF-001-ivr`. No new EXP id, no new
hypothesis.** Four grounds:

1. **It changes the object, not the apparatus.** Same INT-1, same ENC-B, same
   `Bfb = 512`, same `i < j` enumeration, same driver at `786aeb05` — *imported,
   not edited*. EXP-LPF-001 already carries four objects under one contract
   (`OBJ-REAL`, `OBJ-NULL-UNIF`, `OBJ-CTRL-PRODUCT`, the two plant families); a
   fifth, `OBJ-REAL-FRESH`, is the same move a fifth time.
2. **It is this experiment's own named control.** `RT082-CTRL-1` was filed by
   EXP-LPF-001's red team; `RT049-CTRL-5` is EXP-LPF-001's control debt; and
   RR-LPF-2's L-4 disposition *names it in terms*.
3. **A new EXP id would orphan the calibration and the driver from their
   contract** — the argument that decided EXP-SMTH vs EXP-LPF the other way.
   Every reported quantity is a **ratio whose denominator is an EXP-LPF-001
   calibration array** (bits-16 `u=2`: `0.0012764339776488623`, archived at
   `104d32fa`). Under a new id those arrays become a foreign input and the
   anti-tuning chain `ba1567ee → 104d32fa → 2ff751c5` attaches to a contract
   they were never approved under.
4. **Immutability is satisfied, and here is exactly how.** AGENTS.md rule 4
   forbids *editing* a record, not *adding* one. **Nothing existing is edited by
   any task in this queue.** The control specification, RR-IVR-1 and the wrapper
   are **new files at new paths** under `experiments/EXP-LPF-001/control_ivr/`,
   frozen and hash-bound before any datum — **precisely the RR-LPF-1 → RR-LPF-2
   precedent**, which BATCH-026 authored, TASK-20260801-068 reviewed and
   BATCH-027 used to adjudicate a real measurement.

**The counter-argument, stated and answered:** the frozen spec pins `OBJ-REAL`
to the 2301 instances, and the free rider is a quantity the driver does not
compute. The first is answered by the *definition* of a control. The second by
construction — the wrapper **imports** the driver and aggregates outside it. **If
the free rider cannot be computed without modifying the driver, the contract
author must say so and stop.** That is a finding, never a licence to edit.

**What the ruling does not do:** it does **not** advance `H-LPF-001`, and **no
task in this batch writes `ledger/hypotheses/H-LPF-001.yaml`.** The control
*produces* what RT049-CTRL-5 demands; whether that supports `replicated` needs
the statistics re-read under RR-LPF-2 at those instances — **and RR-LPF-2's bands
are the very thing under test.** Adjudicating it here would be circular. Ranked
as the successor contract, first among them.

---

## 3. The pre-registration — fixed by the Coordinator, not the contract author

This is a **stronger anti-tuning posture than BATCH-027 had**, and BATCH-027's
was the strongest the campaign had had. The design is fixed in
`DEC-20260801-015`, committed alone at TASK-20260802-002, **before any contract
author is engaged and before any instance exists**, and the freeze commit must be
a Git **ancestor** of the run commit.

| fixed here | value |
|---|---|
| `k` per cell | **20**, `ν = 19`; any increase needs a versioned `protocol_amendment` |
| master seeds | **90001 … 90020**, disjoint from 2301 and every archived stream |
| substitution rule | next unused integer upward from **90021**, deterministic, every substitution reported |
| quantities | `p̂(u)` at `u ∈ {2,3,4,5}` and `STAT-KS-DICK`, 2 cells → **10 VR comparisons** |
| **primary** | **VR at bits-16, `u = 2`** — finest resolution (±0.87%) and the rung the reject fired at |
| free rider | 512 per-index smooth rates, **both nulls** |
| `R_PERM` | **2000** |

---

## 4. The reading rule `RR-IVR-1` — simpler than a branch structure, and argued

RR-LPF-2 exists to route one measurement into one of six mutually exclusive
dispositions. **This control asks a measurement question with a continuous
answer**, and the honest instrument for that is an **interval**, not a branch.
Importing branch machinery would manufacture a disposition the data does not
carry **and would let this batch re-adjudicate BATCH-027 through the back door.**

- **`I-0`** — the only suspending condition (integrity: short arm, hash drift,
  sub-100% factorization, seed collision, **fewer than 20 distinct instances**,
  all instances identical, tripwire true, timeout/crash/budget). On firing, **no
  ratio is a measurement** and the outcome is an *instrument* outcome.
- **`C-WIDE`** — yardstick too narrow at rung `u` **only if** `VR ≥ 1.2596` at
  **both** cells. Repair is a **superseding note**, never an edit.
- **`C-TIGHT`** — yardstick conservative **only if** `VR ≤ 0.7297` at **both**
  cells. Strengthens nothing.
- **`C-INDET`** — *"not resolved at that rung at k = 20"*, **in those words**.
  Never read as "the band is correct".
- **`C-REPRO-1`** (primary, **yardstick-free**) — `z_2301` against the fresh
  family's own sd. Because `OBJ-REAL` is exhaustive there is **no
  within-instance noise**, so three explanations separate cleanly in advance.
- **`C-REPRO-2`** (secondary, **circularity declared**) — count below the
  archived edge; `P(X≥3) = 0.00097` under the no-offset null; **void if C-WIDE
  fires at that cell/rung**.
- **`C-MEAN`** — computed, **and expressly not read by anyone**. Refusing to
  compute an obvious statistic so nobody can look at it is not rigour; *reading*
  it would adjudicate `H-LPF-001` through a statistic no frozen rule covers.

**Multiplicity, declared in advance.** Ten comparisons at 0.05 one-sided would
be FWER ≈ **0.401** — `OBJ-RT082-3` exists because exactly this was left to the
reader. The **both-cells rule** is adopted in advance: per-rung ≤ 0.0025, FWER
over five rungs ≤ **0.01243**. Both cells share the same 20 master seeds, so
independence is an **approximation** — declared here, measured by the run, and
recomputed by the Red Team.

---

## 5. Attainability — the one genuinely new duty, pre-registered

`OBJ-REAL` is exhaustive, so **there is exactly one noise source in this design:
the instance.** `(k−1)s²/σ² ~ χ²₁₉`.

| quantity | derived value |
|---|---|
| 90% interval for σ | `[s·0.79392, s·1.37041]` |
| relative SE of `s` | `1/√38 = 0.1622` (±16%) |
| **declare-wide floor** | `VR ≥ 1.2596` |
| **declare-tight ceiling** | `VR ≤ 0.7297` |

| true VR | power (one cell) | power (both cells) |
|---|---|---|
| **16** | ≈ 1.000 | ≈ 1.000 |
| 4 | ≈ 1.000 | ≈ 1.000 |
| 2 | 0.990 | 0.980 |
| 1.5 | 0.818 | 0.669 |
| 1.26 | ≈ 0.50 | ≈ 0.25 |
| ≤ 1.1 | **no useful power — declared, not discovered** |

**The whole case for `k = 20`:** the alternative that matters is **not** a 26%
inflation. `OBJ-RT082-1` route (a) puts the effective sample size nearer 512 than
130,816, i.e. `VR ≈ √(130816/512) = 15.98` — **the factor of sixteen the goal
record names**. The floor is `1.2596`. **The alternative that would vacate the
entire detection-floor table sits ~12.7× above the floor.**

**What `k = 20` does not buy:** resolution better than ~26%. An all-`C-INDET`
outcome licenses *"the iid band is not shown to be wrong by more than about a
quarter in either direction at k = 20"* — **materially weaker than "the band is
correct", and EV-IVR-001 must write the weaker one.**

---

## 6. A correction to the free rider as first specified

RT-20260801-082 specified the dispersion of the 512 rates against
`√(p(1−p)/511)`. **The 512 rates are not independent** — each pair enters exactly
two of them — so that comparison alone is an **uncontrolled** statistic: the exact
failure `docs/inventor-protocol.md` §3 names, applied to the control that exists
to enforce §3.

**The repair costs no factorization at all:** a **permutation null** over the
130,816 **pair slots** at `R_PERM = 2000`, holding the incidence structure and
the total smooth count fixed. Under no-first-order-projection the indicators are
exchangeable across pairs, so the null is **exact conditionally on the total**.
**Both** nulls are reported; neither alone.

**`W3` — the two instruments are not substitutes.** The free rider sees
**first-order structure only**. A purely *second-order*, pair-level dependence
would leave the 512 rates at their exchangeable dispersion while still inflating
the between-instance sd. **A clean free rider licenses no statement about VR**,
and a large VR with a clean free rider is a coherent outcome, not a
contradiction.

**`PRE-Q-1`, answered from source before freezing:** does `generate_instance`
vary `p`, or only the curve at a `p` fixed by `bits`? The factor base depends
**only on `p`**. If `p` is fixed, all 20 instances share **one** small-x window
and RT049-B6 bites harder. Neither answer invalidates the control; **only an
unstated answer would.**

---

## 7. Gates retired — argued, and the reduction is self-voiding

| retired | status | why |
|---|---|---|
| calibration arm | **retired as a re-run, not waived** | re-running it adds pure noise **to the denominator of the ratio under test** |
| plant-Z / perturbation ladder | **absent, not waived** | nothing is planted; this control **certifies no power against any contamination** |
| movement-at-every-rung | **retired as a plant-ladder re-run; re-formed** | no clause reads a `moving_rungs` list or a gamma floor → **re-forms as "every ratio carries its interval"** |
| four-change-cap diff | **retired; replaced by a harder duty** | RR-IVR-1 has no predecessor → **the non-inheritance check**: an imported clause would silently re-adjudicate BATCH-027 |
| alt-class source re-derivation | **retired as a derivation; carried as restatement** | V1–V12 unchanged; the batch authors **W1–W5** fresh instead |
| one-cycle amendment cap | **not applicable** | no reading rule is amended |

**No sixth discipline is added.** The five are carried, two re-formed:
attainability **re-authored**, movement **re-formed**, anti-tuning
**strengthened**, decision-variable variation as **denominator traceability**,
and PERTURB-TAIL-1 **sharpened** — a standard deviation whose underlying values
are not archived is unauditable, so the 20 per-instance vectors and the 512
per-index arrays **must** be archived as arrays.

**Self-voiding:** the reduction rests entirely on hash equality of
`specification.yaml` `0d6c946f`, `reading_rule.yaml` `8bcb196f`,
`reading_rule_v2.yaml` `b633eaf1`, `lpf001_driver.py` `786aeb05`, and the
calibration package at `104d32fa`. **Any mismatch at any archive voids the
reduction, stops the batch, and returns the full duty set.**

---

## 8. The queue

| task | role | what | gate |
|---|---|---|---|
| 001 | coordinator | open, author DEC-20260801-015 | — |
| 002 | coordinator | **snapshot** the opening alone (the pre-registration) | — |
| 003 | executor | author + **freeze** control spec, RR-IVR-1, wrapper. **No run.** | CFG-1 |
| 004 | coordinator | **snapshot** the freeze alone — the anti-tuning anchor | — |
| 005 | reviewer | independent contract review, 7 checks | PASS/REVISE |
| 006 | coordinator | **snapshot** review + `APPROVAL_DETERMINATION` | **RC-28** |
| 007 | executor | **RUN-LPF-001-ivr, once** | `review_required: true` |
| 008 | coordinator | **snapshot** the run alone, before anyone reads it | — |
| 009 | validator | independent validation | — |
| 010 | red-team | independent red team (sibling of 009, no edge) | — |
| 011 | coordinator | **ledger archive** — EV-IVR-001, DEC-20260802-001, GOAL | — |

**Exactly one experimental run is authorizable.** A `REVISE` at TASK-20260802-005
means the run does not happen, 007–011 stand terminal `blocked`, and BATCH-028
records a **non-execution** — a record-integrity outcome, **never** a
mathematical result and **never** an infrastructure failure.

---

## 9. Claim ceiling

Toy tier. G1–G4 **OPEN**. No `support`, no `reject_scoped`, no `replicated`, **no
hypothesis transition of any kind**. `dominated_by` may not be null.

> **A variance ratio is evidence about the yardstick and is not evidence about
> HEUR-DS-1 in either direction.** A wide band does not mean the intermediates
> are uniform; a tight band does not mean they are not.

> **This batch may not re-adjudicate BATCH-027.** DEC-20260801-014 stands; L-4 is
> not re-selected, re-read or reversed; EV-LPF-001 is neither edited nor
> re-scored. A `C-WIDE` finding is repaired by a **superseding note under a new
> id**.

V1–V12 (with V8's deep-tail blindness and V9), ABS-REL-LPF-1, LIMBB-DECL-RR066,
W1–W5, DEF-065-1..5, DEF-068-A..D, D2–D6, RT049-B6 sharpened, OPEN-RR052-B/C/D,
OPEN-RR066-A, OPEN-LPF049-A, OPEN-BATCH022-A/B, OPEN-BATCH023-B, OPEN-BATCH024-A,
OPEN-BATCH027-A/B and the standing model-independence caveat **all bind**.

---

## 10. New open items, and one corrected diagnosis

- **`OPEN-BATCH028-A` — EV-STR-001 is *misfiled*, not missing.** The ideation
  session reported it has no file. **It does**, at `ledger/EV-STR-001.yaml` — the
  ledger **root** — not `ledger/evidence/`, so every directory glob misses it. It
  also declares `hypothesis_id: STR-H-001`, a non-canonical id, and
  `ledger/DEC-20260718-003.yaml` is misfiled the same way. **The distinction
  matters because the two defects have different repairs and one is forbidden:**
  an absence is repaired by writing a record; a **misfiled archived record may
  not be repaired by moving it**, because a move changes the path every prior
  citation resolves against. Acting on the wrong diagnosis would have produced
  the forbidden repair. Carried ranked, not repaired here.
- **`OPEN-BATCH028-B` — the knowledge-promotion gate has no route for a
  methodological finding.** `KN-CAND-BATCH024-A`'s trigger (b) is **met** and
  recorded as met; the gate is stated purely in *hypothesis dispositions*, which
  a transferable *procedural* lesson can never satisfy. A trigger met twice
  against a structurally unreachable gate is **evidence of misalignment**, and it
  is named here rather than deferred a third time without explanation.

---

## 11. The frontier — recorded, not decided

Seven proposals (`IDEA-20260802-001..007`) are filed and **unconsumed**. None is
approved, closed or dismissed, and **none may be called saturated** without the
inventor-protocol §4 obstruction, argument and forward guidance.

- **1st behind the single action — `IDEA-20260802-004`** (crypto-scale HEUR-DS-1
  validation): most target-profile-aligned; C12 is a flat **NO** today.
  *Deferred because running a larger, costlier measurement whose yardstick may be
  wrong by 16× buys a bigger number carrying the same undeclared error.*
- **2nd — `IDEA-20260802-001`** (saddle-point smoothness reference): BATCH-027's
  actual distributional finding was about **the reference**.
- **`IDEA-20260802-003` — the only exponent-moving candidate in the set.**
  Enumerate-and-join pinned at `1/2` *identically in arity*, with box-constrained
  small-root solving as the sole escape targeting `1/2 → ω_LA/m`. Not first
  because a conditional result may only be dispatched **paired with a
  heuristic-validation experiment**; designing that pairing is its first work.
  **Not deprioritized for lack of merit.**
- **`IDEA-20260802-005`** — kills or bounds `H-ENDO-001`, which stands `approved`
  **with zero evidence**, in an afternoon. Unusually good cost-to-information.
- Carried unranked against each other: `-002` (tracked-object enumeration toward
  `KN-OPEN-019`), `-006` (scalar index set as tracked object), `-007`
  (charged-unit cost model).

Successors ranked behind the single action: the **RR-LPF-2 re-read at the fresh
instances** that would actually decide `replicated` (**new, first**), then
RT082-CTRL-2 (windowed null), RT082-CTRL-3 (second encoding), the deep-tail
perturbation family, the centred-LIMB-B successor, the signed `(D+, D-)` driver
revision, the dependence-power repair, route (b) of KN-CAND-BATCH023-A,
RT049-CTRL-3, the generated superseded-by index, and OPEN-BATCH027-A /
OPEN-BATCH028-A / OPEN-BATCH028-B.
