# Endpoint reuse: execution package

This package prepares and runs the prospective six-arm study. No confirmation
cohort, image, isolated measurement, service connection, or S3 publication is
created by writing or testing these files. Current observations are in
`readiness-observation-01.json` and `evidence/observations.json`; readiness is false.

The fixed workload is 64 ordinary curves, two independent solver replicates,
64 ordered public targets per cell, and six arms: `static_small`, `static_full`,
`static_filled`, `harvest`, `harvest_disabled`, and `rho_reference`. There are
128 curve/replicate cells and 768 native child invocations. Within a cell every
arm processes the same 64 targets sequentially. Cell and arm order use the
frozen SHA-256 seed law in `protocol/seed_rules.py`; the final protocol hash
and public post-freeze nonce determine that order. Secret scalar labels and
private target-generation roots are never image or solver inputs.

## Phases and identities

1. Commit the implementation, parent adapter, public verifier, cohort-generator
   code and analysis code as source revision A. `prepare_context.py` copies
   allowlisted **committed** files, excluding confirmation `public/`, `private/`,
   development outputs and caches. It does not snapshot a dirty working tree.
2. With a real digest-pinned Debian/Ubuntu base, `build-image.sh` builds a
   code-only image. It runs `python3 implementation/build.py --output
   /usr/local/bin/endpoint_reuse`, never the scientific workload. The image
   records source A, the executable's actual SHA-256, compiler/package versions,
   and every packaged code-file hash in `/opt/study/build-info.json`. Resolve
   and retain the real private-registry image digest and build-info bytes.
   No registry push is implicit. Never upload this private repository to a
   public registry.
3. Freeze the prospective protocol using the actual source/binary/image pins.
   Only then draw and retain the public external nonce, generate the fresh
   cohort, and seal its public manifest. This keeps protocol-derived solver
   seeds out of the image/protocol hash dependency cycle.
4. `bundle_inputs.py` verifies and packages the public cohort locally. Its
   receipt says `uploaded:false` and contains no fabricated S3 pointer. Through
   the authorized lab identity, upload it under the existing lab's `inputs/`
   prefix, retaining the actual S3 object VersionId and SHA-256. The final
   launch plan/handoff binds the actual image, source A, binary hash, frozen
   protocol, input object version/content hash and public-manifest hash.
5. `prepare_request.py` runs the repository's actual
   `tools/experiment_protocol.py validate` and creates offline **arguments for
   the existing `isolab_k8s_run` tool**. It never dispatches. Its prepared-launch
   metadata always leaves `ready:false`: an offline JSON file proves no live
   registry access, queue ownership, capacity or scientific approval.
6. The executor obtains a real overview, publishes its actual queue claim and
   dispatches through the admitted connection. Preserve the returned Job/Pod
   identities; inspect an ambiguous submission before doing anything else.
   There are no automatic measurement retries.

## Actual backend field mapping

The inspected upstream contract and source copies are pinned in
`evidence/manifest.json`. `isolab_k8s_run` accepts only `job_name`, `command`,
`image`, `cpu`, `memory`, `seconds`, and `retries`. The image must end in
`@sha256:<64 lowercase hex digits>`; the command is literal argv. This package
requests four exclusive vCPUs, 12 GiB, the frozen operational deadline and zero
retries. The real service requests equal CPU/memory requests and limits,
whole-core allocation, one lab Job per node, UID/GID 1000, read-only root,
`/work` and `/tmp`, and its normal IRSA identity. No key or token belongs in
the request or in chat.

`instance_type` and `isolation_profile` are **not** fields of the generic MCP
tool. The separate official `submit-job` shell launcher supports
`--isolation-profile l2 --instance-type c8a.2xlarge`, with at least four CPUs and
no retries. The prepared metadata gives those exact arguments for an already
authorized launcher; it does not add those fields to an unsupported API.
Changing a node label does not create an observed L2 grade.

The existing GitHub `isolab-experiment.yml` on crypto main accepts only the
deployed native ecbench interface. It cannot execute this new C++ program.
Its historical default includes IC and must not be substituted for this
classical, non-IC study. The pending commit-image branch's successful contract
job is not evidence that its skipped build/experiment ran. See the retained
workflow and job evidence. The session's Actions-variable read returned 403;
its configuration and organization OIDC readiness remain unverified.

## Runtime and retained evidence

`worker.py` verifies actual image build-info, all code hashes, the native binary,
and the frozen protocol before measurement. It uses the existing IRSA SDK chain
to GET the exact `inputs/` object VersionId, verifies its content SHA-256, rejects
oversized members, symlinks, hardlinks and path traversal, and verifies the full
public manifest through the standalone public reader.

`run_experiment.py` creates exact public one-cell TSV slices, interleaves arms
according to the frozen order, and invokes only the native binary's declared
`--run FIXTURES TARGETS SETTINGS ARM FRESH_OUTPUT` interface. Every native child
gets its **own `os.wait4` rusage**. Linux max RSS is converted from KiB to bytes;
it covers the entire child, including parsing, shared validation, constructor,
64 targets, trace output and teardown. This is not the previous solver-API
timing boundary. Per-child host facts, timestamps, argv, inputs, raw output,
stdout/stderr, exit/signal, timeout, and missing/unattempted outcomes are retained.
Native failure is never retried or replaced with invented target rows.
An adapter status of `completed` means complete producer output; it does not
mean that all 64 targets were solved. Per-target misses and censoring stay rows.

Counts remain the primary scientific measurements. All producer CPU/wall clocks
are retained with `wall_valid:false`: generic placement, host facts, and a
successful equation check do not prove L2. This package is not an isolation
grader; any later qualification needs the real independent isolation evidence.
The child timeout and global watchdog are frozen operational classifications,
not campaign spending limits. An interrupt does not authorize a clock-preserving
restore; this adapter implements no restore.

The algorithm and outer worker retain separate manifests. The final
`raw-manifest.json` lists all sealed payload files; `upload-status.json` is a
post-manifest transport record. Original streams remain intact, with lossless
line-complete parts of at most 61,440 bytes provided for archival. The uploader
writes only the assigned `runs/<Job>/<Pod>/` prefix through the existing IRSA
identity, keeps logical and stored SHA-256 hashes, uses gzip transport for
artifacts of at least 1 MiB, records actual S3 VersionIds, and attempts to retain
partial-upload failures. No local metadata marks an object published before
the real SDK call returns. A receipt cannot certify its own transport.

`fetch_results.py` uses an authorized normal S3 SDK connection to pin/GET the
actual receipt version and each recorded object version, verify stored hashes,
decode gzip where declared, and verify all logical hashes. Its collector receipt
is beside the raw tree, not inside the sealed payload. The seven-tool generic
MCP interface lists result objects but does not itself download their bytes;
the executor also needs this ordinary result-read capability.

`readiness_probe.py` performs only real local MCP catalog/overview and registry
manifest reads. Missing connection or digest fails closed before any Job call.
It does not emulate a service, install credentials, alter permissions, or grade
a run. A new ChatGPT-hosted tool connection can instead be inspected through
its real tools; the local CLI probe is not an invented prerequisite for it.

Software checks are `python3 -B -m unittest discover -s execution -p
'test_adapter.py' -v`, Python syntax and Bash syntax. They use fixed synthetic
adapter fixtures and child stubs only. They are not confirmation measurements,
capacity validation, or evidence of an ECDLP improvement.
