# Reconciliation of the two BATCH-9e3584 review chains

Task `TASK-20260812-2a3aa0`. Goal `GOAL-MLKEM-005`, batch `BATCH-c347e1`.
Ordered by `DEC-20260812-15d3b2` `reconciliation_action_for_the_merger` step 5 and
by `goal_next_action_to_apply` step one.
Ledger drafts written alongside this note, in this same directory:
`DEC-20260812-2233ed.draft.yaml`, `EV-MLKEM-c7a814.draft.yaml`.

**What this instrument is.** The side-by-side reading of two independent review waves
over one producer snapshot, and its provenance. The binding acts are the two drafts
above once the ledger-archive task `TASK-20260812-a03011` stages and commits them; this
file is the account a later reader needs in order to overturn them.

**BOTH CHAINS ARE VALID AND NEITHER IS DELETED.** Nothing here modifies, corrects,
renames or deletes `EV-MLKEM-9346bb`, `DEC-20260809-afe29b`, `KN-FIND-2a35aa`,
`EV-MLKEM-e45478` or `DEC-20260812-15d3b2`. Where I conclude that a sentence in one
chain reaches further than what was shown, the instrument is the new record
`DEC-20260812-2233ed` and never an edit to either chain.

**CLAIM TIER STAYS TOY.** Nothing in BATCH-9e3584, in either wave, in this note or in
either draft bears on ML-KEM security, on any FIPS 203 parameter set, on any attack
cost, or on any cost model. No number here is transported to `beta = 606`, `d = 1420`,
or any other parameter set, by extrapolation, by analogy, or by any other route.

---

## 0. Provenance, split explicitly

`BATCH-cbe023` produced a Coordinator claim about the git record that a Validator then
proved false. The 2026-08-11 adjudication and the wave-2 note both hold that line by
separating what was read from what was relayed, and this note holds it too.

### 0.1 Read by me in this worktree, in full, and therefore mine to assert

- `ledger/decisions/DEC-20260812-15d3b2.yaml`
- `ledger/decisions/DEC-20260809-afe29b.yaml`
- `ledger/evidence/EV-MLKEM-9346bb.yaml`
- `ledger/evidence/EV-MLKEM-e45478.yaml`
- `knowledge/findings/KN-FIND-2a35aa.md`
- `.../BATCH-9e3584/reviews-wave2/WAVE2-COORDINATOR-RECONCILIATION.md`
- `.../BATCH-9e3584/COORDINATOR-ADJUDICATION-20260811.md`
- `.../BATCH-c347e1/dispatch_queue.json` (my own task card and its handoff)
- `templates/research-records.md` (the Evidence and Coordinator-decision sections)
- `tools/validate_ledger.py` (`REQUIRED`, `DOCUMENTED_NULL_OK`, `field_is_satisfied`,
  `check_ledger_record`, `check_cross_refs`)

### 0.2 Read by me in this worktree IN PART, by targeted reads and greps, and marked as partial

I state this rather than implying full readings I did not make.

- **Wave-1 Red Team** `.../reviews/TASK-20260809-444fe7/red_team_report.md`: read the
  header and inference block, the section-0 finding table (RT-1 .. RT-10) and its
  against-my-own-thesis paragraph, section 1 (the git verification table), sections
  2.4-2.5, section 3, section 4, and sections 11-16 including the narrowest supported
  statement. **Not read in full**: sections 5-10 and 2.1-2.3, which I know only through
  the section-0 table and through `EV-MLKEM-9346bb`.
- **Wave-1 Validator** `.../reviews/TASK-20260809-3f1dc4/validation_report.yaml`: read
  the F-1 finding verbatim with context, the index of finding ids, severities and
  `where` fields (F-1 .. F-11, V-P1, V-P2, V-P4, V-P5, V-P6), the
  `corrections_required_before_any_of_this_is_cited` list, and the `verdict: passed`
  line. A grep for `G_REL_PASS`, `816`, `across-cell` and `ANY rule` over the whole file
  returned **zero matches**, which is the basis for the claim in section 2 that wave-1's
  Validator does not name the across-cell aggregation. **Not read in full.**
- **Wave-2 Validator** `.../reviews-wave2/TASK-20260812-da8c3b/validation_report.yaml`:
  read the index of finding ids and severities (F-1 .. F-7) and the `verdict: passed`
  line. **Not read in full**; its content is otherwise known to me through
  `EV-MLKEM-e45478` and the wave-2 note.
- **Wave-2 Red Team** `.../reviews-wave2/TASK-20260812-aadafd/red_team_report.md`: read
  its section-10 baselines passage, section 11 narrowest supported statement, section 12
  budget and infrastructure table, and the head of section 13. **Not read in full**; its
  content is otherwise known to me through `EV-MLKEM-e45478` and the wave-2 note.
