#!/usr/bin/env python3
"""TASK-20260926-59169c CP-3: check EVERY J7 wdag-v1 certificate with the own
checker checks/wdag_check.py (written before any re-deriver code was read).

f_k sources:
  pool BS-xxx         -> blind-inputs.json equations (the plan's extraction);
  NCONV-REPLAY:s:role -> (A) J7's own kept rows in stream-replay.jsonl.gz and
                         (B) the run's instances.jsonl.gz E_hex for N-CONV:s:role
                         (used only where the replayed rows equal the run's).
Also, as a cross-check on the pool mapping, each pool certificate is checked
against the run's instances.jsonl.gz rows of the mapped run key.
Standard library only (plus the own checker).
"""
import argparse, gzip, json, os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wdag_check as W  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--snap", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    rev = os.path.join(a.snap, "coordination/review/certbin-20260926-089841")
    j7 = os.path.join(rev, "reviews/TASK-20260926-83cebf")
    run = os.path.join(a.snap, "experiments/EXP-CERTBIN-ddfe75/runs/RUN-CERTBIN-6ebb0e")
    blind = json.load(open(os.path.join(rev, "blind/blind-inputs.json")))
    key = json.load(open(os.path.join(rev, "blind-inputs-key.json")))
    pool = {s["label"]: W.system_from_monomial_lists(s["equations"]) for s in blind["systems"]}
    inst = {}
    for line in gzip.open(os.path.join(run, "instances.jsonl.gz"), "rt"):
        r = json.loads(line)
        inst[r["key"]] = r
    replay_rows = {}
    for line in gzip.open(os.path.join(j7, "stream-replay.jsonl.gz"), "rt"):
        r = json.loads(line)
        if r["arm"] == "N-CONV" and r["outcome"] in ("kept_unsat", "kept_sat"):
            role = "unsat" if r["outcome"] == "kept_unsat" else "sat"
            replay_rows["NCONV-REPLAY:%d:%s" % (r["slot"], role)] = r["row_hex"]
    results = []
    t0 = time.time()
    for line in gzip.open(os.path.join(j7, "wcerts.jsonl.gz"), "rt"):
        c = json.loads(line)
        lab = c["label_or_replay_key"]
        rec = {"j7_label": lab}
        if lab.startswith("NCONV-REPLAY:"):
            _, slot, role = lab.split(":")
            rk = "N-CONV:%s:%s" % (slot, role)
            rec["run_key"] = rk
            FA = W.system_from_hex(replay_rows[lab])
            st, det = W.check_wdag(c, FA)
            rec["status_on_j7_rows"] = st
            rec["detail_on_j7_rows"] = det
            FB_rows = inst[rk]["E_hex"]
            same = [int(x, 16) for x in FB_rows] == [int(x, 16) for x in replay_rows[lab]]
            rec["replay_rows_equal_run_rows"] = same
            if same:
                FB = W.system_from_hex(FB_rows)
                st2, det2 = W.check_wdag(c, FB)
                rec["status_on_run_rows"] = st2
                if st2 != "valid":
                    rec["detail_on_run_rows"] = det2
            else:
                rec["status_on_run_rows"] = "not_checked_rows_differ"
            rec["status"] = st
        else:
            rk = key[lab]["key"]
            rec["run_key"] = rk
            st, det = W.check_wdag(c, pool[lab])
            rec["status"] = st
            rec["detail"] = det
            FB = W.system_from_hex(inst[rk]["E_hex"])
            rec["pool_equations_equal_run_rows"] = W.system_to_colbits(pool[lab]) == [int(x, 16) for x in inst[rk]["E_hex"]]
            st2, det2 = W.check_wdag(c, FB)
            rec["status_on_run_rows"] = st2
        results.append(rec)
    labels_with_cert = {r["j7_label"] for r in results}
    summary = {
        "certificates_checked": len(results),
        "valid": sum(r["status"] == "valid" for r in results),
        "invalid": [r for r in results if r["status"] != "valid"],
        "replay_certs": sum(r["j7_label"].startswith("NCONV") for r in results),
        "pool_certs": sum(not r["j7_label"].startswith("NCONV") for r in results),
        "replay_valid_on_run_rows": sum(r.get("status_on_run_rows") == "valid" for r in results if r["j7_label"].startswith("NCONV")),
        "pool_valid_on_run_rows": sum(r.get("status_on_run_rows") == "valid" for r in results if not r["j7_label"].startswith("NCONV")),
        "pool_equations_equal_run_rows_all": all(r.get("pool_equations_equal_run_rows", True) for r in results),
        "pool_labels_without_cert": sorted(set(key) - labels_with_cert),
        "seconds": round(time.time() - t0, 1),
    }
    json.dump({"summary": summary, "per_certificate": results}, open(a.out, "w"), indent=1)
    print(json.dumps(summary, indent=1)[:3000])


if __name__ == "__main__":
    main()
