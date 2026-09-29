# TASK-20260812-55056b — INDEPENDENT VALIDATION

    goal / batch   GOAL-MLKEM-005 / BATCH-4ed139
    role           validator
    policy         review-adversarial      effort xhigh
    state          queued
    depends_on     TASK-20260812-56b9da, TASK-20260812-b581a8,
                   TASK-20260812-78a6e3, TASK-20260812-4b8ede,
                   TASK-20260812-0e930c, TASK-20260812-b53c2f
    archived_by    TASK-20260812-655fe9   (ledger archive, runs alone)
    budget         7200 s wall clock, 4 GB, 1 run
    claim tier     TOY

## Objective

Independently verify the lead's G-VAR2 implementation, both fixture validations,
the V_evade scoring and all three riders — re-deriving every forced value as a
**first-class artifact**, rebuilding both fixtures yourself, and building your own
null wherever a producer's calibration is load-bearing.

## The checks that are not optional

* **Notarization in BOTH directions**, with git plumbing run by you in this
  worktree: `prereg.md` absent at the notarizing commit's parent; **zero**
  producer files at the notarizing commit; every lead artifact first appearing at
  the producer snapshot; ancestry asserted against the **notarizing commit
  itself**; `git log --all --follow` returning exactly one commit for the frozen
  text. A Coordinator claim about the git record has already been proved false
  once in this goal (BATCH-cbe023 F-1). Do not accept it; check it.
* **Change-set equality on all three archive commits** — `-1ed548` (3 declared
  paths), `-b581a8` (8), `-b53c2f` (22): change set equals declared set
  (own `artifact_paths` ∪ source `artifact_paths`), 0 extra, 0 missing, both
  counts reported per archive. That exact test failed on three archives of
  BATCH-9e3584.
* **Both fixtures rebuilt by you**: run `probe_nullroute.py` (0.31 s, six routes
  — wave 2 never tested R2, R4 or R5) and `probe_gvar_family.py` (0.24 s).
* **The fibre clause at its declared weak point.** PREREG-1 §3.5 concedes before
  the run that VAR-F moves the free parameter from FAMILY to **DECLARED ARGUMENT
  SET**. Check every declared argument set in §2.4 for honesty, and whether a
  different but equally defensible declaration flips any verdict.
* **The degenerate-scale rule in both directions.** Verify both the frozen and
  the naive reading are reported at every `scale_degenerate` cell, and check
  whether the rule is doing the refusing while VAR-F is decorative —
  rider (ii)'s `X_gso_k` is the discriminating case.
* **`tau_var = 1e-3` as a free parameter.** Report the verdict surface over at
  least four decades of `tau_var` and say which verdicts are threshold-stable.
  PREREG-1 §3.4 declares the threshold **calibrated on committed numbers**;
  check whether that calibration is load-bearing for F0, for F1, or for both.
* **Rider (i) re-derived independently** from `results_relvar.json`. It
  adjudicates a direct contradiction between two prior validators, one of whom
  you are replacing; it must not be taken on trust.
* **Committed vs uncommitted, per artifact read.** **Every producer artifact in
  this batch is committed before you run** — the lead at `-b581a8`, the three
  riders at `-b53c2f` (queue gap **G-2**, closed by taking the better shape). If
  you find any producer artifact you had to read uncommitted, **you have found
  something and must say so.** What remains genuinely uncommitted across a
  dispatch window is your own report and probes — PD-4 proper, open and
  inherited.

## Deliverable

    reviews/TASK-20260812-55056b/validation_report.yaml

**List every probe path you write explicitly in the report**, under a `probes/`
directory in your write scope. An undeclared probe cannot be committed and its
evidence is lost; a declared probe that does not exist dangles the archive. Both
are defect D3.

## Discipline

Name, before you run, the arrangement in which your own check could not fail —
in **both** directions, could-not-FIRE and could-not-PASS — and show you are in
neither. State which of your claims are single-source and which replicated.
Record independence as **PROCEDURAL AND NEVER MODEL-LEVEL** with
`model_verified: false` and its reason: AGENTS.md rule 12 is UNMET AND UNWAIVED,
and RI-3 of DEC-20260812-7c4a1e measures that one review pass of this kind has
substantially less than full recall.

INDEPENDENT SESSION. COMMIT NOTHING. Binding carries: PREREG-1 §§11 and 11.1 in
full. CLAIM TIER TOY. `knowledge/INDEX.md` is not written, regenerated or staged.
