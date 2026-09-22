// Fresh coordinate-only N19 MITM baseline and admitted native math controls.
#include <CommonCrypto/CommonDigest.h>
#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <map>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>
using namespace std;
static constexpr uint32_t N=19,FIELD=1u<<N,MASK=FIELD-1,POLY=FIELD|39,R=262543;
static void need(bool ok,const string& why){if(!ok)throw runtime_error(why);}
static double secs(chrono::steady_clock::time_point t){return chrono::duration<double>(chrono::steady_clock::now()-t).count();}
static string readall(const string& path){ifstream f(path);need(bool(f),"cannot open "+path);return string(istreambuf_iterator<char>(f),{});}
static array<uint32_t,8> sha_words(const string& text){unsigned char h[32];CC_SHA256(text.data(),(CC_LONG)text.size(),h);array<uint32_t,8> out{};for(int i=0;i<8;i++)for(int j=0;j<4;j++)out[i]|=uint32_t(h[4*i+j])<<(8*j);return out;}
static vector<uint32_t> next_array(const string& text,const string& key,size_t& pos){
    auto key_at=text.find("\""+key+"\"",pos);need(key_at!=string::npos,"missing JSON key "+key);
    auto open=text.find('[',key_at);need(open!=string::npos,"missing JSON array "+key);
    int depth=0;size_t close=open;
    for(;close<text.size();close++){
        if(text[close]=='[')depth++;
        else if(text[close]==']'){
            depth--;
            if(depth==0){close++;break;}
        }
    }
    need(depth==0,"unterminated JSON array");
    vector<uint32_t> values;uint64_t value=0;bool digits=false;
    for(size_t i=open;i<close;i++){char c=text[i];if(c>='0'&&c<='9'){value=value*10+c-'0';digits=true;need(value<=UINT32_MAX,"JSON integer overflow");}else if(digits){values.push_back(value);value=0;digits=false;}}
    pos=close;return values;
}
static uint32_t mul(uint32_t a,uint32_t b){uint32_t result=0;while(b){if(b&1)result^=a;b>>=1;a<<=1;if(a&FIELD)a^=POLY;}return result&MASK;}
static uint32_t sq(uint32_t a){return mul(a,a);}
static uint32_t inv(uint32_t a){need(a!=0,"zero inverse");uint32_t result=1,n=FIELD-2;while(n){if(n&1)result=mul(result,a);a=sq(a);n>>=1;}return result;}
static uint32_t refmul(uint32_t a,uint32_t b){uint64_t raw=0;for(int i=0;i<19;i++)if(b>>i&1)raw^=uint64_t(a)<<i;for(int i=36;i>=19;i--)if(raw>>i&1)raw^=uint64_t(POLY)<<(i-19);return raw;}
static uint32_t refinv(uint32_t a){need(a!=0,"reference zero inverse");uint32_t z=1,n=FIELD-2;while(n){if(n&1)z=refmul(z,a);a=refmul(a,a);n>>=1;}return z;}
struct Point {uint32_t x=UINT32_MAX,y=0;bool inf()const{return x==UINT32_MAX;}bool operator==(const Point& q)const{return x==q.x&&y==q.y;}bool operator<(const Point& q)const{return x<q.x||(x==q.x&&y<q.y);}};
static Point nil(){return {};}
static Point opposite(Point p){if(!p.inf())p.y^=p.x;return p;}
static bool oncurve(Point p){return p.inf()||(sq(p.y)^mul(p.x,p.y))==(mul(sq(p.x),p.x)^sq(p.x)^1u);}
static Point add(Point p,Point q){
    if(p.inf())return q;if(q.inf())return p;
    if(p.x==q.x){if((p.y^q.y)==p.x)return nil();need(p==q&&p.x!=0,"bad equal-x group input");
        uint32_t l=p.x^mul(p.y,inv(p.x)),x=sq(l)^l^1;return {x,sq(p.x)^mul(l^1,x)};}
    uint32_t l=mul(p.y^q.y,inv(p.x^q.x)),x=sq(l)^l^p.x^q.x^1;
    return {x,mul(l,p.x^x)^x^p.y};
}
static Point refadd(Point p,Point q){
    if(p.inf())return q;if(q.inf())return p;
    if(p.x==q.x){if((p.y^q.y)==p.x)return nil();need(p==q&&p.x!=0,"reference bad equal-x");
        uint32_t l=p.x^refmul(p.y,refinv(p.x)),x=refmul(l,l)^l^1;return {x,refmul(p.x,p.x)^refmul(l^1,x)};}
    uint32_t l=refmul(p.y^q.y,refinv(p.x^q.x)),x=refmul(l,l)^l^p.x^q.x^1;
    return {x,refmul(l,p.x^x)^x^p.y};
}
static Point scalar(Point p,uint32_t n){Point z=nil();while(n){if(n&1)z=add(z,p);p=add(p,p);n>>=1;}return z;}
static Point frob(Point p){return p.inf()?p:Point{sq(p.x),sq(p.y)};}
static vector<Point> batch(Point p,const vector<Point>& qs){
    vector<Point> out(qs.size());vector<uint32_t> prefix,den;vector<size_t> ids;uint32_t product=1;
    for(size_t i=0;i<qs.size();i++){
        Point q=qs[i];if(p.inf()){out[i]=q;continue;}if(q.inf()){out[i]=p;continue;}
        if(p.x==q.x){out[i]=add(p,q);continue;}
        ids.push_back(i);den.push_back(p.x^q.x);prefix.push_back(product);product=mul(product,p.x^q.x);
    }
    if(!ids.empty()){uint32_t back=inv(product);
        for(size_t z=ids.size();z-->0;){size_t i=ids[z];Point q=qs[i];uint32_t inverse=mul(back,prefix[z]);back=mul(back,den[z]);
            uint32_t l=mul(p.y^q.y,inverse),x=sq(l)^l^p.x^q.x^1;
            out[i]={x,mul(l,p.x^x)^x^p.y};}}
    return out;
}
static uint64_t code(Point p){return p.inf()?UINT64_MAX:(uint64_t(p.x)<<19)|p.y;}
static string jsonpoint(Point p){if(p.inf())return "null";return "["+to_string(p.x)+","+to_string(p.y)+"]";}
static vector<Point> make_base(const string& path){
    string text=readall(path);size_t at=0;auto plane=next_array(text,"plane_key",at);need(plane.size()==4,"plane key cardinality");
    at=0;auto affine=next_array(text,"affine_coordinates",at);need(affine.size()==3,"affine coefficients");
    vector<uint32_t> check={affine[0],affine[0]^affine[1],affine[0]^affine[2],affine[0]^affine[1]^affine[2]};
    sort(check.begin(),check.end());need(check==plane,"plane relation mismatch");
    vector<Point> points;set<uint64_t> unique;set<uint32_t> xs;vector<uint32_t> seed_x;
    at=0;
    for(int i=0;i<4;i++){
        auto values=next_array(text,"point",at);need(values.size()==2,"seed point shape");
        Point p{values[0],values[1]},start=p;
        need(p.x!=0&&oncurve(p)&&scalar(p,R).inf(),"seed off subgroup");
        seed_x.push_back(p.x);
        for(int j=0;j<19;j++){
            need(oncurve(p),"conjugate off curve");
            for(Point q:{p,opposite(p)}){
                need(unique.insert(code(q)).second,"signed orbit overlap");
                points.push_back(q);
            }
            need(xs.insert(p.x).second,"x orbit overlap");p=frob(p);
        }
        need(p==start,"seed conjugate orbit wrong length");
    }
    sort(seed_x.begin(),seed_x.end());need(seed_x==plane,"seed x coordinates differ from selected plane");
    need(points.size()==152&&unique.size()==152&&xs.size()==76,"full base cardinality mismatch");
    sort(points.begin(),points.end());return points;
}
struct Solve {bool sat=false;array<int,3> ids{-1,-1,-1};size_t pair_keys=0;};
static Solve mitm(Point q,const vector<Point>& points){
    unordered_map<uint64_t,pair<int,int>> pairs;
    for(int i=0;i<(int)points.size();i++){
        vector<Point> suffix(points.begin()+i,points.end());
        auto totals=batch(points[i],suffix);
        for(size_t j=0;j<totals.size();j++)pairs.emplace(code(totals[j]),make_pair(i,i+j));
    }
    vector<Point> negs;for(Point p:points)negs.push_back(opposite(p));
    auto differences=batch(q,negs);
    for(int i=0;i<(int)differences.size();i++){
        auto it=pairs.find(code(differences[i]));if(it==pairs.end())continue;
        auto [a,b]=it->second;
        need(add(add(points[a],points[b]),points[i])==q,"native MITM returned wrong group sum");
        return {true,{a,b,i},pairs.size()};
    }
    return {false,{-1,-1,-1},pairs.size()};
}
static void native_controls(const string& basepath,const string& casespath,const string& outpath){
    auto begin=chrono::steady_clock::now();auto points=make_base(basepath);
    uint32_t beta=0;vector<uint32_t> columns;
    auto rank=[](const vector<uint32_t>& x){map<int,uint32_t> pivot;for(auto v:x)while(v){int b=31-__builtin_clz(v);auto it=pivot.find(b);if(it==pivot.end()){pivot[b]=v;break;}v^=it->second;}return pivot.size();};
    for(uint32_t candidate=1;candidate<FIELD;candidate++){uint32_t v=candidate;vector<uint32_t> col;
        for(int i=0;i<19;i++){col.push_back(v);v=sq(v);}if(rank(col)==19){beta=candidate;columns=col;break;}}
    need(beta>0&&columns.size()==19,"normal basis absent");
    for(int i=0;i<19;i++){uint32_t v=columns[i],next=sq(v);need(next==columns[(i+1)%19],"normal Frobenius rotation failure");}
    int products=0;
    for(int i=0;i<19;i++)for(int j=0;j<19;j++){need(mul(1u<<i,1u<<j)==refmul(1u<<i,1u<<j),"monomial product mismatch");products++;}
    for(int i=0;i<4096;i++){auto h=sha_words("N19-AFFINE-SAT-v1-field-"+to_string(i));uint32_t a=h[0]&MASK,b=h[1]&MASK;
        need(a!=0,"frozen field inverse sample is zero");
        need(mul(a,b)==refmul(a,b)&&sq(a)==refmul(a,a),"sampled field product/square mismatch");
        need(mul(a,inv(a))==1,"sampled inverse mismatch");products++;}
    for(Point p:points)need(oncurve(p)&&scalar(p,R).inf(),"base admission/group mismatch");
    int group_cases=0;
    for(int i=0;i<4096;i++){auto h=sha_words("N19-AFFINE-SAT-v1-group-"+to_string(i));
        Point p=points[h[0]%152],q=points[h[1]%152];
        vector<Point> tests={q,nil(),p,opposite(p),opposite(q)};
        auto actual=batch(p,tests);
        for(size_t j=0;j<tests.size();j++)need(actual[j]==refadd(p,tests[j])&&oncurve(actual[j]),"batch/group control mismatch");
        group_cases++;}
    string cases=readall(casespath);size_t at=0;vector<Point> qs;
    for(int i=0;i<8;i++){auto v=next_array(cases,"Q",at);need(v.size()==2,"case Q cardinality");qs.push_back({v[0],v[1]});}
    ofstream f(outpath);need(bool(f),"cannot open native control output");
    f<<"{\"schema\":\"crypto.autoresearch.n19_affine_sat_native_controls.v1\",\"status\":\"passed\",";
    f<<"\"field_products\":"<<products<<",\"group_batches\":"<<group_cases<<",\"normal_beta\":"<<beta<<",\"base_points\":152,\"case_oracle\":[";
    for(int i=0;i<8;i++){if(i)f<<",";Solve s=mitm(qs[i],points);f<<"{\"case_id\":"<<i+1<<",\"status\":\""<<(s.sat?"SAT":"UNSAT")<<"\"}";}
    f<<"],\"wall_seconds\":"<<secs(begin)<<"}\n";
}
static void solve(const string& basepath,Point q,const string& outpath){
    auto start=chrono::steady_clock::now();auto points=make_base(basepath);double construction=secs(start);
    need(oncurve(q)&&scalar(q,R).inf(),"invalid public Q");
    auto search=chrono::steady_clock::now();Solve answer=mitm(q,points);double mitmwall=secs(search);
    ofstream f(outpath);need(bool(f),"cannot open native solve output");
    f<<"{\"schema\":\"crypto.autoresearch.n19_affine_sat_native_result.v1\",\"status\":\""<<(answer.sat?"SAT":"UNSAT")<<"\",";
    f<<"\"Q\":"<<jsonpoint(q)<<",\"base_points\":152,\"pair_sum_keys\":"<<answer.pair_keys;
    if(answer.sat){f<<",\"witness_indices\":["<<answer.ids[0]<<","<<answer.ids[1]<<","<<answer.ids[2]<<"],\"witness\":[";
        for(int i=0;i<3;i++){if(i)f<<",";f<<jsonpoint(points[answer.ids[i]]);}f<<"]";}
    else f<<",\"witness\":null";
    f<<",\"stages\":{\"base_construction_seconds\":"<<construction<<",\"mitm_query_and_replay_seconds\":"<<mitmwall<<"}}\n";
}
int main(int argc,char**argv){
    try{
        need(argc>=2,"native phase required");string phase=argv[1];
        if(phase=="--controls"){
            need(argc==5,"usage --controls BASE CASES OUTPUT");
            native_controls(argv[2],argv[3],argv[4]);
        }else if(phase=="--solve"){
            need(argc==6,"usage --solve BASE QX QY OUTPUT");
            solve(argv[2],Point{uint32_t(stoul(argv[3])),uint32_t(stoul(argv[4]))},argv[5]);
        }else throw runtime_error("unknown native phase");
        return 0;
    }catch(const exception& e){cerr<<"FAILED_IMPLEMENTATION: "<<e.what()<<"\n";return 2;}
}
