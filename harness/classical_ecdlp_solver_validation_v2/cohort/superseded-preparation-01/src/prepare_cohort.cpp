#include "common.hpp"
#include <array>
#include <iostream>
#include <random>
#include <set>

namespace {
using lab::I;
using lab::Fixture;
using lab::Point;
constexpr std::uint64_t curve_seed=0x20261025ec0124ULL;
constexpr I max_p=I{1}<<19;

struct RootCensus {
 std::vector<I> first;
 I count=1;
 explicit RootCensus(const lab::Curve& c):first(static_cast<std::size_t>(c.p),-1) {
  std::vector<unsigned char> multiplicity(static_cast<std::size_t>(c.p));
  for(I y=0;y<c.p;++y) {
   const auto index=static_cast<std::size_t>(c.mod(y*y));
   if(first[index]<0)first[index]=y;
   ++multiplicity[index];
  }
  for(I x=0;x<c.p;++x)count+=multiplicity[static_cast<std::size_t>(c.mod(x*x*x+c.a*x+c.b))];
 }
};

I euler_census(const lab::Curve& c) {
 I count=1;
 for(I x=0;x<c.p;++x) {
  const I value=c.mod(x*x*x+c.a*x+c.b);
  if(value==0)++count;
  else if(c.pow(value,(c.p-1)/2)==1)count+=2;
 }
 return count;
}

I selected_factor(I n,unsigned target_bits) {
 I selected=0,remaining=n;
 auto consider=[&](I q) {
  if(lab::bits(static_cast<std::uint64_t>(q))==target_bits&&lab::prime(q)&&
     std::gcd(n/q,q)==1)selected=std::max(selected,q);
 };
 for(I d=2;d<=remaining/d;++d)if(remaining%d==0) {
  consider(d);
  while(remaining%d==0)remaining/=d;
 }
 if(remaining>1)consider(remaining);
 return selected;
}

void basic_certificate(const Fixture& f) {
 const auto& c=f.c;
 lab::require(c.p>3&&c.p<max_p&&lab::prime(c.p),"unsupported or composite field");
 lab::require(c.a>0&&c.a<c.p&&c.b>0&&c.b<c.p,"special-j or noncanonical curve");
 lab::require(c.mod(4*c.a*c.a*c.a+27*c.b*c.b)!=0,"singular curve");
 lab::require(lab::prime(f.r)&&f.r>2&&f.r<(I{1}<<18)&&f.r!=c.p,"bad subgroup order");
 lab::require(f.N>0&&f.N%f.r==0&&std::gcd(f.N/f.r,f.r)==1,"bad cofactor");
 lab::require(f.N!=c.p&&f.N!=c.p+1,"anomalous or supersingular curve");
 lab::require(!f.P.inf&&c.valid(f.P)&&c.mul(f.P,static_cast<std::uint64_t>(f.r)).inf,"point order certificate fails");
 if(f.stratum=="power5")lab::require(c.p%5==1,"wrong power5 field");
}

std::vector<Fixture> read_public(const std::string& path,bool certify) {
 std::ifstream in(path);lab::require(bool(in),"cannot read fixtures");
 std::vector<Fixture> out;std::string line;
 while(std::getline(in,line)) {
  if(line.empty()||line.rfind("id\t",0)==0||line[0]=='#')continue;
  std::istringstream row(line);Fixture f;
  row>>f.id>>f.stratum>>f.c.p>>f.c.a>>f.c.b>>f.P.x>>f.P.y>>f.r>>f.N>>f.seed;
  lab::require(!row.fail(),"bad fixture row");f.P.inf=false;
  if(certify)basic_certificate(f);
  out.push_back(f);
 }
 lab::require(!out.empty(),"empty fixture panel");return out;
}

void refuse_existing(const std::string& path) {
 std::ifstream in(path);lab::require(!in.good(),"refuse existing preparation output");
}

void self_test() {
 unsigned checks=0;
 for(I p:{5,7,11,17,23})for(I a=0;a<p;++a)for(I b=0;b<p;++b) {
  lab::Curve c{p,a,b};
  if(c.mod(4*a*a*a+27*b*b)==0)continue;
  RootCensus roots(c);
  lab::require(roots.count==euler_census(c),"root/Euler test mismatch");++checks;
  lab::require(roots.count==static_cast<I>(c.points().size()),"point enumeration mismatch");++checks;
 }
 for(const Fixture& f:std::vector<Fixture>{
   {"dev1","ordinary",{61,1,4},{41,55,false},19,57,1},
   {"dev2","ordinary",{37,29,3},{30,30,false},17,34,2},
   {"dev3","ordinary",{127,13,45},{26,68,false},41,123,3}}) {
  basic_certificate(f);++checks;
  Point point{};
  for(I k=0;k<f.r;++k) {
   lab::require(f.c.mul(f.P,static_cast<std::uint64_t>(k))==point,"scalar test mismatch");
   point=f.c.add(point,f.P);++checks;
  }
  lab::require(point.inf,"canonical scalar loop not closed");++checks;
 }
 lab::require(selected_factor(34,5)==17&&selected_factor(57,5)==19&&selected_factor(123,6)==41,"factor selector mismatch");++checks;
 lab::require(selected_factor(49,3)==0,"noncoprime cofactor admitted");++checks;
 std::cout<<"{\"kind\":\"input_generator_self_tests\",\"checks\":"<<checks<<",\"passed\":true}\n";
}

void generate_curves(const std::string& fixture_path,const std::string& history_path,const std::string& exclude_path) {
 refuse_existing(fixture_path);refuse_existing(history_path);
 std::ofstream out(fixture_path),hist(history_path);
 lab::require(bool(out)&&bool(hist),"cannot create curve outputs");
 std::set<std::tuple<I,I,I>> used;
 const auto exclusions=read_public(exclude_path,false);
 for(const auto& f:exclusions)used.emplace(f.c.p,f.c.a,f.c.b);
 lab::require(exclusions.size()==32&&used.size()==32,"expect all32 prior curves");
 lab::RNG rng(curve_seed);std::uint64_t attempt=0;unsigned accepted=0;
 out<<"id\tstratum\tp\ta\tb\tPx\tPy\tr\tN\tseed\n";
 for(unsigned bits:{12U,14U,16U,18U})for(const std::string stratum:{"ordinary","power5"})for(unsigned index=0;index<3;) {
  const auto seed=rng.next();lab::RNG draw(seed);const I lo=I{1}<<(bits-1),hi=I{1}<<(bits+1);
  I p=lo+static_cast<I>(draw.bounded(static_cast<std::uint64_t>(hi-lo)));if(p%2==0)++p;
  while(p<hi&&!lab::prime(p))p+=2;
  Fixture f;f.seed=seed;f.stratum=stratum;f.c.p=p;std::string reason;
  if(p>=hi||p<=3)reason="range";
  else if(stratum=="power5"&&p%5!=1)reason="p_mod5";
  else {
   f.c.a=1+static_cast<I>(draw.bounded(static_cast<std::uint64_t>(p-1)));
   f.c.b=1+static_cast<I>(draw.bounded(static_cast<std::uint64_t>(p-1)));
   if(used.contains({p,f.c.a,f.c.b}))reason="duplicate_curve";
   else if(f.c.mod(4*f.c.a*f.c.a*f.c.a+27*f.c.b*f.c.b)==0)reason="singular";
   else {
    const RootCensus roots(f.c);f.N=roots.count;
    if(f.N==p||f.N==p+1)reason="anomalous_or_trace0";
    else {
     f.r=selected_factor(f.N,bits);
     if(f.r==0||f.r==p)reason="r_size_or_anomalous";
     else {
      for(I x=0;x<p;++x) {
       const I y=roots.first[static_cast<std::size_t>(f.c.mod(x*x*x+f.c.a*x+f.c.b))];
       if(y<0)continue;
       const Point candidate=f.c.mul({x,y,false},static_cast<std::uint64_t>(f.N/f.r));
       if(!candidate.inf){f.P=candidate;break;}
      }
      if(f.P.inf)reason="cofactor_zero";
      else {
       f.id="sv-"+stratum+"-r"+std::to_string(bits)+"-"+std::to_string(index);
       basic_certificate(f);lab::require(euler_census(f.c)==f.N,"independent curve census mismatch");
       out<<f.id<<'\t'<<stratum<<'\t'<<p<<'\t'<<f.c.a<<'\t'<<f.c.b<<'\t'<<f.P.x<<'\t'<<f.P.y<<'\t'<<f.r<<'\t'<<f.N<<'\t'<<seed<<'\n';
       used.emplace(p,f.c.a,f.c.b);++index;++accepted;reason="accepted";
      }
     }
    }
   }
  }
  ++attempt;hist<<"{\"i\":"<<attempt<<",\"bits\":"<<bits<<",\"stratum\":"<<lab::json_quote(stratum)<<",\"seed\":"<<seed<<",\"p\":"<<p<<",\"a\":"<<f.c.a<<",\"b\":"<<f.c.b<<",\"N\":"<<f.N<<",\"r\":"<<f.r<<",\"outcome\":"<<lab::json_quote(reason)<<"}\n";
 }
 std::cout<<"{\"scope\":\"input_preparation_only\",\"fixtures\":"<<accepted<<",\"candidate_curves\":"<<attempt<<",\"seed\":"<<curve_seed<<"}\n";
}

void generate_targets(const std::string& fixture_path,const std::string& public_path,const std::string& truth_path,const std::string& seed_path) {
 for(const auto& p:{public_path,truth_path,seed_path})refuse_existing(p);
 const auto panel=read_public(fixture_path,true);lab::require(panel.size()==24,"wrong target fixture count");
 std::ofstream out(public_path),truth(truth_path),seeds(seed_path);
 lab::require(bool(out)&&bool(truth)&&bool(seeds),"cannot create target outputs");
 std::random_device os;std::array<std::uint32_t,8> words{};for(auto& word:words)word=os();
 std::seed_seq sequence(words.begin(),words.end());std::mt19937_64 rng(sequence);
 seeds<<"{\"purpose\":\"custodian-only target seed; reveal after outputs sealed\",\"seed_words\":[";
 for(std::size_t i=0;i<words.size();++i){if(i)seeds<<',';seeds<<words[i];}seeds<<"]}\n";
 out<<"fixture_id\ttarget_id\tQx\tQy\tQinf\n";truth<<"fixture_id\ttarget_id\tk\n";
 for(const auto& f:panel) {
  std::uniform_int_distribution<I> uniform(0,f.r-1);
  for(unsigned i=0;i<32;++i) {
   const I k=uniform(rng);const Point Q=f.c.mul(f.P,static_cast<std::uint64_t>(k));
   const auto id=f.id+"-t"+std::to_string(i);
   out<<f.id<<'\t'<<id<<'\t'<<Q.x<<'\t'<<Q.y<<'\t'<<static_cast<unsigned>(Q.inf)<<'\n';
   truth<<f.id<<'\t'<<id<<'\t'<<k<<'\n';
  }
 }
 std::cout<<"{\"scope\":\"input_preparation_only\",\"public_targets\":768,\"truth_input_to_candidate\":false}\n";
}
}

int main(int argc,char** argv) {
 try {
  lab::require(argc>=2,"expected --self-test, --curves or --targets");
  const std::string mode=argv[1];
  if(mode=="--self-test"){lab::require(argc==2,"bad self-test arguments");self_test();}
  else if(mode=="--curves"){lab::require(argc==5,"usage: --curves FIXTURES HISTORY EXCLUDED");generate_curves(argv[2],argv[3],argv[4]);}
  else if(mode=="--targets"){lab::require(argc==6,"usage: --targets FIXTURES PUBLIC PRIVATE_TRUTH PRIVATE_SEEDS");generate_targets(argv[2],argv[3],argv[4],argv[5]);}
  else throw std::runtime_error("unknown preparation mode");
 }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
