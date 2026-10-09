MOD = x^83+x^14+x^4+x+1; read("sample83.gp");
g = ffgen(Mod(1,2)*MOD, 'g);
fromint(n) = my(s = 0*g, kk = 0); while(n, if(n % 2, s += g^kk); n \= 2; kk++); s;
Phi = polmodular(11, , , 'Y);
roots_q(j) = my(L = factor(subst(Phi, 'x, j)*g^0)[,1]); apply(f -> -polcoeff(f,0)/polcoeff(f,1), select(f -> poldegree(f)==1, L~));
{cyc(bb) = my(j0 = 1/fromint(bb), r = roots_q(j0), prev = j0, cur = r[1], n = 1);
  while(cur != j0 && n < 5000, my(rr = roots_q(cur), nx = 0); for(i = 1, #rr, if(rr[i] != prev, nx = rr[i]));
    if(nx == 0, nx = prev); prev = cur; cur = nx; n++); n}
print("crater: 11-cycle ", cyc(1));
{for(i = 1, #SAMPLE, print("b=", SAMPLE[i], " -> 11-cycle ", cyc(SAMPLE[i])));}
