import json, sys
sys.path.insert(0, ".")
from mpoly import *

mine = json.load(open("indep_tables.json"))
myS4 = {tuple(map(int, k.split(","))): v for k, v in mine["S4"].items()}
myS3 = {tuple(map(int, k.split(","))): v for k, v in mine["S3"].items()}

REPO = "/Volumes/SSD990/crypto-autoresearcher/experiments/EXP-MONO-815525/implementation"
th = json.load(open(REPO + "/s4_monomials.json"))
print("executor gens:", th["gens"], "n terms:", len(th["terms"]))
# executor gens order: x1,x2,x3,x4,A,B ; mine: x1,x2,x3,x4,U,A,B,y1,y2
theirs = {}
for k, v in th["terms"].items():
    m = tuple(map(int, k.split(",")))
    key = (m[0], m[1], m[2], m[3], 0, m[4], m[5], 0, 0)
    theirs[key] = v
print("S_4 tables identical:", theirs == myS4, "| mine", len(myS4), "theirs", len(theirs))
if theirs != myS4:
    d = set(theirs) ^ set(myS4)
    print("  symmetric-difference monomials:", list(d)[:10])
    for k in set(theirs) & set(myS4):
        if theirs[k] != myS4[k]:
            print("  coeff mismatch", k, theirs[k], myS4[k]); break

th3 = json.load(open(REPO + "/s3_monomials.json"))
theirs3 = {}
for k, v in th3["terms"].items():
    m = tuple(map(int, k.split(",")))
    theirs3[(m[0], m[1], m[2], 0, 0, m[3], m[4], 0, 0)] = v
print("S_3 tables identical:", theirs3 == myS3)

# symmetric coefficients c_k from executor
sym = json.load(open(REPO + "/s4_symmetric_coeffs.json"))
print("sym gens:", sym["gens"], "keys:", sorted(sym["coeffs"]))
def ev_sym(tab, e1, e2, e3, A, B):
    t = 0
    for k, co in tab.items():
        m = tuple(map(int, k.split(",")))
        t += co * e1**m[0] * e2**m[1] * e3**m[2] * A**m[3] * B**m[4]
    return t
import random
random.seed(11)
ok4 = ok_all = True
for _ in range(500):
    a,b,c,A_,B_ = (random.randint(-30,30) for _ in range(5))
    e1,e2,e3 = a+b+c, a*b+a*c+b*c, a*b*c
    # my c_4 = S_3^2 with S_3 = A^2-2A e2-4B e1+e2^2-4 e1 e3
    s3 = A_*A_ - 2*A_*e2 - 4*B_*e1 + e2*e2 - 4*e1*e3
    if ev_sym(sym["coeffs"]["4"], e1,e2,e3,A_,B_) != s3*s3: ok4 = False
    # and check every c_k of theirs against MY S_4 evaluated at x1,x2,x3 = a,b,c
    myc = coeff_list(myS4, "x4")
    for k in range(5):
        val = 0
        for m, co in myc[k].items():
            val += co * a**m[0] * b**m[1] * c**m[2] * A_**m[5] * B_**m[6]
        if ev_sym(sym["coeffs"][str(k)], e1,e2,e3,A_,B_) != val: ok_all = False
print("executor c_4(e) == (A^2-2Ae2-4Be1+e2^2-4e1e3)^2 on 500 random pts:", ok4)
print("executor c_k(e) == my S_4's x4-coefficients on 500 random pts, k=0..4:", ok_all)
