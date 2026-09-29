#!/usr/bin/env python3
# s2b_freeze_digest.py -- TASK-20260903-ac03af (BATCH-060cb4, GOAL-AES-003)
# Fresh for this task; re-derives the committed freeze_digest.py convention
# (lineage, as carried by s2a_freeze_digest.py) for the POST-ARM freeze
# re-verification of Stage S2b-4. Consumes the C freeze-mode output of the
# EXTENDED build re-run AFTER both k=3 arms, computes sha256 digests of every
# 256-byte per-position table, INDEPENDENTLY re-checks bijection and
# nestedness from the hex bytes, applies the folded smoke self-check
# assertions (cap-256 convention), and compares the digested result against
# the PRE-ARM committed R4_table_freeze_ext.json:
#
#   POST-ARM RE-VERIFICATION vs R4 (PREREGISTRATION.md section 6.2: 'Post-arm
#   (S2b-4) the freeze re-runs and re-verifies against R4 exactly'):
#     - every point k in {0,1,2,3,4,8,12,16}: per_position_table_sha256,
#       concat_sha256, positions, per_position_is_aes, bijection, nestedness,
#       AND the per_position_table_hex bytes themselves (R4 stores hex, so
#       byte-equality is checkable, stronger than digest equality);
#     - the k=3 concat digest must STILL equal the committed pre-arm constant
#       922e24c9c065eb79c7efcbd536b41111ad70d11a1a49cf56207832e4949c6262;
#     - aes_table_sha256, identity_table_sha256, position_order, family,
#       construction_pin, cross_k_nesting;
#     - selfcheck cap-INDEPENDENT counters compared for equality, and (R4 and
#       this re-run are BOTH cap-256 outputs of the SAME build) the
#       cap-DEPENDENT fields compared too, with the comparison disclosed;
#     - raw C output byte-identity vs the S2a-4 raw C output
#       (fbf35ae6...) reported informationally (freeze mode is deterministic;
#       the raw file carries no timestamp fields).
#   ANY mismatch on compared fields is CC3-GATE-FAIL (no data-dependent table
#   choice may enter anywhere; the k=3 arms must not perturb the surface).
#
# usage: python3 src/s2b_freeze_digest.py <c_freeze_output.json> \
#            <committed_R4.json> <s2a_raw_c_output.json> <out_verify.json>
# Exit codes: 0 pass; 7 = post-arm re-verification mismatch.
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
    "independent_session": True,
}
EXPECTED_ORDER = [0, 4, 8, 12, 1, 5, 9, 13, 2, 6, 10, 14, 3, 7, 11, 15]
EXPECTED_KS = [0, 1, 2, 3, 4, 8, 12, 16]
K3_COMMITTED_CONCAT = "922e24c9c065eb79c7efcbd536b41111ad70d11a1a49cf56207832e4949c6262"


def sha256_hex(hexstr):
    return hashlib.sha256(bytes.fromhex(hexstr)).hexdigest()


def digest_points(fj):
    aes_bytes = bytes.fromhex(fj["aes_table_hex"])
    assert len(aes_bytes) == 256
    out_points = {}
    ok = True
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
            tb = bytes.fromhex(pt["per_position_table_hex"][j])
            assert len(tb) == 256, f"k={k} pos {j}: table not 256 bytes"
            digests.append(hashlib.sha256(tb).hexdigest())
            concat += tb
            if sorted(tb) != list(range(256)):
                bijective = False
            expect = aes_bytes if is_aes_flags[j] else bytes(range(256))
            if tb != expect:
                nested = False
        if not (bijective and nested and pt["bijective_all_positions"]
                and pt["nestedness_check"]):
            ok = False
        out_points[k] = {
            "k": k,
            "positions": P_k,
            "per_position_is_aes": is_aes_flags,
            "per_position_table_sha256": digests,
            "concat_sha256": hashlib.sha256(concat).hexdigest(),
            "bijective_all_positions": bijective,
            "nestedness_check": nested,
            "per_position_table_hex": pt["per_position_table_hex"],
        }
    return out_points, ok


