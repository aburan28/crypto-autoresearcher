// Independent Jacobian public-point verification of recorded candidate and baseline scalars.
// This code imports no producer/common arithmetic and never reads scalar truth.
#include <cstdint>
#include <fstream>
#include <iostream>
#include <map>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <tuple>

namespace check {
using I=std::int64_t;
void need(bool b,const std::string& s){if(!b)throw std::runtime_error(s);}
struct P {I x=0,y=0;bool inf=true;friend bool operator==(const P&,const P&)=default;};
struct J {I x=0,y=1,z=0;};
struct C {
 I p=0,a=0,b=0;
 I m(I x)const{x%=p;return x<0?x+p:x;}
 I power(I x,I n)const{I z=1;for(;n;n>>=1,x=m(x*x))if(n&1)z=m(z*x);return z;}
 bool valid(P q)const{return q.inf?(q.x==0&&q.y==0):(q.x>=0&&q.x<p&&q.y>=0&&q.y<p&&m(q.y*q.y)==m(q.x*q.x*q.x+a*q.x+b));}
 J project(P q)const{return q.inf?J{}:J{q.x,q.y,1};}
 J twice(J q)const{
  if(q.z==0||q.y==0)return {};
  I yy=m(q.y*q.y),yyyy=m(yy*yy),zz=m(q.z*q.z),s=m(4*q.x*yy),v=m(3*q.x*q.x+a*m(zz*zz));
  I x=m(v*v-2*s);return {x,m(v*(s-x)-8*yyyy),m(2*q.y*q.z)};
 }
 J add(J q,J t)const{
  if(q.z==0)return t;
  if(t.z==0)return q;
  I z1=m(q.z*q.z),z2=m(t.z*t.z),u1=m(q.x*z2),u2=m(t.x*z1);
  I s1=m(q.y*m(t.z*z2)),s2=m(t.y*m(q.z*z1));
  if(u1==u2)return s1==s2?twice(q):J{};
  I h=m(u2-u1),v=m(4*h*h),j=m(h*v),r=m(2*(s2-s1)),w=m(u1*v),x=m(r*r-j-2*w);
  return {x,m(r*(w-x)-2*s1*j),m(2*q.z*t.z*h)};
 }
 P affine(J q)const{if(q.z==0)return {};I z=power(q.z,p-2),z2=m(z*z);return {m(q.x*z2),m(q.y*m(z*z2)),false};}
 P mul(P q,I n)const{need(valid(q)&&n>=0,"bad multiplication input");J z{},v=project(q);for(;n;n>>=1,v=twice(v))if(n&1)z=add(z,v);return affine(z);}
};
bool prime(I n){if(n<2)return false;for(I d=2;d<=n/d;++d)if(n%d==0)return false;return true;}
struct F {C c;P p;I r=0;};
using Target=std::pair<std::string,std::string>;
using Case=std::tuple<std::string,std::string,std::string>;
struct Result {std::set<I> candidates;I hits=0,scalar=-1;};
std::map<std::string,F> fixtures(const std::string& path){
 std::ifstream in(path);need(bool(in),"fixture file");std::string line;need(bool(std::getline(in,line)),"fixture header");need(line=="id\tstratum\tp\ta\tb\tPx\tPy\tr\tN\tseed","fixture header mismatch");
 std::map<std::string,F> out;
 while(std::getline(in,line)){if(line.empty())continue;std::istringstream row(line);std::string id,stratum;std::uint64_t seed=0;I order=0;F f;
  row>>id>>stratum>>f.c.p>>f.c.a>>f.c.b>>f.p.x>>f.p.y>>f.r>>order>>seed;need(!row.fail(),"fixture row");std::string extra;need(!(row>>extra),"fixture columns");f.p.inf=false;
  need(f.c.p>3&&f.c.p<(I{1}<<20)&&prime(f.c.p)&&f.r>2&&prime(f.r),"field/order bounds");need(f.c.a>=0&&f.c.a<f.c.p&&f.c.b>=0&&f.c.b<f.c.p,"curve range");need(f.c.m(4*f.c.a*f.c.a*f.c.a+27*f.c.b*f.c.b)!=0,"singular curve");
  need(f.c.valid(f.p)&&f.c.mul(f.p,f.r).inf,"independent subgroup certificate");need(out.emplace(id,f).second,"duplicate fixture");
 }need(!out.empty(),"empty fixtures");return out;
}
std::map<Target,P> targets(const std::string& path,const std::map<std::string,F>& fs){
 std::ifstream in(path);need(bool(in),"target file");std::string line;need(bool(std::getline(in,line)),"target header");need(line=="fixture_id\ttarget_id\tQx\tQy\tQinf"||line=="fixture_id target_id Qx Qy Qinf","target header mismatch");std::map<Target,P> out;
 while(std::getline(in,line)){if(line.empty())continue;std::istringstream row(line);std::string fixture,target,extra;P q;I inf=0;row>>fixture>>target>>q.x>>q.y>>inf;need(!row.fail()&&!(row>>extra)&&(inf==0||inf==1),"target row");q.inf=inf!=0;
  auto f=fs.find(fixture);need(f!=fs.end()&&f->second.c.valid(q),"invalid target");need(f->second.c.mul(q,f->second.r).inf,"target outside subgroup");need(out.emplace(Target{fixture,target},q).second,"duplicate target");
 }need(!out.empty(),"empty targets");return out;
}
void verify(const std::string& fpath,const std::string& tpath,const std::string& cpath,const std::string& opath){
 auto fs=fixtures(fpath);auto qs=targets(tpath,fs);std::ifstream in(cpath);need(bool(in),"candidate file");std::string line;need(bool(std::getline(in,line)),"candidate header");need(line=="fixture_id\ttarget_id\tcase_id\tcandidate","candidate header mismatch");
 std::map<Case,Result> cases;std::set<Case> empty_cases;std::uint64_t tested=0;
 while(std::getline(in,line)){if(line.empty())continue;std::istringstream row(line);std::string fixture,target,id,extra;I k=0;row>>fixture>>target>>id>>k;need(!row.fail()&&!(row>>extra),"candidate row");auto f=fs.find(fixture);auto q=qs.find({fixture,target});need(f!=fs.end()&&q!=qs.end()&&!id.empty(),"unknown candidate target");Case key{fixture,target,id};auto& result=cases[key];
  if(k==-1){need(result.candidates.empty()&&empty_cases.insert(key).second,"duplicate or mixed empty case");continue;}
  need(k>=0&&k<f->second.r&&empty_cases.count(key)==0,"candidate range");need(result.candidates.insert(k).second,"duplicate candidate");need(result.candidates.size()<=1024,"candidate list too large");
  if(f->second.c.mul(f->second.p,k)==q->second){++result.hits;result.scalar=k;}++tested;
 }
 std::ofstream out(opath);need(bool(out),"verification output");out<<"fixture_id\ttarget_id\tcase_id\tcandidate_count\tverification_hits\tverified_scalar\n";
 std::uint64_t recovered=0;for(const auto& [key,result]:cases){const auto& [fixture,target,id]=key;need(result.hits<=1,"multiple discrete-log answers");out<<fixture<<'\t'<<target<<'\t'<<id<<'\t'<<result.candidates.size()<<'\t'<<result.hits<<'\t'<<result.scalar<<'\n';if(result.hits)++recovered;}
 need(!cases.empty(),"no candidate cases");std::cout<<"{\"status\":\"independent_public_equations_pass\",\"candidate_cases\":"<<cases.size()<<",\"candidate_scalars_checked\":"<<tested<<",\"recovered_cases\":"<<recovered<<",\"arithmetic\":\"independently_coded_Jacobian\",\"hidden_scalar_labels_read\":false}\n";
}
void self_test(){
 std::uint64_t checks=0;auto test=[&](bool b,const std::string& why){++checks;need(b,why);};
 C c{17,2,2};P p{5,1,false};test(c.valid(p),"base");test(c.mul(p,0)==P{},"zero");test(c.mul(p,1)==p,"one");test(c.mul(p,2)==P{6,3,false},"two");test(c.mul(p,3)==P{10,6,false},"three");test(c.mul(p,18)==P{5,16,false},"r-minus-one");test(c.mul(p,19).inf,"order");test(c.mul(p,3)!=c.mul(p,4),"wrong witness mutation");
 for(I k=0;k<19;++k){auto q=c.mul(p,k);test(c.valid(q),"curve");test(c.affine(c.add(c.project(q),c.project(p)))==c.mul(p,(k+1)%19),"addition");}
 C large{524287,0,1};P low{0,1,false};test(prime(large.p),"large field prime");test(large.valid(low),"large field point");test(large.mul(low,0).inf,"large k0");test(large.mul(low,1)==low,"large k1");test(large.mul(low,2)==P{0,524286,false},"large r-minus-one");test(large.mul(low,3).inf,"large subgroup order");
 C near{1048573,1048572,1};P high{1048572,1,false};test(prime(near.p),"near guard prime");test(near.valid(high),"safe modular cubic near guard");test(near.valid(near.mul(high,2)),"near guard doubling");test(near.valid(near.mul(high,19)),"near guard multiplication");test(!large.valid(P{0,2,false}),"mutated y");test(!large.valid(P{524287,1,false}),"noncanonical x");test(!large.valid(P{1,0,true}),"noncanonical infinity");
 C outside{17,0,1};test(outside.valid(P{1,6,false}),"outside point on curve");test(!outside.mul(P{1,6,false},3).inf,"outside subgroup rejected");
 std::cout<<"{\"self_test\":\"pass\",\"checks\":"<<checks<<",\"scope\":\"verification_development_only\"}\n";
}
}
int main(int argc,char** argv){try{if(argc==2&&std::string(argv[1])=="--self-test"){check::self_test();return 0;}if(argc==6&&std::string(argv[1])=="--verify"){check::verify(argv[2],argv[3],argv[4],argv[5]);return 0;}std::cerr<<"usage: verify-candidates --self-test | --verify FIXTURES TARGETS CANDIDATES OUTPUT\n";return 2;}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
