# TASK-20260907-75d1a5 — completeness of the Stage 2 exact-G protocol

Recorded: 2026-09-07. Role: coordinator. Goal: GOAL-ECDLP-001. Experiment: EXP-ECDLP-5cad48.

## Object checked

The eight-prime exact-G measurement ranked by `DEC-20260907-701e9e`. Text:

- `experiments/EXP-ECDLP-5cad48/amendments/v1_stage2_exact_g.yaml`

This receipt does not authorize the measurement. It does not classify W. It does not fit a.

## Verdict: complete enough to file, not authorized

The protocol names:

- eight archived Stage 2 cells and M grids, first curve only
- seven arms including quadratic_character and planted_theta
- exact fields G_exact, M_delta_exact, W_exact, min_q, cs_bound_exact
- whole-group FFT bucket_stats, no jackknife
- 168 required rows
- Stage 1 overlap on S2-P523 and S2-P1033 five shared arms
- Stage 0 overlap on S2-P65539 at M=40 five shared arms
- producer classification prohibition
- refuse-until-authorized
- proof_search_map
- certificate kind none
- claim-changing review plan path `review_plan_s2g.yaml` owning completeness, overlap, and a blind P2 re-derivation on S2-P523 at M=5

Predecessor SHA of `v1_stage1_cs_aligned_authorized.yaml` is `2f9fa7f13269b6a041fe171e5d61071a9da771c788da70d9ba71f8c17aebb888`. Execution authorized is false.

## What this receipt does not do

- Does not authorize `RUN-ECDLP-5cad48-S2G`.
- Does not classify W.
- Does not fit a.
- Does not authorize Stage 5 of EXP-ECDLP-a98ea9.
- Does not change H-ECDLP-07c7c6.
- Does not claim an official supported bound.
- Does not run a consume-only Stage 2 aligned CS audit.

Cited: DEC-20260907-701e9e, DEC-20260907-fb97c0, RUN-ECDLP-5cad48-S2, H-ECDLP-2ade73, EXP-ECDLP-5cad48, IDEA-20260904-f7d47d.
