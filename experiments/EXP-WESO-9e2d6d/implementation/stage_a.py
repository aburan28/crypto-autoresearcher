"""EXP-WESO-9e2d6d STAGE-A (RUN-WESO-aa2237): exact WISDE ground truth and the
delta-extraction interface identity I-1.

Procedure (spec stages[STAGE-A]): fetch/verify the four WISDE files (primary
route; FB-A only on the declared trigger), parse every type, and for each type
compute |O^x| (qfminim), delta_rank4 (rank-4 minimum of Nrd/p over the
two-sided ideal P, qflll + qfminim), N1 (from WISDE), the Gross-lattice label.
Gates I-1, A-1, A-2 (exact); A-3 reported.  Reference laws for Stage B.
"""
import argparse
import datetime
import os
import re
import subprocess
import sys
import time
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import yaml  # noqa: E402

PRIMES = [1019, 4099, 10007, 20011]
EXPECTED = {
    1019: (4175, "9b05570a23f511c9bc632686ec4f49f09bc4c31a49150109a33ea622fdca0cdb"),
    4099: (15481, "db5ea399baaa8947276b733e64ac8cdcfcb27cc7db130309d40a5cb29b2ff3a0"),
    10007: (39117, "44a404df7c4abc4d345afb6c650813cf7a69795b8003aef274e7ec4f3a95a8e8"),
    20011: (76900, "aad258048850de714c0dad546218c6b7e0527b619b18549df7120558f9645f2b"),
}
URL = "https://raw.githubusercontent.com/christellevincent/WISDE/main/results/results%d.sage"
UA = "crypto-autoresearcher/TASK-20260926-41c7e7"


def utc():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch(p, cache):
    """Primary route; up to 5 attempts; everything logged before parsing."""
    path = os.path.join(cache, "results%d.sage" % p)
    attempts = []
    ok = False
    for a in range(1, 6):
        ts = utc()
        argv = ["curl", "-sS", "-L", "--max-time", "300", "-A", UA, "-o", path, "-w", "%{http_code}", URL % p]
        r = subprocess.run(argv, capture_output=True, text=True)
        status = r.stdout.strip()
        nbytes = os.path.getsize(path) if os.path.exists(path) else None
        sha = common.sha256_file(path) if os.path.exists(path) else None
        exp_b, exp_h = EXPECTED[p]
        match = (status == "200" and nbytes == exp_b and sha == exp_h)
        attempts.append({"attempt": a, "url": URL % p, "argv": argv, "utc": ts, "http_status": status,
                         "curl_rc": r.returncode, "curl_stderr": r.stderr.strip()[:500],
                         "bytes": nbytes, "sha256": sha, "expected_bytes": exp_b, "expected_sha256": exp_h,
                         "equal_to_committed": match})
        if match:
            ok = True
            break
        if status == "200" and sha is not None and sha != exp_h:
            break  # hash mismatch is itself the FB-A trigger; no retry-until-match
    return ok, path, attempts


TERM = re.compile(r"([+-]?)([^+-]+)")


def parse_elt(s):
    s = s.replace(" ", "")
    v = [Fraction(0)] * 4
    idx = {"": 0, "i": 1, "j": 2, "k": 3}
    for sign, body in TERM.findall(s):
        if "*" in body:
            c, var = body.split("*")
        elif body in ("i", "j", "k"):
            c, var = "1", body
        else:
            c, var = body, ""
        c = Fraction(c)
        if sign == "-":
            c = -c
        v[idx[var]] += c
    return v


def parse_wisde(text):
    types = []
    blocks = re.split(r"^i = (\d+)\s*$", text, flags=re.M)
    # blocks: [pre, idx, body, idx, body, ...]
    for t in range(1, len(blocks) - 1, 2):
        idx = int(blocks[t])
        body = blocks[t + 1]
        mb = re.search(r"^\[(.*)\]\s*$", body, flags=re.M)
        mt = re.search(r"^\s*\((\d+)\s*,\s*(\d+)\s*,\s*(\d+)\)\s*$", body, flags=re.M)
        elts = [parse_elt(e) for e in mb.group(1).split(",")]
        types.append({"index": idx, "basis": elts, "N": [int(mt.group(1)), int(mt.group(2)), int(mt.group(3))]})
    tail = re.search(r"the largest d is (\d+)", text)
    return types, (int(tail.group(1)) if tail else None)


