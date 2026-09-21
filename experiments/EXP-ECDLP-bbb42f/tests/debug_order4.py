import sys
sys.path.insert(0, "experiments/EXP-ECDLP-bbb42f")
from driver.ecc import scalar_mult, point_add, point_neg

p, a, b = 97, 91, 67
P = (55, 57)

L = 98
m = 7
aa = -2

negQ_base = point_neg(scalar_mult(L, P, a, p), p)
print("L*P =", scalar_mult(L, P, a, p))
print("negQ_base = -(L*P) =", negQ_base)

am = aa * m
print("aa*m =", am)
s1 = scalar_mult(am, P, a, p)
print("scalar_mult(am, P) [am negative] =", s1)
shift = point_neg(s1, p)
print("shift = -scalar_mult(am,P) =", shift)

target = point_add(negQ_base, shift, a, p)
print("target = negQ_base + shift =", target)

# cross check via direct definition: want -L*P + (-am)*P should equal -(L+am)*P
direct = point_neg(scalar_mult(L + am, P, a, p), p)
print("direct -(L+am)*P =", direct, " L+am=", L+am)
