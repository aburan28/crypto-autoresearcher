namespace endpoint {
int self_test(){
 unsigned checks=0;auto check=[&](bool b,const char*m){lab::require(b,m);++checks;};
 std::vector<lab::Fixture> fixtures{{"dev-small","ordinary",{17,2,2},{5,1,false},19,19,0x2915U},{"dev-rho","ordinary",{383,261,146},{196,297,false},181,362,0x1144U},{"dev-wide","ordinary",{65537,1,7},{13979,44364,false},13121,65605,0x1741U}};
 for(const auto&f:fixtures){
  dec::Ops validation(f.c);dec::validate_fixture(f,validation);
  const int dp=static_cast<int>(lab::bits(static_cast<U>(f.r))/3);const U denominator=U{1}<<(2*dp),initial=(static_cast<U>(f.r)+denominator/2)/denominator;
  Settings s{"fixed-development",f.id,0,dp,initial,std::min(static_cast<U>(f.r),4*initial),0,0,0x134572U};
  Table small(f,s,"static_small"),disabled(f,s,"harvest_disabled"),candidate(f,s,"harvest");
  check(small.setup_status==CA_OK&&disabled.setup_status==CA_OK&&candidate.setup_status==CA_OK,"fixed BL setup");
  check(dec::cost_json(small.setup_cost)==dec::cost_json(disabled.setup_cost),"A/A exact setup EC vector");
  check(aux_json(small.setup_aux)==aux_json(disabled.setup_aux),"A/A exact setup auxiliary vector");
  check(small.size()==disabled.size()&&small.size()==candidate.size(),"initial known prefix size");
  for(U i=0;i<small.size();i++)check(small.entry(i).fp==disabled.entry(i).fp&&small.entry(i).exp==disabled.entry(i).exp&&small.entry(i).fp==candidate.entry(i).fp&&small.entry(i).exp==candidate.entry(i).exp,"initial prefix bytes identical");
  for(U k:{U{0},U{1},U{2},U{7},static_cast<U>(f.r-1)}){
   const auto q=element(f.c.mul(f.P,k));const auto a0=small.ops.cost,b0=disabled.ops.cost;small.adapter.aux={};disabled.adapter.aux={};ca_stats sa{},sb{};er_reuse_stats reuse{};U x=0,y=0;
   const auto ra=ca_precomp_table_solve(small.fixed,&q,&x,&sa),rb=er_recycle_solve(disabled.growing,&q,&y,&sb,&reuse,nullptr,nullptr);
   if(!(ra==rb&&x==y&&ra==CA_OK&&x==k))std::cerr<<"AA diagnosis fixture="<<f.id<<" k="<<k<<" status="<<static_cast<int>(ra)<<","<<static_cast<int>(rb)<<" x="<<x<<","<<y<<" known="<<small.size()<<","<<disabled.size()<<"\n";
   check(ra==rb&&x==y&&ra==CA_OK&&x==k,"A/A fixed scalar status equality");
   check(dec::cost_json(dec::difference(small.ops.cost,a0))==dec::cost_json(dec::difference(disabled.ops.cost,b0)),"A/A exact online EC vector");
   check(aux_json(small.adapter.aux)==aux_json(disabled.adapter.aux),"A/A exact online auxiliary vector");
   check(sa.group_ops==sb.group_ops&&sa.iterations==sb.iterations&&sa.collisions==sb.collisions,"A/A upstream deterministic path");
   std::vector<er_event> events;auto capture=[](void*c,const er_event*e){static_cast<std::vector<er_event>*>(c)->push_back(*e);return 1;};ca_stats cs{};er_reuse_stats growth{};U z=0;
   check(er_recycle_solve(candidate.growing,&q,&z,&cs,&growth,capture,&events)==CA_OK&&z==k,"candidate fixed scalar recovery");
   bool verified=false;std::map<U,er_event> staged;
   for(const auto&e:events){
    check(e.known+e.pending<=s.cap,"arena active plus pending cap");
    if(e.kind==1){check(f.c.mul(f.P,(k+e.a)%static_cast<U>(f.r))==point(e.point),"terminal D=(x+a)P");if(e.pending_slot!=std::numeric_limits<U>::max())staged.emplace(e.pending_slot,e);}
    if(e.kind==6){check(!verified&&e.exponent==k&&point(e.point)==point(q),"causal verified solution event");verified=true;}
    if(e.kind==3){check(verified&&staged.contains(e.pending_slot),"no admission before public witness");check(e.exponent==(k+staged.at(e.pending_slot).a)%static_cast<U>(f.r),"admitted exponent formula");}
    if(e.kind==8)check(e.pending_slot<e.known,"pending never searched");
   }
   check(verified,"success emits public verification before admission");
   if(growth.inserted==0)check(growth.sort_comparisons==0,"zero insertions skip already-sorted prefix");
   std::set<U> exact;for(U i=0;i<candidate.size();i++){auto e=candidate.entry(i);check(e.exp<static_cast<U>(f.r)&&exact.insert(e.exp).second,"canonical exact endpoint dedup");const auto d=element(f.c.mul(f.P,e.exp));check(hash_point(&candidate.adapter.g,&d)==e.fp,"known endpoint witness remains valid");}
  }
 }
#ifdef ER_DEVELOPMENT_API
 check(er_rng_development_check()!=0,"instrumented RNG exact pinned stream");
 {
  const auto&f=fixtures[1];Settings s{"forced-development",f.id,0,0,1,8,0,0,0x184155U};Table t(f,s,"harvest");t.adapter.force_hash=true;t.adapter.forced_hash=0;
  check(er_test_replace(t.growing,nullptr,0)==CA_OK,"empty controlled known prefix");
  U k=7;auto q=element(f.c.mul(f.P,k));std::vector<er_event> events;auto capture=[](void*c,const er_event*e){if(e->kind==1)static_cast<std::vector<er_event>*>(c)->push_back(*e);return 1;};U x=0;ca_stats st{};er_reuse_stats rs{};
  check(er_recycle_solve(t.growing,&q,&x,&st,&rs,capture,&events)==CA_ERR_NOT_FOUND,"pending cannot solve its own target");
  check(t.size()==0&&rs.rolled_back==s.cap,"failed target rolls back every pending slot");check(events.size()==512,"forced no-match attempts retained");
  const U a=events[0].a;U correct=(a+k)%static_cast<U>(f.r);if(correct==0){k=8;q=element(f.c.mul(f.P,k));correct=(a+k)%static_cast<U>(f.r);}check(correct>0,"collision control canonical exponent");
  er_entry aliases[2]{{0,correct-1},{0,correct}};check(er_test_replace(t.growing,aliases,2)==CA_OK,"forced fingerprint aliases installed");events.clear();st={};rs={};
  check(er_recycle_solve(t.growing,&q,&x,&st,&rs,capture,&events)==CA_OK&&x==k,"later fingerprint alias returns correct witness");check(rs.bucket_candidates_verified==2&&rs.rejected_bucket_witnesses==1,"wrong first fingerprint witness rejected");
  std::size_t j=1;std::vector<er_event> starts;check(er_test_replace(t.growing,nullptr,0)==CA_OK,"reset empty retry control");st={};rs={};
  check(er_recycle_solve(t.growing,&q,&x,&st,&rs,capture,&starts)==CA_ERR_NOT_FOUND,"record deterministic retry offsets");while(j<starts.size()&&starts[j].a==starts[0].a)j++;check(j<starts.size(),"distinct retry offset exists");
  er_entry retry{0,(starts[j].a+k)%static_cast<U>(f.r)};check(er_test_replace(t.growing,&retry,1)==CA_OK,"known later endpoint installed");st={};rs={};events.clear();
  check(er_recycle_solve(t.growing,&q,&x,&st,&rs,capture,&events)==CA_OK&&x==k&&st.iterations==j+1,"forced retry hit positive control");check(rs.inserted==1&&t.size()==2,"failed earlier endpoint activated after success");st={};rs={};
  check(er_recycle_solve(t.growing,&q,&x,&st,&rs,capture,&events)==CA_OK&&st.iterations==1,"harvested endpoint first-hit positive control");
  check(er_test_replace(t.growing,nullptr,0)==CA_OK,"reset staging controls");const U e=9,offset=(e+static_cast<U>(f.r)-k)%static_cast<U>(f.r);const auto d=element(f.c.mul(f.P,e));
  check(er_test_stage(t.growing,&d,offset)==CA_OK,"stage witnessed endpoint");rs={};check(er_test_commit(t.growing,&q,(k+1)%static_cast<U>(f.r),&rs)==CA_ERR_INVALID&&t.size()==0&&rs.rolled_back==1,"wrong witness cannot activate endpoint");
  check(er_test_stage(t.growing,&d,offset)==CA_OK&&er_test_stage(t.growing,&d,offset)==CA_OK,"stage duplicate exact point");rs={};check(er_test_commit(t.growing,&q,k,&rs)==CA_OK&&t.size()==1&&rs.inserted==1&&rs.duplicates==1,"dedup repeated full point by canonical exponent");
  check(er_recycle_configure(t.growing,1,1)==CA_OK&&er_test_stage(t.growing,&d,offset)==CA_ERR_LIMIT&&t.size()==1,"zero remaining cap rejects pending stage");
 }
#endif
 {
  const auto&f=fixtures[1];Settings s{"filled-development",f.id,0,2,2,8,20000,20000,1267058};Table filled(f,s,"static_filled");
  check(filled.setup_status==CA_OK&&filled.size()==s.cap,"static filled reaches distinct endpoint cap");
  check(filled.build_stats.group_ops+filled.fill_stats.reported_group_ops<=s.precomp_limit,"entire reported precomputation respects guard");
  std::set<U> exponents;for(U i=0;i<filled.size();i++){const auto e=filled.entry(i);check(exponents.insert(e.exp).second,"filled exact endpoints distinct");const auto q=element(f.c.mul(f.P,e.exp));check(hash_point(&filled.adapter.g,&q)==e.fp,"filled endpoint public witness");}
  Settings limited=s;limited.cell="partial-fill-development";limited.cap=static_cast<U>(f.r);limited.precomp_limit=500;Table partial(f,limited,"static_filled");
  check(partial.setup_status==CA_ERR_LIMIT&&partial.size()>0&&partial.size()<limited.cap,"fill watchdog retains partial known table");
  U digest=0;for(U i=0;i<partial.size();i++)digest^=entry_digest(partial.entry(i));check(digest==partial.state_hash,"partial setup hash is actual known state");
  check(partial.build_stats.group_ops+partial.fill_stats.reported_group_ops<=limited.precomp_limit,"partial fill total reported guard");
 }
 {
  const auto&f=fixtures[2];Settings s{"wide-filled-development",f.id,0,4,4,16,20000,20000,1267058};Table wide(f,s,"static_filled");
  check(wide.setup_status==CA_OK&&wide.size()==s.cap,"wide fixed fixture fills distinct endpoint cap");
  check(wide.build_stats.group_ops+wide.fill_stats.reported_group_ops<=s.precomp_limit,"wide fill reported guard");
  for(U i=0;i<wide.size();i++){const auto e=wide.entry(i);const auto d=element(f.c.mul(f.P,e.exp));check(hash_point(&wide.adapter.g,&d)==e.fp,"wide filled endpoint public witness");}
 }
 std::cout<<"{\"correctness_checks_passed\":"<<checks<<",\"scientific_cohort_run\":false,\"performance_collected\":false,\"upstream_commit\":"<<lab::json_quote(upstream)<<"}\n";return 0;
}
}
