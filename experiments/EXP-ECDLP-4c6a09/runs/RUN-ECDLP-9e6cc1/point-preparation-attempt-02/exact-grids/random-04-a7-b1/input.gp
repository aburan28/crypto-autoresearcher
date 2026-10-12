default(parisizemax,2000000000);default(nbthreads,1);setrand(1);
bitheight(P)={my(H=0,V);if(#P==1,return(0));for(i=1,2,for(j=0,2,V=polcoef(lift(P[i]),j);H=max(H,if(numerator(V),logint(abs(numerator(V)),2)+1,0));H=max(H,logint(denominator(V),2)+1)));H};
reduce_point(N,P,PR,MP)={if(#P==1,return([0]));if(nfeltval(N,P[1],PR)<0,return([0]));[lift(trace(nfmodpr(N,P[1],MP))),lift(trace(nfmodpr(N,P[2],MP)))]};
{main()=
my(N=nfinit((2)*y^0+(-1)*y^1+(3)*y^2+(1)*y^3),EK=ellinit([0,0,0,7,1],N),S=[[Mod((0/1)*y^0+(0/1)*y^1+(0/1)*y^2,N.pol),Mod((1/1)*y^0+(0/1)*y^1+(0/1)*y^2,N.pol)],[Mod((3/1)*y^0+(0/1)*y^1+(0/1)*y^2,N.pol),Mod((7/1)*y^0+(0/1)*y^1+(0/1)*y^2,N.pol)]],D,IDX,DIR,STEPS,TAB,P,I,DELTA,OLD,T,B,NB,MAXBITS,PI,PR,MP,RED,HASH,DT,EP);
for(bi=1,1,B=[4][bi];D=concat([0],vector(2*B,j,if(j%2,(j+1)/2,-j/2)));NB=#D^#S;
for(rep=1,3,
gettime();STEPS=vector(#S,i,vector(4*B+1,j,ellmul(EK,S[i],j-2*B-1)));DT=gettime();print("@@NF_PRECOMPUTE|",B,"|",rep,"|",DT,"|",#S*4*B);
IDX=vector(#S,i,1);DIR=vector(#S,i,1);TAB=vector(NB);P=[0];MAXBITS=0;
gettime();for(ti=1,NB,TAB[ti]=P;MAXBITS=max(MAXBITS,bitheight(P));I=#S;while(I>0 && (IDX[I]+DIR[I]<1 || IDX[I]+DIR[I]>#D),DIR[I]=-DIR[I];I--);if(!I,break);OLD=D[IDX[I]];IDX[I]+=DIR[I];DELTA=D[IDX[I]]-OLD;P=elladd(EK,P,STEPS[I][DELTA+2*B+1]));
DT=gettime();print("@@NF_GENERATE|",B,"|",rep,"|",NB,"|",NB-1,"|",DT,"|",MAXBITS);
for(kj=1,3,PI=(2^([6,7,12][kj]))^3-2^([6,7,12][kj])-1;
if(!#polrootsmod(N.pol,PI),next);
OLD=vecmin(lift(polrootsmod(N.pol,PI)));
PR=idealprimedec(N,PI);I=0;for(j=1,#PR,if(PR[j][4]==1 && lift(trace(nfmodpr(N,Mod(y,N.pol),PR[j])))==OLD,I=j;break));if(!I,error("Missing chosen prime"));PR=PR[I];MP=nfmodprinit(N,PR);
EP=ellinit([0,0,0,7,1],PI);
HASH=0;gettime();for(ti=1,NB,RED=reduce_point(N,TAB[ti],PR,MP);if(!ellisoncurve(EP,RED),error("Grid reduction off curve"));HASH=(HASH*1000003+if(#RED==1,0,RED[1]+PI*RED[2]+1))%2305843009213693951;if(rep==1,print("@@POINT|",B,"|",kj,"|",ti,"|",if(#RED==1,"O",Str(RED[1],",",RED[2])))));DT=gettime();print("@@NF_REDUCE|",B,"|",rep,"|",kj,"|",NB,"|",DT,"|",HASH);
);););};
iferr(main(),E,print("@@ERROR|",E));print("@@DONE");quit;
