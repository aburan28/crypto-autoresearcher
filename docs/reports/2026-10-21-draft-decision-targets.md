# Decision references to frozen AUXIN drafts — 2026-10-21

The full-corpus [ledger audit in PR #2453](https://github.com/aburan28/crypto-autoresearcher/pull/2453)
found five `decision references unknown target` errors for four AUXIN draft
contracts. The cited files are frozen design-stage `successor_contract`
records, not published experiment specifications. Four decisions rule
`revise` and do not approve their drafts; the fifth authorizes only a
zero-run reviewer launch. Indexing those drafts as experiments would let
evidence cite unapproved work as if it were an experiment record.

The validator now resolves only these five decision/target pairs when the
file's SHA-256, embedded ID, goal, batch, producer, `draft` status, and null
approval fields all agree. It does not register those IDs for other record
types. A missing file, changed bytes, wrong batch, or approved state still
produces the unknown-target error.

| Frozen draft | Design batch | Decisions citing it |
|:--|:--|:--|
| `EXP-AUXIN-bafa2e` | `BATCH-9b2090` | `DEC-20260929-21bb51`, `DEC-20260929-7efa82` |
| `EXP-AUXIN-369078` | `BATCH-36b01a` | `DEC-20260929-4eade7` |
| `EXP-AUXIN-55c6c0` | `BATCH-14b284` | `DEC-20260929-93fc4d` |
| `EXP-AUXIN-92dccc` | `BATCH-1907cf` | `DEC-20260929-cfb294` |

On the complete checkout, `python3 tools/validate_ledger.py` reported
**157** unsuppressed errors after this change, versus **162** on main
`e20013ae20d2c09019d8ea1b2fed7556c61ad4ba`. Set comparison found
exactly the five lines above removed and **zero added**. The prune-only
baseline remained at **1,210** suppressed historical errors and the advisory
count at **543**. The old log has SHA-256
`8d970c4cc0ccecadc8b84eaea63bdbac5c59850c3daf46b6897aedd6351bf0ca`;
the new log has SHA-256
`266163fc12794efab6168bc4d9144e42b15b07fe9fecc5cb0443b9d022b34e00`.
`tools/ci_ledger_gate.py` accepted the complete head/base reports and found
no new errors. The focused indexing and gate suite passed **40 tests**,
including changed-draft, approved-draft, wrong-decision, wrong-batch, and
evidence-citation controls.

The ledger gate remains red. This correction changes no scientific result,
benchmark, timing, dashboard datum, or canonical performance graph; no new
measurement was produced.
