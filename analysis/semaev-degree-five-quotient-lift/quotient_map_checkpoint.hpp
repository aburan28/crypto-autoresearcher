// Candidate custody for completed suffixes of the triangular provisional map.
// Included after quotient_checkpoint.hpp and the producer's matrix helpers.
#include <filesystem>

struct MapCheckpoint {
    std::string directory, publish_hook, fetch_hook;
    Digest seed_hash{}, binary_hash{};
    uint64_t chunk_rows = 0;
    bool restore_mode = false;
    bool prune_local = false;

    MapCheckpoint(const Checkpoint& checkpoint) {
        auto env=[](const char* key) { const char* value=getenv(key); return std::string(value?value:""); };
        directory=env("SEMAEV_MAP_DIR");
        publish_hook=env("SEMAEV_MAP_PUBLISH");
        fetch_hook=env("SEMAEV_MAP_FETCH");
        std::string restore=env("SEMAEV_MAP_RESTORE");
        if(!restore.empty() && restore!="1") throw std::runtime_error("invalid map restore flag");
        restore_mode=(restore=="1");
        std::string prune=env("SEMAEV_MAP_PRUNE_LOCAL");
        if(!prune.empty() && prune!="1") throw std::runtime_error("invalid map prune flag");
        prune_local=(prune=="1");
        if(directory.empty()) {
            if(!publish_hook.empty() || !fetch_hook.empty() || restore_mode || prune_local)
                throw std::runtime_error("map cache option requires SEMAEV_MAP_DIR");
            return;
        }
        if(checkpoint.directory.empty()) throw std::runtime_error("map cache requires relation checkpoint context");
        seed_hash=checkpoint.seed_hash; binary_hash=checkpoint.binary_hash;
        std::filesystem::create_directories(directory);
        std::string raw=env("SEMAEV_MAP_CHUNK_ROWS");
        chunk_rows=raw.empty()?65536:std::stoull(raw);
        if(!chunk_rows || chunk_rows>65536 || chunk_rows%4096)
            throw std::runtime_error("map chunk rows must be a multiple of 4096 in [4096,65536]");
    }

    static int hook(const std::string& executable,const std::vector<std::string>& args,int absent=0) {
        pid_t pid=fork(); if(pid<0) throw std::runtime_error("map hook fork failed");
        if(pid==0) {
            std::vector<char*> argv; argv.push_back(const_cast<char*>(executable.c_str()));
            for(const auto& arg:args) argv.push_back(const_cast<char*>(arg.c_str()));
            argv.push_back(nullptr); execv(executable.c_str(),argv.data()); _exit(127);
        }
        int status=0;
        if(waitpid(pid,&status,0)!=pid || !WIFEXITED(status) ||
           (WEXITSTATUS(status)!=0 && (!absent || WEXITSTATUS(status)!=absent)))
            throw std::runtime_error("map hook failed");
        return WEXITSTATUS(status);
    }

    std::string path(uint64_t start,uint64_t end) const {
        return directory+"/map-"+std::to_string(start)+"-"+std::to_string(end)+".bin";
    }
    static constexpr uint64_t magic=0x31504d434c5153ULL;
    static constexpr uint64_t header_words=9;

