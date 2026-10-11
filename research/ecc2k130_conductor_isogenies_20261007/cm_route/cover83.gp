\\ Tile the whole 6473-floor by horizontal 11-cycles: each cycle must have length ord[l_11] = 1079, stay inside the
\\ class-polynomial root set, and the cycles together must cover all 6474 curves (6 = index of <[l_11]> in Cl).
MOD = x^83+x^14+x^4+x+1; read("all83.gp");
g = ffgen(Mod(1,2)*MOD, 'g); toint(z) = subst(lift(z.pol), variable(z.pol), 2);
fromint(n) = my(s = 0*g, kk = 0); while(n, if(n % 2, s += g^kk); n \= 2; kk++); s;
Phi = polmodular(11, , , 'Y);
roots_q(j) = my(L = factor(subst(Phi, 'x, j)*g^0)[,1]); apply(f -> -polcoeff(f,0)/polcoeff(f,1), select(f -> poldegree(f)==1, L~));
{walk(bb) = my(j0 = 1/fromint(bb), r = roots_q(j0), prev = j0, cur = r[1], out = List([bb]));
  while(cur != j0 && #out < 5000, listput(out, toint(1/cur)); my(rr = roots_q(cur), nx = 0);
    for(i = 1, #rr, if(rr[i] != prev, nx = rr[i])); if(nx == 0, nx = prev); prev = cur; cur = nx);
  Vec(out)}
seen = Set(); ncyc = 0; outside = 0;
{while(#seen < #ALL, my(start = setminus(ALL, seen)[1], c = walk(start)); ncyc++;
   outside += #setminus(Set(c), ALL);
   print("cycle ", ncyc, ": length ", #c, ", outside the floor set: ", #setminus(Set(c), ALL));
   seen = setunion(seen, Set(c)));}
print("cycles: ", ncyc, "; curves covered: ", #setintersect(seen, ALL), " / ", #ALL, "; visited curves outside the set: ", outside);
