\\ FEASIBILITY PROBE ONLY
NN=1009; found=0;
{
for(ss=1,8, for(yq=1,8, tt=2+NN*ss; yv=NN*yq; qq=tt^2+3*yv^2; if(qq%4!=0,next); pp=qq\4; if(!isprime(pp),next);
  okb=0; for(bb=1,30, EE=ellinit([0,bb],pp); if(ellcard(EE)==pp+1-tt, okb=bb; break));
  if(okb>0, EE=ellinit([0,okb],pp); print("s=",ss," y'=",yq," p=",pp," bits=",#binary(pp)," b=",okb," group=",ellgroup(EE)," cofactor primes=",factor((pp-1)\NN)[,1]~); found++)));
print("found ",found);
}
quit;
