// Frozen public-synthetic P9 pair-table reuse experiment.  One runtime-
// parameterized implementation serves both n=19/k=4 and n=23/k=16.
#include <CommonCrypto/CommonDigest.h>
#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <filesystem>
#include <iomanip>
#include <iostream>
#include <map>
#include <numeric>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <tuple>
#include <variant>
#include <unordered_map>
#include <unordered_set>
#include <vector>
using namespace std;
static constexpr uint64_t INFKEY=UINT64_MAX;
static uint32_t N=0,FIELD=0,MASK=0,POLY=0,R=0,CURVE_ORDER=0;
static int BASE_POINTS=0,ORBITS=0;
static string REGIME;
static void need(bool value,const string& why){if(!value)throw runtime_error(why);}
static double elapsed(chrono::steady_clock::time_point t){return chrono::duration<double>(chrono::steady_clock::now()-t).count();}
struct Counts{uint64_t add=0,mul=0,square=0,inverse=0,batch=0,canon_poly=0,canon_normal=0,transport=0;};
static Counts counts;
static string readall(const string& p){ifstream f(p,ios::binary);need(bool(f),"cannot read "+p);return string(istreambuf_iterator<char>(f),{});}
struct Point;
struct Json {
    using array=vector<Json>;using object=map<string,Json>;
    variant<nullptr_t,bool,uint64_t,string,array,object> v=nullptr;
    bool is_null()const{return holds_alternative<nullptr_t>(v);}
    uint64_t integer()const{need(holds_alternative<uint64_t>(v),"JSON integer required");return get<uint64_t>(v);}
    const string& text()const{need(holds_alternative<string>(v),"JSON string required");return get<string>(v);}
    const array& list()const{need(holds_alternative<array>(v),"JSON array required");return get<array>(v);}
    const object& dict()const{need(holds_alternative<object>(v),"JSON object required");return get<object>(v);}
    const Json& at(const string& k)const{auto& d=dict();auto it=d.find(k);need(it!=d.end(),"JSON key absent "+k);return it->second;}
};
struct JsonParser{
    const string& s;size_t i=0;
    void ws(){while(i<s.size()&&(s[i]==' '||s[i]=='\n'||s[i]=='\r'||s[i]=='\t'))i++;}
    char take(){need(i<s.size(),"unexpected JSON EOF");return s[i++];}
    string str(){need(take()=='\"',"JSON string expected");string o;
        while(true){char c=take();if(c=='\"')break;need(uint8_t(c)>=0x20,"JSON control in string");
            if(c=='\\'){char e=take();if(e=='\"'||e=='\\'||e=='/')o+=e;
                else if(e=='b')o+='\b';else if(e=='f')o+='\f';else if(e=='n')o+='\n';
                else if(e=='r')o+='\r';else if(e=='t')o+='\t';else throw runtime_error("unsupported JSON escape");}
            else o+=c;}return o;}
    Json value(){ws();char c=i<s.size()?s[i]:'\0';Json j;
        if(c=='{'){take();Json::object o;ws();if(i<s.size()&&s[i]=='}'){i++;j.v=o;return j;}
            while(true){ws();string k=str();ws();need(take()==':',"JSON colon expected");
                need(o.emplace(k,value()).second,"duplicate JSON key "+k);ws();char z=take();
                if(z=='}')break;need(z==',',"JSON object comma expected");}j.v=std::move(o);return j;}
        if(c=='['){take();Json::array a;ws();if(i<s.size()&&s[i]==']'){i++;j.v=a;return j;}
            while(true){a.push_back(value());ws();char z=take();if(z==']')break;need(z==',',"JSON array comma expected");}
            j.v=std::move(a);return j;}
        if(c=='\"'){j.v=str();return j;}
        if(c>='0'&&c<='9'){uint64_t x=0;while(i<s.size()&&s[i]>='0'&&s[i]<='9'){
                need(x<=(UINT64_MAX-uint64_t(s[i]-'0'))/10,"JSON integer overflow");x=x*10+uint64_t(s[i++]-'0');}
            j.v=x;return j;}
        if(s.compare(i,4,"null")==0){i+=4;return j;}if(s.compare(i,4,"true")==0){i+=4;j.v=true;return j;}
        if(s.compare(i,5,"false")==0){i+=5;j.v=false;return j;}throw runtime_error("unsupported JSON token");}
    Json parse(){Json out=value();ws();need(i==s.size(),"trailing JSON bytes");return out;}
};
static Json parse_json(const string& path){string s=readall(path);return JsonParser{s}.parse();}
static uint32_t u32(const Json& j){uint64_t x=j.integer();need(x<=UINT32_MAX,"JSON u32 overflow");return uint32_t(x);}
static Point point_from_json(const Json& j);
static void set_regime(const string& id){REGIME=id;counts={};
    if(id=="n19_k4"){N=19;POLY=(1u<<19)|39;R=262543;CURVE_ORDER=525086;ORBITS=4;BASE_POINTS=152;}
    else if(id=="n23_k16"){N=23;POLY=(1u<<23)|33;R=4196903;CURVE_ORDER=8393806;ORBITS=16;BASE_POINTS=736;}
    else throw runtime_error("unknown regime "+id);FIELD=1u<<N;MASK=FIELD-1;}
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
    uint64_t raw=0;for(uint32_t bit=0;bit<N;bit++)if(b>>bit&1)raw^=uint64_t(a)<<bit;
    for(int bit=int(2*N-2);bit>=int(N);bit--)if(raw>>bit&1)raw^=uint64_t(POLY)<<(bit-N);
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
static uint64_t pack(Point p){return p.inf()?INFKEY:(uint64_t(p.x)<<N)|p.y;}
static Point unpack(uint64_t key){return key==INFKEY?O():Point{uint32_t(key>>N),uint32_t(key&MASK)};}
static Point point_from_json(const Json& j){need(!j.is_null(),"affine JSON point required");auto& a=j.list();
    need(a.size()==2,"JSON point must have two coordinates");return {u32(a[0]),u32(a[1])};}
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
    vector<Point> seed;
    vector<Point> points;
    vector<vector<Point>> orbit;
    unordered_set<uint64_t> membership;
    Point generator=O();
    vector<int> candidate_indices;
};
static bool closed(const vector<Point>& points){
    unordered_set<uint64_t> all;
    for(Point p:points)all.insert(pack(p));
    for(Point p:points){
        if(p.inf()||!all.count(pack(neg(p)))||!all.count(pack(frob(p))))return false;
    }
    return true;
}
static uint32_t halftrace(uint32_t c){uint32_t w=0,t=c;for(uint32_t j=0;j<(N+1)/2;j++){
    w^=t;t=sq(sq(t));}return w;}
