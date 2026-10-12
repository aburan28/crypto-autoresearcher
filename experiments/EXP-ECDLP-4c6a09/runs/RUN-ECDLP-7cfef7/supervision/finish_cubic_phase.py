"""Preserve cubic descents; higher degrees are handled by the separate bound run."""
import importlib.util
import json
import os
import signal
import time
from datetime import datetime, timezone
from pathlib import Path

run = Path('/workspace/solinas-run/experiments/EXP-ECDLP-4c6a09/runs/RUN-ECDLP-7cfef7')
plan = json.loads((run / 'plan.json').read_text())
cubic_ids = {j['id'] for j in plan['jobs_to_execute'] if j['degree'] == 3}
while not (run / 'raw-result.json').exists():
    done = {p.parent.name for p in (run / 'instances').glob('*/result.json')}
    if cubic_ids <= done:
        processes = []
        for p in Path('/proc').iterdir():
            if not p.name.isdigit():
                continue
            try:
                args = (p / 'cmdline').read_bytes().split(b'\0')
            except (FileNotFoundError, PermissionError):
                continue
            if any(b'RUN-ECDLP-7cfef7/source/run_rank.py' in x for x in args) and b'campaign' in args:
                processes.append(int(p.name))
            if any(b'RUN-ECDLP-7cfef7/instances/' in x for x in args):
                processes.append(int(p.name))
        for pid in processes:
            try:
                os.kill(pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
        time.sleep(.5)
        spec = importlib.util.spec_from_file_location('rank_runner', run / 'source/run_rank.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for d in (run / 'instances').iterdir():
            if (d / 'result.json').exists():
                continue
            launch = json.loads((d / 'launch.json').read_text())
            r = module.parse((d / 'stdout.log').read_text(), (d / 'stderr.log').read_text(), False)
            r.update({'job': launch['job'], 'exit_code': -15, 'timed_out': False,
                      'finished_at_utc': datetime.now(timezone.utc).isoformat(),
                      'elapsed_seconds': (datetime.now(timezone.utc) - datetime.fromisoformat(launch['started_at_utc'])).total_seconds(),
                      'stopped_for_method_switch': True, 'conditional_on_grh': bool(r['uncertified_class_unit_data'] and r['nf_bounds']),
                      'status': 'bounds' if r['nf_bounds'] else 'unfinished'})
            r['bounds_coincide'] = r['exact']
            if r['conditional_on_grh']:
                r['status'] = 'conditional_exact' if r['exact'] else 'conditional_bounds'
                r['exact'] = False
            with (d / 'result.json').open('x') as f:
                json.dump(r, f, indent=2)
                f.write('\n')
        reused = json.loads((run / 'reused-results.json').read_text())
        nf = reused['nf'] + [json.loads(p.read_text()) for p in (run / 'instances').glob('*/result.json')]
        output = {'q': reused['q'], 'nf': nf, 'reused_from_run': reused['source_run'],
                  'process': {'complete': False, 'cubic_phase_complete': True,
                              'finished_at_utc': datetime.now(timezone.utc).isoformat(),
                              'stop_action': 'SIGTERM to this campaign supervisor and its remaining GP jobs after all cubic jobs completed.',
                              'reason': 'The separate RUN-ECDLP-280de8 computes higher-degree candidate-group bounds, avoiding quartic enumeration. Preserve actual full descents and use the separate record for the remaining higher-degree scope.',
                              'terminated_pids': processes,
                              'unattempted_job_ids': [j['id'] for j in plan['jobs_to_execute'] if not (run / 'instances' / j['id']).exists()]}}
        with (run / 'raw-result.json').open('x') as f:
            json.dump(output, f, indent=2)
            f.write('\n')
        print('CUBIC_PHASE_COMPLETE', len(nf), 'actual NF result records', flush=True)
        break
    time.sleep(2)
