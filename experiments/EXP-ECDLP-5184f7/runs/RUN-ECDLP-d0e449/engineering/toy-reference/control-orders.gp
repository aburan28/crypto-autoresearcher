for(i=1,2,p=if(i==1,1000003,1000033);if(!isprime(p),error("control not prime"));N=ellcard(ellinit([2,3],p));print([p,N,Vec(factor(N)[,1])]));
quit;
