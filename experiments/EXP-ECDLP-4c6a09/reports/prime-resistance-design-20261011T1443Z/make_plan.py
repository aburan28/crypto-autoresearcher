#!/usr/bin/env python3
"""Write a proposed protocol; never launch an ECDLP trial."""
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

REPO=Path('/workspace/solinas-run')
BASE=REPO/'experiments/EXP-ECDLP-4c6a09'
OUT=BASE/'reports/prime-resistance-design-20261011T1443Z'
PROPOSED_ID='EXP-ECDLP-5184f7'

def dump(p,x):
    with p.open('x') as f:json.dump(x,f,indent=2);f.write('\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    OUT.mkdir(exist_ok=False)
    (OUT/'inputs').mkdir()
    historical=BASE/'runs/RUN-ECDLP-24c35a/raw-result.json'
    cells=json.loads(historical.read_text())['cells']
    anchors={}
    for cell in cells:
        f=cell['field']
        if f['kind']=='solinas':
            anchors[(f['shape'],f['k'])]={key:f[key] for key in ['shape','k','p','p_bits','g']}
    identity=BASE/'reports/random-fields-20261011T0523Z/curve-identities.csv'
    shutil.copy2(identity,OUT/'inputs/historical-curve-identities.csv')
    provenance=[{'kind':'internal','path':str(p.relative_to(REPO)),'sha256':sha(p)} for p in [historical,identity,
        BASE/'runs/RUN-ECDLP-9e6cc1/plan.json',BASE/'reports/random-fields-20261011T0523Z/summary.json']]
    plan={
      'proposed_experiment_id':PROPOSED_ID,'related_experiment':'EXP-ECDLP-4c6a09','goal':'GOAL-ECDLP-001',
      'created_at_utc':datetime.now(timezone.utc).isoformat(),
      'status':'proposed_design_not_executed','official_ledger_registration':False,
      'authorization':'User: Devise a experiment with controls to measure this',
      'question':'Do curves over specified Solinas-style sparse primes require more ECDLP attack work than comparable curves over random primes?',
      'estimands':[
        {'id':'population','quantity':'Distribution of largest prime subgroup order, cofactor and obvious weak-curve flags on uniformly sampled nonsingular coefficient models','conditioning':'Prime size/magnitude only; no post-curve security screening'},
        {'id':'conditional_attack','quantity':'Verified attack group operations normalized by sqrt(ell)','conditioning':'Matched safe-screened ordinary curve subgroups with comparable ell; scope is the tested attacks'},
        {'id':'arithmetic','quantity':'CPU time per identical field or group operation workload','conditioning':'Same operand sizes and workload; common generic reduction then specialized sparse reduction on identical inputs'}],
      'main_prime_sample':{
        'bit_lengths':[24,28,32],'sparse_primes_per_bit_length':12,'blocks':36,
        'sparse_catalog':'Distinct prime integers p=2^b-2^a+s*2^c+t, 1<=c<a<=b-2, s,t in {-1,+1}; deduplicate integer values and keep all representations',
        'definition':'Specified four-term Solinas-style binary ensemble; distinct from the exact NIST polynomial families',
        'catalog_verification':'Complete finite enumeration and exact PARI isprime before selection; insufficient catalog is an input-preparation impediment, not permission to change the family',
        'sampling':'Uniform without replacement from the verified integer catalog; 4 primes per RNG seed and bit length, global deduplication',
        'seeds':[2026101105,2026101106,2026101107],
        'arms':['S: sparse','R: locally matched random prime','C: locally matched random prime with the same residue modulo 12'],
        'control_rule':'Uniform odd-integer rejection sampling in [ceil(.99*pS),floor(1.01*pS)], intersected with the same bit length; exact isprime; never nextprime',
        'C_additional_rule':'Require pC mod 12 = pS mod 12; R has no residue restriction',
        'exclusion':'R and C lie outside the complete sparse catalog and all pinned anchor primes; every selected modulus globally unique',
        'candidate_cap_per_control':20000,'total_moduli':108,
        'selection_blindness':'Freeze moduli before any curve count or attack outcome; retain all tested prime candidates and rejections'},
      'exact_anchor_cohort':{
        'anchors':list(anchors.values()),'control_arms':'One R and one C per anchor under the same local rules',
        'audit_all_six_anchors':True,'attack_anchors_max_prime_bits':40,
        'attackable_anchor_count':4,'audit_only_anchor_count':2,'total_moduli':18,
        'inference':'Case studies reported individually, never pooled as 36 extra independent prime samples; broader sparse-family results do not establish the NIST families',
        'secondary_fixed_models':[{'A':-3,'B':3},{'A':7,'B':1}],
        'fixed_model_policy':'Order/structure diagnostic only; prior selection for rank gains is disclosed and excluded from primary statistics'},
      'curve_sampling':{
        'population_models_per_modulus':32,'matched_candidate_models_per_modulus':512,
        'distribution':'Uniform A,B in F_p, using rejection from a keyed SHA-256 byte stream; reject singular discriminant only for the population cohort',
        'same_stream_policy':'Shared deterministic block/curve seed stream, with each modulus using its own exact uniform rejection; identical integer coefficients are not asserted',
        'record_population':['A','B','j','N','factorization(N)','largest_prime_ell','largest_prime_multiplicity','cofactor','trace','trace^2-4p','quadratic_twist_order','factorization(twist_order)','anomalous_flag','supersingular_flag','j_special_flag','small_embedding_degree_flag'],
        'population_exclusions':'None beyond singularity; flagged curves are retained and their rates reported',
        'matched_screen':'Ordinary; N!=p; j not 0 or 1728; multiplicity of ell in N is 1; 16<=bit_length(ell)<=26; no k<=20 with p^k=1 mod ell',
        'security_note':'This is a defined obvious-weakness screen, not a certificate excluding every endomorphism or attack',
        'match_rule':'Enumerate all 512 candidates per modulus regardless of outcomes. Use outcome-blind deterministic maximum-cardinality, then minimum-cost bipartite matching S-R and S-C on abs(log(ellS/ellX)), requiring max(ellS,ellX)/min(ellS,ellX)<=1.10. Break ties by candidate indices. Select first 8 common S rows by candidate index among eligible match intersections; no curve reused within a contrast',
        'matched_curve_pairs_per_block_per_contrast_max':8,
        'matching_shortfall':'Retain unmatched curves and empty blocks, never redraw a prime; report actual coverage and require at least 8 nonempty prime blocks per size stratum for a stratum estimate',
        'projection':'h=N/ell; G=h*P from deterministic seeded public points, require G!=O and ell*G=O; all identities and seeds recorded'},
      'targets_and_attacks':{
        'targets_per_group':4,'walk_seeds_per_target':[1,2,3,4],
        'target_generation':'Independent uniform q in [1,ell-1] from frozen domain-separated RNG; Q=qG; identical draw-index/seed policy on paired groups',
        'truth_policy':'q stored in validation-only file; attack receives p,A,B,ell,h,G,Q and its public algorithm seed, never q',
        'primary':'Pollard rho 16-adding walk with SHA-256 partition and Brent cycle detection; constants and restart policy fixed before any performance measurement',
        'walk_precompute':'T_i=a_iG+b_iQ for 16 seeded uniform coefficient pairs; setup counted separately and in total-work secondary metric',
        'partition':'SHA-256(walk_seed || canonical_compressed_point) mod 16; generic reducer common to S/R/C',
        'collision':'P=aG+bQ, Pprime=aprimeG+bprimeQ; solve q=(a-aprime)/(bprime-b) mod ell only when denominator nonzero; verify qG=Q; zero denominator restarts within the same work cap',
        'operation_cap':'20*ceil(sqrt(ell)) group calls after precomputation, shared across all restarts; censored searches retained',
        'secondary':'BSGS with M=min(4096,ceil(sqrt(ell))) stored points, identical declared memory cap and public verification; deterministic query cap ceil(ell/M)+1 guarantees coverage for correctly implemented valid groups',
        'verification':'Every reported scalar checked independently against Q and separately against synthetic truth',
        'maximum_main_rho_attempts':36*3*8*4*4,
        'maximum_main_BSGS_attempts':36*3*8*4,
        'setup_policy':'Point/cardinality discovery and target generation are preparation costs, reported separately; table/walk setup measured separately and in end-to-end work'},
      'controls':[
        {'id':'CTRL-R','purpose':'Random-prime baseline with matched prime size and magnitude'},
        {'id':'CTRL-C','purpose':'Same p mod 12 control distinguishes simple congruence mediation from a residual sparse-form effect; does not replace R total contrast'},
        {'id':'CTRL-ELL','purpose':'Order matching and sqrt(ell) normalization remove the leading generic subgroup-size effect'},
        {'id':'CTRL-SHAM','purpose':'Same exact curve/group/targets, two permuted family labels and identical seeds must give exactly identical answers and operation counts'},
        {'id':'CTRL-ISO','purpose':"Scaling isomorphism A'=u^4 A, B'=u^6 B, (x',y')=(u^2 x,u^3 y); transport G,Q. Same transported point hashing must reproduce walk traces and counts; native coordinate hashing diagnoses representation-dependent walk effects"},
        {'id':'CTRL-ORACLE','purpose':'Coordinate-blind opaque labels over the same group, with internal labels hidden from the solver; test generic walk behavior without exposing prime representation or target truth'},
        {'id':'CTRL-WALK','purpose':'Repeat rho with independent keyed partitions; predeclared replication uses a 32-adding walk on all main matched groups, not a selected winning subset'},
        {'id':'CTRL-BSGS','purpose':'Known-scalar generic control with fixed memory cap; distinguishes rho walk problems from broader attack-cost observations'},
        {'id':'CTRL-EASY','purpose':'At preparation, one deliberately small-prime subgroup (ell in {5,7,11,13}) for each bit-size stratum; instrument must solve correctly and register lower raw work; normalized asymptotics not applied to these tiny groups'},
        {'id':'CTRL-TIME','purpose':'Frozen ABBA/randomized order, CPU affinity, no concurrent timing jobs, five batches per workload; report CPU/wall separately'},
        {'id':'CTRL-REDUCE','purpose':'Generic reducer for both families first; then specialized reduction on S and generic reduction on the identical S instances; exact outputs must agree'},
        {'id':'CTRL-REPLAY','purpose':'Repeat fixed source/seed operation-count records byte-identically after removing measured timing fields'}],
      'control_sampling':{
        'sham_and_iso':'First 2 eligible S groups per bit stratum; no selection on runtime',
        'opaque_oracle':'All main matched groups and target/walk-seed combinations',
        'replication_walk':'All main matched groups, one additional 32-adding walk with seeds [101,102,103,104] on the same targets; precompute boundary identical',
        'easy_curve_search':'First qualifying candidate within the recorded 512-model pool; missing easy control prevents instrument pass for that stratum, not a mathematical conclusion'},
      'arithmetic_panel':{
        'moduli':'All main and anchor moduli; optional deployed public NIST primes are explicitly a separate arithmetic-only extension, not part of this frozen sample',
        'workloads':['65536 seeded field products/reductions','16384 nonzero field inversions','4096 fixed-count group additions on public points'],
        'repetitions':5,'sequential_timing':True,
        'backends':['Same generic big-integer reducer for every modulus','Validated specialized sparse reducer on the same S operands'],
        'claim_boundary':'Changes in time per operation are implementation observations; faster or slower arithmetic is not extra mathematical ECDLP hardness'},
      'metrics':{
        'population':['log2(ell)/2 generic-security proxy','cofactor distribution','fraction of obviously flagged curves','twist-order features'],
        'primary_attack':'U=min(search_group_calls/sqrt(ell),20*ceil(sqrt(ell))/sqrt(ell)); mark solved/censored explicitly',
        'primary_summary':'Restricted mean normalized search work, computed over all target/walk seeds including right-censored runs at the declared cap; paired geometric mean ratio S/R and S/C over curves, with equal weight per prime block',
        'secondary_attack':['Verified recovery fraction at cap','total group calls including precompute','field multiplication and inversion counts','CPU and wall seconds','actual stored points/bytes and peak RSS'],
        'BSGS_normalization':'W/(M+ell/(2M)); report raw W and M as well',
        'no_inflation':'Targets, walk seeds and curve samples nested under prime blocks are not independent primes'},
      'analysis':{
        'freeze':'All sources, samples, matching features, caps and tests fixed before attack measurement; split generic/optimized reduction phases',
        'labels':'Attack implementation uses no explicit family branch in generic phase; analyst initially receives opaque arm labels, revealed only after matching and raw verification freeze',
        'primary_contrast':'S versus R; S versus C is a prespecified mechanistic secondary contrast',
        'uncertainty':'10000 paired bootstrap replicates resampling whole prime blocks within each bit-size stratum, retaining all nested rows; 99 percent confidence interval. Finite sampled ensemble, not uniform all-prime inference',
        'practical_margin':0.20,
        'increased_tested_cost':'99 percent lower confidence limit for S/R exceeds 1.20 overall, with same direction in at least two of three size strata, no instrument failures, and no effect attributable to setup, subgroup size, timing/backend or coordinate-hash controls',
        'equivalence':'99 percent confidence interval entirely within [1/1.20,1.20] => tested normalized costs practically similar in sampled scope',
        'inconclusive':'Interval crossing either decision boundary, too few prime blocks, or control failure; failure to reject equality alone is not equivalence',
        'censoring':'Restricted-mean cost is the primary estimand at the preset work cap. If either arm has >5 percent censorship, report cap-limited inference and do not claim unrestricted mean cost; preserve every failure and censor separately',
        'population_claim':'Larger typical ell or fewer flags means this generation ensemble gives different curve properties; conditional subgroup hardness is a separate question',
        'resistance_claim':'Higher rho cost is attack-specific. Generic prime-order groups of equal order are abstractly isomorphic; generic attacks cannot certify an intrinsic prime-family hardness separation. A broader resistance claim requires a validated structure-aware shortcut on random-prime curves that the sparse cases avoid, plus independent reproduction'},
      'resources_and_stops':{
        'max_concurrent_preparation_workers':2,'max_concurrent_timing_workers':1,
        'memory_per_worker_bytes':4294967296,'overall_memory_headroom_bytes':8589934592,
        'process_watchdog_seconds':600,'campaign_budget_maximum_batches':None,'campaign_total_wall_seconds':None,
        'watchdog_meaning':'Machine protection only; a stopped process is an implementation/resource observation, not higher hardness',
        'sample_stopping':'Fixed catalog and control candidate caps, fixed 512-curve pools and eight matched rows per block; fixed target/seed counts; no outcome-based extra primes or target selection'},
      'artifacts_and_readiness':{
        'required':['Frozen protocol and source hashes','prime candidate and rejection traces','all population curves and matching matrices','full EC1 curve/field/subgroup/G identities','public targets and separate validation truth','per-attempt counters/collisions/restarts/censor status','timing environment and raw logs','clustered analysis with intervals','editable figures and inspected PDF'],
        'curve_identity':'tools/curve_identity.py, exact field definition, A/B, subgroup order/cofactor and generator; different primes imply different curves even for the same rational coefficients',
        'launcher_state':'Design only: the rho/oracle/timing integration and blinded sample builder have not been implemented or run',
        'registration_policy':'No official experiment approval or research-state change made; register/approve only after implementation, correctness controls and repository readiness/capacity checks',
        'review':'Any claim of increased resistance or a contradiction of established evidence requires independent review; none has been obtained in this design session'},
      'prior_evidence':provenance,
      'known_bounds':{
        'dominated_by':'Declared generic Pollard rho and memory-accounted BSGS are always retained as attack baselines; the proposed study asserts no new algorithm',
        'sota_delta':'Not measured; planned paired primitive-count and runtime ratios only, no sealed frontier bound or asymptotic improvement'}
    }
    dump(OUT/'plan.json',plan)
    dump(OUT/'design-provenance.json',{'sources':provenance,'historical_anchors':list(anchors.values()),
                                     'design_only':True,'new_ECDLP_results':None})
    shutil.copy2(Path(__file__),OUT/'make_plan.py')
    shutil.copy2('/usr/share/common-licenses/GPL-2',OUT/'GPL-2.txt')
    print(OUT,flush=True)

if __name__=='__main__':main()
