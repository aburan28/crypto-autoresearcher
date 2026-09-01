#!/usr/bin/env python3
"""Validator binding-control checks for BATCH-7939d0 (TASK-20260901-0dcc8d).
Fresh code: filesystem stats, sha256 hashes, and field-by-field JSON diffs
computed directly, never from producer-reported values.
"""
import difflib
import hashlib
import json
import os

ROOT = "/Volumes/SSD990/crypto-autoresearcher/.worktrees/aes003-batch015-20260831"
B793 = "coordination/goals/GOAL-AES-003/batches/BATCH-7939d0"
TA = os.path.join(B793, "tasks/TASK-20260901-92672b")
TB = os.path.join(B793, "tasks/TASK-20260901-47b21f")
B014 = "coordination/goals/GOAL-AES-003/batches/BATCH-014/tasks/TASK-20260805-b95720"
B015 = "coordination/goals/GOAL-AES-003/batches/BATCH-015/tasks/TASK-20260805-d408ac"

def p(rel):
    return os.path.join(ROOT, rel)

def sha256(rel):
    h = hashlib.sha256()
    with open(p(rel), "rb") as f:
        h.update(f.read())
    return h.hexdigest()

def load(rel):
    with open(p(rel)) as f:
        return json.load(f)

out = {}

# ---------- CONTROL 1: preregistration mtime ordering ----------
for tid, tdir in (("TASK-20260901-92672b", TA), ("TASK-20260901-47b21f", TB)):
    pre = os.stat(p(os.path.join(tdir, "PREREGISTRATION.md"))).st_mtime
    runs_dir = p(os.path.join(tdir, "runs"))
    files = sorted(os.listdir(runs_dir))
    newer = []
    older_or_equal = []
    for fn in files:
        mt = os.stat(os.path.join(runs_dir, fn)).st_mtime
        (newer if mt > pre else older_or_equal).append((fn, mt))
    out.setdefault("control1_preregistration_mtime", {})[tid] = {
        "preregistration_mtime_epoch": pre,
        "n_runs_files": len(files),
        "n_files_strictly_newer": len(newer),
        "files_not_newer": older_or_equal,
        "pass": len(older_or_equal) == 0,
        "first_run_file": min(newer, key=lambda t: t[1])[0] if newer else None,
        "first_run_mtime_epoch": min(newer, key=lambda t: t[1])[1] if newer else None,
        "gap_seconds": (min(newer, key=lambda t: t[1])[1] - pre) if newer else None,
    }

# ---------- CONTROL 2: r=16 byte parity (producer A) ----------
det_v = sha256(os.path.join(TA, "runs/DET-R16.json"))
det_ver = sha256(os.path.join(TA, "runs/DET-R16-VERBATIM.json"))
sm_v = sha256(os.path.join(TA, "runs/SMOKE22-R16.json"))
sm_ver = sha256(os.path.join(TA, "runs/SMOKE22-R16-VERBATIM.json"))
fr16 = load(os.path.join(TA, "runs/F-R16-P30.json"))
m1 = load(os.path.join(B014, "runs/M1-FEISTEL-P30.json"))
field_diffs = {}
for k in sorted(set(fr16) | set(m1)):
    if k == "arm":
        continue
    if fr16.get(k, "<missing>") != m1.get(k, "<missing>"):
        field_diffs[k] = {"F-R16-P30": fr16.get(k, "<missing>"), "M1-FEISTEL-P30": m1.get(k, "<missing>")}
out["control2_r16_byte_parity"] = {
    "detcheck_sha256_variant": det_v,
    "detcheck_sha256_verbatim": det_ver,
    "detcheck_identical": det_v == det_ver,
    "smoke22_sha256_variant": sm_v,
    "smoke22_sha256_verbatim": sm_ver,
    "smoke22_identical": sm_v == sm_ver,
    "claimed_detcheck_sha256": "a9ae7aa5cf74dffaa588c94afe1c1dd79fcb72bfa05b75137ef8c3f2027c0e38",
    "claimed_smoke22_sha256": "498b78d03e55b2fc9fe3b597d7881b93e3ee482914f027381e85e2cccc5514dd",
    "detcheck_matches_claimed": det_v == "a9ae7aa5cf74dffaa588c94afe1c1dd79fcb72bfa05b75137ef8c3f2027c0e38",
    "smoke22_matches_claimed": sm_v == "498b78d03e55b2fc9fe3b597d7881b93e3ee482914f027381e85e2cccc5514dd",
    "F-R16-P30_vs_M1-FEISTEL-P30_field_diffs_beyond_arm": field_diffs,
    "field_parity_pass": field_diffs == {},
    "arm_labels": {"F-R16-P30": fr16["arm"], "M1-FEISTEL-P30": m1["arm"]},
    "pass": det_v == det_ver and sm_v == sm_ver and field_diffs == {},
}

