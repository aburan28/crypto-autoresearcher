"""Own M_4 / literal W_4 cross-checks (TASK-20260926-c58e87; RT-7: at most 10 archived or O4
systems in total). Own code only (rtlib.own_M4_record, rtlib.own_W4); compares with the engine
record (O4: o4-engine-records.json; archived: RUN-CERTBIN-6ebb0e closures.jsonl.gz).
Systems (7): O4 N-CONV-VR:0:unsat, O4 N-CONV-VR:0:sat, O4 S3-VR:3 (unsat descent);
archived N-CONV:0:unsat, the first archived N-CONV unsat with fallen 987, archived
N-CONV17:83:unsat, the first archived N-CONVL unsat that M_4 does not refute.
Usage: python3 own_crosscheck.py <worktree> <j10-ptm dir>
"""
import gzip
import json
import sys
import time

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import rtlib as R  # noqa: E402

wt, d = sys.argv[1], sys.argv[2]
run = f"{wt}/experiments/EXP-CERTBIN-ddfe75/runs/RUN-CERTBIN-6ebb0e"
CL = {}
for l in gzip.open(f"{run}/closures.jsonl.gz", "rt"):
    r = json.loads(l)
    CL.setdefault(r["key"], {})[r["closure"]] = r
INS = {json.loads(l)["key"]: json.loads(l) for l in gzip.open(f"{run}/instances.jsonl.gz", "rt")}
O4S = json.load(open(f"{d}/o4-systems.json"))
O4E = {r["key"]: r for r in json.load(open(f"{d}/o4-engine-records.json"))["records"]}
o4hex = {k["key"]: k["E_hex"] for k in O4S["kept"] if "E_hex" in k}
o4hex.update({f"S3-VR:{dd['slot']}": dd["E_hex"] for dd in O4S["descents"]})

f987 = next(k for k, v in CL.items() if INS[k]["arm"] == "N-CONV" and INS[k]["role"] == "unsat" and v["M_4"]["fallen"] == 987)
cl_nm4 = next(k for k, v in sorted(CL.items(), key=lambda kv: INS[kv[0]]["slot"] if INS[kv[0]]["slot"] is not None else 999)
              if INS[k]["arm"] == "N-CONVL" and INS[k]["role"] == "unsat" and not v["M_4"]["one"])
plan = [("O4", "N-CONV-VR:0:unsat", True), ("O4", "N-CONV-VR:0:sat", True), ("O4", "S3-VR:3", True),
        ("RUN", "N-CONV:0:unsat", False), ("RUN", f987, False), ("RUN", "N-CONV17:83:unsat", True),
        ("RUN", cl_nm4, True)]
out = []
for src, key, want_w in plan:
    E = R.hex_to_E(o4hex[key] if src == "O4" else INS[key]["E_hex"])
    t0 = time.time()
    m4 = R.own_M4_record(E)
    rec = {"source": src, "key": key, "own_M4": m4, "own_M4_seconds": round(time.time() - t0, 1)}
    eng_m4 = O4E[key]["M4"] if src == "O4" else CL[key]["M_4"]
    eng_w4 = O4E[key]["W4"] if src == "O4" else CL[key]["W_4"]
    rec["engine_M4"] = {k: eng_m4[k] for k in ("rank", "one", "dims_by_deg")}
    rec["M4_agree"] = all(m4[k] == eng_m4[k] for k in ("rank", "one", "dims_by_deg"))
    if want_w:
        t1 = time.time()
        w4 = R.own_W4(E)
        rec["own_W4"] = w4
        rec["own_W4_seconds"] = round(time.time() - t1, 1)
        rec["engine_W4"] = {k: eng_w4[k] for k in ("dims", "final_dim", "one", "one_first_iteration", "dims_by_deg", "iterations_to_fixpoint")}
        rec["W4_agree"] = all(w4[k] == eng_w4[k] for k in ("dims", "final_dim", "one", "one_first_iteration", "dims_by_deg", "iterations_to_fixpoint"))
    out.append(rec)
    print(json.dumps(rec), flush=True)
json.dump(out, open(f"{d}/own-crosscheck.json", "w"), indent=1)
