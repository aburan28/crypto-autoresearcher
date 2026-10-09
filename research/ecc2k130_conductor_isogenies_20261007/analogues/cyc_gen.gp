\\ horizontal s-isogeny cycle length through E_b (s split in Q(sqrt(-7)), s not dividing the conductor)
\\ = order of [l_s] in Cl(End E_b). set MOD, IN (file of [b,a2,...] vectors written by vert_gen.gp), S, CAP before reading.
g = ffgen(Mod(1,2)*MOD, 'g);
fromint(n) = my(s = 0*g, kk = 0); while(n, if(n % 2, s += g^kk); n \= 2; kk++); s;
Phi = polmodular(S, , , 'Y);
roots_q(j) = my(L = factor(subst(Phi, 'x, j)*g^0)[,1]); apply(f -> -polcoeff(f,0)/polcoeff(f,1), select(f -> poldegree(f)==1, L~));
{cyc(bb) = my(j0 = 1/fromint(bb), r = roots_q(j0), prev = j0, cur = r[1], n = 1);
  while(cur != j0 && n < CAP, my(rr = roots_q(cur), nx = 0); for(i = 1, #rr, if(rr[i] != prev, nx = rr[i]));
    if(nx == 0, nx = prev); prev = cur; cur = nx; n++); n}
print("crater: ", cyc(1));
L = readvec(IN); {for(i = 1, #L, print("b'=", L[i][1], " -> ", S, "-cycle length ", cyc(L[i][1])));}
