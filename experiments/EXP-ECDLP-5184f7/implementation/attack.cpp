// Public synthetic ECDLP benchmark. The solver interface exposes group values,
// equality, addition and encodings, never target scalars or family tags.
#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <ctime>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <openssl/hmac.h>
#include <openssl/sha.h>
#include <random>
#include <sstream>
#include <stdexcept>
#include <string>
#include <sys/resource.h>
#include <unordered_map>
#include <vector>

using U = uint64_t;
using Wide = __uint128_t;
using Signed = __int128_t;
struct Cap {};
U inverse(U a, U p) {
    Signed t=0, n=1; U r=p, s=a;
    while(s) {U q=r/s, z=r-q*s; r=s; s=z; Signed v=t-Signed(q)*n; t=n; n=v;}
    if(r!=1) throw std::runtime_error("noninvertible element");
    t%=p; if(t<0)t+=p; return U(t);
}
U isqrt(U n) {U r=U(std::sqrt((long double)n)); while(Wide(r+1)*(r+1)<=n)++r; while(Wide(r)*r>n)--r; return r;}
double cpu_now(){return double(std::clock())/CLOCKS_PER_SEC;}
double wall_now(){return std::chrono::duration<double>(std::chrono::steady_clock::now().time_since_epoch()).count();}
std::string hex(const unsigned char* p,size_t n){std::ostringstream s; for(size_t i=0;i<n;++i)s<<std::hex<<std::setw(2)<<std::setfill('0')<<unsigned(p[i]);return s.str();}
struct Counts {U calls=0, muls=0, invs=0, doubles=0, adds=0, scalars=0, negs=0, encoding_products=0;};
void counters(const Counts& c){std::cout<<"{\"group_calls\":"<<c.calls<<",\"field_products\":"<<c.muls<<",\"field_inversions\":"<<c.invs<<",\"doublings\":"<<c.doubles<<",\"additions\":"<<c.adds<<",\"scalar_multiplications\":"<<c.scalars<<",\"negations\":"<<c.negs<<",\"encoding_products\":"<<c.encoding_products<<"}";}

class Group;
class Value {
    U x=0,y=0; bool infinity=true; std::array<unsigned char,32> label{};
    friend class Group;
public:
    friend bool operator==(const Value&a,const Value&b){return a.infinity==b.infinity&&(a.infinity||(a.x==b.x&&a.y==b.y));}
};
class Group {
    U p,A,B; bool opaque; U ux=1,uy=1; int width;
    std::array<unsigned char,32> oracle_key{};
    int phase_=0; double last_wall=wall_now(),last_cpu=cpu_now();
    U product(U a,U b){++counts[phase_].muls;return Wide(a)*b%p;}
    U inv(U a){++counts[phase_].invs;return inverse(a,p);}
    Value wrap(U x,U y,bool inf=false){Value v;v.x=x;v.y=y;v.infinity=inf;
        if(opaque){auto e=coordinate_encoding(v,false);unsigned int size=0;HMAC(EVP_sha256(),oracle_key.data(),32,e.data(),e.size(),v.label.data(),&size);}
        return v;}
    std::vector<unsigned char> coordinate_encoding(const Value&v,bool transport){
        if(v.infinity)return {0};U x=v.x,y=v.y;
        if(transport&&(ux!=1||uy!=1)){x=Wide(x)*ux%p;y=Wide(y)*uy%p;counts[phase_].encoding_products+=2;}
        std::vector<unsigned char> data(1+width);data[0]=2+(y&1);
        for(int i=0;i<width;++i)data[width-i]=(x>>(8*i))&255;
        return data;
    }
public:
    std::array<Counts,3> counts{};
    std::array<double,3> wall{},cpu{};
    U cap=0;
    Group(U pp,U aa,U bb,bool oracle,U u):p(pp),A(aa),B(bb),opaque(oracle){
        if(p> (U(1)<<40))throw std::runtime_error("attack field exceeds frozen toy boundary");
        width=(64-__builtin_clzll(p)+7)/8;
        if(u!=1){U invu=inverse(u,p);ux=Wide(invu)*invu%p;uy=Wide(ux)*invu%p;}
        const std::string domain="opaque-group-interface/server-key/20261011";
        SHA256(reinterpret_cast<const unsigned char*>(domain.data()),domain.size(),oracle_key.data());
    }
    void phase(int next){wall[phase_]+=wall_now()-last_wall;cpu[phase_]+=cpu_now()-last_cpu;phase_=next;last_wall=wall_now();last_cpu=cpu_now();}
    void finish(){phase(phase_);}
    Value point(U x,U y){if((Wide(y)*y%p)!=(Wide(x)*x%p*x%p+Wide(A)*x+B)%p)throw std::runtime_error("off-curve input");return wrap(x,y);}
    Value zero(){return wrap(0,0,true);}
    Value neg(const Value&v){++counts[phase_].negs;return v.infinity?v:wrap(v.x,v.y? p-v.y:0);}
    Value add(const Value&a,const Value&b){
        if(phase_==1&&cap&&counts[1].calls>=cap)throw Cap();++counts[phase_].calls;
        if(a.infinity)return b;if(b.infinity)return a;
        U numerator,denominator;
        if(a.x==b.x){if((a.y+b.y)%p==0)return zero();++counts[phase_].doubles;
            numerator=(product(3,product(a.x,a.x))+A)%p;denominator=product(2,a.y);
        }else{++counts[phase_].adds;numerator=(b.y+p-a.y)%p;denominator=(b.x+p-a.x)%p;}
        U slope=product(numerator,inv(denominator));U x=(product(slope,slope)+2*p-a.x-b.x)%p;
        U y=(product(slope,(a.x+p-x)%p)+p-a.y)%p;return wrap(x,y);
    }
    Value mul(Value v,U n){++counts[phase_].scalars;Value out=zero();while(n){if(n&1)out=add(out,v);n>>=1;if(n)v=add(v,v);}return out;}
    std::vector<unsigned char> encoding(const Value&v){if(opaque)return {v.label.begin(),v.label.end()};return coordinate_encoding(v,true);}
    size_t key(const Value&v)const{if(opaque){U x;std::copy_n(v.label.data(),8,reinterpret_cast<unsigned char*>(&x));return x;}
        if(v.infinity)return 0;U z=v.x^(v.y+0x9e3779b97f4a7c15ULL);z^=z>>30;z*=0xbf58476d1ce4e5b9ULL;z^=z>>27;return z;}
};
struct Hash {const Group*group;size_t operator()(const Value&v)const{return group->key(v);}};
struct State {Value value;U a,b;};
struct Collision {U calls,a,b,aa,bb,denom;long long q;std::string point;};
struct Result {long long q=-1;U restarts=0,iterations=0,M=0,entries=0,table_bytes=0;bool verified=false;std::string trace;std::vector<Collision> collisions;};
U uniform(std::mt19937_64&r,U n){U limit=UINT64_MAX-UINT64_MAX%n;U x;do{x=r();}while(x>=limit);return x%n;}
U partition(Group&g,const Value&v,U seed,U count){auto bytes=g.encoding(v);std::vector<unsigned char> input(8+bytes.size());
    for(int i=0;i<8;++i)input[7-i]=(seed>>(8*i))&255;std::copy(bytes.begin(),bytes.end(),input.begin()+8);
    unsigned char digest[32];SHA256(input.data(),input.size(),digest);return digest[31]%(count);}
