# EXP-GPS-001 RUN-b — GPS-1 stage 1: exact n=21 D5 sem column set, composition
# segmentation, a9-law check, P2 static table (forensics; no new rank matrices).
#
# Column presence law used (PROVEN exact at top degree, see analysis.md):
#   deg-5 monomial m is a column iff exists equation i and top-slice m' in f_i
#   (|m'| = deg_i) with m' subseteq m. (Each pair (i,m') yields a distinct row
#   (i, mu=m\m'), so no GF(2) parity cancellation is possible at degree D.)
#   deg<=4: up-closure count == C(42,<=4) proves every low monomial present
#   (exact set is always a subset of the up-closure).
#
# Usage: sage experiments/EXP-GPS-001/src/gps1_cols.sage --out <raw.json> --work <dir>
import sys, os, time, json, argparse, platform, datetime, itertools, hashlib
import pickle
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('--out', required=True)
p.add_argument('--work', required=True)
args = p.parse_args()

EXPDIR = Path('/Volumes/Volume/crypto-autoresearcher/experiments/EXP-SIG-007')
sys.path.insert(0, str(EXPDIR / 'src'))
import sage.version
load(str(EXPDIR / 'src' / 'h013_f5_signatures.sage'))

t_start = time.time()
def sha256(pth):
    return hashlib.sha256(Path(pth).read_bytes()).hexdigest()
PINNED = {
    "h013_f5_signatures.sage": "1ba96fe477c9dc2e7c551c96353c8361d21e40134551342636b2f13015c09087",
    "semaev_tree.py": "e9f1681b4e422f7a67176fffd3e5f91ab7a95c9fddc1eb925c2bb0a93a9becef",
    "ic_first_fall_fast.py": "f1c98bd8642df226760f43038d6687e73794d04b9c7a9073f244b8a0433fad61",
    "macaulay_export.py": "c00b8aad9ad47f8a3f09c39f6b65062a37562703bfd1c4f6159b1e54b1dbad97",
}
ih = {f.name: sha256(f) for f in sorted((EXPDIR / 'src').iterdir()) if f.name in PINNED}
out = {
    "experiment": "EXP-GPS-001", "run": "RUN-EXP-GPS-001-b", "phase": "gps1_columns",
    "args": vars(args),
    "environment": {"sage_version": str(sage.version.version),
                    "python_version": sys.version.split()[0],
                    "os": platform.platform(), "machine": platform.machine()},
    "instrument_sha256": ih,
    "instrument_sha256_matches_pinned": all(ih.get(k) == v for k, v in PINNED.items()),
    "started_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
}
def flush():
    out["elapsed_s_so_far"] = round(time.time() - t_start, 2)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    json.dump(jsonsafe(out), open(args.out, "w"), indent=1)
def log(m):
    print("[gps1b %.1f] %s" % (time.time() - t_start, m), flush=True)

N, T, SEED, D = 21, 3, 1, 5
K = (N + T - 1) // T          # 7
NB = N + T * K                # 42
BLOCKS = [(0, N), (N, N + K), (N + K, N + 2 * K), (N + 2 * K, N + 3 * K)]
def block_of(v):
    if v < N: return 0
    return 1 + (v - N) // K
def comp_of_int(m):
    c = [0, 0, 0, 0]
    mm = m
    while mm:
        low = mm & (-mm)
        c[block_of(low.bit_length() - 1)] += 1
        mm ^^= low
    return tuple(c)

log("build_boolean_semaev(21,3,1) ...")
monosets, nb, meta = build_boolean_semaev(N, T, SEED)
assert int(nb) == NB, (nb, NB)
eq_degs = [max(mono_deg(x) for x in f) for f in monosets]
out["meta"] = meta
out["eq_degs"] = sorted(eq_degs)
out["n_eqs"] = len(monosets)
out["monosets_sha256"] = hashlib.sha256(
    repr(sorted(tuple(sorted(tuple(sorted(m)) for m in f)) for f in monosets)).encode()).hexdigest()
log("built: %d eqs, degs %s (%.1fs)" % (len(monosets), out["eq_degs"], time.time() - t_start))
flush()