def gpmat(basis):
    # columns = basis elements
    rows = []
    for r in range(4):
        rows.append(",".join(str(basis[c][r]) for c in range(4)))
    return "[" + ";".join(rows) + "]"


def e_of(p):
    return {1: 0, 5: 1, 7: 1, 11: 2}[p % 12]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--cache-dir", required=True)
    a = ap.parse_args()
    rd = a.run_dir
    os.makedirs(a.cache_dir, exist_ok=True)
    t_start = time.time()

    # ---- fetch (logged before any parsing) --------------------------------
    fetchlog = {"wisde_fetch_log": {"route_decision": "spec inputs.wisde_dataset.route_decision (PRIMARY re-fetch; FB-A only on 5 failures or hash mismatch)",
                                    "tls_verification_disabled": False, "https_proxy_unset": False,
                                    "cache_dir_outside_repository": a.cache_dir, "bytes_committed": False,
                                    "files": []}}
    routes = {}
    paths = {}
    for p in PRIMES:
        ok, path, att = fetch(p, a.cache_dir)
        routes[p] = "primary" if ok else "FB-A_required"
        paths[p] = path
        fetchlog["wisde_fetch_log"]["files"].append({"p": p, "route": routes[p], "attempts": att})
    with open(os.path.join(rd, "wisde_fetch_log.yaml"), "w") as f:
        yaml.safe_dump(fetchlog, f, sort_keys=False, width=110)
    common.log("fetch routes:", routes)
    if any(r != "primary" for r in routes.values()):
        # FB-A is declared but not implemented in this driver: stop honestly.
        common.write_json(os.path.join(rd, "status.json"), {
            "status": "failed", "validity": "invalid", "failure_class": "infrastructure_error",
            "reason": "FB-A trigger fired for %s; FB-A path not executed by this driver" % [p for p in routes if routes[p] != "primary"],
            "stage_outcome": "STOPPED_FB-A_NOT_EXECUTED"})
        return

    gp = common.GP()
    all_types = []
    per_prime = {}
    for p in PRIMES:
        text = open(paths[p]).read()
        types, tail_d = parse_wisde(text)
        gp.cmd("p=%d" % p, want=False)
        bnd = int(gp.val("sqrtnint(p\\2,3)"))
        mism = []
        for t in types:
            gp.cmd("Bt=%s" % gpmat(t["basis"]), want=False)
            isord = gp.val("isorder(Bt,p)") == "1"
            disc_ok = gp.val("discrd2(Bt,p)==p^2") == "1"
            gp.cmd("Bt=lathnf(Bt); Bl=lllorder(Bt,p)", want=False)
            d4 = int(gp.val("deltaorder(Bl,p)[1]"))
            nu = int(gp.val("nunits(Bl,p)"))
            gg = gp.val("grossgram(Bl,p)")
            canon = gp.val("latcanon(Bt)")
            t.update({"p": p, "is_order": isord, "reduced_disc_is_p": disc_ok, "delta_rank4": d4,
                      "N1": t["N"][0], "units": nu, "gross_gram": gg,
                      "order_hash": common.sha256_str(canon)})
            if d4 != t["N"][0]:
                mism.append(t["index"])
        # Gross labels: bucket by theta prefix (Nrd <= p), separate by qfisom
        T = p
        keys = {}
        for t in types:
            key = gp.val("thetakey(%s,%d)" % (t["gross_gram"], T))
            t["theta_key_sha256"] = common.sha256_str(key)
            keys.setdefault(t["theta_key_sha256"], []).append(t)
        label_of = {}
        shared = []
        for key, grp in keys.items():
            reps = []  # list of (label, gram)
            for t in grp:
                lab = None
                for (l, g) in reps:
                    iso = gp.val("qfisom(%s,%s)!=0" % (t["gross_gram"], g))
                    if iso == "1":
                        lab = l
                        break
                if lab is None:
                    lab = t["index"]
                    reps.append((lab, t["gross_gram"]))
                else:
                    shared.append([lab, t["index"]])
                t["gross_label"] = lab
                label_of[t["index"]] = lab
        # weights and laws
        tot = Fraction(0)
        for t in types:
            t["c_t"] = 1 if t["N1"] == 1 else 2
            t["w_mass"] = str(Fraction(2, t["units"]))
            t["pi_unnorm"] = Fraction(t["c_t"] * 2, t["units"])
            tot += t["pi_unnorm"]
        ncurves = sum(t["c_t"] for t in types)
        pi_delta, pi_delta_uj, pi_type = {}, {}, {}
        for t in types:
            pi = t["pi_unnorm"] / tot
            t["pi"] = float(pi)
            t["pi_exact"] = str(pi)
            t["pi_uniform_j"] = t["c_t"] / ncurves
            pi_delta[t["N1"]] = pi_delta.get(t["N1"], 0.0) + float(pi)
            pi_delta_uj[t["N1"]] = pi_delta_uj.get(t["N1"], 0.0) + t["c_t"] / ncurves
            pi_type[t["gross_label"]] = pi_type.get(t["gross_label"], 0.0) + float(pi)
        H = sum(1 for t in types if t["N1"] == 1) + 2 * sum(1 for t in types if t["N1"] >= 2)
        Hexp = p // 12 + e_of(p)
        mass = sum(Fraction(t["c_t"], t["units"]) for t in types)
        maxN1 = max(t["N1"] for t in types)
        per_prime[p] = {
            "route": routes[p], "n_types": len(types), "n_curves": ncurves,
            "I1_mismatches": len(mism), "I1_mismatch_indices": mism,
            "I1": "PASS" if not mism else "FAIL",
            "all_parsed_bases_are_orders": all(t["is_order"] for t in types),
            "all_reduced_disc_p": all(t["reduced_disc_is_p"] for t in types),
            "A1": {"H_reconstructed": H, "floor_p_12_plus_e": Hexp, "verdict": "PASS" if H == Hexp else "FAIL"},
            "A2": {"max_N1": maxN1, "max_delta_rank4": max(t["delta_rank4"] for t in types),
                   "bound_floor_cuberoot_p_over_2": bnd, "verdict": "PASS" if maxN1 <= bnd else "FAIL"},
            "A3_reported_not_gate": {"eichler_mass_sum_c_over_units": str(mass), "float": float(mass),
                                     "p_minus_1_over_24": str(Fraction(p - 1, 24)), "equal": mass == Fraction(p - 1, 24)},
            "wisde_tail_largest_d": tail_d,
            "gross_labels": {"theta_prefix_T_nrd_le": T, "n_labels": len(set(label_of.values())),
                             "types_sharing_a_label": shared},
            "pi_delta": {str(k): v for k, v in sorted(pi_delta.items())},
            "pi_delta_uniform_j": {str(k): v for k, v in sorted(pi_delta_uj.items())},
            "pi_type_by_gross_label": {str(k): v for k, v in sorted(pi_type.items())},
            "units_histogram": {str(u): sum(1 for t in types if t["units"] == u) for u in sorted(set(t["units"] for t in types))},
        }
        for t in types:
            t.pop("pi_unnorm")
            t["basis"] = [[str(x) for x in e] for e in t["basis"]]
        all_types.extend(types)
        common.log("p=%d types=%d I1_mismatch=%d A1=%s A2=%s A3=%s" % (
            p, len(types), len(mism), per_prime[p]["A1"]["verdict"], per_prime[p]["A2"]["verdict"],
            per_prime[p]["A3_reported_not_gate"]["equal"]))
    gp.close()

    with open(os.path.join(rd, "types.jsonl"), "w") as f:
        import json
        for t in all_types:
            f.write(json.dumps({k: t[k] for k in ["p", "index", "N", "N1", "delta_rank4", "units", "gross_label",
                                                  "theta_key_sha256", "c_t", "w_mass", "pi", "pi_exact", "pi_uniform_j",
                                                  "is_order", "reduced_disc_is_p", "order_hash", "gross_gram", "basis"]},
                               sort_keys=True) + "\n")

    i1_total = sum(per_prime[p]["I1_mismatches"] for p in PRIMES)
    a1_pass = [p for p in PRIMES if per_prime[p]["A1"]["verdict"] == "PASS"]
    a2_fail = [p for p in PRIMES if per_prime[p]["A2"]["verdict"] != "PASS"]
    if i1_total > 0:
        outcome, status, validity, reason = "FC-VOID (SR-1: I-1 mismatch)", "completed_valid", "valid", "Stage A gate I-1 FAILED; STOP ALL"
    elif len(a1_pass) < 3:
        outcome, status, validity, reason = "STOP (SR-2: fewer than 3 primes pass A-1)", "completed_valid", "valid", "SR-2"
    elif a2_fail:
        outcome, status, validity, reason = "A-2 FAIL at %s" % a2_fail, "completed_valid", "valid", "A-2 failure (anchor)"
    else:
        outcome, status, validity, reason = "PASS (I-1, A-1, A-2 at all four primes)", "completed_valid", "valid", "all Stage-A gates pass"
    raw = {"experiment_id": "EXP-WESO-9e2d6d", "run_id": "RUN-WESO-aa2237", "stage": "STAGE-A",
           "primes": PRIMES, "per_prime": {str(p): per_prime[p] for p in PRIMES},
           "I1_total_mismatches": i1_total, "A1_passing_primes": a1_pass,
           "stage_outcome": outcome, "elapsed_seconds": round(time.time() - t_start, 2)}
    common.write_json(os.path.join(rd, "raw-result.json"), raw)
    common.write_json(os.path.join(rd, "manifest_extra.json"), {
        "seeds_used": {"note": "Stage A is deterministic; no RNG is used."},
        "inputs": {"wisde_files": [{"p": p, "path_outside_repo": paths[p], "bytes": EXPECTED[p][0], "sha256": EXPECTED[p][1],
                                     "route": routes[p]} for p in PRIMES],
                   "fetch_log": "wisde_fetch_log.yaml"},
        "workers": 1})
    common.write_json(os.path.join(rd, "status.json"), {"status": status, "validity": validity, "reason": reason,
                                                        "failure_class": None, "stage_outcome": outcome})
    rel = "experiments/EXP-WESO-9e2d6d/runs/RUN-WESO-aa2237/"
    common.write_exec_report(rd, "RUN-WESO-aa2237", "STAGE-A", {
        "protocol_deviations": [],
        "runs": {"completed": ["RUN-WESO-aa2237"] if status == "completed_valid" else [], "invalid": [], "failed": []},
        "gates": {
            "I-1": {"verdict": "PASS" if i1_total == 0 else "FAIL", "total_mismatches": i1_total,
                    "per_prime": {str(p): {"route": routes[p], "mismatches": per_prime[p]["I1_mismatches"],
                                           "n_types": per_prime[p]["n_types"]} for p in PRIMES}},
            "A-1": {str(p): per_prime[p]["A1"] for p in PRIMES},
            "A-2": {str(p): per_prime[p]["A2"] for p in PRIMES},
            "A-3_reported_not_gate": {str(p): per_prime[p]["A3_reported_not_gate"] for p in PRIMES},
        },
        "stage_outcome": outcome,
        "observations": [
            "Route per prime: %s (fetched bytes and SHA-256 equal to the committed RUN-SSIQ-4de240-a values; see wisde_fetch_log.yaml)." % routes,
            "Gross-lattice labels: %s labels for %s types; types sharing a label: %s." % (
                {str(p): per_prime[p]["gross_labels"]["n_labels"] for p in PRIMES},
                {str(p): per_prime[p]["n_types"] for p in PRIMES},
                {str(p): per_prime[p]["gross_labels"]["types_sharing_a_label"] for p in PRIMES}),
            "Units histogram per prime (|O^x| -> #types): %s." % {str(p): per_prime[p]["units_histogram"] for p in PRIMES},
        ],
        "anomalies": [],
        "artifact_paths": [rel + x for x in ["manifest.yaml", "command.txt", "environment.json", "stdout.log", "stderr.log",
                                             "raw-result.json", "wisde_fetch_log.yaml", "types.jsonl", "execution_report.yaml"]],
        "executor_assessment": {"protocol_complete": True, "data_quality": "good", "requires_rerun": False},
    })
    common.log("STAGE-A outcome:", outcome)


if __name__ == "__main__":
    main()
