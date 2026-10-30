# F5 second-pass preparation

26 October 2026. Task TASK-20261026-26de77 is prepared for a frozen exact
panel. **No second-pass arithmetic panel or pilot has run.** Experimental
execution awaits root's exact Phase B release, the committed frozen protocol
and the successful real S3 checkpoint gate.

The proposed panel uses all four prior P-256 maps (degrees 3,5,11,11), eight
canonical source points, sixteen signed labels and six targets. Three
targets are constructed correctness controls, two use a fixed hash-to-point
law, and one is O. Each complete source relation set is compared with the
same labelled endpoint set. Membership, inverse transport, geometric pole
certificates and a coordinate-isomorphism control are retained separately.

Two actual algorithms are exported: the exhaustive affine source oracle and
the endpoint/Jacobian pair lookup. Their shared setup and unequal work scopes
preclude a method-cost comparison. No natural yield or scaling inference is
planned. See `derivation.md`, `literature.md`, `protocol.draft.json` and the
root-owned execution gates for exact assumptions and controls.

Future commands, from the repository root, after root releases the exact
source/protocol/checkpoint identities:

```text
python3 -B research/p256_factor_base_parallel_20261026/tracks/f5/run.py --out research/p256_factor_base_parallel_20261026/tracks/f5/runs/run-01 --seed 2026102605 --release research/p256_factor_base_parallel_20261026/runtime/releases/TASK-20261026-26de77.json
python3 -B research/p256_factor_base_parallel_20261026/tracks/f5/export.py research/p256_factor_base_parallel_20261026/tracks/f5/runs/run-01 --out research/p256_factor_base_parallel_20261026/tracks/f5/export-run-01.json
python3 tools/experiment_protocol.py check-export research/p256_factor_base_parallel_20261026/tracks/f5/export-run-01.json --protocol research/p256_factor_base_parallel_20261026/tracks/f5/protocol.json --verify-files
```

The proposed data will support fixed-domain exactness observations only.
All failure paths retain their output directory. No result, flow or current
PDF is fabricated before data. Root owns final report rendering and the PR.
