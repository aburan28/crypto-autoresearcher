// Included after the producer's matrix/read/write helpers. Separate instrument.
#include <openssl/evp.h>
#include <array>
#include <filesystem>
#include <string>
#include <unistd.h>
#include <fcntl.h>
#include <sys/wait.h>

using Digest = std::array<unsigned char,32>;
static Digest file_digest(const std::string& path, uint64_t length=UINT64_MAX) {
    FILE* f=fopen(path.c_str(),"rb");
    if(!f) throw std::runtime_error("cannot hash file");
    EVP_MD_CTX* ctx=EVP_MD_CTX_new();
    if(!ctx || EVP_DigestInit_ex(ctx,EVP_sha256(),nullptr)!=1)
        throw std::runtime_error("digest initialization failed");
    std::vector<unsigned char> buf(1<<20);
    while(length) {
        size_t n=fread(buf.data(),1,std::min<uint64_t>(buf.size(),length),f);
        if(!n) { if(ferror(f)) throw std::runtime_error("digest read failed"); break; }
        if(EVP_DigestUpdate(ctx,buf.data(),n)!=1) throw std::runtime_error("digest update failed");
        if(length!=UINT64_MAX) length-=n;
    }
    if(length!=0 && length!=UINT64_MAX) throw std::runtime_error("short digest input");
    Digest d; unsigned int n=0;
    if(EVP_DigestFinal_ex(ctx,d.data(),&n)!=1 || n!=d.size()) throw std::runtime_error("digest finalize failed");
    EVP_MD_CTX_free(ctx); fclose(f); return d;
}

