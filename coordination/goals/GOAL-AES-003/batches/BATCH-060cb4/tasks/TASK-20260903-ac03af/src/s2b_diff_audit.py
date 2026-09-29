#!/usr/bin/env python3
# s2b_diff_audit.py -- TASK-20260903-ac03af (BATCH-060cb4, GOAL-AES-003)
# Fresh for this task. POST-ARM source-diff audit of Stage S2b-4: the
# extended source used for the k=3 arms must STILL differ from the frozen
# base source by EXACTLY the declared diff list of IDEA-20260903-8f26ac
# family_extension_design.declared_source_diff (BINDING; PREREGISTRATION.md
# section 6.1), and the extended binary must still hash to the certified
# 3ccc377c... . Re-derives the unified diff, classifies the changed base
# lines against the protected regions, and compares the hunk content
# byte-for-byte with the S2a-1 audited diff (runs/S2a1_diff_audit.txt,
# sha256 2a17faa1...), which was itself judged equal to the declared list
# EXACTLY. Any additional diff is CC3-GATE-FAIL.
#
# usage: python3 src/s2b_diff_audit.py <base.c> <extended.c> <extended_bin> \
#            <s2a_diff_audit.txt> <out_diff.txt> <out_audit.json>
# Exit codes: 0 pass; 12 = CC3-GATE-FAIL.
import json, sys, hashlib, subprocess, datetime

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
BASE_SHA = "ec748cefcb1fccfdd4e441a4898b21cf4b7eff056599ce07769e3f0fab091f37"
EXT_SHA = "45808af6ff6fa18d805dac8910845b01813e4b9b49ae289fcc705e2913fad1c0"
BIN_SHA = "3ccc377cdee7e4c433570b5541e057a6bbc20ca4fb32b59028211c5a88324db8"
S2A_DIFF_SHA = "2a17faa1422d8448ce146908db43e4a4b0e1ba473060b02ed49fb981d3184f4c"
PROTECTED_REGIONS = {
    "counter_increment_sites_worker(:387-499 incl zhist/whist :459)": (387, 499),
    "cap_branch(:489-495)": (489, 495),
    "table_construction_set_diluted_tables(:199-220)": (199, 220),
    "table_construction_diluted_position_list(:222-240)": (222, 240),
    "pin_mode(:542-624)": (542, 624),
    "pinidentity_mode(:626-659)": (626, 659),
    "geom_mode(:661-669)": (661, 669),
    "mini_arm_emit(:681-731 base)": (681, 731),
    "schedule_pin_block(:856-875 base)": (856, 875),
    "stream_derivation_and_trial_loop(:877-899 base)": (877, 899),
    "aggregation_and_receipt_emission(:900-1043 base)": (900, 1043),
}
DECLARED_ITEMS = [
    "(i) arm-mode sbox-token whitelist: ADD token s3 mapping to ksel=3 (one else-if branch mirroring s1/s2/s4/s8/s12); refusal message names the admitted set",
    "(ii) FREEZE_KS {0,1,2,4,8,12,16} -> {0,1,2,3,4,8,12,16} (one array entry; loop bounds 7->8 in point-emission and cross-k-nesting loops)",
    "(iii) usage string and freeze-mode header comment, naming the extended point",
    "NOTHING ELSE",
]


