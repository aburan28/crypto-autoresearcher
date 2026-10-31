#!/usr/bin/env python3
"""Generate only the two fresh outside custody indexes AFTER root publication.

This is a representation/file inventory tool, not scientific verification.
It reads completed outputs, never experiment/SDK/host arithmetic modules, and
never writes canonical files, changes source outputs, or performs network I/O.
"""
from pathlib import Path
import argparse,datetime,hashlib,json,re,sys
from reporting import E,RUN,SOURCE,BATCH,VIEW,CUSTODY,read,sha,desc,finished,fresh,encode,need
POST_INDEX=E+'/postrun/output-custody.json'
NATIVE_INDEX=E+'/reports/run-report-custody.json'
STORE='s3://setec-astronomy-artifacts/store/sha256/'

def regular_tree(root):
    root=Path(root)
    if not root.exists():return []
    found=[]
    for p in sorted(root.rglob('*')):
        need(not p.is_symlink(),'symlink output '+str(p))
        need(p.is_dir() or p.is_file(),'special output '+str(p))
        if p.is_file():found.append(p)
    return found

def receipt_map(paths):
    records=[];by={}
    for path in paths:
        p=Path(path);d=read(p);need(d.get('all_full_s3_gets_verified') is True,'actual completed storage receipt required')
        reads=d.get('readbacks',[])
        need(type(reads) is list,'readback receipt list')
        for r in reads:
            need(r.get('full_s3_get_verified') is True and type(r.get('bytes')) is int and r['bytes']>=0,'actual full GET record required')
            key=r['path'];entry={'sha256':r['sha256'],'bytes':r['bytes']}
            need(key not in by or by[key]==entry,'conflicting storage receipts');by[key]=entry
        records.append({'path_at_recording':str(p),'sha256':sha(p),'actual_verified_object_count':len(reads),'receipt':d})
    return records,by

def output_entry(repo,path,published):
    repo=Path(repo).resolve();p=Path(path);need(p.is_file() and not p.is_symlink() and p.resolve().is_relative_to(repo),'owned regular file required')
    logical=p.relative_to(repo).as_posix();digest=sha(p);size=p.stat().st_size
    storage={'form':'native_regular_file','logical_content_sha256':digest,'logical_content_bytes':size,'expected_Git_stored_path':logical,'expected_Git_stored_sha256':digest}
    # Later metadata/pointer files are themselves separately indexed. A hydrated
    # logical payload is retained on disk while Git stores exactly one pointer.
    if not p.name.endswith('.blob.json'):
        pointer=Path(str(p)+'.blob.json')
        need(not Path(str(p)+'.gz').exists() and not Path(str(p)+'.gz.blob.json').exists(),'ambiguous stored forms '+logical)
        if pointer.exists():
            q=read(pointer);need(q.get('schema')=='crypto.autoresearch.blob_pointer.v1' and q.get('encoding')=='identity','supported identity pointer required')
            need(q['sha256']==q['content_sha256']==digest and q['size']==q['content_size']==size and q['uri']==STORE+digest[:2]+'/'+digest,'pointer/payload binding mismatch')
            need(published.get(logical)=={'sha256':digest,'bytes':size},'new payload lacks actual full GET receipt '+logical)
            manifest=p.parent/'.artifacts.json';d=read(manifest)
            need(d['files'].get(p.name)=={'sha256':digest,'bytes':size},'modern same-payload authority missing '+logical)
            storage={'form':'identity_blob_pointer_with_exact_hydrated_payload','logical_content_sha256':digest,'logical_content_bytes':size,'expected_Git_stored_path':pointer.relative_to(repo).as_posix(),'expected_Git_stored_sha256':sha(pointer),'uri':q['uri'],'pointer_sha256':sha(pointer),'storage_manifest_path':manifest.relative_to(repo).as_posix(),'storage_manifest_sha256':sha(manifest),'full_GET_receipt_verified':True}
    return {'logical_path':logical,'sha256':digest,'bytes':size,'role':'administrative_metadata' if '/custody/' in logical or p.name.startswith('.') or p.name.endswith('.blob.json') else 'retained_producer_output','storage':storage}

def domain_files(repo):
    repo=Path(repo).resolve()
    post=regular_tree(repo/E/'postrun')+regular_tree(repo/SOURCE)
    for name in ['export.json','export.validation.json','.artifacts.json','.gitignore','export.json.blob.json','export.validation.json.blob.json']:
        p=repo/E/name
        if p.exists():post.append(p)
    native=regular_tree(repo/E/'reports')
    post={p.relative_to(repo).as_posix():p for p in post if p.relative_to(repo).as_posix() not in [POST_INDEX,NATIVE_INDEX]}
    native={p.relative_to(repo).as_posix():p for p in native if p.relative_to(repo).as_posix() not in [POST_INDEX,NATIVE_INDEX]}
    need(not set(post)&set(native),'inventory domains overlap')
    return post,native

