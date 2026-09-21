# TASK-20260814-d13724 — AUTHOR PREREG-7

    goal / batch    GOAL-MLKEM-005 / BATCH-a5b13c
    role            coordinator
    policy          coordinator-orchestration-code     effort high
    state           completed
    depends_on      (none)
    review_required false
    archived_by     TASK-20260814-487c0f
    budget          5400 s, 2 GB, 1 run
    claim tier      DERIVATION (C1) / MEDIUM (C2) -- NOT TOY

## What it did

Discharged `DEC-20260813-9c7353`'s single `next_action` in full: returned
`GOAL-MLKEM-005` to `RQ-MLKEM-001`'s substantive mechanism-search portfolio
rather than a fifth consecutive `hkz`-admissibility instrument-design batch.

Read all three currently-`proposed`, unadvanced `RQ-MLKEM-001` hypotheses in
full (`H-MLKEM-11aabf`, `H-MLKEM-232843`, `H-MLKEM-34e22e`) and made the
portfolio call explicitly, reasoned rather than defaulted: `H-MLKEM-232843`
and `H-MLKEM-34e22e` are implementation-defect-detection instruments
(decapsulation key-field integrity; sampler budget), `GOAL-MLKEM-002`-
adjacent and topically unrelated to this goal's own tracked object.
`H-MLKEM-11aabf` concerns the ciphertext-side compression/noise structure
directly, using the same pinned cost instrument
(`tools/sage_free_estimator`) this goal's own completion criterion C1
requires, and is the most decision-relevant of the three. Ruled
`/design-experiment` directly rather than `/propose-ideas` first:
`H-MLKEM-11aabf` is already a mature, decision-ready hypothesis (explicit
mechanism, numbered heuristic with its own falsification condition, seven
exact predictions, four falsification conditions, a correctly-scoped
`test_boundary` and `interpretation_limits`) that a fresh ideation pass
would not sharpen further.

Wrote and froze `PREREG-7`: Stage A (C1, the exact Compress/Decompress
fibre census at d in {4,5,10,11,12}, pure integer arithmetic, zero external
dependency, gates Stage B per the cheapest-decisive-gate discipline) and
Stage B (C2, the ciphertext-side block-size readout under three declared
noise models -- M0 single marginal, M1 per-class rescaling, M2
clean-samples-only reduced dimension -- via the pinned, already-
known-answer-controlled `estimator.lwe_primal.primal_bdd` under
`RC.MATZOV`, gated on Stage A clearing). Froze a fresh four-branch
termination clause (`T-CIPHNOISE-NODATA` / `-CLOSED` / `-OPEN` / `-MIXED`),
designed new for this experiment kind rather than reused from the `hkz`
lineage's `T-HKZINDEP-*`/`T-MUTCTRL-*` shapes. Ruled explicitly (section 3.7)
that `PREREG-2` section 7.5's repair bar does not engage this document at
all, since it never touches the `hkz`/`A-1` admissibility lane. Checked
`docs/inventor-protocol.md` section 8 and concurred `H-MLKEM-11aabf`'s own
`proof_search_map: not_applicable` is correct -- no proof_search_map is
owed. Stated explicitly (section 0.2) that `H-MLKEM-11aabf`'s status should
move `proposed -> specified` once this document is notarized, as a
separate act by a session holding a shell, not enacted by this document.

Section 1 binds the lead to independently re-verify, before trusting any
Stage B number: the pinned estimator's availability and its known-answer
control (exact delta 0.0 on `primal_bdd`), the FIPS 203 parameter
correspondence of `estimator.schemes.KyberXXX`, and -- critically -- whether
the installed API can even represent the M0/M1/M2 noise constructions at
all, rather than this document asserting an unverified API surface. If it
cannot, that is infrastructure signal for Stage B specifically
(`T-CIPHNOISE-NODATA`), and Stage A's own result stands independently.

Executed with NO SHELL, using read-only file access only. C1/C2's frozen
predictions are transcribed VERBATIM from `H-MLKEM-11aabf.predictions`,
not recomputed by this session.

## Artifact

    tasks/TASK-20260814-d13724/prereg.md
