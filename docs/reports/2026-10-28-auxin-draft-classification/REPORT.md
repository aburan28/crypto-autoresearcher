# Hash-bound classification of the AUXIN successor draft

**Mechanical validation, 2026-10-28.** The archived
[`EXP-AUXIN-339fb0` specification](../../../experiments/EXP-AUXIN-339fb0/specification.yaml)
has a top-level `successor_contract` rather than `experiment`. Its source
header says `status draft, approved_by null`. The `fresh` block gives
`id: EXP-AUXIN-339fb0`, `status: draft`, `approved_by: null`, and
`approval_decision: null`; its `F-APPROVAL` block is also draft. It is
byte-identical to the [design-stage copy](../../../coordination/goals/GOAL-AUXIN-a93442/batches/BATCH-ad00c6/design/TASK-20260929-d519f6/draft-contract.yaml):
both SHA-256 hashes are
`6a1dca32c109d5badf4ba143c31f9d4d9a49e18ae287c8bb4fc604526bf02ecc`.
This establishes a placed draft, not an approved executable experiment.

The [hosted ledger job on PR #2655](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/40627808095/job/122616982776)
contains one error for this path: `expected top-level key 'experiment'`.
[PR #2656](https://github.com/isogeny-labs/crypto-autoresearcher/pull/2656)
separately archives the complete 65-error inventory; it was open when this
classification report was written.
The validator now classifies **only this exact path and both exact copies**
as a draft. It requires matching experiment, batch, task, and goal IDs;
draft status; null approval fields; and the frozen hash on both files.
It records a visible advisory and keeps the existing legacy alias for
reference resolution, but it does not register an experiment in `ctx.ids`.
No run is authorized by this classification.

![Draft classification and refusal paths](classification.svg)

## Controls and result

`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest
tools.test_validate_ledger.FrozenSuccessorDraftTests -v` passed 3 tests on
the scoped worktree. The positive test checks the advisory and absence from
the experiment index. Negative controls mutate status, approver and ID;
alter the source copy; and present the same document under another path.
The altered source copy retains the ordinary top-level schema error and no
experiment registration. The underlying archived files, hash registries,
suppression baseline, and numerical results are unchanged.

The [complete-tree hosted ledger job](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/40630565509/job/122625879025)
compared branch head `07460029d2ebfdc3f800161bc144e4b0ac70ef0f` with
base `fb55b843d5c025d95e80de6185f12a4dd5da2a6f`. Its downloaded
[CI artifact](https://github.com/isogeny-labs/crypto-autoresearcher/actions/runs/40630565509/artifacts/12790843247)
contains the exact [base log](evidence/ledger-base.log) and
[head log](evidence/ledger-head.log). The base has **65 errors in 22 paths**;
the head has **64 in 21**. Set comparison finds **zero added** and exactly
one removed message:

> `experiments/EXP-AUXIN-339fb0/specification.yaml: expected top-level key 'experiment'`

The base log SHA-256 is
`463cdceec5d3b008c9788d45f91842197e50b5066bb3aaa547fcf10d88d58149`;
the head log SHA-256 is
`3c9ef0f1c32e23900a5b47c5e093e844b326fbdf2d03c8eebf21338ba7ed2a77`.
Advisories increase from 578 to 579, as intended. Both full validators still
exit 1. The CI relative-delta gate passes because no new error appeared;
the **absolute full-ledger gate remains red**. [validation.json](validation.json)
records the comparison. No canonical performance graph changes: this is a
record-category correction with no measured quantity.
