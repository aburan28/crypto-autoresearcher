# Validation report — TASK-20260904-e13cf2

Independent Validator review of the RG-0 source-state census package produced by
`TASK-20260904-1f4e2f`.

Task `TASK-20260904-e13cf2` · Batch `BATCH-256a94` · Goal `GOAL-SSI-001`
Joints owned: **J1, J2, J3, J5**. J4 and J6 belong to `TASK-20260904-22e444`
and are invisible to me by construction; this report carries no whole-claim
verdict. The Coordinator composes.

---

## Citation prohibition (restated verbatim; NOT lifted by this artifact)

> The `P=512` crossover value and its `w=2^80` sign are **NOT
> citation-eligible**. This task does not lift that prohibition. Only a
> committed Coordinator decision on independently reviewed evidence can lift
> it.

Nothing in the four joints I own bears on that prohibition, and I make **no
recommendation to lift it**. A Validator recommendation would in any case not
be a decision: only a committed Coordinator decision on independently reviewed
evidence can lift it. As a precaution beyond the letter of the prohibition I
have withheld every substantive numeric value at `log2p = 512` from this
report, including ones the producer already published; `log2p = 512` rows are
referred to by coordinate and by residual magnitude only.

## Claim boundary

Record reading, code reading, `git` object inspection, and arithmetic on
already-committed literals. No experiment was executed, no timing was measured,
and `cost_model.py` was never imported or run. **No security,
standardized-parameter, exponent, or asymptotic-complexity claim is made in any
direction.** I changed no status, wrote no ledger record, committed nothing, and
wrote exactly one file, inside my assigned `write_scope`.

## Inference provenance (requested vs served)

| field | value |
| --- | --- |
| `requested_policy` | `review-adversarial` |
| `requested_reasoning_effort` | `xhigh` |
| `fallback_allowed` / `degraded_allowed` | `false` / `false` |
| `independent_session_required` | `true` |
| served by | Claude Code subagent `validator` (`.claude/agents/validator.md`, `model: inherit`, `effort: xhigh` at line 17) |
| `resolved_model_id` | `claude-opus-5`, as reported by the runtime |
| `fallback_used` | `false` — no substitution was made or accepted |
| `degraded_requirements` | none recorded |
| `model_verified` | **`false` / undetermined.** `AUTORESEARCH_POLICY` and `AUTORESEARCH_BACKEND` are unset in this session, so no `orchestration.adapter env` receipt binds the requested policy to the resolved model. I did not run `adapter doctor --probe`. Recorded as undetermined rather than asserted. |
| `independent_session` | `true` — I did not produce this package and hold no authorship of any artifact under review |
| Bedrock | no provider, backend, endpoint or model identifier containing `bedrock` was selected or contacted |

## Snapshot binding — is this a committed receipt?

Yes. Verified before any content review, per the prohibition on accepting a
working-tree-only artifact.

