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
 bool valid(Point q) const {if(q.inf)return q.x==0&&q.y==0;return q.x>=0&&q.x<p&&q.y>=0&&q.y<p&&mod(q.y*q.y)==mod(mod(q.x*q.x)*q.x+a*q.x+b);}
 Point neg(Point q) const {require(valid(q),"invalid point in negation");return q.inf?q:Point{q.x,mod(-q.y),false};}
 Point add(Point q,Point s) const {
  require(valid(q)&&valid(s),"invalid point in addition");if(q.inf)return s;if(s.inf)return q;
  if(q.x==s.x&&mod(q.y+s.y)==0)return {};
  I slope=q==s?mod(mod(3*mod(q.x*q.x)+a)*inv(2*q.y)):mod((s.y-q.y)*inv(s.x-q.x));
  I x=mod(slope*slope-q.x-s.x);return {x,mod(slope*(q.x-x)-q.y),false};
 }
 Point mul(Point q,std::uint64_t n) const {require(valid(q),"invalid point in multiplication");Point z{};for(;n;n>>=1,q=add(q,q))if(n&1U)z=add(z,q);return z;}

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
}
