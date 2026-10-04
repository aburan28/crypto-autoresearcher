"""Scratch inspection 16: verify run artifacts + validate_ledger.
Not a protocol artifact."""
import json, os, subprocess

RUNS = 'experiments/EXP-ECRANK-41775b/runs'
for d in sorted(os.listdir(RUNS)):
    p = os.path.join(RUNS, d)
    if os.path.isdir(p):
        print(d, '->', sorted(os.listdir(p)))

r3 = json.load(open(os.path.join(RUNS, 'R3-extended-readmission', 'raw-result.json')))
print('\nR3 N A ext:', r3['N_per_H_convention_A_ext'])
print('R3 N B ext:', r3['N_per_H_convention_B_ext'])
print('R3 ratios A:', r3['decade_ratios_A_ext'])
print('R3 ratios B:', r3['decade_ratios_B_ext'])
print('R3 3-dec A:', r3['three_decade_ratio_A_ext_10e4_to_10e7'],
      'B:', r3['three_decade_ratio_B_ext_10e4_to_10e7'])
print('R3 ceiling A/B:', r3['saturation_ceiling_A'], r3['saturation_ceiling_B'])
print('R3 hist:', r3['multiplicity_histogram'], 'max mult:', r3['max_multiplicity'])
print('R3 max h_A/h_B:', r3['max_h_A_observed'], r3['max_h_B_observed'])
print('R3 n8:', r3['n8_band']['report'][:80], 'vacuous:', r3['n8_band']['vacuous'])
print('R3 P2:', {k: v for k, v in r3['precondition_P2'].items() if 'note' not in k and 'shortfall' not in k})
c6 = r3['c6_certificate_recomputation']
print('C6 rows certified:', len(c6['per_instance']), 'exhaustion:', c6['exhaustion'])
print('C6 all match:', all(x.get('matches_committed') for x in c6['per_instance']))
r2 = json.load(open(os.path.join(RUNS, 'R2-structural-trace', 'raw-result.json')))
print('\nR2 adjudication:', r2['adjudication']['p1_adjudication'])
print('R2 dyn all meta identical:', all(x['meta_identical'] for x in r2['dynamic']))
print('R2 dyn all roots identical:', all(x['root_set_union_identical'] for x in r2['dynamic']))
r1 = json.load(open(os.path.join(RUNS, 'R1-calibration', 'raw-result.json')))
print('\nR1 pass:', r1['calibration_pass'])
r4 = json.load(open(os.path.join(RUNS, 'R4-density-derivation', 'raw-result.json')))
print('R4 control outcome:', r4['proves_too_much_control']['p5_outcome'][:80])
r5 = json.load(open(os.path.join(RUNS, 'R5-replay', 'raw-result.json')))
print('R5 empty:', r5['replay']['replay_diff_empty'])
