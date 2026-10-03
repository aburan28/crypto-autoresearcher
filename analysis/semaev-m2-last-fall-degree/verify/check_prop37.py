"""Check of Proposition 3.7, step (b), at t = 3 (theorem-dossier.md).

For every assignment sigma of the coordinates of x2 and x3, check that the
restricted system F_sigma has degree <= 2, and find the least D <= 3 with
1 in W_D(F_sigma). The proposition claims D <= 3 for every sigma.
usage (from code/, which has ./lfdclose2): check_prop37.py inst.sys n k
where inst.sys comes from gen3.py, e.g. gen3.py 13 5 1 77 rand unsat c3tiny."""
import subprocess, sys, collections
path, n, k = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
tok = open(path).read().split(); N, npol = int(tok[0]), int(tok[1]); p = 2; polys = []
for _ in range(npol):
    c = int(tok[p]); p += 1; polys.append([int(x, 16) for x in tok[p:p + c]]); p += c
fixvars = list(range(n + k, n + 3 * k))               # coordinates of X2 and X3
keep = [v for v in range(N) if v not in fixvars]; newidx = {v: i for i, v in enumerate(keep)}
fixmask = sum(1 << v for v in fixvars)
hist = collections.Counter(); maxdeg = 0
for sigma in range(1 << len(fixvars)):
    onemask = sum(1 << v for i, v in enumerate(fixvars) if (sigma >> i) & 1)
    res = []
    for poly in polys:
        acc = {}
        for m in poly:
            if (m & fixmask) & ~onemask: continue
            r = m & ~fixmask; nm = 0
            while r:
                low = r & -r; v = low.bit_length() - 1; r ^= low; nm |= 1 << newidx[v]
            acc[nm] = acc.get(nm, 0) ^ 1
        res.append(sorted(m for m, c in acc.items() if c))
    maxdeg = max([maxdeg] + [bin(m).count("1") for q in res for m in q])
    txt = f"{len(keep)} {len(res)}\n" + "".join(str(len(q)) + " " + " ".join(format(m, 'x') for m in q) + "\n" for q in res)
    dmin = None
    for D in (1, 2, 3):
        out = subprocess.run(["./lfdclose2", str(D)], input=txt, capture_output=True, text=True).stdout
        if f"W{D}_one 1" in out: dmin = D; break
    hist[dmin] += 1
print(f"assignments {1 << len(fixvars)}; max degree of restricted systems {maxdeg}; least D with 1 in W_D: {dict(hist)}")
