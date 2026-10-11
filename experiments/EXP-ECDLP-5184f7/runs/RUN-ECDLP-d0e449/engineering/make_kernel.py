"""Mechanical big-integer extension of the retained public synthetic kernel."""
from pathlib import Path
import hashlib
repo=Path('/workspace/solinas-run')
ext=repo/'experiments/EXP-ECDLP-5184f7/extensions/nist-fullsize-20261011'
out=ext/'implementation'
out.mkdir(parents=True,exist_ok=True)
original=repo/'experiments/EXP-ECDLP-5184f7/implementation/attack.cpp'
s=original.read_text()
replacements=[
('#include <algorithm>','#include <boost/multiprecision/cpp_int.hpp>\n#include <algorithm>'),
('using U = uint64_t;','using U = uint64_t;\nusing Big = boost::multiprecision::cpp_int;\nBig mod(Big a,const Big& p){a%=p;if(a<0)a+=p;return a;}'),
('U inverse(U a, U p) {\n    Signed t=0, n=1; U r=p, s=a;\n    while(s) {U q=r/s, z=r-q*s; r=s; s=z; Signed v=t-Signed(q)*n; t=n; n=v;}','Big inverse(Big a, Big p) {\n    Big t=0, n=1, r=p, s=a;\n    while(s!=0) {Big q=r/s, z=r-q*s; r=s; s=z; Big v=t-q*n; t=n; n=v;}'),
('return U(t);','return t;'),
('U x=0,y=0; bool infinity','Big x=0,y=0; bool infinity'),
('U p,A,B; bool opaque; U ux=1,uy=1; int width;','Big p,A,B; bool opaque; Big ux=1,uy=1; int width;'),
('U product(U a,U b){++counts[phase_].muls;return Wide(a)*b%p;}','Big product(const Big& a,const Big& b){++counts[phase_].muls;return a*b%p;}'),
('U inv(U a)','Big inv(Big a)'),
('Value wrap(U x,U y','Value wrap(Big x,Big y'),
('if(v.infinity)return {0};U x=v.x,y=v.y;','if(v.infinity)return {0};Big x=v.x,y=v.y;'),
('x=Wide(x)*ux%p;y=Wide(y)*uy%p;','x=x*ux%p;y=y*uy%p;'),
('data[0]=2+(y&1);','data[0]=2+(y&1).convert_to<unsigned>();'),
('data[width-i]=(x>>(8*i))&255;','data[width-i]=((x>>(8*i))&255).convert_to<unsigned>();'),
('Group(U pp,U aa,U bb,bool oracle,U u)','Group(Big pp,Big aa,Big bb,bool oracle,Big u)'),
('if(p> (U(1)<<40))throw std::runtime_error("attack field exceeds frozen toy boundary");','if(p < 3 || p >= (Big(1)<<232))throw std::runtime_error("attack field exceeds full-size boundary");'),
('width=(64-__builtin_clzll(p)+7)/8;','width=(boost::multiprecision::msb(p)+8)/8;'),
('if(u!=1){U invu=inverse(u,p);ux=Wide(invu)*invu%p;uy=Wide(ux)*invu%p;}','if(u!=1){Big invu=inverse(u,p);ux=invu*invu%p;uy=ux*invu%p;}'),
('Value point(U x,U y){if((Wide(y)*y%p)!=(Wide(x)*x%p*x%p+Wide(A)*x+B)%p)','Value point(Big x,Big y){if((y*y%p)!=(x*x%p*x%p+A*x+B)%p)'),
('return v.infinity?v:wrap(v.x,v.y? p-v.y:0);','return v.infinity?v:wrap(v.x,v.y!=0?Big(p-v.y):Big(0));'),
('U numerator,denominator;','Big numerator,denominator;'),
('U slope=product(numerator,inv(denominator));U x=','Big slope=product(numerator,inv(denominator));Big x='),
('U y=(product(slope,(a.x+p-x)%p)+p-a.y)%p;','Big y=(product(slope,(a.x+p-x)%p)+p-a.y)%p;'),
('Value zero(){return wrap(0,0,true);}', 'Value zero(){return wrap(0,0,true);}\n    size_t limbbytes(const Value&v)const{size_t a=v.x.backend().capacity(),b=v.y.backend().capacity();return ((a>2?a:0)+(b>2?b:0))*sizeof(boost::multiprecision::limb_type);}'),
('Value mul(Value v,U n)','Value mul(Value v,Big n)'),
('if(n&1)out=add(out,v);','if((n&1)!=0)out=add(out,v);'),
('U z=v.x^(v.y+0x9e3779b97f4a7c15ULL);','U z=(v.x&Big(UINT64_MAX)).convert_to<U>()^((v.y+0x9e3779b97f4a7c15ULL)&Big(UINT64_MAX)).convert_to<U>();'),
('struct State {Value value;U a,b;};','struct State {Value value;Big a,b;};'),
('struct Collision {U calls,a,b,aa,bb,denom;long long q;','struct Collision {U calls;Big a,b,aa,bb,denom,q;'),
('struct Result {long long q=-1;','struct Result {Big q=-1;'),
('U uniform(std::mt19937_64&r,U n){U limit=UINT64_MAX-UINT64_MAX%n;U x;do{x=r();}while(x>=limit);return x%n;}','Big uniform(std::mt19937_64&r,const Big& n){\n if(n<=UINT64_MAX){U small=n.convert_to<U>(),limit=UINT64_MAX-UINT64_MAX%small,x;do{x=r();}while(x>=limit);return x%small;}\n unsigned bits=boost::multiprecision::msb(n)+1,words=(bits+63)/64;Big x,mask=(Big(1)<<bits)-1;do{x=0;for(unsigned i=0;i<words;++i){x<<=64;x+=r();}x&=mask;}while(x>=n);return x;\n}'),
('unsigned char coefficients[16];for(int i=0;i<8;++i){coefficients[7-i]=(s.a>>(8*i))&255;coefficients[15-i]=(s.b>>(8*i))&255;}SHA256_Update(&ctx,coefficients,16);','unsigned width=8;if(s.a>UINT64_MAX||s.b>UINT64_MAX)width=32;std::vector<unsigned char> coefficients(width*2);for(unsigned i=0;i<width;++i){coefficients[width-1-i]=((s.a>>(8*i))&255).convert_to<unsigned>();coefficients[2*width-1-i]=((s.b>>(8*i))&255).convert_to<unsigned>();}SHA256_Update(&ctx,coefficients.data(),coefficients.size());'),
('Result rho(Group&g,Value G,Value Q,U ell,U seed,U adding)','Result rho(Group&g,Value G,Value Q,Big ell,U seed,U adding)'),
('U a=uniform(random,ell),b=uniform(random,ell);','Big a=uniform(random,ell),b=uniform(random,ell);'),
('U denominator=(hare.b+ell-tortoise.b)%ell;long long q=-1;','Big denominator=(hare.b+ell-tortoise.b)%ell,q=-1;'),
('q=Wide((tortoise.a+ell-hare.a)%ell)*inverse(denominator,ell)%ell;','q=((tortoise.a+ell-hare.a)%ell)*inverse(denominator,ell)%ell;'),
('g.mul(G,U(q))','g.mul(G,q)'),
('Result bsgs(Group&g,Value G,Value Q,U ell){','Result bsgs(Group&g,Value G,Value Q,Big order){\n    if(order>(Big(1)<<26))throw std::runtime_error("BSGS exceeds kernel instrumentation boundary");U ell=order.convert_to<U>();'),
('U adding,seed,p,A,B,ell,h,gx,gy,qx,qy,u;','U adding,seed,cap;Big p,A,B,ell,h,gx,gy,qx,qy,u;'),
('>>qx>>qy>>u))','>>qx>>qy>>u>>cap))'),
('group.cap=isqrt(400*ell)+1;Result result;','group.cap=cap;Result result;'),
('Wide(group.counts[1].calls)*group.counts[1].calls>Wide(400)*ell','Big(group.counts[1].calls)*group.counts[1].calls>Big(400)*ell'),
('result.table_bytes=Allocation::bytes+sizeof(table);', 'result.table_bytes=Allocation::bytes+sizeof(table);for(const auto& kv:table)result.table_bytes+=g.limbbytes(kv.first);'),
('usage: attack public-jobs.txt','usage: attack public-jobs-with-explicit-cap.txt')]
for old,new in replacements:
    if old not in s: raise RuntimeError('missing source replacement: '+old)
    s=s.replace(old,new)
(out/'attack.cpp').write_text(s)
(ext/'kernel-origin.json').write_text(__import__('json').dumps({'source':'../../implementation/attack.cpp','sha256':hashlib.sha256(original.read_bytes()).hexdigest(),'transformation':'make_kernel.py; fixed public job format adds explicit cap, coordinates and scalar coefficients support up to 232-bit fields; algorithms, counters and control encodings retained'},indent=2)+'\n')
