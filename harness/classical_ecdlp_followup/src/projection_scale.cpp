// Exact finite coordinate observations and declared nulls; no scalar decoder.
#include "common.hpp"
#include <array>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <numeric>
#include <set>

namespace ps {
using lab::I;
using U=std::uint64_t;
constexpr I maximum_order=8191;
constexpr unsigned repetitions=99;
constexpr long double tolerance=1e-12L;
constexpr std::size_t row_limit=60*1024;

struct Kahan {
    long double sum=0,correction=0;
    void add(long double v){const long double y=v-correction,t=sum+y;correction=(t-sum)-y;sum=t;}
};
U mix(U z){z=(z^(z>>30))*0xbf58476d1ce4e5b9ULL;z=(z^(z>>27))*0x94d049bb133111ebULL;return z^(z>>31);}
U domain_hash(const std::string& name){U h=14695981039346656037ULL;for(char raw:name){h^=static_cast<unsigned char>(raw);h*=1099511628211ULL;}return h;}
void digest(U& h,U value){for(unsigned i=0;i<8;++i){h^=value&255U;h*=1099511628211ULL;value>>=8;}}
void shuffle(lab::RNG& rng,std::vector<I>& labels){for(std::size_t i=labels.size();i>1;--i)std::swap(labels[i-1],labels[static_cast<std::size_t>(rng.bounded(static_cast<U>(i)))]);}
bool sign_invariant(const std::vector<I>& labels){if(labels.size()<3||labels.size()%2==0)return false;for(std::size_t i=1;i<labels.size();++i)if(labels[i]!=labels[labels.size()-i])return false;return true;}
std::vector<I> sign_shuffle(lab::RNG& rng,const std::vector<I>& labels){
    lab::require(sign_invariant(labels),"sign-pair null requires negation-invariant labels");
    const auto half=(labels.size()-1)/2;std::vector<I> pairs(labels.begin()+1,labels.begin()+1+static_cast<std::ptrdiff_t>(half));shuffle(rng,pairs);
    auto out=labels;for(std::size_t i=1;i<=half;++i)out[i]=out[labels.size()-i]=pairs[i-1];
    lab::require(out[0]==labels[0]&&sign_invariant(out),"sign-pair invariant failed");return out;
}
std::vector<unsigned> fibre_profile(const std::vector<I>& labels){
    lab::require(labels.size()>=3&&labels.size()<=static_cast<std::size_t>(maximum_order),"unsupported registered subgroup order");
    const I largest=*std::max_element(labels.begin(),labels.end());lab::require(largest>=0&&largest<static_cast<I>(labels.size()),"bad image label");
    std::vector<unsigned> out(static_cast<std::size_t>(largest+1),0);
    for(I x:labels){lab::require(x>=0&&x<=largest,"negative/out-of-range image label");++out[static_cast<std::size_t>(x)];}
    for(unsigned n:out)lab::require(n!=0,"labels must be consecutive and occupied");
    return out;
}
std::vector<long double> clog_table(std::size_t maximum_mass){
    std::vector<long double> out(maximum_mass+1,0);for(std::size_t i=1;i<out.size();++i)out[i]=static_cast<long double>(i)*std::log2(static_cast<long double>(i));return out;
}
struct Entropy {
    long double bits=0,weighted_support=0;
    U population=0,visits=0,conditional_cells=0,joint_nonzero=0,checksum=14695981039346656037ULL;
    unsigned maximum_support=0;
    std::map<unsigned,U> support_cells,support_mass;
};
// Integer frequencies of histogram counts avoid floating summation in hot loops.
long double histogram_entropy(const std::vector<U>& margins,const std::vector<U>& joint,const std::vector<long double>& clog,U population){
    lab::require(margins.size()==joint.size()&&clog.size()>=margins.size(),"entropy table size mismatch");
    Kahan sum;U marginal_mass=0,joint_mass=0;
    for(std::size_t c=1;c<margins.size();++c){
        marginal_mass+=static_cast<U>(c)*margins[c];joint_mass+=static_cast<U>(c)*joint[c];
        if(margins[c]!=joint[c])sum.add((static_cast<long double>(margins[c])-static_cast<long double>(joint[c]))*clog[c]);
    }
    lab::require(marginal_mass==population&&joint_mass==population,"histogram population mismatch");
    long double answer=sum.sum/static_cast<long double>(population);if(answer<0&&answer>-tolerance)answer=0;return answer;
}
Entropy exact_pair(const std::vector<I>& labels,const std::vector<long double>& clog,bool omit_identity=false,bool retain=false){
    const auto profile=fibre_profile(labels);const auto r=labels.size(),d=profile.size();
    std::vector<std::vector<std::size_t>> fibres(d);
    for(std::size_t k=0;k<r;++k)if(!omit_identity||k!=0)fibres[static_cast<std::size_t>(labels[k])].push_back(k);
    std::size_t largest=0;for(const auto& f:fibres)largest=std::max(largest,f.size());
    const auto capacity=largest*largest;lab::require(clog.size()>capacity,"pair log table too short");
    std::vector<U> margins(capacity+1,0),joint(capacity+1,0);std::vector<unsigned> counts(d,0),touched;touched.reserve(d);
    Entropy out;const U n=static_cast<U>(r-(omit_identity?1U:0U));out.population=n*n;U weighted=0;
    for(std::size_t a=0;a<d;++a)if(!fibres[a].empty())for(std::size_t b=0;b<d;++b)if(!fibres[b].empty()){
        const auto mass=fibres[a].size()*fibres[b].size();++margins[mass];touched.clear();
        for(std::size_t x:fibres[a])for(std::size_t y:fibres[b]){
            std::size_t sum=x+y;if(sum>=r)sum-=r;const auto c=static_cast<std::size_t>(labels[sum]);
            if(counts[c]++==0)touched.push_back(static_cast<unsigned>(c));
            ++out.visits;
        }
        U subtotal=0;for(unsigned c:touched){subtotal+=counts[c];++joint[counts[c]];}
        lab::require(subtotal==mass,"pair conditional mass mismatch");
        const auto support=static_cast<unsigned>(touched.size());++out.conditional_cells;out.joint_nonzero+=support;
        weighted+=static_cast<U>(mass)*support;out.maximum_support=std::max(out.maximum_support,support);
        if(retain){++out.support_cells[support];out.support_mass[support]+=static_cast<U>(mass);std::sort(touched.begin(),touched.end());for(unsigned c:touched){digest(out.checksum,a);digest(out.checksum,b);digest(out.checksum,c);digest(out.checksum,counts[c]);}}
        for(unsigned c:touched)counts[c]=0;
    }
    lab::require(out.visits==out.population,"pair visits mismatch");out.bits=histogram_entropy(margins,joint,clog,out.population);
    out.weighted_support=static_cast<long double>(weighted)/static_cast<long double>(out.population);
    lab::require(std::isfinite(out.bits)&&out.bits>=0&&out.bits<=std::log2(static_cast<long double>(d))+tolerance,"invalid pair entropy");return out;
}
Entropy exact_unary(const std::vector<I>& labels,const std::vector<long double>& clog,unsigned bit,bool retain=false){
    lab::require(bit<=1,"bad transition bit");const auto profile=fibre_profile(labels);const auto r=labels.size(),d=profile.size();
    const auto largest=static_cast<std::size_t>(*std::max_element(profile.begin(),profile.end()));lab::require(clog.size()>largest,"unary log table too short");
    std::vector<std::vector<std::size_t>> fibres(d);for(std::size_t k=0;k<r;++k)fibres[static_cast<std::size_t>(labels[k])].push_back(k);
    std::vector<U> margins(largest+1,0),joint(largest+1,0);std::vector<unsigned> counts(d,0),touched;touched.reserve(d);Entropy out;out.population=static_cast<U>(r);U weighted=0;
    for(std::size_t a=0;a<d;++a){const auto mass=fibres[a].size();++margins[mass];touched.clear();
        for(std::size_t k:fibres[a]){std::size_t target=2*k+bit;if(target>=r)target-=r;const auto c=static_cast<std::size_t>(labels[target]);if(counts[c]++==0)touched.push_back(static_cast<unsigned>(c));++out.visits;}
        U subtotal=0;for(unsigned c:touched){subtotal+=counts[c];++joint[counts[c]];}lab::require(subtotal==mass,"unary conditional mass mismatch");
        const auto support=static_cast<unsigned>(touched.size());++out.conditional_cells;out.joint_nonzero+=support;weighted+=static_cast<U>(mass)*support;out.maximum_support=std::max(out.maximum_support,support);
        if(retain){++out.support_cells[support];out.support_mass[support]+=static_cast<U>(mass);std::sort(touched.begin(),touched.end());for(unsigned c:touched){digest(out.checksum,a);digest(out.checksum,c);digest(out.checksum,counts[c]);}}
        for(unsigned c:touched)counts[c]=0;
    }
    lab::require(out.visits==out.population,"unary visits mismatch");out.bits=histogram_entropy(margins,joint,clog,out.population);out.weighted_support=static_cast<long double>(weighted)/static_cast<long double>(out.population);
    lab::require(std::isfinite(out.bits)&&out.bits>=0&&out.bits<=std::log2(static_cast<long double>(d))+tolerance,"invalid unary entropy");return out;
}
// Separate small contingency-map references are development checks only.
long double slow_pair(const std::vector<I>& labels,bool wrong_sum=false){
    std::map<std::pair<I,I>,U> margins;std::map<std::tuple<I,I,I>,U> joint;const auto r=labels.size();
    for(std::size_t i=0;i<r;++i)for(std::size_t j=0;j<r;++j){const auto a=labels[i],b=labels[j],c=labels[wrong_sum?i:(i+j)%r];++margins[{a,b}];++joint[{a,b,c}];}
    Kahan sum;for(const auto& [key,n]:joint){const auto [a,b,c]=key;(void)c;sum.add(-static_cast<long double>(n)/static_cast<long double>(r*r)*std::log2(static_cast<long double>(n)/static_cast<long double>(margins.at({a,b}))));}return sum.sum;
}
long double slow_unary(const std::vector<I>& labels,unsigned bit){
    std::map<I,U> margins;std::map<std::pair<I,I>,U> joint;const auto r=labels.size();for(std::size_t i=0;i<r;++i){++margins[labels[i]];++joint[{labels[i],labels[(2*i+bit)%r]}];}
    Kahan sum;for(const auto& [key,n]:joint)sum.add(-static_cast<long double>(n)/static_cast<long double>(r)*std::log2(static_cast<long double>(n)/static_cast<long double>(margins.at(key.first))));return sum.sum;
}
std::string b64_u16(const std::vector<I>& values){
    static constexpr char alphabet[]="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";std::vector<unsigned char> bytes;bytes.reserve(2*values.size());
    for(I v:values){lab::require(v>=0&&v<=65535,"u16 codec range");const auto n=static_cast<U>(v);bytes.push_back(static_cast<unsigned char>(n&255U));bytes.push_back(static_cast<unsigned char>(n>>8));}
    std::string out;out.reserve(4*((bytes.size()+2)/3));for(std::size_t i=0;i<bytes.size();i+=3){const U a=bytes[i],b=i+1<bytes.size()?bytes[i+1]:0,c=i+2<bytes.size()?bytes[i+2]:0;const U word=(a<<16)|(b<<8)|c;out+=alphabet[(word>>18)&63U];out+=alphabet[(word>>12)&63U];out+=i+1<bytes.size()?alphabet[(word>>6)&63U]:'=';out+=i+2<bytes.size()?alphabet[word&63U]:'=';}return out;
}
std::vector<I> unb64_u16(const std::string& s){
    const std::string alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";lab::require(s.size()%4==0,"bad base64 length");std::vector<unsigned char> bytes;
    for(std::size_t i=0;i<s.size();i+=4){std::array<U,4> digit{};unsigned padding=0;for(unsigned j=0;j<4;++j){const char c=s[i+j];if(c=='='){++padding;lab::require(i+4==s.size()&&j>=2,"bad base64 padding");}else{lab::require(padding==0,"data after padding");const auto where=alphabet.find(c);lab::require(where!=std::string::npos,"bad base64 symbol");digit[j]=static_cast<U>(where);}}lab::require(padding<=2,"too much base64 padding");const U word=(digit[0]<<18)|(digit[1]<<12)|(digit[2]<<6)|digit[3];bytes.push_back(static_cast<unsigned char>((word>>16)&255U));if(padding<2)bytes.push_back(static_cast<unsigned char>((word>>8)&255U));if(padding<1)bytes.push_back(static_cast<unsigned char>(word&255U));}
    lab::require(bytes.size()%2==0,"odd u16 byte count");std::vector<I> out;for(std::size_t i=0;i<bytes.size();i+=2)out.push_back(static_cast<I>(bytes[i])+256*static_cast<I>(bytes[i+1]));return out;
}
struct Projection {std::string name;std::vector<I> labels,dictionary;U field_powers=0;};
Projection compress(std::string name,const std::vector<I>& raw,U powers=0){Projection p;p.name=std::move(name);p.dictionary=raw;std::sort(p.dictionary.begin(),p.dictionary.end());p.dictionary.erase(std::unique(p.dictionary.begin(),p.dictionary.end()),p.dictionary.end());p.labels.reserve(raw.size());for(I v:raw)p.labels.push_back(static_cast<I>(std::lower_bound(p.dictionary.begin(),p.dictionary.end(),v)-p.dictionary.begin()));p.field_powers=powers;return p;}
Projection make_projection(const lab::Fixture& f,const std::vector<lab::Point>& points,const std::string& name){
    std::vector<I> raw;raw.reserve(points.size());U powers=0;const U hash_seed=f.seed^domain_hash("L9.scale.xhash7.v1");
    for(auto q:points){I v=0;if(name=="constant")v=0;else if(q.inf)v=0;else if(name=="full_point")v=1+q.x*f.c.p+q.y;else if(name=="kummer_x")v=q.x+1;else if(name=="x_mod_7")v=q.x%7+1;else if(name=="power_residue_5"){lab::require((f.c.p-1)%5==0,"unavailable fifth-power residue");if(q.x==0)v=1;else{v=f.c.pow(q.x,(f.c.p-1)/5)+1;++powers;}}else if(name=="x_hash_7")v=static_cast<I>(mix(static_cast<U>(q.x)^hash_seed)%7)+1;else throw std::runtime_error("unknown projection");raw.push_back(v);}
    return compress(name,raw,powers);
}
void write_map(std::ostream& out,const std::map<unsigned,U>& m){out<<'[';bool first=true;for(const auto& [a,b]:m){if(!first)out<<',';first=false;out<<'['<<a<<','<<b<<']';}out<<']';}
void write_rle(std::ostream& out,const std::vector<unsigned>& v){out<<'[';bool first=true;for(std::size_t i=0;i<v.size();){std::size_t j=i+1;while(j<v.size()&&v[j]==v[i])++j;if(!first)out<<',';first=false;out<<'['<<v[i]<<','<<j-i<<']';i=j;}out<<']';}
void write_values(std::ostream& out,const std::vector<long double>& v){out<<'[';for(std::size_t i=0;i<v.size();++i){if(i)out<<',';out<<v[i];}out<<']';}
struct Summary {long double mean=0,sd=0,minimum=0,maximum=0;};
Summary summarize(const std::vector<long double>& v){lab::require(v.size()>=2,"short null ensemble");Summary s;Kahan sum,sq;for(long double x:v)sum.add(x);s.mean=sum.sum/static_cast<long double>(v.size());for(long double x:v)sq.add((x-s.mean)*(x-s.mean));s.sd=std::sqrt(sq.sum/static_cast<long double>(v.size()-1));s.minimum=*std::min_element(v.begin(),v.end());s.maximum=*std::max_element(v.begin(),v.end());return s;}
struct Ensemble {std::vector<long double> pair,u0,u1;U pair_visits=0,unary_visits=0,permutation_swaps=0;std::string pair_origin,unary_origin;};
Entropy control_pair(const std::vector<I>& labels,bool injective){
    const auto profile=fibre_profile(labels);Entropy e;e.population=static_cast<U>(labels.size())*static_cast<U>(labels.size());e.maximum_support=1;e.weighted_support=1;
    if(injective){lab::require(profile.size()==labels.size(),"injective control not injective");for(unsigned n:profile)lab::require(n==1,"injective control fibre");e.conditional_cells=e.population;e.joint_nonzero=e.population;e.support_cells[1]=e.population;e.support_mass[1]=e.population;}
    else{lab::require(profile.size()==1,"constant control not constant");e.conditional_cells=1;e.joint_nonzero=1;e.support_cells[1]=1;e.support_mass[1]=e.population;}return e;
}
Ensemble null_ensemble(const Projection& p,const std::vector<unsigned>& profile,const std::vector<long double>& logs,U seed,bool matched,const Entropy& observed,const std::array<Entropy,2>& unary){
    Ensemble e;const bool zero_control=p.name=="constant"||p.name=="full_point";const bool kummer_invariance=matched&&p.name=="kummer_x";const bool derived=zero_control||kummer_invariance;
    e.pair_origin=derived?"derived_exact_invariance":"measured_exact_full_pairs";e.unary_origin=derived?"derived_exact_invariance":"measured_exact_unary_census";
    if(derived){e.pair.assign(repetitions,observed.bits);e.u0.assign(repetitions,unary[0].bits);e.u1.assign(repetitions,unary[1].bits);return e;}
    lab::RNG rng(seed);
    for(unsigned i=0;i<repetitions;++i){auto shuffled=matched?sign_shuffle(rng,p.labels):p.labels;if(!matched)shuffle(rng,shuffled);e.permutation_swaps+=matched?static_cast<U>((p.labels.size()-1)/2-1):static_cast<U>(p.labels.size()-1);lab::require(fibre_profile(shuffled)==profile,"null changed exact fibre profile");const auto a=exact_pair(shuffled,logs),b=exact_unary(shuffled,logs,0),c=exact_unary(shuffled,logs,1);e.pair.push_back(a.bits);e.u0.push_back(b.bits);e.u1.push_back(c.bits);e.pair_visits+=a.visits;e.unary_visits+=b.visits+c.visits;}
    return e;
}
void emit_ensemble(std::ostream& out,const std::string& prefix,const Ensemble& e){
    out<<','<<lab::json_quote(prefix+"_entropy_bits")<<':';write_values(out,e.pair);
    out<<','<<lab::json_quote(prefix+"_unary_b0_entropy_bits")<<':';write_values(out,e.u0);
    out<<','<<lab::json_quote(prefix+"_unary_b1_entropy_bits")<<':';write_values(out,e.u1);
    const auto a=summarize(e.pair),b=summarize(e.u0),c=summarize(e.u1);
    out<<','<<lab::json_quote(prefix+"_mean_bits")<<':'<<a.mean<<','<<lab::json_quote(prefix+"_sample_sd_bits")<<':'<<a.sd<<','<<lab::json_quote(prefix+"_min_bits")<<':'<<a.minimum<<','<<lab::json_quote(prefix+"_max_bits")<<':'<<a.maximum;
    out<<','<<lab::json_quote(prefix+"_unary_b0_mean_bits")<<':'<<b.mean<<','<<lab::json_quote(prefix+"_unary_b0_sample_sd_bits")<<':'<<b.sd<<','<<lab::json_quote(prefix+"_unary_b0_min_bits")<<':'<<b.minimum<<','<<lab::json_quote(prefix+"_unary_b0_max_bits")<<':'<<b.maximum;
    out<<','<<lab::json_quote(prefix+"_unary_b1_mean_bits")<<':'<<c.mean<<','<<lab::json_quote(prefix+"_unary_b1_sample_sd_bits")<<':'<<c.sd<<','<<lab::json_quote(prefix+"_unary_b1_min_bits")<<':'<<c.minimum<<','<<lab::json_quote(prefix+"_unary_b1_max_bits")<<':'<<c.maximum;
    out<<','<<lab::json_quote(prefix+"_pair_value_origin")<<':'<<lab::json_quote(e.pair_origin)<<','<<lab::json_quote(prefix+"_unary_value_origin")<<':'<<lab::json_quote(e.unary_origin);
    out<<','<<lab::json_quote(prefix+"_pair_visits")<<':'<<e.pair_visits<<','<<lab::json_quote(prefix+"_unary_visits")<<':'<<e.unary_visits<<','<<lab::json_quote(prefix+"_permutation_swaps")<<':'<<e.permutation_swaps;
}
std::string projection_row(const lab::Fixture& f,const Projection& p){
    const auto profile=fibre_profile(p.labels);const auto largest=static_cast<std::size_t>(*std::max_element(profile.begin(),profile.end()));
    const bool control=p.name=="constant"||p.name=="full_point";const auto logs=clog_table(control?largest:largest*largest);
    const Entropy observed=control?control_pair(p.labels,p.name=="full_point"):exact_pair(p.labels,logs,false,true);
    const std::array<Entropy,2> unary{exact_unary(p.labels,logs,0,true),exact_unary(p.labels,logs,1,true)};
    const bool matched=sign_invariant(p.labels);const U null_seed=f.seed^domain_hash("L9.scale.unconditional.v1/"+f.id+"/"+p.name),matched_seed=f.seed^domain_hash("L9.scale.sign-pair.v1/"+f.id+"/"+p.name);
    if(control)lab::require(std::abs(observed.bits)<tolerance&&std::abs(unary[0].bits)<tolerance&&std::abs(unary[1].bits)<tolerance,"zero control failed");
    if(p.name=="kummer_x"){
        lab::require(matched&&profile.size()==(p.labels.size()+1)/2&&profile.front()==1,"Kummer orbit profile failed");for(std::size_t i=1;i<profile.size();++i)lab::require(profile[i]==2,"Kummer nonidentity fibre failed");
        const auto expected=static_cast<long double>((f.r-1)*(f.r-1))/static_cast<long double>(f.r*f.r);lab::require(std::abs(observed.bits-expected)<tolerance,"finite-r Kummer pair calibration failed");
        lab::require(std::abs(unary[0].bits)<tolerance,"Kummer doubling must be deterministic");lab::require(std::abs(unary[1].bits-static_cast<long double>(f.r-1)/static_cast<long double>(f.r))<tolerance,"finite-r Kummer double/add calibration failed");
    }
    const auto unconditional=null_ensemble(p,profile,logs,null_seed,false,observed,unary);
    Ensemble paired;if(matched)paired=null_ensemble(p,profile,logs,matched_seed,true,observed,unary);
    const auto& primary=matched?paired:unconditional;const auto primary_pair=summarize(primary.pair),primary0=summarize(primary.u0),primary1=summarize(primary.u1);
    std::ostringstream out;out<<std::setprecision(18)<<"{\"track\":\"L9-scale\",\"fixture\":"<<lab::json_quote(f.id)<<",\"stratum\":"<<lab::json_quote(f.stratum)<<",\"scope\":\"exploratory_toy_followup\",\"outcome\":\"complete_valid\",\"projection\":"<<lab::json_quote(p.name)<<",\"p\":"<<f.c.p<<",\"r\":"<<f.r<<",\"image_size\":"<<profile.size()<<",\"entropy_bits\":"<<observed.bits;
    out<<",\"pair_value_origin\":"<<lab::json_quote(control?"derived_exact_zero_control":"measured_exact_full_pairs")<<",\"logical_pair_population\":"<<observed.population<<",\"observed_pair_visits\":"<<observed.visits<<",\"conditional_cells\":"<<observed.conditional_cells<<",\"joint_nonzero_cells\":"<<observed.joint_nonzero<<",\"weighted_candidate_support\":"<<observed.weighted_support<<",\"maximum_candidate_support\":"<<observed.maximum_support<<",\"support_cell_histogram\":";write_map(out,observed.support_cells);out<<",\"support_pair_mass\":";write_map(out,observed.support_mass);
    out<<",\"joint_histogram_fnv64_not_cryptographic\":";if(control)out<<"null";else out<<lab::json_quote(std::to_string(observed.checksum));
    for(unsigned b=0;b<2;++b){const auto key="unary_b"+std::to_string(b);out<<','<<lab::json_quote(key+"_entropy_bits")<<':'<<unary[b].bits<<','<<lab::json_quote(key+"_population")<<':'<<unary[b].population<<','<<lab::json_quote(key+"_visits")<<':'<<unary[b].visits<<','<<lab::json_quote(key+"_conditional_cells")<<':'<<unary[b].conditional_cells<<','<<lab::json_quote(key+"_joint_nonzero_cells")<<':'<<unary[b].joint_nonzero<<','<<lab::json_quote(key+"_maximum_support")<<':'<<unary[b].maximum_support<<','<<lab::json_quote(key+"_weighted_support")<<':'<<unary[b].weighted_support<<','<<lab::json_quote(key+"_support_cell_histogram")<<':';write_map(out,unary[b].support_cells);out<<','<<lab::json_quote(key+"_support_population_mass")<<':';write_map(out,unary[b].support_mass);out<<','<<lab::json_quote(key+"_joint_fnv64_not_cryptographic")<<':'<<lab::json_quote(std::to_string(unary[b].checksum));}
    out<<",\"histogram_reconstruction\":\"Decode orbit-ordered labels. Pair counts sum1 into (labels[i],labels[j],labels[(i+j)%r]); unary b counts sum1 into (labels[i],labels[(2*i+b)%r]). Scalar-labelled orbit is charged instrumentation, not a decoder.\"";
    out<<",\"label_codec\":\"base64_uint16_little_endian_v1\",\"projection_labels_count\":"<<p.labels.size()<<",\"projection_labels_u16le_base64\":"<<lab::json_quote(b64_u16(p.labels))<<",\"fibre_sizes_rle\":";write_rle(out,profile);
    if(p.name=="full_point")out<<",\"raw_dictionary_encoding\":\"Regenerate by sorting {0 for O;1+x*p+y for each nonidentity [k]P}, k=0..r-1. Fullpoint values can exceed uint16; no dictionary truncation.\"";
    else out<<",\"raw_dictionary_count\":"<<p.dictionary.size()<<",\"raw_dictionary_u16le_base64\":"<<lab::json_quote(b64_u16(p.dictionary));
    out<<",\"null_repetitions\":"<<repetitions<<",\"null_seed\":"<<lab::json_quote(std::to_string(null_seed));emit_ensemble(out,"null",unconditional);
    out<<",\"negation_invariant\":"<<(matched?"true":"false")<<",\"matched_null_applicable\":"<<(matched?"true":"false")<<",\"matched_null_repetitions\":"<<(matched?repetitions:0U)<<",\"primary_reference_kind\":"<<lab::json_quote(matched?"sign_pair_matched_null":"unconditional_relabeling_null");
    if(matched){out<<",\"matched_null_seed\":"<<lab::json_quote(std::to_string(matched_seed));emit_ensemble(out,"matched_null",paired);}else out<<",\"matched_null_entropy_bits\":[],\"matched_null_unary_b0_entropy_bits\":[],\"matched_null_unary_b1_entropy_bits\":[],\"matched_null_unavailable_reason\":\"not negation invariant\"";
    out<<",\"primary_observed_minus_reference_mean_bits\":"<<observed.bits-primary_pair.mean<<",\"primary_unary_b0_observed_minus_reference_mean_bits\":"<<unary[0].bits-primary0.mean<<",\"primary_unary_b1_observed_minus_reference_mean_bits\":"<<unary[1].bits-primary1.mean;
    out<<",\"null_generator\":\"SplitMix64; rejection-bounded Fisher-Yates; fresh original labels each repetition; matched shuffle permutes nonzero sign-pair labels and fixes identity. Analytically derived control arrays consume no RNG/permutation/pair visits.\"";
    out<<",\"derived_control_justification\":\"Constant and bijective projections have zero pair/unary entropy after any codomain/domain relabeling. Kummer matched sign-pair shuffles are codomain permutations and preserve both pair and unary entropies; profile checked before reuse. All remaining null values are measured census values.\"";
    out<<",\"total_pair_visits\":"<<observed.visits+unconditional.pair_visits+paired.pair_visits<<",\"total_unary_visits\":"<<unary[0].visits+unary[1].visits+unconditional.unary_visits+paired.unary_visits<<",\"entropy_clog_lookup_entries\":"<<logs.size()<<",\"entropy_clog_lookup_storage_bytes\":"<<logs.size()*sizeof(long double)<<",\"projection_evaluations\":"<<f.r<<",\"projection_field_exponentiations\":"<<p.field_powers<<",\"shared_orbit_group_additions\":"<<f.r;
    out<<",\"cost_scope\":\"Exact entropy integer counters plus log-table storage; source/input certification and projection/sort/codec CPU also included in whole-process time. Orbit is shared across six projections, not six independently charged setups.\",\"sampling_error\":\"none for full finite populations; null ensemble variation is retained, no inferential test\",\"attack_claimed\":false,\"construction_gap\":\"No inference decoder or solver advantage is supplied by this observation module.\"}\n";
    return out.str();
}
void run(const std::string& fixtures,const std::string& output){
    const auto panel=lab::read_fixtures(fixtures);for(const auto& f:panel){lab::require(f.r<=maximum_order,"projection order envelope r<=8191");lab::require(f.c.a!=0&&f.c.b!=0&&f.N!=f.c.p+1,"follow-up requires ordinary non-special-j fixtures");lab::require(f.stratum=="ordinary"||f.stratum=="power5","unexpected follow-up stratum");if(f.stratum=="power5")lab::require(f.c.p%5==1,"power5 stratum field mismatch");}
    lab::require(!std::ifstream(output).good(),"refusing to overwrite existing projection output");std::ofstream out(output);lab::require(static_cast<bool>(out),"cannot create projection output");U rows=0;
    for(const auto& f:panel){const auto points=lab::orbit(f);for(const std::string name:{"full_point","constant","kummer_x","x_mod_7","power_residue_5","x_hash_7"}){
        if(name=="power_residue_5"&&(f.c.p-1)%5!=0)out<<"{\"track\":\"L9-scale\",\"fixture\":"<<lab::json_quote(f.id)<<",\"stratum\":"<<lab::json_quote(f.stratum)<<",\"scope\":\"exploratory_toy_followup\",\"projection\":\"power_residue_5\",\"outcome\":\"not_applicable\",\"reason\":\"5 does not divide p-1\"}\n";
        else {const auto row=projection_row(f,make_projection(f,points,name));out<<row;out.flush();lab::require(row.size()<=row_limit,"projection row exceeds frozen60KiB envelope; original row retained for failure rescue");}
        ++rows;out.flush();lab::require(static_cast<bool>(out),"projection output write failed");}
        std::cerr<<"L9-scale completed "<<f.id<<" r="<<f.r<<'\n';}
    std::cout<<"{\"status\":\"complete\",\"track\":\"L9-scale\",\"rows\":"<<rows<<",\"fixtures\":"<<panel.size()<<",\"attack_claimed\":false}\n";
}
void self_test(){
    U checks=0;const auto check=[&](bool value,const std::string& why){++checks;lab::require(value,why);};
    for(I order:{3,5,7,11,19,31}){
        const auto r=static_cast<std::size_t>(order);std::vector<I> constant(r,0),full(r),kummer(r),coarse(r),dyadic(r);for(I i=0;i<order;++i){const auto j=static_cast<std::size_t>(i);full[j]=i;kummer[j]=std::min(i,order-i);coarse[j]=kummer[j]%3;dyadic[j]=i&1;}
        for(auto labels:{constant,full,kummer,coarse,dyadic}){const auto logs=clog_table(r*r);const auto p=exact_pair(labels,logs,false,true);check(std::abs(p.bits-slow_pair(labels))<tolerance,"independent pair contingency");for(unsigned b=0;b<2;++b){const auto u=exact_unary(labels,logs,b,true);check(u.visits==r,"unary population");check(std::abs(u.bits-slow_unary(labels,b))<tolerance,"independent unary contingency");}}
        check(exact_pair(dyadic,clog_table(r*r)).conditional_cells==4,"dyadic four input cells");check(exact_unary(dyadic,clog_table(r*r),0).conditional_cells==2,"dyadic unary two input cells");
        const auto logs=clog_table(r*r);const auto k=exact_pair(kummer,logs);const auto expected=static_cast<long double>((order-1)*(order-1))/static_cast<long double>(order*order);check(std::abs(k.bits-expected)<tolerance,"finite-r Kummer pair");check(std::abs(exact_pair(kummer,logs,true).bits-1)<tolerance,"conditioned Kummer pair");check(std::abs(exact_unary(kummer,logs,0).bits)<tolerance,"Kummer unary doubling");check(std::abs(exact_unary(kummer,logs,1).bits-static_cast<long double>(order-1)/static_cast<long double>(order))<tolerance,"Kummer unary double/add");check(std::abs(slow_pair(kummer,true)-expected)>tolerance,"wrong group sum mutation detected");check(std::abs(k.bits-1)>tolerance,"wrong one-bit calibration detected");
        lab::RNG rng(44);const auto original=fibre_profile(kummer);for(unsigned j=0;j<5;++j){const auto shuffled=sign_shuffle(rng,kummer);check(fibre_profile(shuffled)==original&&shuffled[0]==kummer[0],"matched null exact fibres");check(std::abs(exact_pair(shuffled,logs).bits-k.bits)<tolerance,"derived Kummer pair invariance");for(unsigned b=0;b<2;++b)check(std::abs(exact_unary(shuffled,logs,b).bits-exact_unary(kummer,logs,b).bits)<tolerance,"derived Kummer unary invariance");}
        check(unb64_u16(b64_u16(full))==full,"codec full labels");check(unb64_u16(b64_u16(kummer))==kummer,"codec quotient labels");
    }
    for(const std::vector<I>& v: {std::vector<I>{},std::vector<I>{0},std::vector<I>{0,1,255,256,65535}})check(unb64_u16(b64_u16(v))==v,"codec byte/endian/padding roundtrip");
    std::vector<I> maximum_labels(static_cast<std::size_t>(maximum_order));std::iota(maximum_labels.begin(),maximum_labels.end(),I{0});check(unb64_u16(b64_u16(maximum_labels))==maximum_labels,"maximum envelope label codec");
    auto rejects=[&](const auto& fn,const std::string& why){bool failed=false;try{fn();}catch(const std::exception&){failed=true;}check(failed,why);};
    rejects([]{(void)fibre_profile({0,-1,1});},"negative labels rejected");rejects([]{(void)fibre_profile({0,2,2});},"missing labels rejected");rejects([]{lab::RNG rng(1);(void)sign_shuffle(rng,{0,1,2});},"noninvariant matched null rejected");rejects([]{(void)unb64_u16("AA=A");},"bad codec padding rejected");rejects([]{(void)b64_u16({65536});},"codec overflow rejected");
    lab::Fixture f;f.id="development-p61";f.stratum="ordinary";f.c={61,1,4};f.P={41,55,false};f.r=19;f.N=57;f.seed=7;lab::certify(f);const auto points=lab::orbit(f);
    for(std::size_t i=0;i<points.size();++i){check(f.c.add(points[i],points[i])==points[(2*i)%points.size()],"actual EC double rule");check(f.c.add(f.c.add(points[i],points[i]),f.P)==points[(2*i+1)%points.size()],"actual EC double/add rule");for(std::size_t j=0;j<points.size();++j)check(f.c.add(points[i],points[j])==points[(i+j)%points.size()],"actual EC pair rule");}
    for(const std::string name:{"full_point","constant","kummer_x","x_mod_7","power_residue_5","x_hash_7"}){const auto p=make_projection(f,points,name);const auto logs=clog_table(points.size()*points.size());const auto a=exact_pair(p.labels,logs),b=exact_unary(p.labels,logs,0),c=exact_unary(p.labels,logs,1);check(std::abs(a.bits-slow_pair(p.labels))<tolerance,"actual projection pair reference");check(std::abs(b.bits-slow_unary(p.labels,0))<tolerance,"actual projection unary0 reference");check(std::abs(c.bits-slow_unary(p.labels,1))<tolerance,"actual projection unary1 reference");const auto row=projection_row(f,p);check(row.size()<row_limit,"development serialized row bound");check(row.find("\"null_repetitions\":99")!=std::string::npos,"all null values serialized");if(name=="kummer_x")check(row.find("derived_exact_invariance")!=std::string::npos,"invariance reuse explicitly labelled");}
    std::cout<<"L9-SCALE SELF_TEST_PASS checks="<<checks<<"; no follow-up measurement cohort executed\n";
}
}
int main(int argc,char**argv){try{if(argc==2&&std::string(argv[1])=="--self-test"){ps::self_test();return 0;}if(argc==4&&std::string(argv[1])=="--run"){ps::run(argv[2],argv[3]);return 0;}std::cerr<<"usage: projection_scale --self-test | --run FIXTURES_TSV OUTPUT_JSONL\n";return 2;}catch(const std::exception&e){std::cerr<<"L9-scale ERROR "<<e.what()<<'\n';return 1;}}
