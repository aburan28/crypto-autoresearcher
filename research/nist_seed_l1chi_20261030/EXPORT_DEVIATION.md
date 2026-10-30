# Export: what `check-export` still reports, and why (recorded 2026-10-30 UTC)

`export.json` was built by `tools/experiment_protocol.py from-rows` from
`runs/rows.jsonl`: one row per eligible curve (69) plus the secp256k1
positive control. It binds the frozen protocol (`039665e8…`) and the frozen
`analyze.py` hash. It passes the schema.
`check-export --verify-files` still reports 81 findings in three groups. None
changes a number. Each records a mismatch between the export tool's model and
this study's frozen design.

## E1. Arm commit (4 findings)

- The protocol pins commit `a5378935`, which was `main` when the protocol was
  frozen.
- The run happened at `9339f214`, the commit that merged the frozen protocol.
- `analyze.py` and `calibrate.py` match their frozen SHA-256 values exactly,
  and that was checked before the run. The instrument is therefore identical.
  The export still records the true run commit.

## E2. Arm × instance coverage (7 findings) and the seed table (70 findings)

The tool assumes every protocol arm is measured on every instance: 4 arms × 69
curves = 276 rows, with a seed per (arm, instance, replicate) cell. The frozen
protocol instead models its arms as roles:

| Arm | What it is |
| --- | --- |
| `target` | prime239v1 only |
| `eligible` | the other 68 curves |
| `positive` | secp256k1 |
| `null_model` | an analytic distribution, with no rows |

The only randomness is the null's Monte Carlo seed, 20261030, which is
recorded. Every row is exact arithmetic, so no per-cell seed exists. This is
a design-modelling error in the protocol record, made when it was frozen. It
is not a missing measurement: the population is complete (69 of 69). It
can't be corrected now without a post-data amendment, which the tool would
itself flag, so the record stays as frozen and the mismatch is documented
here.

A future protocol of this kind should declare a single arm measured on every
instance, with the target and controls as instance labels.
