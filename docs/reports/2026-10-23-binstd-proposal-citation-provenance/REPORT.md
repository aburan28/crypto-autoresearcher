# BINSTD proposal citation provenance correction

This is a source-reading correction to two archived proposals, not a new
experiment, performance measurement, or proof. The originals remain unchanged.
The [editable citation diagram](citation-graph.dot) and its
[SVG](citation-graph.svg) show the limited source chain; the [PDF](report.pdf)
contains the same diagram.

## Source and exact correction

I read the committed
[`KR-IC-73db3f`](../../../knowledge/frontiers/ecdlp/index-calculus/KR-IC-73db3f.yaml)
card. It calls the small-product-space factor-base choice a **heuristic** and
says smaller dimensions of `V^(i)` can lower Weil-descent degree and variable
count. Its four cited literature records are marked `abstract_read`; this audit
did not read their full papers or establish a measured solver improvement.

Each archived proposal, `IDEA-20261003-94078e` and
`IDEA-20261003-c9c6c3`, calls itself an adaptation but cites that card as
`recalled`. The validator rejects this combination. Each additive replacement
changes only `citations[4]`: it records the card as an internal source read by
Codex, narrows the citation claim to the card's heuristic scope, and names the
card and its upstream reading limit in `verified_by`. All other parsed fields
are identical to the archived proposal. The supersession registry binds each
original and replacement by SHA-256.

The focused structured comparison passed on both records. It also checked
the card's `heuristic` status, all four `abstract_read` source states, and
both registry hash pairs. A complete-tree `python3 tools/validate_ledger.py`
run on parent `f7408a231b` reported 120 unsuppressed errors in 36 paths.
The same command on PR head `6c08b90468` reported 118 in the same 36 paths.
An exact error-line comparison found only the two targeted citation errors
removed and no new error. Both validator invocations still exited 1;
neither the 1,210-entry legacy baseline nor frozen records changed. The
[delta receipt](validation.json), [parent log](validator-parent.log) and
[PR log](validator.log) preserve the full result. Repository CI is still
required on the final head; this local result is not a clean-ledger claim.

## Limits and graph state

The correction does not change the proposals' experimental contracts, data,
decisions, or novelty claim. It supports only attribution to the internal
heuristic card; it does not independently verify that card's upstream
literature. No numerical claim or established scientific relationship changed.
I searched canonical graph and report sources in `knowledge/` and
`docs/reports/` for both proposal IDs and the card ID and found no existing
graph that refers to them. The diagram here records the new provenance path;
other graphs and performance dashboards therefore need no update from this
metadata correction.
