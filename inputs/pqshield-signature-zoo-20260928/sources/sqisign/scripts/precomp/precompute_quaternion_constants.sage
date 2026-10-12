#!/usr/bin/env sage
proof.all(False)  # faster

################################################################

from parameters import p, negligible, hd_margin, add_shift_cst, security_bits, deg_mix
negl = negligible

################################################################

logp = p.nbits()  # == ceil(log(p,2)) for a prime; the latter fails at 256-bit precision for near-2^n p
loglogp = ceil(log(logp,2))
tors2val = (p+1).valuation(2)

defs = dict()

# Equivalent ideal data
small = ceil(log(negl, 2) / -1)
assert 2**-small <= negl

add_shift = ceil((- small / log(1-1/(add_shift_cst * logp),2))**(0.25) - 1)
assert (1 - 1/(add_shift_cst * logp)) ** ((add_shift + 1)**4) <= negl

defs['QUAT_primality_num_iter'] = ceil(-log(negl, 4))

# Equivalent ideal data
defs['QUAT_equiv_bound_coeff'] = add_shift


#qlapoty constants
defs['QUAT_qlapoty_used_power_of_two'] = tors2val-hd_margin

# Representative ideal-norm scales on the signing path, in bits.
# These describe the magnitudes keygen/sign actually produce, and are what the quaternion tests
# and the CT benchmarks must feed the constant-time reduction entry points. All three sit above
#   degree: n(SEC_DEGREE) = n(COM_DEGREE), the keygen/commit ideal (keygen.c:40, sign.c:19).
#   equiv:  the sqrt(p)*QUAT_equiv_bound_coeff^2 scale every ideal is reduced to by
#           quat_ideal_small_equivalent_coprime; the +15 is a measured, not yet based in
#           QUAT_equiv_bound_coeff. 
#   prod:   bits(2N) of the two-ideal product at the parallelogram site (ideal.c).
defs['QUAT_degree_norm_bits'] = deg_mix.bit_length()
defs['QUAT_equiv_norm_bits'] = logp//2 + 15
defs['QUAT_prod_norm_bits'] = 2 * (logp//2 + 15)

# Per-level primitives for the lattice config, src/quaternion/ref/lvlx/lll/lll_config.h.
# p and its integer square root: the Z[i] form's second coordinate is pre-scaled by s = isqrt(p),
# so that |z1|^2 + s^2*|z2|^2 stands in for the quaternion norm |z1|^2 + p*|z2|^2. Consumed by
# lll_config.h (QUAT_P_BITS -> FP_PRIME) and gaussian_xgcd.c (the sqrt weight).
sqrt_p = isqrt(p)
assert sqrt_p**2 <= p < (sqrt_p + 1)**2

defs['QUAT_P_BITS'] = logp
defs['QUAT_SQRT_P_BITS'] = ZZ(sqrt_p).nbits()

# Emitted as quoted lowercase hex without a 0x prefix -- ibz_set_from_str(..., 16) parses this.
hex_defs = dict()
hex_defs['QUAT_P_HEX'] = p
hex_defs['QUAT_SQRT_P_HEX'] = sqrt_p


################################################################

with open('include/quaternion_constants.h','w') as hfile:
    print(f'#include <quaternion.h>', file=hfile)
    print(f'#include <stddef.h>', file=hfile)
    print(f'#include <stdint.h>', file=hfile)
    for k,v in defs.items():
        v = ZZ(v)
        print(f'#define {k} {v}', file=hfile)
    for k,v in hex_defs.items():
        print(f'#define {k} "{int(v):x}"', file=hfile)


