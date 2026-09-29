"""Scratch inspection 7: find the R12 coset (read-only). Not a protocol artifact."""
import sys
sys.path.insert(0, 'experiments/EXP-ECRANK-73275e/source')
import ecrank_engine as E

cosets = E.eligible_cosets()
print('n cosets:', len(cosets))
target_V = sorted([0, 1, 14, 15, 38, 39, 40, 41])
cands = [c for c in cosets if sorted(c['V']) == target_V]
print('cosets with V == target:', len(cands))
for c in cands:
    print('m0', c['m0'], 'members', c['members'],
          'values', sorted(E.class_value(m) for m in c['members']))
# reproduce the R12 coset choice: rng_c = random.Random(760906); cosets[rng_c.randrange(len(cosets))]
import random
rng_c = random.Random(760906)
c = cosets[rng_c.randrange(len(cosets))]
print('R12 choice:', sorted(c['V']), 'm0', c['m0'],
      'values', sorted(E.class_value(m) for m in c['members']))
