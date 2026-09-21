# Experiment Contract: EXP-SGCP-EMBED-001 preflight, version 3a

Version 1 was rejected before execution. Its scoped specification negative and
concrete counterexamples are preserved in `pre-run-red-team-v1.md`.
Version 2 was also revised before execution; version 3 and the 3a monotonic
audit clarification received read-only mathematical GO.

## Hypothesis

The builder and an independently written verifier can faithfully instantiate
the SGCP-EMBED-001 formal objects and controls on only the generated 5-bit
prime-order curve.

## Null hypothesis

At least one fixture, source binding, control, formal closure, exact axiom
check, pruning result, or independently reconstructed field disagrees.

## Parameters

- curve: `p=19`, `a=2`, `b=9`, `q=23`, `G=(0,3)`
- factor-base sizes: `4`, `6`, and `8`
- policies: balanced-only, canonical closure, exact balanced-universe optimum
- P2 degree-two set: only submultisets forced by selected degree-four maxima
- P2 candidate universe: every distinct flattened pair of canonical degree-two nodes, not one canonical degree-four witness per output
- builder visibility: point coordinates and EC arithmetic, never scalar indices
- verifier visibility: independently enumerated complete scalar table
- final `4F+4F` join: measured for retention but absent from `star`

The full mathematical contract is
`notes/sgcp_embed_001_contract_20260717.md`. This preflight may not weaken its
formal definitions or claim its 10-12 bit retention criterion.

All controls are defined by
`control-registry-v2.json`, SHA-256
`cf07a4dedcc7d7895df7959aa809bee9fc8aefeff04a1ef643e7bf211173e5ca`.
Both implementations must exact-compare the complete registry.

## Metrics

Record exact raw witness supports, formal closures, evaluation collisions,
partial-operation edges, all model axioms, constrained labels and delta, both
relative and absolute final support, source loss, public-model bytes, charged
private-audit bytes, operation counters, complete search proof, memory, and wall
time.

## Positive controls

PC-FREE-MONOID, PC-CYCLIC-NO-WRAP, the fixed PC-EC-FOREST, and
PC-REPEATED-PRIME must pass.

## Negative controls

NC-BALANCED-ONLY, NC-ALL-WITNESSES, NC-DUPLICATE-TAG,
NC-COMPAT-MUTATION, NC-FINAL-EDGE, NC-B6-D2-COLLISION,
NC-B8-CANONICAL-LOSS, and NC-OPTIMIZER-FIXTURE must reproduce their isolated
registered behavior.

## Success criterion

All controls behave as registered, all three factor-base rows terminate, the
verifier reconstructs the complete public model and private audit exactly, and
no 6-12 bit row is executed. This establishes implementation readiness only.

## Falsification criterion

Any mismatch returns `valid=false`, preserves the first exact counterexample,
and blocks the full sweep.

## Reproduction command

Commands remain unauthorized until source hashes are frozen in
`implementation.md`. The eventual five-bit commands are:

```bash
python3 -B experiments/EXP-SGCP-EMBED-001/src/sgcp_embed.py \
  --contract notes/sgcp_embed_001_contract_20260717.md \
  --literature notes/structured_group_coordinate_predicates_literature_20260717.md \
  --toy-bits 5 --factor-base-sizes 4 6 8 \
  --output experiments/EXP-SGCP-EMBED-001/preflight/sgcp-embed-001-5bit.json

python3 -B experiments/EXP-SGCP-EMBED-001/src/verify_sgcp_embed.py \
  --contract notes/sgcp_embed_001_contract_20260717.md \
  --literature notes/structured_group_coordinate_predicates_literature_20260717.md \
  --input experiments/EXP-SGCP-EMBED-001/preflight/sgcp-embed-001-5bit.json \
  --output experiments/EXP-SGCP-EMBED-001/preflight/sgcp-embed-001-5bit-verification.json
```

## Claim boundary

`HYPOTHESIS`, `MODEL-BOUND`, and implementation preflight. No ECDLP, lower
bound for standard coordinates, exponent, rank, relation, descent, or
deployment claim is authorized.
