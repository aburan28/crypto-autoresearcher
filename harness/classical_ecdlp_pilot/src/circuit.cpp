#include "common.hpp"
#include <algorithm>
#include <array>
#include <bit>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <limits>
#include <map>
#include <numeric>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

// Classical exact bit programs and a finite, exact matchgate grammar.  No new
// cancellation identity or global planar/Pfaffian construction is assumed.
namespace diagnostic {
using lab::I;
using W = std::uint32_t;
using Word = std::vector<W>;
enum class Op { constant, input, land, lxor, lnot };
struct Gate { Op op; W a=0,b=0; };
struct Circuit {
    std::vector<Gate> g{{Op::constant,0,0},{Op::constant,1,0}};
    W inputs=0;
    W push(Op op,W a,W b=0) {
        lab::require(g.size()<std::numeric_limits<W>::max(),"circuit too large");
        if(op!=Op::input && op!=Op::constant)
            lab::require(a<g.size() && (op==Op::lnot || b<g.size()),"non-topological gate");
        g.push_back({op,a,b});return static_cast<W>(g.size()-1);
    }
    W input(){return push(Op::input,inputs++);}
    W land(W a,W b){if(a==0||b==0)return 0;if(a==1)return b;if(b==1||a==b)return a;return push(Op::land,a,b);}
    W lxor(W a,W b){if(a==b)return 0;if(a==0)return b;if(b==0)return a;if(a==1)return lnot(b);if(b==1)return lnot(a);return push(Op::lxor,a,b);}
    W lnot(W a){if(a<2)return a^1U;return push(Op::lnot,a);}
    W lor(W a,W b){return lxor(lxor(a,b),land(a,b));}
    W mux(W s,W no,W yes){if(no==yes)return no;if(s<2)return s==0?no:yes;return lxor(no,land(s,lxor(no,yes)));}
    Word input_word(unsigned n){Word a;for(unsigned i=0;i<n;++i)a.push_back(input());return a;}
    Word constant(std::uint64_t x,unsigned n){Word a;for(unsigned i=0;i<n;++i)a.push_back(static_cast<W>((x>>i)&1U));return a;}
    Word select(W s,const Word& a,const Word& b){lab::require(a.size()==b.size(),"mux width");Word z;for(std::size_t i=0;i<a.size();++i)z.push_back(mux(s,a[i],b[i]));return z;}
    Word add_raw(const Word& a,const Word& b,unsigned n){
        Word z;W carry=0;
        for(unsigned i=0;i<n;++i){const W x=i<a.size()?a[i]:0,y=i<b.size()?b[i]:0,t=lxor(x,y);z.push_back(lxor(t,carry));carry=lor(land(x,y),land(t,carry));}
        return z;
    }
    std::pair<Word,W> sub_raw(const Word& a,const Word& b,unsigned n){
        Word z;W borrow=0;
        for(unsigned i=0;i<n;++i){const W x=i<a.size()?a[i]:0,y=i<b.size()?b[i]:0,t=lxor(x,y);z.push_back(lxor(t,borrow));borrow=lor(land(lnot(x),y),land(lnot(t),borrow));}
        return {z,borrow};
    }
    W eq(const Word&a,const Word&b){lab::require(a.size()==b.size(),"eq width");W out=1;for(std::size_t i=0;i<a.size();++i)out=land(out,lnot(lxor(a[i],b[i])));return out;}
    void eval(std::vector<unsigned char>&v,const std::vector<unsigned char>&in,std::size_t begin=0,std::size_t end=0)const{
        if(end==0)end=g.size();
        if(v.size()!=g.size())v.resize(g.size());
        for(std::size_t i=begin;i<end;++i){const auto&a=g[i];switch(a.op){
          case Op::constant:v[i]=static_cast<unsigned char>(a.a);break;
          case Op::input:lab::require(a.a<in.size(),"input vector short");v[i]=in[a.a];break;
          case Op::land:v[i]=static_cast<unsigned char>(v[a.a]&v[a.b]);break;
          case Op::lxor:v[i]=static_cast<unsigned char>(v[a.a]^v[a.b]);break;
          case Op::lnot:v[i]=static_cast<unsigned char>(v[a.a]^1U);break;
        }}
    }
    bool witness(const std::vector<unsigned char>&v,const std::vector<unsigned char>&in)const{
        if(v.size()!=g.size())return false;
        for(std::size_t i=0;i<g.size();++i){const auto&a=g[i];unsigned char want=0;switch(a.op){
          case Op::constant:want=static_cast<unsigned char>(a.a);break;
          case Op::input:if(a.a>=in.size())return false;want=in[a.a];break;
          case Op::land:want=static_cast<unsigned char>(v[a.a]&v[a.b]);break;
          case Op::lxor:want=static_cast<unsigned char>(v[a.a]^v[a.b]);break;
          case Op::lnot:want=static_cast<unsigned char>(v[a.a]^1U);break;
        }if(v[i]>1||v[i]!=want)return false;}return true;
    }
    std::uint64_t cnf_clauses()const{std::uint64_t n=0;for(auto a:g)switch(a.op){case Op::constant:++n;break;case Op::input:break;case Op::land:n+=3;break;case Op::lxor:n+=4;break;case Op::lnot:n+=2;break;}return n;}
};
std::uint64_t decode(const Word&w,const std::vector<unsigned char>&v){std::uint64_t z=0;for(std::size_t j=0;j<w.size();++j)z|=static_cast<std::uint64_t>(v[w[j]])<<j;return z;}
void set_word(std::vector<unsigned char>&in,std::size_t first,std::uint64_t x,unsigned n){for(unsigned j=0;j<n;++j)in[first+j]=static_cast<unsigned char>((x>>j)&1U);}

struct BPoint{Word x,y;W inf;};
struct Arithmetic{
    Circuit& c; I p,a,b;unsigned n;
    Arithmetic(Circuit& circ,const lab::Curve&curve):c(circ),p(curve.p),a(curve.a),b(curve.b),n(lab::bits(static_cast<std::uint64_t>(p-1))){}
    Word k(I v){return c.constant(static_cast<std::uint64_t>(v),n);}
    Word add(const Word&x,const Word&y){auto sum=c.add_raw(x,y,n+1);auto [diff,borrow]=c.sub_raw(sum,c.constant(static_cast<std::uint64_t>(p),n+1),n+1);auto z=c.select(borrow,diff,sum);z.resize(n);return z;}
    Word sub(const Word&x,const Word&y){auto [d,borrow]=c.sub_raw(x,y,n);auto corrected=c.add_raw(d,k(p),n);return c.select(borrow,d,corrected);}
    Word mul(const Word&x,const Word&y){Word z=k(0),v=x;for(unsigned j=0;j<n;++j){z=c.select(y[j],z,add(z,v));if(j+1<n)v=add(v,v);}return z;}
    Word power(Word v,I e){Word z=k(1);for(;e!=0;e>>=1){if((e&1)!=0)z=mul(z,v);if(e>1)v=mul(v,v);}return z;}
    Word inverse(const Word&x){return power(x,p-2);} // zero maps to zero; callers mask singular branches.
    BPoint zero(){return {k(0),k(0),1};}
    BPoint point(lab::Point q){return q.inf?zero():BPoint{k(q.x),k(q.y),0};}
    BPoint select(W s,const BPoint&no,const BPoint&yes){return {c.select(s,no.x,yes.x),c.select(s,no.y,yes.y),c.mux(s,no.inf,yes.inf)};}
    W valid(const BPoint&q){
        const W xr=c.sub_raw(q.x,k(p),n).second,yr=c.sub_raw(q.y,k(p),n).second;
        const W finite=c.land(c.land(xr,yr),c.eq(mul(q.y,q.y),add(add(mul(mul(q.x,q.x),q.x),mul(k(a),q.x)),k(b))));
        const W canonical_inf=c.land(c.eq(q.x,k(0)),c.eq(q.y,k(0)));
        return c.mux(q.inf,finite,canonical_inf);
    }
    BPoint dbl(const BPoint&q){
        const auto xx=mul(q.x,q.x),num=add(add(xx,xx),add(xx,k(a))),den=add(q.y,q.y);
        const auto slope=mul(num,inverse(den));const auto x=sub(sub(mul(slope,slope),q.x),q.x);
        const auto y=sub(mul(slope,sub(q.x,x)),q.y);
        const W bad=c.lor(q.inf,c.eq(q.y,k(0)));return select(bad,{x,y,0},zero());
    }
    BPoint add_point(const BPoint&q,const BPoint&s){
        const W same_x=c.eq(q.x,s.x),opposite=c.land(same_x,c.eq(add(q.y,s.y),k(0)));
        const auto general=mul(sub(s.y,q.y),inverse(sub(s.x,q.x)));
        const auto xx=mul(q.x,q.x),double_slope=mul(add(add(xx,xx),add(xx,k(a))),inverse(add(q.y,q.y)));
        const auto slope=c.select(same_x,general,double_slope),x=sub(sub(mul(slope,slope),q.x),s.x),y=sub(mul(slope,sub(q.x,x)),q.y);
        BPoint z=select(opposite,{x,y,0},zero());z=select(s.inf,z,q);return select(q.inf,z,s);
    }
    BPoint window(BPoint q,const Word&w){for(std::size_t j=w.size();j!=0;--j){q=dbl(q);q=add_point(q,select(w[j-1],zero(),base));}return q;}
    BPoint base;
};
lab::Point decode_point(const BPoint&q,const std::vector<unsigned char>&v){return {static_cast<I>(decode(q.x,v)),static_cast<I>(decode(q.y,v)),v[q.inf]!=0};}
void point_input(std::vector<unsigned char>&in,std::size_t first,lab::Point q,unsigned n){set_word(in,first,static_cast<std::uint64_t>(q.x),n);set_word(in,first+n,static_cast<std::uint64_t>(q.y),n);in[first+2*n]=static_cast<unsigned char>(q.inf);}

struct DCounts{std::uint64_t scalar_cases=0,target_cases=0,malformed_cases=0,boundary_cases=0,gate_evaluations=0,mutation_cases=0,tag_only_cells=0,nonzero_boundary_cells=0;};
void test_arithmetic(){
    const lab::Curve curve{17,2,2};Circuit c;Arithmetic a(c,curve);auto x=c.input_word(a.n),y=c.input_word(a.n);
    auto sum=a.add(x,y),diff=a.sub(x,y),prod=a.mul(x,y),inv=a.inverse(x);std::vector<unsigned char>v,in(c.inputs);
    for(I u=0;u<17;++u)for(I z=0;z<17;++z){set_word(in,0,static_cast<std::uint64_t>(u),a.n);set_word(in,a.n,static_cast<std::uint64_t>(z),a.n);c.eval(v,in);
        lab::require(static_cast<I>(decode(sum,v))==curve.mod(u+z),"gate addition");lab::require(static_cast<I>(decode(diff,v))==curve.mod(u-z),"gate subtraction");lab::require(static_cast<I>(decode(prod,v))==curve.mod(u*z),"gate multiplication");lab::require(static_cast<I>(decode(inv,v))==(u==0?0:curve.inv(u)),"gate inversion");}
}

void direct_row(const lab::Fixture&f,std::ostream&out){
    lab::certify(f);const unsigned ell=lab::bits(static_cast<std::uint64_t>(f.r-1));
    Circuit c;Arithmetic a(c,f.c);a.base=a.point(f.P);Word scalar=c.input_word(ell);auto value=a.window(a.zero(),scalar);
    const W canonical=c.sub_raw(scalar,c.constant(static_cast<std::uint64_t>(f.r),ell),ell).second;
    const std::size_t cut=c.g.size(),qfirst=c.inputs;BPoint target{c.input_word(a.n),c.input_word(a.n),c.input()};
    const W accepts=c.land(canonical,c.land(c.land(c.eq(value.x,target.x),c.eq(value.y,target.y)),c.lnot(c.lxor(value.inf,target.inf))));
    const auto pts=f.c.points();std::vector<unsigned char>v,in(c.inputs);DCounts counts;
    std::vector<lab::Point> malformed{{1,0,true},{f.c.p,0,false},{0,f.c.p,false}};
    bool found_bad=false;
    for(I x=0;x<f.c.p&&!found_bad;++x)for(I y=0;y<f.c.p&&!found_bad;++y)
        if(!f.c.valid({x,y,false})){malformed.push_back({x,y,false});found_bad=true;}
    lab::require(found_bad,"off-curve negative control absent");
    std::vector<unsigned> parity(pts.size());std::vector<std::uint64_t>tags(pts.size());
    for(std::uint64_t b=0;b<(std::uint64_t{1}<<ell);++b){
        set_word(in,0,b,ell);c.eval(v,in,0,cut);counts.gate_evaluations+=cut;++counts.scalar_cases;
        lab::require(decode_point(value,v)==f.c.mul(f.P,b),"gate scalar mismatch");
        lab::require((v[canonical]!=0)==(b<static_cast<std::uint64_t>(f.r)),"canonical scalar acceptance");
        for(std::size_t j=0;j<pts.size();++j){point_input(in,qfirst,pts[j],a.n);c.eval(v,in,cut,c.g.size());counts.gate_evaluations+=c.g.size()-cut;++counts.target_cases;
            const bool want=b<static_cast<std::uint64_t>(f.r)&&decode_point(value,v)==pts[j];lab::require((v[accepts]!=0)==want,"target predicate mismatch");if(v[accepts]){parity[j]^=1U;tags[j]^=b;}}
        for(auto bad:malformed){
            point_input(in,qfirst,bad,a.n);c.eval(v,in,cut,c.g.size());counts.gate_evaluations+=c.g.size()-cut;++counts.malformed_cases;lab::require(v[accepts]==0,"malformed target accepted");}
    }
    const auto orb=lab::orbit(f);
    for(std::size_t j=0;j<pts.size();++j){auto it=std::find(orb.begin(),orb.end(),pts[j]);if(it==orb.end())lab::require(parity[j]==0&&tags[j]==0,"outside subgroup response");else lab::require(parity[j]==1&&tags[j]==static_cast<std::uint64_t>(it-orb.begin()),"tagged response mismatch");}
    point_input(in,qfirst,{},a.n);set_word(in,0,1,ell);c.eval(v,in);counts.gate_evaluations+=c.g.size();lab::require(c.witness(v,in),"valid gate witness rejected");
    const std::size_t stride=std::max<std::size_t>(1,c.g.size()/64);
    for(std::size_t j=0;j<c.g.size();j+=stride){auto copy=v;copy[j]^=1U;lab::require(!c.witness(copy,in),"corrupt gate witness accepted");++counts.mutation_cases;}
    std::uint64_t block_gates=0,block_eval=0;
    for(unsigned d=1;d<=2;++d){Circuit bc;Arithmetic ba(bc,f.c);ba.base=ba.point(f.P);const std::size_t first=bc.inputs;BPoint incoming{bc.input_word(ba.n),bc.input_word(ba.n),bc.input()};Word word=bc.input_word(d);auto z=ba.window(incoming,word);const W good=ba.valid(incoming);std::vector<unsigned char>bv,bi(bc.inputs);block_gates+=bc.g.size();
        // Every valid full-curve incoming boundary and every local scalar word.
        // Checking the unique output for each word establishes each delta entry;
        // the second loop compares all tagged outgoing boundaries explicitly.
        for(auto A:pts){std::vector<unsigned>bp(pts.size());std::vector<std::uint64_t>bt(pts.size());point_input(bi,first,A,ba.n);
            for(std::uint64_t w=0;w<(std::uint64_t{1}<<d);++w){set_word(bi,2*ba.n+1,w,d);bc.eval(bv,bi);block_eval+=bc.g.size();lab::require(bv[good]!=0,"valid block input rejected");const auto got=decode_point(z,bv),want=f.c.add(f.c.mul(A,std::uint64_t{1}<<d),f.c.mul(f.P,w));lab::require(got==want,"bit block mismatch");auto it=std::find(pts.begin(),pts.end(),got);lab::require(it!=pts.end(),"block output not on curve");const auto index=static_cast<std::size_t>(it-pts.begin());bp[index]^=1U;bt[index]^=w;}
            for(std::size_t j=0;j<pts.size();++j){unsigned expected_p=0;std::uint64_t expected_t=0;for(std::uint64_t w=0;w<(std::uint64_t{1}<<d);++w)if(f.c.add(f.c.mul(A,std::uint64_t{1}<<d),f.c.mul(f.P,w))==pts[j]){expected_p^=1U;expected_t^=w;}lab::require(bp[j]==expected_p&&bt[j]==expected_t,"tagged gate boundary mismatch");++counts.boundary_cases;if(bp[j]!=0||bt[j]!=0)++counts.nonzero_boundary_cells;if(bp[j]==0&&bt[j]!=0)++counts.tag_only_cells;}
        }
        for(auto bad:malformed){point_input(bi,first,bad,ba.n);bc.eval(bv,bi);block_eval+=bc.g.size();lab::require(bv[good]==0,"invalid incoming block accepted");++counts.malformed_cases;}
    }
    out<<"{\"track\":\"D\",\"fixture\":"<<lab::json_quote(f.id)<<",\"scope\":\"exploratory_toy_diagnostic\",\"outcome\":\"complete_valid\",\"p\":"<<f.c.p<<",\"r\":"<<f.r<<",\"scalar_bits\":"<<ell<<",\"gate_nodes\":"<<c.g.size()<<",\"cnf_clause_count_if_tseitin_encoded\":"<<c.cnf_clauses()<<",\"scalar_cases\":"<<counts.scalar_cases<<",\"target_predicate_cases\":"<<counts.target_cases<<",\"malformed_cases\":"<<counts.malformed_cases<<",\"tagged_boundary_cases\":"<<counts.boundary_cases<<",\"nonzero_boundary_cells\":"<<counts.nonzero_boundary_cells<<",\"zero_parity_nonzero_tag_cells\":"<<counts.tag_only_cells<<",\"corrupt_witnesses_rejected\":"<<counts.mutation_cases<<",\"scalar_gate_evaluations\":"<<counts.gate_evaluations<<",\"block_gate_nodes\":"<<block_gates<<",\"block_gate_evaluations\":"<<block_eval<<",\"unique_extension_basis\":\"every gate is deterministic and strictly topological; witness mutations are regressions\",\"compiler_uses_scalar_lookup\":false,\"new_cancellation_rule\":false,\"solver_gain_claim\":false,\"known_control\":\"fixed_window\"}\n";
}

struct R {
    I num=0,den=1;
    R(I n=0,I d=1):num(n),den(d){
        lab::require(d!=0,"zero rational denominator");
        if(den<0){num=-num;den=-den;}
        const I factor=std::gcd(num,den);num/=factor;den/=factor;
    }
    static I product(I a,I b){I z=0;lab::require(!__builtin_mul_overflow(a,b,&z),"exact rational multiplication overflow");return z;}
    static I sum(I a,I b){I z=0;lab::require(!__builtin_add_overflow(a,b,&z),"exact rational addition overflow");return z;}
    friend R operator+(const R&a,const R&b){const I g=std::gcd(a.den,b.den);return {sum(product(a.num,b.den/g),product(b.num,a.den/g)),product(a.den/g,b.den)};}
    friend R operator-(const R&a){return {-a.num,a.den};}
    friend R operator-(const R&a,const R&b){return a+(-b);}
    friend R operator*(const R&a,const R&b){const I g1=std::gcd(a.num,b.den),g2=std::gcd(b.num,a.den);return {product(a.num/g1,b.num/g2),product(a.den/g2,b.den/g1)};}
    friend R operator/(const R&a,const R&b){lab::require(b.num!=0,"division by zero rational");return a*R(b.den,b.num);}
    R& operator+=(const R&b){*this=*this+b;return *this;}
    friend bool operator==(const R&,const R&)=default;
};
using Matrix=std::array<std::array<R,2>,2>;
struct Tensor{std::string name;unsigned arity;std::vector<R>v;std::vector<bool>output;};
Tensor relation(const std::string&name,unsigned arity,const std::vector<bool>&output,const std::vector<unsigned>&support){Tensor t{name,arity,std::vector<R>(std::size_t{1}<<arity),output};for(auto i:support)t.v[i]=1;return t;}
std::vector<Tensor> gate_tensors(){
    std::vector<Tensor> ts;
    ts.push_back(relation("AND",3,{false,false,true},{0,1,2,7}));
    ts.push_back(relation("XOR",3,{false,false,true},{0,5,6,3}));
    ts.push_back(relation("NOT",2,{false,true},{1,2}));
    ts.push_back(relation("COPY",3,{false,true,true},{0,7}));
    ts.push_back(relation("EQUALITY",2,{false,true},{0,3}));
    ts.push_back(relation("CONST0",1,{true},{0}));ts.push_back(relation("CONST1",1,{true},{1}));
    std::vector<unsigned> add;
    for(unsigned a=0;a<2;++a)for(unsigned b=0;b<2;++b)for(unsigned c=0;c<2;++c){const unsigned total=a+b+c;add.push_back(a|(b<<1U)|(c<<2U)|((total&1U)<<3U)|((total>>1U)<<4U));}
    ts.push_back(relation("FULL_ADDER",5,{false,false,false,true,true},add));return ts;
}
Tensor transform(Tensor t,const Matrix&M,const Matrix&inv_t){
    auto v=t.v;
    for(unsigned leg=0;leg<t.arity;++leg){auto z=v;const auto&A=t.output[leg]?M:inv_t;
        for(unsigned mask=0;mask<(1U<<t.arity);++mask){z[mask]=R(0);const unsigned j=(mask>>leg)&1U;for(unsigned i=0;i<2;++i)z[mask]+=A[j][i]*v[(mask&~(1U<<leg))|(i<<leg)];}v=std::move(z);}
    t.v=std::move(v);return t;
}
struct IdChecks{bool parity=true,identities=true;std::uint64_t checked=0;int even_index=-1,odd_index=-1;unsigned bad_alpha=0,bad_beta=0;R residual=0;};
IdChecks identities(const Tensor&t){
    IdChecks out;bool even=false,odd=false;
    for(unsigned m=0;m<t.v.size();++m)if(t.v[m]!=R(0)){if((std::popcount(m)&1)==0){even=true;if(out.even_index<0)out.even_index=static_cast<int>(m);}else{odd=true;if(out.odd_index<0)out.odd_index=static_cast<int>(m);}}
    out.parity=!(even&&odd);
    for(unsigned alpha=0;alpha<t.v.size();++alpha)for(unsigned beta=0;beta<t.v.size();++beta){const unsigned difference=alpha^beta;R sum=0;unsigned order=0;
        for(unsigned bit=0;bit<t.arity;++bit)if((difference&(1U<<bit))!=0){++order;const auto term=t.v[alpha^(1U<<bit)]*t.v[beta^(1U<<bit)];sum+=((order&1U)!=0?-term:term);}
        ++out.checked;if(sum!=R(0)){if(out.identities){out.bad_alpha=alpha;out.bad_beta=beta;out.residual=sum;}out.identities=false;}
    }return out;
}
std::vector<Matrix> grammar(){std::vector<Matrix>out;for(I a=-1;a<=1;++a)for(I b=-1;b<=1;++b)for(I c=-1;c<=1;++c)for(I d=-1;d<=1;++d)if(a*d-b*c!=0)out.push_back({{{R(a),R(b)},{R(c),R(d)}}});return out;}
Matrix inv_transpose(const Matrix&m){const R det=m[0][0]*m[1][1]-m[0][1]*m[1][0];lab::require(det!=R(0),"singular basis");return {{{m[1][1]/det,-m[1][0]/det},{-m[0][1]/det,m[0][0]/det}}};}
std::uint64_t basis_calibration(){
    const auto bases=grammar();const auto eq=relation("matchgate_equality",2,{false,true},{0,3});const auto mg=identities(eq);lab::require(mg.parity&&mg.identities,"known matchgate equality failed");
    const auto odd=relation("matchgate_odd",3,{true,true,true},{1,2,4});const auto oi=identities(odd);lab::require(oi.parity&&oi.identities,"known arity-three matchgate failed");
    Tensor pf{"known_pfaffian_4",4,std::vector<R>(16),std::vector<bool>(4,true)};
    pf.v[0]=1;pf.v[3]=1;pf.v[5]=2;pf.v[9]=3;pf.v[6]=4;pf.v[10]=5;pf.v[12]=6;pf.v[15]=8;
    const auto pi=identities(pf);lab::require(pi.parity&&pi.identities,"known four-leg Pfaffian signature failed");
    const auto bad=relation("violates_pfaffian_4",4,{true,true,true,true},{0,15});const auto bi=identities(bad);lab::require(bi.parity&&!bi.identities,"Pfaffian negative calibration missed");
    const auto mixed=relation("mixed_parity",3,{true,true,true},{0,1});lab::require(!identities(mixed).parity,"parity negative calibration missed");
    lab::RNG rng(0x6d61746368676174ULL);Tensor random_even{"frozen_random_even",5,std::vector<R>(32),std::vector<bool>(5,true)};
    for(unsigned i=0;i<32;++i)if((std::popcount(i)&1)==0)random_even.v[i]=R(static_cast<I>(rng.next()%7U)-3);
    const auto ri=identities(random_even);lab::require(ri.parity&&!ri.identities,"frozen random non-matchgate calibration missed");
    Tensor random_mixed{"frozen_random_mixed",5,std::vector<R>(32),std::vector<bool>(5,true)};
    for(auto&x:random_mixed.v)x=R(static_cast<I>(rng.next()%7U)-3);
    lab::require(!identities(random_mixed).parity,"frozen random mixed-parity calibration missed");
    std::uint64_t checks=0;
    for(const auto&M:bases){const auto inv=inv_transpose(M);
        for(unsigned x=0;x<2;++x)for(unsigned y=0;y<2;++y){R z=0;for(unsigned j=0;j<2;++j)z+=M[j][x]*inv[j][y];lab::require(z==R(x==y?1:0),"wire contraction changed");++checks;}}
    return checks+7;
}
void matchgate_row(std::ostream&out){
    const auto bases=grammar();const auto ts=gate_tensors();const auto calibrations=basis_calibration();
    struct Failure{Matrix basis;std::string tensor;Tensor transformed;IdChecks check;};
    std::vector<Failure>failures;
    std::vector<std::uint64_t>passes(ts.size()),parity_passes(ts.size());std::uint64_t all=0,total=0;std::vector<std::string>rejections;
    for(const auto&M:bases){const auto inv=inv_transpose(M);bool good=true;std::string first;
        for(std::size_t i=0;i<ts.size();++i){const auto transformed=transform(ts[i],M,inv);const auto c=identities(transformed);total+=c.checked;if(c.parity)++parity_passes[i];if(c.parity&&c.identities)++passes[i];else{good=false;if(first.empty()){first=ts[i].name;failures.push_back({M,first,transformed,c});}}}
        if(good)++all;else rejections.push_back(first);
    }
    out<<"{\"track\":\"L4\",\"fixture\":\"shared_boolean_gate_grammar\",\"scope\":\"exploratory_toy_diagnostic\",\"outcome\":\"complete_valid\",\"coefficient_domain\":\"exact_rational_int64_bounded\",\"grammar_matrices_before_singularity_filter\":81,\"invertible_matrices\":"<<bases.size()<<",\"gate_signatures\":"<<ts.size()<<",\"matchgate_identity_checks\":"<<total<<",\"calibration_checks\":"<<calibrations<<",\"all_signature_survivors\":"<<all<<",\"per_signature\":[";
    for(std::size_t i=0;i<ts.size();++i){if(i)out<<',';out<<"{\"name\":"<<lab::json_quote(ts[i].name)<<",\"parity_passes\":"<<parity_passes[i]<<",\"full_passes\":"<<passes[i]<<'}';}
    out<<"],\"first_rejection_counts\":{";std::map<std::string,std::uint64_t>freq;for(const auto&x:rejections)++freq[x];bool first=true;for(const auto&[name,n]:freq){if(!first)out<<',';first=false;out<<lab::json_quote(name)<<':'<<n;}
    out<<"},\"basis_failures\":[";
    for(std::size_t i=0;i<failures.size();++i){if(i)out<<',';const auto&f=failures[i];out<<"{\"matrix\":[["<<f.basis[0][0].num<<','<<f.basis[0][1].num<<"],["<<f.basis[1][0].num<<','<<f.basis[1][1].num<<"]],\"first_tensor\":"<<lab::json_quote(f.tensor)<<",\"parity_pass\":"<<(f.check.parity?"true":"false")<<",\"identity_pass\":"<<(f.check.identities?"true":"false");
        if(!f.check.parity){const auto e=static_cast<std::size_t>(f.check.even_index),o=static_cast<std::size_t>(f.check.odd_index);out<<",\"even_support_witness\":["<<e<<','<<f.transformed.v[e].num<<','<<f.transformed.v[e].den<<"],\"odd_support_witness\":["<<o<<','<<f.transformed.v[o].num<<','<<f.transformed.v[o].den<<']';}
        if(!f.check.identities)out<<",\"identity_witness\":["<<f.check.bad_alpha<<','<<f.check.bad_beta<<','<<f.check.residual.num<<','<<f.check.residual.den<<']';
        out<<'}';}
    out<<"],\"global_planar_construction\":false,\"novelty_claim\":false,\"inference_scope\":\"only_the_81_entry_finite_common_basis_grammar\"}\n";
}
} // namespace diagnostic

