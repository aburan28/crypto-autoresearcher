"""Deterministically reformat already published development points; no entropy."""
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import subprocess

ROOT = Path('/workspace/classical-ecdlp-validation-ready')
HERE = Path(__file__).resolve().parent
B = 'f606a49ca777f44602303a57fc4519aca6a7c2e6'
PREFIX = 'harness/classical_ecdlp_solver_validation_v2/cohort/public/'

def blob(name):
    return subprocess.check_output(['git', 'show', B + ':' + PREFIX + name], cwd=ROOT)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def tsv(name, columns, rows):
    text = io.StringIO(newline='')
    writer = csv.DictWriter(text, fieldnames=columns, delimiter='\t', lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    data = text.getvalue().encode()
    with (HERE / name).open('xb') as stream:
        stream.write(data)
    return {'path': name, 'bytes': len(data), 'sha256': sha(data)}

fixtures, targets = blob('fixtures.tsv'), blob('public-targets.tsv')
source_fixtures = list(csv.DictReader(fixtures.decode().splitlines(), delimiter='\t'))
fixture = next(f for f in source_fixtures if f['id'] == 'sv-ordinary-r18-3')
source_targets = [t for t in csv.DictReader(targets.decode().splitlines(), delimiter='\t')
                  if t['fixture_id'] == fixture['id']]
assert len(source_targets) == 16
f = {'fixture_id': fixture['id'], 'stratum': fixture['stratum'],
     **{k: fixture[k] for k in ('p', 'a', 'b', 'r', 'N', 'seed')},
     'gx': fixture['Px'], 'gy': fixture['Py']}
panel = [{'fixture_id': f['fixture_id'], 'replicate': 0,
          'target_id': f'runtime-calibration-existing-Q-{i:02d}', 'target_ordinal': i,
          'qx': source_targets[i % 16]['Qx'], 'qy': source_targets[i % 16]['Qy'],
          'infinity': source_targets[i % 16]['Qinf']} for i in range(64)]
r = int(f['r'])
t = r.bit_length() // 3
c0 = (r + (1 << (2*t-1))) // (1 << (2*t))
cap = 4*c0
ceil_root = math.isqrt(r) + (math.isqrt(r)**2 != r)
setting = {'cell_id': 'runtime-calibration-existing-r18-rep0',
           'fixture_id': f['fixture_id'], 'replicate': 0, 'dp_bits': t,
           'initial_chains': c0, 'endpoint_cap': cap,
           'max_precomp_ops': 256*cap*(1 << t)+8192,
           'max_online_ops': 256*ceil_root+8192, 'seed': f['seed']}
files = [tsv('fixtures.tsv', ['fixture_id','stratum','p','a','b','gx','gy','r','N','seed'], [f]),
         tsv('targets.tsv', ['fixture_id','replicate','target_id','target_ordinal','qx','qy','infinity'], panel),
         tsv('settings.tsv', ['cell_id','fixture_id','replicate','dp_bits','initial_chains','endpoint_cap','max_precomp_ops','max_online_ops','seed'], [setting])]
plan = {'schema': 'classical.ecdlp.runtime-calibration-plan/v1',
        'purpose': 'Pre-freeze operational runtime estimate on reused public development points only; no registered confirmation observations.',
        'source_a_revision': 'fe01ccd832832488c58abeef17548b0a8db6035f',
        'source_b_revision': B,
        'image_id': 'im-Dsuo5jmqF3rOilhwkmGrzu', 'app_id': 'ap-EAHJ6SjvmeY99EQ2I47duh',
        'binary_sha256': '0eb981311b4dd0de7da9faf51178d1d97759d48a54e4c143f2f9d44ef31d8c48',
        'native_helper_sha256': 'e2f03b383fa9a21e984b8648e3700db7834954e26f3f30e86b7addf2f5b2f48d',
        'build_info_sha256': 'e1095196c90492476e7d8ef461b496d63954118e4875a19210e518840e1b1b3e',
        'source_inputs': [{'commit': B, 'path': PREFIX+'fixtures.tsv', 'sha256': sha(fixtures)},
                          {'commit': B, 'path': PREFIX+'public-targets.tsv', 'sha256': sha(targets)}],
        'source_target_ids': [t['target_id'] for t in source_targets],
        'unique_public_points': 16, 'targets_per_child': 64, 'repeat_rule': 'Existing16point order repeated four times, with unique development IDs and ordinals0..63.',
        'private_scalars_read_or_generated': False, 'fresh_random_targets_generated': False,
        'fixture_id': f['fixture_id'], 'setting': setting, 'inputs': files,
        'arms': ['static_small','static_full','static_filled','harvest','harvest_disabled','rho_reference'],
        'native_child_timeout_seconds': 3600, 'native_global_timeout_seconds': 3600,
        'preflight_sandbox_timeout_seconds': 600, 'preflight_command_timeout_seconds': 540,
        'runtime': 'vm', 'cpu': [2,2], 'memory_mib': [12288,12288], 'block_network': True,
        'wall_valid': False, 'l2_or_dedicated_physical_host_attested': False,
        'estimate_formula': '128 * sum(actual six child wall_seconds); fixed provider/startup/staging/collection overhead excluded, not an upper bound or a study comparison.',
        'limitations': 'One reused18-bit fixture with repeated public points is an operational proxy, not a runtime guarantee for64new curves or independent uniform targets. No algorithm performance claim.'}
with (HERE / 'plan.json').open('x') as stream:
    json.dump(plan, stream, indent=2, allow_nan=False)
    stream.write('\n')
print(json.dumps({'inputs': files, 'fixture_id': f['fixture_id'], 'setting': setting}, indent=2))
