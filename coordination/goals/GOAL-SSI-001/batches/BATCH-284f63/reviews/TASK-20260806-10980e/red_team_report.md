# Red-team report — TASK-20260806-10980e (BATCH-284f63, GOAL-SSI-001)

Independent session. I did not produce `EXP-SSI-9b542d` or `repair_report.md` and I repair
neither. I change no status, edit no raw artifact, and commit nothing. All numbers below
were recomputed by me in a scratch Python process from the literal formulas and literal
frozen values in the reviewed files — not copied from `repair_report.md`'s tables.

## 0. Snapshot binding, independently verified

Receipt: `coordination/goals/GOAL-SSI-001/batches/BATCH-284f63/archives/TASK-20260806-b03b21/snapshot-receipt.json`,
commit `966a46c5`. I recomputed both declared hashes directly against the working tree at
that commit:

| path | receipt sha256 | recomputed sha256 | match |
|---|---|---|---|
| `experiments/EXP-SSI-9b542d/specification.yaml` | `e73c63dc…82d8cf0bf` | `e73c63dc…82d8cf0bf` | yes |
| `.../TASK-20260806-55cf1f/repair_report.md` | `0c7aca37…07f7b725d` | `0c7aca37…07f7b725d` | yes |

`git show 966a46c5 --stat` shows the commit adds only the receipt file plus (in the same
commit) an unrelated ECDLP receipt; content-verified per `research_dispatch.py`'s stated
binding rule. `verification.status: pending_post_commit` remains open for the Coordinator's
post-commit verifier; that is outside this task's write_scope.

---

## 1. THE BOUNDARY CONDITION (Fix 1) — independently recomputed: HOLDS EXACTLY

`MC_P13_CORRECTED.formula`, as literally written in the spec:

```
T_A(P, w) = L_paper(P) + E(P) + S + c*sqrt(P) + A + 0.5*max(0, L_mem(P) - log2_w)
```

At `log2_w = L_mem(P)` (`w = M`): `max(0, L_mem(P) - L_mem(P)) = max(0,0) = 0`, so
`T_A(P, L_mem(P)) = L_paper(P) + E(P) + S + c*sqrt(P) + A = T_full(P)` identically for every
`S, A, c`, and every per-entry law (none of these parameters appear inside the `max(...)`
term). I evaluated this in Python for all five committed `P` and law `L1`, `S=A=c=0`:

| P | T_full(P) | T_A(P, L_mem(P)) corrected | residual |
|---|---|---|---|
| 256 | 118.461337 | 118.461337 | **0.0** (to float precision) |
| 384 | 170.046299 | 170.046299 | **0.0** |
| 512 | 217.161337 | 217.161337 | **0.0** |
| 576 | 244.031262 | 244.031262 | **0.0** |
| 768 | 315.946299 | 315.946299 | **0.0** |

**Confirmed exactly as claimed**, both algebraically and numerically. This is a correct fix
of the defect (`T_full/sqrt(min(w,M))` in `EXP-WESOVOW-001/cost_model.py` line 236 and
`MC_P13` in `EXP-SSI-697354` both take the sqrt of a raw memory *count*, not a *ratio*, and
neither reduces to `T_full` at `w=M`).

One notational flag, not a computational defect: `cost_functions.assessed_method_cost.
MC_P13_CORRECTED.equivalent_form` writes `T_A(P,w) = T_full(P) * 2^{0.5*max(0, log2 M -
log2 w)}` — reusing the symbols `T_A`/`T_full` for *linear* cost in that sentence, while
`formula:` two lines above uses the same symbols for *log2* cost (additive). The algebra is
consistent once you substitute correctly (I verified both readings agree), but a reader who
does not substitute carefully could momentarily read it as a second, additive-vs-multiplicative
contradiction inside the same block. Cosmetic; recommend disambiguating the symbol reuse in
a future version.

---

## 2. THE REPRODUCTION GATE (Fix 2) — independently recomputed: MATCHES

Configuration as declared: `log2 p = 256`, `log2_w = 1000` (`memory_grid.
unbounded_memory_representation`), memoryless baseline, `c = 0`. I re-derived `E(256)` for
all four laws from the frozen `a1..a4` fit coefficients (`E1(P)=log2(a1*P)`, etc.) and
`T_A = L_paper(256) + E(256) + S + A` (penalty is `0` since `1000 >= L_mem(256)=92.5`):