int main(int argc,char**argv){
    try{
        if(argc==2&&std::string(argv[1])=="--self-test"){
            diagnostic::test_arithmetic();diagnostic::basis_calibration();
            const std::vector<lab::Fixture>fs{{"D-selftest-p5","special_control",{5,0,1},{0,1,false},3,6,1},{"D-selftest-p17","special_control",{17,2,2},{5,1,false},19,19,1},{"D-selftest-p23","special_control",{23,1,1},{17,3,false},7,28,1}};
            for(const auto&f:fs)diagnostic::direct_row(f,std::cout);
            diagnostic::matchgate_row(std::cout);
            std::cout<<"{\"self_test\":\"pass\",\"scope\":\"development_only\"}\n";return 0;
        }
        if(argc==4&&std::string(argv[1])=="--run"){
            const auto fixtures=lab::read_fixtures(argv[2]);std::ofstream out(argv[3]);lab::require(static_cast<bool>(out),"cannot open output");
            diagnostic::test_arithmetic();for(const auto&f:fixtures)diagnostic::direct_row(f,out);diagnostic::matchgate_row(out);return 0;
        }
        std::cerr<<"usage: circuit --self-test | --run FIXTURES_TSV OUTPUT_JSONL\n";return 2;
    }catch(const std::exception&e){std::cerr<<"circuit diagnostic failed: "<<e.what()<<'\n';return 1;}
}
