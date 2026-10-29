"""Complete paginated descriptive observations, with acyclic source links/digests.

The unified export and its findings must be written before render(). Reports
are terminal derived artifacts: this renderer never edits export.json or hashes
its own report artifacts into an input whose bytes the report then includes.
"""
from pathlib import Path
from collections import Counter
import hashlib
import json
import math
import textwrap


def unique(pairs):
    result={}
    for key,value in pairs:
        if key in result:raise ValueError('duplicate JSON key')
        result[key]=value
    return result


def nonfinite(value):
    raise ValueError('nonfinite JSON')


def finite_float(value):
    result=float(value)
    if not math.isfinite(result):raise ValueError('nonfinite JSON')
    return result


def loads(blob):
    return json.loads(blob,object_pairs_hook=unique,parse_constant=nonfinite,parse_float=finite_float)


def read(path):
    path=Path(path)
    if path.is_symlink() or not path.is_file() or path.stat().st_size>64<<20:raise ValueError('bounded regular report input required')
    return loads(path.read_bytes())


def compact(value):
    return json.dumps(value,sort_keys=True,allow_nan=False,separators=(',',':'))


def lines_for(label,value):
    """Human-readable structure; every scalar is retained without truncation."""
    if isinstance(value,dict):
        if not value:return [label+': {}']
        result=[label+':']
        for key,item in sorted(value.items()):result.extend(lines_for('  '+str(key),item))
        return result
    if isinstance(value,list):
        if not value:return [label+': []']
        result=[label+':']
        for index,item in enumerate(value):result.extend(lines_for('  ['+str(index)+']',item))
        return result
    return [label+': '+compact(value)]


def file_digest(path):
    digest=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1<<20),b''):digest.update(block)
    return digest.hexdigest()


def local(root,name):
    path=root/name
    if not isinstance(name,str) or path.is_symlink() or path.resolve().parent!=root.resolve():raise ValueError('unsafe report reference')
    return path


def uniform_summary(path):
    """Aggregate all retained rows; raw records remain linked by byte digest."""
    summary={'rows':0,'successes':0,'saturated':0,'zero_M':0,'M_histogram':Counter(),'exact_probability_histogram':Counter(),'cost_vectors':Counter(),'public_equations':0,'conditioning':set()}
    with path.open('rb') as stream:
        while True:
            line=stream.readline((64<<20)+1)
            if not line:break
            if len(line)>64<<20 or not line.endswith(b'\n'):raise ValueError('bounded complete uniform JSONL required')
            row=loads(line);value=row['uniform'];summary['rows']+=1
            summary['successes']+=value['success'];summary['saturated']+=value['saturated'];summary['zero_M']+=value['effective_M']==0
            summary['M_histogram'][str(value['effective_M'])]+=1
            summary['exact_probability_histogram'][compact(value['success_probability_exact'])]+=1
            summary['public_equations']+=value['public_equations'];summary['conditioning'].add(value['conditioning'])
            for family in ['primitive_vector','stream_counts']:
                for primitive,count in value.get(family,{}).items():summary['cost_vectors'][family+'/'+primitive]+=count
    return {key:(dict(value) if isinstance(value,Counter) else sorted(value) if isinstance(value,set) else value) for key,value in summary.items()}