- `E(256)`: L1=11.961337, L2=12.017922, L3=12.068995, L4=12.024756 (spec's frozen values:
  11.961328 / 12.017922 / 12.069019 / 12.024751 — agreement to ≤3e-5 bits, consistent with
  6-decimal rounding of `a1`/`a3`; not a defect).
- **RG-1** (S=0,A=0): band `[118.461337, 118.568995]` ⊂ `[118.25, 118.75]`. PASS.
- **RG-2** (S=3,A=0): band `[121.461337, 121.568995]` ⊂ `[121.25, 121.75]`. PASS.
- **RG-3** (A=1.584963): `[120.046301, 120.153958]` ⊂ `[119.9, 120.4]` and `[123.046301,
  123.153958]` ⊂ `[122.9, 123.4]`. PASS.
- **RG-5**: I scanned all 4 laws × 2 S × 4 A at c=0 myself: **min gap = 2.524114** (L3,
  S=3.0, A=3.906891), **max gap = 11.275629** (L1, S=0, A=−1.736966). Span
  `[2.524114, 11.275629] ⊇ [6, 11]` — PASS, and this independently reproduces
  `EV-SSI-455241`'s cited `2.5241`/`11.2756` to 4 decimal places.

**The band is a genuine consequence of the corrected formula, not a copy-forward of the
rejected contract's numbers**, confirmed by direct recomputation from the T1/T2 literals in
this specification, not from `repair_report.md`'s printed table.

---

## 3. THE CENTRAL QUESTION — is `BOUNDARY-CONDITION-GATE` capable of failing? YES, for the
exact defect class that got the predecessor rejected. Verified both ways, independently.

First I confirmed `MC_P13_SUPERSEDED_do_not_use` in the new spec is a **verbatim
transcription** of `EXP-SSI-697354`'s actually-committed, actually-rejected `MC_P13`
(`experiments/EXP-SSI-697354/specification.yaml:304`: `T_A(P,w) = ... - 0.5*min(log2_w,
L_mem(P))` — identical string). This is not a straw model; it is the program's own prior
artifact.

I evaluated **both** BCG-1 (corrected) and BCG-2 (superseded) at `w = L_mem(P)` for all five
committed rows, from the formulas as written, independent of `repair_report.md`:

| P | L_mem(P) | BCG-1 residual (corrected) | BCG-2 residual (superseded) | claimed BCG-2 |
|---|---|---|---|---|
| 256 | 92.5 | 0.0 | 46.25 | 46.25 |
| 384 | 138.6 | 0.0 | 69.3 | 69.3 |
| 512 | 181.3 | 0.0 | 90.65 | 90.65 |
| 576 | 206.0 | 0.0 | 103.0 | 103.0 |
| 768 | 272.2 | 0.0 | 136.1 | 136.1 |

Exact match, all five rows, and each residual equals `0.5*L_mem(P)` exactly, as claimed.
**BCG-1 passes (0.0, eight-plus orders of magnitude inside the 1e-9 tolerance) and BCG-2
fails (46–136 bits, eight-plus orders of magnitude outside it) — a genuine, non-degenerate
pass/fail pair, both computed independently by me, not merely asserted.**

I also independently re-derived the report's differential-slope argument (§3.1 of
`repair_report.md`), by direct differentiation rather than trusting the prose: below the
clamp (`log2_w < L_mem(P)`), corrected term `= 0.5*(L_mem(P)-log2_w)` has slope `-0.5`;
superseded term `= -0.5*log2_w` also has slope `-0.5`. **Identical slope, differing only by
the constant `0.5*L_mem(P)`.** `d(constant)/d(log2 w) = 0`, so MONO-1..4 and SANITY-1 (all
differential) are provably blind to this exact defect class by construction — this is a
correct, checkable claim, not hand-waving.

**Verdict on the central question: the binding defect (control incapable of returning a
negative about the mathematical object) is fixed *for the specific defect class that got
`EXP-SSI-697354` rejected* — a constant, w-independent additive/subtractive anchor error.**
`BOUNDARY-CONDITION-GATE` demonstrably discriminates between the two competing formulas the
program has actually proposed, on the frozen committed inputs, with a tolerance eight orders
of magnitude tighter than the defect it targets.

### 3a. Scope limit on that verdict — construct the cheapest counterexample

`BOUNDARY-CONDITION-GATE` tests a *single point* (`w=M`) against a *single* named alternative
model. It is not a general-purpose falsifier of "any wrong cost model." Two cheap
constructions show the edge of its coverage (both would need to be caught, if at all, by the
*other* controls, not by BCG):