- I directory-listed `.../reviews-wave2/TASK-20260812-aadafd/probes/` (7 `.py` files
  present) and `.../reviews/TASK-20260809-444fe7/probes/` (20 files present, matching the
  wave-1 Red Team's own section-12 declaration of 20 probe files plus its report).

### 0.3 Relayed, and NOT mine

**I hold no shell in this session.** I ran no git command, no producer code, no probe,
no `yaml.safe_load`, and no `tools/validate_ledger.py`.

- **Every statement about the git record**: the three-way commit split
  (`1aa7db53` / `c034ef38` / `502d15a0`), the 30-for-30 content match at HEAD and at the
  declared commits, the ancestry chain, the D3 table at 9 dangling and 9 undeclared, the
  archive commit messages, the producer run ordering and the notarization chain in both
  directions. These are the four reviewers' measurements and, where the adjudication and
  the wave-2 note state them, the dispatching sessions' — attributed at each place and
  never narrated as mine.
- **The state of `origin/claude/ml-kem-solution-ckdxmg`** (tip `86ac7f72e`, archive
  commit `5004932a9`, its five `completed` task states, its zero files under
  `reviews-wave2/`): relayed from the wave-2 note, which attributes it to its
  dispatching session.
- **Every numeric result of all four review sessions**, and every producer number. I
  recomputed nothing.
- **That both branches are now merged into `main`**: asserted by my task card and by the
  `BATCH-c347e1` queue objective. What I can assert from reading this worktree is
  weaker and is exactly this: `ledger/evidence/EV-MLKEM-9346bb.yaml`,
  `ledger/decisions/DEC-20260809-afe29b.yaml`, `knowledge/findings/KN-FIND-2a35aa.md`,
  `.../reviews/TASK-20260809-3f1dc4/validation_report.yaml`,
  `.../reviews/TASK-20260809-444fe7/red_team_report.md` and its 20 probe files are all
  **present in this worktree** alongside the wave-2 records, which is what makes this
  reconciliation possible at all. Whether this worktree equals `origin/main` I did not
  and cannot check.

### 0.4 What I could not verify and hand on rather than assert

`yaml.safe_load` on the two drafts and `python3 tools/validate_ledger.py` before and
after. I hold no shell, so I have **no before-count and no after-count**, and I did not
estimate either. `TASK-20260812-a03011` must run both before staging, must record the
two counts in its receipt, and — per its own card — may correct a schema or parse defect
provided it records the correction and does not rewrite the analysis or soften a verdict.

---

## 1. What is being reconciled

Two independent review waves ran over **one** producer snapshot, `c034ef38`, because the
`BATCH-9e3584` continuation queue listed `TASK-20260809-3f1dc4` (validator) and
`TASK-20260809-444fe7` (red team) as `queued` with a note reading "NOT RUN" when they had
already been executed on a separate branch. Both chains are now in this tree.

| | wave 1 | wave 2 |
| --- | --- | --- |
| validator slot | `TASK-20260809-3f1dc4` | `TASK-20260812-da8c3b` (executed card `-3f1dc4`) |
| red-team slot | `TASK-20260809-444fe7` | `TASK-20260812-aadafd` (executed card `-444fe7`) |
| reports at | `.../reviews/<slot>/` | `.../reviews-wave2/<slot>/` |
| probe files | 20 | 28 |
| evidence record | `EV-MLKEM-9346bb` | `EV-MLKEM-e45478` |
| decision | `DEC-20260809-afe29b` | `DEC-20260812-15d3b2` |
| knowledge entry | `KN-FIND-2a35aa` | none (promotion deliberately scheduled) |
| `fpylll` | present, 0.6.4 | **ABSENT in both sessions** |
| validator verdict | `passed` | `passed` |
| decision value | `revise` | `revise` |

The mechanism of the collision is recorded in `DEC-20260812-15d3b2.collision` and in the
wave-2 note; it is a coordination defect and not an evidence defect, and this
reconciliation does not reopen it. Restated once because it bears on how the agreement
below must be read: a reserved identifier held in a shared mutable coordination record is
a single-writer resource handed to every worker that reads it, and
`tools/allocate_id.py --check` answers from the working tree only.

---

## 2. (a) What the two waves reached IN COMMON

**Label this precisely.** All four reviewer sessions across both waves resolve to the
same model. Wave 2 records `resolved_model_id: claude-opus-5` for both of its sessions;
wave 1 records `resolved_model_id: null` with the same verification gap and states in its
own boundaries that "two reviews resolving to one model are not two independent
judgements". Every one of the four records `model_verified: false`. **AGENTS.md rule 12
is UNMET AND UNWAIVED, and two waves does not change that by one step.**

So the agreement below is a **TWO-SAMPLE AGREEMENT OF ONE MODEL**. It is procedural, not
model-level. Stated as sharply as I can:

- **What it does buy.** It discriminates against the hypothesis that any listed finding
  is a *session-level* artifact — a fluke of one session's attention, prompt path or
  reading order. Two sessions formed without reference to each other, on two branches,
  landed on the same place. That is worth having and it is exactly this much.
- **What it does not buy.** It discriminates **not at all** against a shared model-level
  bias, a shared blind spot, or a shared misreading of the frozen text. Four correlated
  judgements of unknown and unmeasured correlation are not four judgements.
- **A useful internal gradient.** Where both waves *built the object* and measured it —
  the centered C2 ladder, the reseeded null families, the independent rebuild of the 80
  frozen bases — the agreement is stronger than where both merely *read the same
  committed artifact*, because the former agrees on a construction and the latter can
  agree by copying the same number twice.

### 2.1 The common list

| # | finding | wave 1 | wave 2 | kind of agreement |
| --- | --- | --- | --- | --- |
| C-1 | **Validator verdict `passed`**, meaning the four producer receipts are admissible evidence and nothing more — adjudicating no outcome row, retiring nothing, rescoring `BATCH-a44d08` in no respect | verdict line | verdict line, with L-3 stating the boundary | same verdict, same stated meaning |
| C-2 | **Producer arithmetic reproduces from raw, zero mismatches** | ~10^4 recomputations at 1e-12 relative, zero mismatches; bitwise re-execution of the lead | 646 stored per-basis values bit-exact; 75 G-REL2 cells and 38 G-REL1 entries at max deviation 0.00e+00 on nine statistics; C1 table and C2 ladder rebuilt from raw | both rebuilt from raw with their own code |
| C-3 | **Notarization holds in both directions**; prereg sha256 `190cf474...` agrees from the working tree, from the blob at `1aa7db53`, from the sidecar, and with all four producer manifests | reported | reported, plus the producer-ordering datum and the `--follow` rename artifact | both ran git plumbing themselves (relayed) |
| C-4 | **The 2026-08-11 Coordinator git account is CORRECT in every checkable particular**, and both report the stronger at-the-declared-commits form of the 30-for-30 match | RT §1 table, all rows CORRECT | OBS-W12 | both checked rather than accepted, as their cards required |
| C-5 | **Two of the adjudication's three UNKNOWNs resolve in its favour** (both archive commit messages carry their task id and `GOAL-MLKEM-005`); **PR/push state stays open** | RT §1 | OBS-W13 | agreement including on what stays unknown |
| C-6 | **"a factor of 6 to 31" is FALSE at its lower end; the corrected endpoints are 4.87x to 31.03x**, and no verdict moves | C-F1 / F-1 | F-1 / OBS-W2 | **endpoints agree exactly; a count does not — see §4.2** |
| C-7 | **The 8-basis collapse completion is NOT load-bearing**: all readings agree at all 117 scored cells, 0 disagreements | OBS-8, recomputed under four readings | F-2 (validator) and the Red Team's own 117-cell check | measured twice, independently |
| C-8 | **`X_null` and the UNPLANTED `X8 = rdet` are both zero-dispersion**, bit-identical across all 8 frozen bases at 38 of 38 cells, and `G-VAR` fires on both in the frozen family | OBS-1, OBS-4, three routes | three-source per `EV-MLKEM-e45478` (ii)(a) | now four independent evaluations across the two waves |
| C-9 | **Section B-prime's decay-check FAIL survives reseeding** | 2 families: 35 and 39 of 48 | 1 validator family: 34 of 48; 8 red-team replicates: 28, 37, 36, 32, 32, 29, 28, 35 | 11 independently seeded families across the two waves; none within seven steps of the pre-registered PASS threshold of <= 21 |
| C-10 | **The single reported `n_fire = 35` is not a property of the estimator** | RT-4 Monte Carlo sampling sd ~ 4.2 of 48; the quoted `se_step/se_diff` 1.05-1.08 is one seed draw against families spanning 0.75-1.22 | RT-B1 empirical 32.1 +/- 3.6 over 8 replicates, the reported value a 0.80 sd high draw, declared a lower bound | **same quantity, two disjoint constructions, consistent answers (4.2 model vs 3.60 empirical lower bound)** |
| C-11 | **The centered C2 control corroborates the producer's own diagnosis of P-C2c**: 0 of 10 targets fire at `delta/SE <= 1.0` | RT-7 / `probe_c2_centered.py` | OBS-W11 / `probe_c2_centered.py` | **built independently in both waves, identical result; the strongest single agreement in these two chains** |
| C-12 | **P-C2e could not have failed mathematically**: a constant offset is an exact symmetry of `se_decomposition`; both reproduce the producer's `8.53e-16` as `8.527e-16` | RT-7, plus `8.938e-11` at `1e6 * SE` and 11.68 relative under a structured one-column injection | RT-C2b, same algebra, same `8.527e-16` | derivation reached twice |
| C-13 | **Four C2 targets are unreachable by the 12-SE ladder**, and they are the degenerate-`nu_eff` targets | OBS-13 (4 of 10 unreachable, exactly the four smallest `nu_eff`) | RT-C1b (positive control tested 6 of 10) | same fact, wave 2 adds why (see §3.2) |
| C-14 | **Section C1's re-score changed no verdict**, as prereg 4.5 declared in advance; P-C1a falsified and reported against the producer's own interest | OBS-13 | OBS-W9, all ten ratios reproduced to four decimals | both recomputed independently |
| C-15 | **Claim tier TOY; no cryptographic baseline; `dominated_by`/`sota_delta` null or `not_applicable` FOR THAT REASON**, checked rather than asserted | stated and verified | stated and verified, both reviewers searched for a cost claim and found none | agreement including on the method of checking |
| C-16 | **Rule 12 unmet and unwaived; independence procedural, never model-level; `model_verified: false`** in all four reviewer sessions | stated | stated, unprompted, in both reports | this is the agreement that bounds all the others |
| C-17 | **`AM-3` IS NOT RETIRED; `BATCH-a44d08` IS NOT RESCORED IN ANY RESPECT** | restated | restated | binding carry, observed by both |
| C-18 | **Neither wave's bitwise agreement is portability.** Every probe of both waves ran on the producers' own numerical stack (python 3.11.15, numpy 2.4.6, scipy 1.17.1) | stated in boundaries | stated in `coordinator_verification_performed`, correcting the Red Team's own "different environment" phrasing | both refuse the over-read |

### 2.2 The one thing the common list is worth, stated once

C-11 and C-10 are the two entries where two sessions **built different objects and got
the same answer**. Everything else in the list is either a re-reading of the same
committed bytes or a re-execution of the same arithmetic. When this reconciliation is
cited, C-11 and C-10 may be cited as procedurally corroborated; the rest may be cited
only as "reproduced twice, by one model, in two sessions".

---

## 3. (b) What is UNIQUE to each wave

### 3.1 Wave 1 only

1. **RT-1, the six-route table — route dependence.** `X_null` evaluated through six
   arithmetic routes to `log|det B|`: R0 closed form and R1 `slogdet(B)` and R3
   `slogdet(UB)` are 38 of 38 bit-identical and REFUSED; **R2 QR of `B^T`, R4
   `0.5 slogdet(BB^T)` and R5 `slogdet(BH)` are 0 of 38 and ADMITTED**, all six
   reproducing the notarized prereg 2.6 table at 304 of 304 cell-by-basis entries and
   walking G-REL2 at 19 of 19. **Wave 2 never tested R2, R4 or R5.** Its RT-R2 computed
   the definitional matrix path, which is wave-1's R1, and found the same refusal.
   Route dependence is wave 1's alone.
2. **RT-2 / OBS-3 — the producer's own committed carrier of route dependence.**
   `forced_arithmetic.rdet_T1_ambient_isometry_residual = 3.865352482534945e-12` against
   `report_relvar.md` section 4's blanket "Residuals are 0 identically". Wave 2 does not
   name it.
3. **The AM-13 scope ruling for P-R6, and the official Section R open-prediction count of
   ONE.** Wave 1's two reviewers divided (Validator 1, Red Team 2) and the Coordinator
   ruled the clause general. Wave 2 touches the prediction count nowhere.
4. **C-F5, the cross-platform framing is not citable**, with the citable replacement: a
   portability result across three textually distinct implementations at 24 of 24
   per-basis pairs to 6 decimals, max absolute deviation `4.84e-07`, `fpylll` pinned at
   0.6.4 in both runs and the reduction input bit-identical by construction. **Wave 2
   could not touch this at all** — `fpylll` absent — and instead records that its own
   agreements are not cross-platform.
5. **C-F8 and V-P6 — the G-NUM gap.** "X_null walks the ENTIRE AM-4 gate" is unsupported
   from the batch's own artifacts (section 6 contains no G-NUM row); the Validator
   measured it itself, `max rho_T0 = 0.000e+00` exactly against `tau_num = 1e-6`.
6. **C-F6 / OBS-1 — the provenance and novelty finding, and it is the largest thing wave 2
   has no counterpart to.** `X_null`, its definition, `s_X = 1.0` and both headline
   figures (G-REL1 3.1035, G-REL2 0.6000) were already built, measured and committed as
   `BATCH-cbe023` RT-A1 and quoted verbatim in `DEC-20260808-05b684` rationale (iii);
   RT-A1 is cited nowhere in the batch. The headline is **REPLICATED AND EXTENDED, never
   new** — which is against the producer on novelty and for it on evidential strength.
7. **RT-3, the guard amplitude.** `mu` median 0.224 for the guard against `hkz` 16.3 and
   `lam1n` 2.30, the mirrored gap 79x to 266x at identical cells; and, against the Red
   Team's own prediction, the guard **does** fire under the pinned floor (19 of 19 pinned
   REL2 entries).
