"""Prospective manifest transport. Not an approval or an experiment launcher.

This component fills the producer-output schema gap identified in the SNFS
repair packet. An approved future wrapper may call it before the supervisor
seals a new run. It never runs a producer, changes a receipt or writes inside
an already sealed run. No historical record is migrated by this module.
"""
from pathlib import Path
import hashlib,json,os
import yaml


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(run_dir, *, experiment_id, run_id, scientific_parameters,
            producer_manifest_name='producer-manifest.yaml'):
    """Write only a new, unsealed run's transport manifest from actual files.

    The caller first moves its producer manifest to producer-manifest.yaml.
    Scientific values and original producer bytes are retained, never inferred.
    The supervisor remains responsible for checking output and sealing a receipt.
    """
    run_dir=Path(run_dir).resolve()
    if (run_dir/'execution-receipt.json').exists():raise ValueError('Run is sealed or terminal; use an additive record, never transport in place.')
    if run_dir.name!=run_id or run_dir.parent.name!='runs' or run_dir.parent.parent.name!=experiment_id:raise ValueError('Run-directory identity mismatch')
    if not scientific_parameters:raise ValueError('Frozen scientific parameters must be explicit')
    launch=json.loads((run_dir/'launch.json').read_text());environment=json.loads((run_dir/'environment.json').read_text())
    producer=run_dir/producer_manifest_name;flat=yaml.safe_load(producer.read_text())
    if not isinstance(flat,dict) or flat.get('experiment_id')!=experiment_id:raise ValueError('Producer experiment identity mismatch')
    if launch['run_id']!=run_id:raise ValueError('Supervisor run identity mismatch')
    if flat.get('id',flat.get('run_id')) not in (None,run_id):raise ValueError('Producer run identity mismatch')
    commit=launch['authority']['commit']
    if environment.get('commit')!=commit:raise ValueError('Launch/environment source commit mismatch')
    if not environment.get('source_sha256'):raise ValueError('Frozen source bindings are absent')
    raw=run_dir/'raw-result.json'
    if not raw.is_file():raise ValueError('Producer raw output is missing')
    raw_digest=digest(raw)
    if flat.get('raw_result_sha256') not in (None,raw_digest):raise ValueError('Producer raw-output digest mismatch')
    body=dict(id=run_id,experiment_id=experiment_id,status='observation',
        code=dict(commit=commit,command=launch['argv'],source_sha256=environment['source_sha256'],
            trial_plan_sha256=launch['plan_sha256'],producer_manifest_sha256=digest(producer)),
        environment=environment,inputs=dict(parameters=scientific_parameters),
        timing=dict(supervisor_started_at=launch['started_at'],producer_timing={k:v for k,v in flat.items() if 'seconds' in k or k.endswith('_unix')},
            note='Only literal observed timing fields are copied. A final supervisor duration is not invented before its receipt exists.'),
        result=dict(raw_result=str(raw),raw_result_sha256=raw_digest,outcome=None,
            certificate=dict(kind='none'),output_validated=False,scientific_review_verified=False,
            outcome_note='Producer observations only. Supervisor checker, schema validation and receipt are pending.'),
        transport=dict(producer_manifest=producer_manifest_name,producer_manifest_sha256=digest(producer),
            producer_fields_copied_at_top_level=True,scientific_parameters_changed=False))
    # Retain legacy keys so the original checker can still read its own fields.
    output={**flat,'run':body}
    target=run_dir/'manifest.yaml'
    with target.open('x') as f:yaml.safe_dump(output,f,sort_keys=False)
    return target
