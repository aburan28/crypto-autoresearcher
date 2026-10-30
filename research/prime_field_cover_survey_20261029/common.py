"""Fixed administrative bindings; importing executes no mathematical panel."""
from hashlib import sha256
from pathlib import Path
import json
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
NATIVE = HERE
INPUTS = ROOT/'research/prym_factor_base_width_20261025/fixtures.json'
PARAMETERS = {'shift_order':'all_field_elements_ascending','base_atoms':16,'source_count':64}
SOURCES = [HERE/'driver.py',
    ROOT/'src/crypto_autoresearcher/index_calculus/cover_frames.py',
    ROOT/'src/crypto_autoresearcher/index_calculus/curve.py',
    ROOT/'research/prym_experiment_design_20261019/implementation/independent.py',
    ROOT/'src/crypto_autoresearcher/index_calculus/execution_gate.py',
    ROOT/'research/p256_factor_base_parallel_20261026/runtime/checkpoint_gate.py',
    ROOT/'scripts/checkpoint.sh', ROOT/'tools/experiment_protocol.py',
    ROOT/'schemas/experiment-protocol.v1.json', ROOT/'schemas/experiment-export.v1.json',
    *[HERE/(name+'.py') for name in ('common','prepare','supervise','analyze')]]


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
