# Execution report — EXP-ICINV-e0cd8f

- **Task** TASK-20260810-ab0a07 · **Goal** GOAL-ENDO-001 · **Batch** BATCH-d7e255
- **Contract** `experiments/EXP-ICINV-e0cd8f/specification.yaml` version 1,
  `status: approved`, `approved_by: coordinator`, approving decision
  DEC-20260810-a4bec4. Read at run time and bound by
  `sha256 9ec38891fdee6285025d0cddbe1fdc364839091e4f5204eb06ae59836a245781`.
  READ-ONLY to this task; not modified.
- **Hypothesis** H-ICINV-d5e351 — **status unchanged (`specified`)**. This task
  changed no hypothesis status and wrote no ledger or evidence record.
- **Claim tier** toy. No attack, no exponent, no speedup, `sota_delta` zero.
- **Runs** `RUN-ICINV-e0cd8f-s0`, `RUN-ICINV-e0cd8f-s1` (2 of a maximum 8).

**THIS REPORT INTERPRETS NOTHING.** It records what ran, what did not, every
deviation, the gate outcomes and the measured numbers.

---

## 1. Terminal outcome

**Both runs terminated at the SR3 backend gate with status
`failed_infrastructure` (failure class `infrastructure_error`). NEITHER FROZEN
VERDICT WAS EMITTED.** `verdict.json` in each run records
`frozen_verdict_emitted: null` and `outcome: SR3-GATE-STOP`.

This is an infrastructure stop under AGENTS.md rule 5 and the contract's own
`absence_is_infrastructure` clause. **It is not negative mathematical evidence,
not a null result, and in particular not evidence that any Semaev invariant is
constant or varying across the isogeny class.** H-ICINV-d5e351 is untouched in
both directions.

Selecting `CLASS-INVARIANT` or `CLASS-VARYING` here would be fabrication: both
are verdicts about four invariant families across the class *and* its control
set, and only one family was computed, on the class only.

---

## 2. Gate outcomes, in contract order

### SR1 — support gate: **PASSED**

Symbolic re-derivation of the S_3 monomial-support counts, computed twice by
two engines that share no code:

| | generic | `a = 0` | `b = 0` |
|---|---|---|---|
| SageMath 10.9, `QQ[a,b,x1,x2,x3]` | 13 | 9 | 10 |
| sympy 1.14.0 (independent) | 13 | 9 | 10 |
| committed reference, read at run time | 13 | 9 | 10 |

The reference counts were **read from
`coordination/.../BATCH-cb71b5/reviews/red-team/red_team_notes.md` at run time**
and bound by `source_sha256
414d850b5b91a5718fb4c178a2c2d36da16269346fe45f535d5d54d57eea1850`. Nothing was
transcribed (EXP-ICINV-4d33aa amendment v2 change A4, CORR-20260807-a24675).

The `a = 0` and `b = 0` counts are derived **symbolically**, not observed: T4
fixes `D_0 = -59`, so `j = 0` and `j = 1728` cannot occur in this class and
`a != 0 != b` on every member — confirmed on all 138 enumerated members.

**S_3 monomial support on all 138 class members: 13 on every member**
(multiset `{13: 138}`, one distinct value). Cross-checked on **all 138** by
sympy: zero disagreements.

### SR2 — census gate: **PASSED**

Re-emitted from scratch by `harness/isogeny_class.py:enumerate_curves` /
`class_census`:

- enumerated members of the `p = 4001, t = 30` class: **138**
- `D = t^2 - 4p = -15104 = -59 * 16^2` (`D_0 = -59`, conductor `f = 16`)
- Hurwitz–Kronecker certification: observed weighted mass
  `sum 2/|Aut(E)| = 138.0` equals `H(4p - t^2) = 138.0` — **agrees**
- `|Aut|` multiset over the class: `{2: 138}`
- whole-field sanity: all **253** traces at `p = 4001` agree with the mass
  formula; **zero** disagreements
- agrees with the committed 138-member census (read at run time) and with the
  contract's `expected_member_count`

### SR3 — backend gate: **FIRED. This is the terminal stop.**

Declared and recorded **before any resolution was computed** and before any
ideal was built (`backend-provenance.json`,
`evaluated_before_any_resolution_was_computed: true`).

| backend | present | independent of Sage | minimal free resolutions |
|---|---|---|---|
| SageMath 10.9 (primary) | yes | — | **yes** |
| Macaulay2 | **no** | — | — |
| standalone Singular | **no** | — | — |
| Magma | **no** | — | — |
| Singular via Sage's interface | yes | **NO** | yes |
| sympy 1.14.0 | yes | yes | **no** |
| msolve 0.9.5 | yes | yes | **no** |

