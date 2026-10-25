# Held-out confirmation candidate and interval tooling control

2026-10-22. This report records implementation and tooling observations only.
It makes no scientific verdict about graph-wide relation yield or ECDLP cost.

## Scope and source

The candidate analyzer follows the frozen study draft
[`PROTOCOL-original-draft.md`](../PROTOCOL-original-draft.md) and the candidate
discovery selection. It targets the fixed P29 and P37 graph strata and the
selected `low_x`, `mid_x`, and `random_x` factor bases. No confirmation arm
receipts exist here, so no curve comparison was calculated. The planned
receipt path is shown in [`confirmation_flow.svg`](confirmation_flow.svg).

## Implementation controls

`python3 -m unittest research/isogeny_relation_yield_scan_20261016/graph_confirmation_candidate_20261023/test_confirm.py -v`
passed four tests on this candidate checkout. The controls enumerate exact
interval endpoints for populations 5–20, check zero-count and infinite
ratios, exercise deterministic tie handling, replay an interval cache, and
reject a changed cache endpoint and changed receipt binding. These tests do
not exercise full P29/P37 confirmation receipts.

## Exact interval tooling measurement

[`benchmark-interval.json`](benchmark-interval.json) records one measured
calculation on an Apple M4 Pro, macOS 26.6, Python 3.13.1, from source
`exact_interval.py` SHA-256
`5fb49e17775d1a12806f32ddca05a078d4d2167fd529541e1d4f7d1a8057b0e4`.
The exact command was `python3 benchmark_interval.py > benchmark-interval.json`.
For population 81,640,511,860, draws 32,768, an illustrative observed count
2,048, and tail threshold 1/58,800, elapsed wall time was **44.834188750 s**.
The integer lower and upper population-success bounds were 4,661,659,633
and 5,569,195,061. The observed count is a calculation input, not a curve
measurement. This single timing has no spread and is not a whole-study
runtime estimate.

## Limits and next checks

The Coordinator must bind this source to a runnable confirmation plan after
validated discovery. The analyzer must then see every selected fresh-target
receipt; any missing or censored arm halts analysis. Full paired targetwise
differences and curve-by-base interaction remain to be implemented from
per-target raw occupancy records. No canonical scientific graph changed:
there is no confirmation evidence to add. Complete same-point ECDLP/rho costs
remain a later measured stage.
