# Additive repair of the 2026-09-07 ledger integrity failures

Authority: `DEC-20260907-44b7d9`, under the user's request to fix the reported
issues and open a PR. Original diagnosis: 50 errors across 24 paths, reproduced
at base `7553db09ac5d57885163886e043e75e88857ca46` in `validation-before.log`.
No experiment was run and no hypothesis or goal status changed.

| Original package | Errors | Correction |
| --- | ---: | --- |
| ECRANK evidence metadata and run references | 14 | Hash-pinned replacement `EV-ECRANK-469594`, neutral and unverified; original malformed ID and file remain; eight run references resolve through their canonical replacements. |
| ECDLP 5cad48 Stage 2 manifest | 8 | Source-backed fields added in a replacement, with missing execution revision/dirty state explicitly null and `completed_invalid`; directional evidence is barred. |
| Five a98ea9 manifests | 5 | Canonical field mapping; exact multiline Git status strings escaped without changing their values; original gate failures retained as invalid outcomes. |
| Six bbb42f raw companions | 6 | Byte-identical copies of the original `results.json`, which each original manifest names as its result artifact. |
| Eight ECRANK run manifests | 8 | Canonical wrapper and `certificate.kind: none` for construction/control observations. Original measurements and producer assertions remain unchanged. |
| MLKEM RT-CTRL-1 package | 4 | Command/environment extracted from original manifest; terminal receipt copied verbatim as operational raw output; no solve certificate claimed. |
| SSI cost reconstruction package | 4 | Command extracted from original manifest and exact `.txt` log copies; no solve certificate claimed. |
| ECRANK checkpoint | 1 | Canonical `batch_checkpoint` wrapper without changing the original fields. |

`artifact-mapping.json` records every new run/schema/companion artifact, its
SHA-256, and the original source hashes. All original source bytes are retained.
Both supersession registries pin originals and replacements. No error baseline,
legacy inventory, frozen protocol, dispatch queue, or H3 claim is changed.

The MLKEM raw alias is a terminal lifecycle receipt, explicitly covered by the
RT-CTRL-1 frozen metrics and stopping rule. Its `worker_result_exists: false`
remains visible. It is not a completed BKZ result or a claim about ML-KEM security.

The S2 source package contains command/environment/parameters/timing/raw output,
but no executing revision or dirty-tree receipt. `stage2.py` defines `_git_info`
without calling it in the inspected main path. The schema repair does not
replace the missing execution fact with a snapshot commit. The original
producer's `status: valid` is retained only under `original_producer_assertions`;
the canonical replacement is invalid for evidence use until authentic execution
provenance is recovered. This is an integrity disposition, not a mathematical
negative or an H3 result.

The malformed ECRANK evidence's reported success/control flags are preserved
as producer assertions, including its deferred independent verifier work.
Adding missing metadata does not affirm these claims or discharge that review.

The local Coordinator design disposition is preserved in
`coordinator-disposition.md`; its pending identifier check was subsequently
completed successfully for `TASK-20260907-88f112`. The control plane implements
and tests the changes; the disposition does not claim an independent code or
scientific review.
