# Global curve identities and archived benchmark views

Applies to crypto, crypto-autoresearcher and cryptanalysis. This adopts the
existing cryptanalysis `EC1` convention; it does not rename archived records.
The byte-identical reference implementation is `tools/curve_identity.py` in
all three repositories. It only hashes metadata; it performs no cryptographic
computation or mathematical certification.

## Naming rule for new comparisons

Always retain the compact curve alias **and** full global curve UID. A degree,
`Koblitz`, `ECC2K`, or a repository-local name is a display hint, never a join key.

| Identity | What it identifies |
| --- | --- |
| `field_sha256` | Exact field metadata: characteristic, degree, representation/basis, defining polynomial or prime modulus, element encoding |
| `curve_uid = urn:ec-record:1:sha256:<64hex>` | SHA-256 of `{"field": field, "curve": curve_without_curve_id}`; exact model, coefficients, subgroup, cofactor, generator and target group |
| Existing `EC1N<n>C<tag>h<digest-prefix>` | Binary-field compact alias; `N` is field degree, not subgroup bits |
| Existing `EC1P<b>C<tag>h<digest-prefix>` | Prime-field compact alias; exact prime is bound by the manifest, not its bit length |
| `EC1Q<p>D<n>C<tag>h<digest-prefix>` | Extension-field alias for nonbinary characteristic; does not reuse binary `N` |
| `candidate_uid = urn:ec-candidate:1:sha256:<64hex>` | Exact candidate manifest; IC, Pollard rho and other methods retain distinct method configurations |
| Workload / run | Frozen input-set hash / one recorded execution; hardware and outcome do not change the curve ID |

Retain full digests for joins and collision detection. Never join on the compact
suffix alone. Existing IC1, PS1, workload and run labels remain valid and visible.
This is exact **representation identity**, not a canonical isomorphism-class ID.
Changing basis, generator, subgroup, model, or bound metadata changes the record
identity. Equivalence requires an explicit sourced mapping; equal degree, order,
or j-invariant is insufficient. Never infer an equivalence automatically.

Canonical bytes are sorted-key, compact UTF-8 JSON (`ensure_ascii=False`), without
floats. Integers stay integers; encoded field elements retain their declared
encoding. List order is significant. Preserve existing hash preimages exactly:
converting hexadecimal strings to integers or adding certificates changes the
hash. Keep alias mappings and new attestations separate from immutable records.
If an existing producer has a different hash preimage, label it unresolved and
record a versioned adapter; never silently assign its label to another digest.

Use the same `field` and `curve` records for IC and rho on the same instance.
A new rho manifest records `method: "pollard-rho"`, its exact configuration and
implementation references, `factor_base: "none"`, and `isogeny: "none"` when absent.
Hash that manifest with `candidate_identity`; do not give rho an IC1 label.
An IC manifest retains its existing factor-base, stage and implementation records.
A factor base needs its actual enumerated-set digest, construction and quotient
convention; a point count or dimension alone cannot identify it. Preserve artifact
hashes separately from point-set hashes. Unknown is `null`, never `"none"` or zero.
An isogeny route records ordered source/destination curve UIDs and map-artifact
hashes, direction and degree, with provenance/verification status. The destination
keeps its own curve identity. Route and factor-base changes affect the candidate,
not the source curve. No isogeny construction is performed by these tools.

## UI handoff and evidence boundaries

The initial dashboard import is **all nine rows of cryptanalysis's archived
primary toy benchmark**, not the whole history or a new measurement. The offline
snapshot binds the source repository, exact commit, file SHA-256 hashes, exact
curve records, candidate/workload hashes, source-reported statuses and measurements.
The exporter checks committed source bytes, ID hashes, curve/workload bindings and
target counts. It imports no runner, solver or kernel and emits no scalar secrets,
raw logs or executable configurations. Verification badges mean the source reports
verification; metadata hashes do not independently certify performance or math.

From a cryptanalysis checkout, export existing records only:

```sh
python tools/export_benchmark_snapshot.py > /tmp/cryptanalysis-primary.json
```

To refresh crypto-autoresearcher, review the exported JSON, copy it into
`ui/benchmarks/cryptanalysis-primary.json`, and update the exact-file SHA-256 in
`ui/benchmarks/catalog.json` in the same PR. Both local and static readers consume
the shared `comparisons.json` payload. Browsing does not contact another repo or
launch a run. Snapshot content works offline; external source links need network.

The Compare page filters by global curve identity, expands exact field/subgroup
metadata and shows recorded IC / paired rho online timings, status, target counts,
operation unit, calibration and scope. Total and online quantities stay separate.
No overall ranking, speedup, confidence interval or transfer to larger curves is
inferred. Failures, timeouts and unknown quantities must remain rows on refresh.
A future ranked table requires matching workload, target count, timing boundary,
calibration, hardware/resources, verification and declared comparison variable.

## Rollout and remaining inputs

- Implemented: common metadata helper and naming rule in all three repositories;
  read-only primary archive exporter; pinned dashboard import and curve filter.
- Existing records remain untouched. Producers are not retroactively migrated.
- crypto's older scoreboard data needs source-specific metadata adapters before
  exact global IDs can be attached. A width/degree label alone is insufficient.
- Isogeny-specific UI rows need archived, fully specified map/route metadata.
- Pollard rho can share curve UIDs now; the initial view shows the paired rho
  timings already present in IC receipts, not independently archived rho candidates.
- New snapshots, production deployment and the earlier Compare UI PR remain
  separate delivery steps. This change performs no experiments or research-state
  transitions and alters no established measurement objective.
