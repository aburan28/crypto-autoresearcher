# Raw symbolic checks

Let (m\ge2), (F_m=\{a=x^m,b=x^m+x\}), and (R=k[x]).

1. (b-a=x), so (x\in(F_m)). Also (a=x\cdot x^{m-1}) and (b=x(x^{m-1}+1)), so ((F_m)\subseteq(x)). Hence ((F_m)=(x)).
2. If (i<m), both (a) and (b) exceed the degree cap. Starting from no admitted generator, the smallest vector space closed under permitted multiplication is (0).
3. If (i\ge m), (a,b\in V_{F_m,i}), so (x=b-a\in V_{F_m,i}). For each (q\in R) with \(\deg(xq)\le i\), closure gives (xq\in V_{F_m,i}). Linearity gives every element of ((x)\cap R_{\le i}). All closure operations preserve ideal membership and the cap, proving the reverse inclusion.
4. For (i<m), (x\notin V_{F_m,i}); at (i=m), (x\in V_{F_m,m}). Thus (d_x=m).
5. If (d<m), the requirement for (f=x) tests membership at \(\max(d,\deg x)<m\), which fails. If (d=m), every (f\in(x)) belongs to (V_{F_m,\max(m,\deg f)}). Hence (d_{F_m}=m).
6. Substitute (m=D) and (m=D+1). Both profiles through (D-1) are zero, yet the exact cutoffs are (D) and (D+1). More generally, any (m\ge D) gives the same truncated profile with cutoff (m).

No code or experimental run was used for these checks.
