# BATCH-003 ledger archive: two defects found while assembling it

## 1. I marked the validator FAILED when it had not failed

The validation session was terminated by an API session limit and its last words
to me were "Now writing the report." I took that at face value, wrote a failure
receipt classifying the task as `resource_exhaustion`, marked it `failed` in the
queue, and drafted an evidence cap on the grounds that BATCH-003 had only one
independent review.

**Then I looked in the directory.** `validation_report.yaml` is there, 57707
bytes, carrying per-claim verdicts and ending with a complete inference block —
the section that comes last. The session died while reporting back TO ME, after
its artifact was written. The task completed; the notification did not.

I deleted the failure receipt and restored the task to `completed`. Recording
this because the error had a direction: I was about to cap the batch's evidence
on the basis of a review I had not opened. Reading the artifact before ruling on
whether it exists is not a subtle discipline.

## 2. THE VALIDATION REPORT DOES NOT PARSE AS YAML

`yaml.safe_load` fails at line 844, column 103: `mapping values are not allowed
here` — an unquoted colon inside a prose scalar. The content is intact and
human-readable; the file is machine-unreadable.

**I have not edited it.** It is a reviewer's artifact and mine to archive, not to
correct. It is archived exactly as written, with this defect recorded here, and
the ledger records cite it as a reviewer artifact carrying a syntax defect.

Two things this does NOT mean. It is not a reason to discount the review's
substance — every verdict I cite from it I read directly. And it is not an
excuse to treat the review as absent: the validator returned CONFIRMED on M1's
non-singularity, CONFIRMED on the producer's own diagnosis of the engine-B
timeouts as resource exhaustion rather than evidence, and — auditing in the
direction it was asked to — UNDERSTATED on a claim whose measured content exceeds
its wording.

## 3. `check_merge_hygiene.py` has been FAILING since BATCH-002 landed, and I did not notice

It reports five unparseable files:

    BATCH-002/.../runs/WRONG6-06.json, WRONG6-07.json, WRONG7-01.json
    BATCH-003/.../runs/B1_cnt_soft.json, B1b_cnt_soft.json

Every one is a **zero-byte or truncated output of a killed run** — the timeout
artifacts this campaign has been careful to record as `resource_exhaustion`
rather than delete. They are honest records. They are also, being named `.json`
and containing no JSON, exactly what the hygiene checker is built to catch.

The BATCH-002 files have been committed since that batch's snapshot archive. I
ran the checker repeatedly after that and reported PASS at least once from an
invocation whose output was consumed by a shell pipeline. **I reported a PASS I
had not actually read.** That is the same error as (1) in a different costume:
asserting the state of a thing I did not look at.

Not repaired here, and the reason is not laziness: the files are immutable
artifacts inside a dispatcher-verified archive, and rewriting or deleting them to
satisfy a linter would destroy honest records of failed runs to make a check go
green. The correct repair is in the CHECKER or the NAMING CONVENTION, not in the
evidence. Recorded as an open item for a successor batch.
