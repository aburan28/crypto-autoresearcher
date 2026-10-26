"""Render retained finite matrices only; never constructs a relation."""
import json


def render(directory, result, experiment):
    from reportlab.graphics import renderSVG
    from reportlab.graphics.shapes import Drawing, Rect, String
    from reportlab.lib.colors import HexColor
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

    points = [dict(fixture_uid=c['curve_uid'], p=c['p'], b=c['b'],
                   rank=c['projection']['rank'], U=c['projection']['U'],
                   attempts=c['attempts'], rows=len(c['rows'])) for c in result.get('cells', [])]
    graph = dict(schema='prym-width-recorded-graph/v1', source='raw-result.json', points=points,
                 axes=dict(x='fixed curve B within field p', y='matrix columns modulo r'),
                 uncertainty='Exact finite matrices; no sampling interval or population claim.',
                 reference='Frozen m8 RUN-ECDLP-ea49a6: p4099 B13/B16 each rank0/U7 and zero rows. No m8 replay.',
                 cost_scope='Raw partial S only; no matched timing/cost comparison.')
    with (directory/'graph-source.json').open('x') as stream:
        json.dump(graph, stream, indent=2)
        stream.write('\n')
    drawing = Drawing(480, 225)
    drawing.add(String(10, 210, 'Recorded width stream: rank and projected unknown columns', fontSize=10))
    maximum = max([p['U'] for p in points]+[1])
    for i, point in enumerate(points):
        x, scale = 40+i*160, 145/maximum
        drawing.add(Rect(x, 40, 30, point['U']*scale, fillColor=HexColor('#b7c5d6'), strokeWidth=0))
        drawing.add(Rect(x+35, 40, 30, point['rank']*scale, fillColor=HexColor('#2454ad'), strokeWidth=0))
        drawing.add(String(x, 25, f"p={point['p']}, B={point['b']}: {point['rank']}/{point['U']}", fontSize=9))
    drawing.add(String(10, 5, 'Grey=U, blue=rank; exact column counts. Conditional finite panel only.', fontSize=8))
    renderSVG.drawToFile(drawing, str(directory/'graph.svg'))
    paragraphs = [
        f"Completed: {result.get('complete')}. Retained cells: {len(points)}. These are observations only.",
        'The scientific workload is the complete m16 stream on the same p4099 A2 B13 and B16 curves, generators and public sources as the frozen m8 reference. The new base preserves the old eight atoms and appends under the same public rule. Old m8 source order is materialized independently of the new fixture UID. No m8 scientific replay is included.',
        'For the frozen m8 reference, both p4099 curves had zero rows and rank0/U7. This follow-up is conditioned on those known cases; no unbiased fresh-curve or population inference is licensed. Input-derived U is reported beside measured rank. Old descriptor nesting does not imply monotonic accepted rows, rank or rank/U.',
        'events.jsonl retains every complete source-block status/digest/checkpoint and immediate accepted witness. raw-result.json retains public witnesses, native-to-projected signed maps, affine and augmented ranks, pivot rows, right-kernel bases, progress and raw counters. A failed/incomplete run is censored work, never mathematical negative evidence.',
        'Producer field/group/pow-call/hash vectors, stage vectors, online/final matrix units, encoded status/digest/event bytes and inline checker times are retained separately. Independent checker costs are in verification.json. Counters are partial S: pow internals, Python bookkeeping, general byte movement, complete independent arithmetic counters and compression/upload/readback/storage costs require reconciliation. No ECDLP speedup or security claim is made.',
        'Native authority, exact argv, clean source revision, input/source hashes, versions, timestamps and measured self RSS are recorded by the native manifest and environment. Canonical object custody and actual remote readback remain separate delivery obligations. Hashes and arithmetic replay do not prove prescribed execution.']
    text = '# '+experiment+' / '+directory.name+'\n\n'+'\n\n'.join(paragraphs)
    text += '\n\n![Recorded rank and unknown columns](graph.svg)\n'
    with (directory/'report.md').open('x') as stream:
        stream.write(text)
    styles = getSampleStyleSheet()
    items = [Paragraph(experiment+' / '+directory.name, styles['Title']), Spacer(1, 12), drawing]
    for paragraph in paragraphs:
        items.extend([Spacer(1, 10), Paragraph(paragraph, styles['BodyText'])])
    SimpleDocTemplate(str(directory/'report.pdf')).build(items)
