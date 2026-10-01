// Frozen public-synthetic N19 exact pair transport. All three arms share this
// field, group, batch addition, base constructor and sorted third-point scan.
#include <CommonCrypto/CommonDigest.h>
#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <numeric>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <tuple>
#include <unordered_map>
#include <unordered_set>
#include <vector>
using namespace std;
static constexpr uint32_t N=19,FIELD=1u<<N,MASK=FIELD-1,POLY=FIELD|39,R=262543;
static constexpr uint64_t INFKEY=UINT64_MAX;
static constexpr int BASE_POINTS=152;
static void need(bool value,const string& why){if(!value)throw runtime_error(why);}
static double elapsed(chrono::steady_clock::time_point t){return chrono::duration<double>(chrono::steady_clock::now()-t).count();}
struct Counts{uint64_t add=0,mul=0,square=0,inverse=0,batch=0,canon_poly=0,canon_normal=0,transport=0;};
static Counts counts;
static string readall(const string& p){ifstream f(p,ios::binary);need(bool(f),"cannot read "+p);return string(istreambuf_iterator<char>(f),{});}
static vector<uint32_t> array_numbers(const string& text,const string& key,size_t& cursor){
    size_t found=text.find("\""+key+"\"",cursor);need(found!=string::npos,"JSON key absent "+key);
    size_t open=text.find('[',found);need(open!=string::npos,"JSON array absent "+key);
    int depth=0;size_t close=open;
    for(;close<text.size();close++){
        if(text[close]=='[')depth++;
        else if(text[close]==']'){depth--;if(depth==0){close++;break;}}
    }
    need(depth==0,"JSON array unterminated "+key);
    vector<uint32_t> out;uint64_t value=0;bool active=false;
    for(size_t k=open;k<close;k++){
        char c=text[k];
        if(c>='0'&&c<='9'){value=value*10+(c-'0');active=true;need(value<=UINT32_MAX,"JSON integer overflow");}
        else if(active){out.push_back(uint32_t(value));value=0;active=false;}
    }
    cursor=close;return out;
}
static uint32_t scalar_number(const string& text,const string& key){
    size_t found=text.find("\""+key+"\"");need(found!=string::npos,"JSON numeric key absent "+key);
    size_t colon=text.find(':',found);need(colon!=string::npos,"JSON numeric colon absent "+key);
    size_t at=text.find_first_of("0123456789",colon+1);
    need(at!=string::npos,"JSON numeric value absent "+key);
    return uint32_t(stoul(text.substr(at)));
}
static uint32_t mul(uint32_t a,uint32_t b){
    counts.mul++;uint32_t out=0;
    while(b){if(b&1)out^=a;b>>=1;a<<=1;if(a&FIELD)a^=POLY;}
    return out&MASK;
}
static uint32_t sq(uint32_t a){counts.square++;return mul(a,a);}
static uint32_t inverse(uint32_t a){
    need(a!=0,"zero field inverse");counts.inverse++;
    uint32_t result=1,e=FIELD-2;
    while(e){if(e&1)result=mul(result,a);a=sq(a);e>>=1;}
    return result;
}
static uint32_t refmul(uint32_t a,uint32_t b){
    uint64_t raw=0;for(int bit=0;bit<19;bit++)if(b>>bit&1)raw^=uint64_t(a)<<bit;
    for(int bit=36;bit>=19;bit--)if(raw>>bit&1)raw^=uint64_t(POLY)<<(bit-19);
    return uint32_t(raw);
}
static uint32_t refinv(uint32_t a){
    need(a!=0,"zero reference inverse");uint32_t result=1,e=FIELD-2;
    while(e){if(e&1)result=refmul(result,a);a=refmul(a,a);e>>=1;}
    return result;
}
struct Point {
    uint32_t x=UINT32_MAX,y=0;
    bool inf()const{return x==UINT32_MAX;}
    bool operator==(const Point& p)const{return x==p.x&&y==p.y;}
    bool operator!=(const Point& p)const{return !(*this==p);}
    bool operator<(const Point& p)const{return x<p.x||(x==p.x&&y<p.y);}
};
static Point O(){return {};}
static uint64_t pack(Point p){return p.inf()?INFKEY:(uint64_t(p.x)<<19)|p.y;}
static Point unpack(uint64_t key){return key==INFKEY?O():Point{uint32_t(key>>19),uint32_t(key&MASK)};}
static string point_json(Point p){return p.inf()?"null":"["+to_string(p.x)+","+to_string(p.y)+"]";}
static Point neg(Point p){if(!p.inf())p.y^=p.x;return p;}
static bool oncurve(Point p){
    return p.inf()||(p.x<FIELD&&p.y<FIELD&&
        (sq(p.y)^mul(p.x,p.y))==(mul(sq(p.x),p.x)^sq(p.x)^1u));
}
static Point add(Point p,Point q){
    counts.add++;if(p.inf())return q;if(q.inf())return p;
    if(p.x==q.x){
        if((p.y^q.y)==p.x)return O();
        need(p==q&&p.x!=0,"invalid equal-x point pair");
        uint32_t l=p.x^mul(p.y,inverse(p.x)),x=sq(l)^l^1u;
        return {x,sq(p.x)^mul(l^1u,x)};
    }
    uint32_t l=mul(p.y^q.y,inverse(p.x^q.x)),x=sq(l)^l^p.x^q.x^1u;
    return {x,mul(l,p.x^x)^x^p.y};
}
static Point refadd(Point p,Point q){
    if(p.inf())return q;if(q.inf())return p;
    if(p.x==q.x){
        if((p.y^q.y)==p.x)return O();
        need(p==q&&p.x!=0,"invalid reference equal-x point pair");
        uint32_t l=p.x^refmul(p.y,refinv(p.x)),x=refmul(l,l)^l^1u;
        return {x,refmul(p.x,p.x)^refmul(l^1u,x)};
    }
    uint32_t l=refmul(p.y^q.y,refinv(p.x^q.x)),x=refmul(l,l)^l^p.x^q.x^1u;
    return {x,refmul(l,p.x^x)^x^p.y};
}
static Point scalar(Point p,uint32_t n){
    Point out=O();while(n){if(n&1)out=add(out,p);p=add(p,p);n>>=1;}return out;
}
static Point frob(Point p){return p.inf()?p:Point{sq(p.x),sq(p.y)};}
static Point frob_shift(Point p,int j){for(int k=0;k<j;k++)p=frob(p);return p;}
static vector<Point> batch_fixed(Point p,const vector<Point>& other){
    counts.batch++;counts.add+=other.size();
    vector<Point> result(other.size());vector<uint32_t> den,prefix;vector<size_t> ids;
    uint32_t total=1;
    for(size_t k=0;k<other.size();k++){
        Point q=other[k];
        if(p.inf()){result[k]=q;continue;}
        if(q.inf()){result[k]=p;continue;}
        if(p.x==q.x){
            counts.add--;result[k]=add(p,q);continue;
        }
        uint32_t d=p.x^q.x;ids.push_back(k);den.push_back(d);
        prefix.push_back(total);total=mul(total,d);
    }
    if(!ids.empty()){
        uint32_t back=inverse(total);
        for(size_t z=ids.size();z-->0;){
            size_t k=ids[z];Point q=other[k];uint32_t id=mul(back,prefix[z]);
            back=mul(back,den[z]);uint32_t l=mul(p.y^q.y,id);
            uint32_t x=sq(l)^l^p.x^q.x^1u;
            result[k]={x,mul(l,p.x^x)^x^p.y};
        }
    }
    return result;
}
static array<uint32_t,8> sha_words(const string& label){
    unsigned char hash[32];CC_SHA256(label.data(),(CC_LONG)label.size(),hash);
    array<uint32_t,8> out{};
    for(int i=0;i<8;i++)for(int k=0;k<4;k++)out[i]|=uint32_t(hash[4*i+k])<<(8*k);
    return out;
}
struct Base {
    array<Point,4> seed{};
    vector<Point> points;
    array<vector<Point>,4> orbit{};
    unordered_set<uint64_t> membership;
    Point generator{743,138613};
};
static bool closed(const vector<Point>& points){
    unordered_set<uint64_t> all;
    for(Point p:points)all.insert(pack(p));
    for(Point p:points){
        if(p.inf()||!all.count(pack(neg(p)))||!all.count(pack(frob(p))))return false;
    }
    return true;
}
static Base construct_base(const string& path){
    string text=readall(path);size_t cursor=0;
    need(scalar_number(text,"n")==19&&scalar_number(text,"modulus")==POLY&&
         scalar_number(text,"a")==1&&scalar_number(text,"b")==1&&
         scalar_number(text,"r")==R&&scalar_number(text,"cofactor")==2,
         "native base curve/field/subgroup parameters differ");
    auto generator=array_numbers(text,"generator",cursor);
    need(generator==vector<uint32_t>{743,138613},"native declared G differs");
    cursor=0;
    auto plane=array_numbers(text,"plane_key",cursor);need(plane.size()==4,"plane key count");
    cursor=0;auto affine=array_numbers(text,"affine_coordinates",cursor);
    need(affine.size()==3&&affine[0]!=0&&affine[1]!=0&&affine[2]!=0&&affine[1]!=affine[2],"affine coefficient shape");
    vector<uint32_t> image={affine[0],affine[0]^affine[1],affine[0]^affine[2],affine[0]^affine[1]^affine[2]};
    sort(image.begin(),image.end());need(image==plane,"affine key mismatch");
    Base base;cursor=0;vector<uint32_t> seed_x;
    for(int i=0;i<4;i++){
        auto values=array_numbers(text,"point",cursor);need(values.size()==2,"seed point shape");
        Point p{values[0],values[1]},start=p;
        need(p.x!=0&&oncurve(p)&&scalar(p,R).inf(),"seed off curve/prime subgroup");
        base.seed[i]=p;seed_x.push_back(p.x);
        for(int j=0;j<19;j++){
            need(oncurve(p),"generated conjugate off curve");
            Point n=neg(p);
            for(Point q:{p,n}){
                need(base.membership.insert(pack(q)).second,"signed Frobenius base overlap");
                base.orbit[i].push_back(q);base.points.push_back(q);
            }
            p=frob(p);
        }
        need(p==start&&base.orbit[i].size()==38,"seed not full signed orbit");
    }
    sort(seed_x.begin(),seed_x.end());need(seed_x==plane,"seeds do not encode selected plane");
    sort(base.points.begin(),base.points.end());
    set<uint32_t> xs;for(Point p:base.points)xs.insert(p.x);
    need(base.points.size()==152&&xs.size()==76&&base.membership.size()==152&&closed(base.points),
         "base lacks 152-point signed Frobenius closure");
    need(scalar_number(text,"expected_x_values")==76&&
         scalar_number(text,"expected_signed_points")==152&&
         scalar_number(text,"expected_effective_orbits")==4,
         "frozen base expected cardinalities differ");
    return base;
}
struct Normal {
    uint32_t beta=0;
    array<uint32_t,19> columns{},inverse_columns{};
    array<array<uint32_t,16>,5> nibble{},poly_nibble{};
    static int rank(const array<uint32_t,19>& values){
        map<int,uint32_t> pivots;
        for(uint32_t v:values)while(v){
            int k=31-__builtin_clz(v);auto it=pivots.find(k);
            if(it==pivots.end()){pivots[k]=v;break;}v^=it->second;
        }
        return pivots.size();
    }
    static uint32_t inverse_linear(uint32_t value,const array<uint32_t,19>& columns){
        map<int,pair<uint32_t,uint32_t>> pivots;
        for(int i=0;i<19;i++){
            uint32_t row=columns[i],mask=1u<<i;
            while(row){
                int bit=31-__builtin_clz(row);auto it=pivots.find(bit);
                if(it==pivots.end()){pivots[bit]={row,mask};break;}
                row^=it->second.first;mask^=it->second.second;
            }
            need(row!=0,"normal basis linearly dependent");
        }
        uint32_t out=0;
        while(value){
            int bit=31-__builtin_clz(value);auto it=pivots.find(bit);
            need(it!=pivots.end(),"normal inverse missing pivot");
            value^=it->second.first;out^=it->second.second;
        }
        return out;
    }
    Normal(){
        for(uint32_t candidate=1;candidate<FIELD;candidate++){
            array<uint32_t,19> test{};uint32_t x=candidate;
            for(int i=0;i<19;i++){test[i]=x;x=sq(x);}
            if(rank(test)==19){beta=candidate;columns=test;break;}
        }
        need(beta!=0,"normal basis absent");
        for(int i=0;i<19;i++)inverse_columns[i]=inverse_linear(1u<<i,columns);
        for(int chunk=0;chunk<5;chunk++)for(int pattern=0;pattern<16;pattern++){
            uint32_t v=0,poly=0;for(int bit=0;bit<4;bit++){
                int position=4*chunk+bit;
                if(position<19&&(pattern>>bit&1)){
                    v^=inverse_columns[position];poly^=columns[position];
                }
            }
            nibble[chunk][pattern]=v;poly_nibble[chunk][pattern]=poly;
        }
    }
    uint32_t linear(uint32_t x)const{
        uint32_t out=0;for(int i=0;i<19;i++)if(x>>i&1)out^=inverse_columns[i];return out;
    }
    uint32_t to_normal(uint32_t x)const{
        need(x<FIELD,"normal conversion field value out of range");
        uint32_t out=0;
        for(int chunk=0;chunk<5;chunk++){
            uint32_t part=(x>>(4*chunk))&15;
            if(chunk==4)need((part&8)==0,"unused twentieth bit entered nibble table");
            out^=nibble[chunk][part];
        }
        return out;
    }
    uint32_t to_poly(uint32_t mask)const{
        need(mask<FIELD,"normal mask outside19bits");uint32_t out=0;
        for(int chunk=0;chunk<5;chunk++){
            uint32_t part=(mask>>(4*chunk))&15;
            if(chunk==4)need((part&8)==0,"unused twentieth normal bit entered nibble table");
            out^=poly_nibble[chunk][part];
        }
        return out;
    }
    uint32_t to_poly_linear(uint32_t mask)const{
        uint32_t out=0;for(int i=0;i<19;i++)if(mask>>i&1)out^=columns[i];return out;
    }
    static uint32_t rot(uint32_t mask,int shift){
        shift%=19;if(!shift)return mask;
        return ((mask<<shift)|(mask>>(19-shift)))&MASK;
    }
};
struct Frame {uint64_t key=INFKEY;int shift=0;int sign=1;Point canonical=O();};
static Frame canonical_poly(Point p){
    counts.canon_poly++;
    if(p.inf())return {};
    Frame best;bool found=false;Point current=p;
    for(int j=0;j<19;j++){
        for(int sign:{1,-1}){
            Point candidate=sign==1?current:neg(current);
            uint64_t key=pack(candidate);
            if(!found||key<best.key){
                best={key,j,sign,candidate};found=true;
            }
        }
        current=frob(current);
    }
    return best;
}
static Frame canonical_normal(Point p,const Normal& normal){
    counts.canon_normal++;
    if(p.inf())return {};
    uint32_t mask=normal.to_normal(p.x),best=MASK+1;int shift=0;
    for(int j=0;j<19;j++){
        uint32_t candidate=Normal::rot(mask,j);
        if(candidate<best){best=candidate;shift=j;}
    }
    return {best,shift,1,O()};
}
static Point forward(Point p,int shift,int sign){
    p=frob_shift(p,shift);
    return sign==1?p:neg(p);
}
static Point backward(Point p,int shift,int sign){
    counts.transport++;
    p=frob_shift(p,(19-shift)%19);
    return sign==1?p:neg(p);
}
struct Row {
    Point a,b,sum;
    int first_orbit=-1,second_orbit=-1,second_shift=-1,second_sign=0;
    int frame_shift=0,frame_sign=1;
};
static bool row_less(const Row& a,const Row& b){
    return tie(a.a.x,a.a.y,a.b.x,a.b.y,a.sum.x,a.sum.y,
               a.first_orbit,a.second_orbit,a.second_shift,a.second_sign)<
           tie(b.a.x,b.a.y,b.b.x,b.b.y,b.sum.x,b.sum.y,
               b.first_orbit,b.second_orbit,b.second_shift,b.second_sign);
}
enum class Arm{Expanded,Poly,NormalX};
static string arm_name(Arm arm){
    if(arm==Arm::Expanded)return "expanded";
    if(arm==Arm::Poly)return "canonical_poly";
    return "canonical_normal_x";
}
static Arm parse_arm(const string& name){
    if(name=="expanded")return Arm::Expanded;
    if(name=="canonical_poly")return Arm::Poly;
    if(name=="canonical_normal_x")return Arm::NormalX;
    throw runtime_error("unknown arm");
}
struct Table {
    struct PairIndices {uint16_t first,second;};
    Arm arm;const Base* base;
    unordered_map<uint64_t,PairIndices> expanded;
    unordered_map<uint64_t,Row> canonical;
    size_t anchors=0;
    Table(Arm a,const Base& b):arm(a),base(&b){}
    void insert_expanded(uint64_t key,int first,int second){
        need(arm==Arm::Expanded,"expanded insertion into canonical table");
        // Sorted i<=j iteration chooses the lexicographically first point pair.
        expanded.emplace(key,PairIndices{uint16_t(first),uint16_t(second)});
    }
    void insert_canonical(uint64_t key,const Row& row){
        need(arm!=Arm::Expanded,"canonical insertion into expanded table");
        auto at=canonical.find(key);
        if(at==canonical.end())canonical.emplace(key,row);
        else if(row_less(row,at->second))at->second=row;
    }
    size_t keys()const{return arm==Arm::Expanded?expanded.size():canonical.size();}
    Row exported_row(uint64_t key)const{
        if(arm!=Arm::Expanded)return canonical.at(key);
        auto [i,j]=expanded.at(key);
        return make_expanded_row(i,j,key);
    }
    Row make_expanded_row(int i,int j,uint64_t key)const{
        Point a=base->points[i],b=base->points[j];
        return {a,b,unpack(key),-1,-1,-1,0,0,1};
    }
};
static Row make_row(Point a,Point b,Point sum,int i=-1,int k=-1,int shift=-1,int sign=0){
    if(b<a)swap(a,b);
    return {a,b,sum,i,k,shift,sign,0,1};
}
static Table build_table(Arm arm,const Base& base,const Normal* normal){
    Table table(arm,base);
    if(arm==Arm::Expanded){
        for(int i=0;i<BASE_POINTS;i++){
            vector<Point> suffix(base.points.begin()+i,base.points.end());
            auto sums=batch_fixed(base.points[i],suffix);
            for(size_t offset=0;offset<sums.size();offset++)
                table.insert_expanded(pack(sums[offset]),i,i+offset);
        }
        table.anchors=11628;
    }else{
        need(arm!=Arm::NormalX||normal!=nullptr,"normal arm missing fresh basis");
        for(int i=0;i<4;i++)for(int k=i;k<4;k++){
            vector<Point> second;
            for(int j=0;j<19;j++){
                Point positive=frob_shift(base.seed[k],j);
                second.push_back(positive);second.push_back(neg(positive));
            }
            auto sums=batch_fixed(base.seed[i],second);
            for(int index=0;index<38;index++){
                Point a=base.seed[i],b=second[index],s=sums[index];
                int j=index/2,sign=index%2? -1:1;
                if(arm==Arm::Poly){
                    Frame frame=canonical_poly(s);
                    Row row=make_row(forward(a,frame.shift,frame.sign),
                                     forward(b,frame.shift,frame.sign),frame.canonical,
                                     i,k,j,sign);
                    row.frame_shift=frame.shift;row.frame_sign=frame.sign;
                    need(add(row.a,row.b)==row.sum,"poly table normalized endpoints not additive");
                    table.insert_canonical(frame.key,row);
                }else{
                    Frame frame=canonical_normal(s,*normal);
                    Point left=frob_shift(a,frame.shift),right=frob_shift(b,frame.shift);
                    Row row=make_row(left,right,frob_shift(s,frame.shift),i,k,j,sign);
                    row.frame_shift=frame.shift;
                    need(add(row.a,row.b)==row.sum,"normal-x stored endpoints not additive");
                    table.insert_canonical(frame.key,row);
                }
            }
        }
        table.anchors=380;
    }
    need(table.keys()==(arm==Arm::Expanded?11097:293),"frozen pair-table distinct-key count mismatch");
    return table;
}
struct PairHit {bool found=false;Point a=O(),b=O();int frame_shift=0,frame_sign=1;uint64_t key=INFKEY;int examined_rows=0;};
static PairHit lookup_pair(Point target,const Table& table,const Normal* normal){
    Frame frame;
    if(table.arm==Arm::Expanded)frame.key=pack(target);
    else if(table.arm==Arm::Poly)frame=canonical_poly(target);
    else{need(normal!=nullptr,"normal-x lookup missing basis");frame=canonical_normal(target,*normal);}
    if(table.arm==Arm::Expanded){
        auto at=table.expanded.find(frame.key);
        if(at==table.expanded.end())return {false,O(),O(),0,1,frame.key,0};
        Point a=table.base->points[at->second.first],b=table.base->points[at->second.second];
        need(add(a,b)==target,"expanded pair-index witness fails group identity");
        return {true,a,b,0,1,frame.key,1};
    }
    auto at=table.canonical.find(frame.key);
    if(at==table.canonical.end())return {false,O(),O(),frame.shift,frame.sign,frame.key,0};
    const Row& stored=at->second;int sign=frame.sign;
    if(table.arm==Arm::NormalX){
        Point aligned=frob_shift(target,frame.shift);
        if(aligned==stored.sum)sign=1;
        else if(aligned==neg(stored.sum))sign=-1;
        else return {false,O(),O(),frame.shift,frame.sign,frame.key,1};
    }
    Point a=backward(stored.a,frame.shift,sign),b=backward(stored.b,frame.shift,sign);
    need(add(a,b)==target,"transported pair fails exact group identity");
    return {true,a,b,frame.shift,sign,frame.key,1};
}
static void verify_pair(Point target,const PairHit& hit,const Base& base){
    need(hit.found,"missing pair hit");
    need(base.membership.count(pack(hit.a))&&base.membership.count(pack(hit.b)),
         "transported endpoint outside base");
    need(add(hit.a,hit.b)==target,"pair witness group identity fails");
}
struct Query {
    bool sat=false;int third=-1,probes=0,canonicalizations=0,transport_rows=0;
    Point a=O(),b=O(),p=O();
};
static Query query(Point q,const Base& base,const Table& table,const Normal* normal){
    need(oncurve(q)&&scalar(q,R).inf(),"query Q off curve/prime subgroup");
    vector<Point> negatives;negatives.reserve(BASE_POINTS);
    for(Point p:base.points)negatives.push_back(neg(p));
    auto differences=batch_fixed(q,negatives);
    Query result;
    for(int i=0;i<BASE_POINTS;i++){
        result.probes++;
        PairHit hit=lookup_pair(differences[i],table,normal);
        if(table.arm!=Arm::Expanded)result.canonicalizations++;
        result.transport_rows+=hit.examined_rows;
        if(!hit.found)continue;
        verify_pair(differences[i],hit,base);
        Point third=base.points[i];
        need(base.membership.count(pack(third))&&add(add(hit.a,hit.b),third)==q,
             "exact-three returned witness fails full group replay");
        result.sat=true;result.third=i;result.a=hit.a;result.b=hit.b;result.p=third;
        break;
    }
    return result;
}
static string query_json(const Query& q){
    ostringstream out;out<<"{\"status\":\""<<(q.sat?"SAT":"UNSAT")<<"\",\"third_index\":"<<q.third
        <<",\"probes\":"<<q.probes<<",\"canonicalizations\":"<<q.canonicalizations
        <<",\"transport_rows_examined\":"<<q.transport_rows<<",\"witness\":";
    if(q.sat)out<<"["<<point_json(q.a)<<","<<point_json(q.b)<<","<<point_json(q.p)<<"]";
    else out<<"null";
    out<<"}";return out.str();
}
static string stats_json(const Table& table){
    size_t value_bytes=(table.arm==Arm::Expanded?sizeof(Table::PairIndices):sizeof(Row));
    size_t buckets=(table.arm==Arm::Expanded?table.expanded.bucket_count():table.canonical.bucket_count());
    float load=(table.arm==Arm::Expanded?table.expanded.load_factor():table.canonical.load_factor());
    ostringstream out;out<<"{\"keys\":"<<table.keys()<<",\"rows\":"<<table.keys()
        <<",\"anchor_additions\":"<<table.anchors<<",\"bucket_count\":"<<buckets
        <<",\"load_factor\":"<<setprecision(17)<<load
        <<",\"key_sizeof\":"<<sizeof(uint64_t)<<",\"value_sizeof\":"<<value_bytes
        <<",\"value_type\":\""<<(table.arm==Arm::Expanded?"inline_pair_indices":"inline_canonical_row")<<"\""
        <<",\"logical_key_row_payload_bytes\":"<<table.keys()*(value_bytes+sizeof(uint64_t))
        <<",\"payload_scope\":\"logical sizeof key+row only; excludes map/vector/bucket allocation and RSS\"}";
    return out.str();
}
static string counts_json(const Counts& c){
    ostringstream out;out<<"{\"group_add\":"<<c.add<<",\"field_mul\":"<<c.mul
        <<",\"field_square\":"<<c.square<<",\"field_inverse\":"<<c.inverse
        <<",\"batch_calls\":"<<c.batch<<",\"canonical_poly\":"<<c.canon_poly
        <<",\"canonical_normal_x\":"<<c.canon_normal<<",\"inverse_transport\":"<<c.transport<<"}";
    return out.str();
}
static string hash_bytes(const unsigned char* bytes,size_t size){
    unsigned char hash[32];CC_SHA256(bytes,(CC_LONG)size,hash);
    ostringstream out;out<<hex<<setfill('0');
    for(unsigned char value:hash)out<<setw(2)<<unsigned(value);
    return out.str();
}
static string hash_bytes(const vector<uint8_t>& bytes){return hash_bytes(bytes.data(),bytes.size());}
static void write_u32(ofstream& out,uint32_t value){for(int k=0;k<4;k++)out.put(char(value>>(8*k)));}
static string key_json(uint64_t key,Arm arm){
    if(key==INFKEY)return "{\"kind\":\"infinity\",\"value\":null}";
    if(arm==Arm::NormalX)return "{\"kind\":\"normal_x\",\"value\":"+to_string(key)+"}";
    return "{\"kind\":\"full_point\",\"value\":"+to_string(key)+"}";
}
static bool verify_row(uint64_t key,const Row& row,Arm arm,const Base& base,const Normal* normal){
    if(!base.membership.count(pack(row.a))||!base.membership.count(pack(row.b)))return false;
    if(add(row.a,row.b)!=row.sum)return false;
    if(arm==Arm::Expanded)return key==pack(row.sum);
    if(arm==Arm::Poly)return key==canonical_poly(row.sum).key;
    return normal!=nullptr&&key==canonical_normal(row.sum,*normal).key;
}
static void write_tables(const string& out,const array<Table,3>& tables,const Base& base,const Normal& normal){
    vector<const Table*> order={&tables[0],&tables[1],&tables[2]};
    sort(order.begin(),order.end(),[](const Table* a,const Table* b){return arm_name(a->arm)<arm_name(b->arm);});
    ofstream f(out+"/control_tables.json");need(bool(f),"cannot open control tables");
    f<<"{\"schema\":\"crypto.autoresearch.n19_pair_transport_tables.v1\",\"arms\":[";
    for(size_t ai=0;ai<order.size();ai++){
        const Table& table=*order[ai];if(ai)f<<",";
        f<<"{\"arm\":\""<<arm_name(table.arm)<<"\",\"stats\":"<<stats_json(table)<<",\"rows\":[";
        vector<uint64_t> keys;
        if(table.arm==Arm::Expanded)for(auto& [key,indices]:table.expanded)keys.push_back(key);
        else for(auto& [key,row]:table.canonical)keys.push_back(key);
        sort(keys.begin(),keys.end());bool first=true;
        for(uint64_t key:keys){Row row=table.exported_row(key);
            need(verify_row(key,row,table.arm,base,table.arm==Arm::NormalX?&normal:nullptr),
                 "control table row fails actual verifier");
            if(!first)f<<",";first=false;
            f<<"{\"key\":"<<key_json(key,table.arm)<<",\"normalized_endpoints\":["
             <<point_json(row.a)<<","<<point_json(row.b)<<"],\"stored_sum\":"<<point_json(row.sum)
             <<",\"anchor\":["<<row.first_orbit<<","<<row.second_orbit<<","
             <<row.second_shift<<","<<row.second_sign<<"],\"source_frame\":["
             <<row.frame_shift<<","<<row.frame_sign<<"]}";
        }
        f<<"]}";
    }
    f<<"]}\n";
}
static vector<Point> public_universe(const string& poolpath,const Base& base,vector<Point>& representatives){
    string text=readall(poolpath);size_t cursor=0;
    auto scalars=array_numbers(text,"public_target_scalar_representatives",cursor);
    need(scalars.size()==6909,"public scalar representative count");
    vector<Point> all;all.reserve(R);all.push_back(O());representatives.reserve(6909);
    unordered_set<uint64_t> seen;seen.insert(pack(O()));
    for(uint32_t d:scalars){
        need(d>0&&d<R,"public target scalar outside subgroup");
        Point q=scalar(base.generator,d),p=q;
        need(!q.inf()&&oncurve(q)&&scalar(q,R).inf(),"public target invalid");
        representatives.push_back(q);unordered_set<uint64_t> own;
        for(int j=0;j<19;j++){
            for(Point signed_point:{p,neg(p)}){
                need(own.insert(pack(signed_point)).second,"public signed orbit shorter than38");
                need(seen.insert(pack(signed_point)).second,"public signed orbit overlap");
                all.push_back(signed_point);
            }
            p=frob(p);
        }
        need(p==q&&own.size()==38,"public Frobenius orbit not exactly38");
    }
    need(all.size()==R&&seen.size()==R,"public universe not entire prime-order subgroup");
    return all;
}
static void verify_all_pair_sums(const array<Table,3>& tables,const Base& base,const Normal& normal){
    vector<uint64_t> keys;for(auto& [key,indices]:tables[0].expanded)keys.push_back(key);
    sort(keys.begin(),keys.end());need(keys.size()==11097,"expanded distinct sums");
    for(uint64_t key:keys){
        Point sum=unpack(key);
        for(int arm=1;arm<3;arm++){
            PairHit hit=lookup_pair(sum,tables[arm],arm==2?&normal:nullptr);
            verify_pair(sum,hit,base);
        }
    }
}
static void write_membership(const string& out,const array<Table,3>& tables,
                             const Base& base,const Normal& normal,
                             const vector<Point>& universe,array<int,3>& yes){
    constexpr uint32_t bytes_per_arm=(R+7)/8;
    array<vector<uint8_t>,3> bits;
    for(auto& row:bits)row.assign(bytes_per_arm,0);
    for(size_t i=0;i<universe.size();i++){
        Point target=universe[i];
        for(int arm=0;arm<3;arm++){
            PairHit hit=lookup_pair(target,tables[arm],arm==2?&normal:nullptr);
            if(hit.found){
                verify_pair(target,hit,base);
                bits[arm][i>>3]|=uint8_t(1u<<(i&7));yes[arm]++;
            }
        }
        uint8_t mask=uint8_t(1u<<(i&7));
        need(((bits[0][i>>3]^bits[1][i>>3])&mask)==0&&
             ((bits[0][i>>3]^bits[2][i>>3])&mask)==0,
             "canonical pair-membership decision differs from expanded");
    }
    need(yes[0]==11097&&yes[1]==11097&&yes[2]==11097,
         "full subgroup pair-membership coverage regression");
    for(auto& row:bits)need((row.back()&0x80)==0,"membership high padding bit set");
    ofstream f(out+"/control_membership.bin",ios::binary);need(bool(f),"membership output failed");
    f.write("KIC19PT1",8);write_u32(f,1);write_u32(f,R);write_u32(f,3);write_u32(f,bytes_per_arm);
    for(auto& row:bits)f.write(reinterpret_cast<const char*>(row.data()),row.size());
    f.close();need(bool(f),"membership binary write failed");
    ofstream hashes(out+"/membership_hashes.json");
    hashes<<"{\"schema\":\"crypto.autoresearch.n19_pair_membership_hashes.v1\","
          <<"\"universe_points\":"<<R<<",\"bytes_per_arm\":"<<bytes_per_arm
          <<",\"expanded_sha256\":\""<<hash_bytes(bits[0])<<"\","
          <<"\"canonical_poly_sha256\":\""<<hash_bytes(bits[1])<<"\","
          <<"\"canonical_normal_x_sha256\":\""<<hash_bytes(bits[2])<<"\"}\n";
}
static void write_queries(const string& out,const array<Table,3>& tables,const Base& base,
                          const Normal& normal,const vector<Point>& representatives,
                          array<int,3>& sat,array<int,3>& exception_sat){
    ofstream f(out+"/control_queries.json");need(bool(f),"control queries output failed");
    f<<"{\"schema\":\"crypto.autoresearch.n19_pair_transport_queries.v1\","
     <<"\"scope\":\"control-only table reuse; no benchmark timing\",\"targets\":[";
    for(size_t k=0;k<representatives.size();k++){
        if(k)f<<",";Point q=representatives[k];
        array<Query,3> result={query(q,base,tables[0],nullptr),
                               query(q,base,tables[1],nullptr),
                               query(q,base,tables[2],&normal)};
        need(result[0].sat==result[1].sat&&result[0].sat==result[2].sat&&
             result[0].third==result[1].third&&result[0].third==result[2].third,
             "exact-three query status/first-third differs across arms");
        f<<"{\"target_index\":"<<k<<",\"Q\":"<<point_json(q)<<",\"arms\":{";
        for(int arm=0;arm<3;arm++){
            if(arm)f<<",";sat[arm]+=result[arm].sat;
            f<<"\""<<arm_name(tables[arm].arm)<<"\":"<<query_json(result[arm]);
        }
        f<<"}}";
    }
    for(int arm=0;arm<3;arm++)need(sat[arm]==6189,"exact-three target coverage must be6189/6909");
    f<<"],\"exceptions\":[";
    vector<Point> exceptions;exceptions.push_back(O());
    exceptions.insert(exceptions.end(),base.points.begin(),base.points.end());
    need(exceptions.size()==153,"exception count");
    for(size_t k=0;k<exceptions.size();k++){
        if(k)f<<",";Point q=exceptions[k];
        array<Query,3> result={query(q,base,tables[0],nullptr),
                               query(q,base,tables[1],nullptr),
                               query(q,base,tables[2],&normal)};
        need(result[0].sat==result[1].sat&&result[0].sat==result[2].sat&&
             result[0].third==result[1].third&&result[0].third==result[2].third,
             "exception query mismatch");
        f<<"{\"kind\":\""<<(k==0?"infinity":"base_point")<<"\",\"index\":"<<k
         <<",\"Q\":"<<point_json(q)<<",\"arms\":{";
        for(int arm=0;arm<3;arm++){
            if(arm)f<<",";exception_sat[arm]+=result[arm].sat;
            f<<"\""<<arm_name(tables[arm].arm)<<"\":"<<query_json(result[arm]);
        }
        f<<"}}";
    }
    f<<"]}\n";
}
static string forgery_controls(const array<Table,3>& tables,const Base& base){
    // Use a deterministic nonzero expanded pair sum whose Frobenius and sign
    // perturbations actually differ. Run every forged object through the same
    // group/table validator used for genuine rows and query witnesses.
    vector<uint64_t> keys;for(auto& [key,indices]:tables[0].expanded)if(key!=INFKEY)keys.push_back(key);
    sort(keys.begin(),keys.end());bool selected=false;uint64_t chosen=0;PairHit real;
    for(uint64_t key:keys){
        Point target=unpack(key);PairHit hit=lookup_pair(target,tables[1],nullptr);
        verify_pair(target,hit,base);
        Point shift_a=frob(hit.a),shift_b=frob(hit.b);
        Point sign_a=neg(hit.a),sign_b=neg(hit.b);
        if(add(shift_a,shift_b)!=target&&add(sign_a,sign_b)!=target){
            chosen=key;real=hit;selected=true;break;
        }
    }
    need(selected,"no nonzero pair suitable for fixed wrong-frame/sign falsification");
    Point target=unpack(chosen);
    auto actual_pair_verifier=[&](Point a,Point b){
        return base.membership.count(pack(a))&&base.membership.count(pack(b))&&add(a,b)==target;
    };
    need(actual_pair_verifier(real.a,real.b),"genuine pair witness rejected");
    need(!actual_pair_verifier(frob(real.a),frob(real.b)),"wrong inverse shift accepted");
    need(!actual_pair_verifier(neg(real.a),neg(real.b)),"wrong inverse sign accepted");
    Row genuine=tables[1].canonical.at(canonical_poly(target).key);
    uint64_t key=canonical_poly(genuine.sum).key;
    need(verify_row(key,genuine,Arm::Poly,base,nullptr),"genuine poly row rejected");
    need(!verify_row(key^1,genuine,Arm::Poly,base,nullptr),"wrong table key accepted");
    Row wrong_sum=genuine;wrong_sum.sum=add(genuine.sum,base.generator);
    need(!verify_row(key,wrong_sum,Arm::Poly,base,nullptr),"wrong stored sum accepted");
    Point bad=base.generator;
    for(int bit=0;bit<19&&oncurve(bad);bit++)bad.y=base.generator.y^(1u<<bit);
    need(!oncurve(bad),"offcurve input fixture missing");
    auto valid_input=[](Point p){return oncurve(p)&&scalar(p,R).inf();};
    need(!valid_input(bad),"offcurve input accepted");
    vector<Point> bad_base=base.points;bad_base.erase(bad_base.begin());
    need(!base.membership.count(pack(base.generator)),"G unexpectedly already in B");
    bad_base.push_back(base.generator);sort(bad_base.begin(),bad_base.end());
    need(bad_base.size()==152&&set<Point>(bad_base.begin(),bad_base.end()).size()==152,
         "same-shape noninvariant base fixture not152distinct points");
    need(!closed(bad_base),"same-shape noninvariant base accepted");
    vector<Point> missing=base.points;missing.pop_back();
    need(!closed(missing),"missing-point base accepted");
    ostringstream out;
    out<<"{\"target_pair_sum\":"<<point_json(target)
       <<",\"wrong_inverse_shift_plus_one\":\"rejected_by_actual_group_verifier\""
       <<",\"wrong_inverse_sign\":\"rejected_by_actual_group_verifier\""
       <<",\"wrong_table_key\":\"rejected_by_actual_row_verifier\""
       <<",\"wrong_stored_sum\":\"rejected_by_actual_row_verifier\""
       <<",\"offcurve_input\":\"rejected\""
       <<",\"missing_point_base\":\"rejected_by_closure_guard\""
       <<",\"same_shape_replace_removed_point_with_G\":\"rejected_by_closure_guard\""
       <<",\"same_shape_points\":152}";
    return out.str();
}
static void controls(const string& basepath,const string& casespath,const string& poolpath,const string& out){
    auto start=chrono::steady_clock::now();Base base=construct_base(basepath);
    need(oncurve(base.generator)&&scalar(base.generator,R).inf(),"declared G invalid");
    uint64_t field_checks=0;
    for(int i=0;i<19;i++)for(int j=0;j<19;j++){
        need(mul(1u<<i,1u<<j)==refmul(1u<<i,1u<<j),"monomial multiplication mismatch");
        field_checks++;
    }
    for(int k=0;k<4096;k++){
        auto h=sha_words("N19-PAIR-TRANSPORT-v1-field-"+to_string(k));
        uint32_t a=h[0]&MASK,b=h[1]&MASK,nonzero=1+h[0]%(FIELD-1);
        need(mul(a,b)==refmul(a,b),"hashed field product mismatch");
        need(mul(nonzero,inverse(nonzero))==1,"hashed nonzero inverse mismatch");
        field_checks++;
    }
    bool zero_rejected=false;try{(void)inverse(0);}catch(const exception&){zero_rejected=true;}
    need(zero_rejected,"zero inverse incorrectly accepted");
    auto normal_start=chrono::steady_clock::now();Normal normal;
    for(uint32_t x=0;x<FIELD;x++){
        uint32_t fast=normal.to_normal(x),linear=normal.linear(x);
        need(fast==linear&&normal.to_poly(fast)==x&&normal.to_poly(fast)==normal.to_poly_linear(fast),
             "all-field normal round-trip/two-nibble-table mismatch");
        need(normal.to_normal(sq(x))==Normal::rot(fast,1),"Frobenius normal rotation mismatch");
    }
    double normal_wall=elapsed(normal_start);
    for(Point p:base.points)need(oncurve(p)&&scalar(p,R).inf(),"base point subgroup failure");
    Point T{0,1};need(oncurve(T)&&add(T,T).inf(),"declared 2-torsion T invalid");
    Frame torsion_poly=canonical_poly(T),origin_poly=canonical_poly(O());
    Frame torsion_normal=canonical_normal(T,normal),origin_normal=canonical_normal(O(),normal);
    need(origin_poly.key==INFKEY&&origin_normal.key==INFKEY&&torsion_normal.key==0,
         "short-orbit standalone canonicalization failed");
    for(int k=0;k<4096;k++){
        auto h=sha_words("N19-PAIR-TRANSPORT-v1-group-"+to_string(k));
        Point p=base.points[h[0]%152],q=base.points[h[1]%152];
        vector<Point> tests={q,O(),p,neg(p),neg(q)};
        auto actual=batch_fixed(p,tests);
        for(size_t j=0;j<tests.size();j++)
            need(actual[j]==refadd(p,tests[j])&&oncurve(actual[j]),
                 "independent batch/group addition mismatch");
    }
    auto build_start=chrono::steady_clock::now();
    array<Table,3> tables={build_table(Arm::Expanded,base,nullptr),
                           build_table(Arm::Poly,base,nullptr),
                           build_table(Arm::NormalX,base,&normal)};
    double table_wall=elapsed(build_start);
    write_tables(out,tables,base,normal);
    verify_all_pair_sums(tables,base,normal);
    vector<Point> representatives;auto universe=public_universe(poolpath,base,representatives);
    array<int,3> pair_yes{};write_membership(out,tables,base,normal,universe,pair_yes);
    array<int,3> sat{},extra{};
    write_queries(out,tables,base,normal,representatives,sat,extra);
    // The eight frozen public cases are identity checks against the accepted
    // known-answer panel, not a new target-selection step.
    string case_text=readall(casespath);size_t position=0;
    for(int i=0;i<8;i++){
        auto values=array_numbers(case_text,"Q",position);need(values.size()==2,"frozen case shape");
        Point q{values[0],values[1]};
        Query answer=query(q,base,tables[0],nullptr);
        bool expected=(i%2==0);need(answer.sat==expected,"frozen eight-case status mismatch");
    }
    string forgeries=forgery_controls(tables,base);
    ofstream f(out+"/native_controls.json");need(bool(f),"native controls output absent");
    f<<"{\"schema\":\"crypto.autoresearch.n19_pair_transport_native_controls.v1\","
     <<"\"status\":\"passed\",\"field_checks\":"<<field_checks
     <<",\"normal_all_field_values\":"<<FIELD<<",\"normal_beta\":"<<normal.beta
     <<",\"normal_columns\":[";
    for(int i=0;i<19;i++){if(i)f<<",";f<<normal.columns[i];}
    f<<"],\"normal_control_wall_seconds\":"<<setprecision(17)<<normal_wall
     <<",\"group_batch_cases\":4096,\"pair_sum_membership_points\":"<<R
     <<",\"pair_sum_members\":"<<pair_yes[0]
     <<",\"triple_targets\":6909,\"triple_SAT\":"<<sat[0]<<",\"triple_UNSAT\":"<<6909-sat[0]
     <<",\"exception_queries\":153,\"exception_SAT\":"<<extra[0]
     <<",\"table_build_control_seconds\":"<<table_wall
     <<",\"control_reuse_not_benchmark\":true,\"forgeries\":"<<forgeries
     <<",\"torsion_and_infinity\":{\"T\":"<<point_json(T)
     <<",\"T_poly_key\":"<<torsion_poly.key<<",\"T_normal_x_key\":"<<torsion_normal.key
     <<",\"O_poly_key\":null,\"O_normal_key\":null},"
     <<"\"counters\":"<<counts_json(counts)
     <<",\"wall_seconds\":"<<elapsed(start)<<"}\n";
    cout<<"{\"status\":\"passed\",\"pair_keys\":[11097,293,293],\"triple_SAT\":6189}\n";
}
static void benchmark_query(const string& basepath,Arm arm,Point q,const string& output){
    auto full_start=chrono::steady_clock::now();
    auto t=chrono::steady_clock::now();Base base=construct_base(basepath);double base_wall=elapsed(t);
    need(!q.inf()&&oncurve(q)&&scalar(q,R).inf(),"cold public Q invalid");
    t=chrono::steady_clock::now();
    Normal* normal=nullptr;
    if(arm==Arm::NormalX)normal=new Normal();
    double normal_wall=elapsed(t);
    t=chrono::steady_clock::now();Table table=build_table(arm,base,normal);double table_wall=elapsed(t);
    t=chrono::steady_clock::now();Query answer=query(q,base,table,normal);double query_wall=elapsed(t);
    auto serialization=chrono::steady_clock::now();
    ostringstream json;
    json<<"{\"schema\":\"crypto.autoresearch.n19_pair_transport_query.v1\","
        <<"\"arm\":\""<<arm_name(arm)<<"\",\"Q\":"<<point_json(q)
        <<",\"result\":"<<query_json(answer)<<",\"table\":"<<stats_json(table)
        <<",\"stages\":{\"base_construction_validation_seconds\":"<<setprecision(17)<<base_wall
        <<",\"normal_basis_and_nibble_prep_seconds\":"<<normal_wall
        <<",\"table_build_seconds\":"<<table_wall<<",\"query_transport_replay_seconds\":"<<query_wall
        <<"},\"counters\":"<<counts_json(counts)<<",\"status\":\""
        <<(answer.sat?"SAT":"UNSAT")<<"\"}";
    double serialize_wall=elapsed(serialization);
    ofstream f(output,ios::binary);need(bool(f),"cannot write cold query result");
    f<<json.str()<<"\n";f.flush();need(bool(f),"cold result write failed");f.close();
    auto output_done=chrono::steady_clock::now();
    ofstream timing(output+".timing.json");need(bool(timing),"cold output timing write failed");
    timing<<"{\"serialization_seconds\":"<<setprecision(17)<<serialize_wall
          <<",\"result_write_seconds\":"<<chrono::duration<double>(output_done-serialization).count()-serialize_wall
          <<",\"process_observed_until_timing_file_seconds\":"<<elapsed(full_start)
          <<",\"scope\":\"C++ internal stages; whole process launch-to-wait4 is primary\"}\n";
    delete normal;
}
int main(int argc,char** argv){
    try{
        need(argc>=2,"--control or --query required");
        string phase=argv[1];
        if(phase=="--control"){
            need(argc==6,"usage --control BASE CASES POOL OUTDIR");
            controls(argv[2],argv[3],argv[4],argv[5]);
        }else if(phase=="--query"){
            need(argc==7,"usage --query BASE ARM QX QY OUTPUT");
            benchmark_query(argv[2],parse_arm(argv[3]),
                            Point{uint32_t(stoul(argv[4])),uint32_t(stoul(argv[5]))},argv[6]);
        }else throw runtime_error("unknown phase");
        return 0;
    }catch(const exception& e){cerr<<"FAILED_IMPLEMENTATION: "<<e.what()<<"\n";return 2;}
}