static bool lift_x(uint32_t x,Point& out){if(x==0)return false;
    uint32_t ix=inverse(x),c=x^1u^sq(ix),w=halftrace(c);
    if((sq(w)^w)!=c)return false;uint32_t y=mul(x,w),other=y^x;
    out={x,min(y,other)};need(oncurve(out),"halftrace lift produced off-curve point");return true;}
static Point public_generator(){for(uint32_t x=1;x<=4095;x++){Point p;if(!lift_x(x,p))continue;
    Point g=add(p,p);if(!g.inf()&&scalar(g,R).inf())return g;}throw runtime_error("public generator scan exhausted");}
static void append_orbit(Base& base,Point seed,int candidate_index){
    need(seed.x!=0&&oncurve(seed)&&scalar(seed,R).inf(),"seed off curve/prime subgroup");
    vector<Point> own;Point p=seed,start=seed;
    for(uint32_t j=0;j<N;j++){need(oncurve(p),"generated conjugate off curve");
        for(Point q:{p,neg(p)}){need(base.membership.insert(pack(q)).second,"signed Frobenius base overlap");
            own.push_back(q);base.points.push_back(q);}p=frob(p);}
    need(p==start&&own.size()==2*N,"seed lacks full signed Frobenius orbit");
    base.seed.push_back(seed);base.orbit.push_back(std::move(own));base.candidate_indices.push_back(candidate_index);
}
static Base construct_base(const string& n19_path){
    Base base;
    if(REGIME=="n19_k4"){
        Json root=parse_json(n19_path);need(u32(root.at("n"))==N&&u32(root.at("modulus"))==POLY&&
            u32(root.at("a"))==1&&u32(root.at("b"))==1&&u32(root.at("r"))==R&&
            u32(root.at("cofactor"))==2,"native n19 base parameters differ");
        auto& seeds=root.at("seed_points").list();need(seeds.size()==4,"n19 seed count");
        vector<uint32_t> seed_x;for(auto& item:seeds){Point p=point_from_json(item.at("point"));
            append_orbit(base,p,int(u32(item.at("pool_orbit_index"))));seed_x.push_back(p.x);}
        auto& plane_json=root.at("plane_key").list();vector<uint32_t> plane;
        for(auto& x:plane_json)plane.push_back(u32(x));sort(seed_x.begin(),seed_x.end());
        need(seed_x==plane,"n19 seeds do not encode selected plane");
        need(u32(root.at("expected_x_values"))==76&&u32(root.at("expected_signed_points"))==152&&
             u32(root.at("expected_effective_orbits"))==4,"n19 frozen cardinalities differ");
    }else{
        set<uint32_t> labels;
        for(int index=0;index<4096&&int(base.seed.size())<ORBITS;index++){
            auto h=sha_words("PAIR-REUSE-v1-base-n23-"+to_string(index));
            uint32_t x=uint32_t((uint64_t(h[1])<<32|h[0])%FIELD);Point p;
            if(x==0||!lift_x(x,p)||!scalar(p,R).inf())continue;
            uint32_t label=p.x,q=p.x;for(uint32_t j=1;j<N;j++){q=sq(q);label=min(label,q);}
            if(!labels.insert(label).second)continue;append_orbit(base,p,index);
        }
        need(int(base.seed.size())==ORBITS,"n23 deterministic base recipe exhausted without16orbits");
    }
    sort(base.points.begin(),base.points.end());set<uint32_t> xs;
    for(Point p:base.points)xs.insert(p.x);
    need(int(base.seed.size())==ORBITS&&int(base.points.size())==BASE_POINTS&&
         int(base.membership.size())==BASE_POINTS&&int(xs.size())==BASE_POINTS/2&&closed(base.points),
         "base signed Frobenius cardinality/closure failure");
    return base;
}
static Base construct_control_base(const string& n19_path){Base base=construct_base(n19_path);
    base.generator=public_generator();need(oncurve(base.generator)&&scalar(base.generator,R).inf(),"public generator invalid");return base;}
