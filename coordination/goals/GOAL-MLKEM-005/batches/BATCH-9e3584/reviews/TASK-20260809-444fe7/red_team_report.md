# RED TEAM — BATCH-9e3584, all four producers

    task        TASK-20260809-444fe7   (red-team, INDEPENDENT SESSION)
    goal        GOAL-MLKEM-005
    batch       BATCH-9e3584
    archived_by TASK-20260809-60f9cc
    claim_tier  TOY
    budget      7200 s wall / 4 GB / 1 run.  Used: ~7 s of probe compute,
                peak child RSS 102.2 MB (measured).  No cap bound.

**CLAIM TIER IS TOY AND STAYS TOY.** Nothing in this report bears on ML-KEM
security, on any FIPS 203 parameter set, on any attack cost, or on any cost
model. No number here may be transported to `beta = 606`, `d = 1420`, or any
other parameter set, by extrapolation, by analogy, or by any other route.
There is no algorithm, no cost model and no attack in this batch, so there is
**no cryptographic baseline**, and `dominated_by` / `sota_delta` are
necessarily `null`. Any successor presenting any of this against a
cryptographic baseline must first supply the baseline; there is none here.

**I COMMITTED NOTHING.** This report and every probe under `probes/` sit
uncommitted across a dispatch window (PD-4, open) and are the sole carriers of
their own evidence until `TASK-20260809-60f9cc` commits them. Every probe path
is listed explicitly in §12.

**WHAT I READ.** The producer artifacts **as committed at `c034ef38`** and the
frozen pre-registration **as committed at `1aa7db53`**, extracted with
`git show <commit>:<path>` and not from the working tree. Also read:
`AGENTS.md`; `agents/red-team.md`; `CLAUDE.md`; `docs/inventor-protocol.md`;
`ledger/decisions/DEC-20260808-05b684.yaml` (AM-10..AM-14, in force, **not
re-litigated**); `knowledge/findings/KN-FIND-f38a89.md` as the only citation
route for AM4-OBS-1; `COORDINATOR-ADJUDICATION-20260811.md`; both
`snapshot-receipt.json` files at `502d15a0`; the continuation queue and my
task card; `BATCH-cbe023/reviews/TASK-20260808-6de788/red_team_report.md` and
its committed probes; and the committed inputs those probes read
(`BATCH-cbe023/tasks/TASK-20260808-3a5f18/results_am7.json`,
`.../TASK-20260808-2a9085/measure_am4.py`).

**Producer artifacts are cited by their COMMITTED filenames** (D3):
`measure_relvar.py` / `results_relvar.json` / `report_relvar.md`;
`measure_nullfam.py` / `results_nullfam.json` / `report_nullfam.md`;
`rescore_c1.py` / `results_c1.json` / `report_c1.md`;
`posctl_c2.py` / `results_c2.json` / `report_c2.md`.

**Inference.** `requested_policy: review-adversarial`;
`reasoning_effort: xhigh` per `orchestration/model-policies.yaml`;
`independent_session_required: true`, honoured — I produced none of the
artifacts under review, and this session did not write the pre-registration,
run any producer, or make any archive. `fallback_used: false`.
`model_verified: false`, and the reason is recorded rather than papered over:
this runtime binds no model provenance, no adapter probe receipt exists for
this session, and the resolved model cannot be probed from inside a subagent.
**Independence in this goal is PROCEDURAL AND NEVER MODEL-LEVEL. AGENTS.md
rule 12 is UNMET AND UNWAIVED.** The same session authored the
pre-registration, ran all four producers and made both archives; this review
and `TASK-20260809-3f1dc4` are the batch's entire independence budget, and
procedural separation does not pass as independence.

---

## 0. Summary of what this review found

| # | finding | severity | evidence |
| --- | --- | --- | --- |
| **RT-1** | **PRIMARY.** `G-VAR` refuses an arithmetic ROUTE, not an observable. The same closed form `X_null`, evaluated by QR of `B^T` or on an ambient-isometry presentation `BH`, is **0 of 38 cells bit-identical**, agrees with the notarized closed form to `5.1e-14` / `3.1e-14` relative, reproduces the notarized prereg 2.6 table at **304 of 304 (cell x basis)** to every printed digit, and **walks `G-REL2` at 19 of 19 cells**. `report_relvar.md` §5(iii)'s "it cannot be tuned into or out of firing" is false as stated. | **MAJOR — bounds the refusal's generality; does NOT overturn `R-OUT-1`** | `probes/probe_nullroute.py` |
| **RT-2** | The producer's **own committed number** already shows RT-1 for the unplanted candidate: `results_relvar.json` `forced_arithmetic.rdet_T1_ambient_isometry_residual = 3.865e-12`, while `report_relvar.md` §4 states of `G-INV` for `rdet` and `X_null` that "Residuals are `0` identically". That is true for T2/T3 (`0.0`) and **false for T1**. | **MODERATE — prose contradicted by its own artifact** | `results_relvar.json`, `report_relvar.md` §4 |
| **RT-3** | The MUST-PASS guard clears `tau_rel` at amplitude multiplier `mu` median `0.224`; `hkz` misses at `mu` median `16.3` and `lam1n` at `2.30`. At the **same cells** the guard's mirrored gap is `2.5x`–`266x` the candidate's. A binary guard certifies "the criterion can fire", never "the criterion resolves an effect of the candidates' size". | **MODERATE — AM-10(c) satisfied in the letter; the amplitude question is unaddressed** | `probes/probe_guard.py` |
| **RT-4** | P-B1's falsifier (`n_fire(c=6) <= 21 of 48`) had probability **0.00175** under a null of the shape AM-13 mandates (20 000 reps). `n_fire` computed from the SE ratio **alone** is 34; with `Delta := 0` it is 34; realized 35. The only quantity carrying information about the object moves the headline by exactly **one detection-floor unit**. | **MODERATE — the prediction, not the producer** | `probes/probe_bprime.py` |
| **RT-5** | The rebuilt null family's `SE_step/SE_diff` median is `1.037`; the real arm's implied ratio, recovered from the committed exact-null `c_min` median `2.990`, is `0.473` — a factor **2.19**. `c_min` is affine in that ratio, so the two objects are not the same shape *for this statistic*. Direction of the finding unaffected; the magnitude `-6` is not interpretable. | **MODERATE** | `probes/probe_bprime.py` |
| **RT-6** | The count **saturates instead of decaying**: under a null with ratio 1 the expected `c_min` is `1 + t_{n-1,0.998}`, which **falls** with more draws (`5.207` at `n=8` → `3.878` as `n → inf`), and the carried headline `c = 6` lies above it at every `n`. More data drives the null count **up** toward `48 of 48`. | **MODERATE — strengthens the producer's own artifact verdict and names what stays open** | `probes/probe_bprime.py` |
| **RT-7** | P-C2e **could not have failed**. A constant offset is an exact symmetry of `se_decomposition`: `MS_S`, `MS_P`, `MS_res` are functions of centred deviations only. I reproduce the producer's `8.53e-16` exactly (`8.527e-16`) and it stays at `8.9e-11` at offsets of `1e6 * SE`. A structured one-column injection moves the SE by up to `11.68` relative. The pre-registered ladder is confined to the estimator's own invariance class, so Section C2 **did** run in the could-not-FIRE arrangement prereg 5.4 claims it averted. | **MAJOR for C2's headline; the section's other checks stand** | `probes/probe_c2_centered.py` |
| **RT-8** | Section R's 7-for-7 prediction record: **4 forced by algebra and correctly labelled UNTESTED**, 1 (P-R7) reduces to a units fact readable from `s_X = 1.0` and the committed `|hkz| < 1`, leaving **2** with genuinely live falsifiers (P-R1, P-R6). The report claims 3. | **MINOR** | §4 below |
| **RT-9** | `report_relvar.md` §11 asserts that it does not use BATCH-cbe023's non-citable relocation phrase; §7 contains "closed here rather than relocated", which reintroduces that phrase's vocabulary inside a comparative claim about BATCH-cbe023. | **MINOR — compliance** | `report_relvar.md` §7 vs §11 |
| **RT-10** | `tau_rel = 0.025` is the **maximum of four numbers** — the most dispersion-sensitive functional of a four-point sample — and carries no dispersion anywhere. The same carried rule read at the same four nulls' p95 gives `0.0735`, a factor `2.94`. **No verdict moves**: all ten are invariant at `0.15` and at `0.025`, and the alternative lies between them. | **MINOR — AM-11 applied to a producer statistic** | `probes/probe_c1_nc.py` |

**Findings that go AGAINST my thesis, reported at the same weight** (§10):
the three Coordinator claims about the git record are **all correct**; the
producer's diagnosis of P-C2c is **confirmed** by the centered control I built
(0 of 10 targets fire at `delta/SE <= 1.0`); the stated mechanism for
excluding `N-C` is **confirmed** (denominator collapses `117.9x`, numerator
moves `1.08x`) and the exclusion moves the instrument *toward* falsifiability;
the cross-platform agreement is **stronger** than the report claims (24 of 24
per-basis pairs at 6 decimals, and the three implementations are textually
distinct); the MUST-PASS guard **does** fire under the pinned normalization
(19 of 19 pinned `REL2` entries); and my predicted escape route through a
unimodular re-presentation **did not escape**.

---

## 1. Coordination record — I verified it myself, as required, and it holds

`probes/probe_gitrecord.py` → `probes/probe_gitrecord_output.json`. It reads
the git object database (`git rev-parse`, `diff-tree`, `show`, `merge-base`),
recomputes every declared `sha256`, and reconstructs the D3 table from the
`dispatch_queue.json` **as committed at `502d15a0`**. 0.43 s.

| Coordinator claim | my verdict |
| --- | --- |
| `1aa7db53` = 2 pre-registration files | **CORRECT** — `prereg.md`, `prereg_sha256.txt`, both additions |
| `c034ef38` = 28 producer files | **CORRECT** — 28 additions, all under `tasks/TASK-20260809-{cda2f6,311784,97d6cf,3eb72c}/`, 7 each |
| `502d15a0` = 2 receipts + queue | **CORRECT** — 2 added receipts, 1 modified `dispatch_queue.json` |
| chain is linear `1aa7db53 → c034ef38 → 502d15a0` | **CORRECT** — each is the sole parent of the next |
| all 30 declared artifacts match their recorded `sha256` at HEAD | **CORRECT — 30 of 30, zero mismatches.** They also match **at the declared commit**, 30 of 30, which the Coordinator did not claim and which is the stronger statement |
| D3: nine declared producer artifact paths dangle | **CORRECT — exactly 9 of 28 dangle and exactly 9 committed files are undeclared**, one-for-one per task: `measure_bnull/report_bnull/results_bnull` ↛ `measure_nullfam/report_nullfam/results_nullfam`; `measure_ctau/report_ctau/results_ctau` ↛ `rescore_c1/report_c1/results_c1`; `measure_cposctl/report_cposctl/results_cposctl` ↛ `posctl_c2/report_c2/results_c2` |
| all three commits reachable from HEAD | **CORRECT** |

**Two of the Coordinator's three declared UNKNOWNs resolve in the
affirmative,** and I record it because the adjudication invited exactly this:
`git log -1 --format=%B` shows that **both** `1aa7db53` and `c034ef38` carry
their task id (`TASK-20260809-91cf76`, `TASK-20260809-4d928d`) **and**
`GOAL-MLKEM-005` in the message body, so the commit-message rule
(`research_dispatch.py:1103-1114`) is satisfied by both. I did not resolve the
third (PR state / `origin/main` merge base at each commit): I hold no
authority to open or inspect a PR for this branch and I decline to guess.

