# EXP-GPS-001 RUN-c — GPS-1 P1: exact identity of the 947 burst pivot columns.
# Re-reduces burst unit cols [449000,454000) against carries 0..74 (streaming,
# sha256-verified, same order as the pinned staircase) and takes the
# left-to-right column rank profile of the reduced chunk. Profile size must
# equal 947 (state.json unit 92 k). Pivot columns are then classified by block
# composition via work/shell_order.pkl (RUN-b).
#
# Usage: sage experiments/EXP-GPS-001/src/gps1_burst.sage --out <raw.json> --work <dir>
import sys, os, time, json, argparse, platform, datetime, hashlib, pickle, gc
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('--out', required=True)
p.add_argument('--work', required=True)
args = p.parse_args()

EXPDIR = Path('/Volumes/Volume/crypto-autoresearcher/experiments/EXP-SIG-007')
sys.path.insert(0, str(EXPDIR / 'src'))
import sage.version
load(str(EXPDIR / 'src' / 'h013_f5_signatures.sage'))
from sage.all import GF, matrix
F2 = GF(2)

t_start = time.time()
def file_hash(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()
out = {"experiment": "EXP-GPS-001", "run": "RUN-EXP-GPS-001-c", "phase": "gps1_burst_profile",
       "args": vars(args),
       "environment": {"sage_version": str(sage.version.version),
                       "python_version": sys.version.split()[0],
                       "os": platform.platform(), "machine": platform.machine()},
       "started_at": datetime.datetime.now(datetime.timezone.utc).isoformat()}
def flush():
    out["elapsed_s_so_far"] = round(time.time() - t_start, 2)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    json.dump(jsonsafe(out), open(args.out, "w"), indent=1)
def log(m):
    print("[gps1c %.1f] %s" % (time.time() - t_start, m), flush=True)

R5 = EXPDIR / 'work/n21_s1/rank5'
st = json.load(open(R5 / 'state.json'))
nrows, ncols = st['nrows'], st['ncols']
J0, J1 = 449000, 454000
assert st['units'][92]['j0'] == J0 and st['units'][92]['j1'] == J1 and st['units'][92]['k'] == 947

# burst-unit carries are entries 0..74 (carry_075 is the burst's own output)
carries_meta = st['carries'][:75]
assert len(carries_meta) == 75 and sum(c['npiv'] for c in carries_meta) == 265003

log("loading adjacency ...")
with open(EXPDIR / 'work/n21_s1/s1_adjacency.pkl', 'rb') as f:
    adj = pickle.load(f)
col_rows = adj['col_rows']
assert adj['ncols'] == ncols and len(col_rows) == ncols and adj['nrows'] == nrows

c = J1 - J0
CK = Path(args.work) / 'burst_ckpt'
CK.mkdir(parents=True, exist_ok=True)
ck_start = -1
if (CK / 'B.pkl').exists():
    meta_ck = json.load(open(CK / 'meta.json'))
    ck_start = meta_ck['next_carry']
    log("resuming: loading B checkpoint after carry %d ..." % (ck_start - 1))
    with open(CK / 'B.pkl', 'rb') as f:
        B = pickle.load(f)
else:
    log("filling B (%d x %d) ..." % (nrows, c))
    t0 = time.time()
    B = matrix(F2, nrows, c)
    for jj in range(c):
        for r in col_rows[J0 + jj]:
            B[r, jj] = 1
    out["tm_fill"] = round(time.time() - t0, 2)
    ck_start = 0
    log("fill done (%.1fs)" % out["tm_fill"])
flush()

t0 = time.time()
for ci in range(ck_start, len(carries_meta)):
    cm = carries_meta[ci]
    pth = R5 / cm['file']
    with open(pth, 'rb') as f:
        P, H = pickle.load(f)
    Y = B.matrix_from_rows(list(P))
    B += H * Y
    del P, H, Y
    gc.collect()
    if (ci + 1) % 5 == 0 or ci == len(carries_meta) - 1:
        with open(CK / 'B.pkl.tmp', 'wb') as f:
            pickle.dump(B, f, protocol=4)
        os.replace(CK / 'B.pkl.tmp', CK / 'B.pkl')
        json.dump({'next_carry': int(ci + 1)}, open(CK / 'meta.json', 'w'))
        log("checkpoint after carry %d (%.1fs)" % (ci, time.time() - t0))
        flush()
    if time.time() - t_start > 200:
        with open(CK / 'B.pkl.tmp', 'wb') as f:
            pickle.dump(B, f, protocol=4)
        os.replace(CK / 'B.pkl.tmp', CK / 'B.pkl')
        json.dump({'next_carry': int(ci + 1)}, open(CK / 'meta.json', 'w'))
        out["halt"] = "softcap: checkpointed after carry %d; resume by rerunning" % ci
        out["wall_seconds"] = round(time.time() - t_start, 2)
        flush()
        print("HALT softcap after carry %d" % ci, flush=True)
        sys.exit(2)
out["tm_reduce"] = round(time.time() - t0, 2)
log("reduce vs 75 carries done (%.1fs)" % out["tm_reduce"])
flush()

t0 = time.time()
B.echelonize()   # row ops only -> pivot columns = left-to-right profile
prof = list(B.pivots())
out["tm_ech"] = round(time.time() - t0, 2)
out["profile_size"] = len(prof)
out["profile_matches_state_k947"] = (len(prof) == 947)
log("profile size = %d (expect 947)" % len(prof))
assert len(prof) == 947
pivot_cols = [int(J0 + j) for j in prof]
out["pivot_cols_min"] = min(pivot_cols)
out["pivot_cols_max"] = max(pivot_cols)

# classify
with open(Path(args.work) / 'shell_order.pkl', 'rb') as f:
    sh = pickle.load(f)
shell, cid = sh['shell'], sh['cid']
SHELL_START = sh['shell_start']
class_ids = {v: k for k, v in sh['class_ids'].items()}
burst_hist = {}
burst_pivot_rows = []
for jc in pivot_cols:
    cls = class_ids[cid[jc - SHELL_START]]
    burst_hist[cls] = burst_hist.get(cls, 0) + 1
out["burst_pivot_comp_hist"] = dict(sorted(burst_hist.items(), key=lambda kv: -kv[1]))
out["burst_pivot_n_classes"] = len(burst_hist)
top = sorted(burst_hist.items(), key=lambda kv: -kv[1])
out["P1_top_class_share"] = top[0][1]
out["P1_all_in_le2"] = len(burst_hist) <= 2
out["P1_ge800_in_one"] = top[0][1] >= 800
# also whole-unit class hist for context
unit_hist = {}
for j in range(J0 - SHELL_START, J1 - SHELL_START):
    cls = class_ids[cid[j]]
    unit_hist[cls] = unit_hist.get(cls, 0) + 1
out["burst_unit_comp_hist"] = dict(sorted(unit_hist.items(), key=lambda kv: -kv[1]))
with open(Path(args.work) / 'burst_pivot_cols.json', 'w') as f:
    json.dump({'pivot_cols': pivot_cols}, f)
out["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
out["wall_seconds"] = round(time.time() - t_start, 2)
flush()
log("DONE hist=%s" % out["burst_pivot_comp_hist"])
