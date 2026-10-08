\\ m = 83 Koblitz crater E: y^2+xy=x^3+1 over F_2^83 (a = 0, #E = 4*l). Conductor prime 6473 (inert, h = 6474).
\\ The 6473-floor = all curves with End = Z + 6473*O_K = roots of H_D mod 2, D = -7*6473^2 (PARI polclass invariant 1 = Weber f, valid as D = 1 mod 8 and 3 does not divide D;
\\ mod 2 the relation (f^24-16)^3 = j f^24 becomes j = f^48).
\\ Field: first irreducible trinomial/pentanomial of degree 83.
MODp = 0; for(k=1,82, if(polisirreducible(Mod(1,2)*(x^83+x^k+1)), MODp = x^83+x^k+1; break));
{if(!MODp, forvec(v=[[1,40],[1,40],[1,40]], my(P = x^83+x^v[3]+x^v[2]+x^v[1]+1); if(polisirreducible(Mod(1,2)*P), MODp = P; break), 2));}
print("field modulus ", MODp);
g = ffgen(Mod(1,2)*MODp, 'g); toint(z) = subst(lift(z.pol), variable(z.pol), 2);
E = ellinit([1,0,0,0,1], g); N = ellcard(E); print("#E = ", factor(N));
D = -7*6473^2; print("D = ", D, "  h(D) = ", qfbclassno(D));
t = getabstime(); H = polclass(D, 1); print("polclass(D, 1) [Weber f]: degree ", poldegree(H), ", max coeff ~2^", round(log(normlp(Vec(H), oo))/log(2)), ", ", (getabstime()-t)\1000, " s");
writebin("H_D_weber.bin", H);
t = getabstime(); H2 = H*Mod(1,2); F = factor(H2*g^0)[,1]; rts = apply(r -> -polcoeff(r,0)/polcoeff(r,1), select(r -> poldegree(r) == 1, F~));
print("roots of H_D mod 2 in F_2^83: ", #rts, "  (", (getabstime()-t)\1000, " s)");
B = vecsort(apply(z -> toint(1/z^48), rts));
print("b = f^-48 and f^-3 = (f^-48)^(1/16) give the same set: ", Set(B) == Set(apply(z -> toint(1/z^3), rts)));
fromint(n) = my(s = 0*g, kk = 0); while(n, if(n % 2, s += g^kk); n \= 2; kk++); s;
\\ choose the F_q-model with #E = N (a2 in {0,1}) for every floor curve
t = getabstime(); A = vector(#B, i, my(a2 = -1); for(aa = 0, 1, if(ellcard(ellinit([1,aa,0,0,fromint(B[i])], g)) == N, a2 = aa)); a2);
print("models with #E = N: ", #select(a -> a >= 0, A), " / ", #B, "   (a2 values ", Set(A), ", ", (getabstime()-t)\1000, " s)");
write("floor6473.txt", vector(#B, i, [B[i], A[i]]));
