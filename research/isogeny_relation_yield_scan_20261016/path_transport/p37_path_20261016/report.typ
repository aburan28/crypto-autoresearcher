#set page(paper: "us-letter", margin: 0.75in)
#set text(font: "New Computer Modern", size: 9pt)

= P37 base transport to check vertex 20
16 October 2026 | Conductor T-3406 | implementation observation

This bounded continuation carries the fixed P37 source `low_x` signed base from archived edge 4 to prespecified degree-7 check vertex 20. It records implementation observations only; no relation-yield, rank, ECDLP-cost, or hypothesis-status decision follows. The complete commands and raw logs are in `report.md` and this directory.

== Recorded checks

#table(
  columns: (auto, auto),
  inset: 6pt,
  [Saved chain], [21 checkpoints: source through edge 20],
  [New continuation], [Edges 5–20; process exit 0],
  [Independent replay], [20 edges; 64,000 point images; pass],
  [Terminal SHA-256], [`c7b4ef4b29ca188108c96fefaa357608f4d5c15283f0ffd8e60eabcb4aad8cc2`],
)

#image("edge_times.svg", width: 100%)

== Resources and boundary

The continuation recorded 345.33 s wall, 20.75 s user+system CPU and 229,146,624 B maximum RSS. The independent verifier recorded 19.87 s wall, 1.22 s CPU and 70,942,720 B maximum RSS. The chart uses per-edge internal elapsed values only; complete wall time and scheduler conditions are separate. A 420-second watchdog bounded the producer. P37 edges 21–256, the committed discovery targets, native-base yield, rank and complete same-point solver remain open.
