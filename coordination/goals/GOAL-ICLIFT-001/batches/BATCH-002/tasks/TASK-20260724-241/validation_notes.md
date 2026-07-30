# TASK-20260724-241 validation notes

Independently recomputed the free-x slot set and polarisation Gram for
`p=7`, `b=[3,2,2,4,5,5,3]` using the frozen `is_square_poly` predicate loaded by
path and Sage group law. Slot count 33 and Gram rank 6 match the executor
record; height control `deg(num x(nS))=2n²` for `n=1..12` holds.

Re-ran `analyze_surface` on an anomalous surface
`b=[3,2,2,2,3,3,2]` and reproduced `span_rank=11` with `height_ctrl` true.
That reading exceeds Shioda–Tate’s `r≤8` and must not be interpreted as the
geometric Mordell–Weil rank. The primary gate metric (shortest relation
infinity-norm = 1, specialised to O) remains group-law verified.

Overall: `valid_with_findings`.
