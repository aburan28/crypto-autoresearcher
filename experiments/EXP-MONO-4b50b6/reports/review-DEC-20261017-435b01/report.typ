#set document(title: "Decision report DEC-20261017-435b01", author: "Coordinator, crypto-autoresearcher")
#set page(paper: "a4", margin: (x: 2cm, y: 2cm), numbering: "1 / 1")
#set text(size: 9.5pt)
#set par(justify: false, leading: 0.6em)
#show heading.where(level: 2): set text(size: 11pt)
#let vb(body) = block(fill: luma(244), inset: 7pt, radius: 3pt, width: 100%, body)

= Decision report: DEC-20261017-435b01
GOAL-MONO-001 · lane BATCH-3186a5 (closes BATCH-450ac7) · produced by TASK-20261017-5aa462 · 2026-10-17

== Status
This decision is a *conditional adoption*. It takes effect only when the ledger archive TASK-20261017-517bbe commits and verifies with conditions AC-1 to AC-6 holding. Until then nothing here is official. GOAL-MONO-001 status is unchanged: it stays active, because the J4 DISSENT of TASK-20260930-40470a is recorded and outstanding and a recorded DISSENT blocks closure.

== Decision
Decision label, verbatim (DEC-20261017-435b01 decision_label):
#vb[#"CONDITIONAL ADOPTION OF ROUTE (c). Subject to conditions AC-1 to AC-6, all of which must hold in the single ledger archive TASK-20261017-517bbe: the scoped instrument no-go is adopted as GOAL-MONO-001 completion criterion (c), \"a scoped instrument/protocol no-go is recorded\". The instrument is the generic-fibre Frobenius cycle-type census in the frozen EXP-MONO-4b50b6 form, AS A PROBE OF INDEX-CALCULUS RELATION RATE. It is a no-go by derivation for every m >= 3 with p > 3, at toy tier. The question is not closed. The J2 and J3 DISSENTs of TASK-20260930-40470a are superseded on the merits. The J4 DISSENT persists. GOAL-MONO-001 STATUS IS NOT CHANGED: it stays active, because a recorded DISSENT blocks closure."]
- *Decision vocabulary:* `reject_scoped` (the instrument is rejected as a relation-rate probe; the question stays open).
- *Evidence strength:* replicated, by CORR-20261017-4ac525 (EV-MONO-1ef611, read with CORR-20261005-a53ac8).
- *Claim tier:* toy (#"Not an ECDLP result. No security estimate moves in either direction, and no curve is called weak.").
- *Scoped claim:* EV-MONO-1ef611 obstruction.scope (i), as closed by DEC-20261017-435b01:
#vb[#"Only the generic-fibre Frobenius cycle-type census in the frozen EXP-MONO-4b50b6 form, as a probe of index-calculus relation rate, on the factor-base locus (p > 3, E/F_p nonsingular, x_i = x(P_i) with P_1..P_{m-1} in E(F_p) affine), for every m >= 3 by derivation."]
read with CS-D2 below.

== Observation
The review TASK-20261016-9c1bc5 (validator-breakthrough, effort max, fresh session, zero runs; snapshot-archived by TASK-20261016-548959) measured, on the factor-base locus, the fraction of generic fibres with non-trivial Frobenius. Every value below is read by key from its computations.json and agrees with review_report.md Part 1.3 Checks 2 and 4.
#table(columns: 5, stroke: 0.4pt + luma(200), inset: 4pt,
  [*cell*], [*p*], [*generic fibres N*], [*non-trivial*], [*95% upper bound (derived)*],
  [A m=3], [131], [4,830], [0], [0.00062],
  [A m=4], [131], [278,496], [0], [1.08e-05],
  [D m=3], [61], [1,122], [0], [0.00267],
  [D m=4], [61], [30,600], [0], [9.79e-05],
  [B m=5], [1999], [24], [0], [0.117],
  [C m=5], [1009], [23], [0], [0.122],
  [A m=5], [131], [7], [0], [0.348],
)
Totals reported by the review (Part 1.3): 439,829 base tuples at m in {3, 4, 5} on four curves at p in {61, 131, 1009, 1999}; 316,290 generic fibres; 0 with non-trivial Frobenius. RUN-MONO-4b50b6-002 V4 at m=3: 1,196 off-diagonal factor-base pairs, 0 non-split, as EV-MONO-a0a89c OBS-4 records it.

#figure(image("obstruction.svg", width: 100%), caption: [Fraction of generic fibres with non-trivial Frobenius, on the factor-base locus (blue; thin lines are derived one-sided 95% bounds $1 - 0.05^(1\/N)$ for 0 of $N$) and off the locus (orange; the proves-too-much null object 1 of review_report.md Part 5). Reference line at 0: by derivation. Data: obstruction-data.json; regenerate with plot.py.])

