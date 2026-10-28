# CCR root matching on the fixed NIST/ANSI cohort

The missing historical selector remains unresolved. Corrected CCR recovery
finds every one of 112 rational cyclic kernels across 147 curve/degree cells.
All eleven reconstructed omissions and all ten publications enter a favorable
case at degree seven or higher. No cohort input has the tested projection
collision or repeated-root complication. The literal-draft conversion finds
no kernels at degree five or higher, including for the publications.

The subsequent [finite two-predicate audit](two-rule-audit-20261027/report.md)
tests combinations directly: 1,913 frozen predicates reduce to 495 observation
signatures, with zero robust or possible fits among 122,265 signature pairs
and all 16 Boolean functions per pair. This includes local CM splitting,
power residues of j and coefficients, all 61 source-table root levels, and
recorded validation features. Its scope is two atoms from that library;
arbitrary complex or field-dependent rules remain outside that result.

The [signed Frobenius extension](signed-frobenius-20261027/report.md) adds
full torsion actions and source eigenvalue-list metrics. It finds 16 exact
retrospective signature-pair fits, including a two-cap separator at auxiliary
prime 199 covering all ten publications and eleven omissions. Independently
frozen source-policy checks expose the remaining gap: uniform caps reject
every publication, unknown-degree mode loses four, and the later counter's
reported working-prime traces stop below 199 on all omissions. Every fit and
counterexample is retained; historical use remains unestablished.

The [exact capacity calibration](signed-frobenius-20261027/calibration-01/report.md)
checks both the broad search and the narrow same-prime cap family. The broad
family represents 3,864 of 4,480 field-count labelings robustly; the narrow
family represents only the observed labeling, at ell=199. With stream
endpoints fixed the counts are 110 of 126 and 1 of 126. These are descriptive
reference populations, not historical-choice probabilities. A newly recovered
December 1996 Dewaghe thesis contains the sign refinements, but its Atkin
odd-projective-order condition fails published P-224 as an acceptance rule.
At that point Müller's 1995 dissertation was located but unread. The
subsequent [period-source audit](signed-frobenius-20261027/period-eigenvalue-20261027/report.md)
retrieves and reads the actual thesis, then checks its special CM routes by
two independent methods on all 21 curves, including P-384. None is
supersingular or in an ordinary base-field isogeny class containing j=0 or
j=1728; generic-j positive controls exercise both targets. The thesis switches
methods for large candidate lists and insufficient memory, and explicitly
continues beyond its literal first-phase product threshold. It supplies no
32/2048 acceptance gate or original caller. The historical-use gap stays open.

The [implementation-source continuation](signed-frobenius-20261027/period-eigenvalue-20261027/implementation-sources-01/report.md)
now recovers and reads Maurer's actual 130-page thesis, dated 29 July 1994.
It documents separate total-CRT and baby-step-table bounds, table rebalancing,
supplied-prime-list and saved-splitting-file modes, and the names of the C
functions. Its explicit unsupported type2 repeated-fiber condition is absent
on all 21 curves in the retained later-table audit: 1,281 curve/level cells,
1,185 parameters and 2,071 fibers, including 299 type2 fibers. This is a new
source-to-existing-evidence crosswalk with zero new scientific trials. The
printed loop guard has an initialization inconsistency that prevents treating
the informal pseudocode as an authenticated executable. Neither the original
caller nor the two fitted caps or a cube-root-of-j requirement is recovered.
The next [source recovery](signed-frobenius-20261027/period-eigenvalue-20261027/eco-code-recovery-01/report.md)
obtains Lehmann's actual 125-page thesis from its July1997 author-homepage
capture and statically inventories an advertised LiDIA1.3 package captured
May1997 (its internal version header still says1.2.0). Le94's cube occurs in
forward q-series construction; the curve interface substitutes j(E), with no
cube-root-of-j prerequisite. It reports coefficient tables for every prime
ell<800. CRT stabilization and libI binary conversion identify original-table
provenance as a concrete remaining dependency. The retained all21 crosswalk
has zero documented precondition failures, with the later-table/rational-root
scope explicit. The general package lacks the named eco routines; the2000
announcement explicitly excludes SEA from the free distribution. Original
coefficient bytes and the NIST caller remain missing. The overall selector
remains unresolved.

The [table-artifact continuation](signed-frobenius-20261027/period-eigenvalue-20261027/eco-code-recovery-01/table-artifacts-01/report.md)
verifies all14 entries of Le94's printed ell5 integer table against the later
ASCII table and checks the modulo101 values independently. The preserved1997
libI/FreeLIP/GMP binary interfaces establish a file/backend/ABI dependency;
original file bytes, visitation and error policy remain unknown, leaving all21
historical I/O predictions undetermined. The previously located SWH
LiDIA-history snapshot is actually empty; its full-visit metadata supplies no
source branches. Exact receipts and failed indexes are retained. The selector
remains unresolved.

