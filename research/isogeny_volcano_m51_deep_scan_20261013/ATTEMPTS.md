# Attempt and failure accounting

## Admitted scientific run

The sealed session records one non-resumed scientific execution:

- one build/self-test phase;
- one 21-control invocation, completed with all controls passing;
- one attempt (`attempt-000000`) for each of 256 scan shards;
- one aggregate phase over all shard outputs;
- one global classification invocation over all 42 hits; and
- one terminal global selection and seal.

All 256 shard receipts report `status=complete`, `exit_status=0`,
`timed_out=false`, `cancelled=false`, and `scientific_eligible=true`. The
classification receipt likewise reports a successful single invocation.
There was no admitted retry, resume, timeout, cancellation, crash, or
outcome-dependent rekey.

The runner retained zero admitted failures before the cutoff and zero admitted
failures overall. The final selection contains no blocking failure. Empty
attempt staging directories in the archive are expected after their accepted
payloads were promoted into canonical `build/`, `controls/`, `chunks/`,
`aggregate/`, and `classification/` locations.

## Development evidence outside the scientific sample

The frozen `PROVENANCE.md` records pre-freeze build, arithmetic, parser,
fail-closed, process-reaping, and control tests. It also records a feasibility
pilot whose complete 272-child parent fiber was frozen for exclusion before
the admitted scan. That pilot is not scientific data, did not consume the
32-pair quota, and was not silently substituted for an admitted result.

No unreported failed scientific attempt is being used as evidence against the
existence of endpoints or against any weakness hypothesis.