def source_checks(repo):
    root=Path(repo)/CUSTODY
    # Exact actual command records are mandatory; no empty success placeholder.
    source=root/'source-check-export.command.json';derivative=root/'canonical-check-export.command.json'
    need(source.is_file(),'source actual check-export command record missing')
    s=read(source);need(type(s.get('returncode')) is int,'source check returncode missing')
    d=read(derivative) if derivative.is_file() else None
    if (Path(repo)/E/'export.json').exists():need(d is not None and type(d.get('returncode')) is int,'actual derivative file check required')
    return {'source':s,'derivative':d,'source_command_record_sha256':sha(source),'derivative_command_record_sha256':None if d is None else sha(derivative)}

def generate(repo,completion_path,storage_receipts,inspection_path,package,source_inspection_path=None):
    repo=Path(repo).resolve();completion=finished(completion_path);package=Path(package).resolve();need(not package.exists() and not package.is_relative_to(repo),'fresh outside index package required')
    records,published=receipt_map(storage_receipts);post,native=domain_files(repo);need(post and native,'actual postrun and report output domains required')
    launch=read(repo/RUN/'launch.json');receipt=read(repo/RUN/'execution-receipt.json');need(launch['started_at']==receipt['started_at'],'native timestamps differ')
    stamp=datetime.datetime.fromisoformat(launch['started_at']).astimezone(datetime.timezone.utc).strftime('%Y%m%dT%H%MZ');subtree=E+'/reports/run-'+stamp;pdf=repo/subtree/'report.pdf';need(pdf.is_file(),'actual native report PDF missing')
    inspection=read(inspection_path);need(inspection.get('all_pages_inspected') is True and type(inspection.get('page_count')) is int and inspection['page_count']>0 and inspection.get('pdf_sha256')==sha(pdf),'actual matching all-page native PDF inspection required')
    source_inspection=None if source_inspection_path is None else read(source_inspection_path)
    if source_inspection is not None and (repo/SOURCE/'report.pdf').is_file():need(source_inspection.get('pdf_sha256')==sha(repo/SOURCE/'report.pdf'),'source PDF inspection digest mismatch')
    checks=source_checks(repo);source=repo/SOURCE;result=read(source/'postrun-result.json') if (source/'postrun-result.json').is_file() else None
    contract=read(repo/BATCH/'admission/output-contract.v1.json');expected={}
    for name in sorted(set(contract['production_complete_files'])|set(contract['normal_return_files'])|set(contract['conditional_files'])):
        p=source/name
        expected[name]=({'present':True,**desc(p,p.relative_to(repo).as_posix())} if p.is_file() else {'present':False,'reason':'No source output emitted at the actual completed process destination; preserve the actual returncode/errors and source-stage semantics.','source_condition':contract['conditional_files'].get(name),'source_status':None if result is None else result.get('status')})
    public=read(repo/VIEW/'supervisor/modal/collected/public-cohort.json');ids=[c['curve_id'] for c in public['curves']];need(len(ids)==len(set(ids)),'duplicate retained public curve IDs')
    dynamic=[]
    for ident in ids:
        for kind in ['uniform']+(['null'] if re.fullmatch(r'(discovery|validation)-(10|13|16)-[0-3]',ident) else []):
            name=kind+'-'+ident+('.jsonl' if kind=='uniform' else '.json');p=source/name
            dynamic.append({'kind':kind,'actual_curve_id':ident,'path':p.relative_to(repo).as_posix(),'present':p.is_file(),'bytes':p.stat().st_size if p.is_file() else None,'sha256':sha(p) if p.is_file() else None,'absence_reason':None if p.is_file() else 'Not emitted by the actual source process; no dynamic observation substituted.'})
    postentries=[output_entry(repo,p,published) for _,p in sorted(post.items())];nativeentries=[output_entry(repo,p,published) for _,p in sorted(native.items())]
    need({e['logical_path'] for e in postentries}==set(post) and {e['logical_path'] for e in nativeentries}==set(native),'exact file inventory')
    for entries in [postentries,nativeentries]:need(not {e['logical_path'] for e in entries}&{POST_INDEX,NATIVE_INDEX},'self/cross-index cycle')
    input_names=[E+'/protocol.json',E+'/trial-plan.json',RUN+'/launch.json',RUN+'/execution-receipt.json',RUN+'/manifest.yaml',RUN+'/raw-result.json',RUN+'/modal-evidence-manifest.json',VIEW+'/view-provenance.json',VIEW+'/supervisor/manifest.yaml',BATCH+'/archives/TASK-20261029-5635b4/snapshot-receipt.json',BATCH+'/archives/TASK-20261029-5b0e13/snapshot-receipt.json']
    input_names += [BATCH+'/reviews/TASK-20261029-3b5feb/'+n for n in ['report.md','checks.json','read-attestation.yaml']]
    inputs=[desc(repo/x,x) for x in input_names]
    common={'task_id':'TASK-20261029-cbafca','recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_completion_command':completion,'native_status_unchanged':'invalid_output/check1/publishedfalse','scientific_status_transition':False,'inputs':inputs,'excluded_indexes':[POST_INDEX,NATIVE_INDEX],'no_self_or_cross_index_hash_cycle':True,'canonical_publication_status':'outside prepared final indexes; root must materialize exact bytes then actual snapshot verifies Git/storage custody.'}
    pindex={**common,'schema':'classical.ecdlp.controlled-followup.postrun-custody/v1','source_output_root':SOURCE,'source_postrun_result':result,'source_export':None if not (source/'export.json').is_file() else desc(source/'export.json',SOURCE+'/export.json'),'actual_export_checks':checks,'source_generated_report_inspection':source_inspection if source_inspection is not None else {'status':'not_attested_by_this_index','reason':'Source-generated PDF is preserved; no inspection pass invented.'},'expected_source_outputs':expected,'dynamic_source_outputs':dynamic,'actual_storage_receipts':records,'storage_manifests':[e for e in postentries if e['logical_path'].endswith('/.artifacts.json')],'inventory_domain':{'include':[E+'/postrun/**',SOURCE+'/**',E+'/export.json',E+'/export.validation.json','actual experiment-root storage sidecars when present'],'exclude':[POST_INDEX,NATIVE_INDEX],'overlay':'DEC-20261029-346631 full-native JSON representation only'},'files':postentries,'calibration_resolution':'Frozen1/512field NOTQUALIFIED; exact prelaunch note and later Coordinator assessment separately retained; actual signednumerator/allretainedn/undefined/full1800/no grid-as-CI or defined-only renormalization.'}
    nindex={**common,'schema':'classical.ecdlp.controlled-followup.native-run-report-custody/v1','actual_first_trial_started_at':launch['started_at'],'actual_directory':subtree,'timestamp_source':desc(repo/RUN/'launch.json',RUN+'/launch.json'),'timestamp_cross_check':desc(repo/RUN/'execution-receipt.json',RUN+'/execution-receipt.json'),'covered_runs':[{'path':RUN,'native_status':'invalid_output','driver_returncode':receipt['returncode'],'native_checker_returncode':receipt['check_returncode'],'native_published':receipt['published']}],'pdf_inspection':inspection,'source_generated_report_inspection':source_inspection if source_inspection is not None else {'status':'not_attested_by_this_index'},'graph_data':subtree+'/observations.json','graph_source':subtree+'/draw_observations.py','graph_rendering':subtree+'/observations.svg','PDF_source':subtree+'/report.typ','actual_storage_receipts':records,'storage_manifests':[e for e in nativeentries if e['logical_path'].endswith('/.artifacts.json')],'inventory_domain':{'include':[E+'/reports/**'],'exclude':[POST_INDEX,NATIVE_INDEX]},'files':nativeentries,'canonical_graphs':'No mathematical or official scientific status changed by this producer report; local actual-observation graph only.'}
    fresh(package/POST_INDEX,encode(pindex));fresh(package/NATIVE_INDEX,encode(nindex));delivery={'schema':'classical.ecdlp.postrun-final-index-delivery/v1','task_id':'TASK-20261029-cbafca','package_directory':str(package),'path_sha256':{x:sha(package/x) for x in [POST_INDEX,NATIVE_INDEX]},'exact_domains':{'postrun_files':len(postentries),'native_files':len(nativeentries)},'all_actual_output_sets_hashed':True,'original_source_and_native_bytes_unchanged':True,'both_indexes_exclude_both_indexes':True,'root_materialization_and_snapshot_pending':True};fresh(package/'delivery-manifest.json',encode(delivery));print(json.dumps(delivery,indent=2))

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repo',type=Path,required=True);p.add_argument('--completion-record',type=Path,required=True);p.add_argument('--storage-receipt',type=Path,action='append',required=True);p.add_argument('--native-pdf-inspection',type=Path,required=True);p.add_argument('--source-pdf-inspection',type=Path);p.add_argument('--package',type=Path,required=True);a=p.parse_args();generate(a.repo,a.completion_record,a.storage_receipt,a.native_pdf_inspection,a.package,a.source_pdf_inspection)
if __name__=='__main__':main()
