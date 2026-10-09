# Sparse checkouts for execution sessions

A full checkout is about 9.3 GB in 122,000 files, and most of it is immutable
archive that an execution (`run`) session never reads:

| excluded by the `harness` profile | size | files |
| --- | ---: | ---: |
| `experiments/*/runs/` (except experiments with a trial plan) | 5.1 GB | 42,000 |
| `inputs/refs/` (reference bundles, incl. committed Rust build trees) | 1.1 GB | 6,100 |
| `inputs/archive_from_autolab/`, `inputs/pqshield-signature-zoo-20260928/` | 0.3 GB | 3,900 |
| `research/cold_*/` (IC run outputs) | 0.3 GB | 430 |

The `harness` profile keeps everything else, about 2.4 GB: code, specifications,
the ledger, `coordination/`, knowledge, and the `runs/` of every experiment
that has a `trial-plan.json`, because the selector and the runner hash those
receipts to decide what is still planned. On a 2026-10-09 checkout it
materialized 75,199 of 122,529 files in 15 seconds.

## Commands

```sh
python3 tools/sparse_checkout.py status                       # profile, files on/off disk, history
python3 tools/sparse_checkout.py apply harness                # set the profile (frees ~7 GB)
python3 tools/sparse_checkout.py add --experiment EXP-...     # that experiment whole + inputs it names
python3 tools/sparse_checkout.py add --goal GOAL-...          # every experiment naming the goal
python3 tools/sparse_checkout.py add --path inputs/refs/X/    # any path (end a directory with /)
python3 tools/sparse_checkout.py patterns harness             # print the rules, change nothing
python3 tools/sparse_checkout.py disable                      # full checkout again
```

`--experiment` materializes `experiments/<ID>/` including its `runs/`, plus
every tracked path its `specification.yaml`, `trial-plan.json` or
`dependencies.json` names. A named directory also re-includes the excluded
subtrees beneath it. `apply` replaces earlier additions; `add` keeps them.
The profile and its additions are recorded as comments in the worktree's
`info/sparse-checkout` file, so each git worktree has its own.

## Using less network, not only less disk

A sparse checkout of an existing full clone only frees disk: the blobs were
already downloaded. To download less, clone blobless and let the profile
decide which blobs arrive:

```sh
python3 tools/sparse_checkout.py clone https://github.com/aburan28/crypto-autoresearcher DIR [--branch B]
```

This is `git clone --filter=blob:none --no-checkout`, the `harness` rules, then
`git checkout`: history arrives as commits and trees, and only materialized
files are downloaded. The tool is standard library only, so a copy of the file
can run before any checkout exists. Anything read later outside the profile
(`git show HEAD:<path>`, `add --experiment`) is fetched on demand.

**Session start.** In Claude Code on the web, set
`CRYPTO_AR_SPARSE_PROFILE=harness` in the environment's variables and
`.claude/hooks/session-start.sh` applies the profile before anything else
runs, which also leaves room for the SageMath install (it needs 10 GiB free).
Without the variable the hook prints a one-line hint when a full checkout
leaves less than 20 GiB free. The hook's history fetch is now
`tools/sparse_checkout.py deepen`: `git fetch --unshallow --filter=blob:none`,
commits and trees only. The plain `--unshallow` it replaces downloaded every
blob of all ~1,300 branches; archive verification needs reachability and
trees, and reads the few old blobs it needs on demand. `goal_portfolio_health.py`
deepens the same way.

**Child sessions.** `create_session`'s `sparse_checkout_paths` is cone mode
(whole directories), which cannot express "every experiment but not its
runs". Start the child in an environment whose variables set
`CRYPTO_AR_SPARSE_PROFILE=harness`, or make `python3
tools/sparse_checkout.py apply harness` the first line of its prompt.

## What knows about sparse checkouts

Excluding a path hides it from the filesystem, not from git: it stays in
`HEAD` and in the index with the skip-worktree bit. **Absence on disk is not
absence from the repository.**

- `tools/newest_experiments.py` reads legacy run activity from the index, so
  an experiment with runs off disk still selects as `needs_reconciliation`,
  not as unrun. A trial plan whose coverage depends on runs off disk selects
  as `needs_materialization`, with the `add --experiment` command as its
  reason. On the 2026-10-09 checkout full and sparse selections were
  identical (1,040 rows); without this the sparse one offered 992 runnable
  rows instead of 90.
- `tools/experiment_execution.py` reports such a trial as `not_materialized`,
  never `planned`, and `run` refuses to launch while any run directory of the
  plan is off disk or outside the sparse rules (`git add` would refuse its
  records, so they could never be published).
- `tools/allocate_id.py --check` counts identifiers carried by off-disk paths;
  its identifier-bearing path set was identical in both checkouts (41,893).
- `tools/validate_ledger.py`, `tools/goal_portfolio_health.py` and
  `tools/portfolio_kpis.py` sweep the whole repository and **refuse** a sparse
  checkout: off-disk run records read to them as missing (validate_ledger
  reported 2,042 errors instead of 105) and as unrun contracts (which moves
  approval capacity). Run them in a full checkout, or after `disable`.
  `CRYPTO_AR_ALLOW_SPARSE=1` runs them over what is on disk, for diagnosis
  only.
- CI checks out in full and is unaffected.

## Which sessions should use it

| session | checkout |
| --- | --- |
| `run` (execution) | `harness`; `add --experiment` for a named experiment outside it |
| Executor, Validator, Red Team on one experiment | `harness` plus `add --experiment` |
| `coordinate`, `research-status`, `review-evidence`, ledger commits | full |
| `deep-research`, `curate-knowledge`, `propose-ideas` | either; `harness` keeps the ledger and knowledge |

A session that needs an excluded path adds it (`add --path`); it does not
conclude the path is missing. `git ls-files <path>` tells the two apart.
