// Exact local-basis audits.  This is not an ECDLP solver or a global lower bound.
// Rational/tensor conventions adapt the immutable first-pilot circuit.cpp.
#include <algorithm>
#include <array>
#include <bit>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <limits>
#include <map>
#include <numeric>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>

namespace audit {
using I=std::int64_t;
using U=std::uint64_t;
void require(bool x,const std::string& s){if(!x)throw std::runtime_error(s);}
struct R {
 I n=0,d=1;
 R(I a=0,I b=1):n(a),d(b){
  require(d!=0,"zero rational denominator");
  require(n!=std::numeric_limits<I>::min()&&d!=std::numeric_limits<I>::min(),"rational normalization overflow");
  if(d<0){n=-n;d=-d;}const I g=std::gcd(n,d);n/=g;d/=g;
 }
 static I mul(I a,I b){I z=0;require(!__builtin_mul_overflow(a,b,&z),"rational product overflow");return z;}
 static I add(I a,I b){I z=0;require(!__builtin_add_overflow(a,b,&z),"rational sum overflow");return z;}
 friend R operator+(R a,R b){const I g=std::gcd(a.d,b.d);return {add(mul(a.n,b.d/g),mul(b.n,a.d/g)),mul(a.d/g,b.d)};}
 friend R operator-(R a){require(a.n!=std::numeric_limits<I>::min(),"rational negation overflow");return {-a.n,a.d};}
 friend R operator-(R a,R b){return a+(-b);}
 friend R operator*(R a,R b){const I g=std::gcd(a.n,b.d),h=std::gcd(b.n,a.d);return {mul(a.n/g,b.n/h),mul(a.d/h,b.d/g)};}
 friend R operator/(R a,R b){require(b.n!=0,"rational division by zero");return a*R(b.d,b.n);}
 friend bool operator==(const R&,const R&)=default;
};
struct F2 {
 unsigned v=0;
 F2(I n=0):v(static_cast<unsigned>(n&1)){}
 friend F2 operator+(F2 a,F2 b){return F2(a.v^b.v);}
 friend F2 operator-(F2 a){return a;}
 friend F2 operator-(F2 a,F2 b){return a+b;}
 friend F2 operator*(F2 a,F2 b){return F2(a.v&b.v);}
 friend F2 operator/(F2 a,F2 b){require(b.v==1,"F2 division by zero");return a;}
 friend bool operator==(const F2&,const F2&)=default;
};
// Tiny square-zero ring F2[e]/(e²), encoded constant+2*linear.
struct E {
 unsigned v=0;
 E(I n=0):v(static_cast<unsigned>(n)&3U){}
 friend E operator+(E a,E b){return E(a.v^b.v);}
 friend E operator-(E a){return a;}
 friend E operator-(E a,E b){return a+b;}
 friend E operator*(E a,E b){const unsigned ac=(a.v&1U)&(b.v&1U),u=((a.v&1U)*(b.v>>1U))^((b.v&1U)*(a.v>>1U));return E(ac|(u<<1U));}
 friend E operator/(E a,E b){require((b.v&1U)==1,"square-zero nonunit inverse");return a*b;}
 friend bool operator==(const E&,const E&)=default;
};

// Ordinary polynomial algebra over F2.  Exponents are NEVER reduced by x²=x.
constexpr std::size_t variables=20;
using Monomial=std::array<unsigned char,variables>;
struct Poly {
 std::set<Monomial> terms;
 Poly(I constant=0){if((constant&1)!=0)terms.insert(Monomial{});}
 static Poly variable(std::size_t i){require(i<variables,"bad polynomial variable");Poly p;Monomial m{};m[i]=1;p.terms.insert(m);return p;}
 friend Poly operator+(Poly a,const Poly& b){for(const auto&m:b.terms){auto [it,added]=a.terms.insert(m);if(!added)a.terms.erase(it);}return a;}
 friend Poly operator-(const Poly&a){return a;}
 friend Poly operator-(Poly a,const Poly&b){return a+b;}
 friend Poly operator*(const Poly&a,const Poly&b){Poly out;for(const auto&x:a.terms)for(const auto&y:b.terms){Monomial m{};for(std::size_t i=0;i<variables;++i){const unsigned z=static_cast<unsigned>(x[i])+static_cast<unsigned>(y[i]);require(z<=255,"polynomial exponent overflow");m[i]=static_cast<unsigned char>(z);}auto[it,added]=out.terms.insert(m);if(!added)out.terms.erase(it);}return out;}
 friend bool operator==(const Poly&,const Poly&)=default;
};

template<class S>using Matrix=std::array<std::array<S,2>,2>;
template<class S>S det(const Matrix<S>&m){return m[0][0]*m[1][1]-m[0][1]*m[1][0];}
template<class S>Matrix<S> inverse_transpose(const Matrix<S>&m){const auto d=det(m);return {{{m[1][1]/d,-m[1][0]/d},{-m[0][1]/d,m[0][0]/d}}};}
template<class S>struct Tensor {unsigned arity;std::vector<S> v;};
template<class S>Tensor<S> and_tensor(){Tensor<S>t{3,std::vector<S>(8)};for(unsigned i:{0U,1U,2U,7U})t.v[i]=S(1);return t;}
template<class S>Tensor<S> pin(unsigned value){Tensor<S>t{1,std::vector<S>(2)};t.v[value]=S(1);return t;}
template<class S>Tensor<S> transform(Tensor<S>t,const std::vector<Matrix<S>>&legs){
 require(legs.size()==t.arity,"wrong leg transform count");
 for(unsigned leg=0;leg<t.arity;++leg){auto z=t.v;for(unsigned mask=0;mask<(1U<<t.arity);++mask){z[mask]=S(0);for(unsigned i=0;i<2;++i)z[mask]=z[mask]+legs[leg][(mask>>leg)&1U][i]*t.v[(mask&~(1U<<leg))|(i<<leg)];}t.v=std::move(z);}return t;
}
template<class S>Tensor<S> uniform_and(const Matrix<S>&m){const auto n=inverse_transpose(m);return transform(and_tensor<S>(),{n,n,m});}
struct Result {bool parity=true,gp=true;int even=-1,odd=-1;U checks=0;};
template<class S>Result identities(const Tensor<S>&t){
 Result out;for(unsigned i=0;i<t.v.size();++i)if(t.v[i]!=S(0)){if((std::popcount(i)&1)==0){if(out.even<0)out.even=static_cast<int>(i);}else if(out.odd<0)out.odd=static_cast<int>(i);}
 out.parity=out.even<0||out.odd<0;
 for(unsigned a=0;a<t.v.size();++a)for(unsigned b=0;b<t.v.size();++b){S sum(0);unsigned order=0;for(unsigned j=0;j<t.arity;++j)if(((a^b)&(1U<<j))!=0){++order;const S p=t.v[a^(1U<<j)]*t.v[b^(1U<<j)];sum=sum+((order&1U)!=0?-p:p);}++out.checks;if(sum!=S(0))out.gp=false;}
 return out;
}
template<class S>S invariant_B(const Tensor<S>&t){require(t.arity==3,"B requires three legs");S out(0);for(unsigned i=0;i<4;++i)out=out+t.v[i]*t.v[i^7U];return out;}
template<class S>U wire_checks(const Matrix<S>&m){const auto n=inverse_transpose(m);for(unsigned x=0;x<2;++x)for(unsigned y=0;y<2;++y){S z(0);for(unsigned j=0;j<2;++j)z=z+m[j][x]*n[j][y];require(z==S(x==y?1:0),"wire contraction changed");}return 4;}
template<class S>bool monomial(const Matrix<S>&m){return (m[0][1]==S(0)&&m[1][0]==S(0))||(m[0][0]==S(0)&&m[1][1]==S(0));}

template<class S>void scalar_json(std::ostream&o,const S&s);
template<>void scalar_json<R>(std::ostream&o,const R&s){o<<'['<<s.n<<','<<s.d<<']';}
template<>void scalar_json<F2>(std::ostream&o,const F2&s){o<<s.v;}
template<class S>void vector_json(std::ostream&o,const std::vector<S>&v){o<<'[';for(std::size_t i=0;i<v.size();++i){if(i)o<<',';scalar_json(o,v[i]);}o<<']';}
template<class S>void matrix_json(std::ostream&o,const Matrix<S>&m){o<<'[';for(unsigned i=0;i<2;++i){if(i)o<<',';o<<'[';for(unsigned j=0;j<2;++j){if(j)o<<',';scalar_json(o,m[i][j]);}o<<']';}o<<']';}
void integer_matrix_json(std::ostream&o,const Matrix<R>&m){o<<"[["<<m[0][0].n<<','<<m[0][1].n<<"],["<<m[1][0].n<<','<<m[1][1].n<<"]]";}
void monomials_json(std::ostream&o,const Poly&p){o<<'[';bool first=true;for(const auto&m:p.terms){if(!first)o<<',';first=false;o<<'[';bool f=true;for(std::size_t i=0;i<variables;++i)for(unsigned j=0;j<m[i];++j){if(!f)o<<',';f=false;o<<i;}o<<']';}o<<']';}

std::vector<Matrix<R>> rational_grammar(){std::vector<Matrix<R>>v;for(I a=-2;a<=2;++a)for(I b=-2;b<=2;++b)for(I c=-2;c<=2;++c)for(I d=-2;d<=2;++d){Matrix<R>m{{{R(a),R(b)},{R(c),R(d)}}};if(det(m)!=R(0))v.push_back(m);}return v;}
std::vector<Matrix<F2>> binary_grammar(){std::vector<Matrix<F2>>v;for(I a=0;a<2;++a)for(I b=0;b<2;++b)for(I c=0;c<2;++c)for(I d=0;d<2;++d){Matrix<F2>m{{{F2(a),F2(b)},{F2(c),F2(d)}}};if(det(m)!=F2(0))v.push_back(m);}return v;}
std::vector<Matrix<E>> ring_grammar(){std::vector<Matrix<E>>v;for(I a=0;a<4;++a)for(I b=0;b<4;++b)for(I c=0;c<4;++c)for(I d=0;d<4;++d){Matrix<E>m{{{E(a),E(b)},{E(c),E(d)}}};if((det(m).v&1U)!=0)v.push_back(m);}return v;}

struct Symbolic {Poly lhs,rhs;};
Symbolic symbolic_identity(){
 Tensor<Poly> t{3,std::vector<Poly>(8)};for(unsigned i=0;i<8;++i)t.v[i]=Poly::variable(i);
 std::vector<Matrix<Poly>>legs(3);for(unsigned leg=0;leg<3;++leg)for(unsigned i=0;i<2;++i)for(unsigned j=0;j<2;++j)legs[leg][i][j]=Poly::variable(8+leg*4+i*2+j);
 auto lhs=invariant_B(transform(t,legs));auto rhs=det(legs[0])*det(legs[1])*det(legs[2])*invariant_B(t);
 require(lhs==rhs,"universal characteristic-two covariance expansion failed");
 require(lhs.terms.size()==32,"unexpected covariance normal form size");
 for(const auto&m:lhs.terms)require(std::accumulate(m.begin(),m.end(),0U)==8U,"covariance monomial degree changed");
 const auto x=Poly::variable(0);require(x*x!=x,"polynomial backend incorrectly reduced x squared");
 require(lhs!=rhs+x,"polynomial mutation trap failed");return {lhs,rhs};
}

struct Stats {U q=0,q_and=0,q_joint=0,q_pins=0,old=0,old_and=0,f2=0,f2_and=0,independent=0,independent_pure=0,ring=0,ring_pure=0,gp=0,wire=0,calibrations=0;};
std::string first_mixed(const Result&p0,const Result&p1,const Result&a){if(!p0.parity)return "CONST0";if(!p1.parity)return "CONST1";if(!a.parity)return "AND";return "none";}
void record_prefix(std::ostream&o,const char*kind){o<<"{\"track\":\"L4-audit\",\"fixture\":\"shared_basis_audit\",\"scope\":\"exploratory_toy_followup\",\"row_kind\":\""<<kind<<"\",\"outcome\":\"complete_valid\"";}

void calibrate(Stats&s){
 const Matrix<R>positive{{{R(1),R(2)},{R(1),R(0)}}};const auto a=uniform_and(positive);const auto result=identities(a);
 const std::vector<R>expected{R(1,2),R(0),R(0),R(1,2),R(0),R(1,2),R(1,2),R(0)};
 require(a.v==expected&&result.parity&&result.gp,"AND-only rational escape control failed");++s.calibrations;
 require(!identities(transform(pin<R>(0),{positive})).parity,"load-bearing pin countercontrol missed");++s.calibrations;
 require(identities(transform(pin<R>(1),{positive})).parity,"CONST1 rational calibration failed");++s.calibrations;
 const Matrix<F2>reduction{{{F2(1),F2(2)},{F2(1),F2(0)}}};require(det(reduction)==F2(0),"rational positive control must be singular on reduction");++s.calibrations;
 Tensor<R>eq{2,{R(1),R(0),R(0),R(1)}};auto e=identities(eq);require(e.parity&&e.gp,"equality matchgate calibration failed");++s.calibrations;
 Tensor<R>pf{4,std::vector<R>(16)};pf.v[0]=1;pf.v[3]=1;pf.v[5]=2;pf.v[9]=3;pf.v[6]=4;pf.v[10]=5;pf.v[12]=6;pf.v[15]=8;
 const auto p=identities(pf);require(p.parity&&p.gp,"four-leg Pfaffian calibration failed");++s.calibrations;
 pf.v[15]=9;require(!identities(pf).gp,"Pfaffian defect mutation not detected");++s.calibrations;
 const Tensor<F2>xor_gate{3,{F2(1),F2(0),F2(0),F2(1),F2(0),F2(1),F2(1),F2(0)}};
 require(identities(xor_gate).parity&&invariant_B(xor_gate)==F2(0),"XOR proves-too-much control failed");++s.calibrations;
 require(invariant_B(and_tensor<F2>())==F2(1),"AND invariant calibration failed");++s.calibrations;
 const auto whole=and_tensor<F2>();Tensor<F2>even=whole,odd=whole;
 for(unsigned i=0;i<8;++i){if((std::popcount(i)&1)==0)odd.v[i]=F2(0);else even.v[i]=F2(0);require(even.v[i]+odd.v[i]==whole.v[i],"two-signature sum changed AND");}
 require(identities(even).parity&&identities(even).gp&&identities(odd).parity&&identities(odd).gp,"two-parity sum countercontrol failed");++s.calibrations;
 require(E(2)*E(2)==E(0)&&E(3)*E(3)==E(1),"square-zero arithmetic failed");++s.calibrations;
 R wrong(0);for(unsigned j=0;j<2;++j)wrong=wrong+positive[j][0]*positive[j][0];require(wrong!=R(1),"wrong inverse-transpose orientation trap failed");++s.calibrations;
 (void)symbolic_identity();++s.calibrations;
}

Stats audit(std::ostream* output){
 Stats s;calibrate(s);const auto qs=rational_grammar();const auto fs=binary_grammar();const auto es=ring_grammar();
 for(const auto&m:qs){++s.q;s.wire+=wire_checks(m);const auto a=uniform_and(m),p0=transform(pin<R>(0),{m}),p1=transform(pin<R>(1),{m});
  const auto ca=identities(a),c0=identities(p0),c1=identities(p1);s.gp+=ca.checks+c0.checks+c1.checks;
  const bool and_ok=ca.parity&&ca.gp,pins=c0.parity&&c1.parity,joint=pins&&and_ok;
  if(and_ok)++s.q_and;
  if(pins)++s.q_pins;
  if(joint)++s.q_joint;
  const bool mono=monomial(m);require(pins==mono,"pin/monomial equivalence failed on finite grammar");require(!joint,"common pin-and-AND obstruction contradicted");
  bool old=true;for(const auto&row:m)for(const auto&v:row)if(v.n<-1||v.n>1)old=false;if(old){++s.old;if(and_ok)++s.old_and;}
  if(output){auto&o=*output;record_prefix(o,"per_basis");o<<",\"field\":\"Q\",\"matrix\":";integer_matrix_json(o,m);o<<",\"determinant\":";scalar_json(o,det(m));
   o<<",\"pin0_parity\":"<<(c0.parity?"true":"false")<<",\"pin1_parity\":"<<(c1.parity?"true":"false")<<",\"basis_monomial\":"<<(mono?"true":"false")<<",\"and_parity\":"<<(ca.parity?"true":"false")<<",\"and_matchgate_identities\":"<<(ca.gp?"true":"false")<<",\"joint_candidate_passed\":false,\"first_mixed_tensor\":\""<<first_mixed(c0,c1,ca)<<"\",\"pin0_coefficients\":";vector_json(o,p0.v);o<<",\"pin1_coefficients\":";vector_json(o,p1.v);o<<",\"and_coefficients\":";vector_json(o,a.v);o<<"}\n";}
 }
 require(s.old==48&&s.old_and==0,"original finite grammar regression changed");require(s.q_and>0,"expanded grammar failed to contain known rational escape");
 for(const auto&m:fs){++s.f2;s.wire+=wire_checks(m);const auto a=uniform_and(m);const auto result=identities(a);if(result.parity)++s.f2_and;require(invariant_B(a)==F2(1)&&!result.parity,"uniform F2 obstruction regression failed");
  if(output){auto&o=*output;record_prefix(o,"per_basis");o<<",\"field\":\"F2\",\"matrix\":";matrix_json(o,m);o<<",\"and_parity\":false,\"invariant_B\":1,\"and_coefficients\":";vector_json(o,a.v);o<<"}\n";}
 }
 for(const auto&a:fs)for(const auto&b:fs)for(const auto&c:fs){++s.independent;const auto t=transform(and_tensor<F2>(),{a,b,c});const auto value=invariant_B(t);require(value==det(a)*det(b)*det(c),"independent-leg F2 covariance failed");if(identities(t).parity)++s.independent_pure;require(!identities(t).parity&&value==F2(1),"independent-leg F2 obstruction regression failed");}
 for(const auto&m:es){++s.ring;s.wire+=wire_checks(m);const auto t=uniform_and(m);if(identities(t).parity)++s.ring_pure;require((invariant_B(t).v&1U)!=0&&!identities(t).parity,"square-zero ring obstruction regression failed");}
 require(s.f2==6&&s.f2_and==0&&s.independent==216&&s.independent_pure==0&&s.ring==96&&s.ring_pure==0,"finite domain coverage failed");
 if(output){auto&o=*output;const auto symbolic=symbolic_identity();record_prefix(o,"symbolic_identity_certificate");
  o<<",\"ambient_ring\":\"F2[f0,...,f7,A00,...,C11] with ordinary exponents\",\"variables\":20,\"variable_order\":[\"f000\",\"f100\",\"f010\",\"f110\",\"f001\",\"f101\",\"f011\",\"f111\",\"A00\",\"A01\",\"A10\",\"A11\",\"B00\",\"B01\",\"B10\",\"B11\",\"C00\",\"C01\",\"C10\",\"C11\"],\"monomial_encoding\":\"sorted variable indices with repetitions, coefficient1\",\"monomial_order\":\"lexicographic full20-entry exponent vectors\",\"degree_per_monomial\":8,\"lhs_monomials\":";monomials_json(o,symbolic.lhs);o<<",\"rhs_monomials\":";monomials_json(o,symbolic.rhs);o<<",\"residual_monomials\":[],\"boolean_exponent_reduction\":false,\"proof_assistant_checked\":false}\n";
  record_prefix(o,"summary");o<<",\"grammar_entry_bound\":2,\"rational_matrices_pre_filter\":625,\"rational_invertible_matrices\":"<<s.q<<",\"rational_and_only_survivors\":"<<s.q_and<<",\"rational_both_pin_survivors\":"<<s.q_pins<<",\"rational_common_pin_and_survivors\":"<<s.q_joint<<",\"old_invertible_matrices\":"<<s.old<<",\"old_and_only_survivors\":"<<s.old_and<<",\"positive_Q_basis\":[[1,2],[1,0]],\"positive_Q_and_coefficients\":[[1,2],[0,1],[0,1],[1,2],[0,1],[1,2],[1,2],[0,1]],\"positive_Q_basis_reduction_singular\":true,\"gf2_matrices_pre_filter\":16,\"gf2_invertible_matrices\":"<<s.f2<<",\"gf2_and_parity_survivors\":"<<s.f2_and<<",\"independent_gf2_triples\":"<<s.independent<<",\"independent_gf2_parity_survivors\":"<<s.independent_pure<<",\"square_zero_single_tag_invertible_matrices\":"<<s.ring<<",\"square_zero_single_tag_parity_survivors\":"<<s.ring_pure<<",\"and_two_parity_sum_control\":true,\"rational_gp_checks\":"<<s.gp<<",\"wire_contraction_checks\":"<<s.wire<<",\"calibration_checks\":"<<s.calibrations<<",\"symbolic_variables\":20,\"symbolic_lhs_terms\":32,\"symbolic_rhs_terms\":32,\"symbolic_residual_terms\":0,\"symbolic_boolean_exponent_reduction\":false,\"global_planar_construction\":false,\"new_solver_claim\":false,\"novelty_claim\":false,\"scope_limit\":\"fixed local AND tensor and declared invertible local gauges; block regrouping, sums or alternate encodings untested\"}\n";
 }
 return s;
}
}

