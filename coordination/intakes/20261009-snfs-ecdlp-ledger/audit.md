# SNFS-ECDLP hypothesis-ledger intake audit — 2026-10-09

Disposition: file all 23 user-supplied records as `proposed` IDEA-* proposals
under RQ-ECDLP-002 / GOAL-ECDLP-001, with lineage to H-ECDLP-bd1572 (filed
earlier the same day from the same chat line) and its five EXP-ECDLP
contracts. This is an intake decision, not a novelty finding, not an approval,
and not an assessment that any record is correct. Nothing ran.

## What was done

- Source stored verbatim at `source.yaml`; every source field mapped onto the
  proposal schema (`manifest.yaml`, `field_mapping`); no field dropped.
- Immutable ids minted with `tools/allocate_id.py --next idea --date 20261009`
  and confirmed with `--check`; map in `id-map.yaml` and `manifest.yaml`.
- Campaign-unique seeds assigned per record (`manifest.yaml`,
  `seed_assignment`); the source left them unassigned by design.
- Harness-only fields authored per record: class, predictions,
  falsification conditions (the source's "falsified if" and "alive if"
  clauses carried as written), heuristic assumptions with validation routes,
  target complexity, proof-search map (filled on A3, D4, E1, E3; marked
  not applicable on the controls), confounders, dominated_by, sota_delta,
  prior_art against the known-results map.

## Overlap with existing records (merge lineage, do not rename)

| Source | Overlapping contract(s) | What the proposal adds |
| --- | --- | --- |
| B1, B2, C3 | EXP-ECDLP-15534c (formal-group defect uniformity, Smart control) | lift-independence and homomorphism checks, ramified arms, information test; canonical-lift arm; smoothness of the Teichmueller lift |
| B3, B4 | EXP-ECDLP-6dacdb (embedding-degree census, k*), EXP-ECDLP-2535ec (F_p^* positive control) | generalized-Jacobian identification; CADO polyselect Murphy-E comparison and exact ord_l(p) |
| B7 | EXP-ECDLP-28ad87 (genus-2 cover floor) | genus 3 and the descent-direction control |
| D1, D2, F1 | EXP-ECDLP-3e8403 (SNFS-field lift covering) | rank and height measurements; the r(log p, m) table over certified high-rank curves |

A design that extends one of these supersedes it under a new id; the
contracts above are not edited.

## Novelty labels

`tools/validate_ledger.py` refuses `known`/`adaptation` on a record with a
`recalled` citation, and no external source was read in this session, so
17 records are `unverified` whatever the source said; the source's label is
kept in `intake.source_novelty`. Five records whose sources are all in the
knowledge base are `known` (A1, B1, B2, B6, D3) and one is `adaptation` (A4).
A reviewer with retrieval tools should chase the `recalled` entries; that is
what they are for (AGENTS.md rule 9).

## What this intake does not do

- No `/design-experiment`, no hypothesis record, no DEC, no approval:
  GOAL-ECDLP-001 was at the approval capacity cap when this was written
  (`manifest.yaml`, `approval`), so the standing authorization cannot be
  exercised on these records until a slot opens or a contract is retired.
- No scientific claim: 13 records exceed the 8 KiB proposal advisory cap
  because the source's own experiment text is long; the cap is advisory.
