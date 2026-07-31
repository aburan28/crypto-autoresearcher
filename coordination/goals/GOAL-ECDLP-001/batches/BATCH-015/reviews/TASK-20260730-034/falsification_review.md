# TASK-20260730-034 — Falsification and scope review of the BATCH-015 probe

**Cite this document by path and task ID only. No `RT-*` identifier is minted.**
`RT-20260729-036` is not issued to this or any report.

- Goal: `GOAL-ECDLP-001` · Batch: `BATCH-015` · Role: red-team
- Snapshot under review: `e3cf9fdd770cbab3ebf55691a60143ace2b75f4c`
- Session independence: **asserted**. Model independence: **not available and not
  claimed** (INT-BATCH015-D, INT-BATCH015-E). This session counts toward **no**
  completion quorum.
- Bounded card: 2400 s. Lines of attack not reached are named in section 10.

Byte provenance was checked, not assumed: `structure_probe.json`,
`supply_probe.json`, `probe_driver.py` and `probe_manifest.json` were re-hashed
from git object content at `e3cf9fdd` and are identical to the working tree.
This is a review of the committed snapshot.

---

## 1. The case against, at full strength

The probe will be summarised by whoever reads it next as three facts: *both
CTRL-4 structure assertions pass; twenty-eight supply units with maximum
shortfall zero; the pre-registered falsification condition did not fire.* Taken
together those read as a clean bill of health for the two committed-code
hypotheses `DEC-20260729-004`'s derivation assumes.

**They do not amount to that, and the reason is the same in all three cases: the
probe measured places where nothing was doing the work of making the answer come
out other than it did.**

### 1.1 The block identity is the constructor's own arithmetic, read back

`harness/endomorphism_la.py::_build_phi_invariant_factor_base` mutates its
output list on exactly one path:

```python
orbit = [x, (zeta3 * x) % p, (zeta3 * zeta3 * x) % p]
...
xs.extend(orbit)
return xs[:B] if len(xs) >= B else xs
```

`xs` is never permuted, never inserted into, never appended to elsewhere. The
truncation `xs[:B]` preserves the first `floor(B/3)` contiguous triples intact.
CTRL-4's condition (ii) then evaluates

```python
F[3*j + k] == pow(zeta3, k, p) * F[3*j] % p   for 0 <= j < len(F)//3
```

— which is the same arithmetic expression, applied to the values that expression
produced. **It is a mirror test.** It cannot fail for any `B`, any curve, any
seed, and — critically — for any `zeta3`.

I ran the mutation. Calling the committed builder at `B = 192` on CURVE-J12S1
with `zeta3 = 5` (whose cube is 125 mod 2293, so it is *not* a cube root of
unity) and with `zeta3 = 1234` (cube 1799): **both CTRL-4 conditions report PASS
in both cases**, exactly as with the true `zeta3 = 1303`.

An assertion that passes when handed a value that is not a cube root of unity is
not an assertion about phi-invariance. The consequence is sharp: of the two
limbs of hypothesis D-3, **only the length limb was tested.** Any successor
sentence of the form "D-3 holds on committed code" without that qualification
would violate the batch's own prohibition against treating D-3 as established
beyond what the probe measures.

Note what the assertion structurally cannot see. The frozen `EXP-STR-004`
contract builds its whole ladder on the residue contrast, and says so: at
`B = 3q + 1` "the last phi-orbit is TRUNCATED to a single element whose
phi-image is not in F". CTRL-4 (ii) checks only *complete* blocks. At `B = 193`
the probe correctly records `tail_indices_not_in_a_complete_block: [192]` — and
checks nothing about it. The one structural variable the design exists to vary
is outside the assertion's field of view by construction.

### 1.2 The `len(F) != B` clause could not have fired at these parameters

The clause fires only if the builder exhausts `j < 50*B + 1000` before
accumulating `ceil(B/3)` whole orbits. Re-running the committed builder
read-only on CURVE-J12S1:

| B | draws consumed | trial bound | margin |
|---|---|---|---|
| 192 | 139 | 10600 | **76.3x** |
| 193 | 140 | 10650 | **76.1x** |

