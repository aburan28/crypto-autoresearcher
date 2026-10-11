\\ m = 51 Koblitz crater y^2+xy=x^3+1 over F_2[x]/(x^51+x^6+x^3+x+1): floor of conductor F via the class polynomial mod 2
\\ (PARI polclass invariant 1 = Weber f; mod 2, j = f^48).
MOD = x^51+x^6+x^3+x+1; g = ffgen(Mod(1,2)*MOD, 'g); toint(z) = subst(lift(z.pol), variable(z.pol), 2);
fromint(n) = my(s = 0*g, kk = 0); while(n, if(n % 2, s += g^kk); n \= 2; kk++); s;
E = ellinit([1,0,0,0,1], g); N = ellcard(E);
{floor_cm(F, OUTF) = my(D = -7*F^2, t = getabstime(), H = polclass(D, 1), tc = (getabstime()-t)\1000);
  print("F=", F, ": h(D)=", qfbclassno(D), "  polclass degree ", poldegree(H), ", max coeff ~2^", round(log(normlp(Vec(H), oo))/log(2)), ", ", tc, " s");
  my(L = factor(H*g^0)[,1], rts = apply(r -> -polcoeff(r,0)/polcoeff(r,1), select(r -> poldegree(r) == 1, L~)));
  my(B = vecsort(apply(z -> toint(1/z^48), rts)));
  my(A = vector(#B, i, my(a2 = -1); for(aa = 0, 1, if(ellcard(ellinit([1,aa,0,0,fromint(B[i])], g)) == N, a2 = aa)); a2));
  print("   roots in F_2^51: ", #rts, "; models with #E = N: ", #select(a -> a >= 0, A), "  (a2 values ", Set(A), ")");
  write(OUTF, vector(#B, i, [B[i], A[i]])); B}
