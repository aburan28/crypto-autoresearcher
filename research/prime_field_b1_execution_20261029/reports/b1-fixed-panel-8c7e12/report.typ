#set page(paper: "a4", margin: 16mm)
#set text(size: 9pt)
#set par(justify: false)
= Fixed Prym x=0 completion and prime-field archive
Observations only. This report records one physical paired panel and a derived archive import. It promotes no scientific status or performance claim.

Run: #raw("b1-fixed-panel-8c7e12"). Curves: p=4099, a=2; b=13, r=4021, P=(0,264), and b=16, r=4111, P=(0,4). Both original bases have sixteen atoms, with fifteen unknown signed columns after public anchors. The exact curve/base identities and source arrays remain in the frozen inputs.

== Observed coverage
Panel complete: True. Collection branches: 9175040; separate replay branches: 9175040. Unknown cells: 0. No rank-based stop or substituted inputs. A/A and statistical null arms are inapplicable to this deterministic complete census; marked-small software positives and corruption controls preceded the freeze. Separate full replay checks actual finite outputs; it is not independent scientific review.

#table(columns: (auto,auto,auto,auto,auto,auto,auto), inset: 4pt,
  [b],[arm],[status],[witnesses],[equations],[rank],[nullity],
  [13],[historical],[verified],[97],[13],[13],[2],
[13],[completed],[verified],[121],[13],[13],[2],
[16],[historical],[verified],[67],[9],[9],[6],
[16],[completed],[verified],[78],[9],[9],[6],
)
#image("observations.svg",width: 100%)
Counts are exact within the two fixed inputs; no population interval or extrapolation is implied. Distinct equations are normalized affine rows, including the public-anchor-adjusted right side.

- b=13: 0 new distinct equations; rank increment 0; 0 witness rows with nonzero old-kernel syndrome. Source-zero witnesses 0; constraint-zero witnesses 24.
- b=16: 0 new distinct equations; rank increment 0; 0 witness rows with nonzero old-kernel syndrome. Source-zero witnesses 0; constraint-zero witnesses 11.

== Diagnostic resources and retained failures
Exit 0, timeout False, source unchanged after True. Wall 1046.509s, user CPU 1038.897s, system CPU 5.708s, peak RSS 221691904 bytes. Host AMD EPYC 9V74 80-Core Processor; kernel 6.18.55. These shared-host clocks have wall_valid=false. Collection operation vectors exclude replay, complete elimination/serialization/storage accounting and full S; no rate or speedup is inferred.

- b=13, historical_nonzero, collection: complete; CPU 121.864s, wall 122.109s.
- b=13, historical_nonzero, verification: complete; CPU 87.074s, wall 87.307s.
- b=13, completed_zero, collection: complete; CPU 148.808s, wall 148.924s.
- b=13, completed_zero, verification: complete; CPU 127.317s, wall 127.455s.
- b=16, historical_nonzero, collection: complete; CPU 144.410s, wall 144.569s.
- b=16, historical_nonzero, verification: complete; CPU 103.242s, wall 103.388s.
- b=16, completed_zero, collection: complete; CPU 176.619s, wall 176.856s.
- b=16, completed_zero, verification: complete; CPU 131.300s, wall 131.529s.

#pagebreak()
== Reproducibility and provenance
Frozen protocol canonical SHA256: #raw("ce2e79df3ef31396ba13c015c7c2443b8df74e0176ca452b8a8988095906324c"). Exact source commit: #raw("03d202a1709f44da6eaf069841bc881a81fe5dc3"). Source/release/input/interpreter/package locks, actual S3 gate, owner/PIDs, host facts, stdout/stderr, every source status string/digest, accepted witness and phase record are retained in the run directory. The full analysis was frozen before data; compressed records preserve original-byte hashes in archive-encoding.json. Data were published before this report. Administrative failures are retained separately and do not count as failed mathematical trials.

#image("pipeline.svg",width: 100%)

== Derived database and an exploratory symmetry lead
Coverage: 2 curves, 2 exact bases, 30 projected atoms, 2 action audits, 6 observation cells, 363 witnessed rows. Exact field/group integers use decimal TEXT. The archive binds 27 source files by bytes/hash and stores process resources once. Retained historical observations have NULL attempt counts where unavailable. Hash import reports the source's verification scope and confers no independent proof.

On the even sextic, the existing deck/negation action transforms a cubic to sign * v(deck * X). These are accepted-witness grouping counts derived after collection, separate from the frozen primary analysis:

- b=13, completed_zero: 121 accepted witnesses, 13 cubic orbits, 13 distinct affine equations.
- b=13, historical_nonzero: 97 accepted witnesses, 13 cubic orbits, 13 distinct affine equations.
- b=16, completed_zero: 78 accepted witnesses, 9 cubic orbits, 9 distinct affine equations.
- b=16, historical_nonzero: 67 accepted witnesses, 9 cubic orbits, 9 distinct affine equations.

Exploratory exact re-encoding check: 35 of 35 constraint-zero witnesses share the same public source, full cubic and native coefficient vector with a historical witness. Original-row links are in database/reencodings.json. This is stronger than matching a coarse orbit key, within these accepted rows only.

An equal cubic key does not erase source-specific obligations or certify reuse of a residual computation. Rejected candidates are not covered by these counts. The next caching study must preserve all branches, charge interpolation/setup, compare identical outputs and separately measure validation. B1 itself has no cache enabled.

== Limits and next measurements
The paired finite result concerns only the exact two retained curves, bases, source order and cubic law. More witnesses, more equations and more information are different quantities. Full rank is not required by the separate natural-target criterion vN=0. Eight independent natural targets remain ungenerated in this panel; D1, natural partial relations and native many-target operator reuse remain separate measurements. Original C1/Prym reports and their historical graphs remain unchanged.

== Shifted-cover algebra: implemented, not collected
The new ShiftedCover software interface keeps the same E and uses C_h: y²=f(x²+h), with coefficients c4=3h, c2=3h²+a, c0=f(h). The maps (x,y) to (x²+h,y) and, for nonzero x, (c0/x²,c0*y/x³), satisfy their quotient equations by substitution. The latter auxiliary curve has coefficients (c2,c4*c0,c0²), including the term absent at h=0. The software rejects a singular base or f(h)=0 and deduplicates the x=0 lift. Fixed p101 software controls exercise h=0,1,2,3; there is no shift search on the retained p4099 curves here.

A prospective common-atom survey would retain only h for which every original atom coordinate u has u-h square or zero, freezing selection before relation yields. A later collector must preserve original E/base/log columns, source schedule, poles and signs. This is a genus-two cover interface; no elliptic isogeny, subgroup eigenvalue, Jacobian certificate or advantage is asserted. See shifted-covers.md for the derived identities and exact successor boundary.

Sources (internal/retrieved): original Context/Census and fixed inputs; B1 literature.md and frozen protocol; database schema.sql/build.py and source-bound generation receipt; Petit, Kosters, Messeng, PKC2016, sections 3.1-3.2, primary PDF SHA256 a53030a6cde720c354aebfb65b1eb01e07766ce2d26e543d77f2516c0a49ef5b. Solver and linear-algebra costs stay charged. No novelty, complete ECDLP recovery or asymptotic claim.
