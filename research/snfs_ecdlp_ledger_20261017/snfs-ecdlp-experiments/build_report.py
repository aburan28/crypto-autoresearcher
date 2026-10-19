from pathlib import Path
import base64
import csv
import hashlib
import html
import json
import statistics
from collections import Counter
import shutil

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parent
DATA={p.stem:json.loads(p.read_text()) for p in (ROOT/'results').glob('SNFS-*.json')}
PLANS=json.loads((ROOT/'experiment-plans.json').read_text())
PLAN={r['provisional_id']:r for r in PLANS['records']}
META=json.loads((ROOT/'run-metadata.json').read_text())
assert len(DATA)==len(PLAN)==23 and DATA.keys()==PLAN.keys()

verdicts={
 'SNFS-A1':'Zero support differences in 18 fixed-curve S3/S4 comparisons; throughput not tested.',
 'SNFS-A2':'No roots recovered by this weak S3 lattice prototype; bivariate validation gate remains unmet.',
 'SNFS-A3':'No resolved SAT case beat enumeration; many attempts are censored by the one-second cap.',
 'SNFS-A4':'Valid digit maps tested; finite closure effects require random-subset controls, not a universal 1.00 ratio.',
 'SNFS-B1':'Torsion-section controls passed modulo p^2; original unrescaled statistic is identically zero.',
 'SNFS-B2':'Known-answer random-lift Smart controls worked when nondegenerate; four canonical CM controls gave zero.',
 'SNFS-B3':'Reduced Tate-pairing controls passed; independent generalized-Jacobian implementation still missing.',
 'SNFS-B4':'Small embedding-degree sample is inconclusive; no CADO comparison or sieving.',
 'SNFS-B5':'Finite cyclic-kernel quotient identities checked; full generalized-Jacobian classification not tested.',
 'SNFS-B6':'Small zero-dimensional factor bases have compact repeated-squaring descriptions; cheap decomposition is unproven.',
 'SNFS-B7':'Five split-cover Jacobian order identities passed; no index-calculus complexity experiment.',
 'SNFS-C1':'Frobenius-order class numbers sampled; End(E) not certified. Rational CM gives an exact exception to a universal height bound.',
 'SNFS-C3':'Smooth representatives become sparse at higher precision; omega(1)=1 accounts for the remaining one-event floor.',
 'SNFS-D1':'Exact cyclic-sublattice counts/coverage checked; no high-rank certificates available.',
 'SNFS-D2':'Fixed-curve height control checked; random-lift rank distribution remains untested.',
 'SNFS-D3':'All nine observed small relations are single-point 2-torsion; no new two-point dependence found.',
 'SNFS-D4':'Original independence trigger is invalid: nonzero B-smooth W cannot be divisible by p>B.',
 'SNFS-D5':'Five profiles end at L/2; held-out quadratic search finds only the known defining recurrence.',
 'SNFS-E1':'Eight prescribed-fibre rank-eight split pencils constructed and checked; higher-rank growth remains open.',
 'SNFS-E2':'Exact E8-family minimum squared norm two and determinant one; no universal height claim.',
 'SNFS-E3':'Low-section solver has limited fresh coverage; oracle MITM shows no median cold-cost advantage over rho.',
 'SNFS-E4':'Exact E8 counts agree with known controls; candidate count above group order still leaves many targets uncovered.',
 'SNFS-F1':'Actual degree-one reductions of a fixed new non-torsion quadratic-field point checked; average rank gain untested.',
}


def fmt(x):return html.escape(str(x))