**A factual correction to my own task card, offered because a card is not
evidence either.** The card states "Your predecessor's probes were lost to
exactly this." They were not. All six files
(`probe_A1_null_observable.{py,out.json}`,
`probe_A2_rel2_replication.{py,out.txt}`,
`probe_BC_artifact_arithmetic.{py,out.txt}`) are present in the HEAD tree,
committed by `b33158fc`. I read them and this review depends on two of them.
The declaration discipline the card demands is still right — I follow it in
§12 — but the premise offered for it is false, and correcting it matters
because "the predecessor's evidence was lost" would otherwise become a citable
fact about this goal.

**What none of this repairs.** The archive tasks' commit-scope binding remains
broken exactly as the Coordinator recorded, and I take no position on the
supersession, which is not mine to take. What I can say from measurement:
every byte I reviewed is committed, reachable, and content-verified, and
fixed before this review was dispatched. The purpose of the read-a-snapshot
rule is met.

---

## 2. PRIMARY TARGET — attacking the generality of the `G-VAR` refusal

### 2.1 What the lead reports, stated precisely so the attack lands on it

`report_relvar.md` §2 realizes `R-OUT-1`: `X_null` walks `G-REL1` (10 of 10
lattices), `G-REL2` (19 of 19 cells) and passes `G-NUM`/`G-INV`/`G-Q` by
algebra, while bit-identical across all 8 frozen bases at all 38 scored cells;
`G-VAR` fires; the gate is INADMISSIBLE, with no admissibility claim
reportable from it in either direction. `X8 = rdet`, from the original frozen
list and not planted, is also bit-identical at 38 of 38.

**I do not dispute that conclusion and my probe does not weaken it.** One
refused blind observable is sufficient for `R-OUT-1`; finding more escapes
cannot make a gate more admissible. What I attack is the *generality* the
report claims **for the refusal criterion itself**, in §5(iii):

> "So the criterion separates parameter arithmetic from basis-dependent
> measurement, which is what AM-11 asks of it. The decision was made
> **structurally, by bit-identity of the 8 IEEE-754 doubles, not by a
> tolerance**, so it cannot be tuned into or out of firing."

### 2.2 The observable the refusal did not consider

AM-11 states the requirement over **functions**: "any closed-form function of
`(d, k, beta, q)` with zero between-basis variance MUST be refused". Bit
identity is a property of the **arithmetic route** used to evaluate a
function. `measure_relvar.py:260` is explicit that it chose the route:

```python
def x_null_of(d, k, beta, q):
    """... Computed here FROM THE MATRIX-FREE CLOSED FORM, exactly as prereg
    2.6 states it, so that its zero dispersion is a property of the observable
    and not of a float path."""
```

The comment asserts what the code cannot deliver. Zero dispersion here is a
property of *that* path. `probes/probe_nullroute.py` evaluates **the same
mathematical observable** through six routes to `log|det B|`, all equal to
`(d-k) log q` exactly for every `A`, and scores each through the same
`rho_both` / `G-REL` / bit-identity path (0.31 s, 39.0 MB):