void trace_update(SHA256_CTX&ctx,Group&g,const State&s){auto bytes=g.encoding(s.value);SHA256_Update(&ctx,bytes.data(),bytes.size());
    unsigned char coefficients[16];for(int i=0;i<8;++i){coefficients[7-i]=(s.a>>(8*i))&255;coefficients[15-i]=(s.b>>(8*i))&255;}SHA256_Update(&ctx,coefficients,16);}
Result rho(Group&g,Value G,Value Q,U ell,U seed,U adding){
    Result result;std::mt19937_64 random(seed);std::vector<State> table;
    for(U i=0;i<adding;++i){U a=uniform(random,ell),b=uniform(random,ell);table.push_back({g.add(g.mul(G,a),g.mul(Q,b)),a,b});}
    SHA256_CTX trace;SHA256_Init(&trace);g.phase(1);
    auto step=[&](State s){U i=partition(g,s.value,seed,adding);s.value=g.add(s.value,table[i].value);
        s.a=(s.a+table[i].a)%ell;s.b=(s.b+table[i].b)%ell;++result.iterations;trace_update(trace,g,s);return s;};
    try{while(result.q<0){U a=uniform(random,ell),b=uniform(random,ell);State tortoise{g.add(g.mul(G,a),g.mul(Q,b)),a,b};
        trace_update(trace,g,tortoise);State hare=step(tortoise);U power=1,length=1;
        while(!(tortoise.value==hare.value)){if(length==power){tortoise=hare;power*=2;length=0;}hare=step(hare);++length;}
        U denominator=(hare.b+ell-tortoise.b)%ell;long long q=-1;
        if(denominator){q=Wide((tortoise.a+ell-hare.a)%ell)*inverse(denominator,ell)%ell;
            g.phase(2);result.verified=g.mul(G,U(q))==Q;g.phase(1);
            if(!result.verified)throw std::runtime_error("invalid rho collision scalar");result.q=q;
        }else ++result.restarts;
        auto encoded=g.encoding(tortoise.value);result.collisions.push_back({g.counts[1].calls,tortoise.a,tortoise.b,hare.a,hare.b,denominator,q,hex(encoded.data(),encoded.size())});
    }}catch(const Cap&){}
    unsigned char digest[32];SHA256_Final(digest,&trace);result.trace=hex(digest,32);return result;
}

