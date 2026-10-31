// Classical toy diagnostics L1/L3. No scalar-recovery algorithm is claimed.
#include "common.hpp"
#include <algorithm>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

namespace pe {
using lab::I;
using U=std::uint64_t;

struct Counts {
    U additions=0,multiplications=0,power_calls=0,inversions=0;
    U projective_checks=0,doubles=0,adds=0,section_calls=0,scalar_calls=0;
    U reduction_crosschecks=0;
};

struct Ring {
    I n,p;
    Counts* counts;
    I mod(I v) const { v%=n; return v<0?v+n:v; }
    I add(I a,I b) const { ++counts->additions; return mod(mod(a)+mod(b)); }
    I sub(I a,I b) const { ++counts->additions; return mod(mod(a)-mod(b)); }
    I mul(I a,I b) const {
        ++counts->multiplications;
        // n=p²<2^32; the product of canonical residues fits uint64_t.
        return static_cast<I>((static_cast<U>(mod(a))*static_cast<U>(mod(b)))%static_cast<U>(n));
    }
    I power(I a,U e) const {
        ++counts->power_calls;
        I out=1;
        while(e!=0) {
            if((e&1U)!=0) out=mul(out,a);
            e>>=1;
            if(e!=0) a=mul(a,a);
        }
        return out;
    }
    I inverse(I a) const {
        ++counts->inversions;
        lab::require(mod(a)%p!=0,"attempted inverse of nonunit modulo p^2");
        return power(a,static_cast<U>(p*(p-1)-1));
    }
};

struct J { I x=1,y=1,z=0; };

struct Lift {
    lab::Curve base;
    Counts counts;
    Ring ring;
    explicit Lift(lab::Curve c):base(c),ring{c.p*c.p,c.p,&counts} {
        lab::require(c.p>3&&c.p<=65535&&lab::prime(c.p),"unsupported p-adic field");
    }
    Lift(const Lift&)=delete;
    Lift& operator=(const Lift&)=delete;

    void check(J q) {
        ++counts.projective_checks;
        lab::require(q.x>=0&&q.x<ring.n&&q.y>=0&&q.y<ring.n&&q.z>=0&&q.z<ring.n,
            "noncanonical projective residue");
        lab::require(q.x%base.p!=0||q.y%base.p!=0||q.z%base.p!=0,
            "non-unimodular projective point: ring addition chart invalid");
        const I z2=ring.mul(q.z,q.z),z4=ring.mul(z2,z2),z6=ring.mul(z4,z2);
        const I rhs=ring.add(ring.add(ring.mul(ring.mul(q.x,q.x),q.x),
            ring.mul(base.a,ring.mul(q.x,z4))),ring.mul(base.b,z6));
        lab::require(ring.mul(q.y,q.y)==rhs,"projective curve equation failed over Z/p^2");
    }

    lab::Point reduce(J q) {
        if(q.z%base.p==0) return {0,0,true};
        const I zi=base.inv(q.z%base.p),z2=base.mod(zi*zi);
        return {base.mod((q.x%base.p)*z2),base.mod((q.y%base.p)*base.mod(z2*zi)),false};
    }

    J section(lab::Point q) {
        ++counts.section_calls;
        lab::require(base.valid(q),"invalid input to point section");
        if(q.inf) return {};
        lab::require(q.y!=0,"Hensel section requires a non-2-torsion finite point");
        const I x=ring.power(q.x,static_cast<U>(base.p));
        lab::require(x%base.p==q.x&&ring.power(x,static_cast<U>(base.p))==x,
            "Teichmuller lift failed");
        const I rhs=ring.add(ring.add(ring.mul(ring.mul(x,x),x),ring.mul(base.a,x)),base.b);
        const I difference=ring.sub(rhs,ring.mul(q.y,q.y));
        lab::require(difference%base.p==0,"Hensel residual is not divisible by p");
        const I correction=base.mod((difference/base.p)*base.inv(base.mod(2*q.y)));
        const J out{x,ring.mod(q.y+base.p*correction),1};
        check(out);
        lab::require(reduce(out)==q,"section does not reduce to input");
        return out;
    }

