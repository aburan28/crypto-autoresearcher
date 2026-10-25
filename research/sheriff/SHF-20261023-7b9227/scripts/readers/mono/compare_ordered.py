"""Control B (ordered base): test the ordered-base census (out/ordered_summary.json) against the
claimed group (Z/2)^{m-2} regular and against wrong groups of the same degree: cyclic regular
C_{2^{m-2}}, dihedral, S_{2^{m-2}}, and (degree 8) the quaternion group Q_8 regular and
C_4 x C_2 regular.  A wrong group is rejected when it predicts cycle types never observed in
thousands of fibres, or by chi-square.  Also aggregates the census totals.
Usage: sage -python compare_ordered.py OUTDIR
"""
import sys, json, os, collections
from sage.all import *
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mono_lib import agl32

OUT = sys.argv[1]
S = json.load(open(os.path.join(OUT, 'ordered_summary.json')))


def dist(G):
    c = collections.Counter()
    for g in G:
        c[tuple(sorted(g.cycle_type()))] += 1
    return c


def regular_rep(G):
    """Regular permutation representation of an abstract (permutation) group G."""
    els = list(G)
    idx = {g: i + 1 for i, g in enumerate(els)}
    gens = []
    for h in G.gens():
        gens.append([idx[h * g] for g in els])
    return PermutationGroup(gens)


alts = {
    2: {'Z2': CyclicPermutationGroup(2)},
    4: {'V4_regular(claimed)': PermutationGroup([[(1, 2), (3, 4)], [(1, 3), (2, 4)]]),
        'C4_regular': CyclicPermutationGroup(4), 'D4': DihedralGroup(4), 'A4': AlternatingGroup(4), 'S4': SymmetricGroup(4)},
    8: {'(Z/2)^3_regular(claimed)': PermutationGroup([[(1, 2), (3, 4), (5, 6), (7, 8)], [(1, 3), (2, 4), (5, 7), (6, 8)], [(1, 5), (2, 6), (3, 7), (4, 8)]]),
        'C8_regular': CyclicPermutationGroup(8), 'C4xC2_regular': regular_rep(PermutationGroup([[(1, 2, 3, 4)], [(5, 6)]])),
        'Q8_regular': regular_rep(QuaternionGroup()), 'D8_natural': DihedralGroup(8),
        'AGL(3,2)': agl32(), 'S8': SymmetricGroup(8)},
}


def chi2(obs, probs, N):
    s = 0.0; imp = {}
    for k in set(obs) | set(probs):
        o = obs.get(k, 0); pk = probs.get(k, 0)
        if pk == 0:
            if o: imp[str(k)] = o
            continue
        s += (o - pk * N) ** 2 / (pk * N)
    return round(float(s), 1), imp


out = {'per_curve': {}, 'totals': {}}
tot = collections.defaultdict(lambda: collections.Counter())
for key, bym in S['frobenius'].items():
    out['per_curve'][key] = {}
    for mk, rec in bym.items():
        m = int(mk.split('=')[1]); d = 2 ** (m - 2)
        obs = collections.Counter({eval(k): v for k, v in rec['cycle_types'].items()})
        N = sum(obs.values())
        if N == 0:
            out['per_curve'][key][mk] = {'admissible': 0, 'alternatives': {}}
            continue
        tot[mk]['admissible'] += N
        tot[mk]['mismatches'] += rec['mismatches']
        tot[mk]['identity'] += obs[tuple([1] * d)]
        for st, v in rec['status_counts'].items():
            tot[mk]['status:' + st] += v
        res = {}
        for name, G in alts[d].items():
            dd = dist(G); o = sum(dd.values())
            probs = {k: v / o for k, v in dd.items()}
            c2, imp = chi2(obs, probs, N)
            res[name] = {'order': int(o), 'chi2': c2, 'dof': len(probs) - 1, 'types_predicted_never_seen': [str(k) for k in probs if obs.get(k, 0) == 0], 'types_seen_impossible': imp}
        out['per_curve'][key][mk] = {'admissible': N, 'alternatives': res}
for mk, c in tot.items():
    d = 2 ** (int(mk.split('=')[1]) - 2)
    out['totals'][mk] = dict(c)
    out['totals'][mk]['identity_fraction'] = (c['identity'] / c['admissible']) if c['admissible'] else None
    out['totals'][mk]['chebotarev_identity'] = 1.0 / d
json.dump(out, open(os.path.join(OUT, 'compare_ordered.json'), 'w'), indent=1, default=str)
print(json.dumps(out['totals'], indent=1, default=str))
for key, bym in out['per_curve'].items():
    for mk, r in bym.items():
        print(key, mk, 'N=%d' % r['admissible'], {n: (a['chi2'], len(a['types_predicted_never_seen']), bool(a['types_seen_impossible'])) for n, a in r['alternatives'].items()})
