"""POST-SEAL checks for J1 (TASK-20260924-7e2d94). Written and run AFTER seal.txt.

Not part of the sealed verifier. Reads the sealed verification.json, the run's
cell-summary.json and decision-rules.json (allowed after the seal by the card's
must_not_read_note), and instance-sets.json E_hex (allowed after the
construction is fixed, VC-2).

PS-1  counted-set check: the (instance, closure) pairs MR1-MR4 count are exactly
      the pairs carrying a certificate verified by MY code; no counted pair
      lacks a certificate; the MR5 certificate table matches my counts.
PS-2  VC-2 optional construction agreement on the 144 curve instances: my
      f_0..f_16 against E_hex decoded as a list of 17 row integers, bit j (LSB
      first) = column j of mu_order(2) (degree ascending, lexicographic index
      tuples). The bit layout is NOT stated at bit level in the a4f217 receipt
      or in null-systems.json's convention string; it was identified by trying
      two readings of the list-of-rows form on ONE instance (U62:F-S3:27):
      LSB-first matched, MSB-first-in-172-bits did not. It is then applied
      unchanged to all 144.
PS-3  (extra, beyond VC-2's letter) the same decoding applied to the 124 null
      E_hex, compared with systems/null-systems.json: an independent re-check
      of the opening archive's extraction.
"""
import datetime as dt
import hashlib
import itertools
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import descent as D   # noqa: E402

TASK_DIR = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(TASK_DIR, "../../../../.."))
RUN = os.path.join(REPO, "experiments/EXP-CERTBIN-e94b27/runs/RUN-CERTBIN-c417e0")
NULLS = os.path.join(REPO, "coordination/review/certbin-20260924-3d7e1a/systems/null-systems.json")
B_CURVE = json.load(open(os.path.join(REPO, "experiments/EXP-CERTBIN-4e92d7/runs/RUN-CERTBIN-3b7e05/curve.json")))["B"]


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def canon(f):
    return hashlib.sha256(json.dumps([sorted([i for i in range(18) if (m >> i) & 1] for m in e) for e in f],
                                     separators=(",", ":")).encode()).hexdigest()


