"""Scratch inspection 15: debug calibration families (v2 constructors).
Not a protocol artifact."""
import sys
from fractions import Fraction as Fr
sys.path.insert(0, 'experiments/EXP-ECRANK-41775b/source')
import run_package_v2 as RP

v, f1, f2 = RP.run_calibration()
print(json.dumps if False else '')
import json
print('f1 A:', v['family_1']['N_per_H_convention_A'])
print('f1 B:', v['family_1']['N_per_H_convention_B'])
print('f1 checks:', v['family_1']['exact_checks'])
print('f1 ratios A:', v['family_1']['decade_ratios_A'])
print('f1 ratios B:', v['family_1']['decade_ratios_B'])
print('f1 two-dec A:', v['family_1']['two_decade_ratio_A'],
      'B:', v['family_1']['two_decade_ratio_B'])
print('f2 per-dec A:', v['family_2']['per_decade_counts_A'])
print('f2 per-dec B:', v['family_2']['per_decade_counts_B'])
print('f2 checks:', v['family_2']['exact_checks'])
# diagnose: heights of first few roots
for tp in f1[:3]:
    print('tuple', tp['tuple_index'], 'low t', tp['root_low']['t'],
          'high t', tp['root_high']['t'])
insts = RP.family_instances(f1)
for (r, t) in insts[:4]:
    print('inst t', t, 'h_A', RP.h_A_of(r), 'h_B', RP.h_B_of(t))
