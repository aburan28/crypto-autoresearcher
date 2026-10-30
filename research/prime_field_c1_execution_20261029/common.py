"""Fixed administrative bindings; importing executes no mathematical panel."""
from hashlib import sha256
from pathlib import Path
import json
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
F1 = ROOT/'research/p256_factor_base_parallel_20261026/tracks/f1'
INPUTS = F1/'inputs.json'
PARAMETERS = {'max_dimension': 560, 'profile_stages': True}
SOURCES = [F1/(name+'.py') for name in ('driver', 'profiled', 'reference', 'core', 'exterior')]+[
    ROOT/'research/p256_factor_base_parallel_20261025/baseline/s4-symmetric.json',
    ROOT/'src/crypto_autoresearcher/index_calculus/curve.py',
    ROOT/'src/crypto_autoresearcher/index_calculus/execution_gate.py',
    ROOT/'research/p256_factor_base_parallel_20261026/runtime/checkpoint_gate.py',
    ROOT/'scripts/checkpoint.sh',
    ROOT/'tools/experiment_protocol.py', ROOT/'schemas/experiment-protocol.v1.json',
    ROOT/'schemas/experiment-export.v1.json',
    *[HERE/(name+'.py') for name in ('common', 'prepare', 'supervise', 'analyze')]]


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
