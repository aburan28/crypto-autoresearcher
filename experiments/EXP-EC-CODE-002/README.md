# EXP-EC-CODE-002

Search for target-aware multiplication-map features that rank **partial** factor-base supports by whether they extend to a valid 3-point decomposition.

This experiment is stacked on `EXP-EC-CODE-001` and deliberately forbids the full-support determinant, completion by group addition, and scalar/discrete-log information from feature extraction. Exhaustive group addition is used only to construct evaluation labels.

## Run

Quick smoke run:

```bash
python3 experiments/EXP-EC-CODE-002/src/rank_partial_supports.py --quick \
  --output experiments/EXP-EC-CODE-002/results/quick.json
```

Full toy sweep:

```bash
python3 experiments/EXP-EC-CODE-002/src/rank_partial_supports.py \
  --output experiments/EXP-EC-CODE-002/results/full.json
```

## Interpretation

The first-pass runner screens invariant rank/intersection features from shortened `L(4O)` evaluation spaces and their Schur products. Dimension-only features are retained as negative controls because `EXP-EC-CODE-001` found them constant on its original toy instance.

A feature is interesting only if it enriches true partial supports on held-out curves and survives basis-change/random-code/arbitrary-syndrome controls. Even then, it is not an ECDLP speedup until an end-to-end relation generator beats exhaustive support search after all feature and preprocessing costs are charged.
