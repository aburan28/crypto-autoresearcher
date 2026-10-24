# Frozen twist-subgroup pairing screen

Frozen 2026-10-23 UTC before computing this screen. The historical labels and
earlier twist factorizations are known, so this is a retrospective arithmetic
comparison, not a blinded selection test or an ECDLP cost experiment.

## Question and exact inputs

Under the stipulated premise that the generator evaluated all eleven omitted
curves, could a large prime subgroup on their *quadratic twists* have a small
pairing embedding degree that distinguishes them from published controls?

Use the eleven seed-level classes in
`research/nist_seed_skipped_curves_20261016/assessed.json` and ten published
controls in its `traits.json`, with full EC1 UIDs. Use only the completed prime
factorizations in `research/nist_seed_selection_deep_20261016/twist_factor_probe.json`,
the P-224 block-1485 `research/nist_seed_selection_followup_20261016/verification.json`,
and the two later factor receipts under
`research/nist_seed_commonality_20261023/factor_runs/`. The inherited
primality and product checks are documented in the corresponding reports.
Recompute every factor product against the archived exact twist order and
fail on a missing class, duplicate key or mismatch. Count the two isomorphic
P-224 coefficient signs once.

## Declared arithmetic and controls

For every certified prime factor `ell` of the twist order with
`ell >= 2^80`, test `pow(p,k,ell)==1` for `1 <= k <= 20` (the historical
small-degree range) and separately for `1 <= k <= 1000` (a bounded
exploratory extension). Record the first hit and factor bitlength, or
`>bound`; this is an exact negative within each finite bound, not the full
order `ord_ell(p)`. Report whether *any* qualifying factor hits each bound,
and the minimum hit if so. Also report the largest certified factor's result
regardless of whether other large factors exist. Compare all eleven omissions
with the eight same-field published controls in 25 within-field pairs; P-384
and P-521 are retained but have no omitted same-field pair. No extra cutoff
or feature is added after inspection.

Controls: `ell=7,p=2` must first hit at `k=3`; `ell=11,p=3` first hits at
`k=5`; `ell=7,p=3` must have no hit by `k=3` and first hit by `k=6`.
Wrong factor products and a duplicate class key must be rejected. A separate
verification recomputes every recorded modular result and the 21 twist-order
products. Python version, source digests, command, outputs and exceptions are
retained.

## Inference and stop

A hit on a twist factor is a property of that twist subgroup, not the source
prime-order ECDLP subgroup. An attack consequence needs a concrete
unvalidated-input protocol exposing reusable secret multiplication on twist
points, the observable output, subgroup size, pairing transfer and complete
cost. `ell < 2^80` is outside this declared screen, and a degree greater than
1000 remains unknown. Even a perfect omitted-only split would be a candidate
historical rule, not attribution without original code/logs. Stop after all 21
classes, the two fixed bounds, and the declared pairwise comparison. Preserve
the script, JSON receipt, Markdown report, editable chart and inference
diagram, SVGs, and inspected PDF.
