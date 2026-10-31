# n=43 polynomial00: retained terminal closure observation

The first fixed n=43 polynomial-basis input has **zero ordered Boolean solutions** by the separate exhaustive counter. The degree-four producer reported `W4_one 1` and `closure_contains_one`, so it emitted no noncontainment certificate. This is a terminal producer observation, not an independently checked identity witness or a rigorous upper bound on the last fall degree.

The [public terminal evidence](../../archive/fresh-n43-poly-00.terminal.publication.json) contains the original system, producer arguments and transcripts, result, exact-count record and inference record. Its gzip bundle was read back and hashed through anonymous HTTPS and the content-addressed S3 store. The [machine-readable row](../../validation/n43-poly00-publication-001/result.json) pins the raw result, count and inference hashes. The reusable [publisher](../../publish_terminal_row.py) accepts only a completed `closure_contains_one` row, checks every producer artifact and the canonical inference link, and refuses a lower-bound inference.

This is one completed row of the frozen 20-input n=43–44 panel, which is still running on the remaining original inputs.