**msolve 0.9.5 was found on the host by this run and is not named in the
dispatching handoff's `second_backend_note`.** It is a genuinely independent
Gröbner engine and it broadens the cross-check for dimension and elimination
degree — but it computes no free resolution, so it does not close the gap.

Coverage decided **per primary metric**, because a backend that cannot compute a
metric cannot agree with another backend about it:

| primary metric | independent cross-check available |
|---|---|
| S_3 monomial support | sympy |
| singular-locus dimension | msolve |
| elimination-polynomial degree | sympy, msolve |
| elimination-polynomial factorisation type | sympy |
| **graded Betti numbers** | **NONE** |
| **Castelnuovo–Mumford regularity** | **NONE** |
| **singular-locus degree** | **NONE** |

**Why the gate fires.** C-BACKEND and success criterion (3) require a *second,
independent* backend agreeing on at least 20 curves including every curve
carrying a claimed difference. Three primary metrics admit **no independent
backend on this host at all**, in either verdict direction. Criterion (3)
therefore cannot be met as literally written, and the contract's
`absence_is_infrastructure` clause makes that a terminal infrastructure stop.

Per the handoff's `second_backend_note` this is **raised, not worked around**:
C-BACKEND was not relaxed, no weaker check was substituted for the cross-check,
and the run did not proceed past SR3 on the assumption that a substitute would
be accepted. The Coordinator decides: either a versioned `protocol_amendment`
under `experiments/EXP-ICINV-e0cd8f/amendments/` filed **before** any affected
data exists, or `failed_infrastructure` recorded as-is.

**No clean two-backend cross-check is claimed anywhere.** Sage's bundled
Singular is labelled throughout as a second *code path*, not a second backend.

### SR4–SR7

- **SR4 control-first — NOT REACHED.** SR4 is downstream of SR3. The 138-curve
  control set was **not drawn** and no control-set invariant was computed.
  `control-set-invariants.json` records `not_computed` with that reason and the
  reserved seed. **No class-versus-control comparison exists or is implied.**
- **SR5 frozen scope — honoured.** `p = 4001`, `t = 30`, `m ∈ {3, 4}`,
  degrevlex, standard grading. No extra prime, class, arity or grading.
- **SR6 budget — not exceeded.** See §5.
- **SR7 no outcome shopping — honoured.** The gate outcome and every multiset
  were computed inside the run and written to `verdict.json`; nothing was
  selected afterwards. The reported metric set does not depend on the outcome.

---

## 3. What was measured, and what was not

**Computed (one of four invariant families):**

| quantity | class multiset | distinct values |
|---|---|---|
| S_3 monomial support, all 138 members | `{13: 138}` | 1 |
| S_4 monomial support, all 138 members | `{439: 137, 391: 1}` | **2** |

**Not computed — every one a GATE statement under AGENTS.md rule 5, and NONE of
them constancy:** singular locus and its dimension and degree; graded Betti
table; Castelnuovo–Mumford regularity; elimination-polynomial degree and
factorisation type; the Koszul indicator (`C-KOSZUL`); the C-ORDER second
monomial order; the entire control set. **No ideal was built and no resolution
was computed** — `ideals_built: 0`, `resolutions_computed: 0`.

### Tail check — extreme-curve listing (contract-required, in full)

One member of the class deviates from the class mode in a computed family:

| field | value |
|---|---|
| curve_id | `TOY-P12-bc0b3378` |
| `(a, b)` | `(441, 294)` |
| j-invariant | `2257` |
| S_3 monomial support | `13` (= class mode) |
| **S_4 monomial support** | **`391`** vs class mode **`439`** |
| C-GAUGE recheck | `u = 1711`, gauged model `(2118, 2496)`: S_4 support **391**, S_3 support 13, exact weighted identity holds |
| independent cross-check (sympy) | S_4 support **391**, S_3 support 13 — **agrees** |
| true 2-volcano level | `not_computed` — the contract states this experiment does not rebuild the volcano; the distribution `{0: 3, 1: 9, 2: 18, 3: 36, 4: 72}` was read from the committed record as a reporting covariate only |

This difference **survives both C-GAUGE and the independent-backend
cross-check**. It is reported as a measurement. **What it means — including
whether it bears on isogeny-class invariance at all — is not decided here**;
the S_4 family is a contract *secondary* metric, no control set was computed,
and no resolution-derived family was computed.