8. **RT-6, saturation.** Expected `c_min` under a ratio-1 null is `1 + t_{n-1,0.998}`,
   which falls with more draws (5.207 at n = 8 to 3.878), so the null count rises toward
   48 of 48 with more data; only `c < 5.207` can separate at all.
9. **RT-4 and RT-5.** `P(P-B1 falsifier) = 0.00175` over 20000 reps under the null AM-13
   mandates; the PASS clause's second conjunct is a tautology true of any family; the
   null's shape parameter differs from the real arm's by a factor 2.19.
10. **RT-10.** `tau_rel = 0.025` is a maximum of four numbers spanning a factor 2.32; the
    same rule at p95 gives 0.0735; no verdict moves.
11. **The instrument acts.** `AM-15` and `AM-16`; the prospective protocol amendment PA-1;
    the program defect `PD-d49e35` (the receipt-cannot-state-its-own-commit tension); the
    supersession of archive tasks `TASK-20260809-91cf76` and `TASK-20260809-4d928d`; and
    the promotion of `KN-FIND-2a35aa`.
12. **Coverage.** Wave 1 had `fpylll` 0.6.4 and its reduction-dependent rows are covered
    by it; wave 2's are not.

### 3.2 Wave 2 only

1. **RT-R1 — the family (fibre) conditionality, and the wave's sharpest object.** The
   frozen family `B_i = [[I_k, A_i],[0, q I_{d-k}]]` holds `|det B| = q^(d-k)` constant
   across the basis index by construction, so every determinant-only functional is
   bit-identical there and **`G-VAR` could not have failed to fire on one**. The Red Team
   built the nearest family differing in exactly one respect — F1 with
   `[[I_k, A_i],[0, diag(m_i)]]`, `m_i[0] = q + i`, same `A_i` draw, same grid, same
   `tau_rel`, same `s_X`, identical code path — and `G-VAR` fires 38 of 38 on both `rdet`
   and `X_null` in F0 and **0 of 38 on both in F1**, while `X_null` still walks G-REL1
   10/10 and G-REL2 19/19 and still reads zero entries of `A_i`. A witness probe reports
   F1's `X_null` taking 8 distinct doubles strictly increasing in the basis index at 6 of
   6 cells against 1 distinct value at 6 of 6 in F0. The missing separator is named:
   dispersion **on the fibre of the family over the observable's own declared arguments**.
   Cost 0.24 s per candidate at `d <= 140`, no reduction. Single-source.
