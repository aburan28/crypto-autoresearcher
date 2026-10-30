#include "common.hpp"
#include <iostream>
#include <set>

int main(int argc,char**argv){
 try{
  lab::require(argc==3,"usage: fixtures OUTPUT_TSV REJECTION_JSONL");
  std::ofstream out(argv[1]),history(argv[2]);lab::require(bool(out)&&bool(history),"cannot create fixture outputs");
  out<<"id\tstratum\tp\ta\tb\tPx\tPy\tr\tN\tseed\n";
  lab::RNG rng(0x25ec20261025ULL);std::set<std::tuple<lab::I,lab::I,lab::I>> used;
  std::uint64_t attempts=0;
  for(unsigned s: {5U,6U,8U,6U}){
   const std::string stratum=attempts!=0&&used.size()==6?"endo_j0":"main";
   for(unsigned index=0;index<2;){
    const auto seed=rng.next();lab::RNG candidate(seed);const lab::I lo=lab::I{1}<<(s-1),hi=lab::I{1}<<(s+1);
    lab::I p=lo+static_cast<lab::I>(candidate.next()%static_cast<std::uint64_t>(hi-lo));if(p%2==0)++p;
    while(!lab::prime(p)&&p<hi)p+=2;
    std::string reason;lab::Fixture f;f.seed=seed;f.stratum=stratum;f.c.p=p;
    if(p>=hi||p<=3)reason="prime_range";
    if(reason.empty()){
     f.c.a=stratum=="endo_j0"?0:1+static_cast<lab::I>(candidate.next()%static_cast<std::uint64_t>(p-1));
     f.c.b=1+static_cast<lab::I>(candidate.next()%static_cast<std::uint64_t>(p-1));
     if(stratum=="endo_j0"&&p%3!=1)reason="endo_field";
     else if(used.contains({p,f.c.a,f.c.b}))reason="duplicate";
     else if(f.c.mod(4*f.c.a*f.c.a*f.c.a+27*f.c.b*f.c.b)==0)reason="singular";
     else{
      const auto points=f.c.points();f.N=static_cast<lab::I>(points.size());
      if(f.N==p||f.N==p+1)reason="anomalous_or_trace_zero";
      else{
       for(lab::I r=lo;r<(lab::I{1}<<s);++r)if(lab::prime(r)&&r!=p&&f.N%r==0)f.r=r;
       if(f.r==0)reason="subgroup_size";
       else{
        for(auto q:points){q=f.c.mul(q,static_cast<std::uint64_t>(f.N/f.r));if(!q.inf){f.P=q;break;}}
        if(f.P.inf)reason="cofactor_projection_zero";
        else{
         f.id="pilot-"+stratum+"-r"+std::to_string(s)+"-"+std::to_string(index);
         lab::certify(f);
         // Independent point-count formula using Euler's criterion.
         lab::I count=1;for(lab::I x=0;x<p;++x){auto rhs=f.c.mod(x*x*x+f.c.a*x+f.c.b);count+=rhs==0?1:(f.c.pow(rhs,(p-1)/2)==1?2:0);}
         lab::require(count==f.N,"independent point count disagrees");
         out<<f.id<<'\t'<<stratum<<'\t'<<p<<'\t'<<f.c.a<<'\t'<<f.c.b<<'\t'<<f.P.x<<'\t'<<f.P.y<<'\t'<<f.r<<'\t'<<f.N<<'\t'<<seed<<'\n';
         used.emplace(p,f.c.a,f.c.b);++index;reason="accepted";
        }
       }
      }
     }
    }
    ++attempts;history<<"{\"candidate\":"<<attempts<<",\"seed\":"<<seed<<",\"stratum\":"<<lab::json_quote(stratum)<<",\"r_bits\":"<<s<<",\"p\":"<<p<<",\"a\":"<<f.c.a<<",\"b\":"<<f.c.b<<",\"N\":"<<f.N<<",\"outcome\":"<<lab::json_quote(reason)<<"}\n";
   }
  }
  std::cout<<"{\"fixtures\":"<<used.size()<<",\"candidates\":"<<attempts<<",\"scope\":\"fixture_preparation_only\"}\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}
}
