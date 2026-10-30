#include "common.hpp"
#include <array>
#include <iostream>
#include <random>
#include <set>

int main(int argc,char** argv) {
 try {
  lab::require(argc==7,"usage: prepare_inputs FIXTURES HISTORY PUBLIC_TARGETS PRIVATE_TRUTH PRIVATE_SEEDS EXCLUDE_FIXTURES");
  for(int i=1;i<6;++i){std::ifstream existing(argv[i]);lab::require(!existing.good(),"refuse existing preparation output");}
  std::ofstream out(argv[1]),hist(argv[2]),targets(argv[3]),truth(argv[4]),seeds(argv[5]);
  lab::require(bool(out)&&bool(hist)&&bool(targets)&&bool(truth)&&bool(seeds),"cannot create preparation outputs");
  std::set<std::tuple<lab::I,lab::I,lab::I>> used;
  for(const auto& f:lab::read_fixtures(argv[6]))used.emplace(f.c.p,f.c.a,f.c.b);
  lab::RNG curve_rng(0x20261025c0ffeeULL);std::uint64_t attempts=0;unsigned accepted=0;
  std::vector<lab::Fixture> panel;
  out<<"id\tstratum\tp\ta\tb\tPx\tPy\tr\tN\tseed\n";
  for(unsigned s:{8U,10U,12U})for(const std::string stratum:{"ordinary","power5"})for(unsigned index=0;index<4;) {
   const auto seed=curve_rng.next();lab::RNG draw(seed);const lab::I lo=lab::I{1}<<(s-1),hi=lab::I{1}<<(s+1);
   lab::I p=lo+static_cast<lab::I>(draw.bounded(static_cast<std::uint64_t>(hi-lo)));if(p%2==0)++p;while(p<hi&&!lab::prime(p))p+=2;
   lab::Fixture f;f.seed=seed;f.stratum=stratum;f.c.p=p;std::string reason;
   if(p>=hi||p<=3)reason="range";
   else if(stratum=="power5"&&p%5!=1)reason="p_mod5";
   else {
    f.c.a=1+static_cast<lab::I>(draw.bounded(static_cast<std::uint64_t>(p-1)));
    f.c.b=1+static_cast<lab::I>(draw.bounded(static_cast<std::uint64_t>(p-1)));
    if(used.contains({p,f.c.a,f.c.b}))reason="duplicate";
    else if(f.c.mod(4*f.c.a*f.c.a*f.c.a+27*f.c.b*f.c.b)==0)reason="singular";
    else {
     const auto points=f.c.points();f.N=static_cast<lab::I>(points.size());
     if(f.N==p||f.N==p+1)reason="anomalous_or_trace0";
     else {
      for(lab::I r=lo;r<(lab::I{1}<<s);++r)if(lab::prime(r)&&r!=p&&f.N%r==0&&std::gcd(f.N/r,r)==1)f.r=r;
      if(f.r==0)reason="r_size";
      else {
       for(auto q:points){q=f.c.mul(q,static_cast<std::uint64_t>(f.N/f.r));if(!q.inf){f.P=q;break;}}
       if(f.P.inf)reason="cofactor_zero";
       else {
        f.id="followup-"+stratum+"-r"+std::to_string(s)+"-"+std::to_string(index);lab::certify(f);
        lab::I census=1;for(lab::I x=0;x<p;++x){const auto rhs=f.c.mod(x*x*x+f.c.a*x+f.c.b);census+=rhs==0?1:(f.c.pow(rhs,(p-1)/2)==1?2:0);}
        lab::require(census==f.N,"independent curve count disagrees");
        out<<f.id<<'\t'<<stratum<<'\t'<<p<<'\t'<<f.c.a<<'\t'<<f.c.b<<'\t'<<f.P.x<<'\t'<<f.P.y<<'\t'<<f.r<<'\t'<<f.N<<'\t'<<seed<<'\n';
        used.emplace(p,f.c.a,f.c.b);panel.push_back(f);++index;++accepted;reason="accepted";
       }
      }
     }
    }
   }
   ++attempts;hist<<"{\"i\":"<<attempts<<",\"s\":"<<s<<",\"t\":"<<lab::json_quote(stratum)<<",\"seed\":"<<seed<<",\"p\":"<<p<<",\"a\":"<<f.c.a<<",\"b\":"<<f.c.b<<",\"N\":"<<f.N<<",\"o\":"<<lab::json_quote(reason)<<"}\n";
  }
  std::random_device os;std::array<std::uint32_t,8> words{};for(auto& w:words)w=os();
  std::seed_seq seed_sequence(words.begin(),words.end());std::mt19937_64 target_rng(seed_sequence);
  seeds<<"{\"purpose\":\"custodian-only target generation seed; reveal after candidate outputs sealed\",\"seed_words\":[";
  for(std::size_t i=0;i<words.size();++i){if(i)seeds<<',';seeds<<words[i];}seeds<<"]}\n";
  targets<<"fixture_id\ttarget_id\tQx\tQy\tQinf\n";truth<<"fixture_id\ttarget_id\tk\n";
  for(const auto& f:panel){std::uniform_int_distribution<lab::I> uniform(0,f.r-1);for(unsigned j=0;j<8;++j){const auto k=uniform(target_rng);const auto Q=f.c.mul(f.P,static_cast<std::uint64_t>(k));const auto id=f.id+"-t"+std::to_string(j);targets<<f.id<<'\t'<<id<<'\t'<<Q.x<<'\t'<<Q.y<<'\t'<<static_cast<unsigned>(Q.inf)<<'\n';truth<<f.id<<'\t'<<id<<'\t'<<k<<'\n';}}
  std::cout<<"{\"fixtures\":"<<accepted<<",\"candidate_curves\":"<<attempts<<",\"public_targets\":"<<panel.size()*8<<",\"scope\":\"input_preparation_only\"}\n";
 }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
