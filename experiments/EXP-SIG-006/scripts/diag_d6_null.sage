# EXP-SIG-006 Phase A — diagnosis of the D6 null failure (EV-SIG-005 C5).
#
# Machine-checks, at n=9 seed=1 (the RUN-h/RUN-k anchor instance):
#   A1. ncols reproduction at D3..D6 for both arms (C1 anchor vs receipts).
#   A2. Column-set formation law: cols(D) vs the up-closure-with-slack of the
#       equation supports; exact parity (cancellation) deviations; the
#       missing-set's (degree, block-composition) histograms.
#   A3. Variety ground truth: |V_sem|, |V_null_old| via full 2^18 enumeration.
#   A4. sr_pred semantics: the pinned in-place loop == formal series
#       (1+z)^nb / PROD (1+z^{d_i}) [truncated-positive]; textbook Bardet
#       series for contrast; freeze degree (first non-positive coeff) per n.
#   A5. Fall arithmetic at D6 from column degrees + receipt ranks.
#
# Usage: sage experiments/EXP-SIG-006/scripts/diag_d6_null.sage --out <raw.json>

import sys, os, time, json, argparse, platform, datetime, itertools, hashlib
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('--out', required=True)
args = p.parse_args()

EXPDIR = Path(args.out).resolve().parents[2]
sys.path.insert(0, str(EXPDIR / 'src'))
import sage.version
load(str(EXPDIR / 'src' / 'h013_f5_signatures.sage'))

t_start = time.time()
out = {
    "experiment": "EXP-SIG-006", "phase": "A_diagnosis",
    "args": vars(args),
    "environment": {
        "sage_version": str(sage.version.version),
        "python_version": sys.version.split()[0],
        "os": platform.platform(), "machine": platform.machine(),
    },
    "started_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "checks": {}, "n9": {}, "series": {},
}


def flush():
    out["elapsed_s_so_far"] = round(time.time() - t_start, 2)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w") as fh:
        json.dump(jsonsafe(out), fh, indent=1)


def sha256(pth):
    return hashlib.sha256(Path(pth).read_bytes()).hexdigest()


PINNED = {
    "h013_f5_signatures.sage": "1ba96fe477c9dc2e7c551c96353c8361d21e40134551342636b2f13015c09087",
    "semaev_tree.py": "e9f1681b4e422f7a67176fffd3e5f91ab7a95c9fddc1eb925c2bb0a93a9becef",
    "ic_first_fall_fast.py": "f1c98bd8642df226760f43038d6687e73794d04b9c7a9073f244b8a0433fad61",
    "macaulay_export.py": "c00b8aad9ad47f8a3f09c39f6b65062a37562703bfd1c4f6159b1e54b1dbad97",
}
ih = {f.name: sha256(f) for f in sorted((EXPDIR / 'src').iterdir())}
out["instrument_sha256"] = ih
out["instrument_sha256_matches_pinned"] = all(ih.get(k) == v for k, v in PINNED.items())
flush()

# ---------------------------------------------------------------- A1/A2
print("=== A1/A2: build n=9 seed=1 sem + old null; column-set law ===", flush=True)
monosets, nb, meta = build_boolean_semaev(9, 3, 1)
rng = random.Random(stable_seed("null", 9, 3, 1))
null_ms = boolean_null(monosets, nb, rng)
eq_degs = [max(mono_deg(m) for m in f) for f in monosets]
degs_null = [max(mono_deg(m) for m in f) for f in null_ms]
out["n9"]["meta"] = meta
out["n9"]["eq_degs_sem"] = sorted(eq_degs)
out["n9"]["eq_degs_null"] = sorted(degs_null)
print("  nb=%d hist=%s standard-ish R_x=%s..." % (nb, meta.get('eq_degs_hist'), str(meta.get('R_x'))[:12]), flush=True)

# receipt anchors (EV-SIG-005 RUN-h/RUN-k)
RECEIPT_NCOLS = {"sem": {3: 544, 4: 3056, 5: 11032, 6: 29332},
                 "null": {3: 936, 4: 4038, 5: 12615, 6: 31180}}

# block id per variable index (n=9: u=0..8, x1=9..11, x2=12..14, x3=15..17)
def block_of(v):
    if v < 9: return 0       # u
    return 1 + (v - 9) // 3  # x1,x2,x3