# ---- exact quintic presence via top-slice containment
log("marking up-closures (int bitmasks) ...")
present5 = set()           # deg-5 present (exact)
covered_le4 = set()        # deg<=4 covered (up-closure; will prove == all)
tops = []                  # (m'_int, deg_i) top-slice monomials
for i, f in enumerate(monosets):
    di = eq_degs[i]
    slack = D - di
    for mp in f:
        dmp = len(mp)
        mi = 0
        for v in mp:
            mi |= 1 << v
        if dmp == di:
            tops.append((mi, di))
        # supersets of mp up to size D with size-mp <= slack
        rest = [v for v in range(NB) if not (mi >> v) & 1]
        for extra in range(0, min(slack, D - dmp) + 1):
            tgt = dmp + extra
            for combo in itertools.combinations(rest, extra):
                mm = mi
                for v in combo:
                    mm |= 1 << v
                if tgt == D:
                    if dmp == di:
                        present5.add(mm)
                else:
                    covered_le4.add(mm)
        del rest
log("tops=%d present5=%d covered_le4=%d (%.1fs)" %
    (len(tops), len(present5), len(covered_le4), time.time() - t_start))
flush()

from math import comb
FULL_LE4 = sum(comb(NB, d) for d in range(0, D))          # 124,314
FULL_5 = comb(NB, D)                                       # 850,668
miss_le4 = []
full_le4_set = set()
for d in range(0, D):
    for combo in itertools.combinations(range(NB), d):
        mm = 0
        for v in combo:
            mm |= 1 << v
        full_le4_set.add(mm)
        if mm not in covered_le4:
            miss_le4.append(mm)
miss_le4_hist = {}
for mm in miss_le4:
    k = (bin(mm).count('1'), comp_of_int(mm))
    miss_le4_hist[k] = miss_le4_hist.get(k, 0) + 1
out["counts"] = {
    "full_le4": FULL_LE4, "covered_le4": len(covered_le4),
    "le4_all_present": len(covered_le4) == FULL_LE4,
    "missing_le4": len(miss_le4),
    "full_deg5": FULL_5, "present_deg5": len(present5),
    "missing_deg5": FULL_5 - len(present5),
    "ncols_computed": len(covered_le4) + len(present5),
    "ncols_receipt": 778394,
    "ncols_match": (len(covered_le4) + len(present5)) == 778394,
    "shell_start": len(covered_le4),
    "NOTE": ("exact column set is always a SUBSET of the up-closure (parity can "
             "only remove); up-closure total == receipt 778,394 therefore proves "
             "up-closure == exact everywhere AND fixes the true quintic shell "
             "start at covered_le4 (=124,244), correcting the IDEAS estimate "
             "124,314 (654,080) by 70 columns"),
}
out["missing_le4_by_deg_comp"] = {str(k): v for k, v in
                                  sorted(miss_le4_hist.items())}
assert out["counts"]["ncols_match"]
log("ncols == 778,394 EXACT MATCH; missing deg5 = %d; missing le4 = %d"
    % (out["counts"]["missing_deg5"], len(miss_le4)))
SHELL_START = out["counts"]["shell_start"]

# missing-set composition histogram (a9 balanced-composition check)
miss_hist = {}
tops_by_deg = {}
for mi, di in tops:
    tops_by_deg.setdefault(di, set()).add(mi)
for combo in itertools.combinations(range(NB), D):
    mm = 0
    for v in combo:
        mm |= 1 << v
    if mm not in present5:
        miss_hist[comp_of_int(mm)] = miss_hist.get(comp_of_int(mm), 0) + 1
out["missing_deg5_by_comp"] = {str(k): v for k, v in
                               sorted(miss_hist.items(), key=lambda kv: -kv[1])}
log("missing classes: %d; top: %s" % (len(miss_hist), list(out["missing_deg5_by_comp"].items())[:6]))
flush()

# ---- ordered shell: present quintics in (degrevlex-by-tuple) order == colidx order
log("ordering %d quintic columns ..." % len(present5))
shell = sorted(present5, key=lambda m: tuple(sorted(
    (v for v in range(NB) if (m >> v) & 1))))
comps = [comp_of_int(m) for m in shell]
class_ids = {}
cid = []
for c in comps:
    if c not in class_ids:
        class_ids[c] = len(class_ids)
    cid.append(class_ids[c])
