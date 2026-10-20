"""Synthetic CI fixture builder; never executes a protocol binary."""
from pathlib import Path
import importlib.util
import hashlib
import json
import shutil
import subprocess
import yaml
ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "experiments/EXP-SCURVE-1a8daf/runs/RUN-SCURVE-561a96"


def load_checker(relative, name):
    path = ROOT / relative
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ROLE1 = load_checker("research/p192-weighted-cm-20261007-v2-role1-interface/check_role1_interface.py", "retained_role1_checker")
ROLE2 = load_checker("research/p192-weighted-cm-20261007-v2-role2-box0-interface/check_role2_box0_interface.py", "retained_role2_checker")


def git(root, *args):
    return subprocess.check_output([
        'git', '-c', 'core.hooksPath=/dev/null', '-c', 'user.name=Unit fixture',
        '-c', 'user.email=fixture@example.invalid', '-C', str(root), *args,
    ], text=True).strip()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def replace(value, mapping):
    if isinstance(value, str):
        for old, new in sorted(mapping.items(), key=lambda item: -len(item[0])):
            value = value.replace(old, new)
        return value
    if isinstance(value, list):
        return [replace(x, mapping) for x in value]
    if isinstance(value, dict):
        return {k: replace(v, mapping) for k, v in value.items()}
    return value


