"""J3 (iii): LOWER-bracket audit on the curve arm from raw-result.json.
Own affine group law and double-and-add (no code shared with the producer):
re-verify every certificate [k]P == Q, check that every solved target has a
certificate, every certificate's target is solved, k_found == certificate k,
unsolved targets carry k_found == -1, and that the arm's solved count equals
its certificate count.  Also re-derive, for RESEL-L arms, that the set of
targets whose walks may enter the pool (solved) is exactly the certified set."""
import json, sys, time
BASE = 'experiments/EXP-ECDLP-612fb1/runs'
RUNS = ['RUN-ECDLP-612fb1-34', 'RUN-ECDLP-612fb1-35', 'RUN-ECDLP-612fb1-36']

def inv(a, p):
    return pow(a % p, p - 2, p)

def add(P1, P2, p, a):
    if P1 is None: return P2
    if P2 is None: return P1
    x1, y1 = P1; x2, y2 = P2
    if x1 == x2:
        if (y1 + y2) % p == 0: return None
        lam = (3 * x1 * x1 + a) * inv(2 * y1, p) % p
    else:
        lam = (y2 - y1) * inv(x2 - x1, p) % p
    x3 = (lam * lam - x1 - x2) % p
    return (x3, (lam * (x1 - x3) - y1) % p)

def mul(k, P, p, a):
    R = None; Q = P
    while k:
        if k & 1: R = add(R, Q, p, a)
        Q = add(Q, Q, p, a); k >>= 1
    return R

out = {}
t0 = time.time()
for rid in RUNS:
    raw = json.load(open(f'{BASE}/{rid}/raw-result.json'))
    cv = raw['curve']; p, a, b, N = cv['p'], cv['a'], cv['b'], cv['N']
    G = tuple(cv['P'])
    assert (G[1] ** 2 - G[0] ** 3 - a * G[0] - b) % p == 0
    assert mul(N, G, p, a) is None, 'N*G != O'
    res = {'curve_id': cv['curve_id'], 'p': p, 'N': N, 'arms': {}}
    for arm, A in raw['arms'].items():
        solved = A['solved']; kf = A.get('k_found'); certs = A.get('certificates', [])
        U = len(solved)
        n_solved = sum(solved)
        cert_targets = {c['target'] for c in certs}
        ok_verify = 0; bad_verify = []; mism_k = 0; on_curve_Q = 0
        for c in certs:
            Q = tuple(c['Q']); k = c['k']
            if (Q[1] ** 2 - Q[0] ** 3 - a * Q[0] - b) % p == 0: on_curve_Q += 1
            R = mul(k, G, p, a)
            if R == Q: ok_verify += 1
            else: bad_verify.append(c['target'])
            if kf is not None and kf[c['target']] != k: mism_k += 1
        solved_set = {u for u in range(U) if solved[u]}
        unsolved_with_k = (sum(1 for u in range(U) if not solved[u] and kf[u] != -1) if kf is not None else None)
        solved_without_k = (sum(1 for u in range(U) if solved[u] and kf[u] == -1) if kf is not None else None)
        res['arms'][arm] = {'targets': U, 'solved': n_solved, 'certificates': len(certs),
                            'cert_targets_eq_solved_set': cert_targets == solved_set if arm != 'RHO' else 'n/a (RHO emits none)',
                            'independent_verify_pass': ok_verify, 'independent_verify_fail': bad_verify[:10], 'n_fail': len(bad_verify),
                            'Q_on_curve': on_curve_Q, 'k_found_mismatch_vs_cert': mism_k,
                            'unsolved_targets_with_k_found': unsolved_with_k, 'solved_targets_without_k_found': solved_without_k,
                            'producer_verified_flags_all_true': all(c.get('verified') for c in certs),
                            'producer_seeded_log_match_all_true': all(c.get('seeded_log_match') for c in certs),
                            'k_in_range_1_N-1': all(1 <= c['k'] < N for c in certs)}
    out[rid] = res
    print(rid, json.dumps(res, indent=None)[:1800])
print('elapsed', round(time.time() - t0, 1), 's')
json.dump(out, open(sys.argv[1] + '/j3_lower_bracket_curve.json', 'w'), indent=1)
