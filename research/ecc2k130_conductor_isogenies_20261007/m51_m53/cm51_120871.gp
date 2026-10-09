\\ m = 51, a = 0 crater y^2+xy=x^3+1 over F_2[x]/(x^51+x^6+x^3+x+1): the 120871-floor (End = Z + 120871 O_K, h = 120870)
\\ as the roots mod 2 of the class polynomial for D = -7*120871^2. PARI polclass invariant 1 = Weber f (D = 1 mod 8, D = 2 mod 3);
\\ mod 2, (f^24-16)^3 = j f^24 gives j = f^48. H is reduced mod 2 right away (the integer polynomial is ~2 GB and is not kept);
\\ H mod 2 is factored over F_2 (factors of degree d | 51), one root of each factor is found in F_2^51, and its d conjugates
\\ are taken by squaring.
MOD = x^51+x^6+x^3+x+1; g = ffgen(Mod(1,2)*MOD, 'g); toint(z) = subst(lift(z.pol), variable(z.pol), 2);
fromint(n) = my(s = 0*g, kk = 0); while(n, if(n % 2, s += g^kk); n \= 2; kk++); s;
E = ellinit([1,0,0,0,1], g); N = ellcard(E);
F = 120871; D = -7*F^2; print("D = ", D, "  h(D) = ", qfbclassno(D), "  D mod 8 = ", D % 8, ", D mod 3 = ", D % 3);
t = getabstime(); H = polclass(D, 1); tc = (getabstime()-t)\1000;
print("polclass(D, 1) [Weber f]: degree ", poldegree(H), ", max coeff ~2^", round(log(normlp(Vec(H), oo))/log(2)), ", ", tc, " s");
H2 = lift(H*Mod(1,2)); H = 0; writebin("H_D_mod2.bin", H2);
t = getabstime(); FA = factormod(H2, 2); print("factor H mod 2 over F_2: ", #FA~, " irreducible factors, degrees ", Set(apply(poldegree, FA[,1]~)),
  ", multiplicities ", Set(FA[,2]~), "  (", (getabstime()-t)\1000, " s)");
{t = getabstime(); R = List(); foreach(FA[,1]~, P, my(L = factor(subst(lift(P), variable(lift(P)), 'Y)*g^0)[,1], r = 0);
   foreach(L~, f, if(poldegree(f) == 1, r = -polcoeff(f,0)/polcoeff(f,1); break)); if(r == 0, error("factor without root in F_2^51"));
   my(c = r); for(i = 1, poldegree(P), listput(R, c); c = c^2); if(c != r, error("orbit")));
 print("roots in F_2^51: ", #R, ", distinct ", #Set(Vec(R)), "  (", (getabstime()-t)\1000, " s)");}
B = vecsort(apply(z -> toint(1/z^48), Vec(R)));
{t = getabstime(); A = vector(#B, i, my(a2 = -1); for(aa = 0, 1, if(ellcard(ellinit([1,aa,0,0,fromint(B[i])], g)) == N, a2 = aa)); a2);
 print("models with #E = N: ", #select(a -> a >= 0, A), " / ", #B, "   (a2 values ", Set(A), ", ", (getabstime()-t)\1000, " s)");}
write("floor51_120871_cm.txt", vector(#B, i, [B[i], A[i]]));
