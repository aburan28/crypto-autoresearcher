\\ CM route to a conductor floor of a Koblitz crater E: y^2+xy=x^3+a x^2+1 over F_2^m. For a prime F | f_pi, the F-floor is
\\ the set of curves in the isogeny class with End = Z + F*O_K, K = Q(sqrt(-7)); their j-invariants are the roots mod 2 of the
\\ class polynomial for D = -7 F^2, all of which lie in F_2^m. PARI polclass invariant 1 is Weber f (allowed since
\\ D = 1 mod 8 and 3 does not divide D); mod 2, (f^24-16)^3 = j f^24 gives j = f^48, so b = 1/j = f^-48.
\\ Checks: number of roots = h(D); each j has a model with #E = N; Galois orbits; level by horizontal S-isogeny cycles:
\\ their length must equal ord[l_S] in Cl(D) (crater: 1), and every visited curve must be in the root set.
\\ set before reading: m, a, F, S, NSAMP, OUT
\\ optionally set FIELD_MODULUS to a degree-m irreducible polynomial over F_2
MODp = 0;
REQUIRE_FIELD_MODULUS =
  type(FIELD_MODULUS_REQUIRED) == "t_INT" && FIELD_MODULUS_REQUIRED;
if(REQUIRE_FIELD_MODULUS &&
   (type(FIELD_MODULUS) != "t_POL" || poldegree(FIELD_MODULUS) != m),
  error("required FIELD_MODULUS does not have degree m")
);
if(type(FIELD_MODULUS) == "t_POL" && poldegree(FIELD_MODULUS) == m,
  if(!polisirreducible(Mod(1,2)*FIELD_MODULUS),
    error("FIELD_MODULUS is not irreducible over F_2"));
  MODp = FIELD_MODULUS
);
if(!MODp,
  for(kk = 1, m-1,
    if(polisirreducible(Mod(1,2)*(x^m+x^kk+1)),
      MODp = x^m+x^kk+1;
      break
    )
  )
);
{if(!MODp,
  forvec(v = [[1,m-1],[1,m-1],[1,m-1]],
    my(P = x^m+x^v[3]+x^v[2]+x^v[1]+1);
    if(polisirreducible(Mod(1,2)*P),
      MODp = P;
      break
    ),
    2
  )
);}
if(!MODp, error("no irreducible degree-m field modulus found"));
g = ffgen(Mod(1,2)*MODp, 'g); toint(z) = subst(lift(z.pol), variable(z.pol), 2);
fromint(n) = my(s = 0*g, kk = 0); while(n, if(n % 2, s += g^kk); n \= 2; kk++); s;
E = ellinit([1,a,0,0,1], g); N = ellcard(E);
D = -7*F^2; if(D % 8 != 1 || D % 3 == 0, error("Weber f not allowed for D"));
print("m=", m, " a=", a, "  field F_2[x]/(", MODp, ")  #E = ", factor(N), "\n  F=", F, ", D=", D, ", h(D)=", qfbclassno(D));
t = getabstime(); H = polclass(D, 1); print("  polclass(D, 1) [Weber f]: degree ", poldegree(H), ", max coeff ~2^", round(log(normlp(Vec(H), oo))/log(2)), ", ", (getabstime()-t)\1000, " s");
H2 = lift(H*Mod(1,2)); H = 0;
t = getabstime(); FA = factormod(H2, 2); print("  H mod 2 over F_2: ", #FA~, " irreducible factors, degrees ", Set(apply(poldegree, FA[,1]~)), ", multiplicities ", Set(FA[,2]~));
{R = List(); foreach(FA[,1]~, P, my(L = factor(subst(lift(P), variable(lift(P)), 'Y)*g^0)[,1], r = 0);
   foreach(L~, f, if(poldegree(f) == 1, r = -polcoeff(f,0)/polcoeff(f,1); break)); if(r == 0, error("factor without root in F_2^m"));
   my(c = r); for(i = 1, poldegree(P), listput(R, c); c = c^2); if(c != r, error("orbit")));}
B = vecsort(apply(z -> toint(1/z^48), Vec(R))); print("  roots in F_2^m: ", #B, ", distinct ", #Set(B), "  (", (getabstime()-t)\1000, " s)");
{t = getabstime(); A = vector(#B, i, my(a2 = -1); for(aa = 0, 1, if(ellcard(ellinit([1,aa,0,0,fromint(B[i])], g)) == N, a2 = aa)); a2);
 print("  models with #E = N: ", #select(z -> z >= 0, A), " / ", #B, "  (a2 values ", Set(A), ", ", (getabstime()-t)\1000, " s)");}
orbmin(z) = my(c = z^2, mn = toint(z)); while(c != z, mn = min(mn, toint(c)); c = c^2); mn;
print("  Galois orbits: ", #Set(apply(b -> orbmin(fromint(b)), B)));
write(OUT, vector(#B, i, [B[i], A[i]]));
\\ level check
ordq(D, p) = my(Q = qfbprimeform(D, p), R = Q, k = 1, I = qfbpow(Q, 0)); while(qfbred(R) != qfbred(I), R = qfbcomp(R, Q); k++); k;
o = ordq(D, S); print("  ord[l_", S, "] in Cl(D) = ", o);
Phi = polmodular(S, , , 'Y); BS = Set(B);
roots_q(j) = my(L = factor(subst(Phi, 'x, j)*g^0)[,1]); apply(f -> -polcoeff(f,0)/polcoeff(f,1), select(f -> poldegree(f)==1, L~));
{walk(bb) = my(j0 = 1/fromint(bb), r = roots_q(j0), prev = j0, cur = r[1], n = 1, outside = 0);
  while(cur != j0 && n < 4*o + 10, if(!setsearch(BS, toint(1/cur)), outside++); my(rr = roots_q(cur), nx = 0);
    for(i = 1, #rr, if(rr[i] != prev, nx = rr[i])); if(nx == 0, nx = prev); prev = cur; cur = nx; n++); [n, outside]}
print("  crater ", S, "-cycle length: ", walk(1)[1]);
{t = getabstime(); for(i = 1, NSAMP, my(b = B[1 + (i-1)*(#B\NSAMP)], w = walk(b));
   print("  b=", b, ": ", S, "-cycle length ", w[1], if(w[1] == o, " = ord", " != ord"), ", visited curves outside the root set: ", w[2]));
 print("  (cycle walks ", (getabstime()-t)\1000, " s)");}
