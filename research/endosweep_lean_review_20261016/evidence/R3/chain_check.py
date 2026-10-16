import json, re
L = open('/home/user/wt/lean/formal/CryptoResearch/Endosweep/ChainEigen.lean').read()
R = '/home/user/wt/lean/research/'
d = json.load(open(R+'endosweep_chainsweep_20261006/chains.constants.json'))
n = int(d['n'],16); lam = int(d['omega_root'],16)
gn = int(re.search(r'def n : Int := (\d+)', L).group(1))
gl = int(re.search(r'def lamω : Int := (\d+)', L).group(1))
print('n', gn==n, 'lam', gl==lam, 'D', d['D_K'], 'cons', d['eigenvalues_consistent_across_orders'], 'nchains', len(d['chains']))
rows = re.findall(r'\{ id := "([^"]+)", a := (-?\d+), b := (-?\d+), ma := (-?\d+), mb := (-?\d+), norm := (\d+), order := \[([\d, ]+)\], e := (\d+),\s*b1 := \((-?\d+), (-?\d+)\), b2 := \((-?\d+), (-?\d+)\),\s*tests := \[\((-?\d+), (-?\d+), (-?\d+)\), \((-?\d+), (-?\d+), (-?\d+)\)\] \}', L)
print('lean rows', len(rows))
ok = True
for row, c in zip(rows, d['chains']):
    (id_, a, b, ma, mb, norm, order, e, b11, b12, b21, b22, k, k1, k2, kk, kk1, kk2) = row
    want = (c['id'], c['element'][0], c['element'][1], c['matched_element'][0], c['matched_element'][1], c['norm'], [int(x) for x in order.split(',')] == c['order'],
            int(e) == int(c['eigenvalue'],16),
            (int(b11), int(b12)) == tuple(int(x) for x in c['glv_basis'][0]),
            (int(b21), int(b22)) == tuple(int(x) for x in c['glv_basis'][1]),
            [(int(k),int(k1),int(k2)),(int(kk),int(kk1),int(kk2))] == [(int(t['k'],16), int(t['k1']), int(t['k2'])) for t in c['test_vectors']])
    got = (id_, int(a), int(b), int(ma), int(mb), int(norm))
    if got != want[:6] or not all(want[6:]): ok=False; print('MISMATCH', id_, got, want)
print('all rows match:', ok, [r[0] for r in rows] == [c['id'] for c in d['chains']])
# 20261005 chain constants
for fn, nm in [('cryptopro_b_chain_5_5_7.constants.json','e557'), ('cryptopro_b_chain_5_31.constants.json','e531')]:
    j = json.load(open(R+'endosweep_20261005/'+fn))
    keys = list(j.keys())
    ev = j.get('eigenvalue')
    lv = int(re.search(r'def '+nm+r' : Int := (\d+)', L).group(1))
    print(fn, keys[:20])
    print('  eigen', ev, 'match', (int(ev,16) if isinstance(ev,str) else ev) == lv, 'matched', j.get('matched_element'), 'n', int(j['n'],16)==n if 'n' in j else None)