The instance affords **366 distinct full phi-orbits** (1099 liftable
x-coordinates). And because `a = 0`, the liftable set is *closed* under
`x -> zeta3*x` — `(zeta3*x)^3 + b = x^3 + b` — which I verified directly, so the
builder's per-member curve test never rejects an orbit. The builder first
returns a short list only at `B` of about **1142** on this instance.

So the tested `B` sits at roughly one sixth of the failure boundary, with a 76x
margin on the trial bound. **Ask what the quantity should have done.** `B` is the
parameter meant to destroy the length property. The measurement that would carry
information is a sweep in `B` up to and past the orbit supply, expected to hold
to `B ~ 1098` and fail above. Two adjacent PASSes near the bottom of the range
is the canonical artifact tell of `docs/inventor-protocol.md` §3: a flat quantity
where nothing was pushing on it.

What survives is real but small: at `e3cf9fdd`, on this instance, the builder
returns lists of length exactly 192 and 193. That is a fact worth having. It is
not a passed stress test.

### 1.3 `183` is `732 / 4`

`_collect_relations` generates targets by an arithmetic progression:

```python
k = (t_idx + 1) * max(2, inst.seed % max(2, n - 3)) % (n - 1) + 1
```

On CURVE-J12S1, `n = 733` and the derived seed is `100`, so the multiplier is
`c = 100` and `gcd(100, 732) = 4`. The progression visits exactly
`(n - 1) / gcd(c, n - 1) = 732 / 4 = 183` distinct `k` values. I confirmed by
direct computation that these give exactly 183 distinct target x-coordinates.

**183 is a divisibility accident of the derived seed against `n - 1`.** It is a
property of the target generator, not of the curve, the field, or either factor
base.

Consequences:

- At L192 (`Q = 202`) and L193 (`Q = 203`) **the quota is unreachable by
  construction.** `len(relations) = 183` is the generator's cycle length. Both
  arms hit `hits = attempts = 183`: every distinct target that exists decomposed.
  The loop's remaining 827 of 1010 iterations do nothing but `continue`.
- The censoring is far wider than the two headline cells. Of the 28 supply units,
  **24 report a saturated instrument constant**:
  - `len(relations) = 60 = Q` at L24, L25, L48, L49, A12M3, A13M3 — 12 units;
  - `= 106` or `107 = Q` at L96, L97, X96, X97 — 8 units;
  - `= 183` = target-cycle ceiling at L192, L193 — 4 units.
- **Only L12 and L13, both arms — four units — report an uncensored number.**

Any ladder across `B` built on those cells is confounded above the ceiling.

### 1.4 The null object is well built and was measured on a censored quantity

Credit where it is owed, because a fatigue report dressed as a negative result
is itself a defect. I read `harness/semaev.py::build_factor_base`, which
`_build_random_factor_base` delegates to: it returns `size` **distinct on-curve**
x-coordinates from the same `_seed_int` stream under the same trial bound. Arm
E-prime is matched to arm A-prime on size, liftability, determinism and seed
source, and differs only in phi-orbit structure. **This is a properly constructed
null object, not a strawman, and running it was right.**

But the identities a successor will notice — 60/60, 106/106, 107/107, 183/183 —
all occur at units where §1.3 shows the quantity is clamped. **Two arms cannot
differ on a number that is pinned.** Those identities are *forced*; they are not
a controlled null.

And the instrument is demonstrably *not* blind to the arm. Where the clamp does
not bind:

| cell | A-prime | E-prime | quantity |
|---|---|---|---|
| L12 | 29 | 17 | `len(relations)` |
| L13 | 31 | 20 | `len(relations)` |
| L24 | 150 | 132 | targets consumed to fill quota |
| L25 | 139 | 129 | targets consumed |
| A12M3 | 82 | 104 | targets consumed |
| A13M3 | 75 | 95 | targets consumed |
| X96 | 289 | 296 | targets consumed |

Seven separations, and (reading "fewer targets for the same quota" as the same
direction) six of seven point the same way. **This report declines to call that a
finding** — the batch forbids an arm comparison, it is one instance and one
realisation, and the control that would separate an orbit-structure effect from
a plain coverage effect has not been run. But the honest reading is *the
quantity is censored*, **not** *the arms are indistinguishable*. A successor who
reads `183/183` as a controlled null is reading the clamp.

### 1.5 The one real test in the probe

