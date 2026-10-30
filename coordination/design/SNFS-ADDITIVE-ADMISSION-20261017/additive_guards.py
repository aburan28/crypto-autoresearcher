"""Proposed fail-closed additive-only guards. Not wired into production admission."""
from __future__ import annotations
import json, re
from pathlib import Path
import yaml
from experiment_preapproval import _bound_file, _git_blob, _hash, _mapping, _read
from experiment_execution import safe_path
SCHEMA='crypto.autoresearch.additive_preapproval_packet.v1'

def assess_original(root,packet,canonical,raw,plan,blockers):
    """Return supplemental input bindings only; never replace frozen scientific fields."""
    exp=packet['experiment_id'];ref=packet.get('source_ref');decision=packet.get('approval_decision_id')
    for label,p in canonical.items():
        try:safe_path(root,p)
        except (ValueError,TypeError):blockers.append(f'additive canonical path unsafe: {label}')
    source=packet.get('original') or {}
    expected=f'experiments/{exp}/trial-plan.json'
    if source.get('trial_plan')!=expected:
        blockers.append('additive original: exact canonical original plan required');return {}
    try:
        old_bytes=safe_path(root,expected).read_bytes();old=json.loads(old_bytes)
        if source.get('trial_plan_sha256')!=_hash(old_bytes) or _git_blob(root,ref,expected)!=old_bytes:
            blockers.append('additive original: original plan hash/publication mismatch')
        spec_bytes=safe_path(root,canonical['specification']).read_bytes()
        if raw.get('specification')!=spec_bytes or source.get('specification_sha256')!=_hash(spec_bytes):
            blockers.append('additive original: frozen specification bytes changed')
        spec=yaml.safe_load(spec_bytes);spec=spec.get('experiment',spec)
        if decision==spec.get('approved_by') or decision==old.get('approved_by'):
            blockers.append('additive approval: fresh prospective correction decision required')
        for identity in ('experiment_id','hypothesis_id','goal_id','question_id'):
            if old.get(identity)!=plan.get(identity):blockers.append(f'additive identity changed: {identity}')
        if plan.get('task_id')==old.get('task_id') or plan.get('queue')==old.get('queue'):
            blockers.append('additive ownership: new queue/task namespace required; original claim is not transferred')
    except (OSError,ValueError,TypeError) as exc:
        blockers.append(f'additive original: unavailable: {exc}');return {}
    preview=packet.get('preview') or {};path=packet.get('amendment')
    data=_read(preview.get('amendment'),'amendment',blockers) if preview.get('amendment') else None
    document=_mapping(data,'amendment',blockers,kind='yaml');am=document.get('protocol_amendment',document)
    prefix=f'experiments/{exp}/amendments/'
    if not isinstance(path,str) or not path.startswith(prefix) or path==prefix:
        blockers.append('additive amendment: scoped additive path required')
    try:
        if path:safe_path(root,path)
    except ValueError as exc:blockers.append(f'additive amendment: unsafe path: {exc}')
    if data is None or plan.get('amendment')!={'path':path,'sha256':_hash(data)}:
        blockers.append('additive amendment: exact plan-to-amendment hash binding required')
    if (am.get('experiment_id')!=exp or am.get('approved_by')!=decision or am.get('status')!='approved'
        or am.get('frozen') is not True or am.get('scientific_parameters_changed') is not False
        or am.get('original_trial_plan_sha256')!=_hash(old_bytes)):
        blockers.append('additive amendment: prospective approval/identity/original-plan binding incomplete')
    allowed={'experiment_id','approved_by','status','frozen','scientific_parameters_changed','original_trial_plan_sha256','kind','input_bindings','manifest_transport','retry_receipts'}
    if set(am)-allowed:blockers.append('additive amendment: unsupported override fields')
    for family in ('source_sha256','input_sha256'):
        for p,h in (old.get(family) or {}).items():
            if (plan.get(family) or {}).get(p)!=h:blockers.append(f'additive closure: original {family} removed or changed: {p}')
    before=old.get('trials') or [];after=plan.get('trials') or []
    if len(before)!=len(after):blockers.append('additive scientific scope: trial count changed')
    kind=am.get('kind')
    if kind not in ('transport_repair','retry'):blockers.append('additive kind: only transport_repair or retry supported')
    for prior,current in zip(before,after):
        allowed_change={'run_id','artifacts','check_argv'}
        if any(prior.get(k)!=current.get(k) for k in (set(prior)|set(current))-allowed_change):
            blockers.append('additive scientific scope: argv, identity, dependencies or resources changed')
        if not set(prior.get('artifacts',[]))<=set(current.get('artifacts',[])):
            blockers.append('additive archive: original trial artifacts removed')
        rid=current.get('run_id');runpath=f'experiments/{exp}/runs/{rid}'
        if (root/runpath).exists() or _git_blob(root,ref,runpath+'/execution-receipt.json') is not None:
            blockers.append('additive run identity: new destination already exists; never reuse an attempted run')
        if kind=='transport_repair' and rid!=prior.get('run_id'):
            blockers.append('additive transport: original unattempted run identity must be retained')
        if kind=='retry':
            if rid==prior.get('run_id'):blockers.append('additive retry: fresh immutable RUN ID required')
            receipt=(am.get('retry_receipts') or {}).get(prior.get('run_id'),{})
            receipt_path=f"experiments/{exp}/runs/{prior.get('run_id')}/execution-receipt.json"
            if receipt.get('path')!=receipt_path:
                blockers.append('additive retry: original immutable receipt path missing')
            else:
                _bound_file(root,receipt_path,receipt.get('sha256'),ref,blockers,'additive retry receipt')
                try:
                    outcome=json.loads((root/receipt_path).read_bytes())
                    if outcome.get('status') not in ('infrastructure_error','invalid_output','interrupted','watchdog_expired','memory_limit_exceeded','claim_expired'):
                        blockers.append('additive retry: prior receipt is not an eligible terminal failure')
                    if outcome.get('run_id')!=prior.get('run_id') or outcome.get('trial_id')!=prior.get('id'):
                        blockers.append('additive retry: receipt identity mismatch')
                except (OSError,ValueError):blockers.append('additive retry: prior receipt unreadable')
        if current.get('check_argv')!=prior.get('check_argv'):
            transport=(am.get('manifest_transport') or {}).get(prior.get('id'),{})
            wrapper=transport.get('wrapper_source') or {}
            original=prior.get('check_argv') or []
            argv=['python3',wrapper.get('path'),'--original-checker-json',json.dumps(original,separators=(',',':')),'--run-dir','{run_dir}']
            if current.get('check_argv')!=argv or wrapper.get('sha256')!=(plan.get('source_sha256') or {}).get(wrapper.get('path')):
                blockers.append('additive manifest transport: wrapper command/source binding mismatch')
            if 'producer-manifest.yaml' not in current.get('artifacts',[]):
                blockers.append('additive manifest transport: original producer manifest must be retained')
            fixture=transport.get('fixture') or {}
            if not fixture.get('path'):blockers.append('additive manifest transport: committed schema-fixture receipt required')
            else:_bound_file(root,fixture['path'],fixture.get('sha256'),ref,blockers,'additive manifest transport fixture')
    return am.get('input_bindings') or spec.get('input_bindings') or {}