def sha256_file(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def changed_base_lines(diff_text):
    lines = []
    old_ln = None
    for ln in diff_text.splitlines():
        if ln.startswith("@@"):
            parts = ln.split()
            old = parts[1]
            old_start = int(old.split(",")[0][1:])
            old_ln = old_start
        elif old_ln is None:
            continue
        elif ln.startswith("---") or ln.startswith("+++"):
            continue
        elif ln.startswith("-"):
            lines.append(old_ln)
            old_ln += 1
        elif ln.startswith("+"):
            pass
        elif ln.startswith("\\"):
            pass
        else:
            old_ln += 1
    return sorted(set(lines))


def main():
    base_c, ext_c, ext_bin, s2a_diff_path, out_diff, out_json = sys.argv[1:7]
    base_sha = sha256_file(base_c)
    ext_sha = sha256_file(ext_c)
    bin_sha = sha256_file(ext_bin)
    proc = subprocess.run(["diff", "-u", base_c, ext_c], capture_output=True, text=True)
    diff_text = proc.stdout
    open(out_diff, "w").write(diff_text)
    diff_sha = hashlib.sha256(diff_text.encode()).hexdigest()
    hunks_new = "\n".join(diff_text.splitlines()[2:])
    s2a_raw = open(s2a_diff_path).read()
    s2a_sha = hashlib.sha256(s2a_raw.encode()).hexdigest()
    hunks_s2a = "\n".join(s2a_raw.splitlines()[2:])
    hunk_content_identical_to_s2a_audit = hunks_new == hunks_s2a
    cbl = changed_base_lines(diff_text)
    hunk_count = diff_text.count("\n@@")
    violations = []
    for region, (lo, hi) in PROTECTED_REGIONS.items():
        inside = [n for n in cbl if lo <= n <= hi]
        if inside:
            violations.append({"region": region, "changed_lines_inside": inside})
    extra_hunks = hunk_count - 5
    hash_ok = (base_sha == BASE_SHA and ext_sha == EXT_SHA and bin_sha == BIN_SHA
               and s2a_sha == S2A_DIFF_SHA)
    verdict_ok = (hash_ok and hunk_content_identical_to_s2a_audit
                  and hunk_count == 5 and extra_hunks == 0
                  and not violations
                  and cbl == [672, 679, 743, 770, 775, 814, 848])
    out = {
        "schema": "crypto.autoresearch.s2b4_postarm_diff_audit.v1",
        "task_id": "TASK-20260903-ac03af",
        "batch_id": "BATCH-060cb4",
        "goal_id": "GOAL-AES-003",
        "idea_record": "IDEA-20260903-8f26ac",
        "run_id": "S2b-4",
        "post_arm": True,
        "order_note": "audited AFTER both k=3 arms and the post-arm freeze re-run, BEFORE the CC3 composition",
        "base_source": base_c,
        "extended_source": ext_c,
        "extended_binary": ext_bin,
        "base_sha256_observed": base_sha,
        "base_sha256_frozen": BASE_SHA,
        "extended_sha256_observed": ext_sha,
        "extended_sha256_certified": EXT_SHA,
        "binary_sha256_observed": bin_sha,
        "binary_sha256_certified": BIN_SHA,
        "binary_hash_recheck_pass": bin_sha == BIN_SHA,
        "declared_diff_source": "IDEA-20260903-8f26ac family_extension_design.declared_source_diff (BINDING); PREREGISTRATION.md section 6.1",
        "declared_items": DECLARED_ITEMS,
        "diff_file": out_diff,
        "diff_sha256": diff_sha,
        "hunk_count": hunk_count,
        "expected_hunk_count": 5,
        "extra_hunks_beyond_declared": extra_hunks,
        "changed_base_lines": cbl,
        "changed_base_lines_expected_S2a1": [672, 679, 743, 770, 775, 814, 848],
        "s2a_diff_audit_reference": s2a_diff_path,
        "s2a_diff_audit_sha256_observed": s2a_sha,
        "s2a_diff_audit_sha256_bound": S2A_DIFF_SHA,
        "hunk_content_identical_to_s2a_audit_modulo_header_paths": hunk_content_identical_to_s2a_audit,
        "equivalence_argument": ("same frozen base bytes (ec748cef...) and same extended bytes (45808af6...) as the "
                                 "S2a-1 audit -> identical hunk content; the S2a-1 audit (sha256 2a17faa1...) judged that "
                                 "diff equal to the declared list EXACTLY (items i/ii/iii, nothing else); only the two "
                                 "header lines carrying file paths/timestamps differ between the two diff texts"),
        "protected_regions_check": {
            region: {"range": list(rng),
                     "changed_lines_inside": [n for n in cbl if rng[0] <= n <= rng[1]]}
            for region, rng in PROTECTED_REGIONS.items()
        },
        "protected_region_violations": violations,
        "nothing_else_satisfied": extra_hunks == 0 and not violations,
        "hash_checks_pass": hash_ok,
        "equality_verdict": ("PASS: post-arm diff still equals the declared list EXACTLY (items i/ii/iii, nothing else)"
                             if verdict_ok else "CC3-GATE-FAIL: post-arm diff deviates from the declared list"),
        "on_failure": "ANY additional diff vs the frozen base is CC3-GATE-FAIL: halt",
        "audited_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "parse_attestation": "machine-generated JSON; parsed whole with python3 json.load before composition",
        "inference": INFERENCE,
    }
    json.dump(out, open(out_json, "w"), indent=1)
    print(json.dumps({"equality_verdict": out["equality_verdict"],
                      "hunk_count": hunk_count, "changed_base_lines": cbl,
                      "hunk_content_identical_to_s2a": hunk_content_identical_to_s2a_audit,
                      "binary_hash_recheck_pass": out["binary_hash_recheck_pass"],
                      "violations": violations}, indent=1))
    sys.exit(0 if verdict_ok else 12)


if __name__ == "__main__":
    main()
