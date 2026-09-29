# Design snapshot declaration

Coordinator archive task TASK-20260907-ae9e70 commits the exact nine producer artifacts of TASK-20260907-ea2134 plus this declaration. The dispatch queue is operational receipt state and is committed separately after the artifact commit; no self-referential commit hash is placed here.

- ledger/hypotheses/H-FROB-824aa8.yaml
- experiments/EXP-FROB-b8cf21/specification.yaml
- ledger/handoffs/TASK-20260907-ee1e3c.yaml
- ledger/hypotheses/H-ICEX-9d76cb.yaml
- experiments/EXP-ICEX-17a209/specification.yaml
- ledger/handoffs/TASK-20260907-bde32d.yaml
- ledger/decisions/DEC-20260907-12ee7d.yaml
- coordination/intake/ecc-design-20260907-ea2134/review.md
- coordination/intake/ecc-design-20260907-ea2134/source-notes.json

Records: H-FROB-824aa8, EXP-FROB-b8cf21, TASK-20260907-ee1e3c, H-ICEX-9d76cb, EXP-ICEX-17a209, TASK-20260907-bde32d, DEC-20260907-12ee7d.

All artifacts are designs and approvals only. There are no scientific runs or evidence findings. The full ledger has six inherited errors described in bootstrap.json; scoped validation must add none. Future execution stays unadmitted until full-ledger integrity and the declared focus, runtime, claim, lock and independent-review gates are met.

Validation before freeze (control-plane results, 2026-09-07): new record schemas/cross-references PASS; exact12/20 cell counts PASS; canonical future manifest/companions and scope agreement PASS; dispatch queue PASS; git diff --check PASS. Full tools/validate_ledger.py exited1 with exactly the same six inherited errors in experiments/EXP-ECDLP-5cad48/runs/RUN-ECDLP-5cad48-S2G/manifest.yaml as the synchronized base; zero added errors. The source archive contains ten intended files, largest26.7KB at that inspection. No experiment, simulation, solver or mathematical certificate checker was executed by this design session. Planned run-ID syntax is compatible with RUN_ID. The control plane completed exact rg checks for RUN-FROB-b8cf21-ee1e3c and RUN-ICEX-17a209-bde32d across existing manifest.yaml/manifest.json files and experiment paths: both searches returned exit1/no matches, not a timeout. A fresh collision check still precedes future first execution.
