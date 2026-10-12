default(parisizemax,2000000000);default(nbthreads,1);setrand(1);
{main()=
my(N=nfinit((4)*y^0+(-3)*y^1+(-1)*y^2+(1)*y^3),EK=ellinit([0,0,0,7,1],N),QR=[2, 2, 0, [[0, 1], [1, 3]]],NR,T,S=List(),P,dup,PR,MP,R,MR,PI,EP,C,F,L,H,G,found,RP);
NR=[3, 4, [[Mod(0, y^3 - y^2 - 3*y + 4), Mod(1, y^3 - y^2 - 3*y + 4)], [Mod(9*y^2 - 32*y + 29, y^3 - y^2 - 3*y + 4), Mod(-120*y^2 + 337*y - 259, y^3 - y^2 - 3*y + 4)], [Mod(3, y^3 - y^2 - 3*y + 4), Mod(7, y^3 - y^2 - 3*y + 4)]]];T=NR[3];
T=concat([QR[4][1]],T);print("@@RAW_SEED_COUNT|",#T-1);
for(i=1,#T,P=T[i];if(#P==1,next);if(!ellisoncurve(EK,P),error("Seed off exact curve"));dup=0;for(t=1,#S,if(P==S[t] || P==ellneg(EK,S[t]),dup=1;break));if(!dup,listput(S,P)));
print("@@UNIQUE_AVAILABLE_SEED_COUNT|",#S);S=Vec(S);if(#S>4,S=S[1..4]);
for(i=1,#S,print("@@SEED|",i,"|",vector(3,t,polcoef(lift(S[i][1]),t-1)),"|",vector(3,t,polcoef(lift(S[i][2]),t-1))));
for(kj=1,3,R=2^([6,7,12][kj]);PI=R^3-R-1;
EP=ellinit([0,0,0,7,1],PI);C=ellcard(EP);F=factor(C);L=F[#F[,1],1];if(F[#F[,1],2]!=1,error("Repeated largest prime"));H=C/L;
RP=QR[4][1];G=ellmul(EP,[Mod(RP[1],PI),Mod(RP[2],PI)],H);if(#G==1,G=ellmul(EP,ellgroup(EP,,1)[3][1],H));if(#G==1,error("Zero G"));
print("@@GROUP|",kj,"|",PI,"|",C,"|",L,"|",H,"|",lift(G[1]),"|",lift(G[2]));
MR=polrootsmod(N.pol,PI);if(!#MR,print("@@NO_ROOT|",kj);next);R=vecmin(lift(MR));
PR=idealprimedec(N,PI);found=0;for(i=1,#PR,if(PR[i][4]==1 && lift(trace(nfmodpr(N,Mod(y,N.pol),PR[i])))==R,found=i;break));if(!found,error("Missing degree-one prime"));PR=PR[found];MP=nfmodprinit(N,PR);
print("@@ROOT|",kj,"|",R,"|",found);
for(i=1,#S,if(nfeltval(N,S[i][1],PR)<0,print("@@REDUCED_SEED|",kj,"|",i,"|O");next);
P=[lift(trace(nfmodpr(N,S[i][1],MP))),lift(trace(nfmodpr(N,S[i][2],MP)))];if(!ellisoncurve(EP,P),error("Reduced seed off curve"));print("@@REDUCED_SEED|",kj,"|",i,"|",P[1],"|",P[2]));
);};iferr(main(),E,print("@@ERROR|",E));print("@@DONE");quit;
