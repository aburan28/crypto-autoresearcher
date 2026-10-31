#set page(paper: "us-letter", margin: (x: 0.72in, y: 0.67in))
#set text(font: "Helvetica Neue", size: 9pt)
#set heading(numbering: none)
= Operational checker review: DEC-20261019-3bf0cd
*EXP-ICPERF-515ae3 · GOAL-ICPERF-e6b6a4 · Claim tier: operational checker admission only*

*Decision.* `accept_tool_gate_scoped` applies to the corrected CLI with external P1–P4 plan SHA-256 `1242a62527951bd0f2bb7f908fd2be50e85dcd79cf7a0db0dd09d69de64a29db` and the two archived attestation inputs. It does not decide the P1–P4 scientific joints. Evidence: independent, bounded synthetic mutation review in TASK-20261019-52baee, archived by TASK-20261019-a0ad65.

#figure(image("diagram.svg", width: 100%), caption: [Observed synthetic tool controls: one frozen baseline accepted; 20 false fixtures rejected. Source: TASK-20261019-52baee. Counts are cases, not ECDLP solver trials.])

*Observation.* Eight false cases were refused at external pin/plan admission (two pin, six plan mutations); twelve were refused at attestation, verdict or blindness composition. The root session reran the exact pinned P1–P4 and V1/V2 commands; both returned PASS.

*Comparison.* DEC-20261019-da1c84 refused the earlier checker after three false acceptances. The corrected pinned CLI rejects those classes. This is a tool admission correction, with no measured IC cost comparison.

*Inference.* The Coordinator allows a later separately admitted retrospective P1–P4 composition. Direct `check()` on an arbitrary plan is outside this gate: a missing `joint` key or one-character nonempty statement can pass. Review read histories and model identity are attestations. The sealed reviewer labels its role validator while its handoff says reviewer; both identifiers remain visible in DEC-20261019-3bf0cd.

*Limitations.* RUN-ICPERF-eb0d88 remains `invalid_output`; two frozen outputs are missing and three positive calls remain timeout-censored. Natural yield, useful rank, linear algebra, complete IC cost and rho gap remain unmeasured. The temporary mutation fixture bytes were not archived. This report is a delayed visual sidecar under TASK-20261019-ffb51e, following the timing deviation in DEC-20261019-3bf0cd.

*Next.* Verify this sidecar receipt, then bind it and the decision receipt into an additive final-admission queue with the exact external pin before TASK-20261019-6398fb is claimed. Existing run and frontier diagrams were checked and left unchanged because this decision changes no scientific measurement or route.

*Sources.* DEC-20261019-3bf0cd; TASK-20261019-52baee report and attestation; TASK-20261019-a0ad65 snapshot and ledger receipts; TASK-20261019-52baee completed release.
