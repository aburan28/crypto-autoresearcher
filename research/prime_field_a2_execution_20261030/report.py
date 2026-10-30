"""Write-once descriptive report for the prospective norm-completion census."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import typst


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('run','inputs','out'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);load=lambda p:json.loads(p.read_text())
    analysis=load(a.run/'analysis.json');execution=load(a.run/'execution.json');export=load(a.run/'export.json');inputs=load(a.inputs);cells=analysis['cells']
    plt.rcParams.update({'svg.fonttype':'none','font.size':9});fig,axes=plt.subplots(1,2,figsize=(9,2.8));labels=[c['cell_id']+'\n'+c['arm'] for c in cells]
    for ax,key,title in zip(axes,('accepted_witnesses','rank_gain'),('Accepted witnesses','Additional rank on original15 columns')):
        values=[c[key] for c in cells];ax.bar(range(4),[v or 0 for v in values],color=['#2166ac','#c85e18']*2)
        for i,v in enumerate(values):ax.annotate('unknown' if v is None else str(v),(i,v or 0),xytext=(0,3),textcoords='offset points',ha='center',fontsize=8)
        ax.set_xticks(range(4),labels,fontsize=7);ax.set_title(title);ax.set_ylabel('objects' if key=='accepted_witnesses' else 'dimensions');ax.spines[['top','right']].set_visible(False);ax.set_ylim(0,max(1,ax.get_ylim()[1])*1.25)
    fig.suptitle(a.run.name+': all four fixed arm/curve records',fontsize=10);fig.tight_layout();fig.savefig(a.out/'observations.svg');plt.close(fig)
    svg=a.out/'observations.svg';svg.write_text('\n'.join(v.rstrip() for v in svg.read_text().splitlines())+'\n')
    show=lambda v:'unknown' if v is None else str(v)
    table='\n'.join(','.join('['+show(v)+']' for v in (c['cell_id'],c['arm'],c['accepted_witnesses'],c['norm_completed_witnesses'],c['distinct_equations'],c['new_rank'],c['combined_rank'],c['rank_gain'],c['base_nullity_after']))+',' for c in cells)
    phases='\n'.join('- '+v['cell_id']+' '+str(v.get('arm'))+' '+v['phase']+': '+v['status']+', CPU '+format(v['cpu_seconds'],'.3f')+'s.' for v in export['backend_record']['phase_records'])
    text=f'''#set page(paper:"a4",margin:16mm)
#set text(size:9pt)
= Residual norm-cancellation completion
Observations only. This prospective new census follows the verified A1 residual-pool observation. It keeps both original p4099 E curves, original16native atoms,15projected unknowns, historical97/rank13 and67/rank9 matrices, original64public sources, completed x=0 policy and cubic pole(3,3) law fixed. It does not add A1/B2/D1 relations, a target, outside unknowns or a pool.

The smooth reference requires both residual endpoints to belong to the original base. The completed arm additionally accepts a rational distinct residual pair when its E images (x1²,y1),(x2²,y2) have equal x-coordinate and opposite y. Their sum on E is zero, so the principal-divisor relation has only the three original constrained base terms plus the known source. The full six-point C witness and auxiliary norm still have to pass. All other lower-degree, repeated-root and unsupported residual cases remain rejected. A residual pair already inside the base is labelled smooth even if it cancels.

Panel complete: {analysis['panel_complete']}; collection branches {analysis['physical_collection_attempts_observed']}; full separate replay branches {analysis['physical_replay_attempts_observed']}; unknown cells {analysis['unknown_cells']}. Four nested arm records share TWO complete source streams in ONE physical process. Counts/counters on the smooth records and shared backend resources are charged once; repeated logical attempts are not additional execution work. There is no rank stop, branch sample or outcome-based case selection.

#table(columns:(auto,auto,auto,auto,auto,auto,auto,auto,auto),inset:3pt,
[case],[arm],[rows],[new norm rows],[equations],[new rank],[combined],[gain],[nullity],
{table}
)
#image("observations.svg",width:100%)
Gain is rank(M plus selected new rows)-rank(M) on the same original15columns. Witness count, distinct affine-equation count and independent information remain separate. New-row action on a complete old right kernel, full combined kernels and exact signed public-anchor projection are retained and checked. No outside-column subtraction is necessary because no outside unknown is introduced.

#pagebreak()
== Execution boundary and retained scope
Run #raw({json.dumps(a.run.name)}), exact native source #raw({json.dumps(execution['source_commit'])}), canonical protocol SHA256 #raw({json.dumps(export['protocol']['sha256'])}). Root froze this new protocol after A1 observations and before any new A2 branch. Exact inputs, explicit committed root release, source/input/interpreter/packages, actual canonical S3 checkpoint gate, exclusive ownership/PIDs and host are retained. Full EC1 curve identities: {', '.join(c['fixture']['ec1']['curve_uid'] for c in inputs['cells'])}.

Exit {execution['returncode']}, timeout {execution['timeout']}, source unchanged after {execution['source_unchanged_after']}. Shared-host diagnostic wall {execution['diagnostic_wall_seconds']:.3f}s, user CPU {execution['cpu_user_seconds']:.3f}s, system CPU {execution['cpu_sys_seconds']:.3f}s, peak RSS {execution['max_rss_bytes']}bytes, wall_valid=false. Producer field/group counts omit replay, linear algebra and complete S. Collection, per-arm elimination and verification are separate process-cost components, not distinct physical executions.

{phases}

The separate checker reconstructs every source/triple/sign-deck descriptor, canonical alias, status/digest and accepted row. Independent polynomial/group arithmetic verifies interpolation, squarefree residual division, exact residual E images, norm-completion labels, original E and auxiliary equations, affine distinctness/ranks, full old/combined kernels and old-kernel syndromes. It imports the earlier independent B2 descriptor lane, not the new producer or producer arithmetic. This is an implementation check, not independently staffed scientific review or a field-counter audit.

Collection snapshots precede elimination and final results precede separate verification. All attempts, accepted witnesses, misses, failures and unknown prefixes survive;2048 retained rows is a protective refusal gate, not truncation or a scalable memory claim. Raw data were committed/pushed before this report. Large closed JSON/journals are losslessly gzip encoded with original-byte hashes and official content-addressed S3 manifests. The v5 database is a fresh extension of the preserved v4 snapshot; historical reports and graphs stay unchanged. This graph covers this exact new panel.

Sources: A1 verified observations and native witnesses; original Prym principal-divisor/independent arithmetic, B1 historical preprocessing, B2/D1 scope/collision findings, PKM2016 sections3.1–3.4 (primary PDF SHA256 a53030a6cde720c354aebfb65b1eb01e07766ce2d26e543d77f2516c0a49ef5b). Negation and cancelling pushforwards are existing group/divisor facts; a short three-term equation is not a novel scalar action or isogeny. We have not measured a dedicated meet-in-the-middle triple-sum collector, complete S, matched rho gap or larger-field holdout. A local relation-space completion establishes no scalable or end-to-end speedup. No novelty or official scientific status is asserted; model readiness and full-ledger validation remain unclaimed.
'''
    (a.out/'report.typ').write_text(text);(a.out/'plotted-data.json').write_text(json.dumps(cells,indent=2)+'\n')
    typst.compile(str(a.out/'report.typ'),output=str(a.out/'report.pdf'),root=str(a.out.resolve()))
    print(json.dumps(dict(report=str(a.out/'report.pdf'),sha256=sha256((a.out/'report.pdf').read_bytes()).hexdigest())))


if __name__=='__main__':main()
