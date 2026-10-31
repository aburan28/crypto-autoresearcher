// Source-bound classical baselines and a candidate-prefix/rho composition.
// Upstream rho/precomp algorithms are unchanged; all EC operations use dec::Ops.
#pragma once
#include "arithmetic/legacy/decoder.hpp"
#include "candidate/endpoint_reuse.h"
#include <cryptanalysis/ca_rho.h>
#include <cryptanalysis/ca_precomp.h>
#include <chrono>
#include <ctime>
#include <memory>
#include <type_traits>
#include <sys/resource.h>
#include <time.h>

namespace endpoint {
using dec::U;using lab::I;using lab::Point;
constexpr const char* scope="classical_ecdlp_endpoint_reuse";
constexpr const char* track="solver-baselines";
constexpr const char* upstream="379faa0f1e38facd9c8fdfc527f0b89518cf2e70";
struct Aux {U hash_calls=0,equality_calls=0,negation_calls=0,canonicalization_calls=0,batch_calls=0;};
struct Adapter {ca_group g{};dec::Ops* ops;Aux aux;bool force_hash=false;U forced_hash=0;
 explicit Adapter(const lab::Fixture&f,dec::Ops&o);
};
static_assert(std::is_standard_layout_v<Adapter> && offsetof(Adapter,g)==0);
Adapter& adapter(const ca_group*g){return *const_cast<Adapter*>(reinterpret_cast<const Adapter*>(g));}
Point point(const ca_elem&e){lab::require(e.w[2]<=1&&e.w[3]==0,"noncanonical adapter element");return {static_cast<I>(e.w[0]),static_cast<I>(e.w[1]),e.w[2]!=0};}
ca_elem element(Point p){return {{static_cast<U>(p.x),static_cast<U>(p.y),p.inf?1U:0U,0}};}
void op(const ca_group*g,ca_elem*r,const ca_elem*a,const ca_elem*b){*r=element(adapter(g).ops->add(point(*a),point(*b)));}
void dbl(const ca_group*g,ca_elem*r,const ca_elem*a){op(g,r,a,a);}
void inv(const ca_group*g,ca_elem*r,const ca_elem*a){auto&p=adapter(g);++p.aux.negation_calls;auto q=point(*a);if(!q.inf)q.y=p.ops->minus(0,q.y);*r=element(q);}
void identity(const ca_group*,ca_elem*r){*r=element({});}
int is_identity(const ca_group*,const ca_elem*a){return point(*a).inf?1:0;}
int equal(const ca_group*g,const ca_elem*a,const ca_elem*b){++adapter(g).aux.equality_calls;return point(*a)==point(*b)?1:0;}
U hash_point(const ca_group*g,const ca_elem*a){++adapter(g).aux.hash_calls;if(adapter(g).force_hash)return adapter(g).forced_hash;const auto q=point(*a);return q.inf?dec::mix(0x6f726465722d6964ULL):dec::mix(static_cast<U>(q.x)^std::rotl(static_cast<U>(q.y),32)^0x706f696e742d7631ULL);}
void batch(const ca_group*g,ca_elem*r,const ca_elem*a,const ca_elem*b,std::size_t n,U*){++adapter(g).aux.batch_calls;for(std::size_t i=0;i<n;++i)op(g,r+i,a+i,b+i);}
int encode(const ca_group*g,ca_elem*r,const U*w){ca_elem q{{w[0],w[1],w[2],w[3]}};if(w[2]>1||w[3]!=0)return 0;if(!adapter(g).ops->valid(point(q)))return 0;*r=q;return 1;}
void decode(const ca_group*,U*w,const ca_elem*a){std::copy(std::begin(a->w),std::end(a->w),w);}
int valid(const ca_group*g,const ca_elem*a){return adapter(g).ops->valid(point(*a))?1:0;}
int canonical(const ca_group*g,ca_elem*a){auto&z=adapter(g);++z.aux.canonicalization_calls;auto q=point(*a);if(q.inf||q.y<=z.ops->curve.p-q.y)return 0;++z.aux.negation_calls;q.y=z.ops->minus(0,q.y);*a=element(q);return 1;}
const ca_group_vtable vt{op,dbl,inv,identity,is_identity,equal,hash_point,batch,encode,decode,valid,canonical};
Adapter::Adapter(const lab::Fixture&f,dec::Ops&o):ops(&o){g.vt=&vt;g.kind=CA_GROUP_EC;g.order=static_cast<U>(f.r);g.p=static_cast<U>(f.c.p);g.a=static_cast<U>(f.c.a);g.b=static_cast<U>(f.c.b);g.cofactor=static_cast<U>(f.N/f.r);}
std::string aux_json(const Aux&a){std::ostringstream o;o<<"{\"hash_calls\":"<<a.hash_calls<<",\"equality_calls\":"<<a.equality_calls<<",\"negation_calls\":"<<a.negation_calls<<",\"canonicalization_calls\":"<<a.canonicalization_calls<<",\"batch_calls\":"<<a.batch_calls<<'}';return o.str();}
std::string stats_json(const ca_stats&s){std::ostringstream o;o<<std::setprecision(18)<<"{\"reported_group_ops\":"<<s.group_ops<<",\"iterations\":"<<s.iterations<<",\"table_entries\":"<<s.table_entries<<",\"collisions\":"<<s.collisions<<",\"table_bytes_peak_estimate\":"<<s.bytes_peak<<",\"upstream_wall_seconds\":"<<s.seconds<<",\"threads\":"<<s.threads<<'}';return o.str();}
U ceil_sqrt(U r){U m=static_cast<U>(std::sqrt(static_cast<long double>(r)));while(m*m<r)++m;while(m>1&&(m-1)*(m-1)>=r)--m;return m;}
U nonzero_seed(U s){return s?s:1;}
U rho_seed(const lab::Fixture&f,const dec::Target&t){return nonzero_seed(f.seed^dec::hash("validation.rho.paired.v1")^dec::mix(t.ordinal+0x4125U));}
U rho_limit(const lab::Fixture&f){return 256U*ceil_sqrt(static_cast<U>(f.r))+8192U;}
U rho_effective_r(const lab::Fixture&f){const U root=static_cast<U>(std::sqrt(static_cast<long double>(f.r)))+1;const U budget=root/(48U*lab::bits(static_cast<U>(f.r)));U r=8;while(r*2<=budget&&r*2<=1024)r*=2;return r;}
U rho_effective_walks(const lab::Fixture&f){const U root=static_cast<U>(std::sqrt(static_cast<long double>(f.r)))+1;return std::max(U{1},std::min(U{256},root/(24U*lab::bits(static_cast<U>(f.r)))));}
int rho_effective_dp(const lab::Fixture&f){const long double expected=1.25L*static_cast<long double>(static_cast<U>(std::sqrt(static_cast<long double>(f.r)))+1)/1.4142L;const long double per=expected/(32.0L*static_cast<long double>(rho_effective_walks(f)));return per>=2?static_cast<int>(std::floor(std::log2(per))):0;}
struct Result {std::optional<U> scalar;ca_status status=CA_OK;ca_stats stats{};dec::Cost counters;Aux aux;long double cpu=0,wall=0;};
Result rho(const lab::Fixture&f,const dec::Target&t,dec::Ops&ops,U seed){const auto before=ops.cost;Adapter a(f,ops);ca_rho_params p;ca_rho_params_default(&p);p.threads=1;p.negation_map=1;p.seed=nonzero_seed(seed);p.max_ops=rho_limit(f);U scalar=0;Result z;const auto base=element(f.P),target=element(t.q);z.status=ca_rho_solve(&a.g,&base,&target,&p,&scalar,&z.stats);if(z.status==CA_OK){++ops.cost.candidate_verifications;lab::require(scalar<static_cast<U>(f.r)&&ops.scalar(f.P,scalar)==t.q,"rho returned wrong scalar");z.scalar=scalar;}z.counters=dec::difference(ops.cost,before);z.aux=a.aux;return z;}

} // namespace endpoint
