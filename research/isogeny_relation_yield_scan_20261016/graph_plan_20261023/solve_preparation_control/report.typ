#set page(margin: 22mm)
#set text(size: 10pt)
= Solve-stage preparation control

This report records implementation-control observations only. It makes no claim about relation yield, rank, ECDLP time, or Pollard-rho performance.

== Control identity

- Control: `CONTROL-SOLVE-PREP-P37-v0000`
- Command: `python3 research/isogeny_relation_yield_scan_20261016/graph_plan_20261023/solve_preparation_control/run_prepare_control.py`
- Source commit: `fa022a9be60252f7a5cb29e534540bf9f3823d0c`; the working tree was dirty. Exact paths, host, Python, timings, and root digests are in `result.json`.
- Scope: P37 walk vertex 0; `low_x`, `mid_x`, and `random_x`; 1,600 x-orbits and 32,768 targets per arm. Deterministic public control roots were used, not scientific post-freeze roots.

== Recorded observations

Each arm produced the same endpoint `Q` and target-vector digest, with 32,768 targets. The three factor-base digests differ. Payload sizes below are recorded values from one preparation per arm (`n=1` each); they measure serialization size, not relation performance.

#figure(image("payload-size.svg", width: 100%), caption: [Prepared input payload bytes by base treatment; `n=1` per arm. Control `CONTROL-SOLVE-PREP-P37-v0000`.])

No relation collection, rank solve, scalar recovery, independent DLP verification, or rho trial ran. Scientific admission and post-freeze roots are absent.

An independent seed and group replay control for the P37 vertex-0 `low_x` input is recorded in `verify-result.json`. It passed on all 32,768 target rows and 3,200 signed base points with deterministic seed replay enabled. This replay covers input identity and group equations only.

== Reproduction

Runner: `run_prepare_control.py`. Replay runner: `verify_control.py`. Plot source: `draw.py`. Machine-readable receipts: `result.json` and `verify-result.json`. These files and the rendered report are kept together.
