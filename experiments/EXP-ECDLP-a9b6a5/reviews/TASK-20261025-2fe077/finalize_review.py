"""Freeze the final reviewer record after all actual source and visual reads."""
import hashlib
import json
import os
import secrets
from datetime import datetime, timezone
from pathlib import Path

import jsonschema

ROOT = Path('/workspace/crypto-autoresearcher')
TASK = 'TASK-20261025-2fe077'
OUT = 'experiments/EXP-ECDLP-a9b6a5/reviews/'+TASK
BASE = 'experiments/EXP-ECDLP-a9b6a5'
PHASE = 'coordination/goals/GOAL-ECDLP-001/batches/BATCH-49720f/phase-seals/'+TASK


def encoded(obj):
    return (json.dumps(obj, indent=2)+'\n').encode()


def write(name, obj):
    body=encoded(obj)
    with (ROOT/OUT/name).open('xb') as stream:
        stream.write(body)
        stream.flush()
        os.fsync(stream.fileno())
    return {'path':OUT+'/'+name,'sha256':hashlib.sha256(body).hexdigest(),'bytes':len(body)}


def finish(reader,g):
    # These are real post-release source reads, including own earlier artifacts.
    results={name:json.loads(reader.read(OUT+'/'+name)) for name in
             ('verification.json','math-verification.json','control-verification.json','reference-verification.json','custody-verification.json','pdf-text-inspection.json','nonce-replay.json')}
    for name in ('verification.json','math-verification.json','control-verification.json','reference-verification.json','custody-verification.json'):
        assert results[name]['status']=='passed'
    derivation=reader.read(OUT+'/derivation.json')
    assert hashlib.sha256(derivation).hexdigest()=='ae7664788ea39e1e6401c4f7ed9e2686087443dcea3b584895c9c53666d737a8'
    plan=reader.read('ledger/handoffs/'+TASK+'.yaml')
    assert hashlib.sha256(plan).hexdigest()=='c348ead5736ad00ec9972ce4baf3c3551dbb0fd3003968ecafc93834c99905f3'
    seal=reader.read(PHASE+'/seal.json')
    release=reader.read(PHASE+'/release.json')
    assert hashlib.sha256(seal).hexdigest()=='0c4648409728e4bc2dac082cfdaf74a0d12b34e70e1be84409cfb23b192df304'
    assert hashlib.sha256(release).hexdigest()=='25270930f57b0f78604581b1dc48be05c5a366e08dfd87512dafcdb8b4f8ebaa'
    export_bytes=reader.read(BASE+'/export.json')
    export=json.loads(export_bytes)
    protocol=json.loads(reader.read(BASE+'/protocol.json'))
    schema=json.loads(reader.read('schemas/experiment-review.v1.json'))
    public_archive_path='coordination/goals/GOAL-ECDLP-001/batches/BATCH-49720f/archives/TASK-20261025-cc5781-verified-260f23a.json'
    public_archive=reader.read(public_archive_path)
    visual={'schema':'review-visual-inspection/v1','task_id':TASK,'recorded_at':g['now'](),
            'method':'Rendered the actual PDF to PNG with PyMuPDF; both page images were then opened with view_image in this reviewer session.',
            'pdf_sha256':results['pdf-text-inspection.json']['pdf_sha256'],
            'pages_inspected':[1,2],'page_images':[OUT+'/pdf-page-1.png',OUT+'/pdf-page-2.png'],
            'graph_legible':True,'table_legible':True,'run_ids_and_evidence_paths_present':True,
            'limits_present':True,'status':'passed',
            'observations':['Page1 shows U/rank bars and exact four-cell table; page2 shows coverage, controls, custody and cost limits.','No page clipping or missing text observed; graph legend is compact near its heading.']}
    visual_artifact=write('visual-inspection.json',visual)
    # Hash every existing own artifact through the same contemporaneous reader.
    # Final report/companion/manifest do not yet exist, preventing self-reference.
    artifact_bindings=[]
    for directory,subdirs,files in os.walk(ROOT/OUT):
        subdirs.sort()
        for name in sorted(files):
            path=Path(directory)/name
            relative=str(path.relative_to(ROOT))
            if relative==OUT+'/read-events.json':
                continue
            body=reader.read(relative)
            artifact_bindings.append({'path':relative,'sha256':hashlib.sha256(body).hexdigest(),'bytes':len(body)})
    original_code=next(v for v in artifact_bindings if v['path']==OUT+'/review.py')
    assert original_code['sha256']=='9d63ce6bbacbc4768107d6dad18e376f708a41e9b34cf624cb30cb4a5c83f32c'
    # Last reviewer source read: the event log includes this very read event.
    log_body=reader.read(OUT+'/read-events.json')
    events=reader.events
    assert json.loads(log_body)==events
    assert [v['seq'] for v in events]==list(range(1,len(events)+1))
    sources=list(dict.fromkeys(v['source'] for v in events if v['kind']=='read'))
    phases=json.loads(derivation)
    assert set(phases['sources_read'])=={v['source'] for v in events[:48]}
    assert events[48]['kind']=='seal' and events[49]['kind']=='unblind'
    log_binding={'path':OUT+'/read-events.json','sha256':hashlib.sha256(log_body).hexdigest(),'bytes':len(log_body)}
    artifact_bindings.append(log_binding)
    generated=g['now']()
    math=results['math-verification.json'];control=results['control-verification.json']
    ref=results['reference-verification.json'];custody=results['custody-verification.json']
    summary=results['verification.json']
    row_ids=[v['run_id'] for v in export['runs']]
    assert len(row_ids)==4
    expected={(str(v['b']),v['m']):v for v in summary['cells']}
    for row in export['runs']:
        key=(row['instance_id'][1:],16 if row['arm']=='m16_candidate' else 8)
        actual=expected[key]
        assert row['measurements']['counted']=={
            'attempted':actual['attempts'],'accepted':actual['accepted'],'U':actual['U'],
            'rank':actual['rank'],'augmented_rank':actual['augmented_rank'],'nullity':actual['nullity']}
        assert row['measurements']['wall_valid'] is False
    nonce_audit=results['nonce-replay.json']
    assert nonce_audit['status']=='passed' and nonce_audit['units_sampled']==nonce_audit['identical']==16 and nonce_audit['mismatched']==0
    review_id='REV-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+secrets.token_hex(3)
    companion={'schema':'experiment.review/v1','review_id':review_id,'created':generated,
               'export':{'path':'../../export.json','sha256':hashlib.sha256(export_bytes).hexdigest(),'export_id':export['export_id']},
               'protocol_sha256':protocol['freeze']['protocol_sha256'],
               'reviewer':{'runtime':'Codex','model':None,'session':'/root/prym_width_sealed_review','role':'validator',
                           'independence':{'same_session_as_producer':False,'same_host_class':None,'shares_code_with_producer':False,
                                           'declared_conflicts':['Producer/checker implementations were inspected only after the sealed deliberate release; no producer/checker arithmetic was imported or executed. Generic PyYAML and JSON Schema are used only for file formats.']}},
               'checks':[
                   {'id':'exact-content','kind':'hashes','result':'pass','detail':'73 current native source/input bindings, both native receipt artifact sets, stored/logical gzip content and20 export file bindings verified; own remote GET not performed.'},
                   {'id':'finite-workload','kind':'protocol_adherence','result':'pass','detail':'Exactly4587520 new m16 descriptors,128 source blocks, no early stop or extra scientific m8 arm; four export rows agree with independently verified native cells.'},
                   {'id':'planted-and-copied','kind':'controls','result':'pass','detail':'p101 positive prefix/alias paths passed;19 known-false copied objects and4 pointer/content mutations rejected.'},
                   {'id':'all-descriptors','kind':'replay','result':'pass','detail':'Fresh independent implementation matched every m16 status/digest and all164 principal/E1/E2/transported rows; full coverage exceeds a nonce sample.'},
                   {'id':'exact-matrices','kind':'recompute','result':'pass','detail':'Projected matrices/RHS, affine and augmented ranks, independent rows, pivots, kernels and source checkpoints recomputed.'},
                   {'id':'finite-only','kind':'statistics','result':'pass','detail':'Exhaustive finite census; no sampling interval or population significance is inferred. Conditioned historical selection is disclosed.'},
                   {'id':'limits','kind':'scope','result':'pass','detail':'Two fixed toy curves; no speedup/security/general obstruction/complete weighted S or prescribed-execution proof claim.'},
                   {'id':'native-provenance','kind':'provenance','result':'pass','detail':'Native commits/clean state/commands/receipts are bound. Export runtime/model/session/role remain honestly null. Publication custody is supplied by separate root/Coordinator records, not authenticated by this local byte audit.'},
                   {'id':'sealed-phases','kind':'blinding','result':'pass','detail':'Actual48 phase1 reads precede immutable derivation; Coordinator seal/unblind boundaries49/50 precede all protected reads. Final formal checker is a separate root action.'},
                   {'id':'counters-and-clocks','kind':'measurement_validity','result':'pass','detail':'Counts are finite exact cells; all export clocks invalid for performance evidence. Stage subtotals reconcile, but arithmetic primitive counters are not independently instrumented and remain partial S.'}],
               'replay':{'performed':True,'method':'Full4587520-descriptor census independently completed first; additional16 post-publication nonce-selected accepted-witness units then rechecked, each original plus transported principal/E1/E2. Counters here refer only to those16 sampled witness units. Conservative(1-f)^16 table applies to accepted-witness sampling, not to full census coverage.',
                         'units_sampled':16,'nonce':nonce_audit['nonce'],'identical':16,'mismatched':0,'miss_probability':nonce_audit['miss_probability']},
               'observations':['RUN-ECDLP-967315-b13:2293760 descriptors,97 rows,U15,rank13,augmented13,nullity2.',
                               'RUN-ECDLP-967315-b16:2293760 descriptors,67 rows,U15,rank9,augmented9,nullity6.',
                               'RUN-ECDLP-ea49a6-b13 and-b16:229376 historical descriptors each,0 rows,U7,rank0,nullity7. Accepted-witness embedding is vacuous on these cells; planted positive embedding passed.'],
               'judgments':[{'claim_id':'finite-observation','verdict':'supported_within_scope','basis':'All prescribed finite integrity checks passed; this judgment covers recorded measurement integrity only.','scope':'Exactly the two conditioned toy cells and declared validation controls.'},
                            {'claim_id':'no-attack-claim','verdict':'not_established','basis':'Attack, scaling, performance, complete-S and execution-proof claims are explicitly outside this protocol and were not tested.','scope':'No scientific hypothesis or security verdict.'}],
               'open_questions':['Native primitive-operation counter coverage and complete weighted S remain unreconciled.','No fresh reviewer remote GET or independent publication-time authentication was performed.','Producer runtime/model/session/role provenance is absent and remains null.','Historical private source/input closure outside the prospective allowlist was not inspected.'],
               'recommendation':{'action':'no_action','reason':'No additional run is needed to complete this scoped integrity review; the Coordinator owns archival publication and any official interpretation.'},
               'asserts_nothing_about':['official research status','ECDLP speedup or security','general rank obstruction','complete weighted S','prescribed-execution proof']}
    jsonschema.Draft202012Validator(schema).validate(companion)
    report={'schema':'prym-fresh-independent-review/v1','task_id':TASK,'generated_at':generated,
            'reviewer_session':'/root/prym_width_sealed_review','phase1_derivation_sha256':hashlib.sha256(derivation).hexdigest(),
            'plan_sha256':hashlib.sha256(plan).hexdigest(),'checked_scope':summary['checked_scope'],
            'finite_observations':summary['cells'],'known_false_controls':control['known_false_copies'],
            'positive_controls':{'prefix':control['positive_prefix'],'alias':control['alias_positive']},
            'principal_witness_scope':{'all_rows':164,'required_samples':{str(v['b']):v['required_principal_sample_indices'] for v in math['cells']},'wider_than_required':True,'additional_nonce_selected_witness_units':16,'nonce_drawn_at':nonce_audit['drawn_at']},
            'source_code_imports':{'producer_arithmetic':False,'checker_arithmetic':False,'own_sealed_review_arithmetic':True,'generic_parsers':['PyYAML','jsonschema']},
            'cost_checks':summary['cost_checks'],'evidence_artifacts':artifact_bindings,
            'publication_custody_record':{'path':public_archive_path,'sha256':hashlib.sha256(public_archive).hexdigest(),'scope':'Read as separate Coordinator publication/custody evidence, not reviewer remote GET or proof of chronology.'},
            'joint_findings':[
                {'joint':'public_input_projection_and_support','verdict':'holds','detail':'Sealed fresh public arithmetic recounts r4021/r4111, reconstructs base/prefix and64 signed public-source pairs, U8=7/U16=15, descriptor cardinalities and quotient/infinity conventions.'},
                {'joint':'complete_stream_and_old8_embedding','verdict':'holds','detail':'All4587520 m16 statuses/digests and128 blocks matched; all458752 old8 descriptors and transported keys embed; selected historical streams matched; planted positive handles vacuous archived accepted embedding.'},
                {'joint':'native_witness_rank_and_transport','verdict':'holds','detail':'All164 principal/E1/E2/transported witnesses plus finite matrices/ranks/kernels/checkpoints matched; false source/lift/U/pivot/kernel/transport copies rejected.'},
                {'joint':'custody_and_cost_limits','verdict':'holds','detail':'73 current source/input bindings and all native stored/logical raw/artifact/export bytes checked. Producer GET, local cache access, incomplete primitive counters and no execution proof remain distinctly scoped.'}],
            'review_attestation':{'task_id':TASK,'joints_owned':['public_input_projection_and_support','complete_stream_and_old8_embedding','native_witness_rank_and_transport','custody_and_cost_limits'],
                                  'sources_read':sources,'read_sibling_reports':False,'blind_from_respected':True,'verdict':'holds',
                                  'phased_release':{'schema':'sealed-blind-review/v1','events':events}},
            'procedure_deviations':[],
            'execution_and_scope_notes':['Validation replay writes no official run record or new scientific arm.','All164 principal/E2 rows were checked, explicitly wider than the fixed sample.','The phase1 polynomial f-v^2 differs by a global sign from stored v^2-f; this changes residual coefficients by a unit, not roots/divisors. Native source lift is -[a]P; hyperelliptic bit0 and deck bit1 implement the sealed intrinsic sign table.','Final exact formal CLI checks are root actions after this quiescent freeze, with separate actual outputs; no pass is asserted on their behalf.'],
            'limitations':summary['limitations'],'no_scientific_verdict':True,'prescribed_execution_proof':False,'reviewer_fresh_remote_GET':False,
            'last_actual_reviewer_read_at':events[-1]['at'],'actual_read_event_count':len(events),'source_count':len(sources),
            'formal_checks':{'status':'pending separate-actor root final checks','requested':['tools/check_review_independence.py --no-addenda --plan exact_handoff --reports report.json','tools/experiment_protocol.py review validate experiment-review.json']},
            'visual_inspection':visual_artifact,'read_events':log_binding}
    companion_artifact=write('experiment-review.json',companion)
    report_artifact=write('report.json',report)
    artifact_bindings += [companion_artifact,report_artifact]
    manifest=write('artifact-manifest.json',{'schema':'prym-review-artifacts/v1','task_id':TASK,'generated_at':g['now'](),'artifacts':artifact_bindings,
                                          'scope':'Exact final reviewer bytes; final separate-actor formal-check artifacts may be archived alongside this manifest.'})
    print(json.dumps({'quiescent':True,'report':report_artifact,'companion':companion_artifact,'manifest':manifest,
                      'events':log_binding,'last_read_at':events[-1]['at'],'generated_at':generated,
                      'actual_read_events':len(events),'unique_sources':len(sources),'review_id':review_id},indent=2),flush=True)
