# TASK-20260731-121 — EXP-IT-001 RC-27 protocol amendment (B-5–B-8)

**Goal:** GOAL-ECDLP-001  
**Batch:** BATCH-027  
**Amendment:** PA-IT-001-v3-rc27-b5-b8  
**Parent v2 freeze:** `285e533e`  
**Queue amend:** QUEUE-AMEND-20260731-016  
**Author session:** fresh (did not author PA-IT-001-v2)

## Disposition

Authored specification.v3.yaml + PA-IT-001-v3-rc27-b5-b8 discharging B-5–B-8,
retaining B-1. No run. No Executor. H-IT/H-DS/H-IC/H-STR untouched. BATCH-026
CI not cancelled. Toy ceiling.

## Discharge summary

- **B-1 retained:** d=3; H_min; F_hit tree-ball; HEUR pre-search schema.
- **B-5:** N_MAP-IT-001-v3; h_max=256; N*=min(Cand); detectors on N*.
- **B-6:** R_xfer := min over certificate-bearing paths; BFS by increasing j.
- **B-7:** NULL-IT-NEIGHBOR-v1 XOR 3-regular; algorithm id in packaging hash.
- **B-8:** Plant injection + plant_detected via raw-ledger recompute.

## Next

TASK-20260731-122 snapshot; then independent re-review TASK-123 (do not self-review).
