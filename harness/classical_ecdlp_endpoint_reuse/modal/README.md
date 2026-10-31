# Modal VM controller

This adapter builds a code-only image and runs one existing six-arm endpoint-reuse
study in one network-blocked Modal VM. It leaves the original implementation,
Isolab worker and producer unchanged. An image build/native self-test is software
validation; it is not a scientific target measurement. VM isolation does not
establish L2 or a dedicated physical host. Every engine clock remains invalid.

Source A is the original native/helper commit. Source B is a separate committed
closure containing all new `modal/*.py` code, including local protocol, admission
and export tools. `prepare_context.py` reads Git blobs, never the working tree.
It includes source files from A and the adapter from B, and excludes public and
private inputs, development outputs, credentials, caches and test outputs.
The context records every packaged source file's actual commit, both source-tree
hashes and an adapter manifest. `build_image.py` verifies this exact selection
again against committed objects before an upload is possible.

The public base is Debian bookworm slim pinned to
`sha256:7ff6ba31527b9e336162fa061746c366c4b2032f4d2cff2078bea43f78efe3f8`.
The original `execution/image_build.py` calls the original native build script.
Its original build-info is supplemented by `modal-image-build.json`, which records
source A/B, compiler executable hashes and the actual native/build-info hashes.
The completed build receipt records the actual `im-*` Image object ID, `ap-*` App
ID and software-probe `sb-*` ID. A Modal Image ID is not an OCI digest.

Run these commands from the repository root, using the reviewed Modal SDK 1.6.2
environment for commands that access Modal. Authentication stays in the local
controller process; do not create credential files or pass credentials into the
Sandbox. Substitute actual committed revisions and fresh output paths.

```sh
python3 harness/classical_ecdlp_endpoint_reuse/modal/prepare_context.py \
  --repo . --source-revision SOURCE_A --adapter-revision SOURCE_B --output CONTEXT
python3 harness/classical_ecdlp_endpoint_reuse/modal/build_image.py \
  --repo . --context CONTEXT --plan-only
python3 harness/classical_ecdlp_endpoint_reuse/modal/build_image.py \
  --repo . --context CONTEXT --out BUILD_RECEIPT_DIRECTORY
```

Only after the prospective protocol has been frozen and the one fresh cohort has
been sealed, the controller consumes its existing public bundle:

```sh
python3 harness/classical_ecdlp_endpoint_reuse/modal/controller.py run \
  --image-receipt BUILD_RECEIPT_DIRECTORY/receipt.json --protocol FROZEN_PROTOCOL \
  --public-bundle SEALED_PUBLIC.tar.gz --inputs-manifest-sha256 ACTUAL_SHA256 \
  --plan-only
python3 harness/classical_ecdlp_endpoint_reuse/modal/controller.py run \
  --image-receipt BUILD_RECEIPT_DIRECTORY/receipt.json --protocol FROZEN_PROTOCOL \
  --public-bundle SEALED_PUBLIC.tar.gz --inputs-manifest-sha256 ACTUAL_SHA256 \
  --out CONTROLLER_OUTPUT
```

`--plan-only` makes no SDK/account calls. An actual run requires the exact frozen
source, image receipt, build-info, adapter and placement pins. The App is
`classical-ecdlp-validation` in `main`. Its one Sandbox uses `runtime="vm"`,
`block_network=True`, CPU request/limit `(2,2)` physical cores (four vCPU
equivalent), memory request/limit `(12288,12288)` MiB, no Secrets, no OIDC token
and no attached account storage. Frozen operational watchdogs cap Sandbox
lifetime at 5400 seconds, command lifetime at 4200 seconds, staging at 600 seconds
and collection at 600 seconds. Scientific global/child watchdogs remain 3600
seconds. These are process/lifetime bounds, not new research budgets.

Only the public bundle, frozen protocol and actual provider context are staged,
with SHA-256 readback. Archives reject path traversal, links, devices, duplicates,
undeclared files and mismatched hashes. The engine runs through `env -i` and
`setpriv` as UID/GID 1000 with cleared supplementary groups and no new privileges.
Before sealing, the root supervisor observes and quiesces remaining reserved
UID1000 processes. Any failure to establish quiescence refuses the final seal.

The remote supervisor retains failures, partial streams, censoring and complete
raw output in a deterministic parent archive. The archive is transported through
the Sandbox filesystem API in hashed 64 MiB parts. Collection verifies every part,
the actual reconstructed archive hash, the exact safe archive membership, every
raw member hash and the process-cleanup evidence. Successful output paths are:

- `controller-receipt.json`, `plan.json`, `provider-context.json` and intent/identity receipts;
- `collected/output.tar.gz`, `archive-receipt.json` and `collection-receipt.json`;
- `collected/tree/output-manifest.json`, `process-cleanup.json`, engine streams
  and `raw/algorithm-raw-manifest.json` with the complete native raw tree.

The controller terminates the VM only after verified complete archive collection.
On ambiguous submission it records the unique requested name and any actual
Sandbox ID and never submits a replacement. Failed collection preserves the
remote Sandbox until its bounded provider lifetime. To collect from an identified
existing Sandbox without starting another measurement:

```sh
python3 harness/classical_ecdlp_endpoint_reuse/modal/controller.py collect \
  --sandbox-id ACTUAL_SB_ID --out FRESH_COLLECTION_DIRECTORY
```

This recovery command collects only and does not terminate the Sandbox. The
operator can terminate the same Sandbox after inspecting the verified receipt.
Unsealed snapshots are explicitly incomplete and never establish full coverage.

The controller's fixed checks use mocks and synthetic byte strings:

```sh
python3 -m unittest discover -s harness/classical_ecdlp_endpoint_reuse/modal \
  -p 'test_controller.py' -v
```

Implementation sources checked before coding: repository `AGENTS.md` and
`docs/agent-contract-extended.md`; the original build, bundle, public input and
producer code at source A; the retained official-document review
`/workspace/classical-ecdlp-endpoint-reuse/modal-route-feasibility/report.md` and
its retrieval manifest; official [Image SDK](https://modal.com/docs/sdk/py/latest/Image),
[Sandbox SDK](https://modal.com/docs/sdk/py/latest/Sandbox),
[file access](https://modal.com/docs/guide/sandbox-files),
[resource](https://modal.com/docs/guide/sandbox-resources) and
[network](https://modal.com/docs/guide/sandbox-networking) documentation; and the
installed SDK 1.6.2 implementations of Image IDs/build/copy and Sandbox filesystem,
creation and exec. These support the API route, not physical-isolation claims.
The separate real software VM probe is retained at
`/workspace/classical-ecdlp-endpoint-reuse/modal-vm-software-probe-20261027-02.json`.
This controller implementation's tests make no account calls, upload no source,
build no remote image, generate no cohort and execute no study targets. Actual
source-pinned image construction and scientific execution require their own
observed receipts from the authorized operator.
