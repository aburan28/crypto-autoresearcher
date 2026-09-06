import sys
sys.path.insert(0, "experiments/EXP-ECDLP-bbb42f")
from driver.predicates import embedding_degree
import random

def brute_order(p, N):
    x = p % N
    o = 1
    cur = x
    while cur != 1:
        cur = (cur * x) % N
        o += 1
    return o

random.seed(7)
fails = 0
for _ in range(50):
    N = random.choice([13, 17, 19, 23, 29, 31, 97, 101, 103, 997, 1009, 1013])
    p = random.randrange(2, N)
    import math
    if math.gcd(p, N) != 1:
        continue
    got = embedding_degree(N, p)
    want = brute_order(p, N)
    if got != want:
        fails += 1
        print("MISMATCH", N, p, got, want)
print("fails=", fails)
