// Exact finite lossy-projection observations; no ECDLP decoder or speed claim.
#include "common.hpp"
#include <cmath>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <numeric>

namespace {
using lab::I;
using U = std::uint64_t;
constexpr unsigned null_repetitions = 99;
constexpr I maximum_order = 1023;
constexpr long double tolerance = 1e-12L;

struct Kahan {
    long double sum = 0, correction = 0;
    void add(long double v) {
        const long double adjusted = v-correction;
        const long double next = sum+adjusted;
        correction = (next-sum)-adjusted;
        sum = next;
    }
};

U mix(U z) {
    z = (z^(z>>30))*0xbf58476d1ce4e5b9ULL;
    z = (z^(z>>27))*0x94d049bb133111ebULL;
    return z^(z>>31);
}

U domain_hash(const std::string& name) {
    U h = 14695981039346656037ULL;
    for (char raw : name) { const auto c=static_cast<unsigned char>(raw); h ^= c; h *= 1099511628211ULL; }
    return h;
}

U uniform_below(lab::RNG& rng, U bound) {
    lab::require(bound>0,"zero shuffle bound");
    // Rejection removes modulo bias for an ideal uniform 64-bit source.
    const U threshold = (U{0}-bound)%bound;
    for (;;) { const U value = rng.next(); if(value>=threshold)return value%bound; }
}

void permute(lab::RNG& rng, std::vector<I>& labels) {
    for(std::size_t i=labels.size();i>1;--i)
        std::swap(labels[i-1],labels[static_cast<std::size_t>(uniform_below(rng,static_cast<U>(i)))]);
}

bool negation_invariant(const std::vector<I>& labels) {
    if(labels.size()<3||labels.size()%2==0)return false;
    for(std::size_t k=1;k<labels.size();++k)
        if(labels[k]!=labels[labels.size()-k])return false;
    return true;
}

std::vector<I> permute_sign_pairs(lab::RNG& rng,const std::vector<I>& labels) {
    lab::require(negation_invariant(labels),"sign-pair null requires exact negation invariance");
    const auto half=(labels.size()-1)/2;
    std::vector<I> pair_labels;
    pair_labels.reserve(half);
    for(std::size_t k=1;k<=half;++k)pair_labels.push_back(labels[k]);
    permute(rng,pair_labels);
    std::vector<I> out=labels;
    for(std::size_t k=1;k<=half;++k)out[k]=out[labels.size()-k]=pair_labels[k-1];
    lab::require(out[0]==labels[0]&&negation_invariant(out),"sign-pair null invariant failed");
    return out;
}

void digest_u64(U& h,U value) {
    for(unsigned j=0;j<8;++j) { h^=value&255U; h*=1099511628211ULL; value>>=8; }
}

struct Entropy {
    long double bits = 0;
    long double weighted_support = 0;
    U pairs = 0, conditional_cells = 0, joint_nonzero_cells = 0;
    U checksum = 14695981039346656037ULL;
    unsigned maximum_support = 0;
    std::map<unsigned,U> support_cell_histogram, support_pair_mass;
};

std::vector<long double> clog_table(std::size_t r) {
    std::vector<long double> out(r*r+1,0);
    for(std::size_t i=1;i<out.size();++i)out[i]=static_cast<long double>(i)*std::log2(static_cast<long double>(i));
    return out;
}

Entropy exact_entropy(const std::vector<I>& labels,const std::vector<long double>& clog,
                      bool omit_identity=false,bool retain_support=false) {
    lab::require(labels.size()>=3&&labels.size()<=static_cast<std::size_t>(maximum_order),"unsupported entropy order");
    const auto r=labels.size();
    const I largest=*std::max_element(labels.begin(),labels.end());
    lab::require(largest>=0&&largest<static_cast<I>(r),"bad projection image index");
    const auto d=static_cast<std::size_t>(largest+1);
    std::vector<std::vector<std::size_t>> fibres(d);
    std::vector<unsigned> validation(d,0);
    for(std::size_t i=0;i<r;++i) {
        lab::require(labels[i]>=0&&labels[i]<=largest,"malformed projection label");
        ++validation[static_cast<std::size_t>(labels[i])];
        if(!omit_identity||i!=0)fibres[static_cast<std::size_t>(labels[i])].push_back(i);
    }
    for(unsigned n:validation)lab::require(n>0,"projection labels must be consecutive and occupied");
    lab::require(clog.size()>r*r,"short entropy lookup table");
    const U n=static_cast<U>(r-(omit_identity?1U:0U));
    Entropy out;
    out.pairs=n*n;
    std::vector<unsigned> counts(d,0),touched;
    touched.reserve(d);
    Kahan numerator,weighted_support;
    U counted_pairs=0;
    for(std::size_t a=0;a<d;++a)if(!fibres[a].empty())
        for(std::size_t b=0;b<d;++b)if(!fibres[b].empty()) {
            const U mass=static_cast<U>(fibres[a].size())*static_cast<U>(fibres[b].size());
            numerator.add(clog[static_cast<std::size_t>(mass)]);
            touched.clear();
            for(std::size_t x:fibres[a])for(std::size_t y:fibres[b]) {
                const auto c=static_cast<std::size_t>(labels[(x+y)%r]);
                if(counts[c]++==0)touched.push_back(static_cast<unsigned>(c));
                ++counted_pairs;
            }
            U subtotal=0;
            for(unsigned c:touched) {
                subtotal+=counts[c];
                numerator.add(-clog[counts[c]]);
            }
            lab::require(subtotal==mass,"conditional histogram mass mismatch");
            const auto support=static_cast<unsigned>(touched.size());
            out.joint_nonzero_cells+=static_cast<U>(support);
            ++out.conditional_cells;
            weighted_support.add(static_cast<long double>(mass)*static_cast<long double>(support));
            out.maximum_support=std::max(out.maximum_support,support);
            if(retain_support) {
                ++out.support_cell_histogram[support];out.support_pair_mass[support]+=mass;
                std::sort(touched.begin(),touched.end());
                for(unsigned c:touched) {
                    digest_u64(out.checksum,static_cast<U>(a));digest_u64(out.checksum,static_cast<U>(b));
                    digest_u64(out.checksum,c);digest_u64(out.checksum,counts[c]);
                }
            }
            for(unsigned c:touched)counts[c]=0;
        }
    lab::require(counted_pairs==out.pairs,"total histogram mass mismatch");
    out.bits=numerator.sum/static_cast<long double>(out.pairs);
    if(out.bits<0&&out.bits>-tolerance)out.bits=0;
    out.weighted_support=weighted_support.sum/static_cast<long double>(out.pairs);
    lab::require(std::isfinite(out.bits)&&out.bits>=0&&out.bits<=std::log2(static_cast<long double>(d))+tolerance,"invalid exact entropy");
    return out;
}

struct Projection {
    std::string name;
    std::vector<I> labels,raw_dictionary;
    U field_exponentiations=0;
};

// Independent slow contingency-map reference used only in development tests.
long double slow_entropy(const std::vector<I>& labels,bool wrong_sum=false) {
    std::map<std::pair<I,I>,U> margins;
    std::map<std::tuple<I,I,I>,U> joint;
    const auto r=labels.size();
    for(std::size_t x=0;x<r;++x)for(std::size_t y=0;y<r;++y) {
        const I a=labels[x],b=labels[y],c=labels[wrong_sum?x:(x+y)%r];
        ++margins[{a,b}];++joint[{a,b,c}];
    }
    long double answer=0;
    for(const auto& [key,count]:joint) {
        const auto [a,b,c]=key;(void)c;
        const auto mass=margins.at({a,b});
        answer-=static_cast<long double>(count)/static_cast<long double>(r*r)*
            std::log2(static_cast<long double>(count)/static_cast<long double>(mass));
    }
    return answer;
}

Projection compress(std::string name,const std::vector<I>& raw,U exponentiations=0) {
    Projection out;
    out.name=std::move(name);out.raw_dictionary=raw;
    std::sort(out.raw_dictionary.begin(),out.raw_dictionary.end());
    out.raw_dictionary.erase(std::unique(out.raw_dictionary.begin(),out.raw_dictionary.end()),out.raw_dictionary.end());
    out.labels.reserve(raw.size());
    for(I label:raw)out.labels.push_back(static_cast<I>(std::lower_bound(out.raw_dictionary.begin(),out.raw_dictionary.end(),label)-out.raw_dictionary.begin()));
    out.field_exponentiations=exponentiations;
    return out;
}

std::vector<Projection> projections(const lab::Fixture& f,const std::vector<lab::Point>& orbit) {
    std::vector<Projection> out;
    const auto append=[&](const std::string& name,const auto& value,U powers=0) {
        std::vector<I> raw;raw.reserve(orbit.size());
        for(const auto point:orbit)raw.push_back(value(point));
        out.push_back(compress(name,raw,powers));
    };
    append("full_point",[&](lab::Point q){return q.inf?I{0}:1+q.x*f.c.p+q.y;});
    append("constant",[](lab::Point){return I{0};});
    append("kummer_x",[](lab::Point q){return q.inf?I{0}:q.x+1;});
    U nonzero_x=0;for(auto q:orbit)if(!q.inf&&q.x!=0)++nonzero_x;
    append("quadratic_character_x",[&](lab::Point q){if(q.inf)return I{0};if(q.x==0)return I{1};return f.c.pow(q.x,(f.c.p-1)/2)==1?I{2}:I{3};},nonzero_x);
    for(I power:{3,5,7})if((f.c.p-1)%power==0)
        append("power_residue_"+std::to_string(power),[&](lab::Point q){if(q.inf)return I{0};if(q.x==0)return I{1};return f.c.pow(q.x,(f.c.p-1)/power)+1;},nonzero_x);
    const unsigned width=lab::bits(static_cast<U>(f.c.p-1));
    for(unsigned t:{1U,2U,4U,8U}) {
        append("top_x_"+std::to_string(t),[&](lab::Point q){return q.inf?I{0}:(q.x>>(width>t?width-t:0))+1;});
        append("bottom_x_"+std::to_string(t),[&](lab::Point q){return q.inf?I{0}:(q.x&static_cast<I>((U{1}<<t)-1))+1;});
    }
    for(I modulus:{3,5,7,11})append("x_mod_"+std::to_string(modulus),[&](lab::Point q){return q.inf?I{0}:q.x%modulus+1;});
    for(U buckets:{16U,32U,64U})append("rho_partition_"+std::to_string(buckets),[&](lab::Point q){return q.inf?I{0}:static_cast<I>(mix(static_cast<U>(1+q.x*f.c.p+q.y)^f.seed)%buckets)+1;});
    return out;
}

void write_array(std::ostream& out,const std::vector<I>& values) {
    out<<'[';for(std::size_t i=0;i<values.size();++i){if(i)out<<',';out<<values[i];}out<<']';
}

void write_map(std::ostream& out,const std::map<unsigned,U>& values) {
    out<<'[';bool first=true;for(const auto& [value,count]:values){if(!first)out<<',';first=false;out<<'['<<value<<','<<count<<']';}out<<']';
}

void emit_projection(std::ostream& out,const lab::Fixture& f,const Projection& p,
                     const std::vector<long double>& clog) {
    const Entropy observed=exact_entropy(p.labels,clog,false,true);
    std::vector<unsigned> fibre_sizes(p.raw_dictionary.size(),0);
    for(I label:p.labels)++fibre_sizes[static_cast<std::size_t>(label)];
    const U seed=f.seed^domain_hash("L9.null.v1/"+f.id+"/"+p.name);
    lab::RNG rng(seed);
    std::vector<long double> null_values;
    null_values.reserve(null_repetitions);
    Kahan null_sum;
    U null_pairs=0,null_conditional_cells=0,null_joint_cells=0;
    for(unsigned repetition=0;repetition<null_repetitions;++repetition) {
        std::vector<I> shuffled=p.labels;
        permute(rng,shuffled);
        std::vector<unsigned> actual(fibre_sizes.size(),0);
        for(I label:shuffled)++actual[static_cast<std::size_t>(label)];
        lab::require(actual==fibre_sizes,"null permutation changed fibre profile");
        const Entropy e=exact_entropy(shuffled,clog);
        null_values.push_back(e.bits);null_sum.add(e.bits);
        null_pairs+=e.pairs;null_conditional_cells+=e.conditional_cells;null_joint_cells+=e.joint_nonzero_cells;
    }
    const long double mean=null_sum.sum/static_cast<long double>(null_values.size());
    Kahan squared;
    for(long double v:null_values)squared.add((v-mean)*(v-mean));
    const long double sd=std::sqrt(squared.sum/static_cast<long double>(null_values.size()-1));
    const bool matched_applicable=negation_invariant(p.labels);
    const U matched_seed=f.seed^domain_hash("L9.sign-pair-null.v1/"+f.id+"/"+p.name);
    std::vector<long double> matched_values;
    Kahan matched_sum,matched_squared;
    U matched_pairs=0,matched_conditional_cells=0,matched_joint_cells=0;
    long double matched_mean=0,matched_sd=0;
    if(matched_applicable) {
        lab::RNG matched_rng(matched_seed);
        matched_values.reserve(null_repetitions);
        for(unsigned repetition=0;repetition<null_repetitions;++repetition) {
            const auto shuffled=permute_sign_pairs(matched_rng,p.labels);
            std::vector<unsigned> actual(fibre_sizes.size(),0);
            for(I label:shuffled)++actual[static_cast<std::size_t>(label)];
            lab::require(actual==fibre_sizes,"sign-pair null changed point fibre profile");
            const Entropy e=exact_entropy(shuffled,clog);
            matched_values.push_back(e.bits);matched_sum.add(e.bits);
            matched_pairs+=e.pairs;matched_conditional_cells+=e.conditional_cells;matched_joint_cells+=e.joint_nonzero_cells;
            if(p.name=="kummer_x")lab::require(std::abs(e.bits-observed.bits)<tolerance,"Kummer sign-pair null must preserve entropy");
        }
        matched_mean=matched_sum.sum/static_cast<long double>(matched_values.size());
        for(long double value:matched_values)matched_squared.add((value-matched_mean)*(value-matched_mean));
        matched_sd=std::sqrt(matched_squared.sum/static_cast<long double>(matched_values.size()-1));
    }
    long double conditional_nonidentity=-1;
    U calibration_pairs=0;
    if(p.name=="constant"||p.name=="full_point")lab::require(std::abs(observed.bits)<tolerance,"zero-entropy calibration failed");
    if(p.name=="kummer_x") {
        const long double expected=static_cast<long double>((f.r-1)*(f.r-1))/static_cast<long double>(f.r*f.r);
        lab::require(std::abs(observed.bits-expected)<tolerance,"finite-r Kummer calibration failed");
        const Entropy restricted=exact_entropy(p.labels,clog,true);
        conditional_nonidentity=restricted.bits;calibration_pairs=restricted.pairs;
        lab::require(std::abs(restricted.bits-1)<tolerance,"nonidentity Kummer calibration failed");
    }
    out<<std::setprecision(18)<<"{\"track\":\"L9\",\"fixture\":"<<lab::json_quote(f.id)
       <<",\"stratum\":"<<lab::json_quote(f.stratum)<<",\"scope\":\"exploratory_toy_diagnostic\",\"outcome\":\"complete_valid\",\"projection\":"<<lab::json_quote(p.name)
       <<",\"p\":"<<f.c.p<<",\"r\":"<<f.r<<",\"image_size\":"<<fibre_sizes.size()<<",\"entropy_bits\":"<<observed.bits
       <<",\"entropy_method\":\"exact integer full-pair histogram; long-double log2 with compensated accumulation\""
       <<",\"weighted_candidate_support\":"<<observed.weighted_support<<",\"maximum_candidate_support\":"<<observed.maximum_support
       <<",\"conditional_cells\":"<<observed.conditional_cells<<",\"joint_nonzero_cells\":"<<observed.joint_nonzero_cells
       <<",\"support_cell_histogram\":";write_map(out,observed.support_cell_histogram);
    out<<",\"support_pair_mass\":";write_map(out,observed.support_pair_mass);
    out<<",\"projection_labels\":";write_array(out,p.labels);
    out<<",\"raw_label_dictionary\":";write_array(out,p.raw_dictionary);
    out<<",\"fibre_sizes\":[";for(std::size_t i=0;i<fibre_sizes.size();++i){if(i)out<<',';out<<fibre_sizes[i];}out<<']';
    out<<",\"joint_histogram_fnv64_not_cryptographic\":"<<lab::json_quote(std::to_string(observed.checksum))
       <<",\"null_repetitions\":"<<null_repetitions<<",\"null_seed\":"<<lab::json_quote(std::to_string(seed))
       <<",\"null_generator\":\"SplitMix64; rejection-bounded Fisher-Yates; each shuffle starts with original labels; generator state continues across repetitions\""
       <<",\"null_entropy_bits\":[";
    for(std::size_t i=0;i<null_values.size();++i){if(i)out<<',';out<<null_values[i];}out<<']';
    out<<",\"null_mean_bits\":"<<mean<<",\"null_sample_sd_bits\":"<<sd<<",\"null_mean_mc_standard_error_bits\":"<<sd/std::sqrt(static_cast<long double>(null_values.size()))
       <<",\"null_min_bits\":"<<*std::min_element(null_values.begin(),null_values.end())<<",\"null_max_bits\":"<<*std::max_element(null_values.begin(),null_values.end())
       <<",\"observed_minus_null_mean_bits\":"<<observed.bits-mean
       <<",\"unconditional_null_is_secondary_for_negation_invariant_projection\":"<<(matched_applicable?"true":"false")
       <<",\"negation_invariant\":"<<(matched_applicable?"true":"false")
       <<",\"matched_null_applicable\":"<<(matched_applicable?"true":"false")
       <<",\"matched_null_repetitions\":"<<(matched_applicable?null_repetitions:0U)
       <<",\"primary_reference_kind\":"<<lab::json_quote(matched_applicable?"sign_pair_matched_null":"unconditional_relabeling_null");
    if(matched_applicable) {
        out<<",\"matched_null_seed\":"<<lab::json_quote(std::to_string(matched_seed))
           <<",\"matched_null_generator\":\"SplitMix64; rejection-bounded Fisher-Yates on nonzero sign-pair labels; identity fixed; each shuffle starts with original pair labels; state continues across repetitions\""
           <<",\"matched_null_entropy_bits\":[";
        for(std::size_t i=0;i<matched_values.size();++i){if(i)out<<',';out<<matched_values[i];}out<<']';
        out<<",\"matched_null_mean_bits\":"<<matched_mean<<",\"matched_null_sample_sd_bits\":"<<matched_sd
           <<",\"matched_null_mean_mc_standard_error_bits\":"<<matched_sd/std::sqrt(static_cast<long double>(matched_values.size()))
           <<",\"matched_null_min_bits\":"<<*std::min_element(matched_values.begin(),matched_values.end())
           <<",\"matched_null_max_bits\":"<<*std::max_element(matched_values.begin(),matched_values.end())
           <<",\"observed_minus_matched_null_mean_bits\":"<<observed.bits-matched_mean
           <<",\"primary_observed_minus_reference_mean_bits\":"<<observed.bits-matched_mean;
    } else {
        out<<",\"matched_null_entropy_bits\":[],\"matched_null_mean_bits\":null,\"matched_null_unavailable_reason\":\"projection is not negation invariant on this entire subgroup\""
           <<",\"primary_observed_minus_reference_mean_bits\":"<<observed.bits-mean;
    }
    out
       <<",\"observed_pair_visits\":"<<observed.pairs<<",\"null_pair_visits\":"<<null_pairs<<",\"calibration_pair_visits\":"<<calibration_pairs
       <<",\"matched_null_pair_visits\":"<<matched_pairs
       <<",\"total_pair_visits\":"<<observed.pairs+null_pairs+matched_pairs+calibration_pairs
       <<",\"null_conditional_cells_total\":"<<null_conditional_cells<<",\"null_joint_nonzero_cells_total\":"<<null_joint_cells
       <<",\"matched_null_conditional_cells_total\":"<<matched_conditional_cells<<",\"matched_null_joint_nonzero_cells_total\":"<<matched_joint_cells
       <<",\"projection_evaluations\":"<<f.r<<",\"projection_field_exponentiations\":"<<p.field_exponentiations
       <<",\"entropy_clog_lookup_entries\":"<<clog.size()<<",\"entropy_clog_lookup_storage_bytes\":"<<clog.size()*sizeof(long double)
       <<",\"setup_group_additions_for_shared_orbit\":"<<f.r
       <<",\"orbit_setup_reuse\":\"shared by projection panel; scalar labels used only for exact enumerative observation, not an inverse algorithm\""
       <<",\"missing_constructor\":\"no propagation or scalar-recovery decoder is supplied\"";
    if(conditional_nonidentity>=0)out<<",\"nonidentity_conditioned_entropy_bits\":"<<conditional_nonidentity;
    out<<"}\n";
}

void run(const std::string& fixture_file,const std::string& output_file) {
    const auto fixtures=lab::read_fixtures(fixture_file);
    for(const auto& f:fixtures)lab::require(f.r<=maximum_order,"L9 exact-panel registered envelope is r<=1023");
    lab::require(!std::ifstream(output_file).good(),"refusing to overwrite existing L9 output");
    std::ofstream out(output_file);lab::require(static_cast<bool>(out),"cannot create L9 output");
    U rows=0;
    for(const auto& f:fixtures) {
        const auto points=lab::orbit(f);
        const auto log_table=clog_table(points.size());
        for(const auto& p:projections(f,points)){emit_projection(out,f,p,log_table);++rows;}
        for(I d:{3,5,7})if((f.c.p-1)%d!=0) {
            out<<"{\"track\":\"L9\",\"fixture\":"<<lab::json_quote(f.id)<<",\"scope\":\"exploratory_toy_diagnostic\",\"projection\":\"power_residue_"<<d<<"\",\"outcome\":\"not_applicable\",\"reason\":\"d does not divide p-1\"}\n";++rows;
        }
        out.flush();lab::require(static_cast<bool>(out),"L9 output write failed");
        std::cerr<<"L9 completed fixture "<<f.id<<" r="<<f.r<<"\n";
    }
    std::cout<<"L9 complete rows="<<rows<<" null_repetitions="<<null_repetitions<<" exact_full_pair_enumeration=true; no scalar-recovery algorithm\n";
}

void self_test() {
    U checks=0;
    const auto check=[&](bool good,const std::string& message){++checks;lab::require(good,message);};
    for(I order:{3,5,7,11,19,31}) {
        const auto r=static_cast<std::size_t>(order);
        const auto table=clog_table(r);
        std::vector<I> constant(r,0),injective(r),kummer(r);
        for(I k=0;k<order;++k){injective[static_cast<std::size_t>(k)]=k;kummer[static_cast<std::size_t>(k)]=std::min(k,order-k);}
        const auto a=exact_entropy(constant,table,false,true),b=exact_entropy(injective,table,false,true),c=exact_entropy(kummer,table,false,true);
        const long double expected=static_cast<long double>((order-1)*(order-1))/static_cast<long double>(order*order);
        check(std::abs(a.bits)<tolerance,"constant reference");check(std::abs(b.bits)<tolerance,"injective reference");
        check(std::abs(c.bits-expected)<tolerance,"Kummer finite-r reference");
        check(std::abs(exact_entropy(kummer,table,true).bits-1)<tolerance,"Kummer nonidentity reference");
        check(a.maximum_support==1&&b.maximum_support==1&&c.maximum_support==2,"support references");
        check(c.pairs==static_cast<U>(order*order),"pair accounting");
        check(std::abs(c.bits-1)>tolerance,"intentionally wrong one-bit calibration must be rejected");
        lab::RNG rng(47);auto shuffled=kummer;permute(rng,shuffled);
        auto left=kummer,right=shuffled;std::sort(left.begin(),left.end());std::sort(right.begin(),right.end());
        check(left==right,"shuffle must preserve exact fibres");
        check(exact_entropy(shuffled,table).pairs==static_cast<U>(order*order),"shuffle accounting");
        check(std::abs(exact_entropy(shuffled,table).bits-slow_entropy(shuffled))<tolerance,"independent shuffled contingency reference");
        check(std::abs(slow_entropy(kummer,true)-expected)>tolerance,"wrong group-sum rule must fail Kummer calibration");
        check(negation_invariant(kummer)&&negation_invariant(constant),"sign-invariant controls recognized");
        check(!negation_invariant(injective),"injective point labels are not negation invariant");
        for(unsigned repetition=0;repetition<5;++repetition) {
            const auto matched=permute_sign_pairs(rng,kummer);
            check(matched[0]==kummer[0]&&negation_invariant(matched),"matched null fixes identity and sign pairs");
            auto sorted=matched;std::sort(sorted.begin(),sorted.end());
            check(sorted==left,"matched null preserves full feature multiset");
            check(std::abs(exact_entropy(matched,table).bits-c.bits)<tolerance,"Kummer matched-null entropy is unchanged");
        }
    }
    bool malformed=false;
    try{(void)exact_entropy({0,-1,1},clog_table(3));}catch(const std::exception&){malformed=true;}
    check(malformed,"negative label rejection");
    malformed=false;
    try{(void)exact_entropy({0,2,2},clog_table(3));}catch(const std::exception&){malformed=true;}
    check(malformed,"missing image label rejection");
    malformed=false;
    try{lab::RNG rng(1);(void)permute_sign_pairs(rng,{0,1,2});}catch(const std::exception&){malformed=true;}
    check(malformed,"non-invariant sign-pair null rejection");
    lab::Fixture f;f.id="development-p17";f.stratum="main";f.c={17,2,2};f.P={5,1,false};f.r=19;f.N=19;f.seed=7;
    lab::certify(f);
    const auto ec_orbit=lab::orbit(f);
    for(std::size_t i=0;i<ec_orbit.size();++i)for(std::size_t j=0;j<ec_orbit.size();++j)
        check(f.c.add(ec_orbit[i],ec_orbit[j])==ec_orbit[(i+j)%ec_orbit.size()],"EC pair addition versus cyclic label reference");
    const auto panel=projections(f,ec_orbit);
    check(panel.size()==19,"p17 available projection count");
    bool saw_kummer=false;
    for(const auto& p:panel) {
        const auto observed=exact_entropy(p.labels,clog_table(19));
        check(observed.pairs==361,"EC projection pair count");
        check(std::abs(observed.bits-slow_entropy(p.labels))<tolerance,"independent EC contingency reference");
        if(p.name=="kummer_x") {saw_kummer=true;check(std::abs(observed.bits-324.0L/361.0L)<tolerance,"actual EC Kummer correction");}
    }
    check(saw_kummer,"EC Kummer exists");
    std::ostringstream row;emit_projection(row,f,panel[2],clog_table(19));
    check(row.str().find("\"null_repetitions\":99")!=std::string::npos,"all null outcomes serialized");
    check(row.str().find("\"nonidentity_conditioned_entropy_bits\":1")!=std::string::npos,"conditional calibration serialized");
    check(row.str().find("\"matched_null_repetitions\":99")!=std::string::npos,"all sign-pair null outcomes serialized");
    std::cout<<"L9 SELF_TEST_PASS checks="<<checks<<" null_repetitions="<<null_repetitions<<"; exact toy entropy calibration only\n";
}
}

int main(int argc,char** argv) {
    try {
        if(argc==2&&std::string(argv[1])=="--self-test"){self_test();return 0;}
        if(argc==4&&std::string(argv[1])=="--run"){run(argv[2],argv[3]);return 0;}
        std::cerr<<"usage: lossy --self-test | --run FIXTURES_TSV OUTPUT_JSONL\n";return 2;
    }catch(const std::exception& e){std::cerr<<"L9 ERROR "<<e.what()<<'\n';return 1;}
}
