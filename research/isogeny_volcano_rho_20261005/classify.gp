\\ classify curves y^2+xy=x^3+b over F_2^37 into volcano levels
g=ffgen(Mod(1,2)*(x^37+x^9+x^2+x+1),'g); q=2^37; N=137439487532; ell=230603167;
fromint(n)=my(s=0*g,k=0); while(n, if(n%2, s+=g^k); n\=2; k++); s;
toint(z)=subst(lift(z.pol),variable(z.pol),2);
K=ffgen(ffinit(2,37*18),'h); emb=ffembed(g,K);
P18=lift(Mod(-x,x^2-x+2)^(37*18)); N18=2^(37*18)+1-(2*polcoeff(P18,0)+polcoeff(P18,1)); co18=N18/73^2;
\\ 1 iff E[73] subset E(F_q^18) (pi scalar on E[73]) <=> 73 | [End(E):Z[pi]]
scalar73(b)=my(EK=ellinit([1,0,0,0,ffmap(emb,b)],K)); for(t=1,4, my(P=ellmul(EK,random(EK),co18)); if(ellmul(EK,P,73)!=[0], return(0))); 1;
