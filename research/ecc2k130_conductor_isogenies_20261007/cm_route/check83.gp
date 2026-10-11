ordq(D,p,cap)=my(Q=qfbprimeform(D,p),R=Q,k=1,I=qfbpow(Q,0)); while(qfbred(R)!=qfbred(I) && k<cap, R=qfbcomp(R,Q); k++); k;
D = -7*6473^2;
{forprime(s = 3, 60, if(kronecker(-7, s) == 1, print("ord[l_", s, "] in Cl(-7*6473^2) = ", ordq(D, s, 10000))));}
