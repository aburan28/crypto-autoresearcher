# EXP-DREG-004 cost probe (READ-ONLY; does not modify checkpoint or instrument).
# Quantifies per-invocation overhead components for the carrier-codec assessment:
#   (a) carry sha256 verify time, (b) carry unpickle time (sage m4ri PNG pickle),
#   (c) pickle re-dump time (save side), (d) raw-bit sizes vs pickle sizes,
#   (e) adjacency cache load time, (f) sage/python startup constant.
import json, os, pickle, hashlib, time, sys

SD = "runs/RUN-DREG-004-MEASURE-N21-SEM-A/work/h012c_measure_n21_sem_a_sem_n21_t0"
ADJ = "runs/RUN-DREG-004-MEASURE-N21-SEM-A/work/h012c_adj_sem_n21_t3_i0_D5_s2026_0da7ff6aa40007e8.pkl"

st = json.load(open(SD + "/state.json"))
carries = st["carries"]
n = len(carries)

def file_hash(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()

# (a)+(b) load path, exactly like load_carries but timed per stage
t_hash = t_load = 0.0
blocks = []
raw_bits = 0
pkl_bytes = 0
for c in carries:
    p = os.path.join(SD, c["file"])
    pkl_bytes += os.path.getsize(p)
    t0 = time.time(); file_hash(p); t_hash += time.time() - t0
    t0 = time.time()
    with open(p, "rb") as f:
        P, H = pickle.load(f)
    t_load += time.time() - t0
    blocks.append((P, H))
    nr, k = H.dimensions()
    raw_bits += (nr * k) / 8.0

# (c) save side: pickle.dumps on a 3-block sample, scaled (full pass too slow for the cap)
t_dump = 0.0
sample = blocks[:3]
for P, H in sample:
    t0 = time.time(); pickle.dumps((P, H), protocol=4); t_dump += time.time() - t0
t_dump_per_block_sample = t_dump / len(sample)
t_dump = t_dump_per_block_sample * len(blocks)

# (e) adjacency load
t0 = time.time()
with open(ADJ, "rb") as f:
    adj = pickle.load(f)
t_adj = time.time() - t0

out = {
    "n_carry_blocks": n,
    "carry_pickle_bytes": pkl_bytes,
    "carry_raw_bit_bytes": int(raw_bits),
    "pickle_overhead_ratio": round(pkl_bytes / raw_bits, 2),
    "t_sha256_verify_s": round(t_hash, 1),
    "t_unpickle_s": round(t_load, 1),
    "t_unpickle_per_block_s": round(t_load / n, 2),
    "t_pickle_dump_s": round(t_dump, 1),
    "t_dump_per_block_s": round(t_dump / n, 2), "dump_side": "3-block sample scaled",
    "t_adjacency_load_s": round(t_adj, 1),
    "raw_bit_load_estimate_s": round(raw_bits / 1.5e9, 1),
    "rank_acc": st["rank_acc"], "next_col": st["next_col"],
}
print(json.dumps(out, indent=1))
