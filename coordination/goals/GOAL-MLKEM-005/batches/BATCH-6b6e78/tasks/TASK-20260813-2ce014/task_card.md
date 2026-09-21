# TASK-20260813-2ce014 — THE LEAD PRODUCER: score A-1's falsifiers

    goal / batch    GOAL-MLKEM-005 / BATCH-6b6e78
    role            executor
    policy          executor-implementation     effort medium
    state           queued
    depends_on      TASK-20260813-502381  (the notarizing commit MUST exist first)
    review_required true
    archived_by     TASK-20260813-48240d
    budget          5400 s session, 4 GB, 1 run — MEASUREMENT CAPPED AT 600 s
    claim tier      TOY

## The three obligations you own, from the goal's single next_action

Obligation **(a)** — the numbered assumption — is discharged by the frozen text
itself. Yours are (b), (c) and (d), and **(d) gates the other two**.

**(d) THE FIBRE FAMILY IS PER CANDIDATE, AND THE GUARD MUST GUARD.** Build each
candidate's fibre family from **that candidate's own** declared nuisance set
(PREREG-2 §2.4), using the frozen `PIN-DET` and `PIN-A00` constructions (§2.3).
Then **ASSERT AND PRINT, per candidate, per fibre family and per lattice, WHICH
DECLARED ARGUMENTS WERE VERIFIED CONSTANT** across the basis index — not
`abs(det B)` alone. `abs(det B_i)` by **exact integer** equality, `A[0,0]` by
integer equality. That printout is `R3-OUT-4` and it is a **first-class
deliverable**: a run that computes it and does not print it per candidate has
**not** discharged (d). If any declared nuisance argument varies anywhere,
**`R3-OUT-V` fires**: report the instrument defect and **stop**, rather than
reporting fibre verdicts you have just voided.

*Why this is first:* in `BATCH-4ed139` `A[0,0]` was declared a fibre nuisance
argument and held fixed **nowhere**, and the guard never checked it. Both reviews
found it independently. This obligation exists to fix exactly that.

**(b) RE-SCORE F0's REFUSAL HALF WITH `R6_exact` ADDED**, and report **all three
frozen readings**, per candidate, per route, per cell, with coverage:

    V6   the SIX float routes {R0..R5}         -- the frozen PREREG-1 4.1 reading
    V7   the SEVEN routes {R0..R5, R6_exact}   -- every route must hold
    VX   the EXACT route ALONE {R6_exact}

**No one of the three may be reported without naming its route set in the same
sentence.** Scope is the **refusal half only** — `X_null` and `rdet`,
determinant-only, no reduction.

**AND RE-RUN THE ARCHIVED PROBE, UNMODIFIED, FROM ITS COMMITTED PATH:**

    coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/reviews/
      TASK-20260812-696cd4/probes/probe_precision_null.py      (0.4 s)

with `--out` pointing into **this** task's directory. **DO NOT COPY IT, DO NOT
EDIT IT, DO NOT VENDOR IT** — it is a committed artifact of another batch and it
is immutable. Record its sha256 and report whether the re-run agrees with the
archived `probe_precision_null_output.json` **field by field**; name any
disagreeing field. The point of re-running it is that **this batch's own record
answers the question rather than inheriting `DEC-20260812-781961`'s answer.**

**(c) EVERY VAR-F-LIKE CONSTANCY CLAUSE AT TWO WORKING PRECISIONS.** For every
in-scope candidate, route and covered cell, at **both** `binary32` and
`binary64`: `s_c^fib`, `m_c^fib`, `rho`, `bit_identical`, the number of distinct
IEEE-754 values, **the committed `VAR-F` verdict at that precision**, and the
ratio `rho(binary32)/rho(binary64)`. **State per clause whether its verdict
CHANGES with precision**, with the cell count — and where it does, say in your own
words that the clause is reading a **representation** rather than an observable.

## The specification is PREREG-2, not this card