Other tail checks: degenerate geometry (empty singular locus, unit ideal, zero
elimination ideal) — **not applicable, no ideal was built**. Control-set spread
— **not computed** (SR4 not reached). m = 3 versus m = 4 consistency — within
the support family only: all 138 members agree at m = 3; one member differs at
m = 4, listed above.

---

## 4. Controls

| control | status |
|---|---|
| C-SUPPORT | **discharged** — 13 / 9 / 10 re-derived symbolically by two engines and matched against the run-time-read reference |
| C-CENSUS | **discharged** — 138 members, Hurwitz-certified, agrees with committed census |
| C-GAUGE | **discharged for every computed invariant** — all 138 members, `u` drawn from seed `20260810`; S_3 and S_4 supports agree, and the exact weighted identity `S_3^{(u^4 a, u^6 b)}(u^2 x) == u^8 · S_3^{(a,b)}` holds on all 138. Zero disagreements |
| C-BACKEND | **NOT SATISFIABLE ON THIS HOST — the gate that fired.** Performed for what is coverable: S_3 support on all 138 (sympy, zero disagreements), S_4 support on a declared 21-curve subsample including the deviating curve (sympy, zero disagreements). Betti, regularity and singular-locus degree covered by **neither** path |
| C-ORDER | **not computed** — applies to resolution-derived quantities; no ideal built |
| C-KOSZUL | **not computed** — a property of the Jacobian generators; no ideal built |
| C-CONTROL-SET | **not computed** — SR4 not reached |

---

## 5. Budget

| | budget | s0 | s1 | total |
|---|---|---|---|---|
| wall clock | 7200 s / run | 27.3 s | 18.0 s | 45.3 s |
| CPU | 6 h total | 7.20 s | 7.52 s | 14.7 s |
| peak RSS | 8 GB | 90.8 MB | 91.8 MB | — |
| runs | 8 max | — | — | **2** |

**No budget was exhausted.** The stop is the SR3 gate, not the budget.

Host load averages recorded at run time in `environment.json`
(`[52.7, 49.9, 48.0]` on 14 cores at the s0 probe). Both runs were
**single-threaded and sequential** by instruction; no task was parallelised and
no other BATCH-d7e255 task was started. Contention affected wall clock only —
every output is an exact symbolic invariant over F_p and cannot be corrupted by
it.

---

## 6. Deviations from the approved protocol — recorded, not discarded

1. **SR3 raised as a stopping-rule outcome instead of the contract's
   cross-check being performed as written.** The contract's C-BACKEND is not
   satisfiable on this host for three primary metrics. Escalated to the
   Coordinator per the handoff. C-BACKEND was **not** relaxed by the executor.
2. **Two runs where one was planned; the second corrects the first's
   cross-check subsample rule.** `RUN-ICINV-e0cd8f-s0` declared its C-BACKEND
   subsample as the first 20 curve_ids in sorted order. That run then observed
   a curve deviating in the S_4 family, and that curve was **not** in its
   subsample — so s0's cross-check did not cover the one difference s0
   exhibited. `RUN-ICINV-e0cd8f-s1` changes the rule to *first 20 UNION every
   curve deviating from the class mode*, computed inside the run, giving a
   21-curve subsample that contains the deviating curve.
   **`RUN-ICINV-e0cd8f-s0` IS RETAINED IN FULL, is not deleted, re-keyed or
   re-scored, and its manifest stands as written.** s1 records
   `supersedes: RUN-ICINV-e0cd8f-s0` with the reason. This is not rerunning
   until a favourable result appears: both runs report the identical measured
   multisets and the identical SR3 gate outcome; only the cross-check coverage
   of the deviating curve differs.
3. **`msolve 0.9.5` present on the host and not named in the handoff's
   backend inventory.** Recorded in `backend-provenance.json` with
   `discovered_by_this_run: true`. It does not change the SR3 outcome.
4. **Inference policy not served by the adapter-resolved model.**
   `AUTORESEARCH_POLICY` was unset, so this session was not launched with the
   adapter-resolved environment. `python3 -m orchestration.adapter resolve
   --role executor` resolves `executor-implementation -> anthropic:claude-sonnet-5
   (effort=medium)`; the model that actually answered is `claude-opus-5`. The
   handoff sets `fallback_allowed: false`, so this divergence is **recorded and
   escalated, not absorbed**: `inference.fallback_used: true` with its reason in
   both manifests. Every number in both runs is deterministic computer algebra
   with **no model in the loop**.
