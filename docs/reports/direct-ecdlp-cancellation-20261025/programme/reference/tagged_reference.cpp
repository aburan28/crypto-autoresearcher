// Development reference only: exhaustive O(r) tagged counting, not a fast ECDLP solver.
#include <algorithm>
#include <bit>
#include <cstdint>
#include <exception>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

using I = std::int64_t;
using U = std::uint64_t;

struct Point {
    I x = 0, y = 0;
    bool infinity = true;
    friend bool operator==(const Point&, const Point&) = default;
};

struct Curve {
    I p, a, b;
    I mod(I x) const { x %= p; return x < 0 ? x + p : x; }
    I pow(I x, I e) const {
        I z = 1;
        for (; e != 0; e >>= 1, x = mod(x*x)) if ((e & 1) != 0) z = mod(z*x);
        return z;
    }
    I inverse_scan(I x) const {
        x = mod(x);
        for (I y = 1; y < p; ++y) if (mod(x*y) == 1) return y;
        throw std::invalid_argument("noninvertible field element");
    }
    bool canonical(Point q) const {
        if (q.infinity) return q.x == 0 && q.y == 0;
        return q.x >= 0 && q.x < p && q.y >= 0 && q.y < p &&
            mod(q.y*q.y) == mod(q.x*q.x*q.x + a*q.x + b);
    }
    void require(Point q) const {
        if (!canonical(q)) throw std::invalid_argument("noncanonical or off-curve point");
    }
    Point neg(Point q) const {
        require(q);
        return q.infinity ? q : Point{q.x, mod(-q.y), false};
    }
    Point add(Point q, Point s) const {
        require(q); require(s);
        if (q.infinity) return s;
        if (s.infinity) return q;
        if (q.x == s.x && mod(q.y+s.y) == 0) return {};
        const I slope = q == s ? mod((3*q.x*q.x+a)*inverse_scan(2*q.y)) :
            mod((s.y-q.y)*inverse_scan(s.x-q.x));
        const I x = mod(slope*slope-q.x-s.x);
        return {x, mod(slope*(q.x-x)-q.y), false};
    }
    std::vector<Point> points() const {
        std::vector<Point> out{{}};
        for (I x=0; x<p; ++x) for (I y=0; y<p; ++y)
            if (canonical({x,y,false})) out.push_back({x,y,false});
        return out;
    }
};

bool prime(I n) {
    if (n < 2) return false;
    for (I d=2; d <= n/d; ++d) if (n % d == 0) return false;
    return true;
}

void validate_curve(const Curve& c) {
    // Bound all products to this development implementation's signed arithmetic.
    if (c.p > 1000 || !prime(c.p) || c.p <= 3 || c.a < 0 || c.a >= c.p ||
        c.b < 0 || c.b >= c.p || c.mod(4*c.a*c.a*c.a+27*c.b*c.b) == 0)
        throw std::invalid_argument("unsupported, singular, or non-prime curve");
}

struct Jacobian { I x=0, y=1, z=0; };

Jacobian project(Point q) { return q.infinity ? Jacobian{} : Jacobian{q.x,q.y,1}; }

Jacobian double_j(const Curve& c, Jacobian q) {
    if (q.z == 0 || q.y == 0) return {};
    const I yy=c.mod(q.y*q.y), yyyy=c.mod(yy*yy), zz=c.mod(q.z*q.z);
    const I s=c.mod(4*q.x*yy), m=c.mod(3*q.x*q.x+c.a*c.mod(zz*zz));
    const I x=c.mod(m*m-2*s);
    return {x,c.mod(m*(s-x)-8*yyyy),c.mod(2*q.y*q.z)};
}

Jacobian add_j(const Curve& c, Jacobian q, Jacobian s) {
    if (q.z == 0) return s;
    if (s.z == 0) return q;
    const I z1=c.mod(q.z*q.z), z2=c.mod(s.z*s.z);
    const I u1=c.mod(q.x*z2), u2=c.mod(s.x*z1);
    const I s1=c.mod(q.y*c.mod(s.z*z2)), s2=c.mod(s.y*c.mod(q.z*z1));
    if (u1 == u2) return s1 == s2 ? double_j(c,q) : Jacobian{};
    const I h=c.mod(u2-u1), i=c.mod(4*h*h), j=c.mod(h*i);
    const I rr=c.mod(2*(s2-s1)), v=c.mod(u1*i);
    const I x=c.mod(rr*rr-j-2*v);
    return {x,c.mod(rr*(v-x)-2*s1*j),c.mod(2*q.z*s.z*h)};
}

