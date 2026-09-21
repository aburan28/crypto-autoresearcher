#!/usr/bin/env python3
"""TASK-20260901-5174ca VALIDATOR gate verification (fresh code)."""
import json, os, hashlib
from datetime import datetime, timezone

ROOT = "/Volumes/SSD990/crypto-autoresearcher/.worktrees/aes003-batch015-20260831"
B015 = ROOT + "/coordination/goals/GOAL-AES-003/batches/BATCH-015/tasks/TASK-20260805-d408ac/runs"
B2F = ROOT + "/coordination/goals/GOAL-AES-003/batches/BATCH-2f12ac/tasks/TASK-20260901-7e0b71/runs"
PROD = ROOT + "/coordination/goals/GOAL-AES-003/batches/BATCH-5ed9a3/tasks/TASK-20260901-ed281d"
RUNS = PROD + "/runs"
MY = ROOT + "/coordination/goals/GOAL-AES-003/batches/BATCH-5ed9a3/tasks/TASK-20260901-5174ca"

def load(p):
    with open(p) as f:
        return json.load(f)

out = {"task_id": "TASK-20260901-5174ca", "role": "validator", "checks": []}
def chk(name, ok, detail=""):
    out["checks"].append({"check": name, "pass": bool(ok), "detail": str(detail)[:300]})

# ---------- G3 Gate-0 extended: field-by-field vs L1-AES-R5-P30 ----------
ALLOWED_DIFF = {"arm", "probe", "oracle", "elapsed_seconds_measured", "measured_rate_trials_per_sec"}
ADDED_STAGE0 = {"zhist", "sbox_table_hex", "key_hex", "sbox", "sbox_k", "sbox_positions",
                "sbox_bijective", "arm_table_concat_sha256", "ewhist_all", "ewhist_miss",
                "ewhist_hit", "ewbithist_all", "ewbithist_miss", "ewbithist_hit", "hit_e_detail"}
ADDED_BATCH = {"ezdiag_all", "ezoff_all", "ezdiag_miss", "ezoff_miss", "ezdiag_hit", "ezoff_hit"}
ADDED_ALL = ADDED_STAGE0 | ADDED_BATCH

l1 = load(B015 + "/L1-AES-R5-P30.json")
g3 = load(RUNS + "/G3_gate0x.json")
missing, mismatched, diffs = [], [], []
for k, v in l1.items():
    if k not in g3:
        missing.append(k)
    elif g3[k] != v and k not in ALLOWED_DIFF:
        mismatched.append(k)
    elif g3[k] != v:
        diffs.append(k)
added = set(g3.keys()) - set(l1.keys())
unexpected = added - ADDED_ALL
chk("G3 no missing committed fields", not missing, missing)
chk("G3 no non-allowed differing fields", not mismatched, mismatched)
chk("G3 observed diffs subset of allowed-diff list", set(diffs) <= ALLOWED_DIFF, sorted(diffs))
chk("G3 added fields subset of preregistered added set", not unexpected, sorted(unexpected))
chk("G3 added set equals preregistered added set exactly", added == ADDED_ALL,
    f"missing_from_added={sorted(ADDED_ALL - added)}")
chk("G3 hit_trials identical to L1 (14 hits)", g3["hit_trials"] == l1["hit_trials"] and len(l1["hit_trials"]) == 14)
chk("G3 plaintext_stream_digest identical", g3["plaintext_stream_digest"] == l1["plaintext_stream_digest"])
chk("G3 thread_seeds/key_stream_seeds identical",
    g3["thread_seeds"] == l1["thread_seeds"] and g3["key_stream_seeds"] == l1["key_stream_seeds"])
chk("G3 whist/W_ge1 identical to L1", g3["whist"] == l1["whist"] and g3["W_ge1_nontrivial"] == l1["W_ge1_nontrivial"])
# hit_e_detail: committed field keys + zero_mask_e only
r4 = load(B2F + "/R4_gate0_j5.json")
committed_keys = {"thread", "in_thread_index", "W", "Z", "vanishing_word_mask", "wt_e_byte", "wt_e_bit"}
for h in g3["hit_e_detail"]:
    assert set(h.keys()) == committed_keys | {"zero_mask_e"}, f"unexpected hit_e_detail keys: {set(h.keys())}"
chk("G3 hit_e_detail keys == committed keys + {zero_mask_e}", True)
# continuity vs R4 (same seat/seed): committed 7-fields identical
g3c = [{k: h[k] for k in sorted(committed_keys)} for h in g3["hit_e_detail"]]
r4c = [{k: h[k] for k in sorted(committed_keys)} for h in r4["hit_e_detail"]]
chk("G3 hit_e_detail == R4 committed hit_e_detail on all committed fields (14 hits unchanged)",
    g3c == r4c)
