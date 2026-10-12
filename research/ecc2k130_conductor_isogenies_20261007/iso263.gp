\\ All 264 rational 263-isogenies from the ECC2K-130 curve E: y^2+xy=x^3+1 over F_2^131.
\\ Field: F_2[x]/(x^131+x^8+x^3+x^2+1) (the SEC sect131 pentanomial). Elements written as integers of their bits.
\\ pi = -1 on E[263], so E[263] is F_q-rational on the quadratic twist Et: y^2+xy=x^3+x^2+1 (Tr(1)=1, m odd),
\\ with the same x-coordinates. Char-2 Velu (a1=1,a2=a3=a4=0,a6=1): E' = y^2+xy=x^3+v x+(1+v), v = sum of the
\\ 131 x-coordinates of a half-kernel; normalised b' = 1/j' = 1+v+v^2.
g = ffgen(Mod(1,2)*(x^131+x^8+x^3+x^2+1), 'g); q = 2^131;
toint(z) = subst(lift(z.pol), variable(z.pol), 2);
E  = ellinit([1,0,0,0,1], g);  N = ellcard(E);
Et = ellinit([1,1,0,0,1], g);  T = ellcard(Et);
print("N  = ", factor(N)); print("#twist = ", factor(T), "   (2q+2-N check: ", T == 2*q+2-N, ")");
G = ellgroup(Et, , 1); print("twist group structure ", G[2]);
\\ basis of Et[263]: exponent of Et(F_q) is n1 = G[2][1], so [n1/263]R lies in Et[263] for every R;
\\ keep two such points with a nontrivial Weil pairing (an independent basis).
n1 = G[2][1]; setrand(263);
{P1 = [0]; while(P1 == [0], P1 = ellmul(Et, random(Et), n1/263));
 P2 = [0]; while(P2 == [0] || ellweilpairing(Et, P1, P2, 263) == 1, P2 = ellmul(Et, random(Et), n1/263));
 if(ellmul(Et,P1,263) != [0] || ellmul(Et,P2,263) != [0], error("not 263-torsion"));}
print("Et[263] basis found; Weil pairing e(P1,P2) has order ", fforder(ellweilpairing(Et,P1,P2,263)));
gens = concat(vector(263, i, elladd(Et, P1, ellmul(Et, P2, i-1))), [P2]);
res = List();
{for(s = 1, #gens, my(Q = gens[s], R = Q, v = 0*g);
   for(k = 1, 131, v += R[1]; R = elladd(Et, R, Q));
   my(bp = 1 + v + v^2);
   listput(res, [s, toint(bp), bp == 1]));}
write("iso263_raw.txt", Vec(res));
nh = #select(r -> r[3], Vec(res)); print("subgroups: ", #res, "   images equal to E itself (j=1, horizontal): ", nh);
desc = select(r -> !r[3], Vec(res)); B = Set(apply(r -> r[2], desc));
print("descending images: ", #desc, "   distinct j-invariants: ", #B);
\\ verify every descending image is isogenous (same #E) and record a2 of the F_q-model with #E = N
fromint(n) = my(s = 0*g, k = 0); while(n, if(n % 2, s += g^k); n \= 2; k++); s;
{out = List(); for(i = 1, #B, my(bb = B[i], a2 = -1);
   for(a = 0, 1, if(ellcard(ellinit([1,a,0,0,fromint(bb)], g)) == N, a2 = a));
   if(a2 < 0, error(Str("no model with #E=N for b=", bb)));
   listput(out, [bb, a2]));}
print("all ", #out, " descending images have a model with #E = N (ellcard)");
write("floor263.txt", Vec(out));
