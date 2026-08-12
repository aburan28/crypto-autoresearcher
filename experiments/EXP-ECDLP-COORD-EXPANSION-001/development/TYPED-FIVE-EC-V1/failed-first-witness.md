# Failed First-Witness Attempt

## Status

`NEGATIVE RESULT`, scoped to deterministic first-witness relation selection.
This was an implementation-valid hypothesis failure, not evidence against the
typed relation universe or coordinate point decomposition generally.

## Pinned Source

- source commit: `56fd2b0e`
- command: the exact reproduction command in `contract.md`
- raw stdout: `failed-first-witness.raw-result.json` (empty because the
  process failed before emitting its single JSON document)
- stderr and resource receipt: `failed-first-witness.stderr`

## Observation

The 10-bit cells completed, but the first 12-bit family stopped at quotient
rank `7/9` after exhausting the declared relation-target budget. The collector
retained only the first `A` split and first stored `4R` witness for each
successful target.

## Falsification Probe

A point-only read-only probe retained every supported `A` split while keeping
one canonical `4R` witness per split. All 15 curve/family cells at 10, 12, and
14 bits then reached the predicted quotient rank:

- 10 bits: `6/6` for all five families;
- 12 bits: `9/9` for all five families;
- 14 bits: `11/11` for all five families.

The probe did not use subgroup scalar labels to choose rows.

## Narrowest Conclusion

First-witness selection can introduce relation-rank bias. A functional typed
collector must either retain multiple supported splits or prove that its
witness-selection distribution spans the target-row quotient. Constant
support probability alone is insufficient evidence for relation rank.

## Successor

The repaired collector performs one complete `A` scan per known target and
inserts every supported split. Its target query exponent remains the intended
`|A|`, while candidate-row multiplicity and dependent rows are charged
separately.