1. **Sign-flipped clamp inside `max`.** A mutated formula `0.5*max(0, log2_w - L_mem(P))`
   (direction reversed) gives `max(0,0)=0` at `w=M` too — BCG-1 would falsely **pass** this
   badly-wrong model. I confirmed this is nonetheless caught elsewhere: this mutation makes
   `Delta`'s slope `+0.0` below the clamp and `-0.5` above it, which is exactly backwards from
   `MONO-1`'s required `+0.5`/`0.0` pattern — so `MONO-1` (not `BCG`) is the control that
   catches this specific mutation. Coverage survives, but only because two controls are
   combined; `BCG` alone does not.
2. **Memory-blind model** (`T_A(P,w) = T_full(P)` for all `w`, no penalty term at all) also
   trivially satisfies BCG-1 at `w=M` (residual `0` by definition, since there is no `w`
   dependence to fail). This is caught by `MONO-1`'s slope requirement (`+0.5` expected,
   `0` observed) and by `MONO-4` (no divergence from `MC_VOW`), not by `BCG`.

Neither of these is a gap in the *repair as delivered* — `MONO-1/2/4` remain in the contract
unmodified and do the complementary job, and `repair_report.md` never claims `BCG` subsumes
them. But the spec's own `can_this_control_fail` text for `BOUNDARY-CONDITION-GATE` should be
read narrowly: it is proven capable of catching *the historical anchor-offset class*, not
capable of catching every plausible wrong model in isolation.

### 3b. A genuine inconsistency in the new spec's own self-description of `RG-REPRODUCTION-GATE`

`RG-REPRODUCTION-GATE.can_this_control_fail` (spec, `controls[0]`) states: *"this control's
tolerance windows are wide enough that a CONSTANT offset in the memory term at unbounded
memory (exactly the class of bug that got EXP-SSI-697354 rejected) does NOT necessarily move
any of RG-1..RG-5 outside their bands, because those bands were never actually sensitive to
the memory term at log2_w=1000 in either formula version."*

I checked this directly against the superseded formula at `log2_w=1000`: `min(1000,
L_mem(P)) = L_mem(P)` for every committed row (since max `L_mem` is 272.2 ≪ 1000), so the
superseded formula's memory term at "unbounded" memory is **not** zero — it is
`-0.5*L_mem(P)`, i.e. exactly the 46.25–136.1-bit deviation in the table above. Evaluated
against RG-1's band `[118.25, 118.75]`, the superseded formula at NIST-I gives
`T_A(256,1000) = 118.461337 - 46.25 = 72.211337`, which is **72 bits (not 0.5 bits) outside
the band** — this is precisely `EV-SSI-455241` OBJ-1's own dispatcher-verified finding
(`T_A(256) = 72.2113` against `[118.25, 118.75]`), cited elsewhere in this same repaired
spec's provenance notes. **The literal sentence quoted above therefore appears to be false**
for the superseded formula: RG-1..5's bands are, and historically were, highly sensitive to
this exact defect at "unbounded" memory — that sensitivity is what caused OBJ-1 in the first
place. The charitable reading is that the sentence means "the *design-time hand-computed
numbers used to set the band* were derived without plugging the buggy formula through" (which
`repair_report.md` §3.1 states more carefully and correctly), not "the band cannot detect the
bug at runtime" (which is demonstrably false). As written in the frozen spec, the sentence is
ambiguous-to-incorrect and should be corrected before a Validator or Coordinator relies on it
to characterize `RG-REPRODUCTION-GATE`'s discriminating power.

---

## 4. Per-control capable-of-failing verdict, computed pass/fail case for each

Per the task's instruction, I constructed or identified a pass case and a fail case for
**every** control in the new contract, distinguishing "capable of failing given a
counterfactual mutated input" from "capable of failing given the actual frozen, committed
inputs that will be dispatched" — the latter is the sharper test and is what
`EV-SSI-455241`'s "zero of fourteen" finding was actually about.