Point normalize(const Curve& c, Jacobian q) {
    if (q.z == 0) return {};
    const I zi=c.pow(q.z,c.p-2), zz=c.mod(zi*zi);
    return {c.mod(q.x*zz),c.mod(q.y*c.mod(zz*zi)),false};
}

Point multiply_j(const Curve& c, Point p, U n) {
    Jacobian q{};
    for (Jacobian v=project(p); n!=0; n>>=1, v=double_j(c,v))
        if ((n&1U)!=0) q=add_j(c,q,v);
    return normalize(c,q);
}

struct Subgroup {
    Curve c;
    Point p;
    U r;
    unsigned bits;
    Subgroup(Curve curve, Point generator, U order) : c(curve),p(generator),r(order),bits(0) {
        validate_curve(c); c.require(p);
        if (p.infinity || r > 1000 || !prime(static_cast<I>(r)) ||
            !multiply_j(c,p,r).infinity)
            throw std::invalid_argument("uncertified prime-order subgroup");
        bits=static_cast<unsigned>(std::bit_width(r-1));
    }
};

struct Trace { std::vector<Point> states; };

// Total point-level scalar program. Range acceptance is a separate predicate.
// This is not yet a Boolean gate/carry encoding of the arithmetic.
Point scalar_program(const Subgroup& g, U b, Trace* trace=nullptr) {
    if (b >= (U{1} << g.bits)) throw std::invalid_argument("input exceeds scalar bit width");
    Point q{};
    if (trace != nullptr) trace->states.push_back(q);
    for (unsigned j=g.bits; j!=0; --j) {
        q=g.c.add(q,q);
        if (trace != nullptr) trace->states.push_back(q);
        q=g.c.add(q, ((b>>(j-1))&1U)!=0 ? g.p : Point{});
        if (trace != nullptr) trace->states.push_back(q);
    }
    return q;
}

bool valid_trace(const Subgroup& g, U b, const Trace& t) {
    Trace expected;
    (void)scalar_program(g,b,&expected);
    return expected.states == t.states;
}

// (constant, linear coefficients) in F2[e_0,...]/(e_i e_j for every i,j).
struct Tag {
    bool constant=false;
    U linear=0;
    friend bool operator==(const Tag&, const Tag&) = default;
    friend Tag operator+(Tag a,Tag b) { return {a.constant!=b.constant,a.linear^b.linear}; }
    friend Tag operator*(Tag a,Tag b) {
        return {a.constant&&b.constant,(a.constant?b.linear:0)^(b.constant?a.linear:0)};
    }
};

Tag input_tag(U b,unsigned bits) {
    Tag out{true,0};
    for (unsigned j=0; j<bits; ++j)
        out=out*Tag{true,((b>>j)&1U)!=0 ? (U{1}<<j) : 0};
    return out;
}

enum class AuxiliaryPolicy { deterministic_unique, unconstrained };

Tag tagged_response(const Subgroup& g, Point q,
    AuxiliaryPolicy policy=AuxiliaryPolicy::deterministic_unique) {
    g.c.require(q);
    if (policy!=AuxiliaryPolicy::deterministic_unique)
        throw std::invalid_argument("parity encoding requires unique auxiliary extensions");
    Tag z{};
    for (U b=0; b<(U{1}<<g.bits); ++b)
        if (b<g.r && scalar_program(g,b)==q) z=z+input_tag(b,g.bits);
    return z;
}

// Exact one/two-step boundary specification, ready to compare a future rule.
// Bit j tags the j-th least-significant bit of the block word.
Point step_block(const Subgroup& g,Point boundary,U word,unsigned steps) {
    if(steps<1||steps>2||word>=(U{1}<<steps))
        throw std::invalid_argument("unsupported micro-block");
    g.c.require(boundary);
    for(unsigned j=steps;j!=0;--j)
        boundary=g.c.add(g.c.add(boundary,boundary),((word>>(j-1))&1U)!=0?g.p:Point{});
    return boundary;
}

