// Newly written arithmetic adapters, not Atkin's missing ZL library.
#include <gmpxx.h>
#include <string>
#include <vector>
#include <sstream>
#include <stdexcept>
static unsigned radix_bits=26;
static unsigned long long operations=0;
static std::vector<std::string> divisions;
static int zero_divisions=0;
extern "C" {
extern struct {int safe;} zlsafe_;
extern struct {int nprint;} print_;
typedef void (*callback)(int*,int*,int*,int*,int*,int*,int*,int*,int*,int*);
static callback roots_callback=nullptr,check_callback=nullptr;
void setup_(int *bits,callback roots,callback check) {
  radix_bits=*bits; roots_callback=roots;check_callback=check;
  zlsafe_.safe=1;print_.nprint=0;operations=0;divisions.clear();zero_divisions=0;
}
}
static mpz_class readz(const int *a) {
  if(a[0]<1 || a[0]>24) throw std::runtime_error("adapter length outside 1..24");
  mpz_class v=0;
  for(int i=1;i<=a[0];++i){v<<=radix_bits;v+=static_cast<unsigned>(a[i]);}
  return v;
}
static void writez(int *a,const mpz_class &v) {
  if(v<0) throw std::runtime_error("negative adapter output");
  unsigned n=mpz_sizeinbase(v.get_mpz_t(),2);n=(n+radix_bits-1)/radix_bits;
  if(n>24)throw std::runtime_error("adapter output longer than 24 digits");
  a[0]=n;mpz_class t=v,mask=(mpz_class(1)<<radix_bits)-1;
  for(unsigned i=n;i>=1;--i){mpz_class r=t&mask;a[i]=r.get_ui();t>>=radix_bits;}
}
extern "C" {
void zlmmul_(int*a,int*b,int*c,int*p){mpz_class x=readz(a),y=readz(b),q=readz(p);writez(c,(x*y)%q);++operations;}
void zlmadd_(int*a,int*b,int*c,int*p){mpz_class x=readz(a),y=readz(b),q=readz(p);writez(c,(x+y)%q);++operations;}
void zlmsub_(int*a,int*b,int*c,int*p){mpz_class x=readz(a),y=readz(b),q=readz(p),r=(x-y)%q;if(r<0)r+=q;writez(c,r);++operations;}
void zlmmsb_(int*a,int*b,int*c,int*d,int*p){mpz_class x=readz(a),y=readz(b),z=readz(c),q=readz(p),r=(x-y*z)%q;if(r<0)r+=q;writez(d,r);++operations;}
void zlmmad_(int*a,int*b,int*c,int*d,int*p){mpz_class x=readz(a),y=readz(b),z=readz(c),q=readz(p);writez(d,(x+y*z)%q);++operations;}
void zlmsqu_(int*a,int*b,int*p){mpz_class x=readz(a),q=readz(p);writez(b,(x*x)%q);++operations;}
void zldif_(int*a,int*b,int*c){mpz_class x=readz(a),y=readz(b);writez(c,x-y);++operations;}
void zlmdiv_(int*a,int*b,int*c,int*p){
  mpz_class x=readz(a),y=readz(b),q=readz(p),inv,r=0;
  if(mpz_invert(inv.get_mpz_t(),y.get_mpz_t(),q.get_mpz_t()))r=x*inv%q;
  else ++zero_divisions;
  divisions.push_back("["+x.get_str()+","+y.get_str()+","+r.get_str()+"]");
  writez(c,r);++operations;
}
int zlmax_(int*a,int*b){mpz_class x=readz(a),y=readz(b);return cmp(x,y);}
void blvnoc_(int*a,int*b,int*,int*p){
  mpz_class x=0;for(int i=0;i<p[0];++i){x<<=radix_bits;x+=static_cast<unsigned>(a[i]);}writez(b,x);
}
void getjqn_(int*r,int*d,int*a,int*j,int*q,int*p,int*v,int*c){roots_callback(r,d,a,j,q,p,v,c,nullptr,nullptr);}
void charla_(int*s,int*a,int*b,int*aq,int*bq,int*k,int*q,int*p,int*f){check_callback(s,a,b,aq,bq,k,q,p,f,nullptr);}
const char *snapshot_(){static std::string s;std::ostringstream out;out<<"{\"operations\":"<<operations<<",\"zero_divisions\":"<<zero_divisions<<",\"divisions\":[";for(size_t i=0;i<divisions.size();++i){if(i)out<<",";out<<divisions[i];}out<<"]}";s=out.str();return s.c_str();}
}