| control | pass case (computed) | fail case (constructed) | fails on *frozen* committed data? |
|---|---|---|---|
| `RG-REPRODUCTION-GATE` (RG-1..5) | verified §2 above, all PASS | a mutated `a1` (e.g. +5%) moves `E(256)` outside the 0.5-bit window — constructed, not evaluated on real data | **NO** — same as predecessor; frozen data is not close to any threshold |
| `NULL-OBJECT` | `D_null0(256)=E(256)≈11.96–12.07` bits, inside preregistered `[11.9,14.2]` | `E(P) < 1.0` bit would trip F4; `E(P) <= A_conversion` would trip F6 — neither reachable by the committed T1 fit (E≈12 throughout) | **NO** — `EV-SSI-455241` already found F4 would require `E<0.0039` and F6 `E<=4.9`; unaffected by this repair |
| `MONO-1` (slope) | corrected slope verified `+0.5`/`0.0` above §3 | sign-flipped or missing-clamp implementation — constructed in §3a | **YES, on an implementation bug**, not on data |
| `MONO-2` (kink location) | kink at `L_mem(P)` by construction | dropped `max(0,.)` clamp produces no kink | **YES, on an implementation bug** |
| `MONO-3` (locus direction) | reports `NOT_EVALUABLE` correctly when <2 loci exist (by design, never vacuously "pass") | a genuine wrong-direction move — data/formula dependent | contingent, not testable by hand here |
| `MONO-4` (MC differ ≥0.5 bit) | `MC_P13_CORRECTED` and `MC_VOW` structurally diverge (memory term on opposite sides) | identical surfaces — would need both formulas coded identically | **NO** — structurally guaranteed apart given the two adopted formulas |
| `MONO-5` (data monotonicity) | verified `L_paper`, `L_mem` strictly increasing across all 5 rows; `L_paper(P)-P/3` in `[21.17,46.4]` ⊂ `[21,47]` | a non-monotone T2 column — data property, not reachable on the committed, already-transcribed table | **NO** — same as predecessor, data is fixed and monotone |
| `FITTED-WINDOW-GUARD` | every emitted cell stamped with extrapolation ratio | an implementation that omits a stamp on one cell | **YES, on an implementation omission** |
| `ADVERSARIAL-CORNER` | reports the pure-RAM corner value alongside `MC_VOW` comparison | a headline surviving the median grid but not the corner — data/formula dependent, not evaluated here | contingent |
| `SANITY-1-MODEL-COHERENCE` | sign of `dT_A/d(log2 w)` verified negative-cost-with-more-memory (physically correct) for **both** corrected and superseded formulas (§3) | self-disclosed as unable to catch OBJ-2 — confirmed by my own derivative check in §3 | **NO on the anchor-offset class — the spec is honest about this** |
| `BOUNDARY-CONDITION-GATE` (BCG-1/BCG-2) | BCG-1 = 0.0 exactly, all 5 rows (§3) | BCG-2 = 0.5·L_mem(P), 46.25–136.1 bits, all 5 rows (§3) | **YES — the one control whose fail branch is reached on the actual frozen, committed formulas and data**, verified independently |

**Bottom line on Fix 3**: of the fourteen-plus assertions carried into this contract, the
same roughly dozen inherited from `EXP-SSI-697354` remain — as before — essentially
guaranteed to pass on the *frozen, already-committed* T1/T2 data (their failure thresholds
are numerically unreachable by the committed numbers, exactly as `EV-SSI-455241` found).
`BOUNDARY-CONDITION-GATE` is the **one** new control whose fail branch (`BCG-2`) is actually
reached, deterministically, on the frozen inputs — because it varies the *formula* itself as
the free variable (the exact axis the anchor bug lives on) rather than varying data or
implementation wiring. That satisfies DEC-20260806-a00a28's "at least one" requirement, for
the exact defect class named. The Coordinator's closure decision should say this precisely —
"one control now object-level-capable, for the anchor-offset class; the other dozen remain
data-driven-unreachable, as before" — rather than implying the whole control set is now
healthy.

---

## 5. Withdrawn IDEA-20260806-62ba9d figures — not reintroduced

`grep -n "1\.585\|2\.585\|32%\|43%"` across `specification.yaml` and `repair_report.md`
returns exactly two hits, both inside `claim_ceiling.forbidden_sentences`, explicitly
*naming* the withdrawn figures in order to forbid citing them — not citing them as live.
Confirmed clean.

---

## 6. Runnability — verified by actual execution, not by inference

The repair task's own dependency-verification section states it "could not [attempt the
import] first-hand" because its tool surface (Read/Grep/Glob/Write/Edit) has no code
execution. I have Bash and ran the check directly in this environment:

```
re          PRESENT
ast         PRESENT
math/json/os/sys/time/hashlib/statistics/platform/importlib   PRESENT
numpy       ABSENT
sympy       ABSENT
sage/g6k/fpylll/scipy/mpmath                                   ABSENT
python3 --version -> 3.11.15
```

This **confirms** `dependency_contract.stdlib_modules_permitted` includes `re`/`ast` in the
spec text (`experiments/EXP-SSI-9b542d/specification.yaml:156`) and **confirms** the
repair's inferred conclusion (language-spec guarantee + corroborating imports elsewhere in
the repo) was correct, with a stronger form of evidence than the repair task itself could
produce. `optional_permitted`/`forbidden` correctly scope numpy to `XCHK-2` only; I grepped
every other `numpy` mention in the spec and confirmed none of them touches a primary-path
reported number.

---

## 7. Scope discipline (Fix per DEC-20260806-a00a28, unnamed but load-bearing)

I independently recomputed the SCOPE-B per-axis gap from `T_full(P)` at `S=A=c=0`, law `L1`,
against `2^128`/`2^192`/`2^256`:

- NIST-I: `128 - 118.461337 = 9.538663` bits (spec: `9.5387`)
- NIST-III: `192 - 170.046299 = 21.953701` bits (spec: `21.9537`)
- NIST-V: `256 - 217.161337 = 38.838663` bits (spec: `38.8387`)

Matches to 4 decimals, and confirms the gap **grows** with level. `claim_ceiling.
forbidden_sentences` correctly forbids the unqualified "NIST-III/V retain margin" sentence
and requires the axis to be named. Confirmed present, not the withdrawn framing.

**One carried, undisclosed gap in the new spec** (not one of DEC-20260806-a00a28's four named
fixes, so not a repair-completeness failure, but worth recording): `EV-SSI-455241` separately
found "SCOPE-A and SCOPE-B are numerically identical at log2 k_DG=0, so the contract's Q5
counts one observation twice" — because `L_prev(P)` (the paper's own previous-methods column)
equals the level's own NIST target bit-count exactly (`L_prev(256)=128=2^128` target, etc.),
which I confirmed directly from the T2 table. The new spec's `scope_statement` still lists
SCOPE-A and SCOPE-B as if independent axes and does not carry this caveat forward the way it
explicitly carries the `MC_VOW` misattribution caveat. This is a genuine, still-open,
undisclosed finding from the predecessor review that this repair silently drops rather than
flags — low severity (out of the four named fixes), but should be named in the ledger
archive's decision text rather than left implicit.

---

## 8. Fix 4 mechanical — confirmed

`stdlib_modules_permitted` includes `re, ast` (line 156, verified above). `memory_grid.
w_grid_log2` (14 values) is now a literal field in the frozen spec, and I confirmed it
matches `H-SSI-7fe2bf.yaml:500`'s `log2_w_grid` list value-for-value
(`[20,25,30,35,40,50,60,70,80,92.5,138.6,181.3,206.0,272.2]`), so no drift was introduced
while relocating it.

---

## 9. Objections summary by severity

**HIGH**: none. No defect found that would, on its own, invalidate the repair's central
claim.

**MODERATE**:
- §3b: `RG-REPRODUCTION-GATE.can_this_control_fail`'s literal claim that RG-1..5 were "never
  actually sensitive to the memory term at log2_w=1000 in either formula version" is false
  for the superseded formula, contradicting the record's own dispatcher-verified OBJ-1
  finding (72.2 vs. `[118.25,118.75]`, a 46-bit deviation). Should be corrected before the
  Coordinator's ledger archive cites this control's characterization as accurate.
- §4: the dozen controls inherited unmodified from `EXP-SSI-697354` remain, as before,
  essentially unreachable-to-fail on the frozen committed data. This is consistent with
  DEC-20260806-a00a28's "at least one" bar (satisfied by BCG), but the ledger decision should
  say this precisely rather than imply the whole control set is now healthy.

**LOW**:
- §1: cosmetic notational reuse of `T_A`/`T_full` for both log2- and linear-cost forms in
  `equivalent_form`.
- §3a: `BOUNDARY-CONDITION-GATE` covers one point and one named alternative model; a
  sign-flipped-clamp or memory-blind mutation would pass BCG-1 and must be (and is) caught by
  `MONO-1`/`MONO-4` instead — coverage survives only as a combination, not from BCG alone.
- §7: the predecessor's "SCOPE-A/SCOPE-B numerically identical, double-counted" finding is
  not carried forward as a disclosed caveat in the new spec, unlike the `MC_VOW`
  misattribution caveat which is explicitly carried.

