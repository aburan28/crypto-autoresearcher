// Read-only observer. The access-only header exposes fields without changing layout.
#include "LiDIA/eco_prime.h"
#include "LiDIA/galois_field.h"
#include "LiDIA/gf_element.h"
#include "LiDIA/random_generator.h"
#include <iostream>
#include <vector>
#include <algorithm>
#include <cstdlib>
#ifdef LIDIA_NAMESPACE
using namespace LiDIA;
#endif
void emit_poly(const char *name,const Fp_polynomial &f) {
 std::cout << "AUDIT POLY " << name << " " << f.degree();
 for(long i=0;i<=f.degree();++i)std::cout << " " << f[i];
 std::cout << std::endl;
}
void relation(const eco_prime &q) {
 const base_vector<udigit> &v=q.get_relation();
 std::cout << "AUDIT REL " << v.get_size();
 for(long i=0;i<v.get_size();++i)std::cout << " " << v[i];
 std::cout << std::endl;
}
int main(int argc,char **argv) {
 if(argc!=2)return 64;
 try {
  const unsigned long ell=std::strtoul(argv[1],0,10);
  if(ell!=3 && ell!=5 && ell!=13)return 64;
  random_generator::seed(1);bigint::seed(bigint(1));
  bigint p;std::cin>>p;bigmod::set_modulus(p);galois_field field(p);
  gf_element a(field),b(field);std::cin>>a>>b;
  eco_prime q(a,b);q.set_info_mode(0);q.set_strategy(eco_prime::DONT_COMPUTE_SP_DEGREE);
  if(!q.set_prime(ell)) {std::cout<<"AUDIT TABLE_UNAVAILABLE"<<std::endl;return 2;}
  Fp_polynomial full;full.set_modulus(p);q.build_poly_in_X(full,q.jinv);
  emit_poly("modular",full);
  base_vector<bigint> found=find_roots(full);std::vector<bigint> roots;
  for(long i=0;i<found.get_size();++i)roots.push_back(found[i]);
  std::sort(roots.begin(),roots.end());
  q.compute_splitting_type();
  std::cout<<"AUDIT SPLIT "<<ell<<" "<<q.is_elkies()<<" "<<roots.size()<<" "<<q.trans_type()<<std::endl;
  if(roots.empty()) {
   q.compute_trace_atkin();relation(q);
   std::cout<<"AUDIT ATKIN_COMPLETE"<<std::endl;
  }
  for(std::size_t r=0;r<roots.size();++r) {
   for(int profile=0;profile<2;++profile) {
    std::cout<<"AUDIT ROOT_BEGIN "<<r<<" "<<profile<<" "<<roots[r]<<std::endl;
    eco_prime v(a,b);v.set_info_mode(0);v.set_strategy(eco_prime::DONT_COMPUTE_SP_DEGREE);
    v.set_ev_search_strategy(eco_prime::EV_DIVISION_POLYNOMIAL | (profile ? eco_prime::TEST_X_COORDINATE : eco_prime::TEST_Y_COORDINATE));
    if(!v.set_prime(ell))return 2;v.compute_splitting_type();v.ftau[0]=roots[r];
    Fp_polynomial kernel,remainder;bigmod qa,qb;Fp_poly_modulus mod;
    v.compute_divisor_of_division_polynomial(kernel,qa,qb);
    emit_poly("kernel",kernel);std::cout<<"AUDIT QUOTIENT "<<qa.mantissa()<<" "<<qb.mantissa()<<std::endl;
    mod.build(kernel);v.compute_psi(remainder,ell,mod);
    std::cout<<"AUDIT DIVISION_ZERO "<<remainder.is_zero()<<std::endl;
    v.compute_trace_elkies();relation(v);
    std::cout<<"AUDIT ROOT_COMPLETE "<<r<<" "<<profile<<std::endl;
   }
  }
  std::cout<<"AUDIT COMPLETE"<<std::endl;return 0;
 } catch(basic_error const &e) {
  std::cout<<"AUDIT SOURCE_ERROR"<<std::endl;e.traditional_error_handler();return 2;
 } catch(...) {std::cout<<"AUDIT UNKNOWN_ERROR"<<std::endl;return 3;}
}
