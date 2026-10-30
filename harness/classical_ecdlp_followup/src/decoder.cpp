// Public-input approximate coordinate-state decoder. Classical, toy, no speed claim.
#include "common.hpp"
#include <array>
#include <cmath>
#include <filesystem>
#include <functional>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <numeric>
#include <optional>
#include <set>

namespace dec {
using lab::I;
using U=std::uint64_t;
using V=std::vector<long double>;
constexpr unsigned training_samples=2048,calibration_samples=512,view_count=4;
constexpr const char* scope="exploratory_toy_followup";
#define DEC_COUNTERS(X) \
 X(field_additions) X(field_multiplications) X(field_power_calls) X(field_inversions) \
 X(group_additions) X(scalar_multiplications) X(sqrt_calls) X(sqrt_nonresidue_tests) \
 X(primality_divisor_tests) X(generator_factor_trials) X(rng_draws) \
 X(sampler_finite_attempts) X(sampler_rejections) X(subgroup_samples) \
 X(feature_evaluations) X(dp_multiply_add_terms) X(beam_children) \
 X(candidate_verifications) X(calibration_log2_evaluations) \
 X(dobrushin_absdiff_terms) X(mixing_power_multiplications)
struct Cost {
#define DECLARE(name) U name=0;
 DEC_COUNTERS(DECLARE)
#undef DECLARE
};
Cost difference(const Cost&a,const Cost&b){Cost z;
#define DIFF(name) lab::require(a.name>=b.name,"counter reversal");z.name=a.name-b.name;
 DEC_COUNTERS(DIFF)
#undef DIFF
 return z;}
std::string cost_json(const Cost&c){std::ostringstream o;o<<'{';bool first=true;
#define EMIT(name) if(!first)o<<',';first=false;o<<'"'<<#name<<"\":"<<c.name;
 DEC_COUNTERS(EMIT)
#undef EMIT
 return o.str()+'}';}
U mix(U z){z=(z^(z>>30))*0xbf58476d1ce4e5b9ULL;z=(z^(z>>27))*0x94d049bb133111ebULL;return z^(z>>31);}
U hash(const std::string&s){U h=14695981039346656037ULL;for(char raw:s){h^=static_cast<unsigned char>(raw);h*=1099511628211ULL;}return h;}
struct Random {
 lab::RNG rng;Cost&cost;
 Random(U seed,Cost&c):rng(seed),cost(c){}
 U next(){++cost.rng_draws;return rng.next();}
 U below(U n){lab::require(n!=0,"zero random bound");U threshold=(U{0}-n)%n;for(;;){U x=next();if(x>=threshold)return x%n;}}
};
struct Ops {
 lab::Curve curve;Cost cost;I sqrt_z=0;
 explicit Ops(lab::Curve c):curve(c){}
 I mod(I x)const{return curve.mod(x);}
 I plus(I x,I y){++cost.field_additions;return mod(x+y);}
 I minus(I x,I y){++cost.field_additions;return mod(x-y);}
 I times(I x,I y){++cost.field_multiplications;return mod(mod(x)*mod(y));}
 I power(I x,U e){++cost.field_power_calls;I out=1;x=mod(x);while(e){if(e&1U)out=times(out,x);e>>=1;if(e)x=times(x,x);}return out;}
 I inverse(I x){++cost.field_inversions;lab::require(mod(x)!=0,"inverse zero");return power(x,static_cast<U>(curve.p-2));}
 bool valid(lab::Point p){if(p.inf)return p.x==0&&p.y==0;if(p.x<0||p.x>=curve.p||p.y<0||p.y>=curve.p)return false;return times(p.y,p.y)==plus(plus(times(times(p.x,p.x),p.x),times(curve.a,p.x)),curve.b);}
 lab::Point add(lab::Point x,lab::Point y){
  ++cost.group_additions;lab::require(valid(x)&&valid(y),"noncanonical point in public arithmetic");
  if(x.inf)return y;
  if(y.inf)return x;
  if(x.x==y.x&&plus(x.y,y.y)==0)return {};
  I slope=x==y?times(plus(times(3,times(x.x,x.x)),curve.a),inverse(times(2,x.y))):times(minus(y.y,x.y),inverse(minus(y.x,x.x)));
  I z=minus(minus(times(slope,slope),x.x),y.x);
  lab::Point result{z,minus(times(slope,minus(x.x,z)),x.y),false};
  lab::require(valid(result),"invalid public addition output");return result;
 }
 lab::Point scalar(lab::Point x,U n){++cost.scalar_multiplications;lab::require(valid(x),"invalid public scalar input");lab::Point out{};while(n){if(n&1U)out=add(out,x);n>>=1;if(n)x=add(x,x);}return out;}
 std::optional<I> square_root(I n){
  ++cost.sqrt_calls;n=mod(n);if(n==0)return I{0};
  if(power(n,static_cast<U>((curve.p-1)/2))!=1)return {};
  if(curve.p%4==3){I x=power(n,static_cast<U>((curve.p+1)/4));lab::require(times(x,x)==n,"sqrt fast path");return x;}
  I q=curve.p-1;unsigned s=0;while(q%2==0){q/=2;++s;}
  if(sqrt_z==0){for(I z=2;z<curve.p;++z){++cost.sqrt_nonresidue_tests;if(power(z,static_cast<U>((curve.p-1)/2))==curve.p-1){sqrt_z=z;break;}}}
  lab::require(sqrt_z!=0,"Tonelli nonresidue missing");I c=power(sqrt_z,static_cast<U>(q)),x=power(n,static_cast<U>((q+1)/2)),t=power(n,static_cast<U>(q));unsigned m=s;
  while(t!=1){I y=t;unsigned i=0;for(i=1;i<m;++i){y=times(y,y);if(y==1)break;}lab::require(i<m,"Tonelli invariant failed");I b=power(c,U{1}<<(m-i-1));x=times(x,b);c=times(b,b);t=times(t,c);m=i;}
  lab::require(times(x,x)==n,"Tonelli root mismatch");return x;
 }
};
bool public_prime(I n,Cost&c){if(n<2)return false;for(I d=2;d<=n/d;++d){++c.primality_divisor_tests;if(n%d==0)return false;}return true;}
void validate_fixture(const lab::Fixture&f,Ops&ops){
 const auto&c=f.c;lab::require(c.p>3&&c.p<=65535&&public_prime(c.p,ops.cost),"unsupported/nonprime p");
 lab::require(c.a>0&&c.a<c.p&&c.b>0&&c.b<c.p,"ordinary nonspecial curve parameters required");
 lab::require(f.stratum=="ordinary"||f.stratum=="power5","unsupported fixture stratum");
 if(f.stratum=="power5")lab::require((c.p-1)%5==0,"power5 stratum requires 5 dividing p-1");
 lab::require(c.mod(4*c.a*c.a*c.a+27*c.b*c.b)!=0,"singular curve");
 lab::require(f.r>2&&f.r<=8191&&f.r!=c.p&&public_prime(f.r,ops.cost),"unsupported/nonprime subgroup");
 lab::require(f.N>0&&f.N<=c.p+513&&f.N!=c.p&&f.N%f.r==0&&f.N!=c.p+1,"unsupported/anomalous public order");
 const I trace=c.p+1-f.N;lab::require(trace*trace<=4*c.p,"public order outside Hasse interval");
 lab::require(std::gcd(f.N/f.r,f.r)==1,"cofactor projection not certified surjective");
 lab::require(!f.P.inf&&ops.valid(f.P)&&ops.scalar(f.P,static_cast<U>(f.r)).inf,"prime-order base check failed");
}
// Deliberately light: no read_fixtures(), certify(), points() or orbit() call.
std::vector<lab::Fixture> public_fixtures(const std::string&path){
 std::ifstream in(path);lab::require(bool(in),"cannot open public fixture file");std::vector<lab::Fixture> out;std::set<std::string> ids;std::string line;
 while(std::getline(in,line)){if(line.empty()||line[0]=='#'||line.rfind("id\t",0)==0)continue;lab::Fixture f;std::istringstream row(line);row>>f.id>>f.stratum>>f.c.p>>f.c.a>>f.c.b>>f.P.x>>f.P.y>>f.r>>f.N>>f.seed;lab::require(!row.fail(),"malformed public fixture");std::string extra;lab::require(!(row>>extra),"extra public fixture columns");f.P.inf=false;lab::require(ids.insert(f.id).second,"duplicate fixture");out.push_back(f);}
 lab::require(!out.empty(),"empty public fixture panel");return out;
}
struct Target {std::string fixture,id;lab::Point q;U ordinal=0;};
std::vector<Target> public_targets(const std::string&path){
 std::ifstream in(path);lab::require(bool(in),"cannot open PUBLIC target file");std::string line;std::vector<Target> out;std::set<std::string> ids;std::map<std::string,U> ordinals;
 while(std::getline(in,line)){if(line.empty()||line[0]=='#'||line.rfind("fixture_id",0)==0)continue;Target t;I flag=-1;std::istringstream row(line);row>>t.fixture>>t.id>>t.q.x>>t.q.y>>flag;lab::require(!row.fail()&&(flag==0||flag==1),"malformed public target");std::string extra;lab::require(!(row>>extra),"extra target columns: scalar labels are not accepted");t.q.inf=flag!=0;t.ordinal=ordinals[t.fixture]++;lab::require(ids.insert(t.id).second,"target IDs must be globally unique");out.push_back(t);}
 lab::require(!out.empty(),"empty public target set");return out;
}
lab::Point sample(const lab::Fixture&f,Ops&ops,Random&rng){
 ++ops.cost.subgroup_samples;
 // Under the public certified N, this samples all N curve points uniformly.
 if(rng.below(static_cast<U>(f.N))==0)return {};
 for(;;){++ops.cost.sampler_finite_attempts;I x=static_cast<I>(rng.below(static_cast<U>(f.c.p)));I rhs=ops.plus(ops.plus(ops.times(ops.times(x,x),x),ops.times(f.c.a,x)),f.c.b);auto y=ops.square_root(rhs);
  if(!y){++ops.cost.sampler_rejections;continue;}
  if(*y==0){if(rng.below(2)!=0){++ops.cost.sampler_rejections;continue;}}
  else if(rng.below(2)!=0)*y=f.c.p-*y;
  lab::Point p{x,*y,false};lab::require(ops.valid(p),"sample is off curve");
  // gcd(h,r)=1 and N=h*r give a surjective map with h equal-sized fibres.
  auto result=ops.scalar(p,static_cast<U>(f.N/f.r));lab::require(ops.valid(result),"cofactor sample off curve");return result;
 }
}
enum class Kind {xmod7,power5,xhash7,constant};
struct Feature {
 Kind kind;std::string name;unsigned d;U seed;std::vector<I> fifth_roots;
 Feature(Kind k,const lab::Fixture&f,Ops&ops):kind(k),d(k==Kind::constant?1U:(k==Kind::power5?7U:8U)),seed(f.seed^hash("L9.scale.xhash7.v1")){
  name=k==Kind::xmod7?"x_mod_7":k==Kind::power5?"power_residue_5":k==Kind::xhash7?"x_hash_7":"constant";
  if(k!=Kind::power5)return;
  lab::require((f.c.p-1)%5==0,"power5 unavailable");std::vector<I> factors;I n=f.c.p-1;
  for(I q=2;q<=n/q;++q){++ops.cost.generator_factor_trials;if(n%q==0){factors.push_back(q);while(n%q==0)n/=q;}}
  if(n>1)factors.push_back(n);
  I generator=0;
  for(I g=2;g<f.c.p;++g){bool good=true;for(I q:factors)if(ops.power(g,static_cast<U>((f.c.p-1)/q))==1){good=false;break;}if(good){generator=g;break;}}
  lab::require(generator!=0,"public multiplicative generator missing");I root=ops.power(generator,static_cast<U>((f.c.p-1)/5)),x=1;
  for(unsigned i=0;i<5;++i){fifth_roots.push_back(x);x=ops.times(x,root);}std::sort(fifth_roots.begin(),fifth_roots.end());lab::require(std::adjacent_find(fifth_roots.begin(),fifth_roots.end())==fifth_roots.end(),"nonprimitive fifth root");
 }
 unsigned operator()(lab::Point p,Ops&ops)const{
  ++ops.cost.feature_evaluations;if(kind==Kind::constant)return 0;if(p.inf)return 0;
  if(kind==Kind::xmod7)return 1U+static_cast<unsigned>(p.x%7);
  if(kind==Kind::xhash7)return 1U+static_cast<unsigned>(mix(static_cast<U>(p.x)^seed)%7U);
  if(p.x==0)return 1;
  I value=ops.power(p.x,static_cast<U>((ops.curve.p-1)/5));auto it=std::lower_bound(fifth_roots.begin(),fifth_roots.end(),value);lab::require(it!=fifth_roots.end()&&*it==value,"power residue outside public roots");return 2U+static_cast<unsigned>(it-fifth_roots.begin());
 }
};
struct Model {
 Feature feature;std::array<V,2> k;std::array<std::vector<U>,2> counts,heldout;
 std::vector<U> row_counts;std::array<V,2> marginal;std::array<U,2> accurate{},marginal_accurate{};
 std::array<long double,2> loss{},marginal_loss{},dobrushin{};V mixing_powers;U training_seed=0,calibration_seed=0;Cost construction,calibration;
 explicit Model(Feature f):feature(std::move(f)){}
 unsigned size()const{return feature.d;}
};
long double contraction_delta(const V&k,unsigned d,Cost&cost){
 lab::require(k.size()==static_cast<std::size_t>(d)*d,"contraction matrix size");long double maximum=0;
 for(unsigned a=0;a<d;++a)for(unsigned b=a+1;b<d;++b){long double difference=0;for(unsigned c=0;c<d;++c){difference+=std::abs(k[a*d+c]-k[b*d+c]);++cost.dobrushin_absdiff_terms;}maximum=std::max(maximum,difference/2);}
 return maximum;
}
Model train(const lab::Fixture&f,Kind kind,Ops&ops){
 Cost before=ops.cost;Model m{Feature(kind,f,ops)};const auto d=m.size();
 for(auto&v:m.counts)v.assign(d*d,0);
 for(auto&v:m.heldout)v.assign(d*d,0);
 m.row_counts.assign(d,0);
 m.training_seed=f.seed^hash("decoder.train.v1/"+m.feature.name);Random rng(m.training_seed,ops.cost);
 for(unsigned i=0;i<training_samples;++i){auto x=sample(f,ops,rng);unsigned a=m.feature(x,ops);auto y=ops.add(x,x);auto z=ops.add(y,f.P);std::array<unsigned,2> next{m.feature(y,ops),m.feature(z,ops)};++m.row_counts[a];for(unsigned bit=0;bit<2;++bit)++m.counts[bit][a*d+next[bit]];}
 for(unsigned bit=0;bit<2;++bit){m.k[bit].resize(d*d);m.marginal[bit].resize(d);std::vector<U> columns(d,0);
  for(unsigned a=0;a<d;++a){long double total=0;for(unsigned c=0;c<d;++c){columns[c]+=m.counts[bit][a*d+c];auto probability=static_cast<long double>(m.counts[bit][a*d+c]+1)/static_cast<long double>(m.row_counts[a]+d);m.k[bit][a*d+c]=probability;total+=probability;}lab::require(std::abs(total-1)<1e-12L,"kernel is not stochastic");}
  for(unsigned c=0;c<d;++c)m.marginal[bit][c]=static_cast<long double>(columns[c]+1)/static_cast<long double>(training_samples+d);
  m.dobrushin[bit]=contraction_delta(m.k[bit],d,ops.cost);
 }
 m.mixing_powers.push_back(1);long double delta=std::max(m.dobrushin[0],m.dobrushin[1]);for(unsigned t=1;t<=lab::bits(static_cast<U>(f.r-1));++t){m.mixing_powers.push_back(m.mixing_powers.back()*delta);++ops.cost.mixing_power_multiplications;}
 m.construction=difference(ops.cost,before);before=ops.cost;
 m.calibration_seed=f.seed^hash("decoder.heldout.v1/"+m.feature.name);Random held(m.calibration_seed,ops.cost);
 for(unsigned i=0;i<calibration_samples;++i){auto x=sample(f,ops,held);unsigned a=m.feature(x,ops);auto y=ops.add(x,x),z=ops.add(y,f.P);std::array<unsigned,2> next{m.feature(y,ops),m.feature(z,ops)};
  for(unsigned bit=0;bit<2;++bit){unsigned best=0,base=0;for(unsigned c=1;c<d;++c){if(m.k[bit][a*d+c]>m.k[bit][a*d+best])best=c;if(m.marginal[bit][c]>m.marginal[bit][base])base=c;}
   ++m.heldout[bit][a*d+next[bit]];m.accurate[bit]+=best==next[bit]?1U:0U;m.marginal_accurate[bit]+=base==next[bit]?1U:0U;
   m.loss[bit]-=std::log2(m.k[bit][a*d+next[bit]]);m.marginal_loss[bit]-=std::log2(m.marginal[bit][next[bit]]);ops.cost.calibration_log2_evaluations+=2;
  }
 }
 m.calibration=difference(ops.cost,before);return m;
}
U legal_completions(U prefix,unsigned used,unsigned ell,U r){lab::require(used<=ell,"prefix depth overflow");unsigned remaining=ell-used;U lo=prefix<<remaining;if(lo>=r)return 0;U high=lo+(U{1}<<remaining);return std::min(high,r)-lo;}
struct Backward {
 unsigned ell,d;std::vector<long double> values;
 Backward(unsigned e,unsigned states):ell(e),d(states),values(static_cast<std::size_t>(e+1)*2*states,0){}
 long double&at(unsigned pos,bool less,unsigned a){return values[(static_cast<std::size_t>(pos)*2+static_cast<std::size_t>(less))*d+a];}
 long double at(unsigned pos,bool less,unsigned a)const{return values[(static_cast<std::size_t>(pos)*2+static_cast<std::size_t>(less))*d+a];}
};
Backward backwards(const Model&m,U r,unsigned terminal,Cost&cost){
 unsigned ell=lab::bits(r-1),d=m.size();lab::require(terminal<d,"terminal state out of range");Backward out(ell,d);for(unsigned less=0;less<2;++less)out.at(ell,less!=0,terminal)=1;
 for(unsigned pos=ell;pos!=0;){--pos;unsigned upper=static_cast<unsigned>(((r-1)>>(ell-pos-1))&1U);
  for(unsigned flag=0;flag<2;++flag)for(unsigned a=0;a<d;++a)for(unsigned bit=0;bit<2;++bit){if(flag==0&&bit>upper)continue;bool nextless=flag!=0||bit<upper;for(unsigned c=0;c<d;++c){out.at(pos,flag!=0,a)+=m.k[bit][a*d+c]*out.at(pos+1,nextless,c);++cost.dp_multiply_add_terms;}}
 }
 return out;
}
struct View {lab::Point R,shifted;unsigned start=0,terminal=0;};
struct Views {std::array<View,view_count> data;U seed=0;Cost cost;};
Views make_views(const lab::Fixture&f,const Target&t,const Model&m,Ops&ops){
 Cost before=ops.cost;Views views;views.seed=f.seed^hash("decoder.views.v1/"+m.feature.name)^mix(t.ordinal+0x52a090U);Random rng(views.seed,ops.cost);const unsigned ell=lab::bits(static_cast<U>(f.r-1));
 for(auto&v:views.data){v.R=sample(f,ops,rng);auto shifted=v.R;for(unsigned j=0;j<ell;++j)shifted=ops.add(shifted,shifted);v.shifted=ops.add(t.q,shifted);v.start=m.feature(v.R,ops);v.terminal=m.feature(v.shifted,ops);}
 views.cost=difference(ops.cost,before);return views;
}
struct Node {U prefix=0,tie=0;bool less=false;std::vector<V> alpha;std::vector<lab::Point> points;long double score=0;};
struct ExactContext {std::vector<lab::Point> start_points;std::function<std::pair<lab::Point,unsigned>(lab::Point,unsigned)> advance;};
struct Search {std::vector<U> candidates;std::vector<long double> scores;Cost inference;U maximum_live_nodes=0,backward_payload_bytes=0,beam_alpha_payload_bytes=0,beam_point_payload_bytes=0;};
Search search(const Model&m,U r,const std::vector<std::pair<unsigned,unsigned>>&states,unsigned width,U tie_seed,Cost&cost,const ExactContext*exact=nullptr){
 lab::require(width>0&&!states.empty(),"empty beam/views");Cost before=cost;const unsigned ell=lab::bits(r-1),d=m.size();std::vector<Backward> beta;
 for(auto [start,terminal]:states){lab::require(start<d,"start state out of range");beta.push_back(backwards(m,r,terminal,cost));}
 Node first;if(exact){lab::require(exact->start_points.size()==states.size()&&bool(exact->advance),"invalid exact-prefix context");first.points=exact->start_points;}else for(auto [start,terminal]:states){(void)terminal;V v(d,0);v[start]=1;first.alpha.push_back(std::move(v));}
 std::vector<Node> beam{std::move(first)};Search result;
 for(unsigned used=0;used<ell;++used){std::vector<Node> children;const unsigned upper=static_cast<unsigned>(((r-1)>>(ell-used-1))&1U);
  for(const auto&parent:beam)for(unsigned bit=0;bit<2;++bit){if(!parent.less&&bit>upper)continue;Node child;child.prefix=2*parent.prefix+bit;child.less=parent.less||bit<upper;U count=legal_completions(child.prefix,used+1,ell,r);lab::require(count>0,"range DP admitted empty prefix");++cost.beam_children;
   child.score=-(static_cast<long double>(states.size())-1)*std::log(static_cast<long double>(count));
   for(std::size_t view=0;view<states.size();++view){long double likelihood=0;
    if(exact){auto [point,label]=exact->advance(parent.points[view],bit);lab::require(label<d,"exact prefix label out of range");child.points.push_back(point);likelihood=beta[view].at(used+1,child.less,label);}
    else{V next(d,0);for(unsigned a=0;a<d;++a)if(parent.alpha[view][a]!=0)for(unsigned c=0;c<d;++c){next[c]+=parent.alpha[view][a]*m.k[bit][a*d+c];++cost.dp_multiply_add_terms;}
     for(unsigned c=0;c<d;++c){likelihood+=next[c]*beta[view].at(used+1,child.less,c);++cost.dp_multiply_add_terms;}child.alpha.push_back(std::move(next));}
    child.score+=likelihood>0?std::log(likelihood):-std::numeric_limits<long double>::infinity();
   }
   child.tie=mix(tie_seed^mix(child.prefix+0x510ed3U)^mix(used+1));children.push_back(std::move(child));
  }
  result.maximum_live_nodes=std::max(result.maximum_live_nodes,static_cast<U>(children.size()+beam.size()));
  std::sort(children.begin(),children.end(),[](const Node&a,const Node&b){if(a.score!=b.score)return a.score>b.score;if(a.tie!=b.tie)return a.tie<b.tie;return a.prefix<b.prefix;});if(children.size()>width)children.resize(width);beam=std::move(children);
 }
 for(const auto&n:beam){result.candidates.push_back(n.prefix);result.scores.push_back(n.score);}
 result.backward_payload_bytes=static_cast<U>(states.size())*(ell+1U)*2U*d*sizeof(long double);if(exact)result.beam_point_payload_bytes=result.maximum_live_nodes*static_cast<U>(states.size())*sizeof(lab::Point);else result.beam_alpha_payload_bytes=result.maximum_live_nodes*static_cast<U>(states.size())*d*sizeof(long double);result.inference=difference(cost,before);return result;
}
template<class T>std::string array_json(const std::vector<T>&v){std::ostringstream o;o<<std::setprecision(18)<<'[';for(std::size_t i=0;i<v.size();++i){if(i)o<<',';o<<v[i];}return o.str()+']';}
std::string point_json(lab::Point p){std::ostringstream o;o<<"{\"x\":"<<p.x<<",\"y\":"<<p.y<<",\"inf\":"<<(p.inf?"true":"false")<<'}';return o.str();}
std::string probability_json(const V&v){for(auto x:v)lab::require(std::isfinite(x)&&x>=0,"invalid probability");return array_json(v);}
void emit_kernel(std::ostream&out,const lab::Fixture&f,const Model&m,const Cost&validation,unsigned targets){
 const auto d=m.size();out<<std::setprecision(18)<<"{\"track\":\"L9-decoder\",\"row_kind\":\"kernel\",\"fixture\":"<<lab::json_quote(f.id)<<",\"stratum\":"<<lab::json_quote(f.stratum)<<",\"scope\":\""<<scope<<"\",\"outcome\":\"complete_valid\",\"feature\":"<<lab::json_quote(m.feature.name)<<",\"p\":"<<f.c.p<<",\"r\":"<<f.r<<",\"states\":"<<d<<",\"training_samples\":"<<training_samples<<",\"heldout_samples\":"<<calibration_samples<<",\"heldout_calibration_samples\":"<<calibration_samples<<",\"training_seed\":"<<lab::json_quote(std::to_string(m.training_seed))<<",\"heldout_seed\":"<<lab::json_quote(std::to_string(m.calibration_seed))<<",\"public_feature_hash_seed\":"<<lab::json_quote(std::to_string(m.feature.seed))<<",\"fifth_power_roots_in_label_order\":"<<array_json(m.feature.fifth_roots)<<",\"laplace_pseudocount\":1,\"training_row_counts\":"<<array_json(m.row_counts)<<",\"training_transition_counts_0\":"<<array_json(m.counts[0])<<",\"training_transition_counts_1\":"<<array_json(m.counts[1])<<",\"kernel_0\":"<<probability_json(m.k[0])<<",\"kernel_1\":"<<probability_json(m.k[1])<<",\"heldout_transition_counts_0\":"<<array_json(m.heldout[0])<<",\"heldout_transition_counts_1\":"<<array_json(m.heldout[1])<<",\"calibration_used_for_tuning\":false,\"calibration\":[";
 for(unsigned bit=0;bit<2;++bit){if(bit)out<<',';out<<"{\"bit\":"<<bit<<",\"samples\":"<<calibration_samples<<",\"conditional_top1_hits\":"<<m.accurate[bit]<<",\"marginal_top1_hits\":"<<m.marginal_accurate[bit]<<",\"conditional_logloss_sum_bits\":"<<m.loss[bit]<<",\"marginal_logloss_sum_bits\":"<<m.marginal_loss[bit]<<",\"conditional_logloss_mean_bits\":"<<m.loss[bit]/calibration_samples<<",\"marginal_logloss_mean_bits\":"<<m.marginal_loss[bit]/calibration_samples<<'}';}
 out<<"],\"dobrushin_delta_0\":"<<m.dobrushin[0]<<",\"dobrushin_delta_1\":"<<m.dobrushin[1]<<",\"dobrushin_delta_max\":"<<std::max(m.dobrushin[0],m.dobrushin[1])<<",\"delta_max_power_by_suffix_length\":"<<array_json(m.mixing_powers)<<",\"contraction_scope\":\"Floating diagnostic only. In the exact trained Markov model, identical t-bit suffixes contract one-view endpoint absolute probability differences by delta_max^t and a product of four likelihoods by at most4delta_max^t; not a posterior, true-EC-dynamics or security bound.\",\"construction_counters\":"<<cost_json(m.construction)<<",\"heldout_calibration_counters\":"<<cost_json(m.calibration)<<",\"construction_counter_scope\":\"Incremental feature setup and training; public Tonelli nonresidue cache may be reused from earlier features. Sum all fixture kernels for total setup.\",\"fixture_validation_counters_shared\":"<<cost_json(validation)<<",\"fixture_targets_validated\":"<<targets<<",\"shared_validation_is_not_additive_across_features\":true,\"kernel_numeric_payload_bytes\":"<<2U*d*d*(sizeof(U)+sizeof(long double))+d*sizeof(U)<<",\"payload_size_scope\":\"Trained probabilities, raw training counts and row masses only; excludes calibration, marginals, objects, allocator overhead and temporary matrices.\",\"public_sampler\":\"balanced finite roots plus identity1/N then cofactor projection; Tonelli-Shanks; no scalar labels\",\"public_order_certificate_trusted\":true,\"full_ec_census_used\":false,\"scalar_orbit_dictionary_used\":false,\"model_assumption\":\"Uniform rerandomized one-time marginals do not imply an exact hidden-state Markov law or independent views\",\"attack_advantage_claimed\":false}\n";
}
void emit_target(std::ostream&out,const lab::Fixture&f,const Target&t,const Model&m,const Views&views,unsigned width,bool exact_mode,Ops&ops){
 Cost before=ops.cost;std::vector<std::pair<unsigned,unsigned>> states;ExactContext exact;for(const auto&v:views.data){states.emplace_back(v.start,v.terminal);exact.start_points.push_back(v.R);}exact.advance=[&](lab::Point p,unsigned bit){auto q=ops.add(p,p);if(bit!=0)q=ops.add(q,f.P);return std::make_pair(q,m.feature(q,ops));};U tie_seed=f.seed^hash("decoder.tie.v1/"+m.feature.name)^mix(t.ordinal+0x1ca459U);auto result=search(m,static_cast<U>(f.r),states,width,tie_seed,ops.cost,exact_mode?&exact:nullptr);
 std::optional<U> verified;unsigned hits=0;for(U k:result.candidates){++ops.cost.candidate_verifications;if(ops.scalar(f.P,k)==t.q){verified=k;++hits;}}lab::require(hits<=1,"distinct canonical scalar candidates both verify");
 auto counters=difference(ops.cost,before);out<<std::setprecision(18)<<"{\"track\":\"L9-decoder\",\"row_kind\":\"target\",\"fixture\":"<<lab::json_quote(f.id)<<",\"scope\":\""<<scope<<"\",\"outcome\":\"complete_valid\",\"feature\":"<<lab::json_quote(m.feature.name)<<",\"prefix_mode\":"<<lab::json_quote(exact_mode?"exact":"model")<<",\"target_id\":"<<lab::json_quote(t.id)<<",\"target_ordinal\":"<<t.ordinal<<",\"p\":"<<f.c.p<<",\"r\":"<<f.r<<",\"beam_width\":"<<width<<",\"views_count\":"<<view_count<<",\"candidate_count\":"<<result.candidates.size()<<",\"candidates\":"<<array_json(result.candidates)<<",\"candidate_scores\":[";
 for(std::size_t i=0;i<result.scores.size();++i){if(i)out<<',';if(std::isfinite(result.scores[i]))out<<result.scores[i];else out<<"null";}
 out<<"],\"verified_scalar\":";if(verified)out<<*verified;else out<<"null";out<<",\"candidate_verification_hits\":"<<hits<<",\"toy_discrete_log_witness\":"<<(verified?"true":"false")<<",\"chance_reference_hits_per_target\":"<<static_cast<long double>(result.candidates.size())/f.r<<",\"chance_reference_scope\":\"exact for scalar-independent candidate sets such as constant projection; descriptive B/r comparator for learned coordinate model\",\"tie_seed\":"<<lab::json_quote(std::to_string(tie_seed))<<",\"view_seed\":"<<lab::json_quote(std::to_string(views.seed))<<",\"views\":[";
 for(std::size_t i=0;i<views.data.size();++i){if(i)out<<',';const auto&v=views.data[i];out<<"{\"R\":"<<point_json(v.R)<<",\"shifted_target\":"<<point_json(v.shifted)<<",\"start_state\":"<<v.start<<",\"terminal_state\":"<<v.terminal<<'}';}
 out<<"],\"shared_view_counters\":"<<cost_json(views.cost)<<",\"views_reused_between_beam_widths\":true,\"views_reused_between_prefix_modes\":true,\"inference_and_verification_counters\":"<<cost_json(counters)<<",\"maximum_live_nodes\":"<<result.maximum_live_nodes<<",\"backward_payload_bytes\":"<<result.backward_payload_bytes<<",\"beam_alpha_payload_bytes\":"<<result.beam_alpha_payload_bytes<<",\"beam_point_payload_bytes\":"<<result.beam_point_payload_bytes<<",\"score_definition\":\"sum_view ln(prefix likelihood) minus (views-1) ln(legal completions); model uses alpha dot beta, exact uses beta at public exact-prefix point label; suffix model and view independence remain approximate\",\"cold_cost_note\":\"Complete batch adds shared validation once, all incremental feature setup, shared views once per case and each inference/verification. Calibration is charged study work. No individual-feature cold bound is claimed because public sampler setup can be reused.\",\"source_separation\":\"Only public E,P,r,N,Q,feature and ordinal seeds reach decoder; no truth file is opened; not OS-enforced blindness\",\"attack_advantage_claimed\":false,\"solver_gain_claimed\":false}\n";
}

U checks=0;
void check(bool test,const std::string&s){++checks;lab::require(test,s);}
template<class F>void rejects(F fn,const std::string&s){bool threw=false;try{fn();}catch(const std::exception&){threw=true;}check(threw,s);}
Model synthetic_model(unsigned d,bool constant){
 lab::Fixture f{"unit","ordinary",{17,2,2},{5,1,false},19,19,1};Ops ops(f.c);Model m{Feature(Kind::constant,f,ops)};m.feature.d=d;
 for(unsigned bit=0;bit<2;++bit){m.k[bit].assign(d*d,0);for(unsigned a=0;a<d;++a)m.k[bit][a*d+(constant?0U:(2*a+bit)%d)]=1;}
 return m;
}
void self_test(){
 // Independent direct finite-field root checking is confined to development.
 for(I p:{17,23,37,61,127}){Ops ops({p,1,1});for(I n=0;n<p;++n){auto root=ops.square_root(n);bool exists=false;for(I x=0;x<p;++x)if(x*x%p==n)exists=true;check(bool(root)==exists,"Tonelli square/non-square classification");if(root)check((*root)*(*root)%p==n,"Tonelli root");}}
 for(lab::Curve curve:std::vector<lab::Curve>{{17,2,2},{23,1,1}}){Ops arithmetic(curve);std::vector<lab::Point> points{{}};for(I x=0;x<curve.p;++x)for(I y=0;y<curve.p;++y)if(curve.valid({x,y,false}))points.push_back({x,y,false});for(auto x:points)for(auto y:points)check(arithmetic.add(x,y)==curve.add(x,y),"public arithmetic full-pair affine cross-check");for(auto x:points)for(U k=0;k<12;++k)check(arithmetic.scalar(x,k)==curve.mul(x,k),"public scalar arithmetic cross-check");}
 lab::Fixture f{"unit","ordinary",{17,2,2},{5,1,false},19,19,0x2915U};Ops ops(f.c);validate_fixture(f,ops);Random rng(0x9132U,ops.cost);
 for(unsigned i=0;i<256;++i){auto q=sample(f,ops,rng);check(f.c.valid(q)&&f.c.mul(q,static_cast<U>(f.r)).inf,"unlabelled sampler subgroup membership");}
 auto constant=synthetic_model(1,true);
 for(U r:{3U,5U,17U,19U,31U}){unsigned ell=lab::bits(r-1);Cost counter;auto b=backwards(constant,r,0,counter);check(b.at(0,false,0)==r,"constant root prior count");
  for(unsigned depth=0;depth<=ell;++depth)for(U prefix=0;prefix<(U{1}<<depth);++prefix){U actual=0;for(U k=0;k<r;++k)if((k>>(ell-depth))==prefix)++actual;check(legal_completions(prefix,depth,ell,r)==actual,"canonical prefix completion count");}
  for(unsigned width:{1U,8U}){auto s=search(constant,r,{{0,0},{0,0},{0,0},{0,0}},width,0x31U,counter);check(s.candidates.size()==std::min<U>(width,r),"constant beam cardinality");std::set<U> unique(s.candidates.begin(),s.candidates.end());check(unique.size()==s.candidates.size(),"constant candidates unique");for(U k:s.candidates)check(k<r,"constant canonical range");}
 }
 auto full=synthetic_model(17,false);
 {Cost c;check(contraction_delta(full.k[0],17,c)==1&&contraction_delta(full.k[1],17,c)==1,"permutation contraction calibration");check(contraction_delta(constant.k[0],1,c)==0,"constant contraction calibration");V equal_rows{.2L,.8L,.2L,.8L};check(contraction_delta(equal_rows,2,c)==0,"identical-row contraction calibration");}
 for(U k=0;k<17;++k)for(unsigned width:{1U,8U}){unsigned ell=lab::bits(16);unsigned R=3;unsigned terminal=static_cast<unsigned>(((U{1}<<ell)*R+k)%17);Cost counter;auto s=search(full,17,{{R,terminal}},width,0x2dU,counter);check(!s.candidates.empty()&&s.candidates.front()==k,"full-state deterministic positive decoder");auto b=backwards(full,17,terminal,counter);check(b.at(0,false,R)==1,"unique deterministic target completion");ExactContext exact;exact.start_points={{static_cast<I>(R),0,false}};exact.advance=[](lab::Point p,unsigned bit){unsigned next=static_cast<unsigned>((2*p.x+bit)%17);return std::make_pair(lab::Point{static_cast<I>(next),0,false},next);};auto e=search(full,17,{{R,terminal}},width,0x2dU,counter,&exact);check(e.candidates.front()==k,"full-state exact-prefix positive decoder");}
 // Matrix DP is checked against direct branch recursion for a non-deterministic model.
 auto soft=synthetic_model(2,true);soft.k[0]={.7L,.3L,.2L,.8L};soft.k[1]={.4L,.6L,.9L,.1L};
 for(U r:{3U,5U,7U,13U})for(unsigned terminal=0;terminal<2;++terminal){Cost counter;auto b=backwards(soft,r,terminal,counter);for(unsigned start=0;start<2;++start){long double exact=0;unsigned ell=lab::bits(r-1);for(U k=0;k<r;++k){V alpha(2,0);alpha[start]=1;for(unsigned j=ell;j!=0;--j){unsigned bit=static_cast<unsigned>((k>>(j-1))&1U);V next(2,0);for(unsigned a=0;a<2;++a)for(unsigned c=0;c<2;++c)next[c]+=alpha[a]*soft.k[bit][a*2+c];alpha=next;}exact+=alpha[terminal];}check(std::abs(b.at(0,false,start)-exact)<1e-12L,"soft backward DP vs exhaustive branches");}}
 rejects([&]{Cost c;(void)backwards(soft,7,2,c);},"invalid terminal rejected");rejects([&]{(void)legal_completions(0,3,2,5);},"invalid prefix rejected");
 auto trained=train(f,Kind::xmod7,ops);check(std::accumulate(trained.row_counts.begin(),trained.row_counts.end(),U{0})==training_samples,"training sample count");
 for(unsigned bit=0;bit<2;++bit){check(std::accumulate(trained.heldout[bit].begin(),trained.heldout[bit].end(),U{0})==calibration_samples,"heldout sample count");check(std::isfinite(trained.loss[bit])&&std::isfinite(trained.marginal_loss[bit]),"finite heldout loss");}
 lab::Fixture f5{"unit-power5","power5",{61,1,4},{41,55,false},19,57,0x2105U};Ops ops5(f5.c);validate_fixture(f5,ops5);auto fifth=train(f5,Kind::power5,ops5);check(fifth.feature.fifth_roots.size()==5,"public fifth-root alphabet");for(U k=0;k<static_cast<U>(f5.r);++k){auto q=f5.c.mul(f5.P,k);unsigned label=fifth.feature(q,ops5);if(q.inf)check(label==0,"fifth identity label");else if(q.x==0)check(label==1,"fifth zero label");else check(label>=2&&label<7&&fifth.feature.fifth_roots[label-2]==f5.c.pow(q.x,(f5.c.p-1)/5),"fifth coordinate label cross-check");}
 Target target{"unit","unit-target",f.c.mul(f.P,7),0};auto views=make_views(f,target,trained,ops);for(const auto&v:views.data){auto expected=v.R;for(unsigned j=0;j<lab::bits(static_cast<U>(f.r-1));++j)expected=f.c.add(expected,expected);expected=f.c.add(expected,target.q);check(expected==v.shifted,"public rerandomization identity");}
 auto pure=train(f,Kind::constant,ops);Target t1=target,t2=target;t2.q=f.c.mul(f.P,12);auto v1=make_views(f,t1,pure,ops),v2=make_views(f,t2,pure,ops);Cost c1,c2;std::vector<std::pair<unsigned,unsigned>> st1,st2;for(auto v:v1.data)st1.emplace_back(v.start,v.terminal);for(auto v:v2.data)st2.emplace_back(v.start,v.terminal);auto a=search(pure,19,st1,8,0x11U,c1),b=search(pure,19,st2,8,0x11U,c2);check(a.candidates==b.candidates,"constant candidate set independent of public target");
 ExactContext exact_constant;for(auto v:v1.data)exact_constant.start_points.push_back(v.R);exact_constant.advance=[&](lab::Point p,unsigned bit){auto q=ops.add(p,p);if(bit)q=ops.add(q,f.P);return std::make_pair(q,pure.feature(q,ops));};auto same=search(pure,19,st1,8,0x11U,ops.cost,&exact_constant);check(a.candidates==same.candidates,"constant model/exact-prefix candidates identical");
 rejects([&]{lab::Fixture wrong=f;wrong.N=38;Ops o(wrong.c);validate_fixture(wrong,o);},"invalid public order sanity check");
 rejects([&]{lab::Fixture wrong=f;wrong.N=std::numeric_limits<I>::max();Ops o(wrong.c);validate_fixture(wrong,o);},"oversized order rejected before Hasse squaring");
 std::cout<<"{\"self_test\":\"pass\",\"checks\":"<<checks<<",\"scope\":\"development_only\",\"scientific_run\":false}\n";
}
int run(const std::string&fixture_path,const std::string&target_path,const std::string&output){
 lab::require(!std::filesystem::exists(output),"refusing output overwrite");auto fixtures=public_fixtures(fixture_path);auto targets=public_targets(target_path);std::map<std::string,std::vector<Target>> grouped;std::set<std::string> known;
 for(const auto&f:fixtures)known.insert(f.id);
 for(const auto&t:targets){lab::require(known.contains(t.fixture),"unknown target fixture");grouped[t.fixture].push_back(t);}
 std::ofstream out(output);lab::require(bool(out),"cannot create output");U rows=0;
 for(const auto&f:fixtures){Ops ops(f.c);validate_fixture(f,ops);auto it=grouped.find(f.id);lab::require(it!=grouped.end()&&!it->second.empty(),"fixture without public targets");for(const auto&t:it->second)lab::require(ops.valid(t.q)&&ops.scalar(t.q,static_cast<U>(f.r)).inf,"invalid/off-subgroup public target");const Cost shared_validation=ops.cost;
  for(Kind kind:{Kind::xmod7,Kind::power5,Kind::xhash7,Kind::constant}){if(kind==Kind::power5&&(f.c.p-1)%5!=0){out<<"{\"track\":\"L9-decoder\",\"row_kind\":\"not_applicable\",\"fixture\":"<<lab::json_quote(f.id)<<",\"feature\":\"power_residue_5\",\"scope\":\""<<scope<<"\",\"outcome\":\"not_applicable\",\"reason\":\"5 does not divide p-1\"}\n";++rows;continue;}
   auto model=train(f,kind,ops);emit_kernel(out,f,model,shared_validation,static_cast<unsigned>(it->second.size()));++rows;
   for(const auto&t:it->second){auto views=make_views(f,t,model,ops);for(bool exact:{false,true})for(unsigned width:{1U,8U}){emit_target(out,f,t,model,views,width,exact,ops);++rows;}}
  }
 }
 lab::require(bool(out),"output write failure");std::cout<<"{\"status\":\"complete\",\"scope\":\""<<scope<<"\",\"fixtures\":"<<fixtures.size()<<",\"public_targets\":"<<targets.size()<<",\"rows\":"<<rows<<",\"truth_labels_read\":false,\"attack_advantage_claimed\":false}\n";return 0;
}
}
int main(int argc,char**argv){try{if(argc==2&&std::string(argv[1])=="--self-test"){dec::self_test();return 0;}if(argc==5&&std::string(argv[1])=="--run")return dec::run(argv[2],argv[3],argv[4]);std::cerr<<"usage: decoder --self-test | --run FIXTURES_TSV PUBLIC_TARGETS_TSV FRESH_OUTPUT_JSONL\n";return 2;}catch(const std::exception&e){std::cerr<<"decoder refused: "<<e.what()<<'\n';return 1;}}
