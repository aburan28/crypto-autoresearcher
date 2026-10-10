import json, sys, os
sys.path.insert(0, 'm3closure'); sys.path.insert(0, 'm3closure/vendor')
import pilot_lib as L
cells = sys.argv[1:]
cap_uns, cap_sat = 40, 10
out = {}
for cell in cells:
    d = json.load(open(f'm3closure/instances/{cell}.json'))
    uns = [i for i in d['instances'] if i['nsol']==0][:cap_uns]; sat = [i for i in d['instances'] if i['nsol']>0][:cap_sat]
    rows = []
    for i in uns + sat:
        sysm = L.build_chain3(d['n'], d['k'], d['basis'], d['b'], i['z'], d['modulus'])
        assert sysm['N'] == i['N']
        rows.append({'id': i['id'], 'family': 'S3', 'n': i['n'], 'N': i['N'], 'nsol': i['nsol'], 'equations': sysm['equations']})
        if i['nsol'] == 0 and len([r for r in rows if r['family']=='NULL']) < 12:
            nl = L.support_null(sysm, i['id'])
            rows.append({'id': i['id'].replace('-S3-','-NULL-'), 'family': 'NULL', 'n': i['n'], 'N': i['N'], 'nsol': -1, 'equations': nl['equations']})
    out[cell] = rows
    print(cell, len(rows), flush=True)
json.dump(out, open('brial_systems.json', 'w'))