2. **Validator O-2 — `G-VAR` as frozen is EVADABLE, i.e. necessary but not sufficient.**
   `V_evade(B,beta) = X_null(B,beta) + 1e-9 * A[0,0] / q`, pushed through the producer's
   own committed `measure_relvar.py` and its own `rho_both()`, `summarize()` and
   `bit_identical()`: not bit-identical at any of the 38 cells (max between-basis float
   sd `3.91e-10`), so `G-VAR` **admits** it, while it walks G-REL1 10/10 and G-REL2 19/19
   under every aggregation rule including the strictest. The frozen text names the
   loose-tolerance hazard and closes it by choosing bit identity; **the symmetric hazard
   of the bit test is named in no producer artifact and in no wave-1 record.**
   Single-source.
3. **RT-R3 — the over-closure.** Only the PASS side was shown vacuous. The gate's
   **refusal side is untested in either direction** and its false-refusal rate has never
   been measured. Names and prices the cheapest test — one observable informative by
   construction and structurally refused, e.g. a statistic over the leading `k` raw-GSO
   log-norms, which depends on `A` and `k` but takes no `beta` argument and so fails REL-1
   by algebra exactly as `rdet` and `lam1n` do; minutes of numpy, one QR per basis, no
   reduction — and correctly declines to run it, because introducing a candidate
   observable is the Idea Generator's and the Coordinator's act.
4. **F-2 — a SECOND, UNDECLARED aggregation, this one ACROSS CELLS.** `G_REL_PASS`
   (`measure_relvar.py` lines 816-819) collapses across lattices and cells with an **ANY**
   rule: REL1 passes if at least one scored lattice passes, REL2 if at least one scored
   cell passes. It is not in the frozen text and is not among the declared implementation
   completions, and it is what selects R-OUT-4 over R-OUT-5 and produces the reported
   "2 of 5". **My grep of the wave-1 validation report for `G_REL_PASS`, `816`,
   `across-cell` and `ANY rule` returned zero matches**, so this is wave 2's alone. The
   defect is the non-disclosure: the reported outcome is correct under the frozen text's
   own "majority" language, `X_null` passes under all three rules, and R-OUT-1 is
   invariant to the choice.
5. **RT-R2 — R-OUT-3 is unreachable by construction.** `x_null_of` implements the closed
   form and never touches the matrix, so the outcome row for "passes the gate but
   dispersion is non-zero, therefore a defect in the instrument" cannot fire; P-R3 is
   forced by the **source code**, which is strictly stronger than the report's already
   honest "forced by algebra". The remedy was supplied in the same probe: the definitional
   matrix path reproduces the notarized 2.6 table at 38 of 38.