def block_comp(m):
    c = [0, 0, 0, 0]
    for v in m:
        c[block_of(v)] += 1
    return tuple(c)

def coverage_predict(ms, D):
    """Simple up-closure model: m (|m|<=D) covered iff exists eq i and
    m' in f_i with m' subseteq m and |m|-|m'| <= D - deg_i. Ignores
    cancellation parity."""
    degs = [max(mono_deg(x) for x in f) for f in ms]
    subs = []  # per eq: list of (monomial, deg_eq)
    for i, f in enumerate(ms):
        subs.append((list(f), degs[i]))
    cov = set()
    for f, di in subs:
        slack = D - di
        for mp in f:
            dmp = len(mp)
            # supersets m of mp with |m| <= D and |m|-|mp| <= slack
            for extra_sz in range(0, min(slack, D - dmp) + 1):
                rest = [v for v in range(nb) if v not in mp]
                for combo in itertools.combinations(rest, extra_sz):
                    cov.add(mp | frozenset(combo))
    return cov

def parity_covered(ms, D):
    """Exact column set via per-row parity (ground truth, same as
    tagged_macaulay's colidx keys but computed independently)."""
    degs = [max(mono_deg(x) for x in f) for f in ms]
    cols = set()
    for i, f in enumerate(ms):
        di = degs[i]
        for md in range(0, D - di + 1):
            for combo in itertools.combinations(range(nb), md):
                prod = multiply(f, frozenset(combo))
                cols |= set(prod)
    return cols

arms = {"sem": monosets, "null": null_ms}
colsets = {a: {} for a in arms}
for aname, ms in arms.items():
    for D in (3, 4, 5, 6):
        t0 = time.time()
        exact = parity_covered(ms, D)
        simple = coverage_predict(ms, D)
        colsets[aname][D] = exact
        ncols = len(exact)
        rec_ok = (ncols == RECEIPT_NCOLS[aname][D])
        parity_diff = exact.symmetric_difference(simple)
        out["n9"].setdefault("columns", {})[f"{aname}_D{D}"] = {
            "ncols": ncols, "receipt": RECEIPT_NCOLS[aname][D],
            "receipt_match": bool(rec_ok),
            "simple_coverage_model_matches_exact": (len(parity_diff) == 0),
            "parity_deviation_count": len(parity_diff),
            "n_missing_constant": int(frozenset() not in exact),
            "cols_by_degree": {str(d): sum(1 for m in exact if len(m) == d)
                               for d in range(0, D + 1)},
            "sec": round(time.time() - t0, 2),
        }
        print("  %s D%d: ncols=%d (receipt %d, match=%s) simple-model delta=%d (%.1fs)"
              % (aname, D, ncols, RECEIPT_NCOLS[aname][D], rec_ok,
                 len(parity_diff), time.time() - t0), flush=True)
        flush()

# missing-set characterization at D6 (and D5)
full6 = set()
for d in range(0, 7):
    for combo in itertools.combinations(range(nb), d):
        full6.add(frozenset(combo))
for D in (5, 6):
    fullD = set(m for m in full6 if len(m) <= D)
    missing = fullD - colsets["sem"][D]
    bc_hist = {}
    for m in missing:
        bc = block_comp(m)
        bc_hist[bc] = bc_hist.get(bc, 0) + 1
    bc_sorted = sorted(bc_hist.items(), key=lambda kv: (kv[1], kv[0]),
                       reverse=True)
    out["n9"][f"missing_sem_D{D}"] = {
        "n_missing": len(missing),
        "by_degree": {str(d): sum(1 for m in missing if len(m) == d)
                      for d in range(0, D + 1)},
        "by_block_comp": {str(k): v for k, v in bc_sorted},
    }
    print("  missing sem D%d: %d monomials, by_degree=%s"
          % (D, len(missing), out["n9"][f"missing_sem_D{D}"]["by_degree"]), flush=True)
# does the null miss anything beyond the constant at D6?
miss_null6 = full6 - colsets["null"][6]
out["n9"]["missing_null_D6"] = {
    "n_missing": len(miss_null6),
    "monomials": [sorted(m) for m in miss_null6],
}
print("  missing null D6: %d -> %s" % (len(miss_null6), [sorted(m) for m in miss_null6]), flush=True)
flush()

