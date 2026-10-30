"""Future native launch interface; exact existing native admission stays binding."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT/'research/prym_experiment_design_20261019/implementation'))
import native_runtime_v2 as native
from render_width import render

EXPERIMENT = 'EXP-ECDLP-a9b6a5'


def validate_protocol_binding(plan, protocol_path=None):
    from export_width import validate_protocol
    path = ROOT/f'experiments/{EXPERIMENT}/protocol.json' if protocol_path is None else protocol_path
    path = path.resolve()
    relative = str(path.relative_to(ROOT))
    file_sha256 = sha256(path.read_bytes()).hexdigest()
    if (plan.get('execution_plan', {}).get('protocol_hashes') != [dict(path=relative, sha256=file_sha256)] or
            plan['input_sha256'].get(relative) != file_sha256):
        raise ValueError('frozen protocol file binding missing or changed')
    if 'specification' in plan:
        import yaml
        specification = yaml.safe_load((ROOT/plan['specification']).read_text())['experiment']
        if specification.get('execution_plan', {}).get('protocol_hashes') != [dict(path=relative, sha256=file_sha256)]:
            raise ValueError('specification protocol file binding missing or changed')
    protocol = validate_protocol(path)
    return dict(path=relative, file_sha256=file_sha256,
                canonical_sha256=protocol['freeze']['protocol_sha256'])


def validate_config_binding(plan, config_path):
    canonical = HERE/'config.json'
    if config_path.resolve() != canonical.resolve():
        raise ValueError('only exact canonical width configuration is admissible')
    relative = str(canonical.relative_to(ROOT))
    if plan['input_sha256'].get(relative) != sha256(canonical.read_bytes()).hexdigest():
        raise ValueError('width configuration not frozen in native plan')
    binding_file = HERE/'source-bindings.json'
    if plan['input_sha256'].get(str(binding_file.relative_to(ROOT))) != sha256(binding_file.read_bytes()).hexdigest():
        raise ValueError('width source-binding manifest must itself be a frozen plan input')
    bindings = json.loads(binding_file.read_text())
    for kind, plan_key in [('source_sha256', 'source_sha256'), ('input_sha256', 'input_sha256')]:
        for path, expected in bindings[kind].items():
            if (sha256((ROOT/path).read_bytes()).hexdigest() != expected or
                    plan[plan_key].get(path) != expected):
                raise ValueError('missing/stale complete width binding: '+path)
    from check_inputs import validate
    config = json.loads(canonical.read_text())
    panel = json.loads((ROOT/config['fixture_file']).read_text())
    validate(config, panel)
    return validate_protocol_binding(plan)


def check_replay_admission(directory, config_path):
    # The independent checker never imports the producer, even for admission.
    plan, _ = native.binding(directory, EXPERIMENT)
    validate_config_binding(plan, config_path)
    if not (directory/'manifest.yaml').is_file() or not (directory/'raw-result.json').is_file():
        raise ValueError('target replay requires retained native producer outputs')


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--config', required=True, type=Path)
    parser.add_argument('--run-dir', required=True, type=Path)
    args, _ = parser.parse_known_args()
    original_binding = native.binding
    protocol_binding = {}

    def strict_binding(directory, experiment):
        plan, commit = original_binding(directory, experiment)
        protocol_binding.update(validate_config_binding(plan, args.config))
        return plan, commit

    native.binding = strict_binding
    native.render = render
    from collect_width import run, _NATIVE_CAPABILITY

    def admitted_runner(config, panel, event):
        result = run(config, panel, event, capability=_NATIVE_CAPABILITY)
        result['protocol_binding'] = dict(protocol_binding)
        return result

    return native.main(EXPERIMENT, admitted_runner)
