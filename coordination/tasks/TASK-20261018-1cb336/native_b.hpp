// Route B: independently written counting, polynomial restriction and integers.
// Does not include or call route A, including its field/group routines.
#include <algorithm>
#include <array>
#include <iostream>
#include <map>
#include <queue>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>
namespace second {
using Z=long long;using Record=std::map<std::string,std::string>;
std::string text(std::string x){return '"'+x+'"';}
std::string integer(Z x){return std::to_string(x);}
std::string boolean(bool x){return x?"true":"false";}
std::string list(std::vector<std::string>x){std::string r="[";for(size_t j=0;j<x.size();++j){if(j)r+=",";r+=x[j];}return r+"]";}
std::string numbers(std::vector<Z>x){std::vector<std::string>r;for(Z a:x)r.push_back(integer(a));return list(r);}
std::string dictionary(Record x){std::vector<std::string>r;for(auto entry:x)r.push_back(text(entry.first)+":"+entry.second);std::string a=list(r);a.front()='{';a.back()='}';return a;}
Z residue(Z a,Z p){while(a<0)a+=p;return a%p;}
struct Fraction{
 Z top,bottom;
 Fraction(Z x=0,Z y=1):top(x),bottom(y){if(!y)throw std::runtime_error("zero denominator");if(bottom<0)top=-top,bottom=-bottom;Z a=top<0?-top:top,b=bottom;while(b){Z t=a%b;a=b;b=t;}top/=a;bottom/=a;}
 std::string encoded()const{return text(integer(top)+"/"+integer(bottom));}
};
Fraction plus(Fraction x,Fraction y){return {x.top*y.bottom+y.top*x.bottom,x.bottom*y.bottom};}
Fraction minus(Fraction x,Fraction y){return {x.top*y.bottom-y.top*x.bottom,x.bottom*y.bottom};}
Fraction times(Fraction x,Fraction y){return {x.top*y.top,x.bottom*y.bottom};}
Fraction divide(Fraction x,Fraction y){return {x.top*y.bottom,x.bottom*y.top};}
bool less(Fraction x,Fraction y){return x.top*y.bottom<y.top*x.bottom;}
struct Point{
 Z x=-1,y=-1;
 bool zero()const{return x<0;}
 bool operator==(Point z)const{return x==z.x&&y==z.y;}
 bool operator<(Point z)const{if(zero()!=z.zero())return !zero();if(x!=z.x)return x<z.x;return y<z.y;}
 std::string encoded()const{return zero()?"null":numbers({x,y});}
};
std::string pointlist(std::vector<Point>x){std::vector<std::string>r;for(auto p:x)r.push_back(p.encoded());return list(r);}
struct Cubic{
 Z prime,c2,c1,c0;
 Z reduced(Z a)const{return residue(a,prime);}
 bool contains(Point a)const{return a.zero()||reduced(a.y*a.y)==reduced(((a.x+c2)*a.x+c1)*a.x+c0);}
 Point opposite(Point a)const{return a.zero()?a:Point{a.x,reduced(prime-a.y)};}
 Point join(Point a,Point b)const{
  if(a.zero())return b;
  if(b.zero())return a;
  if(a.x==b.x&&reduced(a.y+b.y)==0)return {};
  Z den,num;if(a==b){den=reduced(2*a.y);num=reduced(3*a.x*a.x+2*c2*a.x+c1);}else{den=reduced(b.x-a.x);num=reduced(b.y-a.y);}
  Z slope=-1;for(Z candidate=0;candidate<prime;++candidate)if(reduced(candidate*den)==num){slope=candidate;break;}
  if(slope<0)throw std::runtime_error("no unique chord slope");
  Z intercept=reduced(a.y-slope*a.x);
  // Restrict cubic to the line and divide by both known roots, with
  // multiplicity for tangency. This is not route A's addition formula.
  std::vector<Z>coeff{reduced(c0-intercept*intercept),reduced(c1-2*slope*intercept),reduced(c2-slope*slope),1};
  for(Z root:{a.x,b.x}){std::vector<Z>quotient(coeff.size()-1);quotient.back()=coeff.back();for(int i=int(quotient.size())-1;i>0;--i)quotient[i-1]=reduced(coeff[i]+root*quotient[i]);if(reduced(coeff[0]+root*quotient[0]))throw std::runtime_error("non-root in chord restriction");coeff=quotient;}
  Z third=-1;for(Z candidate=0;candidate<prime;++candidate)if(reduced(coeff[0]+coeff[1]*candidate)==0){third=candidate;break;}
  if(third<0)throw std::runtime_error("third root absent");
  return {third,reduced(-slope*third-intercept)};
 }
 std::vector<Point> enumerate()const{std::vector<Point>x{{}};for(Z a=0;a<prime;++a)for(Z b=0;b<prime;++b)if(contains({a,b}))x.push_back({a,b});return x;}
};
// Decimal grade-school integer, independent of route A's binary limbs.
struct Decimal{
 std::vector<int>digit{1};
 void multiply(unsigned value){unsigned carry=0;for(int&v:digit){unsigned t=unsigned(v)*value+carry;v=int(t%10);carry=t/10;}while(carry){digit.push_back(carry%10);carry/=10;}}
 bool below(Decimal other)const{if(digit.size()!=other.digit.size())return digit.size()<other.digit.size();for(size_t i=digit.size();i-->0;)if(digit[i]!=other.digit[i])return digit[i]<other.digit[i];return false;}
};
Decimal repeated(unsigned base,int exponent){Decimal r;for(int i=0;i<exponent;++i)r.multiply(base);return r;}
Record reduction(){Record output;for(int modulus:{17,4}){std::vector<std::string>image_sets;std::vector<Z>sizes;Z failures=0,visited=0;for(int left=0;left<4;++left)for(int right=0;right<4;++right){std::vector<Z>seen;for(int a=left;a<modulus;a+=4)for(int b=right;b<modulus;b+=4){Z value=residue(residue(a+b,modulus),4);if(std::find(seen.begin(),seen.end(),value)==seen.end())seen.push_back(value);if(value!=(left+right)%4)++failures;++visited;}std::sort(seen.begin(),seen.end());sizes.push_back(seen.size());image_sets.push_back(numbers(seen));}auto prefix="mod"+integer(modulus)+"_";output[prefix+"images"]=list(image_sets);output[prefix+"image_sizes"]=numbers(sizes);output[prefix+"mismatches"]=integer(failures);output[prefix+"pairs"]=integer(visited);}output["residue_pairs"]="16";return output;}
Record translations(){Cubic curve{11,8,2,0};auto all=curve.enumerate();std::vector<Point>kernel;for(auto p:all)if(curve.join(p,p).zero())kernel.push_back(p);std::vector<std::string>sets;std::vector<Z>counts;for(auto s:std::vector<Point>{{0,0},{1,0},{2,0}}){if(!curve.contains(s)||!curve.join(s,s).zero())throw std::runtime_error("center is not two-torsion");counts.push_back(kernel.size());sets.push_back(pointlist(kernel));}Point t{5,4},s{0,0};Z low=6,high=6;for(int k=0;k<2;++k)low*=4;for(int k=0;k<3;++k)high*=4;return {{"curve_model",text("y^2=x^3+8*x^2+2*x over F11")},{"point_count",integer(all.size())},{"points",pointlist(all)},{"commuting_counts",numbers(counts)},{"commuting_points",list(sets)},{"witness_left",curve.join(curve.opposite(s),t).encoded()},{"witness_right",curve.opposite(curve.join(t,s)).encoded()},{"double_T",curve.join(t,t).encoded()},{"bound",integer(low)},{"nearby_bound",integer(high)},{"gap",integer(high-low)}};}
Record incidence(){Cubic curve{17,0,1,1};Point p{0,1},q{4,1},candidate{13,16},control{0,16};Z m=-1;for(Z a=0;a<17;++a)if(residue(a*(q.x-p.x),17)==residue(q.y-p.y,17))m=a;Z c=residue(p.y-m*p.x,17);std::vector<Point>remaining;for(Z x=0;x<17;++x){Point r{x,residue(m*x+c,17)};if(curve.contains(r)&&!(r==p)&&!(r==q))remaining.push_back(r);}if(remaining.size()!=1)throw std::runtime_error("restricted cubic did not have one remaining root");auto col=[&](Point r){return residue(r.y-m*r.x-c,17)==0;};return {{"points_on_curve",list({boolean(curve.contains(p)),boolean(curve.contains(q)),boolean(curve.contains(candidate))})},{"chord_collinear",boolean(col(candidate))},{"third_intersection",remaining[0].encoded()},{"sum_of_first_two",curve.opposite(remaining[0]).encoded()},{"control_collinear",boolean(col(control))},{"slope",integer(m)}};}
Record windows(){Cubic curve{151,0,1,3};Point p{1,55},acc;std::vector<Point>multiples{{}};for(int k=1;k<=1000;++k){acc=curve.join(acc,p);multiples.push_back(acc);if(acc.zero())break;}if(!multiples.back().zero())throw std::runtime_error("bounded order test incomplete");Z order=multiples.size()-1;Record output{{"point_order",integer(order)},{"point_count",integer(curve.enumerate().size())},{"point_on_curve",boolean(curve.contains(p))},{"residue_1728",integer(1728%151)}};Z discriminant=residue(4+27*9,151),j=-1;for(Z value=0;value<151;++value)if(residue(value*discriminant,151)==residue(1728*4,151))j=value;output["j"]=integer(j);std::vector<Z>counts,orders;for(Z lambda:{5,23}){Z element=1,length=0;do{element=(element*lambda)%167;++length;}while(element!=1&&length<=167);orders.push_back(length);std::vector<Z>scalars;std::vector<Point>points;Z scalar=1;for(int k=0;k<8;++k){scalars.push_back(scalar);if(scalar>=order)throw std::runtime_error("scalar outside certified point order");points.push_back(multiples[scalar]);scalar=scalar*lambda%167;}std::vector<Point>sums;for(int k=7;k>=0;--k)for(int l=7;l>=k;--l){Point sum=curve.join(points[k],points[l]);if(std::find(sums.begin(),sums.end(),sum)==sums.end())sums.push_back(sum);}std::sort(sums.begin(),sums.end());counts.push_back(sums.size());output["scalars_"+integer(lambda)]=numbers(scalars);output["window_"+integer(lambda)]=pointlist(points);output["pair_sums_"+integer(lambda)]=pointlist(sums);}output["multiplier_orders"]=numbers(orders);output["pair_sum_5"]=integer(counts[0]);output["pair_sum_23"]=integer(counts[1]);output["shortfall"]=integer(counts[0]-counts[1]);Z pairs=0;for(int i=1;i<=8;++i)pairs+=i;output["ceiling"]=integer(pairs);output["escape_fraction"]=Fraction(1,8).encoded();Decimal left=repeated(167,100),right=repeated(9,100);for(int k=0;k<421;++k)right.multiply(2);bool lo=right.below(left);right.multiply(2);output["log_sides"]=list({boolean(lo),boolean(left.below(right))});Z a=2828*2828,b=2829*2829;output["sqrt_squares"]=numbers({a,b});output["sqrt_sides"]=list({boolean(a<8000000),boolean(8000000<b)});return output;}
Record cancellation(){std::vector<std::string>items;for(auto coordinates:std::vector<std::array<Z,3>>{{2,1,2},{4,2,1}}){Z x=coordinates[0],y=coordinates[1],lambda=coordinates[2];Z polynomial=(x*x+1)*x+1,defect=polynomial-y*y,gap=3*defect,rhs=x*(3*x*x+1),lhs=rhs-gap;Z xdisplacement=2*lambda*x,reference_numerator=lambda*(2*x+3),cross=reference_numerator*(y+y)-x*y;items.push_back(dictionary({{"x",integer(x)},{"y",integer(y)},{"lambda",integer(lambda)},{"defect",integer(defect)},{"lhs",integer(lhs)},{"rhs",integer(rhs)},{"gap",integer(gap)},{"three_times_defect",integer(defect+defect+defect)},{"y_gap",integer(lambda*3*defect)},{"x_cross",integer(xdisplacement*y)},{"ref_cross",integer(cross)},{"defect_remainder",integer(residue(defect,5))},{"ref_remainder",integer(residue(cross,5))}}));}return {{"rows",list(items)}};}
std::vector<int> ancestors(std::vector<int>map,int mark){std::vector<int>d(map.size(),1000);std::queue<int>todo;d[mark]=0;todo.push(mark);while(!todo.empty()){int current=todo.front();todo.pop();for(size_t x=0;x<map.size();++x)if(map[x]==current&&d[x]>d[current]+1){d[x]=d[current]+1;todo.push(x);}}return d;}
Record covers(){auto left=ancestors({1,2,3,4,5,6,7,7},3),right=ancestors({1,2,3,4,5,6,7,7},5),circle=ancestors({1,2,3,4,5,6,7,0},0);std::vector<Z>cover_a,cover_b,union_set,intersection;Z ba=0,bb=0;for(int point=0;point<8;++point){bool a=left[point]<=4,b=right[point]<=4;if(a)cover_a.push_back(point);if(b)cover_b.push_back(point);if(a||b){union_set.push_back(point);if(left[point]<=right[point])++ba;else ++bb;}if(a&&b)intersection.push_back(point);}Record output{{"path_cover_sets",list({numbers(cover_a),numbers(cover_b)})},{"cover_sizes",numbers({Z(cover_a.size()),Z(cover_b.size())})},{"cover_union",integer(union_set.size())},{"intersection",integer(intersection.size())},{"size_sum",integer(cover_a.size()+cover_b.size())},{"basin_sizes",numbers({ba,bb})},{"uncovered",integer(8-union_set.size())}};std::vector<std::string>variants;Fraction oracle(41,25);for(int convention=0;convention<=1;++convention){Z ptotal=0,ctotal=0,ccover=0;for(int point=0;point<8;++point){int pd=left[point]<right[point]?left[point]:right[point];ptotal+=pd<4+convention?pd:4+convention;ctotal+=circle[point]<3+convention?circle[point]:3+convention;if(circle[point]<=3)++ccover;}Fraction pcost(ptotal,union_set.size()),ccost(ctotal,ccover);auto pconstant=divide(times(Fraction(2),times(pcost,pcost)),Fraction(8));auto cconstant=divide(times(ccost,ccost),Fraction(8));std::vector<std::string>weighted;for(Fraction probe:{Fraction(0),Fraction(1,100),Fraction(1,10)})weighted.push_back(times(pcost,plus(Fraction(1),probe)).encoded());variants.push_back(dictionary({{"convention",text(convention?"min(D+1,tau)":"min(D,tau)")},{"path_truncated_sum",integer(ptotal)},{"cycle_truncated_sum",integer(ctotal)},{"path_cost",pcost.encoded()},{"cycle_cost",ccost.encoded()},{"path_constant",pconstant.encoded()},{"cycle_constant",cconstant.encoded()},{"path_gap",minus(oracle,pconstant).encoded()},{"cycle_gap",minus(cconstant,oracle).encoded()},{"lambda_costs",list(weighted)}}));}output["conventions"]=list(variants);auto low=times(Fraction(11,20),oracle),high=times(Fraction(17,20),oracle);output["band_low"]=low.encoded();output["band_high"]=high.encoded();output["band_low_gap"]=minus(low,Fraction(9,10)).encoded();output["band_high_gap"]=minus(Fraction(7,5),high).encoded();output["falsifier"]=times(Fraction(19,20),oracle).encoded();output["twice_gap"]=minus(plus(oracle,oracle),Fraction(16,5)).encoded();Fraction regular;for(int offset=3;offset>=0;--offset)regular=plus(regular,Fraction(offset,4));output["spacing_ratio"]=divide(regular,Fraction(4)).encoded();Z fact=1;Fraction partial(1);for(int k=1;k<=8;++k){fact*=k;partial=plus(partial,Fraction(1,fact));}Fraction tail=divide(Fraction(1,fact*9),minus(Fraction(1),Fraction(1,10)));Fraction e_upper=plus(partial,tail);auto lower=minus(Fraction(1),Fraction(partial.bottom,partial.top));auto upper=minus(Fraction(1),Fraction(e_upper.bottom,e_upper.top));output["series_partial"]=partial.encoded();output["one_minus_lower"]=lower.encoded();output["one_minus_upper"]=upper.encoded();output["series_strict_bounds"]=list({boolean(less(Fraction(632,1000),lower)),boolean(less(upper,Fraction(633,1000)))});Z product=1;for(int k=0;k<5;++k){Z factor=1;for(int j=0;j<k;++j)factor*=2;product*=factor;}output["rung_product"]=integer(product);return output;}
Record calculate(std::string code){if(code=="95f69f")return reduction();if(code=="c9110e")return translations();if(code=="efafc0")return incidence();if(code=="d68ac9")return windows();if(code=="f7310e")return cancellation();if(code=="c9c5a4")return covers();throw std::runtime_error("unknown worksheet");}
void synthetic(){Cubic curve{7,0,1,1};Point p{0,1};if(!curve.contains(p)||!curve.join(p,curve.opposite(p)).zero()||!(curve.join(p,p)==Point{2,5}))throw std::runtime_error("group control failed");Fraction value=plus(Fraction(1,7),Fraction(2,7));if(value.top!=3||value.bottom!=7||!repeated(3,4).below(repeated(4,4)))throw std::runtime_error("integer control failed");auto all=curve.enumerate();for(Point a:all)for(Point b:all){if(!curve.contains(curve.join(a,b))||!(curve.join(a,b)==curve.join(b,a)))throw std::runtime_error("synthetic closure/commutation");for(Point c:all)if(!(curve.join(curve.join(a,b),c)==curve.join(a,curve.join(b,c))))throw std::runtime_error("synthetic associativity");}if(!repeated(167,100).below(repeated(168,100)))throw std::runtime_error("decimal large integer synthetic control");}
}
int main(int argc,char**argv){try{if(argc==2&&std::string(argv[1])=="--self-test"){second::synthetic();std::cout<<"{\"synthetic_control\":true,\"frozen_worksheet_executed\":false}\n";return 0;}if(argc!=1)throw std::runtime_error("no arithmetic parameters accepted");std::cout<<second::dictionary(second::calculate(WORKSHEET_KIND))<<"\n";}catch(const std::exception&e){std::cerr<<e.what()<<"\n";return 1;}}
