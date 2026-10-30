"""Render recorded width observations; no scientific computation or replay."""
from pathlib import Path
import hashlib
import json
import shutil
import sys
from xml.sax.saxutils import escape

ROOT = Path('/workspace/prym-width-run')
EXPERIMENT = 'EXP-ECDLP-a9b6a5'
RUN = 'RUN-ECDLP-967315'


def main():
    from reportlab.graphics.shapes import Drawing, Rect, String
    from reportlab.graphics import renderSVG
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    run = ROOT/f'experiments/{EXPERIMENT}/runs/{RUN}'
    cache = ROOT/f'experiments/{EXPERIMENT}/export-inputs/{RUN}'
    load = lambda path: json.loads(path.read_text())
    raw, check, receipt = (load(cache/name) for name in ['raw-result.json', 'verification.json', 'execution-receipt.json'])
    launch, env = (load(run/name) for name in ['launch.json', 'environment.json'])
    export = load(ROOT/f'experiments/{EXPERIMENT}/export.json')
    assert raw['complete'] and check['status'] == 'passed' and not check['failed_checks']
    assert sum(c['attempts'] for c in raw['cells']) == 4587520
    dest = ROOT/f'experiments/{EXPERIMENT}/reports/run-20261026T0559Z'
    dest.mkdir(parents=True, exist_ok=False)
    shutil.copyfile(__file__, dest/'render_report.py')
    points = [dict(b=c['b'], p=c['p'], curve_uid=c['curve_uid'], ec1_curve_uid=c['ec1_curve_uid'],
                   attempts=c['attempts'], accepted=len(c['rows']), rank=c['projection']['rank'],
                   U=c['projection']['U'], augmented_rank=c['projection']['augmented_rank'],
                   nullity=c['projection']['U']-c['projection']['rank'],
                   first_full_rank=c['first_full_rank'], reasons=c['reasons'],
                   operation_vector=c['attack_operation_vector'], wall_seconds=c['wall_seconds'],
                   cpu_seconds=c['cpu_seconds'], online_matrix_units=c['online_matrix_units'],
                   final_certificate_matrix_units=c['final_certificate_matrix_units'],
                   exploratory_nonzero_entries_per_column=[sum(row[j] != 0 for row in c['projection']['projected_rows']) for j in range(c['projection']['U'])]) for c in raw['cells']]
    graph = dict(schema='prym-width-session-recorded-graph/v1', run_id=RUN,
                 reference_run_id='RUN-ECDLP-ea49a6', candidate=points,
                 reference=[dict(b=b, attempts=229376, accepted=0, rank=0, U=7) for b in [13,16]],
                 source='Native raw-result.json and frozen historical reference; no new m8 replay.',
                 uncertainty='Exact finite enumeration; selected two curves, no population interval.')
    (dest/'graph-source.json').write_text(json.dumps(graph, indent=2)+'\n')
    drawing = Drawing(470, 215)
    drawing.add(String(8,200,'Recorded matrix rank and unknown columns',fontSize=12))
    for i,p in enumerate(points):
        for j,(label,U,rank) in enumerate([('m8',7,0),('m16',p['U'],p['rank'])]):
            x=30+i*225+j*85
            drawing.add(Rect(x,48,27,U*8,fillColor=colors.HexColor('#c2cdda'),strokeWidth=0))
            drawing.add(Rect(x+30,48,27,rank*8,fillColor=colors.HexColor('#2454ad'),strokeWidth=0))
            drawing.add(String(x,32,f'{label}: {rank}/{U}',fontSize=9))
        drawing.add(String(45+i*225,14,f'p=4099, A=2, B={p["b"]}',fontSize=10))
    drawing.add(String(8,183,'Grey: U; blue: rank modulo the corresponding prime r.',fontSize=9))
    renderSVG.drawToFile(drawing,str(dest/'graph.svg'))
    table = [['Curve B','Width','Attempts','Accepted rows','Rank / U','Nullity']]
    for p in points:
        table += [[str(p['b']),'8 reference','229,376','0','0 / 7','7'],
                  [str(p['b']),'16 candidate',f'{p["attempts"]:,}',str(p['accepted']),f'{p["rank"]} / {p["U"]}',str(p['nullity'])]]
    paragraphs = [
        'These are observations from one completed run, with no scientific verdict or performance claim. '+
        'Goal GOAL-ECDLP-001; hypothesis H-ECDLP-51f052; experiment '+EXPERIMENT+'; run '+RUN+'.',
        'The complete workload was two public synthetic prime-field curves, 64 public source scalars per curve, '+
        'and 35,840 tuple/sign branches per source: 4,587,520 new attempts. The frozen seed0 shuffle, generators '+
        'and old eight atoms were preserved while appending eight atoms. No new m8 trials, target Q, secret '+
        'labels, pilot or early-rank stop were used. One trial requested; one completed; zero failed or timed out.',
        'The historical m8 reference is RUN-ECDLP-ea49a6. Both cases were chosen because their old collection had '+
        'zero rows. The table reports exact finite counts; this conditioned panel supplies no population estimate. '+
        'Nullity is labeled arithmetic U minus recorded rank. A larger base also increases the unknown-column count.',
        'The native independent checker replayed every branch status and accepted witness, checked transported '+
        'encoding equations, and recomputed projected matrices, affine/augmented ranks and kernel certificates. '+
        'Its recorded status is passed with no failed checks. This separate implementation was developed in the '+
        'same engineering session; the independently staffed sealed review is a distinct stage.',
        'Exploratory arithmetic on the recorded matrices: all 15 unknown columns have a nonzero coefficient in '+
        'at least one accepted row on both curves. The nullities are therefore not explained by entirely untouched '+
        'columns in this retained stream. This support count was added after observing the data; it is not a '+
        'preregistered primary metric or a general rank obstruction.',
        'Field/group/pow-call/hash counters, matrix units, source checkpoints and every acceptance/rejection status '+
        'are retained in native data. These are partial S: pow internals, Python bookkeeping, general byte movement, '+
        'complete independent primitive counts, compression, upload and readback remain excluded. Times are '+
        'diagnostic on an unisolated host and all exported clocks have wall_valid=false. Historical and candidate '+
        'timings do not establish a matched cost comparison.',
        'Canonical compressed objects were published and freshly read back before the native receipt was sealed. '+
        'Logical and stored hashes, canonical manifests and custody records remain authoritative; export-inputs '+
        'is an ignored reconstructible analysis cache. No prescribed-computation proof or ECDLP reduction follows '+
        'from checksums, schema acceptance or replay.',
    ]
    wall = raw.get('wall_seconds'); cpu = raw.get('cpu_seconds')
    paragraphs += [f'Recorded construction wall/CPU: {wall} / {cpu} seconds. '+
                   f'Recorded independent-checker wall/CPU: {check.get("wall_seconds")} / {check.get("cpu_seconds")} seconds. '+
                   f'Source commit {env["commit"]}; native admission required a clean source. Python {env["python"]}.',
                   'Frozen protocol canonical SHA256: 6e88a562c9a1a53c20bbbfca346b3583da9bf23ae28bf5fbe80d33ab087a9163. '+
                   'The unified export has four logical rows: two completed candidate cells and two archived reference cells. '+
                   'A/A is signed/deck encoding transport of retained witnesses; planted positive, false-source and '+
                   'interruption controls were software tests, not extra target runs. Their frozen records are linked below.']
    command = 'python3 research/prym_factor_base_width_20261025/execute_with_storage.py run --plan experiments/EXP-ECDLP-a9b6a5/trial-plan.json --owner executor-prym-width-20261026 --epoch 1'
    links = [('../../runs/'+RUN+'/execution-receipt.json','Native receipt'),('../../runs/'+RUN+'/verification.json','Complete replay'),('../../artifact-deliveries/'+RUN+'/custody.json','Canonical custody'),('../../export.json','Unified export'),('../../export-analysis.json','Frozen descriptive analysis'),('../../protocol.json','Frozen protocol'),('../../../../research/prym_factor_base_width_20261025/software-tests.txt','Planted software controls')]
    md = '# Prym factor-base width: recorded run\n\n'+'\n\n'.join(paragraphs[:3])+'\n\n'
    md += '\n'.join(['| '+' | '.join(table[0])+' |','|'+'---|'*len(table[0])]+['| '+' | '.join(r)+' |' for r in table[1:]])+'\n\n![Recorded rank and U](graph.svg)\n\n'
    md += '\n\n'.join(paragraphs[3:])+f'\n\nExact outer command, workdir `/workspace/prym-width-run`:\n\n```sh\n{command}\n```\n\n'
    md += '\n'.join(f'- [{label}]({path})' for path,label in links)+'\n\nCanonical graph sources checked: existing historical census records remain unchanged; this report adds the width16 observation graph. No scientific frontier changes.\n'
    (dest/'report.md').write_text(md)
    source = dict(paragraphs=paragraphs, table=table, command=command, source_commit=env['commit'],
                  run_receipt_sha256=hashlib.sha256((run/'execution-receipt.json').read_bytes()).hexdigest(),
                  export_flow=export['flow'], links=links)
    (dest/'report-source.json').write_text(json.dumps(source,indent=2)+'\n')
    styles=getSampleStyleSheet(); items=[Paragraph('Prym factor-base width: recorded run',styles['Title'])]
    for text in paragraphs[:3]:items.extend([Spacer(1,9),Paragraph(escape(text),styles['BodyText'])])
    t=Table(table,repeatRows=1);t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e8eef5')),('FONTSIZE',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),6)]));items.extend([Spacer(1,12),t,Spacer(1,12),drawing])
    for text in paragraphs[3:]:items.extend([Spacer(1,9),Paragraph(escape(text),styles['BodyText'])])
    items += [Spacer(1,10),Paragraph('Exact outer command (workdir /workspace/prym-width-run): '+escape(command),styles['BodyText'])]
    items += [Spacer(1,10),Paragraph('Evidence: native receipt, verification, raw/event pointers, artifact-deliveries custody, protocol.json, export.json and export-analysis.json beside this report. '+RUN+' / '+EXPERIMENT,styles['BodyText'])]
    SimpleDocTemplate(str(dest/'report.pdf'),title='Prym width16 recorded observations').build(items)
    print(dest)


if __name__ == '__main__': main()
