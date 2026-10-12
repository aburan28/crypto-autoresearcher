# Solinas point-distribution measurement

Whole-curve measurements over prime fields. See the frozen [protocol](PROTOCOL.md)
for populations, independence units, controls and limitations. This task does
not request or recover scalars. Historical number-field and ML pilots are
separate tasks and are unchanged.

From the repository root, using Python with NumPy and SciPy installed:

```sh
python -m unittest discover -s tasks/solinas_point_distribution/tests -v
python tasks/solinas_point_distribution/run.py --output tasks/solinas_point_distribution/runs/point-distribution-20261012
python tasks/solinas_point_distribution/verify.py tasks/solinas_point_distribution/runs/point-distribution-20261012
python tasks/solinas_point_distribution/analyze.py tasks/solinas_point_distribution/runs/point-distribution-20261012
```

The first command checks mathematical formulas, production matching and
statistical independence units. The runner reads the existing public NIST
curve pool from EXP-ECDLP-5184f7 / RUN-ECDLP-d0e449. It saves the exact source
hashes, input preparation, environment and all field artifacts. A different
output directory is required for a new measurement; completed results cannot
be overwritten. `progress.json` is a live derived view.

Each `.npz` file is loaded with `allow_pickle=False`. Coordinates are big-endian
bytes, with width ceil(bit_length(p)/8). Uniform weights are 0, 1 or 2. Windows
are determined by saved start coordinates and their length. Census masks use
little-endian bit order, truncated to p; set weights to twice the mask and to
one at the separately recorded cubic roots. Isomorphic companion masks are
reconstructible from the first census by the recorded permutation. No private
key, scalar truth or target point dataset exists in this task.