**INFO / confirmed correct** (independently recomputed, not merely re-asserted): Fix 1
boundary algebra (§1); Fix 2 reproduction-gate band (§2); Fix 3's BCG-1/BCG-2 pass/fail pair
and the differential-blindness argument (§3); no reintroduction of withdrawn 62ba9d figures
(§5); dependency availability, verified by actual execution rather than inference (§6);
SCOPE-B growing-gap framing and forbidden-sentence discipline (§7); Fix 4 mechanical items and
w-grid provenance match (§8).

---

## 10. Cheapest observation that would falsify the repair's central claim

**Re-run BCG-2 (or the equivalent hand computation in §3) and check whether the residual ever
comes out below 1.0 bit.** I performed exactly this recomputation independently, from the
formula text alone, and it did not: the residual is `0.5*L_mem(P)` exactly at all five
committed rows (46.25 / 69.3 / 90.65 / 103.0 / 136.1 bits), eight-plus orders of magnitude
above both the `1e-9` BCG-1 tolerance and the `1.0`-bit control-integrity floor. **This is the
single cheapest test that would have falsified the "at least one control can now fail"
claim, and it survives.** The narrower, still-live falsifier for the *scope* of that claim
(not its truth) is the sign-flipped-clamp mutation in §3a: run that mutation through BCG-1
and confirm it passes (I predict it will, by the symmetry of `max(0,x)`/`max(0,-x)` at
`x=0`), then confirm `MONO-1` alone catches it — this is the next concrete action.

## 11. Narrowest supported statement

Independently recomputed: Fix 1 (boundary algebra), Fix 2 (reproduction-gate band), Fix 4
(mechanical) are correctly implemented in `experiments/EXP-SSI-9b542d/specification.yaml`.
Fix 3 (the binding control-capability defect) is genuinely repaired **for the specific
anchor/constant-offset defect class that got `EXP-SSI-697354` rejected** — `BOUNDARY-
CONDITION-GATE`'s BCG-1/BCG-2 pair is demonstrably capable of returning a negative on the
program's own historical wrong formula, verified independently in §3 — but that repair is
scoped to that one defect class (§3a) and does not extend the other dozen inherited controls'
data-driven unreachability (§4), and the contract's own text about `RG-REPRODUCTION-GATE`'s
discriminating power contains an inaccuracy (§3b) that should be corrected. No security claim
about SQIsign is made or supportable by this record; nothing here is evidence about SSI in
either direction (`certificate.kind: none`, unchanged).

## 12. Next concrete action

Coordinator, before authorizing execution: (a) correct or clarify
`RG-REPRODUCTION-GATE.can_this_control_fail`'s sentence about insensitivity at
`log2_w=1000` (§3b) so it does not contradict `EV-SSI-455241` OBJ-1 on record; (b) record in
the ledger decision, precisely, that `BOUNDARY-CONDITION-GATE` fixes the anchor-offset class
specifically and that the other dozen inherited controls remain data-driven-unreachable on
the frozen inputs (§4), rather than certifying the full control set as now object-level; (c)
optionally, before dispatch, have the Executor add the sign-flipped-clamp mutation from §3a
as an explicit `crossover.py` self-test (BCG passes, MONO-1 catches it) to make the
BCG+MONO-1 complementary-coverage argument executable rather than asserted. None of these
block `execution_authorization` on the four fixes DEC-20260806-a00a28 actually named — those
four are verified.

## Artifact paths

