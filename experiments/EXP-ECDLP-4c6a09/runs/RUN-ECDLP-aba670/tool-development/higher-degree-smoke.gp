default(realprecision,80);default(parisizemax,2000000000);
read("ellQ.gp");read("ell-certified.gp");read("qfsolve.gp");read("resultant3.gp");
rank_bnfinit(P,flag=1)={my(B=bnfinit(P,flag));if(bnfcertify(B)!=1,error("BNF certification failed"));print("@@BNFCERT|",poldegree(P));B};
DEBUGLEVEL_ell=0;LIM1=2;LIM3=4;LIMTRIV=2;MAXPROB=20;LIMBIGPRIME=0;
setrand(1); B=rank_bnfinit(y^7-y^3+1,1); print("@@Q|",ellrank(ellinit([0,0,0,11,6])));
print("@@ROOTS|",nfroots(B,x^3+11*x+6));
R=bnfellrank(B,[0,0,0,11,6]);print("@@P224|",R);quit;
