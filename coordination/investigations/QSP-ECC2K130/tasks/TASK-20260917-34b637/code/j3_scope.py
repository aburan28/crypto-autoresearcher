"""J3(a): the precise scope of  beta > 1/2.

beta >= n/((q+1)n') = n/(n+n'-r) holds for EVERY n' (the identity (q+1)n' =
n + (n'-r) does not need q >= 1).  The final step  n/(n+n'-r) > 1/2  is
equivalent to  n + r > n'.  This script decides that inequality over a large
parameter range and reports exactly where it fails.
"""
fail = []; ok = 0
for n in range(2, 140):
    for npr in range(2, 400):
        if npr == n or n % npr == 0:   # n' | n is Diem's family, excluded
            continue
        q, r = divmod(n, npr)
        assert (q + 1) * npr == n + (npr - r), "identity (q+1)n' = n + (n'-r) FAILED"
        lower = (n, n + npr - r)                     # n/(n+n'-r) as a fraction
        gt_half = 2 * lower[0] > lower[1]            # > 1/2 ?
        if gt_half: ok += 1
        else: fail.append((n, npr, q, r, lower, 2*lower[0] == lower[1]))
print("identity (q+1)n' = n + (n'-r) verified on", ok + len(fail), "(n,n') pairs with n' not dividing n")
print("pairs where n/(n+n'-r) >  1/2 :", ok)
print("pairs where n/(n+n'-r) <= 1/2 :", len(fail))
print("every failing pair has q = 0 ?:", all(f[2] == 0 for f in fail))
print("every failing pair has n' >= 2n ?:", all(f[1] >= 2*f[0] for f in fail))
print("min n' among failing pairs, per n (first few):",
      [(n, min(f[1] for f in fail if f[0] == n)) for n in range(2, 8)])
print("equality n/(n+n'-r) == 1/2 happens exactly at n' == 2n ?:",
      all((f[5]) == (f[1] == 2*f[0]) for f in fail))
print()
print("So: beta > 1/2 is derivable exactly when q >= 1, i.e. n' < n")
print("    (n' | n is already excluded, so n' <= n and n' != n give n' < n).")
print("    At n' = 2n the bound is exactly 1/2; at n' > 2n it is below 1/2.")
print()
print("WHY n' > n CANNOT ARISE UNDER (B)'s OWN HYPOTHESIS:")
print("    (B) assumes N_K(L) = p^{n'}.  But N_K(L) counts DISTINCT roots in K,")
print("    so N_K(L) <= |K| = p^n.  Hence p^{n'} <= p^n, i.e. n' <= n; with")
print("    n' not dividing n this gives n' < n and therefore q >= 1.")
print("    That step appears NOWHERE in H-QSP-5540d7 (A), (B) or (E).")
