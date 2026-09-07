import sys
sys.path.insert(0, "experiments/EXP-ECDLP-bbb42f")
from driver.ecc import point_add, OpCounter

p = 100003
a = 5
P1 = (12345, None)
# find real points
from driver.ecc import random_point
import random
rng = random.Random(1)
P1 = random_point(a, 7, p, rng)
P2 = random_point(a, 7, p, rng)
while P2[0] == P1[0]:
    P2 = random_point(a, 7, p, rng)

ctr = OpCounter()
point_add(P1, P2, a, p, ctr)
print("general add: mults=", ctr.field_mults, "invs=", ctr.field_invs)

ctr2 = OpCounter()
point_add(P1, P1, a, p, ctr2)
print("doubling: mults=", ctr2.field_mults, "invs=", ctr2.field_invs)
