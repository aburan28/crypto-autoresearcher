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
  --out research/prime_field_b1_execution_20261029/database/prime-fields.sqlite
```

Omit `--run` to import only the retained catalog. Outputs must be fresh.
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
```

The new-equation view compares normalized affine rows only within the same
physical execution and exact base. More equations are distinct from more
rank. `old_kernel_syndrome_json` retains B1's old-space test separately.
No SQL view estimates collision probabilities, total attack cost or speedup.

Sources checked before implementation: `docs/curve-identities.md` (exact
representation versus base identity), `docs/artifacts.md`, the merged
`prime_field_symmetries_20261029/catalog.json` and its source/literature note,
and the B1 native result/checker format. Provenance is internal/retrieved.
Canonical historical graphs remain unchanged; the new B1 report graphs new
observations and records this database's actual coverage. No scientific
status transition is made by the import.
