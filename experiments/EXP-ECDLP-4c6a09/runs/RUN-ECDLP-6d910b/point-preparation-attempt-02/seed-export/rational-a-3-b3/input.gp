default(parisizemax,2000000000);default(nbthreads,1);setrand(1);
{main()=
my(N=nfinit((-1)*y^0+(-1)*y^1+(1)*y^3),EQ=ellinit([0,0,0,-3,3]),EK=ellinit([0,0,0,-3,3],N),QR=[1, 1, 0, [[1, 1]]],S,NR,F,EP,C,L,H,G,RP,R,PI,MR,found);
S=QR[4];
for(i=1,#S,if(!ellisoncurve(EK,S[i]),error("Seed fails exact curve equation")));
for(i=1,#S,if(S[i]==QR[4][1],if(i>1,S=concat([S[i]],vector(#S-1,j,S[if(j<i,j,j+1)])));break));
for(i=1,#S,print("@@SEED|",i,"|",vector(3,j,polcoef(lift(S[i][1]),j-1)),"|",vector(3,j,polcoef(lift(S[i][2]),j-1))));
for(j=1,3,
R=2^([6,7,12][j]);PI=R^3-R-1;EP=ellinit([0,0,0,-3,3],PI);C=ellcard(EP);F=factor(C);L=F[#F[,1],1];if(F[#F[,1],2]!=1,error("Repeated largest subgroup prime"));H=C/L;
RP=QR[4][1];G=ellmul(EP,[Mod(RP[1],PI),Mod(RP[2],PI)],H);if(#G==1,G=ellmul(EP,ellgroup(EP,,1)[3][1],H));if(#G==1,error("Zero generator"));
print("@@GROUP|",j,"|",PI,"|",C,"|",L,"|",H,"|",lift(G[1]),"|",lift(G[2]));
MR=polrootsmod(N.pol,PI);
if(!#MR,print("@@NO_ROOT|",j);next);
R=R;
if(subst(N.pol,y,Mod(R,PI))!=0,error("Chosen root invalid"));
PI=idealprimedec(N,PI);found=0;for(i=1,#PI,if(PI[i][4]==1 && lift(nfmodpr(N,Mod(y,N.pol),PI[i]))==R,found=i;break));if(!found,error("Degree-one prime missing"));
print("@@ROOT|",j,"|",R,"|",found);
for(i=1,#S,RP=[nfmodpr(N,S[i][1],PI[found]),nfmodpr(N,S[i][2],PI[found])];if(!ellisoncurve(EP,RP),error("Reduced seed off curve"));print("@@REDUCED_SEED|",j,"|",i,"|",lift(RP[1]),"|",lift(RP[2])));
);};
iferr(main(),E,print("@@ERROR|",E));print("@@DONE");quit;
