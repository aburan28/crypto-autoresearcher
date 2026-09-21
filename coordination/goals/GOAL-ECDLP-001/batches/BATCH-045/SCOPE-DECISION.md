# BATCH-045 scope decision — one superseding EXP-IT-001 repair-5

Opening authority: `DEC-20260803-001`, implementing the durable
`GOAL-ECDLP-001.next_action` after BATCH-044.

This batch authors exactly one superseding immutable amendment
`PA-IT-001-v3-rc45-repair-5` that closes remaining review blockers from
`RT-20260803-005` / `EV-IT-006` before any Executor or experiment run:

1. **RT-044-Y1** — make the frozen amendment `yaml.safe_load`-clean (quote
   acceptance scalars that embed colons).
2. **RT-044-M2** — ship a present
   `experiments/EXP-IT-001/implementation/recompute_null_plant_from_ledger.py`
   in the proposal snapshot and keep it listed in
   `implementation_archive_manifest` (no false-presence claim).

Preserve substantive RC-44 closures of RT-314-B1..B3 and RC-43 command /
certificate / comparator / Pareto wording. Then obtain one new independent
`review-adversarial`/xhigh session.

No implementation beyond the null-recompute helper required for M2 presence,
no Executor admission, no experiment run, no hypothesis transition, no
support/rejection/SOTA/novelty/closure claim. Claim ceiling remains
experiment-design only. `GOAL-ECDLP-001` stays `active`; `H-IT-001` stays
`specified`.

The amendment must be non-destructive: no edits to
`experiments/EXP-IT-001/specification.v3.yaml`, prior overlays, existing run
artifacts, or ledger decisions.
