# Source-bound derived analysis

These programs index and explain retained observations. They do not collect
relations, select new targets, search for scalar labels, change frozen primary
analyses or promote research status. B2 and D1 each have their own prospective
protocol, source lock, root release, exclusive supervisor and immutable export.

`archive.py` losslessly gzips closed, separately verified raw results/events
before export. It refuses Git-tracked originals, checks decompressed bytes and
records original/archive digests. Store the returned explicit gzip paths with
the official artifact tool. Finish all storage-manifest changes before creating
the unified export, whose bindings include those manifests.

`report.py` reads the recorded analysis/export into a fresh report directory,
with a recorded-data SVG, plotted values, Typst source and PDF. Inspect every
PDF page before publication. Run records must be committed/pushed first.

`certify_bases.py` reconstructs original M plus each full-rank B2 cell. Every
projected atom receives original-row weights, an exact unit-vector check and a
separate public point-multiplication check. `certify_targets.py` retains every
frozen D1 index and finds the first individual natural row whose vector
annihilates the original M kernel. Its explicit target-unit certificate uses
only M plus that one row, with augmented rank rank(M)+1 and unchanged base
nullity. This differs from the earliest combined recovery in the full stream,
which may occur first at full rank. Neither builder creates a target label for
collection. Recovered scalar values are outputs of checked row combinations.

```sh
PYTHONPATH=src:.:research/prime_field_progress_20261030 python3 \
  research/prime_field_progress_20261030/certify_targets.py \
  --run research/prime_field_d1_execution_20261030/runs/d1-fixed-panel-a91d96 \
  --inputs research/prime_field_d1_execution_20261030/inputs.json \
  --out research/prime_field_d1_execution_20261030/database/isolated-target-certificates.json
```

`database.py` makes a fresh v3 SQLite snapshot by read-only backup of the
original v2 artifact. It checks every export-bound file's digest and byte size
before import. The parent bytes and every historical row remain intact. New
subset/target cells are separate from historical observations; incomplete
metrics remain NULL. Original/native versus projected atom indexing remains
distinct. Field/subgroup values and scalars use exact decimal TEXT.

```sh
python3 research/prime_field_progress_20261030/database.py \
  --base research/prime_field_b1_execution_20261029/database/prime-fields-with-covers.sqlite \
  --b2-run research/prime_field_b2_execution_20261030/runs/b2-fixed-panel-802e2a \
  --b2-inputs research/prime_field_b2_execution_20261030/inputs.json \
  --d1-run research/prime_field_d1_execution_20261030/runs/d1-fixed-panel-a91d96 \
  --d1-inputs research/prime_field_d1_execution_20261030/inputs.json \
  --out research/prime_field_b2_execution_20261030/database/prime-fields-v3.sqlite
```

Hydrate the relevant artifact directories with
`python3 tools/artifacts/artifacts.py pull <directory>`. The parent SQLite is
reconstructed from its `.gz`; native raw JSON remains in its single recorded
plain/gzip encoding. New SQLite files above1MiB are gzip archived, with both
digests in a separate generation receipt, through the official store.

Views `subset_rank_summary`, `target_recovery_summary` and
`isolated_target_summary` expose rank gains, combined-prefix ranks and
single-row recovery with remaining base nullity. All public-source matches
and same/negated inter-target matches are retained; the latter point only to
earlier indices on the same curve, so each pair is stored once. No index is
filtered, replaced or relabelled. Four physical executions are expected after
importing B1, the cover survey, B2 and D1; candidate/reference records and phase
costs never create additional physical executions.

Metadata preserves the parent's builder/schema digests under `parent_*`,
binds the new builder and hashes the resulting sorted sqlite_master SQL with
its stated canonical-JSON recipe. The generation receipt also binds the
parent, frozen inputs, exports and certificate builders at committed source.
Hashing/importing results is not independent scientific review. These are two
small fixed curves, not a database of scalable attack results. Clock and partial
operation counters do not provide a complete S or a speedup comparison.
