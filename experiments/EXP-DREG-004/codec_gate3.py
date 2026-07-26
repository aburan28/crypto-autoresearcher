# Codec gate round 3: compile + verify + time the raw-bit Cython codec.
import json, os, pickle, hashlib, time, sys
sys.path.insert(0, "/Volumes/Volume/crypto-autoresearcher/src")
from sage.all import GF, matrix, random_matrix

F2 = GF(2)
WD = "runs/RUN-DREG-004-REBUILD-A/work/h012c_rebuild_a_sem_n21_t0"
out = {}

import importlib.util
spec = importlib.util.spec_from_file_location(
    "rawcarrier", "/Volumes/Volume/crypto-autoresearcher/experiments/EXP-DREG-004/rawcarrier_ext.so")
raw = importlib.util.module_from_spec(spec)
t0 = time.time(); spec.loader.exec_module(raw)
out["load_ext_s"] = round(time.time() - t0, 1)
print("ext loaded", flush=True)

with open(os.path.join(WD, "carry_000_000.pkl"), "rb") as f:
    P, H = pickle.load(f)
nr, k = H.dimensions()

tests = [("k2000_real", H)]
t0 = time.time(); Hbig = random_matrix(F2, 279048, 6808); out["synth_gen_s"] = round(time.time() - t0, 1)
tests.append(("k6808_synth", Hbig))

for name, M in tests:
    nr, k = M.dimensions()
    d = {"nr": nr, "k": k}
    t0 = time.time(); blob = raw.dump_raw(M, nr, k); d["raw_dump_s"] = round(time.time() - t0, 3)
    d["raw_bytes"] = len(blob)
    t0 = time.time()
    M2 = matrix(F2, nr, k)
    raw.load_raw(blob, M2, nr, k)
    d["raw_load_s"] = round(time.time() - t0, 3)
    d["bit_exact"] = bool(M2 == M)
    t0 = time.time(); pblob = pickle.dumps(M, protocol=4); d["pickle_dump_s"] = round(time.time() - t0, 2)
    t0 = time.time(); pickle.loads(pblob); d["pickle_load_s"] = round(time.time() - t0, 2)
    d["pickle_bytes"] = len(pblob)
    out[name] = d
    print(name, json.dumps(d), flush=True)

# projection to the destroyed 45-file npiv distribution (from rescued state)
st = json.load(open("STATE-RESCUE.json"))
npivs = [c["npiv"] for c in st["carries"]]
if out.get("k6808_synth", {}).get("bit_exact"):
    per6808_load = out["k6808_synth"]["raw_load_s"]
    per6808_dump = out["k6808_synth"]["raw_dump_s"]
    proj_load = sum(per6808_load * (x / 6808.0) for x in npivs)
    proj_dump = sum(per6808_dump * (x / 6808.0) for x in npivs)
    out["projection_45files"] = {
        "raw_load_total_s": round(proj_load, 1),
        "raw_dump_total_s": round(proj_dump, 1),
        "pickle_load_measured_total_s": 198.6,
        "gate_b_margin_s": round(198.6 - proj_load, 1),
        "raw_bytes_total": sum((6808 + 63) // 64 * 8 * 0 for _ in []) or None,
    }
print(json.dumps(out.get("projection_45files", {}), indent=1))
json.dump(out, open("codec_gate3.json", "w"), indent=1)
print("GATE DATA SAVED")