    J twice(J q) {
        ++counts.doubles;
        if(q.z==0) return {};
        if(q.y==0) return {};
        const I yy=ring.mul(q.y,q.y),yyyy=ring.mul(yy,yy),z2=ring.mul(q.z,q.z);
        const I s=ring.mul(4,ring.mul(q.x,yy));
        const I m=ring.add(ring.mul(3,ring.mul(q.x,q.x)),ring.mul(base.a,ring.mul(z2,z2)));
        const I x=ring.sub(ring.mul(m,m),ring.mul(2,s));
        const J out{x,ring.sub(ring.mul(m,ring.sub(s,x)),ring.mul(8,yyyy)),
            ring.mul(2,ring.mul(q.y,q.z))};
        check(out);
        return out;
    }

    J plus(J q,J s) {
        ++counts.adds;
        if(q.z==0) return s;
        if(s.z==0) return q;
        const I z1=ring.mul(q.z,q.z),z2=ring.mul(s.z,s.z);
        const I u1=ring.mul(q.x,z2),u2=ring.mul(s.x,z1);
        const I s1=ring.mul(q.y,ring.mul(s.z,z2)),s2=ring.mul(s.y,ring.mul(q.z,z1));
        if(u1==u2) {
            if(s1==s2) return twice(q);
            lab::require(ring.add(s1,s2)==0,"unsupported coincident-reduction ring chart");
            return {};
        }
        const I h=ring.sub(u2,u1),rr=ring.sub(s2,s1),hh=ring.mul(h,h),hhh=ring.mul(hh,h);
        const I v=ring.mul(u1,hh);
        const I x=ring.sub(ring.sub(ring.mul(rr,rr),hhh),ring.mul(2,v));
        const J out{x,ring.sub(ring.mul(rr,ring.sub(v,x)),ring.mul(s1,hhh)),
            ring.mul(h,ring.mul(q.z,s.z))};
        check(out);
        return out;
    }

    void check_reduction(J q,lab::Point input,U scalar) {
        ++counts.reduction_crosschecks;
        lab::require(reduce(q)==base.mul(input,scalar),"p^2 point reduction disagrees with independent affine multiplication");
    }

    J multiply_left(J q,lab::Point input,U scalar) {
        ++counts.scalar_calls;
        J out{};
        U prefix=0;
        const unsigned width=lab::bits(scalar);
        for(unsigned j=width;j!=0;--j) {
            out=twice(out);prefix*=2;
            if(((scalar>>(j-1))&1U)!=0) {out=plus(out,q);++prefix;}
            check_reduction(out,input,prefix);
        }
        check(out);
        return out;
    }

    J multiply_right(J q,lab::Point input,U scalar) {
        ++counts.scalar_calls;
        J out{};
        U accumulated=0,weight=1;
        while(scalar!=0) {
            if((scalar&1U)!=0) {
                out=plus(out,q);accumulated+=weight;
                check_reduction(out,input,accumulated);
            }
            scalar>>=1;
            if(scalar!=0) {q=twice(q);weight*=2;check_reduction(q,input,weight);}
        }
        check(out);
        return out;
    }

    I formal_parameter(J q) {
        check(q);
        lab::require(q.z%base.p==0,"[r]section did not reduce to infinity");
        lab::require(q.y%base.p!=0,"nonunit Y on formal infinity chart");
        const I t=ring.sub(0,ring.mul(ring.mul(q.x,q.z),ring.inverse(q.y)));
        lab::require(t%base.p==0,"formal parameter not divisible by p");
        return t;
    }

