import sys
sys.path.insert(0,'/home/user/wt/lean')
from harness.endosweep import frobenius as FR
S='/tmp/claude-0/-home-user/6ef12e21-c055-593f-aa44-2a41ea293670/scratchpad/review/R3/'
lv = [(q,t,m,FR.lucas_V(q,t,m)) for (q,t) in [(2,1),(2,-1),(4,-3),(3,1),(7,-2)] for m in (0,1,2,5,13,19)]
q4 = [(m, (4**m+1-FR.lucas_V(4,-3,m))//8, (2**m+1-FR.lucas_V(2,1,m))//2, (2**m+1-FR.lucas_V(2,-1,m))//4) for m in (2,3,5,7,11,13,17,19)]
lv_lean = ", ".join(f"(({q} : Int), ({t} : Int), ({m} : Nat), ({v} : Int))" for q,t,m,v in lv)
q4_lean = ", ".join(f"(({m} : Nat), ({a} : Int), ({b} : Int), ({c} : Int))" for m,a,b,c in q4)
src = f"""import CryptoResearch.Endosweep.FrobeniusSplit
open CryptoResearch.Endosweep
-- q4_split: hypotheses satisfiable at m = 5
#check FrobeniusSplit.q4_split 5 (by decide) (by decide)
#check FrobeniusSplit.q4_not_prime 7 (by decide) (by decide)
def lvCases : List (Int × Int × Nat × Int) := [{lv_lean}]
#eval lvCases.all fun (q, t, m, v) => FrobeniusSplit.V t q m == v
def q4Cases : List (Nat × Int × Int × Int) := [{q4_lean}]
#eval q4Cases.all fun (m, a, b, c) => FrobeniusSplit.n4 m == a && FrobeniusSplit.na m == b && FrobeniusSplit.nb m == c
#eval q4Cases
"""
open(S+'r3_C.lean','w').write(src)
print(q4)