def main():
    sat=DATA['SNFS-A3']['rows'];satcounts=Counter(r['SAT']['status'] for r in sat)
    resolved=[r for r in sat if r['SAT']['status'] in ('verified-sat','unsat')]
    ratios=[r['SAT_cold_total_seconds']/r['enumeration_cold_total_seconds'] for r in resolved]
    e3=DATA['SNFS-E3']['rows'];fresh=[r for r in e3 if r['target_type']=='fresh']
    planted=[r for r in e3 if r['target_type']!='fresh']
    e4=DATA['SNFS-E4']['rows']
    cpu=sum(r['cpu_seconds'] for r in META['runs'])
    summary={
      'scope':'All 23 records have finite pilots or receipts; the original full campaigns have NOT been executed.',
      'source':'Resource-capped serial run in run-metadata.json; earlier development timings are superseded.',
      'records':23,'measurement_rows':sum(len(r['rows']) for r in DATA.values()),
      'cpu_seconds':cpu,'module_wall_seconds':sum(r['wall_seconds'] for r in META['runs']),
      'A3':{'cases':len(sat),'statuses':dict(satcounts),
        'resolved_cold_SAT_to_cold_enumeration_ratio_min':min(ratios),
        'resolved_cold_SAT_to_cold_enumeration_ratio_median':statistics.median(ratios),
        'cost_scope':'Both totals include the shared full curve-point table, factor-base filtering and verified target decomposition.',
        'warning':'Timeout-bound outcomes can change across machines/reruns. Resolved comparisons are conditional, not an unbiased solver-success estimate.'},
      'E3':{'fresh_targets':len(fresh),'planted_low_section_targets':len(planted),
        'geometry_fresh_successes':sum(r['geometry_low_section']['success'] for r in fresh),
        'geometry_planted_successes':sum(r['geometry_low_section']['success'] for r in planted),
        'rho_fresh_successes':sum(r['rho']['status']=='verified' for r in fresh),
        'rho_all_successes':sum(r['rho']['status']=='verified' for r in e3),
        'oracle_MITM_fresh_successes':{m:sum(r['oracle_MITM'][m]['success'] for r in fresh) for m in ('1','2')},
        'per_prime':[]},
      'D4':{'original_independence_trigger':'mathematically invalid for B<p and W nonzero',
            'verified_smooth_kernel_overlap':sum(r['smooth_kernel_overlap'] for r in DATA['SNFS-D4']['rows'])},
      'ranking':{'best_open_research_question':'SNFS-E3 with SNFS-E1/E2/E4 support; no fast blind solver demonstrated',
                 'second':'Revised SNFS-A3 compositional-factor-base decomposition',
                 'retire_as_written':'SNFS-D4 smoothness/kernel independence trigger'},
      'no_asymptotic_claim':True,'no_deployed_keys':True,'no_sieving':True,
    }
    for p in sorted({r['p'] for r in fresh}):
        f=[r for r in fresh if r['p']==p];item={'p':p,'N':f[0]['N'],
            'fresh_targets':len(f),'geometry_hits':sum(r['geometry_low_section']['success'] for r in f),
            'rho_hits':sum(r['rho']['status']=='verified' for r in f)}
        for m in ('1','2'):
            ss=[r for r in f if r['oracle_MITM'][m]['success']]
            cold_ratios=[(r['oracle_MITM'][m]['one_target_total_seconds']+
                (0 if r['oracle_MITM'][m]['success'] else r['rho']['wall_seconds']))/r['rho']['wall_seconds'] for r in f]
            batch_hybrid=0.;batch_rho=sum(r['rho']['wall_seconds'] for r in f)
            for case in sorted({r['case'] for r in f}):
                cohort=[r for r in f if r['case']==case]
                batch_hybrid+=cohort[0]['pencil_build_seconds']+cohort[0]['oracle_MITM'][m]['precompute_seconds']
                batch_hybrid+=sum(r['oracle_MITM'][m]['lookup_seconds']+
                    (0 if r['oracle_MITM'][m]['success'] else r['rho']['wall_seconds']) for r in cohort)
            item['M'+m]={'hits':len(ss),'conditional_median_cold_MITM_to_rho_ratio':statistics.median(
                r['oracle_MITM'][m]['one_target_total_seconds']/r['rho']['wall_seconds'] for r in ss),
                'matched_coverage_median_cold_hybrid_to_rho_ratio':statistics.median(cold_ratios),
                'hybrid_uses_rho_for_failed_MITM_targets':True,
                'matched_coverage_batch_hybrid_to_rho_ratio':batch_hybrid/batch_rho}
        item['H8_complete_lattice_coverage']=[r['coverage'] for r in e4 if r['p']==p and r['H']==8]
        summary['E3']['per_prime'].append(item)
    (ROOT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    with (ROOT/'all-leads.csv').open('w',newline='') as f:
        writer=csv.writer(f);writer.writerow(['provisional_id','title','pilot_scope','rows','evidence_class','verdict','next_priority','followup_cpu_cap','full_protocol_limitations'])
        for pid,d in DATA.items():writer.writerow([pid,d['title'],d['scope'],len(d['rows']),d['evidence_class'],verdicts[pid],PLAN[pid]['priority'],PLAN[pid]['cpu_cap'],' | '.join(d['limitations'])])

    fig,ax=plt.subplots(figsize=(8,4.4),layout='constrained')
    primes=sorted({r['p'] for r in e4})
    for H,color in zip((2,4,6,8),('#b47729','#8773a7','#3986a8','#1a7754')):
        pairs=[[r['coverage'] for r in e4 if r['p']==p and r['H']==H] for p in primes]
        ax.plot(primes,[statistics.mean(t) for t in pairs],marker='o',label=f'H = {H}',color=color)
        ax.fill_between(primes,[min(t) for t in pairs],[max(t) for t in pairs],alpha=.13,color=color)
    ax.set_xscale('log',base=2);ax.set_xticks(primes,[str(p) for p in primes]);ax.set_ylim(0,1.04)
    ax.set_xlabel('Field prime p');ax.set_ylabel('Fraction of fibre group reached')
    ax.set_title('Complete E8 short-section coverage: two surfaces per prime')
    ax.legend(title='Squared height');ax.grid(alpha=.18)
    fig.savefig(ROOT/'coverage.png',dpi=160)
    image=base64.b64encode((ROOT/'coverage.png').read_bytes()).decode()
    cards=[]
    for pid in [r['provisional_id'] for r in json.loads((ROOT/'inputs/normalized-ledger.json').read_text())['records']]:
        d=DATA[pid];p=PLAN[pid]
        cards.append(f'''<details><summary><b>{fmt(pid)}</b> — {fmt(verdicts[pid])}</summary>
          <p><b>Executed scope:</b> {fmt(d['scope'])}. {len(d['rows'])} recorded rows; {fmt(d['evidence_class'])}.</p>
          <p><b>Limits:</b> {' '.join(fmt(t) for t in d['limitations'])}</p>
          <p><b>Next hypothesis:</b> {fmt(p['hypothesis'])}</p>
          <ol>{''.join('<li>'+fmt(t)+'</li>' for t in p['steps'])}</ol>
          <p><b>Controls:</b> {'; '.join(fmt(t) for t in p['controls'])}</p>
          <p><b>Measurements:</b> {'; '.join(fmt(t) for t in p['measurements'])}</p>
          <p><b>Stopping rule:</b> {fmt(p['stopping_rule'])}</p>
          <a href="results/{pid}.json">Raw evidence</a></details>''')
    table=''.join(f"<tr><td>{r['p']}</td><td>{r['geometry_hits']}/{r['fresh_targets']}</td><td>{r['M1']['hits']}/{r['fresh_targets']}</td><td>{r['M2']['hits']}/{r['fresh_targets']}</td><td>{r['rho_hits']}/{r['fresh_targets']}</td><td>{r['M1']['matched_coverage_median_cold_hybrid_to_rho_ratio']:.1f}×</td><td>{r['M1']['matched_coverage_batch_hybrid_to_rho_ratio']:.2f}×</td></tr>" for r in summary['E3']['per_prime'])
    page=f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
    <title>ECDLP hypothesis pilots and experiment plans</title><style>
    body{{font:16px/1.55 system-ui,sans-serif;color:#20312d;background:#f6f7f4;margin:0}}main{{max-width:1040px;margin:auto;padding:36px 24px}}
    h1{{font-size:32px;line-height:1.2}}h2{{font-size:23px;margin-top:32px}}.note{{border-left:4px solid #b47729;padding:14px;background:#fff9ec}}
    table{{border-collapse:collapse;width:100%;background:white}}th,td{{padding:10px;border-bottom:1px solid #dce4de;text-align:left}}
    details{{background:white;border:1px solid #dce4de;border-radius:8px;margin:10px 0;padding:15px}}summary{{cursor:pointer}}a{{color:#146448}}img{{width:100%;max-width:850px}}
    .metrics{{display:flex;gap:24px;flex-wrap:wrap}}.metrics div{{background:white;padding:16px;border-radius:8px}}small{{color:#52615a}}
    </style><main><h1>23 hypothesis records: finite pilots and corrected experiments</h1>
    <p class="note"><b>All 23 records received a bounded pilot or control. The original full campaigns were not executed.</b>
    These measurements cover synthetic small fields and selected mathematical controls. General section solving, certified high-rank number-field work,
    full generalized-Jacobian arithmetic, large solver sweeps and CADO polynomial selection remain unrun. No sieving or deployed-key work occurred.</p>
    <div class="metrics"><div><b>23</b><br>records covered</div><div><b>{summary['measurement_rows']}</b><br>measurement rows, not independent experiments</div>
    <div><b>{cpu:.1f} s</b><br>measured serial-run CPU</div><div><b>0</b><br>asymptotic claims</div></div>
    <h2>What changed the assessment</h2>
    <p><b>E3 remains the best open research question, with no demonstrated fast blind solver.</b> Eight target-independent rank-eight cubic pencils were checked.
    The 92-section interpolation method found {summary['E3']['geometry_fresh_successes']} of {len(fresh)} fresh targets and {summary['E3']['geometry_planted_successes']} of {len(planted)} planted low-section targets.
    Rho verified every one of the {len(e3)} toy target logs. Oracle MITM recovered many logs, but median cold costs were above rho at each size.
    Query success on a small fixed section set is not a general section-finding algorithm.</p>
    <table><tr><th>p</th><th>Geometry hits</th><th>Oracle M=1 hits</th><th>Oracle M=2 hits</th><th>Rho hits</th><th>Cold M=1/rho*</th><th>Batch M=1/rho*</th></tr>{table}</table>
    <p><small>*Ratios show the M=1 hybrid, which uses rho after an unsuccessful MITM lookup, giving equal coverage on the measured targets.
    Cold ratios charge pencil and MITM setup for each query; batch ratios share setup once per surface over 20 fresh targets.
    Both include coordinate recovery and verification. These tiny-instance comparisons do not establish asymptotic gains.</small></p>
    <p>The M=1 oracle hybrid was faster after amortization on the three smaller 20-target batches, but not on the largest tested size.
    This is ordinary bounded group search with shared preprocessing; it is not a new blind section algorithm. Both M=1 and M=2 costs and success counts are retained in summary.json.</p>
    <p><b>E4:</b> exact short-vector counts are 241, 2401, 9121 and 26641 at squared heights 2,4,6,8. At p=16381, 26641 candidates still reached only about 53–70% of the fibre.
    Candidate count above group order does not guarantee coverage.</p><img alt="Coverage versus field size at four fixed heights" src="data:image/png;base64,{image}">
    <p><b>A3:</b> {len(sat)} completed target attempts: {satcounts.get('verified-sat',0)} verified SAT answers, {satcounts.get('unsat',0)} verified unsatisfiable cases and {satcounts.get('unknown',0)} censored/unknown attempts.
    Among resolved cases the minimum cold SAT/enumeration wall-time ratio was {min(ratios):.1f}×, including full curve-point table construction, factor-base filtering and verified target solving.
    This pilot uses a full point table; a production implementation could build a factor base more cheaply.
    This is one bit-vector implementation on small parameters, not a general SAT or algebraic lower bound.</p>
    <p><b>A2:</b> the selected weak lattice prototype recovered no S3 plants in 18 cases; all nine univariate controls passed.
    The separate required bivariate validation is missing, so this does not establish a Coppersmith threshold or a negative result on the full method.</p>
    <p><b>D4:</b> the original independence test is mathematically invalid. For nonzero integral W and B&lt;p, B-smoothness excludes p divisibility.
    The pilot verified zero overlap. A nonzero mutual information caused by that exclusion is not an attack signal. Further work needs a different feature and a costed held-out prediction test.</p>
    <p><b>Controls:</b> torsion-section, Smart, Tate-pairing, split-cover, EDS and class-number controls passed within their stated scopes.
    Compact zero-dimensional factor-base descriptions exist, but no cheap decomposition follows from that fact. All nine fitted-lift small relations were single-point 2-torsion.</p>
    <h2>All records and proposed follow-ups</h2><p>Open each record for what was executed, what remains unrun, controls, measurements and a stopping rule.
    The follow-up CPU caps are proposals, not completed expenditure. Original theorem-closed records retain receipt-only eligibility.</p>{''.join(cards)}
    <h2>Reproduction and provenance</h2><p>Run <code>python run_all.py</code> after installing the pinned requirements. The runner uses one BLAS thread,
    a 240-second CPU soft cap, 300-second wall cap and 3 GiB address-space cap per module. Timings and timeout-bound solver outcomes may vary by machine.
    Seeds derive reproducibly from the staged local candidates; campaign-wide reservation and canonical hypothesis IDs remain pending the existing harness.</p>
    <p><a href="summary.json">Machine-readable summary</a> · <a href="all-leads.csv">All-record CSV</a> ·
    <a href="experiment-plans.json">23 corrected experiment designs</a> · <a href="run-metadata.json">Build and resource metadata</a></p>
    </main></html>'''
    (ROOT/'report.html').write_text(page)


if __name__=='__main__':main()
