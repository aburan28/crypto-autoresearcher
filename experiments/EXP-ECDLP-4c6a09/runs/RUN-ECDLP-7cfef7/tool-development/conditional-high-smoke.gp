default(realprecision,80);default(parisizemax,2000000000);default(nbthreads,1);
read("/workspace/solinas-run/experiments/EXP-ECDLP-4c6a09/runs/RUN-ECDLP-aba670/source/ellQ.gp");
read("/workspace/solinas-run/experiments/EXP-ECDLP-4c6a09/runs/RUN-ECDLP-aba670/source/ell-certified.gp");
read("/workspace/solinas-run/experiments/EXP-ECDLP-4c6a09/runs/RUN-ECDLP-aba670/source/qfsolve.gp");
read("/workspace/solinas-run/experiments/EXP-ECDLP-4c6a09/runs/RUN-ECDLP-aba670/source/resultant3.gp");
rank_bnfinit(P,flag=1)={my(B,C);print("@@CERT_START|",poldegree(P),"|",P);B=bnfinit(P,flag);C=0;print("@@CERT_OK|",poldegree(P),"|",P);B};
DEBUGLEVEL_ell=0;MAXPROB=20;LIMBIGPRIME=0;setrand(1);

{rank_main()=my(B,QR,R);QR=ellrank(ellinit([0,0,0,11,6]),2);print("@@Q|",QR);B=rank_bnfinit(y^7-y^3+1,1);LIM1=0;LIM3=0;LIMTRIV=0;R=bnfellrank(B,[0,0,0,11,6],QR[4]);print("@@NF|",R);};
rank_main();quit;
