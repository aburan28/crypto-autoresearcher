smooth(n,B)={my(f=factor(n)[,1]);f[#f]<=B}
hits(D,bits,B,trials)={my(c=0,v,t,p,N);
 for(i=1,trials, v=random(2^(bits\2-2))+1; t=2^(bits\2)+random(2^(bits\2)); if((t^2-D*v^2)%4,next);
  p=(t^2-D*v^2)/4; if(p<2^(bits-1)||p>=2^bits||!isprime(p),next);
  N=p+1-t; if(isprime(N)&&smooth(N-1,1024), c++)); c}
print(hits(-163,32,1024,400000)); print(hits(-3,32,1024,400000));
\\ Hasse boundary: |t| >= 2 sqrt(p) - 2^8
hb(D,bits)={my(v,t,p,N,k=0);for(i=1,400000,v=random(40)+1;t=2^(bits\2+1)-random(2^9)+0; if((t^2-D*v^2)%4,next);p=(t^2-D*v^2)/4;if(p<2^(bits-1)||p>=2^bits||!isprime(p),next);N=p+1-t;if(isprime(N),k++));k}
print(hb(-163,32));print(hb(-7,32));
