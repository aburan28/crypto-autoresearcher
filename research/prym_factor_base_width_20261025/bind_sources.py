"""Bind local draft engineering bytes; grants no execution authority."""
import argparse
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def build():
    shared = ROOT/'research/prym_experiment_design_20261019/implementation'
    source = list(HERE.glob('*.py'))
    source += [shared/name for name in ['arithmetic.py', 'census.py', 'fixtures.py',
                                        'independent.py', 'native_runtime_v2.py', 'relations.py']]
    source += [ROOT/'research/prym_rank_census_20261025/check_census.py',
               ROOT/'src/crypto_autoresearcher/__init__.py', ROOT/'tools/curve_identity.py']
    source += [ROOT/'research/prym_rank_census_20261025/storage-delivery-20261025/execute_with_storage.py']
    source += [ROOT/'tools'/name for name in [
        'artifact_store.py', 'artifacts/artifacts.py', 'experiment_execution.py',
        'experiment_protocol.py',
        'research_dispatch.py', 'goal_lanes.py', 'sparse_checkout.py',
        'validate_ledger.py', 'validate_dispatch_reference.py', 'fast_yaml.py']]
    source += [ROOT/'orchestration'/name for name in [
        '__init__.py', 'research_budget.py', 'fast_yaml.py']]
    # fixtures imports the index_calculus package to reuse its prime predicate;
    # package initialization imports sibling modules even though no solver or
    # discrete-log routine is invoked by public input construction.
    source += list((ROOT/'src/crypto_autoresearcher/index_calculus').glob('*.py'))
    config = json.loads((HERE/'config.json').read_text())
    fixtures = json.loads((HERE/'fixtures.json').read_text())
    inputs = [HERE/name for name in ['config.json', 'fixtures.json', 'input-validation.json', 'contract.json']]
    inputs += [ROOT/'.artifacts/config.json']
    inputs += [ROOT/'schemas'/name for name in ['experiment-protocol.v1.json', 'experiment-export.v1.json']]
    inputs += [ROOT/config[k] for k in ['historical_config_file', 'historical_fixture_file']]
    inputs += [ROOT/path for path in fixtures['historical_reference_sha256']]

    def hashes(paths):
        return {str(path.relative_to(ROOT)): sha256(path.read_bytes()).hexdigest()
                for path in sorted(set(paths))}

    return dict(schema='prym-width-source-input-bindings/v1', execution_authorized=False,
                source_sha256=hashes(source), input_sha256=hashes(inputs),
                scope='Local public-input and planted-software implementation only; target stream unexecuted.',
                manifest_binding='The future native plan must additionally bind this manifest itself and frozen protocol.json as inputs, and declare the protocol full-file SHA in execution_plan.protocol_hashes. Both are excluded from this map to avoid recursive freeze bindings.',
                native_guard='Python capabilities prevent accidental API entry only; they are not a sandbox, security boundary or prescribed-execution proof.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    bindings = build()
    if args.check:
        if json.loads((HERE/'source-bindings.json').read_text()) != bindings:
            raise SystemExit('source/input bindings differ')
    else:
        with (HERE/'source-bindings.json').open('x') as stream:
            json.dump(bindings, stream, indent=2)
            stream.write('\n')
    print(json.dumps(dict(source_files=len(bindings['source_sha256']), input_files=len(bindings['input_sha256']),
                          checked=args.check, execution_authorized=False)))
