// Direct completion enumerator. Input is diagnostic paid predicate-label table.
// Never an attack executor: equality checks use a separately certified full orbit.
// No random draws, early success return, candidate cap, or outcome cutoff.
#include <algorithm>
#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <vector>
using U=uint64_t;
int main(){
 try {
  U r; unsigned L,curve_index;
  if(!(std::cin>>r>>L>>curve_index)||r<3||r>2147483647ULL||L<2||L>31||L!=static_cast<unsigned>(65-__builtin_clzll(r))) throw std::runtime_error("invalid header");
  std::vector<int> bits(r);
  for(U i=0;i<r;++i) if(!(std::cin>>bits[i])||bits[i]<-1||bits[i]>1) throw std::runtime_error("incomplete/invalid table");
  int extra; if(std::cin>>extra) throw std::runtime_error("trailing table data");
  std::vector<uint32_t> marks(r,0); uint32_t epoch=0;
  const U D=1ULL<<L;
  for(U s=1;s<r;++s){
   U V=0,mask=0,u=s; unsigned hd=0; std::vector<unsigned> erased,defined;
   for(unsigned i=0;i<L;++i){
    unsigned shift=L-1-i; int b=bits[u];
    if(b<0){erased.push_back(shift);mask|=1ULL<<shift;}
    else {defined.push_back(shift);V|=U(b)<<shift;hd+=unsigned(b)!=unsigned(u>r/2);}
    u=2*u%r;
   }
   unsigned e=erased.size();
   std::cout<<'['<<curve_index<<','<<s<<','<<V<<','<<mask<<','<<e<<','<<hd<<",[";
   for(unsigned t=0;t<=2;++t)for(unsigned ec: {0U,2U}){
    if(t||ec)std::cout<<',';
    U wc=0,legal=0,zero=0,M=0,hit=0,tt=0,tf=0,ot=0,of=0,weights[3]={0,0,0};
    bool capped=e>ec;
    if(++epoch==0){std::fill(marks.begin(),marks.end(),0);epoch=1;}
    auto visit=[&](U word,unsigned weight){
     ++wc;++weights[weight]; U k=(r*word+D-1)/D;
     bool ok=k<r&&D*k<r*(word+1);
     if(!ok)return;
     ++legal;
     // Two separate diagnostic orbit-equation certifications, including k=0.
     bool transformed=k==s;bool original=k==s;
     if(transformed)++tt;else ++tf;
     if(original)++ot;else ++of;
     if(k==0)++zero;
     else if(marks[k]!=epoch){marks[k]=epoch;++M;}
     if(transformed&&original)hit=1;
    };
    if(!capped)for(U assignment=0;assignment<(1ULL<<e);++assignment){
     U W=V;
     for(unsigned j=0;j<e;++j)W|=((assignment>>(e-1-j))&1ULL)<<erased[j];
     visit(W,0);
     if(t>=1)for(unsigned j=0;j<defined.size();++j)visit(W^(1ULL<<defined[j]),1);
     if(t>=2)for(unsigned j=0;j<defined.size();++j)for(unsigned k=j+1;k<defined.size();++k)visit(W^(1ULL<<defined[j])^(1ULL<<defined[k]),2);
    }
    U expected=capped?0:(1ULL<<e)*(1+(t>=1?defined.size():0)+(t>=2?defined.size()*(defined.size()-1)/2:0));
    if(wc!=expected||M>r-1||tt+tf!=legal||ot+of!=legal)throw std::runtime_error("internal count invariant");
    unsigned status=capped?4:hit?0:wc&&legal==0?2:3;
    if(t==0&&ec==0&&e)status=1;
    std::cout<<'['<<status<<','<<wc<<','<<legal<<','<<wc-legal<<','<<zero<<','<<M<<','<<hit<<','<<tt<<','<<tf<<','<<ot<<','<<of<<','<<weights[0]<<','<<weights[1]<<','<<weights[2]<<']';
   }
   std::cout<<"]]\n";
   if(!std::cout)throw std::runtime_error("output failed");
  }
  return 0;
 }catch(const std::exception& e){std::cerr<<"census refused: "<<e.what()<<'\n';return 2;}
}