The supply clause needed `max(0, R_base(B) - len(relations)) >= 2` somewhere.
Unlike §1.1 and §1.2 this was **not** analytically dead. The tightest unit is
L12/arm_E_prime: `R_base = 5`, so firing required `len(relations) <= 3`; observed
17. At `B = 12` and `m = 2` the pair-coverage heuristic gives no a-priori
guarantee, and E-prime landed within a factor of 5.7 of firing. **This limb was a
genuine test with a wide margin, and it was passed.** It should be reported with
the margin quoted — "the tightest unit was L12/arm_E_prime at 17 against
`R_base = 5`" — and never as the bare phrase "the falsification condition
passed".

---

## 2. Was the condition reinterpreted? (gate G2)

**No.** Commit order checked against git, not taken on assertion:

| commit | time | content |
|---|---|---|
| `d0bdec84` | 2026-07-30 18:14:54 -0700 | BATCH-015 opening; freezes `PRE_REGISTERED_FALSIFICATION_CONDITION` |
| `085f5d48` | 18:25:00 -0700 | QUEUE-AMEND-20260730-001/-002 |
| `e3cf9fdd` | 18:33:52 -0700 | probe artifacts |

The condition precedes the probe by nineteen minutes and two commits.

`probe_driver.py::finish()` implements exactly two clauses — `returned_length !=
B` over valid PART A assertions, and `shortfall >= 2` over valid PART B records
with `shortfall = max(0, R_base_recomputed - len(relations))`. No other
threshold, no other comparison, no other scope. A shortfall of **one** is
tolerated exactly as the arm E-prime limb declares. Infrastructure-failed and
budget-cancelled units are excluded and named rather than scored as zeros, which
is correct under AGENTS core rule 5 — and in this run there were none.

**No artifact of this batch applies a different threshold, comparison or scope.
Not a blocking finding.**

---

## 3. Prohibition list, item by item (gate G3)

Method: recursive grep over every BATCH-015 artifact for each prohibited
construction, plus a manual read of the eight probe artifacts and the snapshot
receipt.

| # | Prohibition | Result |
|---|---|---|
| 1 | H-STR-002's mechanism tested/confirmed/refuted by BATCH-014 or -015 | **No violation.** `probe_manifest.what_this_is` states the negative. |
| 2 | Low alpha on a shift-closed row list cited as confirming H-STR-002 | **No violation.** No alpha computed; the only `alpha` token in the probe tree is the driver's own prohibition docstring. |
| 3 | Asserting in either direction that `phi_alpha` is an artifact of the row-insertion rule | **No violation.** No closure invoked; `include_phi_orbits` recorded `False` at all 28 units and 4 determinism repeats. |
| 4 | Promoting the reserved KN-FIND-010 sentence in its present wording | **No violation.** Appears only inside the prohibition text. |
| 5 | DEFER-BATCH009-001 described as discharged; D-3 established beyond measurement; RT-CM-1..6 addressed; UC-3..7 repaired | **No violation in the artifacts**, but see §1.1 — D-3 has two limbs and only one was reached. Flagged forward. |
| 6 | EV-STR-001's yield penalty quoted as 17.5x alone | **No violation.** Every occurrence in the batch tree is the full range 17.5x–4128.6x inside the prohibition text. |
| 7 | C-20 power sentence without RT21-1; PDC-15's "better than 3.2e-5"; the deviation count of eight; any EXP-YIELD-002 difference column | **No violation.** None appears in any probe artifact. |
| 8 | Issuing RT-20260729-036 to any report | **No violation, and this report mints no `RT-*` identifier at all.** |
| 9 | Stating or implying that the ledger validates | **No violation.** INT-BATCH012-F is carried unrepaired and no artifact contradicts it. This report does not state or imply that the ledger validates. |

No offending text to quote.

---

## 4. Re-adjudication of BATCH-014 (gate G4)

**No instance found.** No BATCH-015 artifact argues for or against
`DEC-20260729-004` `refine`, the TASK-20260729-042 REVISE contract review, the
TASK-20260729-043 NOT APPROVED determination or the QUEUE-AMEND-20260729-005
stand-down. No artifact treats `EXP-STR-004` as approved. No artifact treats it
as ambiguous between the two frozen copies — the probe cites the committed path.
The four are carried as committed facts. **Nothing blocking.** This report does
not reopen them either.

