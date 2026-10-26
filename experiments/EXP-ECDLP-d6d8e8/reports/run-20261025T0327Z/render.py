"""Render recorded observations only; no relation collection or new sampling."""
from datetime import datetime
import json
from pathlib import Path
import sys
import yaml
from reportlab.graphics import renderSVG
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT/'tools'))
import artifact_store


def main():
    run = ROOT/'experiments/EXP-ECDLP-d6d8e8/runs/RUN-ECDLP-ea49a6'
    raw = artifact_store.read_json(run/'raw-result.json')
    check = artifact_store.read_json(run/'verification.json')
    receipt = json.loads((run/'execution-receipt.json').read_text())
    manifest = yaml.safe_load((run/'manifest.yaml').read_text())['run']
    panel = json.loads((ROOT/'research/prym_rank_census_20261025/fixtures.json').read_text())
    table = []
    for fixture in panel['fixtures']:
        pair = [next(c for c in raw['cells'] if c['curve_uid']==fixture['uid'] and c['arm']==a)
                for a in ['sample64','full3584']]
        table.append([str(fixture['p']), str(fixture['b']), str(pair[0]['projection']['U']),
                      str(len(pair[0]['rows'])), str(pair[0]['projection']['rank']),
                      str(len(pair[1]['rows'])), str(pair[1]['projection']['rank']),
                      str(pair[1]['first_full_rank']['attempt']) if pair[1]['first_full_rank'] else '—'])
    points = [dict(curve_uid=c['curve_uid'], p=c['p'], arm=c['arm'], rows=len(c['rows']),
                   U=c['projection']['U'], rank=c['projection']['rank'], first_full_rank=c['first_full_rank'],
                   operation_vector=c['attack_operation_vector'], matrix_units=c['online_matrix_units'],
                   wall_seconds=c['wall_seconds'], cpu_seconds=c['cpu_seconds']) for c in raw['cells']]
    source = dict(run_id='RUN-ECDLP-ea49a6', source='../../runs/RUN-ECDLP-ea49a6/raw-result.json',
                  metric='Rank and unknown columns modulo each target prime r; accepted row counts.',
                  units='columns, rows, attempted descriptors; unweighted operation vectors',
                  uncertainty='Exact fixed finite panel; no population interval or deployed-curve extrapolation.', points=points)
    (HERE/'graph-source.json').write_text(json.dumps(source, indent=2)+'\n')
    drawing = Drawing(490, 190)
    drawing.add(String(5, 176, 'RUN-ECDLP-ea49a6: sampled / full census rank, n=8 paired curves', fontSize=10))
    for j, point in enumerate(points):
        x = 8+j*29
        drawing.add(Rect(x, 40, 8, point['U']*15, fillColor=HexColor('#c5d0de'), strokeWidth=0))
        drawing.add(Rect(x+9, 40, 8, point['rank']*15, fillColor=HexColor('#2465a3'), strokeWidth=0))
        drawing.add(String(x, 29, f"{point['rank']}/{point['U']}", fontSize=7))
        drawing.add(String(x, 18, str(point['p']), fontSize=6))
        drawing.add(String(x, 8, '64' if point['arm']=='sample64' else '3584', fontSize=6))
    drawing.add(String(5, 0, 'Grey=U, blue=rank; x labels: p / branches per source. U=0 is all-public calibration.', fontSize=7))
    renderSVG.drawToFile(drawing, str(HERE/'graph.svg'))
    sample_rows = sum(len(c['rows']) for c in raw['cells'] if c['arm']=='sample64')
    full_rows = sum(len(c['rows']) for c in raw['cells'] if c['arm']=='full3584')
    attempts = sum(c['attempts'] for c in raw['cells'])
    start, end = map(datetime.fromisoformat, [receipt['started_at'], receipt['finished_at']])
    paragraphs = [
        f'Observations only. EXP-ECDLP-d6d8e8 / H-ECDLP-51f052 / GOAL-ECDLP-001. '
        f'RUN-ECDLP-ea49a6 completed one requested native trial: {attempts:,} attempts, 16 cells, '
        f'11 controls. Independent complete-stream checker: {check["status"]}; failed checks: {check["failed_checks"]}. '
        'No failure, timeout, repair, extra branch or early stop occurred. No scientific verdict or ECDLP improvement is asserted.',
        f'Measured accepted rows: {sample_rows} sampled and {full_rows} exhaustive. '
        'The two F101 bases are entirely exposed by the public source schedule (U=0); their rows are calibration. '
        'Among the six U>0 fixture pairs, sampled matrices reach full rank on two; exhaustive matrices on four. '
        'Both F4099 fixtures accept zero rows in either arm. This is an exact statement about the fixed collector/base/source grid, '
        'and supplies no general rank cap or security conclusion.',
        'Workload: eight fixed fresh A=2 curves; public sources 1..64; seed 0 fixes source order. '
        'Sampled arm: 64 distinct branches per source, 4,096 attempts per fixture. '
        'Exhaustive arm: all binomial(8,3) times 4^3 = 3,584 branches, 229,376 attempts per fixture. '
        'The factor base, public anchors, source lifts, constructor and alias law match within each pair. '
        'Repeated field sizes are distinct curve instances, not extra independent seeds.',
        f'Measured producer wall/CPU: {raw["wall_seconds"]:.6f}/{raw["cpu_seconds"]:.6f} s; '
        f'peak self RSS: {manifest["timing"]["producer_peak_rss_bytes"]:,} bytes. '
        f'Independent checker wall/CPU: {check["wall_seconds"]:.6f}/{check["cpu_seconds"]:.6f} s; '
        f'peak self RSS: {check["peak_rss_bytes"]:,} bytes. '
        f'Derived native start-to-receipt elapsed time: {(end-start).total_seconds():.6f} s '
        '(timestamp subtraction; includes checker/storage, not an attack-cost bound).',
        'All branch statuses, including rejects and aliases, were independently replayed. Accepted principal witnesses, '
        'E1 source equations, E2 cancellation, projected rank/augmented rank, first-full-rank events, finite nullspaces, '
        'sample-equation containment and transported atom-permutation A/A passed the frozen checker. '
        'The separate observation-integrity review is not implied by this checker pass.',
        'Raw field/group/hash vectors and online/final matrix units are retained per arm and at first-full-rank events '
        'in raw-result.json and graph-source.json. Input search retains all 135 inspected candidates. '
        'Producer wall includes inline witness/A/A checks; their arithmetic is outside the collector field counters. '
        'Pow internals, Python bookkeeping, byte movement, sampled process-group peak and independent operation-count '
        'verification remain missing. No complete weighted S, current-best IC comparison, optimized rho reference or blind DLP recovery was measured.',
        f'Code authority: {manifest["code"]["commit"]}, clean tracked tree at launch. Runtime: Python 3.12.14 on Linux; '
        'frozen PyYAML 6.0.3 and reportlab 4.4.9 match. The Cursor-specific /usr/local Python path is absent in this managed runtime; '
        'the actual interpreter is recorded in environment.json. Scientific source20/input5 bindings are unchanged. '
        'Approval: DEC-20261025-1bd76a; storage/approval snapshots b3bbf59b1 and 58d9e0d3a.',
        'Exact outer command: python3 research/prym_rank_census_20261025/storage-delivery-20261025/execute_with_storage.py '
        'run --plan experiments/EXP-ECDLP-d6d8e8/trial-plan.json --owner executor-prym-census --epoch 1. '
        'The native command.txt records the frozen launcher invocation; the trial plan binds both launcher and independent checker.',
        'Canonical storage: raw-result.json and events.jsonl are native gzip/blob pointers. Canonical CLI publication and fresh '
        'GET/digest checks completed before receipt sealing. Separate artifact-deliveries/RUN-ECDLP-ea49a6/custody.json binds '
        'logical content, stored object and receipt digests. Metadata-only native coverage reports output_validated; it does not '
        'establish a prescribed-computation proof. Public cache selector: CRYPTO_AR_BLOB_CACHE=/tmp/prym-native-blob-cache.',
        'Procedure note: the completed-release CLI checked only physical raw paths and initially refused two compacted logical '
        'outputs. Its documented authoritative-receipt option was then used with both explicit logical content hashes; all '
        '19 declared outputs are bound. No run bytes, sealed receipt, source grid or scores were edited. '
        'Credentials were confined to the operational process and excluded from source, run files and commits.',
    ]
    header = ['p','B','U','sample rows','rank','full rows','rank','full first attempt']
    md = '# Fixed Prym rank census / RUN-ECDLP-ea49a6\n\n'+paragraphs[0]+'\n\n'
    md += '![Recorded rank and unknown columns](graph.svg)\n\n'
    md += '| '+' | '.join(header)+' |\n| '+' | '.join(['---']*len(header))+' |\n'
    md += '\n'.join('| '+' | '.join(row)+' |' for row in table)+'\n\n'
    md += '\n\n'.join(paragraphs[1:])+'\n\nSources: immutable raw commit 23548ce37; native manifest, verification.json, execution-receipt.json and canonical custody sidecar. Graph source: graph-source.json.\n'
    (HERE/'report.md').write_text(md)
    styles = getSampleStyleSheet()
    styles['BodyText'].fontSize = 9
    styles['BodyText'].leading = 11
    story = [Paragraph('Fixed Prym rank census', styles['Title']), Paragraph('RUN-ECDLP-ea49a6 / EXP-ECDLP-d6d8e8', styles['Heading2']),
             Paragraph(paragraphs[0], styles['BodyText']), Spacer(1, 8), drawing, Spacer(1, 8)]
    t = Table([header]+table, hAlign='LEFT')
    t.setStyle(TableStyle([('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,-1),7),
                          ('BACKGROUND',(0,0),(-1,0),HexColor('#e8eef7')),('GRID',(0,0),(-1,-1),0.25,HexColor('#9aa8bb'))]))
    story.extend([t, Spacer(1, 10)])
    for paragraph in paragraphs[1:]:
        story.append(KeepTogether([Paragraph(paragraph, styles['BodyText']), Spacer(1, 7)]))
    story.append(Paragraph('Immutable evidence: raw commit 23548ce37; manifest, verification.json, execution-receipt.json and canonical custody sidecar. Diagram source: graph-source.json.', styles['BodyText']))
    SimpleDocTemplate(str(HERE/'report.pdf'), topMargin=30, bottomMargin=30).build(story)


if __name__ == '__main__':
    main()