def build(root):
    """Build fabricated unit-test metadata in a disposable root, not research evidence."""
    root = root.resolve()
    spec = importlib.util.spec_from_file_location('original_role1_fixture', ROOT / 'tests/test_p192_wcm_role1_interface.py')
    fixture = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fixture)
    doc, decision_path, run, _ = fixture.make_decision_fixture(root)
    a = doc['coordinator_decision']['authorization']
    for role, content in [('producer', 'pub fn producer_fixture(x:u32)->u32{x+1}\n'), ('verifier', 'pub fn verifier_fixture(y:u64)->u64{y*3}\n')]:
        package = Path(a['executables'][role]['package_path'])
        (package / 'src/lib.rs').write_text(content)
        (package / 'Cargo.lock').write_text('version = 3\n')
    # Commit the exact protected checker/schema bytes before the synthetic decision.
    role1_rel = 'research/p192-weighted-cm-20261007-v2-role1-interface/'
    for rel in ['check_role1_interface.py', 'schemas/role1-artifacts.schema.json', 'schemas/role1-dispatch-decision.schema.json']:
        dest = root / role1_rel / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / role1_rel / rel, dest)
    decision_path.unlink()
    git(root, 'init', '-q')
    git(root, 'add', '.')
    git(root, 'commit', '-qm', 'Synthetic protected protocol fixture')
    protocol = git(root, 'rev-parse', 'HEAD')
    a['protocol']['commit'] = protocol
    # The retained producer/verifier implementations share a source revision;
    # keep that relation in this synthetic metadata while retaining distinct
    # packages and distinct binary contents.
    original_receipt = json.loads((RUN / 'independent-verifier-receipt.json').read_bytes())
    assert original_receipt['source_commit'] == original_receipt['verifier_commit']
    a['executables']['verifier']['verifier_commit'] = a['executables']['producer']['source_commit']
    a['executables']['verifier']['embedded_verifier_commit'] = a['executables']['producer']['source_commit']
    a['executables']['supervisor']['embedded_verifier_commit'] = a['executables']['producer']['source_commit']
    a['executables']['supervisor']['embedded_protocol_commit'] = protocol
    a['executables']['producer']['embedded_protocol_commit'] = protocol
    a['supervisor_argv'] = ROLE1._resolved_supervisor_argv(a)
    decision_path.write_text(yaml.safe_dump(doc, sort_keys=False))
    git(root, 'add', str(decision_path.relative_to(root)))
    git(root, 'commit', '-qm', 'Synthetic decision fixture; no execution')
    decision = git(root, 'rev-parse', 'HEAD')
    shutil.copytree(RUN, run)
    old_receipt = json.loads((RUN / 'independent-verifier-receipt.json').read_bytes())
    old_command = json.loads((RUN / 'command.txt').read_bytes())
    old_environment = json.loads((RUN / 'environment.json').read_bytes())
    mapping = {
        old_receipt['protocol_commit']: protocol,
        old_receipt['source_commit']: a['executables']['producer']['source_commit'],
        old_receipt['verifier_commit']: a['executables']['verifier']['verifier_commit'],
        old_receipt['decision_binding']['decision_commit']: decision,
        old_receipt['decision_binding']['decision_sha256']: digest(decision_path.read_bytes()),
        old_receipt['decision_binding']['decision_id']: doc['coordinator_decision']['id'],
        RUN.name: run.name,
    }
    for index in [0, 2, 4, 6, 8, 10, 12, 14, 22]:
        mapping[old_command[index]] = a['supervisor_argv'][index]
    for role in ['supervisor', 'producer', 'verifier']:
        mapping[old_environment[role + '_binary_sha256']] = a['executables'][role]['binary_sha256']
    documents = {}
    for path in run.iterdir():
        if path.suffix in ['.json', '.yaml'] or path.name == 'command.txt':
            documents[path.name] = replace(json.loads(path.read_bytes()), mapping)
    documents['command.txt'] = a['supervisor_argv']
    audit = documents['dependency-audit.json']
    for role in ['producer', 'verifier']:
        record = a['executables'][role]
        package = Path(record['package_path'])
        audit[role + '_git']['git_top_level'] = record['repository_path']
        audit[role + '_git']['package_root'] = record['package_path']
        audit[role + '_rust_sources'] = ROLE1._collect_rust_hash_rows(package)
        audit[role + '_cargo_toml_sha256'] = digest((package / 'Cargo.toml').read_bytes())
    audit['verifier_cargo_lock_sha256'] = digest((Path(a['executables']['verifier']['package_path']) / 'Cargo.lock').read_bytes())
    audit['identical_source_hashes'] = []
    audit['source_clone_screen'] = ROLE1.compute_source_clone_screen(
        Path(a['executables']['producer']['package_path']) / 'src',
        Path(a['executables']['verifier']['package_path']) / 'src')
    old_hashes = {p.relative_to(run).as_posix(): digest(p.read_bytes()) for p in run.rglob('*') if p.is_file()}
    hash_map = {}
    def update_inventory(value):
        if isinstance(value, dict):
            relative = value.get('path')
            if relative in old_hashes and 'sha256' in value and 'byte_length' in value:
                data = (run / relative).read_bytes()
                value['sha256'] = digest(data)
                value['byte_length'] = len(data)
            for item in value.values():
                update_inventory(item)
        elif isinstance(value, list):
            for item in value:
                update_inventory(item)
    # Every digest edge is checked again by the unchanged native validator.
    previous = None
    for _ in range(30):
        for name, body in documents.items():
            documents[name] = replace(body, hash_map)
            update_inventory(documents[name])
            (run / name).write_bytes(ROLE1._canonical_json_bytes(documents[name]))
        factor_sha = digest((run / 'factor-base.json').read_bytes())
        (run / 'factor-base.sha256').write_text(f'{factor_sha}  factor-base.json\n')
        current = {p.relative_to(run).as_posix(): digest(p.read_bytes()) for p in run.rglob('*') if p.is_file()}
        if current == previous:
            break
        for name, sha in current.items():
            hash_map[old_hashes[name]] = sha
            if previous and previous[name] != sha:
                hash_map[previous[name]] = sha
        previous = current
    else:
        raise AssertionError('fixture digest graph did not stabilize')
    git(root, 'add', '.')
    git(root, 'commit', '-qm', 'Synthetic retained output fixture; no binary executed')
    return run, decision_path, protocol, decision
