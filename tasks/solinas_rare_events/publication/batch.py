#!/usr/bin/env python3
"""Agent-free fixed independent-seed accumulation, with a prospective batch plan."""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from research import HERE,put_json,sha,source_files


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--root',type=Path,required=True)
    parser.add_argument('--seed-prefix',required=True);parser.add_argument('--batches',type=int,required=True);parser.add_argument('--workers',type=int,default=3)
    args=parser.parse_args()
    if args.batches<1 or args.workers<1:parser.error('batches and workers must be positive')
    root=args.root.resolve();root.mkdir(parents=True,exist_ok=True)
    plan={'schema':1,'seeds':[f'{args.seed_prefix}-{i:06d}' for i in range(args.batches)],
        'source_sha256':{p.name:sha(p) for p in source_files()},'wrapper_sha256':sha(__file__),
        'pooler_sha256':sha(Path(__file__).with_name('pool.py')),'workers':args.workers,
        'stopping':'All declared seeds; no outcome-dependent selection, enlargement or stopping.',
        'pooled_inference':'Nine exact paired tests, separate nine-rate and24-tail CP families, each alpha0.001. Per-seed analyses are diagnostics, not independent chances to select a discovery.'}
    plan_path=root/'batch-plan.json'
    if plan_path.exists():
        if json.loads(plan_path.read_text())!=plan:raise ValueError('Refuse changed batch plan; use a new root')
    else:put_json(plan_path,plan)
    env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1');runs=[]
    for i,seed in enumerate(plan['seeds']):
        run=root/f'run-{i:06d}';runs.append(run)
        if not (run/'completion.json').exists():
            subprocess.run([sys.executable,str(HERE/'research.py'),'--output',str(run),'--seed',seed,'--workers',str(args.workers)],env=env,check=True)
        if not (run/'verification.json').exists():subprocess.run([sys.executable,str(HERE/'verify.py'),str(run)],env=env,check=True)
        if not (run/'analysis.json').exists():subprocess.run([sys.executable,str(HERE/'analyze.py'),str(run)],env=env,check=True)
    output=root/'pooled-analysis.json'
    if not output.exists():subprocess.run([sys.executable,str(Path(__file__).with_name('pool.py')),'--output',str(output),*[str(r) for r in runs]],env=env,check=True)
    print(json.dumps({'fixed_batches_complete':len(runs),'pooled_analysis':str(output)}))


if __name__=='__main__':main()