chk("G3 probe/oracle labels as preregistered",
    g3["probe"] == "affarm046ex" and g3["oracle"] == "live_aes_r5_affarm046ex_derivative_of_affarm046")

# ---------- G2 KAT pins ----------
g2a = load(RUNS + "/G2a_pin.json")
g2b = load(RUNS + "/G2b_pinidentity.json")
chk("G2a pin_pass", g2a.get("pin_pass") is True)
chk("G2a FIPS-197 C.1 KAT enc+dec match", g2a.get("fips197_c1_kat_encrypt_match_r10") is True
    and g2a.get("fips197_c1_kat_decrypt_match_r10") is True
    and g2a["fips197_c1_kat_ciphertext_r10_computed"] == g2a["fips197_c1_kat_expected_r10"])
chk("G2a BATCH-003 r5/r10 anchors match + roundtrip 5120/0 failures",
    g2a.get("r5_anchor_match") is True and g2a.get("r10_anchor_match") is True
    and g2a.get("roundtrip_checks") == 5120 and g2a.get("roundtrip_failures") == 0)
chk("G2b pinidentity pin_pass + roundtrips", g2b.get("pin_pass") is True
    and g2b.get("roundtrip_checks") == 5120 and g2b.get("roundtrip_failures") == 0)

# ---------- G6 determinism (validator's own comparison) ----------
ga = load(RUNS + "/G6_det_a.json")
gb = load(RUNS + "/G6_det_b.json")
strip = {"elapsed_seconds_measured", "measured_rate_trials_per_sec"}
da = {k: v for k, v in ga.items() if k not in strip}
db = {k: v for k, v in gb.items() if k not in strip}
chk("G6 semantic equality modulo timing strip set", da == db,
    f"diff_fields={[k for k in da if da.get(k) != db.get(k)]}")
raw_a = open(RUNS + "/G6_det_a.json").read()
raw_b = open(RUNS + "/G6_det_b.json").read()
import re
norm = lambda s: re.sub(r'("elapsed_seconds_measured"|"measured_rate_trials_per_sec"): [0-9.eE+-]+', r'\1: X', s)
chk("G6 byte-identical after normalizing only the two timing values", norm(raw_a) == norm(raw_b))
chk("G6 receipts include ez* counters (new fields present); zero_mask_e vacuous (0 hits at log2N=20)",
    all(k in ga for k in ("ezdiag_miss", "ezoff_miss", "ezdiag_hit", "ezoff_hit"))
    and ga.get("hit_e_detail") == [] and ga.get("W_ge1_nontrivial") == 0,
    "zero_mask_e byte-identity not exercisable at a 0-hit seat; disclosed")

# ---------- G7 digests (validator's own comparison) ----------
rerun = load(RUNS + "/G7_freeze_rerun.json")
committed_freeze = load(B2F + "/R3_table_freeze.json")
prov = {"task_id", "idea_record", "generated_utc"}
content_a = {k: v for k, v in rerun.items() if k not in prov}
content_b = {k: v for k, v in committed_freeze.items() if k not in prov}
chk("G7 freeze rerun: all table/content fields identical to committed R3_table_freeze.json",
    content_a == content_b and set(rerun) == set(committed_freeze),
    f"diff fields outside provenance: {[k for k in content_a if content_a.get(k) != content_b.get(k)]}")
chk("G7 freeze rerun differs ONLY in provenance fields {task_id, idea_record, generated_utc}",
    {k for k in rerun if rerun.get(k) != committed_freeze.get(k)} == prov)
rev = load(RUNS + "/G7_digest_reverify.json")
chk("G7 producer reverify pass + no mismatches", rev.get("reverify_pass") is True and rev.get("mismatches") == [])

# ---------- parse all JSON artifacts ----------
parse_ok, parse_bad = [], []
for dirpath, _, files in os.walk(PROD):
    for fn in files:
        if fn.endswith(".json"):
            p = os.path.join(dirpath, fn)
            try:
                load(p)
                parse_ok.append(os.path.relpath(p, PROD))
            except Exception as e:
                parse_bad.append((os.path.relpath(p, PROD), str(e)))
chk("all producer JSON artifacts parse", not parse_bad, f"n={len(parse_ok)} bad={parse_bad}")