Tag block_response(const Subgroup& g,Point incoming,Point outgoing,unsigned steps) {
    g.c.require(incoming); g.c.require(outgoing);
    Tag out{};
    for(U word=0;word<(U{1}<<steps);++word)
        if(step_block(g,incoming,word,steps)==outgoing) out=out+input_tag(word,steps);
    return out;
}

struct Checks {
    U assertions=0, pairs=0, scalar_inputs=0, subgroup_targets=0, outside_targets=0;
    U transition_candidates=0, trace_mutations=0, ring_checks=0, expected_rejections=0;
    U block_boundary_cases=0;
    void check(bool condition,const std::string& message) {
        ++assertions;
        if (!condition) throw std::runtime_error(message);
    }
    template<class F> void rejects(F f,const std::string& label) {
        bool threw=false;
        try { f(); } catch (const std::invalid_argument&) { threw=true; }
        check(threw,"did not reject "+label); ++expected_rejections;
    }
};

void test_ring(Checks& t) {
    const std::vector<Tag> tags=[] {
        std::vector<Tag> out;
        for (unsigned a=0; a<2; ++a) for (U v=0; v<8; ++v) out.push_back({a!=0,v});
        return out;
    }();
    for (Tag a:tags) for (Tag b:tags) for (Tag c:tags) {
        t.check((a*b)*c==a*(b*c),"ring multiplication associativity");
        t.check(a*(b+c)==a*b+a*c,"ring distributivity");
        t.ring_checks+=2;
    }
    for (unsigned i=0;i<3;++i) for(unsigned j=0;j<3;++j) {
        t.check(Tag{false,U{1}<<i}*Tag{false,U{1}<<j}==Tag{},"all products of tags vanish");
        ++t.ring_checks;
    }
    for (U b=0;b<8;++b) {
        const Tag z=input_tag(b,3);
        t.check(z==Tag{true,b},"input tag expansion");
        t.check(z+z==Tag{},"even witness multiplicity erases scalar and count");
        t.check(z+z+z==z,"odd multiplicity retains tag; uniqueness still required");
        t.ring_checks+=3;
    }
}

