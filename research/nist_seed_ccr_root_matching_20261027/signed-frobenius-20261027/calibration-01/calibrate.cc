#include <algorithm>
#include <array>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>
using U=uint32_t; using Q=uint64_t;
void require(bool x,const std::string&s){if(!x)throw std::runtime_error(s);}
struct Sig{U t,f,u;}; struct Witness{int a=-1,b=-1,f=-1;};
struct Label{U mask;int endpoint;Witness robust,possible;Q capbits=0;int ell=-1,c=-1,d=-1;};
struct Point{int c=0,d=0;}; struct Level{int ell;std::vector<Point> points;};
struct Input{int n,m,k,g,l;U actual,fixed,endpoints,full;std::vector<Sig> sigs;std::vector<std::pair<U,int>> strata;std::vector<Label> labels;std::vector<int> index;std::vector<Level> levels;};
std::array<U,4> bins(Sig a,Sig b){return {(a.f|a.u)&(b.f|b.u),(a.f|a.u)&(b.t|b.u),(a.t|a.u)&(b.f|b.u),(a.t|a.u)&(b.t|b.u)};}
std::vector<std::array<U,3>> predictions(Sig a,Sig b,U fixed,U full){
 auto z=bins(a,b);std::vector<std::array<U,3>> out;
 for(U f=0;f<16;f++){U pos=0,neg=0;for(int j=0;j<4;j++)if(f&(1u<<j))pos|=z[j];else neg|=z[j];if((pos&fixed)!=fixed)continue;require(((pos&neg)&~fixed)==0,"unknown outside fixed positives");out.push_back({((pos&~fixed)|fixed)&full,U((neg&fixed)==0),f});}return out;
}
bool witness_ok(Sig a,Sig b,U mask,int f,int n,bool robust){
 for(int i=0;i<n;i++){bool any=false,all=true;int target=(mask>>i)&1;for(int x=0;x<2;x++)for(int y=0;y<2;y++){U am=x?(a.t|a.u):(a.f|a.u),bm=y?(b.t|b.u):(b.f|b.u);if(((am&bm)>>i)&1){bool ok=(((f>>(2*x+y))&1)==target);any|=ok;all&=ok;}}if(robust?!all:!any)return false;}return true;
}
void controls(){
 Sig a{12,3,0},b{10,5,0};auto p=predictions(a,b,0,15);require(p.size()==16,"XOR population");std::vector<U> masks;for(auto z:p)masks.push_back(z[0]);std::sort(masks.begin(),masks.end());for(U i=0;i<16;i++)require(masks[i]==i,"full four-bin detector");require(witness_ok(a,b,6,6,4,true),"XOR two variables");
 Sig same{0,3,0};for(auto z:predictions(same,same,0,3))require(z[0]!=1&&z[0]!=2,"collision negative");
 Sig u{2,0,1},zero{0,3,0};bool possible=false,robust=false;for(auto z:predictions(u,zero,1,3))if(z[0]==1){possible=true;robust|=z[1];require(witness_ok(u,zero,1,z[2],2,false),"unknown witness");}require(possible&&!robust,"unknown distinction");require(predictions(a,b,0,15)==p,"A/A repeat");
}
Input load(const std::string&d){
 Input x;std::ifstream meta(d+"/meta.txt");meta>>x.n>>x.m>>x.k>>x.g>>x.l>>x.actual>>x.fixed>>x.endpoints;require(bool(meta),"metadata read");require(x.n==21&&x.m==2551&&x.k==4480&&x.g==6&&x.l==61,"fixed dimensions");x.full=(1u<<x.n)-1;std::ifstream ss(d+"/signatures.tsv");
 for(int i=0;i<x.m;i++){int id;Sig s;ss>>id>>s.t>>s.f>>s.u;require(bool(ss)&&id==i,"signature row");require((s.t&s.f)==0&&(s.t&s.u)==0&&(s.f&s.u)==0&&(s.t|s.f|s.u)==x.full,"ternary partition");require((s.u&~x.fixed)==0,"unknown scope");x.sigs.push_back(s);}
 U unionmask=0,derivedfixed=0;std::ifstream st(d+"/strata.tsv");for(int i=0;i<x.g;i++){U m;int k;st>>m>>k;require(bool(st)&&!(unionmask&m)&&k>=0&&k<=__builtin_popcount(m),"strata");unionmask|=m;if(k==__builtin_popcount(m))derivedfixed|=m;x.strata.push_back({m,k});}require(unionmask==x.full&&derivedfixed==x.fixed,"stratum coverage");
 x.index.assign(x.full+1,-1);std::ifstream ls(d+"/labels.tsv");int endpoints=0;U prev=0;for(int i=0;i<x.k;i++){U m;int e;ls>>m>>e;require(bool(ls)&&(i==0||m>prev)&&m<=x.full,"label order");prev=m;for(auto q:x.strata)require(__builtin_popcount(m&q.first)==q.second,"label field count");require(e==int((m&x.endpoints)==x.endpoints),"endpoint flag");require((m&x.fixed)==x.fixed,"fixed positives");endpoints+=e;Label v;v.mask=m;v.endpoint=e;x.labels.push_back(v);x.index[m]=i;}require(endpoints==126&&x.index[x.actual]>=0,"reference populations");
 std::ifstream caps(d+"/caps.tsv");int ell,id,c,dd;int count=0;while(caps>>ell>>id>>c>>dd){if(x.levels.empty()||x.levels.back().ell!=ell){require(x.levels.empty()||x.levels.back().ell<ell,"level order");x.levels.push_back({ell,{}});}require(id==int(x.levels.back().points.size())&&c>=0&&dd>0,"cap point");x.levels.back().points.push_back({c,dd});count++;}require(count==1281&&int(x.levels.size())==x.l,"cap matrix");for(auto&v:x.levels)require(int(v.points.size())==x.n,"level completeness");return x;
}
void enumerate(Input x,const std::string&d){
 Q pairs=0,functions=0,actualrp=0,actualpp=0,actualrf=0,actualpf=0;int actualid=x.index[x.actual];
 for(int a=0;a<x.m;a++)for(int b=a+1;b<x.m;b++){
  pairs++;functions+=16;bool ar=false,ap=false;auto z=bins(x.sigs[a],x.sigs[b]);
  for(U f=0;f<16;f++){U pos=0,neg=0;for(int j=0;j<4;j++)if(f&(1u<<j))pos|=z[j];else neg|=z[j];if((pos&x.fixed)!=x.fixed)continue;U mask=((pos&~x.fixed)|x.fixed)&x.full;int id=x.index[mask];if(id<0)continue;bool robust=(neg&x.fixed)==0;auto&v=x.labels[id];if(v.possible.a<0)v.possible={a,b,int(f)};if(robust&&v.robust.a<0)v.robust={a,b,int(f)};if(id==actualid){actualpf++;ap=true;if(robust){actualrf++;ar=true;}}}
  actualrp+=ar;actualpp+=ap;
 }
 require(pairs==Q(x.m)*(x.m-1)/2,"pair completeness");require(actualrp==16&&actualpp==16&&actualrf==19&&actualpf==19,"original fit reproduction");
 std::ofstream models(d+"/cap-models.csv");models<<"ell,candidate_cap,degree_cap,prediction_mask,reference_label_id\n";Q capmodels=0;
 for(int k=0;k<x.l;k++){
  auto&level=x.levels[k];std::vector<int> cs,ds;for(auto p:level.points){cs.push_back(p.c);ds.push_back(p.d);}std::sort(cs.begin(),cs.end());cs.erase(std::unique(cs.begin(),cs.end()),cs.end());std::sort(ds.begin(),ds.end());ds.erase(std::unique(ds.begin(),ds.end()),ds.end());
  for(int c:cs)for(int dd:ds){U mask=0;for(int i=0;i<x.n;i++)if(level.points[i].c<=c&&level.points[i].d<=dd)mask|=1u<<i;int id=x.index[mask];models<<level.ell<<','<<c<<','<<dd<<','<<mask<<','<<id<<'\n';capmodels++;if(id>=0){auto&v=x.labels[id];v.capbits|=Q(1)<<k;if(v.ell<0){v.ell=level.ell;v.c=c;v.d=dd;}}}
 }
 require(bool(models),"cap model write");std::ofstream out(d+"/coverage.csv");out<<"id,mask,endpoint,robust_a,robust_b,robust_f,possible_a,possible_b,possible_f,cap_level_bits,cap_ell,cap_c,cap_d\n";
 int robust=0,possible=0,cap=0,er=0,ep=0,ec=0;std::vector<int> perlevel(x.l,0);
 for(int i=0;i<x.k;i++){auto&v=x.labels[i];bool r=v.robust.a>=0,p=v.possible.a>=0,c=v.capbits!=0;robust+=r;possible+=p;cap+=c;er+=v.endpoint&&r;ep+=v.endpoint&&p;ec+=v.endpoint&&c;for(int k=0;k<x.l;k++)perlevel[k]+=bool(v.capbits&(Q(1)<<k));out<<i<<','<<v.mask<<','<<v.endpoint<<','<<v.robust.a<<','<<v.robust.b<<','<<v.robust.f<<','<<v.possible.a<<','<<v.possible.b<<','<<v.possible.f<<','<<v.capbits<<','<<v.ell<<','<<v.c<<','<<v.d<<'\n';}require(bool(out),"coverage write");
 std::ofstream sum(d+"/enumerator-summary.txt");sum<<"labels "<<x.k<<"\nendpoint_labels 126\nfull_robust_covered "<<robust<<"\nfull_possible_covered "<<possible<<"\ncaps_covered "<<cap<<"\nendpoint_full_robust "<<er<<"\nendpoint_full_possible "<<ep<<"\nendpoint_caps_covered "<<ec<<"\npairs "<<pairs<<"\ntruth_functions "<<functions<<"\ncap_models "<<capmodels<<"\nactual_robust_pairs "<<actualrp<<"\nactual_possible_pairs "<<actualpp<<"\nactual_robust_functions "<<actualrf<<"\nactual_possible_functions "<<actualpf<<'\n';require(bool(sum),"summary write");
 std::ofstream ll(d+"/level-coverage.csv");ll<<"ell,covered_labelings,actual_label_covered\n";for(int k=0;k<x.l;k++)ll<<x.levels[k].ell<<','<<perlevel[k]<<','<<bool(x.labels[actualid].capbits&(Q(1)<<k))<<'\n';require(bool(ll),"level summary write");std::cout<<"ENUMERATOR_COMPLETE "<<robust<<' '<<possible<<' '<<cap<<'\n';
}
std::pair<bool,bool> exists(Sig a,Sig b,U mask,U fixed,U full){
 auto z=bins(a,b);U req1=0,req0=0,known1=0;for(int j=0;j<4;j++){if(z[j]&mask)req1|=1u<<j;if(z[j]&(full^mask))req0|=1u<<j;if(z[j]&(mask&~fixed))known1|=1u<<j;}bool robust=(req1&req0)==0;bool possible=(known1&req0)==0;
 for(U bits=fixed;bits&&possible;bits&=bits-1){U bit=bits&-bits;U choices=0;for(int j=0;j<4;j++)if(z[j]&bit)choices|=1u<<j;if((choices&~req0)==0)possible=false;}return {robust,possible};
}
void verify(Input x,const std::string&d){
 std::vector<U> population;for(U mask=0;mask<=x.full;mask++){bool ok=true;for(auto p:x.strata)if(__builtin_popcount(mask&p.first)!=p.second){ok=false;break;}if(ok)population.push_back(mask);}require(population.size()==x.labels.size(),"independent population cardinality");for(int i=0;i<x.k;i++)require(population[i]==x.labels[i].mask,"independent complete population");
 std::ifstream in(d+"/coverage.csv");std::string line;std::getline(in,line);int robust=0,possible=0,cap=0,er=0,ep=0,ec=0;Q negativechecks=0;std::ofstream absence(d+"/absence-checks.csv");absence<<"mask,robust_absence_verified,possible_absence_verified,pairs_checked\n";
 for(int i=0;i<x.k;i++){
  require(bool(std::getline(in,line)),"coverage row read");std::replace(line.begin(),line.end(),',',' ');std::istringstream row(line);int id,e;U mask;Witness rw,pw;Q cb;int ce,cc,cd;row>>id>>mask>>e>>rw.a>>rw.b>>rw.f>>pw.a>>pw.b>>pw.f>>cb>>ce>>cc>>cd;require(bool(row)&&id==i&&mask==x.labels[i].mask&&e==x.labels[i].endpoint,"coverage identity");bool r=rw.a>=0,p=pw.a>=0;
  for(auto w:{rw,pw})if(w.a>=0)require(w.a<w.b&&w.b<x.m&&w.f>=0&&w.f<16,"witness indices");
  if(r)require(witness_ok(x.sigs[rw.a],x.sigs[rw.b],mask,rw.f,x.n,true),"robust rowwise witness");if(p)require(witness_ok(x.sigs[pw.a],x.sigs[pw.b],mask,pw.f,x.n,false),"possible rowwise witness");
  Q scanned=0;if(!r||!p){for(int a=0;a<x.m;a++)for(int b=a+1;b<x.m;b++){auto ex=exists(x.sigs[a],x.sigs[b],mask,x.fixed,x.full);require(r||!ex.first,"false robust absence");require(p||!ex.second,"false possible absence");scanned++;}negativechecks+=scanned;absence<<mask<<','<<!r<<','<<!p<<','<<scanned<<'\n';}
  Q computed=0;for(int k=0;k<x.l;k++){auto&v=x.levels[k];int c=0,dd=0;for(int j=0;j<x.n;j++)if(mask&(1u<<j)){c=std::max(c,v.points[j].c);dd=std::max(dd,v.points[j].d);}bool found=true;for(int j=0;j<x.n;j++)if(!(mask&(1u<<j))&&v.points[j].c<=c&&v.points[j].d<=dd){found=false;break;}if(found)computed|=Q(1)<<k;}require(computed==cb,"independent rectangle coverage");if(cb){int k=0;while(k<x.l&&x.levels[k].ell!=ce)k++;require(k<x.l,"cap witness level");U pred=0;for(int j=0;j<x.n;j++)if(x.levels[k].points[j].c<=cc&&x.levels[k].points[j].d<=cd)pred|=1u<<j;require(pred==mask,"cap witness prediction");}
  robust+=r;possible+=p;cap+=cb!=0;er+=e&&r;ep+=e&&p;ec+=e&&cb!=0;
 }
 Q rp=0,pp=0,rf=0,pf=0;for(int a=0;a<x.m;a++)for(int b=a+1;b<x.m;b++){
  auto z=bins(x.sigs[a],x.sigs[b]);U pos=0,neg=0,known=0;for(int j=0;j<4;j++){if(z[j]&x.actual)pos|=1u<<j;if(z[j]&(x.full^x.actual))neg|=1u<<j;if(z[j]&(x.actual&~x.fixed))known|=1u<<j;}
  if((pos&neg)==0){rp++;rf+=Q(1)<<(4-__builtin_popcount(pos|neg));}
  bool any=false;if((known&neg)==0)for(U f=0;f<16;f++)if((f&known)==known&&!(f&neg)){bool ok=true;for(U bits=x.fixed;bits;bits&=bits-1){U bit=bits&-bits,choices=0;for(int j=0;j<4;j++)if(z[j]&bit)choices|=1u<<j;if(!(choices&f)){ok=false;break;}}if(ok){pf++;any=true;}}pp+=any;
 }
 require(rp==16&&pp==16&&rf==19&&pf==19,"independent actual fit counts");std::ofstream out(d+"/verifier-summary.txt");out<<"labels "<<x.k<<"\nendpoint_labels 126\nfull_robust_covered "<<robust<<"\nfull_possible_covered "<<possible<<"\ncaps_covered "<<cap<<"\nendpoint_full_robust "<<er<<"\nendpoint_full_possible "<<ep<<"\nendpoint_caps_covered "<<ec<<"\nnegative_pairs_checked "<<negativechecks<<"\nactual_robust_pairs "<<rp<<"\nactual_possible_pairs "<<pp<<"\nactual_robust_functions "<<rf<<"\nactual_possible_functions "<<pf<<'\n';require(bool(out),"verifier summary");std::cout<<"VERIFIER_COMPLETE "<<robust<<' '<<possible<<' '<<cap<<'\n';
}
int main(int argc,char**argv){try{require(argc==3,"usage: calibrate enumerate|verify DIRECTORY");controls();Input x=load(argv[2]);std::string mode=argv[1];if(mode=="enumerate")enumerate(x,argv[2]);else if(mode=="verify")verify(x,argv[2]);else throw std::runtime_error("unknown mode");return 0;}catch(const std::exception&e){std::cerr<<"CALIBRATION_ERROR "<<e.what()<<'\n';return 2;}}
