// Frozen finite K1/F2^19 coordinate geometry and coverage search.
// No scalar-log table, SAT solver, rho, or imported target enters this program.
#include <CommonCrypto/CommonDigest.h>
#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <numeric>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>
using namespace std;

static constexpr uint32_t N=19, FIELD=1u<<N, MASK=FIELD-1, POLY=FIELD|39u;
static constexpr uint32_t ORDER=262543, TARGETS=6909, WORDS=(TARGETS+63)/64;
static void need(bool b,const string& m){if(!b) throw runtime_error(m);}
static double seconds(chrono::steady_clock::time_point a){return chrono::duration<double>(chrono::steady_clock::now()-a).count();}
static string readall(const string& p){ifstream f(p,ios::binary);need(bool(f),"cannot read "+p);return string(istreambuf_iterator<char>(f),{});}
static string sha_bytes(const string& s){unsigned char h[CC_SHA256_DIGEST_LENGTH];CC_SHA256(s.data(),(CC_LONG)s.size(),h);ostringstream out;out<<hex<<setfill('0');for(auto x:h)out<<setw(2)<<(unsigned)x;return out.str();}
static string sha_file(const string& p){return sha_bytes(readall(p));}
static array<uint32_t,8> digest(const string& s){unsigned char h[32];CC_SHA256(s.data(),(CC_LONG)s.size(),h);array<uint32_t,8> a{};for(int i=0;i<8;i++)for(int k=0;k<4;k++)a[i]|=uint32_t(h[4*i+k])<<(8*k);return a;}
static string nums_json(const vector<uint32_t>& v){ostringstream o;o<<"[";for(size_t i=0;i<v.size();i++){if(i)o<<",";o<<v[i];}o<<"]";return o.str();}
static vector<uint32_t> array_numbers(const string& text,const string& key){
    auto at=text.find("\""+key+"\"");need(at!=string::npos,"missing JSON key "+key);at=text.find('[',at);need(at!=string::npos,"missing array "+key);
    int depth=0;size_t end=at;
    for(;end<text.size();end++){
        if(text[end]=='[')depth++;
        else if(text[end]==']'){
            depth--;
            if(depth==0){end++;break;}
        }
    }
    need(depth==0,"unterminated array "+key);vector<uint32_t> out;uint64_t value=0;bool active=false;
    for(size_t i=at;i<end;i++){char c=text[i];if(c>='0'&&c<='9'){active=true;value=value*10+(c-'0');need(value<=UINT32_MAX,"JSON integer overflow");}else if(active){out.push_back(uint32_t(value));value=0;active=false;}}
    return out;
}
static map<int,int> historical_histogram(const string& path){
    string source=readall(path),needle="\"coverage_histogram\":{",all;
    auto start=source.find(needle);need(start!=string::npos,"historical histogram missing");start+=needle.size();
    auto end=source.find('}',start);need(end!=string::npos,"historical histogram unterminated");
    map<int,int> result;size_t at=start;
    while(at<end){
        auto a=source.find('"',at);if(a==string::npos||a>=end)break;
        auto b=source.find('"',a+1);need(b!=string::npos&&b<end,"historical histogram bad key");
        int key=stoi(source.substr(a+1,b-a-1));auto colon=source.find(':',b+1);need(colon!=string::npos&&colon<end,"historical histogram bad value");
        size_t consumed=0;int value=stoi(source.substr(colon+1,end-colon-1),&consumed);need(value>0,"historical histogram nonpositive frequency");
        result.emplace(key,value);at=colon+1+consumed;
    }
    need(accumulate(result.begin(),result.end(),0,[](int n,const auto& row){return n+row.second;})==66045,"historical histogram count mismatch");
    need(result.rbegin()->first==6257&&result.at(6257)==1,"historical at-most maximum mismatch");
    return result;
}
static uint32_t mul(uint32_t a,uint32_t b){uint32_t z=0;while(b){if(b&1)z^=a;b>>=1;a<<=1;if(a&FIELD)a^=POLY;}return z&MASK;}
static uint32_t sq(uint32_t a){return mul(a,a);}
static uint32_t power(uint32_t a,uint32_t n){uint32_t z=1;while(n){if(n&1)z=mul(z,a);a=sq(a);n>>=1;}return z;}
static uint32_t inv(uint32_t a){need(a!=0,"zero field inverse");return power(a,FIELD-2);}
static uint32_t refmul(uint32_t a,uint32_t b){
    uint64_t raw=0;for(int i=0;i<19;i++)if((b>>i)&1)raw^=uint64_t(a)<<i;
    for(int i=36;i>=19;i--)if((raw>>i)&1)raw^=uint64_t(POLY)<<(i-19);
    return uint32_t(raw);
}
static int degree(uint64_t p){return p?63-__builtin_clzll(p):-1;}
static uint64_t rempoly(uint64_t a,uint64_t b){need(b!=0,"zero polynomial divisor");while(degree(a)>=degree(b))a^=b<<(degree(a)-degree(b));return a;}
static uint64_t gcdpoly(uint64_t a,uint64_t b){while(b){auto r=rempoly(a,b);a=b;b=r;}return a;}
static uint32_t refsq(uint32_t a){return refmul(a,a);}
static uint32_t refinv(uint32_t a){
    need(a!=0,"zero reference inverse");uint32_t z=1,n=FIELD-2;
    while(n){if(n&1)z=refmul(z,a);a=refsq(a);n>>=1;}
    return z;
}

