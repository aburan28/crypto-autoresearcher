"""Derived views of retained census bytes; performs no collection."""
import json
from pathlib import Path


def render(directory, result, experiment):
    from reportlab.graphics import renderSVG
    from reportlab.graphics.shapes import Drawing, Rect, String
    from reportlab.lib.colors import HexColor
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
    directory = Path(directory)
    cells = result.get('cells', [])
    points = [dict(p=c['p'], curve_uid=c['curve_uid'], arm=c['arm'],
                   rows=len(c['rows']), rank=c['projection']['rank'], U=c['projection']['U']) for c in cells]
    drawing = Drawing(490, 200)
    drawing.add(String(4, 185, f'{directory.name}: rank modulo r / unknown columns', fontSize=10))
    for j, row in enumerate(points):
        x = 7+j*29
        drawing.add(Rect(x, 45, 8, row['U']*15, fillColor=HexColor('#becada'), strokeWidth=0))
        drawing.add(Rect(x+9, 45, 8, row['rank']*15, fillColor=HexColor('#235e9b'), strokeWidth=0))
        drawing.add(String(x, 34, f"{row['rank']}/{row['U']}", fontSize=7))
        drawing.add(String(x, 22, str(row['p']), fontSize=6))
        drawing.add(String(x, 11, '64' if row['arm']=='sample64' else '3584', fontSize=6))
    drawing.add(String(4, 0, 'x: field p / branches per source. Grey: U. Blue: rank. Exact finite matrices.', fontSize=7))
    renderSVG.drawToFile(drawing, str(directory/'graph.svg'))
    with (directory/'graph-source.json').open('x') as stream:
        json.dump(dict(run_id=directory.name, source='raw-result.json', points=points,
                       uncertainty='Exact census; no population or security extrapolation.'), stream, indent=2)
    text = (f'# {experiment} / {directory.name}\n\nObservations only; no scientific verdict or ECDLP gain claim.\n\n'
            f"Completed: {result.get('complete')}. Cells: {len(cells)}. Paired fixed factor bases and public sources; "
            '64 sampled branches versus all 3584 branches per source. Publicly exposed base logs are removed in both arms. '
            'U=0 cells are calibration only. No early stop at full rank.\n\n'
            '![Recorded projected ranks](graph.svg)\n\n'
            'Raw witnesses, rank progress, first full-rank locations, finite nullspace certificates and partial operation '
            'vectors: raw-result.json. All branch statuses and commitments: events.jsonl. '
            'Independent complete replay and its separate resource cost: verification.json. Native compacted stored forms '
            'and any artifact-store manifests retain the same content commitments.\n\n'
            'Costs include separately retained public-input search and collector counters, diagnostic wall/CPU time and '
            'peak producer RSS. Pow internals, Python bookkeeping, byte movement and independently verified operation counts '
            'remain missing; these are not a complete weighted S. No prescribed-computation proof is supplied.\n\n'
            'Exact command, clean source revision, source/input hashes, dependency versions and native admission: '
            'manifest.yaml, launch.json and execution-receipt.json. These toy observations establish no deployed-curve weakness.\n')
    (directory/'report.md').write_text(text)
    styles = getSampleStyleSheet()
    items = [Paragraph(experiment+' / '+directory.name, styles['Title']), Spacer(1, 10)]
    for paragraph in text.split('\n\n')[1:]:
        if paragraph.startswith('!['):
            items.append(drawing)
        else:
            items.extend([Paragraph(paragraph.replace('\n', ' '), styles['BodyText']), Spacer(1, 9)])
    SimpleDocTemplate(str(directory/'report.pdf')).build(items)
