p=1009;
{for(b=1,60, E=ellinit([0,0,0,1,b],p); if(!E,next); G=ellgroup(E); if(#G>=1 && G[#G]%9==0 && (#G==1||G[1]%3!=0 || 1),
  N=ellcard(E); if(N%9==0 && G[#G]%9==0 && (#G==1 || valuation(G[1],3)==0 || 1),
   P=ellgenerators(E)[1]; break)))}
print(E.j," ",ellcard(E)," ",ellgroup(E));
P=ellgenerators(E)[1]; o=ellorder(E,P); print("ord P=",o);
{for(k=1,12, Q=ellmul(E,P,k); xn=ellxn(E,3); f=lift(Mod(1,p)*(xn[1]-Q[1]*xn[2]));
  F=factormod(f,p); print(k," mod3=",k%3," ",vecsort(vector(#F~,i,poldegree(F[i,1])))))}
