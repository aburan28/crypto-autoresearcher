# TT Supervised Artifact Contract V1

## Status

Status: `HYPOTHESIS`, `TOY-EVIDENCE`, `MODEL-BOUND`.

Artifact freeze: unauthorized.

Campaign execution: unauthorized.

## Hypothesis

A complete V22 child result and its parent supervision receipt can be packaged
as a small deterministic Git-trackable directory without weakening their byte
identity or allowing ambiguous decompression.

## Null hypothesis

The format is rejected if packaging is nondeterministic, omits either authority,
accepts a symlink or extra file, permits a digest mismatch, permits concatenated
or trailing gzip data, expands beyond the uncompressed gate, or fails to recover
the exact canonical child result.

## Closed artifact set

Each envelope directory contains exactly:

- `child-result.json.gz`;
- `parent-receipt.json`;
- `envelope-manifest.json`.

Every path must be a direct bounded regular file. Symlinks, directories,
hardlink aliasing among the three files, and extra names are rejected.
The numeric pre-read caps are 256 MiB for both compressed and uncompressed
child bytes, 4 MiB for the parent receipt, and 1 MiB for the manifest.
On macOS/exFAT, publication removes only the optional `._` AppleDouble sidecar
for each of these three names while the directory is still private, verifies the
closed set again, syncs it, and atomically renames it. A sidecar or any other
extra name present after publication remains a verification failure.

## Canonical identities

The manifest records:

- protocol and role;
- child schema, canonical uncompressed byte length and SHA-256;
- deterministic gzip byte length and SHA-256;
- parent-receipt schema, byte length and SHA-256;
- exact static-audit SHA-256;
- `artifact_freeze_authorized=false` and a development-only boundary.

The parent receipt must be exact canonical JSON and independently bind the child
stdout bytes and SHA-256. The child must be exact canonical JSON with
`valid=true`, the expected protocol, role-compatible schema, and the toy/model
claim boundary.
Any artifact-freeze, campaign-execution, or generic-runner authority field at
any depth in either authority must be exactly false. Validation traverses every
object and array. The producer claim object is also an exact closed map, so
extra authorization keys cannot hide inside it.

## Trust model

The manifest states that the reviewed source-staging parent and local host are
trusted and that malicious or concurrent host mutation is excluded. It also
binds `generic_runner_supervision_claim=false` and
`campaign_execution_authorized=false`. Verification reconstructs these exact
values; editing or omitting one fails closed. This package does not claim
generic-runner containment, kernel enforcement of the parent, artifact freeze,
or campaign authority.

## Compression contract

Compression is RFC 1952 gzip produced at level 9 with modification time zero.
The manifest binds the exact compressed bytes, so Python/zlib implementation
drift is visible rather than normalized away.

Decompression is bounded to 256 MiB. The decoder must reach end-of-stream once,
consume all input, expose no unused or unconsumed bytes, and recover exactly the
manifest-bound canonical result. Concatenated gzip members and trailing data
fail closed.
Verification then recompresses the recovered child under this exact contract and
requires byte equality, so rebinding a valid but noncanonical gzip stream does
not satisfy the manifest's level and timestamp claims.

## Cost model

Packaging and verification both report the child and compressed byte counts,
compression ratio, wall and CPU time, parent-process peak RSS, and application
bytes read and written. Packaging additionally reports:

- observed peak temporary logical and allocated bytes;
- AppleDouble files and bytes removed before publication;
- file and directory sync counts and the atomic rename count;
- caught-failure cleanup policy and the fact that power-loss crash residue is
  not measured by this development format.

File-set validation uses bounded no-follow metadata opens rather than payload
reads. Reported read bytes therefore cover the one input pass and the one
self-verification pass exactly. A caught post-rename verification failure removes
the just-published development directory and syncs its parent; power-loss residue
remains explicitly unmeasured.

These costs are development diagnostics. A future supervised executor must add
them to, not hide them behind, the child accounting.

## Positive control

Pack the V22 producer output and parent receipt twice. Both package directories
must have byte-identical files, and verification must recover the exact
138,592,835-byte child result.

## Negative controls

- alter child or receipt bytes;
- alter a manifest digest and recompute only its payload checksum;
- append a second gzip member;
- append trailing bytes;
- lower the decompression bound below the recovered size;
- replace one artifact with a symlink;
- hardlink two artifact names;
- add an unlisted file.

## Success criterion

All positive controls are deterministic and all negative controls reject before
an extracted child result is published.

## Falsification criterion

Any accepted mismatch, ambiguity, unbounded expansion, alias, extra path, or
nondeterministic package byte falsifies this version of the format.

## Next concrete action

Obtain an independent re-review of the implementation and controls, then package
V22 outside the repository only if that review returns `GO` for the measured
development preflight.
