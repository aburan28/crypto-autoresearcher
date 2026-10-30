"""Validator re-derivation of the controls: qr_window positive/negative control, full-period identity,
brute-force 60 cases, planted-relation sensitivity gate, Bateman-Horn comparison. indlib.py only."""
import itertools, math, collections, time
import numpy as np
from math import comb
from indlib import *

t1, t2, t3 = load('t1'), load('t2'), load('t3')
mem = []
for t in ('t4', 't5', 't6', 't7'):
    mem += load(t)['members']
byk = {(m['arm'], m['cell'], m['index']): m for m in mem}


def powmod_vec(a, e, p):
    res = np.ones_like(a)
    base = a % p
    while e:
        if e & 1:
            res = res * base % p
        base = base * base % p
        e >>= 1
    return res


def own_scan(A, B, p, S):
    x = np.arange(S, dtype=np.int64)
    f = (x * x % p * x % p + (A % p) * x % p + (B % p)) % p
    chi = powmod_vec(f, (p - 1) // 2, p)
    sq = chi == 1
    cx = powmod_vec(x, (p - 1) // 2, p)
    inV = cx != p - 1
    return dict(S=S, L=int(sq.sum()), zero=int((f == 0).sum()), V=int(inV.sum()), Vlift=int((inV & sq).sum()))


# ---- qr scans per curve, then pools
t0 = time.time()
bad_scan = []
pools = collections.defaultdict(lambda: [0, 0, 0, 0, 0])
for s in t2['controls']['qr_scans']:
    m = byk[(s['arm'], s['cell'], s['index'])]
    S = min(131072, m['p'] // 2)
    r = own_scan(m['A'], m['B'], m['p'], S)
    rec = s['scan']
    if (r['S'], r['L'], r['zero'], r['V'], r['Vlift']) != (rec['S'], rec['L'], rec['zero'], rec['V'], rec['Vlift']) or s['p'] != m['p']:
        bad_scan.append((s['arm'], s['cell'], s['index'], r, rec))
    d = pools[(s['arm'], s['cell'])]
    d[0] += r['S']; d[1] += r['L']; d[2] += r['V']; d[3] += r['Vlift']; d[4] += 1
print(f"qr scans recomputed for {len(t2['controls']['qr_scans'])} curves; per-curve mismatches vs recorded: {len(bad_scan)}  ({time.time()-t0:.0f}s)")
rec_pools = load('t8')['scan_efficiency']['pools']
ok_band = True
for k in sorted(pools):
    S, L, V, Vl, n = pools[k]
    R, Rw, se = S / L, (Vl / V) / (L / S), 2 / math.sqrt(S)
    rp = rec_pools[f'{k[0]}|{k[1]}']
    same = abs(R - rp['R_pool']) < 1e-12 and abs(Rw - rp['R_wrong']) < 1e-12
    band = (1.98 <= R <= 2.02 and 0.96 <= Rw <= 1.04) if k[0] == 'N-B' else None
    print(f"  {k[0]:4s}{k[1]}: n_curves={n:2d} S_total={S:8d} R_pool={R:.5f} (se {se:.5f}, |R-2|/se={abs(R-2)/se:.2f}) R_wrong={Rw:.5f} recorded_equal={same} N-B-band_ok={band}")

# ---- full-period point-count identity (Euler criterion, not the producer's table-of-squares method)
print('full-period identity (my Euler-criterion scan over all x in F_p):')
t0 = time.time()
allok = True
for x in t2['controls']['full_period']:
    m = byk[(x['arm'], x['cell'], x['index'])]
    p, A, B = m['p'], m['A'], m['B']
    Lc = Z = 0
    chunk = 1 << 21
    for lo in range(0, p, chunk):
        xx = np.arange(lo, min(lo + chunk, p), dtype=np.int64)
        f = (xx * xx % p * xx % p + (A % p) * xx % p + (B % p)) % p
        chi = powmod_vec(f, (p - 1) // 2, p)
        Lc += int((chi == 1).sum()); Z += int((f == 0).sum())
    chi_sum = Lc - (p - Lc - Z)
    ok = (Lc == (m['N'] - 1) // 2 and Z == 0 and chi_sum == m['N'] - p - 1 and chi_sum == -(p + 1 - m['N']))
    allok &= ok
    print(f"  {x['arm']:4s}{x['cell']} idx{x['index']:2d} p={p:9d}: #nonzero-square f(x)={Lc} (N-1)/2={(m['N']-1)//2} zero={Z} sum chi={chi_sum} -trace={-(p+1-m['N'])} ok={ok}")
print('  all full-period identities hold:', allok, f'({time.time()-t0:.0f}s)')

# ---- brute force 60 cases
bf = t2['controls']['brute_force']['detail']
shape = collections.Counter((c['N'], c['B'], c['kind']) for c in bf)
exp_shape = {(N, B, k) for N in (211, 307, 401, 503, 1009) for B in (5, 8, 13, 20) for k in ('random_classes', 'arithmetic_progression', 'random_coset')}
print('brute-force: 60 distinct (N,B,kind) cells exactly the frozen grid:', set(shape) == exp_shape and len(bf) == 60)
badbf = 0
for c in bf:
    N, lab = c['N'], c['labels']
    h = collections.Counter()
    for t in itertools.combinations_with_replacement(lab, 3):
        h[sum(t) % N] += 1
    cs, ts, coll, mx = histogram_stats(lab, N)
    kindok = True
    if c['kind'] == 'arithmetic_progression':
        kindok = lab == list(range(1, len(lab) + 1))
    elif c['kind'] == 'random_coset':
        a = lab[0]
        kindok = lab == [a * i % N for i in range(1, len(lab) + 1)]
    else:
        kindok = len({min(v, N - v) for v in lab}) == len(lab)
    ok = (len(h) == c['coverage'] and sum(h.values()) == comb(len(lab) + 2, 3) and
          (cs, ts) == (sum(h.values()), len(h)) and cov_prefix_scatter(lab, N)[0] == len(h) and kindok and c['ok'])
    # full per-target equality of c(r)
    l = np.asarray(lab, dtype=np.int64); Bq = len(l)
    pairs = np.concatenate([(l[:j + 1] + l[j]) % N for j in range(Bq)])
    hv = np.zeros(N, dtype=np.int64); off = 0
    for k in range(Bq):
        off += k + 1
        hv += np.bincount((pairs[:off] + l[k]) % N, minlength=N)
    ok &= all(int(hv[r]) == h.get(r, 0) for r in range(N))
    badbf += (not ok)
print('brute-force cases failing my literal-itertools full c(r) comparison:', badbf)

# ---- sensitivity gate (t3) re-derivation
def rng(seed, cell, arm, a, b):
    return np.random.Generator(np.random.PCG64(np.random.SeedSequence([seed, CELL_CODE[cell], ARM_CODE[arm], a, b])))

print('sensitivity gate re-derivation:')
for cell in ('C16', 'C20', 'C24'):
    rs = sorted((m for m in t3['members'] if m['cell'] == cell), key=lambda m: m['index'])
    V, ratios, known, det, ks = [], [], [], 0, []
    for m in rs:
        N = m['N']; B = cube_base(N)
        assert m['member_base_size'] == B + 1 and m['member_T'] == comb(B + 3, 3) and len(m['random_seen']) == 200
        mu = comb(B + 2, 3) / N
        kn = (1 - math.exp(-comb(B + 3, 3) / N)) / (1 - math.exp(-mu))
        rnd = np.array(m['random_seen'], float)
        k = int((rnd >= m['member_seen']).sum())
        ks.append(k); det += ((1 + k) / 201 <= 0.01)
        V.append([m['member_seen']] + list(rnd)); ratios.append(m['member_seen'] / rnd.mean()); known.append(kn)
    V, ratios, known = np.array(V, float), np.array(ratios), np.array(known)
    se = ratios.std(ddof=1) / math.sqrt(len(ratios)); tol = max(0.001, 3 * se)
    n = len(V)
    u = rng(7007, cell, 'N-B-ctrl', 0, 0).integers(0, V.shape[1], size=(20000, n))
    pick = V[np.arange(n)[None, :], u]
    ts = (pick / ((V.sum(axis=1)[None, :] - pick) / 200) - 1).mean(axis=1)
    tobs = float(np.mean(V[:, 0] / V[:, 1:].mean(axis=1) - 1))
    p = (1 + int((np.abs(ts) >= abs(tobs)).sum())) / 20001
    ok = (n == 8 and det >= 7 and abs(ratios.mean() - known.mean()) <= tol and p <= 0.001)
    print(f"  {cell}: detected {det}/8 (k per curve {ks}) pooled ratio {ratios.mean():.5f} known {known.mean():.5f} diff {100*abs(ratios.mean()-known.mean()):.3f}% tol {100*tol:.3f}% (margin {100*(tol-abs(ratios.mean()-known.mean())):.3f}%) rand p {p:.2e}  GATE {ok}")

# ---- Bateman-Horn (secondary heuristic H3) recomputation
def bh(lo, hi, qmax=100000):
    sv = bytearray([1]) * (qmax + 1); sv[0:2] = b'\x00\x00'
    for i in range(2, math.isqrt(qmax) + 1):
        if sv[i]:
            sv[i * i::i] = bytearray(len(sv[i * i::i]))
    c = 4.0
    for q in range(3, qmax + 1, 2):
        if not sv[q]:
            continue
        if q < 2000:
            w = sum(1 for t in range(q) if ((5 * t * t + 19 * t + 19) * (5 * t * t + 18 * t + 20)) % q == 0)
        else:
            w = 4 if legendre(-19, q) == 1 else 0
        c *= (1 - w / q) / (1 - 1 / q) ** 2
    tot = 0.0
    for t in range(3, 100000, 2):
        p = 5 * t * t + 19 * t + 19; N = 5 * t * t + 18 * t + 20
        if p > hi: break
        if p > lo: tot += c / (math.log(p) * math.log(N))
    return c, tot
for cell, (lo, hi) in CELLS.items():
    c, e = bh(lo, hi)
    rb = t1['inventory']['bateman_horn'][cell]
    print(f'  BH {cell}: mine c_odd={c:.6f} expected={e:.4f} | recorded c_odd={rb["c_odd"]:.6f} expected={rb["expected"]:.4f} exact={rb["exact"]}')