# ---------- CONTROL 3: verbatim source sha256 (producer B) ----------
srcB_feistel = sha256(os.path.join(TB, "src/rc8probe_feistel.c"))
srcB_fresh = sha256(os.path.join(TB, "src/rc8probe_freshfeistel.c"))
out["control3_verbatim_source"] = {
    "feistel_c_task_copy_sha256": srcB_feistel,
    "feistel_c_archived_sha256": sha256(os.path.join(B014, "src/rc8probe_feistel.c")),
    "feistel_c_parity": srcB_feistel == sha256(os.path.join(B014, "src/rc8probe_feistel.c")),
    "claimed_feistel_sha256": "9b36c0e714118e11e160b9aec81c9a6c1aceecc6fb2b6c452b3dd3bbf98d8566",
    "feistel_matches_claimed": srcB_feistel == "9b36c0e714118e11e160b9aec81c9a6c1aceecc6fb2b6c452b3dd3bbf98d8566",
    "freshfeistel_c_task_copy_sha256": srcB_fresh,
    "freshfeistel_c_archived_sha256": sha256(os.path.join(B015, "src/rc8probe_freshfeistel.c")),
    "freshfeistel_c_parity": srcB_fresh == sha256(os.path.join(B015, "src/rc8probe_freshfeistel.c")),
    "claimed_freshfeistel_sha256": "d163b64e6b0d6bce1f23027bb7209c0a8c5ef1984874465119f61adf3e0d450d",
    "freshfeistel_matches_claimed": srcB_fresh == "d163b64e6b0d6bce1f23027bb7209c0a8c5ef1984874465119f61adf3e0d450d",
}

# supplementary: producer A variant source vs archived source (structural edit claim)
a_var = open(p(os.path.join(TA, "src/rc8probe_feistel_rk.c"))).read().splitlines(keepends=True)
a_base = open(p(os.path.join(B014, "src/rc8probe_feistel.c"))).read().splitlines(keepends=True)
diff = list(difflib.unified_diff(a_base, a_var, lineterm=""))
added = [l for l in diff if l.startswith("+") and not l.startswith("+++")]
removed = [l for l in diff if l.startswith("-") and not l.startswith("---")]
out["control3b_variant_source_diff"] = {
    "variant_source_sha256": sha256(os.path.join(TA, "src/rc8probe_feistel_rk.c")),
    "n_added_lines": len(added), "added_lines": [l.rstrip("\n") for l in added],
    "n_removed_lines": len(removed), "removed_lines": [l.rstrip("\n") for l in removed],
}
out["control3_verbatim_source"]["pass"] = (out["control3_verbatim_source"]["feistel_c_parity"]
                                           and out["control3_verbatim_source"]["freshfeistel_c_parity"])

# ---------- CONTROL 4: frozen comparator usage ----------
frozen = load(os.path.join(B015, "RESULTS.json"))["frozen_comparator"]
resA = load(os.path.join(TA, "RESULTS.json"))
daA = load(os.path.join(TA, "runs/decision_analysis.json"))
resB = load(os.path.join(TB, "RESULTS.json"))
daB = load(os.path.join(TB, "runs/decision_analysis.json"))
aesA = load(os.path.join(TA, "runs/AES-P30.json"))
fr = {k: aesA[k] for k in ("W_ge1_nontrivial", "nontrivial_trials", "seed", "arm_id", "amask", "smask", "threads", "key_stream_seeds", "thread_seeds", "plaintext_stream_digest")}
out["control4_frozen_comparator"] = {
    "frozen_block_source_B015": {k: frozen[k] for k in ("W_ge1_nontrivial", "nontrivial_trials", "null_expectation_analytic", "key_hex", "seed", "armid", "rounds", "amask", "smask", "threads", "plaintext_stream_digest")},
    "producerA_frozen_block": resA["frozen_comparator"],
    "producerA_frozen_values_match_B015": all(
        resA["frozen_comparator"].get(k) == frozen.get(k)
        for k in ("W_ge1_nontrivial", "nontrivial_trials", "null_expectation_analytic", "key_hex", "seed", "armid", "rounds", "amask", "smask", "threads", "plaintext_stream_digest")
    ),
    "producerA_live_AES_arm_reproduces_frozen": {
        "W_ge1_nontrivial": aesA["W_ge1_nontrivial"] == frozen["W_ge1_nontrivial"],
        "nontrivial_trials": aesA["nontrivial_trials"] == frozen["nontrivial_trials"],
        "seed": aesA["seed"] == frozen["seed"],
        "thread_seeds": aesA["thread_seeds"] == frozen["thread_seeds"],
        "plaintext_stream_digest": aesA["plaintext_stream_digest"] == frozen["plaintext_stream_digest"],
        "W_ge1_by_word_vs_frozen_claim": aesA["W_ge1_by_word"] == [4, 4, 2, 4],
    },
    "producerB_cross_anchor_values": resB["frozen_comparator_context"]["values_read_verbatim_via_RC_D_RESULTS"],
    "producerB_cross_anchor_matches_B015": all(
        resB["frozen_comparator_context"]["values_read_verbatim_via_RC_D_RESULTS"].get(k) == frozen.get(k)
        for k in ("W_ge1_nontrivial", "nontrivial_trials", "null_expectation_analytic", "key_hex", "seed", "armid", "rounds", "amask", "smask")
    ),
    "producerB_da_cross_anchor_x": daB["comparisons"]["frozen_r5_531001_vs_F16_S2_cross_anchor"]["x_aes"],
}

