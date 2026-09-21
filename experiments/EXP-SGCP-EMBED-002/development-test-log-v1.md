# EXP-SGCP-EMBED-002 development test log v1

**Status:** implementation evidence only; no canonical run

## Focused tests

The first focused run found one result-schema guard bug: an integer
`forbidden_final_edge_count` was incorrectly passed through a Boolean-only
check. The mathematical rows were not returned. The guard was narrowed to the
actual Boolean axiom fields and the suite was rerun.

Final command:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B -m unittest \
  discover -s tests -p 'test_sgcp_embed_family.py' -v
```

Final result: `8/8 PASS` in `0.201s`.

The suite covers:

- curve generation and all registered special-case filters at 5-8 bits;
- exact factor-base cardinality, sign symmetry, and deterministic predicates;
- branch-and-bound versus exhaustive graph fixtures;
- a forced nonzero-gap interval containing the exact optimum;
- all three frozen EXP-SGCP-EMBED-001 optimum tuples;
- all `2^12` graph/direct-closure outcomes on the frozen B=4 row;
- independent row reconstruction and rejection of an energy mutation;
- refusal of non-development execution.

## Development execution

One smoke row completed valid, followed by the 16-row bounded matrix in
`development/DEV-SGCP-EMBED-002-V1/`. The separately written verifier rebuilt
all 16 rows and independently proved all primary support optima.

## Boundary

The test and development runs do not satisfy the canonical source-freeze,
runner, multi-seed, four-null, or independent-review gates.
