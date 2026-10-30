#set page(paper: "a4", margin: (x: 1.6cm, y: 1.5cm), footer: context align(right, text(size: 8pt, counter(page).display("1"))))
#set text(font: "Liberation Sans", size: 9pt, lang: "en", ligatures: false)
#show raw: set text(font: "Liberation Mono")
#set par(justify: false, leading: 0.55em)
#set heading(numbering: none)
#show heading: set block(above: 0.8em, below: 0.4em)
#heading(level: 1)[#text("F3 second pass: m=4 source prepared, execution pending")]

#text("26 October 2026; TASK-20261026-821d10. This is a prospective engineering report. No second-pass arithmetic panel, pilot measurement or experimental row has run. The frozen protocol, root execution release and successful real S3 checkpoint gate remain prerequisites. A schema or syntax check is not mathematical validation.")
#parbreak()

#text("The new source extends the first-pass three-partition hybrid to four disjoint P-256 partitions of eight points. The candidate joins signed point pair sums through their shared x coordinate, then recovers signs using full point equality. The solver interface receives points and partitions only; labels, Q and the public constructed-control witness do not enter it.")
#parbreak()

#figure(image("diagram.svg", width: 100%, height: 6.4cm, fit: "contain"), caption: [#text("Prospective F3 implementation workflow; no result counts")])

#text("The planned reference is a separately implemented Jacobian oracle that visits every signed quadruple and independently checks labels and recovered-scalar arithmetic. The derived completeness argument is in derivation.md (derivation.md). There is no general Groebner extraction claim or new asymptotic claim.")
#parbreak()

#text("The fixed panel contains eight unplanted SHA-derived labelled bases, using target seeds 202610260301 through 202610260308, and separately constructed useful and zero-Q controls. Every rejected draw and incomplete case must survive in raw records. Natural cases impose no expected dependency count. The useful control discloses its already-known generation witness; the zero-Q control deliberately arranges A=B=0. They test correctness.")
#parbreak()

#text("Declared refusal/premise checks cover forged labels, off-curve inputs, inverse-coordinate duplicates, overlapping partitions, wrong signs, repeated-index cancellation, integer coefficients that vanish modulo r and adaptive-label or label-reading selection premises. The latter audit declared premises and do not detect an undisclosed adaptive construction.")
#parbreak()

#text("The schema requires two arms. The prospective export unit is one algorithm over the entire fixed ten-case panel: a MITM arm and an exhaustive-reference arm, interleaved within each case. They share input construction, postprocessing and a diagnostic process interval. The comparison criterion is exact relation-list equality and valid certificates, not a performance comparison. All native stage counters remain separate. Wall/CPU/RSS values are diagnostic, with wall_valid=false on the shared host.")
#parbreak()

#text("The draft protocol (protocol.draft.json) remains explicitly draft. Root must pin the actual Python executable, committed source, exact curve metadata and analysis source, then freeze and commit protocol.json before data. The executable checks those bytes and invokes the shared serialized checkpoint gate; it has no skip-gate option. An in-process 115-second guard is intended to leave a partial timeout receipt before the declared 120-second external process guard. Such a stop leaves unfinished cases unknown. No in-row process restore is implemented; subsequent attempts need fresh paths and preserve preceding raw records.")
#parbreak()

#text("analysis.py only reads recorded rows and case files. export.py fills the unified export from observed source/interpreter, host, counters and raw-file digests; it does not substitute planned identities for missing observations. The generated run report and diagram will be fresh artifacts after execution, preserving this prospective report. Commands (commands.md) name the exact future entry points. Preparation checks (preparation-checks.json) record software-only syntax/schema/help checks, not arithmetic observations.")
#parbreak()

#text("The source review (literature.md) records the APS primary sections actually read and the inaccessible Kudo chapter. The exact curve record (curve-record.json) identifies the published P-256 field, coefficients, generator and subgroup; its metadata digest is not a primality or group-order proof. Native model binding is unprobed and no canonical review or official research-state transition is claimed.")
#parbreak()

#text("The open question remains a naturally productive structured labelled solver with complete construction, search, recovery and memory costs. Sparse fixed domains and constructed positives alone do not establish that interface. The historical first-pass F3 diagram/counts and aggregate counting screen remain unchanged: no second-pass observation exists to change their measured coverage. This new SVG describes prospective source and gates only.")
#parbreak()