`tasks/TASK-20260813-25cb95/prereg.md`: the assumption `A-1` and its five
falsifiers (§1.2), the `precision_degenerate` rule with both readings (§1.3), the
frozen objects and per-candidate argument sets (§2), the **derived exact route**
for `X_gso_k` (§2.9) and its `P-GRAM` check, the diagnostic (§3), the `K`-interval
computation (§3.5), the `X_hash` calibration (§3.6), obligation (b)'s three
readings (§4), the prediction register (§5), the must-pass guard and the
could-not-fail arrangements (§6), the four-way termination clause (§7) and the
outcome rows (§8). **Do not re-derive any of it and do not amend it.**

## Artifacts — TEN PATHS, AND WRITE NOTHING ELSE IN THE REPOSITORY

    tasks/TASK-20260813-2ce014/measure_a1.py
    tasks/TASK-20260813-2ce014/results_a1.json
    tasks/TASK-20260813-2ce014/report_a1.md
    tasks/TASK-20260813-2ce014/rerun_probe_precision_null_output.json
    tasks/TASK-20260813-2ce014/rerun_probe_precision_null_stdout.log
    tasks/TASK-20260813-2ce014/rerun_probe_precision_null_stderr.log
    tasks/TASK-20260813-2ce014/command.txt
    tasks/TASK-20260813-2ce014/stdout.log
    tasks/TASK-20260813-2ce014/stderr.log
    tasks/TASK-20260813-2ce014/run_manifest.yaml

Run **every** Python invocation with `PYTHONDONTWRITEBYTECODE=1` and `-B` so no
`__pycache__` appears inside the repository. `command.txt` records **every**
invocation in order. `report_a1.md` must **LIST EVERY PATH THIS TASK WROTE**
inside the repository. An undeclared committed file and a declared uncommitted
file are the two halves of defect D3 and both are terminal for an archive.

## Bounds

Seconds to low minutes. **Hard cap 600 s of total measurement wall clock.** **NO
NEW REDUCTION OF ANY KIND, and nothing reduction-dependent above `d = 40`.**
`R7_exact_gram` is **mandatory at `d <= 40`** and **best-effort at
`d in {100, 140}`** under a **45 s per-lattice cap**; a lattice over the cap is
`UNCOVERED` and forces the `-PARTIAL` suffix. `lam1n`, `hkz` and `rawtail` are
**OUT OF SCOPE** (PREREG-2 §2.5) — a declared scope limit, **never** an `FC-1`
firing.

## The things not to get wrong

* **The falsifiers are scored against the CERTIFIED class**, not against §2.4's
  `expected` column. If a certification contradicts the expectation, the
  **certification binds** and the disagreement is a **finding**.
* **`P-GRAM` failing means the derivation is wrong.** Report `R7_exact_gram` as
  UNAVAILABLE — which fires `FC-1` — and report the disagreement. **Do not patch
  the derivation and do not substitute another route.**
* **Read the termination branch off `R3-OUT-1` and `R3-OUT-2` under `R3-OUT-V`'s
  precedence, and nowhere else.** Name the branch, quote the clause, state what it
  licenses and forbids. Do not argue for a different branch. Do not report a
  branch the numbers do not fire.
* **Do not specify, propose or imply a replacement criterion, fibre clause, gate
  or threshold.** Reporting that a `K`-interval is non-empty is a **measurement**;
  proposing a `K` is not yours to make.
* **Do not restate `KN-FIND-9d44b4`'s promoted content as a new result** (PREREG-2
  §9 lists exactly what that is).
* A timeout, a crash or a missing dependency is **INFRASTRUCTURE SIGNAL**
  (`AGENTS.md` rule 5). It forces PREREG-2 §7.6's `-PARTIAL` suffix. It is
  **never** a falsifier of `A-1`.
* `AM-18(f)`: a **run** is any invocation that executes the declared measurement
  to completion. A completed measurement invocation may not be reclassified, and a
  superseded completed run is enumerated against the budget with its reason.
  Record **the adapter binding for this role** beside the model that answered.

## Binding carries

PREREG-2 §§10 and 10.1 in full, including the citable range **4.87x to 31.03x**,
that **neither** sub-6x count is citable, that any sub-threshold count must name
**all four axes plus its summation algorithm** in the same sentence, and that
"genuinely cross-platform" is not citable. **CLAIM TIER TOY.**
`knowledge/INDEX.md` is not written, regenerated or staged. **COMMIT NOTHING.**