# sem-vs-null D6 column diff decomposition
sem6, null6 = colsets["sem"][6], colsets["null"][6]
out["n9"]["coldiff_D6"] = {
    "sem_only": len(sem6 - null6), "null_only": len(null6 - sem6),
    "intersection": len(sem6 & null6),
}
print("  D6 coldiff: sem_only=%d null_only=%d inter=%d"
      % (len(sem6 - null6), len(null6 - sem6), len(sem6 & null6)), flush=True)

# ---------------------------------------------------------------- A3
print("=== A3: variety ground truth (2^%d enumeration) ===" % nb, flush=True)
import numpy as np

def variety_count(ms):
    P = np.arange(2 ** nb, dtype=np.uint32)
    sol = np.ones(2 ** nb, dtype=bool)
    for f in ms:
        acc = np.zeros(2 ** nb, dtype=bool)
        for m in f:
            mm = np.uint32(0)
            for v in m:
                mm |= np.uint32(1 << v)
            acc = np.logical_xor(acc, (P & mm) == mm)
        sol &= ~acc
    return int(sol.sum())

t0 = time.time()
nv_sem = variety_count(monosets)
print("  |V_sem| = %d (%.1fs)" % (nv_sem, time.time() - t0), flush=True)
t0 = time.time()
nv_null = variety_count(null_ms)
print("  |V_null_old| = %d (%.1fs)" % (nv_null, time.time() - t0), flush=True)
out["n9"]["variety"] = {"V_sem": nv_sem, "V_null_old": nv_null,
                        "enumeration": "full 2^18, numpy parity of monomials subseteq point"}
flush()

# ---------------------------------------------------------------- A4
print("=== A4: sr_pred series semantics ===", flush=True)

def series_code_semantics(eq_degs_l, nbv, Dmax):
    """Verbatim replica of the pinned semireg_rank_pred loop."""
    from math import comb
    a = [comb(nbv, j) if j <= nbv else 0 for j in range(Dmax + 2)]
    for d in eq_degs_l:
        for j in range(d, Dmax + 2):
            a[j] -= a[j - d]
    HF = []
    ok = True
    for d in range(Dmax + 2):
        if not ok or a[d] <= 0:
            HF.append(0)
            if a[d] <= 0:
                ok = False
        else:
            HF.append(a[d])
    pred = {}
    tot = 0
    for D in range(0, Dmax + 1):
        tot += comb(nbv, D) - HF[D]
        pred[D] = tot
    return pred, HF

