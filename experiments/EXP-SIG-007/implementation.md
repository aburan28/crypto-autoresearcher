# EXP-SIG-007 — implementation notes

## Why a staged instrument

The pinned SIG instrument (`analyze_syzygy_space` with `extract=True`) computes
the D5 Macaulay rank by a streaming Python-bigint echelon **with transformation
tracking**. At n=21 D5 (nb=42, nrows=279,048, ncols ≤ 974,982, expected rank
~2.7×10⁵) that needs ~25–40 GB — this is what killed EXP-SIG-005 RUN-n
(AGENTS rule 5: infrastructure censoring, not evidence). EXP-SIG-007 therefore
never builds the tracked echelon. All quantities are split into independently
checkpointed stages:

| stage | content | memory | method |
|---|---|---|---|
| S0 | build, filter, D3/D4 (extract), residual_4 (pinned+canonical), B3/B4, null D3/D4 control | <1 GB | pinned instrument, verbatim |
| S1 | D5 rows+colidx, K5 family, closure images F3/F4 (position lists), column adjacency | ~3 GB | pinned instrument + compact pickles |
| S2 | rankK5, A3_5, A4_5 | ~1 GB | **reduction-free union ranks on dense m4ri** |
| S3 | rank(M5) | ~3–8 GB | checkpointed block-staircase m4ri |

Then `extra_5 = (nrows − rank) − rankK5` and `residual_5 = extra_5 − A4_5`
(verbatim EXP-SIG-003/005 definitions).

## S2: union ranks as the primary method

Prior experiments computed `A3_5/A4_5` by canonical `full_reduce` mod K5 and
then *cross-checked* with the reduction-free union identity
`rank(K5 ∪ F) − rank(K5)` (control C6, which passed on every cell). Here the
union identity **is** the primary method: it is exact (rank of an explicit
matrix), reduction-free, and validated against the canonical-method anchors
(C9a: n=12 seed 2 → rankK5 2,093, A3_5 242, A4_5 444; n=15 seed 1 → 3,944 /
392 / 705; n=18 seed 1 → 6,650 / 578 / 1,026).

Dense m4ri echelons are staged: K5 first, then rref-basis ∪ F3, then
rref-basis ∪ F4 — each stage carries only the nonzero rref rows.

## S3: block-staircase rank engine

Algorithm copied from `src/h012c_block_m4ri.py` (sha256
`0eb38126…`, reference copy in `src/`): column sub-chunks, block-staircase
carriers `(P, H)` with the staircase property, `rank = Σ` per-chunk new
pivots (exact quotient argument). Differences from h012c, all recorded:

1. **Systems come from the SIG instrument** (`build_boolean_semaev`,
   stable_seed-based), NOT `h012_peel_rank.build_system` (which seeds its RNG
   differently: `seed0 + 1000·ti + n`). The DREG and SIG instances are
   different draws; SIG-series continuity requires SIG instances.
2. Rows/adjacency come from the pinned `tagged_macaulay` (same enumeration as
   `macaulay_export.macaulay_rows`, plus tags; vanishing products kept —
   none occur at these sizes).
3. Engine validation on SIG instances (C9b): n=12 seed 2 sem D5 must give
   rank 28,097 under two chunk sizes (4,000 with a mid-run resume; 12,000
   straight) — mirrors RUN-DREG-001-CONTROL-N12-PARTB plus a resume check.

h012c's own validation (rank 28,096/69,073/143,882 on its instances, matching
dense m4ri and peel+core) is inherited as algorithm-level evidence; C9b
re-validates the re-driven engine on a SIG instance.

## Checkpoint/kill discipline

- Harness cap ~280 s per Bash invocation; driver `--soft-cap 235` checked
  before every stage/chunk; every stage atomically checkpoints
  (`state.tmp` → `os.replace`).
- `cell` mode resumes at the first incomplete stage; `rank5` mode resumes at
  `state.json` + sha256-verified carries.
- A stage that exceeds its invocation is **censored_compute**
  (infrastructure, AGENTS rule 5 — NOT evidence).

## Budget reality (recorded up front)

DREG cost model (EV-DREG-001 §7, same machine class): n=18 sem D5 = 3,212 s
work; n=21 extrapolated 25,000–32,000 s (7–9 h). This task has 3,300 s total.
**S3 at n=21 is therefore expected to censor.** The deliverable is the honest
partial: gate + anchors, n=21 S0–S2 (new exact structural numbers:
rankK5, A3_5, A4_5, D5 support size), S3 progress + resume command.
