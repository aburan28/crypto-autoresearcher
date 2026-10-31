#set page(paper:"a4",margin:16mm)
#set text(size:9pt)
= Direct signed three-sum collection
Observations from #raw("a3-fixed-panel-0cddd8"). The original two p4099 curves, original16atoms, public64source schedules and historical97/rank13 or67/rank9 matrices are unchanged. Both direct collectors search every signed triple with distinct atom indices j < k < l and equation εj Bj + εk Bk + εl Bl = sP. No cover lift is required, and no outside unknown, recovered atom label or target is used.

Enumeration evaluates every source/triple/sign descriptor. The pair-table method constructs all signed pairs once, queries sP − εl Bl, retains every bucket entry and accepts only j < k < l. Infinity is a supported key. Each arm has its own cold setup/sign/source/projection and elimination accounting. Both complete their fixed stream; neither stops at full rank. Row ordering is canonical before analysis.

#table(columns:(auto,auto,auto,auto,auto,auto,auto,auto),inset:3pt,
[case],[arm],[descriptors / queries],[rows],[equations],[new rank],[combined],[gain],
[b13],[enumeration],[286720],[75],[57],[15],[15],[2],
[b13],[pair_table],[2048],[75],[57],[15],[15],[2],
[b16],[enumeration],[286720],[61],[55],[15],[15],[6],
[b16],[pair_table],[2048],[61],[55],[15],[15],[6],
)
Enumeration descriptors and pair-table queries are different work units. Each curve has480pair entries. Four arm records belong to ONE physical admitted process; they are not four physical executions. Distinct affine equations and independent rank are different measurements.

#image("observations.svg",width:100%)
Gain is rank(M plus new rows)−rank(M) on the unchanged15projected columns. Full old/combined right kernels, signed public-anchor projection, pivot-row indices and old-kernel syndromes are retained. New rank is calculated without adding the old rows; old rank is still measured and charged.

#pagebreak()
== Archived norm rows and complete checks
The archived A2 norm_completed=true rows are a frozen subset reference. Their two residual E images sum to zero, leaving only three signed original atoms and the source. Every such descriptor must occur in the direct census. A2 smooth five-term rows are excluded from this assertion. The original archived full C/auxiliary checks are not rerun as part of A3.

- b13: 92 archived norm witnesses map to 30 distinct direct descriptors.
- b16: 105 archived norm witnesses map to 29 distinct direct descriptors.

The separate checker imports the old independent E arithmetic, not producer arithmetic. It reconstructs every exhaustive descriptor, status and digest, reconstructs every pair entry and query bucket including rejected index orderings, checks identical complete row lists, validates all old principal rows, and recomputes affine ranks, consistency, pivot spans, complete kernels and old-kernel action. Logical table counters and stage-counter conservation are checked; producer field counters are not independently audited. This is an implementation check, not independently staffed scientific review.

== Stage accounting
The following totals are recorded instrumented operations per arm, including its setup, collection, certificate construction, public projection, affine normalization, old/new/combined elimination, kernels and kernel action. Fp operations and Fr operations are separate units. Inversions have their own unit; internal modular arithmetic inside inversion is not expanded. Group additions include underlying field operations, so the columns must not be added as disjoint cost units.

#table(columns:(auto,auto,auto,auto,auto,auto,auto),inset:3pt,
[case],[arm],[Fp group add],[Fp mul],[Fp inv],[Fr mul],[Fr inv],
[b13],[enumeration],[574543],[1725417],[574242],[34106],[118],
[b13],[pair_table],[3631],[12554],[3457],[34106],[118],
[b16],[enumeration],[574450],[1725120],[574291],[26030],[100],
[b16],[pair_table],[3538],[12385],[3378],[26030],[100],
)
Every collection/analysis stage also retains diagnostic wall and CPU seconds. Query and hit extraction are one explicitly combined stage. No C lifting or polynomial extraction exists in this direct implementation. Storage, serialization, sorting, hash-table comparisons, Python allocations, validation and independent replay do not have a complete weighted operation model. The outer phase journal and whole-process resources cover the execution diagnostically; do not add outer clocks to their inner components. Complete S, calibrated Delta-per-total-cost, matched rho and an end-to-end speedup remain unmeasured. A2's older incomplete counters are not a matched cost baseline.

#pagebreak()
== Execution and provenance
Native source #raw("620c1b254afcdfaa2143ad6e945a0859d57e8146"). Canonical protocol SHA256 #raw("bf8530e2786b862634bb4cdee8488c7c59a484e62c382ee5528c3da43e2efce8"). Exact input bytes, source closure, interpreter/packages, committed root release, actual S3 checkpoint/gate, ownership/PIDs, stdout/stderr and all branch journals are retained. Sources and protocol were frozen before native collection; preparation controls used only marked p101 fixtures.

Panel complete: True. Exit 0; timeout False; source unchanged after True. Shared-host diagnostic wall 11.479s; user CPU 9.426s; system CPU 1.811s; peak RSS 62287872bytes. All clocks wall_valid=false. Protective2048retained-row/4096pair-entry gates refuse with the prefix preserved; they never truncate a successful census. The2GiB/21600s process watchdog protects the host. Failures and unknowns remain explicit.

Full curve identities: urn:ec-record:1:sha256:a1c28a9c3fbfd4bac32eb2c772e55c59bd42f41729760037ce455637dacd10e6, urn:ec-record:1:sha256:55ec353815ef38de210150cb01255f7d4b5cd94fd0e6e0807020809672f6c64c.

Collection snapshots precede elimination; final results precede separate checking. All raw records were committed and pushed before this report. Closed large records are losslessly gzipped with original/archive hashes and official content-addressed S3 manifests. The v6 database is a fresh indexed extension of the byte-preserved v5 parent, retaining older records and adding direct-arm rows and archived norm matches. Historical reports and graphs remain intact. This panel's graph is a new derived view; no canonical scientific verdict is changed.

== Prior work and boundaries
Petit–Kosters–Messeng, PKC2016 sections3.1–3.4, distinguishes base construction, relation solving and linear algebra (retrieved primary PDF SHA256 a53030a6cde720c354aebfb65b1eb01e07766ce2d26e543d77f2516c0a49ef5b). The repository already records generic enumeration/pair-table methods and broader cost obstructions under LEAD-ICP-generic-table-decomposition, index_calculus/README.md and FINDING-PF-IC-001. The coordinator read the linked crypto primary program at423ea37eca55e459028adae4276d628ea6249738. Full provenance and inspected source sections are in literature.md.

The pair-table method is a standard generic construction. This study diagnoses the earlier Prym norm-completion lead and measures this local implementation; it does not revive a closed generic attack direction or assert a new symmetry, novel attack, scalable advantage or transfer to larger fields. Only the two already studied small curves are tested. Independent larger-field holdouts and natural-target queries are subsequent separately specified experiments. No scientific status promotion, verified configured model identity or passing full-ledger audit is asserted.
