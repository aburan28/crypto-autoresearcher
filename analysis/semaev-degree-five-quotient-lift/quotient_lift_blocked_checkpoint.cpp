// Separate blocked-rewrite checkpoint candidate; requires new integration qualification.
// See BOUNDED-EXPORT-MEMORY.md; requires launcher RLIMIT and actual placement.
// Frozen original quotient_lift.cpp and running trials remain unchanged.
// Output is untrusted until the original independent checker accepts it.
#include <m4ri/m4ri.h>
#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <vector>
using U = uint64_t;
static int N, D;
static U choose_[64][7], offsets[7];
static std::vector<U> masks;
static U column(U m) {
    int k=0; U rank=0, t=m;
    while(t) { int x=__builtin_ctzll(t); rank+=choose_[x][++k]; t&=t-1; }
    return offsets[k]+rank;
}
static void universe() {
    for(int n=0;n<=N;n++) { choose_[n][0]=1; for(int k=1;k<=D;k++)
        choose_[n][k]=(n?choose_[n-1][k-1]+choose_[n-1][k]:0); }
    U count=0;
    for(int d=D;d>=0;d--) { offsets[d]=count; count+=choose_[N][d]; }
    if(count>INT32_MAX) throw std::runtime_error("monomial universe exceeds native index range");
    masks.resize(count);
    for(int d=D;d>=0;d--) {
        if(!d) { masks[offsets[d]]=0; continue; }
        U m=(U(1)<<d)-1;
        for(U j=0;j<choose_[N][d];j++) {
            masks[offsets[d]+j]=m;
            U u=m&-m, v=m+u; m=v+(((v^m)/u)>>2);
        }
    }
}
static void read_exact(FILE* f, void* p, size_t size, size_t count) {
    if(fread(p,size,count,f)!=count) throw std::runtime_error("truncated seed certificate");
}
static void write_exact(FILE* f, const void* p, size_t size, size_t count) {
    if(fwrite(p,size,count,f)!=count) throw std::runtime_error("certificate write failed");
}
static long leading(mzd_t* A, long row) {
    word* p=mzd_row(A,row);
    for(wi_t w=0;w<A->width;w++) if(p[w]) return w*64+__builtin_ctzll(p[w]);
    return -1;
}
static void xor_row(word* dst, const word* src, size_t width) {
    for(size_t w=0;w<width;w++) dst[w]^=src[w];
}
static bool kills_constant(mzd_t* A, long rank, mzd_t* map) {
    std::vector<word> v(map->width);
    std::memcpy(v.data(),mzd_row(map,map->nrows-1),map->width*sizeof(word));
    std::vector<long> piv(map->ncols,-1);
    for(long i=0;i<rank;i++) piv.at(leading(A,i))=i;
    while(true) {
        long c=-1;
        for(size_t w=0;w<v.size();w++) if(v[w]) { c=w*64+__builtin_ctzll(v[w]); break; }
        if(c<0) return true;
        if(piv[c]<0) return false;
        xor_row(v.data(),mzd_row(A,piv[c]),v.size());
    }
}
static void append(mzd_t*& A, long& rank, mzd_t* E) {
    mzd_t* B=mzd_init(rank+E->nrows,E->ncols);
    for(long i=0;i<rank;i++) std::memcpy(mzd_row(B,i),mzd_row(A,i),E->width*sizeof(word));
    for(long i=0;i<E->nrows;i++) std::memcpy(mzd_row(B,rank+i),mzd_row(E,i),E->width*sizeof(word));
    mzd_free(A); A=B; rank=mzd_echelonize_m4ri(A,0,0);
}
static void export_map(const char* path,mzd_t* map,mzd_t* A,long rank) {
    long work=map->ncols, nq=work-rank;
    std::vector<long> pivot(work,-1), free(work,-1);
    for(long i=0;i<rank;i++) pivot.at(leading(A,i))=i;
    long q=0; for(long i=0;i<work;i++) if(pivot[i]<0) free[i]=q++;
    if(q!=nq || nq<=0) throw std::runtime_error("invalid export rank");
    mzd_t* projection=mzd_init(work,nq);
    for(long c=work-1;c>=0;c--) {
        if(free[c]>=0) { mzd_write_bit(projection,c,free[c],1); continue; }
        word* src=mzd_row(A,pivot[c]); word* dst=mzd_row(projection,c);
        for(long w=c/64;w<A->width;w++) {
            U v=src[w];
            // Avoid the historical producer's shift-by-64 expression.
            if(w==c/64) v=(c%64==63)?0:(v & ~((U(1)<<(c%64+1))-1));
            while(v) { int b=__builtin_ctzll(v); v&=v-1;
                xor_row(dst,mzd_row(projection,w*64+b),projection->width); }
        }
    }
    FILE* f=fopen(path,"wbx"); if(!f) throw std::runtime_error("output exists or cannot be created");
    int64_t hdr[4]={N,D,map->nrows,nq}; write_exact(f,hdr,8,4);
    write_exact(f,masks.data(),8,masks.size());
    // Apply the same linear projection in bounded matrix blocks. This does
    // not change quotient coordinates, row order, or the certificate format.
    // Admission reserves a 4096-row output block rather than a full map.
    // Projection storage is covered by the working-coordinate allowance.
    constexpr long export_rows=4096;
    for(long start=0;start<map->nrows;start+=export_rows) {
        long end=std::min(long(map->nrows),start+export_rows);
        mzd_t* window=mzd_init_window(map,start,0,end,map->ncols);
        mzd_t* product=mzd_mul(nullptr,window,projection,0);
        mzd_free_window(window);
        for(long i=0;i<product->nrows;i++)
            write_exact(f,mzd_row(product,i),8,product->width);
        mzd_free(product);
    }
    if(fclose(f)) throw std::runtime_error("certificate close failed");
    mzd_free(projection);
}
#include "quotient_checkpoint.hpp"
int main(int argc,char** argv) try {
    if(argc<3 || argc>5) throw std::runtime_error("usage: quotient_lift SEED OUTPUT [chunk_rows=4096] [memory_bytes=8589934592]");
    const U endian=1; if(*reinterpret_cast<const unsigned char*>(&endian)!=1) throw std::runtime_error("little-endian host required");
    long chunk=argc>3?std::stol(argv[3]):4096;
    U limit=argc>4?std::stoull(argv[4]):U(8)<<30;
    if(chunk<1 || chunk>60000 || limit>(U(96)<<30)) throw std::runtime_error("invalid resource arguments");
    Checkpoint checkpoint(argv[1]);
    FILE* f=fopen(argv[1],"rb"); if(!f) throw std::runtime_error("cannot open seed");
    int64_t hdr[4]; read_exact(f,hdr,8,4);
    if(hdr[0]<3 || hdr[0]>52 || hdr[1]<1 || hdr[1]>4 || hdr[1]>=hdr[0] || hdr[2]<1 || hdr[3]<1 || hdr[3]>hdr[2]) throw std::runtime_error("invalid seed header");
    N=hdr[0]; D=hdr[1]+1; universe();
    long high=choose_[N][D], old=hdr[2], nq=hdr[3];
    if(old!=long(masks.size())-high) throw std::runtime_error("seed universe size mismatch");
    U qw=(nq+63)/64;
    if(__uint128_t(old)*(qw+2)*8+__uint128_t(masks.size())*40 > limit/2) throw std::runtime_error("seed allocation gate refused");
    std::vector<U> seed_masks(old); read_exact(f,seed_masks.data(),8,old);
    for(long j=0;j<old;j++) if(seed_masks[j]!=masks[high+j]) throw std::runtime_error("seed monomial order mismatch");
    mzd_t* seed=mzd_init(old,nq);
    std::vector<long> rep(nq,-1), repq(old,-1);
    for(long j=0;j<old;j++) {
        word* row=mzd_row(seed,j); read_exact(f,row,8,qw);
        if(nq%64 && (row[qw-1]>>(nq%64))) throw std::runtime_error("seed bit outside codomain");
        long unit=-1; bool multiple=false;
        for(U w=0;w<qw;w++) if(row[w]) {
            if(unit>=0 || (row[w]&(row[w]-1))) multiple=true;
            unit=w*64+__builtin_ctzll(row[w]);
        }
        if(unit>=0 && !multiple) rep[unit]=j;
    }
    if(fgetc(f)!=EOF) throw std::runtime_error("seed has trailing bytes"); fclose(f);
    for(long q=0;q<nq;q++) { if(rep[q]<0) throw std::runtime_error("seed is not unit-surjective"); repq[rep[q]]=q; }
    std::vector<word> allowed(qw,0);
    for(long j=old-1;j>=0;j--) {
        if(repq[j]>=0) allowed[repq[j]/64]|=U(1)<<(repq[j]%64);
        else for(U w=0;w<qw;w++) if(mzd_row(seed,j)[w]&~allowed[w]) throw std::runtime_error("nontriangular seed");
    }
    std::vector<long> divisor(high,-1), missing(high,-1), standard;
    for(long i=0;i<high;i++) {
        U t=masks[i], best=std::numeric_limits<U>::max();
        while(t) { int x=__builtin_ctzll(t); t&=t-1; U m=masks[i]^(U(1)<<x); long c=column(m)-high;
            if(repq[c]<0 && m<best) { best=m; divisor[i]=c; missing[i]=x; } }
        if(divisor[i]<0) standard.push_back(i);
    }
    long nhigh=standard.size(), work=nq+nhigh;
    U stride=((work+63)/64+2)*8, seedstride=(qw+2)*8;
    // Includes one full map and one bounded export product (<=4096 rows),
    // seed, relation copies/products, coordinate actions, low rows and indices.
    // Projection has <=work rows and <=work columns; the 3*work term
    // remains available during export alongside A. Margin and RLIMIT remain.
    __uint128_t payload=(__uint128_t(masks.size())+4096)*stride + __uint128_t(old)*seedstride
        + __uint128_t(3*work+4*chunk+nq)*stride + __uint128_t(nq+chunk)*seedstride
        + __uint128_t(masks.size())*40;
    // Additional live workspace for the retained blocked rewrite algorithm.
    // The bounded export term and checkpoint state accounting stay intact.
    payload += __uint128_t(N)*nq*sizeof(long) + __uint128_t(N)*4096*sizeof(long)
        + __uint128_t(nq+4096)*stride + __uint128_t(4096)*seedstride;
    __uint128_t envelope=payload*135/100+(U(64)<<20);
    if(envelope>limit) throw std::runtime_error("lift allocation gate refused");
    std::cerr<<"admitted working_coordinates "<<work<<" border "<<nhigh<<" envelope_bytes "<<U(envelope)<<"\n";
    mzd_t* map=mzd_init(masks.size(),work);
    for(long j=0;j<old;j++) for(U w=0;w<qw;w++) { U v=mzd_row(seed,j)[w]; while(v) { int b=__builtin_ctzll(v); v&=v-1; mzd_write_bit(map,high+j,nhigh+w*64+b,1); } }
    for(long q=0;q<nhigh;q++) mzd_write_bit(map,standard[q],q,1);
    // Separate implementation: block triangular substitution. Outside-block
    // dependencies are one GF(2) matrix product per missing-variable group;
    // inside-block dependencies retain the original reverse substitution.
#ifndef REWRITE_BLOCK_ROWS
#define REWRITE_BLOCK_ROWS 4096
#endif
    constexpr long rewrite_rows=REWRITE_BLOCK_ROWS;
    static_assert(rewrite_rows>0 && rewrite_rows<=4096, "invalid rewrite block");
    std::vector<std::vector<long>> target(N,std::vector<long>(nq));
    for(int x=0;x<N;x++) for(long q=0;q<nq;q++)
        target[x][q]=column(seed_masks[rep[q]]|(U(1)<<x));
    U internal_edges=0, external_edges=0, rewrite_blocks=0;
    for(long end=high;end>0;) {
        long start=std::max(0L,end-rewrite_rows);
        std::vector<std::vector<long>> groups(N);
        for(long i=start;i<end;i++) if(divisor[i]>=0) groups[missing[i]].push_back(i);
        for(int x=0;x<N;x++) if(!groups[x].empty()) {
            mzd_t* T=mzd_init(nq,work);
            for(long q=0;q<nq;q++) if(target[x][q]>=end)
                std::memcpy(mzd_row(T,q),mzd_row(map,target[x][q]),map->width*sizeof(word));
            mzd_t* P=mzd_init(groups[x].size(),nq);
            for(long j=0;j<long(groups[x].size());j++)
                std::memcpy(mzd_row(P,j),mzd_row(seed,divisor[groups[x][j]]),seed->width*sizeof(word));
            mzd_t* E=mzd_mul(nullptr,P,T,0);
            for(long j=0;j<long(groups[x].size());j++)
                std::memcpy(mzd_row(map,groups[x][j]),mzd_row(E,j),map->width*sizeof(word));
            mzd_free(E); mzd_free(P); mzd_free(T);
        }
        for(long i=end-1;i>=start;i--) if(divisor[i]>=0) {
            word* dst=mzd_row(map,i); word* source=mzd_row(seed,divisor[i]);
            for(U w=0;w<qw;w++) { U v=source[w]; while(v) {
                int b=__builtin_ctzll(v); v&=v-1;
                long t=target[missing[i]][w*64+b];
                if(t<=i) throw std::runtime_error("nontriangular extended rewrite");
                if(t<end) { xor_row(dst,mzd_row(map,t),map->width); internal_edges++; }
                else external_edges++;
            } }
        }
        rewrite_blocks++; end=start;
    }
    std::cerr<<"rewrite_blocks "<<rewrite_blocks<<" internal_edges "<<internal_edges
             <<" external_edges "<<external_edges<<"\n";
    std::cerr<<"provisional map constructed\n";
    mzd_t* A=mzd_init(1,work); long rank=0;
    checkpoint.load(A,rank,work,nhigh,old,chunk);
    auto action=[&](int x) { mzd_t* T=mzd_init(nq,work); for(long q=0;q<nq;q++)
        std::memcpy(mzd_row(T,q),mzd_row(map,column(seed_masks[rep[q]]|(U(1)<<x))),map->width*sizeof(word)); return T; };
    auto killed=[&]() { if(kills_constant(A,rank,map)) {
        std::cout<<"{\"status\":\"projection_kills_one\",\"working_coordinates\":"<<work<<",\"relation_rank\":"<<rank<<"}\n";
        return true; } return false; };
    for(int x=checkpoint.next_x;checkpoint.phase==0 && x<N;x++) {
        mzd_t* T=action(x);
        for(long start=checkpoint.next_row;start<old;start+=chunk) {
            long end=std::min(old,start+chunk);
            mzd_t* P=mzd_init_window(seed,start,0,end,nq);
            mzd_t* E=mzd_mul(nullptr,P,T,0); mzd_free_window(P);
            for(long j=start;j<end;j++) xor_row(mzd_row(E,j-start),mzd_row(map,column(seed_masks[j]|(U(1)<<x))),map->width);
            append(A,rank,E); mzd_free(E);
            if(killed()) return 0;
            checkpoint.next_x=(end==old)?x+1:x;
            checkpoint.next_row=(end==old)?0:end;
            if(checkpoint.next_x==uint64_t(N)) checkpoint.phase=1;
            checkpoint.save(A,rank,work,nhigh,old,chunk);
        }
        mzd_free(T); std::cerr<<"seed variable "<<x+1<<"/"<<N<<" rank "<<rank<<"\n";
    }
    mzd_free(seed);
    int rounds=checkpoint.rounds;
    while(checkpoint.phase!=2) {
        long before=rank; std::vector<long> low;
        for(long i=0;i<rank;i++) if(leading(A,i)>=nhigh) low.push_back(i);
        if(low.empty()) {
            checkpoint.phase=2; checkpoint.save(A,rank,work,nhigh,old,chunk); break;
        }
        mzd_t* L=mzd_init(low.size(),nq);
        for(long j=0;j<long(low.size());j++) for(long q=0;q<nq;q++)
            if(mzd_read_bit(A,low[j],nhigh+q)) mzd_write_bit(L,j,q,1);
        for(int x=0;x<N;x++) {
            mzd_t* T=action(x);
            for(long start=0;start<L->nrows;start+=chunk) {
                long end=std::min(long(L->nrows),start+chunk);
                mzd_t* P=mzd_init_window(L,start,0,end,nq);
                mzd_t* E=mzd_mul(nullptr,P,T,0); mzd_free_window(P);
                append(A,rank,E); mzd_free(E); if(killed()) return 0;
            }
            mzd_free(T);
        }
        mzd_free(L); rounds++; std::cerr<<"closure round "<<rounds<<" rank "<<rank<<"\n";
        checkpoint.rounds=rounds; checkpoint.phase=(rank==before)?2:1;
        checkpoint.save(A,rank,work,nhigh,old,chunk);
        if(rank==before) break;
    }
    export_map(argv[2],map,A,rank);
    std::cout<<"{\"status\":\"candidate_certificate\",\"working_coordinates\":"<<work<<",\"codimension\":"<<work-rank<<",\"closure_rounds\":"<<rounds<<"}\n";
    mzd_free(A); mzd_free(map); return 0;
} catch(const std::exception& e) { std::cerr<<"refused: "<<e.what()<<"\n"; return 2; }
