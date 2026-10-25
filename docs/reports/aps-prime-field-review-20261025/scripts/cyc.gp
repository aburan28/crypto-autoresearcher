default(parisize, 400000000);
{
p = 10009; B = 72; e = (p-1)/B;
print("p=",p," B=",B," e=",e);
g = znprimroot(p); gB = g^e;
muB = vector(B, i, lift(gB^i));
cnt = Map();
for(i=1,B, for(j=1,B, if(i!=j, d = lift(Mod(muB[j]-muB[i],p)^B); if(mapisdefined(cnt,d), mapput(cnt,d,mapget(cnt,d)+1), mapput(cnt,d,1)))));
M = Mat(cnt);
ok = 1;
for(t=1,6,
  a = Mod(random(p-2)+1, p);
  lhs = prod(i=1,B, (Mod(muB[i],p)+a)^B - 1);
  rhs = a^B; for(k=1, matsize(M)[1], rhs *= (a^B - M[k,1])^(M[k,2]/B));
  print("a=",lift(a),"  lhs==rhs: ", lhs==rhs); ok = ok && (lhs==rhs));
print("all ok: ", ok);
s = 0; for(k=1, matsize(M)[1], s += M[k,2]/B; if(denominator(M[k,2]/B)!=1, print("non-integer multiplicity!")));
print("sum r_u = ", s, " (expect B-1 = ", B-1, "); distinct cosets hit: ", matsize(M)[1], " of e = ", e);
}