---

## 5. Claim-ceiling audit

I looked specifically for drift toward alpha, closure, rank, diagnosticity,
solvability, cost, or H-STR-002's mechanism; for toy-scale results presented as
broader; and for any implication that DEFER-BATCH009-001 is discharged or
EXP-STR-004 approved.

**The committed artifacts and the snapshot receipt are clean on all seven.** Wall
clock and RSS are labelled budget accounting in three separate places; `run_ids`
is empty with its reason stated; the certificate block says no certifiable claim
is made rather than emitting an empty certificate; the queue's cell table was
recomputed rather than adopted and `table_disagreements` is empty. The Executor
exercised real discipline and this report records that plainly rather than
manufacturing a breach.

The exposure is downstream, not upstream. §1.1, §1.3 and §1.4 name the three
sentences a successor is likely to write that *would* breach the ceiling.

---

## 6. Process findings

### 6.1 The two amendments were schema repairs — verified, not accepted

`git diff d0bdec84 085f5d48` is **pure addition**: 274 insertions, zero
deletions, over `dispatch_queue.json` (+77) and the two newly rendered
`dispatch_plan` files. The additions are two task-level `archive` objects for the
two Coordinator archive cards; `ledger/evidence/EV-STR-005.yaml` added to
TASK-035's `artifact_paths` with `EV-STR-005` in its `record_ids`; and the two
amendment records themselves. **No task's objective, constraints, budget,
read_scope, write_scope, completion_gate or inference block changed. The
falsification condition text, the claim ceiling, the fourteen cells, the two arms
and the executor card are byte-identical across the amendment.** Neither
amendment materially altered what the batch could conclude.

