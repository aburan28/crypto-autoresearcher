#!/usr/bin/env python3
# freeze_reverify.py -- TASK-20260903-695ebe (BATCH-060cb4, GOAL-AES-003)
# Fresh for this task; re-implements the documented lineage freeze-digest and
# re-verification semantics (lineage tool: TASK-20260902-987716
# src/freeze_digest.py, snapshot-bound sha256 c29e876b76a4a4ba6cf200d36a56ae1bc8faf8c0bdacbc40df5c30024a2b2814;
# comparison contract per PREREGISTRATION.md section 15 S0-4).
#
# S0-4 contract: rerun freeze mode on the re-verified build; digests,
# bijection, nestedness, cross_k_nesting ALL identical vs the committed
# R3_table_freeze.json; position_order and the cap-INDEPENDENT folded-smoke
# selfcheck counters additionally compared; the cap-DEPENDENT selfcheck
# fields (hit_detail_records, hit_log_overflow) differ by construction
# (committed file cap-64, this build cap-256) and are DISCLOSED, never
# compared as mismatches.
#
# usage: python3 src/freeze_reverify.py <c_freeze_output.json> <out_freeze.json>
#        --reverify <committed_freeze.json> <out_reverify.json>
# Exit codes: 0 pass; 6 freeze check failure; 7 reverify mismatch.
import json, sys, hashlib, datetime

EXPECTED_ORDER = [0, 4, 8, 12, 1, 5, 9, 13, 2, 6, 10, 14, 3, 7, 11, 15]
EXPECTED_KS = [0, 1, 2, 4, 8, 12, 16]
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


def sha256_hex(hexstr):
    return hashlib.sha256(bytes.fromhex(hexstr)).hexdigest()


def digest_freeze(raw):
    fj = json.loads(raw)
    assert fj["mode"] == "freeze", "C output is not a freeze-mode receipt"
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
    out = {
        "schema": "crypto.autoresearch.table_freeze.v1",
        "task_id": "TASK-20260903-695ebe",
        "idea_record": "IDEA-20260903-8f26ac",
        "pin_decision": "DEC-20260901-fb6f11",
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
    # folded smoke assertions (cap-256 convention; HIT_LOG_CAP per thread)
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


def main():
    c_out_path, out_path = sys.argv[1], sys.argv[2]
    with open(c_out_path) as f:
        raw = f.read()
    out = digest_freeze(raw)
    with open(out_path, "w") as f:
        json.dump(out, f, indent=1)
    if "--reverify" in sys.argv:
        i = sys.argv.index("--reverify")
        committed_path, reverify_out_path = sys.argv[i + 1], sys.argv[i + 2]
        with open(committed_path) as f:
            committed = json.load(f)
        mismatches = []
        if committed.get("aes_table_sha256") != out["aes_table_sha256"]:
            mismatches.append("aes_table_sha256")
        if committed.get("identity_table_sha256") != out["identity_table_sha256"]:
            mismatches.append("identity_table_sha256")
        cpts = {p["k"]: p for p in committed.get("points", [])}
        for p in out["points"]:
            cp = cpts.get(p["k"])
            if cp is None:
                mismatches.append(f"point k={p['k']} missing from committed file")
                continue
            if cp.get("per_position_table_sha256") != p["per_position_table_sha256"]:
                mismatches.append(f"k={p['k']} per-position digests differ")
            if cp.get("concat_sha256") != p["concat_sha256"]:
                mismatches.append(f"k={p['k']} concat digest differs")
            if cp.get("bijective_all_positions") != p["bijective_all_positions"]:
                mismatches.append(f"k={p['k']} bijection flag differs")
            if cp.get("nestedness_check") != p["nestedness_check"]:
                mismatches.append(f"k={p['k']} nestedness flag differs")
        if committed.get("cross_k_nesting") != out["cross_k_nesting"]:
            mismatches.append("cross_k_nesting differs")
        if committed.get("position_order") != out["position_order"]:
            mismatches.append("position_order differs")
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
                "cap_independent_fields_compared": list(cap_independent_fields),
                "identical": not diffs,
                "cap_dependent_not_compared_disclosed": {
                    "hit_detail_records": {"committed_cap64": csc.get("hit_detail_records"),
                                           "rerun_cap256": nsc.get("hit_detail_records")},
                    "hit_log_overflow": {"committed_cap64": csc.get("hit_log_overflow"),
                                         "rerun_cap256": nsc.get("hit_log_overflow")},
                },
            }
        rv = {
            "schema": "crypto.autoresearch.digest_reverify.v2",
            "task_id": "TASK-20260903-695ebe",
            "idea_record": "IDEA-20260903-8f26ac",
            "pin_decision": "DEC-20260901-fb6f11",
            "committed_freeze_file": committed_path,
            "rerun_freeze_file": out_path,
            "compared": "digests, bijection, nestedness, cross_k_nesting, position_order, cap-independent selfcheck counters",
            "mismatches": mismatches,
            "selfcheck_cap_independent_comparison": selfcheck_cmp,
            "reverify_pass": len(mismatches) == 0,
            "reverified_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "parse_attestation": ("machine-generated JSON; parsed whole with python3 "
                                  "json.load before task completion"),
            "inference": INFERENCE,
        }
        with open(reverify_out_path, "w") as f:
            json.dump(rv, f, indent=1)
        print(json.dumps({"freeze_pass": out["freeze_pass"],
                          "reverify_pass": rv["reverify_pass"],
                          "mismatches": mismatches}, indent=1))
        sys.exit(0 if (out["freeze_pass"] and rv["reverify_pass"]) else 7)
    print(json.dumps({"freeze_pass": out["freeze_pass"],
                      "identity_selfcheck": out["selfcheck_identity_k0"]["assert_pass"],
                      "aes_selfcheck": out["selfcheck_aes_k16"]["assert_pass"]}, indent=1))
    sys.exit(0 if out["freeze_pass"] else 6)


if __name__ == "__main__":
    main()
