import json, sys
sys.path.insert(0, 'm3closure'); sys.path.insert(0, 'm3closure/vendor')
import pilot_lib as L
out = json.load(open('brial_systems.json'))
for cell in ['n9-poly', 'n11-poly']:
    d = json.load(open(f'm3closure/instances/{cell}.json'))
    for i, x in enumerate(d['instances'][:12]):
        sysm = L.build_chain3(d['n'], d['k'], d['basis'], d['b'], x['z'], d['modulus'])
        fake = {"N": sysm["N"], "equations": sysm["equations"], "seed": 0, "draw": i,
                "var_names": [f"v{j}" for j in range(sysm["N"])], "n": d['n'], "m": 3, "t": 3, "k": d['k']}
        nl = L.boolsys.matched_null(fake, 1)
        cnt, bs = L.boolean_count_m2({"N": nl["N"], "equations": nl["equations"]})
        out[cell].append({'id': x['id'].replace('-S3-','-NULL2-'), 'family': 'NULL2', 'n': d['n'], 'N': nl['N'], 'nsol': cnt, 'equations': nl['equations']})
    print(cell, 'null2 added', flush=True)
json.dump(out, open('brial_systems.json', 'w'))
