# Red team — BATCH-9e3584, Sections R, B', C1, C2

`TASK-20260809-444fe7` / `BATCH-9e3584` / `GOAL-MLKEM-005`.
Governed by the frozen contract
`tasks/TASK-20260809-4011dd/prereg.md`, sha256
`190cf4740b0ecefdbe7d1da0868a6258352b044ae5e99da470060f94049c70ea`
— recomputed at the shell in this session, and additionally recomputed from the
**blob at the notarizing commit** `1aa7db53` and from the sidecar; all three
agree with the value in the task card.

**CLAIM TIER TOY, UNCONDITIONALLY.** Nothing in this report bears on ML-KEM
security, on any FIPS 203 parameter set, on any attack cost, or on any cost
model. Every object I built is at `d <= 140`, `q <= 3329`. I changed no research
status, disposed of no hypothesis, promoted nothing to `knowledge/`, **rescored
no frozen verdict**, modified no producer artifact, wrote nothing outside my
`write_scope`, did not write, regenerate or stage `knowledge/INDEX.md`, and
**made no commit**.

## Inference record

```
requested_policy: review-adversarial
resolved:        anthropic:claude-opus-5 (effort=xhigh), from
                 `python3 -m orchestration.adapter resolve --role red-team --independent-session`
                 -> "review-adversarial -> anthropic:claude-opus-5 (effort=xhigh)"
answering_model: claude-opus-5   (the model actually serving this session)
fallback_used:   false
degraded:        false
independent_session: true (PROCEDURAL)
model_verified:  false
model_verified_reason: >-
  No adapter probe receipt exists for this session and the resolved model cannot
  be probed from inside a subagent. Per CLAUDE.md, per-role model selection is
  process-level under Claude Code and subagents keep `model: inherit`; the
  policy's reasoning effort binds per subagent. Recorded as a verification gap,
  never as satisfied.
```

**Independence in this goal is PROCEDURAL AND NEVER MODEL-LEVEL.** `AGENTS.md`
rule 12 is **UNMET AND UNWAIVED**: the same session authored the
pre-registration, ran all four producers and made both archives, and every
producer and reviewer across this goal and its two predecessor campaigns
resolves to the same model. I did not produce any artifact I review here. That
is separation of *session and task*, not of *model*, and it must not be
presented as more.

## Binding carries observed in this report

AM-10 .. AM-14 of `DEC-20260808-05b684` and their binding carries are in force
and are **not re-litigated**. **AM-3 is NOT retired** — its power remains
undemonstrated rather than disproved. **BATCH-a44d08 is not rescored in any
respect.** The phrases "the obstruction is relocated" and "CONSISTENT" (in
either direction) do not appear as claims anywhere below. "29 of 48" appears
only in the same sentence as the exact-null benchmark of 47 of 48. The `3.91%`
floor is cited only with its **NEGATIVE-VARIANCE-COMPONENT** qualifier; the
tightest non-degenerate floor is `10.83%`. `AM4-OBS-1` is not cited here at all;
where it would be, the route is `knowledge/findings/KN-FIND-f38a89.md` only.
`k = |K_I|` is the identity block throughout; `k_fpylll = d - k` (AM-9).

---

# 0. What I read, and what I verified rather than accepted

## 0.1 The two commits named on my card

I read the producer artifacts **as committed at `c034ef38`** and the frozen
pre-registration **as committed at `1aa7db53`**. Both are real, resolve, and are
ancestors of `HEAD` (`2fcad1f7e82be3bfb1c150b1b2f60f6e65532e0a`); I checked
`merge-base --is-ancestor` for each rather than accepting the dispatching
session's assertion. For every one of the 30 declared artifacts I compared the
**blob at the declared commit** against the working-tree file, so the bytes I
read are the committed bytes and no artifact moved under this review.

## 0.2 The Coordinator's git claims — CHECKED, NOT ACCEPTED