Read [the report](report.md), its inspected [PDF](report.pdf), the complete
[21-curve comparison](comparison.csv), and the [147 cell results](cells.csv).
These are reconstructed omissions, not documented historical rejection events.
Fresh mathematical projection root sets are reconstructed; historical q-series
tables, executable use, root order and stopping policy are not established.

The source distinguishes auxiliary-prime selection from curve selection:
without a suitable root, advance to the next auxiliary prime; choose a
non-repeated S1 root; try quotient-coefficient pairings and validate the kernel.
The special-j controls exercise projection collisions, including a repeated
S1 value already excluded by that source root rule. No cohort case has it.

## Exact replay

Check [BUNDLE.json](BUNDLE.json), extract the archive, and run under a Python
environment with `python-flint==0.9.0`:

```sh
zstd -dc evidence.tar.zst | tar -xf -
python3 -B evidence/verify.py
python3 -B audit_publication.py evidence
```

The full replay passed after archive extraction into a different directory;
[portable-replay.stdout](portable-replay.stdout) retains the result. Neither
auditor invokes an external scientific producer or network. FLINT arithmetic
runs in process. [FLINT-RUNTIME.json](FLINT-RUNTIME.json) pins the runtime used.
The second auditor binds all public mirrors, both full-identity CSVs and the
source-rule summary to that export.

The 65-file export retains all three native attempts and their process and
case framing. Attempt01 stops at a control gate before cohort calls. Attempt02
starts all 147 cohort cells but leaves 46 partial after a reconstruction error
used inexact GP factorials. Attempt03 uses exact factorials and a maximum-degree
control, and all 147 cells finish. Those failures are operational observations;
they do not count as curve rejections. The original paper bytes, scan images,
interpreter and FLINT binaries are excluded explicitly, with exact digests and
retrieval locations retained.

## Derived artifacts and delivery

With ReportLab installed, `python3 -B make_report.py` regenerates the Markdown,
three-page PDF, quantitative SVG and workflow diagram from recorded values.
[workflow.diagram.json](workflow.diagram.json) is editable diagram data. Every
final PDF page was visually inspected. Earlier study figures retain their own
sealed-run scope; no canonical frontier or formal hypothesis state changes.

Canonical object-store delivery was refused with HeadObject403. Exact archive
bytes were pushed in Git under the existing `large-file-ok` PR exception. No
remote store success or green merge-readiness claim is made; the earlier
immutable A/A-record collisions remain a separate publication issue.


## Dated class-number lower bound, 28 October2026 UTC

[Completed source-bound certificate test](../nist_seed_class_number_dated_bound_20261028/certificate-report-01/report.md): all11 omissions and8 published controls prove h(K)>=16,777,216; P-384/P-521 retain UNKNOWN_D_K. The documented200 and10^7 lower bounds reject zero omissions, so contribute no exclusions to a two-rule model. Both implementations, all controls and exports pass. Initial17/4 outputs and prospective P-256 import amendment are retained. No exact class number or1997 adoption is claimed. The P-224 cube/splitting observation and existing signed-action/source graphs remain unchanged.


[Single ideal-class element follow-up, 28 October2026 UTC](../nist_seed_class_number_dated_bound_20261028/element-order-01/report-01/report.md): ETSI's individual-element order>=200 witness passes for all11 omissions and8 publications at the first odd split prime. Every reduced power agrees across2 methods (3,781 per arm). No1997 use, original witness-choice/retry policy or actual selector is established. P384/P521 unknowns remain explicit; previous graphs unchanged.


[May1997 polynomial-degree source and later fix](signed-frobenius-20261027/period-eigenvalue-20261027/eco-code-recovery-01/degree-routines-01/report.md),28October2026UTC: exact old/later bytes and dated2001fix note verified; actualpatch not recovered. Four normalized bodies match; latercaller removesfixedroots. Source-only degree-one invalid-index path is untestednatively/unlinkedtooriginalcaller. Intendeduniform-random valid-input exception bound<2^-174 percall in documentedrange is conditional,not historicalodds. Every21 identity remainsbound;all original applicationsUNDETERMINED;0newnative trials;full selector unresolved.


## Requested stopping point,28October2026

[Final fixed arithmetic pass](../nist_seed_final_checks_20261028/report.md):21 curves checked once;63 original/opposite-root/twist order certificates independently verified;no fixed flag or monotone twist-strength separator. MOV20/100,order/anomalous checks all pass. Investigation loop stopped by user instruction; historical objective unresolved and paused. No further speculative arithmetic or historical-code rounds are scheduled.
