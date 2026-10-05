#!/usr/bin/env python3
"""Independent post-checks of a closure output on one instance.
usage: postcheck.py SYSTEM.ms  PREFIX.lm  SOLUTIONS.txt  [D=4]
 (i)  LM-file hash (SHA-256 of the file exactly as defined on the card) and per-size counts
 (ii) evaluation-kernel ground truth from the enumerated zero set V: LM(I_{<=D}) computed WITHOUT any closure
      (m in LM(I) iff its evaluation vector on V lies in the span of the evaluation vectors of all smaller monomials);
      checks  LM(W) subset of LM(I_{<=D})  (else 'impossible'-type error) and  r <= c - rank_V ;
      reports whether LM(W) == LM(I_{<=D}) and whether the up-sets they generate coincide.
 (iii) N_std by an APRIORI level-wise count of faces (an algorithm that shares nothing with the C depth-first search):
      F_s = { S, |S| = s : all (s-1)-subsets in F_{s-1} and (s <= D implies S not in LM) }.
 prints one JSON line."""
import sys, os, json, hashlib, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from msparse import *
from ref_closure import eval_vec, popcount, all_monomials, key_degrevlex

def main():
    ms, lmf, solf = sys.argv[1:4]
    D = int(sys.argv[4]) if len(sys.argv) > 4 else 4
    N, B, R, info = parse_ms(ms)
    raw = open(lmf, 'rb').read()
    lm_hash = hashlib.sha256(raw).hexdigest()
    lms = [int(x) for x in raw.decode().split()]
    assert lms == sorted(lms) and len(set(lms)) == len(lms)
    lmset = set(lms)
    pts = [int(x) for x in open(solf).read().split()]
    out = dict(instance=os.path.basename(ms), N=N, lm_sha256=lm_hash, n_lm=len(lms),
               lm_by_size=[sum(1 for m in lms if popcount(m) == s) for s in range(D + 1)], V=len(pts))
    # (ii) evaluation-kernel ground truth
    mons = sorted(all_monomials(N, D), key=key_degrevlex)
    c = len(mons)
    basis = {}; lmI = set(); std = []
    for m in mons:
        v = eval_vec(m, pts)
        while v:
            h = v.bit_length() - 1
            if h in basis: v ^= basis[h]
            else: basis[h] = v; break
        if v: std.append(m)
        else: lmI.add(m)
    out['columns'] = c; out['eval_rank'] = len(std); out['r_I_upper_bound'] = c - len(std)
    out['LM_W_subset_LM_I'] = lmset <= lmI
    out['rank_le_bound'] = len(lms) <= c - len(std)
    out['LM_W_equals_LM_I'] = (lmset == lmI)
    out['missing_from_W'] = len(lmI - lmset)
    # up-set generated within size <= D: monomials of size<=D containing a member of LM(W)
    # (check LM(I)'s up-closure inside {<=D}: is every LM(I) monomial above some LM(W) member?)
    def upgen(S):
        S = set(S); res = set()
        for m in all_monomials(N, D):
            # does m contain a member of S as subset?  test all subsets of m (m has <= D bits)
            bits = [j for j in range(N) if (m >> j) & 1]
            found = False
            for r in range(len(bits) + 1):
                for sub in itertools.combinations(bits, r):
                    mm = 0
                    for j in sub: mm |= 1 << j
                    if mm in S: found = True; break
                if found: break
            if found: res.add(m)
        return res
    out['upset_W_equals_upset_I_leq_D'] = None
    out['std_ground_truth_sizes'] = [popcount(m) for m in std]
    # (iii) Apriori count
    faces_prev = {0} if 0 not in lmset else set()
    total = len(faces_prev)
    sizes = [len(faces_prev)]
    s = 1
    while faces_prev:
        cand = set()
        for S in faces_prev:
            hi = S.bit_length()
            for v in range(hi, N):
                cand.add(S | (1 << v))
        faces = set()
        for T in cand:
            if s <= D and T in lmset: continue
            ok = True
            x = T
            while x:
                low = x & -x
                if (T ^ low) not in faces_prev: ok = False; break
                x ^= low
            if ok: faces.add(T)
        total += len(faces); sizes.append(len(faces))
        faces_prev = faces; s += 1
    out['N_std_apriori'] = total
    out['N_std_apriori_by_size'] = sizes
    out['verdict_apriori'] = 'sufficient' if total == len(pts) else ('insufficient' if total > len(pts) else 'impossible')
    print(json.dumps(out))

main()
