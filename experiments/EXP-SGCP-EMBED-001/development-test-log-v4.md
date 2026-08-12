# SGCP source-repair v4 development test log

Status: DEVELOPMENT ONLY. No approval lock, canonical run, certificate, or
verification output was created.

## Source bindings

- builder SHA-256: `0580aad43fc1cc0a9bce11b34cce5626edade57ff902b6ad53ab31db0216d1b1`
- main verifier SHA-256: `931d7bd240dc6565d22ae85385d253a7b9ab20b123198ab133df43ef68bb4337`
- scalar-index oracle source SHA-256: `a2e5af8c3fab960ec663c08fbdecf869262088ac5c5b628fb967d89a561b5fb6`
- scalar-index artifact SHA-256: `830e96d8e8095960d31e51c9af1d9afaf14990e209a7a113648cef79feb87f3e`
- focused tests SHA-256: `10b2b076874c12be600faea6170f62a5a76a8ee8b91d88a9a287e57a23d95168`
- proposed specification SHA-256: `458de0ce9aeb3225e91d0e1f0cbe99a3e16e0f34b264e142d1ba4fe901a55bd4`

## Focused suite

```bash
PYTHONPATH=src python3 -B tests/test_sgcp_embed.py -v
```

Result: `22` tests passed in `55.259s`.

The frozen-plan composition test loads exact generator/verifier argv from the
specification. It validates relative invocation-token preservation and rejects
an otherwise equivalent absolute-token receipt mutation.

## Repository suite

```bash
PYTHONPATH=src python3 -B -m unittest discover -s tests -p 'test_*.py' -v
```

Result: `62` tests passed in `109.255s`.

## Additional v4 controls

- Literal raw and retained target-to-pair maps exact-match the coordinate and
  scalar-index reconstructions.
- Reversing one retained pair is rejected even when target counts are unchanged.
- An in-range diagnostic integer with a recomputed receipt remains accepted,
  and `covert_scalar_encoding_excluded` remains false.
- An oversized diagnostic integer remains invalid.
- Experiment record/schema validation passed `3/3`.
- Proposed protocol hashes passed `16/16`.

These controls establish implementation behavior only. They do not establish
an approved run, useful ECDLP relations, matrix rank, descent, or a rho speedup.
