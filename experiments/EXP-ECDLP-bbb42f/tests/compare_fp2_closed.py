import sys
sys.path.insert(0, "experiments/EXP-ECDLP-bbb42f")
from driver.isogeny3 import _raw_push_point_3

p, a, b, x0 = 1009, 134, 29, 273
pts = [(331, 91), (970, 945), (154, 996), (404, 738), (666, 794)]
oracle = [(870, 750), (1004, 948), (823, 613), (775, 180), (429, 579)]

for P, exp in zip(pts, oracle):
    got = _raw_push_point_3(P, a, p, x0)
    print(P, "closed=", got, " oracle=", exp, " match=", got == exp)
