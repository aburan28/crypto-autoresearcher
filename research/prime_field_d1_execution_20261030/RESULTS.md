# Independent natural-target observations, 2026-10-30

All eight prospectively fixed public targets completed the full census and
separate arithmetic/hash-recipe replay:18,350,080 collection branches and the
same number of replay branches,807 accepted witnesses. No target was replaced
or filtered. The process exited0 without timeout or exception; frozen source
bytes were unchanged. All eight targets were recovered. Every first combined
recovery occurred at full augmented rank16, so this stream did not demonstrate
an earlier combined recovery with base uncertainty remaining.

| Curve b | Index | Public Q | Witnesses | First combined branch | First combined rank | First isolated branch |
|---|---:|---|---:|---:|---:|---:|
| 13 | 0 | (4089,1564) | 105 | 699349 | 16 | 1971351 |
| 13 | 1 | (1609,1768) | 82 | 657402 | 16 | none |
| 13 | 2 | (3069,1236) | 74 | 968588 | 16 | 2115468 |
| 13 | 3 | (101,329) | 71 | 688967 | 16 | none |
| 16 | 0 | (1899,1988) | 91 | 1238046 | 16 | none |
| 16 | 1 | (2343,1096) | 105 | 1256460 | 16 | none |
| 16 | 2 | (4072,1786) | 150 | 829278 | 16 | 1938652 |
| 16 | 3 | (3742,1930) | 129 | 1333892 | 16 | 1436892 |

Each target used exactly2,293,760 scheduled branches over multipliers1..64,
including misses, with no recovery stop. The original sixteen native atoms,
fifteen projected base unknowns, source order and historical preprocessing
remain fixed:97rows/rank13 on b13,67rows/rank9 on b16. No B2 rows or atom logs
were used. Four SHA256 indices per full EC1 curve identity were frozen before
generation; no scalar labels were drawn. All targets differ from signed base
points, projected public anchors, all64 signed public sources, and each other
up to sign on the same curve. The generation receipt retains these checks.

## Isolated recovery and its explanation

Four later individual rows satisfy vN=0 for the original deficient M. Explicit
target-unit row-combination certificates use only M plus that one natural row.
They have augmented rank14 on b13 or10 on b16, leaving respectively2 or6 base
dimensions free, and pass separate public multiplication checks. This verifies
the identifiability criterion on natural rows; it does not establish cheaper
target recovery than the earlier full-rank stream.

A further **post-hoc** public-point diagnostic explains all four successes:

| Curve/index | Multiplier t | Public coincidence |
|---|---:|---|
| b13/0 | 56 | [56]Q = -[4]P |
| b13/2 | 60 | [60]Q = -[13]P |
| b16/2 | 55 | [55]Q = -[46]P |
| b16/3 | 41 | [41]Q = -[46]P |

These comparisons multiply public points directly; they do not use recovered
scalar labels. The targets themselves do not coincide with known sources, but
these multiples do. Thus the isolated recoveries are elementary public-multiple
collisions, not evidence for a new descent mechanism or cost advantage. This
diagnostic was added after observing individual successes, separately from
the prospective direct-target coincidence policy. All original cases and
primary metrics remain unchanged.

## Labelled derived partial-relation reuse

Treat each target's natural rows as [B,-t] on base columns and one outside
target column. Without using its recovered scalar, cancel that column and
score Delta=rank([[M,0],[B,-t]])-rank(-t)-rank(M). The dense python-flint oracle
agrees with carried-row cancellation:outside rank1, stacked rank16, Delta2 for
each b13 case and6 for each b16 case. The resulting base-only rank is15.
All799 cancellation equations retain original partial-row weights, reproduce
the coefficients/RHS, cancel the outside column and pass separate public
base-point equations. This is post-hoc reuse of retained data, not a new native
execution or completion of the residual-outside-point collector lead.

Each case is charged2,293,760 collection plus2,293,760 replay branches. Diagnostic
construction, elimination/extraction, dense-oracle and certificate-check CPU
components are retained separately. The branch ratio is an exact work-count
ratio, not complete collection/elimination S or an attack-cost comparison.
The native whole-process shared-host clocks were wall1971.213s, user CPU1959.213s,
system CPU8.218s, peak RSS238,534,656bytes; wall_valid=false. Producer counters
are partial. No novelty, scalable speedup or scientific status is asserted.

## Evidence and database

Native source:`14ef48bfa82c5678664204f28df5232b7c729ee7`.
Frozen protocol canonical SHA256:
`09a05ea721b99e17b07ae3641cb6913a6a6ca21b90a19d207f23ea24e4d5467c`.
Real canonical S3 checkpoint/admission, explicit root release, source/input/
interpreter locks and exclusive resource supervision preceded generation.

- [Analysis](runs/d1-fixed-panel-a91d96/analysis.json) and
  [unified export](runs/d1-fixed-panel-a91d96/export.json), checked with all file
  bindings after lossless archival. Raw data committed/pushed ine600afd62
  before reporting. All16 gzip result/journal artifacts are S3-backed and
  remote verified; original-byte hashes remain beside the run.
- [Report source](reports/d1-fixed-panel-a91d96/report.typ),
  [graph](reports/d1-fixed-panel-a91d96/observations.svg), and inspected two-page
  report.pdf, hydrated through its sibling artifact manifest.
- [v3 generation receipt](../prime_field_b2_execution_20261030/database/v3-fixed-panel/generation.json),
  [isolated certificates](../prime_field_b2_execution_20261030/database/v3-fixed-panel/isolated-target-certificates.json),
  and losslessly encoded target-partial-cancellations.json.gz. The receipt
  binds committed builders, inputs, exports, parent and original/archive hashes.

The fresh SQLite snapshot retains the original v2 parent bytes and history,
two curves/two bases,8198 cover frames,363 historical witnessed rows, then adds
10 subset cells/487 rows and8 target cases/807 rows,4 isolated certificates,
135 bound source files. Four physical executions mean B1, cover survey, B2,
D1; duplicate method records, derived analyses and phases are not executions.
Integrity and foreign keys pass; SQL partial scores and isolated ranks equal
the checked certificates/oracle. Hydrate prime-fields-v3.sqlite.gz and decompress
the ignored SQLite for queries documented in the progress README.

The separate replay is an implementation check, not staffed scientific review.
Sources are the original target/census lanes, B1 preprocessing, the merged
prym_leads_20261027 matrix/target criteria and PKM2016 section3.2. Historical
graphs remain unchanged; the new graph covers this exact panel. The next open
tests are residual-outside cancellation and target reuse that cannot be
explained by these bounded public-multiple coincidences, with prospectively
fixed cases and complete charged costs.
