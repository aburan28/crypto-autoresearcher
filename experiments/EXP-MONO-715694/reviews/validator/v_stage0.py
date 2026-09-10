# Independent, from-scratch re-verification of Stage 0 / Stage 0b.
# Deliberately does NOT import experiments/EXP-MONO-715694/implementation/run_experiment.py.
import itertools, json, sys
from collections import Counter

def cycle_type(perm):
    # fresh implementation, different style (functional, using sets) from the Executor's trace loop
    n = len(perm)
    seen = set()
    lens = []
    for i in range(n):
        if i in seen:
            continue
        j = i
        c = 0
        while j not in seen:
            seen.add(j)
            j = perm[j]
            c += 1
        lens.append(c)
    lens.sort()
    return tuple(lens)

LABELS = {(1,1,1,1):"identity",(1,1,2):"transposition",(2,2):"double_transposition",(1,3):"three_cycle",(4,):"four_cycle"}
ORDER = ["identity","transposition","double_transposition","three_cycle","four_cycle"]

def parity(perm):
    n=len(perm)
    inv=0
    for i in range(n):
        for j in range(i+1,n):
            if perm[i]>perm[j]:
                inv+=1
    return inv%2

s4 = Counter()
a4 = Counter()
for p in itertools.permutations(range(4)):
    ct = LABELS[cycle_type(p)]
    s4[ct]+=1
    if parity(p)==0:
        a4[ct]+=1

s4vec = [s4[c] for c in ORDER]
a4vec = [a4[c] for c in ORDER]
print("S4 vec:", s4vec, "sum:", sum(s4vec))
print("A4 vec:", a4vec, "sum:", sum(a4vec))
assert s4vec == [1,6,3,8,6], s4vec
assert a4vec == [1,0,3,8,0], a4vec
print("STAGE0 MATCH: OK")

# Stage 0b: independently re-tabulate N1 exhaustive real data for both runs
def tabulate_n1(path):
    counts = Counter()
    total=0
    excluded=0
    threecycles=0
    with open(path) as f:
        for line in f:
            line=line.strip()
            if not line: continue
            total+=1
            rec=json.loads(line)
            if rec.get("class") is None:
                excluded+=1
                continue
            perm = rec["perm"]
            ct = LABELS[cycle_type(perm)]
            if ct=="three_cycle":
                threecycles+=1
            counts[ct]+=1
    return total, excluded, counts, threecycles

repo = sys.argv[1] if len(sys.argv)>1 else "."
p1 = repo+"/experiments/EXP-MONO-a20e48/runs/RUN-MONO-a20e48-1/per_base_point_log/N1_k1_exhaustive.jsonl"
p2 = repo+"/experiments/EXP-MONO-a20e48/runs/RUN-MONO-a20e48-2/per_base_point_log/N1_k1_exhaustive.jsonl"

for label, p in [("run1",p1),("run2",p2)]:
    total, excluded, counts, tc = tabulate_n1(p)
    nonram = total-excluded
    vec = [counts[c] for c in ORDER]
    print(label, "total_rows=",total, "excluded=",excluded, "non_ramified=",nonram, "vec=",vec, "3cycles=",tc)
    assert tc == 0, "3-cycle found!"
    assert nonram == 44310, nonram
    assert vec == [6105, 11100, 16050, 0, 11055], vec

print("STAGE0B MATCH: OK (both runs, exact counts match Executor's reported [6105, 11100, 16050, 0, 11055])")
