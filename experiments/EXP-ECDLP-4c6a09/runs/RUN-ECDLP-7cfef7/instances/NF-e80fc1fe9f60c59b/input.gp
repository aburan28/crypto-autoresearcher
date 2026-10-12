default(realprecision,80);default(parisizemax,2000000000);default(nbthreads,1);
read("/workspace/solinas-run/experiments/EXP-ECDLP-4c6a09/runs/RUN-ECDLP-7cfef7/source/ellQ.gp");
read("/workspace/solinas-run/experiments/EXP-ECDLP-4c6a09/runs/RUN-ECDLP-7cfef7/source/ell-certified.gp");
read("/workspace/solinas-run/experiments/EXP-ECDLP-4c6a09/runs/RUN-ECDLP-7cfef7/source/qfsolve.gp");
read("/workspace/solinas-run/experiments/EXP-ECDLP-4c6a09/runs/RUN-ECDLP-7cfef7/source/resultant3.gp");
CERTIFY_ALL=1;
rank_bnfinit(P,flag=1)={my(B,C);print("@@BNF_START|",poldegree(P),"|",P);B=bnfinit(P,flag);if(CERTIFY_ALL || poldegree(P)<=12,C=bnfcertify(B);if(C!=1,error("BNF certification failed"));print("@@CERT_OK|",poldegree(P),"|",P),print("@@UNCERT_BNF|",poldegree(P),"|",P));B};
DEBUGLEVEL_ell=0;MAXPROB=100;LIMBIGPRIME=31;setrand(1);

{rank_main()=
my(Eq=ellinit([0,0,0,-8,2]),QR,BN,NR,T,RP,EK);
QR=ellrank(Eq,2);print("@@Q_BOUND|",QR[1],"|",QR[2]);print("@@Q_RAW|",QR);
if(QR[1]!=QR[2],QR=ellrank(Eq,5,QR[4]);print("@@Q_BOUND|",QR[1],"|",QR[2]);print("@@Q_RAW|",QR));
BN=rank_bnfinit((1)*y^0+(-1)*y^1+(1)*y^3,1);
T=#nfroots(BN,x^3+(-8)*x+(2));
if(T!=0 && T!=1 && T!=3,error("Unexpected root count"));
T=if(T==3,2,if(T==1,1,0));print("@@TORSION_DIM|",T);
EK=ellinit([0,0,0,-8,2],BN);RP=QR[4];
LIM1=2;LIM3=2;
LIMTRIV=2;print("@@DESCENT_START|",LIMTRIV);
NR=bnfellrank(BN,[0,0,0,-8,2],RP);
for(i=1,#NR[3],if(!ellisoncurve(EK,NR[3][i]),error("Point failed curve equation")));
print("@@NF_BOUND|",LIMTRIV,"|",NR[1],"|",NR[2],"|",T);
print("@@NF_RAW|",NR);RP=NR[3];
if(NR[1]<NR[2]-T,
LIMTRIV=4;print("@@DESCENT_START|",LIMTRIV);
NR=bnfellrank(BN,[0,0,0,-8,2],RP);
for(i=1,#NR[3],if(!ellisoncurve(EK,NR[3][i]),error("Point failed curve equation")));
print("@@NF_BOUND|",LIMTRIV,"|",NR[1],"|",NR[2],"|",T);
print("@@NF_RAW|",NR);RP=NR[3];
);
};
iferr(rank_main(),err,print("@@ERROR|",err));
print("@@DONE");quit;
