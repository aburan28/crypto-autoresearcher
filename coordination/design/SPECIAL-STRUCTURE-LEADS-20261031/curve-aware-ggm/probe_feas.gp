\\ feasibility probe only: not a result
gen(lo,hi,maxa)={my(cnt=0,tot=0,k1=0,ex=List(),ex1=List(),E,n);
 forprime(p=lo,hi,
  for(a=1,maxa,
   E=ellinit([a,a+3]*Mod(1,p));
   if(type(E)!="t_VEC",next);
   n=ellcard(E);
   if(!isprime(n)||n==p,next);
   tot++;
   if((p-1)%n==0,k1++; if(#ex1<2,listput(ex1,[p,a,n])));
   if((p-1)%n!=0&&(p^2-1)%n!=0, cnt++; if(#ex<3,listput(ex,[p,a,n])))));
 print("prime-order curves=",tot," k>2 =",cnt," k=1 =",k1);print(" k>2 e.g. ",ex);print(" k=1 e.g. ",ex1);}
gen(4099,7000,12);
\\ supersingular k=2 control y^2=x^3+x, p=3 mod 4, N | p+1 prime = (p+1)/4 style
ss(lo,hi)={my(c=0);forprime(p=lo,hi,if(p%4==3,my(n=(p+1)/4);if(isprime(n),c++;if(c<=2,print("ss k=2 ex p=",p," N=",n)))));print("ss count ",c);}
ss(4099,70000);
my(p=4099+0);
\\ class number of first example
E=ellinit([1,4]*Mod(1,4099));if(type(E)=="t_VEC",t=ellap(E);print("sample a=1: t=",t," h=",quadclassunit(t^2-4*4099).no," card=",ellcard(E)));
