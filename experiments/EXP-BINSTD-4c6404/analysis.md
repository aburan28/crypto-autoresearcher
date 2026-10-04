# EXP-BINSTD-4c6404 analysis

Review task TASK-20261004-26d06a. Archived by TASK-20261004-485b06.
Evidence EV-BINSTD-0da481. Decision DEC-20261004-29f894.
Hypothesis H-BINSTD-dcc004 stays approved. Amazon Bedrock was not used.
No Magma, Sage, or AUXIN.

## Observation

RUN-BINSTD-9daa20 is the only Stage-0 run directory. Producer argv returned 0
and `raw-result.json` outcome is `O-STAGE0-OK`. `claims.break`,
`claims.ecdlp_solve`, and `claims.exponent_move` are false.
`certificate.kind` is `none`.

`check.stdout.log` is:

```
FAIL:
  r_n freeze mismatch
```

The execution receipt status is `invalid_output`, with `check_returncode` 1
and `returncode` 0. The manifest status is `invalid_measurement`.
`RESULTS.md` labels the experiment `O-IMPEDIMENT` and says the frozen
prediction was not compared.

No Stage-1 run directory exists. `RUN-BINSTD-42a607` was not created.
`stage1/` holds only `.gitkeep`. Stage 2 was not launched. No Stage-1
timings exist.

A temp replay copied the experiment to `/tmp/review-binstd-4c6404`, ran
Stage 0 only with `--run-dir /tmp/review-binstd-4c6404-run`, and ran
`check.py` on that run directory. Stage 0 printed
`{"ok": true, "outcome": "O-STAGE0-OK", "stage": 0}` and exited 0.
`check.py` exited 1 and printed `FAIL:` / `r_n freeze mismatch`. The fresh
freeze wrote `r_n` keys `"17"`, `"23"`, `"31"` (strings). The repository
experiment directory was not written by the replay. Stage 1 was not launched.

## Comparison

The producer raw label `O-STAGE0-OK` and the independent check disagree.
`H-BINSTD-dcc004` defines `O-STAGE0-OK` as Stage-0 freeze twins agreeing,
with no scientific timing yet. It defines `O-IMPEDIMENT` as timeout, crash,
or a missing Stage-0 freeze: infrastructure, and never negative evidence
against `H-BINSTD-dcc004` / `HEUR-BINSTD-79a077-H1`.

`RESULTS.md` uses the experiment-level label `O-IMPEDIMENT` for the failed
independent freeze check, and leaves the producer raw outcome
`O-STAGE0-OK` unchanged. That conjunction matches the receipt, the check
stdout, and the manifest. It does not match a validated Stage-0 success.

`O-SUPPORT` and `O-FAIL-BAND` are the band readings. Stage 0 in `run.py`
does not call `decide()`. Those labels are returned only for stage >= 1.
`check.py` records `r_n freeze mismatch` on the Stage-0 path and returns 1
before the Stage-1/Stage-2 ratio block. The band was not measured.

The temp replay reproduces the archived check failure: exit 1 and the same
`r_n freeze mismatch` line.

## Inference

The independent check rejected the Stage-0 freeze, so there is no measured
Wiedemann-versus-dense band. Stage 1 was not launched. `O-IMPEDIMENT` is
not a refutation of `H-BINSTD-dcc004` or `HEUR-BINSTD-79a077-H1`.

The decision is `refine`. Direction is neutral. Strength is inconclusive.
Claim tier is toy. Proof status is not applicable. The hypothesis remains
`approved`. `EXP-BINSTD-4c6404` moves from `approved` to `invalid`. No
`KN-FIND` is promoted. This package does not authorize a Stage-1 run on
the failed freeze.

## Limitation

Scope is the archived Stage-0 package plus one temp replay of Stage 0.
Toys named in the contract are n in {17, 23, 31}; none of those band cells
were timed. This package does not calibrate n=23, n=31, or ECC2K-130.
No discrete logarithm is solved. No exponent is claimed.

The recorded defect is the `r_n` freeze mismatch (JSON string keys versus
integer `R_N`). Repairing that freeze so `check.py` exits 0 is a later
task. This review does not perform that repair and does not authorize it.
The archived run has `code.dirty` true; the manifest says implementation
sources matched the trial-plan hashes and that the freeze files were
uncommitted at process exit.