6. **RT-C1a — Section C1's only live observation reduces to a controlled null.** 200,000
   effect-free iid-normal 8x4 tables through the identical carried `se_decomposition` give
   `P(SE_2way/SE_naive < 1) = 0.3982`, expected **3.98 of 10 against 4 observed**; null
   median 1.0896, p05 0.3871, p01 0.1785; a permutation null agrees target by target
   within 0.03 in percentile; the extreme 0.3635 sits at the 4.4th percentile, and across
   ten targets the chance at least one falls that low is about 36%. A controlled null **in
   both directions** — equally not evidence that the instrument is sound. Wave-1's RT-10
   attacked `tau_rel`'s dispersion but built no effect-free null for this ratio.
7. **RT-C1b — the degeneracy is a property of the `S = 8, E = 4` design, not of the
   data.** On 100,000 draws per model: unstructured iid-normal 8x4 gives
   `P(nu_eff <= 1.5) = 0.357`, `P(|t|crit >= 8) = 0.527` (expected 5.27 of 10),
   `P(negative variance component) = 0.143`; with support and pool structure
   (0.4 / 0.2 / 0.4), 0.006, 0.014 and 0.0003. The committed profile is 4 of 10 degenerate
   and 1 of 10 negative-variance-component. **The binding constraint on Section C is
   `E = 4`, not the relative floor** — and the four non-firing targets are UNINFORMATIVE,
   which is not the same as null, a distinction wave 2 keeps and I keep.
8. **The `n_fire` dispersion profile across the whole `c` grid**: sd 1.20 at `c = 4`, 3.60
   at `c = 6`, 1.19 at `c = 8`, 0.00 at every `c >= 12` — the carried headline constant
   sits exactly on the steep part of the transition.
9. **F-7 and the collision itself.** The wave-2 Validator discovered the duplicate
   execution while re-checking its own dependency's ancestry, and named both halves of the
   mechanism. It reports that it did **not** open the other validation report, reading only
   that blob's git metadata, which is the property that makes wave 2 worth comparing at all.
10. **OBS-W13 — the Red Team's refinement of the recorded defect, in the Coordinator's
    favour.** For both archive tasks, the receipt's own `path_sha256` path set **equals**
    its commit's change set exactly, so D3 is a defect of the queue's `artifact_paths` and
    not of the receipts. Wave 1 states the compatible fact that the dangling names exist
    only in the frozen task cards inside `dispatch_queue.json`, but does not make the
    positive statement about the receipts. Consistent with wave 1 and sharper.
11. **F-4 — propagation of a mis-diagnosis.** `measure_relvar.py`'s comments restate
    `BATCH-cbe023`'s defect D-2, which that batch's Validator had already established to be
    a mis-diagnosis; this is the sixth artifact to carry it forward. Only the label repeats
    it; the producer's added guard is real and executes.
12. **F-6 — a budget guard above its budget.** `TASK-20260809-311784`'s durable
    `command.txt` runs `timeout 7200` against a declared budget of 3600 s. The run used
    119.5 s; nothing bound.
13. **Two structural constraints closed WITHOUT `fpylll`**: `lam1n` takes no `beta`
    argument so its value must be identical across the three betas at every
    (lattice, basis), 0 violations of 48; `hkz` is a mean over the last beta indices of a
    decreasing profile so it must be non-decreasing in `beta`, 0 violations of 48.
