import sys, random, time
from math import comb
EXP = "/Volumes/Volume/crypto-autoresearcher/experiments/EXP-SIG-005"
sys.path.insert(0, EXP + "/src")
load(EXP + "/src/h013_f5_signatures.sage")

def P(*a):
    print(*a); sys.stdout.flush()

def model(n, N=60):
    nb = 2*n
    a = [comb(nb, j) if j <= nb else 0 for j in range(N)]
    for d in ([2]*n + [3]*n):
        for j in range(d, N):
            a[j] -= a[j-d]
    return a
def pred_dreg(n):
    a = model(n)
    return next(D for D in range(len(a)) if a[D] <= 0)

def rank_bitmasks(masks):
    piv = {}
    for bb in masks:
        bb = int(bb)
        while bb:
            lead = bb.bit_length() - 1
            if lead in piv:
                bb ^^= piv[lead]
            else:
                piv[lead] = bb
                break
    return len(piv)

def degree_fall_counts(monosets, nb, D, kmax=2):
    """rank_full and n_le_k = dim of ideal elements of degree <= k at Macaulay deg D."""
    rows, colidx = tagged_macaulay(monosets, nb, D)
    coldeg = {c: mono_deg(m) for m, c in colidx.items()}
    full = []
    for tag, prod in rows:
        bb = 0
        for m in prod:
            bb |= 1 << colidx[m]
        if bb:
            full.append(int(bb))
    rank_full = rank_bitmasks(full)
    out = {"rank_full": rank_full, "ncols": len(colidx), "nrows": len(rows)}
    for k in range(0, min(kmax, D - 1) + 1):
        keepmask = 0
        for c, dg in coldeg.items():
            if dg > k:
                keepmask |= 1 << c
        keepmask = int(keepmask)
        rank_high = rank_bitmasks([bb & keepmask for bb in full if (bb & keepmask)])
        out["n_le_%d" % k] = rank_full - rank_high
    return out

for n in [6, 9]:
    t, seed = 3, 1
    dr = pred_dreg(n)
    monosets, nb, meta = build_boolean_semaev(n, t, seed)
    P("=" * 80)
    P("n=%d t=%d nb=%d n_eqs=%d eq_deg_hist=%s  PRED d_reg=%d"
      % (n, t, nb, meta["n_eqs"], meta["eq_degs_hist"], dr))
    P("--- AXIS A: 'extra' (non-model syzygies) census [task definition of first-fall] ---")
    P("  D | rank sr_pred deficit | kdim rankK EXTRA | note")
    d_ff_extra = None
    for D in range(1, dr + 1):
        t0 = time.time()
        rec, rows, kernel, kpiv = analyze_syzygy_space(
            monosets, nb, D, extract=(D <= 4), block_size=n)
        note = ""
        if rec["extra"] > 0 and d_ff_extra is None:
            d_ff_extra = D
            note = "<== d_ff (first extra>0)"
        if D == dr:
            note += " [d_reg]"
        P("  %d | %6d %6d %6d | %6d %5d %5d | %s  (%.1fs)"
          % (D, rec["rank"], rec["sr_pred"], rec["deficit"],
             rec["kernel_dim"], rec["rankK"], rec["extra"], note, time.time()-t0))
        if D <= 4 and rec.get("extra_reps"):
            from collections import Counter
            md = Counter(tuple(rp["mult_degrees"]) for rp in rec["extra_reps"])
            sr = Counter(rp["support_rows"] for rp in rec["extra_reps"])
            P("      extra_reps=%d  mult_deg_hist=%s  support_rows_hist=%s"
              % (len(rec["extra_reps"]), dict(md), dict(sr)))
    P("  A-result: d_ff(extra)=%s  d_reg=%d  gap=%s"
      % (d_ff_extra, dr, (dr - d_ff_extra) if d_ff_extra else "n/a"))

    P("--- AXIS B: operational degree-fall census (dim of ideal elts of deg<=k at Macaulay deg D) ---")
    P("  D | rank_full ncols nrows | n_le_0(const) n_le_1(linear) n_le_2 | note")
    d_ff_lin = None
    for D in range(2, dr + 1):
        t0 = time.time()
        c = degree_fall_counts(monosets, nb, D, kmax=2)
        if c.get("n_le_1", 0) > 0 and d_ff_lin is None:
            d_ff_lin = D
        note = ""
        if D == d_ff_lin and c.get("n_le_1", 0) > 0:
            note = "<== first LINEAR appears"
        if D == dr:
            note += " [d_reg]"
        P("  %d | %8d %6d %6d | le0=%d le1=%d le2=%d | %s  (%.1fs)"
          % (D, c["rank_full"], c["ncols"], c["nrows"],
             c.get("n_le_0", 0), c.get("n_le_1", 0), c.get("n_le_2", 0),
             note, time.time()-t0))
    P("  B-result: first LINEAR ideal element at D=%s (d_reg=%d)" % (d_ff_lin, dr))
    P("")
P("ALL DONE")