def main():
    c_out_path, r4_path, s2a_raw_path, out_path = sys.argv[1:5]
    raw = open(c_out_path).read()
    fj = json.loads(raw)
    assert fj["mode"] == "freeze"
    assert fj["position_order"] == EXPECTED_ORDER, "position order drifted"
    r4 = json.load(open(r4_path))
    new_points, freeze_ok = digest_points(fj)
    mismatches = []
    per_point = {}
    r4_points = {p["k"]: p for p in r4["points"]}
    for k in EXPECTED_KS:
        np_ = new_points.get(k)
        cp = r4_points.get(k)
        entry = {"k": k}
        if np_ is None or cp is None:
            mismatches.append(f"point k={k} missing (new={np_ is not None}, R4={cp is not None})")
            entry["status"] = "MISSING"
            per_point[k] = entry
            continue
        diffs = []
        if cp.get("per_position_table_sha256") != np_["per_position_table_sha256"]:
            diffs.append("per_position_table_sha256")
        if cp.get("concat_sha256") != np_["concat_sha256"]:
            diffs.append("concat_sha256")
        if cp.get("positions") != np_["positions"]:
            diffs.append("positions")
        if cp.get("per_position_is_aes") != np_["per_position_is_aes"]:
            diffs.append("per_position_is_aes")
        if cp.get("bijective_all_positions") != np_["bijective_all_positions"]:
            diffs.append("bijective_all_positions")
        if cp.get("nestedness_check") != np_["nestedness_check"]:
            diffs.append("nestedness_check")
        if cp.get("per_position_table_hex") != np_["per_position_table_hex"]:
            diffs.append("per_position_table_hex (BYTE-level)")
        if diffs:
            mismatches.append(f"k={k} post-arm fields differ vs R4: {diffs}")
        entry["status"] = "byte-equal to R4" if not diffs else "MISMATCH"
        entry["fields_compared"] = ["per_position_table_sha256", "concat_sha256", "positions",
                                    "per_position_is_aes", "bijective_all_positions",
                                    "nestedness_check", "per_position_table_hex"]
        entry["diffs"] = diffs
        if k == 3:
            entry["concat_sha256_observed"] = np_["concat_sha256"]
            entry["concat_sha256_committed_prearm_constant"] = K3_COMMITTED_CONCAT
            entry["k3_digest_still_committed"] = np_["concat_sha256"] == K3_COMMITTED_CONCAT
            if np_["concat_sha256"] != K3_COMMITTED_CONCAT:
                mismatches.append("k=3 concat digest drifted from the pre-arm committed constant")
        per_point[k] = entry
    for k in sorted(r4_points):
        if k not in new_points:
            mismatches.append(f"committed point k={k} missing from post-arm freeze")
    if fj["position_order"] != r4.get("position_order"):
        mismatches.append("position_order differs vs R4")
    aes_sha = sha256_hex(fj["aes_table_hex"])
    identity_sha = sha256_hex("".join(f"{i:02x}" for i in range(256)))
    if r4.get("aes_table_sha256") != aes_sha:
        mismatches.append("aes_table_sha256 differs vs R4")
    if r4.get("identity_table_sha256") != identity_sha:
        mismatches.append("identity_table_sha256 differs vs R4")
    if r4.get("construction_pin") != fj["construction_pin"]:
        mismatches.append("construction_pin differs vs R4")
    if r4.get("family") != fj["family"]:
        mismatches.append("family differs vs R4")
    cross_ok = fj["cross_k_nesting"] is True and r4.get("cross_k_nesting") is True
    if not cross_ok:
        mismatches.append("cross_k_nesting not true on both files")
    cap_independent_fields = ("trials", "trivial_swaps_excluded",
                              "nontrivial_trials", "W_ge1_nontrivial",
                              "whist", "W_ge1_by_word", "ewhist_all",
                              "ewhist_miss", "ewhist_hit", "zhist")
    cap_dependent_fields = ("hit_detail_records", "hit_log_overflow", "hit_log_cap")
    selfcheck_cmp = {}
    for label in ("selfcheck_identity_k0", "selfcheck_aes_k16"):
        csc = r4.get(label, {})
        nsc = fj.get(label, {})
        diffs_ind = [f for f in cap_independent_fields if csc.get(f) != nsc.get(f)]
        diffs_dep = [f for f in cap_dependent_fields if csc.get(f) != nsc.get(f)]
        if diffs_ind:
            mismatches.append(f"{label} cap-independent counters differ vs R4: {diffs_ind}")
        if diffs_dep:
            mismatches.append(f"{label} cap-dependent counters differ vs R4 (same-build cap-256 comparison): {diffs_dep}")
        selfcheck_cmp[label] = {
            "cap_independent_fields_compared": list(cap_independent_fields),
            "cap_independent_identical_to_R4": not diffs_ind,
            "cap_dependent_fields_compared_same_build_cap256": list(cap_dependent_fields),
            "cap_dependent_identical_to_R4": not diffs_dep,
            "note": "R4 and this post-arm re-run are BOTH cap-256 outputs of the same extended build, so cap-dependent fields are compared here (unlike the R3-vs-R4 battery, which disclosed them)",
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
    if not id_ok:
        mismatches.append("selfcheck_identity_k0 committed assertions fail on post-arm re-run")
    if not aes_ok:
        mismatches.append("selfcheck_aes_k16 internal-consistency assertions fail on post-arm re-run")
    s2a_raw_sha = hashlib.sha256(open(s2a_raw_path, "rb").read()).hexdigest()
    new_raw_sha = hashlib.sha256(raw.encode()).hexdigest()
    raw_byte_identity = s2a_raw_sha == new_raw_sha
    verify_pass = (len(mismatches) == 0 and freeze_ok and cross_ok
                   and id_ok and aes_ok
                   and new_points[3]["concat_sha256"] == K3_COMMITTED_CONCAT)
    out = {
        "schema": "crypto.autoresearch.s2b4_postarm_freeze_reverification.v1",
        "task_id": "TASK-20260903-ac03af",
        "batch_id": "BATCH-060cb4",
        "goal_id": "GOAL-AES-003",
        "idea_record": "IDEA-20260903-8f26ac",
        "run_id": "S2b-4",
        "c_freeze_output": c_out_path,
        "committed_freeze_file_R4": r4_path,
        "s2a_raw_c_output_reference": s2a_raw_path,
        "freeze_seed": fj["freeze_seed"],
        "post_arm": True,
        "order_note": "this freeze re-run executes AFTER both k=3 arms (S2b-2, S2b-3) and BEFORE the CC3 composition",
        "k3_arms_run_before_this_rerun": ["U3_k3_seed1 (seed 531001, armid 11)", "U4_k3_seed2 (seed 531002, armid 11)"],
        "per_point_comparison": per_point,
        "k3_digest_still_committed": new_points[3]["concat_sha256"] == K3_COMMITTED_CONCAT,
        "k3_concat_sha256_observed": new_points[3]["concat_sha256"],
        "k3_concat_sha256_committed_prearm_constant": K3_COMMITTED_CONCAT,
        "aes_table_sha256": aes_sha,
        "identity_table_sha256": identity_sha,
        "position_order": fj["position_order"],
        "cross_k_nesting": fj["cross_k_nesting"],
        "selfcheck_comparison_vs_R4": selfcheck_cmp,
        "selfcheck_identity_k0_assert_pass": id_ok,
        "selfcheck_aes_k16_assert_pass": aes_ok,
        "raw_c_output_sha256_postarm": new_raw_sha,
        "raw_c_output_sha256_s2a": s2a_raw_sha,
        "raw_c_output_byte_identity_vs_s2a_informational": raw_byte_identity,
        "raw_byte_identity_note": "freeze mode is deterministic and the raw C output carries no timestamp fields; byte-identity vs the S2a-4 raw output (fbf35ae6...) is the strongest form of re-verification and is reported informationally - the binding check is the field-level equality vs R4 above",
        "mismatches": mismatches,
        "mismatch_count_expected": 0,
        "freeze_ok": freeze_ok,
        "reverification_pass": verify_pass,
        "on_failure": "ANY mismatch vs the pre-arm R4 commitment is CC3-GATE-FAIL: halt (no data-dependent table choice may enter; the k=3 arms must not perturb the surface)",
        "verified_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "parse_attestation": "machine-generated JSON; parsed whole with python3 json.load (C input and R4) before composition",
        "inference": INFERENCE,
    }
    json.dump(out, open(out_path, "w"), indent=1)
    print(json.dumps({"reverification_pass": verify_pass, "mismatches": mismatches,
                      "k3_digest_still_committed": out["k3_digest_still_committed"],
                      "raw_byte_identity_vs_s2a": raw_byte_identity}, indent=1))
    sys.exit(0 if verify_pass else 7)


if __name__ == "__main__":
    main()
