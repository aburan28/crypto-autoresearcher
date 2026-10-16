import json, re, sys
sys.path.insert(0, '/home/user/wt/lean')
from harness.endosweep import subgroup as SG, quadorder as QO
L = open('/home/user/wt/lean/formal/CryptoResearch/Endosweep/SubgroupIndex.lean').read()
def grab(ns, name):
    blk = L.split(f'namespace {ns}')[1].split(f'end {ns}')[0]
    m = re.search(r'def ' + re.escape(name) + r' : \w+ := (.+)', blk)
    return m.group(1)
d = json.load(open('/home/user/wt/lean/research/endosweep_subgroup_20261008/subgroup.json'))['results']
ark = {c['name']: c for c in json.load(open('/home/user/wt/lean/research/endosweep_curves_20261006/arkworks/curves.json'))['curves']}
def ev(s, env):
    s = s.replace('BLS.', '').replace('CP6.', '')
    s = s.replace('0x', '0x')
    return eval(s, {}, env)
# CP6
c = d['CP6-782 G1']; a = ark['cp6_782']
env = {}
for nm in ['D','p','r','h','t','eα','e']:
    env[nm] = ev(grab('CP6', nm), env)
env['π'] = ev(grab('CP6','π'), env)
for nm in ['βmem','βclr','βclrShort']:
    env[nm] = ev(grab('CP6', nm), env)
print('CP6 p', env['p'] == int(a['field']['p'],16))
print('CP6 r', env['r'] == int(c['r'],16) == int(a['order'],16))
print('CP6 h', env['h'] == int(c['h'],16) == int(a['cofactor'],16))
print('CP6 t', env['t'] == int(c['trace'],16))
print('CP6 pi', env['π'] == tuple(int(x) for x in c['frobenius_in_O']))
print('CP6 eα', env['eα'] == int(c['alpha']['eigenvalue_on_G'],16))
print('CP6 e', env['e'] == int(c['effective_cofactor'],16))
al = SG.Alpha(4, 1, 0, {}, '')
def to_w(cc): return al.to_omega(int(cc['c0']), int(cc['c1']))
print('CP6 βmem', env['βmem'] == to_w(c['membership']['chosen']), c['membership']['chosen']==c['membership']['shortest_valid'])
print('CP6 βclr', env['βclr'] == to_w(c['clearing']['chosen']))
print('CP6 βclrShort', env['βclrShort'] == to_w(c['clearing']['shortest_valid']))
D=-339; pim1=(env['π'][0]-1, env['π'][1]); r=env['r']; h=env['h']
print(' recompute: N(pi)=p', QO.norm(D,*env['π'])==env['p'], 'Tr', QO.trace(D,*env['π'])==env['t'], 'N(pi-1)=hr', QO.norm(D,*pim1)==h*r)
print(' idx mem', SG.element_index(D,[env['βmem'],pim1])==r, 'idx clr', SG.element_index(D,[env['βclr'],pim1])==h, SG.element_index(D,[env['βclrShort'],pim1])==h)
print(' h=6e', h==6*env['e'], SG.element_index(D,[(env['e'],0),pim1])==h)
print(' tors', [SG.element_index(D,[(l,0),pim1]) for l in (2,3,7,29)], [x['predicted'] for x in c['torsion_checks']])
print(' json kernel_order mem', int(c['membership']['chosen']['kernel_order_on_E(F_q)'])==r, 'clr', int(c['clearing']['chosen']['kernel_order_on_E(F_q)'])==h)
print(' t = p+1-hr', env['t'] == env['p']+1-h*r)
# BLS
c = d['BLS12-381 G1']; a = ark['bls12_381']
env = {}
for nm in ['D','u','p','r','h','t','eφ']:
    env[nm] = ev(grab('BLS', nm), env)
env['π'] = ev(grab('BLS','π'), env)
env['φ'] = ev(grab('BLS','φ'), env)
for nm in ['βmem','βmemShort']:
    env[nm] = ev(grab('BLS', nm), env)
print('BLS u', env['u'] == SG.BLS12_381_U)
print('BLS p', env['p'] == int(a['field']['p'],16))
print('BLS r', env['r'] == int(c['r'],16) == int(a['order'],16))
print('BLS h', env['h'] == int(c['h'],16) == int(a['cofactor'],16))
print('BLS t', env['t'] == int(c['trace'],16))
print('BLS pi', env['π'] == tuple(int(x) for x in c['frobenius_in_O']))
print('BLS eφ', env['eφ'] == int(c['alpha']['eigenvalue_on_G'],16))
al = SG.Alpha(-1, 1, 0, {}, '')
def to_w(cc): return al.to_omega(int(cc['c0']), int(cc['c1']))
print('BLS βmem', env['βmem'] == to_w(c['membership']['chosen']))
print('BLS βmemShort', env['βmemShort'] == to_w(c['membership']['shortest_valid']))
print('BLS clearing chosen', c['clearing']['chosen']['c0'], 1-env['u'])
