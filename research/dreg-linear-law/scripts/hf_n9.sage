import sys, random, time
from math import comb
from collections import Counter

EXP = "/Volumes/Volume/crypto-autoresearcher/experiments/EXP-SIG-005"
sys.path.insert(0, EXP + "/src")
load(EXP + "/src/h013_f5_signatures.sage")

def model_a(nb, eq_degs, N):
    a = [comb(nb, j) if j <= nb else 0 for j in range(N + 1)]
    for d in eq_degs:
        for j in range(d, N + 1):
            a[j] -= a[j - d]
    return a

def pred_dreg(nb, eq_degs, N=80):
    a = model_a(nb, eq_degs, N)
    return next(D for D in range(len(a)) if a[D] <= 0)

def echelon_pivot_degs(rows, colidx):
    inv = {c: m for m, c in colidx.items()}
    piv = {}
    for (tag, prod) in rows:
        bb = 0
        for m in prod:
            bb |= 1 << colidx[m]
        bb = int(bb)
        while bb:
            lead = bb.bit_length() - 1
            if lead in piv:
                bb = bb ^^ piv[lead]
            else:
                piv[lead] = bb
                break
    degc = Counter()
    for lead in piv:
        degc[mono_deg(inv[lead])] += 1
    return degc, len(piv)

def single_matrix_hf(n, D, t=3, seed=1):
    monosets, nb, meta = build_boolean_semaev(n, t, seed)
    eq_degs = [max(mono_deg(m) for m in f) for f in monosets]
    dreg = pred_dreg(nb, eq_degs)
    rng = random.Random(stable_seed("null", n, t, seed))
    null_ms = boolean_null(monosets, nb, rng)
    print("=" * 80, flush=True)
    print("n=%d nb=%d n_eqs=%d eq_hist=%s  graded HF from SINGLE matrix M_D at D=%d  (pred d_reg=%d)"
          % (n, nb, len(monosets),
             {d: eq_degs.count(d) for d in sorted(set(eq_degs))}, D, dreg), flush=True)
    for arm, ms in (("null", null_ms), ("sem", monosets)):
        t0 = time.time()
        rows, colidx = tagged_macaulay(ms, nb, D)
        cdeg = Counter(mono_deg(m) for m in colidx)
        pdc, rk = echelon_pivot_degs(rows, colidx)
        print("  [%s] ncols=%d rank=%d stacked_q=%d  (%.1fs)"
              % (arm, len(colidx), rk, len(colidx) - rk, time.time() - t0), flush=True)
        print("    d | appear(d) | pivots(d) | HF_graded(d)", flush=True)
        for d in range(0, D + 1):
            ap = cdeg.get(d, 0)
            pv = pdc.get(d, 0)
            print("    %d | %9d | %9d | %d" % (d, ap, pv, ap - pv), flush=True)

single_matrix_hf(9, 5)   # pre-collapse (d_reg=6)
single_matrix_hf(9, 6)   # at d_reg=6
