"""J2 step 0b: the CLEAN structural criterion.
n = q n' + r  =>  n' - r = (q+1) n' - n.  So j := (n'-r)/(q+1) is an integer
iff (q+1) | n, and then j = n' - n/(q+1).
Consequence: a cell can host a degenerate candidate ONLY IF (q+1) | n."""
def crit(n, npr):
    q, r = divmod(n, npr)
    assert npr - r == (q+1)*npr - n
    ok = (n % (q+1) == 0)
    j = npr - n//(q+1) if ok else None
    return q, r, ok, j

# check the identity on a wide range
for n in range(1, 400):
    for npr in range(1, 400):
        crit(n, npr)
print("identity n'-r = (q+1)n' - n verified for all 1<=n,n'<=399")

PRIMES=[7,11,13,17,19,23,29,31]
allcells=[(11,6),(13,7),(7,3),(11,4),(13,5),(131,33),(131,44),(131,66),(23,12)]
allcells+= [(n,npr) for n in PRIMES for npr in range(2,16) if npr<n and n%npr]
bad=[]
for (n,npr) in set(allcells):
    q,r,ok,j = crit(n,npr)
    if ok: bad.append((n,npr,q,r,j))
print("experiment cells with (q+1)|n :", bad)
print()
# general statement: n prime, 2<=n'<n  =>  2 <= q+1 < n  =>  (q+1) does not divide n
viol=[]
for n in [p for p in range(3,200) if all(p%k for k in range(2,int(p**.5)+1))]:
    for npr in range(2,n):
        q,r,ok,j=crit(n,npr)
        if not (2 <= q+1 < n): viol.append(("range",n,npr,q))
        if ok: viol.append(("div",n,npr,q))
print("counterexamples to 'n prime, 2<=n'<n => 2<=q+1<n and (q+1) never divides n':", viol)
print()
# the ONE cell in the contract with composite n is the r=0 control C1 (12,6)
for (n,npr) in [(12,6),(3,2),(4,3)]:
    q,r,ok,j=crit(n,npr)
    print("(n,n')=(%d,%d): q=%d r=%d (q+1)|n=%s j=%s  -> degenerate d must be 2^j=%s"
          % (n,npr,q,r,ok,j, (1<<j) if ok and j and j>=1 else "n/a"))
