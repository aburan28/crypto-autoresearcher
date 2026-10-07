read("walk41.gp"); N=2199025563772;
{foreach([[409,5031829425,410],[1721,14893930241,1722]], v,
  my(lp=v[1], b=v[2], h=v[3]);
  print("floor-",lp," seed b=",b,": cyc23=",cyc(23,b,3000)," cyc11=",cyc(11,b,2000));
  my(w=walkl(29,b,h+5)); print("  29-cycle closed=",w[1]," length=",#w[2]," (class number ",h,")");
  my(S=Set(w[2])); print("  distinct curves=",#S, "  all #E=N: ", #select(bb->ellcard(ellinit([1,0,0,0,fromint(bb)],g))!=N, w[2])==0);
  write("floor"lp".txt", w[2]))}
