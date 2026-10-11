#!/usr/bin/env python3
from sage.all import *
proof.all(False)  # faster

import re
for l in open('sqisign_parameters.txt'):
    for k in ('p'):
        m = re.search(rf'^\s*{k}\s*=\s*([x0-9a-f]+)', l)
        if m:
            v = ZZ(m.groups()[0], 0)
            globals()[k] = v

f = (p+1).valuation(2)

#choices
tors2val = f
logp = p.bit_length()
#security
default_security_bits = int(ceil(logp / 16)) * 8
security_bits = default_security_bits
# add_parameter_set: explicit security override from parameters.txt
for _l in open('sqisign_parameters.txt'):
    _m = re.search(r'^\s*security\s*=\s*(\d+)', _l)
    if _m:
        security_bits = int(_m.group(1))
if security_bits > default_security_bits:
    import warnings
    warnings.warn(f"security_bits too large ({security_bits} > {default_security_bits}, expect possible failures")
if (security_bits % 8) != 0:
    import warnings
    warnings.warn(f"security_bits {security_bits} is not a multiple of 8, expect possible failures")

globals()['security_bits'] = security_bits
globals()['negligible'] = 2**(-security_bits)
#sizes
globals()['deg_mix'] = next_prime(p * 2**(2*security_bits))
globals()['response_bits'] = ceil(((logp)/2) + (security_bits/4)) + 1
globals()['challenge_bits'] = security_bits
globals()['hash_iterations'] = 1
#quaternion
globals()['add_shift_cst'] = 2 
globals()['hd_margin'] = 2
globals()['prime_cofactor_size'] = logp
bits = ceil(logp/64)*64
globals()['ibz_num_limbs'] = 5*bits//64






__all__ = ['p', 'f', 'security_bits', 'hash_iterations','negligible', 'deg_mix', 'response_bits', 'add_shift_cst',  'add_shift_cst', 'hd_margin', 'prime_cofactor_size', 'ibz_num_limbs' ]

