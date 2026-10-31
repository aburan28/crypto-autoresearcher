#pragma once
#include <algorithm>
#include <bit>
#include <cstdint>
#include <fstream>
#include <numeric>
#include <sstream>
#include <stdexcept>
#include <string>
#include <tuple>
#include <vector>

namespace lab {
using I=std::int64_t;
inline void require(bool test,const std::string& message) { if(!test) throw std::runtime_error(message); }
inline bool prime(I n) { if(n<2)return false;for(I d=2;d<=n/d;++d)if(n%d==0)return false;return true; }
inline unsigned bits(std::uint64_t n) { return static_cast<unsigned>(std::bit_width(n)); }
struct Point {
 I x=0,y=0; bool inf=true;
 friend bool operator==(const Point&,const Point&)=default;
 friend bool operator<(const Point& x,const Point& y){return std::tie(x.inf,x.x,x.y)<std::tie(y.inf,y.x,y.y);}
};
struct Curve {
 I p=0,a=0,b=0;
 I mod(I n) const { n%=p;return n<0?n+p:n; }
 I pow(I x,I n) const {I v=1;x=mod(x);for(;n;n>>=1,x=mod(x*x))if(n&1)v=mod(v*x);return v;}
 I inv(I x) const {x=mod(x);require(x!=0,"inverse of zero");return pow(x,p-2);}
 bool valid(Point q) const {if(q.inf)return q.x==0&&q.y==0;return q.x>=0&&q.x<p&&q.y>=0&&q.y<p&&mod(q.y*q.y)==mod(q.x*q.x*q.x+a*q.x+b);}
 Point neg(Point q) const {require(valid(q),"invalid point in negation");return q.inf?q:Point{q.x,mod(-q.y),false};}
 Point add(Point q,Point s) const {
  require(valid(q)&&valid(s),"invalid point in addition");if(q.inf)return s;if(s.inf)return q;
  if(q.x==s.x&&mod(q.y+s.y)==0)return {};
  I slope=q==s?mod((3*q.x*q.x+a)*inv(2*q.y)):mod((s.y-q.y)*inv(s.x-q.x));
  I x=mod(slope*slope-q.x-s.x);return {x,mod(slope*(q.x-x)-q.y),false};
 }
 Point mul(Point q,std::uint64_t n) const {require(valid(q),"invalid point in multiplication");Point z{};for(;n;n>>=1,q=add(q,q))if(n&1U)z=add(z,q);return z;}
 std::vector<Point> points() const {
  std::vector<std::vector<I>> roots(static_cast<std::size_t>(p));
  for(I y=0;y<p;++y)roots[static_cast<std::size_t>(mod(y*y))].push_back(y);
  std::vector<Point> out{{}};for(I x=0;x<p;++x)for(I y:roots[static_cast<std::size_t>(mod(x*x*x+a*x+b))])out.push_back({x,y,false});return out;
 }
};
struct Fixture { std::string id,stratum; Curve c; Point P; I r=0,N=0; std::uint64_t seed=0; };
struct RNG {
 std::uint64_t state;
 explicit RNG(std::uint64_t seed):state(seed){}
 std::uint64_t next(){state+=0x9e3779b97f4a7c15ULL;std::uint64_t z=state;z=(z^(z>>30))*0xbf58476d1ce4e5b9ULL;z=(z^(z>>27))*0x94d049bb133111ebULL;return z^(z>>31);}
 std::uint64_t bounded(std::uint64_t n){require(n!=0,"zero RNG bound");const auto threshold=(std::uint64_t{0}-n)%n;for(;;){const auto x=next();if(x>=threshold)return x%n;}}
 void shuffle(std::vector<I>& v){for(std::size_t i=v.size();i>1;--i)std::swap(v[i-1],v[static_cast<std::size_t>(bounded(i))]);}
};
inline std::string json_quote(const std::string& s){std::string out="\"";for(char raw:s){const auto c=static_cast<unsigned char>(raw);if(c=='\"'||c=='\\'){out+='\\';out+=static_cast<char>(c);}else if(c=='\n')out+="\\n";else if(c=='\r')out+="\\r";else if(c=='\t')out+="\\t";else{require(c>=32,"unsupported control character in JSON");out+=static_cast<char>(c);}}return out+'\"';}
inline void certify(const Fixture& f){
 const auto& c=f.c;require(c.p>3&&c.p<=65535&&prime(c.p),"unsupported or composite field");
 require(c.a>=0&&c.a<c.p&&c.b>=0&&c.b<c.p,"noncanonical curve");
 require(c.mod(4*c.a*c.a*c.a+27*c.b*c.b)!=0,"singular curve");
 require(prime(f.r)&&f.r>2&&f.r!=c.p&&f.r<=65535,"invalid subgroup order");
 require(!f.P.inf&&c.valid(f.P),"invalid base point");
 require(c.mul(f.P,static_cast<std::uint64_t>(f.r)).inf,"base point order certificate fails");
 require(f.N>0&&f.N%f.r==0&&f.N!=c.p,"invalid/anomalous whole curve order");
 require(static_cast<I>(c.points().size())==f.N,"point count certificate fails");
 if(f.stratum=="main"){
  require(c.a!=0&&c.b!=0,"special j in main stratum");
  // For p>3, supersingular curves have trace zero. Explicitly reject it.
  require(f.N!=c.p+1,"supersingular main fixture");
 }
 if(f.stratum=="endo_j0")require(c.a==0&&c.b!=0&&c.p%3==1,"invalid j=0 stratum");
 if(f.stratum=="ordinary"||f.stratum=="power5") {
  require(c.a!=0&&c.b!=0&&f.N!=c.p+1,"special/supersingular follow-up fixture");
  require(std::gcd(f.N/f.r,f.r)==1,"cofactor shares subgroup factor");
  if(f.stratum=="power5")require(c.p%5==1,"power5 field condition fails");
 }
}
inline std::vector<Point> orbit(const Fixture& f){std::vector<Point> out;out.reserve(static_cast<std::size_t>(f.r));Point q{};for(I k=0;k<f.r;++k){out.push_back(q);q=f.c.add(q,f.P);}require(q.inf,"orbit does not close");return out;}
inline std::vector<Fixture> read_fixtures(const std::string& path){
 std::ifstream in(path);require(static_cast<bool>(in),"cannot read fixture file");std::string line;std::vector<Fixture> out;
 while(std::getline(in,line)){if(line.empty()||line[0]=='#'||line.rfind("id\t",0)==0)continue;
  std::istringstream row(line);Fixture f;row>>f.id>>f.stratum>>f.c.p>>f.c.a>>f.c.b>>f.P.x>>f.P.y>>f.r>>f.N>>f.seed;require(!row.fail(),"bad fixture row");f.P.inf=false;certify(f);out.push_back(f);
 }require(!out.empty(),"empty fixture panel");return out;
}
}
