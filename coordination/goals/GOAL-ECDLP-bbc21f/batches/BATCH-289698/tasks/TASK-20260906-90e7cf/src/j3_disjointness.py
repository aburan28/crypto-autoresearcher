"""J3/J4(ii): the disjointness inequality at BOTH a. A T/2 table cannot cover
more than the exact global top-T/2 basin share; if STATIC(T)'s exact
coverage already exceeds that share, 'T/2 reaches T' is impossible on that
instance whatever the selection rule."""
import json, sys, math
sys.path.insert(0, 'experiments/EXP-ECDLP-612fb1/source')
import instrument as I
BASE = 'experiments/EXP-ECDLP-612fb1/runs'
CELLS = {'2^20,a=1/4': range(1, 6), '2^20,a=1/2': range(6, 11), '2^24,a=1/4': range(13, 18), '2^24,a=1/2': range(18, 23)}
out = {'C_max_model': {a: I.c_max(a)[1] for a in (0.0625, 0.125, 0.25, 0.5)}}
print('MODEL C_max(a):', {k: round(v, 4) for k, v in out['C_max_model'].items()}, '(a/2 is the T/2-table ceiling at the full-T walk length)')
for cell, rr in CELLS.items():
    rows = []
    for i in rr:
        s = json.load(open(f'{BASE}/RUN-ECDLP-612fb1-{i:03d}/summary.json'))
        T = s['params']['T']; top = s['basins']['top_share_by_t']
        stT = s['fixture']['static_T_exact_coverage']
        st_round = [r['exact_coverage'] for r in s['arms']['STATIC(T)']['rounds']]
        rl2 = [r['exact_coverage'] for r in s['arms']['RESEL-L(T/2)']['rounds']]
        rlT = [r['exact_coverage'] for r in s['arms']['RESEL-L(T)']['rounds']]
        st2 = [r['exact_coverage'] for r in s['arms']['STATIC(T/2)']['rounds']]
        s2T = [r['exact_coverage'] for r in s['arms']['STATIC2T']['rounds']]
        rows.append({'seed': s['params']['seeds']['walk_key_seed'], 'top_T': top[str(T)], 'top_T2': top[str(T // 2)], 'top_2T': top[str(2 * T)],
                     'STATIC_T_exact_cov': stT, 'STATIC_T2_exact_cov': st2[0], 'STATIC2T_exact_cov': s2T[0],
                     'STATIC_T_gt_top_T2': stT > top[str(T // 2)],
                     'RESEL_T2_cov_last': rl2[-1], 'RESEL_T2_cov_max': max(rl2), 'RESEL_T2_max_minus_top_T2': max(rl2) - top[str(T // 2)],
                     'RESEL_T_cov_last': rlT[-1], 'RESEL_T_gap_to_top_T': top[str(T)] - rlT[-1],
                     'gap_top_T2_minus_STATIC_T': top[str(T // 2)] - stT,
                     'C_max_a_half': I.c_max(s['params']['a'] / 2)[1], 'C_max_a': I.c_max(s['params']['a'])[1]})
    out[cell] = rows
    print(f'\n== {cell} ==  (T/2 ceiling MODEL C_max(a/2) = {rows[0]["C_max_a_half"]:.4f}; C_max(a) = {rows[0]["C_max_a"]:.4f})')
    print('seed | top-T | top-T/2 | STATIC(T) cov | STATIC(T)>top-T/2 | top-T/2 - STATIC(T) | RESEL-L(T/2) cov last/max | max - top-T/2 | RESEL-L(T) cov last | gap to top-T | STATIC(T/2) cov | STATIC2T cov')
    for r in rows:
        print(f"{r['seed']} | {r['top_T']:.4f} | {r['top_T2']:.4f} | {r['STATIC_T_exact_cov']:.4f} | {r['STATIC_T_gt_top_T2']} | {r['gap_top_T2_minus_STATIC_T']:+.4f} | {r['RESEL_T2_cov_last']:.4f}/{r['RESEL_T2_cov_max']:.4f} | {r['RESEL_T2_max_minus_top_T2']:+.4f} | {r['RESEL_T_cov_last']:.4f} | {r['RESEL_T_gap_to_top_T']:.4f} | {r['STATIC_T2_exact_cov']:.4f} | {r['STATIC2T_exact_cov']:.4f}")
json.dump(out, open(sys.argv[1] + '/j3_disjointness.json', 'w'), indent=1)
