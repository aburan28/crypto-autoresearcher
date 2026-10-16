#set page(paper: "us-letter", margin: 0.7in)
#set text(font: "New Computer Modern", size: 9pt)

= Complete P29 checkpointed base transport
16 October 2026 | Conductor T-3394 | implementation observation

This report records the fixed P29 source `low_x` base carried through the archived 2,048-edge degree-7 walk. It makes no relation-yield, rank, ECDLP-cost, or hypothesis-status decision. The complete commands, raw logs, source hashes and limitations are in `report.md`.

== Bounded attempts

#table(
  columns: (auto, auto, auto, auto),
  inset: 6pt,
  [Phase], [Last edge], [Process status], [Independent replay],
  [First continuation], [1,907], [540 s watchdog], [1,907 edges, 976,384 point images],
  [Second continuation], [2,048], [exit 0], [2,048 edges, 1,048,576 point images],
)

The first process stopped at its watchdog without a partial checkpoint. The independently verified prefix bound a second attempt, which reached the prescribed endpoint. The final independent hash and point-map replay passed with terminal checkpoint SHA-256 `39d17f4eff4bd408f86b59c6a5cbf10980d99b3ddd5f4c3680c9e4b3607737f3`.

#image("edge_times.svg", width: 100%)

== Resource record and boundary

The second continuation recorded 82.18 s wall, 7.25 s user+system CPU, and 249,167,872 B maximum RSS. The full verifier recorded 42.44 s wall, 7.55 s user+system CPU, and 80,494,592 B maximum RSS. The first forced stop did not leave native resource totals. Per-edge times in the chart are internal diagnostics, not complete wall time. P37's remaining path, the committed discovery target stream, native-base yield, rank, same-point solving and matched rho remain open.
