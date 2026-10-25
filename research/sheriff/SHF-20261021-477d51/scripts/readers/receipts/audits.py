#!/usr/bin/env python3
"""Summarise the six producer audit.json files (SHF-20261021-477d51 receipts reader): file hashes
vs the files on disk, replayed seqs -> arm/role/target_index, auditor vs producer identity."""
import datetime, hashlib, json, sys
from collections import Counter, OrderedDict
B = sys.argv[1]
out = OrderedDict()
for s in ["c24", "c28", "c30", "r24", "r26", "r28"]:
    a = json.load(open(f"{B}/sessions/{s}.audit.json"))
    sess = json.load(open(f"{B}/sessions/{s}/session.json"))
    host = json.load(open(f"{B}/sessions/{s}/host.json"))
    recs = {}
    for l in open(f"{B}/sessions/{s}/records.jsonl"):
        r = json.loads(l)
        recs[r["seq"]] = r
    files_ok = {f: hashlib.sha256(open(f"{B}/sessions/{s}/{f}", "rb").read()).hexdigest() == h for f, h in a["files"].items()}
    reps = []
    for rp in a["replays"]:
        r = recs[rp["seq"]]
        reps.append({"seq": rp["seq"], "record_id_matches": r["record_id"] == rp["record_id"], "arm": r["arm"],
                     "role": r["role"], "warmup": r["warmup"], "round": r["round"], "target_index": r["workload"]["target_index"],
                     "reproduced": rp["reproduced"], "detail": rp["detail"]})
    ts = lambda ms: datetime.datetime.fromtimestamp(ms / 1000, datetime.timezone.utc).isoformat()
    out[s] = OrderedDict(
        ok=a["ok"], problems=a["problems"], checks_all_true=all(a["checks"].values()), records=a["records"],
        verified_records=a["verified_records"], regraded=a["regraded"], n_replays=len(a["replays"]),
        replay_seqs=[rp["seq"] for rp in a["replays"]], replay_arms=dict(Counter(x["arm"] for x in reps)),
        replay_rounds=dict(Counter(x["round"] for x in reps)),
        replay_record_ids_match=all(x["record_id_matches"] for x in reps), all_reproduced_identical=all(x["reproduced"] and x["detail"] == "identical" for x in reps),
        file_hashes_match_disk=files_ok, audit_session_id_ok=a["session_id"] == sess["session_id"],
        auditor_binary_eq_producer=a["auditor_binary_sha256"] == sess["binary_sha256"],
        auditor_env_eq_producer=a["auditor_env_class_id"] == sess["env_class_id"],
        auditor_hw_class=a.get("auditor_hardware_class_id"), producer_hw_class=host.get("hardware_class_id"),
        audited_utc=ts(a["audited_unix_ms"]), session_finished_utc=ts(sess["finished_unix_ms"]))
json.dump(out, open(sys.argv[2], "w"), indent=1)
for s, v in out.items():
    print(s, {k: v[k] for k in ("ok", "n_replays", "replay_arms", "replay_rounds", "replay_record_ids_match", "all_reproduced_identical", "auditor_binary_eq_producer", "auditor_env_eq_producer", "auditor_hw_class", "producer_hw_class", "audited_utc", "session_finished_utc")}, "files_ok", all(v["file_hashes_match_disk"].values()))
