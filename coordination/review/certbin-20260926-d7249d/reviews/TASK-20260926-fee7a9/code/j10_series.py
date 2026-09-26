"""J10 (1): Boolean semi-regular series and every reference number of D-5, exact integer arithmetic."""
import json, sys
from math import comb
def series(n, m, terms=6):
    # (1+z)^n / (1+z^2)^m as a power series, exact
    num = [comb(n, i) for i in range(terms)]
    inv = [0] * terms  # 1/(1+z^2)^m = sum_k (-1)^k C(m+k-1,k) z^{2k}
    for k in range(terms):
        if 2 * k < terms:
            inv[2 * k] = (-1) ** k * comb(m + k - 1, k)
    out = [sum(num[i] * inv[d - i] for i in range(d + 1)) for d in range(terms)]
    return out
def dimB(n, d):
    return sum(comb(n, i) for i in range(d + 1))
s20 = series(20, 19); s19 = series(19, 18)
res = {'n20_m19': s20, 'n19_m18': s19}
cum20 = [sum(s20[:d + 1]) for d in range(5)]
cum19 = [sum(s19[:d + 1]) for d in range(5)]
res['dimB20'] = [dimB(20, d) for d in range(5)]
res['dimB19'] = [dimB(19, d) for d in range(5)]
res['M4_profile_semiregular'] = [max(0, dimB(20, d) - cum20[d]) for d in range(5)]
res['rank_M3'] = dimB(20, 3) - cum20[3]
res['rank_M4'] = dimB(20, 4) - cum20[4]
res['R4_profile_semiregular'] = [max(0, dimB(19, d) - cum19[d]) for d in range(5)]
res['rank_R3'] = dimB(19, 3) - cum19[3]
res['rank_R4'] = dimB(19, 4) - cum19[4]
Bp = [0] + [dimB(19, d - 1) for d in range(1, 5)]  # dim B'_{<=d-1}, with B'_{<=-1} = 0
res['T5_W4_dims_by_deg_from_ref'] = [res['R4_profile_semiregular'][d] + Bp[d] for d in range(5)]
res['T5_W4_final_dim'] = res['rank_R4'] + dimB(19, 3)
res['fixture'] = {'M_3': [21 * 19, dimB(20, 3)], 'M_4': [dimB(20, 2) * 19, dimB(20, 4)],
                  "R'_3": [20 * 19, dimB(19, 3)], "R'_4": [dimB(19, 2) * 19, dimB(19, 4)]}
res['trivial_syzygies_M4'] = comb(19, 2) + 19
res['rows_minus_trivial'] = dimB(20, 2) * 19 - res['trivial_syzygies_M4']
res['D5_claims'] = {
  'n20_m19 == [1,20,171,760,1425,-2356]': s20 == [1, 20, 171, 760, 1425, -2356],
  'n19_m18 == [1,19,153,627,969,-2565]': s19 == [1, 19, 153, 627, 969, -2565],
  'rank M_3 == 399': res['rank_M3'] == 399, 'rank M_4 == 3819': res['rank_M4'] == 3819,
  'M_4 profile == [0,0,19,399,3819]': res['M4_profile_semiregular'] == [0, 0, 19, 399, 3819],
  "rank R'_3 == 360": res['rank_R3'] == 360,
  "R'_4 profile == [0,0,18,360,3267]": res['R4_profile_semiregular'] == [0, 0, 18, 360, 3267],
  'T5 final_dim 4427': res['T5_W4_final_dim'] == 4427,
  'T5 dims_by_deg [0,1,38,551,4427]': res['T5_W4_dims_by_deg_from_ref'] == [0, 1, 38, 551, 4427],
  'fixtures': res['fixture'] == {'M_3': [399, 1351], 'M_4': [4009, 6196], "R'_3": [380, 1160], "R'_4": [3629, 5036]},
  'dim B19_{<=3} == 1160': dimB(19, 3) == 1160,
  '4009 - 190 == 3819': res['rows_minus_trivial'] == 3819,
}
res['n17_ref'] = {'series_n18_m17': series(18, 17), 'series_n17_m16': series(17, 16), 'dimB17_3': dimB(17, 3)}
json.dump(res, open(sys.argv[1], 'w'), indent=1)
print(json.dumps(res, indent=1))
