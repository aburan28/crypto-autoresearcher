#!/usr/bin/env python3
# Emit fp_generic_params.h for p = c*2^t - 1 (see fp_generic.h).
import sys

c, t = int(sys.argv[1]), int(sys.argv[2])
p = c * (1 << t) - 1
bits = p.bit_length()
N = (bits + 63) // 64
spare = 64 * N - bits
assert c % 2 == 1 and c < 2**31, "need odd c < 2^31"
assert spare >= 4, "need >= 4 spare bits (asm domain invariant)"
assert t >= 64 * (N - 1)

R = (1 << (64 * N)) % p
def limbs(v):
    return ", ".join("0x%016xULL" % ((v >> (64 * i)) & (2**64 - 1)) for i in range(N))

print("#ifndef FP_GENERIC_PARAMS_H")
print("#define FP_GENERIC_PARAMS_H")
print("#define FPG_N %d" % N)
print("#define FPG_BITS %d" % bits)
print("#define FPG_C %dULL" % c)
print("#define FPG_T %d" % t)
print("#define FPG_P_INIT { %s }" % limbs(p))
print("#define FPG_ONE_INIT { %s }" % limbs(R % p))
print("#define FPG_R2_INIT { %s }" % limbs((R * R) % p))
print("#define FPG_TWO_INV_INIT { %s }" % limbs((pow(2, -1, p) * R) % p))
print("#define FPG_THREE_INV_INIT { %s }" % limbs((pow(3, -1, p) * R) % p))
print("#endif")
