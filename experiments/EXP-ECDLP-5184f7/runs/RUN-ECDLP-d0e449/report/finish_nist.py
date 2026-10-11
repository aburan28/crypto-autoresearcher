"""Derived communication, exact endpoint checks and curve identity export."""
import csv, datetime, hashlib, importlib.metadata, json, math, shutil, sys
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

RUN=Path(sys.argv[1]).resolve();sys.path.insert(0,str(RUN/'source'))
from common import write,sha
from curve_identity import curve_identity
from finite_math import Curve


def show(result):
    if result.get('CI99_9')is None:return 'unavailable'
    lo,hi=result['CI99_9'];return f"{result['estimate']:.4f} [{lo:.4f}, {hi:.4f}]"


def main():
    out=RUN/'report';out.mkdir(exist_ok=False);load=lambda p:json.loads((RUN/p).read_text())
    summary=load('analysis/summary.json');manifest=load('manifest.json');nf=load('theory/number-fields.json')['records'];groups=load('preparation/public-groups.json')
    gm={g['group_id']:g for g in groups};jobs={j['job_id']:j for j in load('attacks/job-index.json')};targets={t['id']:t for t in load('preparation/public-targets.json')}
    maps=load('attacks/isomorphism-maps.json');mapped={r['source_identity']['curve_uid']:r for r in maps}
    actual=[];checked=0;large_caps=0
    for p in sorted((RUN/'attacks').glob('chunk-*/public-jobs.txt')):
        raw={r['job_id']:r for r in map(json.loads,(p.parent/'raw-results.jsonl').read_text().splitlines())}
        for line in p.read_text().splitlines():
            fs=line.split();jid,mode,adding,seed=fs[:4]
            if mode not in ['native_iso','transport']:continue
            pp,A,B,ell,h,gx,gy,qx,qy,u,cap=map(int,fs[4:]);j=jobs[jid];g=gm[j['group_id']];t=targets[j['target_id']]
            assert A==g['A']*pow(u,4,pp)%pp and B==g['B']*pow(u,6,pp)%pp
            assert [gx,gy]==[g['G'][0]*pow(u,2,pp)%pp,g['G'][1]*pow(u,3,pp)%pp]
            assert [qx,qy]==[t['Q'][0]*pow(u,2,pp)%pp,t['Q'][1]*pow(u,3,pp)%pp]
            ec=Curve(pp,A,B);assert ec.on_curve((gx,gy))and ec.on_curve((qx,qy))and ec.mul((gx,gy),ell)is None
            if raw[jid]['scalar']is not None:assert ec.mul((gx,gy),raw[jid]['scalar'])==(qx,qy)
            else:assert raw[jid]['censored'];large_caps+=1
            checked+=1
    for m in maps:
        original=next(g for g in groups if g['identity']['curve_uid']==m['source_identity']['curve_uid'])
        actual.append({'group_id':original['group_id']+'-iso','case':original['case'],'purpose':'degree-1 isomorphic endpoint control','field':m['field'],'curve':m['curve'],'identity':m['destination_identity']})
    identities=[{'group_id':g['group_id'],'case':g['case'],'purpose':g['kind'],'field':g['field'],'curve':g['curve'],'identity':g['identity']}for g in groups]
    identities.extend(actual)
    identities.extend({'group_id':'arithmetic-'+r['modulus_id'],'case':r['modulus_id'].split('-')[0]+'-'+r['modulus_id'].split('-')[1],'purpose':'arithmetic full group; seed order unresolved',**r}for r in load('arithmetic/curve-identities.json'))
    for r in identities:
        # Identity namespace is explicit; the arithmetic seed's order is unresolved.
        tag='nistisomorphism'if r['purpose']=='degree-1 isomorphic endpoint control'else 'nistarithmetic'if r['purpose'].startswith('arithmetic')else'niststandard'if r['purpose']=='standard-anchor'else'nistcomparison'
        assert curve_identity(r['field'],r['curve'],tag)==r['identity']
    write(out/'full-curve-identities.json',identities)
    cols=['purpose','case','group_id','curve_id','curve_uid','p','A','B','subgroup_order','cofactor','generator_JSON']
    with (out/'all-curve-identities.csv').open('x',newline='')as f:
        w=csv.DictWriter(f,fieldnames=cols,lineterminator='\n');w.writeheader()
        for r in identities:w.writerow({'purpose':r['purpose'],'case':r['case'],'group_id':r['group_id'],**{k:r['identity'][k]for k in ['curve_id','curve_uid']},
             'p':r['field']['characteristic'],'A':r['curve']['a4'],'B':r['curve']['a6'],'subgroup_order':r['curve']['subgroup_order'],'cofactor':r['curve']['cofactor'],'generator_JSON':json.dumps(r['curve']['generator'],separators=(',',':'))})
    write(out/'derived-checks.json',{'actual_isomorphic_endpoint_jobs_checked':checked,'censored_large_transport_jobs':large_caps,'all_actual_endpoint_checks_pass':True,'identity_rows':len(identities),
          'canonical_graph_change':'None: no mechanism, sealed bound, paired challenge verdict or promoted claim in this observational run',
          'graphs_checked':['Historical Solinas reports and workflow figures','New primary-ratio and fixed-field workflow figures','knowledge/frontiers/ecdlp tree inventory'],
          'independent_scientific_review_obtained':False})
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'svg.fonttype':'none','svg.hashsalt':RUN.name})
    old=RUN.parent/'RUN-ECDLP-07aad1/analysis/summary.json';solinas=json.loads(old.read_text())['primary_result']
    primary=[('Solinas catalog: 72 distinct toy primes',solinas)]
    for case in ['P-192','P-224']:primary.append((case+': one fixed full-size field',summary['cases'][case]['primary']))
    fig,ax=plt.subplots(figsize=(8.3,3.2));ax.axvspan(1/1.2,1.2,color='#e9f1eb');ax.axvline(1,color='#777777',linestyle='--')
    for y,(label,r)in enumerate(primary):
        lo,hi=r['CI99_9'];ax.errorbar(r['estimate'],y,xerr=[[r['estimate']-lo],[hi-r['estimate']]],fmt='o',capsize=4,color='#145b73')
        ax.text(max(x[1]['CI99_9'][1]for x in primary)+.015,y,show(r),va='center',fontsize=8)
    ax.set(yticks=range(3),yticklabels=[p[0]for p in primary],xlabel='S / random-control rho search calls divided by sqrt(subgroup order)',
        xlim=(min(.8,min(x[1]['CI99_9'][0]for x in primary)-.025),max(1.24,max(x[1]['CI99_9'][1]for x in primary)+.31)))
    ax.invert_yaxis();ax.grid(axis='x',alpha=.2);fig.suptitle('Completed small-subgroup attacks: marginal 99.9% intervals')
    fig.text(.5,.015,'Solinas: 24–36-bit fields, 16–28-bit subgroups. P-192/P-224: full fields, 16–20-bit subgroups. Different scopes.',ha='center',fontsize=7)
    fig.tight_layout(rect=(0,.05,1,.96));fig.savefig(out/'primary-comparison.svg');plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(8.3,4.0),sharex=True)
    for ax,case in zip(axes,['P-192','P-224']):
        labels=[];results=[]
        for mode,name in [('rho','Native 16'),('oracle','Opaque 16'),('rho32','Native 32')]:
            for arm in ['R','C']:labels.append(name+'/'+arm);results.append(summary['cases'][case]['attack_comparisons'][mode+'_S_'+arm])
        for y,r in enumerate(results):
            lo,hi=r['CI99_9'];ax.errorbar(r['estimate'],y,xerr=[[r['estimate']-lo],[hi-r['estimate']]],fmt='o',capsize=3,color='#145b73')
        ax.axvline(1,color='#777777',linestyle='--');ax.axvspan(1/1.2,1.2,color='#e9f1eb');ax.set(yticks=range(len(labels)),yticklabels=labels,title=case,xlabel='Normalized rho work ratio, S/control');ax.invert_yaxis();ax.grid(axis='x',alpha=.2)
    fig.suptitle('Frozen matched control-field bootstrap · 500,000 replicates · 99.9% marginal intervals')
    fig.tight_layout(rect=(0,.04,1,.95));fig.savefig(out/'attack-ratios.svg');plt.close(fig)
    fig,ax=plt.subplots(figsize=(8.3,2.6));ax.axis('off')
    boxes=[(.16,.70,'Exact standard prime\n512 uniform curve models'),(.16,.29,'144 random fields R\n144 residue-matched fields C\n4 uniform models per field'),(.52,.49,'Exact curve orders\nOrdinary, verified small factors\nMatch subgroup orders ≤10%'),(.85,.49,'4 targets × 4 rho seeds\nNative / opaque / 32-adding\nComplete BSGS checks')]
    for x,y,text in boxes:ax.text(x,y,text,ha='center',va='center',fontsize=8,bbox={'boxstyle':'round,pad=.5','facecolor':'#e9f1f5','edgecolor':'#145b73'})
    for xy,xytext in [((.39,.57),(.32,.70)),((.39,.40),(.32,.29)),((.72,.49),(.65,.49))]:ax.annotate('',xy=xy,xytext=xytext,arrowprops={'arrowstyle':'->','color':'#145b73'})
    ax.text(.5,.04,'Separate large-prime subgroups: one target, 4,096-call cap → bounded recovery only; full ECDLP remains unresolved.',ha='center',fontsize=8)
    fig.tight_layout();fig.savefig(out/'workflow.svg');plt.close(fig)
    fig,ax=plt.subplots(figsize=(8.3,3.0));ax.axis('off')
    boxes=[(.15,.78,'Integer ring O_K\nPolynomial relation for theta\nUnit rank 1 (P-192) or 3 (P-224)'),(.53,.78,'Principal ideal P=(a-theta)\nNorm(a-theta)=f(a)=p'),(.87,.78,'Residue field F_p\ntheta maps to a'),(.15,.30,'E(K): points before reduction\nMordell-Weil rank unmeasured'),(.53,.30,'E(F_p): finite points\nFree integer rank zero'),(.87,.30,'Prime-order subgroup\nQ=[x]G; x unknown')]
    for x,y,text in boxes:ax.text(x,y,text,ha='center',va='center',fontsize=7.8,bbox={'boxstyle':'round,pad=.5','facecolor':'#e9f1f5'if y>.5 else'#f0eee6','edgecolor':'#145b73'})
    for xy,xytext in [((.39,.78),(.31,.78)),((.76,.78),(.69,.78)),((.39,.30),(.31,.30)),((.76,.30),(.69,.30))]:ax.annotate('',xy=xy,xytext=xytext,arrowprops={'arrowstyle':'->','color':'#145b73'})
    ax.text(.34,.11,'Good reduction; global image coverage unmeasured',ha='center',fontsize=7.8)
    ax.text(.80,.11,'Efficient scalar recovery still needed',ha='center',fontsize=7.8)
    ax.set_title('Coordinate reduction and elliptic scalar relations are separate',fontsize=10)
    fig.tight_layout();fig.savefig(out/'field-structure.svg');plt.close(fig)
    counts=summary['counts'];control=summary['integrity_controls'];anchor=load('preparation/standard-anchors.json')
    primary_table='\n'.join(f"| {case} | {show(summary['cases'][case]['primary'])} | {summary['cases'][case]['primary']['matched_pairs']} | {summary['cases'][case]['primary']['control_fields']} |"for case in ['P-192','P-224'])
    detail='\n'.join(f"| {case} | {name} | {show(r)} |"for case in ['P-192','P-224']for name,r in summary['cases'][case]['attack_comparisons'].items()if not name.endswith('search_wall'))
    bounded_table='\n'.join(f"| {case} | {arm} | {r['successes']}/{r['n']} | {r['CI99_9'][1]:.4f} |"for case in ['P-192','P-224']for arm,r in summary['bounded_large_subgroups'][case].items()if arm!='standard_anchor'and r['n'])
    arithmetic_table='\n'.join(f"| {case} | {work} | {show(r['S_R'])} | {r['S_Python_fold_over_builtin_ratio']:.4f} |"for case in ['P-192','P-224']for work,r in summary['arithmetic'][case].items())
    population_table='\n'.join(f"| {case} | {endpoint} | {show(r['difference_S_minus_control'])} |"for case in ['P-192','P-224']for endpoint,r in summary['population'][case]['R'].items()if 'difference_S_minus_control'in r)
    nf_table='\n'.join(f"| {r['case']} | {r['polynomial']} | {r['degree']} | {r['signature']} | {r['unit_rank_by_Dirichlet']} | {r['field_discriminant']} |"for r in nf)
    md=f'''# P-192 and P-224 full-field comparison — 2026-10-11

Measured observations from EXP-ECDLP-5184f7 / {RUN.name}. All {summary['attack_jobs']:,} scheduled jobs completed. These two exact primes were confirmed by the user; they are separate fixed-prime studies, not new independently sampled Solinas prime families.

| Fixed prime | Native rho S/R ratio [99.9% CI] | Matched pairs | Independent matched R fields |
| --- | --- | --- | --- |
{primary_table}

{chr(10).join(case+': '+summary['cases'][case]['decision']+'.'for case in ['P-192','P-224'])}

The decisive scope limit is the subgroup: the complete attacks use **16–20-bit prime-order subgroups inside the full 192/224-bit fields**. They do not solve the full cryptographic subgroup and do not establish that P-192 or P-224 is safer or weaker than random-field cryptography. Separate large-subgroup walks are censored at 4,096 search calls.

![Primary comparisons](primary-comparison.svg)

## Frozen design and controls

Source, sampling, stopping and analysis froze at {manifest['source_commit']} before scientific selection. Each fixed prime has 512 uniform nonsingular curve models. Each case has 144 globally distinct size-matched random fields (R) and 144 size-and-mod-12-matched random fields (C), four curve models per control field. Total: **{counts['random_control_fields']} random fields, two fixed fields, {counts['uniform_models']:,} unconditional main models**. Each fixed S prime has 288 random controls, compared with four controls per S prime in the wider Solinas study, and 512 unconditional S models rather than 128. Across these two cases there are 576 random fields; it has fewer total models because full-size point counting is much more expensive. No prior observations are pooled.

Uniform rejection draws and exact PARI primality decisions are retained. Curve orders are exact PARI ellcard outputs with Hasse checks. Partial factorization uses primes below 2^20 and records exact primality flags for the remaining cofactor; unresolved composite cofactors are not treated as prime or as complete factorization. Small attack subgroups require ordinary curves, nonspecial j, N≠p, multiplicity one, and no embedding degree ≤20. Matching maximizes cardinality, then minimizes log-order distance, with ≤10% subgroup-order mismatch. A curve is used once per contrast; shared S identities across R/C are retained.

Four independently generated public synthetic targets and four solver seeds per curve drive each rho variant. The solver receives points, order, seed and cap, not synthetic scalar truth or prime-family tags. Native rho16, opaque rho16, independent native rho32 and complete BSGS are compared. The opaque interface limits this fixed solver's coordinate access; it is not a formal adversarial oracle or a security proof. Setup, search and verification are recorded separately. Native/opaque work is restricted search calls/sqrt(ell), capped at 20. BSGS uses setup+search divided by M+ell/(2M), with M≤4096. Its memory counts include allocated table nodes, buckets, container object and stored coordinate heap limbs, excluding allocator metadata and other process state.

![Workflow](workflow.svg)

## Higher confidence without counting dependent observations twice

The primary estimate is the exponentiated mean paired log ratio, with equal weight to each matched control field. All pairs, targets and solver seeds in that field stay together in **500,000 whole-field bootstrap replicates**. The matching is fixed, not rerun. Approximate marginal 99.9% intervals and reserved three-family Bonferroni 99.9667% intervals are in analysis/summary.json. The latter reserve approximate joint 99.9% primary coverage for the prior wider Solinas test and these two cases; other diagnostics have marginal coverage only. The frozen practical-similarity band is [1/1.2,1.2], with at least 25 matched R fields and 50 pairs required for a decision.

{chr(10).join(case+': reserved primary interval ['+', '.join(f'{v:.6f}'for v in summary['cases'][case]['primary']['CI99_9667_reserved_three_primary_tests'])+'].'for case in ['P-192','P-224'])}

Curve-population binary rates use all 512 independent S curve draws and the first uniform curve per independent control field for conservative binomial intervals. Both 99.95% rate intervals produce a conservative ≥99.9% difference interval under the sampling model. Every other control curve remains in descriptive counts. Trace comparisons use all four models per field with clustering. Fixed-seed pseudorandomness and an enormous prime pool sampled without replacement are the experimental random-sampling approximation.

## Attack diagnostics and integrity

| Case | Contrast | Ratio [marginal 99.9% CI] |
| --- | --- | --- |
{detail}

![Rho variants](attack-ratios.svg)

All {control['exact_control_checks']} sham/replay/inverse-transport equality checks passed. All returned synthetic scalars and collision equations passed the external arithmetic checks. {control['BSGS_exact_accounting_jobs']} BSGS jobs match setup=M+popcount(M)+bit_length(M)−1 and search=floor(scalar/M). Main small-subgroup rho censors: {summary['small_main_rho_censors']}. {checked} actual isomorphic endpoint jobs were checked in this derived report, including {large_caps} censored large-transport jobs. The two tiny-subgroup BSGS positive controls complete if present; finite-cap tiny rho censors are valid censored observations.

Full EC1 aliases/UIDs, fields, models, subgroup orders, cofactors and generators are in all-curve-identities.csv and full-curve-identities.json ({len(identities)} rows). Arithmetic identities describe the full finite group and explicitly mark their seed's point order unresolved; that point is not falsely asserted to generate the whole group.

## Large subgroups: the experiment cannot infer full security

| Case | Arm | Recovered targets / specified trials | Exact-model 99.9% upper recovery probability |
| --- | --- | --- | --- |
{bounded_table}

These bounds concern the selected synthetic challenge distribution and this **4,096-search-call** solver only. They are not lower bounds on every algorithm, not an ECDLP-bit estimate, and not evidence of extra resistance. The standard NIST coefficient/order/generator anchors also have one capped target each; they are anchors, not a repeated-curve population. Their exact primality, nG=O and curve order were checked by PARI and the public arithmetic instrument. Constants are recalled public NIST parameters; internal arithmetic verification supplies the measured mathematical identity, not an external standards-document citation.

## Curve order and arithmetic

| Case | Unconditional endpoint | S−R probability difference [conservative ≥99.9% interval] |
| --- | --- | --- |
{population_table}

These rates describe order primality and certified factors in sampled curves. A small factor of N does not make a separate large prime-order subgroup weak. Partial factorization does not establish the full curve's largest prime factor when its residual is composite. All R/C rates, raw hit counts and trace intervals are retained in analysis/summary.json.

| Case | Full-field operation | Python builtin S/R timing ratio [99.9% conditional interval] | S fold/builtin timing ratio |
| --- | --- | --- | --- |
{arithmetic_table}

All {summary['arithmetic_integrity']['observations']} arithmetic observations have exactly equal reference outputs. Timing intervals resample control fields conditional on the single S five-batch median, excluding S systematic timing error. Fold/builtin ratios are descriptive prototype measurements on one fixed field; no prime-population interval is claimed. Both inversion paths use identical Python pow. The P-192 inversion rows nevertheless have a 5.61× fold-label/builtin-label median ratio; this timing variation has an unmeasured cause and is recorded in arithmetic/timing-observation.json. It is not an algorithmic difference. No observations were discarded or repeated. Primary group-call results do not use these timings. These are not optimized native or assembly comparisons and are not ECDLP-security measurements.

## Theory in plain language

1. **A special prime changes coordinate arithmetic.** With P-192, 2^192 ≡ 2^64+1 (mod p). With P-224, 2^224 ≡ 2^96−1 (mod p). These identities replace high bits with shifts and additions/subtractions during modular reduction. That can speed up point arithmetic for honest users and attackers alike. It does not itself tell us the hidden scalar in Q=[x]G.
2. **The elliptic-curve subgroup determines generic collision work.** A prime-order subgroup of size ell is cyclic; generic rho typically needs work proportional to sqrt(ell). Matching ell and dividing work by sqrt(ell) lets this study ask whether the implemented walk behaves differently because of the field. For the actual standard subgroup orders the generic scale is roughly 2^96 and 2^112 operations, vastly above a 4,096-call walk. These are generic-model scales, not certified universal attack lower bounds.
3. **Rank has two different meanings here.** E(F_p) is finite, so its free integer rank is zero; a prime-order subgroup needs one generator. Mordell-Weil rank over a number field counts independent infinite-order points before reduction. A larger number-field rank may supply more candidate reduced points, but those points land in the same finite cyclic subgroup. It does not reveal their discrete logs or create independent finite-group dimensions.
4. **A lift still needs useful relations.** For f(2^k)=p, a suitable number-field prime ideal can reduce lifted points to F_p. A homomorphic reduction preserves group addition. A practical attack would additionally need cheap target lifts, broad point coverage, enough independent scalar relations, and cheaper end-to-end solving than rho. This run does not measure that number-field machinery, relation rank or asymptotic advantage; earlier archived number-field reports remain separate.
5. **An abstract isomorphism is not an efficient attack.** Two prime-order cyclic groups are abstractly isomorphic. Computing the needed coordinate/scalar correspondence can itself require solving the discrete log. This study's explicit coordinate isomorphism controls have known degree-one maps and inverse encodings; arbitrary unrelated curves do not acquire those maps from having a similarly shaped field prime.

## The chosen number-field lifts: exact algebra, separate from curve rank

| Prime | Polynomial f(t) | Field degree | Signature (real, complex pairs) | Unit rank | Lift-field discriminant |
| --- | --- | --- | --- | --- | --- |
{nf_table}

Many number fields can have F_p as a residue field. These two lifts are selected because their low-coefficient polynomials reproduce the standard primes; their degree and unit rank describe the selected lifts. A curve-specific calculation is needed to determine elliptic endomorphisms. These are exact derived invariants, not sample estimates and not elliptic-curve Mordell-Weil ranks. The chosen lift-field discriminants are separate from any sampled curve's Frobenius or endomorphism-field discriminant, whose full ring/conductor audit remains unresolved. PARI certifies irreducibility, signatures, field discriminants and index one in theory/number-fields.json with raw GP source/output alongside. P-192 evaluates f at 2^64; P-224 at 2^32. Each evaluation equals the stated prime. The monic polynomial also gives the exact norm identity Norm(a−theta)=f(a)=p. Thus the ideal (a−theta) is principal and prime, with norm p. It equals (p,theta−a) in the recorded integer basis. Since p does not divide the field discriminant, this degree-one ideal is unramified, and the ring-of-integers quotient is F_p. The derivation is retained in theory/principal-ideal-derivation.json.

![Coordinate and point structures](field-structure.svg) This is a reduction of integral/local coordinates; it is not a field homomorphism from the characteristic-zero field K to F_p.

The rank of O_K's multiplicative unit group is r1+r2−1 by Dirichlet's theorem, hence 1 and 3. Elliptic-curve rank concerns E(K) under point addition and remains unmeasured here. Scalar-relation matrix rank over the subgroup field is a further distinct quantity. Any link from unit rank to useful elliptic scalar relations still needs an explicit algorithm and measured end-to-end costs. Simply scaling coordinates by a unit sends E(A,B) to E(u^4 A,u^6 B), preserving the hidden scalar under the known isomorphism. For nonspecial j, this is generally a different curve model; it supplies no additional independent scalar equation by itself.

## Provenance, failures and limits

All evidence here is internal measured or derived evidence tied to {RUN.name}, manifest.json, the frozen contract, preparation/attacks/arithmetic raw outputs and analysis/summary.json. Prior Solinas reference: RUN-ECDLP-07aad1, kept separate. Source and kernel hashes, exact commands, dependency versions and resource limits are in manifest.json; actual phase exits/timings are in execution-result.json. Engineering failures and corrections are retained: missing Boost headers, the old instrument's 26-bit subgroup guard, and an overstrict tiny-rho recovery assertion. The initial instrument issues occurred before scientific sampling and are not negative mathematical evidence. During preparation, the absent optional SEA tables were supplied after exact parity verification of four completed P-224 order/factor/primality records. The fixed Debian data package, original GP hash, wrapper and application time are in engineering/seadata-*.json. Completed measurements stay unchanged; remaining GP launches load the data. Preparation timings mix these data setups and are not causal field-hardness measurements. The primary attack kernel and frozen sampling/analysis code stay unchanged.

There is no independent scientific review, sealed bound, asymptotic result, complete general endomorphism-ring audit or official research-state promotion. Canonical knowledge/frontiers/ecdlp and historical report/graph inventories were checked; no supported frontier or mechanism changes, so those immutable graphs remain as archived. Only this run's explanatory workflow and comparison figures are added. A higher confidence level widens intervals at a fixed sample size; it does not eliminate bias or extend the tested subgroup scope. PR publication depends on working GitHub authentication.
'''
    (out/'report.md').write_text(md)
    escape=lambda s:s.replace('_','\\_').replace('#','\\#').replace('[','\\[').replace(']','\\]')
    def table(rows):return '#table(columns: (1.1fr, 2.0fr, 2.5fr), inset: 5pt, '+',\n'.join('['+escape(v)+']'for row in rows for v in row)+')'
    primary_rows=[('Case','S/R ratio; marginal 99.9% CI','Pairs / matched R fields')]+[(case,show(summary['cases'][case]['primary']),str(summary['cases'][case]['primary']['matched_pairs'])+' / '+str(summary['cases'][case]['primary']['control_fields']))for case in ['P-192','P-224']]
    bounded_rows=[('Case / arm','Recovered / trials','99.9% upper bounded-recovery probability')]+[(case+' / '+arm,f"{r['successes']} / {r['n']}",f"{r['CI99_9'][1]:.4f}")for case in ['P-192','P-224']for arm,r in summary['bounded_large_subgroups'][case].items()if arm!='standard_anchor'and r['n']]
    ty=f'''#set page(paper: "a4", margin: 17mm, footer: context [#align(center)[#counter(page).display()]])
#set text(font: "DejaVu Sans", size: 9.6pt)
#set par(justify: false, leading: .55em)
#set heading(numbering: none)
= P-192 and P-224: measured comparisons
{RUN.name} · EXP-ECDLP-5184f7 · 2026-10-11

All {summary['attack_jobs']:,} scheduled jobs completed, with {control['exact_control_checks']} exact integrity comparisons passing. The main result concerns 16–20-bit subgroups inside full 192/224-bit fields. The standard-size cryptographic ECDLP remains unresolved.

{table(primary_rows)}

{chr(10).join(escape(case+': '+summary['cases'][case]['decision']+'.')for case in ['P-192','P-224'])}

#image("primary-comparison.svg", width: 100%)

Sources: analysis/summary.json, preparation/matching.json and attacks raw-results.jsonl. The Solinas reference is RUN-ECDLP-07aad1, a separate toy-field study. Comparisons have different scopes; this figure does not rank deployed prime security.

There are {counts['random_control_fields']} independent random control fields, two fixed S primes and {counts['uniform_models']:,} unconditional main curve models. S has 512 models per prime; each of 288 random fields per case has four. R matches size; C additionally matches residue modulo 12. The frozen source commit is {manifest['source_commit'][:12]}.

#pagebreak()
= How to read the theory
P-192 is 2^192 − 2^64 − 1, so 2^192 is congruent to 2^64 + 1 modulo p. P-224 is 2^224 − 2^96 + 1, so 2^224 is congruent to 2^96 − 1 modulo p. These are coordinate-reduction identities: useful for arithmetic, and available to both honest users and attackers.

The hidden scalar problem is Q = [x]G. In a cyclic prime-order subgroup of size ell, generic rho collision work has scale sqrt(ell). Matching subgroup orders and normalizing calls by sqrt(ell) isolates this implemented walk's dependence on the field. It does not establish the performance of every structural attack.

Over a finite field, E(F_p) is a finite group and has free integer rank zero. A prime-order subgroup has one generator. Number-field Mordell-Weil rank instead counts independent infinite-order points before reduction. More lifted generators may yield more candidate points, but do not supply their hidden finite-group scalars.

Many number fields can have F_p as a residue field. The chosen lifts use t^3−t−1 at t=2^64 and t^7−t^3+1 at t=2^32; their ranks describe these particular lifts. Exact PARI field invariants give degrees 3 and 7, signatures (1,1) and (1,3), and unit ranks 1 and 3. These are multiplicative unit ranks, not elliptic ranks or endomorphism-field invariants. Norm(a−theta)=f(a)=p makes (a−theta) an explicit principal prime ideal. The ring-of-integers quotient at that degree-one ideal is F_p; there is no characteristic-zero-field homomorphism to F_p.

A number-field reduction can preserve point addition at good reduction. An attack would also need cheap target lifting, useful coverage and enough independent scalar relations to make the full workflow cheaper than rho. This run does not measure that number-field workflow; its earlier immutable evidence stays separate.

Abstractly isomorphic cyclic groups do not automatically have efficiently computable coordinate maps. The tested degree-one isomorphisms have explicit maps (x,y) to (u^2 x,u^3 y), with known inverse encodings.

#image("field-structure.svg", width: 100%)

#pagebreak()
= Controls and confidence
Only ordinary nonsingular models enter small-subgroup attacks. The selected factor has multiplicity one, 16–20 bits and no embedding degree at most 20; anomalous and special-j cases are excluded. Maximum-cardinality matching then minimizes log-order distance, with at most 10% mismatch. All selections freeze before attacks.

The solver gets only public points, subgroup order, seeds and cap. Synthetic scalar truth stays outside its input and is used afterward. Native rho16, opaque rho16, independent native rho32 and complete BSGS are retained. Setup and verification are separate from primary search.

#image("attack-ratios.svg", width: 100%)

The primary ratio weights each matched random control field equally. Whole-field bootstrap preserves every paired curve/target/seed in its cluster. 500,000 replicates yield approximate marginal 99.9% intervals. Matching is held fixed. Three-family 99.9667% primary intervals reserve approximate joint 99.9% coverage for the wider Solinas study and these two cases; diagnostics have marginal coverage only.

{chr(10).join(escape(case+' reserved primary interval: '+str(summary['cases'][case]['primary']['CI99_9667_reserved_three_primary_tests']))for case in ['P-192','P-224'])}

The similarity band is [1/1.2, 1.2], requiring at least 25 matched R fields and 50 pairs. This is a frozen practical comparison, not an exact equality test. All {control['BSGS_exact_accounting_jobs']} BSGS jobs match the exact setup/search accounting. {checked} actual transported endpoint jobs pass their point and subgroup checks. Complete curve identities are in all-curve-identities.csv.

#pagebreak()
= Large groups and remaining uncertainty
Large prime factors have at least 128 bits. One target and one rho seed stop at 4,096 search group calls. These walks cannot resolve the typical cryptographic subgroup. A null outcome is censored and inconclusive for full ECDLP resistance.

{table(bounded_rows)}

The upper probabilities describe the selected synthetic challenge distribution and this bounded solver only. They are not algorithm-independent security bounds. The exact standard coefficient/order/generator anchors have one capped target each and are not a repeated-curve population. Their primality, curve orders and nG=O were checked internally. Actual subgroup generic scales are roughly 2^96 and 2^112 operations, far above this run's caps.

Uniform curve-order audits retain exact orders, normalized traces, prime-order flags, certified small factors and residual primality flags. Factorization is partial; unresolved composite residuals are not prime or known largest factors. Binary population intervals use all S draws and one unconditional control curve per independent field, with conservative binomial-model 99.9% difference coverage; every other control row is retained descriptively. All-four-curve trace comparisons preserve field clusters.

The full-field arithmetic panel has {summary['arithmetic_integrity']['observations']} exact-output-equal observations. Its 99.9% timing intervals cover sampled control-field variation conditional on one fixed S median and exclude S systematic timing error. Python fold ratios are descriptive prototypes; both inversion paths use the same builtin pow. P-192 inversion labels nevertheless differ by 5.61× in their medians. This substantial timing variation has an unmeasured cause and is retained in arithmetic/timing-observation.json; it supplies no algorithmic or security claim. No samples were repeated or discarded. Primary group-call results use no timing observations. report.md and analysis/summary.json contain every ratio and interval. Optimized native/assembly arithmetic is untested.

Sources, seeds, exact commands, versions and code hashes: manifest.json and contract.json. Actual phase outcomes: execution-result.json. All raw outputs are retained, including excluded engineering failures and corrections. During preparation, missing SEA data were installed after four completed order/factor/primality outputs matched exactly. That runtime amendment is retained; preparation times mix data setups and are not security comparisons. No independent scientific review, sealed bound, asymptotic result or official claim promotion was obtained. Historical/canonical graphs remain as archived because their supported content does not change.
'''
    (out/'report.typ').write_text(ty);shutil.copyfile(__file__,out/'finish_nist.py')
    for svg in out.glob('*.svg'):
        svg.write_text('\n'.join(line.rstrip()for line in svg.read_text().splitlines())+'\n')
    import typst
    typst.compile(str(out/'report.typ'),output=str(out/'report.pdf'),root=str(out))
    write(out/'build-metadata.json',{'built_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'python':sys.version,'versions':{name:importlib.metadata.version(name)for name in ['matplotlib','typst']},
        'PDF_SHA256':sha(out/'report.pdf'),'builder_SHA256':sha(out/'finish_nist.py'),
        'boundary':'Derived communication only; frozen measurements and analysis unchanged'})
    print(json.dumps({'report':str(out),'curve_identity_rows':len(identities),'isomorphic_endpoint_jobs':checked,'primary':{k:v['primary']for k,v in summary['cases'].items()}},indent=2))

if __name__=='__main__':main()