| check | result |
| --- | --- |
| snapshot commit `5872cf99a2e71c0455502244047ad3c2f019ccbc` exists and is reachable from `HEAD` | yes (`git merge-base --is-ancestor` → 0) |
| all seven declared artifacts: worktree sha256 == snapshot-commit sha256 == `HEAD` sha256 == receipt's `source_path_sha256` | **7 / 7 identical** |
| artifacts also identical at `c1a39ee5a` (the pre-archive publish commit named in the receipt's `content_first_note`) | 7 / 7 |
| receipt's `commit_sha` | `null`, `verification.status: pending_post_commit` — the receipt binds by **content**, and the content binding verifies. Recorded, not glossed. |
| producer wrote exactly the seven declared artifacts and nothing else | yes (`git show --name-status c1a39ee5a -- <task dir>` lists exactly the seven; `task_card.yaml` predates it, added in `7c8bf37cd`) |
| my own write scope was empty and untracked before this report | yes |

## Frozen-artifact immutability — stated, as required

**No file under `experiments/` was modified, moved, or staged by this batch.**

* `git log --since=2026-09-01 -- experiments/EXP-WESOVOW-001` → empty.
* `git diff 1f6fe9b4e^ HEAD -- experiments/` → empty (`1f6fe9b4e` is the batch's
  first commit, the producer's task claim).
* The last commits touching `experiments/EXP-WESOVOW-001` are `add98ba2a`
  (2026-08-24) and `7d188a7c3` (2026-08-08 23:46:54 −0700).
* `git status --porcelain` on the whole tree returns exactly one entry — my own
  untracked review directory. Nothing under `experiments/` is dirty.
* I read `experiments/EXP-WESOVOW-001/**` and both run directories read-only. I
  never imported or executed `cost_model.py`.

---

# PRE-REGISTERED DERIVATION OF THE REQUIRED LAW

**Precedence, stated as the completion gate requires: this derivation is the
standard against which I tested the producer. The producer's conclusion is not
the standard against which I tested the derivation.** It was written from
`experiments/EXP-WESOVOW-001/specification.yaml` **alone**, and committed to
disk **before** I opened `law_equivalence.md`, `reconcile.py`,
`controls_report.md`, `source_state_census.md`, `anchor_reconciliation.*`, or
`BATCH-eb0a7e/.../corrected_charging.py`. Source of the derivation: the frozen
specification, at the line numbers below, read by me.

### Lines the derivation rests on

* `specification.yaml:7-8` — title: "in the van Oorschot-Wiener middle-memory regime"
* `specification.yaml:36` — `log2M` (memory, entries), `log2T_full` (time) per field size
* `specification.yaml:38` — per `(p, w, c)`: `log2 T(w)`, speedup vs `T_DG`, crossover flag
* `specification.yaml:39-40` — analytic crossover `w* = (T_full * 2^{c*sqrt(log2 p)} / T_DG)^2, capped by M`
* `specification.yaml:70` — `log2(T_full) = log2(M) - log2(P0)`
* `specification.yaml:109-129` — the frozen grid and the `2^{c*sqrt(log2 p)}` overhead
* `specification.yaml:142-144` — C2: `log2 T_DG = log2(p)/2`
* `specification.yaml:146-147` — C3: `T(w)` non-increasing in `w`; `T(w) = T_full` for `w >= M`
* `specification.yaml:148-149` — C4: at `w = M`, vOW time equals `T_full` exactly

### Derivation

Postulate the vOW middle-memory form the title names, `T(w) = T_full * (M/w)^a`
for `w <= M`, clamped above `w = M`.

1. **C4 fixes the boundary value only.** `T(M) = T_full` holds for *any* `a`. C4
   alone therefore constrains the clamp point, not the exponent.
2. **C3 forces the clamp and the sign.** `a >= 0` gives non-increasingness below
   the cap; and for `w > M` the unclamped expression returns `T < T_full`, which
   contradicts "T(w) must equal T_full for w >= M". So the `max(0, ·)` is
   **required by the contract**, not an implementation nicety.
3. **`a = 1/2` is an import, not a spec entailment.** The contract names van
   Oorschot–Wiener but never writes the exponent. I record this as a gap in the
   frozen contract rather than pretend I derived it. (It was never in dispute:
   the pre-fix law also carries slope 0.5.)

### The required law

```
log2 T(w; p, c) = c*sqrt(log2 p) + log2 T_full(p) + max(0, (log2 M(p) - log2 w)/2)
```

### A contradiction inside the frozen contract, found before reading the producer

Solving `log2 T(w*) = log2 T_DG` under that law gives

```
log2 w* = log2 M + 2*(log2 T_full + c*sqrt(log2 p) - log2 T_DG),  capped at log2 M
```

The contract's own `specification.yaml:39-40` states the same quantity **without
the `log2 M` term**. That form is the crossover of `T(w) = T_full*2^{cs}/sqrt(w)`,
which at `w = M` gives `T_full*2^{cs}/sqrt(M)`, not `T_full*2^{cs}` — i.e. it
**violates C4 of the same file** unless `log2 M = 0`. I recorded, before opening
any producer artifact, the prediction that this is the shape of the charging-law
defect and that the corrected law is the one carrying `+ log2 M`.

**That prediction is confirmed by the committed record.** The pre-fix
`cost_model.py` computed `log2w_star = 2.0 * (log2Tfull + overhead_bits -
log2TDG)` — the `specification.yaml:39-40` form verbatim — and commit
`7d188a7c3` changed it to `log2M + 2.0 * (...)`. The frozen amendment
(`protocol_amendment.yaml:64`) carries the `log2 M` form. **`specification.yaml`
itself was never amended and still carries the defective form.** This is J1
objection 1 below.

---

# J1 — source-state census

**Verdict: `CONFIRMED WITH CAVEAT`.**

## The attack I ran

I did not accept a single producer quotation. I opened each of the five
governing artifacts at its own line numbers and read the law there myself:

| # | site | what I read at that line |
| --- | --- | --- |
| 1 | `cost_model.py:239` | `"T_w_vOW": "T(w) = T_full * sqrt(M / min(w, M))",` |
| 2 | `cost_model.py:272-275` | `overhead_bits = c * math.sqrt(b2p)` / `log2Tw = (log2Tfull + 0.5 * max(0.0, log2M - lw) + overhead_bits)` |
| 3 | `runs/RUN-WESOVOW-001/raw-result.json:13` | `"T_w_vOW": "T_full / sqrt(min(w, M))",` |
| 4 | `runs/RUN-WESOVOW-201692-001/raw-result.json:13` | `"T_w_vOW": "T(w) = T_full * sqrt(M / min(w, M))",` |
| 5 | `specification.yaml:145-149` | C3 and C4 as the census quotes them |

All five census quotations reproduce **exactly** what I read.

## Committed versus worktree — checked, not assumed

The census claims committed state, and the claim holds. I re-derived it rather
than reading the census's table:

| check | my result |
| --- | --- |
| `git hash-object experiments/EXP-WESOVOW-001/cost_model.py` | `a7ec7fd1ac4a48e7025fe8e7cfee0e46f6344b47` |
| `git rev-parse HEAD:...cost_model.py` | `a7ec7fd1…` (identical) |
| `git rev-parse origin/main:...cost_model.py` | `a7ec7fd1…` (identical) |
| `git rev-parse 5872cf99a:...cost_model.py` | `a7ec7fd1…` (identical) |
| `git rev-parse 27efe0cdc:...cost_model.py` (session `HEAD` the census names) | `a7ec7fd1…` (identical) |
| `git status --porcelain experiments/` | empty |

**A stronger binding the census did not use, which I supply.**
`sha256(cost_model.py) = 714e63667c7d31bf685ebd89d3179cb55953a9e89d611f36b96ebf4067444842`
is *equal* to `source_sha256_at_run` recorded at
`runs/RUN-WESOVOW-201692-001/manifest.yaml:31`. So the committed implementation
is not merely "a file carrying the corrected law"; it is **byte-identical to the
source that produced the successor run's receipt**. That upgrades the census's
verdict from a statement about a file to a statement about provenance of the
run, and it is checkable from committed state alone.

## Record chain — does `DEC-20260809-c1066f` admit what the census says?

Yes, and the amendment it names exists:

* `DEC-20260809-c1066f`: `decision: accept_with_caveat`;
  `snapshot_commit: 7d188a7c38e1d44b46796fe97b34fe4118628216`;
  `protocol_amendment_task: TASK-20260809-ef3e58`;
  `official_research_state_changed: false`; `hypothesis_status_transition: none`.
* `coordination/goals/GOAL-SSI-001/batches/BATCH-2e6130/tasks/TASK-20260809-ef3e58/protocol_amendment.yaml`
  exists, is tracked at `HEAD`, and at `:53-56` freezes exactly
  `T(w) = T_full * sqrt(M / min(w, M))` and
  `log2(T(w)) = log2(T_full) + 0.5*max(0, log2(M) - log2(w)) + overhead_bits`.
* `git log -1 --format=%P 7d188a7c3` → `6f8b400d8b70d0c0e36663b9365a3869f239d126`,
  which equals the successor manifest's `commit_at_run_time` (`manifest.yaml:23`).
  The chain decision → amendment → snapshot → run closes.
* `EV-SSI-4b17e7` independently states the same corrected law in its
  `observations` and records "The crossover includes log2M."

## Ancestry claims re-verified from scratch

The census's history section and `BATCH-256a94/CORRECTION-20260904-rg0-timing.md`
both survive re-checking:

| check | my result |
| --- | --- |
| `git merge-base --is-ancestor 7d188a7c3 e45861af` | non-zero |
| `git merge-base --is-ancestor 7d188a7c3 bd47a3f5c` | non-zero |
| `git merge-base --is-ancestor 7d188a7c3 origin/main` | 0 |
| `git merge-base --is-ancestor 7d188a7c3 7044fd3a5` (the `origin/main` tracking value at census time) | 0 |
| `bd47a3f5c` committer date | 2026-08-24T11:32:12−07:00 = 18:32 UTC |
| `2675886ea` committer date | 2026-08-24T20:50:28+00:00 |
| `cost_model.py:236` and `:270` at `8c5188b90` **and** at `bd47a3f5c` | `"T_w_vOW": "T_full / sqrt(min(w, M))",` and `log2Tw = log2Tfull - 0.5 * min(lw, log2M) + overhead_bits` — the exact strings the `BATCH-eb0a7e` Validator cites, at the lines it cites |
| `git ls-tree bd47a3f5c .../runs/` | `RUN-WESOVOW-001` only |

So the `BATCH-eb0a7e` team read a genuinely pre-fix revision, and the
"admitted upstream on 2026-08-09" element of the batch's
`opening_observation.leading_hypothesis` and of the Coordinator's
`coordinator_prior` is **not supported by git**. I reached that independently;
the producer reports it as AN-1/R7 and the Coordinator has since recorded the
same correction. None of this changes the `fix_already_applied` verdict.

## Concrete objections

**Objection J1-1 (substantive).** *The census's inventory of where the charging
law appears in the governing artifacts is incomplete at a named `file:line` in
the frozen contract, and its characterisation of that file is wrong.*
`source_state_census.md:108-110` states: "The specification states a
**normalisation requirement**, not a closed-form law." `specification.yaml:39-40`
states a closed form:

```
crossover memory log2(w*) per (p, overhead c), analytic: w* = (T_full * 2^{c*sqrt(log2
    p)} / T_DG)^2, capped by M
```

That is the **pre-fix** crossover — the expression commit `7d188a7c3` deleted
from `cost_model.py`. The committed implementation (`cost_model.py:288`), the
frozen amendment (`protocol_amendment.yaml:64`) and `BATCH-eb0a7e`'s
`corrected_charging.py:231-236` all carry the additional `log2 M` term. I
recomputed the gap from the committed `fitted_opt` anchors: it equals exactly
`log2 M` at every field size — `93.27781828665178`, `137.48765358816084`,
`203.30702177853001`, `268.68673590177326` bits (the `log2p = 512` value
withheld). `specification.yaml:39-40` and `specification.yaml:148-149` (C4)
cannot both hold unless `log2 M = 0`.

I searched for any prior disclosure of this and found none: not in any of the
seven producer artifacts (`grep -rn 'capped by M|analytic|specification.yaml:3[0-9]|specification.yaml:4[0-9]'`
returns nothing), not in `outstanding_fix.md`'s R1–R8, not in
`protocol_amendment.yaml`, not in `CORR-20260806-3ac71e` or
`CORR-20260808-c792f8`, not in `DEC-20260809-c1066f` or `DEC-20260824-384e78`.

This is a **sixth site** of the charging law in a governing artifact, it still
carries the defective form, and the census does not report it. It does not
overturn `fix_already_applied` — that verdict is about the implementation and
the runs, and it is correct about them — but the census's scope sentence
understates what the frozen contract contains, and a later reader who takes
`specification.yaml` as the authority on the crossover will read the defective
form. **I take no action on it; only a recorded protocol amendment and a
committed Coordinator decision can touch a frozen contract.**

**Objection J1-2 (factual, minor).** Two numbers in the census's own git
narrative do not survive re-reading:

* `source_state_census.md:179` — "Its diff to `cost_model.py` is +17/−6."
  `git show --numstat 7d188a7c3 -- .../cost_model.py` returns `11  6`. It is
  **+11/−6**. (11 + 6 = 17, which suggests added and removed were summed.)
* `source_state_census.md:238` — "Nine of the eleven files arrive in
  `7d188a7c3`." **Eight** arrive there (`command.txt`, `environment.json`,
  `execution_report.yaml`, `manifest.yaml`, `raw-result.json`,
  `runtime-session-receipt.json`, `stderr.txt`, `stdout.txt`) and three in
  `add98ba2a`; 8 + 3 = 11. The census's own "three files in `add98ba2a`"
  (`outstanding_fix.md` R6) is right, so the two statements are mutually
  inconsistent.

Neither affects the verdict. I record them because this joint asked me to test
whether the producer's quotations survive independent re-reading, and these two
do not.

**Objection J1-3 (residual, reported as undetermined).** The `origin/main` arm
of the census's committed-state table is a claim about a **local
remote-tracking ref**, whose currency depends on a `git fetch` I cannot verify
from committed state. I re-checked it against the ref as it now stands and
against the value it held at census time (`7044fd3a5`), and both agree; I did
not re-fetch. The `HEAD` and snapshot arms are fully verified and are sufficient
on their own, so this is a limitation on one arm, not a break.

## What I could not break

I looked for a quotation contradicting the census, a named committed record that
does not say what the census reports, and a conflation of worktree with
committed state. **I found none of the three.** How I searched: re-read all five
quotation sites at their own line numbers against the blob at four different
commits; opened `DEC-20260809-c1066f`, `EV-SSI-4b17e7`,
`protocol_amendment.yaml`, `CORR-20260806-3ac71e`, `CORR-20260808-c792f8` and
`DEC-20260824-384e78` myself and compared each against the census's one-line
summary in its record table; and re-ran every ancestry and hash comparison the
census reports plus four it does not.

---

# J2 — law equivalence

**Verdict: `CONFIRMED WITH CAVEAT`.**

## Result

My pre-registered law, derived from `specification.yaml` alone, is

```
log2 T(w; p, c) = c*sqrt(log2 p) + log2 T_full + max(0, (log2 M - log2 w)/2)
```

The three statements under comparison are the same function as that, and as each
other, everywhere — **including at and above the memory cap**:

| statement | site I read | form |
| --- | --- | --- |
| `L_curr` serialized | `cost_model.py:239`; `RUN-WESOVOW-201692-001/raw-result.json:13` | `T(w) = T_full * sqrt(M / min(w, M))` |
| `L_curr` executable | `cost_model.py:273-275` | `log2Tfull + 0.5*max(0.0, log2M - lw) + overhead_bits` |
| `L_eb0a7e` | `BATCH-eb0a7e/.../corrected_charging.py:56-58` | `log2_t_full + overhead_bits + 0.5*max(0.0, log2_m - log2_w)` |
| frozen amendment | `protocol_amendment.yaml:53-56` | both of the above, stated as `linear_law` and `log2_law` |

`log2M - min(log2w, log2M) = max(0, log2M - log2w)` identically, so the
serialized and executable forms coincide; the remaining two differ from `L_curr`
only in the order in which three reals are added.

## The numerical test, run in a third summation order

To avoid confirming an ordering by reusing it, I implemented my derivation as
`ov + Tf + max(0, (M - w)/2)` — **different from both** `L_curr`
(`(Tf + penalty) + ov`) and `L_eb0a7e` (`(Tf + ov) + penalty`) — and evaluated
all 240 rows under both anchors:

| comparison | max abs deviation (bits) |
| --- | --- |
| mine vs producer's `log2T_w_current_law` | `5.684341886080802e-14` |
| mine vs producer's `log2T_w_eb0a7e_law` | `5.684341886080802e-14` |
| mine vs `BATCH-eb0a7e` committed `recomputed_table.json` | **`0.0`** (240 / 240 rows) |
| mine vs producer's `log2T_w_predecessor_law` | `2.842170943040401e-14` |
| mine vs producer's `log2w_star_current_law` | `0.0` |
| mine vs `RUN-WESOVOW-201692-001` committed cells | `5.684341886080802e-14` (120 / 120) |

The `0.0` against the `BATCH-eb0a7e` table is the summation-order explanation
*predicting its own signature*: my ordering is bit-identical to `L_eb0a7e`'s and
differs from `L_curr`'s by exactly one ULP near `2^8`. `5.684341886080802e-14`
is `2^-44.0`. I reproduce the producer's counts exactly: 76 of 240 rows non-zero,
164 exactly zero.

## The boundary the Coordinator expected to break

A min/max clamp difference invisible below the cap and appearing at or above it.
**It is not there, and I tested it directly rather than by inspection.** Both
implementations use the identical `max(0.0, log2M - log2w)`. Feeding the
producer's own `rg4_cap_and_monotonicity` 2·10⁵ arbitrary anchors — `log2T_full`
and `log2M` uniform on ±10⁶, all five fields, all four `c` — the value at
`log2w = log2M` and at `log2w = log2M + 1` never departed from `log2T_full + ov`,
not once. Smallest budget at largest field (`log2w = 30`, `log2p = 768`) and
largest overhead (`c = 2.0`) both reproduce to ≤ `5.7e-14`.

## The crossover, which `law_equivalence.md` does not check

The amendment makes the crossover part of the corrected model
(`crossover.equation`, `:63-64`), and `law_equivalence.md` verifies only the
charging expression. I closed the gap myself: `cost_model.py:288`,
`protocol_amendment.yaml:64` and `corrected_charging.py:231-236` are one
expression, and it reproduces all 20 committed successor-run
`log2w_star_entries` values to **`0.0`** bits. Completeness gap in the artifact,
not an error.

## Concrete objection

**Objection J2-1 (substantive).** *"Derived independently in `BATCH-eb0a7e`"
does not survive checking as a claim of **independence**.*
`ledger/corrections/CORR-20260808-c792f8.yaml:52` already states the corrected
law verbatim —

```
T_A(P,w) = T_full(P) + 0.5*max(0, L_mem(P) - log2_w)
```

— and `:72-73` already states the corrected crossover,
`log2 w* = L_mem(P) - 2*(T_DG(P) - T_full(P))`. I checked whether that record
was visible to the `BATCH-eb0a7e` producer: `git cat-file -e
bd47a3f5c:ledger/corrections/CORR-20260808-c792f8.yaml` **succeeds**, as does
the same test for `CORR-20260806-3ac71e`. (The amendment, `EV-SSI-4b17e7`,
`DEC-20260809-c1066f` and `DEC-20260809-39eb45` were all **absent** at that
base — so `BATCH-eb0a7e` did not read those. It did not need to.)

Consequence, stated precisely: `L_curr ≡ L_eb0a7e` is agreement between **two
implementations of one already-committed written formula**, not between two
independent derivations. It is strong evidence of transcription fidelity and
weak-to-no evidence about the law's correctness. `law_equivalence.md:41` and the
handoff both describe `L_eb0a7e` as "derived independently"; a downstream reader
would be entitled to read that as corroboration, and it is not.

What *does* bear independently: my own derivation from `specification.yaml` C3
and C4, written before I opened any of these files, lands on the same function —
with the recorded caveat that the exponent `1/2` is a vOW import rather than a
spec entailment.

**Objection J2-2 (minor, sub-ULP).** Two producer figures differ from my
recomputation by one ULP, both explained by the same summation-order mechanism
the producer itself documents, neither a defect:

* `law_equivalence.md:141`, the `log2p = 576` half-`log2M` offset: artifact
  `101.65351088926502`, mine `101.65351088926501`. (The producer computed it as
  `L_curr − L_pred`; I computed `log2M / 2`.)
* `anchor_reconciliation.md:103`, third column of the `log2p = 512` row: mine
  differs by `5.7e-14`, the same ULP residue. Value withheld.

## What I could not break

I looked for a `(p, log2w, c)` cell where the two corrected laws differ by any
amount attributable to the formulas, and for an omission of the clamp region
from the producer's equality argument. **I found neither.** How I searched: full
240-row sweep in a third summation order under both anchors; direct evaluation at
`w = M` and `w = M+1` for all 5 × 4 combinations under both anchors; the two
grid corners the attack plan names; and a 2·10⁵-sample randomised search over
arbitrary anchors through the producer's own code.

---

# J3 — numerical reconciliation

**Verdict: `CONFIRMED`.**

## Sampling rule, stated

**I did not sample. I recomputed all 240 rows** and every reported quantity in
each of them, from committed literals I parsed myself — `PAPER_PAIRS` by my own
text parse of `cost_model.py:60-65`; `fitted_opt` from
`RUN-WESOVOW-001/raw-result.json` `per_field[*].optimal.log2T,.log2M` — using my
own law in my own summation order. On top of the full sweep I called out seven
**adversarially chosen** rows individually, exactly as the attack plan directs:
the largest law-vs-law residue; the smallest **non-zero** residue; a row the
producer reports as agreeing exactly; the tightest `|speedup vs DG|` margin
outside `log2p = 512`; the tightest overlap row; and both extreme grid corners
(`fitted_opt`, `p = 768`, `w = 2^30`, `c = 2.0`; `PAPER_PAIRS`, `p = 768`,
`w = 2^80`, `c = 0`).

## Structural checks

| check | result |
| --- | --- |
| declared `row_count` vs actual | 240 vs 240 |
| rows per anchor | 120 `fitted_opt`, 120 `PAPER_PAIRS` |
| missing grid cells | none, either anchor |
| duplicated grid keys `(anchor, p, w, c)` | none |
| extra cells outside the frozen grid | none |
| **mixed-anchor rows** | **zero.** For all 240 rows, `log2T_full_anchor` **and** `log2M_anchor` are both exactly equal (float equality) to the committed pair of that row's own named anchor, and `anchor_source_time_and_memory` names the matching file. |
| `citation_prohibited` flag | 48 rows, exactly and only the `log2p = 512` rows |

## Independent recomputation

| quantity | max \|mine − producer\| (bits) |
| --- | --- |
| `log2T_w_current_law` | `5.684341886080802e-14` |
| `log2T_w_eb0a7e_law` | `5.684341886080802e-14` |
| `log2T_w_predecessor_law` | `2.842170943040401e-14` |
| `overhead_bits` | `0.0` |
| `log2w_star_current_law` | `0.0` |
| `log2speedup_vs_DG_current_law` | `5.684341886080802e-14` |

**Pass-through fidelity — the thing this joint was told to suspect.** I asserted,
row by row, that every `eb0a7e_recomputed_table_value` is float-equal to the
corresponding row of the committed `BATCH-eb0a7e/.../recomputed_table.json`
(240/240 pass), and that every `RUN_WESOVOW_201692_001_log2T_w` is float-equal to
the committed successor cell at
`per_field[log2p=p].van_oorschot_wiener[w=2^w][c=c].log2T_w` (120/120 pass). The
comparison against `RUN-WESOVOW-201692-001` reads **committed run output**, not
the producer's own recomputation. The suspected substitution is not present.

**No tolerance inflation.** Declared tolerances are `REPRO_TOL = 1e-9` (fixed by
the task card) and `EQ_TOL = 1e-12`. Observed residues are ≤ `5.7e-14`, about
18× below the tighter tolerance and four orders below the looser. Nothing was
widened to accommodate a result; I verified the 1e-9 gate is live by tripping it
(J5 below).

**Deviation tables re-derived.** `anchor_reconciliation.md:101-105` reproduces
exactly from the committed literals at four of five field sizes, with one
sub-ULP difference at `log2p = 512` (value withheld). The census's five
`0.5*log2M` deficits reproduce exactly at four of five, with the one-ULP
difference at `log2p = 576` noted under J2-2.

## Concrete objection

**Objection J3-1.** *The 120 "overlap" comparisons are not an additional check;
they are RG-2 reported a second time.* `build_rows` anchors `fitted_opt` on the
**predecessor** run's `optimal` values while comparing against the **successor**
run's cells. That is legitimate only because the two `optimal` sets are exactly
equal — which I verified independently by exact float equality at all five field
sizes, so the row construction is sound. But given that equality,
`recomputed_minus_run_bits` evaluates the *same function on the same arguments*
as RG-2's `reproduction_gate(raw_succ, fitted_succ, law_curr, …)`. The `0.0` at
all 120 overlapping rows (`anchor_reconciliation.md:66`, "What this
reconciliation settles" item 3) and RG-2's `max_abs_diff_bits: 0.0`
(`controls_report.md:90`) are **one measurement presented in two artifacts as if
they were two**.

Two riders. First, the `0.0` is weaker than it reads: it is bit-exact only
because `reconcile.py`'s `law_curr` reproduces `cost_model.py:273-275`'s
association order character for character; my re-ordering shows the underlying
real-number agreement is ULP-level (`≤ 5.7e-14`), not exact by mathematical
necessity. Second, and to the producer's credit, the corresponding **absence**
is handled correctly and explicitly: `PAPER_PAIRS` overlaps no committed run
cell, and `anchor_reconciliation.md:82-87` states that as "a **stated absence of
overlap** — neither agreement nor disagreement", rather than letting a `null`
read as a pass.

## What I could not break

I looked for a row whose independently recomputed value exceeds the declared
tolerance, a missing or duplicated grid cell, and a mixed-anchor row. **I found
none of the three**, on a full 240-row sweep rather than a sample.

---

# J5 — control capability

**Verdict: `REFUTED`, narrowly and specifically: RG-4 has no reachable failure
branch on any real anchor, and three of its arms are reported as carrying
information when all three are algebraically entailed. RG-0, RG-1, RG-2 and RG-3
are each capable of failing, and I demonstrated the branch for each.**

## Method

Rather than reasoning about the controls, I imported `reconcile.py` as a module
(its `main()` guarded by `__name__` and never executed; nothing written outside
my scratchpad) and **fed the producer's own control functions inputs designed to
make them fail**, checking that the implementation actually takes the failure
branch.

## Per-control capability assessment

| control | concrete input that makes it fail | did the producer's implementation take that branch? |
| --- | --- | --- |
| **RG-0** | `git hash-object cost_model.py` differing from `git rev-parse HEAD:…` → the corrected law would be a worktree fact, not a committed one, and no verdict about committed state could be named. Or `cost_model.py:239` holding `"T_full / sqrt(min(w, M))"` → `fix_outstanding`. | **Yes.** I ran the hash comparison myself (equal at worktree/`HEAD`/`origin/main`/snapshot), and confirmed the discriminating branch is real: the pre-fix blob at `8c5188b90` and at `bd47a3f5c` holds exactly the `fix_outstanding` string at `:236` and its executable at `:270`. Both branches distinguishable. |
| **RG-1** | Feed `L_curr` to the predecessor run. | **Yes** — `status: FAIL`, `mismatch_count: 120`, `max_abs_diff_bits 134.34336795088666`. Exercised by the producer as `proves_too_much` object 3 and re-run by me. |
| **RG-2** | (a) perturb one committed cell by `+2e-9` bits; (b) delete one budget row. | **Yes, both, verified by me.** (a) `log2p=384, w=2^50, c=1.0` perturbed by `+2e-9` → `FAIL`, `mismatch_count: 1` — the `1e-9` gate is live, not decorative. (b) deleting `log2p=576, w=2^70` → `FAIL`, `cells_checked: 116` of 120. |
| **RG-3** | An anchor with `log2M = 0` presented as a *real* anchor — the procedure would then be blind to a difference where one is claimed to exist. | **Yes** — `status: FAIL`, `all_real_rows_discriminate: false`, `min_abs_separation_bits: 0.0`. |
| **RG-4** | **None on any real anchor.** See below. | The only input that flips any arm is the degenerate `log2M = 0` anchor, which makes `predecessor_law_violates_cap_everywhere` go false → `FAIL`. Verified by me. |

## RG-3 and the inventor-protocol artifact tell — credit where due

The separation the package reports between the two laws is a constant
`0.5*log2M`. The parameter that must destroy it is `log2M → 0`. **The producer
measures that decay rather than asserting it**: the synthetic `log2M = 0`
object is evaluated, both laws collapse to `log2T_full`, and the procedure
reports no difference. That is a null object of the same shape, run through the
identical measurement, with the required "what should this quantity do as the
destroying parameter increases" answered by computation. The producer also
records the correct limitation: the smallest real-anchor separation is 46.25
bits, so the control demonstrates sensitivity to a large difference only, not to
a small one. I re-ran both arms and reproduce both results.

## Why RG-4 is refuted

`controls_report.md:177-189` states: *"What in RG-4 is **not** entailed by
`L_curr`, and therefore does carry information: 1. The predecessor-law arm.
2. Monotonicity across the memory grid … not a tautology of the `max(0, ·)`
clamp at one argument. 3. The `log2w = log2M + 1` row …"*

**All three items are entailed.**

1. *Predecessor-law arm.* `L_pred` at `w = M` gives `Tf - 0.5*log2M + ov`; the
   test is `|−0.5·log2M| > 1e-12`, i.e. `log2M ≠ 0`. Entailed for every real
   anchor. I confirmed it flips **only** on the degenerate `log2M = 0` anchor.
2. *Monotonicity.* `max(0, M − w)` is non-increasing in `w` for **every** `M`.
   This is an identity about the function, not a contingent property of the
   numbers. I ran 2·10⁵ arbitrary anchors (`log2T_full`, `log2M` uniform on
   ±10⁶, including negative and 10⁶-magnitude values, all fields, all `c`)
   through the producer's own `rg4_cap_and_monotonicity`: **the monotonicity arm
   never failed once, and neither did the cap arm.**
3. *The `log2w = log2M + 1` row.* This is the **same** identity as the cap arm —
   `max(0, negative) = 0` at a shifted argument — listed as a separate
   non-entailed item.

The producer's stated failing inputs for these arms
(`controls_report.md:191-196`) are **mutations of the law in the code**
("Substituting a penalty of `-0.5*max(0, log2M - log2w)` makes the monotonicity
arm fail"), not inputs to the control. That tests `reconcile.py`'s transcription
of `law_curr`, which is real but is a much weaker thing than a control on the
committed artifacts, and it is not what "does carry information" conveys.

**Does RG-4's cap identity get entailed by the law under test?** *Yes* — and the
producer says so, correctly and prominently: `controls_report.md:162-167`, "the
cap arm of RG-4 **cannot fail for `L_curr`** and its pass is a restatement of the
law, **not independent confirmation**". Its citation of the `BATCH-eb0a7e`
Validator's matching caveat is accurate; I read
`BATCH-eb0a7e/reviews/TASK-20260824-5b150a/validation_report.md:160-164` myself
and it says what the producer quotes it as saying. That prior Validator also
named the degenerate `log2M = 0` input as its own control's only concrete
failure — independently consistent with what I found here.

So the disclosure is **partial**: honest and correct on the arm it addresses,
and wrong on the three arms it exempts. `RG-4` as run has **no reachable failure
branch on any anchor either run package supplies**. That is precisely the
breaking artifact this joint declared: *"a control with no reachable failure
branch, or a passing control whose pass is entailed by the law under test and was
reported as confirmation."*

**Scope of the refutation, stated so it cannot be over-read.** No number in the
package is wrong because of this. RG-4's computed values are correct and I
reproduce them. What does not survive is the claim about **what RG-4's pass
establishes**. RG-0, RG-1, RG-2 and RG-3 remain capable of failing, on inputs I
constructed and ran.

## A latent fragility, recorded but not a finding

`reconcile.py:285` builds the monotonicity sequence as
`list(MEMORY_BUDGETS) + [M, M + 1.0]`, which is sorted only if `log2M > 80`. The
minimum `log2M` across both anchors is `92.5`, so the sequence is sorted here. I
checked the failure mode anyway: with `log2M < 80` the sequence would still be
non-increasing because of the clamp, so the check would not silently pass a
violation. No defect.

---

# Per-deliverable table

| deliverable | present at declared path | snapshot-bound | my finding |
| --- | --- | --- | --- |
| `source_state_census.md` | yes | sha256 matches receipt, `HEAD`, snapshot | Verdict `fix_already_applied` is correct and is a claim about committed state. Two git miscounts (J1-2); one substantive omission at `specification.yaml:39-40` and one false generalisation at `:108-110` (J1-1). |
| `law_equivalence.md` | yes | matches | Equivalence result is correct and reproduces in a third summation order. Does not check the crossover (I did; it holds). "Derived independently" overstated (J2-1); two sub-ULP figures (J2-2). |
| `reconcile.py` | yes | matches | Standalone, stdlib-only, no import from `experiments/`, controls implemented as reachable branches — except RG-4, whose branches are unreachable on real anchors (J5). |
| `anchor_reconciliation.json` | yes | matches | 240 rows, full grid both anchors, no duplicates, no mixed-anchor rows, every value recomputes from committed literals to ≤ `5.7e-14` bits. Pass-through values byte/float-faithful to their committed sources (360 assertions). |
| `anchor_reconciliation.md` | yes | matches | Faithful to the JSON. Overlap/absence-of-overlap handled correctly. Duplicate reporting of RG-2 as an independent comparison (J3-1). |
| `controls_report.md` | yes | matches | RG-0…RG-3 capability assessments are correct and I re-ran each failure branch. RG-4 non-entailment claim at `:177-189` refuted (J5). |
| `outstanding_fix.md` | yes | matches | R1–R8 are each supported at the `file:line` given. The `specification.yaml:39-40` residual is missing from the list (J1-1). Nothing was applied, staged or committed — I verified this against git independently. |

# Limitations of this review

1. **I own four joints of six.** J4 (anchor reconciliation and citation
   eligibility) and J6 (scope and provenance of the fix-status verdict) belong to
   `TASK-20260904-22e444` and are invisible to me. Nothing here is a whole-claim
   verdict.
2. **Provenance of neither run is attested by anything I checked.** Both
   manifests record `dirty_tree: true` (`RUN-WESOVOW-001/manifest.yaml:19`,
   `RUN-WESOVOW-201692-001/manifest.yaml:24`). I did not re-execute
   `cost_model.py` and am not authorised to. What I *can* bind is stronger than
   the producer claimed but still not execution provenance:
   `sha256(cost_model.py)` equals the successor manifest's
   `source_sha256_at_run`, so the committed bytes are the bytes that manifest
   names — not proof that the recorded command produced the recorded output.
3. **RG-1/RG-2 and my reproduction of them check derived cells against
   primitive anchors from the same file.** Neither reproduces `optimal.log2T`,
   `optimal.log2M`, the Dickman `ρ` machinery, the `B` optimizer, the paper-pair
   transcription, or the byte conversions. A "0.0-bit agreement between an
   implementation and its own output" establishes that the 120 cells are the
   stated closed form applied to that file's own anchors — arithmetic
   self-consistency — and establishes **nothing** about whether those anchors,
   or the law, are right.
4. **The `1/2` exponent is not derivable from the frozen contract.** My
   derivation imports it from van Oorschot–Wiener. C3 and C4 fix the clamp and
   the normalisation, which is the whole content of the repaired defect, but a
   contract that never writes its own exponent is a gap I am reporting, not
   closing.
5. **Model verification is undetermined.** No `adapter env` receipt binds this
   session's resolved model to the requested `review-adversarial` policy, and I
   ran no probe. Recorded as `model_verified: false`.
6. **The producer package records no resolved-model provenance.** Its seven
   declared artifacts include no runtime-session receipt; `source_state_census.md:4-5`
   self-reports the *requested* policy only. AGENTS.md's artifact policy asks for
   the resolved runtime model identifier and its probe-verification status. The
   task card did not require one, so this is a contract gap rather than a
   producer failure — but it means the producer's inference provenance is
   undetermined from committed state.
7. **The `origin/main` arm of the census is verified only against a local
   remote-tracking ref**, whose currency I cannot establish from committed state.
8. **One producer quotation I did not re-verify at its source**: none. Every
   quotation I relied on was re-read at its own `file:line`, including the
   `BATCH-eb0a7e` Validator caveat the producer cites.
9. **Budget.** Wall clock and memory well inside 3600 s / 2 GB; **2 of at most 2
   runs used** (one full recomputation sweep with the control-capability probes,
   one short arithmetic check of the deviation tables). No timeout, crash, or
   resource exhaustion occurred. Had one occurred it would be an operational
   observation and never mathematical evidence.

# Things I treated as inadmissible, and did not use

* `BATCH-256a94/batch.yaml` → `opening_observation`. I read it and treated it as
  an **unverified Coordinator hypothesis**. It supports no verdict of mine. Where
  it was checkable I checked it independently, and its
  `leading_hypothesis` timing element ("admitted upstream on 2026-08-09") is
  **not supported by git** — the same element appears in the review plan's
  `coordinator_prior`, and is likewise unsupported there.
* The Coordinator's `coordinator_prior` on `TASK-20260904-1f4e2f`. I read it
  because the review plan lives on that card, and my findings agree with parts of
  it. That agreement is not evidence; I reached each verdict from artifacts I
  opened myself, and the one element of the prior I could test against git turned
  out to be wrong.
* Anything under
  `coordination/goals/GOAL-SSI-001/batches/BATCH-256a94/reviews/TASK-20260904-22e444`.
  **Never read, never listed, never grepped.** My batch-tree listing used
  `-prune` on that path. I did not encounter it.

---

```yaml
validation_report:
  id: VAL-20260904-e13cf2
  task_id: TASK-20260904-e13cf2
  goal_id: GOAL-SSI-001
  batch_id: BATCH-256a94
  package_under_review: coordination/goals/GOAL-SSI-001/batches/BATCH-256a94/tasks/TASK-20260904-1f4e2f
  snapshot_commit: 5872cf99a2e71c0455502244047ad3c2f019ccbc
  snapshot_receipt: coordination/goals/GOAL-SSI-001/batches/BATCH-256a94/archives/TASK-20260904-47c3ea/snapshot_commit_receipt.json
  run_ids: []
  run_id_note: >-
    This review validates a task-report package, not an experiment run. It reads
    two frozen run packages as inputs: RUN-WESOVOW-001 and
    RUN-WESOVOW-201692-001. Neither was executed, re-executed, or modified.

  inference:
    requested_policy: review-adversarial
    requested_reasoning_effort: xhigh
    fallback_allowed: false
    degraded_allowed: false
    independent_session_required: true
    served_by_runtime: claude_code
    served_by_agent: .claude/agents/validator.md
    resolved_model_id: claude-opus-5
    resolved_model_id_source: runtime self-report; no adapter env receipt in this session
    fallback_used: false
    degraded_requirements: []
    model_verified: false
    model_verified_note: >-
      AUTORESEARCH_POLICY and AUTORESEARCH_BACKEND are unset; no
      `orchestration.adapter doctor --probe` was run. Recorded as undetermined,
      not asserted.
    independent_session: true
    bedrock_used: false

  artifact_checks:
    - id: AC-1
      check: all seven declared producer artifacts exist at their declared paths
      result: pass
      detail: seven files, no eighth; task_card.yaml predates the producer (commit 7c8bf37cd)
    - id: AC-2
      check: worktree sha256 == snapshot-commit sha256 == HEAD sha256 == receipt source_path_sha256
      result: pass
      detail: 7 of 7 identical; also identical at c1a39ee5a
    - id: AC-3
      check: snapshot commit exists and is reachable from HEAD
      result: pass
      detail: 5872cf99a2e71c0455502244047ad3c2f019ccbc, ancestor of HEAD 33407648c
    - id: AC-4
      check: archive receipt completeness
      result: pass_with_note
      detail: >-
        commit_sha is null and verification.status is pending_post_commit; the
        receipt binds by content and the content binding verifies exactly. The
        release receipt TASK-20260904-1f4e2f.1.release.json carries an empty
        artifact_sha256 map, so it binds nothing; the snapshot receipt does.
    - id: AC-5
      check: no file under experiments/ modified, moved, or staged by this batch
      result: pass
      detail: >-
        no commit since 2026-09-01 touches experiments/EXP-WESOVOW-001;
        git diff 1f6fe9b4e^..HEAD -- experiments/ is empty; worktree clean under
        experiments/. Last content change to the experiment was 7d188a7c3
        (2026-08-08) and add98ba2a (2026-08-24).
    - id: AC-6
      check: committed cost_model.py bytes bind to the successor run's manifest
      result: pass
      detail: >-
        sha256 714e63667c7d31bf685ebd89d3179cb55953a9e89d611f36b96ebf4067444842
        equals source_sha256_at_run at RUN-WESOVOW-201692-001/manifest.yaml:31
    - id: AC-7
      check: cost_model.py blob identity across worktree, HEAD, origin/main, snapshot, census-time HEAD
      result: pass
      detail: a7ec7fd1ac4a48e7025fe8e7cfee0e46f6344b47 at all five
    - id: AC-8
      check: decision -> amendment -> snapshot -> run chain closes
      result: pass
      detail: >-
        DEC-20260809-c1066f names protocol_amendment_task TASK-20260809-ef3e58
        (file exists, tracked at HEAD) and snapshot_commit 7d188a7c3, whose
        parent 6f8b400d8 equals the successor manifest's commit_at_run_time
    - id: AC-9
      check: run-record provenance attestation
      result: incomplete
      detail: >-
        both run manifests record dirty_tree: true; neither run's execution
        provenance is attested by anything in this package or by me
    - id: AC-10
      check: producer inference provenance recorded
      result: incomplete
      detail: >-
        no runtime-session receipt among the seven artifacts; requested policy is
        self-reported at source_state_census.md:4-5; resolved model identifier and
        probe status undetermined. The task card did not require one.
    - id: AC-11
      check: citation provenance of the package's references
      result: pass
      detail: >-
        every reference I checked resolves to a committed record read at its own
        file:line; no `recalled` reference is doing load-bearing work

  metric_recomputations:
    - id: MR-1
      quantity: log2 T(w) over the full frozen grid, both anchors (240 rows)
      method: >-
        independent implementation of a law derived from specification.yaml C3/C4
        before reading any producer artifact, written in a third summation order
        distinct from both implementations under comparison
      max_abs_deviation_bits: 5.684341886080802e-14
      result: pass
    - id: MR-2
      quantity: log2 T(w) vs BATCH-eb0a7e committed recomputed_table.json (240 rows)
      max_abs_deviation_bits: 0.0
      result: pass
    - id: MR-3
      quantity: log2 T(w) vs RUN-WESOVOW-201692-001 committed cells (120 overlap rows)
      max_abs_deviation_bits: 5.684341886080802e-14
      result: pass
    - id: MR-4
      quantity: analytic crossover log2 w* (20 cells, successor run)
      max_abs_deviation_bits: 0.0
      result: pass
      note: not checked by law_equivalence.md; closed by me
    - id: MR-5
      quantity: RG-1 and RG-2 reproduction gates recomputed from scratch
      result: pass
      detail: >-
        RG-1 120/120 cells, max 1.4210854715202004e-14 bits; RG-2 120/120 cells,
        max 5.684341886080802e-14 bits, under my summation order
    - id: MR-6
      quantity: predecessor-vs-current law offset (0.5*log2M) per field
      result: pass
      detail: >-
        exact at four of five fields; one ULP difference at log2p=576
        (mine 101.65351088926501, artifact 101.65351088926502)
    - id: MR-7
      quantity: anchor divergence table (anchor_reconciliation.md:101-105)
      result: pass
      detail: exact at four of five fields; one sub-ULP difference at log2p=512
    - id: MR-8
      quantity: pass-through fidelity of quoted committed values
      result: pass
      detail: >-
        240/240 eb0a7e table values and 120/120 successor-run cell values are
        float-equal to their committed sources (asserted row by row)
    - id: MR-9
      quantity: grid structure
      result: pass
      detail: 240 rows, 120 per anchor, zero missing, zero duplicated, zero mixed-anchor
    - id: MR-10
      quantity: specification.yaml:39-40 crossover vs cost_model.py:288 crossover
      result: discrepancy_found
      detail: >-
        differ by exactly log2 M at every field size. specification.yaml:39-40 is
        the pre-fix form and is inconsistent with C4 of the same file unless
        log2 M = 0. Undisclosed anywhere in the package or the governing records.

  control_checks:
    - control: RG-0
      verdict_reported: fix_already_applied
      capable_of_failing: true
      failing_input: >-
        worktree blob differing from HEAD blob (would force indeterminate), or
        cost_model.py:239 holding "T_full / sqrt(min(w, M))" (would force
        fix_outstanding)
      branch_verified_by_validator: >-
        hash comparison re-run by me and equal at all four refs; the
        fix_outstanding string verified present at 8c5188b90:236 and bd47a3f5c:236
    - control: RG-1
      verdict_reported: PASS
      capable_of_failing: true
      failing_input: predecessor run evaluated under L_curr
      branch_verified_by_validator: FAIL, 120 mismatches, max 134.34336795088666 bits
    - control: RG-2
      verdict_reported: PASS
      capable_of_failing: true
      failing_input: >-
        one committed cell perturbed by +2e-9 bits; or one budget row deleted
      branch_verified_by_validator: >-
        FAIL with mismatch_count 1 (1e-9 gate is live); FAIL with 116 of 120 cells
    - control: RG-3
      verdict_reported: PASS
      capable_of_failing: true
      failing_input: a log2M = 0 anchor presented as a real anchor
      branch_verified_by_validator: FAIL, all_real_rows_discriminate false, min separation 0.0
      null_object_control: >-
        present and correct. The reported separation is 0.5*log2M; the parameter
        that must destroy it (log2M -> 0) does destroy it, and the producer
        measures that decay rather than asserting it.
    - control: RG-4
      verdict_reported: PASS (both anchors)
      capable_of_failing: false
      cap_identity_entailed_by_law_under_test: true
      entailment_disclosed_by_producer: partial
      finding: >-
        Every arm is algebraically entailed given only log2M > 0. The producer
        discloses this correctly for the cap arm (controls_report.md:162-167) but
        asserts at :177-189 that the predecessor-law arm, monotonicity, and the
        w = M+1 row are NOT entailed and "therefore do carry information". All
        three are entailed: max(0, M-w) is non-increasing in w for every M; the
        w = M+1 row is the same max(0, negative) = 0 identity as the cap; and the
        predecessor arm flips only on the degenerate log2M = 0 anchor. A random
        search of 2e5 arbitrary anchors through the producer's own
        rg4_cap_and_monotonicity never failed either arm.
      failing_input: >-
        none on any real anchor. The only input that flips any arm is log2M = 0,
        which makes predecessor_law_violates_cap_everywhere false and RG-4 FAIL.
    - control: proves_too_much
      note: >-
        assigned to TASK-20260904-22e444 and not adjudicated here. Touched only
        where object 3 demonstrates RG-1/RG-2's reachable failure branch, which
        is within J5.

  heuristic_validation_checks:
    - check: pre-registered prediction
      result: satisfied_by_this_review
      detail: >-
        the required law was derived from specification.yaml alone and written to
        disk before any producer artifact was opened; the derivation predicted the
        specification.yaml:39-40 / C4 contradiction before it was observed
    - check: sample integrity
      result: not_applicable
      detail: no sampling occurred; this package is arithmetic on committed literals
    - check: correspondence validity
      result: not_applicable
      detail: no substitute sampler is used
    - check: scale binding
      result: satisfied
      detail: >-
        all conclusions are scoped to log2 p in {256,384,512,576,768}, log2 w in
        {30..80}, c in {0.0,0.5,1.0,2.0}, this cost model, and these two anchors.
        The producer states the scope; no transfer is claimed and none is
        admissible from this package.

  cost_model_checks:
    - check: declared unit
      result: pass
      detail: >-
        F_{p^2}-operations for time, table entries for memory
        (specification.yaml:71-73, cost_model.py:232-233); all quantities log2
    - check: memory reported alongside time
      result: pass
      detail: >-
        every row carries log2M_anchor beside log2T_full_anchor, and byte
        conversions at 64 and 256 bytes/entry exist in both run packages
    - check: optimistic assumptions flagged
      result: pass_with_note
      detail: >-
        the paper's "1 op per table entry" convention is declared at
        specification.yaml:71 and carried into the honesty_constraints at :158-159
    - check: total expected cost as per-attempt cost x inverse success probability
      result: pass
      detail: >-
        log2 T_full = log2 M - log2 P0 (specification.yaml:70, cost_model.py:176)
        is exactly per-attempt cost times inverse success probability, with P0 the
        stated heuristic success probability; it is not computed as if success
        were certain
    - check: anchor divergence honestly localised
      result: pass
      detail: >-
        localised to the anchor inputs, not the formula; the producer states
        explicitly that the reconciliation does not choose an anchor and cannot.
        Which anchor is citable is J4's question, not mine.

  proof_architecture_checks:
    - check: baseline fixture
      result: pass
      detail: >-
        the predecessor law is reproduced exactly from the predecessor run's own
        committed anchors; the pre-fix source revision is located at a named
        commit and its two lines reproduce the BATCH-eb0a7e citation verbatim
    - check: strictness witness
      result: not_applicable
      detail: no improvement claim is made by this package
    - check: interface preservation
      result: pass
      detail: >-
        the representation change from law to log2 law records its own identity
        (log2M - min(log2w, log2M) = max(0, log2M - log2w)), which I verified
    - check: ceiling and nearby control
      result: partial
      detail: >-
        the nearby object (the degenerate log2M = 0 anchor) is run, and it is the
        object on which RG-4's only reachable failure lives

  verdict: incomplete

  verdict_rationale: >-
    The package is admissible as a committed, content-verified snapshot, and
    three of my four joints hold: the census is a claim about committed state and
    survives independent re-reading (J1, with caveats), the three corrected
    charging laws are one function including at and above the cap (J2, with a
    caveat on what that agreement is evidence for), and the 240-row reconciliation
    recomputes from committed literals with no missing, duplicated, or
    mixed-anchor row and no tolerance inflation (J3). J5 is refuted: RG-4 has no
    reachable failure branch on any real anchor and its non-entailment claim does
    not survive checking. Two items were also found that the package does not
    disclose: specification.yaml:39-40 still carries the pre-fix crossover, which
    contradicts C4 of the same file; and the "independently derived" status of the
    BATCH-eb0a7e law does not hold, because the corrected formula was already
    committed at that batch's own base. `incomplete` rather than `passed` because
    a control that cannot fail was reported as carrying information and one
    governing artifact still carries the defective law unreported; `incomplete`
    rather than `failed` because no computed value in the package is wrong, every
    number I could recompute recomputes, and the RG-0 verdict itself stands. This
    verdict admits the receipt's arithmetic as checkable evidence. It supports no
    SSI or ECDLP claim, demonstrates no speedup, and authorises no promotion.

  limitations:
    - I own J1, J2, J3, J5 only; J4 and J6 are invisible to me and this is not a whole-claim verdict.
    - Neither run's execution provenance is attested; both manifests record dirty_tree true.
    - RG-1/RG-2 and my reproduction of them check derived cells against primitive anchors from the same file; the optimal anchors, the Dickman machinery, the B optimizer and the paper-pair transcription are read as inputs and are not reproduced by anyone.
    - A 0.0-bit agreement between an implementation and its own output establishes arithmetic self-consistency and nothing about the correctness of the anchors or of the law.
    - The exponent 1/2 in the required law is an import from van Oorschot-Wiener, not an entailment of the frozen contract, which never writes it.
    - This session's resolved model is not probe-verified; model_verified is false.
    - The producer package records no resolved-model provenance; its inference provenance is undetermined from committed state.
    - The origin/main arm of the census rests on a local remote-tracking ref whose currency is not establishable from committed state.
    - No security, standardized-parameter, exponent, or asymptotic-complexity claim is made or supported in any direction.
    - The P=512 crossover value and the w=2^80 sign are not citation-eligible; this report does not lift that prohibition, makes no recommendation to lift it, and withholds every substantive log2p=512 value as a precaution.

  artifact_paths:
    - coordination/goals/GOAL-SSI-001/batches/BATCH-256a94/reviews/TASK-20260904-e13cf2/validation_report.md
```

---

```yaml
review_attestation:
  task_id: TASK-20260904-e13cf2
  role: validator
  round: BATCH-256a94 review of TASK-20260904-1f4e2f
  review_plan_defined_on: TASK-20260904-1f4e2f
  independent_session: true
  joints_owned:
    - J1 source-state census
    - J2 law equivalence
    - J3 numerical reconciliation
    - J5 control capability
  joint_verdicts:
    J1 source-state census: CONFIRMED WITH CAVEAT
    J2 law equivalence: CONFIRMED WITH CAVEAT
    J3 numerical reconciliation: CONFIRMED
    J5 control capability: REFUTED
  read_sibling_reports: false
  sibling_report_encountered: false
  sibling_report_path_excluded: coordination/goals/GOAL-SSI-001/batches/BATCH-256a94/reviews/TASK-20260904-22e444
  blindness_note: >-
    I never read, opened, listed or grepped anything under the sibling review
    path. My batch-tree listing used `-prune` on it. I formed every finding from
    the producer package, the frozen experiment, the committed ledger records and
    git objects.
  blind_rederivation_required_of_me: false
  blind_rederivation_note: >-
    The plan's blind_rederivation block is assigned to TASK-20260904-22e444, not
    to me, so its blind_from list does not bind this task. My own J2 constraint
    -- derive the required law from specification.yaml alone and record it before
    opening law_equivalence.md -- was honoured: the derivation was written to
    disk before I opened any producer artifact, and it is reproduced verbatim in
    this report.
  sources_read:
    - AGENTS.md
    - agents/validator.md
    - coordination/goals/GOAL-SSI-001/batches/BATCH-256a94/tasks/TASK-20260904-e13cf2/task_card.yaml
    - ledger/handoffs/TASK-20260904-e13cf2.yaml
    - coordination/goals/GOAL-SSI-001/batches/BATCH-256a94/tasks/TASK-20260904-1f4e2f/task_card.yaml
    - coordination/goals/GOAL-SSI-001/batches/BATCH-256a94/batch.yaml
    - coordination/goals/GOAL-SSI-001/batches/BATCH-256a94/CORRECTION-20260904-rg0-timing.md
    - coordination/goals/GOAL-SSI-001/batches/BATCH-256a94/archives/TASK-20260904-47c3ea/snapshot_commit_receipt.json
    - coordination/goals/GOAL-SSI-001/batches/BATCH-256a94/claims/TASK-20260904-1f4e2f.1.release.json
    - coordination/goals/GOAL-SSI-001/batches/BATCH-256a94/claims/TASK-20260904-e13cf2.1.claim.json
    - coordination/goals/GOAL-SSI-001/batches/BATCH-256a94/tasks/TASK-20260904-1f4e2f/source_state_census.md
    - coordination/goals/GOAL-SSI-001/batches/BATCH-256a94/tasks/TASK-20260904-1f4e2f/law_equivalence.md
    - coordination/goals/GOAL-SSI-001/batches/BATCH-256a94/tasks/TASK-20260904-1f4e2f/reconcile.py
    - coordination/goals/GOAL-SSI-001/batches/BATCH-256a94/tasks/TASK-20260904-1f4e2f/anchor_reconciliation.json
    - coordination/goals/GOAL-SSI-001/batches/BATCH-256a94/tasks/TASK-20260904-1f4e2f/anchor_reconciliation.md
    - coordination/goals/GOAL-SSI-001/batches/BATCH-256a94/tasks/TASK-20260904-1f4e2f/controls_report.md
    - coordination/goals/GOAL-SSI-001/batches/BATCH-256a94/tasks/TASK-20260904-1f4e2f/outstanding_fix.md
    - experiments/EXP-WESOVOW-001/specification.yaml
    - experiments/EXP-WESOVOW-001/cost_model.py
    - experiments/EXP-WESOVOW-001/runs/RUN-WESOVOW-001/manifest.yaml
    - experiments/EXP-WESOVOW-001/runs/RUN-WESOVOW-001/raw-result.json
    - experiments/EXP-WESOVOW-001/runs/RUN-WESOVOW-201692-001/manifest.yaml
    - experiments/EXP-WESOVOW-001/runs/RUN-WESOVOW-201692-001/raw-result.json
    - experiments/EXP-WESOVOW-001/runs/RUN-WESOVOW-201692-001/command.txt
    - experiments/EXP-WESOVOW-001/runs/RUN-WESOVOW-201692-001/environment.json
    - experiments/EXP-WESOVOW-001/runs/RUN-WESOVOW-201692-001/execution_report.yaml
    - coordination/goals/GOAL-SSI-001/batches/BATCH-2e6130/tasks/TASK-20260809-ef3e58/protocol_amendment.yaml
    - coordination/goals/GOAL-SSI-001/batches/BATCH-eb0a7e/tasks/TASK-20260824-dd5b5c/corrected_charging.py
    - coordination/goals/GOAL-SSI-001/batches/BATCH-eb0a7e/tasks/TASK-20260824-dd5b5c/recomputed_table.json
    - coordination/goals/GOAL-SSI-001/batches/BATCH-eb0a7e/task-cards/TASK-20260824-dd5b5c.md
    - coordination/goals/GOAL-SSI-001/batches/BATCH-eb0a7e/reviews/TASK-20260824-5b150a/validation_report.md
    - ledger/decisions/DEC-20260809-c1066f.yaml
    - ledger/decisions/DEC-20260824-384e78.yaml
    - ledger/evidence/EV-SSI-4b17e7.yaml
    - ledger/corrections/CORR-20260806-3ac71e.yaml
    - ledger/corrections/CORR-20260808-c792f8.yaml
    - orchestration/roles.yaml
    - orchestration/model-policies.yaml
    - .claude/agents/validator.md
    - git objects: commits 33407648c, 5872cf99a, 26a8d6061, 45d5986e2, c1a39ee5a, 19f3a222b, 27efe0cdc, 1f6fe9b4e, 7c8bf37cd, a769ca3e7, 7d188a7c3, add98ba2a, 8c5188b90, bd47a3f5c, e45861af, 2675886ea, efd27d78, 7044fd3a5, 6f8b400d8, cf82d44f6; and the blob of cost_model.py at five refs
  sources_read_note: >-
    coordination/goals/GOAL-SSI-001/batches/BATCH-eb0a7e/reviews/TASK-20260824-5b150a/validation_report.md
    is a PRIOR ROUND's report, not a sibling in this round. My J5 attack plan
    directs me to it by name. I read lines 150-175 to verify the caveat the
    producer quotes from it. Listed here in full disclosure. Earlier I also ran a
    recursive grep across BATCH-eb0a7e that scanned that file and returned no
    match from it.
    ledger/decisions/DEC-20260809-39eb45.yaml and ledger/evidence/EV-SSI-e8cc71.yaml,
    ledger/evidence/EV-SSI-12c22e.yaml and ledger/evidence/EV-WESO-001.yaml are in
    my read_scope but I did not open them; the producer's one-line summaries of
    them are therefore UNVERIFIED by me and I relied on none of them.
  procedure_deviations: []
  verdict: inconclusive
  verdict_note: >-
    `inconclusive` is the round-level verdict for my four joints taken together,
    and it is a composition, not a hedge: J3 holds, J1 and J2 hold with recorded
    caveats, and J5 breaks. A single word cannot carry a split like that, and the
    per-joint verdicts above are the operative record. The Coordinator composes
    this with J4 and J6; I cannot see them and offer no whole-claim verdict.
```