    void save(mzd_t* map,uint64_t start,uint64_t end,uint64_t high,uint64_t work) const {
        if(directory.empty()) return;
        if(start>=end || end>high || end-start>chunk_rows)
            throw std::runtime_error("invalid map chunk interval");
        uint64_t width=(work+63)/64;
        if(map->width!=width) throw std::runtime_error("map row width mismatch");
        std::string final=path(start,end), partial=final+".partial";
        if(std::filesystem::exists(final)) {
            if(!restore_mode) throw std::runtime_error("map chunk already exists");
            read(map,start,end,high,work);
            if(!publish_hook.empty()) hook(publish_hook,{final});
            std::cerr<<"reused map chunk "<<start<<" "<<end<<"\n";
            return;
        }
        FILE* file=fopen(partial.c_str(),"wbx");
        if(!file) throw std::runtime_error("cannot create map chunk");
        uint64_t h[header_words]={magic,1,uint64_t(N),uint64_t(D),high,work,start,end,width};
        write_exact(file,h,8,header_words);
        write_exact(file,seed_hash.data(),1,32); write_exact(file,binary_hash.data(),1,32);
        for(uint64_t i=start;i<end;i++) write_exact(file,mzd_row(map,i),8,width);
        if(fflush(file) || fsync(fileno(file)) || fclose(file)) throw std::runtime_error("map chunk flush failed");
        Digest digest=file_digest(partial);
        file=fopen(partial.c_str(),"ab"); if(!file) throw std::runtime_error("cannot append map digest");
        write_exact(file,digest.data(),1,32);
        if(fflush(file) || fsync(fileno(file)) || fclose(file)) throw std::runtime_error("map digest flush failed");
        if(rename(partial.c_str(),final.c_str())) throw std::runtime_error("map chunk rename failed");
        int dirfd=open(directory.c_str(),O_RDONLY|O_DIRECTORY);
        if(dirfd<0) throw std::runtime_error("map directory open failed");
        int rc=fsync(dirfd); close(dirfd); if(rc) throw std::runtime_error("map directory sync failed");
        if(!publish_hook.empty()) hook(publish_hook,{final});
        std::cerr<<"saved map chunk "<<start<<" "<<end<<"\n";
    }

    void read(mzd_t* map,uint64_t start,uint64_t end,uint64_t high,uint64_t work) const {
        std::string file_path=path(start,end);
        uint64_t width=(work+63)/64, bytes=header_words*8+64+(end-start)*width*8+32;
        if(std::filesystem::file_size(file_path)!=bytes) throw std::runtime_error("map chunk size mismatch");
        Digest actual=file_digest(file_path,bytes-32), expected;
        FILE* file=fopen(file_path.c_str(),"rb"); if(!file) throw std::runtime_error("cannot read map chunk");
        if(fseeko(file,bytes-32,SEEK_SET)) throw std::runtime_error("map chunk seek failed");
        read_exact(file,expected.data(),1,32); rewind(file);
        if(actual!=expected) throw std::runtime_error("map chunk digest mismatch");
        uint64_t h[header_words]; read_exact(file,h,8,header_words);
        Digest sh,bh; read_exact(file,sh.data(),1,32); read_exact(file,bh.data(),1,32);
        if(h[0]!=magic || h[1]!=1 || h[2]!=uint64_t(N) || h[3]!=uint64_t(D) ||
           h[4]!=high || h[5]!=work || h[6]!=start || h[7]!=end || h[8]!=width ||
           sh!=seed_hash || bh!=binary_hash)
            throw std::runtime_error("incompatible map chunk identity");
        for(uint64_t i=start;i<end;i++) {
            word* row=mzd_row(map,i); read_exact(file,row,8,width);
            if(work%64 && row[width-1]>>(work%64)) throw std::runtime_error("map padding bits");
        }
        read_exact(file,expected.data(),1,32);
        if(fgetc(file)!=EOF || ferror(file)) throw std::runtime_error("map chunk trailing data");
        fclose(file);
    }

    // A missing chunk stops at the first uncomputed block. Other failures are fatal.
    uint64_t restore(mzd_t* map,uint64_t high,uint64_t work) const {
        if(directory.empty() || !restore_mode) return high;
        uint64_t end=high;
        while(end) {
            uint64_t start=end>chunk_rows?end-chunk_rows:0;
            std::string file_path=path(start,end);
            if(!std::filesystem::exists(file_path) && !fetch_hook.empty()) {
                int rc=hook(fetch_hook,{std::to_string(start),std::to_string(end),file_path},2);
                if((rc==0) != std::filesystem::exists(file_path))
                    throw std::runtime_error("map fetch result/file mismatch");
            }
            if(!std::filesystem::exists(file_path)) break;
            read(map,start,end,high,work);
            if(prune_local) std::filesystem::remove(file_path);
            std::cerr<<"restored map chunk "<<start<<" "<<end<<"\n";
            end=start;
        }
        return end;
    }
};