def main():
    seal = open(os.path.join(TASK_DIR, "seal.txt")).read()
    ver_path = os.path.join(TASK_DIR, "verification.json")
    ver_sha = sha(ver_path)
    out = {"schema": "certbin.rc1.j1_post_seal_checks.v1", "task_id": "TASK-20260924-7e2d94",
           "run_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "verification_json_sha256": ver_sha,
           "verification_json_sha256_equals_seal": ("sha256: " + ver_sha) in seal,
           "inputs_sha256": {}}
    for p in ("cell-summary.json", "decision-rules.json", "instance-sets.json"):
        out["inputs_sha256"]["experiments/EXP-CERTBIN-e94b27/runs/RUN-CERTBIN-c417e0/" + p] = sha(os.path.join(RUN, p))
    ver = json.load(open(ver_path))
    cs = json.load(open(os.path.join(RUN, "cell-summary.json")))
    dr = json.load(open(os.path.join(RUN, "decision-rules.json")))
    sets = json.load(open(os.path.join(RUN, "instance-sets.json")))["sets"]

    # ---------------------------------------------------------------- PS-1
    mine = {}
    for r in ver["certificates"]:
        mine.setdefault((r["closure"], r["set"]), {"submitted": 0, "verified": set(), "rejected": set()})
        e = mine[(r["closure"], r["set"])]
        e["submitted"] += 1
        (e["verified"] if r["verified"] else e["rejected"]).add(r["key"])
    all_keys = {s: {e["key"] for e in lst} for s, lst in sets.items()}

    def ver_keys(cl, s):
        return mine.get((cl, s), {"verified": set()})["verified"]

    ps1 = {}
    u62 = all_keys["U62"]
    w4u = ver_keys("W_4", "U62")
    m5u = ver_keys("M_5", "U62")
    ps1["MR1"] = {"run_a": cs["MR1_w4_refuted_U62"]["a"], "run_n": cs["MR1_w4_refuted_U62"]["n"],
                  "my_verified_W4_U62": len(w4u), "equal": cs["MR1_w4_refuted_U62"]["a"] == len(w4u),
                  "decision_rules_a": dr["rules"]["RC1-DR-1"]["inputs"]["a"]}
    ps1["MR2"] = {"run_b": cs["MR2_m5_refuted_U62"]["b"], "my_verified_M5_U62": len(m5u),
                  "equal": cs["MR2_m5_refuted_U62"]["b"] == len(m5u),
                  "my_verified_M5_U62_is_all_of_U62": m5u == u62,
                  "decision_rules_b": dr["rules"]["RC1-DR-3"]["inputs"]["b"]}
    r_mine = w4u | m5u | ver_keys("W_5", "U62")
    ps1["MR3"] = {"run_r": cs["MR3_refuted_at_D_le_5_U62"]["r"], "run_label_counts": cs["MR3_refuted_at_D_le_5_U62"]["label_counts"],
                  "my_verified_any_closure_U62": len(r_mine), "equal": cs["MR3_refuted_at_D_le_5_U62"]["r"] == len(r_mine),
                  "my_label_W4": len(w4u), "decision_rules_r": dr["rules"]["RC1-DR-2"]["inputs"]["r"]}
    mr4 = {}
    for s in ("N-AFF62", "N-F262"):
        for cl in ("W_4", "M_5", "W_5"):
            run_v = cs["MR4_null_refutation_rates"][s][cl]["verified_refuted"]
            mr4[f"{s}|{cl}"] = {"run_verified_refuted": run_v, "run_n": cs["MR4_null_refutation_rates"][s][cl]["n"],
                                "my_verified": len(ver_keys(cl, s)), "equal": run_v == len(ver_keys(cl, s))}
    ps1["MR4"] = mr4
    # per-instance W_4 flags against my verified W_4 certificates, every set
    flags = {e["key"]: e["one"] for e in cs["secondary"]["per_instance_W4"]}
    my_w4 = set().union(*[ver_keys("W_4", s) for s in sets])
    counted_w4 = {k for k, v in flags.items() if v}
    ps1["W4_per_instance"] = {"instances_listed": len(flags), "run_one_true": len(counted_w4),
                              "my_verified_W4_keys": len(my_w4),
                              "run_one_true_without_my_verified_certificate": sorted(counted_w4 - my_w4),
                              "my_verified_certificate_where_run_one_false": sorted(my_w4 - counted_w4),
                              "sets_equal": counted_w4 == my_w4}
    mr5 = {}
    for kc, e in cs["MR5_soundness_and_certificates"]["certificates"].items():
        cl, s = kc.split("/")
        m = mine.get((cl, s), {"submitted": 0, "verified": set(), "rejected": set()})
        mr5[kc] = {"run": e, "my_submitted": m["submitted"], "my_verified": len(m["verified"]), "my_rejected": len(m["rejected"]),
                   "equal": (e["reported_refutations"] == e["submitted"] == m["submitted"] and e["verified"] == len(m["verified"])
                             and e["failed"] == len(m["rejected"]) and e["uncertified"] == 0)}
    ps1["MR5_certificate_table"] = mr5
    ps1["kinds_in_my_file_not_in_run_table"] = sorted(f"{cl}/{s}" for (cl, s) in mine if f"{cl}/{s}" not in cs["MR5_soundness_and_certificates"]["certificates"])
    ps1["all_equal"] = (ps1["MR1"]["equal"] and ps1["MR2"]["equal"] and ps1["MR3"]["equal"] and all(v["equal"] for v in mr4.values())
                        and ps1["W4_per_instance"]["sets_equal"] and all(v["equal"] for v in mr5.values())
                        and not ps1["kinds_in_my_file_not_in_run_table"])
    # certificate size secondary (run-report / cell-summary) against my |C|
    sizes = {}
    for cl in ("W_4", "M_5"):
        cc = sorted(r["C_size"] for r in ver["certificates"] if r["closure"] == cl)
        n = len(cc)
        med = (cc[n // 2] if n % 2 else (cc[n // 2 - 1] + cc[n // 2]) / 2) if n else None
        md = Counter(r["max_deg_mu"] for r in ver["certificates"] if r["closure"] == cl)
        run = cs["secondary"]["certificate_sizes"][cl]
        mine_c = {"count": n, "min": cc[0], "median": med, "max": cc[-1], "max_deg_mu_max": max(md),
                  "max_deg_mu_distribution": {str(k): v for k, v in sorted(md.items())}}
        sizes[cl] = {"run": run, "mine": mine_c,
                     "equal": all(float(run[k]) == float(mine_c[k]) for k in ("count", "min", "median", "max", "max_deg_mu_max"))
                     and run["max_deg_mu_distribution"] == mine_c["max_deg_mu_distribution"]}
    ps1["certificate_sizes_secondary"] = sizes
    out["PS-1_counted_set"] = ps1

    # ---------------------------------------------------------------- PS-2 / PS-3
    mons = [()] + [(i,) for i in range(18)] + list(itertools.combinations(range(18), 2))
    masks = [sum(1 << i for i in m) for m in mons]

    def decode(rows_hex):
        rows = [int(h, 16) for h in rows_hex]
        return [frozenset(masks[j] for j in range(172) if (rows[k] >> j) & 1) for k in range(len(rows))], \
            [rows[k] >> 172 for k in range(len(rows))]

    ps2 = {"layout": "list of 17 row integers (hex); bit j, LSB first, = column j of mu_order(2) = [()] + [(i,)] + combinations(range(18), 2)",
           "layout_identification": "two readings tried on U62:F-S3:27 only (LSB-first matched; MSB-first within 172 bits did not); then applied unchanged",
           "compared": 0, "agree": 0, "disagree_keys": [], "high_bits_nonzero_keys": [],
           "my_system_sha256_equals_sealed_construction": 0}
    for s in ("U62", "S62", "C20"):
        for e in sets[s]:
            xR = e["archived"]["x_R"]
            mine_f, _ = D.descend_symbolic(xR, B_CURVE)
            dec, hi = decode(e["E_hex"])
            ps2["compared"] += 1
            if len(dec) == 17 and dec == list(mine_f):
                ps2["agree"] += 1
            else:
                ps2["disagree_keys"].append(e["key"])
            if any(hi):
                ps2["high_bits_nonzero_keys"].append(e["key"])
            if canon(mine_f) == ver["construction"][e["key"]]["system_sha256"]:
                ps2["my_system_sha256_equals_sealed_construction"] += 1
    out["PS-2_curve_E_hex_construction_agreement"] = ps2
    nulls = json.load(open(NULLS))
    ps3 = {"compared": 0, "agree": 0, "disagree_keys": []}
    for s in ("N-AFF62", "N-F262"):
        for e in sets[s]:
            dec, hi = decode(e["E_hex"])
            ns = [frozenset(sum(1 << i for i in mono) for mono in eq) for eq in nulls[e["key"]]["equations"]]
            ps3["compared"] += 1
            if dec == ns and not any(hi):
                ps3["agree"] += 1
            else:
                ps3["disagree_keys"].append(e["key"])
    out["PS-3_null_E_hex_vs_null_systems_json"] = ps3
    p = os.path.join(TASK_DIR, "post-seal-checks.json")
    with open(p, "w") as fh:
        json.dump(out, fh, indent=1)
        fh.write("\n")
    print(json.dumps({"verification_json_sha256_equals_seal": out["verification_json_sha256_equals_seal"],
                      "PS-1_all_equal": ps1["all_equal"], "W4_sets_equal": ps1["W4_per_instance"]["sets_equal"],
                      "sizes_equal": {k: v["equal"] for k, v in sizes.items()},
                      "PS-2": {k: ps2[k] for k in ("compared", "agree", "disagree_keys", "high_bits_nonzero_keys", "my_system_sha256_equals_sealed_construction")},
                      "PS-3": ps3}, indent=1))


if __name__ == "__main__":
    main()