def render(root):
    root=Path(root);export=read(root/'postrun-result.json')
    path=root/'analysis.json'
    if not path.exists():path=root/'partial-analysis.json'
    data=read(path) if path.exists() else {'per_curve_six_cell':[]}
    rows=data.get('per_curve_six_cell',[])
    report=['# Controlled follow-up retained observations','',
        'Operational export: '+export['status']+'. Scientific validity: not assessed.',
        'Observations only. Curve is the population unit; six cells share each confirmation trace.',
        'No scientific, significance, scalar-ordering or performance conclusion.',
        'Actual VM isolation remains unqualified. No qualified clocks or independent native worker counter replay.',
        'Native RSS, interpreter allocations, I/O and Python integer internals are unmetered.',
        'Undefined cost ratios remain null; zero costs remain zero. Requested backend/model/usage/probe are unverified unless an authenticated record explicitly supplies them.','',
        '## Operational failures and unified-export findings']
    report.extend(lines_for('Failures',export.get('errors',[])))
    report.extend(lines_for('Export findings',export.get('export_findings',[])))
    if (root/'export.validation.json').exists():report.extend(lines_for('Export validation',read(root/'export.validation.json')))
    report+=['','## Coverage and physical traces']
    for key in ['coverage','traces_by_curve','paired_discordants_t0e0_t1e2','uncertainty']:
        report.extend(lines_for(key,data.get(key,None)))
    grouped=[('Calibration (discovery and validation)',{'discovery','validation'}),('Confirmation A',{'confirmation-A'}),('Confirmation B',{'confirmation-B'}),('Explicit disclosed fixtures / other retained identifiers',set())]
    for title,stages in grouped:
        report+=['','## '+title]
        selected=[r for r in rows if r.get('stage','disclosed_fixture') in stages] if stages else [r for r in rows if r.get('stage','disclosed_fixture') not in {'discovery','validation','confirmation-A','confirmation-B'}]
        if not selected:report.append('No retained decoder rows for this section.')
        for row in selected:
            report.append('Curve '+row['curve_id']+'; cell '+row['cell']+'; successes / attempts '+str(row['successes'])+' / '+str(row['attempts']))
            report.extend(lines_for('  six-cell observation',row))
    report+=['','## Calibration: all retained arms and error/erasure histograms']
    if (root/'calibration.json').exists():report.extend(lines_for('calibration',read(root/'calibration.json')))
    else:report.append('Calibration unavailable; no values inferred.')
    report+=['','## Independent host references: BSGS cold/warm, nonzero uniform, null/support/duplicates/ties']
    if (root/'references.json').exists():
        references=read(root/'references.json');report.extend(lines_for('references',references))
        for curve in references.get('curves',[]):
            if curve.get('null_file'):
                null=read(local(root,curve['null_file']))
                mask=dict(null.get('mask_reference',{}));mask.pop('draws',None);mask.pop('orientation_multiplicities',None);mask.pop('free_pair_scalars',None)
                stats=null.get('retained_bank_statistics');stats=dict(stats) if stats is not None else None
                if stats is not None:
                    samples=stats.pop('reference_statistics',[])
                    stats['reference_statistics_histogram']=dict(Counter(compact(item) for item in samples))
                report.extend(lines_for('Null '+curve['curve_id'],{**{key:value for key,value in null.items() if key not in {'mask_reference','retained_bank_statistics'}},'mask_reference':mask,'retained_bank_statistics':stats}))
            if curve.get('uniform_file'):report.extend(lines_for('Uniform '+curve['curve_id'],uniform_summary(local(root,curve['uniform_file']))))
    else:report.append('References unavailable; no null eligibility, cold/warm result or uniform outcome inferred.')
    report+=['','## Cost scope and retained component vectors']
    for key in ['cost_scope','setup_components','physical_trace_components_once','unmetered','wall_valid','counter_replay_qualified']:
        report.extend(lines_for(key,data.get(key,None)))
    report.append('Uniform reference uses min(M,r-1)/(r-1) on distinct nonzero candidates; M-determination is candidate work excluded from reference costs. Saturation is explicit.')
    report+=['','## Raw and source links / SHA256 digests',
        'This terminal report binds existing inputs; report.md/report.svg/report.pdf are excluded from this index to avoid a self-hash cycle.']
    bundle=read(root/'export.json') if (root/'export.json').exists() else {}
    for item in bundle.get('files',[]):report.append('Raw link '+item['path']+' SHA256 '+item['sha256']+' bytes '+str(item['bytes']))
    for path in sorted(root.iterdir()):
        if path.is_file() and not path.is_symlink() and path.name not in {'report.md','report.svg','report.pdf'}:
            report.append('['+path.name+']('+path.name+') SHA256 '+file_digest(path)+' bytes '+str(path.stat().st_size))
    (root/'report.md').write_text('\n'.join(report)+'\n')
    import matplotlib
    matplotlib.use('Agg')
    matplotlib.rcParams['svg.hashsalt']='controlled-followup-report-v1'
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    fig,axes=plt.subplots(1,2,figsize=(12,5))
    for axis,stage,title in zip(axes,['confirmation-A','confirmation-B'],['Confirmation A','Confirmation B']):
        selected=[row for row in rows if row.get('stage')==stage]
        if selected:
            for index,row in enumerate(selected):
                if row['attempts']:axis.scatter(index,row['successes']/row['attempts'],s=12)
            axis.set(xlabel='Retained curve / cell index',ylabel='Success events / attempts',ylim=(-.02,1.02))
        else:axis.text(.5,.5,'No retained rows',ha='center',va='center',transform=axis.transAxes)
        axis.set_title(title+' (shared traces within each curve)')
    fig.suptitle('Operational export: '+export['status']+'; descriptive only; wall_valid=false')
    fig.tight_layout();fig.savefig(root/'report.svg')
    wrapped=[]
    for line in report:
        wrapped.extend(textwrap.wrap(line,width=108,break_long_words=True,break_on_hyphens=False,replace_whitespace=False,drop_whitespace=False) or [''])
    chunks=[wrapped[index:index+65] for index in range(0,len(wrapped),65)] or [[]]
    with PdfPages(root/'report.pdf') as pdf:
        for index,chunk in enumerate(chunks,1):
            page=plt.figure(figsize=(8.3,11.7));page.text(.055,.96,'\n'.join(chunk),va='top',fontsize=7,fontfamily='DejaVu Sans Mono',linespacing=1.25)
            page.text(.055,.025,'Controlled follow-up | retained observations | page '+str(index)+' / '+str(len(chunks)+1),fontsize=7)
            pdf.savefig(page);plt.close(page)
        pdf.savefig(fig)
    plt.close(fig)
