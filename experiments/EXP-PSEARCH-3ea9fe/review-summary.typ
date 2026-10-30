#set page(paper: "a4", margin: (x: 15mm, y: 13mm), numbering: "1")
#set text(font: "DejaVu Sans", size: 9pt, fill: rgb("172b3a"))
#set par(justify: false, leading: 0.56em, spacing: 0.65em)
#set heading(numbering: none)
#show heading.where(level: 1): set text(size: 17pt)
#show heading.where(level: 2): set text(size: 11pt)
#show table.cell: set text(size: 8.5pt)
= Prefix-search comparison
#text(size: 8pt)[DEC-20261030-0c834c · EXP-PSEARCH-3ea9fe · RUN-PSEARCH-c61489]

*The finite mechanism criterion is met; a total-cost advantage remains unestablished.* Of 48 ordinary matched triples,46 produced a checked genuine partial-prefix refutation and fewer complete-model callbacks. All 48 complete projected sets match independently checked reference certificates. The decision recommends separately admitted replication after strategy/accounting refinement; it authorizes no execution or unchanged scaling.

== Fixed scope and outcome
The 12 public inputs use F17: $y^2=x^3+2x+2$ and F97: $y^2=x^3+x+4$, digit widths 2,3 and the first three affine x representatives with least nonzero ordinate. Each retains quartic, membership, quadratic and quadratic\_aa encodings, with model-only, partial-prefix and candidate A/A strategies. *144 searches + 9 solver controls + 12 references = 165 executions.* All 153 solver transcripts completed; none was censored or missing.

Cadical195/python-sat1.9.dev17 uses degree 2, 256 admitted rows and 512 PC calls per arm;20000 decisions/conflicts per solve call and frozen outer-call/watchdog limits. Only theory-call timing changes: the candidate also checks eligible contiguous LSB prefixes while assigned\_count less than n and depth less than n. The nonlazy propagator and external-clause path remain shared.

#figure(image("review-summary.svg", width: 100%), caption: none)

The bars sum 12 fixed pairs per encoding; the candidate strategy A/A repeat is excluded. Quadratic\_aa is a specified encoding, not an extra replication of this graph. The two ties are c05/quartic (F17,s3,target\[5,1\]) and c11/quartic (F97,s3,target\[4,13\]): each 64→64 callbacks, with zero partial proofs. These are descriptive event totals, not timing or independent population samples.

*5208 identities checked:* 5196 ordinary + 12 control. Candidate and strategy A/A have 882 genuine partial proofs each. All 48 ordinary A/A comparisons match exactly; native 51 additionally includes three synthetic classes. Positive-prefix, empty-clause and viable-prefix controls pass; three false multiplier/clause/model mutations are rejected. No search leaf fallback occurred. Twelve references contain 9 projections, repeated across four encodings as 36 per strategy. This certifies projected sets, not all auxiliary roots or scalar recovery.

#pagebreak()
== Fewer model checks do not settle cost
#table(columns: (2.5fr, 1fr, 1fr), inset: 4pt, stroke: 0.4pt + rgb("ccd5dc"), fill: (x,y) => if y == 0 {rgb("eef3f6")} else {none},
 [*Recorded unit; 48 ordinary rows*], [*Model-only*], [*Partial-prefix*],
 [Complete-model callbacks], [1768], [886],
 [PC calls], [1954], [1954],
 [Search coefficient multiplications], [981664], [981664],
 [Search coefficient additions], [695814], [695814],
 [Evaluation-term visits], [87287], [46532],
 [Duplicate-prefix visits], [3498], [8111],
 [Prefix scans], [37142], [41563],
)
UNKNOWN remains 222, row-capped calls 12, and restriction-term visits 94016 per ordinary strategy. Arithmetic counters omit some primitives; native/Python work, memory, serialization and fsync are not fully counted. Reference instrumentation has separate source-event units. No pooled cost, runtime ranking, new degree-of-regularity result, novelty, formal proof or general ECDLP advantage follows.

== Actual independent review and correction
All seven sealed review joints hold. One fresh reviewer separately implemented restriction, multiplier, sparse-coverage, reference-certificate and paired-value checks, sharing frozen polynomial construction. It ran one allowed native verifier invocation and no search replay. Native independence and review-schema gates passed. This is source/transcript/certificate consistency, not universal solver correctness or authenticated callback execution.

Raw-before-export clock/hash ordering is local attestation, not an independent timestamp/archive proof. The pre-export receipt-status correction and other check-development failures are retained. Requested native Codex gpt-6.1-sol/xhigh/fork-none was prospectively admitted; actual serving model/provider/UUID/effective effort remain unverified.

The first export failed because six bundle rows used instance\_id=fixed\_inventory. A *post-data packaging adapter* changes only that label to protocol instance string0. The reviewer checked all six actual rows: seed 0, replicate 0 and all other fields are unchanged; old labels reproduce all six native errors. The frozen helper and protocol remain unchanged; validation passes and the original failure is retained. The entire export command is not claimed frozen. Six bundles and 786 file entries are packaging units, not observations.

== Decision and next action
Recommend a strategy design addressing repeated prefix traversal and avoidable arithmetic calls before a separately frozen held-out comparison. Retain all four encodings, exact identities/projected completeness, A/A/controls, the charged complementary-point baseline and separate setup/search/verification/reconstruction/I/O accounting. *Do not scale the unchanged experiment on callback counts.* No new launch or H/EV/KN/goal transition is authorized; knowledge promotion is not warranted by this single finite observation. Historical PNEXT invalid\_output remains unchanged. The general prime-field ECDLP objective remains open.

#text(size: 7.4pt)[Sources: sealed review/recompute/attestation in reviews/TASK-20261030-ae3dc7; hashes and actual native receipts in review-inputs.json. Review 12e815fb4ef1abbea4c37dcedf6b48c1814884af; release 6b4d3480db; ledger claim 854ba05c27. Source b2080b14a1; protocol source 3b39d45f4e033f2bc74abc420ef133466fbe65ae; canonical protocol hash b66fb751d2cf5ce1899970a7476df9e5dbaad1661801694204d2dc7d803c271c. PDF inspection and exact ten-path archive remain root-owned pending steps at composition. Current native ledger-record validation governs; the separate legacy JSON decision schema cannot express current hex IDs/knowledge\_promotion and is unchanged.]