struct Checkpoint {
    // phase 0: seed chunks; phase 1: start next closure round; phase 2: export.
    uint64_t sequence=0, phase=0, next_x=0, next_row=0, rounds=0;
    uint64_t saves=0, stop_after=0;
    std::string directory, restore, hook;
    Digest seed_hash{}, binary_hash{};
    Checkpoint(const char* seed) {
        auto env=[](const char* k) { const char* v=getenv(k); return std::string(v?v:""); };
        directory=env("SEMAEV_CHECKPOINT_DIR"); restore=env("SEMAEV_CHECKPOINT_RESTORE");
        hook=env("SEMAEV_CHECKPOINT_PUBLISH");
        std::string stop=env("SEMAEV_CHECKPOINT_STOP_AFTER");
        if(!stop.empty()) { size_t used=0; stop_after=std::stoull(stop,&used);
            if(used!=stop.size() || !stop_after) throw std::runtime_error("invalid checkpoint stop count"); }
        if(directory.empty() && (!restore.empty() || !hook.empty() || stop_after))
            throw std::runtime_error("checkpoint directory required");
        if(!directory.empty()) {
            std::filesystem::create_directories(directory);
            seed_hash=file_digest(seed); binary_hash=file_digest("/proc/self/exe");
        }
    }
    void load(mzd_t*& A,long& rank,long work,long nhigh,long old,long chunk) {
        if(restore.empty()) return;
        uint64_t bytes=std::filesystem::file_size(restore);
        constexpr size_t header_words=14;
        if(bytes<header_words*8+96) throw std::runtime_error("short checkpoint");
        Digest actual=file_digest(restore,bytes-32), expected;
        FILE* f=fopen(restore.c_str(),"rb"); if(!f) throw std::runtime_error("cannot open checkpoint");
        if(fseeko(f,bytes-32,SEEK_SET)) throw std::runtime_error("checkpoint seek failed");
        read_exact(f,expected.data(),1,32); rewind(f);
        if(actual!=expected) throw std::runtime_error("checkpoint content hash mismatch");
        uint64_t h[header_words]; read_exact(f,h,8,header_words);
        Digest sh,bh; read_exact(f,sh.data(),1,32); read_exact(f,bh.data(),1,32);
        if(h[0]!=0x315450434c5153ULL || h[1]!=1 || h[2]!=uint64_t(N) || h[3]!=uint64_t(D)
            || h[4]!=uint64_t(work) || h[5]!=uint64_t(nhigh) || h[6]!=uint64_t(old)
            || h[7]!=uint64_t(chunk) || sh!=seed_hash || bh!=binary_hash)
            throw std::runtime_error("incompatible checkpoint identity");
        phase=h[8]; next_x=h[9]; next_row=h[10]; rounds=h[11]; sequence=h[13];
        if(phase>2 || h[12]>uint64_t(work) || rounds>INT32_MAX || !sequence || sequence==UINT64_MAX)
            throw std::runtime_error("invalid checkpoint state");
        if(phase==0 ? (next_x>=uint64_t(N) || next_row>=uint64_t(old) || next_row%chunk || rounds!=0)
                    : (next_x!=uint64_t(N) || next_row!=0))
            throw std::runtime_error("invalid checkpoint position");
        uint64_t width=(work+63)/64;
        if(__uint128_t(header_words*8+96)+__uint128_t(h[12])*width*8!=bytes)
            throw std::runtime_error("checkpoint size mismatch");
        // Free the placeholder first; restoring never duplicates the matrix.
        mzd_free(A); rank=h[12]; A=mzd_init(std::max<long>(1,rank),work);
        long previous=-1;
        for(long i=0;i<rank;i++) {
            word* row=mzd_row(A,i); read_exact(f,row,8,width);
            if(work%64 && row[width-1]>>(work%64)) throw std::runtime_error("checkpoint padding bits");
            long pivot=leading(A,i);
            if(pivot<=previous || pivot>=work) throw std::runtime_error("checkpoint not echelon");
            previous=pivot;
        }
        read_exact(f,expected.data(),1,32);
        if(fgetc(f)!=EOF || ferror(f)) throw std::runtime_error("checkpoint trailing data");
        fclose(f);
        std::cerr<<"restored checkpoint "<<sequence<<" phase "<<phase<<" rank "<<rank<<"\n";
    }
    void save(mzd_t* A,long rank,long work,long nhigh,long old,long chunk) {
        if(directory.empty()) return;
        if(sequence==UINT64_MAX) throw std::runtime_error("checkpoint sequence overflow");
        ++sequence;
        std::string final=directory+"/checkpoint-"+std::to_string(sequence)+".bin", tmp=final+".partial";
        if(std::filesystem::exists(final)) throw std::runtime_error("checkpoint identity exists");
        FILE* f=fopen(tmp.c_str(),"wbx"); if(!f) throw std::runtime_error("cannot create checkpoint");
        uint64_t h[]={0x315450434c5153ULL,1,uint64_t(N),uint64_t(D),uint64_t(work),uint64_t(nhigh),
            uint64_t(old),uint64_t(chunk),phase,next_x,next_row,rounds,uint64_t(rank),sequence};
        write_exact(f,h,8,14); write_exact(f,seed_hash.data(),1,32); write_exact(f,binary_hash.data(),1,32);
        for(long i=0;i<rank;i++) write_exact(f,mzd_row(A,i),8,A->width);
        if(fflush(f) || fsync(fileno(f)) || fclose(f)) throw std::runtime_error("checkpoint flush failed");
        Digest d=file_digest(tmp); f=fopen(tmp.c_str(),"ab");
        if(!f) throw std::runtime_error("checkpoint footer open failed");
        write_exact(f,d.data(),1,32);
        if(fflush(f) || fsync(fileno(f)) || fclose(f)) throw std::runtime_error("checkpoint footer flush failed");
        if(rename(tmp.c_str(),final.c_str())) throw std::runtime_error("checkpoint rename failed");
        int dirfd=open(directory.c_str(),O_RDONLY|O_DIRECTORY);
        if(dirfd<0) throw std::runtime_error("checkpoint directory open failed");
        int sync_status=fsync(dirfd); close(dirfd);
        if(sync_status) throw std::runtime_error("checkpoint directory sync failed");
        // A synchronous executable hook must publish and verify before returning.
        // No shell interpretation; the snapshot path is its sole argument.
        if(!hook.empty()) {
            pid_t p=fork(); if(p<0) throw std::runtime_error("checkpoint hook fork failed");
            if(p==0) { execl(hook.c_str(),hook.c_str(),final.c_str(),(char*)nullptr); _exit(127); }
            int status=0; if(waitpid(p,&status,0)!=p || !WIFEXITED(status) || WEXITSTATUS(status))
                throw std::runtime_error("checkpoint publication failed");
        }
        std::cerr<<"saved checkpoint "<<sequence<<" phase "<<phase<<" next_variable "<<next_x<<" next_row "<<next_row<<" rank "<<rank<<"\n";
        if(stop_after && ++saves>=stop_after) { std::cerr<<"qualification stop after complete checkpoint\n"; std::exit(75); }
    }
};
