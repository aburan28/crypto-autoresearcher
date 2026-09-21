"""J2 step 0: is `degenerate_candidates: 0` STRUCTURAL rather than observed?
Enumerate every (n, n') cell of EXP-QSP-33b442 and ask whether ANY d in the
cell's declared degree range can satisfy d = 2^j with j(q+1) = n'-r."""
PRIMES = [7, 11, 13, 17, 19, 23, 29, 31]

cells = []   # (stage, n, n', degree range)
for (n, npr) in [(11,6),(13,7),(7,3),(11,4),(13,5)]:
    cells.append(("S1", n, npr, list(range(2,8))))
for (n, npr) in [(11,6),(13,7)]:
    cells.append(("S1b", n, npr, [3,5,7]))
s2 = []
for n in PRIMES:
    for npr in range(2,16):
        if npr >= n or n % npr == 0: continue
        dmax = min(8, (1<<npr)-1)
        s2.append(("S2", n, npr, list(range(2, dmax+1))))
cells += s2
for npr in (33,44,66):
    cells.append(("S3", 131, npr, list(range(3,8))))
for (n,npr) in [(11,6),(23,12)]:
    cells.append(("S4", n, npr, list(range(1,4))))

print("stage-2 (n,n') cells:", len(s2), " total cells:", len(cells))

def jsol(n, npr):
    q, r = divmod(n, npr)
    m = npr - r
    if m % (q+1): return None, q, r, m
    return m // (q+1), q, r, m

possible = []
rows = []
for (st, n, npr, drange) in cells:
    j, q, r, m = jsol(n, npr)
    ok = (j is not None) and (1<<j) in drange and j >= 1
    rows.append((st, n, npr, q, r, m, q+1, j, ok))
    if ok: possible.append((st,n,npr,j))
print("cells admitting ANY degenerate candidate:", len(possible), possible)
print()
print("%-4s %4s %4s %3s %4s %6s %6s %6s %s" % ("st","n","n'","q","r","n'-r","q+1","j","d=2^j in range?"))
seen=set()
for row in rows:
    key=(row[1],row[2])
    if key in seen: continue
    seen.add(key)
    st,n,npr,q,r,m,q1,j,ok = row
    print("%-4s %4d %4d %3d %4d %6d %6d %6s %s" % (st,n,npr,q,r,m,q1, "-" if j is None else j, ok))
