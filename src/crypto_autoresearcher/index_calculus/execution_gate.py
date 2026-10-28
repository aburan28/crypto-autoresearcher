"""Admission shared by the new research launchers; importing never executes."""
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import subprocess
import sys


def admit(repo, protocol_path, input_path, source_paths, parameters, release_path):
    """Bind committed source/input/parameters, then use the existing real gate.

    A release is a Coordinator artifact, not produced or approved by this helper.
    It must bind the full dependency closure in source_sha256/input_sha256.
    """
    repo = Path(repo).resolve()
    protocol = json.loads(Path(protocol_path).read_text())
    release_path = Path(release_path).resolve()
    release = json.loads(release_path.read_text())
    if release.get('parameters') != parameters:
        raise ValueError('release parameters differ from requested execution')
    if release.get('execution_authorized') is not True:
        raise ValueError('missing Coordinator execution release')
    if release.get('interpreter_sha256') != sha256(Path(sys.executable).resolve().read_bytes()).hexdigest():
        raise ValueError('release does not bind the current interpreter')
    commit = release.get('source_commit')
    if not commit:
        raise ValueError('release requires a pinned source commit')
    relative_release = str(release_path.relative_to(repo))
    committed_release = subprocess.check_output(['git', 'show', 'HEAD:'+relative_release], cwd=repo)
    if committed_release != release_path.read_bytes():
        raise ValueError('execution release must be committed unchanged')
    committed_protocol = subprocess.check_output(
        ['git', 'show', 'HEAD:'+str(Path(protocol_path).resolve().relative_to(repo))], cwd=repo)
    if committed_protocol != Path(protocol_path).read_bytes():
        raise ValueError('frozen protocol must be committed unchanged')
    locks = {**release.get('source_sha256', {}), **release.get('input_sha256', {})}
    helper = repo/'research/p256_factor_base_parallel_20261026/runtime/checkpoint_gate.py'
    required = [Path(input_path).resolve(), *(Path(p).resolve() for p in source_paths),
                Path(__file__).resolve(), helper, repo/'tools/experiment_protocol.py',
                repo/'schemas/experiment-protocol.v1.json']
    for path in required:
        if str(path.relative_to(repo)) not in locks:
            raise ValueError('release omits required input/source: '+str(path))
    for relative, expected in locks.items():
        path = (repo/relative).resolve()
        path.relative_to(repo)
        if sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError('source/input hash mismatch: '+relative)
        original = subprocess.check_output(['git', 'show', commit+':'+relative], cwd=repo)
        if sha256(original).hexdigest() != expected:
            raise ValueError('source commit mismatch: '+relative)
    subprocess.run([sys.executable, 'tools/experiment_protocol.py', 'validate', str(protocol_path)],
                   cwd=repo, check=True)
    spec = importlib.util.spec_from_file_location('_prime_field_checkpoint_gate', helper)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.require_gate(repo, release_path, protocol)