// Count exactly the allocator-requested table node/bucket bytes, plus object
// size. This is distinct from process RSS and includes implementation overhead.
struct Allocation {static inline size_t bytes=0;};
template<class T>struct Alloc {
    using value_type=T;Alloc()=default;template<class V>Alloc(const Alloc<V>&){}
    T*allocate(size_t n){Allocation::bytes+=n*sizeof(T);return std::allocator<T>{}.allocate(n);}
    void deallocate(T*p,size_t n){Allocation::bytes-=n*sizeof(T);std::allocator<T>{}.deallocate(p,n);}
    template<class V>bool operator==(const Alloc<V>&)const{return true;}
};
Result bsgs(Group&g,Value G,Value Q,U ell){
    Result result;U root=isqrt(ell)+1;result.M=std::min<U>(4096,root);
    using Pair=std::pair<const Value,U>;std::unordered_map<Value,U,Hash,std::equal_to<Value>,Alloc<Pair>> table(0,Hash{&g});
    table.reserve(result.M);Value current=g.zero();
    for(U i=0;i<result.M;++i){table.emplace(current,i);current=g.add(current,G);}
    Value giant=g.neg(g.mul(G,result.M));result.entries=table.size();result.table_bytes=Allocation::bytes+sizeof(table);
    g.phase(1);current=Q;U cap=(ell+result.M-1)/result.M+1;
    for(U j=0;j<cap;++j){auto it=table.find(current);if(it!=table.end()){U q=(Wide(j)*result.M+it->second)%ell;
            g.phase(2);result.verified=g.mul(G,q)==Q;g.phase(1);if(!result.verified)throw std::runtime_error("invalid BSGS scalar");result.q=q;break;}
        current=g.add(current,giant);++result.iterations;}
    if(result.q<0)throw std::runtime_error("BSGS coverage failed");return result;
}

int main(int argc,char**argv){
    if(argc!=2){std::cerr<<"usage: attack public-jobs.txt\n";return 2;}
    std::ifstream input(argv[1]);if(!input)throw std::runtime_error("missing public job file");
    std::string line;
    while(std::getline(input,line)){
        if(line.empty())continue;std::istringstream fields(line);std::string id,mode;U adding,seed,p,A,B,ell,h,gx,gy,qx,qy,u;
        if(!(fields>>id>>mode>>adding>>seed>>p>>A>>B>>ell>>h>>gx>>gy>>qx>>qy>>u))throw std::runtime_error("malformed public job");
        Group group(p,A,B,mode=="oracle",mode=="transport"?u:1);Value G=group.point(gx,gy),Q=group.point(qx,qy);
        group.cap=isqrt(400*ell)+1;Result result;
        try{result=mode=="bsgs"?bsgs(group,G,Q,ell):rho(group,G,Q,ell,seed,adding);}
        catch(const std::exception&e){std::cerr<<id<<": "<<e.what()<<"\n";return 1;}
        group.finish();struct rusage usage{};getrusage(RUSAGE_SELF,&usage);
        std::cout<<"{\"job_id\":\""<<id<<"\",\"mode\":\""<<mode<<"\",\"adding\":"<<adding<<",\"seed\":"<<seed<<",\"ell\":"<<ell
                 <<",\"cap\":"<<group.cap<<",\"scalar\":";if(result.q<0)std::cout<<"null";else std::cout<<result.q;
        std::cout<<",\"verified\":"<<(result.verified?"true":"false")<<",\"censored\":"<<(result.q<0||Wide(group.counts[1].calls)*group.counts[1].calls>Wide(400)*ell?"true":"false")
                 <<",\"iterations\":"<<result.iterations<<",\"restarts\":"<<result.restarts<<",\"M\":"<<result.M<<",\"stored_entries\":"<<result.entries
                 <<",\"table_allocated_bytes\":"<<result.table_bytes<<",\"process_max_RSS_KiB\":"<<usage.ru_maxrss<<",\"trace_sha256\":\""<<result.trace<<"\",\"counts\":{\"setup\":";
        counters(group.counts[0]);std::cout<<",\"search\":";counters(group.counts[1]);std::cout<<",\"verification\":";counters(group.counts[2]);std::cout<<"},\"wall_seconds\":["<<std::setprecision(12)<<group.wall[0]<<","<<group.wall[1]<<","<<group.wall[2]<<"],\"cpu_seconds\":["<<group.cpu[0]<<","<<group.cpu[1]<<","<<group.cpu[2]<<"],\"collisions\":[";
        for(size_t i=0;i<result.collisions.size();++i){const auto&c=result.collisions[i];if(i)std::cout<<",";std::cout<<"{\"calls\":"<<c.calls<<",\"a\":"<<c.a<<",\"b\":"<<c.b<<",\"aprime\":"<<c.aa<<",\"bprime\":"<<c.bb<<",\"denominator\":"<<c.denom<<",\"point_encoding\":\""<<c.point<<"\",\"scalar\":";if(c.q<0)std::cout<<"null";else std::cout<<c.q;std::cout<<"}";}
        std::cout<<"]}\n"<<std::flush;
    }
}
