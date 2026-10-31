"""Descriptive reports from completed native exports, without new collection."""
import argparse
import gzip
from hashlib import sha256
import json
from pathlib import Path
import sqlite3

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import typst

ROOT=Path(__file__).resolve().parents[2]


def text(value):
    return 'unknown' if value is None else str(value)


def build_b2(run,inputs,analysis,execution,export,out):
    definitions={c['id']:c for c in inputs['cells']};cells=analysis['cells']
    fig,axes=plt.subplots(1,2,figsize=(9,2.8));arms=['baseline','shifted']
    for ax,key,title in zip(axes,['unique_equations','rank_gain'],['Distinct affine equations','Additional rank on original columns']):
        for j,arm in enumerate(arms):
            values=[next(c[key] for c in cells if c['cell_id']==i and c['arm']==arm) for i in definitions]
            x=[i+(j-.5)*.34 for i in range(5)]
            ax.bar(x,[v or 0 for v in values],width=.32,label='h=0, same subset' if j==0 else 'Shifted, same subset',color=['#2166ac','#c85e18'][j])
            for position,value in zip(x,values):ax.annotate(text(value),(position,value or 0),xytext=(0,3),textcoords='offset points',ha='center',fontsize=8)
        ax.set_xticks(range(5),[i.replace('-h','\nh=') for i in definitions],fontsize=8)
        ax.set_title(title);ax.set_ylabel('objects');ax.spines[['top','right']].set_visible(False)
        ax.set_ylim(0,max(ax.get_ylim()[1],1)*1.2)
    axes[0].legend(fontsize=7,loc='upper left');fig.suptitle(run.name+': five fixed matched subsets',fontsize=10)
    fig.tight_layout();fig.savefig(out/'observations.svg');plt.close(fig)
    table='\n'.join(','.join('['+text(x)+']' for x in (c['cell_id'],c['arm'],len(definitions[c['cell_id']]['active_atoms']),c['witnesses'],c['unique_equations'],c['new_rank'],c['preprocessing_rank'],c['combined_rank'],c['rank_gain']))+',' for c in cells)
    phases='\n'.join(f"- {p['cell_id']} {p['arm']} {p['phase']}: {p['status']}, CPU {p['cpu_seconds']:.3f}s." for p in export['backend_record']['phase_records'])
    return f'''= Matched shifted-cover collectors
Observations only. One fixed physical panel, with five matched pairs. The original two p4099 E curves, sixteen native atoms and fifteen projected unknown columns stay fixed. Each pair uses the same fourteen or fifteen active atoms for both constraints and residual acceptance, original64-source order, completed-zero policy and cubic pole(3,3) law. Only h changes. All five shifts were selected by the earlier membership-only survey, including every coverage-maximizing tie; no relation yield selected these cases.

Complete panel: {analysis['panel_complete']}; collection attempts {analysis['collection_attempts_observed']}; separate replay attempts {analysis['verification_attempts_observed']}; unknown cells {analysis['unknown_cells']}. The separate arithmetic checker reconstructs every branch/status/digest, both E and auxiliary point equations, native coefficients, affine ranks, complete kernels and old-kernel action. It is an implementation cross-check, not independent scientific review.

#table(columns:(auto,auto,auto,auto,auto,auto,auto,auto,auto),inset:3pt,
[case],[arm],[atoms],[rows],[equations],[new rank],[old rank],[combined],[gain],
{table}
)
#image("observations.svg",width:100%)
The old matrices have rank9/15 on b16 and13/15 on b13. Gain is rank(M plus new rows)-rank(M) on the same original columns. Standalone rank or witness count is not additional information. Histories and each new row's old-kernel syndrome are retained. Counts are exact for these fixed cases; no curve-population or asymptotic inference follows.

#pagebreak()
== Execution boundary
Run #raw({json.dumps(run.name)}), exact source #raw({json.dumps(execution['source_commit'])}). Frozen protocol canonical SHA256 #raw({json.dumps(export['protocol']['sha256'])}). Exact committed inputs, release, interpreter/packages, real S3 gate, ownership/PIDs, host, stdout/stderr, per-source status blocks, accepted witnesses and native phase journals are beside the raw export. Lossless encodings retain original-byte hashes in archive-encodings. Data were committed/pushed before this report.

Exit {execution['returncode']}, timeout {execution['timeout']}, source unchanged after {execution['source_unchanged_after']}. Diagnostic wall {execution['diagnostic_wall_seconds']:.3f}s, user CPU {execution['cpu_user_seconds']:.3f}s, system CPU {execution['cpu_sys_seconds']:.3f}s, peak RSS {execution['max_rss_bytes']}bytes. Shared host, wall_valid=false. Producer field/group counters omit helper primality/coefficient integer work, inline separate row verification, complete replay/elimination, hashing and storage accounting. No complete S, calibrated rate or attack-cost comparison is claimed.

{phases}

== Interpretation boundary and next use
Each pair is a finite relation-space comparison, with unchanged unknowns. Any pooled row-space or independent-target attachment is a separately labelled derived analysis. D1 retains the original rank13/9 matrices as its primary preprocessing, independently of these outcomes. Native success does not change an official research state. Small p101 controls preceded the freeze; an initial eight-atom nonzero-shift positive had no accepted row and was widened only as a marked software fixture, with the initial failure log preserved. No p4099 scientific input was changed by that correction.

Sources (internal/retrieved): prior B1 and complete cover-survey RESULTS.md; original relations/independent arithmetic; newly merged prym_leads_20261027 README at068985583; PKM2016 sections3.1–3.2, primary PDF digest a53030a6cde720c354aebfb65b1eb01e07766ce2d26e543d77f2516c0a49ef5b. Translated covers and complete-divisor duplicate explanations are existing work. Pole-complete unequal-infinity strata remain a separate unexecuted lead. Historical figures and records remain unchanged; this graph records only this panel. No novelty, E-isogeny, full-DLP speedup or general rank bound is asserted.
'''


