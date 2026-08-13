# TASK-20260803-535d15 validation notes

Early complete draft written before long-running checks. It records only work
actually performed so far and will be refined in place.

## Scope and frozen input

- Task card read in full from
  `coordination/goals/GOAL-MLKEM-004/batches/BATCH-d2a728/dispatch_queue.json`.
- Required contracts and context read:
  `AGENTS.md`, `agents/validator.md`, `docs/inventor-protocol.md` (including
  sections 3 and 6), `ledger/goals/GOAL-MLKEM-004.yaml`,
  `KN-TECH-14efa5`, `KN-TECH-797223`, and `KN-OPEN-016`.
- Producer report, script, results, receipt, rebuild transcript, and snapshot
  receipt read. No sibling Red Team output was read.
- Frozen snapshot declared by the card:
  `8cc51677f7202e9f9b85efdf834860254798abf4`.
- Snapshot reachability and hashes have not yet been independently checked in
  this draft.

## Preliminary source audit

`measure_scores.py` constructs `A`, `s`, and `e` from the recorded instance
seed, then sets `b = A*s + e mod q`. The dual basis is built from `A` and `q`
only. LLL and g6k are seeded independently. The secret is not passed into the
basis, LLL, sieve, coefficient extraction, or vector selection.

The secret enters candidate construction in two places: as the explicitly
labelled correct candidate and as the base of eight `s+e_j` near misses. The
near misses therefore have a deliberate structural advantage over independent
wrong candidates: their phase differs from the correct phase by one coordinate
of `y`. That is useful as a local-sensitivity control but does not contaminate
the correct-secret score or cause the sieve to know `s`. It does mean the three
wrong-candidate classes are not exchangeable and must not be pooled without
declaring the mixture.

The null keeps `A`, the dual vectors, candidates, and scoring code fixed and
replaces `b` by a uniform vector in `Z_q^m`. This removes the LWE relation
between the named secret and the target while holding the measured vector
population fixed. It is the right same-shape null for asking whether the
fixed scoring pipeline ranks the nominal secret when no LWE signal exists.
A null that re-randomizes `A` and regenerates the sieve vectors would instead
test sensitivity to the vector population / instance, which this one-instance
archive does not control.

## Producer rebuild record

The producer transcript does not show a from-scratch rebuild. It explicitly
states that `/tmp/sagevenv` already existed and that the install command
returned `Requirement already satisfied`. It does show successful functional
checks of passagemath 10.8.7, fpylll 0.6.4, and g6k 0.1.2 before the official
measurement, plus two preserved errors in the producer's verification script.
This is a reproducibility-ladder defect, not evidence against the measurement.

The current Coordinator-started rebuild is separate work and must not be
described as this validator's independent rebuild. Its status and any
validator-executed functional check remain to be recorded.

## Commands run so far

```text
ls "coordination/goals/GOAL-MLKEM-004/batches/BATCH-d2a728/tasks"
```

Output:

```text
TASK-20260803-e53ce2
```

```text
mkdir -p "coordination/goals/GOAL-MLKEM-004/batches/BATCH-d2a728/tasks/TASK-20260803-535d15/scripts"
```

Output: none; exit 0.

## Checks still pending in this early draft

- Frozen-commit reachability, parent, exact changed paths, artifact hashes, and
  working-tree identity to the committed blobs.
- Direct raw JSON recomputation of every quantitative claim in report sections
  2, 4, and 5.
- Exhaustive score/phase equality and all array lengths.
- Independent seed reconstruction of `A`, `s`, `e`, candidates, and null target.
- Rank of `A^T mod 127`, and whether `y` is recoverable from candidate phase
  differences.
- Larger NULL-target candidate-class control with a new recorded seed.
- Status of `instrument-rebuild2`, current instrument functionality, and an
  attempted reproduction if the rebuilt venv is usable.
- Adapter probe and exact validator runtime provenance.

No comparison against `MATZOV.Nf` has been run or will be run in this task.
