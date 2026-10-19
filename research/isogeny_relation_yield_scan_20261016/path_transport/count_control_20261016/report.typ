#set page(paper: "us-letter", margin: 0.75in)
#set text(font: "New Computer Modern", size: 9pt)

= First check-vertex targetwise count control
16 October 2026 | Conductor T-3387 | public implementation control

This report records observations only. It makes no relation-yield advantage, ECDLP-cost, or hypothesis-status decision. The full report, commands, source hashes, inputs and raw logs are in `report.md` and this directory.

== Fixed workload

P29 uses 512 signed source-base points transported through degree-7 edge 8; P37 uses 3,200 through edge 4. Each source/destination pair receives the same 128 deterministic public coefficient labels. The pair of prepared inputs in each stratum was built from independently replayed graph checkpoints. The separate C++ ordered-count oracle then enumerated every base-point pair and probed each target. Source code commit: `90f5ac1c94`; run revision: `94efd47f02ff21671b895d561876e06c81fee8d2`.

== Recorded counts

#table(
  columns: (auto, auto, auto, auto),
  inset: 6pt,
  [Endpoint], [Targets], [Nonempty], [Ordered relations],
  [P29 source], [128], [15], [90],
  [P29 edge 8], [128], [15], [90],
  [P37 source], [128], [7], [48],
  [P37 edge 4], [128], [7], [48],
)

The P29 source/destination count files have identical SHA-256 `d7c0e65b...fae55`; the P37 files have identical SHA-256 `f799d1cd...4d473`. Every target count matches, including zeros. These 128 fixed labels are control points and are excluded from the later discovery sample.

#image("counts.svg", width: 100%)

== Resources and limits

The four counter processes exited zero. Native `time -l` reported P29 source/destination wall times 1.19/1.08 s and maximum RSS about 9 MB; P37 wall times 66.11/79.38 s and maximum RSS about 288 MB. P37 CPU user+system was 3.29/4.27 s. The wall/CPU gap lacks a load trace or repeats, so it is diagnostic only. A 300-second process watchdog was applied; no memory kill guard was installed. Exact native logs are retained.

The graph-wide protocol remains a draft. Full-path transport, committed discovery targets, native base comparison, rank, same-point solves and matched rho remain separate requirements. The prior graph diagrams were checked and remain accurate for path geometry; this figure carries the new count data.
