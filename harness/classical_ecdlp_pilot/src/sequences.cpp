#include "common.hpp"

#include <algorithm>
#include <array>
#include <cstdint>
#include <fstream>
#include <filesystem>
#include <iostream>
#include <limits>
#include <map>
#include <numeric>
#include <sstream>
#include <string>
#include <utility>
#include <vector>

// Explicit enumerative diagnostics. No locator, cheap state constructor, or
// non-generic ECDLP solver is implemented or claimed here.
namespace seq {
using lab::I;
using U = std::uint64_t;
constexpr std::size_t K = 15;
constexpr I infinity_symbol = -1;

struct Counts {
    U additions=0, multiplications=0, inversions=0;
    U feature_rows=0, polynomial_calls=0, gaussian_rows=0, bm_symbols=0;
};

struct Field {
    I p;
    Counts* count;
    I norm(I a) const { a %= p; return a < 0 ? a+p : a; }
    I add(I a,I b) const { ++count->additions; return norm(a+b); }
    I sub(I a,I b) const { ++count->additions; return norm(a-b); }
    I mul(I a,I b) const { ++count->multiplications; return norm(a*b); }
    I power(I a,U e) const {
        I v=1;
        while(e!=0) { if((e&1U)!=0) v=mul(v,a); e>>=1; if(e!=0) a=mul(a,a); }
        return v;
    }
    I inv(I a) const {
        lab::require(norm(a)!=0,"inverse of zero");
        ++count->inversions;
        return power(norm(a),static_cast<U>(p-2));
    }
};

using Feature = std::array<I,K>;

// Frozen order: 1,x0,x1,x2,x3,x0^2,x0*x1,x0*x2,x0*x3,
// x1^2,x1*x2,x1*x3,x2^2,x2*x3,x3^2.
Feature features(const std::array<I,4>& x,const Field& f) {
    Feature v{};
    v[0]=1;
    for(std::size_t i=0;i<4;++i) v[1+i]=x[i];
    std::size_t k=5;
    for(std::size_t i=0;i<4;++i) for(std::size_t j=i;j<4;++j) v[k++]=f.mul(x[i],x[j]);
    ++f.count->feature_rows;
    return v;
}

I evaluate(const Feature& x,const Feature& coefficients,const Field& f) {
    I y=0;
    for(std::size_t j=0;j<K;++j) y=f.add(y,f.mul(x[j],coefficients[j]));
    return y;
}

struct Row { Feature x; I y; };
struct Model { bool consistent=true; std::size_t rank=0; Feature coefficients{}; };

Model solve(const std::vector<Row>& rows,const Field& f) {
    std::vector<std::array<I,K+1>> matrix(rows.size());
    for(std::size_t i=0;i<rows.size();++i) {
        std::copy(rows[i].x.begin(),rows[i].x.end(),matrix[i].begin());
        matrix[i][K]=rows[i].y;
    }
    std::array<std::size_t,K> columns{};
    std::size_t pivot=0;
    for(std::size_t col=0;col<K && pivot<rows.size();++col) {
        std::size_t candidate=pivot;
        while(candidate<rows.size() && matrix[candidate][col]==0) ++candidate;
        if(candidate==rows.size()) continue;
        std::swap(matrix[pivot],matrix[candidate]);
        const I scale=f.inv(matrix[pivot][col]);
        for(std::size_t j=col;j<=K;++j) matrix[pivot][j]=f.mul(matrix[pivot][j],scale);
        for(std::size_t i=0;i<rows.size();++i) if(i!=pivot && matrix[i][col]!=0) {
            const I factor=matrix[i][col];
            for(std::size_t j=col;j<=K;++j) matrix[i][j]=f.sub(matrix[i][j],f.mul(factor,matrix[pivot][j]));
            ++f.count->gaussian_rows;
        }
        columns[pivot]=col;
        ++pivot;
    }
    Model model;
    model.rank=pivot;
    for(const auto& row:matrix) {
        bool zero=true;
        for(std::size_t j=0;j<K;++j) if(row[j]!=0) zero=false;
        if(zero && row[K]!=0) model.consistent=false;
    }
    if(model.consistent) for(std::size_t i=0;i<pivot;++i) model.coefficients[columns[i]]=matrix[i][K];
    // Every free variable stays zero. RREF/pivot order is deterministic.
    return model;
}

std::size_t linear_complexity(const std::vector<I>& sequence,const Field& f) {
    std::vector<I> c(1,1),b(1,1);
    std::size_t length=0,shift=1;
    I previous=1;
    for(std::size_t n=0;n<sequence.size();++n) {
        ++f.count->bm_symbols;
        I discrepancy=sequence[n];
        for(std::size_t i=1;i<=length;++i)
            if(i<c.size()) discrepancy=f.add(discrepancy,f.mul(c[i],sequence[n-i]));
        if(discrepancy==0) { ++shift; continue; }
        const auto old=c;
        const I scale=f.mul(discrepancy,f.inv(previous));
        if(c.size()<b.size()+shift) c.resize(b.size()+shift,0);
        for(std::size_t i=0;i<b.size();++i) c[i+shift]=f.sub(c[i+shift],f.mul(scale,b[i]));
        if(2*length<=n) {
            length=n+1-length;
            b=old;
            previous=discrepancy;
            shift=1;
        } else ++shift;
    }
    return length;
}

// Division polynomial values at one fixed odd-prime-order point. The only
// denominator in this evaluation recurrence is 2*y(P), which is nonzero.
class DivisionPolynomials {
    const lab::Fixture& g;
    const Field& f;
    std::map<U,I> cache;
    I cube(I x) const { return f.mul(f.mul(x,x),x); }
public:
    DivisionPolynomials(const lab::Fixture& fixture,const Field& field):g(fixture),f(field) {
        const I x=g.P.x,y=g.P.y,a=g.c.a,b=g.c.b;
        lab::require(!g.P.inf && f.norm(2*y)!=0,"EDS needs a finite point with 2y nonzero");
        const I x2=f.mul(x,x),x3=f.mul(x2,x),x4=f.mul(x2,x2),x6=f.mul(x3,x3);
        const I a2=f.mul(a,a),a3=f.mul(a2,a),b2=f.mul(b,b);
        cache[0]=0;cache[1]=1;cache[2]=f.norm(2*y);
        cache[3]=f.sub(f.add(f.add(f.mul(3,x4),f.mul(6,f.mul(a,x2))),f.mul(12,f.mul(b,x))),a2);
        I inner=f.add(x6,f.mul(5,f.mul(a,x4)));
        inner=f.add(inner,f.mul(20,f.mul(b,x3)));
        inner=f.sub(inner,f.mul(5,f.mul(a2,x2)));
        inner=f.sub(inner,f.mul(4,f.mul(f.mul(a,b),x)));
        inner=f.sub(inner,f.mul(8,b2));
        inner=f.sub(inner,a3);
        cache[4]=f.mul(f.norm(4*y),inner);
    }
    I value(U n) {
        ++f.count->polynomial_calls;
        auto hit=cache.find(n);if(hit!=cache.end()) return hit->second;
        const U m=n/2;
        I answer;
        if((n&1U)!=0) {
            answer=f.sub(f.mul(value(m+2),cube(value(m))),f.mul(value(m-1),cube(value(m+1))));
        } else {
            const I left=f.mul(value(m+2),f.mul(value(m-1),value(m-1)));
            const I right=f.mul(value(m-2),f.mul(value(m+1),value(m+1)));
            answer=f.mul(f.mul(value(m),f.inv(f.norm(2*g.P.y))),f.sub(left,right));
        }
        cache.emplace(n,answer);return answer;
    }
};

struct Prediction {
    std::size_t chart_windows=0,excluded_infinity=0,train_rows=0,test_rows=0;
    Model model;
    U exact_test_matches=0;
};

Prediction predict(const std::vector<I>& periodic,const Field& f) {
    lab::require(periodic.size()>=5,"sequence period is too short for a four-value predictor");
    std::vector<Row> rows;
    Prediction out;
    for(std::size_t n=0;n<periodic.size();++n) {
        std::array<I,4> x{};
        bool finite=true;
        for(std::size_t j=0;j<5;++j) if(periodic[(n+j)%periodic.size()]==infinity_symbol) finite=false;
        if(!finite) { ++out.excluded_infinity;continue; }
        for(std::size_t j=0;j<4;++j) x[j]=periodic[(n+j)%periodic.size()];
        rows.push_back({features(x,f),periodic[(n+4)%periodic.size()]});
    }
    out.chart_windows=rows.size();out.train_rows=rows.size()/2;out.test_rows=rows.size()-out.train_rows;
    const std::vector<Row> training(rows.begin(),rows.begin()+static_cast<std::ptrdiff_t>(out.train_rows));
    out.model=solve(training,f);
    if(out.model.consistent) for(std::size_t i=out.train_rows;i<rows.size();++i)
        if(evaluate(rows[i].x,out.model.coefficients,f)==rows[i].y) ++out.exact_test_matches;
    return out;
}

struct PredictionAggregate {
    U fits=0,inconsistent=0,underidentified=0,tested=0,matches=0,excluded=0;
    std::size_t min_rank=K,max_rank=0;
    void include(const Prediction& p) {
        excluded+=p.excluded_infinity;
        min_rank=std::min(min_rank,p.model.rank);max_rank=std::max(max_rank,p.model.rank);
        if(p.model.consistent) {
            ++fits;if(p.model.rank<K) ++underidentified;
            tested+=p.test_rows;matches+=p.exact_test_matches;
        } else ++inconsistent;
    }
};

std::string aggregate_json(const PredictionAggregate& a) {
    std::ostringstream out;
    out<<"{\"consistent_fits\":"<<a.fits<<",\"inconsistent_fits\":"<<a.inconsistent
       <<",\"underidentified_consistent_fits\":"<<a.underidentified<<",\"test_predictions_attempted\":"<<a.tested
       <<",\"exact_test_matches\":"<<a.matches<<",\"excluded_infinity_windows\":"<<a.excluded
       <<",\"minimum_training_rank\":"<<a.min_rank<<",\"maximum_training_rank\":"<<a.max_rank<<"}";
    return out.str();
}

std::vector<I> x_symbols(const std::vector<lab::Point>& points) {
    std::vector<I> a;a.reserve(points.size());
    for(const auto& p:points) a.push_back(p.inf?infinity_symbol:p.x);
    return a;
}

std::string json_sizes(const std::vector<std::size_t>& values) {
    std::ostringstream out;out<<'[';
    for(std::size_t i=0;i<values.size();++i){if(i)out<<',';out<<values[i];}out<<']';return out.str();
}

void run_l2(const lab::Fixture& g,const std::vector<lab::Point>& points,std::ostream& out) {
    Counts counts;const Field f{g.c.p,&counts};
    DivisionPolynomials division(g,f);
    U coordinate_checks=0,ward_checks=0;
    const U order=static_cast<U>(g.r);
    std::vector<I> eds;eds.reserve(static_cast<std::size_t>(order+1));
    for(U n=0;n<=order;++n) eds.push_back(division.value(n));
    lab::require(eds.front()==0 && eds[1]==1 && eds.back()==0,"EDS endpoint calibration failed");
    for(U n=1;n<order;++n) {
        const I w=division.value(n);
        lab::require(w!=0,"nonidentity EDS value unexpectedly zero");
        const I x=f.sub(g.P.x,f.mul(f.mul(division.value(n-1),division.value(n+1)),f.inv(f.mul(w,w))));
        lab::require(x==points[static_cast<std::size_t>(n)].x,"division-polynomial coordinate mismatch");
        ++coordinate_checks;
    }
    const U bound=std::min<U>(order-1,16);
    for(U m=1;m<=bound;++m) for(U n=1;n<=m;++n) {
        const I wm=division.value(m),wn=division.value(n);
        const I left=f.mul(division.value(m+n),division.value(m-n));
        const I right=f.sub(f.mul(f.mul(division.value(m+1),division.value(m-1)),f.mul(wn,wn)),
                            f.mul(f.mul(division.value(n+1),division.value(n-1)),f.mul(wm,wm)));
        lab::require(left==right,"Ward EDS identity mismatch");++ward_checks;
    }
    std::vector<std::size_t> prefixes,eds_complexity;
    for(std::size_t n=8;n<=eds.size();n*=2) {
        prefixes.push_back(n);
        eds_complexity.push_back(linear_complexity(std::vector<I>(eds.begin(),eds.begin()+static_cast<std::ptrdiff_t>(n)),f));
    }
    if(prefixes.empty()||prefixes.back()!=eds.size()) {
        prefixes.push_back(eds.size());eds_complexity.push_back(linear_complexity(eds,f));
    }
    auto symbols=x_symbols(points);
    PredictionAggregate translated,nulls;
    U skipped_coordinate_prefixes=0,coordinate_prefixes=0,coordinate_bm_sum=0;
    std::vector<std::size_t> coordinate_lengths;
    for(std::size_t n:prefixes) if(n<=symbols.size()) coordinate_lengths.push_back(n);
    if(coordinate_lengths.empty()||coordinate_lengths.back()!=symbols.size()) coordinate_lengths.push_back(symbols.size());
    std::ostringstream per_target;
    per_target<<'[';
    for(std::size_t shift=0;shift<symbols.size();++shift) {
        std::vector<I> translated_symbols(symbols.size());
        for(std::size_t i=0;i<symbols.size();++i) translated_symbols[i]=symbols[(i+shift)%symbols.size()];
        const auto prediction=predict(translated_symbols,f);translated.include(prediction);
        if(shift!=0)per_target<<',';
        per_target<<'['<<shift<<','<<prediction.model.rank<<','<<(prediction.model.consistent?1:0)
                  <<','<<prediction.train_rows<<','<<prediction.test_rows<<','<<prediction.exact_test_matches<<",[";
        bool first_prefix=true;
        for(std::size_t n:coordinate_lengths) {
            if(!first_prefix) per_target<<',';
            first_prefix=false;
            std::vector<I> prefix(translated_symbols.begin(),translated_symbols.begin()+static_cast<std::ptrdiff_t>(n));
            if(std::find(prefix.begin(),prefix.end(),infinity_symbol)!=prefix.end()) {++skipped_coordinate_prefixes;per_target<<"null";}
            else {const auto complexity=linear_complexity(prefix,f);coordinate_bm_sum+=complexity;++coordinate_prefixes;per_target<<complexity;}
        }
        per_target<<"]]";
    }
    per_target<<']';
    lab::RNG rng(g.seed^U{0x4c325f4e554c4c});
    for(unsigned trial=0;trial<99;++trial) {
        auto shuffled=symbols;rng.shuffle(shuffled);nulls.include(predict(shuffled,f));
    }
    out<<"{\"track\":\"L2\",\"fixture\":"<<lab::json_quote(g.id)
       <<",\"scope\":\"exploratory_toy_diagnostic\",\"outcome\":\"complete_valid\""
       <<",\"stratum\":"<<lab::json_quote(g.stratum)<<",\"p\":"<<g.c.p<<",\"r\":"<<g.r
       <<",\"eds_coordinate_checks\":"<<coordinate_checks<<",\"ward_identity_checks\":"<<ward_checks
       <<",\"eds_prefix_lengths\":"<<json_sizes(prefixes)<<",\"eds_prefix_linear_complexities\":"<<json_sizes(eds_complexity)
       <<",\"public_translated_targets\":"<<symbols.size()<<",\"quadratic_monomials\":15,\"translated_quadratic\":"<<aggregate_json(translated)
       <<",\"null_permutations\":99,\"shuffled_quadratic\":"<<aggregate_json(nulls)
       <<",\"coordinate_finite_prefixes\":"<<coordinate_prefixes<<",\"coordinate_prefixes_excluded_for_infinity\":"<<skipped_coordinate_prefixes
       <<",\"sum_coordinate_prefix_linear_complexities\":"<<coordinate_bm_sum
       <<",\"coordinate_prefix_lengths\":"<<json_sizes(coordinate_lengths)
       <<",\"per_target_columns\":[\"known_shift_in_truth_enumeration\",\"training_rank\",\"consistent_1_or_0\",\"training_windows\",\"test_windows\",\"exact_matches_if_consistent\",\"coordinate_bm_by_prefix_null_means_infinity\"]"
       <<",\"per_target\":"<<per_target.str()
       <<",\"enumerated_orbit_points\":"<<points.size()<<",\"orbit_point_additions\":"<<points.size()
       <<",\"modular_additions\":"<<counts.additions<<",\"modular_multiplications\":"<<counts.multiplications
       <<",\"modular_inversions\":"<<counts.inversions<<",\"feature_rows\":"<<counts.feature_rows
       <<",\"gaussian_eliminated_rows\":"<<counts.gaussian_rows<<",\"bm_symbols_processed\":"<<counts.bm_symbols
       <<",\"encoded_coefficient_bits_per_model\":"<<(K*lab::bits(static_cast<U>(g.c.p-1)))
       <<",\"coefficient_payload_bytes_per_model\":"<<sizeof(Feature)
       <<",\"translated_sequence_symbol_copies\":"<<(symbols.size()*symbols.size())
       <<",\"null_shuffle_swaps\":"<<(99*(symbols.size()-1))
       <<",\"arithmetic_counter_scope\":\"sequence, interpolation and recurrence arithmetic; excludes shared EC certification and orbit arithmetic\""
       <<",\"construction_gap\":\"No public target-specific nonlinear index locator or scalar decoder; all scalar orientations were enumerated and charged.\"}\n";
}

struct Compare {
    U* calls=nullptr;U* symbols=nullptr;
    bool operator()(const std::vector<I>& a,const std::vector<I>& b) const {
        ++*calls;
        for(std::size_t i=0;i<a.size();++i) {++*symbols;if(a[i]!=b[i])return a[i]<b[i];}
        return false;
    }
};
struct Residuals {
    std::size_t states=0,transitions=0;
    U symbols_constructed=0,comparison_calls=0,comparison_symbols=0;
    U stored_symbol_bytes=0,transitions_checked=0;
    std::vector<std::size_t> distinct_per_depth;
};

Residuals residuals(const std::vector<I>& sequence,unsigned maxdepth) {
    lab::require(!sequence.empty(),"empty periodic sequence");
    Residuals result;
    std::map<std::vector<I>,std::size_t,Compare> ids(Compare{&result.comparison_calls,&result.comparison_symbols});
    std::vector<std::vector<std::size_t>> levels;
    for(unsigned e=0;e<=maxdepth;++e) {
        const U step=U{1}<<e;
        std::vector<std::size_t> level(static_cast<std::size_t>(step));
        std::map<std::size_t,bool> depth_ids;
        for(U j=0;j<step;++j) {
            std::vector<I> vector(sequence.size());
            for(std::size_t n=0;n<sequence.size();++n) {
                vector[n]=sequence[static_cast<std::size_t>((step*static_cast<U>(n)+j)%static_cast<U>(sequence.size()))];
                ++result.symbols_constructed;
            }
            auto insertion=ids.emplace(std::move(vector),ids.size());
            level[static_cast<std::size_t>(j)]=insertion.first->second;
            depth_ids.emplace(insertion.first->second,true);
        }
        result.distinct_per_depth.push_back(depth_ids.size());levels.push_back(std::move(level));
    }
    std::map<std::size_t,std::array<std::size_t,2>> transitions;
    for(unsigned e=0;e<maxdepth;++e) for(std::size_t j=0;j<levels[e].size();++j) {
        const std::array<std::size_t,2> children{levels[e+1][j],levels[e+1][j+levels[e].size()]};
        auto insertion=transitions.emplace(levels[e][j],children);
        lab::require(insertion.second||insertion.first->second==children,"equal residual functions have inconsistent transitions");
        result.transitions_checked+=2;
    }
    result.states=ids.size();result.transitions=2*transitions.size();
    result.stored_symbol_bytes=static_cast<U>(ids.size())*static_cast<U>(sequence.size())*sizeof(I);
    return result;
}

std::string residual_json(const Residuals& r) {
    std::ostringstream out;
    out<<"{\"exact_states\":"<<r.states<<",\"distinct_per_depth\":"<<json_sizes(r.distinct_per_depth)
       <<",\"defined_transitions\":"<<r.transitions<<",\"transition_checks\":"<<r.transitions_checked
       <<",\"symbol_lookups_constructed\":"<<r.symbols_constructed<<",\"comparison_calls\":"<<r.comparison_calls
       <<",\"compared_symbols\":"<<r.comparison_symbols<<",\"stored_symbol_payload_bytes\":"<<r.stored_symbol_bytes<<"}";
    return out.str();
}

std::size_t ambiguity_max(const std::vector<I>& symbols) {
    std::map<I,std::size_t> frequencies;
    for(I a:symbols)++frequencies[a];
    std::size_t result=0;for(const auto& entry:frequencies)result=std::max(result,entry.second);return result;
}

void run_l6(const lab::Fixture& g,const std::vector<lab::Point>& points,std::ostream& out) {
    const unsigned depth=std::min<unsigned>(lab::bits(static_cast<U>(g.r)),6);
    auto x=x_symbols(points);
    std::vector<I> full;full.reserve(points.size());
    for(const auto& p:points) full.push_back(p.inf?0:1+p.x+g.c.p*p.y);
    const auto exact=residuals(x,depth),full_control=residuals(full,depth);
    lab::RNG rng(g.seed^U{0x4c365f4e554c4c});
    const std::size_t shift=static_cast<std::size_t>(rng.next()%static_cast<U>(x.size()));
    std::vector<I> rotated(x.size());
    for(std::size_t n=0;n<x.size();++n)rotated[n]=x[(n+shift)%x.size()];
    const auto orientation_control=residuals(rotated,depth);
    U null_lookup=0,null_comparisons=0,null_bytes=0;
    std::vector<std::size_t> null_states;null_states.reserve(99);
    for(unsigned trial=0;trial<99;++trial) {
        auto shuffled=x;rng.shuffle(shuffled);const auto r=residuals(shuffled,depth);
        null_states.push_back(r.states);null_lookup+=r.symbols_constructed;null_comparisons+=r.comparison_symbols;
        null_bytes=std::max(null_bytes,r.stored_symbol_bytes);
    }
    const auto xambiguity=ambiguity_max(x),fullambiguity=ambiguity_max(full);
    lab::require(xambiguity==2&&fullambiguity==1,"projection ambiguity calibration mismatch");
    out<<"{\"track\":\"L6\",\"fixture\":"<<lab::json_quote(g.id)
       <<",\"scope\":\"exploratory_toy_diagnostic\",\"outcome\":\"complete_valid\""
       <<",\"stratum\":"<<lab::json_quote(g.stratum)<<",\"r\":"<<g.r<<",\"base\":2,\"depth\":"<<depth
       <<",\"boundary\":\"periodic modulo r\",\"x_residuals\":"<<residual_json(exact)
       <<",\"full_point_control\":"<<residual_json(full_control)<<",\"cyclic_orientation_shift\":"<<shift
       <<",\"orientation_control\":"<<residual_json(orientation_control)
       <<",\"null_permutations\":99,\"null_exact_states\":"<<json_sizes(null_states)
       <<",\"null_total_symbol_lookups\":"<<null_lookup<<",\"null_total_compared_symbols\":"<<null_comparisons
       <<",\"null_max_stored_symbol_payload_bytes\":"<<null_bytes
       <<",\"null_shuffle_swaps\":"<<(99*(points.size()-1))
       <<",\"x_max_scalar_ambiguity\":"<<xambiguity<<",\"x_singleton_fibres\":1,\"x_two_element_fibres\":"<<((g.r-1)/2)
       <<",\"full_point_max_scalar_ambiguity\":"<<fullambiguity
       <<",\"enumerated_orbit_points\":"<<points.size()<<",\"orbit_point_additions\":0,\"orbit_reused_from_L2\":true"
       <<",\"construction_gap\":\"Residual vectors and the scalar dictionary were explicitly enumerated; no cheap uniform constructor or public target orientation decoder.\"}\n";
}

void self_test() {
    Counts counts;const Field f{17,&counts};
    std::vector<I> zeros(32,0),geometric;I z=1;
    for(unsigned i=0;i<32;++i){geometric.push_back(z);z=f.mul(z,3);}
    lab::require(linear_complexity(zeros,f)==0,"zero BM control");
    lab::require(linear_complexity(geometric,f)==1,"geometric BM control");
    std::vector<I> fibonacci{0,1};
    for(unsigned i=2;i<32;++i)fibonacci.push_back(f.add(fibonacci[i-1],fibonacci[i-2]));
    lab::require(linear_complexity(fibonacci,f)==2,"Fibonacci BM control");
    std::vector<std::array<I,4>> sites(1,std::array<I,4>{0,0,0,0});
    for(std::size_t i=0;i<4;++i){std::array<I,4>a{};a[i]=1;sites.push_back(a);a[i]=2;sites.push_back(a);}
    for(std::size_t i=0;i<4;++i)for(std::size_t j=i+1;j<4;++j){std::array<I,4>a{};a[i]=1;a[j]=1;sites.push_back(a);}
    lab::require(sites.size()==K,"quadratic unisolvent site count");
    Feature coefficients{};for(std::size_t j=0;j<K;++j)coefficients[j]=static_cast<I>(j+1);
    std::vector<Row> rows;
    for(const auto& site:sites){const auto x=features(site,f);rows.push_back({x,evaluate(x,coefficients,f)});}
    const auto model=solve(rows,f);
    lab::require(model.consistent&&model.rank==K&&model.coefficients==coefficients,"quadratic coefficient recovery control");
    auto contradictory=rows;contradictory.push_back(rows.front());contradictory.back().y=f.add(contradictory.back().y,1);
    lab::require(!solve(contradictory,f).consistent,"inconsistent interpolation was accepted");
    std::vector<I> parity{0,1};const auto r=residuals(parity,4);
    lab::require(r.states==3&&r.transitions==6,"known parity 2-kernel control");
    lab::Fixture fixture{"selftest-p17","development",{17,2,2},{5,1,false},19,19,17};
    lab::certify(fixture);const auto points=lab::orbit(fixture);
    std::ostringstream diagnostic;run_l2(fixture,points,diagnostic);run_l6(fixture,points,diagnostic);
    lab::require(diagnostic.str().find("\"track\":\"L2\"")!=std::string::npos,"L2 output absent");
    lab::require(diagnostic.str().find("\"track\":\"L6\"")!=std::string::npos,"L6 output absent");
    std::cout<<"PASS sequences developer checks: BM zero/geometric/Fibonacci; full-rank 15-term quadratic recovery; inconsistent system rejection; exact parity kernel; p17 EDS/Ward/coordinate and L2/L6 smoke checks\n";
}
} // namespace seq

int main(int argc,char** argv) {
    try {
        if(argc==2&&std::string(argv[1])=="--self-test") {seq::self_test();return 0;}
        if(argc!=4||std::string(argv[1])!="--run") {
            std::cerr<<"usage: sequences --self-test | --run FIXTURES_TSV OUTPUT_JSONL\n";return 2;
        }
        const auto fixtures=lab::read_fixtures(argv[2]);
        lab::require(!std::filesystem::exists(argv[3]),"refusing to overwrite an existing output path");
        std::ofstream out(argv[3],std::ios::out|std::ios::trunc);
        lab::require(static_cast<bool>(out),"cannot open output path");
        for(const auto& fixture:fixtures) {
            lab::certify(fixture);const auto points=lab::orbit(fixture);
            seq::run_l2(fixture,points,out);seq::run_l6(fixture,points,out);
            out.flush();lab::require(static_cast<bool>(out),"output write failure");
        }
        return 0;
    } catch(const std::exception& e) {std::cerr<<"FAIL sequences: "<<e.what()<<'\n';return 1;}
}