`COORDINATOR-ADJUDICATION-20260811.md` §0 states in terms that every statement
it makes about git is **attributed, not verified** ("I hold no shell and ran no
git command"), and both `COORDINATOR-DEFECT.md` files repeat it. My card
requires me to verify the three-way commit split, the 30-for-30 content match
and the D3 table myself, because a Validator already proved one such Coordinator
git claim false in this goal (BATCH-cbe023 F-1). I did, in
**`probes/probe_archive_record.py`** (read-only git; 2.06 s).

**Every checkable claim in the adjudication and both defect records is TRUE.**

| Coordinator claim | my independent finding | verdict |
| --- | --- | --- |
| `1aa7db53` changed exactly the 2 pre-registration files | 2 paths, both additions | **CONFIRMED** |
| `c034ef38` changed exactly the 28 producer files, parent `1aa7db53` | 28 paths, parent `1aa7db5313f6…` | **CONFIRMED** |
| `502d15a0` changed both receipts + `dispatch_queue.json`, no source artifact | 3 paths: 2 receipts + the queue | **CONFIRMED** |
| neither receipt rides inside the commit it declares | `receipt ∈ change set` is **False** for both | **CONFIRMED (D2)** |
| 30 declared artifacts, 30 match sha256, zero mismatches | 30/30 against the **blobs at the declared commits**, 30/30 against the working tree, 0 mismatches | **CONFIRMED, and by a stronger test than the one claimed** |
| D3: 9 of the 28 declared producer artifact names do not exist; 9 committed files undeclared | exactly 9 and 9, listed below | **CONFIRMED** |
| the frozen text is absent at `3d5dd80a` and `git log --all --follow` returns one commit | absent; exactly 1 commit | **CONFIRMED** |

**Two refinements I record because they matter downstream, neither of which
contradicts the Coordinator.**

1. **The receipts' own `path_sha256` maps are internally consistent with their
   commits.** For *both* archive tasks, the declared path set **equals** the
   commit's change set exactly. D3 is a defect of the **queue's**
   `artifact_paths`/`deliverables`, not of the receipts. The adjudication's
   phrase "nine of the 28 **declared** producer artifact paths do not exist" is
   true of the queue and false of the receipt; keeping the two apart matters,
   because a future reader who bins the receipt as unreliable loses the only
   correct declaration of what was committed. The defect record's own arithmetic
   ("had the receipt ridden inside `c034ef38`, the change-set test would still
   have failed with missing 10 and extra 9") checks out exactly: 9 dangling + 1
   receipt = 10 missing, 9 undeclared = 9 extra.
2. **Two of the adjudication's three UNKNOWNs are resolvable and I resolved
   them.** Both archive commit messages **do** contain their task id and
   `GOAL-MLKEM-005` (`research_dispatch.py:1103-1114` is satisfied), and both
   **do** record the base commit checked — in the commit message, not the
   receipt: "Base checked: origin/main `3d5dd80a…`". So the only surviving
   failure is the change-set equality test, and the only surviving UNKNOWN is
   push/PR state, which is not decidable from this clone. This narrows the
   defect rather than widening it.

The nine dangling names, which **must not be cited by any downstream record**,
and the nine committed names that replace them:

| task | queue declares (DANGLING — no such file) | committed, and what I cite |
| --- | --- | --- |
| `-311784` | `measure_bnull.py`, `report_bnull.md`, `results_bnull.json` | `measure_nullfam.py`, `report_nullfam.md`, `results_nullfam.json` |
| `-97d6cf` | `measure_ctau.py`, `report_ctau.md`, `results_ctau.json` | `rescore_c1.py`, `report_c1.md`, `results_c1.json` |
| `-3eb72c` | `measure_cposctl.py`, `report_cposctl.md`, `results_cposctl.json` | `posctl_c2.py`, `report_c2.md`, `results_c2.json` |
| `-cda2f6` | — | `measure_relvar.py`, `report_relvar.md`, `results_relvar.json` (unchanged) |

**Every citation in this report uses the committed names.**

## 0.3 The notarization property, re-derived

`prereg.md` first appears at `1aa7db53` (committer date 13:10:41Z), is absent at
its parent `3d5dd80a`, and `git log --all --follow` returns exactly one commit
for it. **No producer artifact exists at `1aa7db53`** — I checked
`run_manifest.yaml` and `command.txt` for all four producers. Exactly two
commits in the entire history touch any `BATCH-9e3584/tasks/` path. The four
producers' recorded completion times are 13:16:20Z, 13:25:29Z, 13:26:05Z and
13:27:55Z, all after 13:10:41Z.

**The residual trust assumption, named because it is not eliminable by git.**
What the record proves is that no producer artifact entered the repository
before the frozen text did. It does **not** prove that no *measurement* was
performed earlier and committed later; the run timestamps are self-reported by
the same session. The runtime blob check each producer performs pins the *text*,
not the *clock*. The pattern is sound and I do not object to it — I record its
exact reach so that no successor over-reads it.

---

# 1. PRIMARY TARGET — the lead reports the gate INADMISSIBLE under `G-VAR`

My card directs: *if the lead reports the gate INADMISSIBLE under G-VAR, attack
the generality of the refusal and find the observable it did not consider.*

`report_relvar.md` §2 (`R-OUT-1`): `X_null` walks the entire AM-4 gate while
bit-identical across all 8 frozen bases at all 38 scored cells; `G-VAR` fires;
the gate is INADMISSIBLE and **no admissibility claim is reportable from it in
either direction**. `OBS-R1`: `X8 = rdet`, an unplanted member of the frozen
ten-candidate list, is also bit-identical at all 38 cells.

## 1.0 First, what I independently confirm

**`probes/probe_gvar_family.py`** re-implements the frozen family from the
producer's own `make_A`, computes `rdet` through the same `slogdet` path and
`X_null` **through the matrix** (see RT-R2), and applies the producer's own
`bit_identical()` function. On a different environment (numpy 2.4.6, scipy
1.17.1, python 3.11.15, no fpylll):

* `G-VAR` fires on `rdet` at **38 of 38** cells and on `X_null` at **38 of 38** —
  the producer's headline and `OBS-R1` reproduce exactly;
* `X_null` passes `G-REL1` at **10 of 10** lattices and `G-REL2` at **19 of 19**
  mirrored cells; `rdet` passes `G-REL2` at **19 of 19** — the producer's counts
  reproduce exactly;
* the notarized `prereg` §2.6 closed-form table reproduces at **38 of 38** cells
  to `< 1e-6` through an independent matrix path.

Nothing in what follows disputes those numbers. **The objection is to what the
refusal is taken to mean, and to how far it generalizes.**

## RT-R1 — `G-VAR` measures a property of the FAMILY, not of the observable; the proposed repair does not repair the gate

**BUILT, NOT PROPOSED.** `probes/probe_gvar_family.py` builds the nearest object
that differs in **exactly one respect** and scores it through the identical code
path:

```
F0  frozen  B_i = [[I_k, A_i],[0, q I_{d-k}]]      |det| = q^(d-k)      CONSTANT in i
F1  nearby  B_i = [[I_k, A_i],[0, diag(m_i)]]      m_i[0] = q+i         VARIES in i
```

`A_i` is the *same draw* in both; `d`, `k`, the beta grid, the mirrored pairs,
`tau_rel = 0.10`, `s_X = 1.0` and the code path are held fixed. In **both**
families `rdet` and `X_null` read **zero entries of `A_i`**: their blindness to
the basis content is identical and provable.

| | `G-VAR` fires on `rdet` | on `X_null` | `X_null` `G-REL1` | `X_null` `G-REL2` |
| --- | --- | --- | --- | --- |
| **F0** (frozen) | 38 / 38 | 38 / 38 | 10 / 10 PASS | 19 / 19 PASS |
| **F1** (nearby) | **0 / 38** | **0 / 38** | 10 / 10 PASS | 19 / 19 PASS |

**In F1 the gate *repaired with `G-VAR`* admits `X_null`.** The
`probes/probe_gvar_relabel_witness.py` witness sharpens it: at every cell tested,
F1's `X_null` takes **8 distinct IEEE-754 values, strictly increasing in the
basis index `i`**, and its entire between-basis variation is a monotone
relabelling of that index.

The consequence for the report's §5(iii) — *"does the gate need a dispersion
criterion? Yes, and it needs more than one"* — is that adding `G-VAR` is **not**
the repair. `G-VAR` as written ("non-zero between-basis dispersion at fixed
`(d, k, beta, q)`") refuses an observable exactly when the family holds that
observable's own argument constant. It is a joint property of *(observable,
family)*. `R-OUT-1` is therefore correct **within F0** and is not a portable
admissibility clause.

**Reported against my own thesis, at the same weight (this is the part that cuts
for the producer).** F0 is not the wrong family; it is the family in which
`G-VAR` has the *most* power against a determinant-only functional, precisely
because it holds `|det|` fixed. And in F1 the determinant genuinely differs
between lattices, so admitting a determinant functional there is not obviously
an error. The objection survives both concessions in this narrower and still
material form: **`G-VAR` cannot distinguish "this observable reads the instance"
from "this observable reads a nuisance parameter that happens to vary across the
family", and nothing in the batch tests it against a family where those differ.**

**The missing separator, named.** What the gate lacks is not dispersion but
*dispersion conditioned on the observable's own arguments*: a clause requiring
`X` to be non-constant on the fibre of the family over whatever `X` is a
function of. Operationally: every candidate must be scored on a family
constructed to hold its declared argument fixed, and `G-VAR` must be evaluated
there. That is cheap — 0.24 s in this instance — and it is the concrete forward
guidance the closure currently lacks.

## RT-R2 — `R-OUT-3` could not fire: the instrument-defect detector does not exist

`prereg` §2.6 states that the measuring task "recomputes [the `X_null` table]
through the identical code path and must reproduce this table; a departure is a
defect in the code path", and `R-OUT-3` is the row for "passes the gate but
dispersion is non-zero → **DEFECT IN THE INSTRUMENT**".

`measure_relvar.py:260` implements

```python
def x_null_of(d, k, beta, q):
    return (beta / d) * (1.0 / d) * ((d - k) * math.log(q)) if q > 1 else 0.0
```

— the **closed form**, which never touches the matrix. The producer discloses
this in the docstring. The consequence, which the report does not draw, is that
**`R-OUT-3` is unreachable by construction**: a function with no `i` argument
cannot produce non-zero between-basis dispersion, and the "recomputation" of the
§2.6 table is a tautology that cannot detect a code-path defect. `P-R3` is
therefore not merely "forced by algebra"; it is forced by the **source code**,
which is a strictly stronger statement than the report's already-honest
"UNTESTED".

**This objection comes with its remedy, already run.** `probe_gvar_family.py`
computes `X_null` definitionally, `(beta/d)(1/d)·log|det B|`, from `slogdet` of
the actual integer matrix, and reproduces the notarized §2.6 table at **38 of 38
cells**. The instrument check `R-OUT-3` promised now exists and passes.

## RT-R3 — the closure over-reaches in the safe direction: only the PASS side was shown vacuous

"**NO ADMISSIBILITY CLAIM IS REPORTABLE FROM THIS GATE IN EITHER DIRECTION**" is
a closure, and `docs/inventor-protocol.md` §4 holds a closure to a named
obstruction, an argument, and forward guidance naming what remains open. The
obstruction is named and the argument is sound. But what was demonstrated is
that **passing** the gate carries no information: a blind closed form clears
every clause. Nothing was shown about the **refusal** side. A candidate that the
gate rejects — `lam1n` fails `G-REL2` at 2 of 8 bases, `hkz` fails it at every
computable cell — is rejected by a criterion whose *false-refusal* rate has never
been measured.

Note the direction of the error: the batch closes **more** than it showed, in the
conservative direction. Under the inventor protocol that is a failure mode
symmetric with overclaiming, and preserving the narrowest valid conclusion here
means stating a **wider** result than the report does:

> the AM-4/AM-8 gate's PASS side is uninformative on the frozen family, because
> a parameter-determined closed form and an unplanted member of the frozen
> candidate list both clear it; the gate's FAIL side is **untested in either
> direction**, and `G-VAR` does not repair the PASS side outside F0.

**Cheapest test of the untested side, with its cost.** Build one observable that
is informative by construction *and* structurally refused — e.g. a statistic
over the leading `k` raw-GSO log-norms, which depends on `A` and on `k` but takes
no `beta` argument and therefore fails `REL-1` by algebra exactly as `rdet` and
`lam1n` do. If the gate refuses a quantity that demonstrably separates the
mirrored pairs, the refusal side is shown vacuous too and the closure is earned.
**Cost: minutes of numpy, one QR per basis, no reduction, `d <= 140`.** I did not
run it: it is a new candidate rather than an attack on a reported number, and
introducing candidates is the Idea Generator's and the Coordinator's business,
not mine.

## RT-R4 — the headline needed no measurement, and the compute bought three other things

`R-OUT-1`'s two conjuncts were both derivable from the notarized text before the
run: §2.6 pre-computes `X_null`'s `G-REL1`/`G-REL2` passes in closed form, §2.7
lists `G-INV`/`G-Q` as FORCED, and §2.5 plus the closed form give zero
dispersion. The report says so plainly (four of seven predictions FORCED,
reported as UNTESTED), which is exactly right and is why this is an objection
about *interpretation*, not about honesty.

The consequence for the record: the LEAD's headline is a **design audit of a
gate**, obtainable at zero compute, and the 48.4 s of measurement bought three
genuinely empirical items — `X_mp`'s pass (10/10 and 14/19, with a live
`R-OUT-5`), the `L7/L8` replication, and the normalization disagreement at 3
cells. Only the second could have disagreed with an external measurement. A
successor should not read `R-OUT-1` as evidence that the measurement campaign was
necessary for it.

## RT-R5 — the non-frozen aggregation rule: verified, and one reading not tested

`report_relvar.md` §9.1 discloses that the pre-registration never froze a rule
for collapsing 8 per-basis criterion values into one verdict, and claims the
three reported readings agree at every cell. **I checked all 117 computable
cells in `results_relvar.json`: 0 disagreements** between {mean over 8, legacy
`i = 0`, majority of 8}. The disclosure is accurate and no headline depends on
the choice.

One reading was not among the three: **unanimity**. `hkz`'s `G-REL1` at `L8` has
mean 0.13848 with `n_pass = 7 of 8`, so under an all-8-must-pass rule it would
flip. No headline moves (`hkz` already fails `G-REL` through `REL-2`), so this is
a caveat and not a defect — but a successor that freezes an aggregation rule
should freeze it before, not after, seeing that three readings happened to agree.

## RT-R6 — what I could not check: INFRASTRUCTURE, never negative evidence

`fpylll` is **absent** in this session's environment. I could not re-run the HKZ
pipeline, and therefore did **not** independently re-verify: the 48 reductions
and their `max hkz_violation = 0.0`; `lam1n` and `hkz` at any cell; or the
`L7/L8` replication that the report calls its strongest result and reports as
agreeing with the earlier review measurement to every digit. **This is
infrastructure signal and is not evidence against any of it.** Cost to close:
one `fpylll` install plus ~20 s of reduction at `d <= 40` — the cheapest
unclosed check in this review, and I name it as the first thing an independent
replication should do.

---

# 2. Section B' — `n_fire` is reported from one realization of a random object

`report_nullfam.md` §1: *"On the rebuilt null family, `n_fire(c = 6)` is 35 of
48, against the committed real count of 29 of 48 and the Red Team's exact-null
benchmark of 47 of 48."* §2 reads a **FAIL** of the decay check from `35 >= 29`
and concludes the count is an **ARTIFACT**.

## RT-B1 — AM-11's dispersion requirement was not applied to this section's own headline statistic

`n_fire` is a **newly proposed statistic computed on a random object** — 13
independently drawn Haar frame stacks — reported from **one** draw with **no
dispersion**, while the pre-registered decision boundary ("materially below = at
least 8 of 48") is a fixed constant. AM-10 requires replication and AM-11
requires dispersion; Section R applied both to `G-REL` and Section B' applied
neither to `n_fire`.

**BUILT: `probes/probe_nfire_dispersion.py`.** It imports the producer's own
module and reuses `make_errors`, `haar_frames`, `project`, `arm_r_values`,
`se_of_difference` and `score_cell` verbatim, holding the CBD error sample, the
carried Haar arm that sets `SE_diff`, `q_Beta`, `N_ERR`, `CHUNK`, `N_DRAW`,
`t_crit`, `GATE_K` and the `c` grid **fixed**, and varying **only** the 13-frame
family's seeds through a disjoint offset. 8 replicates, 610.4 s.

```
n_fire(c = 6) over 8 independent null families:  28, 37, 36, 32, 32, 29, 28, 35
mean 32.12    sd 3.60 (ddof 1)    min 28    max 37    range 9
```

Readings, in order of how much they matter:

1. **The decay-check FAIL survives.** No replicate comes near the PASS threshold
   of `<= 21`; the minimum is 28, seven steps above it. The frozen "materially
   below" margin of 8 of 48 is `2.2x` the measured sd, so the PASS side is
   properly separated. **The producer's substantive verdict — the count does not
   decay, so it is an artifact — is robust across realizations, and I say so as
   loudly as I say the rest.**
2. **The headline *sentence* is not robust.** "The null fires **more often than
   the real arm**" is realization-dependent: **2 of 8** replicates fire *less*
   often than the committed real count (28 < 29, twice). The FAIL boundary sits
   `0.87 sd` from the null family's own mean, so a single draw cannot reliably
   place the count on one side of it.
3. **The reported 35 is a high draw**, `0.80 sd` above the replicate mean of
   32.12. The honest report of this statistic is `32.1 +/- 3.6`, not `35`.
4. **`c = 6` is the least stable point of the whole `c` grid.** Across
   replicates: sd at `c = 4` is 1.20, at `c = 6` is **3.60**, at `c = 8` is 1.19,
   and 0.00 at every `c >= 12`. The carried headline constant lands exactly on
   the steep part of the transition — which the producer's own §3 mechanism
   (`c_min ≈ 1 + t_crit·SE_step/SE_diff ≈ 5.5`, just below 6) predicts and does
   not connect to the instability of the reported number.
5. **My figure is a LOWER BOUND.** The error sample and the Haar arm are frozen
   across my replicates, so 3.60 understates the total sampling dispersion of
   `n_fire`. A wider replication can only widen it.

Corroborations of the producer inside the same probe: 0 degenerate steps in every
replicate (matching "all 48 are live"); `se_step/se_diff` medians 0.95–1.14
(matching the reported 1.05–1.08); `n_fire` monotone non-decreasing in `c` in
every replicate.

**This does not retire AM-3.** Its power remains **undemonstrated rather than
disproved** and its `0.096` family-wise false-failure bound stands.

## RT-B2 — the decision rule has a margin on one side only

`prereg` §3.3 gives PASS a quantitative margin (8 of 48, set in advance) and
gives FAIL a bare inequality (`null >= real`). Applied to a statistic with
sd 3.6, a bare inequality at a boundary 0.87 sd from the mean is a coin-weighting
rather than a test. **The cheapest repair, for a successor: state the FAIL side
with its own margin, in units of the statistic's measured between-replicate sd,
and measure that sd in the same run.** Cost: `~75 s x R` replicates; `R = 8`
took 610 s here on a shared 4-core host.

---

# 3. Section C1 — the section's only live finding is a controlled null

`report_c1.md` produced four results. Three are declared-in-advance non-events
and are correctly labelled as such: 0 FALSIFYING at both floors; all ten verdicts
invariant to the repair (prereg §4.5 declared this the predicted outcome before
the re-score); and `P-C1a` **FALSIFIED** with the producer stating that the
arithmetic could have told it so beforehand. That leaves **AM-14(e)** —

> "FOUR of ten targets have `SE_2way/SE_naive < 1` ... A ratio below 1 is **in
> tension with AM-7 clause (1)**"

— carrying the section's entire live content.

## RT-C1a — first, the arithmetic reproduces exactly

**`probes/probe_c1_seratio_null.py`** recomputes `SE_2way`, `nu_eff` and the
ratio from the committed raw `8 x 4` tables. All ten ratios reproduce the
report's table **to four decimals** (1.0416, 1.2196, 0.3635, 1.0736, 1.2299,
0.8495, 1.3686, 0.9651, 1.1810, 0.8397), and the recomputed `SE_Delta_bar`
matches the committed value at **relative deviation exactly 0.0** at all ten
targets. Section C1's arithmetic is correct and I found nothing wrong with it.

## RT-C1b — the missing null: 4 of 10 below 1 is exactly what an effect-free table gives

`docs/inventor-protocol.md` §3 asks what the reported quantity should have done.
If `ratio < 1` is a finding about the instrument, an `8 x 4` table with **no**
support effect and **no** pool effect should not produce it at a comparable rate.
The identical `se_decomposition()` (carried verbatim, degenerate branch included)
on 200,000 iid-normal null tables:

```
P(SE_2way / SE_naive < 1) = 0.3982   ->  expected 3.98 of 10 targets
observed                            :  4 of 10
null median 1.0896   null p05 0.3871   null p01 0.1785
```

**The count is the null expectation to two decimal places.** A permutation null —
each target's own 32 entries shuffled, destroying the support x pool structure
while keeping its marginal exactly — agrees target by target (percentiles within
0.03 of the iid null everywhere).

The extreme value is a different question and is scored separately: `0.3635` sits
at the **4.4th percentile** of the iid null and the **4.1st** of its own
permutation null. Across 10 targets, the chance that at least one falls that low
is `1 - 0.956^10 ≈ 36%`. **So the extreme is unremarkable too.**

**Objection, stated narrowly.** AM-14(e)'s disclosure requirement was met — the
ratios are reported per target, which is what AM-14(e) asks. What is not
supported is the *interpretation* attached to them: "in tension with AM-7 clause
(1)" reads a signal off a statistic whose null this batch did not measure. The
correct statement is that the ratio, at `S = 8`, `E = 4`, **does not
discriminate**: its null is centred at 1.09 with a 5th percentile of 0.39, so
individual targets below 1 are routine. Under the inventor protocol this is a
**controlled null**, not a finding, in either direction — it is equally not
evidence that the instrument is sound.

## RT-C1c — the "degenerate regime" is a property of the `S = 8, E = 4` design

`report_c2.md` §5 records that four targets cannot fire even at a 12 SE
injection, their `|t|crit` running 18.9 to 70.0 on `nu_eff` between 1.00 and
1.50, and calls this correct behaviour in the degenerate regime. Nobody asked
what an effect-free table does. **`probes/probe_c1_nueff_null.py`**, 100,000
draws per model:

| null model | `P(nu_eff <= 1.5)` | `P(|t|crit >= 8)` | expected count of 10 | `P(neg. var. comp.)` |
| --- | --- | --- | --- | --- |
| iid normal, no structure | 0.357 | **0.527** | **5.27** | 0.143 |
| with support + pool structure (0.4 / 0.2 / 0.4) | 0.006 | 0.014 | 0.14 | 0.0003 |
| **committed data** | — | — | **4 of 10** | **1 of 10** (null expectation 1.43) |

**More than half of effect-free `8 x 4` tables produce a critical value the
12 SE ladder cannot reach.** The committed profile — 4 of 10 degenerate, 1 of 10
negative-variance-component — sits *below* the unstructured null's expectation
and far above the structured null's. Two conclusions, kept apart:

* **About the instrument (supported):** at `S = 8, E = 4` with Satterthwaite on
  three mean squares, the two-way SE is degenerate often enough that the Section
  C instrument has no resolving power at a large fraction of targets **by
  design**. C2's `P-C2d` was scoped to targets with `|t|crit < 8` — a correct
  pre-registration, but it means the positive control tested **6 of 10** targets
  and the other four were structurally untestable at any rung.
* **About the data (NOT supported, and I do not claim it):** a degeneracy profile
  matching an unstructured null does **not** prove the targets carry no
  structure. It means the four non-firing targets are **uninformative**, not that
  they are null. No label is asserted or negated, in either direction.

**Forward guidance, which is what the closure standard requires:** the binding
constraint on Section C is `E = 4`, not `tau_rel`. Re-deriving the floor from
0.15 to 0.025 could not have changed a verdict (prereg §4.5 said so in advance,
and it did not); raising `E`, or replacing Satterthwaite with a design whose
`nu_eff` is bounded below, is the only change that moves the instrument's
resolving power. That is a concrete successor experiment, and it is cheap: no
reduction, no new draw at the frame level, only more pools.

---

# 4. Section C2 — I ran the repair it deferred, and it corroborates the producer

`report_c2.md` recorded `P-C2c` **FALSIFIED** (one target fired at
`delta/SE = 1.0`), then **refused** the consequence its own pre-registration
declared ("the instrument is over-sensitive"), diagnosing instead that the
target's committed `|Delta_bar|` was already `4.5295 SE` — `88.5%` of its own
`|t|crit` — so a constant additive injection cannot separate sensitivity from a
pre-existing near-critical effect. It pre-registered a **CENTERED** variant for a
successor and deliberately did not run it, on the stated ground that adding an
unregistered analysis to rescue a falsified prediction is the failure mode the
batch exists to close.

**That is correct conduct, and it left the diagnosis untested. Testing another
agent's deferred repair is my job, not theirs.**
**`probes/probe_c2_centered.py`** subtracts each target's own `Delta_bar` from
its committed raw `8 x 4` table and runs the identical ladder through the
identical `full_score()` path:

```
fired at delta/SE <= 1, UNCENTERED :  d140_b40/graded_t0.0050 @ 1.0   (reproduces the producer)
fired at delta/SE <= 1, CENTERED   :  none
max centered SE recovery deviation :  8.527e-16   (the producer reports 8.53e-16)
targets with |t|crit < 8 firing at 12 SE, centered : 6 of 6
```

**The producer's diagnosis is corroborated by measurement.** With the
pre-existing effect removed, no target fires at the "should not catch" rungs, and
`P-C2d`'s 6-of-6 holds. The "over-sensitive" reading its own pre-registration
declared is **not** supported, exactly as the producer argued without the
measurement. **This finding runs against my adversarial prior and is reported at
the same weight as my objections.**

## RT-C2a — the honest limit of my own probe

After centering, `|t| = delta/SE` exactly, and the minimum `|t|crit` over the ten
targets is 2.78, so **the t-clause cannot fire at rungs 0.5 and 1.0 by
arithmetic**. My probe is therefore in a could-not-FIRE arrangement on that
clause, and I named it in the probe's own docstring before running it. Its live
content is (a) that the *implemented* path behaves as the algebra says — the same
thing AM-14(b) asked of C2 itself — and (b) the relative-difference clause, which
is not forced. I report the result as an implementation check, never as a test
that could have failed mathematically.

## RT-C2b — `P-C2e` is forced, and the report says so obliquely

"Recovered SE = committed SE to `1e-12`" is guaranteed in exact arithmetic
because a constant offset leaves every variance component unchanged; the
producer states the algebra in prereg §5.2 and then presents `8.53e-16` as
`P-C2e` HOLDS. It is a floating-point check of an implementation, which is
valuable and is what AM-14(b) asked for, but it is **not** a test of the SE
construction that could have failed mathematically. The only way this check
fires is an implementation bug — worth having, worth labelling as such.

---

# 5. The gate's requirement: for EACH producer, the arrangement in which its check could not have failed, IN BOTH DIRECTIONS, and whether it ran in it

| producer | could-not-**FIRE** arrangement | ran in it? | could-not-**PASS** arrangement | ran in it? |
| --- | --- | --- | --- | --- |
| **`-cda2f6` (R) — `G-VAR`** | dispersion decided by a loose tolerance, so float noise lifts everything above the bar and nothing is refused | **NO** — bit-identity of IEEE-754 doubles, verified by me with the producer's own `bit_identical()` reproducing 38/38 | every scored candidate is a closed form, so `G-VAR` refuses everything and inadmissibility is trivial | **NO** — `lam1n`, `hkz`, `rawtail` have 0 bit-identical cells |
| **`-cda2f6` (R) — `G-VAR`, THIRD arrangement, NOT NAMED by the prereg** | — | **YES, IT RAN IN IT.** `G-VAR` cannot fail to fire on *any* determinant-only functional in a family that holds `\|det\|` constant across `i`, which the frozen family does by construction. The could-not-FAIL arrangement is at the level of the **family**, not the threshold. Demonstrated by `probe_gvar_family.py` (F1: 0/38) | — | — |
| **`-cda2f6` (R) — `G-REL`** | evaluated at `\|X\|` normalization only, where small `\|X\|` clears 0.10 on noise | **NO** — both normalizations at every entry with `s_X/\|X\|` beside them | `\|X\| << s_X` pins the denominator at 1.0, so nothing can ever clear it | **NO** — `X_mp` passes 10/10 and 14/19 |
| **`-cda2f6` (R) — `R-OUT-3` instrument-defect row** | — | **YES, IT RAN IN IT.** `x_null_of` takes no basis index, so "passes but non-zero dispersion" is unreachable and the promised code-path check is vacuous. Supplied by me: 38/38 through a matrix path | the row could not have been reached in the PASS direction either | **YES** — same cause |
| **`-cda2f6` (R) — `X_mp` MUST-PASS** | `X_mp` chosen after seeing which candidates pass | **NO** — fixed in the notarized text; I verified §1.4 is in the blob at `1aa7db53` | `X_mp` could not fail | **NO** — it failed 5 of 19 `REL-2` cells, all at `beta = d/2` where the gap is zero by symmetry and all below their own floors |
| **`-311784` (B')** | the null can never look like the real arm, because it is built by a different pipeline | **NO** — I read the code: errors, chunking, quantile estimator, `n_draw`, `SE`, `t_crit`, `GATE_K` and the `c` grid are identical; only the frame seeds differ | the null can never differ from the real arm, because `c_min` is dominated by `t_crit·SE_step/SE_diff` | **YES — AND DECLARED IN ADVANCE** as a FAIL/artifact rather than a null result (prereg §3.3, §3.5). Correct conduct |
| **`-311784` (B') — arrangement NOT NAMED in either direction** | — | **YES, IT RAN IN IT.** `n_fire` is one realization of a random object with no dispersion, and the FAIL boundary sits 0.87 sd from the statistic's own replicate mean (`probe_nfire_dispersion.py`) | — | — |
| **`-97d6cf` (C1)** | the re-score changes nothing because clause (i) binds at every target | **YES — AND DECLARED IN ADVANCE** (prereg §4.5 named it the most likely outcome, before the re-score). Correct conduct; the primary axis had one reachable outcome | the widened band is so wide every target enters it | **NO** — 1 of 10 |
| **`-97d6cf` (C1) — arrangement NOT NAMED** | — | **YES, IT RAN IN IT.** AM-14(e)'s ratio was interpreted with no null; its null gives 3.98 of 10 below 1 against 4 observed (`probe_c1_seratio_null.py`) | — | — |
| **`-3eb72c` (C2)** | the offset is applied to `Delta_bar` after the decomposition, so `SE` cannot change | **NO** — injected into the raw `S x E` table; I reproduced the recovery at `8.527e-16` independently | the ladder starts so high that every rung fires | **NO** — starts at 0.5 SE, and the bottom rung fired at exactly one target, which is why the falsification is on the record |
| **`-3eb72c` (C2) — arrangement NOT NAMED** | — | **YES, IT RAN IN IT.** Four of ten targets have `|t|crit` of 18.9–70.0 and cannot fire at any rung of a ladder topping out at 12 SE; the control therefore tested 6 of 10 targets. `probe_c1_nueff_null.py` shows that degeneracy rate is the design's, not the data's | — | — |

---

# 6. AM-10 (replication) and AM-11 (dispersion) applied to EVERY statistic, including newly proposed ones

| statistic | proposed by | replicated? | dispersion reported? | my finding |
| --- | --- | --- | --- | --- |
| `G-REL1`/`G-REL2` per candidate | R | YES, over 8 bases | YES (`sd_k`, `sd_dmk`, `sd_g`, paired `t`, detection floor) | compliant; I reproduce the F0 counts independently |
| between-basis dispersion / bit-identity | R | YES, 8 bases | YES (bit test + float sd beside it) | compliant; 38/38 reproduced. **But see RT-R1**: the dispersion is family-conditional and the family was not varied |
| `X_null` closed-form table | R | "recomputed" via the same closed form | n/a | **NOT a replication** (RT-R2). I supply a genuine matrix-path check: 38/38 |
| mirrored gap `mean_g`, paired `t` at `L7/L8` | R | YES, 8 bases, and against an earlier review measurement | YES | **could not re-verify — `fpylll` absent (INFRASTRUCTURE, not evidence)** |
| `n_fire(c)` on the null family | **B' — NEW** | **NO** | **NO** | **the principal AM-10/AM-11 gap.** I supply 8 replicates: `32.12 +/- 3.60`, range 28–37 |
| `se_step/se_diff` median | B' | NO | per-cell median only | my replicates give 0.95–1.14, consistent |
| `tau_rel_rebuilt = 0.025` | C1 | derived from committed medians | n/a (a threshold, not an estimate) | arithmetic verified: `1.67 x 0.01496443 = 0.02499060` |
| `SE_2way/SE_naive` | **C1 — NEW** | deterministic; no replicate exists | **NO null, NO dispersion** | I supply both: null `P(<1) = 0.3982`, expected 3.98 of 10 vs 4 observed → **controlled null** |
| `nu_eff`, `\|t\|crit` | C1/C2 | deterministic | per target, no null | I supply the null: `P(\|t\|crit >= 8) = 0.527` under no structure → degeneracy is a design property |
| SE recovery at every rung | C2 | 10 targets x 9 rungs | max deviation reported | reproduced at `8.527e-16`; **forced in exact arithmetic** (RT-C2b) |
| `\|t\|` monotonicity in `delta` | C2 | 10 of 10 | n/a | forced by the same algebra |

---

# 7. Cheapest falsification of every headline, WITH ITS COST

| headline | cheapest falsifier | cost | run? | outcome |
| --- | --- | --- | --- | --- |
| R: the gate is INADMISSIBLE under `G-VAR` (`R-OUT-1`) | a family of the same q-ary shape in which the determinant varies across `i`, scored through the identical path | **0.24 s numpy**, no reduction | **YES** | refusal holds in F0; `G-VAR` fires 0/38 in F1, so the proposed repair does not generalize |
| R: `OBS-R1`, `rdet` is parameter-determined | the same probe | included above | **YES** | confirmed in F0, dissolved in F1 — it is a statement about the frozen family |
| R: `R3` for `hkz` survives replication | replicate `L7/L8` under a different seed family / more bases and find `\|t\| >= t_crit` | ~20 s of fpylll at `d <= 40` + one install | **NO — fpylll absent (INFRASTRUCTURE)** | the cheapest unclosed check in this review |
| R: `R1` is populated (2 of 5 pass `G-REL`) | apply a unanimity aggregation rule | seconds, from `results_relvar.json` | **YES** | `hkz` `G-REL1` at `L8` would flip (7/8); no headline moves |
| B': the null fires more often than the real arm; decay check FAIL | replicate the null family at independent seed offsets | **~75 s per replicate**; 8 replicates = 610 s | **YES** | FAIL verdict robust (min 28, PASS needs <= 21); the *sentence* is not — 2 of 8 replicates fire less often than the real arm |
| C1: all ten verdicts invariant to the repair | none needed — forced by arithmetic and declared in advance | 0 | n/a | not contested |
| C1: 4 of 10 ratios below 1 are "in tension with AM-7 clause (1)" | the same statistic on an effect-free `8 x 4` table | **7 s** | **YES** | controlled null: expected 3.98 of 10 |
| C2: the instrument is clean on the SE axis | none available — forced in exact arithmetic; only an implementation bug can fire it | 0 | n/a | reproduced at `8.527e-16` |
| C2: `P-C2c`'s diagnosis (a pre-existing near-critical effect, not over-sensitivity) | the CENTERED ladder the producer deferred | **0.04 s** | **YES** | diagnosis **corroborated**; no centered target fires at `<= 1 SE` |
| Coordinator: three-way split, 30-for-30, D3 | re-run git and re-hash every declared path | **2.06 s** | **YES** | every claim confirmed; two UNKNOWNs resolved in the Coordinator's favour |

---

# 8. Where the measurement went against my own thesis

Reported at the same weight as my objections, per my card:

1. **C2's diagnosis of its own falsified prediction is right.** I ran the
   centered control expecting it to be a live test of over-sensitivity. It is
   not: nothing fires at `<= 1 SE` once the pre-existing effect is removed. The
   producer reached that conclusion by argument and declined to run the
   measurement, and the measurement agrees with the argument.
2. **B's substantive verdict survives replication.** I set out to test whether
   `35 of 48` was a lucky draw. It is a high draw — but no replicate comes within
   seven steps of the PASS threshold, so "the count does not decay when the
   parameter meant to destroy it is applied" holds at every one of 8 seed
   families. The artifact verdict is robust; only the headline sentence is not.
3. **Every Coordinator claim about git that I could check is true.** I went
   looking for a second BATCH-cbe023 F-1 and did not find one; the two facts the
   adjudication left UNKNOWN both resolve in its favour, which *narrows* the
   defect it recorded against itself.
4. **The producers' arithmetic reproduces exactly wherever I could re-derive it**
   — `SE_Delta_bar` at relative deviation `0.0` across all ten C1 targets, all
   ten `SE_2way/SE_naive` ratios to four decimals, the SE recovery to the same
   `8.5e-16`, the `X_null` §2.6 table at 38/38, the F0 bit-identity at 38/38, and
   `G-REL` counts of 10/10 and 19/19.
5. **Section R's non-frozen aggregation rule is genuinely inconsequential.** I
   checked all 117 computable cells expecting to find a verdict that depended on
   it. Zero disagreements.

# 9. The arrangements in which MY OWN checks could not fail — both directions

Each was named in the probe's docstring **before** the probe was run.

| probe | could-not-FIRE | am I in it? | could-not-PASS | am I in it? |
| --- | --- | --- | --- | --- |
| A `probe_gvar_family` | F1's moduli constant in `i`, making F1 = F0 under another name | **NO** — `m_i[0] = q+i` strictly increases; asserted in the output | a tolerance-based dispersion test that never fires | **NO** — I use the producer's own `bit_identical()`, and F0 fires 38/38 in the same run |
| A2 `probe_gvar_relabel_witness` | F1's 8 values not distinct, so there is no relabelling to exhibit | **NO** — 8 distinct doubles at 6 of 6 cells | F0's values also distinct, making the contrast empty | **NO** — F0 gives 1 distinct value at 6 of 6 |
| B `probe_c1_seratio_null` | a null of a different shape or decomposition, making any difference a pipeline difference | **NO** — `S = 8`, `E = 4` and `se_decomposition()` carried verbatim | the ratio an algebraic constant, so the answer is always "controlled null" | **NO** — the full null distribution and its lower tail are reported and each target is placed in it |
| B2 `probe_c1_nueff_null` | `nu_eff` bounded below by 21, so no degenerate draw can appear | **NO** — realized minimum is 1.0 | nearly every null draw degenerate, so design and data cannot be separated | **NO** — the structured null gives `P(\|t\|crit >= 8) = 0.014` against the unstructured 0.527 |
| C `probe_c2_centered` | after centering, `\|t\| = delta/SE`, so rungs 0.5 and 1.0 cannot fire on the t-clause | **YES, PARTIALLY — DISCLOSED.** Its live content is the implementation check and the relative-difference clause, which is not forced | centering also changes SE, comparing two instruments | **NO** — SE recovery reported at every rung, max `8.527e-16` |
| D `probe_archive_record` | checking the working tree only, which cannot detect a wrong commit binding | **NO** — every hash is checked against the blob **at the declared commit** | checking only what the Coordinator listed | **NO** — I recompute the change sets from git and compare set-wise in both directions |
| E `probe_nfire_dispersion` | reusing the producer's seeds, reproducing 35 with sd 0 by construction | **NO** — disjoint offset `10^7·(rep+1)`, asserted against the producer's seed range | an unbounded statistic making any spread look large | **NO** — `n_fire ∈ [0,48]` with a 1-step floor, and a small sd would have been reported as a finding for the producer |

**Post-hoc provenance, disclosed.** Probes A2 and B2 were **written after** A and
B respectively had been run and read; each says so in its own docstring. A2
exhibits numbers A's summary already implies; B2 answers a question B's output
raised. Neither changes a verdict and neither rescored anything. Every probe was
executed **exactly once**; no probe was re-run and no output was discarded.

# 10. Baseline comparison and Pareto honesty

**There is no cryptographic baseline here, and that is the correct answer rather
than an unchecked one.** No algorithm, cost model, attack, or resource claim is
made anywhere in BATCH-9e3584 — I checked all four reports and the
pre-registration for one and there is none. Accordingly Pollard-rho, BSGS and
any specialized lattice baseline are **not applicable**: there is no procedure to
compare, no time/memory/data axis on which to place it, and no eliminated search
dimension whose computation cost would need charging (`KN-LIT-7593` has no
purchase here). `dominated_by: not_applicable`, `sota_delta: not_applicable`,
with that reason recorded rather than a bare `null`.

The **within-program** baselines that do exist are all present and all cited by
the producers: BATCH-cbe023's `i = 0` `G-REL` draw (Section R reports it beside
its own two readings), the committed real count of 29 of 48 together with the
exact-null benchmark of 47 of 48 (Section B'), the frozen `tau_rel = 0.15`
scoring (Section C1, reported beside 0.025), and the committed `SE` (Section C2).
I add three baselines the batch lacked: the **nearby family** F1, the **null
`8 x 4` table**, and the **replicate distribution of `n_fire`**.

Any successor that presents any number from this batch against a cryptographic
baseline must first supply that baseline. **There is none here.**

# 11. The narrowest supported statement

> On the frozen family `B = [[I_k, A],[0, q I_{d-k}]]` at `q = 3329`,
> `d ∈ {20, 30, 40, 100, 140}` and the frozen beta grid, the AM-4/AM-8 gate's
> clause set admits two determinant-only observables — the planted `X_null` and
> the unplanted `X8 = rdet` — that are bit-identical across all 8 frozen bases at
> all 38 scored cells, so **passing that gate carries no information about a
> basis at fixed `(d, k, beta, q)`**. That refusal is **conditional on the
> family**: in a family differing in exactly one respect, both observables are
> admitted by `G-VAR` while reading no more of the basis than before, so adding
> `G-VAR` does not repair the gate in general. The gate's **refusal** side
> remains untested in either direction. `X_mp = rawtail` passes `G-REL` at 10/10
> and 14/19, so `G-REL` is a criterion that can fire. On the rebuilt null family
> `n_fire(c = 6)` is `32.1 +/- 3.6` over 8 independent seed families (frame-draw
> dispersion only, a lower bound), never within seven steps of the
> pre-registered PASS threshold, so the decay check's **FAIL** verdict holds at
> every replicate while the single reported value of 35 and the claim that the
> null fires more often than the real arm do not survive replication as stated;
> the committed real count is 29 of 48 and the Red Team's exact-null benchmark
> is 47 of 48. Section C1's re-score changed no verdict, as its own
> pre-registration predicted, and its one live observation — 4 of 10 targets with
> `SE_2way/SE_naive < 1` — is a **controlled null** (expected 3.98 of 10 under an
> effect-free table of the same shape). Section C2's instrument is clean on the
> SE axis by an argument its own algebra forces, and its refusal of the
> "over-sensitive" reading is **corroborated** by the centered control it
> deferred. **CLAIM TIER TOY throughout: nothing here bears on ML-KEM security,
> on any FIPS 203 parameter set, on any attack cost, or on any cost model, and no
> number is transported to `beta = 606` or `d = 1420`.** `AM-3 is not retired`;
> `BATCH-a44d08 is not rescored in any respect`.

# 12. Budget and infrastructure

| | |
| --- | --- |
| wall clock, whole task | ~40 min against a 7200 s budget; **not exceeded** |
| probe compute | 625 s total (A 0.24 s, A2 0.05 s, B 7.24 s, B2 4.39 s, C 0.04 s, D 2.06 s, E 610.4 s) |
| peak memory | ~1.2 GB (probe E), against 4 GB; **not exceeded** |
| `maximum_runs: 1` | **interpretation disclosed:** read as one execution per declared probe and no repeated attempts at the same measurement. Every probe ran exactly once; no producer-style run was performed; nothing was re-run after its output was seen. A red team that may execute nothing cannot satisfy a completion gate that requires a probe to be BUILT |
| environment | python 3.11.15, numpy 2.4.6, scipy 1.17.1, Linux x86_64, 4 cores shared with one concurrent review agent, BLAS threads pinned to 1 |
| **`fpylll` ABSENT** | **INFRASTRUCTURE SIGNAL, never negative mathematical evidence.** No HKZ reduction was run and no reduction-dependent number was independently re-verified |
| `knowledge/INDEX.md` | not written, not regenerated, not staged |
| commits | **none.** Every artifact below is uncommitted and is the sole carrier of its own evidence until `TASK-20260809-60f9cc` commits it (PD-4, open) |

# 13. DECLARED ARTIFACT PATHS — every probe path, explicitly

All paths are repository-relative. **An undeclared file in the archive commit is
the D3/DEF-3 defect class that already made two archives in this batch
terminally unverifiable, so this list is exhaustive and every file below exists
on disk now.** I verified set equality in both directions: 29 declared, 29 on
disk under my write scope, no missing path and no undeclared file. All seven
`.stderr.log` files are present and **empty** (sha256
`e3b0c44298fc1c14…`, the empty-file digest) — that emptiness is itself the
record that no probe wrote to stderr, and they must be committed rather than
omitted.

```
coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/red_team_report.md
coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_gvar_family.py
coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_gvar_family.json
coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_gvar_family.stdout.log
coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_gvar_family.stderr.log
coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_gvar_relabel_witness.py
coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_gvar_relabel_witness.json
coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_gvar_relabel_witness.stdout.log
coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_gvar_relabel_witness.stderr.log
coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_c1_seratio_null.py
coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_c1_seratio_null.json
coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_c1_seratio_null.stdout.log
coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_c1_seratio_null.stderr.log
coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_c1_nueff_null.py
coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_c1_nueff_null.json
coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_c1_nueff_null.stdout.log
coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_c1_nueff_null.stderr.log
coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_c2_centered.py
coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_c2_centered.json
coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_c2_centered.stdout.log
coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_c2_centered.stderr.log
coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_archive_record.py
coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_archive_record.json
coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_archive_record.stdout.log
coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_archive_record.stderr.log
coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_nfire_dispersion.py
coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_nfire_dispersion.json
coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_nfire_dispersion.stdout.log
coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_nfire_dispersion.stderr.log
```

**29 paths: this report plus 7 probes x 4 files.** Each probe is re-executable
as `python3 <probe>.py --out <probe>.json` from the repository root; each is
read-only outside its own JSON; none invokes git for writing.

# 14. Minor observations, recorded because they were checkable and not because they block anything

1. `run_manifest.yaml` for `-97d6cf` and `-3eb72c` carries no `finished_utc` and
   `-3eb72c`'s carries no `resources` block. **Both appear in the corresponding
   `results_c1.json` / `results_c2.json`** (`13:26:05Z` / `13:27:55Z`, max RSS
   109 MB each), so the artifact policy is satisfied at the task-directory level
   and this is a manifest-completeness note only.
2. `G-VAR`'s "it admits `lam1n`, `hkz`, `rawtail`" is over **18** cells for
   `lam1n` and `hkz` (small-`d` only) against **38** for the others; the
   `NOT COMPUTED` accounting in `results_relvar.json` is correct and complete,
   and no count mixes the two.
3. The C1 widened band admits exactly 1 of 10 targets. The probability that at
   least one of ten targets lands in a 20%-wide window below its own critical
   value is not small, so "a near miss reached the record" is the right framing
   and "SUGGESTIVE, NOT FALSIFYING, and nothing more" is the right label. I raise
   it only so a successor does not later cite the count as a rate. Cost to
   calibrate: seconds, on the same null machinery as probe B2.

---

```yaml
red_team_report:
  id: null
  id_note: >-
    tools/allocate_id.py exposes no `RT-` record type (choices: batch,
    coordinator_decision, evidence, experiment, handoff, hypothesis, idea,
    research_question) and AGENTS.md rule 14 forbids new legacy 3-digit
    identifiers, so no id is minted. This report is addressed by its task id,
    exactly as the BATCH-cbe023 red-team report was. Recorded as a schema gap,
    not worked around.
  task_id: TASK-20260809-444fe7
  batch_id: BATCH-9e3584
  goal_id: GOAL-MLKEM-005
  role: red-team
  claim_tier: toy
  snapshots_read:
    producer_artifacts: c034ef38003028a20b8e97f7f0a55bd6a16fdb5d
    frozen_pre_registration: 1aa7db5313f6d3da1f366443d4d6066597393402
    receipts_and_queue: 502d15a0fc51d7d21ac04830b61f02fe56d58029
    HEAD_at_review: 2fcad1f7e82be3bfb1c150b1b2f60f6e65532e0a
    verification: >-
      All three resolve and are ancestors of HEAD; verified by me, not accepted
      from the dispatching session. All 30 declared artifacts match their
      recorded sha256 against the BLOBS AT THE DECLARED COMMITS and against the
      working tree, 0 mismatches.
  inference:
    requested_policy: review-adversarial
    resolved_model_id: anthropic:claude-opus-5
    reasoning_effort: xhigh
    answering_model: claude-opus-5
    fallback_used: false
    degraded: false
    independent_session: true
    independence_kind: PROCEDURAL ONLY -- never model-level
    model_verified: false
    model_verified_reason: >-
      No adapter probe receipt exists for this session and the resolved model
      cannot be probed from inside a subagent. AGENTS.md rule 12 is UNMET AND
      UNWAIVED in this goal.
  claim_under_review: >-
    The four BATCH-9e3584 producer headlines: (R) the AM-4/AM-8 admissibility
    gate is INADMISSIBLE under G-VAR because X_null and the unplanted X8=rdet
    walk it with bit-identical values across 8 bases at 38 of 38 cells, with no
    admissibility claim reportable in either direction; (B') n_fire(c=6) is 35 of
    48 on the rebuilt null family against the committed real count of 29 of 48
    and the Red Team's exact-null benchmark of 47 of 48, so the decay check
    FAILS and the count is an artifact; (C1) the re-score at tau_rel 0.025 leaves
    all ten verdicts invariant and four of ten targets have SE_2way/SE_naive < 1,
    in tension with AM-7 clause (1); (C2) the injecting positive control finds no
    SE inflation, and P-C2c's falsification is diagnosed as a pre-existing
    near-critical effect rather than over-sensitivity.
  objections:
  - id: RT-R1
    severity: material
    target: Section R headline R-OUT-1 and its section 5(iii) recommendation
    objection: >-
      G-VAR's firing is a joint property of (observable, family), not of the
      observable. The frozen family holds |det B| = q^(d-k) constant across the
      basis index by construction, so every determinant-only functional is
      bit-identical there and G-VAR could not have failed to fire on one. BUILT
      the nearest family differing in exactly one respect (m_i[0] = q+i, same
      A_i, same code path): G-VAR fires 0 of 38 on both rdet and X_null while
      X_null still passes G-REL1 at 10/10 and G-REL2 at 19/19 and still reads
      zero entries of A. The gate REPAIRED WITH G-VAR admits it. Adding G-VAR is
      therefore not the repair section 5(iii) proposes.
    evidence: probes/probe_gvar_family.json, probes/probe_gvar_relabel_witness.json
    concession_recorded: >-
      F0 is the family in which G-VAR has the MOST power against a
      determinant-only functional; the producer's family choice is not wrong,
      and in F1 the lattices genuinely differ. The surviving objection is that
      G-VAR cannot separate reading the instance from reading a nuisance
      parameter, and nothing in the batch tests that.
  - id: RT-R2
    severity: material
    target: prereg 2.6 and outcome row R-OUT-3
    objection: >-
      measure_relvar.py's x_null_of implements the closed form and never touches
      the matrix, so R-OUT-3 ("passes the gate but non-zero dispersion -> DEFECT
      IN THE INSTRUMENT") is unreachable by construction and the promised
      code-path check is a tautology. P-R3 is forced by the SOURCE CODE, which
      is stronger than the report's honest "forced by algebra".
    remedy_supplied: >-
      probe_gvar_family.py computes X_null definitionally from slogdet of the
      integer matrix and reproduces the notarized 2.6 table at 38 of 38 cells.
      The instrument check R-OUT-3 promised now exists and passes.
  - id: RT-R3
    severity: material
    target: '"NO ADMISSIBILITY CLAIM IS REPORTABLE FROM THIS GATE IN EITHER DIRECTION"'
    objection: >-
      The demonstration establishes that PASSING the gate is uninformative. It
      establishes nothing about the REFUSAL side, whose false-refusal rate has
      never been measured. Closing both directions is premature closure in the
      conservative direction, which docs/inventor-protocol.md treats as
      symmetric with overclaiming. The narrowest valid conclusion is WIDER than
      the one reported.
    forward_guidance: >-
      Build one observable that is informative by construction and structurally
      refused -- e.g. a statistic over the leading k raw-GSO log-norms, which
      depends on A and k but takes no beta argument and so fails REL-1 by
      algebra. Minutes of numpy, one QR per basis, no reduction.
  - id: RT-R4
    severity: minor
    target: the LEAD's compute allocation
    objection: >-
      R-OUT-1's two conjuncts were both derivable from the notarized text before
      the run, so the headline is a design audit obtainable at zero compute. The
      48.4 s bought X_mp's pass, the L7/L8 replication and the normalization
      disagreement; only the second could have disagreed with an external
      measurement. A successor must not read R-OUT-1 as evidence that the
      campaign was necessary for it.
  - id: RT-R5
    severity: minor
    target: implementation completion 1, the non-frozen G-REL aggregation rule
    objection: >-
      The disclosure is accurate -- I checked all 117 computable cells and found
      0 disagreements between {mean over 8, legacy i=0, majority of 8}. A fourth
      plausible reading, unanimity, was not tested and would flip hkz's G-REL1
      at L8 (7 of 8 bases). No headline moves. Freeze the rule before, not after,
      observing that readings agree.
  - id: RT-B1
    severity: material
    target: Section B' headline
    objection: >-
      n_fire is a newly proposed statistic on a random object, reported from one
      realization with no dispersion, against a fixed decision boundary. BUILT 8
      replicates varying only the frame seeds: 28, 37, 36, 32, 32, 29, 28, 35;
      mean 32.12, sd 3.60. The reported 35 is 0.80 sd above the replicate mean;
      the FAIL boundary sits 0.87 sd from that mean; 2 of 8 replicates fire LESS
      often than the committed real count. c = 6 is the least stable point of the
      entire c grid (sd 3.60 there against 1.20 at c=4 and 1.19 at c=8). The
      honest report of this statistic is 32.1 +/- 3.6, and my figure is a LOWER
      BOUND because the error sample and the Haar arm are frozen.
    finding_for_the_producer: >-
      The substantive verdict survives: no replicate comes within seven steps of
      the PASS threshold of <= 21, so the decay check FAILS at all 8 seed
      families and the artifact reading holds. Only the headline sentence -- "the
      null fires more often than the real arm" -- fails to replicate as stated.
    evidence: probes/probe_nfire_dispersion.json
  - id: RT-B2
    severity: minor
    target: prereg 3.3's decision rule
    objection: >-
      PASS has a quantitative margin (8 of 48, set in advance) and FAIL has a
      bare inequality. Against a statistic with sd 3.6, a bare inequality 0.87 sd
      from the mean cannot classify a single draw. State the FAIL side with its
      own margin in units of the measured between-replicate sd, measured in the
      same run.
  - id: RT-C1a
    severity: material
    target: AM-14(e), Section C1's only live observation
    objection: >-
      "FOUR of ten targets have SE_2way/SE_naive < 1 ... in tension with AM-7
      clause (1)" was interpreted with no null. BUILT the null: on 200,000
      effect-free 8x4 tables through the identical carried se_decomposition,
      P(ratio < 1) = 0.3982, so the expected count is 3.98 of 10 against 4
      observed. A permutation null on each target's own 32 entries agrees within
      0.03 in percentile everywhere. The extreme 0.3635 sits at the 4.4th
      percentile of the null, and P(at least one of ten that low) is about 36%.
      This is a CONTROLLED NULL in both directions -- equally not evidence that
      the instrument is sound.
    scope_preserved: >-
      AM-14(e)'s disclosure requirement was met; the objection is to the
      interpretation, not to the disclosure or the arithmetic, which reproduces
      exactly (SE relative deviation 0.0 at all ten targets).
    evidence: probes/probe_c1_seratio_null.json
  - id: RT-C1b
    severity: material
    target: the "degenerate regime" narrative shared by C1 and C2
    objection: >-
      Four of ten targets cannot fire at any rung because |t|crit is 18.9 to 70.0
      on nu_eff of 1.00 to 1.50. BUILT the null: P(|t|crit >= 8) = 0.527 on
      effect-free 8x4 tables, so the expected count is 5.27 of 10 against 4
      observed, while a structured null gives 0.14 of 10. The degenerate regime
      is a property of the S=8, E=4 Satterthwaite design, not of the
      measurements, and the C2 positive control therefore tested 6 of 10 targets
      with the other four structurally untestable.
    scope_preserved: >-
      A degeneracy profile matching an unstructured null does NOT show those
      targets carry no structure; it shows they are UNINFORMATIVE. No Section C
      label is asserted or negated in either direction, and BATCH-a44d08 is not
      rescored in any respect.
    forward_guidance: >-
      The binding constraint on Section C is E = 4, not tau_rel. Re-deriving the
      floor could not change a verdict and did not. Raising E, or replacing
      Satterthwaite with a design whose nu_eff is bounded below, is the only
      change that moves resolving power -- and it needs no reduction and no new
      frame-level draw.
    evidence: probes/probe_c1_nueff_null.json
  - id: RT-C2a
    severity: minor
    target: P-C2e
    objection: >-
      "Recovered SE = committed SE" is forced in exact arithmetic because a
      constant offset leaves every variance component unchanged; the producer
      states the algebra and then reports 8.53e-16 as P-C2e HOLDS. It is a
      floating-point implementation check -- valuable, and what AM-14(b) asked
      for -- but not a test of the SE construction that could have failed
      mathematically. Only an implementation bug can fire it.
  - id: RT-INFRA-1
    severity: disclosure
    target: the coverage of this review
    objection: >-
      fpylll is ABSENT in this session's environment. I did NOT independently
      re-verify the 48 HKZ reductions and their max violation 0.0, lam1n or hkz
      at any cell, or the L7/L8 replication the report calls its strongest
      result. This is INFRASTRUCTURE SIGNAL and is never negative mathematical
      evidence about any of them. Cost to close: one fpylll install plus about
      20 s of reduction at d <= 40 -- the cheapest unclosed check in this review.
  required_controls:
  - id: CTRL-1
    status: BUILT AND RUN
    control: >-
      Nearby-family control on G-VAR: the frozen family against a family
      differing in exactly one respect (the scaled block's diagonal varies with
      the basis index), same A, same code path, same thresholds.
    result: G-VAR fires 38/38 in F0 and 0/38 in F1 for both rdet and X_null.
    path: probes/probe_gvar_family.py, probes/probe_gvar_relabel_witness.py
  - id: CTRL-2
    status: BUILT AND RUN
    control: >-
      Null-object control on SE_2way/SE_naive: 200,000 effect-free 8x4 tables
      plus a per-target permutation null, through the carried decomposition.
    result: P(ratio<1) = 0.3982, expected 3.98 of 10 against 4 observed.
    path: probes/probe_c1_seratio_null.py
  - id: CTRL-3
    status: BUILT AND RUN
    control: >-
      Null-object control on nu_eff and |t|crit, unstructured and structured.
    result: P(|t|crit>=8) = 0.527 unstructured, 0.014 structured; 4 of 10 observed.
    path: probes/probe_c1_nueff_null.py
  - id: CTRL-4
    status: BUILT AND RUN
    control: The CENTERED positive control Section C2 pre-registered and deferred.
    result: >-
      No target fires at delta/SE <= 1 once centered; the uncentered firing
      reproduces; SE recovery 8.527e-16; 6 of 6 fire at 12 SE. The producer's
      diagnosis is corroborated.
    path: probes/probe_c2_centered.py
  - id: CTRL-5
    status: BUILT AND RUN
    control: >-
      Replication control on n_fire: 8 independent null families, frame seeds
      varied, everything else frozen.
    result: 28,37,36,32,32,29,28,35 -- mean 32.12, sd 3.60, range 9.
    path: probes/probe_nfire_dispersion.py
  - id: CTRL-6
    status: BUILT AND RUN
    control: >-
      Independent re-verification of the Coordinator's git claims: three-way
      commit split, 30-for-30 against the blobs at the declared commits, D3
      table, notarization ordering, commit-message rule.
    result: Every checkable claim CONFIRMED; two of three UNKNOWNs resolved.
    path: probes/probe_archive_record.py
  - id: CTRL-7
    status: NOT RUN -- INFRASTRUCTURE
    control: Re-run the HKZ pipeline and re-verify the L7/L8 replication.
    reason: fpylll absent. Never negative evidence.
    cost: one install plus about 20 s of reduction at d <= 40.
  - id: CTRL-8
    status: NOT RUN -- OUT OF ROLE
    control: >-
      False-refusal control on the gate: one observable informative by
      construction that the gate structurally refuses.
    reason: >-
      Introducing a new candidate observable is the Idea Generator's and the
      Coordinator's business, not the Red Team's.
    cost: minutes of numpy, one QR per basis, no reduction.
  counterexample_or_mutation: >-
    The mutation that carries the review: B_i = [[I_k, A_i],[0, diag(m_i)]] with
    m_i[0] = q+i and every other quantity held fixed. It changes exactly one
    property of the frozen family -- whether |det B_i| depends on the basis index
    -- and it flips G-VAR from firing at 38 of 38 to firing at 0 of 38 on two
    observables that read no entry of A in either family. In that family the AM-4
    gate repaired with G-VAR admits an observable whose entire between-basis
    variation is a strictly monotone relabelling of the basis index (8 distinct
    IEEE-754 doubles at 6 of 6 witnessed cells). Cost: 0.24 s of numpy.
  baseline_comparison:
    cryptographic_baseline: not_applicable
    reason: >-
      No algorithm, cost model, attack, or resource claim exists anywhere in
      BATCH-9e3584 -- I checked all four reports and the pre-registration.
      Pollard-rho, BSGS and any specialized lattice baseline have nothing to
      compare against; no search dimension is eliminated, so KN-LIT-7593's rule
      about charging an invariant's own cost has no purchase here.
    dominated_by: not_applicable
    sota_delta: not_applicable
    within_program_baselines_present_and_cited:
    - BATCH-cbe023's i=0 G-REL draw, reported by Section R beside its own readings
    - the committed real count of 29 of 48 with the exact-null benchmark of 47 of 48
    - the frozen tau_rel = 0.15 scoring, reported beside 0.025
    - the committed SE(Delta_bar), reproduced by C2 and by me at 0.0 deviation
    baselines_this_review_adds:
    - the nearby family F1
    - the effect-free 8x4 null table, for the SE ratio and for nu_eff
    - the replicate distribution of n_fire over 8 independent null families
  heuristic_challenges:
  - >-
    G-VAR ("an admissible observable MUST have non-zero between-basis dispersion
    at fixed (d,k,beta,q)") is not a portable clause: it is conditional on the
    family holding the observable's own argument fixed, and no numbered statement
    of that condition exists. Restate it as dispersion on the fibre of the family
    over the observable's own arguments, and require each candidate to be scored
    on a family built to hold its declared argument fixed.
  - >-
    "materially below = 8 of 48" is set in advance and is defensible; its
    counterpart on the FAIL side is a bare inequality with no margin, applied to
    a statistic whose measured sd is 3.6. A margin is needed on both sides or on
    neither.
  - >-
    "SE_2way >= SE_naive" is treated as an expectation of AM-7 clause (1) at the
    level of individual targets. Under S=8, E=4 it holds only in the aggregate:
    the null median is 1.09 but P(< 1) is 0.40. If AM-7 clause (1) is meant
    per-target it is refuted by the design, not by the data.
  - >-
    tau_rel = 0.10 with s_X = 1.0 is carried, not rebuilt. Section R discloses
    this and reports both normalizations, which is the right handling; the
    remaining exposure is that at every hkz cell s_X exceeds |X| by 2.3x to
    16.9x, so the criterion is in practice an ABSOLUTE 0.10 test in hkz's own
    units and is not a relative criterion at that scope at all.
  cost_model_challenges:
  - >-
    None applicable to the batch: no cost model, no complexity claim, no memory
    or time-memory statement, no o(1)/polylog cofactor, and no per-attempt versus
    total-expected-cost bookkeeping appears anywhere in BATCH-9e3584. Recorded as
    checked-and-absent rather than as omitted.
  - >-
    The only cost quantities present are wall clocks (48.4 s, 119.5 s, 0.25 s,
    0.24 s) and max RSS, all correctly presented as budget accounting rather than
    as results. My own costs are in section 12 of this report.
  reduction_and_scope_challenges:
  - >-
    Scope inflation: none found. All four reports carry explicit "what this does
    NOT establish" sections, state the TOY tier, refuse to transport to beta=606
    or d=1420, and decline to reinstate or negate any frozen label. The
    affected-versus-safe question does not arise because no scheme scope is
    claimed.
  - >-
    Scope DEFLATION found, and it is the mirror failure: R-OUT-1 closes the
    gate's refusal side, which was never tested. See RT-R3.
  - >-
    No published reduction is instantiated anywhere in this batch, so there is no
    cited theorem whose hypotheses could fail to transfer.
  - >-
    D3 binds every downstream citation: nine declared producer artifact names do
    not exist. Every citation in this report uses the committed names, and the
    ledger archive must do the same.
  proof_architecture_challenges:
  - >-
    Observation-fiber attack, EXECUTED: hold the observable and its code path
    fixed and vary the underlying family. Two preimages land on opposite sides of
    the G-VAR conclusion (F0 refuses, F1 admits). The missing separator is named:
    dispersion conditioned on the observable's own arguments.
  - >-
    Quantifier-order attack: R-OUT-1 reads "there exists an observable such that
    for all bases the value is constant". It is used as "for all gates of this
    shape, no admissibility claim is reportable". The universal is over ONE
    family. The quantifier over families is silently existential in the proof and
    universal in the conclusion.
  - >-
    Method-ceiling attack: the largest claim the measure can support is a
    statement about the PASS side of a five-clause gate on one basis family at
    q=3329, d <= 140. It does not reach "no admissibility claim is reportable in
    either direction".
  - >-
    Nearby-object attack, EXECUTED: applied the same reasoning to the closest
    object for which the desired conclusion is false, and it failed to
    distinguish it. That is the missing problem-specific ingredient.
  - >-
    Compositional-invariant attack: deleting G-VAR from the proposed repaired
    gate returns the original gate, and adding it back does not restore the
    conclusion outside F0. The strengthened invariant does not imply the final
    target.
  - >-
    Boundary and strictness attack: the old method (BATCH-cbe023's i=0 draw) IS
    genuinely embedded and is reported beside the new readings at every cell, and
    the perturbation (8 bases, both normalizations, a paired test with its own
    floor) is strictly more informative rather than merely different. This audit
    PASSES.
  narrowest_supported_statement: >-
    See section 11 of this report, reproduced in force: on the frozen family at
    q=3329 and d in {20,30,40,100,140}, the AM-4/AM-8 gate's PASS side is
    uninformative, because a parameter-determined closed form and an unplanted
    member of the frozen candidate list both clear it with bit-identical values
    across 8 bases at 38 of 38 cells; that refusal is conditional on the family
    and adding G-VAR does not repair the gate outside it; the gate's refusal side
    is untested in either direction; X_mp = rawtail passes G-REL at 10/10 and
    14/19, so G-REL can fire; n_fire(c=6) on the rebuilt null family is 32.1
    +/- 3.6 over 8 independent seed families (frame-draw dispersion only, a lower
    bound) and never within seven steps of the pre-registered PASS threshold, so
    the decay check FAILS at every replicate while the reported single value of
    35 does not survive replication as stated, against the committed real count
    of 29 of 48 and the Red Team's exact-null benchmark of 47 of 48; Section C1
    changed no verdict as its own pre-registration predicted, and its one live
    observation is a controlled null; Section C2 is clean on an axis its algebra
    forces, and its refusal of the over-sensitive reading is corroborated by the
    centered control it deferred. CLAIM TIER TOY. AM-3 is not retired.
    BATCH-a44d08 is not rescored in any respect.
  next_concrete_action: >-
    ONE ACTION: before any successor spends compute on candidate observables,
    re-score G-VAR on a family constructed to hold each candidate's own declared
    argument fixed -- the fibre condition of RT-R1 -- and record the result as a
    versioned amendment to the G-VAR clause. probes/probe_gvar_family.py is the
    working template and costs 0.24 s per candidate at d <= 140 with no
    reduction. Until that clause is restated, no "repaired gate" should be built
    on, and no admissibility claim should be made from a gate whose refusal side
    (RT-R3) has also never been tested.
  premature_closure_check:
    closure_claimed_by_batch: >-
      "THE GATE IS INADMISSIBLE UNDER G-VAR ... NO ADMISSIBILITY CLAIM IS
      REPORTABLE FROM THIS GATE IN EITHER DIRECTION."
    named_obstruction: PRESENT -- the clause set contains no dispersion requirement.
    argument: PRESENT -- closed form, G-REL arithmetic, bit-identity over 8 bases.
    forward_guidance: >-
      PARTIAL AND NOW SHOWN INCOMPLETE. The only guidance offered is "the gate
      needs a dispersion criterion, and more than one"; probe A shows that
      criterion is insufficient outside the frozen family, and no successor
      clause set, no surviving-candidate question and no refusal-side test is
      named. This is the gap a successor must close, and it is why the closure is
      recorded here as SCOPED rather than earned in the form stated.
    verdict: >-
      Not a fatigue report -- real mechanism, real measurement, correct within its
      family. But over-closed in the conservative direction (RT-R3) and
      under-specified forward. Scope it to the PASS side on the frozen family and
      the closure is sound.
  prohibitions_observed:
  - No Executor receipt or Validator report was altered; I read only.
  - No bounded failure is called an impossibility result.
  - No conditional result is rejected for being conditional on a stated heuristic.
  - No broader ECDLP or lattice conclusion is claimed; no cost path exists here.
  - No commit was made; nothing was written outside the assigned write_scope.
  - knowledge/INDEX.md was not written, regenerated or staged.
  artifact_paths:
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/red_team_report.md
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_gvar_family.py
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_gvar_family.json
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_gvar_family.stdout.log
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_gvar_family.stderr.log
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_gvar_relabel_witness.py
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_gvar_relabel_witness.json
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_gvar_relabel_witness.stdout.log
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_gvar_relabel_witness.stderr.log
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_c1_seratio_null.py
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_c1_seratio_null.json
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_c1_seratio_null.stdout.log
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_c1_seratio_null.stderr.log
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_c1_nueff_null.py
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_c1_nueff_null.json
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_c1_nueff_null.stdout.log
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_c1_nueff_null.stderr.log
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_c2_centered.py
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_c2_centered.json
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_c2_centered.stdout.log
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_c2_centered.stderr.log
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_archive_record.py
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_archive_record.json
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_archive_record.stdout.log
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_archive_record.stderr.log
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_nfire_dispersion.py
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_nfire_dispersion.json
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_nfire_dispersion.stdout.log
  - coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_nfire_dispersion.stderr.log
  archived_by: TASK-20260809-60f9cc
  committed: false
  committed_note: >-
    PD-4 is open. This report and all 28 probe files sit UNCOMMITTED across a
    dispatch window and are the SOLE CARRIERS of their own evidence until
    TASK-20260809-60f9cc commits them. All 29 paths are declared above; an
    undeclared file in that commit is the D3/DEF-3 defect class that already made
    two archives in this batch terminally unverifiable.
```