# producer A: live AES arm vs BATCH-015 L1-AES-R5-P30 field-by-field (3 allowed diffs)
l1 = load(os.path.join(B015, "runs/L1-AES-R5-P30.json"))
allowed = {"arm", "elapsed_seconds_measured", "measured_rate_trials_per_sec"}
diffs_l1 = {}
for k in sorted(set(aesA) | set(l1)):
    if k in allowed:
        continue
    if aesA.get(k, "<missing>") != l1.get(k, "<missing>"):
        diffs_l1[k] = {"AES-P30": aesA.get(k, "<missing>"), "L1-AES-R5-P30": l1.get(k, "<missing>")}
out["control4b_AES_arm_vs_L1"] = {
    "allowed_field_differences": sorted(allowed),
    "field_differences_beyond_allowed": diffs_l1,
    "pass": diffs_l1 == {},
    "allowed_diff_values": {k: {"AES-P30": aesA.get(k), "L1-AES-R5-P30": l1.get(k)} for k in sorted(allowed)},
}

# ---------- CONTROL 5: determinism JSONs ----------
dets = {}
for tid, tdir, names in ((TA.split("/")[-1], TA, ["DET-R4", "DET-R8", "DET-R16", "DET-R16-VERBATIM", "DET-R32"]),
                          (TB.split("/")[-1], TB, ["detcheck-S2"])):
    dets[tid] = {}
    for nm in names:
        d = load(os.path.join(tdir, f"runs/{nm}.json"))
        dets[tid][nm] = {
            "deterministic": d.get("deterministic"),
            "same_key_same_input_same_output": d.get("same_key_same_input_same_output"),
            "decrypt_inverts_encrypt": d.get("decrypt_inverts_encrypt"),
            "round_key_schedule_reproducible": d.get("round_key_schedule_reproducible"),
        }
out["control5_determinism"] = dets

# ---------- supplementary: err/timing exit codes, budget stamps ----------
supp = {"exit_codes": {}, "budget": {}}
for tid, tdir in (("TASK-20260901-92672b", TA), ("TASK-20260901-47b21f", TB)):
    runs_dir = p(os.path.join(tdir, "runs"))
    for fn in sorted(os.listdir(runs_dir)):
        if fn.endswith(".timing.txt"):
            txt = open(os.path.join(runs_dir, fn)).read()
            ec = None
            for line in txt.splitlines():
                if "exit" in line.lower():
                    ec = line.strip()
            supp["exit_codes"][f"{tid}/{fn}"] = ec
    stamps = [json.loads(l) for l in open(p(os.path.join(tdir, "budget_stamps.jsonl"))) if l.strip()]
    supp["budget"][tid] = {"stamps": stamps}

out["supplementary"] = supp
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "controls.json"), "w") as f:
    json.dump(out, f, indent=2)
print("control1:", {k: v["pass"] for k, v in out["control1_preregistration_mtime"].items()})
print("control2:", out["control2_r16_byte_parity"]["pass"], "| detcheck identical:", out["control2_r16_byte_parity"]["detcheck_identical"], "| smoke identical:", out["control2_r16_byte_parity"]["smoke22_identical"], "| field parity:", out["control2_r16_byte_parity"]["field_parity_pass"], "| claimed-match:", out["control2_r16_byte_parity"]["detcheck_matches_claimed"], out["control2_r16_byte_parity"]["smoke22_matches_claimed"])
print("control3:", out["control3_verbatim_source"]["pass"], "| feistel:", out["control3_verbatim_source"]["feistel_c_parity"], out["control3_verbatim_source"]["feistel_matches_claimed"], "| fresh:", out["control3_verbatim_source"]["freshfeistel_c_parity"], out["control3_verbatim_source"]["freshfeistel_matches_claimed"])
print("control3b diff:", out["control3b_variant_source_diff"]["n_added_lines"], "added,", out["control3b_variant_source_diff"]["n_removed_lines"], "removed")
print("control4: A frozen match:", out["control4_frozen_comparator"]["producerA_frozen_values_match_B015"], "| B cross-anchor match:", out["control4_frozen_comparator"]["producerB_cross_anchor_matches_B015"], "| live AES reproduces:", out["control4_frozen_comparator"]["producerA_live_AES_arm_reproduces_frozen"])
print("control4b AES vs L1:", out["control4b_AES_arm_vs_L1"]["pass"], "diffs:", out["control4b_AES_arm_vs_L1"]["field_differences_beyond_allowed"])
print("control5:", json.dumps(out["control5_determinism"]))
