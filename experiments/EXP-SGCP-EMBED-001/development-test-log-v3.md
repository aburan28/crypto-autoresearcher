# SGCP source-repair v3 development test log

Status: DEVELOPMENT ONLY. The worktree was dirty, no approval lock existed, no
canonical runner command was issued, and no canonical certificate was written.

## Source bindings

- builder SHA-256: `125590041f53a2ec9913007b3edcbfcb968a971ee7e7c6980afc0130ba2c4049`
- main verifier SHA-256: `c7b3f2ae7a0eea4008a21aa10529f121236d7f65a5fa9f07e19358d6256a3933`
- scalar-index oracle source SHA-256: `a2e5af8c3fab960ec663c08fbdecf869262088ac5c5b628fb967d89a561b5fb6`
- scalar-index artifact SHA-256: `830e96d8e8095960d31e51c9af1d9afaf14990e209a7a113648cef79feb87f3e`
- focused tests SHA-256: `e223b604ee63e6141da852a5da0f5e04e01cef7db594824a505a3d42daf31bbb`
- proposed specification SHA-256: `0dc0cb7d7b1f8b8ee6c0c968992ef23453f1ab38d96b2344e07ab62db9cea61c`
- base Git commit: `f4c8109ce7ac01f7783c1af666d581c525ac8c61`

## Focused suite

```bash
PYTHONPATH=src python3 -B tests/test_sgcp_embed.py -v
```

Result: `22` tests passed in `49.005s`.

The suite covers strict JSON/integer gates, all frozen controls, exact builder
and verifier reconstruction, target-wise private audit data, fixed-point bytes,
operation attribution, isolated no-descendant runner role composition, scoped
scalar-material claims, the independent scalar-index oracle, and adversarial
certificate mutations.

## Repository suite

```bash
PYTHONPATH=src python3 -B -m unittest discover -s tests -p 'test_*.py' -v
```

Result: `62` tests passed in `61.919s`.

## Runner-protocol checks

- Generator and verifier were executed in a disposable development fixture
  with `-I -S -B` and child `RLIMIT_NPROC=0`.
- The verifier consumed a runner-shaped predecessor `raw-result.json`, manifest,
  and receipt and reported the exact predecessor SHA-256.
- `_verify_protocol_hashes` accepted all `16` proposed protocol files.
- `tests/test_records.py` accepted the `review_required` specification.
- `approved_by` remains null. These checks did not invoke the canonical runner.

## Scalar-index differential

The independently structured oracle reproduced:

| B | candidates | valid | conflicts | subsets | objective | outcome digest prefix |
|---:|---:|---:|---:|---:|---|---|
| 4 | 31 | 12 | 20 | 4096 | `(13,5,20,26)` | `8f95f52f` |
| 6 | 68 | 8 | 4 | 256 | `(7,4,17,20)` | `c571d463` |
| 8 | 124 | 14 | 53 | 16384 | `(7,4,14,21)` | `38f0c54a` |

It also exact-matched selected universe indices, formal witnesses, target-wise
raw/retained witness counts and histograms, and candidate/parent-pair density
accounting. This is optimizer implementation evidence, not ECDLP performance
evidence.
