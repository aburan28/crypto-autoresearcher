# Implementation - AutoLab R182 target subresultant

This is a provenance-pinned import of a verified AutoLab research package. The
destination verifier checks immutable hashes and the report's scoped admission
flags; it does not re-execute the transitive AutoLab R76-R182 implementation.

## Provenance

- Source repository: `https://github.com/aburan28/autolab`
- Upstream repository: `https://github.com/autolabhq/autolab`
- Source commit: `835c850bf2103e7c67f85614887a2bea9c6e6913`
- Source pull request: `https://github.com/autolabhq/autolab/pull/10`
- Source round and harness state: `R182`, `V131`
- Import verifier: `experiments/EXP-ALR-001/verify_import.py`

## Copied Artifacts

| Artifact | SHA-256 |
|---|---|
| `frozen_m6_gcd_equivalent_target_subresultant.json` | `29291879484cf68bc16b83e2341818a611bb0c529c53e135f33bc181f30d462e` |
| `gcd_equivalent_target_subresultant_applicability_r182.json` | `5f1700e9b00d6756daa58d38f36002e7f0dee704632f223de8f4bc55cfce620c` |
| `m6_gcd_equivalent_target_subresultant_controls.json` | `850099e9c6f538baea1f94b7d87dafbe8c2df7a83b3dcf9d47be9b233639b77f` |
| `m6_gcd_equivalent_target_subresultant_cost_ledger.json` | `0eb0f05465fc072c72b6cccc24105d420431eb53162a6d5042b135bdcb454121` |
| `m6_gcd_equivalent_target_subresultant_replay.json` | `bec170f0a0148e269b28c0499f7a8c65b20a3270a8f8dbfc41a0724d3e71e9ba` |
| `p1436_autoresearch_focus_harness_v131_result.md` | `47e7b2b328b93d4b2fcbb64773b654a930f2bbfd9c2a96de7a63963e89c3122c` |
| `p1553_m6_gcd_equivalent_target_subresultant_probe_gate_r182.md` | `960fbcdcae0867bc8b02786f81af9eb68ed337d2dfff9019e62c61248ca303fd` |
| `p1553_m6_gcd_equivalent_target_subresultant_probe_parent_report_r182.yaml` | `d83ffeed2d66b78ec40a7b14e3a89fd5a8940775d21f5c297c6105454032ba66` |
| `p1553_m6_gcd_equivalent_target_subresultant_probe_r182.py` | `0058a28e4c337df97cec7b2e87bb5cc16e18a5b47029ab72d12b852405875e15` |
| `p1553_m6_gcd_equivalent_target_subresultant_probe_report_r182.json` | `9a38150e9e7e0e41f455b000b4cda390aaff4f428c2828d5ffeed8a9781f7f5d` |
| `test_p1553_m6_gcd_equivalent_target_subresultant_probe_r182.py` | `37e7ced472a7eb2244e1539cb3248fd2e170bdec343a89a69b93ce9e05d39a7e` |

## Reproduction Boundary

The producer imports R181 and its transitive AutoLab ancestors. Those ancestors
are bound recursively by the copied R182 parent report but are not duplicated
inside this EXP package. Re-executing R182 requires checking out the source
repository at the pinned commit. The destination verifier instead establishes
that the reviewed producer, outputs, tests, gate, parent receipt, and V131
verification summary arrived unchanged.

Source verification recorded 162 R182-plus-harness tests and 1,283 full ECDLP
tests passing, deterministic output replay, and 2,141 exact recursive bindings.
Those are imported receipts, not a destination-side re-execution claim.