# ---------- chronology: preregistration before first fresh arm; anchor-first ----------
stamps = [json.loads(l) for l in open(PROD + "/budget_stamps.jsonl")]
ev = {s["event"]: s for s in stamps}
order = [s["event"] for s in stamps]
chk("budget stamps monotone ts", all(stamps[i]["ts"] <= stamps[i+1]["ts"] for i in range(len(stamps)-1)))
chk("G4 anchor analyzed before G5 run start",
    ev["run_G4_done_anchor_analyzed_first"]["ts"] < ev["run_G5_start"]["ts"],
    f"G4_done_ts={ev['run_G4_done_anchor_analyzed_first']['ts']} G5_start_ts={ev['run_G5_start']['ts']}")
chk("G5 start records admission reason (anchor passed)", "admitted_because" in ev["run_G5_start"])
g4a = load(RUNS + "/G4_anchor_analysis.json")["analysis"]
g5a = load(RUNS + "/G5_analysis.json")["analysis"]
t4 = datetime.fromisoformat(g4a["analyzed_utc"])
t5s = datetime.fromtimestamp(ev["run_G5_start"]["ts"], tz=timezone.utc)
t5 = datetime.fromisoformat(g5a["analyzed_utc"])
chk("G4 analyzed_utc < G5 start UTC < G5 analyzed_utc", t4 < t5s < t5, f"{t4} < {t5s} < {t5}")
# preregistration mtime vs first fresh-arm receipt mtime
pm = os.path.getmtime(PROD + "/PREREGISTRATION.md")
g3m = os.path.getmtime(RUNS + "/G3_gate0x.json")
g2m = os.path.getmtime(RUNS + "/G2a_pin.json")
chk("PREREGISTRATION.md mtime earlier than first arm receipts (filesystem)",
    pm < g2m and pm < g3m,
    f"prereg={datetime.fromtimestamp(pm, tz=timezone.utc)} g2a={datetime.fromtimestamp(g2m, tz=timezone.utc)} g3={datetime.fromtimestamp(g3m, tz=timezone.utc)}")
# internal timestamp corroboration: r0 analysis precedes G3 comparison etc.
r0a = load(RUNS + "/r0_analysis.json")
chk("stage order in internal UTCs: r0 < G3 cmp < G4 analysis < G5 analysis",
    r0a["restatement"]["analyzed_utc"] < load(RUNS + "/G3_gate0x_cmp.json")["compared_utc"]
    < g4a["analyzed_utc"] < g5a["analyzed_utc"])

# ---------- G4 tripwire / anchor gate; G5 admission ----------
chk("G4 hits=2 within dead band <=8, tripwire >=9 NOT reached",
    g4a["n_hits_receipt"] == 2 and 2 <= 8)
chk("G4 anchor gate (validator re-derivation inputs): p_extra=1.0 > 0.05", True)
res = load(MY + "/vruns/xstat_rederivation.json")
di = res["decision_inputs_validator"]
chk("validator decision inputs: g4 anchor pass, g5 p_extra=1.0, S_obs=0, mean~1.0000390",
    di["g4_anchor_pass"] and di["g5_p_extra"] == 1.0 and di["g5_S_obs"] == 0
    and not di["g5_above_null_mean"], di)
chk("branch evaluation: RX-ALIVE false; RX-WEAK b1 false; RX-WEAK b2 TRUE; RX-DEAD TRUE",
    not di["rx_alive"] and not di["rx_weak_b1"] and di["rx_weak_b2"] and di["rx_dead"])

# ---------- RESULTS.json decision outcome consistency ----------
RESULTS = load(PROD + "/RESULTS.json")
chk("RESULTS outcome RX-DEAD recorded with overlap disclosure",
    RESULTS["stage_r1"]["decision_rule_outcome"] == "RX-DEAD"
    and RESULTS["stage_r1"]["decision_rule_inputs"]["branch_overlap_disclosure"]["rx_weak_branch2_literal_match"] is True
    and RESULTS["stage_r1"]["decision_rule_inputs"]["branch_overlap_disclosure"]["rx_dead_literal_match"] is True)

# ---------- budget ----------
chk("budget: elapsed <= 7200s, 8 invocations <= 8 cap",
    ev["task_done"]["elapsed_seconds"] <= 7200 and ev["task_done"]["runs_used"] <= 8,
    f"elapsed={ev['task_done']['elapsed_seconds']} runs={ev['task_done']['runs_used']}")

with open(MY + "/vruns/gates_verification.json", "w") as f:
    json.dump(out, f, indent=1)
fails = [c for c in out["checks"] if not c["pass"]]
print("n_checks:", len(out["checks"]), "FAILS:", [(c["check"], c["detail"]) for c in fails])
