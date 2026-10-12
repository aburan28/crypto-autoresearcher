\\ Independent level checks for the 263-isogeny images (run after iso263.gp).
\\ (1) structure of the twist's 263-part: (Z/263)^2 iff pi is scalar on E[263] iff 263 | [End:Z[pi]] (crater side);
\\     cyclic Z/263^2 on the 263-floor.  (2) horizontal 11-isogeny cycle length = ord [l_11] in Cl(End):
\\     1 on the crater, 131 on the 263-floor (Cl(-7*263^2) has order 262).
g = ffgen(Mod(1,2)*(x^131+x^8+x^3+x^2+1), 'g);
fromint(n) = my(s = 0*g, k = 0); while(n, if(n % 2, s += g^k); n \= 2; k++); s;
toint(z) = subst(lift(z.pol), variable(z.pol), 2);
F = read("floor263.txt");
tw263(bb, a2) = my(Et = ellinit([1, 1-a2, 0, 0, fromint(bb)], g), c = ellgroup(Et)); [valuation(c[1],263), if(#c>1, valuation(c[2],263), 0)];
crater = tw263(1, 0); print("crater twist 263-part exponents: ", crater);
{ok = 0; for(i = 1, #F, my(e = tw263(F[i][1], F[i][2])); if(e == [2,0], ok++, print("UNEXPECTED ", F[i], " ", e)));}
print("263-floor images with cyclic Z/263^2 twist 263-part: ", ok, " / ", #F);
Phi = polmodular(11, , , 'Y);
roots_q(j) = my(L = factor(subst(Phi, 'x, j)*g^0)[,1]); apply(f -> -polcoeff(f,0)/polcoeff(f,1), select(f -> poldegree(f)==1, L~));
{cyc11(bb) = my(j0 = 1/fromint(bb), r = roots_q(j0), prev = j0, cur = r[1], n = 1);
  while(cur != j0 && n < 1000, my(rr = roots_q(cur), nx = 0); for(i = 1, #rr, if(rr[i] != prev, nx = rr[i]));
    if(nx == 0, nx = prev); prev = cur; cur = nx; n++); n}
print("11-cycle length: crater ", cyc11(1));
{cnt = Map(); for(i = 1, #F, my(L = cyc11(F[i][1])); mapput(cnt, L, if(mapisdefined(cnt, L), mapget(cnt, L), 0) + 1)); print("11-cycle lengths over all ", #F, " floor curves (length -> count): ", Mat(cnt));}