14. **Two minor manifest gaps** (`-97d6cf` records no `max_rss`; `-3eb72c` carries no
    resources block, both figures present in the results JSON) and the producer **ordering**
    datum (13:16:20Z, 13:25:29Z, 13:26:05Z, 13:27:55Z, all after the notarizing commit's
    13:10:41Z and before the snapshot's 13:37:48Z).
15. **The `git log --all --follow` rename-detection artifact** on the four zero-byte
    `stderr.log` blobs, corrected by the wave-2 Validator against its own first result.

### 3.3 Where wave 2 is NARROWED by this reconciliation

Per my task's constraint: where a wave-2 finding was already established or already
refuted by wave 1, `EV-MLKEM-e45478` is **narrowed by `DEC-20260812-2233ed`**, never
corrected. Four places, and each narrowing is about **novelty**, not about correctness.

- **N-1. RT-R1's CONSEQUENCE was already established by wave 1; its MECHANISM was not.**
  `EV-MLKEM-e45478`'s inference states that in F1 "adding `G-VAR` is NOT the repair the
  report proposes". That conclusion was already reached, archived and promoted to the
  corpus by wave 1, on independent grounds: RT-1's six-route table, OBS-2, OBS-14's
  compositional statement, `KN-FIND-2a35aa` section 5, and `AM-16` enacted on those
  grounds. **RT-R1 is a second, disjoint escape mechanism for an already-established
  conclusion, not its discovery.** The narrowing cuts the novelty claim and *raises* the
  evidential weight of the conclusion: two independent escape mechanisms, two built
  counterexamples, from two waves that did not read each other.
- **N-2. The centered C2 ladder is not a control "the batch did not contain".** Wave 1's
  Red Team had already built it (`probe_c2_centered.py`), obtained the identical result
  (0 of 10 targets firing at `delta/SE <= 1.0`), and archived it; wave 1's decision cites
  it. `DEC-20260812-15d3b2` rationale lists "the centered ladder Section C2 deferred"
  among four controls the batch did not contain. Narrowed: **not new to wave 2 — and
  independently built twice with the same answer, which is stronger than new.**
- **N-3. The 8-replicate dispersion estimate for `n_fire`, and the independently seeded
  null family, are not the first of their kind.** Wave 1 had already built two
  independently seeded null families (35 and 39 of 48) and had already measured `n_fire`'s
  sampling dispersion at about 4.2 of 48 by a 20000-rep Monte Carlo, recording explicitly
  that `n_fire` is reported without any dispersion anywhere. Narrowed as to novelty;
  wave 2's empirical 3.60 (declared a lower bound) and wave 1's modelled 4.2 are two
  differently constructed estimates of one quantity and they are consistent.
- **N-4. The effect-free 8x4 null tables (RT-C1a, RT-C1b) are NOT narrowed.** Wave 1 has
  no counterpart. They stand as wave 2's second-most consequential contribution after
  RT-R1 and RT-R3.

Symmetrically, and recorded so the narrowing is not one-directional: **wave 1's claim
that `G-VAR`'s non-vacuity is established** — `EV-MLKEM-9346bb`
`validity_verification.control_comparability`, "G-VAR is non-vacuous in both directions"
— is **narrowed by this record too**, by O-2 and RT-R1. `G-VAR` is non-vacuous *on the
frozen family and against exactly-zero-dispersion closed forms*; it admits a `1e-10`
perturbation carrying no usable information (O-2) and it refuses nothing in F1 (RT-R1).
Narrowed by reference; `EV-MLKEM-9346bb` is not edited.

---

## 4. (c) Do the two waves' VERDICTS agree?

**Yes on every operative verdict, with one substantive divergence and one unresolved
numeric discrepancy.**

### 4.1 Where the verdicts agree

- **Both Validators returned `passed`**, with the same stated meaning.
- **Both decisions are `revise`**, neither moves a hypothesis, neither adjudicates a
  producer outcome row into a claim about lattices, and both hold claim tier TOY.
- **Neither Red Team overturns the core of R-OUT-1.** Both state in their own narrowest
  supported statements that in the frozen family, under the criterion as frozen, `X_null`
  (and the unplanted `rdet`) walk the relevance clauses while bit-identical across all 8
  bases at 38 of 38 cells — so **passing the gate carries no information about a basis at
  fixed `(d, k, beta, q)`**. Wave 1 section 15; wave 2 section 11.
- **Both Red Teams conclude that ADDING `G-VAR` DOES NOT REPAIR THE GATE**, by two
  disjoint mechanisms, each with its own built counterexample. This is the strongest
  agreement in the two chains and it is emphatically **not a replication**: neither wave
  ran the other's construction, and neither knew of it.
- **Both agree the decay-check FAIL survives and the single reported `n_fire` does not.**
- **Both agree Section C1 changed no verdict and Section C2's own diagnosis of P-C2c is
  right**, the latter each against its own red-team thesis.
- **Both agree "6 to 31" is false at the same low endpoint** and that no verdict moves.

### 4.2 The one substantive divergence

**The reach of "NO ADMISSIBILITY CLAIM IS REPORTABLE FROM THIS GATE IN EITHER
DIRECTION."**

- **Wave 1 asserts it and its Red Team endorses it verbatim.** It is the citable form of
  R-OUT-1 in `DEC-20260809-afe29b.what_is_citable_and_what_is_not`; it is OBS-1's closing
  sentence in `EV-MLKEM-9346bb`; it appears in wave-1's Red Team section 15; and
  `KN-FIND-2a35aa` carries it into the corpus **in its opening paragraph**, with the
  supporting sentence "One refused blind observable is sufficient for that verdict".
- **Wave 2's RT-R3 holds that it over-closes.** What was demonstrated is that *passing*
  the gate carries no information, because a blind closed form clears every clause
  evaluated. **Nothing was shown about the refusal side.** A candidate the gate rejects is
  rejected by a criterion whose false-refusal rate has never been measured.
  `EV-MLKEM-e45478` states in its boundaries that the sentence "IS NOT SUPPORTED AS STATED
  AND IS NOT RECORDED HERE".

This is the single most consequential disagreement between the two chains, and it is not
dissolvable by reading more carefully — I tried, and the attempt is worth recording
because it is where the reconciliation actually lands. The sentence has two readings and
wave 1 uses both:

1. **As an ABSTENTION** — "no admissibility claim is reportable from that gate in either
   direction **and none is made here**" (`EV-MLKEM-9346bb` OBS-1). Read this way it
   **survives wave 2 intact and is reinforced by it**: if the refusal side is untested,
   then a fortiori nothing may be reported from it. The operational carry is unchanged
   under both waves.
2. **As a demonstrated CLOSURE** — the reading `KN-FIND-2a35aa`'s opening paragraph
   invites, and which `DEC-20260809-afe29b.what_is_not_decided` leans toward with "the
   gate that would say so is inadmissible, in either direction". Read this way it is
   **NOT SUPPORTED**, and RT-R3 is right. `docs/inventor-protocol.md` treats premature
   closure as a failure mode symmetric with overclaiming, and this is an instance of it.

So the two waves agree on **what to do** and disagree on **what was shown**. That is a
real disagreement about evidential basis, not a verbal one, and it has a concrete
consequence: wave 1 lists no unresolved confound for the refusal side, wave 2 does, and
only wave 2 generates the false-refusal control as an owed experiment.

### 4.3 The unresolved numeric discrepancy

**How many entries fall below 6x.** Both waves agree the endpoints are **4.87x to
31.03x** and that no verdict moves. They do not agree on the count:

| | wave 1 (`F-1`) | wave 2 (`F-1`) |
| --- | --- | --- |
| minimum | 4.87x at L1/L2 beta 15 | 4.87x, value `0.486626`, at REL2 L1/L2 beta 15 |
| maximum | 31.03x (G-REL1) | 31.03x, value `3.103480` |
| entries below 6x | **15 of the 19 G-REL2 cells** — 13 further cells at exactly 5.71x and one at 4.97x | **TWO**, over all 29 X_null G-REL entries at the mean-over-8 reading — 4.87x and 4.97x |
| stated split | G-REL1 12.17x to 31.03x; G-REL2 4.87x to 6.00x | one range over all 29 entries |

Wave 1's G-REL2 range implies most G-REL2 cells sit below 0.6, i.e. below 6x; wave 2's
count implies 27 of 29 entries sit at or above 0.6. **I did not recompute either and I
hold no shell, so I do not adjudicate this.** It is recorded as an open numeric
discrepancy. Binding consequence, which costs nothing to obey: the corrected **endpoints
4.87x to 31.03x are citable and the false range "6 to 31" may never be re-cited**; the
**count of sub-6x entries is NOT CITABLE from either wave** until it is re-measured from
the committed `results_relvar.json`, which is a read of a committed file and no new
compute.

### 4.4 A scope divergence that is not a disagreement

Wave 1 had `fpylll` 0.6.4 and covers the reduction-dependent rows; **wave 2 did not have
it in either session** and covers none of them. So the L7/L8 portability result and its
C-F5 correction exist only in wave 1, and no wave-2 finding bears on `lam1n`, `hkz`, the
48 reductions or their reported max violation of 0.0. **INFRASTRUCTURE SIGNAL, never
negative mathematical evidence**, and never a defect of any producer or of either wave.
Both waves price the fix identically at one install plus about 20 s of reduction at
`d <= 40`; both call it the cheapest unclosed check.

---

## 5. (d) Does "R-OUT-1 STANDS", with AM-15 and AM-16, survive RT-R1 and RT-R3?

Answered in four parts, because the honest answer has four.

### 5.1 R-OUT-1 as a scoped proposition: SURVIVES, UNCHANGED

`DEC-20260809-afe29b`'s citable form of R-OUT-1 is already scoped to `q = 3329`,
`d in {20,30,40,100,140}`, the frozen `(k, beta)` grid, **8 frozen bases**, and no
reduction beyond the frozen HKZ pipeline at `d <= 40`. Those 8 frozen bases **are** the
family F1 differs from. RT-R1 exhibits no counterexample inside that scope; it exhibits a
nearby family outside it, and `EV-MLKEM-e45478`'s own boundary agrees: "R-OUT-1 IS CORRECT
WITHIN THE FROZEN FAMILY F0". **The two waves agree on the proposition** and differ only
in how loudly the family is named.

**What I add, and it is a citation rule rather than a correction.** Every downstream
citation of R-OUT-1 must name **the family as a scope parameter**, not only the
`(d, k, beta, q)` grid — because RT-R1 measured that the family is load-bearing, flipping
`G-VAR` from 38 of 38 to 0 of 38 under a change in exactly one respect. Wave 1's scope
lines list "8 frozen bases", which names the family only implicitly; that is now
insufficient and the rule binds forward.

### 5.2 AM-15: SURVIVES UNTOUCHED, and wave 2 strengthens its grounds

Nothing in wave 2 bears against it. AM-15 concerns consistency-check labelling and the
restatement of a non-citation carry as a rule about **quotation** rather than
**occurrence**. Wave-2's F-3 independently reports that the frozen pre-registration is
**internally inconsistent** on the 29-of-48 carry — it puts the count and its benchmark in
adjacent sentences while its own section 3.2 requires them in the same sentence — so a
successor enforcing the carry as an occurrence rule finds it unsatisfiable while quoting
P-B1 verbatim. That is precisely AM-15(b)'s diagnosis, reached independently. **AM-15 is
adopted unchanged and its grounds are now two-wave.**

### 5.3 AM-16: SURVIVES AS AN AMENDMENT, BUT ITS VALIDATION CLAUSE (d) IS SHOWN INSUFFICIENT

This is the reconciliation's operative finding on the instrument.

AM-16 replaces bit identity with a scaled, per-cell-profiled dispersion criterion (a),
requires every candidate to be scored through at least two declared arithmetic routes (b),
withdraws the all-cells reduction (c), and **validates G-VAR2 against the six routes
already built and committed in `probe_nullroute.py`, whose committed output declares the
target behaviour in advance** (d), with (e), (f), (g) covering graded guards, non-constant
SE injections, and dispersion beside count-style headlines.

**Every one of those six routes lives in F0.** RT-R1 shows that F0 is the family in which
a dispersion criterion has the **most** power against a determinant-only functional,
precisely because it holds `|det B|` fixed across the basis index. So a criterion
validated only against `probe_nullroute.py` would be scored in the one arrangement where
its own family-blindness cannot appear — which is exactly the could-not-fail pattern this
goal has recorded repeatedly, now one level up, at the level of the family rather than the
threshold.

Therefore:

- **AM-16 (a), (b), (c), (e), (f), (g) survive unchanged and are adopted.**
- **AM-16 (d) survives as NECESSARY and is recorded as NOT SUFFICIENT.** A criterion that
  passes it has been shown to resist re-presentation through a float path. It has **not**
  been shown to resist a change of family (RT-R1) or an information-free perturbation of
  relative size about `1e-10` (O-2).
- The two waves' validation objects are **complementary and neither alone suffices**:
  `probe_nullroute.py` (wave 1, route axis) and `probe_gvar_family.py` plus
  `probe_gvar_relabel_witness.py` (wave 2, family axis). Both are committed in this tree.

This is enacted as **AM-17(a)** in `DEC-20260812-2233ed`, prospective only. AM-16 is
**not re-litigated**: what is added is a clause its own validation object cannot supply.

### 5.4 The "either direction" closure: SURVIVES AS AN ABSTENTION, NOT AS A DEMONSTRATED CLOSURE

Per section 4.2. Concretely, and this is the one place a wave-1 sentence is narrowed:

- **The operational carry stands**: no admissibility claim may be reported from this gate,
  in either direction, and none is made anywhere in either chain or in this one.
- **The demonstrated basis is one-sided**: the PASS side is shown vacuous on the frozen
  family; the REFUSAL side is **untested in either direction** and its false-refusal rate
  has never been measured.
- `KN-FIND-2a35aa`'s opening paragraph and `DEC-20260809-afe29b`'s
  `what_is_not_decided` carry the closure reading. **They are not edited.** The narrowing
  travels by reference in `DEC-20260812-2233ed`, and the corpus debt it creates is
  recorded in section 6 below.
- **`EV-MLKEM-e45478` is NOT narrowed on RT-R3.** It is the one wave-2 finding that says
  something wave 1 neither said nor refuted, and it is credited in full.

This is enacted as **AM-17(b)**, prospective only: a closure over a gate must state
separately what was demonstrated on the PASS side and what on the REFUSAL side, and the
phrase "in either direction" may be used only when both sides were measured or when it is
explicitly labelled an abstention with its untested side named.

### 5.5 And AM-17(c), from wave-2 F-2

Every aggregation that collapses a per-unit array into a verdict — including collapses
**across cells and lattices**, not only across bases — must be declared as an
implementation completion, with the rule named, before the run. Grounds: `G_REL_PASS`'s
undeclared ANY rule, which selects an outcome row. R-OUT-1 is invariant to it and the
reported outcome is correct under the frozen text's own "majority" language, so this is a
disclosure rule and **not** a finding of producer non-compliance.

---

## 6. Knowledge promotion: not discharged here, and why, with the debt named

`DEC-20260812-15d3b2` **scheduled** the promotion to this reconciliation
(`knowledge_promotion.not_warranted`, reason 3, and reconciliation step 5). I do not
discharge it, and the reason is a scope fact rather than a judgement:

- **Neither my write scope nor the archive task's artifact paths carry `knowledge/`.** My
  `write_scope` is exactly this task directory. `TASK-20260812-a03011`'s declared
  `artifact_paths` are its receipt, `ledger/decisions/DEC-20260812-2233ed.yaml`,
  `ledger/evidence/EV-MLKEM-c7a814.yaml` and `ledger/goals/GOAL-MLKEM-005.yaml`. A
  `KN-FIND` written here could not be committed in the same archive commit as its
  regenerated index, which the `/curate-knowledge` convention requires, and an undeclared
  file in that commit is defect D3 reproduced.
- **The mandatory gate does not fire.** `DEC-20260812-2233ed` is `revise`; it is not
  `support` and not `reject_scoped`, and no hypothesis status moves.
- **The two candidate findings remain single-source.** RT-R1 and O-2 are each one
  construction, one session, re-executed by no party independent of the reviewer that
  built it. The fibre re-score carried in `goal_next_action_to_apply` is precisely the
  experiment that would supply the missing replication.

**The debt, named so it does not die here.** Two things are owed to the corpus and neither
is discharged:

1. `KN-FIND-2a35aa`'s opening paragraph carries the "in either direction" closure, and its
   section 4 prescribes a repair whose validation object is F0-only. Both are narrowed by
   RT-R1 and RT-R3. The instrument is a **successor `KN-FIND` entry narrowing it by
   reference** — exactly as `KN-FIND-2a35aa` itself narrowed `KN-FIND-f38a89` — and
   **never an edit**. `KN-FIND-2a35aa` is immutable and its `superseded_by` stays null.
2. The two knowledge promotions owed from `GOAL-MLKEM-003` remain owed and blocked on a
   second backend.

Both must be carried into the successor batch **with `knowledge/findings/` and
`knowledge/INDEX.md` in a declared write scope**, or they will be owed a fourth time.

---

## 7. Binding carries, restated and not re-litigated

- **CLAIM TIER TOY**, unconditionally. Nothing in BATCH-9e3584, in either wave, bears on
  ML-KEM security, on any FIPS 203 parameter set, on any attack cost, or on any cost model.
- **AM-10 through AM-14 of `DEC-20260808-05b684` and their binding carries are IN FORCE**
  and are not re-litigated here.
- **AM-3 IS NOT RETIRED.** Its power is undemonstrated rather than disproved, and its
  0.096 family-wise false-failure bound stands.
- **BATCH-a44d08 IS NOT RESCORED IN ANY RESPECT**; its Section C verdict and detection
  floors remain void in both directions.
- **The BATCH-cbe023 non-citable carries stand unchanged**: "the obstruction is
  relocated"; "29 of 48" without its exact-null benchmark of 47 of 48 in the same
  sentence; and "CONSISTENT", in either direction. The 3.91% floor is not citable without
  the NEGATIVE-VARIANCE-COMPONENT qualifier; the non-degenerate figure is 10.83%.
- **"a factor of 6 to 31" is CORRECTED to 4.87x to 31.03x and the false range may never be
  re-cited.** The count of entries below 6x is additionally non-citable pending
  re-measurement (section 4.3).
- **AM-15 and AM-16 of `DEC-20260809-afe29b` are adopted**, with AM-16(d) recorded as
  necessary and not sufficient (section 5.3). **AM-16 is not re-litigated.**
- **`TASK-20260809-60f9cc` is not run, in any form.** It is already `completed` against
  `5004932a9`.
- **`EV-MLKEM-9346bb` and `DEC-20260809-afe29b` are not re-minted.** This chain uses only
  `DEC-20260812-2233ed` and `EV-MLKEM-c7a814`.

---

## 8. One batch_log entry, not two

`DEC-20260812-15d3b2` reconciliation step 6 requires **one** `batch_log` entry for
BATCH-9e3584, naming both decisions, both evidence records, both review waves and both
snapshot commits. `DEC-20260812-2233ed.batch_log_instruction` carries the content for the
archive task to apply; two entries for one batch would misrepresent the batch as two.

## 9. What a later Coordinator needs to overturn me

- **To overturn the narrowing in 5.4** (that the closure survives only as an abstention):
  exhibit a measurement, in either wave or a successor, that bounds the gate's
  **false-refusal** rate. None exists in either chain; if one is found in the parts of the
  four reports I did not read in full (section 0.2), this narrowing falls and the
  instrument is a superseding record, not an edit.
- **To overturn 5.3** (that AM-16(d) is insufficient): show that `probe_gvar_family.py`'s
  F1 does not differ from F0 in exactly one respect, or that its 0-of-38 result does not
  reproduce. It costs 0.24 s. The Red Team named that could-not-fail arrangement in the
  probe's own docstring before running and asserted against it in the probe's output; a
  successor should check the assertion rather than take it.
- **To overturn the "two-sample agreement of one model" label in section 2**: produce an
  adapter probe receipt showing that the four reviewer sessions did **not** all resolve to
  one model. Every one of the four records `model_verified: false` with its reason, so this
  is a verification gap and not a settled fact; resolving it in the other direction would
  upgrade the whole of section 2 and nothing else in this note.
- **To resolve 4.3**: re-read the committed `results_relvar.json` and count the G-REL
  entries below 0.6. No new compute.
- **What cannot be overturned by argument, only by measurement:** the claim tier. It stays
  **TOY**.

## 10. Status

**UNCOMMITTED.** This note and both drafts sit uncommitted as written — PD-4, open and
inherited. None of it is durable or official until `TASK-20260812-a03011` stages the two
drafts verbatim to `ledger/decisions/` and `ledger/evidence/`, commits once and alone with
its receipt inside the commit carrying `commit_sha: null`, **runs the post-commit verifier
before the push and not after**, and pushes with an open PR against `main` naming
`DEC-20260812-2233ed`, `EV-MLKEM-c7a814` and `GOAL-MLKEM-005`. I wrote nothing under
`ledger/`, I touched no other file anywhere, and **I did not commit.**
