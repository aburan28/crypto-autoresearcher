"""Report the completed shifted-cover admissibility census from retained rows."""
import argparse
import gzip
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import typst


def load(path):
    if path.is_file():return json.loads(path.read_text())
    with gzip.open(str(path)+'.gz','rt') as stream:return json.load(stream)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',type=Path,required=True);parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();args.out.mkdir(parents=True,exist_ok=False)
    raw=load(args.run/'raw/survey.json');analysis=load(args.run/'analysis.json')
    execution=load(args.run/'execution.json');export=load(args.run/'export.json');host=load(args.run/'host.json')
    plt.rcParams.update({'font.size':9,'svg.fonttype':'none'})
    fig,axes=plt.subplots(1,2,figsize=(8.6,2.4));histograms=[]
    for axis,cell in zip(axes,raw['cells']):
        counts=[sum(row['base_square_mask'].count('1')==k for row in cell['rows']) for k in range(17)]
        histograms.append(dict(fixture_uid=cell['fixture_uid'],counts=counts))
        axis.bar(range(17),counts,color=['#2166ac']*16+['#238b45'])
        axis.set(yscale='log',xlabel='Original atoms with rational cover lifts',ylabel='Shifts (count; log scale)',
                 title=f"p={cell['p']}, a={cell['a']}, b={cell['b']}; all4099 shifts")
        axis.set_xticks([0,4,8,12,16]);axis.spines[['top','right']].set_visible(False)
    fig.suptitle(args.run.name+': membership only; no relations collected',fontsize=10)
    fig.tight_layout();fig.savefig(args.out/'admissibility.svg');plt.close(fig)
    svg=args.out/'admissibility.svg'
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
    (args.out/'histogram-data.json').write_text(json.dumps(histograms,indent=2)+'\n')
    rows=[]
    for cell,summary in zip(raw['cells'],analysis['cells']):
        if cell['fixture_uid']!=summary['fixture_uid']:raise ValueError('report fixture order differs')
        rows.append(','.join('['+str(v)+']' for v in (cell['b'],summary['frames'],summary['eligible_frames'],
            summary['nonzero_eligible_frames'],summary['singular_frames'],summary['public_source_lifts_for_eligible']))+',')
    lists='\n'.join(f"- b={c['b']}: eligible h={c['eligible_h']}." for c in raw['cells'])
    costs='\n'.join(f"- b={c['b']}: {c['counters']['modular_pow_calls']} explicit membership powers; {c['counters']['setup_group_ops']} setup group calls." for c in raw['cells'])
    q=lambda v:json.dumps(str(v))
    source=f'''#set page(paper:"a4",margin:16mm)
#set text(size:9.5pt)
= Common-atom shifted-cover survey
Observations only. One physical complete admissibility survey; relation-collection attempts: zero. No performance claim or scientific-state transition is made.

Run #raw({q(args.run.name)}). The original two E curves and sixteen-atom bases remain fixed: p=4099,a=2,b=13,r=4021,P=(0,264), and b=16,r=4111,P=(0,4). For C_h: y²=f(x²+h), an atom (u,y) lifts exactly when u-h is square or zero. Every h=0 through4098 is retained; singular f(h)=0 is excluded from admissibility. All64 original public sources are assessed without selecting by relation yield. h=0 is the historical positive control.

#table(columns:(auto,auto,auto,auto,auto,auto),inset:4pt,
[b],[frames],[eligible],[nonzero eligible],[singular],[source points with lifts],
{chr(10).join(rows)}
)
{lists}

Exploratory subset readout from the retained masks: the best nonzero shift covers15/16 atoms for b=13 (h=3437), and14/16 for b=16 (h=3279,3343,3437,3769). These are all coverage-maximizing ties; no relation yield was measured or used to choose them. A same-subset h=0 versus h collector comparison remains unrun.

#image("admissibility.svg",width:100%)
Histogram counts are derived by counting recorded membership bits. Zero means no observed shift in that exact bin; no broader curve-population model or interval is implied. Source-point counts include a zero lift once and are not signed deck-lift multiplicities.

Panel complete: {analysis['panel_complete']}; unknown fixtures: {analysis['unknown_cells']}. All8198 coefficient/membership rows passed a full roots-set reference and128 source points were checked by separate arithmetic, including curve-order recounts. The reference uses polynomial convolution for coefficients. It is an implementation cross-check, not independent scientific review. Two survey cells and two reference-method cells share one physical process; duplicate object counts are not added.

== Resources and source boundary
Exit {execution['returncode']}; timeout {execution['timeout']}; source unchanged {execution['source_unchanged_after']}. User CPU {execution['cpu_user_seconds']:.3f}s, system CPU {execution['cpu_sys_seconds']:.3f}s, wall {execution['diagnostic_wall_seconds']:.3f}s, peak RSS {execution['max_rss_bytes']} bytes. Host {host['cpu_model']}; wall_valid=false. Explicit membership counters omit helper primality guards, coefficient arithmetic, reference work and complete S.
{costs}

Source commit #raw({q(execution['source_commit'])}). Protocol canonical SHA256 #raw({q(export['protocol']['sha256'])}). The committed protocol/release, input/interpreter/source locks, actual S3 gate, owner/PIDs, raw masks/coefficients, source points, phase records and export are beside the run. Lossless compression binds original bytes in archive-encoding.json. Data were published before this report.

== Follow-through and limits
This complete finite survey determines common-atom frame admissibility only on the two exact bases. An admissible shifted frame still needs a separately frozen collector with unchanged E/base/log columns/source schedule, corrected x⁴ and auxiliary terms, pole/residual/sign checks and full charged cost. A finite absence of a nonzero common-atom shift says nothing about declared subsets, other bases, other covers or function spaces. Natural-target recovery and partial-column cancellation remain separate tests.

Sources: shifted-covers.md (derived quotient identities), original Prym Context and fixed fixtures, cover-survey literature.md, PKM2016 sections3.1–3.2 (retrieved primary, solver/linear-algebra costs remain charged). Full EC1/fixture identities remain in raw cells and inputs. Historical graphs remain unchanged; this new graph covers only this survey. No isogeny, Jacobian or subgroup-eigenvalue certificate is asserted.
'''
    (args.out/'report.typ').write_text(source)
    typst.compile(str(args.out/'report.typ'),output=str(args.out/'report.pdf'),root=str(args.out.resolve()))
    print(json.dumps(dict(report=str(args.out/'report.pdf'))))


if __name__=='__main__':main()
