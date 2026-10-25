# Checks run on 2026-10-25 in the sparse worktree (origin/main 0b38ac1157 + this change)

| check | command | result |
|---|---|---|
| known-results map | `python3 tools/build_frontier_map.py --check` | OK: 57 rows (30 index-calculus) — `frontier_map_check.txt` |
| lead atlas | `python3 tools/lead_atlas.py --check` | OK: 147 leads; warnings only about `crypto` evidence paths not checked out here — `lead_atlas_check.txt` |
| knowledge corpus | `python3 tools/build_knowledge_index.py --verify-corpus` | "knowledge corpus builds cleanly" (INDEX.md is generated, not committed) |
| source index | `make sources` then `python3 tools/build_source_index.py --check` | regenerated SOURCES.md / sources.json; up to date (8114 literature entries) |
| identifiers | `python3 tools/allocate_id.py --audit` | none of the 17 new ids malformed or duplicated (29 pre-existing malformed ids unrelated) |
| ledger | `CRYPTO_AR_ALLOW_SPARSE=1 python3 tools/validate_ledger.py` | 104 new errors, all pre-existing on origin/main (IDEA-20261003/20261016 prior_art blocks, TASK-20260910/20261003/20261017 review plans and budgets, RUN-ICPERF-943efa manifest); zero mention any record of this change — `validate_ledger.txt` |

The worktree is sparse (`.claude/` and `.mcp.json` excluded because the session sandbox cannot write them), hence the `CRYPTO_AR_ALLOW_SPARSE=1` run; the 65 off-disk tracked files are all under `.claude/` plus `.mcp.json`, none a ledger record.
