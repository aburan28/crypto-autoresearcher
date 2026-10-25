# Solve-stage preparation control

This report records implementation-control observations only. It does not claim relation-yield, rank, ECDLP, or Pollard-rho performance.

## Control identity

- Control: `CONTROL-SOLVE-PREP-P37-v0000`
- Purpose: exercise the additive finalist solve-stage input preparer on the P37 walk's vertex 0.
- Command: `python3 research/isogeny_relation_yield_scan_20261016/graph_plan_20261023/solve_preparation_control/run_prepare_control.py`
- Source commit: `fa022a9be60252f7a5cb29e534540bf9f3823d0c`; working tree was dirty and the exact starting paths are in [result.json](result.json).
- Environment and wall/CPU/RSS measurements: recorded in [result.json](result.json).
- Roots: fixed deterministic control values derived from the labels `base-control`, `target-control`, and `verifier-control`; digests are recorded. They are not the post-freeze scientific roots.
- Workload: 32,768 targets per each of `low_x`, `mid_x`, and `random_x`; 1,600 base x-orbits per arm.

## Observations

All three preparations produced the same endpoint `Q` and the same target-vector digest. Each produced the expected 32,768 targets. The three base digests differ. The raw prepared-input digests and byte sizes are in the machine-readable result. The plot shows those recorded payload sizes (`n=1` preparation per arm); it does not measure relation yield.

No relation collector, rank checker, Sage linear algebra, scalar recovery, independent DLP verification, or rho baseline ran. No Coordinator-approved admission or scientific seed stream was used. These missing measurements remain open.

## Reproduction and files

The runner is [run_prepare_control.py](run_prepare_control.py); the plot source is [draw.py](draw.py), and its rendered SVG is [payload-size.svg](payload-size.svg). The report source is [report.typ](report.typ), with the rendered [report.pdf](report.pdf).

An independent seed and group replay of the P37 vertex-0 `low_x` solve input is also recorded in [verify-result.json](verify-result.json), produced by [verify_control.py](verify_control.py). It verified all 32,768 target rows and 3,200 signed base points with deterministic seed replay enabled. It checks input identity and group equations only; relation collection and solver behavior remain untested.
