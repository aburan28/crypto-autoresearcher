# Addendum: this archive's binding commit, and why there are two

Additive. It corrects nothing in `ledger-receipt.json`, which is committed and
immutable, and it changes no hash, record, or verdict.

## What happened

`TASK-20260921-bd5f2e` staged its three declared paths and committed them at
`73f807a8137028e650b549f75d091a7f5e0842ff`. That commit is correct in every
respect except one: **its message names all six record ids and omits the task id
itself.**

`research_dispatch.py` requires an archive commit's message to name the task id
*and* every record id (`_verify_archive`, which reads `git log -1 --format=%B` of
the declared `commit_sha` and fails on any missing identifier). So the render
failed:

```
dispatch error: archive task TASK-20260921-bd5f2e commit message is missing IDs
['TASK-20260921-bd5f2e']
```

Six of seven identifiers were present. Only the task's own id was absent, and the
card's constraint said in terms "commit message names the task id and every record
id". This is the dispatcher catching a real omission against a requirement that
was written down, not a tooling quirk.

## Why the commit was not amended

`73f807a81` carries `EV-SEMBIN-c6e9ad` and `DEC-20260921-2c62d7`, and it is
pushed. AGENTS.md "Durable research commits" forbids rewriting history over pushed
run records, for the reason that a receipt naming a commit that no longer exists is
not reproducible. Amending would have made the omission invisible and destroyed the
evidence that a declared constraint was missed — which is the same reasoning that
keeps `TASK-20260921-064ae9`'s misfiled `parent_sha` standing rather than repaired.

An `--amend` here would also have been cheap and tempting precisely because nothing
else references the commit yet. That is the condition under which the rule is
easiest to break and least visible, which is when it matters most.

## What was done instead

A follow-up commit stages only this addendum and carries a message naming
`TASK-20260921-bd5f2e` and all six record ids. The queue's `archive_binding` points
`commit_sha` at that follow-up, with `parent_sha` = `73f807a81`.

The declared `path_sha256` set is unchanged and still verifies, because this archive
binds `content_first`, which checks declared hashes **against HEAD** rather than
against the tree of the commit named in `commit_sha`. So the binding is exactly as
strong as before: an in-place edit to the evidence record, the decision, the
analysis, or either draft would still fail the render.

## The cost, stated plainly

The commit named in this archive's binding is **not** the commit that created the
records it binds. A reader reconstructing the timeline must read `73f807a81` for
that, and this file for why.

That inversion is not new in this program — it is the standing consequence of
`tools/producer_landing.py`, which commits a producer's output the moment it
returns, so that later archives routinely stage only a receipt and bind artifacts
that already exist. `TASK-20260916-92128f` and `TASK-20260921-064ae9` both disclose
the same shape. What is new here is that the inversion was caused by a defect rather
than by the landing remedy, and that distinction is why this file exists instead of
a line in a receipt.

## What this addendum does not do

- It does not change the transition. `EXP-SEMBIN-c2c312` is `inconclusive`.
- It does not change any hash, any record, or any joint verdict.
- It does not move `H-SEMBIN-112e2e`, which stays `specified`.
- It does not affect the verdict that `GOAL-SEMBIN-5078bc`'s completion criterion 1
  is **not met**.
- It does not edit `ledger-receipt.json`, whose `commit_sha: null` and
  `commit_sha_note` remain accurate for the commit it was staged in.

## Forward guidance

The card's constraint is satisfiable mechanically and was not checked mechanically.
A commit-message assembler that takes the task id and `record_ids` straight from the
card would make this class of omission impossible, and would have cost less than
this addendum. Worth adding beside the `FG-4` receipt/queue comparison proposed in
`CORR-20260921-f5e9c4` — both are cases where a declared invariant existed and
nothing enforced it until a render failed.
