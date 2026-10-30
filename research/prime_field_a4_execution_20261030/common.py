"""Fixed administrative bindings; importing executes no mathematical panel."""
from hashlib import sha256
from pathlib import Path
import json
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
NATIVE = HERE
INPUTS = HERE/'inputs.json'
PARAMETERS = {'prefixes':[0,16,64],'max_retained_rows':2048,'max_pair_entries':4096,'generation_after_admission':True}
ARMS = ['prefix0','prefix16','prefix64']
SOURCES = [HERE/(name+'.py') for name in ('core','check','driver')]+[
    *[ROOT/'research/prym_experiment_design_20261019/implementation'/(name+'.py') for name in ('arithmetic','independent','fixtures','relations')],
    ROOT/'research/prime_field_a3_execution_20261030/core.py',ROOT/'tools/curve_identity.py',
    ROOT/'research/prym_factor_base_width_20261025/check_inputs.py',
    *[ROOT/'src/crypto_autoresearcher/index_calculus'/(name+'.py') for name in ('curve','execution_gate')],
    ROOT/'research/p256_factor_base_parallel_20261026/runtime/checkpoint_gate.py',ROOT/'scripts/checkpoint.sh',
    ROOT/'tools/experiment_protocol.py',ROOT/'schemas/experiment-protocol.v1.json',ROOT/'schemas/experiment-export.v1.json',
    *[HERE/(name+'.py') for name in ('common','prepare','supervise','analyze')]]


def specifications(rules):
    return [dict(id='p'+str(f['p'])+'-i'+str(i),p=f['p'],base_size=f['base_size'],curve_index=i)
            for f in rules['fields'] for i in range(rules['curves_per_field'])]


def expected_work(spec,rules):
    from math import comb
    n=spec['base_size']
    return dict(source_queries=rules['sources']*n*2,target_queries=rules['targets']*n*2,
                pair_entries=comb(n,2)*4,oracle_signed_triples=comb(n,3)*8)


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def write_once(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()


def bindings(commit):
    """Require every exact source/input byte to exist at the stated commit."""
    maps = []
    for paths in (SOURCES, [INPUTS]):
        result = {}
        for path in paths:
            relative = str(path.relative_to(ROOT))
            expected = digest(path)
            original = subprocess.check_output(['git', 'show', commit+':'+relative], cwd=ROOT)
            if sha256(original).hexdigest() != expected:
                raise ValueError('source/input differs from pinned commit: '+relative)
            result[relative] = expected
        maps.append(result)
    return maps