    I defect_from_lift(J s,lab::Point q,I r) {
        check(s);
        lab::require(reduce(s)==q,"lift has wrong reduction");
        const J left=multiply_left(s,q,static_cast<U>(r));
        const J right=multiply_right(s,q,static_cast<U>(r));
        const I a=formal_parameter(left),b=formal_parameter(right);
        lab::require(a==b,"left/right p^2 scalar multiplication disagrees on formal parameter");
        return a/base.p;
    }
    I defect(lab::Point q,I r) { return defect_from_lift(section(q),q,r); }
};

std::string integer_array(const std::vector<I>& a) {
    std::ostringstream out;out<<'[';
    for(std::size_t j=0;j<a.size();++j){if(j!=0)out<<',';out<<a[j];}
    return out.str()+']';
}

std::string profile_row(const lab::Fixture& f) {
    const auto points=lab::orbit(f);
    Lift lift(f.c);
    std::vector<I> profile;profile.reserve(points.size());
    for(const auto q:points) profile.push_back(lift.defect(q,f.r));
    const auto public_section_counts=lift.counts;
    lab::require(profile.front()==0,"identity section defect nonzero");
    U sign_checks=0;
    for(I k=0;k<f.r;++k) {
        const auto j=static_cast<std::size_t>(k);
        lab::require(profile[static_cast<std::size_t>((f.r-k)%f.r)]==f.c.mod(-profile[j]),"section sign equivariance failed");
        ++sign_checks;
    }
    std::vector<I> histogram(static_cast<std::size_t>(f.c.p));
    U pairs=0,nonzero=0;
    I first_i=-1,first_j=-1,first_value=0;
    for(I i=0;i<f.r;++i) for(I j=0;j<f.r;++j) {
        const I d=f.c.mod(profile[static_cast<std::size_t>((i+j)%f.r)]-
            profile[static_cast<std::size_t>(i)]-profile[static_cast<std::size_t>(j)]);
        ++histogram[static_cast<std::size_t>(d)];++pairs;
        if(d!=0) {++nonzero;if(first_i<0){first_i=i;first_j=j;first_value=d;}}
    }
    const I slope=profile[1];
    const I inverse=slope==0?0:f.c.inv(slope);
    const auto predict=[&](I value){return slope==0?I{0}:f.c.mod(value*inverse)%f.r;};
    I hits=0,nontrivial_hits=0;
    for(I k=0;k<f.r;++k) if(predict(profile[static_cast<std::size_t>(k)])==k) {
        ++hits;if(k!=0&&k!=1&&k!=f.r-1) ++nontrivial_hits;
    }
    lab::RNG rng(f.seed^U{0x4c315045524d5554});
    std::vector<I> null_hits,null_nontrivial_hits;
    std::vector<I> pair_labels;
    for(I j=2;j<=(f.r-1)/2;++j) pair_labels.push_back(j);
    for(unsigned repeat=0;repeat<99;++repeat) {
        auto labels=pair_labels;rng.shuffle(labels);auto shuffled=profile;
        for(std::size_t j=0;j<labels.size();++j) {
            const I destination=static_cast<I>(j)+2;
            const I raw=profile[static_cast<std::size_t>(labels[j])];
            const I value=(rng.next()&1U)!=0?raw:f.c.mod(-raw);
            shuffled[static_cast<std::size_t>(destination)]=value;
            shuffled[static_cast<std::size_t>(f.r-destination)]=f.c.mod(-value);
        }
        auto original_multiset=profile,shuffled_multiset=shuffled;
        std::sort(original_multiset.begin(),original_multiset.end());std::sort(shuffled_multiset.begin(),shuffled_multiset.end());
        lab::require(original_multiset==shuffled_multiset,"sign-pair relabeling changed feature multiset");
        I total=0,nontrivial=0;
        for(I k=0;k<f.r;++k) if(predict(shuffled[static_cast<std::size_t>(k)])==k) {
            ++total;if(k!=0&&k!=1&&k!=f.r-1) ++nontrivial;
        }
        null_hits.push_back(total);null_nontrivial_hits.push_back(nontrivial);
    }
    // Secondary reference reproduces the simpler unconditional label shuffle.
    // It does not retain the publicly known identity/generator/sign anchors.
    lab::RNG unconditioned_rng(f.seed^U{0x4c31554e434f4e44});
    std::vector<I> unconditional_hits,unconditional_nontrivial_hits;
    for(unsigned repeat=0;repeat<99;++repeat) {
        auto shuffled=profile;unconditioned_rng.shuffle(shuffled);I total=0,nontrivial=0;
        for(I k=0;k<f.r;++k) if(predict(shuffled[static_cast<std::size_t>(k)])==k) {
            ++total;if(k!=0&&k!=1&&k!=f.r-1) ++nontrivial;
        }
        unconditional_hits.push_back(total);unconditional_nontrivial_hits.push_back(nontrivial);
    }
    // Deliberately scalar-labelled hard-lift control. This is advice, not a section
    // available from a challenge point. Its construction cost is recorded.
    const J lifted_generator=lift.section(f.P);
    J hard{};
    std::vector<I> hard_profile;
    U hard_linearity_checks=0;
    for(I k=0;k<f.r;++k) {
        const I value=lift.defect_from_lift(hard,points[static_cast<std::size_t>(k)],f.r);
        lab::require(value==f.c.mod(k*slope),"scalar-labelled hard-lift linearity control failed");
        hard_profile.push_back(value);++hard_linearity_checks;
        hard=lift.plus(hard,lifted_generator);
        lift.check_reduction(hard,f.P,static_cast<U>(k+1));
    }
    lab::require(lift.formal_parameter(hard)/f.c.p==slope,"sequential [r] lift disagrees with binary multiplication");
    // Exact formal-group control: for t=pc, t²=0 modulo p², so its law is additive.
    // Doubling is checked by actual projective arithmetic; no two-point ring chart is assumed.
    U formal_controls=0;
    for(I c=0;c<f.c.p;++c) {
        J q{1,lift.ring.n-1,f.c.p*c};lift.check(q);
        lab::require(lift.formal_parameter(q)==f.c.p*c,"formal chart parameter calibration failed");
        const J doubled=lift.twice(q);
        lab::require(lift.formal_parameter(doubled)==lift.ring.mod(2*f.c.p*c),"formal doubling is not additive modulo p^2");
        ++formal_controls;
    }
    const std::set<I> image(profile.begin(),profile.end());
    const auto& n=lift.counts;
    std::ostringstream out;
    out<<"{\"track\":\"L1\",\"fixture\":"<<lab::json_quote(f.id)
       <<",\"scope\":\"exploratory_toy_diagnostic\",\"outcome\":\"complete_valid\""
       <<",\"p\":"<<f.c.p<<",\"r\":"<<f.r
       <<",\"section\":\"Teichmuller_x_Hensel_y_mod_p_squared\",\"section_calls\":"<<n.section_calls
       <<",\"profiles\":"<<integer_array(profile)<<",\"profile_image_size\":"<<image.size()
       <<",\"hard_lift_labelled_control_profile\":"<<integer_array(hard_profile)
       <<",\"hard_lift_labelled_linearity_checks\":"<<hard_linearity_checks
       <<",\"hard_lift_control_uses_known_scalar_labels\":true"
       <<",\"exact_pair_count\":"<<pairs<<",\"nonzero_additivity_defects\":"<<nonzero
       <<",\"defect_histogram\":"<<integer_array(histogram)
       <<",\"first_nonadditive_pair\":["<<first_i<<','<<first_j<<','<<first_value<<']'
       <<",\"sign_checks\":"<<sign_checks<<",\"formal_doubling_controls\":"<<formal_controls
       <<",\"fixed_public_linear_predictor_hits\":"<<hits<<",\"predictor_slope_nonzero\":"<<(slope!=0?"true":"false")
       <<",\"fixed_public_linear_predictor_nontrivial_hits\":"<<nontrivial_hits
       <<",\"nontrivial_target_count\":"<<f.r-3
       <<",\"label_permutation_count\":99,\"label_permutation_hits\":"<<integer_array(null_hits)
       <<",\"label_permutation_nontrivial_hits\":"<<integer_array(null_nontrivial_hits)
       <<",\"label_permutation_definition\":\"permute sign-pairs and independently orient them, fixing scalar labels 0,+1,-1; preserve exact feature multiset and sign symmetry\""
       <<",\"secondary_unconditional_permutation_count\":99"
       <<",\"secondary_unconditional_permutation_hits\":"<<integer_array(unconditional_hits)
       <<",\"secondary_unconditional_nontrivial_hits\":"<<integer_array(unconditional_nontrivial_hits)
       <<",\"primary_null\":\"matched_sign_pair_permutation\""
       <<",\"orbit_reference_group_additions\":"<<f.r
       <<",\"ring_additions\":"<<n.additions<<",\"ring_multiplications\":"<<n.multiplications
       <<",\"public_section_ring_additions\":"<<public_section_counts.additions
       <<",\"public_section_ring_multiplications\":"<<public_section_counts.multiplications
       <<",\"ring_power_calls\":"<<n.power_calls<<",\"ring_inversions\":"<<n.inversions
       <<",\"projective_doubles\":"<<n.doubles<<",\"projective_adds\":"<<n.adds
       <<",\"projective_curve_checks\":"<<n.projective_checks<<",\"scalar_calls\":"<<n.scalar_calls
       <<",\"independent_affine_reduction_checks\":"<<n.reduction_crosschecks
       <<",\"predictor_definition\":\"D(Q)/D(P) mod p then mod r; constant zero if D(P)=0\""
       <<",\"cost_scope\":\"ring counters include construction and verification; affine crosscheck calls and orbit adds separate; no comparative timing\""
       <<",\"limitations\":[\"single fixed computable section\",\"predictor discovery observations only\",\"hard-lift scalar advice confined to labelled control\",\"no decoder or solver advantage\"]}";
    return out.str();
}

std::string endomorphism_row(const lab::Fixture& f) {
    const auto points=lab::orbit(f);
    U verified=0;
    for(I k=0;k<f.r;++k) {
        lab::require(f.c.neg(points[static_cast<std::size_t>(k)])==points[static_cast<std::size_t>((f.r-k)%f.r)],"negation eigenvalue mismatch");
        lab::require((k*(1+(f.r-1)))%f.r==0,"negation redundant witness mismatch");++verified;
    }
    I beta=0,lambda=-1;U eigenvalue_search=0,automorphism_checks=0,cube_root_candidates=0;
    bool applicable=f.c.a==0&&(f.c.p-1)%3==0;
    if(applicable) {
        for(I z=2;z<f.c.p;++z) {++cube_root_candidates;if(f.c.pow(z,3)==1){beta=z;break;}}
        lab::require(beta!=0,"nontrivial cube root missing in p=1 mod3");
        const lab::Point image{f.c.mod(beta*f.P.x),f.P.y,false};
        lab::require(f.c.valid(image),"j0 endomorphism failed curve membership");
        for(I k=0;k<f.r;++k) {++eigenvalue_search;if(points[static_cast<std::size_t>(k)]==image){lambda=k;break;}}
        if(lambda>=0) {
            lab::require((1+lambda+lambda*lambda)%f.r==0,"j0 eigenvalue polynomial failed");
            for(I k=0;k<f.r;++k) {
                const auto q=points[static_cast<std::size_t>(k)];
                const lab::Point transformed=q.inf?q:lab::Point{f.c.mod(beta*q.x),q.y,false};
                lab::require(transformed==points[static_cast<std::size_t>((lambda*k)%f.r)],"j0 action disagreement");
                lab::require((k*(1+lambda+lambda*lambda))%f.r==0,"j0 redundant relation did not hold for every scalar");
                ++automorphism_checks;
            }
        }
    }
    std::ostringstream out;
    out<<"{\"track\":\"L3\",\"fixture\":"<<lab::json_quote(f.id)
       <<",\"scope\":\"exploratory_toy_diagnostic\",\"outcome\":\"complete_valid\""
       <<",\"p\":"<<f.c.p<<",\"r\":"<<f.r<<",\"negation_verified_targets\":"<<verified
       <<",\"negation_eigenvalue\":"<<f.r-1<<",\"negation_witness_compatible_scalars\":"<<f.r
       <<",\"j0_applicable\":"<<(applicable?"true":"false")<<",\"beta\":"<<beta<<",\"lambda\":"<<lambda
       <<",\"j0_subgroup_stable\":"<<(lambda>=0?"true":"false")
       <<",\"j0_verified_targets\":"<<automorphism_checks<<",\"enumerated_eigenvalue_lookup_probes\":"<<eigenvalue_search
       <<",\"cube_root_candidate_tests\":"<<cube_root_candidates
       <<",\"j0_witness_compatible_scalars\":"<<(lambda>=0?f.r:0)
       <<",\"orbit_reference_group_additions\":"<<f.r
       <<",\"cost_scope\":\"full enumerated reference orbit and lookup charged; no cheap scalar orientation inferred\""
       <<",\"limitations\":[\"known automorphism controls\",\"all witness relations k-independent\",\"new coordinate observable and decoder absent\"]}";
    return out.str();
}

U self_test() {
    U checks=0;
    const auto assert_test=[&](bool condition,const std::string& message){lab::require(condition,message);++checks;};
    for(const lab::Curve c:std::vector<lab::Curve>{{5,0,1},{17,2,2},{23,1,1}}) {
        Lift lift(c);
        const I n=c.p*c.p;
        for(I a=0;a<n;++a) for(I b=0;b<n;++b) {
            // Direct signed multiplication is bounded on these developer fixtures.
            assert_test(lift.ring.mul(a,b)==(a*b)%n,"ring multiplication calibration");
        }
        for(I a=1;a<n;++a) if(a%c.p!=0)
            assert_test(lift.ring.mul(a,lift.ring.inverse(a))==1,"ring inverse calibration");
        for(const auto point:c.points()) if(point.inf||point.y!=0) {
            const auto q=lift.section(point);
            assert_test(lift.reduce(q)==point,"section reduction calibration");
            if(!point.inf) {
                const auto inverse=lift.section(c.neg(point));
                assert_test(q.x==inverse.x&&lift.ring.add(q.y,inverse.y)==0,"Hensel sign calibration");
                assert_test(lift.plus(q,inverse).z==0,"lift inverse addition calibration");
                const auto doubled=lift.twice(q);
                if(doubled.z%c.p!=0) {
                    const I slope=lift.ring.mul(lift.ring.add(lift.ring.mul(3,lift.ring.mul(q.x,q.x)),c.a),lift.ring.inverse(lift.ring.mul(2,q.y)));
                    const I ex=lift.ring.sub(lift.ring.mul(slope,slope),lift.ring.mul(2,q.x));
                    const I ey=lift.ring.sub(lift.ring.mul(slope,lift.ring.sub(q.x,ex)),q.y);
                    const I zi=lift.ring.inverse(doubled.z),z2=lift.ring.mul(zi,zi);
                    assert_test(lift.ring.mul(doubled.x,z2)==ex&&lift.ring.mul(doubled.y,lift.ring.mul(z2,zi))==ey,"independent affine p^2 doubling calibration");
                }
            }
        }
        const auto all=c.points();
        for(const auto a:all) for(const auto b:all) {
            if(a.inf||b.inf||a.y==0||b.y==0||a.x==b.x) continue;
            const auto q=lift.section(a),v=lift.section(b),sum=lift.plus(q,v);
            const I slope=lift.ring.mul(lift.ring.sub(v.y,q.y),lift.ring.inverse(lift.ring.sub(v.x,q.x)));
            const I ex=lift.ring.sub(lift.ring.sub(lift.ring.mul(slope,slope),q.x),v.x);
            const I ey=lift.ring.sub(lift.ring.mul(slope,lift.ring.sub(q.x,ex)),q.y);
            const I zi=lift.ring.inverse(sum.z),z2=lift.ring.mul(zi,zi);
            assert_test(lift.ring.mul(sum.x,z2)==ex&&lift.ring.mul(sum.y,lift.ring.mul(z2,zi))==ey,"independent affine p^2 addition calibration");
        }
        bool rejected=false;
        try{(void)lift.ring.inverse(c.p);}catch(const std::exception&){rejected=true;}
        assert_test(rejected,"nonunit inverse not rejected");
        rejected=false;
        try{lift.check({c.p,c.p,c.p});}catch(const std::exception&){rejected=true;}
        assert_test(rejected,"non-unimodular point not rejected");
    }
    const std::vector<lab::Fixture> fixtures{
        {"dev-p5","special-j0",{5,0,1},{0,1,false},3,6,1},
        {"dev-p17","ordinary",{17,2,2},{5,1,false},19,19,2},
        {"dev-p23","ordinary",{23,1,1},{17,3,false},7,28,3}};
    for(const auto& f:fixtures) {
        lab::certify(f);
        assert_test(profile_row(f).find("complete_valid")!=std::string::npos,"profile developer case failed");
        assert_test(endomorphism_row(f).find("complete_valid")!=std::string::npos,"endomorphism developer case failed");
    }
    return checks;
}
} // namespace pe

