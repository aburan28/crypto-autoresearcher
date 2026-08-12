# Analysis — Autolab task/result migration

## Observation

The corrected canonical migration selected 186,032 entries totaling
51,286,418,925 bytes
from `tasks`, `research`, `experiments`, `output`, and `research_ledger.md`. It
cataloged all 32 top-level task packages, verified all 186,032 destination
entries as identical, and found zero missing or hash-mismatched entries. The
content tree SHA-256 is
`be7c43abb7b4786a08081c795d54f7bcf0d7f42566f2eb41b240865324a4171c`.

The first run copied 38,382 files and bound 186,029 entries, but its enumerator
omitted three already-present directory symlinks used as fixture aliases.
`CORR-ALMIG-001` records the defect; the first receipt is retained and is not
used for the complete-coverage claim.

## Comparison

A second read-only pass used a separate metadata directory and disabled harness
output. It independently enumerated the same 186,032 entries and 51,286,418,925
bytes, verified every destination entry as already identical, found zero
mismatches, and reproduced the same tree SHA-256.

## Inference

The selected local mirror was byte-identical to the source at verification
time, including all 27 symlinks whose target text is hash-bound. This supports only
the integrity and coverage of the local migration. It does not verify any
historical scientific claim.

## Limitation

Historical controls, certificates, timings, model provenance, and claim scope
remain exactly as recorded in Autolab. Current-harness promotion requires new
review and, where applicable, re-execution. The source repository was dirty, so
its commit identifies only the tracked base and the file manifest is the byte
identity record. The 51 GB raw mirror remains a working-tree input archive, not
a verified Git snapshot commit.
