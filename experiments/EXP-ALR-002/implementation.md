# Implementation - AutoLab R183 sparse-projector Prony locator

This is a provenance-pinned import of a verified AutoLab research package. The
destination verifier checks immutable hashes and the report's scoped admission
flags; it does not re-execute the transitive AutoLab R76-R183 implementation.

## Provenance

- Source repository: `https://github.com/aburan28/autolab`
- Upstream repository: `https://github.com/autolabhq/autolab`
- Source commit: `583225fe9224d3f2a3dc910d88108deeb5cb31b6`
- Source pull request: `https://github.com/autolabhq/autolab/pull/10`
- Source round and harness state: `R183`, `V132`
- Predecessor archive: `EXP-ALR-001`
- Import verifier: `experiments/EXP-ALR-002/verify_import.py`

## Copied Artifacts

| Artifact | SHA-256 |
|---|---|
| `frozen_m6_sparse_projector_prony_locator.json` | `8d020353811cf7cf47e7950fe14f7da1df74eafb7c904f7e0abcfd875ef48c4b` |
| `m6_sparse_projector_prony_locator_controls.json` | `9575764c7e662210b9f41ffe2783be3f6b95926f7b3d534e361401704b63366f` |
| `m6_sparse_projector_prony_locator_cost_ledger.json` | `c91e54b65c5068a3cada5b3f2237ec1f1228989d2115f22cfc2fd183cec27a6b` |
| `m6_sparse_projector_prony_locator_replay.json` | `2473d0295858506f0ec687c03831c5b345f726323e59486ef98f17b070ba168e` |
| `p1436_autoresearch_focus_harness_v132_result.md` | `bcc9f9a3429a5632734e8b79c848547a06d528ed92c02835cd0b0b299d1a4a03` |
| `p1553_m6_sparse_projector_prony_locator_probe_gate_r183.md` | `4544744eccc2050390b69bc377d6188e6e66b28c226c2840d0f607bc9330e67d` |
| `p1553_m6_sparse_projector_prony_locator_probe_parent_report_r183.yaml` | `28f0bf2f9f380944bf92ad2349eabd7fe230cf0e9d18574f3b09a84ac88a983c` |
| `p1553_m6_sparse_projector_prony_locator_probe_r183.py` | `202a28eade6a3d532c4f9f8cf6ae3e02c9a74da9bccc436069917204e511b53f` |
| `p1553_m6_sparse_projector_prony_locator_probe_report_r183.json` | `a2e746fa5159a3684d3f6913888ad9c6a1fd7983fcb9abbacc17e6d4ee5baae5` |
| `sparse_projector_prony_locator_applicability_r183.json` | `652e2a17148613d57d729200a3297948e9cebc898ce07992482a5bf3927e3be8` |
| `test_p1553_m6_sparse_projector_prony_locator_probe_r183.py` | `c44e54238b0599e30211a4035ed19858104272c11bfb866d2528e63343fac60e` |

## Reproduction Boundary

The producer imports R182 and its transitive AutoLab ancestors. Those ancestors
are bound recursively by the copied R183 parent report but are not duplicated
inside this EXP package. Re-executing R183 requires checking out the source
repository at the pinned commit. The destination verifier instead establishes
that the reviewed producer, outputs, tests, gate, parent receipt, and V132
verification summary arrived unchanged.

Source verification recorded 161 R183-plus-harness tests and 1,296 full ECDLP
tests passing, deterministic output replay, and 2,166 exact recursive bindings.
Those are imported receipts, not a destination-side re-execution claim.