| route to `log|det B|` | max rel dev from the closed form | `X_null` bit-identical | `G-VAR` | `G-REL2` pass | reproduces prereg 2.6 |
| --- | --- | --- | --- | --- | --- |
| R0 closed form *(the producer's)* | `0` | 38 of 38 | **REFUSES** | 19/19 | 304/304 |
| R1 `slogdet(B)` *(the producer's `rdet` route)* | `1.1e-15` | 38 of 38 | **REFUSES** | 19/19 | 304/304 |
| **R2 QR of `B^T`** | `5.07e-14` | **0 of 38** | **admits** | 19/19 | **304/304** |
| R3 `slogdet(UB)`, `U` unimodular | `9.8e-16` | 38 of 38 | REFUSES | 19/19 | 304/304 |
| R4 `0.5 slogdet(BB^T)` | `2.35e-09` | 0 of 38 | admits | 19/19 | 304/304 |
| **R5 `slogdet(BH)`, `H` ambient isometry** | `3.11e-14` | **0 of 38** | **admits** | 19/19 | **304/304** |

Read the R2 and R5 rows. Those observables

* are the **same function of `(d, k, beta, q)`** — AM-11's antecedent holds;
* reproduce the **notarized prereg 2.6 table at 304 of 304 cell-by-basis
  entries to every printed digit**, so at the resolution the frozen text
  itself uses they are indistinguishable from the refused one;
* carry a between-basis float sd of `1.20e-13` (R2) and `5.44e-14` (R5),
  which is `5.0e-12` and `2.3e-12` times `hkz`'s committed between-basis sd of
  `0.023888` at `L7 beta=5`;
* **walk `G-REL2` at 19 of 19 cells and `G-REL1` at 10 of 10**, exactly as the
  refused route does;
* and `G-VAR` **admits** them.

`G-VAR` as built therefore refuses a *presentation*, not an observable. It
**can** be tuned out of firing — not by loosening a tolerance, which the
prereg correctly guarded against, but by changing the arithmetic route, which
it did not consider. R5 is not an exotic construction: it is the transform the
gate's **own `G-INV` T1 clause** applies.

### 2.3 The producer's own committed number already says this (RT-2)

`results_relvar.json`, `forced_arithmetic`:

```
rdet_T1_ambient_isometry_residual  = 3.865352482534945e-12
rdet_T3_unimodular_residual        = 0.0
rdet_T2_permutation_residual       = 0.0
```

`report_relvar.md` §4 says of `G-INV` for `rdet` and `X_null`: "`|det UB| =
|det B|` and `|det BH| = |det B|` **by algebra**. Residuals are `0`
identically." For T2 and T3 that is exactly right. For **T1 it is false in the
producer's own artifact**: the measured residual is `3.87e-12`. And that
non-zero residual is precisely the vanishing basis dependence that escapes the
bit test — had the frozen family presented its bases post-isometry, `rdet`
would not have been bit-identical and `G-VAR` would have admitted it. The
"and it was not planted" finding about `rdet`, which the report offers as the
strongest evidence that `G-VAR` is needed, is a property of the integer-LU
route on this block-triangular presentation. (For that presentation partial
pivoting never touches `A`: the LU diagonal is `[1]*k + [q]*(d-k)` whatever
`A` is. I verified this and it is why R1 is bit-identical.)

### 2.4 A second, independent narrowness: `G_VAR_REFUSES` is an all-cells test

`measure_relvar.py:614-619`:

```python
"ZERO_DISPERSION_EVERYWHERE": bool(cells) and n_zero == len(cells),
"G_VAR_REFUSES":              bool(cells) and n_zero == len(cells),
```

A candidate is refused only if **every** cell is bit-identical. An observable
that is parameter-determined at 37 of 38 cells and basis-dependent at 1 is
admitted, and nothing in the artifact records how close it came. `G-VAR`
reports a Boolean where it holds a 38-cell profile.

### 2.5 What this does and does not do to `R-OUT-1`

It does **not** overturn it, and I say so plainly: `X_null` via the notarized
closed form *is* refused, `G-VAR` *did* fire, and the gate *is* inadmissible
by the pre-registered criterion. What falls is the report's claim about the
criterion's generality, and with it the forward inference a successor would
otherwise draw — that adding `G-VAR` repairs the gate. It does not: a
parameter-determined observable submitted through any float path passes
`G-VAR` today.

**The cheapest repair, offered as forward guidance rather than as a
requirement.** Replace bit identity with a **scaled** dispersion test —
between-basis sd measured against the candidate's own between-**cell** range
at fixed `(d,k)` — and report the profile rather than a Boolean. On the
measured numbers that separates cleanly: the escaping routes sit at `1e-13`
against a between-cell range of order `1`, while `hkz` sits at `2.4e-2`. A
criterion that draws its line at exactly zero cannot distinguish "no
information" from "information at `1e-16`", and those are 13 orders of
magnitude apart in a quantity the artifact already records (`float_sd`).

---

## 3. Is `X_mp = rawtail` a fair guard? — the nearby object a fair guard must catch

`probes/probe_guard.py` (0.14 s), derived **entirely from the producer's
committed per-basis entries**, so it cannot disagree with the producer about
any measurement — only about what the measurement supports. It also
recomputes every reported `G_REL2` mean from the per-basis entries: **max
deviation `0.0` at all five candidates.** The committed numbers are internally
consistent.

Define, per candidate per cell per basis, the **amplitude multiplier**
`mu = tau_rel * max(|X_a|, s_X) / |X_b - X_a|`: the factor by which that
candidate's own mirrored gap would have to be multiplied to reach `tau_rel`.
`mu < 1` means a pass with margin `1/mu`; `mu > 1` means a miss by `mu`. No
threshold of mine enters it.

| candidate | cells | entries with the `s_X` floor binding | `mu` median | `mu` min .. max | cells passing at the mean |
| --- | --- | --- | --- | --- | --- |
| `rawtail` (the guard) | 19 | 19 of 152 | **0.224** | 0.110 .. 50.8 | 14 of 19 |
| `hkz` | 9 | **72 of 72** | **16.3** | 3.09 .. 33.9 | 0 of 9 |
| `lam1n` | 9 | 0 of 72 | 2.30 | 1.92 .. 3.37 | 0 of 9 |
| `null` | 19 | 16 of 152 | 0.175 | 0.167 .. 0.206 | 19 of 19 |
| `rdet` | 19 | 0 of 152 | 0.104 | 0.103 .. 0.104 | 19 of 19 |

At the **same cells**, guard against candidate:

| cell | `mu` rawtail | `mu` hkz | `mu` lam1n | rawtail gap / hkz gap |
| --- | --- | --- | --- | --- |
| `L7/L8 b5` | 0.207 | 3.09 | 1.92 | 78.9 |
| `L7/L8 b15` | 0.118 | 16.3 | 1.92 | 137.5 |
| `L9/L10 b7` | 0.211 | 7.12 | 2.30 | 181.4 |
| `L9/L10 b22` | 0.110 | 20.8 | 2.30 | 180.5 |
| `L11/L12 b10` | 0.215 | 4.19 | 3.37 | 105.3 |
| `L11/L12 b30` | 0.116 | 33.9 | 3.37 | 265.7 |

**The objection, stated narrowly.** AM-10(c) asks for "at least one declared
candidate that MUST PASS it, so the criterion has a could-not-PASS guard of
its own", and `X_mp` satisfies that in the letter: it was fixed in the
notarized text before any measurement, `R-OUT-5` was a live row, and it
passed. What it does **not** establish is the sentence `report_relvar.md` §7
builds on it — that the criterion "was not pinned by its `s_X = 1.0` floor
into never firing" as a statement about the regime the candidates live in.
`rawtail` and `hkz` are **the same functional form** (`mean_{i>=d-beta} log
||b*_i|| - logdet/d`) on the raw and the HKZ-reduced basis, and the guard's
effect is 79x–266x the candidate's at the identical cell. A guard that fires
two orders of magnitude above where the candidates sit reports that the
criterion is not identically dead; it reports nothing about resolution.

**And the same pre-registration knows the fix.** prereg 5.2 gives Section C2 a
graded ladder (`delta/SE` in `{0.5, 1, 2, 3, 4, 6, 8, 12}`) with declared
SHOULD and SHOULD-NOT rungs. Section R got a binary guard. A `lambda`-graded
guard — `X_lambda = C + lambda (X_mp - C)` scored through the identical path —
would have measured the criterion's crossing amplitude directly, at the cost
of one extra loop over already-computed numbers.

**Against my own thesis, and it is the sharper half of this section.** I
predicted the guard would live entirely in the relative regime while the
candidates live in the pinned regime, so that the guard never exercises the
`s_X = 1.0` floor. **That is wrong.** `rawtail` has 19 pinned `REL2` entries
and **passes all 19**; `X_null` has 16 and passes all 16; and in `REL1`, `hkz`
is pinned at 48 of 48 entries and **passes 47 of them**. The criterion
demonstrably fires under the pinned floor. `report_relvar.md` §7's sentence is
supported by the data. What survives is the amplitude point above, not the
regime point.

---

## 4. The seven predictions, and what the "FORCED" labels are doing (RT-8)

`report_relvar.md` §6 flags the 7-for-7 record itself, labels four as forced
by algebra and UNTESTED, and names P-R1, P-R6, P-R7 as "the section's actual
empirical content". That self-flagging is exactly right in kind. I disagree
about the count.

| # | prediction | my reading |
| --- | --- | --- |
| P-R2 | `X_null` walks the gate | **FORCED**, correctly labelled. prereg 2.6 pre-computes the `G-REL` values in closed form; the gate walk is arithmetic. |
| P-R3 | `X_null` has exactly zero dispersion | **FORCED**, correctly labelled — **conditional on the matrix-free route**, which is the whole of RT-1. Under the QR or isometry route the *same* prediction is false at 38 of 38 cells. The label is right; the reason recorded for it (a property of the observable) is not. |
| P-R5 | `REL-1` identically 0 for `rdet`, `lam1n` | **FORCED**, correctly labelled. |
| `G-Q`/`G-INV` inside P-R2 | | **FORCED**, correctly labelled, and the report additionally discloses that the `q=1` rung compares a q-ary lattice against `Z^d`. Good practice. |
| **P-R7** | the two normalizations disagree somewhere | **NOT MEANINGFULLY LIVE.** `s_X = 1.0` is frozen, and the committed `hkz` magnitudes are `0.025..0.191` — every one below 1. Whenever `\|X_a\| < 1` and the realized `rho_absX` straddles `0.10`, disagreement follows. The producer had `s_X = 1.0` and knew from the quoted review measurement that `s_X` exceeded every realized `\|hkz\|`; §2.3's own stated basis for P-R7 is that quoted measurement. Falsifying it required no disagreement at **any** of 9 hkz cells x 2 normalizations. Its content is a units fact, not a finding. |
| **P-R1** | `X_mp` passes at a majority of pairs | **GENUINELY LIVE.** `R-OUT-5` would have voided every `G-REL` verdict in the section. It held at 10/10 and 14/19. |
| **P-R6** | `hkz` `L7/L8 beta=5` not significant | **GENUINELY LIVE** — an independent replication that could have disagreed. See §5. |

So: **2 live, not 3**. This is a calibration point about the section's
evidential weight, not a defect. The report's instinct — "a pre-registration
in which every prediction lands is weak evidence that the predictions were
demanding" — is the right instinct and I am extending it by one row.

**The load-bearing verdict is unaffected.** `R-OUT-1` rests on P-R2+P-R3, both
forced, which is *why* the refusal is robust: a conclusion reachable by
algebra is not at the mercy of a measurement. The narrowness is in §2, not
here.

---

## 5. The digit-for-digit replication claim (`probes/probe_replication.py`, 0.33 s)

`report_relvar.md` §5(i) claims "AGREEMENT to every reported digit", on a
different OS, architecture, Python and numpy. The comparison there is at 3–5
significant figures, because that is the precision the predecessor's *report*
printed. The predecessor's **committed probe output** carries per-basis `hkz`
values to 6 decimals. I compared all of them.

**R1 — the agreement is REAL and STRONGER than claimed.** 48 committed values
(3 betas x 8 bases x 2 sides of `L7/L8`): **24 of 24 pairs agree at 6
decimals**, max absolute deviation `4.84e-07`, i.e. exactly the rounding of
the predecessor's printed precision. This is a measurement against my own
thesis and I report it at full weight: the shared-precision suspicion is
wrong.

**R2 — but it is a portability result, not method independence, and the
distinction matters.**

* Basis construction is `numpy.random.default_rng([1, d, k, i])` (PCG64, a
  platform-independent seed sequence) into exact `int64`. The **input** to the
  reduction is bit-identical across platforms *by construction*, not by
  agreement.
* `fpylll` is `0.6.4` in **both** runs — the report's §8 table records this as
  an EXACT MATCH. Any systematic behaviour of the HKZ enumeration is therefore
  common to both.
* **Against my thesis again:** I expected a shared code path and did not find
  one. No function is AST-identical between the predecessor's probe and
  `measure_relvar.py`, and **neither** is AST-identical to the declared common
  ancestor `measure_am4.py`, despite both labelling the pipeline "CARRIED
  VERBATIM" (identifier-set Jaccard 0.66–0.77). Three independent
  implementations agreeing to 6 decimals on shared seeds is a genuine result
  and rules out a platform-dependent float artifact in the HKZ profile at
  these cells.

**What remains true and should be stated in the record rather than the
stronger phrase:** the agreement tests the *specification's* portability
across three implementations and two platforms with an exactly matched
`fpylll`. It cannot detect an error in the shared specification or in
`fpylll 0.6.4`. "This is the strongest replication in this section" is fair;
"a measurement of ours, not an inheritance of theirs" is fair; an unqualified
reading as *independent confirmation of correctness* is not, and no successor
should quote it that way.

**One orientation detail, checked and clean.** The producer's table shows
`beta=5` mean gap `-0.001027` against the quoted `0.00103`, annotated
"(magnitude; mirror direction)", while the `t` signs match. I checked the
predecessor's probe source: it prints `abs(c0.mean() - a0.mean())`, a
magnitude, with a signed `t`. The producer's annotation is correct.

---

## 6. Section B' — is the null the right null? (`probes/probe_bprime.py`, 4.7 s, 101.7 MB)

Gate first: I reproduced `n_fire` across the whole `c` grid from the committed
per-step values — **matches the committed table exactly**.

### 6.1 The headline number is a function of two standard errors

A step fires at `c = 6` iff `c_min <= 6` iff
`SE_step/SE_diff <= (5 + Delta/SE_diff)/t_crit`, a ratio threshold of
`5/4.2071245566 = 1.18846` at `Delta = 0`.

    realized SE_step/SE_diff over the 48 live steps
        min 0.7861   median 1.0370   max 1.4632   sd 0.1489      (my computation)
    n_fire(c=6) realized                                35
    n_fire(c=6) from the ratio alone (Delta ignored)    34
    n_fire(c=6) with Delta forced to 0                  34
    median Delta / SE_diff                              -0.0326

`Delta` — the only quantity in the statistic that carries information about
the object — moves the headline by **one step of 48**, which is exactly the
detection floor the section itself declares (`1 of 48 = 2.083` percentage
points). The report says the count is set "almost entirely" by the ratio; the
measurement says the residual is one floor unit.

### 6.2 P-B1's falsifier was all but unreachable (RT-4)

Monte Carlo of the frozen statistic — `r_j(t_i)` iid across the 13 grid points
and 8 draws with an independent 8-draw reference arm, which is the exact
exchangeability the mandated independent-frame construction realizes; the
model is mine, the `t_crit`, `n_draw`, `c` grid and 48-step family size are
frozen. 20 000 reps:

    n_fire(c=6) over 48:  mean 34.0   sd 4.2   min 16   max 48
    P(n_fire <= 21)  =  0.00175      <- P-B1's pre-registered falsifier
    P(n_fire <= 29)  =  0.14110      <- "below the committed real count"
    realized                35        <- inside the bulk; the model matches the object

The prediction's falsifier had probability `0.00175` under the null the
amendment itself mandated. That is a statement about **the prediction**, not
about the producer's conduct: the pre-registration predicted the outcome it
got, said in advance that this arrangement counts as a FAIL rather than a null
result, and reported it. But P-B1 "HOLDS" carries essentially no evidential
weight, and the section's content is the **mechanism** it exposed, which the
report does state (§3) and which §6.1 and §6.3 here quantify.

**A second could-not-fail direction inside the criterion.** prereg 3.3's PASS
clause has two conjuncts, and the second — "`n_fire(c)` **decays** as `c`
decreases toward the negative control" — is a tautology:
`n_fire(c) = #{i : c_min(i) <= c}` is monotone non-decreasing in `c` by
definition, for any family whatsoever. `report_nullfam.md` §2 says so —
"Monotone non-decreasing in `c`, as it must be" — which is honest, but the
clause was pre-registered as half of a pass/fail criterion. The criterion is
effectively single-clause.

### 6.3 Is it a null "of the same shape"? (RT-5)

`c_min` is affine in `SE_step/SE_diff`, so that ratio *is* the shape parameter
for this statistic. The exact null keeps the real arm's `SE_step` and
`SE_diff` and sets `Delta := 0`, so its `c_min = 1 + t_crit * ratio` exactly,
and the committed exact-null `c_min` median of `2.990` inverts to

    implied SE_step/SE_diff of the REAL arm        0.4730
    median SE_step/SE_diff of the NULL FAMILY      1.0370      factor 2.19

The two objects differ by a factor of 2.19 in the one parameter the statistic
is a function of, however much of the pipeline is carried byte-for-byte. AM-13
asks for "the identical count computed on a NULL OBJECT of the same shape";
the pipeline is the same shape and the variance structure is not.

**This does not disturb the direction of the finding, and I say so at the same
weight as the objection.** On the rebuilt null family `n_fire(c = 6)` is 35 of
48, against the committed real count of 29 of 48 and the Red Team's exact-null
benchmark of 47 of 48 — both nulls at or above the real count, under two
different variance structures, which is *more* robust than one comparison
would be. What is not interpretable is the signed magnitude `-6`: it is 1.4
Monte-Carlo sd of the null count (`sd 4.2`), and the two arms' ratios differ
by 2.19x. **AM-11 applied to the producer's own headline statistic: `n_fire`
is reported without any dispersion, and it has a sampling sd of about 4.2 of
48 — roughly two of the section's own detection-floor units.**

### 6.4 The count saturates instead of decaying, and that is the real result (RT-6)

Ask what the parameter meant to destroy the effect should do. For a count of
this kind that parameter is the number of draws `n`: more data should make a
null *harder* to call. Under a null with ratio 1 the expected `c_min` is
`1 + t_{n-1, 0.998}`:

| `n_draw` | 8 | 12 | 16 | 32 | 64 | 128 | → ∞ |
| --- | --- | --- | --- | --- | --- | --- | --- |
| expected null `c_min` | **5.207** | 4.573 | 4.286 | 3.999 | 3.933 | 3.905 | **3.878** |
| fires at the carried `c = 6`? | yes | yes | yes | yes | yes | yes | yes |

The carried headline `c = 6` lies **above** the null's own `c_min` at every
`n`, and the gap widens with `n`. So the null count rises toward `48 of 48`
with more data. This is `docs/inventor-protocol.md` §3's artifact tell in its
exact form, stated as a property of the statistic rather than of one
realization, and it is a stronger statement than the single 35-vs-29
comparison the section rests on.

**Forward guidance, because a closure needs one.** This does not close
anything: it names the discriminating region that stays **open**. Only
`c < 1 + t_crit = 5.207` at `n_draw = 8` can separate a real arm from a null
at all, which is where the `c` grid's `0..4` rungs sit — and there the two
objects do separate (null family `0, 0, 1, 1, 10`; the committed real count at
`c = 4` is 16 and the exact-null benchmark at `c = 4` is 42). Whether that
separation is an effect is untested by anything in this batch, and I do not
claim it is. **AM-3 IS NOT RETIRED**; its power remains undemonstrated rather
than disproved, and nothing here disproves it. **BATCH-a44d08 is not rescored
in any respect.**

---

## 7. Section C1 — attacking the `N-C` exclusion (`probes/probe_c1_nc.py`, 0.19 s)

**First, the boundary.** AM-14(c) *itself* names the four `N-A`/`N-B` medians
("on this batch's rebuilt nulls (medians 0.65%, 0.98%, 0.77%, 1.50%) the
frozen rule gives 0.025"). The exclusion of `N-C` is therefore a **carry**,
not the producer's discretion, and challenging it would re-litigate AM-14,
which I am forbidden to do and would decline to do anyway. What is fair game
is the producer's stated **mechanism**, which is a claim of its own.

The claim: for Gaussian errors `R ~ Beta(beta/2,(d-beta)/2)` exactly, so `D`
is driven to ~0 on both sides and the denominator `max(|D_GR|,|D_TL|)`
collapses; `N-C`'s medians `1.0216` / `1.0050` are an artifact of a vanishing
denominator, not a measure of null central tendency.

The committed replicate records let both terms be recovered, since
`relative_difference = |Delta_bar| / max(|D_GR|,|D_TL|)`:

| null | R | median `\|Delta_bar\|` | median recovered denominator | median rel. diff |
| --- | --- | --- | --- | --- |
| `N-A d100_b40` | 300 | `3.34e-04` | `5.16e-02` | `6.46e-03` |
| `N-A d140_b40` | 300 | `4.16e-04` | `4.28e-02` | `9.77e-03` |
| `N-B d100_b40` | 300 | `3.98e-04` | `5.17e-02` | `7.68e-03` |
| `N-B d140_b40` | 300 | `6.57e-04` | `4.39e-02` | `1.50e-02` |
| `N-C d100_b40` | **60** | `5.17e-04` | **`4.75e-04`** | `1.02e+00` |
| `N-C d140_b40` | **60** | `3.62e-04` | **`3.35e-04`** | `1.00e+00` |

**The stated mechanism is CONFIRMED, against my thesis.** The denominator
collapses by a factor of **117.9** while the numerator moves by **1.08**. The
report's explanation is the right explanation. And the exclusion is not
self-serving: including `N-C` under the same carried rule would give
`tau_rel = 1.67 x 1.0216 = 1.706`, which makes the relative-difference clause
*harder* to satisfy and a FALSIFYING verdict *less* reachable. The producer's
choice moves the instrument toward falsifiability, not away.

**RT-10, AM-11 applied to `tau_rel` itself.** `tau_rel` is the **maximum of
four numbers** — the most dispersion-sensitive functional of a four-point
sample — and no dispersion is attached to it anywhere in the batch. The four
medians span a factor of 2.32 (`0.00646 .. 0.01496`). The same carried rule
read at the same four nulls' **p95** instead of their median gives
`1.67 x 0.0440 = 0.0735`, a factor 2.94. **No verdict moves**: `report_c1.md`
reports all ten targets at `0.15` and at `0.025` and all ten are invariant,
and `0.0735` lies between them. The point is a disclosure gap, not a verdict
risk, and I state the second half as loudly as the first.

**RT-8 companion — P-C1c was near-forced, and the mechanism is the useful
part.** The four targets with `SE_2way/SE_naive < 1` are, from the committed
`scoring` block, exactly the four smallest `nu_eff` in the family:

    d100_b30/unreduced          nu_eff 1.000   ratio 0.3635   |t|crit 70.02
    d140_b40/graded_t0.0025     nu_eff 1.346   ratio 0.9651   |t|crit 25.36
    d140_b40/unreduced          nu_eff 1.426   ratio 0.8397   |t|crit 21.62
    d100_b40/unreduced          nu_eff 1.503   ratio 0.8495   |t|crit 18.90
    ---- every other target has nu_eff >= 2.639 and ratio >= 1.04 ----

Small `nu_eff` means `MS_S + MS_P - MS_res` is small, which is the same
quantity that makes `SE_2way` small. The AM-14(e) tension the report discloses
is a **degeneracy signature concentrated at low `nu_eff`**, not a property
spread across the family — which is forward guidance the disclosure alone does
not give, and which is checkable from the committed `nu_eff` column. P-C1c's
falsifier ("every target has ratio `>= 1`") was therefore close to dead given
committed numbers readable before the re-score. AM-14(e) requires the
reporting, and the reporting is done correctly; the *prediction* around it
carried little.

**P-C1a.** The producer records it FALSIFIED and diagnoses it as pointed the
wrong way, since lowering `tau_rel` can only make "floor `>=` tau_rel" more
common. That diagnosis is arithmetically correct and the self-report is
exactly the right handling. I add only that this makes P-C1a a
could-not-**PASS** prediction — deterministically, not probabilistically —
which is the mirror image of P-B1 in §6.2.

**Detection-floor citation.** I verified the producer's attribution: exactly
one of the ten targets is `NEGATIVE_VARIANCE_COMPONENT` under the committed
`se_decomposition`, and it is `d100_b40 / graded_t0.0025` with `nu_eff = 21.0`
by the residual-df fallback — the target carrying the `3.91%` figure, which is
**not citable without the NEGATIVE-VARIANCE-COMPONENT qualifier; the tightest
non-degenerate floor is `10.83%` relative and the family-level bound over
targets with a well-defined two-way SE is `~10.8%` relative**. The report
handles this correctly in prose. One presentational risk: the table cell shows
the bold figure with the qualifier only in the paragraph below it, which is
where a downstream quotation would lose it.

---

## 8. Section C2 — I built the control the producer declined (`probes/probe_c2_centered.py`, 0.85 s, 102.2 MB)

Gate first: my transcription of `se_decomposition` / `full_score` reproduces
the **committed** scoring at all ten targets at **max relative deviation
`0.0`**, verdicts included. Everything below measures the producer's
instrument, not mine.

### 8.1 P-C2e could not have failed (RT-7) — the section ran in its could-not-FIRE arrangement

`se_decomposition` computes `MS_S`, `MS_P` and `MS_res` from `(row - gm)`,
`(col - gm)` and `(D - row - col + gm)`. Adding a constant `c` to every entry
adds `c` to `gm`, to every row mean and to every column mean, leaving all
three **algebraically unchanged**. `SE`, `nu_eff` and the
`NEGATIVE_VARIANCE_COMPONENT` flag are invariants of the constant-offset group
action. Measured:

    max SE relative deviation over the FROZEN ladder (0 .. 12 SE)   8.527e-16
        -- I reproduce report_c2.md's reported 8.53e-16 exactly
    max SE relative deviation at offsets up to 1e6 * SE             8.938e-11
    targets whose NEGATIVE_VARIANCE_COMPONENT flag ever changed     0 of 10
    max |SE relative change| under a STRUCTURED one-column offset   1.168e+01

Pushing the offset **five orders of magnitude past the pre-registered ladder**
leaves the deviation at cancellation level. `8.53e-16` is the signature of an
exact identity, not the outcome of a test that could have failed.

prereg 5.4 names the could-not-FIRE arrangement as "the injection is applied
to `Delta_bar` **after** the variance decomposition, so `SE` is unchanged by
construction and inflation can never be detected" and claims it is averted by
injecting into the raw `S x E` table. **For a constant offset those two are
the same operation**, because the decomposition is exactly equivariant. The
section ran in the arrangement it declared averted. `report_c2.md` §2's
"which is what AM-14(b) asked to be shown rather than assumed" therefore
overstates: what was shown is that the *implementation* contains no bug
breaking an identity — a real check that would catch, say, an uncentred sum of
squares, but not the SE inflation AM-14(b) names.

The structured injection makes the point constructively: the same shift in
`Delta_bar` delivered through **one pool column** moves the recovered SE by up
to `11.68` relative. SE response is observable — under injections that move
the variance components, which is the class the frozen ladder excludes by
construction. (Caveat stated plainly: a real violation need not look like a
single-column offset. The claim is only that the ladder's injection class is
exactly the estimator's invariance class.)

### 8.2 The centered control — and the producer's diagnosis is CONFIRMED

`report_c2.md` §4 records P-C2c FALSIFIED, diagnoses it as a defect in prereg
5.2's own SHOULD-NOT-catch clause rather than in the instrument, proposes a
centered variant, and declines to run it because it is unregistered. **The
refusal to self-rescue is correct discipline and the right call.** It also
leaves the diagnosis untested, and an unregistered check is exactly what a
red-team probe is for. I recorded my expectation in the probe source *before*
running it — that the producer would be right and I would be wrong.

`D_centered = D - mean(D)`, then the frozen ladder, frozen `alpha_pair`,
frozen `tau_rel` at both `0.15` and `0.025`:

    targets firing at delta/SE <= 1.0 on the CENTERED table:  0 of 10

**The producer's diagnosis is confirmed.** The single fire at `delta/SE = 1.0`
in the committed run is arithmetic on a target whose committed `|t|` was
already `88.5%` of its own critical value, not instrument over-sensitivity.

**And the control yields a quantity the batch does not otherwise have** — the
instrument's own sensitivity ladder, in `delta/SE` units, isolated from each
target's committed effect:

| cell | target | `\|t\|crit` | first firing rung @ `tau_rel=0.15` | @ `0.025` |
| --- | --- | --- | --- | --- |
| `d100_b30` | `graded_t0.0025` | 6.97 | 12.0 | 8.0 |
| `d100_b30` | `graded_t0.0050` | 4.98 | 6.0 | 6.0 |
| `d100_b30` | `unreduced` | 70.02 | never on the ladder | never |
| `d100_b40` | `graded_t0.0025` | 2.87 | 12.0 | 3.0 |
| `d100_b40` | `graded_t0.0075` | 5.36 | 6.0 | 6.0 |
| `d100_b40` | `unreduced` | 18.90 | never | never |
| `d140_b30` | `graded_t0.0025` | 4.80 | 8.0 | 6.0 |
| `d140_b40` | `graded_t0.0025` | 25.36 | never | never |
| `d140_b40` | `graded_t0.0050` | 5.12 | 6.0 | 6.0 |
| `d140_b40` | `unreduced` | 21.62 | never | never |

Read as a control on the instrument and nothing else: **4 of 10 targets are
not reachable at all by a 12-SE injection**, and they are exactly the four
degenerate-`nu_eff` targets of §7. `report_c2.md` §5 already says the control
correctly does not fire there; the centered ladder shows that this is not a
property of those targets' committed effects but of their critical values. The
remaining six first fire between 3 and 12 SE depending on the floor in use.

---

## 9. The could-not-fail arrangement, BOTH DIRECTIONS, for each of the four producers

Required by my gate. For each producer: the arrangement in which its check
could not have failed, in each direction, and **whether it ran in it**.

### 9.1 `TASK-20260809-cda2f6` — Section R (`report_relvar.md`)

| check | could-not-FIRE | ran in it? | could-not-PASS | ran in it? |
| --- | --- | --- | --- | --- |
| `G-VAR` | a loose tolerance lets float noise lift a closed form above the bar, so nothing is refused | **NO** — decided by bit identity, and it fired on two candidates | every candidate is a closed form, so it refuses everything vacuously | **NO** — it admits `lam1n`, `hkz`, `rawtail` at 0 of their cells bit-identical |
| `G-VAR`, **the direction neither the prereg nor the report names** | the criterion is a property of the ARITHMETIC ROUTE: a mathematically parameter-determined observable evaluated by any float path is never refused | **YES — IT RAN IN IT.** `probe_nullroute`: `X_null` via QR of `B^T` and via `BH`, 0 of 38 bit-identical, `5.1e-14`/`3.1e-14` from the closed form, prereg 2.6 reproduced 304/304, `G-REL2` 19/19, **admitted** | symmetrically, any observable submitted matrix-free is refused whatever it means | **YES** — `X_null` and `rdet` are refused because of their route, and the producer's own `rdet_T1 = 3.865e-12` shows the same observable escapes on an isometry presentation |
| `G-REL` | evaluated at `\|X\|` only, so small `\|X\|` clears `0.10` on noise | **NO** — both normalizations at every entry with `s_X/\|X\|`, plus the paired `t` and its floor | every `\|X\| << s_X`, so `G-REL` is an absolute `0.10` test nothing can clear | **NO**, and this is stronger than I expected: `rawtail` passes **19 of 19** of its pinned `REL2` entries and `hkz` passes **47 of 48** pinned `REL1` entries |
| `X_mp` guard | chosen after seeing which candidates pass | **NO** — fixed in the notarized text, `R-OUT-5` live | *(not named by the prereg)* the guard's amplitude is so far above the candidates' that passing is uninformative about resolution | **YES, in the amplitude sense** — `mu` 0.224 against `hkz` 16.3 and `lam1n` 2.30; §3 |

### 9.2 `TASK-20260809-311784` — Section B' (`report_nullfam.md`)

| check | could-not-FIRE | ran in it? | could-not-PASS | ran in it? |
| --- | --- | --- | --- | --- |
| the decay criterion | the null uses a different pipeline, so any difference is a pipeline artifact | **NO** — everything but the frame draw carried byte-for-byte | `c_min` is dominated by `t_crit * SE_step/SE_diff`, so the counts coincide whatever the path structure | **YES — and the prereg declared in advance that this is a FAIL.** Correctly handled |
| the decay criterion's **second conjunct** | — | — | "`n_fire(c)` decays as `c` decreases" is true of any family by definition | **YES — vacuous.** The criterion is effectively single-clause |
| **P-B1 itself** | *(unnamed)* the falsifier `n_fire <= 21` is unreachable for an independent-frame null, whose SE ratio is centred on 1 by construction | **YES — IT RAN IN IT.** `P = 0.00175` over 20 000 reps | P-B1 could not have "failed to hold" in any practical sense | **YES**, same measurement |
| the null's shape | — | — | *(unnamed)* the two objects' `SE_step/SE_diff` differ by 2.19x, and `c_min` is affine in exactly that | **YES** — §6.3 |

### 9.3 `TASK-20260809-97d6cf` — Section C1 (`report_c1.md`)

| check | could-not-FIRE | ran in it? | could-not-PASS | ran in it? |
| --- | --- | --- | --- | --- |
| the re-score | clause (i) `\|t\|` binds at every target and clause (ii) never bound, so nothing moves | **YES — and prereg 4.5 declared this as the most likely outcome before the run.** All ten verdicts invariant | the widened band is so wide every target enters it | **NO** — 1 of 10 |
| **P-C1a** | — | — | lowering `tau_rel` can only make "floor `>=` tau_rel" **more** common, so a prediction that a target moves **out** of it is arithmetically impossible | **YES — deterministically.** The producer records it FALSIFIED and diagnoses it correctly |
| **P-C1c** | — | — | the four sub-1 ratios are the four smallest `nu_eff`, all in the degenerate regime, and those `nu_eff` were committed and readable before the re-score | **YES, near-deterministically** — §7 |
| `tau_rel` derivation | — | — | *(unnamed)* the rule reads a **maximum of four** with no dispersion attached | **YES** — but no verdict moves under the alternative reading; §7 |

### 9.4 `TASK-20260809-3eb72c` — Section C2 (`report_c2.md`)

| check | could-not-FIRE | ran in it? | could-not-PASS | ran in it? |
| --- | --- | --- | --- | --- |
| SE-inflation detection (P-C2e) | the injection leaves `SE` unchanged by construction, so inflation can never be detected | **YES — IT RAN IN IT, contrary to prereg 5.4.** A constant offset is an exact symmetry of `se_decomposition`; injecting into the raw table is the same operation as shifting `Delta_bar`. `8.527e-16` over the ladder, `8.9e-11` at `1e6 * SE` | *(no meaningful direction: an exact identity cannot fail)* | **YES** |
| the ladder | the ladder starts so high every rung fires | **NO** — starts at `0.5 SE`, below every `\|t\|crit` | the bottom rungs can never fire, so P-C2c is vacuous | **NO** — the bottom rung **did** fire at one target, which is why the falsification is on the record |
| P-C2c's reading | *(the producer's own diagnosis)* an uncentered ladder cannot separate over-sensitivity from a pre-existing near-critical `Delta_bar` | **YES — and the diagnosis is CORRECT**, confirmed by the centered control I built: 0 of 10 fire at `<= 1.0 SE` | — | — |
| P-C2d | — | — | the four targets that do not fire at 12 SE are exactly those with `\|t\|crit >= 8`, driven by `nu_eff` of 1.00–1.50 | **partly** — the prediction is conditioned on `\|t\|crit < 8` and so excludes them by construction; correctly declared in advance |

---

## 10. Measurements that went AGAINST my own thesis

Listed together, at the same weight as §0's objections, because the
predecessor's adverse findings are why its report was credited.

1. **The Coordinator's git claims are all correct** — three-way split,
   30-for-30 at HEAD *and* at the declared commits, and the D3 table exactly
   9-for-9. I looked for an error of the BATCH-cbe023 F-1 class and there is
   none. Two of three declared UNKNOWNs additionally resolve in the
   affirmative. §1
2. **My predecessor's probes were not lost.** All six files are committed at
   HEAD. My own task card's premise is wrong. §1
3. **The MUST-PASS guard does fire under the pinned normalization** — 19 of 19
   pinned `REL2` entries, and `hkz` passes 47 of 48 pinned `REL1` entries. My
   predicted "regime mismatch" objection is refuted; only the amplitude
   objection survives. §3
4. **The unimodular re-presentation did not escape `G-VAR`.** I predicted
   `slogdet(UB)` would break bit identity; it is bit-identical at 38 of 38 for
   both observables. The escape needed the QR and isometry routes. §2.2
5. **The cross-platform agreement is stronger than the report claims** — 24 of
   24 per-basis pairs at 6 decimals, max deviation `4.84e-07`, and the three
   implementations are textually distinct with no AST-identical function even
   against the declared common ancestor. §5
6. **The producer's diagnosis of P-C2c is correct** — the centered control I
   built to test it returns 0 of 10 targets firing at `delta/SE <= 1.0`. §8.2
7. **The stated mechanism for excluding `N-C` is correct** — denominator
   collapses `117.9x`, numerator moves `1.08x` — and the exclusion moves the
   instrument *toward* falsifiability (`tau_rel` 0.025 rather than 1.706). §7
8. **`results_relvar.json` is internally consistent** — every reported `G_REL2`
   aggregate recomputes from its own per-basis entries at max deviation `0.0`,
   at all five candidates. §3
9. **`results_nullfam.json` reproduces its own count table** from its
   committed per-step values, exactly, across the whole `c` grid. §6
10. **`RT-10` does not move a verdict.** The alternative `tau_rel` reading
    lies between `0.025` and `0.15`, and all ten verdicts are invariant across
    both. §7

---

## 11. Cheapest falsification of every headline, with its cost

Costs are measured on this host unless marked *estimated*; where estimated I
say so rather than reporting a number I did not measure.

| headline | cheapest falsifier | cost |
| --- | --- | --- |
| **R:** the gate is INADMISSIBLE under `G-VAR` (`R-OUT-1`) | Exhibit any cell where the notarized closed-form `X_null` is **not** bit-identical across the 8 bases under the producer's own route, or where it fails a gate clause. Re-run `measure_relvar.py`'s `x_null_of` over the 38 cells. | **0.31 s measured** (`probe_nullroute` R0 column). *Not falsified: R0 is 38/38.* |
| **R:** "`G-VAR` … cannot be tuned into or out of firing" | Evaluate the same closed form through a float route and score it through the identical path. | **0.31 s, 39 MB, measured — ALREADY FALSIFIED** (`probe_nullroute` R2/R5). Cheaper still: read `forced_arithmetic.rdet_T1_ambient_isometry_residual = 3.865e-12` in the committed JSON — **zero new compute**. |
| **R:** `rdet` is a parameter-determined observable the gate admits | Present the frozen bases post-isometry and re-run the bit test. | **0.31 s measured**; `rdet\|R5` is 0 of 38 bit-identical. |
| **R:** the MUST-PASS guard shows `G-REL` "was not pinned into never firing" | Count `rawtail`'s pinned-regime passes. | **0.14 s measured — NOT falsified**, 19 of 19. |
| **R:** the guard licenses `G-REL` verdicts on the candidates | Compute `mu` for guard and candidates at the same cells. | **0.14 s measured**; `mu` 0.224 vs 16.3 / 2.30. |
| **R:** all 7 predictions hold; 3 are live | Check whether P-R7's falsifier was reachable given frozen `s_X = 1.0` and the quoted `\|hkz\|` range. | **zero compute** — reading `report_relvar.md` §5(i)'s own `s_X/\|X\|` column. |
| **R:** digit-for-digit agreement across platforms | Compare the predecessor's committed 6-decimal per-basis values with the producer's committed per-basis values. | **0.33 s measured — NOT falsified**, 24/24. |
| **B':** `n_fire(c=6)` = 35 of 48 on the null family, against the committed real count of 29 of 48 and the exact-null benchmark of 47 of 48; the decay check FAILS | Recompute `n_fire` from the committed per-step values. | **4.7 s measured (dominated by the 20 000-rep Monte Carlo; the recomputation alone is <0.1 s) — NOT falsified**, matches exactly. |
| **B':** P-B1 HOLDS | Monte-Carlo the frozen statistic under the mandated null and read `P(n_fire <= 21)`. | **4.7 s, 102 MB measured**; `P = 0.00175`. |
| **B':** the null is a null "of the same shape" | Invert the committed exact-null `c_min` median for the real arm's SE ratio and compare. | **<0.1 s measured**; 0.473 vs 1.037. |
| **C1:** `tau_rel = 0.025`; all ten verdicts invariant | Re-derive from the committed medians and re-score at both floors. | **0.19 s measured — NOT falsified.** |
| **C1:** `N-C` excluded because its denominator collapses | Recover numerator and denominator from the committed replicate records. | **0.19 s measured — NOT falsified**, 117.9x vs 1.08x. |
| **C1:** `tau_rel` is well determined | Read the same rule at the four nulls' p95 instead of their median. | **0.19 s measured**; 0.0735 vs 0.025, no verdict moves. |
| **C2:** no SE inflation detected (`8.53e-16`), P-C2e HOLDS | Raise the constant offset past the ladder and watch the deviation; then inject non-constantly. | **0.85 s, 102 MB measured — the *interpretation* is falsified**: `8.9e-11` at `1e6 SE`, `11.68` relative under a one-column injection. |
| **C2:** P-C2c's falsification is a prereg defect, not an instrument defect | Build the centered control and count the fires at `<= 1.0 SE`. | **0.85 s measured — NOT falsified**, 0 of 10. |
| **Coordination record:** the 3-way split, 30-for-30, the D3 table | Recompute every declared hash from the git object database and rebuild the D3 table from the committed queue. | **0.43 s measured — NOT falsified.** |
| **Anything cryptographic** | *n/a* | There is no cryptographic claim in this batch to falsify. Claim tier TOY; no baseline exists; `dominated_by` and `sota_delta` are `null` for that reason and not by omission. |

**Total probe compute for this entire review: ~7 s wall and 102 MB peak, against a 7200 s / 4 GB budget.** No cap bound. Every falsifier above is
seconds, which is itself a finding: nothing in this batch is expensive to
check, so no future objection to it can be priced out.

---

## 12. EVERY PROBE PATH, DECLARED EXPLICITLY

All paths are repository-relative, all sit under my assigned `write_scope`
`coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7`,
and **all are uncommitted**. `TASK-20260809-60f9cc` must declare every one of
these 21 paths (this report plus 20 probe files) in its `artifact_paths`, or
the evidence is lost.

```
coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/red_team_report.md
coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_gitrecord.py
coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_gitrecord_output.json
coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_nullroute.py
coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_nullroute_output.json
coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_nullroute_output.txt
coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_guard.py
coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_guard_output.json
coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_guard_output.txt
coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_bprime.py
coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_bprime_output.json
coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_bprime_output.txt
coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_c1_nc.py
coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_c1_nc_output.json
coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_c1_nc_output.txt
coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_c2_centered.py
coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_c2_centered_output.json
coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_c2_centered_output.txt
coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_replication.py
coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_replication_output.json
coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_replication_output.txt
```

Every probe re-executes from the repository root with
`python3 <path> [--out <file>]`, carries its could-not-fail arrangements in
both directions in its own module docstring **before** its code, and states in
its output record that it is NOT PRE-REGISTERED and rescores no frozen
verdict. `probe_gitrecord.py` writes its JSON to stdout; the others take
`--out`.

**Every probe here is a probe on my own frames.** None is pre-registered; each
ran at the scale stated in its output (`reps`, `n_cells`, `n_targets`,
`n_bases`); and **none rescores any frozen verdict**. Where a probe reproduces
a committed number, it is a reproduction gate on my own code, never a
re-adjudication of the producer's.

---

## 13. AM-10 and AM-11 applied to EVERY statistic, including my own

AM-10: replication across all frozen bases / cells / targets, with the
between-unit mean, sd and a paired test where one applies. AM-11: non-zero
dispersion reported for every statistic.

| statistic | proposer | AM-10 | AM-11 | note |
| --- | --- | --- | --- | --- |
| `rho` at both normalizations, `s_X/\|X\|` | R | **met** — 8 bases, mean/sd/min/median/max per cell | **met** | three aggregation readings reported, all agreeing |
| `mean_g`, `sd_g`, `t_paired`, detection floor | R | **met** — paired over 8 bases, df 7 | **met** | |
| `float_sd`, `bit_identical`, cell counts | R | **met** — 8 bases at 38 cells | **met** — `float_sd` reported beside the bit test | but the **decision** discards the dispersion it reports; §2.4 |
| `hkz_violation` | R | max over 48 reductions | **not met** — a max, no dispersion | instrument check at exact `0.0`; immaterial |
| `n_fire(c=6)` **headline** | B' | **met** — per cell 9/11/8/7 and pooled | **NOT MET** — no dispersion anywhere | sampling sd ≈ **4.2 of 48** (my MC); the `-6` difference is 1.4 sd. §6.3 |
| `c_min`, `se_step/se_diff` | B' | **met** — per cell medians | **met** — min/median/max per cell | |
| `mean Delta` over 48 steps | B' | **met** | **met** — `+4.345e-05` against per-step sd `~1.1e-03` | correctly labelled a construction check, not a test |
| `tau_rel = 0.025` | C1 | 4 nulls x 300 replicates | **NOT MET** — a max of four medians, no dispersion | p95 reading gives `0.0735`; no verdict moves. §7 |
| per-target `\|t\|`, rel. diff, floor | C1 | **met** — 10 targets, each from an 8x4 table | **met** — SE and `nu_eff` per target | |
| `SE_2way/SE_naive` | C1 | **met** — all 10 | **met** — range `0.3635..1.3686` | concentrated at the four smallest `nu_eff`; §7 |
| SE recovery deviation | C2 | **met** — 10 targets x 9 rungs | **met** — max over all | but the quantity is an invariant; §8.1 |
| `\|t\|` monotonicity | C2 | **met** — 10 of 10 | n/a (Boolean) | |
| first-firing rung (centered) | **mine** | **met** — 10 targets | **met** — range and the 4 never-firing named | §8.2 |
| route bit-identity + `float_sd` | **mine** | **met** — 8 bases x 38 cells x 6 routes | **met** — sd, min, max, spread per cell | §2.2 |
| `mu` amplitude multiplier | **mine** | **met** — 8 bases per cell | **met** — n/mean/sd/min/median/max | §3 |
| MC `n_fire` distribution | **mine** | **met** — 20 000 reps x 4 cells x 12 steps | **met** — sd 4.2, full percentile vector | §6.2 |
| recovered null denominators | **mine** | **met** — 300/300/300/300/60/60, unequal replication disclosed | **met** — min/median/p95/max | §7 |
| 6-decimal agreement | **mine** | **met** — 8 bases x 3 betas x 2 sides | **met** — max and median deviation | §5 |

---

## 14. Prohibitions, checked against myself

* I altered **no** Executor receipt and **no** Validator report; I read them at
  `c034ef38` / `1aa7db53` and wrote only under my own `write_scope`.
* I called **no** bounded failure an impossibility. RT-1 bounds a criterion's
  generality; it does not say a dispersion criterion cannot work, and §2.5
  names a concrete construction that would.
* I rejected **nothing** for being surprising, and rejected **no** conditional
  result for being conditional.
* I claimed **no** broader conclusion: nothing here has a cost path, because
  nothing here has a cost model.
* **AM-10..AM-14 are not re-litigated.** Where AM-14(c) mandates an exclusion,
  I attacked only the producer's stated mechanism and said so (§7).
  **AM-3 IS NOT RETIRED.** **BATCH-a44d08 IS NOT RESCORED IN ANY RESPECT.**
  **AM4-OBS-1** is cited only through `knowledge/findings/KN-FIND-f38a89.md`
  and is not relied on here. `k = |K_I|`, `k_fpylll = d - k` (AM-9) throughout.
* Non-citable phrases: I have not restated the BATCH-cbe023 relocation phrase
  as a claim (RT-9 reports the producer's near-use of its vocabulary without
  asserting it); `29 of 48` appears only beside `47 of 48` in the same
  sentence; BATCH-cbe023's non-citable verdict word is asserted in
  neither direction and appears nowhere in this report; `3.91%` appears
  only with its NEGATIVE-VARIANCE-COMPONENT qualifier and the non-degenerate
  `10.83%`.
* `knowledge/INDEX.md` was **not** written, regenerated or staged. I ran no
  `git add`, no `git commit`, and no write outside my `write_scope`.
* **Premature closure avoided.** Nothing here closes a lane. §6.4 names what
  stays open (`c < 5.207`), §2.5 names a concrete replacement criterion, and
  §8.1 names the injection class that would make AM-14(b)'s target
  observable.
* No measurement, timing, citation or run is fabricated. No timeout, crash or
  missing dependency occurred; had one, it would be INFRASTRUCTURE SIGNAL and
  never negative mathematical evidence.

---

## 15. Narrowest supported statement

> At `q = 3329`, `d in {20, 30, 40, 100, 140}` and the frozen `(k, beta)` grid,
> with 8 frozen bases and no reduction beyond the frozen HKZ pipeline at
> `d <= 40`, and at claim tier **TOY**:
>
> BATCH-9e3584's four producers ran their declared measurements on committed,
> content-verified artifacts, and their arithmetic reproduces. `R-OUT-1`
> stands as reported — the notarized closed-form `X_null` walks `G-REL`,
> `G-NUM`, `G-INV` and `G-Q` while bit-identical across the 8 bases at all 38
> scored cells, `G-VAR` fires, and **no admissibility claim is reportable from
> that gate in either direction**.
>
> What is **not** supported is the generality claimed for the refusal.
> `G-VAR` as implemented decides on the arithmetic route by which an
> observable is evaluated, not on the observable: the same closed form
> evaluated by a QR of `B^T` or on an ambient-isometry presentation is 0 of 38
> cells bit-identical, agrees with the notarized prereg 2.6 table at 304 of
> 304 entries to every printed digit, walks `G-REL2` at 19 of 19 cells, and is
> **admitted**. Adding `G-VAR` in its present form therefore does not repair
> the gate against the failure mode AM-11 names.
>
> Section B''s count is a function of two standard-error estimates: `Delta`
> moves it by one step of 48, its null value **rises** toward the ceiling with
> more draws, and P-B1's falsifier had probability `0.00175` under the null
> AM-13 mandates. The section's artifact verdict is right, and better
> supported by that mechanism than by the single count comparison it rests on.
>
> Section C1 changes no verdict, as it declared in advance, and its stated
> reasons check out. Section C2's instrument is clean on translation
> equivariance, which is what it actually measured; SE inflation of the kind
> AM-14(b) names remains **untested**, because a constant offset is an exact
> symmetry of the estimator under test. The centered control, built here,
> confirms the producer's own diagnosis of P-C2c and additionally supplies the
> instrument's sensitivity ladder: 4 of 10 targets are unreachable by a 12-SE
> injection, and they are the four degenerate-`nu_eff` targets.
>
> Nothing in this batch bears on ML-KEM security, on any FIPS 203 parameter
> set, on any attack cost, or on any cost model. There is no cryptographic
> baseline, so `dominated_by` and `sota_delta` are `null` for that reason.
> Independence in this goal is procedural and never model-level; AGENTS.md
> rule 12 is UNMET AND UNWAIVED.

---

## 16. Required output record

```yaml
red_team_report:
  id: RT-20260811-444fe7
  task_id: TASK-20260809-444fe7
  goal_id: GOAL-MLKEM-005
  batch_id: BATCH-9e3584
  claim_tier: toy
  snapshot_read:
    producers: c034ef38003028a20b8e97f7f0a55bd6a16fdb5d
    pre_registration: 1aa7db5313f6d3da1f366443d4d6066597393402
    receipts_and_queue: 502d15a0fc51d7d21ac04830b61f02fe56d58029
    read_method: >-
      git show <commit>:<path> for every producer artifact and for the frozen
      pre-registration; never from the working tree.
  claim_under_review: >-
    BATCH-9e3584's four producer headlines. Section R's R-OUT-1 (the AM-4/AM-8
    gate is INADMISSIBLE under G-VAR because X_null walks it while bit-identical
    across all 8 frozen bases at all 38 scored cells, with X8 = rdet unplanted
    and equally bit-identical); Section B''s null-family count and FAILED decay
    check; Section C1's re-derived tau_rel = 0.025 with all ten verdicts invariant;
    and Section C2's no-SE-inflation result at 8.53e-16 with its self-recorded
    falsification of P-C2c.
  objections:
  - id: RT-1
    severity: major
    target: TASK-20260809-cda2f6 / report_relvar.md section 5(iii)
    statement: >-
      G-VAR as implemented refuses an ARITHMETIC ROUTE, not an observable. AM-11
      quantifies over closed-form FUNCTIONS of (d,k,beta,q); bit identity is a
      property of the evaluation path. The same X_null evaluated by QR of B^T
      or on an ambient-isometry presentation BH is 0 of 38 cells bit-identical,
      agrees with the closed form to 5.07e-14 and 3.11e-14 relative, reproduces
      the notarized prereg 2.6 table at 304 of 304 cell-by-basis entries to every
      printed digit, walks G-REL1 at 10 of 10 and G-REL2 at 19 of 19, and is ADMITTED.
      The report's "it cannot be tuned into or out of firing" is false as stated.
    does_not_overturn: >-
      R-OUT-1 itself. One refused blind observable suffices for the inadmissibility
      verdict; what falls is the generality of the criterion and the forward inference
      that adding G-VAR repairs the gate.
    evidence: probes/probe_nullroute.py + probe_nullroute_output.json
  - id: RT-2
    severity: moderate
    target: TASK-20260809-cda2f6 / report_relvar.md section 4
    statement: >-
      The report states that G-INV residuals for rdet and X_null are zero identically.
      results_relvar.json records forced_arithmetic.rdet_T1_ambient_isometry_residual
      = 3.865352482534945e-12. True for T2 and T3 (both 0.0), FALSE for T1 in
      the producer's own artifact - and that residual is exactly the vanishing
      basis dependence that escapes the bit test, so the unplanted-rdet finding
      is a property of the integer-LU route on this block-triangular presentation.
    evidence: results_relvar.json (c034ef38); probes/probe_nullroute_output.json
  - id: RT-3
    severity: moderate
    target: TASK-20260809-cda2f6 / report_relvar.md section 7
    statement: >-
      The MUST-PASS guard satisfies AM-10(c) in the letter and fires under the
      pinned normalization (19 of 19 pinned REL2 entries), but it clears tau_rel
      at amplitude multiplier mu median 0.224 while hkz misses at 16.3 and lam1n
      at 2.30; at identical cells the guard's mirrored gap is 2.5x-266x the candidate's.
      rawtail and hkz are the same functional form on the raw and reduced basis.
      A binary guard reports that the criterion can fire, never what it can resolve.
      The same pre-registration gives Section C2 a graded ladder and Section R
      a binary guard.
    evidence: probes/probe_guard.py + probe_guard_output.json
  - id: RT-4
    severity: moderate
    target: TASK-20260809-311784 / report_nullfam.md section 5
    statement: >-
      P-B1's falsifier (n_fire(c=6) at most 21 of 48) had probability 0.00175
      under a null of the shape AM-13 mandates (20000 reps of the frozen statistic).
      n_fire from the SE ratio alone is 34, with Delta forced to 0 it is 34, realized
      35: the only information-carrying quantity moves the headline by exactly
      one detection-floor unit. Separately, prereg 3.3's decay conjunct is a tautology
      - n_fire(c) is monotone in c by definition - so the criterion is effectively
      single-clause.
    evidence: probes/probe_bprime.py + probe_bprime_output.json
  - id: RT-5
    severity: moderate
    target: TASK-20260809-311784 / report_nullfam.md section 4
    statement: >-
      c_min is affine in SE_step/SE_diff, so that ratio is the shape parameter
      for this statistic. The null family's median is 1.0370; the real arm's,
      recovered from the committed exact-null c_min median 2.990, is 0.4730 -
      a factor 2.19. The two objects are not the same shape for this statistic.
      The DIRECTION of the finding is unaffected; the signed magnitude is not
      interpretable, being 1.4 Monte-Carlo sd of the null count.
    evidence: probes/probe_bprime_output.json
  - id: RT-6
    severity: moderate
    target: TASK-20260809-311784 / report_nullfam.md section 2
    statement: >-
      Ask what should destroy the count. Under a null with ratio 1 the expected
      c_min is 1 + t_{n-1,0.998}, which FALLS with more draws (5.207 at n=8 to
      3.878 as n grows), and the carried headline c = 6 lies above it at every
      n. The null count therefore saturates upward toward 48 of 48 with more data.
      This strengthens the section's artifact verdict and names the region that
      stays open: only c below 1 + t_crit = 5.207 can discriminate at n_draw =
      8.
    evidence: probes/probe_bprime_output.json
  - id: RT-7
    severity: major
    target: TASK-20260809-3eb72c / report_c2.md section 2 and prereg 5.4
    statement: >-
      P-C2e could not have failed. se_decomposition is exactly equivariant under
      a constant offset (MS_S, MS_P, MS_res are functions of centred deviations
      only), so injecting into the raw S x E table is the same operation as shifting
      Delta_bar afterwards - which is the could-not-FIRE arrangement prereg 5.4
      claims to have averted. Measured: 8.527e-16 over the frozen ladder (reproducing
      the reported 8.53e-16) and 8.938e-11 at offsets of 1e6 SE, while a structured
      one-column injection moves the SE by 11.68 relative. The section verified
      an implementation identity, not SE inflation; SE inflation of the kind AM-14(b)
      names remains UNTESTED.
    evidence: probes/probe_c2_centered.py + probe_c2_centered_output.json
  - id: RT-8
    severity: minor
    target: TASK-20260809-cda2f6 / report_relvar.md section 6
    statement: >-
      Of the seven predictions, four are forced by algebra and correctly labelled
      UNTESTED, and a fifth (P-R7) reduces to a units fact readable from the frozen
      s_X = 1.0 and the committed |hkz| in 0.025 to 0.191, all below 1. Two, not
      three, had genuinely live falsifiers: P-R1 and P-R6. The report's own instinct
      about a 7-for-7 record is right; this extends it by one row and does not
      disturb R-OUT-1, which rests on forced rows.
    evidence: report_relvar.md sections 5(i)/6; results_relvar.json G_REL2
  - id: RT-9
    severity: minor
    target: TASK-20260809-cda2f6 / report_relvar.md sections 7 and 11
    statement: >-
      Section 11 asserts the report does not use BATCH-cbe023's non-citable relocation
      phrase; section 7 contains "closed here rather than relocated", which reintroduces
      that phrase's vocabulary inside a comparative claim about BATCH-cbe023.
      Narrow compliance observation; no measurement depends on it and this report
      does not restate the phrase as a claim.
    evidence: report_relvar.md sections 7, 11
  - id: RT-10
    severity: minor
    target: TASK-20260809-97d6cf / report_c1.md section 1
    statement: >-
      tau_rel = 0.025 is the maximum of four numbers spanning a factor 2.32, the
      most dispersion-sensitive functional of a four-point sample, and carries
      no dispersion anywhere. The same carried rule read at those four nulls'
      p95 gives 0.0735, a factor 2.94. Reported for completeness: NO verdict moves,
      since all ten are invariant at 0.15 and 0.025 and the alternative lies between
      them.
    evidence: probes/probe_c1_nc.py + probe_c1_nc_output.json
  findings_against_my_own_thesis:
  - >-
    The three Coordinator claims about the git record are ALL CORRECT - the three-way
    split, 30 of 30 content match at HEAD (and, additionally, at the declared
    commits), and the D3 table exactly 9 dangling / 9 undeclared. Both archive
    commit messages additionally carry their task id and GOAL-MLKEM-005, resolving
    two of the Coordinator's three UNKNOWNs.
  - >-
    My own task card's premise that the predecessor's probes were lost is FALSE.
    All six files are committed at HEAD (b33158fc) and this review depends on
    two of them.
  - >-
    The MUST-PASS guard DOES fire under the pinned normalization (19 of 19 pinned
    REL2 entries) and hkz passes 47 of 48 pinned REL1 entries. My predicted regime-mismatch
    objection is refuted; only the amplitude objection survives.
  - >-
    My predicted escape route through a unimodular re-presentation DID NOT escape
    G-VAR - slogdet(UB) is bit-identical at 38 of 38 for both observables.
  - >-
    The cross-platform agreement is STRONGER than report_relvar.md claims - 24
    of 24 per-basis pairs agree at 6 decimals (max deviation 4.84e-07), and the
    predecessor probe, the producer script and the declared common ancestor share
    NO AST-identical function.
  - >-
    The producer's diagnosis of P-C2c is CONFIRMED by the centered control I built
    - 0 of 10 targets fire at delta/SE at most 1.0.
  - >-
    The stated mechanism for excluding N-C is CONFIRMED (denominator collapses
    117.9x, numerator moves 1.08x), and the exclusion moves the instrument TOWARD
    falsifiability (tau_rel 0.025 rather than 1.706).
  - >-
    results_relvar.json is internally consistent - every reported G_REL2 aggregate
    recomputes from its per-basis entries at max deviation 0.0. results_nullfam.json
    reproduces its own n_fire table exactly.
  required_controls:
  - >-
    A SCALED dispersion criterion replacing bit identity - between-basis sd against
    the candidate's own between-cell range at fixed (d,k) - reported as a 38-cell
    profile rather than an all-cells Boolean. On the measured numbers the escaping
    routes sit at 1e-13 against a between-cell range of order 1, while hkz sits
    at 2.4e-2.
  - >-
    Every candidate observable scored through AT LEAST TWO arithmetic routes,
    with the route declared beside the value, before any G-VAR verdict is reported.
    The route is currently an undeclared free parameter of the gate.
  - >-
    A GRADED (lambda-scaled) MUST-PASS guard for any G-REL-class criterion, reporting
    the crossing amplitude, so the guard measures resolution rather than mere
    non-deadness. Cost: one loop over already-computed numbers.
  - >-
    For any count-style headline, its sampling dispersion under the declared null
    (n_fire has sd about 4.2 of 48 here) and the probability of its own falsifier
    under that null, both reported beside the count.
  - >-
    For any SE-validation control, at least one NON-CONSTANT injection, since
    a constant offset is an exact symmetry of the estimator under test.
  - >-
    The centered variant of C2 (BUILT here) adopted as the standard form of that
    control, because the uncentered ladder cannot separate instrument sensitivity
    from a target's committed effect.
  counterexample_or_mutation: >-
    BUILT, not proposed. X_null evaluated as (beta/d)(1/d) * sum_i log|R_ii| from
    the QR of B^T, and as (beta/d)(1/d) * log|det(BH)| for a fixed ambient isometry
    H. Both are the same function of (d,k,beta,q) as the refused X_null - equal
    to (beta/d^2)(d-k) log q for every A - both reproduce the notarized prereg
    2.6 table at 304 of 304 cell-by-basis entries to every printed digit, both
    walk G-REL1 (10/10) and G-REL2 (19/19), and both are ADMITTED by G-VAR at
    0 of 38 cells bit-identical. Companion controls also built: the centered C2
    ladder, the structured one-column injection, the Monte-Carlo null-of-the-null
    for n_fire, the recovered N-C denominators, the 6-decimal cross-platform comparison,
    and an independent verification of the git record.
  baseline_comparison: >-
    NOT APPLICABLE, and stated rather than omitted. This batch proposes no algorithm,
    no cost model and no attack, so there is no Pollard-rho, BSGS or specialized-baseline
    comparison to make and no cryptographic frontier to sit on. dominated_by and
    sota_delta are null FOR THAT REASON, checked against every axis (time, memory,
    data/queries) by observing that no axis is claimed. The only comparisons available
    are internal instrument comparisons and they are made in the report: X_null
    against rdet/lam1n/hkz/rawtail through the identical gate; the rebuilt null
    family against the committed real count and against the exact-null benchmark;
    tau_rel 0.025 against 0.15; and the constant against the structured injection.
  heuristic_challenges:
  - >-
    IMPLICIT HEURISTIC, UNNUMBERED - "bit identity of 8 IEEE-754 doubles operationalizes
    AM-11's zero between-basis variance". FALSE as a general identification; it
    holds only relative to a fixed arithmetic route. Cheapest exposure: evaluate
    the same closed form by QR - 0.31 s, done.
  - >-
    IMPLICIT HEURISTIC, UNNUMBERED - "a MUST-PASS guard that passes shows the
    criterion is usable on the candidates". It shows the criterion is not identically
    dead. The guard's amplitude is one to two orders of magnitude above the candidates'.
    Cheapest exposure: the mu statistic - 0.14 s, done.
  - >-
    IMPLICIT HEURISTIC, UNNUMBERED - "a null family differing from the real arm
    in exactly one construction step is a null of the same shape". For a statistic
    affine in SE_step/SE_diff, sameness of shape is sameness of that ratio; measured
    factor 2.19. Cheapest exposure: invert the committed exact-null c_min median
    - under 0.1 s, done.
  - >-
    IMPLICIT HEURISTIC, UNNUMBERED - "injecting into the raw table rather than
    into Delta_bar makes the control able to detect SE inflation". False for a
    constant offset, which is an exact symmetry of the decomposition. Cheapest
    exposure: raise the offset to 1e6 SE and watch the deviation stay at cancellation
    level - 0.85 s, done.
  - >-
    RANDOM-MODEL TRANSFER, on my own Monte Carlo and disclosed as mine. It models
    r_j(t_i) as exchangeable Gaussians, which is what independent Haar frames
    are designed to deliver but is not what quantile ratios of CBD errors exactly
    are. Guarded by reporting the realized per-step ratios beside the simulated
    ones; the realized n_fire of 35 sits inside the simulated bulk (mean 34.0,
    sd 4.2), so the model matches the object at the resolution used. The realized
    numbers, not the model, carry RT-4's finding; the model supplies only the
    falsifier probability.
  cost_model_challenges:
  - >-
    NO COST MODEL IS PROPOSED ANYWHERE IN THIS BATCH, so there is nothing to recompute
    with o(1)/polylog overheads made explicit, no memory-beside-time claim to
    audit, no per-attempt-cost-times-inverse-success- probability bookkeeping
    to check, and no van Oorschot-Wiener interpolation to price. Recorded as satisfied-by-absence
    rather than skipped.
  - >-
    The only costs present are instrument costs and they are honestly reported:
    Section R 48.38 s with 17.25 s of reduction, max hkz_violation 0.0 over 48
    reductions, no cap bound; Section B' 119.5 s; C1 0.25 s; C2 0.24 s. I verified
    the artifacts carry them and that validity is VALID with used_runs 1 of 1
    at each producer.
  - >-
    Cost of the review itself, measured: about 7 s of probe compute and 102.2
    MB peak against a 7200 s / 4 GB budget. Every falsifier in section 11 of the
    report costs seconds, so no future objection to this batch can be priced out.
  reduction_and_scope_challenges:
  - >-
    NO published reduction is instantiated anywhere in this batch, so there is
    no cited theorem whose hypotheses could fail to transfer.
  - >-
    SCOPE IS NOT INFLATED, verified clause by clause: every producer report carries
    an explicit "what this does NOT establish" section, each disclaims ML-KEM
    security, FIPS 203 parameter sets, attack costs and cost models, each records
    certificate.kind none with its reason, and each states the absence of a cryptographic
    baseline. The tested scope - q = 3329, d in {20,30,40,100,140}, reduction-dependent
    candidates at d at most 40 - is stated in the artifacts and is far below any
    cryptographic dimension.
  - >-
    ONE SCOPE RISK, presentational: report_c1.md's table cell carries the 3.91%
    figure in bold with its NEGATIVE-VARIANCE-COMPONENT qualifier only in the
    paragraph below, which is where a downstream quotation would lose it. The
    tightest non-degenerate floor is 10.83% relative and the family-level bound
    over targets with a well-defined two-way SE is about 10.8% relative.
  proof_architecture_challenges:
  - >-
    OBSERVATION-FIBER ATTACK, executed and successful. Hold the observation (the
    reported value of X_null, and the whole G-REL/G-NUM/G-INV/G-Q transcript)
    fixed and vary the underlying object - here the evaluation route rather than
    the lattice. Two preimages land on opposite sides of the G-VAR conclusion
    while agreeing to 14 significant digits and reproducing the notarized table
    at 304 of 304 entries. THE MISSING SEPARATOR IS A SCALE: G-VAR draws its line
    at exactly zero in a quantity (float_sd) that the artifact already records
    and that spans 13 orders of magnitude across the candidates.
  - >-
    QUANTIFIER-ORDER ATTACK. AM-11 reads "for every closed-form function of (d,k,beta,q)
    ... MUST be refused". The implementation realizes "for every VALUE ARRAY produced
    by a chosen route ...". The witness (the route) is selected after the observable,
    which is exactly the order the amendment does not license. Section R's own
    G-REL aggregation rule is handled correctly by contrast: three readings reported,
    all agreeing, and the choice declared as an implementation completion.
  - >-
    NEARBY-OBJECT ATTACK, executed. The closest object for which the desired conclusion
    is false is X_null-by-QR, and G-VAR fails to distinguish it from an admissible
    observable. The missing problem-specific ingredient is a dispersion SCALE
    anchored to the observable's own dynamic range.
  - >-
    BOUNDARY AND STRICTNESS ATTACK on Section C2. The old method (closed-form
    arithmetic in the SE) is supposed to be strictly embedded as the boundary
    of the new one (inject and re-run the full path). For a CONSTANT offset the
    two coincide exactly, so the perturbation is not strictly better; it becomes
    strictly better only under a non-constant injection, which the frozen ladder
    excludes.
  - >-
    METHOD-CEILING ATTACK on Section B'. The largest claim n_fire can support
    at n_draw = 8 is bounded by the null's own expected c_min of 5.207; at the
    carried c = 6 the ceiling is "the null fires almost always", so no positive
    power statement about AM-3 is reachable at that c by any amount of data. This
    is a ceiling on the STATISTIC AT THAT c, not on AM-3: AM-3 IS NOT RETIRED,
    and c below 5.207 is where its power remains testable.
  - >-
    COMPOSITIONAL-INVARIANT ATTACK on the AM-4/AM-8 gate. Deleting G-VAR leaves
    the gate admitting X_null (the batch's own finding). Adding G-VAR in its present
    form leaves the gate admitting X_null-by-QR (this report's finding). So the
    strengthened invariant still does not imply the final target - "an admitted
    observable carries information about the lattice" - and the first step that
    fails is the operationalization of dispersion.
  narrowest_supported_statement: >-
    At q = 3329, d in {20,30,40,100,140}, the frozen (k,beta) grid, 8 frozen bases,
    no reduction beyond the frozen HKZ pipeline at d at most 40, claim tier TOY:
    R-OUT-1 stands as reported - the notarized closed-form X_null walks the AM-4
    gate while bit-identical across the 8 bases at all 38 scored cells, G-VAR
    fires, and NO ADMISSIBILITY CLAIM IS REPORTABLE FROM THAT GATE IN EITHER DIRECTION.
    What is NOT supported is the generality claimed for the refusal: G-VAR as
    implemented decides on the arithmetic route, and the same closed form evaluated
    by QR of B^T or on an ambient-isometry presentation is admitted at 0 of 38
    cells bit-identical while reproducing the notarized prereg 2.6 table at 304
    of 304 entries and walking G-REL2 at 19 of 19. Section B''s count is a function
    of two standard-error estimates whose null value RISES with more draws and
    whose pre-registered falsifier had probability 0.00175; its artifact verdict
    is right and is better supported by that mechanism than by the single count
    comparison. Section C1 changes no verdict, as declared in advance, and its
    stated reasons check out. Section C2 measured translation equivariance, not
    SE inflation, which remains UNTESTED. Nothing bears on ML-KEM security, any
    FIPS 203 parameter set, any attack cost or any cost model; there is no cryptographic
    baseline, so dominated_by and sota_delta are null for that reason. AM-3 IS
    NOT RETIRED; BATCH-a44d08 IS NOT RESCORED IN ANY RESPECT.
  next_concrete_action: >-
    ONE BOUNDED TASK, and it is cheap because everything in this batch is: re-specify
    G-VAR as a SCALED dispersion criterion - between-basis sd at fixed (d,k,beta,q)
    measured against the candidate's own between-cell range at fixed (d,k), reported
    as a 38-cell profile rather than an all-cells Boolean - and require every
    candidate to be scored through AT LEAST TWO declared arithmetic routes, with
    the route recorded beside each value. Validate it against the six routes already
    built in probes/probe_nullroute.py, whose committed output gives the target
    behaviour: all six routes to X_null and rdet must be REFUSED, while lam1n,
    hkz and rawtail remain ADMITTED. Estimated cost, by comparison with the measured
    0.31 s of probe_nullroute.py and the measured 48.38 s of the producer run
    it would replace: seconds to low minutes, d at most 40, no new reduction.
    Until that runs, no admissibility claim is reportable from this gate in either
    direction, and this report asserts none.
  dominated_by: null
  sota_delta: null
  dominated_by_justification: >-
    Checked against every axis of the frontier - time, memory, data/queries -
    by establishing that the batch claims none of them: no algorithm, no cost
    model, no attack, no solve, no relation, certificate.kind none in every manifest.
    There is therefore no frontier row to compare against and the null is a checked
    null, not an unchecked one (AGENTS.md rule 5, docs/inventor-protocol.md Pareto
    honesty). A successor that presents any of this against a cryptographic baseline
    must first supply the baseline.
  inference:
    requested_policy: review-adversarial
    reasoning_effort: xhigh
    resolved_model_id: null
    model_verified: false
    model_verified_reason: >-
      This runtime binds no model provenance. No adapter probe receipt exists
      for this session and the resolved model cannot be probed from inside a subagent,
      so the identifier is unverified configuration rather than a verified binding.
      Recorded as a verification gap, never as satisfied.
    fallback_used: false
    degraded_allowed: false
    independent_session: true
    independence_note: >-
      PROCEDURAL AND NEVER MODEL-LEVEL. AGENTS.md rule 12 is UNMET AND UNWAIVED.
      The session that authored the pre-registration also ran all four producers
      and made both archives; this review and TASK-20260809-3f1dc4 are the batch's
      entire independence budget. I produced none of the artifacts under review.
  budget_used:
    wall_clock_seconds_of_probe_compute: 7.4
    peak_child_rss_mb: 102.2
    runs: 1
    caps_bound: false
  validity:
    status: VALID
    note: >-
      No timeout, crash or missing dependency occurred. Had one occurred it would
      be INFRASTRUCTURE SIGNAL and never negative mathematical evidence.
  artifact_paths:
  - >-
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/red_team_report.md
  - >-
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_gitrecord.py
  - >-
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_gitrecord_output.json
  - >-
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_nullroute.py
  - >-
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_nullroute_output.json
  - >-
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_nullroute_output.txt
  - >-
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_guard.py
  - >-
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_guard_output.json
  - >-
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_guard_output.txt
  - >-
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_bprime.py
  - >-
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_bprime_output.json
  - >-
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_bprime_output.txt
  - >-
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_c1_nc.py
  - >-
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_c1_nc_output.json
  - >-
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_c1_nc_output.txt
  - >-
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_c2_centered.py
  - >-
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_c2_centered_output.json
  - >-
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_c2_centered_output.txt
  - >-
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_replication.py
  - >-
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_replication_output.json
  - >-
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/reviews/TASK-20260809-444fe7/probes/probe_replication_output.txt
  archive_instruction: >-
    TASK-20260809-60f9cc must declare ALL 21 paths above in its artifact_paths.
    They are uncommitted and are the sole carriers of their own evidence (PD-4,
    open). An undeclared probe cannot be committed and its evidence is lost.

```
