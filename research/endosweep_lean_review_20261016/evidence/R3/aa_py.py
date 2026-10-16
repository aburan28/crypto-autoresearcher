import sys, random
sys.path.insert(0, '/home/user/wt/lean')
from harness.endosweep import alphaadic as AA
random.seed(7)
pts = [(0,0),(1,0),(-1,0),(7,0),(-7,0),(88,0),(-88,0),(87,0),(-2,2),(3,-5),(100,1),(-1000,37),(123456,-7890),(-98765,4321),(5,1),(-50,-50),(175,0),(52,0),(53,0),(-53,0)]
pts += [(random.randint(-10**6,10**6), random.randint(-10**4,10**4)) for _ in range(30)]
print(len(pts))
out = []
for (D, al) in [(-619,(4,1)),(-339,(4,1)),(-339,(1,4))]:
    rule = AA.int_rule(D, al)
    for z in pts:
        dg = rule.digit(z)
        q = AA.exact_div(D, (z[0]-dg[0], z[1]-dg[1]), al)
        out.append(f"{D} {al} {z} {dg} {q}")
open('/tmp/claude-0/-home-user/6ef12e21-c055-593f-aa44-2a41ea293670/scratchpad/review/R3/aa_py.out','w').write("\n".join(out)+"\n")
print("pts", pts)
# Python full expansions of some sample orbits to compare iteration counts
for (D, al) in [(-619,(4,1)),(-339,(4,1))]:
    rule = AA.int_rule(D, al)
    print(D, [len(AA.expand(rule, z)) for z in pts[:12]])
rule = AA.int_rule(-339,(1,4))
try:
    AA.expand(rule,(-2,2),max_len=50)
except RuntimeError as e: print('1+4w (-2,2):', e)
