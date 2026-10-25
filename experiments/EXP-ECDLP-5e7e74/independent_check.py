"""Independent S witness/model/census metric checks; no scientific launch."""
import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'research/prym_experiment_design_20261019/implementation'))
from census import Census
from independent import dense_rank,verify_fixture,verify_rank,verify_row


def selected(records,bucket,labels=None):
    seen=Counter(v[bucket] for v in records);hits=Counter()
    for j,v in enumerate(records):hits[v[bucket]]+=v['accepted'] if labels is None else labels[j]
    order=sorted(seen,key=lambda b:(-Fraction(hits[b]+1,seen[b]+2),b))
    return sorted(order[:(len(order)+3)//4])


def check(config,panel,result,event_path):
    fixtures={v['uid']:v for v in panel['fixtures']}
    for fixture in fixtures.values():verify_fixture(fixture)
    expected={(u,s) for u in fixtures for s in config['seeds']}
    cells={(v['curve_uid'],v['seed']):v for v in result['cells']}
    if set(cells)!=expected or len(cells)!=len(result['cells']):raise ValueError('fixed panel mismatch')
    # Events arrive in one cell at a time. Avoid storing all 24 fixed pools.
    active=None;training=[];truth={};predictions={};attempted={};checks=[]
    def finish(key):
        if key is None:return
        cell=cells[key];fixture=fixtures[key[0]]
        if cell.get('status')=='finite_support_exhausted':
            checks.append({'curve_uid':key[0],'seed':key[1],'status':'inconclusive_finite_support'});return
        if len(training)!=config['candidates_per_split']:raise ValueError('training quota mismatch')
        if len({v['candidate_id'] for v in training})!=len(training):raise ValueError('training aliases repeated')
        if len(truth)!=config['candidates_per_split']:raise ValueError('census quota mismatch')
        if {v['candidate_id'] for v in training}&set(truth):raise ValueError('train/holdout leakage')
        permutation=sorted(range(len(training)),key=lambda j:sha256(f'prym-S-null|{key[1]}|{training[j]["candidate_id"]}'.encode()).digest())
        if permutation!=cell['training']['null_permutation']:raise ValueError('null permutation changed')
        expected_models={'real':selected(training,'bucket'),
          'permuted':selected(training,'bucket',[training[j]['accepted'] for j in permutation]),
          'split_product':selected(training,'split_bucket')}
        for name,buckets in expected_models.items():
            if buckets!=cell['training']['models'][name]['retained_buckets']:raise ValueError('independent selector fit mismatch')
        arms=cell['arms']
        if not all(arms['identity'][k]==arms['identity_aa'][k] for k in ['rank','candidates','rows','operation_vector']):
            raise ValueError('identity A/A mismatch')
        if not all(arms['real'][k]==arms['coordinate'][k] for k in ['rank','candidates','rows']):
            raise ValueError('coordinate transport mismatch')
        census=Census(fixture)
        for item in attempted.get('census',[]):
            ident=item['candidate_id']
            if ident not in truth:continue
            row=census.accepted(item['scalar'],item['triple'],item['options'])
            if (row is not None)!=truth[ident]:raise ValueError('independent full-census disagreement')
        for arm,value in arms.items():
            for row in value['rows']:verify_row(fixture,row)
            ranks=value['rank'];U=value['U']
            if not 0<=ranks<=U:raise ValueError('invalid rank')
            if value['status']=='complete' and value['candidates']<config['candidates_per_split'] and ranks!=U:
                raise ValueError('premature rank stop')
        metrics={}
        for arm in ['real','permuted','split_product']:
            kept=[ident for ident,model in predictions.items() if model[arm]]
            true_positive=sum(truth[ident] for ident in kept);positive=sum(truth.values())
            metrics[arm]={'pool':len(truth),'kept':len(kept),'true_positives':true_positive,
                'false_negatives':positive-true_positive,
                'precision':None if not kept else true_positive/len(kept),
                'recall':None if not positive else true_positive/positive}
        checks.append({'curve_uid':key[0],'seed':key[1],'finite_pool_metrics':metrics,'scope':'Diagnostics only; no weighted S.'})
    with Path(event_path).open() as stream:
        for line in stream:
            item=json.loads(line);key=(item['curve_uid'],item['seed'])
            if key!=active:
                finish(active);active=key;training=[];truth={};predictions={};attempted={}
            if item['phase']=='training_label':
                if int(item['candidate_id'][-1],16)%2:raise ValueError('holdout ID in training')
                training.append(item)
            elif item['phase']=='census_label':
                ident=item['candidate_id']
                if not int(ident[-1],16)%2 or ident in truth:raise ValueError('repeated/training ID in census')
                truth[ident]=item['accepted'];predictions[ident]=item['frozen_predictions']
            elif item['phase']=='enumerate' and item['worker_mode']=='census' and item['status']=='eligible':
                attempted.setdefault('census',[]).append(item)
    finish(active)
    return checks


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--config',type=Path,required=True);parser.add_argument('--run-dir',type=Path,required=True);args=parser.parse_args()
    config=json.loads(args.config.read_text());root=Path(__file__).resolve().parents[2];panel=json.loads((root/config['fixture_file']).read_text())
    raw=args.run_dir/'raw-result.json';result=json.loads(raw.read_text());failed=[];checks=[]
    try:checks=check(config,panel,result,args.run_dir/'events.jsonl')
    except Exception as exc:failed.append(repr(exc))
    with (args.run_dir/'verification.json').open('x') as stream:json.dump({'schema':'prym-selector-check/v1','status':'failed' if failed else 'passed','failed_checks':failed,'cells':checks,'raw_result_sha256':sha256(raw.read_bytes()).hexdigest(),'limits':['Partial raw work vectors are not independently verified complete S.','Accepted witnesses/full-census labels checked independently; stream/geometric-orbit law still needs the separate prospective audit.']},stream,indent=2)
    return bool(failed)

if __name__=='__main__':raise SystemExit(main())
