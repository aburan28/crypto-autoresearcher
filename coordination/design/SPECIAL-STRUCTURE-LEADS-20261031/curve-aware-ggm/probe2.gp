k1(lo,hi)={my(c=0,E,n,N);forprime(p=lo,hi,N=(p-1)/2;if(!isprime(N),next);for(a=1,40,E=ellinit([a,a+5]*Mod(1,p));if(type(E)!="t_VEC",next);if(ellcard(E)==p-1,c++;if(c<=2,print("k=1 (h=2) ex p=",p," a=",a," N=",N));break)));print("k=1 h=2 count ",c);}
k1(4099,60000);
\\ tate self-pairing nontrivial?
p=4099; N=(p-1)/2; print(isprime(N));
