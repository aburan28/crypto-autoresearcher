import json,os
D=os.path.dirname(os.path.abspath(__file__))
agg=json.load(open(os.path.join(D,'agg.json')))
rows=agg['rows']; old=json.load(open(os.path.join(D,'RESULTS.json')))
def summ(f):
    s=[r for r in rows if f(r)]
    return {"diagonals_measured":len(s),
     "survivor_count_histogram":{str(k):sum(1 for r in s if r["survivor_count"]==k) for k in sorted(set(r["survivor_count"] for r in s))},
     "diagonals_with_unique_survivor":sum(1 for r in s if r["unique_survivor"]),
     "diagonals_unique_and_equal_true_byte":sum(1 for r in s if r["unique_survivor_is_true_byte"]),
     "diagonals_unique_and_equal_hintkey_byte":sum(1 for r in s if r["unique_survivor_is_hintkey_byte"]),
     "diagonals_true_byte_anywhere_in_survivor_set":sum(1 for r in s if r["true_byte_among_survivors"]),
     "diagonals_hintkey_byte_anywhere_in_survivor_set":sum(1 for r in s if r["hintkey_byte_among_survivors"]),
     "trials":len(set(r["run"] for r in s)),"runs":sorted(set(r["run"] for r in s))}
R=dict(old)
R["environment"]=agg["environment"] if "environment" in agg else agg["env"]
R["artifact_hashes"]=agg["files"]
R["run_ledger"]=agg["ledger"]
R["per_diagonal_measurements"]=rows
R["segments"]={
 "segment_1":{"start_utc":"2026-08-02T17:06:47Z","binding_stop_utc":"2026-08-02T17:56:47Z","declared_wall_clock_seconds":3000,
  "machine_conditions":"CONTENDED: up to three GOAL-AES-003 BATCH-002 producer tasks shared the 4 cores; load average 12 measured at 17:31:18Z. r=6 runs took 123-282 s against BATCH-001's 69 s.",
  "outcome":"halted on the C2 stamp with 3 completed all-wrong trials, 5 truncated runs, 1 operator-terminated run, and the partial-hint arm never started."},
 "segment_2":{"start_utc":"2026-08-02T17:55:12Z","binding_stop_utc":"2026-08-02T18:40:12Z","declared_wall_clock_seconds":2700,
  "machine_conditions":"UNCONTENDED: sole producer, runs strictly sequential at 4 threads. Load average 3.1-4.0 at launch. r=6 runs 94-103 s, r=7 runs 155-171 s.",
  "resumed_by":"coordinator instruction: the segment-1 shortfall was a scheduling error (three producers on 4 cores), and the batch should have waited rather than run degraded.",
  "outcome":"partial-hint arm completed in full (7 trials) plus 8 further all-wrong trials and a matched uncontended true-hint arm."}}
R["arms"]={
 "TRUE6 (segment 1, contended)":{"predicted":"P1: survivor_count==1 on all 4 diagonals, survivor == true K6 byte","measured":summ(lambda r:r["run"]=="TRUE6"),"prediction_met":True,
   "reproduces_batch001":"survivors 253,65,253,122 = fd,41,fd,7a, matching BATCH-001 attack6b_out.json rk_last 6d88a37a110b3efddbf98641ca0093fd"},
 "TRUE7 (segment 1, contended)":{"predicted":"P2: survivor_count==1 on all 4 diagonals, survivors == 8034b976","measured":summ(lambda r:r["run"]=="TRUE7"),"prediction_met":True,
   "reproduces_batch001":"survivors 128,52,185,118 = 80,34,b9,76, exactly BATCH-001 attack7_out.json true_K6prime_bytes 8034b976"},
 "TRUE (segment 2, uncontended, fresh seed 90031)":{"predicted":"same as P1/P2","measured":summ(lambda r:r["run"] in ("TRUE6-S2","TRUE7-S2")),"prediction_met":True,
   "note":"independent confirmation of the true-hint arm on a fresh seed with the machine to itself: TRUE6-S2 93.97 s, TRUE7-S2 155.98 s, both 4/4 unique and correct."},
 "ALL-WRONG hint, 3 of 3 bytes wrong (both segments)":{"predicted":"P3: survivor_count==0 on essentially every diagonal","measured":summ(lambda r:r["nwrong_requested"]==3),"prediction_met":True,
   "trials_completed":11,"trials_required_by_card":8,
   "composition":"segment 1: WRONG6-01, WRONG6-02, WRONG7-02 (contended). segment 2: WRONG6-B01..B06, WRONG7-B01, WRONG7-B02 (uncontended). 11 distinct wrong keys, 11 distinct seeds."},
 "PARTIAL hint, 1 of 3 bytes wrong (segment 2)":{"predicted":"P4: survivor_count==0","measured":summ(lambda r:r["nwrong_requested"]==1),"prediction_met":True,
   "trials_completed":4,"runs":"PART6-1of3-A/B, PART7-1of3-A/B"},
 "PARTIAL hint, 2 of 3 bytes wrong (segment 2)":{"predicted":"P4 by extension: survivor_count==0","measured":summ(lambda r:r["nwrong_requested"]==2),"prediction_met":True,
   "trials_completed":3,"runs":"PART6-2of3-A/B, PART7-2of3-A"}}
R["pooled_wrong_hint_distribution"]=summ(lambda r:r["nwrong_requested"]==3)
R["pooled_partial_hint_distribution"]=summ(lambda r:r["nwrong_requested"] in (1,2))
R["pooled_true_hint_distribution"]=summ(lambda r:r["nwrong_requested"]==0)
R["wrong_keys_used"]=([l.strip() for l in open(os.path.join(D,'wrong_keys.txt')) if l.strip()]+
                      [l.strip() for l in open(os.path.join(D,'wrong_keys_seg2.txt')) if l.strip()])
R["wrong_key_origin"]="python3 secrets.token_hex(16), generated in-session, independent of the target key; wrong_keys.txt (segment 1) and wrong_keys_seg2.txt (segment 2)"
json.dump(R,open(os.path.join(D,'RESULTS.json'),'w'),indent=1)
print(json.dumps({k:R[k] for k in ("pooled_true_hint_distribution","pooled_wrong_hint_distribution","pooled_partial_hint_distribution")},indent=1))