== Comparison
Off the locus the same statistic varies. Proves-too-much object 1 (review_report.md Part 5), read by key:
#table(columns: 4, stroke: 0.4pt + luma(200), inset: 4pt,
  [*set*], [*generic fibres*], [*non-trivial*], [*fraction (measured)*],
  [A m=3 all of F_p^2 (p=131)], [16,256], [8,120], [0.500],
  [D m=4 all of F_p^3 (p=61)], [191,688], [148,512], [0.775],
  [B m=4 20,000 random (p=1999)], [19,907], [14,888], [0.748],
)
The constancy on the locus is therefore a locus effect, and the generic tuple is the null object of the same shape (review_report.md Part 5, Result).

== Inference
As decided in DEC-20261017-435b01 (composition route_c; closure_gate_check), not added here: the census in the frozen EXP-MONO-4b50b6 form cannot discriminate relation rate on the factor-base locus, because its value there is 0 by derivation for every m >= 3 with p > 3. Route (a), verbatim:
#vb[#"NOT ADOPTABLE in this round (CU7-C2). The J4 DISSENT of TASK-20260930-40470a is untouched (CU7-C3) and persists (A01 K1e)."]
Why the goal is not completed, verbatim:
#vb[#"Plan entry C-4 (DEC-20260810-2f86db N-1) expected that on adoption \"GOAL-MONO-001 moves to completed under criterion (c) ... together with the KN-OPEN-009 supersession\". AGENTS.md \"Goal closure quorum (suspended)\" still binds: \"a recorded DISSENT blocks closure\". So does docs/agent-contract-extended.md: \"A single DISSENT blocks closure. It is not outvoted; it stands until a new Coordinator decision supersedes it on the merits\". The J4 DISSENT of TASK-20260930-40470a is recorded and outstanding. This decision does not supersede it, because no fresh rule-12 review of the route-(a) object exists (A01 K1e). AGENTS.md wins over C-4 where they differ. Criterion (c) is recorded met on effect, and the goal is not moved to completed. The KN-OPEN-009 supersession still lands with the adoption (AC-3). This is the part of C-4 that concerns the no-go's promotion. Its goal-closure part is deferred (PD-A)."]

== Limitation
- #"CS-C10. One reviewer owned every joint, so the round has coverage but no cross-reviewer independence. Model independence holds only as reported: claude-fable-5-1 against claude-opus-5-5. No identifier is probe-verified."
- #"Blind ordering is self-attested (independence_ruling). AC-1 checks only internal consistency."
- #"Semaev 2004 Theorem 1 was retrieved once (TASK-20260930-40470a). CU-7 could not retrieve it (HTTP 403, a tooling failure under RC-6) and verified its content on its own S_3 to S_5. The m >= 6 extent rests on the theorem as read once, which is acceptable for a derivation-tier record."
- #"This composer holds no shell. Every digest, checker output and git fact is taken from committed files or the top-level session's reports. It read the predecessor report only at G-3 (by search) and read computations.json only at the keys cited."
- #"Toy primes only (13 to 1999 across CU-7; 101 to 1999 in the predecessor; 211 to 1601 in BATCH-003). No claim at cryptographic scale. No ECDLP result. No security estimate moves."
- #"Two lanes (BATCH-450ac7 and BATCH-3186a5) stay open together until the 517bbe archive verifies and BATCH-450ac7 is closed. Neither holds a live claim at writing. Claims stay within max_concurrent 1."
- Transfer and extrapolation, verbatim: #"Extension to every m >= 3: a derivation, not an extrapolation of measurements (Q-B). No transfer is asserted to F_{q^n}, to Gaudry/Diem factor bases, to other statistics, or to cryptographic scale. The R2 compounding clause is an untested extrapolation and is not asserted (CS-D2)."

