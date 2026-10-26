"""Render own evidence report and chart from independently checked summaries."""
import copy
import hashlib
import io
import json
from pathlib import Path

from reportlab.graphics.shapes import Drawing, Rect, Line, String
from reportlab.graphics import renderPDF, renderSVG
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

ROOT = Path('/workspace/crypto-autoresearcher')
OUT = 'experiments/EXP-ECDLP-a9b6a5/reviews/TASK-20261025-2fe077'


def render(reader, g, h):
    names = ['math-verification.json', 'control-verification.json', 'reference-verification.json', 'custody-verification.json']
    inputs = {name: reader.read(OUT+'/'+name) for name in names}
    math, controls, reference, custody = [json.loads(inputs[name]) for name in names]
    raw = json.loads(reader.read('experiments/EXP-ECDLP-a9b6a5/export-inputs/RUN-ECDLP-967315/raw-result.json'))
    events = reader.read('experiments/EXP-ECDLP-a9b6a5/export-inputs/RUN-ECDLP-967315/events.jsonl')
    h['check'](raw['producer_artifact_counters']['events_jsonl_encoded_bytes'] == len(events), 'event byte instrumentation differs')
    costs = []
    for cell in raw['cells']:
        total = {}
        for stage in cell['attack_stage_operation_vectors'].values():
            for key, value in stage.items():
                total[key] = total.get(key, 0)+value
        h['check'](all(cell['attack_operation_vector'].get(k) == v for k,v in total.items()), 'stage/counter reconciliation differs')
        h['check'](cell['attack_operation_vector']['candidate_digest_bytes'] == 32*cell['attack_operation_vector']['candidate_hashes'], 'candidate byte count differs')
        costs.append({'b': cell['b'], 'reported_partial_operation_vector': cell['attack_operation_vector'],
                      'stage_sum_matches_reported_counters': True,
                      'storage_counter_bytes_independently_recomputed': True,
                      'arithmetic_primitive_counts_independently_instrumented': False,
                      'inline_checker_wall_seconds_diagnostic': cell['inline_checker_wall_seconds'],
                      'exclusions': ['pow internals','Python bookkeeping','general byte movement','complete weighted S','independent primitive instrumentation']})
    binding = {name: {'path': OUT+'/'+name, 'sha256': hashlib.sha256(body).hexdigest()} for name,body in inputs.items()}
    quantity_rows = []
    for old, new in zip(reference['cells'], math['cells']):
        quantity_rows += [{'b': old['b'], 'm':8, 'attempts':old['attempts_validation_replayed'], 'accepted':0, 'U':7, 'rank':0, 'augmented_rank':0, 'nullity':7},
                          {'b':new['b'], 'm':16, 'attempts':new['attempts_replayed'], 'accepted':new['accepted_rows'],
                           **{k:new['certificate'][k] for k in ('U','rank','augmented_rank','nullity')}}]
    graph_source = {'schema':'prym-review-finite-graph/v1','generated_at':g['now'](), 'data':quantity_rows,
                    'unit':'columns / exact finite matrix rank', 'sampling_uncertainty':'none for this complete finite census',
                    'run_ids':['RUN-ECDLP-967315','RUN-ECDLP-ea49a6'],
                    'evidence':binding, 'conditioning':'Same two curves selected after historical m8 zero rows; no population inference.'}
    graph_binding = h['save']('graph-source.json',graph_source)
    drawing = Drawing(510, 255)
    drawing.add(String(15,239,'Finite rank and public-projection dimension',fontName='Helvetica-Bold',fontSize=13))
    drawing.add(String(15,221,'Two conditioned F4099 curves; exact full-stream values',fontSize=9))
    left, bottom, height = 40, 52, 145
    for tick in range(0,17,4):
        y=bottom+height*tick/16
        drawing.add(Line(left,y,490,y,strokeColor=colors.HexColor('#d8dde3'),strokeWidth=0.5))
        drawing.add(String(left-18,y-3,str(tick),fontSize=8))
    drawing.add(String(4,204,'columns',fontSize=8))
    for i,row in enumerate(quantity_rows):
        x=65+110*i
        drawing.add(Rect(x,bottom,24,height*row['U']/16,fillColor=colors.HexColor('#dce4ec'),strokeColor=colors.HexColor('#8094a8')))
        drawing.add(Rect(x+28,bottom,24,height*row['rank']/16,fillColor=colors.HexColor('#1764a0'),strokeColor=colors.HexColor('#1764a0')))
        drawing.add(String(x+3,bottom+height*row['U']/16+5,str(row['U']),fontSize=9))
        drawing.add(String(x+32,bottom+height*row['rank']/16+5,str(row['rank']),fontSize=9))
        drawing.add(String(x-1,34,'B'+str(row['b'])+' / m'+str(row['m']),fontSize=9))
        drawing.add(String(x-4,20,'accepted '+str(row['accepted']),fontSize=8))
    drawing.add(Rect(280,234,10,8,fillColor=colors.HexColor('#dce4ec'),strokeColor=colors.HexColor('#8094a8')))
    drawing.add(String(294,234,'U',fontSize=9))
    drawing.add(Rect(331,234,10,8,fillColor=colors.HexColor('#1764a0'),strokeColor=colors.HexColor('#1764a0')))
    drawing.add(String(345,234,'rank(M)',fontSize=9))
    svg = renderSVG.drawToString(drawing)
    svg = svg.encode() if isinstance(svg,str) else svg
    with (ROOT/OUT/'graph.svg').open('xb') as stream:stream.write(svg)
    findings = [
        'Independent validation of finite observation integrity only. This report makes no scientific hypothesis, attack, speedup, security, complete-S or prescribed-execution-proof verdict.',
        'A fresh phase-one derivation was generated at 2026-10-26T06:30:40.398622Z, after its last read at 06:30:40.386171Z. The Coordinator seal at 06:31:39.053124Z and deliberate release at 06:33:33.695485Z were recorded as distinct authority boundary events; all protected reads followed release.',
        'The reviewer replayed every one of 4,587,520 m16 descriptors with independently written EC, polynomial, source-lift, interpolation, residual and canonical-identity code. All 128 status streams and branch commitments matched, including all rejected descriptors.',
        'All 164 accepted E1 equations, principal polynomial/divisor witnesses, E2 sums and transported encodings passed. The fixed first4/last4/8 SHA-ranked sample is identified in math-verification.json; checking all rows is the explicitly wider scope. Every projected matrix, affine/augmented rank, pivot span, right kernel, rank progress and source checkpoint passed.',
        'Both m8 reference cells were validation-replayed for 458,752 descriptors. All old8 descriptors and canonical keys embed under explicit fixture UID transport. There were zero historical accepted witnesses, so their empirical witness embedding is vacuous; a separate p101 positive witness tested the nonvacuous prefix path and the opposite-source alias path.',
        'All 19 known-false copies were rejected. They cover source a+1 and seeded-uniform alternatives, native lift, U/anchor/pivot/kernel/affine/augmented rank, dropped/duplicated/changed statuses, missing/duplicated/reordered source blocks, prefix, transported encoding and alias key. Four separate logical-content pointer mutations were rejected during custody verification.',
        'The 73 current native source/input bindings and all native receipt artifact hashes were rechecked. Three compressed remote-object representations were read from an existing public local cache; the remaining compressed raw representation was read from the repository. Stored SHA/size, gzip decoding and logical SHA/size matched, and 20 export file entries matched.',
        'The reviewer made no fresh remote GET. Producer GET attestations and the parent-supplied publication custody are separate from this local byte audit. Historical source/input maps are retained as receipt-bound metadata; excluded historical private fixtures/helpers were not read or re-executed.',
        'Counts and ranks describe exactly these two conditioned toy cases. There is no sampling uncertainty for this finite census, while implementation and custody limits remain. Native primitive-operation vectors reconcile with their stage subtotals, but were not independently instrumented. Pow internals, Python bookkeeping, general byte movement and a complete weighted S remain excluded. Clocks are diagnostic and are not a performance comparison.',
        'The native export honestly leaves producer runtime, model, session and role null. No missing provenance was copied from planned metadata. No canonical scientific graph is changed: this exclusive-scope review adds its own evidence-linked chart, and the native graph artifacts were content-hash checked.',
    ]
    columns=['B','m','attempts','accepted','U','rank','aug rank','nullity']
    table=[columns]+[[row[k] for k in ('b','m','attempts','accepted','U','rank','augmented_rank','nullity')] for row in quantity_rows]
    markdown='# Independent finite-stream integrity review\n\n'+'\n\n'.join(findings[:2])+'\n\n'
    markdown+='| '+' | '.join(columns)+' |\n| '+' | '.join(['---']*len(columns))+' |\n'
    markdown+='\n'.join('| '+' | '.join(map(str,row))+' |' for row in table[1:])+'\n\n'
    markdown+='\n\n'.join(findings[2:])+'\n\n'
    markdown+='Evidence: '+', '.join('['+name+']('+name+')' for name in names)+'.\n\n'
    markdown+='Runs: RUN-ECDLP-967315 and RUN-ECDLP-ea49a6. Task: TASK-20261025-2fe077. Claim tier: toy.\n'
    markdown+='\nThe Coordinator owns archival publication and any official research-state decision. Formal phase/independence and companion validation are performed by root against the final quiescent artifacts.\n'
    with (ROOT/OUT/'report.md').open('x') as stream:stream.write(markdown)
    styles=getSampleStyleSheet()
    styles['BodyText'].fontSize=9
    styles['BodyText'].leading=12
    story=[Paragraph('Independent finite-stream integrity review',styles['Title']),
           Paragraph('TASK-20261025-2fe077 | toy | RUN-ECDLP-967315 and RUN-ECDLP-ea49a6',styles['BodyText']),Spacer(1,10)]
    for paragraph in findings[:2]:story += [Paragraph(paragraph,styles['BodyText']),Spacer(1,7)]
    story += [drawing,Spacer(1,5)]
    grid=Table(table,hAlign='LEFT',colWidths=[28,28,65,50,28,35,48,38])
    grid.setStyle(TableStyle([('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,-1),8),
                              ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e6edf4')),
                              ('GRID',(0,0),(-1,-1),0.4,colors.HexColor('#b8c6d4')),
                              ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
    story += [grid,Spacer(1,9),Paragraph('Exact finite counts; no population or performance inference. The m8 reference is conditioned historical data.',styles['BodyText']),PageBreak()]
    for paragraph in findings[2:]:story += [Paragraph(paragraph,styles['BodyText']),Spacer(1,8)]
    story += [Paragraph('Evidence files: '+', '.join(names)+'. Commands and code are retained in review.py, phase2.py, controls_custody.py, render_review.py and the session transcript. The complete read timeline is read-events.json.',styles['BodyText'])]
    doc=SimpleDocTemplate(str(ROOT/OUT/'report.pdf'),pagesize=A4,rightMargin=38,leftMargin=38,topMargin=35,bottomMargin=35)
    doc.build(story)
    summary={'task_id':'TASK-20261025-2fe077','generated_at':g['now'](),'status':'passed',
             'cells':quantity_rows,'evidence':binding,'cost_checks':costs,
             'checked_scope':{'new_m16_statuses':4587520,'old_m8_validation_statuses':458752,
                              'new_scientific_m8_attempts':0,'all_accepted_principal_E1_E2_rows':164,
                              'negative_copied_objects':19,'negative_pointer_objects':4,
                              'current_native_source_input_bindings':73,'export_file_bindings':20},
             'no_scientific_verdict':True,'prescribed_execution_proof':False,
             'reviewer_fresh_remote_GET':False,'arithmetic_primitive_counters_independently_instrumented':False,
             'formal_checker_actor':'root after final quiescent freeze',
             'procedure_deviations':[],
             'graph_source':graph_binding,'graph_svg_sha256':hashlib.sha256(svg).hexdigest(),
             'limitations':findings[6:]}
    artifact=h['save']('verification.json',summary)
    print(json.dumps({'rendered':True,'verification':artifact,'graph_source':graph_binding}),flush=True)
    return summary
