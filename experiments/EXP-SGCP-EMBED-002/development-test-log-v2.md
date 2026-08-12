# EXP-SGCP-EMBED-002 development test log v2

**Status:** frozen-fixture implementation evidence only; no V2 family row and
no canonical run were created.

## Focused V2 controls

Command:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B -m unittest \
  discover -s tests -p 'test_sgcp_embed_family.py' -v
```

Result: `12/12 PASS` in `0.271s` after the final accounting mutation control.

The suite establishes, on abstract graphs and the frozen five-bit fixture:

- exact density-objective agreement with exhaustive enumeration;
- a serialized nonempty frontier and deterministic root-to-frontier replay;
- separate formal-multiset and ordered-tuple energy recounts;
- all four frozen B=4 density-cap optima;
- predecessor optimum regression and exhaustive conflict/closure equivalence;
- row-level semantic reconstruction and selected accounting mutations;
- refusal of both canonical and additional development curve execution.

## Predecessor regression

The broader `test_sgcp_embed.py` suite ran 22 tests in `46.594s`. Twenty-one
passed. The remaining locked-run composition test stopped before execution
because its reserved immutable directory
`experiments/EXP-SGCP-EMBED-001/runs/RUN-SGCP-EMBED-001` already exists. The
directory was preserved; this is an environment precondition, not a
mathematical or source mismatch.

## Independent review outcome

Theory, accounting, and red-team reviewers all returned `REVISE`. Their
accepted mutations and limitations are preserved in:

- `pre-run-theory-review-v2.md`
- `pre-run-accounting-review-v2.md`
- `pre-run-red-team-v2.md`

No additional curve-family row was spent. Version 1 remains at 17 of 18
authorized development rows, and canonical `maximum_runs` remains zero.
