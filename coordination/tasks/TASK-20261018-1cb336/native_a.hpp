// Route A. No scientific arithmetic is imported from route B.
#include <algorithm>
#include <array>
#include <cstdint>
#include <iostream>
#include <map>
#include <numeric>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>
#include <tuple>
namespace first {
using I=long long;
using O=std::map<std::string,std::string>;
std::string q(const std::string&s){return "\""+s+"\"";}
std::string n(I a){return std::to_string(a);}
std::string b(bool a){return a?"true":"false";}
std::string arr(const std::vector<std::string>&a){std::string s="[";for(auto&x:a){if(s.size()>1)s+=",";s+=x;}return s+"]";}
std::string nums(const std::vector<I>&a){std::vector<std::string>v;for(auto x:a)v.push_back(n(x));return arr(v);}
std::string obj(const O&a){std::string s="{";for(auto&[k,v]:a){if(s.size()>1)s+=",";s+=q(k)+":"+v;}return s+"}";}
I mod(I a,I p){a%=p;return a<0?a+p:a;}
I powmod(I a,I e,I p){I r=1;while(e){if(e&1)r=r*a%p;a=a*a%p;e/=2;}return r;}
I ipow(I a,int e){I r=1;while(e--)r*=a;return r;}
struct R{I p,d;R(I a=0,I z=1):p(a),d(z){if(d<0)p=-p,d=-d;auto g=std::gcd(p,d);p/=g;d/=g;}std::string s()const{return q(n(p)+"/"+n(d));}};
R operator+(R a,R b){return {a.p*b.d+b.p*a.d,a.d*b.d};}
R operator-(R a,R b){return {a.p*b.d-b.p*a.d,a.d*b.d};}
R operator*(R a,R b){return {a.p*b.p,a.d*b.d};}
R operator/(R a,R b){return {a.p*b.d,a.d*b.p};}
bool operator<(R a,R b){return a.p*b.d<b.p*a.d;}
struct P{I x=0,y=0;bool inf=true;P()=default;P(I a,I z):x(a),y(z),inf(false){};bool operator==(const P&t)const{return inf==t.inf&&(inf||(x==t.x&&y==t.y));}bool operator<(const P&t)const{return std::tie(inf,x,y)<std::tie(t.inf,t.x,t.y);}std::string s()const{return inf?"null":nums({x,y});}};
struct E{
 I p,a2,a4,a6;
 bool on(P a)const{return a.inf||mod(a.y*a.y-a.x*a.x*a.x-a2*a.x*a.x-a4*a.x-a6,p)==0;}
 P neg(P a)const{return a.inf?a:P(a.x,mod(-a.y,p));}
 P add(P a,P z)const{if(a.inf)return z;if(z.inf)return a;if(a.x==z.x&&mod(a.y+z.y,p)==0)return {};I den,num;if(a==z){num=3*a.x*a.x+2*a2*a.x+a4;den=2*a.y;}else{num=z.y-a.y;den=z.x-a.x;}I l=mod(num*powmod(mod(den,p),p-2,p),p),x=mod(l*l-a2-a.x-z.x,p);return {x,mod(l*(a.x-x)-a.y,p)};}
 P mul(I k,P a)const{P r;while(k){if(k&1)r=add(r,a);a=add(a,a);k/=2;}return r;}
 std::vector<P> points()const{std::vector<P>v{{}};for(I x=0;x<p;x++)for(I y=0;y<p;y++)if(on(P(x,y)))v.emplace_back(x,y);return v;}
};
std::string ps(const std::vector<P>&v){std::vector<std::string>a;for(auto p:v)a.push_back(p.s());return arr(a);}
// Unsigned base-2^32 integer, only multiplication by a small input is needed.
struct Big{std::vector<uint32_t>w{1};void times(uint32_t x){uint64_t c=0;for(auto&t:w){c+=uint64_t(t)*x;t=uint32_t(c);c>>=32;}if(c)w.push_back(uint32_t(c));}bool operator<(const Big&z)const{if(w.size()!=z.w.size())return w.size()<z.w.size();for(size_t i=w.size();i-->0;)if(w[i]!=z.w[i])return w[i]<z.w[i];return false;}};
Big power(unsigned a,int k){Big r;while(k--)r.times(a);return r;}
O low(){O out;for(int N:{17,4}){std::vector<std::set<I>>images(16);I misses=0,pairs=0;for(I a=0;a<N;a++)for(I z=0;z<N;z++){images[(a%4)*4+z%4].insert(((a+z)%N)%4);misses+=(((a+z)%N)%4)!=((a%4+z%4)%4);pairs++;}std::vector<I>sizes;std::vector<std::string>sets;for(auto&s:images){sizes.push_back(s.size());sets.push_back(nums(std::vector<I>(s.begin(),s.end())));}auto pre="mod"+n(N)+"_";out[pre+"image_sizes"]=nums(sizes);out[pre+"images"]=arr(sets);out[pre+"mismatches"]=n(misses);out[pre+"pairs"]=n(pairs);}out["residue_pairs"]="16";return out;}
O translation(){E e{11,8,2,0};auto points=e.points();std::vector<I>counts;std::vector<std::string>lists;for(P s:{P(0,0),P(1,0),P(2,0)}){std::vector<P>good;for(P t:points){bool ok=true;for(P p:points)ok &= e.add(e.neg(e.add(p,s)),t)==e.neg(e.add(e.add(p,t),s));if(ok)good.push_back(t);}counts.push_back(good.size());lists.push_back(ps(good));}P s(0,0),t(5,4);return {{"curve_model",q("y^2=x^3+8*x^2+2*x over F11")},{"point_count",n(points.size())},{"points",ps(points)},{"commuting_counts",nums(counts)},{"commuting_points",arr(lists)},{"witness_left",e.add(e.neg(s),t).s()},{"witness_right",e.neg(e.add(t,s)).s()},{"double_T",e.add(t,t).s()},{"bound",n(ipow(4,2)*6)},{"nearby_bound",n(ipow(4,3)*6)},{"gap",n(ipow(4,3)*6-ipow(4,2)*6)}};}
O chord(){E e{17,0,1,1};P a(0,1),z(4,1),given(13,16),control(0,16);I slope=mod((z.y-a.y)*powmod(z.x-a.x,15,17),17);P sum=e.add(a,z);auto col=[&](P t){return mod((z.x-a.x)*(t.y-a.y)-(z.y-a.y)*(t.x-a.x),17)==0;};return {{"points_on_curve",arr({b(e.on(a)),b(e.on(z)),b(e.on(given))})},{"chord_collinear",b(col(given))},{"third_intersection",e.neg(sum).s()},{"sum_of_first_two",sum.s()},{"control_collinear",b(col(control))},{"slope",n(slope)}};}
O window(){E e{151,0,1,3};P p(1,55),t;I order=0;do{t=e.add(t,p);++order;if(order>1000)throw std::runtime_error("order bound");}while(!t.inf);O out;out["point_order"]=n(order);out["point_count"]=n(e.points().size());out["point_on_curve"]=b(e.on(p));out["j"]=n(mod(1728*4*powmod(mod(4+27*9,151),149,151),151));out["residue_1728"]=n(1728%151);std::vector<I>counts,orders;for(I lambda:{5,23}){I v=1,morder=0;do{v=v*lambda%167;morder++;}while(v!=1&&morder<=167);orders.push_back(morder);std::vector<I>scalars;std::vector<P>pts;v=1;for(int i=0;i<8;i++){scalars.push_back(v);pts.push_back(e.mul(v,p));v=v*lambda%167;}std::set<P>sums;for(int i=0;i<8;i++)for(int j=i;j<8;j++)sums.insert(e.add(pts[i],pts[j]));counts.push_back(sums.size());out["scalars_"+n(lambda)]=nums(scalars);out["window_"+n(lambda)]=ps(pts);out["pair_sums_"+n(lambda)]=ps(std::vector<P>(sums.begin(),sums.end()));}out["multiplier_orders"]=nums(orders);out["pair_sum_5"]=n(counts[0]);out["pair_sum_23"]=n(counts[1]);out["shortfall"]=n(counts[0]-counts[1]);out["ceiling"]=n(8*9/2);out["escape_fraction"]=R(1,8).s();Big lhs=power(167,100),lo=power(9,100),hi=lo;for(int i=0;i<421;i++)lo.times(2);for(int i=0;i<422;i++)hi.times(2);out["log_sides"]=arr({b(lo<lhs),b(lhs<hi)});out["sqrt_squares"]=nums({2828LL*2828,2829LL*2829});out["sqrt_sides"]=arr({b(2828LL*2828<8LL*1000*1000),b(8LL*1000*1000<2829LL*2829)});return out;}
O cancellation(){std::vector<std::string>rows;for(auto p:std::vector<std::array<I,3>>{{2,1,2},{4,2,1}}){I x=p[0],y=p[1],l=p[2],def=x*x*x+x+1-y*y,lhs=3*y*y-2*x-3,rhs=3*x*x*x+x;rows.push_back(obj({{"x",n(x)},{"y",n(y)},{"lambda",n(l)},{"defect",n(def)},{"lhs",n(lhs)},{"rhs",n(rhs)},{"gap",n(rhs-lhs)},{"three_times_defect",n(3*def)},{"y_gap",n(l*(rhs-lhs))},{"x_cross",n(2*l*x*y)},{"ref_cross",n(l*(2*x+3)*2*y-x*y)},{"defect_remainder",n(mod(def,5))},{"ref_remainder",n(mod(l*(2*x+3)*2*y-x*y,5))}}));}return {{"rows",arr(rows)}};}
struct G{std::vector<int>f;std::vector<int>stores;int cap;};
std::vector<int> dist(const G&g,int store){std::vector<int>d(g.f.size(),1000);for(size_t start=0;start<g.f.size();start++){int v=start;for(int k=0;k<=g.cap+1;k++){if(v==store){d[start]=k;break;}v=g.f[v];}}return d;}
O graphs(){G path{{1,2,3,4,5,6,7,7},{3,5},4},cyc{{1,2,3,4,5,6,7,0},{0},3};auto d0=dist(path,3),d1=dist(path,5),dc=dist(cyc,0);std::vector<I>a,z,united,inter,basins{0,0};for(int i=0;i<8;i++){if(d0[i]<=4)a.push_back(i);if(d1[i]<=4)z.push_back(i);if(std::min(d0[i],d1[i])<=4){united.push_back(i);basins[d0[i]<=d1[i]?0:1]++;}if(d0[i]<=4&&d1[i]<=4)inter.push_back(i);}O out{{"path_cover_sets",arr({nums(a),nums(z)})},{"cover_sizes",nums({I(a.size()),I(z.size())})},{"cover_union",n(united.size())},{"intersection",n(inter.size())},{"size_sum",n(a.size()+z.size())},{"basin_sizes",nums(basins)},{"uncovered",n(8-united.size())}};std::vector<std::string>variants;for(int extra:{0,1}){I sp=0,sc=0,covered=0;for(int i=0;i<8;i++){sp+=std::min(4+extra,std::min(d0[i],d1[i]));sc+=std::min(3+extra,dc[i]);covered+=dc[i]<=3;}R pc(sp,united.size()),cc(sc,covered),pk=R(2)*pc*pc/R(8),ck=cc*cc/R(8),oracle(41,25);std::vector<std::string>costs;for(R lambda:{R(0),R(1,100),R(1,10)})costs.push_back((pc*(R(1)+lambda)).s());variants.push_back(obj({{"convention",q(extra?"min(D+1,tau)":"min(D,tau)")},{"path_truncated_sum",n(sp)},{"cycle_truncated_sum",n(sc)},{"path_cost",pc.s()},{"cycle_cost",cc.s()},{"path_constant",pk.s()},{"cycle_constant",ck.s()},{"path_gap",(oracle-pk).s()},{"cycle_gap",(ck-oracle).s()},{"lambda_costs",arr(costs)}}));}out["conventions"]=arr(variants);R oracle(41,25),low=R(11,20)*oracle,high=R(17,20)*oracle;out["band_low"]=low.s();out["band_high"]=high.s();out["band_low_gap"]=(low-R(9,10)).s();out["band_high_gap"]=(R(7,5)-high).s();out["falsifier"]=(R(19,20)*oracle).s();out["twice_gap"]=(R(2)*oracle-R(16,5)).s();I residual_sum=0;for(int i=0;i<4;i++)residual_sum+=i;out["spacing_ratio"]=(R(residual_sum,4)/R(4)).s();R s(0);I factorial=1;for(int k=0;k<=8;k++){if(k)factorial*=k;s=s+R(1,factorial);}R upper=s+R(10,9*factorial*9),lower_one=R(1)-R(s.d,s.p),upper_one=R(1)-R(upper.d,upper.p);out["series_partial"]=s.s();out["one_minus_lower"]=lower_one.s();out["one_minus_upper"]=upper_one.s();out["series_strict_bounds"]=arr({b(R(632,1000)<lower_one),b(upper_one<R(633,1000))});I product=1;for(int r:{1,2,4,8,16})product*=r;out["rung_product"]=n(product);return out;}
O run(const std::string&s){if(s=="95f69f")return low();if(s=="c9110e")return translation();if(s=="efafc0")return chord();if(s=="d68ac9")return window();if(s=="f7310e")return cancellation();if(s=="c9c5a4")return graphs();throw std::runtime_error("unknown worksheet");}
void selftest(){E e{5,0,1,1};P p(0,1);if(!e.on(p)||!e.add(p,e.neg(p)).inf||!(e.add(p,p)==P(4,2))||!(power(2,3)<power(3,3)))throw std::runtime_error("synthetic control");if((R(1,2)+R(1,3)).p!=5||(R(1,2)+R(1,3)).d!=6)throw std::runtime_error("rational control");auto pts=e.points();for(P a:pts)for(P z:pts){if(!e.on(e.add(a,z))||!(e.add(a,z)==e.add(z,a)))throw std::runtime_error("synthetic closure/commutation");for(P c:pts)if(!(e.add(e.add(a,z),c)==e.add(a,e.add(z,c))))throw std::runtime_error("synthetic associativity");}if(!(power(167,100)<power(168,100)))throw std::runtime_error("large integer synthetic control");}
}
int main(int argc,char**argv){try{if(argc==2&&std::string(argv[1])=="--self-test"){first::selftest();std::cout<<"{\"synthetic_control\":true,\"frozen_worksheet_executed\":false}\n";return 0;}if(argc!=1)throw std::runtime_error("no arithmetic parameters are accepted; source is frozen");std::cout<<first::obj(first::run(WORKSHEET_KIND))<<"\n";}catch(const std::exception&e){std::cerr<<e.what()<<"\n";return 1;}}
