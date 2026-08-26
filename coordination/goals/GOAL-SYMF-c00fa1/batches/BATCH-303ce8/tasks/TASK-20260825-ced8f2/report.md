# Pre-snapshot frontier correction addendum

Task `TASK-20260825-ced8f2` creates an overlay only. It does not modify either
original producer shard, any ledger record, or any research status.

## SHA-0 row added

Aoki and Sasaki's CRYPTO 2009 paper was opened and read at the named primary
URL. Table 1 on PDF page 3 reports a proper-preimage attack on the first 52 of
80 SHA-0 steps with time `2^157.1` compression-function computations and
memory stated as `negligible`. The same table reports the existing 52-step
point at time `2^156.6` and memory `2^15`.

The added row uses the existing row's comparison key. The two points are
Pareto-incomparable: the new point gives up time and reduces memory. The source
does not quantify “negligible” more precisely. Data, preprocessing, queries,
and success probability are not stated for this table row and therefore carry
`not_stated_by_source`; no values were inferred.

Exact locator: *Meet-in-the-Middle Preimage Attacks Against Reduced SHA-0 and
SHA-1*, Table 1 and its unit footnote, PDF page 3,
<https://www.iacr.org/archive/crypto2009/56770071/56770071.pdf>.

## Eligibility and count overlays

The logical view sets `LEGACY-MD4-PREIMAGE-NOPRECOMP` to
`frontier.is_frontier: false`. Its memory value remains null with
`unresolved_transcription`; this unresolved cost axis blocks frontier
eligibility. The correction does not supply, estimate, or infer a memory value.

The block-cipher shard summary overlay records exactly the Coordinator's Python
recount: 20 rows, 16 `author_reported_primary_text_read`, 4
`secondary_pointer_only`, and 0 rows with `is_frontier: true`. These are
internal mechanical counts only; no row was reinterpreted.

## Boundary attestation

This task performed no cryptanalytic search, attack execution, experiment,
status transition, or commit. The original producer task directories
`TASK-20260825-51dfe7` and `TASK-20260825-7d3441` were not changed. The only
created files are the four deliverables in this successor task directory.
