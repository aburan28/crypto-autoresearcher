"""Public input construction only. Never imports or invokes relation collection."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SHARED = ROOT / 'research/prym_experiment_design_20261019/implementation'
sys.path.insert(0, str(SHARED))
from fixtures import describe, attach_ec1
from arithmetic import Field


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def build(config):
    old_config = json.loads((ROOT/config['historical_config_file']).read_text())
    old_panel = json.loads((ROOT/config['historical_fixture_file']).read_text())
    panel = []
    for selected in config['curves']:
        old = next(f for f in old_panel['fixtures'] if
                   (f['p'], f['a'], f['b'], f['r']) ==
                   (config['p'], config['a'], selected['b'], selected['r']))
        new, counts = describe(old['p'], old['a'], old['b'], config['factor_base_size'])
        if new is None:
            raise ValueError('unchanged public rule cannot extend base: '+repr(counts))
        attach_ec1(new)
        if (new['P'] != old['P'] or new['ec1'] != old['ec1'] or
                new['factor_base'][:8] != old['factor_base']):
            raise ValueError('inherited generator, EC1 or prefix mismatch')
        sources = list(range(1, 65))
        derivation = f"{old_config['domain']}|sources|{old['uid']}|0"
        random.Random(derivation).shuffle(sources)
        # Trace every inspected x, including rejected candidates. x=0 is retained
        # by the inherited rule; the unchanged constructor rejects those branches.
        trace, seen, accepted = [], set(), 0
        field = Field(old['p'])
        for x in range(new['construction_counts']['base_x_inspected']):
            u = x*x % old['p']
            y = field.sqrt((u**3+old['a']*u+old['b']) % old['p'])
            reason = ('not_rational' if y is None else
                      'norm_already_seen' if u in seen else 'append')
            record = dict(x=x, norm_x=u, canonical_y=y, reason=reason)
            if reason == 'append':
                record['atom_index'] = accepted
                seen.add(u)
                accepted += 1
            trace.append(record)
        new['width_binding'] = dict(
            old_fixture_uid=old['uid'], old_prefix_sha256=digest(old['factor_base']),
            new_base_sha256=digest(new['factor_base']),
            old_to_new_atoms=list(range(8)), source_order=sources,
            source_order_sha256=digest(sources), source_order_derivation=derivation,
            source_order_domain=old_config['domain'], source_order_seed=0,
            construction_trace=trace, construction_trace_sha256=digest(trace),
            inherited_x_zero_atom_preserved=True)
        panel.append(new)
    references = {}
    run = ROOT/config['historical_run']
    for name in ['verification.json', 'execution-receipt.json',
                 'raw-result.json.gz.blob.json', 'events.jsonl.gz.blob.json']:
        references[str((run/name).relative_to(ROOT))] = sha256((run/name).read_bytes()).hexdigest()
    custody = ROOT/config['historical_custody']
    for path in [custody, custody.parent/'.artifacts.json']:
        references[str(path.relative_to(ROOT))] = sha256(path.read_bytes()).hexdigest()
    return dict(schema='prym-factor-base-width-fixtures/v1', fixtures=panel,
                historical_reference_sha256=references,
                historical_reference_note='Local frozen metadata only; raw blobs not hydrated or independently remote-read here. Zero accepted old m8 rows makes empirical witness embedding vacuous.',
                secret_labels_present=False, relation_acceptance_observed=False,
                source_order_normalization='Materialized historical m8 UID/domain seed0 shuffle, reused independently of new fixture UID. No tuple sample or m8 replay is added.')


if __name__ == '__main__':
    result = build(json.loads((HERE/'config.json').read_text()))
    with (HERE/'fixtures.json').open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps(dict(fixtures=len(result['fixtures']), acceptance_observed=False)))