struct Normal {
    uint32_t beta=0;
    vector<uint32_t> columns,inverse_columns;
    vector<array<uint32_t,16>> nibble,poly_nibble;
    static int rank(const vector<uint32_t>& values){
        map<int,uint32_t> pivots;
        for(uint32_t v:values)while(v){
            int k=31-__builtin_clz(v);auto it=pivots.find(k);
            if(it==pivots.end()){pivots[k]=v;break;}v^=it->second;
        }
        return pivots.size();
    }
    static uint32_t inverse_linear(uint32_t value,const vector<uint32_t>& columns){
        map<int,pair<uint32_t,uint32_t>> pivots;
        for(uint32_t i=0;i<N;i++){
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
        columns.resize(N);inverse_columns.resize(N);nibble.resize((N+3)/4);poly_nibble.resize((N+3)/4);
        for(uint32_t candidate=1;candidate<FIELD;candidate++){
            vector<uint32_t> test(N);uint32_t x=candidate;
            for(uint32_t i=0;i<N;i++){test[i]=x;x=sq(x);}
            if(rank(test)==int(N)){beta=candidate;columns=test;break;}
        }
        need(beta!=0,"normal basis absent");
        for(uint32_t i=0;i<N;i++)inverse_columns[i]=inverse_linear(1u<<i,columns);
        for(uint32_t chunk=0;chunk<nibble.size();chunk++)for(int pattern=0;pattern<16;pattern++){
            uint32_t v=0,poly=0;for(int bit=0;bit<4;bit++){
                int position=4*chunk+bit;
                if(position<int(N)&&(pattern>>bit&1)){
                    v^=inverse_columns[position];poly^=columns[position];
                }
            }
            nibble[chunk][pattern]=v;poly_nibble[chunk][pattern]=poly;
        }
    }
    uint32_t linear(uint32_t x)const{
        uint32_t out=0;for(uint32_t i=0;i<N;i++)if(x>>i&1)out^=inverse_columns[i];return out;
    }
    uint32_t to_normal(uint32_t x)const{
        need(x<FIELD,"normal conversion field value out of range");
        uint32_t out=0;
        for(uint32_t chunk=0;chunk<nibble.size();chunk++){
            uint32_t part=(x>>(4*chunk))&15;
            if(chunk+1==nibble.size())need((part&~((1u<<(N-4*chunk))-1))==0,"normal input padding bits set");
            out^=nibble[chunk][part];
        }
        return out;
    }
    uint32_t to_poly(uint32_t mask)const{
        need(mask<FIELD,"normal mask outside field width");uint32_t out=0;
        for(uint32_t chunk=0;chunk<poly_nibble.size();chunk++){
            uint32_t part=(mask>>(4*chunk))&15;
            if(chunk+1==poly_nibble.size())need((part&~((1u<<(N-4*chunk))-1))==0,"normal mask padding bits set");
            out^=poly_nibble[chunk][part];
        }
        return out;
    }
    uint32_t to_poly_linear(uint32_t mask)const{
        uint32_t out=0;for(uint32_t i=0;i<N;i++)if(mask>>i&1)out^=columns[i];return out;
    }
    static uint32_t rot(uint32_t mask,int shift){
        shift%=int(N);if(!shift)return mask;
        return ((mask<<shift)|(mask>>(N-shift)))&MASK;
    }
};
struct Frame {uint64_t key=INFKEY;int shift=0;int sign=1;Point canonical=O();};
static Frame canonical_poly(Point p){
    counts.canon_poly++;
    if(p.inf())return {};
    Frame best;bool found=false;Point current=p;
    for(uint32_t j=0;j<N;j++){
        for(int sign:{1,-1}){
            Point candidate=sign==1?current:neg(current);
            uint64_t key=pack(candidate);
            if(!found||key<best.key){
                best={key,int(j),sign,candidate};found=true;
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
    for(uint32_t j=0;j<N;j++){
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
    p=frob_shift(p,(int(N)-shift)%int(N));
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
    if(name=="canonical_normal_x")return Arm::NormalX;
    throw runtime_error("unsupported P9 worker arm");
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
        table.anchors=size_t(BASE_POINTS)*(BASE_POINTS+1)/2;
    }else{
        need(arm!=Arm::NormalX||normal!=nullptr,"normal arm missing fresh basis");
        for(int i=0;i<ORBITS;i++)for(int k=i;k<ORBITS;k++){
            vector<Point> second;
            for(uint32_t j=0;j<N;j++){
                Point positive=frob_shift(base.seed[k],j);
                second.push_back(positive);second.push_back(neg(positive));
            }
            auto sums=batch_fixed(base.seed[i],second);
            for(int index=0;index<int(2*N);index++){
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
        table.anchors=size_t(ORBITS)*(ORBITS+1)/2*(2*N);
    }
    if(REGIME=="n19_k4")need(table.keys()==(arm==Arm::Expanded?11097:293),"n19 pair-table distinct-key count mismatch");
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
static string hash_file(const string& path){string bytes=readall(path);return hash_bytes(reinterpret_cast<const unsigned char*>(bytes.data()),bytes.size());}
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
static vector<uint64_t> sorted_expanded_keys(const Table& table){
    vector<uint64_t> keys;keys.reserve(table.expanded.size());
    for(auto& [key,indices]:table.expanded)keys.push_back(key);
    sort(keys.begin(),keys.end());return keys;
}
static string expanded_key_sha(const Table& table){
    vector<uint64_t> keys=sorted_expanded_keys(table);vector<uint8_t> bytes;bytes.reserve(8*keys.size());
    for(uint64_t key:keys)for(int k=0;k<8;k++)bytes.push_back(uint8_t(key>>(8*k)));
    return hash_bytes(bytes);
}
static void write_base_json(ostream& f,const Base& base,const Normal& normal){
    f<<"{\"id\":\""<<REGIME<<"\",\"n\":"<<N<<",\"modulus\":"<<POLY<<",\"r\":"<<R
     <<",\"curve_order\":"<<CURVE_ORDER<<",\"cofactor\":2,\"a\":1,\"b\":1,\"generator\":"
     <<point_json(base.generator)<<",\"candidate_indices\":[";
    for(size_t i=0;i<base.candidate_indices.size();i++){if(i)f<<",";f<<base.candidate_indices[i];}
    f<<"],\"seeds\":[";for(size_t i=0;i<base.seed.size();i++){if(i)f<<",";f<<point_json(base.seed[i]);}
    f<<"],\"points\":[";for(size_t i=0;i<base.points.size();i++){if(i)f<<",";f<<point_json(base.points[i]);}
    f<<"],\"normal\":{\"beta\":"<<normal.beta<<",\"columns\":[";
    for(size_t i=0;i<normal.columns.size();i++){if(i)f<<",";f<<normal.columns[i];}
    f<<"],\"inverse_columns\":[";
    for(size_t i=0;i<normal.inverse_columns.size();i++){if(i)f<<",";f<<normal.inverse_columns[i];}
    f<<"],\"nibble_chunks\":"<<normal.nibble.size()<<"}}";
}
static void write_table_json(ostream& f,const Table& expanded,const Table& canonical,
                             const Base& base,const Normal& normal){
    f<<"{\"id\":\""<<REGIME<<"\",\"expanded\":{\"stats\":"<<stats_json(expanded)
     <<",\"sorted_packed_keys_le64_sha256\":\""<<expanded_key_sha(expanded)<<"\"},"
     <<"\"canonical_normal_x\":{\"stats\":"<<stats_json(canonical)<<",\"rows\":[";
    vector<uint64_t> keys;keys.reserve(canonical.canonical.size());
    for(auto& [key,row]:canonical.canonical)keys.push_back(key);sort(keys.begin(),keys.end());
    for(size_t i=0;i<keys.size();i++){if(i)f<<",";uint64_t key=keys[i];const Row& row=canonical.canonical.at(key);
        need(verify_row(key,row,Arm::NormalX,base,&normal),"canonical row fails actual verifier");
        f<<"{\"key\":"<<key_json(key,Arm::NormalX)<<",\"normalized_endpoints\":["
         <<point_json(row.a)<<","<<point_json(row.b)<<"],\"stored_sum\":"<<point_json(row.sum)
         <<",\"anchor\":["<<row.first_orbit<<","<<row.second_orbit<<","<<row.second_shift<<","
         <<row.second_sign<<"],\"source_frame\":["<<row.frame_shift<<","<<row.frame_sign<<"]}";}
    f<<"]}}";
}
static void verify_support(const Table& expanded,const Table& canonical,const Base& base,const Normal& normal){
    unordered_set<uint64_t> expanded_set,canonical_expansion,canonical_keys;
    for(auto& [key,indices]:expanded.expanded){expanded_set.insert(key);canonical_keys.insert(canonical_normal(unpack(key),normal).key);}
    need(canonical_keys.size()==canonical.canonical.size(),"canonical keyset size differs from full pair canonicalization");
    for(auto& [key,row]:canonical.canonical){
        need(canonical_keys.count(key)&&verify_row(key,row,Arm::NormalX,base,&normal),"canonical row/key not in full pair support");
        Point p=row.sum;
        for(uint32_t j=0;j<N;j++){canonical_expansion.insert(pack(p));canonical_expansion.insert(pack(neg(p)));p=frob(p);}
    }
    need(canonical_expansion==expanded_set,"orbit-expanded canonical support differs from complete unordered pair support");
    for(uint64_t key:sorted_expanded_keys(expanded)){
        Point target=unpack(key);PairHit hit=lookup_pair(target,canonical,&normal);verify_pair(target,hit,base);
    }
}
static uint64_t poly_mod(uint64_t a,uint64_t modulus,int degree){
    for(int bit=63-__builtin_clzll(a|1);bit>=degree;bit--)if((a>>bit)&1)a^=modulus<<(bit-degree);
    return a;
}
static uint64_t poly_square_mod(uint64_t a,uint64_t modulus,int degree){
    uint64_t raw=0;for(int i=0;i<=degree;i++)if((a>>i)&1)raw^=uint64_t(1)<<(2*i);
    return poly_mod(raw,modulus,degree);
}
static uint64_t poly_gcd(uint64_t a,uint64_t b){
    while(b){int degree=63-__builtin_clzll(b);a=poly_mod(a,b,degree);swap(a,b);}return a;
}
static bool irreducible(){
    uint64_t x=2,q=x;for(uint32_t i=0;i<N;i++)q=poly_square_mod(q,POLY,N);
    if(q!=x)return false;q=poly_square_mod(x,POLY,N);return poly_gcd(POLY,q^x)==1;
}
static bool prime_u32(uint32_t v){if(v<2)return false;if((v&1)==0)return v==2;
    for(uint32_t d=3;uint64_t(d)*d<=v;d+=2)if(v%d==0)return false;return true;}
static int64_t trace_value(){int64_t a=2,b=1;if(N==0)return a;if(N==1)return b;
    for(uint32_t k=2;k<=N;k++){int64_t c=b-2*a;a=b;b=c;}return b;}
struct Panels{vector<vector<Point>> q;vector<vector<uint32_t>> scalar;};
static uint64_t first8(const array<uint32_t,8>& h){return uint64_t(h[0])|(uint64_t(h[1])<<32);}
static Panels generate_panels(const Base& base){
    Panels out;out.q.resize(8);out.scalar.resize(8);
    for(int panel=0;panel<8;panel++){set<uint32_t> seen;
        for(int k=0;out.q[panel].size()<512;k++){auto h=sha_words("PAIR-REUSE-v1-target-"+REGIME+"-"+to_string(panel)+"-"+to_string(k));
            uint32_t d=1+uint32_t(first8(h)%(R-1));if(!seen.insert(d).second)continue;
            Point q=scalar(base.generator,d);need(!q.inf()&&oncurve(q)&&scalar(q,R).inf(),"public panel point invalid");
            out.scalar[panel].push_back(d);out.q[panel].push_back(q);
        }
    }return out;
}
static Query checked_query(Point q,const Base& base,const Table& table,const Normal* normal){
    Query answer=query(q,base,table,normal);if(answer.sat){
        need(answer.third>=0&&answer.third<BASE_POINTS&&answer.probes==answer.third+1,"SAT first-hit accounting invalid");
        need(add(add(answer.a,answer.b),answer.p)==q,"SAT full witness replay failed");
    }else need(answer.third==-1&&answer.probes==BASE_POINTS,"UNSAT exhaustive probe accounting invalid");
    return answer;
}
static string forgeries(const Table& expanded,const Table& canonical,const Base& base,const Normal& normal){
    bool inverse_rejected=false,sign_rejected=false,key_rejected=false,sum_rejected=false;
    Point chosen_target=O(),wrong_a=O(),wrong_b=O(),flipped_a=O(),flipped_b=O(),wrong_sum_value=O();
    uint64_t genuine_key=INFKEY,wrong_key_value=INFKEY;int chosen_shift=0,chosen_sign=1;
    for(uint64_t packed:sorted_expanded_keys(expanded)){if(packed==INFKEY)continue;Point target=unpack(packed);
        Frame frame=canonical_normal(target,normal);auto it=canonical.canonical.find(frame.key);if(it==canonical.canonical.end())continue;
        const Row& row=it->second;int aligned_sign=frob_shift(target,frame.shift)==row.sum?1:-1;
        Point bad_a=backward(row.a,(frame.shift+1)%int(N),aligned_sign);
        Point bad_b=backward(row.b,(frame.shift+1)%int(N),aligned_sign);
        Point sign_a=backward(row.a,frame.shift,-aligned_sign),sign_b=backward(row.b,frame.shift,-aligned_sign);
        auto actual_rejects=[&](Point a,Point b){try{PairHit forged{true,a,b,frame.shift,aligned_sign,frame.key,1};
                verify_pair(target,forged,base);return false;}catch(const exception&){return true;}};
        inverse_rejected|=actual_rejects(bad_a,bad_b);
        sign_rejected|=actual_rejects(sign_a,sign_b);
        key_rejected|=!verify_row(frame.key^1,row,Arm::NormalX,base,&normal);
        Row bad=row;bad.sum=add(row.sum,base.generator);sum_rejected|=!verify_row(frame.key,bad,Arm::NormalX,base,&normal);
        if(inverse_rejected&&sign_rejected&&key_rejected&&sum_rejected){chosen_target=target;wrong_a=bad_a;wrong_b=bad_b;
            flipped_a=sign_a;flipped_b=sign_b;wrong_sum_value=bad.sum;genuine_key=frame.key;wrong_key_value=frame.key^1;
            chosen_shift=frame.shift;chosen_sign=aligned_sign;break;}
    }
    need(inverse_rejected&&sign_rejected&&key_rejected&&sum_rejected,"real transport/key/sum forgery was not rejected");
    Point badq=base.generator;for(uint32_t bit=0;bit<N&&oncurve(badq);bit++)badq.y=base.generator.y^(1u<<bit);
    need(!oncurve(badq),"offcurve forgery unavailable");bool offcurve_rejected=false;
    try{(void)query(badq,base,expanded,nullptr);}catch(const exception&){offcurve_rejected=true;}
    need(offcurve_rejected,"offcurve Q accepted by actual query verifier");
    vector<Point> missing=base.points;missing.pop_back();need(!closed(missing),"one-point-removed base accepted");
    Point outside=O();for(uint32_t d=1;d<R;d++){Point p=scalar(base.generator,d);if(!p.inf()&&!base.membership.count(pack(p))){outside=p;break;}}
    need(!outside.inf(),"outside-base subgroup replacement unavailable");
    vector<Point> replaced=base.points;replaced[0]=outside;sort(replaced.begin(),replaced.end());
    need(set<Point>(replaced.begin(),replaced.end()).size()==size_t(BASE_POINTS)&&!closed(replaced),
         "same-cardinality noninvariant base accepted");
    ostringstream o;o<<"{\"target\":"<<point_json(chosen_target)<<",\"frame_shift\":"<<chosen_shift
      <<",\"frame_sign\":"<<chosen_sign<<",\"wrong_inverse_endpoints\":["<<point_json(wrong_a)<<","<<point_json(wrong_b)
      <<"],\"wrong_sign_endpoints\":["<<point_json(flipped_a)<<","<<point_json(flipped_b)
      <<"],\"genuine_table_key\":"<<genuine_key<<",\"wrong_table_key_value\":"<<wrong_key_value
      <<",\"wrong_stored_sum_value\":"<<point_json(wrong_sum_value)<<",\"offcurve_Q\":"<<point_json(badq)
      <<",\"wrong_inverse_shift_plus_one\":true,\"wrong_sign\":true,\"wrong_table_key\":true,"
      <<"\"wrong_stored_sum\":true,\"offcurve_Q_rejected\":true,\"one_point_removed_base\":true,"
      <<"\"same_cardinality_noninvariant_base\":true,\"replacement\":"<<point_json(outside)<<"}";return o.str();
}
static void field_group_controls(const Base& base,const Normal& normal,uint64_t& field_checks,
                                 string& product_sha,string& inverse_sha){
    need(irreducible(),"declared field polynomial reducible");need(prime_u32(R),"declared r not prime");
    int64_t trace=trace_value();need(int64_t(FIELD)+1-trace==CURVE_ORDER,"Koblitz trace/order recurrence mismatch");
    for(uint32_t i=0;i<N;i++)for(uint32_t j=0;j<N;j++){
        need(mul(1u<<i,1u<<j)==refmul(1u<<i,1u<<j),"monomial product mismatch");field_checks++;}
    vector<uint8_t> products,inverses;products.reserve(4096*4);inverses.reserve(4096*4);
    for(int k=0;k<4096;k++){auto h=sha_words("PAIR-REUSE-v1-field-"+REGIME+"-"+to_string(k));
        uint32_t a=h[0]&MASK,b=h[1]&MASK,nz=1+h[0]%(FIELD-1);
        uint32_t product=mul(a,b),inv=inverse(nz);
        need(product==refmul(a,b)&&mul(nz,inv)==1,"hashed field product/inverse mismatch");field_checks++;
        for(int j=0;j<4;j++){products.push_back(uint8_t(product>>(8*j)));inverses.push_back(uint8_t(inv>>(8*j)));}}
    product_sha=hash_bytes(products);inverse_sha=hash_bytes(inverses);
    bool zero=false;try{(void)inverse(0);}catch(const exception&){zero=true;}need(zero,"zero inverse accepted");
    for(uint32_t x=0;x<FIELD;x++){uint32_t fast=normal.to_normal(x),linear=normal.linear(x);
        need(fast==linear&&normal.to_poly(fast)==x&&normal.to_poly_linear(fast)==x,
             "normal conversion roundtrip/oracle mismatch");
        need(normal.to_normal(sq(x))==Normal::rot(fast,1),"normal Frobenius rotation mismatch");}
    bool padding_in=false,padding_out=false;
    try{(void)normal.to_normal(FIELD);}catch(const exception&){padding_in=true;}
    try{(void)normal.to_poly(FIELD);}catch(const exception&){padding_out=true;}
    need(padding_in&&padding_out,"normal input/output padding guard missing");
    for(Point p:base.points)need(oncurve(p)&&scalar(p,R).inf(),"base membership/subgroup failure");
    Point T{0,1};need(oncurve(T)&&add(T,T).inf()&&neg(T)==T&&frob(T)==T&&neg(O())==O()&&frob(O())==O(),
        "O/T short-orbit Frobenius/negation control failed");
    Frame origin=canonical_normal(O(),normal),torsion=canonical_normal(T,normal);
    need(origin.key==INFKEY&&origin.shift==0&&torsion.key==0&&torsion.shift==0,
        "O/T short-orbit canonical control failed");
    for(int k=0;k<4096;k++){auto h=sha_words("PAIR-REUSE-v1-group-"+REGIME+"-"+to_string(k));
        Point p=base.points[h[0]%base.points.size()],q=base.points[h[1]%base.points.size()];
        vector<Point> tests={q,O(),p,neg(p),neg(q)};auto actual=batch_fixed(p,tests);
        for(size_t j=0;j<tests.size();j++)need(actual[j]==refadd(p,tests[j])&&oncurve(actual[j]),"batch/reference group mismatch");}
}
static void write_query_group(ostream& f,const Base& base,const Normal& normal,
                              const Table& expanded,const Table& canonical,const Panels& panels){
    f<<"{\"id\":\""<<REGIME<<"\",\"panels\":[";
    for(int panel=0;panel<8;panel++){if(panel)f<<",";f<<"[";
        for(int index=0;index<512;index++){if(index)f<<",";Point q=panels.q[panel][index];
            Query a=checked_query(q,base,expanded,nullptr),b=checked_query(q,base,canonical,&normal);
            need(a.sat==b.sat&&a.third==b.third,"panel arm status/first-hit differs");
            f<<"{\"index\":"<<index<<",\"Q\":"<<point_json(q)<<",\"expanded\":"<<query_json(a)
             <<",\"canonical_normal_x\":"<<query_json(b)<<"}";}
        f<<"]";}
    f<<"],\"exceptions\":[";
    vector<Point> exceptions={O()};exceptions.insert(exceptions.end(),base.points.begin(),base.points.end());
    for(size_t i=0;i<exceptions.size();i++){if(i)f<<",";Point q=exceptions[i];
        Query a=checked_query(q,base,expanded,nullptr),b=checked_query(q,base,canonical,&normal);
        need(a.sat==b.sat&&a.third==b.third,"exception arm status/first-hit differs");
        f<<"{\"index\":"<<i<<",\"Q\":"<<point_json(q)<<",\"expanded\":"<<query_json(a)
         <<",\"canonical_normal_x\":"<<query_json(b)<<"}";}
    f<<"],\"membership_probes\":[";
    for(int k=0;k<4096;k++){if(k)f<<",";auto h=sha_words("PAIR-REUSE-v1-member-"+REGIME+"-"+to_string(k));
        uint32_t d=1+uint32_t(first8(h)%(R-1));Point q=scalar(base.generator,d);
        PairHit a=lookup_pair(q,expanded,nullptr),b=lookup_pair(q,canonical,&normal);
        need(a.found==b.found,"membership probe arms differ");if(a.found){verify_pair(q,a,base);verify_pair(q,b,base);}
        f<<"{\"index\":"<<k<<",\"Q\":"<<point_json(q)<<",\"member\":"<<(a.found?"true":"false");
        if(a.found)f<<",\"expanded_witness\":["<<point_json(a.a)<<","<<point_json(a.b)
                    <<"],\"canonical_witness\":["<<point_json(b.a)<<","<<point_json(b.b)<<"]";
        else f<<",\"expanded_witness\":null,\"canonical_witness\":null";f<<"}";}
    f<<"]}";
}
static void controls(const string& n19_path,const string& out){
    struct Record{string id;Base base;Normal normal;Table expanded;Table canonical;Panels panels;uint64_t field_checks;
        string field_product_sha,field_inverse_sha;
        string forged;double wall;
        Record(string i,const string& path):id(std::move(i)),base((set_regime(id),construct_control_base(path))),normal(),
            expanded(build_table(Arm::Expanded,base,nullptr)),canonical(build_table(Arm::NormalX,base,&normal)),
            panels(generate_panels(base)),field_checks(0),wall(0){}
    };
    auto all_start=chrono::steady_clock::now();vector<unique_ptr<Record>> records;
    for(string id:{"n19_k4","n23_k16"}){auto start=chrono::steady_clock::now();
        auto rec=make_unique<Record>(id,n19_path);field_group_controls(rec->base,rec->normal,rec->field_checks,
            rec->field_product_sha,rec->field_inverse_sha);
        verify_support(rec->expanded,rec->canonical,rec->base,rec->normal);
        rec->forged=forgeries(rec->expanded,rec->canonical,rec->base,rec->normal);rec->wall=elapsed(start);
        records.push_back(std::move(rec));
    }
    ofstream bases(out+"/bases.json");need(bool(bases),"bases output open failed");bases<<"{\"schema\":\"crypto.autoresearch.pair_reuse_bases.v1\",\"regimes\":[";
    for(size_t i=0;i<records.size();i++){if(i)bases<<",";set_regime(records[i]->id);write_base_json(bases,records[i]->base,records[i]->normal);}bases<<"]}\n";bases.close();
    ofstream panels_file(out+"/public_panels.json");need(bool(panels_file),"public panels open failed");
    panels_file<<"{\"schema\":\"crypto.autoresearch.pair_reuse_public_panels.v1\",\"regimes\":[";
    for(size_t z=0;z<records.size();z++){auto& rec=*records[z];set_regime(rec.id);if(z)panels_file<<",";
        panels_file<<"{\"id\":\""<<rec.id<<"\",\"panels\":[";for(int p=0;p<8;p++){if(p)panels_file<<",";panels_file<<"[";
            for(int q=0;q<512;q++){if(q)panels_file<<",";panels_file<<point_json(rec.panels.q[p][q]);}panels_file<<"]";}panels_file<<"]}";}
    panels_file<<"]}\n";panels_file.close();
    filesystem::create_directories(out+"/panels");
    vector<pair<string,string>> panel_files;
    for(auto& recptr:records){auto& rec=*recptr;set_regime(rec.id);for(int p=0;p<8;p++){
        string relative="panels/"+rec.id+"_panel_"+to_string(p)+".json",path=out+"/"+relative;
        ofstream one(path);need(bool(one),"Q-only panel file open failed");
        one<<"{\"schema\":\"crypto.autoresearch.pair_reuse_panel.v1\",\"regime\":\""<<rec.id
           <<"\",\"panel\":"<<p<<",\"points\":[";
        for(int q=0;q<512;q++){if(q)one<<",";one<<point_json(rec.panels.q[p][q]);}one<<"]}\n";one.close();
        panel_files.push_back({relative,hash_file(path)});
    }}
    ofstream panel_manifest(out+"/panel_files.json");need(bool(panel_manifest),"panel manifest open failed");
    panel_manifest<<"{\"schema\":\"crypto.autoresearch.pair_reuse_panel_files.v1\",\"files\":[";
    for(size_t i=0;i<panel_files.size();i++){if(i)panel_manifest<<",";panel_manifest<<"{\"path\":\""
        <<panel_files[i].first<<"\",\"sha256\":\""<<panel_files[i].second<<"\"}";}panel_manifest<<"]}\n";panel_manifest.close();
    ofstream tables(out+"/pair_tables.json");need(bool(tables),"pair tables output open failed");tables<<"{\"schema\":\"crypto.autoresearch.pair_reuse_tables.v1\",\"regimes\":[";
    for(size_t i=0;i<records.size();i++){if(i)tables<<",";set_regime(records[i]->id);write_table_json(tables,records[i]->expanded,records[i]->canonical,records[i]->base,records[i]->normal);}tables<<"]}\n";tables.close();
    ofstream queries(out+"/control_queries.json");need(bool(queries),"control queries output open failed");queries<<"{\"schema\":\"crypto.autoresearch.pair_reuse_queries.v1\",\"regimes\":[";
    for(size_t i=0;i<records.size();i++){if(i)queries<<",";set_regime(records[i]->id);write_query_group(queries,records[i]->base,records[i]->normal,records[i]->expanded,records[i]->canonical,records[i]->panels);}queries<<"]}\n";queries.close();
    ofstream oracle(out+"/oracle_metadata.json");need(bool(oracle),"oracle output open failed");
    oracle<<"{\"schema\":\"crypto.autoresearch.pair_reuse_oracle.v1\","
          <<"\"public_panels_sha256\":\""<<hash_file(out+"/public_panels.json")<<"\","
          <<"\"panel_files_sha256\":\""<<hash_file(out+"/panel_files.json")<<"\","
          <<"\"control_queries_sha256\":\""<<hash_file(out+"/control_queries.json")<<"\","
          <<"\"linked_status_sections\":[\"panels.status_first_hit_witness\",\"exceptions.status_first_hit_witness\",\"membership_probes.member_witness\"],\"regimes\":[";
    for(size_t z=0;z<records.size();z++){auto& rec=*records[z];set_regime(rec.id);if(z)oracle<<",";
        oracle<<"{\"id\":\""<<rec.id<<"\",\"candidate_indices\":[";for(size_t i=0;i<rec.base.candidate_indices.size();i++){if(i)oracle<<",";oracle<<rec.base.candidate_indices[i];}
        oracle<<"],\"panel_scalars\":[";for(int p=0;p<8;p++){if(p)oracle<<",";oracle<<"[";for(int q=0;q<512;q++){if(q)oracle<<",";oracle<<rec.panels.scalar[p][q];}oracle<<"]";}oracle<<"]}";}
    oracle<<"]}\n";oracle.close();
    ofstream control(out+"/native_controls.json");need(bool(control),"native controls output open failed");
    control<<"{\"schema\":\"crypto.autoresearch.pair_reuse_native_controls.v1\",\"status\":\"passed\",\"regimes\":[";
    for(size_t i=0;i<records.size();i++){auto& rec=*records[i];set_regime(rec.id);if(i)control<<",";
        control<<"{\"id\":\""<<rec.id<<"\",\"field_irreducible\":true,\"trace\":"<<trace_value()
               <<",\"curve_order\":"<<CURVE_ORDER<<",\"r_prime\":true,\"field_checks\":"<<rec.field_checks
               <<",\"field_products_u32le_sha256\":\""<<rec.field_product_sha<<"\",\"field_inverses_u32le_sha256\":\""<<rec.field_inverse_sha<<"\""
               <<",\"normal_all_field_values\":"<<FIELD<<",\"normal_beta\":"<<rec.normal.beta
               <<",\"base_points\":"<<rec.base.points.size()<<",\"unordered_pairs\":"
               <<size_t(BASE_POINTS)*(BASE_POINTS+1)/2<<",\"expanded_keys\":"<<rec.expanded.keys()
               <<",\"canonical_keys\":"<<rec.canonical.keys()<<",\"panel_queries\":4096,"
               <<"\"membership_probes\":4096,\"exception_queries\":"<<BASE_POINTS+1
               <<",\"forgeries\":"<<rec.forged<<",\"pre_serialization_validation_wall_seconds\":"<<setprecision(17)<<rec.wall<<"}";}
    control<<"],\"wall_seconds\":"<<setprecision(17)<<elapsed(all_start)<<"}\n";control.close();
    cout<<"{\"status\":\"passed\",\"regimes\":2,\"panel_queries_per_regime\":4096}\n";
}
static vector<Point> read_panel(const string& path,const string& regime,int panel){
    Json root=parse_json(path);need(root.at("schema").text()=="crypto.autoresearch.pair_reuse_panel.v1"&&
        root.at("regime").text()==regime&&int(root.at("panel").integer())==panel,"Q-only panel identity differs");
    vector<Point> out;for(auto& item:root.at("points").list())out.push_back(point_from_json(item));
    need(out.size()==512,"public panel must contain512Q");return out;
}
static void benchmark_job(const string& regime,const string& n19_path,const string& panel_path,
                          int panel,int M,Arm arm,const string& output){
    auto full=chrono::steady_clock::now();set_regime(regime);
    auto t=chrono::steady_clock::now();vector<Point> q=read_panel(panel_path,regime,panel);double input_wall=elapsed(t);
    need(M==1||M==32||M==512,"M outside frozen set");q.resize(M);
    t=chrono::steady_clock::now();Base base=construct_base(n19_path);double base_wall=elapsed(t);
    t=chrono::steady_clock::now();for(Point p:q)need(!p.inf()&&oncurve(p)&&scalar(p,R).inf(),"cold public Q invalid");
    double q_validation_wall=elapsed(t);
    t=chrono::steady_clock::now();unique_ptr<Normal> normal;if(arm==Arm::NormalX)normal=make_unique<Normal>();double normal_wall=elapsed(t);
    t=chrono::steady_clock::now();Table table=build_table(arm,base,normal.get());double table_wall=elapsed(t);
    t=chrono::steady_clock::now();vector<Query> answers;answers.reserve(M);
    for(Point p:q)answers.push_back(checked_query(p,base,table,normal.get()));double query_wall=elapsed(t);
    auto serialization=chrono::steady_clock::now();ostringstream json;
    json<<"{\"schema\":\"crypto.autoresearch.pair_reuse_job.v1\",\"regime\":\""<<regime
        <<"\",\"panel\":"<<panel<<",\"M\":"<<M<<",\"arm\":\""<<arm_name(arm)<<"\",\"queries\":[";
    for(int i=0;i<M;i++){if(i)json<<",";json<<"{\"index\":"<<i<<",\"Q\":"<<point_json(q[i])
        <<",\"result\":"<<query_json(answers[i])<<"}";}
    json<<"],\"table\":"<<stats_json(table)<<",\"stages\":{\"input_read_seconds\":"<<setprecision(17)<<input_wall
        <<",\"base_construction_validation_seconds\":"<<base_wall
        <<",\"public_Q_validation_seconds\":"<<q_validation_wall
        <<",\"normal_basis_and_nibble_prep_seconds\":"<<normal_wall<<",\"table_build_seconds\":"<<table_wall
        <<",\"all_queries_transport_replay_seconds\":"<<query_wall<<"},\"counters\":"<<counts_json(counts)
        <<",\"status\":\"completed\"}";
    double serialize_wall=elapsed(serialization);ofstream f(output,ios::binary);need(bool(f),"cold result open failed");
    f<<json.str()<<"\n";f.flush();need(bool(f),"cold result write failed");f.close();auto done=chrono::steady_clock::now();
    ofstream timing(output+".timing.json");need(bool(timing),"cold timing open failed");
    timing<<"{\"serialization_seconds\":"<<setprecision(17)<<serialize_wall
          <<",\"result_write_seconds\":"<<chrono::duration<double>(done-serialization).count()-serialize_wall
          <<",\"process_observed_until_timing_file_seconds\":"<<elapsed(full)
          <<",\"scope\":\"C++ stages; direct Popen-to-wait4 is primary\"}\n";
}
int main(int argc,char** argv){
    try{need(argc>=2,"--control or --job required");string phase=argv[1];
        if(phase=="--control"){need(argc==4,"usage --control N19_BASE OUTDIR");controls(argv[2],argv[3]);}
        else if(phase=="--job"){need(argc==9,"usage --job REGIME N19_BASE PUBLIC_PANELS PANEL M ARM OUTPUT");
            benchmark_job(argv[2],argv[3],argv[4],stoi(argv[5]),stoi(argv[6]),parse_arm(argv[7]),argv[8]);}
        else throw runtime_error("unknown phase");return 0;
    }catch(const exception& e){cerr<<"FAILED_IMPLEMENTATION: "<<e.what()<<"\n";return 2;}
}
