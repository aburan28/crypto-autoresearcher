#set page(paper: "a4", margin: (x: 17mm, y: 15mm))
#set text(font: ("Liberation Sans", "DejaVu Sans"), size: 9pt)
#set par(justify: true, leading: 0.6em)
#show heading.where(level: 1): set text(size: 13pt)
#show heading.where(level: 2): set text(size: 10.5pt)

= Matched legacy/repaired `s4_expr` rerun: run report

*Observation-only run record.* EXP-SEMAEV-93d5cc and its successors EXP-SEMAEV-88c46c and EXP-SEMAEV-6e9dcf; hypothesis H-SEMAEV-94dab2; goal GOAL-ECDLP-001; approvals DEC-20261018-a7a0fd, DEC-20261019-5b9240, DEC-20261019-ebf1dc. This report states what ran and what it recorded. It gives no verdict, support or weakening; the evidence review (TASK-20261018-83a561, then a decision record) does that.

== What ran

Every archived run whose code path calls `harness.semaev.s4_expr` was rerun twice, concurrently, on one host: arm *legacy* with `s4_expr` from the exact `semaev.py` bytes all those runs recorded (sha256 `53a23952…`, vendored), arm *repaired* with the current `harness/semaev.py` (sha256 `c417f194…`). Nothing else was substituted; programs, frozen instances, targets, seeds and caps are the archived ones. Host: this container, Linux x86\_64, 4 CPUs, CPython 3.13, sympy 1.14.0, Singular 4.4.1. The archive ran on macOS arm64 (MTIC, FIB) and with Singular 4.3.2 (ICINV). Supervisor: `tools/experiment_execution.py`; checker `implementation/check.py` (arm fingerprints, member hashes, re-extraction). Commits are each run manifest's `code.commit`; every manifest records `dirty: false`.

#table(
  columns: (1.25fr, 1.2fr, 1.5fr, 0.9fr, 0.8fr),
  inset: 4pt, stroke: 0.4pt + rgb("d9d8d2"),
  [*Cell*], [*Run*], [*Archived run*], [*Status*], [*Wall s*],
  [icinv-m4], [RUN-SEMAEV-9cab7b], [RUN-ICINV-e0cd8f-m3class (m4)], [validated], [2098],
  [fib-004], [RUN-SEMAEV-3e69b6], [RUN-FIB-004], [validated], [1816],
  [fib-005], [RUN-SEMAEV-4be606], [RUN-FIB-005], [validated], [1808],
  [fib-decision], [RUN-SEMAEV-894e27], [RUN-FIB-006C / 007 / 008], [validated], [9],
  [mtic-007], [RUN-SEMAEV-2a8498], [RUN-MTIC-007], [validated], [1511],
  [mtic-008], [RUN-SEMAEV-fcd67c], [RUN-MTIC-008], [validated], [1575],
  [mtic-010b], [RUN-SEMAEV-500a81], [RUN-MTIC-010b], [interrupted], [—],
  [mtic-010b], [RUN-SEMAEV-980e8c (88c46c)], [RUN-MTIC-010b], [interrupted], [—],
  [mtic-010b], [RUN-SEMAEV-0e5876 (6e9dcf)], [RUN-MTIC-010b], [validated], [1516],
)

The two interrupted attempts were killed by container restarts (00:37 and 01:45 UTC on 2026-10-19), 13 and 16 minutes in, before any aggregation; both are preserved as written, with no receipt, and are not results (amendments `AMD-EXP-SEMAEV-93d5cc-20261019-mtic010b-successor`, `AMD-EXP-SEMAEV-88c46c-20261019-successor`). Excluded by import analysis (never call `s4_expr`): RUN-MTIC-001..006, -009; RUN-FIB-001..003. RUN-MTIC-010 and RUN-FIB-006/006B are superseded in the archive by -010b and -006C.

== Controls

*CTRL-LEGACY-REPRO* (legacy rerun against the archive, frozen rules in `compare.py`): passed in every completed cell. ICINV 552/552 m4 records equal; FIB per-target (capped, basis size, basis degree, trivial) equal on all 200 + 75 (C16) and 75 + 15 (C20) common targets, `n_measured` differences 0; MTIC per-target tuples equal on all 25, 13 and 12 attempted targets, attempted-count differences 0. mtic-010b (RUN-SEMAEV-0e5876): regime, K\* and uncensored counts equal at 16, 20 and 24 bits, and K\* and capped pattern equal for both ablation bases (B = 52: 13/13 capped, B = 115: 12/12). *CTRL-ARM-FINGERPRINT* and *CTRL-REEXTRACT* passed in every completed trial (check.py exit 0): legacy S4 has free symbols {x1, x2, x4}, total degree 16, 227 terms; repaired {x1, x2, x3, x4}, degree 12, 439 terms, residue 0 on the EXP-SEMAEV-a097b5 witness; every FIB spawn child logged its arm's module and source hash.

