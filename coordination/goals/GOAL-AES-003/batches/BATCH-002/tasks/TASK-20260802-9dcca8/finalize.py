import json,os
D=os.path.dirname(os.path.abspath(__file__))
agg=json.load(open(os.path.join(D,'agg.json')))
rows=agg['rows']
def summ(f):
    s=[r for r in rows if f(r)]
    return {"diagonals_measured":len(s),
     "survivor_count_histogram":{str(k):sum(1 for r in s if r["survivor_count"]==k) for k in sorted(set(r["survivor_count"] for r in s))},
     "diagonals_with_unique_survivor":sum(1 for r in s if r["unique_survivor"]),
     "diagonals_unique_and_equal_true_byte":sum(1 for r in s if r["unique_survivor_is_true_byte"]),
     "diagonals_unique_and_equal_hintkey_byte":sum(1 for r in s if r["unique_survivor_is_hintkey_byte"]),
     "diagonals_true_byte_anywhere_in_survivor_set":sum(1 for r in s if r["true_byte_among_survivors"]),
     "diagonals_hintkey_byte_anywhere_in_survivor_set":sum(1 for r in s if r["hintkey_byte_among_survivors"]),
     "runs":sorted(set(r["run"] for r in s))}
INF={"policy":"executor-implementation","requested_policy":"executor-implementation",
 "resolved_model_id":"claude-opus-5","fallback_used":True,"model_verified":False,
 "model_verification_note":"adapter probe not run; orchestration/model-policies.yaml GPT-5.6 aliases are unresolvable under Claude Code (CLAUDE.md model policy note). The id recorded is the harness-reported model of the executing session.",
 "standing_basis":"0137a051eb5828789eb267fa83c8278086578d4c"}
R={
"schema":"crypto.autoresearch.task_results.v1",
"task_id":"TASK-20260802-9dcca8",
"goal_id":"GOAL-AES-003","batch":"BATCH-002","rank":1,
"title":"The wrong-hint null for the hinted r=6 and r=7 constructions",
"question_id":"RQ-AES-003","decision_refs":["DEC-20260802-007","DEC-20260802-9bda5c"],
"supersedes_nothing":"This task mints no ledger record and changes no status. It reports measurements only.",
"claim_tier":"toy",
"scope_statement":"Reduced-round AES-128 at r=6 and r=7 on one 4-core machine, one target key, hint-assisted. NOTHING here asserts anything about full-round or deployed AES. No comparison to published cryptanalysis is made in either direction (RQ-AES-003 R3).",
"inference":INF,
"environment":agg['env'],
"git_commit_at_task_start":"41414e805b68374bcf40f8cfc0eb796e88ebfc56",
"git_commit_at_results_assembly":agg['env']['git_commit'],
"git_dirty_tree_at_assembly":agg['env']['git_dirty_tree'],
"artifact_hashes":agg['files'],
"object_under_test":{
 "source":"coordination/goals/GOAL-AES-003/batches/BATCH-001/tasks/attack/sq.c (UNMODIFIED, read-only)",
 "variant_used":"sq_null.c in this task directory: a byte-for-byte copy of sq.c with two ADDED modes attack6n/attack7n. The BATCH-001 file was not edited.",
 "what_changed":["hint[d][t] may be taken from a separate hint key (nwrong of the 3 bytes per diagonal)","per-diagonal reporting: survivor count, full survivor list, true byte, hint-key byte"],
 "what_did_not_change":["worker6/worker7 fold","partial-sum tail","survivor test (a k3 survives iff for every row r some k4 remains)","the oracle always encrypts under the TRUE target key","in attack7n the last round key K7 handed to the attack is always the TRUE one"],
 "binary_selftest":{"command":"./sq_null selftest 2b7e151628aed2a6abf7158809cf4f3c 3243f6a8885a308d313198a2e0370734","exit_status":0,"result":"software reference and AES-NI agree at every round 1..10; round-10 output 3925841d02dc09fbdc118597196a0b32 equals the FIPS-197 C.1 known answer"}},
"target_key":"2b7e151628aed2a6abf7158809cf4f3c",
"wrong_keys_used":[l.strip() for l in open(os.path.join(D,'wrong_keys.txt')) if l.strip()],
"wrong_key_origin":"python3 secrets.token_hex(16), generated in this session, independent of the target key; recorded verbatim in wrong_keys.txt",
"structures_per_trial":2,"texts_per_structure":4294967296,
"run_ledger":agg['ledger'],
"per_diagonal_measurements":rows,
"arms":{
 "TRUE6":{"predicted":"P1: survivor_count==1 on all 4 diagonals, survivor == true K6 byte","measured":summ(lambda r:r["run"]=="TRUE6"),"prediction_met":True,
   "reproduces_batch001":"rk_last survivors 253,65,253,122 = fd,41,fd,7a, matching BATCH-001 attack6b_out.json rk_last 6d88a37a110b3efddbf98641ca0093fd"},
 "TRUE7":{"predicted":"P2: survivor_count==1 on all 4 diagonals, survivors == 8034b976","measured":summ(lambda r:r["run"]=="TRUE7"),"prediction_met":True,
   "reproduces_batch001":"survivors 128,52,185,118 = 80,34,b9,76, exactly BATCH-001 attack7_out.json true_K6prime_bytes 8034b976"},
 "WRONG6":{"predicted":"P3: survivor_count==0 on essentially every diagonal","measured":summ(lambda r:r["run"].startswith("WRONG6")),"prediction_met":True,
   "trials_completed":2,"trials_planned":8},
 "WRONG7":{"predicted":"P3: survivor_count==0 on essentially every diagonal","measured":summ(lambda r:r["run"].startswith("WRONG7")),"prediction_met":True,
   "trials_completed":1,"trials_planned":8},
 "PARTIAL_1_OF_3_WRONG":{"predicted":"P4: survivor_count==0","measured":None,"status":"NOT RUN","reason":"budget: the third arm never started before the binding stop"}},
"pooled_wrong_hint_distribution":summ(lambda r:r["nwrong_requested"]==3),
"pooled_true_hint_distribution":summ(lambda r:r["nwrong_requested"]==0),
}
json.dump(R,open(os.path.join(D,'RESULTS_partial.json'),'w'),indent=1)
print(json.dumps(R['pooled_wrong_hint_distribution'],indent=1))
print(json.dumps(R['pooled_true_hint_distribution'],indent=1))
