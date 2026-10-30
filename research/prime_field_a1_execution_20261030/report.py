"""Descriptive write-once report from the sealed A1 export; no new science run."""
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
    with (gzip.open(path,'rt') if path.suffix=='.gz' else path.open()) as f:return json.load(f)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('run','inputs','out'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    analysis=load(a.run/'analysis.json');execution=load(a.run/'execution.json');export=load(a.run/'export.json');inputs=load(a.inputs)
    definitions={c['id']:c for c in inputs['cells']};cells=analysis['cells'];fig,axes=plt.subplots(1,2,figsize=(9,2.9))
    plt.rcParams.update({'svg.fonttype':'none'})
    labels=[c['cell_id']+'\n'+c['arm'] for c in cells]
    values=[c['accepted_witnesses'] for c in cells];axes[0].bar(range(6),[v or 0 for v in values],color='#2166ac')
    for i,v in enumerate(values):axes[0].annotate('unknown' if v is None else str(v),(i,v or 0),xytext=(0,3),textcoords='offset points',ha='center',fontsize=8)
    axes[0].set_title('Accepted witnessed equations');axes[0].set_ylabel('witnesses')
    direct=[c['direct_base_gain'] for c in cells];cross=[c['cross_row_cancellation_gain'] for c in cells]
    axes[1].bar(range(6),[v or 0 for v in direct],label='Already base-only (U=0)',color='#2166ac')
    axes[1].bar(range(6),[v or 0 for v in cross],bottom=[v or 0 for v in direct],label='Needs cross-row cancellation',color='#c85e18')
    for i,c in enumerate(cells):axes[1].annotate('unknown' if c['delta'] is None else str(c['delta']),(i,c['delta'] or 0),xytext=(0,3),textcoords='offset points',ha='center',fontsize=8)
    axes[1].set_title('Additional base rank after eliminating U');axes[1].set_ylabel('dimensions');axes[1].legend(fontsize=6,loc='upper left')
    for ax in axes:
        ax.set_xticks(range(6),labels,fontsize=7);ax.spines[['top','right']].set_visible(False);ax.set_ylim(0,max(1,ax.get_ylim()[1])*1.3)
    fig.suptitle(a.run.name+': fixed nested residual pools, all six cells',fontsize=10);fig.tight_layout();fig.savefig(a.out/'observations.svg');plt.close(fig)
    svg=a.out/'observations.svg';svg.write_text('\n'.join(v.rstrip() for v in svg.read_text().splitlines())+'\n')
    display=lambda value:'unknown' if value is None else str(value)
    table='\n'.join(','.join('['+display(v)+']' for v in (c['cell_id'],c['arm'],c['known_public_pool_points'],c['accepted_witnesses'],c['distinct_equations'],c['outside_unknown_columns'],c['outside_rank'],c['stacked_rank'],c['base_rank_before'],c['delta'],c['direct_base_gain'],c['cross_row_cancellation_gain']))+',' for c in cells)
    phases='\n'.join('- '+str(v['cell_id'])+' '+str(v.get('arm'))+' '+v['phase']+': '+v['status']+', CPU '+format(v['cpu_seconds'],'.3f')+'s.' for v in export['backend_record']['phase_records'])
    source=f'''#set page(paper:"a4",margin:16mm)
#set text(size:9pt)
= Bounded residual-point partial relations
Observations only. The two original p4099 E curves, sixteen native atoms, fifteen projected base unknowns, original64-source schedules and historical M remain fixed. Only residual acceptance broadens: points must lie in the original base or the first0,16,32 independently hashed pool representatives. Constraints stay in the original base. Each curve has ONE pool32 branch stream; the three nested arms filter the same witnesses by geometric pool ordinal, even if coefficients subsequently cancel. No base enlargement or new target is supplied.

Each32-point pool uses SHA256(domain|fullEC1curveUID|index|counter), domain prime-field-residual-pool/20261030/v1, canonical-y first rational nonidentity subgroup point outside the old base and previous slots, counter bound10000. No scalar labels are generated. Known public-source coincidences are retained and projected as known values. Hashing, subgroup checks and all rejected counters are retained. The x=0 completion and pole(3,3) cubic law stay fixed; lower-degree or repeated intersections remain rejected.

Panel complete: {analysis['panel_complete']}; physical collection branches {analysis['physical_collection_attempts_observed']}; full separate replay branches {analysis['physical_replay_attempts_observed']}. The six logical arm records are not six collections. Shared counters are charged only to smooth records; process resources once in the backend. No clock or attempt duplication should be added across nested arms.

#table(columns:(auto,auto,auto,auto,auto,auto,auto,auto,auto,auto,auto,auto),inset:2pt,
[case],[arm],[known pool],[rows],[equations],[U cols],[rank U],[stacked],[M rank],[Delta],[direct],[cross],
{table}
)
#image("observations.svg",width:100%)
Delta=rank([[M,0],[B,U]])-rank(U)-rank(M). A naive stacked-rank increase counts outside unknowns and is not additional base information. Direct gain uses M plus rows whose projected U is zero; cross gain is Delta minus direct gain. Thus known-source pool coincidences or cancellation within one row are distinguished from information requiring cancellation across multiple rows. Every original-row weight, base-only RHS, old-kernel syndrome and complete cancellation kernel is retained and independently checked.

#pagebreak()
== Execution, verification and retained costs
Run #raw({json.dumps(a.run.name)}), source #raw({json.dumps(execution['source_commit'])}), canonical protocol SHA256 #raw({json.dumps(export['protocol']['sha256'])}). Explicit committed root release, actual canonical S3 checkpoint gate, source/input/interpreter/package locks and exclusive ownership preceded all native pool generation. The exact inputs record full EC1 identities: {', '.join(c['pool_curve_uid'] for c in inputs['cells'])}.

Native exit {execution['returncode']}, timeout {execution['timeout']}, source unchanged after {execution['source_unchanged_after']}. Shared-host diagnostic wall {execution['diagnostic_wall_seconds']:.3f}s, user CPU {execution['cpu_user_seconds']:.3f}s, system CPU {execution['cpu_sys_seconds']:.3f}s, peak RSS {execution['max_rss_bytes']}bytes; wall_valid=false. Producer field/group counts exclude separate replay, elimination/serialization and complete S. Pool construction, collection, per-arm elimination and verification phases are separately retained; they are components of one process, not independent executions or calibrated cost comparisons.

{phases}

The separate implementation reconstructs every hash selection/counter, all branch statuses/digests and accepted witnesses, original E and auxiliary principal sums, signed public-anchor projection, affine ranks/complete kernels, exact Delta and every cancellation's weights/point equation. It imports the earlier independent B2 descriptor/arithmetic lane, not the new producer or producer arithmetic. This is an implementation check, not staffed independent scientific review or a field-counter audit. Protective gates2048 accepted partial rows and32 outside columns refuse with retained prefixes, never truncate; they imply no scalable elimination bound.

Raw .collection snapshots precede elimination, final result precedes separate verification. Failure/timeout prefixes and unknown cells remain explicit. Data were committed/pushed before this report. Closed large JSON/journals are losslessly gzipped with original/archive byte hashes; adjacent store manifests retain remote objects. The fresh v4 SQLite receipt binds the original v3 parent and this export; prior database bytes and historical graphs remain unchanged. This graph covers only this fixed panel. Software positives/corruptions preceded freeze; a no-op test mutation was corrected before native data, with its correction retained. Full-ledger validation was refused in the sparse checkout and is not claimed; no ledger status was changed.

Sources: prior B1/B2/D1 observations and native/checker source, original relation_quality outside-cancellation criterion and merged Prym matrix review; Petit/Kosters/Messeng PKC2016 sections3.1–3.4, primary PDF SHA256 a53030a6cde720c354aebfb65b1eb01e07766ce2d26e543d77f2516c0a49ef5b. Relation generation and linear algebra have distinct costs. Outside-column elimination is existing linear algebra, not a novelty claim. Neither a larger witness pool nor a local rank change establishes a complete ECDLP speedup. Conclusions cover these fixed pools/curves only; complete S, asymptotic advantage, larger-field behavior and official scientific promotion remain unestablished.
'''
    (a.out/'report.typ').write_text(source);(a.out/'plotted-data.json').write_text(json.dumps(cells,indent=2)+'\n')
    typst.compile(str(a.out/'report.typ'),output=str(a.out/'report.pdf'),root=str(a.out.resolve()))
    print(json.dumps(dict(report=str(a.out/'report.pdf'),sha256=digest(a.out/'report.pdf'))))


def digest(path):return sha256(path.read_bytes()).hexdigest()


if __name__=='__main__':main()
