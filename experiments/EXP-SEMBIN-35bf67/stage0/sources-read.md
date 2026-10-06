# Stage-0 sources-read list (DEC-20261005-c83e5a N1)

Recorded at Stage-0 freeze, before any Stage-1 code or output existed.

Read (in full unless noted):

- CLAUDE.md (auto-loaded), docs/agent-runtime-core.md, agents/executor.md
- docs/evidence-and-reproducibility.md (reproduction-package and manifest sections)
- ledger/handoffs/TASK-20261002-530540.yaml
- ledger/decisions/DEC-20261005-c83e5a.yaml
- ledger/decisions/DEC-20261002-99c798.yaml
- experiments/EXP-SEMBIN-35bf67/specification.yaml
- ledger/hypotheses/H-SEMBIN-d895d9.yaml
- ledger/proposals/IDEA-20260913-9ba7fc.yaml
- ledger/proposals/IDEA-20260913-449d2b.yaml
- inputs/SEMAEV-2015-310/tables.yaml
- inputs/SEMAEV-2015-310/paper_fulltext.md lines 530-659 (Section 4.5 / 4.5.1) and a grep for
  random / sparse / irreducible / preferable
- experiments/EXP-DREG-001/analysis.md, experiments/EXP-DREG-001/specification.yaml
- experiments/EXP-DREG-001/runs/RUN-DREG-001-VALIDATE-N15-A/{command.txt, manifest.yaml (lines 1-80),
  work/*.json, work/*/state.json}
- src/semaev_tree.py (full), src/h012_peel_rank.py (lines 1-230: boolean_null, semireg_rank_pred,
  peel_and_rank start, build_system, main start), grep of src/h012c_block_m4ri.py imports/defs

Not read before freeze:

- experiments/EXP-SEMBIN-7e1371/** (not opened at any point before freeze)
- ledger/decisions/DEC-20261004-df2986.yaml (not opened; known only through the
  DEC-20261005-c83e5a N2 paraphrase of its M4RI note)
- RUN-SEMBIN-5ed13e, RUN-SEMBIN-9bb990 (not opened)
- knowledge/literature/KN-LIT-fa346d.md, KN-LIT-e77232.md, knowledge/open-problems/KN-OPEN-d218ec.md,
  ledger/proposals/IDEA-20260913-9c54f9.yaml (declared inputs; not needed for Stage 0 and not opened)

No EXP-SEMBIN-7e1371 code is used for either rank arm.
