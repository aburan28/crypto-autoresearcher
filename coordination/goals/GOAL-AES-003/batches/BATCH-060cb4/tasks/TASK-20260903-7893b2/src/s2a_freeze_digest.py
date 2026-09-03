#!/usr/bin/env python3
# s2a_freeze_digest.py -- TASK-20260903-7893b2 (BATCH-060cb4, GOAL-AES-003)
# Fresh for this task; re-derives the committed freeze_digest.py convention
# (lineage BATCH-e5d753 TASK-20260902-987716 / BATCH-7b798d / BATCH-ace664),
# EXTENDED to the eight-point surface {0,1,2,3,4,8,12,16} of the declared k=3
# extension. Consumes the C freeze-mode output of the EXTENDED build,
# computes sha256 digests of every 256-byte per-position table, INDEPENDENTLY
# re-checks bijection and nestedness from the hex bytes, applies the folded
# smoke self-check assertions (cap-256 convention), and writes the write-once
# extended freeze commitment R4_table_freeze_ext.json.
#
# SURFACE-DIFF BATTERY (IDEA-20260903-8f26ac family_extension_design,
# PREREGISTRATION.md section 6.2; pre-registered):
#   (a) for every k in {0,1,2,4,8,12,16}, per-position table sha256 digests,
#       concat digest, position lists, per_position_is_aes flags, bijection
#       and nestedness checks MUST equal the committed R3_table_freeze.json
#       values exactly - any mismatch is CC3-GATE-FAIL; additionally
#       aes_table_sha256, identity_table_sha256, position_order compared
#       (lineage S0-4 convention), and cap-INDEPENDENT selfcheck counters
#       compared with the cap-DEPENDENT fields (hit_detail_records,
#       hit_log_overflow, hit_log_cap) disclosed, never compared as
#       mismatches (committed R3 file is cap-64; this build is cap-256);
#   (b) the k=3 entry (positions [0,4,8], per-position digests, bijection
#       true, nestedness true) is committed in the same file with mtime
#       BEFORE any k=3 arm (S2b's job; none run in this task);
#   (c) cross_k_nesting true over all eight points;
#   (d) selfcheck_identity_k0 + selfcheck_aes_k16 assertions pass (cap-256).
#
# usage: python3 src/s2a_freeze_digest.py <c_freeze_output.json> <out_R4.json>
#        --battery <committed_R3.json> <out_battery.json>
# Exit codes: 0 pass; 6 = freeze check failure; 7 = battery mismatch.
#
# INFERENCE BLOCK: policy executor-implementation; requested_policy
# executor-implementation; resolved_model_id
# fireworks-ai/accounts/fireworks/models/qwen3p8-max (session-reported; no
# adapter probe run in this session); fallback_used true; model_verified
# false; degraded_requirements []; amendment DEC-20260831-0d1eeb.
import json, sys, hashlib, datetime

INFERENCE = {
    "policy": "executor-implementation",
    "requested_policy": "executor-implementation",
    "resolved_model_id": "fireworks-ai/accounts/fireworks/models/qwen3p8-max",
    "resolved_model_id_note": "session-reported; no adapter probe run in this session",
    "model_verified": False,
    "fallback_used": True,
    "fallback_reason": "session-backend transport under inference amendment DEC-20260831-0d1eeb",
    "degraded_requirements": [],
    "amendment": "DEC-20260831-0d1eeb",
}
EXPECTED_ORDER = [0, 4, 8, 12, 1, 5, 9, 13, 2, 6, 10, 14, 3, 7, 11, 15]
EXPECTED_KS = [0, 1, 2, 3, 4, 8, 12, 16]   # extended surface (declared diff)


def sha256_hex(hexstr):
    return hashlib.sha256(bytes.fromhex(hexstr)).hexdigest()