void test_fixture(Checks& t,const Subgroup& g,U group_order) {
    const auto pts=g.c.points();
    t.check(pts.size()==group_order,"whole curve order");
    t.check(group_order%g.r==0,"subgroup order divides whole curve order");
    t.check(group_order!=static_cast<U>(g.c.p),"fixture is non-anomalous");
    for (Point a:pts) for (Point b:pts) {
        const Point affine=g.c.add(a,b), jac=normalize(g.c,add_j(g.c,project(a),project(b)));
        t.check(g.c.canonical(affine),"affine output canonical");
        t.check(affine==jac,"independent affine/Jacobian addition disagreement");
        ++t.pairs;
    }
    for (U b=0;b<(U{1}<<g.bits);++b) {
        Trace trace;
        const Point q=scalar_program(g,b,&trace);
        t.check(q==multiply_j(g.c,g.p,b),"scalar affine/Jacobian disagreement");
        t.check(trace.states.size()==2*g.bits+1,"deterministic trace length");
        t.check(valid_trace(g,b,trace),"generated trace valid");
        ++t.scalar_inputs;
        for (std::size_t j=0;j<trace.states.size();++j) {
            Trace changed=trace;
            changed.states[j]=pts[(static_cast<std::size_t>(std::find(pts.begin(),pts.end(),trace.states[j])-pts.begin())+1)%pts.size()];
            t.check(!valid_trace(g,b,changed),"mutated trace accepted");
            ++t.trace_mutations;
        }
    }
    // Enumerate all possible intermediate/output witnesses of one point-level
    // step, for all incoming points and both bits. Each pair of local factors
    // must have exactly one satisfying extension.
    for (Point q:pts) for (unsigned bit=0;bit<2;++bit) {
        U count=0;
        for(Point middle:pts) for(Point s:pts) {
            if(middle==g.c.add(q,q) && s==g.c.add(middle,bit!=0?g.p:Point{})) ++count;
            ++t.transition_candidates;
        }
        t.check(count==1,"point-level transition not single valued");
    }
    // Known fixed-window identity is a positive control, not a new attack.
    // Preserve every tag on every incoming/outgoing point boundary.
    for(unsigned steps=1;steps<=2;++steps) for(Point incoming:pts) for(Point outgoing:pts) {
        Tag window{};
        for(U word=0;word<(U{1}<<steps);++word) {
            const Point expected=normalize(g.c,add_j(g.c,
                project(multiply_j(g.c,incoming,U{1}<<steps)),
                project(multiply_j(g.c,g.p,word))));
            if(expected==outgoing) window=window+input_tag(word,steps);
        }
        t.check(block_response(g,incoming,outgoing,steps)==window,
            "tagged block boundary differs from fixed-window control");
        ++t.block_boundary_cases;
    }
    for(U k=0;k<g.r;++k) {
        const Point q=multiply_j(g.c,g.p,k);
        t.check(tagged_response(g,q)==Tag{true,k},"tagged response differs from scalar");
        t.check(tagged_response(g,g.c.neg(q))==Tag{true,k==0?0:g.r-k},"point sign handling");
        ++t.subgroup_targets;
    }
    for(Point q:pts) {
        bool inside=false;
        for(U k=0;k<g.r;++k) if(multiply_j(g.c,g.p,k)==q) inside=true;
        if(!inside) {
            t.check(tagged_response(g,q)==Tag{},"outside-subgroup target must return zero");
            ++t.outside_targets;
        }
    }
    t.rejects([&]{(void)scalar_program(g,U{1}<<g.bits);},"oversized bit input");
    t.rejects([&]{(void)tagged_response(g,g.p,AuxiliaryPolicy::unconstrained);},"ambiguous witness semantics");
    t.rejects([&]{(void)tagged_response(g,Point{1,0,true});},"noncanonical infinity");
    t.rejects([&]{(void)tagged_response(g,Point{-1,1,false});},"negative coordinate");
    t.rejects([&]{(void)tagged_response(g,Point{g.c.p,1,false});},"out-of-range coordinate");
    bool rejected_off_curve=false;
    for(I x=0;x<g.c.p&&!rejected_off_curve;++x) for(I y=0;y<g.c.p&&!rejected_off_curve;++y)
        if(!g.c.canonical({x,y,false})) {
            t.rejects([&]{(void)tagged_response(g,Point{x,y,false});},"off-curve target");
            rejected_off_curve=true;
        }
    t.check(rejected_off_curve,"off-curve rejection case exists");
    std::cout<<"fixture p="<<g.c.p<<" a="<<g.c.a<<" b="<<g.c.b
        <<" Px="<<g.p.x<<" Py="<<g.p.y<<" r="<<g.r
        <<" curve_order="<<group_order<<" cofactor="<<group_order/g.r
        <<" scalar_bits="<<g.bits<<" status=pass\n";
}

int main(int argc,char** argv) {
    if(argc!=2||std::string(argv[1])!="--self-test") {
        std::cerr<<"usage: tagged-reference --self-test\n"; return 2;
    }
    try {
        Checks t;
        test_ring(t);
        test_fixture(t,Subgroup{{5,0,1},{0,1,false},3},6);
        test_fixture(t,Subgroup{{17,2,2},{5,1,false},19},19);
        // The constructor checks that this nonidentity point has prime order seven.
        test_fixture(t,Subgroup{{23,1,1},{17,3,false},7},28);
        t.rejects([]{validate_curve({15,1,1});},"composite field");
        t.rejects([]{validate_curve({5,0,0});},"singular curve");
        t.rejects([]{(void)Subgroup{{17,2,2},{5,1,false},17};},"incorrect claimed order");
        t.rejects([]{(void)Subgroup{{5,0,1},{0,1,false},6};},"composite subgroup order");
        std::cout<<"PASS assertions="<<t.assertions<<" addition_pairs="<<t.pairs
            <<" scalar_inputs="<<t.scalar_inputs<<" subgroup_targets="<<t.subgroup_targets
            <<" outside_subgroup_targets="<<t.outside_targets
            <<" transition_candidates="<<t.transition_candidates
            <<" block_boundary_cases="<<t.block_boundary_cases
            <<" trace_mutations="<<t.trace_mutations<<" ring_checks="<<t.ring_checks
            <<" expected_rejections="<<t.expected_rejections<<"\n";
        std::cout<<"scope=development-correctness-only; no Boolean-wire encoding, cancellation rule, scientific trial, timing, or speedup claim\n";
    } catch(const std::exception& e) { std::cerr<<"FAIL "<<e.what()<<'\n'; return 1; }
}
