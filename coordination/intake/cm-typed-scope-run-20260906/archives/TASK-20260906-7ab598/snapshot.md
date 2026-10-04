# Snapshot TASK-20260906-7ab598

Archive of the exact producer implementation and run receipt for
EXP-ENDO-c6c7a7 / RUN-ENDO-c6c7a7-single / TASK-20260906-f0e20a.

This receipt sits inside the commit it describes, so it cannot carry that
commit's own sha. After the commit, `dispatch_queue.json`
`tasks[TASK-20260906-7ab598].archive` is the authoritative binding
(`commit_sha`, `parent_sha`, `path_sha256`). Parent expected at authoring
time: `d48709b077ee0fd371700921d4be66795747ac03`.

## Record IDs

- EXP-ENDO-c6c7a7
- RUN-ENDO-c6c7a7-single
- TASK-20260906-f0e20a
- TASK-20260906-7ab598

## Producer path_sha256 (computed on the bytes staged for this commit)

```
0c2d47479c17afd7f3daa50e6a01a7b3d2b1b5854da0b7efd6f8e006940432fe  experiments/EXP-ENDO-c6c7a7/implementation/evaluate.py
9a3c6c32e110b4f6f195cce96723e1d8f0ffa1ed1ab570b475e3b1e722607223  experiments/EXP-ENDO-c6c7a7/runs/RUN-ENDO-c6c7a7-single/manifest.yaml
b01ca8e0ce5f195588c496c6bb6e5d0014ba56be0cfb9d63742f1470daed2dd8  experiments/EXP-ENDO-c6c7a7/runs/RUN-ENDO-c6c7a7-single/command.txt
cdd7e2f8fa884cf079073cd038744a02034b5df59ca218525d33700a057a04cb  experiments/EXP-ENDO-c6c7a7/runs/RUN-ENDO-c6c7a7-single/environment.json
f021d162289ffffe180d15a54622a24272345aadb1c5a3691b1eca9c0291520a  experiments/EXP-ENDO-c6c7a7/runs/RUN-ENDO-c6c7a7-single/stdout.log
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  experiments/EXP-ENDO-c6c7a7/runs/RUN-ENDO-c6c7a7-single/stderr.log
95be2183f6013311546c438b0935c811f87ab661bbfb8936de8d6364967f8734  experiments/EXP-ENDO-c6c7a7/runs/RUN-ENDO-c6c7a7-single/raw-result.json
f74bbecac7b2e3ef744a79f5edbf19be790b35fd2bfc77ea3f98b3e6108e2a6c  experiments/EXP-ENDO-c6c7a7/runs/RUN-ENDO-c6c7a7-single/metrics.json
cb46d3f14df2627349b95b6511e928fa02b396334f54ff0f430847b71b08e02c  experiments/EXP-ENDO-c6c7a7/runs/RUN-ENDO-c6c7a7-single/certificates.json
6bfa85deb4dbe443f09ef0d2bc919454ffaf0a12aa776fedf6b7d60e58d5a639  experiments/EXP-ENDO-c6c7a7/runs/RUN-ENDO-c6c7a7-single/execution-report.yaml
1c87b0c713546e8f3cbac7a115c247383ca2781e1e3b8be36753cd4ca94cb746  experiments/EXP-ENDO-c6c7a7/runs/RUN-ENDO-c6c7a7-single/resource-usage.json
```

Frozen authority hashes were re-checked before the run and matched
TASK-20260906-04ab4d:

```
f422d4ccecf168135eb0a09fb4f2907196f2f5f5acd8ea4ae6da3f78536cf800  experiments/EXP-ENDO-c6c7a7/specification.yaml
3027e617f946ab6cc6ac0fc6104946ef862743083b288def25e167d804323a73  experiments/EXP-ENDO-c6c7a7/fixtures.json
1b51835566f9433db0a9fa0278015e3f19b564f11eb737af73156a15a6dec014  experiments/EXP-ENDO-c6c7a7/oracle-key.json
```

## Gates

- G1: all eleven declared producer artifacts exist.
- G2: `check_run` on the new manifest returned no errors.
- G3: `tools/check_merge_hygiene.py` PASS.
- G4: `tools/validate_ledger.py` reports no new error naming EXP-ENDO-c6c7a7
  or RUN-ENDO-c6c7a7-single. Pre-existing main errors (ECRANK and others)
  are unchanged and outside this write_scope.
- G5: origin/main merged before the run (already up to date at
  d48709b077ee0fd371700921d4be66795747ac03). Merge, never rebase.

## What this does not do

No hypothesis or goal status change. No validator dispatch in this commit.
No scientific interpretation. Independent review remains TASK-20260906-af0691.
