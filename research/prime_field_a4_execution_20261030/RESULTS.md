# Larger-field holdouts and independent natural targets

All four prospectively selected fixtures and32independent public targets
completed, with full separate eligibility/hash/sum/table/query/affine/kernel/
certificate checks. Full source-matrix rank was reached on one fixture.
The only recovered target occurred on that full-rank fixture; no single or
joint recovery occurred with base uncertainty remaining.

| Fixture | E: a=2, b | Group order | Native/projected columns | Source rows | Rank after64sources | Target rows / targets decomposed | Targets recovered |
|:--|--:|--:|:--|--:|:--|:--|--:|
| p8191-i0 | 5009 | 8311 | 16/16 | 30 | 15/16 | 5 / 4 | 0 |
| p8191-i1 | 7229 | 8263 | 16/14 | 34 | 14/14 | 1 / 1 | 1 |
| p65537-i0 | 20845 | 65713 | 32/32 | 45 | 30/32 | 5 / 4 | 0 |
| p65537-i1 | 55325 | 65539 | 32/31 | 27 | 23/31 | 4 / 4 | 0 |

The136source rows are new observed witnesses. Fifteen target rows decompose
13of32targets; decomposition does not imply identifiability. The source-only
ranks at prefix16 were9,8,14,5; all prefix0ranks were0. Public signed anchors
from all64sources remain known at every prefix, so prefix0 does not mean zero
public information. Unknown widths14 and31 reflect retained public anchor
coincidences, not additional measured rank gains.

The one recovered target is p8191-i1/index6 with scalar1466, verified by
[1466]P=Q. The prospectively fixed diagnostic also finds **[62]Q=-P**, which
supplies an elementary public explanation of the same scalar. It was not
fed into the prefix matrices. Eight targets across the two F8191fixtures
have bounded-multiple matches; none has a direct signed-source or base
coincidence. No F65537target has a match in this diagnostic. Nonmatches
exclude only t1..64 versus signed s1..64, not every possible explanation.

Target-column elimination uses the same outside-rank subtraction as partial
relations. At prefix0 it adds one base dimension on p8191-i0 and p65537-i0;
at prefix64 the gains are0,0,1,0. Final base ranks after cancelling target
columns are15,14,31,23, with nullities1,0,1,8. Thus the p65537-i0joint rank35
does not mean its32base columns are determined: outside target rank4 leaves
base rank31. All ranks and complete kernels were separately checked.

Rules, not selected curve points, were committed before native generation.
Curve b values come from a frozen domain-separated SHA256 counter recipe,
with prime order r!=p, nonzeroB, nonsingularity and distinctness eligibility.
All124candidate records and5,316,634order point tests are retained. The
generator and factor base use existing first-rational/first-norm rules.
Targets hash independently to canonical rational points; no scalar labels
were drawn and no source/base coincidence or recovery outcome caused redraw.
There is no historical M on these holdouts. These are exact selected small
fixtures, not uniform population sampling; field and base size vary together.

Native collection built4928pair entries, made12,288source queries and1536
target queries. Each table is reused across its64sources and8targets.
The separate complete signed-sum oracle enumerated88,320signed triples once
across the four fixtures, mapping each sum to all source/target points, and
reconstructed every table entry/query bucket. Complete semantic coverage is
not a claim that source-times-triple enumeration was physically repeated.
One physical supervised run has four shared streams and12prefix observations.

Disjoint stage records retain generation, setup/sign/source construction,
table building, target draw/query/extraction/certification, public-collision
diagnostics and each prefix projection/normalization/elimination/kernel/
row-weight/public-recovery work. Shared collection counters occur once on
prefix0; cumulative counters and inclusive outer clocks are not added again.
Fp/Fr/group/logical units overlap and are not a scalar total. Generation
counts, Python/OS/hash/sort/storage work and verifier arithmetic do not supply
a complete weighted model. No calibrated complete S, matched rho, scalable
advantage or end-to-end speedup is asserted.

Scientific source:`d12aee8d6bec91cd225afe2d5b5ceec605129cd6`.
Canonical frozen protocol SHA256:
`2072ba5fcc6b9dcc4eca176cb0252d71b3667624fd94b1414447eba0ee0fe8db`.
Actual S3 checkpoint/gate, explicit source-bound root release,21source files plus one rules file,
exact rules/interpreter/packages and exclusive ownership preceded generation.
Exit0, no timeout/exception, source_unchanged_after=true. Shared-host
diagnostics: wall8.321050156s, userCPU6.101967s, systemCPU1.723517s,
RSS62,275,584bytes, wall_valid=false. Protective machine/candidate/row gates
never truncated or stopped a completed stream on rank or recovery.

- [Analysis](runs/a4-holdout-panel-c47bc8/analysis.json),
  [export](runs/a4-holdout-panel-c47bc8/export.json), and
  [execution](runs/a4-holdout-panel-c47bc8/execution.json). Data were
  committed/pushed in7f95b023e before reporting; export--verify-files passes.
  Thirteen generated/collection/final/journal objects are officially stored
  and remote-verified. Four large JSON files are losslessly gzipped with
  original/archive hashes; other files retain their encoding.
- [Report source](reports/a4-holdout-panel-c47bc8-corrected-bindings/report.typ) and
  [graph](reports/a4-holdout-panel-c47bc8-corrected-bindings/observations.svg). All3PDFpages were
  inspected; hydrate the PDF through its artifact manifest. The original report
  is preserved with an additive binding-count correction (21source files plus
  one rules file). No native source, data or result changed.
- [v7 generation receipt](database/v7-holdouts/generation-v7.json). The
  byte-preserved v6 parent is extended to6curves/6bases,8historical physical
  executions,136holdout source rows,15target rows,32public targets and12prefix
  certificate records. Integrity/FKs and gzip roundtrip pass. The verified
  archive is in S3; the plain SQLite remains ignored.

Twenty-four selected root software tests and7administrative controls passed
before native data; marked p101controls include deficient-rank functional
identifiability and certificate corruptions. Full-ledger validation refused
the sparse checkout; no full-ledger pass, staffed scientific review, verified
configured model identity or official scientific transition is claimed.
The source review is in [literature.md](literature.md), including primary
PKM2016sections3.1–3.4, A3 and D1. Existing reports/graphs remain historical
views; this new graph records this panel only.

The next discriminating control is source selection on unchanged curves,
bases and projected columns: the current small scalar window versus frozen
hash-selected public sources. A separate prospective protocol must distinguish
new relation information from newly exposed public anchors. Cause, broader
base geometry, more sources and larger-field transfer remain open; the finite
deficiencies do not prove impossibility. See the linked
[rank/target-coverage problem](../../problems/prime-field-holdout-rank-and-target-coverage.md).
