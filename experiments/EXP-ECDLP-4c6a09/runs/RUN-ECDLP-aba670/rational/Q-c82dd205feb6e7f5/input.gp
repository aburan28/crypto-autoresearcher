default(realprecision,80);default(parisizemax,2000000000);default(nbthreads,1);
read("/workspace/solinas-run/experiments/EXP-ECDLP-4c6a09/runs/RUN-ECDLP-aba670/source/ellQ.gp");
read("/workspace/solinas-run/experiments/EXP-ECDLP-4c6a09/runs/RUN-ECDLP-aba670/source/ell-certified.gp");
read("/workspace/solinas-run/experiments/EXP-ECDLP-4c6a09/runs/RUN-ECDLP-aba670/source/qfsolve.gp");
read("/workspace/solinas-run/experiments/EXP-ECDLP-4c6a09/runs/RUN-ECDLP-aba670/source/resultant3.gp");
rank_bnfinit(P,flag=1)={my(B,C);print("@@CERT_START|",poldegree(P),"|",P);B=bnfinit(P,flag);C=bnfcertify(B);if(C!=1,error("BNF certification failed"));print("@@CERT_OK|",poldegree(P),"|",P);B};
DEBUGLEVEL_ell=0;MAXPROB=20;LIMBIGPRIME=0;setrand(1);

{rank_main()=
my(Eq=ellinit([0,0,0,13,12]),QR,BN,NR,T,RP,EK);
QR=ellrank(Eq,2);print("@@Q_BOUND|",QR[1],"|",QR[2]);print("@@Q_RAW|",QR);
if(QR[1]!=QR[2],QR=ellrank(Eq,5,QR[4]);print("@@Q_BOUND|",QR[1],"|",QR[2]);print("@@Q_RAW|",QR));
};
iferr(rank_main(),err,print("@@ERROR|",err));
print("@@DONE");quit;
