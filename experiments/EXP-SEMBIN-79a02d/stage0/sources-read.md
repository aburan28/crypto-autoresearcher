# Stage 0 sources-read list (pre-run notice N1)

Read by the Executor for TASK-20261002-fc71d6 BEFORE the Stage-0 freeze
(`stage0/FREEZE.sha256`). Order approximately as read.

1. docs/agent-runtime-core.md; agents/executor.md
2. ledger/handoffs/TASK-20261002-fc71d6.yaml
3. experiments/EXP-SEMBIN-79a02d/specification.yaml (amendments/ and runs/ were empty)
4. ledger/hypotheses/H-SEMBIN-8e8bef.yaml
5. ledger/decisions/DEC-20261005-3d5aea.yaml — key `pre_run_notices` only (N1-N4)
6. experiments/EXP-DREG-001/analysis.md; experiments/EXP-DREG-001/specification.yaml
7. src/h012c_block_m4ri.py; src/h012_peel_rank.py; src/semaev_tree.py; src/macaulay_export.py; src/ic_first_fall_fast.py
8. inputs/SEMAEV-2015-310/paper_fulltext.md lines 1-40, 380-760, 1045-1062 (sections 4.3-4.5.1, Tables 1 text, off-diagonal remark)
9. inputs/SEMAEV-2015-310/tables.yaml lines 1-112 (Tables 1-2)
10. ledger/proposals/IDEA-20260913-449d2b.yaml — lines 36-60, 380-700, 750-870 (C2 definition, minimal test, controls, falsification)
11. knowledge/findings/KN-FIND-006.md lines 1-60
12. experiments/EXP-DREG-001/runs/RUN-DREG-001-VALIDATE-N12-A/{command.txt, environment.json, raw-result.json, work/.../state.json (first 900 bytes)}; experiments/EXP-DREG-001/runs/RUN-DREG-001-VALIDATE-N15-A/raw-result.json
13. grep only (no content beyond matching lines): experiments/EXP-DREG-001/DREG_harness.py (no comparison found); src/crypto_autoresearcher/index_calculus/msolve.py lines 1-40 (prime-field msolve wrapper); experiments/EXP-DREG-001 for "modulus"
14. experiments/EXP-SEMBIN-473340/runs/RUN-SEMBIN-3a4248/manifest.yaml (run-manifest format template only)
15. /root/.ccr/README.md (proxy rules; github.com returned 403, PyPI reachable)

NOT read (N1): experiments/EXP-SEMBIN-35bf67/{stage0,stage1,stage2,stage3,runs,RESULTS.md} on any branch or PR #1827;
experiments/EXP-SEMBIN-7e1371/runs/**. No EXP-SEMBIN-35bf67 or EXP-SEMBIN-7e1371 implementation code was opened or used.
Directory listings of experiments/EXP-SEMBIN-*/runs/ were made to find a manifest template; the two blinded experiments were filtered out of the listing commands.
Not read: knowledge/literature/KN-LIT-fa346d.md, KN-LIT-e77232.md, knowledge/open-problems/KN-OPEN-d218ec.md, inputs/SEMAEV-2015-310 beyond the ranges above.
