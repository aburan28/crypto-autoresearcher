"""Write-once direct-collector observation report from retained admitted records."""
import argparse
import gzip
from hashlib import sha256
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import typst


def load(path):
    paths=[p for p in (path,Path(str(path)+'.gz')) if p.is_file()]
    if len(paths)!=1: raise ValueError('missing/ambiguous encoding')
    with (gzip.open(paths[0],'rt') if paths[0].suffix=='.gz' else paths[0].open()) as stream: return json.load(stream)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('run','inputs','out'): parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args();args.out.mkdir(parents=True,exist_ok=False)
    analysis=load(args.run/'analysis.json');execution=load(args.run/'execution.json');export=load(args.run/'export.json');inputs=load(args.inputs)
    cells=analysis['cells'];native={};verifications={}
    for cell in inputs['cells']:
        value=load(args.run/'raw'/(cell['id']+'.json'));verifications[cell['id']]=load(args.run/'raw'/(cell['id']+'.verification.json'))
        for arm in value['arms']: native[cell['id'],arm['arm']]=arm
    plt.rcParams.update({'svg.fonttype':'none','font.size':9})
    fig,axes=plt.subplots(1,2,figsize=(9,3));labels=[c['cell_id']+'\n'+c['arm'] for c in cells]
    plotted=[]
    for axis,field,title in zip(axes,('distinct_equations','rank_gain'),('Distinct projected affine equations','Additional rank on original 15 columns')):
        values=[c[field] for c in cells];axis.bar(range(4),values,color=['#2166ac','#bd5426']*2)
        for i,value in enumerate(values): axis.annotate(str(value),(i,value),xytext=(0,3),textcoords='offset points',ha='center')
        axis.set_xticks(range(4),labels,fontsize=7);axis.set_title(title);axis.set_ylabel('equations' if field=='distinct_equations' else 'dimensions')
        axis.spines[['top','right']].set_visible(False);axis.set_ylim(0,max(1,max(values))*1.3);plotted.append(dict(field=field,values=values))
    fig.suptitle(args.run.name+': two fixed curves, four matched records',fontsize=10);fig.tight_layout();fig.savefig(args.out/'observations.svg');plt.close(fig)
    svg=args.out/'observations.svg';svg.write_text('\n'.join(v.rstrip() for v in svg.read_text().splitlines())+'\n')
    table='\n'.join(','.join('['+str(v)+']' for v in (c['cell_id'],c['arm'],c['attempts'],c['accepted_witnesses'],c['distinct_equations'],c['new_rank'],c['combined_rank'],c['rank_gain']))+',' for c in cells)
    costs=[]
    for c in cells:
        arm=native[c['cell_id'],c['arm']];counts=arm['analysis']['total_counters']
        costs.append(','.join('['+str(v)+']' for v in (c['cell_id'],c['arm'],counts.get('Fp.group_add',0),counts.get('Fp.field_mul',0),
                    counts.get('Fp.field_inv',0),counts.get('Fr.field_mul',0),counts.get('Fr.field_inv',0)))+',')
    subsets='\n'.join('- '+key+': '+str(v['archived_norm_subset']['witnesses'])+' archived norm witnesses map to '+str(v['archived_norm_subset']['distinct_direct_descriptors'])+' distinct direct descriptors.' for key,v in verifications.items())
    phases=[]
    for c in cells:
        arm=native[c['cell_id'],c['arm']]
        for record in arm['collection_phases']+arm['analysis']['analysis_phases']:
            phases.append(dict(cell_id=c['cell_id'],arm=c['arm'],**record))
    (args.out/'plotted-data.json').write_text(json.dumps(dict(cells=cells,plotted=plotted,phases=phases),indent=2)+'\n')
    text=f'''#set page(paper:"a4",margin:16mm)
#set text(size:9pt)
= Direct signed three-sum collection
Observations from #raw({json.dumps(args.run.name)}). The original two p4099 curves, original16atoms, public64source schedules and historical97/rank13 or67/rank9 matrices are unchanged. Both direct collectors search every signed triple with distinct atom indices j < k < l and equation εj Bj + εk Bk + εl Bl = sP. No cover lift is required, and no outside unknown, recovered atom label or target is used.

Enumeration evaluates every source/triple/sign descriptor. The pair-table method constructs all signed pairs once, queries sP − εl Bl, retains every bucket entry and accepts only j < k < l. Infinity is a supported key. Each arm has its own cold setup/sign/source/projection and elimination accounting. Both complete their fixed stream; neither stops at full rank. Row ordering is canonical before analysis.

#table(columns:(auto,auto,auto,auto,auto,auto,auto,auto),inset:3pt,
[case],[arm],[descriptors / queries],[rows],[equations],[new rank],[combined],[gain],
{table}
)
Enumeration descriptors and pair-table queries are different work units. Each curve has480pair entries. Four arm records belong to ONE physical admitted process; they are not four physical executions. Distinct affine equations and independent rank are different measurements.

#image("observations.svg",width:100%)
Gain is rank(M plus new rows)−rank(M) on the unchanged15projected columns. Full old/combined right kernels, signed public-anchor projection, pivot-row indices and old-kernel syndromes are retained. New rank is calculated without adding the old rows; old rank is still measured and charged.

#pagebreak()
== Archived norm rows and complete checks
The archived A2 norm_completed=true rows are a frozen subset reference. Their two residual E images sum to zero, leaving only three signed original atoms and the source. Every such descriptor must occur in the direct census. A2 smooth five-term rows are excluded from this assertion. The original archived full C/auxiliary checks are not rerun as part of A3.

{subsets}

The separate checker imports the old independent E arithmetic, not producer arithmetic. It reconstructs every exhaustive descriptor, status and digest, reconstructs every pair entry and query bucket including rejected index orderings, checks identical complete row lists, validates all old principal rows, and recomputes affine ranks, consistency, pivot spans, complete kernels and old-kernel action. Logical table counters and stage-counter conservation are checked; producer field counters are not independently audited. This is an implementation check, not independently staffed scientific review.

== Stage accounting
The following totals are recorded instrumented operations per arm, including its setup, collection, certificate construction, public projection, affine normalization, old/new/combined elimination, kernels and kernel action. Fp operations and Fr operations are separate units. Inversions have their own unit; internal modular arithmetic inside inversion is not expanded. Group additions include underlying field operations, so the columns must not be added as disjoint cost units.

#table(columns:(auto,auto,auto,auto,auto,auto,auto),inset:3pt,
[case],[arm],[Fp group add],[Fp mul],[Fp inv],[Fr mul],[Fr inv],
{chr(10).join(costs)}
)
Every collection/analysis stage also retains diagnostic wall and CPU seconds. Query and hit extraction are one explicitly combined stage. No C lifting or polynomial extraction exists in this direct implementation. Storage, serialization, sorting, hash-table comparisons, Python allocations, validation and independent replay do not have a complete weighted operation model. The outer phase journal and whole-process resources cover the execution diagnostically; do not add outer clocks to their inner components. Complete S, calibrated Delta-per-total-cost, matched rho and an end-to-end speedup remain unmeasured. A2's older incomplete counters are not a matched cost baseline.

#pagebreak()
== Execution and provenance
Native source #raw({json.dumps(execution['source_commit'])}). Canonical protocol SHA256 #raw({json.dumps(export['protocol']['sha256'])}). Exact input bytes, source closure, interpreter/packages, committed root release, actual S3 checkpoint/gate, ownership/PIDs, stdout/stderr and all branch journals are retained. Sources and protocol were frozen before native collection; preparation controls used only marked p101 fixtures.

Panel complete: {analysis['panel_complete']}. Exit {execution['returncode']}; timeout {execution['timeout']}; source unchanged after {execution['source_unchanged_after']}. Shared-host diagnostic wall {execution['diagnostic_wall_seconds']:.3f}s; user CPU {execution['cpu_user_seconds']:.3f}s; system CPU {execution['cpu_sys_seconds']:.3f}s; peak RSS {execution['max_rss_bytes']}bytes. All clocks wall_valid=false. Protective2048retained-row/4096pair-entry gates refuse with the prefix preserved; they never truncate a successful census. The2GiB/21600s process watchdog protects the host. Failures and unknowns remain explicit.

Full curve identities: {', '.join(c['fixture']['ec1']['curve_uid'] for c in inputs['cells'])}.

Collection snapshots precede elimination; final results precede separate checking. All raw records were committed and pushed before this report. Closed large records are losslessly gzipped with original/archive hashes and official content-addressed S3 manifests. The v6 database is a fresh indexed extension of the byte-preserved v5 parent, retaining older records and adding direct-arm rows and archived norm matches. Historical reports and graphs remain intact. This panel's graph is a new derived view; no canonical scientific verdict is changed.

== Prior work and boundaries
Petit–Kosters–Messeng, PKC2016 sections3.1–3.4, distinguishes base construction, relation solving and linear algebra (retrieved primary PDF SHA256 a53030a6cde720c354aebfb65b1eb01e07766ce2d26e543d77f2516c0a49ef5b). The repository already records generic enumeration/pair-table methods and broader cost obstructions under LEAD-ICP-generic-table-decomposition, index_calculus/README.md and FINDING-PF-IC-001. The coordinator read the linked crypto primary program at423ea37eca55e459028adae4276d628ea6249738. Full provenance and inspected source sections are in literature.md.

The pair-table method is a standard generic construction. This study diagnoses the earlier Prym norm-completion lead and measures this local implementation; it does not revive a closed generic attack direction or assert a new symmetry, novel attack, scalable advantage or transfer to larger fields. Only the two already studied small curves are tested. Independent larger-field holdouts and natural-target queries are subsequent separately specified experiments. No scientific status promotion, verified configured model identity or passing full-ledger audit is asserted.
'''
    (args.out/'report.typ').write_text(text)
    typst.compile(str(args.out/'report.typ'),output=str(args.out/'report.pdf'),root=str(args.out.resolve()))
    print(json.dumps(dict(report=str(args.out/'report.pdf'),sha256=sha256((args.out/'report.pdf').read_bytes()).hexdigest())))


if __name__=='__main__': main()
