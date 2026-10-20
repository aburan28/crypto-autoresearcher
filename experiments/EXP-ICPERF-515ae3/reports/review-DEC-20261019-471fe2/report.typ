#set page(paper: "us-letter", margin: (x: 0.72in, y: 0.65in))
#set text(font: "Helvetica Neue", size: 8.5pt)
#set heading(numbering: none)
= Prime63 m=2 retrospective review
*DEC-20261019-471fe2 · EV-ICPERF-3f4a4e · EXP-ICPERF-515ae3 · RUN-ICPERF-eb0d88*

*Decision and scope.* The Coordinator records an inconclusive scientific result and retrospectively classifies this exact experiment attempt as `invalid` for two absent frozen supervisor outputs. DEC-20261019-cf7e51 records the earlier execution start as `approved → running`; DEC-20261019-471fe2 records `running → invalid`. The decisions are dated at review, and do not rewrite the run. Evidence strength: inconclusive. Claim tier: medium for one 63-bit prime-field instance. H-ICPERF-05021b remains approved.

#figure(image("diagram.svg", width: 96%), caption: [Three separately planted positive calls reached the 600 s cap and remain timeout-censored; both frozen run-root outputs are absent. Sources: RUN-ICPERF-eb0d88 receipts; EV-ICPERF-3f4a4e.])

*Observation.* The standard supervisor recorded `invalid_output`, with both required run-root files absent. The child and narrower raw checker exited zero. The injected monitor fault fired as specified. Positive call wall times were 600.148084 s (coset), 600.072356 s (random), and 600.058805 s (small_x), each with no response. Blind Validator P1/P2 independently inventoried 15 raw members, checked the archived planted witness identities and found both output absences. Red Team P3/P4 matched 26 custody entries to original bytes and checked chronology and censors.

*Comparison.* Factor base, target, encoder and equation shape co-vary across arms; every positive call is censored. The displayed stop overhead is not a speed ranking. Archived satisfying input witnesses do not constitute a returned solver certificate. The corrected checker accepted the original Red Team attestation and post-seal Validator clarification only under the external exact-plan SHA-256 pin. Its PASS checks format and declared blindness, not read-history authenticity or scientific validity.

*Inference.* The four review joints hold in their custody and bounded-interpretation scopes. The standard output contract fails, so the trial is invalid. Three positive censors remain observations, not evidence that the polynomial systems lack solutions or that any base is superior. Natural relation yield, useful rank, linear algebra, target recovery, complete cold/online IC cost, matched rho and Bernstein–Lange gap are unmeasured.

*Limitation and next action.* One curve (p=9223372021248595841, r=9223372018953067627), B=475, m=2, three distinct planted targets and one attempt per arm. No transfer to other fields, curves or arities follows. A prospective fresh-ID plan/launcher/checker mapping and standard-supervisor censored and canned-positive fixtures must validate before another scientific run. The output-contract problem stays open.

*Sources and graph check.* EV-ICPERF-3f4a4e; DEC-20261019-cf7e51; DEC-20261019-471fe2; TASK-20261019-bb87e3 and TASK-20261019-02a5c2 sealed reports; TASK-20261019-6398fb four-file snapshot; RUN-ICPERF-eb0d88 receipts. Earlier run graph/source, prime63 integration diagram, and ECDLP frontier inventory were checked and left unchanged because this review adds no validated cost comparison.
