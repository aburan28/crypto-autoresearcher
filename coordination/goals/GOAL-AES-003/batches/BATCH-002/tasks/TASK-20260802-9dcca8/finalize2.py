import json,os
D=os.path.dirname(os.path.abspath(__file__))
R=json.load(open(os.path.join(D,'RESULTS_partial.json')))
R["findings"]=[
 {"id":"F1","label":"measured",
  "statement":"With the hint bytes taken from the TRUE key schedule, both constructions reproduce BATCH-001 exactly in this session on this binary: 8 of 8 diagonals (4 at r=6, 4 at r=7) have exactly ONE surviving byte and it is the CORRECT byte. r=7 survivors are 8034b976, identical to BATCH-001 attack7_out.json."},
 {"id":"F2","label":"measured",
  "statement":"With the hint bytes taken from an INDEPENDENT WRONG key, the filter admits NO survivor at all. Across 12 measured diagonals from 3 completed wrong-hint trials (WRONG6-01 seed 90001, WRONG6-02 seed 90002, WRONG7-02 seed 90002, three distinct wrong keys, all 3 of 3 hint bytes per diagonal actually differing from the true bytes), the survivor-count histogram is {0: 12}. Zero diagonals had a unique survivor; zero had the true byte anywhere in the survivor set; zero had the wrong key's own corresponding byte anywhere in the survivor set."},
 {"id":"F3","label":"interpretation, stated in the strongest honest form the measurement supports",
  "statement":"HYPOTHESIS (B) -- that the filter admits exactly one survivor per diagonal for structural reasons and was correct only because the hint was correct -- IS REFUTED BY THIS MEASUREMENT at the sample size measured. A false hint does not produce a different unique survivor; it produces NO survivor. The uniqueness observed in BATCH-001 is therefore not a structural artefact of the survivor test, and the r=6 and r=7 constructions are consistent with hypothesis (A), hint-assisted isolation of the CORRECT byte.",
  "limits_of_this_statement":["3 completed wrong-hint trials, not the 8 the card required (see incompleteness).","One target key. Wrong keys were fully independent; the near-miss regime (hints wrong in one byte) was NOT tested at all.","This says nothing about whether the constructions are useful: r=6 remains dominated (see carried_forward), and r=7 remains not a key recovery.","Toy tier. Nothing here bears on full-round or deployed AES."]},
 {"id":"F4","label":"measured, secondary",
  "statement":"After the FIRST structure the wrong-hint arms are indistinguishable from the true-hint arm in bulk survivor count (WRONG6-01 4108, WRONG6-02 4177, WRONG7-02 4003, WRONG6-03..07 4047/4004/4102/4102/4127 before truncation, versus TRUE6 4159-equivalent scale and TRUE7 4066). The separation appears only after the SECOND structure, where the true-hint arms retain 16-32 pairs and the wrong-hint arms retain 11-21 pairs that do not survive the four-row consistency test. One structure is therefore not decisive; two are."}]
R["incompleteness_and_dropped_work"]={
 "halted_on_budget":True,
 "binding_stop_utc":"2026-08-02T17:56:47Z",
 "wrong_hint_trials_required_by_card":8,"wrong_hint_trials_completed":3,
 "shortfall_is_real_and_not_softened":"The completion gate asked for at least 8 independent wrong-hint trials. THREE completed. The distribution reported is the full distribution of what was measured, but it is a smaller sample than the card required.",
 "dropped_or_failed_work":[
  {"item":"WRONG6-03,04,05,06,07","status":"resource_exhaustion / budget truncation","detail":"Launched concurrently at 1 thread each at 17:31:54Z after the machine's load average was measured at 12 (other BATCH-002 producer tasks share the 4 cores). All five hit their 1150 s timeout (exit status 124) at 17:46 having completed only structure 0 of 2, so no per-diagonal verdict exists for them. THIS IS NOT NEGATIVE MATHEMATICAL EVIDENCE and is not counted in any distribution."},
  {"item":"WRONG7-01","status":"operator/infrastructure termination","detail":"Started 17:29:19Z at 4 threads. At 17:31:20Z the executor killed its driver's GNU timeout wrapper while re-planning the queue; timeout forwarded SIGTERM and the child died with 0 bytes of output. A protocol deviation by the executor, recorded, not repaired. Relaunched as WRONG7-02, which completed in 627 s and is reported."},
  {"item":"PARTIAL arm (1 of 3 hint bytes wrong), PART6-01/02 and PART7-01","status":"NOT RUN","detail":"Never started before the binding stop. The third arm the card asked for if cheap was NOT cheap on a contended machine and is the main dropped measurement: the question 'does the filter need ALL hint bytes correct, or is it insensitive to some of them' is UNANSWERED by this task."},
  {"item":"WRONG6 trials 06..08 and WRONG7 trials 03..08","status":"NOT RUN","detail":"Budget."}],
 "checks_that_did_not_run":[
  {"check":"partial-wrong-hint arm","reason":"budget; binding stop reached"},
  {"check":"second target key","reason":"not planned; out of scope of the preregistration"},
  {"check":"adapter model probe","reason":"no resolvable adapter under this harness; model_verified false"},
  {"check":"independent re-verification certificate","reason":"certificate.kind is none for this task: it is a pure measurement of survivor counts and claims no solve and no relation. The true-hint arms reproduce BATCH-001's certified bytes but this task mints no new certificate."}],
 "budget_note":"Executor halted on the C2 stamp. Per the card, halting on the stamp is full compliance; the shortfall in trial count is reported here rather than concealed."}
R["certificate"]={"kind":"none","basis":"pure measurement run: survivor counts under true and false hints. No discrete-log solve, no factor-base relation, no new key-recovery claim."}
R["carried_forward_unchanged_from_BATCH-001"]={
 "statement":"The r=6 key recovery WORKS AND IS DOMINATED. It requires 12 hint bytes and, by BATCH-001's own measured numbers, costs 69.39 s against roughly 25 s for exhaustive search over the same hinted residual.",
 "dominated_by":"exhaustive search over the hinted residual","sota_delta":"NEGATIVE",
 "label":"MEASURED BY BATCH-001, NOT RE-MEASURED HERE. This task did not re-run the cost comparison and reports no cost measurement of its own; its own wall times were taken on a contended machine and are not cost measurements.",
 "r7_status":"The r=7 run is NOT a key recovery and carries no certificate: the true last round key K7 is supplied as input in BATCH-001 and in every arm here.",
 "correction_ref":"CORR-20260802-003"}
R["what_this_task_does_not_do"]=[
 "It does not declare any hypothesis supported, rejected or closed; that is the Reviewer's and Coordinator's judgment.",
 "It asserts nothing about full-round or deployed AES.",
 "It makes no comparison to published cryptanalysis in either direction.",
 "It does not revisit the r=4 / r=5 relabelling; that stands as BATCH-001 recorded it."]
json.dump(R,open(os.path.join(D,'RESULTS.json'),'w'),indent=1)
print("written",os.path.getsize(os.path.join(D,'RESULTS.json')))
