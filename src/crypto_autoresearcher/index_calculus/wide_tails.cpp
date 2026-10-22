// Exact, file-backed tail builder for odd prime fields below 2^63.
// Input: p a b h B followed by B lines of x y. Output: little-endian (x, code).
// The Python wrapper freezes and supervises this executable; this program
// never chooses a curve, factor base, target, or resource budget.
#include <algorithm>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <queue>
#include <stdexcept>
#include <string>
#include <vector>

using u64 = uint64_t;
using u128 = __uint128_t;
struct Point { u64 x, y; };
struct Level { u64 x, y, v, nv, first; };
struct Pair { u64 x, code; };

static u64 P, A, BASE;
static u64 addm(u64 a, u64 b) { u64 s=a+b; return s>=P ? s-P : s; }
static u64 subm(u64 a, u64 b) { return a>=b ? a-b : a+P-b; }
static u64 mulm(u64 a, u64 b) { return static_cast<u64>((u128)a*b % P); }
static u64 powm(u64 a, u64 n) {
    u64 r=1; for (;n;n>>=1,a=mulm(a,a)) if(n&1) r=mulm(r,a); return r;
}
static u64 first(u64 code) { return ((code>>1)%BASE)>>1; }
static bool less_pair(const Pair& a, const Pair& b) {
    if(a.x!=b.x) return a.x<b.x;
    u64 af=first(a.code), bf=first(b.code);
    return af!=bf ? af>bf : a.code<b.code;
}
static void write64(std::ostream& o,u64 x) {
    char b[8]; for(int i=0;i<8;++i) b[i]=static_cast<char>(x>>(8*i));
    o.write(b,8);
}
static bool read64(std::istream& in,u64& x) {
    char b[8]; if(!in.read(b,8)) return false;
    x=0; for(int i=7;i>=0;--i) x=(x<<8)|static_cast<unsigned char>(b[i]);
    return true;
}
static void write_pair(std::ostream& o,const Pair& p) { write64(o,p.x);write64(o,p.code); }
static bool read_pair(std::istream& in,Pair& p) {
    if(!read64(in,p.x)) return false;
    if(!read64(in,p.code)) throw std::runtime_error("truncated pair");
    return true;
}
static u64 checked_code(u64 digit,u64 v,u64 y) {
    u128 z=((u128)digit+(u128)BASE*v)*2+(y>P/2);
    if(z>UINT64_MAX) throw std::runtime_error("packed code overflow");
    return static_cast<u64>(z);
}
static u64 checked_digit(u64 digit,u64 v) {
    u128 z=(u128)digit+(u128)BASE*v;
    if(z>UINT64_MAX) throw std::runtime_error("tail digit overflow");
    return static_cast<u64>(z);
}
struct Sink {
    std::string dir; size_t cap; std::vector<Pair> buf; std::vector<std::string> paths;
    Sink(std::string d,size_t c):dir(std::move(d)),cap(c) { buf.reserve(c); }
    void add(Pair p) { buf.push_back(p);if(buf.size()==cap) flush(); }
    void flush() {
        if(buf.empty()) return;
        std::sort(buf.begin(),buf.end(),less_pair);
        std::string path=dir+"/chunk-"+std::to_string(paths.size())+".bin";
        std::ofstream out(path,std::ios::binary); if(!out) throw std::runtime_error("open chunk");
        for(auto p:buf) write_pair(out,p);
        if(!out) throw std::runtime_error("write chunk");
        paths.push_back(path);buf.clear();
    }
    u64 merge(const std::string& target) {
        flush();
        struct Reader { std::ifstream in; Pair p{}; bool valid=false; };
        std::vector<Reader> readers(paths.size());
        struct Node { Pair p; size_t i; };
        auto worse=[](const Node& a,const Node& b){ return less_pair(b.p,a.p); };
        std::priority_queue<Node,std::vector<Node>,decltype(worse)> q(worse);
        for(size_t i=0;i<paths.size();++i) {
            readers[i].in.open(paths[i],std::ios::binary);
            if(!readers[i].in) throw std::runtime_error("open merge input");
            if(read_pair(readers[i].in,readers[i].p)) q.push({readers[i].p,i});
        }
        std::ofstream out(target,std::ios::binary); if(!out) throw std::runtime_error("open final");
        u64 n=0; Pair prev{}; bool have=false;
        while(!q.empty()) {
            Node cur=q.top();q.pop();
            if(have && less_pair(cur.p,prev)) throw std::runtime_error("merge order");
            write_pair(out,cur.p);prev=cur.p;have=true;++n;
            if(read_pair(readers[cur.i].in,readers[cur.i].p)) q.push({readers[cur.i].p,cur.i});
        }
        if(!out) throw std::runtime_error("write final");
        return n;
    }
};
static void append_level(std::vector<Level>& next,u64 a,u64 v,u64 nv,Point p) {
    next.push_back({p.x,p.y,v,nv,a});
}
int main(int argc,char** argv) {
 try {
    if(argc!=5) throw std::runtime_error("usage: wide_tails input.txt scratch_dir output.bin chunk_entries");
    std::ifstream in(argv[1]);if(!in) throw std::runtime_error("open input");
    u64 b;int h;in>>P>>A>>b>>h>>BASE;
    if(!in||P<3||P>=(1ULL<<63)||!(P&1)||h<2||h>8||BASE<2||BASE%2)
        throw std::runtime_error("invalid header");
    size_t B=BASE/2;std::vector<Point> fb(B);
    for(auto& p:fb) {in>>p.x>>p.y;if(!in||p.x>=P||p.y>=P) throw std::runtime_error("invalid point");}
    std::vector<Level> level;level.reserve(B);
    for(size_t i=0;i<B;++i) level.push_back({fb[i].x,fb[i].y,2*i,2*i+1,i});
    Sink sink(argv[2],std::stoull(argv[4]));
    u64 charges=0,inverse_batches=0,exceptions=0;
    auto t0=std::chrono::steady_clock::now();
    for(int k=2;k<=h;++k) {
        std::vector<Level> next;
        for(size_t a=0;a<B;++a) {
            auto start=std::lower_bound(level.begin(),level.end(),a,
                [](const Level& e,size_t x){return e.first<x;});
            size_t off=start-level.begin(),n=level.size()-off;
            if(!n) continue;
            charges+=n;++inverse_batches;
            std::vector<u64> pref(n+1);pref[0]=1;
            for(size_t j=0;j<n;++j) {
                u64 dx=subm(level[off+j].x,fb[a].x);
                pref[j+1]=mulm(pref[j],dx ? dx : 1);
            }
            u64 inv=powm(pref[n],P-2);
            for(size_t j=n;j-->0;) {
                const Level& s=level[off+j];
                u64 dx=subm(s.x,fb[a].x),dxinv=mulm(pref[j],inv);
                inv=mulm(inv,dx ? dx : 1);
                Point out[2]{}; bool ok[2]={true,true};
                if(dx) {
                    u64 sx=addm(fb[a].x,s.x);
                    for(int sign=0;sign<2;++sign) {
                        u64 sy=sign ? subm(0,s.y) : s.y;
                        u64 lam=mulm(subm(sy,fb[a].y),dxinv);
                        u64 x=subm(mulm(lam,lam),sx);
                        out[sign]={x,subm(mulm(lam,subm(fb[a].x,x)),fb[a].y)};
                    }
                } else {
                    ++exceptions;
                    u64 den=addm(fb[a].y,fb[a].y);
                    if(!den) throw std::runtime_error("unsupported two-torsion point");
                    u64 x2=mulm(fb[a].x,fb[a].x);
                    u64 lam=mulm(addm(addm(x2,x2),x2),powm(den,P-2));
                    lam=addm(lam,mulm(A,powm(den,P-2)));
                    u64 x=subm(mulm(lam,lam),addm(fb[a].x,fb[a].x));
                    Point doubled{x,subm(mulm(lam,subm(fb[a].x,x)),fb[a].y)};
                    if(s.y==fb[a].y) {out[0]=doubled;ok[1]=false;}
                    else if(s.y==subm(0,fb[a].y)) {ok[0]=false;out[1]=doubled;}
                    else throw std::runtime_error("same x has invalid y");
                }
                for(int sign=0;sign<2;++sign) if(ok[sign]) {
                    u64 v=checked_digit(2*a,s.v),nv=checked_digit(2*a+1,s.nv);
                    if(sign) {v=checked_digit(2*a,s.nv);nv=checked_digit(2*a+1,s.v);}
                    if(k==h) sink.add({out[sign].x,checked_code(2*a,sign?s.nv:s.v,out[sign].y)});
                    else append_level(next,a,v,nv,out[sign]);
                }
            }
        }
        if(k<h) level.swap(next);
    }
    u64 entries=sink.merge(argv[3]);
    auto secs=std::chrono::duration<double>(std::chrono::steady_clock::now()-t0).count();
    std::cout<<"{\"entries\":"<<entries<<",\"s3_solves\":"<<charges
             <<",\"inverse_batches\":"<<inverse_batches<<",\"exceptions\":"<<exceptions
             <<",\"chunks\":"<<sink.paths.size()<<",\"seconds\":"<<secs<<"}\n";
    return 0;
 } catch(const std::exception& e) {std::cerr<<e.what()<<"\n";return 2;}
}
