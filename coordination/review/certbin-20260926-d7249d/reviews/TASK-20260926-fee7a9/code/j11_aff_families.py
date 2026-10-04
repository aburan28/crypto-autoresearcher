"""J11 (4): N-AFF19 effective family count. Per family: solve E(r) = E'^0 + sum_j r_j E'^j
(r = bits of x_R) by own GF(2) elimination over the family's systems, check every system
fits, and compute affine ranks per family and pooled."""
import sys, json, gzip, collections
run, outp = sys.argv[1], sys.argv[2]
recs = [json.loads(l) for l in gzip.open(run + '/instances.jsonl.gz', 'rt')]
aff = [r for r in recs if r['arm'] == 'N-AFF19']
def vec(r):
    x = 0
    for k, h in enumerate(r['E_hex']):
        x |= int(h, 16) << (211 * k)
    return x
def rank(vs):
    piv = {}
    for v in vs:
        while v:
            p = v.bit_length() - 1
            if p in piv:
                v ^= piv[p]
            else:
                piv[p] = v; break
    return len(piv)
res = {'families': {}}
fam = collections.defaultdict(list)
for r in aff:
    fam[r['family']].append(r)
allv = []
for d in sorted(fam):
    rs = fam[d]
    vs = [vec(r) for r in rs]
    allv += vs
    aff_rank = rank([v ^ vs[0] for v in vs[1:]])
    # solve for E'^0, E'^j: unknown coefficient vector per system is (1, r_0..r_18)
    # Gaussian elimination on augmented rows [coef | E]
    rows = []
    for r, v in zip(rs, vs):
        coef = 1 | ((r['x_R'] & ((1 << 19) - 1)) << 1)
        rows.append((coef, v))
    piv = {}
    fits = True
    for coef, v in rows:
        while coef:
            p = coef.bit_length() - 1
            if p in piv:
                pc, pv = piv[p]; coef ^= pc; v ^= pv
            else:
                piv[p] = (coef, v); break
        if coef == 0 and v != 0:
            fits = False  # inconsistent: system not affine in r
    res['families'][d] = {'n_systems': len(rs), 'affine_rank_of_systems': aff_rank,
                          'coef_rank': len(piv), 'all_systems_fit_one_affine_map_in_r': fits}
res['pooled_affine_rank'] = rank([v ^ allv[0] for v in allv[1:]])
res['n_pooled'] = len(allv)
json.dump(res, open(outp, 'w'), indent=1)
print(json.dumps(res, indent=1))
