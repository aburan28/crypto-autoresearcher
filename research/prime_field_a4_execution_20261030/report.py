"""Render a write-once holdout report from the admitted retained records."""
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
    options=[p for p in (path,Path(str(path)+'.gz')) if p.is_file()]
    if len(options)!=1: raise ValueError('missing/ambiguous retained record')
    with (gzip.open(options[0],'rt') if options[0].suffix=='.gz' else options[0].open()) as stream: return json.load(stream)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('run','out'): parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args();args.out.mkdir(parents=True,exist_ok=False)
    analysis=load(args.run/'analysis.json');execution=load(args.run/'execution.json');export=load(args.run/'export.json');generated=load(args.run/'raw/generated.json')
    cells=analysis['cells'];definitions=generated['cells'];release=load(args.run.parent.parent/'release.json');native={c['id']:load(args.run/'raw'/(c['id']+'.json')) for c in definitions}
    plt.rcParams.update({'svg.fonttype':'none','font.size':9});fig,axes=plt.subplots(2,2,figsize=(8.8,4.2))
    for ax,definition in zip(axes.flat,definitions):
        values=[c for c in cells if c['cell_id']==definition['id']];width=values[0]['base_columns']
        ax.plot([c['prefix'] for c in values],[c['base_rank'] for c in values],marker='o',color='#2166ac',label='source-only rank')
        ax.axhline(width,color='#777777',linestyle='--',label='projected columns')
        for c in values: ax.annotate(str(c['base_rank']),(c['prefix'],c['base_rank']),xytext=(0,4),textcoords='offset points',ha='center',fontsize=8)
        ax.set_xticks([0,16,64]);ax.set_ylim(-1,width+3);ax.set_title(definition['id']);ax.set_ylabel('dimensions');ax.set_xlabel('public-source prefix');ax.spines[['top','right']].set_visible(False)
    fig.suptitle(args.run.name+': four prospective holdouts',fontsize=10);fig.tight_layout();fig.savefig(args.out/'observations.svg');plt.close(fig)
    path=args.out/'observations.svg';path.write_text('\n'.join(s.rstrip() for s in path.read_text().splitlines())+'\n')
    table='\n'.join(','.join('['+str(v)+']' for v in (c['cell_id'],c['prefix'],c['base_rank'],c['base_nullity'],c['source_rows'],c['single_targets'],c['joint_targets'],c['joint_base_nullity']))+',' for c in cells)
    fixtures='\n'.join('- '+c['id']+': p='+str(c['fixture']['p'])+', b='+str(c['fixture']['b'])+', r='+str(c['fixture']['r'])+', atoms='+str(len(c['fixture']['factor_base']))+'. Full EC1 UID: '+c['fixture']['ec1']['curve_uid']+'.' for c in definitions)
    target_summary=[];recovered=[]
    for definition in definitions:
        value=native[definition['id']];last=value['prefixes'][-1]
        target_summary.append(','.join('['+str(v)+']' for v in (definition['id'],len(value['rows']),len(value['target_collection']['rows']),len({v['target_index'] for v in value['target_collection']['rows']}),
                              sum(bool(v['bounded_multiple_matches']) for v in value['collision_diagnostics']),sum(v['direct_public_scalar']is not None for v in value['collision_diagnostics'])))+',')
        for identified in last['joint_recoveries']:
            if identified['identifiable']:
                diagnostic=value['collision_diagnostics'][identified['target_index']]
                recovered.append(definition['id']+' target'+str(identified['target_index'])+', scalar'+str(identified['scalar'])+', bounded multiple matches '+str(len(diagnostic['bounded_multiple_matches'])))
    text=f'''#set page(paper:"a4",margin:16mm)
#set text(size:9pt)
= Larger-field holdouts and independent targets
Observations from #raw({json.dumps(args.run.name)}). Four new eligible curves were chosen prospectively by the frozen hash/candidate rule: two each over8191(base16) and65537(base32). Generation and all eligibility rejections occurred after native admission. Base points use the existing first-distinct x² norm rule; generators use the first rational E point. Neither relation yield nor rank nor target outcome selected a curve. These fields exceed the earlier4099field but remain small. Field size and base size change together, so this is not a one-factor scaling study.

#image("observations.svg",width:100%)
#table(columns:(auto,auto,auto,auto,auto,auto,auto,auto),inset:3pt,
[fixture],[prefix],[base rank],[base nullity],[rows],[single Q],[joint Q],[base nullity after target cancellation],
{table}
)
Single Q counts targets with at least one natural row satisfying vN=0 on the source-only prefix M. Joint Q uses all eight target columns and carried row-weight certificates. The last column subtracts target-column rank before measuring remaining base uncertainty. All early-single and early-joint counts are zero in this panel. The one recovered target appears only on the fixture whose source matrix has full projected rank. Rank deficiency and misses remain measured outcomes.

#pagebreak()
== Target generation, decomposition and certificates
Eight independent public targets per curve were generated by hashing the full EC1 UID, target index and counter to x, then choosing the minimum rational y. No target scalar labels were drawn. Rejected nonrational/duplicate candidates are retained; all source/base coincidences stay, without redraw. This is an exact specified canonical-point distribution, not a standardized hash-to-curve or a claim of uniformity over every prime-order curve/point.

#table(columns:(auto,auto,auto,auto,auto,auto),inset:4pt,
[fixture],[source rows],[target rows],[targets with a direct decomposition],[targets with bounded multiple matches],[direct public-source collisions],
{chr(10).join(target_summary)}
)
Recovered public scalars (derived outputs only, each checked by multiplication): {('; '.join(recovered)) or 'none'}.

Target queries use Q itself. The separately charged prospective diagnostic compares [t]Q, t=1..64, against signed [s]P, s=1..64, and records signed base coincidences. A bounded nonmatch excludes only this fixed diagnostic; it proves no general absence of public coincidences. Diagnostic scalar labels are not fed into the prefix systems or used to choose cases. Decomposition, individual identifiability, joint recovery and known public collisions remain separate quantities.

Each fixture has one full signed-pair table, reused for64source points and8targets. All buckets and infinity keys are kept; accepted triples have j < k < l and independently chosen signs. Total physical collection:4928pair entries,12288source queries,1536target queries. Prefix0/16/64 are analyses of one collected stream, not three independently executed cold collectors. The signed public projection knows all64public source multiples at every prefix; prefix0 means zero collected equations, not zero public information.

The independent oracle enumerated every signed distinct triple once per fixture,88320triples total, mapping its E sum to all source and target points. It separately reconstructs eligibility, canonical EC1/base/generator, all target recipe counters, all pair entries and query buckets, source/target rows, affine consistency/ranks, complete kernels, target-unit and natural-row weight certificates and final public equations. This is an independent implementation check, not staffed scientific review or a producer field-counter audit. Complete semantic coverage does not mean source-times-triple enumerations were physically repeated.

== Cost coverage
Every candidate trace and generation diagnostic is retained; generation checked {analysis['generation_verification']['candidate_records']}candidates and {analysis['generation_verification']['order_point_tests']}order point tests. Candidate order/base construction uses the old generation implementation and only partial primitive counters. Per-fixture records separately retain setup/sign/source construction, pair building, source queries/extraction, target generation/queries/extraction/certification, public-multiple diagnostics, and each prefix projection/normalization/elimination/kernel/carried-certificate/public verification. One physical supervised panel contains four streams and12prefix records. Shared collection counters belong once to prefix0; disjoint prefix costs are recorded once in the backend. Cumulative snapshots and outer clocks are inclusive views and must not be added again.

Fp, Fr, group and logical units overlap and are not a scalar total. Inversion internals, Python hash/sort/serialization/storage/allocator/OS work and independent verifier arithmetic lack a complete weighted model. All clocks are shared-host diagnostics with wall_valid=false. The observed vector is not complete S, a calibrated cost per target, a matched rho comparison or an end-to-end speedup claim.

#pagebreak()
== Execution, source and retained scope
Exact scientific source #raw({json.dumps(execution['source_commit'])}); canonical protocol SHA256 #raw({json.dumps(export['protocol']['sha256'])}). Rules-only inputs and exact{len(release['source_sha256'])}source plus one rules file and interpreter/package bindings, frozen prospective protocol, explicit root release, actual canonical S3 checkpoint/gate and exclusive ownership all preceded generation.

Exit {execution['returncode']}; timeout {execution['timeout']}; source unchanged {execution['source_unchanged_after']}; panel complete {analysis['panel_complete']}; unknown cells {analysis['unknown_cells']}. Diagnostic wall {execution['diagnostic_wall_seconds']:.3f}s, userCPU {execution['cpu_user_seconds']:.3f}s, systemCPU {execution['cpu_sys_seconds']:.3f}s, RSS {execution['max_rss_bytes']}bytes; wall_valid=false. Oneprocess/thread,2GiB/21600s protective watchdog;2048row/4096pair/128candidate gates refuse with retained prefixes, never truncation or rank/recovery stops.

{fixtures}

Generated fixtures are saved before their separate eligibility check; collection snapshots precede all prefix recovery; final results precede the independent checker. Raw data were committed/pushed before this report. Four large final/collection JSON files are losslessly gzip encoded with original/archive hashes; other raw objects retain their encoding. Official content-addressed S3 manifests bind all large retained records. The v7database extends a byte-preserved v6 parent, adding these four curves/bases, source/target witnesses,32public targets and12prefix certificate records. Earlier reports/databases remain intact. This graph is a new scoped view; no canonical scientific verdict changes.

Primary source PKM2016sections3.1–3.4 (https://people.maths.ox.ac.uk/petit/files/16PKC_primeECDLP.pdf) separates precomputation, relation solving and linear algebra. A3 and D1 results/literature supply the direct-interface and public-collision context. Complete references, assumptions and source sections read are in literature.md. Known generic-table cost obstructions remain; this panel asserts no novel symmetry, general rank law, scalable attack, official scientific status change, verified configured model or full-ledger pass. Software preparation used marked p101 controls only. Sparse full-ledger validation refused off-disk records and was not claimed passed.

The next discriminating check is a separately frozen source-selection comparison on these holdouts: small scalar windows versus independently hashed public sources, with fixed original columns/anchors and all collection costs retained. A broader base or extra source pool is not credited merely for introducing unknowns. More targets alone do not imply recovery while the old kernel remains; the recorded target-row syndromes locate that question precisely. Those follow-up trials were not executed in this panel.
'''
    (args.out/'report.typ').write_text(text);(args.out/'plotted-data.json').write_text(json.dumps(dict(cells=cells,fixture_ids=[v['id'] for v in definitions]),indent=2)+'\n')
    typst.compile(str(args.out/'report.typ'),output=str(args.out/'report.pdf'),root=str(args.out.resolve()))
    print(json.dumps(dict(report=str(args.out/'report.pdf'),sha256=sha256((args.out/'report.pdf').read_bytes()).hexdigest())))


if __name__=='__main__': main()