One forward hazard follows. `tools/research_dispatch.py::_validate_ledger_archive`
requires *unconditionally* that a `ledger` archive declare a path under
`ledger/evidence/`. So a dispatcher schema now asserts, structurally, that an
evidence record will exist for a batch whose own ceiling says it produces no
result. The amendment names and forbids the obvious failure ("NO EVIDENCE RECORD
MAY BE WRITTEN UNDER BRANCH 2 IN ORDER TO MAKE A DECLARED PATH COUNT COME TRUE"),
and declare-then-deviate is pre-registered with BATCH-014's TASK-20260729-048 as
precedent. **TASK-20260730-035 must exercise that route and record the shortfall
rather than write a record to satisfy a path count.** A live hazard, not a breach.

The queue's own standing lesson — a queue never passed through
`tools/research_dispatch.py` is an unverified artifact — is correct and is
endorsed here.

### 6.2 The discarded duplicate: no dependency, but a demonstrated ambiguity

Checked by diff, not assumed. **In the committed `EXP-STR-004/specification.yaml`,
`CTRL-4` is the factor-base structure assertion. In the discarded duplicate,
`CTRL-4` is a different control entirely — "RESIDUE CONTRAST AT EVERY RUNG" — and
that copy has no `the_fourteen_named_cells` block at that location.**

Nothing in BATCH-015 depends on the discarded artifact: the probe recomputed
`R_base` and `Q` from the formulas and recorded no disagreement, and I
independently confirmed the fourteen cells and the CTRL-4 text in the *committed*
copy match what the queue carried and what the driver executed. The
`structure_probe.json` authority field cites the path, which resolves
unambiguously on this branch.

But the bare identifier `CTRL-4 of EXP-STR-004` is now **demonstrably** ambiguous
across two frozen copies. Every successor citation must carry a commit sha.

### 6.3 What the shared-model fallback costs

The producing Executor (TASK-20260730-031), the Validator (TASK-20260730-033) and
this Red Team all resolve to `claude-opus-5`, with `fallback_used: true` and
`model_verified: false` on each. Session independence is asserted; **model
independence is unavailable and is nowhere claimed.**

The concrete cost is *correlated blind spots*, not laziness. An executor that
implements a check by transcribing the constructor's own expression, and a
reviewer on the same model who reads the check and finds it faithful to the
contract, will agree — correctly about fidelity, wrongly about informativeness.
**§1.1 is exactly that failure.** I did not find it by reading. I found it by
re-executing the committed builder with a bogus `zeta3` and watching the
assertion pass.

The mitigation costs no model diversity and should become standing practice:
**require a mutation test for every assertion-style control.** A control that has
never been shown to *fail* on a deliberately broken input is not known to be a
control. Mutation evidence is model-independent in a way that cross-reading is
not.

---

## 7. Pareto position

`dominated_by` was checked against every axis and is **not** `null` — an
unchecked `null` there would be a fabrication under AGENTS rule 5.

- **Time:** no time figure is produced. The 2.05 s of PART B is budget accounting
  and is explicitly not a cost measurement. `sota_delta = 0`.
- **Memory:** no memory figure is produced. The 76 MB peak RSS is budget
  accounting. `sota_delta = 0`.
- **Data / queries:** none produced. `sota_delta = 0`.
- **Exponent:** none moved, approached or bounded in either direction.
  `sota_delta = 0`.

`dominated_by`: Pollard rho with the order-3 automorphism (Wiener–Zuccherato;
Duursma–Gaudry–Morain), the closest specialized baseline for `j = 0` curves;
plain Pollard rho; BSGS. All dominate trivially, because the probe offers no
figure on any axis. Within this campaign, EV-STR-001 and EV-STR-003 dominate too:
they at least measured quantities on this instrument, whereas this probe measures
the instrument.

**The only reproducible speedup measured anywhere in this lineage is the
classical constant factor `r = 3`, which is already the specialized baseline
rather than an improvement on it, and a constant factor is NOT target-class under
`docs/target-result-profile.md` rule A1** — A1 asks for movement of the
asymptotic exponent, and a constant leaves the exponent of `sqrt(n)` exactly
where it was. BATCH-015 is admitted only under A1's building-block clause. This
report agrees with the queue's own self-assessment on that point and does not
soften it.

---

## 8. Controls (gate G5)

| id | control | dispatch? |
|---|---|---|
| CTRL-RT034-A | **Mutation test of CTRL-4.** Re-run the assertion against (1) a non-cube-root `zeta3`, (2) one block element replaced, (3) two blocks interleaved; require FAIL on each. Milliseconds, ~10 lines, no new cell, no closure, no cost quantity. **The cheapest discriminating control in this review** — it decides whether "CTRL-4 passes" ever meant anything. Case (1) already run and reported in §1.1. | **YES — in a successor.** Not here; this task may not enlarge the batch. |
| CTRL-RT034-B | **Decensor the headline cells.** At L192/L193, either vary the progression multiplier so `gcd(c, n-1) = 1` (needs a versioned protocol amendment, since it changes committed behaviour), or report the cell as censored with the ceiling quoted (free, prose only). | **YES — in a successor.** Option (b) immediately at zero cost; option (a) only under an amendment. |
| CTRL-RT034-C | **Report the uncensored supply quantity.** Use the `hits` and `attempts` the committed loop already returns and the probe already recorded, instead of a `len(relations)` clamped at `Q`. Not a cost quantity, not a ratio, not a rate claim — two counts. | **YES — in a successor.** Zero additional compute; the numbers are already committed at `e3cf9fdd`. |
| CTRL-RT034-D | **Builder failure-boundary sweep.** Locate the first `B` at which the builder returns short, so future D-3 assertions sit at a known distance from a known boundary. Expectation ≈ 1142 on CURVE-J12S1 (red-team diagnostic, **not** a batch measurement and **not** evidence). | **YES — in a successor.** Seconds of compute. |
| CTRL-RT034-E | **Cross-curve breadth extension** — repeat the fourteen cells on more `j = 0` seeds. | **NO — I would not run this, and I name it so my recommendation is falsifiable.** It multiplies censored numbers: 24 of 28 units are saturated. Decensoring strictly dominates it. Reconsider only afterwards. |

No control named here is dispatched by this task, no new card is proposed, and
**no approval or execution of `EXP-STR-004` is recommended** — it is not this
batch's to approve.

---

## 9. Verdict, and what would falsify it (gate G6)

**The probe is sound as executed and over-read as framed.**

- *Was the falsification condition capable of failing?*
  - `len(F) != B` — capable in principle, **dead in practice**: 76x trial-bound
    margin, failure boundary at `B ≈ 1142` against a tested `B` of 192/193.
  - The CTRL-4 block identity — **not capable at all**, at any `B`, on any curve,
    with any `zeta3`. It is a constructor identity. Note carefully that
    condition (ii) is *not* part of the pre-registered falsification condition,
    which cites only `len(F) != B`; so this does not impugn the condition. It
    impugns the headline sentence "both structure assertions PASS", which is
    where the information content is silently zero.
  - `shortfall >= 2` — **genuinely capable**, cleared by a factor of 5.7 at the
    tightest unit. This is the one real test in the probe, and it was passed.

- *Does the output support reopening the execution question on the merits?*
  **No — and this is said plainly rather than by manufacturing an objection.**
  The pre-registered disposition made reopening contingent on the condition
  *firing*, and it did not. Nothing measured here shows the stand-down's basis
  defective in substance. Equally, nothing here supports approving anything.

- *Is this a closure?* **No, in either direction.** This report closes no lane,
  names no obstruction and declares nothing dead. Premature closure is a failure
  mode symmetric with overclaiming, and a count of instrument checks is not a
  statement about the endomorphism lane's mathematics.

**What would falsify my own recommendation:**

1. **SELF-F1** — exhibit any `(inst, B, zeta3)` for which the committed builder
   returns a list whose complete blocks violate the identity. I claim none exists
   because `xs.extend(orbit)` is the only mutation of `xs` and `xs[:B]` preserves
   whole leading triples. One counterexample and §1.1 falls entirely.
2. **SELF-F2** — show the distinct-target count stays 183 when the multiplier `c`
   is varied so `gcd(c, n-1)` changes. If 183 survives, it is not `732/4` and
   §1.3 is wrong.
3. **SELF-F3** — show `len(F) != B` is reachable near `B = 192` on some *other*
   declared curve. I swept only CURVE-J12S1; if such a curve exists, §1.2 weakens
   to "dead on one curve, live on another".
4. **SELF-F4** — demonstrate a third clause in the preserved condition text that
   I missed and that the committed data trips. I read `finish()` line by line and
   found exactly two. If there is a third and it fires, reopening is owed and my
   verdict is wrong.

**Dissents, recorded verbatim in `red_team_report.yaml`,** including two against
my own recommendation and one against my own clean claim-ceiling bill:
DISSENT-1 (the seven consistent arm separations I declined to call a finding),
DISSENT-2 (CTRL-4 should perhaps be deleted rather than repaired), DISSENT-3
(a document that must deny eleven claims is positioned close to all eleven).

**Next concrete action.** TASK-20260730-035 should record, in the
`DEC-20260730-031` scope text and in any `EV-STR-005` it writes, the single
sentence that **CTRL-4 condition (ii) is an identity of
`_build_phi_invariant_factor_base` and establishes no property of the factor
base, and that 24 of the 28 supply counts are clamped at `Q(B)` or at the
183-target cycle ceiling.** That one sentence is what stops the next Coordinator
banking a tautology and a clamp as two settled facts.

---

## 10. Bounded-card disclosure (gate G9)

Not reached inside the 2400 s cap, named rather than hidden:

- The builder failure-boundary sweep was run on **CURVE-J12S1 only**. My §1.2
  margins do not cover CURVE-J16S3; SELF-F3 names that as a live falsifier of my
  own objection.
- `ledger/hypotheses/H-STR-002.yaml` and `ledger/decisions/DEC-20260729-004.yaml`
  were **not read in full**. I checked for re-adjudication by grep across the
  BATCH-015 tree and found none, and I neither relied on nor disputed the content
  of either record. UC-7's record that FC-1 is ambiguous as drafted is carried
  unresolved and is not resolved by this batch or by this report.
- The BATCH-014 TASK-20260729-046 validation report (narrowings N1–N8) and the
  TASK-20260729-047 red-team report were **not read in full**; I worked from the
  queue's carried text of RT35-CTRL-1, RT35-CTRL-2 and the third dissent. If any
  of N1–N8 contradicts something here, that document governs and this is a gap in
  my review.

No commit was made by this session. Nothing was written outside
`coordination/goals/GOAL-ECDLP-001/batches/BATCH-015/reviews/TASK-20260730-034/`.
Both files are archived by TASK-20260730-035.
