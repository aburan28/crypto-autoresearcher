# Proposed successor: common-atom shifted covers

29 October2026. Derived algebra and a software interface, not a new scientific
collector run, shift search or claimed ECDLP improvement. Sources checked first:
the original Prym `relations.py` and `independent.py`, existing Context.pi2 and
cubic construction, the fixed B1 design, and PKM2016 sections3.1–3.2. All are
internal/retrieved; no novelty claim is made. The audit-curve skill's distinction
between a map and a subgroup/isogeny certificate was consulted; this is not a
security verdict or an elliptic-isogeny construction.

For the same nonsingular E: y²=u³+a*u+b over a certified field of characteristic
greater than3, put f(u)=u³+a*u+b. The genus-two frame

```
C_h: y²=f(x²+h)=x⁶+3h*x⁴+(3h²+a)*x²+(h³+a*h+b)
pi1(x,y)=(x²+h,y)
c4=3h, c2=3h²+a, c0=f(h)
E2_h: V²=U³+c2*U²+(c4*c0)*U+c0²
pi2(x,y)=(c0/x²,c0*y/x³)       for x != 0
pi2(0,y)=infinity
```

The two displayed point identities follow directly by substitution. E remains
exactly the original elliptic curve. C_h is smooth when E is smooth and c0!=0:
a repeated root of f(x²+h) with x!=0 would give a repeated root of f, and x=0
can be a root only when c0=0. The software refuses that degeneration. No
Jacobian decomposition certificate, scalar eigenvalue, rational subgroup
transport or attack advantage is inferred from these identities. In particular
E2_h is not asserted to be isogenous to E.

`cover_frames.ShiftedCover` implements both affine maps and every rational
lift of an existing E point, including the single x=0 deck lift. The h=0
coefficients agree with the historical implementation. Fixed p101 software
controls verify both quotient equations and all rational affine lifts for
h=0,1,2,3. They test no h on the retained p4099 curves. The probable-prime guard
does not replace external field/order certificates beyond its documented
deterministic range.

For an existing E atom F_i=(u_i,y_i), rational cover lifts exist exactly when
u_i-h is a square or zero. Thus the prospective common-atom set is

```
H_B = {h in Fp : f(h)!=0 and every u_i-h is a square or zero}.
```

A separate frozen finite survey can enumerate all h in public order for each
original base, retain every membership rejection and source-lift count, and
record H_B completely. h=0 is the exact historical control. It must not search
for favourable relation yields while choosing h. If another frame is admissible,
a later paired collector should hold E, signed atoms, original log columns,
source order, cubic interpolation and pole/residual/sign verification fixed.
The x⁴ coefficient and the auxiliary quotient must both change correctly;
silently reusing the old zero-x⁴ formula would be an implementation error.

All field/membership setup, failed shifts, source misses, interpolation,
elimination and verification stay charged. If H_B contains only0, that closes
only the all-current-atoms survey on the exact fixtures. A declared subset
comparison or a different function space would be separate work; it must not
silently enlarge a factor base or count new unknowns as information.

No survey or shifted-cover collector was executed in this iteration. The
database and B1 report preserve that boundary, with old and new finite results
separate from this proposed successor.
