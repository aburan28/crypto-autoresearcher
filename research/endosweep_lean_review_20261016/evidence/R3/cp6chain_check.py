import json, re
L = open('/home/user/wt/lean/formal/CryptoResearch/Endosweep/ChainEigen.lean').read()
d = json.load(open('/home/user/wt/lean/research/endosweep_curves_20261006/curves.json'))
c = next(c for c in d['results'] if c['name']=='arkworks/cp6_782')
ark = {x['name']:x for x in json.load(open('/home/user/wt/lean/research/endosweep_curves_20261006/arkworks/curves.json'))['curves']}
r = int(ark['cp6_782']['order'],16)
blk = L.split('namespace CP6')[1]
lr = int(re.search(r'def r : Int := (\d+)', blk).group(1))
print('r', lr==r, 'nrows json', len(c['rows']), 'eig_consistent', c['eigenvalues_consistent'])
rows = re.findall(r'\{ a := (-?\d+), b := (-?\d+), sign := (-?\d+), norm := (\d+), steps := \[([\d, ]+)\], e := (\d+) \}', blk)
print('lean rows', len(rows))
print('json row keys', list(c['rows'][0].keys()))
ok=True
for lrw, jr in zip(rows, c['rows']):
    a,b,s,nm,st,e = lrw
    good = [int(a),int(b)]==jr['element'] and int(nm)==jr['norm'] and [int(x) for x in st.split(',')]==jr['steps'] and int(e)==int(jr['eigenvalue'],16)
    if not good: ok=False; print('MISMATCH', lrw, jr['element'], jr['norm'], jr['steps'], jr['eigenvalue'])
print('rows match', ok)
e9 = int(re.search(r'def e9 : Int := (0x[0-9a-f]+)', blk).group(1),16)
e4 = int(re.search(r'def e4 : Int := (\d+)', blk).group(1))
print('e9 in json', any(jr['element']==[9,1] and int(jr['eigenvalue'],16)==e9 for jr in c['rows']))
print('e4 == row0', e4 == int(c['rows'][0]['eigenvalue'],16))
# sign determination independently
lam = e4-4
for jr in c['rows']:
    a,b = jr['element']; e=int(jr['eigenvalue'],16)
    sg = [s for s in (1,-1) if (e - s*(a+b*lam))%r==0]
    print(jr['element'], sg, end='; ')
print()
# check the cp6_782 README forms
lp = 1-lam
print('5-lp', (e4-(5-lp))%r==0, 'lp-10', (e9-(lp-10))%r==0)
