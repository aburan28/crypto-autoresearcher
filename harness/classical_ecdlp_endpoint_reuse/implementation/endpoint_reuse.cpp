#include "bridge.hpp"
#include <cstring>
#include <limits>

namespace endpoint {
constexpr const char* row_schema="classical.ecdlp.endpoint-reuse.row.v1";
struct Settings {std::string cell,fixture;unsigned replicate=0;int dp=0;U initial=0,cap=0,precomp_limit=0,online_limit=0,seed=0;};
struct PublicTarget {std::string fixture,id;unsigned replicate=0;U ordinal=0;Point q;};
void reject_negative_columns(const std::string&line,const std::set<unsigned>&columns){std::istringstream in(line);std::string token;unsigned index=0;while(in>>token){if(columns.contains(index))lab::require(token.empty()||token[0]!='-',"negative public unsigned/canonical column");index++;}}
std::vector<lab::Fixture> read_fixtures(const std::string&path){
 std::ifstream in(path);lab::require(bool(in),"cannot open public fixtures");std::vector<lab::Fixture> out;std::set<std::string> ids;std::string line;
 while(std::getline(in,line)){if(line.empty()||line[0]=='#'||line=="fixture_id\tstratum\tp\ta\tb\tgx\tgy\tr\tN\tseed")continue;reject_negative_columns(line,{2,3,4,5,6,7,8,9});lab::Fixture f;std::istringstream row(line);row>>f.id>>f.stratum>>f.c.p>>f.c.a>>f.c.b>>f.P.x>>f.P.y>>f.r>>f.N>>f.seed;std::string extra;f.P.inf=false;lab::require(!row.fail()&&!(row>>extra),"public fixture columns malformed");lab::require(ids.insert(f.id).second,"duplicate fixture id");out.push_back(f);}
 lab::require(!out.empty(),"empty public fixtures");return out;
}
std::vector<Settings> read_settings(const std::string&path){
 std::ifstream in(path);lab::require(bool(in),"cannot open settings");std::vector<Settings> out;std::set<std::string> ids;std::string line;
 while(std::getline(in,line)){if(line.empty()||line[0]=='#'||line=="cell_id\tfixture_id\treplicate\tdp_bits\tinitial_chains\tendpoint_cap\tmax_precomp_ops\tmax_online_ops\tseed")continue;reject_negative_columns(line,{2,3,4,5,6,7,8});Settings s;std::istringstream row(line);row>>s.cell>>s.fixture>>s.replicate>>s.dp>>s.initial>>s.cap>>s.precomp_limit>>s.online_limit>>s.seed;std::string extra;
 lab::require(!row.fail()&&!(row>>extra),"settings columns malformed");lab::require(s.replicate<2&&s.dp>=0&&s.dp<=20&&s.initial>0&&s.cap>=s.initial&&s.seed!=0,"invalid settings");lab::require(ids.insert(s.cell).second,"duplicate cell id");out.push_back(s);}
 lab::require(!out.empty(),"empty settings");return out;
}
std::vector<PublicTarget> read_targets(const std::string&path){
 std::ifstream in(path);lab::require(bool(in),"cannot open public targets");std::vector<PublicTarget> out;std::set<std::string> ids;std::map<std::pair<std::string,unsigned>,U> ordinals;std::string line;
 while(std::getline(in,line)){if(line.empty()||line[0]=='#'||line=="fixture_id\treplicate\ttarget_id\ttarget_ordinal\tqx\tqy\tinfinity")continue;reject_negative_columns(line,{1,3,4,5,6});PublicTarget t;I inf=-1;std::istringstream row(line);row>>t.fixture>>t.replicate>>t.id>>t.ordinal>>t.q.x>>t.q.y>>inf;std::string extra;
 lab::require(!row.fail()&&!(row>>extra)&&t.replicate<2&&(inf==0||inf==1),"public target columns malformed; no hidden scalar columns accepted");t.q.inf=inf!=0;
 lab::require(t.ordinal==ordinals[{t.fixture,t.replicate}]++,"noncontiguous target ordinal");lab::require(ids.insert(t.id).second,"duplicate target id");out.push_back(t);}
 lab::require(!out.empty(),"empty public target panel");return out;
}
std::string point_json(Point q){return "{\"x\":"+std::to_string(q.x)+",\"y\":"+std::to_string(q.y)+",\"infinity\":"+(q.inf?"true":"false")+"}";}
std::string status_name(ca_status s,bool solved=false){if(s==CA_OK)return solved?"solved":"ready";if(s==CA_ERR_LIMIT||s==CA_ERR_NOMEM)return "censored";if(s==CA_ERR_INVALID||s==CA_ERR_INTERNAL)return "invalid";return "failed";}
std::string upstream_stats_json(const ca_stats&s){std::ostringstream o;o<<"{\"reported_group_ops\":"<<s.group_ops<<",\"iterations\":"<<s.iterations<<",\"table_entries\":"<<s.table_entries<<",\"collisions\":"<<s.collisions<<",\"table_bytes_peak_estimate\":"<<s.bytes_peak<<",\"threads\":"<<s.threads<<"}";return o.str();}
std::string rng_json(er_rng_counts c){return "{\"seed_calls\":"+std::to_string(c.seed_calls)+",\"word_draws\":"+std::to_string(c.word_draws)+",\"below_calls\":"+std::to_string(c.below_calls)+"}";}
std::string reuse_json(const er_reuse_stats&s){std::ostringstream o;o<<'{';bool first=true;
#define EMIT_REUSE(field) if(!first)o<<',';first=false;o<<'"'<<#field<<"\":"<<s.field;
 EMIT_REUSE(unmatched_dp) EMIT_REUSE(chain_limit_restarts) EMIT_REUSE(staged) EMIT_REUSE(capacity_rejections)
 EMIT_REUSE(exact_exponent_comparisons) EMIT_REUSE(scalar_addmods) EMIT_REUSE(sort_comparisons)
 EMIT_REUSE(bucket_candidates_verified) EMIT_REUSE(rejected_bucket_witnesses) EMIT_REUSE(proposed)
 EMIT_REUSE(inserted) EMIT_REUSE(duplicates) EMIT_REUSE(fingerprint_aliases) EMIT_REUSE(rolled_back)
 EMIT_REUSE(known_before) EMIT_REUSE(known_after) EMIT_REUSE(pending_peak) EMIT_REUSE(capacity)
#undef EMIT_REUSE
 o<<'}';return o.str();}
std::string fill_json(const er_fill_stats&s){std::ostringstream o;o<<'{';bool first=true;
#define EMIT_FILL(field) if(!first)o<<',';first=false;o<<'"'<<#field<<"\":"<<s.field;
 EMIT_FILL(seed) EMIT_FILL(starts) EMIT_FILL(max_starts) EMIT_FILL(terminals) EMIT_FILL(chain_limit_restarts)
 EMIT_FILL(duplicates) EMIT_FILL(inserted) EMIT_FILL(reported_group_ops) EMIT_FILL(known_before) EMIT_FILL(known_after) EMIT_FILL(capacity)
#undef EMIT_FILL
 o<<",\"work\":"<<reuse_json(s.work)<<'}';return o.str();}
std::string memory_json(const er_memory&m){std::ostringstream o;o<<'{';bool first=true;
#define EMIT_MEMORY(field) if(!first)o<<',';first=false;o<<'"'<<#field<<"\":"<<m.field;
 EMIT_MEMORY(known) EMIT_MEMORY(endpoint_capacity) EMIT_MEMORY(endpoint_allocated_bytes)
 EMIT_MEMORY(fixed_base_bytes) EMIT_MEMORY(adding_points_bytes) EMIT_MEMORY(adding_scalars_bytes)
 EMIT_MEMORY(object_bytes) EMIT_MEMORY(build_worker_entry_capacity) EMIT_MEMORY(build_worker_entry_bytes)
 EMIT_MEMORY(build_live_array_bytes) EMIT_MEMORY(build_control_bytes)
#undef EMIT_MEMORY
 o<<",\"growth_sort_stack_entry_bytes\":16,\"scope\":\"Requested bytes only; excludes allocator metadata, setup library-sort scratch, pthread stack and RSS. Build fields are a conservative simultaneously-live upper bound; candidate growth uses no heap beyond the arena.\"}";return o.str();}
U entry_digest(er_entry e){return dec::mix(e.fp^std::rotl(e.exp,17)^0x65726c61622d7631ULL);}
struct Table {
 const lab::Fixture&f;Settings setting;std::string arm;dec::Ops ops;Adapter adapter;
 ca_precomp_table* fixed=nullptr;er_precomp_table* growing=nullptr;ca_status setup_status=CA_OK;ca_stats build_stats{};er_fill_stats fill_stats{};U setup_reported_upper=0,walk_limit=0;dec::Cost setup_cost;Aux setup_aux;er_rng_counts setup_rng{};U state_hash=0;
 Table(const lab::Fixture&fixture,const Settings&s,std::string name):f(fixture),setting(s),arm(std::move(name)),ops(f.c),adapter(f,ops){
  if(arm=="rho_reference")return;
  setup_reported_upper=21U*(lab::bits(static_cast<U>(f.r))-1U);
  if(s.precomp_limit&&s.precomp_limit<=setup_reported_upper){setup_status=CA_ERR_LIMIT;return;}
  walk_limit=s.precomp_limit?s.precomp_limit-setup_reported_upper:0;
  er_rng_reset();ca_precomp_params p;ca_precomp_params_default(&p);p.seed=s.seed;p.r=20;p.dp_bits=s.dp;p.table_size=arm=="static_full"?s.cap:s.initial;p.threads=1;p.walks=1;p.early_abort=0;p.max_precomp_ops=walk_limit;p.max_online_ops=s.online_limit;
  const auto base=element(f.P);
  if(arm=="harvest"||arm=="harvest_disabled"||arm=="static_filled"){
   setup_status=er_precomp_table_new(&adapter.g,&base,&p,&growing,&build_stats);
   if(setup_status==CA_OK){setup_status=er_recycle_configure(growing,s.cap,arm=="harvest");
    if(setup_status!=CA_OK){er_precomp_table_free(growing);growing=nullptr;}}
   if(setup_status==CA_OK&&arm=="static_filled")setup_status=er_precompute_fill(growing,s.precomp_limit,build_stats.group_ops,&fill_stats);
  }else{
   setup_status=ca_precomp_table_new(&adapter.g,&base,&p,&fixed,&build_stats);
   if(setup_status==CA_OK){setup_status=er_static_reserve(fixed,s.cap);
    if(setup_status!=CA_OK){ca_precomp_table_free(fixed);fixed=nullptr;}}
  }
  setup_cost=ops.cost;setup_aux=adapter.aux;setup_rng=er_rng_snapshot();
  if(fixed||growing){lab::require(size()<=s.cap,"initial endpoint cap exceeded");for(U i=0;i<size();i++)state_hash^=entry_digest(entry(i));}
 }
 ~Table(){if(fixed)ca_precomp_table_free(fixed);if(growing)er_precomp_table_free(growing);}
 Table(const Table&)=delete;Table&operator=(const Table&)=delete;
 U size()const{return growing?er_recycle_entries(growing,nullptr,0):(fixed?er_static_entries(fixed,nullptr,0):0);}
 er_entry entry(U i)const{er_entry e{};lab::require((growing?er_recycle_entry_at(growing,i,&e):er_static_entry_at(fixed,i,&e))!=0,"endpoint snapshot index invalid");return e;}
 er_memory memory()const{er_memory m{};if(growing)er_recycle_memory(growing,&build_stats,&m);else if(fixed)er_static_memory(fixed,&build_stats,setting.cap,&m);return m;}
};
struct Stream {
 std::ostream&out;const lab::Fixture&f;const Settings&s;const std::string&arm;const PublicTarget* target=nullptr;U provisional_hash=0,rows=0;
 std::string common(const std::string&kind)const{std::ostringstream o;o<<"{\"schema\":"<<lab::json_quote(row_schema)<<",\"scope\":"<<lab::json_quote(scope)<<",\"row_kind\":"<<lab::json_quote(kind)<<",\"cell_id\":"<<lab::json_quote(s.cell)<<",\"fixture\":"<<lab::json_quote(f.id)<<",\"replicate\":"<<s.replicate<<",\"arm\":"<<lab::json_quote(arm);return o.str();}
 std::string target_fields()const{return ",\"target_id\":"+lab::json_quote(target->id)+",\"target_ordinal\":"+std::to_string(target->ordinal);}
 void write(const std::string&line){out<<line<<"}\n";++rows;lab::require(bool(out),"raw output write failed");}
 static int event(void*context,const er_event*e){auto&stream=*static_cast<Stream*>(context);try{stream.emit(*e);return 1;}catch(...){return 0;}}
 void emit(const er_event&e){
  const std::string state=",\"known_count\":"+std::to_string(e.known)+",\"pending_count\":"+std::to_string(e.pending)+",\"endpoint_cap\":"+std::to_string(s.cap);
  std::ostringstream o;
  if(e.kind==1||e.kind==2){o<<common("terminal")<<target_fields()<<",\"attempt\":"<<e.attempt<<",\"reason\":"<<lab::json_quote(e.kind==1?"unmatched_dp":"chain_limit")<<",\"point\":"<<point_json(point(e.point))<<",\"offset_a\":"<<e.a<<",\"fp\":"<<e.fp<<",\"pending_slot\":"<<(e.pending_slot==std::numeric_limits<U>::max()?"null":std::to_string(e.pending_slot))<<state;}
  else if(e.kind==3){o<<common("harvest_proposal")<<target_fields()<<",\"pending_slot\":"<<e.pending_slot<<",\"fp\":"<<e.fp<<",\"exponent\":"<<e.exponent<<",\"accepted\":"<<(e.accepted?"true":"false")<<state;if(e.accepted)provisional_hash^=entry_digest({e.fp,e.exponent});}
  else if(e.kind==4){o<<common("harvest_commit_ready")<<target_fields()<<",\"accepted_count\":"<<e.accepted<<state;}
  else if(e.kind==6){o<<common("verified_solution")<<target_fields()<<",\"point\":"<<point_json(point(e.point))<<",\"verified_scalar\":"<<e.exponent<<",\"public_equation_checked\":true"<<state;}
  else if(e.kind==7){o<<common("lookup")<<target_fields()<<",\"attempt\":"<<e.attempt<<",\"fp\":"<<e.fp<<",\"offset_a\":"<<e.a<<",\"lookup_begin\":0,\"lookup_end_exclusive\":"<<e.known<<state;}
  else if(e.kind==8){const U candidate=e.exponent>=e.a?e.exponent-e.a:static_cast<U>(f.r)-(e.a-e.exponent);o<<common("lookup_witness")<<target_fields()<<",\"attempt\":"<<e.attempt<<",\"entry_index\":"<<e.pending_slot<<",\"fp\":"<<e.fp<<",\"exponent\":"<<e.exponent<<",\"offset_a\":"<<e.a<<",\"candidate_scalar\":"<<candidate<<",\"public_equation_checked\":true,\"verified\":"<<(e.accepted?"true":"false")<<state;}
  else throw std::runtime_error("unknown C event kind");
  write(o.str());
 }
};
void emit_setup(Stream&stream,Table&t){
 const auto&s=t.setting;std::ostringstream o;o<<stream.common("setup")<<",\"status\":"<<lab::json_quote(status_name(t.setup_status))<<",\"parameters\":{\"dp_bits\":"<<s.dp<<",\"parameter_scope\":"<<lab::json_quote(t.arm=="rho_reference"?"BL input-cell settings, not applied to rho reference":"actual BL settings")<<",\"rho_auto_requested\":"<<(t.arm=="rho_reference"?"true":"false")<<",\"initial_chains\":"<<s.initial<<",\"requested_build_chains\":"<<(t.arm=="static_full"?s.cap:(t.arm=="rho_reference"?0:s.initial))<<",\"endpoint_cap\":"<<s.cap<<",\"max_precomp_ops\":"<<s.precomp_limit<<",\"upstream_max_precomp_walk_ops\":"<<t.walk_limit<<",\"reported_setup_upper_bound\":"<<t.setup_reported_upper<<",\"fill_goal\":"<<(t.arm=="static_filled"?s.cap:0)<<",\"max_online_ops\":"<<s.online_limit<<",\"seed\":"<<s.seed<<",\"threads\":1,\"walks\":1,\"early_abort\":false,\"adding_steps\":20,\"max_online_attempts\":512},\"counters\":"<<dec::cost_json(t.setup_cost)<<",\"auxiliary_work\":"<<aux_json(t.setup_aux)<<",\"upstream_stats\":"<<upstream_stats_json(t.build_stats)<<",\"rng\":"<<rng_json(t.setup_rng)<<",\"fill\":"<<fill_json(t.fill_stats)<<",\"precompute_reported_ops_total\":"<<(t.build_stats.group_ops+t.fill_stats.reported_group_ops)<<",\"memory\":"<<memory_json(t.memory())<<",\"known_count\":"<<t.size()<<",\"endpoint_cap\":"<<s.cap<<",\"table_state_hash64\":"<<t.state_hash;stream.write(o.str());
 for(U i=0;i<t.size();i++){const auto e=t.entry(i);stream.write(stream.common("initial_endpoint")+",\"index\":"+std::to_string(i)+",\"fp\":"+std::to_string(e.fp)+",\"exponent\":"+std::to_string(e.exp));}
}
void emit_target(Stream&stream,Table&t,const PublicTarget&q){
 stream.target=&q;stream.provisional_hash=t.state_hash;t.adapter.aux={};er_rng_reset();const auto before=t.ops.cost;const U known_before=t.size();ca_stats st{};er_reuse_stats reuse{};reuse.known_before=known_before;reuse.known_after=known_before;reuse.capacity=t.arm=="rho_reference"?0:t.setting.cap;U x=0,actual_rho_seed=0;ca_status status=t.setup_status;
 const auto point_q=element(q.q);
 if(t.arm=="rho_reference"){
  ca_rho_params p;ca_rho_params_default(&p);p.seed=nonzero_seed(t.setting.seed^dec::hash("endpoint-reuse.rho.v1")^dec::mix(q.ordinal+1));actual_rho_seed=p.seed;p.threads=1;p.negation_map=1;p.max_ops=t.setting.online_limit;const auto base=element(t.f.P);status=ca_rho_solve(&t.adapter.g,&base,&point_q,&p,&x,&st);
 }else if(status==CA_OK){
  if(t.growing)status=er_recycle_solve(t.growing,&point_q,&x,&st,&reuse,Stream::event,&stream);
  else status=ca_precomp_table_solve(t.fixed,&point_q,&x,&st);
 }
 if(status==CA_OK){++t.ops.cost.candidate_verifications;lab::require(x<static_cast<U>(t.f.r)&&t.ops.scalar(t.f.P,x)==q.q,"returned witness failed public equation");}
 if(t.arm=="harvest"&&status==CA_OK)t.state_hash=stream.provisional_hash;
 const auto cost=dec::difference(t.ops.cost,before);
 if(!t.growing){reuse.known_before=known_before;reuse.known_after=t.size();reuse.capacity=t.arm=="rho_reference"?0:t.setting.cap;}
 lab::require(t.size()<=t.setting.cap,"known endpoint cap violated");
 std::ostringstream o;o<<stream.common("target")<<stream.target_fields()<<",\"point\":"<<point_json(q.q)<<",\"status\":"<<lab::json_quote(status_name(status,status==CA_OK))<<",\"upstream_status\":"<<static_cast<int>(status)<<",\"rho_seed\":"<<(t.arm=="rho_reference"?std::to_string(actual_rho_seed):"null")<<",\"verified_scalar\":"<<(status==CA_OK?std::to_string(x):"null")<<",\"public_equation_checked\":"<<(status==CA_OK?"true":"false")<<",\"counters\":"<<dec::cost_json(cost)<<",\"auxiliary_work\":"<<aux_json(t.adapter.aux)<<",\"upstream_stats\":"<<upstream_stats_json(st)<<",\"rng\":"<<rng_json(er_rng_snapshot())<<",\"reuse\":"<<reuse_json(reuse)<<",\"known_count\":"<<t.size()<<",\"pending_count\":0,\"endpoint_cap\":"<<t.setting.cap<<",\"table_state_hash64\":"<<t.state_hash<<",\"harvest_committed\":"<<(t.arm=="harvest"&&status==CA_OK?"true":"false");stream.write(o.str());
}
int run(const std::string&fixtures_path,const std::string&targets_path,const std::string&settings_path,const std::string&arm,const std::string&output){
 lab::require(std::set<std::string>{"static_full","static_small","static_filled","harvest","harvest_disabled","rho_reference"}.contains(arm),"unknown arm");lab::require(!std::filesystem::exists(output),"refusing existing output");
 const auto fixtures=read_fixtures(fixtures_path);const auto targets=read_targets(targets_path);const auto settings=read_settings(settings_path);std::map<std::string,lab::Fixture> by_id;for(const auto&f:fixtures)by_id.emplace(f.id,f);
 for(const auto&q:targets)lab::require(by_id.contains(q.fixture),"target fixture unknown");
 std::ofstream out(output);lab::require(bool(out),"cannot create raw output");U count=0,total_targets=0;
 for(const auto&s:settings){lab::require(by_id.contains(s.fixture),"settings fixture unknown");const auto&f=by_id.at(s.fixture);lab::require(s.cap<=static_cast<U>(f.r),"endpoint capacity exceeds subgroup population");std::vector<const PublicTarget*> panel;for(const auto&q:targets)if(q.fixture==s.fixture&&q.replicate==s.replicate)panel.push_back(&q);lab::require(!panel.empty(),"cell has no targets");
  dec::Ops validation(f.c);dec::validate_fixture(f,validation);for(const auto*q:panel)lab::require(validation.valid(q->q)&&validation.scalar(q->q,static_cast<U>(f.r)).inf,"public target outside subgroup");
  Stream stream{out,f,s,arm};std::ostringstream v;v<<stream.common("fixture_validation")<<",\"curve\":{\"p\":"<<f.c.p<<",\"a\":"<<f.c.a<<",\"b\":"<<f.c.b<<"},\"base\":"<<point_json(f.P)<<",\"order\":"<<f.r<<",\"total_order\":"<<f.N<<",\"counters\":"<<dec::cost_json(validation.cost)<<",\"target_count\":"<<panel.size();stream.write(v.str());
  Table table(f,s,arm);emit_setup(stream,table);for(const auto*q:panel){emit_target(stream,table,*q);total_targets++;}count+=stream.rows;
 }
 out.flush();lab::require(bool(out),"raw output flush failed");std::cout<<"{\"rows\":"<<count<<",\"cells\":"<<settings.size()<<",\"targets\":"<<total_targets<<",\"clocks_emitted\":false}\n";return 0;
}
int self_test();
} // namespace endpoint
#include "tests/self_test.inc"
extern "C" void ca_group_mul(const ca_group*g,ca_elem*r,const ca_elem*a,std::uint64_t k,std::uint64_t*count){auto&ops=*endpoint::adapter(g).ops;const auto before=ops.cost.group_additions;*r=endpoint::element(ops.scalar(endpoint::point(*a),k));if(count)*count+=ops.cost.group_additions-before;}
extern "C" int ca_check_members(const ca_group*g,const ca_elem*base,const ca_elem*target,std::uint64_t n,const char*){ca_elem p{},q{};ca_group_mul(g,&p,base,n,nullptr);ca_group_mul(g,&q,target,n,nullptr);return ca_group_is_identity(g,&p)&&ca_group_is_identity(g,&q);}
int main(int argc,char**argv){try{if(argc==2&&std::string(argv[1])=="--self-test")return endpoint::self_test();if(argc==7&&std::string(argv[1])=="--run")return endpoint::run(argv[2],argv[3],argv[4],argv[5],argv[6]);throw std::runtime_error("usage: endpoint_reuse --self-test | --run FIXTURES TARGETS SETTINGS ARM FRESH_OUTPUT");}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 2;}}