def digest_freeze(raw):
    fj = json.loads(raw)
    assert fj["mode"] == "freeze"
    assert fj["position_order"] == EXPECTED_ORDER, "position order drifted from frozen spec"
    aes_hex = fj["aes_table_hex"]
    aes_bytes = bytes.fromhex(aes_hex)
    assert len(aes_bytes) == 256
    identity_hex = "".join(f"{i:02x}" for i in range(256))
    out_points = []
    all_ok = True
    seen_positions = None
    for pt in fj["points"]:
        k = pt["k"]
        assert k in EXPECTED_KS, f"unexpected freeze point k={k}"
        P_k = EXPECTED_ORDER[:k]
        is_aes_flags = [1 if j in P_k else 0 for j in range(16)]
        assert pt["per_position_is_aes"] == is_aes_flags, f"k={k}: position set drifted"
        digests = []
        bijective = True
        nested = True
        concat = b""
        for j in range(16):
            thex = pt["per_position_table_hex"][j]
            tb = bytes.fromhex(thex)
            assert len(tb) == 256, f"k={k} pos {j}: table not 256 bytes"
            digests.append(sha256_hex(thex))
            concat += tb
            if sorted(tb) != list(range(256)):
                bijective = False
            expect = aes_bytes if is_aes_flags[j] else bytes(range(256))
            if tb != expect:
                nested = False
        if bijective != pt["bijective_all_positions"]:
            all_ok = False
        if nested != pt["nestedness_check"]:
            all_ok = False
        if not (bijective and nested):
            all_ok = False
        if seen_positions is not None and not set(P_k) >= set(seen_positions):
            all_ok = False
        seen_positions = P_k
        out_points.append({
            "k": k,
            "positions": P_k,
            "per_position_is_aes": is_aes_flags,
            "per_position_table_sha256": digests,
            "concat_sha256": hashlib.sha256(concat).hexdigest(),
            "bijective_all_positions": bijective,
            "nestedness_check": nested,
            "per_position_table_hex": pt["per_position_table_hex"],
        })
    ks_emitted = [p["k"] for p in out_points]
    if ks_emitted != EXPECTED_KS:
        all_ok = False
    out = {
        "schema": "crypto.autoresearch.table_freeze.v1",
        "task_id": "TASK-20260903-7893b2",
        "idea_record": "IDEA-20260903-8f26ac",
        "pin_decision": "DEC-20260901-fb6f11",
        "extension_note": ("EXTENDED freeze commitment R4: frozen-build surface plus the declared k=3 point "
                           "(declared source diff of IDEA-20260903-8f26ac family_extension_design); "
                           "committed write-once PRE-ARM (no k=3 arm runs in Stage S2a; k=3 arms are Stage S2b)"),
        "mode": "freeze",
        "family": fj["family"],
        "position_order": EXPECTED_ORDER,
        "construction_pin": fj["construction_pin"],
        "aes_table_sha256": sha256_hex(aes_hex),
        "identity_table_sha256": sha256_hex(identity_hex),
        "points": out_points,
        "cross_k_nesting": fj["cross_k_nesting"],
        "selfcheck_identity_k0": fj["selfcheck_identity_k0"],
        "selfcheck_aes_k16": fj["selfcheck_aes_k16"],
        "freeze_seed": fj["freeze_seed"],
        "generated_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    sc0 = fj["selfcheck_identity_k0"]
    nt0 = sc0["nontrivial_trials"]
    nthr0 = sc0["threads"]
    per_thread_hits0 = nt0 // nthr0 if sc0["trivial_swaps_excluded"] == 0 else None
    id_ok = (
        sc0["trials"] == 1024
        and sc0["trivial_swaps_excluded"] + nt0 == 1024
        and sc0["whist"] == [0, 0, 0, nt0, 0]
        and sc0["W_ge1_nontrivial"] == nt0
        and sc0["W_ge1_by_word"] == [0, nt0, nt0, nt0]
        and sc0["ewhist_all"] == [nt0] + [0] * 16
        and sc0["ewhist_hit"] == [nt0] + [0] * 16
        and sc0["ewhist_miss"] == [0] * 17
        and sc0["ewbithist_all_sum_check"] == nt0
        and sc0["ewbithist_hit_sum_check"] == nt0
        and sc0["ewbithist_miss_sum_check"] == 0
        and per_thread_hits0 is not None
        and sc0["hit_detail_records"] == nthr0 * min(per_thread_hits0, 256)
        and sc0["hit_log_overflow"] == nt0 - nthr0 * min(per_thread_hits0, 256)
    )
    sc16 = fj["selfcheck_aes_k16"]
    nt16 = sc16["nontrivial_trials"]
    wh16 = sc16["whist"]
    wge1_16 = sc16["W_ge1_nontrivial"]
    nthr16 = sc16["threads"]
    aes_ok = (
        sc16["trials"] == 1024
        and sc16["trivial_swaps_excluded"] + nt16 == 1024
        and sum(wh16) == nt16
        and wge1_16 == sum(wh16[1:5])
        and sum(sc16["ewhist_all"]) == nt16
        and sum(sc16["ewhist_hit"]) == wge1_16
        and sum(sc16["ewhist_miss"]) == nt16 - wge1_16
        and sc16["ewbithist_all_sum_check"] == nt16
        and sc16["ewbithist_hit_sum_check"] == wge1_16
        and sc16["ewbithist_miss_sum_check"] == nt16 - wge1_16
        and sc16["hit_detail_records"] + sc16["hit_log_overflow"] == wge1_16
        and sc16["hit_detail_records"] <= nthr16 * 256
    )
    out["selfcheck_identity_k0"]["assert_pass"] = id_ok
    out["selfcheck_aes_k16"]["assert_pass"] = aes_ok
    out["freeze_pass"] = bool(all_ok and fj["cross_k_nesting"] and id_ok and aes_ok)
    out["parse_attestation"] = ("machine-generated JSON; parsed whole with python3 "
                                "json.load (C input and this output) before task completion")
    out["inference"] = INFERENCE
    return out


def battery(out, committed):
    mismatches = []
    per_point = {}
    if committed.get("aes_table_sha256") != out["aes_table_sha256"]:
        mismatches.append("aes_table_sha256")
    if committed.get("identity_table_sha256") != out["identity_table_sha256"]:
        mismatches.append("identity_table_sha256")
    if committed.get("position_order") != out["position_order"]:
        mismatches.append("position_order")
    cpts = {p["k"]: p for p in committed.get("points", [])}
    for p in out["points"]:
        cp = cpts.get(p["k"])
        entry = {"k": p["k"]}
        if cp is None:
            entry["status"] = "NEW POINT (committed pre-arm by this file)"
            entry["positions_expected_P3"] = p["k"] == 3 and p["positions"] == EXPECTED_ORDER[:3]
            entry["bijective"] = p["bijective_all_positions"]
            entry["nested"] = p["nestedness_check"]
            if p["k"] == 3:
                if not (p["positions"] == EXPECTED_ORDER[:3]
                        and p["bijective_all_positions"] and p["nestedness_check"]):
                    mismatches.append("k=3 new entry fails pre-arm commitment conjuncts")
            else:
                mismatches.append(f"point k={p['k']} missing from committed file")
            per_point[p["k"]] = entry
            continue
        diffs = []
        if cp.get("per_position_table_sha256") != p["per_position_table_sha256"]:
            diffs.append("per_position_table_sha256")
        if cp.get("concat_sha256") != p["concat_sha256"]:
            diffs.append("concat_sha256")
        if cp.get("positions") != p["positions"]:
            diffs.append("positions")
        if cp.get("per_position_is_aes") != p["per_position_is_aes"]:
            diffs.append("per_position_is_aes")
        if cp.get("bijective_all_positions") != p["bijective_all_positions"]:
            diffs.append("bijective_all_positions")
        if cp.get("nestedness_check") != p["nestedness_check"]:
            diffs.append("nestedness_check")
        if diffs:
            mismatches.append(f"k={p['k']} existing-point fields differ: {diffs}")
        entry["status"] = "byte-equal to R3" if not diffs else "MISMATCH"
        entry["fields_compared"] = ["per_position_table_sha256", "concat_sha256", "positions",
                                    "per_position_is_aes", "bijective_all_positions", "nestedness_check"]
        entry["diffs"] = diffs
        per_point[p["k"]] = entry
    for k in sorted(cpts):
        if k not in {p["k"] for p in out["points"]}:
            mismatches.append(f"committed point k={k} missing from extended freeze")
    cross_ok = out["cross_k_nesting"] is True and committed.get("cross_k_nesting") is True
    if not cross_ok:
        mismatches.append("cross_k_nesting not true on both files")
    cap_independent_fields = ("trials", "trivial_swaps_excluded",
                              "nontrivial_trials", "W_ge1_nontrivial",
                              "whist", "W_ge1_by_word", "ewhist_all",
                              "ewhist_miss", "ewhist_hit", "zhist")
    selfcheck_cmp = {}
    for label in ("selfcheck_identity_k0", "selfcheck_aes_k16"):
        csc = committed.get(label, {})
        nsc = out.get(label, {})
        diffs = [f for f in cap_independent_fields if csc.get(f) != nsc.get(f)]
        if diffs:
            mismatches.append(f"{label} cap-independent counters differ: {diffs}")
        selfcheck_cmp[label] = {
            "assert_pass_extended_build": nsc.get("assert_pass"),
            "cap_independent_fields_compared": list(cap_independent_fields),
            "identical_to_R3": not diffs,
            "cap_dependent_not_compared_disclosed": {
                "hit_detail_records": {"committed_cap64": csc.get("hit_detail_records"),
                                       "extended_cap256": nsc.get("hit_detail_records")},
                "hit_log_overflow": {"committed_cap64": csc.get("hit_log_overflow"),
                                     "extended_cap256": nsc.get("hit_log_overflow")},
                "hit_log_cap": {"committed_cap64": csc.get("hit_log_cap"),
                                "extended_cap256": nsc.get("hit_log_cap")},
            },
        }
    return mismatches, per_point, selfcheck_cmp, cross_ok


def main():
    c_out_path, out_path = sys.argv[1], sys.argv[2]
    raw = open(c_out_path).read()
    out = digest_freeze(raw)
    json.dump(out, open(out_path, "w"), indent=1)
    if "--battery" in sys.argv:
        i = sys.argv.index("--battery")
        committed_path, battery_out_path = sys.argv[i + 1], sys.argv[i + 2]
        committed = json.load(open(committed_path))
        mismatches, per_point, selfcheck_cmp, cross_ok = battery(out, committed)
        k3 = next((p for p in out["points"] if p["k"] == 3), None)
        rv = {
            "schema": "crypto.autoresearch.surface_diff_battery.v1",
            "task_id": "TASK-20260903-7893b2",
            "batch_id": "BATCH-060cb4",
            "goal_id": "GOAL-AES-003",
            "idea_record": "IDEA-20260903-8f26ac",
            "run_id": "S2a-4",
            "committed_freeze_file_R3": committed_path,
            "extended_freeze_file_R4": out_path,
            "battery_conjuncts": {
                "a_existing_seven_points_byte_equal_to_R3": all(
                    v.get("status") == "byte-equal to R3" for k, v in per_point.items() if k != 3),
                "b_k3_entry_committed_pre_arm": k3 is not None
                and k3["positions"] == EXPECTED_ORDER[:3]
                and k3["bijective_all_positions"] and k3["nestedness_check"],
                "c_cross_k_nesting_true_over_eight_points": cross_ok,
                "d_selfcheck_assertions_pass": out["selfcheck_identity_k0"]["assert_pass"]
                and out["selfcheck_aes_k16"]["assert_pass"],
            },
            "per_point_comparison": per_point,
            "k3_committed_entry": None if k3 is None else {
                "k": 3,
                "positions": k3["positions"],
                "per_position_is_aes": k3["per_position_is_aes"],
                "per_position_table_sha256": k3["per_position_table_sha256"],
                "concat_sha256": k3["concat_sha256"],
                "bijective_all_positions": k3["bijective_all_positions"],
                "nestedness_check": k3["nestedness_check"],
            },
            "selfcheck_comparison": selfcheck_cmp,
            "mismatches": mismatches,
            "battery_pass": len(mismatches) == 0 and out["freeze_pass"],
            "on_failure": "ANY existing-point digest mismatch is CC3-GATE-FAIL: halt",
            "verified_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "parse_attestation": ("machine-generated JSON; parsed whole with python3 "
                                  "json.load before task completion"),
            "inference": INFERENCE,
        }
        json.dump(rv, open(battery_out_path, "w"), indent=1)
        print(json.dumps({"freeze_pass": out["freeze_pass"],
                          "battery_pass": rv["battery_pass"],
                          "mismatches": mismatches}, indent=1))
        sys.exit(0 if rv["battery_pass"] else 7)
    print(json.dumps({"freeze_pass": out["freeze_pass"]}, indent=1))
    sys.exit(0 if out["freeze_pass"] else 6)


if __name__ == "__main__":
    main()
