# BATCH-038 — input capsule

Everything a worker in this batch may rely on, and the exact state it starts from.

## Binding records

| record | role |
| --- | --- |
| `experiments/EXP-SMTH-71b1b0/specification.yaml` | the frozen contract; **sha256 `e193a196…`, 17950 bytes** |
| `experiments/EXP-SMTH-71b1b0/freeze_receipt.json` | digest pin; the Executor re-hashes and HALTS on mismatch |
| `ledger/decisions/DEC-20260803-155a86.yaml` | authorization to execute |
| `ledger/corrections/CORR-20260803-a1c41e.yaml` | two unresolved receipt defects |
| `ledger/hypotheses/H-SMTH-001.yaml` | the hypothesis under test |
| `ledger/corrections/CORR-20260803-77d5da.yaml` | why OPEN-BATCH023-A is still owed |
| `DEC-20260801-011` | ranked OPEN-BATCH023-A first |

## Base state

- Branch `claude/implementation-p9dqz3`, merge commit `5fbc8b8c` (`origin/main` merged, never rebased).
- `tools/check_merge_hygiene.py`: **PASS** — no conflict markers, no unparseable records.
- `tools/validate_ledger.py`: **FAIL, 20 new errors** (down from 110 before the merge).

## The 20 pre-existing validator errors

None are introduced by this batch and none is a dependency of it. Listed so no
worker mistakes them for damage it caused:

- `H-WESO-001`: missing `question_id`
- `DEC-20260731-011`, `DEC-20260731-013`: missing `decided_by`; `knowledge_promotion.promoted` not a list
- `DEC-20260802-201`: missing `knowledge_promotion`
- `EXP-ECTD-001`: missing `success_criterion`
- `EXP-JMV-002`, `-003`, `-005`, `-006`: missing `hypothesis_id`
- `EXP-DS-001/runs/RUN-DS-001-ctrl-unplanted/manifest.json`: frozen legacy hash changed — supersede, do not edit
- `EXP-DREG-001/runs/RUN-DREG-001-CTRLB-N12-D6/manifest.yaml`: `run.code.command` missing
- `EV-DS-006` … `EV-DS-010`: cite unknown `RUN-DS-001-ctrl-*` runs
- `EV-IT-001`, `EV-IT-002`: cite `RUN-IT-001-bounded-toy` / `RUN-IT-001-rerun`

## The manifest trap — read this before writing any run artifact

The last two errors are the reason this batch carries a binding Executor
constraint.

`RUN-IT-001-bounded-toy` and `RUN-IT-001-rerun` **exist**, each with
`command.txt`, `environment.json`, `stdout.log`, `stderr.log`,
`raw-result.json` and `manifest.json`. They are complete run packages. They
still fail validation, because:

- `validate_ledger.py` scans runs only at `experiments/*/runs/*/manifest.yaml`;
- those runs wrote `manifest.json`, flat, with no top-level `run:` key;
- the JSON rescue path registers ids only for **frozen legacy** manifests, and
  these are new (BATCH-028, 2026-07-31), so it does not cover them;
- their ids are therefore never registered, and every evidence record citing
  them fails.

The validator's own comment names the trap: *"without registering the id
nothing may cite the run — every evidence record naming it fails instead,
which is the schema debt reported as the record's own defect."*

**So:** write `experiments/EXP-SMTH-71b1b0/runs/RUN-SMTH-71b1b0-001/manifest.yaml`,
nested under a top-level `run:` key, with `run.id`, `run.code.commit` and
`run.code.command` populated, and the five companion artifacts present.

## Budget (from the contract, not negotiable here)

`maximum_runs: 1` · `maximum_resume_count: 1` · wall `5400 s` · CPU `21600 s` ·
peak RSS `4 GiB` · disk `16 GiB` · workers `4` · `no_network: true`.

**Bounded working set is required.** `RUN-SMTH-PILOT-002` crossed RSS and
nothing else — 15,368,192 bytes over a 4 GiB cap (0.36%), at 40.6% completion,
on 5.4% of its wall ceiling and 2.0% of its CPU. Peak resident memory must
therefore depend on the shard buffer and interpreter baseline **alone**, never
on records already produced. A pre-flight RSS probe at ~5, 10 and 20 percent of
records — tolerance and margin declared *before* it runs — gates the full run.

`stop_semantics`: crossing any ceiling stops at the next record boundary. **A
stop is reported as a stop, never as a result** (AGENTS.md core rule 5).

## Success criterion (quoted, not paraphrased)

> SUPPORT AT TOY SCALE iff, at BOTH field sizes: KS2-DS-1 ≤ 0.006373,
> TAIL-DS-1 ≤ 0.01, DECAY-1 does not fire, and the blocking controls
> CTRL-ENCA-POWER, CTRL-APPARATUS-IDENTITY, CTRL-FACTOR-COMPLETE and
> CTRL-PAIR-COUNT all pass. KS-DS-1 and RATE-DS-1 are reported alongside but do
> not gate this criterion.

## Claim ceiling

**TOY TIER under every outcome.** No crypto-scale, medium-scale,
affected-scheme or asymptotic claim is derivable; no exponent or cost saving is
claimed or claimable. A negative outcome closes only the exact tested scope.
