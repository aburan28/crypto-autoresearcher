#!/usr/bin/env python3
"""Derived wider-run report, exact identities and lossless GitHub-sized raw shards."""
import csv
import datetime
import hashlib
import json
import math
import shutil
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

RUN=Path(sys.argv[1]).resolve()
sys.path.insert(0,str(RUN/'source'))
from common import write,sha
from curve_identity import curve_identity
from finite_math import Curve


def main():
    out=RUN/'report';out.mkdir(exist_ok=False)
    load=lambda p:json.loads((RUN/p).read_text())
    summary=load('analysis/summary.json');groups=load('preparation/public-groups.json')
    jobs={j['job_id']:j for j in load('attacks/job-index.json')}
    gm={g['group_id']:g for g in groups};targets={t['id']:t for t in load('preparation/public-targets.json')}
    identities=[{**g,'purpose':'original attack group'}for g in groups]
    endpoints={};endpoint_jobs=[]
    for path in sorted((RUN/'attacks').glob('block-*/raw-results.jsonl')):
        raw={r['job_id']:r for r in map(json.loads,path.read_text().splitlines()) if r['mode']in['native_iso','transport']}
        if not raw:continue
        for line in (path.parent/'public-jobs.txt').read_text().splitlines():
            jid,mode,adding,seed,*vals=line.split()
            if mode not in ['native_iso','transport']:continue
            p,A,B,ell,h,gx,gy,qx,qy,u=map(int,vals);j=jobs[jid];g=gm[j['group_id']];t=targets[j['target_id']]
            assert u%p and A==g['A']*pow(u,4,p)%p and B==g['B']*pow(u,6,p)%p
            assert [gx,gy]==[g['G'][0]*pow(u,2,p)%p,g['G'][1]*pow(u,3,p)%p]
            assert [qx,qy]==[t['Q'][0]*pow(u,2,p)%p,t['Q'][1]*pow(u,3,p)%p]
            c=Curve(p,A,B);assert c.on_curve((gx,gy)) and c.on_curve((qx,qy)) and c.mul((gx,gy),ell)is None
            assert raw[jid]['scalar']is not None and c.mul((gx,gy),raw[jid]['scalar'])==(qx,qy)
            model={**g['curve'],'a4':A,'a6':B,'generator':[gx,gy]};ident=curve_identity(g['field'],model,'primecomparison')
            endpoints[g['group_id']]={**g,'group_id':g['group_id']+'-iso','A':A,'B':B,'G':[gx,gy],
                'curve':model,'identity':ident,'purpose':'degree-1 isomorphic control',
                'source_curve_uid':g['identity']['curve_uid'],'degree':1,'u':u}
            endpoint_jobs.append({'job_id':jid,'actual_curve_uid':ident['curve_uid'],'actual_subgroup_and_scalar_checked':True})
    identities.extend(endpoints.values())
    write(out/'isomorphism-identities.json',{'endpoints':list(endpoints.values()),'jobs':endpoint_jobs,
          'map':'(x,y)->(u^2*x,u^3*y), degree 1 over F_p; nonzero u; inverse parameter u^-1'})
    ai=[]
    for path in sorted((RUN/'arithmetic').glob('m*/result.json')):
        r=json.loads(path.read_text());m=r['modulus'];row=load('preparation/curves/'+m['id']+'/curves.json')['curves'][0];pc=r['public_curve']
        assert (pc['p'],pc['A'],pc['B'])==(row['p'],row['A'],row['B'])
        f={'characteristic':pc['p'],'degree':1,'representation':'prime field, canonical integer residues','element_encoding':'integers 0..p-1','modulus':pc['p']}
        c={'model':'short-Weierstrass','a4':pc['A'],'a6':pc['B'],'subgroup_order':row['ell'],'cofactor':row['h'],
           'generator':pc['G'],'target_group':'prime-order cyclic subgroup of E(F_p)'}
        assert Curve(pc['p'],pc['A'],pc['B']).mul(tuple(pc['G']),row['ell'])is None
        ai.append({**m,**pc,'group_id':'arithmetic-'+m['id'],'ell':row['ell'],'h':row['h'],'field':f,'curve':c,
                   'identity':curve_identity(f,c,'primecomparison'),'purpose':'arithmetic microbenchmark'})
    identities.extend(ai);write(out/'arithmetic-curve-identities.json',ai)
    with (out/'all-curve-identities.csv').open('x',newline='')as f:
        cols=['purpose','group_id','curve_uid','field_sha256','p','A','B','ell','h','Gx','Gy'];w=csv.DictWriter(f,fieldnames=cols,lineterminator='\n');w.writeheader()
        w.writerows({**{k:g[k]for k in cols[:2]+['p','A','B','ell','h']},'curve_uid':g['identity']['curve_uid'],
          'field_sha256':g['identity']['field_sha256'],'Gx':g['G'][0],'Gy':g['G'][1]}for g in identities)
    # The retained original exceeds GitHub's 100 MiB blob limit. Per-block JSON
    # records reconstruct its exact bytes; keep the original locally and in ZIP.
    original=RUN/'preparation/matching.json';matching=json.loads(original.read_text());shards=RUN/'preparation/matching-blocks';shards.mkdir()
    for row in matching:write(shards/f"block-{row['block']:02d}.json",row)
    rebuilt=(json.dumps(matching,indent=2)+'\n').encode();assert hashlib.sha256(rebuilt).hexdigest()==sha(original)
    write(shards/'index.json',{'original':'../matching.json','original_bytes':original.stat().st_size,'original_sha256':sha(original),
          'format':'JSON array in sorted block order, indent=2, trailing newline',
          'parts':[{'path':f"block-{r['block']:02d}.json",'sha256':sha(shards/f"block-{r['block']:02d}.json")}for r in matching]})
    (RUN/'.gitignore').write_text('/preparation/matching.json\n**/__pycache__/\n')
    (RUN/'reassemble-matching.py').write_text('''import json,hashlib\nfrom pathlib import Path\nr=Path(__file__).parent;s=r/'preparation/matching-blocks';m=json.loads((s/'index.json').read_text());rows=[]\nfor p in m['parts']:\n b=(s/p['path']).read_bytes();assert hashlib.sha256(b).hexdigest()==p['sha256'];rows.append(json.loads(b))\nb=(json.dumps(rows,indent=2)+'\\n').encode();assert len(b)==m['original_bytes'] and hashlib.sha256(b).hexdigest()==m['original_sha256']\np=r/'preparation/matching.json'\nif p.exists():assert p.read_bytes()==b\nelse:\n with p.open('xb')as f:f.write(b)\nprint('Exact raw matching.json reconstructed/verified',len(b),'bytes')\n''')
    write(out/'derived-checks.json',{'actual_isomorphic_jobs':len(endpoint_jobs),'all_actual_endpoint_checks_pass':True,
          'curve_identity_rows':len(identities),'lossless_matching_shards':len(matching),'matching_exact_bytes_verified':True,
          'BSGS_exact_accounting_jobs':summary['BSGS_jobs_exactly_accounted'],
          'canonical_graph_change':'None; this run supplies no mechanism, sealed bound or paired challenge verdict',
          'graphs_checked':['New workflow and attack-ratio figures','Historical Solinas design/report figures','knowledge/frontiers/ecdlp tree inventory'],
          'claim_status':'Measured observations and derived accounting only; no independently reviewed promotion'})
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'svg.fonttype':'none','svg.hashsalt':RUN.name})
    fig,ax=plt.subplots(figsize=(8.3,4.3));labels=[];v=[]
    for mode,label in [('rho','Native rho 16'),('oracle','Opaque rho 16'),('rho32','Native rho 32'),('bsgs','BSGS')]:
        for arm in ['R','C']:labels.append(label+' / '+('random'if arm=='R'else'residue controls'));v.append(summary['attack_comparisons'][mode+'_S_'+arm])
    xmin=min(x['CI99_9'][0]for x in v)-.02;xmax=max(x['CI99_9'][1]for x in v)+.16
    for y,x in enumerate(v):
        a,z=x['CI99_9'];ax.errorbar(x['estimate'],y,xerr=[[x['estimate']-a],[z-x['estimate']]],fmt='o',capsize=3,color='#236478')
        ax.annotate(f"{x['estimate']:.4f} [{a:.4f}, {z:.4f}]",(xmax-.15,y),fontsize=8,va='center')
    ax.axvline(1,color='gray',linestyle='--');ax.set(yticks=range(len(labels)),yticklabels=labels,xlim=(xmin,xmax),xlabel='Solinas / pooled control normalized group work (dimensionless)');ax.invert_yaxis();ax.grid(axis='x',alpha=.2)
    fig.suptitle('72 fresh prime blocks · marginal 99.9% whole-block bootstrap intervals')
    fig.text(.5,.015,RUN.name+'; 500,000 replicates within four field-bit strata. Each control pools two prime arms.',ha='center',fontsize=7)
    fig.tight_layout(rect=(0,.05,1,.95));fig.savefig(out/'attack-ratios.svg');plt.close(fig)
    fig,ax=plt.subplots(figsize=(8.3,2.3));ax.axis('off')
    for x,t in [(.01,'72 fresh sparse primes\n288 distinct random controls'),(.35,'128 unconditional models / prime\n1024 matching candidates / prime'),(.69,'8 matched groups / arm\n4 targets × 4 rho seeds')]:
        ax.text(x+.135,.58,t,ha='center',va='center',fontsize=8,bbox={'boxstyle':'round,pad=.7','facecolor':'#e7f0f3','edgecolor':'#236478'})
    for x in [.30,.64]:ax.annotate('',xy=(x+.035,.58),xytext=(x,.58),arrowprops={'arrowstyle':'->','color':'#236478'})
    ax.text(.5,.12,'Four strata: 24 / 28 / 32 / 36 bits. Baseline moduli excluded; baseline outcomes not pooled.',ha='center',fontsize=9)
    fig.suptitle('Frozen prospective sample → five-arm matching → attack trials');fig.tight_layout();fig.savefig(out/'workflow.svg');plt.close(fig)
    p=summary['primary_result'];a,z=p['CI99_9'];ba,bz=p['CI99_9667_reserved_three_primary_tests']
    table='\n'.join(f"| {k} | {x['estimate']:.6f} | {x['CI99_9'][0]:.6f}–{x['CI99_9'][1]:.6f} |"for k,x in summary['attack_comparisons'].items())
    arithtable='\n'.join(f"| {k} | {x['S_R']['estimate']:.4f} | {x['S_R']['CI99_9'][0]:.4f}–{x['S_R']['CI99_9'][1]:.4f} | {x['median_Python_fold_over_builtin_seconds']:.4f} |"for k,x in summary['arithmetic'].items())
    population=summary['population_proxy_difference_bits']['S_R']
    md=f'''# Wider Solinas prime comparison — 2026-10-11

**Measured native-rho Solinas / pooled random-control ratio {p['estimate']:.6f}; marginal 99.9% CI [{a:.6f}, {z:.6f}].** Decision under the frozen margin [1/1.2,1.2]: {summary['decision']}. The reserved three-family Bonferroni 99.9667% interval is [{ba:.6f}, {bz:.6f}], offering approximate joint 99.9% primary coverage if three family tests are completed. The two other named prime definitions remain a separate user clarification; this run asserts nothing about them.

## Scope and design

EXP-ECDLP-5184f7 / {RUN.name} is a prospective extension of RUN-ECDLP-a24605. It excludes every baseline modulus and pools no baseline result. It samples 18 distinct sparse primes per 24/28/32/36-bit stratum, 72 total; two independent size-matched random primes and two size-and-mod-12-matched random primes per block, **288 controls**. Prime form: p=2^b−2^a+s2^c+t, 1 ≤ c ≤ a−1, a ≤ b−2, s,t=±1, deduplicated by integer. Candidate draws and exact PARI primality decisions are retained.

All {summary['prepared_nonsingular_models']:,} prepared models and {summary['unconditional_models']:,} unconditional models are retained. Each prime has a fixed pool of 1,024 uniform nonsingular coefficient models. Conditional largest-subgroup attacks exclude anomalous, supersingular, special-j and embedding-degree≤20 cases; ell has 16–28 bits, multiplicity one. Eight S candidates must match all four control arms within 10% ell. Matching is maximum-cardinality, then minimum log-order distance, with fixed SciPy assignment tie handling. There are 2,880 matched groups and four tiny easy groups.

![Workflow](workflow.svg)

## Measured results and integrity

All **{summary['attack_jobs']:,}** attack jobs completed. Main rho censor count: **{summary['main_rho_censors']}**. All returned scalars and collision equations passed the runner checks. All **{summary['exact_control_checks']}** sham/replay/transport equality checks and four BSGS easy positive controls passed. The supplement checks {len(endpoint_jobs)} jobs on 16 actual isomorphic endpoint models. Exact EC1 identities, subgroup orders and generators are in [all-curve-identities.csv](all-curve-identities.csv).

| Contrast | Ratio | Marginal 99.9% interval |
|---|---:|---:|
{table}

![Attack comparison](attack-ratios.svg)

Rho uses search group calls/sqrt(ell), restricted at horizon 20. Setup and verification remain separate. Each control mean pools two independent prime arms per matched slot; eight slot log-ratios average to one prime-block observation. Seeds and targets are repetitions, not 150,000 independent samples. All 72 blocks receive equal weight. The 500,000-replicate bootstrap resamples whole blocks within bit strata; nominal percentile coverage is approximate. Three-family adjustment applies to the primary comparisons only; exploratory contrasts are marginal.

BSGS uses M=min(4096,ceil(sqrt(ell))), retains allocated table bytes and normalizes setup+search by M+ell/(2M). Every one of {summary['BSGS_jobs_exactly_accounted']:,} BSGS jobs matches exact counts: setup=M+popcount(M)+bit_length(M)−1; search=floor(q/M). Its empirical contrast therefore includes finite target-position and subgroup/table-size effects; a BSGS difference alone is not a field-prime resistance result.

## Population and arithmetic

The unconditional generic proxy 0.5 log2(largest prime factor of curve order) differs by {population['estimate']:.6f} bits for S minus pooled R, with marginal 99.9% CI {population['CI99_9']}. This is a group-order proxy, not a certified security bound. Full N, factorization, trace, twist order and obvious-weakness flags remain in each modulus's curves.json; no weak curves are removed from the unconditional audit.

| Python workload | Generic S / pooled R | Marginal 99.9% CI | Median fold / builtin S seconds |
|---|---:|---:|---:|
{arithtable}

All {summary['arithmetic_observations']:,} arithmetic observations have exact output agreement. Inversion intentionally uses the identical builtin pow in both paths. This Python folding prototype does not measure production optimized field arithmetic; timings and their intervals describe this implementation and machine, not intrinsic ECDLP work or a sealed bound.

## Theory, boundaries and provenance

Generic rho solves synthetic Q=qG using collisions, requiring order sqrt(ell) group operations. The field's binary expression can change primitive arithmetic costs without changing that operation count. Abstract isomorphism of equal-order cyclic groups does not supply a computable coordinate map between arbitrary elliptic curves. The opaque solver interface prevents this implemented solver from consulting coordinates, not adversarial reflection. The tested degree-1 maps explicitly transport G and Q and preserve the subgroup.

This is a finite toy study with uniform short-Weierstrass coefficient models and matched largest-prime subgroups. It is not a universal result about Solinas primes, real deployed ECDLP, structure-aware attacks, number-field rank or all possible arithmetic backends. The 36-bit stratum broadens field sizes but does not approach deployed cryptographic sizes. There is no asymptotic algorithm, scientific-state promotion, sealed bound, or frontier update; generic rho and memory-accounted BSGS remain the reference methods. Original reports and canonical frontier graphs stay unchanged.

Sources and this extension's contract froze at [run manifest](../manifest.json) before selection. See [frozen contract](../contract.json), [exact commands and phase outcomes](../execution-result.json), [machine summary](../analysis/summary.json), [prime blocks](../analysis/prime-block-metrics.json), [checks and identities](derived-checks.json), and all retained preparation, attack and arithmetic directories. The 192-MiB matching array is retained locally and in the ZIP; committed per-block JSON shards reconstruct its exact original bytes using reassemble-matching.py and verified hashes. This is a storage representation change, not a trial correction. No independent scientific review was obtained.
'''
    (out/'report.md').write_text(md)
    typ=f'''#set page(paper: "a4", margin: 18mm, footer: context align(center)[#text(size: 8pt)[{RUN.name} · #counter(page).display()]])
#set text(font: "DejaVu Sans", size: 10pt)
= Wider Solinas prime comparison
2026-10-11 · EXP-ECDLP-5184f7 · {RUN.name}

#text(size: 17pt, weight: "bold")[Native rho ratio {p['estimate']:.4f}]

Marginal *99.9% interval: {a:.4f}–{z:.4f}*. Reserved three-family 99.9667% Bonferroni interval: {ba:.4f}–{bz:.4f}. Frozen practical-similarity margin: 0.8333–1.2000. Decision: {summary['decision']}.

*Prospective wider scope:* 72 fresh sparse-prime blocks, 288 random controls, four field-bit strata (24/28/32/36), 368,640 nonsingular prepared models and 46,080 unconditional audit models. Baseline moduli are excluded and baseline outcomes are not pooled.

#image("workflow.svg",width:100%)

The sparse integer catalog is p=2^b−2^a+s2^c+t, 1 ≤ c ≤ a−1, a ≤ b−2, s,t=±1. Each block has two size-matched random controls and two controls additionally matching p mod 12. Fixed pools give eight common S matches across all four control arms, within 10% subgroup order; largest ell has 16–28 bits. The unconditional audit does not exclude weak curves.

Whole-prime-block bootstrap: 500,000 replicates within bit-size strata. Targets and walk seeds are repetitions, not independent prime samples. Intervals have approximate nominal coverage. The three-family adjustment concerns primary tests only; other results use marginal intervals. This run does not identify or test the two other user-named prime cases.

#pagebreak()
= Attack results and controls
#image("attack-ratios.svg",width:100%)

All {summary['attack_jobs']:,} jobs completed; main rho censors = {summary['main_rho_censors']}. All recovered scalars and collision equations passed arithmetic checks. All {summary['exact_control_checks']} sham, replay and transported-isomorphism checks and four BSGS easy positive controls passed. {len(endpoint_jobs)} actual transported endpoint jobs were also checked; full identities accompany the report.

Rho endpoint: search group calls/sqrt(ell), capped at normalized horizon 20; setup and verification remain separate. Each comparison pools two control arms per slot, then averages eight slot log-ratios per block. BSGS uses setup+search normalized by M+ell/(2M), M≤4096, with table memory retained.

Every one of {summary['BSGS_jobs_exactly_accounted']:,} BSGS jobs matches exact count identities: setup=M+popcount(M)+bit_length(M)−1; search=floor(q/M). Its empirical contrast includes target position and finite ell/table-size effects; it does not establish extra resistance from field-prime form.

#pagebreak()
= Implications and scope
The unconditional proxy (0.5 log2 largest prime factor of curve order) differs by {population['estimate']:.4f} bits, S minus pooled random controls. Its marginal 99.9% interval is {population['CI99_9'][0]:.4f}–{population['CI99_9'][1]:.4f}. This is not a certified security bound.

The arithmetic panel has {summary['arithmetic_observations']:,} exact-output-equal observations. Python folding and builtin modular arithmetic are implementation comparisons. Inversion uses identical builtin pow in both paths. report.md and analysis/summary.json retain every timing ratio and higher-confidence interval; production C/assembly arithmetic is untested.

Generic rho collision work depends mainly on subgroup size. Sparse binary expressions can affect field reduction. Equal-order cyclic groups being abstractly isomorphic supplies no efficient coordinate map between arbitrary curves. The implemented opaque interface limits this solver's coordinate access; it is not a formally enforced oracle against an adversarial program.

Scope is the declared finite sparse-prime catalog, uniform nonsingular coefficient models, matching rules and implemented toy attacks. This does not settle deployed ECDLP, structural attacks, all Solinas primes, number-field rank or unrelated prime families. No scientific claim, sealed bound or canonical frontier is promoted.

= Artifacts and provenance
See manifest.json and contract.json for preselection source commit, hashes, seeds and exact commands; execution-result.json for actual phase outcomes; analysis/summary.json for every estimate; report/all-curve-identities.csv for {len(identities):,} full EC1 identities; report.md for links and detailed limitations. All raw outputs are retained. Committed per-block matching shards reconstruct the exact retained large array; this changes storage only. No independent scientific review was obtained.
'''
    (out/'report.typ').write_text(typ);shutil.copyfile(__file__,out/'finish_wide.py')
    import typst
    typst.compile(str(out/'report.typ'),output=str(out/'report.pdf'),root=str(out))
    print(json.dumps({'report':str(out),'primary':p,'identities':len(identities),'matching_shards':len(matching)}))


if __name__=='__main__':main()