int main(int argc,char** argv) {
    try {
        if(argc==2&&std::string(argv[1])=="--self-test") {
            const auto n=pe::self_test();
            std::cout<<"{\"status\":\"pass\",\"scope\":\"development_self_test_only\",\"checks\":"<<n<<"}\n";
            return 0;
        }
        if(argc!=4||std::string(argv[1])!="--run") {
            std::cerr<<"usage: padic-endo --self-test | --run FIXTURES_TSV OUTPUT_JSONL\n";return 2;
        }
        const auto fixtures=lab::read_fixtures(argv[2]);
        std::ofstream out(argv[3],std::ios::out|std::ios::trunc);
        lab::require(static_cast<bool>(out),"cannot open output JSONL");
        for(const auto& f:fixtures) {
            lab::certify(f);
            out<<pe::profile_row(f)<<'\n';out.flush();
            out<<pe::endomorphism_row(f)<<'\n';out.flush();
            lab::require(static_cast<bool>(out),"failed writing output JSONL");
        }
        std::cout<<"{\"status\":\"complete\",\"tracks\":[\"L1\",\"L3\"],\"fixtures\":"<<fixtures.size()<<"}\n";
    } catch(const std::exception& e) {std::cerr<<"ERROR: "<<e.what()<<'\n';return 1;}
    return 0;
}