== Recorded values (archived / legacy rerun / repaired rerun)

#table(
  columns: (1.1fr, 2.2fr, 1.2fr, 1.2fr, 1.4fr),
  inset: 4pt, stroke: 0.4pt + rgb("d9d8d2"),
  [*Cell*], [*Quantity (measured)*], [*Archived*], [*Legacy*], [*Repaired*],
  [icinv-m4], [m4 `s4_support` values (records)], [227 ×546, 225 ×4, 210 ×2], [same], [439 ×550, 391 ×2],
  [icinv-m4], [m4 singular locus dim/degree], [2/60 ×552], [same], [2/39 ×552],
  [icinv-m4], [gauge m4 agreement], [276/276], [276/276], [276/276],
  [fib-004], [C16-1 solved / capped of 200], [200 / 0], [200 / 0], [200 / 0],
  [fib-004], [C16-1 median Groebner s], [0.0279], [0.0579], [3.678],
  [fib-004], [C16-1 basis size (counts)], [3: 16, 4: 184], [same], [14–19 (5 values)],
  [fib-004], [C16-2 measured (all capped), stop], [75, curve cap], [75, curve cap], [31, run cap],
  [fib-005], [C20-1, C20-2 measured (all capped)], [75, 15], [75, 15], [75, 15],
  [fib-decision], [C16-1 Spearman rho\_s (p)], [−0.024 (0.742)], [−0.097 (0.171)], [−0.366 (< 1e−4)],
  [fib-decision], [curves passing the gate; gate], [none; fail], [none; fail], [none; fail],
  [fib-decision], [C16-1 predictor-cost ratio], [8.6e−6], [4.2e−6], [6.5e−8],
  [mtic-007], [16-bit attempted / capped / cancelled], [25/25/25], [25/25/25], [25/25/25],
  [mtic-008], [20-bit; 24-bit attempted / capped], [13/13; 12/12], [same], [same],
  [mtic-010b], [regime, K\* (all accountings)], [(i), infinite], [(i), infinite], [(i), infinite],
)

Derived values: medians are of the recorded per-target `cost_seconds`; the C16-1 median ratio repaired/legacy is 3.678 / 0.0579 ≈ 63.5 (legacy/archived ≈ 2.07, host speed). The p-values are the recorded 10,000-replicate permutation values (p reported as 0.0 for the repaired arm). The legacy-rerun versus archive spread of rho\_s on identical code (0.073) is the recorded timing-noise A/A for that statistic; the repaired-versus-legacy difference is 0.269.

#figure(image("figure-icinv.svg", width: 100%), caption: [ICINV m4 invariants per record (552 = 276 curves × base and gauge twin) for RUN-ICINV-e0cd8f-m3class (archived) and RUN-SEMAEV-9cab7b (both arms). Counts are recorded values.])

#figure(image("figure-fib.svg", width: 100%), caption: [Left: recorded Groebner seconds per C16-1 target, n = 200 per arm (RUN-FIB-004; RUN-SEMAEV-3e69b6), log scale, bar = median. Right: recorded C16-1 Spearman rho\_s (RUN-FIB-006C; RUN-SEMAEV-894e27) against the frozen EXP-FIB-001 bands: |rho| < 0.2 falsification band, 0.2–0.4 inconclusive, gate at −0.4.])

== Frozen conclusion fields (compare.conclusion\_fields)

Repaired arm differs from the archive in: icinv-m4 `s4_support` value set and singular-locus value set (gauge agreement and the class-versus-control comparison unchanged). Equal to the archive in every other frozen field: FIB `resource_exhaustion` and all-capped flags for all four curves; correlation gate, curves passing, per-curve status, cost gate, gate and RUN-FIB-008 outcome; MTIC all-capped and median-at-cap flags at 16, 20 and 24 bits; MTIC-010b regime and K\* per accounting at 16, 20 and 24 bits and K\* for both ablation bases. Outside the frozen fields (recorded, not pre-registered as conclusion fields): the C16-1 rho\_s moves from the EXP-FIB-001 falsification band (|rho| < 0.2) into its inconclusive band (0.2 ≤ |rho| < 0.4), and C16-2 measures 31 instead of 75 targets because the slower C16-1 solves consume the 1800 s run cap.

== Limits

Toy tier only. Wall-clock caps make every capped count host-dependent; they reproduced exactly here, which is a property of this host. No cost, speedup or ECDLP claim; no hypothesis status changes. Sources: each run's `manifest.yaml`, `raw-result.json`, `arms.tar.gz` (member hashes in `arms-manifest.json`) and `execution-receipt.json`; `plot-data.json` and `chart.py` here reproduce both figures.