5. **Wall-clock ordering note.** The class enumeration (SR2's input) is
   computed before SR1 because SR1 needs the member list. The SR2 *comparison*
   and all three gate verdicts are evaluated in contract order SR1 → SR2 → SR3.
   Recorded in `class-census.json:note_on_ordering`.

**No curve was dropped. No infrastructure failure occurred beyond the missing
backend that is itself the SR3 outcome. No unexpected crash, timeout or OOM.**

---

## 7. Contract compliance checks

- **`python3 tools/check_run_source_provenance.py --experiment EXP-ICINV-e0cd8f
  --strict` → PASS**, exit 0: `2 pinned, 0 unpinned, 0 unreadable, of 2 run
  manifest(s) in scope`. `harness/exp_icinv_e0cd8f/sr1_support.sage` is pinned
  **explicitly** in both manifests, because it runs in a separate `sage`
  process and can never appear in the driver's `sys.modules`.
- **No `f_V` polynomial appears in any computed ideal — no ideal was computed
  at all.** `harness/semaev.py:118`'s `[S_3, fV1, fV2]` system was not reused.
  `f_V_present_in_any_ideal: false` in `per-curve-invariants.json`.
- **No p-value, permutation test, null-object test or dispersion statistic
  appears anywhere in the output.** `statistics_computed: "none"`.
- **`harness/semaev.py` and `harness/exp_icinv.py` were not edited.** All new
  code is in the new package `harness/exp_icinv_e0cd8f/`.
- **Certificate:** `kind: none`, explicitly. Pure measurement run — no
  discrete-log solve and no factor-base relation is claimed.
- **Write scope honoured exactly:** `harness/exp_icinv_e0cd8f/`,
  `experiments/EXP-ICINV-e0cd8f/runs/**`, and this file. The specification and
  `amendments/` were not written. No ledger, goal, knowledge, queue or other
  experiment path was touched.
- **Nothing was committed.** The Coordinator makes the snapshot commit.

## 8. Branch state against `origin/main`

- `git fetch origin main` run before the manifests were written.
- Base commit checked: `origin/main = c022cd2ded3e554884c72f40807bdafdd4921399`.
- Branch `feat/ecdlp-isogeny-experiments-f2eeb3` at
  `91eff124588f0263df1417832c2124679e1df836` (the snapshot commit named in the
  handoff), **0 behind / 2 ahead**. **Merge outcome: no merge required**;
  `origin/main` is an ancestor of HEAD. Nothing was rebased.
- Both runs recorded `code.commit: 91eff1245...`, `code.dirty: false`.

## 9. Artifacts

`experiments/EXP-ICINV-e0cd8f/runs/RUN-ICINV-e0cd8f-s0/` and
`experiments/EXP-ICINV-e0cd8f/runs/RUN-ICINV-e0cd8f-s1/`, each containing all
15 contract-required files — `manifest.yaml`, `command.txt`,
`environment.json`, `stdout.log`, `stderr.log`, `raw-result.json`,
`class-census.json`, `support-derivation.json`, `per-curve-invariants.json`,
`control-set-invariants.json`, `gauge-recheck.json`, `backend-crosscheck.json`,
`koszul-indicator.json`, `verdict.json`, `backend-provenance.json` — plus
`sr1-sage-input.json` and `sr1-sage-output.json`, both declared in the manifest
`artifacts` block.

Code: `harness/exp_icinv_e0cd8f/__init__.py`,
`harness/exp_icinv_e0cd8f/run_gate.py`,
`harness/exp_icinv_e0cd8f/sr1_support.sage`.

## 10. Scope and honesty

One prime `p = 4001` (~12 bits), one trace `t = 30`, one isogeny class of 138
curves, arities `m ∈ {3, 4}`, degrevlex, standard grading after homogenisation
with respect to `x0`. `claim_tier: toy`. **No attack, no exponent, no speedup;
`sota_delta` zero on every axis.** `dominated_by` parallel Pollard rho with
distinguished points at `0.886 sqrt(N)` group operations and `O(1)` memory
(KN-TECH-001, KN-TECH-006).

**No transfer is claimed** to another prime, class, arity, grading or monomial
order, and none to the deployed `f_V`-bearing formulation the harness actually
runs. The S_4 support difference recorded in §3 is **not** a predicted Gröbner
speedup and must not be reported as one: the campaign's committed −0.44% /
−0.67% Gröbner-time pair against an exact 23–31% drop in S_3 support is the
standing demonstration of that non-transfer.

**No GOAL-ENDO-001 completion criterion is claimed met by this task.** No
attestation and no closure quorum is recorded. Nothing here bears on
H-ICINV-6c7920 or EV-ENDO-10109d in either direction.