int main(int argc,char**argv){
 try{
  if(argc==2&&std::string(argv[1])=="--self-test"){
   const auto s=audit::audit(nullptr);std::cout<<"{\"status\":\"pass\",\"scope\":\"development_only\",\"q_invertible\":"<<s.q<<",\"q_and_only_survivors\":"<<s.q_and<<",\"q_pins_and_survivors\":"<<s.q_joint<<",\"f2_uniform\":"<<s.f2<<",\"f2_independent\":"<<s.independent<<",\"single_tag_uniform\":"<<s.ring<<",\"symbolic_identity_terms\":32,\"symbolic_residual_terms\":0,\"calibrations\":"<<s.calibrations<<"}\n";return 0;
  }
  if(argc==4&&std::string(argv[1])=="--run"){
   std::ifstream fixtures(argv[2]);audit::require(bool(fixtures)&&fixtures.peek()!=std::ifstream::traits_type::eof(),"fixture manifest missing/empty (global audit is curve independent)");
   std::ifstream prior(argv[3]);audit::require(!prior.good(),"refuse output overwrite");std::ofstream out(argv[3]);audit::require(bool(out),"cannot create output");(void)audit::audit(&out);audit::require(bool(out),"output write failed");return 0;
  }
  std::cerr<<"usage: basis_audit --self-test | --run FIXTURES_TSV FRESH_OUTPUT_JSONL\n";return 2;
 }catch(const std::exception&e){std::cerr<<"basis audit refused: "<<e.what()<<'\n';return 1;}
}