import array
with open(Path(args.work) / 'shell_order.pkl', 'wb') as f:
    pickle.dump({'shell': array.array('Q', shell),
                 'cid': array.array('B', cid),
                 'class_ids': {str(k): v for k, v in class_ids.items()},
                 'shell_start': SHELL_START}, f, protocol=4)
log("shell_order.pkl saved (%.1fs)" % (time.time() - t_start))

# ---- class runs segmentation
runs = []
st_ = 0
for j in range(1, len(cid) + 1):
    if j == len(cid) or cid[j] != cid[st_]:
        runs.append((st_ + SHELL_START, j + SHELL_START, comps[st_]))
        st_ = j
runs_out = [(a, b, str(c)) for (a, b, c) in runs]
out["n_class_runs"] = len(runs_out)
out["n_classes"] = len(class_ids)
# class sizes
csz = {}
for c in comps:
    csz[c] = csz.get(c, 0) + 1
out["class_sizes"] = {str(k): v for k, v in sorted(csz.items(), key=lambda kv: -kv[1])}

# ---- alignment of plateau/burst with class boundaries
def classify_range(a, b):
    """classes intersecting column range [a,b) (shell coords absolute)."""
    lo, hi = a - SHELL_START, b - SHELL_START
    touched = {}
    for (r0, r1, c) in runs:
        if r1 <= lo + SHELL_START or r0 >= hi + SHELL_START:
            continue
        x0, x1 = max(r0, lo + SHELL_START), min(r1, hi + SHELL_START)
        touched[str(c)] = touched.get(str(c), 0) + (x1 - x0)
    return touched
PLATEAU = (364000, 449000)
BURST = (449000, 454000)
TAIL = (454000, 778394)
# boundary alignment: does 364000/449000/454000 coincide with run starts/ends?
bounds = {364000, 449000, 454000, SHELL_START, 778394}
edges = set()
for (r0, r1, c) in runs:
    edges.add(r0 + SHELL_START); edges.add(r1 + SHELL_START)
out["boundary_alignment"] = {str(b): (b in edges) for b in sorted(bounds)}
out["plateau_classes"] = classify_range(*PLATEAU)
out["burst_unit_classes"] = classify_range(*BURST)
out["tail_classes_n"] = len(classify_range(*TAIL))
log("plateau classes: %s" % out["plateau_classes"])
log("burst unit classes: %s" % out["burst_unit_classes"])
log("boundary alignment: %s" % out["boundary_alignment"])
flush()

# ---- order validation vs adjacency row-counts (sample of quintic columns)
log("adjacency system_hash + row-count validation (500 columns) ...")
import pickle as _pk, random as _rd
with open(EXPDIR / 'work/n21_s1/s1_adjacency.pkl', 'rb') as f:
    adj = _pk.load(f)
col_rows = adj['col_rows']
assert adj['ncols'] == 778394 and len(col_rows) == 778394 and adj['nrows'] == 279048
def monosets_hash(monosets_):
    h = hashlib.sha256()
    for f in monosets_:
        encoded = sorted(tuple(sorted(int(v) for v in m)) for m in f)
        h.update(len(encoded).to_bytes(8, "big"))
        for mono in encoded:
            h.update(len(mono).to_bytes(4, "big"))
            for v in mono:
                h.update(v.to_bytes(4, "big"))
    return h.hexdigest()
mh = monosets_hash(monosets)
out["system_hash_rebuilt"] = mh
out["system_hash_adjacency"] = adj['system_hash']
out["system_hash_match"] = (mh == adj['system_hash'])
log("system_hash match: %s" % out["system_hash_match"])
assert out["system_hash_match"]
tops_l = [(mi, di) for mi, di in tops]
def rowcount_pred(m):
    cnt = 0
    for mi, di in tops_l:
        if mi & m == mi:
            cnt += 1
    return cnt
rng = _rd.Random(int(7))
idxs = sorted(rng.sample(range(len(shell)), 500))
mismatch = 0
for j in idxs:
    if rowcount_pred(shell[j]) != len(col_rows[SHELL_START + j]):
        mismatch += 1
out["rowcount_validation"] = {"sampled": 500, "mismatches": mismatch}
log("rowcount mismatches: %d/500" % mismatch)
assert mismatch == 0
out["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
out["wall_seconds"] = round(time.time() - t_start, 2)
flush()
log("DONE")
