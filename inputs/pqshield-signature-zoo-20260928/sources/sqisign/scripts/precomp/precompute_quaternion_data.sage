#!/usr/bin/env sage
proof.all(False)  # faster



from parameters import p, security_bits, response_bits
from cformat import Ibz, Object, ObjectFormatter

from sage.algebras.quatalg.quaternion_algebra import basis_for_quaternion_lattice
bfql = lambda els: basis_for_quaternion_lattice(els, reverse=True)

Quat1, (i,j,k) = QuaternionAlgebra(-1, -p).objgens()
assert Quat1.discriminant() == p         # ramifies correctly

O0mat = matrix([list(g) for g in [Quat1(1), i, (i+j)/2, (1+k)/2]])
O0 = Quat1.quaternion_order(list(O0mat))

# Prime cofactor for random ideal given norm
def log_prob(n,logM):
    
    return round(n * log(1 - 1 / (2 * logM), 2))

bits_m = p.nbits() - response_bits + 2 

# print(log_prob(floor(2**(response_bits + bits_m) / p), 2**(response_bits + bits_m)))

while (round(log_prob(floor(2**(response_bits + bits_m) / p), response_bits + bits_m)) > (-security_bits)) : 
    bits_m =  bits_m + 1


prime_cofactor = next_prime(2^bits_m)

algobj = [Ibz(p)]


# basis (columns)
# ibz_mat_4x4_t is a struct wrapping the array: one extra brace level
O0_obj = [Ibz(O0mat.denominator()), [[[Ibz(v) for v in vs] for vs in O0mat.transpose()*O0mat.denominator()]]]
 

objs = ObjectFormatter([
        Object('ibz_t', 'QUAT_prime_cofactor', Ibz(prime_cofactor)),
        Object('quat_alg_t', 'QUATALG_PINFTY', algobj),
        Object('quat_lattice_t', 'MAXORD_O0', O0_obj),
    ])

with open('include/quaternion_data.h','w') as hfile:
    with open('quaternion_data.c','w') as cfile:
        print(f'#include <quaternion.h>', file=hfile)
        print(f'#include <stddef.h>', file=cfile)
        print(f'#include <stdint.h>', file=cfile)
        print(f'#include <quaternion_data.h>', file=cfile)

        objs.header(file=hfile)
        objs.implementation(file=cfile)

