# Direct signed-three-sum observations

Run `a3-fixed-panel-0cddd8` completed on both original p4099 curves. Exhaustive
enumeration and the signed-pair table returned exactly the same complete rows,
in the same canonical order. Each new matrix alone has rank15 on the original
15 projected factor-base columns. No outside unknowns or archived A2 rows were
added to these matrices.

| Curve | Direct rows, each method | Distinct affine equations | Old rank | New rank | Combined rank | Gain |
|:--|--:|--:|--:|--:|--:|--:|
| b13, r4021 | 75 | 57 | 13 | 15 | 15 | 2 |
| b16, r4111 | 61 | 55 | 9 | 15 | 15 | 6 |

All197 archived A2 norm-completion witnesses occur in this direct census.
The92 b13 witnesses map to30 distinct signed-triple descriptors; the105 b16
witnesses map to29. Thus the136 direct descriptors include77 that do not
occur in the frozen norm-only reference. This is descriptor coverage, not77
additional independent equations. A2 smooth five-term rows are a different
semantic set and were excluded from this subset assertion.

Each curve used the original16atoms, original64source schedule and historical
97/rank13 or67/rank9 M only. Both direct arms independently constructed their
setup, signs, sources and public projection. Enumeration completed286,720
signed distinct-triple descriptors per curve. The pair method built480signed
pairs and completed2,048queries per curve, retaining every bucket hit before
the j<k<third test. Infinity keys are supported. These are different work
units, not a meaningful descriptor/query cost ratio. Neither method stopped
at full rank.

The separate implementation replayed all573,440 enumeration descriptors,
960pair entries and4,096queries across the two cells, checking exact rows,
statuses/digests, all table buckets, original principal rows, affine
consistency/ranks, pivot spans, complete kernels and old-kernel action. No
producer arithmetic was imported by this checker. It is an implementation
check, not independently staffed scientific review or a field-counter audit.
The archived full C certificates remain in their original A2 record; A3
checks their direct E correspondence and cancelling-image metadata.

Instrumented totals per method include its own setup/sign/source construction,
collection, relation certification, projection, affine normalization,
old/new/combined elimination, kernels and old-kernel action:

| Curve/method | Fp group additions | Fp multiplications | Fp inversions | Fr multiplications | Fr inversions |
|:--|--:|--:|--:|--:|--:|
| b13 enumeration | 574543 | 1725417 | 574242 | 34106 | 118 |
| b13 pair table | 3631 | 12554 | 3457 | 34106 | 118 |
| b16 enumeration | 574450 | 1725120 | 574291 | 26030 | 100 |
| b16 pair table | 3538 | 12385 | 3378 | 26030 | 100 |

These columns overlap: group operations use the listed field operations.
Fp/Fr operations and inversions are also separate units. They must not be
added as a scalar total. Producer operation calls and named logical events
are counted; Python/OS costs, inversion internals, storage and replay
arithmetic do not have a complete weighted model. Query and extraction share
one explicitly labelled stage. Every inner stage has diagnostic CPU/wall
measurements; outer and whole-process clocks are inclusive, not additional
costs. C lifting, polynomial extraction and outside cancellation are absent
from this direct implementation. Complete S, a calibrated rank-gain per total
cost, matched rho and a matched direct-versus-cubic cost comparison remain
unmeasured.

One supervised physical execution produced four method/curve records. Shared
host diagnostics: wall11.479065659s, userCPU9.426267s, systemCPU1.810964s,
peakRSS62,287,872bytes; wall_valid=false. Exit0, no timeout/exception,
source_unchanged_after=true. Exclusive ownership and source/input/interpreter/
package/protocol/release checks passed, including the actual canonical S3
checkpoint gate. Exact scientific source is
`620c1b254afcdfaa2143ad6e945a0859d57e8146`; canonical protocol SHA256 is
`bf8530e2786b862634bb4cdee8488c7c59a484e62c382ee5528c3da43e2efce8`.
The complete protocol was frozen before native data. The2048-row/4096-pair
gates are protective refusals retaining prefixes, not truncation or rank stops.

- [Raw analysis](runs/a3-fixed-panel-0cddd8/analysis.json),
  [export](runs/a3-fixed-panel-0cddd8/export.json) and
  [execution](runs/a3-fixed-panel-0cddd8/execution.json). Raw data were
  committed/pushed inffce2b175 before report creation. All six closed
  collection/final/journal files were officially stored and remote-verified.
  Two final JSON files are losslessly gzipped with original/archive hashes;
  sub-MiB snapshots/journals retain their original encoding. Hydrate through
  the adjacent artifact manifest.
- [Report source](reports/a3-fixed-panel-0cddd8/report.typ) and
  [graph](reports/a3-fixed-panel-0cddd8/observations.svg); all three PDF pages
  were inspected. The PDF is available through its artifact manifest.
- [v6 database receipt](database/v6-fixed-panel/generation-v6.json) binds
  the byte-preserved v5 parent, committed builder, inputs and exported files.
  It retains all prior data, adds272 direct rows across both identical-method
  representations and197 archived norm-match links, and stores7 historical
  physical executions. Integrity and foreign-key checks pass. The plain
  SQLite is ignored; its verified gzip archive is in the artifact store.

Root21 selected software regressions and7 administrative controls passed.
The initial shallow-copy mistake in a corruption test was corrected and
recorded before native execution. The full-ledger validator refused the sparse
checkout; no full-ledger pass or official scientific transition is asserted.
Existing graphs and reports were checked as historical views and preserved;
this panel has its own new graph.

[Literature review](literature.md) includes PKM2016sections3.1–3.4 and the
existing generic-table decomposition studies and cost obstruction. Pair-table
collection is prior work. This experiment clarifies the A2 interface and
records this local implementation; it makes no novelty, scalable advantage
or end-to-end attack claim. The tested curves are the same two small cases,
so larger-field transfer remains open. The next experiments are independent,
prospectively selected larger-field fixtures and public target queries with
construction, table reuse, elimination and recovery costs kept separate.
