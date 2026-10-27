"""One credential-free VM calibration controller. Root supplies SDK process env."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import sys

HERE = Path(__file__).resolve().parent

def utc():
    return datetime.now(timezone.utc).isoformat()

def sha(data):
    return hashlib.sha256(data).hexdigest()

def write(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')

def regular_bytes(sb, path):
    info = sb.filesystem.stat(path)
    if getattr(info.type, 'value', info.type) != 'file':
        raise ValueError('Expected remote regular file: '+path)
    return sb.filesystem.read_bytes(path)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise ValueError('Fresh calibration output directory required')
    plan = json.loads((HERE/'plan.json').read_text())
    for item in plan['inputs']:
        data = (HERE/item['path']).read_bytes()
        assert len(data) == item['bytes'] and sha(data) == item['sha256']
    args.out.mkdir(parents=True)
    import modal
    assert modal.__version__ == '1.6.2'
    record = {'schema': 'classical.ecdlp.runtime-calibration-controller/v1',
              'started_at': utc(), 'sdk_version': modal.__version__, 'plan_sha256': sha((HERE/'plan.json').read_bytes()),
              'purpose': plan['purpose'], 'scientific_confirmation_measurement': False,
              'wall_valid': False, 'automatic_retry': False, 'completed': False,
              'create_calls': 0, 'worker_exec_calls': 0, 'termination_requested': False,
              'inputs_staged': [], 'files_collected': []}
    sb = None
    try:
        app = modal.App.lookup('classical-ecdlp-validation', environment_name='main', create_if_missing=False)
        assert app.app_id == plan['app_id']
        image = modal.Image.from_id(plan['image_id'])
        record['create_calls'] = 1
        write(args.out/'create-intent.json', record)
        sb = modal.Sandbox.create('sleep', '600', app=app, image=image, runtime='vm', block_network=True,
             cpu=(2,2), memory=(12288,12288), timeout=600, secrets=[], include_oidc_identity_token=False, workdir='/work')
        record.update({'sandbox_id': sb.object_id, 'app_id': app.app_id, 'image_id': image.object_id})
        write(args.out/'sandbox-created.json', record)
        info = regular_bytes(sb, '/opt/study/build-info.json')
        assert sha(info) == plan['build_info_sha256']
        (args.out/'build-info.json').write_bytes(info)
        prep = sb.exec('python3','-c',"from pathlib import Path;Path('/work/calibration').mkdir()", timeout=30)
        assert prep.wait() == 0
        for name in ['fixtures.tsv','targets.tsv','settings.tsv','plan.json','worker.py']:
            data = (HERE/name).read_bytes()
            remote = '/work/calibration/'+name
            sb.filesystem.write_bytes(data, remote)
            assert sha(regular_bytes(sb, remote)) == sha(data)
            record['inputs_staged'].append({'path':name,'bytes':len(data),'sha256':sha(data),'readback_verified':True})
            (args.out/name).write_bytes(data)
        prep = sb.exec('chown','-R','1000:1000','/work/calibration', timeout=30)
        assert prep.wait() == 0
        argv = ['env','-i','PATH=/usr/local/bin:/usr/bin:/bin','HOME=/work','TMPDIR=/work/tmp',
                'OMP_NUM_THREADS=1','PYTHONDONTWRITEBYTECODE=1','setpriv','--reuid=1000','--regid=1000',
                '--clear-groups','--no-new-privs','python3','/work/calibration/worker.py']
        record['worker_exec_calls'] = 1
        record['worker_argv'] = argv
        write(args.out/'worker-intent.json', record)
        proc = sb.exec(*argv, timeout=540)
        record['worker_returncode'] = proc.wait()
        (args.out/'worker.stdout.txt').write_text(proc.stdout.read())
        (args.out/'worker.stderr.txt').write_text(proc.stderr.read())
        # Reuse the reviewed UID1000 cleanup before sealing any partial raw files.
        seal_code = """import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,'/opt/study/modal')
from controller import quiesce_study_processes
cleanup=quiesce_study_processes()
print(json.dumps(cleanup),flush=True)
assert cleanup['quiescent'], 'Study UID1000 remained live'
root=Path('/work/calibration/result')
root.mkdir(exist_ok=True)
(root/'process-cleanup.json').write_text(json.dumps(cleanup,indent=2)+'\\n')
manifest={'schema':'classical.ecdlp.runtime-calibration-output-manifest/v1','study_uid1000_quiescent':True,
'files':[{'path':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
for p in sorted(root.iterdir()) if p.is_file() and p.name!='output-manifest.json']}
(root/'output-manifest.json').write_text(json.dumps(manifest,indent=2)+'\\n')
"""
        seal = sb.exec('python3', '-c', seal_code, timeout=50)
        record['seal_returncode'] = seal.wait()
        (args.out/'seal.stdout.txt').write_text(seal.stdout.read())
        (args.out/'seal.stderr.txt').write_text(seal.stderr.read())
        assert record['seal_returncode'] == 0
        data = regular_bytes(sb, '/work/calibration/result/output-manifest.json')
        manifest = json.loads(data)
        assert manifest['schema'] == 'classical.ecdlp.runtime-calibration-output-manifest/v1'
        assert manifest['study_uid1000_quiescent'] is True
        (args.out/'output-manifest.json').write_bytes(data)
        raw_out = args.out/'result'
        raw_out.mkdir()
        seen = set()
        for item in manifest['files']:
            name = item['path']
            if name in seen or PurePosixPath(name).name != name or name in ('','.', '..'):
                raise ValueError('Unsafe or duplicate result name')
            seen.add(name)
            remote = '/work/calibration/result/'+name
            info = sb.filesystem.stat(remote)
            assert getattr(info.type,'value',info.type) == 'file' and info.size == item['bytes']
            target = raw_out/name
            sb.filesystem.copy_to_local(remote, target)
            assert target.stat().st_size == item['bytes'] and sha(target.read_bytes()) == item['sha256']
            record['files_collected'].append({**item,'readback_verified':True})
        receipt_path = raw_out/'receipt.json'
        receipt = json.loads(receipt_path.read_text()) if receipt_path.exists() else {'completed':False,'worker_failed_before_receipt':True}
        record['completed'] = record['worker_returncode'] == 0 and receipt['completed']
        record['runtime_estimate'] = receipt.get('runtime_estimate')
    except Exception as error:
        record['error'] = {'type':type(error).__name__, 'message':str(error)}
        raise
    finally:
        if sb is not None:
            try:
                sb.terminate()
                record['termination_requested'] = True
            except Exception as error:
                record['termination_error'] = type(error).__name__
        record['finished_at'] = utc()
        write(args.out/'controller-receipt.json', record)
    print(json.dumps({'completed':record['completed'], 'sandbox_id':record.get('sandbox_id'),
                      'runtime_estimate':record.get('runtime_estimate')}), flush=True)
    return 0 if record['completed'] else 1

if __name__ == '__main__':
    sys.exit(main())
