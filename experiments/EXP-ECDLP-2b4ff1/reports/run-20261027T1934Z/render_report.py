#!/usr/bin/env python3
"""Render the recorded report data; no simulation, fitting, bootstrap or solver."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from xml.sax.saxutils import escape

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

HERE = Path(__file__).resolve().parent
DATA = json.loads((HERE/'data.json').read_bytes())
ARMS = ['static_small', 'static_full', 'static_filled', 'harvest', 'harvest_disabled', 'rho_reference']
BASELINES = ['static_filled', 'static_small', 'static_full', 'rho_reference']
LABELS = {'static_filled': 'Static distinct-filled (primary)', 'static_small': 'Static small',
          'static_full': 'Static requested-full', 'rho_reference': 'Rho reference'}
ROWS = [next(r for r in DATA['analysis']['comparisons'] if r['candidate']=='harvest' and
             r['baseline']==baseline and r['prefix']==64) for baseline in BASELINES]


def human(s):
    """Separate prose tokens while preserving identities, hashes and code paths."""
    s = re.sub(r'(\d)(curves?|queries|targets?|replicates?|resamples|cells?|children|cases|fixtures|settings|producer|raw|final|terminal|promotions|solved|failed|mismatches|native|public|ordinary|control|bit|seconds|bytes|here|unique|pairs|streams|A/A)', r'\1 \2', s)
    s = re.sub(r'\b(all|from|after|per|each|over|across|with|and|at|before|cofactor|is|were|interval|return|receipt|passed|attempt|the|covers|figure|pointwise|prefix)(?=\d)', r'\1 ', s, flags=re.I)
    s = re.sub(r'(?<=[A-Za-z]):(?=\d)', ': ', s)
    s = re.sub(r';(?=\S)', '; ', s)
    s = re.sub(r'(?<=[A-Za-z]),(?=\d)', ', ', s)
    for old, new in [('bothreplicates','both replicates'), ('allprefixes','all prefixes'),
                     ('sixarms','six arms'), ('eightarms','eight arms'), ('wait4user','wait4 user'),
                     ('wait4ru_maxrss','wait4 ru_maxrss'), ('sourceA','source A'), ('sourceB2','source B2'),
                     ('publicqueries','public queries'), ('publicwitnesses','public witnesses'),
                     ('nativechildren','native children'), ('nativechecks','native checks'),
                     ('prefix64counters','prefix 64 counters'), ('neither0nor1728','neither 0 nor 1728'),
                     ('fromKiB','from KiB'), ('user+system','user + system'), ('cohortdraw','cohort draw')]:
        s=s.replace(old,new)
    return s


def graph():
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10, 'svg.fonttype': 'none'})
    fig, ax = plt.subplots(figsize=(8.2, 3.3))
    for i, row in enumerate(ROWS):
        y = len(ROWS)-1-i
        v = row['gmean_ratio']; lo, hi = row['pointwise_cluster_bootstrap_ci95']
        ax.errorbar(v, y, xerr=[[v-lo], [hi-v]], fmt='o', color='#126a83' if i==0 else '#48576a',
                    capsize=4, markersize=7, linewidth=1.7)
        ax.text(1.035, y, f'{v:.3f} [{lo:.3f}, {hi:.3f}]', va='center', fontsize=9)
    ax.axvline(1, ls='--', color='#aab0b7', lw=1)
    ax.set_yticks(range(4), [LABELS[b] for b in BASELINES[::-1]])
    ax.set_xlim(0.15, 1.47)
    ax.set_xticks([.2,.4,.6,.8,1.0])
    ax.set_xlabel('Harvest / reference group-invocation ratio (unitless)')
    ax.set_title('Recorded counts: setup and 64 queries', loc='left', fontsize=13, pad=12)
    ax.grid(axis='x', color='#e6e9ed', linewidth=.7)
    for s in ('top','right','left'): ax.spines[s].set_visible(False)
    ax.spines['bottom'].set_color('#c8ced5')
    ax.tick_params(axis='y', length=0)
    fig.tight_layout()
    fig.savefig(HERE/'ratios-m64.svg', bbox_inches='tight')
    fig.savefig(HERE/'ratios-m64.png', dpi=180, bbox_inches='tight')
    plt.close(fig)


def ratio_table_md():
    lines=['| Candidate / reference | Role | Recorded ratio | Recorded 95% cluster interval |',
           '|---|---|---:|---:|']
    for r in ROWS:
        lo, hi=r['pointwise_cluster_bootstrap_ci95']
        lines.append(f"| `harvest / {r['baseline']}` | {'Primary at64queries' if r['decisive'] else 'Secondary'} | {r['gmean_ratio']:.6f} | [{lo:.6f}, {hi:.6f}] |")
    lines.append('| `harvest_disabled / static_small` | A/A | 1.000000 | [1.000000, 1.000000] |')
    return '\n'.join(lines)


def diagnostics_md():
    out=['| Arm | Group invocations: sum across128cells | Whole-child CPU seconds: sum | Maximum child RSS (MiB) |',
         '|---|---:|---:|---:|']
    for arm in ARMS:
        row=DATA['arm_diagnostics'][arm]
        out.append(f"| `{arm}` | {row['group_additions_m64']:,} | {row['whole_child_cpu_seconds']:.6f} | {row['maximum_child_maxrss_bytes']/1048576:.3f} |")
    return '\n'.join(out)


METHOD = ('For each curve, sum the two replicate costs for each arm, divide harvest by the reference, '
          'and take the geometric mean of the64curve ratios. Intervals are the frozen analysis\'s pointwise '
          '95% cluster-bootstrap intervals from10,000resamples of curves, preserving bothreplicates and allprefixes. '
          'Only harvest/static_filled after64queries is the registered primary contrast. Secondary rows are descriptive; '
          'their intervals make no familywise discovery claim.')
SCOPE = ('The metric sums reported solver-native setup and online group_additions, including public answer checks '
         'and endpoint promotion checks. Common input certification, parsing, output, orchestration and non-EC '
         'bookkeeping are separate costs. Scalar-multiplication/doubling diagnostics are not added again. '
         'A group invocation is not a complete application-runtime unit.')
LIMITS = [
    'The independent verifier checked public equations and causal trace/state conditions. It did not independently replay native operation counts or attest execution or isolation.',
    'The verifier did not independently count every curve point. Its public order checks are Hasse/divisibility and subgroup checks. The trace state hash64 is not a cryptographic certificate.',
    'All producer clocks have wall_valid=false. The Modal VM does not attest L2 or exclusive physical-host placement. CPU/RSS and supervisor elapsed time are retained operational diagnostics.',
    'The fixed endpoint limit bounds known plus pending slots; it does not bound whole-process RSS. Sorting, hashing, lookup and other non-EC costs are not priced by group invocation counts.',
    'This fixed64-query panel covers12/14/16/18-bit prime subgroups,16curves per size. It does not identify a scaling exponent or provide a cryptographic-size runtime estimate.',
    'Thirty repeated public-query records within cells are retained under the registered with-replacement sampling. The8,192 identifiers are unique; the public points need not all be distinct.',
]


def markdown():
    text=f'''# Classical endpoint-reuse run observations

This is a descriptive record of RUN-ECDLP-b883bf for EXP-ECDLP-2b4ff1, H-ECDLP-3509c4 and GOAL-ECDLP-e70832. It reports execution, public correctness checks and the frozen analysis; it makes no scientific verdict or official status transition.

All **768 planned native children completed** with no recorded failed, timed-out or unattempted child. All **49,152 target-arm scalar witnesses** passed independent public equation checks. The fixed panel contains **64 ordinary curves ×2replicates ×64targets =8,192target IDs**, evaluated by sixarms. The verifier checked6,432retained terminal equations and5,885promotions; all128A/A pairs matched.

Records: [run manifest](../../runs/RUN-ECDLP-b883bf/manifest.yaml), [frozen protocol](../../protocol.modal-vm.v1.json), [plot/table data](data.json), [checked graph hashes](graph-check.json).

## Recorded comparison at64targets

{ratio_table_md()}

{METHOD}

![Recorded group-invocation ratios and the frozen pointwise95% cluster intervals. RUN-ECDLP-b883bf;64curves, two replicates per curve,64targets per cell.](ratios-m64.svg)

{SCOPE}

## Execution and controls

- One approved supervisor trial, RUN-ECDLP-b883bf, on CPU-only Modal VM `sb-01M5ZDNY7CWH1T1Z5HET0QP6JD`; no scientific retry or restoration. Supervisor return code0 and output checker return code0; receipt status `output_validated`.
- Six arms: `static_small`, `static_full`, `static_filled`, `harvest`, `harvest_disabled`, `rho_reference`. `static_full` pays the requested raw-chain budget and may underfill; `static_filled` pays to reach the distinct endpoint count. Harvest uses verified endpoint admission into the bounded known-plus-pending arena.
- Registered sizes12,14,16,18subgroup bits,16fresh ordinary nonanomalous curves each, j neither0nor1728, cofactor1..3. Targets were sampled uniformly with replacement. Hidden target labels were not inputs to the solver VM or read by the independent verifier.
- Exact A/A:128cell pairs,256control streams,16,384target rows, four registered fields equal (`prefixes`, `status_counts`, initial-entry SHA and target-answer/counter-trace SHA);0mismatches.
- Independent public verifier:64fixtures,128settings cells,768producer cells,143,301raw rows,49,152cases,49,152final scalar witnesses,6,432terminal equations and5,885promotions. Producer target statuses:49,152solved;0failed/censored/invalid. Analysis field `primary_panel_eligible=true` is retained as a recorded field, not a claim-review decision.
- Supervisor driver interval46.669368seconds, from2026-10-27T19:34:00.933932Z to19:34:47.603300Z; final supervisor receipt19:34:49.841671Z. This interval includes control and transport activity and is unqualified.

Exact launch:

```sh
python3 tools/experiment_execution.py run \\
  --plan experiments/EXP-ECDLP-2b4ff1/trial-plan.json \\
  --owner executor-modal-endpoint --epoch 1
```

The launch argv, supervisor Python version, command, public per-cell seeds and input SHA bindings are retained in `launch.json`, `command.txt`, `environment.json`, the frozen trial plan and each native `execution.json`. Private labels are not needed for the public checks.

## Recorded resource and count diagnostics

{diagnostics_md()}

These columns are labelled arithmetic, not additional statistical analyses. The count column sums the128frozen prefix64counters per arm; it is not the geometric-mean comparison above. CPU sums wait4user+system seconds over whole native children, including common input validation, parsing, setup, targets, output and teardown. RSS is the maximum recorded Linux wait4ru_maxrss across128children, converted fromKiB tobytes by sourceA, then divided by1,048,576here. These clocks remain unqualified. Per-child observations and all field-counter families remain in the raw archive.

## Limits of this record

'''+'\n'.join('- '+s for s in LIMITS)+f'''

## Source and artifact custody

- Native/helper/verifier/analysis sourceA: `fe01ccd832832488c58abeef17548b0a8db6035f`.
- Modal adapter sourceB2: `de6ed88850fc8bad17ccbabfad8b66a791e478e5`. Binary SHA256: `{DATA['binary_sha256']}`.
- Frozen protocol canonical SHA256: `{DATA['protocol_sha256']}`. Public inputs-manifest SHA256: `{DATA['inputs_manifest_sha256']}`. Protocol frozen2026-10-27T19:25:53Z, before the fresh cohort draw.
- Full controller evidence archive:43,223,355bytes, SHA256 `{DATA['archive']['sha256']}`, at `{DATA['archive']['uri']}`. The run's storage pointers and readback record provide transport details. The archive contains all raw streams, input slices, child observations and retained source/provider identities.
- Data for these figures and tables, with exact source-file SHA256s, are in `data.json`; `extract_observations.py` performs only copied-summary extraction and labelled sums, and `render_report.py` renders them without launching a solver, sampling or fitting.
- Frozen-analysis source: `harness/classical_ecdlp_endpoint_reuse/protocol/analysis.py`; public verifier: `harness/classical_ecdlp_endpoint_reuse/verification/verify_public.py`. Actual verifier/analysis command records, summary hashes and exports are retained by the accompanying postrun archive.

## Development calibration and prior context

Before the new cohort was drawn, calibration attempt01 exposed unreadable support-source permissions and stopped before any native child. Its complete failure receipt was retained. The B2 image correction made the source readable and immutable to UID1000 and added an engine-import probe. The repaired image passed783native software checks. A separate calibration on one already-used18-bit fixture and16already-used public points repeated to64queries completed sixchildren and384public witness checks. Its runtime estimate was planning metadata, not confirmation data; it did not alter the fixed study design.

Internal sources checked for report scope: the frozen protocol and analysis, native child/parent receipts, independent verification summaries, and `docs/reports/classical-ecdlp-endpoint-reuse-20261026/report.md` (mechanism and prior-work audit). These are internal retrieved records; this report adds no literature-completeness claim.

Canonical graph check: the existing mechanism SVG and its rendering source, plus the separate non-generic proof-search map/source/rendering, were checked and left unchanged. This finite run changes neither the causal algebra diagram nor uniform-constructor proof obligations and makes no official scientific transition. `graph-check.json` records the exact checked hashes. The new graph above records only this run's observations.
'''
    (HERE/'report.md').write_text(human(text))


def pdf():
    pdfmetrics.registerFont(TTFont('ReportSans', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
    pdfmetrics.registerFont(TTFont('ReportSans-Bold', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
    pdfmetrics.registerFontFamily('ReportSans', normal='ReportSans', bold='ReportSans-Bold',
                                italic='ReportSans', boldItalic='ReportSans-Bold')
    styles=getSampleStyleSheet()
    for style in styles.byName.values():
        style.fontName='ReportSans-Bold' if style.name.startswith(('Heading','Title')) else 'ReportSans'
    styles.add(ParagraphStyle(name='SmallNote',parent=styles['BodyText'],fontSize=8,leading=10,spaceAfter=5))
    styles['BodyText'].fontSize=9;styles['BodyText'].leading=12;styles['BodyText'].spaceAfter=7
    styles['Heading1'].fontSize=18;styles['Heading1'].leading=22
    styles['Heading2'].fontSize=12;styles['Heading2'].leading=15;styles['Heading2'].spaceBefore=8
    story=[]
    def p(s,style='BodyText'):story.append(Paragraph(escape(human(s)),styles[style]))
    def table(rows,widths):
        t=Table([[Paragraph(escape(str(x)),styles['SmallNote']) for x in r] for r in rows], colWidths=widths,repeatRows=1)
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e8eef2')),('VALIGN',(0,0),(-1,-1),'TOP'),
                              ('LINEBELOW',(0,0),(-1,0),.5,colors.HexColor('#b1bac5')),('BOTTOMPADDING',(0,0),(-1,-1),6),
                              ('TOPPADDING',(0,0),(-1,-1),5),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f5f7f9')])]))
        story.append(t);story.append(Spacer(1,8))
    p('Classical endpoint-reuse run observations','Title')
    p('RUN-ECDLP-b883bf · EXP-ECDLP-2b4ff1 · 27 October 2026','SmallNote')
    p('This descriptive run report records execution, public correctness checks and the frozen analysis. It makes no scientific verdict or official status transition.')
    p('768/768 planned native children completed. All49,152target-arm scalar witnesses passed independent public equation checks. The fixed panel is64ordinary curves ×2replicates ×64targets (8,192unique target IDs), evaluated by sixarms. All128A/A pairs matched.')
    p('Recorded comparison after64queries','Heading2')
    rows=[['Harvest / reference','Role','Ratio','Recorded95% cluster interval']]
    for r in ROWS:
        lo,hi=r['pointwise_cluster_bootstrap_ci95'];rows.append([r['baseline'],'Primary' if r['decisive'] else 'Secondary',f"{r['gmean_ratio']:.6f}",f'[{lo:.6f}, {hi:.6f}]'])
    rows.append(['harvest_disabled / static_small','A/A','1.000000','[1.000000, 1.000000]'])
    table(rows,[1.95*inch,.9*inch,.85*inch,2.0*inch])
    story.append(Image(str(HERE/'ratios-m64.png'),width=6.4*inch,height=2.58*inch))
    p('Figure1. Recorded ratios and frozen pointwise95% cluster intervals. RUN-ECDLP-b883bf;64curve clusters, two replicates per curve,64queries per cell. Graph renders recorded summary values only.','SmallNote')
    p(METHOD,'SmallNote')
    story.append(PageBreak())
    p('Cost scope, execution and controls','Heading1')
    p(SCOPE)
    p('Six arms: static_small; static_full (requested raw-chain budget, may underfill); static_filled (charged distinct filling); harvest (verified bounded endpoint admission); harvest_disabled (A/A); rho_reference.')
    p('Registered sizes:12/14/16/18-bit prime subgroups,16ordinary nonanomalous curves per size, j neither0nor1728 and cofactor1..3. Sampling is uniform with replacement:30repeated public-query records remain visible. Unique target IDs do not imply distinct points.')
    p('Public verification passed:64fixtures;128settings cells;768producer cells;143,301raw rows;49,152final scalar witnesses;6,432terminal equations;5,885promotions. Target statuses were49,152solved with0failed/censored/invalid. Hidden scalar labels were not read.')
    p('A/A controls:128cell pairs,256native streams and16,384target rows; all four registered fields matched, with0mismatches. The recorded analysis field primary_panel_eligible is true. This is not a separate claim-review decision.')
    p('Recorded count and resource diagnostics','Heading2')
    rows=[['Arm','Group calls, sum','Whole-child CPU(s), sum','Max child RSS(MiB)']]
    for arm in ARMS:
        x=DATA['arm_diagnostics'][arm];rows.append([arm,f"{x['group_additions_m64']:,}",f"{x['whole_child_cpu_seconds']:.6f}",f"{x['maximum_child_maxrss_bytes']/1048576:.3f}"])
    table(rows,[1.55*inch,1.25*inch,1.35*inch,1.15*inch])
    p('Labelled arithmetic across128children per arm. Group-call totals sum the frozen prefix64counters; these are not the equal-curve geometric means. CPU sums wait4user+system seconds for whole native children, including input validation/parsing, solver work, output and teardown. RSS is the largest recorded ru_maxrss, converted fromKiB. All clocks remain unqualified.','SmallNote')
    p('One scientific supervisor trial; no scientific retry/restoration. VM sb-01M5ZDNY7CWH1T1Z5HET0QP6JD. Supervisor and checker returned0; output_validated. Driver interval46.669368s (19:34:00.933932Z–19:34:47.603300Z); final receipt19:34:49.841671Z. The operational interval includes control and transport activity and is not a qualified algorithm clock.','SmallNote')
    p('Exact command: python3 tools/experiment_execution.py run --plan experiments/EXP-ECDLP-2b4ff1/trial-plan.json --owner executor-modal-endpoint --epoch 1. Launch argv, supervisor Python version, public per-cell seeds and input SHA bindings are retained in run launch/environment/command and native execution records.','SmallNote')
    story.append(PageBreak())
    p('Provenance and measurement limits','Heading1')
    for s in LIMITS:p('• '+s)
    p('Source and custody','Heading2')
    p('Native/helper/verifier/analysis sourceA: '+DATA['source_a'],'SmallNote')
    p('Modal adapter sourceB2: '+DATA['source_b'],'SmallNote')
    p('Native binary SHA256: '+DATA['binary_sha256'],'SmallNote')
    p('Frozen protocol canonical SHA256: '+DATA['protocol_sha256'],'SmallNote')
    p('Public inputs-manifest SHA256: '+DATA['inputs_manifest_sha256'],'SmallNote')
    p('Full controller evidence:43,223,355bytes; SHA256 '+DATA['archive']['sha256']+'. Content-addressed URI: '+DATA['archive']['uri'],'SmallNote')
    p('data.json records exact source-file hashes and labelled arithmetic. extract_observations.py copies summaries and sums recorded fields; render_report.py produces this report and figure without simulation, fitting or solver calls. Actual postrun command/verification/export records accompany the published study.','SmallNote')
    p('Development calibration and graph check','Heading2')
    p('Before the fresh cohort draw, development attempt01 stopped on source-file permissions before any native child; its failure record was retained. The B2 image fixed UID1000 read/traverse permission and added an import probe. It passed783native software checks. Separate retained-fixture calibration completed6children and384public witnesses; its planning estimate was not confirmation data.','SmallNote')
    p('The prior mechanism/prior-work audit, frozen protocol, analysis, supervisor/child receipts and independent verifier summaries were the internal sources read. Existing mechanism and separate non-generic proof-search graphs were checked and left unchanged; finite observations do not change their algebra/proof obligations or official scientific status. Exact hashes are in graph-check.json.','SmallNote')
    def footer(canvas, doc):
        canvas.setFont('ReportSans',7)
        canvas.setFillColor(colors.HexColor('#5b6570'))
        canvas.drawString(.65*inch,.38*inch,'RUN-ECDLP-b883bf | Observations only | Classical ECDLP')
        canvas.drawRightString(7.85*inch,.38*inch,str(doc.page))
    doc=SimpleDocTemplate(str(HERE/'report.pdf'),pagesize=(8.5*inch,11*inch),rightMargin=.65*inch,leftMargin=.65*inch,
                          topMargin=.6*inch,bottomMargin=.6*inch,title='Classical endpoint-reuse run observations',author='Run observation report')
    doc.build(story,onFirstPage=footer,onLaterPages=footer)


if __name__=='__main__':
    graph();markdown();pdf()
    print('Rendered report.md, report.pdf and ratios-m64.svg/png from data.json')