struct Point {uint32_t x=UINT32_MAX,y=0;bool inf()const{return x==UINT32_MAX;}bool operator==(const Point& q)const{return x==q.x&&y==q.y;}bool operator<(const Point& q)const{return x<q.x||(x==q.x&&y<q.y);}};
static Point infinity(){return {};}
static Point neg(Point p){if(!p.inf())p.y^=p.x;return p;}
static bool oncurve(Point p){return p.inf()||(sq(p.y)^mul(p.x,p.y))==(mul(sq(p.x),p.x)^sq(p.x)^1u);}
static Point add(Point p,Point q){
    if(p.inf())return q;if(q.inf())return p;
    if(p.x==q.x){
        if((p.y^q.y)==p.x)return infinity();
        need(p==q&&p.x!=0,"invalid equal-x group input");
        uint32_t l=p.x^mul(p.y,inv(p.x)),x=sq(l)^l^1u;
        return {x,sq(p.x)^mul(l^1u,x)};
    }
    uint32_t l=mul(p.y^q.y,inv(p.x^q.x)),x=sq(l)^l^p.x^q.x^1u;
    return {x,mul(l,p.x^x)^x^p.y};
}
static Point refadd(Point p,Point q){
    if(p.inf())return q;if(q.inf())return p;
    if(p.x==q.x){
        if((p.y^q.y)==p.x)return infinity();
        need(p==q&&p.x!=0,"reference equal-x error");
        uint32_t l=p.x^refmul(p.y,refinv(p.x)),x=refsq(l)^l^1u;
        return {x,refsq(p.x)^refmul(l^1u,x)};
    }
    uint32_t l=refmul(p.y^q.y,refinv(p.x^q.x)),x=refsq(l)^l^p.x^q.x^1u;
    return {x,refmul(l,p.x^x)^x^p.y};
}
static Point scalar(Point p,uint32_t n){Point z=infinity();while(n){if(n&1)z=add(z,p);p=add(p,p);n>>=1;}return z;}
static Point frob(Point p){return p.inf()?p:Point{sq(p.x),sq(p.y)};}
static uint32_t xkey(uint32_t x){uint32_t best=x;for(int i=1;i<19;i++){x=sq(x);best=min(best,x);}return best;}
static uint64_t pointcode(Point p){return p.inf()?UINT64_MAX:(uint64_t(p.x)<<19)|p.y;}
static vector<Point> batch_add(Point p,const vector<Point>& qs){
    vector<Point> out(qs.size());vector<uint32_t> den,pre;vector<size_t> ids;den.reserve(qs.size());pre.reserve(qs.size());
    uint32_t acc=1;
    for(size_t k=0;k<qs.size();k++){
        Point q=qs[k];if(p.inf()){out[k]=q;continue;}if(q.inf()){out[k]=p;continue;}
        if(p.x==q.x){out[k]=add(p,q);continue;}
        uint32_t d=p.x^q.x;ids.push_back(k);den.push_back(d);pre.push_back(acc);acc=mul(acc,d);
    }
    if(!ids.empty()){
        uint32_t v=inv(acc);
        for(size_t h=ids.size();h-->0;){
            auto k=ids[h];auto q=qs[k];uint32_t inverse=mul(v,pre[h]);v=mul(v,den[h]);
            uint32_t l=mul(p.y^q.y,inverse),x=sq(l)^l^p.x^q.x^1u;
            out[k]={x,mul(l,p.x^x)^x^p.y};
        }
    }
    return out;
}
struct Pool {
    vector<Point> reps;vector<uint32_t> public_scalars;array<uint32_t,4> prior{};
    explicit Pool(const string& path){
        string text=readall(path);auto v=array_numbers(text,"pool_representatives");
        need(v.size()==74,"pool representatives must be 37 coordinate pairs");
        for(int i=0;i<37;i++)reps.push_back({v[2*i],v[2*i+1]});
        public_scalars=array_numbers(text,"public_target_scalar_representatives");
        need(public_scalars.size()==6909,"target scalar list size mismatch");
        auto old=array_numbers(text,"prior_selected_indices");need(old.size()==4,"prior index count");
        copy(old.begin(),old.end(),prior.begin());
        need(prior==array<uint32_t,4>{6,9,22,28},"prior index binding changed");
    }
};
using X4=array<uint32_t,4>;using I4=array<int,4>;
static X4 canonical(X4 x){X4 best{};bool first=true;for(int j=0;j<19;j++){sort(x.begin(),x.end());if(first||x<best){best=x;first=false;}for(auto& v:x)v=sq(v);}return best;}
static I4 orbit_ids(I4 x){sort(x.begin(),x.end());return x;}
struct Geometry {
    map<X4,I4> planes;map<I4,X4> bases;uint64_t collision_pairs=0;
};
struct PairRecord {uint32_t z,x,y;uint8_t i,j;bool operator<(const PairRecord& r)const{return z<r.z;}};
static Geometry enumerate_planes(const vector<vector<uint32_t>>& xorbit,int count){
    vector<PairRecord> pairs;for(int i=0;i<count;i++)for(int j=i+1;j<count;j++)for(auto x:xorbit[i])for(auto y:xorbit[j])pairs.push_back({x^y,x,y,uint8_t(i),uint8_t(j)});
    sort(pairs.begin(),pairs.end());Geometry g;
    for(size_t a=0;a<pairs.size();){
        size_t b=a+1;while(b<pairs.size()&&pairs[b].z==pairs[a].z)b++;
        for(size_t u=a;u<b;u++)for(size_t v=u+1;v<b;v++){
            auto p=pairs[u],q=pairs[v];I4 ids=orbit_ids({p.i,p.j,q.i,q.j});
            if(adjacent_find(ids.begin(),ids.end())!=ids.end())continue;
            X4 key=canonical({p.x,p.y,q.x,q.y});
            need(key[0]!=key[1]&&key[1]!=key[2]&&key[2]!=key[3],"degenerate plane retained");
            auto it=g.planes.emplace(key,ids);
            need(it.first->second==ids,"one canonical plane has conflicting orbit IDs");
            auto base=g.bases.find(ids);if(base==g.bases.end()||key<base->second)g.bases[ids]=key;
            g.collision_pairs++;
        }
        a=b;
    }
    return g;
}
struct Prepared {
    Pool pool;vector<vector<Point>> full;vector<vector<uint32_t>> xs;vector<uint32_t> target_keys;
    unordered_map<uint32_t,uint16_t> target_index;double prepare_seconds=0;
    explicit Prepared(const string& path):pool(path){
        auto start=chrono::steady_clock::now();need(pool.reps[0].x!=0&&oncurve(pool.reps[0])&&scalar(pool.reps[0],ORDER).inf(),"bad generator");
        // 262543 is prime: complete trial division through its integer square root.
        for(uint32_t d=2;uint64_t(d)*d<=ORDER;d++)need(ORDER%d!=0,"declared subgroup order composite");
        unordered_set<uint64_t> all_points;unordered_set<uint32_t> all_x;
        for(int i=0;i<37;i++){
            Point p=pool.reps[i];need(p.x!=0&&oncurve(p)&&scalar(p,ORDER).inf(),"bad pool representative");
            vector<Point> members;unordered_set<uint64_t> seen;vector<uint32_t> xvals;
            for(int j=0;j<19;j++){need(oncurve(p)&&scalar(p,ORDER).inf(),"bad conjugate");Point n=neg(p);
                for(Point q:{p,n}){need(seen.insert(pointcode(q)).second,"orbit has duplicate signed point");members.push_back(q);need(all_points.insert(pointcode(q)).second,"pool signed orbit overlaps");}
                need(all_x.insert(p.x).second,"pool x orbit overlaps");xvals.push_back(p.x);p=frob(p);
            }
            need(p==pool.reps[i]&&members.size()==38&&seen.size()==38,"orbit not length 38");
            sort(members.begin(),members.end());full.push_back(std::move(members));xs.push_back(std::move(xvals));
        }
        need(all_points.size()==1406&&all_x.size()==703,"pool expansion cardinality mismatch");
        unordered_set<uint32_t> keys;unordered_set<uint64_t> target_points;
        for(auto d:pool.public_scalars){need(d>0&&d<ORDER,"invalid public representative scalar");Point q=scalar(pool.reps[0],d);
            need(!q.inf()&&oncurve(q)&&scalar(q,ORDER).inf(),"bad public target");
            need(keys.insert(xkey(q.x)).second,"duplicate signed target orbit");
            Point current=q;unordered_set<uint64_t> one_orbit;
            for(int shift=0;shift<19;shift++){
                for(Point p:{current,neg(current)}){
                    // Frobenius and sign are group automorphisms, so subgroup
                    // membership follows from the checked representative q.
                    need(!p.inf()&&oncurve(p),"invalid signed target conjugate");
                    need(one_orbit.insert(pointcode(p)).second,"target signed orbit shorter than 38");
                    need(target_points.insert(pointcode(p)).second,"target signed orbit overlap");
                }
                current=frob(current);
            }
            need(current==q&&one_orbit.size()==38,"target signed orbit not exactly 38");
        }
        need(keys.size()==TARGETS&&target_points.size()==ORDER-1,"target orbit partition mismatch");
        target_keys.assign(keys.begin(),keys.end());sort(target_keys.begin(),target_keys.end());
        for(size_t i=0;i<target_keys.size();i++)target_index[target_keys[i]]=uint16_t(i);
        prepare_seconds=seconds(start);
    }
    int index(Point p)const{if(p.inf())return -1;auto it=target_index.find(xkey(p.x));need(it!=target_index.end(),"nonidentity sum absent from verified target partition");return it->second;}
};
struct Bits {
    array<uint64_t,WORDS> w{};
    void set(int k){if(k>=0)w[k>>6]|=uint64_t(1)<<(k&63);}
    void unite(const Bits& b){for(size_t i=0;i<WORDS;i++)w[i]|=b.w[i];}
    int count()const{int n=0;for(auto x:w)n+=__builtin_popcountll(x);return n;}
};
static void write_u32(ofstream& o,uint32_t v){for(int i=0;i<4;i++)o.put(char(v>>(8*i)));}
static void write_u64(ofstream& o,uint64_t v){for(int i=0;i<8;i++)o.put(char(v>>(8*i)));}
struct Cache {
    vector<Bits> triple,pair;array<array<int,37>,37> pidx{};int tidx[37][37][37]{};
    vector<array<int,3>> tnames;vector<array<int,2>> pnames;
    double pair_seconds=0,triple_seconds=0;
    explicit Cache(const Prepared& prep){
        auto start=chrono::steady_clock::now();
        for(int i=0;i<37;i++)for(int j=i;j<37;j++){
            int k=pair.size();pidx[i][j]=pidx[j][i]=k;pnames.push_back({i,j});Bits b;
            for(Point z:batch_add(prep.pool.reps[i],prep.full[j]))b.set(prep.index(z));
            pair.push_back(b);
        }
        need(pair.size()==703,"pair support count");pair_seconds=seconds(start);start=chrono::steady_clock::now();
        for(int i=0;i<37;i++)for(int j=i;j<37;j++)for(int k=j;k<37;k++){
            int index=triple.size();tnames.push_back({i,j,k});int ids[3]={i,j,k};sort(ids,ids+3);do{tidx[ids[0]][ids[1]][ids[2]]=index;}while(next_permutation(ids,ids+3));
            Bits b;for(Point q:prep.full[j]){Point pq=add(prep.pool.reps[i],q);for(Point z:batch_add(pq,prep.full[k]))b.set(prep.index(z));}
            triple.push_back(b);
        }
        need(triple.size()==9139,"triple support count");triple_seconds=seconds(start);
    }
    void save(const string& path,const string& manifest)const{
        ofstream o(path,ios::binary);need(bool(o),"cannot create support cache");
        o.write("KIC19S01",8);write_u32(o,1);write_u32(o,TARGETS);write_u32(o,WORDS);write_u32(o,triple.size());write_u32(o,pair.size());
        for(auto& b:triple)for(auto x:b.w)write_u64(o,x);
        for(auto& b:pair)for(auto x:b.w)write_u64(o,x);
        o.close();need(bool(o),"support cache write failed");
        ofstream m(manifest);m<<"{\n  \"schema\": \"crypto.autoresearch.n19_support_cache.v1\",\n  \"byte_order\": \"little_endian\",\n";
        m<<"  \"target_orbits\": "<<TARGETS<<", \"words_per_support\": "<<WORDS<<", \"triple_supports\": "<<triple.size()<<", \"pair_supports\": "<<pair.size()<<",\n";
        m<<"  \"triple_order\": \"i<=j<=k lexicographic\", \"pair_order\": \"i<=j lexicographic\",\n";
        m<<"  \"cache_bytes\": "<<filesystem_size(path)<<", \"cache_sha256\": \""<<sha_file(path)<<"\"\n}\n";
    }
    static uint64_t filesystem_size(const string& path){ifstream f(path,ios::binary|ios::ate);return uint64_t(f.tellg());}
};
struct Score {I4 ids{};int exact=0,atmost=0;bool plane=false;X4 key{};};
static pair<int,int> score_base(const Prepared& prep,const Cache& cache,I4 ids){
    Bits e,a;for(int x=0;x<4;x++)for(int y=x;y<4;y++)for(int z=y;z<4;z++)e.unite(cache.triple[cache.tidx[ids[x]][ids[y]][ids[z]]]);
    a=e;for(int x=0;x<4;x++)for(int y=x;y<4;y++)a.unite(cache.pair[cache.pidx[ids[x]][ids[y]]]);
    for(int x:ids)a.set(prep.index(prep.pool.reps[x]));
    return {e.count(),a.count()};
}
static string i4json(I4 a){return "["+to_string(a[0])+","+to_string(a[1])+","+to_string(a[2])+","+to_string(a[3])+"]";}
static string x4json(X4 a){return "["+to_string(a[0])+","+to_string(a[1])+","+to_string(a[2])+","+to_string(a[3])+"]";}
static void save_geometry(const string& out,const Geometry& g,const Prepared& prep,double wall){
    ofstream geom(out+"/geometry.json");geom<<"{\n\"schema\":\"crypto.autoresearch.n19_geometry.v1\",\"pool_orbits\":37,\"x_values\":703,\"points\":1406,";
    geom<<"\"target_orbits\":6909,\"canonical_planes\":"<<g.planes.size()<<",\"plane_compatible_bases\":"<<g.bases.size()<<",\"pair_collision_partitions\":"<<g.collision_pairs<<",\"plane_discovery_wall_seconds\":"<<setprecision(17)<<wall<<",\"preparation_wall_seconds\":"<<prep.prepare_seconds<<",\"target_keys\":"<<nums_json(prep.target_keys)<<"}\n";
    ofstream cat(out+"/plane_catalogue.json");cat<<"{\n\"schema\":\"crypto.autoresearch.n19_plane_catalogue.v1\",\"planes\":[";
    bool first=true;for(auto& [key,ids]:g.planes){if(!first)cat<<",";first=false;uint32_t a=key[0],b=key[0]^key[1],c=key[0]^key[2];
        need(a!=0&&b!=0&&c!=0&&b!=c&&X4{a,a^b,a^c,a^b^c}!=X4{},"bad affine triple");
        X4 check={a,a^b,a^c,a^b^c};sort(check.begin(),check.end());need(check==key,"plane coordinate reconstruction failed");
        cat<<"{\"key\":"<<x4json(key)<<",\"orbit_ids\":"<<i4json(ids)<<",\"a\":"<<a<<",\"b\":"<<b<<",\"c\":"<<c<<"}";
    }cat<<"]}\n";
}
static void save_scores(const string& out,const Prepared& prep,const Cache& cache,const Geometry& geom,const string& historical){
    auto start=chrono::steady_clock::now();vector<Score> scores;scores.reserve(66045);map<int,int> hist;
    int global=-1,global_at=-1,prior_e=-1,prior_a=-1;
    for(int a=0;a<37;a++)for(int b=a+1;b<37;b++)for(int c=b+1;c<37;c++)for(int d=c+1;d<37;d++){
        I4 ids={a,b,c,d};auto [e,at]=score_base(prep,cache,ids);auto it=geom.bases.find(ids);
        scores.push_back({ids,e,at,it!=geom.bases.end(),it==geom.bases.end()?X4{}:it->second});
        hist[at]++;global=max(global,e);global_at=max(global_at,at);if(ids==I4{6,9,22,28}){prior_e=e;prior_a=at;}
    }
    need(scores.size()==66045,"frontier cardinality mismatch");
    need(prior_e==6224&&prior_a==6257,"frozen chosen-prior coverage regression failed");
    need(hist==historical_histogram(historical)&&global_at==6257&&hist.at(6257)==1,
         "amended full at-most-three historical histogram regression failed");
    vector<I4> global_exact_indices;for(const auto& score:scores)if(score.exact==global)global_exact_indices.push_back(score.ids);
    vector<size_t> ranked(scores.size());iota(ranked.begin(),ranked.end(),0);
    stable_sort(ranked.begin(),ranked.end(),[&](size_t x,size_t y){
        const auto& a=scores[x];const auto& b=scores[y];
        if(a.exact!=b.exact)return a.exact>b.exact;if(a.atmost!=b.atmost)return a.atmost>b.atmost;
        if(a.ids!=b.ids)return a.ids<b.ids;return a.key<b.key;
    });
    vector<size_t> plane_rank;for(size_t idx:ranked)if(scores[idx].plane)plane_rank.push_back(idx);
    ofstream o(out+"/base_scores.json");o<<"{\"schema\":\"crypto.autoresearch.n19_base_frontier.v1\",\"count\":66045,\"global_exact_max\":"<<global<<",\"global_exact_max_indices\":[";
    for(size_t i=0;i<global_exact_indices.size();i++){if(i)o<<",";o<<i4json(global_exact_indices[i]);}
    o<<"],\"global_at_most_max\":"<<global_at<<",\"historical_at_most_histogram_sha256\":\""<<sha_file(historical)<<"\",\"prior_exact\":"<<prior_e<<",\"prior_at_most\":"<<prior_a<<",\"at_most_histogram\":{";
    bool first=true;for(auto [k,v]:hist){if(!first)o<<",";first=false;o<<"\""<<k<<"\":"<<v;}o<<"},\"ranked_scores\":[";
    for(size_t pos=0;pos<ranked.size();pos++){if(pos)o<<",";const Score& s=scores[ranked[pos]];
        o<<"{\"rank\":"<<pos+1<<",\"orbit_ids\":"<<i4json(s.ids)<<",\"exact_three\":"<<s.exact<<",\"at_most_three\":"<<s.atmost<<",\"plane_compatible\":"<<(s.plane?"true":"false");
        if(s.plane)o<<",\"plane_key\":"<<x4json(s.key);o<<"}";
    }o<<"]}\n";o.close();need(bool(o),"base_scores write failed");
    ofstream selected(out+"/selected.json");selected<<"{\"schema\":\"crypto.autoresearch.n19_selected_base.v1\",\"candidate_exists\":"<<(!plane_rank.empty()?"true":"false");
    if(!plane_rank.empty()){const Score& s=scores[plane_rank[0]];uint32_t a=s.key[0],b=a^s.key[1],c=a^s.key[2];
        selected<<",\"orbit_ids\":"<<i4json(s.ids)<<",\"plane_key\":"<<x4json(s.key)<<",\"affine_coordinates\":["<<a<<","<<b<<","<<c<<"],\"exact_three\":"<<s.exact<<",\"at_most_three\":"<<s.atmost<<",\"ratio_to_prior_6224\":"<<setprecision(17)<<double(s.exact)/6224.0<<",\"ratio_to_measured_global_exact\":"<<double(s.exact)/global;}
    selected<<",\"plane_compatible_base_count\":"<<plane_rank.size()<<",\"frontier_scoring_wall_seconds\":"<<setprecision(17)<<seconds(start)<<"}\n";
}
static void controls(const string& input,const string& out){
    auto start=chrono::steady_clock::now();Prepared prep(input);uint64_t products=0,group_pairs=0;
    uint32_t x=2;for(int i=0;i<19;i++)x=sq(x);need(x==2,"Frobenius irreducibility condition failed");
    need(gcdpoly(uint64_t(2)^uint64_t(refsq(2)),POLY)==1,"irreducibility gcd condition failed");
    for(int i=0;i<19;i++)for(int j=0;j<19;j++){need(mul(1u<<i,1u<<j)==refmul(1u<<i,1u<<j),"monomial field discrepancy");products++;}
    for(int i=0;i<19;i++){need(sq(1u<<i)==refsq(1u<<i),"basis square discrepancy");need(mul(1u<<i,inv(1u<<i))==1,"basis inverse discrepancy");}
    for(int i=0;i<4096;i++){auto h=digest("N19-AFFINE-v1-field-"+to_string(i));uint32_t a=h[0]&MASK,b=h[1]&MASK;
        need(a!=0,"frozen inverse-control first operand is zero");
        need(mul(a,b)==refmul(a,b),"field sampled product discrepancy");products++;
        need(mul(a,inv(a))==1,"sampled inverse discrepancy");}
    for(Point p:prep.pool.reps){need(oncurve(p)&&scalar(p,ORDER).inf(),"representative subgroup discrepancy");need(add(p,infinity())==p&&add(p,neg(p)).inf()&&add(p,p)==refadd(p,p),"representative group discrepancy");}
    for(int i=0;i<4096;i++){auto h=digest("N19-AFFINE-v1-group-"+to_string(i));Point a=prep.full[h[0]%37][h[2]%38],b=prep.full[h[1]%37][h[3]%38];
        need(oncurve(a)&&oncurve(b)&&scalar(a,ORDER).inf()&&scalar(b,ORDER).inf(),"sampled subgroup discrepancy");
        need(add(a,b)==refadd(a,b)&&add(b,a)==refadd(b,a),"sampled point addition discrepancy");
        vector<Point> exceptional={infinity(),a,neg(a),b,neg(b)};
        auto batched=batch_add(a,exceptional);need(batched.size()==exceptional.size(),"batch output length mismatch");
        for(size_t k=0;k<exceptional.size();k++){
            need(batched[k]==refadd(a,exceptional[k]),"batch exceptional/addition discrepancy");
            need(batched[k].inf()||(batched[k].x<FIELD&&batched[k].y<FIELD&&oncurve(batched[k])),"batch field-range discrepancy");
        }
        group_pairs++;}
    vector<vector<uint32_t>> first8(prep.xs.begin(),prep.xs.begin()+8);Geometry fast=enumerate_planes(first8,8);
    unordered_map<uint32_t,uint8_t> owner;for(int i=0;i<8;i++)for(auto v:first8[i])owner[v]=i;
    set<X4> slow;vector<uint32_t> all;for(auto& v:first8)all.insert(all.end(),v.begin(),v.end());sort(all.begin(),all.end());
    for(size_t a=0;a<all.size();a++)for(size_t b=a+1;b<all.size();b++)for(size_t c=b+1;c<all.size();c++){
        uint32_t d=all[a]^all[b]^all[c];if(d<=all[c])continue;auto hit=owner.find(d);if(hit==owner.end())continue;
        I4 ids=orbit_ids({owner[all[a]],owner[all[b]],owner[all[c]],hit->second});
        if(adjacent_find(ids.begin(),ids.end())!=ids.end())continue;
        slow.insert(canonical({all[a],all[b],all[c],d}));
    }
    need(slow.size()==fast.planes.size(),"first-eight exhaustive triple plane count mismatch");
    for(auto& [key,ids]:fast.planes)need(slow.count(key),"first-eight exhaustive triple plane key mismatch");
    auto reverse19=[](uint32_t v){uint32_t o=0;for(int i=0;i<19;i++)o=(o<<1)|((v>>i)&1);return o;};
    for(auto& [key,ids]:fast.planes){auto a=reverse19(key[0]),b=reverse19(key[1]),c=reverse19(key[2]),d=reverse19(key[3]);need((a^b^c^d)==0,"bit reversal plane invariance failed");}
    ofstream f(out+"/controls.json");f<<"{\"schema\":\"crypto.autoresearch.n19_native_controls.v1\",\"status\":\"passed\",\"field_products\":"<<products<<",\"sampled_group_pairs\":"<<group_pairs<<",\"batched_group_cases\":"<<group_pairs*5<<",\"first_eight_pair_planes\":"<<fast.planes.size()<<",\"first_eight_triple_planes\":"<<slow.size()<<",\"field_irreducibility\":true,\"signed_orbit_points\":1406,\"target_orbits\":6909,\"wall_seconds\":"<<setprecision(17)<<seconds(start)<<"}\n";
}
static void science(const string& input,const string& out,const string& historical){
    auto start=chrono::steady_clock::now();Prepared prep(input);
    ofstream progress(out+"/progress.jsonl",ios::app);progress<<"{\"stage\":\"prepared\",\"seconds\":"<<setprecision(17)<<seconds(start)<<"}\n";progress.flush();
    auto gstart=chrono::steady_clock::now();Geometry g=enumerate_planes(prep.xs,37);save_geometry(out,g,prep,seconds(gstart));
    progress<<"{\"stage\":\"geometry\",\"seconds\":"<<seconds(gstart)<<",\"planes\":"<<g.planes.size()<<"}\n";progress.flush();
    auto cstart=chrono::steady_clock::now();Cache cache(prep);cache.save(out+"/support_cache.bin",out+"/support_cache_manifest.json");
    progress<<"{\"stage\":\"support_cache\",\"seconds\":"<<seconds(cstart)<<",\"triple_supports\":"<<cache.triple.size()<<"}\n";progress.flush();
    save_scores(out,prep,cache,g,historical);progress<<"{\"stage\":\"frontier_complete\",\"seconds\":"<<seconds(start)<<"}\n";progress.flush();
}
int main(int argc,char** argv){
    try{
        need(argc==5,"usage: search --controls|--science POOL_JSON OUTPUT_DIR HISTORICAL_GLOBAL_JSONL");
        string phase=argv[1],input=argv[2],out=argv[3],historical=argv[4];
        if(phase=="--controls")controls(input,out);
        else if(phase=="--science")science(input,out,historical);
        else throw runtime_error("unrecognized phase");
        return 0;
    }catch(const exception& e){cerr<<"FAILED_IMPLEMENTATION: "<<e.what()<<"\n";return 2;}
}
