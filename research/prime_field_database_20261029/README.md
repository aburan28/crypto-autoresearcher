# Prime-field archive database

This is a derived archive index, not a curve search or a relation collector.
The first import uses the exact retained catalog from PR2726 and the two
original sixteen-atom p4099 fixtures. A B1 export can add its four newly
collected cells after collection and separate replay finish. No absent cell
is filled with a zero count, and historical attempt counts not present in
the catalog remain SQL NULL.

`schema.sql` separates full EC1 representation identities, ordered projected
base hashes, atoms, signed actions, physical executions, observations,
status totals and individual witnessed equations. Integers for field and
subgroup values are decimal TEXT, preserving P-256-width integers exactly.
The present imported curve coverage is only the two p4099 curves; the data
type's capacity does not assert a broader census.

Each source file is bound by its actual SHA256 and byte count. Export-bound
files are checked before import. Mathematical verification labels explicitly
describe what the source reports; importing or hashing a certificate does not
become an independent scientific review. Shared process resource records
live once in `executions`, avoiding accidental addition across four cells.
The database contains public witnesses and no secret scalar labels.

```sh
python3 research/prime_field_database_20261029/build.py \
  --run research/prime_field_b1_execution_20261029/runs/FRESH_RUN \
  --cover-survey research/prime_field_cover_survey_20261029/runs/FRESH_SURVEY \
  --out research/prime_field_b1_execution_20261029/database/prime-fields.sqlite
```

Omit both run flags to import only the retained catalog. Outputs must be fresh.
Hydrate S3-backed raw files before building. The generated SQLite file follows
the repository artifact policy; keep its manifest and a generation receipt
binding builder/schema/input/output hashes. Rebuild from those exact bytes.

Example queries:

```sql
SELECT b,arm,attempts,witnesses,unique_equations,rank,projected_columns,nullity
FROM rank_summary ORDER BY CAST(b AS INTEGER),arm;
SELECT * FROM zero_witness_summary;
SELECT observation_id,COUNT(*) FROM new_completed_equations
GROUP BY observation_id;
SELECT base_sha256,name,known_constraint_rank,additional_rank_after_constraints
FROM actions;
SELECT * FROM cubic_reuse_summary;
SELECT b,h,atoms_with_lifts,source_points_with_lifts
FROM cover_admissibility WHERE eligible=1;
```

The new-equation view compares normalized affine rows only within the same
physical execution and exact base. More equations are distinct from more
rank. `old_kernel_syndrome_json` retains B1's old-space test separately.
The `kernels` table retains each fresh cell's checked right-kernel basis for
later target-identifiability tests `v*N=0`; it does not require full base rank.
It does not invent kernels missing from the retained historical catalog.
No SQL view estimates collision probabilities, total attack cost or speedup.

Version2 adds `native_atoms` with the original sixteen-atom indexing,
`cover_sources` in the exact source order and all `cover_frames` masks and
coefficients. The sixteen-bit cover masks index `native_atoms`, not the
fifteen projected unknowns in `atoms`. Cover survey costs occupy their own
physical execution row. Existing version1 database artifacts are preserved;
their receipts bind the earlier source/schema bytes. The new combined file
is a separate artifact and never overwrites the earlier database.

The cubic reuse view is exploratory derived archive analysis. On the existing
even sextic, the already-valid deck/negation actions transform `v(X)` to
`sign*v(deck*X)`. The builder stores a canonical key over these four cubics,
with the curve identity included in its digest. Equal keys group functions;
each source, interpolation witness, projected equation and sign obligation
remains separately available. A function key alone cannot authorize dropping
branches or reusing source-specific residuals. This view measures a candidate
for a separately frozen caching experiment; no cache is enabled in B1.
This view covers accepted witnesses only. It does not count cubic duplication
among rejected candidates, which must be instrumented before assessing total
collection savings.

Sources checked before implementation: `docs/curve-identities.md` (exact
representation versus base identity), `docs/artifacts.md`, the merged
`prime_field_symmetries_20261029/catalog.json` and its source/literature note,
and the B1 native result/checker format. Provenance is internal/retrieved.
Canonical historical graphs remain unchanged; the new B1 report graphs new
observations and records this database's actual coverage. No scientific
status transition is made by the import.

The published combined snapshot is
`../prime_field_b1_execution_20261029/database/prime-fields-with-covers.sqlite.gz`;
its adjacent generation-v2.json binds original/archived byte hashes. Hydrate
the artifact, then `gzip -dk` to reconstruct the ignored local SQLite file.
The membership-only all-tie subset candidates are retained in cover-subsets.json.