def series_formal(eq_degs_l, nbv, Dmax, sign):
    """Exact formal series (1+z)^nbv * PROD_i (1 + sign*z^{d_i})^{±1}:
    sign=+1 -> the code's effective series (1+z^d)^{-1} per equation;
    sign=-1 -> textbook Bardet (1-z^d) per equation."""
    from math import comb
    N = Dmax + 1
    a = [comb(nbv, j) if j <= nbv else 0 for j in range(N + 1)]
    for d in eq_degs_l:
        if sign == +1:
            # multiply by (1+z^d)^{-1} = sum_k (-1)^k z^{kd}
            b = a[:]
            for j in range(d, N + 1):
                b[j] = sum((-1) ** k * a[j - k * d] for k in range(0, j // d + 1))
            a = b
        else:
            for j in range(N, d - 1, -1):
                a[j] -= a[j - d]
    HF = []
    ok = True
    for dd in range(N + 1):
        if not ok or a[dd] <= 0:
            HF.append(0)
            if a[dd] <= 0:
                ok = False
        else:
            HF.append(a[dd])
    pred = {}
    tot = 0
    for D in range(0, Dmax + 1):
        tot += comb(nbv, D) - HF[D]
        pred[D] = tot
    return pred, HF, a

# n=9 check: code == formal (1+z^d)^{-1}; both vs receipts
pred_code, HF_code = series_code_semantics(eq_degs, nb, 6)
pred_formal, HF_formal, a_formal = series_formal(eq_degs, nb, 6, +1)
pred_bardet, HF_bardet, a_bardet = series_formal(eq_degs, nb, 6, -1)
receipt_sr = {3: 180, 4: 1674, 5: 9504, 6: 28068}
out["series"]["n9"] = {
    "code_loop_pred": {str(k): v for k, v in pred_code.items()},
    "code_loop_HF": HF_code,
    "formal_inv_pred": {str(k): v for k, v in pred_formal.items()},
    "formal_inv_HF": HF_formal,
    "formal_inv_coeffs": a_formal,
    "bardet_pred": {str(k): v for k, v in pred_bardet.items()},
    "bardet_HF": HF_bardet,
    "receipt_sr_pred": {str(k): v for k, v in receipt_sr.items()},
    "code_matches_formal_inv": pred_code == pred_formal,
    "code_matches_receipts": all(pred_code[D] == receipt_sr[D] for D in (3, 4, 5, 6)),
}
print("  n=9: code==formal(1+z^d)^-1: %s ; code==receipts: %s"
      % (pred_code == pred_formal, out["series"]["n9"]["code_matches_receipts"]), flush=True)
print("  HF code   : %s" % HF_code, flush=True)
print("  HF bardet : %s" % HF_bardet, flush=True)
flush()

# freeze degree per n (rebuild meta only; cheap)
def freeze_info(n):
    ms_, nb_, meta_ = build_boolean_semaev(n, 3, 1)
    ed = [max(mono_deg(x) for x in f) for f in ms_]
    pred_, HF_ = series_code_semantics(ed, nb_, 8)
    freeze = next((d for d, h in enumerate(HF_) if h == 0 and d > 0), None)
    return {"n": n, "nb": nb_, "hist": meta_.get("eq_degs_hist"),
            "HF_to_8": HF_, "freeze_degree": freeze,
            "pred": {str(k): v for k, v in pred_.items()}}

for n in (12, 15, 18):
    out["series"][f"n{n}"] = freeze_info(n)
    print("  n=%d nb=%d hist=%s freeze D=%s HF=%s"
          % (n, out["series"][f"n{n}"]["nb"], out["series"][f"n{n}"]["hist"],
             out["series"][f"n{n}"]["freeze_degree"], out["series"][f"n{n}"]["HF_to_8"]), flush=True)
    flush()

# ---------------------------------------------------------------- A5
print("=== A5: fall arithmetic at D6 ===", flush=True)
deg6_sem = out["n9"]["columns"]["sem_D6"]["cols_by_degree"]["6"]
deg6_null = out["n9"]["columns"]["null_D6"]["cols_by_degree"]["6"]
le5_sem_D6 = sum(v for k, v in out["n9"]["columns"]["sem_D6"]["cols_by_degree"].items() if int(k) <= 5)
le5_null_D6 = sum(v for k, v in out["n9"]["columns"]["null_D6"]["cols_by_degree"].items() if int(k) <= 5)
# receipt ranks
rank6_sem, rank6_null = 27292, 31179
rank5_sem, rank5_null = 8595, 9504
out["n9"]["fall"] = {
    "deg6_cols": {"sem": deg6_sem, "null": deg6_null},
    "le5_cols_at_D6": {"sem": le5_sem_D6, "null": le5_null_D6},
    "rank_D6": {"sem": rank6_sem, "null": rank6_null},
    "rank_D5": {"sem": rank5_sem, "null": rank5_null},
    "rowD6_cap_Vle5_lower_bound": {
        "sem": rank6_sem - deg6_sem,
        "null": rank6_null - deg6_null,
    },
    "fall_dims_lower_bound_vs_rankD5": {
        "sem": (rank6_sem - deg6_sem) - rank5_sem,
        "null": (rank6_null - deg6_null) - rank5_null,
    },
    "le5_cols_total_nonconstant": le5_null_D6,
}
print("  rowD6 ∩ V_≤5 lower bound: sem %d, null %d; fall dims vs rank_D5: sem %d, null %d"
      % (rank6_sem - deg6_sem, rank6_null - deg6_null,
         (rank6_sem - deg6_sem) - rank5_sem, (rank6_null - deg6_null) - rank5_null), flush=True)

out["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
out["wall_seconds"] = round(time.time() - t_start, 2)
flush()
print("wrote %s (%.1fs)" % (args.out, out["wall_seconds"]), flush=True)
