from pathlib import Path
import sys
import yaml

ROOT = Path('/Volumes/SSD990/crypto-autoresearcher/.tmp/first-fall-designs-20260905')
PAIRS = [
    ('IDEA-20260905-df55e9', 'H-PFDR-2139a5', 'EXP-PFDR-f32e6c'),
    ('IDEA-20260905-e6e2e5', 'H-PFDR-232b3a', 'EXP-PFDR-782085'),
    ('IDEA-20260905-850460', 'H-PFDR-d5f90f', 'EXP-PFDR-25057c'),
]

class UniqueLoader(yaml.SafeLoader):
    pass

def mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in result:
            raise ValueError(f'duplicate key {key!r} on line {key_node.start_mark.line + 1}')
        result[key] = loader.construct_object(value_node, deep=deep)
    return result

UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, mapping)

def read(relative, kind):
    doc = yaml.load((ROOT / relative).read_text(), Loader=UniqueLoader)
    assert set(doc) == {kind}, (relative, 'unexpected root')
    return doc[kind]

def filled(obj, keys, label):
    for key in keys:
        assert key in obj and obj[key] is not None and obj[key] != '', (label, key)

for idea_id, hypothesis_id, experiment_id in PAIRS:
    idea = read(f'ledger/proposals/{idea_id}.yaml', 'idea')
    assert idea['id'] == idea_id and idea['status'] == 'proposed'
    assert idea['novelty_status'] == 'unverified'
    hypothesis = read(f'ledger/hypotheses/{hypothesis_id}.yaml', 'hypothesis')
    assert hypothesis['id'] == hypothesis_id and hypothesis['status'] == 'specified'
    assert hypothesis['question_id'] == 'RQ-PFDR-ae2fba'
    assert idea_id in yaml.safe_dump(hypothesis), (hypothesis_id, 'missing idea binding')
    filled(hypothesis, ['statement', 'mechanism', 'assumptions', 'predictions',
                       'test_boundary', 'falsification_conditions',
                       'interpretation_limits', 'proof_search_map'], hypothesis_id)
    experiment = read(f'experiments/{experiment_id}/specification.yaml', 'experiment')
    assert experiment['id'] == experiment_id and experiment['hypothesis_id'] == hypothesis_id
    assert experiment['status'] == 'review_required' and experiment['approved_by'] is None
    filled(experiment, ['objective', 'inputs', 'controls', 'independent_variables',
                       'metrics', 'replication', 'budget', 'stopping_rules',
                       'invalidation_rules', 'success_criterion', 'falsification_criterion',
                       'required_artifacts', 'preregistered_prediction', 'scale_relevance'], experiment_id)
    budget = experiment['budget']
    assert budget['wall_clock_seconds_per_run'] >= 600
    assert budget['maximum_memory_gb'] >= 8
    assert budget['total_cpu_hours'] > 0 and budget['maximum_runs'] > 0
    assert budget.get('maximum_workers', 1) == 1
    assert experiment['assigned_to'] == 'executor'
    assert not list((ROOT / 'experiments' / experiment_id / 'runs').glob('**/*.*'))
    print(f'PASS {idea_id} -> {hypothesis_id} -> {experiment_id}')

decision = read('ledger/decisions/DEC-20260905-f53e68.yaml', 'coordinator_decision')
assert decision['decision'] == 'expand'
assert decision['decided_by'] == 'coordinator'
assert not decision['evidence_refs'] and not decision['knowledge_promotion']['promoted']
assert decision['knowledge_promotion']['not_warranted']
print('PASS design-only decision and zero run artifacts')