def build_d1(run,inputs,analysis,execution,export,out,supplements):
    cases=analysis['cells'];definitions={c['fixture']['uid']:c for c in inputs['cells']}
    prefix_ranks={}
    for c in cases:
        path=run/'raw'/(c['curve_uid']+'-target-'+str(c['target_index'])+'.json')
        if path.is_file():value=json.loads(path.read_text())
        elif Path(str(path)+'.gz').is_file():
            with gzip.open(str(path)+'.gz','rt') as stream:value=json.load(stream)
        else:value={}
        first=value.get('first_combined_recovery')
        prefix_ranks[(c['curve_uid'],c['target_index'])]=None if first is None else first['certificate']['augmented_rank']
    labels=[f"b={definitions[c['curve_uid']]['fixture']['b']}\nj={c['target_index']}" for c in cases]
    fig,axes=plt.subplots(1,2,figsize=(9,2.8))
    for ax,key,title in zip(axes,['witnesses','first_combined_attempt'],['Accepted natural target witnesses','First recovery prefix (branches)']):
        series=[(key,'combined stream','#2166ac')]
        if key=='first_combined_attempt':series.append(('first_single_attempt','isolated natural row','#c85e18'))
        maximum=0
        for j,(field,label,color) in enumerate(series):
            values=[c.get(field) for c in cases];x=[i+(j-.5)*.36 if len(series)>1 else i for i in range(8)]
            ax.bar(x,[v or 0 for v in values],width=.34 if len(series)>1 else .7,color=color,label=label)
            for position,v in zip(x,values):ax.annotate('none' if v is None else str(v),(position,v or 0),xytext=(0,3),textcoords='offset points',ha='center',fontsize=5,rotation=90 if len(series)>1 else 0)
            maximum=max(maximum,max(v or 0 for v in values))
        if len(series)>1:ax.legend(fontsize=6,loc='upper left');ax.set_ylim(0,max(1,maximum)*1.65)
        ax.set_xticks(range(8),labels,fontsize=7);ax.set_title(title);ax.spines[['top','right']].set_visible(False)
        if len(series)==1:ax.set_ylim(0,max(1,ax.get_ylim()[1])*1.25)
    fig.suptitle(run.name+': eight frozen public hash indices',fontsize=10)
    fig.tight_layout();fig.savefig(out/'observations.svg');plt.close(fig)
    isolated={(c['fixture_uid'],c['target_index']):c['isolated'] for c in supplements['certificates']['cases']}
    table='\n'.join(','.join('['+('none' if v is None and c['verified'] else text(v))+']' for v in (definitions[c['curve_uid']]['fixture']['b'],c['target_index'],c['base_rank'],c['witnesses'],c['identified_target'],c['augmented_rank'],prefix_ranks[(c['curve_uid'],c['target_index'])],None if isolated[(c['curve_uid'],c['target_index'])] is None else isolated[(c['curve_uid'],c['target_index'])]['augmented_rank'],None if isolated[(c['curve_uid'],c['target_index'])] is None else isolated[(c['curve_uid'],c['target_index'])]['remaining_base_nullity'],c['status']))+',' for c in cases)
    points='\n'.join(f"- b={definitions[c['curve_uid']]['fixture']['b']}, j={c['target_index']}: Q={c['target']}; base coincidence {c['target_is_signed_base_point']}; projected anchor {c['target_is_public_anchor']}; broader known-source matches {supplements['matches'][(c['curve_uid'],c['target_index'])][0]}; earlier-target matches {supplements['matches'][(c['curve_uid'],c['target_index'])][1]}." for c in cases)
    partial_scores='; '.join(f"b={definitions[c['fixture_uid']]['fixture']['b']},j={c['target_index']}: Delta={text(None if c['score'] is None else c['score']['delta'])}" for c in supplements['partials']['cases'])
    multiplier_matches='; '.join(f"b={definitions[c['fixture_uid']]['fixture']['b']},j={c['target_index']},t={c['isolated']['multiplier']}: {c['isolated']['public_multiplier_source_matches']}" for c in supplements['certificates']['cases'] if c['isolated'] is not None)
    return f'''= Independent natural-target recovery
Observations only. Eight fixed public hash indices, four per full EC1 curve identity, were frozen before any p4099 target generation. Domain prime-field-leads/20261028/target/v1; SHA256 of UTF-8 domain|curveUID|decimal index|decimal counter, big-endian mod p, first rational canonical-y point in the subgroup, counter bound10000. No target scalar label or manufactured known-log point was provided. All coincidences and unsuccessful cases remain; every target runs the full64-multiplier census regardless of first recovery.

The exact original E curves, sixteen atoms, fifteen unknown columns, public source order and old rank13/9 preprocessing are fixed independently of B2 outcomes. A target form is determined by vN=0; combinations are checked by whether the target unit vector lies in the augmented row space. Final and first-prefix row-combination weights are checked against original rows and recovered scalars are checked by multiplication on E. Full base rank is not required.

Complete panel: {analysis['panel_complete']}; unknown cases {analysis['unknown_cases']}; collection branches {analysis['collection_attempts_observed']}; separate replay branches {analysis['verification_attempts_observed']}. The native exporter holds eight candidate and eight integrated reference method records over ONE physical panel; duplicate method counts and clocks must not be added. Complete branch replay and the independent hash/root/group recipe check are separate implementations, not independent scientific review.

#table(columns:(auto,auto,auto,auto,auto,auto,auto,auto,auto,auto),inset:2pt,
[b],[j],[M rank],[rows],[identified],[final rank],[first combined rank],[isolated rank],[base nullity],[status],
{table}
)
#image("observations.svg",width:100%)
Prefix positions count scheduled branches, including misses; they are not elapsed costs. Final rank and first combined rank refer to the full stream's augmented sixteen-column system. A first rank below16 leaves base uncertainty; rank16 identifies the whole augmented system. The isolated columns instead use the original M plus ONE natural target row, with explicit unit-vector weights and a separate public-point check. Their rank is derived as rank(M)+1; remaining base nullity is15-rank(M). Thus a later isolated row can identify a target with base uncertainty even if the earlier combined stream first recovered it at full rank. Every case remains in both comparisons.

Labelled post-hoc partial-relation reuse: {partial_scores}. Treating the target as one outside column, Delta=rank([[M,0],[B,-t]])-rank(-t)-rank(M). Cancellation uses no recovered target scalar. Original-row weights, resulting base-only point equations and a separate dense modular rank oracle are checked. Each completed case is charged its collection and replay branches; analysis CPU components are diagnostic and complete S remains unmeasured. This is not a new native execution or a residual-outside-point collector result.

#pagebreak()
== Frozen targets and retained scope
{points}

The projected public-anchor flag covers anchors actually used in the base projection. The broader known-public-source comparison and cross-target coincidences are retained separately by the pre-generation reporting policy; no target is filtered or replaced. All raw hash attempts, generated recipes, native rows, statuses/digests, source blocks, first/final certificates and failure prefixes survive. Counted successes describe this finite panel, not an inferred distribution of target-descent costs.

Additional post-hoc public-point diagnostic for each isolated certificate: {multiplier_matches}. This compares [t]Q directly with every signed known public source [s]P, using no target scalar label. A listed collision is an elementary public-multiple recovery and is not evidence of a new descent mechanism or advantage. This diagnostic was added after observing individual successes; it changes no frozen target, primary metric or case inclusion.

Full hash curve identities: {', '.join(c['target_curve_uid'] for c in inputs['cells'])}. Supplementary isolated certificates and database are bound in report-inputs.json; these are labelled derived analyses, not changes to frozen primary metrics.

Run #raw({json.dumps(run.name)}), source #raw({json.dumps(execution['source_commit'])}); protocol canonical SHA256 #raw({json.dumps(export['protocol']['sha256'])}). Source/input/interpreter/release locks, actual S3 gate, ownership/PIDs, host and native phase journal are retained. Data were committed/pushed before this report. Exit {execution['returncode']}, timeout {execution['timeout']}, source unchanged {execution['source_unchanged_after']}. Wall {execution['diagnostic_wall_seconds']:.3f}s, user CPU {execution['cpu_user_seconds']:.3f}s, system CPU {execution['cpu_sys_seconds']:.3f}s, peak RSS {execution['max_rss_bytes']}bytes. Shared-host wall_valid=false. Partial field/group/hash/validation counters omit complete linear algebra, replay, serialization/storage and complete S. There is no calibrated IC/rho, cold/online or attack-cost comparison.

Sources (internal/retrieved): original TargetRelations and separate Census/arithmetic lane, B1 fixed preprocessing, prym_leads_20261027 target-row criterion and matrix review, PKM2016 section3.2. The arbitrary-coefficient pair examples are controls, not natural unknown-target successes. Broader bases, fields, targets, pole laws and signed partial relations remain separate work. This report promotes no scientific status, novelty, asymptotic improvement or speedup. Historical graphs stay unchanged; this graph covers this exact panel.
'''


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--kind',choices=['b2','d1'],required=True);parser.add_argument('--run',type=Path,required=True)
    parser.add_argument('--inputs',type=Path,required=True);parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--target-certificates',type=Path);parser.add_argument('--target-partials',type=Path);parser.add_argument('--database',type=Path)
    args=parser.parse_args();args.out.mkdir(parents=True,exist_ok=False)
    def load(p):
        with (gzip.open(p,'rt') if p.suffix=='.gz' else p.open()) as stream:return json.load(stream)
    inputs,analysis,execution,export=(load(p) for p in (args.inputs,args.run/'analysis.json',args.run/'execution.json',args.run/'export.json'))
    plt.rcParams.update({'font.size':9,'svg.fonttype':'none'})
    paths=[args.inputs,args.run/'analysis.json',args.run/'execution.json',args.run/'export.json',Path(__file__)]
    if args.kind=='d1':
        if args.target_certificates is None or args.database is None or args.target_partials is None:raise ValueError('D1 needs explicit derived certificate/partial/database inputs')
        certificates=load(args.target_certificates)
        partials=load(args.target_partials)
        if any(value['source_export_sha256']!=sha256((args.run/'export.json').read_bytes()).hexdigest() for value in (certificates,partials)):raise ValueError('supplement export differs')
        with sqlite3.connect('file:'+str(args.database.resolve())+'?mode=ro',uri=True) as connection:
            matches={(uid,index):(public,other) for uid,index,public,other in connection.execute('SELECT b.fixture_uid,t.target_index,t.public_source_matches_json,t.intertarget_matches_json FROM target_cases t JOIN bases b USING(base_sha256)')}
        source=build_d1(args.run,inputs,analysis,execution,export,args.out,dict(certificates=certificates,matches=matches,partials=partials))
        paths.extend([args.target_certificates,args.target_partials,args.database])
    else:source=build_b2(args.run,inputs,analysis,execution,export,args.out)
    (args.out/'report-inputs.json').write_text(json.dumps([dict(path=str(p),bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest()) for p in paths],indent=2)+'\n')
    svg=args.out/'observations.svg';svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
    (args.out/'plotted-data.json').write_text(json.dumps(analysis['cells'],indent=2)+'\n')
    header='#set page(paper:"a4",margin:16mm)\n#set text(size:9pt)\n'
    (args.out/'report.typ').write_text(header+source)
    typst.compile(str(args.out/'report.typ'),output=str(args.out/'report.pdf'),root=str(args.out.resolve()))
    print(json.dumps(dict(report=str(args.out/'report.pdf'),sha256=sha256((args.out/'report.pdf').read_bytes()).hexdigest())))


if __name__=='__main__':main()
