#!/usr/bin/env python3
"""Post-data descriptive report of retained counters; performs no solver calls."""
import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
import artifact_store as store
import experiment_protocol as ep


def render(out):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import typst
    export=ep.read_json(out/'export.json')
    protocol=ep.read_json((out/export['protocol']['path']).resolve())
    findings=ep.schema_errors(export,'experiment.export/v1') or ep.lint_export(export,protocol,out,True)
    if findings:raise ValueError('\n'.join(findings))
    rawdir=ROOT/'experiments/EXP-PNEXT-624f41/runs/RUN-PNEXT-ad1645'
    raw=store.read_json(rawdir/'raw-result.json')
    receipt=store.read_json(rawdir/'execution-receipt.json')
    launch=store.read_json(rawdir/'launch.json')
    supplemental=ep.read_json(ROOT/'coordination/prime_sat_followup_20261029/supplemental-check-result.json')
    if supplemental['result']['valid'] is not True:raise ValueError('supplemental replay did not pass')
    rows={r['arm']:r['measurements']['counted'] for r in export['runs']}
    names=['quartic','membership','quadratic','quadratic_aa']
    coeff=['leaf_sat','prefix_univariate_gcd','exhaustive_reference','aa_reverse_prefix']
    for name in ('report.md','report.typ','report.pdf','diagram.svg','report-data.json','renderer.py'):
        if (out/name).exists():raise FileExistsError(out/name)
    data={'run_id':rawdir.name,'counts':rows,'supplemental':supplemental,'native_receipt':receipt,
          'protocol_hash':protocol['freeze']['protocol_sha256'],'resources':raw['resources'],
          'interpretation':'Post-data descriptive observations; native invalid_output unchanged.'}
    (out/'report-data.json').write_text(json.dumps(data,indent=2)+'\n')
    shutil.copyfile(__file__,out/'renderer.py')
    fig,axes=plt.subplots(1,3,figsize=(12,4),layout='constrained')
    ax=axes[0]
    ax.bar(range(4),[rows[n]['phase_search_search_events_sat_candidates'] for n in names],color='#2b708e')
    ax.set_xticks(range(4),['Quartic','Membership','Quadratic','Reverse A/A'],rotation=30,ha='right')
    ax.set_ylabel('SAT candidates, sum over 106 cells');ax.set_title('Coordinate search')
    ax=axes[1]
    ax.bar(range(4),[rows[n]['phase_search_search_arithmetic_coefficient_multiplications'] for n in names],color='#ca732b')
    ax.set_xticks(range(4),['Quartic','Membership','Quadratic','Reverse A/A'],rotation=30,ha='right')
    ax.set_ylabel('Instrumented search field multiplications');ax.set_title('Algebraic search work')
    ax.ticklabel_format(axis='y',style='sci',scilimits=(0,0))
    ax=axes[2];bottom=[0,0,0]
    for phase,color in [('construction','#6baed6'),('search','#2b708e'),('proof_check','#ca732b'),('reconstruction','#7b4173')]:
        vals=[rows[n].get('phase_'+phase+'_polynomial_coefficient_multiplications',0) for n in coeff[:3]]
        ax.bar(range(3),vals,bottom=bottom,label=phase.replace('_',' '),color=color)
        bottom=[a+b for a,b in zip(bottom,vals)]
    ax.set_xticks(range(3),['Leaf SAT','Prefix gcd','Reference'],rotation=30,ha='right')
    ax.set_ylabel('Instrumented polynomial coefficient multiplications');ax.set_title('Coefficient phases, six cells')
    ax.ticklabel_format(axis='y',style='sci',scilimits=(0,0));ax.legend(fontsize=7)
    for ax in axes:ax.grid(axis='y',alpha=.15)
    fig.suptitle('RUN-PNEXT-ad1645: native validation failed; supplemental artifact replay passed',fontsize=10)
    fig.savefig(out/'diagram.svg');plt.close(fig)
    svg=out/'diagram.svg'
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
    intro=('Observations only. The single native trial completed data collection but its frozen checker failed on an explicit-zero versus absent census counter. '
           'The original invalid_output receipt is preserved. A separate post-data checker changed only sparse counter equality and passed all retained model, certificate, witness and declared chart checks. '
           'This is exploratory replay, not a successful native run, independent scientific review, or hypothesis promotion.')
    scope=('Encoding inputs: E/F_17:y^2=x^3+2x+2 (order 19), E/F_97:y^2=x^3+x+4 (order 89); two- and three-bit x domains; all affine target x representatives with least nonzero y. '
           'Each arm has 106 cells and the same complete projected census, 85 coordinate pairs in aggregate. Search is separately bounded at degree 2, 256 rows, 128 SAT candidates, 512 PC calls. '
           'Quadratic input degree does not establish lower degree of regularity. These previously seen finite fixtures provide no held-out or cryptographic-scale inference.')
    status=('Native flow: one trial attempted, producer return 0, checker return 1. Ten aggregate export rows remain failed/excluded with verification_pass=0. '
            'Supplemental replay: 424 encoding arms (406 complete searches, 18 censored), 24 coefficient arms, 14,324 encoding certificates, 29,478 coefficient prefix certificates and 500,848 leaf certificates passed. '
            'The nine original synthetic controls and five sparse-counter integrity controls passed. Raw S3 objects were verified by fresh HEAD/GET/hash; native snapshot archival and scientific review remain pending.')
    md=['# Certified SAT follow-up: retained observations',intro,'',
        'Experiment `EXP-PNEXT-624f41`; hypothesis `H-PNEXT-8f9166`; goal `GOAL-PFDR-fd09e0`; run `RUN-PNEXT-ad1645`.',
        status,'',scope,'',
        '| Encoding | Complete/censored | SAT candidates | Search field multiplications | Online certificate multiplications | Final certificate multiplications | Full-census assignments |',
        '|---|---:|---:|---:|---:|---:|---:|']
    for n in names:
        r=rows[n]
        md.append(f"| {n} | {r['search_complete']}/{r['search_censored']} | {r['phase_search_search_events_sat_candidates']:,} | {r['phase_search_search_arithmetic_coefficient_multiplications']:,} | {r['phase_search_online_certificate_check_coefficient_multiplications']:,} | {r['phase_verification_coefficient_multiplications']:,} | {r['phase_census_boolean_assignments_visited']:,} |")
    md+=['','Construction adds 22,908 field multiplications for each quartic arm or 10,729 for each quadratic arm. Membership additionally uses 8,480 field-power calls and 23,744 transform subtractions. Every arm reconstructs all 85 census witnesses, with 170 inverse calls and 85 group additions. Other primitive counters are retained in report-data.json; they are not discarded or converted into a mixed cost total.',
         '', 'Coefficient inputs: F_17, the same curve, d=8 and 16, c=1, targets (0,6),(3,1),(5,1). All four arms complete all six cells with 278 coefficient models. Recovered relations partition as 155 generic plus 123 target-overlap fallback relations. Completeness is for five distinct affine x coordinates with U dividing X^d-1. Repeated x coordinates and identity summands are outside this predicate.',
         '', '| Coefficient arm | Full assignments checked | Prefixes | Construction mult. | Search mult. | Proof-check mult. | Reconstruction mult. |',
         '|---|---:|---:|---:|---:|---:|---:|']
    for n in coeff:
        r=rows[n]
        values=[r.get('phase_'+phase+'_polynomial_coefficient_multiplications',0) for phase in ('construction','search','proof_check','reconstruction')]
        md.append('| '+n+' | '+f"{r.get('search_event_coefficient_assignments_evaluated',0):,}"+' | '+f"{r.get('phase_search_prefixes_visited',0):,}"+' | '+' | '.join(f'{v:,}' for v in values)+' |')
    md+=['', 'The prefix arm checks 29,478 three-coefficient prefixes and rejects 29,203 whole prefixes, covering 496,451 assignments. Guarded gcd clauses reject another 4,397 values; 278 full coefficient models remain. It still evaluates 501,126 univariate root candidates, so it does not remove that enumeration. Forward/reverse prefix order produces identical field-arithmetic counts; SAT decisions are 3,378 versus 3,387. The quadratic forward/reverse order changes search multiplication counts despite equal completion, showing order sensitivity.',
         '', 'Each coefficient arm also pays 2,240 exceptional signed-point tuple enumerations, 11,200 Jacobian group-addition calls and 2,128 inverse calls in fallback. Shared reference census and the separate supplemental checker are recorded separately. Instrumented coefficient operations omit some Python and group-formula work; these totals are not complete CPU or end-to-end costs. No timing advantage is claimed.',
         '', '![Recorded counters and explicit scope](diagram.svg)',
         '', 'All table and graph values are retained integer counters or exact sums over fixed cells. No statistical uncertainty interval applies. No values are obtained by new scientific search. The frozen numerical extraction is unchanged; the failure adapter, sparse-counter correction and this renderer are explicitly post-data. Protocol/export schema validation does not turn the failed run into confirmatory evidence.',
         '',f"Code/launch authority: `{launch['authority']['commit']}`. Protocol hash: `{protocol['freeze']['protocol_sha256']}`. Config hash: `{raw['config_sha256']}`.",
         f"Started `{receipt['started_at']}`, finished `{receipt['finished_at']}`. Exact command: `{json.dumps(launch['argv'])}`.",
         f"Producer resource telemetry: `{json.dumps(raw['resources'],sort_keys=True)}`. Independent checker is excluded from this producer telemetry; no matched timing inference.",
         '', 'Frozen parameters, source/input hashes, host metadata, certificates and journals are linked by [export.json](export.json). Supplemental checker receipt and its code are linked there separately. See [report-data.json](report-data.json) for every phase/primitive counter.',
         '', 'Literature context: [Kosters and Yeo, Notes on summation polynomials](https://arxiv.org/html/1503.08001); [Hader et al., MCSat over finite fields](https://arxiv.org/html/2402.17927v1). These motivate exact encodings and univariate conflicts; this run claims neither novelty of those mechanisms nor reproduction of their performance.',
         '', 'The prior partial-matrix and two-bit-backdoor sweeps were not expanded. No current result establishes a general ECDLP algorithm, unknown-scalar recovery, or a degree-of-regularity bound. Canonical research graphs remain unchanged because no scientific decision was made.']
    (out/'report.md').write_text('\n'.join(md)+'\n')
    q=lambda s:json.dumps(s,ensure_ascii=False)
    typ=['#set page(paper: "a4", flipped: true, margin: 15mm)','#set text(size: 9pt)',
         '= Certified SAT follow-up: retained observations', '#text('+q(intro)+')',
         '#text('+q('EXP-PNEXT-624f41 / RUN-PNEXT-ad1645. '+status)+')',
         '#image("diagram.svg", width: 100%)','#text('+q(scope)+')',
         '#pagebreak()','= Recorded counts and provenance']
    for line in md:
        if line.startswith('| ') and not line.startswith('|---'):
            typ+=['#text(size: 8pt, '+q(line)+')','#parbreak()']
    for paragraph in [
        'The prefix method retains 501,126 univariate root tests despite only 278 full coefficient checks. Relation coverage is five distinct affine x coordinates, with 155 generic and 123 fallback relations; repeated coordinates are outside scope.',
        'Every coefficient arm additionally performs 2,240 fallback signed-point enumerations and 11,200 Jacobian additions. Construction, proof checking, recovery, exhaustive reference and supplemental verification are charged separately in the full report. Counters are instrumented subsets, not total runtime.',
        'Quadratic A/A search multiplications differ with generator order; coefficient A/A field counts match but SAT decisions differ. No regularity, speedup or scalar-recovery inference.',
        'Protocol '+protocol['freeze']['protocol_sha256']+'; native authority '+launch['authority']['commit'],
        'Sources: arxiv.org/html/1503.08001; arxiv.org/html/2402.17927v1. All raw links, exact commands, controls, host facts and primitive counters are in report.md, report-data.json and export.json beside this PDF.']:
        if paragraph:typ+=['#parbreak()','#text('+q(paragraph)+')']
    (out/'report.typ').write_text('\n'.join(typ)+'\n')
    typst.compile(str(out/'report.typ'),output=str(out/'report.pdf'))
    print(json.dumps({'report':str(out/'report.md'),'pdf':str(out/'report.pdf'),'inspection_required':True}))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True)
    render(p.parse_args().out.resolve())
