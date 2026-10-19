\\ Planning arithmetic for the two frozen D_K=-19 conductor floors.
ordform(D,p,n)={my(F=qfbprimeform(D,p),I=qfbpow(F,0),fac=factor(n));for(i=1,matsize(fac)[1],for(j=1,fac[i,2],if(qfbpow(F,n/fac[i,1])==I,n=n/fac[i,1],break)));return(n)};
D29=-19*8209^2; D37=-19*131101^2;
print([D29,quadclassunit(D29)[2],ordform(D29,7,qfbclassno(D29))]);
print([D37,quadclassunit(D37)[2],ordform(D37,7,qfbclassno(D37))]);