== Counter-statements (carried verbatim, AC-2)
*CS-QA* (#"O-4 / Q-A (i), A01 K3b-K3c, CU7-C4")
#vb[#"DEC-20260904-dd58c3 next_action item (3) and the goal-head line next_action_2026_09_04 'DECISIVELY CONFIRMED' are read under DEC-20260904-dd58c3's own scope_statement: full S_4 monodromy at m=4 over the SYMMETRIC base, at toy scale, on 4 curves at 2 primes. Neither establishes the absence of an exceptional locus at m=4 for every curve; the uniform-in-curve statement is so far a single-reviewer derivation (DEC-20260930-8553d4 CU-9) that no committed record has re-derived. This closure neither rests on nor asserts those statements, and asserts nothing about monodromy on KN-OPEN-009's ordered base (A01 K1d)."]
*CS-N1* (#"N-1 (sub-threshold J2 finding), A01 K3b-K3c")
#vb[#"EV-MONO-1ef611 resource_check R1's sentence \"any discriminating content left in a relation-search statistic on that locus must therefore come from factor-base membership, and factor-base membership is what the D-4 count measures\" is read with one added clause: \"or from the root-multiplicity structure of the fibre, which is also non-constant on the locus (SC-1; IDEA-20260805-90df50)\". R1 remains a design input only; nothing here states that the D-4 count or the root-multiplicity structure discriminates."]
*CS-K1d* (#"A01 K1d; CU7-C7")
#vb[#"Nothing in this adoption states or implies that GOAL-MONO-001 criterion (a) is met, or that the monodromy on KN-OPEN-009's ordered base is full symmetric or wreath. The J4 DISSENT of TASK-20260930-40470a against route (a) is carried by reference and persists."]
*CS-D2* (#"O-2 (DEC-20260810-2f86db D-2; DEC-20260930-8553d4 CU-2); CU7-C7")
#vb[#"What is closed is the generic-fibre Frobenius cycle-type census, in the frozen instrument form of EXP-MONO-4b50b6, as a probe of index-calculus relation rate. The relation-rate question is NOT closed, the relation-supply half of KN-OPEN-009 is NOT answered, and no other statistic is closed. The D-4 factor-base-point count is not condemned, at any m. EV-MONO-1ef611 resource_check R2 (IDEA-20260803-ff7415) is an open, untested lead only: the transfer from F_p to F_{q^n} is an untested extrapolation and no exponent statement is made."]
*CS-QB* (#"Q-B; J3 composer notes; closure-gate error-statement note")
#vb[#"The obstruction value is 0, an exact dimensionless fraction, by derivation, for every m >= 3 with p > 3, nonsingular E/F_p and affine P_1..P_{m-1} in E(F_p). The \"every m\" extent rests on the derivation alone (the group law and Semaev 2004 Theorem 1, retrieved by TASK-20260930-40470a, recalled in TASK-20261016-9c1bc5). Measured corroboration, all with zero exceptions and all at toy primes: m=3 in RUN-MONO-4b50b6-002 V4 (1,196 off-diagonal factor-base pairs, as EV-MONO-a0a89c OBS-4 records it); the TASK-20260930-40470a review computations at m=3 and m=4 exhaustive on two curves and m=5 at random (2,401 + 117,649 + 10,404 + 182,104 exhaustive tuples, as TASK-20261016-9c1bc5 review_report.md Part 4 reads them by key); and the TASK-20261016-9c1bc5 blind computations, 439,829 base tuples with 316,290 generic fibres at m in {3, 4, 5} on four curves at p in {61, 131, 1009, 1999}. No m >= 6 and no prime above 1999 is measured."]
*CS-C10* (#"plan C-10 (repeated as required)")
#vb[#"Independence is by session and role. By model it holds only as reported: the CU-7 reviewer reported claude-fable-5-1; the producers, the predecessor reviewer, the A01 author and this composer report claude-opus-5-5. No identifier is probe-verified. One reviewer owned every joint (plan PD-1), which buys coverage, not cross-reviewer independence."]

== Independence ruling
Checker output, verbatim: 
#vb[#"tools/check_review_independence.py --plan ledger/handoffs/TASK-20261016-9c1bc5.yaml --reports .../review_attestation.yaml, exit 1, verbatim in the TASK-20261016-548959 snapshot receipt: \"re-deriver TASK-20261016-9c1bc5 read 1 blind_from path(s) -- coordination/goals/GOAL-MONO-001/review/TASK-20260930-40470a/\". The same single problem appears in the reviewer's self-run (computations.json independence_check_self_run)."]
Ruling, verbatim:
#vb[#"ACCEPTED AS THE PLAN'S DELIBERATE SEQUENCED LIFT. NOT AN INDEPENDENCE FAILURE. The ruling rests on the plan text, not on the reviewer's word. (1) The plan declares the lift BEFORE any reviewer ran. blindness.lifted_for names TASK-20261016-9c1bc5, and its rationale says \"The reviewer is blind to coordination/goals/GOAL-MONO-001/review/TASK-20260930-40470a/ until its blind re-derivation section and outputs are written ... After that it may read the predecessor report\". blind_rederivation.blind_from_note says \"The third path is blind until the blind section is complete\". RC-2 orders the work that way. inputs_note lists the two predecessor files as SEQUENCED inputs. PD-2 declares the lift \"so that tools/check_review_independence.py and the composer can read it as deliberate\". (2) The checker computes a flat intersection between sources_read and blind_from. It has no representation of order (tools/check_review_independence.py lines 1012-1028). Its FAIL is therefore exactly what the plan's own design produces when the reviewer reads what the plan told it to read. (3) The only path flagged is the third one. The two producer paths that stay blind throughout, experiments/EXP-MONO-4b50b6/ and coordination/goals/GOAL-MONO-001/batches/BATCH-003/, are not flagged, so sources_read names neither. (4) The report's own evidence of order: the attestation's sources_read carries a \"--- blind section frozen here (2026-10-16T17:25:53Z) ---\" marker before the first predecessor path, and computations.json records blind.frozen_at_utc 2026-10-16T17:25:53Z and blind.frozen_section_sha256 244bca5607c005444c7c2893fb13d419abc3e3da2d25fabe2ebe79aa39c50afb. That freeze time lies inside the session window the runtime receipt records (launch about 17:06Z, report received before 17:55Z). (5) The blind section is substantively disjoint from the predecessor's (Part 1a). It uses curves A, B, C and D, none of the predecessor's C1 to C5 and not the producers' p=211 curve. It builds S_5 by a different route (a formal-degree Sylvester determinant interpolated over F_p, with no PARI or FLINT). Its specialisation argument also differs (a morphism E^{m-1} -> P^1 and the regularity of mu, against the predecessor's curve germ and Gauss's lemma). A replication of the predecessor would be unlikely to differ on all three."]
What the ruling does not establish, verbatim:
#vb[#"The ORDER of work is self-attested. No commit or external timestamp separates the freeze from the unblinding. The frozen hash and the freeze time sit inside the reviewer's own computations.json. The ruling accepts the order on the plan's declared design and on corroborating evidence. It does not claim the order was externally verified. AC-1 makes the one cheap mechanical cross-check: the embedded frozen text must hash to the recorded value and must agree with report Parts 0 and 1."]

== Canonical graphs checked
knowledge/frontiers/ecdlp/: README.md, KR-IC-1fcdbc, KR-IC-5765d2, KR-IC-5931ee, KR-IC-5a43e5, KR-IC-889857, KR-IC-955fd6, KR-IC-fbdb61 and KR-RHO-53c89f were checked and are *unchanged*. None mentions monodromy, GOAL-MONO, KN-OPEN-009 or a Frobenius cycle-type census; this decision is a toy-tier instrument no-go with no cost claim, so no frontier row moves. No scope finding.

== Next actions
*NA-1* (#"coordinator (shell-holding top-level session; archive and mechanical production; no status authority)"):
#vb[#"Commit the BATCH-3186a5 queue alone (517bbe LA-1) and open lane BATCH-3186a5. Then run TASK-20261017-df5651 (CORR-20261017-4ac525, KN-FIND-4f0d84, KN-OPEN-8a7432 and the two superseded_by edits) and TASK-20261017-5aa462 (decision report, graph and PDF). Then run the ledger archive TASK-20261017-517bbe alone, checking AC-1 to AC-6. Verify it, push, and open or refresh the PR. Then close lane BATCH-450ac7 with outcome archived, naming the 517bbe commit."]
Declared successor (not an additional next action):
#vb[#"After the archive verifies, a fresh Coordinator session reranks GOAL-MONO-001. Candidate S-1: a pre-review plan and a fresh rule-12 review-breakthrough review of the route-(a) question, including the CU-9 derivations J4 rests on, at zero runs. It is the only act that can dispose of J4 and make goal closure decidable, and it bears on KN-OPEN-8a7432 Q2. Candidate S-2: design IDEA-20260803-ff7415 (R2, KN-OPEN-8a7432 Q3), paired with a heuristic-validation experiment at target scale (agents/coordinator.md \"Dispatch bias\"). Provisional order is S-1 then S-2, because S-1 is decision-changing for this goal and S-2 is the lane's only exponent-relevant lead. The rerank decides. Recheck: tools/goal_lanes.py lanes GOAL-MONO-001 shows BATCH-450ac7 closed archived."]

== Records
EV-MONO-1ef611 · CORR-20261005-a53ac8 · CORR-20261017-4ac525 · DEC-20261017-435b01 · DEC-20260810-2f86db · RUN-MONO-4b50b6-002 · EV-MONO-a0a89c · TASK-20261016-9c1bc5 · TASK-20261016-548959 · TASK-20260930-40470a · KN-FIND-4f0d84 · KN-OPEN-8a7432 · REVIEW-MONO-20261016-9c1bc5.
