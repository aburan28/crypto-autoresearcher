"""V1(2) addendum: check the CryptoMiniSat model (v-lines of logs/cms_xor_n19l6-19-U.out)
against the CNF-XOR file it was run on (Xn19l6-19-U.dimacs), clause by clause.
The .anf and the .dimacs are different encodings with different variable numbering
beyond the 18 core bits, so the CMS model is checked on its own file."""
import sys

RUN = "/workspace/experiments/EXP-ICPERF-66fd51/runs/RUN-ICPERF-305ca3"
BENCH = "/workspace/inputs/TRIMOSKA-ECICB-2024/upstream/benchmarks"

inst = sys.argv[1] if len(sys.argv) > 1 else "n19l6-19-U"
lits = []
for ln in open(f"{RUN}/logs/cms_xor_{inst}.out"):
    if ln.startswith("v "):
        lits += [int(t) for t in ln[2:].split()]
model = {abs(t): t > 0 for t in lits if t != 0}

lines = open(f"{BENCH}/X{inst}.dimacs").read().strip().split("\n")
hdr = lines[0].split()
nv, nc = int(hdr[2]), int(hdr[3])
assert len(model) == nv, (len(model), nv)
n_or = n_xor = 0
unsat = []
for k, ln in enumerate(lines[1:]):
    toks = ln.split()
    if toks[0] == "x":
        n_xor += 1
        v = 0
        for t in toks[1:]:
            t = int(t)
            if t == 0:
                break
            val = model[abs(t)]
            if t < 0:
                val = not val
            v ^= int(val)
        if v != 1:
            unsat.append(k)
    else:
        n_or += 1
        sat = False
        for t in toks:
            t = int(t)
            if t == 0:
                break
            val = model[abs(t)]
            if t < 0:
                val = not val
            sat |= val
        if not sat:
            unsat.append(k)
print(f"{inst}: {nv} vars, {nc} clauses ({n_or} OR, {n_xor} XOR); model literals {len(model)}; unsatisfied clauses = {len(unsat)}")
core = "".join("1" if model[i] else "0" for i in range(1, 19))
print(f"first 18 vars of CMS model: {core[:6]} {core[6:12]} {core[12:18]}")