- `experiments/EXP-SSI-9b542d/specification.yaml`
- `coordination/goals/GOAL-SSI-001/batches/BATCH-284f63/tasks/TASK-20260806-55cf1f/repair_report.md`
- `coordination/goals/GOAL-SSI-001/batches/BATCH-284f63/archives/TASK-20260806-b03b21/snapshot-receipt.json`
- `experiments/EXP-SSI-697354/specification.yaml` (comparison baseline for the rejected `MC_P13`)
- `experiments/EXP-WESOVOW-001/cost_model.py` (comparison baseline for the anchor defect's other instance)
- `ledger/decisions/DEC-20260806-a00a28.yaml`
- `ledger/evidence/EV-SSI-455241.yaml`
- `ledger/hypotheses/H-SSI-7fe2bf.yaml` (w-grid provenance cross-check)
- `inputs/P13-WESOLOWSKI-2026/paper_fulltext.md` (T2 transcription cross-check, lines 234-238)
- `docs/claims-and-verification.md` (claim-tier mechanical rule cross-check)

```yaml
red_team_report:
  id: RT-20260806-10980e
  task_id: TASK-20260806-10980e
  claim_under_review: >-
    EXP-SSI-9b542d's repair_report.md claim that all four DEC-20260806-a00a28 repair
    requirements are met: (1) MC_P13_CORRECTED reduces to T_full exactly at w=M; (2)
    RG-1..RG-5's band is a consequence of the corrected formula under its declared
    configuration; (3) BOUNDARY-CONDITION-GATE supplies at least one control capable of
    returning a negative about the mathematical object; (4) re/ast added and the w-grid moved
    into the frozen spec.
  objections:
    - "RG-REPRODUCTION-GATE.can_this_control_fail's claim that RG-1..5 were 'never actually sensitive to the memory term at log2_w=1000 in either formula version' is false for the superseded formula and contradicts the record's own OBJ-1 finding (72.2 vs [118.25,118.75], a 46-bit deviation), independently recomputed in this review."
    - "BOUNDARY-CONDITION-GATE covers a single anchor point against a single named alternative model; a sign-flipped-clamp or memory-blind mutation passes BCG-1 and is caught only by MONO-1/MONO-4, not by BCG itself -- coverage is a combination, not BCG alone, and the spec does not state this scope limit explicitly."
    - "The other ~dozen controls inherited unmodified from EXP-SSI-697354 remain, as before, essentially unreachable-to-fail on the frozen committed T1/T2 data (their fail thresholds require data far from what is committed) -- this repair fixes 'at least one' as required, but the ledger decision must not imply the whole control set is now object-level."
    - "EV-SSI-455241's separate finding that SCOPE-A and SCOPE-B are numerically identical at log2 k_DG=0 (double counting) is not carried forward as a disclosed caveat in the new contract, unlike the MC_VOW misattribution caveat which is explicitly retained."
    - "cost_functions.assessed_method_cost.MC_P13_CORRECTED.equivalent_form reuses the symbols T_A/T_full for both log2-cost (additive) and linear-cost (multiplicative) forms in adjacent sentences; consistent once substituted correctly, but a readability/notation defect."
  required_controls:
    - "Correct or clarify the RG-REPRODUCTION-GATE.can_this_control_fail sentence about insensitivity at log2_w=1000 so it does not contradict EV-SSI-455241 OBJ-1 on record."
    - "Add an explicit sign-flipped-clamp (or equivalent memory-blind) self-test to crossover.py demonstrating BCG-1 passes it and MONO-1 catches it, making the BCG+MONO-1 complementary-coverage argument executable rather than asserted."
    - "Ledger decision text should state precisely which controls are now object-level-capable (BOUNDARY-CONDITION-GATE, for the anchor-offset class) versus which remain data-driven-unreachable on the frozen inputs (the inherited dozen), rather than certifying the full control set uniformly."
  counterexample_or_mutation: >-
    A mutated formula 0.5*max(0, log2_w - L_mem(P)) (clamp direction reversed) satisfies
    BOUNDARY-CONDITION-GATE's BCG-1 check at w=M (residual 0, since max(0,0)=0 regardless of
    sign convention) despite being a physically backwards cost law (cost falls as memory
    shrinks below the table size). This is caught by MONO-1 (wrong slope sign/kink pattern),
    not by BCG, and demonstrates BCG's single-point, single-alternative-model scope.
  baseline_comparison: >-
    Not applicable in the ECDLP/Pollard-rho/BSGS sense -- this record costs a model
    (Wesolowski p^{1/3+o(1)} SSI attack vs. matched Delfs-Galbraith / vOW baseline), not an
    executed attack, per its own scope statement. The relevant "baseline" for this review is
    the rejected predecessor contract's control set (EXP-SSI-697354, EV-SSI-455241), against
    which BOUNDARY-CONDITION-GATE is a genuine, independently-verified improvement for the
    anchor-offset defect class specifically.
  heuristic_challenges:
    - "heuristic_under_test: NONE is correctly stated and this contract validates no heuristic; it depends on HEUR-XO-1..3 and Wesolowski Heuristic 1 without testing them -- accepted, not an objection."
  cost_model_challenges:
    - "Fix 1 boundary condition independently recomputed as exactly 0.0 for MC_P13_CORRECTED and exactly 0.5*L_mem(P) for MC_P13_SUPERSEDED_do_not_use, at all five committed P rows -- matches the spec's claimed table exactly."
    - "Fix 2 reproduction-gate bands (RG-1..RG-5) independently recomputed from the T1/T2 literals and match the claimed bands to within rounding noise from 6-decimal coefficient truncation (<3e-5 bits)."
    - "MC_VOW's misattribution caveat (memory discount applied to the baseline rather than the assessed method's own table) remains unrepaired, explicitly out of DEC-20260806-a00a28's four named fixes, and is disclosed as such -- accepted, not a fresh objection."
    - "SCOPE-B growing-gap figures (9.5387/21.9537/38.8387 bits at NIST-I/III/V) independently recomputed from T_full(P) at S=A=c=0 and match to 4 decimal places; forbidden_sentences correctly bars the withdrawn 'NIST-III/V retain margin' unqualified sentence."
  reduction_and_scope_challenges:
    - "affected_conditionally_in_model and safe_or_out_of_range sections correctly scope the claim to SQIsign-family constructions under Heuristic 1 and HEUR-XO-1..3, unbounded-memory model only, cost-model only, never an executed attack -- no scope inflation found."
    - "SCOPE-A/SCOPE-B double-counting at log2 k_DG=0 (EV-SSI-455241 finding) is not disclosed in the new contract's scope_statement -- a carried, silently-dropped caveat, low severity since out of this task's four named fixes."
  proof_architecture_challenges: []
  narrowest_supported_statement: >-
    Fixes 1, 2, and 4 are independently verified correct by direct recomputation from the
    formulas and literals in the frozen spec. Fix 3 is genuinely repaired for the specific
    constant-offset anchor-error defect class that got EXP-SSI-697354 rejected -- verified via
    independent computation of both BCG-1 (pass, residual 0.0) and BCG-2 (fail, residual
    0.5*L_mem(P), 46.25-136.1 bits, matching the spec's claimed table exactly at all five
    committed P rows) -- but that repair does not extend to the other ~dozen inherited
    controls, which remain, as before, essentially unreachable-to-fail on the frozen committed
    data, and one control's own self-description (RG-REPRODUCTION-GATE.can_this_control_fail)
    contains a claim that contradicts the record's own OBJ-1 finding. No claim about SSI,
    SQIsign, or the supersingular isogeny problem is supported or asserted by this review.
  next_concrete_action: >-
    Coordinator: before granting execution_authorization, correct the RG-REPRODUCTION-GATE
    self-description inconsistency (Section 3b of this report) and record precisely, in
    DEC-20260806-e2a6fa, that BOUNDARY-CONDITION-GATE is object-level-capable for the
    anchor-offset class specifically while the inherited controls remain data-driven-
    unreachable -- do not certify the full fourteen-plus-assertion set as uniformly healthy.
    Neither finding blocks authorization on the four fixes DEC-20260806-a00a28 actually named;
    those four are independently verified correct in this report.
  artifact_paths:
    - coordination/goals/GOAL-SSI-001/batches/BATCH-284f63/reviews/TASK-20260806-10980e/red_team_report.md
  reviewed_records:
    - experiments/EXP-SSI-9b542d/specification.yaml
    - experiments/EXP-SSI-697354/specification.yaml
    - coordination/goals/GOAL-SSI-001/batches/BATCH-284f63/tasks/TASK-20260806-55cf1f/repair_report.md
    - ledger/decisions/DEC-20260806-a00a28.yaml
    - ledger/evidence/EV-SSI-455241.yaml
    - experiments/EXP-WESOVOW-001/cost_model.py
    - ledger/hypotheses/H-SSI-7fe2bf.yaml
    - inputs/P13-WESOLOWSKI-2026/paper_fulltext.md
    - docs/claims-and-verification.md
    - coordination/goals/GOAL-SSI-001/batches/BATCH-284f63/archives/TASK-20260806-b03b21/snapshot-receipt.json
  inference:
    requested_policy: review-adversarial
    reasoning_effort: xhigh
    resolved_model_id: claude-sonnet-5
    fallback_used: true
    fallback_reason: >-
      This Claude Code harness resolves every policy alias in
      orchestration/model-policies.yaml to one model. Recorded, never silently substituted
      (AGENTS.md rule 11).
    degraded_allowed: false
    independent_session: true
    model_verified: false
    model_verified_reason: No adapter probe receipt exists for this session.
```
